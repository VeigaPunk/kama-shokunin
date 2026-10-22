Verdict: defect found. Two small, fixable wording defects, one in a committed lesson and one in the committed KQ36 row. The repair opened no harm to code, coverage, history or the exit contract.

# CriticC1NoNewHarm: round 25, attempt 2, wave 2 (falsify)

Seat: KamaR25a2.CriticC1NoNewHarm (fresh seat, critic, leaf, read-only on lane production files).
Target: every C1-related change from efe58e96 to fa3b62ae6475d111eb466d79af616aeebb08bbb9, plus the round-24 spot-check routed defects (`corpus/lessons/round-24-verifier-spotcheck.md:147-160`).
Attack: did the repair-first C1 open a new harm? I checked for a changed exit contract, dropped coverage, a hidden survivor, a history rewrite, a routed defect that was contradicted or claimed as solved beyond its evidence, and PM08 credit through M02.
No llama-server child was started. No tool was installed or updated. I found `/usr/bin/time` absent and used the bash `time` keyword instead.

## Harm list

| # | Harm | Kind | Impacted axes | Smallest safe correction |
|---|---|---|---|---|
| H1 | The committed lesson says the SKILL registry row records M17's survival. It does not. | false provenance, fixable | quality, discernment (and KQ36 self-compliance) | Add the survival to the `SKILL.md:888` pinned-values cell, or change the lesson cell to name the places that do say it |
| H2 | The committed KQ36 row says the efe58e96 instrument exits 2 "after ten mutants". Nine ran. | miscount in a production file, fixable | quality | Change "after ten mutants" to "after nine mutants (M01-M07, M09, M10; no M08 exists)" |

Both are wording defects. Neither one changes the C1 value or any measured outcome.

### H1: lesson claims a SKILL row says something it does not say

- Committed `corpus/lessons/round-25.md:49` (bytes at fa3b62ae), Mistakes row "survival hidden by a same-line re-anchor", fix column: "the instrument docstring and SKILL registry row now say M17 survives and why".
- `SKILL.md:888` at fa3b62ae, "Retained isolation mutation experiment" row, pinned-values cell, quoted whole: "28 retained literals since round 25 (M11 and M17 re-anchored; M33 is the second call site of the M17 refusal), 4 retired IDs without reuse; `RETIRED` explains their removed component; unchanged isolation elements remain explicit". It has no survival statement and no reason. `grep -n 'M17\|M33' SKILL.md` finds only lines 882, 888 and 1006, and none of them mentions survival.
- The survival is stated elsewhere: the instrument docstring (`tests/report-audit/isolation-mutants.py:33-39` at fa3b62ae), `LOG.md:1648-1650`, `SCORECARD.md:1278-1281`, the SCORECARD C1 row (`SCORECARD.md:1260`) and `corpus/QUALITY.md:203`.
- Why it matters: the lesson presents this row as the fix for the "survival hidden" mistake. KQ36, added in the same commit, asks that "a re-anchor names, per mutant, whether its last recorded kill still holds". The live registry row is where an agent reads the instrument's contract, and it still shows only "re-anchored". This is the same "same-line re-anchor hides a moved kill" pattern that the round's own mistake row is about.
- Correction (one cell, no target change): append to the `SKILL.md:888` pinned-values cell: "M17 survives the grid since round 24 (its reachable path moved to `bare_objects()`, where F13 now kills M33); M20 survives as at round 23". The alternative is to replace "and SKILL registry row" in `round-25.md:49` with "`LOG.md:1648-1650` and `SCORECARD.md:1278-1281`".

### H2: "after ten mutants" is nine

