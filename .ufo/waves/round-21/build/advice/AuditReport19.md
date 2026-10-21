VERDICT: partial - hand derivation matches the tool for round 19 (8 required, 4 post-report, 0 defects, exit 0); one tool-blind measured-commit contradiction (L87) and verified tool defects (case, digits, object type, --report cutoff, errata scope) remain.
Scope: round-19 kama report; lane master (tip a29bb84); fleet first-add ac9859f (ct 1792565257, kama-shokunin). Read-only: no lane or fleet writes; scratch removed; tool installs: none.
Evidence: .ufo/waves/round-21/build/out/AuditReport19-6/probes.py (rerun: python3 probes.py <file>, exit 0) and results.txt.

## 1. Hand derivation (git only)
- `git -C kama-shokunin log --format=%H%x09%an%x09%ct%x09%s master` (rc 0, 82 rows), filtered to author kama-shokunin and subject `round-19:` or `checkpoint(r19)`: 12 commits.
- PRE (ct <= 1792565257): 8 = 7229fa95, 5b108c1a, f1790e25, 84cf2f76, 028235e6, 05f0f6c7, 30ed3783, 24adc8ed (tip at report time). All 8 are cited in the Landed body (report lines 67-79) by 7-hex prefix. Omitted: none.
- POST: 4 = 8d9191f5, 60e8fd8a, 464ea5a3, 3389513f. None is cited anywhere in the report.
- 37bd4c5b (protocol-shokunin, ct 1792566309) is excluded by author and subject.
- 40-hex tokens: 7229fa95eb… (L68) and 24adc8ed372e… (L72). `rev-parse --verify -q X^{commit}`: lane rc 0, fleet rc 1 for both; `merge-base --is-ancestor X master` rc 0. Unresolved: none.
- Landed short tokens (L71, L72, L75, L76): each prefix matches exactly one lane object and zero fleet objects (`cat-file --batch-all-objects`: lane 3582, fleet 8996). Unresolved: none.
- Outside Landed: L54 `7229fa9` and L87 `7229fa95` resolve to 7229fa95 (pre-report). L116 `8bf99cae` is the protocol-shokunin round-18 spot-check commit; its file corpus/lessons/round-18-verifier-spotcheck.md exists (`cat-file -e` rc 0), so the citation is correct. L85 `6c216313…` is not a git object; it is the correct prefix of install_tree_sha256 6c216313a88d…5a2c (.ufo/waves/round-18/live-recovery/receipt-1.json:446; receipts 2-3 identical).

## 2. Tool vs derivation (cwd = lane)
| args | exit | round-19 result |
|---|---|---|
| `--rounds 19 --no-errata --json` | 0 | required 8, post 4, round_commits 12, defects [], clean |
| `--rounds 19 --no-errata` | 0 | required 8, post 4, defects 0 |
| `--rounds 19 --json` (default ledger) | 1 | defects 0; errata_unmatched 9 (rows for r10/r18/r20), status failed |
| `--rounds 19 --no-errata --report 19=<committed path> --json` | 1 | committed=false, cutoff=now, required 12, 4 landed-omitted (3389513f, 464ea5a3, 60e8fd8a, 8d9191f5) |
| `--no-errata` (rounds 10-20) | 1 | 9 defects: r10 1, r18 3, r19 0, r20 5 (matches the stated raw count) |
| no args (rounds 10-20, ledger) | 0 | 9 corrected, 0 uncorrected |

For the requested command the tool matches the derivation exactly: no false negative and no false positive for round 19.

## 3. Defects the tool cannot see
- T-1 (report L87): "The measured commit for both claims is `7229fa95…` plus the post-commit grid fail-closed change (committed in the evidence commit)". L76 says the measured work commit is `028235e6…`. Both committed evidence files at tip 24adc8ed say on line 1 `measured_commit=028235e6f28d5b7f4106dd121956f10d2c762f48` (`git show`, rc 0). Git: 7229fa95..028235e6 changes the C1 checker (tools/citation-provenance.py, 62 lines), the registry (required-citations.json, 18) and the grid (install-tree-grid.py, 25) (`git diff --stat`, rc 0). The grid change lands in 5b108c1 and 84cf2f7, not in evidence commit 05f0f6c7, which changes only the two receipt files. L87 has no committed support; the tool sees only that 7229fa95 resolves.
- L54 harness start `7229fa9`: not checkable from git (run records uncommitted, L60-61). [INFERENCE] consistent with advice GateTreeBaseline.md (head-7229fa9 snapshot).

## 4. Tool defects (controlled probes; results.txt)
Method: committed report copied into scratch fleets with the same committer time; one mutation each; real lane; `--rounds 19 --no-errata --json`.
- P2 uppercase Landed citation `5B108C1A…`: exit 1, FALSE POSITIVE landed-omitted 5b108c1a7e94… (regexes are `[0-9a-f]` only, lines 50-51).
- P7 absent uppercase 40-hex: exit 0, FALSE NEGATIVE (unresolved-full-hash missed).
- P3 decimal `1792565257` in Landed: exit 1, FALSE POSITIVE landed-unresolved (digit runs match ABBREV).
- P5 lane tree object e8ced4d6… as a full hash: exit 0, BLIND (`is_object` without kind, line 117).
- P4 round-18 commit 8bf99cae… in Landed: exit 0, BLIND (existence only). P8 post-report commit 8d9191f5… in Landed: exit 0, BLIND (no cutoff check).
- Controls behave: P0 clean (exit 0); P1 heading renamed, exit 1 (9 defects); P6 absent lowercase 40-hex, exit 1; P9 dropped 028235e6, exit 1.
- Real `--report` on a committed report: cutoff=now (line 110) contradicts the docstring (lines 22-24 reserve "now" for uncommitted reports). Source of the FALSE POSITIVES in section 2.
- Real `--rounds 19` with the default ledger: apply_errata (lines 166-181) counts other rounds' rows as unmatched, giving a false "failed" verdict.

## 5. Limits and suggested fixes
- Only round 19 is audited. Ledger correctness for r10/r18/r20 rests on the tool's counts, not a re-derivation.
- Suggested fixes [INFERENCE, not applied]: case-insensitive hex; exclude digit-only runs; full hashes must be commits; honor the commit cutoff for committed `--report` paths; scope errata rows to audited rounds; check Landed commit author and round.
- `--selftest` not run. No tool installs. Scratch /tmp/kama-r21-AuditReport19-6 removed (script cleanup True).
- Lane tools/__pycache__ holds 3 .pyc files: citation-provenance (03:33) and kama-llamacpp-live plus report-landing-audit (both 07:45:27, written by a process I did not run). My runs were scripts or `python3 -B` imports, so none of these is mine [INFERENCE].
