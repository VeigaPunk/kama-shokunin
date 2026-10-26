source: S036 (llama.cpp `tools/server/server-http.cpp` @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad = release b11755, `middleware_server_state` lines 307-328, pre-routing order 347-359); S037 (`tools/server/server.cpp` @ same commit, lines 440-515); S035 (README @ same commit, §GET `/health` lines 479-490, §GET `/v1/models` line 1258); S038 (release b11755 asset identity); S039 (pinned GGUF identity); S040 (llm-d v0.10 readiness-probe page, liveness versus model-aware readiness); S017 (Kubernetes probe lifecycle vocabulary); S041 (own-work live receipt `.ufo/waves/round-16/live/receipt.json`)
verified-at: 2026-10-20 — upstream files fetched at the pinned commit and saved with digests under `.ufo/waves/round-16/sources/llama.cpp-704366d/`; final live run 2026-10-20T14:06:27.859Z–14:06:27.974Z by L1 through `tools/kama-llamacpp-live.py` (sha256 b8c5e8d4…); stub matrix run by L1 through `tests/probe-verdicts/check.py`
recheck: on-release — re-open the pinned middleware and re-run the live harness when the installed llama.cpp build changes; the receipt is a dated sample, never present service state

# llama.cpp loading-to-ready lifecycle and the MODEL_LOADING verdict

## Claim

A single-model llama-server answers almost every request with HTTP 503 and one
fixed JSON body while its model loads. Before round 16, `tools/kama-probe.sh`
graded that body `FOREIGN_SERVICE` / `non-2xx-non-model-http`, an evidence
string that calls the endpoint a "non-model service". The probe now grades the
exact body `MODEL_LOADING` / `llamacpp-loading` (drift, exit 2). The match is on
body shape only: it does not prove the runtime is llama.cpp, which model is
loading, or that the server will become ready.

Earlier corpus ground: `runtime-health-surface-matrix.md:14` already recorded
the README's `/health` 503 body (round 10). That fact is not new. This entry
adds the code-level path that puts the same body on `/v1/models`, the probe's
mapping, the scope limits, and one live lane-owned run.

## Lifecycle at b11755 (S036, S037)

1. **Listener before model.** Single-model mode starts the HTTP listener, then
   calls `load_model`, and stores `is_ready = true` only after it returns
   (server.cpp:493-515). No `store(false)` appears in the server sources read.
