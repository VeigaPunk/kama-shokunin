#!/usr/bin/env python3
"""Run the frozen counter's own expansion/recompute on the X1 fixtures (read-only)."""
import importlib.util, json, subprocess, sys
C = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py"
spec = importlib.util.spec_from_file_location("c1c", C); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def g(d,*a): return subprocess.run(["git","-C",d,*a],capture_output=True).stdout.decode()
for d in sys.argv[1:]:
    tip = g(d,"rev-parse","HEAD").strip()
    rows,_ = m.read_contract(d, tip)
    files = m.contract_files(d, tip, rows) if rows else []
    ev = m.recompute(d, tip, files) if files else []
    print(f"{d.split('/')[-1]:32s} contract_rows={len(rows) if rows else 0} counter_files={files} counter_events={[(e['commit'][:8],e['file'],e['deleted'],e['status']) for e in ev]}")
