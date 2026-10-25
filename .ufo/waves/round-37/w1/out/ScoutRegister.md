# kama slice of the absent-defect register — re-derivation (round 37, w1)

Scope: re-run the §10 recipe over the campaign register, list the seven kama ids with
their class cells, and cross-check that slice against the verdicts recorded in
`corpus/lessons/round-36.md`. No fetches were made; every claim below is derived from
committed bytes on this host.

## 1. Recipe, verbatim from the lane's own record

`corpus/lessons/round-36.md:47` states the recipe as the operator recipe:

```
awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}'
```

Run over `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`
(cwd = the campaign wave dir; the file was not modified):

```
$ awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}' absent-defect-register.md
 S200   `payload-absent`
 S202   `payload-absent`
 S206   `payload-absent`
 S210   `payload-absent`
 S211   `payload-absent`
 S224   `payload-absent`
 S230   `payload-absent`
```

Guard check (so the slice is not silently short): the file holds 8 lines matching
``| `kama` |``; the eighth is the per-lane totals row `| `kama` | 7 |` at line 245,
which the `$3 ~ /round[0-9]+/` guard drops. Seven data rows survive, and no kama data
row is lost by the guard.

## 2. The seven ids and their class cells

| id | lane round | class cell | register line | cited source (register cell) |
|---|---|---|---|---|
| S200 | round1 | `payload-absent` | 92 | https://arxiv.org/abs/2312.07104 |
| S202 | round1 | `payload-absent` | 93 | https://docs.docker.com/reference/compose-file/services/ |
| S206 | round1 | `payload-absent` | 94 | https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ |
| S210 | round1 | `payload-absent` | 95 | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide |
| S211 | round1 | `payload-absent` | 96 | https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-推理引擎.md |
| S224 | round3 | `payload-absent` | 97 | https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ |
| S230 | round3 | `payload-absent` | 98 | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py |

This matches `corpus/lessons/round-36.md:47` on both axes it asserts: *seven* kama
rows, each carrying an S-id, and *the class cell in every one of them reads
`payload-absent`*. Agreement is exact, 7/7.

The ids are not globally unique in the register: `S224` also appears as a `mado` row
(line 145) and `S230` as a `tsukuroi` row (line 367, whose id cell is malformed as
``S230` ``). The lane cell in the recipe is what makes the slice well-defined, so the
re-derivation is reproducible only with the lane guard intact.

## 3. What the class cell asserts (needed to read the cross-check)

From `absent-defect-register.py:46-77`, observed in the generator's source:

- a row enters the register iff it has **at least one** ABSENT quote
  (`if f.get("verdict") != "ABSENT": continue`);
- `payload-absent` is assigned when the cited URL is neither in `failed_urls` nor in
  `no_locator_rows` — i.e. the class is a **provenance/reachability** statement
  (the fetch happened and the checker could not see the quote), not a per-quote
  fabrication verdict;
- the note cell is **boilerplate generated from the class** (`absent-defect-register.py:77`),
  not a per-row hand check;
- consequent: a row's class does not assert that *every* quote on it failed. S211 shows
  this directly — its census record carries two quotes, one with verdict `folded`
  (fold `markdown`) and one `ABSENT` (`still-live`); only the latter puts the row in the
  register.

Class cells therefore cannot contradict a hand-check verdict on their own dimension
(reachability vs. presence). The honest cross-check is: does the lesson's located
page text stand against the register's per-quote claim "the quote is in none of them".

## 4. Cross-check against `corpus/lessons/round-36.md`

Lesson verdict table at `corpus/lessons/round-36.md:51-57`; the shorthand in this
ticket ("S202/S206/S230 present; S200/S210/S211 absent; S224 not-located") maps 1:1
onto those cells.

| id | lesson verdict (line) | ticket shorthand | against the register's class claim | verdict |
|---|---|---|---|---|
| S200 | absent (:51) | absent | the quoted cell `DOI not in Semantic Scholar` is a status fragment, not a page sentence; not in the page text read | **agree** |
| S202 | present, not appended (:52) | present | page carries the span; register cell differs in quote style | **disagree** with the class claim |
| S206 | present, not appended (:53) | present | page carries the span; register cell differs in inline-code markup plus spacing | **disagree** with the class claim |
| S210 | absent (:54) | absent | `Page Not Found` is a status fragment; page instead carries `python3 -m sglang.launch_server` | **agree** |
| S211 | absent (:55) | absent | token `still-live` occurs nowhere in the page text read | **agree** (for the `still-live` quote; the row's other quote folded, see §3) |
| S224 | quote not located (:56) | not-located | compound span absent (`render-only`, `always return 200`); page does carry `check_health()` and a 503 on `EngineDeadError` | **agree as-quoted**, compound only |
| S230 | present, covered by the lane's own row (:57) | present | sentence carried at lines 790-791; same URL and anchor as lane row S329 | **disagree** with the class claim |

Tally: **agreement 4/7** (S200, S210, S211, S224-as-quoted), **disagreement 3/7**
(S202, S206, S230). No id is missing on either side and no id is present on one side
only: the *slice* agrees exactly, the *substantive verdicts* do not agree for three
rows.

## 5. Mechanism of the three disagreements (local evidence only)

The census records in `quote-lint-full-v5.json` reproduce the register verbatim (same
quotes, `verdict: ABSENT`, `fold: None` for all six single-quote rows). The fold ladder
that produced those `None`s is `quote-lint.py:635-640`:

```
["exact","whitespace","case","no-whitespace","markdown","nfkc","typographic","c-escape","de-wrapped","html","md-link"]
```

**S202 — quote style.** Register/census cell: `…expected to be 'healthy' (as indicated
by healthcheck) before starting a dependent service.` Lesson-recorded span:
`…expected to be "healthy" (as indicated by healthcheck ) before starting`. The two
strings differ in (a) `'healthy'` vs `"healthy"` and (b) a space before `)`. No fold in
the ladder folds single↔double quote style; the typographic fold normalizes curly
quotes to their straight forms, not one straight quote character to the other. A fold
for (b) exists but folds are applied one at a time, never composed, so (a) alone is
enough to return `None`. Reproduced locally: `match(lesson_span, register_quote) -> None`.

**S206 — markup plus spacing, two dimensions in one quote.** Register/census cell
carries literal backticks around the placeholder and no surrounding spaces:
`对于vLLM/SGLang，可通过模型列表接口`<EAS_ENDPOINT>/v1/models`获取。`; the
lesson-recorded span is `…接口 <EAS_ENDPOINT>/v1/models 获取。`. Reproduced locally with
the lesson's transcription as the page proxy:

```
strip-backticks + drop-whitespace  ->  True   (both normalize to
  对于vLLM/SGLang，可通过模型列表接口<EAS_ENDPOINT>/v1/models获取。)
