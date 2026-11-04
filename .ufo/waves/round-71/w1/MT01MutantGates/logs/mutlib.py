"""Mutant builder + detector runner for MT01 (round 71). Writes only under S."""
import hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

S = pathlib.Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
TMP = S / "tmp"; TMP.mkdir(parents=True, exist_ok=True)

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def build(base_text, patches, out_path, tag):
    """patches: list of (old,new[,count]). Applies exactly; asserts each matched."""
    txt = base_text
    for p in patches:
        old, new = p[0], p[1]
        cnt = p[2] if len(p) > 2 else 1
        n = txt.count(old)
        if n != cnt:
            raise SystemExit(f"{tag}: patch expects {cnt} occurrences of {old[:60]!r}, found {n}")
        txt = txt.replace(old, new)
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(txt)
    compile(txt, str(out), "exec")  # syntax check
    return sha(out)

def run(argv, cwd, tag, timeout=300, env_extra=None):
    env = dict(os.environ)
    env["TMPDIR"] = str(TMP)
    env.pop("PYTHONPATH", None)
    if env_extra: env.update(env_extra)
    t0 = time.time()
    try:
        p = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, errors="replace",
                           timeout=timeout, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    rec = {"tag": tag, "argv": argv, "cwd": str(cwd), "exit": rc,
           "stdout": out, "stderr": err, "secs": round(time.time() - t0, 2)}
    with open(S / "logs" / "detectors.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

def tail(rec, n=1):
    lines = [l for l in rec["stdout"].strip().splitlines() if l.strip()]
    return lines[-n:] if lines else []
