#!/usr/bin/env python3
"""MT01Forgeries: write MY OWN probe mutants (not the counter's MUTANTS bytes).

Reads the probe bytes from the round-98 clone, applies each patch with an
exact-once anchor assertion, writes mutants + a manifest. Never touches the
lane's tracked file.
"""
import hashlib
import json
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r98/MT01Forgeries/repo")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries/mutants")

# Each patch is (anchor, replacement), applied with bytes.count(anchor) == 1.
PATCHES = {
    # (A) header cost stays 5+nd, but every step spent inside a KV value
    # (including the per-element string charge) is charged twice.
    "A_kv2x": [(
        b"        def skip_value(t, depth=0):\n"
        b"            if t in SCALAR:\n",
        b"        def skip_value(t, depth=0):\n"
        b"            _s0 = steps[0]\n"
        b"            try:\n"
        b"                _skip_value(t, depth)\n"
        b"            finally:\n"
        b"                steps[0] += steps[0] - _s0\n"
        b"\n"
        b"        def _skip_value(t, depth=0):\n"
        b"            if t in SCALAR:\n")],
    # (B) one constant 6 steps per tensor header, whatever the rank (nd>=1): parse the
    # nd dims normally, then credit back nd-1 steps, so 5+nd - (nd-1) = 6.
    "B_flat6": [(
        b"                ne = [u64() for _ in range(nd)] or [1]\n"
        b"                tt, off = u32(), u64()\n",
        b"                ne = [u64() for _ in range(nd)] or [1]\n"
        b"                steps[0] -= nd - 1 if nd >= 1 else 0  # flat6: credit the rank back\n"
        b"                tt, off = u32(), u64()\n")],
    # (C) MAX_META 512 MiB -> 100 MiB.
    "C_maxmeta100": [(
        b"MAX_KV, MAX_ARR, MAX_TENSORS, MAX_META = 100_000, 50_000_000, "
        b"1_000_000, 512 * 1024 ** 2",
        b"MAX_KV, MAX_ARR, MAX_TENSORS = 100_000, 50_000_000, 1_000_000\n"
        b"MAX_META = 100 * 1024 ** 2  # MT01: 100 MiB header cap")],
    # (D) one FEWER step per header: 5+nd -> 4+nd.
    "D_minus1": [(
        b"            for _ in range(n_tensors):\n"
        b"                skip(u64())  # name\n",
        b"            for _ in range(n_tensors):\n"
        b"                steps[0] -= 1\n"
        b"                skip(u64())  # name\n")],
    # (E) one MORE step per header: 5+nd -> 6+nd, charged after the header completes
    # (a different site from the counter's loop-top patch; same class).
    "E_plus1": [(
        b"                infos.append((off, n // blk * tsz))\n",
        b"                infos.append((off, n // blk * tsz))\n"
        b"                steps[0] += 1\n")],
    # (F) two MORE steps per header: 5+nd -> 7+nd.
    "F_plus2": [(
        b"            for _ in range(n_tensors):\n"
        b"                skip(u64())  # name\n",
        b"            for _ in range(n_tensors):\n"
        b"                steps[0] += 2\n"
        b"                skip(u64())  # name\n")],
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    probe = (CLONE / "tools/kama-probe.sh").read_bytes()
    OUT.mkdir(parents=True, exist_ok=True)
    man = {"probe_path": str(CLONE / "tools/kama-probe.sh"),
           "probe_sha256": sha(probe), "probe_bytes": len(probe), "mutants": {}}
    for name, patches in PATCHES.items():
        b = probe
        steps = []
        for anchor, repl in patches:
            n = b.count(anchor)
            if n != 1:
                print(f"REFUSE {name}: anchor occurs {n} times, not exactly once",
                      file=sys.stderr)
                return 2
            b = b.replace(anchor, repl, 1)
            steps.append({"anchor_sha256": sha(anchor), "anchor_len": len(anchor),
                          "replacement_len": len(repl)})
        p = OUT / f"{name}.sh"
        p.write_bytes(b)
        # the mutant must still be a syntactically plausible shell script and
        # differ from the probe
        assert b != probe, name
        man["mutants"][name] = {"file": str(p), "sha256": sha(b),
                                "bytes": len(b), "patches": steps}
        print(f"MUTANT {name} sha256={sha(b)} bytes={len(b)}")
    (OUT / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    print(f"PROBE_SHA256 {man['probe_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
