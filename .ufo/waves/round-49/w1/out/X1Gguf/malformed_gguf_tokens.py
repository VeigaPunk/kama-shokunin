#!/usr/bin/env python3
"""Seat X1Gguf: adversarial inputs to gguf_tokens() of
tools/round49-replay-witness-audit.py (C1 counter).

Each case is built in a temp dir and the decoder runs in a subprocess with a
wall-clock cap, so a hang is recorded as such instead of stalling the seat.

  python3 malformed_gguf_tokens.py <counter.py> <scratch-dir> <real-model.gguf>

Output: one JSON object per line (also written next to this script when --out).
"""
import json
import os
import struct
import subprocess
import sys
import textwrap

COUNTER = sys.argv[1]
TRUE_LAST = None   # decoded last token of the intact file, set in main()
SCRATCH = sys.argv[2]
REAL = sys.argv[3]
OUT = sys.argv[4] if len(sys.argv) > 4 else None
CAP = 60  # seconds per case

CHILD = textwrap.dedent("""
import importlib.util, json, sys, time
spec = importlib.util.spec_from_file_location("c1counter", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
t0 = time.monotonic()
try:
    v = mod.gguf_tokens(sys.argv[2])
    out = {"outcome": "returned", "type": "list", "length": len(v),
           "first": v[0] if v else None, "last": v[-1] if v else None,
           "last_repr": repr(v[-1]) if v else None}
except BaseException as exc:
    out = {"outcome": "raised", "type": type(exc).__name__, "message": str(exc)[:200]}
out["seconds"] = round(time.monotonic() - t0, 3)
print(json.dumps(out))
""")


def kv_str(key, value):
    k = key.encode()
    v = value.encode()
    return struct.pack("<Q", len(k)) + k + struct.pack("<I", 8) + struct.pack("<Q", len(v)) + v


def kv_u32(key, value):
    k = key.encode()
    return struct.pack("<Q", len(k)) + k + struct.pack("<I", 4) + struct.pack("<I", value)


def kv_array_u32(key, values):
    k = key.encode()
    return (struct.pack("<Q", len(k)) + k + struct.pack("<I", 9)
            + struct.pack("<I", 4) + struct.pack("<Q", len(values))
            + b"".join(struct.pack("<I", v) for v in values))


def kv_array_strings(key, strings):
    k = key.encode()
    body = b"".join(struct.pack("<Q", len(s.encode())) + s.encode() for s in strings)
    return (struct.pack("<Q", len(k)) + k + struct.pack("<I", 9)
            + struct.pack("<I", 8) + struct.pack("<Q", len(strings)) + body)


def gguf(version, kvs, tensor_count=0):
    return b"GGUF" + struct.pack("<I", version) + struct.pack("<QQ", tensor_count, len(kvs)) + b"".join(kvs)


def build_plain(path, version=3, strings=("a", "b", "c")):
    with open(path, "wb") as fh:
        fh.write(gguf(version, [kv_str("general.architecture", "llama"),
                                kv_array_strings("tokenizer.ggml.tokens", strings)]))


def nested(path, depth):
    # one KV whose value is an array nested `depth` times; deepest is a UINT8 array
    body = struct.pack("<I", 0) + struct.pack("<Q", 1) + b"\x00"   # et=uint8, n=1, value
    for _ in range(depth):
        body = struct.pack("<I", 9) + struct.pack("<Q", 1) + body  # array of 1 nested array
    key = b"general.name"
    with open(path, "wb") as fh:
        fh.write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 1)
                 + struct.pack("<Q", len(key)) + key + struct.pack("<I", 9) + body)


def many_empty_strings(path, n):
    key = b"tokenizer.ggml.tokens"
    with open(path, "wb") as fh:
        fh.write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 1)
                 + struct.pack("<Q", len(key)) + key + struct.pack("<I", 9)
                 + struct.pack("<I", 8) + struct.pack("<Q", n))
        fh.write(b"\x00" * 8 * n)   # every token is the empty string


def trunc(src, dst, cut_from_end=0, keep=0):
    data = open(src, "rb").read()
    end = len(data) - cut_from_end if cut_from_end else keep
    with open(dst, "wb") as fh:
        fh.write(data[:end])
    return end


