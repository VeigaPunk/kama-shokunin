author: hyaku closure (non-author integrator, @m_opus)

# kama round 51: non-author closure spot-check

Date: 2026-10-27 (closed 2026-10-27 UTC). Base `57a2e25bf702b03aa61f9265e968cf68058ecb82` (round-50 spot-check), freeze `804bde75164444bdf0fe6783d7aa45774bf562bd`, build `b6bed925b032ac2c19b63ef4af358ebdd5922c26`, build-fix `73bf2a7a17104a62a3e442912c8776cbd8dedbd5`, build-fix 2 `138af25b963450b6520794995605fa7dbbcd87e0`, wave spec `4eca4892`, integration `c5ec93d5b8b8759d5c2fa7a092c7375c875b04bc`, measured commit `be8169a667301dc2b8118615e262968266959303`, results `1ab1de39`, lane tip `b1d7b7aee5d05ffb43f99cf4bc20af00fc6865c6`. I re-measured both claims myself: I ran the frozen counters on a fresh local clone at the base, the measured commit and the tip. Two read-only reviewer seats I dispatched (not lane seats) verified the prompt fidelity and the committed receipts; I cite what they observed.

Driver digest (from `.ufo/watchdog.log`, which is mutable):
`2026-10-26T23:50:04-03:00 launch kama round=51 pgid=3034560 driver=hyaku-inline attempt=1`
`2026-10-27T00:16:15-03:00 lane-dead-no-report kama round=51; retry same round (hyaku-inline attempt=1: attempt 1 L1 KamaR51 died in the orchestrator session exit 2026-10-26 23:57:36 -03 (SIGHUP during an operator omp update); no report; killed 7 min after launch, no lane writes)`
`2026-10-27T00:16:24-03:00 launch kama round=51 pgid=889077 driver=hyaku-inline attempt=2`
`2026-10-27T01:12:23-03:00 complete kama round=51; hyaku-inline attempt=2`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my re-measurement at the measured commit and at the tip. Both fail at the base.
- No axis is harmed. In the SCORECARD diff no score changed and no capability was lost (11 → 11).
- The spot-check agrees with the Gate on the one admit (S499) and on the three rejects I sampled.
- Round-50 closure R1–R5 and R7 are answered. R6 is answered for its C1 decoy and C2 threshold parts; the rest is carried.
- The round was filed before WAVE-DONE, with 15–16 seats still running. Those seats are still writing into the lane worktree (section 1). This is a status-neutral conformance defect.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H %ci %s' -- .ufo/reports/round-51/kama.md` → one commit: `kama-shokunin 39877b174e99927521246dd449486a68f72bfaee 2026-10-27 01:11:05 -0300 round-51: kama report` | pass |
| Report filed after its cited tip and before `complete` | Tip `b1d7b7ae` was committed at 01:10:06 -03 and the report landed at 01:11:05. The driver's `complete` line is at 01:12:23 | pass |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 lines, all `[~]`, each with a pointer | pass |
| Cited lane commits exist and are ancestors of the branch | `git rev-parse --verify <h>^{commit}` and `git merge-base --is-ancestor <h> master` hold for every hash cited in the report: the 9 round commits, the base, and the events `97c864be` and `ed135b3c`. `git log 57a2e25b..b1d7b7ae` lists exactly 9 commits, all authored `kama-shokunin`, all committed before the report | pass |
| Lane pushed | `jj-lane.sh state` → `branch=master local=b1d7b7ae… remote=b1d7b7ae… ahead=0 behind=0 head=detached tracked=1 untracked=29`. `git ls-remote origin refs/heads/master` → `b1d7b7aee5d05ffb43f99cf4bc20af00fc6865c6` | pass |
| No uncommitted round work | `git status --porcelain` shows 1 modified and 29 untracked paths, all under `.ufo/waves/round-51/a2w1/out/`. They are M1Ctr (`mu11–mu18.out`, `runs/`), M2Live (`evidence/*`, `proposals/`), V3Review (`V3Review.md`, `V3Review/`), and an in-place rewrite of the committed `X7Regen.md` (13+/13−, same verdict, reworded). These are seats that were still running when the report was filed | defect D1 (status-neutral) |
| Prompt carries the template contract | Reviewer seat R51PromptConform. Both prompt commits are by the lane identity before each launch: `c41732ca` at 23:50:02, and `646f4348` at 00:16:23. It rendered `templates/round-prompt.md` (kama, 51, fleet root, the AXES line, `<kama-repo>`) and compared it with §1–5 using difflib: ratio 1.0, 140/140 lines, 0 non-placeholder differences. The five child-lane items and the round-level items are present. Compared with the round-50 prompt, the only substantive change is the §6 routing amendment chain and its "Current map" | pass |
| Quoted L2 route map vs MISSION and live map | Prompt §1–5 quote no `@m_*`. The §6 "Current map" matches the committed Sen4Policy receipt on every dispatched role: executor `@m_mim`, reviewer/mutation-tester `@m_zfl`, critic/scout `@m_kfc`, connector `@m_antigravity`, scribe/sentinel/revenger/simplifier `@m_flash`. That receipt records config mtime `2026-10-27T02:39:08Z` and sha256 `0d5874660274…`. Fleet `MISSION.md` names no aliases. Round-50 R7 is closed | pass |
| L2 floor and role split | `a2w1/dispatch.json` (`ufo-swarm-wave-dispatch-v1`, spawn 66): executor 18, reviewer 11, critic 9, scribe 7, mutation-tester 5, scout 5, sentinel 4, connector 4, revenger 2, simplifier 1. That equals the report. Attack share is 25/66. `validate.out` = `exit=0`. `w1-results.json` is absent at the tip, as the report states | pass |
| Seat count at filing | The report says 50 of 66 seat reports were in hand and lists 16 still running, V1Review among them. At `1ab1de39` there are **51** committed seat reports: `V1Review.md` (11,579 B) is already there. So 15 were missing | defect D2 (bookkeeping, status-neutral) |
| WAVE-DONE before report | The report discloses that it was filed without WAVE-DONE, under an operator budget notice | defect D1 (disclosed) |
| Counters frozen before data | Counter sha256 at the tip: `e5753c45…5155` and `254e63ba…1660`. These equal `preregistration.json` `claims[*].counter_sha256`. `git diff --stat 804bde75 b1d7b7ae -- tools/round51-*.py` is empty. `freeze/prereg-time-check.out` → `RESULT fail`, exit 1: `frozen_at_utc` is 6 s after the commit time. The KQ64 check fired as built, and an erratum is committed. The freeze time of record is the commit time, which is before the build `b6bed925` (00:39:06) | pass (self-caught timestamp defect, erratum on record) |

