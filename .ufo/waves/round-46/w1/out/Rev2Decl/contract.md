# kama-shokunin — reconstructed append-only contract (round 46, seat Rev2Decl)

Audited lane tip: `0163fea2dab3f282ebd70c71da9ab5de4cedf733`. Frozen inputs untouched
(`tools/append-only-audit.py`, `tools/round46-append-audit-check.py`, `.ufo/waves/round-46/preregistration.json`).

**Verdict.** The lane's append-only contract is *region*-scoped and carries three explicit
exceptions (mutable SOURCES cells; the re-derived SCORECARD head sections; appended corrections).
The frozen C2 five-file default is *file*-scoped and encodes only the first and third exception
for SOURCES, none of the SCORECARD exception, and four declared append-only surfaces sit outside
its population. Measured at the audited tip: 2 of its 5 events (`dd9f5dc6` SCORECARD 24/31 and the
residual of `0718b6ab` SCORECARD 2416/2417) are text its own contract exempts from the
append-only rule, and `corpus/lessons/` (declared append-only, 68 files, 292 commits) yields
**0 events** — coverage that is free and currently absent.

## 1. Method (read-only; nothing in the lane was written)

| # | Command | Result |
|---|---|---|
| M1 | `python3 tools/append-only-audit.py --repo . --to 0163fea2…` | `summary commits=292 events=5 restored=3 partial=2 unrestored=0`, **exit 1** → `default-five.out` |
| M2 | same, `--files $(ls corpus/lessons/*.md \| paste -sd,)` | `events=0`, **exit 0** → `lessons.out` |
| M3 | same, `--files $(ls corpus/knowledge/*.md \| paste -sd,)` | `events=3 restored=0 partial=0 unrestored=3`, **exit 1** → `knowledge.out` |
| M4 | same, `--files README.md,SKILL.md,PROVINCE.md,AGENTS.md,SHONEN.md,registry/history/DELTA.md,registry/{verdict-ledger,claim-outcome-ledger,release-recheck-b11889,recheck-r45,digest-ledger,engine-pins,staged-refusals,report-landing-errata}.tsv` | `events=6 partial=3 unrestored=3`, **exit 1**; all six are `SKILL.md` (5) and `SHONEN.md` (1); `registry/**` and DELTA produce **0 events** → `omitted-candidates.out` |
| M5 | parent-line decomposition of the two SCORECARD events (`git diff --no-renames -U0 <c>^1 <c> -- SCORECARD.md`, compare against the blob at the tip) | `dd9f5dc6 deleted=31 absent_at_tip=7`; `0718b6ab deleted=2417 absent_at_tip=1` → `scorecard-head-decomposition.out` |
| M6 | position test on M5's restorations: are the "restored" lines still in the head? | `dd9f5dc6: present_before_line137=2 only_after_line137=22 absent=7` |
| M7 | `grep -n`/`sed -n` for every declaration cited below; `git log -8 -- SCORECARD.md`; `git show --stat 82b5e9d3` | provenance cited per row |

Counting is exact: `deleted` = `-` lines of the `-U0` diff against the first parent (header
excluded); `restored_at_tip` = deleted line texts occurring *somewhere* in the file at `to`.

## 2. Contract: what is append-only, where, and by which line

Rule vocabulary — **A** whole file append-only; **A-row** rows appended, named cells mutable;
**A-corr** append-only with corrections appended (naming the superseded text); **R** re-derived
in place; **N** not append-only.

