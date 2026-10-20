# AttackClaim — executable guard repair versus repeated wording

## Axes and bounded conclusion

- **Calibration (assigned lowest axis, 7):** the relevant improvement is enforcing an already-written measurement precondition, not adding another sentence or improving Ollama classification policy. Numeric calibration remains **7 → 7**.
- **Operability (assigned axis, 8):** valid, sufficiently large, distinct-name corpora must still reach the real classifier CLI. A blanket rejection is not a repair.
- **Provenance / claim integrity:** preserve the historical receipt and frozen source; distinguish a newly enforced guard from runtime restoration, new classifier repertoire, broader semantic coverage, or independent judgment.

The frozen source supplies a concrete behavioral counterexample to its own existing promise. The current source contains the minimal executable correction. This supports a substantive **guard-enforcement** claim by static inspection; this report does not establish an exercised before/after result or an admission verdict.

## Strongest falsifiable counterexample

Clone the first literal fixture in `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json:2-17` once per name below, changing **only** each fixture's `name`:

```json
["n00", "n01", "n02", "n03", "n04", "n05", "n06", "n07", "n08", "n09", "n10", "n11", "n12", "n13", "n14", "n15", "n00"]
```

Use either the supported array envelope or an object containing that array under `cases`. There are **17 fixtures and 16 distinct stripped names**. The minimum-size condition therefore cannot explain rejection.

Static predictions, not executed observations:

1. **Frozen before:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:350-362` computes `unique == 16` and returns no corpus problem. With an existing, launchable tool and successful temporary staging, its `run()` reaches `measure_case()` for every fixture (`:365-383`). The classifier subprocess is reached by that path in the original runner (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:211-251`). Thus duplicate names do not prevent classifier-child launch. **[INFERENCE]** A matching classifier would also allow all 17 cloned positive cases to pass; that full outcome was not measured here.
2. **Current source:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:350-364` now adds `"duplicate case names"` when `len(declared) != unique`. Its `run()` (`:367-397`) emits unmeasured records from the corpus-error branch instead of entering `measure_case()`. The expected result is exit 1, `unique_case_names == 16`, total/failed 17, passed 0, a corpus error containing that stable reason, and zero runner-spawned classifier children. The unmeasured-record definition (`:159-176`) retains null observed process fields.
3. **Valid paired control:** remove only the last `"n00"`. The remaining 16 distinct names must not trigger either corpus check and must reach the existing measurement path. A functioning classifier should yield 16 measured passes; no pass result is claimed here.

The committed matrix `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/AppendDuplicate.json:1-96` already expresses these exact invalid/valid counterparts for both envelopes. Its invalid controls have 16 unique stripped names, so they discriminate the new duplicate predicate from the old minimum guard.

## Why this is not another wording-only correction

The old promise is already explicit in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:13-14,73-78`: duplicated corpora fail before any child runs. Restating that promise changes nothing about the 17-fixture counterexample. The frozen implementation checks only the number of distinct names; the current implementation checks both distinct-name minimum and presence of duplicates. The changed execution branch, not a new wording count, is the falsifiable delta.

The smallest safe source correction is the two-line predicate now present at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:358-359`, retaining the existing stripped-name collection, minimum check, schema, classifier policy, and pre-child corpus gate. No additional normalization or validation is needed for this claim.

## Counterexample to an overbroad calibration claim

The valid paired control intentionally repeats the **same captured metadata and expected finding 16 times under different names**. It is admissible under this name-uniqueness contract. Consequently, a successful guard demonstration does **not** show semantic independence of the fixtures, improved constant-answer resistance, additional classifier edge coverage, better model quality, or serving readiness. Rejecting those renamed copies by content would instead change the contract and break the required valid control.

This is a claim-scope boundary, not a reason to add content hashing or new classifier policy. The smallest safe reporting correction is:

> Enforced the existing stripped-case-name uniqueness precondition: a duplicate beyond 16 distinct names is rejected before classifier-child launch, while a valid distinct-name corpus remains measurable. Calibration stays 7; no runtime or classifier-policy improvement is claimed.

Keep the original replay capability and its earlier 51-case result historical. `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:407-432,443-451` already limits that capability to offline metadata and holds calibration at 7. A guard fix does not re-earn the repertoire entry or rewrite the old receipt.

## Evidence boundary and smallest remaining recommendation

- The before/after comparison must use the **same name-only-mutated cases** with explicit runner/tool selection. An absent-tool before run, a corpus with fewer than 16 unique names, or changed classifier expectations cannot demonstrate this bug.
- Zero wrapper-marker writes alone means no observed wrapper execution, not independently observed absence of every possible child process. Support the precise claim with the pre-child branch/source evidence above and the paired positive control that proves the marker mechanism is exercised. State “runner-spawned classifier child” rather than incorrectly counting the externally launched runner itself as forbidden.
- Main should retain per-case subprocess/JSON evidence for the invalid and valid controls before claiming an exercised delta. This leaf ran no verification commands.

## Scope and limitations

Read-only source, fixture, frozen-manifest, scorecard, quality-criterion, and assignment-artifact inspection; only this report was written. The guard was observed in current source, and the AppendDuplicate matrix was read. The planned harness path `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/check.py` was not present when inspected, so its eventual implementation and results are outside this review. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/manifest.json:1-5` declares a source commit/path/digest; no independent digest or commit verification was performed. No probes, tests, builds, linters, formatters, smoke runs, runtime invocations, installs, host mutation, source edits, or admission/judgment were performed.

Report: .ufo/waves/round-15/build/advice/AttackClaim.md
