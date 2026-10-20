# FindingMap — UFO-FSD Connector: Per-Case Findings, Outer Fail-Closed Gate, and Aggregate Harness Exit Decoupling

**Seat:** `KamaR14.FindingMap` (role: connector, leaf member)  
**Lane Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`  
**Report Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/advice/FindingMap.md`  
**Status:** Static analysis and proposal synthesis. No builds, tests, linters, or verification runs executed (reserved for L1). No tools installed or upgraded.

---

## 1. Evidence

### A. Contract and Shared Interface (`spec.json`)
- **Classifier CLI & stdout contract:** `tools/kama-ollama-evidence.py --tags PATH --ps PATH --expect EXACT_NAME`.
  - JSON stdout schema: `kama-ollama-evidence/v1`.
  - Required keys: `finding_id`, `verdict_exit`, `expected_model`, `readiness="unknown"`, `scope="offline-captures-not-runtime"`, `reasons` (list).
  - Exit code mapping:
    - `exit 0`: ONLY `loaded_same_digest` (metadata correspondence, NOT readiness).
    - `exit 1`: `available_not_loaded`, `remote_inventory`, `identity_conflict`.
    - `exit 2`: `unknown` / `invalid_input`.
- **Harness & Selftest contract:**
  - `measure.py`: Evaluates test cases from `tests/ollama-evidence/cases.json` via child CLI invocations; emits `total`, `passed`, `failed`, `records`, `verdict_exit`; `exit 0` indicates all fixtures passed, else `exit 1`.
  - `--selftest`: Spawns actual child CLI fixtures with literal expected exits/IDs; emits `finding_id` (`clean` or `selftest_failed`), `verdict_exit` (0 or 1).
- **Readiness & Timing Boundaries:** "No timestamps/expiry/current-liveness inferences. Inputs explicitly caller-authorized exported metadata, no acquisition feature."

### B. Precedent Evidence in Repository & Historical Lessons
- **Round 12/13 Mistake D2 (`round-13-verifier-spotcheck.md:258–267`, `round-12.md:207–214`):**
  A repointed manifest produced an outer verdict of `manifest_invalid` (exit 2, could-not-evaluate), while an inner mismatch counter registered 1 under a verified anchor. Conflating the inner sub-finding count with the outer evaluation exit resulted in historical presentation debt. Outer fail-closed verdicts outrank and preempt inner comparative findings.
- **`kama-probe` Exit Inversion (`tools/kama-probe.sh:925–926`, `SKILL.md:13–14`, `AttackReadiness.md:36–45`):**
  In `kama-probe check`, exit 0 = all rows reconcile, exit 1 = probe error, exit 2 = drift. In the new classifier, exit 0 = single-model metadata correspondence, exit 1 = definite domain divergence (`available_not_loaded`, `remote_inventory`, `identity_conflict`), exit 2 = `unknown` / `invalid_input`. If unaddressed, downstream scripts using shell `&&` conditionals will confuse test/tool exit with runtime health.
- **Served-Identity Crosswalk Grounding (`corpus/knowledge/served-identity-crosswalk.md:29–45`):**
  Tags-to-ps digest join is explicitly an `[INFERENCE]`, not documented vendor join semantics. S011/S031 confirm tags may contain remote entries (`remote_model`, `remote_host`); S012 confirms ps entries are time-bounded (`expires_at`). Neither establishes live execution readiness.

### C. Peer Proposal Syntheses (`.ufo/waves/round-14/advice/`)
- `ReviewSelftest.md` (F1, F5): Warning that selftest/harness exit 0/1 collides with classifier domain verdicts; warns against using the same output schema namespace.
- `ReviewSchema.md` (H1, H2, H4): Unhandled Python exceptions default to exit 1 (colliding with domain exit 1); `--help` defaults to exit 0; lack of explicit precedence creates evaluation ambiguity.
- `ReviewRemote.md` (F3, F4) & `ReviewDigest.md` (F1, F2): Propose precedence ladders where structural validation and entry selection fail closed before remote or digest checks occur.
- `AttackReadiness.md` (CE1–CE5) & `AttackStaleness.md` (CE1–CE4): Exit 0 is strictly offline metadata correspondence across two files; it does not verify same-host, same-daemon, concurrent timing, or serving readiness.
- `AttackAmbiguity.md` (A1–A22, P1): Exact string selection on `name`/`model` only, never by digest; duplicate selected entries must fail closed to `unknown` (exit 2).

