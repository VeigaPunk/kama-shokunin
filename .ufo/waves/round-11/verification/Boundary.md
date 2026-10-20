# Boundary — C2 Crosswalk Handoffs, PROVINCE, and QUALITY KQ5 Connection

- **Seat:** `Boundary` (`KamaR11.Boundary`, UFO-FSD connector, leaf member)
- **Role:** Connector — advisory verification report; author advisor, not an outside non-author verifier
- **Lane:** `kama-shokunin`
- **Round:** Round 11 (steered round label/heading date: `2026-10-19`)
- **Verified-at:** `2026-10-20T03:52:00Z` UTC (`date -u`); historical source open dates (`2026-10-19`) and legacy observation dates (`2026-09-28`, `2026-10-14`, `2026-10-15`) remain reported unchanged
- **Assigned Scope:** Connect crosswalk handoffs with `PROVINCE.md`, `corpus/knowledge/cross-lane-scope.md`, and `QUALITY.md` KQ5. Distinguish local model residency from remote routing, credentials, and eval; identify exact bleed if any. Stop after one bounded proposal.
- **Tooling Directive Record:** Zero tools or packages installed or updated. Actual install record: `none`. Native read-only tools (`read`, `grep`, `glob`, `bash date -u`) were used exclusively. No test, build, lint, formatter, or probe commands executed.

---

## 1. Grounded Evidence Base

1. **`PROVINCE.md` Surface Ownership and Refusals (`PROVINCE.md:3-53`):**
   - *Domain:* Local model serving and endpoint health — local LLM endpoints, baseURL drift, served-model reconciliation, probe conventions (`PROVINCE.md:3-4`).
   - *Owns:* Producer discovery and read-only inspection of local serving ports (`tools/kama-probe.sh listeners`, `ss -ltn` loopback enumeration) (`:10`); baseURL pins in surviving/loadable consumers (`:11`); served-model-id reconciliation (`GET /v1/models` vs `--alias` vs configured model id) (`:12`); liveness/readiness probe conventions (`/health`, `/props`, `/slots`) (`:13`); endpoint-drift detection and invocation history (`:14`); endpoint-consumers cross-lane registry (`:15`).
   - *Refuses:* Model quality/eval (`kengaku`), credential material & auth flows (`kagi`), dispatch/route mechanism (`kumitate`), remote web surfaces (`kake`), and bounty targets (`kasegi`) (`PROVINCE.md:40-41`).
   - *Core Boundary Rule:* Kama answers *"is the thing at this baseURL the model this config believes it is, right now"* — never *"is the model good"* or *"is the request safe"* (`PROVINCE.md:41-43`).
   - *Hard Write Boundary:* Kama never writes to `~/.config`, `~/.omp`, or systemd units; it detects and reports stale pins, leaving changes to the operator (`PROVINCE.md:45-49`).
   - *Out of Province Rule:* Anything outside the domain is named in the round report for the owning lane and never absorbed (`PROVINCE.md:51-53`).

2. **`corpus/knowledge/cross-lane-scope.md` Consumer Ownership and Arbitration (`cross-lane-scope.md:1-87`):**
   - *Ownership Principle:* Separates *who owns an endpoint fact* from *who owns the file or behavior that declares/uses it* (`:5`).
   - *Consumer Ownership Matrix:*
     - OpenCode provider `qwen-local` (`8080/v1`): Kama owns service/model identity; Kagi owns credentials/auth hygiene; Operator owns provider config (`:12`).
     - Janitor agent (`8080/v1` "no fallback"): Kama owns actual service/model; Kotoba owns agent instruction surface; Kagi owns auth/secret handling (`:13`).
     - Distiller agent (local primary + cloud fallback cascade): Kama owns health/identity of local primary; Kotoba owns agent file / fallback policy; Kumitate owns route/cascade resolution mechanism (`:14`).
     - Kengaku round-4 battery: Kama owns endpoint identity/availability; Kengaku owns task set, generation, grading, evaluation (`:15`).
     - Janitor CLI wrapper: Kama owns service/model identity; Kagi owns wrapper request/auth/credential flow (`:16`).
     - Systemd unit: Kama owns process/port/model identity; Operator owns unit edits/service changes (`:17`).
     - OMP/fleet model-role map: Kumitate owns route/dispatch resolution if a fleet role resolves to a local endpoint; Kama owns identity/health of the resolved local endpoint if present (`:18`).
   - *Falsifiable Arbitration Rule (`:32`):* Hold consumer text, credentials, route table, and evaluation inputs fixed and vary one cause at a time:
     - if changing only the response at a fixed baseURL/port changes service or served-model identity → `kama`;
     - if changing only credentials/auth changes it → `kagi`;
     - if changing only route mapping changes the resolved URL → `kumitate`;
     - if changing only agent/instruction wording changes it → `kotoba`;
     - if changing only tasks/scoring changes it → `kengaku`.
   - *Adjacency Rule (`:51`):* If the evidence predicate belongs to another domain, record observed endpoint fact, name owning lane, and hand off; MUST NOT absorb source edits, credentials, or duplicate evaluation/route work.
   - *Round-10 Corrections A25–A37 (`:53-79`):* Formally re-anchored the 9 historical handoff lines (lines 38–47) as immutable history under KQ3/KQ7 without mutating original bytes.

