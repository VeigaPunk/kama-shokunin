#!/usr/bin/env python3
"""Compare base vs M model_matches exit codes over targeted + fuzz pairs, under set -euo pipefail."""
import json
import random
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIBB = HERE.parent / "lib" / "libB.sh"
LIBM = HERE.parent / "lib" / "libM.sh"
TMP = HERE / "served.bin"

rng = random.Random(912)
pool_alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/\\"


def rid():
    n = rng.randint(0, 12)
    s = "".join(rng.choice(pool_alpha) for _ in range(n))
    if rng.random() < 0.2:
        s += ".gguf"
    if rng.random() < 0.1:
        s = "1e3" if rng.random() < 0.5 else "1000"
    return s


UNI = "modèle/日本.gguf"

PAIRS = [
    (["good"], "good"), (["good"], "good.gguf"), (["/models/sub/good.gguf"], "good"),
    (["good.gguf.gguf"], "good"), (["good.gguf.gguf"], "good.gguf"), (["other"], "good"),
    (["good", "other"], "good"), (["other", "good"], "good"), ([], "good"), ([], ""),
    ([], "*"), ([""], "good"), (["", ""], "good"), (["/"], "good"), (["/", "//"], "good"),
    (["a/"], "a"), (["a/"], "a.gguf"), ([".gguf"], ""), ([".gguf"], "good"),
    (["x.GGUF"], "x"), (["x.GGUF"], "x.GGUF"), (["a.Gguf"], "a"), (["good "], "good"),
    (["good"], "good "), ([" good"], "good"), (["good"], " good"), ([r"\u001bgood"], "good"),
    ([r"a\b"], r"a\b"), ([r"a\b"], "a"), ([r'q"b\s'], r'q"b\s'), (["1e3", "1000"], "1e3"),
    (["1e3", "1000"], "1000"), (["1000"], "1e3"), (["01"], "1"), (["0x10"], "16"),
    (["16"], "0x10"), (["1.0"], "1"), (["1"], "1.0"), (["5."], "5"), (["-0"], "0"),
    (["nan"], "nan"), (["+5"], "5"), (["1E3"], "1000"), (["010"], "10"), (["good\r"], "good"),
    (["good"], "good\r"), (["\rgood"], "good"), (["a/b/c.gguf"], "c"), (["a/b/"], "b"),
    (["a//b"], "b"), (["good\n"], "good"), (["\n"], "good"), (["good", "/"], "good"),
    (["/", "good"], "good"), (["good.gguf", "/x/good.GGUF"], "good"), (["1000"], "1000"),
    ([UNI], UNI), (["モデル/na.me.gguf"], "na.me"), (["модель"], "модель"), (["𝄞"], "𝄞"),
    ([UNI], "modèle"), (["dup", "dup", "good", "dup"], "good"), (["Good"], "good"),
    (["good"], "Good"), (["good"], "*"), (["*"], "good"), (["-"], "-"), (["-"], "good"),
]

many = [f"x{i:06d}" for i in range(200000)]
LARGE = [
    ("T1-like-hit", "\n".join(many + ["good"]), "good"),
    ("T2-like-miss", "\n".join(many), "good"),
    ("T4-like-3.9M", "a" * 3900000 + "\ngood", "good"),
    ("T5-like-slashes", "a/" * 1900000 + "good.gguf", "good"),
]


def run(lib, served, expected, timeout):
    TMP.write_bytes(served.encode("utf-8", "surrogateescape"))
    cmd = ["bash", "-c",
           'source "$1"; set -euo pipefail; rc=0; model_matches "$(cat "$2")" "$3" || rc=$?; printf "%s" "$rc"',
           "_", str(lib), str(TMP), expected]
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode(), p.stderr.decode(), time.monotonic() - t0
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT", "", time.monotonic() - t0


def main() -> int:
    bad = 0
    lines = []
    cases = [(f"pair{i}", s, e) for i, (s, e) in enumerate(PAIRS)]
    cases += [(f"fuzz{i}", [rid() for _ in range(rng.randint(1, 6))], rid() if rng.random() < 0.7 else "")
              for i in range(400)]
    for name, ids, exp in cases:
        served = "\n".join(ids)
        rb = run(LIBB, served, exp, 30)
        rm = run(LIBM, served, exp, 60)
        same = rb[0] is not None and rb[0] == rm[0] and rb[1] == rm[1]
        if not same:
            bad += 1
            line = f"DIFF {name} served={ids!r} exp={exp!r} base=({rb[0]},{rb[1]!r},{rb[2]!r}) m=({rm[0]},{rm[1]!r},{rm[2]!r})"
        else:
            line = f"OK {name} rc={rm[0]}"
        lines.append(line)
    for name, served, exp in LARGE:
        rm = run(LIBM, served, exp, 60)
        rb = run(LIBB, served, exp, 30)
        lines.append(f"LARGE {name} base=({rb[0]},{rb[3]:.2f}s) m=({rm[0]},{rm[3]:.2f}s) rc_m={rm[1]}")
        if rm[0] not in (0, 1, 2) or rb[0] not in (0, "TIMEOUT") or (rb[0] == 0 and rb[0] != rm[0]):
            bad += 1
            lines.append(f"  LARGE-DIFF {name}: base={rb[0]}/{rb[1]} m={rm[0]}/{rm[1]}")
    # errexit behaviour must match: direct unguarded call under set -euo pipefail
    for name, served, exp in [("ok", ["good"], "good"), ("miss", ["other"], "good"),
                              ("unresolvable", [], "good")]:
        TMP.write_bytes("\n".join(served).encode())
        outs = []
        for lib in (LIBB, LIBM):
            cmd = ["bash", "-c",
                   'source "$1"; set -euo pipefail; model_matches "$(cat "$2")" "$3"; echo UNREACHABLE',
                   "_", str(lib), str(TMP), exp]
            p = subprocess.run(cmd, capture_output=True, timeout=30)
            outs.append((p.returncode, p.stdout.decode()))
        tag = "ERREXIT-OK" if outs[0] == outs[1] else "ERREXIT-DIFF"
        if outs[0] != outs[1]:
            bad += 1
        lines.append(f"{tag} {name} base={outs[0]} m={outs[1]}")
    (HERE / "mm-results.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    print(f"MM pairs={len(cases)} diffs={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
