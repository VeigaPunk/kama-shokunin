# S2Events — Round-46 append-only audit (SCORECARD finding paragraph)

**Verdict:** the paragraph is drafted (`section.md`) and every figure in it is bound to a run I executed; the audit's five events are reported as they are — 0 unrestored, 3 repaired text-for-text after one real truncation (`0718b6ab` → `82b5e9d3`), 2 accounted SCORECARD-head re-derivations (`dd9f5dc6` 24/31, `0718b6ab` 2416/2417) — with the honest consequence that "SCORECARD.md is append-only" holds for the round record and not for the head, which `SCORECARD.md:6` itself declares re-derived. Two findings (an instrument undercount of 6 lines across two events; the head's archival promise being wider than its practice), each with a proposed fix in this directory and neither applied.

## Deliverables

| Path | What |
|---|---|
| `.ufo/waves/round-46/w1/out/S2Events/section.md` | The `### Round-46 append-only audit` section text, paste-ready, plus a seat appendix (provenance table, findings, out-of-scope) |
| `.ufo/waves/round-46/w1/out/S2Events/audit-at-4a2a4d55.out` | tool output at the base the item names (294 commits), exit 1 |
| `.ufo/waves/round-46/w1/out/S2Events/audit-at-0163fea2.out` | same, 292 commits, exit 1 |
| `.ufo/waves/round-46/w1/out/S2Events/audit-at-head.out` | same, tip `96d32918`, 295 commits, exit 1 |
| `.ufo/waves/round-46/w1/out/S2Events/audit-threshold1.json` | `--threshold 1 --json`: 66 events, 11 restored / 6 partial / 49 unrestored, exit 1 |
| `.ufo/waves/round-46/w1/out/S2Events/selftest.out` | `AOA_SELFTEST pass=10 fail=0`, exit 0 |
| `.ufo/waves/round-46/w1/out/S2Events/recount.py` / `recount.out` | header-aware recount: 2421/2420 SCORECARD, 2292/2292 LOG, plus the exact absent lines |
| `.ufo/waves/round-46/w1/out/S2Events/c2-counter-at-4a2a4d55.out` | C2 counter at the base: `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_partial=2 met=False`, exit 1 |
| `.ufo/waves/round-46/w1/out/S2Events/proposed-scorecard-head-line6.txt` | current `SCORECARD.md:6` verbatim and the proposed narrowing (F2) |

## Evidence (commands, outputs, exit codes)

1. `python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` → exit 1:
   `dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 partial -`; `0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 partial -`; `0718b6abbda6 LOG.md 2290/2290 restored 82b5e9d33a19`; `corpus/QUALITY.md 375/375 restored 82b5e9d33a19`; `corpus/README.md 663/663 restored 82b5e9d33a19`; `summary commits=294 events=5 restored=3 partial=2 unrestored=0`.
2. Same at `0163fea2` (commits=292) and at `HEAD=96d32918` (commits=295): identical five events — the set is not revision-specific.
3. `--threshold 1` at `4a2a4d55`: 66 events (SCORECARD 23, SOURCES 20, LOG 13, README 8, QUALITY 2), 11 restored / 6 partial / 49 unrestored, exit 1 — "append-only" is a threshold-20 statement, not a byte property.
4. `python3 tools/append-only-audit.py --selftest` → `AOA_SELFTEST pass=10 fail=0`, exit 0.
5. `python3 tools/round46-append-audit-check.py --repo <lane> --tip 4a2a4d55 --scratch <scratch>` → `selftest=1 fixture=1 lane=1 table=0 … met=False`, exit 1. `table=0` is expected at the base (the capability row lands with this round); the measured result belongs to §Round-46 measured results.
6. Restoration arithmetic: `git show --numstat 82b5e9d3 -- SCORECARD.md` → `2428 0`; `82b5e9d3` holds 2416/2417 counted (1789/1790 unique) of the deleted text (`recount.out`).
7. The 7 lines absent from the round-42 event, from `recount.out`: the six round-41 `## Axes` rows and the round-41 reconcile sentence. The sentence survives inside the tip line: `grep -c 'Reconciled in round 41 against the measured commit' SCORECARD.md` → `1`; the round-41 depth sha `151023b9…` is at `dd9f5dc6^1` (1) and not at the tip (0). Round-45: `91440eb8…` at `0718b6ab^1` (1), tip (0); its successor `3046955b…` absent at `82b5e9d3^1` (0), present at `82b5e9d3` (1).
8. No round section, correction row, historical table or capability row is among the unrestored lines — the `absent:` list in `recount.out` is six `## Axes` rows and one head sentence.
9. The 24 re-added round-42 lines: 23 are the round-5 banner (8), round-5 plan (9) and round-3 Retired (6) archived in the same commit under §Historical head sections; 1 is `## Saturation`, held only because the current head carries the same heading (the archived copy is `### Saturation (round-10 text)`). Deletion breakdown per hunk: 8+1+6+9+6+1 = 31.

