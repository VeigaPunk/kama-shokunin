author: hyaku closure (non-author integrator, @m_opus)

# kama round 49: non-author closure spot-check

Date: 2026-10-26 (closed 2026-10-27 UTC). Base `438127bc01ff3b99f98468549d58046f932490ef` (round-48 spot-check), freeze `36d5ed2681111b68c180f8ab1646d8dc9beaedee`, build `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, wave spec `122c4ee95701587cef7f4342c3d175622ec2f4ad`, measured commit `24e906f034bc5635ee46d9743b1aa9ff93707362`, results `7fab24e74865cc18c53498e47670307569694d88`, late findings `19c07aa9b3c25e0def4c3b09f3dbb1765f3ae84d`, lane tip `5b395257874b45209696a5be5f675178c33aa7c5`. I re-measured both claims myself with the frozen counters on a fresh local clone of the lane, at the tip, at the measured commit and at the base. Every other gate result below is evidence-verified from committed receipts; I did not execute any other lane gate.

Driver digest (from `.ufo/watchdog.log`, which is mutable):
`2026-10-26T20:07:34-03:00 launch kama round=49 pgid=3711695 driver=hyaku-inline attempt=1`
`2026-10-26T21:01:09-03:00 complete kama round=49; hyaku-inline attempt=1`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my own re-measurement at the tip and at the measured commit; both fail at the base.
- No axis is harmed. In the SCORECARD diff no score changed and no capability was lost (11 → 11).
- The spot-check agrees with the Gate on both admits and on the three rejects I sampled.
- The round-48 closure defects R1–R3 are fixed this round; R4 (route map quote) is operator-side and still open. Remaining defects (section 6) are status-neutral.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an <%ae> \| %H %ci %s' -- .ufo/reports/round-49/kama.md` → one commit: `kama-shokunin <kama@shokunin.local> \| f8cdb853aaff29393faeb0b6d4c2a2296778b698 2026-10-26 21:00:10 -0300 round-49: kama report` | pass |
| Report filed once, after its cited tip | Tip `5b395257` committed 20:59:50 -03; the report landed 20 s later (21:00:10) in a single commit, with no placeholder and no in-place rewrite. It was filed before the driver `complete` line (21:01:09). Round-48 closure R2 is fixed | pass |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 lines, all `[~]`, each with a pointer; `grep -c '^- \[' SHONEN.md` → 4 | pass |
| Cited lane commits exist and are ancestors of the branch | `git cat-file -e <h>^{commit}` and `git merge-base --is-ancestor <h> master` hold for all 8 cited hashes (base, freeze, build, wave spec, measured, results, late findings, tip) and for the cited event `0718b6ab`. `git log 438127bc..master` lists exactly the 7 round-49 commits, all authored `kama-shokunin` | pass |
| Lane pushed and clean | `jj-lane.sh state` → `branch=master local=5b395257… remote=5b395257… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` printed nothing; `git ls-remote origin refs/heads/master` → `5b395257874b45209696a5be5f675178c33aa7c5` | pass |
| Prompt carries the template contract | `.ufo/prompts/kama-round-49.md` (committed `818f074c` by the lane identity, 20:07:32 -03, before the launch line). Lines 1–140 equal `templates/round-prompt.md` rendered with `{{LANE}}`→kama, `{{ROUND}}`→49, `{{FLEET_ROOT}}`→/home/vgpnk/Projects/shokunin, `{{AXES}}`→`operability + calibration (local model serving and endpoint health)` and `<kama-repo>`→`kama-shokunin`; a difflib comparison showed no other difference. Lines 141+ are hyaku addendum §6–§7. `diff kama-round-48.md kama-round-49.md` differs only in round numbers. The five child-lane items are present | pass |
| Quoted L2 route map vs the live map | Prompt line 176 still quotes the run-8 map with critic `@m_flash`. `~/.omp/agent/config.yml` (mtime 18:14 -03, before launch) has `critic: "@m_kfc"`. The lane counted its share from the live map this round | defect R6 (operator-side, status-neutral; carried from round-48 R4) |
| L2 floor and role split | One v2 wave `kama-r49-w1`, 71 seats. Role counts in `w1/dispatch.json`: executor 23, scribe 12, reviewer 11, critic 8, connector 5, scout 4, mutation-tester 4, sentinel 2, simplifier 1, revenger 1, equal to the report. Under the live map m_flash = 23+12+2+1+1 = 39/71 (55%); attack 11+8+4 = 23/71 (32%). `seat-yield-w1.out`: `seats=71 status=unknown:71 reports=71 missing=0`, exit 0 | pass |
| Counters frozen before data | `sha256sum` at the tip: `tools/round49-replay-witness-audit.py` = `86b4a40d…d6c1`, `tools/round49-append-audit-v4-check.py` = `26c465a9…6945`, equal to `preregistration.json` `claims[*].counter_sha256`; `git diff --stat 36d5ed26 5b395257` over both counters is empty. `freeze/prereg-time-check.out` → `RESULT pass`, exit 0. Controls committed `met=False` (base C1/C2, `junk-c1-fake-witness`, `junk-c2-no-exempt`, `junk-c2-word-token`) | pass |
| No uncommitted round work | The lane is clean. The fleet root has one untracked file, `.ufo/reports/round-44/kengaku.md`, which belongs to another lane and is not kama's | pass (operator note) |

