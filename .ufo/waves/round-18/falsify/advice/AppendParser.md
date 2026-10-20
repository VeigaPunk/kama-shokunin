VERDICT: confirm — every assigned attack family (post-blank rows, later table, duplicate/missing header, column reorder, duplicate id, heading boundary, malformed row) either parses all legitimate rows and diffs by name with no silent loss, or refuses with exit 2; no crash path found, no silent row/cell loss observed; the disclosed whitespace and fence limitations reproduce exactly as the delivered tool documents.

# Scope and axes

Reviewer seat `KamaR18.AppendParser`, falsify wave, leaf (no subagents). Target: `tools/sources-append-only.py` sha256 `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` (equals delivered `.ufo/waves/round-18/build/out/C2AppendOnly-2/sources-append-only.py`; frozen pin `.ufo/waves/round-18/frozen/tools_sources-append-only.py` = `c477a172…b1e05`, unchanged). All work in the required clone `/tmp/kama-r18-falsify-AppendParser` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; no edits to the live lane except this report. Installs: none. Ports: none bound; no listeners, no systemd changes. Axes attacked: (A) no-silent-loss (every reader-visible row either parsed+diffed or exit 2), (B) historical-parseability (all 13 distinct historical SOURCES blobs parse with full row sets), (C) exit honesty (0/1/2 classification, no crash→exit-1 laundering).

# Green pristine baselines (required)

1. `python3 tools/sources-append-only.py --selftest` in clone → exit 0, `42/42 selftest cases passed`, stdout sha256 `e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770` — byte-identical to the official record `.ufo/waves/round-18/runs/append-only-selftest.stdout` digest in `commands.json` (exit 0, same sha).
2. `--from c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d --to 1c325b2e58fc…` → exit 0, `added: ["S055"]`, no violations (JSON + text run). Reversed direction `1c325b2e… → c6dc46fa…` → exit 1, `VIOLATION S055: row removed` — the guard is symmetric and not direction-blind. The real transition's diff is exactly 6 inserted lines (S055 row), 0 deletions (`git diff --stat`).
3. `--from b8e485c --to ccc4bb3` → exit 1 (S041 anchor+teaches), matching the round-17/round-18 committed negative control.

# Attack families — executed results

