# ReplicateReceipt — C2 receipt reproducibility (wave 2, falsify)

**Verdict: holds.** The committed tool at `fa3b62ae6475d111eb466d79af616aeebb08bbb9`
reproduces the committed C2 receipt exactly on every value the claim names:
all 14 cells, per-slot value, slot count, KV pool and request outcome are
identical across three independent full runs, and the committed counter prints
`registered 14 observed 14 bound True missing []` on each replicated receipt.
One caveat is recorded below: the counter checks the *shape* of a receipt, not
its truth, so `observed 14` is not by itself evidence that the numbers were
measured (another wave seat owns that instrument question).

## What I ran

Clone of the lane at the tip under test, per the wave contract:

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
  /fast/scratch/hyaku/kama-r25a2w2/ReplicateReceipt/clone
git -C /fast/scratch/hyaku/kama-r25a2w2/ReplicateReceipt/clone \
  checkout fa3b62ae6475d111eb466d79af616aeebb08bbb9
```

Committed bytes used (sha256, identical to the tip blobs):

- `tools/kama-context-capacity.py` → `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27`
  (same value as the `tool.sha256` recorded inside the committed receipt)
- `.ufo/waves/round-25/count-c2.py` → `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d`

Fixture: `~/.local/opt/llama-b11755/llama-server` (sha256
`b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`) and
`~/.cache/kama-shokunin/models/stories260K.gguf` (sha256
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`).
`server_version` read by the tool: `version: 0.7.0-dev (build 11755, commit 704366d76)`.

Five runs of the committed tool, each one child at a time on 127.0.0.1 inside
the assigned range 47400-47419 (ports 47400-47413 actually used; the tool
refuses 8080 and 34113 and I never probed them):

| run | command | started / ended (UTC) | tool exit |
|---|---|---|---|
| r1 | `python3 tools/kama-context-capacity.py --out …/receipt.json --scratch …/logs` | 10:08:42.651 → 10:08:50.712 | 0 |
| r2 | same, `--out …/receipt2.json` | 10:11:02.724 → 10:11:10.833 | 0 |
| r3 | same, `--out …/run3/receipt.json` (own raw dir) | 10:11:35.138 → 10:11:51.302 | 0 |
| r4 | `… --only L1,L2,L3 --out …/run4/receipt.json` | 10:25:04.368 → 10:25:06.469 | 0 |
| r5 | `… --only L1,L2,L3 --out …/run5/receipt.json` | 10:25:06.517 → 10:25:08.653 | 0 |

Every run: `cells_drift []`, `error None`, `all_ports_closed true`,
`observed 14 of 14` (r4/r5: 3 of 3). After the runs, `ss -ltn` shows no
listener on 47400-47419 and `pgrep -a llama-server` shows no process.

## Counter output (committed counter bytes)

```
$ python3 .ufo/waves/round-25/count-c2.py receipt.json          # r1
registered 14 observed 14 bound True missing []          exit 0
$ python3 .ufo/waves/round-25/count-c2.py receipt2.json         # r2
registered 14 observed 14 bound True missing []          exit 0
$ python3 .ufo/waves/round-25/count-c2.py run3/receipt.json     # r3
registered 14 observed 14 bound True missing []          exit 0
$ python3 .ufo/waves/round-25/count-c2.py <committed receipt at tip>
registered 14 observed 14 bound True missing []          exit 0
```

The committed receipt at the tip is byte-identical to the one committed at
`5c95c8f111a981e316cd4933e38fc363e51f8604` (sha256
`78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c`), and the
committed counter scores the earlier `5ea4fc44e1d0b5236e14e8b4881f446626a56682`
receipt `registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']`,
which matches what amendment 4 recorded for that receipt.

## Per-cell comparison table

Full machine-readable table: `out/ReplicateReceipt/cell-comparison.tsv`
(committed vs r1 vs r2 vs r3, one row per cell per field).
Raw-hash table: `out/ReplicateReceipt/raw-hash-comparison.tsv`.
Condensed view (committed value in parentheses; every run equals it):

