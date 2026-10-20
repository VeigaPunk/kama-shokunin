# SiblingOverlap — UFO-FSD Connector: C1 Province Mapping, Sibling Boundaries & Tri-Boundary Calibration Fence

**Seat:** `KamaR13.SiblingOverlap` (Role: UFO-FSD Connector, leaf advisor)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Target:** Map C1 against lane PROVINCE and sibling boundary names: no fleet protocol ownership, Git-method domain support is bounded calibration not expanding province. Identify C0 orchestrator item and leave to owner.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/advice/SiblingOverlap.md`  
**Execution Boundary:** Leaf member only; zero subagent dispatch; zero background jobs; read-only static analysis apart from this advice report; no builds, tests, linters, formatters, gates, or probe executions (unrun $\neq$ pass); all verification checks named for L1 Main integration.

---

## 1. Named Axes (Godspeed Framing)

Under the Godspeed directive and the canonical `SCORECARD.md` / `AXES.md` contract for `kama-shokunin`:

### 1.1 The Six Domain Axes
1. **calibration (current score 7, assigned LIVE axis in `../shokunin.conf:52`):**  
   **Target of Claim C1.** Lowest assigned axis ($7 < \text{operability } 8$); contractually mandatory focus under `AXES.md` §Working the axes. C1 works this axis by resolving the two routed KQ15 criterion discrepancies in `corpus/QUALITY.md:49` ($2 \to 0$ across the fixed denominator of two propositions: finding IDs vs exit classes, and capture vs comparison mechanics). Score remains strictly **7 → 7 ($\Delta 0$)**; resolving documentation precision debt does not constitute external domain calibration.
2. **operability (current score 8, assigned LIVE axis in `../shokunin.conf:52`):**  
   Status: **unchanged ($\Delta 0$)**. No endpoint probe (`tools/kama-probe.sh`), serving unit (`qwen-coder.service`), consumer registry (`endpoint-consumers.tsv`), or runtime daemon is modified or executed.
3. **freshness (historical score 8, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. No live host polling, socket enumeration, or listener census run.
4. **coverage (historical score 9, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. Zero new consumer pin classes or serving models added.
5. **depth (historical score 7, unassigned):**  
   Status: **unchanged ($\Delta 0$)**.
6. **adjacency (historical score 7, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. Province boundaries with all sibling lanes and the fleet orchestrator are strictly respected; no cross-domain bleed; out-of-province issues handed off.

### 1.2 The Three Learning Trends
1. **expansion:**  
   Status: **strictly unchanged**. Accession of S033 (Git `cat-file` manual) documents verification method plumbing; it adds zero covered domain ground, model endpoints, or serving capability.
2. **quality:**  
   Status: **unchanged in Round 13**. Prior Round 12 verdict of `improved` was grounded retrospectively in D4 (`served-identity-crosswalk.md:87–134`), which demarcated documented upstream fields (`remote_model`, `remote_host`) from local residency inferences. Quality trend must **never** credit gate machinery or criterion bookkeeping.
3. **discernment:**  
   Status: **improved** (or unchanged pending independent outside sampling). Non-author outside spot-check defect D1 is faithfully learned without rewriting immutable historical bytes or changing correct code.

---

## 2. Ground Evidence: Province Mapping, Sibling Boundaries & C0 Handoff

Static inspection of `PROVINCE.md`, `SKILL.md`, `corpus/knowledge/cross-lane-scope.md`, `PROTOCOL.md`, and `corpus/lessons/round-12-verifier-spotcheck.md` establishes the structural boundaries of Claim C1:

### 2.1 Lane PROVINCE and Write Boundary
`PROVINCE.md:3–16, 41–52` defines kama's inviolable domain boundary:
- **Domain:** Local model serving & endpoint health — local LLM endpoints, baseURL drift, served-model reconciliation, probe conventions (`tools/kama-probe.sh`).
- **Core Question:** Answers exclusively: *"is the thing at this baseURL the model this config believes it is, right now"* — never *"is the model good"* or *"is the request safe"*.
- **Hard Write Boundary:** Confined strictly to `/home/vgpnk/Projects/shokunin/kama-shokunin/` (and the declared round report path). Kama never writes to `~/.config`, `~/.omp`, systemd units, or fleet-level assets.
- **Out of Province Policy:** *"Out of province $\to$ report, never absorb. Anything found outside the domain is named in the round report for the owning lane."* (`PROVINCE.md:51–52`).

### 2.2 Sibling Boundary Disambiguation
`corpus/knowledge/cross-lane-scope.md:10–52` and `PROVINCE.md:41–44` establish the non-overlapping boundaries with sibling domains:
- **`protocol` (fleet protocol owner):** Owns `PROTOCOL.md`, `PROTOCOL-APPENDIX.md`, fleet-wide gate standards, and closure consequences. Kama holds **zero fleet protocol ownership**.
- **`orchestrator` / `L0` / `operator`:** Owns task scheduling, driver scripts (`scripts/shokunin-closure.sh`, `scripts/shokunin-watchdog.sh`), prompt template generation, host credentials, systemd lifecycle, and fleet git push/commit orchestration.
- **`kengaku`:** Model quality/evaluation, benchmark task batteries, scoring, and output evaluation.
- **`kagi`:** Secret material, credential hygiene, authentication flows, and token redaction.
- **`kumitate`:** Route-selection mechanisms, model-role dispatch maps, and cascade proxies.
- **`kotoba`:** Instruction surfaces, prompt text, and agent definitions (`janitor.md`, `distiller.md`).
- **`kake`:** Remote web endpoints and public network properties.
- **`kasegi`:** Bounty targets and security vulnerability scope research.
- **`aggregator`:** Cross-lane scope arbitration, routed-defect queue, and corpus reviews.

### 2.3 Git-Method Domain Support is Bounded Calibration, NOT Expanding Province
- **Observation:** In Round 12 and Round 13, kama accessed Git documentation: S032 (`git-show` manual, opened in Round 12) and S033 (`git-cat-file` manual, opened in Round 13).
- **Province Risk:** If citing Git CLI manuals is framed as acquiring Git tooling capability, source control governance, or generalized file verification, kama would be improperly expanding its province into developer tooling.
- **Boundary Reality:** S032 and S033 are classified as `docs/A` sources strictly scoped to *auxiliary method support* for historical snapshot evidence correspondence under `PROTOCOL.md` §Gate standard, Two Evidences. S033 §OUTPUT proves that explicit `<type>` (`blob`) emits raw uncompressed object bytes without working-tree smudge filters or textconv transformations.
- **Non-Expansion Guarantee:** Git method support is confined to internal *calibration* of evidence verification. It introduces zero new LLM serving surfaces, zero new endpoint consumers, and zero domain capabilities. Consequently, **expansion remains unchanged ($\Delta 0$)** and **quality remains unchanged ($\Delta 0$)**.

### 2.4 C0 Orchestrator Item: Defect Identification and Handoff to Owner
In `corpus/lessons/round-12-verifier-spotcheck.md:148`, the independent verifier recorded:
> **"2. C0 → orchestrator/protocol owner:** generated closure prompt requests executing a sibling gate despite canonical Gate standard forbidding it. Align the prompt with committed-evidence inspection plus independent claim recount, or obtain a protocol change through its owner. No gate rerun is falsely certified here."

#### Analysis of C0:
1. **The Conflict:** Generated closure prompts (emitted by the driver / closure prompt generator) instructed the closure integrator to execute `python3 .../reproduce.py`. However, canonical `PROTOCOL.md:415` (§Gate standard, Closure consequence) explicitly mandates:
   > *"The integrator verifies a gate's committed evidence (self-test tally, frozen-run verdict, the revision measured); it does not execute a sibling's gate, whose dependencies and write scope are the lane's."*
2. **Province Ownership:** The defect resides in driver prompt generation (`scripts/shokunin-closure.sh` or the fleet-level closure template) and the fleet gate standard in `PROTOCOL.md`. Neither asset is owned by `kama-shokunin`.
3. **Action Required by Kama:** **Leave strictly to owner.** Kama must not edit fleet closure scripts, modify `PROTOCOL.md`, execute sibling gates, or attempt to absorb the orchestrator's verification duty. Kama's duty is fulfilled by identifying the boundary, reporting the handoff, and ensuring its own internal artifacts (`measure.py`, `fidelity.py`) do not mandate external execution or violate local-first read-only invariants.

---

## 3. Cross-Proposal Omission & Contradiction Audit (Round Cache)

Synthesizing findings across peer advisory reports exposes five critical second-order tensions:

1. **Bare Exit Map vs. Deterministic Precedence (`ExitFacts`, `ReceiptFacts`, `ReviewExit`, `AttackTautology` T2):**
   - The required literal `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` accurately captures the exits of these individual finding IDs when primary.
   - *Contradiction:* In `fidelity.py:65–73, 317–319`, exit codes are tri-state and precedence-ordered (`PRIORITY`). `snapshot_tampered` (priority 3) and `source_unavailable` (priority 4) outrank `source_mismatch` (priority 5). If a snapshot has corrupted manifest pins *and* differing bytes, the gate exits 2 with `finding=snapshot_tampered`, not 1. Stating the exit map without precedence qualification creates a semantic inaccuracy.
2. **Tautological Green vs. Empirical Measurement (`AttackTautology` T1):**
   - The two audit phrases (`source_mismatch=1; snapshot_tampered=2; source_unavailable=2` and `capture: git show; comparison: git cat-file blob`) were coined in Round 13.
   - *Contradiction:* Start commit `941bb32` has no KQ16 row and lacks both phrases. Therefore, measuring missing phrases moving $2 \to 0$ is guaranteed by construction. It measures textual adoption, not empirical discovery. The denominator of 2 must be credited to verifier defect D1, and the probe must be labeled a conformance check, not semantic proof.
3. **Historical Byte Immutability vs. Global Regex Sweeps (`AttackEffective` A1, A6; `ReviewPreservation`):**
   - In `corpus/QUALITY.md:49`, line 49 contains the historical wording *"mismatch, snapshot tamper and unavailable source each have distinct nonzero exits"*.
   - *Contradiction:* Because `QUALITY.md` is strictly append-only (KQ3, KQ7, KQ14), line 49 must remain byte-identical. If `measure.py` executes an unanchored global search forbidding "distinct nonzero exits", it will fail permanently on historical text. Furthermore, if KQ16 quotes that phrase to name its supersession, a row-level check will fail. The probe must inspect only the appended KQ16 row, and KQ16 must refer to "KQ15's exit-class clause" without quoting the erroneous phrase verbatim.
4. **Procedural Diversity vs. External Statistical Independence (`ReviewMethods`, `SourceCat`, `SourceShow`):**
   - S032 (`git show`) and S033 (`git cat-file blob`) both read from the same `.git/objects/` store using the same host `git` binary.
   - *Contradiction:* While `cat-file blob` avoids working-tree filters and textconv transformations (unlike porcelain commands), reading the same git object via two commands on the same host does not constitute external statistical independence. Both commands rely on the same authored commits and the same repository. KQ16 and the round lesson must label this as *operational/procedural diversity*, never as independent external provenance.
5. **The Unaddressed Third KQ15 Imprecision (`ReviewNoHarm` F1):**
   - KQ15 at `corpus/QUALITY.md:49` asserts: *"An overridden snapshot without its manifest may only expose a mismatch, never authorize a pass."*
   - *Contradiction:* In `fidelity.py:238–241, 319`, an unpinned snapshot whose bytes match the historical source emits finding `unpinned` with exit 2 (`could-not-evaluate`), not `source_mismatch` (exit 1). Only byte differences emit `source_mismatch`. Thus, "may only expose a mismatch" is technically inaccurate for the matching case.
   - *Boundary Rule:* This third imprecision is **outside the fixed denominator of 2** established by verifier defect D1. It must not be silently folded into C1. It must be explicitly disclosed as an open residual defect.

---

## 4. The Proposed Move: The Tri-Boundary Calibration Fence

To synthesize the round's proposals without cross-domain bleed or metric inflation, we propose one bounded, non-obvious move: **The Tri-Boundary Calibration Fence**.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         TRI-BOUNDARY CALIBRATION FENCE                           │
└──────────────────────────────────────────────────────────────────────────────────┘
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       ▼                                  ▼                                  ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐
│  1. SUBSTRATE / METHOD TIER  │ │    2. CRITERION TIER         │ │  3. PROBE / FLEET TIER       │
│      (corpus/SOURCES.md)     │ │   (corpus/QUALITY.md: KQ16)  │ │ (.ufo/waves/round-13/measure)│
├──────────────────────────────┤ ├──────────────────────────────┤ ├──────────────────────────────┤
│ • Access S033 (git-cat-file) │ │ • Append KQ16 after line 49  │ │ • Small stdlib textual probe │
│ • S032/S033 = method plumbing│ │ • Literal phrases included:  │ │ • Strictly scoped to KQ16 row│
│ • Disclaim runtime truth &   │ │   - source_mismatch=1; ...   │ │ • Verifies start-hash prefix │
│   external oracle authority  │ │   - capture: ... comparison: │ │ • Reports 2->0 on fixed D1   │
│ • EXPANSION: unchanged (0)   │ │ • Precedence qualified (pri) │ │ • C0 left to orchestrator    │
│ • QUALITY: unchanged (0)     │ │ • Disclose F1 residual debt  │ │ • NO fleet protocol claim    │
└──────────────────────────────┘ └──────────────────────────────┘ └──────────────────────────────┘
```

