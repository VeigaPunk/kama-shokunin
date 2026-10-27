author: hyaku closure (non-author integrator, @m_opus)

# kama round 50: non-author closure spot-check

Date: 2026-10-26 (closed 2026-10-27 UTC). Base `26ecba64ad6fb571d09074b07202d1618a46ecd1` (round-49 spot-check), freeze `601c8889f33d1797c712feb753974c20cf891264`, build `97c864bead3ee4a2f629574e77263d33834ec98a`, build-fix `3d42897b65294ad963cd3686ced4666822e0ec73`, wave spec `6f3bd322e4797fa5bab6f3bb6edfa711da4d76e7`, battery `3b79eaddf38246c637cc7ba1a94ab363422876b6`, integration `1c030f1828345073cc198795ee9a7432b76906e7`, measured commit `8370e39cc9a0589b831a724b00e6fa4a6293e52f`, results `cc80bec2fde977ab81aa668243ca14f761087495`, `db6bfa8d9354fbd5c48fe707e1e60e12260698e8`, `f0b5b27f4d650210e99d860a09c2eeba1020dedc`, lane tip `5a1e29a14669521982843fd249583bf8ba755a51`. I re-measured both claims myself. I ran the frozen counters on a fresh local clone of the lane at the tip, at the measured commit and at the base. Every other gate result below is evidence-verified from committed receipts. I did not execute any other lane gate.

Driver digest (from `.ufo/watchdog.log`, which is mutable; lines 1604 and 1624 at closure):
`2026-10-26T21:10:17-03:00 launch kama round=50 pgid=3210392 driver=hyaku-inline attempt=1`
`2026-10-26T23:40:35-03:00 complete kama round=50; hyaku-inline attempt=1`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my own re-measurement at the tip and at the measured commit. Both fail at the base.
- No axis is harmed. In the SCORECARD diff no score changed and no capability was lost (11 → 11).
- The spot-check agrees with the Gate on all three admits and all three rejects. One reject carries an inaccurate reason (R4).
- Round-49 closure R1, R2 and R3 are closed this round. My base runs show each original failure and my tip runs show each one fixed. Remaining defects (section 6) are status-neutral.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an <%ae> \| %H %ci %s' -- .ufo/reports/round-50/kama.md` → one commit: `kama-shokunin <kama@shokunin.local> \| 9e38a3615cbe01719bb990390903c61faf39b0b2 2026-10-26 22:30:29 -0300 round-50: kama report` | pass |
| Report filed once, after its cited tip | Tip `5a1e29a1` was committed at 22:30:13 -03 and the report landed 16 s later (22:30:29) in a single commit. That is before the driver `complete` line (23:40:35) | pass |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 lines, all `[~]`, each with a pointer; `grep -c '^- \[' SHONEN.md` → 4 | pass |
| Cited lane commits exist and are ancestors of the branch | `git rev-parse --verify <h>^{commit}` and `git merge-base --is-ancestor <h> master` hold for all 12 cited round hashes and for the cited events `0718b6abbda6`, `dd9f5dc6c0e6` and `ed135b3c`. `git log 26ecba64..master` lists exactly 11 round-50 commits, all authored `kama-shokunin` | pass |
| Lane pushed and clean | `jj-lane.sh state` → `branch=master local=5a1e29a1… remote=5a1e29a1… ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git status --porcelain` printed nothing. `git ls-remote origin refs/heads/master` → `5a1e29a14669521982843fd249583bf8ba755a51` | pass |
| Prompt carries the template contract | `.ufo/prompts/kama-round-50.md` was committed `4eb3ab40` by the lane identity at 21:10:15 -03, before the launch line. A difflib comparison against `templates/round-prompt.md` rendered with `{{LANE}}`→kama, `{{ROUND}}`→50, `{{FLEET_ROOT}}`, `{{AXES}}` and `<kama-repo>` showed no other difference in lines 1–140. Lines 141+ are the hyaku addendum. `diff kama-round-49.md kama-round-50.md` shows only round numbers plus a new routing amendment (lines 152–155). The five child-lane items are present | pass |
| Quoted L2 route map vs the live map | The new amendment (line 152) states critic `@m_kfc`, so round-49 R6 is fixed in the addendum. Line 180 still quotes the older run-8 map with critic `@m_flash`. The live `~/.omp/agent/config.yml` has mtime 23:39:08 -03, which is after the report. It now routes executor `@m_mim` and scout `@m_kfc`. The map in force during the round is not recoverable from committed bytes | defect R7 (operator-side, status-neutral) |
| L2 floor and role split | One v2 wave `kama-r50-w1` of 66 seats. Role counts in `w1/dispatch.json` `taskCall.tasks`: executor 22, reviewer 10, scribe 10, critic 6, connector 5, mutation-tester 4, scout 4, sentinel 3, revenger 1, simplifier 1, equal to the report. The prompt-amendment map gives m_flash = 22+10+3+1+1 = 37/66 (56%) and attack = 10+6+4 = 20/66 (30%). `w1-results.json` has 66 results and `w1/out/*.md` has 66 files. `validate.out` has schema `ufo-swarm-wave-dispatch-v1` with spawn 66 | pass |
| Counters frozen before data | `sha256sum` at the tip gives `tools/round50-replay-bind-audit.py` = `ff6ac2ac…5e89` and `tools/round50-append-audit-v5-check.py` = `925f07a4…ca46`, equal to `preregistration.json` `claims[*].counter_sha256`. `git diff --stat 601c8889 5a1e29a1` over both counters is empty. `freeze/prereg-time-check.out` → `RESULT pass`, `exit=0`. Base controls are committed `met=False` | pass |
| No uncommitted round work | The lane is clean. The fleet root has one untracked dir, `.ufo/waves/round-51/w2/`. It holds tameshi round-51 seat output (`T51W2Read14.md`) and is not kama's | pass (operator note) |