| cell | args | /props n_ctx (per slot) | total_slots | every /slots n_ctx | KV pool (log) | /v1/models meta.n_ctx_train | mode | request outcomes |
|---|---|---|---|---|---|---|---|---|
| K1 | `-c 0` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 2048 (2048) | 2048 (2048) | – | – |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 (1024) | 2 (2) | [1024,1024] | 2048 (2048) | 2048 (2048) | – | – |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 (2048) | 2 (2) | [2048,2048] | 2048 (2048) | 2048 (2048) | – | – |
| K4 | `-c 1024 -np 1` | 1024 (1024) | 1 (1) | [1024] | 1024 (1024) | 2048 (2048) | – | – |
| K5 | `-c 4096 -np 1` | 2048 (2048) | 1 (1) | [2048] | 4096 (4096) | 2048 (2048) | – | – |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 (512) | 3 (3) | [512,512,512] | 1536 (1536) | 2048 (2048) | – | – |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 (512) | 2 (2) | [512,512] | 1024 (1024) | 2048 (2048) | – | – |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 (512) | 4 (4) | [512,512,512,512] | 4096 (4096) | 2048 (2048) | – | – |
| X1 | `-np 4 --no-kv-unified` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 8192 (8192) | 2048 (2048) | – | – |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 8192 (8192) | 2048 (2048) | – | – |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 (512) | 4 (4) | [512,512,512,512] | 2048 (2048) | 2048 (2048) | – | – |
| L1 | `-c 0` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 2048 (2048) | 2048 (2048) | concurrent | both HTTP 500, `server_error`, `Context size has been exceeded.` (both requests) |
| L2 | `-c 8192 -np 4 --no-kv-unified` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 8192 (8192) | 2048 (2048) | concurrent | both HTTP 200, 600 tokens each, not truncated |
| L3 | `-c 0` | 2048 (2048) | 4 (4) | [2048,2048,2048,2048] | 2048 (2048) | 2048 (2048) | sequential | both HTTP 200, 600 tokens each, not truncated |

**Differing cells: none.** Every field above is byte-equal across the
committed receipt and all three replicated receipts. `args`, `props_n_ctx`,
`total_slots`, `slots_n_ctx`, `kv_pool_n_ctx`, `models_n_ctx_train`,
`request_mode` and the request outcomes agree on 14 of 14 cells.

Also equal across committed and replicated: `kv_pool_candidates` per cell
(X1 = `[2048, 8192, 8192]`, all others two identical entries), the per-cell
`server_sha256` and `model_sha256`, the receipt-level `server.sha256`,
`model_sha256` and `tool.sha256`, `port_refusal_set` = `[8080, 34113]`, and
`teardown` for every cell (`port_closed true`, `child_returncode 0`).

## Independent cross-checks of the committed receipt (not just counter agreement)

Both the committed receipt and the replicated receipt were checked against the
raw bytes they point at (the committed raw files read from the tip blob, the
replicated ones from my own `raw/` directory):

- **Every recorded raw sha256 matches the file it names**: 0 mismatches of 70
  for the committed receipt, 0 of 70 for the replicated receipt.
- **Every `log_lines` entry is a verbatim line of that cell's raw server log**,
  and the last `llama_context: n_ctx = N` line equals the recorded
  `kv_pool_n_ctx`: 0 problems in 14 cells, both receipts.
- **The startup line agrees with the recorded slot layout**
  (`n_slots = N, n_ctx_slot = M, kv_unified = …`): 0 problems, both receipts.
- **`/slots` body per-slot `n_ctx` equals the recorded `slots_n_ctx`, one entry
  per `total_slots`**: 0 problems, both receipts.
- **`/props` `default_generation_settings.n_ctx` equals `props_n_ctx`,
  `total_slots` equals the recorded count, `/v1/models` `data[0].meta.n_ctx`
  equals `props_n_ctx` and `meta.n_ctx_train` equals `models_n_ctx_train`**: 0
  problems, both receipts.

So the committed receipt is internally consistent with its own raw evidence,
not merely acceptable to the counter.

## Reproducible findings (the claims the entry makes about this receipt)

- K1 and X2 report identical endpoint values with pools 2048 and 8192 — true
  in my runs as well (both receipts).
- L1 both requests fail with `Context size has been exceeded.`, L2 and L3 both
  succeed with 600 tokens — reproduced in r1, r2, r3 and again in the two
  load-only runs r4 and r5 (5 of 5 runs: L1 500/500, L2 200/200, L3 200/200).
- The L1 log shows the fit-independent failure at `n_tokens = 1025` for both
  slots in every run. The committed entry cites `final/raw/L1.server.log`
  lines 1849-1866; in my runs the same events land on lines 1848-1865 (r3),
  1849-1866 (r4), 1850-1867 (r5) — the citation is a property of the
  committed log file, not a stable line number across runs. The X1 citations
  (pool lines 283 / 812 / 1344, `load_model: initializing` line 1610) did
  reproduce exactly in r3.