This is not a marker report: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2): my re-measurement

Setup: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/closure-kama-r51/lane` (HEAD `b1d7b7ae`). I copied both counters out of the clone and their sha256 matched the preregistration. I ran `TMPDIR=<run dir> python3 <counter> --repo lane --tip <full commit> --scratch <run dir> --out <file>`. Afterwards no `llama-server`/`kama-llamacpp-live`/`kama-live-replay` process from these runs remained.

### C1: operability 8→8 (the replay's server is the file the replay extracted; sourced on S499)

- Base `57a2e25b` (17 s): `bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False`, exit 1. `own b1: own: rerun server_exe None does not record the observed image ('103:05', '2092454134')`; `replay own_server None does not name the observed member file`. This equals the committed `controls/base.c1.out` verdict.
- Measured `be8169a6` (17 s): `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0. This equals the verdict in `measured/c1.out`.
- Tip `b1d7b7ae` (17 s): `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0. Each of b1–b3 printed `running image 103:05:<inode> is the extracted member, recorded in server_exe and own_server`, with three distinct inodes. Teardown: `invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`. Newrow: `1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']`.
- Spot read at the tip:
  - The counter's `own_exe()` (lines 351–379) opens `/proc/<pid>/exe`, fstats the fd and hashes the same fd. It compares dev:inode with `os.stat` of the replay's member.
  - `tools/kama-live-replay.py` (lines 366–382) refuses a rerun when `server_exe` is absent, has another digest, or names another dev:inode. It also refuses `st_nlink != 1` on the member fd it holds.
  - The mechanism is real, not a counter-shaped stub.
- Disclosed and not closed:
  - A byte-identical copy at the member path still meets the counter (J3CopyDecoy, a preregistered limit).
  - The frozen counter's own leg accepts a hardlinked member (J4Hardlink). The replay now refuses it; the counter does not test it.
  - J4Hardlink's `[INFERENCE]`: `nlink == 1` does not prove extraction provenance, because a file renamed over the member path would pass.
  - The download is not observed.

