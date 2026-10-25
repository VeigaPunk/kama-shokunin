# kama — round-29 verifier spot-check (closure)

author: hyaku closure (non-author integrator, @m_kfc)
date: 2026-10-23
lane tip verified: `7f595a3bf8027e5e48cac3634e79990df513c7ab` (local == origin/master, ahead=0)
base: `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` · report: `.ufo/reports/round-29/kama.md` @ `9596e035eb5c741662e1b73c8a8e8cc3dbe0f6ed` (author kama-shokunin)
dispatch digest (watchdog.log lines 919/933/944/958, verbatim): launch attempt=1 07:41:43-03:00 pgid=447289; lane-dead-no-report 15:03:19-03:00 (stale phase-4 author, orchestrator died ~09:30 -03); launch attempt=2 15:10:23-03:00 pgid=93338; complete attempt=2 16:12:49-03:00.

## 1. Step-1 conformance

| Check | Command | Result |
|---|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-29/kama.md` | `kama-shokunin 9596e03…` PASS |
| Required sections + SHONEN heading (4 boxes, all `[~]` with pointers) | seat PromptFidR29 line-audit of report | PASS, in contract order |
| All cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <hash> master` for 827d1365, 35b90184, 513eba3b, 6de225c2, 227dd1ee, 7f595a3b | PASS (6/6) |
| Pushed, no unpushed lane work | `jj-lane.sh state` → `ahead=0 behind=0`; `git ls-remote origin refs/heads/master` = 7f595a3b… | PASS |
| Prompt carries template contract | seat PromptFidR29 vs `templates/round-prompt.md` | all 10 items present (5 round-level + 5 child-lane); prompt committed by kama-shokunin |
| No uncommitted round work | `git status --porcelain` | **DEFECT**: 2 untracked files (see Routed 1) |
| Census at tip | `scripts/sources-census.sh validate --root … kama` | exit 0, 177 rows, only pre-existing W04 duplicate-URL warnings — matches report end state |
| Marker predicate | report names real work, hashes, receipts | real report, not a marker |

## 2. Claim re-derivation (C1, calibration — re-measured, not only evidence-read)

Counter bytes frozen: `git show 827d1365:.ufo/waves/round-29/count-c1.py | sha256sum` = `git show 7f595a3bf:…` = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (identical at freeze and tip).

Frozen counter run by this closure in fresh local clones (`/tmp/kama-r29-closure/{base,data,tip}`):

- base 2aa46e24: `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2` — byte-identical to committed `.ufo/waves/round-29/before/c1-base.out`.
- data 513eba3b: `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a` — byte-identical to committed `final/c1-513eba3b.out`.
- tip 7f595a3bf: same fields `met True` — matches committed `final/c1-6de225c2.out` (measured at 6de225c2).

Independent structure checks: 11 `| SA29:` correction rows under `## Round 29 — self-assessment corrections` (SCORECARD.md:1443, awk count = 11); SCORECARD diff base→tip is +65/−0 (append-only); SHONEN 1+/1− (disclosed box-2 wording line); QUALITY +14/0 (KQ38, KQ39); README +16/0 (round-29 coverage row); SOURCES +4/0 (S174–S177); lesson +180/0; LOG +67/−0. Commit order pre-data: 827d1365 (freeze) → 35b90184 (14 control receipts) → 513eba3b (correction rows) — linear ancestry, controls committed before any data.

Gate-standard treatment: the frozen counter is the claim's instrument; per §Gate standard closure consequence its committed evidence was verified (receipts byte-match my fresh runs; preregistration predates all seats and data; counter sha unchanged freeze→tip; 14 pre-data control receipts at 35b90184 all fail the target per committed `controls/SUMMARY.md`) **and** the claim was independently re-measured by this closure with the frozen bytes (commands above). Claim verdict: **verified**.