### 4.1 Specification of the Move

1. **Substrate & Method Boundary (`corpus/SOURCES.md` S033):**
   - Retain S033 as `docs/A` mined source anchored to §OUTPUT ("If `<type>` is specified, the raw... contents... will be returned") and the OPTIONS `--filters`/`--textconv` caveat.
   - Explicitly document that S033 provides *method specification* for byte-preserving object reading, not proof of empirical verification or runtime serving truth.
   - Maintain `expansion: unchanged` and `quality: unchanged`.

2. **Criterion & Semantic Boundary (`corpus/QUALITY.md` KQ16):**
   - Append KQ16 in a new section (`## Criteria added — round 13 (2026-10-20)`) immediately after line 49, preserving the first 49 lines byte-for-byte.
   - Incorporate the exact required audit literals:
     - `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
     - `capture: git show; comparison: git cat-file blob`
   - Synthesize the semantic qualifications:
     - Explicitly state that stable distinct finding IDs share exit 2 for could-not-evaluate conditions, and that `source_mismatch=1` applies only when no higher-priority exit-2 finding (`snapshot_tampered`, `source_unavailable`, `manifest_invalid`) is present.
     - Decouple author-recorded capture provenance (`git show`) from machine-executed comparator plumbing (`git cat-file blob`).
     - Refer to "KQ15's exit-class clause" without repeating the forbidden phrase verbatim in the row.
     - Disclose the third KQ15 imprecision (matching unpinned snapshot returning exit 2 `unpinned` rather than mismatch) as an open residual defect outside the fixed denominator of 2.

3. **Probe & Fleet Governance Boundary (`.ufo/waves/round-13/measure.py`):**
   - Implement `measure.py` strictly as a local, read-only textual conformance probe CLI, **not** as a reusable gate policy or fleet protocol gate.
   - Require `measure.py` to:
     - Verify byte-prefix preservation against start commit `941bb32` (`final.startswith(start)` and line-49 hash check).
     - Parse the Markdown table structure to evaluate assertions strictly inside the active `| KQ16 |` row.
     - Evaluate the fixed denominator of 2 on start commit (2 missing) vs final worktree (0 missing).
     - Run isolated in-memory mutation controls (remove exit literal, remove comparator literal, reintroduce mistaken exit wording in KQ16 row, absent row).
   - Delineate C0: State in probe JSON output and round documentation that sibling gate rerun requests (C0) belong strictly to the orchestrator and protocol owner under `PROTOCOL.md:415`.

---

## 5. Affected Axes and Invariants

| Axis / Trend | Pre-Round Score / State | Post-Round Projected State | Delta | Architectural Impact and Defense |
|---|:---:|:---:|:---:|---|
| **calibration** | **7** | **7** | **0** | **Primary target (Claim C1).** Resolves the two routed KQ15 discrepancies ($2 \to 0$ on fixed denominator 2). Precedence qualified, capture decoupled from comparison, and residual F1 disclosed. No metric inflation. |
| **operability** | **8** | **8** | **0** | **Invariant.** No runtime model serving, probe script (`tools/kama-probe.sh`), or endpoint configuration touched or executed. |
| **freshness** | **8** | **8** | **0** | **Invariant.** Historical score preserved; no live endpoint sampling or host polling performed. |
| **coverage** | **9** | **9** | **0** | **Invariant.** Domain coverage unchanged; S033 is verification plumbing, not consumer or serving model coverage. |
| **depth** | **7** | **7** | **0** | **Invariant.** No new crosswalk or runtime matrix introduced. |
| **adjacency** | **7** | **7** | **0** | **Invariant.** Province boundaries strictly guarded. C0 left to orchestrator; fleet protocol owned by protocol lane; Git plumbing kept within method bounds. |
| *expansion* | *unchanged* | *unchanged* | — | No new covered ground, model endpoints, or serving capability admitted. |
| *quality* | *improved (R12)* | *unchanged (R13)* | — | Retrospective credit for R12 quality remains with D4 knowledge interpretation; R13 criterion bookkeeping adds zero quality delta. |
| *discernment* | *unchanged* | *improved / pending* | — | Outside verifier defect D1 faithfully learned; non-author sampling awaited. |

---

## 6. Risks, Contradictions, and Second-Order Effects

1. **Risk of Tautological Conformance Passing as Semantic Verification:**  
   *Contradiction:* A green exit 0 from `measure.py` proves only that the author typed the required strings into `QUALITY.md`. It does not prove that `fidelity.py` runs correctly or that git historical blobs match.  
   *Mitigation:* KQ14's human/source review boundary governs. The lesson and report must explicitly state that `measure.py` is a regression-prevention conformance probe, not an oracle of runtime truth.
2. **Precedence Inversion Under Mutation Attack:**  
   *Contradiction:* If a corrupted snapshot is evaluated against a corrupt manifest, exit 2 is emitted. If a reader naively assumes any mismatch emits exit 1, they will misinterpret gate results.  
   *Mitigation:* KQ16 explicitly codifies the priority rule (`fidelity.py:65–73`), ensuring the exit map is understood as a conditional primary-finding resolution.
3. **Substrate Coupling vs. Provenance Independence:**  
   *Contradiction:* Citing two Git commands (`show` and `cat-file`) can create the false impression of independent dual-oracle consensus.  
   *Mitigation:* The documentation must explicitly state that both commands read the identical local git object database; the distinction is porcelain rendering vs raw blob extraction, not statistical independence.
4. **Third Imprecision Leakage (F1):**  
   *Contradiction:* Reviewers may notice that unpinned matching snapshots exit 2 (`unpinned`), contradicting KQ15's "may only expose a mismatch".  
   *Mitigation:* Disclose F1 in the round lesson and advice as an acknowledged, open residual defect outside the fixed denominator of two, preventing denominator creep or unvouched claims.

---

## 7. Verification Steps (Named for L1 Main Integration)

In strict accordance with leaf member boundaries, zero verification commands were executed by this seat. The L1 Main integrator should execute the following read-only checks once after integration:

```sh
# 1. Verify byte-prefix preservation of corpus/QUALITY.md (start blob intact)
git cat-file blob 941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md | cmp - <(head -n 49 corpus/QUALITY.md)

