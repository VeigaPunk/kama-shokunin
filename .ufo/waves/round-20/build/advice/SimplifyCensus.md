VERDICT: confirm - One stdlib script per claim (~200–350 lines); registry-driven C1 cells; C2 header+identity keys only; reuse git/subprocess/receipt patterns already in lane.

## Axes
**calibration 7** (C1), **operability 8** (C2), plus **complexity** and **falsifiability**: registry-driven populations, no `tools/lib/`, L1-failable stdout only.

## C1 — `tools/error-verdict-census.py` (minimal shape)
**One file**, ~200 lines: `load_cells` → `git_show_bytes(lane, rev, path)` → `run_cell(tmp, instrument_bytes, argv, env)` → `observed_class(stdout, stderr, exit, parser_id)` → `main` tally.

**Keep (claim-bearing):** `--cells PATH`, `--lane`, `--frozen-rev` (default pin), stdout line `cells=N frozen_misclassified=A current_misclassified=B`, `--json` with per-cell `{id, frozen_class, current_class, expected_class}`, exit **0** iff `current_misclassified==0` and all ran, **1** if any current misclass, **2** harness fault; `--selftest` with two stub instruments (verdict-launderer vs honest).

**Cut without losing falsifiability:**
- KillCensus auto-discovery / SKILL-wide scan → population lives only in `registry/error-injection-cells.json`.
- `--current-only` / `--frozen-only` → both arms always (claim is before→after).
- Pluggable Python import of instruments → always `subprocess` + `sys.executable` (mirror `install-tree-grid.py:49–53`).
- Generic JSONPath / AST classifiers → **3–4 `parser_id` literals** in census: `gate_invalid_prefix` (`INVALID ` + exit 1 = verdict per `check-receipt.py:2233–2236`), `grid_status` (`install-tree-grid.py:110–111`), `citation_counts` (`citation-provenance.py:238–241`), `survivors_selftest` (mirror `survivors.py:931–956` semantics, not import).
- Per-cell HTML logs, `--verbose`, retry policy, parallel workers (serial is fine for ≤20 cells).
- Embedding cell injection builders in census → cells JSON carries `argv`/`env`/`files` stubs (CellDesign owns injection).

**Registry minimal row:** `id`, `instrument` (lane-relative path), `mode`, `inject` (dict), `argv`, `expected_class`, `parser_id`, optional `expected_failure` (M5).

**Reuse instead of new code**
- Frozen bytes: copy `git_blob` from `.ufo/waves/round-18/c1/measure.py:193–205` (not a new helper module).
- Subprocess gate call: same shape as `tests/llamacpp-live/install-tree-grid.py:49–53`.
- Git lane probe: `tools/citation-provenance.py:38–49` (`git cat-file`) for sanity, not for instruments.
- Do **not** fold into `measure.py` or `survivors.py` — separate instrument keeps C1 file-set separable.

## C2 — `tools/gguf-identity.py` (minimal shape)
**One file**, ~280 lines: `read_header_and_kv(f, budget)` → `identity_keys(meta, arch)` → optional `reconcile_receipt(path, keys, sha)` → `main`.

**Keep:** streamed `sha256`; magic/version/tensor_count/kv_count; LE v2/v3; BE detect+decode; fail-closed bounds (fixed constants, not flags); identity keys listed in round-20 context; exit **0/1/2/3** map; `--json`; `--receipt` with `model_sha256_post` bind + declared `<arch>.context_length` vs `.captures.props.fields["default_generation_settings.n_ctx"]`; `--selftest` in-memory fixtures (≥6 cases: valid v3, bad magic, truncated, unknown type, duplicate key, identity-mismatch receipt).

**Cut without losing falsifiability:**
- CLI `--max-kv` / `--max-str` → module constants (e.g. 4096 kv, 1 MiB string) still enforced.
- GGUF v1 / full enum torture in v1 tool → defer to `tests/gguf-identity/make_fixtures.py` + falsify wave; v1 line in oracle checklist only.
- Reading any key beyond identity set + keys needed to locate `<arch>` → skip tensor names entirely (never seek past metadata).
- Separate reconcile module/file → single `reconcile_receipt()` (~60 lines).
- Host population census, Ollama blob walker, mmap whole file → out of tool (GgufHostCensus seat).
- `model_alias` vs `general.name` as more than one JSON field → report both strings, no extra exit code.
- `exceeds-train` as exit branch → JSON `context_relation: within|exceeds-train|unknown` with exit 0 when sha bind ok (warning not failure per claim).

**Reuse instead of new code**
- Streamed digest: same loop as `tools/kama-llamacpp-live.py:171–176` (inline duplicate; no new shared module).
- Receipt JSON: stdlib `json.load`; field paths verified on live receipt (see commands below).
## Evidence (executed)
| Command | Exit |
|---------|------|
| `git clone … && checkout 37bd4c5…` | 0 |
| `python3 …/citation-provenance.py --registry /nonexistent` | 2 |
| `python3 …/install-tree-grid.py --selftest` | 0 |
| `git show 37bd4c5:tests/llamacpp-live/install-tree-grid.py \| wc -c` | 0 (8675) |
| `jq … receipt-1.json` (n_ctx 256, model sha matches stories) | 0 |
| `head -c 4 stories260K.gguf \| xxd` → `47475546` (GGUF) | 0 |
| `uv run --with gguf python -c "import gguf"` | 0 |

Installs: none. Sketch: `.ufo/waves/round-20/build/out/SimplifyCensus-2/minimal-contract.json`
