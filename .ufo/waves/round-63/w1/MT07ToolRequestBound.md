# MT07ToolRequestBound — C1 request-bytes binding falsification (round 63)

Seat: MT07ToolRequestBound (leaf, mutation tester). Axis: operability. Milestone: falsify C1 tool grading.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane tree untouched; all mutation in a scratch clone).
Advisory finding only. No verdict on the C1 claim; the L1 decides what the predicate's wording "request bytes ... bound" requires.

## Method

- Read the frozen predicate (controls/freeze.txt), `tools/kama-completion-live.py` (v2), and `tools/round63-c1-counter.py` (grade, score, observe, witness_run, build_controls, main). Relevant facts:
  - Tool `http_post` builds `data = json.dumps(payload)`, sends `data`, and returns `request_body: data`. `_cap` then writes `request_body` and `request_sha256 = sha256(request_body)`. Both come from one in-process object.
  - Counter `completion_request_bound` = `sha256(request_body) == request_sha256 AND json(request_body).prompt == PROMPT`, where `PROMPT` is the counter's constant `'The cat sat on the'`. It never sees the socket.
  - Counter's only outside contact is `observe()`: its own nonce prompt during the hold window. Its only cross-check on prompt content is `completion_prompt_tokens`: `usage.prompt_tokens == len(/tokenize(args.prompt))`. The server log records token counts and timings, not prompt text (checked: `work-M1b/tool-work/server.log`).
- Recipe: `S=/fast/scratch/hyaku/kama-r63/w/MT07ToolRequestBound`, `D=$S/clone` (`git clone --shared`, toplevel asserted before every git mutation), one mutant per commit on top of the tip (`git reset --hard` between mutants, each asserted), counter run unmutated from `$D/tools/` with `--repo $D --tip <mutant commit> --work $S/work-<M>`. Each mutant commit touched exactly one file (`tools/kama-completion-live.py`); `tools/round63-c1-counter.py` is byte-identical to the tip in every mutant.
- Toolchain: `python3` (3.14, system), `llama-server` at `/home/vgpnk/.local/bin/llama-server` (pre-existing, not installed or upgraded by me), pinned fixture `~/.cache/kama-shokunin/models/stories260K.gguf`. Installs or upgrades by this seat: none.

## Baseline (unmutated tool, unmutated counter, tip 03a6a1d8)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Rerun: identical (`out/MT07ToolRequestBound/rerun-base.out.txt`). Baseline is met, so the survivors below are not baseline artifacts.

