# Round 59 verifier spot-check

author: hyaku closure (non-author integrator, @m_opus)

## Conformance

- Report `.ufo/reports/round-59/kama.md` is committed by `kama-shokunin` in fleet commit `f8ed0a756d43cbd40e7e62117249a10bf32c35f6`; it includes `SHONEN` and four `[~]` lines. Lane tip `f1cd775ebb57ecd5bcf02ebcc16a68dba99527fc` is present and ancestor of `master`; all cited round commit hashes checked are ancestors. Lane helper reports `ahead=0 behind=0`; remote `refs/heads/master` equals tip. Lane worktree has unrelated untracked `.ufo/scopes/` and `.ufo/waves/round-57/ClaimFalsifier/09/fixtures/`; no claim made that it is clean. Report has required sections. The dispatched prompt includes canonical round clauses and hyaku addendum. Defects: prompt says its mechanism was one batched swarm; report records 64 result rows and role mix but one incomplete artifact, no per-seat status/dead field; claims 8→8 and 7→7 are not qualifying improvements. Report notes omit individual committed LOG-round associations for every listed hash (LOG has round-59 entries, but not each tie explicitly). Status remains `ok` (real committed round work); no marker.
- Dispatch digest copied from watchdog: `2026-10-27T17:13:51-03:00 launch kama round=59 pgid=3879171 driver=hyaku-inline attempt=1`; `2026-10-27T18:12:31-03:00 complete kama round=59; hyaku-inline attempt=1`.

## Claim re-checks and axes

| Claim | Independent measurement / evidence | Axis verdict |
|---|---|---|
| C1 operability 8→8 | Re-ran `python3 tools/round59-c1-counter.py --repo . --tip aca8d0067ea25627c5015c2193c843965148bc8e --checker tools/round58-battery-exec-check.py --work /tmp/kama-c1closure` at lane tip; observed `genuine=1/1 benign=3/3 noop_rejected=13/16 errors=0 met=False` (exit 1), including N12/N14/N16 accepted. Candidate checker receipt in committed `controls/c1-candidate-final.out` reports 16/16, but R04's direct test `w1/out/R04DecoyArgv.md:46-62` demonstrates the frozen decoy route passes the checker (`runs=5 passed=5/5 ... met=True`). Counter finite behavior re-measured; semantic flaw evidence-verified. | operability: unchanged (no score change); claim not verified, hence no admission. |
| C2 calibration 7→7 | Re-ran frozen counter bytes from lane tip: `git show f1cd775...:tools/round59-c2-counter.py | python3 - --repo ... --tip f1cd775... --fleet-repo ... --fleet-ref a41c6644...` → `rows=44 mismatches=0 met=True`, `maxN=57`, latest `rejected-honest-stop`; base receipt gives `rows=44 mismatches=3 met=False`. Semantic target falsified by committed K05 static assertion and M12 eight clause deletions in lesson/wave records; the frozen predicate explicitly requires current external verdict and none is present. | calibration: unchanged; claim not verified, no discernment progress. |

SCORECARD delta review (`git diff 8f7f58c..f1cd775 -- SCORECARD.md`): scores remain operability 8/calibration 7; no capability entered. The axis scores are appropriately unchanged, though the changes do not demonstrate improvement.

## Learning gate outside spot-check

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S517 admit candidate | Admit | https://docs.python.org/3/library/sys.html#sys.setprofile | Agree | Re-opened Python 3.15.2 docs; located rule states profile events are call/return only and return occurs even with exception. Narrow support is accurately scoped; does not establish actual child output. |
| S518 admit candidate | Admit | https://man7.org/linux/man-pages/man8/ld.so.8.html | Agree | Re-opened live page; `LD_AUDIT is ignored in secure-execution mode` appears, with `$ORIGIN`/`$LIB`/`$PLATFORM` token handling. Supports claimed scope. |
| S513 reject candidate | Reject retained | https://man7.org/linux/man-pages/man8/ld.so.8.html and S512's cited `rtld-audit(7)` snapshot | Disagree | The opened loader page contains secure-execution and token rules; S513's recorded reason that its broad scope overlaps S512 is not true for those claims. S518 itself says it supersedes S513, contradicting the continued rejection. This is an unlearned gate disagreement/contradiction. |
| S200 quarantine | Reject | https://arxiv.org/abs/2312.07104 | Agree | Reopened source abstract/metadata does not contain the alleged “DOI not in Semantic Scholar” fragment; it is not a source quotation. |

The lane's additional S200 decision is evidence-verified via committed `w1/out/S05Quarantine.md`; S202/S206/S210/S211/S224/S230 were not separately sampled here. Canonical sources census command `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exited 0 and printed `kama ok`; existing W04 duplicate-URL warnings and W01 S481 tier-C-mined warning remain. Direct before/after row counts: `git show 8f7f58c:corpus/SOURCES.md | grep -cE '^ {0,3}\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|'` = 259; same at final tip = 259. No new registry rows; S517 used-by touched.

## Trend verdicts

- expansion — unchanged: 259 registry rows at both commits, no new knowledge entries, no uncovered ground admitted (lesson census and `corpus/README.md`).
- quality — improved: KQ99 is a lesson-grounded future criterion after observed C1 counterexamples; fixes do not retroactively pass either claim. (This is narrow and does not offset the claim failures.)
- discernment — harmed: independent sampling agrees on S517/S518/S200 but finds S513 reject inconsistent with reopened source and S518's superseding statement; no correction/lesson is recorded. This conflicts with the lane's own `unchanged` trend verdict and must govern closure.

## Routed defects for next round

- Correct S513 rejection versus S518 supersession; append an explicit lesson and update quality criteria so the outside disagreement is learned (append-only).
- Rebuild C1 counter/checker to reject one-call runner decoy, fixture-name oracle, and BAD_ENV source-text synthesized observations; add hostile `GIT_*` controls.
- Rebuild C2 semantic derivation and controls that fail for each dropped requirement; secure an actual non-author admit/reject spot-check before claiming discernment.
- Resolve lane leftovers `.ufo/scopes/` and `.ufo/waves/round-57/ClaimFalsifier/09/fixtures/`; keep unrelated fleet work untouched.
