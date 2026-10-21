VERDICT: partial - exit 2 at round 3 reproduces and 9 of 10 early-round defects are format artifacts, but exit 2 comes from absent fleet reports (rounds 3, 5), one defect is real, and the round-10 stop is the tool's default range, not a format break.

Attacked: lesson `corpus/lessons/round-21.md` §Limits ("earlier reports use other formats (AuditEarlyRounds: exit 2 at round 3, format artifacts)") and C1's population (rounds 10-20), at a6617149722c73d90e142fbdc8154d6967055f7e. Tool bytes: blob 62bef09f (sha256 bd671a1e), copied to `falsify/out/RevengerEarlyRounds/pinned-report-landing-audit.py`.

## Commands (exit observed)
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py --rounds 1-9 --no-errata`: exit 2, `cannot read .../round-3/kama.md: No such file` (first run). Rerun later on the modified lane tree: exit 2, `round 3 ... not committed in fleet HEAD`.
- Pinned tool with `--lane-repo`/`--fleet-repo`/`--branch a6617149...`, `--rounds 1-9`: exit 2, same round.
- Pinned tool without `--fleet-repo`: exit 2, `not a git repository`. The default fleet root is the parent of the tool's directory.
- `--rounds r --no-errata --json`, r=1..11: exits 1,1,2,1,2,1,1,1,1,1,0.
- `--rounds 1,2,4,6,7,8,9`: exit 1; 7 reports, 10 defects (8 landed-omitted, 2 landed-section-missing), 8 required commits.
- `--rounds 10-` (default): exit 1; rounds 10-20, 11 reports, 9 defects (8 landed-omitted, 1 unresolved-full-hash). Matches C1's stated counts.
- `--selftest`: exit 0, `selftest cases=32 failed=0`.
- `--rounds 1-9 --report 5=<lane copy>`: exit 2 (round 3 still absent).
Raw: `falsify/out/RevengerEarlyRounds/` (`round-N.out/.err`, `commands.json`; argv paths point at the scratch copy, byte-identical to the pinned file).

## Per-round results (pinned blob)
| R | Fleet first add (UTC, author) | Result | Cause (observed) | Class |
|---|---|---|---|---|
| 1 | 74768ab 02:15:55, human | exit 1: section-missing; omitted c6199a2 | heading `## What landed (verifiable artifacts)` L11; sole round commit c6199a2 is cited in header L4 | format |
| 2 | ee1f621 04:36:12, human | exit 1: section-missing; required 0 | heading `## What landed` L9; round commit 83bee7f has subject `round-2` (no colon), silently skipped by `^round-N:`; header L4 cites it; table L11-20 names its artifacts | format + silent false negative (no content loss) |
| 3 | none on any ref | exit 2 | `round-3/kama.md` never committed (`git log --all` empty, exit 0); round-4 commit c390918 adds lesson lines 58-67: "round 3 has no report file" | missing report |
| 4 | cb3c103 00:24:03, protocol-shokunin | exit 1: omitted 84a81304, 0505b718, 47f3aedd | Landed list L23-28 is file-level, no hashes. 84a81304 cited in header L4. 0505b718 touches only round-4-recensus.md (named L25). 47f3aedd edits LOG.md, endpoint-identity.md row 7 (`:481-487` -> `:516`), round-4-recensus.md; not described; Carried-debt L49 still lists `:481-487` as drifted | 2 format; 1 real, minor |
| 5 | none in fleet | exit 2 | lane commit 15a733c adds `.ufo/reports/round-5/kama.md`; the fleet never received it | missing fleet report |
| 6 | 7aee52d 18:35:59Z, kama | exit 1: omitted f396b98 | heading L25 `## Landed changes (lane repo, commit f396b98...)`; the hash sits on the heading line, which `landed_section` never scans | format (false positive) |
| 7 | 1ecde51 18:38:51Z | exit 1: omitted 4bcae65 | heading L18, same | false positive |
| 8 | e8a87e0 18:40:53Z | exit 1: omitted d0f5a2d | heading L20, same | false positive |
| 9 | e676d09 18:43:16Z | exit 1: omitted 35e9175 | heading L20, same | false positive |
| 10 | b69b7ba 22:48:55Z (reference) | exit 1: omitted 4066035 | post-review section L112-125; ledger row 11 corrects it | real (ledger) |

## Lesson claims
1. "exit 2 at round 3": reproduced. The cause is a missing file, not format. Round 5 is the same kind.
2. "format artifacts": 9 of 10 early defects come from four conventions the detector does not parse: heading name (R1, R2), file-level Landed body (R4), hash on the heading line (R6-R9), colon-less subject (R2, silent). The tenth (47f3aedd) is real but minor.
3. "population stops at round 10 for format reasons": the exclusion holds; the stated reason is incomplete.
   - The tool does not stop at 10. Rounds 1, 2, 4, 6-9 run (exit 1). The boundary is the default `--rounds 10-`.
   - No single format break at 10. R4 already has the plain heading with a file list. Rounds 10-20 all use the plain heading (grep of 11 reports); defects appear only on R10, R18, R20.
   - Of 70 kama-shokunin commits reachable from a6617149, the only round-like subject the colon rule misses is 83bee7f. None falls in 10-20.
   Suggested Limits wording [INFERENCE on wording; L1 decides]: "Rounds 1-9 are outside C1's population. Rounds 3 and 5 have no fleet kama report. The other seven use four conventions the detector does not parse: heading name, file-level Landed body, hash on the heading line, colon-less subject."

## Observations (not judged by the tool)
- `--rounds 1-9` is all-or-nothing: the first missing report aborts the run and prints no other round.
- Lane tree drift during this session: `tools/report-landing-audit.py` is modified and uncommitted (working-tree blob 1e98816b; committed 62bef09f). `git status` also shows M SCORECARD.md, tests/llamacpp-live/check-receipt.py, tools/kama-llamacpp-live.py, and untracked round-21 build and falsify files. The working-tree tool reads committed fleet bytes (`git show HEAD:`) and adds selftest cases. Its stdout for rounds 1-11 is byte-identical to the pinned run; only the missing-report message changed. [INFERENCE: L1 integrating.]
- Prose vs git: R1 header "23 files, +3164/-27" vs `git show --shortstat c6199a2` = 20 files, +2895/-24. R2 "+831/-89" vs 83bee7f = 832/-90.
- Lane-side R5 draft (`--report 5=`, cutoff = now; not a fleet verdict): exit 1, one defect, 15a733c (the commit carrying the report). A report cannot cite the commit that adds it [INFERENCE].

## Limits
- Tools installed or updated: none (system python3 3.14.8, git).
- Lane git state untouched. Writes: new untracked files under `falsify/out/RevengerEarlyRounds/` and this report. Scratch `/tmp/kama-r21-RevengerEarlyRounds` removed after writing.
- Not run: working-tree selftest. C1's counts were reproduced, not re-derived from hand recounts.