| File | Regions covered | Rule | Declaring line (verbatim, trimmed) |
|---|---|---|---|
| `LOG.md` | whole file | A-corr | `PROTOCOL.md:463` "`LOG.md` is append-only: entries are never rewritten or deleted; corrections land as new entries."; lane `README.md:16` "`LOG.md` — append-only round log"; `AGENTS.md:4` "Every change appends a LOG.md entry"; `corpus/lessons/round-26-verifier-spotcheck.md:59-62` (a rewritten LOG entry is a defect; correction must be appended) |
| `SCORECARD.md` | every dated round section (`## Round-N …`, `### Round-N …`, `### Planned (round N)`); this is the region the round-16 spot-check measured | A-corr | `corpus/lessons/round-16-verifier-spotcheck.md:41` "**88 additions / 0 deletions**. It is append-only"; `SCORECARD.md:2224` "### Round-40 record corrections (append-only; round-40 closure defect D4)"; `corpus/README.md:521` "append-only records in `corpus/lessons/round-33.md` and `SCORECARD.md`" |
| `SCORECARD.md` | `## Axes` 8-49, `## Planned` 51-54, `## Retired` 55-58, `## Capabilities` 115-132, `## Saturation` 133-136 | **R** (exception, see §3) | `SCORECARD.md:6` "The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and kept current in rounds 43, 44 and 45"; `:10` (round 41 reconcile), `:53` "Superseded in round 42" |
| `SCORECARD.md` | `§Historical head sections` 137-190 (`### Banner (round-5 text)`, `### Planned (round-5 text)`, `### Retired (round-3 text)`, `### Capabilities (round-10 head table)`, `### Saturation (round-10 text)`), plus `### Historical axes table` 21-29 | frozen historical copies | `SCORECARD.md:137-139` "The text below is the lane's head self-description as it stood through round 41, kept verbatim."; `:21` "(round-3 assessment; superseded in round 41)" |
| `corpus/SOURCES.md` | `## Registry` rows, keyed by id | A-row: `status`, `recheck`, `used-by` mutable; `source kind tier scope anchor teaches opened` immutable | `CORPUS.md:116` "**Append-only.** Only `status`, `recheck` and `used-by` change in place, and each change is logged old→new in the round lesson."; `CORPUS.md:118` "A correction is a new row whose `teaches` opens `supersedes S0NN —`"; `corpus/QUALITY.md:123` (KQ22), `:164` (KQ31); `SKILL.md:578` (gate `tools/sources-append-only.py`); `tools/sources-append-only.py:1-25` (cell-level enforcement) |
| `corpus/SOURCES.md` | `## Search log`, `## Round-N source correction` blocks | A-corr (blocks appended, decisions recorded, cells untouched) | `corpus/SOURCES.md:470` "## Round-30 source correction — S174 and S176 (append-only decision record)"; `:490` "append-only: no cell was rewritten"; `:267` (correction to a filed search-log row appended, not edited) |
| `corpus/QUALITY.md` | criterion tables (`KQn` rows) and every `## Criteria added — round N` / `## Round-N qualification` block | A-corr | `corpus/QUALITY.md:3-5` "Criteria are added as new rows; supersession names the old criterion instead of erasing it."; `:24` "appended so no existing line moves"; `:266` "This append-only block supersedes … Earlier text is left in place."; `:82` "is append-only history"; `:143` (KQ26) |
| `corpus/README.md` | coverage map, frontier/disposition prose and round sections | A-corr | `corpus/README.md:637` "The bullet above is left as written (append-only)."; `:604` "keep the old id and are superseded, not edited"; `CORPUS.md:53` "**Corrections are new entries, never rewrites.**" |
| `corpus/lessons/*.md` (68 files) | whole file, per lesson; a later L1 seat may append a dated section | A-corr | `corpus/lessons/round-44.md:37` "lessons are append-only history and the next release recheck should carry it"; `corpus/lessons/round-23.md:98-100` "Everything above this section was written at `245a37f6` and stays unchanged; corrections below are append-only."; `corpus/lessons/round-21.md:114` "Corrections to the text above (append-only; earlier lines stay)"; `PROTOCOL.md:501-502` "Corpus corrections are new entries, never in-place rewrites" |
| `corpus/knowledge/*.md` | **`## Errata` region only**; the body is a dated census and may be edited | A-corr (region) | `corpus/knowledge/consumer-registry.md:30` "## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)"; `LOG.md:231` "Corpus: append-only §Errata in `consumer-registry.md`"; `corpus/QUALITY.md:11` (KQ3) "Corrections preserve old corpus bytes" |
| `registry/history/DELTA.md` | whole file | A (generated) | `registry/history/DELTA.md:3-4` "# Append-only; one line per row-field change between snapshots, in chronological order. Generated by kama-probe.sh snapshot; never hand-edited."; `SCORECARD.md:26` "append-only `DELTA.md`" |
| `.ufo/l0-questions.md` (fleet path, not in the lane repo) | whole file | A-corr | `PROTOCOL.md:524-526` "The file is append-only — … appends a new line naming the superseded one and never rewrites a filed line" |
| fleet `MANIFEST.json` `rounds` array | the array | A after closure | `PROTOCOL.md:314` "**`rounds` is append-only after closure.** Corrections are appended entries carrying `type:`…"; `:320` (§Appendix "Append-only `rounds`") |
| fleet `PROTOCOL-APPENDIX.md` | incident rows | A | `PROTOCOL.md:437` "Rows are append-only dated incidents" |
| fleet lane report `.ufo/reports/round-<N>/<id>.md` | filed bytes | corrections **appended**, never rewritten | `PROTOCOL.md:135-137` "a correction to it lands in the correcting round's own report, or as an erratum appended after the filed bytes in a new commit and naming the text it supersedes — never a rewrite of the filed bytes, labelled or silent" |
| fleet `.ufo/reports/AGGREGATE.md` (rolling audit ledger) | refresh sections | A-corr, "in the same sense as `LOG.md`" | `PROTOCOL.md:338-339` "The ledger is append-only in the same sense as `LOG.md` — refresh sections supersede earlier rows explicitly rather than rewriting them." |
| fleet `.ufo/history-pin.json` | whole file | append-only pin; regeneration is a separate committed act | `PROTOCOL.md:214` "writing/committing the append-only history pin `.ufo/history-pin.json`"; `:215-216` "regenerating a pin is a separate committed act … never a repair inside the same closure pass" |
| `registry/*.tsv` ledgers (`claim-outcome-ledger`, `verdict-ledger`, `release-recheck-*`, `recheck-r45`, `digest-ledger`, `engine-pins`, `staged-refusals`, `report-landing-errata`) | rows after first measurement | **inferred** — one dated statement only for the claim-outcome ledger | `corpus/lessons/round-21.md:67` "the ledger was created this round; append-only applies after measurement". No lane file declares the other ledgers append-only; M4 shows they had 0 mass-deletion events in 292 commits, so treating them as append-only costs nothing observable. |

