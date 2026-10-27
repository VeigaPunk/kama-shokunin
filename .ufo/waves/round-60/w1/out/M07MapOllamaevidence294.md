# M07 — round 60 w1 (line 294, C2 calibration, advisory leaf)
Mapped frozen population line corpus/knowledge/ollama-evidence-replay.md:294 ("S012/S031; every classification rule is labeled **[INFERENCE]** lane policy", second line of KQ6) to the committed live Ollama receipt.
Files: .ufo/waves/round-60/w1/out/M07MapOllamaevidence294/{rows.tsv,notes.md,check.txt,second-look-receipt.json}; lane source untouched, no commit/push/jj, no installs.
OL07A "S012/S031; every classification rule is labeled" — confirmed: ps-after has ≥1 model and every model carries name,model,digest,context_length,size_vram,expires_at, i.e. the /api/ps field set credited to S012 is what v0.40.11 emits.
OL07B "S012/S031; every classification rule is labeled **[INFERENCE]** lane policy" — confirmed: every tags model carries name,model,digest (S031 ModelSummary); remote_model/remote_host are optional and deliberately not asserted here (that is OL06's line).
OL07C "every classification rule is labeled **[INFERENCE]** lane policy" — not-observable (empty predicate, 185-char reason): the labelling policy is about the lane's own docs/classifier; no capture body or receipt field records rule labels.
Evidence (exact): importlib of tools/round60-c2-counter.py → receipt_caps(committed receipt)=True; quotes are exact substrings of the base line (6/9/8 words); safe_compile+evaluate=True+falsifiable=True for OL07A and OL07B; score() on these rows only →
population=14 rows=3 covered=1 evaluated=2 eval_lines=1 sensitive=2/2 bound=2 contradicted=0 amended=0/0 receipt_ok=True good_rows=3 errors=0 met=False (met false only because the other 13 lines are other seats').
Second look: own lane-owned child via tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json → exit 0, verdict MODEL_OK, nonce 9f0726f01d0f, port 44075; identical ps/tags key sets, both predicates True/True; receipt copied as second-look-receipt.json.
Scratch /fast/scratch/hyaku/kama-r60/M07MapOllamaevidence294 removed. No contradicted row → no amendment paragraph proposed.
Risk: both confirms are field-exposure on one version and one fixture model, so a reviewer may prefer "fields published by v0.40.11" over "S012's OpenAPI says so"; the not-observable row is not credited as evaluated (counter rule).
Advisory only (not written): SOURCES S012/S031 already exist at lines 24/43; the frontier step's next free id is S519.
