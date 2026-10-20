# SiblingOverlap — C2 Boundaries, Cross-Lane Scope, and Handoff Mapping

- **Seat:** `SiblingOverlap` (connector, leaf member — parent-dispatched author advisor; not an outside non-author verifier)
- **Lane:** `kama-shokunin`
- **Round:** Round 11 (steered round label/heading date: `2026-10-19`)
- **Verified-at:** `2026-10-20T02:14:19Z` (actual UTC review timestamp from `date -u`); historical source open dates (`2026-10-19`) and legacy observation dates (`2026-09-28`, `2026-10-14`, `2026-10-15`) are reported unchanged.
- **Recheck:** On-round integration; re-verify against `corpus/knowledge/cross-lane-scope.md` and `PROVINCE.md`.
- **Target:** Read-only map C2 boundaries using `PROVINCE.md`, `corpus/knowledge/cross-lane-scope.md`, and read-only fleet mission (`../MISSION.md`). Separate local identity from evaluation, routing, and credentials. Identify exact handoff lines parent should retain. Stop after one bounded proposal.
- **Tooling Directive Record:** Zero tools or packages installed or updated. Native read-only inspection tools (`read`, `grep`, `glob`, `bash date -u`) were used exclusively.

---

## 1. Grounded Evidence Base

1. **`PROVINCE.md` Surface Ownership and Refusals (`PROVINCE.md:3-49`):**
   - *Domain:* Local model serving and endpoint health (`PROVINCE.md:3-4`).
   - *Owns:* Producer discovery, read-only inspection of serving ports (`PROVINCE.md:10`), baseURL pins in consumers (`:11`), served-model-id reconciliation (`:12`), liveness/readiness probe conventions (`:13`), endpoint-drift detection (`:14`), and consumer registry (`:15`).
   - *Refuses:* Model quality/eval (`kengaku`), credential material & auth flows (`kagi`), dispatch/route mechanisms (`kumitate`), remote web surfaces (`kake`), and bounty targets (`kasegi`) (`PROVINCE.md:40-41`).
   - *Core Boundary Rule:* Kama answers *"is the thing at this baseURL the model this config believes it is, right now"* — never *"is the model good"* or *"is the request safe"* (`PROVINCE.md:41-43`).
   - *Hard Write Boundary:* Kama never writes to `~/.config`, `~/.omp`, or systemd units; it detects and reports stale pins, leaving changes to the operator (`PROVINCE.md:45-49`).

2. **`corpus/knowledge/cross-lane-scope.md` Consumer Ownership & Arbitration (`cross-lane-scope.md:1-52`):**
   - *Ownership Principle:* Separates *who owns an endpoint fact* from *who owns the file or behavior that declares/uses it* (`:5`).
   - *Falsifiable Arbitration Rule:* Hold consumer text, credentials, route table, and evaluation inputs fixed and vary one cause at a time: if changing only the response at a fixed baseURL/port changes service/model identity → `kama`; if changing only credentials/auth → `kagi`; if changing only route mapping → `kumitate`; if changing only agent instructions → `kotoba`; if changing only task/scoring → `kengaku` (`:32`).
   - *Adjacency Rule:* If the evidence predicate belongs to another domain, record observed endpoint fact, name owning lane, and hand off; MUST NOT absorb source edits, credentials, or duplicate evaluation/route work (`:49-51`).
   - *Round-10 Corrections A25–A37 (`:53-79`):* Formally re-anchored the 9 historical handoff lines (which cited now-deleted host files: `the-janitor`, `janitor.md`, `distiller.md`, `qwen-coder.service`) as immutable history under KQ3/KQ7 without mutating original bytes.

3. **Fleet Mission & Axes (`../MISSION.md:20-31`, `../AXES.md:9-17`):**
   - `kama`: `operability + freshness (local model serving/endpoints)` (`../MISSION.md:29`).
   - `kengaku`: `novelty + calibration (LLM eval/research)` (`:24`).
   - `kumitate`: `operability + coverage (orchestration/tooling)` (`:26`).
   - `kagi`: `freshness + calibration (secrets/vault ops)` (`:28`).
   - `kotoba`: `depth + consistency (prompt/skill craft)` (`:27`).
   - `AXES.md` Adjacency: "Cross-domain awareness — evidence belonging to another domain reported, not absorbed. Lane reports name contested scope; integrator arbitrates." (`../AXES.md:16`).

