# AuthorityRecon — kama Round 12 Authority & Admission Boundary Analysis

**Seat:** `AuthorityRecon` (scout)  
**Assigned Lane:** `kama-shokunin`  
**Date:** 2026-10-20  
**Scope:** Read fleet `shokunin.conf` kama row and `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` current authority. Explain lowest-axis obligation, no scalar movement, and single calibration claim admission boundary. Absolute path evidence, zero live host/endpoint mutations, no verification runs.

---

## 1. Ground Truth Fleet & Lane Authority

### 1.1 Fleet Configuration (`shokunin.conf:52`)
In `/home/vgpnk/Projects/shokunin/shokunin.conf`:
```text
kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
```
- **Assigned Axes:** `operability` + `calibration`.
- **Precedence:** Under `MISSION.md` §Fleet shape, `shokunin.conf` defines the active contract. Historical text in earlier documents referencing `operability + freshness` represents superseded upstream example templates.

### 1.2 Current SCORECARD Authority (`SCORECARD.md:222-245`)
Per `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` §Round 11 authority:
- **operability:** **8** (last changed round 3; gate verified against local llama.cpp / mock surfaces; endpoints currently unserved/dead).
- **calibration:** **7** (historical assessment; tied with depth and adjacency at 7 across all historical axes).
- **freshness:** **8** (historical axis self-assessed in round 10, not an actively assigned axis in `shokunin.conf`).
- **coverage:** **9** (historical axis worked as permitted extension in round 10/11).
- **depth:** **7** (historical).
- **adjacency:** **7** (historical).

---

## 2. Lowest-Axis Obligation Analysis

### 2.1 The Axis Comparison
Between the two actively assigned axes in `shokunin.conf`:
$$\text{calibration (7)} < \text{operability (8)}$$
- Under `AXES.md` §Working the axes: *"At least one claim works the lane's lowest-scoring non-retired axis, except when the stagnation nudge waives it."*
- Neither axis is retired (`SCORECARD.md:57-65`: *"None. Both assigned axes remain active"*).
- The stagnation nudge is inactive: saturation line requires 8/10 on every owned axis, but calibration remains 7/10 (`SCORECARD.md:132-133`).
- **Conclusion:** Working **calibration** is a strict, mandatory contractual obligation for Round 12.

---

## 3. The "No Scalar Movement" Principle ($7 \to 7$, $\Delta 0$)

### 3.1 Why Calibration Remains 7 $\to$ 7
In Round 12, claim C1 specifies:
- `calibration`: $7 \to 7$ (delta 0).
- Counting metric: old auxiliary snapshot mismatch $1 \to 0$ against source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.

### 3.2 Falsifiable Evidence vs. Global Scalar Advancement
1. **Self-Assessment Discipline (`AXES.md` §The six axes):**  
   Calibration measures self-assessment quality: gaps named honestly, overreach caught, and records kept true to repo state.
2. **Local Evidence Repair Is Not Global Promotion:**  
   Repairing historical evidence correspondence (addressing verifier defect D1 from `corpus/lessons/round-11-verifier-spotcheck.md`) corrects an internal provenance defect (truncated snapshot `SOURCES.md` showing `artifact://1157`). It does not demonstrate expanded calibration across all unobserved serving domains or external peer review.
3. **Prevention of Metric Inflation:**  
   As established in Round 11 (`SCORECARD.md:240-244`), counting command outputs (e.g., verifying digests or exit codes) are falsifiable proof that an exact defect was rectified, not a justification to advance a global scalar integer score from 7 to 8. Advancing scalar scores without an external, non-author review would violate `QUALITY.md` KQ11, KQ14, and `AXES.md` §SCORECARD.md contract.

---

## 4. Single Calibration Claim Admission Boundary (C1)

### 4.1 Claim Boundary Definition
- **Claim ID:** C1 (Calibration).
- **Object of Claim:** Exact-source frozen evidence correspondence for `corpus/SOURCES.md` against git commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
- **Defect Addressed:** Verifier spotcheck Defect D1 (`corpus/lessons/round-11-verifier-spotcheck.md:101-110`):
  - Actual commit blob SHA-256: `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`
  - Erroneous Round 11 frozen SHA-256: `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` (truncated with tool display marker `artifact://1157`).
- **Admission Criterion:** Old auxiliary snapshot mismatch decreases $1 \to 0$ using a fresh, exact corrective snapshot extracted via direct `git show` bytes, verified with fail-capable CLI (`fidelity.py`) and reproducible runner (`reproduce.py`).

### 4.2 Prohibited Claims & Hard Negative Boundaries
Under the Round 12 mandate and `PROVINCE.md`:
1. **No Capability Acquisition:**  
   No entry into the `capabilities:` repertoire table. The repertoire table remains at 1 entry (`sources-registry`, round 10). Evidence verification tooling is lane infrastructure, not a domain capability.
2. **No Serving Readiness or Runtime Liveness:**  
   `qwen-coder.service` remains dead/uninstalled on the host. Endpoints (`34113`, `8080`) remain connection-refused (`DEAD`). No assertion of model health, weight residency, or endpoint recovery may be made.
3. **No Live Host Mutation or Out-of-Province Writes:**  
   Zero writes to `~/.config`, `~/.omp`, systemd units, `/etc`, or fleet-level routing/registry directories.
4. **No Historical Rewrites:**  
   Prior round evidence (e.g., `.ufo/waves/round-11/frozen/**`) is immutable. The defect is corrected via new corrective snapshots under `.ufo/waves/round-12/frozen/**` and appended disclaimers/corrections, adhering to `QUALITY.md` KQ7/KQ14.
5. **No Expansion Masquerading as Calibration:**  
   New S-rows (e.g., S032) or census updates are gate-dependent additions owned by L1, not claim expansions for Round 12.

---

## 5. Verification Checks Named for L1 Main

Per subagent leaf policy, this seat executes no test/build/verification commands. L1 Main should run:
1. `git diff --stat origin/kaika/round HEAD` (verify no files edited outside permitted scope).
2. `python3 .ufo/waves/round-12/fidelity.py --selftest` (verify exit 0 and all synthetic negative controls pass).
3. `python3 .ufo/waves/round-12/reproduce.py` (verify clean 0-mismatch result on new snapshot, exit 1 on old snapshot without manifest, and expected exits on mutation controls).
4. `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` (verify census validity).
