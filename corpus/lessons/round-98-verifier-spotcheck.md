# Round 98 — non-author verifier spot-check (integrator, @m_zfl)

author: hyaku closure (non-author integrator, @m_zfl)
Lane `kama`, round 98. Base `681c80a4e3c745c22559f74b2c2a1917bdc66fc6`; measured candidate
`160e22ddf31f368fe802d3512cd09d51adf59784`; lane tip before this file's commit
`649bb2e94501ee8aa2d4ceaeae52f7a1fb8d1ce9`. Report: `.ufo/reports/round-98/kama.md` (fleet repo).
I authored none of the round's files; the counters were not executed (Gate standard: the integrator
verifies committed evidence, it does not run a sibling's gate). Everything below was re-derived from
committed bytes with plain git/grep/awk reads.

## Step-1 conformance

| Check | Result |
|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-98/kama.md` → `kama-shokunin <kama@shokunin.local> 48e2f1e9…` (erratum) and `2ca6ea85…` (report) — pass |
| `SHONEN` heading, one line per box | `## SHONEN`, 4 lines, all `[~]` with evidence pointers; no `[x]`, no named non-author verifier — pass |
| Cited commits exist and are ancestors of `master` | `git -C kama-shokunin merge-base --is-ancestor <h> master` → YES for `34ad44e9`, `3185c257`, `160e22dd`, `3b71d098`, `380982b1`, `649bb2e9`, `681c80a4` — pass |
| Lane clean and pushed | `scripts/hyaku/jj-lane.sh state …` → `local=649bb2e9 remote=649bb2e9 ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty; `ls-remote origin refs/heads/master` = `649bb2e9…` — pass |
| Prompt carries the template contract | `.ufo/prompts/kama-round-98.md` carries §§1–5 of `templates/round-prompt.md` verbatim with substitutions, the five child-lane items (report path, commit-before-report ordering, `SHONEN` heading, commit-hash tie, write/push scope), the L2 floor (≥8, one batched call), and the hyaku addendum §6. `MISSION.md` §L2 concurrency holds no role pins, so there is no quoted map to conflict with — pass |
| Marker vs real report | Work performed + 5 landed-change commits each tied to a LOG entry + 3 before→after measurements + Sources & frontier + trends + `SHONEN` — real report, status `ok`, not a marker |
| Prefile ledger (Amendment 59) | `python3 scripts/hyaku/prefile-falsification.py --lane kama --round 98` → `PREFILE-FALSIFICATION: pass claims=3 rows=24 attack_seats=8 findings=0`, **exit 0**; 8 rows per claim; every attack-seat artifact read (CN01, CR01, CR02, MT01 matrix, RV01, RV02, SN01, RV03); 8 `falsifies-wording` rows all name `plans/round-98-amendment-1.md` — pass |

Conformance defects (status-neutral; routed below): the SCORECARD and LOG still carry the stale
"10 reported, 2 dead" wave reading that `w1-results.json` (12 results) and lesson M3 contradict; the
lesson's census sentence mislabels base numbers as HEAD; M3 sits outside `## Mistakes`; the
pre-report gate is red and the erratum enumerates five of its six failed arms.

## Per-claim re-check

