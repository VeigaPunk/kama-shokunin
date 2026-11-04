source: S546 — Linux os-release(5), https://man7.org/linux/man-pages/man5/os-release.5.html (docs, tier A, queued→mined on this entry, accessed 2026-11-04; row in `corpus/SOURCES.md`): §OPTIONS `ID=` — "A lower-case string … identifying the operating system, excluding any version information and suitable for processing by scripts". The field's semantics ground the distribution component of the host-identity triple; it does not ground that the triple identifies one physical host.
verified-at: 2026-11-04 — plan `plans/round-74-claims.md` §C3 (frozen predicate, block grammar, exit map) read; the source page fetched live this date (sha256 c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e, retained at `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html`); the r73 counter `tools/round73-province-host-drift.py` read as the frozen base leg. No counter run is claimed here.
recheck: 180d — `curl -sSfL https://man7.org/linux/man-pages/man5/os-release.5.html` and re-locate the §OPTIONS `ID=` entry.

# Host block base-revision preservation — the v2 block grammar

Round 73's counter answers "is the recorded host the host we are on?" by grading the
**newest** host-identity block's triple against the live triple. Round 74 closes the hole
the closure recorded (r73 routed defect 5): the r73 counter cannot see a block **edited**
after recording. A block whose bytes were changed to match the live host after the fact
passes the r73 leg whenever its edited triple equals the live one — the edit is invisible.

## The block grammar (v2)

`PROVINCE.md` carries one paragraph per observation, first line:

    Round-<N> host-identity block (YYYY-MM-DD)

and, in its text, the three identity tokens — the `uname -s` value (kernel name), the
`uname -m` value (machine hardware name), and the `ID=` field of `/etc/os-release`
(parsed, never sourced) — plus, new in round 74, a base-revision token:

    recorded at <rev>

`<rev>` names the commit the block's bytes are committed at: the round-74 record commit
tags the lane's newest block `recorded at 868dd701…`, this round's base revision.

## The preservation rule

A host block carrying a `recorded at <rev>` token must be **byte-identical** at `<rev>`
and at the worktree tip: the block text with the `recorded at <rev>` token sentence
stripped must equal the block text at `<rev>`. Any other byte of the block — the recorded
triple, the date, any surrounding sentence — that differs between `<rev>` and the tip is a
finding (`edited-block`), **even when the edited block matches the live triple**. Matching
the live host is what the base leg grades; preservation is what stops a retrospective
edit from manufacturing that match. The token sentence is stripped because the token
names the revision the comparison runs at — it cannot be present in the block's bytes at
`<rev>` when a later commit added it (the lane's Round-73 block, tagged
`recorded at 868dd701…` at the round-74 record commit, states this convention in its own
text). The v2 counter composes the byte-frozen r73 counter as its base leg and adds this
preservation leg; r73's bytes stay unchanged.

## The honest host-move answer

Append, never edit. A host move is answered by appending a later block carrying a fresh
`recorded at` token for the commit that appends it; the older block stays byte-identical
at its own revision. The round-73 knowledge entry's append-only policy is thereby enforced
by a counter, not only stated.

## Why os-release ID= is the third component

S546 grounds the semantics of the triple's distribution component: os-release(5) defines
`ID=` as "a lower-case string … identifying the operating system, excluding any version
information and suitable for processing by scripts" (§OPTIONS, `ID=` entry). So the block
records distribution identity without version noise (`VERSION_ID` deliberately unread —
a distribution upgrade-in-place is a host move answered by append, not a stale triple),
and the token is stable enough to compare as a string across revisions. The `ID_LIKE=`
fallback field is explicitly not read: the triple asserts the actual distribution.

## What this does not show

- **Not host uniqueness.** As the round-73 scope correction states, two machines sharing
  kernel family, hardware architecture and distribution share this triple; S546 supports
  the `ID=` field's semantics, not one-box identity.
- **Not a serving surface.** `tools/round71-province-host-claims.py` keeps grading declared
  `province-host:` surfaces, unchanged.
- **Not receipt honesty.** Like a receipt header, the block and its token are
  self-declared text; the preservation leg grades byte-stability between two revisions,
  not that the recorded triple was ever measured.
