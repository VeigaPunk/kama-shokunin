# CR02Wording — round-97 claim wording vs the instruments that grade it

**Evidence base.** Lane bytes at `e057166e` (freeze `9e605d41` + amendment 1); every lane read is
`git show <rev>:<path>` so a sibling's live write cannot shift the quoted bytes. Counterexample
fixtures were run on a `git clone --shared` under
`/fast/scratch/hyaku/kama-r97/CR02Wording/fix` (deleted before yield). No tracked lane file was
edited; no mutating git/jj command was run on the lane. No tool was installed.

**Verdict in one line.** All three predicates can print green while the round's stated sentences
are false. C1 is green on a probe whose comment states `5 + nd` and whose parser charges a flat 6
(fixture `7d04f0bf`); C3 is green on the same forged probe and on a seven-row table (`63c1d9fc`);
and the self-assessment the round writes into `SCORECARD.md:17` and
`SKILL.md:2443,2463-2467` says **three** graded forgeries where the shipped counter defines
**four** (`NEW_CELLS` and `MUTANTS` are 4 each, `tools/round97-router-budget.py:146,163`; the
committed legacy control prints four `survived=1`, `controls/c2-legacy-mutants.out:15,31,47,63`).
Each prose-grading counter grades a narrower field than the sentence it is cited for.

Axes impacted: **calibration** (C1's count/prose surface), **operability** (C2's predicate and
receipt wording), **depth** (C3's section prose and row-count).

---

## 1. Clause-by-clause table

### C1 — "the lane's graded self-assessments match the repo" (plan `:33`, predicate `:35-38`)

| # | Sentence clause | Enforced? | Required narrowing or amendment |
|---|---|---|---|
| 1 | Heading: *the lane's graded self-assessments match the repo* | **NO as written.** Only the 14 named surfaces are graded. `SCORECARD.md:17` is the row the After names, and its cell `the three graded probe forgeries` is false (four); no counter re-derives it. | Either narrow the claim to "the 14 named cells" (and say so in the report), or add the count to the graded surfaces and correct the row. |
| 2 | depth row digest / line count / section count | **YES** — `round97-self-assessment-audit.py:92-109`. Recomputed: sha `cb17e461…`, 2470 lines, 59 sections at `e057166e`. | none |
| 3 | adjacency row digest / pipe count | **YES** — `:111-122`. Recomputed: sha `c45318b5…`, 16 pipe lines. | none |
| 4 | `router-byte-decided` pointer resolves, is an ancestor, evidence path exists | **YES** — `:124-137`. | none |
| 5 | "the probe comment states `5 + nd` and every per-rank ceiling derived from `MAX_STEPS`" | **PARTIAL.** `:143-145` is `"5 + nd" in probe and "6 steps per tensor header" not in probe`; `:147-153` binds the four ceiling numbers to `MAX_STEPS`. Nothing reads the parser's charge. Fixture `7d04f0bf` (the counter's own `flat6` mutant, comments untouched) → `SELF_ASSESS97 checks=14 mismatches=0 met=True`, while `tools/kama-probe.sh:575` states `5 + nd` and the parser charges 6 for every rank — the forgery C2's W15 catches (`controls/c2-new-mutants.out:13`). | Parse the per-header charge from `ROUTER_PY` and compare it with the comment, or narrow the sentence to "the comment contains the formula string and the four ceilings derived from `MAX_STEPS`" (do not claim the comment *matches the repo*). |
| 6 | "`SKILL.md` … carries all five ceilings and cites S620/S621" | **PARTIAL.** `:155-164` searches the *whole* file for five numbers and the two S-ids; a number in a superseded correction section satisfies it. No section scoping, no arithmetic check. | Scope to the live step-cost section, or narrow to "SKILL.md contains (anywhere)". |
| 7 | "S621's `teaches` opens `supersedes S618 —` with the `5 + nd` arithmetic" | **PARTIAL.** `:166-180` checks the literal prefix and the substring `5 + nd`; the numbers in the cell are not recomputed. | Recompute the cell's ceilings, or narrow to the literal prefix/substring. |
| 8 | S620 spec / A / mined | **YES** — `:181-185`. | none |
| 9 | "the round-96 identity and receipts quoted in SCORECARD are true" | **PARTIAL.** `:186-192`: `tools/round96-router-budget.py` bytes at `f175a902` equal current **and** the token `f175a902` appears anywhere in SCORECARD. `:193-203`: two needles present in their receipts and in SCORECARD. "Quoted" is substring presence, not attribution to the row/claim. | Say "SCORECARD contains the token" and "the needles occur", or parse the SCORECARD cells that carry them. |
| 10 | `checks=14` | **YES by construction** (14 increments; no data-dependent skip). | none |

