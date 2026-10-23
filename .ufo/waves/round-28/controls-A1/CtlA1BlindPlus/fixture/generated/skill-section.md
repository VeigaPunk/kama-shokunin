## Round-28 request-field outcomes

Control fixture CtlA1BlindPlus. Every row is a pre-scoring guess, not an observation: the sent value, the outcome and any bounds were fixed from the public b11755 server README, the declaration names and general programming knowledge, without running llama-server and without reading the schema body.

| id | field | value | outcome | meaning | source |
|---|---|---|---|---|---|
| F28-01 | top_p | `2.5` | `200, top_p = 1.0` | probability clamp to one, guessed from the README default and unit range | S701 |
| F28-02 | min_p | `2.5` | `200, min_p = 1.0` | probability clamp to one, guessed from the README default and unit range | S702 |
| F28-03 | xtc_probability | `2.5` | `200, xtc_probability = 1.0` | probability clamp to one, guessed from the README default and unit range | S703 |
| F28-04 | typical_p | `-1.5` | `200, typical_p = 0.0` | probability clamp to zero, guessed from the README disabled value one | S704 |
| F28-05 | temperature | `-1.5` | `200, temperature = 0.0` | invalid negative temperature guessed to clamp up to zero | S705 |
| F28-06 | dynatemp_exponent | `-1.5` | `200, dynatemp_exponent = 0.0` | invalid negative exponent guessed to clamp up to zero | S706 |
| F28-07 | mirostat_tau | `-1.5` | `200, mirostat_tau = 0.0` | invalid negative entropy target guessed to clamp up to zero | S707 |
| F28-08 | mirostat_eta | `-1.5` | `200, mirostat_eta = 0.0` | invalid negative learning rate guessed to clamp up to zero | S708 |
| F28-09 | repeat_penalty | `-1.5` | `200, repeat_penalty = 0.0` | invalid negative repetition penalty guessed to clamp up to zero | S709 |
| F28-10 | dry_base | `-1.5` | `200, dry_base = 1.0` | invalid base below one guessed to clamp up to one | S710 |
| F28-11 | adaptive_target | `2.5` | `200, adaptive_target = 1.0` | unknown adaptive field guessed to clamp to the unit bound | S711 |
| F28-12 | adaptive_decay | `2.5` | `200, adaptive_decay = 1.0` | unknown adaptive field guessed to clamp to the unit bound | S712 |
| F28-13 | mirostat | `5` | `200, mirostat = 2` | documented three state selector guessed to clamp to state two | S713 |
| F28-14 | top_k | `-5` | `200, top_k = 0` | count field guessed to clamp up to zero when negative | S714 |
| F28-15 | n_keep | `-5` | `200, n_keep = -1` | sentinel count field guessed to clamp up to minus one | S715 |
| F28-16 | n_discard | `-5` | `200, n_discard = -1` | sentinel count field guessed to clamp up to minus one | S716 |
| F28-17 | n_predict | `-5` | `200, n_predict = -1` | sentinel prediction limit guessed to clamp up to minus one | S717 |
| F28-18 | repeat_last_n | `-5` | `200, repeat_last_n = -1` | sentinel window size guessed to clamp up to minus one | S718 |
| F28-19 | dry_allowed_length | `-5` | `200, dry_allowed_length = 0` | small count guessed to clamp up to zero when negative | S719 |
| F28-20 | dry_penalty_last_n | `-5` | `200, dry_penalty_last_n = -1` | sentinel window size guessed to clamp up to minus one | S720 |
| F28-21 | min_keep | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative count guessed to reject below zero with int32 bounds | S721 |
| F28-22 | n_indent | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative count guessed to reject below zero with int32 bounds | S722 |
| F28-23 | n_probs | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative count guessed to reject below zero with int32 bounds | S723 |
| F28-24 | t_max_prompt_ms | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative millisecond limit guessed to reject below zero with int32 bounds | S724 |
| F28-25 | t_max_predict_ms | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative millisecond limit guessed to reject below zero with int32 bounds | S725 |
| F28-26 | reasoning_budget_tokens | `-5` | `reject 400, bounds 0 to 2147483647` | nonnegative token budget guessed to reject below zero with int32 bounds | S726 |
| F28-27 | seed | `4294967296` | `reject 400, bounds 0 to 4294967295` | unsigned seed guessed to reject one past the uint32 maximum | S727 |
| F28-28 | n_cmpl | `0` | `reject 400, bounds 1 to 2147483647` | positive completion count guessed to reject zero with unit minimum | S728 |
| F28-29 | sse_ping_interval | `-5` | `reject 400, bounds -1 to 2147483647` | interval with disabled sentinel guessed to reject below minus one | S729 |
| F28-30 | stop | `"zqx"` | `200, stop = ["zqx"]` | string stop word guessed to be wrapped into a one element list | S730 |
| F28-31 | dry_sequence_breakers | `"zqx"` | `200, dry_sequence_breakers = ["zqx"]` | string breaker guessed to be wrapped into a one element list | S731 |
| F28-32 | samplers | `"top_k"` | `200, samplers = ["top_k"]` | string sampler name guessed to be wrapped into a one element list | S732 |
| F28-33 | reasoning_format | `"AUTO"` | `200, reasoning_format = "auto"` | uppercase enum value guessed to be normalised to lowercase | S733 |
| F28-34 | dynatemp_range | `-1.5` | `reject 400, bounds 0.0 to 3.4028234663852886e+38` | nonnegative range guessed to reject below zero at float maximum | S734 |
| F28-35 | frequency_penalty | `-1.5` | `reject 400, bounds 0.0 to 3.4028234663852886e+38` | nonnegative penalty guessed to reject below zero at float maximum | S735 |
| F28-36 | presence_penalty | `-1.5` | `reject 400, bounds 0.0 to 3.4028234663852886e+38` | nonnegative penalty guessed to reject below zero at float maximum | S736 |
| F28-37 | dry_multiplier | `-1.5` | `reject 400, bounds 0.0 to 3.4028234663852886e+38` | nonnegative multiplier guessed to reject below zero at float maximum | S737 |
| F28-38 | top_n_sigma | `-5.0` | `reject 400, bounds -1.0 to 3.4028234663852886e+38` | minus one floor guessed to reject below minus one at float maximum | S738 |
