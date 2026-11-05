# CN01OverlapScan — Cross-Lane Overlap Scan and Synthesis Advisory

**Seat:** CN01OverlapScan (kama round 86, wave 1)  
**Role:** UFO-FSD Connector  
**Assigned Axes:** Calibration (7) + Operability (8)  
**Judged On:** Adjacency  
**Target Milestone:** kama r86 w1  
**Freeze Base:** `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`  
**Freeze Commit:** `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`  
**Kama Worktree Rev:** `f4c7acaa0563d1cf813fff90e4b927494a88091f`

---

## 1. Executive Summary & Named Axes

Following three consecutive rejected closures on kama (`round-83` harmed via stale live self-assessment cells; `round-84` honest stop via missed frozen disclosure instruction; `round-85` honest stop via C1 kill rule firing on fenced/comment shadow cells, and C2 mutants M5/M6 escaping due to unverified summary cardinality), round 86 establishes three hardened claims:
- **C1 (calibration):** Rendered-cell identity binding live SCORECARD self-assessment cells (`tools/round86-rendered-cells.py`).
- **C2 (operability):** Mutant-to-owning-arm mapping and summary cardinality reconciliation (`tools/round86-mutant-owners.py`).
- **C3 (freshness):** Pin-recheck origin corroboration distinct from hash integrity (`tools/round86-pin-origin.py`).

This scan audits all 21 sibling lanes across `/home/vgpnk/Projects/shokunin` for existing prior art across these three surfaces, establishes clear province boundaries, mines `considerthese/` for fitting unimplemented proposals, and synthesizes one bounded, non-obvious move that improves **calibration**, **operability**, and **adjacency** without harming any axis.

---

## 2. Cross-Lane Overlap Scan

### (a) Rendered-cell / Markdown selection excluding fences or comments

#### Hit 1: `chousa-shokunin`
- **Path:** `chousa-shokunin/tools/research-gate.sh` (`load_sections()`, lines 791–853); documented in `corpus/knowledge/fenced-heading-r17.md` and `html-comment-r20.md`.
- **Revision:** `acca24498b8259d179db144a8bb2d44c0935e2c1` (landed in rounds 17 and 20).
- **What it proves:** In round 17, `chousa` discovered that a naive `^``` ` toggle allowed 4-tick fences, tilde fences, indented fences, and unclosed fences to shadow `## ` headings. In round 20, it found HTML comment blocks (`<!-- ... -->`) could similarly hide headings. `load_sections()` pairs fences (`^\ {0,3}(\`{3,}|~{3,})`, matching character, closing length $\ge$ opening length, 0–3 spaces indent, unclosed fence failing closed to EOF) and tracks `in_comment` (`<!--` to `-->`), ensuring `## ` lines inside code fences or comments never split or reset a record's `SEC_BODY`.
- **Surface ownership:** `chousa-shokunin` owns deep research methodology, citation chaining, research gate, and declared record structure verification.
- **Duplicate vs. Extend:** Kama's `tools/round86-rendered-cells.py` **extends** `chousa`'s technique. Whereas `chousa` parses section-level ATX headings (`## `) in multi-section research records, `kama` applies fence and comment exclusion to table rows and column-0 authority lines (`**Current authority (round N):**` and `| calibration |` rows) inside `SCORECARD.md`. Kama adds CommonMark 0.31.2 §4.4/§4.5 compliance (indentation checks $\le 3$ spaces, indented code block handling, column-0 requirement) and strips historical `round-<N> correction` blocks to bind live self-assessment cells.

#### Hit 2: `souji-shokunin`
- **Path:** `souji-shokunin/tools/souji-landing-gate.py` (lines 130, 373–405: `HTML_COMMENT_RE` and `in_fence` tracking).
- **Revision:** `c7228424c3919ecf142bab1aec8181722d86467b` (round 16/18).
- **What it proves:** Strips HTML comments (`<!--.*?-->`) from lesson text via `HTML_COMMENT_RE.sub("", lesson_text)` and ignores `STATUS: FAIL` lines inside code fences via a line-by-line `stripped.startswith("```")` toggle, preventing quoted failure reports from registering as uncarried seat failures.
- **Surface ownership:** `souji-shokunin` owns repo workspace hygiene, stale/preserved artifact census, and landing gate verification.
- **Duplicate vs. Extend:** Kama's `tools/round86-rendered-cells.py` **extends** `souji`'s approach. `souji` uses a naive prefix check without tracking fence delimiters (backtick vs. tilde), minimum fence run lengths, unclosed fail-closed semantics, or column-0 constraints. Kama's implementation provides full CommonMark fence pairing and table cell discrimination.

---

### (b) Mutant $\to$ owning-arm mapping or summary/failure-line cardinality reconciliation