## 3. Stated exemptions (each with its declaring line)

| # | Exemption | Declaring line | Scope limit found |
|---|---|---|---|
| E1 | SOURCES mutable cells | `CORPUS.md:116`; `corpus/QUALITY.md:123` (KQ22); `SKILL.md:614` | Cell-level, not line-level: **any** changed immutable cell is a violation, so the lane's rule is far stricter than C2's `deleted >= 20` line count. |
| E2 | SCORECARD head re-derived in place since round 42 | `SCORECARD.md:6`, `:53`; counters `tools/round42-selfdesc-reconcile.py`, `tools/round41-scorecard-reconcile.py` | Five named sections, **not a contiguous head**: `## Move log` 59-69 and `## Actual round 5` 70-114 are *not* in the list; equally the round-3 table at 21-29 is frozen history. |
| E3 | Corrections are appended, never rewritten | `PROTOCOL.md:123-125` "append-only files (`LOG.md`) take an appended correction entry pointing at the superseded text, never an in-place rewrite"; `PROTOCOL.md:366-367`; `CORPUS.md:53`; `corpus/QUALITY.md:143` (KQ26) | A correction is an *addition*, so it never offsets a deletion — the exemption does not make a rewritten region "restored". |
| E4 | `AGENTS.md` is not append-only | `corpus/lessons/round-17-verifier-spotcheck.md:157` "AGENTS.md is not an append-only file." | Its round's own VCS line was corrected in place. |
| E5 | `SHONEN.md` is regenerated verbatim from the fleet template | `PROTOCOL.md:432` "regenerates `SHONEN.md` verbatim from the template"; marks confined to boxes | Not append-only; M4 shows 1 mass-deletion event (`e246c40ec1b4`, 21 deleted, 1 restored). |
| E6 | `SKILL.md` / `PROVINCE.md` use append-with-supersession, not append-only | `SKILL.md:511` "is superseded, not edited"; `:630` "explicit row supersessions"; `PROVINCE.md:146` "Appended correction, round 31 attempt 2"; `corpus/lessons/round-16-verifier-spotcheck.md:42` | No declaration makes either file append-only; M4: `SKILL.md` has 5 mass-deletion events (3 unrestored), `PROVINCE.md` 0. Their omission from any append-only audit is correct. |
| E7 | `considerthese/` is operator-authored and never edited | lane `README.md:21` | Out of lane write scope entirely. |

