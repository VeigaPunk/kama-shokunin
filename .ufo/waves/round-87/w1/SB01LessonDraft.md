# SB01LessonDraft — round 87 wave 1 — scoped findings

Seat: SB01LessonDraft (leaf, no subagent dispatch). Milestone: kama r87 w1. Judged on: calibration.
Revisions read: base `362b0d4a241520c9bc79b204c042d9fcefbb06ea`; freeze `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`.
Deliverable: `.ufo/waves/round-87/w1/out/SB01LessonDraft/lesson-round-87.md` (draft; L1 integrates).

## Scope

- Draft `## Mistakes` (R86V1, R86V2; class · evidence · captured-by · fix) and `## Gate` placeholders (S578 re-open, S580, considerthese pointer) for `corpus/lessons/round-87.md`.
- Read-only evidence only. No lane file edited; no lane gate, counter, selector or probe battery executed (none named by the item). No quotes invented: the lesson quotes no CommonMark or considerthese text.
- No tools installed or updated. No pacman, no network, no git mutation.

## Commands and outputs

Full receipts with exit codes: `.ufo/waves/round-87/w1/out/SB01LessonDraft/receipts-readonly.txt` (re-run of the read-only checks below).

| # | Command (read-only) | Exit | Result |
|---|---|---|---|
| 1 | `mkdir -p` of out and scratch dirs | 0 | created |
| 2 | `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` | 0 | prints the lane root |
| 3 | `git ls-tree -r --name-only 94e8fe7b… -- <3 R86V1 paths>` | 0 | all 3 paths present |
| 4 | `git ls-tree -r --name-only 362b0d4a… -- <same paths>` | 0 | no output (absent at base) |
| 5 | `git show --stat 94e8fe7b…` | 0 | 8 files, 579 insertions; includes the 3 round-86 strays |
| 6 | `ls -la` on the 3 stray files | 0 | mtimes 00:45, 00:46, 00:47 on 2026-11-05 |
| 7 | `ls .ufo/waves/round-86/w3/EX02GateCensus.md`, `CN01OverlapScan.md` | 2 | both absent |
| 8 | `grep -c c1-probes tools/pre-report-gate.py` | 1 | prints `0` (no reference) |
| 9 | `grep -n 'argv_clean = ' tools/pre-report-gate.py` | 0 | line 616: `git … status --porcelain -uall -- wave_rel` |
| 10 | `grep -rln "not implemented" considerthese/` | 0 | 2026-10-20, -21, -22, -23 only |
| 11 | `grep -n` for `CONTAINER`, `FENCE_CLOSE`, `DISPOSITIONS`, `def disposition_of` in `tools/round86-rendered-cells.py` | 0 | lines 66, 68, 83, 265 |
| 12 | `grep -n -o` for `rejected-harmed` and `verdict` in round-86 spotcheck; `grep -n` for list items in `considerthese/2026-10-26.md` | 0 | spotcheck:25 (body), :76 (verdict token); considerthese items at lines 29, 31, 33, 35 |
| 13 | `git status --porcelain -uall -- .ufo/waves/round-86` | (pipeline; exit not captured) | empty output: the strays are no longer untracked |

Reads: `corpus/lessons/round-86-verifier-spotcheck.md` (full), `corpus/lessons/round-86.md` (format and Gate table), `plans/round-87-claims.md` (full), `.ufo/waves/round-87/controls/c1-probes-before.out`, `c1-live-before.out`, `c1-probes.py`, `tools/round86-rendered-cells.py` (lines 60–75, 160–230, 262–285), `tools/pre-report-gate.py` (header; round-clean block), `.ufo/waves/round-86/w3/MT01SelectorMutants.md` (Items 1–2), `corpus/SOURCES.md:331-334`, `considerthese/2026-10-26.md` (full).

## Findings

F1 — R86V1 fix is partial. The three stray files are committed in `94e8fe7b` (receipt 3, 5). Two seat reports the round-86 spotcheck required (`w3/EX02GateCensus.md`, `w3/CN01OverlapScan.md`) are still absent on disk and at the freeze commit (receipt 7). Evidence: `corpus/lessons/round-86-verifier-spotcheck.md:13,80`. The lesson records this as a residual, not as closed.

