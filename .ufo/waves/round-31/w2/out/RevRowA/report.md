```RESULTS
$ /usr/bin/git -c core.hooksPath=/dev/null clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowA/lane
exit: 0
verbatim tail:
Cloning into '/tmp/kama-r31w2/RevRowA/lane'...
done.

$ /usr/bin/git -c core.hooksPath=/dev/null -C /tmp/kama-r31w2/RevRowA/lane checkout -q --detach 382d11b2107d335705875da1a4d889b074bd6fa6
exit: 0
verbatim tail (0 bytes):

$ /usr/bin/sha256sum .ufo/waves/round-31/count-c1.py
cwd: /tmp/kama-r31w2/RevRowA/lane
exit: 0
verbatim tail:
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py

$ /usr/bin/git -C /tmp/kama-r31w2/RevRowA/lane rev-parse HEAD
exit: 0
verbatim tail:
382d11b2107d335705875da1a4d889b074bd6fa6

$ /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane /tmp/kama-r31w2/RevRowA/lane --repo /tmp/kama-r31w2/RevRowA/lane --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowA/c1.json
cwd: /tmp/kama-r31w2/RevRowA/lane
exit: 0
verbatim tail:
registered 18 counted 17 target 12 met True not-counted ['K31-10']

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowA/derive_rows.py /tmp/kama-r31w2/RevRowA/lane /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowA
cwd: /tmp/kama-r31w2/RevRowA/lane
exit: 0
verbatim tail:
K31-01 | committed-cell==rendered yes | live-status 200 | live={"slot_task": 3, "status": 200}
manual-rendered '200, max_tokens = 3, n_predict = 3'; utf8-bytes=34
K31-02 | committed-cell==rendered yes | live-status 200 | live={"slot_task": 8, "status": 200}
manual-rendered '200, max_tokens = 3, n_predict = 3'; utf8-bytes=34
K31-03 | committed-cell==rendered yes | live-status 200 | live={"slot_task": 13, "status": 200}
manual-rendered '200, n_probs = 20'; utf8-bytes=17

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowA/row_probe.py /tmp/kama-r31w2/RevRowA/lane /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowA
cwd: /tmp/kama-r31w2/RevRowA/lane
exit: 0
verbatim tail:
{"id":"BASE","status":200,"slot_task":0,"stored":{"max_tokens":1,"n_predict":1,"n_probs":0},"completion_tokens":1}
{"id":"K31-01","status":200,"slot_task":3,"stored":{"max_tokens":3,"n_predict":3,"n_probs":0},"completion_tokens":3}
{"id":"K31-02","status":200,"slot_task":8,"stored":{"max_tokens":3,"n_predict":3,"n_probs":0},"completion_tokens":3}
{"id":"K31-03","status":200,"slot_task":13,"stored":{"max_tokens":1,"n_predict":1,"n_probs":20},"completion_tokens":1}
{"id":"K31-02-native-override","status":200,"slot_task":16,"stored":{"max_tokens":5,"n_predict":5,"n_probs":0},"completion_tokens":5}

Owned server child launched by row_probe.py:
$ /home/vgpnk/.local/opt/llama-b11755/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47900
pid: 508732
exit: 0 (after this probe sent SIGTERM to its own child)
verbatim tail (last line; full log retained):
0.00.161.139 I srv    operator(): operator(): cleaning up before exit...
```

FINDING: All three committed outcome cells match the handwritten rendering and reproduce as stored settings; K31-02's precedence sentence needs an explicit request-scope qualifier because native `n_predict` overrides it.

LIMITS: One frozen full run and one independent five-request probe on the pinned b11755/stories260K fixture. These establish the sampled settings, not universal precedence, sampler implementation, other builds/models/argv, or C1 improvement/admission. The native-alias counterexample adds a field absent from the registered request: it does not falsify the committed K31-02 sample, and the section's existing one-observation limits already support a narrow reading. The defect is the sentence's unqualified reading as client advice. No other rows, C2, C3, repeated-run stability, or broader parameter combinations were independently reviewed. No tool installs/updates. No tracked lane file was edited; checkout occurred only in the fresh scratch clone. The conflicting trailer path `w2/out/RevRowA.md` is outside this seat's permitted directory and was not written; this report uses the explicitly assigned `w2/out/RevRowA/report.md`.

## Axes and row findings

Axes: **depth** (correct parameter semantics), **calibration** (stored observation versus general behavior), and **operability** (safe, reproducible endpoint evidence). These are impact areas, not axis judgments.

```text
K31-01 | committed-cell==rendered yes | live-status 200 | overclaim none
K31-02 | committed-cell==rendered yes | live-status 200 | overclaim unqualified two-key precedence when native n_predict is also present; measured two-key sample is correct
K31-03 | committed-cell==rendered yes | live-status 200 | overclaim none
```

## Independent derivation and live evidence

Read the cloned registry rows and cloned SKILL.md lines 1247–1249 at `382d11b2107d335705875da1a4d889b074bd6fa6`, not a later working-tree state. All three registry outcomes have `kind: slot`.

