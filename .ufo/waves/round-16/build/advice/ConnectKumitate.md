# ConnectKumitate — kumitate × kama C1/C2 overlap scan (round 16, build wave 2)

Read-only seat. Read: kumitate `SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md`;
kama `PROVINCE.md`, `SKILL.md`, the round-16 spec/frozen cache, and the
`corpus/knowledge` files those point at. No installs; no lane gate, harness or
test run. Writes: this file only.

## Axes

The round declares **operability** and **calibration** (calibration 7 is the
lowest). C2 is the operability artifact (acquire a live endpoint without
becoming one); C1 is the calibration artifact (one verdict must not overreach).

## 1. Contested scope — rulings

| Surface | Ruling | Evidence |
|---|---|---|
| Local model serving, including llama.cpp router mode | **kama** | kumitate `PROVINCE.md:27` — "Local model serving and endpoints → kama."; kama already owns router identity in `corpus/knowledge/served-identity-crosswalk.md:28` |
| Route/alias resolution to a local endpoint | **kumitate** resolves; **kama** grades the resolved endpoint | `corpus/knowledge/cross-lane-scope.md:28` — "**Kumitate** owns how a dispatch/alias resolves; **kama** owns what the resolved local baseURL serves." |
| Router-mode per-request `model` field | **kumitate**-shaped (route selection); kama may record the named model's status only | llama.cpp b11755 `tools/server/README.md:1488` — "`model`: (Required in router mode) The model name, used to route the request to the right instance." |
| `~/.local/bin/omp` builtin `LLAMA_CPP_BASE_URL` → `127.0.0.1:8080` | consumer surface = **kumitate**; endpoint identity = **kama** | kama `corpus/knowledge/consumer-registry.md:101` owner cell — "`kumitate` (omp binary / dispatch tooling)"; `alias-endpoint-normalization.md:39` — "the separate local llama-server endpoint is not an alias route." |
| `probe-*` route-health scripts | **kumitate** | kumitate `SKILL.md:394` — "`probe-*` scripts = bounded route-health probes"; kama `runtime-health-surface-matrix.md:22` — "Routing/gateway health dispatch is kumitate's surface." |
| `~/.local/opt` + `~/.local/bin` installs | operator-authorized; no lane owns the host path; kumitate documents the convention | `~/.omp/agent/RULES.md:7` channel order; kumitate `remaining-scripts-census.md:562-566` (cargo shim at `~/.cargo/bin/cargo`) |

Adjacent but not contested:

- MODEL_LOADING is **not** a routing-health outcome. Kumitate's
  `ROUTING_HEALTH_OUTCOMES` is `ok | capacity | lane_timeout | quality_degraded |
  process_exit` (`SKILL.md:450`); do not add a loading state there.
- kama cannot repoint a consumer even if it wanted to: `PROVINCE.md:45` —
  "**Write boundary (hard):** kama never writes to `~/.config`, `~/.omp`, or systemd".
- kumitate's own North Star is OMP seat routing: `SKILL.md:493` — "No per-lane
  `model` param. Routing = the lane role's pinned route". A llama.cpp router's
  per-request `model` field is a different layer, but the same ownership logic
  applies: selection is dispatch, the selected instance's identity is kama.

## 2. What kama must hand off rather than absorb

1. Any edit to `~/.omp/agent/config.yml`, `modelRoles`, `agentModelOverrides`,
   `retry.fallbackChains`, or aliases → kumitate. kama `PROVINCE.md:40-41`
   already refuses "dispatch/route mechanism (kumitate)".
2. The choice of *which* model a fleet seat requests from a router → kumitate.
   kama may report `status.value` for a named model, never which one to ask for.
3. The `~/.local/bin/omp` builtin default row: kama owns the endpoint verdict,
   kumitate owns the consumer surface (registry owner cell above).
4. Advertising the ephemeral server: C2 must not export `LLAMA_CPP_BASE_URL`,
   append a `registry/endpoint-consumers.tsv` row, or write
   `registry/history`. [INFERENCE] any of those would convert a lane-local
   measurement into a consumer/route change outside kama's authority.

## 3. Reusable conventions worth taking from kumitate

