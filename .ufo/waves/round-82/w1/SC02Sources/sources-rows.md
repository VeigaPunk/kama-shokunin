# SC02Sources — round-82 SOURCES row drafts (contract-v1, 11 columns)

Every row below is for a URL this seat opened itself on 2026-11-04; status, bytes, sha256 and the
anchor line for each fetch are in `curl.txt` in this directory. No cell contains a `|`.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S563 | llama.cpp server README at build tag b12103 — https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md | docs | A | The pinned llama.cpp health surface at the tag the lane's relation register names newest at its 2026-11-04 read: whether the sentence the lane holds at the b11755 pin survives the release gap | heading "### GET /health: Returns health check result" at line 480, quote line 482: "This endpoint is public (no API key check). `/v1/health` also works."; raw file sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137`, 136429 bytes, 2620 lines | a newer release tag is a recheck trigger, never proof the held knowledge is wrong: the /health sentence is byte-identical to the lane's pin b11755 (S564) and only shifts one line (479 to 480) across 15 diff hunks; the README is also byte-identical (same sha256, 2620 lines) at b12110, the newest build tag at the read and the same commit as the stable v0.9.0 tag, so the newest-tag document carries the same anchored sentence | mined | 2026-11-04 | on-release | corpus/knowledge/pin-recheck-trigger.md |
| S564 | llama.cpp server README at the lane's pin b11755 — https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md | docs | A | The lane's own pinned reference for the llama.cpp health surface (registry/engine-pins.tsv pin b11755) | heading "### GET /health: Returns health check result" at line 479, quote line 481: "This endpoint is public (no API key check). `/v1/health` also works."; raw file sha256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`, 119661 bytes, 2402 lines | the pinned-ref side of the recheck, diffed against S563: one located sameness (the anchored sentence is byte-identical) and one located difference (the document grows 2402 to 2620 lines and the heading shifts 479 to 480; the sections present only at b12103 are "### Memory-based unloading", "### POST /tts: Generate speech audio from text" and "### WebSocket /v1/realtime: Realtime transcription") | mined | 2026-11-04 | on-release | corpus/knowledge/pin-recheck-trigger.md |
| S565 | SGLang docs basic_usage/native_api at v0.5.23 (raw docs source) — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx | docs | A | The SGLang Health Check surface the lane probes, at the newest tag the relation register names (v0.5.23) | "## Health Check" heading at line 108; quote line 111: "`/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down."; raw file sha256 `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c`, 18295 bytes, 471 lines | the newest-tag document states four health surfaces — `/health`, `/health_generate`, `/ready` and `/ping` — and the `/ready` and `/ping` bullets are absent from the same page at the lane's pin v0.5.22 (diff hunk @@ -108,6 +108,8 @@), so the release adds readiness and termination surfaces without changing the two held lines | mined | 2026-11-04 | on-release | corpus/knowledge/pin-recheck-trigger.md |
| S566 | llama.cpp b12103 build-release note (GitHub release page) — https://github.com/ggml-org/llama.cpp/releases/tag/b12103 | docs | B | What a build-release note announces, tested against the held /health statement | page title line 1: "Release b12103: opencl: improve q2_0 GEMV for Adreno (#31577)"; rendered text line 153: "b12103: opencl: improve q2_0 GEMV for Adreno (#31577)"; raw HTML sha256 `e71c6e3663d50ca69cadbccef99ce29a45f2f6b80949c5ee5cd75384a4b5ac86`, 174444 bytes, 203 rendered lines | REJECTED: a build-release note names one OpenCL/GEMV commit and its rendered text carries zero occurrences of `/health`, `/v1/models` or `GET /`, so it cannot ground a statement about the probed route; flip: a release note whose body states a change to the anchored route's behavior or semantics | rejected | 2026-11-04 | on-release | — |

## Registry state at the read (collision)

Read at lane tip `bacae0726d7c53455bd083bc6d478bbcd6e7fffc` (2026-11-04, local 10:06 to 10:09 -0300).

