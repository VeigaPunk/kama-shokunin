# MutationCounterA4 — C2 amendment-4 counter falsification probe


Verdict: defect found. The committed counter (count-c2.py at fa3b62ae6475d111eb466d79af616aeebb08bbb9, sha256 7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d) accepts synthetic receipts it should reject: 22 of 31 new probes still score `registered 14 observed 14 bound True missing []`. The registered acceptance rule is narrower than the amendment-4 docstring claims.

## Method

Every synthetic receipt is the committed receipt `context-capacity-receipt.json` (sha256 78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c) with one surgical mutation. The detector is the committed counter bytes run as `python3 counter_pristine.py <receipt>` (60 s timeout). Sequence: pristine baseline → 31 mutants → pristine restore. All runs exit 0 with empty stderr. Baseline and restored output identical: `registered 14 observed 14 bound True missing []`; counter bytes unmodified (hash stable). Full outputs, exit codes and per-receipt sha256 in `results.json`.

## Results table (assigned attacks)

| Probe | Mutation | Counter output | Still counts |
|---|---|---|---|
| P01 | L2: request[1] t_start/t_end copied from request[0] (equal times) | `observed 14 bound True missing []` | YES |
| P02 | L1: request[1] t_start/t_end copied from request[0] | `observed 14 bound True missing []` | YES |
| P03 | L2: request[1] t_start equal to request[0] t_start | `observed 14 bound True missing []` | YES |
| P04 | L3 (sequential): equal times on both requests | `observed 13 missing ['L3']` | no |
| P05 | L2: request[0] t_start = t_end + 1.0 | `observed 13 missing ['L2']` | no |
| P06 | L1: request[1] t_end = t_start - 1.0 | `observed 13 missing ['L1']` | no |
| P07 | K1: log_lines replaced by K2's log lines (foreign cell log) | `observed 14 bound True missing []` | YES |
| P08 | K2: n_slots startup line replaced by K1's line (foreign log line) | `observed 14 bound True missing []` | YES |
| P09 | K1: argv gains --no-warmup AFTER the registered args | `observed 13 missing ['K1']` | no |
| P10 | K1: argv gains --no-context-shift BEFORE the registered args | `observed 14 bound True missing []` | YES |
| P11 | K2: argv gains --swa-full --no-mmap BEFORE the registered args | `observed 14 bound True missing []` | YES |
| P12 | K1: log says n_slots = 1, n_ctx_slot = 1024 but receipt claims total_slots 4 / slots_n_ctx [2048 x4] | `observed 14 bound True missing []` | YES |
| P13 | K2: log n_ctx_slot = 2048 but slots_n_ctx says 1024 | `observed 14 bound True missing []` | YES |
| P14 | L2: both requests status 200 with tokens_predicted = 12 | `observed 14 bound True missing []` | YES |
| P15 | L2: both requests status 200 with tokens_predicted = null | `observed 14 bound True missing []` | YES |
| P16 | L2: both requests status 200 with truncated = true | `observed 14 bound True missing []` | YES |
| P17 | L2: both requests status 200 but carry a server error body | `observed 14 bound True missing []` | YES |
| P18 | L2: t_end stretched to t_start+100 while elapsed_s stays 0.174 | `observed 14 bound True missing []` | YES |
| P19 | L2: HTTP status 599 (in range 100-599 per registered rule) | `observed 14 bound True missing []` | per rule |
| P20 | L2: HTTP status 600 (out of range) | `observed 13 missing ['L2']` | no |
| P21 | receipt-level cells_drift lists K1, L2, L3 | `observed 14 bound True missing []` | YES |
| P22 | every cell carries observed = false | `observed 14 bound True missing []` | YES |
| P23 | K1: argv -m points at a different model file | `observed 14 bound True missing []` | YES |
| P24 | L1: both requests status 200, no error | `observed 14 bound True missing []` | YES |
| P25 control | K4: log_lines replaced by K1's log (pool 2048 vs K4 kv_pool 1024) | `observed 13 missing ['K4']` | no |
| P27 | L2: fabricated overlap times, elapsed_s from real sequential L3 | `observed 14 bound True missing []` | YES |
| P28 | L2: request[1] byte-for-byte duplicate of request[0] | `observed 14 bound True missing []` | YES |
| P29 | K1 and K2 report the same port (47401) | `observed 14 bound True missing []` | YES |
| P30 | K2: n_slots startup line removed | `observed 13 missing ['K2']` | no |
| P31 | L2: real L3 sequential records with faked equal-start overlap | `observed 14 bound True missing []` | YES |
| P32 control | L2: real L3 sequential records verbatim (no overlap) | `observed 13 missing ['L2']` | no |

