# SnapshotCompat — MODEL_LOADING baseline acceptance test

## Files changed
- `tools/test-snapshot.sh` — added one new test block at lines 162-183 (between
  the existing "malformed trust anchor" block and the refusal checks). No
  existing case touched.

## What was added and why
`kama-probe.sh snapshot`'s `diff_baseline` (tools/kama-probe.sh:886-901) trusts a
baseline `latest.tsv` row only when its verdict string is in a hard-coded
whitelist (line 895). Once `MODEL_LOADING` lands in that whitelist (and VOCAB),
a baseline row written during a llama.cpp load window must be diffed like any
other verdict instead of being rebaselined as garbage.

The new block proves both directions with a hand-seeded `latest.tsv` — the same
offline fixture style as the `garbage garbage garbage` case at line 151; no live
port is required because the baseline file is the surface under test:

- `fixture-a\tMODEL_LOADING\tllamacpp-loading\t-\t<port>\tyes` — seeded as a
  registry-id that is *absent* from the current registry (`fixture-b`). If the
  row is accepted, `diff_baseline` must emit
  `fixture-a row-absent (was verdict=MODEL_LOADING …)` in DELTA.md; if it were
  still rejected as malformed, that line could not exist. Asserted via
  `assert_contains`, plus two negative `grep -q` guards (same style as the
  line-156 phantom-row-absent guard): no `malformed-row-dropped id='fixture-a'`
  in DELTA.md and no `dropping malformed baseline row for id='fixture-a'` in
  the run's merged stderr/stdout.
- `fixture-z\tMODEL_LOADED\tbogus\t-\t<port>\tno` — a near-miss unknown verdict
  (one character off the new vocabulary word) proving the whitelist remains an
  exact match: it must still warn `dropping malformed baseline row` and record
  `baseline-note malformed-row-dropped id='fixture-z'` in DELTA.md.
- Exit stays 2 (`run_probe` + `RC -eq 2` style): the `fixture-z` drop and the
  dead `fixture-b` row both keep the gate at drift.

Placement keeps all trust-anchor/baseline cases contiguous before the
`--port`/symlink refusal checks, matching the file's narrative order.

## Design choices
- Reused the dead-fixture phase: the fixture is already killed earlier in the
  script, so `fixture-b` classifies DEAD without any new listener.
- `fixture-a`/`fixture-z` names reuse the existing id vocabulary; no registry
  change needed because the test exercises `latest.tsv` parsing, not live
  classification.
- Six-field seeded rows (`id,verdict,reason,served,port,fmatch`) match the
  writer's emitted format at kama-probe.sh:1048-1050 so only the verdict field
  is under test.

## Expected behaviour
- **Frozen probe** (MODEL_LOADING not in the line-895 whitelist): the block is
  red — fixture-a is dropped, so the `row-absent … MODEL_LOADING` DELTA.md line
  is absent and the two negative guards trip.
- **Repaired probe**: all six checks pass; the fixture-z assertions are
  regression guards that stay green on both sides (MODEL_LOADED is unknown
  either way).

## Limitations
- Covers the `latest.tsv` acceptance path only; producing a live MODEL_LOADING
  snapshot row is the C1 verdict-harness seat's matrix, not this file.
- Whitelist ordering/substring edge cases beyond the near-miss string are not
  exercised (e.g. empty verdict field, extra whitespace) — out of scope for one
  additive case.

## Verification run here
- `bash -n tools/test-snapshot.sh` → clean. No other measurement run; L1 owns
  every gate/measurement.

## Installs
- None.
