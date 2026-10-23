# Round-30 lesson: appended correction records

These four records are proposed additions for integration; `corpus/lessons/round-30.md` was not edited. Git evidence was read in the scratch clone checked out at `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`, using historical commit `043ba425` where noted.

## Correction record 1 — routed defect 1: omitted landed commits

Add these two commits to the round-31 report's Landed-changes table, which the spot-check found incomplete:

| Commit | Committer time | Subject |
|---|---|---|
| `f41dce3` | `2026-10-23T17:13:51-03:00` | `round-30: late control evidence (CtlEditInPlace, CtlTamper, CtlDoNothing, CtlBaseTree variants) and wave registry; summary correction` |
| `043ba425` | `2026-10-23T17:16:02-03:00` | `round-30: lesson calibration note from the CtlEditInPlace arm (what carries the append-only rejection)` |

One-command proof (exit 0):

```sh
git -C /tmp/r31w1-ExecRepairLesson30 log --format='%h %cI %s' 52ac3af8..043ba425
```

Observed output for the omitted rows is exactly the two table rows above; the command returned eight commits in the range.

## Correction record 2 — routed defect 5: Mistakes receipt pointers

Append this correction to `## Mistakes` without changing its original rows:

- **Row 1:** The initial `could-not-evaluate: oracle .ufo/waves/round-29/w1/out/RecallA/missed.json missing at tip` run has no committed receipt. `.ufo/waves/round-30/c1/preliminary/` is a directory, not a receipt path; its committed entries are `bound68.json`, `duplicate-ids.json`, and `long-digest-fix.json`. The committed search has no `missing at tip` match. Preserve the first-run result only as an unretained observation reported in `corpus/lessons/round-30-verifier-spotcheck.md:70`; do not present it as receipt-backed evidence.
- **Row 3:** `long-digest-fix.json` is the post-fix result, not the bound-68 result. Replace that pointer for the bound-68 reading with `.ufo/waves/round-30/c1/preliminary/bound68.json`. Its exact fields are `"oracle_items": 72`, `"oracle_bound": 68`, `"oracle_unbound": 4`, `"statements": 137`; `long-digest-fix.json` instead has `"oracle_items": 72`, `"oracle_bound": 72`, `"oracle_unbound": 0`, `"statements": 141`.

One-command proof (overall exit 0; the expected no-match search exits 1):

```sh
git -C /tmp/r31w1-ExecRepairLesson30 ls-tree -r --name-only 043ba425 -- .ufo/waves/round-30/c1/preliminary && { git -C /tmp/r31w1-ExecRepairLesson30 grep -n -F 'missing at tip' 043ba425 -- .ufo/waves/round-30; grep_rc=$?; test "$grep_rc" -eq 1; } && git -C /tmp/r31w1-ExecRepairLesson30 show 043ba425:.ufo/waves/round-30/c1/preliminary/long-digest-fix.json && git -C /tmp/r31w1-ExecRepairLesson30 show 043ba425:.ufo/waves/round-30/c1/preliminary/bound68.json
```

Observed: the preliminary listing contains only those three files; the search has no output (exit 1); the two receipts contain the exact field values stated above (both `git show` commands exit 0). The missing-receipt limitation is also explicitly recorded by the closure at `corpus/lessons/round-30-verifier-spotcheck.md:70`.

## Correction record 3 — routed defect 6: draft the Gate rejection rows

Add a separate rejection table under `## Gate` (these decisions are not SOURCES admissions):

| Decision | Kind | Committed evidence | Observed basis |
|---|---|---|---|
| `tests/ollama-corpus-guard/check.py` refused as the C2 agreement subject | reject | `.ufo/waves/round-30/c2/receipt-b-corpusguard-refused.json` | `runs=3`, `agree=1`, `disagree=2`, `verdict=disagree`; the output embeds a staging path and patched-wrapper digest, so refusal is retained rather than normalized away. |
| `CtlEditInPlace` rejected | reject | `.ufo/waves/round-30/controls/CtlEditInPlace/counter.out` | `append_only False … unresolved 141 met False`; the append-only byte-prefix rule rejects the in-place rewrite. |

One-command proof (exit 0):

```sh
git -C /tmp/r31w1-ExecRepairLesson30 show 043ba425:.ufo/waves/round-30/c2/receipt-b-corpusguard-refused.json && git -C /tmp/r31w1-ExecRepairLesson30 show 043ba425:.ufo/waves/round-30/controls/CtlEditInPlace/counter.out && git -C /tmp/r31w1-ExecRepairLesson30 show 043ba425:.ufo/waves/round-30/controls/SUMMARY.md
```

Observed receipt values: `agree=1`, `disagree=2`, `runs=3`, `verdict=disagree`; the control output is `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only False valid_corrections 11 false_corrections 0 unresolved 141 met False tip 98544b06ee20` (`exit=0`). `controls/SUMMARY.md` labels this the late CtlEditInPlace correction 4.

## Correction record 4 — routed defect 7: frozen counter docstring drift

Record this as a limit of round-30's frozen counter, for round 31 to cite; do not edit the frozen counter. Its docstring describes only `## Round 29 — self-assessment corrections` and `SA29:<sid>`, while the code's `HEADINGS` also contains `## Round 30 — self-assessment corrections` and its prefix loop accepts both `SA29:` and `SA30:`.

One-command proof (exit 0):

```sh
git -C /tmp/r31w1-ExecRepairLesson30 grep -n -E 'Round 29|SA29:|Round 30|SA30:|HEADINGS' 043ba425 -- .ufo/waves/round-30/count-c1.py
```

Observed lines: docstring line 45 names Round 29/SA29; code lines 84–85 include both headings; code line 486 accepts both prefixes.
