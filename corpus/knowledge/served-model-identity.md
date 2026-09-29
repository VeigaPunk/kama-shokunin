

### Exact readiness-field probes

Because the combined endpoint command emits large bodies, these additional commands select only the reported fields; their outputs are exact for those commands.

Command:

```sh
for p in health props slots; do echo "=== /$p ==="; curl --max-time 5 -sS http://127.0.0.1:34113/$p | jq -c 'if .status then {status} elif .default_generation_settings then {default_generation_settings:{params:{chat_format:.default_generation_settings.params.chat_format,reasoning_format:.default_generation_settings.params.reasoning_format}}} elif type=="array" then . else . end'; done
```

Output:

```text
=== /health ===
{"status":"ok"}
=== /props ===
{"default_generation_settings":{"params":{"chat_format":"Content-only","reasoning_format":"none"}}}
=== /slots ===
[{"id":0,"n_ctx":16384,"is_processing":false},{"id":1,"n_ctx":16384,"is_processing":false}]
```

Command:

```sh
curl --max-time 5 -sS http://127.0.0.1:34113/metrics | grep -E '^(llamacpp:(requests_processing|requests_deferred|prompt_tokens_total|tokens_predicted_total) )'
```

Output:

```text
llamacpp:prompt_tokens_total 360853
llamacpp:tokens_predicted_total 259802
llamacpp:requests_processing 0
llamacpp:requests_deferred 0
```