Tokenizer probe at the tip (`out/MT07ToolRequestBound/tokenize-probe.txt`, via the tool's own hold-mode listener): `"The cat sat on the"` = 8 tokens; `"The dog sat on the"` = 8; `"The bat sat on the"` = 8; `"The cat sat on a"` = 8; `"The cat sat on the mat"` = 10; `"A cat sat on the"` = 9.

## Mutants (all on `tools/kama-completion-live.py`; patches in `out/MT07ToolRequestBound/mutant-*.patch`)

Counter one-liner for each, verbatim from `out/MT07ToolRequestBound/<M>.out.txt` (stderr line where present).

### M1a — record PROMPT, send a different-token-count prompt — KILLED

Mutation: `http_post` sends `{**payload, 'prompt': 'The cat sat on the mat'}` for `/v1/completions` with a `prompt` key; `request_body` still records the original bytes (commit 01b22382).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_prompt_tokens", "verdict"]
```
Kill reason: the server's `usage.prompt_tokens` = 10 against `/tokenize("The cat sat on the")` = 8. `request_bound` did not fire (it reads the recorded text, which is still PROMPT).

### M1b — record PROMPT, send a same-token-count prompt — SURVIVED

Mutation: identical to M1a but the sent prompt is `'The dog sat on the'` (8 tokens, equal to PROMPT). Recorded `request_body` still `"The cat sat on the"` (commit b6db758e).
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Rerun: identical (`rerun-M1b.out.txt`).

Proof the defect is present (not inferred from the counter):
- The M1b receipt records `request_body = {"prompt": "The cat sat on the", ...}`, its sha verifies, `prompt_tokens = 8 = len(tokenize)`, and `completion_request_bound` passes. Every recorded field is consistent with PROMPT.
- The M1b completion text is `" swings. He liked"`. The baseline completion for PROMPT is `" ground. She liked"`.
- The **unmutated** tip tool run with `--prompt "The dog sat on the"` returns `" swings. He liked"` (`tip-probe-dog.json`), byte-for-byte the M1b text. The same unmutated tool run with `--prompt "The cat sat on the"` returns `" ground. She liked"` (`tip-probe-cat.json`), matching baseline. So the M1b server processed `The dog sat on the` while the receipt says `The cat sat on the`, and the counter accepted it.

Why it survives: no check reads the bytes that went to the socket. `completion_request_bound` checks the record against itself plus the constant. `completion_prompt_tokens` is a token count, and `dog`/`cat` tokenise to the same length. `completion_deterministic` compares two requests that both carry the dog prompt. The witness uses its own nonce prompt. The 44 controls include `reqbind` only for "prompt replaced in the recording" and "sha replaced"; none covers "recording differs from wire with an equal token count".

### M2 — record request_body with altered key order — SURVIVED

Mutation: `_cap` records `json.dumps(dict(reversed(payload.items())))`, i.e. `{"timings_per_token": false, "seed": 7, ..., "prompt": "The cat sat on the"}`, and hashes that reordered copy. The bytes sent are unchanged (commit 100c1978).
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Rerun: identical (`rerun-M2.out.txt`). The recorded body is a different byte string from what was sent (key order differs), and the counter cannot tell. `completion_request_bound` only parses JSON and reads `prompt`, and the sha verifies the reordered copy. No control family touches key order or byte-level equality with the wire.

### M3 — omit request_sha256 — KILLED

Mutation: `_cap` records `request_body` but no `request_sha256` (commit 75b3add7).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_request_bound", "verdict"]
```
Killed by `completion_request_bound` (the tool's own check also fails: `passed: False`).

### M4 — record an altered prompt with a consistent sha, send PROMPT — KILLED

Mutation: `_cap` replaces `b'The cat sat on the'` with `b'Other text'` in `request_body` and re-hashes it. The wire carries the real PROMPT (commit 145ee189).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_request_bound", "verdict"]
```
Killed, but the kill is on the recorded text, not the wire: the wire here was correct. `request_bound` is a check on the record's text against a constant, so it cannot distinguish "record wrong, wire right" from "record right, wire wrong".

### M5 — sha computed over bytes other than the recorded body — KILLED (sanity)

Mutation: `request_sha256 = sha256(request_body + b' ')` (commit 434ebe97).
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_request_bound", "verdict"]
```
Confirms the sha comparison is live.

Tally: 6 mutants, 4 KILLED (M1a, M3, M4, M5), 2 SURVIVED (M1b, M2). Both survivors are defects of the C1 control set, not of the baseline.

## What the request_body / request_sha256 pair proves

When the same process writes both, the pair attests only that the record was not edited after capture, and only against an editor who does not re-seal. That is the property the 2 `reqbind` controls test (prompt replaced and re-sealed; sha zeroed). It does not attest:
1. **What went on the wire.** M1b proves the sent prompt can differ from the recorded one under an unchanged record and an unchanged hash. The honest tool sends `data` and records `data`, but nothing outside the tool observes the socket. The only wire-facing check is a token count (`completion_prompt_tokens`), and the llama.cpp server exposes no prompt text in its log or response (checked).
2. **Byte identity of the record.** M2 shows a re-serialised, key-reordered body passes with a self-consistent sha. The counter compares JSON semantics (`prompt`) rather than bytes against any independent source.
3. **The prompt the counter cares about.** `completion_request_bound` compares the recorded prompt with the counter's constant PROMPT (M4 is killed this way with a correct wire). It grades the record's text, not the send.
4. **Anything about the receipt's `request` block.** `receipt['request']['prompt']` is recorded but not graded. M1b's receipt says `"The cat sat on the"` while the server answered for `dog`.

The counter's outside contact (`observe`) sends its own nonce prompt during the hold window. It never observes the tool's requests, so no outside evidence about the tool's request bytes exists anywhere in C1 except the token count.

Mapping to the frozen predicate (no verdict): the predicate says "the request bytes ... all bound". In the counter's sense this holds as record-to-hash integrity and record-to-constant prompt equality. As wire-to-record binding it does not hold: M1b and M2 survive with `met=True`. Whether "bound" means wire-bound is for the L1 to settle.

## Routed defects (advisory; not implemented, not measured)

- A counter-side outside check for the prompt content: during the hold window the counter sends `PROMPT` with the same `seed=7`, `n_predict=8`, `temperature=0.0` to the listener and compares its text with the tool's `completion.choices[0].text`. The premise is supported by my data: the unmutated tool reproduces identical text across runs (baseline vs rerun; tip cat probe matches baseline). This should kill M1b (expected `" ground. She liked"` vs the tool's `" swings. He liked"`). [INFERENCE — I did not implement or run this.]
- A canonical byte check on the recorded body: the counter could require `request_body == json.dumps(expected_dict)` with the tool's own separators and key order. That should kill M2. [INFERENCE — not run.]
- Add control families for "recorded body differs from wire at equal token count" and "key order changed in the record", each credited only with the named-check rule, so the 44-control set covers M1b and M2.

I did not edit the counter or the lane source. No mutant was committed to the lane. The counter and tool at the tip are unchanged.

## Evidence (`.ufo/waves/round-63/w1/out/MT07ToolRequestBound/`)

- `base.out.txt`, `base.err.txt`, `rerun-base.out.txt`: baseline.
- `M1a.out.txt`/`.err.txt`, `M1b.out.txt`, `M2.out.txt`, `M3.out.txt`, `M4.out.txt`, `M5.out.txt` (+ `.err.txt`): counter outputs; `rerun-M1b.out.txt`, `rerun-M2.out.txt`: reruns.
- `receipt-*.json`: the receipt each counter run graded (`receipt-M1b.json` holds the `dog`-sent, `cat`-recorded pair).
- `mutant-M1a.patch` ... `mutant-M5.patch`: the exact tool diffs against the tip.
- `tokenize-probe.txt`, `tip-probe-receipt.json`: tokenizer counts and clean tip probe receipt (REQUEST_OK).
- `tip-probe-dog.json`, `tip-probe-cat.json`: unmutated tool with `--prompt` set to dog/cat, showing the M1b text is what the dog prompt produces.

Scratch `/fast/scratch/hyaku/kama-r63/w/MT07ToolRequestBound/` removed after the evidence copy.

Counter one-liner (baseline, tip 03a6a1d8): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True`