- The registry table holds **305** S-id rows, not 302: commit `962bd251` ("round-82: record the
  round-81 corrections, the round-82 claim/gate/disposition sections, the pin-recheck entry and its
  sources, KQ134 and the twelve-arm gate row") added S563, S564 and S565 to `corpus/SOURCES.md`
  (+3 lines in its stat) before this seat read it.
- Ids now in use: S563 (llama.cpp b12103, mined), S564 (llama.cpp b11755, mined), S565 (SGLang
  README v0.5.23, rejected). Next free id: **S566**.
- My S563 and S564 rows above are independent re-derivations: same URLs, same sha256 values
  (`eafc1b53…a137`, `714c067b…6a37`), same byte counts (136429, 119661), same line counts (2620,
  2402) and same anchor lines (480/482 and 479/481) as the filed rows. Nothing to file for them.
- The filed S565 (SGLang README at v0.5.23) was re-fetched by this seat for corroboration: 9472
  bytes, sha256 `a7654a48a8cd08c824e4445cb906405704148a3c55fb84362c7071d27397303c`, 120 lines, zero
  occurrences of `/health`, `/v1/models`, `health` or `served`; the filed rejection is corroborated
  on my own read, and my mined SGLang native_api row does not replace it.
- My S565 row (mined SGLang native_api at v0.5.23) is **not** in the registry: the filed S565 is the
  rejected SGLang README. My S566 row (rejected llama.cpp release note) is also not in the registry.

## Freshness note — the register's `newest` cell moved during this read

- `https://github.com/ggml-org/llama.cpp/releases/latest` resolved to `releases/tag/v0.9.0` at
  13:08:40Z on 2026-11-04 (published 2026-11-04T13:08:06Z); build releases b12109 (12:33:27Z) and
  b12110 (12:52:04Z) were already published before my first fetch at 13:07:36Z.
- `git ls-remote --tags` at 13:10Z: newest build tag b12110 (commit `cd959bae99ff`, the same commit
  as tag v0.9.0); b12104 through b12108 do not exist; 280 build tags strictly above b11755 (the
  relation register records 278 at its own read). The register's `newest=b12103` and `newer=278` are
  therefore a **dated observation**, not a defect — exactly the round's thesis, seen live.
- The README bytes are identical at b12103, b12110 and v0.9.0 (sha256 `eafc1b53…a137`, 136429 bytes,
  2620 lines, quote at line 482 in all three), so the register's staleness changes no held statement.
- Wording check on `corpus/knowledge/pin-recheck-trigger.md` (not my file, not edited): its sentence
  "The release gap of 348 tags" uses the build-number delta (12103 minus 11755), while the register's
  `newer=278` and the receipt's count of build tags above b11755 are both 278 (numbers are skipped,
  e.g. b12104–b12108). The tag count is 278; 348 is the number delta.

## Filing map (recommended, append-only)

1. Keep the filed S563 and S564 unchanged.
2. Keep the filed S565 (rejected SGLang README) unchanged; it is already cited in
   `corpus/lessons/round-82.md` §Gate and the registry is append-only by id.
3. File the mined SGLang native_api row at **S566** and the rejected llama.cpp release-note row at
   **S567**; the lesson §Gate table then needs the two extra rows (`S566` mined, `S567` rejected).
   If the L1 instead wants the dispatch's numbering, the only faithful route is to supersede the
   filed S565, which would break the lesson's citation and the append-only convention — not
   recommended.

## Independent evidence behind the cells

- S563 and S564 sha256 values recomputed by this seat with `sha256sum` over its own `curl` output;
  both match the filed registry rows and the lesson §Gate table.
- `diff -u` between S564 and S563 is 15 hunks (exit 1, differences found); the health heading is
  context in the diff and the anchored sentence is unchanged.
- The `### GET /health` heading wording located: "### GET /health: Returns health check result".
- S565 was diffed against the same page at the lane's SGLang pin v0.5.22 (sha256
  `209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb`, 17359 bytes, 467 lines):
  the only health-section change is the two added bullets (`/ready`, `/ping`).
- S566 rendered text was extracted from the fetched HTML after stripping scripts, styles and tags;
  `opencl` appears in the release title and two bullets, and `/health`, `/v1/models` and `GET /`
  each count 0.
