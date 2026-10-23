
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | POST /v1/chat/completions without messages | S990 |
| E27-91 | `"prompt" must not be empty` | POST /completion with empty prompt list | S991 |
