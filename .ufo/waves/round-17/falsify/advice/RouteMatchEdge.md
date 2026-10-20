VERDICT: confirm — scoped C1 route conjunct requires exact GET and exact /v1/models after query stripping; HEAD-only and trailing-slash-only probes fail.

## Scope and findings by severity

Recommendation only, not an admission or a verdict on all of round 17. Attacked the route-match conjunct landed at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, including its stub request capture, grading integration, and canonical gate return code.

**No actionable defect found in the assigned route-match behavior.** The query-bearing request passes intentionally; this is not raw request-target equality. Extra requests are permitted, but a qualifying method and path must occur in the same recorded request.

Axes of this scoped attack: **method discrimination**, **query-stripped exact-path boundary**, **causal isolation of the route conjunct**, and **test containment**. These are review dimensions, not changes to lane axes or scores.

## Source evidence at the assigned commit

All source line citations below refer to the assigned commit. Code was read and exercised in the disposable checkout, not executed from the lane.

1. **Exact method and query-stripped exact path, on one request.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:374-376`:
   - `r.get("method") == "GET"`
   - `r.get("path", "").split("?", 1)[0] == "/v1/models"`

   Both predicates are inside the same `any(...)` generator. `HEAD` and lowercase `get` cannot satisfy the method predicate; `/v1/models/` cannot satisfy the path predicate. `/v1/models?x` can satisfy it. Lines 372-373 explicitly exempt closed-port rows by returning `None`; stub-mode rows return a boolean.

2. **The result actually gates the row.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:453` assigns `record["route_ok"]` from the predicate; line 481 adds `and record["route_ok"] is not False` to the pass conjunction. Lines 448-451 also record it on timeout and return the still-failing row. Lines 648-659 and 672 derive and return gate code 1 when any row fails. This is not merely a recorded diagnostic.

3. **Stub method permissiveness does not weaken the grader.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:216` records `{"method": self.command, "path": self.path}`. Lines 217-219 perform exact route lookup followed by query-stripped fallback. Lines 255-258 dispatch HTTP methods through the same responder, but lines 252-253 suppress the HEAD body. Thus HEAD can receive HTTP 200 while still failing the independent exact-GET check. With this fixture's null default, missing trailing-slash routes fall through to HTTP 404 at lines 220-223.

4. **The honest probe's canonical request remains unchanged.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh:456`: `fetch "$port" "/v1/models" "m$port"`. Its curl invocation at lines 294-297 uses the supplied URL without a HEAD or alternate-method option. The empirical honest-probe baseline recorded `GET /v1/models` and `GET /health` and passed.

