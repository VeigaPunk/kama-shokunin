# ProvinceOverlap — Evidence-Repair Fit vs Protocol Ownership (Kama Round 12)

**Seat:** `KamaR12.ProvinceOverlap` (connector)  
**Assigned Lane:** `kama-shokunin` (`/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Date:** 2026-10-20  
**Role Mandate:** Find one non-obvious move — including a compatible synthesis across the round's proposals — that improves at least one of the round's declared axes without harming another. Stop after one bounded proposal.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/advice/ProvinceOverlap.md`  
**Execution Disclaimer:** Author advisor leaf seat. No verification runs, tests, builds, or host mutations were performed. Unrun != pass. Tools installed/updated: none.

---

## 1. Naming the Axes

Per Godspeed step 1 and `shokunin.conf:52`, the active authority axes are:
- **`calibration` (7, lowest assigned; target $7 \to 7$, $\Delta 0$):** Focus of Round 12 Claim C1. Governs self-assessment accuracy, honest discrepancy reporting, and exact-source frozen evidence correspondence (reducing auxiliary snapshot mismatch $1 \to 0$ against source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`).
- **`operability` (8, assigned; unchanged):** Local model serving discovery and endpoint health. Ports `8080` and `34113` remain unserved (`DEAD`); unit `qwen-coder.service` remains absent. No serving capability acquisition or runtime recovery is claimed.
- **`adjacency` (7, historical; unchanged):** Strict adherence to domain boundaries: "Out of province → report, never absorb" (`PROVINCE.md:50`).
- **`coverage` (9, historical; unchanged):** Retained documentation coverage; no new knowledge domain absorbed.
- **`freshness` (8, historical; unchanged):** Historical probe observations preserved without claiming live endpoint revalidation.
- **`depth` (7, historical; unchanged):** Analytical rigor without ungrounded extrapolation.
- **`quality` (supporting criterion):** Criterion honesty via KQ15.

---

## 2. Evidence from Round Cache & Local Repositories

### 2.1 Kama Province Boundary & Hard Write Limits (`PROVINCE.md:1-53`)
- **Domain:** Local model serving & endpoint health — local LLM endpoints, baseURL drift, served-model reconciliation, probe conventions.
- **Refuses:** Model quality/eval (`kengaku`), credentials & auth flows (`kagi`), dispatch/routing mechanisms (`kumitate`), remote web surfaces (`kake`), and fleet protocol/gate governance (`protocol`).
- **Boundary Invariant:** Kama answers *"is the thing at this baseURL the model this config believes it is, right now"* — never *"is the fleet protocol sound"* or *"is the gate standard adequate for all lanes"*.
- **Out of Province Policy:** *"Anything found outside the domain is named in the round report for the owning lane... report, never absorb"* (`PROVINCE.md:50-53`; `corpus/knowledge/cross-lane-scope.md:44-53`).

### 2.2 Canonical Fleet Ownership of Protocol & Gate Standards (`shokunin.conf:20`, `PROTOCOL.md:375-425`)
- In `/home/vgpnk/Projects/shokunin/shokunin.conf:20`:
  ```text
  protocol|.|fleet-meta: protocol soundness, gate integrity
  aggregator|.|fleet-meta: cross-lane knowledge synthesis, finding router
  kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
  ```
- In `/home/vgpnk/Projects/shokunin/PROTOCOL.md` §Gate standard ("Two evidences", lines 390-399):
  The canonical fleet specification mandates: *"A frozen baseline's expected.json MUST pin the digest of every snapshot input file, and the gate verifies those digests before comparing verdicts: an edited snapshot is snapshot_tampered (could-not-evaluate), not a compared verdict..."*
  `PROTOCOL.md` currently pins **digest integrity against a local manifest**. It does not specify or require a git-object source correspondence check (`git cat-file blob <commit>:<path>`).

### 2.3 Ground Truth Defect D1 Authority (`corpus/lessons/round-11-verifier-spotcheck.md:101-118`)
- The independent non-author closure reviewer (`CloseKamaR11`) uncovered **Auxiliary snapshot defect D1**:
  - Committed git blob at `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md` has SHA-256 `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`.
  - Frozen snapshot `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` has SHA-256 `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` (truncated line 55 with `artifact://1157` marker).
  - The Round 11 runner reported exit 0 and `11 frozen digests verified` because the corrupted snapshot matched the corrupted digest committed in `round-11/frozen/expected.json`.
  - **Closure Finding:** *"A green digest check proves integrity against the shipped expected file, not correspondence with git history."*

### 2.4 The Peer Proposal Landscape in Round 12
- `SkillRegistry.md`: Appends a gate registry row for `fidelity.py` under `SKILL.md` §Round-12 local evidence registry, mapping exits (0 clean, 1 failed, 2 could-not-evaluate).
- `QualityCriterion.md`: Appends `KQ15` to `corpus/QUALITY.md`, requiring byte comparison against `git show <pinned-commit>:<path>` with source correspondence reported separately from digest integrity.
- `ReviewSourcePin.md` & `ReviewGateInterface.md`: Propose rigorous constants, exit precedence, and attack matrices, but also explore abstract gate architectures, finding taxonomy schemas, and generic verification invariants.
- `spec.json:2`: Restricts the scope: *"All work is lane-local historical-evidence repair... One claim C1 CALIBRATION... No scalar increase, capability acquisition, serving readiness or live host claim."*

---

## 3. The Contradiction & Province Tension

A sharp boundary tension exists between the general verification insight uncovered by D1 and the structural ownership boundaries of the fleet:

1. **Systemic Defect vs. Fleet Authority:**  
   Defect D1 revealed a structural loophole in the standard gate pattern: a gate that only verifies `expected.json` digests against disk snapshots is circular if the snapshot was corrupted at generation time. However, Kama does NOT own `PROTOCOL.md` or the fleet-wide Gate standard. Attempting to generalize `fidelity.py` into a fleet-level protocol cutover, or modifying fleet-level protocol specifications, directly violates Kama's province refusal: *"protocol retains protocol soundness and gate integrity"* (`cross-lane-scope.md:44`).
2. **Lane Capability vs. Evidence Tooling:**  
   If `fidelity.py` is registered as a new serving capability in Kama's repertoire table (`SCORECARD.md`), it violates the mandate that repertoire entries remain at 1 (`sources-registry`), improperly inflating `operability`.
3. **Contested Boundary:**  
   Does establishing a two-tier verification standard (git source correspondence separate from digest integrity) constitute a protocol feature cutover? If Kama enacts it as a fleet-wide rule, yes. If Kama implements it strictly as a lane-local gate for historical evidence repair while handing off the finding to the `protocol` lane, no.

---

## 4. The Proposed Move: Decouple & Route

**Implement a strict two-sided partition: bind `fidelity.py` strictly as a lane-local historical evidence repair gate for Claim C1 calibration, while explicitly routing the systemic gate-standard blind spot to the `protocol` lane via a standard adjacency handoff without absorbing it.**

### 4.1 Side A: Lane-Local Evidence Repair (Kama C1 Calibration)
- **Classification:** `fidelity.py` is strictly lane evaluation infrastructure, registered in `SKILL.md` under `SKILL.md` §Gate registry in compliance with the outer interface of `PROTOCOL.md:375-425` (exits 0, 1, 2; `--selftest`; pinned inputs).
- **Scope Restriction:** It governs exactly one historical defect: resolving the auxiliary snapshot mismatch on `corpus/SOURCES.md` from $1 \to 0$ against source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
- **Repertoire Discipline:** `fidelity.py` MUST NOT be added to `SCORECARD.md` §Repertoire capabilities. The capability count remains 1 (`sources-registry`).
- **No Scalar Inflation:** Calibration score remains explicitly $7 \to 7$ ($\Delta 0$). The $1 \to 0$ transition is an evidence delta, not an integer score promotion.

### 4.2 Side B: Adjacency Finding-to-Owner Handoff to `protocol` Lane
In Kama's round report (`.ufo/reports/round-12/kama.md`) and within `corpus/knowledge/cross-lane-scope.md`, file an explicit, non-absorbing handoff packet:

```markdown
- **protocol:** Kama reports: In Round 11 verification, Kama observed that PROTOCOL.md §Gate standard ("Two evidences", lines 390-399) verifies digest integrity against committed expected.json, which proves tamper-resistance of committed files but cannot detect when a frozen snapshot diverged from git history at capture time (demonstrated by D1, where line 55 was truncated to a 768-byte tool-display marker artifact://1157 while reproduce.py reported 11 frozen digests verified). Kama has repaired this locally for its own historical snapshot via fidelity.py and criterion KQ15. Kama does not mutate PROTOCOL.md or export fidelity.py; generalizing source-correspondence requirements into the fleet-wide Gate standard belongs exclusively to protocol.
```

---

## 5. Trace of Second-Order Effects across Surfaces

1. **Contract Surface:**
   - Preserves `PROVINCE.md:50` and `cross-lane-scope.md:44`: Kama reports the endpoint and evidence repair facts, leaving fleet protocol integrity to `protocol`.
   - Protects `SCORECARD.md`: Keeps `capabilities` at 1, `operability` at 8, `calibration` at 7 ($7 \to 7$, $\Delta 0$), and `adjacency` at 7.
   - Prevents rejected submissions at independent closure: No non-author reviewer can reject Kama for unauthorized fleet protocol cutover or claiming a new serving capability.
2. **Runtime Surface:**
   - Unserved serving ports (`8080`, `34113`) remain untouched.
   - Zero writes to host configuration (`~/.config`, `~/.omp`, systemd user units).
   - `fidelity.py` and `reproduce.py` execute without network, daemon, or process binding.
3. **Substrate Surface:**
   - Direct git object inspection (`git cat-file blob <commit>:<path>`) is executed read-only against the repository object database.
   - Subprocess execution strips ambient mutable git environment variables (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_INDEX_FILE`) and sets `GIT_NO_REPLACE_OBJECTS=1` to guarantee tamper-proof raw byte retrieval.
4. **Verification Surface:**
   - Clear division of responsibility: Main L1 verifies the local gate execution via `reproduce.py` and `--selftest`.
   - Fleet verifier verifies committed evidence and confirms that no root protocol files (`PROTOCOL.md`, `MANIFEST.json`, `shokunin.conf`) were modified by Kama.

---

## 6. Risks & Failure Modes

1. **Adjacency Overreach (High):**  
   If Kama's final report or lesson asserts that `PROTOCOL.md` is "defective" or that other lanes "must" adopt `fidelity.py`, closure will sustain an adjacency failure.  
   *Mitigation:* Keep wording strictly descriptive: report the observed D1 phenomenon as local evidence and hand off the general gate question to `protocol`.
2. **Capability Repertoire Pollution (Medium):**  
   If the author records `fidelity.py` in the `capabilities:` table in `SCORECARD.md`, it masquerades as an operability expansion.  
   *Mitigation:* Confirm `SCORECARD.md` retains exactly 1 capability (`sources-registry`).
3. **Circular Trust in Implementation (Medium):**  
   If `fidelity.py` reads the source commit or path from the mutable manifest rather than hardcoded constants, coherent mutation attacks will pass.  
   *Mitigation:* Maintain `SOURCE_COMMIT` and `SOURCE_PATH` as immutable module constants, as recommended by `ReviewSourcePin` and `ReviewGateInterface`.

---

## 7. Verification Checks Named for L1 Main

Per subagent leaf constraints, **no verification commands were executed by this seat**. Upon wave completion, Main L1 should run:

1. **Province & Git Purity Check:**
   ```sh
   git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat origin/kaika/round HEAD
   ```
   *Expectation:* Zero modified files outside `/home/vgpnk/Projects/shokunin/kama-shokunin`. Zero modifications to fleet-level `PROTOCOL.md`, `PROTOCOL-APPENDIX.md`, `MISSION.md`, or `shokunin.conf`.
2. **Capability Table Check:**
   ```sh
   grep -A 5 "capabilities:" /home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md
   ```
   *Expectation:* Exactly 1 capability (`sources-registry`, round 10). `fidelity.py` is NOT listed.
3. **Lane-Local Gate Registry Verification:**
   ```sh
   grep -A 10 "Round-12 local evidence registry" /home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md
   ```
   *Expectation:* Registered as a gate owned by `kama` with entry command `python3 .ufo/waves/round-12/fidelity.py`, verdict map `0 clean / 1 failed / 2 could-not-evaluate`, and `--selftest`.
4. **Adjacency Handoff Check:**
   ```sh
   grep -A 4 "protocol: Kama reports" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/cross-lane-scope.md
   ```
   *Expectation:* Clean handoff text routing the generic two-evidences gate blind spot to `protocol`, without asserting fleet authority.
5. **Gate Execution & Falsification:**
   ```sh
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py --selftest
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/reproduce.py
   ```
   *Expectation:* `--selftest` exits 0 on isolated fixtures; `reproduce.py` outputs clean 0-mismatch verdict on the new snapshot and exit 1 mismatch on the old Round 11 snapshot.