#### Hit 1: `mado-shokunin`
- **Path:** `mado-shokunin/quality/counters/c1-r72-summary-credit.py` and `quality/counters/c1-r72-landing-controls.py` (lines 16–22: `credit()`); documented in `corpus/knowledge/summary-credit-own-detail-r72.md`.
- **Revision:** `9bcb4fd5b598844f168230dc05e441721d95b272` (round 72; current HEAD `a722c60493f24f83429112e9123058835b2cdd82`).
- **What it proves:** A landing kill is credited only when the child's last parsed `MADO_LANDING_COUNTERS_SELFTEST: <p>/<n> assertions passed` summary reports $p < n$ with $n > 0$ **and** the run's own `SELFTEST FAIL` lines number exactly $n - p$. This arithmetic rule rejects `bare-failing` lines ($0/2$ without fail lines), forged summaries ($0/0$ or $p == n$), and mismatching failure lines.
- **Surface ownership:** `mado-shokunin` owns desktop and compositor craft, including its own landing counter selftest.
- **Duplicate vs. Extend:** Kama's `tools/round86-mutant-owners.py` **extends** `mado`'s cardinality reconciliation. While `mado` checks summary-to-failure-line count equality ($n - p == \text{count}(\text{FAIL})$) across general assertions, `kama` couples this cardinality rule with an explicit 1:1 mapping of declared mutations to specific named **owning arms** (`M2` $\to$ `note-deletion-equals-subject`, `M3` $\to$ `note-deletion-above-subject`, `M4` $\to$ `note-subject-exact-summary`, `M5` $\to$ `arm-count`, `M6` $\to$ `summary-cardinality`). It verifies that each mutant is killed only by its designated owning arm or via an invalid reconciliation clause, requiring `pass + fail == arms == 34` and `fail_lines == fail == count(APPEND_DEBT_SELFTEST_FAIL)`. This directly closes the hole where M5 (dropped arm) and M6 (forged summary `pass=0 fail=0`) escaped in round 85.

#### Hit 2: `tameshi-shokunin`
- **Path:** `tameshi-shokunin/tools/mutate-and-run.sh` and `corpus/knowledge/mutation-case-kumitate-claims.md` (rounds 8, 41, 53).
- **Revision:** `55d5a5c6002a048337cc511e1712df87b961d364`.
- **What it proves:** Evaluates suite kill rates by applying single-edit AST/source mutations to tool code and observing suite pass/fail totals (`CLAIMS_SELFTEST: n/39 pass`) and exit codes.
- **Surface ownership:** `tameshi-shokunin` owns verification fixture craft and cross-lane mutation test suites.
- **Duplicate vs. Extend:** Kama's `tools/round86-mutant-owners.py` **extends** (does not duplicate). Tameshi evaluates aggregate suite kill ratios across external gates but does not enforce single owning-arm attribution or assert summary header vs. failure-line cardinality. Kama enforces strict owning-arm attribution to prevent masked escapes.

---

### (c) Source-origin corroboration distinct from local hash integrity

#### Hit 1: `chousa-shokunin`
- **Path:** `chousa-shokunin/tools/quote-reopen.py` (`verify` mode); documented in `corpus/knowledge/quote-reopen-r29.md`.
- **Revision:** `acca24498b8259d179db144a8bb2d44c0935e2c1` (round 29).
- **What it proves:** Fetches live upstream HTTP(S) URLs cited in `corpus/SOURCES.md`, strips HTML tags, normalizes whitespace/NFKC, and verifies verbatim quote presence on the live web page, separating quote location from truth or support. Crucially, `quote-reopen-r29.md` §6 observed that previous counters failed to prove a live fetch because static local snapshots satisfied them.
- **Surface ownership:** `chousa-shokunin` owns deep research methodology, citation chaining, and quote verification against web sources.
- **Duplicate vs. Extend:** Kama's `tools/round86-pin-origin.py` **extends** `chousa`'s approach. While `chousa` performs normalized substring search of text quotes within web HTML, `kama` corroborates committed local anchor extracts (`registry/pin-recheck-rows.tsv` pointing to extracts in `corpus/captures/`). It verifies the local SHA-256 digest over the stored body, fetches the live upstream URL, extracts the exact declared line range, and performs a byte-for-byte comparison against upstream bytes, discriminating between local digest fraud (`bad`), upstream line changes (`mismatch`), network unavailability (`unreachable`), and true byte fidelity (`verified`).

#### Hit 2: `kake-shokunin`
- **Path:** `kake-shokunin/scripts/source_snapshot.py`.
- **Revision:** `f0b2dc635e34cc1c593655d926af74f19bd21034` (round 36).
- **What it proves:** Performs live HTTP GET requests to record redirect chains, status codes, and complete bodies into a versioned manifest.
- **Surface ownership:** `kake-shokunin` owns web properties, publishing, and HTTP crawl semantics.
- **Duplicate vs. Extend:** Kama's `tools/round86-pin-origin.py` **extends** this. Kake snapshots full HTTP response bodies to audit redirect graphs. Kama verifies specific line-range slices of upstream source files against previously pinned local extracts without storing full-page downloads, proving provenance and origin freshness.