This is not a marker report: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2): my re-measurement

Fresh clone `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r49-closure/lane` (HEAD `5b395257`). I copied the frozen counters out of the clone and ran `python3 <counter> --repo lane --tip <commit> --scratch <dir> --out <file>`. No process from these runs was left behind (`pgrep -af kama-r49-closure` empty afterwards).

### C1: operability 8→8 (replay execution witness and bounded archive verification, sourced on S494/S495)

- Base `438127bc`: `witness=0 cap=0 newrow=0 witnessed=0/3 met=False`, exit 1. Details: each replay exits 2 with `no ready.json` (the base tool has no witness mode); `cap sparse-1e15: exit None … seconds=30.0 FAIL` (the round-48 R1 unbounded read); `newrow: 0 rows new since base`. This equals the committed `controls/base.c1.out`.
- Measured `24e906f0`: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0. Equals `measured/c1.out`.
- Tip `5b395257`: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0 (12 s). Details: three held b11909 servers (pids 151713, 169148, 188354) observed `exe+listen+model ok`, a fresh nonce round-tripped on each against the counter's own 512-token vocabulary decode; `cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' … seconds=0.1 ok`; `newrow: … ['| S494 |']`.
- Spot read of `tools/kama-llamacpp-live.py` at the tip: `prepare_witness_dir()`, `hold_for_witness()` (per-pid temp opened `O_EXCL|O_NOFOLLOW`, hold ends on release, child exit, timeout or parent change; `ready.json` removed when the hold ends), `PR_SET_PDEATHSIG` on the server child, `--witness-timeout` bounded `0 < t <= 3600`. The mechanism is real, not a counter-shaped stub.
- Disclosed and not closed (section 6, R1/R2): the counter does not join the observed pid with the rerun receipt's `child_pid`, so a decoy replay or an inherited-environment hijack meets it (K1Cheat); the loaded model bytes are not bound (K1Design); a host copy of the binary passes (stated limit).

### C2: calibration 7→7 (append-only-audit v4: origin, whole-word binding, negation, no wildcard self-declaration)

- Base `438127bc`: `fixture=0 lane=0 scenarios=4/8 met=False`, exit 1 (`launder`, `substring`, `negated`, `wildcard-self` FAIL; lane event `0718b6abbda6 … ungraded 72 > natively exempt 65`). Equals `controls/base.c2.out` line for line.
- Measured `24e906f0`: `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0; the detail lines equal `measured/c2.out` apart from the command header.
- Tip `5b395257`: `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0 (4 s); lane `ungraded_lines 82` (v3: 89), event `0718b6abbda6 … ungraded 65 <= natively exempt 65`.
- The round-48 C1 counter now reports `lane=0` (`measured/r48c1.out`: `ungraded tool=65 counter=72`, `held_at_to tool=2356 counter=2349`, summary `tool=82 counter=89`). The whole difference is the seven origin-dated lines v4 now grades, and they are held. This is the intended supersession of the v3 definition, not a regression.

### Evidence-verified (committed receipts at `24e906f0`, not executed by me)

- gate `registered 44 unregistered 0 defective 0` (exit 0; at the build it was `42/2` with the two new counters unregistered)
- capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True`
- r41 `mismatches=0 met=True`; r42 `mismatches=0 maxN=49 met=True`; r43 `registered=44 mismatches=0 met=True`; pointer `met=True`
- hexrun `unknown=0` (exit 0; exit 1 with `unknown=2` at the build, fixed at integration); digest-ledger `unknown=0`
- `AOA_SELFTEST pass=36 fail=0`; `KLR_SELFTEST pass=23 fail=0`; check-receipt `16 VALID and 1 NOT-EVALUATED … 107 mutations + unreadable case rejected`; live selftest exit 0
- `sources-append-only.py --from 438127bc --to 24e906f0` exit 0; `append-only-audit --to 24e906f0` exit 0; round-48 C2 counter `replayed=3/3 met=True`
- `git log 24e906f0..5b395257` holds only results, wave results, seat reports and receipts, so these receipts describe the tip's graded surfaces.

