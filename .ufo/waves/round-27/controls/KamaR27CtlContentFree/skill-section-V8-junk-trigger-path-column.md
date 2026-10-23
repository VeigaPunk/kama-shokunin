
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | x | y | /v1/chat/completions | add a messages array to the chat request body | S990 |
| E27-91 | `"prompt" must not be empty` | x | y | /completion | send at least one prompt string or token | S991 |
