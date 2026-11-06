# EX02HarmSweep — round-89 harm sweep (base B vs measured M2)

## Scope
- Lane /home/vgpnk/Projects/shokunin/kama-shokunin, round 89, axis operability.
- Two dedicated `git clone --shared` checkouts in /fast/scratch/hyaku/kama-r89/EX02HarmSweep/:
  `wtb` at B=56174a1fa6a27faa91d3664ef4730b48dd3149c0, `wt` at M2=21b9e36d6192e0a691550b32e0e6c38412227f4c
  (both `git rev-parse --show-toplevel` verified as the clone root; worktrees clean before runs).
- Probe bytes measured: B sha256 99dd1ab8d41bb682bb24d4747b85d1f86fb84c145c6531cd2f0201d738d54be5,
  M2 sha256 a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf
  (matches `probe_sha256` printed by the frozen round-88 counter at M2).
- Operator router 127.0.0.1:1234 was touched GET-only through `kama-probe.sh check` (no POST; no completion,
  load or unload). All other live work ran on lane-owned children started and killed by the arm tools.
- Host was carrying ~50 concurrent fleet seats; latency numbers are medians of 5 interleaved runs and are
  indicative, not a quiet-host benchmark.

## Commands and outputs (exit codes are true)
Run from each clone (B = wtb, M2 = wt):
1. `python3 tests/probe-verdicts/check.py` — B exit 0 `tests=72 passes=72 failures=0`; M2 exit 0 same.
2. `bash tools/test-snapshot.sh` — B exit 0 `RESULT pass=30 fail=0`; M2 exit 0 same.
3. `python3 tools/round88-router-cells.py --repo <clone> --rev <rev> --work <scratch>` —
   B exit 1 `ROUTER_CELLS cells=17 mismatches=2 ... probe_sha256=99dd1ab8…`; M2 exit 1
   `mismatches=2 canned=14 live=3 probe_sha256=a4f496bb…`; both mismatch sets are exactly C05-sleeping and
   C12-wildcard-none-loaded (expected=MODEL_UNLOADED observed=MODEL_OK reason=router-sleeping ok=0).
4. `python3 .ufo/waves/round-88/repair/oracle-cells.py --repo <clone> --rev <rev> --work <scratch>` —
   B exit 0 `ORACLE_CELLS rev=56174a1f… cells=3 mismatches=0`; M2 exit 0 `cells=3 mismatches=0`.
5. `python3 tools/round79-unregistered-census.py --selftest` — B exit 0 `pass=4 fail=0`; M2 exit 0 same.
6. `python3 tools/round78-live-reconcile.py --selftest` — B exit 0 `pass=4 fail=0`; M2 exit 0 same.
7. `python3 tools/pre-report-gate.py --repo <clone> --round 89 --tip 21b9e36d…` — B exit 1
   `PRE_REPORT round=89 arms=14 failed=3 uncommitted=0`; M2 exit 1 same counts. Per arm:
   - 1 selfdesc FAIL both (`closure_ptr: calibration row latest outside closure is round-87; newest … round-88`)
   - 2 newest-closure FAIL both (`STALE_CALIBRATION … round-87-verifier-spotcheck.md`)
   - 3 receipt-audit, 4 worktree-landing, 5 round-scope, 6 round-clean, 7 round74-v2: exit 0 both
   - 8 round75-instruments: B exit 2 could-not-evaluate (`no frozen plan at 56174a1f:plans/round-89-claims.md`);
     M2 exit 1 FAIL (`APPEND_DEBT … bad_rows=19 … hash-mismatch late line 96 cf28c470…`)
   - 9 round77, 10 round78, 11 round81, 12 round82, 13 round83, 14 round86: exit 0 both
8. Operator 1234, `bash <probe> check --port 1234 --expect <id> --json --timeout 5 --connect-timeout 2`
   (defaults), 4 ids x 5 runs per probe, B and M2 interleaved: every run exit 0,
   verdict `MODEL_OK` reason `router-unloaded-autoload` for LFM3-1.7B, LFM3-1.7B-Uncensored,
   LFM3-Omni-2B, LFM3-VL-2B. Medians (added = M2 − B):
   LFM3-1.7B 130.5→1530.7 ms (+1400.2); Uncensored 135.5→1518.1 (+1382.6);
   Omni-2B 138.0→1469.6 (+1331.6); VL-2B 135.6→1438.0 (+1302.4).
   Wildcard `--expect '*'`: B 0.09 s x3, M2 1.09/1.11/1.09 s.
9. Largest GGUF on host, M2's `file_state()` extracted verbatim from the probe, 5 runs each:
   qwen-image-edit-2511-Q4_K_S 12.411 GB → `ok`, 4.8 ms, 262,257 B read; qwen-image-2512 12.268 GB → 4.3 ms;
   LFM3-1.7B-Q8_0 1.846 GB → 256.2 ms, 7,864,430 B read; LFM3-1.7B-Uncensored-AD-Q6_K 1.588 GB → 259.5 ms;
   LFM3-Omni-2B-Q8_0 1.846 GB → 244.1 ms; LFM3-VL-2B-Q8_0 1.846 GB → 246.3 ms; mmproj 0.2-0.5 GB → 0.4-1.4 ms;
   stories260K 1.2 MB → 0.5 ms.

