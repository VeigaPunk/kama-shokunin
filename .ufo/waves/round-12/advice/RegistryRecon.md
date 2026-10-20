# Round 12 — RegistryRecon (SOURCES.md Structure, Census & Boundary Analysis)

**Seat:** `KamaR12.RegistryRecon` (scout)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Target:** Read `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` full relevant sections. Map current row count/navigation/date errors and immutable-cell constraints for D2, D4. Identify structural edge risks.  
**Policy:** Subagent leaf scout report only. No verification runs, no builds/tests/linters/formatters, no subagent dispatch. Unrun != pass; name checks for L1.

---

## 1. Document Geometry and Section Breakdown

`corpus/SOURCES.md` has 66 lines and strictly adheres to the four-section structure defined under `SOURCES-CONTRACT-v1`:

1. **Header / Contract Prelude (lines 1–8):**
   - Declares `Contract: SOURCES-CONTRACT-v1 (kaika, 2026-10-19, frozen)`.
   - Links claim admission to `QUALITY.md`.
   - Defines scoped source tiers.
   - Contains the historical opening sentence: `"Every row was opened in round 10 (2026-10-19); the round lesson lessons/round-10.md §Gate carries each row's URL, access date and quote."` (lines 6–7).
2. **`## Registry` (lines 9–44):**
   - Line 11: Column header row (`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`).
   - Line 12: Column separator row (`|---|...|`).
   - Lines 13–43: 31 source rows (`S001` to `S031`).
3. **`## Paths` (lines 45–51):**
   - Defines 4 curated study paths: Health & readiness (line 47), Served identity (line 48), Serving observability (line 49), GGUF & quantization boundary (line 50).
   - Line 48 contains prospective/historical text: `"Served identity (next entry, K02) — S016 → S001 → S010 → S011 → S012: the generic model-list shape first..."`.
4. **`## Search log` (lines 52–58):**
   - Documents chronological search passes: 2026-10-19 ART dossier re-open (line 54), 2026-10-19 ART leads (line 55), 2026-10-19 community claims sweep (line 56), and 2026-10-20 UTC round-11 served-identity re-open (line 57).
5. **`## Leads (unopened)` (lines 59–66):**
   - Lines 61–62: 2 historical unopened leads (Reddit r/ollama Prometheus metrics, Ollama health/readiness route).
   - Lines 64–66: Appended Round 12 correction prose addressing verifier defects D2 and D4.

---

## 2. Row Count and Census Mapping

Static inspection of the registry table (lines 13–43) yields the following deterministic counts:

| Dimension | Count | Details / Identifiers |
|---|---|---|
| **Total Rows** | **31** | `S001` through `S031` |
| **Tier A** | 28 | `S001`–`S026`, `S030`, `S031` |
| **Tier B** | 0 | None |
| **Tier C** | 3 | `S027`, `S028`, `S029` (community-sourced issues/discussions) |
| **Status: mined** | 21 | `S001`–`S020`, `S031` |
| **Status: queued** | 5 | `S021`, `S022`, `S023`, `S025`, `S029` |
| **Status: rejected**| 5 | `S024`, `S026`, `S027`, `S028`, `S030` |
| **Status: invalid** | 0 | None |
| **Missing used-by** | 0 | All 21 `mined` rows cite existing paths in `corpus/knowledge/`; all queued/rejected cite `—` |

### Round 12 Census Boundary:
- `S032` is **absent** from the file. Per the Round 12 wave spec, `SourceCorrections` was strictly instructed not to add `S032`; L1 Main owns row additions following gate verification.
- Claim C1 is strictly calibration-focused (correcting the frozen SOURCES snapshot mismatch $1 \to 0$ at calibration $7 \to 7$, $\Delta 0$). No expansion claim is asserted for Round 12.

---

## 3. Mapping Navigation & Date Errors (D2, D4)

