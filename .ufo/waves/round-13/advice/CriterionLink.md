# CriterionLink — UFO-FSD Connector: KQ14/KQ15 Connection to Proposed KQ16 & Boundary Synthesis

**Seat:** `KamaR13.CriterionLink` (Role: UFO-FSD Connector, leaf advisor)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Scope:** Connect previous round-12 lesson mistakes and outside verifier spot-check defect D1 to the proposed KQ16 criterion update, synthesizing proposals across `Criterion`, `Measure`, `ExitFacts`, `ReceiptFacts`, `ReviewExit`, `ReviewProbe`, `ReviewSkill`, `SourceCat`, and `SourceShow`. Preserve semantic-human (KQ14), manifest-integrity (KQ15), and append-only byte-preservation boundaries without claiming executed checks or inflating scalar scores.  
**Deliverable Path:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/advice/CriterionLink.md`  
**Execution Boundary:** Leaf member only; zero subagent dispatch; static code/receipt analysis only; zero test, build, lint, format, or gate execution (unrun $\neq$ pass); verification checks named for L1 Main.

---

## 1. Named Axes (Godspeed Framing)

Under the Godspeed directive and the canonical `SCORECARD.md` / `AXES.md` contract for `kama-shokunin`:

### 1.1 The Six Domain Axes
1. **calibration (7 → 7, $\Delta 0$):** Primary assigned axis (lowest assigned score 7 vs operability 8; mandated focus under `AXES.md` §Working the axes). Works claim C1: resolving two routed KQ15 criterion discrepancies ($2 \to 0$ across fixed denominator 2: finding IDs vs exit classes, and capture vs comparison mechanics). Score remains integer 7, precluding metric inflation on documentation corrections.
2. **operability (8 → 8, $\Delta 0$):** Unchanged. No endpoint probe (`tools/kama-probe.sh`), serving unit (`qwen-coder.service`), consumer registry (`endpoint-consumers.tsv`), or runtime daemon modified.
3. **freshness (unchanged):** Historical score 7. No live endpoint polling, host re-census, or runtime revalidation performed.
4. **coverage (unchanged):** Historical score 8. Zero new consumer pin classes or serving models added; S033 addition is verification method documentation, not domain expansion.
5. **depth (unchanged):** Historical score 7. No new crosswalk or decision table added.
6. **adjacency (unchanged):** Historical score 7. Province boundaries with kumitate, tsukuroi, and orchestrator respected; fleet protocol and C0 issues left to their owners.

### 1.2 The Three Learning Trends
1. **expansion (unchanged):** S033 source row accession documents Git method plumbing; it adds zero covered domain ground, model endpoints, or serving capability.
2. **quality (trend: improved):** Grounded strictly in Round 12 D4 knowledge interpretation (`corpus/knowledge/served-identity-crosswalk.md:87–134`), which demarcated documented upstream fields (`remote_model`, `remote_host`) from local residency inferences and registry supersession. Quality trend must **never** credit gate machinery or criterion bookkeeping.
3. **discernment (trend: unchanged pending outside sample):** Internal author-wave proposals are not independent outside review; promotion boxes remain uncertified author assertions until a non-author spot-check evaluates Round 13.

---

## 2. Evidence Synthesis: Connecting Round-12 Mistakes to KQ16

Static analysis of Round 12 artifacts (`fidelity.py`, `reproduce.py`, `acceptance.json`, `corpus/lessons/round-12.md`) and the outside spot-check (`corpus/lessons/round-12-verifier-spotcheck.md:144–149`) grounds the exact two routed propositions:

| # | Topic | KQ15 Formulation (`corpus/QUALITY.md:49`) | Code & Receipt Ground Truth | KQ16 Literal Requirement & Scope |
|---|---|---|---|---|
| **P1** | **Exit Classes vs. Finding IDs** | `"...mismatch, snapshot tamper and unavailable source each have distinct nonzero exits."` | `fidelity.py:317–319` and `SKILL.md:395–397`: Tri-state exit mapping.<br>• Exit 0 = `clean`<br>• Exit 1 = `source_mismatch` (protocol class `failed`)<br>• Exit 2 = shared `could-not-evaluate` class (`snapshot_tampered`, `source_unavailable`, `manifest_invalid`, `snapshot_unavailable`, `unpinned`, `internal_error`).<br>Historical receipt `acceptance.json` confirms: `before` exits 1 (`source_mismatch`); `tamper` exits 2 (`snapshot_tampered`); `unavailable` exits 2 (`source_unavailable`). Finding IDs are distinct and stable; exit classes are shared. | Exact literal phrase:<br>`source_mismatch=1; snapshot_tampered=2; source_unavailable=2`<br>Must explain stable distinct finding IDs with shared exit 2 for could-not-evaluate conditions. |
| **P2** | **Capture vs. Comparison Mechanics** | `"A frozen historical copy is compared byte-for-byte with the blob fetched directly as git show <pinned-commit>:<source-path>..."` | `fidelity.py:271–274` and `reproduce.py:80`: Programmatic verification retrieves the historical blob via `git cat-file blob <pinned-commit>:<source-path>`.<br>`corpus/lessons/round-12.md:14–15` and `advice/Fidelity.md:26–40`: Initial snapshot creation was captured via `git show <pinned-commit>:<source-path>`.<br>Official documentation decouples the two: S032 (`git-show` manual §DESCRIPTION: "For plain blobs, it shows the plain contents") documents capture; S033 (`git-cat-file` manual §OUTPUT: "If &lt;type&gt; is specified, the raw... contents... will be returned") documents comparison. | Exact literal phrase:<br>`capture: git show; comparison: git cat-file blob`<br>Must decouple the author capture method from the gate comparator plumbing. |

---

## 3. Preservation of Inviolable Architectural Boundaries

In synthesizing the transition from KQ15 to KQ16, three inviolable boundaries must be preserved intact:

### 3.1 The Semantic-Human Boundary (KQ14 Governance)
- **Rule (`corpus/QUALITY.md:41`):** "A zero uncorrected count or in-bounds pointer alone proves the old claim true; shape-only `test -e`/`wc -l` is used to infer file-body pin presence or absence... human/source review establishes the claim's content."
- **Application to Round 13:** The `measure.py` probe verifies *textual documentation conformance* (the syntactic presence of audit literals and absence of mistaken phrases). It does **not** constitute semantic proof of code behavior or runtime truth. Code correctness and exit mappings remain grounded in static code review of `fidelity.py` and committed historical receipts (`acceptance.json`). KQ16 must explicitly reiterate that KQ14 governs.

### 3.2 The Manifest-Integrity Boundary (KQ15 Substantive Core)
- **Rule (`corpus/QUALITY.md:49`):** Source correspondence is reported separately from SHA-256 digest integrity against a pinned manifest; clean requires both; an overridden snapshot without a manifest cannot authorize a pass; coherent snapshot+manifest edits still fail source correspondence; corrections append a new dated snapshot plus manifest leaving old receipts byte-intact.
- **Application to Round 13:** KQ16 supersedes **only** the two inaccurate propositions in KQ15 (exit mapping and comparator naming). The entire remainder of KQ15's safety perimeter—manifest integrity, separate reporting, anti-tamper controls, and fail-closed handling—remains fully active and binding.

### 3.3 The Append-Only Byte-Preservation Boundary (KQ3, KQ7, KQ14)
- **Rule (`corpus/QUALITY.md:11, 29, 41`):** Historical corpus bytes are never edited in place, rewritten, or deleted. Corrections append new sections at the end of the file.
- **Application to Round 13:** Line 49 of `corpus/QUALITY.md` (the original KQ15 text containing the mistaken wording) is an immutable historical record. KQ16 must be appended as a new section (`## Criteria added — round 13 (2026-10-20)`) after line 49. The historical mistake is superseded by reference, never erased.

