# K2Checks — attack: C2 replay comparison (round 47, lane kama)

**Verdict:** The C2 replay comparison is check-pass/fail-only; two receipts can agree on every evaluated check and still disagree on what was observed — proven with the lane's own three b11909 receipts and three fresh replays — and the only way a stricter replay can tighten this is a *stable-projection* comparison that pins digests, statuses, extracted fields and the teardown contract but explicitly ignores ports, pids, wall-clock stamps, counts and per-process random marker bytes (proposed patch in `proposed-compare.diff`).

## Evidence

All runs used scratch `$S=/fast/scratch/hyaku/kama-r47/K2Checks`; lane read-only, receipts from `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json` (schema `kama-llamacpp-live/v4`, all `outcome=pass`, 11 evaluated checks, all passed).

### 1. Replays (kama-live-replay.py)
Command (per receipt, `n=1,2,3`):
```
python3 <lane>/tools/kama-live-replay.py --receipt <lane>/.ufo/waves/round-47/c2/live/receipt-$n.json --work $S/w$n --out $S/w$n/replay.json --timeout 900
```
Output (all three):
```
replay match=True refused=None mismatches=0 exit=0
```
`exit=0` for all three; `$S/w$n/rerun-receipt.json` written. The rerun receipts keep: `schema` v4, `outcome=pass`, 11 evaluated checks, all passed, identical to receipt-$n (`parity=True`); `server.sha256`/`model.sha256`/`model_sha256_post` equal; `teardown` = `log_path=None`, `returncode=0`, `sigterm_sent=True`, `sigkill_sent=False`, `port_refuses=True`, `alive_at_teardown_start=True`, `term_wait_ms=3`; `loading_envelope_exact=True`, `loading_observed=True`, `loading_bodies_dropped=0`; `pdeathsig={'prctl_ok':'unknown','requested':True}`; `port_listener_ownership='child'`; props `fields` identical (`build_info=b11909-caa8191df`, `default_generation_settings.n_ctx=256`, `is_sleeping=False`, `model_alias=kama-r47-live`, `total_slots=4`).

### 2. What differs between runs (deep JSON diff of receipts vs reruns)
`Python` deep-diff of each receipt-$n vs its rerun and of receipts pairwise. Captured values observed to differ:

| Field(s) | Values observed (6 runs) | Class |
|---|---|---|
| `port` (+ `argv[8]`, `probes[*].argv[4]`, `probes[*].result.rows[0].declared`, teardown listening line) | 37903, 44883, 39739, 46063, 35551, 33327 | instance |
| `child_pid` | 3871869, 3872567, 3873367, 385695, 398566, 409846 | instance |
| `started_utc` / `ended_utc` | e.g. 21:16:50.545Z vs 21:29:46.336Z | instance |
| `transitions[*].t_ms`, `loading_503.t_ms` | 6–14 ms | instance |
| `transitions[0].repeats` | 245, 227, 191, 203, 200, 229 | instance |
| `transitions[1].repeats` / `loading_503_bodies[0].repeats` / `checks[9].observed.total_503_responses` | 17/33/28/1/0/0; 18/34/29/2/1/1 | instance |
| `teardown.log_lines[*]` | relative clock offsets + model path + port (e.g. `0.00.005.256` vs `0.00.004.807`; `...:37903` vs `...:46063`) | instance |
| `server.arg`/`server.realpath`, `model.arg`/`model.path`, `argv[0]`, `argv[2]` | lane install paths vs scratch re-acquired paths | instance |
| `captures.props.body_sha256` (+ `Content-Length` 2067→2077) | 6 distinct values | byte-volatile (see 4) |
| `captures.models.body_sha256` / `transitions[2].body_sha256` | 6 distinct values | byte-volatile (see 3) |
| `captures.models.body.data[0].created` | 1793049410, 1793049411, 1793050186, 1793050188, 1793050190, 1793050272 | instance |

Identical across all six runs (stable): `schema`, `alias`, `ctx=256`, `threads=1`, `outcome`, `server.sha256=35ac50fb…`, `server_impl_sha256`, `install_tree_sha256`, `install_links_sha256`, `model.sha256=270cba1b…`, `model_sha256_post`, provenance block, `captures.health` (body `{"status":"ok"}` + sha `a29ee2b1…` + status 200 + headers), `captures.metrics.status=501`, `captures.slots.element_count=4` (+ slots body sha), loading-503 body/sha `baa09177…` + headers, `port_refusal_set={8080,34113}`, `pdeathsig`, teardown rc/signals/refusal/log_path/alive/truncation, probe verdicts (`MODEL_OK` exit 0 / `MODEL_MISMATCH` exit 2, reasons `matched`/`served-id-mismatch`), `child_env_keys` membership.

### 3. Why models bodies differ — `created` is wall clock
`server-context.cpp` @ b11909 commit `caa8191d` line 5502:
```cpp
{"created",  std::time(0)},
```
Confirmed empirically: `created == floor(epoch(started_utc))` for all six runs (e.g. receipt-1 `1793049410` = floor(21:16:50.545Z); rerun-1 `1793050186` = floor(21:29:46.336Z); receipts 1/2 in the same second share `1793049410`, receipt-3 next second has `1793049411`). The parsed models data is otherwise byte-identical across runs — `created` is the only difference (`keys only in orig: set() only in rerun: set(); differs: .created`).

