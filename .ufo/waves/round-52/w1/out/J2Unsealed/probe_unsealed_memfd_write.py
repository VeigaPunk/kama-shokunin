#!/usr/bin/env python3
"""Round 52 J2Unsealed: can the running image of an exec'd memfd be written while the
exec'd process is alive - and does F_SEAL_WRITE add anything beyond exec's deny-write?

The build's C1 predicate rests on F_SEAL_WRITE|SHRINK|GROW|SEAL (seals 15). The ablation
(sealed_member skips F_ADD_SEALS) leaves the image a plain memfd, still /memfd:, still
nlink 0, still the frozen digest - only F_GET_SEALS differs. This probe measures what that
difference buys, with every outcome reported, nothing asserted.

Cases (payload /bin/sleep, copied bytes, exec'd through /proc/<parent>/fd/<n> with
pass_fds and argv[0]=name, the way tools/kama-llamacpp-live.py execs the --server-fd):
  U*  unsealed memfd, child running
  S*  sealed memfd (F_ADD_SEALS 15 issued before exec), child running
  D*  regular file on disk, opened O_RDWR BEFORE exec, child running (the ETXTBSY analogue)

  identity       /proc/<child>/exe link, nlink, st_dev:st_ino, F_GET_SEALS
  held-fd write  write(2) on a descriptor opened before the exec
  pwrite+readback pwrite 4 bytes at offset 0 on that descriptor, then pread to show the
                 running image's own bytes changed
  held-fd fitruncate shrink / grow
  open-exe       open(/proc/<child>/exe, O_RDWR) then write
  open-self-fd   open(/proc/self/fd/<n>, O_WRONLY) then write
  seal-late      F_ADD_SEALS 15 after exec
  after-exit     write(2) on the held descriptor once the child is gone (control)
Nothing listens on any port; the only writes are inside a scratch dir under TMPDIR.
"""
from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

F_ADD_SEALS, F_GET_SEALS = 1033, 1034
SEALS_ALL = 15
PAYLOAD = "/bin/sleep"
HOLD = 3.0


def why(exc):
    if isinstance(exc, OSError):
        return f"{type(exc).__name__}:{exc.errno}:{exc.strerror}"
    return f"{type(exc).__name__}:{exc}"


def fill(fd, data):
    off = 0
    while off < len(data):
        off += os.write(fd, data[off:])


