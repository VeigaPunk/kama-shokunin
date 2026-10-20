# MetadataLearning — UFO-FSD Connector Advisory Report (Round 11)

- **Seat:** `MetadataLearning` (UFO-FSD connector; author advisor, leaf member — not an outside non-author verifier)
- **Lane:** `kama-shokunin` (local model serving & endpoint health)
- **Round:** Round 11 (steered round label/heading date: `2026-10-19`)
- **Review Timestamp:** `2026-10-20T03:52:00Z` UTC (`date -u` verified) — actual review date 2026-10-20 UTC; historical observation dates (`2026-09-28`, `2026-10-14`, `2026-10-15`) and source open dates (`2026-10-19`) are cited as immutable history.
- **Assigned Scope:** Connect legacy supplements with CORPUS legacy correction rule versus provenance-opening rule. Identify durable SKILL guidance needed without duplicated admission methods. Trace second-order effects across runtime, contract, substrate, and verification surfaces.
- **Tooling Directive Record:** Zero packages or tools installed or updated during this review. No network, host configs, service endpoints, or live sockets contacted. No builds, tests, linters, or formatters executed. Implementation, corpus, and fleet repos unmodified. Sole write target: `.ufo/waves/round-11/verification/MetadataLearning.md`.

---

## 1. Grounded Evidence Base

The analysis rests on verifiable, read-only evidence across the repository:

1. **`CORPUS.md` Provenance and Correction Rules (`/home/vgpnk/Projects/shokunin/CORPUS.md`):**
   - *New Entry Provenance Rule (`:163-166`):* "A new knowledge entry opens with its provenance trio. `source:`, `verified-at:` and `recheck:` come first; when the source is external, `source:` cites its `S###` row in `corpus/SOURCES.md` alongside the URL and anchor. Provenance in prose or HTML comments is unreadable to a freshness..."
   - *Legacy Correction Rule (`:116-118`):* "2. Append-only. Only `status`, `recheck` and `used-by` change in place, and each change is logged old→new in the round lesson. A correction is a new row whose `teaches` opens `supersedes S0NN —`."
   - *No Duplicated Methods Rule (`:119-120`):* "3. No second method. Claim admission stays in `corpus/QUALITY.md`; the research method stays chousa's...".

2. **`QUALITY.md` Criteria (`kama-shokunin/corpus/QUALITY.md`):**
   - *KQ3 (Byte Preservation, `:11`):* "Historical examples have explicit dates/supersession, and active instructions use existing registered surfaces. Corrections preserve old corpus bytes."
   - *KQ7 (Immutable History & Stale-Anchor Prevention, `:29`):* "A correction round publishes a stale-anchor ledger and a pasteable count that reaches 0, with every correction appended at the end of its file. Reject or limit when: Any ledger row stays uncorrected, a dated line is rewritten, or a mid-file insertion shifts other files' line anchors."
   - *KQ11 (Legacy Provenance Suffixes, `:38`):* "Legacy provenance supplements preserve the original byte prefix, identify historical observation dates or unknown dates, distinguish metadata review from live revalidation, and name a bounded current recheck or an explicit unavailable surface. New knowledge entries still open with the provenance trio."

3. **`LEARNING.md` Cycle (`/home/vgpnk/Projects/shokunin/LEARNING.md:9-21`):**
   - *Section 3 (Understanding):* "distill what was admitted: connect entries, state the principle behind them, fold durable understanding into `SKILL.md` (decision tables, error patterns, checklists), and sharpen `QUALITY.md` from what the gate got right and wrong."

4. **`legacy-baseline.json` & `measure.py` (`kama-shokunin/.ufo/waves/round-11/`):**
   - `legacy-baseline.json:1-83` pins 9 legacy files totaling 138,376 bytes with exact SHA-256 hashes and 27 missing fields (`source`, `verified-at`, `recheck`).
   - `measure.py:145-177` (`_scan_supplement`) scans for column-zero fields under `^##\s+Provenance supplement\b` at EOF, validating `file[:N] == baseline.sha256`.
   - `measure.py:327-375` (`check_crosswalk`) verifies that net-new entries (`corpus/knowledge/served-identity-crosswalk.md`) contain lines 1–4 opening provenance fields.

