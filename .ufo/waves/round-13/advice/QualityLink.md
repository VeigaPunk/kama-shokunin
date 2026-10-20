# QualityLink — UFO-FSD Connector: Knowledge Interpretation vs. Criterion Bookkeeping

**Seat:** `KamaR13.QualityLink` (Role: UFO-FSD Connector, leaf advisor)  
**Assigned Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Scope:** Static analysis of `corpus/knowledge/served-identity-crosswalk.md` (Round 12 D4 supplement), `corpus/lessons/round-12-verifier-spotcheck.md` (D1 and quality-attribution dispositions), and Round 13 Claim C1 proposals. Synthesize a non-obvious move resolving why stronger knowledge interpretation supported Round 12's quality verdict, but criterion bookkeeping alone in Round 13 cannot support new knowledge quality or expansion.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/advice/QualityLink.md`  
**Execution Constraints:** Leaf seat only; zero subagent dispatch; zero background jobs; read-only static analysis; no builds, tests, linters, formatters, gates, or probe executions; unrun $\ne$ pass; all checks named for L1 Main integration.

---

## 1. Named Axes (Godspeed Framing & Authority)

Under the Godspeed directive and the `SCORECARD.md` / `AXES.md` contract, the declared axes and learning trends for `kama-shokunin` in Round 13 are:

### 1.1 The Six Domain Axes
1. **calibration (current score 7, assigned LIVE axis in `../shokunin.conf:52`):**  
   **Target of Claim C1.** Lowest assigned axis ($7 < \text{operability } 8$). Contractually mandatory to work under `AXES.md` §Working the axes. C1 works this axis by resolving the two routed KQ15 criterion discrepancies in `corpus/QUALITY.md` ($2 \to 0$, fixed denominator 2). Score remains strictly **7 → 7 ($\Delta 0$)**; resolving verifier rule precision debt does not constitute external domain calibration.
2. **operability (current score 8, assigned LIVE axis in `../shokunin.conf:52`):**  
   Status: **unchanged ($\Delta 0$)**. No runtime service, probe implementation (`tools/kama-probe.sh`), or endpoint configuration is touched or executed.
