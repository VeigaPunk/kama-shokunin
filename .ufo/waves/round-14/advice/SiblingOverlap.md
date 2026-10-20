# SiblingOverlap — Round 14 PROVINCE Mapping, Cross-Lane Scope, and Handoff Synthesis

- **Seat:** `SiblingOverlap` (`KamaR14.SiblingOverlap`, role: UFO-FSD connector, leaf member — parent-dispatched author advisor; not an outside non-author verifier)
- **Lane Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`
- **Round:** Round 14 (steered label / date: `2026-10-20` UTC)
- **Verified-at:** `2026-10-20T06:33:00Z` (actual review timestamp from `date -u`); historical observation dates preserved.
- **Report Path:** `.ufo/waves/round-14/advice/SiblingOverlap.md` (written relative to lane root)
- **Tooling Directive Record:** Zero tools or packages installed or updated. Native inspection tools used exclusively.
- **Status of Implementation:** Implementation files (`tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`, `corpus/knowledge/ollama-evidence-replay.md`, `.ufo/waves/round-14/measure.py`) were pending on disk at review time; under the round-14 contract, in-flight files are pending, not defects. Findings below rest on repository evidence, the `spec.json` contract, opened vendor documentation, and the round-14 advisory cache.

---

## 1. Grounded Evidence Base

1. **`PROVINCE.md` Surface Ownership and Refusals (`PROVINCE.md:3-52`):**
   - *Domain:* Local model serving & endpoint health — local LLM endpoints, baseURL drift, served-model reconciliation, probe conventions (`PROVINCE.md:3-4`).
   - *Owns:* Producer discovery, read-only inspection of serving ports (`:10`), baseURL pins in consumers (`:11`), served-model-id reconciliation (`:12`), liveness/readiness probe conventions (`:13`), endpoint-drift detection (`:14`), consumer registry (`:15`).
   - *Refuses:* Model quality/eval (`kengaku`), credential material & auth flows (`kagi`), dispatch/route mechanisms (`kumitate`), remote web surfaces (`kake`), bounty targets (`kasegi`) (`:40-41`).
   - *Core Boundary Rule:* Kama answers *"is the thing at this baseURL the model this config believes it is, right now"* — never *"is the model good"* or *"is the request safe"* (`:41-43`).
   - *Hard Write Boundary:* Kama never writes to `~/.config`, `~/.omp`, or systemd units; it detects and reports stale pins, leaving changes to the operator (`:45-49`).
   - *Out of Province Rule:* Anything found outside the domain is named in the round report for the owning lane; report, never absorb (`:51-52`).

2. **`corpus/knowledge/cross-lane-scope.md` Arbitration Rule (`cross-lane-scope.md:1-52`):**
   - *Ownership Principle:* Separates *who owns an endpoint fact* from *who owns the file or behavior that declares/uses it* (`:5`).
   - *Falsifiable Arbitration Rule:* Hold consumer text, credentials, route table, and evaluation inputs fixed and vary one cause at a time: if changing only the response at a fixed baseURL/port changes service/model identity → `kama`; if changing only credentials/auth → `kagi`; if changing only route mapping → `kumitate`; if changing only agent instructions → `kotoba`; if changing only task/scoring → `kengaku` (`:32`).
   - *Adjacency Rule:* If the evidence predicate belongs to another domain, record observed endpoint fact, name owning lane, and hand off; MUST NOT absorb source edits, credentials, or duplicate evaluation/route work (`:49-51`).

3. **Fleet Mission & Declared Axes (`../MISSION.md:20-31`, `../AXES.md:9-17`, `SCORECARD.md:340-366`):**
   - Assigned LIVE axes for `kama`: `operability + calibration` (`../shokunin.conf:52`, `SCORECARD.md:340`).
   - Primary C1 target axis for Round 14: **calibration** (lowest assigned axis, score 7; operability 8; stagnation waiver inactive; numeric score remains 7 → 7).
   - Single capability: `ollama-offline-evidence-replay` (offline Ollama `/api/tags` and `/api/ps` metadata evidence reconciliation; `claims.json:8-14`).
   - Adjacent domains: `kagi` (`freshness + calibration`), `kumitate` (`operability + coverage`), `kengaku` (`novelty + calibration`), `kotoba` (`depth + consistency`).

4. **Round-14 Proposal Cache (`.ufo/waves/round-14/advice/`):**
   - `ScopeSimplifier.md`: Keep classifier strictly offline stdlib, 4 flags, exact matching, no time logic, closed set of reason codes; resolve spec ambiguities upfront.
   - `AttackStaleness.md`: Captures are historical; `expires_at` lease expiry cannot be evaluated against wall clock; capture timing and cross-capture simultaneity are unknown.
   - `HistoricalIntegrity.md`: Crosswalk digest join was explicitly labeled `[INFERENCE]` in round 11 (`served-identity-crosswalk.md:45`); round 14 turns it into an inspectable offline classification policy, not a vendor behavior claim.
   - `ReviewCli.md`: Uncaught Python exceptions exit 1 (colliding with verdict exit 1); default argparse breaks stdout JSON contract; selftest must run child CLI.
   - `ReviewDigest.md`: Total precedence order required (F1); `invalid_input` vs `unknown` mapping (F2); non-exact alias with same digest must not be asserted absent from weights (F3).
   - `ReviewRemote.md`: Strict typing for `remote_model`/`remote_host` (F1); duplicate JSON keys override remote markers (F2); total precedence order (F3).
   - `ReviewSelftest.md`: Selftest exit codes collide with domain verdict exits (F1); empty cases.json must fail (F2); oracle independence (F3).
   - `SafetyInputs.md`: Duplicate JSON keys hide remote markers; truthiness on remote keys; echoing body values leaks secrets (e.g. `remote_host` userinfo URLs); non-regular files / memory exhaustion.
   - `AttackAmbiguity.md`: `ollama cp` alias with shared digest must not yield loaded without exact expected name match (A1); precedence ladder (P1).
   - `AttackReadiness.md`: `loaded_same_digest` is content correspondence, not host/daemon identity or readiness; exit-code convention is inverted relative to `kama-probe` (CE4).
   - `ReviewSource.md`: S012 has no remote fields; ps remote markers are defensive policy, not vendor documentation.

---

## 2. Mapping the Replay Feature to PROVINCE Ownership vs Adjacent Domains

The Round 14 capability (`ollama-offline-evidence-replay`) introduces an offline CLI tool (`tools/kama-ollama-evidence.py`) that reconciles exported JSON captures from Ollama endpoints (`GET /api/tags` and `GET /api/ps`) against an expected model identifier (`--expect`). To preserve Kama's province and avoid cross-domain bleed under `PROVINCE.md:40-43`, ownership boundaries must be strictly partitioned:

```
+----------------------------------------------------------------------------------------------------+
|                               KAMA PROVINCE (Local Model Serving)                                  |
|  Reconciles exported offline metadata: tags (available) vs ps (resident) for exact expected model  |
|  Verdicts: loaded_same_digest (0), available_not_loaded (1), remote_inventory (1),                 |
|            identity_conflict (1), unknown (2), invalid_input (2).                                  |
|  Invariants: readiness="unknown", scope="offline-captures-not-runtime", no live I/O.                |
+------------------------------------+----------------------------------+----------------------------+
                  |                                   |                               |
                  v                                   v                               v
    KAGI (Secrets & Credentials)          KUMITATE (Orchestration)             KENGAKU (LLM Evaluation)
  - Owns Bearer tokens, vault ops,      - Owns dispatch routes, model      - Owns generation quality,
    userinfo passwords in URLs.           cascades, alias tables           - Owns benchmark scoring, token
  - Kama treats remote_host as            (ollama cp), worker proxies.       accuracy, perplexity, context.
    opaque; NEVER echoes URI user-      - Kama evaluates exact name        - Kama exit 0 (loaded) proves
    info or auth headers into             only; NEVER manages alias          ONLY syntactic digest equality;
    stdout or reasons.                    mapping or routing fallbacks.      NEVER proves model is viable.