## Findings

**F1 — the `---` filter drops `--…` content lines (frozen instrument, both copies).**
`tools/append-only-audit.py:102` and `tools/round46-append-audit-check.py:115`:
`dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]`.
After the diff marker the text of a deleted line beginning `--` becomes `---…`, so it is dropped as if it were the `---` header — the docstring says only "the `---` header" is excluded.
Shown by: `git show 0718b6ab^1:SCORECARD.md | grep -c '^--out '` → `4` (tip → `4`); header-aware recount (`recount.out`) `2421`/`2420` versus the tool's `2417`/`2416`; LOG `2292`/`2292` versus `2290`/`2290` (the two LOG lines are wrapped `--tip …` / `--rev …`).
Impact: counts only; no `status` or `restored_by` changes, and both counters share the filter so C2's `lane` leg still agrees.
Fix (proposed, not applied — counter is frozen with `counter_sha256 4dcfbe10…`): skip only the line followed by `+++`, per the diff in `section.md` §Findings F1.

**F2 — `SCORECARD.md:6`'s archival promise is wider than the practice.**
Line 6 says "the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections". The `## Axes` rows re-derived in rounds 42 and 45 are not archived: `grep -c 151023b99bec SCORECARD.md` → `0` and `grep -c 91440eb8 SCORECARD.md` → `0`, each present (`1`) in the pre-change file. So the append-only carve-out for the head is real but its compensation is only partial; that is what makes the two partials more than bookkeeping.
Commands: `git show dd9f5dc6^1:SCORECARD.md | grep -c 151023b99bec`; `git show 0718b6ab^1:SCORECARD.md | grep -c 91440eb8`.
Fix: `proposed-scorecard-head-line6.txt` (narrow the sentence to the blocks actually archived), or append the superseded rows under §Historical head sections.

**F3 — `restored_by=-` on a partial is definitional, not "nothing restored" (disclosure only).**
`82b5e9d3` holds 2416/2417 of the SCORECARD event but the field is null because one line is never held. Frozen contract, no fix; the paragraph states it.

## Touched surfaces

- Created: `.ufo/waves/round-46/w1/out/S2Events/` (10 files: `section.md`, six receipts, `recount.py`, `recount.out`, `proposed-scorecard-head-line6.txt`) and this report `.ufo/waves/round-46/w1/out/S2Events.md`.
- Read-only: `kama-shokunin/{SCORECARD.md,LOG.md,tools/*}`, lane git history, `.ufo/waves/round-46/{preregistration.json,controls/}`, `considerthese/2026-10-26.md`, fleet `AXES.md`.
- Not edited: counters, preregistration, controls, SCORECARD, LOG, any lane file. No git/jj mutation, no service action, no subagent.

## Out of scope / not done

- The C2 capability-table row (`| append-only-audit | … | 46 |`) is not added — C2's `table` leg and the measured commit belong to the round's capability entry and §Round-46 measured results.
- No measured-commit receipt: the measured commit does not exist yet; the paragraph reports `4a2a4d55`, `0163fea2` and `96d32918`.
- F1's fix is proposed only; applying it to a frozen counter in this round would invalidate C2's pre-registered `counter_sha256`.

## Tooling

None installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r46/S2Events` used for the counter's fixture and the diff dumps, then removed; every receipt was copied into the out directory first.
