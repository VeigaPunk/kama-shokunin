# EX03BoundRows - 12 bound run templates executed one by one at tip 03a6a1d

Item: execute each row of registry/capability-claims-r63.tsv (read via `git show <tip>:...`, split on tab, no csv parser)
in a scratch export of the tip. Seat is advisory; no verdict on the claims.

## Setup (exact)
- Tip export: `git -C <lane> archive 03a6a1d850902a66a13dfad33f89cf3a8b759a09 | tar -x -C $S/tip` (S=/fast/scratch/hyaku/kama-r63/w/EX03BoundRows).
- Placeholders: %T=$S/tip, %S=$S/s, %R=/home/vgpnk/Projects/shokunin/kama-shokunin, TIPREV=03a6a1d850902a66a13dfad33f89cf3a8b759a09.
- Executed `bash -c <run>`, cwd=$S/tip (same as the C2 counter's run helper), sequential, timeout 900.
- Environment passed: exactly PATH, HOME, LANG, TMPDIR ($S/tmp) - nothing else (no LC_ALL, no GIT_*).
- Driver and per-row stdout+stderr: out/EX03BoundRows/ (drive.py, res.json, <cap>.txt, cc.json, claims-at-tip.tsv).
- Tools installed/updated: none.

## Per-row results
| # | cap | exit | pattern appears | wall s | recorded verdict |
|---|-----|------|-----------------|--------|------------------|
| 1 | sources-registry | 0 | yes | 0.06 | true |
| 2 | ollama-offline-evidence-replay | 0 | yes | 2.07 | true |
| 3 | live-llamacpp-lifecycle | 0 | yes (`"outcome": "pass"`) | 0.34 | true |
| 4 | gguf-declared-identity-replay | 0 | yes | 0.05 | true |
| 5 | context-capacity-receipt | 2 | yes (and alt `host-not-idle-before-K1` also present) | 20.18 | host-busy |
| 6 | instrument-agreement | 0 | yes (`IA_SELFTEST pass=4 fail=0`) | 0.14 | true |
| 7 | pin-watch | 0 | yes | 0.04 | true |
| 8 | digest-ledger | 0 | yes (`unknown=0`) | 1.04 | true |
| 9 | hexrun-census | 0 | yes (`unknown=0`) | 0.80 | true |
| 10 | append-only-audit | 0 | yes | 1.67 | true |
| 11 | live-receipt-replay | 0 | yes (`KLR_SELFTEST pass=48 fail=0`) | 0.60 | true |
| 12 | live-ollama-lifecycle | 0 | yes (`"verdict": "MODEL_OK"`, nonce ctrun0001 accepted) | 1.67 | true |

Rows 1-4 and 6-12 match their recorded verdict (pattern emitted, exit 0). Row 5 produced the declared host-busy outcome
(exit 2, `kama-context-capacity: host-not-idle-before-K1`); it did not produce the idle `all_ports_closed` verdict-true path
because the host was never idle. Total ~33.7 s.

## Context-capacity row (row 5) detail
- Waited the tool's own `--host-idle-timeout 20` (waited_s 20.066) and refused: cc.json `error: host-not-idle-before-K1`, `exit_code 2`, `cells: []`.
- `host_idle.other_pids_seen` (tool's own list, cc.json): 242776, 1706355, 2811272, 3262613, 2824550, 2828229.
- My `pgrep -x llama-server` immediately before AND after the row: 242776, 1706355, 3262613 (identical sets).
  - 242776 = operator llama-server port 45669 (LFM3-1.7B); 1706355 = operator llama-server port 1234 (--models-dir lfm3). Foreign by definition.
  - 3262613 = ollama-v0.40.11 llama-server, --port 37323, model path under /fast/scratch/hyaku/kama-r61-closure/c1/... : a leftover from round 61, not the operator pair and not a round-63 seat. I did not touch it.
  - 2811272, 2824550, 2828229 are in the tool's list but in neither of my pgrep snapshots: transient peer-seat llama-servers (sibling live probes) visible only during the 20 s window.
- The stdout is `{"all_ports_closed": true, "cells": 0, "observed": 0, "ports_used": []}` followed by the refusal line, so the row's `"all_ports_closed": true`
  pattern is present at exit 2 even though no cell ran. Verdict true therefore must key on exit 0 (the counter does: verdict true needs exit 0); a
  pattern-only check would read the busy refusal as verdict true. Observation for the C2 control set, not a verdict.

## Other observations
- digest-ledger line: `tokens=145 blob=126 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`.
- hexrun-census line: `tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0`.
- Rows 3 and 12 (live) used no registered consumer ports; all rows ran with the 4-key env and none failed for a missing env var (LC_ALL absent is harmless).
- Wall times are single runs; row 5 is dominated by the fixed 20 s idle wait.

## Tally
EX03 rows=12 exit0=11 exit2=1(declared host-busy) pattern_present=12/12 recorded_match=12/12