- Committed `corpus/QUALITY.md:203` (KQ36, "Shown able to fail"): `exits 2 at efe58e96 (after ten mutants)`. I extracted this with `sed -n 203p corpus/QUALITY.md | grep -o 'exits 2 at efe58e96[^)]*)'`, exit 0.
- At efe58e96 the MUTANTS order is `M01 M02 M03 M04 M05 M06 M07 M09 M10 M11 ...`. I listed it with `git show efe58e96:tests/report-audit/isolation-mutants.py | grep -o '("M[0-9][0-9]-[a-z0-9-]*"'`. No M08 exists: the round-23 `final/mutants.json` rows also skip M08, and `grep M08 tests/report-audit/isolation-mutants.py` returns nothing. The instrument stops on M11 (`a2-build/out/ExecC1BaseRun/efe58e96-instrument.stderr`: `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`). That makes nine mutants applied before the stop, not ten.
- The source of the miscount is `a2-build/advice/ExecC1BaseRun.md:3,54,80` ("ten mutants (M01–M10)"). The errata (`errata-attempt-2.json:13`) and `LOG.md:1644-1645` say "M01-M10", which is a correct range. Only the count is wrong.
- Correction: change it to "after nine mutants (M01-M07, M09, M10)".

## What holds (checked, no harm)

1. **Exit contract unchanged.** `git diff efe58e96 fa3b62ae -- tests tools/report-landing-audit.py` touches only `tests/report-audit/isolation-mutants.py`. Its hunks are docstring lines, comments and MUTANTS tuples (`1fc41e3`: +30/-3; `fa3b62a`: +7 docstring lines). No executable line changed. The auditor `tools/report-landing-audit.py` and the grid are byte-unchanged from efe58e96 to fa3b62ae (they are absent from `git diff --stat efe58e96 fa3b62ae -- tools tests`, which lists only `isolation-mutants.py` and the new `kama-context-capacity.py`). The docstring at `isolation-mutants.py:41-44` still states the exit contract: 0 means pristine passed and every mutant ran, 2 means could not evaluate.
2. **Registered count at every post-repair revision.** I extracted committed trees with `git archive` into scratch and ran the C1 command verbatim (`out/CriticC1NoNewHarm/static-count.txt`):
   - efe58e96: `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`, exit 0
   - 1fc41e34: `registered 28 stale 0 []`, exit 0
   - fa3b62ae: `registered 28 stale 0 []`, exit 0
   - 46be41cf (current master, which adds only report-draft and falsify-wave files): `registered 28 stale 0 []`, exit 0
3. **No dropped coverage.** I compared per-mutant killing rows between the round-23 full run (`.ufo/waves/round-23/final/mutants.json`) and the round-25 run (`final/c1/c1-tip-mutants.json`); output is in `out/CriticC1NoNewHarm/kill-rows-r23-vs-r25.txt`. The only differences are:
   - M17 lost F13. F13 now kills M33, so the row still has a killing mutant.
   - M02 gained F06.
   - M14, M22, M27 and M29 are absent. They were retired in round 24, not round 25.

   No grid row that had a killing mutant before round 25 lost it. Ids M01-M32 that are not retired keep their round-23 rows, except M17.
4. **No hidden survivor.** The survivors are M17 and M20.
   - M20 already survived at round 23 (`LOG.md:1396`, `corpus/lessons/round-23.md:120`, `SCORECARD.md:1166`), so it is not new.
   - M17 is new. It is disclosed in the instrument docstring, `LOG.md:1648`, `SCORECARD.md:1260,1278`, `QUALITY.md:203`, the lesson and the report draft. The only gap is the SKILL row (H1).
