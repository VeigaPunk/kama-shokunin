VERDICT: partial — `tools/kama-probe.sh` diff 20e392e..b8e485c (C1 calibration). Every one of the 9 hunks is MODEL_LOADING-scoped with no unrelated churn, the vocabulary is consistent in all four enumerations plus the listeners case, and the body-shape-only wording matches the matcher exactly. Two wording claims are wider than the code supports: "Drift (exit 2)" is true only for `check`/`snapshot` (`listeners` and `consumers` return 0 on MODEL_LOADING), and the absolute "Router mode never emits it" has a sub-millisecond startup window in the pinned source. No functional defect found.

# ReviewProbeDiff — C1 probe hunk scoping and vocabulary consistency

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD `b8e485c` (`b8e485cc6b201c8e4604a20808e58babbfe08e34`), base `20e392e`. Read-only; only this report and `/tmp/kama-r16-ReviewProbeDiff/` (removed) were written.

## Axes named

- **A1 scope** — does each hunk exist only to introduce/consume MODEL_LOADING?
- **A2 wording fidelity** — does the prose claim exactly what the code does?
- **A3 vocabulary consistency** — header / usage / `VOCAB` / listeners counters / baseline whitelist / registry comment.
- **A4 no-harm reproducibility** — matrix, near-miss fall-through, python3-absent fallback, snapshot round-trip.

## What I ran (cwd = lane root unless noted)

