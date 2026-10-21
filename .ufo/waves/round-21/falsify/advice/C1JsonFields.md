VERDICT: confirm - all 11 reports' JSON fields match an independent recount at b76727f (0 mismatches); F1-F3 are latent, not field errors.

# C1JsonFields - FALSIFY of report-landing-audit JSON (round 21)

Attacked: `.ufo/waves/round-21/runs/b76727f3/c1-audit-raw.stdout` (sha256 af2707ad...e24, equal to commands.json `c1-audit-raw` stdout_sha256). Producer: `tools/report-landing-audit.py` committed blob 62bef09f, identical at b76727f and lane tip a6617149.
Recount (read-only, re-runnable): `.ufo/waves/round-21/falsify/out/C1JsonFields/c1-json-recount.py`; output `recount-output.txt` (`exit=0`, `MISMATCHES=0`).

## Result
0 mismatches for rounds 10-20: cutoff, required, round_commits, post_report (SHAs and order), report path, report_committed, defects (kind, token, cited_elsewhere, corrected_by), and summary (reports, defects, by_kind, required_commits, post_report_commits, status, errata fields).

| r | cutoff = add `%at` (add) | required / round_commits / post | defects (JSON agrees with recount) |
|---|---|---|---|
| 10 | 1792450135 (b69b7ba2) | 2 / 2 / 0 | landed-omitted 40660352 ce=T |
| 11 | 1792468776 (dff17307) | 2 / 2 / 0 | none |
| 12 | 1792471121 (5ee71e4c) | 2 / 2 / 0 | none |
| 13 | 1792472920 (3ecce953) | 2 / 2 / 0 | none |
| 14 | 1792478534 (52c833d1) | 2 / 2 / 0 | none |
| 15 | 1792485831 (402b93b5) | 3 / 3 / 0 | none |
| 16 | 1792505790 (9ec9c524) | 3 / 3 / 0 | none |
| 17 | 1792524895 (54343767) | 2 / 2 / 0 | none |
| 18 | 1792561152 (23bdc3f8) | 7 / 7 / 0 | landed-omitted 101f3991 ce=T, 1c325b2e ce=T, c6dc46fa ce=T |
| 19 | 1792565257 (ac9859f4) | 8 / 12 / 4 | none |
| 20 | 1792577594 (04eb5d2d) | 9 / 9 / 0 | unresolved-full-hash 0957ce619789d13d894e...; landed-omitted 0957ce619789 ce=T, 33a6777866d0 ce=F, 846e366dc9db ce=F, 92b146253fd3 ce=F |

Totals: reports 11, defects 9, required 42, post 4, status failed (exit 1); all equal to JSON.

## cited_elsewhere vs the reports (every prefix occurrence checked)
- r10 40660352: L114 "Lane commit **`4066035`**" and L120 "Output at `4066035`", both in "## Post-review fixes" (Landed is L28-39). True is correct.
- r18: L19 `101f3991...`, L27 `1c325b2`, L26 `c6dc46f`, all outside Landed (L73-87). True is correct.
- r20 0957ce619789: L7 `runs/0957ce61/` and L10 full hash `0957ce619789d13bb5779606078fa1498114d2c7`. True is correct.
- r20 33a6777866d0, 846e366dc9db, 92b146253fd3: zero occurrences of the first 7 hex chars anywhere in the report (case-insensitive, bounded or not). False is correct.

## Findings (none is a field mismatch)
- F1 latent (reproducibility): the committed tool reads the fleet working-tree copy, not HEAD. Working tree == HEAD == first-add blob for all 11 today, so no effect; an uncommitted edit would change defects. The lane working tree is dirty: its `tools/report-landing-audit.py` hashes 1e98816b (committed 62bef09f), reads `git show HEAD:<rel>`, and adds selftest cases. It also reproduces the measured bytes (rc 1). `git diff --name-only HEAD` lists SCORECARD.md, tests/llamacpp-live/check-receipt.py, tools/kama-llamacpp-live.py, tools/report-landing-audit.py. Not touched by me.
- F2 latent: `report_cutoff` takes `out[-1]` of default-ordered `git log`, which is "first added" only with one add. Each path has exactly one add, so no effect.
- F3 by design: body-text abbreviations are never resolved. 18 checkable body tokens (incl. two blob OIDs and the r20 splice) resolve to no commit. Inspected ones are digests or blob/tree IDs (r16 L175 `270cba1b...`, r17 L64 `b853576e...`, r19 L85 `--tree-sha 6c216313...`, r20 L65 `753bfa73...`) or upstream llama.cpp commit `704366d76` (r16 L131, L172, "GitHub Pre-release"; absent from lane and fleet). No lane-commit citation outside Landed is unresolved.
- F4 by design: unresolved-full-hash accepts any object type. Two full blob OIDs (r12 `7de1360655ea...`, r15 `783004569af9...`) are labelled as blobs in their sentences, so no false negative here.
- F5 verified: the r20 unresolved token is a splice. Its first 15 hex chars are commit 0957ce619789d13bb..., its last 26 are commit 33a6777866d0f63d894... Consistent with the closure note (line 7 nonexistent, correct hash at line 10).
- F6 verified, no false negative: in the window (author time >= 1792440000) all 50 kama-shokunin commits match `^round-N:` or `^checkpoint(rN)`. The non-matching kama commits I listed are older than the window or are `round-2`.
- F7 boundary: protocol-shokunin integrator commit 03b5f0e8b9ec ("round-10 verifier spot-check") has author time 1792450135, exactly the r10 cutoff. Excluded by the author rule (correct per spec); it would tie at `<=` if that rule changed.
- F8 noted: cited_elsewhere counts any bounded >=7-hex prefix, including run-directory names (r20 `runs/0957ce61/`). The r20 True flag also has the full hash at L10, so it holds either way.

## Limits
- Not checked: `--selftest` and the errata-applied ledger variant (outside the raw-JSON scope). Upstream 704366d76 is not verifiable offline.
- [INFERENCE] The measured argv ran the lane working-tree path. The committed and working-tree variants give identical bytes for these inputs, so the measured output is unaffected.

## Commands run (exits)
- `git clone -q <lane> /tmp/kama-r21-C1JsonFields/lane && git checkout -q b76727f...` -> 0
- `git merge-base --is-ancestor a6617149 b76727f` -> 1; reverse direction -> 0 (b76727f is an ancestor of lane tip)
- `git log --diff-filter=A --format=%at -- .ufo/reports/round-N/kama.md` (fleet, N=10..20, in recount) -> 0
- `git rev-parse b76727f:tools/report-landing-audit.py a6617149:...` -> 0 (both 62bef09f); `git hash-object` on lane worktree copy -> 0 (1e98816b)
- `git diff --name-only b76727f a6617149 -- tools registry .ufo/reports corpus/SOURCES.md` -> 0, empty
- `git diff --name-only HEAD` (lane, GIT_OPTIONAL_LOCKS=0) -> 0
- committed tool at b76727f, `--lane-repo <clone> --fleet-repo <fleet> --branch b76727f... --rounds 10-20 --no-errata --json` -> 1, stdout byte-identical to raw
- working-tree tool, lane tip (master = a6617149), same flags -> 1, byte-identical
- `python3 falsify/out/C1JsonFields/c1-json-recount.py` -> 0 (MISMATCHES=0)
- `sha256sum c1-audit-raw.stdout` -> af2707ad...e24 (matches commands.json)

## Installs and cleanup
No tools installed or updated. Lane and fleet were only read (no ref, index, or file writes). Scratch `/tmp/kama-r21-C1JsonFields` removed.