## False counts per assigned attack

1. **Overlap faked with equal times — FALSE COUNT.** The overlap test (count-c2.py:109) is `overlap = max(q["t_start"]) < min(q["t_end"])`, satisfied by copying one request's times onto the other (P01/P02/P03/P28) or by editing only t_start/t_end while leaving the recorded `elapsed_s` witness contradictory (P18, P27, P31: real sequential records relabelled concurrent via equal t_start). The counter never reads `elapsed_s`, so the time evidence is self-asserted; a receipt can claim L1/L2 concurrency that the run never had. Control P32/P26 show the check only bites when the times do not overlap at all.
2. **t_start greater than t_end — correctly rejected** (P05/P06 kill the cell; no false count).
3. **A log line from another cell — FALSE COUNT.** P07 (whole foreign log) and P08 (foreign n_slots startup line) still score 14/14. The SLOT regex (count-c2.py:53) only requires *some* line to match; the captured n_slots/n_ctx_slot/kv_unified values are never compared to the cell's total_slots, slots_n_ctx, or kv_unified. The only cross-field binding is the pool line (count-c2.py:87-89), so two cells with the same pool (K1/K2/K3) accept each other's logs (control P25 rejects only because K4's pool differs).
4. **Argy with extra flags — partially FALSE COUNT.** The registered "argv ends with the registered args" rule (count-c2.py:80) rejects flags appended *after* the args (P09). But flags inserted *before* the args pass undetected (P10/P11), and the model path itself is never checked (P23). The launch rule in preregistration-amendment-2.json says cells launch exactly `llama-server -m <model> --host 127.0.0.1 --port <free> --no-webui --offline -v <args>`; an extra flag there changes what was served.
5. **total_slots mismatching the n_slots log line — FALSE COUNT.** P12 (log says n_slots=1, n_ctx_slot=1024 against claimed total_slots=4, slots [2048x4]) and P13 (n_ctx_slot mismatch) both score 14/14. The counter never ties the log's n_slots to total_slots nor n_ctx_slot to slots_n_ctx.
6. **status 200 with tokens_predicted below 600 in L2 — FALSE COUNT.** P14 (tokens_predicted=12), P15 (null), P16 (truncated=true), P17 (error body with status 200) all score 14/14. The counter checks the *requested* n_predict (1000/600) but never the *actual* `tokens_predicted`, `truncated`, `error`, or `error_type` that the tool records (kama-context-capacity.py:525-549). A load cell claiming "both complete with HTTP 200" can carry zero completed tokens and still count.

## Additional findings

- P19: status 599 counts. This is exactly the amendment-4 rule ("HTTP status 100-599"), so it is per-contract, not a false count; note 599 is not a real HTTP status.
- P21: the receipt's own `cells_drift` field is never read by the counter; a receipt announcing drift still scores 14/14.
- P22: the `observed` flag is ignored (wave-1 already reported this shape; confirmed).
- P24: L1 counts with both requests at status 200, although the registered L1 cell exists to observe the context-size concurrency error; the counter does not consult the registered prediction (prediction grading is intentionally not the claim value, but the receipt can contradict the cell's purpose and still count).

## Smallest correction

Tighten the received cell_ok/load checks so the accepted set is what the docstring claims: read the captured SLOT groups and require `n_slots == total_slots`, `n_ctx_slot == slots_n_ctx[i]`, and `kv_unified` consistent with the cell; require `argv` to equal exactly the launch prefix plus the registered args (and that `-m` points at the model path the receipt declares); require `tokens_predicted == 600` (not null, not truncated) for a status-200 load request; and cross-check `elapsed_s` against `t_end - t_start` so fabricated overlap is detectable. Each change shrinks the accepted set (none would reject the committed receipt, which passes all of them).

## Restoration evidence

Counter bytes sha256 before and after all runs: 7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d (unchanged). Receipt bytes sha256 before/after: 78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c (unchanged). Baseline output reproduced exactly after the last mutant (restoration.baseline_reproduced=True). No lane production file was modified; artifacts only under the seat out-dir.
