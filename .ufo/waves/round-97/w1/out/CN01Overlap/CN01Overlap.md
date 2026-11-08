# CN01Overlap — Cross-Claim and Cross-Lane Overlap Scan (Round 97 Wave 1)

**Seat:** `CN01Overlap` (Connector)  
**Lane:** `kama-shokunin` (`/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Milestone:** `kama r97 w1`  
**Axes Evaluated:** `operability` (8), `calibration` (7), `depth` (7)  
**Status:** Complete

---

## 1. Executive Summary & Named Axes

This seat performs the canonical cross-claim and cross-lane overlap analysis for Round 97 under UFO-FSD connector rules:
1. **Prior-Round Lineage:** Evaluates Round 97's three claims (C1 calibration, C2 operability, C3 depth) against previous rounds 93–96 to establish whether each is a re-run, narrowed successor, or genuinely new ground.
2. **Sibling Knowledge Scan:** Audits `/home/vgpnk/Projects/shokunin/*-shokunin/corpus/knowledge` for step budgets in probe parsers and SCORECARD self-assessment audits (8 cited rows) to determine whether kama duplicates sibling territory or remains within its assigned province.
3. **Contested Scope & Boundary Verdict:** Identifies out-of-province concerns that must be reported rather than absorbed.
4. **Connector Synthesis:** Synthesizes the findings of wave-1 peer seats (`RV01SelfAssess`, `RV02BudgetCells`, `CR01Boundary`, `CR02Wording`, `RV03Intent`, `EX01SelfAssessControl`) into one bounded, non-obvious move that improves calibration, depth, and operability without harming any other axis.

---

## 2. Prior-Round Mapping Table (Rounds 93–96 vs Round 97)

Every claim in Round 97 answers a routed defect or uncovers a blind spot from earlier rounds. None is an ungrounded re-run, and none is detached from the lane's core serving/health domain.

| Claim | Axis | Counter / Artifact | Round 97 Plan Reference | Prior Lineage (Rounds 93–96) | Plan Lines | Lineage Classification |
|---|---|---|---|---|---|---|
| **C1** | Calibration (7) | `tools/round97-self-assessment-audit.py` (14 checks, 0 mismatches) | `plans/round-97-claims.md:33-69` | **r96 C3:** `tools/round96-disclosure-audit.py` (3 checks; failed when check 1 required the false constant "6 steps/header").<br>**r95 C3:** `tools/round95-freeze-audit.py` (receipts present, tokens match, S-rows resolve).<br>**r94 C3:** frontier-step census (`sources-census.sh validate`, lesson Gate/Mistakes).<br>**r93:** No C3 declared. | `plans/round-96-claims.md:100-125`<br>`plans/round-95-claims.md:107-130`<br>`plans/round-94-claims.md:94-108`<br>`plans/round-93-claims.md:1-95` | **Corrected & Expanded Successor.**<br>Directly remedies the falsification that caused round-96's `rejected-honest-stop` (routed defect 1: false constant 6 disclosure and literal-presence counter). Replaces the brittle 3-disclosure check with a 14-surface multi-file self-assessment audit across SCORECARD live rows, SKILL.md, probe comments, S-rows, and previous round identity. |
| **C2** | Operability (8) | `tools/round97-router-budget.py` (17 cells; amended with `--slow-files 72`) | `plans/round-97-claims.md:70-109`<br>`plans/round-97-amendment-1.md:1-27` | **r96 C1:** `tools/round96-router-budget.py` (13 cells; raised `MAX_STEPS` to 5M). Closing wave MT01 proved 4 probe mutants survive all 13 cells.<br>**r95 C1:** `tools/round95-router-budget.py` (10 cells W01–W10; deterministic work budget replacing wall clock).<br>**r94 C1:** `tools/round94-router-budget.py` (per-file deadline slice; failed under load).<br>**r93 C1:** `tools/round93-router-repeat.py` (10 repeat cells; inode memo). | `plans/round-96-claims.md:29-74`<br>`plans/round-95-claims.md:30-70`<br>`plans/round-94-claims.md:21-53`<br>`plans/round-93-claims.md:18-50` | **Narrowed, Forgery-Hardened Successor.**<br>Carries forward the 13 legacy cells unchanged and adds 4 targeted discrimination cells (W14 900k-nd1, W15 700k-nd4, W16 maxmeta, W17 833333-nd1) plus 4 explicit mutation controls (`flat6`, `undercharge`, `maxmeta`, `nopreamble`) to close the survivability loophole discovered in r96 closure. |
| **C3** | Depth (7) | `tools/round97-depth-boundary-audit.py` (`SKILL.md` §Round 97 correction) | `plans/round-97-claims.md:110-131` | **r96 C2:** `tools/round96-depth-audit.py` (step-cost table in SKILL.md; stated 6 steps/header and per-rank ceilings; cited S618).<br>**r95 C2:** `tools/round95-setter-sweep.py` (106 setter rows P01–P106, 9 entry decisions R20/R21).<br>**r94 C2:** `tools/round94-setter-sweep.py` (config.ini route, entry points, R18/R19).<br>**r93 C2:** `tools/round93-setter-rows.py` (48 setter rows, R16/R17). | `plans/round-96-claims.md:75-99`<br>`plans/round-95-claims.md:71-106`<br>`plans/round-94-claims.md:54-93`<br>`plans/round-93-claims.md:51-86` | **Narrowed, Arithmetic-Corrected Successor.**<br>Corrects the erroneous constant-6 narrative from Round 96 C2 to the true `5 + nd` formula, cites S620 (spec) and S621 (code supersession of S618), and adds an executable 6-row boundary lookup table for readers covering the two critical rank classes (nd=1 and nd=4) across the 5 000 000 step ceiling. |

---

## 3. Sibling Knowledge Scan Table (`*-shokunin/corpus/knowledge`)

A fleet-wide scan was conducted across `/home/vgpnk/Projects/shokunin/*-shokunin/corpus/knowledge` for the two round topics:
- **Topic A:** Step budgets in probe parsers (deterministic work limits, parser step counters, GGUF/model parser bounds).
- **Topic B:** Self-assessment audits of SCORECARD (executable rows, self-claim audits, evidence pointer resolution).

Below are the 8 most relevant rows across the fleet:

| Row | Lane | File & Line | Topic | Ground & Content | Province Relationship to Kama |
|---|---|---|---|---|---|
| 1 | `tameshi-shokunin` | `corpus/knowledge/executable-self-assessment.md:5` (lines 7–10, 36–39) | Topic B (SCORECARD audit) | "Executable self-assessment rows: claims with checks" — defines the pattern of executing a SCORECARD row's quoted command at a target revision (`c1-measure.py`) to verify stated scores and capability outputs. Cites kumitate as prior art. | **Stays in kama's province.** Tameshi owns fleet-wide mutation testing and test sufficiency frameworks. Kama's C1 applies executable self-assessment strictly to its own internal repository artifacts (`SCORECARD.md`, `SKILL.md`, `tools/kama-probe.sh`) without duplicating or altering tameshi's testing harness. |
| 2 | `kumitate-shokunin` | `corpus/knowledge/executable-scorecard.md:1` (lines 3–6, 59–62) | Topic B (SCORECARD audit) | "executable scorecard — this lane's own axes, re-derived" — re-derives kumitate's own checklist items and axis scores using `scripts/proxy-check.mjs`. | **Stays in kama's province.** Kumitate owns agent dispatch and build orchestration. Its scorecard audit governs kumitate-local metrics; kama audits its own serving/endpoint health metrics. |
| 3 | `chousa-shokunin` | `corpus/knowledge/self-claim-audit-r63.md:5` (lines 10–16, 20–28) | Topic B (Self-claim audit) | "Auditing a self-assessment statement against the repo it names (round 63)" — defines 7 machine-checkable rule classes (`tools/claims-audit.py`) to detect false statements in frozen claims files. | **Stays in kama's province.** Chousa owns fleet-wide investigation and meta-claims lexical checking. Kama's C1 is domain-specific to kama's repo (e.g. GGUF step formulas, git ancestry of capability pointers). |
| 4 | `souji-shokunin` | `corpus/knowledge/self-assessment-pointer-resolution.md:7` (lines 13–18, 26–34) | Topic B (Pointer audit) | "A dangling evidence pointer is a census item: locate its bytes, then say where they live" — classifies dangling evidence pointers in SCORECARD/SKILL into a 7-class ledger (`tools/souji-pointer-check.py`). | **Stays in kama's province.** Souji owns repository hygiene and git tracking policy. Kama's C1 check 6 evaluates that `router-byte-decided` points to an ancestor commit with committed evidence, keeping self-consistency within its own tree. |
| 5 | `kake-shokunin` | `corpus/knowledge/claim-count-derivation.md:1` (lines 7–10) | Topic B (Self-assessment counts) | Derives self-assessment counts from commands; explicitly cites and imports S130 from kama's `corpus/knowledge/self-assessment-at-writing.md`. | **Stays in kama's province.** Demonstrates that kama originally originated the self-assessment count derivation pattern; kake imports it for web surfaces. |
| 6 | `kama-shokunin` | `corpus/knowledge/self-assessment-at-writing.md:5` (lines 18–24) | Topic B (SCORECARD audit) | "Checking self-assessment statements at writing" — establishes kama's standing protocol for checking self-assessment statements against repo state and recording dated corrections in `SCORECARD.md`. | **Held core ground.** Sourced originally in round 29; directly grounds kama C1's 14-check audit. |
| 7 | `kama-shokunin` | `corpus/knowledge/endpoint-identity.md:99` | Topic A (Probe budget) | "A refusal or timeout is DEAD for that sample under the binding contract. It means unavailable within the probe budget..." | **Held core ground.** Kama exclusively owns local endpoint probe budgets and failure classification. |
| 8 | `kumitate-shokunin` | `corpus/knowledge/native-trial-launch.md:133` | Topic A (Probe budget) | `budgets.phase0ProbeTokens` vs probes×2048 → halt `probe-budget` | **Disjoint domain.** Kumitate's "probe budget" governs LLM token allowances during agent trial launches. It shares no mechanism or semantics with kama's deterministic GGUF byte/seek parser step budget (`MAX_STEPS = 5 000 000`). |

### Province Verdict
1. **Probe Parser Step Budgets:** 100% exclusive to `kama-shokunin`. No sibling lane (neither `tameshi-shokunin`, `tsukuroi-shokunin`, nor `kumitate-shokunin`) parses GGUF/model files or implements parser step budgets. Kama's C2 and C3 operate wholly within held ground (`PROVINCE.md` rounds 88–93).
2. **SCORECARD Self-Assessment Audits:** Completely compliant with lane boundaries. Sibling lanes (`tameshi`, `kumitate`, `chousa`, `souji`) maintain meta-patterns or audit their own respective scorecards. Kama's C1 instrument (`tools/round97-self-assessment-audit.py`) grades 14 surfaces strictly internal to `kama-shokunin`.

---

## 4. Contested Scope to Report Rather Than Absorb

Under `PROVINCE.md` ("Out of province → report, never absorb") and `corpus/knowledge/cross-lane-scope.md`, the following surfaces observed during Round 97 must remain reported rather than absorbed into lane claims:

1. **Host Ollama Listener on 127.0.0.1:8080 (Operator-Owned):**
   - Observed active on loopback port 8080 outside the lane's control. It causes `round78-instruments` (pre-report gate arm 10) to register red.
   - *Province Boundary:* Kama observes and classifies loopback listeners read-only; it strictly refuses to kill, restart, or repoint host-level daemons (`PROVINCE.md` write boundary). Reported as an external host condition.
2. **Model Weight Loading / Inference Evaluation (Kengaku Domain):**
   - The probe's `ROUTER_PY` checks file existence, permissions, and GGUF header geometry in linear time without loading tensor weights.
   - *Province Boundary:* Evaluating model inference, perplexity, context quality, or sampling behavior belongs strictly to `kengaku-shokunin`. Kama reports only file validity and autoload readiness.
3. **Dispatch & Routing Architecture (Kumitate Domain):**
   - Router autoload candidate validation (`status.args`) checks local model paths for llama-server router mode.
   - *Province Boundary:* The dispatch mechanism, upstream agent routing, and orchestration pipelines belong to `kumitate-shokunin`. Kama handles only endpoint readiness.
4. **Fleet-Wide Test Harness & Claim Meta-Auditing (Tameshi & Chousa Domains):**
   - Kama's C1 counter is strictly lane-local. Any proposal to generalize `round97-self-assessment-audit.py` across sibling scorecards would violate tameshi's and chousa's jurisdictions and is refused.
5. **Carried / Disclosed Defects from Round 96/97 Plan:**
   - Carried defects remain explicitly routed: R1 (`round75-instruments` bad_rows=19), slow `/props` answer (r94 SC02 F4), pass-level wall-clock wrapper (SC01), and the ctime memo shape (disclosed as unobservable from outside).

---

## 5. Non-Obvious Connector Move (Cross-Claim Synthesis)

### Evidence from Round 97 Waves & Peers
- **Peer Findings:**
  - `RV03Intent` demonstrated in `rv03-newcells.out` that all four new cells in C2 (W14, W15, W16, W17) evaluate only the `>` side of the step budget (exceeding budget $\rightarrow$ `-`, loadable). Consequently, an overcharge mutant (such as `plus1`: charging $+1$ extra step per header) or a stub probe that always emits `MODEL_OK` passes all four new cells!
  - `CR02Wording` and `RV01SelfAssess` identified a latent disclosure discrepancy: `SKILL.md:2443` is headed `### Round 97 correction (step-budget boundary table and the three graded forgeries...)` and lines 2463–2467 discuss only 3 variants and W14–W16, omitting W17 and the 4th mutant (`nopreamble`), whereas `round-97-claims.md` line 70 and `tools/round97-router-budget.py` explicitly grade 4 forgeries across 17 cells.
  - `EX01SelfAssessControl` proved that `tools/round97-self-assessment-audit.py` (C1) validates 14 discrete checks, but does not check the forgery count disclosure in `SKILL.md`. Check 9 only requires the 5 ceilings and S620/S621 citations. This repeats the exact mechanism of Round 96's rejection: a narrative disclosure in `SKILL.md` drifting from the counter's actual mechanism while the self-assessment audit stays green!
  - `CR01Boundary` noted that C3's boundary table in `SKILL.md` contains the exact two-sided boundary pairs:
    - nd=1: `833,332` (4,999,996 $\le$ budget $\rightarrow$ `invalid`) vs `833,333` (5,000,002 $>$ budget $\rightarrow$ `-`)
    - nd=4: `555,555` (4,999,999 $\le$ budget $\rightarrow$ `invalid`) vs `555,556` (5,000,008 $>$ budget $\rightarrow$ `-`)

### Affected Axes
- **operability** (8, assigned pair)
- **calibration** (7, lowest axis)
- **depth** (7, lowest axis)

### Proposed Move
**Reconcile the Disclosed Forgery Count and Cross-Couple the C2/C3 Boundary Duals in SKILL.md and Self-Assessment Audit Documentation.**

Specifically, in the integration phase:
1. **Harmonize Narrative Disclosures:** Update `SKILL.md` §Round 97 correction heading and prose to explicitly declare **four** graded probe forgeries (adding `nopreamble`, which drops the 4 preamble steps and is witnessed by W17 at 833,333 headers nd=1: $4,999,998 \le 5\text{M} \rightarrow \text{invalid}$ under mutant vs $5,000,002 > 5\text{M} \rightarrow -$ under real probe).
2. **Explicitly Cross-Link C3 Boundary Table to C2 Witnesses:** Annotate the C3 boundary table in `SKILL.md` to show that row 2 (`833,333`, nd=1 $\rightarrow$ `-`) is the exact witness for W17, and explain that row 1 (`833,332`, nd=1 $\rightarrow$ `invalid`) is its `<=` dual that establishes two-sided discrimination against overcharging forgeries (the `plus1` class identified by `RV03Intent`).
3. **Preserve C1 Self-Assessment Digest Consistency:** Recompute and update the SHA-256 and line count in SCORECARD's live `depth` row so that C1's Check 1 remains strictly `0 mismatches` at M1.

### Risks & Invariants
- *Risk:* Editing `SKILL.md` without updating SCORECARD's live depth row would flip C1 Check 1 to `mismatch=1` (as demonstrated by EX01 mutant A).
  *Mitigation:* C1 check 1 strictly binds the SHA256; any doc edit must simultaneously update SCORECARD's live depth row.
- *Risk:* Changing frozen counters or predicates.
  *Mitigation:* The move touches zero frozen code or counter bytes; it reconciles documentation and structural coupling between already-declared claims C2 and C3.

### Verification
- `python3 tools/round97-self-assessment-audit.py --repo . --rev M1` exits 0 with `checks=14 mismatches=0 met=True`.
- `python3 tools/round97-router-budget.py --repo . --rev M2 --work <scratch> --slow-files 72` exits 0 with `cells=17 mismatches=0 load_cells=17 load_stable=1`.
- `python3 tools/round97-depth-boundary-audit.py --repo . --rev M3` exits 0 with `rows=6 checks=8 mismatches=0 met=True`.
- Non-author review verifies that `SKILL.md` §Round 97 correction correctly states four forgeries, aligning narrative disclosure with counter implementation.
