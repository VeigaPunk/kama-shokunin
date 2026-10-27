#!/usr/bin/env python3
"""Dump raw instrument output per fixture for the E03 receipts (no verdict logic)."""
import json
import pathlib
import subprocess
import sys

S = pathlib.Path("/fast/scratch/hyaku/kama-r57/E03CounterSelftest")
FIX = json.loads((S / "out" / "fixtures.json").read_text())
INSTRUMENTS = {
    "c1": {
        "prereg-pre-repair": S / "bin/prereg-pre-repair.py",
        "prereg-candidate": S / "bin/prereg-candidate.py",
        "ref-c1-execbind": S / "bin/ref-c1-execbind.py",
        "noop-c1-instrument": S / "bin/noop-c1-instrument.py",
    },
    "c2": {
        "selfdesc-committed": S / "bin/ref/round42-selfdesc-reconcile.py",
        "ref-c2-witness": S / "bin/ref/ref-c2-witness.py",
        "frozen-noop": S / "bin/frozen-noop.py",
    },
}


def main(mode):
    lines = []
    for label, path in INSTRUMENTS[mode].items():
        for name, meta in FIX[mode].items():
            p = subprocess.run([sys.executable, str(path), "--repo", meta["dir"],
                                "--tip", meta["tip"]], capture_output=True, text=True)
            body = [l for l in p.stdout.splitlines()
                    if not l.startswith("detail:")]
            lines.append(f"=== instrument={label} fixture={name} exit={p.returncode}")
            lines += [f"    {l}" for l in body]
            if p.stderr.strip():
                lines.append(f"    stderr: {p.stderr.strip()}")
    text = "\n".join(lines) + "\n"
    (S / "out" / f"evidence-{mode}.txt").write_text(text)
    sys.stdout.write(text)


if __name__ == "__main__":
    main(sys.argv[1])
