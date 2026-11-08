#!/usr/bin/env python3
"""MT01Forgeries: charge-arithmetic detector on MY mutant probe bytes.

Extracts the embedded ROUTER_PY parser from each probe file and runs it on
tiny synthetic GGUFs with a REDUCED MAX_STEPS (set in the exec namespace after
loading the parser, so the probe's code path is the one under test). The
reduced budget makes a tiny file land on the boundary the mutant moves; the
real end-to-end run at MAX_STEPS = 5 000 000 is in selfcheck.py.

Case -> expected flip (only the named mutant differs from pristine):
  nd1_30 cap=170   pristine '-'   D_minus1 'invalid'
  nd1_30 cap=200   pristine 'invalid'  E_plus1/F_plus2 '-'
  nd1_30 cap=230   pristine 'invalid'  E_plus1 'invalid'  F_plus2 '-'
  nd4_30 cap=200   pristine '-'   B_flat6 'invalid'
  strarr_30 cap=60 pristine 'invalid'  A_kv2x '-'
  maxmeta110 (real budget, no override) pristine 'invalid'  C_maxmeta100 '-'
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries")
SCRATCH = Path("/fast/scratch/hyaku/kama-r98/MT01Forgeries")
PRISTINE = SCRATCH / "repo/tools/kama-probe.sh"
MUTANTS = OUT / "mutants"


def probe_files():
    d = {"pristine": PRISTINE}
    for p in sorted(MUTANTS.glob("*.sh")):
        d[p.stem] = p
    return d


def extract_parser(probe: bytes) -> str:
    a = b"ROUTER_PY=$(cat <<'PY'\n"
    i = probe.index(a) + len(a)
    j = probe.index(b"\nPY\n", i)
    src = probe[i:j]
    k = src.index(b"\ntry:\n    doc = json.load(open(sys.argv[1]))")
    return src[:k + 1].decode()


def ns_for(probe: bytes) -> dict:
    ns = {}
    exec(compile(extract_parser(probe), "<router_py>", "exec"), ns)
    return ns


def tiny_tensors(n: int, nd: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n, 0)]
    for i in range(n):
        name = b"t%d" % i
        dims = struct.pack("<" + "Q" * nd, 1, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, 1 << 40))  # bad offset -> invalid
    return b"".join(out)


def tiny_strarr(n: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, n))
    out.append((struct.pack("<Q", 1) + b"x") * n)
    name = b"t0"
    out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    return b"".join(out)


def maxmeta_like(payload_len: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<I", 8))          # GGUF string value
    out.append(struct.pack("<Q", payload_len))
    out.append(b"\0" * 64)
    name = b"t0"
    tail = (struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    return b"".join(out) + b"\0" * (payload_len - 64) + tail


CASES = [
    ("nd1_30_cap170", lambda: tiny_tensors(30, 1), 170),
    ("nd1_30_cap200", lambda: tiny_tensors(30, 1), 200),
    ("nd4_30_cap200", lambda: tiny_tensors(30, 4), 200),
    ("strarr_30_cap60", lambda: tiny_strarr(30), 60),
]


def main() -> int:
    fx = SCRATCH / "patchcheck"
    fx.mkdir(parents=True, exist_ok=True)
    rows = {}
    files = {}
    for case, build, cap in CASES:
        p = fx / f"{case}.gguf"
        p.write_bytes(build())
        files[case] = str(p)
    mm = fx / "maxmeta110.gguf"
    mm.write_bytes(maxmeta_like(110 * 1024 ** 2))
    files["maxmeta110"] = str(mm)

    ranges = [("nd1_30_cap170", 170, "invalid", "D_minus1"),
              ("nd1_30_cap200", 200, "-", "E_plus1,F_plus2"),
              ("nd4_30_cap200", 200, "invalid", "B_flat6"),
              ("strarr_30_cap60", 60, "-", "A_kv2x")]
    cap_of = {c: cap for c, _, cap in CASES}

    for name, path in probe_files().items():
        ns = ns_for(path.read_bytes())
        row = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "cases": {}}
        for case, _, cap in CASES:
            ns["MAX_STEPS"] = cap
            ns["MAX_META"] = 512 * 1024 ** 2
            row["cases"][case] = ns["gguf_parse"](files[case])
        # maxmeta: use the mutant's own baked constants (no override)
        ns2 = ns_for(path.read_bytes())
        row["cases"]["maxmeta110"] = ns2["gguf_parse"](files["maxmeta110"])
        rows[name] = row
        print(f"PATCHCHECK {name} " + " ".join(f"{k}={v}" for k, v in row["cases"].items()),
              flush=True)

    fails = []
    for case, cap, flipped_to, who in ranges:
        base = rows["pristine"]["cases"][case]
        if base == flipped_to:
            fails.append(f"{case}: pristine already {base!r}, harness cannot discriminate")
            continue
        for w in who.split(","):
            if rows[w]["cases"][case] != flipped_to:
                fails.append(f"{case}: {w} = {rows[w]['cases'][case]!r}, expected {flipped_to!r}")
    if rows["pristine"]["cases"]["maxmeta110"] != "invalid":
        fails.append("maxmeta110: pristine not invalid")
    if rows["C_maxmeta100"]["cases"]["maxmeta110"] != "-":
        fails.append("maxmeta110: C_maxmeta100 not '-'")
    # E vs F: at cap 230 only F flips
    ns = ns_for((MUTANTS / "E_plus1.sh").read_bytes())
    ns["MAX_STEPS"] = 230
    e230 = ns["gguf_parse"](files["nd1_30_cap200"])
    ns = ns_for((MUTANTS / "F_plus2.sh").read_bytes())
    ns["MAX_STEPS"] = 230
    f230 = ns["gguf_parse"](files["nd1_30_cap200"])
    print(f"PATCHCHECK E_plus1@230={e230} F_plus2@230={f230}")
    if not (e230 == "invalid" and f230 == "-"):
        fails.append(f"E/F separation at cap 230 failed: E={e230} F={f230}")

    (OUT / "patchcheck.json").write_text(json.dumps({"rows": rows, "fails": fails}, indent=2) + "\n")
    if fails:
        for f in fails:
            print(f"PATCHCHECK_FAIL {f}")
        return 1
    print("PATCHCHECK_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
