# KR01C1Fidelity — C1-r63 predicate fidelity (attack)

Seat: KR01C1Fidelity (leaf, advisory, no subagents). Round 63, kama lane. Axis: operability. Claim: C1-r63.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD; confirmed `git -C lane rev-parse HEAD`).
Scope: read freeze.txt C1 sentence against tools/round63-c1-counter.py and its docstring, and against
tools/kama-completion-live.py (v2) at the tip. Counter line numbers below are tools/round63-c1-counter.py at the tip;
"tool:" lines are tools/kama-completion-live.py at the tip; "llm:" is tools/kama-llamacpp-live.py at the tip.
Scratch /fast/scratch/hyaku/kama-r63/w/KR01C1Fidelity removed after receipts were copied to
.ufo/waves/round-63/w1/out/KR01C1Fidelity/ (receipts, mutant diffs, counter outputs, probe driver and output).
Tools installed: none. No lane or fleet file was edited; all mutations were committed only in my scratch clones.

## 0. Bottom line

- The sentence is identical in freeze.txt and the counter docstring (script check after whitespace normalisation: equal).
- No round-63 receipt, receipt schema string or registry row carries the sentence (see §1).
- Of the clauses, the counter enforces most of what the sentence names, with three real gaps that a counter-level
  survivor or a probe demonstrates: (F1) the serving process is never proven to be the pinned llama.cpp binary, only
  that the tool-declared child owns the port; (F2) the /tokenize count is bound to a string the counter never reads;
  (F3) "strict timings" is type-strict, not plausibility-strict. Two named clauses have no targeted control (server
  re-hash, nonce) and their enforcing lines survive mutation (CM1, CM2).
- Baseline counter at the tip: met=True (44/44, 3/3, errors=0). Four seat mutants all SURVIVED (§5).

## 1. Sentence identity (freeze vs docstring vs receipt label)

- freeze.txt "Predicate (same sentence as tools/round63-c1-counter.py docstring)" and counter docstring lines 6-21:
  identical after collapsing whitespace (checked with a script; `freeze==docstring: True`).
- Receipt label: none carries the predicate. Round-63 receipts (tool `checks[*].reason`, tool:320-554) are
  per-check strings, not the sentence; the tool `schema` field is `kama-completion-live/v2` (tool:67). The counter
  output line (counter:725-728) has no predicate label and does not print the tool blob sha.
- The only other C1 label is SCORECARD.md:3269, which sits under the **Round 62** heading (SCORECARD.md:3258-3298).
  It quotes the round-62 tip dc5e1010 and a round-62 output format (`fake_rejected=…`, which the round-63 counter
  does not emit). It is not a round-63 label; it is listed here so that nobody reads it as one.
- PROVINCE.md:190 paraphrases C1 and omits the request-bytes, nonce, listener and 44-control clauses; it is a summary,
  not the sentence.

## 2. Clause → enforcing line (counter at tip unless stated)

