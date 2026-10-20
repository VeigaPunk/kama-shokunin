# CountsConnection — Round 12 C1 Assessment, Census Analysis & Honest Verdicts

**Seat:** `KamaR12.CountsConnection` (Role: UFO-FSD Connector, author advisor)  
**Assigned Lane:** `kama-shokunin`  
**Date:** 2026-10-20  
**Scope:** Assess C1 ($1 \to 0$ mismatched snapshot, calibration $7 \to 7$, $\Delta 0$), with zero coverage/capability claims. Explain why census updates and new S-row additions do not masquerade as domain expansion. Formulate honest per-axis and trend verdict wording. Synthesize a non-obvious move that improves calibration/quality without harming other axes.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/advice/CountsConnection.md`  
**Execution Constraints:** Leaf member; zero subagent dispatch; static repository review and round cache analysis; zero verification runs, tests, builds, or host mutations (unrun $\ne$ pass); checks named for L1 Main.

---

## 1. Named Axes (Godspeed Framing)

Under the Godspeed directive and `SCORECARD.md` / `AXES.md` contract, the declared axes and learning trends for `kama-shokunin` are:

### 1.1 The Six Domain Axes
1. **operability:** Current score **8** (assigned in fleet `shokunin.conf:52`). Status: unchanged. No runtime unit or probe implementation modified.
2. **calibration:** Current score **7** (assigned in fleet `shokunin.conf:52`). Status: **lowest assigned axis** ($7 < 8$). Contractually mandatory to work under `AXES.md` §Working the axes. C1 works this axis.
3. **freshness:** Historical score **8** (round 10 assessment, not currently assigned in `shokunin.conf`). Status: unchanged. No live host re-census or endpoint polling.
4. **coverage:** Historical score **9** (round 11 assessment). Status: unchanged. No new consumer pin classes or serving engines added.
5. **depth:** Historical score **7** (round 1 assessment). Status: unchanged.
6. **adjacency:** Historical score **7** (round 1 assessment). Status: unchanged. Boundary with other lanes respected.

### 1.2 The Three Learning Trends
1. **expansion:** Movement on the domain frontier (serving runtimes, endpoints, metrics).
2. **quality:** Rigor of admission criteria, falsifiability of negative controls, and evidence provenance.
3. **discernment:** Non-author external gate verification and spot-check agreement.

---

## 2. Assessment of Claim C1: Snapshot Mismatch $1 \to 0$ and Calibration $7 \to 7$ ($\Delta 0$)

### 2.1 The Concrete Physical Defect (D1 Ground Truth)
In Round 11, the closure reviewer (`corpus/lessons/round-11-verifier-spotcheck.md:101-118`) discovered verifier defect **D1**:
- **Declared Source Commit:** `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` at `corpus/SOURCES.md`.
- **Actual Historical Blob:** Git blob OID `7de1360655eadada356fe110813c6e1338142551`, length 18,898 bytes, SHA-256:
  $$\text{SHA-256}(\text{git show } 2f7303c\dots:\text{corpus/SOURCES.md}) = \mathtt{9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a}$$
- **Round-11 Frozen Snapshot:** `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` had SHA-256:
  $$\mathtt{52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1}$$
  Its line 55 was truncated by harness terminal rendering and contained an `artifact://1157` marker.
- **The Blind Spot:** In Round 11, `.ufo/waves/round-11/reproduce.py` checked frozen files against `.ufo/waves/round-11/frozen/expected.json`, which pinned the truncated hash `52665cf...`. The test passed with `frozen_digests_verified: 11` because the runner checked *digest self-consistency*, not *correspondence with git history*.

### 2.2 Claim C1 Definition
- **Baseline (Before):** 1 auxiliary frozen snapshot mismatches the declared immutable source commit (`2f7303c...`).
- **Target (After):** 0 snapshot mismatches. A new corrective snapshot (`.ufo/waves/round-12/frozen/corpus/SOURCES.md`) is captured directly from raw `git show` / `git cat-file blob` bytes, matching the source commit blob `9dc40d25...`.
- **Counting Metric:** Integer count of mismatched frozen snapshots against declared git source history: $1 \to 0$.
- **Counting Command:** `python3 .ufo/waves/round-12/reproduce.py` invoking `fidelity.py`.

