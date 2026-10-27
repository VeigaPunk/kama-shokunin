author: hyaku closure (non-author integrator, @m_opus)

# kama round 52: non-author closure spot-check

Date: 2026-10-27 (closed 2026-10-27 UTC). Base `9ff76b1f763512be2f554cbbfd0b2213b63b0847`, freeze `8551ba7f2056f2465d20f5b50586978133212fe1`, build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, wave spec `34d8260051bbab8859485e8209fcf4be19dc9a2b`, integration and measured commit `35e3b1dc9ca32c24e543366c6ff78e15c0bdb32e`, results `ade21a45170a0f5e2e77ea5a400fd5cb4c2d5497`, lane tip `eb7b16cfa6b535d726027e338f0fb7232359a995`. Report `.ufo/reports/round-52/kama.md` (fleet repo).

Method: I took plain measurements myself over committed bytes (git, grep, sha256sum, a git-history line check, the sources census, and curl of the cited sources). I did **not** execute the lane's frozen claim counters. They are registered in `SKILL.md` §Round-52 instrument registry (lines 1549–1550). PROTOCOL §Gate standard (Closure consequence) has the closure verify their committed evidence instead. I dispatched no seats.

Driver digest (from `.ufo/watchdog.log`, which is mutable):
`2026-10-27T01:28:37-03:00 launch kama round=52 pgid=638770 driver=hyaku-inline attempt=1`
`2026-10-27T02:41:41-03:00 complete kama round=52; hyaku-inline attempt=1`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify. For C1, my plain measurement covers the mechanism, the source row and the counter pin, and the live leg is evidence-verified from the frozen-counter receipt. C2 is re-derived independently from git history, 155 of 155 lines.
- No axis is harmed. No score changed (8/8/7/9/7/7), and capabilities stay at 11 → 11.
- The spot-check agrees with the Gate on 2 admits (S500, S502) and 2 rejects (S503, S505). S505's line anchor is wrong (R1).
- Round-51 closure D1–D7 are answered in `corpus/lessons/round-52.md` §Errata. D5 is partly carried, as the lane states.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an <%ae> %H %ci' -- .ufo/reports/round-52/kama.md` → `kama-shokunin <kama@shokunin.local> 3945011969fbc4b0bdcf4c856626d016068558ec 2026-10-27 02:40:15 -0300` (one commit) | pass |
| Report filed after its tip and before `complete` | tip `eb7b16cf` committed 02:39:49 -03 → report 02:40:15 → `complete` 02:41:41. `w1-results.json` at the tip reads `seats 70, results 70`, so the report was filed after WAVE-DONE (round-51 D1 closed) | pass |
| `SHONEN` heading, one line per box | `## SHONEN`: 4 lines, all `[~]`, each with a pointer | pass |
| Cited lane commits exist and are ancestors of the branch | `git rev-parse --verify <h>^{commit}` and `git merge-base --is-ancestor <full> master` hold for `9ff76b1f 8551ba7f 5dacf2c7 34d82600 35e3b1dc ade21a45 eb7b16cf 1ab1de39`. `39877b17` is the fleet-repo round-51 report commit (`git -C <fleet> rev-parse` → `39877b174e99…`), not a lane commit. `git log 9ff76b1f..eb7b16cf` → exactly 6 commits, all `kama-shokunin`, matching the report's Landed-changes table | pass |
| Lane pushed | `jj-lane.sh state` → `branch=master local=eb7b16cf… remote=eb7b16cf… ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git ls-remote origin refs/heads/master` → `eb7b16cfa6b535d726027e338f0fb7232359a995` | pass |
| No uncommitted round work | `git status --porcelain` → 0 lines | pass |
| Prompt carries the template contract | Prompt `ee016fdf` (lane identity, 01:28:35, 2 s before launch). I rendered `templates/round-prompt.md` (byte-identical to the canonical kimi-shokunin template) with kama/52/fleet root/AXES line and diffed it against prompt lines 1–140. The only difference is the `<kama-repo>` placeholder → `kama-shokunin`. §6/§7 differ from the round-51 prompt only in round numbers and attempt (20+/20−) | pass |
| Quoted route map vs MISSION | `grep -c '@m_' MISSION.md` → 0. The §6 "Current map" is unchanged from the round-51 prompt that the round-51 closure matched to the live map | pass |
| L2 floor and role mix | `w1/spec.json`: 70 seats: executor 21, reviewer 12, scout 10, critic 8, mutation-tester 6, scribe 5, sentinel 3, connector 3, simplifier 1, revenger 1. This equals the report. Attack share is 26/70. `validate.out` `exit=0`. No planner seat: the validator conflict is carried as L0 `kama \| round-39` | pass (planner gap carried) |
| Counters frozen before data | `sha256sum` of `tools/round52-replay-memfd-audit.py` at `8551ba7f`, `35e3b1dc` and `eb7b16cf` → `053ff502…21f5` each time. `tools/round52-append-restore-check.py` → `29dfd886…53ea` each time. Both equal `preregistration.json` `claims[*].counter_sha256`. `freeze/prereg-time-check.out` → `RESULT pass`, exit 0 | pass |
| Sources census | My run of `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0: `1 ok`, `1 W01` (S481), 94 `W04`, 0 `E`. Byte-identical to the committed `census/end.out` (diff empty) | pass |

This is not a marker report: real lane commits and evidence. Status `ok`.

## 2. Claims (step 2)

### C1: operability 8→8. The replay's server runs from a sealed anonymous memfd (sourced on S500). Plain-measured and evidence-verified.

Plain measurements, mine (`git show <rev>:<file> | grep -c <pattern>`):

| Pattern | `kama-live-replay.py` base → tip | `kama-llamacpp-live.py` base → tip |
|---|---|---|
| `memfd_create` | 0 → 4 | 0 → 5 |
| `F_ADD_SEALS` | 0 → 2 | 0 → 2 |
| `MFD_ALLOW_SEALING` | 0 → 1 | 0 → 1 |
| `sealed_member` | 0 → 6 | 0 → 0 |
| `server-fd` | 0 → 4 | 0 → 19 |

- SOURCES rows went 240 → 246 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`), which equals the report. S500 (memfd_create(2)) is present at the tip and absent at the base.
- Spot read at the tip:
  - `kama-live-replay.py:223–276` `sealed_member()`:
    - It calls `os.memfd_create`, with `MFD_EXEC` when available.
    - It streams and hashes the member.
    - It applies `F_ADD_SEALS SEALS_ALL`, then reads `F_GET_SEALS` back, re-hashes the sealed bytes, and returns `{"memfd": True, "member", "sha256", "seals", dev, inode}`.
  - `kama-llamacpp-live.py:798–827` `sealed_fd()` refuses each of these: not-sealed, `F_SEAL_EXEC`, size mismatch, digest mismatch.
  - `:734–771` records `nlink` and `seals` of the image opened through `/proc/<pid>/exe`.
  - The mechanism is real, not a counter-shaped stub.