| # | Command | Exit | Result excerpt |
|---|---|---|---|
| 1 | `git diff 20e392e b8e485c -- tools/kama-probe.sh` | 0 | 130 diff lines, **9 hunks**, `52 insertions(+), 8 deletions(-)` |
| 2 | `git show 20e392e:tools/kama-probe.sh \| sha256sum`; `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh` | 0 | both `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` — the frozen before-arm is byte-identical to the pre-image |
| 3 | `bash -n tools/kama-probe.sh`; `shellcheck -S warning tools/kama-probe.sh`; `git diff --check 20e392e b8e485c -- tools/kama-probe.sh tools/test-snapshot.sh` | 0 / 0 / 0 | clean |
| 4 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/.../current.json` | 0 | `tests=72 passes=72 failures=0` |
| 5 | Python census of `tests/probe-verdicts/*.json` | 0 | 9 families, 72 rows, expected verdicts `{FOREIGN_SERVICE 37, MODEL_LOADING 17, MODEL_OK 8, UNAUTHORIZED_SERVICE 5, MODEL_MISMATCH 3, DEAD 1, NOT_HTTP 1}` |
| 6 | Local stub (`python3 http.server`, ephemeral port 34797) serving the **exact** envelope on every path; `bash tools/kama-probe.sh check --port 34797 --expect '*' --json` | **2** | `verdict=MODEL_LOADING reason=llamacpp-loading drift=True summary={'registry_rows_evaluated':1,'model_ok':0,'drift':1,'exit':2}` |
| 7 | same stub; `bash tools/kama-probe.sh listeners --port 34797 --json` | **0** | row `MODEL_LOADING/llamacpp-loading`; `summary={'probed':1,'model_endpoints':0,'foreign_service':0,'unauthorized_service':0,'dead':0,'not_http':0,'model_loading':1}` (sum = probed) |
| 8 | stub with `"code":"503"`; `check --port 33679 --expect '*' --json` | 2 | `FOREIGN_SERVICE / non-2xx-non-model-http`, drift true — near-miss falls through unchanged |
| 9 | Copy of the probe with `HAVE_PY` forced 0 (`sed` on the tmp copy); exact-envelope stub, port 46441 | 2 | `FOREIGN_SERVICE / non-2xx-non-model-http` — the documented fail-closed branch |
| 10 | Extracted `body_is_llamacpp_loading` from the current file and ran it over 8 fixtures | 0 | `exact rc=0`, `extra rc=0`; `array/bool/code404/float/str/type` all `rc=1` |
| 11 | Stub + one-row /tmp registry (no lane registry/history); `snapshot --registry … --history /tmp/…` twice | 2 / 2 | `latest.tsv`: `probe-stub MODEL_LOADING llamacpp-loading - 42473 yes`; run 2: `rows=1 model_ok=0 drift=1 transitions=0 exit=2`, **0** "malformed" lines |
| 12 | same stub; `bash tools/kama-probe.sh consumers --registry … --json` | **0** | `verdict=MODEL_LOADING reason=llamacpp-loading summary={… 'exit': 0}` |
| 13 | Python token compare of header bullet, `verdicts:` usage line, `VOCAB` | 0 | all three = `[MODEL_OK, MODEL_MISMATCH, FOREIGN_SERVICE, UNAUTHORIZED_SERVICE, DEAD, NOT_HTTP, MODEL_LOADING]` (`header==VOCAB: True`, `usage==VOCAB: True`) |
| 14 | Teardown checks: `pgrep -af 'stub/stub.py'`; `ss -ltn` filtered to 42473/46441/34797/33679; `pgrep -x llama-server` | 1 / empty / 1 | no stub, no listener, **no llama-server**; I started none |
| 15 | Reads (no execution): pinned `sources/llama.cpp-704366d/server-http.cpp:307-328,354-358`, `server.cpp:269,283-284,452-460,490-517`, `sources/pins.json` | — | quoted below |

No `measure.py` (forbidden). No full `listeners` scan (it would probe 8080/34113); only `--port` mode. No llama-server started.

## 1. Hunk inventory — CONFIRM, every hunk is MODEL_LOADING-scoped

| # | Location (current file) | Change | Scoped? |
|---|---|---|---|
| 1 | `tools/kama-probe.sh:27-36` | header bullet + MODEL_LOADING paragraph | yes — doc of the new verdict only |
| 2 | `:62` | `VOCAB` gains `MODEL_LOADING` | yes |
| 3 | `:117` | `verdicts:` usage line gains it | yes |
| 4 | `:420-448` | new `body_is_llamacpp_loading()` (comment + python) | yes |
| 5 | `:503-508` | new 503 gate in `classify`, after 401/403, before HTML/2xx | yes |
| 6 | `:723` + `:733` | `n_loading` local + `MODEL_LOADING)` counter | yes |
| 7 | `:743-744` | listeners JSON summary gains `"model_loading": %s` | yes — integration of the new verdict |
| 8 | `:748-749` | listeners text summary gains `model_loading=%s` | yes |
| 9 | `:939` | `diff_baseline` baseline-verdict whitelist gains `MODEL_LOADING` | yes — required for the new verdict to survive a snapshot round-trip |

The 8 deletions are exactly the 8 replaced lines (no formatting churn, no refactor, no unrelated comment). `git diff --check` clean.

## 2. Wording audit

| Claim (current file) | Evidence | Status |
|---|---|---|
| `:32-34` "GET /v1/models answered 503 with the exact … envelope" | `:503` `[ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading`; run 6 | **confirm** |
| `:34` "(b11755 tools/server/server-http.cpp:307-328)" | `sources/pins.json` locates the block `start 307 end 328`; pinned `server-http.cpp:307-328` is `middleware_server_state` | **confirm** (exact) |
| `:35` "A body-shape match only — runtime identity and served model are unverified" | matcher reads only `doc["error"]`; no `Server`/Content-Type/runtime input; `C_SERVED` stays `-` (snapshot `latest.tsv` shows `served_model=-`); matrix rows `no-server-header`, `plain-json-content-type`, `exact-envelope-labelled-html` all pass | **confirm** |
| `:36` "requires python3 (without it the body keeps FOREIGN_SERVICE)" | run 9: forced `HAVE_PY=0` → `FOREIGN_SERVICE / non-2xx-non-model-http` | **confirm** |
| `:423-425` "any deviation (… code as string or float, non-503 status) falls through" | run 10 (string/float/bool/code 404/wrong type → rc 1) + 31 near-miss rows in the matrix | **confirm** |
| `:421` "while is_ready is false every non-frontend path returns 503" | pinned `server-http.cpp:308-325`: `frontend_paths` bypass, else `res.status = 503` + exact body | **confirm** |
| `:35` "Drift (exit 2): not ready" | `check`/`snapshot` exit 2 (runs 6, 11); **`listeners` exit 0** (run 7), **`consumers` exit 0** (run 12) | **partial** → F1 |
| `:35-36` "Router mode never emits it" | pinned `server.cpp:455-460`: `ctx_http.start()` returns with listeners accepting, **then** `is_ready.store(true)` | **partial** → F2 (info) |

## 3. Vocabulary consistency — CONFIRM

- `VOCAB`, the header bullet and the `verdicts:` usage line are token-identical (run 13), same order, new token appended last.
- `cmd_listeners` switches on all 7 verdicts; the only verdict enumeration that lacked a counter is the one the diff adds (`:733`). Buckets sum to `probed` in run 7.
- `diff_baseline`'s hardcoded whitelist (`:939`) accepts `MODEL_LOADING` and still drops `MODEL_LOADED` — demonstrated by the seeded `latest.tsv` in `tools/test-snapshot.sh:162-180` and by my run 11 (no `malformed-row-dropped`, `transitions=0` on the second run).
- `registry/endpoint-consumers.tsv:32` appends `| MODEL_LOADING`; `read_registry` skips `#` lines, so no parser effect.
- No code outside `tools/kama-probe.sh` hardcodes the verdict set: `grep -rn 'NOT_HTTP\|MODEL_MISMATCH\|MODEL_LOADING' --include='*.py' --include='*.sh' --include='*.tsv' tools/ tests/ registry/` → only the probe, its tests, `tests/llamacpp-live/check-receipt.py` (MODEL_MISMATCH only), and the updated registry comment. The four JSON emitters (`listeners` `:743`, `consumers` `:814`, `check` `:889`, `snapshot` `:1063`) all interpolate `$VOCAB`; observed with the new token in runs 6, 7, 12.

## 4. Findings

### F1 — LOW — "Drift (exit 2)" is unqualified; two subcommands return 0 on MODEL_LOADING

`:35` reads "Drift (exit 2): not ready" inside the verdict-vocabulary block. Only `check`/`snapshot` gate on the verdict:

- `tools/kama-probe.sh:864` `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi` → `eval_rows` returns 2.
- `cmd_listeners` returns 0 unconditionally (`:744` returns 0; JSON `exit_codes` even says `"2": "drift (listeners does not gate)"`).
- `cmd_consumers` sets `exit_code=2` only for `file_match` `no`/`missing` (`:800-801`).

Observed: exact envelope → `listeners` **exit 0** (run 7), `consumers` **exit 0** (run 12), `check`/`snapshot` **exit 2** (runs 6, 11). This mirrors pre-existing behavior for FOREIGN_SERVICE, so it is not a regression, but the new sentence is the first to attach "drift/exit 2" to a verdict globally. Suggest `Drift in check/snapshot (exit 2): not ready` (same fix applies to the sibling doc copies; the docs seats own those).

### F2 — INFO — "Router mode never emits it" has a startup window; the stronger sibling counterexample is off the probe's path

Pinned source: `server.cpp:455` `if (!ctx_http.start())`, then `:460` `ctx_http.is_ready.store(true);` in the router branch. `server-http.cpp:493-547` `start()` binds, spawns the listener thread, and calls `wait_until_ready()` before returning, so a request accepted between the return of `start()` and the store at `:460` is answered by `middleware_server_state` with the exact 503 body. The window is a few instructions (sub-millisecond, practically unreachable), but "never" is absolute. In single-model mode the same window is the intended load duration (`server.cpp:507-515`).

Note on overlap: the sibling finding in `CriticNoHarm.md` §F1 (router relays a child's envelope on **proxied** routes) is real but does not touch the probe's query path — `/v1/models` is the router's own handler (`server.cpp:269` `routes.get_models = models_routes->get_router_models;`, wired at `:283-284`), not a proxy. So F2 is the only path-level counterexample for this sentence. Consequence either way is conservative: a stray match yields MODEL_LOADING (drift, exit 2), never a false `MODEL_OK`.

[INFERENCE] The window argument is a static read of pinned code; `server-models.cpp`/`server-http.h` are not in the pinned set, so the router models handler and the initial value of `is_ready` were not independently inspected.

### F3 — NIT — line citation differs between header and gate comment

Header `:34` cites `server-http.cpp:307-328` (matches `pins.json`); the gate comment `:420` cites `307-325`. Both lie inside the same lambda (`325` is `return false;`), so neither is wrong; aligning them would remove a needless second authority.

### Non-findings checked and cleared

- The gate is placed **after** the 401/403 branch (`:494-501`) and **before** the HTML sniff/model-array logic (`:510-518`); it therefore cannot mask DEAD/NOT_HTTP/auth, and it only fires for status 503 + exact body. Near-miss bodies keep `FOREIGN_SERVICE / non-2xx-non-model-http` (run 8), identical to the pre-image.
- `model_endpoints` in the listeners summary still counts only `MODEL_OK|MODEL_MISMATCH`; a loading endpoint is counted once in the new `model_loading` bucket, and the buckets sum to `probed` (run 7). Defensible semantics, no double count.
- JSON schema stays `kama-probe/v1`; the listeners change is a purely additive summary key, and every emitter's JSON parsed in my runs.

## 5. Residual risk and verification gaps

- My stub is `python3 http.server`, not llama.cpp. I did not start llama-server (not authorized by this item), so the real 503 surface was not exercised here; the pinned source and the four live receipts are the runtime evidence, not this report.
- `server-models.cpp`/`server-http.h` are unpinned; router-handler behavior beyond `server.cpp` route wiring is unverified here.
- Full `listeners` enumeration was not run (it would probe 8080/34113); only `--port` mode, which skips `ss` and the registry.
- The 72/72 matrix rerun duplicates `RerunMatrixCurrent`/`RerunMatrixFrozen`; I ran the current probe only and did not re-derive the before/after changed-set (L1's `measure-stdout.txt` reports `directional: loading_expectations=17 before_failed=17 changed=17 equal=True`).
- No installs or upgrades were made.

Report: `.ufo/waves/round-16/falsify/advice/ReviewProbeDiff.md`
