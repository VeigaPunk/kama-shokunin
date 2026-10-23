## Round-28 request-field outcomes

Decision table of what llama-server b11755 does with an out-of-range or
transformed value of one request field, one row per field with its declaring
line in tools/server/server-schema.cpp @704366d.

| id | field | value | outcome | meaning | source |
|---|---|---|---|---|---|
| F28-01 | n_cache_reuse | -1 | reject 400, bounds 0 to 2147483647 | Out of range below zero is rejected with hard bounds | S940 |
| F28-02 | xtc_threshold | 1.5 | 200, xtc_threshold = 1.0 | Value above the soft limit is clamped down to one | S941 |
| F28-10 | top_k | -1 | reject 400, bounds 0 to 2147483647 | Cited line is the set_desc line not the declaration | S942 |
| F28-11 | min_p | 2.0 | reject 400, bounds 0 to 1 | Cited line is the set_limits line not the declaration | S943 |
| F28-12 | top_p | 2.0 | reject 400, bounds 0 to 1 | Cited line declares a different field entirely here | S944 |
| F28-13 | top_n_sigma | -1 | reject 400, bounds 0 to 2147483647 | Cited line is off by one from declaration | S945 |
| F28-14 | n_predict | -1 | reject 400, bounds 0 to 2147483647 | Sources row names L440 containing the L44 substring | S946 |
| F28-15 | n_keep | -1 | reject 400, bounds 0 to 2147483647 | Sources row names the wrong commit not 704366d | S947 |
| F28-16 | n_discard | -1 | reject 400, bounds 0 to 2147483647 | Cites a file other than server-schema.cpp instead | S948 |
| F28-17 | noise n_indent noise | junk 7 junk | prefix 200, n_indent = 123456 suffix | every needed token is wrapped inside longer junk text | ref S949 here |
| F28-18 | repeat_last_n | -1 | reject 400, bounds 0 to 2147483647 | One sources row cited by many registry rows here | S950 |
| F28-19 | repeat_last_n | 3 | 200, repeat_last_n = 99 | One sources row cited by many registry rows again | S950 |

---

### Second-table / heading-prefix variant (used only in receipt-skill-ordering.json)

This decoy was inserted *before* the real section above to probe the
"second SKILL table before the real one" and "heading prefix" tricks. Its
heading also starts with the frozen `## Round-28 request-field outcomes`
prefix, and its table has a 5-column (wrong) header, which poisons the
counter's single global `header_ok` flag so the real table's rows are never
collected. Result: counted dropped to 0 (every row `a:no-skill-row`).

```
## Round-28 request-field outcomes (draft — ignore this one)

| id | field | value | outcome | source |
|---|---|---|---|---|
| F28-01 | n_cache_reuse | -1 | reject 400, bounds 0 to 2147483647 | S940 |
| F28-02 | xtc_threshold | 1.5 | 200, xtc_threshold = 1.0 | S941 |
```
