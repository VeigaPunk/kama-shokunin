# Round70 primary-source reread, 2026-11-03

The author reopened both immutable URLs with recheck-sources.py, fetched bytes into memory only, checked exact source anchors and recorded metadata/short quotations in source-recheck.json. No full source capture is retained. Script execution exit0; exact source hashes match the preparation pins.

- vLLM model.py, served_model_name docstring lines235–242: API-visible serving names are configurable aliases, including multiple accepted names and one response label. The advertised string is therefore not by itself the identity of loaded checkpoint bytes. This source does not define our strict synthetic grammar or normalization policy.
- llama.cpp tools/server/README.md, direct server GET /v1/models lines1346–1350: model information can be returned while its metadata is null during loading. Inventory is not a readiness witness. The direct-server statement is not generalized to router inventories.

Own synthesis: keep exact parsed-name membership, historical lossy comparison compatibility, loaded-weight identity, process ownership and readiness as separate propositions. Legacy basename/suffix comparison is retained as historical compatibility, never silently promoted into exact membership. Exact names can coexist with normalization collisions; all names must be validated before any success is emitted.

Novelty is executable evidence calibration under finite bounds, not discovery of the lane's already-held alias/readiness distinctions. Offline fixtures and a green evaluator cannot prove any live endpoint serves any weights. No registered consumer was contacted.
