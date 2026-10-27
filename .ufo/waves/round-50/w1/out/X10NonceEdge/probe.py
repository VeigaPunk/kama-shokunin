#!/usr/bin/env python3
"""X10NonceEdge probe: 40 nonce forms through a witnessed, held llama-server.

Starts the LANE replay tool (round-50 build) on the committed round-48 v5
receipt-3, waits for its witness ready.json, checks the held server is the frozen
binary as the listener, then for each nonce form sends POST /tokenize
{"with_pieces": true} and POST /detokenize and applies the frozen C1 counter's
rules verbatim (imported from tools/round50-replay-bind-audit.py):

    piece ok  <=> isinstance(piece, str) and 0 <= id < len(vocab)
                  and vocab[id].replace("\u2581", " ") == piece
    detok ok  <=> content in (nonce, " " + nonce)

then writes the witness release file, waits for the replay to exit and records
the rerun receipt verdict, pid death and port refusal.
"""
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

S = sys.argv[1]
LANE = os.path.join(S, "lane")
COUNTER = os.path.join(LANE, "tools/round50-replay-bind-audit.py")
REPLAY = os.path.join(LANE, "tools/kama-live-replay.py")
RECEIPT = os.path.join(LANE, ".ufo/waves/round-48/c2/live/receipt-3.json")
WORK = os.path.join(S, "work")
WIT = os.path.join(S, "witness")
OUTJ = os.path.join(S, "replay.json")
RESULT = os.path.join(S, "nonce-probe.json")
SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
VOCAB_KEY = "tokenizer.ggml.tokens"


