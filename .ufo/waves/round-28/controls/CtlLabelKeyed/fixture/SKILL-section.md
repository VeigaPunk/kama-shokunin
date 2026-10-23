
## Round-28 request-field outcomes (label-keyed control, scratch only)

| id | field | value | outcome | meaning | source |
|---|---|---|---|---|---|
| F28-01 | n_cache_reuse | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 renamed verbatim (value -1, bounds 0..2147483647) | S140 |
| F28-02 | xtc_threshold | 1.5 | 200, xtc_threshold = 1.0 | label-keyed control row, copied: pilot F28-91 renamed verbatim (value 1.5, effective 1.0) | S141 |
| F28-03 | n_keep | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S142 |
| F28-04 | n_discard | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S143 |
| F28-05 | n_probs | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S144 |
| F28-06 | min_keep | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S145 |
| F28-07 | dry_allowed_length | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S146 |
| F28-08 | dry_penalty_last_n | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S147 |
| F28-09 | repeat_last_n | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S148 |
| F28-10 | top_k | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S149 |
| F28-11 | mirostat | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S150 |
| F28-12 | n_indent | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S151 |
| F28-13 | n_cmpl | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S152 |
| F28-14 | t_max_predict_ms | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S153 |
| F28-15 | sse_ping_interval | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S154 |
| F28-16 | reasoning_budget_tokens | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S155 |
| F28-17 | speculative.n_max | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S156 |
| F28-18 | speculative.n_min | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S157 |
| F28-19 | top_p | 1.5 | 200, top_p = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S158 |
| F28-20 | min_p | 1.5 | 200, min_p = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S159 |
| F28-21 | typical_p | 1.5 | 200, typical_p = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S160 |
| F28-22 | xtc_probability | 1.5 | 200, xtc_probability = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S161 |
| F28-23 | adaptive_target | 1.5 | 200, adaptive_target = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S162 |
| F28-24 | speculative.p_min | 1.5 | 200, speculative.p_min = 1.0 | label-keyed control row, copied: pilot F28-91 value 1.5 and effective 1.0 reused for another float field | S163 |
| F28-25 | adaptive_decay | 1.5 | 200, adaptive_decay = 0.99 | label-keyed control row, copied: value from pilot F28-91; effective 0.99 copied from README --adaptive-decay 'valid range 0.0 to 0.99' | S164 |
| F28-26 | n_predict | 8192 | 200, n_predict = 2048 | label-keyed control row, copied: round-25 cell X1 KV pool 8192 sent; effective 2048 copied from round-25 per-slot n_ctx (K1) | S165 |
| F28-27 | seed | -1 | 200, seed = 4294967295 | label-keyed control row, copied: README --seed '-1, use random seed'; effective copied from round-26 base generation_settings.seed | S166 |
| F28-28 | temperature | -5 | 200, temperature = 0.800000011920929 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S167 |
| F28-29 | top_n_sigma | -5 | 200, top_n_sigma = -1.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S168 |
| F28-30 | dry_base | -5 | 200, dry_base = 1.75 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S169 |
| F28-31 | repeat_penalty | -5 | 200, repeat_penalty = 1.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S170 |
| F28-32 | frequency_penalty | -5 | 200, frequency_penalty = 0.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S171 |
| F28-33 | presence_penalty | -5 | 200, presence_penalty = 0.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S172 |
| F28-34 | mirostat_tau | -5 | 200, mirostat_tau = 5.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S173 |
| F28-35 | mirostat_eta | -5 | 200, mirostat_eta = 0.10000000149011612 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S174 |
| F28-36 | dynatemp_range | -5 | 200, dynatemp_range = 0.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S175 |
| F28-37 | dynatemp_exponent | -5 | 200, dynatemp_exponent = 1.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S176 |
| F28-38 | dry_multiplier | -5 | 200, dry_multiplier = 0.0 | label-keyed control row, copied: value -5 copied from E26-17 '--ctx-size -5'; effective copied from round-26 base generation_settings | S177 |
| F28-39 | speculative.ngram_size_n | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S178 |
| F28-40 | speculative.ngram_size_m | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S179 |
| F28-41 | speculative.ngram_min_hits | -1 | reject 400, bounds 0 to 2147483647 | label-keyed control row, copied: pilot F28-90 value -1 and bounds 0..2147483647 reused for another integer field | S180 |