The actual frozen docstring's **RENDER rules are lines 50–54**, not the assignment's stale lines 40–46. For a slot, prepend `200, `, sort the `outcome.set` keys, render each integer with JSON notation, and join with `, `:

| id | registry set | hand-rendered outcome | UTF-8 bytes |
|---|---|---|---|
| K31-01 | `{"max_tokens":3,"n_predict":3}` | `200, max_tokens = 3, n_predict = 3` | 34 |
| K31-02 | `{"max_tokens":3,"n_predict":3}` | `200, max_tokens = 3, n_predict = 3` | 34 |
| K31-03 | `{"n_probs":20}` | `200, n_probs = 20` | 17 |

`derive_rows.py` compares these handwritten string constants with the committed cell's UTF-8 bytes; it does not import or call the counter renderer. Markdown delimiter-padding spaces are excluded, as in the counter's table parser. `manual-row-comparison.json` preserves each full registry row, committed table line, meaning, both hexadecimal byte strings, equality, and the extracted frozen receipt `live` block.

Frozen receipt blocks, verbatim:

```json
{"id":"K31-01","live":{"status":200,"slot_task":3}}
{"id":"K31-02","live":{"status":200,"slot_task":8}}
{"id":"K31-03","live":{"status":200,"slot_task":13}}
```

Those blocks alone do **not** retain the checked slot values; `counted: true` is not independent proof. Therefore `row_probe.py` separately sends the registry base and the three exact row bodies, retaining the raw response and entire `/slots` body after each request in `row-probe.json`:

- **K31-01:** base `max_tokens:1` becomes `max_tokens:3`; raw newest slot stores `max_tokens:3,n_predict:3`. The response reports three completion tokens and `finish_reason:"length"`. The meaning expressly refuses to infer sampler use from a stored alias; within the stated request/profile, no overclaim is identified. Pinned `server-schema.cpp` lines 44–48 declare `n_predict` and its two aliases, including cited S190 at line 47.
- **K31-02:** the actual body contains **both** `max_tokens:1` and `max_completion_tokens:3`; raw newest slot stores both output-limit keys as 3. This is genuine evidence of precedence for this unequal pair, not a no-op equal-value observation. However, S189's quoted generic copier line (`server-common.cpp:1530`) alone is not a proof of universal precedence.
- **K31-03:** the body has `logprobs:true`, no `top_logprobs`, and base `max_tokens:1`; raw newest slot stores `n_probs:20`, versus 0 for the base. Pinned `server-common.cpp:1515–1519` explicitly supplies the default 20. The meaning concerns this stored mapping, not a claim that the sampler used all twenty candidates. No overclaim is identified within the stated profile.

## Counterexample and smallest safe correction

Hypothesis tested: the phrase “With both keys present, max_completion_tokens determines stored max_tokens and n_predict” is false without excluding the native `n_predict` override.

Exact additional request:

```json
{"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"max_completion_tokens":3,"n_predict":5}
```

Observed: **HTTP 200**, newest task **16**, stored `max_tokens:5,n_predict:5`, response `usage.completion_tokens:5`, `finish_reason:"length"`. Both OAI limit keys remain present, but neither controls the stored limit in this case. This also shows why K31-01's output-limit advice must retain its surrounding sampled-profile and stored-only caveats. The endpoint deliberately accepts native parameters: pinned `server-common.cpp:1524–1530` says it copies llama.cpp-specific parameters and explicitly permits the `n_predict` override.

Smallest safe correction, advisory only: replace K31-02's meaning with:

> In this probe, max_tokens=1 and max_completion_tokens=3, with n_predict absent, stored max_tokens and n_predict were both 3; inspect stored settings when limits conflict.

This is a fixable prose-scope defect, not an unavoidable axis tradeoff, and it requires no change to the frozen counter or outcome cell. No correction was applied and no admission/judgment was invoked. Confirming these three observations cannot cure the separately recorded no-op-registry weakness in C1's frozen predicate.

## Retained evidence

All paths below are relative to this report's directory:

- `commands.json`: every top-level command, exit, duration, and verbatim output tail; raw command logs `01-clone.log`, `02-checkout.log`, `03-counter-pin.log`, `04-clone-head.log`, `05-live-counter.log`, `07-independent-row-probe.log`, `08-hand-render-compare.log`.
- `c1.json`: complete, unmodified frozen full-run receipt; first run exited 0, so no retry occurred.
- `manual-row-comparison.json` and `derive_rows.py`: handwritten-render byte comparison and complete selected registry/table/live inputs.
- `row-probe.json`, `row-probe-server.log`, `row_probe.py`: independent raw requests/responses/full slots, owned server argv/PID/exit, and exact probe source. The probe verified binary/library/model digests against the registry and checked `/props` model identity. Only its own child was signaled; port 47900 was used, never 8080 or 34113.

Read tools and artifact writes were not shell commands and have no process exit status. Internal git queries and the ephemeral server started by the unmodified frozen counter are implementation details of the recorded counter invocation; that counter deletes its own server log. No output from an unrun command is represented here.
