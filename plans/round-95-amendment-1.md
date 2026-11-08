# Round 95 — amendment 1 (post-freeze narrowing, Amendment 59 ledger)

Date: 2026-11-08. Author: L1 `KamaR95`. Frozen plan: `plans/round-95-claims.md` (commit
`c798e831d6703428563a70789d1252dc39503d60`). This file does not rewrite the frozen plan; it records the
narrowing the round's own measurement forces, per Amendment 59: "If a wave artifact falsifies a claim's wording
you either (i) amend the frozen claim down to the enforceable property, citing the artifact, and then file; or (ii)
file an honest stop."

## C1 operability — **verified** (unchanged wording; the discriminator sentence is confirmed)

The frozen predicate reproduces at M1 `f63256607916cdeb35580a7af315b5f4b54eba18`:
`ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1 budget=work probe=rev …`
exit 0 (`.ufo/waves/round-95/measured/c1.out`). The base control reproduces the defect the claim removes:
`mismatches=1 positive_mismatches=1`, W03 graded `MODEL_OK/router-unloaded-autoload` at 60.20 s — the round-94
constant wrapper truncating forty distinct slow files and leaving every truncated candidate loadable
(`controls/c1-base.out`, exit 1).

Disclosed at the freeze and unchanged: W03 costs 81.7 s at natural load on this host (1.36× the round-94
constant), the counter refuses to claim a discriminator below 1.25× (`controls/c1-discriminator-guard.out`,
exit 2 at 8 files), a candidate over `MAX_TENSORS`/`MAX_STEPS` stays `-`, and a slow `/props` still decides the
verdict (routed).

## C3 calibration — **narrowed** (frozen predicate not reachable as worded at F)

Falsified wording, from this round's own run:

- `.ufo/waves/round-95/measured/c3.out` (run against the counter at the freeze commit `c798e831`) reports
  `FREEZE_AUDIT receipts=7 present=7 missing=0 tokens=0 matching=0 cited=17 unresolved=4 met=False`, exit 1.
- Two independent reasons, both properties of the frozen instrument rather than of the round's work:
  1. **`unresolved=4`**: the plan cites S616/S617 as the round's sourced rows, and those rows are committed at M2
     (`beef8922`), not at F — a freeze that precedes its own sourced work cannot resolve them. S604 is cited in the
     C2 "sourced" paragraph too and resolves; the four counted ids are S616, S617 and their two repeats.
  2. **`tokens=0`**: the token arm finds a tool only on a `python3 tools/<tool>.py` occurrence *inside one line's
     backticked span*; the frozen plan writes each predicate as a two-line backticked command, so the arm never
     fires and `tokens=0 matching=0` is vacuous, not a pass.

Narrowed claim (this is what round 95 claims, and what the frozen counter enforces): the round's statement of its
own instruments is auditable — at the round's landed tip, `tools/round95-freeze-audit.py` over the amended
statement below reports `receipts=7 present=7 missing=0 tokens=6 matching=6 cited=8 unresolved=0 met=True`, exit 0;
and the same seven receipt files are present at the freeze commit itself
(`git -C . ls-tree -r --name-only c798e831 -- .ufo/waves/round-95/controls` lists all seven), so "the freeze
carries the receipts it names" is shown by the tree, not by the audit's source arm.

Disclosed: the audit grades presence and literal tokens, never receipt content. A committed file whose bytes do
not contain what its name promises passes; the content gate stays the counters' own grading and the non-author
read (recorded as lesson M4 below).

### Amended statement audited by the frozen counter

Freeze-time receipts (each committed with the plan at `c798e831`):

`controls/census-start.out`, `controls/c1-base.out`, `controls/c2-base.out`, `controls/c3-base.out`,
`controls/c1-discriminator-guard.out`, `controls/sources-opened.out`, `controls/c2-section-candidate.md`

Predicate lines (one per line so the frozen token arm reads them):

C1: `python3 tools/round95-router-budget.py --repo . --rev <M1> --work <scratch>` prints `ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1 budget=work probe=rev w03_seconds=81.7`
C2: `python3 tools/round95-setter-sweep.py --repo . --rev <M2> --work <scratch>` prints `SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0 derived_disagree=0 decisions=9 decisions_bound=9 met=True`
C3: `python3 tools/round95-freeze-audit.py --repo . --rev <tip> --plan plans/round-95-amendment-1.md` prints `FREEZE_AUDIT receipts=7 present=7 missing=0 tokens=6 matching=6 cited=8 unresolved=0 met=True`

Sources cited by the round: S593, S596, S604, S606, S613, S614, S615, S616, S617 (all resolve at the landed tip).
