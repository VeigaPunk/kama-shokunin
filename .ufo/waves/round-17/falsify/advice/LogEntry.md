VERDICT: partial — round-17 counts, landed paths and retained measurement totals match; the measured-revision pointer is missing and two evidence-wording defects remain.

# Scope and axes

Attacked `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:992-1025` at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, not the moving lane worktree. Axes: **calibration** (truthful counts and bounded claims), **operability** (claimed landed surfaces versus actual diff), and **evidence provenance** (revision and artifact consistency). This is advisory review, not claim admission, integration or a runtime verdict.

All lane citations below refer to that pinned commit unless another revision is explicitly named. Inspection and the sole executed lane counting command used an isolated checkout at `/tmp/KamaR17.LogEntry-clone`, now removed. Only this Report was written in the lane.

# Findings, by severity

## P2 — The promised measured/landed revision does not resolve through LOG

- `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:674-676` says the build commit's hash is in the round-17 LOG section: “hash in `LOG.md` §round 17”.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:992-1025` contains only the **start** revision, at line 994, and no delivered/measured revision. Its measurement paragraph links back to the scorecard at lines 1024-1025.
- The commit actually reviewed is `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; its direct parent is the recorded start, `cff9e62f05aa7cfb9059444f62eb787100719713` (observed `git rev-list --parents -n 1` output).

This is a broken provenance pointer, not evidence that the measured totals are false. The current check.py, live tool and receipt gate hashes match their retained measurement inputs, which limits the impact. Append a round-17 closure/correction naming the landed hash and binding the measurements to it; do not rewrite the existing LOG entry.

## P3 — The motivation overstates the old port-closure check as unfalsifiable

- `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:999-1001` groups `teardown_port_closed` under “cannot fail on the behaviour they name”.
- The cited source distinguishes this from the genuinely near-tautological exit check: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:53` says “only via a surviving listener”; lines 61-62 explicitly retain that failure case.
- The actual pre-round predicate is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:1029-1032`: it compares `port_refuses` to `True`. Lines 684-687 set that field to `False` on a successful post-teardown connection.

The supported defect is **vacuity on failed/unowned runs**, not impossibility of rejecting an open port. Append that narrower motivation. This does not refute the new ownership gate or its measured improvement.

## P3 — The completion summary gives a conflicting refusal timestamp

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/completion-summary.json:30` places the one refusal “at 14:59Z”.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/attempts.json:3-8` records it at `2026-10-20T15:03:50.107692+00:00`, and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/refused-result-1.json:2` agrees.

Correct the supporting summary's timestamp through a documented correction. The LOG itself gives no refusal time, and the **one refused call / 82 refused / zero spawned** claim is supported; this is not a seat-count discrepancy.

# Bullet-by-bullet result

## Start and VCS — LOG lines 994-995

The start revision is the actual commit parent. The frozen manifest independently names it at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/manifest.json:3-4`. The `AGENTS.md` helper-only VCS instruction is present in the actual diff. Historical clean-tree/nothing-inherited status is author-recorded at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:3-6`; it is not independently reconstructible from the final tree. I did not inspect runtime state or session stores to manufacture that corroboration.

## Motivation — LOG lines 996-1003

- Five surviving grading mutants are explicitly recorded at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/MutateHarness.md:20-28`.
- The pre-round grader copies served identity but omits identity and route from its pass predicate, and calls `row.get` without checking the row's object type: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py:329-346`.
- The old live report records degraded health passing, bad loading bodies passing, SIGKILL passing the exit check and a lost receipt on teardown fault: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:24-34`. Finding P3 above preserves its port-check caveat.
- `git diff b8e485c ccc4bb3 -- corpus/SOURCES.md` shows S041's existing row changed in place: both the anchor and teaches cells changed. This supports the mined-mistake statement.

## Wave counts and policy — LOG lines 1004-1010

The four requested artifacts agree on the LOG's numerical claims:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/validation.json:20-45`: 82 spawn, zero resume; roles executor 15, scout 19, reviewer 14, critic 6, sentinel 2, connector 8, revenger 4, scribe 10, simplifier 2, mutation-tester 2; v2 band 64-100. The actual `dispatch.json` task roster independently has that same role histogram. Its SHA-256 matches validation's recorded stdout digest.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/attempts.json:3-34`: one refusal with 82 refused/zero spawned, four capacity observations at roughly 180-second intervals (92, 56, 26, 15 running), then one successful 82-seat call. Capacity observations are not extra dispatched waves.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/completion-summary.json:16-27`: 82 completed/zero failed and 82 advice reports, with 34 confirm/32 partial/1 refute/15 n/a/zero nonconformant.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/verdict-counts.json:3-15`: that same verdict histogram, 82 expected/82 files, no missing/unexpected/unreadable reports. The clone-only counter reproduced it exactly. A separate literal search found no advice report with a leading blank line, so the counter's first-nonempty-line behavior does not change this wave's first-line result.

`RevengerPlannerWalk` is a revenger in the dispatch roster; no L2 planner is added to the totals. The statement that L1 holds the planner seat is a role declaration, not an extra completed seat. No saturation/convergence claim is made: 82 is inside the declared band, not a claim that all 100 slots were occupied. Zero resumes means no `resume_continuity_v1` preflight path is claimed by this LOG entry.

## Landed paths and behavior — LOG lines 1011-1019

`git show --stat 54a29268e2083caa2b1e0d54ee1e7d90961302f3` contains **every named landed path** (187 changed files overall). No listed artifact is absent from the commit.