4. **Sibling Proposal Round Cache (`.ufo/waves/round-11/advice/`):**
   - `ReviewContract.md` (S3) & `AttackCoverage.md`: Warn that Ollama `/api/tags` and `/api/ps` are already mentioned in `runtime-health-surface-matrix.md:17` under flawed S009/S010 citations. C2 is genuine expansion only if it establishes the four distinct concepts (availability, loaded models, alias identity, readiness) and their negative limits (what cannot be concluded).
   - `Simplify.md`: Recommends dropping duplicated handoffs, health routes, and metrics columns from the C2 crosswalk entry, delegating cross-lane boundaries to `cross-lane-scope.md` via tight pointer.
   - `ReviewIdentity.md` & `SourceRunning.md`: Highlight that `/api/ps` shows loaded/running models with an expiry, `/api/tags` shows available disk inventory, and `/v1/models` in Ollama is available inventory (not running weights).

---

## 2. C2 Boundary Mapping: Separating Local Identity from Adjacent Domains

The C2 crosswalk (`corpus/knowledge/served-identity-crosswalk.md`) establishes four core operational concepts across local serving engines (Ollama, llama.cpp, and OpenAI reference):
1. **Available Inventory:** Models present in storage or configured in catalog (`/api/tags`, `GET /models` router cache, `/v1/models` catalog).
2. **Loaded / Resident Models:** Models currently loaded into memory/VRAM (`/api/ps`, `llama-server` single-model `/v1/models` when meta is populated, or router `status == "loaded"`).
3. **Alias Identity:** Mappings between external names and internal model artifacts (`ollama cp`, `llama-server --alias`).
4. **Health / Readiness:** Daemon HTTP reachability vs. inference execution readiness (`/health`, `/slots`, `/props`).

To preserve Kama's province and avoid cross-domain bleed under `PROVINCE.md:40-43`, these four concepts must be cleanly separated from adjacent lane domains:

### A. Local Identity vs. Evaluation (`kengaku`)
- **Kama owns:** Reporting what model identifier, alias, or digest is served or resident in memory at a local endpoint (`PROVINCE.md:12`).
- **Kengaku owns:** Evaluating model generation quality, output accuracy, benchmark scoring, perplexity, context saturation behavior, and prompt calibration (`../MISSION.md:24`; `cross-lane-scope.md:27`).
- **Boundary Line:** Observing that an endpoint responds with a matching model ID or that `/api/ps` lists a model with resident VRAM does **not** certify that the model is capable, properly quantized, or producing non-degraded tokens. C2 must state that served-model presence is not evaluation fidelity.

### B. Local Identity vs. Routing & Orchestration (`kumitate`)
- **Kama owns:** Endpoint route syntax, engine-level response schemas, and verifying whether a specific baseURL/port serves a declared model (`PROVINCE.md:10, 12`).
- **Kumitate owns:** Dispatch mechanisms, dynamic model-role resolution (e.g. OMP `modelRoles`), client fallback cascades (e.g. falling back from local primary to cloud provider), and load-balancing across workers (`../MISSION.md:26`; `cross-lane-scope.md:28`).
- **Boundary Line:** The fact that an engine supports multiple models (`/api/tags`) or provides an OpenAI-compatible route does **not** authorize Kama to manage client dispatch tables or author fallback logic. Kama checks the resolved destination; Kumitate resolves the route.

### C. Local Identity vs. Credentials & Auth Hygiene (`kagi`)
- **Kama owns:** Documenting endpoint authorization interfaces (e.g. OpenAI requiring Bearer tokens, `llama-server` `--api-key`) and classifying HTTP status codes (e.g. `401 Unauthorized` as `UNAUTHORIZED_SERVICE`) (`PROVINCE.md:10`; `endpoint-identity.md`).
- **Kagi owns:** API key generation, secret vault storage, Bearer token injection, request authorization hygiene, and preventing secret leakage (`../MISSION.md:28`; `cross-lane-scope.md:26`).
- **Boundary Line:** Kama verifies whether an endpoint requires or accepts authentication; Kama never inspects host secrets, captures credential headers, or validates API key strings.

