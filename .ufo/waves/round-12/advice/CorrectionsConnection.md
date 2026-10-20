# CorrectionsConnection — UFO-FSD Connector: D2–D5 Cross-Document Occurrence & Authority Mapping

**Seat:** `KamaR12.CorrectionsConnection` (UFO-FSD connector, leaf advisor)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Scope:** Static mapping of defects D2–D5 across target surfaces (`SKILL.md`, `SOURCES.md`, `served-identity-crosswalk.md`, `README.md`, `lessons/round-11.md`), distinguishing immutable history from active claim corrections, auditing omissions, and synthesizing one bounded non-obvious move. No verification runs; name checks for L1.

---

## 1. Axes

- **calibration (7 → 7, $\Delta 0$):** Primary assigned axis (lowest assigned vs operability 8). Repairing historical evidence correspondence, anchoring inference boundaries, and eliminating false claims of upstream changes without scalar inflation.
- **operability (8 → 8, $\Delta 0$):** Unchanged. No endpoint, probe command (`tools/kama-probe.sh`), or serving configuration modified.
- **quality (trend: improved):** Rigorous demarcation of empirical observation versus analytical inference; strict separation of digest integrity from source correspondence.
- **discernment (trend: unchanged pending outside sample):** Preservation of non-author outside review boundary (`round-11-verifier-spotcheck.md`); no self-certified promotion.
- **coverage, freshness, depth, adjacency (all $\Delta 0$):** Unaffected.

---

## 2. Occurrence Mapping Across Target Files (D2–D5)

Static analysis traces defects D2–D5 (routed from `corpus/lessons/round-11-verifier-spotcheck.md:213-231`) across the five requested file surfaces:

| Target File | Defect ID | Exact Line Anchor & Text | Status / Category | Resolution Method in Round 12 |
|---|---|---|---|---|
| **`corpus/SOURCES.md`** | **D2** | lines 6–7: `"Every row was opened in round 10 (2026-10-19)..."` | **Immutable historical prelude** | Appended correction note at lines 63–65 after `## Leads (unopened)` clarifying S001–S030 vs S031 (round 11, 2026-10-20) and S032 (round 12). |
| **`corpus/SOURCES.md`** | **D2** | line 48: `"Served identity (next entry, K02) — S016 → S001 → S010 → S011 → S012..."` | **Immutable historical navigation** | Appended correction note at lines 63–65 recording that K02 landed at `corpus/knowledge/served-identity-crosswalk.md`. |
| **`corpus/SOURCES.md`** | **D4** | line 43: `S031` teaches cell: `"supersedes S011 — ... list membership does not prove local residency..."` | **Immutable row cell (parser-critical)** | Appended prose at lines 64–66 explicitly labeling the non-residency conclusion as `[INFERENCE]` and defining `supersedes S011` as lane-registry supersession under `SOURCES-CONTRACT-v1`. |
| **`SKILL.md`** | **D3** | line 357: `"Admission remains corpus/QUALITY.md KQ11–KQ13."` | **Dated round-11 section text** | Appended section `## Round-12 correction — admission criteria pointer (D3, 2026-10-20)` at lines 376–386 establishing that admission requires the full applicable criteria set (KQ1–KQ14 + KQ15). |
| **`SKILL.md`** | **D2, D4** | lines 361–366: references crosswalk, tags/ps split, and S031 remote fields. | **Active expertise surface** | Consistent with D2/D4; already treats crosswalk as landed and distinguishes remote inventory from loaded weights. |
| **`corpus/knowledge/served-identity-crosswalk.md`** | **D4** | lines 1, 84: `"supersedes S011's local-residency implication"` | **Active knowledge entry** | Appended section `## Correction — round 12 D4 (authored 2026-10-20 UTC)` at lines 87–121 explains registry supersession vs upstream stability. |
| **`corpus/knowledge/served-identity-crosswalk.md`** | **D4** | line 29: `"a tags entry does not prove local weights (S031)"`<br>line 38: Failure case 6 under `## Grounded failure cases`<br>lines 52, 63: local residency conclusions | **Active failure analysis** | Appended section at lines 87–121 explicitly classifies these statements as `[INFERENCE]`. |
| **`README.md` (root)** | **None** | lines 1–14: lane pointer and domain boundary. | **Live entrypoint** | No D2–D5 occurrences. |
| **`corpus/README.md`** | **D2, D4** | line 123: `"K02's documented served-identity crosswalk..."`<br>lines 139–144: Round-12 frontier disposition | **Live corpus index** | Fully reconciled by appended round-12 notes (lines 129–144) naming D1, D2, D3, D4 and K02 landed status. |
| **`corpus/lessons/round-11.md`** | **D2, D3, D4, D5** | lines 32, 40–45, 87, 89, 96, 114, 126, 151 | **Immutable round-11 lesson record** | Completely immutable. Records round-11 observations as they occurred (including intermediate KQ11–KQ13 references before KQ14 was added). Must not be rewritten. |
| **`.ufo/round-10/SEAT-PROTOCOL.md`** | **D5** | line 1 (now line 32): `# Round 10 — seat protocol (L1-issued, binding on all 64 seats)` | **Archival undelivered plan** | Prepend override banner at lines 1–31 by `ArchiveDisclaimer` explicitly disclaiming all 64-seat authority while preserving the 4413-byte suffix. |

