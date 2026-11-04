# SR02 — Ollama v0.40.11 surface reconnaissance (scout, read-only)

Seat: SR02ScoutOllama, kama round 80 wave 1. Read-only: no lane edit, no fixture, no subagent.
Observed 2026-11-04T10:35–10:44Z. Lane worktree tip at observation:
`fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` (base of record `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`;
siblings were writing untracked files during the run). Every upstream byte below was fetched at the
tag `v0.40.11`, not from master; the tag resolves upstream (`git ls-remote --tags` exit 0 →
`675150d6ad2747df1e218ef59de9194bc4a7e538	refs/tags/v0.40.11`).
Scratch `$S=/fast/scratch/hyaku/kama-r80/SR02ScoutOllama` was used for all fetches and removed before
yield; the fetch receipts are copied to `receipts.txt` beside this file.

Labels: **[OBS]** = read directly in the fetched bytes or command output; **[INF]** = inference from
those bytes; **[GAP]** = not established by this seat. Line numbers are 1-based in the named file at
the pinned tag.

## A. `GET /api/tags` vs `GET /api/ps` in the pinned release documentation

Fetch **[OBS]**: `curl -sS -o api_v0.40.11.md -w 'HTTP=%{http_code} BYTES=%{size_download}\n'
https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md` → exit 0, `HTTP=200
BYTES=54614`, sha256 `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5`,
1872 lines. Header banner (line 3): `> Note: Ollama's API docs are moving to
https://docs.ollama.com/api` — at this tag the GitHub file is the prose mirror; a SOURCES row must
name this URL, not docs.ollama.com.

| Endpoint | Heading (line) | Endpoint line | Description sentence (line) | Words |
|---|---|---|---|---|
| `GET /api/tags` | `## List Local Models` (1352) | 1355 | 1358: “List models that are available locally.” | 6 |
| `GET /api/ps` | `## List Running Models` (1763) | 1766 | 1769: “List models that are currently loaded into memory.” | 8 |

Both quotes are ≤25 words and are the entire description under each heading **[OBS]**; word counts
were computed with `python3 -c` over the exact lines.

What each lists, precisely **[OBS]** from the same file's request/response examples:

- `/api/tags` (section 1352–1406) returns one JSON object `{"models": [...]}`; each entry carries
  `name`, `model`, `modified_at`, `size`, `digest`, `details{parent_model, format, family, families,
  parameter_size, quantization_level}`. It has **no** `expires_at`, **no** `size_vram`, and no
  residency/readiness field: it is an inventory of models available to the server, not a statement
  that any is loaded. The file does not document the remote-entry markers (`remote_model`,
  `remote_host`: 0 hits in this file) — those exist only in the same tag's OpenAPI document (below)
  and in S031 for the docs.ollama.com surface.
- `/api/ps` (section 1763–1806) returns the same `{"models": [...]}` envelope; entries carry `name`,
  `model`, `size`, `digest`, `details{...}` plus `expires_at` (example line 1799) and `size_vram`
  (line 1800). It is the only one of the two that names a loaded state and an unload time.
- Hence: **tags = on-disk inventory available locally; ps = models currently resident in memory with
  an expiry.** A tags hit is not evidence of loading; a ps hit is a time-bounded observation. **[INF]**
  This is the exact split a census may lean on: `/api/tags` membership is the "engine serves the
  fixture model" check, and it is not a loaded-state or readiness claim.

Same-tag machine spec cross-check **[OBS]**: `curl …/docs/openapi.yaml` → exit 0, `HTTP=200
BYTES=87348`, sha256 `e94c8f02969c6807f431b7d0643eb0f8368f1d1baa719a4edaf07989b758f257`, OpenAPI
3.1.0, `info.version 0.1.0`.

- `/api/tags` at line 1669 (operationId `list`, 200 description “List available models”);
  `/api/ps` at 1704 (operationId `ps`, 200 description “Models currently loaded into memory”).
- `ModelSummary` 654–699 includes `remote_model` (664, “Name of the upstream model, if the model is
  remote”) and `remote_host` (667); `Ps` 728–752 includes `expires_at` (“Time when the model will be
  unloaded”), `size_vram`, `context_length`.
- `'/v1/models'` occurs **0** times in this spec; the only `/v1/*` path declared is `/v1/systemone`
  (line 1189). The spec is therefore not a source for the OpenAI-compatible routes.

## B. Is an OpenAI-compatible `/v1/models` documented at the pinned tag? — **Yes**

Exact path opened **[OBS]**: `docs/api/openai-compatibility.mdx` in `ollama/ollama` at tag `v0.40.11`
(`https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`) →
exit 0, `HTTP=200 BYTES=25472`, sha256
`44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5`, 432 lines. **The answer is
“documented at this tag” — a report of “not documented at this tag” would be wrong.**