# 2. Verify exact presence of the two audit literal phrases in KQ16
grep -F 'source_mismatch=1; snapshot_tampered=2; source_unavailable=2' corpus/QUALITY.md
grep -F 'capture: git show; comparison: git cat-file blob' corpus/QUALITY.md

# 3. Verify absence of the mistaken exit phrase in the appended KQ16 row only
sed -n '/^| *KQ16/p' corpus/QUALITY.md | grep -E 'distinct\s+non-?zero\s+exits' && echo "FAIL: mistaken phrase in KQ16" || echo "OK"

# 4. Verify S033 accession in corpus/SOURCES.md (single row, tier A, 11 cells)
grep -c '^| S033 ' corpus/SOURCES.md
git diff --numstat 941bb32c3f591bc63cbf7579b2b6c552228307cd -- corpus/SOURCES.md

# 5. Execute measure.py textual conformance probe (L1 final run only)
python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md --before-revision 941bb32c3f591bc63cbf7579b2b6c552228307cd
```

---

## 8. Summary of Limits

- **Leaf-only report:** Written by `KamaR13.SiblingOverlap` under read-only constraints.
- **Zero code execution:** No builds, tests, linters, formatters, gates, or probe scripts were executed.
- **Receipt grounding:** All historical execution data cited (e.g., `acceptance.json`) are committed observations from prior rounds, never fresh executions.
- **Unrun $\neq$ Pass:** All verification steps above are recommendations for L1 Main integration.

Report: .ufo/waves/round-13/advice/SiblingOverlap.md