---

## 2. Affected Axes

1. **Calibration (Primary Assigned Axis, currently 7; target: maintain 7 without inflation):**
   - Eliminates over-claiming: guarantees that exit 0 (`loaded_same_digest`) can never be construed or consumed as model serving readiness.
   - Enforces strict correspondence: verifies that every test record asserts a literal 2-tuple `(verdict_exit, finding_id)`, preventing exit-code false positives.
   - Guarantees fail-closed discipline: ensures unparseable, malformed, or ambiguous evidence terminates at outer exit 2 (`invalid_input` or `unknown`), preventing partial matches from leaking into exit 1 or exit 0.
2. **Operability (Assigned Axis, currently 8):**
   - Eliminates exit-code collisions between domain classifier results and test harness / selftest results.
   - Protects downstream orchestrators from treating crash failures (exit 1) as valid domain mismatch verdicts.
   - Preserves deterministic, machine-readable JSON outputs across all CLI paths.

---

## 3. Proposed Move: Two-Tier Fail-Closed Envelope Protocol and Meta-Exit Decoupling

Synthesize the round's advisory proposals into one unified, bounded architectural move connecting per-case evaluation to aggregate verification:

```
+-----------------------------------------------------------------------------------------+
|                                    INPUT PROCESSING                                     |
|  CLI Arguments: --tags PATH --ps PATH --expect EXACT_NAME                               |
+------------------------------------------------------------+----------------------------+
                                                             |
                                                             v
+-----------------------------------------------------------------------------------------+
|                         TIER 1: OUTER ENVELOPE GATE (Fail-Closed)                       |
|  - Files unreadable / missing / non-regular / size cap exceeded    --> exit 2 (invalid_input)|
|  - JSON malformed / duplicate keys (object_pairs_hook)             --> exit 2 (invalid_input)|
|  - Top-level 'models' missing or not array                         --> exit 2 (invalid_input)|
|  - Entry not object / name, model, digest not valid string         --> exit 2 (invalid_input)|
|  - Present remote_model/remote_host not non-empty string           --> exit 2 (invalid_input)|
|  - Matches for --expect in tags == 0                               --> exit 2 (unknown)      |
|  - Matches for --expect in tags > 1 OR in ps > 1                   --> exit 2 (unknown)      |
+------------------------------------------------------------+----------------------------+
                                                             | (Tier 1 Clean: Exactly 1 tags match,
                                                             |  and 0 or 1 ps match)
                                                             v
+-----------------------------------------------------------------------------------------+
|                       TIER 2: INNER RECONCILIATION LADDER (Domain)                      |
|  1. Within-entry mismatch: selected tags/ps name != model          --> exit 1 (identity_conflict)
|  2. Remote marker: non-empty remote_model/remote_host on tags/ps   --> exit 1 (remote_inventory)
|  3. Unloaded: valid ps array, but 0 ps matches for --expect        --> exit 1 (available_not_loaded)
|  4. Digest divergence: selected tags digest != selected ps digest  --> exit 1 (identity_conflict)
|  5. Correspondence: selected tags digest == selected ps digest     --> exit 0 (loaded_same_digest)
|     [INVARIANT: readiness="unknown", scope="offline-captures-not-runtime"]               |
+-----------------------------------------------------------------------------------------+
```

### Component A: Two-Tier Classifier Evaluation (Resolving Mistake D2 Precedent)
The classifier `tools/kama-ollama-evidence.py` must partition execution into two discrete tiers:
1. **Tier 1 (Outer Envelope Gate):**
   Evaluates all structural, syntactic, and selection constraints.
   - Any I/O error, non-regular file, JSON decode failure, duplicate key, missing `models` array, or invalid field type terminates immediately with **Exit 2, `finding_id: "invalid_input"`**.
   - If tags contains zero matches for `--expect`, terminate immediately with **Exit 2, `finding_id: "unknown"`**, regardless of ps contents or remote markers.
   - If tags contains >1 matches or ps contains >1 matches for `--expect`, terminate immediately with **Exit 2, `finding_id: "unknown"`**.
   - *Crucial boundary:* No inner domain comparison (remote precedence, digest match, or availability) is evaluated if Tier 1 fails.
