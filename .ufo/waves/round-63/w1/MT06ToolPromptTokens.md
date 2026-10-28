# MT06ToolPromptTokens — falsify the C1 /tokenize binding (round 63, kama)

Seat: mutation-tester, leaf (no dispatch). Judged on: operability. Milestone: falsify C1 tool grading.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (amendment-1 tip). Advisory finding only; no verdict on the claim, no commit to the lane, no edit outside this report and out dir.
Tools used: git (read-only on lane; mutating only inside my scratch clone), python3 (counter, probe). No installs or upgrades; no pacman.

## Setup
- Scratch: `/fast/scratch/hyaku/kama-r63/w/MT06ToolPromptTokens/` (clone `clone/` via `git clone -q --shared`, toplevel asserted before each mutation). Scratch removed before yield.
- Unmutated counter run from `clone/tools/` with `--repo <clone> --tip <rev> --work <scratch>`.
- Live fixture: pinned stories260K model + pinned llama-server, launched by the counter itself on an unregistered loopback port. Foreign llama-servers on 1234/45669 not touched.

## Baseline (unmutated tool, unmutated counter, tip 03a6a1d8)
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0. Genuine receipt: `completion.usage.prompt_tokens=8`, `tokenize.body={"tokens":[1,291,280,294,262,294,353,265]}` (8 ids, real BOS id 1 first).

## Mutants (all in the tool file `tools/kama-completion-live.py`, committed in the clone, scored by the unmutated counter)

| id | mutation | clone commit | verdict |
|----|----------|--------------|---------|
| A | skip `/tokenize`; fabricate tokenize capture `{"tokens":[1]*usage.prompt_tokens}` | 986aac72528ee325222cb57018f144e106cb3a0c | **SURVIVED** |
| B | `/tokenize` called with `add_special: false` | 27b12506ee55c7a6a8acbdb4592654ae000811ee | KILLED |
| C | receipt's completion body `usage.prompt_tokens` +1 (and total +1, body re-sealed, content-length updated) with a matching fabricated tokenize capture of n+1 ids | da5986b1a7054ce5dcde275ee9a8e28609e20da1 | **SURVIVED** |
| C0 (control) | completion usage +1 (re-sealed), genuine `/tokenize` kept | e93cd063afc2a94faed2312a1f8e91619053ab56 | KILLED |

Counter one-liners, verbatim (stdout; exit code in brackets):

A [exit 0]:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
B [exit 1]:
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_prompt_tokens", "verdict"]
```
C [exit 0]:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
C0 [exit 1]:
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
error: live: ["completion_prompt_tokens", "verdict"]
```

Mutant patches and receipts: `.ufo/waves/round-63/w1/out/MT06ToolPromptTokens/` (`mutant-{A,B,C,C0}.patch`, `{base,A,B,C,C0}/receipt.json`, `probe.py`).

### Why A and C survive (receipt-level evidence)
- A: receipt `captures.tokenize.body` = `{"tokens": [1, 1, 1, 1, 1, 1, 1, 1]}` (8 ids, status 200), receipt `usage.prompt_tokens=8`. The grader's `completion_prompt_tokens` (counter lines 219-225) recomputes `len(tokens) == usage.prompt_tokens` from the receipt's own two captures, so a length-only fabrication passes. The stored check and recomputed check agree, so `inconsistent` is empty.
- C: receipt `usage.prompt_tokens=9`, tokenize length 9 — the genuine server count for the request prompt `The cat sat on the` is 8 (genuine base receipt). The receipt is therefore wrong about the server by one token and the counter still returns met=True.

### Diagnostic: the live witness does not see the receipt (probe.py, read-only use of counter functions)
Probe re-ran the mutant tool in hold mode and re-scored its receipt against a fresh outside witness (`score()`):
```
C  (mutant):  receipt usage.prompt_tokens= 9 receipt tokenize len= 9
               witness usage_prompt_tokens= 19 witness tokenize_count= 19
               score met= True fails= []
base (genuine): receipt usage.prompt_tokens= 8 receipt tokenize len= 8
               witness usage_prompt_tokens= 18 witness tokenize_count= 18
               score met= True fails= []
```
The witness numbers are for the counter's nonce prompt, so they are not comparable to the receipt's PROMPT count; the point is that `score()` never reads `captures.tokenize` or `captures.completion.usage` against any outside value. The witness is internally consistent (`live_ptok`: outside usage == outside tokenize of the nonce prompt), and the only receipt-to-witness binding is `live_fp_capture` (fingerprint string). Nothing binds the receipt's prompt count to the server.


## Answer to the judged question
Is a fabricated-but-consistent tokenize capture caught by anything other than the live witness?
- **No, nothing catches it — including the live witness.** The live witness (`observe()` + `live_ptok`) makes its own nonce-prompt `/tokenize` call and its own nonce-prompt completion; it never reads the receipt's tokenize capture or the receipt's completion `usage`. So the fabrication is invisible to the witness as well as to the grader.
- The only in-counter check on that pair is `completion_prompt_tokens`, which compares the receipt against itself. It is a receipt-internal consistency check, not a server binding. Fabrication that keeps the two captures equal passes.
- The failure is structural, not a single-seed luck: the 44-control set cannot catch it either. The `ptok` family has exactly two controls, both one-sided: (i) `usage.prompt_tokens += 1` alone (expect `completion_prompt_tokens`), (ii) `tokenize.tokens.append(7)` alone (expect `completion_prompt_tokens`). Neither is a consistent pair, so a consistent pair is never exercised. The C1 predicate sentence ("the server's own /tokenize prompt count all bound") is therefore not what the grader enforces: the count is bound receipt-to-receipt only.
- Also observed: the binding is by length only. A's fabricated ids are all `1`, while the genuine ids are `[1,291,280,294,262,294,353,265]`. A counter-side tokenize of the receipt's PROMPT with a token-id comparison would catch A, and a counter-side `/v1/completions` for PROMPT during the hold would catch C (receipt 9 vs server 8). Neither is in the counter.
- B is caught, but only indirectly: `add_special=false` returns 7 ids vs usage 8 (genuine BOS offset). The counter never checks the `add_special` field of the request body; it catches B because the count disagrees. [INFERENCE, not run] An A+B variant (fabricated 8-id capture plus add_special=false) would survive for the same reason as A.

## Recommended remediation (advisory, for L1 to judge)
1. In `round63-c1-counter.py`, bind the receipt's tokenize and completion usage to the counter's own contact with the held child for the receipt's `request.prompt` (PROMPT), not only the nonce prompt: compare `captures.tokenize.body` token ids (not just length) and `captures.completion.usage.prompt_tokens` to the outside values.
2. Add consistent-pair controls to the `ptok` family (usage +1 AND fabricated tokenize of n+1; tokenize replaced by `[1]*n` with genuine usage), each credited only if the new cross-check name is in the failure set and the collateral cap holds.
3. Re-run `c1-base` and the mutant set after the change; A, B, C, C0 should then read KILLED.

I did not modify the counter or the tool; I only report what the unmutated counter does.

## Counts
- Mutants A, B, C, C0 (+ baseline): 4 mutants; SURVIVED 2 (A, C), KILLED 2 (B, C0). Baseline met=True.
- Counter one-liner at tip (unmutated, baseline): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True`.