### 4. Why props bodies differ — per-process random `media_marker`
`server-context.cpp` line 5574:
```cpp
{ "media_marker",                get_media_marker() },
```
Two instrumented runs (copy of the live tool pinned to the lane's absolute `LANE`, `--probe $S/kama-probe.sh`; both `exit=0`) captured raw bodies from the same server binary and model, same work paths:
```
/props: DIFFER
  first diff at 1286: ..."media_marker":"<__media_MLcMj2cyVsgrIPHRwwxt0Bpwu3TcX2LQ__>",...
                     vs ..."media_marker":"<__media_yXlTrMnnNSOuyDYWldCnmDF1VdUxWK8R__>",...
  len 2077 vs 2077
  keys only in run1: set()  only run2: set()
  key media_marker: '<__media_MLcMj2cyVsgrIPHRwwxt0Bpwu3TcX2LQ__>' vs '<__media_yXlTrMnnNSOuyDYWldCnmDF1VdUxWK8R__>'
```
`/health` (15 chars), `/metrics` (136), `/slots` (253) and `/v1/models` bodies were identical in those two runs. The extracted `fields` projection (the five keys the live tool stores) is stable even though the raw props body is not.

### 5. Counterexample: agreement on checks ≠ agreement on observation
- Receipt-1 vs receipt-3: both pass all 11 evaluated checks, yet their captured observations differ — models `created` (1793049410 vs 1793049411), `captures.props.body_sha256` (fb5e3e82… vs 9089951c…), `total_503_responses` (18 vs 29), port/pid/utc.
- Replay of receipt-1 reports `match=True` even though its own rerun differs from receipt-1 on the same kinds of fields (`created` 1793050186, props sha 4e9f5643…, `total_503_responses` 2, port 46063).
- The replay `compare()` only checks `schema`, `outcome`, `server.sha256`, `model.sha256`, and evaluated-check pass/fail parity (kama-live-replay.py:108-124); the C2 counter additionally checks rerun `started_utc >= counter start`, input digests, and that re-acquired inputs sit under scratch (round47-live-replay-audit.py:273-289). Neither compares observations.

## Classification for a stricter replay

**Must compare (stable facts):** `schema`/`outcome`/`alias`/`ctx`/`threads`; digest triple (`server.sha256`, `model.sha256`, `model_sha256_post`); `build_info` prefix `b11909-`; health body sha + status 200; metrics 501; slots `element_count` + body sha; loading-503 body sha and `loading_envelope_exact`/`loading_observed`; teardown `returncode=0`, `sigterm_sent`, `sigkill_sent=False`, `port_refuses`, `alive_at_teardown_start`, `log_path=None`; `port_listener_ownership='child'`; probe verdicts/reasons/exits; evaluated-check parity; extracted props `fields`; models body parsed **minus `created`**.

**Must ignore (instance facts):** `port` and everything derived (probe argv/declared rows, listening line), `child_pid`, `started_utc`/`ended_utc`, all `t_ms`, all `repeats`/`*_503_responses` counts, teardown log-line offsets, absolute paths (`server.arg/realpath`, `model.arg/path`, `argv[0]`/`argv[2]`), `child_env_keys` values, `port_refusal_set` contents, `term_wait_ms` jitter.

**Byte-volatile, compare normalized:** `captures.models.body_sha256` (strip `created`, server-context.cpp:5502); `captures.props.body_sha256` (strip `media_marker`, server-context.cpp:5574) — or compare the extracted `fields` instead.

## Defect and proposed fix
- Defect: `tools/kama-live-replay.py` `compare()` (lines 108–124) cannot see observation drift; fields like `created` and `media_marker` make byte-exact body comparison impossible without normalization, and the current evaluator never attempts it.
- Command that shows it: the diffs above; or `python3 tools/kama-live-replay.py --receipt <lane>/.ufo/waves/round-47/c2/live/receipt-1.json --work $S/w1 --out $S/w1/replay.json` prints `match=True` while `$S/w1/rerun-receipt.json` carries a different `created`, props sha and 503 count than the receipt.
- Proposed fix: add a stable-projection comparison to `compare()` that compares health body sha, models stable data (minus `created`), props `fields`, slots `element_count`, loading-503 body sha + envelope flags, teardown booleans/returncode/log_path, and port ownership — and ignores all instance facts. Patch: `.ufo/waves/round-47/w1/out/K2Checks/proposed-compare.diff` (unified diff against `tools/kama-live-replay.py`). Validated: `compare(orig1, rerun1) == []` (no false positive), `compare(orig1, orig3) == []` (legitimate cross-run variance not flagged), and a doctored model `id` is caught (`capture:models.stable:…`).

## Files written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks/proposed-compare.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks/receipt-1.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks/receipt-2.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks/receipt-3.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Checks/install.txt
