#!/usr/bin/env python3
"""EX02LiveRouterBudget: real llama-server b12177 router, >=12 entries naming one slow invalid GGUF + one valid; probe at B vs M1 under nproc burners; oracle POST."""
import hashlib, json, os, signal, socket, struct, subprocess, sys, time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r94/EX02LiveRouterBudget")
SERVER = Path.home() / ".local/opt/llama-b12177/llama-server"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
BASE = "e6f1dcce"
M1 = "a27656a454b1a2364f8b6e55f42fbca8c2e86ee4"
TENSORS = 150000

CHILDREN = []
BURNERS = []

def kill_all(*_a):
    for p in list(CHILDREN):
        try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try: p.kill()
            except Exception: pass
    for p in list(BURNERS):
        try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try: p.kill()
            except Exception: pass
    CHILDREN.clear(); BURNERS.clear()
    sys.exit(0)

def gguf_slow(n_tensors: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, off))
        off += 32  # (1*4+31)//32*32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + b"\0" * 16  # truncated data, same as counter slow.gguf

def gguf_ok() -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 0)]
    out.append(struct.pack("<Q", 8) + b"t0000000" + struct.pack("<IQIQ", 1, 32, 0, 0))
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + b"\0" * 128

def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def load1():
    try: return open("/proc/loadavg").read().split()[0]
    except OSError: return "?"

def http(method, port, path, body=None, timeout=60):
    import urllib.request, urllib.error
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data,
                                 headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

def entries(port):
    code, txt = http("GET", port, "/v1/models", timeout=5)
    assert code == 200, f"GET /v1/models -> {code} {txt[:200]}"
    return {e["id"]: (e.get("status") or {}) for e in json.loads(txt).get("data", [])}

def start_router(models_dir: Path, preset: Path, cwd: Path, log: Path, owned: str) -> int:
    port = free_port()
    p = subprocess.Popen([str(SERVER), "--host", "127.0.0.1", "--port", str(port),
                          "--models-max", "4", "--models-dir", str(models_dir),
                          "--models-preset", str(preset)],
                         stdout=log.open("w"), stderr=subprocess.STDOUT, cwd=cwd,
                         start_new_session=True)
    CHILDREN.append(p)
    for _ in range(120):
        if p.poll() is not None:
            raise RuntimeError(f"router exited rc={p.returncode} log={log}: {log.read_text(errors='replace')[:800]}")
        try:
            ents = entries(port); break
        except Exception:
            time.sleep(0.25)
    else:
        raise RuntimeError("router never answered /v1/models")
    for mid, st in ents.items():
        a = st.get("args") or []
        paths = [a[i+1] for i, x in enumerate(a[:-1]) if x in ("--model", "-m")]
        if paths and owned not in str(paths):
            raise RuntimeError(f"entry {mid!r} not owned: {paths}")
    return port

def run_probe(probe_path: Path, port: int, expect: str, env: dict, cwd: Path):
    t0 = time.monotonic()
    p = subprocess.run(["bash", str(probe_path), "check", "--port", str(port), "--expect", expect,
                        "--timeout", "60", "--connect-timeout", "5", "--json"],
                       capture_output=True, text=True, timeout=180, env=env, cwd=cwd)
    dt = time.monotonic() - t0
    try:
        doc = json.loads(p.stdout)
        row = doc["rows"][0]
        return row["verdict"], row.get("reason", "?"), p.returncode, dt, p.stdout.strip()[:300]
    except Exception as e:
        return f"UNPARSED(rc={p.returncode})", str(e), p.returncode, dt, (p.stdout[:300] + " | stderr: " + p.stderr[:300])

