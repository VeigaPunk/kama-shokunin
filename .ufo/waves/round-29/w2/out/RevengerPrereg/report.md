# RevengerPrereg — attempt-1 timeline reconstruction from immutable records (kama round-29 w2)

Seat: `kama-r29-w2-RevengerPrereg-9`. Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD detached at `513eba3ba51a142c9936553e3a85918345eb5c4c` (lane Git state untouched; read-only commands only). Scratch: `/tmp/revengerprereg-9/`. No tools installed (existing git/stat/find only).

## 1. Verified commit timeline (git log --format='%H %aI %cI %s', lane repo)

| commit | author date | committer date | subject (abbrev) |
|---|---|---|---|
| `2aa46e2481d2…` (base) | 2026-10-23T06:55:34-03:00 (09:55:34Z) | 09:55:34Z | round-28 verifier spot-check |
| `827d136546b8…` (freeze) | 2026-10-23T06:55:34-03:00 (09:55:34Z) | **2026-10-23T07:55:43-03:00 (10:55:43Z)** | round-29: C1 freeze … before any seat |
| `35b90184f638…` (controls) | 08:11:28-03:00 (11:11:28Z) | 11:11:28Z | pre-freeze control call receipts (14 seats …) before any correction row |
| `513eba3ba51a…` (data) | 09:02:52-03:00 (12:02:52Z) | 12:02:52Z | C1 data (11 appended self-assessment correction rows) … |

Ordering freeze → controls → data is as claimed. Two date observations:

- **O1** — Goal text and `controls/SUMMARY.md` both state freeze at "10:55:45Z"; git committer date is **10:55:43Z** (2 s mismatch, cosmetic).
- **O2** — `827d136`'s author date (09:55:34Z) is identical to the second with its parent `2aa46e2`'s author date, one hour before its committer date. Consistent with a jj-rewrite/rebase preserving author time [INFERENCE]; flagged as an observation, no content effect.

Frozen artifacts' mtimes precede the freeze commit: `count-c1.py` 07:54:08, `before/c1-base.json` 07:55:13, `preregistration.json` 07:55:40 (all -03). `sha256sum count-c1.py` = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` ✓ matches preregistration and goal.

Pushed-tip state: `origin/master` = `refs/heads/master` = `49f849f292c3…` ("considerthese: 2026-10-23 daily reflection", committed 09:21:19-03 — AFTER the data commit); `git merge-base --is-ancestor` confirms `513eba3b` IS an ancestor of `49f849f`. The final receipts below were cloned "of origin at 513eba3b…", i.e. 513eba3b was the pushed tip at receipt time (09:03/09:16 local). The lane is now verified at a tip that is no longer origin/master — fact, not a defect.

## 2. Controls: post-data shaping of pre-data artifacts? — NONE FOUND

Controls were committed at `35b90184` (11:11:28Z), before data (12:02:52Z).

- **C1.1 Committed blobs unchanged since.** `git status --porcelain` shows no `controls/` entries; `git diff --stat HEAD -- .ufo/waves/round-29/controls …` is empty (exit 0). Working tree == committed pre-data blobs.
- **C1.2 No data-commit knowledge.** grep over `controls/` for `513eba3|35b9018`: **no matches**. No control receipt names either round-29 commit hash.
- **C1.3 No landed-cause leakage.** grep over `controls/` for the landed rows' distinctive cause phrases (`line 29 is the kama row`, `written as if lane-relative`, `line 384 exists there`, `live re-census output`, `test-snapshot result quoted`, `quoted audit result`, `citation-provenance before-run/after-run`, `quoted gate output`): **no matches**. Matches on `MISSION.md:29` / `round-17-verifier-spotcheck.md:217–221` are the base-statement *tokens* echoed from the frozen base receipt (`before/c1-base.json`, knowable at freeze), not the landed rows' cause text.
- **C1.4 Correction rows in controls are sandbox-local.** Every control `counter.out`/receipt tip is the freeze tip `827d136546b8…` or a scratch-clone tip (`3fe6136627df`, `63329ad1c797`, `93efe2d45da5`, `1c2a351f8519`, `f9d5889b621d`, `af96283389de`, `a59f90ec1d70`, …) — never `513eba3b`. `RefPaste/counter.out`: `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip a59f90ec1d70` — the reference policy already demonstrated "meets" **pre-data, in its sandbox clone**, as `controls/SUMMARY.md` discloses. CtlSourceBounds' 16 predicted sids (`predictions.json`/`correction-rows.md`, policy label "source-text prediction") do not coincide with the landed 11-row set (e.g. predicts `Q:cda32b698f:0`, which never landed) — controls did not prefigure the exact data rows.
- **C1.5 CtlSourceBounds prediction lock is real in shape.** `REPORT-before-scoring.md` and `REPORT.md` share the pre-result hash `80f9e0d9be84…` / prediction hash `f1a477ff43b8…` as claimed; scoring (valid 9 / false 7) could not have been known at prediction time from the report's own account. (Hash equality of the two report prefixes re-verified by reading both files; the pre-scoring copy is byte-identical up to the "Actual detector output" heading.)