```

### A. Local Identity Reconciliation (`kama`)
- **Kama owns:** Reconciling whether exported static captures from `/api/tags` and `/api/ps` demonstrate that an exact expected model name or model alias has an identical non-empty SHA-256 digest in resident memory metadata (`loaded_same_digest`), is recorded in disk inventory without resident metadata (`available_not_loaded`), carries remote upstream delegation markers (`remote_inventory`), or contains conflicting identity/digests (`identity_conflict`).
- **Kama refuses:** Current daemon liveness, host installation status, network reachability, cross-capture simultaneity, or inference readiness. Kama outputs `readiness="unknown"` and `scope="offline-captures-not-runtime"` in every JSON record.

### B. Local Identity vs. Credentials & Auth Hygiene (`kagi`)
- **Kama owns:** Classifying the syntactic presence of `remote_host` on a selected model entry as `remote_inventory` (exit 1).
- **Kagi owns:** API authentication tokens, secret vaults, Bearer headers, and userinfo credential hygiene (`../MISSION.md:28`; `cross-lane-scope.md:26`).
- **Boundary Line:** As identified by `SafetyInputs.md`, a `remote_host` URL in Ollama can carry HTTP basic auth or userinfo (e.g. `https://api-user:secret-token@ollama-gateway.internal`). Kama's classifier must treat `remote_host` as an **opaque string token**, must NEVER resolve or dereference it, must NEVER parse or validate authentication material, and must NEVER echo the raw `remote_host` value into `reasons` or stdout. Kama emits fixed reason codes (e.g. `tags_remote_host_present`). Credential validation remains strictly `kagi`'s province.

