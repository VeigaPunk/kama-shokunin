# PriorCoverage — round 15 connector (KamaR15.PriorCoverage-3)

Read-only advice. I edited no file except this report. I ran no runner, classifier, harness, selftest, test, build, lint or formatter. Commands I did run were read-only: `git rev-parse`, `git hash-object` (no `-w`), `git diff`, `git status`, `sha256sum`, and stdlib-Python JSON/path inspection. Nothing was installed or updated through any channel (pacman, uv, npm or binary), consistent with the operator's host-wide pacman pause. No install was needed. I did no session or history access.

## Axes

- Assigned: **calibration 7** (the lowest) and **operability 8**.
- Tracked: freshness 8, depth 7, coverage 9, adjacency 7.
- Trends: expansion, quality, discernment.

My target is the boundary between the replay evidence the lane already holds and the new guard behavior, with no expansion inflation.

## Evidence (observed unless marked [INFERENCE])

### E1. The "before" run for the valid unique corpus already exists

- The `measure.py` blob is the same at every relevant revision:
  - `e545ed99` (the round-14 measured revision): `783004569af9072afdeb32c6eeacc462868eb76b`
  - `06cc6db` (delivered): same blob
  - `6e348e2` (round-15 start): same blob
  - `git hash-object .ufo/waves/round-15/frozen/measure-before.py`: same blob
- The frozen file's sha256 is `fda61e00…4b60d`, which matches `frozen/manifest.json`.
- The classifier and cases blobs are also unchanged since `e545ed99`:
  - `tools/kama-ollama-evidence.py`: blob `d38e2ae…`, sha256 `38d1f5d2…`
  - `tests/ollama-evidence/cases.json`: blob `677ba8a…`, sha256 `4a4de0b8…`
  - Both equal the receipt's `tool_sha256` and `cases_sha256`.
- So `.ufo/waves/round-14/acceptance.json` `records[2]` (`final_corpus`) is already the before-observation of exactly "frozen runner × current classifier × current 51 cases":
  - argv: `/usr/bin/python -I -B <lane>/.ufo/waves/round-14/measure.py`, run from the lane root
  - exit 0, stderr empty
  - stdout is 27445 bytes, sha256 `1b1b088389483f204ffd3653ea54215420740772492ea1f62641c3e0455d8ae9`
  - stored `stdout == json.dumps(parsed, indent=2) + "\n"` is `True`
- The working-tree `measure.py` differs from HEAD only by the two lines at `:358–359` (`if len(declared) != unique: problems.append("duplicate case names")`).
- On the held corpus the new predicate is false: 51 raw names are unique, 51 stripped names are unique, and no name has surrounding whitespace. [INFERENCE] The repaired runner should therefore reproduce the held stdout byte for byte.

### E2. Nothing currently re-observes the original 51 cases under the repaired runner

- Three places claim retention without a run against the original corpus:
  - `SCORECARD.md:485`: "retain valid all-unique corpus measurement"
  - `corpus/knowledge/ollama-evidence-replay.md:332–335`: "measures exactly as before"
  - `corpus/lessons/round-15.md:7`: "keep the same … original literal corpus"
- The only planned count is the guard matrix (`SCORECARD.md:491–494`).
- That matrix's positive controls use a single cloned input (see E4), not the 51-case corpus.
- So retention currently rests on static reasoning and the CaseAudit seats' inference. No run supports it.

### E3. Rejecting duplicate names on the committed corpus was already covered

- The classifier's `--selftest` already rejects duplicate names before any child runs (`tools/kama-ollama-evidence.py:356–365`, `duplicate_case_names` / `no_cases_executed`). Its rule differs from the runner's:
  - It always reads `DEFAULT_CASES` (`:493`).
  - It accepts arrays only (`:352–353`).
  - Its minimum counts records, not unique names (`len(document) < MIN_CASES`, `:84,356`).
  - It compares raw, non-empty names with no strip (`:359–364`).
