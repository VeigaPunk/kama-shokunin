# Rev1Head — the lane's head re-derivation practice since round 42

**Verdict:** the per-round preamble banner is a *new* practice introduced by the round-42 head
re-derivation — the banner was byte-stable across the 68 SCORECARD commits from round 5 to round
41, then rewritten in place in every round from 43 to 47 — and only two of those five rewrites
were repaired by the build: the round-42, 43 and 44 banner texts are still absent from
`SCORECARD.md` at `380bcdff`, and the frozen C1 cannot see any of the five (its event threshold is
20 deleted lines per commit/file, each banner is one line). `regressed=0`/`exit 0` at the build
tip is therefore a record of a two-of-five repair, not of the invariant. The banner is an *index*
(machine-derived and machine-checked by `tools/round42-selfdesc-reconcile.py`, and its per-round
delta is two digits and one phrase), so the truer fix is a contract change that gives it a `## `
title v3 can express, with the content guarantee left to the checker that already derives it;
keeping each superseded banner is the correct **r48 stopgap** (C1 pins the exempt set to exactly
five titles) but it is not the fix and it is not enforceable.

## 1. Method

Read-only git over the lane (no writes, no `git add/commit/checkout` in
`/home/vgpnk/Projects/shokunin/kama-shokunin`); one `git clone --shared` in my scratch for the
counter runs and for the counterfactual commit. All `SCORECARD.md` line numbers cite the committed
blob at `380bcdff` (`git show 380bcdff:SCORECARD.md`), not the live working tree — at the time of
writing that tree carries an uncommitted round-48 edit (line 6 rewritten to round 48, r47 banner
appended at 2743).

* Head region = the lines before the `## Round 6` heading (at the build tip that is
  `SCORECARD.md:187`; across the analysed window it moves 146-198 as the head sections grow).
  The analyser takes the *parent's* boundary per commit and clamps a hunk that straddles it.
* `analyze.py` classifies every `git diff -U0 <parent> <commit> -- SCORECARD.md` hunk in that
  region by the parent section of each deleted line (section = the last line starting with
  `## ` at or before it; none = preamble) and by table/prose kind.
* `pass2.py` adds, per class, whether each deleted line still occurs (stripped) in the file at
  the commit itself and at the build tip: i.e. "was the replaced text kept anywhere in the file".
* `evidence.py` runs the frozen C1 at the base and the build, the v3 tool at the base and the
  build, and one counterfactual.

Commands (all reproduced in the deliverables):

```
git -C <clone> log --format=%H -- SCORECARD.md                      # 94 commits
python3 analyze.py <clone> c6199a25 > head-rewrites-all.json        # all history
python3 pass2.py  <clone> 4fe239a4 380bcdff > head-rewrites-r42.json
python3 tools/append-only-audit.py --repo <clone> --to <rev> \
        --contract <clone>/registry/append-only-contract.tsv [--threshold 1] --json
python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip <rev> --scratch <dir>
```

## 2. What each commit rewrote in place before `## Round 6`

22 first-parent commits between `4fe239a4` (round-41 integration) and `380bcdff` touch
`SCORECARD.md`; 19 of them delete head-region lines: 282 lines deleted, of which 235 non-blank,
39 kept somewhere in the file at the same commit, 196 dropped. `deleted` counts blank lines,
`kept`/`dropped` do not. (`head-rewrite-classes.tsv`, `head-rewrites-r42.json`.)