F2 — R86V1 captured-by is precise. The round-clean arm is round-scoped (`tools/pre-report-gate.py:616`), so a round-87 run cannot see round-86 leftovers. At round 86 the closure's green was revision-bound to clean revisions (`spotcheck:42`); a tip run with `--round 86` did go red on those strays (`spotcheck:43`). So the gap was that no tip run followed the writes at 00:45–00:47, not that the arm was blind at round 86.

F3 — R86V2 captured-by: none in round 86 is confirmed. The gate has no reference to the probe battery (receipt 8). The round-86 mutant battery (`measured/terminal/c1-mutants.out`, 10/10) has no arm for a list-marker closer; `list-fence-shadow` (`tools/round86-rendered-cells.py:462-463`) covers a list-marker opener only. MT01 (`w3/MT01SelectorMutants.md` Item 2) left MD and ME as survivors, unarmed.

F4 — Mechanism for R86V2, read from code, not executed. `CONTAINER` (line 66) admits `- ` and `> ` before a fence closer, so `FENCE_CLOSE` (line 68) matches `- ```` as a closer. `disposition_of` (lines 265–270) returns the first word of `DISPOSITIONS` (line 83) found anywhere in the body. Marked `[INFERENCE]` in the lesson: the live base finding `mismatches=2` with expectation `round86 rejected-harmed` (`c1-live-before.out:1-3`) matches the oracle taking `rejected-harmed` from the round-86 closure body (spotcheck:25), whose verdict token is `rejected-honest-stop` (spotcheck:76). Not run; a check of this would be a lane counter run, which this item does not name.

F5 — P-C is not in the round-86 reproduction. The round-86 spotcheck reproduces two false greens (P-A, P-B; spotcheck:25). `c1-probes-before.out:4` shows P-C also escaping at base. The lesson records P-C as first appearing in the round-87 battery.

F6 — considerthese citation discrepancy for the L1. The frozen plan quotes a "proposals only … not implemented" list for `considerthese/2026-10-26.md`. That file's line 27 reads "These are proposals only; I am not acting on any of them."; the phrase "not implemented" occurs in 2026-10-20, -21, -22 and -23 (receipt 10). The 2026-10-26 proposals are at lines 29, 31, 33, 35. The Gate placeholder cites those lines; SC02 owns the disposition.

F7 — S580 and S578 quotes are not recorded. The lesson leaves them as PENDING (SC01 owns S580; the claims require S578 to be re-opened this round). SOURCES.md has S578 and S579 rows at lines 333–334 (`status=mined`, opened 2026-11-04); no S580 row exists.

F8 — Discrepancy the L1 should note: `c1-live-before.out` finding 2 says the closure row names `round-85`, while the newest closure is round 86 (`.ufo/waves/round-87/controls/c1-live-before.out:2`). This is a stale cell, separate from the R86V2 false greens; the lesson does not merge the two.

## Deliverables

- `.ufo/waves/round-87/w1/out/SB01LessonDraft/lesson-round-87.md` — `## Mistakes` (M1 = R86V1, M2 = R86V2) and `## Gate` placeholders (S578, S580, considerthese).
- `.ufo/waves/round-87/w1/out/SB01LessonDraft/receipts-readonly.txt` — command receipts with exit codes.
- `.ufo/waves/round-87/w1/SB01LessonDraft.md` — this report.
- Scratch `/fast/scratch/hyaku/kama-r87/SB01LessonDraft/` removed before yield.

## Not done (by scope)

- S578 re-open quote, S580 quote, considerthese disposition: pending SC01/SC02 (placeholders in the lesson).
- No C1 or C2 measurement: the seat item names none.

VERDICT: lesson draft delivered with R86V1 (partially fixed: two seat reports still absent) and R86V2 (captured-by none confirmed; fix pending integration) and PENDING Gate placeholders for S578, S580 and the considerthese pointer.