| Sentence clause | Enforced at | Finding |
|---|---|---|
| "byte-pinned tools/kama-completion-live.py" | tip blob read: 642-655; dep 656-662; registry 663-667 | Pinned by tip commit only. No digest constant for the tool or `kama-llamacpp-live.py`; output line does not print the tool blob sha. **Partial** (F11) |
| "schema kama-completion-live/v2" | 158 (`out['schema']`); tool SCHEMA tool:67 | Enforced. Relabelled-v1 control `schema` 616-617 |
| "one hold-mode live request-plane lifecycle" | witness_run 374-415 (one Popen 381-387; hold.json poll 391-400; release 404); hold_released 258-259 | Enforced |
| "on the pinned llama.cpp fixture" | model_digest 252-254 (re-hash of receipt path); server_digest 255-257 (re-hash of receipt path); pins 43-44 vs tool:72-74 | Model: enforced and controlled ("digest" family). Server: enforced, **no control** (CM1). Process identity: **not enforced** (F1, TM2) |
| "receipt re-derives from captured bytes" | grade 138-274; cap() body sha 146-156 | Enforced for captures. Hold and teardown facts (259-262) and the listener bit are receipt self-reports (F7) |
| "every graded check recomputed true" | out dict 158-263; fails 281 | Enforced for keys in `out`. Stored `listener_owned` handled at 286-287 |
| "agreeing with the recorded verdict" | inconsistent 265-267; verdict 283-284 | **Partial**: a stored `passed` of None or absent is never compared; `evaluated` never read (F6) |
| "response headers" | 182-183 (completion Content-Type only); tool:370-372 | Enforced for the completion response only (F10) |
| "body completeness" | 184-189 (body_truncated False; body_bytes == len(body.encode()); Content-Length equal when sent) | Enforced; stricter than tool:374-380 |
| "choice shape" | 190-193 (one choice, index int 0, text non-empty, logprobs None) | Enforced; non-empty text is stricter than the doc's own "not a general invariant" caveat (completion-request-plane.md table row) |
| "id/created" | 200-202 | Enforced |
| "strict timings" | 212-218 (predicted_n == completion_tokens; cache_n, prompt_n int >= 0; predicted_ms finite >= 0) | Type-strict only. **No plausibility bound** (F3) |
| "the request bytes ... bound" | 226-234 (sha of request_body == request_sha256; json prompt == PROMPT 48) | **Partial**: prompt only; temperature, seed, n_predict unbound (F5) |
| "the server's own /tokenize prompt count ... bound" | 219-225 (status 200; len(tokens) == usage.prompt_tokens) | **Count only**: captures['tokenize']['request_body'] is never read (F2) |
| "outside request: usage.prompt_tokens equals the held child's /tokenize count for that nonce prompt" | observe 322-362 (nonce prompt 327-328; tokenize 339-340); live_ptok 310-312; live_nonce 309 | Enforced; live_nonce has **no control** (CM2) |
| "fingerprint equals the receipt's captured one" | live_fp_capture 302-303; cfp from capture 290-291 | Enforced and controlled (witness family) |
| "listener is the receipt's child" | live_pid 304-305; live_port 306-307; live_owned 308; stored listener 286-287; listener call 358 via tip `port_owned_by` (llm:641-660); pid/port from tool-written hold.json (tool:480-488, read at 393-399) | Enforced only relative to tool-declared pid and port and tip-code ownership (F1) |
| "all 44 targeted controls rejected by the check each names" | build_controls 513-629 (42 entries) + fake controls 695-715 (2); is_hit 489-495; count gate 720 | Enforced; per-family counts in output |
| "collateral cap of 5 (30 for the envelope break)" | MAX_COLLATERAL 50; ENVELOPE_CAP 51 used only at 530 (envelope tamper) | Enforced |
| "evaluator refuses all 3 planted wrong-reason controls, errors=0" | eval_selftest 498-510; EXPECT 52; gate 721; errors list 640-679 | Enforced. Control escapes fail `met` (not `errors`); both visible |
| "exit 0 iff met" | 731 | Enforced |

Stricter-than-sentence paths (no violation; listed so the seat report is complete): live_status, live_ctype,
live_object, live_model, live_text, live_created, live_fp_shape, live_port, live_server_sha, live_model_sha
(292-317); completion_envelope, completion_model_id, completion_finish_reason, completion_fingerprint,
models_alias_id, props_alias, health_ready, bad_request_graded (158-263); body_bytes equality (188).

## 3. Findings (fidelity gaps)

**F1 (high) — the serving process is never proven to be the pinned binary.** The sentence says the lifecycle runs
"on the pinned llama.cpp fixture" and the listener "is the receipt's child". The counter binds the child only to
values the tool wrote: child_pid (tool:290) and pid/port in hold.json (tool:480-488, read at counter 393-399), and the
ownership bit comes from the tip's `port_owned_by` (llm:641; counter 358). `server_sha256` in the outside witness is
echoed from the tool's hold.json (counter 360, 313-316). Nothing in the counter reads `/proc/<pid>/exe`. The tip already
contains `server_exe(pid)` (llm:731-…), which opens `/proc/<pid>/exe` and returns the running image's sha256; the
docstring at llm:327-333 says the outside observer is meant to read it. C1 uses neither. Evidence: **TM2 SURVIVED**
(§5): a Python stand-in spawned as the child, receipt `argv[0]` still the pinned `/opt/llama-b11755/llama-server`,
`child_pid` 3024162, `captures.tokenize.body` = `{"tokens":[1,2,3,4,5]}`, verdict REQUEST_OK, counter met=True.
Smallest correction (not applied): in observe() call `live_mod.server_exe(pid)` and add `live_exe` (`opened` true and
`sha256 == SERVER_SHA`); add a control that substitutes a non-llama witness and expects `live_exe`.

