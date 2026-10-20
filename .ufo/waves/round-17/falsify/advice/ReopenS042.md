VERDICT: confirm — all eleven S042 cells and the lesson Gate quote resolve against the pinned bytes (b11757 identity independently reproduced); two precision notes, no falsehood.

# What I attacked

SOURCES row S042 at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:54`
(row sha256 `81ce6c56fa79cb77be7193b0d6a0180b333d1f6df281584892a0361e4b981574`, 938 bytes;
identical at lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` and in the working tree),
the Gate row that admits it (`corpus/lessons/round-17.md:60`, line sha256 `5ceddb2a…8ec9`),
and both `used-by` citation sites. Bytes were re-read from the lane's pinned copy and
re-fetched from GitHub at the pinned commit and at b11757; nothing was run in the lane.

Source under test: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`
(pinned copy sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, 264205 bytes).

# Cell-by-cell

| Cell | Verdict | Evidence |
|---|---|---|
| `id` S042 | agree | 46 registry rows, 0 duplicate ids (contract census below); a `S042` text search of `corpus/SOURCES.md` matches only row line 54 and the prose supplement at :164. |
| `source` | agree | Blob URL returns HTTP 200. Title names the file the URL serves (`server-context.cpp`, the `get_health` handler). `git ls-remote --tags` returns `refs/tags/b11755` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, so "(release b11755)" is exact. |
| `kind` = `code` | agree | C++ upstream source; `code` is in the contract enum (`/home/vgpnk/Projects/shokunin/CORPUS.md:86-87`). |
| `tier` = A for this `scope` | agree | Contract: A includes "source code", scoped and never global (`CORPUS.md:91-93`). Scope is one handler's emitted body at one commit — no tier inflation. |
| `scope` | agree, one conservative exclusion | Exclusions are honest, and S036's pointer is right (`corpus/SOURCES.md:48` "Every non-frontend path, `/v1/models` and `/health` included, answers 503"). NOTE P1: "not router" is narrower than the code — the same lambda serves router mode. |
| `anchor` — `get_health` 5288-5299 | agree | `server-context.cpp:5288` "this->get_health = [this](const server_http_req &) {" through `:5299` "};"; body literal at `:5297` "res->ok({{"status", "ok"}});" — both match the lane's `pins.json` span `health_handler_body`. |
| `anchor` — `ok()` 4868-4871 | agree | `:4868` "void ok(const json & response_data) {", `:4869` "status = 200;", `:4870` "data = safe_json_to_str(response_data);", `:4871` "}". NOTE P2 on "compact". |
| `anchor` — raw sha256 / b11757 identity | agree | `sha256sum` of the pinned file and of a fresh fetch at `13786fbb` both give `dd1de0f2…c2329`, 264205 bytes; `refs/tags/b11757` = `13786fbb3a1aaf4ff445c0b92d9f21cbe0af6d42`. NOTE P4 (evidence sits in wave advice, not `pins.json`). |
| `teaches` | agree | Single 200 path: the lambda's only `res->ok` is `:5297`; `ex_wrapper`'s exception path sets `res->status = 500;` (`server.cpp:80`), so no other 200 body descends from this handler. Comment verbatim at `:5289` "error and loading states are handled by middleware". `{"status":"ok"}` is 15 bytes and hashes `a29ee2b1…d288`, equal to every receipt's `captures.health.body_sha256` and its `Content-Length: 15` (`.ufo/waves/round-17/live/receipt-1.json:22-30`); README:489 is the spaced `{"status": "ok" }`. |
| `status` = `mined` | agree | Cited by both `used-by` paths; `mined` requires ≥1 (`CORPUS.md:103-104`). |
| `opened` = 2026-10-20 | agree | Gate preamble `corpus/lessons/round-17.md:56` "All sources opened 2026-10-20."; the row is new in the round-17 diff (20 insertions, 0 deletions). |
| `recheck` = `on-release` | agree | Symbolic cadence is allowed (`CORPUS.md:106`); apt for a commit pinned by release tag. |
| `used-by` | agree | `corpus/knowledge/llamacpp-loading-lifecycle.md:152` "source S042" and `:164` "(S042, server-context.cpp:5297)"; `corpus/lessons/round-17.md:38`, `:60`, `:74`, `:77`. Both files exist; E11 clean. `corpus/README.md:238` also names S042 but is the coverage map, not a knowledge entry or lesson, and existing rows (S035–S041) likewise omit it — correctly excluded under `CORPUS.md:107-108` [INFERENCE on the contract reading]. |

# Lesson `## Gate` quote

Agree. `corpus/lessons/round-17.md:60` carries the row URL, the Gate preamble's access
date, and two located quotes: the comment "error and loading states are handled by
middleware" (8 words, ≤25, verbatim at `server-context.cpp:5289`) and the code literal
`res->ok({{"status", "ok"}});` at `:5297`. It grounds both halves of `teaches`
(the 200 body and the middleware split). The neighbouring reject row (README bytes)
correctly cites `{"status": "ok" }` from `README:489`.

# Precision notes (no cell is false)

