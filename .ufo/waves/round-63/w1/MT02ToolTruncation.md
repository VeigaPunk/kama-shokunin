# MT02ToolTruncation: round 63 C1 tool-side truncation hiding

Seat: MT02ToolTruncation (mutation-tester, leaf, advisory). Axis: operability. Claim: C1-r63.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD at start; read-only use, no lane mutation).
Scope: artificial truncation of the live completion capture, hidden by `_cap` / `http_post`, scored by the unmutated `tools/round63-c1-counter.py`.
This is evidence for the planner, not a verdict on C1.

## Baseline (unmutated tip)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

Live completion capture at the tip: status 200, body 618 bytes, body_truncated False, Content-Length 618 (server-sent).
`BODY_CAP` is 65536, so the live completion never reaches the cap.

## Mutants and verdicts

Each mutant is one commit on a clone of the tip. The unmutated counter was run from the clone's `tools/` with `--repo <clone> --tip <mutant commit>`.

| id | mutation (tool `tools/kama-completion-live.py`) | clone commit | counter one-liner (verbatim) | verdict |
|---|---|---|---|---|
| M1 | `_cap`: `body_truncated` forced `False` (no cut) | ad26aaf7 | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` | **SURVIVED** (met=True) |
| M2 | completion body cut to 200 B in `http_post`; `_cap` flag forced `False`; Content-Length kept | 722c259c | `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` | KILLED (live gate) |
| M2h2 | same cut, flag computed honestly (`len(raw) > cut`) | 519fc4e4 | `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` | KILLED (live gate) |
| M3 | `_cap`: `content-length` removed from captured headers (no cut) | 76e0cf0a | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` | **SURVIVED** (met=True) |
| M4 | combined: M2 cut + flag forced `False` + Content-Length dropped | 90f791a4 | `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` | KILLED (live gate) |
| CM1 | counter probe (not a tool mutant): `completion_untruncated` drops the `body_truncated is False` clause | 82a7ee9f | `tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[... trunc=1/2 ...]` | KILLED (trunc control escapes) |

Notes on the kill lines:
- The M2/M2h2/M4 live-gate errors name the same 16 failing checks: `completion_choice_shape, completion_deterministic, completion_envelope, completion_fingerprint, completion_finish_reason, completion_headers, completion_id_created, completion_model_id, completion_prompt_tokens, completion_request_bound, completion_timings, completion_untruncated, completion_usage, inconsistent:missing-checks, live_fp_capture, verdict`.
- A first M2h run (clone commit a7420bf6) left the flag computed against BODY_CAP, so it was dishonest too; it was discarded and replaced by M2h2. Its result was the same 16-check set (`errors=1 met=False`).
- Because the live gate fails before any control runs, `controls_targeted=0/0`. The collateral cap and the named-check rule (`is_hit`) never apply to these kills.

Patches: `out/MT02ToolTruncation/patches/*.patch`. Full counter outputs and stderr: `out/MT02ToolTruncation/*.out|*.err`. Receipts: `out/MT02ToolTruncation/receipts/`.

## Which receipt field the completeness verdict relies on

`completion_untruncated` (round63-c1-counter.py lines 185-189) is `env and c.body_truncated is False and is_int(c.body_bytes) and c.body_bytes == len(c.body.encode()) and (cl is None or cl digits == c.body_bytes)`. The fields it reads are:

1. `captures.completion.body_truncated`: must be the literal `False`.
2. `captures.completion.body_bytes` against `len(body.encode())`.
3. `captures.completion.headers['content-length']`, when present, against `body_bytes`. **Absent Content-Length is accepted** (`cl is None`).
4. `body_sha256` re-hashed by `grade()`. A tool that cuts and reseals the body passes this.
5. `env` (the envelope, i.e. the body parses as JSON) gates all of it.

## Does the live witness cover it?

No, not for completeness.
- `observe()` makes its own POST and returns the full header dict, but `score()` only reads `content-type` from it (`live_ctype`). It never compares Content-Length, `body_truncated`, or body size.
- The live completion body is 618 B, far under the 65536 B cap. No live run in this seat, or in the base run, exercises the truncation path.
- The two `trunc` controls (`body_truncated: True`, and Content-Length+1) edit the receipt after the fact. They test the receipt grader, not the tool's `_cap` logic, so a tool that lies about the flag on an uncut body passes (M1, M3).

## Findings (advisory)

1. **SURVIVED, M1 (hidden flag, no cut).** A tool that always reports `body_truncated: False` passes the counter. On the live path this is equivalent, because no live capture is ever cut. The counter has no live coverage of the cap.
2. **SURVIVED, M3 (Content-Length dropped, no cut).** The counter accepts a missing Content-Length by design (`cl is None`), and its witness does not record it. Dropping the header is invisible. The live server always sends Content-Length (618), so the tool can remove the only independent completeness signal without a trace.
3. **KILLED, but not by the truncation check (M2, M2h2, M4).** A cut completion body breaks the JSON envelope. That fails 16 checks at the live gate, and `completion_untruncated` is only one of them. M2 (lie) and M2h2 (honest flag) produce the identical failure set, so the counter reacts to the cut, not to the lie. Any cut completion is rejected; whether the flag lies is never separately tested. A JSON body cut mid-object cannot parse, so the envelope always shadows the flag clause on the live path.
4. **M2h2 is the only variant with an independent completeness signal.** Its receipt keeps Content-Length 620 against a 200 B body, so the `cl == body_bytes` clause would fail even if the envelope check did not exist. That clause is untested on the live path.
5. **CM1 shows the controls do grade the flag clause at the receipt level** (trunc=1/2, met=False when the clause is dropped). The gap is in the live witness and the tool-side path, not in the receipt grader.

Counter defect summary: the completeness verdict is graded only on receipt fields that the tool produces, with no outside check that the tool's cap logic was exercised. The live gate also treats a whole-receipt failure as a kill, so the 44-control collateral cap does not apply to tool-side kills.

Suggestions for the planner (not applied; the lane is untouched):
- Add an outside Content-Length witness: have `observe()` record the response Content-Length and compare it to the captured `body_bytes` and `len(body)`.
- Add a live probe whose completion exceeds the cap, so the truncation path runs against the real server and the verdict is checked on that receipt.
- Make absent Content-Length a failure on the live completion, or record its presence in the witness.

## Tool installs and records

No tools installed or upgraded. Pacman not used. Llama-server is the existing `~/.local/bin/llama-server` used by the lane tool, not changed.
Process note: the read tool returned a stale cached view of clone files on two occasions. Every edit was checked against the on-disk state (`sed` / `git diff` against the tip) before commit, and every committed diff was verified against the tip.

## Scratch

All clones and work dirs under `/fast/scratch/hyaku/kama-r63/w/MT02ToolTruncation/` are removed after receipts were copied to `out/MT02ToolTruncation/`. No commit, push, or mutating git on the lane or fleet. The lane was read-only (`git show`, `git cat-file`, `git rev-parse`, `git log`).

Final tally (M1 M2 M2h2 M3 M4 CM1): SURVIVED M1, SURVIVED M3; KILLED M2, M2h2, M4, CM1.
