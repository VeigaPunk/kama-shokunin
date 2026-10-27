#!/usr/bin/env python3
"""X09NewNoopFixtures real-execution probe: run each variant's main() for real (no stubs)
with OUT redirected into scratch, and record the exit code plus the ld_audit value each
written receipt carries. Shows what the battery would do on real hardware, which the
checker's canned harness cannot see."""
import argparse
import importlib.util
import pathlib
import subprocess


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
    lines = ["name real_rc receipts(label=ld_audit)"]
    for name, path in files:
        real_run = subprocess.run
        m = load(path)
        subprocess.run = real_run
        out = scratch / f"out-{name}"
        m.OUT = out
        rc = m.main()
        pairs = []
        for f in sorted(out.glob("*.out")):
            vals = [t.split("=", 1)[1] for t in f.read_text().split() if t.startswith("ld_audit=")]
            pairs.append(f"{f.stem}={vals[0] if vals else 'none'}")
        lines.append(f"{name} {rc} {' '.join(pairs) if pairs else 'no-receipts'}")
    text = "\n".join(lines) + "\n"
    pathlib.Path(a.out).write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
