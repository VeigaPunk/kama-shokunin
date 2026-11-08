# CR01Records — round-99 C2 (calibration) falsification

Seat `CR01Records`, attack wave w1. Lane `kama-shokunin`, HEAD at review
`f6e7ccc285e0c1207378f73c394acbfda58bff23` (the round-99 freeze commit); base revision
`439fdb3d41b55e5b9e6d7c480d17f2c428bae978`. The corrections I graded are **uncommitted** at
review (` M SCORECARD.md`, ` M LOG.md`, `?? corpus/lessons/round-99.md`), so no M2 exists yet; I
graded the working-tree bytes with `--tree` and, to keep the freeze bytes in play, the same bytes
committed in a scratch `git clone --shared` and graded with `--rev`. Receipts:
`.ufo/waves/round-99/w1/out/CR01Records/{adversarial-runs.txt,census-revisions.txt,forge-provenance.txt,check-matrix.tsv}`.

**Verdict.** The twelve substantive statements the corrections make are true — I re-derived every
one (§6). C2's claim that the records "agree with the committed wave evidence on twelve enumerated
propositions" is nevertheless **not established by `checks=12 mismatches=0`**: on the freeze bytes,
a correction that states the *opposite* result passes 12/12 (T_a), a correction that exists only
inside a fenced example passes 12/12 (T_c), a lesson that swaps the r98 base/tip revision
identities passes 12/12 (T_h2), and two of the twelve checks (8, 12) pass at the uncorrected base
with no correction at all. Separately, the graded counter's working-tree bytes differ from the
freeze commit's bytes (`tools/round99-record-audit.py:252`), and the untracked forged-control
receipt is reproducible only with those post-freeze bytes — a K1 exposure, not a sentence-level
defect.

## 1. The twelve checks: re-derive vs token (one line each)

| # | code | mechanism | token-only? |
|---|---|---|---|
| 1 | `tools/round99-record-audit.py:178` | Requires the token `12 reported, 0 dead` in a SCORECARD block whose first heading is after the first `10 reported, 2 dead`; the 12 is re-derived only in check 11. | token + ordering |
| 2 | `tools/round99-record-audit.py:181` | Same for `LOG.md`. | token + ordering |
| 3 | `tools/round99-record-audit.py:185` | `"SCORECARD.md:6431" in both and "LOG.md:4040" in both` — presence in the **concatenation** of both blocks. | **token-only** |
| 4 | `tools/round99-record-audit.py:188` | Population is re-derived from `w1-results.json`, but the record is graded by `\b7 attack\b`, `\b5 non-attack\b`, and every derived name appearing *anywhere* in the union; membership is not graded. | token (association) |
| 5 | `tools/round99-record-audit.py:192` | `EX02BudgetControl` and `SB01-equivalent` substrings. | **token-only** |
| 6 | `tools/round99-record-audit.py:195` | `RV03Intent` substring. | **token-only** |
| 7 | `tools/round99-record-audit.py:201` | Line-local labelled regex (`base…361…A 344…` / `tip…363…A 345…`) over the whole lesson; the revision hashes are never read. | token sequence |
| 8 | `tools/round99-record-audit.py:212` | Re-derives census at the hardcoded `R98_BASE`/`R98_TIP` and compares to hardcoded `EXPECT_*`; it does not read the record. | re-derives, no record |
| 9 | `tools/round99-record-audit.py:217` | Re-derives the gate verdict and arm set from the receipt; the correction is graded only by the six arm names, and the verdict string is *not* required in `both`. | token + derivation |
| 10 | `tools/round99-record-audit.py:224` | `M3`, `round-98.md`, `sampling` inside the `## Mistakes` slice. | **token-only** |
| 11 | `tools/round99-record-audit.py:227` | Re-derives `seats=12/results=12/dead=[]` from the results file; the record is graded by `12 seats` and `12 results` tokens. | token + derivation |
| 12 | `tools/round99-record-audit.py:231` | Pure re-derivation of the results-file split (`len(attack)+len(non)==12 and len(attack)==7`); reads no record and is implied by check 11. | re-derives, no record |