Committed evidence, verified and not executed by me:
- `controls/base.c1.out` (`tip=9ff76b1f…`): `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False`, exit 1. Detail: `F_GET_SEALS on the running image failed: Invalid argument` and `link count 1, not 0`.
- `measured/c1.out` (`tip=35e3b1dc…`): `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0. Each of b1–b3: `running image '/memfd:llama-server (deleted)' 00:01:<inode> seals 15`, three distinct inodes. `newrow: 6 rows new since base; 1 name memfd_create(2): ['| S500 |']`.
- Independent seat reruns: X1Rerun and X2Rerun read base `met=False` and build `met=True`. The preregistered ablations are J1PathExec, J2Unsealed, J3CopyDecoy and J4Hardlink, each `sealed=0 … met=False`. The preregistered limit J5HostMemfd reads `met=True`. J6RenameOver reads `met=True` at the build, as a robustness probe: the image stays the memfd. The same probe met the round-51 counter at the round-51 base, which closes round-51 D5's rename-over `[INFERENCE]`.

The round-51 C1 counter now reads `own=0 … met=False` at `35e3b1dc` (`measured/r51c1.out`). The replay now names its own memfd: its `own_server` dev:inode equals the observed running image (`00:01:178830`). The round-51 counter only expects an on-disk member file. That binding is superseded by a stricter one, which also survives the rename-over the round-51 binding missed, so this is not a harm.

Verdict: **verified** (plain-measured: mechanism, source row, counter pin; evidence-verified: live leg).

### C2: calibration 7→7. The A-corr files hold every line they declared append-only. Re-derived independently.

- My own history check (Python over `git show`, independent of the lane's counter and tool):
  - At `35e3b1dc`, 23 files contain the string `Restored lines (round 52)`. 18 of them carry `Deleted by \`<12-hex>\`` blocks, and the blocks hold **155** lines in total: LOG 22, SCORECARD 23, README 20, QUALITY 2, and 14 lessons (round-1 2, 4-recensus 1, 16 11, 18 4, 19 6, 25 10, 26 17, 27 13, 28 6, 32-verifier-spotcheck 1, 38 11, 40 1, 42 4, 43 1).
  - For every restored line, I compared its multiplicity in `<deleting commit>^:<file>` with `<deleting commit>:<file>`. The parent count exceeded the deleting commit's count for **155 of 155**. Every restored line was genuinely deleted by the commit its block names, and it is re-appended verbatim.
