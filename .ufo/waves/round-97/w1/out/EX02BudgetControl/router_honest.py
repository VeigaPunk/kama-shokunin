import json, os, stat, struct, sys

QSIZES = {0: (1, 4), 1: (1, 2), 2: (32, 18), 3: (32, 20), 6: (32, 22), 7: (32, 24), 8: (32, 34),
          9: (32, 36), 10: (256, 84), 11: (256, 110), 12: (256, 144), 13: (256, 176),
          14: (256, 210), 15: (256, 292), 16: (256, 66), 17: (256, 74), 18: (256, 98),
          19: (256, 50), 20: (32, 18), 21: (256, 110), 22: (256, 82), 23: (256, 136),
          24: (1, 1), 25: (1, 2), 26: (1, 4), 27: (1, 8), 28: (1, 8), 29: (256, 56),
          30: (1, 2), 34: (256, 54), 35: (256, 66), 39: (32, 17), 40: (64, 36),
          41: (128, 18), 42: (64, 18), 43: (1, 1)}
SCALAR = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, 1_000_000, 512 * 1024 ** 2
# Work bound per file: a hostile or odd header becomes "undecidable" (no verdict change),
# never a stall (r89 SN01 F1).
# Round 95 (C1; r94 closure SC02 F2, MT01 NOTE-3): the wall clock is GONE from the decision.
# Rounds 93-94 bounded the parse with a clock (one shared 4 s call deadline, then a 15 s
# per-file slice); either way a candidate's verdict depended on how loaded the host was, so
# the same bytes graded `invalid` on an idle box and `-` (undecided -> loadable) under load.
# Work is what must be bounded, and it is bounded deterministically: MAX_STEPS counts the
# parser's read/seek steps and MAX_META caps the header position in bytes, so a hostile file
# ends `-` after a fixed amount of work whatever the CPU contention. The pass-level limit is
# derived from the candidate count in `router_file_states` (see the shell wrapper), not from
# a constant. Disclosed, unchanged: a file whose declared tensor count exceeds MAX_TENSORS,
# or that needs more than MAX_STEPS, is still `-` (undecidable -> loadable, round-89 rule).
# The binding ceiling is `5 + nd` steps per tensor header: name u64+skip 2, nd u32 1, one
# u64 dim per rank (`nd`), tensor type+offset 2 = 5 + nd. The preamble costs 4 steps, so
# MAX_STEPS = 5 000 000 admits (5 000 000 - 4) // (5 + nd) tensor headers: 833,332 at nd=1,
# 714,285 at nd=2, 624,999 at nd=3, 555,555 at nd=4 (S620; round-97 C1/C3). A constant
# 6 steps/header is only the nd=1 case and misstates every rank-2+ file (round-96 closure
# routed defect 1, CR02 B2-B5). The old 1 000 000 sentence (the MAX_TENSORS constant) was
# never the binding ceiling (round-95 amendment 4, SC02 F1). KV and string-array work also
# charges steps, so the effective tensor ceiling is slightly lower.
MAX_STEPS = 5_000_000  # Round 96 (SC02 F1): a constant-6 budget made a 700 000-tensor
# file decode as undecidable -> loadable at 4 000 000; at 5 000 000 the same nd=1 file
# parses to a decision (invariant: every disclosed ceiling is derived from this value and
# the rank, never named independently)
MAX_STEP_BYTES = MAX_STEPS  # one need() call per bounded read/seek; kept for readers
PATH_FLAGS = ("-m", "--model", "-mm", "--mmproj", "-md", "--model-draft")
NO_OPEN = ("/proc/", "/sys/", "/dev/")


class Bad(Exception):
    pass


class Unknown(Exception):
    pass