3. **`corpus/QUALITY.md` KQ5 and Extended Criteria (`QUALITY.md:13, 28, 38-40`):**
   - *KQ5 Criterion:* "External service/config actions remain an operator handoff; route/secret/eval findings go to the province owner. Reports contain nonsecret shape evidence only."
   - *KQ5 Reject/Limit:* "A training admission requires enabling services, repointing consumers, installing timers, copying config/environment/session/journal bodies, or fabricating receipts/verification." (`QUALITY.md:13`).
   - *KQ6 Criterion:* Vendor/spec claims must cite opened, revision-pinned `SOURCES.md` rows with section anchors; documentation claims are never asserted as present local-runtime facts (`:28`).
   - *KQ13 Criterion (Round 11):* Available inventory, loaded residency, advertised identity, and inference readiness are separate propositions (`:40`).

4. **`corpus/knowledge/served-identity-crosswalk.md` (C2 Admission Artifact):**
   - *Core Claim (`:9`):* Model-list routes do not guarantee residency or readiness: OpenAI reference lists catalog availability; llama.cpp `/v1/models` reports loaded model info but answers while loading; Ollama `/v1/models` documents metadata without a loaded guarantee; Ollama `/api/ps` reports loaded models bounded by `expires_at`; `/api/tags` reports available inventory that may include remote entries (`remote_model`/`remote_host`, S031). A `MODEL_OK` match proves only that the expected id was listed at sample time — not that weights are loaded, local, or ready to execute.
   - *Province Handoff (`:50-52`):* Local endpoint identity/liveness stays `kama` (`endpoint-identity.md`; `tools/kama-probe.sh check`); route/gateway selection → `kumitate` (`cross-lane-scope.md` adjacency rule); model quality/eval → `kengaku`; credentials/auth → `kagi`; remote web properties → `kake`; host config/service changes → `operator` (`PROVINCE.md` write boundary).
   - *QUALITY Clearance (`:66`):* "KQ5: no service started, no request sent, no credentials read; external remediation stays operator-owned."

5. **Peer Verification and Advice Findings (`.ufo/waves/round-11/advice/`):**
   - `SiblingOverlap.md`: Mapped C2 boundaries; identified the need to retain all 9 historical handoff lines in `cross-lane-scope.md:38-47` under KQ3/KQ7; proposed delegating crosswalk handoffs to `cross-lane-scope.md:32`.
   - `Simplify.md`: Identified redundancy in C2; recommended keeping C2 lean (drop redundant `/health` and `/metrics` columns; delegate handoffs to `cross-lane-scope.md`).
   - `AttackCoverage.md`: Proved that C2 is duplicative if it merely restates `/api/tags` vs `/api/ps`, but achieves genuine expansion through U1 (Ollama `/v1/models` is available, not running), U2 (llama.cpp `/v1/models` answers mid-load), U3 (llama.cpp router mode separates `/models` status from `/v1/models`), U4 (Ollama available entries can be remote upstreams), U5 (alias identity limits), and U6 (Ollama `/api/ps` is time-bounded by `expires_at`).
   - `ReviewIdentity.md`: Re-verified sources; confirmed S031 remote entry schema (`remote_model`, `remote_host`); noted that S010 cloud model access requires a "signed-in local server".