### 3.1 Date and Gate Pointer Inconsistencies (D2)
- **Observed Defect in Header (lines 6–7):**  
  `"Every row was opened in round 10 (2026-10-19); the round lesson lessons/round-10.md §Gate carries each row's URL, access date and quote."`
  - In reality, row `S031` (line 43) carries `opened: 2026-10-20` (Round 11 review date).
  - `lessons/round-10.md` §Gate documents quotes only for `S001`–`S030`. The quote and gate admission for `S031` reside in `lessons/round-11.md` §Gate and are corroborated in `corpus/lessons/round-11-verifier-spotcheck.md` §Outside discernment spot-check.
- **Resolution via Appended Prose (line 64):**  
  The appended note clarifies that lines 6–7 describe rows `S001`–`S030` only, while `S031` was opened on 2026-10-20 (UTC) during Round 11.

### 3.2 Navigation and Path Inconsistencies (D2)
- **Observed Defect in Paths Section (line 48):**  
  `"Served identity (next entry, K02) — S016 → S001 → S010 → S011 → S012: the generic model-list shape first..."`
  - Calling K02 the `"(next entry, K02)"` is stale prospective text written prior to K02's implementation. K02 landed in Round 11 as `corpus/knowledge/served-identity-crosswalk.md` (cited in `used-by` for `S001`, `S010`, `S011`, `S012`, `S016`, and `S031`).
  - The path sequence stops at `S012`, omitting `S031` (the crucial caveat row for remote model entries on `/api/tags`).
- **Resolution via Appended Prose (line 64):**  
  The appended note records that `(next entry, K02)` is retained navigation text and that the crosswalk is already landed and present.

### 3.3 Inference vs. Direct Fact & Registry Supersession (D4)
- **Observed Defect in Row S031 (line 43):**  
  The `teaches` cell reads:  
  `"supersedes S011 — available inventory may include remote_model/remote_host; list membership does not prove local residency; remote_model names the upstream model and remote_host the upstream Ollama URL."`
  - The conclusion that *"list membership does not prove local residency"* is an analytical inference (`[INFERENCE]`) derived from `ModelSummary.remote_model` and `remote_host` OpenAPI property descriptions, not an explicit assertion by upstream documentation (which still states *"Summary information for a locally available model"* in its summary).
  - The phrase `"supersedes S011"` represents **lane-registry supersession** under `SOURCES-CONTRACT-v1` (narrowed to the local-residency implication), not an upstream withdrawal or change of Ollama's documented text.
- **Resolution via Appended Prose (line 66):**  
  The appended prose explicitly tags the non-residency conclusion as `[INFERENCE]`, notes the upstream summary wording, and clarifies that supersession is lane-internal registry supersession.

---

## 4. Immutable-Cell Constraints for D2 and D4

The table rows `S001`–`S031` (lines 13–43) are subject to strict immutability constraints:

1. **Historical Evidence Contract (`SOURCES-CONTRACT-v1` & KQ3/KQ7/KQ11/KQ14):**
   - Registry rows are immutable historical records. Prior round cells must not be edited in-place to "clean up" past statements. Corrections must be append-only.
2. **Repository-Wide Line Anchor Stability:**
   - Multiple verification reports and historical documents cite exact line numbers in `corpus/SOURCES.md`:
     - `LlamaModel.md:117` and `LlamaRouter.md:118` cite `SOURCES.md:13` (`S001`).
     - `OllamaCompat.md:13` cites `SOURCES.md:22` (`S010`).
     - `OllamaTags.md:53,91` and `AttackCoverage.md:20` cite `SOURCES.md:23` (`S011`) and `SOURCES.md:43` (`S031`).
     - `OpenAI.md:7` cites `SOURCES.md:28` (`S016`).
     - `round-11-verifier-spotcheck.md:213` explicitly cites `SOURCES.md:6–7`.
   - Modifying or inserting lines mid-file would shift these anchors, directly violating `QUALITY.md` KQ7 (*"a mid-file insertion shifts other files' line anchors"*).