- The new runner guard compares stripped names, from any caller `--cases` path, in either envelope, against a unique-count minimum.
- HarnessReview F2, RegistryReview F4, WhitespaceReview F3 and CaseAudit05/07 already found this divergence.
- The point for credit: the only new behavior is runner-level rejection over caller-supplied corpora under strip identity. The lane did not newly acquire duplicate-corpus rejection.

### E4. The guard matrix adds no classifier coverage

- `check.py:220–244` clones the first fixture with `expected_exit == 0`. That is `cases.json[0]` (`loaded_same_digest`, `--expect llama3:8b`).
- The runner passes only `--tags`, `--ps` and `--expect` to the child. Every guard-matrix child therefore sees one distinct classifier input.
- Counts at read time (files may still change):

  | Measure | Count |
  |---|---|
  | Fixture files | 12 |
  | Tests | 50 |
  | Tests expected rejected | 27 |
  | Tests expected accepted | 23 |
  | Names in accepted controls | 402 |
  | Names in rejected controls | 483 |

- Inside guard runs, `tool_sha256` is the hash of the temporary wrapper, not the classifier.
- `check.py` records `classifier_sha256` separately (`:644–645`). Its top-level `total` counts tests and does not sum `child_count` (`:634–655`).

### E5. Two places now treat the runner differently

- The existing knowledge entry calls the runner a round artifact: `ollama-evidence-replay.md:87–89` says ".ufo/waves/round-14/measure.py … is a round artifact, not a permanent lane command."
- In-flight changes treat it as permanent:
  - `SKILL.md:493–497` registers a permanent kama gate, `python3 tests/ollama-corpus-guard/check.py`, which "exercises `.ufo/waves/round-14/measure.py`".
  - The committed harness defaults `--runner` to that wave path (`check.py:61`).
- The contract keeps the runner at its historical path, so relocating it is not an option. But the two statements conflict and have not been reconciled.

### E6. The source registry grows, but the diagnosis is not new

- S034 (`corpus/SOURCES.md:46`; lesson `round-15.md:55–81`) adds an own-work A row. Census changes from 33 to 34 rows, A30 to A31, mined 23 to 24.
- Its content is the static R1 diagnosis that outside review already holds (`lessons/round-14-verifier-spotcheck.md:142`). The frozen manifest already pins it.
- `round-15.md:64` says "C1 rests on S034 plus the actual outside R1".
- `SCORECARD.md:502–504` correctly refuses a capability row, but does not yet say whether the row growth earns any credit.
- SourceReview F5 flagged the admission decision. The consequence for trend credit is still open.

### E7. Running the frozen runner with default arguments would mismeasure

- Its `LANE = WAVE.parents[2]` resolves to `<lane>/.ufo`. Neither default tool nor default cases exists there.
- So a default-argument run of the frozen runner would measure path absence, not the duplicate defect. ReceiptReview F1 found this.
- `check.py:353–362` passes `--tool` and `--cases` explicitly, so the guard matrix is unaffected.

## Proposed move: held-receipt anchor plus non-additive accounting

One synthesis for L1, at its single verification pass and in its own lesson/SCORECARD appends:

1. **Before.** Use `acceptance.json` `records[2]` as the before-observation of the 51-case corpus, justified by the blob identity in E1. Do not run the frozen runner on that corpus. This avoids E7 and avoids a second 51/51 count.
2. **After: one retention run.** Run exactly the held argv `/usr/bin/python -I -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py` from the lane root.
   - It passes only if exit is 0, stderr is empty, and stdout is byte-identical to `records[2].stdout` (27445 bytes, sha256 `1b1b0883…8ae9`).
   - If it differs, list every differing key against `records[2].parsed`.
   - Byte identity also enforces GuardRepair's "CLI schema preserved" requirement: any new field, `limits` edit or record drift breaks it.
