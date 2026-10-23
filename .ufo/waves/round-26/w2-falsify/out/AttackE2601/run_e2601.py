#!/usr/bin/env python3
"""Scratch re-run of registry E26-01 on ports 47700-47703 (AttackE2601)."""
import json, os, signal, socket, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

SERVER = str(Path.home() / ".local/bin/llama-server")
MODEL = str(Path.home() / ".cache/kama-shokunin/models/stories260K.gguf")
HOST = "127.0.0.1"
SIG = "This server does not support slots endpoint. Start it with `--slots`"
OUT = Path(__file__).parent


def port_free(p):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, p)) != 0


def http(port, method, path, headers, body):
    data = None
    if body is not None:
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except (urllib.error.URLError, OSError) as e:
        return -1, {}, repr(e).encode()


def run(label, port, extra, requests):
    assert 47700 <= port <= 47703 and port_free(port), port
    argv = ["timeout", "120", SERVER, "-m", MODEL, "--host", HOST, "--port", str(port)] + extra
    log = OUT / f"{label}.log"
    fh = open(log, "wb")
    proc = subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    res = {"label": label, "argv": argv, "requests": []}
    try:
        end = time.time() + 60
        ready = False
        while time.time() < end and proc.poll() is None:
            if http(port, "GET", "/health", None, None)[0] == 200:
                ready = True
                break
            time.sleep(0.25)
        res["ready"] = ready
        if ready:
            for method, path, headers, body in requests:
                st, hd, data = http(port, method, path, headers, body)
                txt = data.decode("utf-8", "replace")
                res["requests"].append({"method": method, "path": path, "headers": headers,
                                        "body": body, "status": st,
                                        "content_type": hd.get("Content-Type"),
                                        "resp": txt, "sig_in_resp": SIG in txt})
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(10)
        fh.close()
    closed = False
    for _ in range(40):
        if port_free(port):
            closed = True
            break
        time.sleep(0.25)
    res["exit"] = proc.returncode
    res["port_closed"] = closed
    logtxt = log.read_text("utf-8", "replace")
    res["sig_in_log"] = SIG in logtxt
    res["log_lines_with_slots"] = [l for l in logtxt.splitlines() if "slots" in l.lower()][:20]
    return res


TRIGGER = [("GET", "/slots", {}, "")]
PROBES = TRIGGER + [
    ("GET", "/slots?id_slot=0&fail_on_no_slot=1", {}, None),
    ("GET", "/slots?q=ECHOPROBE_Start_it_with", {"X-Probe": "ECHOPROBE"}, None),
    ("POST", "/slots/0?action=save", {}, {"filename": "x.bin"}),
    ("GET", "/health", {}, None),
]

results = []
results.append(run("trigger-run1", 47700, ["--no-slots", "-t", "2"], TRIGGER))
results.append(run("trigger-run2", 47701, ["--no-slots", "-t", "2"], TRIGGER))
results.append(run("probe-noslots", 47702, ["--no-slots", "-t", "2"], PROBES))
results.append(run("control-default", 47703, ["-t", "2"], TRIGGER))
results.append(run("control-slots-on", 47700, ["--slots", "-t", "2"], TRIGGER))
(OUT / "results.json").write_text(json.dumps(results, indent=1) + "\n")
for r in results:
    print(r["label"], "ready", r["ready"], "exit", r["exit"], "port_closed", r["port_closed"],
          "sig_in_log", r["sig_in_log"])
    for q in r["requests"]:
        print("  ", q["method"], q["path"], "->", q["status"], q["content_type"], q["resp"][:300])
