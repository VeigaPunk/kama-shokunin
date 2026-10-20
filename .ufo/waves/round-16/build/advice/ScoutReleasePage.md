# ScoutReleasePage — llama.cpp b11755 release facts (candidate SOURCES row)

**Seat:** leaf scout, read-only. **Axes:** calibration (7, lowest) + operability.
**Question:** tag, commit, published date, ubuntu-x64 CPU asset name/size/sha256 digest, and whether
the release notes mention server changes — data for a new SOURCES row.

**Headline:** tag `b11755` → commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, published
`2026-10-20T11:18:44Z`, **pre-release**; CPU asset `llama-b11755-bin-ubuntu-x64.tar.gz`,
**22,240,468 bytes**, API `digest` `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`
(matches the claim's `753bfa73…e226`). **The notes mention no server change** — and stronger, the
`b11753...b11755` delta is **2 commits / 2 files, none under `tools/server`**.

## Proposed S035 row (append after S034; next free id)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S035 | llama.cpp release b11755 — https://github.com/ggml-org/llama.cpp/releases/tag/b11755 | docs | A | Build provenance and Ubuntu x64 CPU asset identity for the pinned `llama-server` used by kama's loading-state measurements; not a behavioral contract | Release API `releases/tags/b11755` (release id 418313891); §Linux / "Ubuntu x64 (CPU)"; `published_at` 2026-10-20T11:18:44Z; `target_commitish` 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; asset `llama-b11755-bin-ubuntu-x64.tar.gz` (asset id 659121192) uploaded 2026-10-20T11:21:10Z; opened 2026-10-20 | b11755 is a prerelease whose only change line is the tag commit's Metal MoE kernel fix (#30610/#30699) and which names no server change; `b11753...b11755` changed 2 files, neither under `tools/server`, so `tools/server/server-http.cpp` at 704366d is the b11753 bytes; the CPU asset is 22,240,468 bytes with GitHub-computed `digest` `sha256:753bfa73…e226`. Release-note silence is not behavioral evidence; the compare file lists and the tagged `server-http.cpp` are. | queued | 2026-10-20 | on-release | — |

Notes for the integrator: `kind: docs`, `tier: A` follow the S020 precedent (release-note row); `queued`
+ `used-by —` because no corpus entry cites it yet — if the round-16 lesson cites the pin, set
`used-by: corpus/lessons/round-16.md`. This is a pure addition; no existing row or cell changes.

## Field-by-field evidence

| Field | Value | Source and quote (≤25 words) |
|---|---|---|
| tag | `b11755` | API `releases/tags/b11755`: `"tag_name": "b11755"`; page title "Release b11755 · ggml-org/llama.cpp · GitHub" |
| tag ref | `refs/tags/b11755` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | `git ls-remote --tags https://github.com/ggml-org/llama.cpp` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755` |
| commit | `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | API: `"target_commitish": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`; page shows ``704366d`` and "signed with GitHub's verified signature" (GPG `B5690EEEBB952194`) |
| release class | pre-release, not draft, `immutable: false` | API: `"prerelease": true`, `"draft": false`, `"immutable": false`; page prints "Pre-release" twice |
| release created | `2026-10-20T11:02:05Z` (same instant as the commit's author date) | API: `"created_at": "2026-10-20T11:02:05Z"`; commit API `"date":"2026-10-20T11:02:05Z"` |
| published | `2026-10-20T11:18:44Z` (updated `11:22:04Z`) | API: `"published_at": "2026-10-20T11:18:44Z"`; page renders "released this 20 Oct 11:18" |
| CPU asset name | `llama-b11755-bin-ubuntu-x64.tar.gz` | page: "Ubuntu x64 (CPU)" → `.../download/b11755/llama-b11755-bin-ubuntu-x64.tar.gz`; API `"name": "llama-b11755-bin-ubuntu-x64.tar.gz"` |
| asset id / state / upload | `659121192`, `uploaded`, `2026-10-20T11:21:10Z` | API: `"id": 659121192`, `"state": "uploaded"`, `"created_at": "2026-10-20T11:21:10Z"` |
| asset size | `22240468` bytes | API: `"size": 22240468`; independent HEAD of the download URL: `content-length: 22240468` |
| asset digest | `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` | API: `"digest": "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"` — the sha256 is 64 hex chars, prefix `753bfa73`, suffix `e226` |
| served MIME | `application/octet-stream` | HEAD after the 302 to `release-assets.githubusercontent.com`: `content-type: application/octet-stream` (API metadata instead says `"content_type": "application/json; charset=utf-8"` — metadata default, not the transfer type) |
| download count at capture | 154 | API: `"download_count": 154` (mutable; do not write into a registry cell) |

## Release-notes content: no server change named

- Body change list, in full — one line inside `<details open>`:
  "metal : fix missing MoE kernel variant for 9 experts per token (#30610) (#30699)".
- `grep -c -i server` over the release `body` → **0**. The rest of the body is Website, Attestations
  (`https://github.com/ggml-org/llama.cpp/attestations/57761738`) and per-platform download links.
- The tagged commit's file list is a single file:
  `"filename": "ggml/src/ggml-metal/kernels/mul_mm.metal"`, `"additions": 1, "deletions": 0, "total": 1`.

**Caveat that matters for how this is cited:** llama.cpp's CI release body is the *tagged commit's
subject*, not a changelog for the tag delta. Silence about servers here says nothing about
`b11754→b11755` by itself. The delta was therefore checked separately (next section).

## The build delta b11753…b11755 (resolves the silence)

`b11754` does not exist as a tag; the neighbours are `b11753` (`d8d9297`, prior build) and `b11756`
(`d8061939`, newer than the pin). Compare page `.../compare/b11753...b11755` reports
"2 commits" and "2 files changed":

1. `707616feb5f379e99ff7442680a55b4a1704c7c9` — "ci: Fix --strict mode for API check (#30623)";
   `.patch` shows only `scripts/check-apiabi-compat.sh`.
2. `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` — the Metal kernel above.

Therefore [INFERENCE, from the two exhaustive per-commit file lists] **no `tools/server` file changed
between the previous build and b11755**; the tagged `server-http.cpp` equals its b11753 bytes.

## Corroboration of C1's line citation (same commit, fetched raw)

`raw.githubusercontent.com/.../704366d76f.../tools/server/server-http.cpp`:

- L307: `auto middleware_server_state = [this](const httplib::Request & req, httplib::Response & res) {`
- L308: `if (!is_ready.load()) {`
- L310: `return true; // frontend asset, allow it to load and show "loading"` — the only exemption
- L314: `res.status = 503;`
- L318: `{"message", "Loading model"},`
- L319: `{"type", "unavailable_error"},`
- L320: `{"code", 503}`
- Registered as a **pre-routing** handler (L331 `srv->set_pre_routing_handler(...)`), so every
  non-frontend path — `/v1/models` and `/health` alike — gets the same 503 body while not ready.

C1's range `307-325` is exact for this lambda. The sibling `ScoutReadmeDelta.md` separately shows the
README documents this body under `GET /health` only (new:486-487), so a `/v1/models`-based matcher must
cite `server-http.cpp`, not the README.

## Caveats and limitations

- **API rate limit exhausted mid-run** (`x-ratelimit-remaining: 0`, 60/hr unauthenticated) after the
  release, commit and asset reads; all values above come from responses captured before that, so a
  re-read of S035 today needs a token. `git ls-remote` (protocol, not REST) and raw/patch URLs kept
  working.
- The release **HTML asset table never rendered** ("Assets 38" followed by "Loading", then an error), so
  size/digest exist only in the REST payload; the page's "Assets 38" vs API `assets[]` length **36**
  differs by the two auto-generated source archives [INFERENCE].
- `digest` is GitHub's own upload-time computation, not a publisher-signed checksum; the signed surface
  is the attestation link above. I did **not** download the 22 MB asset to re-hash it.
- The pin is already **not the tip**: `b11756` (`d8061939`) exists as of this check, so "current
  release" must not be claimed for b11755 — `recheck: on-release` is the honest cell.
- Local-install mtimes are a trap, flagged so nobody reads substitution: `~/.local/opt/llama-b11755`
  members are stamped `2026-10-20 08:10:36 -0300` (**11:10:36Z**) — *earlier* than the asset upload
  (11:21:10Z) — while `~/.local/bin/llama-server` is `10:17:53 -0300` (**13:17:53Z**).
  [INFERENCE] the directory carries the tarball's CI build mtimes (tar preserves them); the symlink
  mtime is the real install moment, which is after both upload and publication and matches L1's 10:17
  smoke.
- No LSP applies: everything here is a remote REST/HTML/raw fetch plus `git ls-remote`; no repo file was
  resolved semantically, so no definition/reference traversal was possible or needed.
- Read-only run: no file outside this Report was written, no gate/harness executed, no server started.

## Installs

None this run (no package, tool or binary installed or upgraded). REST reads used `curl` + `jq` already
present on the host.