- **Single-sourced vocabulary.** kumitate `SKILL.md:425` — "Vocabularies are
  single-sourced; learn the source, cite it, never restate a second copy."
  kama still restates its six verdicts in `SKILL.md:11-13`; after C1 the tool's
  `VOCAB` (`tools/kama-probe.sh:60`, now including `MODEL_LOADING`) is the
  source. The SKILL edit should cite it, not carry a seventh parallel list.
- **Versioned opt dir + bin symlink + documented reversal.** lean-cargo installs
  `~/.cargo/bin/cargo` over the rustup proxy with a backup and an uninstall line
  (`kumitate/corpus/knowledge/remaining-scripts-census.md:562-566`);
  `~/.local/opt/ghidra_12.1.4_PUBLIC` is the same versioned-dir pattern
  (`kimi-config-plane.md:258`). C2's `~/.local/opt/llama-b11755` +
  `~/.local/bin/llama-server` matches; the receipt should name both the symlink
  and the versioned realpath, and the version dir is what an operator uninstalls.
- **Pre-registered runnable counts.** kumitate `corpus/QUALITY.md:23` (Q3) —
  "every count carries its counting command and a dated re-run";
  `:74` (Q14) — "evidence pointers never live under `/tmp`". C1's committed matrix plus `measure.py` satisfies
  Q3. C2 deletes its temp log after copying matched lines, so it satisfies Q14
  only if the receipt carries the retained lines (the LiveHarness spec does).

## 4. Router-mode second-order effect on C1

- The loading-503 middleware is the **single-model** path. `server.cpp:152-154`
  computes `is_router_server` from an empty model path; router mode stores
  `ctx_http.is_ready.store(true)` immediately after `ctx_http.start()`
  (`server.cpp:460`), while single-model stores it only after `load_model`
  (`server.cpp:515`). A router therefore answers 2xx with per-model
  `status.value` (`server-models.cpp:2345-2347`) inside an OpenAI-shaped
  `{"data": [...]}` envelope (`server-models.cpp:2448-2450`), not 503.
- Consequence: `MODEL_LOADING` / `llamacpp-loading` is correct only for the
  single-model process. A router can list `status.value: "loading"` **or**
  `"unloaded"` in a 200 body and the current id match would still say
  `MODEL_OK`. Do not extend the verdict to routers this round; name the mode in
  the reason's scope text and in the knowledge entry. [INFERENCE] a router's
  `unloaded` model is available on demand, so grading it as loading would be a
  false negative.
- C2's launch shape (`-m model`) selects single-model mode, so the live receipt
  is in-scope for C1's envelope. That is a real strength of the C2 design and
  should be stated, not left implicit.
- Minor: while loading, `middleware_server_state` runs before
  `middleware_validate_api_key` (`server-http.cpp:354-357`), so a loading
  server returns 503 even to a request that will later be 401. `MODEL_LOADING`
  says "not foreign / not ready", not "access will succeed"; say so in the
  knowledge entry.
- Minor: the LiveHarness argv uses `--no-webui`, which b11755 itself calls
  deprecated — `server-http.cpp:373-374` names `--ui/--no-ui` as current. It
  parses at b11755; the version pin is what keeps that true.

## 5. Move (one, bounded): make C2's producer identity explicit and enforced

**Evidence.**

