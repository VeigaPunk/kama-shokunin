# ProvenanceConnection — UFO-FSD Connector Report (Round 11)

**Seat**: `ProvenanceConnection` (UFO-FSD connector; author advisor, not an outside non-author verifier)  
**Round Label**: kama round 11 (2026-10-19 steered label)  
**Review Execution**: `2026-10-20T02:15:35Z` UTC (`date -u`) — all new verification timestamps reflect actual review on 2026-10-20 UTC; historical observation dates and opened fields (2026-10-19) remain unchanged  
**Assigned Scope**: Read-only connection of legacy provenance plan to `SOURCES.md` contract and round-10 KQ7 immutable history rule; explanation of append-only legacy supplements vs. opening header trio for new entries; identification of stale prose in corpus index (`corpus/README.md`) needing appended supersession; synthesis of one non-obvious move across round proposals  
**Tooling Directive Record**: No packages, tools, or dependencies installed or upgraded during this slice. Read-only repo access (`read`, `glob`, `grep`, `bash date -u`). No tests, builds, linters, formatters, or host modifications executed.

---

## 1. Declared Axes and Authority State

Per `SCORECARD.md`, `shokunin.conf:52`, `MISSION.md:29`, and the round-11 spec:

| Axis | Recorded Score / State | Role in Round 11 | Authority Note / Contradiction |
|---|---|---|---|
| **operability** | **8** (round 3 / round 10 errata) | Assigned LIVE axis | Tied with freshness at 8; no probe changes in round 11 |
| **freshness** | **8** (round 10 errata; 50 stale anchors resolved) | Assigned LIVE axis; target of C1 | Worked lowest LIVE tie (C1: 9 legacy files, 27 missing fields → 0) |
| **coverage** | **9** (round 10 errata; 3 sourced entries) | Target of C2 (served identity crosswalk) | Non-LIVE axis; C2 adds `served-identity-crosswalk.md` |
| **depth** | **7** (round 1) | Unchanged | Governed by `SKILL.md` decision tables and checklists |
| **calibration** | **7** (round 1) | Monitored | Reconciles honest provenance dates vs. live revalidation claims |
| **adjacency** | **7** (round 1) | Unchanged | Province boundary preserved: no service start, no routing changes |

**Explicit Contradiction Noted**:  
`shokunin.conf:52` lists `operability + calibration` as kama's owned pair, whereas `MISSION.md:29` and the round-11 spec declare `operability + freshness` as the assigned LIVE axes. Under `AXES.md` "lowest-scoring non-retired axis", calibration (7) is lower than freshness (8). The round-11 wave follows the parent's explicit mission steering (`operability + freshness`, both 8; C1 works the LIVE tie). This contradiction is recorded explicitly without smoothing.

---

## 2. Connection: Legacy Provenance, SOURCES Contract, and KQ7 Immutable History

### A. The Contractual Framework
1. **`SOURCES-CONTRACT-v1`** (`corpus/SOURCES.md:3`): Governs external source admissions. Tiers (A, B, C), status (`mined`, `queued`, `rejected`), scopes, and revision anchors are strictly bound. KQ6 (`corpus/QUALITY.md:28`) mandates that every vendor/spec claim cite an opened, revision-pinned `SOURCES.md` row.
2. **`QUALITY.md` KQ7 (Immutable History & Stale-Anchor Prevention)**:
   > "A correction round publishes a stale-anchor ledger and a pasteable count that reaches 0, with every correction appended at the end of its file. Reject or limit when: Any ledger row stays uncorrected, a dated line is rewritten, or a mid-file insertion shifts other files' line anchors."
3. **`QUALITY.md` KQ3 (Preservation of Old Corpus Bytes)**:
   > "Historical examples have explicit dates/supersession, and active instructions use existing registered surfaces. Corrections preserve old corpus bytes."
4. **`legacy-baseline.json` Prefix Invariant**:
   All 9 legacy knowledge files have their byte lengths and SHA-256 digests pinned. For each file of length $N$, `sha256(current[:N])` must equal `baseline.sha256` (`prefix_violations=0`).

### B. The Structural Conflict and Resolution
If an agent were to prepend the provenance trio (`source:`, `verified-at:`, `recheck:`) at lines 2–4 of the 9 legacy knowledge files (mirroring the round-10 template), two catastrophic contract violations occur immediately:
1. **Prefix Mutation**: The first $N$ bytes are altered, immediately triggering `prefix_violations > 0` in `measure.py` and invalidating `legacy-baseline.json`.
2. **Global Line-Anchor Breakage**: Inserting 3–4 lines at line 2 shifts every subsequent line in that file down by 3–4 lines. Crucially, across the repository, dozens of citations in `corpus/lessons/round-1.md`, `round-1-citations.md`, `round-10.md`, `DELTA.md`, `SCORECARD.md`, `SHONEN.md`, and `corpus/knowledge/consumer-registry.md` cite specific line numbers within these legacy files (e.g. `listener-census.md:45`, `consumer-registry.md:30`, `cross-lane-scope.md:27`). Prepending would instantaneously invalidate these citations across the entire corpus, creating a cascade of stale anchors and directly violating KQ7 ("a mid-file insertion shifts other files' line anchors").

