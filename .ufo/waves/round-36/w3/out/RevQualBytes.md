# RevQualBytes — KQ45 block review (round 36, wave 3)

Seat: leaf reviewer, quality axis. Target: the KQ45 block at the end of
`corpus/QUALITY.md` (heading line 318, row line 322). QUALITY.md was not edited.
All reads; the only write is this report.

## Measured results (re-derived this session, working tree unless noted)

- KQ45 block read in full (QUALITY.md:318–322). It requires, for every new
  SOURCES row, that the located quote be checked against the source bytes at
  the cited anchor in the round that writes the row; verbatim-labeled quotes
  byte-exact; defects (dropped word, stripped markup, wrong line) corrected by
  an appended superseding row, never by editing the quoted cell; unreachable
  sources recorded as unverifiable-by-fetch, not drift.
- Enumerated all 44 earlier criteria (KQ1–KQ44, QUALITY.md lines 9–316) and
  grepped `quote|verbatim|anchor` (hits at lines 11, 29, 30, 41, 61, 72, 121,
  123, 144, 164, 177, 203, 268). No hit is a landing-time quote-at-anchor check
  of a new SOURCES row.
- S174 fact: `corpus/SOURCES.md:186` teaches cell labels "in the file"
  (§DESCRIPTION, verbatim); the round-30 correction record at the
  `corpus/SOURCES.md` tail records the manual's actual wording "in the given
  file". KQ45's S174 sentence is consistent with both committed bytes.
- S193 fact: `corpus/SOURCES.md:205` quote cell reads `A path is registered
  iff it occurs in a cell of a row of such a table.` (single backticks);
  `git show c4c46ad5:tools/gate-registry-check.py` lines 15–16 read
  ``registered`` (double backticks). The markup drop is real; I re-derived it.
- S192 fact: `corpus/SOURCES.md:204`. The fetch-absence claim (client-rendered
  body) was NOT re-verified by this seat — no fetch run here (RevDrift192's
  scope; also no URL was fetched twice).
