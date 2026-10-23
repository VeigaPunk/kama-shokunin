
## Round-28 request-field outcomes (CONTROL fixture: duplicate-field fishing, guessed outcomes)

| id | field | value | outcome | meaning | source |
| --- | --- | --- | --- | --- | --- |
| F28-01 | `n_predict` | `-2` | reject 400, bounds -1 to 2147483647 | guessed fishing outcome for this request field, never run live | S901 |
| F28-02 | `n_predict` | `-2` | reject 400, bounds 0 to 2147483647 | guessed fishing outcome for this request field, never run live | S902 |
| F28-03 | `n_predict` | `-2` | 200, n_predict = -1 | guessed fishing outcome for this request field, never run live | S903 |
| F28-04 | `n_predict` | `0` | 200, n_predict = -1 | guessed fishing outcome for this request field, never run live | S904 |
| F28-05 | `top_k` | `-5` | 200, top_k = 0 | guessed fishing outcome for this request field, never run live | S905 |
| F28-06 | `top_k` | `-5` | 200, top_k = 40 | guessed fishing outcome for this request field, never run live | S906 |
| F28-07 | `top_k` | `100000` | reject 400, bounds -1 to 2147483647 | guessed fishing outcome for this request field, never run live | S907 |
| F28-08 | `max_tokens` | `-5` | reject 400, bounds -1 to 2147483647 | guessed fishing outcome for this request field, never run live | S908 |
| F28-09 | `max_completion_tokens` | `-5` | 200, n_predict = -1 | guessed fishing outcome for this request field, never run live | S909 |
| F28-10 | `n` | `0` | reject 400, bounds 1 to 2147483647 | guessed fishing outcome for this request field, never run live | S910 |
| F28-11 | `n_cmpl` | `0` | reject 400, bounds 1 to 2147483647 | guessed fishing outcome for this request field, never run live | S911 |
| F28-12 | `max_tokens` | `0` | 200, n_predict = -1 | guessed fishing outcome for this request field, never run live | S912 |
| F28-13 | `n_probs` | `{"logprobs": 5}` | 200, n_probs = 5 | guessed fishing outcome for this request field, never run live | S913 |
| F28-14 | `speculative.n_max` | `-1` | reject 400, bounds 0 to 2147483647 | guessed fishing outcome for this request field, never run live | S914 |
| F28-15 | `speculative` | `{"n_max": -1}` | 200, speculative.n_max = 0 | guessed fishing outcome for this request field, never run live | S915 |
| F28-16 | `speculative.n_max` | `{"speculative": {"n_max": -1}}` | reject 400, bounds 0 to 2147483647 | guessed fishing outcome for this request field, never run live | S916 |
| F28-17 | `speculative.n_min` | `-1` | reject 400, bounds 0 to 2147483647 | guessed fishing outcome for this request field, never run live | S917 |
| F28-18 | `speculative.p_min` | `{"speculative": {"p_min": 2}}` | reject 400, bounds 0 to 1 | guessed fishing outcome for this request field, never run live | S918 |
| F28-19 | `temperature` | `-1` | 200, temperature = 0 | guessed fishing outcome for this request field, never run live | S919 |
| F28-20 | `temperature` | `-1` | 200, temperature = 0 | guessed fishing outcome for this request field, never run live | S920 |
| F28-21 | `top_p` | `{"min_p": 2, "top_p": 2}` | reject 400, bounds 0 to 1 | guessed fishing outcome for this request field, never run live | S921 |
| F28-22 | `min_p` | `2` | reject 400, bounds 0 to 1 | guessed fishing outcome for this request field, never run live | S922 |
| F28-23 | `Mirostat` | `7` | reject 400, bounds 0 to 2 | guessed fishing outcome for this request field, never run live | S923 |
| F28-24 | `dry_base ` | `0.5` | reject 400, bounds 1 to 3.4028234663852886e+38 | guessed fishing outcome for this request field, never run live | S924 |
| F28-25 | `repeat_penalty` | `-1` | reject 400, bounds 0 to 2 | guessed fishing outcome for this request field, never run live | S925 |
| F28-25 | `presence_penalty` | `5` | reject 400, bounds -2 to 2 | guessed fishing outcome for this request field, never run live | S926 |