- The X1 fit probe is visible in every run: the first `llama_context: n_ctx`
  line is 2048, the last is 8192, in both the committed log and mine.

## Differences that are expected, and are not cell differences

42 of the 70 raw sha256 values differ between the committed receipt and any
replicated receipt. The differing keys are exactly `raw_models` (14 cells),
`raw_props` (14) and `server_log` (14); `raw_health` and `raw_slots` are
byte-identical in all 14 cells. The causes are per-run non-determinism, and I
checked each:

- `/v1/models` differs only in `data[0].created` (unix time of the run).
- `/props` differs only in `media_marker` (a random token the server mints per
  start).
- the server log differs only in timestamps, in two `sched_reserve: reserve
  took X ms` durations and in the order in which the two L1 task ids are
  released (task 2 then 3 in the committed log and in r4; task 3 then 2 in r3).

None of these touch a value the receipt claims.

## One defect found (in the counter's acceptance set, not in the receipt)

The committed counter checks the shape of a receipt, not that its numbers were
measured. Mutating my replicated receipt and re-running the committed counter
gives `registered 14 observed 14 bound True missing []` for all of these:

- per-cell `props_n_ctx`, `slots_n_ctx[i]`, `models_n_ctx_train` altered to
  other plausible values;
- per-cell `raw` sha256 values zeroed, or the whole `raw` map emptied;
- per-cell `server_sha256` zeroed; receipt-level `server.sha256` zeroed;
- receipt `exit_code` set to 1; receipt `cells_drift` set to `["x"]`;
- a cell's `teardown.port_closed` set to false; a cell's `observed` set to false;
- an extra unregistered cell `Z9` appended; `kv_pool_candidates` emptied;
- L1's two requests flipped to HTTP 200 with 600 tokens each (the opposite of
  the observed failure) and L2's two requests flipped to HTTP 500;
- `argv` `--port` changed to 47999, or `-m` pointed at another model, with the
  cell's recorded `port` left unchanged.

The counter does reject: a wrong `kv_pool_n_ctx` (X1 → 2048), a wrong
`total_slots`, an `argv` that loses a launch flag or the registered args
suffix, an edited pool line (2048 → 12048), emptied `log_lines`, a fake L3
request overlap, a wrong build string (`build 117550`), and a wrong per-cell
`model_sha256` or `server_version`. Full probe transcript:
`out/ReplicateReceipt/counter-probes.txt`.

Reading: this does not falsify C2. The counter counts *recorded* cells; a
receipt whose L1 shows success is a legitimate (prediction-falsifying)
observation, so accepting it is by design. But it does mean the published
string `registered 14 observed 14 bound True missing []` cannot, by itself,
certify that the numbers in the receipt were measured. The evidence that they
were measured is the receipt plus its 70 raw files, which I checked directly
and found consistent (see above). Seat `KamaR25a2.RerunC2Counter` is
independently running the same instrument battery; I have not proposed a
counter change (not my lane's write scope).

## Files I wrote

Lane (allowed paths only):

- `.ufo/waves/round-25/a2-falsify/advice/ReplicateReceipt.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/cell-comparison.tsv`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/raw-hash-comparison.tsv`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/counter-outputs.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/counter-probes.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replicated-vs-committed-cells.json`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/run-manifest.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/receipt.json`
  and `replication-run3/raw/` (70 raw files of the third full run)

Scratch (heavy, not in the lane): `/fast/scratch/hyaku/kama-r25a2w2/ReplicateReceipt/`
(clone, receipts r1/r2/r3/r4/r5, logs, clobber test).

No production file was modified: no lane source, no receipt, no counter, no
SCORECARD, no entry. No tool was installed or upgraded (the run needed only
the lane's existing `llama-server` build 11755 and Python 3.14.8).

## Risks and limits

- The fixture, the server build and the model are the lane's round-16
  fixture; nothing here says anything about the registered consumers or about
  other builds. The registered consumers were not probed.
- The replicas ran on the same host minutes apart; they show the receipt is
  reproducible here, not that it is reproducible on other hardware.
- I did not run the round-24 mutant battery or any C1 instrument; C1 is
  another seat's ground.
- Line numbers quoted from raw logs are properties of one log file; only the
  values themselves are stable across runs.
