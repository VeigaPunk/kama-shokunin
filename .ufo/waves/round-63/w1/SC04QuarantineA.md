# SC04QuarantineA — kama quarantine slice, first half (hand-check)

Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09
Milestone: open and locate. Read-only. No counter, no lane edit, no commit. Scratch removed after receipts copied.

## Derivation (read-only)

Register: `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` (read bytes only).

`awk -F"|" -v l="kama" '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}'` yields 7 lines:
S200, S202, S206, S210, S211, S224, S230 (all class `payload-absent`).
First half, rounded up, = 4 lines: **S200, S202, S206, S210**.
Full rows read with the same filter (without the field trim) to get the cited URL and quote.

## Method

- Each source fetched with `curl -sL` (HTTP 200 for all four; final bytes sha256 in `out/SC04QuarantineA/raw-fetch.sha256`).
- Markup stripped with stdlib `strip.py`; quote searched literally, then with whitespace and quote-character normalisation; raw HTML also searched for the quote's wording.
- Receipts (text extracts, companion API responses, derivation) in `.ufo/waves/round-63/w1/out/SC04QuarantineA/`.

## Verdicts

| row | cited source | register quote | verdict | located text / reason |
|---|---|---|---|---|
| S200 | https://arxiv.org/abs/2312.07104 | `DOI not in Semantic Scholar` | **absent** (fabrication class) | The page carries the arXiv DOI `https://doi.org/10.48550/arXiv.2312.07104` ("arXiv-issued DOI via DataCite") and a navigation label "Semantic Scholar" under "References & Citations" ("Loading..."). No "not in" statement anywhere in the page. See caveat below. |
| S202 | https://docs.docker.com/reference/compose-file/services/ | `service_healthy : Specifies that a dependency is expected to be 'healthy' (as indicated by healthcheck) before starting ` | **present** (quote-character difference only) | `service_healthy : Specifies that a dependency is expected to be "healthy" (as indicated by healthcheck ) before starting a dependent service`. The register uses single quotes around `healthy`; the page uses double quotes. Substance and wording are identical; the register quote is a prefix of the page sentence. |
| S206 | https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ | `对于vLLM/SGLang，可通过模型列表接口`<EAS_ENDPOINT>/v1/models`获取。` | **present** (markup difference only) | `对于vLLM/SGLang，可通过模型列表接口 <EAS_ENDPOINT>/v1/models 获取。` Rendered in the HTML as `接口<code>&lt;EAS_ENDPOINT&gt;/v1/models</code>获取。`. The register's backticks are code-span markup from the register, not page text. |
| S210 | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide | `Page Not Found` | **absent** (fabrication class) | HTTP 200; page title `SGLangデプロイメント＆推論ガイド | Unsloth Documentation`, guide body present. `Page Not Found` occurs 0 times case-insensitively in the raw bytes and in the text. The only not-found strings are the Next.js framework `notFound` template inside the RSC payload: `404: This page could not be found.` and `This page could not be found.` That template is not the served status or content of this page. |

Tally (first half): **present 2 (S202, S206), absent 2 (S200, S210), unreachable 0.**

## Caveats and calibration

- **S200 is a status claim, not a quote.** `DOI not in Semantic Scholar` reads like a lookup note from the census, not sentence text. Verdict is absent on the register's own definition (quote in none of the cited sources). Companion checks, read-only, recorded as observations only:
  - `api.semanticscholar.org/graph/v1/paper/DOI:10.48550/arXiv.2312.07104` → HTTP 404 `Paper with id DOI:... not found` (observed today). So the note's *status* is plausibly true for the DOI key, but the register text is still not in the cited source.
  - `.../paper/ARXIV:2312.07104` → HTTP 429 twice (rate limit). Unresolved; not needed for the verdict.
- **S210 nuance.** The fetched page is a live guide, not a 404. The 404 strings come from the framework's payload, which would appear on any Next.js page. The quote itself is absent.
- **S202 and S206 are present**; their differences are typographic (quote glyphs, code-span markup, whitespace). Under a strict byte-match they would fail. Under the register's fabrication definition ("in none of them") they are not fabrications. Recording this so the L1 can decide whether the register should normalise punctuation before classifying.
- Nothing was unreachable: all four cited sources returned 200.
- Rows S211, S224, S230 are the second half and were not checked by this seat.

## Tools

No installs. Used `curl`, `awk`, `grep`, `sha256sum`, and python3 stdlib (`strip.py`). Nothing in `~/.local/bin` or on PATH was touched.

## Bounds held

Read bytes from `shokuknow` only; no campaign tool run there; no write there. No git/jj mutation. Live server work: none. Fleet-root files: not written.

Tally: present=2 absent=2 unreachable=0 (first half of kama quarantine, 4 of 7 rows).
