# SrcReopen5 — re-open rows S188 and S189 (C1 depth falsification)

Item: verify pinned quotes on corpus/SOURCES.md rows S188 and S189 against the
round-31 llama.cpp 704366d snapshot
(`.ufo/waves/round-31/sources/llama.cpp-704366d/`, sha256-pinned by
SNAPSHOT.json, server-common.cpp sha256
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442 — verified
identical to the pinned hash).

Both rows sit inside `## Registry` (header line 9; rows at lines 200-201;
next header `## Paths` at 205). Both quotes were re-checked by printing the
pinned line with `sed -n` and substring-testing the row quote against it.

Result lines (no disagreements):

- `S188: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md + registry/chat-param-outcomes-r31.json exists yes`
  - URL: `.../tools/server/server-common.cpp#L1521` @ 704366d, access date 2026-10-23
  - L1521 verbatim: `        throw std::invalid_argument("top_logprobs requires logprobs to be set to true");`
- `S189: quote-verbatim yes; words 3; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md + registry/chat-param-outcomes-r31.json exists yes`
  - URL: `.../tools/server/server-common.cpp#L1530` @ 704366d, access date 2026-10-23
  - L1530 verbatim: `            llama_params[item.key()] = item.value();`

FINDING: no defect on S188 or S189 — both quotes are verbatim on their pinned
lines, ≤25 words, inside `## Registry`, and both `used-by` paths exist.
These two rows do not falsify C1's S180-S191 claim.

Caveats / residual risk: S189's quote also occurs at line 1170 of the same file
(not unique, but the pinned line is correct). `used-by` existence was checked
as path existence only; whether those files actually consume the sources was
not verified. Only 2 of the 12 new rows were in scope for this seat.

Evidence: `.ufo/waves/round-31/w2/out/SrcReopen5/report.md` (full RESULTS
block) plus `verbatim-check.txt`, `evidence.txt`, `table-header.txt` in the
same directory.
