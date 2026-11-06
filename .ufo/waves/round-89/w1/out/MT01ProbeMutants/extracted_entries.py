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
PATH_FLAGS = ("-m", "--model", "-mm", "--mmproj", "-md", "--model-draft")


class Bad(Exception):
    pass


class Unknown(Exception):
    pass


def gguf_state(path):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "-"
    if not stat.S_ISREG(st.st_mode):
        return "invalid"
    size = st.st_size
    try:
        f = open(path, "rb")
    except OSError:
        return "-"
    with f:
        def need(n):
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
                else:
                    for _ in range(n):
                        skip_value(et, depth + 1)
            else:
                raise Bad()
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
for e in seq if isinstance(seq, list) else []:
    if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"] \
            or any(c in e["id"] for c in "\t\r\n"):
        continue
    st = e.get("status")
    fstate = "-"
    if not isinstance(st, dict):
        val, failed = "-", 0
    else:
        v = st.get("value")
        val = v if isinstance(v, str) and v and "\t" not in v and "\n" not in v else "?"
        failed = 1 if st.get("failed") is True else 0
        if val == "unloaded" and not failed:
            try:
                fstate = file_state(st.get("args"))
            except Exception:
                fstate = "-"
    print(f"{e['id']}\t{val}\t{failed}\t{fstate}")

if len(sys.argv) > 2:
    print('RAW', sys.argv[2], gguf_state(sys.argv[2]))
