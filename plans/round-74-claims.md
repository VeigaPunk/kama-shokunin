# kama round 74 — frozen claims

Frozen before any seat scored. Base revision `868dd701bff531be6a36da742d3418f98818e5eb`
(lane `master`, == `origin/master` at freeze). A rule changed after a seat has scored is not
this claim's rule (kumitate r42): a seat that disagrees reports a disagreement and never edits
this file. Predicate sentence, counter code and receipt label are the same sentence in all
three places.

Carry-in: the round-73 non-author closure (`corpus/lessons/round-73-verifier-spotcheck.md`)
graded round 73 an honest stop (B6 verified; the full frozen clean-fixture clause unprovable
on committed bytes) and routed six defects. Its §6 items 1, 2 and 5 are this round's C1, C2
and C3; item 3 (CRT01 classification ruling) is recorded in the round-74 calibration SCORECARD
row; item 4 (append-only history audit red) stays on the routed queue, disclosed, not
re-stamped; item 6 (gate-order: exit-0 mirror census before append) is this round's lesson
mistake 2 and its check tool. `SCORECARD.md` §Planned (round 74) items 1, 2, 3 are C1, C2, C3.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md
freshness conflict stays open at `.ufo/l0-questions.md:145`). Calibration 7 is the lane's
lowest non-retired assigned score (operability 8; depth/adjacency tie at 7 but are not
assigned), so C1 satisfies the lowest-axis duty.

C1, C2 and C3 are causally separable: each instrument runs and verifies with the other two
absent (three independent modules over three independent inputs — SCORECARD.md's capability
headings, the round self-record's receipt citations, PROVINCE.md's host blocks).

## C1 — calibration: the self-description reconciler sees the newest capability repertoire whatever heading form it wears (R73-D1)

Motivating evidence, measured at the base revision: `tools/round42-selfdesc-reconcile.py`'s
`canon()` matches only `canonical list as of round\s+(\d+)\*\*` — a BOLD heading with a
literal closing `**`. From round 72 the record's canonical lists are unbolded
(`## Capabilities — canonical list as of round 72`, `### Capabilities demonstrated in
round 73`), so at base `868dd701` `canon()` returns round **71** (17 rows) while the real
repertoire is 22 rows — the 22-operation record is invisible to the lane's self-description
reconciler. Base probe receipt: `.ufo/waves/round-74/measured/before/probe-canon-base.out`.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and
the receipt label):**

> `python3 tools/round74-selfdesc-canon.py --repo <lane>` prints one
> `SELFDESC_CANON_V2 canon_round=<N> canon_rows=<c> demonstrated=<d> total=<t> invisible=<i>`
> line and exits 0 only when `<lane>/SCORECARD.md` resolves its capability repertoire from the
> newest capability table by round number regardless of heading markup — bold `**Capabilities —
> canonical list as of round <M>**`, unbolded `## Capabilities — canonical list as of round <M>`
> and `### Capabilities demonstrated in round <M>` forms all count — and `invisible` names every
> capability a demonstrated-capabilities table newer than the newest bold canonical heading
> carries while the bold canon does not, requiring `invisible=0` so the record never relies on a
> form its own reconciler cannot see; it exits 1 naming each
> `SELFDESC_CANON_V2_FINDING invisible <round> <name>` and 2 when SCORECARD.md is unreadable or
> no capability table can be parsed.

- the module imports the byte-frozen `tools/round42-selfdesc-reconcile.py` (its `canon()` and
  table parser are reused, never copied); r42's bytes stay unchanged and its selftest stays
  green (5/5 arms). `total` counts the distinct names across the newest-by-round resolution;
  `demonstrated` counts the names added by tables newer than the bold canon.
- exit map: `0` clean (`invisible=0`), `1` findings, `2` could-not-evaluate (CLI misuse, not a
  git repository, SCORECARD.md missing/unreadable).
- wiring: `tools/pre-report-gate.py` arm 7 composes this module with the C2 and C3 modules;
  the gate verdict becomes `PRE_REPORT round=<N> arms=7 failed=<f> uncommitted=<u>`.
- Counting command: `python3 .ufo/waves/round-74/controls/score-survivors.py`.
- Kill rule: fixture `c1_invisible` (built by `.ufo/waves/round-74/controls/build-survivors.py`)
  — a SCORECARD whose newest repertoire additions live only under unbolded
  `### Capabilities demonstrated in round 73/74` tables with the newest bold canon at round 71 —
  makes the base `canon()` resolve round 71 while the hand census counts every demonstrated
  name; the v2 counter must resolve `total=7`, print `invisible=4` and exit 1 naming each
  invisible capability. Fixture `c1_clean` — the same record plus a bold
  `**Capabilities — canonical list as of round 74**` covering all seven names — must exit 0
  with `total=7 invisible=0`. The round-74 record commit adds the bold round-74 canonical list
  (22 rows) so the live run exits 0.