Round-28 routed repairs (items 1–9): spot-verified — KQ38/KQ39 rows present (QUALITY.md:283,289), echo-recheck exit-2 receipt committed, SHONEN box-2 wording matches `controls-frozen.json` reading, report states the round-28 A1 post-data projection fact, gate/instrument registry receipts in `w1/out/`.

Disclosed items from the orchestrator, all verified resolved in the landed tree:

- VerifyMistakeFix D3: landed `tools/prereg-time-check.py` selftest carries the mutant-killing case `flag: space-separated seconds-precision time 7 s after commit` plus the `~HH:MMZ` A1-form case. Closure re-ran all three MutateTimeCheck mutants against the landed tool in `/tmp`: `m02 selftest_exit=1 KILLED`, `m05 selftest_exit=1 KILLED`, `m07s selftest_exit=1 KILLED` (each fails exactly the 7-second case); landed tool selftest: 13 `[PASS]`, 0 `[FAIL]`, `SELFTEST PASS`, exit 0. Committed receipts agree (`mined/patched-75b78bb4.out` exit 1 flagging `2026-10-23 ~08:45Z later than commit by 404s`; `patched-d8bf1804.out` exit 0; `patched-selftest-v2.out` 13/0).
- D1/D2: lesson timestamps equal git committer metadata exactly (827d1365=10:55:43Z, 35b90184=11:11:28Z, 513eba3b=12:02:52Z); LOG.md:1858 now reads "13 cases PASS plus the SELFTEST PASS aggregate line"; `mined/patched-513eba3b.out` records the by-design exit 1 on the round-28 frozen preregistration. The stale "working-tree tool" clause the VerifyLogFreshness seat flagged is also corrected in the landed LOG ("landed tool at the round's tip").
- CensusRun D1: census exit 0 at tip (this closure ran it; row count 177 = committed `final/census-end.out`; start receipt 173 rows exit 0 committed with the freeze).

## 3. Per-axis verdicts

- **calibration: improved** — C1 re-measured met True (unresolved 11→0) at data commit and tip under the frozen counter; SCORECARD carries the 11 observed-value correction rows; score stays 7→7 by the no-self-promotion rule (recorded in SCORECARD round-29 row). Bounded reading (CriticAxisFit) disclosed in report and lesson; accepted as the honest scope: evidence-resolution defects recorded, not proven wrong judgments.
- **operability: unchanged** — no serving/runtime surface touched; `tools/` delta is the timestamp falsifier only; no capability rows claimed or added (verified in SCORECARD diff).
- No other axis touched; lane write scope respected (fleet-root `git status` shows only driver state files; no kama artifacts misrooted; l0-questions append committed by kama-shokunin @7400d67).

## 4. Discernment spot-check (LEARNING.md §Discernment is checked from outside)

SOURCES rows re-opened by seat DiscernSpotR29 with live page fetches (curl, 2026-10-23) against git-scm.com; teaches cells additionally re-read verbatim by this closure.

| Item | Lane decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| S174 Gate quote "last modified the line" + "commit information for each line, not just the first time a commit is referenced" | admit (row S174) | git-blame page §DESCRIPTION/§--line-porcelain (seat fetch; installed git 2.56.0 man agrees) | **agree** | both fragments verbatim on page; ≤25 words each |
| S175 Gate quote "and exit with status 0 if true, or with status 1 if not." | admit (row S175) | git-merge-base page §--is-ancestor | **agree** | verbatim, 13 words |
| S176 Gate quotes "…search blobs in the given trees." / "If it matches, the path is ignored." | admit (row S176) | git-grep page `<tree>…`; gitglossary `exclude` | **agree** | verbatim, plural "trees"; glossary signature `!`/`^` |
| S177 Gate quote "committer date, UNIX timestamp" | admit (row S177) | pretty-formats page `%ct` | **agree** | verbatim, 4 words |
| S174 `teaches` cell marked "(§DESCRIPTION, verbatim)" | admit as written | this closure's `curl https://git-scm.com/docs/git-blame` | **disagree** | page reads "Annotates each line in the **given** file…"; the landed cell drops "given", so the verbatim label is false (fragment itself points at the right sentence) |
| S176 `teaches` cell singular "given tree" + `:(exclude)` example | wave-2 decision "fix pre-landing: 'tree' → 'trees'…" | seat SrcS176 report + landed row | **disagree (record mismatch)** | SrcS176 classifies the cell as an acceptable paraphrase/composition, but the wave-2 decision record claims the singular was fixed; the landed cell still says "given tree" — cell and decision record must be reconciled |
| Admit: ConfirmM02/M04 cause cells overstated ("no committed file at W holds this text") | admit, corrected by appended note | `w1/out/ConfirmM02/verdict.json`, ConfirmM04; trees at ea72c3ae/40660352; SCORECARD appended note :1490–1493 | **agree** | the spans did sit at W in LOG.md/lessons (Q-rule excluded files); the note is the right append-only repair; minor: the note omits the `corpus/lessons/round-2.md:49` hit |
| Reject: amend counter/predicate after CriticAxisFit | reject (frozen predicate) | `w1/out/CriticAxisFit/critique.md`, preregistration.json | **agree** | kill rule freezes the predicate; the objection was accepted as the reading of what C1 shows, which is the correct way to absorb it |

