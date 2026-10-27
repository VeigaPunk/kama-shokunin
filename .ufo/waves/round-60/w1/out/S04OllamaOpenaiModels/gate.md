# Gate — S522, Ollama OpenAI compatibility: model list and single-model routes

## Source opened now (2026-10-27)

- Canonical URL: <https://docs.ollama.com/api/openai-compatibility> — HTTP 200 this run
  (`curl -sS -m 40 -o compat.html -w "%{http_code}" https://docs.ollama.com/api/openai-compatibility` → `200`)
- Version-matched source actually read for the row: <https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx>
  → HTTP 200, 25472 bytes, sha256 `44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5`,
  git blob `75218fc8f8044a8d0c0f0adc6c77684fec57711f`, tag `v0.40.11` → commit `675150d6ad2747df1e218ef59de9194bc4a7e538`
  (`https://api.github.com/repos/ollama/ollama/git/ref/tags/v0.40.11` → `REF=200`).
  Snapshot kept at `docs-api-openai-compatibility-v0.40.11.mdx` beside this file.
- Note: `docs/openai.md` at the same tag is 404 (`TAG_HTTP=404`); the page's source file is `docs/api/openai-compatibility.mdx`.

## Quote (18 words, located)

Heading **`/v1/models` → `#### Notes`**, lines 292–295 of the tag blob (identical two lines repeat under `### /v1/models/{model}`, lines 299–302):

> `created` corresponds to when the model was last modified — `owned_by` corresponds to the ollama username, defaulting to `"library"`

Scope of the quoted statement: the semantic values of those two response fields on those two routes. It says nothing about `id`.

## Measured absence (the scope's `id` question)

```
$ grep -n '\bid\b' docs-api-openai-compatibility-v0.40.11.mdx ; echo "exit=$?"
exit=1
$ grep -n '"data"\|"object"\|"id"' docs-api-openai-compatibility-v0.40.11.mdx ; echo "exit=$?"
exit=1
```

The 432-line page never writes the token `id`, and carries no sample response body for either route. So the documentation states no `id` semantics and no response envelope for `/v1/models` or `/v1/models/{model}`; both headings consist solely of the two notes above. It also names no HTTP method for either route (headings are paths only).

## Tier

**A**, bounded to this scope. First party: the page is the Ollama project's own documentation, and the version-matched text is in the `ollama/ollama` repository at the release tag under `docs/api/`, i.e. the same tree as the server it describes — a primary statement of that server's own OpenAI-compatible surface, not a third-party summary, and not a community artifact. The A is asserted only for statements about the field semantics of `/v1/models` and `/v1/models/{model}` at v0.40.11; it does not extend to other Ollama pages, to other versions, or to the `/v1/chat/completions`, `/v1/completions`, embeddings or audio sections of the same file.

## Duplicate check

```
$ grep -n 'docs.ollama.com/api/openai-compatibility' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
22:| S010 | Ollama OpenAI compatibility — https://docs.ollama.com/api/openai-compatibility | docs | A | Ollama OpenAI-compatible surface | §Endpoints `/v1/models`; source docs/api/openai-compatibility.mdx @ ollama/ollama c1737589973d5cefd676ef16eb43835663540035 (2026-09-23) | Ollama supports a subset of the OpenAI API; `/v1/models` notes `created` and `owned_by` semantics; no health route appears on this page. | mined | 2026-10-19 | on-release | corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md |
292:- **2026-10-20 (UTC) — round-11 served-identity re-open** ... (ledger prose mentioning the same URL)
exit=0
$ grep -n 'ollama/blob/v0.40.11/docs/api/openai-compatibility' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=1
$ awk -F'|' '/^\| S[0-9]/{gsub(/ /,"",$2);print $2}' corpus/SOURCES.md | sort | tail -1
S518
$ grep -c '^| S519 \|^| S520 \|^| S521 \|^| S522 ' corpus/SOURCES.md
0
```

**Verdict: within-scope duplicate — reported, not silently added.** S010 holds the same URL with the broader scope cell "Ollama OpenAI-compatible surface", so this row's scope is a subset of S010's. The row is nevertheless distinguishable and is filed as a report rather than a refusal because: S010's anchor pins docs commit `c1737589…` (2026-09-23) and not a release tag; S010's `teaches` names only `created`/`owned_by` on §Endpoints `/v1/models`; S010 names neither the `/v1/models/{model}` route nor the `id` question, which is this row's added content. Integrator choice (not applied by me): fold the single-model-route and `id`-absence facts into S010, or accept S522 as the release-pinned narrower row. S522 as written contradicts nothing in S010. Id space confirmed free: highest existing id `S518`, zero rows at S519–S522, so the assigned `S522` does not collide.

## Observations — documentation versus the committed live capture (not part of the quote)

Receipt: `.ufo/waves/round-60/live/receipt.json` (`kama-ollama-live/v1`). Both compared captures re-hash to their recorded `sha256` (`hash_ok True` for `v1-models` and `v1-model-single`).

1. **`id` form differs between the two routes, and the documentation covers neither.** Live `GET /v1/models` returned
   `{"object":"list","data":[{"id":"kama-b61c98ad5747:latest","object":"model","created":1793136550,"owned_by":"library"}]}`
   while `GET /v1/models/kama-b61c98ad5747` (the exact request the tool issued, `tools/kama-ollama-live.py:363`) returned
   `{"id":"kama-b61c98ad5747","object":"model","created":1793136550,"owned_by":"library"}`. The list `id` is tag-qualified; the single-route `id` is not; the receipt records `v1_single_id_equals_list_id = false`. The page states no rule that predicts or forbids this.
2. **`created` note holds in this capture.** Doc: "when the model was last modified". Live `created = 1793136550` equals the epoch of `/api/tags` `modified_at` `2026-10-27T18:29:10.137112591-03:00` exactly (delta 0 s; `1793136550` = 2026-10-27T21:29:10Z).
3. **`owned_by` note holds.** Live value `"library"` on both captures, matching the documented default.
4. **Response envelope undocumented.** Live list body uses `object`/`data`; the single body is a bare model object with no envelope; the doc contains no `object`, `data` or `id` literal at all. An empty store returns `{"object":"list","data":null}` (`v1-models-empty`), a `null`-versus-`[]` distinction the page does not address.
5. **Path-parameter qualification undocumented.** The single route answered 200 for the untagged name and echoed it untagged; the doc gives no statement on whether the `{model}` path takes a bare or tag-qualified name.
6. **Live page is not the v0.40.11 text.** The 2026-10-27 page (200) still shows both sections with the same two notes (extracted text lines 639–656), but it also documents `/v1/audio/translations` as "Added in Ollama v0.40.12", i.e. it has moved past the tag. The row therefore anchors the tag blob, not the floating page.

## Limits

One server version (0.40.11), one nonce-named import of one 1.1 MB GGUF fixture, one capture; nothing here addresses cloud/remote model entries, tag-qualified single-route requests (never captured), other `id` forms, or the rest of the OpenAI-compatible surface.