---

## 2. Explicit Contradictions Stated

1. **Axis Authority Contradiction (`shokunin.conf:52` vs `MISSION.md:29`):**
   `shokunin.conf:52` assigns `operability + calibration (local model serving and endpoint health)` to kama. In contrast, `MISSION.md:29` and the round-11 task prompt declare `operability + freshness`. Under `AXES.md` ("lowest-scoring non-retired axis"), calibration (7) is lower than freshness (8). The round-11 spec aligns C1 with CALIBRATION while treating freshness as tied at 8. This contradiction is recorded directly without smoothing into a composite score.

2. **Index Scope Overclaim (`corpus/README.md:32` vs `served-model-identity.md`):**
   `corpus/README.md:32` indexes `served-model-identity.md` as "served-model reconciliation (/v1/models vs --alias vs configured id) + the minimal proof procedure". In reality, `served-model-identity.md` is a 37-line historical fragment containing raw probe outputs (`/health`, `/props`, `/slots`, `/metrics`) from one llama.cpp instance, with zero Ollama content and zero alias-reconciliation procedures. The crosswalk correctly notes this discrepancy, and the parent must append an index correction under KQ7.

3. **Historical Citation Error in Health Matrix (`runtime-health-surface-matrix.md:17`):**
   Line 17 of `runtime-health-surface-matrix.md` cited `S009, S010` for Ollama `/api/tags` and `/api/ps`. However, S009 and S010 do not document `/api/ps` (which is documented in S012), nor do they document native `/api/tags` (documented in S011/S031). This is a provenance defect requiring an appended correction to S011/S012, not new C2 coverage.

4. **"Locally Available" vs Remote Upstream Schema (S011 vs S031):**
   `SOURCES.md` S011 scope and OpenAPI description state "Summary information for a locally available model". However, S031 proves the OpenAPI schema contains `remote_model` ("Name of the upstream model, if the model is remote") and `remote_host` ("URL of the upstream Ollama host, if the model is remote"). Thus, an entry in `/api/tags` does not prove local disk residency or local weights.

5. **Cloud Model Selection vs Local Server Independence (S010):**
   S010 documents that a local server can list and select cloud models (e.g. `gemma4:cloud`), but this requires the precondition: "Through a signed-in local server". This couples local endpoint listing with external user account authentication.

---

## 3. Boundary Analysis: Distinguishing Local Model Residency from Adjacent Surfaces

To ensure strict compliance with `PROVINCE.md:40-43` and `QUALITY.md` KQ5, local model residency must be formally decoupled from adjacent domains:

```
+---------------------------------------------------------------------------------------------------------+
| LOCAL MODEL RESIDENCY (kama domain — PROVINCE.md:10-15)                                                 |
| - Definition: Model weights actively resident in local host RAM/VRAM on loopback socket.                |
| - Grounded Signals: Ollama /api/ps (size_vram > 0, unexpired expires_at); llama.cpp router             |
|   status.value == "loaded"; llama.cpp single-model /v1/models when meta != null.                        |
| - Boundary Rule: Verifies whether the process on a local port has resident weights for an expected ID.  |
+---------------------------------------------------------------------------------------------------------+
       |                                      |                                      |
       v                                      v                                      v
+----------------------+     +--------------------------------+     +----------------------------------+
| REMOTE ROUTING       |     | CREDENTIALS & AUTH HYGIENE     |     | MODEL EVALUATION                 |
| (kumitate / kake)    |     | (kagi / operator)              |     | (kengaku)                        |
| - remote_model / host|     | - Bearer tokens (S016 / S001)  |     | - Token generation quality       |
| - Cloud models (S010)|     | - "signed-in server" (S010)    |     | - Perplexity / benchmark scoring |
| - Fallback cascades  |     | - 401/403 status codes         |     | - Context window degradation     |
| - Upstream dispatch  |     | - Secret storage / vaults      |     | - Quantization loss              |
+----------------------+     +--------------------------------+     +----------------------------------+
```