---

## 4. Cross-Proposal Omission Audit & Peer Analysis

Analysis of emerging peer reports reveals key second-order risks that must be resolved in KQ16 and `measure.py`:

1. **Deterministic Precedence Qualification (`ReviewExit` findings F1–F3):**
   - *Risk:* The bare literal `source_mismatch=1` is misleading if read unconditionally. In `fidelity.py:65–73, 317–319`, exit 1 is emitted *only if* `source_mismatch` is the highest-ranked finding. If a snapshot is mutated and its manifest pin fails, `snapshot_tampered` (exit 2) outranks `source_mismatch` (exit 1), yielding exit 2 even though byte differences exist.
   - *Synthesis:* KQ16 must include the literal phrase verbatim and immediately follow it with an explicit qualification: `exit 1 only when no outranking exit-2 finding is present; clean is 0`.
2. **Vacuous Green & Literal Scoping (`ReviewProbe` & `AttackEffective`):**
   - *Risk:* A naive checker searching `corpus/QUALITY.md` globally for `source_mismatch=1` or forbidding `distinct nonzero exits` globally will fail: the forbidden phrase is permanently present in historical KQ15 (line 49), while the required phrase could be spoofed in a comment.
   - *Synthesis:* `measure.py` must scope its assertions strictly to the active `KQ16` table row, parsing the Markdown table row structure rather than performing unanchored file-level regex scans.