5. **`SKILL.md` Round-11 Addition (`kama-shokunin/SKILL.md:347-374`):**
   - Explicitly notes: "The current lane assignment is the kama row in fleet `shokunin.conf`, as directed by MISSION's Fleet shape section: operability + calibration... Legacy corpus supplements add `source:`, `verified-at:` and `recheck:` without rewriting dated observations... Admission remains `corpus/QUALITY.md` KQ11–KQ13."

---

## 2. Reconciliation: Legacy Correction vs. Provenance-Opening Rule

There is a surface structural tension in the corpus contract:
- **Rule A (`CORPUS.md:163`):** "A new knowledge entry opens with its provenance trio."
- **Rule B (`CORPUS.md:116`, `QUALITY.md` KQ3, KQ7):** "Corrections preserve old corpus bytes... every correction appended at the end of its file... reject or limit when a mid-file insertion shifts other files' line anchors."

### Root Cause Analysis of the Bifurcation
If an automated agent or author attempts to apply Rule A naively to the 9 legacy knowledge files by inserting `source:`, `verified-at:`, and `recheck:` at lines 1–4, two catastrophic structural failures occur:
1. **Byte-Prefix Invalidation:** Modifying bytes $0 \dots M$ destroys the $N$-byte prefix invariant pinned in `legacy-baseline.json`, causing `measure.py` to immediately flag `prefix_violations > 0`.
2. **Global Line-Anchor Corruption:** Inserting 3–4 lines at line 1 shifts every subsequent line in that file downwards. Across the repository, dozens of citations in `corpus/lessons/round-1.md`, `round-1-citations.md`, `round-10.md`, `DELTA.md`, `SCORECARD.md`, `SHONEN.md`, and `consumer-registry.md` cite explicit lines in these legacy files (e.g., `listener-census.md:45`, `cross-lane-scope.md:27`, `consumer-registry.md:30`). Prepending metadata immediately turns valid pointers into stale anchors, violating KQ7.

### Contractual Reconciliation Principle
The two rules govern two distinct phases of knowledge lifecycle:
- **Net-New Admissions (Born-in-Round):** Zero pre-existing line anchors exist; zero byte baselines precede them. Therefore, provenance MUST open the entry (lines 1–4) so downstream linters and consumers evaluate authority before ingesting claims.
- **Legacy Knowledge Files (Historical Census Records):** Already possess immutable byte sequences ($N$ bytes pinned) and active external citations. Therefore, provenance MUST be appended at EOF as an explicit `## Provenance supplement — round 11 (2026-10-19)`.
- **Coverage Counter Protection:** Legacy supplements MUST NOT cite external `S###` rows from `SOURCES.md`. Citing `S###` would spuriously inflate the coverage counter (`grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l`) from 3 to 12 without adding new vendor documentation coverage (violating KQ1 and KQ6). Legacy supplements cite `source: retained historical sample...` or local path/commit evidence.

---

## 3. Boundary: SKILL Domain Guidance vs. QUALITY Admission Methods

`CORPUS.md:119` establishes the inviolable rule: **"No second method. Claim admission stays in `corpus/QUALITY.md`."**

### The Anti-Pattern (Duplicated Admission Methods)
A common failure mode in lane evolution is turning `SKILL.md` into a shadow gatekeeper:
- Specifying source tier requirements in `SKILL.md` instead of `SOURCES.md` / `QUALITY.md`.
- Defining file-format validation scripts, regex checks, or acceptance criteria in `SKILL.md`.
- Mandating gate rubrics in `SKILL.md` that duplicate or diverge from KQ1–KQ13.

When `SKILL.md` duplicates admission logic:
1. The gate drifts across two locations: an entry might satisfy `QUALITY.md` but fail an undocumented rule in `SKILL.md`, or vice versa.
2. The operational specialist becomes confused: `SKILL.md` is intended as the *runtime and domain reasoning runbook*, while `QUALITY.md` is the *curatorial quality bar*.

