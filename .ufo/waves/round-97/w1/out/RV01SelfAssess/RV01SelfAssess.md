# RV01SelfAssess — C1 calibration instrument attack (kama round 97, wave 1)

Seat: RV01SelfAssess, leaf. Lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Scratch: `/fast/scratch/hyaku/kama-r97/RV01SelfAssess/` (clone + per-variant commits; cleaned after receipts copied).
No tracked lane file was edited; no lane git/jj mutation was run. Every fixture commit was made in a
`git clone --shared` under scratch after asserting `git rev-parse --show-toplevel` equalled the clone.

## 0. What was run

- Base: `python3 tools/round97-self-assessment-audit.py --repo <lane> --rev 40763bd2`
  → `SELF_ASSESS97 checks=14 mismatches=9 met=False`, exit 1.
- Freeze: `--rev 9e605d41` → `SELF_ASSESS97 checks=14 mismatches=0 met=True`, exit 0.
- Current master: `--rev master` → `SELF_ASSESS97 checks=14 mismatches=0 met=True`, exit 0.
- The lane moved during this review: master was `9e605d41` at first read, then `e057166e`
  (round-97 amendment 1: C2 host-speed slow-files 72). The C1 counter bytes are identical across
  both: `git diff --stat 9e605d41 e057166e -- tools/round97-self-assessment-audit.py` is empty.
  The predicate is green at both revisions.
- Instrumented copy of the same counter (only a fail-list print added) names the failing checks:
  base `fails=[1, 2, 3, 6, 7, 8, 9, 10, 11]`; M1 `fails=[]`.
- 19 mutation variants were committed one per clone revision and graded with the frozen counter;
  the matrix is in §3. The clone's HEAD was reset to `e057166e` between variants.

Receipts copied to this out dir: `predicate-runs.txt`, `variants.log`, `variants2.log`,
`variants3.log`, `variants4.log`, `audit-instrumented.py`.

## 1. Bottom line

The 14-check counter does exactly what its docstring says on the 14 named surfaces: the do-nothing
control is red at base (9 mismatches), M1 is green, and the counter bytes are frozen (K1). Checks
1, 2, 3, 6, 7, 8, 9, 10 and 11 discriminate base from M1; checks 4, 5, 12, 13 and 14 are green at
both revisions for the same reason (see §2.9 for the K3 consequence).

It does **not** grade the C1 header sentence "the lane's graded self-assessments match the repo".
The instrument grades 14 named occurrences and mostly by literal presence, not by
non-contradiction. Three concrete false-self-assessment shapes pass (§2.2–§2.4), and the live
lane already contains a repeated false count that C1 (and C3) report green: the lane says
"three graded probe forgeries" / "adds three cells" / "three probe variants … W14, W15 and W16"
while the frozen C2 population is **four** new cells (W14–W17) and `CELLS = 17` (§2.1).

## 2. Findings by severity

### 2.1 BLOCKER — a live false self-assessment passes C1: "three" vs the four graded C2 cells

The lane repeats a count of three graded probe forgeries; the counter, the frozen plan's cell list,
the mutant table and the freeze-time control all say four.

