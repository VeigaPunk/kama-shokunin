# LedgerR1 — attack on the appended R1 correction against the old promises

Seat: `KamaR15.LedgerR1` (leaf, no subagent dispatch). Candidate: commit `70af36c` (HEAD, "round-15: enforce duplicate corpus admission before replay children"); working tree clean at read time. Scope: correction prose versus the old "duplicated corpora fail before any child runs" promise, and whether any old receipt is implied altered. No gate, test, runner, child process or fixture run. No installs or updates.

Disclosure: to check the predicate I evaluated the committed `corpus_problems` function body (`.ufo/waves/round-14/measure.py:350-364`) in-process on hand-written name lists. No runner, child, classifier, `check.py` or fixture file was executed. The same results follow from reading lines 352-364 and 131-136.

## Verdict

- **No old receipt is implied altered.** Confirmed by digest and by the git diff.
- **The false promise is accurately described for its stated class.** Confirmed.
- **The corrected promise is stated more broadly than the guard delivers.** Blank or missing fixture names escape the duplicate guard. Lesson `corpus/lessons/round-15.md:90-92` discloses this, but the knowledge correction, SKILL, and KQ18 do not.

## Evidence that holds (no finding)

| Claim | Evidence | Result |
|---|---|---|
| Receipt bytes unchanged | `sha256(.ufo/waves/round-14/acceptance.json)` = `fdf90a5d…cc612`, 303269 bytes; `git show HEAD:` and `git show 6e348e2:` give the same digest; `git diff 6e348e2 70af36c -- .ufo/waves/round-14/acceptance.json` is empty | Byte-identical |
| Old runner preserved | `.ufo/waves/round-15/frozen/measure-before.py` = `fda61e…4b60d`; blob `783004569af9072a…` at `e545ed99`, `6e348e28`, and `70af36c`'s parent chain | Matches the named baseline |
| Committed repair is minimal | `git diff --numstat 6e348e2 70af36c -- .ufo/waves/round-14/measure.py` = `2 0` (two insertions, zero deletions) | Only the duplicate predicate added |
| Prose edits are append-only | `ollama-evidence-replay.md` 51 insertions / 0 deletions; `SKILL.md` diff removes only the trailing-newline on the last line, then appends a section | No old prose rewritten |
| Receipt locators in lesson | `acceptance.json` has no top-level `limits`; `records[0..2].parsed.limits[3]` and `causal_red.parsed.limits[3]` carry the sentence; `records[3]` (child selftest) does not | Lesson lines 103-109 are exact |
| Receipt denominator | `records[0..2].parsed` and `causal_red.parsed` all show `total: 51`, `unique_case_names: 51`; `records[3]` has no unique field | Matches the lesson wording within rounding of "runs" |
| Receipt corpus = present corpus | receipt `cases_sha256` = `4a4de0b8…158ae4` = current `tests/ollama-evidence/cases.json`; in-memory recount of that file: 51 entries, 51 unique stripped names, 0 blank/missing | Independent recount agrees |
| Original promise false for its class | Frozen `corpus_problems` checks only `unique < 16` (`git diff` shows the duplicate check is the sole addition); `run()` `:374-385` calls `measure_case` per fixture when `corpus` is empty | ≥16 distinct names + one repeated name spawns children, as stated |
| Corrected guard ordering | `measure.py:358-359` duplicate check precedes `:360` minimum check; `:377-380` corpus branch skips children for every fixture | Matches "before the minimum check and before any child" |

## Findings

### F1 (medium) — corrected promise overstated for blank or missing names

Mechanism:
- `measure.py:353-355` counts a name only when `isinstance(name, str) and name.strip()`. Blank, whitespace-only, non-string, or absent names never enter `declared`, so they are never compared.
- `measure.py:131-136` `case_name` labels such fixtures `case-NN`.
- `measure.py:211-214` `measure_case` runs `case_problems`, which (`:139-150`) validates `expect`, `expected_exit`, and `expected_finding` only, not `name`.
- So a corpus with 16 distinct non-blank names plus two fixtures named `""` gets `corpus_problems → ([], 16)` and both fixtures reach `measure_case`, and therefore child processes, under the committed repair. (In-memory evaluation of the committed predicate: `(['duplicate case names'], 16)` for a repeated name; `([], 16)` for two blank names and for two nameless fixtures.)

