# K2Design — C2 design attack (round 44, kama)

**Verdict: C2 is met-able, but the draft it must land is wrong on 19 of 204 rows.**
The draft's 15 `other` rows are token-attribution artifacts (quoted author verdicts and
negations), not disagreements; the r23 quality sign reversal — which the lane already
recorded — is scored `absent`; and 12 outside verdicts that exist in `MANIFEST.json` are
recorded as absent because the frozen outside path has no file. Corrected rows are all
counter-valid: `valid=204 bad=0 agree=69 overclaim=2 underclaim=16 other=0 absent=15`
(proposal + receipt under `w1/out/K2Design/`). C2 should be repaired by the L1, not
re-frozen; the predicate's outside half and its novelty sentence remain findings.

## Counterexample (strongest available)

`round-43-verifier-spotcheck.md:96` states exactly one outside verdict —
`**quality: unprovable-but-better.**` — then says "Not `improved` by the trend's
definition". The counter's `read_line` maps the trailing negated word to the same trend,
so the line yields `{unprovable-but-better, improved}`; the draft records `mixed`
(`c2/draft-ledger.tsv`, row `43 quality outside`). The lane's self verdict is the same
`unprovable-but-better` (`.ufo/reports/round-43/kama.md:101`), i.e. **agreement**, but the
draft turns it into one of 15 "disagreements" the SCORECARD must name. The same pattern
repeats wherever an outside file quotes the author: `round-12…17-verifier-spotcheck.md`
lines 123/136/159/174/217 read "supersedes the author's … `unchanged`" and were all read
as `mixed`, though each file's verdict is `improved`.

This is not a counter defect that blocks the claim: the frozen validity rule accepts a
single verdict word that appears on a multi-word line —
`python3 .ufo/waves/round-44/tools/check-fragment.py c2 <frag> <scratch>` returned
`VALID ('43','quality','outside')` for verdict `unprovable-but-better` on line 96
(`w1/out/K2Design/receipts/probe-f3.txt`). It is a draft-read defect, and it survives
any check that only re-reads the cited line.

## Evidence

All commands are read-only. Working dir `/home/vgpnk/Projects/shokunin`.

### 1. The draft reproduces the preregistration's junk control, not the truth

`python3 kama-shokunin/.ufo/waves/round-44/tools/check-fragment.py c2 corrected-ledger.tsv <scratch>`
(proposal copied from the draft with 19 rows corrected):

| ledger | agree | overclaim | underclaim | other | absent | n | table rows |
|---|---|---|---|---|---|---|---|
| draft (as generated) | 61 | 3 | 8 | 15 | 15 | 72 | 26 |
| corrected | **69** | **2** | **16** | **0** | 15 | 87 | **18** |
| corrected, r30 read `unprovable` | 68 | 3 | 16 | 0 | 15 | 87 | 19 |

Draft figures equal the preregistration control `junk-c2-noscorecard`
(`.ufo/waves/round-44/preregistration.json`, `controls.junk-c2-noscorecard.c2`:
`agree=61 overclaim=3 underclaim=8 other=15 absent=15`) — i.e. the expected
"no scorecard" state is exactly the draft's misreading, not a null state.
Receipts: `w1/out/K2Design/receipts/counter-corrected.txt` (summary line
`rows=204 valid=204 missing=0 bad=0 agree=69 overclaim=2 underclaim=16 other=0 absent=15
table_missing=18 table_extra=0 summary=0 axes=0 met=False`; `met=False` only because
SCORECARD is not edited by a seat), and `probe-f1..f5.txt`.

The 19 wrong rows (all corrected rows pass the frozen counter, `bad=0`):