### C2 — "the budget counter grades four probe forgeries the 13-cell set misses" (plan `:70`, predicate `:72-77`)

| # | Sentence clause | Enforced? | Required narrowing or amendment |
|---|---|---|---|
| 1 | Predicate command prints `cells=17 … load_stable=1 …` and exits 0 at M2 | **NOT MET by the frozen command on this host.** `measured/c2.out` @ `e057166e` ends `could-not-evaluate: W03 natural pass 55.0s < 1.25 x 60s` / `c2_exit=2`. Amendment 1 adds `--slow-files 72`; the frozen sentence still lacks the flag. The counter bytes are unchanged (`git show --stat e057166e`: plan + receipts + ready flags only), so K1 holds while the *sentence's command* does not. | Quote the amended command inside the predicate sentence (`--slow-files 72`, plans/round-97-amendment-1.md) or attach the amendment as the binding reading; the report must not print the unamended command as the one that ran. |
| 2 | "the three control receipts print `survived=1` … and `caught=1` for the three new cells, one per mutant" | **FALSE against the instrument.** Four new cells (`NEW_CELLS`, `:146`), four mutants (`MUTANTS`, `:163`), two control files; the new-cells file holds five CONTROL lines (real probe + four mutants), not one receipt per mutant (`controls/c2-new-mutants.out:6,13,20,27,34`). The only three-file reading (`legacy`, `new`, `could-not-evaluate`) does not print `survived`/`caught` in all three. | "Two control files: `c2-legacy-mutants.out` prints `survived=1` for each of the four mutants over the 13 cells; `c2-new-mutants.out` prints `caught=1` for each of the four mutants over the four new cells (real probe `survived=1`)." |
| 3 | Heading: "grades four probe forgeries the 13-cell set misses" | **TRUE of the four in `After`** (legacy receipt: four `survived=1`). But `Before` (`:79-82`) says "proved four probe variants survive every one of the 13 cells" and names a *different* four (unbounded, per-header, `MAX_META`, ctime), then two lines later admits "W13 closed only the unbounded-budget class". W13 is in `LEGACY_CELLS` (`:143-145`) and its own cell comment says the cap is load-bearing, so the unbounded shape does not survive the 13-cell set today. Two fours with intersection 2. | Split the referents: "G1 proved four survive the then-12-cell set; W13 closed unbounded; round 97 grades four mutants (two inherited: undercharge, maxmeta; two new: flat6, nopreamble); ctime is disclosed unobservable." |
| 4 | "each mutant `caught=1` on the new cells" / After's cell↔forgery attribution | **PARTIAL.** `caught = int(n_ok < n)` (`:625`) asserts *some* red cell, not the named one. Receipts: flat6→W15 only; maxmeta→W16 only; undercharge→W14+W15+W17; nopreamble→W14+W15+W17 (`c2-new-mutants.out:13,20,27,34`). So "W17 catches the preamble drop" is receipt-read, not counter-enforced; any mutant that reddens another cell also prints `caught=1`. | State the ∃-red semantics, or add a `--expect-cell` control that grades the named cell. |
| 5 | Both host loads in the predicate; natural-only controls | **YES** — `:630-650`; control receipts are natural-only. | none |
| 6 | K1 "the counter's bytes change after the freeze" | **HOLDS** — amendment 1 changes no counter bytes. The predicate *command* changed; keep "frozen instrument" and "frozen sentence" separate. | Say which one K1 binds. |
| 7 | Disclosed limits (a)-(d) | Honest about the four forgery classes and the ctime argument; **silent** on (i) ∃-red control semantics and (ii) the host-conditional command. | Add both to the limit list. |

