# RevEntryBytes — w3 r36 — entry draft source-quote re-fetch

Target: `corpus/knowledge/sglang-native-route-deprecation.md` (working tree, untouched by this seat).
Method: read the draft, re-fetched both cited URLs fresh on 2026-10-24 (one fetch each, `curl -fsSL`), then checked every located quote for verbatim text, stated line, and word count against the fetched bytes. Saved bytes under this seat: `.ufo/waves/round-36/w3/out/RevEntryBytes/`.

## Fetched bytes (measured)

| source | URL (tag v0.5.22) | lines | bytes | sha256 (this seat's fetch) |
|---|---|---|---|---|
| S328 | `raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx` | 467 | 17359 | `209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb` |
| S329 | `raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py` | 2961 | 110718 | `a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979` |

Byte sizes match the lesson draft's claims exactly (`corpus/lessons/round-36.md` lines 33, 35: "17359 bytes" / "110718 bytes").

## Quote-by-quote verdicts

**S328 — `native_api.mdx`:**

1. **Opening sentence — PRESENT at line 6.** Line 6 verbatim: `Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs. We introduce the following APIs:` The quoted sentence is the byte-exact prefix (15 words, `wc -w`; lesson claims 15 — match; ≤25). It is the first prose line of the page (lines 1–5 are YAML frontmatter), so the entry's "opens with one sentence" is accurate. Line 6 carries a second sentence after the quote; the draft never claims the line ends there.
2. **Route list at line 9 — PRESENT.** Line 9 verbatim: ``- `/get_model_info` `` in the bullet list (lines 8–11: `/generate`, `/get_model_info`, `/server_info`, `/health`). Entry's "route list, on line 9, still names `/get_model_info`" — exact.
3. **`/model_info` zero-count — HOLDS.** `grep -F '/model_info'` over the whole file: 0 matches. The count is genuinely zero, not a substring artifact: in `/get_model_info` the char before `model_info` is `_`, never `/`. Entry's "the count is zero" is correct.
4. **Worked example at line 71 — PRESENT.** Line 71 verbatim: `url = f"http://localhost:{port}/get_model_info"` inside a ` ```python Example ` block. Entry's claim — exact.

**S329 — `http_server.py`:**

5. **`/get_model_info` registration at line 786 — PRESENT.** Line 786 verbatim: `@app.get("/get_model_info")`.
6. **Deprecation warning at lines 790–791 — PRESENT, byte-exact after the language-mandated join.** Line 790: `"Endpoint '/get_model_info' is deprecated and will be removed in a future version. "`; line 791: `"Please use '/model_info' instead."` Two adjacent Python string literals inside one `logger.warning(` call (line 789), implicitly concatenated. Whitespace-joined they equal the draft's quote character-for-character (verified by string equality, not eyeball). Word count 16 (`wc -w` on the joined string); lesson claims 16 — match; ≤25. The two-line anchor is correct as written; a single-line grep for the full quote would falsely miss it.
7. **`/model_info` registration at line 796 — PRESENT.** Line 796 verbatim: `@app.get("/model_info")`.
8. **"Old handler still returns the result of `model_info()`" — SUPPORTED at line 793.** `return await model_info()` (the deprecated handler delegates to the new one). No line number is claimed for this in the draft; the behavior claim is exact.

Cross-checks beyond the entry: SOURCES rows S328/S329 (`corpus/SOURCES.md` lines 214–215) carry the same quotes, anchors, byte-anchored URLs, `used-by` path (exists), mined status and 90d recheck — all consistent with the fetched bytes. Lesson lines 33/35 word counts (15/16) and line anchors (6/9; 790–791, 786, 796) all re-derived and matching.

## Findings by severity

- **Blocker / major / minor: none.** Every quote is verbatim at its stated line, both word counts are mechanically re-derived and correct, both anchors resolve, and the zero-count claim survives a substring-artifact check.
- **Informational (no action):** the S329 quote exists only as two source lines joined by implicit concatenation — the draft's "lines 790–791" anchor already says this correctly; nothing to fix.

## Residual risk and verification gaps

- Single fetch per URL (finish-early bound). Byte-identity with the L1's opening fetch rests on exact size match (17359/110718); the lesson records no sha256, so byte-identity is size-supported, not hash-proven. This seat's sha256 values above enable hash comparison by any later seat.
- Tag identity: `raw.githubusercontent.com/.../v0.5.22/...` returned HTTP 200 for both paths, so the tag resolves and serves both files; I did not additionally pin the tag's commit via `git ls-remote`.
- The entry's §"Why this is its own ground" claims about other lane surfaces (runtime-health matrix, served-model-identity entries) were not audited — outside this seat's byte-attack scope.
