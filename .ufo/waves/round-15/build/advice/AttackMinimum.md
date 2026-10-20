# AttackMinimum — minimum-floor masking review

## Finding

Yes: the old minimum guard can hide missing duplicate detection in a test suite. A duplicate control containing fewer than 16 distinct stripped names fails even when no duplicate check exists. Its rejection therefore does not establish duplicate detection. This is a fixable guard/test-isolation defect, not a justified tradeoff or an admission verdict.

## Named review axes

- Duplicate rejection independent of the existing 16-unique-name floor.
- Fail-closed rejection before any classifier child starts.
- Preservation of valid unique-corpus measurement and existing stripped-name identity.
- Evidence/scope integrity: executable guard repair only; Numeric7 stays7, with no runtime-restoration or score claim.

## Local evidence

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:350-362`: the inspected implementation collects nonempty string names using `strip()`, computes `len(set(declared))`, and appends a problem only when that count is below 16. There is no duplicate predicate in this function.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:350-362`: the frozen baseline contains the same minimum-only guard.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:365-383`: corpus problems select unmeasured records; otherwise a present tool selects the per-case measurement loop. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:211-251` shows that valid case data reaches `subprocess.run` after staging.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json:2-17`: the first fixture, `loaded_same_digest`, supplies the complete capture/expectation payload for name-only controls. Its expected child exit is 0. This review did not execute or independently certify that fixture.

## Falsifiable counterexample

Clone that first fixture for every literal name below, changing only `name`. Use the prescribed fixture schema:

```json
[
  {
    "name": "minimum_floor_must_not_mask_duplicate",
    "names": ["n01", "n02", "n03", "n04", "n05", "n06", "n07", "n08", "n09", "n10", "n11", "n12", "n13", "n14", "n15", "n16", "n01"],
    "envelope": "array",
    "expected_rejected": true
  },
  {
    "name": "same_size_unique_control",
    "names": ["n01", "n02", "n03", "n04", "n05", "n06", "n07", "n08", "n09", "n10", "n11", "n12", "n13", "n14", "n15", "n16", "n17"],
    "envelope": "array",
    "expected_rejected": false
  }
]
```

The negative has 17 rows and exactly 16 distinct stripped names; its late duplicate cannot be caught by the old minimum floor. [INFERENCE] The inspected baseline returns no corpus problems and, with the real tool present and staging successful, enters child measurement. The repaired runner must instead report corpus rejection with zero child launches. The positive has the same row count and payload, so rejecting it would expose a blanket size/content restriction rather than a correct name-uniqueness repair.

A weak alternative—16 rows with one repeated name and only 15 distinct names—does not distinguish the baseline from a repaired runner. A nonzero exit alone is also insufficient: child failure or a missing tool can produce failure without proving the pre-child guard.

## Smallest safe correction

1. Keep the existing minimum floor and add an independent duplicate check over the same stripped-name collection, for example `len(declared) != unique`, before the existing child-measurement branch. Do not change name identity to raw strings, case folding, or capture equality.
2. Retain at least the paired controls above; mirror the duplicate control in the supported object envelope. Whitespace-collision negative controls likewise need at least 16 distinct stripped names.
3. Have L1's authorized verification establish zero child launches for invalid corpora, plus actual successful child measurement for valid controls. Assert corpus-specific rejection, not merely a failing exit code. The baseline counterexample should demonstrate that this is a real regression test rather than coverage of the old floor.

## Limitations

Read-only advisory review, apart from this assigned report. No probes, tests, builds, linters, smoke runs, separate runtime, installs, source edits, or fixture edits. The planned `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/` directory was absent when inspected; no final sibling fixture/harness or final repair was reviewed. All behavioral predictions above are static inferences, not measured results. Canonical judgment remains outside this review.
