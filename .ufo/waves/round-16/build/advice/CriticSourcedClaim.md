# CriticSourcedClaim — round 16 build, advice only (not a verdict)

Attack target: C1's sourced-claim basis (new SOURCES rows for llama.cpp README + `server-http.cpp` at b11755; S001 sufficiency; Gate quote content).
Axes: calibration (primary), operability (secondary: C2 live capture as the binary↔source link).
Sources opened 2026-10-20 (read-only raw GETs into /tmp, nothing written in the lane except this file):
- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/{README.md,server-http.cpp,server.cpp,server-context.cpp,server-models.cpp}`
- README @ c0fd7862 (S001 anchor), README/server-http.cpp @ master, README @ tags b11000/b10000/b9000.
- sha256: README@704366d `714c067b…6a37` (= master today); server-http.cpp@704366d `24ede172…5fdb` (= master today); README@c0fd786 `ad0dbc02…ca23`.
- `git ls-remote … refs/tags/b11755` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad refs/tags/b11755`.
- `~/.local/bin/llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`.
No installs.

## Finding 1 — S001 alone does not ground C1. Its `/v1/models` text points the other way.

**Counterexample.** The probe classifies `GET /v1/models`. The README documents the 503 envelope only under `/health`. Its `/v1/models` section implies the route answers during load:
- README@704366d:1258: "The `meta` field can be `null` (for example, while the model is still loading)." This sentence is identical at b9000, b10000, b11000 and c0fd786.
- The code at the same commit contradicts it. `get_res_model_info` always emits a `meta` object (server-context.cpp:5183 `{"meta",     {`), and the state middleware blocks the route before any handler runs (see F2).
- The lane has already used this README sentence to admit the opposite claim. `corpus/knowledge/served-identity-crosswalk.md:33`: "the documented list always has one element and `meta` can be `null` 'for example, while the model is still loading'". Line 52: "on llama.cpp single-model it can even be observed mid-load". Line 63: "on llama.cpp single-model it can be observed before loading completes (S001)". `runtime-health-surface-matrix.md:55` says the same: "documents nullable `/v1/models` `meta` while loading".

**Why S001 fails KQ13** (`corpus/QUALITY.md:40`: "Each documented field or route is supported by the cited source's actual section"): S001's `/v1/models` section does not say 503, and its `/health` section is about a different route. S001 is also anchored at c0fd7862, which is 41 commits behind 704366d76 (GitHub compare: `ahead 41 0`). Its URL is `blob/master`, which keeps moving. The `/health` text matches b11755 byte-for-byte (the README diff touches only four flag-table lines, 210–240), so S001 can corroborate. It cannot be the sole support.

**Impacted axes:** calibration. If C1 lands without a correction, the corpus holds two contradictory authorities: the crosswalk says /v1/models can answer mid-load, and the new probe verdict says it returns 503 mid-load.

**Smallest correction:**
- (a) Ground the `/v1/models` 503 on the code row (F2). Do not ground it on any README row.
- (b) Append a correction paragraph to `served-identity-crosswalk.md` and `runtime-health-surface-matrix.md`, following KQ7/KQ14 append-only rules. At b11755 single-model, `/v1/models` returns the 503 envelope until `is_ready`. The README's null-`meta` sentence diverges from code at the same commit. The round-11 "observable mid-load" inference is withdrawn for single-model b11755.
- (c) [INFERENCE] I did not check code at older tags, so call this a README/code divergence, not a version change.

## Finding 2 — a version-pinned code row is tier A, but only for "what this commit's single-model server does pre-ready". It is not tier A for "what this binary returns".

**Tier rule.** CORPUS.md:93-94 lists "source code" as tier A, scoped to `scope` ("never global"). The lane's own flip text accepts tagged code: SOURCES.md:39 (S027) says "flip: versioned first-party documentation or tagged code defines the native route". So `kind code, tier A` is honest when the scope is narrow.

**What the code grounds:**
- **Envelope and coverage.** server-http.cpp:312 `// no endpoints are allowed to be accessed when the server is not ready`. Lines 318–320: `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`. Only frontend assets are exempt (309: `if (frontend_paths.count(req.path)) {`).
- **Coverage of every route.** The middleware runs in the pre-routing handler for every non-OPTIONS request: 354 `if (!middleware_server_state(req, res)) {`.
- **Ordering.** The state check runs before the API-key check (357 `if (!middleware_validate_api_key(req, res)) {`). With `--api-key`, a loading server still answers 503 rather than 401. [INFERENCE] MODEL_LOADING precedes UNAUTHORIZED_SERVICE during load. Worth one matrix row.
- **"While loading" needs server.cpp, not server-http.cpp.**
  - server.cpp:493: "start the HTTP server before loading the model to be able to serve /health requests".
  - `is_ready.store(true)` at 515 runs only after `load_model` (507) and `routes.update_meta` (514).
  - server-http.cpp alone shows "not ready", not "loading".

