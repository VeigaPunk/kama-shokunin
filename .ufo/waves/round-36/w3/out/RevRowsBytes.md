# RevRowsBytes — S328/S329 row falsification (r36 w3)

Scope: the last two data rows of `corpus/SOURCES.md` (S328 at line 214, S329 at line 215),
against the fetched sources. Registry untouched. Fetched bytes cached in
`.ufo/waves/round-36/w3/out/RevRowsBytes/` (native_api.mdx, http_server.py).

## Verdict

**No defect found in either row.** Every check in the assignment passes on the fetched bytes.

## Measured results

Both rows are the last two data rows of the `## Registry` table (line 216 is blank, then `## Paths`).
Header (SOURCES.md:11): `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by` = 11 columns.

Fetch (2026-10-24): both URLs HTTP 200.
`docs/docs/basic_usage/native_api.mdx` = 17359 bytes; `python/sglang/srt/entrypoints/http_server.py` = 110718 bytes —
byte sizes match `corpus/lessons/round-36.md` §33/§35 exactly.

| Check | S328 (line 214) | S329 (line 215) |
|---|---|---|
| pipe-delimited column count | 11 = header 11 | 11 = header 11 |
| literal or escaped pipe inside a cell | none (`\|` absent; split on `\|` yields exactly 11 cells) | none (same) |
| recheck cell | `90d` — valid Nd; already used by 18 existing rows (house vocabulary) | `90d` — same |
| used-by cell | `corpus/knowledge/sglang-native-route-deprecation.md` — exactly the entry path; file exists; `corpus/` prefix matches house style (37 rows use `corpus/knowledge`; S327 at line 213 is the immediate precedent) | same |
| opened cell | `2026-10-24` — valid ISO; matches lesson §33 "Opened 2026-10-24", README "opened on 2026-10-24", entry `verified-at: 2026-10-24` | `2026-10-24` — same, matches lesson §35 |

### Anchor-at-cited-line (fetched bytes)

**S328.** Line 6 of native_api.mdx contains, byte-exactly, "Apart from the OpenAI compatible APIs,
the SGLang Runtime also provides its native server APIs." (grep -F on line 6: 1 match; it is the
prefix of line 6, which continues "We introduce the following APIs:"). "route-list line 9" is
`` - `/get_model_info` `` — the route list does name it. Cross-checks of the anchor/teaches claims:
literal string `/model_info` occurs **0** times in the whole file (grep -Fc: 0), so the teaches
"never names /model_info" holds; `/get_model_info` occurs only at lines 9 and 71; line 71 is
``url = f"http://localhost:{port}/get_model_info"`` as the entry states.

**S329.** Line 786 is `@app.get("/get_model_info")` and line 796 is `@app.get("/model_info")` —
the entry's registration claims hold. Lines 790–791 are the two adjacent string literals
`"Endpoint '/get_model_info' is deprecated and will be removed in a future version. "` and
`"Please use '/model_info' instead."` (inside `logger.warning(`, line 789). The anchor quote is the
byte-exact concatenation of those two literals — Python's implicit join, i.e. exactly what the
handler emits (`ast.literal_eval` join == anchor quote: True). The old handler still ends
`return await model_info()` (line 793), as the entry claims.

## Observations (non-defects, recorded for the hazard they resemble)

1. **S329's quote is not contiguous bytes on one source line.** It spans two string literals
   (790 + 791), joined by the language. The anchor honestly cites the range `lines 790-791`, and the
   cell carries no "verbatim" label, so this is not an S174/S176-style false verbatim claim
   (SOURCES.md round-30 decision record). No action needed.
2. The entry says "the count is zero" for `/model_info`. Precisely true for the literal string
   `/model_info`; the bare substring `model_info` appears on 2 lines, both inside `/get_model_info`.
   The entry's phrasing ("The string `/model_info`") is the accurate one.
3. The S329 row anchor carries only lines 790-791 while the entry additionally cites 786 and 796.
   The row's teaches is grounded by 790-791; the registrations live in the entry. Consistent, not a gap.

## Residual risk and verification gaps

- **Single mirror, single fetch.** Both anchors verified against one fetch of
  raw.githubusercontent.com at tag `v0.5.22`. A tag is re-pointable upstream; the rows pin by tag,
  not by commit SHA, so the anchor truth is "as fetched 2026-10-24". No second mirror was consulted.
- **Working-tree scope.** I verified the draft bytes in the lane working tree, not a landed commit;
  what actually lands may differ from what I read.
- **Pre-existing, out of scope:** SOURCES.md's round-31 note (line ~205) routes validation through
  `scripts/sources-census.sh validate`, but no `scripts/` directory (and no `sources-census*` script)
  exists in the working tree — only census output logs inside other seats' sandbox copies. This
  predates and does not touch S328/S329; recorded because the row-adjacent validation path is stale
  in the working tree. I did not check historical revisions.