### C3 — "the step-budget boundary table states the two rank classes" (plan `:110`, predicate `:112-115`)

| # | Sentence clause | Enforced? | Required narrowing or amendment |
|---|---|---|---|
| 1 | "six boundary rows … `steps = 4 + T x (5 + nd)`, the `<=`/`>` comparison against `5,000,000` and the verdict" | **PARTIAL.** Rows are parsed and recomputed (`round97-depth-boundary-audit.py:103-107`), all six required pairs are demanded (`:37-38,115-118`), and the budget literal must occur. **"Six" is not enforced by the exit code**: a seventh *correct* row prints `rows=7 checks=9 mismatches=0 met=True`, exit 0 (fixture `63c1d9fc`); `main` returns 0 on `mismatches == 0` only (`:126`). The predicate's literal `rows=6` is descriptive, not graded. | Amend the predicate to `rows=<n>` plus a `rows != 6` kill, or return 1 when `rows != 6`. |
| 2 | K2 "recompute from the probe's `MAX_STEPS`" | **PARTIAL.** `MAX_STEPS` is read from the probe, but the per-header charge `5 + nd` and `PREAMBLE = 4` are hard-coded (`:35,103`). On fixture `7d04f0bf` (flat6 parser) the counter prints `rows=6 checks=8 mismatches=0 met=True` while every row's verdict is false for that parser (same bytes C2's W15 catches). | Say "recompute from `MAX_STEPS` and the *declared* `5 + nd` formula", or parse the charge from the probe. |
| 3 | "it cites S620 … and S621" | **PARTIAL** — substring presence anywhere in the section (`:133-137`); not bound to the rows. | Bind the citations to the row set, or narrow to "the section contains". |
| 4 | Section prose (the artifact C3 owns; not in its predicate) | **NOT GRADED and FALSE.** `SKILL.md:2443` "the three graded forgeries"; `:2463` "three probe variants survive all 13 of its cells"; `:2467` "grades each with W14, W15 and W16". The repo has four survivors (`c2-legacy-mutants.out:15,31,47,63`), four new cells, four mutants. `SCORECARD.md:17` repeats "three". | Correct to four and name W14–W17 (this edits `SKILL.md`, so the depth digest/lines/sections must be re-recorded in the same change and C1 re-run), or narrow C3's claim to "the table rows only" and route the prose defect. |

---

## 2. Prefile ledger (`.ufo/waves/round-97/claim-falsification.tsv`)

State today: **the file does not exist** (`ls` → No such file). The gate is
`scripts/hyaku/prefile-falsification.py`; its contract is five TAB columns
`claim / artifact / verdict / narrowing / note`, artifact must exist **under
`.ufo/waves/round-97/`**, verdict ∈ `{falsifies-wording, falsifies-number, neutral}`, a
`falsifies-wording` row needs a resolving narrowing pointer, every claim `C1..C3` needs a row, and
**every attack seat must appear as a substring of the artifact column**
(`prefile-falsification.py:66-70,232-236,254-257`).

`ATTACK_ROLES` are `reviewer, security-reviewer, critic, mutation-tester, sentinel, connector,
revenger, labrat` — so the r97 w1 attack seats are **8**: RV01SelfAssess, RV02BudgetCells,
CR01Boundary, CR02Wording, MT01Forgeries, SN01StepFlips, RV03Intent, CN01Overlap. The scouts
(SC01SiblingScan, SC02SourceReopen), executors (EX01SelfAssessControl, EX02BudgetControl) and
scribe (SB01) are **not**
attack roles; do not pad the ledger with them, and do not omit **CN01Overlap** (connector counts).