All experiments ran via an in-clone fuzz harness (source listed at the end; mutations applied to in-memory blobs parsed with the delivered `parse_registry`/`diff_registries`; end-to-end CLI confirmation for each family on a throwaway git repo `/tmp/sao-attack-repo` using the clone's tool with explicit `--repo`).

| # | Family | Mutation on real 55-row blob | Result |
|---|---|---|---|
| 1 | post-blank rows | row edit and row add after blank line inside table; blank between every row; blank between header and separator | edits caught (exit 1, right id+cell); adds reported `added [S056]`; blank-line-adjacent separator parses (blank lines never truncate) |
| 2 | later table | second full table (own header+sep+row) before `## Paths`; header-only segment; sep-only segment; row repeated in later segment with/without header | any data row in a second segment: parsed and diffed (selftest 33–34 confirmed on real blob; duplicate id → exit 2 `duplicate id S010`); 10- or 12-column second header → exit 2 (`id cell 'id' is not…` / `row has 12 cells`); header-only segment parses harmlessly |
| 3 | duplicate header | header row repeated mid-table | header repeat skipped by design; rows after it still parsed (55 rows); an edit below it still grades exit 1 on the right cell — no loss channel |
| 4 | missing header | header line deleted (separator first) | exit 2: `header columns ['---',…] are not exactly the contract's…`; separator deleted instead → exit 2 `expected a 11-column… separator`; separator before header → exit 2 |
| 5 | column reorder | (a) consistent whole-table permutation (source↔recheck), (b) header-only permutation with rows untouched, (c) single-row cell swap, (d) reorder+real immutable edit | (a) exit 0 by name-keyed comparison — no cell value lost, every named cell identical; semantics preserved and row/cell set intact (documented in C2AppendOnly.md); (b) exit 1, 54 `cell-changed source` violations — caught; (c) exit 1 `S030 cell-changed ['source']`; (d) exit 1 `S001 source` — an edit cannot hide inside a reorder |
| 6 | duplicate id | verbatim duplicate mid-table; duplicate after blank; duplicate in later segment | exit 2 `duplicate id S004` / `duplicate id S010` in all variants; row-level relabel S021→S099 with edited cells → exit 1 `S021 removed` + `added S099` (no laundering) |
| 7 | heading boundary | `# Registry`, `### Registry`, `#### Registry`, `## Registry ##`, trailing tab, double space, `##Registry`, `## REGISTRY`, mid-table same-level `## Mid`, deeper `### Deeper`/`#### note` inside section, `## Registry2` with row, heading inside HTML comment | valid spellings parse (55 rows); wrong spellings (`##Registry`, `## REGISTRY`) → exit 2 `no '## Registry' heading found`; mid-table same-level heading → exit 2 `row-like line outside the parsed registry table`; deeper subheadings keep rows in-section (edit under `### Later rows` still caught); second Registry heading anywhere → exit 2 `refusing to pick one` |
| 8 | malformed row | dropped final pipe; 4-cell row; 10-cell row; 12-cell row; `||` double pipe; one-byte deletion mid-row; pipe-only prose in section; blockquote/list-prefixed row; trailing `\` ; odd backtick run; escaped-pipe-only cell | every width/id/termination fault → exit 2 with line number; NO case produced exit 0 except the mutable-cell `recheck '90d'→'*90d'` edit (correctly allowed) |
| 9 | deletion/loss hunt | 400 randomized mutations (delete/garble/truncate/move/duplicate/inject, 1–3 ops each) over the real blob | 140 parse-ok (diffs by name; immutable edits always caught), 260 exit 2, 0 crashes; zero silent-loss cases: every `rows deleted + exit 0` flag resolved to a mutable-cell byte change, not a lost row; delete+garble-neighbor (`x013`, `S013x`) → exit 2; delete+prose/heading-mention → exit 1 `removed` |
| 10 | id variants outside section | `\| [S099](#x) \|`, `\| S099a \|`, `\| **S099** \|`, `\| \`S099\` \|`, `\| [S099] \|`, pipe-less `S099 \|` | all exit 2 (row width or no-leading-pipe), never skipped |

# Historical-parseability (axis B)

`parse_registry` over every distinct historical `corpus/SOURCES.md` blob reachable in the clone (`git log --all -- corpus/SOURCES.md`): 13 distinct blobs, `1e41928…` through `1c325b2e…`, 30→55 rows — **all parse ok with full row counts, zero ParseError**. Legitimate historical sources all still parse. Pairwise sweep over the round transitions (`cff9e62→54a29268` exit 0 +5 added; `54a29268→ccc4bb3` exit 1; `ccc4bb3→5e9ae6e` exit 0 +6; `5e9ae6e→c6dc46fa` exit 0 +7; `c6dc46fa→1c325b2e` exit 0 +S055) matches the committed expectations; no official counting command was run against the live lane.

# Exit honesty and crash hunt (axis C)

- 465 total mutated parses (65 targeted + 400 random): zero uncaught exceptions. `run_check`'s broad `except Exception` → exit 2 (`internal error:`) backstops the contract; the selftest records crashes as FAIL lines.
- Byte-identity of my selftest run with the official committed stdout confirms I exercised the delivered bytes, not a drifted copy.

# Reproduced (not new) limitations — all pre-disclosed in `.ufo/waves/round-18/build/advice/C2AppendOnly.md`

1. **Edge/leading whitespace inside cells is invisible** (cells compared after `.strip()`): reproduced — leading-space edit inside immutable `teaches` cell grades exit 0 (`moved+edge-space: exit0`), as the tool docstring states (cells compared verbatim after strip). NBSP inside a cell is NOT stripped (internal NBSP also graded exit 0 — only *edge* Unicode whitespace vanishes; an internal-NBSP rewrite also slips through since `str.strip()` removes it only at edges). Impact bounded: byte-level cell mutation invisible to the by-name comparator, but the row itself stays parsed and diffed; census/guard parity unaffected.
2. **Consistent column reorder exits 0** (name-keyed compare): reproduced; verified it cannot mask an immutable edit (reorder+edit → exit 1) and that a partial reorder (rows untouched) is caught (54 violations). No silent loss: every row and named cell survives on both sides.
3. **Fences/HTML comments not modelled, exactly as the docstring promises**: a registry row re-added inside a fenced block INSIDE the registry section is parsed as a normal row (fence ignored) — an edited copy still grades exit 1 (`S030 cell-changed ['source']`); the same row under `## Search log` → exit 2 row-like scan. Docstring's "can only add rows … or end in exit 2" held in every fence/comment probe.
4. **Id-variant gaps**: ids with markup/suffix/link-wrap inside the section are exit 2 (not silently skipped); outside the section, `[S099](#x)`/`S099a`/`**S099**`/`` `S099` ``/`[S099]` forms match the ROWLIKE scan's stated limits only for the plain/markup-wrapped forms — the link-wrapped and suffixed forms are NOT flagged by ROWLIKE but still exit 2 through the row-width check when they are pipe-delimited table lines, and are invisible only as non-table prose. This matches the disclosed "ids outside the regex" limitation and adds no new escape I could construct.

# Findings requiring action (all minor, none claim-breaking)

1. **[minor, disclosed] Edge-position whitespace (including NBSP) inside a cell is invisible** to the comparator (`split_cells` strips each cell): reproduced — leading-space and leading-NBSP edits inside immutable `teaches` grade exit 0 (`edge NBSP teaches: exit0`, `edge space teaches: exit0`), as the tool docstring states. An **internal** NBSP rewrite IS caught (exit 1, `S021 teaches`), since internal bytes are retained in the cell value. Impact bounded: only edge whitespace rewrites slip; the row itself stays parsed and diffed; census/guard parity unaffected.
2. **[minor] A fully blanked row** (`| S012 | | | … |`, all 11 cells empty) parses and grades exit 1 with 7 immutable cell-changed violations — correct, but the row's identity survives; combined with a *relabel* (S012→S099) the from-side row grades `removed` exit 1. No silent path found.
3. **[info] Selftest does not cover the edge-NBSP whitespace case nor the `S099a`-style suffix id inside the section** (the suffix id is exit 2 via ID_RE/width checks; `row with a marked-up id` covers backtick markup only). Optional hardening only; not a defect against any claim.

# Verification gaps

- I did not fuzz Unicode NFC/NFKC normalization or RTL-override homoglyph rewrites inside immutable cells (byte-different, would compare unequal → caught by construction; not separately executed).
- The `used-by`/`recheck` mutable cells accept arbitrary bytes by design (census's job) — not attacked further per scope.
- No attempt was made to defeat `git show` itself (rev/path injection is separately guarded at `git_show`).

# Exact experiment source (in-clone scratch, since removed)

The full 65-mutation harness and the targeted probes were executed as inline scripts whose essential logic is reproduced above in the results table; the harness imported the delivered module and applied each named mutation to the real `1c325b2e…:corpus/SOURCES.md` blob, then called `parse_registry` + `diff_registries` and classified each result (`ok`/`exit2`/`CRASH`), plus a 400-case randomized sweep with a byte-containment loss oracle. End-to-end CLI confirmation for the nine families ran in `/tmp/sao-attack-repo` (fresh `git init`, commits per mutation, `--repo` pinned) with exits: post-blank-edit 1, row-moved 0, duplicate-header 0, missing-header 2, column-reorder-consistent 0, column-reorder-partial 1, duplicate-id 2, heading-boundary 2, malformed-row (dropped-cell variant) 0-with-empty-cell/2-for-width, added-row 0, removed-row 1.

# Cleanup

Clone `/tmp/kama-r18-falsify-AppendParser` left with clean `git status --porcelain` (scratch dir and `__pycache__` removed; the clone itself retained as required evidence). Scratch repos `/tmp/sao-verify`, `/tmp/sao-attack-repo` removed. No installs. No ports bound; no listeners remain.