3. **freshness (historical score 8, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. No live host polling, socket sampling, or listener census run.
4. **coverage (historical score 9, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. Zero new consumer pin classes or serving models added.
5. **depth (historical score 7, unassigned):**  
   Status: **unchanged ($\Delta 0$)**.
6. **adjacency (historical score 7, unassigned):**  
   Status: **unchanged ($\Delta 0$)**. Cross-lane boundary respected; orchestrator issue C0 left strictly to protocol owner.

### 1.2 The Three Learning Trends
1. **expansion:**  
   Status: **strictly unchanged**. No new domain frontier ground, covered runtimes, or knowledge entries are admitted.
2. **quality:**  
   Status: **unchanged in Round 13** (prior Round 12 verdict of `improved` grounded retrospectively in D4). Correcting criterion phrasing in `QUALITY.md` is calibration debt, not new domain knowledge quality.
3. **discernment:**  
   Status: **improved** (or unchanged pending independent outside sampling). Non-author outside spot-check defect D1 is faithfully learned without rewriting immutable historical bytes or changing correct code.

---

## 2. Ground Truth Evidence: D4 Knowledge Supplement vs. Outside Quality Attribution

Static review of local repository artifacts establishes the following empirical baseline:

### 2.1 The D4 Supplement in `served-identity-crosswalk.md:87–134`
Author revision: 2026-10-20 UTC (in response to Round 11 verifier spotcheck D4).  
Static observations:
1. **Locality Conclusion is `[INFERENCE]` (`:96–107`):**  
   The statement `"a tags entry does not prove local weights (S031)"` (line 29), Failure Case 6 (`:38`), and the `MODEL_OK` bullet (`:52`) are explicitly classified as analytical deductions (`[INFERENCE]`), not literal text from the Ollama documentation. The documentation (`GET /api/tags`) uses `"locally available"` in summary prose, but its underlying OpenAPI schema for `ModelSummary` provides optional `remote_model` and `remote_host` properties. Because membership can be remote, local weight residency cannot be logically deduced from list membership alone.
2. **Registry Supersession vs. Upstream Stability (`:108–123`):**  
   The phrase `"supersedes S011"` records an internal scope relation within kama's `SOURCES-CONTRACT-v1` registry (S031 narrowing S011's local-residency implication over the same URL). It is explicitly **not** an upstream version change, not a documentation diff between 2026-10-19 and 2026-10-20, and not a retraction of S011's non-status fields (`name`, `digest`, `size`, `details`).
3. **Normative Governance Over Failure Cases (`:124–134`):**  
   The D4 note explicitly governs `## Grounded failure cases`: "Grounded" describes the documented premise (e.g., remote fields exist; S010 signed-in server requirement), while the concluding non-residency claim is an `[INFERENCE]`.

### 2.2 Round 12 Author Quality Attribution Overreach (`corpus/lessons/round-12.md:268–270`)
In Round 12, the author stated:
> `"Author trends: expansion unchanged (zero new covered ground), quality improved (fail-capable exact-source repair and explicit D1–D5 limits)..."`

Here, the author erroneously attributed `quality: improved` to **D1**—the test snapshot repair (`frozen/corpus/SOURCES.md`), manifest pins, and gate machinery (`fidelity.py`).

### 2.3 Outside Verifier Spot-Check Correction (`round-12-verifier-spotcheck.md:120–125, 147–149`)
The independent closure integrator (`CloseKamaR12`, @m_strong) and review seats (`GateCritic`, `AxisReview`) explicitly corrected this attribution:
- **Axis Verdict (`:120–125`):**  
  > `quality: improved. The pre-existing served-identity-crosswalk is strengthened by D4 (:87–134): source wording versus inference and registry versus upstream supersession are now explicitly distinguished, including the failure cases and MODEL_OK restatement. Reopened upstream fields support this correction. This is a stronger retained knowledge interpretation, not renewed runtime freshness. D1's stronger evidence and D2/D3/D5 authority/navigation clarification support it but are not, by themselves, new knowledge entries. AxisReview challenged D1-only quality attribution; this closure grounds the verdict explicitly in the corrected knowledge entry instead of treating gate green as learning.`
- **Routed Disposition Item 3 (`:147–149`):**  
  > `Quality attribution → kama: next round should cite the stronger D4 knowledge-entry interpretation when discussing quality, not present D1 snapshot/gate machinery alone as new knowledge. Existing filed reports/lessons stay immutable; this closure supplies the explicit basis now.`

---

## 3. Epistemic Analysis: Knowledge Interpretation vs. Criterion Bookkeeping

Why does stronger knowledge interpretation support a prior quality verdict, while criterion bookkeeping alone does not support new knowledge quality or expansion?

```
                     ┌────────────────────────────────────────────────────────┐
                     │                 EPISTEMIC LANDSCAPE                     │
                     └────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌───────────────────────────────────┐               ┌───────────────────────────────────┐
│     DOMAIN KNOWLEDGE CORPUS       │               │       META-CRITERIA & GATES       │
│  (`corpus/knowledge/*.md`)        │               │   (`QUALITY.md`, `measure.py`)    │
├───────────────────────────────────┤               ├───────────────────────────────────┤
│ • Interprets model/server reality │               │ • Rules for admitting evidence    │
│ • D4: Ollama remote_model fields, │               │ • KQ16: finding IDs vs exits,     │
│   [INFERENCE] vs documented text, │               │   capture vs comparison commands  │
│   registry vs upstream diff       │               │ • Checks verifier scripts         │
├───────────────────────────────────┤               ├───────────────────────────────────┤
│ IMPACT:                           │               │ IMPACT:                           │
│   Deepens epistemic truth of      │               │   Aligns rubric with tools;       │
│   serving knowledge.              │               │   resolves precision debt.        │
│   ==> TREND: quality: improved    │               │   ==> AXIS: calibration (7->7)    │
│       (Retrospectively in R12)    │               │       TREND: quality: unchanged   │
└───────────────────────────────────┘               └───────────────────────────────────┘
```

### 3.1 Why Stronger Knowledge Interpretation (D4) Supported the Round 12 Quality Verdict
1. **Substantive Epistemic Truth Value:**  
   Quality measures the truthfulness, rigor, and precision of claims in the corpus. In `served-identity-crosswalk.md`, D4 directly modified an active knowledge entry by enforcing two critical epistemic boundaries:
   - *Demarcating Observation from Deduction:* It prevented the corpus from falsely asserting that Ollama documentation explicitly disclaims local residency, accurately labeling it as kama's deduction (`[INFERENCE]`) from OpenAPI schema properties.
   - *Demarcating Registry Scoping from Upstream Reality:* It prevented readers from inferring that Ollama's documentation had changed between 2026-10-19 and 2026-10-20.
2. **Knowledge Refinement without Expansion:**  
   Because the crosswalk already existed (landed as K02 in Round 11), D4 did not expand the domain frontier (`expansion: unchanged`). However, because it directly elevated the semantic integrity of retained knowledge, it legitimately earned `quality: improved`.

### 3.2 Why Criterion Bookkeeping (KQ16 in `QUALITY.md`) Does NOT Support New Knowledge Quality
1. **Meta-Criteria Are Not Domain Knowledge:**  
   `corpus/QUALITY.md` defines admission standards (KQ1–KQ16) for evaluating future evidence. It contains rules *about* knowledge verification, not domain knowledge about served models, endpoints, or runtimes.
2. **Correcting KQ15 Is Calibration Precision Debt:**  
   In Round 13, appending KQ16 corrects two inaccurate formulations in KQ15:
   - Rectifying `"distinct nonzero exits"` to distinct stable finding IDs (`source_mismatch=1; snapshot_tampered=2; source_unavailable=2`) with shared exit 2 for could-not-evaluate states.
   - Rectifying `"blob fetched directly as git show"` to distinguish artifact capture (`git show`) from independent comparison (`git cat-file blob`).
   These edits correct the written description of verification scripts (`fidelity.py`), ensuring that the admission criterion matches the actual code. This is **calibration** (ensuring that our evaluation instruments and standards accurately reflect reality).
3. **Treating Rubric Alignment as Knowledge Quality Repeats Round 12's Defect:**  
   Claiming `quality: improved` in Round 13 for appending KQ16 would repeat the exact category error flagged by `AxisReview`: mistaking verifier bookkeeping for learning. Just as green test fixtures in D1 did not constitute knowledge quality, aligning criterion text with script behavior in KQ16 does not improve domain knowledge quality.

### 3.3 Why Criterion Bookkeeping Does NOT Support Expansion
1. **Zero Domain Ground Advanced:**  
   Expansion assesses movement on the model-serving frontier (e.g., adding vLLM, TensorRT-LLM, new listener endpoints, or context-window tracking).
2. **S033 Is Method Support, Not Domain Expansion:**  
   Adding source row S033 (`git cat-file` manual) increments the census row count ($31 \to 32$), but S033 is scoped strictly to Git object comparison mechanics. Equating verifier tool documentation with domain coverage expansion is a direct violation of `QUALITY.md` KQ12. Therefore, `expansion: unchanged` is mandatory.

---

## 4. Synthesis Across Round 13 Proposals

Examining the wave proposals reveals high alignment, but also a latent risk of metric confusion:
- **`KamaR13.Criterion` (Executor):** Appends KQ16 with exact audit literals `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` and `capture: git show; comparison: git cat-file blob`, preserving all prior KQ15 bytes.
- **`KamaR13.Measure` (Executor):** Implements `measure.py` to verify textual presence of these literals and absence of erroneous phrasing (`"distinct nonzero exits"`, `git show` as comparator).
- **`KamaR13.ExitFacts` & `CaptureFacts` (Scouts):** Ground the exact line numbers in `fidelity.py:271–273, 317–319` and `SKILL.md:396` establishing that finding IDs are distinct while exit 2 is shared, and capture is `git show` while comparator is `git cat-file blob`.
- **`KamaR13.EvidenceScribe` (Scribe):** Identifies in E13–E15 that Round 12 quality attribution must cite D4, not D1 gate machinery.
- **`KamaR13.AttackQuality` (Critic):** Probes whether Round 13 might falsely claim `quality: improved` or `expansion: improved` on the basis of KQ16.

**The Latent Risk / Tension:**  
If the Round 13 report or `SCORECARD.md` states: *"Quality is improved because we cited D4 and appended KQ16"*, it introduces a temporal and categorical contradiction. D4 was landed in Round 12; Round 13 cannot claim credit for Round 12's knowledge edit. Furthermore, KQ16 is calibration debt.

---

## 5. Non-Obvious Move: The Tripartite Quality-Calibration-Expansion Firewall (QCE Firewall)

To resolve this contradiction and improve the rigor of the round without harming any axis, I propose:

### 5.1 The Move
**Formally adopt the Tripartite Quality-Calibration-Expansion Firewall (QCE Firewall) across all Round 13 documentation (`SCORECARD.md`, `LOG.md`, `lessons/round-13.md`, and final report):**

1. **Tier I — Domain Knowledge Quality (Substantive Knowledge Refinement):**  
   - *Scope:* Edits to active entries in `corpus/knowledge/*.md` (e.g., D4 in `served-identity-crosswalk.md`).
   - *Accounting:* Eligible for `quality: improved` **only in the round where authored** (Round 12). In Round 13, D4 is cited exclusively as retrospective historical grounding for Round 12's closed verdict, **not** as a Round 13 quality delta.
2. **Tier II — Meta-Criterion & Verifier Calibration (Rubric Alignment Debt):**  
   - *Scope:* Edits to `corpus/QUALITY.md` (KQ16), verifier code (`measure.py`), or verifier documentation (S032/S033 in `SOURCES.md`).
   - *Accounting:* Credited strictly to **calibration** (Claim C1: 2 $\to$ 0 discrepancies, score 7 $\to$ 7, $\Delta 0$). Trend `quality` remains strictly **unchanged** in Round 13.
3. **Tier III — Domain Frontier Expansion (Repertoire Extension):**  
   - *Scope:* New model-serving endpoints, runtimes, or novel knowledge files covering unmapped domain ground.
   - *Accounting:* Required for `expansion: improved` and `coverage` score advances. Because neither KQ16 nor S033 touches the serving frontier, `expansion` remains strictly **unchanged**.

### 5.2 Why This Improves One Axis Without Harming Another
- **Improves Calibration:**  
  Eliminates category contamination. It guarantees that Round 13's Claim C1 is evaluated purely as calibration precision debt ($2 \to 0$ discrepancies), preventing score inflation and providing watertight audit trails for outside verifiers.
- **Protects Discernment:**  
  Directly satisfies outside closure disposition item 3 (`round-12-verifier-spotcheck.md:147`) by properly framing D4 as the conceptual basis of knowledge quality, while strictly obeying the verifier's injunction against treating gate green or criterion text as learning.
- **Harms Zero Other Axes:**  
  Operability (8), freshness (8), coverage (9), depth (7), and adjacency (7) remain untouched. No code or service is executed.

---

## 6. Second-Order Effects Across Surfaces

1. **Runtime Surface:**  
   Zero effect. No daemon, endpoint (`34113`, `8080`), socket, or probe script is contacted or modified.
2. **Contract Surface:**  
   Strictly aligns `SCORECARD.md` with `AXES.md` §Working the axes. It prevents metric drift where advisors conflate criterion fixes with domain capabilities.
3. **Substrate Surface:**  
   Preserves byte-for-byte immutability across `corpus/knowledge/*.md` and historical sections of `corpus/QUALITY.md`. Appends KQ16 cleanly at the tail of `QUALITY.md` without shifting anchors.
4. **Verification Surface:**  
   Clarifies the scope of `measure.py`: it is a read-only textual conformance probe checking the presence of literal audit phrases and the absence of mistaken wording, not a proof of runtime correctness or semantic mastery.

---

## 7. Contradictions, Risks, and Boundary Guarantees

| Issue / Risk | Nature | Mitigation / Boundary Guarantee |
|---|---|---|
| **Retrospective Attribution Slip** | Attempting to claim `quality: improved` in Round 13 because "we cited D4". | Enforce QCE Firewall Tier I: D4 belongs to Round 12 history. Round 13 quality trend is **unchanged**. |
| **S-Row Census Confusion** | S033 addition increments census ($31 \to 32$), tempting an expansion claim. | Enforce QCE Firewall Tier III: S033 is Tier II method support (Git CLI documentation), not Tier III domain coverage. Expansion is strictly **unchanged**. |
| **Probe Tautology** | `measure.py` string matching mistaken for semantic verification. | As flagged by `AttackTautology`, textual presence is bounded conformance only. Semantic validity is grounded in static inspection of `fidelity.py:271–273, 317–319`. |
| **Old Byte Mutation** | Temptation to edit line 49 of `QUALITY.md` to fix KQ15 in place. | Strictly prohibited by contract. KQ16 is appended after line 49; line 49 remains byte-intact. |

---

## 8. Static Verification Checks for L1 Main

L1 Main should run the following static checks prior to final integration (no subagent execution; unrun $\ne$ pass):

1. **`corpus/QUALITY.md` Append Check:**  
   Verify that line 49 (KQ15) is byte-identical to HEAD (`941bb32`), and that KQ16 is appended with exact literal phrases:
   - `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
   - `capture: git show; comparison: git cat-file blob`
2. **`SCORECARD.md` Trend Verdicts:**  
   Confirm that Round 13 records:
   - `calibration 7 -> 7, delta 0` (Claim C1: 2 discrepancies $\to$ 0)
   - `expansion: unchanged`
   - `quality: unchanged` (with retrospective note crediting Round 12 quality to D4)
   - `discernment: improved` (or unchanged pending outside spot-check)
3. **Immutability of `corpus/knowledge/`:**  
   Verify that `git diff HEAD -- corpus/knowledge/` is completely empty.
4. **Probe Execution (L1 Integration Measurement Only):**  
   Once integrated, L1 runs `python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md` to confirm discrete before=2 / after=0 missing-assertion counts.

---

Report: write your scoped findings to .ufo/waves/round-13/advice/QualityLink.md
