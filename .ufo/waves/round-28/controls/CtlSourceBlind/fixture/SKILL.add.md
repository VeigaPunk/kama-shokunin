
## Round-28 request-field outcomes

| id | field | value | outcome | meaning | source |
| --- | --- | --- | --- | --- | --- |
| F28-00 | sse_ping_interval | -5 | reject 400, bounds -1 to 2147483647 | Blind guess from field name and public README only | S8000 |
| F28-01 | n_predict | -5 | reject 400, bounds -1 to 2147483647 | Blind guess from field name and public README only | S8001 |
| F28-02 | n_indent | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8002 |
| F28-03 | n_keep | -5 | reject 400, bounds -1 to 2147483647 | Blind guess from field name and public README only | S8003 |
| F28-04 | n_discard | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8004 |
| F28-05 | n_cmpl | -5 | reject 400, bounds 1 to 2147483647 | Blind guess from field name and public README only | S8005 |
| F28-06 | t_max_prompt_ms | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8006 |
| F28-07 | t_max_predict_ms | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8007 |
| F28-08 | top_k | -5 | 200, top_k = 0 | Blind guess from field name and public README only | S8008 |
| F28-09 | top_p | 1.5 | 200, top_p = 1.0 | Blind guess from field name and public README only | S8009 |
| F28-10 | min_p | -0.5 | 200, min_p = 0.0 | Blind guess from field name and public README only | S8010 |
| F28-11 | xtc_probability | 1.5 | 200, xtc_probability = 1.0 | Blind guess from field name and public README only | S8011 |
| F28-12 | typical_p | -0.5 | 200, typical_p = 0.0 | Blind guess from field name and public README only | S8012 |
| F28-13 | temperature | -0.5 | 200, temperature = 0.0 | Blind guess from field name and public README only | S8013 |
| F28-14 | dynatemp_range | -0.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 | Blind guess from field name and public README only | S8014 |
| F28-15 | dynatemp_exponent | -0.5 | 200, dynatemp_exponent = 0.0 | Blind guess from field name and public README only | S8015 |
| F28-16 | repeat_last_n | -5 | 200, repeat_last_n = -1 | Blind guess from field name and public README only | S8016 |
| F28-17 | repeat_penalty | -0.5 | 200, repeat_penalty = 0.0 | Blind guess from field name and public README only | S8017 |
| F28-18 | frequency_penalty | 5.0 | 200, frequency_penalty = 2.0 | Blind guess from field name and public README only | S8018 |
| F28-19 | presence_penalty | 5.0 | 200, presence_penalty = 2.0 | Blind guess from field name and public README only | S8019 |
| F28-20 | dry_multiplier | -0.5 | reject 400, bounds 0.0 to 3.4028234663852886e+38 | Blind guess from field name and public README only | S8020 |
| F28-21 | dry_base | -0.5 | 200, dry_base = 1.0 | Blind guess from field name and public README only | S8021 |
| F28-22 | dry_allowed_length | -5 | 200, dry_allowed_length = 0 | Blind guess from field name and public README only | S8022 |
| F28-23 | dry_penalty_last_n | -5 | 200, dry_penalty_last_n = -1 | Blind guess from field name and public README only | S8023 |
| F28-24 | mirostat | 5 | 200, mirostat = 2 | Blind guess from field name and public README only | S8024 |
| F28-25 | mirostat_tau | -0.5 | 200, mirostat_tau = 0.0 | Blind guess from field name and public README only | S8025 |
| F28-26 | mirostat_eta | -0.5 | 200, mirostat_eta = 0.0 | Blind guess from field name and public README only | S8026 |
| F28-27 | adaptive_target | 1.5 | 200, adaptive_target = 1.0 | Blind guess from field name and public README only | S8027 |
| F28-28 | adaptive_decay | 1.5 | 200, adaptive_decay = 0.99 | Blind guess from field name and public README only | S8028 |
| F28-29 | n_probs | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8029 |
| F28-30 | min_keep | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8030 |
| F28-31 | speculative.n_max | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8031 |
| F28-32 | speculative.n_min | -5 | reject 400, bounds 0 to 2147483647 | Blind guess from field name and public README only | S8032 |
| F28-33 | speculative.p_min | 1.5 | 200, speculative.p_min = 1.0 | Blind guess from field name and public README only | S8033 |
| F28-34 | speculative.ngram_size_n | -5 | reject 400, bounds 1 to 2147483647 | Blind guess from field name and public README only | S8034 |
| F28-35 | speculative.ngram_size_m | -5 | reject 400, bounds 1 to 2147483647 | Blind guess from field name and public README only | S8035 |
| F28-36 | speculative.ngram_min_hits | -5 | reject 400, bounds 1 to 2147483647 | Blind guess from field name and public README only | S8036 |
| F28-37 | reasoning_budget_tokens | -5 | reject 400, bounds -1 to 2147483647 | Blind guess from field name and public README only | S8037 |
