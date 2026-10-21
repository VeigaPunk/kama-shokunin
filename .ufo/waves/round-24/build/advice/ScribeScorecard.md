# ScribeScorecard — round-24 SCORECARD correction draft (scribe)

Seat: `KamaR23-2.ScribeScorecard-2` (scribe, leaf; no subagents dispatched).
Scope: draft only, in the out directory. **No production file was created,
edited, appended, committed or pushed** by this seat.

## Verdict

The round-24 SCORECARD block is drafted as a **candidate** with two
append-only corrections to the round-23 author verdict and a fully
predeclared (and entirely **UNRUN**) C1 measurement table. No round-24
improvement, axis move, trend verdict or admission is claimed; the block
states plainly that every round-24 number is unmeasured.

The candidate is at
`.ufo/waves/round-24/build/out/ScribeScorecard/SCORECARD-round-24-draft.md`.
Append point, if the L1 accepts it: after the round-23 block,
`SCORECARD.md:1188`.

## Behavior (what the draft does)

1. **Corrects the round-23 author verdict as closed, not as filed.** The
   round-23 block (`SCORECARD.md:1152-1188`) and the filed report
   (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`, fleet
   `410b511`) are left byte-unchanged; the draft appends a correction table
   with one row per superseded statement, each carrying the closure's
   wording and its file:line anchor.
2. **Records the two r23 corrections with their real location.** The count
   correction (falsify-wave durable lane reports) and the identity-evidence
   correction (killed FIFO-process inventory) are appended, each naming the
   exact stale line, and each marked status-neutral (no verdict, axis score
   or admission changes).
3. **Predeclares the round-24 C1 measurements** from
   `.ufo/waves/round-24/preregistration.json` (expected_after 1-7,
   measurement line), each with its counting command, its expected exit and
   an explicit `UNRUN` status.
4. **Reports the gate that blocks the first measurement**: the preregistered
   counting command names a file that does not exist at the round base.
5. **Leaves the round-24 trend row unresolved**, because no round-24
   measurement exists.

## Gates observed

| Gate | State | Evidence |
|---|---|---|
| Production edits | none by this seat | `git status --porcelain` in the lane shows only the untracked `.ufo/waves/round-24/build/` tree plus the L1's `LOG.md` modification; no file under `SCORECARD.md`, `LOG.md`, `corpus/` or `tools/` was written by this seat |
| Commits / pushes / jj | none | — |
| Fleet / sibling writes | none | all reads; the only fleet file written is my own out/artifact under the lane |
| Heavy files | none | no clone, no fixture build; all heavy work belongs to `/fast/scratch/hyaku/kama-r24/<Name>` and none was needed |
| Subagent dispatch | none | leaf seat |
| Tool installs / updates | **none** | only `git`, `ls`, `wc`, `grep`, `sed -n`, `python3 -c` (stdlib) already on the host |
| Round-24 measurements | **none run** | no grid, selftest, ledger, parity or mutant command was executed |
| Nested seats | none | — |

## Touched surfaces

Production: **none**.
Written (this seat only):
- `.ufo/waves/round-24/build/out/ScribeScorecard/SCORECARD-round-24-draft.md` (new, candidate draft, 11 788 bytes)
- `.ufo/waves/round-24/build/advice/ScribeScorecard.md` (new, this report)

Read (read-only): lane `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-23.md`,
`corpus/SOURCES.md` (row count only), `tools/report-landing-audit.py`,
`tests/report-audit/repo-state-grid.py`, `tests/report-audit/isolation-mutants.py`
(existence only), `.ufo/waves/round-23/**`; fleet `MANIFEST.json` `rounds[428]`,
`.ufo/reports/round-23/kama.md`, `AXES.md`; sibling
`.ufo/waves/round-24/build/out/CritEvidence/**`.

## Findings

### F1 — The round-23 quality-improve reading is superseded (closure-bound)

The round-23 block says "Trend verdicts: … quality **improved** (KQ34,
superseding rows for three defective source rows)"
(`SCORECARD.md:1179-1183`) and "Operability is **traded, not unchanged**"
(`SCORECARD.md:1171-1174`). The closure ruled operability **harmed** and the
quality trend **harmed** (`MANIFEST.json` → `rounds[428]`: `verdicts
{calibration: improved, operability: harmed, …}`, `trends {expansion:
unchanged, quality: harmed, discernment: improved}`,
`admitted: false`, `verdict: rejected-harmed`, closed
2026-10-21T17:44:26Z). `LOG.md:1413-1415` records the supersession and the
rule behind it: "Disclosure of a trade does not waive the no-trade rule."
The draft carries this as an append, not as an edit of the round-23 block.

### F2 — The round-23 grid green did not and could not cover the harm row

`tests/report-audit/repo-state-grid.py:13-14` states that `open` and
`tradeoff` rows "are reported, never graded", and the summary at `:798-806`
counts only `fault`, `control` and `contract` rows. T01 (`t_blobless`, a
`--filter=blob:none --no-local` clone, registered at `:689`) and F23
(`f_promisor_pack`, `:670`) are exactly the two rows the closure's
`harm_ruling` used, and both were ungraded. The closure's independent rerun:
frozen exit 0 with a correct clean verdict → current exit 2
`partial clone (promisor pack)`; and on a real promisor-marked clone of the
lane, the frozen auditor's rounds 10-22 exit 0 with the same JSON verdict as
current on the full clone, while current on the promisor clone exits 2.
Consequence for the draft: the r23 fault/contract/control counts (26/26,
4/4, 13/13) may not be quoted as a no-harm result in round 24.

### F3 — The auditor's refusal sites that round 24 must repair

`tools/report-landing-audit.py:455-457` refuses any repository whose
`objects/pack` holds a `.promisor` marker next to a `.pack`
("partial clone (promisor pack)"), and `:462-465` refuses any repository
whose config carries `extensions.partialclone` or a truthy
`remote.*.promisor` ("partial clone ({key})"). Both are unconditional
metadata tests: they refuse a repository for declaring promisor-ness, not
for lacking an object. That is the mechanism the round-24 preregistration
targets ("A metadata marker alone is not evidence of missing objects",
`LOG.md:1424-1426`). Isolation flags live at `:93`
(`GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)`) and must
survive the repair.

### F4 — The preregistered counting command does not exist yet (gate)

`measurement` in `.ufo/waves/round-24/preregistration.json` names
`python3 tests/report-audit/promisor-grid.py --arm both --json`.
Observed: `git cat-file -e 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tests/report-audit/promisor-grid.py`
→ `fatal: path 'tests/report-audit/promisor-grid.py' does not exist in
'0df800e896f6bce285a81e794ad4ae1d1e6c3a71'`; the working tree at `d1b9d95`
holds only `isolation-mutants.py` and `repo-state-grid.py` under
`tests/report-audit/`. So the round-24 C1 row is **UNRUN and blocked on an
artifact that round 24 must land** — it is not a failure, and the draft says
so. The preregistration's oracle (fixed expected exits and finding IDs
derived before implementation) must be encoded inside that harness before
the measurement counts anything; the draft names that requirement.

### F5 — Falsify-wave durable lane reports: 69, not 68 (count correction)

Observed by this seat: `ls -1 .ufo/waves/round-23/falsify/advice/*.md | wc -l`
→ **69** (the directory holds 70 entries; the 70th is
`swarm-registry.json`). The literal stale count is
`corpus/lessons/round-23.md:178` — "73 seats dispatched (68 reports; dead:
RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty)" —
which is internally inconsistent: 73 − 4 = 69. The filed fleet report does
**not** state 68 falsify reports; it gives 73 falsify seats, 4 dead, and a
141-seat round total (`.ufo/reports/round-23/kama.md:148-155`), i.e. 69
durable reports and 5 seats without a report (build `RevClaimScope` plus the
4 dead falsify seats). The closure says the same and adds that
`RowC03FabricatedFull` wrote 6618 bytes at 16:10:15Z before its final
response aborted at 16:10:50Z, so its empty session `.md` does not make its
lane report absent (`rounds[428].verification.routed_checks`).

**Correction of a correction:** `LOG.md:1417-1420` (commit `d1b9d95`) frames
this as a correction to the *filed* `.ufo/reports/round-23/kama.md`. The
filed report contains no "68"; the stale number lives in the lane lesson at
`corpus/lessons/round-23.md:178`. CritEvidence makes the same point
(`out/CritEvidence/r23-corrections-append.md`, item (a)). The draft states
the location accurately and does not repeat the mis-attribution.

### F6 — The FIFO-process identity correction has two competing glosses (conflict, reported verbatim)

Gloss A — preregistration `expected_after[6]` and `LOG.md:1417-1420`
(`d1b9d95`): "40 of the 56 killed FIFO-process identities were retained, not
full identity evidence."

Gloss B — CritEvidence's retained-transcript reading
(`out/CritEvidence/r23-corrections-append.md`, item (b); and the
`LOG.md` "Round-24 correction provenance refinement" append present in the
working tree): "56 was a matching-process count, while a different listing
pattern kept 40 truncated identity rows (38 git, gpg-agent, scdaemon), not
56 identified FIFO-blocked git processes. Only 19 retained rows could be
linked to FIFO fixtures; 16 counted identities were not retained. The
matching count became zero after cleanup, but this does not independently
prove every victim's identity or blocking cause." Corrected reading carried
by B, verbatim: "56 round-owned fixture processes (git plus at least two gpg
daemons) were killed; 40 identities retained in the session transcript, only
partly shown to be FIFO-blocked."

Mechanism of the discrepancy (B's provenance, corroborated by the closure's
`routed_checks`): the 56 is
`ps -eo pid,args | grep -E 'repo-state-grid-|/tmp/kama-r23' | grep -v grep | wc -l`
at 16:33:38Z, while the 40 rows come from the *different* pattern
`'repo-state-grid-|kama-r23|refusal'` with `head -40`; 37 of the 40 provably
match the counting pattern and 3 are truncated before the path. Retained
listing: `out/CritEvidence/r23-ps-listing-line156.txt` (sha256
`96c21f6f793f5c3c8901eb4a8d6a735dd27a3f98a1d2b058ee4886e1ba7115bc`),
transcript `…/KamaR23-2.jsonl` sha256 at read
`114ffef5714e88e39fe4e3b80155d4f9c036dea99634c7ab5099821f9f1860db`.

The stale statements this corrects: `.ufo/reports/round-23/kama.md:34-35`
("56 orphaned FIFO-blocked git processes from this round were killed"),
`corpus/lessons/round-23.md:109-110`, and `corpus/lessons/round-23.md:174`
(M7, "56 blocked `git` processes"). All of those bytes stay immutable; the
correction is an append.

**This seat does not adjudicate.** The draft carries both glosses verbatim,
marks the conflict, and leaves the final wording to the operator. The
material difference is that Gloss A reads as "40 of 56 FIFO-process
identities retained" while Gloss B reads as "56 killed, 40 identities
retained from a broader pattern, only 19 shown to be FIFO-blocked" — the
two do not describe the same retained set.

### F7 — The axis choice is correct and is the one this round must keep

`SCORECARD.md:23` records calibration 7 and `SCORECARD.md:19` operability 8;
the saturation line is 8/10 on every owned axis with stagnation window N = 4
(`SCORECARD.md:132`), so the stagnation nudge is inactive and a round must
claim the lowest non-retired axis: **calibration 7**. Round 23 declared
exactly that (`SCORECARD.md:1154-1155`) and the closure credited
calibration **improved**; the round-24 preregistration declares
"calibration7→7 narrow" for the same reason. The draft states the axis
explicitly, with the score pair, so the reader need not infer it.

## Commands run (this seat)

Read-only, all against the local lane and fleet; no build, test, formatter
or grid command was run:

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --oneline -8
git -C …/kama-shokunin status --porcelain
git -C …/kama-shokunin cat-file -e 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tests/report-audit/promisor-grid.py
git -C …/kama-shokunin show --stat --oneline HEAD
ls -1 .ufo/waves/round-23/falsify/advice/*.md | wc -l          # → 69
ls -1 .ufo/waves/round-23/falsify/advice | wc -l               # → 70
grep -n "promisor\|partialclone\|no-lazy-fetch" tools/report-landing-audit.py
grep -n "promisor\|T01\|F23\|tradeoff\|contract" tests/report-audit/repo-state-grid.py
grep -n "68\|69" corpus/lessons/round-23.md
python3 -c "import json; m=json.load(open('/home/vgpnk/Projects/shokunin/MANIFEST.json')); …rounds[428]…"
```

The `MANIFEST.json` read was a JSON field dump of `rounds[428]` into
`/tmp/cl428/*.txt` for verbatim reading; nothing in `/tmp` is part of the
deliverable.

## Out of scope for this seat (and why)

- **Writing `SCORECARD.md`, `LOG.md`, `corpus/` or any production file** —
  the contract reserves lane production writes to the L1 (planner seat).
  My deliverable is a candidate block under `build/out/ScribeScorecard/`.
- **Implementing the promisor repair, the grid or the mutants** — the
  assignment is a scribe draft; the implementation seats own the code.
- **Running any round-24 measurement** — no measurement was assigned to me;
  the draft's table is therefore entirely `UNRUN`, and the contract forbids
  inventing results.
- **Adjudicating the F6 conflict** — operator/L1 owns the wording.
- **The r23 closure's open near variants** (alternates, gitfile redirect,
  `--shared`-of-partial bypass, second Landed section, ambiguity overwrite,
  errata CR, `--errata` FIFO, memory ceilings, unisolated sibling gates) —
  carried in the draft's Planned line as debt, not as claims.

## Known limits of this report

- The draft's round-24 rows are **expectations**, not observations. Any
  reader who quotes them as results would be wrong; the draft repeats the
  `UNRUN` status in every row and in its header.
- The expected harness exit for the new grid (`1`, frozen arm red by
  design) is marked `[INFERENCE]` in the draft: the preregistration fixes
  per-case expected exits and finding IDs, not the harness exit. The r23
  analogy is `tests/report-audit/repo-state-grid.py:16-19`.
- I did not re-open any git upstream documentation; no source rows are added
  or claimed by this round's draft.
- I did not verify the round-24 grid's internal expectations (it does not
  exist yet) and therefore cannot say whether the preregistered oracle is
  implementable as written — only that the command it names is absent.
- Sibling seat outputs under `build/out/` were read as they appeared
  (CritEvidence only, at 14:57); later sibling artifacts were not reviewed
  and may refine F5/F6 further.

## Artifact paths

- Draft candidate: `.ufo/waves/round-24/build/out/ScribeScorecard/SCORECARD-round-24-draft.md`
- This report: `.ufo/waves/round-24/build/advice/ScribeScorecard.md`
- Read (not copied): `.ufo/waves/round-24/build/out/CritEvidence/{provenance.txt,r23-corrections-append.md,r23-ps-classification.txt,r23-ps-listing-line156.txt}`
- Read (not copied): `/home/vgpnk/Projects/shokunin/MANIFEST.json` `rounds[428]`; `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`; `/home/vgpnk/Projects/shokunin/AXES.md`

## Checks the L1 should run after integration (not run here)

1. `python3 tests/report-audit/promisor-grid.py --arm both --json` — requires
   the harness to exist first (F4); expected exit 1 (frozen arm red).
2. `python3 tests/report-audit/repo-state-grid.py --arm both --json` —
   expected exit 1, with the promisor policy-row expectation changes
   documented row by row and the non-promisor rows unchanged.
3. `python3 tools/report-landing-audit.py --selftest` — expected exit 0.
4. Recipe line `nh-history-parity` (`.ufo/waves/round-23/recipe.json`) —
   expected exit 0; rounds 10-22, with and without errata, byte-identical
   to frozen.
5. `python3 tests/report-audit/isolation-mutants.py --json` — expected exit 0;
   every survivor listed by row.
6. Only then fill the draft's `UNRUN` cells and the round-24 trend row, and
   decide the F6 wording.

## Tools installed or updated

None.
