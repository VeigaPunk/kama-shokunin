# M05 — base line 141 -> live Ollama evidence (round 60, w1)

Files (only my out dir): `.ufo/waves/round-60/w1/out/M05MapOllamaevidence141/rows.tsv` (3 rows, no header) and `.../notes.md`.
Line mapped: `corpus/knowledge/ollama-evidence-replay.md:141` = `### Matching and policy — all **[INFERENCE]** lane rules`; the section (base 143-176) cites no S0xx row, so its statements are the eight numbered rules.
`OL05a` confirmed (quote `Matching and policy`): tags holds one entry with `name == model == kama-b61c98ad5747:latest` and a 64-hex digest; the server appended `:latest` to the bare nonce name, so rule 1's no-normalization matching runs on equal plain strings.
`OL05b` confirmed (quote `all **[INFERENCE]** lane rules`): pre-generation ps body is literally `{"models": []}` while tags selects — the exact `available_not_loaded` shape of rule 8, live.
`OL05c` not-observable (quote `policy — all **[INFERENCE]** lane rules`): rule precedence lives in the lane's classifier; the captures carry one entry per surface, no duplicates, no remote markers, so no captured body can order the rules.
Evidence: committed receipt only, hashes re-verified; `importlib` load of `tools/round60-c2-counter.py` -> `receipt_caps ok=True`, both predicates `evaluate=True` and `falsifiable=True`, `score` on my rows -> `rows=3 covered=1 evaluated=2 sensitive=2/2 bound=2 contradicted=0 errors=0 good_rows=3 receipt_ok=1`. No fresh live run was needed, so no lane-owned server and no scratch receipt were created; `/fast/scratch/hyaku/kama-r60/M05MapOllamaevidence141` removed.
Caveat handed to the L1, not a claim: the same model reads `kama-...:latest` on `/api/tags` and `/v1/models` but bare `kama-...` on `/v1/models/{model}`, so rule 1 makes the single-model id unusable as `--expect` — correct as written, costly in practice, no amendment requested.
Risks: no contradicted row came out of this line, so it contributes no amendment text; the population line is a heading, so every row quotes a heading fragment while testing a rule beneath it.
No edits to lane source, registry, SOURCES, SKILL.md or any other seat's files; no git/jj mutation, no tool installs.
