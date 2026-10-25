author: hyaku closure (non-author integrator, @m_opus)

# Round 18 — verifier spot-check (non-author closure, recovery attempt 2)

Closed 2026-10-21 by the hyaku closure seat `CloseKama18` (did not author round 18).
Lane range `e75cf680b53484a61709ee1b2787d8dbc6419f74` → `1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e`
(measured tree `eb78788b35b832d08887d4c366d1d0c1df3a6c19`). Report: fleet
`.ufo/reports/round-18/kama.md` (commit `23bdc3f8c92d4be74abead0de4015acf9a749e39`).
Five read-only reviewer seats (`CloseKama18.{ReuseHonesty,PrivacyFix,Accounting,ServiceDownload,ClaimEvidence}`)
re-checked committed bytes; no lane gate, selftest, counter or harness was executed.

Driver digest (copied from mutable `.ufo/watchdog.log`):

```
2026-10-20T16:42:33-03:00 launch kama round=18 pgid=3591651 driver=hyaku-inline attempt=1
2026-10-21T00:47:36-03:00 lane-dead-no-report kama round=18; retry same round (hyaku-inline attempt=1: attempt-1 coordinator KamaR18 ended on provider weekly quota before report; operator-authorized recovery coordinator 2026-10-21 reuses checkpoint 101f3991d3570bc9350fbf9c5561f4be1185699d)
2026-10-21T00:47:37-03:00 launch kama round=18 pgid=2988422 driver=hyaku-inline attempt=2
2026-10-21T02:39:37-03:00 complete kama round=18; hyaku-inline attempt=2
```

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report landed by lane identity, after lane work | `git log --format='%an %H' -- .ufo/reports/round-18/kama.md` | `kama-shokunin 23bdc3f8…` at 02:39:12 -03, after lane tip 1b85a24 (02:05:22) | pass |
| Cited commits exist, ancestors of branch | `git merge-base --is-ancestor <h> refs/heads/master` for 0c75c61, 888cd38, eb78788, 1b85a24, c6dc46f, 1c325b2, 101f3991 | all `commit`, all ancestors | pass |
| Lane clean and pushed | `scripts/hyaku/jj-lane.sh state …`; `git status --porcelain` | `ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty; `ls-remote` master = 1b85a24 | pass |
| SHONEN heading | report §SHONEN vs `grep -cE '^\s*- \[[ x~]\]' SHONEN.md` | 4 lines for 4 boxes, all `[~]` | pass |
| Prompt carries template contract | `diff` of `templates/round-prompt.md` vs `.ufo/prompts/kama-round-18.md` lines 1–140 | only placeholder substitutions differ; hyaku addendum §6 follows; prompt committed by lane (d7beee2, attempt 2; f4c9ae5, attempt 1) | pass |
| Report minimum content, Sources & frontier, trends | report read in full | all present | pass |

Note: `c6dc46f` carries author date 16:41:43 (50 s before the launch line) because jj stamps the
working-copy change at creation after `e75cf68`; its committer date is 19:33:49 — not a defect.

## Claims — re-check

Both claims rest on lane-owned counters and a harness; per §Gate standard (Closure consequence)
they are **evidence-verified** from committed output, with digests tied to the official run; the
numbers below were re-derived by me with `jq` over committed bytes at the tip.

| Claim | Command (mine) | Observed | Reported | Verdict |
|---|---|---|---|---|
| Harness | `jq '{m:.measured_commit,n:(.commands\|length),bad:[.commands[]\|select(.as_expected!=true)\|.name]}' runs/commands.json` | `eb78788b…`, 32, `[]` | 32 commands, all expected exits, measured eb78788b | match |
| C1 operability 8→8 | `jq '{counts,current_clean,faults,exit}' runs/c1-measure.json`; `cat runs/c1-measure.exit` | accepted_bad 5→0, good_rejected 1→0, misclassified 1→0, uncontrolled 0→0, gate_flip_arms 16→17, clean true, faults `[]`, exit 0 | same | verified |
| C2 calibration 7→7 | `jq` group_by over `.results[].items[].before/.after` in `runs/c2-survivors.stdout`; witnesses | before survived 11/miscount 1/accepted 3 → after killed 11/correct 1/handled 3; witnesses 15, mismatches `[]`; exit 0 | same | verified |
| Output binding | `sha256sum runs/c1-measure.stdout runs/c2-survivors.stdout` vs `commands.json` | `83e8a1ed…`, `ea2e3e02…` equal the recorded `stdout_sha256` | — | bound |

Seat `ClaimEvidence` also confirmed: the C1 "before" arm runs the frozen tool/gate whose 10
`frozen/SHA256SUMS` digests equal both the committed snapshot and the `e75cf680` blobs; measured
inputs are byte-identical at eb78788 and 1b85a24 (`git diff --name-only eb78788 1b85a24` touches
only LOG, SCORECARD, lesson and round-18 evidence); the disclosed 2-of-11 C2 kills flipped only
by the arm-combination repair (`runs/pre-repair/c2-survivors.json`: FC-target, FC-f6cache
`inconclusive`, exit 2).

No-harm: `git diff e75cf680 1b85a24 -- SCORECARD.md` is 72 appended lines, no row rewritten;
other axes stated unchanged (freshness 8, coverage 9, depth 7, adjacency 7). Five legacy replays
and the wrong-probe-pin negative control met their expected exits in `commands.json`.

## Recovery-specific checks

- **Attempt-1 reuse/discard honesty — confirmed.** `git diff 101f3991 1b85a24 -- .ufo/waves/round-18/live`
  is empty (receipts restored to checkpoint bytes); recovery receipts live only under
  `live-recovery/` (absent at 101f3991). 20 never-assigned build members = `dispatch-95.json`
  (95) minus `build/spec.json` (75), none with outputs. 10 dead falsify seats = spec (76) minus
  66 advice reports, none cited. Checkpoint 101f3991 is lane-identity, parent 1c325b2, message
  "unadmitted"; LOG/lesson disclose it.
- **Env-value-leak refute (`PrivacyScope`) — fixed, fail-capable.** `check-receipt.py:473-479`
  emits constant text, guards non-strings; selftest cases `env-key-value-echo`,
  `env-key-raw-value-echo`, `env-key-nonstring` with a sentinel asserted absent from
  stdout/stderr (`:2115-2118`); committed `runs/gate-selftest.stdout` 5 VALID + 1 NOT-EVALUATED +
  72 mutations rejected, exit 0, digest matches `commands.json`. No secret-shaped value in
  committed `live/`, `live-recovery/`, `runs/` (all `child_env_keys` = HOME, LANG, PATH).
  Residual: frozen pre-round gate snapshot still interpolates `{k!r}`, fed only trusted legacy
  receipts.
- **Recovery accounting — confirmed.** build 75/75 (role histogram exact), one 95-seat call wholly
  refused (`refused-result-1.json`), falsify 76 spawned / 66 reports / 10 dead; count command →
  28 confirm / 34 partial / 1 refute / 3 nonconformant; residual 7 (4 confirm, 3 partial); total
  158 ≤ 200; `resume:0` in both validations.
- **No long-running service or large download — confirmed.** Recovery live runs were 6 commands at
  05:10Z (02:10 -03), each under 0.2 s; llama-server spawned with `start_new_session` +
  `PR_SET_PDEATHSIG`, killpg teardown; receipts `sigkill_sent false`, `returncode 0`,
  `port_refuses true`. Model (1,185,376 B) and server stub predate the window; `find /home/vgpnk
  /tmp /var/tmp -xdev -newermt '2026-10-21 00:47' -size +100M` → 0 hits; no llama process,
  user unit or listener on ports 40999/36277/43877 remains.

## Per-axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| operability | improved | C1 counters re-derived (5→0, 1→0, 1→0, arms 16→17); score held at 8 by the lane's own cap |
| calibration | improved | C2 15 named items 11 survived/1 miscount/3 accepted → 11 killed/1 correct/3 handled, witnesses 15/15 |
| freshness | unchanged | not claimed; score 8 |
| coverage | unchanged | not claimed; score 9 (new knowledge entry counted under expansion trend) |
| depth | unchanged | not claimed; score 7 |
| adjacency | unchanged | not claimed; score 7 |

## Discernment spot-check

Sources re-opened 2026-10-21 by this closure seat.

| Item | Gate decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| IPv6 loopback is exact `::1` (S050) | admit | `curl https://www.rfc-editor.org/rfc/rfc4291.txt`, line 474; sha256 `4d58dff6…` equals S050 anchor | agree | quote verbatim at cited line; digest pinned correctly |
| tcp6 address fields are four native words (S048) | admit | `raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv6/tcp_ipv6.c` lines 2173/2176 | agree | format `%08X%08X%08X%08X` over `src->s6_addr32[0..3]` at the cited lines |
| repeated scalar/append options (S056 supersedes S054) | admit | llama.cpp `common/arg.cpp` @704366d7, sha256 `bf4c58c1…` equals anchor; lines 833, 836, 3354, 3538, 4321 | agree | port assigns, api-key pushes, spec-type inserts and is warning-exempt, exactly as cited |
| Exception-only guards contain SystemExit/KeyboardInterrupt | reject | `https://docs.python.org/3.14/library/exceptions.html` → serves `/3.14/builtins/exceptions.html`, "Python 3.14.8 documentation", §SystemExit | agree | "inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception" — the guard cannot contain it |
| llama.cpp rejects duplicate flags itself | reject | same `arg.cpp`:832–837 | agree | duplicate only logs a deprecation warning, "only last value will be used" |
| proc_net_tcp.rst defines IPv6 byte order | reject | `raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst`:7–8, 18 | agree | doc names both files, but its only address example (line 18, `010310AC:9C4C`) is 8-hex IPv4; deprecation note at line 8 as quoted |

