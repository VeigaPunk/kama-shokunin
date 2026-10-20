VERDICT: confirm — attacked all eight ReadyControls row oracles (verdict/reason/exit) and `why` claims against the landed `classify()`: every oracle and every `why` holds row-for-row; the only non-discrimination found is family-level, not row-level (exact vs substring, case-sensitive vs case-insensitive id matching).

# FamilyReadyControls — falsification probe

## Axes

1. Oracle correctness against `tools/kama-probe.sh` `classify()` and the C1 rule.
2. `why` accuracy, including provenance claims and frozen/current line numbering.
3. Discrimination: does each row kill the defect it names; is any row redundant?
4. Control status: do the rows pass the frozen probe (they must, if they are controls), and do they hold on the no-`python3` fallback?

## What I ran (commands, exits, excerpts)

Lane root for all commands: `/home/vgpnk/Projects/shokunin/kama-shokunin`.

```text
$ python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json
exit 0        tests=72 passes=72 failures=0
$ ... --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json
exit 1        tests=72 passes=55 failures=17
```

ReadyControls extracted from both records (`records[].family == "ReadyControls"`): **8/8 PASS on the current probe and 8/8 PASS on the frozen probe**. The independent frozen run reproduces L1's 55/17 split exactly, and every ReadyControls row is in the frozen passing set — the family is a genuine control set, not new behavior relabelled. `git log --diff-filter=A` shows `tests/probe-verdicts/ReadyControls.json` added in `b8e485c`, so the rows are new files pinning pre-existing behavior.

Per-row observed output (current probe; requests from the harness record were `GET /v1/models` then `GET /health` for all eight):

| Row | `--expect` | observed verdict/reason/exit | expected |
|---|---|---|---|
| `expect-exact-id` | `kama-ready` | `MODEL_OK` / `matched` / 0 | same |
| `expect-wildcard-star` | `*` | `MODEL_OK` / `expected-wildcard` / 0 | same |
| `expect-wildcard-dash` | `-` | `MODEL_OK` / `expected-wildcard` / 0 | same |
| `expect-different-id` | `qwen2.5-7b-instruct` | `MODEL_MISMATCH` / `served-id-mismatch` / 2 | same |
| `expect-gguf-path-basename` | `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` | `MODEL_OK` / `matched` / 0 | same |
| `served-id-carries-gguf-suffix` | `kama-ready` | `MODEL_OK` / `matched` / 0 | same |
| `ollama-name-not-served-id` | `stories260K` | `MODEL_MISMATCH` / `served-id-mismatch` / 2 | same |
| `second-data-id-match` | `tiny-vocab` | `MODEL_OK` / `matched` / 0 | same |

Additional runs:

```text
$ env PATH=/tmp/kama-r16-FamilyReadyControls/nopy-bin /usr/bin/python3 \
    tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --only <all 8>
exit 0        8/8 PASS with no python3 on PATH (grep/`HAVE_PY=0` fallback)
```

The C1 (`MODEL_LOADING`) rule cannot interact with these rows: the loading gate is `tools/kama-probe.sh:503-508` and requires `F_CODE = 503`; every ReadyControls route is `200`. All eight rows ran through the 2xx branch at `:522` and none emitted `MODEL_LOADING`.

## Why audit

No row carries a `file:line` citation at all: regex over the eight `why` strings for `*.sh|*.py|*.cpp|*.md|*.h` + line numbers returned `[]`. The only numbered reference is prose ("the `''|'*'|'-'` case arm"), and that arm is verbatim identical in frozen `kama-probe-before.sh:488` and current `kama-probe.sh:531` (the round diff only shifts it by +43 lines in total). There is therefore no frozen-numbering drift to falsify in this family.

Every claim checked against the code:

