# RV05TallyDiff — Round 64 wave f

Advisory review only; no claim-admission verdict. Axes: calibration (primary), operability (bounded execution). Reviewed base `0c1eff3c` → candidate `23b3fdb1a925129a9961cf551f6d40bf251602cb`, freeze and X07Tally report. All execution used the required shared scratch clone; no lane source edits, installs, live servers, or counter-wide run.

## Findings, severity ordered

### P2 — SCORECARD statement reader crosses non-round section boundaries

`tools/shortcut-tally.py:625-634` terminates a round only at the next matching `## Round N`, not the next same/higher-level Markdown heading. Therefore an unrelated appendix or subsequent top-level section becomes evidence for the preceding round. `:852-854` promotes that evidence to `disclosed:*`.

Reproduced using the unmodified candidate tool and a committed isolated fixture:

```markdown
## Round 56
Clean round.
## Appendix
A no-op returns met=True.
## Round 57
Clean round.
```

Output (`out/RV05TallyDiff/section-fixture.txt`):

```text
56     -          -    -         0       -        none     disclosed:shortcut
detail: round 56: statement shortcut scorecard SCORECARD.md:4 'A no-op returns met=True.'
```

Expected round 56 `no-disclosure`: the only qualifying statement belongs to Appendix. This can incorrectly satisfy a disclosure conjunct; it is not evidence that the current eight-round result is wrong. Recommendation: bound sections at every equal/higher-level heading and add this fixture to selftest. The existing selftest does not detect this boundary defect.

### P3 — Statement citations are attributed by containing file, not the round discussed

`tools/shortcut-tally.py:671-674,680-690` scans every line of a lesson as evidence for its filename's round; `:637-653` has no referenced-round guard. Actual candidate JSON attributes `corpus/lessons/round-57.md:26` to round 57 even though the sentence explicitly cites round-56's no-op acceptance. It also attributes `corpus/lessons/round-63.md:22-23` (explicit round-62 counter/sensitivity defects) and `SCORECARD.md:3302` (explicit round-62 closure) as round-63 shortcuts.

These are not fabricated statements, but they are misleading per-round diagnostic counts/provenance. Current round 57 has independent genuine round-57 evidence and round 63 has its formal block, so these false attributions do not change current 8/8. Recommendation: distinguish historical-context statements from statements about that round, and add a previous-round-only lesson fixture. Evidence is in `out/RV05TallyDiff/after-40-63.json`.

## Fleet ref / re-derivability

No mutable fleet dependency in the canonical C2 tally run: `tools/round64-c2-counter.py:970-977` invokes only `--repo`, `--rev <tip>`, `--rounds 56-63`, `--json`; no `--fleet-ref` (not a supported flag), `--fleet-rev`, or `--fleet-repo`. The canonical invocation derives all eight statuses from lane-tip blobs.

Optional fleet mode is different: `shortcut-tally.py:1252-1255` defaults `--fleet-rev` to HEAD when a fleet repo is supplied. `Fleet.__init__` resolves it once to a commit (`:698-708`), and reads blobs at that pinned commit (`:710-718`), so there is no within-run moving-ref read. However repeating the command after fleet HEAD moves can change results; JSON metadata `:1312-1314` does not record the resolved fleet revision. X07 discloses the fleet commit in its report and says this mode changes round-57/58 kinds. Treat optional fleet output as requiring a separately recorded fleet SHA, not re-derivable from lane tip alone. No fleet repository was modified or executed by this review.

## Human comparison

All eight current lane-only statuses are supportable; this does not make every individual matched sentence correctly attributed.

| Round | Observed status |
|---|---|
| 56 | disclosed:shortcut+survivor |
| 57 | disclosed:shortcut+survivor |
| 58 | disclosed:survivor |
| 59 | disclosed:shortcut |
| 60 | disclosed:shortcut |
| 61 | disclosed:no-falsify |
| 62 | disclosed:no-falsify+shortcut |
| 63 | ok |

Four rounds independently read at candidate tip (not merely X07 citations):

