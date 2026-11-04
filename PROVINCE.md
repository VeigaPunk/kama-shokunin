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
| lane instruments (the capability repertoire, `SCORECARD.md` canonical list) | `tools/kama-ollama-evidence.py` (offline Ollama capture replay), `tools/gguf-identity.py` (GGUF declared identity), `tools/kama-context-capacity.py` (fixture context-capacity receipt), `tools/instrument-agreement.py` (run agreement), `tools/pin-watch.py` with `registry/engine-pins.tsv` (newer-release triggers for the pinned SGLang, vLLM and llama.cpp lines), `tools/digest-ledger.py` with `registry/digest-ledger.tsv` (classification of every SHA-256 the lane's documents cite), `tools/hexrun-census.py` with `registry/hexrun-ledger.tsv` (classification of every other 32-127 character hex run: git object ids, MD5 sums, over-long or abbreviated runs; round 43), `registry/staged-refusals.tsv` (staged package items the lane refuses, with rounds offered, reason and flip; round 43); `tools/append-only-audit.py` with `registry/append-only-contract.tsv` and `tools/round47-append-audit-v2-check.py`, `tools/round48-append-audit-v3-check.py` (append-only audit of the contract-declared self-description set: every commit deleting >= 20 lines from one of those files, with a deleted count equal to git numstat, the largest share of those lines any commit in the event's window holds again and the commit that restored them; round 46, v2 round 47, v3 round 48 with per-row regions, binding declarations and `regressed` in the exit semantics); `tools/kama-live-replay.py` (re-acquire a live receipt's server archive and model from the URLs its provenance records, verify both sha256 values, re-run the lifecycle and compare every check; round 47), `tools/round67-worktree-landing-check.py` (declared self-record paths byte-identical to their HEAD blobs, DIRTY on any uncommitted or CRLF-translated byte; round 67), `tools/round68-receipt-pointer-audit.py` with `registry/receipt-pointer-resolutions.tsv` (every section-relative `measured/…` receipt citation resolves at a revision; round 68), `tools/round69-newest-closure-counter.py` (the newest non-author closure, fail-closed on an undated one; round 69), `tools/round74-selfdesc-canon.py` (the capability repertoire resolved from the newest table by round number regardless of heading markup; round 74), `tools/round74-receipt-claim-binding.py` (self-record receipt citations bound by explicit revision with paragraph-scoped claim grading; round 74), `tools/round74-province-host-drift.py` (host-block base-revision preservation on top of the frozen r73 drift leg; round 74), `tools/round74-seat-count-check.py` (wave seat-count prose vs items-array drift and census-before-append ordering; round 74), `tools/round72-round-scope.py` (a round's own scope graded as a verdict; round 72), `tools/round72-receipt-tip-binding.py` (every cited receipt bound to the revision it measured; round 72), `tools/round73-round-scope-cases.py` (linked-worktree, newer-round ignored and nested submodule scope cases; round 73), `tools/round73-receipt-claim-binding.py` (three-token tip claims rejected when the receipt names another revision; round 73), `tools/round73-province-host-drift.py` (the recorded host triple graded against the live triple; round 73), `tools/round75-interpretation-pins.py` (the two routed interpretation debts bound to boundary fixtures whose declared reading the committed module produces and whose reversed reading a mutated copy is caught producing; round 75), `tools/round75-survivor-probe.py` (five named source mutants of the receipt-claim module, each required red under its owning selftest arm; round 75), `tools/round75-append-accepted.py` with `registry/append-only-accepted.tsv` and `registry/append-only-declarations.md` (every audit-undisclosed deletion event graded as accepted history by a committed, hash- and class-bound register whose rows must precede the register's introduction; round 75); round 77: `tools/round77-citation-baseline.py` (baseline receipt binding), `tools/round77-append-registers.py` (two-register cutoff accounting), `tools/round77-selfrecord-round76.py` (sealed round-76 fact harness); round 78: `tools/round78-selfrecord-round77.py` (six-fact round-77 self-record grading with value-bound corrections), `tools/round78-append-registers.py` (ancestry-filtered, commit-bound register accounting at the audited revision) and `tools/round78-live-reconcile.py` (three-verdict reconcile trial against the pinned llama.cpp child); round 79: `tools/round79-selfrecord-round78.py` (six-fact round-78 self-record grading with value-bound corrections), `tools/round79-unregistered-census.py` (two-registry census of a serving listener as `registered=yes`/`no`) and the `registered` census class in `tools/kama-probe.sh listeners` (a model-API listener whose port no registry row declares) |

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

**Round-63 note — the v2 request-plane instrument, its falsified claim, and the claim registries (2026-10-28).** `tools/kama-completion-live.py` (schema `kama-completion-live/v2`) grades one real `POST /v1/completions` on the lane-owned pinned llama.cpp b11755 child: response headers, body completeness, choice shape, `id`/`created`, strict `usage`/`timings` and the server's own `/tokenize` count (`corpus/knowledge/completion-request-plane.md`; S526–S528). It serves on an unregistered loopback port through the proxy-free opener (its round-62 predecessor leaked the POST to an environment proxy, `.ufo/waves/round-63/w1/EX06ProxyEnv.md`), contacts no registered consumer and samples no model quality; the three registered consumers keep their last recorded `DEAD` state. The round-63 claim that this is a verified request-plane capability was falsified by the round's own wave (`.ufo/waves/round-63/w1/MT15C1FakeConsistent.md`: a canned answerer behind a real child's inherited listener passes the frozen counter), so `/v1/completions` stays frontier ground and no capability row is added. The self-assessment surfaces the lane keeps honest are `registry/capability-claims-r63.tsv` (12 frozen capabilities bound to live runs, counter `tools/round63-c2-counter.py`; its host-conditional row for `context-capacity-receipt` records that a running llama-server — the operator's own, a leaked lane child, or a concurrent seat — makes the K1 cell refuse with `host-not-idle-before-K1`), its predecessors `registry/capability-claims-r62.tsv` and `registry/ollama-live-claims-r61.tsv` (the round-61 claim registry for `live-ollama-lifecycle`), and `tools/round63-c1-counter.py` (the request-plane counter). These are lane-internal methods: no consumer file is edited, no service is started outside the lane-owned children, and no `~/.config`, `~/.omp` or systemd path is written.

**Round-65 note — new Windows host census (2026-10-31).** The lane moved to a
new host: Windows 10.0.26200, Git Bash (MinGW64, git 2.55.0.windows.3), CPython
3.13.15 (`python`; `python3` is the Microsoft Store alias stub, exit 49). Every
concrete former-host artifact this province named was re-checked read-only on
the new host; each absent surface is recorded here with its marker tag
(`tools/round65-province-host-audit.py` re-derives this list):

- absent-on-this-host (2026-10-31) `province-host:omp-binary` — `~/.local/bin/omp`
  does not exist; no `LLAMA_CPP_BASE_URL` in the environment; `~/.omp/` holds only
  `agent/settings.json` whose single key is `shellPath` (no endpoint pin).
- absent-on-this-host (2026-10-31) `province-host:llama-b11755-install` and
  `province-host:llama-server-link` — `~/.local/opt/llama-b11755` and
  `~/.local/bin/llama-server` do not exist (the round-16 fixture footprint stayed
  on the former host; removal there remains the operator's call).
- absent-on-this-host (2026-10-31) `province-host:kama-cache-gguf` —
  `~/.cache/kama-shokunin/` (the pinned fixture GGUF) does not exist.
- absent-on-this-host (2026-10-31) `province-host:llama-b11755-archive` —
  `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` does not exist.
- absent-on-this-host (2026-10-31) `province-host:qwen-coder-unit` — no systemd
  on this host; `~/.config/systemd/user/qwen-coder.service` does not exist
  (row-absent since snapshot `20261014T124232Z` on the former host; unchanged).
- absent-on-this-host (2026-10-31) `province-host:opencode-json` —
  `~/.config/opencode/opencode.json` does not exist; the directory holds
  `opencode.jsonc` whose only key is `$schema` (no provider block, no baseURL
  pin; read-only shape inspection).
- absent-on-this-host (2026-10-31) `province-host:janitor-md` —
  `~/.config/opencode/agents/` does not exist.
- absent-on-this-host (2026-10-31) `province-host:ufo-src` — `UFO_SRC` is unset
  and no ufo-fsd checkout was located, so the two `$UFO_SRC`-pinned consumer
  rows cannot be evaluated on this host (`file=missing` by absence of the tree,
  not by pin drift).

**Round-67 note — serving-side fixture surfaces and the interpreter precondition
(2026-10-31).** The round-67 extension of `tools/round65-province-host-audit.py`
declares three more host surfaces: the serving-side installs the lane-owned live
fixtures need (paths pinned in `registry/ollama-live-pin.tsv` — the round-16
llama.cpp fixture and the round-60 Ollama fixture are governed instruments on
the former-host shape and cannot run here without them), and the interpreter
precondition every registered `python3 tools/...` command carries. Each absent
surface is recorded here with its marker tag:

- absent-on-this-host (2026-10-31) `province-host:ollama-v04011-install` —
  `~/.local/opt/ollama-v0.40.11` does not exist (the pinned v0.40.11 install
  tree stayed on the former host; removal there remains the operator's call,
  `kama | round-60` L0).
- absent-on-this-host (2026-10-31) `province-host:fixture-gguf-model` —
  `~/.cache/kama-shokunin/models/stories260K.gguf` does not exist (the pinned
  fixture GGUF the round-16 and round-60 live tools load; the parent cache
  surface `province-host:kama-cache-gguf` is recorded absent above).
- absent-on-this-host (2026-10-31) `province-host:python3-interpreter` —
  `python3` on PATH is the Microsoft Store app-execution alias stub, not a
  usable interpreter: `python3 -c "import sys"` exits 49 with "Python was not
  found" (observed round 65), and the alias can report "command not found" or
  open the Store instead of running Python (S539). The audit's `spawn` kind
  grades a real run (exit 0), not PATH existence; every registered
  `python3 tools/...` command runs here only adapted under `python`
  (`tools/round65-host-census.py` records the adaptation).

Serving-runtime census (receipts `.ufo/waves/round-65/measured/endpoint-census.out`,
`.ufo/waves/round-65/measured/consumer-surfaces.out`, `.ufo/waves/round-65/measured/consumer-shape.out`):
no process listens on the registered consumer ports `8080` or `34113` or the
Ollama default `11434` on any interface (full `netstat -ano -p tcp` listen set),
and HTTP probes of `127.0.0.1:8080/health`, `127.0.0.1:8080/v1/models`,
`[::1]:8080/health`, `127.0.0.1:34113/health` and `127.0.0.1:11434/api/tags`
all end in connection refused (curl exit 7, HTTP 000). `ollama` and
`llama-server` binaries are absent from PATH. The three registered consumer
rows keep their last recorded `DEAD` state; on this host the probe gate itself
refuses fail-closed (`ss` absent, `flock` absent), which is the correct
verdict, not a gate defect. Restoring any serving runtime stays operator-owned
work under the write boundary above. The lane-owned live fixtures
(`kama-llamacpp-live`, `kama-completion-live`, `kama-ollama-live`) cannot run
here without their pinned engine installs; they stay governed instruments on
the former host shape, and the round-65 host census
(`tools/round65-host-census.py`) records which lane instruments run on this
host instead. A tracked wave-artifact path
(`.ufo/waves/round-52/w1/out/` containing a `|` character) cannot be checked
out under NTFS, so instruments that clone the lane (the round-42
self-description reconciler selftest) refuse fail-closed on this host; that
path question is filed at `.ufo/l0-questions.md` (kama round-65).

## Host re-derivation — round 71 (2026-11-03; the round-65/67 notes above stay as written)

The markers above were recorded on the 2026-10-31 Windows host. This lane now runs on a different
host: `uname -s` → `Linux`, `uname -r` → `7.2.11-arch1-1` (2026-11-03). Each surface below was
re-derived read-only on this host; the counter `tools/round71-province-host-claims.py` grades these
corrections against live probes and rejects a correction whose claimed verdict disagrees.

- correction-on-host (2026-11-03) `province-host:omp-binary` — present: `test -e ~/.local/bin/omp` exit 0; `command -v omp` → `/home/vgpnk/.local/bin/omp`.
- correction-on-host (2026-11-03) `province-host:llama-b11755-install` — present: `test -d ~/.local/opt/llama-b11755` exit 0 (`LICENSE`, `llama-server`, `libggml-base.so` present).
- correction-on-host (2026-11-03) `province-host:llama-server-link` — present: `readlink -f ~/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`.
- correction-on-host (2026-11-03) `province-host:kama-cache-gguf` — present: `test -d ~/.cache/kama-shokunin` exit 0; it holds `models/`.
- correction-on-host (2026-11-03) `province-host:llama-b11755-archive` — present: `test -f ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` exit 0; sha256 begins `753bfa73…`.
- correction-on-host (2026-11-03) `province-host:qwen-coder-unit` — absent: `systemctl --user show qwen-coder.service -p LoadState -p ActiveState` → `LoadState=not-found`, `ActiveState=inactive`; the marker's "no systemd on this host" reason is itself false (systemd is present), but the unit surface is absent.
- correction-on-host (2026-11-03) `province-host:opencode-json` — present: `test -f ~/.config/opencode/opencode.json` exit 0; the file holds only `$schema` and `autoupdate` (no provider block, no baseURL pin).
- correction-on-host (2026-11-03) `province-host:janitor-md` — absent: `test -d ~/.config/opencode/agents` exit 1.
- correction-on-host (2026-11-03) `province-host:ufo-src` — present: `test -d ~/Projects/ufo-fsd-alpha` exit 0 and `~/Projects/ufo-fsd-alpha/config/the-tick.machine.json` exists; `UFO_SRC` is still unset, so the probe's `$UFO_SRC` step is empty but its declared checkout fallback resolves.
- correction-on-host (2026-11-03) `province-host:ollama-v04011-install` — present: `test -d ~/.local/opt/ollama-v0.40.11` exit 0 (`bin/`, `lib/` present).
- correction-on-host (2026-11-03) `province-host:fixture-gguf-model` — present: `test -f ~/.cache/kama-shokunin/models/stories260K.gguf` exit 0 (1,185,376 bytes).
- correction-on-host (2026-11-03) `province-host:python3-interpreter` — present: `python3 -c 'import sys;print(sys.version.split()[0])'` → `3.14.8`, exit 0; the Store-alias stub is not this host's `python3`.

The four prose claims the same notes make are corrected here against live probes (the counter
carries them as declared extra surfaces; the correction tag namespace is the same):

- correction-on-host (2026-11-03) `province-host:host-identity` — absent: `uname -s` → `Linux`, `uname -r` → `7.2.11-arch1-1`; the 2026-10-31 note describes a Windows host this lane no longer runs on.
- correction-on-host (2026-11-03) `province-host:python3-alias` — absent: `python3 -c "import sys;print(sys.version.split()[0])"` → `3.14.8`, exit 0; `python3` is a real interpreter on this host, not the Microsoft Store alias.
- correction-on-host (2026-11-03) `province-host:ntfs-path` — absent: a scratch repo under `/fast/scratch/hyaku/kama-r71/` commits and checks out `pipe|name.txt` (`git checkout -- .` exit 0), so the NTFS-invalid-path limitation does not apply here; the reconciler's selftest runs on this host.
- correction-on-host (2026-11-03) `province-host:ss-flock` — absent: `command -v ss flock` → `/usr/bin/ss`, `/usr/bin/flock`; the probe gate's fail-closed refusal class does not apply on this host.

**Round-71 note — the report-time instruments and the host re-derivation (2026-11-03).**
`tools/pre-report-gate.py` runs the round's four reconciled instruments plus a round-worktree
cleanliness arm and emits one `PRE_REPORT` verdict; `tools/census-waiver-boundary.py` grades the
census's waiver/not-evaluated semantics with seven cases and kills the five round-70 shims;
`tools/round71-province-host-claims.py` re-derives every `province-host:` marker and four declared
prose claims against this host. All three are lane-local, read-only instruments (the province
counter runs git and path/spawn probes; the pre-report gate runs the lane's own instruments; the
boundary tool runs synthetic census fixtures under a scratch dir). No endpoint, consumer or service
was sampled; the registered consumers keep their last recorded `DEAD` state.

Round-73 host-identity block (2026-11-03). Host triple: `uname -s` -> `Linux`; `uname -m` -> `x86_64`; `/etc/os-release` `ID` -> `arch`. Graded by `tools/round73-province-host-drift.py`; a host move is answered by appending a later block, never by editing this one. recorded at 868dd701bff531be6a36da742d3418f98818e5eb (round-74 freeze base; the v2 preservation leg compares the block text with this token sentence stripped).

**Round-73 note — the three instruments and the recorded host identity (2026-11-03).**
`tools/round73-round-scope-cases.py` (six-case round-scope counter: the three inherited r72 cases
plus `worktree`, `ignored-older-label` and `submodule`; the pre-report gate's arm 6),
`tools/round73-receipt-claim-binding.py` (the frozen r72 receipt-tip binding plus a claim pass over
the citing line) and `tools/round73-province-host-drift.py` (grades the newest
`Round-<N> host-identity block` against the live `uname -s` / `uname -m` / `/etc/os-release` `ID`
triple) are lane-local read-only instruments: they read git state, the lane's self-record and
`PROVINCE.md`, and sample no endpoint, start no runtime and write nothing outside a scratch dir.
The host-identity block appended above records this host's triple; a host move is answered by
appending a later block, never by editing that one. The three registered consumers keep their last
recorded `DEAD` state.

Round-76 instruments (2026-11-04): `tools/round76-receipt-scope.py` (classifies a self-record's
citation population under the declared fence and record-path scope; `--all-findings` lists every
non-record path in each receipt's delta), `tools/round76-selfrecord-facts.py` (re-derives eight
declared self-record facts at the revisions they name and counts value-bound corrections) and
`tools/round76-append-exempt.py` (accounts every append-only audit event once across the
line-bound accepted register, the strict exempt-head class register, restoration and disclosure,
and preserves the multi-register introduction cutoff). They read committed git state, the lane's
registers and self-record, execute no endpoint call and write nothing outside their scratch.

**Round-79 note — the unregistered-listener census class and the tenth gate arm (2026-11-04).**
`tools/kama-probe.sh listeners` gains one census column, `registered` (`yes` when a model-API
listener's port is a registry row's declared baseURL port, `no` when it answers a model API that
no row governs, `-` otherwise) and summary keys `governed`/`unregistered`/`registry`. The class
is a governance dimension, not a verdict: the verdict vocabulary and exit codes are unchanged,
no registry row is admitted, and the live-host leg
(`UNREGISTERED_CENSUS_LIVE`, `tools/round79-unregistered-census.py`) names ungoverned listeners
for the operator without gating anything. The counter's graded legs run the probe with `--port`
so only the lane-owned fixture listener enters the counts; admitting a consumer pin for any
ungoverned listener stays operator-owned, and kengaku's endpoint identity pin (its S178) reads
the same host listener for eval identity, not governance — neither lane absorbs the other's
scope. `tools/pre-report-gate.py` now composes the three round-78 instrument selftests as its
tenth arm (`round78-instruments`), so a scored gate run executes the counters a round lands.

**Round-80 note — the two registers and the third self-record grader (2026-11-04).**
Three instruments and two registers enter the lane's repertoire on ground this province already
holds. `tools/round80-selfrecord-round79.py` grades the round-79 self-record's declared facts
against the receipts those facts cite (calibration ground: the lane's own self-description
versus observed repo state; no endpoint is sampled). `registry/engine-pin-relations.tsv` plus
`tools/round80-engine-pin-relations.py` relate every pinned serving-engine ref the lane holds —
llama.cpp `b11755`, the S553 commit anchor `39febd2a` (= tag `b11963`'s peeled commit), kengaku's
S178 tag `b7200`, sglang `v0.5.22`, vllm `v0.32.0` — to that engine's upstream newest release
and tag identity, re-deriving every cell from a committed `git ls-remote --tags` list; it reads
public tag lists only, never the network at grading time when `--tags-dir` is named, and samples
no endpoint. `tools/round80-ollama-census.py` and `registry/unregistered-class-engines.tsv`
exercise the `registered` census class on a second engine: the lane-owned pinned Ollama v0.40.11
child, started under a scratch HOME and model store on a free unregistered loopback port, one
model created from the fixture GGUF, both registry legs graded, torn down in the same run. That
child is the round-16/60/61 fixture boundary, not service restoration: no `~/.config`, `~/.omp`
or systemd write, no registered consumer contacted, no consumer row admitted, and the live-host
leg gates nothing. The three registered consumers keep their last recorded `DEAD` state; K05
declared-versus-served context capacity across real consumers remains frontier.

## Round-81 instrument note (appended 2026-11-04)

The append-only acceptance surface is now lane-owned instruments: `tools/round81-append-debt.py`
grades the frozen audit's acceptance population under the late-acceptance rule (a later round's
row binds by strict commit ancestry and round order, exact hash/count/class, base population;
`pending` is the graded round's own visible debt), `tools/round81-late-rows.py` generates and
`--check`s the deterministic row set, and `registry/append-only-late.tsv` is the committed
late-acceptance register. The frozen `tools/round75-append-accepted.py` and
`registry/append-only-accepted.tsv` stay as history: their pre-introduction cutoff cannot accept a
post-introduction event, which is why the pre-report gate's arm 8 now composes the new counter.
Late acceptance never restores bytes and never changes the audit's `unrestored` count.

**Round-82 note — the late-row rule and the recheck trigger (2026-11-04).** The lane's two new
instruments: `tools/round82-selfrecord-round81.py` (re-derive the round-81 self-record's six declared
facts at its sealed revision and grade dated value-bound corrections) and `tools/round82-late-delta.py`
re-derives a late register's round delta against the frozen
round-81 generator (carried rows bound byte-wise to the base revision, new rows by cell and by the
accepting/deletion round order), and `tools/round81-append-debt.py` now binds each late row's OWN
introducing commit (`git blame`) instead of one commit for the whole register — the row-level reading
its prose always named. Freshness ground: a `pin-watch` `behind` relation is a recheck trigger, and the
only honest resolution is re-opening the pinned document at its own ref; the round-82 read compares
llama.cpp `tools/server/README.md` at `b11755` and at `b12103` (the `### GET /health` statement is
byte-identical, one line shifted, while the document grew 2402 → 2620 lines), recorded in
`corpus/knowledge/pin-recheck-trigger.md`. No consumer config, unit or host surface is touched.