### C. Local Identity vs. Routing & Orchestration (`kumitate`)
- **Kama owns:** Testing exact string equality between `--expect` and the selected entry's `name` or `model` attribute.
- **Kumitate owns:** Dispatch resolution, model-role mapping (e.g. OMP `modelRoles`), alias cascades (`ollama cp`), dynamic model routing, and fallback cascades from local to remote upstreams (`../MISSION.md:26`; `cross-lane-scope.md:28`).
- **Boundary Line:** If a local daemon has copied a model via `ollama cp llama3.2:latest gpt-4o-alias`, the `/api/ps` table may show `gpt-4o-alias` loaded with digest `D`, while the caller runs `--expect llama3.2:latest`. Kama's classifier strictly evaluates exact expected identity: because `llama3.2:latest` is absent from ps, Kama outputs `available_not_loaded` (exit 1). Kama **refuses to resolve the alias graph** or join by digest across disparate model names. Resolving whether an incoming request to `llama3.2` should be routed to resident alias `gpt-4o-alias` is a `kumitate` orchestration decision. Kama reports the exact endpoint observation; Kumitate resolves the route.

### D. Local Identity vs. Model Evaluation & Benchmark Quality (`kengaku`)
- **Kama owns:** Reporting whether the exported metadata records matching content digests.
- **Kengaku owns:** Evaluating model generation accuracy, benchmark scoring, perplexity, context window saturation, quantization degradation, and output safety (`../MISSION.md:24`; `cross-lane-scope.md:27`).
- **Boundary Line:** Exit 0 (`loaded_same_digest`) proves only that the metadata fields match at capture time. It does **not** certify that the weights in memory are intact, that CUDA inference will succeed, that the model can generate valid tokens, or that quantization is lossless. Kama explicitly emits `readiness="unknown"` to prevent callers from treating metadata correspondence as an evaluation certificate.

### E. Local Identity vs. Service Lifecycle & System Mutation (`Operator / L0`)
- **Kama owns:** Offline parsing of caller-supplied JSON files.
- **Operator (L0) owns:** Running `ollama run`, `ollama pull`, managing systemd units, or modifying host configuration.
- **Boundary Line:** The classifier is read-only, takes file paths, writes only JSON to stdout, and never touches `systemctl`, `~/.ollama`, or loopback network sockets.

---

## 3. Explicit Contradictions Across the Round Cache

A rigorous connector must name contradictions directly rather than smoothing them over:

1. **Contradiction 1: Digest Matching Across Mismatched Names (`ReviewDigest` F3 vs. `AttackAmbiguity` A1 / `ScopeSimplifier` item 5):**
   - *Conflict:* `ReviewDigest.md` (F3) argued that when ps contains an entry with the *same digest* as tags but a *different name*, returning `available_not_loaded` is an unwarranted negative claim, and recommended returning `unknown`. Conversely, `AttackAmbiguity.md` (A1) and `ScopeSimplifier.md` argue that selection is strictly exact name/model match, and that joining across names by digest would falsely validate unselected aliases.
   - *Resolution under PROVINCE:* `AttackAmbiguity.md` is correct. Kama answers only whether the *expected* model name is served/resident. Joining disparate names by digest is alias-resolution, which belongs to `kumitate`. Returning `available_not_loaded` is truthful to Kama's exact-match contract; Kama documents that `available_not_loaded` means "absent from ps under the exact expected name", not "weights are absent under all aliases".

2. **Contradiction 2: Precedence Collision Between Remote and Schema/Conflict Rules (`spec.json` vs. `ReviewRemote` F3 vs. `ReviewDigest` F1):**
   - *Conflict:* `spec.json` states "remote tags or selected ps markers -> remote_inventory regardless digest", but also states "conflicting name/model within selected entry or differing matching digests -> identity_conflict", and "remote takes precedence only after schema valid".
   - *Resolution under PROVINCE:* If a selected entry has a remote marker AND differing digests, `remote_inventory` must win (exit 1). S031 establishes that a remote model delegates execution to an upstream host; local digest comparison is meaningless once remote delegation is established. However, if the file envelope or field types are malformed, schema validation MUST win first (`invalid_input`, exit 2).

3. **Contradiction 3: Exit-Code Collision Between Verdicts, Selftest, and Runtime Errors (`ReviewCli` H1 vs. `ReviewSelftest` F1):**
   - *Conflict:* Python uncaught exceptions default to exit 1 (which collides with domain exit 1: `available_not_loaded`, `remote_inventory`, `identity_conflict`). Furthermore, `--selftest` exiting 0 on clean pass collides with domain exit 0 (`loaded_same_digest`).
   - *Resolution under PROVINCE:* The classifier's `main()` must intercept all exceptions and map them to exit 2 (`invalid_input`) with JSON on stdout. Consumers and wrappers must key on `finding_id` and schema type, never raw process exit code alone.

---

## 4. UFO-FSD Connector Synthesis: The Proposed Non-Obvious Move

### The Move: Bind Replay Findings to Sibling Domain Boundaries via an Explicit 6-Tier Total Precedence Ladder & Closed Reason Taxonomy

Rather than allowing each seat to implement ad-hoc checks or leaving precedence undefined across remote, alias, conflict, and schema conditions, Kama executes a single compatible synthesis:

1. **The 6-Tier Total Precedence Ladder (Deterministic Evaluation Pipeline):**
   The classifier evaluates each case through six strictly ordered tiers and halts on first match:
   - **Tier 1 (`invalid_input`, exit 2):** Structural & schema validation. Unreadable files, non-JSON bytes, duplicate JSON keys (via `object_pairs_hook`), non-object top level, missing/non-array `models`, non-object entries, non-string `name`/`model`/`digest`, wrong-type remote keys (`remote_model`/`remote_host` present as non-string, including `null`, `0`, `false`), missing `--tags` or `--ps` file.
   - **Tier 2 (`unknown`, exit 2):** Selection ambiguity. Filter `models` where `entry["name"] == expect` or `entry["model"] == expect`. If matching count in tags is 0 → `unknown` (reason: `tags_expected_model_not_found`). If matching count in tags > 1 or ps > 1 → `unknown` (reason: `duplicate_matching_entries`).
   - **Tier 3 (`remote_inventory`, exit 1):** Remote delegation. The single selected tags entry or selected ps entry has non-empty string `remote_model` or `remote_host`. Evaluated *before* digest comparison ("regardless of digest"). Emits fixed reasons (`tags_remote_marker_present` or `ps_remote_marker_present`) without echoing URI content.
   - **Tier 4 (`identity_conflict`, exit 1):** Internal or digest contradiction. Within-entry conflict (`entry["name"] != entry["model"]` on either selected entry), OR selected tags digest does not equal selected ps digest (exact character-by-character string comparison).
   - **Tier 5 (`available_not_loaded`, exit 1):** Unloaded disk inventory. Exactly one clean selected tags entry; selected ps count is 0 (including valid empty `models: []`). Reason: `no_exact_ps_match`.
   - **Tier 6 (`loaded_same_digest`, exit 0):** Exact metadata correspondence. Exactly one clean selected tags entry, exactly one clean selected ps entry, equal non-empty string digests, zero remote markers. Always emits `readiness="unknown"`, `scope="offline-captures-not-runtime"`.

