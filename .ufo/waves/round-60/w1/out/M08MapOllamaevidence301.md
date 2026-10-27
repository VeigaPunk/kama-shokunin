# M08MapOllamaevidence301 — round-60 w1, claim C2 line mapping

Attacked claim: C2-r60 row coverage of base line `corpus/knowledge/ollama-evidence-replay.md:301` (QUALITY KQ13, "- KQ13: available inventory, loaded residency, advertised identity and inference").
Files: `.ufo/waves/round-60/w1/out/M08MapOllamaevidence301/rows.tsv` (3 rows OL08a/b/c), `.../notes.md`, `.../live-repeat-r.json`. No lane source, registry or amendment file touched; scratch removed.
OL08a confirmed — tags=1 model, ps-before=[] , ps-after=1 model; `len(c['tags']['models']) == 1 and c['ps-before']['models'] == [] and len(c['ps-after']['models']) == 1` → eval True, falsifiable True (chains tags/ps-before/ps-after `models`).
OL08b confirmed — tags[0].name = v1-models.data[0].id = kama-b61c98ad5747:latest, generate done=true response " upon a time," , ps-before empty → eval True, falsifiable True.
OL08c not-observable — KQ13's four-dimension separation is a lane-classifier rule; no capture body records the emitted finding (reason 171 chars, empty predicate).
Validation: `python3` via importlib on `tools/round60-c2-counter.py`: `receipt_caps` → `caps_ok True keys [...10]`; per row `words 4/4/6`, `quote_on_line True`, `eval True/True`, `falsifiable True/True`, reason_len 171 — exit 0.
Second look: `python3 tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json` (own HOME, OLLAMA_NO_CLOUD=1, CPU-only, own port 37909) → TOOL_EXIT=0, verdict MODEL_OK, elapsed 1.46 s, teardown port_closed true, all 10 capture sha256 verified; same shape (tags=1, ps-before=[], ps-after=1, generate done=true).
No contradicted row: neither the committed receipt nor the repeat contradicts line 301, so no amendment paragraph is offered (`observed` cells are still exact text, pasteable if the lane wants to cite them).
Adjacent, not a row: `/v1/models/{model}` returns id `kama-b61c98ad5747` (tag stripped) while `/v1/models` lists `…:latest`; `ps-after.details.parent_model` is "" vs `stories260K.gguf` in tags — differences inside the identity dimension, not a conflation.
No installed or upgraded tools; no pacman transaction; no port reuse; no sibling lane, fleet or jj/git mutation.
