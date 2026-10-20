# Round 13 — CountLink: Connecting Immutable Commit, Active Suffix, Fixed Denominator & Probe Bounds

**Seat:** `KamaR13.CountLink` (UFO-FSD connector)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Target:** Connect before immutable commit, final current file, two-proposition denominator, historical prefix, and probe limits; prevent counting old intentionally retained false wording as active new defect.  
**Report Path:** `.ufo/waves/round-13/advice/CountLink.md`  
**Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`  
**Boundary:** Leaf connector report only. Read-only static inspection; zero executed builds, tests, linters, formatters, gates, or probe scripts. Tools installed/updated: none.

---

## 1. Named Axes (Godspeed)

1. **calibration (C1 — Primary):** Resolves two routed KQ15 wording discrepancies ($2 \to 0$) on a strictly fixed denominator of 2. Calibration score stays $7 \to 7$ ($\Delta 0$; lowest assigned axis 7 vs operability 8).
2. **operability (Invariant — 8):** Harm none. No runtime, serving, probe, or endpoint code modified or executed.
3. **quality (Invariant / Grounded):** Grounded in Round 12 D4 knowledge-interpretation correction (`served-identity-crosswalk.md:87–134`), not gate machinery.
4. **discernment (Improved):** Grounded in outside spot-check D1 sampling (`round-12-verifier-spotcheck.md:147`) and precise differentiation of stable finding IDs from exit classes.
5. **freshness / coverage / depth / adjacency / expansion (Unchanged):** Textual criterion precision on historical evidence method; zero expansion, no new domain ground.

---

## 2. Evidence (Static & Receipt Grounding)

- **E1 — Immutable Start Commit:** HEAD at Round 13 start is `941bb32c3f591bc63cbf7579b2b6c552228307cd`. At this commit, `corpus/QUALITY.md` contains 49 lines (8619 bytes) ending with KQ15 (`corpus/QUALITY.md:49`).
- **E2 — Routed Proposition 1 Defect in KQ15:** Line 49 asserts: *"mismatch, snapshot tamper and unavailable source each have distinct nonzero exits"*.
  - *Actual Code (`fidelity.py:24–25, 317–319`):* `source_mismatch` emits exit `1`; `snapshot_tampered` and `source_unavailable` emit exit `2`. They share exit 2 (protocol class `could-not-evaluate`). Their distinction is maintained through stable finding IDs, not distinct exit integers.
  - *Registry Concordance (`SKILL.md:396`):* Lists `0 clean; 1 failed (source_mismatch); 2 could-not-evaluate (snapshot_tampered, ..., source_unavailable)`.
- **E3 — Routed Proposition 2 Defect in KQ15:** Line 49 asserts comparison blob is fetched directly as *"git show <pinned-commit>:<source-path>"*.
  - *Actual Code (`fidelity.py:271–273`, `reproduce.py:80`):* Comparator reads historical bytes exclusively via `git cat-file blob <revision>:<path>`.
  - *Provenance Boundary:* Snapshot *capture* was performed via `git show` (`SKILL.md:396`, `lessons/round-12.md:14-15`), while automated *comparison* uses `git cat-file blob` (`fidelity.py:272`).
- **E4 — Mandatory Historical Byte Preservation:** Corpus governance rules (KQ3, KQ7, KQ14, append-only discipline) and outside verifier instructions (`round-12-verifier-spotcheck.md:147`) mandate: *"Append a precise correction; do not rewrite historical criterion/receipt bytes or change valid code solely to fit mistaken wording."* Line 49 must remain byte-identical.
- **E5 — Receipt Evidence:** `.ufo/waves/round-12/acceptance.json` records historical exits: `before` $\to$ exit 1 (`source_mismatch`), `tamper` $\to$ exit 2 (`snapshot_tampered`), `unavailable` $\to$ exit 2 (`source_unavailable`).
- **E6 — Reviewer/Critic Warnings:** `AttackEffective.md` (A1) and `ReviewNoHarm.md` (F3) establish that any whole-file scan for forbidden strings will match line 49 and cause a perpetual false-red failure.

---

## 3. The Core Contradiction & Trap

1. **The Conflict:**
   - Append-only integrity requires that `corpus/QUALITY.md` retain the exact historical bytes of `941bb32...` (lines 1–49). Therefore, the erroneous phrases (`"distinct nonzero exits"` and `git show` comparison) **must permanently exist** in the repository.
   - Conformance checking for the C1 calibration claim requires verifying that the active quality bar no longer asserts these erroneous propositions.
2. **The Danger (False Defect Trap):**
   - If a probe (`measure.py`), a lint script, or a spot-check verifier executes a naive global text check (e.g., `grep -i "distinct nonzero exit" corpus/QUALITY.md`), it will hit line 49 and conclude that the defect persists in the current revision, falsely reporting `missing > 0` or failing the `clean` verdict.
   - If a mutation control introduces `"distinct nonzero exits"` into the active text to test whether the probe detects bad wording, but the probe already matches line 49, the mutation control is tautologically broken.
   - Conversely, if a checker only verifies that the two required literals exist somewhere in the file, it could pass even if KQ16 is malformed, not active, or buried in an inert comment.

---

## 4. Proposed Move (Two-Zone Scoped Counting Protocol)

Synthesizing `AttackEffective` (A1, A4), `AttackTautology` (T1, T2), `ReviewNoHarm` (F3), `ExitFacts`, and `PlannerWalk`, the connector establishes a **Two-Zone Scoped Counting Protocol**:

### Zone 1: Immutable Prefix Invariance (Integrity Tier)
- **Mechanism:** Retrieve historical bytes via `git --no-replace-objects -C <lane> cat-file blob 941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md`.
- **Integrity Assertion:** Assert that `current_bytes[:len(before_bytes)] == before_bytes`.
- **Classification:** Any mutation or deletion in Zone 1 is classified as *historical tampering / prefix corruption* (exit 2 `could-not-evaluate`), not a counted criterion discrepancy.
- **Role of Erroneous Phrases in Zone 1:** The presence of the erroneous wording in line 49 is explicitly recognized as *verified historical integrity*, not an active defect.

### Zone 2: Appended Active Suffix (Conformance Tier)
- **Mechanism:** Scope active evaluation exclusively to the appended suffix `current_bytes[len(before_bytes):]`, isolating the active row matching `^\| *KQ16\b`.
- **Fixed Denominator = 2:** Evaluated strictly within the active KQ16 row:
  1. **Proposition 1 Literal:** `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` MUST be present.
  2. **Proposition 2 Literal:** `capture: git show; comparison: git cat-file blob` MUST be present.
  3. **Active Negative Control:** The erroneous phrasing `"distinct nonzero exits"` (and `git show` as comparison fetch) MUST be strictly absent from the active KQ16 row/cell.
- **Before vs After Accounting:**
  - **`before` (`941bb32`):** Active row was KQ15 (in Zone 1). Lacked Literal 1, lacked Literal 2, contained both erroneous formulations $\to$ **missing count = 2 / 2**, exit 1 (`documentation_mismatch`).
  - **`after` (working tree):** Active row is KQ16 (in Zone 2). Contains Literal 1, contains Literal 2, contains zero erroneous formulations $\to$ **missing count = 0 / 2**, exit 0 (`clean`).
  - **Net Delta:** $2 \to 0$ on fixed denominator 2.

### Zone 2 Mutation Controls in `measure.py`
To avoid false green without polluting Zone 1:
- Mutant 1 (omit exit literal from active KQ16) $\to$ missing count = 1.
- Mutant 2 (omit capture/comparison literal from active KQ16) $\to$ missing count = 1.
- Mutant 3 (reintroduce `"distinct nonzero exits"` into active KQ16) $\to$ active negative check fails $\to$ non-clean / rejection.
- Mutant 4 (tamper with Zone 1 prefix) $\to$ prefix check fails $\to$ exit 2 (`snapshot_tampered`).

---

## 5. Trace Second-Order Effects & Risks

1. **Probe Limits vs. Semantic Proof (KQ14 Boundary):**
   - *Risk:* Treating a 0-missing probe exit as proof that `fidelity.py` or `git cat-file` behaves correctly.
   - *Second-Order Effect:* The probe verifies documentation conformance only. Semantic truth is established separately by static review of `fidelity.py:317-319` and Round 12 receipts. KQ14's human/source review boundary governs.
2. **Finding Precedence Qualifier (Coexisting Findings):**
   - *Risk:* Readers interpreting `source_mismatch=1` unconditionally.
   - *Second-Order Effect:* Per `fidelity.py:55-56, 64-72`, exit 2 findings outrank `source_mismatch`. KQ16 must clarify that `source_mismatch=1` applies when it is the primary finding.
3. **Supersession Referencing (False Red Avoidance):**
   - *Risk:* KQ16 quoting `"distinct nonzero exits"` in its ID cell to describe what it supersedes, triggering the active negative check.
   - *Second-Order Effect:* KQ16 must reference "KQ15's exit-class clause" without quoting the literal phrase verbatim.
4. **Third KQ15 Imprecision (Unpinned Matching Snapshot):**
   - *Risk:* Conflating the unpinned snapshot wording discrepancy with the 2-proposition denominator.
   - *Second-Order Effect:* `ReviewNoHarm` (F1) identified that KQ15's phrase *"may only expose a mismatch"* is imprecise for matching unpinned snapshots (which yield `unpinned` exit 2). This is outside the routed 2-proposition denominator and must remain an explicit open item, not folded into C1.

---

## 6. Verification Checklist (Static Inspection)

To verify the correction without executing lane scripts or gates:
1. `git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file blob 941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md` matches `head -n 49 corpus/QUALITY.md` byte-for-byte.
2. Exactly one row begins with `| KQ16` in `corpus/QUALITY.md`.
3. The KQ16 row contains `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`.
4. The KQ16 row contains `capture: git show; comparison: git cat-file blob`.
5. The KQ16 row does NOT contain `distinct nonzero exit`.
6. Fixed denominator is recorded as 2 ($2 \to 0$, delta 0).
7. Scorecard calibration remains 7 $\to$ 7.
