
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | POST /v1/chat/completions without messages | the server refused this request body | retry once fixed | /v1/chat/completions | aaaa bbbb cccc dddd eeee ffff | S990 |
| E27-91 | `"prompt" must not be empty` | POST /completion with empty prompt list | the server refused this request body | retry once fixed | /completion | aaaa bbbb cccc dddd eeee gggg | S991 |
