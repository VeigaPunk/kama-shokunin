#!/usr/bin/env python3
"""V2: fresh router per rev per rep; probe under load FIRST, oracle after (oracle mutates status to failed)."""
import hashlib, json, os, signal, socket, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import driver as D

LANE = D.LANE
SCRATCH = D.SCRATCH
def fresh_router(port_needed=True):
    models = SCRATCH / "models"
    preset = SCRATCH / "presets.ini"
    cwd = SCRATCH / "router-cwd2"; cwd.mkdir(exist_ok=True)
    # unique log per call
    log = SCRATCH / f"router2-{time.time_ns()}.log"
    port = D.start_router(models, preset, cwd, log, str(SCRATCH))
    return port

def one(label, rev, probe_path, env, pcwd):
    port = fresh_router()
    try:
        ents = D.entries(port)
        assert ents["bad00"]["value"] == "unloaded", ents["bad00"]
        n = int(subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip() or "32")
        D.start_burners(n)
        try:
            # probe under load FIRST
            l = D.load1()
            pv, pr, rc, dt, raw = D.run_probe(probe_path, port, "bad00", env, pcwd)
            print(f"[{label}] REP probe-load target=bad00 burners={n} load={l} => {pv}/{pr} rc={rc} wall={dt:.2f}s", flush=True)
            # wildcard under same load
            pv2, pr2, rc2, dt2, raw2 = D.run_probe(probe_path, port, "*", env, pcwd)
            print(f"[{label}] REP probe-load target=* load={D.load1()} => {pv2}/{pr2} rc={rc2} wall={dt2:.2f}s", flush=True)
        finally:
            D.stop_burners()
        # oracle after probes (validates router truth: 500 failed-to-load)
        l = D.load1()
        ov = D.oracle(port, "bad00")
        print(f"[{label}] REP oracle target=bad00 load={l} => {ov}", flush=True)
        return (pv, pr, dt, ov)
    finally:
        # kill router child (no burners left)
        for p in list(D.CHILDREN):
            try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except Exception:
                try: p.kill()
                except Exception: pass
            try: p.wait(timeout=5)
            except Exception: pass
        D.CHILDREN.clear()

def main():
    signal.signal(signal.SIGTERM, D.kill_all); signal.signal(signal.SIGINT, D.kill_all)
    pcwd = SCRATCH / "probe-cwd"; pcwd.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(pcwd))
    # probes already extracted by driver v1
    probes = {}
    for label, rev in (("BASE", D.BASE), ("M1", D.M1)):
        full = subprocess.run(["git", "-C", str(LANE), "rev-parse", "--verify", rev + "^{commit}"],
                              capture_output=True, text=True, check=True).stdout.strip()
        data = subprocess.run(["git", "-C", str(LANE), "show", f"{full}:tools/kama-probe.sh"],
                              capture_output=True, check=True).stdout
        pp = SCRATCH / f"probe2-{label}.sh"; pp.write_bytes(data); pp.chmod(0o755)
        probes[label] = (full, pp)
        print(f"[{label}] rev={full} probe_sha256={hashlib.sha256(data).hexdigest()}", flush=True)
    results = {}
    for rep in range(2):
        for label in ("BASE", "M1"):
            full, pp = probes[label]
            results[(label, rep)] = one(label, full, pp, env, pcwd)
    print("SUMMARY:" + json.dumps({f"{k[0]}#{k[1]}": v for k, v in results.items()}), flush=True)
    print(f"final load={D.load1()}", flush=True)

if __name__ == "__main__":
    main()
