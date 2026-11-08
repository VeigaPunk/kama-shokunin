# SC01SiblingScan — read-only fleet reconnaissance for kama round 97

Seat: `SC01SiblingScan`, wave 1, leaf member (no dispatch). Lane `kama-shokunin` at `e057166e`
(HEAD). Work is read-only: no lane file was edited, no mutating git/jj command was run.

**Question.** Two defect classes this round claims to close:

- **(a)** a counter that requires the exact false string it was written to catch (the round-96
  kama C3 shape: a check that grades the presence/absence of a fixed phrase instead of the
  binding property — `tools/round96-disclosure-audit.py:51` at base `40763bd2` required the exact
  string `"6 steps per tensor header"`);
- **(b)** a claim sentence wider than the property its counter enforces (round-96 kama C3's stated
  sentence was "every disclosure the lane repeats matches the bytes beside it").

## Method (real commands, read-only)

```
ls -d /home/vgpnk/Projects/shokunin/*-shokunin
for L in */; do ls $L/tools/*.py | wc -l; done                      # lane tool inventories
grep -rnE '"[^"]{8,}" (not )?in [a-z_]+' <lane>/tools --include=*.py   # literal-presence sweep
grep -rniE "overstate|wider than|broader than|counter does not|presence of the exact" \
     */corpus/lessons/round-9*-verifier-spotcheck.md
grep -rniE "overstate|grades literal|literal presence" .ufo/reports/round-9*/
git -C <lane> show HEAD:<path> | grep -n ...                        # per-row presence at each lane tip
git -C <lane> ls-files <path>                                       # trackedness
```

Scope read: all 21 lanes' `tools/`, `plans/round-*-claims.md`, `corpus/lessons/round-9*-verifier-spotcheck.md`,
and the fleet root `.ufo/reports/round-9*/`. Every row below was re-confirmed at the owning lane's
`HEAD` with `git show HEAD:<path>`; quoted phrases are the shortest span that shows the class.

## PRESENT rows (12)

| # | lane | file:line | class | phrase that shows the class | presence at lane HEAD |
|---|---|---|---|---|---|
| A1 | tsukuroi | `tools/check-r96-calibration.py:120-123` | a | `if "largest in-bound" in text:` / `if "boundary member" not in text:` — F3 grades the two r95 tool docstrings by the presence of two exact phrases, not by whether the scope sentence is true | present (`git show HEAD:…` → lines 120-123) |
| A2 | tsukuroi | `tools/check-r96-calibration.py:129-131` | a | `if readme is None or "r94 family roster" not in readme:` / `if "before instrument has no in-bound" in readme:` — README scoping graded by phrase | present (lines 129-131) |
| A3 | tsukuroi | `tools/check-r73-routed-r74.py:83-89` | a | `required = ["13","14"]` … `if not ("12" in body or "twelfth" in body.lower()):` — the LOG.md correction block is graded by bare substring hits (`"12"` matches any `12`), so any body containing those digits passes | present (lines 83-89) |
| A4 | kaidoku | `tools/round-35/c2-calibration-counter.py:84` | a | `if "AAdjacencyCite" not in lesson or "31/32" not in lesson:` — the "31/32 reports" figure the counter was written to catch is graded as a literal in the lesson (the seat-accounting totals beside it *are* recomputed, `:109-113`) | present (`git show HEAD:…` → line 84) |
| A5 | kotodama | `tools/check-craft-exercise.py:254` | a | `if "no universal" not in note and "not asserted" not in note:` — "the constraint bars universal one-symbol-one-domain claims" is decided by two literal words in the note | present (line 254) |
| A6 | tsukuroi | `tools/check-root-dac-correction.py:161` | a | `("nonexhaustive", "non-exhaustive" in claims or "not the only" in claims)` — the scope limit is graded by one of two literal phrasings | present (line 161) |
| B1 | tsukuroi | `tools/check-r96-calibration.py:9-12` (docstring) vs `:110-113` (code) | b | docstring: "SCORECARD.md's 'Round 96' section binds the r95 C2 void clause to an empty `git diff` over that path"; code: `for t in ("void", "git diff", "check-registry-coverage.py")` — three tokens in the section, no `git diff` anywhere | both present at HEAD |
| B2 | tsukuroi | `tools/check-r96-calibration.py:6-8` (docstring) vs `:83-85` (code) | b | docstring: "cites round-95.md, M1 and a development run (the r95 lesson's captured-by `none` fix)"; code: `missing = [t for t in ("round-95.md","M1","development run") if t not in block]` — `captured-by`/`none` is never read anywhere in the file (`grep -n "captured-by"` → docstring only) | both present at HEAD |
| B3 | kaidoku | `SKILL.md:810` | b | "binds every pin to `git cat-file blob <revision>:<path>`" — but `tools/round-97/stop-boundary-repair-battery-v7.py` binds only three pins at the revision (`:204-205` counter/verdict/repair) and hashes the two imported pins from the **live worktree** (`:515-517`, checked at `:224-230` against live `pins`, not `pins_at_rev`); `corpus/QUALITY.md:339` (Row 197) records the gap "corrected … without rewriting the block" | present (SKILL.md still says it at HEAD) |
| B4 | kaidoku | `plans/round-99-claims.md:16` (+ `:18-19`) | b | heading "R99-C1 — calibration: self-assessment mismatches 17 → 0" over "the SKILL.md gate registry rows"; the counter's A4 atom grades row **presence and shape** (`tools/round-99/self-assessment-audit.py:20-29`), and the lane's own successor admits it: "The round-99 counter checked presence and shape, not truth" (`plans/round-100-claims.md:50-51`) | present at HEAD |
| B5 | mado | fleet `.ufo/reports/round-97/mado.md:208` | b | "the r96 spot-check's D1–D13 are closed by this round's record fixes" — the lane's own closure judge: "The Notes' 'the r96 spot-check's D1–D13 are closed' overstates. Its own parenthetical omits D7 and D9, and neither is closed" (`corpus/lessons/round-97-verifier-spotcheck.md:144-146`; D7 rationale still unchanged at `.ufo/waves/round-96/claims-declaration-r96.md:114-115`) | report sentence still at fleet HEAD; the lane closed D7/D9 append-only in r98 (`.ufo/reports/round-98/mado.md:58-59`), i.e. the over-wide r97 sentence stands unrewritten |
| B6 | kumitate | fleet `.ufo/reports/round-95/kumitate.md:65` | b | "K3 harm battery CLEAN at M and final" — the committed receipt at the same revision prints `PROXY: DRIFT (A_WAVE_DRIFT …; C2 …; C2_total …)` and `exit=1` (`.ufo/waves/round-95/close/battery-M.txt`, `git show HEAD:` confirmed) | report sentence still at fleet HEAD; re-flagged at `corpus/lessons/round-96-verifier-spotcheck.md:56` |