2. **Loading gate.** `middleware_server_state` runs in the pre-routing handler.
   While `is_ready` is false it lets frontend assets through (`/` and embedded UI
   files, server-http.cpp:309-311) and answers every other path, `/health` and
   `/v1/models` included, with status 503 and
   `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
   (server-http.cpp:314-325).
3. **Before the API key.** The pre-routing handler short-circuits `OPTIONS`,
   then runs the state gate, then the API-key check (server-http.cpp:347-359).
   A loading server with `--api-key` therefore answers 503, not 401.
4. **Ready.** `/health` returns `{"status":"ok"}`; `/v1/models` returns 200 with
   one `data[]` entry (id = the first `--alias` in sorted order, else the `-m`
   path; `owned_by` `llamacpp`, server-context.cpp:5168-5225) and an
   Ollama-shaped `models[]` array.
5. **Router mode is different.** The router stores `is_ready = true` right after
   its listener starts, before any model loads (server.cpp:455-460), so the
   router's own `/health` and `/v1/models` never answer with this body; its
   `/v1/models` is a catalog with per-model `status`. Routes the router proxies
   to a per-model child (`/metrics`, `/slots`, inference) can relay a loading
   child's 503 [INFERENCE from server-models.cpp; not run]. The probe only asks
   `/v1/models`, so its verdicts are unaffected.
6. **Sleep is different.** A sleeping server answers `/v1/models` and `/health`
   200 from cache (server-context.cpp:5725-5733); sleeping does not reset
   `is_ready` [INFERENCE from code paths; not run].
7. **Documentation lags code.** The README documents the 503 body only under
   `/health` (README:485-487, key order `code, message, type`) and says `/v1/models`
   `meta` "can be `null` (for example, while the model is still loading)"
   (README:1258). In direct mode the code answers that window with the 503, not
   a 200; the same code order holds at the round-10 pin c0fd7862, so the README
   reading was never observable there either. The server emits keys in
   insertion order `message, type, code` (server-http.cpp:318-320), so matching
   must parse JSON, never compare bytes.

## Probe mapping (repaired `tools/kama-probe.sh`)

| `GET /v1/models` answer | Verdict / reason |
|---|---|
| refused / timeout | `DEAD` connection-refused / timeout |
| 401 / 403 (any body, even the loading body) | `UNAUTHORIZED_SERVICE` http-401 / http-403 |
| 503 + JSON `error` with `message` exactly `Loading model`, `type` exactly `unavailable_error`, integer `code` 503 (extra top-level keys allowed; any `Content-Type`) | **`MODEL_LOADING` llamacpp-loading**, drift, exit 2 |
| 503 with any other body (`no slot available`, `Stream owner model is loading, retry later`, `loading model`, `code` `"503"`/`503.0`/`true`, empty, HTML, text) | `FOREIGN_SERVICE` non-2xx-non-model-http (or html-non-model) — unchanged |
| exact loading body at 200/500/502/504 | unchanged generic verdicts |
| 2xx with model array | `MODEL_OK` / `MODEL_MISMATCH` — unchanged |

The verdict needs python3. Without it the probe keeps the old `FOREIGN_SERVICE`
reading (fail closed: still drift, never a false `MODEL_OK`).

## Scope limits

- **Engine-specific; other engines are leads, not admitted facts.** Build-wave
  source and doc reads (advice under `.ufo/waves/round-16/build/advice/`, no
  SOURCES row, no runtime run; KQ6 does not admit them) suggest: vLLM v0.32.0,
  TGI v3.3.7 and KoboldCpp 1.123.1 (default mode) do not listen until ready, so a
  probe would see `DEAD`; SGLang v0.5.22 answers `/v1/models` 200 while
  `/health` is 503; Ollama v0.40.6 lists available models with 200 whatever the
  load state; LocalAI v4.11.0 binds only after startup preload; LM Studio's docs
  mention no 503 (docs only). `MODEL_LOADING` claims none of these engines.
- **Not-ready is not dead and not foreign.** Kubernetes separates readiness
  (withhold traffic, keep running) from liveness (restart) (S017); llm-d's v0.10
  guide separates process liveness on `/health` from model-aware readiness on
  `/v1/models` for vLLM (S040). `MODEL_LOADING` is the readiness class. S040 is
  vLLM-scoped and does not support the llama.cpp body.
- **Older builds can be false-ready.** Sampled tags (not bisected) suggest that
  between roughly b6000 and b7502 llama.cpp let `/v1/models` through during
  load. A probe there sees a model list and can grade a loading server
  `MODEL_OK` [lead: `RevengerEnvelopeHistory.md`, `ReviewMatcherExactness.md`].
  The verdict is tied to the pinned build; re-open S036 when the build changes.
- **A copied body matches.** Any server or proxy sending the exact body is
  graded `MODEL_LOADING`. That is still drift (exit 2 from `check`/`snapshot`).
- **Overlap with earlier entries.** The router catalog and sleep cache were
  already held in `served-identity-crosswalk.md` (round 11); they are repeated
  here only as limits, not as new ground.

## Live observation — round 16 (lane-owned fixture, not service restoration)

Final receipt `.ufo/waves/round-16/live/receipt.json` (`kama-llamacpp-live/v1`,
tool sha256 `b8c5e8d402595f3b…`, probe sha256 `36b64978ee3a3aa2…`),
2026-10-20T14:06:27.859Z–14:06:27.974Z:

- Binary: `~/.local/opt/llama-b11755/llama-server`, launcher sha256
  `b6a31a8e97615a2a…`, `libllama-server-impl.so` `e404b91a81c9ab65…`, install
  tree of 51 files hashed (`install_tree_sha256` `6c216313a88d71b1…`);
  `/props` `build_info` `b11755-704366d76`.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` before and
  after the run; alias `kama-stories260k`.
