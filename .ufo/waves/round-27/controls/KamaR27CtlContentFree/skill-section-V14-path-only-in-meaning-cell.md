
## Round-27 request-validation signatures

| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | no path here | the endpoint /v1/chat/completions refused this request body | add a messages array to the chat request body | S990 |
| E27-91 | `"prompt" must not be empty` | no path here | the endpoint /completion refused this request body | send at least one prompt string or token | S991 |
