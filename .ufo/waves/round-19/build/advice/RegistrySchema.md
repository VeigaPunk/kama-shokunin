VERDICT: confirm - schema and validator reject unknown keys, non-64-hex digests and duplicate ids; selftest 25/25 exit 0; each of 5 single-rule mutants fails its named case; the live lane registry (working tree, with optional doc) validates exit 0.

# RegistrySchema: round-19 BUILD advice

Scope: `registry/required-citations.schema.json` and `tools/validate-required-citations.py` (stdlib only, `--selftest`). Work copy: `/tmp/kama-r19-RegistrySchema` (`cp -a` of the lane at 8bf99ca; registry bytes re-synced to the live working tree). Deliverables mirror lane paths under `/tmp/kama-r19-RegistrySchema/out/`. Lane: this report is the only write; no lane file, index or git state changed.

## Deliverables
| file | sha256 |
|---|---|
| out/registry/required-citations.schema.json | 23c9d32165fa6c20bc7fe2766b1ef4570888f76fbf8a2772af0e2e2e355cdf82 |
| out/tools/validate-required-citations.py | eb031d29295b7991b37c7f81b3095d7719f247e6dea4855c3b4926e06963a2b3 |

Also: `out/SHA256SUMS`; `out/receipts/RECEIPT.txt` (every command with exit, stdout, stderr); `out/receipts/differential.tsv`; `out/fixtures/` (28 inputs); `out/mutants/` (5 evidence-only copies, do not integrate).

## Executed checks (cwd = work copy; exit observed)
- `python3 tools/validate-required-citations.py --selftest` → 0; `selftest: ok (25 cases + schema agreement)`
- `python3 tools/validate-required-citations.py` → 0; `ok: 3 rows`
- `python3 tools/validate-required-citations.py --registry /home/vgpnk/Projects/shokunin/kama-shokunin/registry/required-citations.json` → 0; `ok: 3 rows`
- `python3 tools/validate-required-citations.py --registry out/fixtures/does-not-exist.json` → 2 (unreadable)
- `python3 tools/validate-required-citations.py --selftest --schema /nonexistent/required-citations.schema.json` → 1 (schema unreadable)
- `check-jsonschema --check-metaschema registry/required-citations.schema.json` → 0
- `check-jsonschema --schemafile registry/required-citations.schema.json registry/required-citations.json` → 0; same with `--regex-variant python` → 0
- Mutants, `python3 out/mutants/m_X.py --selftest --schema registry/required-citations.schema.json`, each → 1 with a named failure: m_unknown `unknown key`; m_case `digest uppercase` (+ `uppercase id`); m_newline `digest trailing newline`; m_dup `duplicate id`; m_repeat `repeated key in row: want exit 2, got 0`. `diff` against the final validator → 1 each (one changed line).
- Differential, 28 fixtures × {validator, check-jsonschema ECMAScript default, check-jsonschema python-re}: 28/28 match predictions.
- `git check-ignore` on both new lane paths → 1 (not ignored; read-only).
- Installs: none. Pre-existing tools used: Python 3.14.8 (`/usr/bin/python3`), uv 0.13.0 (`~/.local/bin/uv`), check-jsonschema 0.38.2 (`~/.local/bin`, bundled jsonschema 4.26.0).

## Findings
1. Duplicate ids cannot be expressed in JSON Schema. check-jsonschema accepts `duplicate-id` (exit 0); the validator rejects it (exit 1). The schema description states this; the validator enforces it.
2. Repeated keys inside a row: `json.loads` keeps the last value silently (check-jsonschema exit 0). The validator refuses (exit 2, unusable).
3. Trailing newline. The default check-jsonschema (ECMAScript regex) rejects `id`, `path` and `doc` values ending in `\n` (exit 1). `--regex-variant python` accepts them (exit 0). Python `re.search` validators would accept them too [INFERENCE: from the probe, not every such tool tested]. The validator rejects all of them. Digests are closed in both modes by `minLength`/`maxLength` (exit 1).
4. The registry moved during this seat. My copy (8bf99ca) had 3 rows without `doc`. Lane HEAD is now `7229fa9` ("round-19: citation provenance…"); its registry blob is `5307d855`, 3 rows, no `doc`. The lane working tree (`bb47511d`, mtime 03:36, after my 03:13 copy) adds `doc` to every row and is uncommitted. My first draft rejected `doc` (exit 1 in both validators), which would have failed the live lane. The schema now accepts `doc` as an optional string; the working-tree file and the HEAD blob both validate (exit 0). Who made the working-tree edit is unknown [INFERENCE: L1 or a sibling seat].
5. Tightenings beyond the lane tool, which requires only non-empty strings (and a string `doc`). All current rows pass:
   - rev: exactly 40 lowercase hex. The token grammar allows 7–40, but the tool compares strings exactly, so short revs would only match short tokens.
   - path: no leading `/`, no commas, parentheses or whitespace (token grammar).
   - id: `^[a-z0-9][a-z0-9-]*$`.
   - doc: non-empty, no whitespace, no leading `/`. An empty doc would bind every document, since `endswith("")` is always true [INFERENCE: Python semantics, not executed against the tool].
   L1 should confirm each one.
6. The lane working-tree `tools/citation-provenance.py` (sha `9632e4a9…`) differs from HEAD (`00998d52…`). This seat did not run it.

## Not done / for L1
- Not wired into `citation-provenance.py` or into the round-19 lesson, SCORECARD or SOURCES. Suggested gate order: `python3 tools/validate-required-citations.py`, then `python3 tools/citation-provenance.py` [INFERENCE: usage].
- `citation-provenance.py` and the lane gates were not run. The fleet card assigns gates to the parent.
- The target says `/tmp/out`; the acceptance says `/tmp/kama-r19-RegistrySchema/out`. Delivered to the latter; `/tmp/out` was not written, to avoid colliding with sibling OUT dirs.
- No subagent dispatched (leaf seat). No persistent servers started.