| commit | round | head del | kept | dropped | banner (del/kept/dropped) | classes (del, /d = dropped) |
|---|---|---|---|---|---|---|
| dd9f5dc6 | 42 | 31 | 23 | 7 | **8/8/0** | Planned:pointer 9, **banner 8**, Axes:row 6/6d, Retired 6, Axes:prose 1/1d, Saturation 1 |
| 2793eb51 | 42 | 1 | 0 | 1 | – | Axes:row 1/1d |
| c8c92db4 | 42 | 2 | 0 | 2 | – | Axes:row 2/2d |
| 8bc8e375 | 42 | 2 | 0 | 2 | – | Axes:row 1/1d, Capabilities:mirror 1/1d |
| dabc6eee | 43 | 1 | 0 | 1 | – | Axes:row 1/1d |
| 44fa5627 | 43 | 9 | 0 | 9 | **1/0/1** | Axes:row 3/3d, **banner 1/1d**, Axes:prose 1/1d, Planned:pointer 1/1d, Retired 1/1d, Capabilities:mirror 1/1d, Saturation 1/1d |
| f1a4ad2a | 43 | 3 | 0 | 3 | – | Axes:row 3/3d |
| 9307b15e | 43 | 1 | 0 | 1 | – | Planned:pointer 1/1d |
| ef76777e | 44 | 18 | 8 | 5 | – | Planned:pointer 15/2d, Axes:row 3/3d |
| d48e8cc3 | 44 | 1 | 0 | 1 | **1/0/1** | **banner 1/1d** |
| 21945c61 | 45 | 3 | 0 | 3 | **1/0/1** | **banner 1/1d**, Axes:row 1/1d, Planned:pointer 1/1d |
| 0718b6ab | 45 | 176 | 0 | 140 | **4/0/4** | Historical head sections 48/34d, Actual round 5 43/39d, Axes:prose 26/19d, Capabilities:mirror 18/14d, Axes:row 16/16d, Move log 9/8d, **banner 4/4d**, Planned:pointer 4/2d, Retired 4/2d, Saturation 4/2d |
| 4340cf2f | 46 | 8 | 0 | 8 | **1/0/1** | Axes:row 3/3d, **banner 1/1d**, Planned:pointer 1/1d, Retired 1/1d, Capabilities:mirror 1/1d, Saturation 1/1d |
| 4991ecc2 | 46 | 2 | 0 | 2 | – | Axes:row 1/1d, Planned:pointer 1/1d |
| 42ea1204 | 46 | 14 | 7 | 2 | – | Planned:pointer 14/2d |
| 383f1fc7 | 47 | 9 | 1 | 8 | **1/0/1** | Axes:row 3/3d, Capabilities:mirror 2/1d, **banner 1/1d**, Planned:pointer 1/1d, Retired 1/1d, Saturation 1/1d |
| 3442d707 | 47 | 1 | 0 | 1 | – | Axes:row 1/1d |

Totals by class: exempt-section lines 165 deleted / 106 dropped (Axes rows 45, Axes prose 28,
Planned 48, Retired 13, Saturation 8, Capabilities 23) — that is exactly the re-derivation the
contract forgives. Non-exempt head lines 117 deleted / 90 dropped: **banner 17/9d**, Move log
9/8d, Actual round 5 43/39d, Historical head sections 48/34d (the last three are almost entirely
the `0718b6ab` append/truncation bug, whose text `82b5e9d3` re-appended). 165 + 117 = 282.

The classification answers the item directly: the sections the lane rewrites every round are
`## Axes` rows (45 deletions, 0 kept), the `## Planned` pointer (48/12 dropped), and — new since
round 42 — **the preamble banner (5 single-line rewrites, 0 kept)**. Everything else in the head
was rewritten by the one truncation event, not by the practice.

Pre-round-42 baseline: the banner was created at `e246c40e` (round 5) as an 8-line paragraph and
was **not touched by any of the 68 SCORECARD commits between then and `dd9f5dc6`**. Round 42 is
the only rewrite that kept its predecessor: all 8 old lines were moved verbatim under
`### Banner (round-5 text)` (today `SCORECARD.md:139-152`). Rounds 43-47 kept none.

## 3. Banner lineage and where each replaced text went

`banner-lineage.tsv`, `banner-B*.txt` (byte-exact copies), `missing-banners.txt`:

| version | introduced | superseded by | kept by it | in the file at `380bcdff` |
|---|---|---|---|---|
| B5  (round 5, 8 lines) | e246c40e | – | – | **yes, `SCORECARD.md:145`** (under §Historical head sections) |
| B42 (708 chars) | dd9f5dc6 | 44fa5627 (r43) | no | **absent** |
| B43 (737) | 44fa5627 | d48e8cc3 (r44) | no | **absent** |
| B44 (745) | d48e8cc3 | 21945c61 (r45) | no | **absent** |
| B45 (749) | 21945c61 | 4340cf2f (r46) | no | yes, `SCORECARD.md:2740` (build append) |
| B46 (753) | 4340cf2f | 383f1fc7 (r47) | no | yes, `SCORECARD.md:2742` (build append) |
| B47 (757) | 383f1fc7 | – | – | yes, `SCORECARD.md:6` (current) |

The appended copies are byte-exact: the line at `:2740` equals `git show 82b5e9d3:SCORECARD.md |
sed -n 6p` and `:2742` equals `git show 42ea1204:SCORECARD.md | sed -n 6p` (single exact-line
hits, no duplicates).

## 4. Against `SCORECARD.md:6` — and against the other two surfaces

`SCORECARD.md:6` promises, verbatim: "the round-5 banner and the head sections they replace are
kept verbatim under §Historical head sections."

* For the round-5 banner and the five superseded head sections the promise holds: B5 is at
  `SCORECARD.md:145`, the banner/Planned/Retired/Capabilities/Saturation texts of rounds 5/5/3/10/10
  are at `SCORECARD.md:143-186`.
