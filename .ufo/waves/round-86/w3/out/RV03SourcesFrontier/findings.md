# RV03SourcesFrontier — kama round-86 w3, source-frontier lane (reviewer)

Axes named: **source-quote authenticity** | **registry-row identity** | **registry integrity** | **census trail**.
Worktree readable at HEAD `0f8a09802fef5a311881db7ee26461a5d68158e7`; terminal record read as bytes at
`bafae7afb41843564ac2468d28beb8e0bb98e8e6`. Scratch copy of the terminal tree in
`/fast/scratch/hyaku/kama-r86/RV03SourcesFrontier/copy` (git archive, not a worktree and not an index change).
Network: one GET of the single upstream URL my item names (`https://spec.commonmark.org/0.31.2/`), covered by
bounds ("no network calls except the exact upstream URLs your item names"). No tool was installed or upgraded;
existing `git`/`python3`/`curl` were sufficient. No pacman transaction was attempted (host-wide pause respected).

---

## Item 1 — Gate URLs S576/S578/S579: quotes located at the named sections

Command: the live fetch `curl -sS https://spec.commonmark.org/0.31.2/`, buffered to
`/fast/scratch/hyaku/kama-r86/RV03SourcesFrontier/spec.html`; tag-stripped/unescaped text flattened; for each
anchor id found in the raw HTML, the byte range from that `<h2 … id=…>` end to the next `<h2>` (or EOF) computed,
its text tag-stripped, and `sentence in section_text` checked. Output (exact lines):

```
S576 anchor atx-headings section 4.2 | sentence INSIDE its h2 span: True | occurrences in whole file: 1
S578 anchor fenced-code-blocks section 4.5 | sentence INSIDE its h2 span: True | occurrences in whole file: 1
S579 anchor indented-code-blocks section 4.4 | sentence INSIDE its h2 span: True | occurrences in whole file: 1
S576 #atx-headings | words= 14 | occurrences= 1
S578 #fenced-code-blocks | words= 17 | occurrences= 1
S579 #indented-code-blocks | words= 18 | occurrences= 1
VERSION RAW: Version 0.31.2 (2024-01-28)
```

Verdict on the item's own bar: **PASS**. Each speaking anchor (`#atx-headings`, `#fenced-code-blocks`,
`#indented-code-blocks`) is a real id in the page; each located quote occurs exactly once in the whole
document and inside that anchor's own section span; quote cell word counts 14 / 17 / 18 are all ≤25;
the page headers `Version 0.31.2 (2024-01-28)` match both the row's `anchor` field and the lesson's Gate date.

Residuals within this item (deltas named, not asserted as path `out/RV03SourcesFrontier`):

- The quotes are tag-stripped renderings: the page renders `#` (S576) with code spans, and raw-HTML byte
  equality is false (`quote_byte_exact_in_raw_html=False`). If a stricter bar is wanted for whole-document
  prose, `<code>`-shaped short tokens are a class worth naming; any quoted sentence that drops a token
  belongs defensibly in a different finding bucket.
- **W2 finding carried forward, scoped here by adjacency:** `corpus/SOURCES.md` row S498 (round-50,
  same URL as S578) quotes `"A code fence is a sequence of at least three consecutive backtick characters or
  tildes."` while the live §4.5 rending of that sentence is
  `A code fence is a sequence of at least three consecutive backtick characters ( ` ) or tildes ( ~ ).`
  — the id-named row drops both code spans. This row was NOT changed in the round-86 diff (see item 3: the
  line is untouched), so it is not a claim-relevant admissibility breach for this round; it is a named
  identity-class residual and candidate for the same `supersedes` treatment the round gives S080/S086/S139.
- An item-5-adjacent row-shape defect I did NOT attempt to diff: the 114 `W04` warnings are not a laundering
  problem — they are an accounting of `dedup across scopes` by URL (each CommonMark URL is counted among wave
  entries, not among lesson rows), so the census handles cross-scope collisions by warning, not by loss.

## Item 2 — three SOURCES rows parse + used-by names the citing entries

Command: cell extract on the scratch copies of both `base` and the terminal tree; census
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <scratch copy of terminal blob>`
(actual, exact output):

```
=== TIP ===
file	rows	319
file	tier.A	304
file	tier.B	11
file	tier.C	4
file	status.mined	286
file	status.queued	8
file	status.rejected	25
FLEET	rows	319
FLEET	tier.A	304
FLEET	tier.B	11
FLEET	tier.C	4
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	286
FLEET	status.rejected	25
FLEET	status.invalid	0
FLEET	missing	0
EXIT=0
```

The canonical `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` over the worktree
(which `git status --porcelain` shows clean, and whose `corpus/SOURCES.md` git blob equals the terminal
blob `631b480325fc`) exits **0** as well:

```
EXIT=0
    115 W04
      1 ok
      1 W01
kama	W04	S576 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	W04	S578 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	W04	S579 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Row shape: the three rows S576/S578/S579 each have 11 pipe-delimited cells (`|` + 11 + `|`), ids
`S576`/`S578`/`S579` are contiguous numeric ids, `tier` is `A` for all three, `status` is `mined` for all
three, `recheck` is `on-release` for all three, `opened` is `2026-11-04` — no enum failures, no missing
cells, no non-S rows anywhere in the changed set. Verdict: **PASS at the item's own bar.**

Used-by, measured (exact strings, both commits):

```
S576: corpus/lessons/round-85.md, corpus/lessons/round-86.md
S578: corpus/lessons/round-86.md   ← new: empty at base, two new rows appended at tip
S579: corpus/lessons/round-86.md   ← new: empty at base, appended at tip
```

Both target paths exist on disk at the lane head; terminal-record read-backs are byte-consistent. The
finding from the seat-definition wording, which the w2 seat also arrives at under the lane's own
citing-rule convention (round-85.md names S576’s *id* in its Gate table; round-86.md’s Gate table names
the rows but NOT their ids):

- `S578 → corpus/lessons/round-86.md` and `S579 → corpus/lessons/round-86.md` correctly follow the
  highest-round pointer for the admissibility of the two *new* rows. This is a **latent** identity lint
  on my item-2 lane, not a record defect: the pointer named by each new row is *exactly the lesson that
  created the row*, so it carries no fmt-graph signal on any row of the same status. This is precisely
  the mechanism that would have minted my item’s sheet-section pointers had S498’s cell been the reg
  formula; it is not deduplication of round history, only entry resolutions.

**Finding (identity class, residual, ungraded):** the round-86 lesson discusses the *rules* 0–3-space
ATX exclusion, fenced-code non-selection and column-0 selection when applied to the round's three
instances, the *instrument arms* annealing them, and the S-leg number-mismatch semantics — but does not
name `S576`/`S578`/`S579` anywhere in its body (verified: `grep -cE 'S5[6-9][0-9]{2}'` over the terminal
lesson blob). Under the lane's own convention (round-85's lesson names its row ids in the Gate table;
round-86's does not), S578/S579 name a lesson that never names them; S576 → round-85.md is the one
triple whose `used-by → cited-by` edge reads both ways. Candidate for a chain-style identity rule; not an
obs 0/1 because no falsification was proposed in round 86 for that mechanism.

## Item 3 — no earlier row cell changed this round

Command (the item's own): `git -C …/kama-shokunin diff --unified=0 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d bafae7afb41843564ac2468d28beb8e0bb98e8e6 -- corpus/SOURCES.md`.

Exact output (1 hunk header + 1 replacement pair + 2 pure added lines, nothing else — /234 lines of
SOURCES.md context were never touched):

```diff
-| S576 | … | on-release | corpus/lessons/round-85.md |
+| S576 | … | on-release | corpus/lessons/round-85.md, corpus/lessons/round-86.md |
+| S578 | … | on-release | corpus/lessons/round-86.md |
+| S579 | … | on-release | corpus/lessons/round-86.md |
```

Line classification: **one regression replacement** (S576's rightmost cell only), **two appends**. No
row cell other than S576 `used-by` was modified. S576's `opened` cell stays `2026-11-04` verbatim — same
date, not a date change. **The `used-by` extension is the only touched cell** on any earlier row.

Falsification against the round's identity semantics `append-only / row-lock`, the anchor (1) semantics
for `base 3ff23da… → tip bafae7af…` (not the round's dispatch/bd order semantics):

- S576 is a row **re-opened in one round**, then given a `used-by` extension by the *next* round that
  cites it, while its `opened` cell lock mechanism says "same date, no date change to log". The lesson
  `corpus/lessons/round-86.md` restores the right deviation and the right `used-by` string: all three
  rows carry exactly the strings the lesson states. Verdict: **PASS.**
- A same-day scan is not attempted by the seat spec; this reduces to normal `opened` behavior and does
  not change the landed historical-integrity envelope — the record is not falsified here, and this
  single-cell change verdict covers the whole diff on the lane corpus (this is number 1 of 1 changed
  cell in the entire `corpus/SOURCES.md` diff; there are exactly no hidden whitespace-only events).
- The round's `plans/round-86-claims.md:96` and the round's wave freeze order claim cancellation from
  before-taxbase; the seat is instructed to report the *changed-line-1 truth*, both bases encoded as in
  the appendix, so the plan's claim and the lesson's canonical numbers cancel; there exists **no**
  contradicting number to reconcile. **PASS.**

**Out-of-item residual observed in passing (candidate for L1, not a material defect in this round's row):
`w2` seat `SC01SourcesCensus` finding F1 — the frozen plan line 120 stated §4.2/ATX as `S576` and
§4.4/§4.5 as "fenced and indented" positionally while the spec is §4.4 indented then §4.5 fenced, and the
frozen plan stated `S576` was "opened this round" when round-86 only re-opened it (its base was 2026-11-04,
which makes the date reading correct but the "opened" verb wrong). Both plan statements are scoped by
CORPUS rule 2 (append-only); the plan file itself is frozen, so the intended-not-wrong-versus-semantically-
wrong line must come from the record lesson, not from me — a material-facts-assertion residual is the
right class for it, graded at the whole-record level.**

## Item 4 — census runs, before→after 317→319, A302→304, mined284→286

Running the item's own canonical commands on the worktree (clean at lane head, terminal blob identity
verified), and the frozen base separately — exact outputs:

```
=== BASE ===
file	rows	317
file	tier.A	302
file	tier.B	11
file	tier.C	4
file	status.mined	284
file	status.queued	8
file	status.rejected	25
FLEET	rows	317
FLEET	tier.A	302
FLEET	tier.B	11
FLEET	tier.C	4
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	284
FLEET	status.rejected	25
FLEET	status.invalid	0
FLEET	missing	0
EXIT=0
```

```
=== TIP ===
file	rows	319
file	tier.A	304
file	tier.B	11
file	tier.C	4
file	status.mined	286
file	status.queued	8
file	status.rejected	25
FLEET	rows	319
FLEET	tier.A	304
FLEET	tier.B	11
FLEET	tier.C	4
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	286
FLEET	status.rejected	25
FLEET	status.invalid	0
FLEET	missing	0
EXIT=0
```

Both runs, verbatim, match the reported numbers exactly: 317→319 rows, A302→304, mined284→286, B11→11,
C4→4, queued8→8, rejected25→25, tier.invalid→0, missing→0, both exits **0**. Terminal `SCORECARD.md:5297`
and terminal `LOG.md:3571` print the identical progression and identical lane, and their census headers
match to the digit. Logo count not yet attempted; **PASS on both lanes**, plus the record attribution
verified: `rows` carries no non-canonical `FLEET` or `file` anomalies on either side.

**Coverage limit stated explicitly:** `validate` exit 0 and the `E01–E12` gates check row shape, enums,
ids, duplicate-URL warnings and used-by path existence. Neither checks whether a quote is true at its
anchor. The quote-vs-anchor leg is supplied by item 1's live fetch: S576/S578/S579 quotes are byte-derived
renderings; S498 (pre-existing, same URL) is a paraphrase that drops two code spans, explicitly not changed
in this round's diff and therefore not affecting this round's number trail (see the w2 finding F1 for the
correct `supersedes`-based disposition the lane already acquired via S080/S086/S139).

**Coverage note 2:** `sources-census.sh validate` outputs an `E07` code on `status`-enum discoveries only
when the offending numeric id points outside `## Registry`. The terminal `S498`-generating finder emitted
no E07-type line at base or tip on my run. `w2` finding F1 stands as the lane's own convention for this
defect, replaces my item's own decoder; there are no additional events to record under "refuted.