Rows are counted only where the defect is **present** at the owning HEAD. Two sibling instances of
the same classes that are already closed in-lane and therefore excluded: revenger's "three C2 stubs
that pass the frozen probe" (`.ufo/reports/round-91/revenger.md:61`) is corrected in
`revenger-shokunin/corpus/lessons/round-92.md:123` ("passed the frozen probe, not three (stubA
failed it)") — the receipt `probe-stubA.log` does print `CAP_MESSAGE_TREE=fail`; and kake's
"every finding is routed" (`kake-shokunin/corpus/lessons/round-91-verifier-spotcheck.md:169`) is
quoted only inside the verdict that rejects it.

## Where kama's round-97 instruments sit against this set

Checked by reading the three frozen counters and running two of them read-only
(`python3 tools/round97-self-assessment-audit.py --repo . --rev …` →
`SELF_ASSESS97 checks=14 mismatches=9 met=False` at base `40763bd2`, `checks=14 mismatches=0 met=True`
at HEAD; `tools/round97-depth-boundary-audit.py` → `DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False`
at base, `rows=6 checks=8 mismatches=0 met=True` at HEAD):

- **Depth (C3) — ahead.** `tools/round97-depth-boundary-audit.py:103` recomputes
  `want_steps = PREAMBLE + t * (5 + nd)` from the probe's `MAX_STEPS` and re-derives the `<=`/`>`
  comparison and the verdict, requiring six named `(T, nd)` pairs (`:36-37`). No sibling instrument
  I read grades a step-budget table at all; the nearest siblings grade literal phrases (A1-A6).
- **Calibration (C1) — mixed.** Checks 1-6 and 8 recompute (`sha256` of SKILL.md vs the declared
  digest, `len(skill.splitlines())`, `## ` section count, the adjacency digest and pipe count, the
  capability pointer's `cat-file -e` + `merge-base --is-ancestor` + evidence-path existence, and the
  per-rank ceilings `(MAX_STEPS - 4) // (5 + nd)`), but check 7 is still phrase-graded:
  `if "5 + nd" not in probe or "6 steps per tensor header" in probe:` (`:143`) — the same
  literal-presence shape as A1-A6, applied to the probe's comment rather than its arithmetic.
  Checks 13-14 are likewise literal (`:193-197`: the needles
  `"DEPTH_AUDIT checks=14 mismatches=0"` / `"DISCLOSURE_AUDIT checks=6 mismatches=0"` must appear in
  the receipt file and in SCORECARD).
- **Operability (C2) — the strongest sibling pattern.** `tools/round97-router-budget.py` grades
  behaviour against a fixture oracle and carries mutation controls (`--control --cells legacy|new
  `--expect survived|caught`, `:573-579`), which is the same depth as the best sibling batteries;
  it is not deeper, because kaidoku's `tools/round-100/registry-selftest-truth.py` *executes* each
  registry row's documented self-test and compares the printed count (a claim graded by running the
  claim), which kama's C1 does not do.
- Sibling counter for calibration depth: `tsukuroi-shokunin/tools/check-self-assessment.py`
  recomputes observed values (K08 line count, K09 table lines, K13 census selftest case count) the
  same way kama's C1 recomputes — i.e. kama is not ahead of tsukuroi on recomputation.

**Conclusion (one line): kama's round-97 instruments are level with the strongest siblings on these
two defect classes — ahead of them on depth (C3's counter is the only one in the fleet that
recomputes a step-budget table from `MAX_STEPS`), level on calibration because C1 keeps two
literal-presence checks (`:143`, `:186-196`) of the very class it claims to close, and behind
kaidoku r100 on calibration depth, whose counter executes the claim instead of grading its prose.**

## Unresolved / not covered

- I did not run any sibling counter; all sibling rows are static reads of committed bytes at each
  lane's HEAD, so I cannot say whether any of them is currently red or green.
- Fleet reports under `.ufo/reports/round-100..108/` were not swept for the same two classes; the
  seat scope named `round-9*/`.
- `kotodama`, `mori`, `souji`, `tameshi`, `chousa`, `mado` counters mostly grade tool **stdout**
  strings (`"attributed=66" in text`, `"CONFIRMED W04" in text`); those are machine outputs rather
  than prose claims and are not the round-96 kama C3 class, so they are not counted above.
- kaidoku's own `tools/round-99/self-assessment-audit.py` grades registry-row shape only, and the
  lane's r100 claims file says so; that pair is row B4, not two rows.
- No fixture repo, clone or work tree was created; scratch dir `/fast/scratch/hyaku/kama-r97/SC01SiblingScan/`
  was created empty and removed before this report was written.
