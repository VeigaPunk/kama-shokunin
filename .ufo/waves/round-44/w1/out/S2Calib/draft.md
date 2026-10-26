# C2 calibration — round 44 draft (seat S2Calib)

Draft only. It drafts the SCORECARD section and one QUALITY.md criterion; it does not
write them, does not decide the final ledger, and carries no score. Every line number
below is 1-based and verified at the frozen revisions (`fleet b0fd7b7f`, `lane 9d9cc93`).

Figures quoted outside the paste-ready blocks come from the frozen counter run over the
round-44 draft with the two round-25 line corrections in
`w1/out/S2Calib/fragment.tsv`:

```
rows=204 valid=204 missing=0 bad=0 agree=63 overclaim=2 underclaim=7 other=15 absent=15 table_missing=24 table_extra=0 summary=0 axes=0 met=False
```

(`table_missing=24`, `summary=0`, `axes=0` are the expected reads before the SCORECARD
section exists; `valid=204` with `bad=0` is the part that matters here.)

---

## 1. What the ledger is comparing

204 rows: rounds 10–43 × three LEARNING.md trends × two sides. The self side is the
`.ufo/reports/round-<N>/kama.md` blob at `b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025`; the
outside side is `corpus/lessons/round-<N>-verifier-spotcheck.md` at
`9d9cc93ec50783cd114829a91757b90d57c78dc6`. A row's verdict is whatever the cited line
carries for its trend, so the ledger's figures are a property of *the lines cited* as much
as of the verdicts. That is not a defect to argue away: it is the first thing the round
must say about its own numbers.

## 2. The pattern: every report is filed before the closure that judges it

For every round that has a spot-check file at base (30 of 34), the self report's first-add
commit precedes the closure file's first-add commit:

```
git -C /home/vgpnk/Projects/shokunin        log --diff-filter=A --format=%ci -- .ufo/reports/round-<N>/kama.md b0fd7b7f
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --diff-filter=A --format=%ci -- corpus/lessons/round-<N>-verifier-spotcheck.md 9d9cc93
```