def log(msg):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_counter():
    spec = importlib.util.spec_from_file_location("r50counter", COUNTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # functions and constants only; __main__ guarded
    return mod


def find_model(root):
    hits = []
    for base, _dirs, files in os.walk(root):
        for f in files:
            if f.endswith(".gguf"):
                p = os.path.join(base, f)
                hits.append((sha_file(p), p))
    return hits


def make_nonces():
    """30 counter-form + 10 edge forms (exact, labelled)."""
    out = []
    for i in range(30):
        out.append(("counter-%02d" % (i + 1), "counter-form (lower hex16)",
                    f"kama witness {secrets.token_hex(8)}"))
    h = secrets.token_hex(8)                                  # 16 lower hex
    out += [
        ("edge-01-uppercase-hex", "uppercase hex, counter prefix",
         "kama witness " + h.upper()),
        ("edge-02-digits-only", "digits only, no letters or spaces",
         "".join(secrets.choice("0123456789") for _ in range(30))),
        ("edge-03-leading-space", "one leading space, else counter form",
         f" kama witness {h}"),
        ("edge-04-200-chars", "exactly 200 chars: counter prefix + 188 hex",
         "kama witness " + ("0123456789abcdef" * 12)[:188]),
        ("edge-05-non-ascii-mixed", "non-ASCII: accents, CJK, math sign, emoji",
         "kama witness é中文≥🙂 " + h),
        ("edge-06-newline-embedded", "one newline inside, else counter form",
         f"kama witness {h}\nabcdef01"),
        ("edge-07-trailing-newline", "one trailing newline",
         f"kama witness {h}\n"),
        ("edge-08-tab", "one tab between words",
         f"kama witness\t{h}"),
        ("edge-09-cjk-only", "CJK letters with no ASCII letters",
         "かま 目撃 " + h),
        ("edge-10-double-space", "double space after the first word",
         f"kama  witness {h}"),
    ]
    assert len(out) == 40, len(out)
    return out


def main():
    for d in (WORK, WIT):
        os.makedirs(d, exist_ok=True)
    counter = load_counter()
    result = {
        "schema": "kama-r50-x10-nonce-probe/v1",
        "seat": "X10NonceEdge",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {
            "lane_clone": LANE,
            "lane_head": subprocess.run(["git", "-C", LANE, "rev-parse", "HEAD"],
                                        capture_output=True, text=True).stdout.strip(),
            "receipt": RECEIPT,
            "receipt_sha256": sha_file(RECEIPT),
            "counter": COUNTER,
            "counter_sha256": sha_file(COUNTER),
            "replay": REPLAY,
            "replay_sha256": sha_file(REPLAY),
            "frozen_server_sha256": SERVER_SHA,
            "frozen_model_sha256": MODEL_SHA,
        },
        "nonces": [],
    }
    log(f"counter sha256 {result['inputs']['counter_sha256']}")
    log(f"replay  sha256 {result['inputs']['replay_sha256']}")

    # plant the counter's own canary name in THIS process: the replay gets an allow-list
    # env, so a canary in the held server's environ means the env leg would fail.
    os.environ["KAMA_R50_CANARY"] = "X10-" + secrets.token_hex(6)
    result["canary"] = "KAMA_R50_CANARY"
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL") if k in os.environ}
    env["TMPDIR"] = os.path.join(S, "tmp")
    os.makedirs(env["TMPDIR"], exist_ok=True)
    argv = [sys.executable, "-I", REPLAY, "--receipt", RECEIPT, "--work", WORK,
            "--out", OUTJ, "--witness-dir", WIT, "--witness-timeout", "900"]
    result["replay_argv"] = argv
    result["replay_env_keys"] = sorted(env)
    logfile = open(os.path.join(S, "replay.log"), "wb")
    t0 = time.time()
    proc = subprocess.Popen(argv, env=env, stdout=logfile, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, cwd=S)
    result["replay_pid"] = proc.pid

    ready = None
    deadline = t0 + 900
    while time.time() < deadline:
        if os.path.exists(os.path.join(WIT, "ready.json")):
            try:
                with open(os.path.join(WIT, "ready.json")) as fh:
                    ready = json.load(fh)
                break
            except (OSError, ValueError):
                pass
        if proc.poll() is not None:
            break
        time.sleep(0.25)
    result["ready_wait_s"] = round(time.time() - t0, 3)
    result["ready"] = ready
    if ready is None:
        result["outcome"] = "no-ready"
        result["replay_returncode"] = proc.wait(timeout=300)
        with open(RESULT, "w") as fh:
            json.dump(result, fh, indent=1)
        log("NO READY: " + result["outcome"])
        return 1

    pid, port = int(ready["pid"]), int(ready["port"])
    log(f"ready pid {pid} port {port}")
    held = {
        "exe_sha256": sha_file(f"/proc/{pid}/exe"),
        "exe_matches_frozen": sha_file(f"/proc/{pid}/exe") == SERVER_SHA,
        "listen_inodes": sorted(counter.listen_inodes(port)),
        "pid_socket_inodes": sorted(counter.pid_socket_inodes(pid)),
        "port_refuses_before_release": counter.port_refuses(port),
        "pid_alive": counter.pid_alive(pid),
    }
    held["listen_owned_by_pid"] = bool(set(held["listen_inodes"]) & set(held["pid_socket_inodes"]))
    result["held"] = held

    models = find_model(WORK)
    result["model_files"] = [{"sha256": s, "path": p} for s, p in models]
    mp = next((p for s, p in models if s == MODEL_SHA), None)
    result["model_path"] = mp
    if mp is None:
        result["outcome"] = "no-model"
        _release_and_finish(proc, WIT, result, pid, port, counter, t0)
        return 1
    vocab = counter.gguf_tokens(mp)
    result["vocab_size"] = len(vocab)
    log(f"vocab {len(vocab)} tokens")

    # sanity: the observed mapping of the held server hashes to the frozen model
    probs = []
    result["mapped"] = counter.mapped_model(pid, probs)
    result["mapped_problems"] = probs
    # the frozen counter's own witness function, verbatim, on the held server
    oprobs = []
    ononce, omapped = counter.observe(pid, port, vocab, "KAMA_R50_CANARY", oprobs)
    result["counter_observe"] = {"nonce": ononce, "mapped": omapped, "problems": oprobs}
    log(f"counter.observe nonce={ascii(ononce)} problems={oprobs}")

    for label, kind, nonce in make_nonces():
        row = {"label": label, "kind": kind, "nonce": nonce,
               "chars": len(nonce), "nonce_repr": ascii(nonce)}
        try:
            tk = counter.post(port, "/tokenize", {"content": nonce, "with_pieces": True})["tokens"]
            ids = [t["id"] for t in tk]
            pieces = [t.get("piece") for t in tk]
            bad = [t for t in tk if not (isinstance(t.get("piece"), str)
                                         and 0 <= t["id"] < len(vocab)
                                         and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
            row.update({"n_tokens": len(tk), "ids": ids, "pieces": pieces,
                        "pieces_ok": bool(ids) and not bad,
                        "bad_pieces": bad[:5], "n_bad_pieces": len(bad)})
            dt = counter.post(port, "/detokenize", {"tokens": ids})["content"]
            row.update({"detok": dt, "detok_repr": ascii(dt),
                        "detok_ok": dt in (nonce, " " + nonce),
                        "detok_exact": dt == nonce,
                        "detok_leading_space": dt == " " + nonce})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            row.update({"error": f"{type(exc).__name__}: {exc}", "pieces_ok": False,
                        "detok_ok": False})
        row["rule_ok"] = bool(row.get("pieces_ok")) and bool(row.get("detok_ok"))
        if row.get("pieces"):
            try:
                j = b"".join(p.encode("utf-8") if isinstance(p, str) else bytes(p)
                             for p in row["pieces"]).decode("utf-8", "backslashreplace")
                row["join"] = j
                row["join_rule_ok"] = j in (nonce, " " + nonce)
            except (TypeError, ValueError) as exc:
                row["join_rule_ok"] = False
                row["join_error"] = f"{type(exc).__name__}: {exc}"
        result["nonces"].append(row)
        log(f"{label:24s} tokens={row.get('n_tokens','-'):>3} pieces_ok={row.get('pieces_ok')} "
            f"detok_ok={row.get('detok_ok')} detok={row.get('detok_repr', row.get('error'))!s:.60}")

    _release_and_finish(proc, WIT, result, pid, port, counter, t0)
    return 0


def _release_and_finish(proc, WIT, result, pid, port, counter, t0):
    log("releasing the witness hold")
    with open(os.path.join(WIT, "release"), "w") as fh:
        fh.write("released by X10NonceEdge after 40-nonce probe\n")
    try:
        rc = proc.wait(timeout=300)
    except subprocess.TimeoutExpired:
        proc.terminate()
        rc = proc.wait(timeout=60)
        result["replay_forced_terminate"] = True
    result["replay_returncode"] = rc
    result["replay_total_s"] = round(time.time() - t0, 3)
    time.sleep(1.0)
    result["after"] = {
        "pid_alive": counter.pid_alive(pid),
        "port_refuses": counter.port_refuses(port),
        "ready_gone": not os.path.exists(os.path.join(WIT, "ready.json")),
    }
    try:
        with open(OUTJ) as fh:
            replay = json.load(fh)
        result["replay_out"] = {k: replay.get(k) for k in
                                ("schema", "match", "refused", "mismatches", "notes",
                                 "rerun_receipt")}
        rr = replay.get("rerun_receipt")
        if rr and os.path.exists(rr):
            with open(rr) as fh:
                r = json.load(fh)
            result["rerun"] = {k: r.get(k) for k in
                               ("schema", "outcome", "child_pid", "port", "model_mapping",
                                "witness", "port_listener_ownership", "model_sha256_post")}
            shutil.copy(rr, os.path.join(S, "rerun-receipt.json"))
    except (OSError, ValueError) as exc:
        result["replay_out_error"] = f"{type(exc).__name__}: {exc}"
    rows = result["nonces"]
    result["summary"] = {
        "total": len(rows),
        "rule_ok": sum(1 for r in rows if r.get("rule_ok")),
        "pieces_ok": sum(1 for r in rows if r.get("pieces_ok")),
        "detok_ok": sum(1 for r in rows if r.get("detok_ok")),
        "counter_form_rule_ok": sum(1 for r in rows
                                    if r["label"].startswith("counter") and r.get("rule_ok")),
        "edge_rule_ok": sum(1 for r in rows
                            if r["label"].startswith("edge") and r.get("rule_ok")),
        "join_rule_ok": sum(1 for r in rows if r.get("join_rule_ok")),
        "detok_exact": sum(1 for r in rows if r.get("detok_exact")),
        "detok_leading_space": sum(1 for r in rows if r.get("detok_leading_space")),
        "failing_labels": [r["label"] for r in rows if not r.get("rule_ok")],
        "join_failing_labels": [r["label"] for r in rows if not r.get("join_rule_ok")],
    }
    result["outcome"] = "done"
    with open(RESULT, "w") as fh:
        json.dump(result, fh, indent=1)
    log("summary " + json.dumps(result["summary"]))


if __name__ == "__main__":
    sys.exit(main())
