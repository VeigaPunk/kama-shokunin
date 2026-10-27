# S02OllamaServerEnv — Round 60 w1 (frontier sources)

Row S520 drafted for the Ollama FAQ (bind address + model store selection); gate record and both fetched
source snapshots accompany it. No lane source touched, no commit, no server started (not needed for this item).

- **Opened, per Rule 1:** live `https://docs.ollama.com/faq` (markdown alternate `.md`, sha256 799c4f08…) and the
  tag-pinned `docs/faq.mdx` @ v0.40.11, blob 9e42f77d…, sha256 e3630684…, 413 lines. Access date 2026-10-27.
- **Path discrepancy reported, not smoothed:** the item names `docs/faq.md`; at v0.40.11 that path is HTTP 404 —
  the repository file is `docs/faq.mdx`. Both openable locations were read and agree verbatim on both quotes
  (tag 185/241, live 186/242), so the row cites the live URL and anchors to the tag.
- **Q1** §"How can I expose Ollama on my network?": "Ollama binds 127.0.0.1 port 11434 by default. Change the bind
  address with the `OLLAMA_HOST` environment variable." (16 words)
- **Q2** §"Where are models stored?" → "How do I set them to a different location?": "If a different directory needs
  to be used, set the environment variable `OLLAMA_MODELS` to the chosen directory." (18 words)
- **Tier A scoped only** to "which env vars select bind address and model store" — first-party docs anchored at the
  release tag of the installed binary; page is undated prose, recheck `on-release`.
- **Duplicate check:** `grep -c "docs\.ollama\.com/faq" corpus/SOURCES.md` → 0; `grep -c "OLLAMA_HOST"` → 0;
  `grep -c "OLLAMA_MODELS"` → 0. No within-scope duplicate. S009 (`/api/introduction`) is adjacent (route root
  `localhost:11434`) and named no configuration variable — not superseded.
- **Id:** max in use S518, S519 free, seat-directed id **S520** used. Row validated at exactly 11 columns, no `|` in cells.
- **Not claimed by the page, so not by the row:** precedence between these vars and a config file (only
  `~/.ollama/server.json` → `disable_ollama_cloud` appears), systemd enforcement of the default bind, routes/health.
- Files: `row.md`, `gate.md`, `faq-v0.40.11.mdx`, `faq-live-faq.md`, `hashes.txt` in this directory.