5. **Existing positive fixture, not a weakened test.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ReadyControls.json:3-43` identifies `ReadyControls.expect-exact-id`, serves model `kama-ready`, and requires `{"verdict": "MODEL_OK", "reason": "matched", "exit": 0}`. No matrix or gate source was edited.

## Scratch-wrapper measurements

Used Python 3.14.8. The driver imported the checked-out gate and called its real `main()` with the existing `--only ReadyControls.expect-exact-id --probe ... --json` CLI arguments. It preserved matrix loading, `run_probe()`, request handler, route predicate, `grade()`, and CLI return logic. Its only server substitution pinned the bind address from the canonical `127.0.0.1:0` request to the prechecked, non-consumer `127.0.0.1:49271`.

First ran the actual probe to obtain an accepted row. Each subsequent shell wrapper made the specified real HTTP request(s), consumed the response, then replayed that accepted row and probe exit 0. This holds verdict, reason, drift, served model, and probe exit constant, isolating the route conjunct. Replayed `evidence` text was deliberately cached, not used as evidence of wrapper traffic; the canonical recorded `requests` and separately captured HTTP responses establish actual traffic.

Every wrapper row had `MODEL_OK`, `matched`, drift `false`, served model `kama-ready`, `served_model_ok=true`, `probe_exit=0`, and `error=null`. The driver asserted all five non-route grading conjuncts, exact recorded requests, route result, final row result, and canonical `main()` return. All assertions passed after the setup correction documented below.

| Wrapper traffic (and no other traffic) | HTTP response(s): status / body bytes | `route_ok` | Row passed | Canonical `main()` return |
|---|---|---|---|---|
| `GET /v1/models` | 200 / 413 | true | true | 0 |
| `HEAD /v1/models` | 200 / 0 | false | false | 1 |
| `GET /v1/models?x` | 200 / 413 | true | true | 0 |
| `GET /v1/models/` | 404 / 0 | false | false | 1 |
| `GET /v1/models/?x` | 404 / 0 | false | false | 1 |
| lowercase `get /v1/models` | 200 / 413 | false | false | 1 |
| `HEAD /v1/models`, then `GET /health` | 200 / 0; 200 / 15 | false | false | 1 |
| `HEAD /v1/models`, then `GET /v1/models?x` | 200 / 0; 200 / 413 | true | true | 0 |

The split-across-requests control rules out independently satisfying method and path on different requests. The final control confirms the predicate is existential: a valid request among extra traffic suffices, as the code says. Of eight wrapper cases, three passed and five failed exactly as the contract predicts; the honest-probe baseline also passed.

Representative canonical diagnostics from the tested runs:

- HEAD: `route=missing-GET-/v1/models requests=[HEAD /v1/models]`
- Slash: `route=missing-GET-/v1/models requests=[GET /v1/models/]`
- Query: `[PASS] ReadyControls.expect-exact-id` with `requests=[GET /v1/models?x]`

## Exact shell commands and exit codes

Read/grep/write/edit device calls are not shell commands and have no shell exit code. No recursive filesystem grep was used. LSP discovery is documented under limitations.

1. Clone and pin; **exit 0**:
   ```sh
   git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RouteMatchEdge-clone && git -C /tmp/KamaR17.RouteMatchEdge-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.RouteMatchEdge-clone log --oneline -1
   ```
   Output identified `54a2926` and the round-17 build subject.

2. Read actual changed gate behavior; **exit 0** (working directory `/tmp/KamaR17.RouteMatchEdge-clone`):
   ```sh
   git -C /tmp/KamaR17.RouteMatchEdge-clone diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tests/probe-verdicts/check.py
   ```

3. Port checks before testing, after the initial setup assertion, and after the successful measurements; **exit 0 each**, no listener rows each time:
   ```sh
   ss -ltnp '( sport = :49271 )'
   ```

4. Focused driver, first invocation **exit 1**, corrected invocation **exit 0** (working directory `/tmp/KamaR17.RouteMatchEdge-clone`):
   ```sh
   PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.RouteMatchEdge-scratch python3 /tmp/KamaR17.RouteMatchEdge-scratch/driver.py
   ```
   The first invocation's scratch-only assertion wrongly expected the honest baseline to make *only* the models request. Actual baseline already passed and correctly also made `GET /health`. Changed that assertion to require its first request to be the canonical models GET. This was a test-driver assumption, not a gate defect. The second invocation produced the eight measurements above, plus the passing honest baseline, and `all_assertions_passed=true`.

   Canonical `main()` arguments for the baseline were:
   ```text
   --only ReadyControls.expect-exact-id --probe /tmp/KamaR17.RouteMatchEdge-clone/tools/kama-probe.sh --json
   ```
   For every wrapper case they were:
   ```text
   --only ReadyControls.expect-exact-id --probe /tmp/KamaR17.RouteMatchEdge-scratch/edge-probe.sh --json
   ```
   The canonical `run_probe()` subprocess command for the baseline was:
   ```sh
   bash /tmp/KamaR17.RouteMatchEdge-clone/tools/kama-probe.sh check --port 49271 --expect kama-ready --json --timeout 2 --connect-timeout 1
   ```
   Its wrapper counterpart, invoked once for each table case, was:
   ```sh
   bash /tmp/KamaR17.RouteMatchEdge-scratch/edge-probe.sh check --port 49271 --expect kama-ready --json --timeout 2 --connect-timeout 1
   ```
   All those probe subprocesses exited 0; the rejection codes in the table are the gate's `main()` returns, not wrapper failures. The wrapper executed `python3 /tmp/KamaR17.RouteMatchEdge-scratch/edge-probe.py` with the same arguments, using Python's `http.client` on loopback for the listed traffic.

5. Runtime identification; **exit 0**, output `Python 3.14.8`:
   ```sh
   python3 --version
   ```

6. Final owned-scratch removal and teardown confirmation; **exit 0** (working directory `/tmp`):
   ```sh
   rm -rf -- /tmp/KamaR17.RouteMatchEdge-clone /tmp/KamaR17.RouteMatchEdge-scratch && test ! -e /tmp/KamaR17.RouteMatchEdge-clone && test ! -e /tmp/KamaR17.RouteMatchEdge-scratch && ss -ltnp '( sport = :49271 )'
   ```
   Both scratch trees were absent; `ss` printed only its header, no listener rows.

## Residual risk and verification gaps

- **LSP unavailable:** discovery via `read xd://lsp` returned `No such tool: xd://lsp` and the mounted-device list contained no LSP device. Status, references, definitions, diagnostics, and index warm-up were therefore unavailable. Literal source/diff inspection is not presented as semantic LSP proof; the canonical gate execution supplies behavioral evidence.
- Scoped to the requested route boundary on one unchanged ready-model fixture. Did not rerun the whole matrix, fault-control suite, mutant grid, or claimed 10/10 result, and did not assess broader C1 malformed-output handling or C2. No saturation or mastery claim is supported by these eight controls.
- Query acceptance is deliberate and documented by the predicate's docstring at `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:367-370`; the result must not be described as exact equality of the entire request target including query. Likewise, the predicate proves occurrence of a qualifying recorded request, not that the claimed verdict was computed from its response.
- No serving runtime, same-identity rerouting, or resume path was exercised or changed. Only the gate's loopback stub was started, sequentially, on port 49271. Neither 8080 nor 34113 was bound or contacted. `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:35-37` lists only those two protected consumer ports.
- All lane tool execution occurred in the pinned disposable clone with `PYTHONDONTWRITEBYTECODE=1`; temporary probe files were directed into the owned scratch tree by `TMPDIR`. No lane source, matrix, manifest, runtime state, or sibling file was edited. The required Report is the sole deliberate lane write. Owned scratch was removed before this Report was written.

## Installs

None. No package manager, host service change, or tool update was needed.
