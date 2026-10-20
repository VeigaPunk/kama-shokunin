# RegistryReview — round 15 read-only review of the SKILL gate registry and verdict map

Reviewer: KamaR15.RegistryReview-3 (leaf, read-only except this report).
Scope: `SKILL.md` gate/probe registry rows (lines 294–476) against the code each row names.
Method: static reads and greps only. No gate, self-test, probe, measurement or test was executed.
Pending (in flight, not final failures): `tests/ollama-corpus-guard/*.json` (12 fixtures present) and the
round-15 guard harness/runner, which do not exist yet as an entry command.

## Verdict

The round-11, round-12, round-13 and round-14 classifier/probe rows match their code for the exit
codes they name. The defects are gaps and wording, not wrong exit meanings: the round-14 runner that
round 15 repairs has no registry row; one round-13 row attaches a frozen-mode exit to the live-mode
command; one round-14 cell says "failed" where the code emits findings. No blocking defect.

## Findings (by severity)

**F1 — Medium: `round-14/measure.py` has no registry row.**
The runner the round-15 repair targets is named only in prose (`SKILL.md:472–476`). A registry row
must state its real contract:
- Entry: `python3 .ufo/waves/round-14/measure.py [--tool PATH] [--cases PATH]`
  (`measure.py:459–474`; defaults `measure.py:57–58`, `tools/kama-ollama-evidence.py` and
  `tests/ollama-evidence/cases.json`).
- Exit map is 0 or 1 only. 0 requires at least one fixture and every fixture passing
  (`measure.py:395–397`). 1 covers corpus rejection, absent tool (`unsupported`), invalid cases and
  every unexpected error (`measure.py:428–457`, `477–487`). No exit 2 exists, so the registry's
  0/1/2 convention does not apply here.
- No `--selftest`; the runner is its own test over the fixed fixture set.
- Pinned: `SCHEMA kama-round-14-measure/v1`, `MINIMUM_UNIQUE_CASES = 16` (`measure.py:60,66`).
  Round-14 receipt `acceptance.json` records `cases_sha256 4a4de0b8…` and `unique_case_names: 51`.
- Write scope: stdout JSON; per-fixture `TemporaryDirectory` (`measure.py:382`).

Related limit to record in the row: the round-14 receipts pin the classifier's digest
(`tool_sha256`, e.g. `38d1f5d2…`) but not `measure.py`'s own bytes. Any round-15 edit to
`measure.py` therefore changes what the historical command is without a pin. The row should say
that old receipts do not identify the runner revision.
Fix: add a round-14 measure row (name, gate, 0/1 map, pinned constants above, write scope, owner
kama). Do not add a new path; the spec keeps the runner at the historical path.

**F2 — Low–Medium: round-13 row attaches a frozen-mode exit to the live command.**
Row command: `python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md`
(`SKILL.md:430`). With no `--manifest`, `main` runs `run_live` (`round-13/measure.py:872–875`),
which is unpinned and reads the mutable `HEAD`/before-revision git blob. `snapshot_tampered` (exit 2)
is emitted only from `run_frozen` (`measure.py:553`). The verdict-map cell nevertheless lists
`snapshot_tampered` for the default command, with the frozen pin mentioned only in the cell's
parenthetical.
Fix: split into two rows or state the mode in the command cell: live → 0 `clean`, 1
`documentation_mismatch`, 3 `probe_error`; frozen (`--quality PATH --manifest PATH`) → 0/1/2/3.
Inaccurate today: a live run reporting exit 0 is not a pinned clean verdict.

**F3 — Low: round-14 classifier verdict-map cell says "1 failed", which the code does not support.**
`SKILL.md:470` reads "1 failed captured policy". The same section says exit 1 means
"nonmatching-or-remote evidence" (`SKILL.md:465`). The code maps `available_not_loaded`,
`remote_inventory` and `identity_conflict` to exit 1 (`tools/kama-ollama-evidence.py:91–98`).
`available_not_loaded` is a valid local-tag observation, not a failure.
Fix: "1 nonmatching, remote or conflicting capture (finding IDs distinguish)".

**F4 — Low: the classifier self-test and the round-14 runner define "duplicate" differently.**
`tools/kama-ollama-evidence.py:359–365` compares raw `name` strings. `round-14/measure.py:350–356`
strips names before deduplication. The registered self-test cell (`SKILL.md:470`) does not say
which rule it uses. `"x"` and `"x "` pass the classifier self-test's duplicate check and are rejected
by the runner.
Fix: state the rule in the self-test cell, or align the classifier to strip. Outside the scope of
the round-15 guard repair; record it for that owner.

**F5 — Info: verified matches (no action).**
- Round-14 classifier map: `FINDING_EXIT` (`kama-ollama-evidence.py:91–98`) equals `SKILL.md:446–453`.
  `--help` exits 0 through `SystemExit` (`:517–521`). Argv errors and invalid input exit 2
  (`:483–489`, `:499–501`). Self-test verdict is 0 `clean` or 1 `selftest_failed`
  (`:279–303`), as the row states.
- Round-11 row: `measure.py` provenance returns 0/1/2 (`round-11/measure.py:327`, `:227–271`);
  crosswalk returns 0/1/2 (`:378`, `:346`, `:348`). `--selftest` exists (`:613`). `BASELINE_SHA256`
  is pinned at `:101`, and `legacy-baseline.json` is present.
- Round-12 row: `exit_code = 0 if clean else (1 if source_mismatch else 2)` (`fidelity.py:319`);
  `main` returns 2 on exception (`:622`); `--manifest` default `auto`, `--selftest` present
  (`:585`, `:593`).
- Top probe rows: `check` drift exit 2 and `snapshot` drift exit 2 via `eval_rows` (`kama-probe.sh:840–843`,
  `:973–976`); `die` exits 1 (`:81`); `--help` exits 0 (`:136`). `tools/test-snapshot.sh` covers the
  clean fixture (`:91–92`), dead endpoint exit 2 (`:139`) and row-set drift (`:146–148`). The row's
  "malformed baseline and symlink refusal" claims were not checked in this pass.

## Pending (not final failures)

- `tests/ollama-corpus-guard/*.json`: 12 fixtures are present (ValidBoundaries, AdjacentDuplicate,
  UnicodeDuplicate, TriplicateName, TabCollision, DistantDuplicate, MultipleDuplicates,
  MiddleDuplicate, AppendDuplicate, WhitespaceCollision, PrependDuplicate, ObjectEnvelope).
  Their content and schema were not validated here.
- No round-15 section exists in `SKILL.md`, and no entry command exists for the guard harness.
  When it lands, register it with a 0 pass / 1 fail map only. Use the spec's `verdict_exit` 0/1;
  do not introduce a 2. Pin the fixture set and the JSON schema
  `kama-corpus-guard-test/v1`, and state write scope as temporary directories only.
- `.ufo/waves/round-15/frozen/measure-before.py` and `frozen/manifest.json` exist. Not compared here.

## Limits

- Static reading only; no command was executed, including no `--selftest`, `check`, `snapshot`,
  `measure.py` or fixture run.
- Receipt facts were taken from `round-14/acceptance.json` as recorded. Nothing was re-run to confirm them.
- Digests were not recomputed, and the live state of `registry/endpoint-consumers.tsv` was not read.
- No sibling file or receipt was edited; old receipts and lessons are unchanged.

## Tools

Installed or updated: **none**. No tool installs were needed or attempted.

## Report

Written to `.ufo/waves/round-15/build/advice/RegistryReview.md` (this file).