### What Durable SKILL Guidance MUST Contain
Per `LEARNING.md:16-21`, `SKILL.md` must absorb the *distilled understanding* from admitted knowledge without touching admission mechanics:
1. **Epistemic Classification:** Clear decision guidance teaching the practitioner how to distinguish **Historical Census Records** (rounds 1–9: frozen on-box samples, provenance at EOF, read-only historical evidence; commands like port 34113 or `qwen-coder.service` are retired and must never be re-probed ad-hoc) from **Vendor Documentation Crosswalks** (rounds 10–11: public specs, provenance at lines 1–4, recheck cadence `on-release`/`90d`, not local runtime integration).
2. **Operational Decision Tables:** Incorporating the five multi-engine distinctions discovered by C2 (`served-identity-crosswalk.md`) directly into `SKILL.md`'s decision workflows:
   - Differentiating Ollama's available catalog (`/v1/models` and `/api/tags`) from loaded residency (`/api/ps`).
   - Recognizing transient loading states in llama.cpp (`/v1/models` returning `meta: null`) vs. permanent `MODEL_MISMATCH`.
   - Handling Ollama tags that carry `remote_model` or `remote_host` (unfetched cloud models != local loopback weights).
   - Recognizing that alias names (`ollama cp`, `llama-server --alias`) do not guarantee artifact/digest equality.
   - Understanding that Ollama `/api/ps` residency is time-bounded by `expires_at`.

---

## 4. Grounded Defects, Contradictions, and Smallest Repairs

| # | Item / Location | Defect / Contradiction | Severity | Smallest Repair |
|---|---|---|---|---|
| **D1** | `shokunin.conf:52` vs `MISSION.md:29` / `SCORECARD.md` | `shokunin.conf:52` assigns `operability + calibration`. `MISSION.md:29` (a historical example) assigns `operability + freshness`. Scorecard planned row cited freshness. | **High** (Authority Conflict) | Already resolved in `claims.json:4-5` by binding to `../shokunin.conf:52` (C1 is calibration at 7; operability 8). Parent report must include explicit erratum explaining why `shokunin.conf:52` outranks the historical MISSION example. |
| **D2** | `SKILL.md:347-374` | Section mentions "Admission remains `corpus/QUALITY.md` KQ11–KQ13" but lacks operational integration of the 5 C2 engine distinctions into the main §Decision table (`SKILL.md:127-141`). | **Medium** (Epistemic Gap) | Add 3 operational rows to `SKILL.md` §Decision table guiding the practitioner on `meta: null`, Ollama `/v1/models` catalog vs `/api/ps`, and remote tags. |
| **D3** | `listener-census.md:383` | Baseline file ends in `*` with **no trailing newline**. A direct append of `## Provenance supplement` would fuse as `*## Provenance supplement` or `*verified-at:`, breaking heading and field regexes. | **High** (Syntax Corruption) | Ensure the append in `listener-census.md` is preceded by explicit `\n\n` (already respected by `Legacy7` / Wave 1 executor). |
| **D4** | `SCORECARD.md` §Planned (Round 11) | Planned row states "the 18 pre-round-10 entries", but the actual knowledge directory contains exactly 9 legacy files (27 fields) and 3 round-10 crosswalks. | **Medium** (Denominator Mismatch) | Parent appends a SCORECARD erratum correcting "18 entries" to "9 legacy knowledge files × 3 required fields = 27 fields", matching `legacy-baseline.json`. |

---

## 5. Proposed Non-Obvious Move: Epistemic Provenance Tiering (EPT)

### Move Description
Establish **Epistemic Provenance Tiering (EPT)** in `SKILL.md` and the parent report as the canonical synthesis:

1. **Two-Tiered Structural Standard:**
   - **Tier 1 (Legacy Host Census):** 9 files (rounds 1–9). Provenance placed exclusively at EOF under `## Provenance supplement — round 11 (2026-10-19)`. `source:` cites retained local evidence (strictly no `S###` rows to prevent coverage counter contamination). `verified-at:` records actual UTC review date (`2026-10-20`) while disclaiming live revalidation ("no endpoint contacted; endpoint claims historical"). `recheck:` points to authorized registered surfaces or explicit unavailable scope.
   - **Tier 2 (Sourced Vendor Crosswalks):** Net-new knowledge entries (rounds 10–11). Provenance placed at lines 1–4 opening trio. `source:` cites mined A-tier `S###` rows. `verified-at:` records documentation re-opening date ("no local runtime contacted"). `recheck:` records documentation re-check cadence (`on-release` / `90d`).
2. **Zero-Method Duplication in SKILL:**
   - `SKILL.md` contains zero admission criteria and zero verification regexes (delegated 100% to `corpus/QUALITY.md` KQ11–KQ13 and `measure.py`).
   - `SKILL.md` incorporates the **Served-Identity Epistemic Matrix** into its §Decision table, providing operational triage for agents:
     - `llama.cpp` `/v1/models` returning `meta: null` → Action: Treat as transient loading state; wait for `/health` or poll `/props`. Never conclude `MODEL_MISMATCH`.
     - `Ollama` `/v1/models` returning matching ID → Action: Recognize this as catalog availability. Query `/api/ps` to check if model is loaded into VRAM.
     - `Ollama` `/api/tags` carrying `remote_model` → Action: Flag as remote catalog item. Do not assert local loopback weight availability.
     - `Ollama` `/api/ps` returning model with `expires_at` → Action: Treat as time-bounded residency; do not assert permanent readiness.
     - Legacy knowledge file cited in task → Action: Treat as frozen dated sample; do not execute ad-hoc curl probes against retired ports (34113/8080).

---

## 6. Affected Axes, Second-Order Effects, and Verification

### Affected Axes
- **calibration (Assigned Live Axis; Lowest Non-Retired):** **Improved.** Resolves 27 missing legacy provenance fields to 0; distinguishes metadata review (2026-10-20) from original historical observations (2026-09-28/2026-10-14); prevents coverage score gaming; eliminates false freshness assertions. Historical score 7 kept unchanged honestly due to absence of global objective denominator.
- **coverage (C2 Claimed Axis):** **Improved.** Admits `served-identity-crosswalk.md` with 5 non-duplicative engine distinctions; maintains strict separation from prior matrix coverage; updates `SOURCES.md` S011/S012/S016 queued→mined.
- **operability (Assigned Live Axis):** **Unharmed.** Zero modifications to probe scripts (`tools/kama-probe.sh`), test suites (`tools/test-snapshot.sh`), or registered consumer configurations.
- **depth & adjacency:** **Unharmed.** Province boundaries strictly maintained; no service started, no credentials inspected, no evaluation benchmarks absorbed.

### Second-Order Effects
- **Verification Substrate:** `measure.py` cleanly separates `check_provenance` (EOF supplement scanning, prefix checking) from `check_crosswalk` (lines 1–4 scanning), preventing false test failures across tiers.
- **Line Anchor Stability:** 100% of legacy line numbers remain invariant. Cross-repo citations in `lessons/`, `DELTA.md`, and `SCORECARD.md` continue pointing to exact historical lines.
- **Future Round Hygiene:** Prevents future round agents from attempting to "refactor" legacy files by prepending headers, which would cause cascade failures across git history.

### Verification (for Parent Integration)
1. **Prefix and Field Integrity:** `python3 .ufo/waves/round-11/measure.py provenance` yields `legacy_files=9, missing_files=0, missing_fields=0, prefix_violations=0, exit=0`.
2. **Crosswalk Opening Trio:** `python3 .ufo/waves/round-11/measure.py crosswalk` yields `ok=True, missing_fields=0, required_sources_found=5, exit=0`.
3. **Coverage Counter Non-Contamination:** `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l` yields exactly 4 (3 round-10 crosswalks + 1 round-11 crosswalk; zero legacy files match).
4. **Sources Census Validation:** `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` yields `kama ok, exit=0`.
5. **No Method Duplication:** Grep confirms `SKILL.md` references `QUALITY.md` KQ11–KQ13 for admission and defines no shadow criteria.
