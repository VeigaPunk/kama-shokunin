VERDICT: partial — every headline count reproduces from `runs/` and `live/` against the 54a29268 blobs, but the C2 attribution wording overclaims, k7 has no targeted check, and two no-harm arms ran at cff9e62 plus an overlay rather than the commit tree.

# ScribeReportMeasurements — round 17 before → after measurements and no-harm list

Scope: the Report section "Before → after measurements" (C1 calibration, C2 operability) and the no-harm list, drawn from `.ufo/waves/round-17/runs/` and `.ufo/waves/round-17/live/`. Measured commit: `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (lane HEAD, round-17 build). Frozen pre-round tree: `cff9e62f05aa7cfb9059444f62eb787100719713`. Attacked: the C1 and C2 before→after numbers, the counting commands, the attribution logic behind C2's "0 accepted-bad, 0 inconclusive", and the no-harm claims.

Method: I did not rerun any counting command. I read the recorded JSON/exit/stderr/txt outputs, recomputed sha256 of the measured files as blobs at `54a29268` (`git show <rev>:<path> | sha256sum`), compared them with the working tree (`sha256sum`), and listed the commit diff (`git diff --name-only`/`--stat cff9e62 54a29268`). `git status --porcelain` in the lane shows only `?? .ufo/waves/round-17/falsify/` (sibling wave output). All lane reads were read-only. No tool was installed or updated by this seat.

## Pins at the measured commit

Working tree equals the `54a29268` blob for every measured file (checked 2026-10-20).

| File | sha256 at 54a29268 = worktree | Frozen (cff9e62) | Recorded in |
|---|---|---|---|
| `tests/probe-verdicts/check.py` (current) | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | — | `runs/fault-controls-current.json` `check_sha256`; `runs/noharm-README.txt` |
| `.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py` (before) | `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762` | matches `frozen/manifest.json` | `runs/fault-controls-frozen.json` `check_sha256` |
| `tests/probe-verdicts/fault-controls.py` (detector) | prefix `d3eaadeb8a061b4e` | — | **not recorded in any run JSON** (see F3) |
| `tools/kama-probe.sh` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | same (`frozen/manifest.json`) | `runs/fault-controls-*.json` `probe_sha256`; `live/gate.txt` |
| `tools/kama-llamacpp-live.py` (current) | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` | — | `runs/controls-current.json` `tool_sha256`; `live/gate.txt` |
| `tools/kama-llamacpp-live.py` (before) | — | `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` | `runs/controls-frozen.json` `tool_sha256` |
| `tests/llamacpp-live/check-receipt.py` (current gate) | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` | — | `runs/controls-current.json` `gate_sha256` |
| `tests/llamacpp-live/check-receipt.py` (before gate) | — | `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` | `runs/controls-frozen.json` `gate_sha256` |
| `tests/llamacpp-live/controls.py` (instrument, both arms) | prefix `aad8b1c758fe9616` | — | not recorded in any run JSON |
| `tests/probe-verdicts/` matrix, 9 JSON files | set `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` | byte-identical: `git diff --name-only cff9e62 54a29268 -- tests/probe-verdicts` lists only `check.py` and `fault-controls.py` | `runs/mutants-grid.json` `matrix.set_sha256`; `runs/fault-controls-*.json` `matrix.sha256` |
| `.ufo/waves/round-17/c1/mutants.py` | prefix `498d1f7fa7f248d7` (worktree, clean) | — | not recorded in any run JSON |

## Before → after measurements

### C1 calibration — `check.py` grades `served_model`, route, malformed output; fault-control detector; mutant grid

Counting commands (as recorded in `corpus/lessons/round-17.md` §Measurements; exit codes from the `.exit` files):

1. `python3 tests/probe-verdicts/fault-controls.py --check .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --json` → `runs/fault-controls-frozen.json`, exit 1 (`runs/fault-controls-frozen.exit`).
2. `python3 tests/probe-verdicts/fault-controls.py --check tests/probe-verdicts/check.py --json` → `runs/fault-controls-current.json`, exit 0 (`runs/fault-controls-current.exit`).
3. `python3 .ufo/waves/round-17/c1/mutants.py --grid --out .ufo/waves/round-17/runs/mutants-grid.json` → `runs/mutants-grid.json`. No `.exit` file was recorded for this command; its stderr reads `wrote …/mutants-grid.json` (`runs/mutants-grid.stderr`). Exit code: not recorded.

| Measure | Before (frozen check.py `b853576e…`) | After (current check.py `ddc3f3cc…`) | Source |
|---|---|---|---|
| Fixed-detector faults accepted (F1–F8) | **3 of 8**: F5 served_model, F6 route skip, F8 malformed | **0 of 8** | `runs/fault-controls-frozen.json` `.accepted`=3, F5/F6/F8 `detected`=false; `runs/fault-controls-current.json` `.accepted`=0 |
| Fixed-detector faults detected | 5 of 8 | 8 of 8 | same files, `.detected` |
| Positive control F0 | detected | detected | `positive_control.detected`=true in both |
| Mutants killed, full detector, all applicable | **7 of 8** (M8 malformed-output-passes survives) | **10 of 10** | `runs/mutants-grid.json` cells with `detector`=`full` |
| Mutants killed, full detector, common applicable set (M0–M5, M8, M9) | 7 of 8 | 8 of 8 | same cells; M8 flips survived→killed |
| Mutants killed, pair detector (55/17 vs 72/0) | **1 of 8** (only M9 reject-all) | **1 of 10**; on the common set still 1 of 8 | cells with `detector`=`pair`; M6/M7 are `site_missing` for frozen |
| Round-16 pair baseline reproduced | 55/17 exit 1 (frozen probe) | 72/0 exit 0 (current probe) | `runs/mutants-grid.json` cells[].baseline `r16_reference` |

Reading: the gain is entirely under the full detector. Under the round-16 pair detector neither gate is distinguished on the common set (1 of 8 → 1 of 8), which the lane states.

### C2 operability — receipt v2, gate v1+v2, fail-capable checks, controls

Counting commands (as recorded in the lesson and scorecard; exit codes from `runs/controls-*.exit`):

1. `python3 tests/llamacpp-live/controls.py --tool <frozen tool> --gate <frozen gate> --json` → `runs/controls-frozen.json`, exit 1.
2. `python3 tests/llamacpp-live/controls.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --json` → `runs/controls-current.json`, exit 0.
3. `tools/kama-llamacpp-live.py` ×3 on b11755, each gated by `tests/llamacpp-live/check-receipt.py` → `live/receipt-{1,2,3}.json`, `live/gate.txt` (`VALID`, exit 0 each). The `.stderr`/`.stdout` files of the three runs are empty.

| Measure | Before (frozen tool `b8c5e8d4…` + gate `6b9576a1…`) | After (current tool `0efd1723…` + gate `ad680179…`) | Source |
|---|---|---|---|
| Bad controls accepted (k1–k8) | **6 of 8**: k1 health, k2 loading envelope, k4 SIGKILL, k5 exit 1 on SIGTERM, k6 teardown fault (escaped, no receipt), k8 default SIGTERM disposition | **0 of 8** | `runs/controls-frozen.json` `.accepted_bad`=6, `.controls[].accepted`; `runs/controls-current.json` `.accepted_bad`=0 |
| Inconclusive (rejected for the wrong reason) | 1 (k3 self-exit) | 0 | `.inconclusive` |
| Gate-flip arm (doctored receipt re-run through gate) | 0 accepted (`gate_flip_bad`=0) | 0 accepted, every bad control's gate-flip `rejected`=true | `.gate_flip_bad`; `.controls[].gate_flip` |
| Good control k0 | accepted | accepted | `.good_ok`=true both |
| Current targeted failing check per bad control | — | k1 `health_ready`; k2 `loading_envelope_graded`; k3 `teardown_graceful`+`teardown_port_closed`; k4,k5,k6,k8 `teardown_graceful`; k7 `teardown_graceful`+`teardown_port_closed`+`loading_envelope_graded` | `runs/controls-current.json` `.controls[].failed_checks` |
| Real b11755 runs | — (no v1 live run counted here) | 3 runs; each 11/11 checks `passed`; gate `VALID` with probe `36b64978…` and tool `0efd1723…` pins | `live/receipt-{1,2,3}.json` `.checks`; `live/gate.txt` |

Per real run (`live/receipt-{1,2,3}.json`):

| Run | port | child_pid | ended (UTC) | total 503 responses / distinct bodies | `teardown_graceful` observed | `health_ready` body |
|---|---|---|---|---|---|---|
| 1 | 40089 | 1677834 | 2026-10-20T15:57:45.050Z | 42 / 1 | alive true, returncode 0, sigterm_sent true, sigkill_sent false | `{"status":"ok"}`, 200 |
| 2 | 43091 | 1677955 | 2026-10-20T15:57:45.248Z | 45 / 1 | same | same |
| 3 | 38545 | 1678081 | 2026-10-20T15:57:45.445Z | 45 / 1 | same | same |

The 503 body is the same bytes in all three runs (`body_sha256` baa09177…). Model `stories260K.gguf` sha256 `270cba1b…` unchanged pre/post (`model_unchanged`).

## No-harm list

Each item: evidence, and whether this seat verified it or only cites the recorded output.

1. **Probe unchanged.** `tools/kama-probe.sh` is `36b64978…` at cff9e62 (frozen manifest), at 54a29268, and in the worktree; `git diff --name-only cff9e62 54a29268 -- tools/kama-probe.sh` is empty. *Verified by this seat.*
2. **Matrix unchanged.** The 9 matrix JSON files in `tests/probe-verdicts/` are byte-identical across cff9e62→54a29268; only `check.py` and `fault-controls.py` changed (`git diff --stat`: 2 files, 997 insertions, 16 deletions). Set digest `bf9068d8…` recorded in `runs/mutants-grid.json`. *Verified by this seat (diff); digest as recorded.*
3. **`tools/test-snapshot.sh` unchanged** cff9e62→54a29268 (`git diff --name-only` on that path empty). Result `RESULT pass=30 fail=0`, exit 0 (`runs/noharm-test-snapshot.txt`). The run was at cff9e62 (see L3).
4. **Round-16 measure PASS.** `runs/noharm-r16-measure-clone.txt`: before 55/17 exit 1, after 72/0 exit 0, 17 verdict changes all `MODEL_LOADING` expectations, `measure exit=0`. Run in a `/tmp` clone at cff9e62 with the current `check.py` (`ddc3f3cc…`) overlaid (`runs/noharm-README.txt`). The round-16 measure inputs (`.ufo/waves/round-16/`, `tools/test-snapshot.sh`, `tools/kama-probe.sh`) are unchanged between the two commits, so the overlay equals the commit tree for these inputs. *Verified by this seat (diff); the run itself is as recorded.*
5. **Round-16 v1 receipts still VALID** under the current gate (`runs/v1-receipts-current-gate.txt`): `receipt.json` exit 0, `receipt-frozen-probe.json` exit 0; the frozen-receipt/current-pin case exits 1 as designed.
6. **Receipt gate selftest:** 2 valid receipts accepted; 39 mutations plus an unreadable case rejected; exit 0 (`runs/selftest-check-receipt.txt`; the scorecard's 26 v1 + 13 v2 split is consistent with 39).
7. **`check.py --selftest`:** `tests=72 passes=72 failures=0`; `5/5 malformed tests rejected`; exit 0 (`runs/selftest-tests_probe-verdicts_check.py_--selftest.txt`).
8. **Round-13 measure selftest 13/13** (`"passed": 13` in `runs/selftest-.ufo_waves_round-13_measure.py_--selftest.txt`, line 155; exit 0).
9. **Other selftests exit 0:** count-verdicts 16 classifier cases (`runs/selftest-.ufo_waves_round-17_count-verdicts.py_--selftest.txt`); dispatch-provenance 28/28 (`runs/selftest-.ufo_waves_round-17_dispatch-provenance.py_--selftest.txt`); sources-append-only 14/14 (`runs/selftest-tools_sources-append-only.py_--selftest.txt`); mutants selftest (`runs/selftest-.ufo_waves_round-17_c1_mutants.py_--selftest.txt`, exit 0).
10. **Registered consumer ports untouched.** Receipts used ports 40089, 43091, 38545 (bind(:0) path). `registry/endpoint-consumers.tsv:35` and `:36–37` name 8080 and 34113. The receipts list them only as `port_refusal_set` ([8080, 34113]). The default `pick_port` path connects only to the offered port; the refused set is never dialled (`tools/kama-llamacpp-live.py:68` `HARD_REFUSED_PORTS = {8080, 34113}`; `pick_port` lines 275–306). An explicit `--port` path does connect (line 291–300), and no run passed `--port` to the tool. *Verified by reading the code at 54a29268.*
11. **Lane tree clean.** `git status --porcelain`: only the untracked `.ufo/waves/round-17/falsify/` (sibling output). No lane tracked file was modified by this seat.

## Findings

F1 — **partial (C2 attribution overclaims its own rule).** `tests/llamacpp-live/controls.py:26`: "A rejected run whose failed checks do not cover the token set is ``inconclusive``." The code at `:454–460` is `return any(tok in fid for tok in expected for fid in low)`, documented as "at least one token appears". Consequence: k6 expects `['teardown','fault']` but its only failed check is `teardown_graceful` (`runs/controls-current.json`, k6); the `fault` token is never matched and k6 is still `attributed: true`. Under an all-of reading, k6 (and k4, k5, k8, whose token lists are alternatives) would be inconclusive, and the current "0 inconclusive" would not hold. The token lists look like intended any-of alternatives [INFERENCE from the list shapes], so this is a wording fix, not a changed number — but the docstring is the M2 class again: a documented rule the code does not implement.

F2 — **partial (C2 "each bad control fails its targeted check" is true for k1–k6 and k8 only).** `tests/llamacpp-live/controls.py:322`: `'k7': ('k7', ['--ready-timeout', '2'], False, [],` has no expected token, so `attributed` is `None` and k7 is never attributed. Its rejection is by `teardown_graceful`, `teardown_port_closed` and `loading_envelope_graded` (`runs/controls-current.json`, k7), not by any ready-timeout check. `corpus/lessons/round-17.md` §Measurements (C2 bullet) says "each bad control failing its targeted check"; `SCORECARD.md` §Round 17 C2 row says "each failing its targeted check". Both overstate for k7. Accepted-bad = 0 still holds, because k7 is rejected.

F3 — **gap (reproducibility of C1 numbers).** The before/after C1 run JSONs record `check_sha256` and `probe_sha256` and the matrix digest, but not the sha of the detector itself (`tests/probe-verdicts/fault-controls.py`, prefix `d3eaadeb`), nor of `mutants.py` (prefix `498d1f7f`). `runs/mutants-grid.json` has no exit-code record. Neither changes a number here; both are needed to re-derive the counts from the runs alone.

F4 — **provenance (run location).** The seat rule for lane tool runs is a `/tmp` clone at the measured commit. The recorded paths are lane paths: `runs/mutants-grid.json` `probes.current.path` = `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh`; cells[].`check` = `…/kama-shokunin/tests/probe-verdicts/check.py`; `runs/fault-controls-current.json` `check` is the relative `tests/probe-verdicts/check.py`. The corpus says these were "Commands run by L1 after wave 1 returned" (`corpus/lessons/round-17.md` §Measurements). [INFERENCE: run in the lane by L1.] The numbers are still trustworthy as of the measured commit, because the worktree was clean and every measured file hashes equal to its `54a29268` blob (table above).

F5 — **limitation (no-harm arms at a different tree).** `runs/noharm-README.txt` records the round-16 measure and `test-snapshot.sh` as run at cff9e62 with the current `check.py` overlaid, not at 54a29268. The diff check in no-harm items 3–4 shows the inputs are equal, so this is a labelling gap, not a result change.

F6 — **limitation (parent-death guard requested, not observed).** Each receipt's `pdeathsig` is `{"prctl_ok": "unknown", "requested": true}` (`live/receipt-{1,2,3}.json`). No one of the 11 checks grades it. The C2 claims do not depend on it, but the live receipts do not show that the guard took effect.

F7 — **precision (503 wording).** The lesson's "loading_envelope_graded over every stored 503 body" is accurate under dedup: `total_503_responses` is 42, 45 and 45 (`live/receipt-{1,2,3}.json`, `loading_envelope_graded.observed`), and `distinct_bodies` is 1 in every run. Each run grades one distinct body; the other responses are counted, not individually re-graded. Consistent with the stated limit "bodies are deduped by sha256".

F8 — **comparison caveat (denominators).** The mutant applicability differs between arms: M6 and M7 are `site_missing` for frozen (`runs/mutants-grid.json`). The "10 of 10 vs 7 of 8" comparison therefore mixes sets. The common-set comparison (8 of 8 vs 7 of 8 under full; 1 of 8 vs 1 of 8 under pair) is the honest form and is what the table above reports.

## Limitations

- No counting command was rerun by this seat; numbers are as recorded in `runs/` and `live/`, with the blob and diff checks above as the only re-derivation.
- The live receipts are three b11755 runs on one host with one model (`stories260K.gguf`); they show lifecycle behaviour of that real llama-server build (not a fake), not a general claim about llama.cpp.
- `tools/kama-llamacpp-live.py` argv in each receipt is the child's argv. The `--port` in the receipt is the llama-server argument, not the tool's `--port` flag.
- k6 was rejected by `receipt_written` plus `tool_exit=2` (`runs/controls-current.json`), not by a receipt check; "receipt on internal fault" is graded by `controls.py`, not by `check-receipt.py`.

## Tool installs

None by this seat. No `pacman`, `uv tool`, `npx` or binary installs were made.

## Scratch

Two scratch files under `/tmp` (controls.py and kama-llamacpp-live.py copies from `git show`) were created and removed in the same command. No other scratch exists. No lane file other than this Report was written.

## Outside verdict per claim

C1: [L1 fills after falsify]
C2: [L1 fills after falsify]
No-harm list: [L1 fills after falsify]
