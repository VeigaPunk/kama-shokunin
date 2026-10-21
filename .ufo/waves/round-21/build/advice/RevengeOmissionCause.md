VERDICT: partial - Omissions are deliberate carry-forward scoping: build and attempt-1 commits were relabelled "reused" and left out of Landed; not memory, not pre-commit timing, not "final-only"; the contract covers every round landing, so the audit flags stand.

# RevengeOmissionCause — why r18 and r20 Landed omitted round commits

Read-only seat. Lane not modified; no installs or updates; no scratch created. Lane HEAD a29bb84 (2026-10-21). Command outputs and exits: `.ufo/waves/round-21/build/out/RevengeOmissionCause/evidence.md`.

## Cause (evidence-backed)
Landed lists only the closure step's own commits: from the first commit that acts on falsify findings to HEAD. Earlier round commits are moved to Work performed as "reused" or cited by path, although the lane's LOG records them as landed.
- **r18** (fleet `23bdc3f`, 02:39:12). Landed = `0c75c61..1b85a24` (4). Omitted `c6dc46f` and `1c325b2` (attempt 1; LOG.md:1086 "Landed implementation c6dc46f") and checkpoint `101f399` (subject ends "unadmitted"). Report l.26-27: "Reused after re-verification: implementation commits c6dc46f / 1c325b2"; l.19 names the checkpoint.
- **r20** (fleet `04eb5d2`, 07:13:14). Landed = `c7311039..7a6bc911` (5). Omitted `33a6777` and `0957ce61` (LOG.md:1204 "Work/frozen population landed 33a6777"; LOG.md:1206 "measured 0957ce61"; report l.7 "Reused the committed R20 implementation/frozen population … at 0957ce61"; l.10 cites SKILL.md:652-656 at 0957ce61). Also omitted `92b14625` and `846e366d`: no full or short hash anywhere in the report; described as "validated falsify wave" and "accounted in falsify/…".
- The window opens where falsify findings first act. r20 `c7311039` integrates the 73 reports; `92b14625` and `846e366d` (5 and 4 files; subjects "validate falsify wave", "record falsify wave assignments") precede it. r18 `0c75c61` is the first fix commit after checkpoint `101f399`, which carried the attempt-1 falsify advice.

## Hypotheses
| Hypothesis | Verdict | Evidence |
|---|---|---|
| Written from memory | Refuted for Landed; true for one Work citation | All 9 Landed hashes exist and are ancestors of HEAD; each bullet matches its commit's files (04de7a87 adds runs/c7311039; 9add96e4 adds runs/04de7a87; 3ec5ea68 adds runs/9add96e4; 7a6bc911 = LOG.md +2). Defect: r20 l.7 `0957ce619789d13d894ef21bc863486bcb35b56c` is no object; it is 15 hex of 0957ce61 + 25 hex of 33a6777. |
| Written before later commits | Refuted for both | r18: last cited 1b85a24 at 02:05:22, report 02:39:12, next kama commit 7229fa9 at 02:55:06 (round 19). r20: last 7a6bc911 at 07:10:48, report 07:13:14, next a29bb84 at 07:24:53 (round 21). One add-commit per report in fleet history. Audit post_report=0 for both. |
| Limited to "final" commits | Refuted as stated | Landed has 5 (r20) and 4 (r18) commits, including failed-run commits 04de7a87 and c7311039. The rule is the closure step, not the last commit. |
| Deliberate carry-forward framing | Supported; intent [INFERENCE] | Explicit "Reused" wording (r18 l.26-27; r20 l.7). LOG partitions: r20 LOG.md:1204-1227 (build) vs 1239-1252 (wave-2); r18 LOG.md:1084 (attempt 1) vs 1103 (attempt 2). Watchdog treats r18 attempts 1-2 as "retry same round" (watchdog.log:536-537). |

## Comparators
- Not the habit: r17 Landed lists build `54a29268` and falsify `5e9ae6e` explicitly; r19 lists all 8 pre-report commits. Audit defects 0 for r11-r17 and r19.
- r10 is the written-before-later-commit case: Landed l.30 "All changes are in lane commit 1e41928"; post-review `4066035` (19:47:40, before the 19:48:55 report) appears only in appended l.114.

## Contract (not excused by the cause)
- PROTOCOL.md:118: "Landed means committed, so changes that exist only in a working tree do not count for the round." PROTOCOL.md:154: "changes landed in the child repo, each tied to a LOG.md entry". templates/round-prompt.md:107: "every change tied to a LOG.md entry and to the commit hash". No clause exempts "reused" or "final" work.
- PROTOCOL.md:185-187: a respawned mission inherits its predecessor's working tree and must resolve the uncommitted round work it finds before filing.
- r20 Landed bullets carry no LOG.md pointer; r18 uses one collective pointer.

## Executed checks (exit)
- `python3 -B tools/report-landing-audit.py` → 0: reports=11 defects=9 corrected=9 status=clean.
- `python3 -B tools/report-landing-audit.py --no-errata` → 1: defects=9 (r10 1, r18 3, r20 5).
- `git log -p -- .ufo/reports/round-20/kama.md` → 0: one commit, `04eb5d2`, +67.
- Hash, ancestry and window checks (python) → all resolve except r20 l.7.

## Side findings (not changed)
- `registry/report-landing-errata.tsv` row 3 says "first 16 hex" / "last 24 hex"; the exact split is 15 + 25. Fix by appended row, not in place.
- watchdog.log has no `complete kama round=20` through line 585 (07:23:21), while `launch kama round=21` is at 07:17:03 [observed; cause not evaluated].

## Implications (advice to L1)
- Keep the 9 flags as contract defects. Record the cause in an appended erratum, not a rewrite of filed reports (PROTOCOL.md:134-137).
- Treating "reused" as an exemption would change the contract, not fix the report.

## Confidence
High: timing, hashes, window boundaries, audit counts. Medium: author intent, which is not written down.

## Tools
None installed or updated.
