# ScoutModelProvenance — `ggml-org/models-moved` / `tinyllamas/stories260K.gguf`

Read-only provenance scout for the new SOURCES row. Snapshot at
2026-10-20T13:27:45Z (10:27 -03); the fetch sweep immediately preceded it. Wrote
only this file; no lane gate, harness or test run; no tool installed or updated.

Axes: **A1 pin reproducibility** (which commit, and is a path pin enough?),
**A2 URL truth** (does the ticket's page redirect exist?), **A3 row admissibility**
(license, kind enum, tier, and what the drafted S038 lacks).

## Verdict

- **No hash mismatch.** `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
  is confirmed by five independent surfaces, and bytes fetched through the *old*
  URL are `cmp`-identical to `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`
  (both 1 185 376 bytes).
- **The ticket's page-level redirect no longer exists.** `https://huggingface.co/ggml-org/models`
  answers **HTTP 200 with the ggml-org model listing** (0 redirects). Only the
  `/api/…`, `/blob/…` and `/resolve/…` forms 307 to `models-moved`.
- **No license is declared** anywhere: repo card, file page and GGUF metadata are
  all silent. A SOURCES row may record "no license declared"; it cannot support
  any reuse claim.

## O1 — repo identity

`https://huggingface.co/api/models/ggml-org/models-moved`:

```
"id": "ggml-org/models-moved",  "_id": "6580840062b6ed53c4c72d61",
"sha": "499bc8821c6b12b4e53c5bffcb21ec206f212d81",
"lastModified": "2025-10-28T10:43:38.000Z",  "createdAt": "2023-12-18T17:40:16.000Z",
```

Quote: `"sha": "499bc8821c6b12b4e53c5bffcb21ec206f212d81"`. The canonical page is
`https://huggingface.co/ggml-org/models-moved` (`rel="canonical" href="https://huggingface.co/ggml-org/models-moved"`).
`createdAt` equals the repo's initial commit date (`eeb7ae40…`, 2023-12-18T17:40:16Z), so
[INFERENCE] this is an in-place rename of the same repo object, not a new repo.

## O2 — file identity at HEAD (499bc882)

`https://huggingface.co/api/models/ggml-org/models-moved/tree/main/tinyllamas?expand=true`
(one `tinyllamas/stories260K.gguf` entry; the `/tree/main/<file>` form errors — see T6):

```
"path": "tinyllamas/stories260K.gguf", "size": 1185376,
"oid": "941cd12cc9e7e7b83944e83ab5887cbed28d2f0f",
"lfs": {"oid": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
        "size": 1185376, "pointerSize": 132},
"xetHash": "7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5",
"lastCommit": {"id": "96f460f9c1e2ca43d0adc1c682b832525a2c0ea3",
               "title": "gguf : bump training context from 256 to 2048",
               "date": "2025-10-28T08:55:08.000Z"}
```

Quote: `"lfs": {"oid": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d", "size": 1185376`.
The **file-level** commit is `96f460f9`, not repo HEAD `499bc882`; `499bc882`'s tree
carries the identical LFS oid (verified by re-querying the tree at that revision).

`HEAD https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`
→ `302`, `x-repo-commit: 499bc882…`, `x-linked-size: 1185376`,
`x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`.

## O3 — file page

`https://huggingface.co/ggml-org/models-moved/blob/main/tinyllamas/stories260K.gguf`
renders both hashes:

```
Xet hash: 7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5
Size of remote file: 1.19 MB   ·   SHA256: 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
```

Quote: `SHA256:</dt> <dd class="truncate">270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
`1.19 MB` is decimal MB of 1 185 376 bytes — consistent, not a mismatch. The same
page's VirusTotal link keys on the sha256 (`file/270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
"0/76 engines detect it as malicious").

## O4 — mismatch check (the assigned question)

| # | surface | value |
|---|---|---|
| 1 | tree API `lfs.oid` | `270cba1b…3d256d` |
| 2 | `x-linked-etag` on resolve | `270cba1b…3d256d` |
| 3 | file page `SHA256` | `270cba1b…3d256d` |
| 4 | bytes downloaded via old URL (`sha256sum`, 1 185 376 B) | `270cba1b…3d256d` |
| 5 | local cache file (`sha256sum`, 1 185 376 B) | `270cba1b…3d256d` |

