import json, os, stat, struct, sys, time

QSIZES = {0: (1, 4), 1: (1, 2), 2: (32, 18), 3: (32, 20), 6: (32, 22), 7: (32, 24), 8: (32, 34),
          9: (32, 36), 10: (256, 84), 11: (256, 110), 12: (256, 144), 13: (256, 176),
          14: (256, 210), 15: (256, 292), 16: (256, 66), 17: (256, 74), 18: (256, 98),
          19: (256, 50), 20: (32, 18), 21: (256, 110), 22: (256, 82), 23: (256, 136),
          24: (1, 1), 25: (1, 2), 26: (1, 4), 27: (1, 8), 28: (1, 8), 29: (256, 56),
          30: (1, 2), 34: (256, 54), 35: (256, 66), 39: (32, 17), 40: (64, 36),
          41: (128, 18), 42: (64, 18), 43: (1, 1)}
SCALAR = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, 1_000_000, 512 * 1024 ** 2
# read/seek budget per file and a wall-clock deadline PER FILE: a hostile or
# odd header becomes "undecidable" (no verdict change), never a stall (r89 SN01 F1).
# Round 94 (C1; r93 wave-1 SC02): the deadline is per gguf_parse call, not per ROUTER_PY
# invocation. The former single 4 s deadline was shared by every candidate, so one slow
# file spent the whole call's budget and left later candidates undecided (-), which the
# round-89 rule grades loadable: the verdict flipped MODEL_UNLOADED -> MODEL_OK under host
# load. Each file now gets its own slice; MAX_STEPS stays the deterministic work bound.
MAX_STEPS = 4_000_000
PER_FILE_SECONDS = 15.0
DEADLINE = time.monotonic() + PER_FILE_SECONDS
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
    global DEADLINE
    DEADLINE = time.monotonic() + PER_FILE_SECONDS
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
            if steps[0] > MAX_STEPS or (steps[0] & 0xFFF) == 0 and time.monotonic() > DEADLINE:
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
            for _ in range(n):
                if off + 8 > len(buf):
                    if time.monotonic() > DEADLINE:
                        raise Unknown()
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
            steps[0] += n // 64
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
