# RV01ToolV2 — line-by-line review of tools/kama-completion-live.py (v2)

Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (cloned via `git clone --shared` into scratch; checked out; toplevel asserted).
Judged on: operability. Milestone: review the build. Advisory leaf; no verdict on the frozen claims, no lane edits, no commits.
Evidence: .ufo/waves/round-63/w1/out/RV01ToolV2/ (results.tsv, receipts/, cli/, base.json, fake_server.py.tpl, mkfake.py).
Tools installed: none. Scratch removed after evidence copy.

## Method

- Read the whole tool at the tip (618 lines) and its imports from tools/kama-llamacpp-live.py (`_OPENER`, `hold_for_witness`, `port_owned_by`, `_listen_inodes`, `sha256_file`, `prepare_witness_dir`). The live module is byte-identical to base 7ee8cbdf (diff checked).
- Live baseline at tip with the pinned fixture (llama-server b11755 sha b6a31a8e…, stories260K sha 270cba1b…): `REQUEST_OK`, rc=0, all 22 checks evaluated and passed (base.json).
- Error paths exercised with a scripted fake llama-server (raw-socket HTTP, one mode per variant, same pinned model file, fake's own sha passed via `--server-sha256`). 16 scenarios + 4 CLI cases; every rc and verdict recorded in results.tsv. The fake only changes one response per mode; it answers /health, /v1/models, /props, /tokenize correctly.
- No registered consumer port touched; all servers on unregistered loopback ports picked by the tool. Foreign llama-servers (ports 1234/45669, and another seat's MT08ToolHold probe process) were not touched.

## Answer to the ok_env question

Yes, downstream checks vanish, and the verdict still FAILs. At tip, line 368 `if ok_env:` gates `completion_headers` through `completion_deterministic` (lines 370-463). When the envelope fails those checks are never written into `checks` at all (not even as `evaluated: false`). `completion_envelope` itself is recorded `evaluated=True, passed=False` (line 364), so line 566-567 sets `verdict=FAIL`, rc=1. Reproduced: `envelope_object` → FAIL rc=1, 10 checks present vs 22 on a good run (F6 below). The verdict is correct; the receipt is silent about what was skipped.

## Findings (ordered by severity)

### F1 — medium — uncaught exceptions skip the receipt and exit 1 (the "check failed" code)
Sites (tip):
- line 235 `server_sha = sha256_file(server)` — runs before the `try` at 277; a nonexistent or directory `--server` raises out of `main`.
- line 265 `os.makedirs(hold, exist_ok=True)` — before the `try`; not guarded like `prepare_witness_dir` at 267-271 (which *is* guarded and returns rc 2).
- lines 610-611 `open(args.out, 'w')` — runs after the whole lifecycle; a bad `--out` directory discards a completed receipt.
- lines 517-575 teardown — outside the `try` (504), so an exception there escapes unguarded (static reading; not reproduced).

Reproduction (scratch clone, cwd tools/):
- `--server $S/nope/llama-server` → Python traceback `FileNotFoundError`, rc=1, stdout 0 bytes, no receipt (cli/cli1_nonexistent_server.stderr.txt).
- `--hold-dir /proc/nope/x` → `FileNotFoundError` at makedirs, rc=1, no receipt (cli2).
- `--server <directory>` → `IsADirectoryError`, rc=1, no receipt (cli3).
- `--out $S/nodir/x.json` with a healthy run → full lifecycle runs, then `FileNotFoundError`, rc=1, receipt lost (cli4).
Impact: a harness that reads rc=1 as "endpoint failed" and stdout as a receipt gets a false FAIL with no evidence. Operator sees a traceback, not SETUP_ERROR.

### F2 — medium — served-but-malformed responses are graded as internal faults (SETUP_ERROR, rc=2), not FAIL (rc=1)
The outer `except Exception` at 504-513 wraps the grading code. Three paths escape the per-request handling:
- Grading code assumes shapes it has not checked: line 407 `u = cj.get('usage') or {}` then `u.get`/`u['…']` at 408-418 (non-dict truthy usage); line 455 `c2j['choices'][0].get('text')` (non-dict choice item in the second response).
- http.client exceptions that are not `OSError` escape `http_post` (lines 106-124): `BadStatusLine` from `_OPENER.open`; `IncompleteRead` from `resp.read` (only `OSError`/`URLError` are caught at 116/121).
Reproductions (results.tsv):
- `usage_str` (usage is a string) → `SETUP_ERROR` rc=2, `AttributeError: 'str' object has no attribute 'get'`. Expected FAIL on completion_usage.
- `nondet_nonobj` (second response `choices: [1]`) → `SETUP_ERROR` rc=2, `AttributeError: 'int' object…`. Expected FAIL on completion_deterministic.
- `bad_status_line` (`HTTP/1.1 garbage`) → `SETUP_ERROR` rc=2, `BadStatusLine`. Expected FAIL on completion_envelope.
- `chunked_cut` (chunked body cut mid-stream) → `SETUP_ERROR` rc=2, `IncompleteRead`. Expected FAIL on completion_envelope/headers.
Compare: `trunc_cl`, `timeout`, `bigbody`, `envelope_object` all correctly FAIL rc=1. The docstring (lines 36-37) reserves rc=2 for setup/internal faults; these are endpoint-graded failures. Whether a real llama-server produces the chunked/BadStatusLine shapes is unverified (inference); the usage/choices shape drift is a plausible version regression.
Fix direction: catch `http.client.HTTPException` in `http_post` and return status None; guard `isinstance(u, dict)` and `isinstance(choices[0], dict)` before use.

### F3 — medium — fingerprint regex accepts a trailing newline
line 75 `FINGERPRINT_RE = re.compile(r'^b\d+-[0-9a-f]{9,40}$')` with `.match` at line 398. `$` matches before a trailing `\n`.
Reproduction `fp_newline` (`system_fingerprint: "b11755-704366d76\n"`): REQUEST_OK, rc=0, `completion_fingerprint` passed. Expected FAIL. Fix: `fullmatch` or `\Z`.

### F4 — medium — response bytes are decoded with `errors='replace'`; no check grades UTF-8 validity
line 134 `'body': result['body'].decode('utf-8', errors='replace')`. The body_sha256 (line 133) is over raw bytes, so the hash is honest, but nothing in the verdict sees the invalid bytes.
Reproduction `nonutf8` (a raw 0xFF byte inside the completion JSON string on every completion): REQUEST_OK rc=0, all 22 checks pass. A response that is not valid UTF-8 (and therefore not valid JSON per RFC 8259) is accepted. Fix: a strict-decode check (e.g. `completion_utf8`) that fails on UnicodeDecodeError over the raw body bytes.

### F5 — medium — hold-window witness record is overwritten; `orphaned`/`waited_ms`/`pid` lost from the receipt
line 499 `receipt['hold'] = w` stores the full `hold_for_witness` return (schema, dir, port, pid, released, waited_ms, orphaned). line 560 `receipt['hold'] = {'dir': args.hold_dir, 'released': released}` replaces it before the receipt is emitted.
Reproduction: run with `--hold-dir` and an outside `release` file (runs/hold/receipt.json): `hold = {'dir': …, 'released': True}`. `orphaned` (did the hold end because the harness parent died?) and `waited_ms` are computed by the live primitive and discarded. The counter reads only `hold.released` (c1 counter, `hold = receipt.get('hold')`, the released read at line 259), so no counter breaks; the evidence for "ended by parent death vs release" is gone. Fix: delete line 560's assignment or merge (`{**w, 'dir': …}`).

### F6 — low — ok_env gating hides skipped checks from the receipt; request_bound is gated for no reason
Lines 368-463: every response-derived check is only added when the envelope passes. Verdict is correct (see answer above), but:
- The receipt has no record of which checks were skipped (`envelope_object`: 10 checks present, 22 on a good run).
- `completion_request_bound` (436-444) depends only on the tool's own request bytes, not on the response, yet it is gated; likewise the `tokenize` and `completion2` captures (425-427, 447-448) are simply absent.
Fix: record skipped checks as `evaluated: False, reason: 'not evaluated: completion envelope failed'`; move request_bound outside the gate.

### F7 — low — the NOT_EVALUATED branch is unreachable
Lines 564-571. `model_digest` (238) is always recorded with `evaluated = (passed is not None) = True` because it is a bool, so `evaluated_none` is always False when `checks` is non-empty. The docstring promise of rc=2 for "not-evaluated" (line 37) cannot happen. Static reasoning (not reproduced live; the branch is dead by construction). Remove the branch or make it reachable deliberately.

### F8 — low — non-bool `passed` leaks into the receipt
line 451-456: `det` is `[]` when `c2j['choices']` is an empty list (short-circuit returns the list). Reproduction `nondet_empty`: receipt has `"completion_deterministic": {"passed": [], ...}`. Verdict is correct (FAIL), but the receipt type is wrong. Fix: `bool(...)`.

### F9 — low — two checks cannot fail on the live path (tautologies at the tool layer)
- `completion_request_bound` (436-444): the recorded `request_body` and the bytes sent are the same object (`data` in `http_post`, line 90 → `urllib` `data=data`, line 102 → recorded). It re-hashes its own bytes; it cannot detect a sent/recorded mismatch. The independent binding has to come from the counter; I did not verify that the counter re-derives it (outside my item).
- `listener_owned` (320-322): hard-coded `True`; the falsy branch returns at 308-319 before it is recorded.
Not a defect in verdict arithmetic, but the receipt advertises a binding it does not perform.

### F10 — low — fixed 5 s timeout for the completion POST, no flag
line 86 default `timeout=POLL_TIMEOUT` (68: 5.0), used by the completion, tokenize and completion2 POSTs (353-354, 425-427, 447-448). No CLI option. A slow host can turn a legitimate answer into a `completion_envelope` FAIL (inference: not measured on a loaded host). Reproduction of the mechanism: `timeout` (fake sleeps 6 s) → FAIL rc=1, `completion_envelope`, `captures.completion.error` = timeout class. Correct grading, but no operator knob.

### F11 — low — SIGINT/SIGTERM produce no receipt and leave hold.json
No signal handler; `except Exception` (504) does not catch `KeyboardInterrupt`, so the receipt is never written and teardown is skipped. Reproduction: SIGINT during the hold window → rc=-2, stdout 0 bytes, no receipt. The child did not survive (PR_SET_PDEATHSIG; verified no leftover child carrying my scratch path). `hold.json` remains in the hold dir (its removal at 495-497 is skipped). Live primitive has a `Terminated` class (kama-llamacpp-live.py) that this tool does not use.

### F12 — low — docstring drift
- lines 20-21 "writes nothing outside the receipt and the hold dir": it also writes `server.log` into `--work` (line 283) and `hold.json` (line 490).
- lines 23-24 "body sha256": when `body_truncated`, the hash covers only the first 64 KiB (`raw[:BODY_CAP]` at line 100 feeds `_cap` line 133); the receipt does not say so.

### F13 — nit — dead/inert code
`finally: pass` (514-515); `if ok_env: … ` nesting is fine. `cap`'s `headers` is built from `dict(headers)` (line 99), which collapses duplicate header names before `completion_untruncated` reads Content-Length (not tested; static note).

## Checked and holding (no defect found)

- Baseline live request at tip: REQUEST_OK rc=0, 22/22 checks (base.json). Pinned digests match the host binaries.
- Body cap: `pad` (valid JSON followed by 70 000 spaces) → FAIL rc=1 on `completion_untruncated` (the cap is honoured; read is `BODY_CAP+1`, line 108/111).
- Timeout / server-down: FAIL rc=1, not an internal fault.
- Determinism: `nondet_text` and `nondet_empty` → FAIL rc=1 on completion_deterministic.
- Token count binding: `tokenize_mismatch` → FAIL rc=1 on completion_prompt_tokens.
- Envelope shape: `envelope_object` → FAIL rc=1, verdict FAIL.
- Teardown: `sigterm_ignore` → FAIL rc=1 on teardown_clean after 15 s, child SIGKILLed, port closed.
- Hold window: release file honoured (`hold-window.json`, `released: true`, rc=0).
- Proxy-free opener: `_live._OPENER = build_opener(ProxyHandler({}), _NoRedirect)` (live module), used via attribute lookup at line 106, so the swap is effective.
- Ownership/first-answer gate (308-319) and digest refusal (244-247, rc 2) behave as documented.
- Exit codes 0/1/2 match the docstring on every graded and setup path exercised, except F1 (rc=1 without a receipt) and F2 (rc=2 for graded faults).

## Residual risk / verification gaps

- Not run: the counters (round63-c1/c2); the controls and mutants are other seats' items.
- Not run: real-llama-server behaviour under load (F10 magnitude) or a real chunked/mid-stream crash (F2 reach in production).
- Static only: F1 teardown-path exception, F7 unreachable branch, F13 duplicate-header collapse.
- The fake is a test double: it proves the tool's branches, not what b11755 emits.

## Suggested checks for the main agent after the wave
- Re-run `results.tsv` scenarios against the amended tip (F1-F5 fixes will change rc expectations: usage_str/nondet_nonobj/bad_status_line/chunked_cut should become rc=1 FAIL; fp_newline and nonutf8 should become rc=1 FAIL; cli1-cli4 should become a SETUP_ERROR receipt rc=2).
- Confirm whichever counter control reads `hold` still reads only `released` after the F5 fix.

tally: 13 findings (medium 5: F1 F2 F3 F4 F5; low 7: F6 F7 F8 F9 F10 F11 F12; nit 1: F13) · fake scenarios 16: 10 match the docstring rc contract, 6 breach (usage_str, nondet_nonobj, bad_status_line, chunked_cut expected FAIL rc=1 got rc=2; fp_newline, nonutf8 expected FAIL got rc=0) · CLI cases 4/4 breach (rc=1, no receipt; F1) · live baseline REQUEST_OK rc=0