---

## 3. Boundary Demarcation: Immutable History vs. Active Claim Correction

A central source of ambiguity in Round 12 proposals is the confusion between what constitutes *immutable historical evidence* and what constitutes an *active operational claim*:

1. **Immutable Historical Evidence (Strict Preservation):**
   - **Artifacts:** Prior round reports (`.ufo/reports/`), closure spot-checks (`corpus/lessons/*-verifier-spotcheck.md`), past round lessons (`corpus/lessons/round-11.md`), frozen snapshots (`.ufo/waves/round-11/frozen/**`), and undelivered historical plans (`.ufo/round-10/SEAT-PROTOCOL.md`).
   - **Rule:** Never edit in place. Corrective actions MUST take the form of prepended non-execution banners (for undelivered plans), appended errata sections, or sidecar explanatory notes. Suffix/prefix byte integrity must remain verifiable via `tail` or `cmp`.

2. **Immutable Contract Records with Parser Dependencies (Structural Anchors):**
   - **Artifacts:** `corpus/SOURCES.md` table rows (`S001`–`S031`) and section headers.
   - **Rule:** Rows cannot be edited in place. In particular, `S031` line 43 literally requires `teaches =~ /supersedes S[0-9]{3}/` for `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:648` to grant the `W04` scoped duplicate URL exemption rather than triggering fatal `E04`. Furthermore, mid-file edits shift repository-wide line anchors cited by prior rounds (e.g. `SOURCES.md:6–7`, `:13`, `:23`, `:43`). All D2 and D4 corrections MUST be appended prose after the last lead, preserving the 4-section layout.

3. **Active Knowledge & Operational Guidance (Live Surfaces):**
   - **Artifacts:** `corpus/knowledge/served-identity-crosswalk.md`, `SKILL.md` active gate tables, `corpus/QUALITY.md`.
   - **Rule:** These documents guide active agents and human reasoning. If guidance under an active heading (e.g. `## Grounded failure cases`) contains an un-tagged inference, an appended note alone creates an internal contradiction between the body and the footer. Active operational sections must either carry inline semantic tags or have their section heading explicitly governed by the correction.

---

## 4. Omission Audit & Resolution Receipts

During cross-seat analysis, omissions and boundary tensions were identified, dispatched directly to their respective seat owners via peer messaging, and confirmed resolved:

1. **Reported to & Resolved by `KamaR12.SourceCorrections` (re: `corpus/SOURCES.md:66-71`):**
   - *Issue:* The initial appended D4 prose attributed the quote `"Name of the upstream model, if the model is remote"` to both `remote_model` and `remote_host`.
   - *Resolution:* `SourceCorrections` updated `SOURCES.md:68` and appended closing note `:70-71` clarifying that the quote strictly belongs to `remote_model.description`, while `remote_host.description` separately provides `"URL of the upstream Ollama host, if the model is remote"`.
   - *Crosswalk Line Anchor Shift:* `SourceCorrections` noted that row `S032` was added to the table by L1 accession; `InferenceClarify` safely mitigated line shifting by citing `§Registry row S031` rather than raw line numbers.

2. **Reported to & Resolved by `KamaR12.InferenceClarify` (re: `corpus/knowledge/served-identity-crosswalk.md`):**
   - *Issue:* Failure Case 6 (line 38) resided under `## Grounded failure cases`, while line 90 defined its locality conclusion as `[INFERENCE]`.
   - *Resolution:* `InferenceClarify` appended a normative scope paragraph at `corpus/knowledge/served-identity-crosswalk.md:125-135` establishing that "Grounded" describes each case's documented premise, not every sentence: in case 6 (line 38), the premise is documented while the concluding sentence `"Available inventory is not proof of local weights"` is the governed `[INFERENCE]`. The same applies to the `MODEL_OK` locality restatement at line 52.

3. **Reported to & Confirmed by `KamaR12.SkillRegistry` (re: `SKILL.md:388-403`):**
   - *Confirmation:* Finding IDs and exit maps in the Round 12 local gate row match `fidelity.py` implementation (`clean` 0, `source_mismatch` 1, `snapshot_tampered` 2, `snapshot_unavailable` 2, `manifest_invalid` 2, `source_unavailable` 2, `unpinned` 2, `internal_error` 2).

