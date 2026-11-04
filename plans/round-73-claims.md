# kama round 73 — frozen claims

Frozen before any seat scored. Base revision `6e961996` (lane `master`, == `origin/master` at
freeze). A rule changed after a seat has scored is not this claim's rule (kumitate r42): a seat
that disagrees reports a disagreement and never edits this file. Predicate sentence, counter code
and receipt label are the same sentence in all three places.

Carry-in: the round-72 non-author closure (`corpus/lessons/round-72-verifier-spotcheck.md`) ruled
round 72 **admitted** (both claims verified on re-measurement; no axis harmed; scores held
operability 8 / calibration 7) and routed seven status-neutral defects. Its §6 items 1, 6 and 7 are
record corrections landed with this round's record; items 2 and 3 are C2 and this plan; item 4 is
the lesson's `## Gate`; item 5 is the report's stale-lane line. `SCORECARD.md` §Planned (round 73)
items 1 and 2 are C1 and C2; item 3 is C3, re-scoped: the province counter already re-probes live,
so the host-move class is a *recorded host identity vs live host* grading, not a second copy of the
same probe.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration is tied for the lane's
lowest non-retired score (7, with depth and adjacency), so C1 satisfies the lowest-axis duty.

C1, C2 and C3 are causally separable: each instrument runs and verifies with the other two absent
(three independent modules over three independent inputs — git worktree state, a self-record's
citations, PROVINCE.md's host block).

## C1 — calibration: the round-scope counter kills the three survivors its own claim recorded

Motivating evidence, measured at the base revision and recorded by the round-72 closure: round 72
claimed "the pre-report cleanliness arm cannot be satisfied vacuously", yet three named classes
still pass its counter (`corpus/lessons/round-72-verifier-spotcheck.md` §6, and
`.ufo/waves/round-72/w1/RVW01RoundScopeAttack/attack.md`: A5 linked-worktree dirt, A6 a valid
older-round label hiding another round's ignored work, A7 `submodule.<name>.ignore=all`). That is a
calibration mismatch between the lane's self-assessment and observed repo state — 3 of 3 survivors
pass. Pre-freeze control receipt, measured with the base counter:
`.ufo/waves/round-73/measured/before/score-survivors-base.out`
(`SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round73-round-scope-cases.py --repo <lane> --round <N> --tip <rev>` prints one
> `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` line and exits 0 only when the round's frozen
> claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round `<N>`,
> no path outside the declared record allow-list is uncommitted in the primary worktree or in any
> linked worktree of the repository, no path under a `.ufo/waves/round-<M>/` directory with
> `M >= <N>` is git-ignored, and every initialized submodule worktree has no uncommitted or
> untracked content; it exits 1 naming every finding as `ROUND_SCOPE_V2_FINDING <case> <detail>`.

- case population, fixed at 6 in this order: `label`, `stray`, `ignored` (the three inherited
  cases, same semantics as `tools/round72-round-scope.py`, which stays byte-frozen), plus
  `worktree` (A5: every linked worktree from `git worktree list --porcelain`, its
  `git status --porcelain -uall` graded like `stray`), `ignored-older-label` (A6: every
  `.ufo/waves/round-<M>/` directory present in the worktree with `M >= <N>`, its ignored records
  graded; older rounds' committed-then-ignored leftovers such as `__pycache__/*.pyc` are outside
  the population by the `M >= <N>` bound) and `submodule` (A7: every initialized submodule path,
  its own `git status --porcelain -uall`, plus the parent status at
  `--ignore-submodules=none`).
- exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, not a git repository,
  `--tip` unresolvable, a git command failure, an unbuildable fixture). A scored run never exits 2
  for a finding.
- the module reuses `tools/round72-round-scope.py`'s inherited graders (imported, not copied) and
  leaves its bytes unchanged; the 16 r72 selftest arms stay green.
- wiring: `tools/pre-report-gate.py` arm 6 `round-scope` calls this module; the gate's verdict
  stays `PRE_REPORT round=<N> arms=6 failed=<f> uncommitted=<u>` (the arm name does not change).
- Counting command: `python3 .ufo/waves/round-73/controls/score-survivors.py`.
- Kill rule: each survivor fixture built by `.ufo/waves/round-73/controls/build-survivors.py`
  (`c1_a5`, `c1_a6e`, `c1_a7sub2`) exits 1 naming its new case; `c1_clean` exits 0; the inherited
  cases keep their r72 kill fixtures red.
- Control that skips the claimed work (built before the freeze, scored with the frozen counter):
  the unchanged r72 counter, run over the same three fixtures, accepts all three
  (`base_green=3`). It cannot satisfy the target, so the target is not reachable by doing nothing.
  Receipt: `measured/before/score-survivors-base.out`.

Non-goals: no product or serving claim; the module grades git state only. A round that needs an
ignored file under its own wave dir declares it in this plan first (no `--allow-ignored` escape).

## C2 — operability: every tip claim in the record names the revision its receipt measured

Motivating evidence: the round-72 closure's §6 item 2 and the r72 critic's B6 survivor
(`.ufo/waves/round-72/w1/CRT01ReceiptAttack/attack.md` line 116 and §S3): a receipt graded at an
earlier revision passes the binding gate because the delta is record-only, while the citing line
says "at the report tip" — exactly the r71 defect-4 shape KQ119 now names. The same closure recorded
the round-72 self-record red: `RECEIPT_TIP_BINDING round=72 cited=138 bound=0 unbound=105
shifted=24 stale=9`, exit 1. Control receipt, measured before the freeze:
`.ufo/waves/round-73/measured/before/score-survivors-base.out` (`SURVIVORS c2 base_green=1`, the B6
fixture accepted).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round73-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>` prints one
> `RECEIPT_CLAIM_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t>
> claims=<k> unbound_claims=<j>` line and exits 0 only when the base `RECEIPT_TIP_BINDING` verdict
> for `<rev>` is green and every self-record line that cites a receipt and answers it with a tip
> claim (`at the tip`, `at the report tip`, `report tip`) names a receipt whose own `tip=`/`rev=`
> header equals `<rev>`; it exits 1 naming each base finding and each
> `RECEIPT_CLAIM_FINDING stale-claim <path> :: <line>`, and 2 when the base tool or the self-record
> cannot be evaluated.

- composition: the module shells out to the byte-frozen `tools/round72-receipt-tip-binding.py`
  (same `--repo/--round/--tip`, default record paths) and adds the claim pass over the same record
  blobs at `<rev>` (`SCORECARD.md`'s `## Round <N>` section and `corpus/lessons/round-<N>.md`).
  `cited/bound/unbound/shifted/stale` are the base tool's numbers, echoed; `claims` counts citing
  lines carrying a tip claim, `unbound_claims` those where at least one cited receipt's header is
  not `<rev>`.
- exit map: `0` clean, `1` findings (base or claim), `2` could-not-evaluate (base tool absent or
  exit 2, unreadable self-record, CLI misuse).
- the round's own record must reach `unbound=0 shifted=0 stale=0 unbound_claims=0` at the record
  tip, under the base tool's unchanged population rules (KQ119 applied forward). r72's red record
  stays red as history; it is not repaired.
- Counting command: `python3 tools/round73-receipt-claim-binding.py --repo . --round 73 --tip master`
  plus `python3 .ufo/waves/round-73/controls/score-survivors.py`.
- Kill rule: the B6 fixture exits 1 naming `stale-claim`; a clean fixture (receipt header equal to
  the tip) exits 0; the base tool's own kill fixtures keep their classes.
- Control that skips the claimed work: the unchanged r72 binding gate accepts the B6 fixture
  (`base_green=1`). It cannot satisfy the target.

Non-goals: the binding does not prove a receipt's content is honest; it binds the claim to the
revision the receipt names. A receipt measured at an earlier revision is admissible when the citing
line names that revision instead of the tip.

## C3 — freshness: a host move is caught by a counter, not by a prompt

Motivating evidence: PROVINCE.md's round-65/67 notes described a Windows host the lane had left, and
only a hand-written round-71 re-derivation (14 contradicted surfaces) corrected it. The r71 counter
re-probes each declared surface against its marker, so it catches a host move only while a *marker*
contradicts; a third host move would leave every correction reading `present`/`absent` correctly
while PROVINCE.md's recorded host is wrong. No counter graded "the host this record describes is
the host we are on". Control receipt: `.ufo/waves/round-73/measured/before/score-survivors-base.out`
(`SURVIVORS c3 base_green=1`, the block-exists shortcut accepting a Windows triple).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round73-province-host-drift.py --repo <lane>` prints one
> `PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>` line and exits
> 0 only when `PROVINCE.md` carries at least one `Round-<N> host-identity block (YYYY-MM-DD)` whose
> recorded triple (`uname -s`, `uname -m`, the `ID` field of `/etc/os-release`) equals the live
> triple, the newest block being the one graded; it exits 1 naming
> `PROVINCE_HOST_DRIFT_FINDING <no-block|stale-host> <detail>` when no block exists or the newest
> block's triple differs from the live one.

- block grammar: a paragraph whose first line matches
  `Round-<N> host-identity block (YYYY-MM-DD)` and whose following text carries the three triple
  tokens; the newest block in file order is the graded one (append-only file), so a host move is
  answered by appending a new block, never by editing the old one.
- a kernel-only update does not move the triple (`uname -s`, `uname -m` and `/etc/os-release` `ID`
  are stable across it); a machine or OS change does.
- exit map: `0` clean, `1` findings, `2` could-not-evaluate (PROVINCE.md unreadable, CLI misuse).
- Counting command: `python3 tools/round73-province-host-drift.py --repo .` plus
  `python3 .ufo/waves/round-73/controls/score-survivors.py`.
- Kill rule: `c3_stale` (a Windows triple) exits 1 naming `stale-host`; a block-less fixture exits
  1 naming `no-block`; the live lane exits 0.
- Control that skips the claimed work: a `block-exists` shortcut accepts `c3_stale` (`base_green=1`).

Non-goals: the block records a host identity, not a serving surface; `tools/round71-province-host-claims.py`
stays unchanged and keeps grading the surfaces. Nothing on the host is written.

## Frontier step (rides inside the claim cap; no fourth claim)

- Sourced claim: **C3** rests on a row opened this round for `uname(1)` (`uname -s`, `uname -m`
  semantics); **C1** rests on a row opened this round for `gitmodules(5)`'s
  `submodule.<name>.ignore`; **C2** re-opens **S175** (`git merge-base --is-ancestor`) and **S542**
  (porcelain v1). Every new row is opened live with this lane's access date, a <=25-word located
  quote and retained bytes, and appended only after a scratch-mirror census gate exits 0.
- Assimilation: none this round — no `merge/kama/` entry is re-grounded, so nothing is adopted; the
  id-collision check still runs and its receipt is committed under
  `.ufo/waves/round-73/assimilation/`.
- considerthese: `considerthese/2026-10-26.md` proposal 4 (one pin-gap line per pinned engine each
  round) is still unimplemented; it lands as a `corpus/QUALITY.md` criterion plus this round's real
  `pin-watch` run, and the disposition is recorded in the lesson.
- Mistake to mine: the round-72 C2 tally/line-count copied between records instead of re-run
  (r72 closure §6 item 1) is this round's mined class, with the r73 re-derivation as its fix.

## Freeze control

`controls/freeze.txt` pins `git -C <lane> rev-parse master` (the base line), the sha256 of this
plan, the sha256 of the two control scripts, and the before-receipt sha256s. The control was run
from the base bytes before any seat scored.