Evidence:
- `plans/round-97-claims.md:83` "This round's four graded mutants are the per-header removal
  (`undercharge`), a constant 6 steps/header (`flat6`), the 100 MiB cap (`maxmeta`) and a
  preamble-drop (`nopreamble`, this round's own shape)".
- `plans/round-97-claims.md:86` "**After.** Four cells past the old set: **W14-900k-nd1** … **W15-700k-nd4**
  … **W16-maxmeta** … **W17-833333-nd1**".
- `plans/round-97-claims.md:94` "**Cells (17, frozen in the counter's docstring):** the 13 round-96
  cells unchanged plus W14, W15, W16, W17".
- `tools/round97-router-budget.py:13` "Round 97 adds **three** cells past that:" — followed by a
  four-item list at lines 15 (W14), 18 (W15), 21 (W16), 24 (W17). The docstring is internally
  contradictory.
- `tools/round97-router-budget.py:142` `CELLS = 17`; `:146` `NEW_CELLS = {"W14-900k-nd1",
  "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1"}`; `:163-176` `MUTANTS` has four names; `:574-575`
  `--mutant` choices include `nopreamble`.
- `.ufo/waves/round-97/controls/c2-new-mutants.out` has five `ROUTER_BUDGET97_CONTROL` lines with
  `cells=4`: `mutant=none … survived=1`, and `flat6`, `undercharge`, `maxmeta`, `nopreamble` each
  `caught=1`.
- `SCORECARD.md:17` "plus **the three graded probe forgeries**".
- `SKILL.md:2463-2468` "**three** probe variants survive all 13 of its cells … The round-97 counter
  `tools/round97-router-budget.py` grades each with W14, W15 and W16 respectively" — W17 is omitted.
- C1 at these bytes: `SELF_ASSESS97 checks=14 mismatches=0 met=True`, exit 0.

Mutation receipts (C1 stays green because no check reads the count):
- `D4`: `SCORECARD.md:17` "three graded probe forgeries" → "seven" → C1 `checks=14 mismatches=0`;
  C3 `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0`.
- `D6b`: `SKILL.md:2463` "three probe variants" → "nine", with the depth-row digest/lines/sections
  mechanically synced to the patched file → C1 `checks=14 mismatches=0`; C3 `checks=8 mismatches=0`.

Impact: the sentence "the lane's graded self-assessments match the repo" is false in the live lane,
and C1 is green. This is the round-96 CR02 B2–B5 class (a repeated disclosure the counter is green
on) reproduced in a count cell. The C1 disclosed limit ("other SCORECARD rows … are not graded")
does not cover this: the count is in the depth row, whose checks 1–3 grade only digest, line count
and section count. Note the plan itself is inconsistent — `plans/round-97-claims.md:77` says
"the three new cells, one per mutant" while lines 83/86/94 say four/17 — and the wave brief says
"16 cells"; the authoritative counter and its freeze control say four new cells / 17 total.

### 2.2 HIGH — shape (a): a probe comment naming 1,000,000 (or a near-miss constant-6) passes checks 7–8

The live probe already names 1,000,000 as a non-binding figure:
`tools/kama-probe.sh:580-581` "The old 1 000 000 sentence (the MAX_TENSORS constant) was never the
binding ceiling"; C1 is green at M1. The audit does not read the qualifier, so flipping it to a
false binding claim still passes:

- `A1`: `tools/kama-probe.sh:580-581` → "The binding ceiling is 1 000 000 tensor headers (the
  MAX_TENSORS constant)" (the probe's own arithmetic: 900 000 nd=1 headers cost 5 400 004 steps
  > `MAX_STEPS = 5_000_000`, so the sentence is false) → C1 `checks=14 mismatches=0`, exit 0.
- `A2`: the ceiling list at `tools/kama-probe.sh:577` → "1,000,000 at nd=1" and the true "833,332"
  moved to a later comment line → C1 `checks=14 mismatches=0`. Check 8
  (`tools/round97-self-assessment-audit.py:149-153`) requires only that each formatted ceiling
  occur somewhere in the file; a contradictory statement beside it is invisible.
- `A3`: the honest sentence at `tools/kama-probe.sh:579` "6 steps/header is only the nd=1 case and
  misstates every rank-2+ file" → "6 steps per header is the binding rule at every rank" → C1
  `checks=14 mismatches=0`. Check 7 (`tools/round97-self-assessment-audit.py:143`) rejects only the
  exact string `6 steps per tensor header`; the round-96 defect survives a one-word paraphrase.
- False-rejection mirror `A4`: an honest refutation that quotes the old sentence verbatim
  ("the round-96 comment said \"6 steps per tensor header\" and that was false") → C1
  `checks=14 mismatches=1 met=False`, exit 1, check 7. The counter cannot distinguish asserting
  from quoting-to-refute.

