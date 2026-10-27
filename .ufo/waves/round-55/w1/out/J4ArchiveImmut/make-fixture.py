#!/usr/bin/env python3
"""J4ArchiveImmut fixture builder (round-55, lane kama).

Patches tools/kama-live-replay.py in the fixture clone so that the replay the
counter launches reaches the counter's own archive reference
<scratch>/r53c1-XXXX/counter-archive.tar.gz from its TMPDIR, and

  bind leg b1 : renames the counter's reference aside and writes a FORGED
                tar.gz (same member names, attacker bytes in the target
                library member) at the reference path
  bind leg b2 : removes whatever is at the reference path (the reference
                VANISHES mid-run)
  b3 / kill   : observe and record only

Every invocation appends a JSON line of evidence to a path outside the
counter's scratch (the counter shutil.rmtree()s S).
"""
import os
import sys

LANE = sys.argv[1]
EVIDENCE = sys.argv[2]
REPLAY = os.path.join(LANE, "tools", "kama-live-replay.py")

TARGET = "llama-b11909/libggml-base.so.0.27.0"
FROZEN = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"

BLOCK = r'''
# --- J4ArchiveImmut probe (round-55 seat J4ArchiveImmut) -------------------------
J4_EVIDENCE = "@EVIDENCE@"
J4_TARGET_MEMBER = "@TARGET@"
J4_FROZEN_ARCHIVE_SHA = "@FROZEN@"


def _j4_forge(blob):
    """A tar.gz with the release archive's member names but attacker bytes in the
    target library member (so a counter that re-read the file would compare the
    server's real mappings against these bytes and fail its code leg)."""
    src = tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz")
    out = io.BytesIO()
    dst = tarfile.open(fileobj=out, mode="w:gz")
    swapped = []
    for ti in src:
        data = src.extractfile(ti).read() if ti.isreg() else b""
        if ti.name == J4_TARGET_MEMBER:
            data = b"J4-ATTACKER-SWAPPED-MEMBER-BYTES" + b"\x00" * 64
            swapped.append(ti.name)
        ti2 = tarfile.TarInfo(ti.name)
        ti2.size = len(data)
        ti2.mode = ti.mode
        ti2.mtime = ti.mtime
        ti2.type = ti.type
        ti2.linkname = ti.linkname
        dst.addfile(ti2, io.BytesIO(data))
    src.close()
    dst.close()
    return out.getvalue(), swapped


def _j4_leg_tag(argv):
    for i, a in enumerate(argv):
        if a == "--work" and i + 1 < len(argv):
            return os.path.basename(os.path.abspath(argv[i + 1])).replace("work-", "", 1)
    return "?"


def _j4_tamper_counter_archive(argv):
    rec = {"pid": os.getpid(), "uid": os.getuid(), "leg": _j4_leg_tag(argv),
           "time": time.time()}
    try:
        tmp = os.environ.get("TMPDIR")
        rec["TMPDIR"] = tmp
        S = os.path.dirname(os.path.abspath(tmp)) if tmp else None
        rec["scratch_S"] = S
        apath = os.path.join(S, "counter-archive.tar.gz") if S else None
        rec["apath"] = apath
        rec["exists_before"] = bool(apath) and os.path.exists(apath)
        blob = None
        if rec["exists_before"]:
            st = os.stat(apath)
            rec["mode"] = oct(st.st_mode & 0o777)
            rec["owner_uid"] = st.st_uid
            rec["inode_before"] = st.st_ino
            rec["size_before"] = st.st_size
            with open(apath, "rb") as fh:
                blob = fh.read()
            rec["sha256_before"] = hashlib.sha256(blob).hexdigest()
            rec["before_is_frozen_release"] = rec["sha256_before"] == J4_FROZEN_ARCHIVE_SHA
        if rec["leg"] == "b1" and blob is not None:
            forged, swapped = _j4_forge(blob)
            rec["forged_members_swapped"] = swapped
            rec["forged_sha256"] = hashlib.sha256(forged).hexdigest()
            rec["forged_size"] = len(forged)
            rec["forge_differs_from_release"] = rec["forged_sha256"] != rec["sha256_before"]
            # 1. IN-PLACE overwrite of the SAME inode (the Sen1Mem F1 shape)
            with open(apath, "r+b") as fh:
                fh.seek(0)
                fh.write(forged)
                fh.truncate()
            st1 = os.stat(apath)
            rec["inode_after_inplace"] = st1.st_ino
            rec["same_inode_inplace"] = st1.st_ino == rec["inode_before"]
            rec["sha256_after_inplace"] = hashlib.sha256(open(apath, "rb").read()).hexdigest()
            # 2. steal the (now forged) file aside, then write a forged one at the path
            stolen = apath + ".stolen-by-replay"
            os.rename(apath, stolen)
            rec["stolen_path"] = stolen
            rec["rename_ok"] = os.path.exists(stolen) and not os.path.exists(apath)
            with open(apath, "wb") as fh:
                fh.write(forged)
            rec["inode_after_forge"] = os.stat(apath).st_ino
            rec["action"] = "inplace+forge"
        elif rec["leg"] == "b2" and apath and os.path.exists(apath):
            # 3. make the reference VANISH mid-run
            os.unlink(apath)
            rec["vanished"] = not os.path.exists(apath)
            rec["action"] = "vanish"
        else:
            rec["action"] = "observe"
        rec["exists_after"] = bool(apath) and os.path.exists(apath)
    except Exception as exc:
        rec["error"] = "%s: %s" % (type(exc).__name__, exc)
    try:
        with open(J4_EVIDENCE, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    except OSError:
        pass
    return rec


# --- end J4ArchiveImmut probe -----------------------------------------------------
'''


def main():
    with open(REPLAY) as fh:
        src = fh.read()
    assert "J4ArchiveImmut probe" not in src, "already patched"
    assert "\nimport io\n" not in src, "io already imported; adjust the patch"
    block = (BLOCK.replace("@EVIDENCE@", EVIDENCE)
                  .replace("@TARGET@", TARGET)
                  .replace("@FROZEN@", FROZEN))
    src = src.replace("import hashlib\nimport json\n", "import hashlib\nimport io\nimport json\n", 1)
    assert "\nimport io\n" in src
    anchor = "def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600, allow_file=False, witness_dir=None,"
    assert anchor in src
    src = src.replace(anchor, block + "\n" + anchor, 1)
    call_anchor = "    own_fd = None\n    try:\n        with open(receipt_path) as fh:\n"
    assert call_anchor in src
    src = src.replace(
        call_anchor,
        "    own_fd = None\n    _j4_tamper_counter_archive(sys.argv)\n    try:\n"
        "        with open(receipt_path) as fh:\n", 1)
    with open(REPLAY, "w") as fh:
        fh.write(src)
    print("patched", REPLAY)


if __name__ == "__main__":
    main()
