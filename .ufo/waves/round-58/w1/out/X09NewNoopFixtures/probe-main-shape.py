#!/usr/bin/env python3
"""X09NewNoopFixtures main-shape probe: what does each variant's main() actually ask for,
and what exit does it produce when every leg fails? Patches the module's own `run`,
`assert_mutant_breaks_detection` and `comparator_selftest` with recorders (all legs fail)
and points OUT at scratch, then calls main(). Nothing is written into the lane."""
import argparse
import importlib.util
import pathlib
import subprocess
import tempfile


def load(path):
    spec = importlib.util.spec_from_file_location("m_" + pathlib.Path(path).stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--genuine", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    scratch = pathlib.Path(a.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    files = [("00-genuine", a.genuine)] + [(p.stem, p) for p in sorted(pathlib.Path(a.variants).glob("X*.py"))]
    lines = ["name rc(all-legs-fail) run(label,counter,expected) assert(arg)"]
    for name, path in files:
        real_run = subprocess.run
        m = load(path)
        subprocess.run = real_run
        calls, asserts = [], []
        m.OUT = scratch / f"out-{name}"
        m.comparator_selftest = lambda out: True
        m.run = lambda label, counter, expected, out, _c=calls: (_c.append((label, pathlib.Path(counter).name, expected)), False)[1]
        m.assert_mutant_breaks_detection = lambda counter, out, _c=asserts: (_c.append(pathlib.Path(counter).name), False)[1]
        rc = m.main()
        lines.append(f"{name} {rc} run={calls} assert={asserts}")
    text = "\n".join(lines) + "\n"
    pathlib.Path(a.out).write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
