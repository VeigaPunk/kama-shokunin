# kama-shokunin — Province

**Domain:** local model serving & endpoint health — local LLM endpoints, baseURL
drift, served-model reconciliation, probe conventions.

**Owns (surfaces):**

| Surface | Concrete artifact on this box |
|---|---|
| producer discovery & read-only service inspection of local serving ports | `tools/kama-probe.sh listeners` (`ss -ltn` loopback enumeration + per-listener classification). The serving unit formerly pinned here — `~/.config/systemd/user/qwen-coder.service` (llama-server, `127.0.0.1:34113`) — is deleted; row-absent since snapshot `20261014T124232Z` (`registry/history/DELTA.md:20`). kama governs discovering whatever serves these ports and never claims an installed server |
| baseURL pins in surviving/loadable consumers | the three surviving registry rows in `registry/endpoint-consumers.tsv`: `~/.local/bin/omp` (`LLAMA_CPP_BASE_URL` fallback → `http://127.0.0.1:8080`, `file_match=inherited`, not proof of an effective environment-selected endpoint), `$UFO_SRC/config/the-tick.machine.json:16`, `$UFO_SRC/scripts/local-helper.mjs:8`. Historical, no longer live pins: `~/.config/opencode/opencode.json:158` (the provider block was removed; the file is now 5 lines holding `$schema`/`theme`/`autoupdate` only) and `~/.config/opencode/agents/janitor.md:21` (file deleted); both verified by read-only host inspection, never rewritten |
| served-model-id reconciliation | `GET /v1/models` vs `--alias` vs the configured model id |
| liveness/readiness probe conventions | `/health`, `/props`, `/slots` |
| which vLLM process serves `/health` — weight cache daemon (`vllm preload`) versus inference server | `corpus/knowledge/runtime-health-surface-processes.md` — source readings of the v0.31.0 release note and pull request 58552 (S480, S481); names the process from the sources and samples no endpoint |
| endpoint-drift detection + invocation history | `tools/kama-probe.sh snapshot`, `registry/endpoint-consumers.tsv`, `registry/history/{latest.tsv,DELTA.md}` |
| endpoint-consumers cross-lane registry | `corpus/knowledge/consumer-registry.md`, `cross-lane-scope.md` |
| lane instruments (the capability repertoire, `SCORECARD.md` canonical list) | `tools/kama-ollama-evidence.py` (offline Ollama capture replay), `tools/gguf-identity.py` (GGUF declared identity), `tools/kama-context-capacity.py` (fixture context-capacity receipt), `tools/instrument-agreement.py` (run agreement), `tools/pin-watch.py` with `registry/engine-pins.tsv` (newer-release triggers for the pinned SGLang, vLLM and llama.cpp lines), `tools/digest-ledger.py` with `registry/digest-ledger.tsv` (classification of every SHA-256 the lane's documents cite), `tools/hexrun-census.py` with `registry/hexrun-ledger.tsv` (classification of every other 32-127 character hex run: git object ids, MD5 sums, over-long or abbreviated runs; round 43), `registry/staged-refusals.tsv` (staged package items the lane refuses, with rounds offered, reason and flip; round 43); `tools/append-only-audit.py` with `registry/append-only-contract.tsv` and `tools/round47-append-audit-v2-check.py`, `tools/round48-append-audit-v3-check.py` (append-only audit of the contract-declared self-description set: every commit deleting >= 20 lines from one of those files, with a deleted count equal to git numstat, the largest share of those lines any commit in the event's window holds again and the commit that restored them; round 46, v2 round 47, v3 round 48 with per-row regions, binding declarations and `regressed` in the exit semantics); `tools/kama-live-replay.py` (re-acquire a live receipt's server archive and model from the URLs its provenance records, verify both sha256 values, re-run the lifecycle and compare every check; round 47) |

**Observed state (lane baseline `c390918`, tracked snapshot `20261014T124232Z`):**
`bash tools/kama-probe.sh check` evaluates 3 registry rows — `model_ok=0`, `drift=3`,
exit 2; every row in `registry/history/latest.tsv` is `DEAD` connection-refused
(`8080` and `34113`). `ufo-fsd-thetick` and `ufo-fsd-local-helper` are
correct-pin/dead-endpoint: `file_match=yes` attests the pin, NOT a live `MODEL_OK` —
this lane reports pin correctness and serving liveness separately and never asserts
`MODEL_OK` from retired samples (`registry/history/DELTA.md:9,:12,:20` keep the former
`MODEL_OK`/`systemd-qwen-coder` state as history). Serving runtime is explicitly
unavailable on the concrete surfaces — nothing listens on `8080` or `34113` (probe
connection-refused verdicts; `systemctl --user status qwen-coder` → "Unit
qwen-coder.service could not be found"); restoring a unit is operator-owned work under the
boundary below. The outage retires nothing in this domain: server/health discovery and
drift reconciliation remain governed here — province contraction is an L0 decision.

**Actual round-5 sample (2026-10-15):** the same three rows still sample
`DEAD` / connection-refused, exit 2. Explicit UFO pins resolve `file_match=yes`;
the builtin fallback is `inherited`/`raw`, not proof of an effective runtime
URL or active traffic. Bounded service/socket metadata agrees with the
not-found producer and unserved registered ports. Full command evidence:
`.ufo/round-5/{before-check,host-shape,acceptance}.json`. This supersedes a
current-readiness reading of older successful examples without retiring the
producer-discovery domain or authorizing service restoration.

**Refuses:** model quality/eval (kengaku), credential material & auth flows (kagi),
dispatch/route mechanism (kumitate), remote web surfaces (kake). Boundary rule: kama
answers *"is the thing at this baseURL the model this config believes it is, right
now"* — never *"is the model good"* or *"is the request safe"*.

**Write boundary (hard):** kama never writes to `~/.config`, `~/.omp`, or systemd
units. Those are operator-owned; kama *detects and reports* stale pins, and the
operator repoints them. Rationale: a lane that silently repoints a credential-bearing
consumer config would be acting outside its authority (see
`corpus/lessons/round-1-safety.md`).

**Out of province → report, never absorb.** Anything found outside the domain is
named in the round report for the owning lane (see
`corpus/knowledge/cross-lane-scope.md`).

**Round-16 note — lane-owned live fixture (2026-10-20).** `tools/kama-llamacpp-live.py`
starts one llama-server child (official release b11755, installed by the
operator-authorized tooling directive at `~/.local/opt/llama-b11755`, linked
`~/.local/bin/llama-server`) with a pinned 1.2 MB GGUF kept in the lane-owned
cache `~/.cache/kama-shokunin/`, on a free loopback port that is never a
registered consumer port or a listening port, and tears it down in the same run.
This proposes narrowing round 1's "L0 must approve any endpoint outside the
declared local model registry" only for the process this tool started, **pending
L0 ratification** (`.ufo/l0-questions.md`, kama round-16); any other unregistered
endpoint still needs L0. It is not service restoration, starts no unit, writes
nothing under `~/.config`, `~/.omp` or systemd, and changes no registered row:
the three consumers stay `DEAD`. The release is a GitHub Pre-release; the
install is identified by its asset digest (S038), not the tag. The install tree,
its `~/.local/bin/llama-server` link (which now precedes `/usr/bin` on PATH) and
the cache persist on the host; removal is the operator's call.
**Round-17 note — the same fixture, stricter receipt (2026-10-20).** The lane-owned
child is unchanged in scope (same install, same pinned GGUF, unregistered
loopback ports, torn down in the run) and still **pending L0 ratification**. The
tool now emits `kama-llamacpp-live/v2`: exact ready body, harness-SIGTERM
graceful teardown with returncode 0, ownership-gated port closure, every loading
503 graded, a receipt on internal faults, and loopback-only listener ownership.
Fake-server controls run only `/tmp` fakes on ephemeral loopback ports. No
`/usr/bin/llama-server` exists, so the `~/.local/bin` link shadows nothing; the
"precedes `/usr/bin` on PATH" wording above is shell-local. The retained release
archive `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (sha256 `753bfa73…e226`)
is part of the operator-owned footprint.

**Round-18 note — v3 and listener ownership.** Same pending-ratification fixture,
same binary/model and registered-port refusal. V3 distinguishes a missed loading
observation (tool 2 / gate 3 NOT-EVALUATED) from a failed observed property; a green
receipt still proves no registered-consumer health. Linux child-owned listener
recognition now covers native ::1 and mapped 127/8 using sourced procfs decoding
(S048/S050). Wildcards remain refused. The mechanism enters core via
`corpus/knowledge/loopback-listener-ownership.md`; other engines and K05 stay frontier.
Internal BaseException faults are contained into setup-error receipts; install
retention and the llama-b11755 archive remain the operator's decisions.

Current-emitter clarification (round-18 falsify): the tool **now emits v3**;
this explicitly supersedes the round-17 “now emits v2” sentence at line73.
Internal-fault receipt promises refer to guarded lifecycle paths with writable
output, not help/usage, an unwritable output file or an unconditional guarantee
against interruption between every Python instruction.

**Round-20 frontier note — offline declarations.** GGUF header inspection and
comparison with an existing byte-pinned fixture receipt enter held ground via
`corpus/knowledge/gguf-declared-identity.md` (S058/S060). This reads the one
explicitly named local CI file and metadata only; it loads no weights and
starts no server. It is not a host-wide model inventory or proof of current
serving/loaded-weight identity. Context declaration versus effective per-slot
capacity is not model quality. Kengaku's technique overlap is acknowledged,
not absorbed. K05 across real consumers and other engines remains frontier.
Do not traverse Kagi no-enumerate/config roots to discover models.


**Round-28 core note — request-field schema.** llama-server's per-request
field schema (`tools/server/server-schema.cpp` @704366d76: hard-bound rejects,
silent clamps, handler transforms, as stored in `generation_settings`) enters
held ground for the lane-owned b11755 fixture via SKILL.md "## Round-28
request-field outcomes" (S140-S173). It describes what the server accepts and
stores for one request, not sampling quality, model identity or registered
endpoint health. Other endpoints, builds and engines remain frontier.


**Round-30 frontier→core: run agreement for lane instruments; recall population
for the self-assessment census.** `tools/instrument-agreement.py` (S178/S179
import; see `corpus/knowledge/instrument-run-agreement.md`) and the round-30
counter's declared recall population (S174–S177 plus round-29 RecallA/B) enter
held ground as lane-internal methods. Not held: the siblings' implementations
(kumitate's counter rerun, mori's network re-fetch of source rows), any claim
that agreement implies correctness, and any live endpoint or model-quality
surface. K05 and registered-consumer reconciliation remain frontier; no endpoint
was sampled this round.


**Round-31 core note — the `/v1/chat/completions` conversion layer.** The
OpenAI-compatible chat endpoint's parameter handling (alias resolution through
the pinned schema, the adapter's own validation messages and their 400/500
mapping, `logprobs` → `n_probs`, undeclared OpenAI-standard keys copied then
pruned, and the `/slots` observability boundary) enters held ground through
SKILL.md "## Round-31 chat-completions parameter outcomes", the registry
`registry/chat-param-outcomes-r31.json`, and `corpus/knowledge/chat-adapter-outcomes.md`
(S180-S192, llama.cpp b11755 @ 704366d). It is the chat adapter on the lane-owned
fixture: not served identity, not registered-consumer health, not model quality,
and not the session-level grammar transform (which `/slots` does not expose).
`/v1/completions`, other builds and engines, and K05 beyond the fixture remain
frontier. Sibling lanes hold no competing claim on this surface: kumitate's
watcher posts to `/v1/chat/completions` as a consumer and kengaku excludes the
model-serving plane (`.ufo/waves/round-31/w1/out/ConnSibling/overlap.md`).

*Appended correction, round 31 attempt 2:* the row range above reads `S180-S192`;
the actual opened rows are **S180-S191** and no `S192` exists in `corpus/SOURCES.md`
(`grep -c '^| S192' corpus/SOURCES.md` → 0; route: `.ufo/waves/round-31/w2/out/ScoutProvince/`).
The entry and the registry are correct at S180-S191; only this note's range was
written one row long.

**Round-32 note — instrument registry, meaning-graded (2026-10-24).**
`tools/gate-registry-check.py` v2 grades registry rows for meaning (table-row presence,
cell presence, exit map, cited-path existence; S193) and the round-qualified claim-row
counter `.ufo/waves/round-32/count-c2r.py` enters the registry; both are lane-internal
methods, not new serving surface. The repair exposed and fixed two prose-only
registrations (round-17 verdict census, round-26 echo-signature counter). No endpoint,
runtime or consumer surface was sampled; registered consumers stay `DEAD` and
reconciliation remains the probe's job. Frontier unchanged: `response_format` grammar
transform (S192), `/v1/completions`, other engines, K05 — the wave items under
`.ufo/waves/round-32/w1/` attack exactly these.

**Round-38 note — engine-documentation re-pin ownership (2026-10-25).**
The lane owns how its engine-documentation rows are anchored: the published
SGLang docs pages carry no version marker, and kama re-pins the two rows it
already holds (S333, S334) to release tag v0.5.22 and its peeled commit
(baa9befa…) via new rows S352, S353, with the tag inventory verified by the
lane's own `git ls-remote --tags` row S472. The generic pinning *method*
(how to pin any repo tag) is chousa's ground; the specific re-pin of the two
held docs rows is kama's. No endpoint, runtime or consumer surface was sampled
this round.

**Round-42 note — instruments named in the province (2026-10-25).** The Owns table
now lists every `tools/` and `registry/` surface the SCORECARD capability list cites,
including `pin-watch` (round 41, routed defect R41A10-9 and closure item 2) and
`digest-ledger` (round 42). Both read git objects and public tag lists; `digest-ledger`
also re-hashes the host files its ledger rows name, read-only and confined to the
scanned tree and the home directory. Neither samples an endpoint, starts a runtime or
writes anything. A release-watch *method* for pins the lane does not hold is outside
this province (no chousa document names it, checked 2026-10-25); the lane owns the
watch of its own pinned serving engines. The context-capacity source readings of
`corpus/knowledge/context-capacity-engine-sides.md` (vLLM v0.32.0, llama.cpp 704366d7
router listing) are source readings on held K05 ground, not a serving surface: no
endpoint or runtime was sampled.

**Round-43 note - the hex-run census and the health process map (2026-10-25).** `tools/hexrun-census.py` reads git objects and committed documents only; for an `upstream` ledger row it reads a committed evidence file, never the network, so the GitHub API queries that produced the evidence ran once, in round 43, by `gh api` under the operator's authenticated session, and are not part of the tool. `corpus/knowledge/runtime-health-surface-processes.md` is a source reading of two GitHub API objects (S480, S481); it names which vLLM process answers `/health` and samples no endpoint. The adjacent processes the staged round-13 amendment names (the agentic-api gateway, the Semantic Router) stay refused: a gateway and a route-selection product are dispatch-side surfaces (`corpus/knowledge/cross-lane-scope.md`), reported to the owning lane, not absorbed.

**Round-60 note — live Ollama lane-owned sample, not a registered consumer (2026-10-27).** `tools/kama-ollama-live.py` and `registry/ollama-live-pin.tsv` add a v0.40.11 child-process instrument and source-grounded captured observations (`corpus/knowledge/ollama-live-lifecycle.md`; S519–S523). The single receipt uses the lane's fixture GGUF and an unregistered loopback port under a scratch HOME/model store; it neither contacts nor changes the three registered consumers, whose last recorded state remains `DEAD`. This is not service restoration, readiness for configured consumers, model quality or general Ollama behavior. The round's claim/counter was falsified: no `live-ollama-lifecycle` capability is admitted, and child cleanup after SIGKILL remains a defect. Extending the existing lane-owned unregistered-child exception from llama.cpp to Ollama remains pending operator decision at `.ufo/l0-questions.md` (`kama | round-60`).
