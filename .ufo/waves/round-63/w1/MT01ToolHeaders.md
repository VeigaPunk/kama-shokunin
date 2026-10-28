# MT01ToolHeaders — C1 operability: header lies and a canned-fake tool vs the r63 counter

Seat: MT01ToolHeaders (mutation-tester, leaf). Advisory only: findings below are not a verdict on C1.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (freeze amendment 1).
Counter: `tools/round63-c1-counter.py` (unmutated; read from clone at each tip).
Clones: all mutants committed only in my scratch clone (`git clone --shared`, toplevel asserted). Lane untouched.
Installs/upgrades: none. (`llama-server` 0.7.0-dev build 11755 is pre-existing at ~/.local/bin; not changed.)
Evidence: `.ufo/waves/round-63/w1/out/MT01ToolHeaders/` (receipts, diffs, counter-lines.txt, blindspot.py + output).

## Summary (SURVIVED mutants are counter/control defects)

| # | Mutant (tool only, counter unmutated) | Clone tip | Verdict |
|---|---|---|---|
| M1 | `_cap` pins captured headers to `{"content-type": "application/json"}` for every capture | 68be83a0 | **SURVIVED** (met=True) |
| M2 | `_cap` drops the `headers` key entirely | ac0156c4 | KILLED (met=False, named check `completion_headers`) |
| M3 | Real llama-server spawned and answers health/models/props/ownership; completion, tokenize and bad_request POSTs go to a local canned fake (fingerprint taken from the real binary's `--version`) | 02c93c1d | **SURVIVED** (met=True, 44/44, eval 3/3) |

Prominent: **M1 and M3 pass the counter with the defect present.** The C1 "44 targeted controls" and "3/3 evaluator self-test" are not sensitive to either the header lie or the canned completion body.

## Counter output lines (verbatim)

Unmutated base at tip 03a6a1d (run from clone `tools/`, `--work <scratch>/work-base`):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
M1 (tip 68be83a010f6ff9f5acfbf363cf0d3f83558396b), `--work <scratch>/work-m1`:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
M2 (tip ac0156c4319543cabb687e9658bd5150cba51e86), `--work <scratch>/work-m2`:
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_headers", "verdict"]
```
M3 (tip 02c93c1d08e1e60f294339207c179fb642d1fc3d), `--work <scratch>/work-m3`:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Note on M3 history (my own bug, not a counter finding): first commit 46b02cad read the fingerprint from `--version` stdout; llama-server prints it on stderr, so the run gave `met=False` with `errors=1 ... ["completion_fingerprint", "live_fp_capture", "verdict"]`. Fixed by reading stdout+stderr (02c93c1d). Mutants are not "killed" by that earlier, broken attempt.

## Real header baseline (what the server actually sent)

Base tool run directly (realhdr-receipt.json), completion capture:
`content-type: application/json; charset=utf-8`, `content-length: 619`, `server: llama.cpp`, `connection: close`, `access-control-allow-origin: ''`.
So M1 removes `content-length` and `server` from the receipt and changes the content-type value (params dropped; `ctype_json` strips params, so no grade difference).

## M1 — pinned headers: SURVIVED

What the counter can see (verified by code and by blindspot.py):
- `completion_headers` = `ctype_json(captured headers)`. A pinned `application/json` always passes it, so a non-JSON server answer is hidden from the receipt.
- The live witness recomputes `live_ctype` from its **own** request's headers. That is independent of the tool, but it only ever checks content-type, and only on the witness request, never compared to the receipt.

What the counter cannot see:
- Any header value other than content-type. Nothing compares receipt headers to the wire (witness or otherwise).
- Absence of `content-length`: `completion_untruncated` only checks Content-Length when the receipt carries one (`cl is None` passes). So a pinned tool hides a body-length mismatch.

Demonstration (`blindspot.py`, grade() of the counter applied to real receipts; output in `blindspot-output.txt`):
```
real-headers (base tool): captured completion headers = ['access-control-allow-origin', 'connection', 'content-length', 'content-type', 'server']
  genuine                        completion_untruncated=True completion_envelope=True inconsistent=['missing-checks']
  body rewritten, same content   completion_untruncated=False completion_envelope=True inconsistent=['completion_untruncated', 'missing-checks']
pinned-headers (mutant 1): captured completion headers = ['content-type']
  genuine                        completion_untruncated=True completion_envelope=True inconsistent=['missing-checks']
  body rewritten, same content   completion_untruncated=True completion_envelope=True inconsistent=['missing-checks']
honest capture, server sent text/plain: completion_headers=False
after pin-to-application/json (mutant 1): completion_headers=True
```
("missing-checks" is only because the direct, non-hold receipts lack `hold_released`; identical in both rows, not a confound.)
So a body re-serialised to bytes different from what the server sent is caught when the true Content-Length is recorded and passes once the header lie removes it.

Caveat: M1 used the real server's JSON header, so the lie is only "visible" through the parameter-less value and the dropped headers. I did not run a server that sends a non-JSON content-type (none available); the text/plain row is a re-score of a edited capture, not a live run.

## M2 — headers dropped: KILLED

`completion_headers` is recomputed from `None` and fails; the stored check (also recorded as False by the tool) matches, so `verdict` fails too. Met=False, controls not evaluated (`live_ok=0`). Kill is by the named check. Limit: this kills "no headers at all" only; a tool that keeps content-type and drops content-length (the M1 damage) is not killed.

## M3 — canned fake behind a real spawned server: SURVIVED

Mutant (tip 02c93c1d): after the real child is up and owned, `start_canned()` starts a local `ThreadingHTTPServer`; `http_post` redirects `/v1/completions` and `/tokenize` to it. The fake answers with a canned completion (`id: chatcmpl-canned`, text `' sat on the mat'`, usage 8/8, timings ok), canned tokenize (8 tokens), and a canned 400 for missing prompt. `system_fingerprint` = `b11755-704366d76` from the real binary's `--version` (stderr). Health, models, props, listener ownership, hold window, teardown and the counter's witness all hit the real child.

Direct receipt (T3-receipt.json) shows the tell: `"server": "BaseHTTP/0.6 Python/3.14.8"` on the completion capture, and `id: chatcmpl-canned` — yet `verdict: REQUEST_OK`.

Why the counter accepts it (code-verified):
- The only receipt-to-child binding for the completion is `live_fp_capture` (witness fingerprint == receipt completion fingerprint). Every answer from one build shares the `b<build>-<commit>` string, and the tool can read it from the same binary.
- `live_ptok` compares witness usage with witness tokenize for the **nonce** prompt only. The receipt's PROMPT usage is compared only with the receipt's own tokenize capture (`completion_prompt_tokens`), which the fake also canned consistently.
- `completion_deterministic` compares receipt vs receipt (canned, identical).
- `completion_request_bound` is genuine (the bytes the tool sent). Nothing binds the response to what the child produced.
- The 3-plant `eval_selftest` and 44 controls all mutate the receipt against the same grader; none targets a body that was not produced by the child.

Distinguishing data already in hand: the real child's answer to the same PROMPT at temperature 0, seed 7 is `' ground. She liked'` (realhdr-receipt.json); the canned fake answers `' sat on the mat'`. A witness-side re-issue of PROMPT compared to the receipt text would separate them. [INFERENCE] not implemented or tested as a counter change; cross-run determinism of the real child at temp 0 is assumed, not measured here.

## What a receipt-only counter can and cannot see (conclusion for C1 grading)

Can see: a receipt whose captured content-type is missing or non-JSON (M2 kill; `hdr` controls); a body that disagrees with a recorded Content-Length *when that length is recorded*; receipt-internal arithmetic and stored-vs-recomputed mismatches.

Cannot see: any header other than content-type (server, date, content-length if omitted); whether the captured headers match what the server sent (no wire comparison); whether the completion body was produced by the listener named in the receipt beyond one fingerprint string; text, id, usage or `server` identity of the PROMPT answer. The grader is re-deriving from bytes the same tool wrote, so a tool that lies consistently passes every re-derivation; only an outside contact that re-issues the **same** request to the child can catch a canned body, and the current witness does not do that for the receipt's prompt.

Advisory, not implemented here:
1. Witness re-issues PROMPT with the receipt's exact payload (temperature 0, seed 7, n_predict 8) and checks text and `usage.prompt_tokens` against the receipt, and tokenizes PROMPT itself (covers M3).
2. Witness compares the receipt's header set (at least content-type, content-length, server) with its own response headers for the same endpoint (covers M1 header value/absence).
3. Remove the `cl is None` pass in `completion_untruncated` when the body is JSON with a known byte count, or require content-length from the witness.
4. Add an `eval_selftest` plant for each: header pin (M1) and canned body (M3), so the evaluator refuses them.

## Verification tally
- Mutants run: 3 (+1 self-bug retry). KILLED: 1 (M2). SURVIVED: 2 (M1, M3).
- Baseline unmutated: met=True (44/44, 3/3) at 03a6a1d.
- Commits: only in my scratch clone (M1 68be83a0, M2 ac0156c4, M3 02c93c1d, plus 46b02cad retry). Lane and fleet untouched; no pacman, no installs.
- Scratch `/fast/scratch/hyaku/kama-r63/w/MT01ToolHeaders` removed after copying evidence.
