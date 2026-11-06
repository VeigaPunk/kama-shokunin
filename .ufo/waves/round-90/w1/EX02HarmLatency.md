# EX02HarmLatency — r90 w1 (harm re-run at M, latency budget, R2 recovery)

## Scope
Re-ran the four C1 harm receipts at M `f968fb19bb2a0c2afe271bfe606f11b52d10823f` (probe sha256
`c197912f…`, identical to the lane working tree at `2ee0b55f`), measured base-vs-M latency on
lane-owned stubs and GET-only on the operator router, and answered R2 (r89 `bc` loss) from the
r89 receipts. Read-only in the lane; all writes under `.ufo/waves/round-90/w1/out/EX02HarmLatency/`
and this file. No tool installs were needed (curl 8.23.0, python 3.14 present); pacman untouched.

## Commands and outputs (exit codes)
1. `git -C <lane> status --porcelain tools/kama-probe.sh` → empty output, exit 0. Probe sha256 at
   HEAD `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97` = probe at M.
2. `git clone --shared <lane> <scratch>/wt && git -C <scratch>/wt checkout --detach f968fb19…` →
   exit 0, `rev-parse HEAD` = `f968fb19bb2a0c2afe271bfe606f11b52d10823f`, tree clean.
3. `cd <clone> && python3 tests/probe-verdicts/check.py` (TMPDIR=<scratch>) → `tests=77 passes=77
   failures=0`, exit 0 (42.9 s). Receipt `harm-M-probe-verdicts.out`.
4. `cd <clone> && bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`, exit 0. Receipt
   `harm-M-test-snapshot.out`.
5. `python3 tools/round89-unloadable-cells.py --repo <clone> --rev f968fb19… --work <scratch>` →
   `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev
   probe_sha256=c197912f… rev=f968fb19…`, exit 0. Receipt `harm-M-r89-cells.out`.
6. `bash <M probe> check --port 1234 --expect '*' --json` (GET only) → `MODEL_OK
   router-unloaded-autoload`, `served_model=LFM3-1.7B,LFM3-1.7B-Uncensored,LFM3-Omni-2B,LFM3-VL-2B`,
   summary exit 0. Receipt `operator-1234-M.json`.
   (First attempt exited 1: my TMPDIR pointed at a non-existent dir and `mktemp` failed — my
   harness error, not a probe defect; retried after `mkdir -p`, exit 0.)
7. `PROBES="base=<99cdb4d6 probe>,M=<M probe>" python3 latency.py` → exit 0. Receipts
   `latency.out`, `latency.json` (4 phases, 20/20/20/5 interleaved runs).
8. `PROBES="r89base=<56174a1f probe>,base=…,M=…" python3 latency.py` → exit 0. Receipts
   `latency-3probe.out`, `latency-3probe.json`.
9. `R89B_PROBE=<56174a1f> R89M_PROBE=<5b1e0fb3> python3 r89-reconstruct.py` → exit 0 (30 GET-only
   router runs). Receipts `r89-reconstruct.out`, `r89-reconstruct.json`.
10. `BASE_PROBE=… M_PROBE=… python3 file-state-blindspot.py` → exit 0. Receipt
    `file-state-blindspot.out`.
11. Diff of the re-run cells against `.ufo/waves/round-90/measured/harm-M.out`:
    `ROUTER_UNLOADABLE` lines, `tests=` line and `RESULT` line are byte-identical (diff exit 0).

## Findings

**NOTE (harm holds at M).** All four kill-rule K2 receipts reproduce at M, byte-identical to the
recorded M receipt and equal to the base receipts: 77/77, 30/0, 11 cells 0/0, operator
`MODEL_OK router-unloaded-autoload`. Evidence: `harm-M-probe-verdicts.out` (last 2 lines),
`harm-M-test-snapshot.out:31`, `harm-M-r89-cells.out:12`, `operator-1234-M.json`; recorded
`measured/harm-M.out`; base `controls/harm-base-*.out`. No K2 regression, `positive_mismatches=0`.

**NOTE (C1 latency cost is small).** base→M median ratio: stub-plain 128.6→135.2 ms (1.05x,
p90 1.10x), stub-json 128.9→133.3 ms (1.03x, 1.05x), router-stub 414.1→410.5 ms (0.99x, 1.06x),
operator 366.7→334.7 ms (0.91x, 1.06x). Across the eight phase-pairs in the two shipped receipts
the base→M median ratio is 0.91–1.05 and the p90 ratio 0.87–1.10. Evidence: `latency.out`,
`latency-3probe.out`, `latency.json`, `latency-3probe.json`.

