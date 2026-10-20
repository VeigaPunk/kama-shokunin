# LegacyCount — Round-14 C1: Historical Count Table Clarification (Defect D2)

Lane: `KamaR14.LegacyCount` (leaf scout). Read-only across lane repository except this report.
No test, build, benchmark, or verifier execution. No tools installed or upgraded.
Historical files (`corpus/lessons/round-12.md`, `.ufo/waves/round-12/acceptance.json`, `corpus/lessons/round-13-verifier-spotcheck.md`) remain byte-identical and unedited.

---

## 1. Axes

1. **Semantic Precision & Class Separation:** Maintain rigid separation between outer gate verdict / exit class (`exit 2`, `finding: "manifest_invalid"`, could-not-evaluate / unadmitted run) and internal subfinding counts under a verified anchor (`mismatches: 1`, `source_correspondence_mismatches: 1`).
2. **Historical Immutability & Append-Only Discipline:** Treat historical lessons, receipts, and verifier records as immutable evidence. Never rewrite historical files; resolve presentation debt strictly via appended clarifications.
3. **Grounded Code & Receipt Truth:** Every claim must be grounded in committed static code (`fidelity.py:64–72, 317–323`) and committed execution receipts (`.ufo/waves/round-12/acceptance.json:368–409`).
4. **Criteria Continuity & Boundary Alignment:** Align historical clarification with KQ14 (semantic-human boundary), KQ16 (finding precedence vs exit mapping), and planned KQ17 (outer verdict vs subfinding count).
5. **Integrator Portability:** Provide an exact, self-contained markdown clarification ready for L1 planner integration into `corpus/lessons/round-14.md` and the fleet report without requiring further revision.

---

## 2. Observed Evidence: Round-12 Table vs Acceptance Receipt

### 2.1 The Round-12 Lesson Table (`corpus/lessons/round-12.md:207–214`)

Under section `## Measured author disposition`:

| Case | Observed exit / finding | Source-only mismatch count |
|---|---|---|
| Old round-11 snapshot, no pin | 1 / `source_mismatch` | 1 |
| New corrective snapshot, committed pin | 0 / `clean` | 0 |
| Coherent changed snapshot + changed manifest | 1 / `source_mismatch` | 1 |
| Pristine snapshot + corrupt manifest pin | 2 / `snapshot_tampered` | 0 |
| **Manifest redirected to committed old truncated copy** | **2 / `manifest_invalid`** | **not admitted as a comparison** |
| Empty source repo | 2 / `source_unavailable` | unavailable, not a successful source comparison |
| CLI selftest | 0 / 11 passed, 0 failed | capability of this evidence gate, not serving capability |

### 2.2 The Committed Acceptance Receipt (`.ufo/waves/round-12/acceptance.json:368–409`)

Record `"repoint"`:
- **Command:** `python3 .../fidelity.py --snapshot .../rs --manifest .../rm --repo .../kama-shokunin`
- **Recorded Outer Exit:** `2`
- **Recorded Primary Finding:** `"manifest_invalid"`
- **Recorded Observed Fields:**
  - `finding`: `"manifest_invalid"`
  - `mismatches`: `1`
  - `source_correspondence_mismatches`: `1`
  - `source_anchor_matches`: `true`
  - `source_matches`: `false`
  - `pinned`: `false`
  - `integrity`: `"not_checked"`
  - `integrity_result`: `"not_checked"`
  - `correspondence`: `"mismatch"`
- **Recorded Findings Array:**
  1. `{"id": "manifest_invalid", "detail": "manifest source_revision 'fe57cc8a01acba9b6d7ed20e11b4914dfb68d903' is not the pinned 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad; a manifest cannot redirect the anchor"}`
  2. `{"id": "source_mismatch", "detail": "snapshot differs from 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md at byte offset 18283 (snapshot 18793 bytes, source 18898 bytes)"}`

### 2.3 Static Implementation Grounding (`.ufo/waves/round-12/fidelity.py`)

