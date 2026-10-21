#!/usr/bin/env python3
"""Check kama live receipts against the per-slot context rule in llama.cpp 704366d76.

Source lines (raw sha256 values are in pins.txt next to this file):
  tools/server/server-context.cpp 4654-4663  n_ctx_slot() = min(llama_n_ctx_seq, --kv-unified-per-slot if > 0, n_ctx_train)
  tools/server/server-context.cpp 4829, 5236 /props default_generation_settings.n_ctx = meta.slot_n_ctx = n_ctx_slot()
  tools/server/server-context.cpp 5186-5187  /v1/models data[0].meta.n_ctx = slot_n_ctx; meta.n_ctx_train (4848)
  tools/server/server-context.cpp 5244       /props total_slots = params.n_parallel
  tools/server/server-context.cpp 736-741    JSON of an idle slot with no previous task: id, n_ctx, speculative, is_processing
  src/llama-context.cpp 219, 377-393         n_ctx (0 means n_ctx_train) is padded up to a multiple of 256; with a unified KV
                                             cache n_ctx_seq = n_ctx; otherwise GGML_PAD(n_ctx / n_seq_max, 256)
  tools/server/server.cpp 169-174            -np unset (auto, common/arg.cpp 1406) -> n_parallel = 4, kv_unified = true
The model assumes that no --fit run lowered n_ctx, no YaRN rescale was applied and no --override-kv was given. A receipt whose
argv or environment can change those inputs is reported as could-not-evaluate.

Exit 0: every receipt is consistent. Exit 1: at least one receipt contradicts a source-predicted equality.
Exit 2: no contradiction was observed, but at least one receipt could not be evaluated.
Use --table to print the formula for example launch settings. These values are computed, not served.
"""
import hashlib
import json
import sys

VALUE_FLAGS = {"-c": "ctx", "--ctx-size": "ctx", "-np": "np", "--parallel": "np", "--kv-unified-per-slot": "per_slot"}
BOOL_FLAGS = {"-kvu": True, "--kv-unified": True, "-no-kvu": False, "--no-kv-unified": False}
NEUTRAL_VALUE_FLAGS = {"-m", "--model", "--alias", "-a", "--host", "--port", "-t", "--threads"}
NEUTRAL_FLAGS = {"--no-webui", "--offline"}


class Unusable(Exception):
    pass


def pad256(x):
    return (x + 255) & ~255


