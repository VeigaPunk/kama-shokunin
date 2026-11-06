#!/usr/bin/env python3
"""Case driver: build a hostile /v1/models body, run one probe invocation on a free
loopback port, capture wall time / peak RSS (GNU time -v), stdout, stderr, exit code.

usage: drive.py CASE BODYSPEC [--timeout S] [--json] [--strace] [--expect ID]
BODYSPEC is a JSON file already written by the caller (paths substituted)."""
import json, os, socket, subprocess, sys, time

ROOT = "/fast/scratch/hyaku/kama-r89/SN01ProbeSafety"
PROBE = ROOT + "/probe-M.sh"
TMP = ROOT + "/tmp"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    case, body = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    timeout = 120.0
    json_out = "--json" in args
    strace = "--strace" in args
    expect = "*"
    props = ""
    for i, a in enumerate(args):
        if a == "--timeout":
            timeout = float(args[i + 1])
        if a == "--expect":
            expect = args[i + 1]
        if a == "--props":
            props = args[i + 1]
    port = free_port()
    log = f"{ROOT}/out/{case}.requests.log"
    if os.path.exists(log):
        os.remove(log)
    env = dict(os.environ)
    env["TMPDIR"] = TMP
    env["KAMA_PROBE_TMPDIR"] = TMP
    srv = subprocess.Popen([sys.executable, ROOT + "/srv.py", str(port), body, props, log],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True)
    # wait for the listener
    for _ in range(200):
        try:
            with socket.create_connection(("127.0.0.1", port), 0.1):
                break
        except OSError:
            time.sleep(0.02)
    cmd = ["/usr/bin/time", "-v", "bash", PROBE, "listeners", "--port", str(port),
           "--expect", expect] + (["--json"] if json_out else [])
    if strace:
        cmd = ["/usr/bin/time", "-v", "strace", "-f", "-qq", "-e",
               "trace=openat,open,creat,unlink,unlinkat,mkdir,rename,write",
               "-o", f"{ROOT}/out/{case}.strace", "bash", PROBE, "listeners",
               "--port", str(port), "--expect", expect] + (["--json"] if json_out else [])
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           timeout=timeout, stdin=subprocess.DEVNULL)
        out, err, rc, to = p.stdout, p.stderr, p.returncode, False
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        rc, to = "TIMEOUT", True
    wall = time.time() - t0
    try:
        os.killpg(srv.pid, 9)
    except ProcessLookupError:
        pass
    rss = ""
    for line in err.splitlines():
        if "Maximum resident" in line or "Elapsed (wall clock)" in line or "User time" in line or "System time" in line:
            rss += line.strip() + " | "
    rec = {"case": case, "port": port, "rc": rc, "timeout": to, "wall_s": round(wall, 3),
           "time_v": rss.strip(" |"), "stdout": out, "stderr_tail": "\n".join(err.splitlines()[-4:]),
           "requests": open(log).read().splitlines() if os.path.exists(log) else []}
    with open(f"{ROOT}/out/{case}.json", "w") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps({k: rec[k] for k in ("case", "rc", "timeout", "wall_s", "time_v")}))
    print("STDOUT:\n" + out)


main()