### A. Local Model Residency vs. Remote Routing (`kumitate` / `kake`)
- **What kama owns:** Inspecting the local listening port and documenting engine route syntax (`/api/tags`, `/api/ps`, `/v1/models`). Kama detects whether an entry advertises `remote_model`/`remote_host` (S031) or an external cloud target (`gemma4:cloud`, S010).
- **What kumitate/kake own:** Kumitate owns dispatch mechanisms, upstream routing cascades, dynamic agent-to-model role mapping, and client fallbacks (e.g. `distiller.md` primary-to-cloud fallback). Kake owns remote web endpoints.
- **The Residency-Routing Distinction:** An advertised model ID in `/v1/models` or `/api/tags` is catalog availability, not local execution. If the local daemon acts as a proxy/gateway to a remote upstream host, the model is **not locally resident**. Kama reports the presence of remote metadata and immediately hands off route resolution to `kumitate`.

### B. Local Model Residency vs. Credentials and Auth Hygiene (`kagi` / `operator`)
- **What kama owns:** Documenting that endpoints may enforce authentication interfaces (e.g. HTTP 401 Unauthorized, HTTP 403 Forbidden) and classifying them as `UNAUTHORIZED_SERVICE` in probe logic (`endpoint-identity.md`).
- **What kagi/operator own:** Kagi owns API key lifecycle, secret vault management, Bearer token injection, and request authorization hygiene. Operator owns host configuration files (`~/.config`, `~/.omp`).
- **The Residency-Credential Distinction (KQ5 Compliance):** Documenting that cloud model access requires a "signed-in local server" (S010) or Bearer authorization (S016) is a documentation prerequisite, never an authorization procedure. Under KQ5, Kama MUST NOT inspect credential files (e.g. `~/.ollama/id_ed25519`, `opencode.json`), capture auth headers, or validate user login status. Reports contain nonsecret shape evidence only.

### C. Local Model Residency vs. Model Evaluation (`kengaku`)
- **What kama owns:** Verifying that a local port answers with the expected model identifier, alias, or resident memory allocation (`PROVINCE.md:12`).
- **What kengaku owns:** Evaluating model output accuracy, benchmark scoring, perplexity, context saturation, and prompt calibration (`cross-lane-scope.md:27`).
- **The Residency-Evaluation Distinction:** Verifying that a model has resident weights in VRAM (`size_vram > 0`) or answers `/v1/models` does **not** certify that the model is functioning correctly, producing coherent tokens, or uncorrupted by quantization. Served-model residency is an infrastructure state, not an evaluation verdict.

---

## 4. Exact Bleed Analysis

A rigorous, line-by-line audit of `corpus/knowledge/served-identity-crosswalk.md`, `cross-lane-scope.md`, and round-11 proposals evaluates whether any cross-domain bleed exists:

1. **Remote Routing Bleed: NONE (Cleanly Decoupled)**
   - *Evidence:* In `served-identity-crosswalk.md:51`, the crosswalk explicitly specifies:
     `Route/gateway selection (which upstream or model answers a request) → kumitate (cross-lane-scope.md adjacency rule)`.
   - In line 31 (Failure Case 6), the crosswalk flags that `remote_model`/`remote_host` and cloud models represent available inventory, not local weights, and disclaims any attempt to probe the upstream host or manage dispatch.
   - In line 36, the crosswalk notes `--tags` is "informational, not used for routing".
   - *Verdict:* No bleed into `kumitate` or `kake`.

2. **Credential and Secret Bleed: NONE (Strict KQ5 Compliance)**
   - *Evidence:* In `served-identity-crosswalk.md:51`, the crosswalk declares:
     `credentials/auth → kagi; host config/service changes → operator (PROVINCE.md write boundary)`.
   - In line 66, the QUALITY clearance affirms:
     `KQ5: no service started, no request sent, no credentials read; external remediation stays operator-owned`.
   - The S016 and S010 references cite public documentation schemas and mention authentication requirements purely as interface boundaries. No credential keys, session tokens, or private hashes appear in the file.
   - Legacy supplement reviews in round 11 strictly followed nonsecret shape reads (`wc -l`, `test -e`, `sha256sum`) as recorded in `cross-lane-scope.md:55-79`, preventing any repetition of historical Mistake 9.
   - *Verdict:* Zero credential bleed; 100% KQ5 compliant.