2. **Tier 2 (Inner Reconciliation Ladder):**
   Evaluated strictly when Tier 1 succeeds:
   - Step 1: Selected entry `name != model` within tags or ps $\to$ **Exit 1, `identity_conflict`**.
   - Step 2: Selected tags or ps entry has non-empty `remote_model` or `remote_host` $\to$ **Exit 1, `remote_inventory`** (evaluated before digest comparison, honoring "regardless digest").
   - Step 3: Selected ps entry absent (from a valid ps envelope) $\to$ **Exit 1, `available_not_loaded`**.
   - Step 4: Selected tags digest $\neq$ selected ps digest $\to$ **Exit 1, `identity_conflict`**.
   - Step 5: Selected tags digest $==$ selected ps digest $\to$ **Exit 0, `loaded_same_digest`**.
   - Output invariants: Every result across Exits 0, 1, and 2 carries `readiness: "unknown"` and `scope: "offline-captures-not-runtime"`.

### Component B: Meta-Exit Decoupling in Harness and Selftest
1. **Distinct Output Schema (Confirmed Implemented by `KamaR14.Harness`):**
   The test runner (`measure.py`) does NOT output the domain schema `kama-ollama-evidence/v1`. It emits its own isolated measurement schema:
   - Schema name: `kama-round-14-measure/v1`.
   - Keys: `verdict_exit` (0 strictly when all fixtures pass, else 1), `total`, `passed`, `failed`, `records`. No domain finding is emitted or inferred.
   - For `--selftest`: Spawns child CLI fixtures and reports `finding_id: clean|selftest_failed`.
2. **Strict 2-Tuple Assertion (Confirmed Implemented by `KamaR14.Harness`):**
   In `measure.py`, a test record passes IF AND ONLY IF:
   $$\text{child\_process\_exit} == \text{expected\_exit} \quad \land \quad \text{child\_finding\_id} == \text{expected\_finding\_id}$$
   Matching exit code alone is rejected. This prevents an unhandled exception (CPython exit 1) from accidentally passing an `identity_conflict` (exit 1) test case. Verified satisfied by `KamaR14.Harness`.

---

## 4. Risks and Second-Order Effects

- **Runtime & Substrate Surfaces:** Zero additional packages required; implemented entirely via Python stdlib (`json`, `sys`, `argparse`, `pathlib`). No network access, socket calls, or disk writes outside stdout and child-CLI temporary directories.
- **Contract Surface:** Preserves the shared interface without altering the assigned exit codes (0 for `loaded_same_digest`; 1 for `available_not_loaded`, `remote_inventory`, `identity_conflict`; 2 for `unknown`, `invalid_input`).
- **Fail-Closed Strictness (Trade-off):** In Tier 1, an unselected malformed entry in `tags.json` causes `invalid_input` (exit 2) even if the model requested via `--expect` is valid. This trade-off is intentionally accepted: an invalid evidence envelope cannot guarantee trustworthy partition boundaries.
- **Operator Consumption:** Prevents shell scripts from interpreting `measure.py` exit 0 as proof that local models are running, and prevents downstream orchestration from treating classifier exit 1 as an execution crash.

---

## 5. Verification Checklist (for L1 Canonical Integrator)

*This seat does not execute verification. The following steps are recommended for L1 final checks:*

1. **Static AST / Token Absence:**
   - Confirm `tools/kama-ollama-evidence.py` contains no imports of `urllib`, `requests`, `http`, `socket`, `time`, or `datetime`.
   - Confirm no calls to `os.environ` or external probe scripts.
2. **Fixture Literal Completeness (`tests/ollama-evidence/cases.json`):**
   - Confirm at least 16 literal fixture objects covering Tier 1 (`invalid_input`, `unknown`) and Tier 2 (`remote_inventory`, `identity_conflict`, `available_not_loaded`, `loaded_same_digest`).
   - Verify all test cases contain literal `expected_exit` and `expected_finding`.
3. **Child-CLI Execution & Tuple Check:**
   - Execute `measure.py` and `--selftest`: verify that all child cases validate both exit code and finding ID.
   - Confirm `measure.py` exits 0 with `failed: 0`.
4. **Readiness Invariant Check:**
   - Inspect stdout of exit 0 cases: confirm `readiness == "unknown"` and `scope == "offline-captures-not-runtime"`.
