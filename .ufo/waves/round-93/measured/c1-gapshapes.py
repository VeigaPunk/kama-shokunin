#!/usr/bin/env python3
"""Round-93 L1 receipt (not a claim counter): the wave-1 CR01/MT01 gap shapes graded by the probe at BASE and at the
repaired C1 revision, 2 runs each. H1 64 entries through 33 hard links to slow.gguf (want router-model-invalid);
G1 64 entries through 16 symlinks (want router-model-invalid); D1 63x slow.gguf + a valid ok2.gguf padded to the
same size and given the same mtime (want MODEL_OK autoload); E1 one entry naming ok.gguf as -m and -md (want MODEL_OK
autoload); P2048 2047x slow + one valid last (want MODEL_OK autoload). Usage: c1-gapshapes.py <scratch>"""
import importlib.util, os, subprocess, sys, tempfile
from pathlib import Path
spec = importlib.util.spec_from_file_location("rr", "tools/round93-router-repeat.py")
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
REV = {"BASE": rr.BASE, "M1b": "b37657998858b6300fc8fbbbebb7e256239bf0f8"}
work = Path(tempfile.mkdtemp(dir=sys.argv[1])); R = rr.Runner(work)
slow, ok, ok2 = work / "slow.gguf", work / "ok.gguf", work / "ok2.gguf"
slow.write_bytes(rr.gguf(rr.TENSORS, 1, False)); ok.write_bytes(rr.gguf(1, 32, True))
okb = rr.gguf(2, 32, True); ok2.write_bytes(okb + b"\0" * (slow.stat().st_size - len(okb)))
st = slow.stat(); os.utime(ok2, ns=(st.st_atime_ns, st.st_mtime_ns))
links = []
for i in range(33):
    p = work / f"hl{i:02d}.gguf"; os.link(slow, p); links.append(str(p))
syms = []
for i in range(16):
    p = work / f"sl{i:02d}.gguf"; os.symlink(slow, p); syms.append(str(p))
e = str(ok); s = str(slow)
cells = [("H1-hardlinks-33x64", [[e, "-m", links[i % 33]] for i in range(64)], "MODEL_UNLOADED/router-model-invalid"),
         ("G1-symlinks-16x64", [[e, "-m", syms[i % 16]] for i in range(64)], "MODEL_UNLOADED/router-model-invalid"),
         ("D1-same-size-mtime-pair", [[e, "-m", s]] * 63 + [[e, "-m", str(ok2)]], "MODEL_OK/router-unloaded-autoload"),
         ("E1-one-entry-two-flags", [[e, "-m", e, "-md", e]], "MODEL_OK/router-unloaded-autoload"),
         ("P2048-valid-last", [[e, "-m", s]] * 2047 + [[e, "-m", str(ok2)]], "MODEL_OK/router-unloaded-autoload")]
show = lambda r: subprocess.run(["git", "show", f"{r}:tools/kama-probe.sh"], capture_output=True, check=True).stdout
print(f"# load1={open('/proc/loadavg').read().split()[0]} ok2 size==slow size: {ok2.stat().st_size == st.st_size}, mtime equal: {ok2.stat().st_mtime_ns == st.st_mtime_ns}")
for cid, args, want in cells:
    body = rr.router_body(args)
    for name, rev in REV.items():
        R.install(show(rev))
        with rr.Stub({"/v1/models": body, "/props": rr.PROPS}) as stb:
            res = [R.check(stb.port) for _ in range(2)]
        got = " ".join(f"{v}/{r}/{dt:.2f}s" for _, v, r, dt in res)
        right = all(f"{v}/{r}" == want for _, v, r, _ in res)
        print(f"C1_GAP {cid} rev={name} want={want} right={int(right)} {got}", flush=True)