**Conclusion**: Under `SOURCES-CONTRACT-v1`, KQ3, and KQ7, legacy files **must** receive their provenance metadata via an **append-only supplement** at EOF (`## Provenance supplement — round 11 (2026-10-19)`), ensuring $N$ original bytes remain bit-for-bit unchanged and zero existing line anchors shift.

---

## 3. Why Append-Only for Legacy vs. Opening Trio for New Admissions

The corpus bifurcates knowledge files into two distinct categories, each requiring a different provenance placement:

```
+---------------------------------------------------------------------------------------------------+
| LEGACY KNOWLEDGE FILES (9 files, rounds 1–9)                                                      |
| - Purpose: Frozen historical census records of past host state.                                   |
| - Citations: Actively cited by exact line number across repo lessons and registries.              |
| - Baseline: SHA-256 and byte counts pinned in legacy-baseline.json.                               |
| - Provenance Strategy: APPEND-ONLY at EOF.                                                        |
|   * source: none — historical record (or local path:line; NEVER S-rows)                           |
|   * verified-at: observation date vs. review date (2026-10-20 UTC); claims historical             |
|   * recheck: authorized registered surface / none                                                 |
| - Rule Justification: Zero line-anchor shift (KQ7); 100% prefix byte preservation (KQ3).          |
+---------------------------------------------------------------------------------------------------+
| NEW ADMISSIONS (e.g., served-identity-crosswalk.md, round-10 additions)                           |
| - Purpose: Active vendor/specification crosswalk synthesized from opened documentation.           |
| - Citations: Born in this round; zero pre-existing citations or line anchors exist.               |
| - Baseline: None prior to admission.                                                              |
| - Provenance Strategy: OPENING HEADER TRIO (lines 2–4).                                           |
|   * source: S001 ...; S010 ...; S011 ...; S012 ...; S016 ... (must be mined A-tier rows)          |
|   * verified-at: 2026-10-20 UTC — vendor/spec docs opened; no local runtime contacted             |
|   * recheck: on-release / 90d                                                                     |
| - Rule Justification: Gating metadata precedes claim text; consumers & linters evaluate source    |
|   authority upfront under SOURCES-CONTRACT-v1 without scanning to EOF. No legacy to supplement.  |
+---------------------------------------------------------------------------------------------------+
```

### Critical Provenance Distinction for Legacy Files
As identified by `ReviewContract` (finding S1) and `Simplify`:
- The metric for sourced coverage in `SCORECARD.md` is derived from:
  `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l`
- If legacy files in C1 were to invent or cite an external `source: S###` row, this counter would spuriously jump from 3 to 12 without adding any new vendor documentation coverage!
- Furthermore, citing vendor documentation for historical host census data is factually false (violating KQ1 and KQ6).
- Therefore, legacy supplements **must not** cite `S###` rows; they must honestly state `source: none — historical record` (or cite specific local command ledgers/commits).

---

## 4. Stale Prose in Corpus Index (`corpus/README.md`) Needing Appended Supersession

A comprehensive audit of `corpus/README.md` (94 lines total) identifies the following stale prose:

1. **Line 9 (Blanket "Dated Census" Characterization)**:
   - *Existing text*: "Every `knowledge/` and `lessons/` entry is a **dated census record** of what was observed on its citation date — never proof that an endpoint serves today."
   - *Why stale*: In round 10, the corpus expanded beyond host census records to include multi-engine vendor/specification documentation crosswalks (`runtime-health-surface-matrix.md`, `serving-metrics-crosswalk.md`, `gguf-runtime-compatibility-boundary.md`), and round 11 adds `served-identity-crosswalk.md`. These crosswalk entries are governed by public vendor documentation (`SOURCES.md`), not host socket census observations.
   - *Required supersession*: Clarify that legacy entries (rounds 1–9) are dated host census records, while crosswalk entries (rounds 10–11) are vendor-specification crosswalks governed by `SOURCES.md`.