def predict(ctx, n_ctx_train, n_parallel, kv_unified, per_slot):
    if n_parallel < 0:
        n_parallel, kv_unified = 4, True
    n_ctx = pad256(ctx if ctx else n_ctx_train)
    n_ctx_seq = n_ctx if kv_unified else pad256(n_ctx // n_parallel)
    res = min(n_ctx_seq, per_slot) if per_slot > 0 else n_ctx_seq
    return min(res, n_ctx_train), n_parallel, kv_unified


def launch_settings(argv, env_keys):
    llama_env = sorted(k for k in env_keys if k.startswith("LLAMA_ARG_"))
    if llama_env:
        raise Unusable("LLAMA_ARG_ environment not modelled: " + ",".join(llama_env))
    got = {"ctx": 0, "np": -1, "per_slot": 0, "kvu": False}
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in VALUE_FLAGS or arg in NEUTRAL_VALUE_FLAGS:
            if i + 1 >= len(argv):
                raise Unusable(f"flag {arg} has no value")
            if arg in VALUE_FLAGS:
                try:
                    got[VALUE_FLAGS[arg]] = int(argv[i + 1])
                except ValueError:
                    raise Unusable(f"flag {arg} has a non-integer value") from None
            i += 2
        elif arg in BOOL_FLAGS:
            got["kvu"] = BOOL_FLAGS[arg]
            i += 1
        elif arg in NEUTRAL_FLAGS:
            i += 1
        else:
            raise Unusable(f"argv element {arg!r} is not modelled")
    return got


def check(path):
    try:
        with open(path, encoding="utf-8") as fh:
            receipt = json.load(fh)
        caps = receipt["captures"]
        fields = caps["props"]["fields"]
        models = caps["models"]
        if models.get("body_read_truncated") is not False or not isinstance(models.get("body"), str):
            raise Unusable("/v1/models body absent or truncated")
        body = models["body"].encode("utf-8")
        if hashlib.sha256(body).hexdigest() != models.get("body_sha256"):
            raise Unusable("/v1/models body does not match its recorded sha256")
        meta = json.loads(body)["data"][0]["meta"]
        n_ctx_train, meta_n_ctx = int(meta["n_ctx_train"]), int(meta["n_ctx"])
        props_n_ctx, total_slots = int(fields["default_generation_settings.n_ctx"]), int(fields["total_slots"])
        got = launch_settings(receipt["argv"], receipt.get("child_env_keys", []))
    except Unusable as exc:
        return 2, f"{path}\tCOULD-NOT-EVALUATE\t{exc}"
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        return 2, f"{path}\tCOULD-NOT-EVALUATE\t{type(exc).__name__}: {exc}"
    want, n_parallel, kv_unified = predict(got["ctx"], n_ctx_train, got["np"], got["kvu"], got["per_slot"])
    failed = [name for name, ok in (
        ("props==models.meta.n_ctx", props_n_ctx == meta_n_ctx),
        ("props==predicted", props_n_ctx == want),
        ("total_slots==n_parallel", total_slots == n_parallel),
    ) if not ok]
    slots = caps.get("slots") or {}
    def slots_match(n_ctx):
        body = json.dumps([{"id": i, "n_ctx": n_ctx, "speculative": False, "is_processing": False}
                           for i in range(total_slots)], separators=(",", ":")).encode()
        return hashlib.sha256(body).hexdigest() == slots.get("body_sha256")
    if not slots.get("body_sha256"):
        slot_note = "slots=absent"
    else:
        naive = got["ctx"] // total_slots if got["ctx"] and total_slots else 0
        slot_note = (f"slots(n_ctx={want})={'match' if slots_match(want) else 'no-match'}"
                     f" slots(naive ctx/slots={naive})={'match' if naive and slots_match(naive) else 'no-match'}")
    verdict = "INCONSISTENT " + ",".join(failed) if failed else "CONSISTENT"
    line = (f"{path}\t{verdict}\tctx={got['ctx']} np={'auto' if got['np'] < 0 else got['np']}->{n_parallel}"
            f" kv_unified={str(kv_unified).lower()} n_ctx_train={n_ctx_train} predicted={want}"
            f" props.n_ctx={props_n_ctx} models.meta.n_ctx={meta_n_ctx} total_slots={total_slots} {slot_note}")
    return (1 if failed else 0), line


def table():
    print("ctx\tnp\tkvu\tn_ctx_train\tper_slot_n_ctx (source formula, not served)")
    for ctx, n_ctx_train, n_parallel, kvu in ((256, 2048, -1, False), (256, 2048, 4, False), (1024, 2048, -1, False),
                                              (1024, 2048, 4, False), (4096, 2048, -1, False), (0, 2048, -1, False),
                                              (0, 2048, 4, False)):
        want, n_par, uni = predict(ctx, n_ctx_train, n_parallel, kvu, 0)
        np_text = "auto->4" if n_parallel < 0 else str(n_parallel)
        print(f"{ctx}\t{np_text}\t{str(uni).lower()}\t{n_ctx_train}\t{want}")


def main(argv):
    if argv[1:] == ["--table"]:
        table()
        return 0
    if len(argv) < 2:
        print("usage: nctx-crosscheck.py RECEIPT.json... | --table", file=sys.stderr)
        return 2
    codes = []
    for path in argv[1:]:
        code, line = check(path)
        codes.append(code)
        print(line)
    return 1 if 1 in codes else (2 if 2 in codes else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
