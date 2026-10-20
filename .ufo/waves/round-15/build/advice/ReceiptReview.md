# ReceiptReview: round-14 acceptance provenance and round-15 in-flight integrity (read-only)

Scope: historical round-14 receipts, the frozen pre-repair runner, the in-flight round-15 repair and fixtures. Root: `/home/vgpnk/Projects/shokunin/kama-shokunin`. No tests, harnesses, builds or runners executed. Only read-only git (`log`, `show`, `diff`, `status`, `ls-tree`), `sha256sum`, `cmp`, `diff` and JSON reads. No installs or updates. Pending round-15 items are listed separately and are not treated as failures.

## Verdict

Committed round-14 receipts are intact at byte level. The frozen pre-repair runner is byte-identical to the round-14 runner at the pinned commits. Three things need attention before the round-15 close: (1) the frozen runner's default paths resolve wrongly and could make the red control fail for the wrong reason; (2) the historical receipt's command path now points at repaired bytes, so the appended record must pin hashes; (3) the S012 `used-by` change has no old→new record yet.

## Findings by severity

### F1 — medium: frozen runner default paths resolve under `.ufo/`, not the lane root

- `.ufo/waves/round-15/frozen/measure-before.py:55-58`: `WAVE = Path(__file__).resolve().parent`; `LANE = WAVE.parents[2]`; `DEFAULT_TOOL` and `DEFAULT_CASES` are built from `LANE`.
- Placed in `.ufo/waves/round-14/`, `parents[2]` is the lane root. Placed in `.ufo/waves/round-15/frozen/`, `parents[2]` is `.ufo/`. So the defaults become `.ufo/tools/kama-ollama-evidence.py` and `.ufo/tests/ollama-evidence/cases.json`, neither of which exists.
- Consequence: a red control that runs `--runner .ufo/waves/round-15/frozen/measure-before.py` without explicit `--tool` and `--cases` gets every fixture `unsupported` and exit 1. That is the same exit as the round-14 absent-tool baseline (`acceptance.json` `capability_absent`, exit 1, 0/51). Exit 1 alone cannot discriminate the duplicate defect.
- Recommendation: the harness must pass `--tool` and `--cases` explicitly. Its red assertion must check the duplicate-specific behavior: the frozen runner spawns children for a ≥16-unique-plus-duplicate corpus, and the repaired runner emits the `duplicate case names` problem with zero child invocations. Do not assert exit 1 as evidence.

### F2 — medium: historical receipt command path now resolves to repaired bytes

