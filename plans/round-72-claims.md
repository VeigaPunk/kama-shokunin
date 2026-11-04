# kama round 72 — frozen claims

Frozen before any seat scored. Base revision `d30a8696` (lane `master`, == remote at freeze).
A rule changed after a seat has scored is not this claim's rule (kumitate r42): a seat that
disagrees reports a disagreement and never edits this file. Predicate sentence, counter code
and receipt label are the same sentence in all three places.

Carry-in: the round-71 non-author closure (`corpus/lessons/round-71-verifier-spotcheck.md`)
ruled round 71 **admitted** and routed five status-neutral defects; its §8 item 4 is this
round's C2 motivating evidence, and the round-71 lesson's `## Ceiling`/routing block names the
three C1 survivors this round kills. Planned items 1 and 2 of `SCORECARD.md` §Planned
(round 72) are C1 and C2 respectively.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration is tied for the lane's
lowest non-retired score (7, with depth and adjacency), so C1 satisfies the lowest-axis duty.
C1 and C2 sit on distinct axes and are causally separable: C2's gate runs and verifies with C1's
module absent, and C1's module runs and verifies with C2 absent.

## C1 — calibration: the pre-report cleanliness arm cannot be satisfied vacuously

Motivating evidence, measured at the base revision: the round-71 gate's fifth arm grades
`git status --porcelain -uall -- .ufo/waves/round-<N>` only, so (i) a wrong `--round` label points
at a directory that does not exist and the arm prints `files=0`, (ii) round work outside the wave
dir is invisible, (iii) a git-ignored file inside the wave dir is invisible. Receipt:
`.ufo/waves/round-72/measured/before/round-scope-control-old.out` (`SCOPE_CONTROL cases=3
base_green=3 killed=0`, exit 1).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant, the
gate's arm-6 docstring and the receipt label):**

> `python3 tools/round72-round-scope.py --repo <lane> --round <N> --tip <rev>` prints one
> `ROUND_SCOPE round=<N> cases=3 findings=<f>` line and exits 0 only when the round's frozen
> claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round
> `<N>`, no path outside the declared record allow-list is uncommitted, and no path under
> `.ufo/waves/round-<N>/` is git-ignored; it exits 1 naming every finding as
> `ROUND_SCOPE_FINDING <case> <detail>`.

- cases: `label` (A), `stray` (B), `ignored` (C). `findings` counts named findings; `cases=3` is
  the fixed case population. Case A anchors on the lane's own `plans/round-<N>-claims.md` rather
  than the fleet prompt `.ufo/prompts/kama-round-<N>.md`: the prompt lives in the fleet repo, is
  not a lane path, and cannot be read at a lane tip.
- **Freeze amendment, 2026-11-03T22:45 -03, before any seat returned a score**: case A's anchor
  was first frozen as the fleet prompt path, which does not exist in this repo
  (`git cat-file -e master:.ufo/prompts/kama-round-72.md` -> exit 128 at the freeze commit). The
  predicate was unexecutable as first written; the anchor moved to the lane-owned freeze plan,
  nothing else changed, and the pre-score control receipt was re-taken against the amended
  fixture set. Mined as a mistake in `corpus/lessons/round-72.md`.
- exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, not a git repository,
  unevaluable fixture).
- The arm enters the pre-report gate as arm 6 `round-scope`; the gate's verdict becomes
  `PRE_REPORT round=<N> arms=6 failed=<f> uncommitted=<u>` and its predicate string is amended
  in the same commit (the five-arm string stays as the round-71 historical measurement).
- Counting command: `python3 tools/round72-round-scope.py --repo . --round 72 --tip master`.
- Kill rule: each of the three defect fixtures (missing prompt, one uncommitted file at the repo
  root, one ignored file inside the wave dir) exits 1 and names its case; the clean fixture
  exits 0; a fixture that cannot be built is exit 2, never a pass.
- Control that skips the work (built before the freeze, scored with the frozen counter): the
  control harness runs the base gate's arm command (`git status --porcelain -uall -- <wave>`) on
  the three fixtures — all three print no record, i.e. the base state is vacuous green. The
  control receipt is the before-measurement above; if the frozen counter cannot kill all three,
  the counter or the target is wrong and no data is taken.