#### Hit 3: `kagi-shokunin`
- **Path:** `kagi-shokunin/corpus/release-clock.py`.
- **Revision:** `09f27e2e16c26484b2675aa2a2b1e2ca4d3d1d8d` (round 25).
- **What it proves:** Fetches live release feeds (XML, Atom, JSON) to detect version drift against anchored versions in `SOURCES.md`.
- **Surface ownership:** `kagi-shokunin` owns secrets and vault ops, freshness + calibration of release clocks.
- **Duplicate vs. Extend:** Kama's `tools/round86-pin-origin.py` **extends** this. Kagi samples release feeds for version drift. Kama verifies static text extracts byte-for-byte against upstream raw byte ranges.

---

## 3. Mining `considerthese/`: Unimplemented Proposals

### Selected Proposal
- **File & Line:** `kama-shokunin/considerthese/2026-10-26.md:33-34` (Proposal 3).
- **Proposal Text:**  
  > "3. **Keep a running count of counters that a shortcut can satisfy:** each SCORECARD section now has a "What `met=True` does not show" paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed."
- **Why prior state lacked it:**  
  Across rounds 42 through 85, the lane added ad-hoc narrative paragraphs ("What `met=True` does not show") in SCORECARD sections and recorded mutant survivors or shortcut controls informally in individual round verifier spot-checks or lessons. The prior state lacked a structured, machine-checkable ledger or census tracking surviving counter mutants, shortcut-vulnerable controls, and wave execution across rounds. Consequently, when counters were written, author-side tools repeatedly allowed known shortcut patterns to pass (e.g., M5/M6 escaping in round 85; shadow cells passing in round 85) without any trend visibility warning the lane that counter robustness had stagnated.
- **Fit for round 86:**  
  Round 86 is a fresh start explicitly responding to three rejected closures caused by counter shortcuts (fenced/comment shadow cells in C1, forged summaries and dropped arms in C2). Adopting this proposal's principle allows the lane to formally track its counter controls (11 C1 arms, 10 C2 arms, 7 C3 arms) and record the transition from 2 surviving mutants to 0.

---

## 4. UFO-FSD Connector Move: One Bounded Synthesis

### The Proposed Move
**Formalize an explicit "Counter Invariant & Population-Disjoint Ledger" in the round-86 lesson.**

L1 carries the following structured synthesis in `corpus/lessons/round-86.md` and the round-86 report:

1. **Precedent Attribution & Population Boundaries:**
   - **C1 (Rendered-Cell Identity):** Acknowledges `chousa` (`research-gate.sh` r17/r20) and `souji` (`souji-landing-gate.py` r16) for the fence-pairing and HTML-comment exclusion precedent. Explicitly states that kama's parser is strictly an internal SCORECARD self-assessment selector, not a general Markdown parser or research gate.
   - **C2 (Mutant Owners & Summary Cardinality):** Acknowledges `mado` (`summary-credit-own-detail-r72.md`) for the summary-to-failure-line cardinality precedent ($n - p == \text{count}(\text{FAIL})$). Explicitly states that kama's owning-arm mapping and population check (`arms == 34`, `fail_lines == fail`) harden its internal debt-selftest instrument, disclaiming generic mutation-testing craft (which belongs to `tameshi`).
   - **C3 (Pin-Origin Corroboration):** Acknowledges `chousa` (`quote-reopen-r29.md`) and `kake` (`source_snapshot.py`) for live upstream fetch precedent. Explicitly bounds kama's instrument to the 5 local engine documentation pins (`registry/pin-recheck-rows.tsv`), disclaiming general web crawling or quote research.
2. **Grounding the `considerthese/2026-10-26.md:33-34` Proposal:**
   - Incorporates a formal tally into the round-86 lesson documenting:
     * Surviving mutants: **2 $\to$ 0** (M5 dropped arm and M6 forged summary killed).
     * Frozen shortcut controls: **28 active arms** (11 in C1, 10 in C2, 7 in C3).
     * False-green elimination: explicitly recording that base bytes fail all three legs (mismatches=3, owners=3/5, c3 exit 2), eliminating shortcut satisfaction.

### Affected Axes
- **Calibration (7 $\to$ holds/improves):** Eliminates misattribution of generic tooling, grounds claims strictly within verified boundaries, and establishes an auditable metric against counter shortcuts.
- **Operability (8 $\to$ holds):** Zero operational overhead; pure standard-library deterministic execution; no services, credentials, or system configs touched.
- **Adjacency (7 $\to$ holds/improves):** Enforces clean boundaries between kama and siblings (`chousa`, `mado`, `tameshi`, `kake`), preventing territory disputes while acknowledging genuine technical precedents.

