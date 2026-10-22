# MutationCounterA4 — synthetic receipt probe results

Counter bytes: sha256 `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d` (committed fa3b62a, equals working tree).
Baseline receipt sha256 `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c`.

Baseline control run: `registered 14 observed 14 bound True missing []` (exit 0). Restoration: counter hash unchanged, receipt hash unchanged, baseline reproduced = True.

## All probes (31 non-control)

| # | mutation | counter output | exit | still counts? |
|---|---|---|---|---|
| P01_overlap_equal_times_L2 | L2: request[1] t_start/t_end copied from request[0] (equal times) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P02_overlap_equal_times_L1 | L1: request[1] t_start/t_end copied from request[0] (equal times) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P03_equal_start_only_L2 | L2: request[1] t_start equal to request[0] t_start, t_end kept | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P04_equal_times_sequential_L3 | L3 (sequential cell): equal times on both requests | `registered 14 observed 13 bound True missing ['L3']` | 0 | no |
| P05_tstart_after_tend_L2 | L2: request[0] t_start = t_end + 1.0 (start after end) | `registered 14 observed 13 bound True missing ['L2']` | 0 | no |
| P06_tstart_after_tend_L1 | L1: request[1] t_end = t_start - 1.0 (start after end) | `registered 14 observed 13 bound True missing ['L1']` | 0 | no |
| P07_log_from_other_cell_K1 | K1: log_lines replaced by K2's log lines (foreign cell log) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P08_log_foreign_slot_line_K2 | K2: n_slots startup line replaced by K1's line (foreign log line) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P09_argv_extra_after_args_K1 | K1: argv gains --no-warmup AFTER the registered args | `registered 14 observed 13 bound True missing ['K1']` | 0 | no |
| P10_argv_extra_before_args_K1 | K1: argv gains --no-context-shift BEFORE the registered args | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P11_argv_extra_before_args_K2 | K2: argv gains --swa-full --no-mmap BEFORE the registered args | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P12_total_slots_vs_n_slots_log_K1 | K1: log says n_slots = 1, n_ctx_slot = 1024 but receipt claims total_slots 4 / slots_n_ctx [2048 x4] | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P13_nctx_slot_mismatch_K2 | K2: log n_ctx_slot = 2048 but slots_n_ctx says 1024 | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P14_l2_status200_tokens_predicted_12 | L2: both requests status 200 with tokens_predicted = 12 (below 600) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P15_l2_status200_tokens_predicted_null | L2: both requests status 200 with tokens_predicted = null | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P16_l2_status200_truncated_true | L2: both requests status 200 with truncated = true | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P17_l2_status200_with_error_body | L2: both requests status 200 but carry a server error body | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P18_l2_elapsed_vs_times_inconsistent | L2: t_end stretched to t_start+100 while elapsed_s stays 0.174 (overlap faked, elapsed ignored) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P19_l2_status_599 | L2: HTTP status 599 (in range 100-599) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P20_l2_status_600 | L2: HTTP status 600 (out of range) | `registered 14 observed 13 bound True missing ['L2']` | 0 | no |
| P21_receipt_cells_drift_nonempty | receipt-level cells_drift lists K1, L2, L3 (drift never read by the counter) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P22_observed_false_everywhere | every cell carries observed = false | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P23_model_path_swapped_K1 | K1: argv -m points at a different model file (model path never checked) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P24_L1_both_requests_status_200 | L1: both requests status 200, no error (concurrency limit did not fire) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P25_control_foreign_log_K4_pool_mismatch | CONTROL K4: log_lines replaced by K1's log (pool 2048 vs K4 kv_pool 1024) | `registered 14 observed 13 bound True missing ['K4']` | 0 | no |
| P26_stretch_L3_sequential_to_overlap | L3: t_end stretched to t_start+100 so the intervals overlap (mode still sequential) | `registered 14 observed 13 bound True missing ['L3']` | 0 | no |
| P27_L2_fabricated_overlap_elapsed_from_L3 | L2: overlapping t_start/t_end fabricated, elapsed_s taken from the real sequential L3 run | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P29_port_collision_K1_K2 | K1 and K2 report the same port (47401); one server cannot serve both cells | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P30_slot_line_removed_K2 | K2: the n_slots startup line is removed from the log | `registered 14 observed 13 bound True missing ['K2']` | 0 | no |
| P31_L2_sequential_records_faked_overlap | L2: requests replaced by L3's real sequential records; request[1].t_start set equal to request[0].t_start (faked overlap, elapsed_s kept) | `registered 14 observed 14 bound True missing []` | 0 | YES |
| P32_control_L2_sequential_records_verbatim | CONTROL L2: requests replaced by L3's real sequential records verbatim (no overlap) | `registered 14 observed 13 bound True missing ['L2']` | 0 | no |
