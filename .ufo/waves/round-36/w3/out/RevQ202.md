# RevQ202 — quarantine check, row S202

Target: https://docs.docker.com/reference/compose-file/services/
Date of fetch: 2026-10-24. Fetches performed: exactly one.

## Verdict
**present** — the page carries the span about `service_healthy` and "as indicated by healthcheck".

## Measured
- Single `curl -sSL` fetch: HTTP 200, no redirect (`FINAL_URL` identical to request URL), 885,676 bytes. Saved to scratch `.ufo/waves/round-36/w3/out/RevQ202/s202.html`; all searches below ran on that local copy, no refetch.
- Tags stripped + entities unescaped, whitespace normalized:
  - `service_healthy`: 5 match(es) in rendered text.
  - `as indicated by health*`: 1 match in rendered text (inside the `service_healthy` condition bullet).
  - `healthcheck`: 15 match(es).
- Quote (18 words, from the `long_syntax` / `condition` description):
  > "Specifies that a dependency is expected to be \"healthy\" (as indicated by healthcheck) before starting a dependent service."

## Inference (not measured)
The quoted wording is a near-exact carrier of the claimed span; only surrounding punctuation/whitespace differs from the phrase as given in the quarantine brief. The span is substantive support for any S202 claim about `depends_on: condition: service_healthy`, so quarantine on "span absent" grounds would not be justified for this row.

## Registry note
- Literal-text search of `corpus/SOURCES.md` for `S202` and for `compose-file/services`: no matches (this is text search only, not semantic proof of row absence). Per instructions, no row was appended and no corpus file touched.

## Bounds
No git/jj mutation, no writes outside `.ufo/waves/round-36/w3/out/RevQ202*`, no subagents, one URL fetch, no secrets read.