- Ledger: `registry/append-only-disclosures.tsv` non-comment lines went 166 → 11, header included, so 165 → 10 rows. The 10 rows at the tip are 7 `corpus/SOURCES.md` and 3 `registry/report-landing-errata.tsv`, the A-row files. This equals the report.
- Deletions this round in A-corr files (`git diff --numstat 9ff76b1f eb7b16cf`): SCORECARD.md has 5. Those are the head banner, the operability/depth/calibration evidence rows, and the `Planned (round 52)` → `(round 53)` pointer. The head is exempt, and the round-51 banner is re-appended verbatim. `corpus/lessons/round-1.md` has 1, a newline-at-EOF change only. LOG, QUALITY, README, SOURCES, SKILL and the lessons otherwise have 0 deletions.
- Committed receipts:
  - `controls/base.c2.out` `corr_lost=151 … met=False`, exit 1.
  - `measured/c2.out` (`tip=35e3b1dc…`) `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0.
  - Ablations J7Prefix, J8LeaveRows, J9DropContract and J10CorrRow each read `lane=0 met=False`. X6Rerun agrees.

Verdict: **verified** (re-measured by an independent history check; counter evidence-verified).

### Regression battery (evidence-verified at `35e3b1dc`)

- gate `registered 50 unregistered 0 defective 0`
- cap `listed 11 observed 11 missing 0 unsubstantiated 0 met True`
- r41 / r42 / r43 `mismatches=0`
- r48c2, r49c1, r50c1, r51c2 `met=True`
- `AOA_SELFTEST pass=51 fail=0`, `KLR_SELFTEST pass=36 fail=0`
- pointer `met=True` at `ade21a45`
- r51c1 `met=False`: the supersession above

Neither claim is exploratory.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| operability | improved | C1. The running server image moves from a path-named file (base: `F_GET_SEALS` EINVAL, link count 1) to a sealed anonymous memfd recorded in `server_exe`/`own_server`, 3/3. The copy, hardlink and rename-over decoys no longer stand in for the image. Score held at 8 |
| calibration | improved | C2. The lane's declared A-corr invariant now holds in the bytes: 155/155 restored lines are traced to their deleting commits, and the ledger shrinks from 165 to 10 genuine A-row losses. Score held at 7 |
| freshness | unchanged | Score 8. Row unchanged in the SCORECARD diff |
| depth | unchanged | Score 7. SKILL.md +18/−0 (round-52 registry). Row evidence re-anchored only |
| coverage | unchanged | Score 9. PROVINCE.md not in the diff |
| adjacency | unchanged | Score 7. N1Overlap reported 16 touchpoints, none absorbed |

`git diff 9ff76b1f eb7b16cf -- SCORECARD.md`: 103 added, 5 removed. The `## Axes` score column is 8/8/7/9/7/7 at both revisions. `corpus/knowledge/` has no diff.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S500 memfd_create(2) | admit | `curl -sSL https://man7.org/linux/man-pages/man2/memfd_create.2.html`, tags stripped: the quote "memfd_create() creates an anonymous file and returns a file descriptor that refers to it." is present once. "Linux 3.17, glibc 2.27." is present (§HISTORY) | agree | Verbatim, 14 words, at §DESCRIPTION. It grounds exactly what `sealed_member()` does, and the HISTORY line supports the row's Linux-only scope |
| S502 mfd_noexec | admit | `curl -sSL https://docs.kernel.org/next/userspace-api/mfd_noexec.html`: "memfd_create() without MFD_EXEC nor MFD_NOEXEC_SEAL acts like MFD_NOEXEC_SEAL was set." is present once | agree | Verbatim, 10 words. It justifies passing `MFD_EXEC` explicitly (`kama-live-replay.py:243`) and the stated limit for `vm.memfd_noexec=2` hosts |
| S503 fexecve(3) | reject | `curl -sSL https://man7.org/linux/man-pages/man3/fexecve.3.html`: the quote "the file to be executed is specified via a file descriptor, fd, rather than via a pathname." is present. Its only `/proc` mentions are the glibc ≤2.26 implementation note and an ENOSYS condition | agree | The page documents descriptor exec, not exec of a `/proc/<pid>/fd/<n>` pathname or the resulting `/proc/self/exe` link. Admitting it as grounding for the tool's launch would overreach. The flip condition is concrete |
| S505 ggml-backend-reg.cpp @ b11909 | reject | `curl -sSL https://raw.githubusercontent.com/ggml-org/llama.cpp/b11909/ggml/src/ggml-backend-reg.cpp`: the quote "default search paths: executable directory, current directory" is at **line 491**. `ggml_backend_load_best` starts at line 480, `GGML_BACKEND_DIR` is at 488–489, and `get_executable_path()` starts at line 401 (it uses `readlink("/proc/self/exe")` and strips up to the last `/`) | agree (decision); anchor defect | The source shows cwd is one of several search paths, after a compiled `GGML_BACKEND_DIR`, so "needs cwd" is too strong. For a `/memfd:…` exe the executable directory degenerates to `/`, which matches the L1's "no backends are loaded" probe. But the S505 anchor "lines 422–439" and the lesson's "line 431" do not locate anything at b11909, and seat S5Ggml called the 7-word quote "21 words" (R1) |