Census validator run by this closure: exit 0.

## 5. Trend verdicts

- **expansion: improved** — independent grade per LEARNING.md's observable: one net-new admitted `knowledge/` entry (`self-assessment-at-writing.md`) on ground the coverage map did not previously hold (round-29 README coverage row names it as new; ScoutHeldRules: no prior lane instrument covered writing-revision statement checks), `source:` citing mined rows S174–S177. Note: the lane self-reported `unchanged` under a stricter serving-surface reading; this closure grades by LEARNING.md's corpus observable.
- **quality: improved** — 11 false self-assessment statements now carry observed values (re-measured); KQ38/KQ39 admission criteria added with lesson citations; round-28 routed repairs landed; the timestamp falsifier is now fail-capable on the exact mistake class that produced the round-28 rejection (exit 1 at 75b78bb4, exit 0 at d8bf1804, 13-case selftest, 3/3 mutants killed — all re-run by this closure).
- **discernment: improved** — outside spot-check agrees with the gate on the sampled admit and reject; seat disagreements this round were learned into fixes (D1 number corrected to 13, D2 receipt added, D3 case landed and mutants verified dead); the two residual disagreements above are routed below, keeping the loop honest.

## 6. Routed defects for the lane (next round)

1. **Uncommitted round work**: `.ufo/waves/round-29/w2/VerifyLogFreshness.md` and `.ufo/waves/round-29/w2/out/VerifyLogFreshness/report.md` are untracked; the tip commit 7f595a3b committed only the seat's `evidence/` directory. Commit the report (or delete it if the evidence dir supersedes it) under the round-30 entry.
2. **LOG.md does not name the attempt-2 landed hashes**: `6de225c289b7…` and `227dd1eeff95…` appear nowhere in LOG.md; the report's Landed-changes ties them to "LOG.md §Round 29 attempt 2 entry", which names neither. Append a hash-naming note (append-only).
3. **S174 teaches verbatim mislabel**: drop "(§DESCRIPTION, verbatim)" or restore "given" in the quote (page: "Annotates each line in the given file…").
4. **S176 teaches vs decision-record mismatch**: reconcile the landed cell ("given tree", `:(exclude)` composition) with the wave-2 SrcS176 "fix pre-landing" decision (which records "tree → trees"); either edit the cell or append a decision-record correction.
5. Minor: SCORECARD :1490–1493 appended note omits the `corpus/lessons/round-2.md:49` location of the M02 span; completeness only.

No SHONEN box is `[x]`-checkable by this closure within round scope; box 2's corrected wording was independently verified against `controls-frozen.json` by the w2 VerifyShonenBox2 seat (lane-dispatched, so it cannot supply the non-author mark — promotion remains operator-owned).

Tool installs by this closure and its seats: none (curl, system git 2.56.0, system python3 only).