Located content **[OBS]**:

- Frontmatter title line 2: `title: OpenAI compatibility`; body line 5: “Connect OpenAI clients to
  Ollama. Ollama supports a subset of the OpenAI API.” (13 words).
- `## Endpoints` at 209; `### /v1/models` at **290**; `### /v1/models/{model}` at **297**.
- Notes under both (294–295, repeated 301–302): “`created` corresponds to when the model was last
  modified” (9 words) and “`owned_by` corresponds to the ollama username, defaulting to `"library"`”
  (9 words). The page documents the routes and those two field semantics only; it makes no
  loaded/residency/readiness promise **[OBS]**.
- Reachability in the same tag's nav: `docs/docs.json` (HTTP 200, 6403 bytes) lists
  `/api/openai-compatibility` in the “API Reference” group (line 244) and redirects `/openai`
  (84–85) and `/api/openai` (88–89) to `/api/openai-compatibility`.

Tree search evidence **[OBS]**: the tag's root `docs/` listing (GitHub contents API,
`contents/docs?ref=v0.40.11`, HTTP 200, 27042 bytes) contains **no** `openai*` file; `docs/api/`
(HTTP 200, 8269 bytes) lists exactly `openai-compatibility.mdx` among 9 files; `docs/integrations/`
holds `openclaw`/`opencode` (different products). Direct probes returned 404 for
`docs/openai.md`, `docs/openai.mdx`, `docs/openai-compatibility.md`, `docs/api/openai.md`,
`docs/integrations/openai.md`, `docs/openai/openai.md`, `docs/v1.md`.

Lane context **[OBS]**: the same file is already cited by `corpus/SOURCES.md` **S010** at commit
`c1737589973d5cefd676ef16eb43835663540035` (2026-09-23), §Endpoints `/v1/models`. So the path is not
new; only the tag-pinned revision and line anchors are. A round-80 row must not restate S010 as a
discovery, and must not contradict it.

## C. The lane's existing Ollama instruments and pins — and what the census must not duplicate

All lane paths below are under `/home/vgpnk/Projects/shokunin/kama-shokunin/`; sizes are bytes on
disk at observation **[OBS]**.

