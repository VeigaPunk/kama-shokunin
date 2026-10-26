# Rev2Decl — kama append-only contract, reconstructed (round 46, w1)

**Verdict:** the lane's append-only contract is **region-scoped with three stated exceptions**
(mutable SOURCES cells, the re-derived SCORECARD head since round 42, appended corrections), while
the frozen C2 five-file default is **file-scoped**: at `0163fea2` it scores 2 of its 5 events on
text the lane's own contract exempts, and it omits four declared append-only surfaces — most
cheaply `corpus/lessons/*.md`, declared append-only at `corpus/lessons/round-44.md:37` and
unguarded at **0 events / exit 0** over the whole 292-commit history.

Full contract: `.ufo/waves/round-46/w1/out/Rev2Decl/contract.md` (file → regions → rule →
declaring line, exemptions, omissions, divergences, confidence).

## 1. The contract, compressed

| Surface | Regions | Rule | Declaring line |
|---|---|---|---|
| `LOG.md` | whole file | append; corrections appended | `PROTOCOL.md:463`; lane `README.md:16`; `AGENTS.md:4` |
| `SCORECARD.md` | dated round sections only | append; corrections appended | `corpus/lessons/round-16-verifier-spotcheck.md:41`; `SCORECARD.md:2224` |
| `SCORECARD.md` | `## Axes` 8-49, `## Planned` 51-54, `## Retired` 55-58, `## Capabilities` 115-132, `## Saturation` 133-136 | **re-derived in place** (exception) | `SCORECARD.md:6`; `:53` |
| `SCORECARD.md` | `§Historical head sections` 137-190; `### Historical axes table` 21-29 | frozen historical copies | `SCORECARD.md:137-139`; `:21` |
| `corpus/SOURCES.md` | `## Registry` rows by id | rows append-only; `status`/`recheck`/`used-by` mutable | `CORPUS.md:116`, `:118`; `corpus/QUALITY.md:123` (KQ22), `:164` (KQ31); `SKILL.md:578` |
| `corpus/SOURCES.md` | `## Search log`, `## Round-N source correction` | appended decision blocks | `corpus/SOURCES.md:470`, `:490`, `:267` |
| `corpus/QUALITY.md` | `KQn` tables + every `## Criteria added` / `## Round-N qualification` block | append; supersession names the old row | `corpus/QUALITY.md:3-5`, `:24`, `:266`, `:82`, `:143` |
| `corpus/README.md` | coverage map, frontier, round prose | append; superseded text stays | `corpus/README.md:637`, `:604`; `CORPUS.md:53` |
| `corpus/lessons/*.md` (68) | whole file per lesson | append; later L1 appends a dated section | `corpus/lessons/round-44.md:37`, `round-23.md:98-100`, `round-21.md:114`; `PROTOCOL.md:501-502` |
| `corpus/knowledge/*.md` | **`## Errata` region only** | append inside Errata; body is a dated census | `corpus/knowledge/consumer-registry.md:30`; `LOG.md:231`; `corpus/QUALITY.md:11` (KQ3) |
| `registry/history/DELTA.md` | whole file | append-only, generated | `DELTA.md:3-4`; `SCORECARD.md:26` |
| fleet `.ufo/l0-questions.md`, `MANIFEST.json` `rounds`, `PROTOCOL-APPENDIX.md` rows | — | append-only | `PROTOCOL.md:524-526`, `:314`, `:437` |
| `registry/*.tsv` ledgers | rows after first measurement | **inferred**, one dated declaration | `corpus/lessons/round-21.md:67` |

Explicitly **not** append-only: `AGENTS.md` (`corpus/lessons/round-17-verifier-spotcheck.md:157`
"AGENTS.md is not an append-only file"), `SHONEN.md` (regenerated verbatim,
`PROTOCOL.md:432`), and `SKILL.md` / `PROVINCE.md` (append-with-supersession only —
`SKILL.md:511`, `:630`; `PROVINCE.md:146`; 5 mass-deletion events in `SKILL.md`, 3 unrestored).

## 2. The frozen five-file default, measured at `0163fea2…`

Default set at `tools/append-only-audit.py:43` (frozen in
`tools/round46-append-audit-check.py:20-22`): `SCORECARD.md, LOG.md, corpus/QUALITY.md,
corpus/README.md, corpus/SOURCES.md`.