- `exact-id` / `different-id` / `wildcard-*`: `classify` gates the arm on `is2 && has_models` (`:522`), then `''|'*'|'-')` → `MODEL_OK`/`expected-wildcard` (`:530-532`); otherwise `model_matches` (`:535`) and the `mrc` cases (`:536-539`). Exact match is `[ "$sn" = "$exp_n" ]` (`:391`). Reasons match verbatim.
- `gguf-path-basename`: `normalize_id` drops the directory then one trailing `.gguf` (`:377`), applied to `--expect` at `:383`; `stories260K.gguf` → `stories260K`, served `stories260K` → match.
- `served-id-carries-gguf-suffix`: `normalize_id` is applied to each served id at `:388`, symmetric with `:383`; `kama-ready.gguf` → `kama-ready`.
- `ollama-name-not-served-id`: `served_ids` group order is `data[].id`, `models[].id`, `models[].name`, `models[].model`, top-level `id` with first non-empty group winning (`:355-366`); `aliases[]` is never read. `data[].id = kama-ready` wins, so `stories260K` is a mismatch.
- `second-data-id-match`: the `while` loop at `:386-392` compares every served id, so `tiny-vocab` (data[1]) matches.

Exit semantics: `eval_rows` --port mode sets drift for every non-`MODEL_OK` verdict (`:848-849`), so `MODEL_MISMATCH` → exit 2; `check.py` validates that expected exit is `0` iff `MODEL_OK` (`check.py:143-145`) and grades actual exit, verdict, reason, and `drift == (verdict != MODEL_OK)` (`check.py:339-347`). All eight pass that full comparison.

One provenance claim is stronger than the README suggests and is **true**: `expect-exact-id`'s `why` says the ready b11755 `/v1/models` body carries an Ollama-shaped `models[]`. The pinned README example (`sources/llama.cpp-704366d/README.md:1286-1311`) shows only `data[]`, but the live b11755 receipt body (`.ufo/waves/round-16/live/receipt.json`, `captures.models.body`) contains both:

> `"models":[{"name":"kama-stories260k",...}],"object":"list","data":[{"id":"kama-stories260k",...,"owned_by":"llamacpp",...}]`

The fixture is shape-faithful but not a literal capture: the live body has `data[].id == models[].name` (both the alias), while the fixture makes them differ (`kama-ready` vs `stories260K`) so precedence is testable. The `why` says "body", not "capture", so this is accurate; note it if the row is later read as a recorded surface.

## Discrimination matrix

I mutated the probe in `/tmp` (never a lane file), one semantic change per mutant, and ran the eight rows with `--only` for each; two mutants that survived were re-run over the full 72-row matrix.

| Mutant (one semantic change) | ReadyControls rows killed |
|---|---|
| drop `'-'` from the wildcard arm | `expect-wildcard-dash` only |
| drop `'*'` from the wildcard arm | `expect-wildcard-star` only |
| remove expected-side normalization | `expect-gguf-path-basename` only |
| remove served-side normalization | `served-id-carries-gguf-suffix` only |
| compare first served id only | `second-data-id-match` only |
| `models[].name` before `data[].id` | `expect-exact-id`, `ollama-name-not-served-id` |
| drop the `data[].id` group | `expect-exact-id`, `ollama-name-not-served-id` |
| union `data[].aliases` into served ids | `ollama-name-not-served-id` only |
| over-broad "every string in the body" extraction | `ollama-name-not-served-id` only |
| ignore `--expect` (always match) | `expect-different-id`, `ollama-name-not-served-id` |
| **substring instead of equality** | **none — 8/8 pass, and 72/72 pass** |
| **case-insensitive compare** | **none — 8/8 pass, and 72/72 pass** |

Both survivors are behaviorally live, not inert. Driven against a live loopback stub returning a semantically different id:

```text
served "kama-ready-Q4_K_M", --expect "kama-ready":
  pristine probe  -> exit 2, MODEL_MISMATCH / served-id-mismatch
  substring probe -> exit 0, MODEL_OK / matched          # false pass
served "KAMA-READY", --expect "kama-ready":
  pristine probe  -> exit 2, MODEL_MISMATCH / served-id-mismatch
  casefold probe  -> exit 0, MODEL_OK / matched          # false pass
```

## Findings (severity order)