- The parenthetical "(CORPUS.md rule 2)" resolves: fleet-root
  `/home/vgpnk/Projects/shokunin/CORPUS.md:116–118` rule 2 ("Append-only … A
  correction is a new row whose `teaches` opens `supersedes S0NN —`"). No
  `corpus/CORPUS.md` exists in the lane; the fleet-root pointer matches prior
  lane usage (`corpus/knowledge/error-is-not-a-verdict.md:164`,
  `corpus/lessons/round-17.md:85`, QUALITY.md:117 "SOURCES-CONTRACT-v1 rule 2").
- Proposal source: `considerthese/2026-10-24.md:29` proposal 2 names S174
  (verbatim label dropping a word), S192 (two lines off) and S193 (line 22 for
  line 15). KQ45's lesson instances are a subset/adaptation and are accurate
  against committed bytes where I checked.
- Incidental cross-check (row bytes are RevS328/RevS329's scope): the S328 and
  S329 quote cells match the lesson Gate quotes word-for-word.

## Answers

### 1. Does any earlier criterion already cover checking a new SOURCES row's quote at its cited anchor?

No. Nothing in KQ1–KQ44 requires that a new SOURCES row's located quote be
checked against the source's own bytes at the cited anchor in the round that
writes the row. KQ45 is new coverage, not a restatement.

### 2. The two nearest earlier criteria, and why neither covers it

- **KQ22** (QUALITY.md:123) — nearest by subject: it is the SOURCES.md
  row-integrity criterion (registry cells other than `status`/`recheck`/
  `used-by` byte-identical from a row's first commit; corrected anchor takes a
  new row; `tools/sources-append-only.py` over every consecutive commit pair).
  Why not: it is purely temporal. It verifies a row does not change after its
  first commit; it never compares the row to the source's bytes. A row landed
  with a dropped word or at the wrong line is byte-stable and passes every
  append-only run forever. Its own reject cell says a census exit 0 (shape,
  enums, used-by) is not evidence — the criterion is source-blind by design.
- **KQ31** (QUALITY.md:164) — next nearest: it governs the correction
  mechanism for immutable SOURCES scope/anchor/teaches (a newly opened row
  whose teaches starts `supersedes S0NN —`; old row intact). Why not: it is
  remedy-only. It presupposes some other check has already detected the
  defect; it imposes no landing-time verification, no byte-exact/verbatim
  test, and no unreachable-vs-drift classification. KQ45's remedy actually
  reuses this mechanism ("appended superseding row (CORPUS.md rule 2)") and
  adds exactly the detection duty KQ31 lacks.

Tertiary neighbors, also not covering it: KQ6 (QUALITY.md:28) grades the
citing entry's citation hygiene (engine, revision, section, tier-fitting row;
"re-derivation at its live line" concerns re-deriving the fact, not checking
the row's quote cell), and KQ13 (QUALITY.md:40) requires entry claims to be
supported by the cited source's actual section — semantic support of entry
claims, with no byte-check of the row's quote and no landing-round duty. KQ16
(QUALITY.md:61) compares a frozen snapshot copy against git history via a
manifest — a different object (snapshot, not registry row) and comparison.

### 3. Does the motivating lesson name a measured fact with a file path?

No — not strictly. The KQ45 lesson cell (QUALITY.md:322) names three measured
facts (S174 dropped "given", S193 dropped markup, S192 fetch-absent) only by
registry id, plus one bare commit hash (c4c46ad5, no path), one external
manual, and the cited URL. The only repo file path in the cell,
`considerthese/2026-10-24.md`, anchors the proposal, not a measured fact.
Mitigation: every fact I could re-derive is true from committed bytes
(S174: SOURCES.md:186 + the round-30 record; S193: SOURCES.md:205 vs the
docstring at c4c46ad5, re-derived by me). But the cell sits below the file's
own sibling convention: KQ44's lesson names `corpus/lessons/…` paths for its
facts, KQ39/KQ43 cite file:line. A reader must resolve the S-ids into
corpus/SOURCES.md (rows at lines 186, 204, 205) and know that S193's source
path is `tools/gate-registry-check.py` — a path the cell never states — to
re-derive them.

## Findings by severity

- **High:** none.
- **Medium:** none.
- **Low — L1 (pointer hygiene):** KQ45's motivating-lesson cell attaches no
  file path or line locator to any of its three measured facts; only ids and a
  bare commit. Facts verified true where checkable, so this is a locator gap,
  not a false claim. Recommendation (I cannot edit QUALITY.md): a follow-up
  correction row or the integrating commit could add
  `corpus/SOURCES.md:186/204/205` and
  `tools/gate-registry-check.py:15–16 @ c4c46ad5` to the cell.
- **Informational:** (I1) "(CORPUS.md rule 2)" resolves only at the fleet root,
  consistent with all prior lane usage; not a dangling reference. (I2) S192's
  anchor cell carries no unverifiable-by-fetch marker — consistent, since KQ45
  governs new rows in their writing round and states no retroactive duty.
  (I3) Proposal 2 says "each day"; KQ45 strengthens to "in the round that
  writes the row" — an adaptation, allowed (proposal text is data).
  (I4) Unlike KQ22, KQ45 names no counter or command; enforcement is a prose
  obligation. Not a defect of these bytes, but a landing-time check tool is
  the obvious future companion.

## Residual risk and verification gaps

- S192 fetch-absence not re-verified here (RevDrift192 dispatched; I ran no
  fetch). S174's live manual not re-fetched (external; the committed round-30
  record is the lane's evidence; RevDrift174 scope).
- The "no earlier criterion covers it" conclusion rests on a full read of
  QUALITY.md plus a literal `quote|verbatim|anchor` sweep (hits listed above);
  the sweep alone would not be semantic proof, but the full read is.
- "Two nearest" is a proximity judgment over subject matter; KQ22 and KQ31 are
  the only earlier rows scoped to SOURCES.md rows themselves.