Lag: min 0.0 min (round 10, both landed in one wave's second), median 9.7 min, max 257.6
min (round 36); no round is negative. Full table: `w1/out/S2Calib/timing.tsv`.

So the ordering is structural, not a per-round choice. The author writes the trend
verdicts first; the non-author who grades them writes second.

## 3. Why "unchanged" was the only honest discernment verdict, and why the closures agree

LEARNING.md's discernment row makes `improved` wait on an act:

> `improved` when — the spot-check agrees with the gate on admits *and* rejects, or a
> disagreement becomes a lesson that adds a grounded `QUALITY.md` criterion
> — `LEARNING.md:35`

and its §Discernment is explicit about who may not supply it:

> Self-assessed taste is not discernment… **A subagent the lane dispatched is still the
> lane.** — `LEARNING.md:40-47`

At report time the spot-check does not exist (section 2), and the lane's own seats are
"still the lane". A report that writes `improved` for discernment at that moment is
attesting its own taste — exactly what the § forbids — or guessing the closure. Writing
`unchanged` and naming the owed act is the only verdict that is true when written.

The closures say so themselves, in their own words:

| round | closure line | text |
|---|---|---|
| 12 | `round-12-verifier-spotcheck.md:123` | "This supersedes the author's honest pending-sample `unchanged` for closure only, without modifying filed text." |
| 14 | `round-14-verifier-spotcheck.md:136` | "Unlike the author's pending-outside-review `unchanged` baseline…" |
| 15 | `round-15-verifier-spotcheck.md:159` | "The author's `unchanged` correctly described pending outside review." |
| 16 | `round-16-verifier-spotcheck.md:174` | same sentence |
| 17 | `round-17-verifier-spotcheck.md:217` | "this closure's outside judgment; the lane wrote `unchanged`" |
| 19 | `round-19-verifier-spotcheck.md:170-172` | "**discernment: improved.** … The lane's \"unchanged\" was correct at write time, pending this act." |
| 39 | `round-39-verifier-spotcheck.md:76` | "previously `unchanged` only because no outside check existed; LEARNING.md grades agreement on admits and rejects as improved" |

And every self row the ledger records as an underclaim states the owed act in its own
bytes, so the pair is auditable from the filed text alone:

| round | self line | the owed act, as filed |
|---|---|---|
| 10 | `round-10/kama.md:93` | "**Discernment: unchanged pending outside check.** … No non-author admit/reject spot-check has happened yet." |
| 11 | `:250` | "no fresh non-author sample yet… Outside closure must sample ≥1 admit and ≥1 reject before admission." |
| 19 | `:115` | "round 19's outside admit/reject sample is still owed" |
| 34 | `:204` | "No independent non-author admit/reject sample exists for round 34… await the outside closure." |
| 35 | `:63` | "No non-author reviewer judged this round's gate." |
| 40 | `:294` | "No independent non-author admit/reject spot-check of the round's Gate decisions was received." |
| 43 | `:102` | "no outside discernment check of this round exists yet" |

**Consequence for the scorecard.** The counter has no class for "honest underclaim": a
filed `unchanged` against a closure `improved` is `underclaim` by its order rule. The
scorecard must therefore name these rows as *ordering pairs* — the filed verdict was
true when filed, and the closure later supplied the act — or the figures read as seven or
eight calibration failures that never happened. Not counting them would be worse: the
ledger exists to show the asymmetry, and the fact that the lane never once wrote
`improved` before its closure is the calibration result.

## 4. The overclaims: two, both expansion, both named by the closure

After the round-25 line corrections (section 6) the ledger holds two overclaims, and both
are expansion. The mechanism is not timing; it is a bar read more loosely by the author
than by the closure:

- **Round 19 — `self improved` vs `outside unchanged`.** Self (`:108`): "expansion —
  improved (narrow). One new curated source row and its Gate were opened and verified this
  round; census 56 → 57". Closure (`:162`): "**expansion: unchanged.** There is one new
  source row (S057) but no new admitted knowledge entry and no capability row, and
  LEARNING's `improved` row needs one of those. This differs from the lane's \"improved
  (narrow)\"; I record the disagreement rather than fault the lane." LEARNING.md's
  expansion row admits `improved` on "net new admitted entries on uncovered ground"; a
  source row is the input to an entry, not an entry.
- **Round 28 — `self improved` vs `outside unprovable-but-better`.** Self (`:203`):
  "expansion: improved" on a capability plus 34 opened tier-A sources. Closure (`:198`,
  `:202-203`): "**expansion: unprovable-but-better.** … The ground did not arrive through
  an admitted claim, so this closure does not grade it `improved`." One order step, same
  mechanism: wave evidence credited as if it were a landed artifact.

Both closures record the disagreement explicitly, so neither is a discovered dishonesty;
both are the same repeatable error — expansion credited before admission. A future report
that cites the admitted entry or capability row (not the source row, not the wave) cannot
make it.

## 5. The `other` class: reading one line, not two verdicts

Fifteen keys are classed `other`, always because one cited line gives the trend two
verdict words. Read for the sentence's *first* verdict and its *subject*, they split:

| kind | rounds (line) | what the second word is |
|---|---|---|
| closure credits the round and quotes the filed verdict | 12 (123), 14 (136), 15 (159), 16 (174), 17 (217), 29 (69), 39 (76) | the author's `unchanged`, preserved "for closure only" |
| self quotes the prior round's verdict | 18 self (130) | "Round 17's outside spot-check (`improved`) still…" |
| self reserves the word conditionally | 27 self (121) | "It stays `unprovable` until a named non-author reviewer rules." |
| negation of another axis | 33 self (222) | "No axis was harmed." |
| word about a file, not the trend | 34 outside (87) | "`corpus/README.md` is unchanged" |
| word about a blob, not the trend | 35 self (62) and outside (113), 37 self (46) | "the r34 report blob is unchanged", "both pinned r36 blobs unchanged" |
| self's own phrase | 24 self (247) | "records the full negative/unprovable target" |
| outside negates the grade it declines | 43 outside (96) | "Not `improved` by the trend's definition" |

On a first-word reading, rounds 12, 14, 15, 16, 17, 18, 27, 29 and 39 are underclaims of
the same ordering kind as section 3 (and 29 is the one *expansion* underclaim: the lane
applied a serving-surface bar stricter than LEARNING.md's entry bar), and rounds 24, 33,
34-expansion, 35-quality, 37-quality and 43-quality **agree**. The ledger keeps `mixed`
because the frozen reader classifies by the cited line and offers no other line for those
keys (`w1/out/S2Calib/line-map.tsv`, columns `single_word_lines` / `multi_word_lines`):
for every one of these keys the file has exactly one line carrying the trend's verdict,
and that line carries two words. The scorecard's job is to say that, per row, in the
evidence column — otherwise `other=15` reads as fifteen disagreements it is not.

## 6. Two draft rows cite a quotation, not the verdict sentence

Both corrected rows are in the same file, and the file's own verdict section is
unambiguous (`round-25-verifier-spotcheck.md:180-194`):

| key | draft cites | verdict sentence | why the draft's line is wrong |
|---|---|---|---|
| 25 quality outside | `:193` "entry's fact false or stale, so quality is not harmed." | `:187` `**Quality: unchanged.**` | the draft's word is **negated**; the closure's graded word is `unchanged` |
| 25 discernment outside | `:200` "The SCORECARD trend line (discernment improved, quality unchanged-to-improved) contradicts the report (both unchanged)." | `:194` `**Discernment: unchanged.**` | the draft's line **quotes SCORECARD's** trend line in order to contradict it |

Effect, computed by the frozen counter (fragment receipt
`w1/out/S2Calib/check-fragment.out`): `agree 61→63, overclaim 3→2, underclaim 8→7`, table
rows 26→24, `n` unchanged at 72. This is also where the brief's "7 of the 8" reproduces:
as the draft stands, all eight underclaims are discernment `unchanged`→`improved`; after
these two corrections there are seven, and all seven are discernment.

## 7. The absent class is a surface gap, not an omission

15 keys have an absent side.

- **12 outside rows: rounds 20–23 have no `round-N-verifier-spotcheck.md` at base**
  (`git -C kama-shokunin cat-file -e 9d9cc93:corpus/lessons/round-2{0,1,2,3}-verifier-spotcheck.md`
  → `does not exist`). Their closures are fleet `MANIFEST.json` entries for lane kama
  (rounds 20, 21, 22, 23; dated 2026-10-21) that carry `admitted` and **no `trends`
  field** — so no outside trend verdict exists anywhere to ledger. The lane's own
  `corpus/lessons/round-22.md:95-102` says the same thing from inside: "`MANIFEST.json`
  rounds[406] is the non-author R21 closure; no separate `round-21-verifier-spotcheck.md`
  file was present." The ledger cannot see an outside verdict that was never written.
- **3 self rows: round 38 filed no trend verdict.** Its `# Trends` section
  (`round-38/kama.md:38-43`) lists *axis* names — calibration, coverage, operability,
  freshness, depth, adjacency — in the slot the LEARNING trends occupy in every other
  round. Those are axis verdicts, not trend verdicts, and `read_line` finds no trend word
  in the file.

Both gaps are honest abstentions and must be labelled as such in the summary
(`absent=<k>`), never folded into agreement.

---

(a) SCORECARD section — paste-ready, figures with placeholders
==============================================================

Rule for the L1: the table's row set must equal the final ledger's mismatch set exactly
(`overclaim ∪ underclaim ∪ other`), with no row for an `absent` key and no row for an
agreeing key; the summary line must contain the counter's exact shape with `n = a + o + u`.
The rows below are the 24 keys of the corrected reading in section 6 — regenerate rather
than trust them if the final ledger cites different lines.

<<<BEGIN SCORECARD BLOCK>>>

### Round-44 calibration ledger

For rounds 10–43, each LEARNING.md trend verdict the lane filed is set beside the outside
closure's verdict, one row per (round, trend, side): 204 rows in
`registry/verdict-ledger.tsv`, scored by `tools/round44-verdict-ledger-audit.py`. Self
rows read `.ufo/reports/round-<N>/kama.md` at
`b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025` (fleet); outside rows read
`corpus/lessons/round-<N>-verifier-spotcheck.md` at
`9d9cc93ec50783cd114829a91757b90d57c78dc6` (lane). Each row cites the line that carries
its verdict; `mixed` means the cited line gives the trend two distinct verdict words. The
comparison order is harmed < unchanged < unprovable < unprovable-but-better < improved.

`agreement=<a>/<n> overclaim=<o> underclaim=<u> other=<x> absent=<k>`

| round | trend | self | outside | class | evidence |
|---|---|---|---|---|---|
| 10 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-10/kama.md:93`; `lane:corpus/lessons/round-10-verifier-spotcheck.md:17` |
| 11 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-11/kama.md:250`; `lane:corpus/lessons/round-11-verifier-spotcheck.md:198` |
| 12 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-12/kama.md:108`; `lane:corpus/lessons/round-12-verifier-spotcheck.md:123` — closure credits improved, quotes the filed `unchanged` |
| 14 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-14/kama.md:91`; `lane:corpus/lessons/round-14-verifier-spotcheck.md:136` — same |
| 15 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-15/kama.md:114`; `lane:corpus/lessons/round-15-verifier-spotcheck.md:159` — same |
| 16 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-16/kama.md:156`; `lane:corpus/lessons/round-16-verifier-spotcheck.md:174` — same |
| 17 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-17/kama.md:101`; `lane:corpus/lessons/round-17-verifier-spotcheck.md:217` — same |
| 18 | discernment | mixed | improved | other | `fleet:.ufo/reports/round-18/kama.md:130`; `lane:corpus/lessons/round-18-verifier-spotcheck.md:126` — self line quotes round 17's `improved` |
| 19 | expansion | improved | unchanged | overclaim | `fleet:.ufo/reports/round-19/kama.md:108`; `lane:corpus/lessons/round-19-verifier-spotcheck.md:162` — source row credited as an admitted entry |
| 19 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-19/kama.md:115`; `lane:corpus/lessons/round-19-verifier-spotcheck.md:170` |
| 24 | discernment | mixed | unchanged | other | `fleet:.ufo/reports/round-24/kama.md:247`; `lane:corpus/lessons/round-24-verifier-spotcheck.md:145` — second word is "negative/unprovable target" |
| 27 | discernment | mixed | improved | other | `fleet:.ufo/reports/round-27/kama.md:121`; `lane:corpus/lessons/round-27-verifier-spotcheck.md:219` — self reserves `unprovable` until a named reviewer |
| 28 | expansion | improved | unprovable-but-better | overclaim | `fleet:.ufo/reports/round-28/kama.md:203`; `lane:corpus/lessons/round-28-verifier-spotcheck.md:198` — wave evidence credited before admission |
| 29 | expansion | unchanged | mixed | other | `fleet:.ufo/reports/round-29/kama.md:136`; `lane:corpus/lessons/round-29-verifier-spotcheck.md:69` — closure credits improved, quotes the filed `unchanged` |
| 33 | discernment | mixed | improved | other | `fleet:.ufo/reports/round-33/kama.md:222`; `lane:corpus/lessons/round-33-verifier-spotcheck.md:64` — "No axis was harmed" is another axis |
| 34 | expansion | improved | mixed | other | `fleet:.ufo/reports/round-34/kama.md:192`; `lane:corpus/lessons/round-34-verifier-spotcheck.md:87` — "README is unchanged" is a file |
| 34 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-34/kama.md:204`; `lane:corpus/lessons/round-34-verifier-spotcheck.md:89` |
| 35 | quality | mixed | mixed | other | `fleet:.ufo/reports/round-35/kama.md:62`; `lane:corpus/lessons/round-35-verifier-spotcheck.md:113` — "the r34 report blob is unchanged" is a blob |
| 35 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-35/kama.md:63`; `lane:corpus/lessons/round-35-verifier-spotcheck.md:114` |
| 37 | quality | mixed | improved | other | `fleet:.ufo/reports/round-37/kama.md:46`; `lane:corpus/lessons/round-37-verifier-spotcheck.md:179` — "pinned r36 blobs unchanged" is a blob |
| 39 | discernment | unchanged | mixed | other | `fleet:.ufo/reports/round-39/kama.md:47`; `lane:corpus/lessons/round-39-verifier-spotcheck.md:76` — closure credits improved, quotes the filed `unchanged` |
| 40 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-40/kama.md:294`; `lane:corpus/lessons/round-40-verifier-spotcheck.md:93` |
| 43 | quality | unprovable-but-better | mixed | other | `fleet:.ufo/reports/round-43/kama.md:101`; `lane:corpus/lessons/round-43-verifier-spotcheck.md:96` — closure writes "Not `improved` by the trend's definition" |
| 43 | discernment | unchanged | improved | underclaim | `fleet:.ufo/reports/round-43/kama.md:102`; `lane:corpus/lessons/round-43-verifier-spotcheck.md:97` |

**Every underclaim is an ordering pair.** The report is filed before the closure that
judges it: in all 30 rounds with a spot-check file the report's first-add commit precedes
the closure file's first-add commit (`git log --diff-filter=A`, median lag 9.7 minutes;
`registry/verdict-ledger.tsv` records the two times in each underclaim row's note).
LEARNING.md grades discernment `improved` on an act — "the spot-check agrees with the gate
on admits and rejects" (`LEARNING.md:35`) — performed by a non-author after the report
lands, and its §Discernment says "A subagent the lane dispatched is still the lane"
(`LEARNING.md:40-47`). A report that wrote `improved` for discernment at that moment
would be attesting its own taste; each of these self rows instead writes `unchanged` and
names the owed act (`round-10/kama.md:93`, `:250`, `:115`, `:204`, `:63`, `:294`, `:102`),
and the closures say so in their own words: "the author's honest pending-sample
`unchanged` for closure only" (`round-12-verifier-spotcheck.md:123`), "The lane's
\"unchanged\" was correct at write time, pending this act"
(`round-19-verifier-spotcheck.md:172`). The underclaim count is the price of an honest
self-assessment order, not an error in it; the lane never once filed `improved` on
discernment before its closure existed.

**Both overclaims are expansion, and both closures name the bar.** Round 19 credited one
new source row as expansion; the closure held `unchanged` because LEARNING.md's row needs
an admitted entry or a capability (`round-19-verifier-spotcheck.md:162`). Round 28
credited a capability and 34 opened sources before any admitted claim; the closure graded
`unprovable-but-better` for the same reason (`round-28-verifier-spotcheck.md:198`,
`:202-203`). Same repeatable error — expansion credited before admission.

**`other` rows are two-voiced lines, not two verdicts.** On a first-word, first-subject
reading, rounds 12, 14, 15, 16, 17, 18, 27, 29 and 39 are underclaims of the ordering kind
above (round 29 the one expansion case: the lane applied a serving-surface bar stricter
than LEARNING.md's entry bar), and rounds 24, 33, 34-expansion, 35-quality, 37-quality and
43-quality agree. The ledger keeps `mixed` because the frozen reader classifies by the
cited line, and for each of these keys the file has exactly one line carrying the trend's
verdict, which carries two words (`w1/out/S2Calib/line-map.tsv`). The evidence column says
what each second word does; none of them is a disagreement with the closure.

**`absent` is a surface gap, not a pass.** Rounds 20–23 have no
`corpus/lessons/round-N-verifier-spotcheck.md` at the measured lane base: their closures
are fleet `MANIFEST.json` entries for lane kama that record `admitted` and no trend
verdict, so no outside trend verdict was ever written (the lane says the same at
`corpus/lessons/round-22.md:95-102`). Round 38's report has no trend verdict at all: its
`# Trends` section lists axis names (calibration, coverage, operability, freshness, depth,
adjacency), so the round filed a verdict for no LEARNING trend. Both are counted in
`absent=`, never in `agreement=`.

**What this does not show.** Agreement between a filed verdict and a later closure, not
the quality of either: a closure can be generous, and round 35's outside `quality`
sentence is the author's sentence verbatim plus one appended line
(`round-35-verifier-spotcheck.md:113` is a prefix-extension of `round-35/kama.md:62`), so
that row is not independent evidence. The reader is also negation-blind and
subject-blind: "quality is not harmed" reads as `harmed` (round 25, line 193), "No axis
was harmed" attaches `harmed` to discernment (round 33, line 222), and "the r34 report
blob is unchanged" attaches `unchanged` to quality (round 35, lines 62, 113). The ledger
cites the verdict sentence, not the nearest line: round 25's two rows cite lines 187 and
194, and citing the draft's lines 193 and 200 instead would read
`agreement=61/72 overclaim=3 underclaim=8` — a three-row swing produced by line choice
alone.

<<<END SCORECARD BLOCK>>>

Footnote for the L1 (not part of the block): the `## Axes` calibration row must name
`registry/verdict-ledger.tsv`, or the counter's `axes` leg reads 0. The heading is
`### Round-44 calibration ledger` exactly; the counter's section scan ends at the next
line beginning with `#`, so keep the table and the figures line in one section.

---

(b) QUALITY.md criterion — KQ58, paste-ready
============================================

Next free id after KQ57. Append after the round-43 section (file ends at the KQ57 row).

<<<BEGIN QUALITY BLOCK>>>

## Criterion added — round 44: a verdict that rests on a later act is filed `unchanged` with the act named, and the ledger cites the verdict sentence

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ58 | A trend verdict in a round report is written only against an act that exists when the report is filed, and the report says which act that is. For discernment, `improved` waits on the outside spot-check agreeing with the gate (`LEARNING.md:35`, `:40-47`), so the report writes `unchanged` and names the owed act and the file that will carry it (`corpus/lessons/round-<N>-verifier-spotcheck.md`); for expansion, the bar is a landed artifact, so the report cites the admitted entry or capability row, never a source row or wave evidence. When the closure lands, the pair is ledgered with its ordering evidence — `git -C <fleet> log --diff-filter=A --format=%ci -- .ufo/reports/round-<N>/kama.md <fleet-rev>` and the same command in the lane for the closure file — and a filed `unchanged` against a closure `improved` is recorded as an ordering pair when the filed bytes name the owed act, and as a calibration defect when they do not. Every ledger row cites the line that is the verdict sentence and reproduces its verdict; the round's SCORECARD reports the agreement counts and names every disagreement and every ordering pair. | A report writes `improved` on a judgement its own round cannot supply — self-attestation, which `LEARNING.md` §Discernment forbids ("A subagent the lane dispatched is still the lane") — or credits expansion before an admitted artifact exists: round 19 filed `expansion: improved` on one source row where the closure held `unchanged` for want of an admitted entry (`round-19-verifier-spotcheck.md:162`), and round 28 filed `improved` on a capability and 34 opened sources before any admitted claim (`round-28-verifier-spotcheck.md:198`). A row whose cited line quotes another round's verdict, negates the word, or speaks about another object is not that round's verdict, and an automatic last-hit cannot tell: round 25's outside `quality` is line 187 `**Quality: unchanged.**`, not line 193's "…so quality is not harmed", and its outside `discernment` is line 194, not line 200, which quotes the SCORECARD trend line in order to contradict it — citing 193 and 200 moves the figures from `agreement=63/72 overclaim=2 underclaim=7` to `61/72, 3, 8` on the same 204 rows. Where the file offers no single-verdict line, the row is `mixed` and the SCORECARD must say what the second word does (round 33's "No axis was harmed", round 35's "the r34 report blob is unchanged"), not count it as a disagreement. | `corpus/lessons/round-44.md` §Calibration; `registry/verdict-ledger.tsv`; `tools/round44-verdict-ledger-audit.py`; `.ufo/waves/round-44/w1/out/S2Calib/draft.md` §2–§6 |

<<<END QUALITY BLOCK>>>

Dependency to flag at integration: KQ58 cites `corpus/lessons/round-44.md` §Calibration,
which does not exist yet. The round-44 lesson must carry the ordering evidence (the
first-add times), the two expansion overclaims, and the round-25 line correction, or the
criterion cites an empty section — the same failure mode KQ25/KQ44 are written about.

---

## Appendix: how the draft's own figures were produced

The round-44 draft (`c2/draft-ledger.tsv`) is a valid 204-row ledger under the frozen
reader (`valid=204 bad=0`), and its comparison reads `agree 61, overclaim 3, underclaim 8,
other 15, absent 15`. The two round-25 corrections in section 6 change only the cited
lines, not the verdicts the closures reached, and move it to `63 / 2 / 7 / 15 / 15`.
Neither set of figures is a score: C2's score stays 7→7, and no closure verdict in this
ledger moves a number.