`cmp /tmp/dl.gguf ~/.cache/kama-shokunin/models/stories260K.gguf` → identical.
**Mismatch: none.** The download was fetched through
`https://huggingface.co/ggml-org/models/resolve/…` (2 redirects, final `200`,
`us.aws.cdn.hf.co/xet-bridge-us/…/7cfbf69e…`), i.e. the old URL still resolves.

## O5 — redirect matrix (A2)

| URL | status | hops | evidence |
|---|---|---|---|
| `https://huggingface.co/ggml-org/models` | **200** | 0 | `<title>ggml-org (ggml-org)</title>`; description `Org profile for ggml-org on Hugging Face…`; links to `/ggml-org/lev-GGUF`, `/ggml-org/Qwen3.5-0.8B-GGUF`, …; **zero** `models-moved` matches |
| `https://huggingface.co/api/models/ggml-org/models` | 307 | 1 | `location: /api/models/ggml-org/models-moved` |
| `https://huggingface.co/ggml-org/models/blob/main/tinyllamas/stories260K.gguf` | 307 | 1 | body: `Temporary Redirect. Redirecting to /ggml-org/models-moved/blob/main/tinyllamas/stories260K.gguf` |
| `https://huggingface.co/ggml-org/models/resolve/main/tinyllamas/stories260K.gguf` | 307→302 | 2 | then Xet CDN `200`, 1 185 376 B |

Quote for the page: `content="Org profile for ggml-org on Hugging Face, the AI community building the future."`
So the ticket's "observed redirect" is true only of API/blob/resolve paths; the bare
repo page now falls back to the org model listing (page title/description are the org's,
and it lists unrelated repos). Cite `models-moved` URLs in the row.

## O6 — license (A3)

- API `?full=true`: `cardData` → `null`; tags → `["gguf", "endpoints_compatible", "region:us"]`; no `license:*` tag.
- Repo root siblings: `.gitattributes`, `README.md` only — no `LICENSE`, no `LICENSE.md`.
- `https://huggingface.co/ggml-org/models-moved/raw/main/README.md` (2 lines):
  "Various models to be used in llama.cpp CI workflow." / "Do not use it in production."
- File page: **0** case-insensitive matches for `license` in 161 151 bytes.
- Local GGUF (19 KV keys, parsed): `general.architecture=llama`, `general.name=llama`,
  `llama.context_length=2048`, `block_count=5`, `embedding_length=64`, `feed_forward_length=172`,
  heads 8/4, `rope.dimension_count=8`, 512-token vocab; **no** license/author/repo key.

**License = not declared.** [INFERENCE] A Tier-A row can support "this repo declares no
license and calls itself a CI fixture"; it cannot support Apache-2.0, MIT, or any reuse
permission for the weights. Upstream training provenance is not stated on the repo.

## O7 — revision drift (A1)

`/tree/<rev>/tinyllamas?expand=true`, same path, same 1 185 376-byte size:

| rev | date | lfs oid |
|---|---|---|
| `688f41dd` ("Upload 3 files") | 2025-09-26T14:05:14Z | `047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b` |
| `22027b1a` ("bump training context 128 to 256") | 2025-10-28T08:07:12Z | `68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2` |
| `96f460f9` ("bump … 256 to 2048") | 2025-10-28T08:55:08Z | `270cba1b…3d256d` |
| `e2d5caf5` | 2025-10-28T09:18:28Z | `270cba1b…3d256d` |
| `499bc882` (HEAD) | 2025-10-28T10:43:38Z | `270cba1b…3d256d` |

Three distinct bytes for one path within ~2.5 h on 2025-10-28. A path-only pin is not
reproducible; the row must carry `commit + path + sha256 + size`. The pinned file's own
`llama.context_length=2048` matches the `96f460f9` commit title.
(Note: `/commits/main?path=…` is **not** usable as file history — see T3.)

## Traps found while measuring