| # | Instrument / pin | What it already holds |
|---|---|---|
| 1 | `tools/kama-ollama-live.py` (24157 B, 558 lines, schema `kama-ollama-live/v2`) | Pinned-binary + GGUF digest checks against `registry/ollama-live-pin.tsv` (`binary-digest`, `model-digest`, `running-exe-digest`, `/api/version`); scratch HOME/`OLLAMA_MODELS` under `--work`; captures `root`, `version`, `tags-empty`, `tags`, `v1-models-empty`, `v1-models`, `v1-model-single`, `show`, `ps-before`, `generate`, `ps-after`; graded tags-vs-ps digest equality, `/v1/models` list and single id forms, `--hold-dir` outside contact, `PR_SET_PDEATHSIG(SIGKILL)`, teardown proof (`child_pre_dead`, `port_closed`); replays through `tools/kama-ollama-evidence.py`. Registered ports are hardcoded `REGISTERED_PORTS = {8080, 34113}` (line 68; the constant block is duplicated verbatim at 107–112). |
| 2 | `tools/kama-ollama-evidence.py` (21028 B) | Offline classifier over caller-supplied tags/ps bodies: `loaded_same_digest`(0), `available_not_loaded`(1), `remote_inventory`(1), `identity_conflict`(1), `unknown`(2), `invalid_input`(2); never contacts an endpoint. The available-vs-loaded distinction already exists as executable code. |
| 3 | `registry/ollama-live-pin.tsv` (11 lines) | `version 0.40.11`; `archive_sha256 7bedab90…` (`ollama-linux-amd64.tar.zst`, 1508659610 bytes); `bin_sha256 b0a4becf…` (40779408 bytes); `model_sha256 270cba1b…` (`stories260K.gguf`); `default_home ~/.local/opt/ollama-v0.40.11`; `default_model ~/.cache/kama-shokunin/models/stories260K.gguf`. This is the only Ollama pin file. Ollama is **absent** from `registry/engine-pins.tsv` (3 rows: sglang v0.5.22, vllm v0.32.0, llama.cpp b11755), so C2's `engines=3` does not include Ollama. |
| 4 | `corpus/knowledge/ollama-live-lifecycle.md` (65 lines) | `verified-at: 2026-10-27`; sources S519/S520/S521/S523; captured HTTP value table (root 200; version `{"version":"0.40.11"}`; `tags-empty`/`ps-before` `{"models":[]}`; `v1-models-empty` `{"object":"list","data":null}`; tags one qualified entry with digest; `/v1/models` list id qualified vs single-route id unqualified; `ps-after` qualified name, same digest, `expires_at`, `size_vram`; `generate` `done:true`); v2 harness changes (hold-dir, pdeathsig, graded `/api/show`, evidence replays); boundaries (no registered-consumer health, no quality, one release/model/host). |
| 5 | `registry/ollama-live-claims-r61.tsv` (28 data rows) | 17 graded claim rows over receipt captures + 11 `notobs` rows naming the lifecycle/crosswalk lines recorded as inference. |
| 6 | `.ufo/waves/round-60/live/receipt.json` (19270 B) / `.ufo/waves/round-61/live/receipt.json` (20131 B) | The two run receipts behind that knowledge entry (v1 nonce `b61c98ad5747`; v2 nonce `r61live01`, port 47887 per the entry). |
| 7 | `tools/round61-c1-counter.py` (20815 B), `tools/round61-c2-counter.py` (24120 B) | The live re-contact counter and the claim-registry evaluator for those receipts. |
| 8 | `tools/round79-unregistered-census.py` (17352 B) | The class proof on the **llama.cpp** fixture: free loopback port outside the registry, two scratch registries, `kama-probe.sh listeners --json` grading, selftest arms `both-legs`/`class-missing`/`probe-error`/`absent-probe`, informational live-host leg; registered ports read from `registry/endpoint-consumers.tsv`. |
| 9 | `tools/kama-probe.sh` | `listeners` already emits the `registered` column (line 768) and the `governed`/`unregistered` summary (770–801). Class = a model-surface verdict (`MODEL_OK`/`MODEL_MISMATCH`/`MODEL_LOADING`/`UNAUTHORIZED_SERVICE`) whose port is in the registry's declared base URLs → `yes`; `no` otherwise; `-` for non-model surfaces or an unreadable registry (`classify_registration`). Introduced by round-79 commit `5ac1a8dd` and **present at the round-80 base** `c45fc7d1` (2 `classify_registration` occurrences; `git diff c45fc7d1 -- tools/kama-probe.sh` empty). |
| 10 | `registry/endpoint-consumers.tsv` (3 rows) | Declared base URLs 8080 and 34113 → governing port set `{8080, 34113}`. A census child on any other free loopback port is `registered=no` by construction; `registered=yes` requires a scratch registry naming the child port. |

Absent / new at observation time **[OBS, timestamped]**:

- `registry/unregistered-class-engines.tsv` — absent (so `--audit` cannot yet print the two-engine line).
- `tools/round80-ollama-census.py` — now present as an **untracked worktree file** (18405 B, mtime
  07:43; it did not exist when this seat started). It hardcodes `SERVER=~/.local/opt/ollama-v0.40.11/bin/ollama`,
  `MODEL=~/.cache/kama-shokunin/models/stories260K.gguf`, `PIN_VERSION="0.40.11"`; reads registered
  ports from `registry/endpoint-consumers.tsv`; starts the child with scratch `HOME`/`OLLAMA_MODELS`,
  creates one model from the fixture GGUF, asserts `/api/version`, asserts the created model is in
  `/api/tags`, captures `/v1/models` and `/api/ps` as observations, runs the probe against two scratch
  registries and grades `registered`/counts, then writes its receipt and (on audit) the register row.
  It does **not** read `registry/ollama-live-pin.tsv` and does **not** verify the binary or GGUF
  sha256 — the pin identity is asserted only as the `/api/version` string **[OBS from code read]**.
  Teardown is `child.terminate()` in `finally` with `start_new_session=True` and no
  `PR_SET_PDEATHSIG`, so a SIGKILLed census parent can leave the child serving **[INF from code read]**.
- No SOURCES row for `docs/api.md` at `v0.40.11`. Existing Ollama doc rows: S010 (openai-compat
  `@c1737589`), S011/S031 (docs.ollama.com/api/tags), S012 (docs.ollama.com/api/ps). S519–S521 cover
  the release digest manifest, FAQ bind/store, and GGUF import; S523 covers the live tool receipt.

Non-duplication guidance for the census seat **[INF, from the above]**:

1. Reuse `registry/ollama-live-pin.tsv` as the engine identity rather than re-declaring version and
   paths; digest verification of binary and GGUF already exists in `kama-ollama-live.py` and is
   currently the one pin fact the census does not carry.
2. Do **not** add Ollama to `registry/engine-pins.tsv`: C2's `engines=3`/`refs=5` is frozen over
   sglang/vllm/llama.cpp, and a fourth row would change that claim's counts.
