#!/usr/bin/env python3
"""Edge inputs + false-green direction + bind attempt."""
import json, os, subprocess, sys, time
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r93/RV01ProbeDiff")
FX = S / "fx"
RP = {v: (S / f"router-{v}.py").read_text() for v in ("base", "m1")}
EXE = str(FX / "valid-small.gguf")


def body(lists):
    return json.dumps({"data": [{"id": "g", "status": {"args": a}} for a in lists]},
                      separators=(",", ":")).encode()


def run(ver, b, idx):
    p = S / f"e-{os.getpid()}.json"
    p.write_bytes(b)
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, "-c", RP[ver], str(p), "files", *idx],
                       capture_output=True, timeout=180, cwd=str(S))
    return r.stdout.decode(errors="replace"), round(time.monotonic() - t0, 2), r.returncode


def show(tag, b, idx):
    rb, tb, cb = run("base", b, idx)
    rm, tm, cm = run("m1", b, idx)
    print(f"{'SAME' if rb == rm else 'DIFF'}\t{tag}\tbase {tb}s rc={cb}\tm1 {tm}s rc={cm}")
    if rb != rm:
        print(f"  base={rb!r}\n  m1__={rm!r}")
    else:
        print(f"  both={rb!r}")
    return rb, rm


print("== hostile path strings ==")
(FX / "a\nb.gguf").write_bytes(b"x")
(FX / "a\tb.gguf").write_bytes(b"x")
weird = [
    ("nul-byte", str(FX / "valid-small.gguf") + "\u0000x"),
    ("lone-surrogate", str(FX) + "/\udcff.gguf"),
    ("newline-in-name", str(FX / "a\nb.gguf")),
    ("tab-in-name", str(FX / "a\tb.gguf")),
    ("path-4097", "/" + "a" * 4096),
    ("path-5000-components", "/" + "/".join(["d"] * 5000)),
    ("dot", "."),
    ("dotdot", ".."),
    ("root", "/"),
    ("proc-self-fd", "/proc/self/fd/0"),
    ("dev-fd-0", "/dev/fd/0"),
    ("dev-stdin", "/dev/stdin"),
]
for name, p in weird:
    show(name, body([[EXE, "-m", p]]), ["0"])

print("\n== false-green direction: valid file rewritten IN PLACE to invalid, size+mtime preserved ==")
Y = FX / "yslow.gguf"
if not Y.exists():
    sys.exit("need yslow")
X = FX / "g.gguf"
valid = b"GGUF" + (3).to_bytes(4, "little") + (0).to_bytes(8, "little") + (0).to_bytes(8, "little") + b"\0" * 40
invalid = b"MUTX" + b"\0" * 60
assert len(valid) == len(invalid) == 64
b = body([[EXE, "-m", str(X)], [EXE, "-m", str(Y)], [EXE, "-m", str(X)]])
outs = {}
for ver in ("base", "m1"):
    X.write_bytes(valid)
    st0 = X.stat()
    os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
    p = S / f"g-{ver}.json"
    p.write_bytes(b)
    r = subprocess.Popen([sys.executable, "-c", RP[ver], str(p), "files", "0", "1", "2"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(S))
    time.sleep(0.15)
    X.write_bytes(invalid)
    os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
    s = X.stat()
    same = (s.st_size == st0.st_size and s.st_mtime_ns == st0.st_mtime_ns)
    out, _ = r.communicate(timeout=180)
    outs[ver] = out.decode()
    print(f"  {ver}: {outs[ver].replace(chr(10),' | ')}  key-stable={same}")
print("  => " + ("SAME" if outs["base"] == outs["m1"] else "DIFF (false green: m1 keeps the stale ok)"))

print("\n== bind-mount of ./ (unshare attempt) ==")
p = subprocess.run(["unshare", "-rm", "--propagation", "private", "bash", "-c",
                    f"mount --bind {FX} /mnt && echo BIND_OK && ls /mnt | head -1"], capture_output=True)
print("  unshare rc=", p.returncode, p.stdout.decode().strip()[:120], p.stderr.decode().strip()[:160])

print("\n== distinct slow files (disclosed limit): 3 distinct slow files x3 each ==")
files = []
for i in range(3):
    f = FX / f"slow{i}.gguf"
    if not f.exists():
        import shutil; shutil.copy(FX / "slow.gguf", f)
    files.append(str(f))
lists = [[EXE, "-m", files[i]] for i in range(3)]
show("3-distinct-slow", body(lists), ["0", "1", "2"])
lists = [[EXE, "-m", f] for f in files for _ in range(3)]
show("3-distinct-slow-x3", body(lists), [str(i) for i in range(9)])