Verdict for (a): **accepted** by checks 7 and 8; the false 1,000,000/binding statement and the
near-miss constant-6 statement both pass.

### 2.3 HIGH — shape (b): counter docstrings are ungraded; a different budget number passes

- `B1`: `tools/round97-router-budget.py` docstring `MAX_STEPS` (5 000 000) → (10 000 000) and
  `MAX_META` (512 MiB) → (1 GiB); `tools/round97-depth-boundary-audit.py` docstring
  `steps = 4 + T * (5 + nd)` → `4 + T * (6 + nd)`, while `tools/kama-probe.sh` still says
  `MAX_STEPS = 5_000_000`, `MAX_META = 512 * 1024 ** 2` and `5 + nd` → C1
  `checks=14 mismatches=0 met=True`, exit 0.
- No C1 check opens either round-97 counter. Check 12 (`tools/round97-self-assessment-audit.py:184-190`)
  only requires `tools/round96-router-budget.py` at `f175a902` to equal the graded revision's bytes.
- The live three-vs-four contradiction in `tools/round97-router-budget.py:13` is the same gap: the
  C2 counter's own docstring disagrees with its cell table and its freeze control, and C1 is green.

Verdict for (b): **accepted**; the instrument has no check for the counters' docstrings, so a
docstring that disagrees with the probe's budget on any number passes.

### 2.4 MEDIUM — shape (c): the capability pointer accepts any resolvable ancestor with the first evidence path

The check (`tools/round97-self-assessment-audit.py:126-136`) requires only: the first hex run in the
row resolves, is an ancestor of the graded revision, and the first backticked `.ufo/waves/...` path
exists at that pointer. `SCORECARD.md:6320` is the graded row; it says "receipts at `a9b5014c`
(measured against `c810f51e`): `.ufo/waves/round-95/measured/c1-m1b.out`,
`.ufo/waves/round-95/controls/c1-base.out`".

- `C1`: pointer `a9b5014c` → `40763bd2` (round-96 verifier spot-check; `40763bd2` is a descendant of
  `a9b5014c`, and `c1-m1b.out` exists at it) → C1 `checks=14 mismatches=0`. The row still says
  "measured against `c810f51e`"; the audit never reads the second hex.
- `C2`: pointer `40763bd2` plus the first evidence path replaced by `.ufo/waves/round-96/measured/c2.out`
  (unrelated to the capability) → C1 `checks=14 mismatches=0`.
