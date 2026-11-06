#!/usr/bin/env python3
"""Run one hostile stub + kama-probe case and emit a JSON measurement.

usage: run_case.py NAME MODE [N] [KIB] [--probe PATH] [--sub check|snapshot]
                   [--expect ID] [--json] [--timeout S] [--registry PATH]
                   [--history PATH] [--maxwall S]
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time

SCRATCH = os.environ.get("SN01_SCRATCH", "/fast/scratch/hyaku/kama-r90/SN01AnswerSafety")
STUB = os.path.join(SCRATCH, "stub.py")


def tree_size(root):
    total = 0
    biggest_hdr = 0
    biggest_any = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            total += sz
            biggest_any = max(biggest_any, sz)
            if fn.endswith(".hdr"):
                biggest_hdr = max(biggest_hdr, sz)
    return total, biggest_hdr, biggest_any


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("mode")
    ap.add_argument("n", nargs="?", type=int, default=0)
    ap.add_argument("kib", nargs="?", type=int, default=8)
    ap.add_argument("--probe", default=os.environ.get("SN01_PROBE", os.path.join(SCRATCH, "probe-M.sh")))
    ap.add_argument("--sub", default="check")
    ap.add_argument("--expect", default="stories260K")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=5)
    ap.add_argument("--registry", default="")
    ap.add_argument("--history", default="")
    ap.add_argument("--snapfix", action="store_true")
    ap.add_argument("--rss", action="store_true")
    ap.add_argument("--path", default="")
    ap.add_argument("--maxwall", type=int, default=180)
    args = ap.parse_args()

    case = os.path.join(SCRATCH, "cases", args.name)
    shutil.rmtree(case, ignore_errors=True)
    os.makedirs(os.path.join(case, "tmpwatch"))
    portfile = os.path.join(case, "port")
    reqlog = os.path.join(case, "req.log")
    env = dict(os.environ)
    env["PORTFILE"] = portfile
    env["REQLOG"] = reqlog
    env["TMPDIR"] = os.path.join(case, "tmpwatch")
    env["KAMA_PROBE_TMPDIR"] = os.path.join(case, "tmpwatch")
    if args.path:
        env["PATH"] = args.path

    stub = subprocess.Popen([sys.executable, STUB, args.mode, str(args.n), str(args.kib)],
                            env=env, start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 10
    while not os.path.exists(portfile):
        if time.time() > deadline:
            stub.kill()
            print(json.dumps({"case": args.name, "error": "stub did not start"}))
            return 1
        time.sleep(0.02)
    port = open(portfile).read().strip()

    cmd = ["bash", args.probe, args.sub, "--port", port, "--expect", args.expect,
           "--timeout", str(args.timeout)]
    if args.json:
        cmd.append("--json")
    if args.snapfix:
        consumer = os.path.join(case, "consumer.txt")
        with open(consumer, "w") as fh:
            fh.write('baseURL = "http://127.0.0.1:%s/v1"\n' % port)
        args.registry = os.path.join(case, "registry.tsv")
        with open(args.registry, "w") as fh:
            fh.write("id\tconsumer_path\tresolver\tdeclared_baseurl\texpected_model_id\tnotes\n")
            fh.write("cli\t%s\tgrep:http://127.0.0.1:[0-9]+/v1\thttp://127.0.0.1:%s/v1\t%s\t-\n"
                     % (consumer, port, args.expect))
        args.history = os.path.join(case, "history")
    if args.sub == "snapshot":
        cmd = ["bash", args.probe, "snapshot", "--registry", args.registry,
               "--history", args.history, "--timeout", str(args.timeout)]
        if args.json:
            cmd.append("--json")

    peak = {"total": 0, "hdr": 0, "any": 0}
    stop = threading.Event()

    def poll():
        while not stop.is_set():
            t, h, a = tree_size(os.path.join(case, "tmpwatch"))
            peak["total"] = max(peak["total"], t)
            peak["hdr"] = max(peak["hdr"], h)
            peak["any"] = max(peak["any"], a)
            time.sleep(0.02)

    th = threading.Thread(target=poll, daemon=True)
    th.start()
    t0 = time.time()
    timefile = os.path.join(case, "time.txt")
    run_cmd = cmd
    if args.rss:
        run_cmd = ["/usr/bin/time", "-v", "-o", timefile] + cmd
    try:
        p = subprocess.run(run_cmd, env=env, capture_output=True, timeout=args.maxwall)
        rc, out, err = p.returncode, p.stdout, p.stderr
        timed_out = False
    except subprocess.TimeoutExpired as e:
        rc, out, err = -99, e.stdout or b"", e.stderr or b""
        timed_out = True
    wall = time.time() - t0
    stop.set()
    th.join(timeout=2)
    try:
        os.killpg(os.getpgid(stub.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    stub.wait(timeout=5)

    result = {
        "case": args.name,
        "mode": args.mode,
        "n": args.n,
        "kib": args.kib,
        "probe": os.path.basename(args.probe),
        "sub": args.sub,
        "rc": rc,
        "wall_s": round(wall, 3),
        "timed_out": timed_out,
        "tmp_peak_bytes": peak["total"],
        "hdr_peak_bytes": peak["hdr"],
        "file_peak_bytes": peak["any"],
        "requests": open(reqlog).read().split() if os.path.exists(reqlog) else [],
        "stdout_tail": out.decode("utf-8", "replace")[-1500:],
        "stderr_tail": err.decode("utf-8", "replace")[-600:],
    }
    with open(os.path.join(case, "result.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