3. **Plumbing Diversity vs. External Independence (`SourceCat` & `SourceShow`):**
   - *Risk:* Conflating operational independence with external oracle authority. Both `git show` and `git cat-file blob` read from the same underlying `.git/objects/` substrate in the same repository.
   - *Synthesis:* The criterion and lesson must label the capture/comparison split as *operational procedural diversity* (porcelain display capture vs plumbing raw-object comparison without working-tree filters), explicitly disclaiming that Git commands constitute statistically independent external oracles.
4. **Automatic Applicability (`ReviewSkill`):**
   - *Confirmation:* `SKILL.md:380–384` establishes that admission criteria include "KQ1–KQ14 plus every subsequently appended criterion... all applicable, never a subset". KQ16 applies automatically upon landing in `QUALITY.md` without modifying `SKILL.md`.

---

## 5. The Non-Obvious Move: The Tripartite Boundary Governance Protocol

To resolve the tension between literal syntactic conformance, historical byte immutability, and deterministic code reality, we propose a compatible synthesis across the round's proposals:

### 5.1 The Core Tension Across Proposals
- **Executor Tension:** `Criterion` must include exact literal phrases (`source_mismatch=1; snapshot_tampered=2; source_unavailable=2`) while accurately capturing complex code logic (precedence ordering where exit 2 outranks exit 1).
- **Verifier Tension:** `Measure` must detect historical wording defects (2 before, 0 after) without falsely flagging the permanently preserved historical mistake in KQ15, and without treating literal presence as semantic runtime proof.

### 5.2 The Proposed Move: Tripartite Boundary Governance Protocol
Adopt a three-tier governance structure linking `QUALITY.md`, `measure.py`, and `fidelity.py`:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           1. CONTRACT TIER                              │
│                      (corpus/QUALITY.md: KQ16)                          │
│  • Appended row superseding KQ15 exit-class & comparator clauses only   │
│  • Carries exact audit literals:                                        │
│    - "source_mismatch=1; snapshot_tampered=2; source_unavailable=2"     │
│    - "capture: git show; comparison: git cat-file blob"                 │
│  • Explicitly qualifies precedence: exit 1 conditional on absence of     │
│    exit 2 findings (snapshot_tampered, source_unavailable, etc.)        │
│  • Explicitly disclaims external oracle status (S032/S033 method only)  │
│  • Governed by KQ14: human/source review remains ultimate semantic bar  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 Row-Scoped Parsing & Mutation Controls
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                         2. VERIFICATION TIER                            │
│                  (.ufo/waves/round-13/measure.py)                       │
│  • Standard-library read-only textual conformance probe (NOT a gate)     │
│  • Historical comparison: reads start commit (941bb32) via git cat-file │
│    blob -> reports missing assertions = 2                               │
│  • Working-tree comparison: reads live QUALITY.md -> missing = 0        │
│  • Row-scoped isolation: parses KQ16 row specifically; ignores KQ15     │
│    historical mistake to prevent false defect flags                     │
│  • Fail-closed mutation controls: in-memory removal of literals and      │
│    injection of mistaken wording must fail-closed                        │
│  • Prefix preservation check: verifies bytes 1..49 equal start commit   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                     Static Code & Receipt Grounding
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                          3. SUBSTRATE TIER                              │
│                    (fidelity.py & acceptance.json)                      │
│  • Immutable code constants: SOURCE_REVISION, SOURCE_PATH, SOURCE_OID    │
│  • Runtime comparator: git cat-file blob with sanitized environment     │
│  • Tri-state exit logic: 0 clean, 1 failed, 2 could-not-evaluate        │
│  • Deterministic PRIORITY resolution: exit 2 outranks exit 1            │
│  • Historical receipts: before=1, tamper=2, unavailable=2               │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Second-Order Effects
- **Runtime Surface:** Zero impact. No daemon, endpoint, or production probe touched.
- **Contract Surface:** Reconciles `QUALITY.md` with `SKILL.md:395–397` and `fidelity.py:317–319`, eliminating contradictory guidance for active agents while preserving historical integrity.
- **Substrate Surface:** Clarifies that Git porcelain (`git show`) and plumbing (`git cat-file`) operate over the identical repository object database (`.git/objects/`), preventing future agents from claiming multi-source statistical independence.
- **Verification Surface:** Provides a clean, non-tautological 2 → 0 before/after measurement for Claim C1 while isolating the test runner from mutable worktree side effects.