| Attack seat | Artifact it will file (path must contain the seat id) | Claims its finding can falsify | Rows the L1 must file |
|---|---|---|---|
| RV01SelfAssess (reviewer) | `w1/out/RV01SelfAssess/RV01SelfAssess.md` | **C1** (primary: re-derivable vs 14 surfaces), **C3** (the same depth-row/§Round 97 prose it reads) | C1 + C3 if its finding reproduces the count drift |
| RV02BudgetCells (reviewer) | `w1/out/RV02BudgetCells/RV02BudgetCells.md` | **C2** (primary: cells, control semantics) | C2 |
| CR01Boundary (critic) | `w1/out/CR01Boundary/CR01Boundary.md` | **C3** (primary: table vs parser), **C2** if it finds W15/W17 attribution | C3 + C2 when both |
| CR02Wording (critic) | `w1/CR02Wording.md` (this file) | **C1** (false comment passes; "three" cell), **C3** (seven-row and flat6 greened; three/four), **C2** (predicate counts/receipts) | C1 + C3 + C2 |
| MT01Forgeries (mutation-tester) | `w1/out/MT01Forgeries/MT01Forgeries.md` | **C2** (primary), **C1** (a forged parser under the unchanged comment stays green) | C2 + C1 |
| SN01StepFlips (sentinel) | `w1/out/SN01StepFlips/SN01StepFlips.md` | **C3** (boundary flips), **C1** if it finds comment/number drift | C3 + C1 when both |
| RV03Intent (revenger) | `w1/out/RV03Intent/RV03Intent.md` | **C2** (control receipts vs "three receipts"/named-cell claims), **C1** (identity clause) | C2 + C1 |
| CN01Overlap (connector) | `w1/out/CN01Overlap/CN01Overlap.md` | **C1/C3** depending on its prior-round table; at minimum a neutral row | at least neutral, C1 or C3 |

Operational traps for the L1: (i) one row per *claim* is not enough — the gate substring-matches
seat ids against artifact paths and reports `attack-seat-unread`; (ii) the same artifact may appear
under two claims (allowed), but the same `(claim, artifact)` twice is `artifact-repeated`;
(iii) a `falsifies-wording` row without a plan-amendment pointer is `narrowing-missing`, and the
pointer must resolve; (iv) the gate refuses at setup until `w1-results.json` and the fleet report
exist — file the ledger before the report closes.

---

## 3. Disclosed limits: honest or hiding a shape?

- **C1** discloses "other SCORECARD rows … are not graded". It does **not** disclose that *other
  cells of the graded depth row* are not graded. The After says "SCORECARD's `depth` row matches
  the committed `SKILL.md` bytes" — only sha/lines/sections are read, while the row's own count
  cell ("three graded probe forgeries") is false. That is the round-96 shape (sentence wider than
  the graded property) one level down, and it is the most likely wording rejection of this round.
- **C2** discloses the forgery classes and the ctime argument honestly; it does not disclose that
  `caught=1` means ∃-red, or that the predicate command is host-conditional. Both change what a
  filer is entitled to say.