def start_child(fd):
    exe = f"/proc/{os.getpid()}/fd/{fd}"
    p = subprocess.Popen([os.path.basename(PAYLOAD), str(HOLD)], executable=exe,
                         pass_fds=(fd,), stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return p, exe


def wait_running(p):
    deadline = time.time() + 2.0
    while time.time() < deadline:
        try:
            link = os.readlink(f"/proc/{p.pid}/exe")
        except OSError:
            link = None
        if link and (link.startswith("/memfd:") or link.endswith("sleep-copy") or link.startswith("/")):
            if p.poll() is None:
                return link
        if p.poll() is not None:
            return f"exited-rc{p.returncode}"
        time.sleep(0.02)
    return "no-running-image-in-2s"


def attempt(label, fn):
    try:
        return {"case": label, "result": "SUCCESS", "detail": fn()}
    except BaseException as exc:  # noqa: BLE001 - every outcome is data here
        return {"case": label, "result": "ERROR", "detail": why(exc)}


def _open_then_write(path, mode="r+b"):
    with open(path, mode, buffering=0) as fh:
        return f"opened; wrote {fh.write(b'Z')} byte(s)"


def reopen_and_write(path):
    """open O_RDWR then write one byte - the path-only attacker's attempt."""
    fd = os.open(path, os.O_RDWR)
    try:
        return f"opened; wrote {os.write(fd, b'Z')} byte(s)"
    finally:
        os.close(fd)


def run(tag, fd, size, first_bytes):
    child, exe = start_child(fd)
    out = []
    try:
        link = wait_running(child)
        st = os.fstat(fd)
        out.append({"case": f"{tag}:identity", "result": link,
                    "detail": {"nlink": st.st_nlink, "dev_ino": "%02x:%02x:%s" % (
                        os.major(st.st_dev), os.minor(st.st_dev), st.st_ino),
                        "child_pid": child.pid, "exec_link": exe}})
        out.append(attempt(f"{tag}:F_GET_SEALS", lambda: fcntl.fcntl(fd, F_GET_SEALS)))
        out.append(attempt(f"{tag}:held-fd write(2)", lambda: os.write(fd, b"X")))

        def corrupt():
            n = os.pwrite(fd, b"\x00\x00\x00\x00", 0)
            back = os.pread(fd, 4, 0)
            return f"pwrite {n} byte(s) at offset 0; pread back {back.hex()}; first 4 bytes were {first_bytes[:4].hex()}"
        out.append(attempt(f"{tag}:held-fd pwrite(0)+readback", corrupt))
        out.append(attempt(f"{tag}:held-fd ftruncate(shrink)", lambda: (os.ftruncate(fd, size - 1), "shrunk")[1]))
        out.append(attempt(f"{tag}:held-fd ftruncate(grow)", lambda: (os.ftruncate(fd, size + 1), "grown")[1]))
        out.append(attempt(f"{tag}:open(/proc/<child>/exe,O_RDWR)+write",
                           lambda: reopen_and_write(f"/proc/{child.pid}/exe")))
        out.append(attempt(f"{tag}:open(/proc/self/fd/<n>,O_WRONLY)+write",
                           lambda: _open_then_write(f"/proc/self/fd/{fd}", "r+b")))
        out.append(attempt(f"{tag}:seal-late F_ADD_SEALS(15)", lambda: fcntl.fcntl(fd, F_ADD_SEALS, SEALS_ALL)))
    finally:
        try:
            child.kill()
        except OSError:
            pass
        child.wait(timeout=5)
    return out


def after_exit_control(first_bytes):
    """Control: once the exec'd child is gone, ETXTBSY no longer applies and the same held
    descriptor writes again - so the deny-write guard, unlike a seal, is lifetime-bound."""
    fd = os.memfd_create("j2unsealed-after-exit", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    fill(fd, first_bytes)
    child, _exe = start_child(fd)
    link = wait_running(child)
    child.kill()
    child.wait(timeout=5)
    rows = [{"case": "after-exit:identity while running", "result": link, "detail": "child then killed"}]
    rows.append(attempt("after-exit:held-fd write(2) once child is gone", lambda: os.write(fd, b"Y")))
    rows.append(attempt("after-exit:held-fd ftruncate(shrink) once child is gone",
                        lambda: (os.ftruncate(fd, len(first_bytes) - 1), "shrunk")[1]))
    rows.append(attempt("after-exit:F_GET_SEALS", lambda: fcntl.fcntl(fd, F_GET_SEALS)))
    os.close(fd)
    return rows


def memfd_case(sealed, first_bytes):
    tag = "sealed-memfd" if sealed else "unsealed-memfd"
    fd = os.memfd_create("j2unsealed-" + tag, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    fill(fd, first_bytes + b"")
    # fill() leaves the offset at EOF; reset it so offset-0 reads mean the header
    os.lseek(fd, 0, os.SEEK_SET)
    if sealed:
        fcntl.fcntl(fd, F_ADD_SEALS, SEALS_ALL)
    size = os.fstat(fd).st_size
    try:
        return run(tag, fd, size, first_bytes)
    finally:
        os.close(fd)


def disk_case(scratch, first_bytes):
    """The regular-file analogue, measured both ways: exec while holding an O_RDWR fd (which
    memfd allows), and the path-only write against a running on-disk image."""
    path = os.path.join(scratch, "sleep-copy")
    with open(path, "wb") as fh:
        fh.write(first_bytes)
    os.chmod(path, 0o755)
    out = []
    fd = os.open(path, os.O_RDWR)
    try:
        try:
            p = subprocess.Popen([path, str(HOLD)], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out.append({"case": "on-disk-file:exec with held O_RDWR fd", "result": "SUCCESS",
                        "detail": f"pid {p.pid}"})
            p.kill()
            p.wait(timeout=5)
        except OSError as exc:
            out.append({"case": "on-disk-file:exec with held O_RDWR fd", "result": "ERROR",
                        "detail": why(exc)})
    finally:
        os.close(fd)
    p = subprocess.Popen([path, str(HOLD)], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.2)
        out.append({"case": "on-disk-file:identity", "result": os.readlink(f"/proc/{p.pid}/exe"),
                    "detail": path})
        out.append(attempt("on-disk-file:open(path,O_RDWR)+write on running image",
                           lambda: reopen_and_write(path)))
        out.append(attempt("on-disk-file:open(path,O_RDONLY)+F_GET_SEALS",
                           lambda: _open_ro_seals(path)))
    finally:
        p.kill()
        p.wait(timeout=5)
    return out


def _open_ro_seals(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        return fcntl.fcntl(fd, F_GET_SEALS)
    finally:
        os.close(fd)


def main():
    scratch = tempfile.mkdtemp(prefix="j2unsealed-")
    first_bytes = open(PAYLOAD, "rb").read()
    try:
        rows = (memfd_case(False, first_bytes) + memfd_case(True, first_bytes)
                + after_exit_control(first_bytes) + disk_case(scratch, first_bytes))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(json.dumps({"python": sys.version.split()[0], "payload": PAYLOAD,
                      "payload_sha256_prefix": __import__("hashlib").sha256(first_bytes).hexdigest()[:16],
                      "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