* The promise says nothing about the banners of rounds 42-47. The build note at
  `SCORECARD.md:2738` reads line 6 as covering them ("although line 6 says the head text it
  replaces is kept verbatim"); that is true of the round-42 rewrite only. So the C1 build finding
  names the wrong invariant.

The invariant actually broken is the one in `registry/append-only-contract.tsv:3`, which declares
`SCORECARD.md  A-corr  corpus/README.md:761  exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`:
everything outside those five `## ` sections — the preamble included — is append-only, "corrections
land as new entries". Under that row the five banner rewrites are violations, not derivations.

But `tools/round42-selfdesc-reconcile.py:160-166` machine-derives the banner: it takes `head` =
every line before the first `## ` and enforces `operability + calibration` present,
`operability and freshness` absent, and `Latest measured round: <max ## Round N>`
(`:186-190`). A paragraph that a tool re-derives from the tree and validates is an index.

So one line is simultaneously **declared a record** (contract row), **derived as an index**
(reconcile), and **promised as neither** (line 6). That three-way disagreement, not the C1
regression, is the calibration defect.

Index evidence beyond the reconcile tool: the per-round delta is a template substitution.
`B45` vs `B46`: `'5'→'6'` (twice), `' and'→','`, insert `' and 46'`. `B46` vs `B47`: `'6'→'7'`
(twice), same comma, insert `' and 47'`. `B42` vs `B47`: only the round number and the
"kept current in rounds …" list. No score, axis or limit changes.

## 5. Why `regressed=0` at the build tip is not evidence

Frozen counter, same clone, same contract (`evidence.out`):

```
C1@base  exit=1 selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 … met=False
C1@build exit=0 selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5
                lane_failures=0 ungraded_lines=89 met=True
```

The base line is all-zero because the v3 tool and contract do not exist at `33e0058`; the build's
"v3 reported regressed=1 at the base" is only observable by running the *built* tool at that tip,
which I did:

```
tool@base  exit=1 regressed=1   0718b6ab deleted=2421 graded=2349 ungraded=72 restored max=2349 to=2348
tool@build exit=0 regressed=0   0718b6ab …                                                          to=2349
```

Now the same tool, same tip, `--threshold 1` (`audit-threshold1-build.json`, exit 1, 98 events):

```
44fa5627 deleted 9 graded 1 unrestored max 0 to 0     <- B42, never restored
d48e8cc3 deleted 1 graded 1 unrestored max 0 to 0     <- B43, never restored
21945c61 deleted 3 graded 1 unrestored max 0 to 0     <- B44, never restored
4340cf2f deleted 8 graded 1 restored   max 1 to 1     <- B45, restored by the build append
383f1fc7 deleted 9 graded 1 restored   max 1 to 1     <- B46, restored by the build append
dd9f5dc6 deleted 31 graded 14 restored max 14 to 14   <- B5 kept in place at r42
```

So the instrument *can* express this violation; the default threshold hides it. The threshold is
frozen in two places: `tools/round48-append-audit-v3-check.py:137` (`THRESHOLD = 20`) and
`tools/append-only-audit.py:62` ("event (commit, file) with |D| >= threshold (default 20)").

Counterfactual (`evidence.py`, commit `f08ebd0564ac` on a branch in my clone, `rev-parse
--show-toplevel` asserted equal to the clone before the commit): rewrite `SCORECARD.md:6` from
round 47 to round 48 and append nothing, exactly the r43-r47 practice —

```
tool@cf exit=0 events=5 regressed=0 partial=0 unrestored=0 vanished=0
tool@cf --threshold 1: f08ebd0564ac deleted 1 graded 1 unrestored max 0 to 0
```

The practice can repeat next round and the frozen counter stays green. The build's remedy is
therefore not self-enforcing: it is a one-round repair of two lines, and the three lines it did not
repair are already the proof. The lane is already applying it again by hand in the working tree
(uncommitted at the time of writing: line 6 set to round 48, the r47 banner appended at 2743) —
which is exactly the shape that has no check behind it.

## 6. Proposed machine-readable form for the preamble banner

v3's region grammar is `*`, `exempt=<titles>@path:line`, `only=<prefix>@path:line`, and a section
is "the title of the last line at or before it that starts with `## `". The preamble has no
`## ` line before it, so it is permanently *graded* and no exempt title can name it — the only
forms v3 can express are "delete nothing" or "give it a `## ` title". Proposal — the index form,
three anchors:

1. **Constant preamble.** `SCORECARD.md:6` becomes a fixed pointer paragraph (it stays the row's
   region pointer and still contains `re-derived` and every title, so the declaration keeps
   binding):

   > Current authority: the single `**Current authority (round N):**` line of `## Current
   > authority` below. This paragraph is constant; a round re-derives that one line and never
   > removes it. The `## Axes` table, `## Planned`, `## Retired`, `## Saturation` and
   > `## Capabilities` are re-derived from the tree by `tools/round42-selfdesc-reconcile.py`
   > (round-42 claim C1); the round-5 banner and the head sections they replace are kept verbatim
   > under `## Historical head sections`.

2. **`## Current authority`** — a round-invariant `## ` title with exactly one entry line, the
   current banner text prefixed with the round:

   ```
   ## Current authority

   **Current authority (round 47):** the assigned axes are operability + calibration (…).
   Latest measured round: 47. Calibration 7 is the lowest assigned axis, … nudge is inactive. …
   ```

   Machine grammar (one line, one section):
   `^\*\*Current authority \(round ([0-9]{1,3})\):\*\* ` + required `operability + calibration`
   + `Latest measured round: <same N>` + `nudge is (inactive|active)`. The section holds exactly
   one line, so "present but re-derived" and "gutted" are distinguishable.

3. **Contract row** (`proposed-contract-row.tsv`):

   ```
   SCORECARD.md  A-corr  corpus/README.md:761
     exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities|## Current authority@SCORECARD.md:6
   ```

   v3's `eligible` rule then gives exactly the semantics an index needs: the line may be
   rewritten (count stays 1 → ungraded) but may not vanish (count 0 < parent's 1 → graded →
   `unrestored`). The content guarantee is not v3's; it is the existing banner leg of
   `tools/round42-selfdesc-reconcile.py:186-190`, rewired to read the section's single entry
   (fallback: lines before the first `## `).

4. **One counter leg to close the threshold hole** (for C1 v4, because a 1-line rewrite is under
   the 20-line event threshold in *any* form): `preamble` — the lines of `SCORECARD.md` before the
   first `## ` at `--tip` must be byte-equal to the same lines at the frozen base
   (`STABLE_BASE = 33e0058277…` already exists in the counter, `:138`). No new grammar, no
   threshold: any future in-place edit of the preamble is an event at size 1.

Migration is one commit in round 49: insert the `## Current authority` title, move line 6's text
into the entry, put the constant pointer at line 6, update the contract row and the counter's
`HEAD_TITLES` (`:139`), and rewire the reconcile banner leg. The replaced r47 banner should be
appended once under whatever archive is kept, so the migration itself deletes nothing unexplained.
`proposed-SCORECARD-head.md` and `proposed-SCORECARD-head.diff` are the exact head text against
`380bcdff`.

**If the lane instead keeps the record reading** (authority text is a claim, not a derivation),
then the build's append is the right shape but must be completed and instrumented:
(a) append B42/B43/B44 byte-exact (`missing-banners.txt`); (b) give the archive a `## ` title
(today it is `### Superseded head banners`, see D4); (c) add a `banner-archive` leg at threshold 0:
every `**Current authority (round N):**` line that exists at any commit in the window must exist at
`--tip`.

## 7. Which is the truer fix — keeping each superseded banner, or a contract change

**Contract change**, for four reasons:

1. The banner is derived: `round42-selfdesc-reconcile.py` reconstructs and validates it from the
   dated sections, and the round-over-round delta carries no fact the round sections do not
   (two digits and one phrase). Keeping versions of a derived line is preserving an index as if it
   were evidence.
2. Keeping cannot be enforced by the instrument that motivated it: the class it repairs is
   invisible at the frozen threshold (counterfactual: exit 0), and the text it archives is never
   validated by anything (the reconcile tool reads only the `head`, so appended copies are inert).
3. The build's own note promises the practice forward ("from round 48 on, each round appends the
   banner it replaces here", `SCORECARD.md:2738`) while three earlier banners of the same class are
   already missing — a rule stated in prose and contradicted by the same file is exactly the
   round-47 complaint (contract in prose only) that produced v2/v3.
4. The contract change is the only form that makes the *declared* rule match the *actual* practice
   without a growing archive, and `exempt` + `eligible` already has the right semantics for it.

Counter-argument, stated plainly: at this round's freeze the contract change is **not admissible**
— `tools/round48-append-audit-v3-check.py:140-146` pins `REQUIRED["SCORECARD.md"] = ("exempt",
frozenset(HEAD_TITLES))` and compares the parsed region's title set for equality, so adding
`## Current authority` makes C1's `contract` leg fail (`contract=0`). The build's append was the
only admissible repair at r48, and it is correct as a stopgap. It is not the fix, and the r48 note
should say so.

## 8. Defects (file:line, showing command, proposed fix)

**D1 — three superseded banners are still unrestored at the build tip; C1 cannot see it.**
`SCORECARD.md` (B42/B43/B44 absent), `tools/round48-append-audit-v3-check.py:137`,
`tools/append-only-audit.py:62`.
Show: `python3 tools/append-only-audit.py --repo <clone> --to 380bcdff --contract
<clone>/registry/append-only-contract.tsv --threshold 1 --json` → exit 1, `44fa5627 … unrestored
max 0 to 0`, `d48e8cc3 … unrestored`, `21945c61 … unrestored`; the default threshold run of the
same tip → exit 0, `regressed=0`.
Fix: adopt §6 (index form) in r49, or append B42/B43/B44 from `missing-banners.txt` now.

**D2 — the build note names the wrong invariant.** `SCORECARD.md:2738`.
Line 6 promises the round-5 banner and the round-5/round-10 head sections; those are present
(`:139-186`, `:145`). It does not promise the banners of rounds 42-47.
Fix: replace "although line 6 says the head text it replaces is kept verbatim under §Historical
head sections" with the contract-row statement (`registry/append-only-contract.tsv:3`: the
preamble is graded, i.e. declared a record), or change line 6 to match §6.