3. **Evaluation Bleed: NONE (Explicit Non-Equivalence)**
   - *Evidence:* In `served-identity-crosswalk.md:43-45`, the crosswalk states:
     `No universal readiness predicate... A MODEL_OK verdict is an inventory statement at sample time. It never establishes loaded weights... or execution readiness`.
   - In line 51: `model quality/eval → kengaku`.
   - The crosswalk never evaluates generation quality, token latency, or prompt completions.
   - *Verdict:* Zero evaluation bleed into `kengaku`.

4. **Identified Boundary Defect in Crosswalk (Minor — Lack of Explicit Cross-Lane Scope Link):**
   - *Defect:* At `served-identity-crosswalk.md:50-52` ("Province handoff"), the text cites `cross-lane-scope.md adjacency rule` generally, but fails to cite the specific operational mechanism: `cross-lane-scope.md:32` (the *Falsifiable Arbitration Rule*).
   - *Impact:* A future consumer reading `served-identity-crosswalk.md` might treat the handoffs as informal prose rather than binding arbitration logic.
   - *Severity:* Low.
   - *Smallest Repair:* In the parent integration of `served-identity-crosswalk.md` or the Round 11 Fleet Report, explicitly anchor the handoffs to `cross-lane-scope.md:32`.

---

## 5. Non-Obvious Move: The Tripartite Residency-Routing-Credential (RRC) Decoupling Protocol

### A. Synthesis Across Round Proposals
The round's peer reports contain complementary insights that, when synthesized, yield a powerful architectural move:
1. `Simplify.md` established that `served-identity-crosswalk.md` must not bloat itself with redundant restatements of cross-lane handoffs, health matrix details, or metrics tables.
2. `AttackCoverage.md` proved that C2's expansion is valid only by formalizing the negative limits of the four concepts (U1: Ollama `/v1/models` is available, not running; U2: llama.cpp `/v1/models` answers mid-load; U4: Ollama tags can be remote upstreams; U6: Ollama `/api/ps` is time-bounded by `expires_at`).
3. `SiblingOverlap.md` proved that all 9 historical handoff lines in `cross-lane-scope.md:38-47` must remain bit-for-bit immutable under KQ3/KQ7, and that new round-11 handoffs belong in the Fleet Report.
4. `ReviewIdentity.md` showed that S010 cloud models require a "signed-in local server" (S010), coupling inventory with credentials.

### B. The Move: Tripartite RRC Decoupling Protocol
Formally bind the C2 served-identity crosswalk to `cross-lane-scope.md:32` by integrating a tripartite decoupling protocol into the Round 11 Fleet Report handoffs and `served-identity-crosswalk.md:48-53`:

1. **Residency Isolation (kama vs. kengaku):**
   - `MODEL_OK` is explicitly defined as an *Inventory Availability* predicate, never an *Execution Readiness* or *Inference Quality* predicate.
   - Documented residency signals (`size_vram > 0`, `expires_at` in Ollama S012; `status.value == "loaded"` in llama.cpp S001) confirm memory allocation on the host, but provide zero warranty of model output accuracy. Model evaluation remains exclusively with `kengaku`.

2. **Remote Routing Quarantine (kama vs. kumitate/kake):**
   - When an endpoint inventory lists a model with `remote_model`/`remote_host` (S031) or a cloud-routed tag (S010 `gemma4:cloud`), Kama's responsibility ends with reporting the presence of the remote metadata at that local socket.
   - Upstream proxying, fallback cascades, gateway routing, and dynamic role resolution are formally quarantined to `kumitate`, while remote web reachability belongs to `kake`. Kama never executes an egress probe to an upstream host.

3. **Credential Precondition Demarcation (kama vs. kagi/operator):**
   - Requirements such as "signed-in local server" (S010) or Bearer auth (S016, S001) are documented strictly as *Prerequisite Interface Constraints*.
   - Under KQ5 and `PROVINCE.md:45-49`, Kama treats authentication failures (HTTP 401/403) as nonsecret status shape evidence (`UNAUTHORIZED_SERVICE`), delegating credential configuration to `kagi` and `operator`. Kama never reads auth tokens, private keys, or session files.