- Port 37527 on 127.0.0.1, listener proven owned by the child at the first HTTP
  answer, before captures and before each probe; refusal set {8080, 34113} plus
  every registry port, and a port already listening is refused. Child
  environment: `HOME`, `LANG`, `PATH` only; `--offline`.
- Load window (polling `/v1/models` alone on one keep-alive connection):
  connection refused for the first 6 ms (210 attempts), then 38 answers of HTTP
  503 with `Server: llama.cpp`, `Content-Type: application/json; charset=utf-8`
  and body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
  (sha256 `baa09177…957c`, keys in `message, type, code` order;
  `loading_envelope_exact` true), then `/v1/models` 200 and `/health` 200 at
  11 ms. Server log: model loaded at about 8.4 ms after start.
- The captured body, replayed on a stub with its status and headers
  (`live/replay-captured-503.py`, output `replay-captured-503.txt`), grades
  `MODEL_LOADING` / `llamacpp-loading` exit 2 with the current probe and
  `FOREIGN_SERVICE` / `non-2xx-non-model-http` exit 2 with the frozen one.
- Ready: `/health` 200; `/v1/models` 200 with `data[].id` `kama-stories260k` and
  `owned_by` `llamacpp`; `/metrics` 501 (no `--metrics`); `/slots` 200.
- Probe: `MODEL_OK` matched exit 0 with the alias; `MODEL_MISMATCH`
  served-id-mismatch exit 2 with `kama-not-this-model`.
- Teardown: SIGTERM, return code 0, port refuses afterwards; no `llama-server`
  process and nothing on 8080/34113 afterwards (`live/controls.txt`).

Control: a separate run with the frozen pre-round probe
(`receipt-frozen-probe.json`, port 43229) also passes all 10 checks, so this
capability does not depend on the `MODEL_LOADING` change.

What the receipt does not show: which weights a production deployment serves
(the id is the caller's alias), health of the registered consumers (8080 and
34113 were refused, never touched, and stay `DEAD` in `registry/history/latest.tsv`),
generation, quality, performance, GPU paths, router mode or sleep, and a live
probe verdict during load (the harness records the raw 503 but runs the probe
only after `/health` is 200; the probe verdict on that body comes from the
replay). Known harness limits from the falsify wave: `health_ready` checks the
status only, not the `{"status":"ok"}` body; `teardown_exited` and
`teardown_port_closed` prove reaping and a refused port, not that SIGTERM caused
the exit; `loading_envelope_exact` is recorded, not graded
(`.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md`).

## Round 17 — ready body, graceful teardown and fail-capable live checks (appended 2026-10-20)

Provenance supplement (the header above is unchanged): source S042
(`tools/server/server-context.cpp` @ 704366d76, `get_health` 5288-5299), S043
(`tools/server/server.cpp` @ 704366d76, signal path 26-38, 519-534, 575-590;
`server-queue.cpp` 132-136), S044 (Python 3.14 `Popen.returncode`), S046
(own-work receipts `.ufo/waves/round-17/live/receipt-{1,2,3}.json`);
verified-at: 2026-10-20 — sources re-fetched at the pinned commit and saved
with digests under `.ufo/waves/round-17/sources/` (`pins.json`); live runs
2026-10-20T15:57:44.932Z–15:57:45.445Z by L1 through `tools/kama-llamacpp-live.py`
(sha256 0efd1723…), each gated `VALID` with all four pins; recheck: on-release,
as above.

**Ready body.** The only 200 body the `/health` handler emits is
`res->ok({{"status", "ok"}});` (S042, server-context.cpp:5297), serialized
compact: 15 bytes `{"status":"ok"}`, sha256 `a29ee2b1…d288`. The README's
`{"status": "ok" }` (S035, README:489) is documentation spacing, so the live
check compares parsed JSON for equality with exactly `{"status": "ok"}`. A 200
with any other body (for example `{"status":"degraded"}`) is not this handler.
A body check must use GET: `OPTIONS` is answered by the pre-routing CORS branch
(server-http.cpp:347-352) before the state gate.

