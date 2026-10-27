#!/usr/bin/env python3
"""J3CopyDecoy lab: does a write-event watch on the member path distinguish an extracted
member from one overwritten by a byte-identical copy? Uses the replay's own code path
(tarfile.extractall(..., filter="data")) on a synthetic archive, then shutil.copyfile."""
import ctypes, json, os, shutil, struct, tarfile, tempfile, time

MASK = 0x8 | 0x80 | 0x100 | 0x4 | 0x2 | 0x200          # CLOSE_WRITE MOVED_TO CREATE ATTRIB MODIFY DELETE
NAMES = {0x2: "MODIFY", 0x4: "ATTRIB", 0x8: "CLOSE_WRITE", 0x80: "MOVED_TO",
         0x100: "CREATE", 0x200: "DELETE"}
libc = ctypes.CDLL("libc.so.6", use_errno=True)


def watch(path):
    fd = libc.inotify_init1(os.O_NONBLOCK)
    if fd < 0:
        raise OSError(ctypes.get_errno(), "inotify_init1")
    wd = libc.inotify_add_watch(fd, path.encode(), MASK)
    if wd < 0:
        raise OSError(ctypes.get_errno(), f"inotify_add_watch {path}")
    return fd


def drain(fd):
    out = []
    while True:
        try:
            buf = os.read(fd, 65536)
        except BlockingIOError:
            return out
        if not buf:
            return out
        off = 0
        while off < len(buf):
            _wd, mask, _cookie, ln = struct.unpack_from("iIII", buf, off)
            off += 16
            name = buf[off:off + ln].split(b"\0", 1)[0].decode("utf-8", "replace")
            off += ln
            if mask & MASK:
                out.append((name, [NAMES[b] for b in sorted(NAMES) if mask & b]))
    return out


def phases(root, host):
    d = os.path.join(root, "server", "llama-b11909")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(root, "src", "llama-b11909")
    os.makedirs(src)
    member = os.path.join(src, "llama-server")
    with open(member, "wb") as fh:                     # pretend bytes, 64 KiB
        fh.write(b"\x7fELF probe" + os.urandom(65536))
    arc = os.path.join(root, "srv.tar.gz")
    with tarfile.open(arc, "w:gz") as tf:
        tf.add(os.path.join(root, "src", "llama-b11909"), arcname="llama-b11909")
    hdr_mtime = int([m for m in tarfile.open(arc).getmembers()
                     if m.name == "llama-b11909/llama-server"][0].mtime)
    fd = watch(d)
    try:
        # phase 1: exactly what kama-live-replay.py extract() does
        with tarfile.open(arc) as tf:
            tf.extractall(os.path.join(root, "server"), filter="data")
        p1 = drain(fd)
        target = os.path.join(d, "llama-server")
        st1 = os.stat(target)
        # phase 2: exactly what the J3CopyDecoy probe does (byte-identical copy over it)
        shutil.copyfile(member, target)
        p2 = drain(fd)
        st2 = os.stat(target)
        # phase 3: a decoy that also forges the mtime back to the tar header
        os.utime(target, ns=(hdr_mtime * 10**9, hdr_mtime * 10**9))
        p3 = drain(fd)
        st3 = os.stat(target)
    finally:
        os.close(fd)
    return {"header_mtime_ns": hdr_mtime * 10**9,
            "phase1_extract": p1, "phase2_copy": p2, "phase3_utime": p3,
            "st1": {"mtime_ns": st1.st_mtime_ns, "ctime_ns": st1.st_ctime_ns, "inode": st1.st_ino},
            "st2": {"mtime_ns": st2.st_mtime_ns, "ctime_ns": st2.st_ctime_ns, "inode": st2.st_ino},
            "st3": {"mtime_ns": st3.st_mtime_ns, "ctime_ns": st3.st_ctime_ns, "inode": st3.st_ino}}


if __name__ == "__main__":
    root = tempfile.mkdtemp(prefix="j3-inotify-", dir=os.environ.get("TMPDIR") or None)
    try:
        rec = phases(root, None)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    rec["close_write"] = {"extract": sum(1 for n, m in rec["phase1_extract"] if "CLOSE_WRITE" in m and n == "llama-server"),
                          "copy": sum(1 for n, m in rec["phase2_copy"] if "CLOSE_WRITE" in m and n == "llama-server"),
                          "utime": sum(1 for n, m in rec["phase3_utime"] if "CLOSE_WRITE" in m and n == "llama-server")}
    rec["mtime_matches_header"] = {"extract": rec["st1"]["mtime_ns"] == rec["header_mtime_ns"],
                                   "copy": rec["st2"]["mtime_ns"] == rec["header_mtime_ns"],
                                   "utime-forged": rec["st3"]["mtime_ns"] == rec["header_mtime_ns"]}
    rec["ctime_after_extract"] = {"copy": rec["st2"]["ctime_ns"] - rec["st1"]["ctime_ns"],
                                  "utime-forged": rec["st3"]["ctime_ns"] - rec["st2"]["ctime_ns"]}
    print(json.dumps(rec, indent=1))
