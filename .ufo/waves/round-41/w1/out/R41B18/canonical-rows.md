# R41B18 extra artifacts — capability repertoire audit (round 41)

Extraction of canonical capability tables from SCORECARD.md at tip
24aa1d3485c107f88b8b838892d43ea7587befcf, using a parser replicating
tools/capability-repertoire-audit.py (tables()/is_capability_table()/
first table after the named "canonical list as of round N" marker).

## r34 canonical table (marker line 1915, table start line 1922, 6 rows)
1. sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10
2. ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14
3. live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16
4. gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20
5. context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25
6. instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30

## r41 canonical table (marker line 2172, table start line 2176, 7 rows)
Rows 1-6 byte-identical to r34 rows 1-6 (verified True).
7. pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41

## Tool runs
- tip 24aa1d3485c107f88b8b838892d43ea7587befcf:
  `listed 7 observed 7 missing 0 unsubstantiated 0 met True` (exit 0)
- base 8893b89466250c4d542912a867392698d2da00ce:
  `listed 6 observed 6 missing 0 unsubstantiated 0 met True` (exit 0)
- Evidence path resolution at tip (git cat-file -e rc 0 for each):
  tools/pin-watch.py, registry/engine-pins.tsv, corpus/knowledge/engine-pin-watch.md
