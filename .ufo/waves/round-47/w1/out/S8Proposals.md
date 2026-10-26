# S8Proposals — round 47, kama lane: what happened to the lane's own proposals

**Verdict: delivered.** All 20 numbered proposals in `considerthese/2026-10-22.md` … `2026-10-26.md` (4 per file) are mapped to the round that took them up or deferred them and to the closure's verdict, every cell carrying `file:line`; 8 landed behind round artifacts, 2 were adopted only in the reflection series, 1 is a pointer never implemented, 1 was deferred by name and is still open, 6 were never named by any round, 2 are in flight in round 47. Five findings follow, one of which corrects a count inside the current reflection.

Deliverable (draft for the round lesson, `considerthese/` untouched): `.ufo/waves/round-47/w1/out/S8Proposals/table.md`. No lane file, fleet file, index or jj state was touched; no clone was made and no lane counter was run, so the freeze-time counters are unaffected.

## 1. Method

- Proposals counted mechanically inside each file's `## Self-improvement suggestions` section: `sed -n '/^## Self-improvement suggestions/,$p' "$f" | grep -cE '^[0-9]+\. \*\*'` → 4 / 4 / 4 / 4 / 4 = 20 (`commands.txt`, exit 0).
- Uptake read three ways: the `considerthese` field and claim predicates in `.ufo/waves/round-*/preregistration.json`, the lesson `## considerthese` prose, and the closure's claim/axis verdicts.
- Every "no round" cell rests on the negative grep recorded in `refs-listing.txt` (counts below), not on absence of memory.