2. **Line 32 (Over-claimed Scope for `served-model-identity.md`)**:
   - *Existing text*: `| knowledge/served-model-identity.md | served-model reconciliation (/v1/models vs --alias vs configured id) + the minimal proof procedure | 1 |`
   - *Why stale*: As established by `ReviewProvenance`, `AttackCoverage`, and `Simplify`, `served-model-identity.md` is an undated 37-line fragment containing only `/health`, `/props`, `/slots`, `/metrics` outputs from one historical llama.cpp instance at `127.0.0.1:34113`. It contains *no* alias reconciliation procedure, *no* multi-engine analysis, and *no* Ollama/vLLM coverage. The actual normalization rule lives in `SKILL.md` §Served-id normalization and `endpoint-identity.md:127`.
   - *Required supersession*: Explicitly note that line 32 over-describes `served-model-identity.md` and that full served-identity reconciliation across engines is provided by the new round-11 `served-identity-crosswalk.md`.

3. **Line 47 (`free-tier-provider-limits.md` Round Range)**:
   - *Existing text*: `| knowledge/free-tier-provider-limits.md | free-tier provider load-test (rounds 6–17): per-round dispatch telemetry, failure classes, concurrency ceilings, inferred-TPS methodology | 6–17 (in progress; loop 1 final) |`
   - *Status*: Corrected by round 10 at line 82 (`*[correction 2026-10-19 (round 10, A50): ...]*`), but line 47 remains frozen.

4. **Lines 73–74 (Frontier Item: Non-Author Spot-Check)**:
   - *Existing text*:
     `- Non-author spot-check of at least one admitted and one rejected candidate; unavailable in round 5, so discernment and promotion remain unverified.`
   - *Why stale*: In round 10, orchestrator-dispatched verifiers (`W3ReviewKama`) conducted an independent non-author spot-check of 1 admitted candidate (the 3 round-10 knowledge entries) and 1 rejected candidate (S030 in-province gate runs), documented in `corpus/lessons/round-10-verifier-spotcheck.md`.
   - *Required supersession*: Declare this Frontier item satisfied and retired by `corpus/lessons/round-10-verifier-spotcheck.md`.

5. **Omission in Coverage Map (Round 10 & Round 11 Entries)**:
   - `corpus/lessons/round-10-verifier-spotcheck.md` is an immutable round-10 artifact present on disk but omitted from the index tables.
   - `corpus/knowledge/served-identity-crosswalk.md` is being added in round 11.

### Mechanism for Index Supersession
Per KQ7, the parent integrator **must not edit lines 9, 32, or 73 in place**. Instead, append at EOF:
```markdown
## Corrections — round 11 (2026-10-19)

*[correction 2026-10-20 UTC (round 11): line 9 is superseded in scope — knowledge/ entries now comprise both dated host census records (rounds 1–9, historical) and revision-pinned vendor documentation crosswalks (rounds 10–11, SOURCES-governed); docs do not establish local runtime integration]*

*[correction 2026-10-20 UTC (round 11): line 32 over-describes served-model-identity.md, which is a 37-line historical fragment of llama.cpp probe outputs; full cross-engine served-identity crosswalk is established in knowledge/served-identity-crosswalk.md]*

*[correction 2026-10-20 UTC (round 11): lines 73–74 Frontier item ("Non-author spot-check... unavailable") is retired — independent non-author spot-check of admitted and rejected candidates was completed in round 10 and recorded in immutable corpus/lessons/round-10-verifier-spotcheck.md]*

## Coverage map — round 11 additions (2026-10-19)

Appended rather than inserted, so no existing line moves (QUALITY.md KQ7).

| Entry | Covers | Round |
|---|---|---|
| `lessons/round-10-verifier-spotcheck.md` | orchestrator non-author spot-check of round-10 admissions (admit: 3 crosswalks; reject: S030 gate runs) | 10 |
| `knowledge/served-identity-crosswalk.md` | served-model identity across engines: availability (/models, /api/tags), loaded models (/v1/models, /api/ps), alias identity, and readiness | 11 |
```

---

## 5. Non-Obvious Move: The Dual-Sourced Lineage Protocol (DSLP)

### A. Synthesis Across Round Proposals
The round's peer reports contain critical findings that could collide if integrated naively:
1. `ReviewContract` (S1) showed that adding `source: S###` to legacy files inflates the coverage counter.
2. `AttackCoverage` (U1–U6) proved that C2 is duplicative if it merely restates `/api/tags` vs `/api/ps`, but achieves genuine expansion by establishing:
   - Ollama `/v1/models` returns available models (unlike llama.cpp `/v1/models` which returns loaded models);
   - llama.cpp `/v1/models` can return `meta: null` while loading (readiness vs. identity conflation);
   - llama.cpp router mode separates `/models` (status) from `/v1/models`;
   - Ollama `/api/tags` includes remote/cloud models (`remote_model`, `remote_host`);
   - `ollama cp` creates alias names without verifying underlying weight digest.