3. **How to label it.** "Retention: denominator 51 unchanged, no new count, no C1 delta, not independent corroboration" (same lane, same oracle; see the round-14 verifier at `:86`). Keep it separate from the counting command.
4. **Guard-matrix denominators stay separate.** Report tests, not cases, split by expected_rejected (recount the final files), and state "distinct classifier inputs: 1".
   - Expected results, by static reading: the frozen runner behaves as accept-all on this matrix, so 23 pass and 27 fail. The repaired runner should give 50 pass and 0 fail.
   - Invocation counts (402 after; 885 before) are observations only. Never add them to, or present them alongside, the 51-case classifier total.
5. **One zero-credit ledger line each:**
   - (a) **Selftest prior coverage (E3).** The claim is "the runner now honors its own promise for caller corpora", not new duplicate rejection.
   - (b) **SKILL gate row (E5).** Add an appended note: it is a regression gate for a historical round artifact kept at its path by contract, not a new lane command. It earns no operability or expansion credit. Lines `:87–89` stay byte-intact.
   - (c) **S034 (E6).** Census +1 own-work row is bookkeeping that restates outside R1. It earns no expansion or discernment credit, and discovery stays with CloseKamaR14.
   - (d) No capability row or coverage-map row. `SCORECARD.md:502–504` already says this.

Effect on axes:

| Axis or trend | Effect |
|---|---|
| Calibration | Improved evidence, numeric stays 7. The "retain" half of C1 gets a test that can fail, where today it rests only on inference. |
| Operability | Unchanged. The plan runs no frozen 51-case run and has no default-path trap. |
| Expansion | Kept honestly at **unchanged**. |
| Coverage | Stays 9. |
| Quality and discernment | TrendMap's ruling and outside review own these. No harm observed. |

## Contradictions (stated, not resolved)

1. `ollama-evidence-replay.md:87–89` (round artifact) versus `SKILL.md:493–497` and `check.py:61` (permanent gate defaulting to that runner).
2. `SCORECARD.md:502–504` ("credited once, not repertoire growth") versus the census +1 row from S034 and `round-15.md:64` ("C1 rests on S034").
3. The retention claims in E2 versus a counting plan that never re-observes the 51 cases.
4. Two duplicate relations are now live in one lane (E3). They agree on the committed corpus only because it has no padded or blank names.

## Risks

- **The retention run could differ for benign reasons.** For example, L1 might deliberately edit `LIMITS`. Treat any byte difference as a finding, name the keys, and do not smooth it into "51/51 still passes".
- **It is not independent corroboration.** The held stdout is author-recorded. The outside verifier checked its internal consistency but did not re-execute it. A same-lane rerun corroborates it without independence.
- **Counts here are a snapshot.** Fixtures and `check.py` were still changing while I read them (the `check.py` tag changed mid-read). Recount from final bytes.
- **Scope is narrow.** Equality covers this one corpus. It certifies nothing about arbitrary valid corpora, blank or missing names (out of scope per `round-15.md:90–92`), runtime behavior or readiness.

## Verification for L1 (once, after all edits)

1. Re-confirm that `git hash-object .ufo/waves/round-15/frozen/measure-before.py` equals `git rev-parse e545ed99:.ufo/waves/round-14/measure.py`, and that the classifier and cases blobs are unchanged (E1).
2. Run the held argv above. Check exit 0, empty stderr, and stdout sha256 `1b1b088389483f204ffd3653ea54215420740772492ea1f62641c3e0455d8ae9` / 27445 bytes.
3. Run `check.py` with `--runner` set to the frozen path and then to the historical path. Expect 23 pass / 27 fail, then 50 pass / 0 fail (or the recounted final values).
   - Expected-rejected tests must show a marker count of 0 after the repair and equal to the test's name count before it.
   - Report `total` as a count of tests.
4. Source census: 33 → 34 rows, reported as zero-credit bookkeeping.

## Limitations

- All predictions are static.
- I did not judge S034 admission or the trend labels.
- I sent no peer messages.

Report: .ufo/waves/round-15/build/advice/PriorCoverage.md
