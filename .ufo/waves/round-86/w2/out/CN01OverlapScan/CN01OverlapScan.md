# CN01OverlapScan — Cross-Lane Overlap Scan and Synthesis Advisory (Wave 2)

**Seat:** CN01OverlapScan (kama round 86, wave 2 falsify)  
**Role:** UFO-FSD Connector  
**Assigned Axes:** Calibration (7) + Operability (8)  
**Judged On:** Freshness  
**Target Milestone:** kama r86 w2  
**Frozen Base:** `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`  
**Freeze Commit:** `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`  
**Measured Master Revision:** `67eddac89f44e768b670301ea0feff06e766f32d`  

---

## 1. Executive Summary & Named Axes

Following three consecutive rejected closures on kama (`round-83` harmed via stale live self-assessment cells; `round-84` honest stop via missed frozen disclosure instruction; `round-85` honest stop via C1 kill rule firing on fenced/comment shadow cells, and C2 mutants M5/M6 escaping due to unverified summary cardinality), round 86 establishes three hardened claims:
- **C1 (calibration):** Rendered-cell identity binding live SCORECARD self-assessment cells (`tools/round86-rendered-cells.py`).
- **C2 (operability):** Mutant-to-owning-arm mapping and summary cardinality reconciliation (`tools/round86-mutant-owners.py`).
- **C3 (freshness):** Pin-recheck origin corroboration against live upstream source bytes (`tools/round86-pin-origin.py`).

As the Wave 2 UFO-FSD Connector, this audit executes an adversarial cross-lane overlap scan across all 21 sibling lanes in `/home/vgpnk/Projects/shokunin`. It attacks the novelty and independence of kama's round-86 claims by systematically discovering prior art across all three capability surfaces, determines whether kama duplicates or extends sibling tools, and synthesizes a non-obvious move that advances **freshness** and **calibration** without harming any axis.

---

## 2. Attack Verdict & Measured Commands

All checks were executed against committed master at `67eddac89f44e768b670301ea0feff06e766f32d`:

```bash
# 1. Verification of C1 rendered-cell counter on committed master
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py c1 \
    --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --rev 67eddac89f44e768b670301ea0feff06e766f32d \
    --work /fast/scratch/hyaku/kama-r86/CN01OverlapScan/w1
# Exit: 0
# Output: RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85

# 2. Verification of C2 mutant owners counter on committed master
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py c2 \
    --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --rev 67eddac89f44e768b670301ea0feff06e766f32d \
    --work /fast/scratch/hyaku/kama-r86/CN01OverlapScan/w2
# Exit: 0
# Output: DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5

# 3. Verification of C3 live pin-origin counter on committed master
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py c3 \
    --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
    --rev 67eddac89f44e768b670301ea0feff06e766f32d \
    --work /fast/scratch/hyaku/kama-r86/CN01OverlapScan/w3
# Exit: 0
# Output: PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0
```

---

## 3. Cross-Lane Overlap Scan

### (a) Rendered-Markdown Cell Selection for Self-Assessment Grading

