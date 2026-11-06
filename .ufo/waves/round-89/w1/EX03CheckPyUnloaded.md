# EX03CheckPyUnloaded — routed defect R5: `tests/probe-verdicts/check.py` cannot grade MODEL_UNLOADED

Milestone kama r89 w1. Measured at M2 `21b9e36d6192e0a691550b32e0e6c38412227f4c` (= lane HEAD for
`tests/probe-verdicts/check.py`, sha256 `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`,
identical at M2 and `c8db8586`). Probe at M2/HEAD `a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf`.
Base probe `56174a1f` = `99dd1ab8d41bb682bb24d4747b85d1f86fb84c145c6531cd2f0201d738d54be5`; F2 probe `9b4c7af1` =
`0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19`. No tool installed or upgraded.

## Scope

Reproduce R5 (the harness cannot grade `MODEL_UNLOADED`), then deliver a candidate patch (`check.py` + a new
`RouterUnloaded.json`) that (a) keeps all 72 existing rows passing against the M2 probe, (b) makes five new
MODEL_UNLOADED rows pass, and (c) can fail — shown on base `56174a1f` and on the pre-router probe `9b4c7af1`.
Touches only my out dir and this file; lane read-only.

## Commands and outputs (true exit codes)

Clone `--shared` at M2 into scratch; `git rev-parse --show-toplevel` = the clone.

1. Baseline, unpatched harness at M2, full lane matrix: `python3 tests/probe-verdicts/check.py --json`
   → **exit 0**, `tests=72 passes=72 failures=0` (`receipts/00-baseline-unpatched-M2.{json,err}`).
2. Defect repro (unpatched harness, one minimal row `ZZRepro.router-unloaded-no-autoload`: `/v1/models` lists
   `stories260K` `status.value=unloaded`, `/props` `{"role":"router","models_autoload":false}`):
   → **exit 1**, `tests=1 passes=0 failures=1`, row `verdict=MODEL_UNLOADED reason=router-unloaded exit=2`
   (exactly as expected) but `served_model='stories260K' (expected '-')` → `passed:false`
   (`receipts/01-defect-repro-unpatched-M2.*`).
3. Same defect without any new harness feature (3 rows using `/bin/sh` and literal paths, `ZZRepro2.json`):
   unpatched **exit 1**, `tests=75 passes=72 failures=3` — only the three MODEL_UNLOADED rows fail, each on
   `served_model` (`receipts/02-unpatched-M2-nofiles-rows.*`); patched **exit 0**, `75/75`
   (`receipts/03-patched-M2-nofiles-rows.*`).
4. Patched harness + `RouterUnloaded.json`, full matrix, M2 probe, `--selftest`
   (`python3 tests/probe-verdicts/check.py --selftest --json`) → **exit 0**, `tests=77 passes=77 failures=0`;
   selftest `7/7` malformed tests rejected (6 embedded + duplicate-name), `2/2` malformed outputs rejected,
   successor row passes, timeout/process-group test passes (`receipts/04-patched-M2-full-77.*`).
5. Patched harness, base probe `56174a1f`, the five new rows → **exit 1**, `tests=5 passes=2 failures=3`: the
   three round-89 rows (missing / non-GGUF / GGUF-v1) grade `MODEL_OK router-unloaded-autoload exit=0`; the two
   round-88 rows correctly still grade MODEL_UNLOADED (`receipts/05-patched-BASE-56174a1f-newrows.*`).
6. Patched harness, F2 probe `9b4c7af1`, same five rows → **exit 1**, `0/5`: every row `MODEL_OK matched`, i.e.
   all five new rows are falsifiable, including the two that predate round 89
   (`receipts/06-patched-F2-9b4c7af1-newrows.*`).
7. Unpatched harness asked to load `RouterUnloaded.json` → **exit 2**, `schema error: RouterUnloaded.json[0]:
   unknown test keys: ['files']` (`receipts/07-unpatched-M2-refuses-files-key.err`).
8. `fault-controls.py` (copy with pins updated, `--skip-slow`) against patched check.py + M2 probe → **exit 0**,
   `faults=15 detected=15 accepted=0`, `F0` positive control healthy, matrix `files=10 tests=77`
   (`receipts/09-fault-controls-patched-M2.json`).
9. TMPDIR witness (in-process `grade()` of the non-GGUF row): fixture dir parent == `$TMPDIR`, exact bytes
   present during the row, `{tmp}` gone from the substituted routes, dir removed after grading, row passed
   (`receipts/08-tmpdir-witness.json`).