**Token-only checks: 3, 5, 6, 10.** In addition, the graded component of checks 1, 2, 4, 9 and 11
is token presence, and check 4's *association* plus check 7's *revision binding* are not graded at
all. Checks 8 and 12 are the only pure re-derivations, and neither is a re-derivation of the
record.

## 2. Adversarial trees

Every tree is the current working-tree content (`SCORECARD.md`, `LOG.md`, both lessons,
`w1-results.json`, the gate receipt) with one mutation. `--tree` = the working counter
(`sha256 59f22d5e…`); the frozen run = `git show f6e7ccc2:tools/round99-record-audit.py`
(`sha256 5e2be139…`) with the same tree committed in a scratch clone and graded `--rev`. Full
transcripts: `out/CR01Records/adversarial-runs.txt`.

| ID | mutation | `--tree` exit | mismatches | `--rev` (freeze bytes) |
|---|---|---|---|---|
| base | none (current corrections) | 0 | 0 | 0 |
| **a** | exact tokens + contradictory narrative (below) | **0** | **0** | **0** |
| b | duplicate correction heading *before* the stale line | 1 | 1,2 | 1,2 |
| b2 | exact duplicate of the live heading before the stale line | 1 | 1,2 | 1,2 |
| **c** | the only correction sits inside a ```` ```text ```` fence labelled "example only" | **0** | **0** | **0** |
| d | census numbers swapped between base and tip | 1 | 7 | 7 |
| e | `12/0` corrected but the old 4-name building list restored | 1 | 4 | 4 |
| **e2** | all 12 names kept, but `CN01Overlap` moved into the attack list and `SN01StepFlips` into the non list | **0** | **0** | **0** |
| **f** | pointer clause deleted from the SCORECARD block (both pointers remain in LOG) | **0** | **0** | **0** |
| **g** | `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` deleted from both correction blocks, six arm names kept | **0** | **0** | **0** |
| **h** | counts kept, hashes replaced (`439fdb3d→361`, `160e22dd→363`) | **0** | **0** | **0** |
| **h2** | counts kept, revision *identities* swapped: `base 649bb2e9 → 361`, `tip 681c80a4 → 363` | **0** | **0** | **0** |
| **i** | M3 row rewritten to "no record was carried; this row is not a sampling note about `round-98.md`" | **0** | **0** | **0** |

Answers to the assigned constructions:

- **(a) passes 12/12.** Appended to the SCORECARD block (T_a):
  "This correction is itself false: the wave really had 10 reported, 2 dead … the 12 seats and 12
  results are an artifact of the directory scan, the 7 attack / 5 non-attack split is the
  spot-check's guess … `SB01-equivalent` really was the fifth builder, `EX02BudgetControl` is a
  different seat, and `RV03Intent` was never dispatched."
  The counter prints `checks=12 mismatches=0 met=True`. Checks 1, 2, 4, 5, 6, 11 are all satisfied
  by substrings inside a sentence that denies them.
- **(b) fails checks 1 and 2.** `correction_blocks()` joins every matching block, and
  `score.find(s_block[:20])` returns the *first* occurrence, which is the pre-stale duplicate, so
  the ordering comparison fails. The ordering guard is real; a duplicate before the stale line is
  refused (both the differently-worded draft and the exact duplicate: `mismatches=2`).
- **(c) passes 12/12.** `BLOCK_RE` (`tools/round99-record-audit.py:65`) is line-anchored and
  markdown-fence-blind. A block inside ```` ```text ```` introduced by "(this is an example only;
  the live record is elsewhere)" is graded live. A reader would not call it live.