def oracle(port, mid):
    code, txt = http("POST", port, "/v1/chat/completions",
                     {"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 2}, timeout=120)
    if code == 200: return "MODEL_OK(200)"
    if code == 500 and "failed to load" in txt: return "MODEL_UNLOADED(500 failed-to-load)"
    if code == 400 and "not loaded" in txt: return "MODEL_UNLOADED(400 not-loaded)"
    return f"INCONCLUSIVE http={code} {txt[:160]!r}"

def start_burners(n):
    for _ in range(n):
        p = subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        BURNERS.append(p)
    time.sleep(2.0)

def stop_burners():
    for p in list(BURNERS):
        try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            try: p.kill()
            except Exception: pass
        try: p.wait(timeout=5)
        except Exception: pass
    BURNERS.clear()

def measure(rev_label, rev_full, probe_path, models_dir, preset, work, port, target, env, pcwd):
    # natural load probe
    t_nat, l_nat = time.monotonic(), load1()
    pv, pr, rc, dt, raw = run_probe(probe_path, port, target, env, pcwd)
    print(f"[{rev_label}] PROBE target={target} load={l_nat} => verdict={pv} reason={pr} rc={rc} wall={dt:.2f}s raw={raw}", flush=True)
    # oracle (may trigger autoload attempt; valid model would load, invalid fails)
    t_or, l_or = time.monotonic(), load1()
    ov = oracle(port, target)
    print(f"[{rev_label}] ORACLE target={target} load={l_or} => {ov} wall={time.monotonic()-t_or:.2f}s", flush=True)
    # under load
    n = int(subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip() or "32")
    start_burners(n)
    try:
        l_load = load1()
        pv2, pr2, rc2, dt2, raw2 = run_probe(probe_path, port, target, env, pcwd)
        print(f"[{rev_label}] PROBE-LOAD target={target} burners={n} load={l_load} => verdict={pv2} reason={pr2} rc={rc2} wall={dt2:.2f}s raw={raw2}", flush=True)
        # wildcard
        pv3, pr3, rc3, dt3, raw3 = run_probe(probe_path, port, "*", env, pcwd)
        print(f"[{rev_label}] PROBE-LOAD target=* burners={n} load={load1()} => verdict={pv3} reason={pr3} rc={rc3} wall={dt3:.2f}s raw={raw3}", flush=True)
    finally:
        stop_burners()
    return

def main():
    signal.signal(signal.SIGTERM, kill_all); signal.signal(signal.SIGINT, kill_all)
    out = SCRATCH / "run"
    out.mkdir(parents=True, exist_ok=True)
    # fixtures
    models = SCRATCH / "models"; models.mkdir(exist_ok=True)
    slow = models / "slow.gguf"; slow.write_bytes(gguf_slow(TENSORS))
    good = models / "good.gguf"; good.write_bytes(gguf_ok())
    # also copy real fixture valid model for the valid entry (router must list it; oracle may try to load the tiny synthetic one, keep tiny)
    print(f"slow.gguf bytes={slow.stat().st_size} sha256={hashlib.sha256(slow.read_bytes()).hexdigest()[:16]}", flush=True)
    print(f"good.gguf bytes={good.stat().st_size} sha256={hashlib.sha256(good.read_bytes()).hexdigest()[:16]}", flush=True)
    # preset: 12 invalid entries all naming slow.gguf + 1 valid entry naming good.gguf
    lines = []
    for i in range(12):
        lines.append(f"[bad{i:02d}]")
        lines.append(f"model = {slow}")
        lines.append("")
    lines.append("[valid1]")
    lines.append(f"model = {good}")
    preset = SCRATCH / "presets.ini"; preset.write_text("\n".join(lines))
    print(f"preset entries=13 (12x slow invalid + 1 valid) lines={len(lines)}", flush=True)
    # probes at two revs
    pcwd = SCRATCH / "probe-cwd"; pcwd.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(pcwd))
    probes = {}
    for label, rev in (("BASE", BASE), ("M1", M1)):
        full = subprocess.run(["git", "-C", str(LANE), "rev-parse", "--verify", rev + "^{commit}"],
                              capture_output=True, text=True, check=True).stdout.strip()
        data = subprocess.run(["git", "-C", str(LANE), "show", f"{full}:tools/kama-probe.sh"],
                              capture_output=True, check=True).stdout
        pp = SCRATCH / f"probe-{label}.sh"; pp.write_bytes(data); pp.chmod(0o755)
        probes[label] = (full, pp)
        print(f"[{label}] rev={full} probe_sha256={hashlib.sha256(data).hexdigest()}", flush=True)
    # router child (autoread preset presumably autoload on by default)
    router_cwd = SCRATCH / "router-cwd"; router_cwd.mkdir(exist_ok=True)
    port = start_router(models, preset, router_cwd, SCRATCH / "router.log", str(SCRATCH))
    print(f"router port={port} load={load1()}", flush=True)
    try:
        ents = entries(port)
        print(f"listed={len(ents)} ids={sorted(ents)[:16]}", flush=True)
        for mid in sorted(ents):
            print(f"  {mid} status={ents[mid].get('value')} args={ents[mid].get('args')}", flush=True)
        # per-rev measurements on same router, target one invalid entry + wildcard
        for label in ("BASE", "M1"):
            full, pp = probes[label]
            measure(label, full, pp, models, preset, SCRATCH, port, "bad00", env, pcwd)
        # valid entry probe sanity (probe should say MODEL_OK? not the claim; report only)
        for label in ("BASE", "M1"):
            full, pp = probes[label]
            pv, pr, rc, dt, raw = run_probe(pp, port, "valid1", env, pcwd)
            print(f"[{label}] PROBE target=valid1 load={load1()} => verdict={pv} reason={pr} rc={rc} wall={dt:.2f}s raw={raw}", flush=True)
        print(f"final load={load1()} nproc burners stopped", flush=True)
    finally:
        kill_all()

if __name__ == "__main__":
    main()