### C2: calibration 7→7 (append-only-audit v6: threshold 1, A-row rule, named disclosures)

- Base `57a2e25b` (4 s): `fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False`, exit 1. Every disclosure fixture exits 2 with `unrecognized arguments: --disclosures`. The lane leg reads `tool definition v5 threshold 20`. This equals `controls/base.c2.out`.
- Measured `be8169a6` (5 s): `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=165 met=True`, exit 0. Lane: `tool v6 threshold 1 exit 0 events 107 disclosed_lines 165 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 165`. I diffed my non-comment lines (scratch paths stripped) against the committed `measured/c2.out`. The only differences are the receipt's command header and its `exit=0` line, so the content is identical.
- Tip `b1d7b7ae` (6 s): identical to the measured run.
- Every bad-disclosure fixture exits 1 at the measured commit and at the tip: junk key, over-count, wrong class, no event, partial disclosure, and two-files-one-commit (the shadow-index case).

### Evidence-verified (committed receipts, not executed by me; reviewer seat R51EvidenceRecheck)

All of these were measured at `tip=be8169a6`:
- gate `registered 48 unregistered 0 defective 0`, exit 0
- cap `listed 11 observed 11 missing 0 unsubstantiated 0 met True`
- r41 `mismatches=0 met=True`; r42 `mismatches=0 maxN=51 met=True`; r43 `registered=48 mismatches=0 met=True`
- digest `unknown=0`; hexrun `unknown=0`, against base `unknown=2` (`X2Battery/runs/hexrun-base.out`, `tip=57a2e25b`)
- sao `added S499 (allowed)`, `no append-only violations`
- aoa `unrestored=0 partial=0 regressed=0 bad_disclosures=0`
- `AOA_SELFTEST pass=51 fail=0`, `KLR_SELFTEST pass=27 fail=0`, live `selftest: ok`
- r50c1 `met=True`; r50c2 `lane=0 … met=False`. The report states this as the v6 supersession.

Round-50 R2 (receipts at the measured commit) is therefore closed.

Planned pointer: the report says `met=True` at the final tip `1ab1de39`. The committed `measured/pointer.out` (at `be8169a6`) and `pointer-int.out` (at `c5ec93d5`) both read `dangling reference §Round-51 measured results`, `met=False`, exit 1. No pointer receipt exists at `1ab1de39`. The fact holds in the bytes: `git grep -n '### Round-51 measured results' 1ab1de39 -- SCORECARD.md` → line 2925, and the section is absent at `be8169a6`. But the cited receipt does not exist (D3).

Seat agreement (receipts): R1Rerun and R2Rerun show base `met=False` and build met ×2. X9Agree is deterministic. Controls J1NoRecord, J2DecoyHost, J5NoLedger, J6NoArow, J7Thresh20 and J8OneClass (v1/v2/v3/p1) are all `met=False`.

X7Regen compared a **scoped** slice at `138af25b`: 142 rows on each side, `only_in_regen=0 only_in_ledger=0`. By assignment it excludes SCORECARD.md (24 rows) and the two `only=` files. The report's phrase "an independent ledger regeneration matches exactly" therefore covers 142 of the ledger's lines, not all 165/166 (D4). Between `138af25b` and `be8169a6` the ledger lost only the round-49 banner row (SCORECARD.md), which sits outside that slice.