New SOURCES rows: the ≤25-word quotes are S500 14, S501 7, S502 10, S503 17 and S505 7 words. All verbatim at their sources, as checked above for S500, S502, S503 and S505.

QUALITY KQ89–KQ93 are present, and all 5 cite a `corpus/lessons/` file. Round-51 D7 is closed.

Discernment: the spot-check agrees with the Gate on 2 of 2 sampled admits and 2 of 2 sampled rejects. The one disagreement is a location defect in a reject's anchor, not its decision.

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | `git diff --numstat 9ff76b1f eb7b16cf -- corpus/knowledge` is empty. Capabilities 11 → 11. Agrees with the lane |
| quality | improved | Both claims verified with the base failures on record. 155/155 restored lines are traced to their deleting commits. The wave-found receipt-checker, probe-scratch and selftest defects are fixed with fail-capable evidence (`integration/m2replay-survivors-killed.out`: five `exit=1`). The four re-opened sources are clean. Agrees with the lane |
| discernment | improved | This outside spot-check agrees with the Gate on 2 admits and 2 rejects, and flip conditions now name what would reopen each reject (round-51 D6). That meets the condition the lane left open in lesson §Spot-check (outside, pending). The S505 anchor defect is routed and does not move the verdict |

## 6. Routed defects (the lane fixes these next round unless marked otherwise)

- **R1 (lane, sources anchor).** S505 `anchor` says "`ggml_backend_load_best`, lines 422–439", and lesson round-52 says the quote is at "line 431". At b11909 the quote is at line 491, the function starts at line 480, and `get_executable_path()` starts at line 401. Seat S5Ggml also counted the quote as "21 words"; it has 7. Append a correction row or erratum with the right lines; do not rewrite S505 in place.
- **R2 (lane, carried C1 limits).** These stay open:
  - a memfd filled from the host install meets (J5HostMemfd); the next reference is a counter-owned extraction;
  - libraries and model load by path (K2Design);
  - the download is not observed;
  - `vm.memfd_noexec=2` hosts cannot run the replay.
  Round-50 carried limits also stay open: probe PATH execution, model bytes rewritten after mapping, and kills during download or readiness.
- **R3 (lane, C2 limits and mutation coverage).**
  - Restoration is byte retention, not visibility: an HTML comment passes (K4Cheat).
  - The counter's `exempt=` rule is simpler than the tool's (L2Slice, 4 SCORECARD lines).
  - The counter's fixtures kill only 2 of 8 tool mutants (M5Fixtures).
  - `corr_lost` counts contract-graded lines only (K7Calib).
- **R4 (lane, carried instrument).** Mistakes #8: nine more committed seat reports were rewritten in place. `seat-report-immutability.py` is planned, not landed.
- **Operator.** Round 52 restores the five `ed135b3c` LOG lines, a reverted craft-hours entry, as history and reverses round 51's disclosure choice (lesson §Gate decision). This needs an operator ruling on whether withdrawn canon may be held as restored history. The lane routed it only in its report and filed no L0 line.
- **Operator, carried L0.** These remain open: the planner seat under the policy-v2 validator (`kama | round-39`), the MISSION axes pair (`kama | round-35`), and the parked worktree (`kama | round-41..43`).
- **Operator, promotion.** All four `SHONEN` boxes are `[~]`. Boxes 1, 2 and 4 look checkable by a non-author:
  - box 1: gate `registered 50 … defective 0` and SKILL §Round-52 instrument registry;
  - box 2: three witnessed b11909 replays whose server runs from a sealed memfd (`measured/c1.out`);
  - box 4: PROVINCE.md is unchanged.
  Box 3 rests on lane seat X4Fresh, which needed lane-tree siblings the docstring does not name. It needs a non-author fresh-session run. Promotion is operator-owned; I marked nothing.
