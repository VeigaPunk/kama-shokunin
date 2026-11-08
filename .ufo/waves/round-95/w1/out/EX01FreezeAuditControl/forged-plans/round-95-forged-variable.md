# Forged plan E — token that exists only as a Python variable, never printed (expected GREEN, defect)

Predicate: `python3 tools/round95-freeze-audit.py --repo . --rev <F>` prints `FREEZE_AUDIT missing_paths=0 met=True`

`missing_paths` appears in the tool's bytes as a dict key, not in its FREEZE_AUDIT output line.