**D3 — one line, three categories.** `SCORECARD.md:6` vs `registry/append-only-contract.tsv:3`
(record) vs `tools/round42-selfdesc-reconcile.py:160-166,186-190` (index).
Show: `python3 -c` difflib of `git show 21945c61:SCORECARD.md | sed -n 6p` and
`git show 4340cf2f:SCORECARD.md | sed -n 6p` → `'5'→'6'` twice, `' and'→','`, insert `' and 46'`.
Fix: §6.

**D4 — the archive is in the wrong section and will accrete there.**
`SCORECARD.md:2736` is a `### ` heading, so it belongs to `## Round 47 — …` at `SCORECARD.md:2701`
(`awk 'NR<=2736 && /^## /{l=NR;t=$0} NR==2736{print l,t}' SCORECARD.md` → `2701 ## Round 47 …`).
The note says each future round appends "here", so r49's append lands inside the round-47 record.
Fix: if the archive is kept, promote it to `## Superseded head banners` (own section), or append
inside the superseding round's `## Round N` section.

**D5 — the frozen counter's threshold hides the whole class (frozen; report, do not edit).**
`tools/round48-append-audit-v3-check.py:137`, `tools/append-only-audit.py:62`; counterfactual
`f08ebd0564ac`: default `exit 0 regressed 0`, `--threshold 1` `unrestored max 0 to 0`.
Fix: C1 v4 `preamble` leg (§6.4), or `banner-archive` leg threshold 0 (§6 alternative).