**Graceful teardown.** SIGINT and SIGTERM share one handler, registered at
server.cpp:529-534 only after `load_model` (507) and `is_ready.store(true)` (515)
(S043). The first signal calls `ctx_server.terminate()` (519-523), which stops
the task loop (`server-queue.cpp:132-136`); the main thread then cleans up, joins
the HTTP thread and returns 0 (server.cpp:575-590). A later signal prints
"Received second interrupt, terminating immediately." and calls `exit(1)`
(server.cpp:30-34). A SIGTERM delivered before line 534 meets the default action,
so Python sees returncode -15: "A negative value -N indicates that the child was
terminated by signal N (POSIX only)." (S044). Returncode 0 alone does not say who
sent the signal; the receipt binds it to the harness through a fresh `poll()`
before `killpg` (`alive_at_teardown_start`), `sigterm_sent` only on successful
delivery, `sigkill_sent` false, and port ownership proven for the child earlier
in the same run.

**Observed (S046).** Three runs on the pinned build and fixture: `/health` 200
`{"status":"ok"}`; 42, 45 and 45 loading 503s on `/v1/models`, every one the exact
envelope (one distinct body, sha256 `baa09177…957c`); SIGTERM to a live child,
returncode 0 after 3 ms, no SIGKILL, port refused afterwards; 11/11 checks.
Independent scratch probes this round (advice `ProbeSigtermExit.md`,
`ProbeHealthBody.md`, `CriticC2Predicates.md`) saw returncode 0 in every
post-ready SIGTERM run and -15 for SIGTERM during loading.

**The v1 limits above are superseded for receipt v2** (`kama-llamacpp-live/v2`):
`health_ready` grades the body; `teardown_exited` is replaced by
`teardown_graceful` (harness SIGTERM to a live child, no SIGKILL, returncode 0,
child ownership); `teardown_port_closed` fails unless child ownership was proven;
`loading_envelope_graded` fails when no 503 was observed or when any stored 503
body is not exact; an exception in teardown still writes a receipt with
`internal:<ExcType>` and exit 2. `model_unchanged` stays as input integrity, not
subject evidence. Fake-server controls (`tests/llamacpp-live/controls.py`) show
each check failing on the misbehaviour it names.

**Correction (appended).** Line 29 above says the gate answers "every other
path" apart from frontend assets; `OPTIONS` is also excluded — it is answered
at server-http.cpp:347-352 before the state gate at 354. The body's `type` and
`code` are at server-http.cpp:319-320, alongside `message` at 318.

Limits: one build (b11755 = 704366d76), CPU, fixture model, single-model mode,
sampled instants on unregistered loopback ports. Not consumer health (8080 and
34113 untouched, still `DEAD`), not router mode or sleep, not generation.

**Round-17 falsify correction (appended).** The graceful-teardown paragraph above
says the first signal stops the task loop and the main thread returns 0. That holds
once `start_loop` is running: a SIGTERM delivered after the handler install
(server.cpp:534) but before `start_loop` resets `running = true`
(`server-queue.cpp:279`) is lost, the server keeps serving, and a later signal exits 1
(S047, supersedes S043; static ordering, not reproduced). The harness signals only
after `/health` 200, the readiness captures and both probe runs, so its runs did not
hit that window, but `/health` 200 (server.cpp:515) does not by itself prove the
handler is installed. "The v1 limits above are superseded" covers the health-body,
teardown and loading-grading limits only: the live probe still runs after readiness,
so a probe verdict on the loading body still comes from the replay. "Still `DEAD`"
for the registered consumers is the last snapshot (20261014T124232Z), not a new
sample. Under heavy CPU saturation the loading window can fall between two polls: in
the falsify wave 1 of 60 real runs at 32x `stress-ng` load observed no 503 and failed
`loading_envelope_graded` on a healthy server (0 of 20 idle runs, 0 of 30 at 3-12x
load; `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md`, `LiveFastLoad.md`).

## Round 18 — missing observation is not failure; v3 boundary

The round-17 line “That holds once start_loop is running” is too strong if read
as sufficient for termination. S047 supplies a necessary ordering condition:
before the reset at server-queue.cpp:279 a handled stop can be overwritten.
Unexamined shutdown calls, mutex acquisition and platform signal behaviour still
limit a general termination guarantee (KQ23; `lessons/round-18.md`). The harness's
observed returncode-0 teardown is a run observation, not a universal theorem.