- `.ufo/waves/round-14/measure.py` is modified in the working tree and is not committed. Current sha256 `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`. The diff against the frozen copy is exactly two added lines at `measure.py:358-359`: `if len(declared) != unique: problems.append("duplicate case names")`.
- The pre-repair bytes are pinned and verified: `.ufo/waves/round-15/frozen/measure-before.py` sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`. This equals `git show 6e348e2:…` (manifest source commit), `git show e545ed9:…` (measured commit) and `git show 06cc6db:…`.
- `acceptance.json` (committed in 06cc6db, unmodified) lists `.ufo/waves/round-14/measure.py` as the command path. Re-running that path now executes the repaired runner, not the measured one. Output schema `kama-round-14-measure/v1` is unchanged, so output alone cannot show which version ran.
- Recommendation: the appended round-15 record must state both hashes and the mapping: receipt path → measured commit `e545ed9` → pre-repair sha `fda61e…`; and the repaired sha after final edit. It must not imply the old receipt was produced by the repaired file. The current `46c5866…` is in-flight and must be re-read after the final edit.
- Note: the frozen manifest pins `source_commit` 6e348e2, while the measured commit is e545ed9. Bytes are the same; the record should name both.

### F3 — medium (pending close-out): S012 `used-by` change lacks old→new record

- `corpus/SOURCES.md` line 24 (S012) differs from HEAD in one cell: `used-by` gains `corpus/lessons/round-15.md`. `cmp` reports the first difference at char 6726, line 24; the row is otherwise unchanged.
- Round-14 rules allow only `used-by` changes, recorded old→new (`round-14-verifier-spotcheck.md` discernment and source sections). `corpus/lessons/round-15.md` names S012 in prose but records no old→new for the `used-by` cell.
- The new value is a lesson path, while all previous `used-by` entries point to `corpus/knowledge/` files. Either record it as a deliberate category change or drop it.
- Pending: LOG round-15 says source handling is "recorded after integration". Not a failure yet.

### F4 — low: repaired duplicate definition is narrower than the prose promise

- Live `corpus_problems` (`.ufo/waves/round-14/measure.py:350-364`) builds `declared` only from `str` names with non-empty `strip()`. Duplicates are therefore detected only among non-whitespace string names. Whitespace-only and non-string `name` values are excluded from both `declared` and `unique`, and `case_name` shows them as `case-NN`.
- Consequence: two whitespace-only names, or two non-string names, pass the repaired guard. That is consistent with CorpusIdentity advice point 5, but the round-15 lesson and SKILL section say "rejects duplicate declared names" without this scope.
- Raw duplicate JSON keys are not inspected (`json.loads` keeps the last value). Documented as a limitation in CorpusIdentity; the round-15 text should say the same.
- Recommendation: the shared fixture schema must not use whitespace-only or non-string names as invalid duplicate controls unless the guard is extended. State the duplicate scope precisely in the corrected text.

### F5 — low/info: frozen-copy line references in the round-15 docs

- Round-15 advice and the lesson cite `measure.py:13–14,77`. Verified: line 14 is the duplicate promise in the docstring and line 77 is the `LIMITS` string. The lesson's "R1" reference to `corpus_problems():350–362` is correct for the pre-repair copy.
- Repaired-file lines shift by two lines after 358. Any appended correction citing post-repair lines must use the repaired numbers.

## Verified intact (executed reads and hashes only)

| Item | Check | Result |
|---|---|---|
| `.ufo/waves/round-14/acceptance.json` | `git status`; `ok`, `errors`, runs | Unmodified. `ok: true`, `errors: []`, `measured_commit` e545ed9…, `recorded_at` 06:38:39.98Z (27 s after e545ed9 at 03:38:12−03:00). |
| acceptance per-run recount (`records[].parsed.records`) | counts | capability_absent exit 1, 0 passed / 51 failed; precedence_red exit 1, 49 / 2; final_corpus exit 0, 51 / 0; selftest exit 0, 51 / 0. Unique names 51 in each run. Causal red is a separate key, exit 1. |
| acceptance `records[].command` | paths | Absent-tool path `.ufo/waves/round-14/frozen/before/tools/…` does not exist (`frozen/` holds only `precedence-*`). Commands use `/usr/bin/python -I -B`, while LOG/SKILL say `python3`. Equivalent; minor wording. |
| tool/cases at measured commit | blob hashes | `tools/kama-ollama-evidence.py` at e545ed9 = `38d1f5d2…` = current; `tests/ollama-evidence/cases.json` at e545ed9 = `4a4de0b8…` = current. Neither is in `git status`. |
| `.ufo/waves/round-14/frozen/precedence-before.py` | sha256 | `6e1c4ba5…`, matches `precedence-before-manifest.json`. |
| `.ufo/waves/round-14/frozen/precedence-only-red.py` | sha256 | `e3123a94…`, matches `precedence-only-red-manifest.json` `derived_sha256`. |
| Round-14 lessons, spot-check, rulings, claims, record, preservation, census/validate JSON | `git status` | Unmodified. |
| `corpus/lessons/round-14-verifier-spotcheck.md` R1 | text | Matches live code: the duplicate check is absent in pre-repair `corpus_problems`. Spot-check was non-author; I did not re-run its recounts. |
| SKILL.md | `cmp` against HEAD | HEAD (37,580 bytes) is a byte prefix of working tree. The added trailing newline and round-15 section are appended, so the prefix is preserved. |
| LOG.md | `cmp` against HEAD | HEAD (57,305 bytes) is a byte prefix of working tree. Round-15 entry appended. |
| Prose promise audit | grep for "before any child" / "duplicated corpus" | Only `measure.py` docstring/LIMITS, the inherited `acceptance.json` limits and round-14 advice `Harness.md:35` (which states the 16-unique floor only). No other prose repeats the false duplicate promise. |
| Round-14 `LOG.md` and `SCORECARD.md` entries | read | Consistent with receipt: 51/51 final, 49/2 draft, selftest clean, one provider-failed scout with no replacement. |
| Round-14 `integration-review.json` `dead_seats` | read | `KamaR14.ExistingProbe`, `Cursor RESOURCE_EXHAUSTED; provider unreachable`. Consistent with R2 wording; committed `advice/ExistingProbe.md` exists. |

## Pending (in flight; not final failures)

- `tests/ollama-corpus-guard/` exists (12 JSON files, untracked, created 05:09). `check.py` is not present yet. Fixture schema check of four files read in full:
  - `AppendDuplicate.json`: 4 entries. Invalid controls: 16 distinct stripped names + one duplicate (n00). Valid controls: 16 unique.
  - `ValidBoundaries.json`: 7 entries. Valid: 16, 32, object-16, and 16 + `N00` (case-significant, accepted). Invalid: 16 distinct + exact duplicate at last or first position.
  - `WhitespaceCollision.json`: 4 entries. Invalid: n01..n16 + `" n04 "`, which strips to 16 distinct; valid: 16.
  - `ObjectEnvelope.json`: 3 entries. Invalid: 16 distinct + n14 duplicate, adjacent or trailing; valid: 16.
  - Not yet read: `AdjacentDuplicate`, `DistantDuplicate`, `MiddleDuplicate`, `MultipleDuplicates`, `PrependDuplicate`, `TabCollision` (733 bytes, check its distinct count), `TriplicateName`, `UnicodeDuplicate`.
- Repaired `measure.py` is in the working tree; its final sha is not yet fixed (see F2).
- `corpus/lessons/round-15.md` is untracked and records R1/R2 correction text. The S012 `used-by` old→new record (F3) is still needed.
- LOG round-15 entry lists source handling, actual commands and measured revision as "recorded after integration". Pending.

## Residual risk and verification gaps

- I did not verify the spot-check's claim that the classifier selftest independently checks duplicates at `tools/kama-ollama-evidence.py:359-365`. It is about classifier duplicate selection, not corpus names, and is out of this review's scope.
- Python `str.strip()` and `isspace()` semantics are as documented in CorpusIdentity; not executed here.
- No Unicode-form or case-fold checks were run; the corpus is ASCII.
- Round-14 receipts are evidence of the 51-case run at e545ed9. They are not a fresh measurement of the repaired runner.

## Tooling

No tools installed or updated. Only pre-existing git, sha256sum, cmp, diff and read tools were used.

Report: .ufo/waves/round-15/build/advice/ReceiptReview.md
