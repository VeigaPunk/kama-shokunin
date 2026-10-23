# CtlSchemaProjection — C1 pre-data control

Arm: `CtlSchemaProjection` (C1 shortcut policy 2: declared-bounds projection).

## Candidate and behavior

The candidate adds 12 CSP rows to `SKILL.md`, 12 corresponding source rows S180–S191 to `corpus/SOURCES.md`, and `registry/chat-param-outcomes-r31.json`. Each claim is explicitly a schema-only projection from the pinned `server-schema.cpp` snapshot at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`; no adapter logic was consulted to select or describe outcomes. CSP-01 through CSP-05 project hard-bound rejection for `sse_ping_interval`, `max_tokens` (alias of `n_predict`), `n_indent`, `n_keep`, and `n_discard`. CSP-06 through CSP-12 project soft-limit clamps for `top_k`, `top_p`, `min_p`, `xtc_probability`, `xtc_threshold`, `temperature`, and `mirostat`.

## Exact retained evidence

- Candidate commit / C1 measured tip: `f04dcdcf67b539f676486c42c545ef3d11578dea`.
- Counter command: `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane . --repo . --tip f04dcdcf67b539f676486c42c545ef3d11578dea --out controls/CtlSchemaProjection/c1.json` (exit 0).
- Counter summary, verbatim: `registered 12 counted 0 target 12 met False not-counted ['CSP-01', 'CSP-02', 'CSP-03', 'CSP-04', 'CSP-05', 'CSP-06', 'CSP-07', 'CSP-08', 'CSP-09', 'CSP-10', 'CSP-11', 'CSP-12']`.
- Counter sha256 from `/usr/bin/sha256sum .ufo/waves/round-31/count-c1.py`: `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`.
- Full per-row evidence is retained in `c1.json`; every row has `live: {}`, so no candidate row was sent by the counter after its pre-live discrimination checks.

## Per-row counter result

No rows counted.

| Candidate rows | Counter reason | Why this schema-only projection fails the C1 predicate |
|---|---|---|
| CSP-01, CSP-02, CSP-03, CSP-04, CSP-05 | `reject-message-not-adapter` | These rows predict schema bounds errors. C1 accepts reject rows only when their message is adapter-authored in the pinned `server-common.cpp`; a schema-derived message is not sufficient evidence of that layer. |
| CSP-06, CSP-07, CSP-08, CSP-09, CSP-10, CSP-11, CSP-12 | `slot-not-a-mapping` | The projected slot key is the same as `param` for each field. C1 requires a different slot key to demonstrate an adapter-layer mapping; the schema projection alone does not supply one. |

The exact `not-counted` list above names every failed row. No counter defect was observed: the counter returned exit 0 and the expected `met False` result. This control intentionally misses the target; these rows must not be represented as adapter measurements.

## Limits

Only the pinned schema declarations, aliases, hard bounds, and soft limits support the candidate. No manual live probes were made, and no `server-common.cpp` adapter logic was read. The frozen C1 counter itself ran the required base request and skipped candidate requests because each row had a pre-live reason (`live: {}`).
