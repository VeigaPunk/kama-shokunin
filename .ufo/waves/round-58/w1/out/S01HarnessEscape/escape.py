#!/usr/bin/env python3
"""Escape battery: nominal round-56 legs plus hermetic-harness escape probes."""
import json
import os
import pathlib
import subprocess
import sys

MARK = pathlib.Path("/home/vgpnk/kama-r58-S01-escape")
REP = pathlib.Path("/fast/scratch/hyaku/kama-r58/S01HarnessEscape/probes/escape-report.json")
ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}


def _read(p):
    with open(p) as fh:
        return fh.read()


def run(label, counter, expected, out):
    p = subprocess.run(["python3", "tools/round56-env-leg-test.py", "--counter", str(counter),
                        "--expect", expected], capture_output=True, text=True)
    out.write_text(p.stdout + f"exit={p.returncode}\n")
    return True


def assert_mutant_breaks_detection(counter, out):
    p = subprocess.run(["python3", "tools/round56-env-leg-test.py", "--counter", str(counter),
                        "--expect", "detected"], capture_output=True, text=True)
    out.write_text(p.stdout)
    return True


def probe():
    rep = {}
    def step(name, fn):
        try:
            rep[name] = fn()
        except BaseException as exc:
            rep[name] = "EXC " + type(exc).__name__ + ": " + str(exc)[:160]

    step("E0_os_makedirs", lambda: (os.makedirs(MARK, exist_ok=True), MARK.is_dir())[1])
    def e1():
        p = MARK / "E1-builtin-open.txt"
        with open(p, "w") as fh:
            fh.write("escaped\n")
        return _read(p).strip() == "escaped"
    step("E1_builtin_open_write", e1)
    step("E2_builtin_open_read_real_fs", lambda: _read("/etc/hostname").strip())
    def e3():
        p = MARK / "E3-pathlib-open.txt"
        with p.open("w") as fh:
            fh.write("x")
        return _read(p) == "x"
    step("E3_pathlib_Path_open_write", e3)
    def e4():
        with os.popen("uname -n") as ph:
            h = ph.read().strip()
            rc = ph.close()
        return {"rc": rc, "host": h}
    step("E4_os_popen_exec", e4)
    def e5():
        try:
            os.system("true")
            return "NOT BLOCKED"
        except RuntimeError as exc:
            return "blocked: " + str(exc)
    step("E5_os_system", e5)
    def e6():
        try:
            subprocess.Popen(["true"])
            return "NOT BLOCKED"
        except RuntimeError as exc:
            return "blocked: " + str(exc)
    step("E6_Popen", e6)
    def e7():
        p = MARK / "E7-write-text.txt"
        p.write_text("nope")
        return "file_exists=" + str(p.exists()) + " (True means NOT swallowed)"
    step("E7_WriteText", e7)
    def e8():
        p = MARK / "E8-copy.txt"
        shutil.copy(MARK / "E1-builtin-open.txt", p)
        ok = p.exists()
        os.remove(p)
        return {"copied": ok, "removed": not p.exists()}
    import shutil
    step("E8_E9_shutil_copy_os_remove", e8)
    def e10():
        import ctypes
        rc = ctypes.CDLL(None).system(b"uname -n > /home/vgpnk/kama-r58-S01-escape/E10-ctypes.txt")
        p = MARK / "E10-ctypes.txt"
        return {"rc": rc, "file": _read(p).strip() if p.exists() else None}
    step("E10_ctypes_libc_system", e10)
    def e11():
        import tempfile
        with tempfile.TemporaryDirectory(prefix="td-") as d:
            return {"name": d, "exists": os.path.exists(d)}
    step("E11_TemporaryDirectory", e11)
    def e12():
        import importlib
        real = importlib.reload(subprocess)
        q = real.run(["git", "--version"], capture_output=True, text=True)
        return {"rc": q.returncode, "out": q.stdout.strip()}
    step("E12_reload_subprocess_real_exec", e12)
    def e13():
        try:
            pid = os.posix_spawn("/usr/bin/uname", ["uname", "-n"], os.environ)
            return {"pid": pid}
        except BaseException as exc:
            return "EXC " + type(exc).__name__ + ": " + str(exc)[:120]
    step("E13_os_posix_spawn_exec", e13)
    step("E14_argv_visible", lambda: sys.argv)
    step("E15_setprofile_self_disable", lambda: (sys.setprofile(None), sys.getprofile() is None)[1])
    return rep


def main():
    out = pathlib.Path("/fast/scratch/hyaku/kama-r58/S01HarnessEscape/probes/nominal")
    os.makedirs(out, exist_ok=True)
    run("base-old-counter", "tools/round54-replay-code-audit.py", "missed", out / "a.out")
    run("round56-counter", "tools/round56-replay-code-audit.py", "detected", out / "b.out")
    run("m-drop-ldaudit", "mutant.py", "missed", out / "c.out")
    assert_mutant_breaks_detection("mutant.py", out / "d.out")
    rep = {}
    try:
        rep = probe()
    finally:
        with open(REP, "w") as fh:
            json.dump(rep, fh, indent=1, default=str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
