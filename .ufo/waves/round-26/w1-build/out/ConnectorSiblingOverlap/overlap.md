# Sibling-overlap scan (adjacency) — llama.cpp / llama-server error knowledge

Scan date: 2026-10-23. Scope: siblings under /home/vgpnk/Projects/shokunin/*-shokunin
(kengaku, kagi, kumitate, kake, tsukuroi, mado, mori, tabi, souji, kasegi, kotoba,
kotodama, kake, tameshi, kaidoku, chousa, lore, game-dev-2d/3d, audio, revenger).
Read-only; nothing outside the lane output dir was written.

## Result of the scan

**No sibling holds a source-pinned llama-server error-signature registry.** Kama's C1
space (verbatim strings from pinned llama.cpp commit 704366d, reproduced live on the
lane-owned fixture) is uncontested. This scan found adjacent knowledge in four siblings,
all of which kama should cite rather than absorb.

## Hits (path:line) and ownership rulings

### 1. kengaku — served-model surface / serving-stack measurement (adjacent, not owning)
- `kengaku-shokunin/PROVINCE.md:14` — served local model surface `127.0.0.1:34113`,
  `/v1/models`, `/health`, process pin (llama-server pid 1299, 41-token argv, EXACT_MATCH).
- `kengaku-shokunin/PROVINCE.md:24-25` — **"Not owned: the model-serving plane (llama-server
  flags, slot/batch config) — no lane owns it; escalate to the integrator instead of
  remediating."** This is the explicit empty seat kama occupies.
- `kengaku-shokunin/PROVINCE.md:69-72` — KV-quantization flags material to any cross-model
  number drawn from :34113; flag-change authority unowned.
- `kengaku-shokunin/SKILL.md:452-456` — llama.cpp multi-slot non-determinism (issue #7052).
- `kengaku-shokunin/SKILL.md:487-499` — scope limit: sub-3-bit + llama.cpp serving-stack
  observation, process-pinned; not Qwen capability measurement.
- `kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:21-36` — live
  llama-server pid/cmdline/version capture (`version: 0.3.0-dev (build 1, commit d7bd3bf)`;
  build differs from kama's pinned b11755/704366d — separate fixtures).
- `kengaku-shokunin/corpus/evidence/round10-fleet/models-34113.json` — served-model capture.
- `kengaku-shokunin/corpus/knowledge/bench-arena-fresh-run.md:11,25-28` — qwen-coder.service
  gone, 34113 connection refused.
- `kengaku-shokunin/corpus/knowledge/eval-prior-art-calibration.md:22-23,65-67` — llama.cpp
  #7052 prior art; serving flags make an experimental unit defensible.
- `kengaku-shokunin/corpus/evidence/round11-fleet/r11-review-baseline.md:98-107` — re-probe
  of 34113 health/models; EXACT_MATCH md again.

**Ownership ruling:** kengaku owns *measurement/eval* of the served model (quality, task
batteries, scoring, determinism claims) and the *historical identity* of the qwen-coder
hosted service. It explicitly does not own the model-serving plane (flags, config, error
signatures). Kama's C1 live signatures are new ground; kama should cite kengaku's surfaces
for served-model metadata (n_ctx, owned_by=llamacpp) rather than re-establishing them.

### 2. kagi — consumer-side endpoint/auth (kama's credential boundary)
- `kagi-shokunin/SKILL.md:42` — dead-model-endpoint diagnostic: "`stream error Cannot
  connect to API` = dead model endpoint (round-3 drift shape; ≈58 s retry window, exponential
  backoff 2→5→9→19→30 s)"; plugin-load failure.
- `kagi-shokunin/SKILL.md:43` — "Verify model endpoint is real": `curl -fsS
  <endpoint-minus-/v1>/health` → `{"status":"ok"}`; "port 8080 was a Jitsi videobridge on
  2026-09-28 while llama-server served the model on 34113".
- `kagi-shokunin/SKILL.md:57-62` — 401/Basic-vs-Bearer matrix on the control plane
  (POST /session, /global/health, `www-authenticate: Basic`).
- `kagi-shokunin/SKILL.md:459-461` — `OPENCODE_SERVER_PASSWORD` auth gap; 401 foreign-server.
- `kagi-shokunin/corpus/knowledge/handler-on-disk-state.md:148-149` — "Server up, model
  endpoint dead" vs "Control-plane password set" (401) — two distinct error classes.
- `kagi-shokunin/corpus/knowledge/control-plane-hardening.md:20-60` — 401/Basic/Bearer
  semantics; misleading auth-wait error.
- `kagi-shokunin/corpus/knowledge/handler-trust-boundary.md:33-57` — auth acceptance matrix.
- `kagi-shokunin/corpus/knowledge/transcript-hygiene.md:44-59` — credential-language WARN
  tiers (`api_key`, `access_token`, `Bearer`, `password`).
- `kagi-shokunin/corpus/transcript-scan.sh:91-96` — secret-shaped pattern list (API keys).
- `kagi-shokunin/corpus/knowledge/credential-isolation.md:18-22` — model/API credential
  variables unset before serve.
- `kagi-shokunin/corpus/lessons/round-7.md:57-60` — dead-endpoint + plugin signatures.
- `kagi-shokunin/corpus/drift-symbols.tsv:15-16` — host-file pin of the-janitor credential
  handling.

**Ownership ruling:** credentials, API-key material, auth flows (401/Basic/Bearer), and
consumer-side request hygiene are kagi's (matches kama PROVINCE.md:40 and
cross-lane-scope.md:12-13,16,26). Kama must not absorb auth vocabulary as its own error
knowledge. If a C1 http-channel row reproduces a 401/403/auth response from llama-server,
it is a *server-side* literal from the pinned source (kama's fixture), but the diagnostic
meaning and credential handling around it are kagi's; the R26 section should cite kagi for
the auth interpretation. Kagi's `Cannot connect to API` dead-endpoint signature is
consumer-side, not a llama-server source literal — do not register it in C1.

### 3. kumitate — omp dispatch/route semantics (kama's routing boundary)
- `kumitate-shokunin/SKILL.md:437-441` — failure-rule vocabulary: 429→rate_limit,
  401→authentication, 403→permission_denied, 400→invalid_request (dispatch failure
  taxonomy, not model-endpoint text).
- `kumitate-shokunin/SKILL.md:47-48,57-62` — dispatch registry semantics (not server text).
- `kama-shokunin/corpus/knowledge/consumer-registry.md:101-105` — omp builtin
  `llama-cpp-local` default (`LLAMA_CPP_BASE_URL || http://127.0.0.1:8080`) is
  kumitate-owned (omp binary/dispatch tooling); auth-broker rows 13-16 are kumitate/kagi.
- `kama-shokunin/corpus/knowledge/cross-lane-scope.md:28` — route-selection mechanism vs
  resolved endpoint: kumitate owns how a dispatch/alias resolves.

**Ownership ruling:** omp route/fallback/dispatch resolution belongs to kumitate. Kama's
C1 section must not frame omp route behavior or status-code taxonomies as its own serving
knowledge; cite kumitate for any dispatch-adjacent statements.

### 4. tsukuroi — OS/journal/systemd error strings (kama's substrate boundary)
- `tsukuroi-shokunin/SKILL.md:46-50` — package, systemd-unit, journal/boot, driver planes;
  error classes (`database is locked`, `Failed to read "/boot/EFI/systemd": Permission
  denied`, `NVIDIA-SMI has failed…`).
- `tsukuroi-shokunin/corpus/knowledge/systemd-user-plane.md:19-23` — "Failed to change
  process scheduling strategy"; "Failed to load RealtimeKit property ... ServiceUnknown".
- `tsukuroi-shokunin/corpus/knowledge/journal-boot-plane.md:160-164` — "Failed to load
  RealtimeKit property" portal warnings.
- `tsukuroi-shokunin/corpus/knowledge/root-dac-decision-r12.md:121-124` — man-page error
  strings (EACCES, EPERM, EROFS) — POSIX errno, not llama-server.

**Ownership ruling:** OS-substrate error strings (pacman, systemd, journal, driver,
errno) are tsukuroi's. Kama's C1 section should not re-derive host-level error text; only
llama-server's own source literals belong to kama. Note `failed to load` / `address
already in use` appear in tsukuroi/kotoba/mori contexts but never as llama-server literals.

### 5. Other siblings — no llama-server error knowledge
- chousa, souji, kasegi, mado, tabi, tameshi, kaidoku, lore, kotoba, kotodama, kake,
  game-dev-2d/3d, audio, mori, revenger: no SKILL.md/PROVINCE.md/corpus hits naming
  llama-server error strings, model-load failure text, or API-key server handling.
  Scattered "does not support"/"failed to load"/"address already in use" occurrences are
  prose, language-dictionary, OSS-binary-string dumps (e.g. kotoba
  `.ufo/round-44/evidence/omp-live-18.12.2-strings.txt:16938`), or task-eval fixtures
  (e.g. kengaku `round28-calibration` fixtures containing unrelated "Address already in
  use" test strings) — none are llama-server serving knowledge.
- mori holds kill/OOM/coredump classification (PROVINCE.md adjacent-row citations in
  tsukuroi PROVINCE.md:123-127): host process death, not server error text.
- kaidoku/revenger: unpackaged/adjacent-RE scope per tsukuroi PROVINCE.md:51; nothing
  model-serving.

## Contested scope
- None of the four hits is a direct conflict with C1: kengaku explicitly declares the
  model-serving plane unowned; kagi's auth vocabulary is consumer-side; kumitate's
  taxonomy is dispatch-side; tsukuroi's strings are OS-side. The serial "This server does
  not support " family (server-common.cpp) is kama's to register but clause (g) makes
  family members block each other — one counted row per family.

## What kama should cite, not absorb
1. Served-model metadata (n_ctx, owned_by=llamacpp, gguf identity) — cite kengaku
   PROVINCE.md:14 / models-34113.json (historical) and kama's own round-16+ live receipts.
2. Consumer-side dead-endpoint diagnostic (`Cannot connect to API`, backoff) — cite kagi
   SKILL.md:42; do not register as a C1 signature.
3. Auth/credential interpretation of any 401/403 http signature — cite kagi
   control-plane-hardening.md / handler-trust-boundary.md.
4. omp builtin local-endpoint default — cite kumitate via consumer-registry.md:101.
5. Host-level error strings — cite tsukuroi SKILL.md:46-50.

## One-line ownership summary
- kengaku: model eval/served-model measurement; explicit non-owner of the serving plane.
- kagi: credentials, auth flows, API-key handling, consumer endpoint diagnostics.
- kumitate: omp dispatch/route/fallback semantics.
- tsukuroi: OS/package/systemd/journal/driver error strings.
- kama: verbatim llama-server source error signatures reproduced live on its own fixture —
  uncontested new ground.