- The new grader implements strict stdout decoding and per-row malformed handling, identity comparison and the GET route conjunct: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:279-287,364-405,460-481`.
- Receipt v2 and the new teardown/loading predicates are in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:50,1310-1356`; the receipt gate selects both schema versions at `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:204-208`.
- The round-13 divergence-only branch selects the exit-4 finding, rather than suppressing other content failures: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/measure.py:125-126,463-485`.
- Source rows S042-S046 exist at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:54-58`; KQ20-KQ22 exist at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:121-123`.
- The actual documentation diff appends the OPTIONS corrections to `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md` and exactly the three named knowledge surfaces (endpoint identity, runtime-health matrix and loading lifecycle). It also adds both claimed ignore entries and the VCS rule. “README” resolves to the corpus README, as the lesson clarifies at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:108-113`.

## Measurements and no-harm — LOG lines 1020-1025

Retained artifacts match the claimed numbers; these are artifact inspections, not newly executed live measurements:

- Fixed detector: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/fault-controls-frozen.json:155-156` is detected 5/accepted 3; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/fault-controls-current.json:155-156` is detected 8/accepted 0. The current input hash matches the committed grader (`ddc3f3cc…`).
- Grid: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/mutants-grid.json:1636-1643,3424-3431,5060-5067,6889-6896` records frozen/pair 1/8, frozen/full 7/8, current/pair 1/10 and current/full 10/10. Frozen has two `site_missing` cases; the denominator change is explicit, not two extra kills against the same eight sites.
- C2: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json:2,176-181` records accepted_bad 6/inconclusive 1; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-current.json:2,243-248` records 0/0. Current tool and gate hashes match committed files (`0efd1723…`, `ad680179…`).
- All three committed v2 receipts have 11 checks, all true, build `b11755-704366d76`, and matching model/server/probe/tool hashes. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/gate.txt:1-7` retains three VALID/exit-0 results. Their full paths are `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-2.json` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-3.json`.
- A direct start-to-round-commit diff has no changes to the probe or nine matrix JSON files. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/noharm-README.txt:1` records the clone overlay and grader digest; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/noharm-r16-measure-clone.txt:33-37` records PASS/exit 0; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/noharm-test-snapshot.txt:31-32` records 30/0; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/v1-receipts-current-gate.txt:1-4` records both v1 receipts VALID.

# Residual risk and verification gaps

- The 82 terminal completions are L1-attested in the summary's line 31. The retained spawn result is an async/pending roster, not an independent terminal-event ledger. Eighty-two extant advice files corroborate delivered reports, not every transport lifecycle event.
- The provenance ledger still has null task-call bindings at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/provenance-ledger.json:60-61`, and records refused 0 at line 24 despite the raw refusal. The lesson already discloses the refused-count defect at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:88`. I used the raw attempt/result artifacts for the LOG count, not that faulty aggregate. Same-identity rerouting and canonical-runtime admission are not established by this scoped review; no such runtime was invoked.
- The live gate text records outputs and probe/tool hashes, but not the full four-pin command argv. The receipts contain all four digests and the lesson records the four-pin invocation; I did not independently rerun those gate calls or infer flag use merely from VALID output.
- `xd://lsp` is **not mounted**: device lookup returned “No such tool”. LSP status/references/definition/diagnostics were therefore unavailable. Targeted source/diff and literal-text inspection are fallbacks, not semantic reference proof. No cold empty LSP result was treated as absence.
- No live endpoint, fake server, llama-server, measurement suite, selftest, build, linter or formatter was run by this seat. No ports were bound/contacted; no host services or routing changed. This is not a full C1/C2 behavioral audit or an outside shokunin admission.

# Exact commands executed and exits

All commands below exited **0**. Git pathspec arguments are shown exactly as executed. Read/grep device operations had no process exit code; the unavailable LSP lookup is described above.

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.LogEntry-clone && git -C /tmp/KamaR17.LogEntry-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3

git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --stat --format=fuller 54a29268e2083caa2b1e0d54ee1e7d90961302f3

git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --format= --no-ext-diff --unified=5 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- LOG.md

PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/count-verdicts.py /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/build/advice --expect-names /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/build/spec.json --json

git -C /tmp/KamaR17.LogEntry-clone rev-list --parents -n 1 54a29268e2083caa2b1e0d54ee1e7d90961302f3

git -C /tmp/KamaR17.LogEntry-clone diff --raw --no-ext-diff cff9e62f05aa7cfb9059444f62eb787100719713 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-probe.sh tests/probe-verdicts/*.json

sha256sum /tmp/KamaR17.LogEntry-clone/tests/probe-verdicts/check.py /tmp/KamaR17.LogEntry-clone/tools/kama-llamacpp-live.py /tmp/KamaR17.LogEntry-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.LogEntry-clone/tools/kama-probe.sh /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/count-verdicts.py /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/dispatch-provenance.py

git -C /tmp/KamaR17.LogEntry-clone show --format= --no-ext-diff --unified=2 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- .gitignore AGENTS.md corpus/SOURCES.md corpus/QUALITY.md corpus/README.md SKILL.md corpus/knowledge/endpoint-identity.md corpus/knowledge/runtime-health-surface-matrix.md corpus/knowledge/llamacpp-loading-lifecycle.md

git -C /tmp/KamaR17.LogEntry-clone diff --no-ext-diff --unified=0 b8e485c ccc4bb3 -- corpus/SOURCES.md

sha256sum /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/build/dispatch.json /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/build/refused-result-1.json /tmp/KamaR17.LogEntry-clone/.ufo/waves/round-17/build/spawn-result.json

rm -rf /tmp/KamaR17.LogEntry-clone && test ! -e /tmp/KamaR17.LogEntry-clone
```

# Installs and cleanup

Installs/updates: **none**. Pacman was not invoked. The isolated clone was removed and its absence checked by the final command. No scratch, server or background job created by this seat remains.