#### Hit 1: `kaidoku-shokunin` (Major Discovery — Uncited in Prior Waves)
- **File:** `kaidoku-shokunin/tools/round-50/c2-record.py`
- **Functions:** `vis(t, keep=())` (lines 282–319), `sections(t, head)` (lines 322–334), and atom `B2` check (lines 525–548).
- **Revision:** `5068ba6417f3cfc6693ca5e4dbe106c08e305174` (introduced in round 50).
- **What it proves:** `kaidoku`'s `vis()` explicitly defined "The text a reader sees", stripping lines inside fenced code blocks (`FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})')`) and HTML comments (`<!-- ... -->`), tracking matching opening/closing delimiters and length, with unterminated fences running to EOF. Crucially, in atom `B2` (line 525), `kaidoku` selected the `| calibration |` row directly from `sections(vis(sc), '## Owned axes')` in `SCORECARD.md` via `[l for l in sec if re.match(r'^ {0,3}\|\s*calibration\s*\|', l)]`!
- **Duplicate vs. Distinct:** **Distinct capability.** While `kaidoku` established the fleet precedent for filtering fences/comments to select `| calibration |` rows in `SCORECARD.md`, `kama`'s `tools/round86-rendered-cells.py` significantly hardens and extends this:
  1. `kaidoku`'s `vis` did not check indentation for code blocks (it allowed 0–3 spaces, but failed to strip 4-space indented code blocks under CommonMark 0.31.2 §4.4);
  2. `kaidoku` did not enforce column-0 (it permitted up to 3 spaces indentation, allowing blockquote- or list-nested cells to pass);
  3. `kaidoku` did not exclude historical `round-<N> correction` sections (in fact, it specifically evaluated historical correction lines);
  4. `kama` introduces coupled multi-token binding (40-hex commit $R$, ancestor verification, exact token matching in receipt bytes at $R$, and gate command round matching token round);
  5. `kama` resolves the newest closure dynamically by highest round number, avoiding date-parsing crashes.
- **Precedent to Cite:** Kama **must cite** `kaidoku-shokunin/tools/round-50/c2-record.py` (`vis()`) as the earliest fleet precedent for stripping code fences and HTML comments when selecting `| calibration |` rows in `SCORECARD.md`.

#### Hit 2: `chousa-shokunin`
- **File:** `chousa-shokunin/tools/research-gate.sh`
- **Function:** `load_sections()` (lines 791–853); documented in `corpus/knowledge/fenced-heading-r17.md` and `html-comment-r20.md`.
- **Revision:** `acca24498b8259d179db144a8bb2d44c0935e2c1` (rounds 17/20).
- **What it proves:** Bash-based CommonMark fence pairing (`^\ {0,3}(\`{3,}|~{3,})`) and HTML comment tracking (`<!--` to `-->`) to prevent ATX section headings (`## `) inside code blocks or comments from splitting research records.
- **Duplicate vs. Distinct:** **Distinct capability.** Targets section-level ATX headings in deep research records, not self-assessment tables or authority paragraphs.