### D. Local Identity vs. Prompt / Agent Surfaces (`kotoba`)
- **Kama owns:** Verifying whether the runtime behind a configured baseURL serves the exact model name or alias expected by a client (`PROVINCE.md:11-12`).
- **Kotoba owns:** Agent system prompts, prompt template engineering, and declared model selection in agent definitions (`../MISSION.md:27`; `cross-lane-scope.md:29`).
- **Boundary Line:** A prompt declaration claiming "there is no fallback" or requesting a specific model is an agent instruction surface for Kotoba; Kama provides only the ground-truth probe of what is actually listening.

### E. Local Identity vs. Service Lifecycle & System Configuration (`operator / L0`)
- **Kama owns:** Non-destructive probe measurement and drift detection of local listening ports (`PROVINCE.md:10, 45-49`).
- **Operator (L0) owns:** Starting/stopping daemons (`systemctl`), editing systemd service files, modifying `~/.config` or `~/.omp`, repointing consumer base URLs, and allocating system VRAM.
- **Boundary Line:** Kama reports `DEAD` or mismatched endpoints; Kama never issues systemctl commands or edits host configurations.

---

## 3. Exact Handoff Lines Parent Should Retain

### A. Existing Historical Lines in `corpus/knowledge/cross-lane-scope.md:38-47`
The parent **MUST retain all 9 existing historical handoff lines** in `cross-lane-scope.md:38-47` verbatim in the corpus file:
1. `kagi` (`:38`): Janitor wrapper/`qwen-local` 8080 target vs Jitsi HTML 404.
2. `kengaku` (`:39`): 34113 vs 8080 local serving vs round-4 eval finding.
3. `kumitate` (`:40`): OMP role map local reference check.
4. `kotoba` (`:41`): `janitor.md` and `distiller.md` agent surfaces.
5. `kake` (`:42`): Loopback model serving vs remote web property.
6. `kasegi` (`:43`): Local consumer pins vs bounty targets.
7. `protocol` (`:44`): Local-serving mismatch vs fleet protocol integrity.
8. `aggregator` (`:45`): Cross-lane drift arbitration.
9. `Operator/L0 decision line` (`:47`): Repointing recommendation.

*Rationale for retention:* Under `corpus/QUALITY.md` KQ3 ("Corrections preserve old corpus bytes") and KQ7 ("every correction appended at the end of its file"), existing knowledge bytes are immutable history. Round 10 already published corrections A25–A37 (`:53-79`) re-anchoring these lines to current host facts. Mutating or deleting lines 38–47 would cause anchor drift and break prefix integrity.

### B. Round 11 Fleet Report Handoff Lines (for Parent Integration)
In the Round 11 Fleet Report (`.ufo/reports/round-11/kama.md` or advice integration), the parent should emit these exact, grounded handoff lines:

- **kengaku:** `Kama reports: C2 served-identity crosswalk establishes local engine catalog and residency interfaces (Ollama /api/tags vs /api/ps, llama.cpp /v1/models vs router /models); presence of an advertised model ID or resident VRAM proves serving identity only, not evaluation validity, benchmark performance, or output accuracy, which remain kengaku's domain. (corpus/knowledge/served-identity-crosswalk.md; PROVINCE.md:40-43; cross-lane-scope.md:27.)`
- **kumitate:** `Kama reports: C2 documents engine-specific route syntax and local model aliasing (ollama cp, llama-server --alias); kumitate retains dispatch orchestration, agent-to-model role mapping, and fallback/cascade routing mechanisms. Kama verifies what is served at the resolved destination; kumitate resolves the route. (corpus/knowledge/served-identity-crosswalk.md; PROVINCE.md:40-43; cross-lane-scope.md:28.)`
- **kagi:** `Kama reports: C2 documents OpenAPI model-list reference schemas and engine authentication interfaces (401/403 status codes); kagi retains secret storage, API token lifecycle, and request authorization hygiene. No credential material was inspected or stored. (corpus/knowledge/served-identity-crosswalk.md; PROVINCE.md:40-43; cross-lane-scope.md:26.)`
- **kotoba:** `Kama reports: C2 provides ground-truth model identity and alias reconciliation for local serving endpoints; kotoba retains agent instruction surfaces, prompt templates, and configured model preferences. (corpus/knowledge/served-identity-crosswalk.md; PROVINCE.md:40-43; cross-lane-scope.md:29.)`
- **Operator/L0:** `Kama reports: C2 served-identity crosswalk is a read-only documentation artifact grounded in opened vendor sources (S001, S010, S011, S012, S016); no host services were started, no systemd units modified, and no consumer configuration rewritten. Operator retains service lifecycle and host configuration authority. (PROVINCE.md:45-49; cross-lane-scope.md:30, 47.)`

