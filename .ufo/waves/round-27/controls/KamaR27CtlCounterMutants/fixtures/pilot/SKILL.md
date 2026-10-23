## Round-27 request-validation signatures

| id | signature | trigger | next action | source |
| --- | --- | --- | --- | --- |
| E27-90 | `'messages' is required` | POST /v1/chat/completions with the registered body | add a messages array to the chat request body | S990 |
| E27-91 | `"prompt" must not be empty` | POST /completion with the registered body | supply at least one prompt before retrying completion | S991 |