2. **Cross-Domain Handoff Binding Table (to publish in `corpus/knowledge/ollama-evidence-replay.md` and Round 14 Report):**
   Every replay finding is bound to the Falsifiable Arbitration Rule, establishing exactly who owns what when a verdict is emitted:

| Classifier Finding | Verdict Exit | What Kama Certifies (Owns) | What Kama Refuses (Handoff to Sibling / Operator) |
|---|---|---|---|
| `loaded_same_digest` | 0 | Exported tags and ps metadata agree on exact name and SHA-256 digest at capture time. | **kengaku:** Does NOT certify inference readiness, token generation quality, or evaluation validity.<br>**Operator:** Does NOT prove daemon is currently running on this host. |
| `available_not_loaded` | 1 | Model is present in tags disk catalog but absent from ps memory table under the exact expected name. | **kumitate:** Does NOT inspect whether weights are resident under an alias (`ollama cp`). Alias route resolution belongs to kumitate. |
| `remote_inventory` | 1 | Selected model entry delegates to upstream upstream host/model (`remote_model`/`remote_host`). | **kagi:** Does NOT validate or echo userinfo credentials or auth headers.<br>**kumitate:** Does NOT manage remote proxy dispatch or fallback cascades. |
| `identity_conflict` | 1 | Model name and alias disagree within entry, or tags and ps digests contradict. | **Operator:** Does NOT repair corrupt manifests or reconcile conflicting tags. |
| `unknown` | 2 | Expected model is unlisted in tags, or multiple conflicting entries match `--expect`. | **Operator:** Does NOT select among ambiguous candidates or pull missing models. |
| `invalid_input` | 2 | Input capture is malformed, unreadable, has duplicate JSON keys, or wrong field types. | **Operator:** Caller must provide valid exported JSON files. |

---

## 5. Affected Axes

- **Calibration (Primary C1 Axis, Score 7 → 7):**
  - *Improvement:* Directly strengthens calibration by replacing prose-only tags/ps distinctions with an executable fail-closed classifier and fixed adversarial fixtures. Eliminates false-positive readiness claims (`readiness="unknown"` invariant), prevents false-positive local claims on remote models, and eliminates ambiguity through the total precedence ladder.
  - *Honest Score:* Calibration score remains **7 → 7 (delta 0)**; fixture coverage over synthetic inputs is not inflated into universal domain mastery.
- **Adjacency (Protected Axis):**
  - *Protection:* Strict adherence to `PROVINCE.md:40-43`. Zero absorption of `kagi` credentials (opaque remote markers, zero secret leakage), `kumitate` routing (refusal to resolve alias graphs by digest), or `kengaku` evaluation (readiness remains strictly unknown).
- **Operability & Freshness (Protected Axes):**
  - *Protection:* Operability remains 8; the tool is an offline stdlib Python CLI with zero runtime dependencies and robust child-process selftests. Freshness remains 8; no temporal assumptions or unverified live probe claims are introduced.
- **Depth (Protected Axis):**
  - *Improvement:* Decision table with real thresholds and named error codes formalizes the operational replay contract.

---

## 6. Risks & Mitigations

1. **Risk 1: Alias-Resident Model Misinterpreted as Unloaded.**
   - *Risk:* A user expects `llama3.2`, but Ollama loaded it under copied alias `llama3.2-backup`. Kama reports `available_not_loaded`.
   - *Mitigation:* Document in `ollama-evidence-replay.md` that `available_not_loaded` means "absent under the exact expected name". Explicitly hand off alias-graph traversal to `kumitate`.
2. **Risk 2: Credential Leakage in Remote Markers.**
   - *Risk:* An input `remote_host` carries userinfo `https://user:password@host`, which leaks into logs if echoed.
   - *Mitigation:* `reasons` must contain only fixed enumeration tokens (e.g. `ps_remote_host_present`). Never echo field values or input file paths into stdout.