# Round 93 (C1; r92 wave-1 SC02 F6): one regular file is parsed once per call, whatever path
# string names it (identity = device, inode, size, mtime, ctime). Every candidate shares one
# deadline, so a listing that repeated one slow invalid file spent the budget on copies and left the
# later candidates undecided, i.e. loadable: the verdict flipped to MODEL_OK with the repeat count.
# ctime is in the key because utime() can restore mtime after an in-place rewrite but not ctime
# (r93 wave-1 RV01 DEFECT-1: a same-size rewrite with mtime restored was served the stale state).
SEEN = {}


def gguf_state(path):
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return gguf_parse(path)
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    if key not in SEEN:
        SEEN[key] = gguf_parse(path)
    return SEEN[key]


def gguf_parse(path):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "-"
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return "invalid"
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError:
        return "-"
    try:
        fst = os.fstat(fd)
    except OSError:
        os.close(fd)
        return "-"
    if not stat.S_ISREG(fst.st_mode):
        os.close(fd)
        return "invalid"
    size = fst.st_size
    f = os.fdopen(fd, "rb")
    steps = [0]
    with f:
        def need(n):
            steps[0] += 1
            if steps[0] > MAX_STEPS:
                raise Unknown()
            pos = f.tell()
            if pos > MAX_META:
                raise Unknown()
            if n < 0 or pos + n > size:
                raise Bad()

        def rd(n):
            need(n)
            b = f.read(n)
            if len(b) != n:
                raise Bad()
            return b

        def skip(n):
            need(n)
            f.seek(n, 1)
        u32 = lambda: struct.unpack("<I", rd(4))[0]
        u64 = lambda: struct.unpack("<Q", rd(8))[0]

        def skip_value(t, depth=0):
            if t in SCALAR:
                skip(SCALAR[t])
            elif t == 8:
                skip(u64())
            elif t == 9:
                if depth > 8:
                    raise Unknown()
                et, n = u32(), u64()
                if n > MAX_ARR:
                    raise Unknown()
                if et in SCALAR:
                    skip(SCALAR[et] * n)
                elif et == 8:
                    skip_strings(n)
                else:
                    for _ in range(n):
                        skip_value(et, depth + 1)
            else:
                raise Bad()

        def skip_strings(n):
            # n length-prefixed strings, parsed from 1 MiB chunks (a tokenizer vocab holds
            # 10^5 entries; per-element reads made a live check 4x slower, r89 EX02)
            base, buf, off = f.tell(), b"", 0
            if base + 8 * n > size:
                raise Bad()
            unpack = struct.Struct("<Q").unpack_from
            # Round 95 (C1; wave-1 RV01 DEFECT-2): one step per STRING ELEMENT, not one per 64.
            # The bulk credit priced a 49M-element array at 766 014 steps while it cost 8 s of CPU,
            # so MAX_STEPS did not bound the work and the derived pass limit was unsound. Every
            # element now costs a step, so the budget is a function of the bytes alone.
            for _ in range(n):
                steps[0] += 1
                if steps[0] > MAX_STEPS:
                    raise Unknown()
                if off + 8 > len(buf):
                    base += off
                    f.seek(base)
                    buf, off = f.read(1 << 20), 0
                    if len(buf) < 8:
                        raise Bad()
                off += 8 + unpack(buf, off)[0]
                if base + off > size:
                    raise Bad()
                if base + off > MAX_META:
                    raise Unknown()
            f.seek(base + off)
        try:
            if rd(4) != b"GGUF":
                return "invalid"
            ver = u32()
            if ver == 1 or ver > 3 or (ver & 0xFFFF) == 0:
                return "invalid"
            n_tensors, n_kv = u64(), u64()
            # every KV takes >= 13 bytes (u64 key length, u32 type, 1-byte value) and every
            # tensor info >= 24 (u64 name length, u32 n_dims, u32 type, u64 offset): counts
            # that cannot fit in the file end in a short read in the loader
            if n_kv * 13 + n_tensors * 24 > size:
                return "invalid"
            if n_kv > MAX_KV or n_tensors > MAX_TENSORS:
                return "-"
            align = 32
            for _ in range(n_kv):
                klen = u64()
                key = rd(klen) if klen <= 64 else (skip(klen) or b"")
                t = u32()
                if key == b"general.alignment":
                    if t != 4:
                        return "invalid"
                    align = u32()
                    if align == 0 or align & (align - 1):
                        return "invalid"
                else:
                    skip_value(t)
            infos = []
            for _ in range(n_tensors):
                skip(u64())  # name
                nd = u32()
                if nd > 4:
                    return "invalid"
                ne = [u64() for _ in range(nd)] or [1]
                tt, off = u32(), u64()
                if tt not in QSIZES:
                    return "-"
                blk, tsz = QSIZES[tt]
                if ne[0] % blk:
                    return "invalid"
                n = 1
                for d in ne:
                    n *= d
                infos.append((off, n // blk * tsz))
            start = (f.tell() + align - 1) // align * align
            expect = 0
            for off, nbytes in infos:
                if off != expect or start + off + nbytes > size:
                    return "invalid"
                expect += (nbytes + align - 1) // align * align
            return "ok"
        except Bad:
            return "invalid"
        except Unknown:
            return "-"


def path_count(args):
    # Round 95 (C1; wave-1 RV01 DEFECT-3): one candidate can name several distinct model paths
    # (-m, -mm, -md ...), and every one of them is parsed. The pass allowance must price PATHS,
    # not entries, or a single candidate with three 200 MB files truncates the pass.
    if not isinstance(args, list) or not args or not all(isinstance(a, str) for a in args):
        return 0
    n = 0
    for i, a in enumerate(args):
        if a in PATH_FLAGS and i + 1 < len(args):
            n += 1
        elif "=" in a and a.split("=", 1)[0] in PATH_FLAGS:
            n += 1
    return n


def file_state(args):
    if not isinstance(args, list) or not args or not all(isinstance(a, str) for a in args):
        return "-"
    if not os.path.isabs(args[0]) or not os.path.isfile(args[0]):
        return "-"
    paths = []
    for i, a in enumerate(args):
        if a in PATH_FLAGS and i + 1 < len(args):
            paths.append(args[i + 1])
        elif "=" in a and a.split("=", 1)[0] in PATH_FLAGS:
            paths.append(a.split("=", 1)[1])
    states = [gguf_state(p) for p in paths if os.path.isabs(p)]
    for want in ("missing", "invalid"):
        if want in states:
            return want
    return "-"


try:
    doc = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
if not isinstance(doc, dict):
    sys.exit(0)
seq = doc.get("data") if isinstance(doc.get("data"), list) else doc.get("models")
seq = seq if isinstance(seq, list) else []
if sys.argv[2] == "count":
    total = 0
    for idx in sys.argv[3:]:
        try:
            total += path_count(seq[int(idx)]["status"].get("args"))
        except Exception:
            pass
    print(total)
    sys.exit(0)
if sys.argv[2] == "files":
    for idx in sys.argv[3:]:
        try:
            fs = file_state(seq[int(idx)]["status"].get("args"))
        except Exception:
            fs = "-"
        print(f"{idx}\t{fs}")
    sys.exit(0)
for n, e in enumerate(seq):
    if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
        continue
    # Round 90 (wave-1 RV01 BLOCKER-1): an id with control characters is kept and printed as
    # \uXXXX text (as served_ids does), never dropped: a dropped entry would hide its status and
    # turn a loading/unloaded router into MODEL_OK for a wildcard consumer.
    rid = "".join("\\u%04x" % ord(c) if ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F else c for c in e["id"])
    st = e.get("status")
    if not isinstance(st, dict):
        val, failed = "-", 0
    else:
        v = st.get("value")
        val = v if isinstance(v, str) and v and not any(ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F for c in v) else "?"
        failed = 1 if st.get("failed") is True else 0
    print(f"{rid}\t{val}\t{failed}\t{n}")