## Findings

- HARM (operability, latency; no verdict change) — the M2 probe adds ~1.3–1.4 s (10–11x) to every live-router
  `check` on 127.0.0.1:1234: B ~130–138 ms → M2 ~1438–1531 ms (medians of 5; item 8 above). Cause: the embedded
  router scan computes `file_state()` for EVERY `unloaded`, not-failed entry before matching, so a per-id check
  parses all four LFM3 headers regardless of `--expect`; the ~1.4 s is ~4 x 250–350 ms of header parsing.
  Evidence: M2 tools/kama-probe.sh:661 (`fstate = file_state(st.get("args"))` inside the per-entry loop) and
  tools/kama-probe.sh:710 (`router_entries` scan feeding `router_refine`); wildcard run is equally slow
  (0.09 s → 1.09 s), confirming the cost is unscoped. Receipts: operator-1234-timing.out,
  operator-1234-runs.jsonl, wildcard-timing.out. This is not covered by C1's K2 (no suite in K2 measures
  latency and no verdict changed); it is still a real operability regression the L1 should disposition.
- NOTE — no false red/green was introduced on the operator router: 4/4 ids grade `MODEL_OK`
  `router-unloaded-autoload` exit 0 at both revisions (their files are present and valid GGUF, so the new
  header path only pays cost, never flips a verdict). Evidence: operator-1234-runs.jsonl.
- NOTE — the header check is metadata-bound, not size-bound, and reads no tensor data: the 12.4 GB Qwen GGUF
  costs 4.8 ms / 262 KB read, while a 1.85 GB LFM3 costs ~250 ms / 7.86 MB because its header holds 128,000
  tokenizer tokens + 293,320 merges (45 KVs, 287 tensors). Evidence: gguf-file-state-timing.out,
  router_entries_module.py. "Largest GGUF on this host" is therefore the cheap case.
- NOTE (risk, unscoped growth) — cost grows linearly with the number of local `unloaded` entries on any
  router: 4 entries ≈ 1.0–1.4 s/check, 20 metadata-heavy entries ≈ 5 s+/check, and the probe has no overall
  deadline (only per-request `--timeout`). A router with a cold page cache or slow-mounted model dir pays the
  read too. Same evidence pointer as the HARM above.
- NOTE — the round-88 debt is unchanged by M2: `round88-router-cells.py` stays `mismatches=2` on C05/C12
  (exit 1 at both revisions), so the round-89 file-state change neither fixes nor worsens the frozen
  sleeping/wildcard false greens; the frozen `mismatches=2` kill rule holds.
- NOTE — pre-report gate parity: same `failed=3` at B and M2, and arms 3–7 and 9–14 are green at both.
  Arm 8 differs only because the base clone's HEAD predates `plans/round-89-claims.md` (could-not-evaluate)
  while the M2 clone can read the round-89 plan and surfaces the carried R4 append-debt (`bad_rows=19`,
  hash-mismatch late line 96 `cf28c470…`). Arms 1–2 (closure pointer / calibration freshness) fail at both
  revisions, i.e. pre-existing lane state, not a C1/C2 regression.
- NOTE — every probe interaction with 1234 was GET-only: `check` issues GET /v1/models, GET /health and
  GET /props (autoload detection); no POST/completion appears anywhere in tools/kama-probe.sh.

## Deliverables
All under `.ufo/waves/round-89/w1/out/EX02HarmSweep/`:
`base-probe-verdicts.out`, `tip-probe-verdicts.out`, `base-test-snapshot.out`, `tip-test-snapshot.out`,
`base-router-cells.out`, `tip-router-cells.out`, `base-oracle-cells.out`, `tip-oracle-cells.out`,
`base-census-selftest.out`, `tip-census-selftest.out`, `base-reconcile-selftest.out`,
`tip-reconcile-selftest.out`, `base-pre-report-gate.out`, `tip-pre-report-gate.out`,
`operator-1234-runs.jsonl`, `operator-1234-timing.out`, `wildcard-timing.out`,
`gguf-file-state-timing.out`, `revisions-probe-sha.txt`, `probe_timing.py`, `router_entries_module.py`.
No tracked lane file was modified; all scratch was confined to /fast/scratch/hyaku/kama-r89/EX02HarmSweep
and is removed before yield.

VERDICT: partial — every frozen B-vs-M2 harm arm holds (72/72, 30/0, round88 mismatches=2 C05/C12 only, oracle 0, selftests 4/4, gate failed=3 both), but M2 adds ~1.3–1.4 s (10–11x) per live-router check because file_state runs for every unloaded entry; verdicts unchanged.