- **56:** `corpus/lessons/round-56.md:26` describes a surviving substring-membership mutant; `:29` reports a no-op harness accepted with `met=True`. Supports both kinds.
- **58:** `corpus/lessons/round-58.md:32` lists accepted unlisted no-ops; `:34` identifies surviving C1/C2 clause mutations. Supports survivor.
- **61:** `corpus/lessons/round-61-verifier-spotcheck.md:59-60` explicitly says wave-level seat falsification never ran because of an orchestrator stall. Supports no-falsify.
- **62:** `corpus/lessons/round-62-verifier-spotcheck.md:20,39` calls sensitivity vacuous; `:40` says dispatched falsification had no WAVE-DONE/results handoff. Supports shortcut plus no-falsify. Here the label means unsettled wave, not absence of all seat activity (the falsify column still says yes).

## Executed checks and comparison

Commands ran from the candidate clone with explicit scratch root `/fast/scratch/hyaku/kama-r64/f/RV05TallyDiff`:

- `python3 tools/shortcut-tally.py --selftest --scratch <scratch>/st`: exit 0, `selftest pass=10 fail=0`.
- `python3 tools/shortcut-tally.py --repo <clone> --rev 23b3fdb1a925129a9961cf551f6d40bf251602cb --rounds 40-63` and JSON variant: exit 0. Compared against X07's `before-40-63.txt`; durable text diff in `out/RV05TallyDiff/comparison.diff`.
- Also executed base tally source against the same candidate revision, JSON, to isolate behavior changes: `out/RV05TallyDiff/record-changes.json`. Only round 41/45 statuses, round 56-62 statuses, and round 57-63 falsify values change. Shortcuts/ids/counters/cheats/mutants remain unchanged throughout 40-63. Rounds 48-53 remain unreadable mutation reports; round 54 remains unreadable:no-section. Round 40 remains no-disclosure.
- Existing selftest confirms `--check 0` fails on a one-shortcut fixture, unknown rev exits 2, unreadable round exits 1, contradictory report exits 1, and two no-disclosure cases remain silent. Full output: `out/RV05TallyDiff/selftest.txt`.
- Negative selftest experiment: loaded candidate module, replaced only the in-memory `line_statements` function with `lambda text: {'shortcut'}`, then ran selftest in isolated scratch. No source modification. Exit 1, `selftest pass=7 fail=3`; statement-formats, no-disclosure-stays and fleet-report fail. Receipt: `out/RV05TallyDiff/negative-selftest.txt`. This demonstrates non-vacuous rejection of blanket disclosure, not comprehensive regex soundness.

## Residual risk / gaps

- Regexes are heuristics, not semantic round binding. An in-memory direct probe of `line_statements('If a mutant survived the counter, the claim would fail.')` returns survivor despite the conditional, not an observed survivor. Recorded in `out/RV05TallyDiff/parser-probes.txt`; do not interpret regex hits as proven events.
- Named-wave reader checks report presence, with missing-results notes; yes does not mean settled. Round 62 illustrates why the status and notes must be read together.
- LSP device unavailable: `read xd://lsp` returned `No such tool`; no status/references/definition/diagnostics device was mounted. Caller/definition checks therefore used literal grep and source reads, not semantic proof.
- Did not execute the full C2 counter or mutate its pins; only the assigned tally and its selftest. No saturation or claim verdict asserted.
- No tools installed/updated. Durable receipts copied to own out directory before scratch removal. Source and fixture content needed to reproduce the boundary finding are included above.
- Self-evaluation: accuracy 4 (heuristic limits explicitly separated), completeness 4 (four rounds read; full C2 intentionally not run), clarity 4 (severity and current-tip impact separated), actionability 4 (boundary fixture and fix target given), conciseness 4 (bulky receipts external). Overall 4.0; improve by adding semantic previous-round/conditional fixtures to the tool, outside this read-only review's scope.

tally_disclosed=8/8; selftest pass=10 fail=0; negative-selftest pass=7 fail=3 exit=1