### 2.3 Why Score Calibration Stays $7 \to 7$ ($\Delta 0$)
1. **Evidence Repair $\ne$ External Calibration:**  
   Repairing an auxiliary test snapshot is a local historical-evidence correction. It rectifies an internal pipeline artifact truncation. Under `AXES.md` §The six axes, calibration assesses self-assessment accuracy across real-world uncertainty. Repairing a defect caught by outside review demonstrates responsiveness, but does not prove global calibration across all serving domains.
2. **Prevention of Metric Inflation:**  
   Advancing from 7 to 8 on an internal defect fix without an independent, non-author spot-check of the live runtime would violate `QUALITY.md` KQ11, KQ14, and `AXES.md` §SCORECARD.md contract. The score integer remains **7**, with progress documented through direction ("improved") and the verified discrete delta ($1 \to 0$).

### 2.4 Strict Boundary Guarantees (Hard Negatives)
- **Zero Coverage Claim:** Coverage remains **9**. Auxiliary verifier snapshots are test fixtures, not model-serving surfaces. No new engine, port, or consumer pin class was added.
- **Zero Capability Claim:** The `capabilities:` table in `SCORECARD.md` remains strictly at **1** (`sources-registry`, round 10). `fidelity.py` and `reproduce.py` are verification scaffolding, not domain capabilities.
- **Zero Serving Readiness Claim:** The endpoints (`127.0.0.1:34113`, `127.0.0.1:8080`) remain connection-refused (`DEAD`). `qwen-coder.service` remains deleted. No live weights or serving readiness is claimed.

---

## 3. Census Accounting: Why S-Row Addition Does Not Masquerade as Expansion

