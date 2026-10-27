# Item 3 — kama quarantine slice, hand-checked (2026-10-26, seat X1Assimilation)

Slice derived with the operator recipe (register read-only, not edited):

    awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
      {print $4, $5}' /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
      -> 7 rows, every line carries an S-id and class `payload-absent`
         S200 S202 S206 S210 S211 S224 S230   (register lines 92-98)

Register header claims 194 rows / 324 absent quotes fleet-wide; the kama slice is
7 rows, all classed `payload-absent` (no `unreachable` row). The register's own
caveat stands: "A quote the checker could not match is a CANDIDATE, not a verdict."

Fetches below are live from this host on 2026-10-26 (`curl -sSL --max-time 60`,
HTTP code and byte count recorded); every cited source answered HTTP 200.

Id join: 6 of the 7 slice ids no longer exist as registry rows (they occur only
in the lessons tables of rounds 35-37); S206 is the only slice id still in
`corpus/SOURCES.md` (line 209, `mined`). The register's `id` column therefore
cannot be joined to today's registry; each verdict below is on the *document*
and the *quote* the register names.

| id | register class | cited source (fetch) | what the page actually carries | verdict |
|---|---|---|---|---|
| S200 | `payload-absent` | https://arxiv.org/abs/2312.07104 — HTTP 200, 43 012 B | `DOI not in Semantic Scholar` occurs **0** times. `Semantic Scholar` occurs once, as the sidebar link `https://api.semanticscholar.org/arXiv:2312.07104`. The cell is the `s2` error string quoted in a lane note (`quote-lint-full-v5.json` findings[574]: "`aaron papers fetch 2312.07104` failed … s2 \"DOI not in Semantic Scholar\"") | **cell is not a page quote** (census extracted a note's prose under `binding: id`). Not fabrication of the paper; the cell is unfaithful to its source. Refuse the cell; adopt only a located sentence from the abs/HTML text |
| S202 | `payload-absent` | https://docs.docker.com/reference/compose-file/services/ — HTTP 200, 887 026 B | `<code>service_healthy</code>: Specifies that a dependency is expected to be "healthy" (as indicated by <a …>healthcheck</a>) before starting a dependent service.` (`grep -c 'Specifies that a dependency is expected'` = 2). The page uses **double** quotes and a hard line break after `"healthy"`; the registry cell uses straight **single** quotes | **payload present**; ABSENT is a fold gap (quotation-mark variant `'`→`"` plus a wrapped line). Adoptable after a fidelity fix: quote with `"healthy"` and collapse the wrap |
| S206 | `payload-absent` | https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ — HTTP 200, 40 874 B | `…对于vLLM/SGLang，可通过模型列表接口<code …>&lt;EAS_ENDPOINT&gt;/v1/models</code>获取。` (`模型列表接口` ×2) | **payload present**; ABSENT is a fold gap on inline-code markup (the page renders the endpoint as `<code>`/`&lt;…&gt;`, the cell writes it in backticks). Row already adopted as S206, mined; nothing to append |
| S210 | `payload-absent` | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide — HTTP 200, 1 308 985 B | `Page Not Found` occurs **0** times; `launch_server` ×7, incl. the SGLang launch argv highlighted as `sglang.launch_server --model-path …`. The cell comes from a conflict note about a *search snippet* (`quote-lint findings[580]`: 'a search snippet in Step 1 labelled this path "Page Not Found"; the direct fetch … returned HTTP 200') | **cell is not a page quote** (note prose). The page is live and carries the row's real anchor. Refuse the cell; the row's located quote (lane S345) stands |
| S211 | `payload-absent` | https://github.com/AaronYang238/llm/blob/35b83cee…/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md — HTTP 200, 494 370 B | `still-live` occurs **0** times; `RadixCache` ×8, e.g. the code block `├─ RadixCache      # 基数树 prefix cache（SGLang 招牌）`. The cell is lane prose (`quote-lint findings[582]`: 'The lane's two SGLang anchors that the frontier flags as "still-live" were re-opened'); the same id's real quote already matched under the `markdown` fold (findings[581], verdict `folded`) | **cell is not a page quote**; the row's quote is present under fold. Not fabrication; refuse the cell, keep the folded anchor |
| S224 | `payload-absent` | https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ — HTTP 200, 386 143 B | First half located: `await engine_client(raw_request).check_health()` and `except EngineDeadError:` → `return Response(status_code=503)`. Second half `render-only servers always return 200` occurs **0** times (`render-only` ×0) — it is the lane's own S004 summary sentence, quoted inside a "Relation to the lane's existing row" note | **compound cell, half located / half lane summary**. Not fabrication; the cell must be split and each half re-quoted (the 200-on-render-only claim belongs to S004's `teaches`, not to this page) |
| S230 | `payload-absent` | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — HTTP 200, 110 718 B | The sentence exists as two **adjacent Python string literals**, lines 790-791: `"Endpoint '/get_model_info' is deprecated and will be removed in a future version. "` + `"Please use '/model_info' instead."`. Concatenation reproduces the quoted sentence exactly; the literal text of the file never contains it on one line | **payload present at message level**; ABSENT is a fold gap for split literals. Adoptable with a two-literal anchor (or quote each literal line separately) |

## Bottom line

No row is a fabrication of absent source text: 6 of 7 cells are traceable to a
real page, and the 7th (S200) is a tool-error label rather than invented source
prose. Three cells are not quotes at all (S200, S210, S211 — census extracted
note prose under `binding: id`); one is half lane-summary (S224); three are
fidelity/markup artifacts (S202 quote marks, S206 inline code, S230 split
literals). Adoption of any row still requires the cell to be replaced by a quote
located in this round's fetch; the register is unedited.

Consistency: rounds 35-37 recorded the same present/not-located split (round-37
lesson lines 59-65: S202/S206/S230 present, S200/S210/S211/S224 absent or
not-located). This check adds the mechanism per row (which fold is missing) and
the S230 two-literal explanation.