**F2 (medium) — the /tokenize count is bound to a string the counter never reads.** Counter 219-225 checks status and
the token count against usage.prompt_tokens. The tool tokenizes `args.prompt` (tool:425-427), but nothing in grade()
reads `captures['tokenize']['request_body']`. Evidence: **TM1 SURVIVED** (tool tokenizes "The dog sat on the";
both prompts tokenize to 8 on the fixture; counter met=True). Probe `tokenize_request_content_dog` met=True.
Smallest correction: `json.loads(cap('tokenize')['request_body'])['content'] == PROMPT`, plus a control.

**F3 (medium) — "strict timings" is type-strict, not plausibility-strict.** Counter 212-218 and tool:419-424 check
types, signs and predicted_n equality only. Probes on the genuine receipt, all met=True:
`timing_predicted_ms_0` (predicted_ms 0.0 for 8 predicted tokens) and `timing_prompt_n_100000` (prompt_n 100000 with
cache_n 0 and prompt_tokens 8). The genuine receipt satisfies prompt_n + cache_n == usage.prompt_tokens (8 + 0 = 8),
so that invariant is available and unused. The knowledge doc completion-request-plane.md lists the round-62 gap as
"timing plausibility" (its opening paragraph) and then says under "Not asserted": "timing values". The sentence and the
doc promise "strict timings"; the code grades shape. Fidelity gap, not a crash.

**F4 (medium) — a named clause with no control, enforcing line survives (CM1).** Server re-hash (255-257). The
model re-hash has its own "digest" control (decoy model path, 614-615); the server path has none. The `tamper` control
that zeroes both sha fields (546-548) fails `server_digest` through the claimed-sha compare, so it would not notice
the re-hash being dropped. Evidence: **CM1 SURVIVED**.

**F5 (low-medium) — request bytes bound to the prompt only.** Counter 231-234. Probe
`completion_request_temp_0.9_seed_99` (temperature 0.9 and seed 99 written into both completion request bodies with
request_sha256 recomputed) met=True. The determinism check (235-244) then compares texts only.

**F6 (low) — recorded-verdict agreement has holes.** inconsistent (265-267) skips any stored check whose `passed` is
None or absent, and never reads `evaluated`. Probes `stored_passed_None` (completion_fingerprint passed=None) and
`stored_evaluated_false_passed_True` both met=True. The tool writes `passed: None` only for the temperature!=0
determinism skip (tool:457-459), so the gap is latent for the shipped tool, but the sentence says "agreeing with the
recorded verdict".

**F7 (low) — teardown and hold facts are receipt self-reports.** Counter 258-262 read `hold.released`,
`teardown.child_pre_dead`, `returncode` and `port_closed` directly from the receipt (tool:517-560 writes them). The
counter does not re-probe the port after teardown. The sentence does not name teardown, but "every graded check
recomputed" includes it. Static reading only; not run.

**F8 (low, by-design residual) — captured bodies are tool-authored beyond the two outside-bound fields.** Probe
`forged_text_both_captures_reseal` (both completion texts rewritten, body sha and content-length resealed) met=True.
The outside answer is compared on fingerprint (302-303) and prompt_tokens (310-312) only. This is what the sentence
asks for; "re-derived from captured bytes" means self-consistent, not independently observed. Recorded so the L1 does
not read "re-derived" as stronger than it is.

**F9 (low) — common-mode logic.** The counter's grade() (153-274) re-implements the tool's checks (tool:145-180,
357-444): `_ctype_json`, `_timings_ok`, `FP_RE`, the envelope test. A mistake shared by both is invisible to the
counter. Pins are typed twice (tool:72-74, counter:43-44; equal today).

**F10 (low) — header scope.** Only the completion response's Content-Type is graded (182-183; tool:370-372). The
sentence says "response headers" without qualification; health, models, props and bad_request headers are not.

**F11 (low) — "byte-pinned" means commit-pinned.** The counter reads whatever tool blob is at `--tip` (642-667);
no digest of the tool or of `kama-llamacpp-live.py` is compared with a frozen value. Output (725-728) does not print
the blob sha, so a reader of the one-line output cannot tie the result to bytes.

**F12 (low, operability) — the counter can exit without its one line.** grade() indexes `stored[k].get` (266) with no
guard, and main() (632-731) has no exception handling. A receipt whose check value is a string raises
AttributeError (probe on the genuine receipt: `stored_check_not_dict`). In the control loop this aborts the run
with no `controls_targeted=` line. Not reachable from the shipped tool; a robustness gap.