## 3. w1/out verdicts vs what each seat could know

Artifact timeline (mtimes, -03): w1 `first-try-spec.json` 08:00:56 / `first-try-dispatch.json` 08:01:01 (during the controls wave, before the controls commit); final `spec.json` 09:01:51, `dispatched-at.txt`/`spawn-result.txt` **09:02:03** ("Spawned 32 background agents…"), i.e. **dispatched 49 s before the data commit** (09:02:52). Earliest w1/out file: `ScribeSrcGitGrep/page.html` 09:02:41 (web fetch); **all 11 ConfirmM verdicts postdate the data commit**: ConfirmM02 09:03:19 → ConfirmM01 09:10:51. Late seats: `ReviewCounterCode/findings.md` 09:15:37, `ExecGateRegistryV2/REPORT.md` 09:32:40, `ScribeInstrumentRegistry/REPORT.md` 09:33:04.

- **W1.1 No reference-to-future-receipt anachronism.** grep over all of `w1/out` for `round-29/(final|mined|repairs|before|count-c1|preregistration|w2)` (31 matches, all inspected): references are only to pre-data artifacts (`before/c1-base.json`, `count-c1.py`, `preregistration.json`, `controls/…`, `repairs/echo-exit2/…`). **No w1 file references `final/` receipts** (`c1-513eba3b*.json/out`, cleanenv at 09:16:07), `mined/patched-selftest-v2.out` / `mined/survivor-recheck.out` (09:08:48), or this wave's `w2/`. No w1 seat cites a receipt created after it ran.
- **W1.2 ConfirmM02 (fastest turnaround, 76 s) is genuine.** Dispatch 09:02:03.420 → `verdict.json` 09:03:19.154 / `REPORT.md` 09:03:19.156 / `advice/ConfirmM02.md` 09:03:19.156. I re-ran its quoted command `git blame -L 20,20 --line-porcelain 2aa46e24 -- SCORECARD.md`: output byte-identical to the verdict's quotation (`ea72c3eae4…`, author/committer-time 1791981983, `previous ed135b3cb8…`, round-3 summary, full line-20 text). The evidence quoted is real; the seat was merely fast, not fabricated. Speed itself (76 s incl. agent boot) is noted as an observation only.
- **W1.3 Data commit cites its confirmers prospectively — the one true timeline anomaly.** The landed SCORECARD.md section (diff in `513eba3b`, file `SCORECARD.md` @@ -1439,3 +1439,26) states: *"the wave-1 Confirm seats check each one independently (`.ufo/waves/round-29/w1/out/ConfirmM01..11/`)"* — committed 09:02:52, when `w1/out/` contained only three scribes' web fetches (09:02:41+); `ConfirmM01/`–`ConfirmM11/` were created 09:03:19–09:10:51, i.e. **27 s to 8 min after the commit that names them as existing checks**. The verification did subsequently happen and its artifacts are consistent with the rows (each ConfirmMXX sid matches a landed row; spot-re-verification of ConfirmM02 above), but the commit's prose asserts a completed independent check that at commit time did not exist. Severity: low for C1's numbers (the receipt `met True` line does not depend on the Confirm seats), moderate for the narrative.
- **W1.4 Wave-1 was re-planned mid-flight, coherently.** First-try spec (08:00:56, 38 seats) contained `ExecEchoRecheckExit2`, `ExecMinedMistake`, `ScribeLessonPreamble`, `ScribeCalibCriterion`, `RecallC/D`, `PrecisionPHNTQ`; final spec (09:01:51, 32 seats) dropped the executors and added `ReviewEchoExit2` + `MutateTimeCheck`. This matches the immutable record: the L1 itself produced `repairs/echo-exit2/{existing.json,receipt.txt}` (mtimes 09:00:06/09:00:07; byte-identical to the `513eba3b` blobs, sha256 `6048be3e…`/`ca3d163b…` re-verified, sentinel 190 ms before receipt) and the mined-fix receipts `mined/orig-*.out`, `mined/patched-*.out` (09:00:49–09:01:06), then had wave seats review that finished work post-data. `ReviewEchoExit2`'s mtime claims (12:00:06.951Z / 12:00:07.142Z) reproduce exactly from stat.
- **W1.5 Mined-fix receipts predate the commit that carries them.** `mined/patched-*.out` (09:01:06) predate `513eba3b` (09:02:52) which commits `tools/prereg-time-check.py`; `MutateTimeCheck` (probe files 09:04:50–09:05:25) then attacked the committed patch, capturing `git diff 35b90184 513eba3b` (its `snapshot.json` head = `513eba3ba…`). Sequence consistent: uncommitted patch → receipts → commit → independent attack. `mined/patched-selftest-v2.out` + `mined/survivor-recheck.out` (09:08:48) are post-w1-start additions not referenced by any w1 file (consistent with an L1-side follow-up).

