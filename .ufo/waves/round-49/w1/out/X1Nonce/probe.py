#!/usr/bin/env python3
"""X1Nonce probe: hold one witnessed rerun of round-48 receipt-3 and replay the C1
counter's nonce rule over 30 counter-form nonces + 10 edge forms."""
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r49/X1Nonce"
LANE = os.path.join(S, "lane")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-3.json")
WORK = os.path.join(S, "work")
WD = os.path.join(S, "wd")
OUTJ = os.path.join(S, "replay.json")


def load_counter():
    path = os.path.join(LANE, "tools", "round49-replay-witness-audit.py")
    spec = importlib.util.spec_from_file_location("c1_counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rule(c1, port, vocab, nonce):
    """Exactly the C1 rule from observe(): pieces equal vocab with U+2581 as space,
    detokenized == nonce or ' ' + nonce."""
    rec = {"nonce": nonce, "len": len(nonce)}
    try:
        tk = c1.post(port, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
    except Exception as exc:  # noqa: BLE001 - record, never crash the probe
        rec.update(rule_holds=False, stage="tokenize", error=f"{type(exc).__name__}: {exc}")
        return rec
    ids = [t["id"] for t in tk]
    bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                 and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
    rec["ids"] = ids
    rec["pieces"] = [t.get("piece") for t in tk]
    rec["bad"] = bad
    rec["pieces_join"] = "".join(t.get("piece") or "" for t in tk)
    if not ids:
        rec.update(rule_holds=False, stage="empty")
        return rec
    if bad:
        rec.update(rule_holds=False, stage="pieces")
        return rec
    try:
        dt = c1.post(port, "/detokenize", {"tokens": ids})["content"]
    except Exception as exc:  # noqa: BLE001
        rec.update(rule_holds=False, stage="detokenize", error=f"{type(exc).__name__}: {exc}")
        return rec
    rec["detok"] = dt
    rec["detok_is_nonce"] = dt == nonce
    rec["detok_is_space_nonce"] = dt == " " + nonce
    ok = dt in (nonce, " " + nonce)
    rec.update(rule_holds=ok, stage="ok" if ok else "detok-mismatch")
    return rec


def main():
    c1 = load_counter()
    os.makedirs(WD, exist_ok=True)
    log = open(os.path.join(S, "replay.log"), "wb")
    env = dict(os.environ, TMPDIR=S)
    cmd = [sys.executable, os.path.join(LANE, "tools", "kama-live-replay.py"),
           "--receipt", RECEIPT, "--work", WORK, "--out", OUTJ,
           "--witness-dir", WD, "--witness-timeout", "600"]
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, cwd=LANE, env=env, stdout=log, stderr=subprocess.STDOUT)
    result = {"schema": "kama-x1-nonce-probe/v1", "replay_cmd": cmd, "ready": None}
    ready = None
    try:
        while time.monotonic() - t0 < 600 and p.poll() is None:
            try:
                with open(os.path.join(WD, "ready.json")) as fh:
                    ready = json.load(fh)
                break
            except (OSError, ValueError):
                time.sleep(0.1)
        result["ready_after_s"] = round(time.monotonic() - t0, 1)
        result["ready"] = ready
        if not ready:
            raise SystemExit("no ready.json")
        pid, port = ready["pid"], ready["port"]
        model = os.path.join(WORK, "download", "stories260K.gguf")
        vocab = c1.gguf_tokens(model)
        result["vocab_len"] = len(vocab)
        result["vocab_uses_u2581"] = sum(1 for v in vocab if "\u2581" in v)
        result["exe_sha256"] = c1.sha_file(f"/proc/{pid}/exe")
        result["exe_is_frozen"] = result["exe_sha256"] == c1.SERVER_SHA
        result["listen_inodes"] = sorted(c1.listen_inodes(port))
        result["listen_owned_by_pid"] = bool(c1.listen_inodes(port) & c1.pid_socket_inodes(pid))
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            result["argv"] = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]
        result["health_before"] = c1.post(port, "/health", {}) if False else None
        import urllib.request
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        result["health_before"] = json.loads(opener.open(
            f"http://127.0.0.1:{port}/health", timeout=10).read())

        counter_form = [f"kama witness {secrets.token_hex(8)}" for _ in range(30)]
        edge = [
            "kama witness 0123456789ABCDEF",          # uppercase hex suffix
            "KAMA WITNESS 0123456789abcdef",          # uppercase prefix words
            "kama witness 0123456789012345",          # digits only
            " kama witness 0123456789abcdef",         # nonce starts with a space
            "kama witness " + "a" * 187,              # 200 characters total
            "kama witness " + "0" * 200,              # 200-char hex-ish payload
            "kama witness caf\u00e9" + "0123456789ab",  # non-ASCII é
            "kama witness 0123456789abcdef\n",        # embedded newline at end
            "kama witness ",                          # empty suffix
            "kama witness 0123456789abcdef0",         # 17 hex chars (one long)
        ]
        result["edge_forms"] = edge
        result["counter_form"] = [rule(c1, port, vocab, n) for n in counter_form]
        result["edge"] = [rule(c1, port, vocab, n) for n in edge]
        result["health_after"] = json.loads(opener.open(
            f"http://127.0.0.1:{port}/health", timeout=10).read())
        result["pid_alive_before_release"] = c1.pid_alive(pid)
    finally:
        os.makedirs(WD, exist_ok=True)
        with open(os.path.join(WD, "release"), "w") as fh:
            fh.write("released by X1Nonce\n")
        try:
            code = p.wait(timeout=300)
        except subprocess.TimeoutExpired:
            p.kill()
            code = None
        result["replay_exit"] = code
        log.close()
        try:
            with open(OUTJ) as fh:
                rj = json.load(fh)
            result["replay_match"] = rj.get("match")
            result["replay_refused"] = rj.get("refused")
            result["replay_mismatches"] = rj.get("mismatches")
            rr = rj.get("rerun_receipt")
            if rr and os.path.isfile(rr):
                with open(rr) as fh:
                    rerun = json.load(fh)
                result["rerun_witness"] = rerun.get("witness")
                result["rerun_outcome"] = rerun.get("outcome")
                result["rerun_teardown"] = (rerun.get("teardown") or {}).get("returncode")
                result["rerun_port_refuses"] = (rerun.get("teardown") or {}).get("port_refuses")
        except (OSError, ValueError) as exc:
            result["replay_read_error"] = repr(exc)
        if ready:
            time.sleep(0.5)
            result["pid_alive_after"] = c1.pid_alive(ready["pid"])
            result["port_refuses_after"] = c1.port_refuses(ready["port"])
        cf = result.get("counter_form") or []
        eg = result.get("edge") or []
        result["summary"] = {
            "counter_form_holds": sum(1 for r in cf if r.get("rule_holds")),
            "counter_form_total": len(cf),
            "edge_holds": sum(1 for r in eg if r.get("rule_holds")),
            "edge_total": len(eg),
        }
        with open(os.path.join(S, "probe-result.json"), "w") as fh:
            json.dump(result, fh, indent=2)
        print(json.dumps(result["summary"]))
        print(json.dumps([
            {"i": i, "holds": r.get("rule_holds"), "stage": r.get("stage"), "len": r.get("len"),
             "pieces": r.get("pieces"), "detok": r.get("detok")} for i, r in enumerate(eg)], indent=1))
        print("counter_form_stages", sorted({r.get("stage") for r in cf}))
        print("replay_exit", result.get("replay_exit"), "match", result.get("replay_match"),
              "witness", result.get("rerun_witness"))
        print("pid_alive_after", result.get("pid_alive_after"),
              "port_refuses_after", result.get("port_refuses_after"))


if __name__ == "__main__":
    main()
