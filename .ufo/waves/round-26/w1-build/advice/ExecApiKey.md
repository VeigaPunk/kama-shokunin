# ExecApiKey — wave-1 findings (C1, API-key enforcement family)

## Verdict

One confirmed, counted signature for the API-key enforcement family: `"authentication_error"`
(22 bytes), the 401-body type constant from the `--api-key` middleware. Counter on scratch
extract: **registered 1 counted 1** (all 12 predicate checks true).

## Fault confirmed

`llama-server` b11755 with `--api-key KEY` rejects any request to a protected route whose
`Authorization` (Bearer) or `X-Api-Key` value does not match, with `HTTP/1.1 401 Unauthorized`
and body `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`.
The lane already holds the `Invalid API Key` text at base, so the only new >= 20-byte signature
from this fault is the `"authentication_error"` constant.

## Candidate (one row — one fault)

- **signature**: `"authentication_error"` (22 bytes; sha256 3c4022711053fde2fa0d52041440f702c78a15aaddfbedcb86f44eb78f10598d)
- **channel**: http (status 401, body carries the signature)
- **args**: `["--api-key", "kama-r26-test-key"]` (allowed; `--api-key` is not in the counter's forbidden set)
- **request**: `GET /props`, no Authorization header (body null)
- **source**: `server-http.cpp:295` — `{"type", "authentication_error"},` (verbatim in pinned file; sha256 of pinned `server-http.cpp` = 24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb = counter pin)
- Source URL (pinned commit, anchored): https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp#L295 — access date 2026-10-23; quote (line 295): `{"type", "authentication_error"},` (10 words).
- Same constant also exists at `server-common.cpp:100` (`type_str = "authentication_error";`), emitted by `format_error_response(ERROR_TYPE_AUTHENTICATION)`; the live 401 body comes from the middleware, so `server-http.cpp` is the cited file.

## Reproduction (twice, own launches, my port block 47664-47667)

1. `GET /props` (no key) on 127.0.0.1:47664 → `HTTP_STATUS=401`, body above; server log `unauthorized: Invalid API Key`; exit codes all 0.
2. `POST /completion` with `Authorization: Bearer wrong-key-here` on 127.0.0.1:47665 → `HTTP_STATUS=401`, byte-identical body; same log line.
3. Healthy baseline on 127.0.0.1:47666 with correct key: `/health` (public, no key) 200, `/props` 200, `/completion` 200; no `authentication_error` anywhere in the log.

All three servers killed; ports 47664-47667 closed (ss shows no listeners). Full commands, outputs and exit codes: `RUNS.txt`; raw bodies: `run1-body.txt`, `run2-body.txt`; logs: `run1-server.log`, `run2-server.log`, `run3-server.log`.

## Checks (all verified)

- Base absence: `git grep -F -q -e '"authentication_error"' 1560e4d8 -- SKILL.md corpus` → exit 1; bare `authentication_error` → exit 1.
- Not in `--help`/`--version` output (grep count 0 each).
- Not in healthy baseline; not an echo of the request (request contains no such string).
- Clause-g adjacency: the 401 body embeds this signature, so at most one counted row can exist for this body (a second row with the same body would fail `g_distinct`). Also the signature is not a substring/superstring of any earlier counted signature — ordinal matters; if an earlier row's channel text contains `"authentication_error"`, this row would then fail `g_distinct`. [INFERENCE] No earlier lane row uses this string; the frozen counter's own run confirms it counts as row one.

## Counter run (scratch `git archive` of a23c0e0)

Scratch-only modifications: `corpus/SOURCES.md` row `S965` (names `server-http.cpp` and commit 704366d), `SKILL.md` new section `## Round-26 live error signatures` with row `KAMA-R26-APIKEY-01 | "authentication_error" | S965`, and registry at `<extract>/registry/error-signatures-r26.json` (note: the counter reads the registry from the lane root `registry/`, not from `.ufo/waves/round-26/`).

Command (flock-held): `flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out counter-receipt.json` → exit 0,
`registered 1 counted 1 target 12 met False not-counted []`. Receipt checks all true: id_unique, a_skill_row, b_long, b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown, e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct. Observed: status 401, channel_sha256 9956a1bd32a70211ff9f3c2e1af8a868de778deffa0689020fe5bea61027c713, excerpt matches the body above.

## Risks / notes

- The family yields exactly one row: every protected-route 401 shares one body, so the "one fault, one row" rule caps the family at one signature. No other >= 20-byte string exists in this 401 body (the other tokens are `Invalid API Key` (already held at base), `"code":401` / `{"code", 401}` (not verbatim in the source), `"message":"Invalid API Key"` (not verbatim in the source)).
- Public routes (`/health`, `/v1/health`, frontend assets) skip the middleware; they emit no error regardless of key.
- Ordering hazard for the L1: because clause (g) forbids a signature appearing in an earlier counted row's channel text, any row counted before this one whose 401/error body contains `"authentication_error"` would void this row, and vice versa. Keep the first API-key row in the file before any other row whose error body could contain this constant.
- No tooling installed this wave (no installs/updates needed).

## Files written (all under the wave's w1-build/out/ExecApiKey/ and advice/)

- `out/ExecApiKey/candidates.json` — registry entry (id/source.row `TBD` placeholders per assignment schema) + notes
- `out/ExecApiKey/RUNS.txt` — every command, output, exit code
- `out/ExecApiKey/run1-body.txt`, `run2-body.txt`, `run1-server.log`, `run2-server.log`, `run3-server.log` — raw evidence
- `out/ExecApiKey/counter-receipt.json` — frozen counter receipt (scratch run)
- Heavy scratch: `/fast/scratch/hyaku/kama-r26/ExecApiKey/` (run scripts, logs, counter extract)
