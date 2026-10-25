# R39Attack14 — upstream quote exact bytes

**Axes:** calibration; coverage.
**Item:** upstream quote exact bytes. Read-only inspection of lane scratch `/fast/scratch/hyaku/kama-r39`; no source or lane files modified, no mutation run.

Claimed quote: “The Unix timestamp (in seconds) when the model was created.” S472 cites OpenAI List models Markdown, §List models → Returns → `created`, line 17. Lane cache `openai-list.md` is 1,657 bytes, SHA-256 `2bbf06bb7a1687dbc9d25ce86c5d249b3f9d1e2c60efc32dbf7af2e4d052793f`, matching the lesson's recorded size/hash. Its exact line 17 bytes are `    The Unix timestamp (in seconds) when the model was created.` The quote occurs contiguously starting at byte offset 313 (zero-based), length 59, including four leading indentation spaces. Therefore the quote text itself matches verbatim after removing Markdown indentation, but it is not byte-for-byte equal to the complete source line (which has those four spaces). The lesson's phrase “quoted bytes resolve there” is supported as a substring; any stronger claim of exact whole-line equality would be false.

The same quoted text occurs in cached `openai-list.html` (609,612 bytes). S472's row, staged source note, amendment, and lesson reproduce the quote text with citation delimiters/typography. These are local cached artifacts; no live re-fetch was made, so they establish internal evidence agreement, not current upstream freshness.

**Finding:** no falsification of the stated quotation/content or line-location claim. Precision caveat: byte-exact content is an indented source-line substring, not the entire raw line. Calibration/coverage claims remain outside this narrow probe; no mutation detector was run. No tools installed.
