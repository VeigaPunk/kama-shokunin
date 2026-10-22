# ExecLoadReplicate per-run table (C2 L1-L3 replicate)

| cell | rep | port | mode | /props n_ctx | slots | /v1/models n_ctx_train | kv pool (log) | req | HTTP status | error text | tokens_predicted | finished_reason | timing predicted_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 1 | 47420 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 500 | 'Context size has been exceeded.' | None | None | None |
| L1 | 1 | 47420 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 500 | 'Context size has been exceeded.' | None | None | None |
| L1 | 2 | 47421 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 500 | 'Context size has been exceeded.' | None | None | None |
| L1 | 2 | 47421 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 500 | 'Context size has been exceeded.' | None | None | None |
| L1 | 3 | 47422 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 500 | 'Context size has been exceeded.' | None | None | None |
| L1 | 3 | 47422 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 500 | 'Context size has been exceeded.' | None | None | None |
| L2 | 1 | 47423 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 0 | 200 | '' | 600 | None | 182.168 |
| L2 | 1 | 47423 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 1 | 200 | '' | 600 | None | 182.203 |
| L2 | 2 | 47424 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 0 | 200 | '' | 600 | None | 184.843 |
| L2 | 2 | 47424 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 1 | 200 | '' | 600 | None | 184.792 |
| L2 | 3 | 47425 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 0 | 200 | '' | 600 | None | 189.363 |
| L2 | 3 | 47425 | concurrent | 2048 | [2048, 2048, 2048, 2048] | 2048 | 8192 | 1 | 200 | '' | 600 | None | 189.395 |
| L3 | 1 | 47426 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 200 | '' | 600 | None | 122.13 |
| L3 | 1 | 47426 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 200 | '' | 600 | None | 122.663 |
| L3 | 2 | 47427 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 200 | '' | 600 | None | 117.96 |
| L3 | 2 | 47427 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 200 | '' | 600 | None | 119.83 |
| L3 | 3 | 47428 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 0 | 200 | '' | 600 | None | 117.136 |
| L3 | 3 | 47428 | sequential | 2048 | [2048, 2048, 2048, 2048] | 2048 | 2048 | 1 | 200 | '' | 600 | None | 122.985 |
