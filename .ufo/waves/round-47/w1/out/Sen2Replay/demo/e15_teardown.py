#!/usr/bin/env python3
"""E15: live-tool teardown on SIGTERM/SIGINT, escalation, log deletion.

Uses a fake server binary (a python script that does not serve anything), so
no llama-server is started; the tool's own lifecycle/teardown code is
exercised exactly as with a real child.
"""
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
LIVE = os.path.join(LANE, "tools/kama-llamacpp-live.py")
S = os.environ["S"]
ROOT = os.path.join(S, "e15")

GRACEFUL = """#!/usr/bin/env python3
import signal, sys, time
signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
time.sleep(30)
"""
STUBBORN = """#!/usr/bin/env python3
import signal, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
time.sleep(30)
"""


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def run_case(name, body, sig):
    d = os.path.join(ROOT, name)
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, "tmp")
    os.makedirs(tmp, exist_ok=True)
    srv = os.path.join(d, "llama-server")
    with open(srv, "w") as fh:
        fh.write(body)
    os.chmod(srv, 0o755)
    model = os.path.join(d, "m.gguf")
    with open(model, "wb") as fh:
        fh.write(b"m" * 32)
    out = os.path.join(d, "receipt.json")
    env = dict(os.environ, TMPDIR=tmp)
    p = subprocess.Popen([sys.executable, LIVE, "--server", srv, "--model", model,
                          "--model-sha256", sha(model), "--alias", "sen2",
                          "--ready-timeout", "60", "--out", out],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                         text=True)
    time.sleep(2.0)
    leftover_before = subprocess.run(["pgrep", "-f", srv], capture_output=True, text=True).stdout.split()
    p.send_signal(sig)
    t0 = time.monotonic()
    try:
        _o, err = p.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        p.kill()
        _o, err = p.communicate()
    dt = time.monotonic() - t0
    time.sleep(0.3)
    leftover_after = subprocess.run(["pgrep", "-f", srv], capture_output=True, text=True).stdout.split()
    for pid in leftover_after:  # never leave a stray behind
        try:
            os.kill(int(pid), signal.SIGKILL)
        except OSError:
            pass
    rec = {}
    if os.path.exists(out):
        with open(out) as fh:
            rec = json.load(fh)
    td = rec.get("teardown") or {}
    print(f"--- {name} signal={signal.Signals(sig).name} exit={p.returncode} "
          f"seconds={dt:.1f}")
    print(f"    child_pids_before_signal={leftover_before} "
          f"leftover_after={leftover_after}")
    print(f"    outcome={rec.get('outcome')} setup_error={rec.get('setup_error')}")
    print(f"    teardown: sigterm_sent={td.get('sigterm_sent')} "
          f"sigkill_sent={td.get('sigkill_sent')} "
          f"alive_at_start={td.get('alive_at_teardown_start')} "
          f"returncode={td.get('returncode')} port_refuses={td.get('port_refuses')} "
          f"log_path={td.get('log_path')!r} log_lines={len(td.get('log_lines') or [])}")
    print(f"    tmp_after={sorted(os.listdir(tmp))}")
    if err.strip():
        print(f"    stderr_tail={err.strip().splitlines()[-1][:120]}")


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    run_case("sigterm-graceful", GRACEFUL, signal.SIGTERM)
    run_case("sigint-graceful", GRACEFUL, signal.SIGINT)
    run_case("sigterm-stubborn", STUBBORN, signal.SIGTERM)