---

## 6. Risks, Contradictions, and Explicit Disclaimers

1. **Risk of Single-Case Overfitting:**
   - *Contradiction/Risk:* Correcting two propositions on one criterion row across one source path (`SOURCES.md`) does not demonstrate generalized review reliability across the entire corpus.
   - *Resolution:* Disclaim generalization explicitly. The before/after denominator is fixed strictly at 2 (the two routed propositions), not all criteria or corpus files.
2. **Risk of Conflating Textual Conformance with Semantic Verification:**
   - *Risk:* An agent observing `measure.py` exit 0 might conclude that `fidelity.py` exit mappings have been dynamically re-proven.
   - *Resolution:* `measure.py` must output JSON explicitly labeling its finding as `clean` documentation conformance, not runtime or execution proof. `fidelity.py` is not executed by this wave.
3. **Risk of Misattributing Learning Trends:**
   - *Risk:* Claiming that adding S033 or appending KQ16 improves `expansion` or `quality`.
   - *Resolution:* `expansion` remains unchanged. `quality` trend improvement must be credited strictly to the Round 12 D4 knowledge interpretation in `served-identity-crosswalk.md:87–134` (Ollama remote properties vs local weights inference), as mandated by the outside verifier spot-check.

---

## 7. Named Verification Checks for L1 Main

Per the leaf connector contract, zero tests or verification commands were executed by this seat. L1 Main should run the following static and measurement checks:

1. **Verify KQ16 Textual Append & Literal Presence:**
   ```sh
   grep -F "source_mismatch=1; snapshot_tampered=2; source_unavailable=2" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md
   grep -F "capture: git show; comparison: git cat-file blob" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md
   ```

2. **Verify Historical Prefix Byte Preservation (Lines 1–49 Intact):**
   ```sh
   git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file blob 941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md | cmp -n $(git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -s 941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md) - /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md
   # Expected exit: 0 (original historical prefix unmodified)
   ```

3. **Verify C1 Measurement Probe (Once Landed by Measure):**
   ```sh
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/measure.py
   # Expected output: JSON with before_missing=2, after_missing=0, denominator=2, verdict=clean, exit=0
   ```

4. **Verify S033 Source Row & Census Integrity:**
   ```sh
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
   # Expected: validate exits 0 (with known W04 warning); census exits 0 reporting 33 rows (A=30, mined=23)
   ```

---

## 8. Summary & Tooling Report

- **Tooling authorization record:** Tools installed or updated: **none**.
- **Delivered artifact:** Scoped connector report completed and written to `.ufo/waves/round-13/advice/CriterionLink.md`.
- **Status:** Complete; awaiting L1 integration and measurement.