- **(d) fails check 7 (one mismatch).** Pure number swap inside the labels (`base … 363 …; tip …
  361 …`) is caught because the regex is line-local and each pattern cannot span the other group.
  The *identity* swap h2 is **not** caught: the counter passes a lesson that says the r98 base is
  `649bb2e9` and the r98 tip is `681c80a4`, i.e. the exact inverse of the verified truth (§3).
- **(e) fails check 4 (one mismatch).** Replacing the five full non-attack names with the old
  `SC01/SC02 scouts, EX01 executor, SB01-equivalent, CN01` list removes
  `SC01SiblingScan`/`SC02SourceReopen`/`EX01SelfAssessControl`/`CN01Overlap`, so the presence
  requirement fails. But e2 shows why it fails: not because membership is checked, but because the
  full strings are absent.

Extra constructions (not assigned, same root cause): f (cross-file token pooling — the SCORECARD
correction names neither of its own stale pointers), g (the verdict line the plan says check 9
grades is not required by the code), h/h2 (check 7 is unbound to revisions), i (check 10 is
token-only; a sentence saying "no record was carried" passes).

## 3. Census revisions and "HEAD" in `round-98.md:28`

Truth first:

- `plans/round-98-claims.md:3` — "Base revision `681c80a4e3c745c22559f74b2c2a1917bdc66fc6`".
- `corpus/lessons/round-98-verifier-spotcheck.md:3-5` — "Lane `kama`, round 98. Base
  `681c80a4e3c745c22559f74b2c2a1917bdc66fc6`; measured candidate
  `160e22ddf31f368fe802d3512cd09d51adf59784`; lane tip before this file's commit
  `649bb2e94501ee8aa2d4ceaeae52f7a1fb8d1ce9`."
- `git merge-base --is-ancestor 681c80a4 649bb2e9` → rc 0; `… 649bb2e9 439fdb3d` → rc 0;
  `… 681c80a4 439fdb3d` → rc 0.
- Frozen census (`bash scripts/sources-census.sh census --file <git show rev:corpus/SOURCES.md>`):

| rev | rows | A | B | C | mined | queued | rejected |
|---|---|---|---|---|---|---|---|
| 681c80a4 (r98 base) | 361 | 344 | 11 | 6 | 324 | 8 | 29 |
| 160e22dd (r98 M1) | 363 | 345 | 11 | 7 | 325 | 8 | 30 |
| 380982b1 (r98 wave commit) | 363 | 345 | 11 | 7 | 325 | 8 | 30 |
| 649bb2e9 (r98 tip) | 363 | 345 | 11 | 7 | 325 | 8 | 30 |
| 439fdb3d (r99 base) | 363 | 345 | 11 | 7 | 325 | 8 | 30 |
| f6e7ccc2 (r99 freeze) | 366 | 347 | 11 | 8 | 327 | 8 | 31 |

So: **681c80a4 is the r98 base and 649bb2e9 the r98 tip, and the two census groups in the
correction are right.** (Full receipt: `out/CR01Records/census-revisions.txt`.)

"HEAD" in `corpus/lessons/round-98.md:28`: the sentence is

> `tiers measured with the census at HEAD (361 rows: A 344, B 11, C 6; mined 324, queued 8, rejected 29) against base (361: A 344, B 11, C 6; mined 324, queued 8, rejected 29)`

At every commit that carries the line (`34ad44e9`, `3185c257`, `3b71d098`, `380982b1`,
`649bb2e9`) the census is **363**, and the r98 *wave* commit `380982b1` is also 363. The 361
figures are reproducible only at `681c80a4` — the round-98 **base** HEAD. "HEAD" therefore cannot
mean the r98 wave commit; it can only mean the pre-round base HEAD. The spot-check states this
exactly (`corpus/lessons/round-98-verifier-spotcheck.md:126-128`):

> `corpus/lessons/round-98.md:28` says "tiers measured with the census at HEAD (361 rows: A 344, B 11, C 6; mined 324, queued 8, rejected 29)"; HEAD is 363 rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30) — the quoted numbers are base's.