- **P1 — scope's "not router" is conservative, and the Gate sentence is broader than the scope.**
  `server-context.cpp:5154-5159` runs `init_routes()` in the `server_routes` constructor
  unconditionally, and `server.cpp:241` says "// note: routes.get_health stays the same"
  while the router branch proxies the other routes; the shared registration is
  `server.cpp:278-279` ("public endpoint (no API key check)"), and router mode stores
  readiness at `server.cpp:460`. So the same handler, hence the same body, exists in router
  mode too — the row's exclusion under-claims rather than misstates. The Gate sentence has
  no mode qualifier; S042 as scoped grounds it for single-model only. **No measurement is
  affected**: the live runs are single-model. Router-side 200 body is [INFERENCE] from code;
  I ran no router.
- **P2 — "compact JSON" is not resolvable from 4868-4871 alone.** Those lines show
  `data = safe_json_to_str(response_data);`; compactness comes from
  `safe_json_to_str` = `data.dump_safe()` (`tools/server/server-common.cpp:1695-1697`) whose
  default is `dump_safe(int indent = -1)` (`common/json.h:265`, fetched at 704366d76).
  The anchor does not name those locations, but the property is independently observed:
  the 15-byte body and its sha256 match three live receipts. [OBSERVED via receipt; code
  chain read]
- **P3 — the "so any other 200 body" clause is entailed by the single `res->ok` branch,
  not by the middleware comment.** The comment grounds only that loading/error are
  middleware-handled; the conclusion is still true (`ex_wrapper` returns 500 on exception,
  `server.cpp:79-90`).
- **P4 — the b11757 byte-identity evidence is wave advice, not a pinned artifact.**
  `build/advice/ScoutLlamaNewerReleases.md:40-46` records the three digests "both revisions";
  `.ufo/waves/round-17/sources/pins.json` pins only 704366d76. I re-fetched
  `server-context.cpp` at `13786fbb` and reproduced the digest, so the cell is reproducible
  today; it is not covered by the lane's own pin evidence.

# Cross-checks run in `/tmp/ReopenS042-clone` (checkout `54a29268e…`)

- Census (`CORPUS.md:130-147`): rows 46, malformed 0, tier A=43 C=3, status mined=36
  queued=5 rejected=5; no invalid kind/tier/status; no duplicate ids; no missing `used-by` path.
- `bash scripts/sources-census.sh validate --file … --today 2026-10-20` → `file ok`, exit 0,
  only the pre-existing W04 for S031 and the documented W04 for S043 (shared URL with S037).
  No E-codes; S042 is not flagged.
- `python3 tools/sources-append-only.py --from cff9e62 --to 54a29268…` → `added S042 (allowed)`
  … `no append-only violations`, exit 0.
- `git diff --numstat cff9e62 54a29268… -- corpus/SOURCES.md` → `20 0`; the only removed line
  in `-U0` output is the `--- a/corpus/SOURCES.md` header, so no existing cell moved.

# Commands (all exit 0 unless shown)

- `sha256sum server-context.cpp server.cpp` (pinned dir) → `dd1de0f2…c2329`, `21439622…5aef4`.
- `curl -sS https://raw.githubusercontent.com/ggml-org/llama.cpp/13786fbb…/tools/server/server-context.cpp` → `http=200 bytes=264205`; `sha256sum` → `dd1de0f2…c2329`.
- `curl -o /dev/null -w '%{http_code}'` on both blob URLs → `200`.
- `curl …/704366d76…/common/json.h` → `http=200`; `grep dump_safe` → `dump_safe(int indent = -1)`.
- `git ls-remote --tags https://github.com/ggml-org/llama.cpp b11755 b11757` → the two refs above.
- `printf '%s' '{"status":"ok"}' | wc -c` → 15; `| sha256sum` → `a29ee2b1…d288`.
- `git clone … && git checkout 54a29268…` → HEAD `54a2926`, clean.
- census commands above; `python3 tools/sources-append-only.py …`; `bash scripts/sources-census.sh validate …`; `git diff` checks.
- Read-only lane reads: `corpus/SOURCES.md`, `corpus/lessons/round-17.md`,
  `corpus/knowledge/llamacpp-loading-lifecycle.md`, `corpus/README.md`,
  `.ufo/waves/round-17/sources/{pins.json,llama.cpp-704366d76/…}`,
  `.ufo/waves/round-17/live/receipt-{1,2,3}.json`, `build/advice/ScoutLlamaNewerReleases.md`.

# Limitations

- No llama-server was started and no port bound; the 15-byte wire body is taken from the
  existing v2 receipts, not a new run. Live behaviour is other seats' ground.
- I did not re-run the C1/C2 harnesses or `check.py`; only the S042 source row, its Gate
  quote and its citations were attacked.
- Router-mode `/health` is code-read only ([INFERENCE]); no router process was launched.
- GitHub blob HTML was checked only by status code; line numbers were verified against the
  pinned raw bytes and `pins.json`, not the rendered page.
- The fleet census script was run read-only with `--file` against the clone; the lane's
  `sources-census.sh` is fleet-owned and lives at `/home/vgpnk/Projects/shokunin/scripts/`.

# Installs

None. No tool was installed or upgraded; no pacman transaction attempted.

Scratch `/tmp/ReopenS042-*` is removed; no lane file other than this Report was written.
