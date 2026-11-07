#!/usr/bin/env python3
"""t4: direct gguf_state comparison, 2048-candidate budget, NO_OPEN-vs-memo under bind, rewrite determinism."""
import json, os, subprocess, sys, time
from pathlib import Path
from collections import Counter

S = Path("/fast/scratch/hyaku/kama-r93/RV01ProbeDiff").resolve()
FX = S / "fx"
RP = {v: (S / f"router-{v}.py").read_text() for v in ("base", "m1")}
EXE = str(FX / "valid-small.gguf")
SRC = {}
for v in ("base", "m1"):
    t = RP[v]; SRC[v] = t[: t.index("\ntry:\n    doc = json.load(open(sys.argv[1]))")]


def body(lists):
    return json.dumps({"data": [{"id": "g", "status": {"args": a}} for a in lists]},
                      separators=(",", ":")).encode()


PART = sys.argv[1] if len(sys.argv) > 1 else "all"

if PART in ("all", "direct"):
    print("== direct gguf_state / gguf_parse, one file per call ==")
    cases = [("missing-abs", "absent/nope.gguf"), ("dir", "empty"), ("fifo", "fifo"), ("devnull", "/dev/null"),
             ("devzero", "/dev/zero"), ("proc-version", "/proc/version"), ("symlink-proc", "link-proc"),
             ("unreadable", "unreadable.gguf"), ("unreadable-dir", "secret/in.gguf"),
             ("valid-small", "valid-small.gguf"), ("valid-0t", "valid-0t.gguf"), ("valid-real", "model.gguf"),
             ("trunc", "trunc.gguf"), ("badmagic", "badmagic.gguf"), ("plain", "plain.gguf"),
             ("ver1", "ver1.gguf"), ("ver4", "ver4.gguf"), ("ver0", "ver0.gguf"),
             ("nkv-huge", "nkv-huge.gguf"), ("nt-huge", "nt-huge.gguf"), ("unk-tt", "unk-tt.gguf"),
             ("socket", "sock"), ("link-broken", "link-broken"), ("loop", "loop-a"), ("link-dir", "link-dir"),
             ("link-valid", "link-valid"), ("dotdot", "sub/../valid-small.gguf"), ("root", "/"),
             ("dot", "."), ("proc-cmdline", "/proc/self/cmdline"),
             ("sys", "/sys/kernel/mm/transparent_hugepage/enabled"), ("zeros", "zeros.gguf"),
             ("short4", "short4.gguf"), ("hdronly", "hdronly.gguf")]
    (FX / "zeros.gguf").write_bytes(b"\0" * 100000)
    (FX / "short4.gguf").write_bytes(b"GGU")
    (FX / "hdronly.gguf").write_bytes(b"GGUF" + (3).to_bytes(4, "little") + (0).to_bytes(8, "little") + (0).to_bytes(8, "little"))
    bad = 0
    for name, rel in cases:
        p = rel if rel.startswith("/") else str(FX / rel)
        got = {}
        for v in ("base", "m1"):
            fn = "gguf_state" if v == "base" else "gguf_parse"
            r = subprocess.run([sys.executable, "-c", SRC[v] + f"\nimport sys; print(repr({fn}(sys.argv[1])))\n", p],
                               capture_output=True)
            got[v] = r.stdout.decode().strip() or ("EXC:" + r.stderr.decode().strip().splitlines()[-1])
        bad += got["base"] != got["m1"]
        print(f"{'SAME' if got['base']==got['m1'] else 'DIFF'}\t{name:16s} base={got['base']:12s} m1={got['m1']}")
    print("DIFFS:", bad)

if PART in ("all", "budget"):
    print("\n== 2048-candidate listings through the probe's own `timeout 8` ==")
    for tag, lists in (("2048x slow", [[EXE, "-m", str(FX / "slow.gguf")]] * 2048),
                       ("2048x missing", [[EXE, "-m", str(FX / "absent/m.gguf")]] * 2048),
                       ("2048x valid0t", [[EXE, "-m", str(FX / "valid-0t.gguf")]] * 2048),
                       ("2048x badmagic", [[EXE, "-m", str(FX / "badmagic.gguf")]] * 2048)):
        p = S / "big.json"; p.write_bytes(body(lists))
        idx = [str(i) for i in range(len(lists))]
        for v in ("base", "m1"):
            t0 = time.monotonic()
            r = subprocess.run(["timeout", "8", sys.executable, "-c", RP[v], str(p), "files", *idx],
                               capture_output=True)
            dt = time.monotonic() - t0
            lines = [l for l in r.stdout.decode().split("\n") if l]
            st = dict(Counter(l.split("\t")[1] for l in lines))
            print(f"  {tag:15s} {v}: rc={r.returncode} {dt:.2f}s lines={len(lines)}/2048 states={st}")

if PART in ("all", "rewrite"):
    X = FX / "r.gguf"
    Y = str(FX / "yslow.gguf")
    valid = b"GGUF" + (3).to_bytes(4, "little") + (0).to_bytes(8, "little") + (0).to_bytes(8, "little") + b"\0" * 40
    invalid = b"MUTX" + b"\0" * 60
    print("\n== mid-call in-place rewrite of one inode, 3 reps ==")
    for init, tgt, restore, tag in ((invalid, valid, True, "invalid->valid same size+mtime"),
                                    (valid, invalid, True, "valid->invalid same size+mtime (false-green dir)"),
                                    (valid, invalid, False, "valid->invalid same size, mtime changes")):
        res = {}
        for v in ("base", "m1"):
            outs = []
            for _ in range(3):
                X.write_bytes(init); st0 = X.stat()
                os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
                p = S / f"r-{v}.json"
                p.write_bytes(body([[EXE, "-m", str(X)], [EXE, "-m", Y], [EXE, "-m", str(X)]]))
                pr = subprocess.Popen([sys.executable, "-c", RP[v], str(p), "files", "0", "1", "2"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(0.15)
                X.write_bytes(tgt)
                if restore:
                    os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
                o, _ = pr.communicate(timeout=120)
                outs.append(o.decode().replace("\n", " | "))
            res[v] = outs
        print(f"  {tag}: stable={len(set(res['base']))==1 and len(set(res['m1']))==1}")
        print(f"     base {res['base']}")
        print(f"     m1   {res['m1']}")
