# R1 historical receipt/prose correction — advisory draft

Author: `KamaR15.R1Correction-3` (leaf advisory seat). Scope: draft the appended R1 correction only. No old receipt, lesson, runner, fixture or sibling file was edited. No runner, selftest, build, lint or test was executed. Read-only inspection only; no tool was installed or updated.

## Findings

1. **Historical receipt is `.ufo/waves/round-14/acceptance.json`.** sha256 `fdf90a5d0886b1f501a67a168a20a4b5a22cfa56fca58aad45eb33757edcc612`, 303269 bytes, identical to `git show HEAD:` (verified by hash). It is a JSON object with keys `measured_commit`, `recorded_at`, `records`, `expected_finding_histogram`, `constant_answer_maximum`, `oracle_note`, `ok`, `errors`, `causal_red`. It has **no top-level `limits` key**. The false promise is embedded in each run's stdout JSON:
   - `records[0].parsed.limits[3]` (absent-tool baseline)
   - `records[1].parsed.limits[3]` (preserved draft)
   - `records[2].parsed.limits[3]` (final corpus)
   - `causal_red.parsed.limits[3]`
   - Text: `the case document must declare at least 16 unique fixture names; narrower or duplicated corpora fail before any child runs`
   - `records[3]` is the child selftest and does not carry it.
   - The receipt's own fields show `total: 51`, `unique_case_names: 51` in the runs.
   - Appending prose to this JSON would change its bytes and break parsing, so the correction must go in the lesson (append point below).

2. **Original runner.** `.ufo/waves/round-14/measure.py` at committed HEAD has sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, byte-identical to `.ufo/waves/round-15/frozen/measure-before.py`. The false promise sits at docstring lines 13–14 and `LIMITS[3]` (line 77). `corpus_problems` (lines 350–362) tests only `unique < MINIMUM_UNIQUE_CASES` (16). `run()` short-circuits to `unmeasured_record` only when `corpus` is non-empty (line 375); otherwise every fixture goes to `measure_case`. Static reading: a corpus with ≥16 distinct stripped names plus a repeat passes the guard and spawns children. Not executed.

3. **Working tree is mid-repair (sibling edit, uncommitted).** `.ufo/waves/round-14/measure.py` now has sha256 `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`. `diff` against the frozen original shows exactly the insertion at lines 358–359: `if len(declared) != unique:` / `problems.append("duplicate case names")`. The appended text below must not describe that repair as verified or committed until red/green evidence exists.

4. **Existing round-15 lesson draft.** `corpus/lessons/round-15.md` (untracked, lane-owned, modified 05:03) already has `### Named historical correction — R1` at lines 32–34. Its claim is correct. Its locator "inherited `acceptance.json` limits" is imprecise because there is no top-level `limits` key. The addendum below supplies exact locators. Lines 32–34 should stay unchanged; the instruction is to append.

5. **Other prose.** `corpus/lessons/round-14.md` does not contain the duplicate promise (grep: no "before any child" match), so it needs no correction. `SKILL.md` lines 479–501 already carry a paragraph stating the promise was false and naming the R1 correction (sibling-authored, present in working tree). That paragraph names `tests/ollama-corpus-guard/check.py`, which **does not exist yet** (`tests/` contains only `ollama-evidence/`). The paragraph is true only after the guard owner creates it. Round-14 `advice/*.md` files are historical advisory prose; none reviewed asserts the duplicate promise except `advice/Harness.md:35–38`, which says "unique", not "duplicate", so it is not a false promise.

6. **Selftest locator.** The spot-check cites `tools/kama-ollama-evidence.py:359–365` for the duplicate check. The actual duplicate check is lines 364–365 (`if len(names) != len(set(names))`); 359–363 are the minimum-count early return. Minor; use 364–365 if cited.

## Draft: exact text to append at END of `corpus/lessons/round-15.md`

Apply after the lesson owner finishes writing. Append as-is, preceded by one blank line. Do not edit lines 32–34.

```markdown
### Named historical correction — R1 locator addendum

This addendum adds exact locators to the R1 correction above. It changes no recorded output and rewrites no old bytes.

Old bytes pinned at drafting time:

- `.ufo/waves/round-14/acceptance.json`, sha256 `fdf90a5d0886b1f501a67a168a20a4b5a22cfa56fca58aad45eb33757edcc612`, 303269 bytes, identical to committed HEAD. It has no top-level `limits` key. The false promise is embedded in the stdout JSON of four recorded runs: `records[0].parsed.limits[3]`, `records[1].parsed.limits[3]`, `records[2].parsed.limits[3]`, and `causal_red.parsed.limits[3]`. The text is "the case document must declare at least 16 unique fixture names; narrower or duplicated corpora fail before any child runs". `records[3]` is the child selftest and does not carry it.
- `.ufo/waves/round-14/measure.py` at committed HEAD, sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, byte-identical to `.ufo/waves/round-15/frozen/measure-before.py`. Its docstring lines 13–14 and `LIMITS[3]` at line 77 carry the duplicate promise. `corpus_problems` at lines 350–362 tests only `unique < MINIMUM_UNIQUE_CASES` (16).

Mechanism, from static reading of the frozen original and not executed in this addendum: a corpus with at least 16 distinct stripped names and one repeated stripped name passes `corpus_problems`. `run()` then takes the `elif tool_present:` branch and calls `measure_case` for every fixture, including the repeated one. The statement "fail before any child runs" was therefore false for that class of corpus.

Not retracted: the recorded 51-case receipt. Its runs record `total: 51` and `unique_case_names: 51`; the duplicate-admission gap did not affect those recorded results. The receipt bytes stay as committed. A JSON receipt cannot take an appended prose footer without changing its bytes, so this lesson is the append point.

Limits of the repair. The duplicate check the round-15 guard adds must be described with these limits, and none of them is claimed as verified here:
- Comparison uses stripped names only (`str.strip()`). No Unicode normalization or case folding is applied.
- A fixture whose `name` is absent, non-string or blank is excluded from the count and is not rejected by the duplicate check. It still reaches child measurement under the generated label `case-NN`.
- `json.loads` keeps the last value of a repeated `name` key inside one fixture. The guard cannot see the earlier value.

Red-before and green-after evidence for the repaired guard is recorded by the round-15 guard check, not by this addendum. Until that evidence is committed, the repaired runner is not claimed as verified.
```

## Limitations

- Mechanism claim (duplicates spawn children under the original) is static reading; not executed.
- Read the sibling's working-tree diff only; did not verify its correctness or the stripped-name logic beyond the diff.
- Did not recount `tests/ollama-evidence/cases.json`; uniqueness rests on the receipt's own `unique_case_names: 51` fields and the spot-check's recount, both cited as observed.
- Contract names `tests/ollama-corpus-guard/*.json` fixtures and a `check.py` gate; neither directory exists in the repo now (only `tests/ollama-evidence/`). Reported, not created.
- R2 (partial-output clarification) is out of this seat's scope and not drafted here.
- Tooling: none installed or updated. Pacman/uv not used.

Report: .ufo/waves/round-15/build/advice/R1Correction.md
