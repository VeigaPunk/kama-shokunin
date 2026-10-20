# Round 14 — TeachingSweep: Operator Lessons & Newest Verifier D2 Discovery

**Seat:** `KamaR14.TeachingSweep` (scout)  
**Lane:** `kama-shokunin` (root `/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Date:** 2026-10-20 UTC  
**Scope:** Discover operator lessons and newest verifier D2; report unreflected teaching or empty discovery. No secret paths. Read-only except this report. Bounded owner recommendations for in-flight files.  
**Boundary:** Leaf member — no subagent dispatch, no background jobs, no commits/pushes. Zero test, build, lint, format, or gate executions. Unrun $\neq$ pass. Tools installed/updated: none.

---

## 1. Axes (Godspeed Framing)

- **calibration:** Primary target axis for C1 (`ollama-offline-evidence-replay`, lowest assigned score 7 vs operability 8; score 7 $\to$ 7, delta 0). Must maintain exact correspondence between offline evidence contracts and executable classification without overclaiming runtime readiness.
- **operability:** Serving implementations, endpoint configurations, and host services remain completely unmutated; offline replay tool operates solely on caller-provided static JSON exports.
- **provenance / integrity:** Historical lessons, verifier records, and past receipts are strictly immutable; clarifications and corrections land strictly via append-only prose in current round artifacts.
- **quality / discernment:** Faithfully records verifier routed defects (D2) and operator demand boundaries without inflating credit or substituting gate mechanics for knowledge gains.

---

## 2. Operator Lessons Sweep & Discovery

### 2.1 Lane-Level Sweep (`/home/vgpnk/Projects/shokunin/kama-shokunin`)

Exhaustive filesystem and git history sweeps were conducted within the lane repository:

1. **Filesystem Pattern Search for `operator-*.md`:**
   - Command: `find /home/vgpnk/Projects/shokunin/kama-shokunin -name 'operator-*.md'`
   - Exit code: `0`
   - Result: `(empty - 0 files found)`
2. **Case-Insensitive Match for `*operator*.md`:**
   - Command: `find /home/vgpnk/Projects/shokunin/kama-shokunin -iname '*operator*.md'`
   - Exit code: `0`
   - Result: `(empty - 0 files found)`
3. **Full Git Commit History Search:**
   - Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --all --name-only -- '**/operator-*.md' 'operator-*.md'`
   - Exit code: `0`
   - Result: `(empty - 0 commits found)`
4. **Corpus Lessons Inventory:**
   - Exactly 17 lesson files exist under `corpus/lessons/`:
     - `probe-mutation-matrix.md`
     - `round-1-citations.md`, `round-1-critic.md`, `round-1-relaunch-freshness.md`, `round-1-safety.md`, `round-1.md`
     - `round-2.md`, `round-4-recensus.md`, `round-5.md`
     - `round-10.md`, `round-10-verifier-spotcheck.md`
     - `round-11.md`, `round-11-verifier-spotcheck.md`
     - `round-12.md`, `round-12-verifier-spotcheck.md`
     - `round-13.md`, `round-13-verifier-spotcheck.md`
   - None are named `operator-*.md`.

### 2.2 Fleet-Level Discovery (`/home/vgpnk/Projects/shokunin`)

At the fleet root, git history search reveals exactly two files matching `operator-*.md`:
1. `.ufo/scopes/shokunin-12h-20261014/operator-demand.md` (commit `cb3c1039`)
2. `.ufo/scopes/souji-mint-20261018/operator-demand.md` (commit `7bf2b1ab`)

Both are campaign/mint demand scoping documents under `.ufo/scopes/`, **not** corpus lesson files (`corpus/lessons/operator-*.md` does not exist at fleet root or lane level).

### 2.3 Binding Operator Directives & Teachings

Key directives extracted from fleet operator demands and prompt addenda:
- **Scope & Configuration Rule:** *"do not change global configs, but do it how it was written"* (`shokunin-12h-20261014:5`). Host services, listeners, routes, and credentials are operator-owned.
- **Safety Boundary:** Never touch operator config, credentials, host services, or a lane with dirty or unpushed work (`souji-mint-20261018:26-27`).
- **No Secret Paths:** No inspection of `~/.config/opencode/opencode.json`, systemd service environments, tokens, private keys, or credentials.
- **Capability Scope:** Replay tool operates on caller-authorized exported files; no acquisition feature, live network calls, or endpoint probes.

**Discovery Outcome:** Formally **empty discovery** for `corpus/lessons/operator-*.md`. No operator lesson file was found or silently ignored.

---

## 3. Newest Verifier D2 Discovery

### 3.1 Verifier Document Identity

The newest non-author verifier artifact in the repository is:
- **Path:** `corpus/lessons/round-13-verifier-spotcheck.md`
- **Commit:** `e1b3d746dbfd2100b61c67b6389217252592460f` (`round-13 verifier spot-check (integrator, hyaku): non-author admit/reject`)
- **Author:** `hyaku closure (non-author integrator, @m_strong)`
- **Reviewed by:** `CloseKamaR13` (2026-10-20 UTC)
- **Status:** `ok`, admitted `true` (C1 calibration verified as improved, score 7 $\to$ 7).

### 3.2 Routed Defect D2 Details

In `round-13-verifier-spotcheck.md:259–267`, under section **## Routed defects and dispositions**:

```markdown
2. **D2 → kama, next steered round: historical count-table clarification.**
   `corpus/lessons/round-12.md:207–214` labels its last column “Source-only
   mismatch count”, but the repointed-manifest row says “not admitted as a
   comparison”. Its committed acceptance receipt records mismatch count **1**
   under a verified source anchor while the outer verdict is
   `manifest_invalid`, exit **2**. Append a named clarification distinguishing
   that count from outer admission; do not rewrite the old lesson or receipt.
   KQ16 already states the distinction correctly. This is status-neutral
   historical presentation debt, not a falsified round-13 C1 or new axis harm.
```

### 3.3 Historical Defect Context & Precedence

1. **The Ambiguity in `corpus/lessons/round-12.md:207–214`:**
   In Round 12's before/after measurements table:
   - Line 213: `| Manifest redirected to committed old truncated copy | 2 / manifest_invalid | not admitted as a comparison |`
   - However, the committed acceptance receipt (`.ufo/waves/round-12/acceptance.json`) recorded:
     `"source_anchor_matches": true, "source_matches": false, "mismatches": 1`
   - The table entry "not admitted as a comparison" characterized the outer gate admission rather than reporting the literal 1-mismatch count under the verified source anchor.
2. **Existing Criterion Precedence (`corpus/QUALITY.md:57–61` KQ16):**
   KQ16 already captured this semantic boundary:
   *"A byte mismatch that co-occurs with a higher-precedence finding exits 2, while the correspondence count still records the mismatch only when the pinned anchor is verified; an unavailable anchor counts zero mismatches."*
3. **Immutability Contract:**
   `corpus/lessons/round-12.md` and `.ufo/waves/round-12/acceptance.json` must NOT be edited in place. The repair must be an appended clarification in the active round's artifacts.

---

## 4. Audit of Unreflected Teachings in Round 14

Static audit of Round 14 artifacts currently in progress:

| Teaching / Defect | Source | Current Round 14 Status | Audit Verdict |
|---|---|---|---|
| **D2 Count-Table Clarification** | `round-13-verifier-spotcheck.md:259–267` | In progress: Assigned to seat `KamaR14.LegacyCount`. Already drafted in `corpus/lessons/round-14.md:28–36` under `## Mistakes` and `### Named historical clarification — round-13 outside D2`. | **Reflected (In-Flight)**: Named clarification explicitly distinguishes outer `manifest_invalid` (exit 2) from source mismatch count 1 under verified anchor, preserving historical files byte-intact. |
| **No Readiness Inferences** | `spec.json`, `served-identity-crosswalk.md:35` | Enforced in `spec.json` contract: `readiness="unknown"`, `scope="offline-captures-not-runtime"`. | **Reflected**: Neither tags/ps digest match nor presence/absence is interpreted as runtime liveness or readiness. |
| **No Timestamps / Expiry Inferences** | `spec.json`, S012 OpenAPI | Enforced in contract; `AttackStaleness` confirms no `time`/`datetime` imports and no wall-clock comparison with `expires_at`. | **Reflected**: Captures are treated as static caller exports without assumed simultaneity. |
| **Exact Name / Alias Matching** | `spec.json`, S011/S012 | Enforced in contract: exact case-sensitive matching; no GGUF basename stripping. | **Reflected**: Matches against exact `name` or `model` fields only. |
| **Remote Origin Precedence** | `spec.json`, S031 | Enforced in contract: nonempty `remote_model` or `remote_host` triggers `remote_inventory` (exit 1) regardless of digest match. | **Reflected**: Prevents remote catalog items from being classified as loaded local models. |
| **Fail Closed on Malformed Inputs** | `spec.json`, KQ17 | Missing models array, missing digest, malformed JSON, or duplicates fail closed as `invalid_input` / `unknown` (exit 2). | **Reflected**: Conservative fail-closed semantics across all inputs. |
| **Zero Live Probes / Network** | Operator demand, `PROVINCE.md` | Feature is purely offline stdlib CLI (`tools/kama-ollama-evidence.py`). | **Reflected**: Zero socket connections, zero network requests. |

---

## 5. Bounded Recommendations to Owners

1. **To `KamaR14.LegacyCount` & `KamaR14.QualityCriterion` (`corpus/lessons/round-14.md`):**
   - Retain the exact wording in `corpus/lessons/round-14.md:34–36`: confirm that `round-12.md:213` recorded source-only mismatch count 1 under a verified source anchor, while outer finding was `manifest_invalid` (exit 2).
   - Ensure `corpus/lessons/round-12.md` remains strictly unmodified (`git diff -- corpus/lessons/round-12.md` must be empty).
2. **To `KamaR14.Classifier` (`tools/kama-ollama-evidence.py`):**
   - Ensure schema output strictly contains: `finding_id`, `verdict_exit`, `expected_model`, `readiness="unknown"`, `scope="offline-captures-not-runtime"`, and `reasons`.
   - Never import `datetime`, `time`, or call `os.stat` for capture time or timestamp parsing.
3. **To `KamaR14.ReportScribe` (`.ufo/reports/round-14/kama.md`):**
   - Record empty discovery for operator lessons (`corpus/lessons/operator-*.md`).
   - Cite the resolution of round-13 verifier D2 via the appended historical clarification in `corpus/lessons/round-14.md`.

---

## 6. Secret Path & Credential Boundary Compliance

- **No Secret Paths Opened:**
  - Neither `~/.config/opencode/opencode.json` nor systemd private environment files were queried or read.
  - No `.ssh`, `.gnupg`, `.auth`, or token-bearing credential paths were accessed.
- All evidence was gathered via filesystem queries (`find`, `git log`, `read`) targeting public repository documentation, receipts, and source structures.

---

## 7. Limits & Grounding

1. **Static Review Only:** No probes, test suites, selftests, or classifiers were executed by this seat.
2. **In-Flight Artifacts:** `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json` were pending creation at inspection; observations are grounded in the contract specifications, peer reviews, and drafted lesson text.
3. **No Tools Installed:** No tools were installed or upgraded.