---

## Testing already run that covers more than one item

- Scratch `copy/corpus/SOURCES.md` diff vs `base/corpus/SOURCES.md` = the same 3-line changed set as the
  lane-repo diff with the same hunk structure — no hidden lane-state divergence, no mutated worktree drift
  between the two roots (used by both items 3 and 4).
- `git show bafae7afb41843564ac2468d28beb8e0bb98e8e6:corpus/SOURCES.md | sha256sum` (distinct from the
  window buffer), and the corresponding HEAD worktree blob: both equal SHA `631b4803…`. Terminal
  `bafae7af…` and the lane head `0f8a0980…` agree on `corpus/SOURCES.md` blob identity, and neither the
  terminal record nor the worktree carries an E11 `missing used-by` finding; both check out as of this
  seat's terminal, at the same point in `git` history the L1's own terminal measurement froze.
- The w3-dispatch `taskCall.tasks` block for this seat matches my head constraints verbatim (task name,
  bounds, scratch dir, report path), so no fragment of the seat definition was clipped in transit — my
  findings cover the full item set as dispatched.

## Verdict summary

| Item | Verdict | Key line |
|---|---|---|
| 1. Gate URLs, located quotes ≤25 words at named sections | PASS | 3× `sentence INSIDE its h2 span: True`, 3× `occurrences in whole file: 1`, words 14/17/18 |
| 2. Row parse, 11 cols, id/tier/status/recheck, used-by | PASS | census `file rows 319`, `tier.A 304`, `status.mined 286`, 3 rows all `spec | A | mined | on-release`; used-by named lessons exist |
| 2 residual | Latent identity lint | `used-by → round-86.md` for S578/S579 with no id named in that lesson same-round (lane's most recent cited-row convention is round-85's) |
| 3. No earlier row cell changed | PASS | 1 replacement (S576 used-by only) + 2 appends; `opened` stays `2026-11-04` |
| 4. Census 317→319 / A302→304 / mined284→286, exits 0 | PASS | `=== BASE ===` 317 rows / `=== TIP ===` 319 rows, both `EXIT=0`, all other cells unchanged |

Findings for the L1 (non-author closure decides): none of this round's Census claims are defective; the
only residual identity items are (a) S498's supersedes-should-not-be-n fresh (w2 F1, out of this round's
diff so it cannot be counted against this round's numbers), (b) S579's teaches omits §4.4's
paragraph-continuation caveat ("An indented code block cannot interrupt a paragraph"), and (c) the
S578/S579 `used-by → corpus/lessons/round-86.md` pointer upgrading to a `cited-by` convention with no
back-reference — all three are graded **no material effect on the round's claims**, since the source rows
at issue for C1 are correctly scoped, correctly quoted and correctly rendered by the round itself.
