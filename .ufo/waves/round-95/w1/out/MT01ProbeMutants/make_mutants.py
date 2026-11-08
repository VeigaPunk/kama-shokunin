#!/usr/bin/env python3
"""Generate single-semantic-change mutants of tools/kama-probe.sh at M1 f6325660.

Input: the pristine bytes of tools/kama-probe.sh at rev f6325660 (sha256 436d994c...).
Each mutant applies ONE semantic change; textual edits are asserted to match exactly once.
Writes mutants/<id>.sh plus mutants/pristine.sh and mutants/DIFF.txt.
"""
import hashlib
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[5]  # .../kama-shokunin
PRISTINE = (REPO / "tools" / "kama-probe.sh").read_bytes()
WANT_SHA = "436d994c71c0af3a96bc1f5ab0f884f629395313f3c02716738cf7af7931b722"


def rep(b: bytes, old: bytes, new: bytes, count=1) -> bytes:
    n = b.count(old)
    if n != count:
        raise SystemExit(f"site matched {n} times, wanted {count}: {old[:70]!r}")
    return b.replace(old, new)


MUTANTS = {}

# M01 -- step bound removed from need() (the per-read/seek bound); skip_strings site kept.
MUTANTS["M01-step-bound-removed"] = lambda b: rep(
    b,
    b"            steps[0] += 1\n            if steps[0] > MAX_STEPS:\n                raise Unknown()\n            pos = f.tell()\n",
    b"            steps[0] += 1\n            pos = f.tell()\n",
)

# M02 -- step bound raised 1000x.
MUTANTS["M02-step-bound-raised"] = lambda b: rep(
    b, b"MAX_STEPS = 4_000_000\n", b"MAX_STEPS = 4_000_000_000\n"
)

# M03 -- step count shared by the whole files-mode pass instead of reset per file.
def m03(b: bytes) -> bytes:
    b = rep(b, b'SEEN = {}\n', b'SEEN = {}\nSHARED_STEPS = [0]\n')
    return rep(b, b'    steps = [0]\n    with f:\n', b'    steps = SHARED_STEPS\n    with f:\n')


MUTANTS["M03-step-budget-shared-per-pass"] = m03

# M04 -- MAX_META no longer bounds the header position (both enforcement sites gone).
def m04(b: bytes) -> bytes:
    b = rep(b, b"            pos = f.tell()\n            if pos > MAX_META:\n                raise Unknown()\n",
            b"            pos = f.tell()\n")
    b = rep(b, b"                if base + off > MAX_META:\n                    raise Unknown()\n", b"")
    return b


MUTANTS["M04-max-meta-removed"] = m04

# M05 -- MAX_META doubled (512 MiB -> 1 GiB).
MUTANTS["M05-max-meta-doubled"] = lambda b: rep(
    b, b"512 * 1024 ** 2", b"1024 * 1024 ** 2"
)

# M06 -- round-94 residue clock re-added: per-file 15 s DEADLINE consulted every 4096 steps.
def m06(b: bytes) -> bytes:
    b = rep(b, b"import json, os, stat, struct, sys\n", b"import json, os, stat, struct, sys, time\n")
    b = rep(b, b"    steps = [0]\n    with f:\n",
            b"    steps = [0]\n    DEADLINE = time.monotonic() + 15.0\n    with f:\n")
    b = rep(b,
            b"            if steps[0] > MAX_STEPS:\n                raise Unknown()\n            pos = f.tell()\n",
            b"            if steps[0] > MAX_STEPS or (steps[0] & 0xFFF) == 0 and time.monotonic() > DEADLINE:\n                raise Unknown()\n            pos = f.tell()\n")
    return b


MUTANTS["M06-residue-clock-readded"] = m06

# M07 -- wrapper per-candidate allowance collapsed to the constant 15 s.
MUTANTS["M07-wrapper-limit-15"] = lambda b: rep(
    b, b"local limit=$((20 + 15 * ncand))", b"local limit=$((20 + 15))"
)

# M08 -- wrapper per-candidate allowance one second per candidate (no 15x factor).
MUTANTS["M08-wrapper-limit-ncand"] = lambda b: rep(
    b, b"local limit=$((20 + 15 * ncand))", b"local limit=$((20 + ncand))"
)

# M09 -- memo key drops ctime (mtime is restorable by utime; ctime is not).
MUTANTS["M09-memo-key-drops-ctime"] = lambda b: rep(
    b, b"key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)",
    b"key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)"
)

# M10 -- file_state returns `invalid` (a negative) for the `-` (undecidable) fallthrough.
MUTANTS["M10-filestate-dash-as-invalid"] = lambda b: rep(
    b, b'    for want in ("missing", "invalid"):\n        if want in states:\n            return want\n    return "-"\n',
    b'    for want in ("missing", "invalid"):\n        if want in states:\n            return want\n    return "invalid"\n'
)

# M11 -- skip_strings work (chunk reads and per-string charge) never counted against MAX_STEPS.
def m11(b: bytes) -> bytes:
    b = rep(b,
            b"                if off + 8 > len(buf):\n                    steps[0] += 1\n                    if steps[0] > MAX_STEPS:\n                        raise Unknown()\n                    base += off\n",
            b"                if off + 8 > len(buf):\n                    base += off\n")
    b = rep(b, b"            steps[0] += n // 64\n", b"")
    return b


MUTANTS["M11-skip-strings-uncounted"] = m11

# M12 -- step bound lowered to 1M (< the 3M steps a 600k-tensor header needs).
MUTANTS["M12-step-bound-lowered"] = lambda b: rep(
    b, b"MAX_STEPS = 4_000_000\n", b"MAX_STEPS = 1_000_000\n"
)


def main() -> int:
    got = hashlib.sha256(PRISTINE).hexdigest()
    if got != WANT_SHA:
        raise SystemExit(f"pristine sha {got} != {WANT_SHA}")
    mdir = OUT / "mutants"
    mdir.mkdir(exist_ok=True)
    (mdir / "pristine.sh").write_bytes(PRISTINE)
    lines = [f"pristine sha256={got} bytes={len(PRISTINE)}"]
    for name, fn in MUTANTS.items():
        b = fn(PRISTINE)
        if b == PRISTINE:
            raise SystemExit(f"{name}: no change")
        if b"DEADLINE" in b and name != "M06-residue-clock-readded":
            raise SystemExit(f"{name}: unintended DEADLINE token")
        p = mdir / f"{name}.sh"
        p.write_bytes(b)
        lines.append(f"{name} sha256={hashlib.sha256(b).hexdigest()} bytes={len(b)}")
        d = REPO / "tools" / "kama-probe.sh"
        import subprocess
        diff = subprocess.run(["diff", "-u", "--label", "pristine", "--label", name, str(d), str(p)],
                              capture_output=True, text=True).stdout
        lines.append(diff)
    (mdir / "DIFF.txt").write_text("\n".join(lines))
    print("\n".join(x for x in lines if x.startswith(("pristine", "M0", "M1"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