| Run (`tools/append-only-audit.py --repo . --to 0163fea2…`) | Result | Exit |
|---|---|---|
| default five | `events=5 restored=3 partial=2 unrestored=0` | **1** |
| `--files $(ls corpus/lessons/*.md)` | `events=0` | **0** |
| `--files $(ls corpus/knowledge/*.md)` | `events=3 unrestored=3` | **1** |
| `--files README.md,SKILL.md,PROVINCE.md,AGENTS.md,SHONEN.md,registry/history/DELTA.md,registry/*.tsv` | `events=6 partial=3 unrestored=3` — all six in `SKILL.md` (5) and `SHONEN.md` (1); `registry/**` and `DELTA.md` 0 | **1** |

### 2a. Omitted surfaces the lane treats as append-only

| Omitted | Declared | Cost of auditing it |
|---|---|---|
| `corpus/lessons/*.md` | `corpus/lessons/round-44.md:37` "lessons are append-only history"; `round-23.md:98-100`; KQ26 `corpus/QUALITY.md:143` | 0 events, exit 0 — free coverage |
| `registry/history/DELTA.md` | its own header `DELTA.md:3-4` "Append-only; … never hand-edited"; `SCORECARD.md:26` | 0 events — free coverage |
| `corpus/knowledge/*.md` `## Errata` region | `consumer-registry.md:30`; `LOG.md:231`; KQ3 | 3 file-level events (`726f737a` 21, `c0a9b029` 47, `d183ec57` 29); **0 of the deleted lines lie in an Errata region** (none of the three files has a `## Errata` heading at the event's parent) → needs region scoping, whole-file inclusion would be wrong |
| `registry/claim-outcome-ledger.tsv` (and sibling ledgers) | `corpus/lessons/round-21.md:67` only (others inferred) | 0 events |
| `.ufo/l0-questions.md`, `MANIFEST.json` `rounds`, `PROTOCOL-APPENDIX.md` | `PROTOCOL.md:524-526`, `:314`, `:437` | out of reach of a `--repo <lane>` tool by construction; not a tool defect |

### 2b. Included wrongly — `SCORECARD.md`

`SCORECARD.md:6` makes five head sections re-derived in place since round 42; a whole-file
deletion count therefore scores the exemption as a violation.

- `dd9f5dc6` (round 42, "SCORECARD head and README/PROVINCE reconciled") → `deleted=31
  restored_at_tip=24 partial`. All 31 deleted lines are the round-5 banner and the five
  re-derived sections. Of the 24 "restored", **22 exist only at/after line 137** — they were
  *moved* into `§Historical head sections`, not kept in place; 2 remain in the head; **7 are
  absent at the tip** (the six pre-round-42 `## Axes` rows + their intro sentence).
- `0718b6ab` (round 45) → `deleted=2417 restored_at_tip=2416 partial`. This one is a genuine
  violation of the append rule: the file went 2429 → 17 lines (append bug; `82b5e9d3`'s subject:
  "restore SCORECARD/LOG/QUALITY/README bodies truncated by the previous commit (append bug) and
  re-append round-45 text"). The single unrestored line is a **head** row (depth, `SKILL.md`
  sha `91440eb8…`, 1420 lines) replaced by that same repair commit's depth re-anchor — i.e. the
  residual `partial` is exempt-region text, while the truncation itself is correctly flagged.

## 3. Defects (reported, not repaired — counters and controls are frozen)

| ID | Defect | File:line | Command that shows it | Proposed fix |
|---|---|---|---|---|
| D1 | The C2 population encodes 2 of the 3 exceptions and 3 of the 7 declared surfaces: SCORECARD's whole file is audited although its head is exempt; `corpus/lessons/`, `registry/history/DELTA.md` and the `## Errata` region are outside it. | `tools/append-only-audit.py:43`; `tools/round46-append-audit-check.py:20-22` | the four runs in §2 | round 47: add a `--declared` set (`corpus/lessons/*.md`, `registry/history/DELTA.md`) and region scoping for `corpus/knowledge/*.md`; patch sketch in `proposed-append-only-audit.patch` (not applied, not tested) |
| D2 | `SCORECARD.md:6`/`:137-139` promise the pre-round-42 head is kept "verbatim" under `§Historical head sections`, but **no pre-round-42 `## Axes` render survives in the file**: `151023b9…` (SKILL 1375-line hash) and `dbb5f4f7…` (PROVINCE 169-line hash) occur 0 times in `SCORECARD.md` at the tip; what survives is the round-3 table (line 21) plus the five round-5/round-10 sections (141-190). | `SCORECARD.md:6`, `:139` | `grep -c 151023b9 SCORECARD.md` → `0`; decomposition in `Rev2Decl/scorecard-head-decomposition.out` | reword line 6/139 to "the round-3 table and the round-5/round-10 head sections are kept verbatim; the `## Axes` table is replaced row-by-row and its prior renders survive only in git history", or add the pre-42 Axes table under `§Historical head sections` |
| D3 | `restored_at_tip` counts text anywhere in the file, so a rewrite-plus-relocation reads as a restore (22/31 of `dd9f5dc6`). The metric cannot distinguish "kept in place" from "moved". | `tools/append-only-audit.py:17-20` (docstring definition) | `Rev2Decl/scorecard-head-decomposition.out` + the position test (contract.md §4c, M6) | state the limit in the contract, or add `restored_in_place` (occurrence line ≤ the deleted line's own region) |
| D4 | Deletion threshold (20) vs the lane's cell rule (any changed `SOURCES` cell, `CORPUS.md:116`; any rewritten `LOG.md` line, `corpus/lessons/round-26-verifier-spotcheck.md:59-62`): a 1-19 line in-place rewrite violates the lane's rule and produces no event. | `tools/append-only-audit.py:43` + audit() threshold; `CORPUS.md:116` | default run reports 5 events for history in which `sources-append-only.py` was created precisely because 1-cell edits occur (`corpus/lessons/round-17.md:85`, S041) | keep the threshold but pair the audit with `tools/sources-append-only.py` over the same range; record in the contract that C2's threshold is *not* the lane's rule |
| D5 | `corpus/lessons/` is declared append-only and unguarded, though it passes cleanly. | `corpus/lessons/round-44.md:37` | `--files $(ls corpus/lessons/*.md)` → 0 events, exit 0 | include it in the next default set |
| D6 | Knowledge files are append-only only in `## Errata`; any file-granular guard misreads their 3 body rewrites as violations. | `corpus/knowledge/consumer-registry.md:30`; `LOG.md:231`; KQ3 `corpus/QUALITY.md:11` | `--files $(ls corpus/knowledge/*.md)` → 3 unrestored, exit 1 | region scoping only; do not add whole files |

## 4. Evidence log

All reads were `git -C` on the lane (read-only) plus the frozen tool; nothing in the lane, the
fleet root, the llama.cpp clone or any counter was written or modified. Scratch was
`/fast/scratch/hyaku/kama-r46/Rev2Decl` (no clone needed), removed at the end.

```
python3 tools/append-only-audit.py --repo . --to 0163fea2…                       exit 1  (events=5)
python3 tools/append-only-audit.py --repo . --to 0163fea2… --files corpus/lessons/*.md   exit 0  (events=0)
python3 tools/append-only-audit.py --repo . --to 0163fea2… --files corpus/knowledge/*.md exit 1  (events=3)
python3 tools/append-only-audit.py --repo . --to 0163fea2… --files <SKILL/SHONEN/registry/DELTA set> exit 1 (events=6)
git log -8 --format=%h%x20%ad%x20%s --date=short 0163fea2 -- SCORECARD.md
git show --stat 82b5e9d3            # +2428 SCORECARD.md, +2294 LOG.md, +375 QUALITY.md, +665 README.md
```

Counters' own words, for the record: `tools/append-only-audit.py:1-40` defines event/restored
and the exit codes; `tools/round46-append-audit-check.py:20-22` freezes the five names and the
threshold. The proposal origin is `considerthese/2026-10-26.md:29` (five files named).

Tooling installed/updated this seat: **none** (no pacman, no uv/npx/binary installs).

## 5. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/contract.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/default-five.out` (+ `.err`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/lessons.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/knowledge.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/omitted-candidates.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/scorecard-head-decomposition.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Rev2Decl/proposed-append-only-audit.patch`
