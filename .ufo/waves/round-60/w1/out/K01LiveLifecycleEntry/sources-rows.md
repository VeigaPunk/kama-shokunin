# SOURCES rows the round-60 knowledge entry requires (draft for integration)

Not edited into `corpus/SOURCES.md` by this seat (lane tree is read-only for the
drafting seat). Column order and cell style follow the registry header at
`corpus/SOURCES.md` (id | source | kind | tier | scope | anchor | teaches |
status | opened | recheck | used-by). Ids: `S519` was re-derived as the next
free id (`grep -cE '^\| S[0-9]{3}' corpus/SOURCES.md` → 259 rows, highest `S518`;
`grep -c 'S519' corpus/SOURCES.md` → 0). L1 may re-assign at integration; if it
does, the knowledge entry's `source:` line must be updated to match.

```
| S519 | Ollama v0.40.11 release — https://github.com/ollama/ollama/releases/tag/v0.40.11 | docs | A | the pinned server release's asset identities for the lane's live Ollama harness | tag v0.40.11; asset `ollama-linux-amd64.tar.zst` (1508659610 bytes) and the release's `sha256sum.txt`, `./ollama-linux-amd64.tar.zst` line; opened 2026-10-27 | The archive digest is published upstream (`7bedab90…4b6d`); no per-member digest for `bin/ollama` is published, so a binary pin rests on the archive plus this host's extraction. | mined | 2026-10-27 | on-release | tools/kama-ollama-live.py, registry/ollama-live-pin.tsv, corpus/knowledge/ollama-live-lifecycle.md |
| S520 | Ollama FAQ — https://docs.ollama.com/faq | docs | A | Ollama server environment configuration: bind host/port, model store location, cloud disable, model keep-alive and default context | §How do I configure Ollama server?, §How can I expose Ollama on my network? (binds 127.0.0.1:11434 by default; `OLLAMA_HOST`), §Where are models stored? (`OLLAMA_MODELS`), §How do I disable Ollama's cloud features? (`OLLAMA_NO_CLOUD=1`), §How do I keep a model loaded in memory or make it unload immediately? (5 minutes), §How can I specify the context window size? (4096 tokens); page undated, fetched 2026-10-27 | Which environment variable moves the bind address, the model store and the cloud switch; the 5-minute keep-alive and 4096-token context are documented defaults, not observed runner values. | mined | 2026-10-27 | 90d | tools/kama-ollama-live.py, corpus/knowledge/ollama-live-lifecycle.md |
| S521 | Ollama Importing a Model — https://docs.ollama.com/import | docs | A | the single-file GGUF import recipe the lane harness uses (a scope extension of S013's quantization statement) | §Importing a GGUF model — `FROM /path/to/file.gguf` in a Modelfile then `ollama create <name>`; page undated, fetched 2026-10-27 | extends S013 — a single-file GGUF is imported by a Modelfile whose `FROM` names the file plus an `ollama create`; the page describes neither the store's blob layout nor the digest the model reports afterwards. | mined | 2026-10-27 | on-release | corpus/knowledge/ollama-live-lifecycle.md |
| S522 | Ollama OpenAI compatibility — https://docs.ollama.com/api/openai-compatibility | docs | A | the `/v1/models` and `/v1/models/{model}` Notes fields only (a scope extension of S010's endpoint inventory) | §/v1/models Notes and §/v1/models/{model} Notes — `created` corresponds to when the model was last modified; `owned_by` corresponds to the ollama username, defaulting to `library`; page undated, fetched 2026-10-27 | extends S010 — the meaning of those two fields, and nothing about the empty list body form or about the tag suffix of a single-route id. | mined | 2026-10-27 | on-release | corpus/knowledge/ollama-live-lifecycle.md |
| S523 | kama round-60 live Ollama lifecycle — `tools/kama-ollama-live.py`, `tools/kama-ollama-evidence.py`, `registry/ollama-live-pin.tsv`, `tools/round60-c1-counter.py`, `.ufo/waves/round-60/live/receipt.json` | own-work | A | one CPU run of the pinned Ollama release on the lane fixture GGUF, its captured HTTP surfaces and their offline replay | receipt sha256 `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6`, lane commit `8b9f3060966c22bede3094d748974caf041b4c33`, nonce `b61c98ad5747`, port 58921, 2026-10-27; counter re-run exit 0 at lane tip `11f2d667f8bd89d127a4fb81dab44007c4c86c7f` | The observed shapes: `data: null` on an empty `/v1/models`; qualified list id versus unqualified single-route id; equal `/api/tags` and `/api/ps` digests after one generate; `size` 1185492 on tags versus 6312427 on ps for one digest; `parent_model` present on tags and empty on ps; `expires_at` minus `created_at` 300.000423 s. | mined | 2026-10-27 | every round — `python3 tools/round60-c1-counter.py --repo <repo> --tip <rev>` | tools/round60-c1-counter.py, corpus/knowledge/ollama-live-lifecycle.md |
```

Notes for the integration step:

- S521 and S522 sit on pages already carried by S013 and S010. Each states a
  distinct `scope`, which `SOURCES.md`'s contract scopes tiers to; neither
  supersedes the earlier row and no earlier cell changes.
- S519's `used-by` names `registry/ollama-live-pin.tsv`; S520's names the
  harness that sets those variables; S523's names the counter that re-runs it.
- `status` `mined` matches the rows opened in rounds 56–58.