3. Do **not** re-claim the tags-vs-ps split as new knowledge: `corpus/knowledge/runtime-health-surface-matrix.md:17`
   states it, `corpus/knowledge/served-identity-crosswalk.md:13` explicitly credits that row and claims
   none of the split as new, and `corpus/QUALITY.md` KQ13 makes inventory, residency, identity and
   readiness separate propositions. A round-80 knowledge entry should cite them, not repeat them.
4. Do **not** cite `docs/api.md` for remote-entry markers: that file omits `remote_model`/`remote_host`;
   the same tag's `openapi.yaml` documents them, and S031 already files the caveat (as an inference,
   with a disclosed supersession of S011).
5. The class-engine register row must name its own engine (`ollama`) and its own receipt carrying
   `class_missing=0`; the round-79 llama.cpp receipt must not be reused as a second engine.
6. A `class_missing=1` control needs a stub/older probe copy: the base probe **has** the class, so
   `git show c45fc7d1:tools/kama-probe.sh` is not a class-missing control [OBS; the frozen control
   `measured/control/c3-base-probe.out` was absent when read — see below].

## Facts / inference / gaps

**Facts [OBS]:** the two endpoint anchors and quotes above; `/api/tags` fields without residency
fields; `/api/ps` with `expires_at`/`size_vram`; `openapi.yaml` at the tag documenting tags/ps but
none of the `/v1/*` OpenAI routes; `docs/api/openai-compatibility.mdx` HTTP 200 at the tag with
`/v1/models` at line 290; the tag's nav/redirects; the lane instrument inventory, sizes and the
round-79 origin of the probe class; Ollama absent from `engine-pins.tsv`; the census tool's
hardcoded constants and its lack of digest checks.

**Inference [INF]:** tags membership is inventory-only and not a loaded-state proof (supported by the
doc's own ps wording and the corpus KQ13/crosswalk); a SIGKILLed census parent can orphan the Ollama
child; a round-80 `/api/tags` SOURCES row is best anchored at the pinned file's line 1358 sentence.

**Gaps [GAP]:** (i) the upstream tree was enumerated only under `docs/` (one level plus
`api/`, `capabilities/`, `integrations/`, `tools/`); a docs path outside `docs/` was not searched —
the tag's `docs.json` nav enumerates the published pages and carries only the one openai page.
(ii) docs.ollama.com pages were not opened this round; the tag's GitHub bytes are the reference.
(iii) Lane state is a moving target: sibling files appeared during the run (lane tip moved
`c45fc7d1`→`fe7b9780`, census tool appeared at 07:43), so absence claims above are timestamped at
10:43Z. (iv) The frozen C3 pre-freeze receipts `measured/before/c3-engines-before.out` and
`measured/control/c3-base-probe.out` did not exist when read; `measured/before/` held `c1-enum.out`
and `c2-relations-absent.out`, `measured/control/` held only the C1/C2 files. Reported as state, not
as a failure of this seat.

## Commands and exit codes

Every command below exited 0; the full byte/status/sha256 log is in `receipts.txt`.

| Command (abridged) | Result |
|---|---|
| `curl -sS -o api_v0.40.11.md -w 'HTTP=%{http_code} BYTES=%{size_download}\n' …/v0.40.11/docs/api.md` | HTTP=200 BYTES=54614, sha256 `96db0308…` |
| `curl … …/v0.40.11/docs/api/openai-compatibility.mdx` | HTTP=200 BYTES=25472, sha256 `44071a12…` |
| `curl … 'api.github.com/repos/ollama/ollama/contents/docs?ref=v0.40.11'` (+ `docs/api`, `docs/integrations`, `docs/capabilities`, `docs/tools`) | HTTP=200 (27042 / 8269 / 25367 / 8615 / 848 bytes) |
| `curl … …/v0.40.11/docs/docs.json` | HTTP=200 BYTES=6403 |
| `curl … …/v0.40.11/docs/openapi.yaml` | HTTP=200 BYTES=87348, sha256 `e94c8f02…` |
| 7 candidate openai paths at the tag | 404 each |
| `git ls-remote --tags https://github.com/ollama/ollama 'v0.40.11' 'v0.40.11^{}'` | `675150d6…	refs/tags/v0.40.11` |
| `git -C lane diff --stat c45fc7d1 -- tools/kama-probe.sh` | empty |
| `git -C lane log --oneline -S'classify_registration' -- tools/kama-probe.sh` | `5ac1a8dd` (round-79) |

Tooling: no installs or upgrades were performed (host pacman transactions are paused; nothing was
needed). Scratch `$S` removed before yield; `receipts.txt` is the only copied receipt.