## 9. Confidence and limits

* Head classification, per-class kept/dropped counts, banner lineage and byte-exact copies: high
  (raw `git diff -U0` / `git show`, scripts and JSON in the deliverables; re-runnable).
* Instrument behaviour (`regressed=1` at base, `regressed=0` at build, threshold-1 unrestored set,
  counterfactual exit 0): high (frozen counter and tool run against the lane's own contract).
* `SCORECARD.md:6` reading and the record/index judgement: high for the wording; the
  recommendation is a design judgement marked as such — the record reading is stated as the
  alternative with the criteria that would make it right (authority text is a claim, not a
  derivation).
* Not measured: rounds after `380bcdff` (`b85783e8`, wave spec, does not touch SCORECARD.md) —
  none of this changes there.

No tools installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r48/Rev1Head` removed after the
copy; the counterfactual commit existed only in that clone.

## Deliverables

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/Rev1Head/`

* `analyze.py`, `pass2.py`, `evidence.py` — the three runs above (`analyze.py`/`pass2.py` take repo + revs as argv; `evidence.py` takes the scratch root from `$S`).
* `head-rewrites-all.json` (94 commits, all history), `head-rewrites-r42.json` (round-41 integration
  → build), `head-rewrite-classes.tsv`, `banner-lineage.tsv`.
* `banner-B5.txt`, `banner-B42.txt`, `banner-B43.txt`, `banner-B44.txt`, `banner-B45.txt`,
  `banner-B46.txt`, `missing-banners.txt` — byte-exact texts and the three still absent.
* `audit-base-33e00582.json`, `audit-build-380bcdff.json`, `audit-threshold1-build.json`,
  `evidence.out` — the tool/counter outputs quoted above.
* `proposed-SCORECARD-head.md`, `proposed-SCORECARD-head.diff`, `proposed-contract-row.tsv` — §6.

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/Rev1Head.md`