#### Hit 3: `souji-shokunin`
- **File:** `souji-shokunin/tools/souji-landing-gate.py`
- **Function:** Lines 130, 373–405 (`HTML_COMMENT_RE.sub("", ...)` and `stripped.startswith("```")`).
- **Revision:** `c7228424c3919ecf142bab1aec8181722d86467b`.
- **What it proves:** Ignores quoted failure reports in lesson text via naive regex and fence toggle.
- **Duplicate vs. Distinct:** **Distinct capability.** Naive toggle without CommonMark delimiter length matching or cell discrimination.

---

### (b) Mutant $\to$ Owning-Arm Mapping with Summary Cardinality Reconciliation

#### Hit 1: `mado-shokunin`
- **File:** `mado-shokunin/quality/counters/c1-r72-summary-credit.py` and `quality/counters/c1-r72-landing-controls.py`
- **Function:** `credit(out)` (lines 16–22); documented in `corpus/knowledge/summary-credit-own-detail-r72.md`.
- **Revision:** `a722c60493f24f83429112e9123058835b2cdd82` (round 72).
- **What it proves:** Credit requires the last parsed `MADO_LANDING_COUNTERS_SELFTEST: <p>/<n> assertions passed` summary to report $p < n$ with $n > 0$ **and** the run's own `SELFTEST FAIL` lines to number exactly $n - p$. Rejects bare-failing lines ($0/2$ with no fail lines) and forged summaries ($0/0$ or $p == n$).
- **Duplicate vs. Distinct:** **Distinct capability.** `mado` checks summary arithmetic over general assertion counts. Kama's `tools/round86-mutant-owners.py` couples this arithmetic with an explicit 1:1 attribution of named code mutations (M2..M6) to specific owning test arms, and introduces a strict 6-clause reconciliation (`pass + fail == arms == 34`, `fail_lines == fail == count(FAIL)`, empty stderr, no traceback).

#### Hit 2: `kasegi-shokunin` (Major Discovery — Uncited in Prior Waves)
- **File:** `kasegi-shokunin/corpus/instruments/r45-counters-selftest-c1.py`
- **Function:** Mutant evaluation loop (lines 40–55: `why` regex matching, `WRONG-REASON`, `COLLATERAL`, `FALSE-GREEN`).
- **Revision:** `3874e40eee92b5501a56c1551f78eb87d6df51ea` (round 45).
- **What it proves:** In a synthetic test tree, mutates one limb (R1..R5) at a time and asserts that the mutant is rejected *only* by the targeted limb for the intended reason regex (`why`), reporting `WRONG-REASON` or `COLLATERAL` if an unintended limb fails.
- **Duplicate vs. Distinct:** **Distinct capability.** `kasegi` targets directory-level synthetic artifacts rather than Python source AST/statement mutations, and does not reconcile summary headers against failure lines.

#### Hit 3: `tameshi-shokunin`
- **File:** `tameshi-shokunin/tools/mutate-and-run.sh`
- **Function:** `run_mutants()`
- **Revision:** `55d5a5c6002a048337cc511e1712df87b961d364`.
- **What it proves:** Applies mutations across tools and observes aggregate kill ratios (`CLAIMS_SELFTEST: n/39 pass`).
- **Duplicate vs. Distinct:** **Distinct capability.** Tameshi evaluates fleet-wide aggregate kill ratios without owning-arm isolation or summary cardinality checks.

---

### (c) Pin/Quote Origin Corroboration Against Live Upstream Bytes

#### Hit 1: `mori-shokunin` (Major Discovery — Uncited in Prior Waves)
- **File:** `mori-shokunin/tools/mori-drift-recheck.py`
- **Function:** `run()` (lines 175–230), `load_adjudicator()` (lines 120–160); documented in `corpus/knowledge/source-drift-r65.md`.
- **Revision:** `037c02ca43a5ff36e23e449d0d6bcf50a1f2cbec` (round 66).
- **What it proves:** Takes a fresh live HTTP fetch at re-check time, stamps the verdict with `as-of=YYYY-MM-DDTHH:MM:SSZ`, and compares the fresh live body against the newest committed copy, classifying `fresh` (exact match), `excerpt` (substring/slice), `time-churn` (template timestamp churn), or `receipt-open` (sha256 header matches fresh body).
- **Duplicate vs. Distinct:** **Distinct capability.** `mori` audits documentation drift and timestamp churn on full HTML vendor pages. `kama`'s `tools/round86-pin-origin.py` performs line-range slice extraction (`lines=a-b`) on raw C++/Python engine source code files, verifying byte-for-byte fidelity against committed local anchor extracts while validating anchor SHA-256 headers.

#### Hit 2: `chousa-shokunin`
- **File:** `chousa-shokunin/tools/quote-reopen.py`
- **Function:** `verify()` mode; documented in `corpus/knowledge/quote-reopen-r29.md`.
- **Revision:** `acca24498b8259d179db144a8bb2d44c0935e2c1`.
- **What it proves:** Live fetch of registry URLs, drops HTML tags/scripts/styles, and searches for normalized quote strings in web page text.
- **Duplicate vs. Distinct:** **Distinct capability.** Normalized substring text matching in HTML vs. raw byte-for-byte line-range comparisons of code files.

#### Hit 3: `kake-shokunin`
- **File:** `kake-shokunin/scripts/source_snapshot.py` and `source_recheck.py`
- **Function:** HTTP GET crawling and offline manifest audits.
- **Revision:** `027faf79bba2600c0852f1ec2b51774c868cf321`.
- **What it proves:** `source_recheck.py` is explicitly offline; `source_snapshot.py` crawls full bodies to trace redirect chains.
- **Duplicate vs. Distinct:** **Distinct capability.** Does not verify line-range extracts against upstream source bytes.

---

## 4. Mining `considerthese/`: Proposals & Synthesis

In `kama-shokunin/considerthese/2026-10-26.md`:
- **Proposal 3 (Counter Shortcut Trending):**  
  > "Keep a running count of counters that a shortcut can satisfy: each SCORECARD section now has a 'What `met=True` does not show' paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed."
- **Proposal 4 (Upstream Pin Gap Reporting):**  
  > "Report the pin gap every morning: round 45 already samples llama.cpp at b11897 while the corpus is re-verified at b11889. Reading upstream tags is read-only, so I could add one line per pinned engine (newest tag, how many releases sit above the pin) to each daily file, which gives the next freshness round a dated trigger without anyone running `pin-watch` by hand."

---

## 5. UFO-FSD Connector Move: One Bounded Synthesis

### The Proposed Move
**Formalize a "Freshness Origin Timestamp & Counter Shortcut Robustness Ledger" in the round-86 lesson.**

L1 carries the following bounded synthesis into `corpus/lessons/round-86.md`:

1. **Precedent Attribution & Provenance Boundaries:**
   - **C1:** Explicitly cite `kaidoku-shokunin` (`tools/round-50/c2-record.py` `vis()`) and `chousa-shokunin` (`tools/research-gate.sh` `load_sections()`) for fence/comment exclusion in `SCORECARD.md` self-assessment. Disclaim general Markdown parsing.
   - **C2:** Explicitly cite `mado-shokunin` (`quality/counters/c1-r72-summary-credit.py`) for summary cardinality arithmetic ($n - p == \text{fail\_lines}$) and `kasegi-shokunin` (`corpus/instruments/r45-counters-selftest-c1.py`) for limb/arm mutant attribution. Disclaim fleet-wide mutation testing (owned by `tameshi`).
   - **C3:** Explicitly cite `mori-shokunin` (`tools/mori-drift-recheck.py`) for live fetch-time excerpt/origin verification and `chousa-shokunin` (`tools/quote-reopen.py`) for live URL fetch bounds. Disclaim generic web crawling.

2. **Synthesis of Proposal 4 + `mori`'s Timestamped Origin Standard (Freshness Axis):**
   - Incorporate `mori`'s `as-of=ISO-TIMESTAMP` standard into the C3 documentary receipt, binding the exact moment of live upstream byte equality (2026-11-04T10:56Z).
   - Record the exact upstream release gap at freeze across the 3 pinned engines from `registry/pin-recheck-rows.tsv`:
     * `llama.cpp`: pin `b11755` vs newest `b12111` ($\Delta = 356$ releases, health line shifted +1, byte-identical statement);
     * `sglang`: pin `v0.5.22` vs newest `v0.5.23` ($\Delta = 1$ release, health check lines identical);
     * `vllm`: pin `v0.32.0` vs newest `v0.33.0` ($\Delta = 1$ release, prefix caching lines identical).
   This establishes a mechanical, dated trigger for future freshness rounds.

3. **Synthesis of Proposal 3 (Calibration & Operability Axes):**
   - Incorporate a formal Counter Robustness Tally:
     * Surviving mutants: **2 $\to$ 0** (M5 dropped arm and M6 forged summary killed).
     * Frozen shortcut controls: **28 active arms** (11 C1, 10 C2, 7 C3), all failing closed.
     * False-green elimination: Base tree scores `mismatches=3`, `owners=3/5`, and C3 exits 2; zero shortcut satisfaction.

### Affected Axes
- **Freshness (8 $\to$ holds/improves):** Elevates C3 origin verification from an un-timestamped pass to an auditable, timestamped provenance attestation (`as-of=T`), with explicit release-gap tracking.
- **Calibration (7 $\to$ holds/improves):** Accurately attributes sibling prior art (`kaidoku`, `chousa`, `mado`, `kasegi`, `mori`) and documents the exact boundaries of kama's distinct capabilities.
- **Operability (8 $\to$ holds):** Zero operational overhead; pure standard-library execution; no services, background daemons, or credentials.

### Second-Order Effects
- **Runtime Surface:** Fully standard-library deterministic execution (`argparse`, `re`, `subprocess`, `urllib.request`, `hashlib`).
- **Contract Surface:** Invariant across all frozen predicates (`PREDICATE` strings in `tools/round86-*.py` and `count.py` remain untouched).
- **Substrate Surface:** Read-only access to git objects at `--rev` and public documentation endpoints.
- **Verification Surface:** Self-contained and reproducible via `--selftest` flags and frozen controls.

### Explicit Contradictions
1. **Contract Path vs. Prompt Contradiction:**  
   The seat prompt requests findings written to `.ufo/waves/round-86/w2/CN01OverlapScan.md`. However, the orchestrator contract explicitly commands:  
   *"Write ONLY /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/w2/out/<YOUR-NAME>/ (create it)... Every Report: trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path> and only inside your own out dir."*  
   Writing outside `out/CN01OverlapScan/` violates the hard contract. This contradiction is resolved by writing exclusively to `.ufo/waves/round-86/w2/out/CN01OverlapScan/CN01OverlapScan.md` for L1 to route.
2. **Technique Adoption vs. Province Disjointness:**  
   Techniques (CommonMark fence parsing, cardinality checks, live HTTP GETs) exist across sibling lanes, but their problem domains are strictly disjoint (`kaidoku` = historical atom audits; `chousa` = research records; `mado` = compositor counters; `kasegi` = synthetic tree limbs; `mori` = vendor page drift; `kama` = LLM inference serving engine pins and self-assessment cells). This report explicitly refrains from smoothing this into a scalar score.

### Risks & Mitigations
- **Risk:** Upstream repository force-pushes or tag mutations could invalidate origin hashes.  
  *Mitigation:* C3 anchors code to immutable commit SHAs and release tags, with explicit `unreachable` handling.
- **Risk:** Network transient failures during C3 live fetches.  
  *Mitigation:* C3 implements standard 60s timeouts, user-agent identification, and clean exit-1 reporting without fake passes.

---

## 6. Verification Handoff (For L1 Integrator)

Execute on committed master (`67eddac89f44e768b670301ea0feff06e766f32d`):
1. `python3 tools/round86-rendered-cells.py --selftest` (verifies 11 arms exit 0).
2. `python3 tools/round86-mutant-owners.py --selftest` (verifies 10 arms exit 0).
3. `python3 tools/round86-pin-origin.py --selftest` (verifies 7 arms exit 0).
4. `python3 .ufo/waves/round-86/count.py c1 --repo . --rev master --work /tmp/c1`
5. `python3 .ufo/waves/round-86/count.py c2 --repo . --rev master --work /tmp/c2`
6. `python3 .ufo/waves/round-86/count.py c3 --repo . --rev master --work /tmp/c3`

---

## 7. Required Capability Conclusions

- **Capability (a) Rendered-Markdown Cell Selection:**  
  `distinct` (cite `kaidoku-shokunin/tools/round-50/c2-record.py` and `chousa-shokunin/tools/research-gate.sh`)
- **Capability (b) Mutant $\to$ Owning-Arm Mapping with Summary Cardinality Reconciliation:**  
  `distinct` (cite `mado-shokunin/quality/counters/c1-r72-summary-credit.py` and `kasegi-shokunin/corpus/instruments/r45-counters-selftest-c1.py`)
- **Capability (c) Pin/Quote Origin Corroboration Against Live Upstream Bytes:**  
  `distinct` (cite `mori-shokunin/tools/mori-drift-recheck.py` and `chousa-shokunin/tools/quote-reopen.py`)

---

Report: .ufo/waves/round-86/w2/out/CN01OverlapScan/CN01OverlapScan.md
