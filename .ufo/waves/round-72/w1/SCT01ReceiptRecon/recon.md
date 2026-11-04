# SCT01ReceiptRecon — receipts, revisions, and the drift class (kama round 72, wave 1)

Read-only reconnaissance. No lane file was edited; the only writes are under this wave dir
(`.ufo/waves/round-72/w1/SCT01ReceiptRecon/`) and the throwaway fixture under `/fast/scratch`.

**Lane tip pinned for every check: `a3cc39f08f4692e990921cf938d0269f6c25fc93` (branch `master`).**
`master` read `090a0b25a71298ed1a58e1f81315d850f4932e74` (the round-72 freeze commit, whose
`controls/freeze.txt` names it as `base=`) when this seat started, and advanced to `a3cc39f08f4692e990921cf938d0269f6c25fc93`
(the 22:41:23 -03 amendment/dispatch commit) while the recon was running. Every table below is
computed at `a3cc39f08f4692e990921cf938d0269f6c25fc93` against committed blobs (`git show a3cc39f0:<path>`), never the worktree.

## 1. Population and method

Sources scanned (the seat's stated population):

| Source | Round |
|---|---|
| `SCORECARD.md` `## Round 70 …` section (from the heading to the round-71 heading) | 70 |
| `SCORECARD.md` `## Round 71 …` section (heading to EOF) | 71 |
| `corpus/lessons/round-70.md` | 70 |
| `corpus/lessons/round-70-verifier-spotcheck.md` | 70 |
| `corpus/lessons/round-71.md` | 71 |
| `corpus/lessons/round-71-verifier-spotcheck.md` | 71 |

Extraction (`enumerate.py`, read-only git plumbing):

1. wave-rooted citations matching `\.ufo/waves/round-7[0-9]/…`;
2. section-relative citations matching `measured/…`, `controls/…`, `w1/…`, resolved against
   `.ufo/waves/round-<the section's round>/` (the same resolution the lane's receipt-pointer
   audit performs) — matches already inside a wave-rooted span are skipped;
3. `{a,b}` brace lists expanded to one path per member; `*` globs expanded against
   `git ls-tree -r --name-only a3cc39f0`.

**Class rule.** *receipt* = a cited file under a `/measured/` directory or with a `.out`
extension; *script* = `.py`; *evidence* = any other cited file; *dir* = a cited directory;
*missing* = cited path absent from the tip tree. All five classes are counted; only receipts
are graded below.

**Grade.** For each receipt: exists at the tip (`cat-file -t`); first five lines carry
`# tip=<40-hex>` or `# rev=<40-hex>` (the frozen C2 form, **strict**) or the same token without
the leading `#` (**lenient** — the round-70 receipts' house form); header revision is an
ancestor of the tip; and `git diff --name-only <rev> a3cc39f0` intersects the instrument-input
prefixes. Two prefix sets are reported because they differ:

* **5-prefix (this seat's text):** `tools/`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`,
  `corpus/knowledge/`.
* **8-prefix (the frozen C2 list):** the five above plus `registry/`, `plans/`.

A header revision that does not resolve is a finding on its own (`shifted`, reason
`non-ancestor`), independent of any diff.

Raw citation count: **116** → **101** deduplicated `(source, path)` rows →
**77 receipt citations over 39 distinct receipt paths**, plus
14 evidence, 5 dir, 4 script and 1 missing rows.
The full 77-row citation table is `table.tsv` in this directory; the per-machine
artefacts are `recon.json`, `report71-receipts.json`, `commands.out`, `ignored-fixture.out`.

## 2. Table A — receipts per source

| source | receipts cited | unbound | `# tip=`/`# rev=` | `tip=` only | shifted by 5-prefix spec | shifted by 8-prefix freeze | non-ancestor | stale (absent at tip) |
|---|---|---|---|---|---|---|---|---|
| `SCORECARD.md#Round-70` | 12 | 8 | 0 | 4 | 4 | 4 | 1 | 0 |
| `SCORECARD.md#Round-71` | 10 | 7 | 3 | 0 | 0 | 3 | 0 | 0 |
| `corpus/lessons/round-70-verifier-spotcheck.md` | 15 | 11 | 0 | 4 | 4 | 4 | 1 | 0 |
| `corpus/lessons/round-70.md` | 17 | 10 | 0 | 7 | 7 | 7 | 3 | 0 |
| `corpus/lessons/round-71-verifier-spotcheck.md` | 16 | 13 | 3 | 0 | 0 | 3 | 0 | 0 |
| `corpus/lessons/round-71.md` | 7 | 6 | 1 | 0 | 0 | 1 | 0 | 0 |
| **total (occurrences)** | **77** | **55** | **7** | **15** | **15** | **22** | **5** | **0** |

Table sizes: **receipts enumerated 77** (occurrences; 39 distinct
paths) · **unbound 55** (28 distinct) ·
**shifted 22** by the frozen list (11 distinct),
**15** by the seat text's five prefixes (8 distinct) ·
**stale 0** · non-ancestor 5 (3 distinct).

## 3. Table B — every distinct cited receipt path (39)

Column key: *header* = form found in the first five lines; *rev* = the 40-hex it names;
*anc* = is that revision an ancestor of the tip; *Δ5*/*Δ8* = does `<rev>..tip` touch that
prefix set; *Δfiles* = files in `<rev>..tip`; *touching* = instrument-input paths it touches
(first four); *sources* = `SC:` = SCORECARD section, `L:` = lesson.

| receipt path (`W:` = `.ufo/waves/`) | exists@tip | header | rev | anc | Δ5 | Δ8 | Δfiles | touching | sources |
|---|---|---|---|---|---|---|---|---|---|
| `W:round-70/measured/after/census-at-af6eb6c2.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/census-at-tip.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/check-kill-probe-gutted.out` | yes | `tip=` no `#` | a7ae13ab6211 | **no** | **touches** | **touches** | n/a | rev absent from lane | L:round-70.md |
| `W:round-70/measured/after/check-kill-probe-intact.out` | yes | `tip=` no `#` | a7ae13ab6211 | **no** | **touches** | **touches** | n/a | rev absent from lane | L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/gutted-check-selftest-passes-at-clean-tip.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md |
| `W:round-70/measured/after/newest-closure-at-tip.out` | yes | none | — | — | — | — | — | — | L:round-70.md |
| `W:round-70/measured/after/receipt-pointer-audit-at-73597158.out` | yes | none | — | — | — | — | — | — | L:round-70.md |
| `W:round-70/measured/after/reconciler-at-73597158.out` | yes | `tip=` no `#` | 73597158ec1c | yes | **touches** | **touches** | 459 | PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/knowledge/cross-lane-scope.md | L:round-70.md |
| `W:round-70/measured/after/reconciler-at-af6eb6c2.out` | yes | `tip=` no `#` | af6eb6c29d78 | yes | **touches** | **touches** | 449 | PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/knowledge/cross-lane-scope.md | L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/reconciler-at-tip.out` | yes | `tip=` no `#` | 7be07423b988 | yes | **touches** | **touches** | 465 | PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/knowledge/cross-lane-scope.md | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/reconciler-record-only-dry.out` | yes | `tip=` no `#` | af6e1c84d146 | **no** | **touches** | **touches** | n/a | rev absent from lane | L:round-70-verifier-spotcheck.md, L:round-70.md |
| `W:round-70/measured/after/refused-member-control-new.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/selfdesc-selftest-at-af6eb6c2.out` | yes | none | — | — | — | — | — | — | SC:Round-70 |
| `W:round-70/measured/after/selfdesc-selftest-at-tip.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/after/worktree-landing-final.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md |
| `W:round-70/measured/before/census-at-base.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md |
| `W:round-70/measured/before/reconciler-at-base.out` | yes | `tip=` no `#` | 6035e952c252 | yes | **touches** | **touches** | 476 | PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/knowledge/cross-lane-scope.md | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/before/refused-member-control-old.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md, SC:Round-70 |
| `W:round-70/measured/final/census.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md, L:round-70.md |
| `W:round-70/measured/final/newest-closure.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md |
| `W:round-70/measured/final/receipt-pointer-audit.out` | yes | none | — | — | — | — | — | — | L:round-70-verifier-spotcheck.md |
| `W:round-70/measured/final/reconciler.out` | yes | `tip=` no `#` | a8df1af54ca2 | yes | **touches** | **touches** | 366 | PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/knowledge/cross-lane-scope.md | L:round-70-verifier-spotcheck.md |
| `W:round-71/measured/after/boundary-at-tip.out` | yes | `# tip=` | 4b2846535fd9 | yes | no | **touches** | 19 | plans/round-72-claims.md | L:round-71-verifier-spotcheck.md, SC:Round-71 |
| `W:round-71/measured/after/pre-report-at-tip.out` | yes | `# tip=` | 4b2846535fd9 | yes | no | **touches** | 19 | plans/round-72-claims.md | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-71 |
| `W:round-71/measured/after/province-claims-at-tip.out` | yes | `# tip=` | 4b2846535fd9 | yes | no | **touches** | 19 | plans/round-72-claims.md | L:round-71-verifier-spotcheck.md, SC:Round-71 |
| `W:round-71/measured/before/PROVINCE-base.md` | yes | none | — | — | — | — | — | — | L:round-71.md |
| `W:round-71/measured/before/census-shim-control.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-71 |
| `W:round-71/measured/before/pre-report-shortcut.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-70, SC:Round-71 |
| `W:round-71/measured/before/province-claims.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, SC:Round-70, SC:Round-71 |
| `W:round-71/w1/EX01PreReportGate/control-fixture.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, SC:Round-71 |
| `W:round-71/w1/EX01PreReportGate/selftest.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |
| `W:round-71/w1/EX02CensusBoundary/fail-waiver-probe.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |
| `W:round-71/w1/EX02CensusBoundary/selftest.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |
| `W:round-71/w1/EX02CensusBoundary/shim-verdicts.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |
| `W:round-71/w1/EX03ProvinceClaims/kill1-flipped.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-71 |
| `W:round-71/w1/EX03ProvinceClaims/kill2-wrongtag.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-71 |
| `W:round-71/w1/EX03ProvinceClaims/kill3-rewrite.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md, L:round-71.md, SC:Round-71 |
| `W:round-71/w1/EX03ProvinceClaims/selftest.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |
| `W:round-71/w1/MT01MutantGates/logs/c2-pristine-selftest.out` | yes | none | — | — | — | — | — | — | L:round-71-verifier-spotcheck.md |

## 4. Findings (a)

1. **Nothing cited is stale.** All 39 distinct receipt paths exist as blobs at
   `a3cc39f0` (`stale = 0`). The round-70/71 self-record does not cite a receipt that was never
   committed; the drift class here is *revision binding*, not missing files.
2. **Unbound is the dominant class: 55 of 77 citations
   (28 of 39 distinct paths) carry no revision in their first
   five lines.** No receipt carries its tip line after line 5, so the five-line window is not the
   cause — the line is absent. Examples: `measured/after/census-at-tip.out`,
   `measured/final/census.out`, `measured/before/pre-report-shortcut.out`,
   `w1/EX03ProvinceClaims/kill1-flipped.out`.
3. **Only 3 distinct receipts carry the strict `# tip=` form the frozen C2
   predicate accepts** — the three round-71 `measured/after/*-at-tip.out` receipts that the
   round-71 gate produced. A further 8 distinct receipts carry `tip=` with no
   `#` (the round-70 reconciler family and `round-71/measured/before/reconciler.out`). Under the
   frozen wording those 15 citations are `unbound`; the round-70 report calls the
   same line a header. **A rule that changed after a seat has scored is not the claim's rule** —
   this is reported as a wording disagreement, not as an edit to the freeze.
4. **Every receipt that does carry a revision is `shifted` from it.** 22 of
   22 bound citations (11 distinct) are
   shifted under the frozen 8-prefix list — **zero bind cleanly**; under the seat text's 5-prefix
   list 15 are shifted and 7 occurrences (3 distinct, all
   `4b284653`) are clean. The seven that flip are the round-71 report-tip receipts, which become
   shifted only because round 72's own freeze commit `090a0b25` touches
   `plans/round-72-claims.md` (Δfiles for `4b284653..a3cc39f0` = 19 files).
5. **Round-70 receipts certify bytes the round-71 instruments replaced.** For
   `7be07423..a3cc39f0` the delta touches 9 instrument inputs: `tools/pre-report-gate.py`,
   `tools/census-waiver-boundary.py`, `tools/round65-host-census.py`,
   `tools/round71-province-host-claims.py`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`,
   `corpus/knowledge/pre-report-gate.md`, `corpus/knowledge/cross-lane-scope.md`. A round-70
   receipt headed `tip=7be07423` is a reading of the round-70 instruments, not of the tip.
6. **Three distinct receipts (5 citations) name revisions that are not in the lane
   repo**: `tip=a7ae13ab621160957c8ac04053a87f393b727589` (`check-kill-probe-intact.out`,
   `check-kill-probe-gutted.out`) and `tip=af6e1c84d1460bae3f0070f03a5385f77eecb2b2`
   (`reconciler-record-only-dry.out`). `git cat-file -t` exits 128 for both objects and
   `merge-base --is-ancestor` exits 128. The round-70 lesson's L1 correction 3 records this class
   by hand ("scratch/fixture revisions that never existed in the lane repo"); the table above is
   its census.
7. **Boundary.** 12 citations in the same six sources point at older waves
   (`round-16/48/49/61/67/68/69`) through the round-70 section's capability table and two lesson
   sentences; they are outside the seat's `round-7*` population and are not in Table B. One
   citation is prose, not a path: `w1/out/` in `round-71.md` Mistake 2 describes a *fixture clone*,
   and mechanical resolution yields `.ufo/waves/round-71/w1/out`, which does not exist. One more is
   malformed: `.ufo/waves/round-16/17/live/receipt*.json` (two waves joined by `/`). A resolver
   must classify both as could-not-evaluate, not as a stale receipt.

## 5. (b) `.ufo/reports/round-71/kama.md`

Source: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-71/kama.md` (read-only, fleet repo).
**The report claims the tip is `7fb6cb4e31dc2f96e4815240a12bfe8da4d07e2e`** ("measured lane
commit … branch `master`, pushed: `ls-remote` equals the local tip, ahead=0").

23 cited paths resolve: 15 receipts (`W:` = `.ufo/waves/`), 3 directories, 3 evidence files, 2 scripts.

| receipt cited by the report | revision it names | relation to the reported tip `7fb6cb4e` |
|---|---|---|
| `W:round-71/measured/after/boundary-at-tip.out` | **yes** | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/after/pre-report-at-tip.out` | **yes** | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/after/province-claims-at-tip.out` | **yes** | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/before/census-shim-control.out` | **yes** | none | — | — |
| `W:round-71/measured/before/git-status.out` | **yes** | none | — | — |
| `W:round-71/measured/before/newest-closure.out` | **yes** | none | — | — |
| `W:round-71/measured/before/pre-report-shortcut.out` | **yes** | none | — | — |
| `W:round-71/measured/before/province-claims.out` | **yes** | none | — | — |
| `W:round-71/measured/before/receipt-audit.out` | **yes** | none | — | — |
| `W:round-71/measured/before/reconciler.out` | **yes** | `tip=` no `#` | f3ee44f47a9680437eeae63a8fa8807552a65119 | yes |
| `W:round-71/measured/before/wlc.out` | **yes** | none | — | — |
| `W:round-71/w1/EX01PreReportGate/selftest.out` | **yes** | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill1-flipped.out` | **yes** | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill2-wrongtag.out` | **yes** | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill3-rewrite.out` | **yes** | none | — | — |

Counts: **11 of 15 cited receipts carry no revision**; 3 name `4b284653`
(headers `# tip=`); 1 names `f3ee44f4` (header `tip=`, no `#`).

### Mismatches named (the class C2 removes)

1. **"Runs at the report tip" vs the receipt's own header.** The C1 work item says "The instrument
   runs at the report tip and its receipt is `…/measured/after/pre-report-at-tip.out`". That
   receipt's line 1 is `# tip=4b2846535fd918881ed3fc664aa46ef130a7d568`. `git rev-list --count
   4b284653..7fb6cb4e` → **3 commits** (1375f51c, 9458c3d7, 7fb6cb4e); to the measured tip
   `a3cc39f0` it is 6 commits. The report's own Before→after section names `4b284653` correctly,
   so the defect is the tip *claim*, not the measurement.
2. **"`9458c3d7` (final gate confirmation)" has no receipt naming `9458c3d7`.** `grep -rl 9458c3d7
   .ufo/waves/round-71/` → no file. The commit `9458c3d7` adds only
   `measured/after/pre-report-at-final.out`, whose header is `# tip=1375f51c…`; that receipt is
   cited nowhere in the report. A commit that carries the confirmation is not a measurement at
   that commit.
3. **"seven green receipts at `4b284653`" is eight.** `git show --stat 1375f51c` → 8 files changed,
   all `measured/after/*.out` (`boundary`, `newest-closure`, `pre-report-at-tip`, `province-claims`,
   `receipt-audit`, `reconciler-at-tip`, `sources-census`, `wlc`). The round-71 lesson's own final
   block lists eight.
4. **11 of 15 cited receipts are unbound**, so no check can relate them to the claimed
   tip at all — the round-71 report's tip statement is verifiable only for the three gate receipts
   it names, and those three disagree with it.

Adjacent record defects of the same class (not the report, but the round's self-record):
`corpus/lessons/round-71.md` says "the lane tip `9458c3d7` equals `ls-remote origin refs/heads/master`"
while the block that states it lands in `7fb6cb4e`, one commit later; and
`corpus/lessons/round-71-verifier-spotcheck.md` calls `4b284653` "two commits before the measured
tip `7fb6cb4e`" where `rev-list --count` gives three.

## 6. (c) Ignored-file proof on this host

Fixture: `mktemp -d -p $S`, `git init`, toplevel asserted equal to the fixture dir, `.gitignore`
holding `ignored.out`, one tracked file committed with
`git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit`, then an untracked and an
ignored file created under `.ufo/waves/round-72/`. Fixture removed by `trap … EXIT`.

```
fixture=/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon/fixture.vr2LK0
toplevel=/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon/fixture.vr2LK0
--- status --porcelain -uall
?? .ufo/waves/round-72/untracked.out
rc=0
--- status --porcelain -uall --ignored
?? .ufo/waves/round-72/untracked.out
!! .ufo/waves/round-72-ignored-only/ignored-only.out
!! .ufo/waves/round-72/ignored.out
rc=0
--- gate-arm form: status --porcelain -uall -- .ufo/waves/round-72
?? .ufo/waves/round-72/untracked.out
rc=0 files=1
--- gate-arm form with --ignored
?? .ufo/waves/round-72/untracked.out
!! .ufo/waves/round-72/ignored.out
rc=0 files=2
--- ignored-only wave dir: gate-arm form (status --porcelain -uall -- .ufo/waves/round-72-ignored-only)
<empty>
rc=0 files=0
--- ignored-only wave dir: with --ignored
!! .ufo/waves/round-72-ignored-only/ignored-only.out
rc=0 files=1
--- check-ignore verdict
.gitignore:1:ignored.out	.ufo/waves/round-72/ignored.out
rc=0
--- check-ignore on a non-ignored path
rc=1
```

What it proves: the ignored file is invisible to `git status --porcelain -uall` and to the base
gate's arm command, and visible only with `--ignored`. On a wave dir that holds one untracked and
one ignored file the base arm prints `files=1` (the untracked one) and `--ignored` prints
`files=2`; on a wave dir that holds **only** an ignored file the base arm prints `<empty>` and
`files=0` while `--ignored` prints the `!!` line and `files=1` — the vacuous green C1 names.
`git check-ignore -v` resolves the rule (`.gitignore:1:ignored.out`, exit 0) and exits 1 for a
non-ignored path.

## 6b. Freeze movement observed while this seat ran (recorded, not judged)

Three facts, from three commands, recorded because they are the same revision/time-binding class
this seat grades. No judgement is offered and no lane file was touched.

* The plan this seat read first (worktree copy, before its first clock reading
  `2026-11-03T22:45:47-03`) ended its C2 section at the "Control that skips the work" paragraph and
  went straight to `Non-goals`. The worktree copy now also carries a
  block headed **"Freeze amendment 2, 2026-11-03T22:50 -03, before any seat returned a score"**
  (`cited=0` becomes exit 2). So the plan's bytes changed under this seat.
* `git show a3cc39f0:plans/round-72-claims.md | sha256sum` → `39f4ddbc…`, which is exactly the
  hash `controls/freeze.txt` pins for that path — i.e. the frozen commit does **not** contain
  amendment 2; the worktree copy (`sha256sum` → `c656e66b…`, 9114 bytes) does.
* At observation time `2026-11-03T22:49:03-03`, `stat` reported the worktree file's mtime as
  `2026-11-03 22:42:21 -03`, eight minutes **before** the amendment's own declared time (22:50) and
  before this seat's read that did not contain the block. A file whose content changed after that
  read cannot have mtime 22:42:21 unless the mtime was preserved or restored; a declared time of
  22:50 cannot be read at 22:49. Either the writer restores mtimes or the declared time is not the
  write time. (Round 71 mined the adjacent "impossible correction date" class; this is the
  observation, not a verdict.)

None of the tables in this report depend on amendment 2: they grade citations and revisions, and
every path is read from the committed tree at `a3cc39f0`, not from the worktree.

## 7. Limits

* The population is what these six texts *cite by path*. A receipt discussed only by value
  (`HOST_CENSUS pass=22 …`) has no path and is not counted.
* Section boundaries are heading-based: `SCORECARD.md` `## Round 70` ends at `## Round 71`, so the
  capability table ("as of round 71") that sits between them is counted in the round-70 section,
  as it is written.
* "Exists at the tip" is a committed-blob check. `master` moved during the recon
  (`090a0b25` → `a3cc39f0`); one traversal at `090a0b25` was observed and the tables were
  recomputed at `a3cc39f0`. If the lane advances again the counts stand at the revision named
  here, not at a later one.
* The relative-path resolver deliberately over-reaches (finding 7); those results are named, not
  silently dropped, because C2's exit-2 rule is exactly about telling "not a receipt" from "stale".

## 8. Files and commands

Written under `.ufo/waves/round-72/w1/SCT01ReceiptRecon/`: `recon.md` (this file), `table.tsv`
(101 rows, every citation), `recon.json`, `report71-receipts.json`, `commands.out`,
`ignored-fixture.out`, `distinct-table.md`, `enumerate.py`, `report71.py`, `ignored-fixture.sh`,
`commands.sh`. Seat report: `.ufo/waves/round-72/w1/SCT01ReceiptRecon.md`.
