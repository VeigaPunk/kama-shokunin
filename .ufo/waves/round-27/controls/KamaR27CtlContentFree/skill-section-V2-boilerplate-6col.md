
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | /v1/chat/completions | the request was rejected | Fix the request and then retry the call | S990 |
| E27-91 | `"prompt" must not be empty` | /completion | the request was rejected | Fix the request body and then retry the call | S991 |