## 4. Frozen C2 five-file default (`tools/append-only-audit.py:` FILES) vs this contract

Default set: `SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md`
(`tools/append-only-audit.py:43`; frozen in `tools/round46-append-audit-check.py:20-22`).

### 4a. Append-only surfaces the default omits

| Omitted | Declared at | Measured cost of including it (M2/M3/M4) | Recommendation (not applied — counters are frozen) |
|---|---|---|---|
| `corpus/lessons/*.md` (68 files) | `corpus/lessons/round-44.md:37`; `round-23.md:98-100`; `round-21.md:114`; `corpus/QUALITY.md:143` (KQ26); `PROTOCOL.md:501-502` | **0 events / exit 0** over 292 commits | cheapest real gap: declared append-only, currently unguarded, zero false positives |
| `corpus/knowledge/*.md` `## Errata` region | `corpus/knowledge/consumer-registry.md:30`; `LOG.md:231`; `corpus/QUALITY.md:11` (KQ3) | **3 events / exit 1** at file granularity: `726f737a` `llamacpp-loading-lifecycle.md` 21, `c0a9b029` `context-capacity.md` 47, `d183ec57` `echo-discriminating-counters.md` 29. Re-checked per event: none of the three files carries a `## Errata` heading at the event's first parent, so **0 of those deleted lines fall inside an Errata region** — they are body edits | needs *region* scoping (Errata block only), not whole-file inclusion; whole-file inclusion would be wrong |
| `registry/history/DELTA.md` | `DELTA.md:3-4`; `SCORECARD.md:26` | **0 events** | declared append-only inside the file itself; free to include |
| `registry/*.tsv` ledgers | `corpus/lessons/round-21.md:67` (claim-outcome ledger only; others inferred) | **0 events** | only the claim-outcome ledger has a dated declaration; the rest are a practice, not a rule |
| `.ufo/l0-questions.md`, fleet `MANIFEST.json` `rounds`, `PROTOCOL-APPENDIX.md` rows, `.ufo/reports/round-<N>/*.md` filed bytes, `.ufo/reports/AGGREGATE.md`, `.ufo/history-pin.json` | `PROTOCOL.md:524-526`, `:314`, `:437`, `:135-137`, `:338-339`, `:214` | n/a — outside the lane repo, so a `--repo <lane>` tool cannot reach them by construction | note as out of population, not as a defect of the tool |

### 4b. Where the default is wrong

| Included | Why it is wrong to treat the whole file as append-only | Evidence |
|---|---|---|
| `SCORECARD.md` | Its head is **re-derived in place** by contract (`SCORECARD.md:6`). Only the dated round sections are append-only. | M1's 2 partial events are head text. `dd9f5dc6` (round 42, "SCORECARD head and README/PROVINCE reconciled") deletes 31 lines; all 31 are the round-5 banner + the five re-derived sections; 22 of them are "restored" only because they were moved into `§Historical head sections` (M6: `only_after_line137=22`), 2 remain in the head, and **7 are absent at the tip**. `0718b6ab` (round 45) truncated the file 2429→17 lines (an append bug, per `82b5e9d3`'s subject "restore … bodies truncated by the previous commit (append bug)"); 2416/2417 lines returned, and the 1 that did not is a *re-anchored* head row (depth, `SKILL.md` sha `91440eb8…`, 1420 lines) replaced by `82b5e9d3`'s own depth re-anchor. |
| `corpus/QUALITY.md`, `corpus/README.md`, `LOG.md`, `corpus/SOURCES.md` | Correct as included (whole-file A-corr / A-row), subject to E1's cell rule being stricter than the tool's line threshold. | `CORPUS.md:116`; `corpus/README.md:637`; `PROTOCOL.md:463` |

### 4c. Metric semantics that the contract does not share

1. **"Restored" means "exists somewhere", not "kept in place."** M6: 22 of `dd9f5dc6`'s 31 deleted
   lines count as restored solely because they were relocated to `§Historical head sections`.
   A rewrite-and-re-append of untouched text reads identically to a genuine restore.
