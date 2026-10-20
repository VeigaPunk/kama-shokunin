# SourceReview — S012 citation relevance vs guard policy inference (round 15)

Read-only review. No tests, builds, measure/check runs, census runs, or installs. Tools installed/updated: none.

## Bottom line

S012 is **not** used as support for the duplicate-corpus guard, and the round-15 lesson says so explicitly (`corpus/lessons/round-15.md:23`). S012 is cited only for the readiness/loaded-memory boundary, which the vendor page supports. One cited phrase overstates the page (F1). The remaining items are traceability, labeling, and pending in-flight work.

## Verified facts (this review)

- S012 page, fetched read-only (`https://docs.ollama.com/api/ps`, OpenAPI 3.1.0, info.version 0.1.0): summary "Retrieve a list of models that are currently running"; 200 description "Models currently loaded into memory"; `Ps` fields name, model, size, digest, details, expires_at ("Time when the model will be unloaded"), size_vram, context_length. The page contains no readiness, liveness, or serving-health semantics.
- `.ufo/waves/round-15/frozen/measure-before.py` sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` = `frozen/manifest.json` sha256 = `git show HEAD:.ufo/waves/round-14/measure.py` sha256 (HEAD `6e348e2`). Frozen baseline is intact.
- Original guard (`measure-before.py:350-362`): `corpus_problems` checks only `unique < MINIMUM_UNIQUE_CASES` (16). No declared-vs-unique comparison. This matches S034's claim text.
- Working tree `.ufo/waves/round-14/measure.py` is modified (in flight, sha256 `46c5866d…5257`). Its diff adds `if len(declared) != unique: problems.append("duplicate case names")` at lines 358–359, before the minimum check. `run()` calls `corpus_problems` (line 372) before any child loop (lines 377–385), so a corpus-level problem produces unmeasured records with no child spawned.
- `tests/ollama-corpus-guard/` has 12 JSON fixtures (in flight). `check.py` does not exist yet.

## Findings

### F1 — low, citation accuracy (actionable now)
- `corpus/lessons/round-15.md:18`: "Reopened S012 documents loaded memory only."
- "Only" is not supported. The page also documents expiry, VRAM, context length, digest, details and size. The supportable wording is: S012 documents a running-model list (200 description "Models currently loaded into memory"); it documents no readiness field or semantics.
- The same row's conclusion (loaded metadata ≠ readiness) is correct. Only the description of the source is overstated.
- Fix: replace the sentence with the 200-description and summary quotes, and drop "only".

### F2 — low, traceability (pending if the in-flight source edit has not landed)
- `corpus/SOURCES.md:24` (S012 row, git diff): `corpus/lessons/round-15.md` appended to `used-by`. The opened cell is unchanged, which is correct.
- The round-15 lesson has no old→new record of this used-by change, and the SOURCES search log has no round-15 entry for the S012 re-open. Round-14 recorded both (`corpus/lessons/round-14.md:66–73`; SOURCES search log line 63).
- Fix: add the old→new used-by record and the re-open search-log entry, including the located quote and access date. Do not edit the immutable cells.

### F3 — low, inference labeling
- S012 is not evidence for the guard's policy, and the lesson does not claim it is (`round-15.md:15` grounds the gate row in "Outside R1; existing runner's stripped-name policy; fixed new test expectations"). That is correct.
- The threshold `MINIMUM_UNIQUE_CASES = 16` and the rule "duplicate declared names are rejected" are lane policy with no vendor source. Nothing in round-15 says so. `corpus/knowledge/ollama-evidence-replay.md:35, 241–244` labels comparable lane rules as `[INFERENCE]` or lane policy.
- Fix: label the 16-minimum and the duplicate rule as "kama lane policy, not sourced" in the round-15 lesson gate or in SKILL §Round-15 (`SKILL.md:487–491`). The SKILL section already says identity is the runner's `name.strip()` convention, not Ollama normalization, so this is one clause.

### F4 — low, SKILL placement (optional)
- `SKILL.md:499–501` puts the S012 sentence inside the guard section. The wording "S012's loaded-memory documentation remains a limit, never readiness evidence" is explicit enough and is not guard support. An optional clarity edit is to say "readiness limit, not guard support" so a skimmer does not infer that S012 backs the guard.

### F5 — pending, new registry row S034 (needs an admission decision)
- `corpus/SOURCES.md:46`: S034, kind `own-work`, tier A, status `mined`, recheck `every round`, used-by `corpus/lessons/round-15.md`. It points at the frozen round-14 guard code.
- The round-15 gate does not admit or mention S034. The SOURCES search log has no round-15 entry that would justify it.
- Tier A for own-work is precedent in this registry (round 1: S001, S013–S015), but `QUALITY.md` KQ6 scopes tier A to vendor/spec statements, and S034 is a code provenance statement. This is a judgment call; it needs an explicit gate row or removal.
- `every round` passes the census `symbolic()` check (`scripts/sources-census.sh:582`), so there is no E09. The cadence is still meaningless for an immutable frozen baseline. A recheck of `on-change` or `on-release` fits better.
- The S034 claim is accurate: `measure-before.py:358–362` rejects only `unique < MINIMUM_UNIQUE_CASES`.

### F6 — pending, dangling criterion reference
- `corpus/lessons/round-15.md:29` says "new KQ18 records that gap". `corpus/QUALITY.md` ends at KQ17 (line 72). KQ18 is not written yet. This is an in-flight gap, not a final failure. Land KQ18 or remove the reference before the round closes.

### F7 — pending, in-flight guard fix (checked, correct so far)
- The in-flight `round-14/measure.py` duplicate check (lines 358–359) is in the right place. It runs before any child, and the minimum check still applies. Its docstring (`measure.py:13–14`) and `LIMITS` line 77 already state the duplicate-and-narrow promise.
- Pending: rerun-equivalent verification belongs to the main agent after edits. I did not execute it.

### F8 — limitation of the guard (not a contract breach)
- `declared` counts only non-empty string names after `strip()`. A fixture with a missing or non-string name is not counted as a duplicate or as a declared name. It becomes a per-case `invalid_record`, and the other valid cases still spawn children. The docstring promise covers duplicate and narrow corpora only, so this is consistent. Reviewers should not read "fails before any child" as covering invalid-name fixtures.
- Names are compared after `strip()` with no Unicode normalization. NFC and NFD forms of the same name count as distinct. `SKILL.md:487–489` states this explicitly, so it is a documented boundary, not a defect.

### F9 — pending, fixture controls (hand-counted; harness not yet present)
Schema shape matches the shared contract (`name`, `names`, `envelope`, `expected_rejected`). Distinct-name counts, by hand from the raw file contents:
- `AdjacentDuplicate.json`: invalid controls have n00–n15 with n05 repeated, 16 distinct, rejected. Valid controls have 16 distinct. Meets the ≥16 rule.
- `DistantDuplicate.json`: Array32 has 32 distinct plus a repeat at the end; Object16 has 16 distinct plus a repeat; ValidArray32Unique has 32 distinct. Meets the rule.
- `ValidBoundaries.json`: exactly-16 array and object accepted; 16 distinct plus `N00` accepted (case-sensitive, consistent with `SKILL.md:487–489`); 16 distinct plus an exact duplicate, first or last, rejected. Meets the rule.
- `UnicodeDuplicate.json`: 16 distinct including `名前`; duplicates appended, adjacent, or in object envelope rejected; valid versions accepted. Meets the rule.
- `WhitespaceCollision`, `TabCollision`, `ObjectEnvelope`, `PrependDuplicate`, `MiddleDuplicate`, `MultipleDuplicates`, `TriplicateName`, `AppendDuplicate`: not counted in this review. Pending for the harness/fixture reviewer.
- Not verifiable until the harness exists: that each fixture is byte-identical to the original `cases.json` except names and envelope; that object-envelope wrapping uses the existing `cases` key; that `check.py` runs the frozen runner. `SKILL.md:495–497` describes `check.py`, which is absent.

## Pending (not final failures)

- F2 (lesson/search-log entries for S012 used-by and re-open)
- F5 (S034 admission decision)
- F6 (KQ18)
- F7 (in-flight `measure.py` edit; main-agent verification)
- F9 (`check.py`, harness wrapping, full fixture audit)

## Verification gaps and limits

- No test, build, measure, census, or lint run (per assignment). Counts in F9 are hand counts from file contents, not tool output.
- S012 re-check was one read-only fetch of the page. I did not re-open S011, S031, or the other rows.
- The S012 quote "Models currently loaded into memory" is confirmed on the page. The exact 5-word count was not re-measured.
- The in-flight `measure.py`, SKILL, SOURCES, lesson and fixture contents may change before the main agent verifies; findings F5–F9 refer to the state at review time.
- Limitation of this review: the lane's round-15 `frozen/measure-before.py` and `manifest.json` were checked by sha256 only, not by behavior.
