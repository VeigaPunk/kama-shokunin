#!/usr/bin/env python3
"""Repeat / alias / mid-call rewrite differentials (base vs M1 ROUTER_PY)."""
import json, os, struct, subprocess, sys, time
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r93/RV01ProbeDiff")
FX = S / "fx"
RP = {v: (S / f"router-{v}.py").read_text() for v in ("base", "m1")}
EXE = str(FX / "valid-small.gguf")


def gguf(n_tensors, elems=1, with_data=False, pad_to=None, valid=False):
    if valid:
        head = b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 0)
        return head + b"\0" * ((pad_to or 24) - len(head))
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def body(lists):
    return json.dumps({"data": [{"id": "g", "status": {"args": a}} for a in lists]},
                      separators=(",", ":")).encode()


def run(ver, b, idx, timeout=120):
    p = S / f"b-{os.getpid()}.json"
    p.write_bytes(b)
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, "-c", RP[ver], str(p), "files", *idx],
                       capture_output=True, timeout=timeout, cwd=str(S))
    return r.stdout.decode(), round(time.monotonic() - t0, 2), r.returncode


def show(tag, b, idx, timeout=120):
    rb, tb, cb = run("base", b, idx, timeout)
    rm, tm, cm = run("m1", b, idx, timeout)
    st = "SAME" if rb == rm else "DIFF"
    print(f"{st}\t{tag}\tbase {tb}s rc={cb}\tm1 {tm}s rc={cm}")
    return rb, rm


slow = FX / "slow.gguf"
slow.write_bytes(gguf(150000))

print("== repeats of one slow invalid file (R01-R04 shape), ROUTER_PY output ==")
for n in (1, 2, 8, 9, 10, 16, 64):
    rb, rm = show(f"slow-x{n}", body([[EXE, "-m", str(slow)]] * n), [str(i) for i in range(n)])
    if rb != rm:
        d = [(i, rb.split("\n")[i], rm.split("\n")[i]) for i in range(n) if rb.split("\n")[i] != rm.split("\n")[i]]
        print(f"  first divergence {d[0][0]}: base {d[0][1]!r} vs m1 {d[0][2]!r}; {len(d)}/{n} differ")

print("\n== R05 shape: 33 alias strings of one slow file x64 ==")
aliases = [str(FX / "slow-link.gguf")] + [str(FX) + "/" + "./" * k + "slow.gguf" for k in range(32)]
if not (FX / "slow-link.gguf").exists():
    os.symlink(slow, FX / "slow-link.gguf")
rb, rm = show("slow-aliases-x64", body([[EXE, "-m", aliases[i % 33]] for i in range(64)]),
              [str(i) for i in range(64)])
print("  base distinct:", sorted(set(rb.split("\n")))[:4], " m1 distinct:", sorted(set(rm.split("\n")))[:4])

print("\n== R06 shape: -m ok --mmproj slow x64 ==")
okp = str(FX / "valid-0t.gguf")
rb, rm = show("slow-mmproj-x64", body([[EXE, "-m", okp, "--mmproj", str(slow)]] * 64),
              [str(i) for i in range(64)])
print("  base distinct:", sorted(set(rb.split("\n")))[:4], " m1 distinct:", sorted(set(rm.split("\n")))[:4])

print("\n== P02 shape: 63x slow then one distinct valid ==")
rb, rm = show("slow63-then-ok", body([[EXE, "-m", str(slow)]] * 63 + [[EXE, "-m", str(FX / 'valid-0t.gguf')]]),
              [str(i) for i in range(64)])
print("  last 3 base:", rb.split("\n")[-4:-1], " m1:", rm.split("\n")[-4:-1])

# ---- mid-call rewrite ----
print("\n== mid-call in-place rewrite of the SAME inode ==")
Y = FX / "yslow.gguf"
Y.write_bytes(gguf(350000))
t0 = time.monotonic(); run("base", body([[EXE, "-m", str(Y)]]), ["0"]); print("  yslow parse ~", round(time.monotonic() - t0, 2), "s each side incl startup")


def rewrite_test(tag, mutate):
    X = FX / "xfile.gguf"
    X.write_bytes(gguf(0, 1, True, pad_to=None) if False else b"MUTX" + b"\0" * 60)
    st0 = X.stat()
    b = body([[EXE, "-m", str(X)], [EXE, "-m", str(Y)], [EXE, "-m", str(X)]])
    outs = {}
    for ver in ("base", "m1"):
        X.write_bytes(b"MUTX" + b"\0" * 60)
        os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
        p = S / f"b-{ver}.json"
        p.write_bytes(b)
        t = time.monotonic()
        r = subprocess.Popen([sys.executable, "-c", RP[ver], str(p), "files", "0", "1", "2"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(S))
        time.sleep(0.15)                      # index 1 (yslow) is parsing now
        mutate(X, st0)
        out, err = r.communicate(timeout=120)
        outs[ver] = out.decode()
        print(f"  {tag} {ver}: {outs[ver].replace(chr(10), ' | ')}  ({round(time.monotonic()-t,2)}s)")
        assert X.exists() and X.is_file()
        X.write_bytes(b"MUTX" + b"\0" * 60)
        os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
    st = "SAME" if outs["base"] == outs["m1"] else "DIFF"
    print(f"  => {tag}: {st}")


def same_size_same_mtime(X, st0):
    X.write_bytes(gguf(0, 1, True, valid=True, pad_to=st0.st_size))   # valid GGUF, identical bytes-length
    os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))                # restore mtime exactly
    s = X.stat()
    print(f"     rewrite: size {s.st_size} (was {st0.st_size}) ino same={s.st_ino == st0.st_ino} "
          f"mtime_ns same={s.st_mtime_ns == st0.st_mtime_ns} ctime changed={s.st_ctime_ns != st0.st_ctime_ns}")


def same_size_new_mtime(X, st0):
    X.write_bytes(gguf(0, 1, True, valid=True, pad_to=st0.st_size))
    print(f"     rewrite: size same, mtime_ns changed={X.stat().st_mtime_ns != st0.st_mtime_ns}")


def diff_size_same_mtime(X, st0):
    X.write_bytes(gguf(0, 1, True, valid=True, pad_to=4096))
    os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
    print(f"     rewrite: size 4096 vs {st0.st_size}, mtime restored")


rewrite_test("same-size+same-mtime", same_size_same_mtime)
rewrite_test("same-size+new-mtime", same_size_new_mtime)
rewrite_test("diff-size+same-mtime", diff_size_same_mtime)

print("\n== replace by rename (new inode) between candidates ==")
X = FX / "x2.gguf"
X.write_bytes(b"MUTX" + b"\0" * 60)
st0 = X.stat()
b = body([[EXE, "-m", str(X)], [EXE, "-m", str(Y)], [EXE, "-m", str(X)]])
for ver in ("base", "m1"):
    p = S / f"b-{ver}.json"; p.write_bytes(b)
    r = subprocess.Popen([sys.executable, "-c", RP[ver], str(p), "files", "0", "1", "2"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(S))
    time.sleep(0.15)
    tmp = FX / "x2.tmp"
    tmp.write_bytes(gguf(0, 1, True, valid=True, pad_to=st0.st_size))
    os.replace(tmp, X)
    out, _ = r.communicate(timeout=120)
    print(f"  rename {ver}: {out.decode().replace(chr(10), ' | ')}")
    X.write_bytes(b"MUTX" + b"\0" * 60); os.utime(X, ns=(st0.st_atime_ns, st0.st_mtime_ns))