---

## 4. UFO-FSD Connector Synthesis: The Proposed Non-Obvious Move

### The Move: Delegate C2 Handoffs to `cross-lane-scope.md` via the Falsifiable Arbitration Rule
Rather than bloating the new C2 crosswalk (`corpus/knowledge/served-identity-crosswalk.md`) with redundant restatements of cross-lane handoffs (as warned by `Simplify.md`), or risking cross-domain bleed into evaluation, routing, and credentials:

1. **Synthesis across round proposals:**
   - Synthesize `Simplify.md` (keep C2 crosswalk focused on engine interface tables; drop prose handoffs), `AttackCoverage.md` (focus C2 on the negative limits and distinct semantics of the 4 concepts), and `ReviewContract.md` (prevent C1/C2 from contaminating adjacent counters or violating domain bounds).
   - Anchor C2's province section to a single pointer: delegate cross-lane arbitration directly to `corpus/knowledge/cross-lane-scope.md:32` (the established *Falsifiable Arbitration Rule*).

2. **The Explicit Engine-Boundary Contract inside C2:**
   Inside `served-identity-crosswalk.md`, include an explicit, compact 4-concept boundary table that maps the four C2 concepts against the falsifiable arbitration rule:
   - **Availability (`/api/tags`, `/models`):** If changing only available catalog changes output → `kama` inventory; if changing orchestrator candidate pool changes it → `kumitate`.
   - **Loaded / Resident (`/api/ps`, `/slots`):** If changing only VRAM/memory residency changes output → `kama` liveness; if changing model inference quality/scoring changes it → `kengaku` evaluation.
   - **Alias Identity (`ollama cp`, `--alias`):** If changing only local alias mapping changes served ID → `kama` reconciliation; if changing agent prompt model request changes it → `kotoba`.
   - **Readiness (`/health`, `/props`):** If changing daemon HTTP listener state changes probe → `kama` probe; if starting/stopping systemd units changes it → `operator`.

### Affected Axes
- **Coverage (Primary C2):** Improves coverage by cleanly formalizing the 4 distinct operational concepts across 3 engines without duplicating existing matrix coverage.
- **Adjacency (Protected):** Strictly prevents Kama from absorbing evaluation claims (`kengaku`), routing cascades (`kumitate`), or auth handling (`kagi`).
- **Calibration (Improved):** Grounded negative bounds explicitly prevent false inferences (e.g. available != loaded; resident != ready; advertised != evaluated).
- **Freshness & Operability:** Harms neither axis; introduces no executable probes, no unverified runtime assertions, and leaves C1's legacy provenance completely decoupled.

### Risks & Mitigations
- *Risk 1 (Second-order verification drift):* An external consumer might read C2's engine table and assume local engines are currently running on the host.
  *Mitigation:* C2 entry's `verified-at:` must state: "Vendor documentation opened; no local runtime contacted; historical host state remains unchanged."
- *Risk 2 (Contaminating the round-10 coverage counter):* If legacy files in C1 mistakenly cite `source: S...`, they move the coverage counter (`ReviewContract.md` S1).
  *Mitigation:* C1 legacy files cite `source: none — historical record` or local path citations; only C2 cites `mined` S-rows.

### Verification
1. **Mechanical Handoff Check:** Verify that `cross-lane-scope.md:38-47` lines are unchanged in byte offset and text.
2. **Province Check:** Run `grep -iE "evaluat|benchmark|credential|cascade|route-selection" corpus/knowledge/served-identity-crosswalk.md` and confirm that all occurrences appear solely under boundary restrictions or pointers to `cross-lane-scope.md`.
3. **No Sibling Edits:** Verify that `SiblingOverlap` edited zero files outside `.ufo/waves/round-11/advice/SiblingOverlap.md`.