- Control that skips the claimed work (built before the freeze, scored with the frozen
  counter): the byte-frozen r42 `canon()` run over `c1_invisible` resolves round 71, not the
  demonstrated rounds — structurally unable to report them, which is the hole. Receipt:
  `measured/before/score-survivors-base.out`.

Non-goals: the module grades heading visibility only; it does not re-grade the reconciler's
other arms (banner, planned, closure pointer) and does not edit SCORECARD.md.

## C2 — operability: the tip-claim rule is realizable — an explicit-revision binding that kills wrapped and offset claims and binds hex case-insensitively

Motivating evidence: the round-73 closure's item 2 — the frozen clean clause "a receipt
header equal to the tip" is a git hash fixed point and cannot exist on committed bytes; the
r73 module's claim pass is line-scoped, so a tip claim split across lines or separated from
its citation escapes (`corpus/lessons/round-73-verifier-spotcheck.md` §2 C2). The round-73
record itself already answers with explicit revisions ("re-run at revision `2e3ca867`"), which
the r73 rule cannot bind. Control receipt:
`.ufo/waves/round-74/measured/before/score-survivors-base.out` (`SURVIVORS c2 base_green=2` —
the `c2_wrapped` and `c2_offset` fixtures pass the r73 counter).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and
the receipt label):**

> `python3 tools/round74-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>`
> prints one
> `RECEIPT_CLAIM_V2 round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j> bound_revisions=<r>`
> line and exits 0 only when the byte-frozen `tools/round72-receipt-tip-binding.py` verdict for
> `<rev>` is green and every blank-line-separated paragraph of the round's self-record (the
> `## Round <N>` section of `SCORECARD.md` and `corpus/lessons/round-<N>.md` at `<rev>`) that
> both cites a receipt and carries a tip claim (`at the tip`, `at the report tip`,
> `report tip`, case-insensitive, matched across line breaks inside the paragraph) has every
> cited receipt whose own `tip=`/`rev=` header (case-insensitive key and hex) names `<rev>`;
> a paragraph that names an explicit 40-hex revision binds each cited receipt whose header
> equals that revision (hex compared case-insensitively), and is a finding when the header
> differs; it exits 1 naming each base finding and each
> `RECEIPT_CLAIM_V2_FINDING <wrapped-claim|offset-claim|stale-revision> <path> :: <line>`, and
> 2 when the base tool or the self-record cannot be evaluated.

- paragraph scoping: the record is split on blank lines; a claim token split across hard line
  breaks (`wrapped-claim`) or standing on a different line of the paragraph than its citation
  (`offset-claim`) is still paired and graded — the line-scoped r73 pass is the hole being
  closed.
- the realizable clean rule replacing the impossible committed-header-equals-tip clause: a
  record paragraph that names the receipt's own explicit revision (`re-run at revision <r>`)
  and whose cited receipt's header equals `<r>` is bound — committable because `<r>` names an
  ancestor commit, never the commit containing the record.
- composition: the module shells out to the byte-frozen `tools/round72-receipt-tip-binding.py`
  and may import but never edit `tools/round73-receipt-claim-binding.py`; both stay unchanged
  and their selftests stay green (16/16 and 14/14).
- exit map: `0` clean, `1` findings (base or claim), `2` could-not-evaluate (base tool absent
  or exit 2, self-record unreadable, CLI misuse).
- Counting command: `python3 .ufo/waves/round-74/controls/score-survivors.py`.
- Kill rule: fixtures `c2_wrapped` (claim token split across two lines, citation in the same
  paragraph, receipt header rev=A≠tip) and `c2_offset` (token on line 1, citation on line 2
  of one paragraph, receipt header rev=A≠tip) each make the r73 counter exit 0 (claim
  uncounted) and must make the v2 counter exit 1 naming `wrapped-claim` / `offset-claim`;
  fixture `c2_mixed_honest` (record names the receipt's revision in upper-case hex, header in
  lower case, no tip claim) must exit 0 with `bound_revisions=1` — a case-sensitive v2
  implementation fails this arm; fixture `c2_clean_realizable` (record names the receipt's own
  revision, header equal) must exit 0 — the clean arm that replaces the impossible rule.
- Control that skips the claimed work: the byte-frozen r73 counter run over `c2_wrapped` and
  `c2_offset` exits 0 on both (`base_green=2`). Receipt: `measured/before/score-survivors-base.out`.

Non-goals: the binding does not prove a receipt's content is honest; it binds the claim to
the revision the receipt names. A receipt naming no revision stays `unbound` under the base
tool's rules, unchanged.