**DEFECT (inherited, not caused by C1): a router check costs 3.2–3.5x the r89 base probe.** On a
lane-owned router-shaped stub (4 entries, 6 model paths, `/props` autoload) r89base 123.7 ms →
r90 base 394.7 ms = 3.19x, M 412.6 ms = 3.34x; on the operator router (GET only) r89base 136.6 ms
→ base 473.2 ms = 3.46x, M 457.9 ms = 3.35x. Cause is the r89 `file_state`/`gguf_state` header
scan over the matching entries' `--model`/`--mmproj` paths (kama-probe.sh:693-712, 747-756); the
cost scales with candidate count (one id 0.129→0.214 s = 1.66x, wildcard over 4 entries
0.125→0.398 s = 3.18x in `r89-reconstruct.out`). Absolute values are load-dependent (base medians
moved 66→559 ms across this seat's runs under fleet load); the ratio reproduces on the stub.
Evidence: `latency-3probe.out` (router-stub, operator-1234 phases), `r89-reconstruct.out`.
This is the price of the r89 `router-model-missing`/`-invalid` rule, not a C1 regression; the
actionable item is the frozen budget below.

**NOTE (R3 budget line, proposed frozen).** Gate on `latency.py` with the base and M probes,
interleaved in one session, 2 unrecorded warmups, nearest-rank median/p90:
`stub-plain` (20 runs, `--expect good`), `stub-json` (20 runs, `--expect good --json`) and
`router-stub` (20 runs, `--expect '*' --json`, the 4-entry stub in `latency.py`): **M median ≤ 1.5x
base median and M p90 ≤ 2.0x base p90**; operator 1234 (5 runs, GET only) is report-only, never a
gate. Rationale: C1 measures 0.91–1.05x median (p90 ≤ 1.10x), leaving headroom; the r89 file_state
regression (3.19x) and the r89 M2 regression (11x,
`round-89/w1/out/EX02HarmSweep/operator-1234-timing.out`) both fail it. A plain stub alone would
not catch the file_state class (1.03–1.05x), so the router-shaped
stub is required. Fixture trap: the stub's `status.args[0]` MUST be the absolute server binary —
`file_state()` returns `-` without opening any file otherwise (kama-probe.sh:695), so such a stub
silently exercises no file check (`file-state-blindspot.out` cell A).

**NOTE (R2: the lost per-call seconds are not recoverable; reconstruction given).**
`.ufo/waves/round-89/measured/harm-final.out:13-31` contains only `error: command not found: bc`,
six empty seconds fields, and four surviving medians (base 0.136/0.138, M' 0.251/0.362). Missing
exactly: the 30 per-run values (6 configs × 5 runs) and the 6 printed per-call seconds; the
generating script was never committed (no file in the lane produces that format). The one raw
timing file that does exist, `round-89/w1/out/EX02HarmSweep/operator-1234-runs.jsonl`, is a
different probe pair (56174a1f vs 21b9e36d, medians 130/1530 ms) and cannot be substituted.
Re-measured at the same two revisions with the same argv (new samples, labelled RECONSTRUCTION):
R89B `LFM3-1.7B` 0.129 s / `*` 0.125 s; R89M 0.214 / 0.212 / 0.209 / 0.202 s and `*` 0.398 s
against surviving 0.136 / 0.138 / 0.251 / 0.362 — −15%…+10% on the four comparable cells.
Evidence: `r89-reconstruct.out`, `r89-reconstruct.json`.

**NOTE (held-out cell, base == M, documented false green).** A router entry whose `status.args[0]`
is not an absolute file and whose `--model` path is missing grades `MODEL_OK
router-unloaded-autoload` on both base and M (cell A), while the same entry with the absolute
server binary first grades `MODEL_UNLOADED router-model-missing` (cell B); a valid path with a
relative `args[0]` stays `MODEL_OK` (cell C). This is the limitation SKILL.md:1802 already
documents ("path relative … unchanged"), so it is not a C1 regression — but it is a reproducible
false green for a router started with a relative binary path. Evidence: `file-state-blindspot.out`.

## Deliverables (all in `.ufo/waves/round-90/w1/out/EX02HarmLatency/`)
`harm-M-probe-verdicts.out`, `harm-M-test-snapshot.out`, `harm-M-r89-cells.out`,
`operator-1234-M.json`, `latency.py`, `latency.out`, `latency.json`, `latency-3probe.out`,
`latency-3probe.json`, `r89-reconstruct.py`, `r89-reconstruct.out`, `r89-reconstruct.json`,
`file-state-blindspot.py`, `file-state-blindspot.out`, `probe-shas.txt`.

VERDICT: holds — at M all four harm receipts equal base and C1 adds ≤10% latency; the 3.2–3.5x router cost is inherited from r89's file_state rule, and the frozen budget line above would catch it.