10. `patch -p1 --dry-run` of both candidate patches in the M2 clone → rc 0 for each.

## Findings

- **DEFECT (reproduced, root cause)** — `expected_served_model()` returned `"-"` for every verdict except
  `MODEL_OK`/`MODEL_MISMATCH`, but `classify()` sets `C_SERVED` at `tools/kama-probe.sh:802-804` inside the
  `is2 && has_models` arm and only then calls `router_refine` at `:820`, which rewrites MODEL_OK to
  `MODEL_UNLOADED`/`MODEL_LOADING`. Every correctly graded router-unloaded row whose body lists its model was
  therefore failed on `served_model`, whatever its verdict/reason/exit said. Evidence: receipt 01 record
  (`served_model='stories260K'`, `served_model_expected='-'`, `passed:false`) and receipt 02 (72 pass, 3 fail).
- **DEFECT (second facet of the same gap)** — the harness had no way to hand the probe host files, so no row
  could express `status.args` pointing at an absent path or a crafted header; the unpatched validator rejects
  such a row outright (receipt 07, exit 2). The patch adds an optional `files` map (relative name →
  `{"text"}`/`{"hex"}`) written under a per-row temp dir inside `$TMPDIR`, with `{tmp}` substituted into every
  string of the row; traversal and `{tmp}`-without-`files` are schema errors (two new selftest cases).
- **BLOCKER for integration** — `tests/probe-verdicts/fault-controls.py:115-117` pins the matrix set
  (`EXPECTED_MATRIX_SHA256 bf9068d8…`, `EXPECTED_MATRIX_TESTS 72`) and refuses to grade otherwise. A tenth
  matrix file changes both: new set = 10 files / 77 tests / sha256
  `380c470440504083cec3b243876afc49e51537c5158a3ea91d22c66c20bab1d2`. The L1 MUST apply
  `fault-controls-pins.patch` in the same commit; with it applied the controls pass 15/15 (receipt 09).
- **NOTE (stale prose the L1 owns)** — `SKILL.md:616` states the harness grades `served_model` as "`-` for
  every non-model verdict" and the matrix as "9 files, set sha256 `bf9068d8…, 72 rows"; both sentences are now
  wrong (the ids are owed by every verdict from the 2xx model-array arm; 10 files / 77 rows /
  `380c4704…`). Rows in `SCORECARD.md`/`LOG.md` quoting the 72-row harm suite must be read as 77 rows after
  integration (`tests=77 passes=77`). This is documentation, not a predicate change.
- **NOTE (falsifiability bound)** — the two rows that predate round 89 (no-autoload, failed) pass on base
  `56174a1f`; they are falsified only by a probe that drops MODEL_UNLOADED grading (F2 fails all five). The
  claim-relevant rows (missing / invalid / GGUF-v1) are falsified by base, which is the graded property.
- **NOTE** — the round-89 `router-model-invalid` class is not just a magic sniff: the GGUF-v1 row (magic
  `GGUF`, version 1) is graded `router-model-invalid` by M2, proving the header checks are reachable from a
  fixture.

## Deliverables (paths under `.ufo/waves/round-89/w1/out/EX03CheckPyUnloaded/`)

- `check.py` — candidate, sha256 `d4f73f1bb0a7f9042ec6b897c49efc4caa40c1ce40f1fc26cd86bdd8726afc75`
  (copy to `tests/probe-verdicts/check.py`; applies as `check-py.patch`, 260 lines, verified `patch -p1
  --dry-run`).
- `RouterUnloaded.json` — candidate, sha256
  `3295035377c895ba3d81668c52e0775044532b30a402897aa24b3e5fbe445726`, 5 rows (copy to
  `tests/probe-verdicts/RouterUnloaded.json`).
- `fault-controls-pins.patch` — pin update (10 files / 77 tests / `380c4704…`), verified dry-run and exercised.
- `check-py.patch` — unified diff of the harness change.
- `receipts/00…09` — every run above, `.json` + `.err` (human summary of the same run).
- Nothing else changed: lane tracked files untouched (only pre-existing `PROVINCE.md`/`SCORECARD.md` edits by
  other seats remain in `git status`).

VERDICT: holds — R5 reproduced (MODEL_UNLOADED rows fail only on `served_model`, 72 existing rows unaffected), patched harness grades 77/77 at M2, fails the new rows on base and on F2, and keeps fault-controls at 15/15 once its matrix pins are updated in the same commit.