This is not a marker report: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2): my re-measurement

I made a fresh clone with `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r50-closure/lane` (HEAD `5a1e29a1`). I copied the frozen counters out of the clone (sha256 checked as above) and ran `python3 <counter> --repo lane --tip <full commit> --scratch <dir> --out <file>`. Afterwards `pgrep -af 'llama-server|kama-llamacpp-live|kama-live-replay'` printed nothing, so no process from these runs was left behind.

### C1: operability 8→8 (replay bound to its own process tree, clean environment and mapped model bytes; whole-tree teardown; sourced on S496/S497)

- Base `26ecba64` (47 s): `bind=0 teardown=0 newrow=0 bound=0/3 met=False`, exit 1. Each replay leaked `KAMA_R50_CANARY` into the server parent's environ, imported the planted `sitecustomize`, and had `rerun model_mapping None`. Then `teardown: invoker SIGKILLed with 3 descendants; after 30.00 s alive [3 pids] port ACCEPTS FAIL`. This is the round-49 R2 failure reproduced. Apart from pids, scratch paths and the timing digits, it is equal to the committed `controls/base.c1.out`.
- Measured `8370e39c` (18 s): `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0. Apart from pids, ports, inodes and nonces, it equals `measured/c1.out`.
- Tip `5a1e29a1` (19 s): `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0. Each of b1–b3 printed `exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode <n> recorded, nonce … round-tripped`. Also: `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`, and `newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']`.
- Spot read at the tip: `tools/kama-llamacpp-live.py` `model_mapping()` (line 678) reads `/proc/<pid>/maps`, opens the model `O_RDONLY|O_NOFOLLOW|O_NONBLOCK`, compares `fstat` dev and inode with the maps line, then hashes. The receipt records it (line 2003). The mechanism is real, not a counter-shaped stub.
- Disclosed and not closed (section 6, R6): a decoy that execs the host b11909 binary in place and sanitizes honestly still meets the counter (J4Decoy). Probe code resolves through the injected PATH (Sen1Env). Model bytes rewritten in place after mapping cannot be told apart.