The lesson99 correction's base/tip attribution is therefore correct. But the counter does not
check it: T_h2 (base `649bb2e9` → 361, tip `681c80a4` → 363) passes 12/12, and check 8's
re-derivation never consults the lesson's hashes.

## 4. Checks whose pass is not evidence, and the required amendment

Mapping to the round-98 spot-check's routed defects: defect 1 → checks 1/2/3/11; defect 2 →
4/5/6/12; defect 3 → 7/8; defect 4 → 10; defect 6 → 9.

**Not evidence at all**

- **Check 12** (`:231`). Passes at the uncorrected base (the base run's mismatch list is
  `1,2,3,4,5,6,7,9,10,11`; 8 and 12 are green) and reads no record. It answers the routed defect's
  *question* ("is the split 7/5?") only by re-asserting the frozen results file; it does not grade
  the correction. **Amendment:** delete it, or replace it with a set-equality between the two
  labelled seat lists parsed out of the correction and the two role sets derived from
  `w1-results.json` (this subsumes the check-4 fix).
- **Check 8** (`:212`). Same: green at base with no correction; it re-derives the census at the
  hardcoded revisions and compares to hardcoded constants. It is an oracle, not a check on the
  record, and it cannot catch the revision misattribution T_h/T_h2. **Amendment:** make check 8 the
  oracle *for* check 7: parse `(rev, rows, A, B, C, mined, queued, rejected)` tuples out of the
  lesson, require the revision set `{681c80a4, 649bb2e9}` with the labels base/tip, and compare
  each tuple to the census re-derived at *that* revision. Then check 7 and 8 are one proposition,
  not two.

**Token-only, so a denial passes**

- **Checks 3, 5, 6** (`:185`, `:192`, `:195`). The plan's limit (c) says these tokens' "values are
  bound by checks 4/9/11's re-derivation". Measured: check 4 does not bind membership (e2), check 9
  does not require the verdict at all (g), and check 11 binds only 12/12/0. **Amendment:**
  check 3: require `SCORECARD.md:6431` in the SCORECARD block and `LOG.md:4040` in the LOG block,
  and assert the target line at M2 contains `10 reported, 2 dead` (parse `SCORECARD.md` line 6431
  and `LOG.md` line 4040). Checks 5/6: require `EX02BudgetControl` in the parsed non-attack list
  and `RV03Intent` in the parsed attack list (set membership), and reject `SB01-equivalent` inside
  the live block except as a quoted stale reference.
- **Check 10** (`:224`). T_i passes with "no record was carried". **Amendment:** require the
  carried proposition, not three words: `RV03Intent` and `EX02BudgetControl` both named as settled,
  the r98 `## Spot-check` placement fact, and the `out/<Name>/` convention, all inside the round-99
  `## Mistakes` slice.
- **Checks 1/2/11** (`:178`, `:181`, `:227`). The corrected counts are tokens; T_a negates them and
  passes. **Amendment:** parse the live block's labelled sentence (`12 reported, 0 dead`,
  `12 seats`, `12 results`) and compare its numbers to the derived values, and reject a live block
  that contains the stale tuple `10 reported, 2 dead` outside a quoted stale reference. The
  position guard (b) is sound and should stay.
- **Check 4** (`:188`). **Amendment:** parse the two labelled lists as sets and require exact set
  equality with the derived `attack`/`non` sets; reject duplicates and any name in both lists.
