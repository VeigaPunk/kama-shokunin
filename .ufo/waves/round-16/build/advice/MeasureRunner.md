# MeasureRunner — round-16 C1 counting command

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/measure.py`
  (new, stdlib only, executable). Nothing else touched.

## What it does

1. Loads `.ufo/waves/round-16/frozen/manifest.json` (exit 3 if unreadable or
   missing the `sha256` field).
2. Verifies `frozen/kama-probe-before.sh`:
   - sha256 == manifest `sha256` (`93ee4302…cd64`);
   - length == manifest `bytes` (47443) when declared;
   - byte-for-byte equality with
     `git -C <lane> cat-file blob <source_commit>:<source_path>`
     (`20e392ea…:tools/kama-probe.sh`, defaults inlined if the manifest omits
     the fields).
   Any mismatch or git failure exits 4 **before any harness run**.
3. Runs `python3 tests/probe-verdicts/check.py --probe P --json` (cwd = lane
   root) for `before` = frozen snapshot, `after` = `tools/kama-probe.sh`, plus
   any extra `--probe NAME=PATH` pairs.
4. Writes `.ufo/waves/round-16/run-<name>.json`:
   `{"name","command","cwd","exit","stdout_sha256","parsed","stderr_tail"}` —
   `name`/`cwd` added for parity with round-15 `run-before.json` convention;
   `parsed` is the decoded stdout JSON or `null`.
5. Prints `name / exit / passes / failures`, per-family `passed/total` counts
   per run, and the list of test names whose observed verdict differs
   before→after (with expected verdict).
6. Exit 0 iff before has ≥1 failure, after has 0 failures, and every
   verdict-changed test's **expected** verdict is `MODEL_LOADING`; else 1.
   Exit 2 = usage error (bad NAME=PATH, duplicate or reserved name
   `before`/`after`).
## Design choices

- **Verdict diff keyed on test name** across the two `records` arrays
  (intersection only); absent names can't be compared.
- **MODEL_LOADING gate uses the expected (oracle) verdict**, not the observed
  one — matches the spec wording "every test that changed verdict is a
  MODEL_LOADING expectation" and also catches a test that flipped the wrong
  way.
- **Tolerant readers**: totals accept `passes|passed` / `failures|failed`;
  record verdicts accept nested `expected.verdict`/`observed.verdict` or flat
  `expected_verdict`/`observed_verdict`/`verdict`; family falls back to the
  `Family.` name prefix. Confirmed with VerdictHarness: the emitted
  `kama-probe-verdicts/v1` document has top-level `tests`/`passes`/`failures`
  plus `records[]` with `name`, `family`, nested `expected.{verdict,reason,
  exit}`, top-level observed `verdict`/`reason`/`probe_exit`, and `passed`
  bool — all read as primary keys by measure.py.
- **Timeout**: `--timeout` (default 600 s) per check.py invocation; a timeout
  records `exit: null` + note in `stderr_tail` so receipts still exist.
- **Probe names** restricted to `[A-Za-z0-9._-]+` so `run-<name>.json` can't
  escape the wave dir; `before`/`after` reserved to protect the two required
  receipts.
- `stdout_sha256` is over raw stdout bytes; `stderr_tail` is the last 600
  UTF-8 chars (errors replaced).

## Verified

- `python3 -m py_compile` clean; `--help` renders (only self-tests permitted
  for this seat). No harness run performed — L1 owns all measurement.

## Limitations / notes for L1

- Assumes `check.py --probe PATH --json` emits one JSON object on stdout even
  on failure (harness exit 2 still lands in the receipt with `parsed` set or
  null).
- The before↔after diff only compares names present in **both** record lists;
  a test added between runs appears in neither `changed` list nor the table
  diff (it does appear in after's per-family counts). If the harness drops
  tests, check `tests` totals in the two run files.
- If `parsed` is null (non-JSON stdout), passes/failures print as `-` and the
  run counts as failing the exit-0 condition.
- No tool installs performed; pacman pause respected (none needed).