5. **M17 is an equivalent mutant (counterexample attempt failed).** If any production input could reach the `lookup()` refusal, M17 surviving would be a grid gap rather than an equivalent mutant. The only non-test `lookup()` call without a peel is `tools/report-landing-audit.py:538` (`lookup(stores, full_tokens)`). Its tokens come from `FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")` (`:90`), so it only ever sees lowercase 40-hex tokens. The self-test calls at `:1170-1174` use an ambiguous short prefix, which returns before the check, or a full id.
   - Probe (`out/CriticC1NoNewHarm/ref-shadow-probe.txt`, git 2.56.0, scratch repository): with `refs/heads/<A>` and `refs/tags/<A>` both pointing at a different commit B, `git cat-file --batch-check` resolves the 40-hex `<A>` to A itself, and a 12-hex prefix of A also resolves to A. Only a ref whose name equals the token (`deadbeef`) resolves to the ref target B, and that is the abbreviation path through `bare_objects()` and M33. Exit 0.
   - So, for git 2.56.0, the `lookup()` refusal is unreachable in production and M17 cannot be killed. [INFERENCE] The same holds for other git versions from 2.45 up, because git treats a full-length hex name as an object id before it consults refs; only 2.56.0 was probed. This matches the docstring's own [INFERENCE] at `isolation-mutants.py:36-39`.
   - Not retiring M17 follows preregistration non-narrowing rule 2 (retire only with a revenger proof). Keeping the round-23 line for M17 and giving the live site a new id satisfies rules 1 and 3 by text.
   - Tradeoff for the judge, not a defect: the id that carried the round-23 F13 kill now points at a likely equivalent mutant, and the new id M33 carries the kill. The opposite assignment would have kept M17's kill history but moved its line. The choice is disclosed.
6. **No id reuse inside the registered instrument.** M33 is new to `isolation-mutants.py` and to the RETIRED list. The short label "M33" was used once before, in a seat-local harness (`.ufo/waves/round-21/falsify/out/C1SelftestReview/mutation-harness.py:151`, `M33-now-fallback-removed`). That was a different instrument and was never registered. Full ids differ, so this is not a reuse. A reader who abbreviates to "M33" should name the instrument.
7. **No history rewrite.**
   - `git reflog show master` lists only linear "export from jj" fast-forwards: 147f5bd → efe58e9 → 5388b7c → 1fc41e3 → 5ea4fc4 → c808ba0 → 46fb04b → 5c95c8f → fa3b62a → 46be41c.
   - `jj --ignore-working-copy op log` shows only snapshot, commit, point-bookmark and push operations. There are no abandon, rebase or squash operations.
   - `git merge-base --is-ancestor` holds for efe58e96 and for 147f5bdd against fa3b62ae.
   - No round-20 to round-24 path and no `.ufo/reports/` path is in `git diff --name-only efe58e96 fa3b62ae`.
   - `LOG.md` and `SCORECARD.md` show zero deleted lines in `git diff --numstat`. Only `SKILL.md` (7), `corpus/SOURCES.md` (1, the S060 used-by change) and `isolation-mutants.py` (3) delete lines.
   - `LOG.md:1501-1502` keeps its bytes. The correction is an appended reading at `LOG.md:1667-1670`.
8. **PM08 gets no credit through M02.** M02 deletes `"--no-lazy-fetch",` (`isolation-mutants.py:61`), which is the same flag the PM08 note concerns (`tools/report-landing-audit.py:138`; `tests/report-audit/promisor-mutants.py:57-64,424-436`). Since round 23, M02 is also killed by F06-lazy-fetch-command (the kill-row diff in item 3). Even so, round-25 text never credits PM08:
   - `corpus/lessons/round-25.md:62-63` (fa3b62ae bytes) says "An M02 kill is not PM08 credit."
   - `SKILL.md:1049-1051` says a legacy M02 result does not establish present PM08 behaviour.
   - The new `SKILL.md:887` cell says "PM08 is a manual review-only note, unexecuted, uncredited".
   - `SKILL.md:992` says "PM08 rests on uncredited manual source inspection (not settled evidence; corrected in round 25)".
   - The preregistration `not_claimed` field excludes PM08 execution credit, and the promisor self-test still fails if PM08 is credited (`promisor-mutants.py:1424-1429`).
