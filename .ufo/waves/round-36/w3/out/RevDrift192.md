# RevDrift192 — S192 quoted-sentence check vs fetched bytes

Seat: w3 leaf RevDrift192. Date: 2026-10-24. Scope: verify registry row S192
(OpenAI Chat Completions API reference — response_format,
https://developers.openai.com/api/reference/resources/chat/index.md) against
one plain fetch. Registry not edited.

## Verdict

**The row's quoted sentence occurs in the fetched bytes. No drift. The source
is fully readable by a plain fetch; no "unfetchable" reason applies.** The row
verifies as quoted.

## Measured results (single fetch, scratch: .ufo/waves/round-36/w3/out/RevDrift192/)

- Fetch: `curl -sS -L` one request. HTTP 200, `content-type:
  text/markdown; charset=utf-8`, 240,530 bytes, no redirect
  (`url_effective` = requested URL). Body saved as `body.fetched`.
- Anchor resolves: `Body Parameters` heading at line 28; the
  `response_format` parameter bullet ("`response_format: optional
  ResponseFormatText or ResponseFormatJSONSchema or
  ResponseFormatJSONObject`") at line 1008, inside that section. The
  `ResponseFormatJSONSchema` sub-object with `json_schema {name, description,
  schema, strict}` and the `strict` semantics paragraph are present (lines
  ~1032–1061), matching the row's scope claim.
- Quoted sentence: present verbatim in the raw bytes, soft-wrapped across
  lines 1012–1014:
  `Setting to ` + backtick + `{ "type": "json_schema", "json_schema": {...} }`
  + backtick + ` enables / Structured Outputs which ensures the model will
  match your supplied JSON / schema.`
- Whitespace-normalized exact comparison (all whitespace folded to single
  spaces, python3 `str.split/join`):
  - row quote with the source's backticks around the JSON literal: **True**
  - row quote with backticks stripped: **False** — the only delta between the
    row's quote and the source is that the row drops the markdown backticks
    around `{ "type": "json_schema", "json_schema": {...} }`. Wording is
    otherwise character-identical. This is quoting style, not drift.

## Reason to record for the row

None required. If the audit pipeline needs a status word: **verified / no
drift**. The row's "accessed 2026-10-24" date matches today's fetch, and the
`.md` mirror serves the full page body to a plain fetch (HTTP 200,
text/markdown).

## Residual risk / verification gaps

- Any audit that substring-matches the row's quote against single raw lines
  (e.g. `grep -F` of the full sentence) will report 0 hits because the page
  soft-wraps the sentence mid-clause. Comparison must whitespace-normalize
  before declaring drift. This is a tooling caveat, not a row defect.
- The fetch is a point-in-time sample of a live docs endpoint
  (on-release recheck cadence per the row); later upstream edits are outside
  this verdict.
- Scratch artifacts (`body.fetched`, `headers.txt`) live in the seat dir only;
  no lane file, git index, or jj state was touched.
