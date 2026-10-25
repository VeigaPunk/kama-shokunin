# RevLessonQuotes — round-36 wave-3 quote word-count audit

Seat: RevLessonQuotes. Date: 2026-10-24. Read-only; no corpus file, registry, or lane state was edited.

## Scope and method

- Lesson: `corpus/lessons/round-36.md` (83 lines, working tree).
- Registry: the S328 and S329 data rows of `corpus/SOURCES.md` (lines 214–215).
- "Quote" was operationalized as every quoted span in the lesson: double-quoted spans and backtick spans. Word count = whitespace split (`str.split()`), per the task definition. Extraction: per-line regex for backtick spans, masked before the double-quote pass; one typographic-quote scan (U+201C/201D/2018/2019: 0 occurrences; U+2026 ellipsis: 1, on L15).
- One parsing correction: the L47 awk recipe contains embedded backticks (`('$2 ~ ("`" l "`") ...`), so a naive backtick regex splits it into fragments (7+1+12). Counted once as the true span, first backtick after "recipe:" through the backtick before " over the campaign register": 20 words. The fragment ` l ` reported by the naive pass is an artifact of the recipe's internal quote characters, not a real quoted span, and is excluded.
- Registry quote cells were extracted by splitting each row on `|` and taking the cell containing ` — ` whose left side starts with `line`/`lines` (S328: `line 6 and route-list line 9 — …`; S329: `lines 790-791 — …`).

## Measured results — lesson `corpus/lessons/round-36.md`

Source-located and register-quoted spans (the spans presented as quotations of sources or of other documents):

| Line | Span | Words | ≤25 |
|---|---|---|---|
| 15 | `kama \| round-35 \| MISSION.md:29 still says operability + freshness …` | 11 | yes |
| 33 | "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." (Located quote, claimed 15) | 15 | yes — claimed 15 matches |
| 35 | "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead." (Located quote, claimed 16) | 16 | yes — claimed 16 matches |
| 51 | `DOI not in Semantic Scholar` | 5 | yes |
| 52 | `service_healthy : Specifies that a dependency is expected to be "healthy" (as indicated by healthcheck ) before starting` | 18 | yes |
| 53 | `对于vLLM/SGLang，可通过模型列表接口 <EAS_ENDPOINT>/v1/models 获取。` | 3 | yes |
| 54 | `python3 -m sglang.launch_server` | 3 | yes |
| 54 | `Page Not Found` | 3 | yes |
| 55 | `still-live` | 1 | yes |
| 56 | `check_health()` | 1 | yes |
| 56 | `EngineDeadError` | 1 | yes |
| 56 | `render-only servers always return 200` | 5 | yes |
| 56 | `render-only` | 1 | yes |
| 56 | `always return 200` | 3 | yes |
| 67 | `file ok` | 2 | yes |
| 76 | "18 words" | 2 | yes |

Incidental backtick spans (commands, paths, ids, flags, control output — code formatting, not quotations of a source; listed for completeness):

| Line | Span (abridged) | Words | ≤25 |
|---|---|---|---|
| 9 | C1 counting command | 6 | yes |
| 11 | C2 counting command | 6 | yes |
| 13 | `.ufo/waves/round-36/preregistration.json` | 1 | yes |
| 13 | `.ufo/waves/round-36/controls/c1-noop.out` | 1 | yes |
| 13 | `uncorrected 4 false_corrections 0 … met False` | 10 | yes |
| 13 | `.ufo/waves/round-36/controls/c2-base.out` | 1 | yes |
| 13 | `named 0 file_exists 0 cited_new 0 met False` | 8 | yes |
| 23 | `wc -w` | 2 | yes |
| 23 | `quote_words` | 1 | yes |
| 37 | `hosted-health-route-configuration.md`, `serving_container_health_route`, `containerSpec.healthRoute`, `AIP_HEALTH_ROUTE` | 1, 1, 1, 1 | yes |
| 39 | `sglang-native-api-deprecation-amendment-2026-10-23-r4.md` | 1 | yes |
| 41 | `http_server.py` | 1 | yes |
| 43 | `endpoint-health-probe-conventions.md` | 1 | yes |
| 47 | awk recipe (full span, see method) | 20 | yes |
| 47 | `payload-absent` | 1 | yes |
| 65 | `corpus/SOURCES.md` | 1 | yes |
| 67 | `.ufo/waves/` | 1 | yes |
| 67 | `used-by` | 1 | yes |
| 67 | `.ufo/waves/round-36/assimilation/validate-census.out` | 1 | yes |
| 69 | `  | S002 |` | 3 | yes |
| 69 | `collisions = S327` | 3 | yes |
| 76 | `quote_words` | 1 | yes |
| 77 | `provider.auth_error: 403` | 2 | yes |
| 77 | `seat-exit-codes.json` | 1 | yes |

Total quoted spans: 46 real spans (1 excluded regex artifact). Maximum measured count: 20 (L47 awk recipe, itself a command, not a quotation). Every span in both tables is 25 words or fewer.

## Measured results — registry rows `corpus/SOURCES.md`

| Row | Quote cell (after anchor ` — `) | Words | ≤25 | Byte-identical to lesson |
|---|---|---|---|---|
| S328 | "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." | 15 | yes | yes — exact string equality with lesson L33 |
| S329 | "Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead." | 16 | yes | yes — exact string equality with lesson L35 |

Cross-consistency (measured, string equality): the lesson's two Located quotes are byte-identical to the S328/S329 quote cells, and the lesson's claimed counts "(15 words)" / "(16 words)" equal the measured 15 and 16. No drift between lesson and registry on either new row.

## Findings by severity

- Critical / Major / Minor: none. Every quote in the lesson draft (46 spans) and both registry-row quotes measure ≤25 words; the lesson's own word-count claims for its two Located quotes (15, 16) are exact.

## Measured vs inference

- Measured: all word counts above (`str.split()` on the working-tree bytes); the two string-equality results; the absence of typographic quotes; the L47 re-spanning.
- Inference: the classification of backtick spans into "quotation of a source" vs "incidental code formatting" is a judgment call — both classes are listed in full, and the ≤25 verdict holds for either reading, so the conclusion does not depend on the classification.

## Residual risk and verification gaps

- Tokenizer dependence: `str.split()` counts standalone symbols as words (L15's two `|` tokens, `+`, and the ellipsis `…` inflate it to 11; prose-only it would be 7). A different tokenizer (e.g. punctuation-stripping or the C1 counter's `quote_words` extractor) could shift counts by a few on such spans. Margin is wide (max 20 vs bound 25), so no verdict flips under any reasonable tokenization, but this seat did not re-run `quote_words` itself.
- The L15 quote is truncated with a trailing `…` character; truncation is not a word-count defect and was not assessed as one.
- Registry-cell extraction used a literal ` — ` split and column-0 id match (text-level, not a semantic registry parser); the printed cell contents confirm the intended quote text was captured.
- Sources themselves (the SGLang pages) were not re-fetched here; this seat verified counts and internal consistency only, per scope.