1. **[medium] No ReadyControls row discriminates exact equality from substring matching.** The substring mutant replaces `[ "$sn" = "$exp_n" ]` with `case "$sn" in *"$exp_n"*)` and passes all eight rows and the entire 72-row matrix (`tests=72 passes=72 failures=0`, exit 0), while producing a false `MODEL_OK`/exit 0 for `kama-ready-Q4_K_M` vs `kama-ready`. The contract (`tools/kama-probe.sh:45`, "comparison is case-sensitive") and the code's `=` are currently correct; the regression risk is real because substring matching is a natural rewrite and normalization already strips only the basename + one suffix, so quantized filenames such as `stories260K-Q4_K_M.gguf` would false-pass against `stories260K`.
2. **[medium-low] No ReadyControls row discriminates case-sensitive comparison.** The casefold mutant passes 8/8 and 72/72 and false-passes `KAMA-READY` vs `kama-ready`. No fixture id differs from another only by case, so the documented case-sensitive rule has no assertion anywhere in the matrix.
3. **[low] The `unresolvable-id` reason is never asserted matrix-wide.** Reachable and correct in the landed code: `--expect /` and `--expect .gguf` both produce `MODEL_MISMATCH`/`unresolvable-id`/exit 2 (`classify:538`, `model_matches:384` returning 2), but `grep -l unresolved tests/probe-verdicts/*.json` returns nothing. A ReadyControls row with `--expect "/"` would pin the third mismatch reason at no extra harness cost.
4. **[low] Rows 1 and 4 have no unique catcher in the 12-mutant set.** `expect-different-id` fails only under "ignore `--expect`", which also fails `ollama-name-not-served-id`; `expect-exact-id` fails only under precedence mutants, which also fail `ollama-name-not-served-id`. Row 1 is the intended positive control and row 4 is the cleanest minimal negative (its expected id appears nowhere in the body), so both are worth keeping — but they are not independent evidence of the matching rule; do not count them as two kills. Every other row (2, 3, 5, 6, 7, 8) has at least one mutant that it alone catches.
5. **[nit] `served-id-carries-gguf-suffix` does not exercise the served-side basename half its `why` names.** The served id `kama-ready.gguf` has no directory, so only the `.gguf` strip is tested on that side; row 5 covers the basename strip on the expected side through the shared `normalize_id`, but a future split of the two call sites would leave served-side directory stripping untested. Adding a directory to the served id (e.g. `data[].id = "/models/kama-ready.gguf"`) would close it without changing the oracle.
6. **[nit] Row 5 embeds an absolute host path** (`/home/vgpnk/.cache/...`) in `expect`. It has no semantic effect (the probe does no path expansion on `--expect`), but the matrix is host-specific for a value whose only tested property is basename/`.gguf` stripping; `models/stories260K.gguf` would test the same rule portably.
7. **[positive] `expect-exact-id`'s Ollama-`models[]` provenance is verified**, not merely plausible: the live b11755 receipt body has both arrays, so the fixture's shape is right (see the Why audit). No line-number citations exist in this family, which is why it survives the frozen→current +43-line shift untouched.

## Residual risk and limits

- My 12-mutant set is not exhaustive; "no unique catcher" for rows 1/4 means within this set, not a proof that no discriminating defect exists.
- The substring/casefold results are a coverage statement about this matrix, not a defect in the landed probe: `model_matches` uses `=` and the contract says case-sensitive. They matter because `72/72` is being used as the round's calibration evidence.
- Mutants ran with `--only` over the eight rows; only the two survivors were confirmed over all 72 rows. Full-matrix results: substring and casefold both exit 0 with `tests=72 passes=72 failures=0`.
- The live-stub demonstration used a synthetic Python loopback server, not `llama-server`; no `llama-server` was started. `pgrep -x llama-server` is empty and nothing listens on 8080/34113 (`ss -ltn` checked). `measure.py` was not run.
- Inference markers: the claim that a substring matcher would false-pass quantized filenames is derived from the stub test above plus `normalize_id`'s exact suffix handling [INFERENCE for the specific filename example; the false-pass mechanism itself is measured].

## Installs

None.

## Scratch

`/tmp/kama-r16-FamilyReadyControls/` (mutants, run JSON, python-free PATH shim) — removed after the report was written.