1. **Precedence Ranking (`fidelity.py:64–72`):**
   ```python
   PRIORITY = (
       'snapshot_unavailable',
       'manifest_invalid',
       'snapshot_tampered',
       'source_unavailable',
       'source_mismatch',
       'unpinned',
       'clean',
   )
   ```
2. **Primary Finding and Outer Exit Determination (`fidelity.py:317–319`):**
   ```python
   finding = next(fid for fid in PRIORITY
                  if any(item['id'] == fid for item in findings))
   exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)
   ```
   Because `manifest_invalid` ranks higher than `source_mismatch` in `PRIORITY`, `finding` was assigned `"manifest_invalid"`, resulting in outer exit `2`.

3. **Subfinding Mismatch Evaluation (`fidelity.py:320–323`):**
   ```python
   # C1 counts only correspondence failures against a verified anchor. Pin
   # and anchor failures stay visible in integrity_result /
   # snapshot_pin_matches / source_anchor_matches and are not folded in.
   mismatches = int(source_matches is False and anchor_matches is True)
   ```
   In the `repoint` control:
   - The repository resolved `SOURCE_REVISION:SOURCE_PATH` (`2f7303c2...:corpus/SOURCES.md`), and the extracted blob matched the code-pinned OID `7de13606...`, SHA-256 `9dc40d25...`, and length 18,898 bytes (`anchor_matches: true`).
   - The snapshot provided (`/tmp/kama-round12-controls-rh1hrwo8/rs`) was the old round-11 snapshot of 18,793 bytes (`52665cf2...`), which differed from the source blob at byte offset 18,283 (`source_matches: false`).
   - Therefore, `mismatches = int(False is False and True is True) == 1`.
   - The receipt faithfully recorded `mismatches: 1` and `source_correspondence_mismatches: 1`.

---

## 3. Defect D2 Analysis (Presentation Debt)

In `corpus/lessons/round-13-verifier-spotcheck.md:259–267`:
> **D2 → kama, next steered round: historical count-table clarification.**
> `corpus/lessons/round-12.md:207–214` labels its last column “Source-only mismatch count”, but the repointed-manifest row says “not admitted as a comparison”. Its committed acceptance receipt records mismatch count **1** under a verified source anchor while the outer verdict is `manifest_invalid`, exit **2**. Append a named clarification distinguishing that count from outer admission; do not rewrite the old lesson or receipt. KQ16 already states the distinction correctly. This is status-neutral historical presentation debt, not a falsified round-13 C1 or new axis harm.

### The Source of Confusion
The author of `corpus/lessons/round-12.md` conflated two distinct concepts:
1. **Outer admission status:** Because the manifest attempted to redirect the source revision away from the code-pinned anchor, the manifest was rejected (`manifest_invalid`, exit 2). The run was therefore not admitted as a valid pinned verification pass.
2. **Inner subfinding correspondence count:** Because the source anchor itself was present and verified against git history (`anchor_matches: true`), the comparator proceeded to compute byte-by-byte correspondence against the snapshot. The snapshot differed from the authentic blob, evaluating `mismatches = 1`.

By entering `"not admitted as a comparison"` in the column explicitly titled `"Source-only mismatch count"`, the table obscured the evaluated metric (`mismatches: 1`) with the outer gate verdict (`exit 2`, not admitted). In contrast, the `"Empty source repo"` row correctly noted `unavailable, not a successful source comparison` because git rev-parse failed, `anchor_matches` was false/null, and `mismatches` was literally `0`.

KQ16 (`corpus/QUALITY.md:61`) already formalized this:
> "A byte mismatch that co-occurs with a higher-precedence finding exits 2, while the correspondence count still records the mismatch only when the pinned anchor is verified; an unavailable anchor counts zero mismatches."

---

## 4. Exact Appended Clarification Text

The following exact text is prepared for L1 to append to `corpus/lessons/round-14.md` (e.g. under `## Prior outside feedback` or `## Mistakes` / historical clarifications) and for reference in the round-14 fleet report. No historical files are modified.

