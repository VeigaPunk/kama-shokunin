# Round-93 lesson `## Gate` — S600–S603 (candidate, SB01LessonDraft)

Read at lane tip `54b8578f0effa249596947bfc1081da902dc4bec` (2026-11-06 23:56 -03). The landed Gate in
`corpus/lessons/round-93.md` (added at `4854ce04`, unchanged at this tip) is correct for the four new rows; this draft is the independently
re-opened block plus two corrections the landed text needs: the re-opened row's **range caveat** and the
`server-models-sched.cpp` reject's **open-receipt gap**.

## Independent re-open (this seat, 2026-11-07T02:47–02:52Z = 2026-11-06 23:47–23:52 -03)

`curl -sfL --max-time 60 https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>` for each file;
`sha256sum` of the fetched bytes. Read-only GET; no credentials; nothing written outside this out dir.

| file | sha256 of fetched bytes | lines | equals |
|---|---|---|---|
| `common/http.h` | `949e44f9c592d1f894818765d8bf433e3cfd183430696464e4965447643d2de1` | 332 | `sources-opened.out`, SOURCES S600 |
| `tools/server/server-connect.cpp` | `2a505b295d649e6e0e70840d0f949a66b06d18269282294e5fb804e0460cc9df` | 297 | `sources-opened.out`, S601 |
| `tools/server/server-http.h` | `29c53f7ffde226edf3e6f48463e4807f7e554ca12e476099f90e0ff18142978d` | 117 | `sources-opened.out`, S602 |
| `tools/server/server-models.h` | `304c013601e1a5abfc9bcc42173b3ec2db23e65e065a8249532c4ddda6a5a6a1` | 465 | `sources-opened.out`, S603 |

Quotes re-read verbatim (1-based lines; surrounding whitespace stripped):

- **S600** line 324 `int port = ntohs(serv_addr.sin_port);`; line 301 `serv_addr.sin_port = htons(0);`;
  lines 90/92/94 `parts.port = std::stoi(port_str);` / `parts.port = 80;` / `parts.port = 443;` (client URL parser);
  `common_http_get_free_port()` begins line 274.
- **S601** line 208 `"--port", std::to_string(port),` inside `server_connect::start` (line 194); the caller is
  `server.cpp:341` `connect_proc.start(params, ctx_http.port)`.
- **S602** line 92 `int port    = 9931;` inside `struct server_http_context` (line 67); `init()` is
  `server-http.cpp:112-125` (`port = params.port;` line 116); `start()` binds at 494-515 (`port = bound_port;` 512);
  `server.cpp:482` calls `init` before `server.cpp:557` calls `start`.
- **S603** line 80 `int port = 0;` inside `struct server_model_meta` (line 74); set by
  `server-models.cpp:1218` `inst.meta.port = common_http_get_free_port();`.