- **T1 repo-level `gguf` block is an aggregate.** API returns
  `"gguf": {"total": 7241732096, "context_length": 32768, "totalFileSize": 3182393056}`.
  The 260K file is 5 blocks × 64 dim, `context_length=2048` (O6). [INFERENCE] HF sums the
  repo's GGUF files; do not quote this block as a fact about `stories260K.gguf`.
- **T2 two hashes on one page.** `Xet hash` (`7cfbf69e…`) ≠ `SHA256` (`270cba1b…`). Only
  the latter is the LFS oid / `x-linked-etag` / local file digest.
- **T3 `commits?path=` filter is ignored.** `…/commits/main?path=tinyllamas/DOES_NOT_EXIST.gguf`
  returns 30 entries, exactly like the real path. Use the tree entry's `lastCommit`.
- **T4 resolve is Xet-bridged.** The 302 target is
  `us.aws.cdn.hf.co/xet-bridge-us/6580840062b6ed53c4c72d61/7cfbf69e…`, keyed by the Xet hash,
  not a classic LFS object URL; integrity is still the sha256.
- **T5 decimal MB.** `1.19 MB` == 1 185 376 B; a row that quotes "1.19 MB" and "1185376" side
  by side is consistent.
- **T6 tree endpoint is dir-scoped.** `…/tree/main/tinyllamas/stories260K.gguf` →
  `{"error":"tinyllamas/stories260K.gguf does not exist on \"main\""}`; query the parent dir.

## Delta for the drafted row (S038)

`.ufo/waves/round-16/build/drafts/sources-rows.md:12` already pins repo commit `499bc882`,
`SHA256`, `1.19 MB`, tree size/oid and `lastModified`. Missing or imprecise there:

1. **license** — absent; add "no license declared (no cardData, no LICENSE, README calls it a CI fixture)".
2. **file-level commit** — add `96f460f9` ("gguf : bump training context from 256 to 2048", 2025-10-28T08:55:08Z);
   note HEAD `499bc882` carries identical bytes.
3. **redirect shape** — row says "page resolves to models-moved"; true for `blob`/`api`/`resolve` (307),
   false for the bare page (200 org listing). State which URL form was used.
4. **kind** — `dataset` is a new enum value: `corpus/SOURCES.md` rows S001–S034 use only
   `docs` (26), `community` (3), `spec` (2), `own-work` (2), `code` (1); `dataset` occurs 0 times.
   Contract-owner decision; flag rather than assume.
5. **recheck** — the file is mutable and churned 3× in 2.5 h; if C2's pin gates the launch,
   recheck belongs at `every round`, not on a calendar.
6. **local byte check** — add "downloaded via old URL, `cmp`-identical to the cache copy, 1 185 376 B".
7. **id** — corpus max is S034; S035–S038 are drafted only. If all four land, the next free id is S039.

## Unknowns

- **When/why the rename happened**: no rename date exposed; [INFERENCE] in-place rename from
  matching `_id`/`createdAt`. The `README` has no move notice (only the CI-fixture text).
- **Why the bare page URL renders the org listing** instead of a 307: HF routing behaviour, not
  recorded anywhere I opened.
- **Local acquisition receipt missing**: the only lane references to `270cba1b…` are build
  spec/context files (`.ufo/waves/round-16/build/spec.json`, `dispatch.json`, `spawn-result.json`).
  `tools/kama-llamacpp-live.py` named by C2 does not exist at read time — `tools/` holds
  `kama-probe.sh`, `kama-ollama-evidence.py`, `test-snapshot.sh`.
- No `SOURCES-CONTRACT` document file exists under `corpus/` (`QUALITY.md`, `README.md`,
  `SOURCES.md`, `knowledge/`, `lessons/` only), so tier/kind vocabulary was read from the
  34 existing rows, not from a spec.

## Tooling

No installs or upgrades. Used `curl`, `sha256sum`, `cmp`, `python3` (stdlib GGUF parse).
Scratch files: `/tmp/hf_models_page.html`, `/tmp/hf_org.html`, `/tmp/hf_file_page2.html`,
`/tmp/dl.gguf` (outside the lane; no lane file touched besides this report).
