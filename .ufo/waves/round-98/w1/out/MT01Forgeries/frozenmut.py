#!/usr/bin/env python3
"""MT01Forgeries: measure the charge class of the COUNTER'S OWN mutants.

The frozen C2 control receipt names a `flat6` mutant and says "a constant-6 probe
needs 4 200 000 ... decides invalid". This script materializes the counter's
mutants with the counter's own apply_mutant (read-only) and measures, from the
mutated parser's bytes with a reduced MAX_STEPS, the preamble cost p and the
per-header cost c at nd=1 and nd=4: total(n) = p + n*c, solved from two header
counts. No cell and no counter fixture is used.
"""
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries")
SCRATCH = Path("/fast/scratch/hyaku/kama-r98/MT01Forgeries")
REPO = SCRATCH / "repo"


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "rb98", REPO / "tools/round98-router-budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_counter()


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


def tiny(n: int, nd: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n, 0)]
    for i in range(n):
        name = b"t%d" % i
        dims = struct.pack("<" + "Q" * nd, 1, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, 1 << 40))
    return b"".join(out)


def threshold(ns, path: str) -> int:
    """Smallest MAX_STEPS at which the parse reaches a verdict (invalid)."""
    for cap in range(0, 4000):
        ns["MAX_STEPS"] = cap
        if ns["gguf_parse"](path) == "invalid":
            return cap
    raise AssertionError("never decided")


def main() -> int:
    fx = SCRATCH / "frozenmut"
    fx.mkdir(parents=True, exist_ok=True)
    files = {}
    for n in (10, 30):
        for nd in (1, 4):
            p = fx / f"n{n}_nd{nd}.gguf"
            p.write_bytes(tiny(n, nd))
            files[(n, nd)] = str(p)
    probe = (REPO / "tools/kama-probe.sh").read_bytes()
    out = {"probe_sha256": hashlib.sha256(probe).hexdigest(), "mutants": {}}

    def measure(label: bytes) -> dict:
        ns = ns_for(bytes(label))
        t10_1 = threshold(ns, files[(10, 1)])
        t30_1 = threshold(ns, files[(30, 1)])
        t10_4 = threshold(ns, files[(10, 4)])
        t30_4 = threshold(ns, files[(30, 4)])
        p1 = (30 * t10_1 - 10 * t30_1) / 20
        c1 = (t30_1 - t10_1) / 20
        p4 = (30 * t10_4 - 10 * t30_4) / 20
        c4 = (t30_4 - t10_4) / 20
        return {"total_10_nd1": t10_1, "total_30_nd1": t30_1,
                "total_10_nd4": t10_4, "total_30_nd4": t30_4,
                "preamble_nd1": p1, "per_header_nd1": c1,
                "preamble_nd4": p4, "per_header_nd4": c4}

    out["mutants"]["pristine"] = measure(probe)
    print("FROZENMUT pristine", out["mutants"]["pristine"], flush=True)
    fdir = OUT / "frozen-mutants"
    fdir.mkdir(exist_ok=True)
    for name in ("flat6", "undercharge", "maxmeta", "nopreamble", "overcharge"):
        mb = MOD.apply_mutant(probe, name)
        (fdir / f"{name}.sh").write_bytes(mb)
        rec = measure(mb)
        rec["sha256"] = hashlib.sha256(mb).hexdigest()
        out["mutants"][name] = rec
        print(f"FROZENMUT {name} sha256={rec['sha256']} "
              f"nd1={rec['preamble_nd1']}+{rec['per_header_nd1']}/hdr "
              f"nd4={rec['preamble_nd4']}+{rec['per_header_nd4']}/hdr", flush=True)
    (OUT / "frozenmut.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
