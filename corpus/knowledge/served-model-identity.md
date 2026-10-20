

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

## Provenance supplement — round 11 (2026-10-19)
source: retained historical sample — `corpus/lessons/round-1.md:3-4` states the round-1 observation date and points to the command-bearing corpus; `corpus/knowledge/listener-census.md:3` supplies the 2026-09-28 approximately 22:47–22:52 -0300 window. This fragment's original bytes are retained in `c6199a2`; no external source or new runtime sample is claimed.
verified-at: original samples 2026-09-28; metadata review 2026-10-20 only. No endpoint contacted or live revalidation claimed. Samples targeted the then-live 127.0.0.1:34113 llama.cpp server. `registry/history/DELTA.md:9-14` and `LOG.md:245-246` record October dead-endpoint observations; the deleted registry row at DELTA line 20 does not establish permanent server retirement. None of those host states was re-observed in round 11.
recheck: on authorized revalidation — `bash tools/kama-probe.sh check; echo "CHECK_EXIT=$?"` (read-only registered-row reconciliation; exit 0/2/1; `SKILL.md` §Checklist item 1); do not replay the 34113 samples above as current — re-probe readiness fields only against an operator-authorized serving base URL.

Scope note: the retained bytes above are the readiness/metrics field fragment (health, props, slots, metrics), not the served-id reconciliation procedure.