- **S596** line 4613 `params.port = 8011;` (re-opened row's located quote), sha256 `c69c0e07…6f67`.

## Gate (paste-ready)

Rows opened by the L1 (`curl -sfL --max-time 60`, receipt `.ufo/waves/round-93/controls/sources-opened.out`, fetched
2026-11-07T02:33:36Z = 2026-11-06 23:33 -03; the new rows carry the UTC date 2026-11-07). This seat re-opened
S600–S603 independently at 2026-11-07T02:47–02:52Z; every digest below equals the fetched bytes, the receipt's second
column and the archive member. Each quote is verbatim at the cited line.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S600 llama.cpp `common/http.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/http.h — 2026-11-07 UTC, sha256 `949e44f9c592d1f894818765d8bf433e3cfd183430696464e4965447643d2de1` | `int port = ntohs(serv_addr.sin_port);` (line 324; the socket is bound to port 0 at line 301) | Grounds P27–P30: the free-port helper a router uses for children, and three client-side URL lines that are not a listen port. |
| S601 llama.cpp `tools/server/server-connect.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-connect.cpp — 2026-11-07 UTC, sha256 `2a505b295d649e6e0e70840d0f949a66b06d18269282294e5fb804e0460cc9df` | `"--port", std::to_string(port),` (line 208, inside `server_connect::start`) | Grounds P31: `--connect` passes the bound port (`server.cpp:341`) to a separate binary and sets no port in llama-server. |
| S602 llama.cpp `tools/server/server-http.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.h — 2026-11-07 UTC, sha256 `29c53f7ffde226edf3e6f48463e4807f7e554ca12e476099f90e0ff18142978d` | `int port    = 9931;` (line 92, member of `server_http_context`) | Grounds P38: a second 9931 that `init()` overwrites (S598 line 116) before any bind (`start()`, line 512). |
| S603 llama.cpp `tools/server/server-models.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.h — 2026-11-07 UTC, sha256 `304c013601e1a5abfc9bcc42173b3ec2db23e65e065a8249532c4ddda6a5a6a1` | `int port = 0;` (line 80, member of `server_model_meta`) | Grounds P46: the router's per-model port before spawn (S599 line 1218). |
| S593, S596–S599 @ `b12177` | **re-opened**, admitted for the P-rows that cite them, **with the range caveat below** | the rows' URLs — 2026-11-07 UTC, digests equal (`sources-opened.out`); `params.port = 8011;` (S596 line 4613) | The rows' quotes are in `corpus/lessons/round-92.md` §Gate; this round's re-fetch equals each row's digest. | Every P-row's text cell is the archive line byte for byte (`measured/c2.out` B2). **Caveat:** the anchor ranges are narrower than the P-rows' cited lines — see below. |
| `tools/server/server-models-sched.cpp` line 423 as a listen-port setter | **reject** (names another port) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models-sched.cpp — 2026-11-07 UTC; fetched this seat, sha256 `b786ea0917ec1d9578c273b6f3930cf9ba90865be7878c18d6337d2f1cfdd54a` | `child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT) + "=" + std::to_string(models.base_params.port));` (line 423) | It hands the **router's** port to a measure child's environment; the child's listen port is set by S599 lines 316/1218 (P41, P43). Not in the frozen population (no `POP_RE` token). Flip: a later pin reads `SERVER_ENV_ROUTER_PORT` as the child's listen port. |
| The codeload archive itself as a SOURCES row | **reject** (input, not a teaching source) | https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 — 2026-11-07 UTC, sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` | n/a (binary archive) | The archive is the counter's pinned population input (`TARBALL_SHA256` in `tools/round93-setter-rows.py`); what kama learns is cited per file through the raw rows above, whose digests equal the archive members. Flip: GitHub stops serving per-file raw URLs for the tag. |

`status` / `recheck` / `used-by` changes on existing rows: none. Verified this seat: the five-row block
S593/S596–S599 has the same digest at base `5af79495` and tip `54b8578f`
(`e7b4e92a…7c07be`), so the rows are byte-identical, and `sources-census.sh validate` exits 0 (`kama ok`; W04
duplicates only). S600–S603 are new rows (`mined`, recheck `on-release`, used-by `SKILL.md`).

### Gate corrections (the two defects in the landed text)

1. **Range caveat (DEFECT, `RV02SetterRows.md` DEFECT-3).** The re-opened row is admitted "for the P-rows that cite
   them", but three rows' anchor cells do not cover the lines this round cites:
   - S596 anchor `per-example defaults lines 1365-1380 and option lambdas (--parallel 2514-2522, --timeout
     3559-3565)`; P08–P24 cite 3318–4764, and P05–P07 cite 2526–2531 (outside 2514–2522).
   - S598 anchor `lines 93-125`; P37 cites 512.
   - S599 anchor `lines 1218-1235`; P39–P45 cite 69, 90, 316, 866, 1292, 2157.
   S593 (464–705) covers P25/P26 and S597 (115–131) covers P47/P48. The digest is whole-file, so the bytes read are
   the same; the *range cell* is stale. KQ22 forbids an in-place anchor edit: add a new row for the later ranges, or
   state the limitation in the Gate. Do not read the row as a per-line anchor.
2. **Open-receipt gap (NOTE).** The `server-models-sched.cpp` reject is quoted verbatim (line 423, verified), but the
   file is not in `controls/sources-opened.out` (nine files, raw URLs only). The lesson says "read in the archive
   2026-11-07 UTC"; either add a raw-URL open line for it or mark the provenance "archive read, no raw digest". K3
   does not fire (the reject cites no S-id), but a reader cannot re-derive the quote from the receipt set.

### Rejects verified, unchanged

- `server-models-sched.cpp:423` quote verified verbatim; the consumer (`SERVER_ENV_CHILD_ROLE=SERVER_ROLE_MEASURE`
  at line 424, `create(child_args, …, child_env)` at 427) is a measure child, and `child_args` carry the model's
  rendered args (which include the `LLAMA_ARG_PORT` of P41) — the env var is not the child's listen port.
- The codeload reject's digest is the counter's pinned `TARBALL_SHA256` (equal, checked in `measured/c2.out`).