## 4. Final receipts at the measured tip

- `final/c1-513eba3b.out` (mtime 09:03:11): `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a` — exactly the goal's quoted receipt line.
- `final/c1-513eba3b-cleanenv.out` (09:16:07) adds `env -i PATH=/usr/bin:/bin HOME=$HOME; clone of origin at 513eba3ba51a…; counter sha256 fe11d599…383`; `diff` of the two `.json` receipts: **identical (exit 0)**; receipt fields `met: true`, `correction_rows: 11`, `false_corrections: []`, `counter_sha256 fe11d599…383`, base `2aa46e24…`.
- Landed rows: exactly 11 `SA29:…` rows in the preregistered format (first cell `SA29:<sid>`, last cell observed value; extra middle columns line/class/token/W/cause — not prohibited by the predicate, which pins only first and last cells). sid set == the 11 mismatches in the frozen base receipt (cross-checked against `before/c1-base.json` excerpts in ConfirmM01/M04/M05 verdicts and `CtlBaseTree/base_failures.jsonl`).
- Uncommitted attempt-1 leftovers do **not** touch the landed data: `git diff -- SCORECARD.md` = 40 insertions, 0 deletions, a new section appended after the corrections table; the corrections rows themselves are byte-stable in the working tree.

## 5. Verdict summary

| # | Finding | Verdict | Confidence |
|---|---|---|---|
| F1 | Data commit's SCORECARD prose cites `w1/out/ConfirmM01..11/` as checks "checked", 27 s–8 min before those outputs existed | **Anomaly (prospective citation)** — subsequent artifacts are real and consistent | High (git commit date vs mtimes) |
| F2 | w1 dispatched 49 s pre-data; ConfirmM02 full cycle in 76 s; verdict/REPORT 2 ms apart | Observation only — quoted evidence re-verified byte-identical | High |
| F3 | Post-data shaping of pre-data control receipts | **None found** (blobs unchanged; no hash/cause leakage; all control tips sandbox-local) | High |
| F4 | w1 seats referencing receipts created after they ran | **None found** (no w1 reference to `final/`, mined v2, survivor, cleanenv, or `w2/`) | High |
| F5 | Freeze record says 10:55:45Z; git says 10:55:43Z; author date == parent's author second | Cosmetic doc mismatch + jj-style author/committer split [INFERENCE] | High / Medium |
| F6 | Final vs cleanenv receipts identical; receipt string matches goal; counter sha matches; landed rows == base-receipt mismatch set | Confirmed | High |

Evidence anchors: lane repo absolute paths as cited; `git log`/`git show`/`git diff`/`git merge-base` outputs quoted above; `stat`/`find` mtimes at 2026-10-23 (host tz -03:00); scratch copy of the data diff at `/tmp/revengerprereg-9/data-diff.txt`. Tooling: none installed; used preinstalled git/coreutils only (pacman untouched, per host-wide pause).