9. **Routed defects: none contradicted, none claimed as fully solved.**
   - Defect 1: no round-25 text turns amended 47/47 into original success. A scan of added lines for `47/47` finds nothing. No round-24 file was edited.
   - Defect 2: only the M-series anchors are claimed (lesson `:58`, "the M-series anchors are repaired by C1"). The filed critic text at `SCORECARD.md:1270` says "This repairs only the M-series portion of routed defect 2; PM08 remains outside the claim." The measurement gap stays visible: M17 survives and is disclosed.
   - Defect 3: the locator paths exist as stated. `.ufo/waves/round-24/fixes/docs/ScribeLesson/` holds six files, including `supersession-index.json`, in both the working tree and fa3b62ae. `falsify/out/ConnSources/verify.txt` is 7052 bytes on disk and in the git object. Neither stated non-existent path exists. The fleet report line is `/home/vgpnk/Projects/shokunin/.ufo/reports/round-24/kama.md:16`, as the lesson says.
   - Defect 4: no round-25 text claims no-effects, backend identity, continuous floor or full isolation. The only added match for "floor" is a llama.cpp `--fit-ctx` floor in the C2 entry.
   - Defect 5: R23-H2 stays operator-owned (preregistration `open_l0`, lesson routed item 5).

## Notes for the L1 and the judge (not harms)

- **Restating routed defects drops two items.** Lesson routed item 3 (`round-25.md:64-72` at fa3b62ae) restates "locator corrections" and "append lineage" but leaves out the routed "original-hash gaps". The round-24 report's own wording at `.ufo/reports/round-24/kama.md:16` is "no prior original-SHA proof". Item 4 (`:73-74`) leaves out "continuous-floor". Neither is contradicted. Adding both words would make the restatement complete.
- **Report-draft wording.** `report-draft.md:13-15` says C1 "Repairs the round-24 spot-check's routed defect 2 (stale M-series instrument)". The routed defect covers "stale PM08/registered mutation semantics", and C1 repairs only the M-series anchor part. The safer wording is "repairs the M-series anchor portion of routed defect 2; PM08 stays outside the claim", matching `SCORECARD.md:1270`.
- **PM08 wording edit versus "separately authorized future work".** Routed defect 2 says to correct stale PM08 semantics "only through separately authorized future work". The round-25 PM08 wording edits (`SKILL.md:887,992`) are not a registered claim or amendment item, and I found no authorization record (`grep authoriz` over the round-25 dispatch, payload, preregistration and amendments finds only the C2 fixture-authorization text). [INFERENCE] The round itself is the future work. The edits only remove overclaims ("static-only", "settled") and claim no credit, so the judge must decide whether this needs separate authorization; it is not a harm to the measured state.
- **KQ36 at the landed tip.** The SCORECARD C1 row names 1fc41e34 as the measured commit, and `report-draft.md:67-68` carries the `LANE_TIP` placeholder. KQ36 rejects "the re-run uses a revision other than the landed tip". The static command already prints `registered 28 stale 0 []` at fa3b62ae and at 46be41cf (item 2). The L1 still has to paste the re-run at the final landed tip after the wave-2 commits.

## Full instrument run at fa3b62ae (supporting, not the claim value)

Command, from my own clone at fa3b62ae (`git rev-parse HEAD` printed `fa3b62ae6475d111eb466d79af616aeebb08bbb9`, clean tree): `python3 tests/report-audit/isolation-mutants.py --json`, started 2026-10-22T10:10Z. A first launch failed at once with exit 127 because `/usr/bin/time` is not installed. That launch ran nothing, and I relaunched with the bash `time` keyword. Result: pending at the time this report was written; see the update below if one is present. Unrun means unverified. Until then, the "unchanged behaviour at fa3b62ae" statement rests on item 1: no executable line, auditor byte or grid byte changed between 1fc41e34 and fa3b62ae.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/CriticC1NoNewHarm.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/CriticC1NoNewHarm/static-count.txt`
- `.ufo/waves/round-25/a2-falsify/out/CriticC1NoNewHarm/kill-rows-r23-vs-r25.txt`
- `.ufo/waves/round-25/a2-falsify/out/CriticC1NoNewHarm/ref-shadow-probe.txt`
- Scratch only, under `/fast/scratch/hyaku/kama-r25a2w2/CriticC1NoNewHarm/`: `clone/` (own clone at fa3b62ae), `t-<rev>/` archive extracts, `refprobe/`, and the `full-tip.*` run files.

Report: .ufo/waves/round-25/a2-falsify/advice/CriticC1NoNewHarm.md