3. **Parser Dependency on Exact S031 Cell Text (Check E04 Exemption):**
   - In `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` lines 646–649:
     ```awk
     if (u!="" && (scope_key in url_scopes) && status!="rejected" &&
         url_scope_nonrejected[scope_key] &&
         teaches !~ /supersedes S[0-9]{3}/)
       printf "%s\tE04\t%s duplicate url %s within scope %s\n",lane,id,u,scope
     ```
   - `S031` shares the URL `https://docs.ollama.com/api/tags` with `S011`. The `sources-census.sh validate` check permits this duplicate URL within scope ONLY because `S031`'s `teaches` cell literally matches `/supersedes S[0-9]{3}/`.
   - Any in-place edit that modifies or removes `"supersedes S011"` from line 43 would immediately cause `sources-census.sh validate` to fail with error `E04 duplicate url within scope`.
4. **Table Column Count (`NF == 13` / 11 Markdown columns):**
   - Adding pipes (`|`) inside cells breaks field counting (`E01 malformed row`).
   - Therefore, D2 and D4 **MUST NOT** be solved by in-place cell modifications; they must be resolved via appended prose at the end of the file.

---

## 5. Structural Edge Risks and Failure Modes

Static analysis identifies the following structural edge risks:

| Risk ID | Edge Condition | Mechanism / Failure Code | Current File Status / Mitigation |
|---|---|---|---|
| **R1** | Appended table rows outside `## Registry` | `sources-census.sh:618-624` checks `if (!in_registry)`: any line matching `/^ {0,3}\|[ \t]*S[0-9]{3,}[ \t]*\|/` triggers `E12 <id> row outside Registry section` (exit 1). | **Clean.** Appended lines 64–66 are pure prose paragraphs; no pipe table syntax is used. |
| **R2** | Disruption of four-section hierarchy | Adding new `##` sections (e.g. `## Errata` or `## Corrections`) alters document shape and may reset `in_registry` flags unexpectedly. | **Clean.** Corrections sit inside `## Leads (unopened)` without introducing any new `##` heading. |
| **R3** | S031 `teaches` mutation | Modifying `supersedes S011` breaks AWK exemption regex for duplicate URL/scope. | **Clean.** Line 43 is byte-identical to Round 11 HEAD. |
| **R4** | Premature S032 inclusion | Adding `S032` before gate verification shifts row count from 31 to 32 and conflicts with L1 planner ownership. | **Clean.** No `S032` row added; row count strictly remains 31. |
| **R5** | Trailing whitespace & newline corruption | Trailing spaces or missing newline corrupt git blob hash and snapshot verification (the root defect D1 in Round 11). | **Clean.** `grep -n ' $' corpus/SOURCES.md` produces 0 matches. File ends with a clean single trailing newline. |

---

## 6. Verification Checks Named for L1 Main

As a leaf advisor, this seat executes no test or validation commands. L1 Main should run the following read-only checks during final integration:

1. **Validation Check:**  
   `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`  
   *Expect:* Exit 0, clean output reporting only the expected warning `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`. Zero `E01`–`E12` errors.
2. **Census Verification:**  
   `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`  
   *Expect:* Exactly 31 rows (`tier.A=28, tier.B=0, tier.C=3; status.mined=21, status.queued=5, status.rejected=5; missing=0, invalid=0`).
3. **Immutable Prefix Diff Verification:**  
   `git diff -U0 origin/kaika/round HEAD -- corpus/SOURCES.md`  
   *Expect:* Exactly 4 added lines (lines 63–66), 0 deleted/modified lines. Original 62 lines byte-exact match.
4. **No Outside Registry Rows:**  
   Ensure `grep -n '^ *| *S[0-9]' corpus/SOURCES.md` matches only lines 13–43 inside the `## Registry` section.