Verdicts: C1 verified (re-measured); C2 verified (re-measured). Neither claim is exploratory.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| operability | improved | C1 re-measured. A replay now holds its rerun server up for an outside observer, which I saw find the frozen b11909 binary listening with the frozen model and answering a fresh nonce, 3/3. The sparse-archive DoS of round-48 R1 is refused in 0.1 s instead of hanging. Score held at 8 |
| calibration | improved | C2 re-measured. The append-only audit stops ungrading text laundered under an exempt heading and refuses substring, negated and wildcard self-declarations; 8/8 constructed fixtures pass, and the lane's seven origin-dated lines are now graded (and held). Score held at 7 |
| freshness | unchanged | Score 8; row unchanged in the SCORECARD diff; r41–r43 regressions met at `24e906f0` |
| depth | unchanged | Score 7; SKILL.md +20/−0 (round-49 registry and witnessed-replay how-to); evidence re-anchor only |
| coverage | unchanged | Score 9; PROVINCE.md not in the diff |
| adjacency | unchanged | Score 7; sibling scan N1Overlap reported, not absorbed |

`git diff 438127bc 5b395257 -- SCORECARD.md`: +71/−8, no score changed (the `## Axes` table rows are identical apart from evidence re-anchors). The removed lines are the round-48 head banner, which is kept verbatim below the head (`grep -cF` of the base banner line at the tip → 1; banner lines 7 → 8), plus head re-anchors and two capability rows reworded, not removed (11 → 11). Numstat for the append-only files: LOG.md 9/0, SKILL.md 20/0, corpus/QUALITY.md 15/0, corpus/README.md 166/0, corpus/SOURCES.md 2/0, `corpus/knowledge/llamacpp-loading-lifecycle.md` 4/0.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S494 (llama.cpp server README at `caa8191d`) | admit | `curl -sSL https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md` → 2523 lines, byte-identical to the committed copy `c1/server-README-caa8191d.md` (`cmp`). Line 700, under `### POST /tokenize` → `**Response:**`, holds the exact quote (20 words). GitHub API `git/ref/tags/b11909` → object `caa8191df159f764fb0160e3d2fc6be008948aee` | agree | Verbatim, ≤25 words, at the cited section and line. The pin is the release commit the receipts record. Scope is limited to the `/tokenize`/`/detokenize` shapes |
| S495 (proc_pid_exe(5)) | admit | `curl -sSL https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html`, tags stripped: the DESCRIPTION paragraph holds "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (15 words); colophon `Linux man-pages 6.19 2026-02-08` | agree | Verbatim, ≤25 words, under §DESCRIPTION ¶1, page version as cited. It grounds hashing `/proc/<pid>/exe`, Linux-only as the row states |
| `/proc/<pid>/cmdline` (`-m <model>` in argv) as proof of binary or model | reject | Committed control `controls/junk-c1-fake-witness.c1.out`: a python stub with `-m <model>` in argv fails only on `exe sha256 375532f8… is not the frozen server` for w1–w3; no model-check problem is reported | agree | argv is self-asserted by whoever starts the process, so the model check passes on a stub. Only the exe digest identifies the running binary |
| `piece` comparison that is only self-consistent between `/tokenize` and `/detokenize` | reject | `w1/out/S1Gate/gate_rejects.out` probe C: a stub with an invented vocabulary detokenizes the nonce exactly (`equals_nonce=1`) while `pieces disagreeing with the model vocabulary=10/10` (`{"id": 0, "piece": "kam"}` vs `vocab[0]='<unk>'`). My own counter runs print `counter vocabulary: 512 tokens from its own download` | agree | A server can be consistent with itself and still be fake. Only a vocabulary the observer decodes from the hashed model can reject it |
| Round-48 C1 counter as the v4 grade | reject | `measured/r48c1.out` at `24e906f0`: `lane=0`, `ungraded tool=65 counter=72`, `held_at_to tool=2356 counter=2349`; my C2 runs show the same 7-line difference (89 → 82) | agree | The old counter recomputes v3 and keeps the seven origin-dated lines ungraded. Using it would grade v4 as a failure for exactly the change C2 claims |

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0; codes `1 ok`, `1 W01` (S481), `93 W04`, 0 `E`. This equals the lane's `census/end.out` code counts, and the report quotes them whole (round-48 R3 fixed).
- SOURCES rows 234 → 236 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` at each revision). Only S494 and S495 were added; `git diff` has no `-` row lines.

Discernment: the spot-check agrees with the Gate on all sampled admits (2) and rejects (3).

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | No new `knowledge/` entry; `llamacpp-loading-lifecycle.md` gained an appended paragraph (S494/S495). Capabilities 11 → 11 (two rows reworded). Agrees with the lane |
| quality | improved | Replay execution is observable from outside, which I re-verified 3/3. The record-time DoS (round-48 R1) is closed. v4 grades seven held lines v3 ungraded. Host-safety fixes landed before measurement (O_EXCL/O_NOFOLLOW temp, parent-death hold end). No admitted entry failed its re-check: S494 and S495 re-opened clean. Agrees with the lane |
| discernment | improved | This outside spot-check agrees with the Gate on the sampled admits and rejects. That meets the condition the lane left open under KQ61 (it self-graded `unchanged` pending it) |

## 6. Routed defects (the lane fixes these next round unless marked otherwise)

- **R1 (lane, operability, C1 counter gap; seats K1Cheat, K1Design, R0Controls).** The counter never joins the observed pid with the rerun receipt's `child_pid`, so a decoy replay that starts the host's b11909 binary and copies the original receipt, or a `PYTHONPATH`/`sitecustomize` hijack of the counter's inherited environment, meets `met=True`. `released`/`waited_ms` are self-asserted, and the loaded model bytes are not bound. Join pid ↔ `child_pid`, scrub the counter's environment, and bind the model the server actually mapped.
- **R2 (lane, operability, host safety; late seat X1Kill).** A killed counter still leaves replay, live tool and server up (the replay spawns its child without its own session). The parent-death hold end covers SIGKILL of the replay, not of the counter. Close this teardown path with a case that can fail.
- **R3 (lane, calibration, C2 definition gaps; seats K2Origin, X2Fixtures, K2Cheat, V2Ctr).** Origin is `git rev-list`-order dependent, fence-blind (a fenced fake `## ` title) and CRLF-sensitive. The counter's lane leg only upper-bounds the tool's self-reported `ungraded` (a tool with `graded + ungraded != deleted` plus a fixture-shape heuristic meets it). The counter's binder copies the tool's rule, so it is not an independent check.
- **R4 (lane, mutation coverage; late seats M1Ctr, M1Live, M2Ctr, M2Tool).** Surviving mutants: C1 counter 11/20, live/replay 10/23, C2 counter 16/49 (5 equivalent), v4 tool 8/29. The lane already routed these to round 50.
- **R5 (lane, carried).** Still open from round 48 R5: sub-20-line deletions unwatched (L1Lowthr), prerelease cliff (r47-D7), b11906 population at b11909+.
- **R6 (orchestrator/operator, prompt route map; carried from round-48 R4).** Prompt §6 line 176 still quotes critic `@m_flash`; the live `agentModelOverrides` routes critic `@m_kfc`. The lane worked around it correctly (39/71 from the live map). The addendum is operator-side and needs the current map.
- **Operator/L0.** Planner seat still impossible under the policy-v2 validator, which also rejects `labrat` (`kama | round-39`). Also open: MISSION axes pair (`kama | round-35`) and parked worktree (`kama | round-41..43`). The fleet-root untracked `.ufo/reports/round-44/kengaku.md` is another lane's and was left untouched.
- **Operator, promotion.** The four `SHONEN` boxes are `[~]` and look checkable by a non-author:
  - box 1: gate registry `registered 44 … defective 0`, SKILL §Round-49 registry;
  - box 2: three witnessed b11909 replays, which I observed 3/3 above;
  - box 3: SKILL witnessed-replay how-to, run from SKILL and `--help` by seat K1Fresh;
  - box 4: PROVINCE.md unchanged this round.

  Promotion is operator-owned; nothing was marked here.