### Control coverage holes (clauses with no targeted control in the 44)
server_digest (255-257); live_nonce (309); live_port (306-307); live_server_sha (313-315) and live_model_sha (316);
completion_usage (203-211: the `ptok` family is named completion_prompt_tokens, not completion_usage);
completion_finish_reason (194-195); completion_fingerprint shape (197-199); models_alias_id (166-167); props_alias
(170-171); bad_request_graded (245-249); completion_timings predicted_n equality (controls cover predicted_ms and
cache_n only); the tokenize request content (no check at all, F2).

## 4. Probe results (receipt-level, genuine tip receipt, live witness; driver and output in out/KR01C1Fidelity/probe/)

| Probe | met | fails | Reading |
|---|---|---|---|
| base | True | [] | genuine receipt accepted |
| timing_predicted_ms_0 | True | [] | F3 |
| timing_prompt_n_100000 | True | [] | F3 |
| tokenize_request_content_dog | True | [] | F2 |
| completion_request_temp_0.9_seed_99 | True | [] | F5 |
| stored_passed_None | True | [] | F6 |
| stored_evaluated_false_passed_True | True | [] | F6 |
| forged_text_both_captures_reseal | True | [] | F8 (by design) |
| server_path_decoy_claimed_pinned_sha | False | inconsistent:server_digest, server_digest | rejected, as intended |
| health_stored_false_recomputed_true | False | inconsistent:health_ready | rejected, as intended |

## 5. Mutants (committed in scratch clones; counter run from clone path, `--tip` = clone commit)

Baseline (B0, lane tip, unmutated): 
`tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` (exit 0)

| Id | Mutation (commit) | Verdict | Counter output (verbatim, exit 0 for all) |
|---|---|---|---|
| CM1 | counter:257 `and sha256_path(srv.get('path')) == SERVER_SHA` replaced by `and True` (fd5830c4) | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| CM2 | counter:309 `'live_nonce': bool(NONCE) and NONCE in …` replaced by `'live_nonce': True` (0ca193cd) | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| TM1 | tool:427 tokenize content `args.prompt.replace('cat', 'dog')` (35a12f17) | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| TM2 | tool:287 child = `sys.executable -c FAKE_SRC` (Python /health, /v1/models, /props, /tokenize, /v1/completions, 400 on missing prompt; fingerprint `b11755-704366d76`); receipt `argv` still the pinned binary (bf744d7c) | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |

Receipts: TM2 `child_pid` 3024162, `captures.tokenize.body` `{"tokens":[1,2,3,4,5]}`, `verdict` REQUEST_OK; the
claimed `argv[0]` is `/opt/llama-b11755/llama-server`. Diffs: out/KR01C1Fidelity/mutants/*.diff.
TM2 is not a KILL under the freeze kill rule as written (the outside contact was live), which is the point of F1:
the sentence's "on the pinned fixture" is not what the counter checks.

## 6. Recommendations (advisory; L1 decides; nothing applied)
1. F1: `live_exe` via `live_mod.server_exe(pid)` in observe(); control for a non-llama witness. Re-run TM2 expecting KILL.
2. F4/CM1 and CM2: targeted controls for server re-hash (decoy server path) and for `live_nonce` (witness sent_prompt
   without the nonce). Re-run CM1/CM2 expecting KILL.
3. F2/TM1: bind captures.tokenize.request_body content to PROMPT; control `tokcontent`. Re-run TM1 expecting KILL.
4. F3: add prompt_n + cache_n == usage.prompt_tokens and predicted_ms > 0 when predicted_n >= 1 (both hold on the
   genuine receipt); controls for each. Or reword "strict timings" in the freeze to "typed timings".
5. F5/F6: bind temperature, seed and n_predict in the request bytes; require `passed` to be a bool and `evaluated`
   True for every graded key.
6. F12: guard per-control scoring and grade(); a malformed receipt should count as a rejection, not abort the line.

## 7. Tally
- Sentence identity: freeze == docstring (True); no receipt label carries the predicate.
- Mutants: SURVIVED 4/4 (CM1, CM2, TM1, TM2). Baseline B0 met=True.
- Probes: 7 clause gaps accepted with met=True (F2, F3 x2, F5, F6 x2, F8 by design); 2 sanity rejections as intended.

tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True (B0, lane tip 03a6a1d8); mutants SURVIVED 4/4
