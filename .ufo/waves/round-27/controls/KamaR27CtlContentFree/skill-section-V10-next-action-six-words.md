
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | x | y | /v1/chat/completions | Fix the request and retry it | S990 |
| E27-91 | `"prompt" must not be empty` | x | y | /completion | Fix the bad request and retry | S991 |