```markdown
### Historical clarification — Round-12 count table repointed-manifest mismatch count (Defect D2)

In `corpus/lessons/round-12.md:207–214`, the summary table of measured author controls labels its last column “Source-only mismatch count”, and reports the row for the repointed manifest as:
`| Manifest redirected to committed old truncated copy | 2 / manifest_invalid | not admitted as a comparison |`

As noted in `corpus/lessons/round-13-verifier-spotcheck.md` (Defect D2), the committed acceptance receipt (`.ufo/waves/round-12/acceptance.json`, record `"repoint"`) records:
- `exit: 2`
- `finding: "manifest_invalid"`
- `source_anchor_matches: true`
- `source_matches: false`
- `mismatches: 1`
- `source_correspondence_mismatches: 1`

**Clarification:**
1. **Outer verdict precedence:** Under `fidelity.py:64–72, 317–319`, `manifest_invalid` is an exit-2 finding that precedes `source_mismatch` in `PRIORITY`. Because the manifest attempted to redirect `source_revision` away from the code-pinned anchor `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`, the primary finding was `manifest_invalid` and the process exited with code 2. The run was not admitted as an authorized pinned comparison pass.
2. **Inner correspondence count under verified anchor:** Under `fidelity.py:320–323`, `mismatches = int(source_matches is False and anchor_matches is True)`. Because the git repository was available and independently verified the pinned blob OID, SHA-256, and byte length (`anchor_matches: true`), byte correspondence between the provided round-11 snapshot and the authentic source blob was evaluated, detecting the byte difference at offset 18,283 (`source_matches: false`). The tool correctly emitted `mismatches: 1`.
3. **Presentation debt resolved:** The column entry “not admitted as a comparison” described the outer admission disposition of the run, rather than the evaluated `mismatches` count of 1. Historical files (`corpus/lessons/round-12.md` and `.ufo/waves/round-12/acceptance.json`) remain byte-identical and unedited per append-only rules. KQ16 and KQ17 formally preserve the distinction between primary outer exit classification and secondary subfinding counts.
```

---

## 5. Bounded Recommendations to Peers

1. **To `KamaR14.QualityCriterion`:**
   - **Grounding for KQ17:** Ground KQ17 directly in Defect D2 and the outer-verdict vs subfinding-count distinction:
     * Outer verdict and process exit code must reflect the primary finding under strict priority order (fail-closed, exit 2 for unadmitted, malformed, or redirected inputs).
     * Subfinding counts (such as byte mismatches under a verified anchor) evaluate internal correspondence metrics independently and must not be conflated with outer run admission.
     * In the offline Ollama classifier (`tools/kama-ollama-evidence.py`), maintain this same separation: malformed or conflicting inputs fail closed as `unknown` / `invalid_input` (exit 2) or `identity_conflict` (exit 1), while `reasons` list records the specific subfindings without altering the fail-closed exit.
   - *Status:* Bounded message delivered to `agent://KamaR14.QualityCriterion`.

2. **To `KamaR14.ReportScribe`:**
   - Incorporate the D2 clarification into the round-14 report facts under §Prior outside feedback / §Mistakes.
   - Reaffirm that D2 was status-neutral presentation debt that does not invalidate round-12 or round-13 C1 calibration.
   - *Status:* Bounded message delivered to `agent://KamaR14.ReportScribe`.

3. **To `KamaR14.EvidenceScribe`:**
   - Confirm in the final-gate evidence checklist that historical files `corpus/lessons/round-12.md`, `.ufo/waves/round-12/acceptance.json`, and `corpus/lessons/round-13-verifier-spotcheck.md` are verified untouched (byte-identical to start revision).
   - *Status:* Bounded message delivered to `agent://KamaR14.EvidenceScribe`.

---

## 6. Limits

- **Static Observation Only:** Findings are derived entirely from committed static source files (`fidelity.py`), committed JSON receipts (`acceptance.json`), and committed lesson and verifier markdown files.
- **No Verification Execution:** No Python scripts, selftests, reproduction harnesses, or git verification commands were executed during this inspection.
- **No Edits to Old Files:** In accordance with repository rules, no historical files were modified.
- **Tooling Directive:** Zero packages or tools were installed, updated, or removed.
