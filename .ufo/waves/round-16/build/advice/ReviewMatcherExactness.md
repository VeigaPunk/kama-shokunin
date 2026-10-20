# ReviewMatcherExactness — C1 exact-triple matcher (operability + calibration)

Read-only seat. The build moved several times during review; this is a verified snapshot.
`tools/kama-probe.sh` sha256 `6edd3c4c…972fa50` (matcher semantics identical in the
earlier `d0d48d8d…` revision I read); `tests/probe-verdicts/check.py` last seen
`fd49ff7c…76140`; 72 matrix tests in 9 families; frozen probe `93ee4302…a2cd64`
(matches `.ufo/waves/round-16/frozen/manifest.json`). No installs; I ran no lane gate,
harness, or test — measurement is L1's.

## Recommendation: ACCEPT — do not narrow, do not widen

The matcher is exactly what llama.cpp serves on the probed path, is object-semantic
(not byte-literal), and the change is monotonic: a static replay of `classify()` is
**0 mismatches over all 72 tests**, the gate fires on exactly the **17** tests
expecting `MODEL_LOADING`, and **no other test's verdict changes** (0 flips). The
frozen probe therefore fails exactly those 17 (each becomes `FOREIGN_SERVICE` /
`non-2xx-non-model-http`, exit 2), matching L1's 10:17 observation.

Why widening is unsafe — real b11755 503 `unavailable_error` bodies with a *different*
message, all landing at status 503 (`server-context.cpp:4872-4873`
`status = json_value(error_data, "code", 500)`):

- `tools/server/server-context.cpp:5396` "no slot available" (`fail_on_no_slot`).
- `tools/server/server-models.cpp:2585` "Stream owner model is loading, retry later"
  (router stream owner; independently verified in raw source).

Matching any 503 `unavailable_error` would label a busy server or a router stream
guard as `MODEL_LOADING`. The exact message is the discriminator, and the code keeps it.

Why narrowing is unsafe: exact key set would break on future added fields (matrix
`ExtraFieldsAllowed`, 64 KiB `Padding64KiB`); requiring the CHARSET/CT would break
behind proxies (`plain-json-content-type`, `exact-envelope-labelled-html`); stringly
`code` acceptance would open the rule to foreign OpenAI-style 503s.

## What the code does

- `tools/kama-probe.sh:428-447` `body_is_llamacpp_loading()` parses JSON with python3:
  top-level dict, `error` dict, `message == "Loading model"`,
  `type == "unavailable_error"`, `not bool` + `isinstance(int)` + `== 503`.
- `:503-508` gates on `F_CODE = "503"` and a non-empty body; evidence `:506` says
  "body matches the llama.cpp loading envelope: not ready; runtime identity and served
  model unverified" — correctly refuses to infer runtime identity from body shape.
- Placed after 401/403 and before the HTML sniff (`:510-514`, reason `:551`) and the
  2xx/model-array branch.
- Integration: `VOCAB` `:62`, help `:117`, comment `:28-36`, `listeners` tally `:733`
  and summary `:743`, baseline reader `:939` (without it a persisted `MODEL_LOADING`
  row would be dropped as malformed and force a rebaseline). `check`/`consumers` exit
  2 automatically because drift is `verdict != MODEL_OK` (`:848`, `:864`).

## Is serialization stable? Key order: no; code type: yes

Wire construction b11755 `tools/server/server-http.cpp:316-323`: order
`message,type,code`, literal integer `503`, serialized by `common_json::dump_safe`
(`common/json.cpp:343-344`, `indent` default `-1` → compact). Ordering contract:
`common/json.h:24` "object keys keep the order in which they are added".

Key order is **not** stable, even inside one binary:

- `tools/server/server-common.cpp:127-131` builds every `format_error_response`
  body as `{"code", "message", "type"}` — code first — while the loading body is
  message,type,code (`server-http.cpp:318-320`).
- `tools/server/README.md:486` documents the loading body code-first with spaces:
  `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`
  and `:487` says "the model is still being loaded."

So a byte-literal matcher would fail against llama.cpp's own documented body. The
implemented object match is right; the matrix pins it with key-order,
pretty-printing, and README-order positives.

Code type is stable: integer `503` from b7600 through master (enum mapper also
`int`, `server-common.cpp:119-120`, `127-131`). Serializer by version:
`using json = nlohmann::ordered_json` at `tools/server/server-common.h` b7600:18,
b8100:16, b8200:16; compact dump (`server-common.cpp:1761-1762` at b8200).

## Versions where the envelope differs (or cannot fire)

Verified by fetching raw files at each tag, not inferred:

| builds | `/v1/models` while `is_ready == false` |
|---|---|
| b6000, b6500, b6800 (pre-split `server.cpp`) | **200** — exempt: `server.cpp:3819-3823` (b6000), `:4220-4224` (b6500) "allow the models endpoint to be accessed during loading" |
| b7100, b7200, b7400 (split exists) | **200** — same exemption: `server-http.cpp:175-177` (b7100), `:182-184` (b7200), `:182-183` (b7400) |
| b7600, b8100, b8200, b8400, b8600, b9000, b10000, b11000, b11755, master | **503 + exact triple**, no exemption (b7600 block; b8100 `:186-201`; b8200 `:188-201`; b11755 `:307-328`) |

`diff` of b11755 vs master over `server-http.cpp:230-360` is empty; no `Retry-After`
or body change. Conclusion: from b7600 to master the 503 loading envelope on
`/v1/models` is identical; no observed version serves a *different* 503 envelope
there. Before b7600 the response is 200, so the gate cannot fire — fail-closed.

Honest scope limit: pre-b7600 builds may be graded `MODEL_OK` while loading (they
serve a model list during load). C1 does not fix that opposite-direction gap.

## Exactness checks (static; no ports, no harness)

- Extracted the exact heredoc `:428-447` and ran 18 literal fixtures: 18/18 intended.
  Accepted: canonical; docs order + spaces; pretty; permuted keys; extra keys;
  trailing newline. Rejected: `503.0`, `5.03e2`, `"503"`, `true`, `null`; error as
  string/list; nested `outer.error`; top-level array; missing `error`; message with
  trailing space; BOM; trailing junk. (`503.0 == 503` is true in Python, so the
  `isinstance(..., int)` guard is load-bearing.)
- Replayed `classify()` over the 72-test matrix: 0 mismatches; 17/17 gate positives;
  0 collateral verdict changes. Verdict mix: 37 FOREIGN_SERVICE, 17 MODEL_LOADING,
  8 MODEL_OK, 5 UNAUTHORIZED_SERVICE, 3 MODEL_MISMATCH, 1 DEAD, 1 NOT_HTTP.
- Harness `check.py`: schema validation `:73-150`, route-exact stubs with compact
  `body_json` and honored `Server`/CT `:178-262`, a stub-saw-nothing guard `:326`,
  and grading of verdict + reason + probe exit **and** the drift contract
  `record["drift"] == (verdict != "MODEL_OK")` at `:340-347`. Probe stdout is JSON-only
  (`warn` → stderr `:87`, `emit_json` → stdout `:180-186`).

## Resolved during review (so L1 does not chase stale notes)

Three gaps I had flagged earlier were closed in the tree while I reviewed:

- `drift true` is now graded: `check.py:346`, after having been extracted but unused.
- Float/bool/message-boundary negatives now exist:
  `NearMissTriple.code-float-503.0`, `code-boolean-true`,
  `message-surrounding-space`, `message-trailing-period`, all → `FOREIGN_SERVICE`.
- The body-vs-header precedence is now pinned: `NearMissTriple.exact-envelope-labelled-html`
  (503 JSON body with `Content-Type: text/html`) → `MODEL_LOADING`, matching the
  claim's "body is a JSON object" wording; `readme-key-order-positive` pins the
  README key order. `empty-503` pins the no-body case.

## Findings by severity

1. **LOW — stale six-value vocabulary in docs.** `SKILL.md:12-13` and
   `corpus/knowledge/consumer-registry.md:84-85` still call the six values the
   "binding vocabulary". Already assigned (wave spec `ProbeSurfaces`, `SkillPlacement`);
   ensure the SKILL append lands and correct the consumer-registry sentence so docs do
   not contradict `VOCAB` (`tools/kama-probe.sh:62`).
2. **INFO — comment version floor.** `tools/kama-probe.sh:32` pins b11755 and is
   accurate, but b6000–b7400 exempt `/v1/models` while loading (200). A "b7600+" scope
   note would prevent over-reading the rule as universal llama.cpp behavior.
3. **INFO — python3 dependency.** Without python3 the verdict is inert (guard `:429`,
   documented `:426-427` and `:36`): fail-closed, never false-pass. Host has python3.

## Residual risk

- A non-llama.cpp service that copies the exact triple (e.g. a llama.cpp-based proxy)
  reads `MODEL_LOADING`; inherent to a body-signature rule and arguably still correct.
- A future llama.cpp change to `message`/`type`/wrapper silently regresses to
  `FOREIGN_SERVICE` (fail-closed). The comment pins b11755; rerun the matrix when the
  installed build moves.
- A proxy that rewrites the body (extra wrapper, BOM, trailing junk) is not matched.

## Verification gaps

I did not run `tests/probe-verdicts/check.py` against either probe; the 0-mismatch /
17-flip / 18-fixture results are a static replay plus an extracted-function unit run.
L1's runner must still execute the real red/green comparison (frozen vs repaired).
Note `check.py` itself moved four times during review; cite behavior, not the hash.