## C3 — freshness: a host block cannot be edited into matching the live host — base-revision preservation (R73-D5)

Motivating evidence: the round-73 closure's item 5 — "host blocks currently have no
base-revision option; a later edit could move the recorded triple without a finding". The r73
counter grades only the newest block's triple against the live triple, so a block edited
after recording (instead of appending a new one) passes whenever its edited bytes match the
live host. Control receipt:
`.ufo/waves/round-74/measured/before/score-survivors-base.out` (`SURVIVORS c3 base_green=1` —
the `c3_edited` fixture passes the r73 counter).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and
the receipt label):**

> `python3 tools/round74-province-host-drift.py --repo <lane>` prints one
> `PROVINCE_HOST_DRIFT_V2 blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n> edited=<e>`
> line and exits 0 only when the byte-frozen `tools/round73-province-host-drift.py` verdict for
> `<lane>` is green and every host-identity block carrying a `recorded at <rev>` token has
> byte-identical block text at `<rev>` and at the worktree tip, so that a block whose recorded
> triple, date or any other byte changed after its recorded revision is a finding even when
> the edited block matches the live triple; it exits 1 naming
> `PROVINCE_HOST_DRIFT_V2_FINDING <no-block|stale-host|edited-block> <detail>` and 2 on
> could-not-evaluate (PROVINCE.md unreadable, a `recorded at` rev unresolvable, CLI misuse).

- the lane's own newest block (Round-73) gains the token `recorded at 868dd701…` (this
  round's base) in the round-74 record commit; appending a new block remains the honest answer
  to a host move, never editing.
- composition: the module runs the byte-frozen r73 counter as its base leg and adds the
  preservation leg; r73's bytes stay unchanged and its selftest stays green (9/9).
- exit map: `0` clean (`stale=0 edited=0`), `1` findings, `2` could-not-evaluate.
- Counting command: `python3 .ufo/waves/round-74/controls/score-survivors.py`.
- Kill rule: fixture `c3_edited` — a block recording this host's live triple
  (`Linux`/`x86_64`/`arch`) at revision A with a `recorded at A` token, then a commit editing
  the block's date byte — keeps the r73 counter green (newest block still matches live) and
  must make the v2 counter exit 1 naming `edited-block`; fixture `c3_clean` (same block
  unchanged after A) must exit 0 with `edited=0`.
- Control that skips the claimed work: the byte-frozen r73 counter run over `c3_edited` exits
  0 (`base_green=1`). Receipt: `measured/before/score-survivors-base.out`.

Non-goals: the block records a host identity triple, not a serving surface and not unique
physical-machine identity (`tools/round71-province-host-claims.py` keeps grading surfaces,
unchanged). Nothing on the host is written.

## Frontier step (rides inside the claim cap; no fourth claim)

- Sourced claim: **C3** rests on a row opened this round for `os-release(5)`
  (man7.org/linux/man-pages/man5/os-release.5.html): the `ID=` field semantics that ground
  the triple's distribution component, cited by the claim's knowledge entry
  `corpus/knowledge/host-block-base-revision.md`. The row is opened live this round (access
  date, ≤25-word located quote, retained bytes) and appended only after the scratch-mirror
  census gate exits 0.
- Mistakes mined into `corpus/lessons/round-74.md` §Mistakes:
  1. `number-drift` — the r73 wave spec's prose said "14 seats" while its `items` array
     carried 15; the fix `tools/round74-seat-count-check.py` recomputes the count from the
     spec's items and fails on the r73 spec bytes (red demo committed).
  2. `landing` (routed defect 6) — r73's registry append preceded the first exit-0
     scratch-mirror census; the round-74 runbook fixes the order and the check tool's
     `census-before-append` arm demonstrates the failure class on a replayed ordering.
- Assimilation: none is adopted (no `merge/kama/` entry is re-grounded this round); the
  id-collision check and the quarantine slice still run, receipts committed under
  `.ufo/waves/round-74/assimilation/`.
- considerthese: `considerthese/2026-10-26.md` re-opened; proposal 4 (pin-gap line) landed in
  round 73; proposals 1–3 are daily-pass workflow, not lane-round work; nothing adopted. The
  disposition lands in the lesson.
- Routed defect 3 (CRT01 classification): recorded in the round-74 calibration SCORECARD row —
  the executable git-state instrument surface (round-scope / receipt-binding family) is
  **calibration**: it counts mismatches between the lane's self-assessment and observed repo
  state, per AXES.md's calibration definition; coverage credit would require new domain
  ground, which these instruments do not hold.

## Freeze control

`controls/freeze.txt` pins `git -C <lane> rev-parse master` (the base line), the sha256 of
this plan, the sha256 of the two control scripts, and the before-receipt sha256s. The control
was run from the base bytes before any seat scored.