- `C3b`: the second evidence path `controls/c1-base.out` replaced by
  `controls/does-not-exist.out` → C1 `checks=14 mismatches=0`; only the first `.ufo/waves/...` path is
  read (`ev = re.search(r"`(\.ufo/waves/[^`]+)`", cap)`).
- Equality loophole: the code calls `git merge-base --is-ancestor <ptr> <rev>`
  (`tools/round97-self-assessment-audit.py:134`); `git merge-base --is-ancestor e057166e e057166e`
  returns 0, so a pointer equal to the graded revision passes even though the code comment at line
  129 says "precedes the tip".
- The first-working commits: `tools/round95-router-budget.py` was added at `c798e831`, the receipt at
  `a9b5014c`; `40763bd2` is a later commit. The audit does not know or check "the commit the
  capability first worked in".

Verdict for (c): **accepted**; any ancestor with the first evidence path passes, and neither the
first-working commit nor the measured-against commit nor the second evidence path is graded.

### 2.5 MEDIUM — check 10 takes the last duplicate S621 row (last-wins)

`sources_rows` (`tools/round97-self-assessment-audit.py:63-66`) stores `rows[m.group(1)]` per line,
so a later duplicate overwrites the canonical row. `E3`: the canonical `corpus/SOURCES.md:376` S621
teaches cell is changed to "the header cost is a constant 6 read/seek steps at every rank" and the
original correct row is appended after it → C1 `checks=14 mismatches=0`. A false canonical row
passes with a decoy duplicate; no duplicate-ID check exists.

### 2.6 MEDIUM — checks 4–5 accept a deleted adjacency file declared as the empty digest

`cross = show(a.repo, rev, "corpus/knowledge/cross-lane-scope.md") or ""`
(`tools/round97-self-assessment-audit.py:115`) has no existence check. `E1b`: delete the file,
declare `sha256` of the empty string
(`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`), `(0 lines)` and `→ 0` pipes →
C1 `checks=14 mismatches=0`. Check 6 does test `has_path`; checks 4–5 do not.

### 2.7 MEDIUM — checks 1–3 grade metadata, not the truth of the SKILL prose

`D6` (SKILL "three" → "nine", digest not updated) → C1 `checks=14 mismatches=1 met=False`, check 1.
`D6b` (same edit, with the declared depth-row sha256/lines/sections recomputed from the patched file)
→ C1 `checks=14 mismatches=0`. The digest binds the file's bytes, not the truth of a sentence inside
it; any semantic falsehood in SKILL is green once the author updates the mechanical cells. `D7` and
`D7b` show the same for a false ceiling.

### 2.8 MEDIUM — check 9 is whole-file literal presence, not the step-cost section

The docstring says "SKILL.md's step-cost section carries all five ceilings"
(`tools/round97-self-assessment-audit.py:25`), but the code checks `"S620" in skill`, `"S621" in
skill` and each formatted ceiling anywhere in the file (`:160-162`). `D7b`: the round-96 step-cost
table's nd=2 row is changed from `| 2 | 7 | 714,285 |` (`SKILL.md:2437`) to `714,286`, and the true
string "714,285" is appended at the end of §Round 97 as a decoy; the depth-row digest/lines are
synced → C1 `checks=14 mismatches=0`, C3 `checks=8 mismatches=0`. A false ceiling in the table
passes both counters.

### 2.9 LOW — K3 read per-check is fired by the instrument's own base control

Plan K3: "a check is green at base and green at M1 for the same reason (no discriminator)." The
instrumented base run is `fails=[1,2,3,6,7,8,9,10,11]`, so checks 4, 5, 12, 13 and 14 are green at
base and at M1 for the same reason:
- 4–5: the adjacency row's digest and pipe count were already correct at base;
- 12: `tools/round96-router-budget.py` at base already equals `f175a902` (sha256
  `6c5579a999fad82c1e8313d2442dc635b6a5499cd05d3f10b1b57784c3fcd7b8` both sides) and SCORECARD
  already names `f175a902`;
- 13–14: both round-96 receipt needles were already in the base SCORECARD (grep count 2 each) and in
  the committed receipts.

Read literally, K3 says a claim with any such check is void; the do-nothing paragraph says only a
green base run is void (the base run is red, 9 mismatches). This is a plan-level contradiction to
escalate, not a counter byte change.

### 2.10 LOW — checks 13–14 grade one needle per receipt, not the quoted numbers

`D2`: `SCORECARD.md:7` "(`DEPTH_AUDIT checks=14 mismatches=0`, base `mismatches=14`)" →
`base `mismatches=13`` → C1 `checks=14 mismatches=0`. The receipt really says
`DEPTH_AUDIT checks=14 mismatches=14 met=False` (`.ufo/waves/round-96/controls/c2-base.out`), and
`c3-base.out` says `mismatches=3`; the audit checks only the `checks=14 mismatches=0` needle and its
presence in SCORECARD. `SCORECARD.md:6342-6343` repeat the base numbers; ungraded. The round-96 C1
base control quoted at `SCORECARD.md:7` (`ROUTER_BUDGET96 cells=13 mismatches=1
positive_mismatches=1` with W11-700k red) is not read at all; the actual control file matches the
quote (`ROUTER_BUDGET96 cells=13 mismatches=1 positive_mismatches=1 … W11-700k ok=0`), so this is a
coverage gap, not a live falsehood.

### 2.11 LOW — checks 7–8 enforce literal strings on the probe, not the disclosure

Check 8 grades nd=1..4 only (`for nd in (1, 2, 3, 4)` at `tools/round97-self-assessment-audit.py:149`);
check 9 grades nd=0..4. The probe comment at `tools/kama-probe.sh:575-582` states nd=1..4, no nd=0
ceiling. If the plan's "every per-rank ceiling in the probe comment" means the five ranks SKILL
carries, the probe surface is one ceiling short; the counter does not test it. (`MAX_STEPS` is
`5_000_000` and `PREAMBLE = 4`; the nd=0 ceiling is 999,999.)

### 2.12 LOW — the C1 output/receipt is not revision-bound

- `--rev` is an input, but the printed line carries only `checks`, `mismatches` and `met`
  (`tools/round97-self-assessment-audit.py:203`): no `rev=`, no repo, no digest. The lane's current
  `.ufo/waves/round-97/measured/c1.out` (untracked at review time) is exactly
  `SELF_ASSESS97 checks=14 mismatches=0 met=True` / `c1_exit=0` — no revision. Compare C2's control
  lines, which print `rev=<sha> probe_sha256=<sha>`.
- Consequence: the receipt text alone cannot show that the command ran at M1; only the commit that
  adds the receipt can bind it topologically. The plan says the measurement receipt is committed
  with M1, so the intended binding is by commit, not by content; a reviewer must check the commit.
  The C3 receipt has the same shape (`DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True`).
- A green C1 receipt can therefore be produced at any revision and is indistinguishable from an M1
  receipt by its bytes.

## 3. Variant matrix (all commits in the scratch clone, graded by the frozen counter)

| id | mutation in the clone | C1 result |
|---|---|---|
| base | none (`e057166e`) | `checks=14 mismatches=0 met=True`, exit 0 |
| A1 | probe: "The binding ceiling is 1 000 000 tensor headers (the MAX_TENSORS constant)" | `checks=14 mismatches=0`, exit 0 |
| A2 | probe: ceiling list "1,000,000 at nd=1" + decoy "833,332" later | `checks=14 mismatches=0`, exit 0 |
| A3 | probe: "6 steps per header is the binding rule at every rank" | `checks=14 mismatches=0`, exit 0 |
| A4 | probe: honest refutation quoting "6 steps per tensor header" | `checks=14 mismatches=1 met=False`, exit 1 (check 7) |
| B1 | C2 docstring 10 000 000 / 1 GiB; C3 docstring `6 + nd` | `checks=14 mismatches=0`, exit 0 |
| C1 | SCORECARD:6320 pointer `a9b5014c` → `40763bd2` | `checks=14 mismatches=0`, exit 0 |
| C2 | pointer `40763bd2` + unrelated evidence `round-96/measured/c2.out` | `checks=14 mismatches=0`, exit 0 |
| C3b | second evidence path → `does-not-exist.out` | `checks=14 mismatches=0`, exit 0 |
| D1 | SCORECARD:17 "grew 2441 → 2470" → 2442 | `checks=14 mismatches=0`, exit 0 |
| D2 | SCORECARD:7 "base `mismatches=14`" → 13 | `checks=14 mismatches=0`, exit 0 |
| D3 | SCORECARD:20 "(148 lines)" → 149 | `checks=14 mismatches=0`, exit 0 |
| D4 | SCORECARD:17 "three graded probe forgeries" → seven | C1 `14/0`; C3 `checks=8 mismatches=0` |
| D5 | SCORECARD:17 "six rows" → nine | C1 `14/0`; C3 `checks=8 mismatches=0` |
| D6 | SKILL:2463 three → nine, digest stale | `checks=14 mismatches=1`, exit 1 (check 1) |
| D6b | SKILL:2463 three → nine, digest/lines synced | C1 `14/0`; C3 `checks=8 mismatches=0` |
| D7 | SKILL:2437 714,285 → 714,286 + decoy, digest stale | `checks=14 mismatches=2`, exit 1 (checks 1,2) |
| D7b | same, digest/lines synced | C1 `14/0`; C3 `checks=8 mismatches=0` |
| E1b | adjacency file deleted; empty digest; 0 pipes | `checks=14 mismatches=0`, exit 0 |
| E3 | canonical S621 false; correct duplicate appended | `checks=14 mismatches=0`, exit 0 |

The frozen counter's bytes in the clone were sha256
`6b912747fd20410f87ebf3d924b1e2e28a94be268a350bbc0b4a867c1d0c794c`, identical to the lane's
`tools/round97-self-assessment-audit.py`.

## 4. Coverage: re-derivable numbers the 14 checks do not grade

Commands were run in the lane repo at `master` (`e057166e`) unless a revision is named.

| # | row / repeated disclosure | re-derivable number | command → observed | C1 grades? | mutation → result |
|---|---|---|---|---|---|
| 1 | `SCORECARD.md:17` depth row: "SKILL.md grew 2441 → 2470 lines" | 2441 and 2470 | `git show 40763bd2:SKILL.md \| wc -l` → 2441; `git show e057166e:SKILL.md \| wc -l` → 2470 | only 2470 (check 2) | D1 (2441→2442) green |
| 2 | `SCORECARD.md:17`: "six rows at nd=1 and nd=4" | 6 | `sed -n '/### Round 97 correction/,/^### /p' SKILL.md \| grep -cE '^\| [0-9,]+ \| nd='` → 6 | no (C3 grades SKILL's rows, not this SCORECARD number) | D5 (six→nine) green C1+C3 |
| 3 | `SCORECARD.md:17`: "the three graded probe forgeries" | 3 vs 4 new cells / 17 | `grep -n 'NEW_CELLS' tools/round97-router-budget.py` → W14,W15,W16,W17; `grep -n 'CELLS = '` → 17; `controls/c2-new-mutants.out` → cells=4 | no | D4 (three→seven) green C1+C3; live value is false |
| 4 | `SCORECARD.md:20` adjacency row: "(148 lines)" | 148 | `wc -l corpus/knowledge/cross-lane-scope.md` → 148 | no (pipes only) | D3 (148→149) green |
| 5 | `SCORECARD.md:7`: "base `mismatches=14`" / "base `mismatches=3`" | 14 and 3 | `git show e057166e:.ufo/waves/round-96/controls/c2-base.out` → `mismatches=14`; `c3-base.out` → `mismatches=3` | only the two `mismatches=0` needles (checks 13–14) | D2 (14→13) green |
| 6 | `SCORECARD.md:7`: round-96 C1 base `mismatches=1 positive_mismatches=1` with W11-700k red | 1 and 1 | `git show e057166e:.ufo/waves/round-96/controls/c1-base.out \| grep 'ROUTER_BUDGET96 cells'` → matches | no (file never read) | none; coverage gap |
| 7 | `SCORECARD.md:6320`: "measured against `c810f51e`" and second evidence path `controls/c1-base.out` | commit and path | `git merge-base --is-ancestor c810f51e 40763bd2`; `git cat-file -e a9b5014c:.ufo/waves/round-95/controls/c1-base.out` | no (first hex and first path only) | C1/C2/C3b green |
| 8 | `SKILL.md:2463-2468` §Round 97: "three probe variants … W14, W15 and W16" (omits W17) | 3 vs 4 | `grep -n 'NEW_CELLS' tools/round97-router-budget.py` → 4 | no (check 9 only S620/S621/ceilings) | D6b (three→nine) green C1+C3 |
| 9 | `SKILL.md:2435-2439` round-96 ceiling table: 999,999 / 833,332 / 714,285 / 624,999 / 555,555 | five ceilings | `sed -n '2435,2439p' SKILL.md` | literal presence anywhere in SKILL (check 9) | D7b (714,286 in the table + true 714,285 decoy) green C1+C3 |
| 10 | probe comment `tools/kama-probe.sh:577-586`: 5 000 000, 700 000, 4 000 000, 1 000 000 | those numbers | `sed -n '575,586p' tools/kama-probe.sh` | only "5 + nd", four ceiling strings, one exact sentence (checks 7–8) | A1/A2/A3 green |
| 11 | `corpus/SOURCES.md:373` S618 `teaches`: "6 read/seek steps per header is the budget against which MAX_STEPS is sized" | 6 vs `5 + nd` | `grep -n '^| S618' corpus/SOURCES.md`; `grep -n 'supersedes S618' corpus/SOURCES.md` → S621:376 | no (check 10 grades S621 only) | none; C1 green. The plan discloses "S618 stays `mined` as history", but the false constant-6 cell remains live in the registry row. |

The round-96 receipts themselves are one line each
(`git show e057166e:.ufo/waves/round-96/measured/c2.out` → `DEPTH_AUDIT checks=14 mismatches=0
met=True`), so check 13–14 cannot distinguish a measured receipt from a hand-written summary; the
"receipts … are true" half of C1's After bullet is not graded.

## 5. Is C1's sentence wider than the instrument?

Yes. The literal predicate is met honestly:
- base `checks=14 mismatches=9 met=False`, exit 1;
- `9e605d41` and `e057166e` `checks=14 mismatches=0 met=True`, exit 0;
- counter bytes unchanged between freeze and master; the do-nothing control is red.

But "the lane's graded self-assessments match the repo" is a claim about the lane's self-description,
and the counter grades 14 named occurrences:
1–3 by a digest/line/section of the same file the author edits (self-referential),
4–5 by a digest and a pipe count (a missing file can pass as the empty digest),
6 by resolvable+ancestor+first-path (not first-working, not measured-against, not the second path),
7–9 largely by literal presence anywhere in the file (contradictory false statements pass),
10 by the last duplicate row, 11 by three cell indices,
12 by round-96 counter byte identity,
13–14 by one needle per receipt.

At least one live repeated disclosure is false and C1-green (§2.1: three vs four/17; SKILL omits
W17), and the round-96 constant-6 cell is still live in `corpus/SOURCES.md:373` (disclosed as
history; S621 supersedes it, but the row itself still asserts the false budget). Several
re-derivable numbers in the graded rows are ungraded (§4: 2441, six rows, three forgeries, 148
lines, base mismatch counts, measured-against commit). So the sentence is wider than the
instrument, and it is currently false in the live lane even though the predicate prints green.

## 6. Residual risk and verification gaps

- C2 was not executed here (its fixtures/load are the C2 seat's); the "three vs four/17" finding uses
  the frozen counter's source (`CELLS`, `NEW_CELLS`, `MUTANTS`), the frozen plan (lines 83/86/94) and
  the committed freeze-time control `controls/c2-new-mutants.out`, not a fresh C2 run. If C2's own
  measurement later prints `cells=17` with four new cells, the prose count is definitively wrong.
- The plan itself says "three new cells" at `plans/round-97-claims.md:77`; the wave brief says "16
  cells". Three numbers circulate (three / 16 / 17). The counter and its control receipt say 17 and
  four new cells. The plan line 77 and the brief should be corrected or explicitly reconciled; C1
  cannot do it.
- Base per-check status came from an instrumented copy of the frozen counter (same bytes plus a
  fail-list print); no check behavior was changed. The instrumented file is in this out dir.
- No tools were installed; no pacman; no host service touched.
- Scratch `/fast/scratch/hyaku/kama-r97/RV01SelfAssess/` was deleted after the receipts in this out
  dir were copied.

## 7. Verdict

C1's literal predicate is **met** at M1 (`checks=14 mismatches=0 met=True`, exit 0 at both `9e605d41`
and `e057166e`), and the base control is honestly red (9 mismatches, failing checks
1,2,3,6,7,8,9,10,11). The instrument is a 14-surface consistency/regression check, not a semantic
calibration gate: the three attacked shapes all pass (a: A1/A2/A3; b: B1 and the live three-vs-four
count; c: C1/C2/C3b), and the live lane's repeated "three graded probe forgeries" contradicts the
frozen four-cell/17-cell C2 population while C1 reports green. The C1 sentence is wider than the
instrument and currently false in the live lane; that is the finding to route.