Commands and observed output (full log with exit codes in `S8Proposals/commands.txt`; lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`, all read-only):

```
grep -rn 'considerthese/2026-10-22\.md' .ufo/waves/round-*/preregistration.json corpus/lessons/round-*.md 2>/dev/null | wc -l   -> 0   [exit 0]
grep -rn 'considerthese/2026-10-23\.md' … | wc -l                                                                                -> 4   [exit 0]
grep -rn 'considerthese/2026-10-24\.md' … | wc -l                                                                                -> 7   [exit 0]
grep -rn 'considerthese/2026-10-25\.md' … | wc -l                                                                                -> 16  [exit 0]
grep -rn 'considerthese/2026-10-26\.md' … | wc -l                                                                                -> 4   [exit 0]
ls .ufo/waves/round-*/preregistration.json | wc -l                                                                               -> 23  [exit 0]
grep -l considerthese .ufo/waves/round-*/preregistration.json | wc -l                                                           -> 9   [exit 0]
grep -c considerthese .ufo/waves/round-39/preregistration.json                                                                   -> exit 2 (file absent)
ls corpus/lessons/round-47*                                                                                                      -> exit 2 (no round-47 closure yet)
grep -rn 'pin gap' corpus/lessons/ .ufo/waves/round-4*/preregistration.json | wc -l                                              -> 1   [exit 0]  (only the unrelated corpus/lessons/round-24.md:579)
```

Rows 9, 10, 12, 13–17 of the table also rest on positive citations, for example `corpus/lessons/round-35.md:57` (proposal 10-24 P1 → KQ44), `corpus/lessons/round-36.md:81` (P2 → KQ45), `corpus/lessons/round-38.md:98` (P4 → KQ47), `.ufo/waves/round-42/preregistration.json:34` (10-25 P1 → digest-ledger), `.ufo/waves/round-43/preregistration.json:64` (10-25 P3 → staged refusals), `.ufo/waves/round-46/preregistration.json:150` (10-26 P1 → append-only-audit).

## 2. Findings

**F1 — the tracking field exists in 9 of 23 preregistrations and is silent where it matters.** Rounds 35, 36, 37 and 38 have a `preregistration.json` with no `considerthese` field, and round 39 has no preregistration at all (exit 2 above). For the 2026-10-24 proposals the only round-side record is lesson prose: `corpus/lessons/round-35.md:57`, `corpus/lessons/round-36.md:81`, `corpus/lessons/round-38.md:98`. Reproduce: `for r in 35 36 37 38; do grep -c considerthese .ufo/waves/round-$r/preregistration.json; done` → `0,0,0,0`. Proposed fix (future rounds only, preregistration template): require `"considerthese": "<file:line> proposal N"` or the literal `"none"`, so an unrecorded uptake is distinguishable from "no proposal taken".

**F2 — the current reflection undercounts its own 2026-10-25 proposals by one.** `considerthese/2026-10-26.md:31` states "three of the four 2026-10-25 proposals became rounds 41 to 43"; proposal 4 was implemented in round 45 as `tools/seat-yield.py` — `corpus/lessons/round-45.md:21` and `.ufo/waves/round-45/preregistration.json:65` — and the round-45 closure records the tool at `corpus/lessons/round-45-verifier-spotcheck.md:115`. Round 45 landed at `a553bd7c` 07:52 BRT and the reflection was written ~09:25 BRT (`considerthese/2026-10-26.md:3`), so the evidence was available. Reproduce: `grep -n "proposal 4" .ufo/waves/round-45/preregistration.json corpus/lessons/round-45.md`. Proposed fix: the lesson row for 10-26 P2 states 4/4 with the round-45 cites.

**F3 — a frontier pointer is not a tracker.** Proposal 10-23 P1 is carried as round 34's frontier item 1 and explicitly not implemented (`corpus/lessons/round-34.md:107-111`; preregistration `.ufo/waves/round-34/preregistration.json:54`), and the string `considerthese/2026-10-23.md` never reappears in any preregistration or lesson after round 34 (4 hits, all round 34). The nearest later artifact, the round-47 shortcut tally (`considerthese/2026-10-26.md:33` → `.ufo/waves/round-47/w1/build_spec.py:133-134`), answers a different question (which counters a shortcut can satisfy, not a class ledger). Reproduce: `grep -rn 'considerthese/2026-10-23\.md' .ufo/waves/round-*/preregistration.json corpus/lessons/round-*.md`. Proposed fix: carry frontier proposals in a registry TSV with an opened-round column instead of prose, so they age visibly.

**F4 — the oldest open item has an explicit repeated deferral and no artifact.** Proposal 10-24 P3 ("prepared, not dispatched" ledger) is deferred by name at `corpus/lessons/round-37.md:84` and `corpus/lessons/round-38.md:98`, and the underlying question is filed operator-side at `corpus/lessons/round-33-verifier-spotcheck.md:70`. No ledger exists at the tip. Reproduce: `grep -rn "prepared-not-dispatched\|prepared, not dispatched" corpus/lessons/round-*.md` shows the two deferrals and no landing. Proposed fix: either `registry/prepared-waves.tsv` (wave, purpose, rounds waited) or a lesson row that drops it with a reason.

**F5 — "implements" in a preregistration does not mean admitted, so counting landed proposals from preregistrations overcounts.** Round 40's preregistration says C1 "also implements" 10-25 P1 (`.ufo/waves/round-40/preregistration.json:36`; lesson `corpus/lessons/round-40.md:30` "applied in bounded form"), while the closure rejects that claim: `corpus/lessons/round-40-verifier-spotcheck.md:105` "**Not admitted — honest stop** (`rejected-honest-stop`)". The proposal lands only at round 42 (`corpus/lessons/round-42-verifier-spotcheck.md:7`, operability improved at `:74`). Proposed fix: a landed-proposal count is taken from the closure's admission line, never from the preregistration.

Not a defect, recorded because a first-round-keyed tracker would miss it: a landed proposal can be re-consumed. 10-24 P2 (KQ45, round 36) is applied again to a new row in round 39 (`corpus/lessons/round-39.md:33`, closure admitted `corpus/lessons/round-39-verifier-spotcheck.md:86`), and 10-25 P2 is re-read in round 44 as the consumer of a `behind` result (`corpus/lessons/round-44.md:41`).

## 3. Calibration reading

- Of 20 proposals, 8 have a landed artifact: 3 as QUALITY criteria (KQ44 `corpus/QUALITY.md:316`, KQ45 `:322`, KQ47 `:334`), 3 as capabilities behind admitted closures (rounds 41, 42/43, 46), 1 as a tool registered in a round whose claims were rejected (round 45, `corpus/lessons/round-45-verifier-spotcheck.md:115`), 1 as a registry in an admitted round (`registry/staged-refusals.tsv`, round 43). Six were never named by any round; the oldest of that set is the 2026-10-22 file, whose own window ends at the round-25 spot-check (`considerthese/2026-10-22.md:3`), leaving rounds 26–47 with no record of it. So the lane's proposal pipeline is real but only half-visible: the failures are in recording, not in uptake.
- The three error classes this table exposes — preregistration "implements" ≠ admitted (F5), frontier pointer decay (F3), and a self-count short by one (F2) — are all counting errors of the same family the lane's calibration axis already tracks, and each is checkable from committed bytes with a one-line grep.

## 4. Bounds observed

- No edits to `considerthese/`, no lane edit, no index/jj mutation, no git write, no fleet-root file. No clone was created; the counters and preregistration were not re-run. No services started, no `agent://all`, no subagents. No tools installed (no pacman/uv/npx calls). Scratch `/fast/scratch/hyaku/kama-r47/S8Proposals` created empty and removed.
- Only writes: the three files below.

## 5. Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S8Proposals.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S8Proposals/table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S8Proposals/refs-listing.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S8Proposals/commands.txt`