- **Check 7** (`:201`). **Amendment:** bind the hashes as in the check-8 amendment. The current
  regex is narrower than the plan's own check-7 wording (`plans/round-99-claims.md:99-101`, which
  names `681c80a4` and `649bb2e9`), i.e. exactly the standing failure class the plan names ("a
  frozen counter going green on a property NARROWER than the claim's wording").
- **Check 9** (`:217`). The code re-derives the receipt's six arms and requires those names in the
  union, but never requires `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` in the correction
  (T_g). **Amendment:** require the verdict line in `both` and set-equality of the six arm names.

Also **falsified lane claims about the instrument**:
`controls/counter-literal-scan.out:16-18,47-49,67-69` states "a value token is bound by a
re-derivation check in the same counter; no counter passes on presence alone except the disclosed
token checks (C2 checks 3/5/6)". T_a/T_c/T_e2/T_f/T_g/T_h2/T_i pass on presence alone outside
3/5/6, and 8/12 pass with no record. The judgement needs rewriting to list the actual token-graded
propositions, or the checks need the amendments above.

## 5. Freeze bytes, K1, and the forged control's provenance

`git diff tools/round99-record-audit.py` (HEAD `f6e7ccc2` = freeze):

```diff
@@ -250,9 +250,8 @@ def main() -> int:
 def read_bytes_at(rev: str, path: str, repo: Path, tree):
-    if tree:
-        p = tree / path
-        return p.read_bytes() if p.exists() else None
+    # The two census revisions are historical and always come from git, also under --tree:
+    # a materialized tree holds only the current bytes.
     p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
```

`sha256(freeze bytes) = 5e2be1391e199aa6…`, `sha256(working tree) = 59f22d5e3e891ca5…`. C2's K1
(`plans/round-99-claims.md:111`) says the counter's bytes change after the freeze commit kills the
claim. If M2 commits this hunk, K1 fires. If M2 does not, the forged control in
`controls/c2-forged.out` is not reproducible from the graded bytes, as measured:

- `python3 tools/round99-record-audit.py --repo . --tree <forge> --work <scratch>` — **working
  bytes** — prints `checks=12 mismatches=2` (checks 1,2), matching the receipt.
- The **freeze bytes** on the same forge tree print `checks=12 mismatches=3` (checks 1,2 **and 8**),
  because `read_bytes_at` under `--tree` reads `tree/corpus/SOURCES.md` for *both* historical tags,
  so `got_base == got_tip` and check 8 can never be satisfied under `--tree` (EXPECT_BASE ≠
  EXPECT_TIP). With a tree lacking `corpus/SOURCES.md` the freeze bytes print
  `could-not-evaluate: census revision bytes unavailable`, exit 2.
- The freeze bytes *do* run cleanly with `--rev` on a scratch clone. I cloned with
  `git clone --shared` into scratch, asserted `git rev-parse --show-toplevel` equals the clone,
  committed the correction set (good = `3d684792`) and a forged version stating `10 reported,
  2 dead` (forge = `06f8aa56`), and ran the freeze counter:
  good → `checks=12 mismatches=0 met=True`, exit 0; forge → `MISMATCH 1`, `MISMATCH 2`,
  `checks=12 mismatches=2`, exit 1 — exactly the intended discrimination, without post-freeze
  bytes. Receipt: `out/CR01Records/forge-provenance.txt`.

So the forged control as filed is evidence for the post-freeze counter, not for the frozen one;
the plan's `--tree` instruction (`plans/round-99-claims.md:108-110`) is incompatible with the
frozen grader's check 8.

Instrument-record defect: the counter's own docstring
(`tools/round99-record-audit.py:10`) says the base run prints `mismatches=9`; the plan
(`plans/round-99-claims.md:92-93`), the committed control (`controls/c2-base.out`), and my rerun
all print **10**. The frozen counter at `--rev 439fdb3d` prints
`RECORD_AUDIT99 checks=12 mismatches=10 met=False`, exit 1.

## 6. What survives

The correction's content is right; I re-derived each proposition from committed bytes:

1. `w1-results.json` (committed at `380982b1`, present at `649bb2e9`): `seats=12`, 12 result
   records, every `output` non-empty; roles give 7 attack
   (RV01/RV02 `reviewer`, CR01/CR02 `critic`, MT01 `mutation-tester`, SN01 `sentinel`, RV03
   `revenger`) and 5 non-attack (SC01/SC02 `scout`, EX01/EX02 `executor`, CN01 `connector`).
2. `corpus/lessons/round-98.md:83` M3 records that `RV03Intent` and `EX02BudgetControl` "settled
   inside the same wave"; both results carry outputs (651 and 1045 chars).
3. `SCORECARD.md:6431` and `LOG.md:4040` are the stale "10 reported, 2 dead" lines; `LOG.md:4044`
   is the `SB01-equivalent` / four-name building list; `SCORECARD.md:6433-6434` lists six attack
   seats without `RV03Intent` and with `CN01`.
4. Census 681c80a4 → 361/344/11/6/324/8/29 and 649bb2e9 → 363/345/11/7/325/8/30 (§3).
5. `.ufo/waves/round-98/measured/pre-report-gate.out` ends
   `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` and carries exactly six
   `PRE_REPORT_ARM … FAIL` lines: `selfdesc`, `newest-closure`, `round-scope`, `round-clean`,
   `round75-instruments`, `round78-instruments` — `round-clean` included.
6. The round-99 `## Mistakes` slice carries M3; the correction blocks are after the stale lines.

The falsification is of the *instrument* (and of the plan's/scan's descriptions of it), not of the
correction's facts. But "`checks=12 mismatches=0` at M2" cannot carry the claim as written: on the
freeze bytes, eight separate mutations of the record's meaning pass 12/12 (T_a, T_c, T_e2, T_f,
T_g, T_h, T_h2, T_i), and 2 of the 12 checks are green at base.