2. **A correction appended is invisible to a deletion counter.** E3 corrections are additions;
   they can restate a rule while the rewritten region stays deleted, and the counter reports
   `partial` for the deletion even though the lane's rule was followed.
3. **Threshold mismatch.** The tool floors at 20 deleted lines (frozen at 20); the lane's SOURCES
   rule is *any* changed cell (`CORPUS.md:116`, KQ22, `tools/sources-append-only.py`) and its
   SCORECARD rule is *any* rewritten line (`corpus/lessons/round-26-verifier-spotcheck.md:59-62`
   treats one rewritten LOG sentence as a defect). A 1-19 line in-place rewrite inside `LOG.md`
   violates the lane's rule and produces no event.

## 5. Divergences from the contract, ranked (all reported, none repaired)

| ID | Statement | Ground |
|---|---|---|
| D1 | The C2 population flags exempt text and misses declared surfaces. | §4a/§4b; M1-M4 |
| D2 | `SCORECARD.md:6` and `:137-139` promise §Historical head sections keep the pre-round-42 head "verbatim", but no pre-round-42 **Axes table** render is retained: `151023b9…` (SKILL 1375-line hash) and `dbb5f4f7…` (PROVINCE 169-line hash) occur **0** times in `SCORECARD.md` at the tip, and 7 of `dd9f5dc6`'s deleted lines are absent. What is retained is the round-3 table (line 21) and the five round-5/round-10 sections (141-190). | M5, M6 |
| D3 | `dd9f5dc6` is scored `partial` (24/31) although its deletions are exactly the exempt re-derivation; its "restored" lines are relocations, so the number measures text survival, not append discipline. | M1, M5, M6 |
| D4 | `0718b6ab` vs `82b5e9d3` is a real violation of the append rule for four files (`SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md` truncated by an append bug) and the counter reports it correctly; only its SCORECARD residual (`2416/2417`) is exempt-region text (a head row re-anchored again in the repair commit). | M1, M5, `git show --stat 82b5e9d3` |
| D5 | `corpus/lessons/` is declared append-only (`round-44.md:37`) and has no guard; it also passes cleanly (0 events), so the gap is coverage, not latent damage. | M2 |
| D6 | `corpus/knowledge/` is append-only only in its `## Errata` region; 3 file-level mass deletions exist outside it, so any whole-file guard would fail on legitimate body edits. The frozen tool is file-granular and cannot express the region. | M3 |

## 6. Confidence

| Claim | Confidence | Basis |
|---|---|---|
| Whole-file append-only: `LOG.md`, `corpus/SOURCES.md` (rows), `corpus/QUALITY.md` (criteria), `corpus/README.md`, `registry/history/DELTA.md` | high (observed declarations + 0-2 events) | §2, M1 |
| `corpus/lessons/*.md` append-only | high — explicit `round-44.md:37`; corroborated by `round-23.md:98-100`, KQ26 | M2 |
| `corpus/knowledge/*.md` append-only **only** in `## Errata` | high for `consumer-registry.md` (its own heading says so), medium elsewhere (inference from `LOG.md:231` + KQ3, plus 3 body deletions that no filed record calls a violation) | M3 |
| SCORECARD head exemption reaches only the five named sections | high — line 6 names them; `## Move log` and `## Actual round 5` are not named | §3 E2 |
| §Historical head sections retain the pre-42 head "verbatim" | **falsified for the Axes table** (D2); holds for the five sections at 141-190 | M5/M6 |
| `registry/*.tsv` ledgers append-only | low / inferred — one dated statement (claim-outcome ledger), 0 observable events | M4 |
| `SKILL.md`, `PROVINCE.md`, `AGENTS.md`, `SHONEN.md` are not append-only | high — explicit for AGENTS.md, template rule for SHONEN, no declaration for SKILL/PROVINCE and in-place deletions exist | M4, §3 E4-E6 |

## 7. Receipts (this directory)

- `default-five.out` / `.err` — M1, exit 1
- `lessons.out` — M2, exit 0
- `knowledge.out` — M3, exit 1
- `omitted-candidates.out` — M4, exit 1
- `scorecard-head-decomposition.out` — M5/M6

Scratch `TMPDIR=/fast/scratch/hyaku/kama-r46/Rev2Decl` held no clones (all reads used
`git -C` on the lane, read-only) and was removed at the end of the seat.