Receipt `kama-llamacpp-live/v3` retains the existing capability and adds
`evaluated` plus tri-state `passed`. Only `loading_envelope_graded` may be null,
for `no-loading-503-observed`; tool exit 2 / gate exit 3 says NOT-EVALUATED.
A genuine false check dominates the missing observation and exits 1. Thus the
old “fails when no 503 was observed” rule no longer describes current code.
S052 supports only keeping an empty observation distinct, not these lane numbers.

The v3 gate accepts `--require-schema v3` to refuse a receipt declaring a weaker
schema. Omit it only for intentional historical v1/v2 receipt verification.
It re-derives exact launch argv (including raw `model.arg`), grades recorded
loading 503 transitions as well as retained bodies, and rejects dropped-body
coverage gaps. S054 shows why server-side duplicate warnings are not rejection.
The raw model argument and resolved input path are separately recorded, avoiding
the old false failure on a genuine relative model path.

S048/S050 ground the fixed IPv6 listener-ownership parser; S051 explains why
Exception-only guards missed KeyboardInterrupt/SystemExit. Internal faults
produce setup-error receipts and exit 2 where output remains writable. A receipt
write failure cannot promise a file it could not write. The gate re-derives
internal consistency, not an authenticated execution trace: an author who
consistently removes evidence can still forge a story. Exact argv does not prove
effective config free from HOME/config.ini inputs. These limits are not hidden
by the retained fake-server controls or the real b11755 samples.

Round-18 own-work observation S055: the three retained real b11755 v3 receipts
in `.ufo/waves/round-18/live/receipt-{1,2,3}.json` each have outcome `pass`,
11 evaluated true checks and a captured loading observation. Each validates
with `--require-schema v3` and model/server/probe/tool SHA-256 pins
(`runs/commands.json`, measured production commit
`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`). These are actual surfaces, not
the fake K0 control. Their counts say nothing about generation or other models.

Round-18 falsify clarifications: **S056 supersedes S054's general last-wins
wording**. Scalar port/host handlers replace their values, but api-key and
spec-type handlers append; spec-type is duplicate-warning-exempt. Exact launch
argv equality remains a lane policy, not a theorem derived from the warning.
The S051 parenthetical “canonical /3.14/library/exceptions.html” means only the
historical redirect alias; the versioned reviewed page is
`https://docs.python.org/3.14/builtins/exceptions.html`. Its unversioned canonical
link serves 3.15 and is not the host-version source. BaseExceptionGroup can also
escape Exception; the tool's BaseException guard covers it, without relying on
the abbreviated three-example list.

**Four-pin limit:** `--expect-server-sha256` pins the launcher file. This release
loads `libllama-server-impl.so`; the receipt records its digest and the install
tree, but those are not independently expected by the current four-pin gate.
A consistent implementation/tree swap can remain internally VALID. Therefore
“four-pin VALID” is not authentication of the complete runtime implementation.
The retained real runs used the observed unchanged installation; no library was
swapped. Implementation-digest preconditions remain a separate possible move.

**Round-18 falsify corrections (appended 2026-10-21).**

- *Window-exclusion evidence (ReopenS047 F2).* The sentence "The harness
  signals only after `/health` 200, the readiness captures and both probe runs,
  so its runs did not hit that window" is not sound evidence: `/health` 200 is
  set at server.cpp:515, before the handler install at 534, and the captures and
  probes run on the HTTP thread, not the main thread. The deciding evidence is
  the receipts' teardown fields: `returncode 0`, `sigkill_sent false`, one
  SIGTERM. A signal lost in [534, 279] leaves the process serving until the
  next signal (exit 1) and would have needed SIGKILL; a pre-534 signal would
  die by default disposition (-15). The observation-order argument is
  [INFERENCE] only.
- *Gate pins.* The "Four-pin limit" paragraph above is historical. The gate now
  accepts `--expect-server-impl-sha256`, and the official round-18 runner passes
  the observed `libllama-server-impl.so` digest as a fifth pin, alongside the
  launcher, model, probe and tool pins. The gate also rejects a receipt whose
  `server_impl_sha256` disagrees with `install_tree['libllama-server-impl.so']`.
  The flagless default records the implementation/tree digests without an
  expected value, so a consistent swap remains VALID *unless* the caller
  supplies the impl pin. Residual: only that one of 51 install-tree members is
  pinned — `libllama-common`/`libggml`/`libllama` swaps stay internally VALID
  under the fifth pin (`ResidImplPin.md` P2). A five-pin VALID is not an
  authenticated execution trace; it binds the bytes the lane observed.


