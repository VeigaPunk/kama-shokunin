#!/usr/bin/env python3
"""Serial re-run of run_matrix.py (concurrency check). Writes to ./serial/ and
compares exit codes and normalized stdout/stderr equality with the parallel
matrix.json written by run_matrix.py."""
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PARALLEL = json.loads((HERE / "matrix.json").read_text())
spec = importlib.util.spec_from_file_location("run_matrix", HERE / "run_matrix.py")
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)
rm.OUT = HERE / "serial"
rm.OUT.mkdir(parents=True, exist_ok=True)
info = rm.config_info()
raw = {cfg: rm.run_cfg(cfg) for cfg in rm.CONFIGS}
rows = [rm.compare(r) for cfg in rm.CONFIGS for r in raw[cfg]]
(rm.OUT / "configs.json").write_text(json.dumps(info, indent=2) + "\n")
(rm.OUT / "matrix.json").write_text(json.dumps(rows, indent=2) + "\n")
par = {(x["cfg"], x["name"]): x for x in PARALLEL}
diffs = []
for x in rows:
    p = par[(x["cfg"], x["name"])]
    for k in ("exit", "exit_ok", "stdout_norm_eq", "stderr_norm_eq"):
        if p[k] != x[k]:
            diffs.append((x["cfg"], x["name"], k, p[k], x[k]))
print(f"serial rows={len(rows)} exit_mismatches={sum(1 for x in rows if not x['exit_ok'])}")
print(f"parallel-vs-serial differences on exit/exit_ok/stdout_eq/stderr_eq: {len(diffs)}")
for d in diffs:
    print("  DIFF", d)