3. **Risk 3: Exit-Code Misinterpretation in Shell Scripts.**
   - *Risk:* A caller runs `if kama-ollama-evidence ...; then send_request; fi`, treating exit 0 as permission to infer.
   - *Mitigation:* The `--help` epilog and documentation explicitly warn that exit 0 is metadata correspondence only, NOT readiness. Wrappers must inspect `readiness` (always `"unknown"`).

---

## 7. Verification

Checks L1 can run during final integration (not run by SiblingOverlap):

1. **Adjacency & Secret Hygiene Check:**
   - Verify that `tools/kama-ollama-evidence.py` contains zero imports of `urllib`, `http`, `socket`, `requests`, `ssl`, or `os.environ`.
   - Verify that no exception string, input path, or `remote_host` body content is interpolated into `reasons`.
2. **Deterministic Precedence Verification:**
   - Execute child CLI selftest on adversarial fixtures: confirm that remote markers take precedence over differing digests (`remote_inventory`, exit 1), but schema defects take precedence over remote markers (`invalid_input`, exit 2).
3. **Exact-Name Alias Boundary Check:**
   - Run a fixture where tags has model A and B with digest D, ps has model B with digest D, and `--expect` is A. Confirm the result is `available_not_loaded` (exit 1), NOT `loaded_same_digest`.
4. **Historical Immutability:**
   - Confirm zero byte modifications in `corpus/knowledge/cross-lane-scope.md` lines 1–80 or `PROVINCE.md`.

---

## 8. Bounded Owner Recommendations

- **To `KamaR14.Classifier` (`tools/kama-ollama-evidence.py`):**
  1. Implement the 6-Tier Total Precedence Ladder exactly as specified in Section 4.
  2. Use `object_pairs_hook` in `json.loads` to reject duplicate JSON keys → `invalid_input` (exit 2).
  3. Enforce strict `type(x) is str` for `remote_model` and `remote_host`; treat `null`, `0`, `false`, `""` as schema violations (`invalid_input`), NOT local models.
  4. Never interpolate input values (especially `remote_host`) into `reasons`; use fixed enum tokens only.
  5. Wrap `main()` with a top-level exception handler mapping unexpected errors to exit 2 (`invalid_input`) with JSON on stdout.
- **To `KamaR14.Fixtures` (`tests/ollama-evidence/cases.json`):**
  1. Include the alias control: tags has A and B with digest D; ps has only B with digest D; expect A → exit 1 `available_not_loaded` (verifies refusal of alias route resolution).
  2. Include the userinfo remote control: `remote_host: "https://user:pass@host"` → exit 1 `remote_inventory` (verifies remote marker handling without credential inspection).
  3. Include the remote + digest conflict control: remote marker present, digests differ → exit 1 `remote_inventory` (verifies precedence over `identity_conflict`).
  4. Include the remote + malformed schema control: `remote_host: 42` → exit 2 `invalid_input` (verifies schema precedence over remote).
- **To `KamaR14.ReplayKnowledge` (`corpus/knowledge/ollama-evidence-replay.md`):**
  1. Include the Cross-Domain Handoff Binding Table (Section 4) mapping each finding to `kagi`, `kumitate`, and `kengaku`.
  2. Explicitly label the tags-to-ps digest join as `[INFERENCE]`.
  3. Document that `available_not_loaded` means absence under the exact queried name, leaving alias resolution to `kumitate`.
- **To `KamaR14.QualityCriterion` (`corpus/QUALITY.md`):**
  1. Append KQ17 stating that offline metadata correspondence must never be asserted as runtime readiness, that outer verdict exit must remain distinct from selected subfinding counts, and that remote/alias/secret boundaries must fail closed.
- **To Main / L1 Planner:**
  1. Retain existing historical handoff lines in `cross-lane-scope.md` verbatim.
  2. In the Round 14 Fleet Report, cite the explicit handoffs: `kagi` retains credential hygiene, `kumitate` retains alias resolution and route dispatch, and `kengaku` retains model evaluation.