def run(name, path, note, expect=None):
    p = subprocess.run([sys.executable, "-c", CHILD, COUNTER, path],
                       capture_output=True, text=True, timeout=CAP, cwd=SCRATCH)
    rec = {"case": name, "bytes": os.path.getsize(path), "note": note}
    try:
        rec.update(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception:
        rec.update({"outcome": "harness-error", "stdout": p.stdout[-400:], "stderr": p.stderr[-800:]})
    rec["rc"] = p.returncode
    if (TRUE_LAST is not None and rec.get("outcome") == "returned"
            and rec.get("length") == 512):
        got = json.loads(p.stdout.strip().splitlines()[-1]).get("last")
        rec["silently_differs_from_true_vocab"] = got != TRUE_LAST
    rec["expect"] = expect
    if p.returncode not in (0, 1):
        rec["stderr"] = p.stderr.strip().splitlines()[-1][:300] if p.stderr.strip() else ""
    return rec


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    d = SCRATCH
    rows = []
    empty = os.path.join(d, "empty.gguf"); open(empty, "wb").close()
    rows.append(run("empty-file", empty, "0 bytes", expect="EvalError model is not GGUF"))

    two = os.path.join(d, "two.gguf"); open(two, "wb").write(b"GG")
    rows.append(run("two-bytes", two, "b'GG'", expect="EvalError model is not GGUF"))

    h8 = os.path.join(d, "h8.gguf"); open(h8, "wb").write(b"GGUF" + struct.pack("<I", 3))
    rows.append(run("header-only-8B", h8, "magic+version, counts missing", expect="struct.error (uncaught by counter's (OSError, EvalError, struct.error)? No: struct.error is caught)"))

    h24 = os.path.join(d, "h24.gguf")
    open(h24, "wb").write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 1))
    rows.append(run("header-24B-kvcount-1", h24, "declares 1 KV, no KV bytes", expect="struct.error"))

    for ver in (0, 1):
        p = os.path.join(d, f"v{ver}.gguf")
        open(p, "wb").write(gguf(ver, [kv_str("general.architecture", "llama")]))
        rows.append(run(f"gguf-v{ver}", p, f"version field = {ver}", expect="EvalError GGUF vN unsupported"))

    ok3 = os.path.join(d, "v3ok.gguf"); build_plain(ok3, 3)
    rows.append(run("gguf-v3-minimal-ok", ok3, "3 string tokens, sanity", expect="returns ['a','b','c']"))
    ok2 = os.path.join(d, "v2ok.gguf"); build_plain(ok2, 2)
    rows.append(run("gguf-v2-minimal-ok", ok2, "same payload, version=2", expect="returns ['a','b','c']"))

    u32 = os.path.join(d, "tokens-u32.gguf")
    open(u32, "wb").write(gguf(3, [kv_array_u32("tokenizer.ggml.tokens", [1, 2, 3])]))
    rows.append(run("tokens-array-uint32", u32, "tokens is ARRAY<UINT32>", expect="EvalError tokens array is not strings"))

    sc = os.path.join(d, "tokens-scalar.gguf")
    open(sc, "wb").write(gguf(3, [kv_str("tokenizer.ggml.tokens", "abc")]))
    rows.append(run("tokens-scalar-string", sc, "tokens is a scalar STRING, not ARRAY", expect="EvalError tokenizer.ggml.tokens absent"))

    rand = os.path.join(d, "random1mb.gguf")
    open(rand, "wb").write(os.urandom(1 << 20))
    rows.append(run("random-1MiB", rand, "os.urandom(1<<20)", expect="EvalError model is not GGUF"))

    # real-file prefix truncations.  In stories260K the tokens array spans
    # bytes 69..6470; token 511 ('<U+200A>', e2 80 8a) starts at 6459.
    # keep=6470 is a complete array, 6469..6467 cut the last token body,
    # 6466..6459 cut its 8-byte length prefix, lower keep cuts earlier tokens.
    global TRUE_LAST
    TRUE_LAST = json.loads(subprocess.run(
        [sys.executable, "-c", CHILD, COUNTER, REAL], capture_output=True, text=True,
        cwd=SCRATCH).stdout.strip().splitlines()[-1])["last"]
    for keep, note in ((6470, "complete array (control)"),
                       (6469, "last token body e2 80 only (1 of 3 bytes)"),
                       (6468, "last token body e2 only"),
                       (6467, "last token body entirely gone, prefix intact"),
                       (6466, "inside last token's 8-byte length prefix"),
                       (6459, "at the start of last token's length prefix"),
                       (6450, "at the start of token 510's length prefix"),
                       (4000, "mid-array, inside some token body"),
                       (100, "inside token 2/3"),
                       (69, "at array payload start, zero token bytes")):
        p = os.path.join(d, f"real-keep-{keep}.gguf")
        trunc(REAL, p, keep=keep)
        rec = run(f"real-prefix-{keep}B", p, note,
                  expect="silent short/patched vocabulary at the tail, else struct.error")
        rec["note"] += "; silent corruption if returned vocab != true vocab"
        rows.append(rec)

    # every scalar KV type 0..12 plus a nested array *before* the tokens key:
    # exercises skip()'s fixed-width table, the only place a silent offset drift
    # could hide (a wrong width would make the tokens lookup land on garbage).
    alltypes = []
    widths = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "B",
              10: "Q", 11: "q", 12: "d"}
    for t, fmt in widths.items():
        key = f"general.skip{t}".encode()
        raw = struct.pack("<" + fmt, 1 if t != 6 else 1.5)
        alltypes.append(struct.pack("<Q", len(key)) + key + struct.pack("<I", t) + raw)
    alltypes.append(struct.pack("<Q", len(b"general.skipstr")) + b"general.skipstr"
                    + struct.pack("<I", 8) + struct.pack("<Q", 4) + b"abcd")
    inner = struct.pack("<I", 0) + struct.pack("<Q", 2) + b"\x01\x00"
    nest = struct.pack("<I", 9) + struct.pack("<Q", 2) + inner + inner
    alltypes.append(struct.pack("<Q", len(b"general.skipnest")) + b"general.skipnest"
                    + struct.pack("<I", 9) + nest)
    alltypes.append(kv_array_u32("general.skiparr", [7, 8, 9]))
    alltypes.append(kv_array_strings("tokenizer.ggml.tokens", ["x", "yy", "zzz", "\u200a", "\u00e9"]))
    sk = os.path.join(d, "skip-coverage.gguf")
    open(sk, "wb").write(gguf(3, alltypes))
    rows.append(run("skip-coverage-types-0-12", sk, "one KV of each scalar type + nested array + uint32 array before tokens",
                    expect="returns ['x','yy','zzz','U+200A','e-acute'] -- offset table correct"))

    # random bytes but with the magic forced, i.e. the checks after the first one
    rnd = bytearray(os.urandom(1 << 20)); rnd[0:4] = b"GGUF"
    rp = os.path.join(d, "random-magic.gguf"); open(rp, "wb").write(bytes(rnd))
    rows.append(run("random-1MiB-magic-forced", rp, "os.urandom(1<<20) with b'GGUF' patched in",
                    expect="EvalError GGUF vN unsupported or struct.error; must not hang"))

    # nkv declares 2**62 KVs in a 1 MB file: loop must stop at EOF, not run 2**62 times
    hn = os.path.join(d, "nkv-huge.gguf")
    open(hn, "wb").write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 1 << 62)
                         + os.urandom(1 << 20))
    rows.append(run("nkv-2pow62", hn, "1 MiB file claiming 4.6e18 KV pairs",
                    expect="struct.error at EOF quickly, no hang"))

    dep = os.path.join(d, "nested.gguf"); nested(dep, 2000)
    rows.append(run("nested-array-depth-2000", dep, "2000 nested ARRAY values before tokens", expect="RecursionError (uncaught by counter)"))

    many = os.path.join(d, "many-empty.gguf"); many_empty_strings(many, 1_000_000)
    rows.append(run("million-empty-string-tokens", many, "8 MB file, 1e6 zero-length tokens", expect="no cap on token count; time grows linearly"))

    for r in rows:
        print(json.dumps(r))
    if OUT:
        with open(OUT, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
