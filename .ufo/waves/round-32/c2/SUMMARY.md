# Round-32 C2 (gate meaning repair) — controls and mutations

Frozen predicate (`.ufo/waves/round-32/preregistration.json` C2):
`gate-registry-check.py --rev <tip>` exits 0, final line `registered 10 unregistered 0
defective 0`; each control fixture exits 1 printing its named defect; `--selftest`
prints `GATE_SELFTEST pass=6 fail=0`.

Do-nothing control (v1 gate, bytes from base `18464d0` at `/tmp/gate-v1.py`):
- `controls/thin-row-v1.out`, `controls/empty-exit-v1.out`,
  `controls/nonexistent-path-v1.out`: each defective fixture reads
  `registered 9 unregistered 0`, `EXIT_CODE=0`.
- `controls/prose-only-v1.out`: base tree (two counters prose-only) reads exit 0.

Repaired gate (v2, `tools/gate-registry-check.py` this commit):
- `controls/thin-row-v2.out`: exit 1, `defective .ufo/waves/round-29/count-c1.py:
  thin-row` (+ `empty-entry`, `empty-exit-map` — a one-cell row is entangled).
- `controls/empty-exit-v2.out`: exit 1, `defective ...: empty-exit-map`.
- `controls/nonexistent-path-v2.out`: exit 1, `defective ...:
  missing-path:.ufo/waves/round-999/count-c999.py`.
- `before-base.out`: v2 semantics on the base tree exit 1 with the two prose-only
  counters `unregistered` — the repair's real-tree before-state.

Mutation arms (each deletes exactly one check; fixture named first):
- `mutations/MutNoExitMap-vs-CtlNoExitMap.out`: exit 0 — the check is load-bearing.
- `mutations/MutNoPath-vs-CtlBadPath.out`: exit 0 — the check is load-bearing.
- `mutations/MutNoThin-vs-CtlThin.out`: still exit 1 (defective 2: empty-entry,
  empty-exit-map) — thin-row is entangled with the cell-presence checks; disclosed.
- `mutations/MutNoExitMap-vs-CtlBadpath.out`: negative control — the wrong mutant
  leaves the badpath fixture failing (exit 1).

Selftest: `selftest-pre.out` — hermetic arms 1-5 PASS; arm 6 (lane tip `9afaf0e9`)
fails with `registered 7 unregistered 3` until the round-32 registry block lands;
re-run at the landed tip below (`selftest-final.out`).