**Round-19 sixth-pin note (appended).** The four-pin limit above is historical
for the official runner: `--expect-install-tree-sha256` now pins the observed
`sorted(name sha)` digest of the install directory's regular files, and the
gate rejects a field↔tree disagreement. Scope: 51 regular files on this host;
the soname symlinks (`libllama.so.0`, `libggml.so.0`, …) and system NEEDED
libraries (`libc`, `libstdc++`, `libssl`, …) are outside it, so retargeting a
link or substituting a system library leaves the pin unchanged (CritC2Inflation,
TreeCap). The pin binds observed bytes; it is not authentication of execution.

## Round-21 supplement — install identity covers soname links (appended 2026-10-21)

The round-19 scope note above stays historical: `install_tree_sha256` still
pins regular files only and keeps its exact encoding, so every earlier receipt
and pin verifies unchanged.

source: own-work `tools/kama-llamacpp-live.py` (`install_tree`, `install_links`, `links_digest`), `tests/llamacpp-live/check-receipt.py` (`install_links_sha`, `link_chain_problem`, `--expect-install-links-sha256`, `--require-install-links`), `tests/llamacpp-live/install-links-grid.py`; S066 ldconfig(8) §DESCRIPTION; S067 ld.so(8) search order; S068 Nix NAR symlink node
verified-at: 2026-10-21 — grid and selftests at the round-21 measured commit (see `lessons/round-21.md`)
recheck: on-release — rerun the grid and both selftests after any change to the install scan, the digest encoding or the chain rule, or a new llama.cpp release layout

**Rule.** A soname (`libllama.so.0`, `libggml.so.0`, …) is a symlink in the
middle of the chain ldconfig maintains (S066), and the loader re-resolves a
slash-less DT_NEEDED name by directory search at every exec (S067). Retargeting
such a link changes the object the loader maps while a regular-file digest is
unchanged. A directory identity therefore records each link's raw target text
as its own typed entry (the NAR design, S068): `install_links` maps basename →
`readlink` text and `install_links_sha256` hashes its canonical JSON (sorted
keys, ASCII escapes; injective, unlike line-joined text).

**Fail closed, never smaller.** The producer refuses (`setup-error
install-tree-unpinnable:…`) when the install directory holds an entry it cannot
pin: an unreadable member, a failed lstat/readlink, a name with a control
character, or anything neither a regular file nor a symlink. The last covers a
`glibc-hwcaps/` subdirectory, which the loader searches before the directory
itself (observed by the round-21 LinksLoaderProof seat).

**Gate.** `install_links` is optional because legacy v3 receipts lack it; when
present, its digest must recompute, no link may share a name with a regular
member, and every chain must end at a pinned regular member through
same-directory basenames (targets with `/`, loops and dangling chains are
rejected). A consistent retarget onto another pinned member is detected only
by `--expect-install-links-sha256`; a stripped block only by
`--require-install-links` or that pin.

**Boundaries.** Binding observed regular-file bytes and link text is not
execution authentication or upstream provenance. Relative targets that leave
the directory (`../lib/…`) are rejected rather than followed; a layout that
needs them is outside this pin. System libraries resolved outside the install
directory remain unpinned.

**Round-21 falsify correction (appended).** "Fail closed, never smaller" above
is superseded: the producer refuses only loader-relevant or unrepresentable
entries (`glibc-hwcaps` of any type, links not resolving to a regular member,
special files, control-character names, unreadable or unhashed members); other
subdirectories are recorded by name in `install_unpinned` with contents outside
the pin. The links digest is always present when the block is (no null). The
ldconfig chain is S066's; "re-resolved at every exec" is kama's inference from
S067, whose step (4) reads the ldconfig cache.

## Round-22 supplement — helper I/O refusal (2026-10-21)

