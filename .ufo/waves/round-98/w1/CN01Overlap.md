# CN01Overlap — Cross-Claim Lineage, Sibling Overlap, and Boundary Synthesis (Round 98 Wave 1)

**Seat:** `CN01Overlap` (Connector)  
**Lane:** `kama-shokunin` (`/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Base Revision:** `681c80a4e3c745c22559f74b2c2a1917bdc66fc6`  
**Freeze Revision:** `34ad44e9f783b35a804f020d6b02c48c04ade481` (`master`)  
**Milestone:** `kama r98 w1`  
**Axes Evaluated:** `operability` (8), `calibration` (7), `depth` (7)  
**Status:** Complete  

---

## 1. Executive Summary & Named Axes

This seat performs the read-only cross-claim lineage and fleet-wide sibling overlap analysis for Kama Round 98 under UFO-FSD connector rules.

1. **Declared Axes:**
   - **Calibration (7, lowest non-retired axis):** Worked by **C1** (`tools/round98-self-assessment-audit.py`, 20 checks). C1 resolves the heading-count blindness from round 97 (where `section()` skipped the `###` heading line) and verifies count agreement across 5 mutants, 6 new cells, and 19 total cells.
   - **Operability (8, assigned pair):** Worked by **C2** (`tools/round98-router-budget.py`, 19 cells). C2 sizes past the $+1$/header overcharge forgery that survived all 17 round-97 cells, introducing `W18-800k-nd1` and `W19-520k-nd4`.
   - **Depth (7, lowest non-retired axis):** Worked by **C3** (`tools/round98-depth-boundary-audit.py`, 8 rows). C3 expands the boundary table in `SKILL.md` §Round 97 correction to cover the decidable overcharge window rows and grounds the 4 preamble steps in S622 (`gguf_header_t`).

2. **Core Invariants & Boundary Rules:**
   - Work is strictly read-only on tracked lane files.
   - No subagent dispatch (`task`).
   - Grounded strictly in local repository evidence and the current round cache (`plans/round-98-claims.md`, `.ufo/waves/round-98/claims.json`, `controls/`, `tools/`).

---

## 2. Lineage: Prior-Round Defect & Wave Finding Mapping

Every claim in Round 98 is a direct, causal successor to an open finding or routed defect from Round 97. **None is a re-run of an already-admitted claim with no new defect.**

### 2.1 Lineage Mapping Table (Rounds 94–97 vs Round 98)

| Claim | Axis | Instrument & Scope | Plan References | Prior Round Lineage & Wave Findings Answered | Is Re-run? | Lineage Classification & Distinguishing Ground |
|---|---|---|---|---|---|---|
| **C1** | Calibration (7) | `tools/round98-self-assessment-audit.py`<br>(20 checks, 0 mismatches) | `plans/round-98-claims.md:43-74`<br>`claims.json:5-13` | **r97 C1:** `tools/round97-self-assessment-audit.py` (18 checks; admitted in amendment 2).<br>**r97 wave finding RV01 §2.1:** `SKILL.md:2443` heading stated "the three graded forgeries" while body prose was amended to "four probe variants" (W14–W17). Check 16 was blind to the heading because `section()` sliced from `start + 1`.<br>**r96 C3:** `tools/round96-disclosure-audit.py` (rejected-honest-stop: required false constant 6).<br>**r95 C3:** `tools/round95-freeze-audit.py`. | **NO** | **Genuinely New Defect Closed (Heading Blindness & 5-Mutant Roll-Forward).**<br>Check 19 explicitly extracts and grades the count word from the `### Round 97 correction` heading line against `len(mutants) == 5`. Check 20 grades the overcharge surface (`overcharge`, `W18-800k-nd1`, `W19-520k-nd4`) across `SCORECARD.md`, `SKILL.md`, and counter docstrings. Check 16 rolls forward from 4 mutants / 17 cells to 5 mutants / 19 cells / 6 new cells. |
| **C2** | Operability (8) | `tools/round98-router-budget.py`<br>(19 cells, `--slow-files 72`, mutant controls) | `plans/round-98-claims.md:75-125`<br>`claims.json:14-22` | **r97 C2:** `tools/round97-router-budget.py` (17 cells; admitted with 4 mutants).<br>**r97 closing wave finding RV03 F5 / R3:** Proved that a probe overcharging $+1$ step per header ($6+nd$ instead of $5+nd$) passed all 17 round-97 cells (`rv03-newcells.out`, `rv03-legacy-plus1.out`), because all round-97 new cells (W14, W15, W17) tested only the $>$ side of `MAX_STEPS` expecting `-`.<br>**r96 C1:** `tools/round96-router-budget.py` (13 cells).<br>**r95 C1:** `tools/round95-router-budget.py` (deterministic work budget replacing wall clock). | **NO** | **Genuinely New Defect Closed (Sizing Past Overcharge Forgery).**<br>Adds the `overcharge` mutant (`steps[0] += 1` at loop top) and two new discriminating cells: `W18-800k-nd1` (800k headers, nd=1) and `W19-520k-nd4` (520k headers, nd=4). Both cells expect `invalid` (real steps $4,800,004 \le 5\text{M}$ and $4,680,004 \le 5\text{M}$), whereas the $+1$ overcharge probe needs $5,600,004 > 5\text{M}$ and $5,200,004 > 5\text{M}$ (producing `-`). Control receipts verify `survived=1` on the 17-cell set (`controls/c2-legacy-mutants.out`) and `caught=1`/`cell_ok=0` on W18/W19 (`controls/c2-new-mutants.out`). |
| **C3** | Depth (7) | `tools/round98-depth-boundary-audit.py`<br>(8 required boundary rows, 14 checks) | `plans/round-98-claims.md:126-153`<br>`claims.json:23-31` | **r97 C3:** `tools/round97-depth-boundary-audit.py` (6 boundary rows; admitted in amendment 2).<br>**r97 wave finding RV03 F5 & CR01:** The 6 round-97 rows were all on the far side or ceiling; none answered whether a file in the overcharge window ($714,286 < T \le 833,332$ at nd=1; $500,000 < T \le 555,555$ at nd=4) decides under the real probe.<br>**r96 C2:** `tools/round96-depth-audit.py` (step-cost table, per-rank ceilings). | **NO** | **Genuinely New Ground (Overcharge Window Boundary Duals & S622 Preamble Grounding).**<br>Expands the boundary table in `SKILL.md` from 6 to 8 rows by adding `(800,000, nd=1)` `invalid` and `(520,000, nd=4)` `invalid`. C3 requires citation of S622 (`gguf_header_t` 4 fields: magic, version, tensor_count, metadata_kv_count) to ground the 4 preamble steps (`PREAMBLE = 4`). |

---

## 3. Sibling Overlap: Cross-Lane Fleet Scan & Province Verdict

### 3.1 Sweep Commands and Execution Evidence

A full scan across all 21 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin` (excluding `/home/vgpnk/Projects/shokunin/kama-shokunin`) was conducted for the three round-98 technical concepts:
1. GGUF step budgets / parser work limits
2. Overcharge mutants / $+1$ loop step probes
3. SKILL-heading count audits

```bash
# 1. Sweep for GGUF step budget claims in sibling plans and tools
grep -rnE "GGUF.*step|step.*budget.*gguf|\bGGUF\b" \
  /home/vgpnk/Projects/shokunin/*-shokunin/{plans,tools}/ --exclude-dir=kama-shokunin
# Output: 0 matches (No matches found)

# 2. Sweep for overcharge probe mutants in sibling plans and tools
grep -rnE "overcharge" \
  /home/vgpnk/Projects/shokunin/*-shokunin/{plans,tools}/ --exclude-dir=kama-shokunin
# Output: 0 matches (No matches found)

# 3. Sweep for SKILL-heading count audits in sibling plans and tools
grep -rnE "heading.*count|count.*heading|SKILL.*heading" \
  /home/vgpnk/Projects/shokunin/*-shokunin/{plans,tools}/ --exclude-dir=kama-shokunin
# Output: 0 matches (No matches found)

# 4. Fleet-wide whole-tree sweep for 'overcharge' across all sibling repositories
grep -rnE "overcharge" \
  /home/vgpnk/Projects/shokunin/*-shokunin/ --exclude-dir=kama-shokunin --exclude-dir=.git
# Output: 0 matches (No matches found)
```

### 3.2 Sibling Province Verdict: **No Overlap**

- **GGUF Step Budgets & Probe Work Limits (100% Kama Exclusive):**
  Under `PROVINCE.md` (rounds 88–98) and `corpus/knowledge/cross-lane-scope.md`, `kama-shokunin` holds sole ownership of local model serving, endpoint health, and deterministic GGUF byte/seek parser step budgets (`MAX_STEPS = 5,000,000`). No sibling lane (`tameshi`, `tsukuroi`, `kumitate`, `kengaku`, etc.) parses GGUF binary files or implements step-budget counters.
- **Overcharge Mutants (100% Kama Exclusive):**
  The $+1$/header overcharge mutant (`steps[0] += 1` inside `for _ in range(n_tensors):`) is unique to `tools/round98-router-budget.py`. Zero references exist anywhere in the fleet.
- **SKILL-Heading Count Audits (Held Lane Ground):**
  While sibling lanes (`tameshi-shokunin`, `kumitate-shokunin`, `chousa-shokunin`, `souji-shokunin`) implement self-assessment audits on their own scorecards (e.g. `kumitate` build proxy checks, `souji` git pointer resolution, `tameshi` test coverage), kama's C1 instrument (`tools/round98-self-assessment-audit.py`) grades 20 named surfaces strictly internal to `kama-shokunin`.

---

## 4. Contested Scope to Report Rather Than Absorb

Under `PROVINCE.md` ("Out of province → report, never absorb") and `corpus/knowledge/cross-lane-scope.md`:
1. **Loopback Listener on 127.0.0.1:8080 (External Host Service):**
   A non-lane Ollama listener remains active on loopback port 8080, causing `round78-instruments` (pre-report arm 10) to register red. Kama observes this read-only; it strictly refuses to restart or kill host services.
2. **Model Weight Loading / Inference Evaluation (Kengaku Domain):**
   `kama-probe.sh` checks GGUF geometry in linear time without loading tensor weights into VRAM. Model inference and perplexity belong strictly to `kengaku-shokunin`.
3. **Dispatch & Routing Architecture (Kumitate Domain):**
   Autoload candidate selection (`status.args`) validates paths for llama-server router mode. Fleet agent routing and dispatch pipelines belong to `kumitate-shokunin`.
4. **Carried Defects from Round 97:**
   R1 (`round75-instruments` bad_rows=19), slow `/props` answer (r94 SC02 F4), pass-level wall-clock wrapper (SC01), and the ctime memo shape (disclosed as unobservable from outside) remain routed and carried unchanged.

---

## 5. One Bounded, Non-Obvious Observation (Connector Move)

### 5.1 Evidence from Current Round Cache & Peer Findings

A cross-claim synthesis across the round cache, `plans/round-98-claims.md`, and peer findings (`CR02Wording`, `EX01SelfAssessControl`, `RV03Intent`, `considerthese/2026-11-08.md`) reveals three interrelated discrepancies:

1. **Ungraded Prose Row Counts vs Graded Table Expansion (Calibration & Depth):**
   - In C3, the boundary table in `SKILL.md` §Round 97 correction expands from 6 rows to 8 rows, enforced strictly by `tools/round98-depth-boundary-audit.py:130` (`rows == 8`).
   - In C1, check 19 now grades the section heading count word ("five graded forgeries") and check 16 grades mutant/cell counts.
   - **However, prose row counts are completely ungraded by both counters:**
     - `SKILL.md:2449` currently reads: *"The six rows below are the two boundary classes the round-96 table does not name:"*
     - `SCORECARD.md:17` depth row reads: *"six KV-free rows at nd=1 and nd=4"*
     Neither C1 nor C3 inspects the row count word ("six" vs "eight") in the prose. If `SKILL.md:2449` or `SCORECARD.md:17` is left saying "six", both counters stay 100% green! This reproduces the exact mechanism of the round-97 heading defect (a narrative disclosure drifting from the table while the counters report green).

2. **False Lower-Bound Sentinel Attribution in Disclosed Limit (f) (Operability):**
   - In `plans/round-98-claims.md:121-122`, disclosed limit (f) states:  
     *"W18/W19 expect `invalid`: they pin the overcharge class from the decidable side; they do not pin the budget's lower bound (**W11 does**, in the same run)."*
   - As proved by `CR02Wording`, this is mathematically false:
     - `W11-700k` (700,000 headers, nd=1) pays $4 + 700,000 \times 6 = 4,200,004 \le 5,000,000$ (`invalid`).
     - Under an undercharge mutant (0 header steps), W11 pays $4 \le 5,000,000 \rightarrow \text{invalid}$ (still green).
     - Under an overcharge mutant ($+1$ step/header), W11 pays $4 + 700,000 \times 7 = 4,900,004 \le 5,000,000 \rightarrow \text{invalid}$ (still green).
     - **W11 catches neither undercharge nor overcharge.**
     - The cell that actually pins the lower bound (catches undercharge) is **W14-900k-nd1** ($5,400,004 > 5\text{M} \rightarrow -$; under undercharge pays $4 \le 5\text{M} \rightarrow \text{invalid} \rightarrow \text{red}$), as verified in `controls/c2-new-mutants.out:15-21` (`expect_cell=W14-900k-nd1 cell_ok=0 caught=1`).

3. **False Instrument Attribution in Lesson M2 (Calibration & Operational History):**
   - In `corpus/lessons/round-98.md:50-56`, M2 states:  
     *"Captured-by: the counter's own control run (the `cells=` count in the summary line)... Shown able to fail: the 16-cell receipt stands in the wave dir as the red evidence."*
   - As proved by `CR02Wording`, in `--control` mode `tools/round98-router-budget.py:653-675` early-returns before the `want_cells` check (`:715-722`). When W01 was dropped, $n=16$, all 16 cells succeeded, `survived = 1`, `ok = 1`, and the command exited 0! The counter never failed. The capture was made by **L1 reading the printed count**, and the 16-cell receipt was never committed to git. Attributing automated rejection to an instrument that exited 0 is the round's standing failure class.

### 5.2 Affected Axes
- **Calibration (7, lowest axis):** Eliminates narrative drift in prose row counts ("six" vs "eight"), updates the heading count ("three" $\rightarrow$ "five"), and corrects lesson capture attribution.
- **Depth (7, lowest axis):** Explicitly pairs C3's two new boundary rows (`(800,000, nd=1)` and `(520,000, nd=4)`) to C2's two new witnesses (`W18-800k-nd1` and `W19-520k-nd4`), establishing them as the mathematical two-sided boundary duals of the overcharge window ($714,286 < T \le 833,332$ at nd=1; $500,000 < T \le 555,555$ at nd=4).
- **Operability (8, assigned pair):** Replaces the false W11 lower-bound attribution with the true sentinel W14 in disclosures.

### 5.3 Proposed Move: Cross-Claim Boundary & Sentinel Reconciliation

During integration at M1/M2/M3:

1. **Reconcile Prose Row Counts and Document Overcharge Duals in `SKILL.md`:**
   - In `SKILL.md:2443`, roll the heading to `### Round 97 correction (step-budget boundary table and the five graded forgeries; dated 2026-11-08)` (satisfies C1 check 19).
   - In `SKILL.md:2449`, update *"The six rows below"* to *"The eight rows below"*.
   - In the boundary table, add rows 7 and 8:
     - `| 800,000 | nd=1 | 4,800,004 | <= budget | invalid |`
     - `| 520,000 | nd=4 | 4,680,004 | <= budget | invalid |`
   - Explicitly annotate rows 7 and 8 as the decidable witnesses for C2 cells `W18-800k-nd1` and `W19-520k-nd4`, contrasting them with their $+1$ overcharge counterparts ($5,600,004 > 5\text{M} \rightarrow -$ and $5,200,004 > 5\text{M} \rightarrow -$).
   - Cite S622 beside S620 and S621 to satisfy C3 check 11 (`"S622" in sect`).

2. **Sync SCORECARD Depth Row:**
   - In `SCORECARD.md:17`, update the depth row text to *"eight KV-free rows at nd=1 and nd=4 ... five graded probe forgeries W14-W19"*, recomputing the sha256 digest, line count, and section count so that C1 checks 1–3 and 16 pass with 0 mismatches.

3. **Correct Disclosed Limit (f) and Lesson M2 Attribution:**
   - In `plans/round-98-claims.md:121-122` (or in the round-98 closing report): correct limit (f) to state: *"(W14 does, from the `-` side, in the same run)"*.
   - In `corpus/lessons/round-98.md:50-56` (M2): correct `Captured-by` to *"L1 read of the `cells=` summary line — the control run exited 0 (`ok=1`)"*, and withdraw the claim that a 16-cell red receipt stands in the wave dir.

### 5.4 Risks & Second-Order Effects
- **Second-Order Risk (C1 Check 1 Hash Invariant):** Editing `SKILL.md` modifies its SHA256 digest and line count. If `SCORECARD.md` depth row is not simultaneously updated with the exact new hash and line count, C1 check 1 will fail with `mismatches=1`.
  - *Mitigation:* Recompute `sha256sum SKILL.md` and `wc -l SKILL.md` after doc edits and update `SCORECARD.md:17` in the same commit.
- **Contract Risk:** Does any part of this move touch frozen counter bytes?
  - *Mitigation:* Zero counter bytes are modified. K1 kill rules on `tools/round98-*.py` remain intact. The move operates entirely within documentation, disclosures, and synchronization of declared surfaces.

### 5.5 Verification Commands
```bash
# 1. Verify C1 self-assessment audit passes 20/20 checks with 0 mismatches at M1
python3 tools/round98-self-assessment-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <M1>
# Expected: SELF_ASSESS98 checks=20 mismatches=0 met=True

# 2. Verify C2 router budget runs all 19 cells with stable load at M2
python3 tools/round98-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <M2> \
  --work /fast/scratch/hyaku/kama-r98/CN01Overlap --slow-files 72
# Expected: ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1

# 3. Verify C3 depth boundary audit recomputes all 8 rows at M3
python3 tools/round98-depth-boundary-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <M3>
# Expected: DEPTH_BOUNDARY98 rows=8 checks=14 mismatches=0 met=True
```
