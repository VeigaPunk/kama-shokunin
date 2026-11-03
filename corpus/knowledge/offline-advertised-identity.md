source: corpus/SOURCES.md S542 (vLLM served_model_name), S543 (llama.cpp direct-server GET /v1/models); tools/kama-offline-identity.py and .ufo/waves/round-70/result/RECOVERED-AUDIT.json
verified-at: 2026-11-03 source reading and independently re-adjudicated first isolated batch
recheck: .ufo/waves/round-70/author/recheck-sources.py for pinned source anchors; independently isolated round70 evaluator for the exact candidate revision

# Evidence ladder for an advertised model name

A configured model identifier is a claim to reconcile, not proof of the backend's weights. vLLM allows explicit API aliases; llama.cpp's direct-server inventory may expose null metadata during model loading. Therefore a successful name comparison and a successful inference-readiness check answer different questions.

## Decision table for the bounded offline projection

| Observation | Warranted conclusion | Next authorized work |
|---|---|---|
| Valid complete inventory contains the exact parsed expected string | That name is advertised in this supplied projection | Preserve exact spelling and provenance; separately obtain an authorized current readiness observation if the task needs it |
| Only path basename or .gguf suffix normalization matches | Legacy comparison compatibility only | Report the raw colliding names; ask the configuration owner to reconcile the intended alias; do not silently repoint |
| Exact name plus another normalized collision | Exact membership holds, ambiguity exists for legacy matching | Keep the exact candidate and collision list separate; never select the first normalized model |
| No exact or legacy-compatible name | No advertised match in the supplied valid projection | Verify capture/config provenance before claiming a current outage |
| Malformed, duplicate, empty or overlimit evidence | Evidence is invalid or insufficient under local policy | Obtain a valid explicit projection; never turn refusal into mismatch or readiness |

The strict input is a synthetic projection, not a full vLLM/llama.cpp API response. It cannot discard unknown fields on the user's behalf. Real captures need a separately reviewed, provenance-preserving projection process. No capture acquisition is implemented.

## Working checklist

1. Identify the exact expected API name, without basename conversion, case folding, Unicode normalization or trimming.
2. Preserve input provenance separately. This classifier does not authenticate a source or establish freshness.
3. Execute only in the approved fixture-only isolation and resource envelope; Python -I alone is not isolation.
4. Read both JSON status and process exit. Invocation/runtime failure is not a domain verdict.
5. Inspect all normalization collisions, even when exact membership exists.
6. Keep readiness, weight identity, runtime ownership and live observation explicitly not established.
7. Escalate credentials to kagi, model-quality judgments to kengaku and dispatch machinery to kumitate; stay within serving-side identity reconciliation.

## Failure patterns

- A ready health response does not identify the served alias, and an alias does not prove health.
- Early success before validating later entries hides malformed or duplicate inventory.
- Raw JSON byte comparison mistakes different escape spellings for different strings.
- Unicode normalization invents equivalence the source contract did not grant.
- A path/suffix collision can be historically compatible without being the exact advertised identifier.
- Green synthetic cases are not live endpoint verification or loaded-weight provenance.

This operationalization does not claim discovery of already-held alias/readiness principles. It narrows how a finite offline tool is allowed to express evidence.