## 7. Smallest safe correction

1. **Keep the freeze bytes.** Revert `tools/round99-record-audit.py`'s `read_bytes_at` hunk to
   `git show f6e7ccc2:…` and run the forged control as a **`--rev`** commit in a scratch
   `git clone --shared` (proved: good 12/12, forge checks 1–2 only). Do not commit the hunk unless
   the plan is amended and the freeze controls regenerated; as it stands, committing it trips K1
   and leaving it uncommitted makes `controls/c2-forged.out` unreproducible. Also change
   `plans/round-99-claims.md:108-110` from `--tree` to the clone/`--rev` method.
2. **Bind the token checks**: per-file pointers with the target line's content (check 3), parsed
   set equality for the seat lists (checks 4/5/6/12), parsed `(rev → census tuple)` for check 7 with
   the hash set `{681c80a4, 649bb2e9}` and base/tip labels (fold in check 8), the verdict line plus
   set equality for check 9, the carried M3 proposition for check 10, and label-adjacent derived
   counts with a reject-if-stale-tuple for checks 1/2/11.
3. **Re-run the forgery control after (2)**: the forged correction must fail *because the graded
   proposition is false*, not because check 8's oracle is broken or because the counter is the
   post-freeze copy.
4. Fix `tools/round99-record-audit.py:10` (`mismatches=9` → `10`) and rewrite
   `controls/counter-literal-scan.out`'s judgement to enumerate the actual token-graded checks.

Impacted axes: **calibration** (C2 — the graded instrument is narrower than the claim; cannot be
counted as evidence until amended), **freshness/provenance** (K1 byte drift and the
golden-receipt reproducibility), and the plan's own named failure class is live. Operability/depth
are not touched by this seat.

## 8. Bounds, tooling, cleanup

- Read-only against the lane: no tracked lane file was written, no git/jj mutation in the lane, no
  `git add/commit/…` outside the scratch clone. Every fixture is under
  `/fast/scratch/hyaku/kama-r99/CR01Records/`; the clone was created with `git clone --shared` and
  its `rev-parse --show-toplevel` was asserted to equal the clone path before the first commit.
- No tools installed or upgraded; no pacman; no host sysctls; no stub servers (C2 is static).
- Scratch `/fast/scratch/hyaku/kama-r99/CR01Records` was removed after the receipts were copied to
  `.ufo/waves/round-99/w1/out/CR01Records/`.