### C. Affected Axes
- **Calibration (Primary Axis):** **Improved.** Eliminates false positive assumptions about model execution. Distinguishes local resident weights from remote upstreams, catalog listings, and mid-load states.
- **Coverage (C2 Axis):** **Improved.** Solidifies the non-duplicative expansion of C2 (U1–U6) across three serving engines without straying outside the local serving domain.
- **Operability:** **Unharmed.** Modifies zero executable probe code; starts no services; preserves `tools/kama-probe.sh check` exactly as written.
- **Freshness & Adjacency:** **Unharmed and Protected.** C1's legacy supplements remain strictly decoupled; no cross-domain bleed into routing, secrets, or evaluation occurs.

### D. Risks and Mitigations
1. **Risk:** An automated consumer reads `served-identity-crosswalk.md` and assumes that if a model is listed in `/api/tags` or `/v1/models`, it can be immediately dispatched for local inference without network access.
   - *Mitigation:* The crosswalk's "What cannot be concluded" section explicitly states that catalog availability does not prove local weights or execution readiness, citing S031 and S010.
2. **Risk:** Future authors might attempt to make `tools/kama-probe.sh` query `/api/tags` remote upstreams to verify endpoint reachability.
   - *Mitigation:* The handoff explicitly forbids egress probes, reserving remote network targets to `kake` and routing to `kumitate`.

### E. Verification Procedure
1. **Verification of Zero Bleed in Crosswalk:**
   Confirm that in `kama-shokunin/corpus/knowledge/served-identity-crosswalk.md`, all mentions of credentials, routing, and evaluation occur strictly under "What cannot be concluded", "Failure cases", "Province handoff", or "QUALITY clearance".
2. **Verification of KQ5 Compliance:**
   Confirm that no credential tokens, API key strings, private paths, or session data exist in `served-identity-crosswalk.md` or any round-11 advisory report.
3. **Verification of Immutability in `cross-lane-scope.md`:**
   Verify that lines 38–47 in `kama-shokunin/corpus/knowledge/cross-lane-scope.md` are bit-for-bit identical to the baseline SHA-256 prefix.

---

## 6. What Is Already Correct

1. **`served-identity-crosswalk.md` Content Discipline:**
   The admitted draft (`corpus/knowledge/served-identity-crosswalk.md`) maintains exceptional domain discipline. It explicitly disclaims residency, local weights, and execution readiness from `/v1/models` listings, credits prior coverage in `runtime-health-surface-matrix.md:17`, and cites opened A-tier sources (S001, S010, S011, S012, S016, S031).
2. **KQ5 Enforcement:**
   Zero secret material, credentials, or session tokens are present in the crosswalk or round-11 files. Shape-only inspection conventions were strictly respected.
3. **Province Boundaries:**
   `PROVINCE.md:40-43` and `cross-lane-scope.md:32, 51` remain fully respected across all round-11 proposals. No sibling domain authority was absorbed.
4. **Tooling Discipline:**
   Zero tools or dependencies were installed; native read-only tools were used exclusively.

---

## 7. Execution and Handoff Summary for Parent Integrator

1. **Retain Existing Historical Lines in `cross-lane-scope.md:38-47` Verbatim:**
   Do not modify, delete, or rewrite the 9 historical handoff lines in `cross-lane-scope.md:38-47`. They are immutable history protected by KQ3 and KQ7.
2. **Integrate RRC Handoff Lines in the Round 11 Fleet Report:**
   In `.ufo/reports/round-11/kama.md`, emit the grounded handoff lines separating local residency from `kengaku` (eval), `kumitate` (routing), `kagi` (credentials), and `operator` (config/service authority), citing `served-identity-crosswalk.md` and `cross-lane-scope.md:32`.
3. **Append Index Corrections to `corpus/README.md`:**
   Append the supersession of line 32 (`served-model-identity.md`) and line 9 at EOF in `corpus/README.md`, ensuring zero line anchors shift.
4. **Final Status:**
   Zero implementation or corpus edits performed by this seat. All findings are purely advisory.
