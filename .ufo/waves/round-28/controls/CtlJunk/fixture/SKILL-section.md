
## Round-28 request-field outcomes (CtlJunk control, fabricated)

| id | field | value | outcome | meaning | source |
|---|---|---|---|---|---|
| F28-01 | kv_spill_ratio | 15 | reject 400, bounds 0 to 8 | caps the share of cached keys the slot may spill (CtlJunk fabricated control row) | S140 |
| F28-02 | token_echo_window | 17 | 200, token_echo_window = 4 | sets how many recent tokens are echoed back before sampling (CtlJunk fabricated control row) | S141 |
| F28-03 | draft_temperature | 8 | reject 400, bounds 0 to 1 | limits how hot the draft model may sample on this request (CtlJunk fabricated control row) | S142 |
| F28-04 | prefix_lock_len | 3 | 200, prefix_lock_len = 4 | pins this many prefix tokens so they are never shifted out (CtlJunk fabricated control row) | S143 |
| F28-05 | sampler_jitter | 2 | reject 400, bounds 1 to 1 | adds bounded random noise to the sampler order per token (CtlJunk fabricated control row) | S144 |
| F28-06 | slot_affinity | 17 | 200, slot_affinity = 128 | binds the request to the slot that served its prefix earlier (CtlJunk fabricated control row) | S145 |
| F28-07 | penalty_horizon | 101 | reject 400, bounds 0.5 to 1 | caps the share of cached keys the slot may spill (CtlJunk fabricated control row) | S146 |
| F28-08 | logit_floor | 3 | 200, logit_floor = 4 | sets how many recent tokens are echoed back before sampling (CtlJunk fabricated control row) | S147 |
| F28-09 | beam_width | 101.0 | reject 400, bounds 0.5 to 100.0 | limits how hot the draft model may sample on this request (CtlJunk fabricated control row) | S148 |
| F28-10 | repeat_decay | 250 | 200, repeat_decay = 2.0 | pins this many prefix tokens so they are never shifted out (CtlJunk fabricated control row) | S149 |
| F28-11 | context_shift_step | 102.0 | reject 400, bounds 0.0 to 2.0 | adds bounded random noise to the sampler order per token (CtlJunk fabricated control row) | S150 |
| F28-12 | batch_hint | -2 | 200, batch_hint = 0 | binds the request to the slot that served its prefix earlier (CtlJunk fabricated control row) | S151 |
| F28-13 | nucleus_floor | 101 | reject 400, bounds 0.0 to 1 | caps the share of cached keys the slot may spill (CtlJunk fabricated control row) | S152 |
| F28-14 | entropy_cap | 250 | 200, entropy_cap = 0 | sets how many recent tokens are echoed back before sampling (CtlJunk fabricated control row) | S153 |
| F28-15 | cache_ttl_ms | 65635 | reject 400, bounds -1 to 65535 | limits how hot the draft model may sample on this request (CtlJunk fabricated control row) | S154 |
| F28-16 | warmup_tokens | 1.5 | 200, warmup_tokens = 0 | pins this many prefix tokens so they are never shifted out (CtlJunk fabricated control row) | S155 |
| F28-17 | stop_margin | 9 | reject 400, bounds 0.0 to 8 | adds bounded random noise to the sampler order per token (CtlJunk fabricated control row) | S156 |
| F28-18 | length_bias | 250 | 200, length_bias = 1 | binds the request to the slot that served its prefix earlier (CtlJunk fabricated control row) | S157 |
| F28-19 | burst_limit | 200.0 | reject 400, bounds 0.0 to 100.0 | caps the share of cached keys the slot may spill (CtlJunk fabricated control row) | S158 |
| F28-20 | softcap_scale | 0.9 | 200, softcap_scale = 0 | sets how many recent tokens are echoed back before sampling (CtlJunk fabricated control row) | S159 |
| F28-21 | prompt_trim | 108 | reject 400, bounds 0 to 8 | limits how hot the draft model may sample on this request (CtlJunk fabricated control row) | S160 |
| F28-22 | accept_ratio | 1.5 | 200, accept_ratio = 0 | pins this many prefix tokens so they are never shifted out (CtlJunk fabricated control row) | S161 |
| F28-23 | rope_nudge | 8 | reject 400, bounds 1 to 1 | adds bounded random noise to the sampler order per token (CtlJunk fabricated control row) | S162 |
| F28-24 | decode_quota | 250 | 200, decode_quota = 1 | binds the request to the slot that served its prefix earlier (CtlJunk fabricated control row) | S163 |
| F28-25 | vocab_mask_level | 107.0 | reject 400, bounds 0.5 to 100.0 | caps the share of cached keys the slot may spill (CtlJunk fabricated control row) | S164 |
| F28-26 | drift_penalty | 17 | 200, drift_penalty = 0 | sets how many recent tokens are echoed back before sampling (CtlJunk fabricated control row) | S165 |
| F28-27 | chunk_overlap | 164 | reject 400, bounds 0.5 to 64 | limits how hot the draft model may sample on this request (CtlJunk fabricated control row) | S166 |
| F28-28 | spec_lookahead | 0.9 | 200, spec_lookahead = 4 | pins this many prefix tokens so they are never shifted out (CtlJunk fabricated control row) | S167 |
| F28-29 | temp_floor | 65635 | reject 400, bounds 1 to 65535 | adds bounded random noise to the sampler order per token (CtlJunk fabricated control row) | S168 |
| F28-30 | sigma_clip | 0.9 | 200, sigma_clip = 0.25 | binds the request to the slot that served its prefix earlier (CtlJunk fabricated control row) | S169 |
