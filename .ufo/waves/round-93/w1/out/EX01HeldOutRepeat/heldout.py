#!/usr/bin/env python3
"""EX01 held-out shapes for C1. Reuses stub/fixture code from round93-router-repeat.py."""
import argparse, hashlib, json, os, shutil, struct, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/home/vgpnk/Projects/shokunin/kama-shokunin/tools")
# import helpers by exec of counter module parts we need (avoid running main)
import importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round93-router-repeat.py")
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)

TENSORS = 150000
BASE = "5af794958b0fc08f574aa2e67650282269549b02"
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"
REPO = "/home/vgpnk/Projects/shokunin/kama-shokunin"

def git_show(rev, path="tools/kama-probe.sh"):
    p = subprocess.run(["git","-C",REPO,"show",f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0: raise SystemExit(f"git show {rev} failed")
    return p.stdout

def gguf_slow(n_tensors=TENSORS, elems=1, with_data=False):
    return c1.gguf(n_tensors, elems, with_data)

def run_probe(R, stub_port):
    return R.check(stub_port)

def cell(label, arg_lists, w, exe, probes, runs=2, budget=20.0):
    body = c1.router_body(arg_lists)
    routes = {"/v1/models": body, "/props": c1.PROPS}
    out = {}
    for name, data in probes.items():
        R = c1.Runner(Path(tempfile.mkdtemp(prefix=f"held-{name}-", dir=w)))
        R.install(data)
        times=[]; verdicts=[]
        for i in range(runs):
            with c1.Stub(routes) as st:
                rc, v, r, dt = R.check(st.port)
            times.append(dt); verdicts.append(f"{v}/{r}")
        out[name] = (verdicts, times)
        shutil.rmtree(R.work, ignore_errors=True)
    print(f"CELL {label} body={len(body)}B", flush=True)
    for name,(vs,ts) in out.items():
        print(f"  {name}: {' '.join(vs)} times={' '.join(f'{t:.2f}s' for t in ts)}", flush=True)
    return out, len(body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    a.out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="ex01-", dir=a.work)).resolve()
    fx = work/"fx"; fx.mkdir()
    bbytes = git_show(BASE); mbytes = git_show(M1)
    probes = {"base": bbytes, "M1": mbytes}
    print(f"load1={open('/proc/loadavg').read().split()[0]} base_sha={hashlib.sha256(bbytes).hexdigest()[:12]} M1_sha={hashlib.sha256(mbytes).hexdigest()[:12]}", flush=True)
    # fixtures
    slow = fx/"slow.gguf"; slow.write_bytes(gguf_slow())
    ok = fx/"ok.gguf"; ok.write_bytes(c1.gguf(1,32,True))
    ok2 = fx/"ok2.gguf"; ok2.write_bytes(c1.gguf(2,32,True))
    # slow valid: many tensors, data present. Use 150k tensors but with_data=True -> huge (150k*32 aligned = ~4.8MB ok)
    slowvalid = fx/"slowvalid.gguf"; slowvalid.write_bytes(c1.gguf(150000, 1, True))
    # distinct slow invalid copies: hardlink? No — task says DISTINCT copies: copy bytes to new files (distinct inode)
    exe = str(ok)
    s = str(slow)
    results = []
    def do(label, args, **kw):
        res, blen = cell(label, args, work, exe, probes, **kw)
        results.append({"label":label,"body_bytes":blen, **{k:{"verdicts":v[0],"times":v[1]} for k,v in res.items()}})
        return res

    # (a) distinct slow invalid copies N=2..256 — create N files, each entry names a different file
    # To keep disk/time sane, N up to 256: each slow.gguf is ~150k*~30B header ≈ 4.5MB? check size
    print(f"slow size={slow.stat().st_size} slowvalid size={slowvalid.stat().st_size} ok size={ok.stat().st_size}", flush=True)
    distinct_files = []
    NMAX = 256
    for i in range(NMAX):
        p = fx/f"slow-{i:04d}.gguf"
        # copy (distinct inode)
        shutil.copyfile(slow, p)
        distinct_files.append(str(p))
    for N in [2,8,16,32,64,128,256]:
        do(f"A-distinct-x{N}", [[exe,"-m",distinct_files[i % len(distinct_files)]] for i in range(N)])

    # (b) one slow invalid listed 4096 and 16384 times (body under 4MiB check happens in router_body)
    for N in [4096, 16384]:
        try:
            do(f"B-repeat-x{N}", [[exe,"-m",s]]*N)
        except Exception as e:
            print(f"  B-repeat-x{N}: router_body raised: {e}", flush=True)

    # (c) hard link and bind mixed with one valid file
    hard = fx/"slow-hardlink.gguf"
    try: os.link(slow, hard)
    except OSError as e: print(f"hardlink failed: {e}")
    bind_ok = True
    # bind mount needs root; try, else skip
    bind = fx/"slow-bind.gguf"
    import subprocess as sp
    r = sp.run(["mount","--bind",str(slow),str(bind)], capture_output=True)
    bind_ok = (r.returncode==0)
    print(f"bind ok={bind_ok} rc={r.returncode}", flush=True)
    hard_str = str(hard) if hard.exists() else s
    mixed = []
    for i in range(63):
        if i % 3 == 0: mixed.append([exe,"-m",hard_str])
        elif bind_ok and i % 3 == 1: mixed.append([exe,"-m",str(bind)])
        else: mixed.append([exe,"-m",s])
    mixed.append([exe,"-m",str(ok)])
    do("C-hardlink-bind-mixed-OK", mixed)
    if bind_ok: sp.run(["umount",str(bind)], capture_output=True)

    # (d) slow VALID GGUF repeated 2048 -> MODEL_OK
    do("D-slowvalid-x2048", [[exe,"-m",str(slowvalid)]]*2048)

    # (e) repeated slow file is --mmproj of distinct valid models
    # distinct valid models: ok, ok2, and create ok3..ok16
    valids = [str(ok), str(ok2)]
    for i in range(3, 17):
        p = fx/f"ok{i}.gguf"; p.write_bytes(c1.gguf(i,32,True)); valids.append(str(p))
    args_e = [[valids[i % len(valids)], "-m", valids[i % len(valids)], "--mmproj", s] for i in range(64)]
    do("E-mmproj-slow-distinct-valid-x64", args_e)
    # also without mmproj: distinct valid models with -m pointing to slow? no, that would be invalid; E is mmproj variant

    # write results json
    (a.out/"results.json").write_text(json.dumps({"results":results}, indent=1))
    print(f"load1_end={open('/proc/loadavg').read().split()[0]}", flush=True)
    shutil.rmtree(work, ignore_errors=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