```

`markdown` strips the backticks but keeps single spaces; `no-whitespace` drops the
spaces but keeps the backticks. No single fold sees the pair, so the row is
`payload-absent` even though the sentence is in the payload modulo markup and spacing.
This is the same class of linter blindness that `quote-lint.py:582-607` already
documents for `<br>` spans and markdown links — the fold ladder is deliberately
non-composing.

**S230 — the register quote is byte-identical to the sentence the lane already admits.**
The register cell at line 98 reads

```
Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead.
```

which is byte-for-byte the quoted sentence `corpus/lessons/round-36.md:57` records as
located at lines 790-791 of the *same* URL, and the same sentence that lane row S329
carries for the admitted entry `corpus/knowledge/sglang-native-route-deprecation.md`.
So the lane holds a committed fetch (2026-10-24, HTTP 200, 110718 bytes) in which the
span is present, while the census's captured document for that URL lacked it.

## 6. Remaining unknowns

1. **Why the census's capture of the S230 URL lacked a sentence the lane's own fetch
   found at lines 790-791.** Candidate causes, unresolved: a different snapshot of the
   `v0.5.22` blob at census time; a 200 response carrying a non-blob body (rate-limit or
   interstitial page) that the checker accepted as the document. The class is
   `payload-absent`, so the URL is *not* in `failed_urls` — the checker believed it had
   the document. Settling this needs exactly one read-only GET of that URL, which this
   item does not authorize ("No fetches needed", and it names no URL).
2. **Whether `(as indicated by healthcheck )` in the lesson span is a live-page artifact
   or a hand-transcription artifact.** Affects the S202 mechanism only in degree: the
   quote-style difference is visible from the bytes either way.
3. **Whether the register's S202/S206/S230 rows should be corrected.** Out of scope: the
   register is campaign-authored and read-only from this lane; the correction path is the
   round-37 lesson row (frozen C1), not an edit here.

## 7. Confidence

- Slice reproduction (ids, order, class cells, line numbers): **high** — deterministic
  command, recipe byte-identical to the lesson's own record, guard-exclusion explained.
- Exact 7/7 agreement of the slice with the lesson's two assertions at `:47`: **high**.
- Verdict mapping (4 agree / 3 disagree) and the S202 + S206 mechanisms: **high** to
  **medium-high** — both blobs read and the fold behaviour reproduced locally; the S206
  reproduction uses the lesson's own transcription as the page proxy, not a live fetch.
- S230 mechanism: **low** — the conflict is established, the cause is not.