source: S075 Python 3.14.8 open; S076 os introduction Note and os.lstat; S077 os.access counterexample; own-work `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/install-io-grid.py`
verified-at: round-22 committed measurement recorded in `corpus/lessons/round-22.md`
recheck: `python3 tests/llamacpp-live/install-io-grid.py --arm both --json` (frozen arm intentionally red); `--arm current --json` and `--selftest` must be clean

The R21 producer's `install_links(server, tree)` backstop already rejected
ordinary unreadable/unhashed members. Its lower-level `install_tree` helper
nevertheless returned an empty/null pair after listing failure or a smaller
regular-file map and comparable digest after stat/read failure. This appendix
narrows the improvement to that helper's contract and its direct consumers,
not a newly discovered producer-level escape or retroactive receipt validation.

`install_tree` now raises its own `SetupError` with
`install-tree-unpinnable:<stage>:<member where applicable>:<error detail>` on
any OSError from the operations it actually performs. The exception cause
retains the originating error. Successful regular-file maps and the sorted
`name sha\n` encoding are unchanged. Symlinks, directories and special entries
remain intentionally outside this map; `install_links` separately implements
their existing policy. A permission precheck is not a replacement for handling
the real operation (S077).

The matrix's frozen/current results are helper outcomes. Its supplementary
`paired_problems` records the old two-helper backstop after a transient injected
fault; it neither launches the server nor claims a producer CLI experiment.
List failures returning null and member omissions returning digests are counted
separately. `check-receipt.py` still accepts the historical JSON schema: it
cannot infer files an older producer omitted, and a digest copied from that
partial receipt is not an independent complete-directory pin.

This is a scan-time, non-atomic observation. C1 handles raised I/O errors only.
The lstat→open replacement window (including a FIFO that blocks), in-place
rewrites during a read, replacement after hashing/before launch or after
launch, unpinned subdirectory contents, external system libraries and loader
configuration remain outside the guarantee. No authenticated execution,
race-safety, model-quality or current registered-endpoint health is inferred.

R21 source-correction representation repaired in R22: current readings use
S078/S079/S080 in place of S066/S067/S068. The chain pattern is documented,
the loader search includes a cache step rather than a directory walk at every
exec, and NAR is serialization prior art rather than every store-path hash.
The source-row changes and bounded quotes are in the round-22 lesson Gate;
historical paragraphs/rows above remain unchanged.

R22 residual source clarification: current Python-source readings use
S087/S088 (superseding S075/S076). The `/3.14/` documentation URL floats
across micro releases: first read3.14.8, later read3.14.9, same quoted error
semantics. Neither page is a fixed3.14.8 URL pin; the host's installed version
and the documentation render are separate observations.

**Measured diagnostic boundary.** The matrix grades refusal class, stage,
member and exception cause; the trailing error-description text is
informational, not a graded property (the detail-erased mutant in
`residual/FinalClaim/FinalClaim/` passes). Producer stat/read diagnostics now
name the first failing operation/file, for example `read:'X':Permission denied`,
rather than the former later-scan `X:unreadable`/`X:not-hashed` list.
The `install-tree-unpinnable:` prefix and actual refusal remain unchanged;
no multi-error aggregation or exact description-text guarantee is credited.

**Round-45 re-verification at b11889 (appended 2026-10-26; S484, S485).** The lifecycle statements this entry rests on (S041, S046, S055, all b11755) were re-run on the official llama.cpp b11889 binary (S484: asset digest `sha256:2076290f…d350`, `llama-server` sha256 `248e790d…f7a7`) with the same model and tool: three receipts (S485, `.ufo/waves/round-45/c1/live/receipt-1.json`..`-3.json`) each pass all 11 checks — exact loading 503 envelope, ready `/health` body `{"status":"ok"}`, `/v1/models` id = alias with owned_by `llamacpp`, `/metrics` 501, probe MODEL_OK and MODEL_MISMATCH, SIGTERM teardown returncode 0 without SIGKILL. These are sampled instants on one fixture model, not a guarantee for later builds; the round-17 "3 ms" teardown figure is a sampled duration (b11889: 15, 9 and 7 ms) and is not re-asserted. Ledger: `registry/recheck-r45.tsv`.
