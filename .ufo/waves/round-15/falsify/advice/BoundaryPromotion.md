# BoundaryPromotion — round 15 falsification (SHONEN unchanged, no phantom promotion, no numeric increase)

Seat: KamaR15.BoundaryPromotion (connector, leaf). Candidate attacked: committed HEAD `70af36c` ("round-15: enforce duplicate corpus admission before replay children"), parent `6e348e2`. No checks, tests, builds or gates were executed. Only read, grep, `git show`/`git hash-object`/`sha256sum` (plain metadata). Scratch diffs went to `/tmp` only. Tools installed: none.

## Result

No fail finding for the assigned attack. Three non-blocking observations are listed in §4.

## 1. SHONEN assertions unchanged — PASS

- `SHONEN.md` worktree SHA-256 = `9a8e9e17e591d0212821db9cc851af49d4eb7f1fd3af9c190aea06650daa38f5`. `git show HEAD:SHONEN.md | sha256sum` gives the same digest. The same digest is recorded in `.ufo/round-5/worktree-byte-manifest.json` (line 7).
- `git log -- SHONEN.md` last touches it at `e246c40` (round-5). `70af36c --stat` lists 98 files and does not include `SHONEN.md`.
- Four author-assertion lines are present, all `- [~]`: `grep -c '^- \[~\]' SHONEN.md` = 4. `grep -c '\[x\]' SHONEN.md` = 0.
- SHONEN's evidence pointers (B1 `SKILL.md` §§Decision table/Error signatures/Checklist; B2 `LOG.md` §§round 1–3; B3 `corpus/knowledge/snapshot-history.md` §Run it; B4 `PROVINCE.md`/`cross-lane-scope.md`) are not shifted by the candidate:
  - `LOG.md`: the only hunk is `@@ -852,0 +853,29 @@` (append at EOF, after round 1–3 entries).
  - `SKILL.md`: `@@ -476 +476,30 @@`. Only the final line changes; the appended round-15 section comes after line 476, so the §Checklist pointer is unchanged.
  - `corpus/knowledge/snapshot-history.md`, `PROVINCE.md`, `cross-lane-scope.md` are not in the candidate.
  - `corpus/QUALITY.md` and `corpus/README.md` hunks are appends (`@@ -72,0 +73,15`, `@@ -177,0 +178,23`).

## 2. No phantom promotion — PASS

- Scan of every `+` line in the candidate commit for `[x]`, `[X]`, `promot`, `mint`, `certif`, `phantom` and `admit`: no `[x]` or `[X]` added. Every hit is negated or descriptive, e.g. "no promotion box is newly certified", "not a promoted serving command", "No promotion or mint" (quoting the round-14 closure), "no outside review yet".
- `corpus/SOURCES.md`: only S012 `used-by` changed (verified cell by cell: the old three knowledge paths plus `corpus/lessons/round-15.md`). Status, recheck and all other cells unchanged. S034 is an own-work row (`A1/B0/C0`, mined).
- The round-15 SCORECARD, LESSON, LOG, SKILL, QUALITY and README entries all state that SHONEN is not changed and no box is certified. Example: `corpus/lessons/round-15.md` line 7 ("Outside review is still required ... not admission or promotion").
- `.ufo/waves/round-15/integration-review.json` (committed) states that author-dispatched advice is not independent admission or promotion.

## 3. No numeric score increase — PASS

- All score statements in the committed non-advisory artifacts read calibration **7 → 7, delta 0** (SCORECARD round-15 section, `corpus/lessons/round-15.md`, LOG round 15 "Numeric calibration stays7", `ollama-evidence-replay.md` correction, QUALITY KQ18 note). Operability stays 8. No `→ 8`, `8 →`, `delta +` or other arrow with an increased value appears in the candidate's added lines.
- The guard repair is exactly two added lines in `.ufo/waves/round-14/measure.py` (`if len(declared) != unique: problems.append("duplicate case names")`), i.e. `@@ -357,0 +358,2 @@`. The parent blob is `7830045…`; the frozen pre-repair copy `.ufo/waves/round-15/frozen/measure-before.py` has blob `783004569af9072afdeb32c6eeacc462868eb76b` and SHA-256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, both matching the round-14 original recorded in the lesson. No classifier file (`tools/kama-ollama-evidence.py`) is in the commit.
- The historical receipt `.ufo/waves/round-14/acceptance.json` and `tests/ollama-evidence/cases.json` are not in the candidate, so the 51/51 denominator and recorded results are unchanged.

## 4. Non-blocking observations (evidence only, not proposed features)

1. **Qualitative "improves" wording in committed advisory files.** `.ufo/waves/round-15/build/advice/SiblingBoundary.md:68` ("Calibration — improves … The score stays 7 → 7"), `FindingExit.md:103` ("Calibration: improves … Numeric score stays 7 → 7") and `PriorCoverage.md:119` ("Improved evidence, numeric stays 7") say calibration improved. The committed SCORECARD, lesson and LOG say delta 0. No numeric value increases. The lane already records "calibration improved, score 7 → 7" in prior rounds (`LOG.md:601,690,782`; `corpus/lessons/round-13-verifier-spotcheck.md:230`), so this is consistent with the existing convention. Outside closure should decide the verdict word; these build files are author-side advice and are not admission.
2. **Inherited outside-status provenance.** The round-15 SCORECARD, LOG and README cite "Outside round14 is `ok / admitted true`" and "Outside R1 found …". That status comes from `corpus/lessons/round-14-verifier-spotcheck.md`, which labels itself "non-author integrator, @m_strong" and says it was "dispatched by the orchestrator, not the lane". Its commit `6e348e2` is authored `protocol-shokunin` with message "(integrator, hyaku)". This seat cannot verify the independence claim beyond the file text. Round-15 credits it only for R1 discovery and repeats the fixed-repertoire wording, not any round-15 admission. I confirmed R1's predicate defect independently from the frozen source: `corpus_problems` (lines 350–364) compares only `unique` with 16 and never compares `len(declared)` with `unique`.
3. **Pending append.** The round-15 SCORECARD states "Final measured revision, counts and verdict are appended after execution", and LOG says "measured revision are recorded after integration". The candidate contains no measured counts or verdict. Any later append must keep calibration 7 → 7 (delta 0), add no `[x]` to SHONEN, and cite the actual command outputs. This is a watch item for the L1 post-execution step, not a current defect.

## 5. Verdict for this attack

- SHONEN assertions: unchanged (digest-verified against HEAD and the round-5 manifest; four `[~]`, zero `[x]`).
- Phantom promotion: none found in committed non-advisory text; outside-admission wording is quoted, not re-asserted as promotion.
- Numeric score: 7 → 7 everywhere committed; no increase.
- Open items: observations 1–3 above; no change to SHONEN is required.
