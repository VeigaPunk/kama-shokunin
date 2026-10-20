VERDICT: confirm — M3a and M4b structurally survive the frozen selftest; unvalidated duplicate headers provide a further direct immutable-cell bypass.

## Findings

### High — A duplicate target column can hide an actual immutable-cell edit

The parser accepts duplicate header names, then `dict(zip(header, cells))` overwrites earlier cells with later ones. `run_check` discards the target header and `diff_registries` derives compared cells only from the source header. Frozen `tools_sources-append-only.py:137-152` says “`row = dict(zip(header, cells))`” and rejects duplicate *row IDs*, but never rejects duplicate column names; `:216-225` says “`to_rows, _ = parse_registry(...)`”.

[INFERENCE] Concrete bypass: start with the normal unique header and S001 `source=src-x`. In `to`, append a second `source` column, change the original source cell to `edited-url`, and put `src-x` in the appended duplicate. The row dictionary retains the last `source` value, so the comparator sees the original value and can return clean. Likewise, appending a second `id` column while changing the first ID cell leaves the last ID as the row key; `id` is excluded from `immutable_cols` (`:172-185`).

**Killing selftests:** reject duplicate header names with exit 2, including a target-side duplicate `source` with the hidden edit above and a duplicated `id` header with the first ID changed. Compare source/target schemas by unique column-name set before diffing; allow a pure order change. Also add a target-only new column case and require schema drift to fail closed rather than silently grade only source columns.

### Medium — M3a is a real selftest survivor

The advice identifies M3a as deriving immutable fields from `header[:8]` (`MutAppendOnlyGuard.md:27`, quote: “`immutable columns taken from header[:8]`”). In the frozen fixture the ninth field is `opened` (`tools_sources-append-only.py:264-277`, quote: “`opened="2026-10-20"`”), and the comparator otherwise compares every non-mutable field (`:172-185`, quote: “`if old[c] != new[c]`”). No current selftest case changes `opened`; the cases are defined at `:294-377`. [INFERENCE] Therefore the described mutant drops `opened` and still satisfies all present selftest expectations; it also misses an in-place `opened` edit.

**Killing selftest:** change only S001 `opened` from `2026-10-20` to `2026-10-21`; expect exit 1 with S001. Add the same single-field mutation for `kind`, `tier`, and `scope` to cover all currently untouched immutable cells.

### Medium — M4b is a real selftest survivor; its “added row” probe needs an added-ID assertion

The advice describes M4b as stopping after the first blank following the header (`MutAppendOnlyGuard.md:31`, quote: “`first blank line after the header`”). Frozen `parse_registry` currently continues across non-row lines (`tools_sources-append-only.py:116-121`, quote: “`if not ROW_RE.match(line): continue`”). But fixtures join all rows contiguously and put the blank only after them (`:281-282`, quote: “`"\n".join(rows)`”). [INFERENCE] A mutant that stops at a blank between row blocks is therefore not exercised by the current selftest and can miss later rows.

**Killing selftest:** make `from` contain S001, a blank line, then S002; make `to` contain only S001; expect exit 1 and S002. The advice's second-block S003-addition probe (`MutAppendOnlyGuard.md:49-50`) is useful only if selftest also asserts `added`: the current runner discards that result (`tools/sources-append-only.py:384`, quote: “`violations, _ = diff_registries(...)`”), and an added-only case still exits 0.

### Medium — Registry-section selection is fail-open on a repeated heading

The parser selects the first Registry heading (`tools/sources-append-only.py:105-111`, quote: “`if REGISTRY_RE.match(line)`”) and stops at the next heading of any kind (`:116-120`, quote: “`if HEADING_RE.match(line): break`”). [INFERENCE] A target with a first Registry table copied from the old version followed by a second Registry heading/table containing an edited row is graded using only the copied table; the edited table is ignored. The parser does not require a unique Registry section.

**Killing selftest:** add a second Registry section after a complete unchanged copy of the source rows, change S001's `source` only in the second section, and expect exit 2 (ambiguous/malformed registry) or a violation. A unique-section check should fail closed.

### Medium — Dropping an immutable target column raises an uncaught KeyError

The parser requires only `id` and the mutable columns (`tools_sources-append-only.py:154-160`, quote: “`for needed in {"id"} | MUTABLE_CELLS`”). If `to` drops an immutable column such as `opened`, parsing can succeed but `diff_registries` indexes `new[c]` (`:182-185`, quote: “`old[c] != new[c]`”). `run_check` catches `ParseError` only around parsing and calls `diff_registries` after that handler (`:218-225`, quote: “`violations, added = diff_registries(...)`”). [INFERENCE] This yields an uncaught KeyError/traceback rather than the documented exit-2 ungradable result. Reject mismatched schemas before comparison and test a dropped immutable column for exit 2, no traceback.

### Low / contract-dependent — Edge whitespace is normalized despite the byte-identical rule

Frozen `split_cells` strips each cell (`tools_sources-append-only.py:80-82`, quote: “`cells.append("".join(buf).strip())`”); its docstring also says values are compared “after leading/trailing whitespace strip” (`:27-31`). KQ22 states `corpus/QUALITY.md:123` that cells “`stay byte-identical from a row's first commit`.” If that means literal cell bytes rather than normalized Markdown padding, changing leading/trailing whitespace around an existing immutable value is accepted. [INFERENCE] Add a raw-row fixture that changes only cell-edge whitespace and expect a violation if byte identity is literal; otherwise document that the contract compares trimmed cell values, not bytes.

## Checks that are not escapes

- **Column reordering alone is handled by name.** Rows become dictionaries keyed by the parsed header (`tools_sources-append-only.py:142`, quote: “`dict(zip(header, cells))`”), and the comparator selects named columns (`:172-185`). [INFERENCE] Reordering a unique header and moving its row cells with it preserves values; a changed `source` under that reordered header remains detectable. Selftest both reorder-only → exit 0 and reordered-header-plus-source-edit → exit 1.
- **Duplicate data-row IDs are rejected.** `parse_registry` raises on a repeated parsed ID (`tools_sources-append-only.py:150-152`, quote: “`if rid in rows_by_id`”), and `run_check` parses both source and target blobs (`:216-217`). The existing selftest puts the duplicate only in `from` (`:364-365`); add a target-side duplicate case expecting exit 2. This does not close the distinct duplicate-*header* bypass above.
- M3b is correctly described as a null mutation: the base immutable list has seven entries, so truncating that list with `[:8]` does not remove a field (advice `MutAppendOnlyGuard.md:33-38`). M1 and M2 are killed by the current `teaches` and removed-row cases (`tools_sources-append-only.py:305-315`); M4a is exercised by the blank between Registry heading and header in `_REGISTRY` (`:264-269`).

## Residual risk and verification gaps

This is static confirmation by reading the frozen parser and its selftests; I did not execute mutants, the historical revision pairs, or tests, so expected mutant outcomes above are marked [INFERENCE]. The reported historical sweep and receipts in `MutAppendOnlyGuard.md` were not independently rerun. LSP was unavailable: `xd://lsp` is not a mounted device, so no references/definition/diagnostics were available; no grep was used as semantic proof. No installs or upgrades.