- The declared **asset** digest is verifiable locally and matches: the retained
  archive `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 bytes)
  hashes to `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`.
  The installed executable is a different file:
  `sha256sum ~/.local/opt/llama-b11755/llama-server` =
  `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`.
  It is a 17,864-byte ELF launcher: `readelf -d` shows
  `NEEDED libllama-server-impl.so` and `RUNPATH $ORIGIN`; the HTTP code is
  `libllama-server-impl.so` = `e404b91a…59ed`.
- My GitHub API re-check was refused — "API rate limit exceeded for
  179.218.13.209" — so remote confirmation was not re-obtained; the local
  archive is what grounds the asset digest above.
- `shutil.which('llama-server')` plus a recorded realpath+sha256 (the
  LiveHarness item, `.ufo/waves/round-16/build/spec.json`) **records** but does
  not **enforce**. A repointed
  `~/.local/bin/llama-server` or a PATH shadow would pass every `checks` entry.
  `which -a llama-server` currently returns only the lane symlink →
  `/home/vgpnk/.local/opt/llama-b11755/llama-server`.

**Proposed move.** In `tools/kama-llamacpp-live.py`, split installation identity
from execution identity and enforce the latter:

- Add `--server-sha256 HEX` (optional). Compare it to the **executable** digest
  (the `realpath` target) and exit 3 on mismatch **before launch**, mirroring
  the existing `--model-sha256` behavior.
- Receipt fields: `server_path` (as invoked), `server_realpath`,
  `server_sha256` (computed executable), `server_impl_sha256` (the
  `libllama-server-impl.so` beside it), and `asset_sha256` with an explicit
  status — `verified` when the retained archive is re-hashed and equals the
  declared asset digest, else `declared-not-recomputed`. Never place the
  tarball digest in `server_sha256`.
- One `checks` entry `server_identity` = pin supplied ∧ executable digest
  matches. The version-dir expectation is recorded as `server_realpath` and is
  gated only when `--server-root` is passed, so a correct binary installed
  elsewhere is not refused. Keep it in the same `checks` array so exit 1 on
  failure is the existing rule.

Why this is non-obvious: both the C2 prose and the install-chain audit carry
`753bfa73…` as "the sha256", but the run executes a different 18 KB loader plus
a 7.3 MB library. Without the split, a receipt can truthfully say "asset sha256
753bfa73" and falsely imply it pinned the code that answered HTTP; an
implementer who wires `--server-sha256` to the quoted asset digest would refuse
a correct install (exit 3) on every run.

**Axes.** Calibration up: the producer identity becomes a measured
precondition instead of prose. Operability neutral-to-up: optional flag, typed
exit 3, no new writes, no config, no route change. No other axis harmed.

**Risks.** (a) Pinning only the loader leaves `libllama-server-impl.so`
mutable; the versioned dir and the archive digest are the whole-tree anchors —
name that limit. (b) Requiring the pin would add friction; keep it optional for
ad-hoc runs and require it on L1's command line. (c) `readelf`/`ss` are host
tools; the "stdlib only" rule is about Python dependencies, and the tool already
shells to `bash` and the server. [INFERENCE] `$ORIGIN` means moving the loader
without its libs fails to start rather than silently loading a system copy.

**Verification (L1).**

1. `--server-sha256 b6a31a8e…` → exit 0, `server_identity` passes, receipt has
   `asset_sha256.status = verified` (the retained archive re-hashes to
   `753bfa73…`).
2. `--server-sha256 753bfa73…` (the asset digest) → exit 3 before launch; no
   listener is created and no server log line exists. This is the falsifier for
   the new field.
3. `--server` pointing at a copy with a different digest → exit 3. A repointed
   symlink therefore cannot pass silently.
4. Include `server_realpath` and `server_impl_sha256` in the receipt so the
   version dir, not the PATH spelling, is the durable pointer.

## 6. One-line hand-offs for L1

- **LiveHarness** (owner of `tools/kama-llamacpp-live.py`): the move above.
- **ScribeSkillSection**: add MODEL_LOADING to `SKILL.md:11-13` by citing
  `tools/kama-probe.sh` `VOCAB`, not by restating a seventh list.
- **ScribeKnowledgeEntry**: keep "router mode" in the scope limits and name the
  **single-model llama.cpp process** as the subject of the 503 envelope.
- **CriticC2ServiceBoundary / SentinelInstallChain**: keep the asset and
  executable digests distinct; do not report `753bfa73` as the binary's digest.

## 7. Limitations

- Read-only; no endpoint contacted and no server launched. Host observations
  were `which -a`, `ls`, `sha256sum`, `readelf -d`, `ldd` on the named install.
  Source reads are raw.githubusercontent at `704366d76`
  (`server-http.cpp`, `server.cpp`, `server-models.cpp`, `README.md`).
- The asset digest was verified **locally** against the retained archive
  (`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` → `753bfa73…`). The
  remote GitHub API re-check was rate-limited, so the archive's provenance
  rests on the round context and the install-chain item, not on a fresh API
  read.
- `tools/kama-probe.sh` was read mid-wave (its `VOCAB` already names
  `MODEL_LOADING`); line numbers there may shift under the sibling edit.
- kumitate core reads were `SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md`.
  Two note files beyond that declared bound were opened only to ground the
  install-convention bullet — `corpus/knowledge/remaining-scripts-census.md`
  (lean-cargo shim) and `corpus/knowledge/kimi-config-plane.md` (ghidra path),
  the latter via grep hits. No other kumitate corpus was read.
- No installs or upgrades performed.