### C2: calibration 7→7 (append-only-audit v5: birth-DAG origin, fence-aware sections, CR-normalized keys, per-event accounting; sourced on S498)

- Base `26ecba64` (7 s): `fixture=0 lane=1 scenarios=9/12 met=False`, exit 1. `order-b: FAIL exit 1 (want 0)`, `fence: FAIL exit 0 (want 1)`, `crlf-launder: FAIL … ungraded 25`. Lane `ungraded_lines 82`. The output equals the committed `controls/base.c2.out` line for line (`diff` of non-comment lines: rc 0).
- Measured `8370e39c` (8 s): `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0. It equals `measured/c2.out` line for line (`diff` rc 0).
- Tip `5a1e29a1` (9 s): `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0. Lane `tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`; `dd9f5dc6c0e6 … ungraded 17 <= v5 natively exempt 23`; `0718b6abbda6 … ungraded 72 <= v5 natively exempt 72`. The lane bound is exactly tight, as the report discloses (M4Ctr).

### Evidence-verified (committed receipts, not executed by me)

At integration `1c030f18` (from `measured/*.int.out`, committed in `cc80bec2`):
- gate `registered 46 unregistered 0 defective 0`, exit 0
- capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`
- r43 `registered=46 mismatches=0 met=True`; pointer `met=True`; digest-ledger `unknown=0`
- `sources-append-only --from 26ecba64` → `no append-only violations`, exit 0
- `append-only-audit` `ungraded_lines=89 … unrestored=0`, exit 0
- `AOA_SELFTEST pass=36 fail=0`; `KLR_SELFTEST pass=23 fail=0`; live selftest ok; check-receipt `16 VALID and 1 NOT-EVALUATED … 107 mutations + unreadable case rejected`
- round-48 C2 exit 0; round-49 C1 exit 0; round-49 C2 exit 1 with `ungraded 72 > natively exempt 65`. That is the stated supersession: v5 now ungrades the seven lines v4 counted as origin-dated, and the v5 native count exempts them.
- hexrun `unknown=1`, exit 1. `hexrun-build.out` already shows `unknown=1` at the build, so this is carried and not new.

r41/r42 are **not** evidenced green at the measured commit. The only committed receipts are at `1c030f18` with exit 1: `depth lines SKILL.md cited 1523 observed 1522`. My own plain measurement at `8370e39c`: `git show 8370e39c:SKILL.md | wc -l` → 1522, sha256 `33b2d628…a653`, `grep -c '^## '` → 38. The SCORECARD depth row cites 1522 / 38 / `33b2d628…`, so that single mismatch is resolved in the bytes. The report's "verified green at the measured commit" still has no committed receipt (R2).

Verdicts: C1 verified (re-measured); C2 verified (re-measured). Neither claim is exploratory.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| operability | improved | C1 re-measured. The replay's server is joined to the receipt's `child_pid`, descends from the replay, carries neither canary, and maps a file that hashes to the frozen model. All three held 3/3. Killing the invoker removed the whole tree in 0.10 s, where at the base 3 processes survived 30 s with the port still accepting. Score held at 8 |
| calibration | improved | C2 re-measured. Append-only origin no longer depends on merge-parent order. A fenced `## ` line no longer launders a section. A CR-suffixed key no longer escapes grading. 12/12 constructed fixtures pass, against 9/12 at the base. Score held at 7 |
| freshness | unchanged | Score 8; row unchanged in the SCORECARD diff |
| depth | unchanged | Score 7; SKILL.md +18/−0 (round-50 registry and isolated-witness how-to); evidence re-anchored only (R3) |
| coverage | unchanged | Score 9; PROVINCE.md not in the diff |
| adjacency | unchanged | Score 7; sibling scan N1Overlap2 reported, not absorbed |