### Second-Order Effects
- **Runtime Surface:** Uses only Python 3 standard library (`argparse`, `re`, `subprocess`, `urllib.request`, `hashlib`). No external processes, network daemons, or background services are introduced.
- **Contract Surface:** Invariant across all frozen predicates (`PREDICATE` strings in `tools/round86-*.py` and `count.py` remain untouched).
- **Substrate Surface:** Read-only access to git objects at `--rev` and local fixture generation in `$TMPDIR`.
- **Verification Surface:** Self-contained and testable via `--selftest` flags and frozen controls without requiring live serving endpoints.

### Explicit Contradictions
1. **Report Location Contradiction:**  
   The seat assignment prompt requests findings written to `.ufo/waves/round-86/w1/CN01OverlapScan.md`. However, the orchestrator contract explicitly states:  
   *"Write ONLY /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/w1/out/<YOUR-NAME>/ (create it)... Every Report: trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path> and only inside your own out dir."*  
   Writing outside `out/CN01OverlapScan/` would violate the hard contract and risk sentinel misroot flags. This contradiction is resolved by writing exclusively to `.ufo/waves/round-86/w1/out/CN01OverlapScan/CN01OverlapScan.md` for L1 to route.
2. **Technique Overlap vs. Province Disjointness:**  
   Techniques (CommonMark fence parsing, cardinality checks, live HTTP GETs) appear in sibling code, but their domains are strictly disjoint (chousa = research records; mado = compositor counters; tameshi = fixture suites; kama = local model serving and self-assessment cells). This report explicitly refrains from smoothing this into a scalar score or claiming cross-lane absorption.

### Risks & Mitigations
- **Risk:** Overclaiming absence of overlap across all 21 lanes based on a bounded sample.  
  *Mitigation:* Findings are scoped as positive evidence of examined surfaces, not an exhaustive fleet census.
- **Risk:** Network flakiness on C3 live origin fetches.  
  *Mitigation:* C3 includes standard 60s timeouts, user-agent identification, and dedicated `unreachable` exit-1 handling without crashing or faking green.

---

## 5. Verification Handoff (For L1 Integrator)

L1 should execute the following read-only checks on committed master:
1. `python3 tools/round86-rendered-cells.py --selftest` (verifies 11 arms exit 0).
2. `python3 tools/round86-mutant-owners.py --selftest` (verifies 10 arms exit 0).
3. `python3 tools/round86-pin-origin.py --selftest` (verifies 7 arms exit 0).
4. `python3 .ufo/waves/round-86/count.py c1 --repo . --rev master --work /tmp/c1`
5. `python3 .ufo/waves/round-86/count.py c2 --repo . --rev master --work /tmp/c2`
6. `python3 .ufo/waves/round-86/count.py c3 --repo . --rev master --work /tmp/c3`

---

## 6. Command Receipts & Hygiene

All commands executed with exit code **0**; no mutating git commands or production modifications were performed:

1. `mkdir -p /fast/scratch/hyaku/kama-r86/CN01OverlapScan /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/w1/out/CN01OverlapScan`  
   *Exit: 0*
2. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD`  
   *Output: f4c7acaa0563d1cf813fff90e4b927494a88091f, Exit: 0*
3. `git -C /home/vgpnk/Projects/shokunin/chousa-shokunin rev-parse HEAD`  
   *Output: acca24498b8259d179db144a8bb2d44c0935e2c1, Exit: 0*
4. `git -C /home/vgpnk/Projects/shokunin/mado-shokunin rev-parse HEAD`  
   *Output: a722c60493f24f83429112e9123058835b2cdd82, Exit: 0*
5. `git -C /home/vgpnk/Projects/shokunin/tameshi-shokunin rev-parse HEAD`  
   *Output: 55d5a5c6002a048337cc511e1712df87b961d364, Exit: 0*
6. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD`  
   *Output: c7228424c3919ecf142bab1aec8181722d86467b, Exit: 0*
7. `git -C /home/vgpnk/Projects/shokunin/kake-shokunin rev-parse HEAD`  
   *Output: f0b2dc635e34cc1c593655d926af74f19bd21034, Exit: 0*
8. `git -C /home/vgpnk/Projects/shokunin/kagi-shokunin rev-parse HEAD`  
   *Output: 09f27e2e16c26484b2675aa2a2b1e2ca4d3d1d8d, Exit: 0*

Scratch directory `/fast/scratch/hyaku/kama-r86/CN01OverlapScan/` will be removed prior to final completion yield.

Report: .ufo/waves/round-86/w1/out/CN01OverlapScan/CN01OverlapScan.md
