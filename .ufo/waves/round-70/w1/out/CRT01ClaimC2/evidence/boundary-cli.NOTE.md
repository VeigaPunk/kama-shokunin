# Note on boundary-cli.out

Raw output, unmodified. One half of it is **not** valid evidence:

- `### landed bytes, --cli` is valid: the file sits at its landed path
  (`tools/round65-host-census.py`), `LANE` resolves to the lane, the census ran against the
  real 22 members, exited 0 (green tip) and named the unknown waiver on stderr ->
  `warn cli_unknown_waiver`.
- `### corrected bytes, --cli` is **invalid**: `ex02-candidate-corrected.py` sits in the
  wave out directory, so the census derives `LANE` from `__file__` and runs the members with
  the wrong cwd; its nonzero exit is a cwd artifact, not a waiver result. The corrected
  file's real-population evidence is `realrun-corrected-at-tip.out` (in-process load with
  `LANE` pinned to the lane root), and the process-boundary `--cli` probe must be rerun
  after landing.