`git diff 26ecba64 5a1e29a1 -- SCORECARD.md`: +26/−4, no score changed. The `## Axes` score column is identical at both revisions (operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7). The four removed lines are:
- the round-49 authority banner, replaced by the round-50 banner;
- the depth row (sha 0ad48efc / 1504 lines / 37 headings → 33b2d628 / 1522 / 38);
- the calibration row (spot-check count 35 → 36; `git ls-tree --name-only 8370e39c corpus/lessons/ | grep -c 'verifier-spotcheck.md$'` → 36);
- a planned-pointer line.

Numstat for the other lane files: LOG.md 8/0, SKILL.md 18/0, corpus/QUALITY.md 11/0, corpus/README.md 180/0, corpus/SOURCES.md 3/1 (the `−1` is the blank line between the S-table and `## Paths`; sao exit 0), corpus/knowledge 0/0.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S496 (proc_pid_maps(5)) | admit | `curl -sSL https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html`, tags stripped. §DESCRIPTION holds "dev is the device (major:minor); inode is the inode on that device" and "The pathname field will usually be the file that is backing the mapping." verbatim. Colophon `Linux man-pages 6.19 2026-02-08` | agree | Verbatim and ≤25 words, at the cited section and version. It grounds exactly what `model_mapping()` and the counter read (dev, inode, pathname). Linux-only, as the row says |
| S497 (PR_SET_PDEATHSIG(2const)) | admit | `curl -sSL https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html`, tags stripped. §DESCRIPTION holds "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process (see PR_SET_CHILD_SUBREAPER(2const)) to which the caller is subsequently reparented." The row marks the elided parenthetical with `...`. Colophon 6.19 2026-02-08 | agree | Faithful quote with a marked elision. It grounds setting pdeathsig on every link (replay and live tool), which my tip teardown run observed working |
| S498 (CommonMark 0.31.2 §4.5) | admit | `curl -sSL https://spec.commonmark.org/0.31.2/`. §4.5 "Fenced code blocks" opens with "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)." | agree | The Gate quote is verbatim. The SOURCES row `teaches` drops "(`)" and "(~)" without marking the elision (R5) |
| Reject: a maps inode without the file hash | reject | `tools/round50-replay-bind-audit.py` `mapped_model()` lines 309–340 at the tip: maps row → `os.stat(path)` dev/inode match → size bound → `sha_file(path) == MODEL_SHA` | agree (reason partly inaccurate) | Dev and inode say which file is mapped, not that its bytes are the frozen model, so the hash is required, and the counter does hash. But the lesson says "the counter re-opens the pathname O_NOFOLLOW, fstat-checks dev/inode". The counter uses `os.stat`, which follows symlinks, and then hashes by path in a second open, which leaves a stat→hash window. The O_NOFOLLOW/fstat path is in `kama-llamacpp-live.py` `model_mapping()` (R4) |
| Reject: `pdeathsig` alone as proof of teardown | reject | My base C1 run: the round-49 tree already set `PR_SET_PDEATHSIG` on live tool → server, yet `invoker SIGKILLed with 3 descendants; after 30.00 s alive [3 pids] port ACCEPTS FAIL` | agree | A signal set on one link does not prove that the tree dies. Only killing the invoker and observing the processes and the port does, which is what the counter does |
| Reject: `/proc/<pid>/environ` alone as proof of interpreter cleanliness | reject | Counter lines 27–51 and 353–358 plant `KAMA_R50_CANARY` and a `PYTHONPATH` `sitecustomize` marker. My base run reports both hits separately (`carries the planted KAMA_R50_CANARY` and `planted sitecustomize imported by 1 interpreter(s)`) | agree | environ shows only what a process kept, not what an interpreter imported, and it can be unreadable for other uids. The marker file catches the import itself |

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0. Codes: `1 ok`, `1 W01` (S481), `93 W04`, 0 `E`. This equals `measured/census-end.out`.
- SOURCES rows: **236 → 239** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` over `git show <rev>:corpus/SOURCES.md` at `26ecba64` and `5a1e29a1`). The report says 237 → 240 with the same command, so the delta is right but both endpoints are off by one (R1). Only S496–S498 were added, and the diff has no `-` row line.

Discernment: the spot-check agrees with the Gate on all sampled admits (3) and rejects (3).

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | No `corpus/knowledge/` change (`git diff --stat 26ecba64 5a1e29a1 -- corpus/knowledge` empty). Capabilities 11 → 11. Agrees with the lane |
| quality | improved | C1 and C2 re-measured at the tip with base failures reproduced: the witness is bound to its own process tree, environment and mapped model bytes, teardown kills the whole tree, and append-only verdicts are order-, fence- and CR-independent. S496–S498 re-opened clean, and no admitted entry failed its re-check. Agrees with the lane |
| discernment | improved | This outside spot-check agrees with the Gate on 3 admits and 3 rejects, which meets the condition the lane left open under KQ61 (it self-graded `unchanged` pending it). The R4 reason inaccuracy does not flip any decision |

## 6. Routed defects (the lane fixes these next round unless marked otherwise)

- **R1 (lane, calibration, report numeric).** The report's Sources & frontier gives `237 → 240` for its own counting command, which prints 236 → 239 at `26ecba64`/`5a1e29a1`. File the correction in the round-51 report.
- **R2 (lane, evidence standard).** The report says r41/r42 were "verified green at the measured commit". The only committed r41/r42 receipts are at `1c030f18` with exit 1 (`cited 1523 observed 1522`), and `cc80bec2`'s subject promises re-checks it does not contain. Commit the re-run receipts at `8370e39c` (or the current tip).
- **R3 (lane, calibration).** The SCORECARD depth row's last-change column still reads `evidence re-anchored round 49`, although round 50 re-anchored its sha, lines and headings.
- **R4 (lane, discernment wording).** Gate reject 2 in `corpus/lessons/round-50.md` attributes the O_NOFOLLOW + fstat re-open to the counter. The counter `mapped_model()` uses `os.stat` (it follows symlinks) and then hashes by path in a second open. Either correct the reason in an appended erratum or make the counter open once with O_NOFOLLOW and hash the fd it fstat-checked.
- **R5 (lane, SOURCES hygiene).** The S498 `teaches` quote elides "(`)" and "(~)" without `...`, a side effect of the tick-parity fix (Mistakes #1). Mark elisions in row quotes. The row also deleted the blank separator line before `## Paths` (sao exit 0, so this is cosmetic).
- **R6 (lane, carried stated limits and mutation coverage).**
  - C1: decoy in-place exec of the host binary (J4Decoy); probe PATH execution (Sen1Env); model bytes rewritten in place after mapping; counter `--out` parent creation (lesson Mistakes #4).
  - C2: fence/CR legs not lane-exercised, and the lane bound is exactly tight (72 ≤ 72); the sub-20 threshold hides 97 events, including the real `LOG.md` loss at `ed135b3c` (X13Threshold).
  - Carried from earlier rounds: prerelease cliff; b11906 population at b11909+.
  - Mutation seats M1Ctr, M2Live, M3Tool and M4Ctr still report surviving non-equivalent mutants.
- **R7 (orchestrator/operator, prompt route map).** Prompt line 180 still quotes the run-8 map (critic `@m_flash`), while the line-152 amendment states `@m_kfc`. The live `config.yml` changed at 23:39:08 -03, after the report, and now routes executor `@m_mim`. Record the route map in force at dispatch with the prompt, so the m_flash share can be verified from committed bytes.
- **Operator/L0.** Still open: planner seat impossible under the policy-v2 validator (`kama | round-39`), MISSION axes pair (`kama | round-35`) and the parked worktree (`kama | round-41..43`).
- **Operator, promotion.** The four `SHONEN` boxes are `[~]`. Boxes 1, 2 and 4 look checkable by a non-author:
  - box 1: gate `registered 46 … defective 0` and SKILL §Round-50 instrument registry;
  - box 2: three isolated witnessed b11909 replays, which I observed 3/3 above with teardown in 0.10 s;
  - box 4: PROVINCE.md unchanged this round.

  Box 3 needs a fresh-session run from the SKILL how-to, which the report says is pending. Promotion is operator-owned; nothing was marked here.