### 3.1 Current Census Ground Truth
In `corpus/SOURCES.md`, the registry currently contains 31 rows (S001–S031):
- Tiers: A = 28, B = 0, C = 3.
- Statuses: mined = 21, queued = 5, rejected = 5.
- Validation: `scripts/sources-census.sh validate` yields 0 errors, with one known scoped warning `W04 duplicate url docs.ollama.com/api/tags` (for S031's remote-model entry).

### 3.2 The Risk of Masquerading as Expansion
If L1 Main adds row **S032** (planned in `spec.json` and `claims.json` for opened gate evidence):
$$\text{Row S032: kind}=\mathtt{own\text{-}work}, \text{tier}=\mathtt{A}, \text{scope}=\mathtt{fidelity.py\text{ gate evidence}}, \text{status}=\mathtt{mined}$$
The census script will output:
$$\text{Total rows: } 31 \to 32 \quad (\mathtt{A}=29, \mathtt{mined}=22)$$

An undisciplined evaluator might conclude: *"New mined row! Census incremented! Therefore, learning trend expansion is improved."*

**This is a category error and a violation of `QUALITY.md` KQ12.**

### 3.3 Demarcation: Domain Frontier vs. Own-Work Verification Instrument
To prevent census inflation from masquerading as expansion, the lane must enforce an explicit distinction:

| Dimension | Domain Frontier Rows (S001–S029, S031) | Own-Work Verification Rows (S030, S032) |
|---|---|---|
| **Subject Matter** | Upstream engine specifications (llama.cpp, vLLM, SGLang, Ollama, GGUF, OTel, Prometheus). | Lane-local verification commands and gate receipts (`kama-probe.sh`, `fidelity.py`). |
| **Epistemic Role** | Teaches external runtime behavior, endpoint contracts, and model health surfaces. | Records internal execution evidence and reproducibility bounds for lane claims. |
| **Trend Mapping** | Contributes to **expansion** when a new runtime distinction is mined. | Contributes to **quality** (falsifiability) and **calibration** (evidence fidelity). |
| **Round 12 State** | **Zero new domain rows.** (S031 was added in round 11; D2/D4 added prose corrections, not rows). | S032 is internal gate evidence for claim C1. |

### 3.4 Consequence for Round 12 Trend Verdicts
- Under `QUALITY.md` KQ12: *"row or field growth is called new knowledge without a new sourced distinction [REJECT/LIMIT]."*
- Adding S032 records the verifiable execution output of `fidelity.py` (tier A, own-work, scoped to C1 snapshot correspondence).
- Because S032 introduces no new external serving knowledge, **the trend `expansion` MUST be reported as `unchanged`**.
- S032 and the $1 \to 0$ snapshot repair support **`quality: improved`** and **`calibration: improved`**, strictly preventing administrative accounting from masquerading as frontier expansion.

---

## 4. Honest Per-Axis and Trend Verdict Wording

For integration into `SCORECARD.md` and the Round 12 Fleet Report, the following wording is recommended:

### 4.1 Six Domain Axes Verdict Table

| Axis | Verdict | Score | Evidence and Scope Limit |
|---|---|---|---|
| **calibration** | **improved** | **7 $\to$ 7 ($\Delta 0$)** | Repaired auxiliary frozen snapshot correspondence (defect D1) by extracting direct `git show` bytes for `2f7303c...:corpus/SOURCES.md`, eliminating the truncated `artifact://1157` artifact ($1 \to 0$ mismatches). `fidelity.py` and `reproduce.py` enforce independent source correspondence separate from self-consistent manifest digests. D2–D5 prose and pointer errata appended. No scalar advancement to 8 claimed without external non-author review. |
| **operability** | **unchanged** | **8 $\to$ 8 ($\Delta 0$)** | Zero modifications to `tools/kama-probe.sh`, endpoint consumer configurations, or live probe thresholds. Host endpoints remain unserved/dead (`34113`, `8080` connection refused). No live capability claimed. |
| **freshness** | **unchanged** | **8 $\to$ 8 ($\Delta 0$)** | No live endpoint census or host socket polling conducted. Retained snapshot observations remain historical. |
| **coverage** | **unchanged** | **9 $\to$ 9 ($\Delta 0$)** | Domain coverage remains identical (same 3 consumer pin rows, same engine routes). Correcting an auxiliary test snapshot does not expand the domain surface. |
| **depth** | **unchanged** | **7 $\to$ 7 ($\Delta 0$)** | No new p-code, binary disassembly, or low-level runtime engine internals analyzed. |
| **adjacency** | **unchanged** | **7 $\to$ 7 ($\Delta 0$)** | Strict lane boundaries respected (routing left to kumitate, auth to kagi, models to kengaku, web to kake). Lane-local historical repair only. |

### 4.2 Three Learning Trends Verdict Table

| Trend | Verdict | Evidence and Scope Limit |
|---|---|---|
| **expansion** | **unchanged** | Zero new external model serving engines, routes, or domain knowledge surfaces admitted. Census row growth ($31 \to 32$ via S032) represents an internal own-work verification instrument for C1, not domain frontier expansion. |
| **quality** | **improved** | Appended criterion KQ15 to `corpus/QUALITY.md`, establishing that snapshot correspondence with git history must be evaluated independently of manifest digest integrity. Fail-capable controls and coherent-mutation attack verification prevent false passes. Conformance defects D2–D5 addressed via append-only corrections. |
| **discernment** | **unchanged** | All claims and findings are author-advisor assessments within the authoring round. No external, non-author spot-check or closure verification has yet occurred. SHONEN promotion assertions remain four `[~]`, zero `[x]`. |

---

## 5. Non-Obvious Move (Connector Synthesis)

### 5.1 Synthesis Across Round 12 Seat Proposals
A comparative analysis across early round advice files reveals two underlying structural tensions:
1. **Manifest Default vs. Old Snapshot Mismatch (`ReviewGateInterface` F1 & `ReviewSourcePin` F1):**  
   The shared CLI contract states: `Default manifest .../frozen/expected.json` and `Snapshot override without manifest allows observing old mismatch rather than tamper`. If `--snapshot <old_d1_file>` is passed without `--manifest`, but `--manifest` silently defaults to `expected.json`, the CLI will compare the old snapshot hash (`52665cf...`) against the expected new hash (`9dc40d...`), producing `snapshot_tampered` (exit 2) instead of `source_mismatch` (exit 1). This would break the runner's C1 red-before check!
2. **Circular Authority vs. Attack Resistance (`AttackSourceAnchor` A1 & `ReviewSourcePin` F1):**  
   If the manifest specifies `source_commit`, an attacker can mutate both snapshot and manifest to point to a mutated commit, passing both digest and source checks. Source authority MUST reside in hardcoded Python constants (`SOURCE_COMMIT`, `SOURCE_BLOB_SHA256`), not in the manifest.
3. **Census Inflation vs. Provenance Integrity (`AttackSourceCuration` & `QualityCriterion` KQ15):**  
   Adding S032 to cite the gate receipt risks being misinterpreted as domain expansion or circular self-endorsement.

### 5.2 The Proposed Move: Strict Decoupling of Defect Counter from Census Registry with Explicit `--unpinned` Gate Semantics

**Move Formulation:**
1. **CLI Interface Disambiguation:**  
   In `fidelity.py`, implement an explicit `--unpinned` flag (or treat `--manifest ""` / explicit sentinel as unpinned). When `--snapshot` is provided with `--unpinned` (or without `--manifest`), the CLI skips manifest digest validation entirely and performs ONLY the direct Git blob correspondence check against hardcoded constants (`SOURCE_COMMIT = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad"`, `SOURCE_PATH = "corpus/SOURCES.md"`, `SOURCE_BLOB_SHA256 = "9dc40d25..."`).
   - Old snapshot $\to$ exit 1 (`source_mismatch`).
   - New snapshot with default manifest $\to$ exit 0 (`clean`).
   - Coherent snapshot+manifest mutation $\to$ exit 1 (`source_mismatch`, defeated by hardcoded source constants).
2. **Decoupled Claim Counting Metric:**  
   In `SCORECARD.md`, explicitly define the counting metric for C1 as:
   $$\Delta \mathtt{mismatches} = 1 \to 0$$
   measured exclusively by `reproduce.py`. Explicitly bar `scripts/sources-census.sh` from being cited as the counting command for C1.
3. **Two-Tier Census Accounting:**  
   In the Round 12 report, annotate the census count as:
   $$\text{Census Total: } 32 = 30 \text{ (Domain Frontier)} + 2 \text{ (Lane Verification Instruments: S030, S032)}$$
   This permanently insulates the lane against claims of metric gaming while preserving full provenance tracking for the verification receipt.

### 5.3 Second-Order Effects
- **Runtime Surface:** Zero effect. No live server probed or mutated.
- **Contract Surface:** Satisfies `spec.json` and `claims.json` exactly while eliminating CLI parameter ambiguity. Fulfills KQ15 by decoupling digest integrity from source correspondence.
- **Substrate Surface:** Git object database remains the sole, immutable source of truth via raw byte extraction (`git cat-file blob`).
- **Verification Surface:** Guarantees that `reproduce.py` reliably captures exit 1 for the old snapshot and exit 1 for the coherent-mutation attack, ensuring the verification suite is strictly falsifiable.

### 5.4 Risks and Mitigations
- **Risk:** Runner author might expect `--snapshot` alone to be unpinned, while another author expects the default manifest.  
  *Mitigation:* `fidelity.py` should accept both: if `--manifest` is omitted AND `--snapshot` is specified, default to unpinned (emitting finding `unpinned_comparison`), but when `--snapshot` is omitted, default to `.ufo/waves/round-12/frozen/expected.json`.
- **Risk:** S032 addition might be flagged by outside verifier as circular self-endorsement.  
  *Mitigation:* S032 is documented as an `own-work` observational artifact recording the gate receipt, not an external authority endorsing the claim. Claim C1 is grounded in Git commit `2f7303c...`, not in S032.

---

## 6. Verification Checks Named for L1 Main

The following checks should be executed once by L1 Main after integration:

1. **Verify Raw Git Blob SHA-256:**
   ```bash
   git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md | sha256sum
   ```
   *Expected:* `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`
2. **Verify New Corrective Snapshot:**
   ```bash
   sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/frozen/corpus/SOURCES.md
   ```
   *Expected:* Matches `9dc40d25...` exactly.
3. **Run Fidelity Self-Test:**
   ```bash
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py --selftest
   ```
   *Expected:* Exit 0, all synthetic cases (`clean`, `source_mismatch`, `snapshot_tampered`, `source_unavailable`) pass.
4. **Run Reproduction Script:**
   ```bash
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/reproduce.py
   ```
   *Expected:* Exit 0, `ok: true`, capturing before exit 1 (`source_mismatch`), after exit 0 (`clean`), coherent attack exit 1 (`source_mismatch`), and manifest corruption exit 2 (`snapshot_tampered`).
5. **Validate Sources Census Integrity:**
   ```bash
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
   ```
   *Expected:* Exit 0, valid census structure, zero errors.
6. **Verify Immutable Prior Round Evidence:**
   ```bash
   git diff 79fa257719e8688692ed1dc443589331ba22b7fe -- .ufo/waves/round-11/
   ```
   *Expected:* Clean diff (zero edits to Round 11 files).

---
*End of Report — KamaR12.CountsConnection*
