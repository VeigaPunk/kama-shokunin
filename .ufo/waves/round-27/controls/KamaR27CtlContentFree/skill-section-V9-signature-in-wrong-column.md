
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | see below | POST /v1/chat/completions rejected: 'messages' is required | the server refused this request body | add a messages array to the chat request body | S990 |
| E27-91 | see below | POST /completion rejected: "prompt" must not be empty | the server refused this request body | send at least one prompt string or token | S991 |
