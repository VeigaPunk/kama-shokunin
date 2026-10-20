VERDICT: confirm — the delivered `sources-append-only.py` kills both named survivors (M3a drops `opened`, M4b drops rows after a blank line) under its own `--selftest`. The e75cf68 self-pair exits 0, b8e485c→ccc4bb3 exits 1 (S041 `anchor`, `teaches`), and all 10 historical pairs give the frozen tool's JSON byte for byte.

Seat `KamaR18.C2AppendOnly-2`, executor, C2 calibration. Axes: calibration (the detector's sensitivity to its own mutants) and operability (exit classification). Everything below is advice from a scratch clone. It is not an L1 measurement.

## Delivered

| path (lane-relative) | sha256 |
|---|---|
| `.ufo/waves/round-18/build/out/C2AppendOnly-2/sources-append-only.py` (619 lines) | `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` |
| `.ufo/waves/round-18/build/out/C2AppendOnly-2/sources-append-only.py.diff` (`diff -u` frozen → new, 583 lines) | `f254ba337d39149109fcbc323a505f744458e109c2e28dab65fd7d099462aa9e` |
| base: `.ufo/waves/round-18/frozen/tools_sources-append-only.py` (`sha256sum -c` OK; equal to `e75cf68:tools/sources-append-only.py`) | `c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05` |

The CLI is unchanged: `--from/--to/--repo/--path/--json/--selftest`. Exit codes are still 0, 1 and 2. The JSON and text report shapes are unchanged.

## Behaviour changes (frozen → delivered; delivered line numbers)

1. **`opened` and every other immutable cell are always compared.** The frozen derivation line is kept verbatim at `:247`, quote `immutable_cols = [c for c in header if c not in MUTABLE_CELLS and c != "id"]`. Two things now back it:
   - **A pinned check, `:248`.** The derived list must equal `IMMUTABLE_CELLS` (`:67`), a literal written separately from `MUTABLE_CELLS` (`:63`). If a slice, filter or set edit narrows the comparison, every run exits 2. This includes main runs, not only the selftest.
   - **A per-cell oracle in the selftest.** `_CELL_EDIT_EXIT` (`:371`) is written out by hand. The loop at `:470` makes one single-cell edit per contract column, 10 cases. Frozen had no case for `opened`, `kind`, `tier` or `scope`: `opened` appears only as a default at frozen `:274` (`scope="scope-x", opened="2026-10-20"):`).
2. **Rows after a blank line, in a later table segment, or under a deeper subheading are parsed.** The section now ends only at a heading of the same or higher level (`:175`). Frozen `:118-119` (`if HEADING_RE.match(line):` / `break`) stopped at any heading, so an edit below a `### …` subheading graded exit 0. A later repeat of the header, or any separator line after the first, is skipped (`:206`).
3. **A row lost by parsing is reported as exit 2, never skipped:**
   - A table line in the section whose id cell is not `S` plus digits now exits 2 (`:215`). Frozen `:147-149` raised only `if rid.startswith("S")` and otherwise ran `continue`. So edits to rows with ids `s002` or `` `S002` `` graded exit 0.
   - A table line without a leading pipe exits 2 (`:179`).
   - **Global accounting:** any row-like line (`:76`) anywhere in the blob that was not read as a registry row exits 2 (`:228`). Frozen ignored a `| S002 |` row placed under `## Paths`, and graded an edit to it exit 0. The CORPUS.md census regex `^\|[[:space:]]*S[0-9]{3,}…` counts that row.
   - More than one `Registry` heading exits 2 (`:158`). Frozen `:107-109` took the first heading and silently dropped the rows of any second one.
4. **The header must hold exactly the contract's 11 column names, in any order (`:191`).** Frozen `:156` required only `{"id"} | MUTABLE_CELLS`. That allowed two failures:
   - A repeated column name (`teaches` written in place of `opened`) made `dict(zip(header, cells))` (frozen `:142`) silently drop the real `teaches` column. A `teaches` edit then graded exit 0.
   - A `--to` that drops a column crashed at `if old[c] != new[c]` (frozen `:185`) with `KeyError`, exit 1, which is the violation code. Synthetic CLI run: frozen rc 1 `KeyError: 'opened'`; delivered rc 2 `header columns … are not exactly the contract's …`.
5. **The first separator must have the header's width (`:199`).**
6. **Exits stay honest:**
   - The blob is decoded as strict UTF-8 (`:273`). Bad bytes are now exit 2. Frozen `:202` `text=True` gave a traceback with exit 1. Synthetic CLI: frozen rc 1 traceback, delivered rc 2 `blob is not UTF-8`. This residual was routed earlier in `.ufo/waves/round-17/build/advice/SentinelSeatWrites.md` F2: "catch `UnicodeDecodeError` as ParseError so it exits 2".
   - If git cannot run, the result is exit 2.
   - Any other exception in `run_check` exits 2 with an `internal error:` message (`:308`). Shown with mutant N6 on the dropped-column pair: rc 2, `internal error: KeyError: 'opened'`.
   - The selftest records a crashing case as a FAIL line instead of aborting (`:539`).
7. A `## Registry ##` heading (closing hashes) is now recognised. Frozen gave exit 2, "no heading".

## Commands run (clone `/tmp/kama-r18-C2AppendOnly-2` at `e75cf680…`, `PYTHONDONTWRITEBYTECODE=1`)

| command | rc | output |
|---|---|---|
| `python3 -m py_compile tools/sources-append-only.py` | 0 | — (the `__pycache__` it wrote in the clone was removed) |
| `python3 -W error` compile of the file | 0 | no SyntaxWarning |
| `python3 tools/sources-append-only.py --selftest` | 0 | `42/42 selftest cases passed` (39 cases + 3 detector checks), 0 FAIL |
| `… --repo . --from e75cf680b53484a61709ee1b2787d8dbc6419f74 --to e75cf680b53484a61709ee1b2787d8dbc6419f74` | 0 | `no append-only violations` |
| `… --from e75cf680… --to e75cf680…` (default `--repo`, the lane path) | 0 | `no append-only violations`. **Disclosure:** this runs only `git -C <lane> show REV:corpus/SOURCES.md`, which is read-only. Every other run used `--repo` = my clone. |
| `… --repo . --from b8e485c --to ccc4bb3` (`--json` too) | 1 | `VIOLATION S041: cell \`anchor\`…`, `VIOLATION S041: cell \`teaches\`…`, `1 append-only violation(s)`; JSON `[('S041','cell-changed',['anchor','teaches'])]` |
| 10-pair sweep, every consecutive commit touching `corpus/SOURCES.md` (`1e41928…5e9ae6e`), `--json`, compared with `cmp` against the frozen tool's output | 9×0, `726f737..ccc4bb3` 1 | **byte-identical JSON on all 10 pairs** |

## Mutation matrix (scratch copies; each OLD string occurs exactly once; detector = mutated `--selftest`)

| mutant | source | frozen selftest | delivered selftest |
|---|---|---|---|
| M3a `header[:8]` (drop `opened`) | C2Survivors' exact edit | **rc 0, 14/14: survives** | rc 1, 15/42: killed (pin; the `opened` case alone also kills it, 39/42 with the pin removed) |
| M4b break at a blank line once `header is not None` | C2Survivors' exact edit | **rc 0, 14/14: survives** | rc 1, 36/42: killed (6 segment/blank-line cases) |
| AO-X1 exclude `kind` | `build/advice/MutBaselineDetectors.md` | **rc 0: survives** | rc 1: killed (pin; the `kind` case alone also kills it) |
| AO-X2 `added = []` | same | **rc 0: survives** | rc 1, 40/42: killed (exact `added` checks) |
| M1 `teaches` made mutable / M2 removed rows skipped / M3c / M4a | round-17 MutAppendOnlyGuard | killed | killed |
| N1–N10 against the new paths: any heading ends the section, no row-like scan, frozen non-`S` id skip, no bare-pipe rule, first heading wins, no header check, no pin, `decode(…,"replace")`, no separator width, duplicates allowed | this seat | n/a | all killed, each by its own named case (41/42, 39/42 or 40/42) |

The survivor count under this matrix drops from 4 to 0. This is my scratch run. L1's `survivors.py` family (c) is the official count.

Grading the new selftest fixtures with the frozen functions shows the old escapes. Frozen gives exit 0 on: an edit under a deeper subheading, a row-like line under `## Paths`, an edit to a `` `S002` `` row, an edit to an `s002` row, a second `Registry` section, a repeated header column, and a separator narrower than the header. Frozen crashes with `KeyError` when `--to` drops `opened`. The delivered tool gives 1 or 2 on each, as the cases expect.

## What the code cannot detect

- **Padding whitespace at cell edges.** Cells are compared after `.strip()`, which also strips Unicode whitespace such as NBSP. KQ22 says "byte-identical", but a change in leading or trailing whitespace is invisible. This design was already in place and is documented in the tool.
- **A consistent column reorder** (header and every row permuted together) changes no cell, so it exits 0. Cells are compared by name.
- **Ids outside the regex.** An id cell that does not start with `S` plus digits is neither parsed nor reported when it sits outside the registry section, e.g. `| [S041](#x) |` or `| S041a |`. The census regex does not count those either.
- **Things not modelled:** fenced code, HTML comments, setext headings and indented code. From reading the parser and running the cases, they can only add rows to the section (which agrees with the census) or end in exit 2. [INFERENCE] This was not fuzzed exhaustively.
- **Ranges.** The tool compares only two blobs. KQ22's sweep over every consecutive pair is still the round-end obligation.
- **Mutable-cell values** are not validated. Enums and paths are the census's job.
- **The selftest runner's own `ok` predicate** is not mutation-tested. The detectors of the detector stop at the three checks at `:561`.

## Known limitations and risks

- **New exit-2 paths could trip on a future layout that is legitimate:**
  - a prose line with a bare `|` inside the registry section;
  - any table whose first cell is an S-number outside `## Registry`, e.g. a corrections table under `## Search log` (the census would miscount such a table too);
  - a second `Registry` heading anywhere, including inside a fence;
  - a first separator whose width differs from the header's.

  None of these occurs in any of the 11 historical blobs or at e75cf68. I surveyed: header = contract header in every blob, no non-table lines in the registry, no row-like line and no `|` outside it.
- **Docs to refresh.** `SKILL.md:576` says "`--selftest` 14 cases". It is now 42 (39 cases + 3 checks). L1 or the ScribeSkillRound18 draft needs to update it.
- **Main runs under the M3a, M1, AO-X1 and M3c mutants** exit 2 on every pair, because of the pin. `survivors.py` grades family (c) by `--selftest` alone, so its counts do not change.
- **Coordination.** I confirmed C2Survivors' family (c) OLD strings, which each occur once: `:247` and `        if not ROW_RE.match(line):` at `:178`. I sent them the sha256.

## Installs, ports, cleanup

- **Installs:** none. No pacman, uv, npm or cargo was used.
- **Ports and servers:** none bound or started.
- **Writes:** only the two OUT files and this report. No lane file, frozen copy, jj state or git index was touched. Lane git use was read-only (`rev-parse`, `ls-files`, `show`).
- **Cleanup:** the clone `/tmp/kama-r18-C2AppendOnly-2` and the scratch `/tmp/kama-r18-C2AppendOnly-2-scratch` (mutants and synthetic repos) are deleted after this report.
