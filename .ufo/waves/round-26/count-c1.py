#!/usr/bin/env python3
"""Round-26 C1 counter (depth): live-reproduced llama-server error signatures in SKILL.md.

Frozen predicate (the same sentence as preregistration.json C1.predicate and the
label `counted` in the receipt):

  A signature is COUNTED iff (a) a table row of the SKILL.md section whose heading
  starts with "## Round-26 live error signatures" begins with the registry id and
  contains the registry signature string verbatim and the registry S### token;
  (b) the signature is at least 20 bytes and does not occur in SKILL.md or any
  tracked file under corpus/ at base 1560e4d8; (c) its S### row exists in
  corpus/SOURCES.md of the measured tree, does not exist at base, and names the
  source file and commit 704366d; (d) the signature occurs verbatim in that
  source file, whose sha256 equals the pinned 704366d value; (e) the counter's
  own run of the registered trigger against the sha256-pinned llama-server and
  fixture model shows the error (http: status >= 400; startup: the process
  exits non-zero within 30 s) and contains the signature in the registered
  channel (http: response body; startup: stdout+stderr), and the signature does
  not occur in the trigger's own request bytes; (f) the signature does not occur,
  verbatim or with all whitespace removed on both sides, in the counter's healthy
  baseline run or in the output of `llama-server --help` and `--version`; (g) the signature is neither a
  substring nor a superstring of an earlier counted signature, it does not
  occur in the channel text of an earlier counted row, no earlier counted
  signature occurs in its own channel text, and its trigger differs from
  every earlier counted trigger (one fault, one counted row).

Claim met iff counted >= 12 (preregistration.json C1.target).

Usage: count-c1.py [--lane DIR] [--repo GITDIR] [--json] [--out FILE]
Exit: 0 ran (whatever the count), 2 could not evaluate (pins, missing inputs,
unsafe port, baseline failed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "1560e4d83f42b04f40336357de6f9637eafa0f4b"
TARGET = 12
MIN_BYTES = 20
SERVER = Path.home() / ".local/bin/llama-server"
SERVER_SHA256 = "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA256 = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
COMMIT = "704366d"
SOURCE_DIR = ".ufo/waves/round-26/sources/llama.cpp-704366d"
SOURCE_SHA256 = {
    "arg.cpp": "bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d",
    "common.cpp": "d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4",
    "gguf.cpp": "7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5",
    "llama-context.cpp": "2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5",
    "llama-model-loader.cpp": "7975d83406627e405d36876472495c6111696e70db66c65a629d6213ec54fc04",
    "llama.cpp": "8058a140d444b67bf64a1ce393d241dfd60080f4b117130c6f82e637e2109233",
    "server-common.cpp": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442",
    "server-context.cpp": "dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329",
    "server-http.cpp": "24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb",
    "server-models.cpp": "9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a",
    "server-queue.cpp": "168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba",
    "server-task.cpp": "4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495",
    "server.cpp": "2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4",
}
REGISTRY = "registry/error-signatures-r26.json"
HEADING = "## Round-26 live error signatures"
HOST = "127.0.0.1"
PORTS = range(47560, 47580)
FORBIDDEN_ARGS = {"-m", "--model", "--host", "--port", "-hf", "--hf-repo", "-mu",
                  "--model-url", "--api-key-file", "--path", "--log-file"}
MISSING_MODEL = "/nonexistent/kama-r26/missing.gguf"
STARTUP_WAIT = 30.0
READY_WAIT = 60.0
REQUEST_TIMEOUT = 30.0
BASELINE_REQUESTS = [
    ("GET", "/health", None),
    ("GET", "/v1/models", None),
    ("GET", "/props", None),
    ("GET", "/slots", None),
    ("POST", "/completion", {"prompt": "Once upon a time", "n_predict": 8}),
    ("POST", "/v1/chat/completions",
     {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 8}),
    ("POST", "/tokenize", {"content": "Once upon a time"}),
]


class CannotEvaluate(Exception):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_show(repo: str, rev: str, path: str) -> str | None:
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                       capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def present_at_base(repo: str, sig: str) -> bool:
    r = subprocess.run(["git", "-C", repo, "grep", "-F", "-q", "-e", sig, BASE,
                        "--", "SKILL.md", "corpus"], capture_output=True, timeout=60)
    if r.returncode not in (0, 1):
        raise CannotEvaluate(f"git grep at base failed: {r.stderr.decode()[:200]}")
    return r.returncode == 0


def sources_rows(text: str) -> dict[str, str]:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(S\d{3,})\s*\|", line)
        if m:
            rows[m.group(1)] = line
    return rows


def skill_rows(text: str) -> list[str]:
    rows, inside = [], False
    for line in text.splitlines():
        if line.startswith("#"):
            inside = line.startswith(HEADING)
            continue
        if inside and line.startswith("|"):
            rows.append(line)
    return rows


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, port)) != 0


def pick_port(used: set[int]) -> int:
    for p in PORTS:
        if p not in used and port_free(p):
            used.add(p)
            return p
    raise CannotEvaluate("no free port in 47560-47579")


def http(port: int, method: str, path: str, headers: dict | None, body) -> tuple[int, bytes]:
    data = None
    if body is not None:
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        return -1, repr(e).encode()


def launch(argv: list[str], log: Path) -> subprocess.Popen:
    fh = open(log, "wb")
    return subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)


def teardown(proc: subprocess.Popen, port: int) -> bool:
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=10)
    for _ in range(20):
        if port_free(port):
            return True
        time.sleep(0.25)
    return False


def wait_ready(proc: subprocess.Popen, port: int) -> bool:
    end = time.time() + READY_WAIT
    while time.time() < end:
        if proc.poll() is not None:
            return False
        status, _ = http(port, "GET", "/health", None, None)
        if status == 200:
            return True
        time.sleep(0.25)
    return False


def model_path(kind: str, tmp: Path) -> str:
    if kind == "fixture":
        return str(MODEL)
    if kind == "missing":
        return MISSING_MODEL
    if kind == "junk":
        p = tmp / "junk.gguf"
        p.write_bytes(b"this is not a gguf model file, kama round 26 junk control\n")
        return str(p)
    raise CannotEvaluate(f"unknown model kind {kind!r}")


def base_argv(model: str, port: int) -> list[str]:
    return [str(SERVER), "-m", model, "--host", HOST, "--port", str(port)]


def run_baseline(tmp: Path, used: set[int]) -> str:
    port = pick_port(used)
    log = tmp / "baseline.log"
    proc = launch(base_argv(str(MODEL), port), log)
    parts = []
    try:
        if not wait_ready(proc, port):
            raise CannotEvaluate("baseline server never became healthy")
        for method, path, body in BASELINE_REQUESTS:
            status, data = http(port, method, path, None, body)
            if status != 200:
                raise CannotEvaluate(f"baseline {method} {path} -> {status}")
            parts.append(data.decode("utf-8", "replace"))
    finally:
        closed = teardown(proc, port)
    if not closed:
        raise CannotEvaluate("baseline port did not close")
    parts.append(log.read_text("utf-8", "replace"))
    for flag in ("--help", "--version"):
        r = subprocess.run([str(SERVER), flag], capture_output=True, timeout=30,
                           stdin=subprocess.DEVNULL)
        text = (r.stdout + r.stderr).decode("utf-8", "replace")
        if r.returncode != 0 or not text.strip():
            raise CannotEvaluate(f"informational baseline {flag} exit {r.returncode}")
        parts.append(text)
    return "\n".join(parts)


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def run_trigger(entry: dict, tmp: Path, used: set[int]) -> dict:
    port = pick_port(used)
    args = [str(a) for a in entry.get("args", [])]
    bad = sorted(set(args) & FORBIDDEN_ARGS)
    if bad:
        return {"error": f"forbidden args {bad}"}
    model = model_path(entry.get("model", "fixture"), tmp)
    argv = base_argv(model, port) + args
    log = tmp / f"{entry['id']}.log"
    blocker = None
    if entry.get("occupy_port"):
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        blocker.bind((HOST, port))
        blocker.listen(1)
    proc = launch(argv, log)
    out = {"port": port, "argv_extra": args}
    try:
        if entry["channel"] == "startup":
            try:
                rc = proc.wait(timeout=STARTUP_WAIT)
            except subprocess.TimeoutExpired:
                rc = None
            out["exit"] = rc
            out["error_shown"] = rc is not None and rc != 0
        elif entry["channel"] == "http":
            if not wait_ready(proc, port):
                out["error_shown"] = False
                out["ready"] = False
            else:
                req = entry["request"]
                status, data = http(port, req["method"], req["path"],
                                    req.get("headers"), req.get("body"))
                out["status"] = status
                out["body"] = data.decode("utf-8", "replace")
                out["error_shown"] = status >= 400
        else:
            out["error_shown"] = False
            out["error"] = f"unknown channel {entry['channel']!r}"
    finally:
        if blocker is not None:
            blocker.close()
        out["port_closed"] = teardown(proc, port)
    out["log"] = log.read_text("utf-8", "replace")
    return out


def main() -> int:
    here = Path(__file__).resolve()
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=str(here.parents[3]))
    ap.add_argument("--repo", default="/home/vgpnk/Projects/shokunin/kama-shokunin")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    lane = Path(a.lane)
    receipt = {"schema": "kama-r26-c1-count/v1", "base": BASE, "lane": str(lane),
               "target": TARGET, "rows": []}
    try:
        if sha256_file(SERVER.resolve()) != SERVER_SHA256:
            raise CannotEvaluate("llama-server sha256 mismatch")
        if sha256_file(MODEL) != MODEL_SHA256:
            raise CannotEvaluate("fixture model sha256 mismatch")
        reg_path = lane / REGISTRY
        skill_path = lane / "SKILL.md"
        src_path = lane / "corpus/SOURCES.md"
        registry = json.loads(reg_path.read_text()) if reg_path.exists() else {"signatures": []}
        skill = skill_rows(skill_path.read_text()) if skill_path.exists() else []
        rows_now = sources_rows(src_path.read_text()) if src_path.exists() else {}
        base_sources = git_show(a.repo, BASE, "corpus/SOURCES.md")
        if base_sources is None:
            raise CannotEvaluate("cannot read base SOURCES.md")
        rows_base = sources_rows(base_sources)
        entries = registry.get("signatures", [])
        with tempfile.TemporaryDirectory(prefix="kama-r26-c1-") as td:
            tmp = Path(td)
            used: set[int] = set()
            baseline = run_baseline(tmp, used) if entries else ""
            receipt["baseline_sha256"] = hashlib.sha256(baseline.encode()).hexdigest()
            counted_sigs: list[str] = []
            counted_texts: list[str] = []
            counted_triggers: list[str] = []
            seen_ids: set[str] = set()
            for e in entries:
                sig = e.get("signature", "")
                sid = e.get("id", "")
                srow = e.get("source", {}).get("row", "")
                sfile = e.get("source", {}).get("file", "")
                r = {"id": sid, "signature": sig, "checks": {}}
                c = r["checks"]
                c["id_unique"] = bool(sid) and sid not in seen_ids
                seen_ids.add(sid)
                c["a_skill_row"] = any(
                    re.match(r"^\|\s*" + re.escape(sid) + r"\s*\|", row)
                    and sig in row and re.search(r"\b" + re.escape(srow) + r"\b", row)
                    for row in skill) if sid and sig and srow else False
                c["b_long"] = len(sig.encode()) >= MIN_BYTES
                c["b_new_at_base"] = (not present_at_base(a.repo, sig)) if sig else False
                row_text = rows_now.get(srow, "")
                c["c_source_row"] = (bool(row_text) and srow not in rows_base
                                     and sfile in row_text and COMMIT in row_text)
                sp = lane / SOURCE_DIR / sfile
                c["d_source_pinned"] = (sfile in SOURCE_SHA256 and sp.is_file()
                                        and sha256_file(sp) == SOURCE_SHA256[sfile])
                c["d_in_source"] = c["d_source_pinned"] and sig.encode() in sp.read_bytes()
                trig_key = json.dumps({k: e.get(k) for k in
                                       ("channel", "args", "model", "occupy_port", "request")},
                                      sort_keys=True)
                req = e.get("request") or {}
                body = req.get("body")
                body_text = body if isinstance(body, str) else json.dumps(body)
                req_bytes = "\n".join([trig_key, " ".join(map(str, e.get("args", []))),
                                       str(req.get("path", "")), json.dumps(req.get("headers")),
                                       body_text or ""])
                prior_ok = all(c.values())
                channel_text = ""
                if prior_ok:
                    run = run_trigger(e, tmp, used)
                    if not run.get("port_closed"):
                        raise CannotEvaluate(f"{sid}: port did not close")
                    channel_text = run.get("body", "") if e["channel"] == "http" else run.get("log", "")
                    c["e_error_shown"] = bool(run.get("error_shown"))
                    c["e_signature_seen"] = sig in channel_text
                    c["e_not_echoed"] = sig not in req_bytes
                    c["f_absent_from_baseline"] = (sig not in baseline
                                                   and squash(sig) not in squash(baseline))
                    r["observed"] = {k: run.get(k) for k in ("status", "exit", "ready")}
                    r["observed"]["channel_sha256"] = hashlib.sha256(channel_text.encode()).hexdigest()
                    r["observed"]["channel_excerpt"] = channel_text[:400]
                else:
                    r["skipped_run"] = "a static check failed"
                c["g_distinct"] = (all(sig not in s and s not in sig for s in counted_sigs)
                                   and all(sig not in t for t in counted_texts)
                                   and all(s not in channel_text for s in counted_sigs)
                                   and trig_key not in counted_triggers)
                r["counted"] = all(c.values()) and "e_error_shown" in c
                if r["counted"]:
                    counted_sigs.append(sig)
                    counted_texts.append(channel_text)
                    counted_triggers.append(trig_key)
                receipt["rows"].append(r)
        receipt["registered"] = len(entries)
        receipt["counted"] = sum(1 for r in receipt["rows"] if r["counted"])
        receipt["met"] = receipt["counted"] >= TARGET
    except CannotEvaluate as ex:
        receipt["could_not_evaluate"] = str(ex)
        print(f"could-not-evaluate: {ex}", file=sys.stderr)
        if a.out:
            Path(a.out).write_text(json.dumps(receipt, indent=1) + "\n")
        return 2
    if a.out:
        Path(a.out).write_text(json.dumps(receipt, indent=1) + "\n")
    if a.json:
        print(json.dumps(receipt, indent=1))
    failed = [f"{r['id']}:{','.join(k for k, v in r['checks'].items() if not v)}"
              for r in receipt["rows"] if not r["counted"]]
    print(f"registered {receipt['registered']} counted {receipt['counted']} "
          f"target {TARGET} met {receipt['met']} not-counted {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