**C1 — calibration (receipt evidence-verified; surfaces re-derived).** Committed receipt
`.ufo/waves/round-98/measured/c1.out` →
`SELF_ASSESS98 checks=20 mismatches=0 met=True rev=160e22ddf31f368fe802d3512cd09d51adf59784 skill_sha256=3021fc5d…`,
exit 0. Base control `controls/c1-base.out` →
`checks=20 mismatches=4 met=False rev=681c80a4… skill_sha256=863eb35d…`, exit 1. Amendment-1
control `controls/c1-amendment1-overcharge.out` → C1 `mismatches=1` and C3 `mismatches=1` on the
`+1` probe, exit 1. Plain re-derivations over committed bytes: `sha256sum SKILL.md` =
`3021fc5d7e8f…` and `wc -l` = 2484 (same at `160e22dd`); `grep -c '^### Round 97 correction'` = 1;
the heading says "five graded forgeries", SCORECARD's depth row says "five graded probe forgeries",
§Round 97's body says "five probe variants", the budget docstring says "new set = six cells" and
`cells=19`; the router counter's `MUTANTS` keys are exactly `flat6, undercharge, maxmeta,
nopreamble, overcharge` (5); `SOURCES.md` ids are unique (`uniq -d` prints nothing); the probe loop
carries exactly the four charged sites and no `steps[0] +=`, with the three preamble reads. Base has
the "three graded forgeries" heading, "four graded probe forgeries", and `cells=17`. **Verdict:
verifies → improved.**

**C2 — operability (receipt evidence-verified; independent matrix and arithmetic).** Committed
`measured/c2.out` tail: `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19
load_stable=1 budget=work probe=rev mutant=none slow_files=72 runs=2 probe_sha256=40ab387e…
base_sha256=27065a5c… rev=160e22dd… w03_seconds=85.9 load1_nat=141.68 burners=64`, exit 0.
`controls/c2-legacy-mutants.out`: `cells=17 cells_ok=17 mutant=overcharge … survived=1 caught=0`.
`controls/c2-new-mutants.out`: real probe `cells=6 cells_ok=6 survived=1`; flat6 → W15-700k-nd4
(`cells_ok=5`), undercharge → W14-900k-nd1 (`3`), maxmeta → W16-maxmeta (`5`), nopreamble →
W17-833333-nd1 (`5`), overcharge → W18-800k-nd1 and W19-520k-nd4 (`4` each, both red), every line
`cell_ok=0 caught=1`. Independent attack evidence MT01 `matrix_final.json`: `E_plus1-legacy` 13/13
survived, `E_plus1-r97set` 17/17 survived, `E_plus1-new-W18/W19` caught with red
`[W18-800k-nd1, W19-520k-nd4]`; `D_minus1-r97set` red at W14/W17; `F_plus2` red at W11 on 13 cells
and W18/W19 on 6. Arithmetic: 800 000 at nd=1 is `4 + 6x800 000 = 4 800 004 ≤ 5 000 000` (invalid)
while `+1` is `4 + 7x800 000 = 5 600 004` (`-`); 520 000 at nd=4 is `4 + 9x520 000 = 4 680 004`
while `+1` is `4 + 10x520 000 = 5 200 004`. The probe is byte-identical at base and HEAD
(`sha256sum tools/kama-probe.sh` = `40ab387e…`). **Verdict: verifies → improved.**

**C3 — depth (re-measured with plain counts; receipt evidence-verified).** Committed
`measured/c3.out` → `DEPTH_BOUNDARY98 rows=8 checks=13 mismatches=0 met=True rev=160e22dd…`, exit 0;
base `controls/c3-base.out` → `rows=6 checks=13 mismatches=4 met=False rev=681c80a4…`, exit 1.
Plain count over the section table: 6 rows at `681c80a4`, 8 at HEAD. Every row recomputed from
`MAX_STEPS = 5,000,000`: 833,332x6+4 = 4,999,996 and 555,555x9+4 = 4,999,999 are `invalid`;
833,333x6+4 = 5,000,002, 900,000x6+4 = 5,400,004, 700,000x9+4 = 6,300,004 and 555,556x9+4 =
5,000,008 are `-`; the two new rows are 800,000/nd=1 = 4,800,004 and 520,000/nd=4 = 4,680,004, both
`invalid`. The section cites S620/S621/S622 and carries the KV-free/`nd > 4` caveat. S622's header
struct was re-opened live (below). **Verdict: verifies → improved.**

**Axis harm check.** `git diff 681c80a4 649bb2e9 -- SCORECARD.md`: depth 7→7, calibration 7→7,
operability 8→8, freshness 8→8, coverage 9→9, adjacency 7→7; two capability rows enter
(`overcharge-forgery-grading`, `heading-count-grading`) with demonstrated evidence pointers. No
score decreased, no retired axis touched.

### Per-axis verdicts

| Axis | Verdict |
|---|---|
| calibration | improved (C1 verified; the 20 named surfaces now match, base 4 mismatches) |
| operability | improved (C2 verified; the 19-cell set catches the +1/header probe the 17-cell set survives) |
| depth | improved (C3 verified; 6→8 boundary rows, all recomputed from MAX_STEPS) |
| coverage | unchanged |
| freshness | unchanged |
| adjacency | unchanged |

## Discernment spot-check (LEARNING.md)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S622 GGUF spec `gguf_header_t` @ `57e2c2ca` | admit (A, spec, mined) | `https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca…/docs/gguf.md` re-opened 2026-11-08: HTTP 200, 43 175 B, sha256 `1dead27b…`; line 277 `struct gguf_header_t {` | agree | The struct at lines 277-300 carries exactly four fields — `magic`, `version`, `tensor_count`, `metadata_kv_count` — so the four preamble steps are spec-grounded; quote, line and digest match the row and the freeze control |
| S623 GGUF naming convention @ same commit | reject (C lead) | Same URL and digest; line 23: "It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames." | agree | Filename provenance only; it grounds no header step cost, and the stated flip (header field order/widths) is unmet |

Row-count cross-checks: HEAD `363` rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30), base
`361` (A 344, B 11, C 6; mined 324, queued 8, rejected 29), each with the frozen census awks;
`git diff 681c80a4 649bb2e9 -- corpus/SOURCES.md` is exactly two inserted rows (S622, S623).
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → `kama ok`, exit 0,
with the standing W04 duplicate-URL warnings (S622/S623 share S620's URL, as disclosed) and the
standing W01 tier-C warning.

## Trend verdicts

- **expansion: unchanged** — one spec row (S622) grounds a term the lane already prices; no new
  admitted `knowledge/` entry (`git diff --stat 681c80a4..HEAD -- corpus/knowledge` is empty) and no
  new governed surface. No coverage regression.
- **quality: improved** — each claim replaces a weaker instrument or self-description and carries a
  red-before control: C1 base 4 mismatches to 0, C2's 17-cell survival to six caught cells with all
  17 old cells still green, C3's six rows to eight with the overcharge-window rows recomputed. No
  graded entry was found false and left unmarked; the stale wave-seat prose is bookkeeping, routed.
- **discernment: improved** — the wave's own eight `falsifies-wording` rows were real and each was
  narrowed by amendment 1 before measurement; the non-author spot-check agrees 2/2 with the gate
  (one admit, one reject).

## Routed defects for round 99

1. **Stale wave-seat count in two files.** `SCORECARD.md:6431` and `LOG.md:4040` say "10 reported,
   2 dead (`RV03Intent-2`, `EX02BudgetControl-2`)"; `w1-results.json` carries 12 seat results
   (including `RV03Intent` and `EX02BudgetControl`) and lesson M3 records that both settled. Append
   a correction in round 99 naming both lines (append-only files get new entries, never rewrites).
2. **Seat-accounting prose is inconsistent.** `LOG.md:4044` names "SB01-equivalent prose carried by
   the lesson" where `EX02BudgetControl` belongs and counts five building seats over four names;
   `SCORECARD.md:6433` lists six attack seats without `RV03Intent`; the report lists `CN01` among
   its seven attack seats. Per `w1-results.json` the split is 7 attack (RV01/RV02/CR01/CR02/MT01/
   SN01/RV03) + 5 non-attack (SC01/SC02/EX01/EX02/CN01); correct the accounting next round.
3. **Lesson census sentence mislabels HEAD.** `corpus/lessons/round-98.md:28` says "tiers measured
   with the census at HEAD (361 rows: A 344, B 11, C 6; mined 324, queued 8, rejected 29)"; HEAD is
   363 rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30) — the quoted numbers are base's.
   Append the correction in round 99's lesson.
4. **M3 placement.** M3 sits after `## Spot-check`, outside `## Mistakes`; fold it into the
   `## Mistakes` record next round (`CORPUS.md` lesson-shape rule).
5. **M2's fix lacks a committed red-before receipt** (the `cells=16` run was overwritten before
   commit); the counter-level `n != len(selected)` fix is still routed. Land the counter fix and
   commit the observed failure output so the fix is shown able to fail.
6. **Pre-report gate remains red and is under-enumerated.** `PRE_REPORT round=98 arms=14 failed=6
   uncommitted=1` (exit 1); the erratum names five failed arms and omits `round-clean` (exit 0, FAIL
   on the same untracked receipt). Disclose the sixth arm and carry the standing reds
   (`selfdesc`, `newest-closure`, `round75-instruments` with `bad_rows=19` and L0 r87/r89,
   `round78-instruments` from the host Ollama listener) as before.
7. **Carried unchanged:** slow `/props` verdict still decides (r94 SC02 F4), the pass-level
   wall-clock wrapper (SC01), the ctime memo shape (unobservable), the C1 checks 13–14
   receipt-needle limit, and the frozen counter's `--control` count check.

**Note for the operator:** the four `SHONEN` boxes remain `[~]` (author-asserted). On the evidence
re-opened here they look checkable by a non-author, but promotion is operator-owned and no box was
marked by this review.
