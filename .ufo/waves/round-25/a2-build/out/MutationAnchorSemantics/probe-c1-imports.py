#!/usr/bin/env python3
"""Import-level compile check for every registered mutant.

For each of the 28 registered mutants, write the mutated auditor to a temp
file and attempt a full module import (importlib).  A mutant is defective if
the mutated file fails to import (SyntaxError, NameError at import time,
etc.).  Pristine import is checked first as a baseline.

Run:  python3 probe-c1-imports.py <lane-root>
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
import tempfile
from pathlib import Path

LANE = Path(sys.argv[1]).resolve()
INSTRUMENT = LANE / "tests/report-audit/isolation-mutants.py"
AUDIT = LANE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("iso_mutants", INSTRUMENT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

src = AUDIT.read_text()

def try_import(path):
    try:
        s = importlib.util.spec_from_file_location("mutated_auditor", path)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)
        return True, None
    except BaseException as exc:  # noqa: BLE001 - capture any import failure
        return False, f"{type(exc).__name__}: {exc}"

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    base = td / "report-landing-audit.py"
    base.write_text(src)
    ok, err = try_import(base)
    print(f"BASELINE pristine import: {ok} {err or ''}")
    for name, old, new in m.MUTANTS:
        p = td / f"mutant-{name}.py"
        p.write_text(src.replace(old, new, 1))
        ok, err = try_import(p)
        print(f"{name:30s} import_ok={ok} {err or ''}")
