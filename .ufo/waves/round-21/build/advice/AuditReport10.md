VERDICT: confirm - the tool's round-10 result (1 landed-omitted, 4066035) equals my hand derivation; no FP/FN on the four kinds; blind spots below are tool limits, not extra r10 defects.

# AuditReport10: hand re-derivation, kama round 10

Scope: fleet `.ufo/reports/round-10/kama.md`, worktree bytes = committed blob at b69b7ba (sha256 4a513e77..., `git status`/`diff` empty, exit 0). Lane `kama-shokunin` master = a29bb84 (exit 0). Lane writes: none outside `build/out/AuditReport10-6/` and this file. No tools installed or updated. Scratch `/tmp/kama-r21-AuditReport10-6` removed (driver printed `scratch removed: True`).

## 1. Hand derivation (git only, not the tool)
- Lane commits on master, author kama-shokunin, subject `round-10:` or `checkpoint(r10)`:
  - 1e41928aba2b81dd65ea75084918a7fadf453720, ct 1792449282, parent 35e9175 (round-9 commit)
  - 40660352d4a9eb00a5d6195f0f064f5c64618143 (4066035), ct 1792450060, parent 1e41928
  - No checkpoint(r10) on any ref (`log --all -i -E --grep='round-?10|checkpoint\(r10\)'`, exit 0). Only other match is 03b5f0e8 (protocol-shokunin, excluded by author).
- First fleet add: b69b7ba27ab74972138509276c3a23cbc493061d, ct 1792450135 (`log --diff-filter=A`, exit 0; sole commit touching the path).
- Pre-report: both lane commits. Post-report: none.
- Landed section (report lines 28-39) cites >=7-hex: `1e41928` only. Line 30 verbatim: "All changes are in lane commit `1e41928`".
- Not cited in Landed: 4066035. It appears only at lines 114 and 120, under "Post-review fixes".
- 40-hex tokens in report: none (`_grep` `[0-9a-f]{40}`: no matches).
- All 7+-hex tokens (lines 3, 30, 42, 44, 47, 109, 114, 118, 120):
  - 1e41928, 35e9175, 4066035: `cat-file -t` = commit in lane (exit 0 each). Fleet: exit 128 (expected; lane commits are not in the fleet repo).
  - 1f81e859 (line 47): not an object. `git show <rev>:tools/kama-probe.sh | md5sum` at 35e9175, 1e41928 and 4066035 each = 1f81e859c2d7f43f87d1f7e01327b2cf (exit 0 x3). The digest is real.
  - Base and parent claims hold: `log -1 %P` gives 35e9175 as parent of 1e41928, and 1e41928 as parent of 4066035.

## 2. Tool comparison
- `python3 tools/report-landing-audit.py --rounds 10 --no-errata --json`: exit 1. One defect: `landed-omitted 40660352d4a9...`, cited_elsewhere=true; round_commits=2, required=2, post_report=[], cutoff=1792450135.
- Hand vs tool: unresolved-full-hash 0/0, landed-unresolved 0/0, landed-section-missing 0/0, landed-omitted 1/1 (same token). FP: none. FN: none.
- The defect is real. `git show --stat 4066035` (exit 0): 4 files, 81 insertions, 0 deletions (LOG.md +5, SCORECARD.md +17, corpus/lessons/round-10.md +15, .ufo/round-10/audit/validate-new-pointers.sh +44 new). Line 30 is therefore false.
- Default ledger: `--rounds 10` exits 1 with `corrected=1 uncorrected=0 errata_unmatched=8 status=failed`. The r10 row (registry/report-landing-errata.tsv:11) corrects the defect. The 8 unmatched rows are rounds 18 and 20, so the run fails only because it is round-scoped. The report's Landed section still omits 4066035; only the ledger corrects the count.

## 3. Defects the tool cannot see (r10)
- None under the four kinds. The Landed overclaim (line 30) is the same defect, counted once.
- No other-round or wrong-object citation in r10. 35e9175 (round 9) appears only as base/before (lines 3, 42, 44, 47, 118) and is the true parent of 1e41928, so it is not a defect. Every other 7+-hex token resolves to its intended commit.
- Stale provenance, not a C1 kind, not counted. Line 3 cites branch `kaika/round` and worktree `.tower/worktrees/kaika/kama-shokunin`. The branch is absent (`branch -a --list`, exit 0: master and origin/* only; fleet `branch --list '*kaika*'`, exit 0, empty). The worktree is absent (`worktree list` shows only the lane at a29bb84; path read: not found).
- Excluded by author rule: 03b5f0e8 (protocol-shokunin, ct 1792450135, "round-10 verifier spot-check (integrator, kaika)") adds corpus/lessons/round-10-verifier-spotcheck.md (+17) to the lane (`show --stat`, exit 0). [INFERENCE] It is an integrator record, so not a kama landing by design.
- [INFERENCE] 03b5f0e8 shares the report's commit second (1792450135). Trend verdicts line 93 ("No non-author admit/reject spot-check has happened yet") may predate it.

## 4. Tool blind spots (probes; fixtures and JSON in `build/out/AuditReport10-6/`; driver `probe-driver.py` exit 0)
| probe | tool result | what it shows |
|---|---|---|
| A: 40-hex = blob 4d3823ac... (`ls-tree 1e41928 -- LOG.md`, exit 0) | 0 defects | `is_object` (lines 70-76) is `cat-file -e` with no type, so any object passes |
| B: fake 40-hex | unresolved-full-hash | control |
| C: Landed also lists 35e9175 (round 9) | 0 defects | any commit is accepted as a landed citation |
| D: Landed lists only 35e9175 | 2x landed-omitted | control: omissions flagged, wrong-round cite not |
| E: `1e41929` (not an object, exit 128) outside Landed | 0 defects | 7+-hex outside Landed never resolved |
| F: `1e41929` inside Landed | landed-unresolved | control |
| scratch fleet: worktree-only edit adds 4066035 to Landed | exit 0, report_committed=true | reads worktree (line 105) but cutoff from git (line 110); HEAD still omits 4066035 |
| same scratch, worktree restored | exit 1, landed-omitted 4066035 | control |
- Master-only scope (line 382 default; `git log <branch>` at lines 86-87): no round-10 kama commit on any other ref (`log --all --not master --grep='round-?(1[0-9]|2[01]):'`, exit 0, empty). 114 non-master commits exist, some with empty subjects (e.g. 00aa1486...). No effect on r10.

## 5. Advisory, not applied
1. Full-hash check: require `^{commit}`, as the Landed check already does.
2. Flag Landed citations that are not round-N lane commits.
3. Resolve 7+-hex tokens everywhere, or allow-list before/base refs by name.
4. Audit the committed blob (`git show <first-add>:<path>`), or refuse when the worktree differs.
5. Scope errata-unmatched failures to the selected rounds.

## 6. Commands and exits
git log master 0; log --diff-filter=A 0; cat-file -t lane 0 (x3), fleet 128 (x4); log -1 x5 0; show --stat 4066035, 1e41928, 03b5f0e8 0; ls-tree 0; tool --json 1; tool with ledger 1; status/diff/sha256 0; md5sum x3 0; log --all --not master 0; rev-list --count 0 (114); log --all --grep 0; branch/worktree 0; cat-file -t 1e41929 and fake 40-hex 128; probe-driver.py 0.
