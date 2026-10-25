# RevS329 — falsification pass on the S329 bytes (sglang v0.5.22 http_server.py)

Seat: w3/RevS329 · 2026-10-24 · single fetch, no corpus mutation, no row appended.

## Measured results

**Fetch.** URL: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — fetched once via the session fetch tool at 2026-10-24, wall time 1.475 s.

- **HTTP status: 200 OK (success path)** — *inference note, flagged*: the fetch tool does not expose a numeric status field; it reports "full response body, returned verbatim" and delivered the complete file (tool-reported 110,870 bytes; 2,961 body lines), which is its success path. No byte-level alternative (403/404 body, partial body) is consistent with the payload.
- Body line numbering below is the raw file's own numbering: the saved tool output carries a 2-line wrapper (note + blank) ahead of the body, so original line = saved line − 2. Cross-checked: saved line 3 is the file's line 1 (`# Copyright 2023-2024 SGLang Team`), and saved 2,963 = body line 2,961.

**Line numbers (original file, v0.5.22 tag):**

| What | Line(s) | Verbatim bytes |
|---|---|---|
| `/get_model_info` route registration | **786** | `@app.get("/get_model_info")` |
| handler def | 787 | `async def get_model_info():` |
| docstring | 788 | `"""Get the model information (deprecated - use /model_info instead)."""` |
| warning call opens | 789 | `logger.warning(` |
| warning message | **790–791** | `"Endpoint '/get_model_info' is deprecated and will be removed in a future version. "` + `"Please use '/model_info' instead."` |
| old handler delegates | 793 | `return await model_info()` |
| `/model_info` route registration | **796** | `@app.get("/model_info")` |
| replacement handler def | 797 | `async def model_info():` |

Each decorator occurs exactly once in the file (grep over the full body found single hits at 786 and 796; no second registration of either route).

**Deprecation warning, quoted (16 words, ≤25):**
"Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead."

## Comparison with the draft bytes

**S329 row (SOURCES.md line 215).** Claims: warning at "lines 790-791" with text `Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead.` → **VERIFIED**. Line span 790–791 is exactly the message string; text matches verbatim, including the two-part concatenation.

**Entry draft (corpus/knowledge/sglang-native-route-deprecation.md, line 4 + line 16).** Four micro-claims, all **VERIFIED**:
1. source line refs "lines 786, 790–791 and 796" — all three land on the claimed bytes.
2. "`/get_model_info` is still registered, at line 786" — yes, decorator at 786.
3. handler warning text — matches verbatim at 790–791.
4. "The replacement route `/model_info` is registered at line 796, and the old handler still returns the result of `model_info()`" — decorator at 796; `return await model_info()` at 793.

The draft's scope disclaimer (line 22, handler "still registered and still answers") is consistent with the source: registration at 786 and a live delegation at 793.

## Divergences

**None.** The fetched v0.5.22 bytes confirm every line-number claim and every quoted string in the S329 row and the entry draft. One nuance, not a falsification: the drafts cite 790–791 for the warning; the enclosing `logger.warning(` call opens at 789. The citations are accurate as given (they point at the message text itself); a future re-cite could add 789 for the call site.

## Evidence chain

1. Fetch tool call (single) → full body saved; wrapper-offset determined by reading saved lines 1–5 and cross-checking the copyright header.
2. Grep over the saved body for `get_model_info|model_info|deprecat` → the table above, all offsets − 2.
3. Read of saved lines 783–801 → verbatim block quoted in the table.
4. Read of entry draft (26 lines) and Grep `-C 3` of SOURCES.md line 215 → claims enumerated and checked one by one.

Fetched artifact retained at the session tool-results path; no second fetch performed.

## Confidence

- High (observed): all line numbers, the warning text, the delegation at 793, single-registration of both routes.
- High (measured): fetch success and body integrity (full verbatim body, line count 2,961).
- The status code 200 is inferred from the tool's success path rather than read off a wire-level field — flagged above; no evidence contradicts it.

**Verdict: the draft landing bytes survive falsification. S329 row and entry draft are accurate to the v0.5.22 source. No row appended; no corpus file touched.**