4. **Reported to & Confirmed by `KamaR12.ArchiveDisclaimer` (re: `.ufo/round-10/SEAT-PROTOCOL.md`):**
   - *Confirmation:* Prepend banner lines 1–31 override the line 32 binding title while preserving the 4413-byte suffix (`tail -c 4413 | sha256sum` = `e9fbaa02...`). Line 24 explicitly notes that tracked sibling templates `round-6` through `round-9` share the same title template and require their own archival labels before reuse.

---

## 5. Non-Obvious Move: The Dual-Anchor Authority Protocol

### The Core Tension Across Proposals
In Round 12, executors faced a sharp contradiction between two inviolable rules:
- *Rule A (Historical Immutability):* Do not edit prior round evidence in place; append-only preserves historical diffs, census regexes, and line anchors.
- *Rule B (Active Semantic Clarity):* Do not allow stale claims, un-tagged inferences, or misleading pointers to masquerade as active truth in live decision documents.

Treating active documents (`served-identity-crosswalk.md`) as immutable history left active headings claiming grounded facts while relegating necessary caveats to an appended tail. Conversely, treating contract registries (`SOURCES.md`) as live editable text risked breaking regex checks (`sources-census.sh` E04) and invalidating hundreds of line citations across historical reports.

### The Proposed Move
**Adopt a Dual-Anchor Governance Model across all kama corpus surfaces:**

1. **For Structural Registries (`corpus/SOURCES.md`):**
   - Enforce the **Lead-Tail Append Standard**: Header text and table rows remain byte-frozen to satisfy `sources-census.sh` and preserve line citations. All scope, date, and navigation errata are placed in an un-numbered prose block at the tail of `## Leads (unopened)`.
   - Reconcile quote precision: Explicitly separate `remote_model` (quoted verbatim) from `remote_host` (schema identifier) in the appended text.

2. **For Active Knowledge Entries (`corpus/knowledge/served-identity-crosswalk.md`):**
   - Enforce **Section-Governing Precedence**: The appended `## Correction — round 12 D4` section must explicitly declare normative precedence over all preceding headings (specifically declaring that item 6 under `## Grounded failure cases` is re-classified as an inferred edge case derived from OpenAPI remote properties).
   - This prevents reader / agent misclassification without requiring in-place line insertions that would disrupt round-11 review citations.

3. **For Archival Artifacts (`.ufo/round-10/SEAT-PROTOCOL.md`):**
   - Retain the L1-approved **Prepend Banner with Suffix Byte Verification**: Suffix bytes remain verifiable via `tail -c 4413`, while first-screen display prevents accidental instruction replay.

### Second-Order Effects
- **Runtime Surface:** Zero impact. No server routes or live models touched.
- **Contract Surface:** Eliminates ambiguity between empirical git history and authored manifests.
- **Substrate Surface:** Leaves `sources-census.sh` awk parsing 100% green (preserves `NF == 13`, table pipe structure, and `/supersedes S[0-9]{3}/`).
- **Verification Surface:** Outside verifier can independently verify historical byte retention via `git show` / `tail -c` and simultaneously verify active semantic consistency.

---

## 6. Risks and Boundaries

1. **Risk of Header Staleness in Sources:** If subsequent rounds append further rows (`S032`, `S033`), the intro sentence (lines 6–7) becomes increasingly dated.  
   *Mitigation:* The appended D2 prose establishes the precedent that the header is a frozen contract prelude for `S001`–`S030`; future rows log their accession exclusively in `## Search log` and `lessons/round-N.md`.
2. **Line Reference Shifts:** Any future editor attempting to clean up `SOURCES.md` by inserting lines in the table will break historical citations across the fleet.  
   *Mitigation:* The Dual-Anchor model strictly prohibits in-place insertions in the table.

---

## 7. Verification Checklist for Main (L1)

1. **Sources Census Conformance:**
   ```sh
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
   ```
   *Expected:* `validate` exits 0 with known warning `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`; `census` exits 0 reporting 31 rows (or 32 if S032 is landed by L1), 0 invalid.

2. **Line Anchor & Byte Integrity Checks:**
   ```sh
   # Verify SEAT-PROTOCOL.md suffix byte retention
   tail -c 4413 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/round-10/SEAT-PROTOCOL.md | sha256sum
   # Expected: e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a

   # Verify SOURCES.md original 62-line prefix retention
   git show 79fa257:corpus/SOURCES.md | cmp -n $(git cat-file -s 79fa257:corpus/SOURCES.md) - /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
   # Expected: exit 0 (original prefix byte-identical)
   ```

3. **Inference Tag Presence in Crosswalk:**
   ```sh
   grep -n "\[INFERENCE\]" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/served-identity-crosswalk.md
   ```
   *Expected:* Matches found in lines 27, 33, 45, and throughout the appended Round-12 D4 section (lines 87–121).

4. **Quality Criteria Hierarchy:**
   ```sh
   grep -n "KQ1[1-5]" /home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md
   ```
   *Expected:* `SKILL.md` line 382 explicitly cites KQ1–KQ14 and KQ15; `QUALITY.md` line 43 defines KQ15.
