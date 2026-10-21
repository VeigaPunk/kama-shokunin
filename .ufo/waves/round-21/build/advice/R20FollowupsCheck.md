VERDICT: confirm - both round-20 follow-ups are detected (raw: 1 unresolved-full-hash + 4 landed-omitted, exit 1) and each is corrected one-to-one by ledger lines 3-7 (exit 0); two ledger evidence-text slips are non-mechanical.

Scope: R20FollowupsCheck (leaf, kama r21). Audited draft a29bb84 in a scratch clone (deleted) and ran the canonical lane read-only. Audit inputs are sha256-identical in lane and clone (ledger baaf4bda..., script a60acc3a...). Fleet r20 report: committed 04eb5d2 and working copy identical (35bbcbb8...). Tool installs: none. Lane not modified.

## 1. Closure text relied on
MANIFEST.json rounds[397]: round 20, type closure, closed_at 2026-10-21T10:16:40Z, lanes {"kama":"ok"}.
- "round commits 33a6777 0957ce6 92b1462 846e366 c731103 04de7a8 9add96e 3ec5ea6 7a6bc91 all by kama-shokunin and ancestors of master."
- "Defects (status-neutral, routed to kama r21): (D1) report :7 cites full hash 0957ce619789d13d894ef21bc863486bcb35b56c which resolves nowhere; actual commit is 0957ce619789d13bb5779606078fa1498114d2c7 (correct at :10); (D2) Landed changes lists 5 commits but omits round commits 33a6777, 0957ce6, 92b1462, 846e366."

## 2. Facts (executed)
- `git cat-file -t 0957ce619789d13d894ef21bc863486bcb35b56c`: exit 128 in lane and fleet. Correct hash: `commit`, exit 0.
- Report first added in fleet commit 04eb5d2 (ctime 1792577594). Round-20 lane commits by kama-shokunin: 9. Audit: required=9, post_report=0.
- Report :7 holds the bad token and `runs/0957ce61/`; :10 holds the correct full hash. 33a6777, 92b1462, 846e366 occur nowhere in the report (literal search).

## 3. Detection and correction
| Follow-up | Raw defect (`--rounds 20 --no-errata`, exit 1) | Ledger row | Remove only that row (`--rounds 10-20 --errata`, exit 1) |
|---|---|---|---|
| D1 | unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c | line 3, corrected_by [3] | only this defect uncorrected |
| D2 | landed-omitted 33a6777866d0f63d894ef21bc863486bcb35b56c | line 4 | only this uncorrected |
| D2 | landed-omitted 0957ce619789d13bb5779606078fa1498114d2c7 (cited at :10 elsewhere) | line 5 | only this uncorrected |
| D2 | landed-omitted 92b146253fd3a8c4bfade94c909dc63b13d6f4a8 | line 6 | only this uncorrected |
| D2 | landed-omitted 846e366dc9dbac58463494a7e05ad060ae3ed3b0 | line 7 | only this uncorrected |

Other runs: `--rounds 10-20 --no-errata` exit 1 (defects=9, so C1 raw count holds). `--rounds 10-20` exit 0 (corrected=9, uncorrected=0, unmatched=0, invalid=0, clean). Canonical `python3 tools/report-landing-audit.py` exit 0 (reports=11). `--selftest` exit 0 (15 cases, 0 failed). Mutants (line-3 token last hex changed; line-3 round 20->21) each exit 1 with errata-unmatched=1. Transcript with every command and exit: `.ufo/waves/round-21/build/out/R20FollowupsCheck/r20-followups-evidence.txt`.

## 4. Draft tests (`--rounds 20 --no-errata --report 20=<draft>`, copies of the committed report)
- As committed: 5 defects, exit 1. Hash fixed only: 4 landed-omitted remain, exit 1. Bullets only: unresolved-full-hash remains, exit 1. Hash fixed plus 4 bullets in Landed: 0 defects, exit 0. Bare `1099158` and `20261021` added to Landed: landed-unresolved x2, exit 1.
- Round 21 (`--rounds 21 --no-errata --report 21=<draft>`): citing nothing gives landed-omitted a29bb84..., exit 1. Citing `a29bb84` gives 0 defects, exit 0. `deadbee1` in Landed gives landed-unresolved, exit 1. A 40-hex non-object in the body gives unresolved-full-hash, exit 1.

## 5. Format rule for `.ufo/reports/round-21/kama.md` (MUST)
1. Every 40-hex token is an existing git object: copy from git output and check `git cat-file -t` = commit. Never splice two hashes. Name each referent with its own full hash (population 33a6777866d0f63d894ef21bc863486bcb35b56c; measured tree 0957ce619789d13bb5779606078fa1498114d2c7).
2. `## Landed changes` gets one bullet per lane commit with author kama-shokunin and subject `round-21:` or `checkpoint(r21)` whose committer time is at or before the report's first fleet commit. Each is cited by a >=7-hex prefix inside that section; body mentions do not count. Derive the list with `git log`, not from memory. At draft time a29bb84 is required.
3. Landed holds only resolvable hex: no typos, and no bare digit runs of 7+ characters (pids, timestamps such as 20261021), which are audited as commit tokens.
4. Gates. Pre-commit: `python3 tools/report-landing-audit.py --report 21=<draft>` must exit 0 (executed: reports=12, clean). Post-commit: `python3 tools/report-landing-audit.py --rounds 10-21` must exit 0 [INFERENCE: not run for r21; executed exit 2 while the fleet file is absent]. Never use subset runs: `--rounds 20` with the ledger exits 1 (errata-unmatched=4).
5. A round-21 commit made after the draft gate but before the report commit becomes required, since the cutoff is the fleet commit time. Re-run the post-commit gate. Post-report semantics are executed (r19: post_report=4).
6. Do not amend or edit the committed report (MANIFEST.json:167 "amend-after-report = defect"). Corrections go in the ledger as append-only round-21 rows with exact round/kind/token (a mismatch exits 1 as errata-unmatched). Lane commits must use kama-shokunin identity (MANIFEST.json:173), or the audit will not require them.

## 6. Residual risks (non-blocking)
- Ledger evidence text is wrong in two places; the audit ignores it. Row 3 says "first 16 hex of 0957ce61 ... last 24 hex of 33a67778". Executed: the token is 0957ce619789d13 (first 15 hex of 0957ce61; hex 16 differs, d vs b) plus d894ef21bc863486bcb35b56c (last 25 hex of 33a67778). Row 5 says 0957ce61 is cited in "the measurement table"; the table does not cite it (it appears only at :7 `runs/0957ce61/` and :10).
- Default range `10-20` (script line 384) excludes round 21. Once the report is committed, only `--rounds 10-21` or `--report` audits it.
- The audit reads the body from the fleet working tree but takes the cutoff from git (script lines 105-110) [INFERENCE: code-read, not executed]. Keep the committed file unmodified.
- Lane working tree at observation, not mine and not audit inputs: ` M tools/kama-llamacpp-live.py` and `?? .ufo/waves/round-21/build/`.

## 7. Cleanup
Scratch /tmp/kama-r21-R20FollowupsCheck removed (verified). No lane, fleet, MANIFEST, ledger or script file modified. New files only: this report and the evidence transcript.
