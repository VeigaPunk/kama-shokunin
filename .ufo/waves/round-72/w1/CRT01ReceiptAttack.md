# CRT01ReceiptAttack — attack on C2 on the landed bytes (seat report)

Seat `CRT01ReceiptAttack` (critic; axis operability), kama round 72, wave 1.
Target: `tools/round72-receipt-tip-binding.py`, bytes
`sha256 a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd` (36406 B, mtime
2026-11-03 22:49:56 -0300, **untracked** at lane tip `a3cc39f0`). Full ledger:
`.ufo/waves/round-72/w1/CRT01ReceiptAttack/attack.md` and the receipts beside it.

The tool moved three times during the attack (32842 B → 33760 B `ef3d6fd5` → 36346 B `025a070e`
→ 36406 B `a9a4e8d3`); every verdict below was re-run on `a9a4e8d3`, sha identical before and
after the run. An out-of-tree receipt binding is what the claim asks for; the instrument's own
bytes have none.

**Rig validity.** Four controls reproduce the frozen kill rule on throwaway repos: clean → exit 0
`cited=1 bound=1`; headerless → 1 `unbound`; side-branch header → 1 `shifted`; deleted receipt → 1
`stale`; delta touching `tools/gate.py` → 1 `shifted`. The frozen before-control re-runs exactly:
`BINDING_CONTROL cited=3 accepted=3 rejected=0`, exit 1.

## The six assigned attacks

| # | fixture | exit | verdict line | in the kill rule? |
|---|---|---|---|---|
| B1 | header names a plausible ancestor taken after the measurement, before an unrelated record commit | **0** | `round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0` | **no** |
| B2 | header names the tip; receipt bytes produced before an instrument edit later reverted | **0** | `bound=1` (see §B2 note) | **no** |
| B3 | brace expansion `{before,after}.out`, second member absent | 1 | `cited=2 bound=1 stale=1 … after/gate.out` | yes — killed |
| B4 | citation inside a fence / HTML comment | 0 / 1 | fenced+backticked *absent* path → `stale` (false positive); fenced *present* receipt → `cited=2 bound=2` (documentation counted); HTML comment → `unbound` (read) | no — undeclared either way |
| B5 | record-path default swallows `tools/` | 1 | `shifted … tools/gate.py touched by …` — default list is exactly the frozen list | yes — killed |
| B6 | receipt committed after the instrument commit, graded against the earlier revision (r71 defect-4 shape) | **0** | `bound=1` | **no** |

**B2 note.** A receipt that exists at tip `T` and names `T` in its own bytes is a git hash fixpoint
(`T = f(tree(T))`), so "empty delta" is unconstructible; the reachable forms are B2 (instrument
edit before the header) and B6 (record-only delta), and both are bound.

## Decisive counterexample — the motivating evidence, on real bytes