3. `AttackFreshness` (F5) and `ReviewProvenance` discovered that `listener-census.md` ends with `*` and **no trailing newline**, which would fuse an appended heading to the table and break markdown parsing unless preceded by `\n\n`.
4. `ReviewContract` (S2) noted a strict dependency ordering: `served-identity-crosswalk.md` must exist on disk before `SourceCurator` updates `SOURCES.md` S011/S012/S016 from `queued` to `mined`, otherwise `scripts/sources-census.sh validate` fails check E11.
5. `Parent IRC` mandated that actual UTC review date `2026-10-20` be declared in `verified-at`, while retaining steered label `2026-10-19` in headings.

### B. The Move: Dual-Sourced Lineage Protocol (DSLP)
Integrate C1 and C2 as a unified, two-tier lineage architecture:
- **Tier 1 (Legacy Provenance Suffixes)**:
  - Exact append-only supplement at EOF:
    ```markdown

    ## Provenance supplement — round 11 (2026-10-19)
    source: none — historical record (or local path:line; strictly no S### prefix)
    verified-at: original observation <date/undated>; provenance review 2026-10-20 UTC; no live revalidation, no endpoint contacted, endpoint claims historical
    recheck: bash tools/kama-probe.sh check --json (or registered surface; never re-probing deleted units)
    ```
  - For `listener-census.md`, explicitly inject `\n\n` prior to the heading to prevent fusion with the unclosed line.
- **Tier 2 (New Crosswalk Admission & Source Synchronization)**:
  - Phase 1: Write `corpus/knowledge/served-identity-crosswalk.md` with opening header trio (lines 2–4) citing S001, S010, S011, S012, S016; table explicitly incorporates U1–U6.
  - Phase 2: `SourceCurator` updates `SOURCES.md` S011/S012/S016 `status` queued → `mined`, `used-by` → `corpus/knowledge/served-identity-crosswalk.md`; S001/S010 append crosswalk to `used-by`.
  - Phase 3: Parent appends index supersession and coverage map block to `corpus/README.md`.

### C. Affected Axes
- **freshness**: **Improved** — resolves all 27 missing legacy provenance fields to 0 with zero byte prefix mutations; supersedes stale index claims via appended errata without line shifts.
- **coverage**: **Improved** — admits non-duplicative, source-grounded served-identity crosswalk; properly indexes round-10 verifier spotcheck and round-11 crosswalk in `corpus/README.md`.
- **calibration**: **Improved** — prevents coverage counter inflation, eliminates false freshness claims, and honestly disclaims undated historical outputs.
- **operability**: **Unharmed** — all existing probe surfaces, registry resolution, and test fixtures (`test-snapshot.sh`) remain untouched and operational.
- **depth & adjacency**: **Unharmed** — respects province boundary (no service starts, no remote probes).

### D. Risks and Verification
1. **Risk**: `measure.py` fails on missing newline in `listener-census.md`.  
   *Mitigation*: Verify trailing byte of `listener-census.md` before appending; ensure double newline precedes heading.
2. **Risk**: Ordering race where `sources-census.sh validate` runs before `served-identity-crosswalk.md` is written.  
   *Mitigation*: Sequential execution: Crosswalk write → SOURCES edit → validate.
3. **Verification**:
   - `python3 .ufo/waves/round-11/measure.py provenance`: `legacy_files=9, missing_files=0, missing_fields=0, prefix_violations=0`, exit 0.
   - S-row counter check: `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l` yields exactly 4 (3 round-10 + 1 round-11).
   - Census validation: `scripts/sources-census.sh validate` yields `kama ok`, exit 0.
   - Line anchor preservation: `git diff` confirms changes to legacy files occur exclusively after original byte offset $N$.

---

## 6. Integration Recommendations for Parent

1. **Adopt DSLP Execution Order**:
   - Step 1: Land `Legacy1`–`Legacy9` appended supplements (enforcing double newline for `listener-census.md`).
   - Step 2: Land `Crosswalk` creating `corpus/knowledge/served-identity-crosswalk.md`.
   - Step 3: Land `SourceCurator` updating `corpus/SOURCES.md` (queued → mined for S011, S012, S016; update used-by).
   - Step 4: Parent appends Corrections and Coverage map additions to `corpus/README.md` at EOF.
   - Step 5: Parent appends SCORECARD erratum reconciling the planning "18 entries" figure to "9 knowledge files".
2. **Strict S-Row Ban on Legacy Files**:
   Reject any legacy supplement containing `source: S###` to preserve the integrity of the coverage/expansion metric.
3. **Dual-Date Stamp Mandate**:
   Every `verified-at` field must pair its historical observation date (or "undated in file bytes") with the actual review timestamp (`2026-10-20 UTC`) and the explicit caveat: "no live revalidation, no endpoint contacted, endpoint claims historical".
4. **Retire Frontier Item**:
   Formalize the completion of the non-author spot-check frontier item by linking `corpus/lessons/round-10-verifier-spotcheck.md` in the README corrections block.