- **C3** discloses incompleteness over `(T, nd)` pairs but not the formula assumption (the counter
  never reads the parser's per-header charge) and not that `rows=6` is unenforced.

**Explicit answer to the seat's Q3.** *Is "the lane's re-derivable self-assessments match the
repo" falsified by a SCORECARD cell that is not re-derivable by the audit?* **Yes.**
`SCORECARD.md:17` cell "the three graded probe forgeries" is a count, re-derivable from
`tools/round97-router-budget.py:146` (`NEW_CELLS` = 4), `:163` (`MUTANTS` = 4) and
`.ufo/waves/round-97/controls/c2-legacy-mutants.out` (four `survived=1`), and it is **false**.
`SKILL.md:2443,2463,2467` repeats the same false count inside the C3 section. All three predicates
stay green because C1 reads only three fields of that row and C3 reads only the table rows. The
frozen C1 predicate (14 surfaces) escapes falsification only by the narrowing in its After; the
sentence the round actually publishes in SCORECARD/SKILL does not.

---

## 4. Smallest safe corrections (ranked)

1. **Count drift (calibration/depth, no counter change).** Correct `SKILL.md:2443,2463,2467` and
   `SCORECARD.md:17` from three to four, name W14–W17, and record an amendment stating the two
   fours (G1 survivors vs round-97 mutants; W13 closed unbounded; ctime unobservable). This edits
   `SKILL.md`, so re-record the depth digest/lines/sections in the same commit and re-run C1 at the
   new measured commit; otherwise C1 goes red (fixture `63c1d9fc` shows exactly those three checks
   failing on an edited `SKILL.md`).
2. **C2 predicate wording.** Replace the second half with the two-file/four-mutant/four-cell
   sentence; put `--slow-files 72` (amendment 1) inside the predicate; state ∃-red control
   semantics; add the mutant→witness-cell table as evidence, not predicate.
3. **C1/C3 formula-vs-parser.** Either add a check that reads the per-header charge from the probe
   (counter change → re-freeze with new controls) or narrow both sentences to "comment strings and
   numbers derived from `MAX_STEPS`" / "declared formula", and route the flat6 counterexample.
4. **C3 row count.** Amend the predicate to `rows=<n>` plus a `rows != 6` kill, or narrow "six"
   to "the six required rows are present among the rows graded".
5. **Ledger.** File per §2 (8 seats; C1/C2/C3 each covered; CN01 not omitted).

---

## 5. Receipts (real commands, real output)

```
$ git -C <lane> log --oneline -2
e057166e round-97 amendment 1: C2 host-speed slow-files 72 (guard fired before any cell scored)
9e605d41 round-97 freeze: three counters, 5 + nd disclosures, S619-S621, boundary table, KQ152

$ git -C <lane> show e057166e --stat
 plans/round-97-amendment-1.md, .ufo/waves/round-97/{controls/c2-could-not-evaluate.out,
 measured/c2.out, w1.ready, w1.ready.dispatched}   # no tools/ bytes

$ git -C <lane> show e057166e:.ufo/waves/round-97/measured/c2.out | tail -2
ROUTER_BUDGET97 could-not-evaluate: W03 natural pass 55.0s < 1.25 x 60s — the round-94 constant
wrapper would not truncate this listing on this host, so no discriminator is claimed
c2_exit=2

# fixture clone (read-only source, scratch work tree)
$ git clone --shared <lane> $S/fix && git -C $S/fix rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r97/CR02Wording/fix

$ python3 tools/round97-self-assessment-audit.py --repo . --rev e057166e
SELF_ASSESS97 checks=14 mismatches=0 met=True            # rc=0
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev e057166e
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True   # rc=0

$ python3 tools/round97-self-assessment-audit.py --repo . --rev 40763bd2
SELF_ASSESS97 checks=14 mismatches=9 met=False           # rc=1 (matches plan)
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev 40763bd2
DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False           # rc=1

# 7d04f0bf = fixture where the probe carries the counter's own `flat6` patch and its comment is
# untouched (diff: ne = [u64() ...] -> _b = rd(8 * nd); struct.unpack ...)
$ python3 tools/round97-self-assessment-audit.py --repo . --rev 7d04f0bf
SELF_ASSESS97 checks=14 mismatches=0 met=True            # rc=0  <-- false self-assessment passes
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev 7d04f0bf
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True   # rc=0  <-- every verdict false for this parser
$ grep -n 'binding ceiling is' tools/kama-probe.sh       # (at 7d04f0bf)
575:# The binding ceiling is `5 + nd` steps per tensor header ...

# b82ebac4 = comment's nd=4 ceiling 555,555 -> 555,556 (numbers ARE graded)
$ python3 tools/round97-self-assessment-audit.py --repo . --rev b82ebac4
SELF_ASSESS97 checks=14 mismatches=1 met=False           # rc=1

# 63c1d9fc = seventh CORRECT boundary row appended to the section
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev 63c1d9fc
DEPTH_BOUNDARY97 rows=7 checks=9 mismatches=0 met=True   # rc=0  <-- predicate says rows=6
```

Tooling: none installed or upgraded this seat. Scratch removed before yield; receipts are the
commands and outputs above.
