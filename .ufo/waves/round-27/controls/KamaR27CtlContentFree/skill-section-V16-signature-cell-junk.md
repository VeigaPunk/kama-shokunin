
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` (server validation) | POST /v1/chat/completions without messages | the server refused this request body | add a messages array to the chat request body | S990 |
| E27-91 | `"prompt" must not be empty` (server validation) | POST /completion with empty prompt list | the server refused this request body | send at least one prompt string or token | S991 |