New SOURCES row re-opened: **S050** — lesson Gate quote "The unicast address 0:0:0:0:0:0:0:1 is
called the loopback address." (9 words ≤ 25) at `rfc4291.txt:474`; second quote at 551–552
verified. **S056** quote `params.api_keys.push_back(key);` at `arg.cpp:3538` verified.

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0,
`ok`, three W04 duplicate-URL warnings (S031, S043, S056); `census` → rows 56 (A 53, C 3; mined 45,
queued 5, rejected 6), exit 0. `git show e75cf680:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 47.
Only S047's `used-by` changed among pre-round rows (old→new logged in SOURCES search log).

## Trend verdicts

- **expansion — improved.** New `corpus/knowledge/loopback-listener-ownership.md` opens with
  `source:` citing mined S048–S050 and has a new coverage-map row (`corpus/README.md:261`); census
  47 → 56.
- **quality — improved.** S056 supersedes S054's over-general reading; the falsify refute and H1
  closed with fail-capable cases; every sampled admission re-verified against its pinned bytes.
- **discernment — improved.** This outside spot-check agrees with the gate on 3 admits and 3 rejects.

## Routed defects (lane fixes next round)

1. **Residual verdict miscount.** `corpus/lessons/round-18.md:316-318` and `LOG.md:1122` say
   "five confirm, two partial" plus `ResidClaims` partial (8 for 7 seats); committed verdicts are
   4 confirm / 3 partial (`git grep -n '^VERDICT' -- .ufo/waves/round-18/residual/advice/`).
   Append corrections.
2. **S055 / Gate-row pointer drift.** S055 anchor ("commands/exits in round-18/runs/commands.json at
   measured c6dc46f") and `lessons/round-18.md:53` (`runs/live-gate-1.stdout: VALID`) now resolve at
   the tip to the recovery pass (measured eb78788, `live-recovery/receipt-1.json`); the described
   bytes exist only at `1c325b2`/`101f3991` (`runs/commands.json` is absent at c6dc46f).
   Lesson:385's "resolves to the bytes it describes" holds for `live/` receipts only. Add a
   revision-qualified correction (append-only).
3. **SCORECARD.md:755** gives the C2 counting command as `survivors.py --json --out PATH`; the
   official argv is `--json` alone (stdout document). Also `runs/c2-survivors.json` (04:08Z) is a
   pre-official run beside the official stdout (05:11Z); the two agree. Disambiguate.
4. **Residual role split** "6 reviewer, 1 critic" (report §Extras) has no committed dispatch record.
5. Carried named residuals (lane-declared): 1 of 51 install-tree members pinned; C2 selftest-kill
   arm lacks full enumeration; detector-self mutant (b) outside C2's 15; `GateCaptureHashes` M1–M4
   and the fresh-mutant survivors listed in SCORECARD §Planned.

## SHONEN note for the operator

All four boxes are `[~]`. Box 2 (end-to-end task executed and logged) looks checkable by a
non-author from committed evidence (LOG round-18 entries; five-pin `VALID` gates over
`live-recovery/receipt-{1,2,3}.json`). Boxes 1, 3, 4 were not independently assessed here.
Promotion is operator-owned.
