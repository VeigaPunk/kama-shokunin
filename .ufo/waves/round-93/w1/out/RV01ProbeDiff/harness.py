#!/usr/bin/env python3
"""RV01ProbeDiff: differential harness base-vs-M1 ROUTER_PY over single/multi candidate bodies."""
import json, os, socket, stat, struct, subprocess, sys, time
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r93/RV01ProbeDiff")
FX = S / "fx"
RP = {v: (S / f"router-{v}.py").read_text() for v in ("base", "m1")}
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"


def gguf(n_tensors=0, elems=1, with_data=True, ver=3, tt=0):
    out = [b"GGUF", struct.pack("<I", ver), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, tt, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)


def build():
    if FX.exists():
        subprocess.run(["chmod", "-R", "u+rwX", str(FX)])
        subprocess.run(["rm", "-rf", str(FX)])
    FX.mkdir(parents=True)
    (FX / "empty").mkdir()
    (FX / "sub").mkdir()
    os.mkfifo(FX / "fifo")
    s = socket.socket(socket.AF_UNIX); s.bind(str(FX / "sock")); s.close()
    (FX / "valid-small.gguf").write_bytes(gguf(1, 32, True))
    (FX / "valid-0t.gguf").write_bytes(gguf(0, 1, True))
    (FX / "badmagic.gguf").write_bytes(b"XXXX" + b"\0" * 60)
    (FX / "ver1.gguf").write_bytes(b"GGUF" + struct.pack("<I", 1) + b"\0" * 60)
    (FX / "ver4.gguf").write_bytes(b"GGUF" + struct.pack("<I", 4) + b"\0" * 60)
    (FX / "ver0.gguf").write_bytes(b"GGUF" + struct.pack("<I", 0) + b"\0" * 60)
    (FX / "nkv-huge.gguf").write_bytes(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 0, 200000) + b"\0" * 64)
    (FX / "nt-huge.gguf").write_bytes(b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 2000000, 0) + b"\0" * 64)
    (FX / "unk-tt.gguf").write_bytes(gguf(1, 32, True, tt=59999))
    (FX / "trunc.gguf").write_bytes(MODEL.read_bytes()[: MODEL.stat().st_size // 2])
    (FX / "plain.gguf").write_bytes(b"not a model at all\n" * 4)
    (FX / "unreadable.gguf").write_bytes(gguf(1, 32, True))
    os.chmod(FX / "unreadable.gguf", 0)
    (FX / "secret").mkdir()
    (FX / "secret" / "in.gguf").write_bytes(gguf(0, 1, True))
    os.chmod(FX / "secret", 0)
    os.symlink("/proc/version", FX / "link-proc")
    os.symlink(FX / "valid-small.gguf", FX / "link-valid")
    os.symlink(FX / "nope-target", FX / "link-broken")
    os.symlink(FX / "empty", FX / "link-dir")
    os.symlink("loop-b", FX / "loop-a"); os.symlink("loop-a", FX / "loop-b")
    (FX / "sub" / "realfile.gguf").write_bytes(gguf(0, 1, True))
    os.symlink(FX / "sub", FX / "sublink")
    os.link(FX / "valid-small.gguf", FX / "hardlink.gguf")
    import shutil; shutil.copy(MODEL, FX / "model.gguf")


def body(args_lists):
    return json.dumps({"object": "list", "data": [
        {"id": "good", "status": {"value": "unloaded", "args": a}} for a in args_lists]},
        separators=(",", ":")).encode()


EXE = str(FX / "valid-small.gguf")


def run(ver, b, idx):
    body = S / f"body-{os.getpid()}-{time.monotonic_ns()}.json"
    body.write_bytes(b)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-c", RP[ver], str(body), "files", *idx],
                       capture_output=True, timeout=120, cwd=str(S))
    dt = time.monotonic() - t0
    body.unlink()
    return p.stdout.decode(), p.stderr.decode(), p.returncode, dt


def cmp(name, b, idx):
    rb, eb, cb, tb = run("base", b, idx)
    rm, em, cm, tm = run("m1", b, idx)
    ok = (rb == rm) and (cb == cm)
    print(f"{'SAME' if ok else 'DIFF'}\t{name}\tbase_rc={cb}\tm1_rc={cm}\tt={tb:.2f}/{tm:.2f}")
    if not ok:
        print(f"  base_out={rb!r}\n  m1__out={rm!r}\n  base_err={eb[-400:]!r}\n  m1__err={em[-400:]!r}")
    return ok, rb, rm


def main():
    build()
    f = lambda n: str(FX / n)
    cases = [
        ("missing-abs", [EXE, "-m", f("absent/nope.gguf")]),
        ("missing-rel", [EXE, "-m", "relx.gguf"]),
        ("dir", [EXE, "-m", f("empty")]),
        ("dir-slash", [EXE, "-m", f("empty") + "/"]),
        ("fifo", [EXE, "-m", f("fifo")]),
        ("devnull", [EXE, "-m", "/dev/null"]),
        ("devzero", [EXE, "-m", "/dev/zero"]),
        ("proc-version", [EXE, "-m", "/proc/version"]),
        ("proc-cmdline", [EXE, "-m", "/proc/self/cmdline"]),
        ("sys-path", [EXE, "-m", "/sys/kernel/mm/transparent_hugepage/enabled"]),
        ("symlink-into-proc", [EXE, "-m", f("link-proc")]),
        ("unreadable", [EXE, "-m", f("unreadable.gguf")]),
        ("unreadable-dir", [EXE, "-m", f("secret/in.gguf")]),
        ("valid-small", [EXE, "-m", f("valid-small.gguf")]),
        ("valid-0t", [EXE, "-m", f("valid-0t.gguf")]),
        ("valid-real-model", [EXE, "-m", f("model.gguf")]),
        ("truncated", [EXE, "-m", f("trunc.gguf")]),
        ("badmagic", [EXE, "-m", f("badmagic.gguf")]),
        ("plain-text", [EXE, "-m", f("plain.gguf")]),
        ("version1", [EXE, "-m", f("ver1.gguf")]),
        ("version4", [EXE, "-m", f("ver4.gguf")]),
        ("version0", [EXE, "-m", f("ver0.gguf")]),
        ("n_kv-huge", [EXE, "-m", f("nkv-huge.gguf")]),
        ("n_tensors-huge", [EXE, "-m", f("nt-huge.gguf")]),
        ("unknown-tensor-type", [EXE, "-m", f("unk-tt.gguf")]),
        ("socket", [EXE, "-m", f("sock")]),
        ("link-broken", [EXE, "-m", f("link-broken")]),
        ("loop", [EXE, "-m", f("loop-a")]),
        ("link-dir", [EXE, "-m", f("link-dir")]),
        ("link-valid", [EXE, "-m", f("link-valid")]),
        ("trailing-slash-file", [EXE, "-m", f("valid-small.gguf") + "/"]),
        ("dotdot", [EXE, "-m", f("sub/../valid-small.gguf")]),
        ("args0-relative", ["valid-small.gguf", "-m", f("valid-small.gguf")]),
        ("args0-missing", [str(FX / "nope-exe"), "-m", f("valid-small.gguf")]),
        ("args0-dir", [f("empty"), "-m", f("valid-small.gguf")]),
        ("args0-devnull", ["/dev/null", "-m", f("valid-small.gguf")]),
        ("args-empty", []),
        ("args-notlist", "nope"),
        ("flag-no-value", [EXE, "-m"]),
        ("model-eq", [EXE, "--model=" + f("valid-small.gguf")]),
        ("model-eq-empty", [EXE, "--model="]),
        ("mm-form", [EXE, "-m", f("valid-0t.gguf"), "--mmproj", f("deepseek")]),
        ("md-form", [EXE, "-m", f("valid-0t.gguf"), "-md", f("deepseek2")]),
        ("mixed-missing-then-invalid", [EXE, "-m", f("absent/x.gguf"), "-mm", f("badmagic.gguf")]),
        ("mixed-invalid-then-missing", [EXE, "-m", f("badmagic.gguf"), "-mm", f("absent/x.gguf")]),
        ("mixed-valid-then-bad", [EXE, "-m", f("valid-0t.gguf"), "-mm", f("badmagic.gguf")]),
    ]
    allsame = True
    print("== single-candidate ==")
    for name, a in cases:
        ok, _, _ = cmp(name, body([a]), ["0"])
        allsame &= ok
    print("\n== args shape / index handling ==")
    for name, doc, idx in [
        ("entry-not-dict", {"data": [42]}, ["0"]),
        ("status-not-dict", {"data": [{"id": "x", "status": "nope"}]}, ["0"]),
        ("status-no-args", {"data": [{"id": "x", "status": {"value": "unloaded"}}]}, ["0"]),
        ("args-ints", {"data": [{"id": "x", "status": {"args": [1, 2, 3]}}]}, ["0"]),
        ("index-out-of-range", {"data": []}, ["0"]),
        ("index-neg", {"data": [{"id": "x", "status": {"args": [EXE, "-m", f("valid-0t.gguf")]}}]}, ["-1"]),
        ("index-nonint", {"data": [{"id": "x", "status": {"args": [EXE, "-m", f("valid-0t.gguf")]}}]}, ["zz"]),
    ]:
        ok, _, _ = cmp(name, json.dumps(doc, separators=(",", ":")).encode(), idx)
        allsame &= ok

    print("\n== multi-candidate: identity aliases (state must be right per file) ==")
    hb = body([[EXE, "-m", f("valid-small.gguf")], [EXE, "-m", f("hardlink.gguf")],
               [EXE, "-m", f("link-valid")], [EXE, "-m", f("sub/../valid-small.gguf")],
               [EXE, "-m", f("sublink/../valid-small.gguf")]])
    ok, rb, _ = cmp("aliases-valid-x5", hb, ["0", "1", "2", "3", "4"]); allsame &= ok
    print("  base:", rb.replace("\n", " | "))
    ib = body([[EXE, "-m", f("nkv-huge.gguf")], [EXE, "-m", f("nt-huge.gguf")],
               [EXE, "-m", f("unk-tt.gguf")], [EXE, "-m", f("badmagic.gguf")]])
    ok, rb, _ = cmp("distinct-invalid-x4", ib, ["0", "1", "2", "3"]); allsame &= ok
    print("  base:", rb.replace("\n", " | "))
    sb = body([[EXE, "-m", f("valid-0t.gguf")], [EXE, "-m", f("absent/m.gguf")],
               [EXE, "-m", f("badmagic.gguf")], [EXE, "-m", f("absent/m.gguf")]])
    ok, rb, _ = cmp("missing-invalid-repeats", sb, ["0", "1", "2", "3"]); allsame &= ok
    print("  base:", rb.replace("\n", " | "))
    twob = body([[EXE, "-m", f("badmagic.gguf"), "--mmproj", f("badmagic.gguf")]])
    ok, rb, _ = cmp("two-flags-one-file", twob, ["0"]); allsame &= ok
    print("  base:", rb.replace("\n", " | "))
    print(f"\nALL_SINGLE_AND_ALIAS_SAME={allsame}")


main()