**Counterexamples that must stay outside the row's scope:**
- **Router mode.** server.cpp:460 `ctx_http.is_ready.store(true);` runs before `load_startup_models()` at 472. A router-mode server that is loading a model does not serve this envelope from its own middleware. The scope must say single-model (`-m`) mode.
- **Sleeping.** server-context.cpp:5728-5730 serves `cached_models` with 200 while `queue_tasks.is_sleeping()`. Sleeping is not loading.
- **The binary.** Code is authority for commit 704366d76. Linking it to the installed binary takes two steps: tag→commit (`git ls-remote`, above) and binary→commit (`--version`, above). [INFERENCE] Equivalence beyond the version string is unproven until C2's live capture. Only the lane's re-runnable capture can carry "this binary returned X at time T". CORPUS.md:94 lists "the lane's own re-runnable gate output" as tier A. KQ6 (`QUALITY.md:28`) rejects "A documentation claim … written as a present local-runtime fact".

**Province note.** The round-10 ruling covered "the lane's own registered local endpoints" (SCORECARD.md:220; lessons/round-10-verifier-spotcheck.md:17). A lane-owned ephemeral server on an unregistered port is not named in that ruling. [INFERENCE] It is in-province, because the documentation-only rule "targeted external live targets". L1 should record that reasoning explicitly so S030's contest does not repeat.

**Smallest correction (rows, append-only):**
1. **server-http.cpp row.** `code | A`.
   - URL pinned: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp`.
   - scope: "llama.cpp b11755 (704366d76) single-model llama-server: response to non-frontend, non-OPTIONS requests while `is_ready` is false".
   - anchor: `middleware_server_state` 307–328 and pre-routing order 354–359.
2. **server.cpp row.** `code | A`, anchored at 493–515, to ground "is_ready flips only after load_model". Alternatively, mark that link `[INFERENCE]` in row 1's teaches. A second cheap row is better than an unsourced bridge.
3. **README@704366d row.** Only if wanted for corroboration.
   - URL pinned to the commit. A different URL from S001's `blob/master` avoids a second W04 duplicate-URL warning (`sources-before-validate.txt:1` already warns about S031).
   - scope: `/health` load-state documentation only.
   - teaches should note the null-`meta` divergence at README:1258.
   - Do not mark it "supersedes S001": S001 is not wrong about `/health`.
4. **Live capture.** Make it an own-work row only if the capture file is committed and the harness re-runs. Scope: "one dated run of `~/.local/opt/llama-b11755` (build 11755, commit 704366d76), lane-owned unregistered loopback port". Recheck: every round.

## Finding 3 — Gate quote content (CORPUS.md:113-114: "URL, the access date, and a ≤25-word quote with its location grounding `teaches`")

Every Gate quote must be copied from the source bytes, not from the C1 context paraphrase.

**False-provenance trap.** The C1 context renders the body as `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`. The README's actual bytes use the order code→message→type, with spaces. [INFERENCE] The code serializes a nlohmann `json` object with sorted keys, so the wire order is also `code, message, type`. A Gate line quoting the context string as "README:486" would be a misquote. The matcher compares parsed values, so key order is irrelevant to C1's logic. It is relevant to quote fidelity.

**Required Gate content per new row:**

- **server-http.cpp@704366d** (accessed 2026-10-20; record the raw sha256 `24ede172…5fdb` for non-author re-open):
  - 312+318–320 (19 words): `// no endpoints are allowed to be accessed when the server is not ready … {"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`
  - Add a located note for 309 (frontend exemption) and 354 vs 357 (state check before API key). These ground "every non-frontend path" and the `--api-key` behaviour.
- **server.cpp@704366d** (if used): 493 (17 words): `// start the HTTP server before loading the model to be able to serve /health requests`. Add located lines 507/515 (`load_model` then `is_ready.store(true)`).
- **README@704366d** (accessed 2026-10-20; sha256 `714c067b…6a37`):
  - 486 (8 words, verbatim): `Body: \`{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}\``
  - 487: `Explanation: the model is still being loaded.`
  - The Gate must also record README:1258's contrary `/v1/models` sentence as a known limitation. A Gate that quotes only `/health` while the README contradicts the probed route is selective quoting.
- **Release link** (Gate prose; already covered by the release-scout row if one is added): tag `b11755` → `704366d76f87…` (ls-remote), and binary `--version` "build 11755, commit 704366d76". Record both, otherwise the code rows do not attach to the installed binary.
- **Each quote's location** needs file and line plus commit, per CORPUS.md:42: "A quote names its location". State whether it is a code comment or code. Line 312 is a comment, not behaviour; the behaviour is at 314–325.

## Not defects (tradeoffs L1 may accept)
- One code row instead of two is fine if the `is_ready`-after-load bridge is marked `[INFERENCE]` in teaches.
- S001 is fine as a cited corroborator for `/health`. It needs no in-place edit; its `recheck: on-release` and `used-by` may gain this round's paths, logged old→new.

## Limitations
- I read code only at 704366d76 (plus README at b9000/b10000/b11000). I did not check envelope stability in older `server-http.cpp` or `examples/server/server.cpp`.
- The GitHub REST tag endpoint returned a non-JSON body (likely rate limit). The tag→commit link comes from `git ls-remote` only.
- I did not view or rerun the L1 smoke capture. Statements about it come from the assignment context, not from me.