`git clone --shared` at `7fb6cb4e`, the round-71 self-record reduced to one citation of
`measured/after/pre-report-at-tip.out` (real committed blob, header `# tip=4b2846535fd9…`,
tip two commits later, delta = the round's receipts + the lesson):

    RECEIPT_TIP_BINDING round=71 cited=1 bound=1 unbound=0 shifted=0 stale=0
    exit: 0

The C2 counter **certifies the defect C2 was written to remove**. On the record as written it
cannot even grade: `--round 71 --tip 7fb6cb4e` → exit 2, `cited path is not a receipt file (.py):
.ufo/waves/round-71/controls/pre-report-shortcut.py (SCORECARD.md:3766)`. With the record's
non-receipt tokens neutralised (scratch clone): `cited=30 bound=9 unbound=7 shifted=3 stale=11`,
and all 11 `stale` findings are bare-basename artifacts (files exist under `measured/after/` or
`w1/`; the tool resolves a bare name to the wave root).

## Survivors and the exact predicate gap each exposes

1. **B1** — nothing ties the receipt's bytes, or its committing commit, to the header revision; any
   record-only-separated ancestor is bound. *Fix:* require no instrument-input commit in
   `receipt_intro..tip`.
2. **B2/B2r** — clause 4 is one-sided (`header..tip`), so instrument history before the header is
   never examined (a reverted edit is invisible too). *Fix:* same `rev-list receipt_intro..tip`
   check, which is strictly wider.
3. **B6** — the delta criterion grades paths, not the claim; a record-only delta is the normal round
   shape, so a receipt that measured an earlier revision passes. *Fix:* grade the citing line — a
   line that says "at the tip"/"report tip" with a header that is not the tip is a finding.
4. **B9** — the receipt's own history is never read: a later record-only commit can rewrite the
   body while the header keeps naming the measured revision. *Fix:* the blob's last-change commit
   must be its introducing commit.
5. **G7** — a *prose* `tip=<sha>` in the first five lines counts as a header, so the `unbound` class
   is dodgeable; the predicate asks for a header. *Fix:* anchor to `^\s*#\s*(tip|rev)=`.
6. **B4a2/B4c** — fenced documentation is graded as citations (false `stale` on an example, inflated
   `cited`/`bound` on a present receipt), while the fence rule is declared nowhere. *Fix:* one rule
   for fences and comments, declared in the docstring.
7. **H1b/E10b** — the verdict line does not name the allow-list it used, and `--record-path` may add
   `tools/`; a citation's grade flips between exit 0 and exit 2 depending on whether the cited
   non-receipt file has landed. *Fix:* print the record-path digest on the line; unlanded non-receipt
   citation → `stale`.

Two measured operability harms that are not predicate gaps: **E10/E11** — any *committed* wave-dir
citation of a non-receipt file aborts the run with exit 2 (the frozen exit map requires it, so the
sentence is the defect: the lane's records cite control scripts and seat reports); and **bare
basenames** resolve to the wave root instead of the receipt's directory (11 spurious `stale` on the
r71 record — resolve a basename against the wave tree, unique hit binds, none is `stale`).

## Freeze disagreements (reported; not edited)

D1 `<rev>` captured twice (tip vs header rev; one reading makes `shifted` dead — the tool takes the
other). D2 the B2 "empty delta" shape is unconstructible. D3 "a cited path that is not a receipt
path → exit 2" conflicts with the tool's own repo-root out-of-scope rule (`B10b` exits 0). D4 the
kill rule does not name the motivating defect (live proof above). D5 the counting command cannot run
on the round-72 record yet (`## Round 72` absent at `a3cc39f0`) and on r71 only with exit 2.

## Commands run (all from the fleet root unless noted)

* 38 fixtures: `python3 tools/round72-receipt-tip-binding.py --repo <fixture> --round 72 --tip master`
  — per-case exit and verdict in `w1/CRT01ReceiptAttack/fixtures.out`.
* `python3 tools/round72-receipt-tip-binding.py --repo . --round 72 --tip master` → exit 2,
  `UNREADABLE … no '## Round 72' section` (`live-lane.out`).
* `python3 tools/round72-receipt-tip-binding.py --repo . --round 71 --tip 7fb6cb4e` → exit 2,
  `UNREADABLE … not a receipt file (.py) … SCORECARD.md:3766` (`live-lane.out`).
* clone experiment, reduced record: exit 0, `round=71 cited=1 bound=1 …` (`live-r71-min.out`).
* clone experiment, neutralised citations: exit 1, `cited=30 bound=9 unbound=7 shifted=3 stale=11`
  (`live-r71-neutralised.out`).
* `python3 .ufo/waves/round-72/controls/receipt-tip-control.py --work <scratch>` →
  `BINDING_CONTROL cited=3 accepted=3 rejected=0`, exit 1 (`control-repro.out`).

## Files written

`.ufo/waves/round-72/w1/CRT01ReceiptAttack.md` (this report) and, under
`.ufo/waves/round-72/w1/CRT01ReceiptAttack/`: `attack.md`, `fixtures.out`, `live-r71-min.out`,
`live-r71-neutralised.out`, `live-lane.out`, `control-repro.out`, `tool-bytes.txt`, and the three
fixture drivers (`build_attacks.py`, `live_r71.py`, `live_r71_min.py`). No lane byte was edited; no
tool byte was edited; scratch is removed at close.