Where the text overstates:
- `corpus/knowledge/ollama-evidence-replay.md:349-355`: "Only the generalized 'duplicated corpora fail' guarantee was wrong." This implies the rest of the promise is correct. It is not, for blank-named duplicates.
- `SKILL.md:487-490`: "Corpus identity is the existing runner's `name.strip()` convention … The preflight rejects duplicate declared names." "Declared" is the only qualifier and it is not defined.
- `corpus/QUALITY.md:87` (KQ18): admission requires "name injectivity over stripped names". Two fixtures named `""` share stripped name `""` and are not rejected, so injectivity over stripped names is not enforced for all fixtures.
- `corpus/knowledge/ollama-evidence-replay.md:332-334`: "rejects any repeated declared name" is accurate but the blank exclusion is not stated alongside it.

Where the scope cut is disclosed: `corpus/lessons/round-15.md:88-92` ("Missing/blank/non-string fixture-name validation … explicitly outside the declared R1 duplicate-declared-name repair"). `WhitespaceReview.md:16` and `TailCaseReview.md:39-44` identified the same gap and recommended rejecting blank names; no such change exists in `70af36c`.

Consequence: the lesson is honest; the knowledge file, SKILL, and KQ18 are not. A reader of the knowledge entry alone would conclude the duplicate class is closed. Whether blank-named duplicates count as "duplicated corpora" under the old wording is arguable; the lesson's own exclusion is the authority for the current scope. Fail-closed hardening of blank names would be new scope, not part of R1, and is not recommended here.

### F2 (low) — no reverse pointer from superseded text to the correction

- `grep -rn round-15 .ufo/waves/round-14` (excluding `advice/`) returns nothing. The receipt cannot carry prose, so this is expected for JSON.
- `corpus/lessons/round-14.md` contains no pointer to `round-15.md`'s named correction. `round-14-verifier-spotcheck.md` is outside-authored and read-only, so it is excluded from this finding.
- `.ufo/waves/round-14/measure.py:14` and `:77` now carry the generalized wording, which is true for declared-name duplicates but still not for blank names (F1). Nothing in that file's neighborhood points to the correction.
- The correction runs one way: lesson to receipt locators. Someone reading the receipt or round-14 lesson, which are the superseded texts, is not directed to the correction.

### F3 (nit) — misquote of the docstring

`ollama-evidence-replay.md:325-327` attributes the quoted phrase "narrower or duplicated corpora fail before any child runs" to "docstring and `LIMITS`". That exact phrase is `LIMITS[3]` only (`measure.py:77`). The docstring (`:13-14`) reads "a narrower or duplicated corpus fails the whole measurement before any child is spawned."

### F4 (nit) — imprecise locator in the summary sentence

`corpus/lessons/round-15.md:34` says the correction covers "the inherited `acceptance.json` limits". The precise locator is `records[0..2].parsed.limits[3]` and `causal_red.parsed.limits[3]`, which the lesson gives correctly at `:103-106`. No defect; the summary wording could cite the locator. The `R1Correction.md` draft's phrase "total: 51, unique_case_names: 51 in the runs" includes `records[3]`, which has no unique field.

## Limits

- F1 is a static reading plus an in-memory evaluation of the committed predicate. No runner or child was executed; the blank-name path was not observed end to end.
- Whether blank-named duplicates are within the old promise's meaning is an interpretation question; this report does not rule on it.
- This report does not assess `tests/ollama-corpus-guard/check.py` matrix coverage, the frozen red manifest, or source-census state; those belong to other seats.
- Out of scope: the `SOURCES.md` S012 used-by cell change (sanctioned by `round-15.md:67-70`); R2 provenance text.
- Tools: none installed or updated.