| # | key | draft | correct | verdict line |
|---|---|---|---|---|
| 1-4 | 18/20/24/27 discernment self | mixed | **unchanged** | `kama.md:130,45,247,121` |
| 5-7 | 33 discernment self / 35,37 quality self | mixed | **improved** | `kama.md:222,62,46` |
| 8-12 | 12/14/15/16/17 discernment outside | mixed | **improved** | spotcheck `:123,136,159,174,217` |
| 13-16 | 29 expansion / 34 expansion / 35 quality / 39 discernment outside | mixed | **improved** | spotcheck `:69,87,113,76` |
| 17 | 43 quality outside | mixed | **unprovable-but-better** | spotcheck `:96` |
| 18 | 25 quality outside | harmed | **unchanged** | spotcheck `:187` (draft cited `:193` "quality is **not** harmed") |
| 19 | 25 discernment outside | improved | **unchanged** | spotcheck `:194` (draft cited `:200`, which quotes the author's SCORECARD line) |

False readings are provably false at the cited line:
`sed -n '187p;193p' round-25-verifier-spotcheck.md` → `- **Quality: unchanged.**` vs
`entry's fact false or stale, so quality is not harmed.`; the latter tokenizes to
`{'quality': {'harmed'}}` (receipt `probe-f1.txt` returns `VALID` for `harmed`).

### 2. Q1 — agreement is closure concurrence, not independent calibration

The outside file is committed **after** the self report in 29 of the 30 rounds
(R10 same minute: `03b5f0e8`/`b69b7ba2` 19:48:55-03; e.g. R43 report `70e6cd5f`
23:59:43-03 vs spotcheck `9d9cc93e` 01:03:59-03; full table
`w1/out/K2Design/q4-refile-times.tsv`). It is also written with the self report in view:
every one of the 30 spotcheck files names the author or the lane's verdict (1–16 hits;
e.g. R13 16), and
five verdict lines reason from the author's own value —
`round-12-verifier-spotcheck.md:123`, `round-14:136`, `round-15:159`, `round-16:174`,
`round-17:217` ("supersedes the author's … `unchanged`", "the author's `unchanged`
correctly described pending outside review"). `round-25-verifier-spotcheck.md:200` quotes
the lane's SCORECARD trend line outright.

So the ledger measures **whether the lane's verdict survived the closure that decides the
round**; it does not measure "SHONEN.md/SCORECARD entries match observed repo state"
(`AXES.md:15`). It is a legitimate self-assessment signal (the deciding authority's
judgment, not the author's), but it is not independent and must be labelled as
concurrence. The direction of flow also explains the 16 underclaims: the author wrote
`unchanged` pending outside review, and the closure then credited `improved`.

### 3. Q2 — the frozen order conflates polarity with evidence status

`ORDER = harmed < unchanged < unprovable < unprovable-but-better < improved`
(`tools/round44-verdict-ledger-audit.py`, docstring "Comparison"). `unchanged` is a
demonstrated non-change; `unprovable` is an absence of evidence. Ranking `unprovable`
above `unchanged` means:

- self `unprovable` vs outside `unchanged` → **overclaim**. Concrete case: r30 self
  bullet `**discernment: unprovable-but-not-yet**` (`kama.md:113`) while the same bullet
  says "the lane reports discernment **unchanged**" (`:116`), against outside
  `MANIFEST.json` rounds[?] discernment `unchanged`. The frozen order would call a
  *more cautious* self verdict an overclaim. Citing `:116` yields agreement
  (`probe` ledger `corrected-ledger.tsv`); citing `:113` yields `unprovable` and one more
  overclaim (`corrected-ledger-r30unprovable.tsv`: `agree=68 overclaim=3`). Both are
  counter-valid, so the line choice, not the evidence, decides the figure.
- self `unchanged` vs outside `unprovable` would be called an underclaim, when it is an
  assertion the evidence does not support.

The population has **zero** plain `unprovable` outside verdicts and one `unprovable`
self reading (r30, arguable), so the rung is effectively untested this round. The safe
move is to cite the lane's filed `unchanged` (`:116`) and disclose the `:113` label;
for future instruments, treat `unprovable` as an evidence bucket alongside `absent`,
not a rung.

The bottom rung is also a polarity claim, not a strength: `harmed` < `unchanged` makes
self `harmed` vs outside `improved` an "underclaim". The population's one sign reversal
is r23 quality (self `improved` at `.ufo/reports/round-23/kama.md:126`, outside `harmed`
at `MANIFEST.json` rounds[428]) — and it lands in the `absent` set, so it is named as
neither overclaim nor reversal by the table. Recommend: keep the frozen order, but in
SCORECARD prose name r23 as a **sign reversal** and state that the order is an
assertion-strength heuristic, not a merit scale.

### 4. Q3 — rounds 20-23 have outside verdicts, all recorded

`git -C kama-shokunin ls-tree --name-only 9d9cc93 corpus/lessons/ | grep verifier-spotcheck`
→ 30 files (10-19, 24-43); rounds 20-23 have only `round-20.md` … `round-24.md`.
The outside verdicts exist:

| round | MANIFEST | expansion | quality | discernment | evidence |
|---|---|---|---|---|---|
| 20 | rounds[397] | improved | improved | unchanged | `verification.rechecks` (no spotcheck field) |
| 21 | rounds[406] | unchanged | improved | unchanged | `verification.spotcheck`; `corpus/lessons/round-22.md:99-102` ("holding discernment unchanged") |
| 22 | rounds[418] | unchanged | improved | improved | `verification.spotcheck` |
| 23 | rounds[428] | unchanged | **harmed** | improved | `verification.spotcheck`; `corpus/lessons/round-24.md:55-60`; `LOG.md:1413-1415`; `SCORECARD.md:1256-1258` |

`round-24-verifier-spotcheck.md` does not cover earlier rounds (`grep -nE 'round-2[0-3]'` →
no hits), and `round-20.md:4-5` cites the R19 closure, not its own. So the 12 absents are
a **path-convention artifact**, not missing evidence: 11 of the 12 are agreements
(20e/20q/20d, 21e/21q/21d, 22e/22q/22d, 23e/23d) and the 12th is r23 quality
(self `improved`, outside `harmed`) — a real disagreement the lane already knew and
wrote down. Full table:
`w1/out/K2Design/q3-outside-verdicts.tsv`.

This also falsifies C2's novelty sentence ("which no surface of the lane did before"):
`SCORECARD.md:1256-1258` says "Outside closure rounds[428] supersedes the round23
author's admission and quality-improved readings", and `LOG.md:1413-1415` repeats it.
The honest claim is "no surface did it for all rounds / no ledger", not "no surface did
it before".

### 5. Q4 — no self report re-filed after closure with changed content

`git -C /home/vgpnk/Projects/shokunin log --format='%h %ad %s' -- .ufo/reports/round-N/kama.md`
plus `git rev-parse <commit>:<path>` comparisons (table
`w1/out/K2Design/q4-refile-times.tsv`):

- R10-R38: the only post-closure commits are the stray deletion `35b91714`
  (2026-10-25T09:21:14-03) and the repair `f47ad6ba` (09:29:03-03). The restore blob
  equals the pre-deletion blob for **all 29** files (`git rev-parse f47ad6ba:<path)` ==
  `git rev-parse 35b91714^:<path>`), so no verdict changed.
- R39-R43: no post-closure content commit. R39's erratum `7b536e11` (10:16:20-03)
  precedes its spotcheck commit (10:20:08-03) and closure (13:20:47Z); its diff is
  `33 insertions(+)` with no trend line changed
  (`git diff e52edfda 7b536e11 -- .ufo/reports/round-39/kama.md`).
- R21's "late wave evidence appendix" `a28c80cc` (09:33:08-03) precedes closure
  (09:51:28-03) by 18 min.
- Cross-round absorption is real, not a re-file: 14 reports cite the **previous** round's
  spotcheck (R11,12,14,15,16,19,20,26,27,29,36,41,42,43), and R20's report states the
  R19 outside verifier "disagreed with the R19 author expansion verdict"
  (`kama.md:45`) — the lane wrote R20 knowing the R19 overclaim that the ledger now
  scores (19 expansion `improved` vs outside `unchanged`).

## Impacted axes

- **calibration (C2's axis)** — the draft would publish 8 false disagreements
  (6 `other` rows that are agreements: 24d, 33d, 35q, 37q, 34e, 43q; plus 25q and 25d),
  misclassify 9 real underclaims as `other` (12,14,15,16,17,18,27,29,39), and report
  `agreement=61/72` instead of `69/87`. That is a *worse* self-assessment record than the
  state it replaces.
- **false provenance / novelty** — the claim's "which no surface of the lane did before"
  is false for r23 quality (`SCORECARD.md:1256-1258`, `LOG.md:1413-1415`) and its
  outside population silently drops 12 verdicts that exist in `MANIFEST.json`.
- **premature saturation** — `met=True` is reachable with the draft's wrong values; the
  counter cannot distinguish a filed verdict from a quoted or negated one, so "met" is
  not evidence that the ledger carries the verdicts.

## Smallest safe correction (for the L1; counters and preregistration frozen)

1. Replace the 19 rows above in `registry/verdict-ledger.tsv` with the corrected values
   and lines; the proposal is `w1/out/K2Design/corrected-ledger.tsv` (counter:
   `valid=204 bad=0`). For r30 cite `kama.md:116` (`unchanged`) and put the `:113`
   `unprovable-but-not-yet` label in the note, or cite `:113` and state the overclaim —
   do not cite one and describe the other.
2. Keep the 12 outside rows `absent` (the counter requires the lane path); put the
   MANIFEST verdict and index in the `note` as the proposal does (`rounds[397|406|418|428]`),
   and say in SCORECARD prose that those 12 outside verdicts exist outside the frozen
   path.
3. SCORECARD: heading exactly `### Round-44 calibration ledger`, an 18-row table
   (`w1/out/K2Design/proposed-scorecard-table.tsv`) and the exact summary line
   `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`; the `## Axes` calibration
   row must name `registry/verdict-ledger.tsv`. Add prose bullets **outside any table**
   (the parser only reads lines starting with `|`):
   - r23 quality self `improved` vs outside `harmed` — a sign reversal excluded by the
     frozen path; cite `SCORECARD.md:1256-1258` and `MANIFEST.json` rounds[428];
   - r38 self has no trend section (`.ufo/reports/round-38/kama.md` headings: only
     `## Notes`), so its 3 `absent` rows are an omission, not a disagreement;
   - the outside file is committed after the self report and cites the author, so
     `agreement` is concurrence, not independent accuracy.
4. Reword the round report's novelty sentence to "no surface did it for all rounds".
5. Instrument findings for the next round (do not edit the frozen counter): `mixed` is
   optional whenever a line carries two verdict words, so a seat can park a disagreement
   in `other`; `absent` is accepted whenever the file is missing even where
   `MANIFEST.json` records the verdict; `unprovable` is an evidence gap, not a strength
   rung. Add the closure's recorded trend as an accepted outside source and require the
   verdict word to be the line's operative one.

## Commands and receipts

- `python3 .ufo/waves/round-44/tools/check-fragment.py c2 <fragment> /fast/scratch/hyaku/kama-r44/K2Design/<dir>`
  → helper exit 0 in every run; counter line as quoted; receipts in
  `w1/out/K2Design/receipts/` (`counter-corrected.txt`, `counter-r30unprovable.txt`,
  `probe-f1.txt` … `probe-f5.txt`).
- `git -C kama-shokunin show 9d9cc93:corpus/lessons/round-<N>-verifier-spotcheck.md` and
  `git -C /home/vgpnk/Projects/shokunin show b0fd7b7f:.ufo/reports/round-<N>/kama.md`
  for every cited line (read-only).
- `python3` MANIFEST extract: kama closure entries `rounds[397,406,418,428]` carry the
  trends above; SCORECARD/LOG citations verified at lane base `9d9cc93`.
- No tool installed or updated. Scratch `/fast/scratch/hyaku/kama-r44/K2Design` removed
  after copying receipts; no lane file, git index or jj state touched.
