#!/usr/bin/env python3
"""V3: discriminating shape - 8 DISTINCT slow invalid files, empty models-dir (no valid entry), wildcard probe under load. True C1 mechanism."""
import hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import driver as D

LANE, SCRATCH = D.LANE, D.SCRATCH

def setup():
    models = SCRATCH / "models3"; models.mkdir(exist_ok=True)
    empty = SCRATCH / "emptydir"; empty.mkdir(exist_ok=True)
    slow_bytes = D.gguf_slow(D.TENSORS)
    paths = []
    for i in range(8):
        p = models / f"s{i}.gguf"
        # distinct inode + slight size difference (pad tail) to defeat SEEN dedup
        p.write_bytes(slow_bytes + b"\0" * (i * 32))
        paths.append(p)
    lines = []
    for i, p in enumerate(paths):
        lines += [f"[s{i:02d}]", f"model = {p}", ""]
    preset = SCRATCH / "presets3.ini"; preset.write_text("\n".join(lines))
    print(f"distinct slow files=8 bytes_each={slow_bytes.__len__()}..{len(slow_bytes)+224}", flush=True)
    return models, empty, preset, paths

def one(label, probe_path, empty, preset, env, pcwd):
    cwd = SCRATCH / "router-cwd3"; cwd.mkdir(exist_ok=True)
    log = SCRATCH / f"router3-{time.time_ns()}.log"
    port = D.start_router(empty, preset, cwd, log, str(SCRATCH))
    try:
        ents = D.entries(port)
        print(f"[{label}] router port={port} listed={sorted(ents)}", flush=True)
        assert all(v.get("value") == "unloaded" for v in ents.values()), ents
        n = int(subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip() or "32")
        D.start_burners(n)
        try:
            l = D.load1()
            pv, pr, rc, dt, _ = D.run_probe(probe_path, port, "*", env, pcwd)
            print(f"[{label}] WB probe-load target=* burners={n} load={l} => {pv}/{pr} rc={rc} wall={dt:.2f}s", flush=True)
            pv1, pr1, rc1, dt1, _ = D.run_probe(probe_path, port, "s07", env, pcwd)
            print(f"[{label}] WB probe-load target=s07 load={D.load1()} => {pv1}/{pr1} rc={rc1} wall={dt1:.2f}s", flush=True)
        finally:
            D.stop_burners()
        ov = D.oracle(port, "s07")
        print(f"[{label}] WB oracle target=s07 load={D.load1()} => {ov}", flush=True)
        return (pv, pr, dt, pv1, pr1, dt1, ov)
    finally:
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
    models, empty, preset, paths = setup()
    pcwd = SCRATCH / "probe-cwd"; pcwd.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(pcwd))
    probes = {}
    for label, rev in (("BASE", D.BASE), ("M1", D.M1)):
        full = subprocess.run(["git", "-C", str(LANE), "rev-parse", "--verify", rev + "^{commit}"],
                              capture_output=True, text=True, check=True).stdout.strip()
        data = subprocess.run(["git", "-C", str(LANE), "show", f"{full}:tools/kama-probe.sh"],
                              capture_output=True, check=True).stdout
        pp = SCRATCH / f"probe3-{label}.sh"; pp.write_bytes(data); pp.chmod(0o755)
        probes[label] = (full, pp)
        print(f"[{label}] rev={full} probe_sha256={hashlib.sha256(data).hexdigest()}", flush=True)
    for rep in range(2):
        for label in ("BASE", "M1"):
            full, pp = probes[label]
            r = one(label, pp, empty, preset, env, pcwd)
            print(f"[{label}#{rep}] RESULT wildcard={r[0]}/{r[1]} wall={r[2]:.2f}s s07={r[3]}/{r[4]} wall={r[5]:.2f}s oracle={r[6]}", flush=True)
    print(f"final load={D.load1()}", flush=True)

if __name__ == "__main__":
    main()