Verdicts: C1 verified (re-measured); C2 verified (re-measured). Neither claim is exploratory.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| operability | improved | C1 re-measured. The replay now binds its rerun to the exact running image by dev:inode of its own extracted member. At the base the tools recorded no `server_exe`/`own_server` (owned 0/3); at the measured commit and tip 3/3. The digest-identical host-install decoy is now refused (J2DecoyHost `own=0`). Score held at 8 |
| calibration | improved | C2 re-measured. v6 grades every deletion (threshold 1, 107 events, against v5's 20-line threshold), applies the A-row rule (58 permitted lines), and names every unheld line in a ledger whose bad rows exit 1. 9/9 scenarios pass, against 0/9 at the base. The SCORECARD calibration/depth re-anchors (37 spot-checks; SKILL `3b2425b7…`/1541/39) re-derive exactly. Score held at 7 |
| freshness | unchanged | Score 8; row unchanged in the SCORECARD diff |
| depth | unchanged | Score 7; SKILL.md +19/−0 (round-51 registry); evidence re-anchored only |
| coverage | unchanged | Score 9; PROVINCE.md not in the diff |
| adjacency | unchanged | Score 7; N1Overlap reported overlaps, not absorbed |

`git diff 57a2e25b b1d7b7ae -- SCORECARD.md`: 39 added, 4 removed, and no score changed. The `## Axes` score column is identical at both revisions (8/8/7/9/7/7). The four removed lines:
- the round-50 banner, re-appended byte-exact under §Superseded head banners; the round-49 banner is also restored byte-identical to `24e906f0`;
- the depth row;
- the calibration row;
- `Planned (round 51)` → `(round 52)`.

Numstat for LOG.md, SKILL.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md and the lesson has zero deletions. `corpus/knowledge/` has no diff.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S499 (proc_pid_exe(5)) | admit | `curl -sSL https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html`, tags stripped: `quote-present: True` for "This symbolic link can be dereferenced normally; attempting to open it will open the executable."; colophon `Linux man-pages 6.19 2026-02-08`. The first attempt failed with `curl: (7) Failed to connect`. The local `man 5 proc_pid_exe` (pacman `man-pages 6.19-1`) has the same §DESCRIPTION text and also states the ` (deleted)` suffix and the `PTRACE_MODE_READ_FSCREDS` check, as the row's `scope` says | agree | Verbatim, 15 words, at the cited section and version. It grounds exactly what `own_exe()` and the live tool do: open the link and fstat/hash the opened image. Tier A man page, Linux-only, as scoped |
| Reject: an exe digest alone as proof of which file a replay runs | reject | `.ufo/waves/round-51/a2w1/out/J2DecoyHost.md`: a decoy exec'ing the host install `/home/vgpnk/.local/opt/llama-b11909/llama-server` (byte-identical to the frozen digest). Result: `bind=1 own=0 … owned=0/3 met=False`. The same tree without the decoy (`138af25b`) gives `met=True`. My base C1 run shows `bind=1` with every digest leg passing while `own=0` | agree | Every digest test passed on the foreign file; only dev:inode identity told the two files apart. The reject is grounded by a discriminating control |
| Reject: a member path's dev and inode as proof of extraction when the file has other links | reject | `J4Hardlink.md`: the xfs hardlink decoy met the frozen counter, `bind=1 own=1 … met=True`, all three on inode `103:05:1890860146`. `tools/kama-live-replay.py:381` now appends `server-exe:member-links:<n>` when `fstat(own_fd).st_nlink != 1` | agree | A hardlink shares the inode, so dev:inode alone cannot tell the extracted member from a linked foreign file. The replay refuses it. The frozen counter still accepts it (disclosed). The seat's `[INFERENCE]` (rename-over) remains, so "Flip: never" overstates closure of the class; the reject itself is right |
| Reject: a disclosure ledger whose rows are not bound to real deleted lines | reject | My own C2 runs at `be8169a6` and `b1d7b7ae`: `bad-disclosure-1..4: exit 1 (want 1) ok` and `partial-disclosure: exit 1 (want 1) ok`. At the base all of these exit 2 because v5 lacks `--disclosures` | agree | A ledger row that names no event, no unheld line, too many lines or the wrong class fails the audit, so a ledger cannot launder a loss |

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0. 96 lines: `1 ok`, `1 W01` (S481, tier C mined), 94 `W04`, 0 `E`. This equals the committed `census/end.out`.
- SOURCES rows: **239 → 240** (`git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` at `57a2e25b` and `b1d7b7ae`). This equals the report, so round-50 R1 is closed. The diff adds S499 and the blank separator (round-50 R5) and removes nothing.
- QUALITY KQ85–KQ88 are present (lines 440–443). The last column of KQ85 and KQ88 cites `corpus/lessons/round-51.md` (KQ88: Mistakes #3). KQ86 cites `C2; round-50 R6; considerthese/2026-10-26.md proposal 1` and KQ87 cites `C2; KQ22`; neither names a lesson (D7).

Discernment: the spot-check agrees with the Gate on the sampled admit (1 of 1) and on every sampled reject (3 of the 5 rejects sampled; all 3 agree).

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | `git diff --stat 57a2e25b b1d7b7ae -- corpus/knowledge` is empty. Capabilities 11 → 11. Agrees with the lane |
| quality | improved | C1 and C2 re-measured, with the base failures reproduced. The witness server is identified by the running file, and append-only grading sees every deletion and names every loss. Hexrun unknowns go from 2 to 0 (receipt). S499 re-opened clean. No admitted entry failed its re-check. Agrees with the lane |
| discernment | improved | This outside spot-check agrees with the Gate on 1 admit and 3 rejects. That meets the condition the lane left open under KQ61 (it self-graded `unprovable-but-better` pending this check) |

## 6. Routed defects (the lane fixes these next round unless marked otherwise)

- **D1 (lane, conformance; disclosed).** The report was filed before WAVE-DONE: 15 seats were still running.
  - Their outputs are landing as uncommitted lane-worktree files: M1Ctr `mu11–mu18.out`/`runs/`, M2Live `evidence/`/`proposals/`, V3Review.
  - X7Regen rewrote its committed `X7Regen.md` in place (13+/13−).
  - Next round: commit the late seat outputs as a separate dated append, with any findings that change a verdict routed. Restore `X7Regen.md` to its committed bytes or file the rewording as a new file, since a committed seat report is not edited in place. Write the `w1-results.json` the report promised.
- **D2 (lane, calibration, report numeric).** The report says it landed with "50 of 66" seat reports and lists V1Review as still running. `1ab1de39` holds 51 seat reports, V1Review among them. File the correction (51/66, 15 running) in the round-52 report.
- **D3 (lane, evidence standard).** The report and SCORECARD claim "planned-pointer `met=True` at the final tip `1ab1de39` (receipt at the final tip)". No such receipt is committed. The committed pointer receipts (`be8169a6`, `c5ec93d5`) read `met=False`. Commit the pointer re-run at `1ab1de39` or the current tip.
- **D4 (lane, calibration wording).** "An independent ledger regeneration matches exactly" (report, C2): X7Regen compared a scoped 142-line slice at `138af25b` that excludes SCORECARD.md and the `only=` files. State the scope wherever the agreement is cited.
- **D5 (lane, carried stated limits and mutation coverage).**
  - C1:
    - Copy decoy (J3CopyDecoy).
    - Hardlink accepted by the frozen counter (J4Hardlink). The replay refuses it; the next counter should test it.
    - Rename-over-member provenance (J4Hardlink `[INFERENCE]`). A counter-owned extraction is the stronger reference.
    - Download not observed. Non-atomic snapshots (K1Design3).
  - C2:
    - Region-restricted files are only bound-checked (J8 p1).
    - Mechanical classes, not judged reasons.
    - As frozen, the counter does not test the ledger cutoff.
  - Carried from earlier rounds: prerelease cliff (b11909 vs upstream b11913), b11906 population. Mutation seats M1Ctr/M2Live were unreported at filing.
- **D6 (lane, Gate wording).** Rejects 1–3 carry "Flip: never". J4Hardlink's own `[INFERENCE]` shows the nlink rule is not a complete provenance proof. A reject's flip condition should name what would reopen it.
- **D7 (lane, QUALITY citation).** LEARNING.md requires every `QUALITY.md` criterion to cite the lesson that produced it. KQ86 and KQ87 cite the claim, R6/considerthese and KQ22, but no lesson file. A lesson does stand behind both: round-50 R6 lives in `corpus/lessons/round-50-verifier-spotcheck.md`, and the round-51 lesson's C2 text states both rules. So this is a citation-form defect, not a criterion without a lesson, and it does not move the discernment verdict. Append a superseding row or an erratum that names the lesson file.
- **Operator/orchestrator.**
  - Round-50 R7 is closed: the prompt's §6 "Current map" matches the committed Sen4Policy receipt.
  - Sen4Policy F1 (`scripts/hyaku/hyaku.env:8-11` run-9 labels stale) is operator-side.
  - Still open: planner seat impossible under the policy-v2 validator (`kama | round-39`), MISSION axes pair (`kama | round-35`), and the parked worktree (`kama | round-41..43`).
- **Operator, promotion.** The four `SHONEN` boxes are `[~]`. Boxes 1, 2 and 4 look checkable by a non-author:
  - box 1: gate `registered 48 … defective 0` and SKILL §Round-51 instrument registry;
  - box 2: three witnessed b11909 replays, each bound to its own extracted server, which I observed 3/3 at the tip with teardown in 0.10 s;
  - box 4: PROVINCE.md unchanged this round.

  Box 3 rests on seat X1Fresh, which is a lane seat. It needs a non-author fresh-session run from the replay docstring. Promotion is operator-owned; nothing was marked here.