Non-goals: no product/serving claim; the module grades git state only. An ignored path the lane
deliberately ships under its wave dir is a finding by design (`--allow-ignored` is not offered;
a round that needs one declares it in this plan first).

## C2 — operability: every receipt the round cites names the revision it measured

Motivating evidence: round-71 spot-check §8 item 4 — the round-71 report described
`measured/after/pre-report-at-tip.out` as running "at the report tip" while the receipt header
names `4b284653`, two commits before the measured tip; the lesson's final-receipts block is a
hand-written invariance argument ("the only commits after it add receipts") that no command
checks. Receipt: `.ufo/waves/round-72/measured/before/receipt-tip-control-old.out`
(`BINDING_CONTROL cited=3 accepted=3 rejected=0`, exit 1 — the shortcut accepts every planted
defect).

**Predicate (frozen, verbatim — same sentence in the tool's `PREDICATE`, the SKILL.md registry
row and the receipt label):**

> `python3 tools/round72-receipt-tip-binding.py --repo <lane> --round <N> --tip <rev>` prints one
> `RECEIPT_TIP_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t>` line and
> exits 0 only when every receipt path cited by the round's self-record (`SCORECARD.md`'s
> round-`<N>` section and `corpus/lessons/round-<N>.md`) exists at `<rev>`, carries a
> `# tip=<40-hex>` or `# rev=<40-hex>` header, names a revision that is an ancestor of `<rev>`,
> and every commit in `<rev>..<tip>` touches only declared record paths; it exits 1 naming each
> `RECEIPT_TIP_FINDING <unbound|shifted|stale> <path>`.

- record paths (default, `--record-path` replaces the default list): `.ufo/waves/round-<N>/**`,
  `corpus/lessons/**`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`.
- instrument inputs (never record paths): `tools/**`, `SKILL.md`, `PROVINCE.md`,
  `corpus/SOURCES.md`, `corpus/knowledge/**`, `registry/**`, `plans/**`. A commit in the delta
  touching one of them is `shifted`, naming the path.
- exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, unreadable self-record,
  a cited path that is not a receipt path, **or `cited=0` — an empty population is never a pass,
  the same vacuous-green class C1 kills**).
- Counting command: `python3 tools/round72-receipt-tip-binding.py --repo . --round 72 --tip master`.
- Kill rule: a receipt with no header (`unbound`), a header naming a non-ancestor or a revision
  whose delta touches `tools/` (`shifted`), and a cited receipt absent at the tip (`stale`) each
  exit 1 and name their class; the clean fixture exits 0.
- Control that skips the work: count the cited receipt paths and require the count to be
  non-zero — that is the shortcut the round-71 practice actually used. It accepts all three
  defect fixtures (`BINDING_CONTROL accepted=3`), so it cannot satisfy the target; the receipt
  is the before-measurement above.

- **Freeze amendment 2, 2026-11-03T22:50 -03, before any seat returned a score**: the zero-citation
  run is now exit 2. Without it a self-record that cites no receipt at all would be vacuously green
  (`every cited receipt ...` is true of the empty set) — the exact class C1 kills. The selftest
  carries an arm for it; the frozen sentence's "exits 0 only when every receipt path ... names a
  revision ..." is unchanged, the exit map gains the empty-population refusal.

Non-goals: the binding does not prove a receipt's *content* is honest (C1's module and the
existing instruments grade that); it binds a receipt to the revision whose bytes it graded.

## Frontier step (rides inside the claim cap; no fourth claim)

- Sourced claim: **C2** rests on **S175** (`git merge-base --is-ancestor` exit-status semantics,
  re-opened this round with this lane's own access date and located quote); **C1** rests on
  **S542** (porcelain v1 stability, re-opened) and on a new row for `git-check-ignore`'s
  ignored-path verdict if the census admits it.
- Assimilation: none this round — the round is sized to two instrument claims; the
  `shoukuknow/merge/kama/` package keeps its round-71 decision (no entry re-grounded, nothing
  adopted). The id-collision check runs anyway and its receipt is committed.
- considerthese: no still-unimplemented proposal in `considerthese/2026-10-26.md` matches two
  instrument claims; the disposition is recorded in the lesson.

## Freeze control

`git -C <lane> rev-parse master` == `.ufo/waves/round-72/controls/freeze.txt` base line.
The control receipts above are produced from the base bytes before any seat runs, and are
committed with this plan.
