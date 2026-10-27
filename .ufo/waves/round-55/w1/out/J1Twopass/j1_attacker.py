#!/usr/bin/env python3
"""J1Twopass out-of-process same-uid attacker.

A separate process (same uid as the counter and the held server) that rewrites a mapped
library's r-x range IN PLACE: the same path, the same inode, opened O_RDWR, one byte
written with pwrite(2) and later restored with pwrite(2). It picks the byte itself by
parsing the ELF program headers of the library (the PT_LOAD segment with PF_X), so it does
not need any capability from the counter.

Usage:
  j1_attacker.py <library> <trigger-file> <result-file> [--hold-ms N] [--delay-ms N]

It waits for <trigger-file> to appear (polled every 0.2 ms), acts, and records:
  t_trigger_seen, t_write, t_restore, file_offset, byte_before, byte_after,
  inode_before, inode_after, path_sha256_before/after.
"""
import hashlib
import json
import os
import struct
import sys
import time


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def exec_segment(path):
    """(file_offset, length) of the PT_LOAD segment carrying PF_X."""
    with open(path, "rb") as fh:
        head = fh.read(64)
        if head[:4] != b"\x7fELF":
            raise SystemExit("not an ELF")
        if head[4] == 2:
            (e_phoff,) = struct.unpack_from("<Q", head, 0x20)
            (e_phentsize, e_phnum) = struct.unpack_from("<HH", head, 0x36)
        else:
            (e_phoff,) = struct.unpack_from("<I", head, 0x1C)
            (e_phentsize, e_phnum) = struct.unpack_from("<HH", head, 0x2A)
        best = None
        for i in range(e_phnum):
            fh.seek(e_phoff + i * e_phentsize)
            ph = fh.read(e_phentsize)
            p_type = int.from_bytes(ph[0:4], "little")
            p_flags = ph[4]
            p_offset = int.from_bytes(ph[8:16], "little")
            p_filesz = int.from_bytes(ph[32:40], "little")
            if p_type == 1 and (p_flags & 1):  # PT_LOAD, PF_X
                if best is None or p_filesz > best[1]:
                    best = (p_offset, p_filesz)
        return best


def main():
    lib = sys.argv[1]
    trigger = sys.argv[2]
    result = sys.argv[3]
    hold_ms = 5.0
    delay_ms = 0.0
    file_offset = None
    args = sys.argv[4:]
    for i, a in enumerate(args):
        if a == "--hold-ms":
            hold_ms = float(args[i + 1])
        if a == "--delay-ms":
            delay_ms = float(args[i + 1])
        if a == "--file-offset":
            file_offset = int(args[i + 1])

    off, size = exec_segment(lib)
    if file_offset is None:
        byte_off = off + size // 2
    else:
        byte_off = file_offset
    ev = {"library": lib, "exec_segment": [off, size], "byte_offset": byte_off,
          "byte_offset_source": "explicit" if file_offset is not None else "elf_pt_load_pf_x"}

    t_wait = time.monotonic()
    while not os.path.exists(trigger):
        time.sleep(0.0002)
    ev["t_trigger_seen"] = time.monotonic()
    if delay_ms:
        time.sleep(delay_ms / 1000.0)

    st0 = os.stat(lib)
    with open(lib, "rb") as fh:
        fh.seek(byte_off)
        before = fh.read(1)
    fd = os.open(lib, os.O_RDWR)
    try:
        ev["inode_before"] = str(st0.st_ino)
        ev["byte_before"] = before.hex()
        t_w = time.monotonic()
        os.pwrite(fd, bytes([before[0] ^ 0xFF]), byte_off)
        ev["t_write"] = time.monotonic()
        time.sleep(hold_ms / 1000.0)
        os.pwrite(fd, before, byte_off)
        ev["t_restore"] = time.monotonic()
    finally:
        os.close(fd)
    st1 = os.stat(lib)
    ev["inode_after"] = str(st1.st_ino)
    ev["same_inode"] = st0.st_ino == st1.st_ino
    ev["byte_after"] = before.hex()
    ev["hold_ms"] = round((ev["t_restore"] - ev["t_write"]) * 1000.0, 3)
    ev["latency_ms_trigger_to_write"] = round((ev["t_write"] - ev["t_trigger_seen"]) * 1000.0, 3)
    ev["wait_ms"] = round((ev["t_trigger_seen"] - t_wait) * 1000.0, 3)
    ev["path_sha256_after"] = sha256_file(lib)
    with open(result, "w") as fh:
        json.dump(ev, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
