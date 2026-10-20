# PriorCoverage — Round 14 UFO-FSD Connector Advisory

**Seat:** `KamaR14.PriorCoverage` (role: connector, leaf member)  
**Lane Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`  
**Report Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/advice/PriorCoverage.md`  
**Date:** 2026-10-20 UTC  
**Tooling Record:** No packages, tools, or dependencies installed or upgraded (none required).  
**Verification:** Leaf contract strictly adhered to; no checks, builds, tests, linters, or smoke runs executed.

---

## 1. Evidence: Prior Coverage vs. New Replay Capability

### A. What Was Already Held at HEAD (`e1b3d74`)
The local corpus already documents and maintains the conceptual tags/ps/digest crosswalk:
1. **Tags vs. Ps Split (Prior since Round 10/11):**
   - `corpus/knowledge/runtime-health-surface-matrix.md:17` records `/api/tags` = available models and `/api/ps` = running models.
   - `corpus/SOURCES.md` S011 (`GET /api/tags`) and S012 (`GET /api/ps`) define the schema fields (`name`, `model`, `digest`, `expires_at`).
2. **Four Predicates & Remote Inventory Limits (Prior in Round 11):**
   - `corpus/knowledge/served-identity-crosswalk.md` rigorously separates four distinct predicates: availability (`/api/tags`), loaded residency (`/api/ps`), advertised identity (`/v1/models`), and inference readiness.
   - S031 and `crosswalk:29,38` establish that `/api/tags` entries may carry `remote_model` and `remote_host`, meaning catalog availability is not proof of local weights.
   - `crosswalk:29,36` documents that `/api/ps` is time-bounded by `expires_at` and is not durable readiness.
   - `crosswalk:35` explicitly grounds failure case 3: an entry listed in `/api/tags` and absent from `/api/ps` does not establish on-demand loading behavior either way.
3. **Digest Join Designated as `[INFERENCE]` (Prior in Round 11/12):**
   - `served-identity-crosswalk.md:29,45` explicitly states: *"joining tags/ps by digest is [INFERENCE] — the pages do not describe the join and prove no on-disk artifact identity"*.
   - Round 12 D4 correction (`served-identity-crosswalk.md:87-134`) reaffirmed that the remote-locality conclusion is `[INFERENCE]`, and that `supersedes S011` is lane-registry supersession rather than an upstream API change.
4. **Precedent from Round 11 Verification:**
   - Round 11 `PriorCoverage.md` (`.ufo/waves/round-11/verification/PriorCoverage.md:29-40`) previously rejected crediting the tags/ps split as new.

### B. What is NEW in Round 14
The corpus held the conceptual crosswalk only as analytical prose. It completely lacked an **executable, offline replay classifier**:
1. **Executable Repertoire:** `tools/kama-ollama-evidence.py` provides a deterministic offline CLI reconciling caller-authorized `/api/tags` and `/api/ps` JSON exports against `--expect <name>` without network, daemons, or sockets.
2. **Machine-Readable Contract:** Emits schema `kama-ollama-evidence/v1` with six mutually exclusive findings (`loaded_same_digest`, `available_not_loaded`, `remote_inventory`, `identity_conflict`, `unknown`, `invalid_input`), fixed exit codes (0, 1, 2), and mandatory `readiness="unknown"`.
3. **Adversarial Control Suite:** `tests/ollama-evidence/cases.json` supplies independent literal fixtures (16+ controls) exercising adversarial edge cases (remote precedence, duplicate selection, alias ambiguity, missing/empty digest, malformed envelopes, casing, and no-GGUF normalization).
4. **Fail-Closed Verification Harness:** Child-CLI `--selftest` and `.ufo/waves/round-14/measure.py` enforce exact literal exit and finding equality without import shortcuts or fallback skips.

---

## 2. Honest Expansion Credit Boundaries

To prevent overclaiming, credit must be strictly bounded across all axes and scorecard sections:

| Surface / Claim | Allowable Credit | Forbidden Overclaim (Must Refuse) |
|---|---|---|
| **Capability Table (`SCORECARD.md`)** | Add new capability row: `ollama-offline-evidence-replay`. What it does: offline reconciliation of exported tags/ps captures to classify metadata correspondence and adversarial edge cases without network or readiness assumptions. | DO NOT claim live Ollama integration, daemon monitoring, or runtime health probing. (SCORECARD lines 23 and 27 explicitly state Ollama remains fixture-shaped parser evidence). |
| **Calibration Axis** | Calibration improved: the lane operationalizes its inferential digest join into a strict, fail-closed, fail-capable decision procedure with 6 stable findings and fixed exit codes. | Numeric score remains **7 → 7 (delta 0)**. AXES and SCORECARD rules forbid scalar advancement without an objective denominator or outside non-author review. |
| **Coverage Axis** | Coverage remains **9 → 9 (delta 0)**. Repertoire gains an operational CLI, but no new serving engine surface, provider protocol, or live endpoint is added. | DO NOT claim coverage expansion from the tags/ps distinction, remote tags caveat, or expiry fields (already held in Round 11/12). |
| **Operability Axis** | Operability remains **8 → 8 (delta 0)**. Serving probe `tools/kama-probe.sh` and registered consumers are untouched; no endpoints are restored. | DO NOT claim live endpoint reconciliation or confuse offline capture replay with live probe execution. |
| **Freshness Axis** | Freshness remains **8 → 8 (delta 0)**. Captures are static, caller-authorized exports. | DO NOT evaluate `expires_at` against host clock or claim current liveness/freshness from offline files. |
| **Knowledge Base (`corpus/knowledge/`)** | New entry `ollama-evidence-replay.md` documents tool usage, CLI interface, and operational decision table. | DO NOT present the digest join as vendor-certified artifact identity or claim vendor docs define the join policy; mark as `[INFERENCE]`. |

---

## 3. Affected Axes (Godspeed Posture)

1. **Calibration (Lowest Assigned, 7 vs 8):** Improved in precision and failure capability. Moves from descriptive prose to executable verification with fixed adversarial fixtures. Kept honest by enforcing `readiness="unknown"` and fail-closed exits.
2. **Operability (Assigned, 8):** Preserved and unharmed. The new offline tool is isolated from `tools/kama-probe.sh`. Exit-code semantics differences are documented to prevent shell pipeline misuse.
3. **Coverage (Tracked, 9):** Preserved and unharmed. Avoids inflationary double-counting of prior-held concepts.
4. **Freshness (Tracked, 8):** Preserved and unharmed. Explicitly refuses time-decay or capture-simultaneity assumptions.

---

## 4. Proposed Move: Two-Tier Evaluation Pipeline Architecture

### A. Context & Contradictions Across Proposals
Reviewers and critics (`ReviewRemote` F3, `ReviewDigest` F1, `ReviewSchema` H4, `ReviewFixtures` H2, `AttackAmbiguity` P1) discovered three conflicting requirements in the specification:
1. *"remote tags or selected ps markers -> remote_inventory regardless digest"* (exit 1).
2. *"missing identity/digest ... fail closed unknown/invalid_input"* (exit 2).
3. *"remote takes precedence only after schema valid"* (Fixtures target).

If an input has a remote marker but a missing/empty digest, or a malformed unselected entry, should it exit 1 (`remote_inventory`) or exit 2 (`invalid_input`)? Furthermore, `AttackReadiness` CE4 identified that exit 0 in `kama-probe.sh` means "all consumers reconcile", whereas in `kama-ollama-evidence.py` exit 0 means `loaded_same_digest` on offline captures with `readiness="unknown"`.

### B. Synthesized Move
Adopt a strict **Two-Tier Evaluation Pipeline Architecture** in `tools/kama-ollama-evidence.py` and mirror it as the literal fixture oracle in `tests/ollama-evidence/cases.json`:

```
+-------------------------------------------------------------------------+
| Tier 1: Syntactic & Structural Invariant Gate (Fail-Closed -> Exit 2)   |
| - Parse JSON with duplicate-key rejection (object_pairs_hook)           |
| - Verify top-level envelopes are objects containing 'models' list       |
| - Validate every entry: non-empty string 'name', 'model'                |
| - Strict remote typing: present remote_model/remote_host must be string |
|   (null, bool, number, [], {} -> invalid_input)                         |
| - Input file existence, non-directory, non-empty                        |
| => ANY FAILURE -> finding_id: "invalid_input", verdict_exit: 2           |
+-------------------------------------------------------------------------+
                                    | (Schema Valid)
                                    v
+-------------------------------------------------------------------------+
| Tier 2: Model Selection & Semantic Resolution                           |
| 2a. Selection: match entry iff expect == name OR expect == model        |
|     - selected count in tags == 0 -> "unknown" (exit 2)                 |
|     - selected count in tags > 1 OR ps > 1 -> "unknown" (exit 2)        |
|     - selected entry missing 'digest' -> "invalid_input" (exit 2)       |
|                                                                         |
| 2b. Within-Entry Coherence:                                             |
|     - selected entry name != model -> "identity_conflict" (exit 1)      |
|                                                                         |
| 2c. Remote Inventory Gate ("Regardless Digest"):                       |
|     - selected tags or ps entry has non-empty remote string             |
|       -> "remote_inventory" (exit 1) [EVALUATED BEFORE DIGEST JOIN]      |
|                                                                         |
| 2d. Cross-Capture Digest Correspondence:                                |
|     - selected ps entry absent (ps models valid)                        |
|       -> "available_not_loaded" (exit 1)                                |
|     - selected tags digest != ps digest                                 |
|       -> "identity_conflict" (exit 1)                                   |
|     - selected tags digest == ps digest (both non-empty strings)        |
|       -> "loaded_same_digest" (exit 0), readiness: "unknown"            |
+-------------------------------------------------------------------------+
```

### C. Second-Order Effects & Benefits
1. **Contract Harmony:** Satisfies all three contract sentences without compromise: schema validity runs first in Tier 1; remote markers take precedence over digest comparison in Tier 2c ("regardless digest"); missing digests and ambiguous selections fail closed in Tier 2a.
2. **Oracle Determinism:** Provides `Fixtures` (`cases.json`) and `Harness` (`measure.py`) with a single, unambiguous ground truth for all 16+ cases.
3. **Safety & Zero Leakage:** Completely eliminates uncaught Python exceptions (which otherwise exit 1 and collide with domain verdicts) and prevents duplicate JSON keys from masking remote markers.
4. **Clear Credit Boundary:** Positions the tool precisely as a metadata consistency classifier, preventing false inference of runtime readiness.

---

## 5. Risks and Mitigations

| Risk | Severity | Second-Order Impact | Concrete Mitigation |
|---|---|---|---|
| **Shell Pipeline Misuse** | High | An operator uses `tool && route_traffic` treating exit 0 as operational health. | Force `readiness: "unknown"` and `scope: "offline-captures-not-runtime"` in every stdout JSON; document exit code semantics in `--help` and `ollama-evidence-replay.md`. |
| **Alias Mismatch False Negative** | Medium | `ollama cp` creates an alias with the same digest; query against original name yields `available_not_loaded`. | `ReplayKnowledge` documents that `available_not_loaded` denotes absence under `--expect` in the supplied capture, not that weights are unresident under other aliases. |
| **Timestamp / Expiry Staleness** | Medium | Operator assumes ps export reflects current memory state. | The classifier completely ignores `expires_at` and host time; Fixtures includes a control with an expired timestamp that still yields `loaded_same_digest`. |
| **Common-Mode Selftest Vacuity** | Medium | Selftest passes vacuously if `cases.json` is missing, empty, or derived from code output. | Harness asserts `total == len(cases)` with a floor of at least 16; tests independent, hand-authored literals; missing tool fails cases as unsupported. |

---

## 6. Verification Checklist for L1 Final Gate

Leaf agents do not run verification; L1 integrator must execute and record:
1. `python3 tools/kama-ollama-evidence.py --help` -> exit 0, clean plaintext help.
2. `python3 tools/kama-ollama-evidence.py --selftest` -> exit 0, finding_id `clean`, 0 failed cases.
3. `python3 .ufo/waves/round-14/measure.py` -> exit 0, total >= 16, passed == total, failed == 0.
4. Negative control: `measure.py --tool absent_path` -> exit 1, failed == total (no skips).
5. Source census: `scripts/sources-census.sh validate` and `census` -> exit 0, row count 33 (S012/S031 used-by updated).
6. Quality check: `corpus/QUALITY.md` line count incremented by 1 (KQ17 appended, preserved prefix).
7. Immutability: Zero deletions in historical lessons `round-1*.md` through `round-13*.md` and verifier spotchecks.
