# MT05ToolTimings — falsify the strict timings check (C1, operability)

Seat: MT05ToolTimings (mutation-tester, leaf). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`
(lane HEAD; ancestor-check passed). Counter: `tools/round63-c1-counter.py` (unmutated at tip unless a row says CM).
Scratch: `/fast/scratch/hyaku/kama-r63/w/MT05ToolTimings` (removed before yield; receipts copied to `out/MT05ToolTimings/`).
Nothing was committed to the lane; all commits are in my clone `$S/clone` (`git clone --shared`, detached at the tip).

## Baseline (unmutated tip, run from `$S/base/tools`)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0. The baseline is met, so every mutant below is judged against a met control.

## Method

Each requested mutant edits the tool (`tools/kama-completion-live.py`) in the clone. Right after the `/v1/completions`
capture, the commit rewrites `timings.<key>` in the captured body, then reseals `body`, `body_bytes`, `body_sha256` and
`headers.content-length`. Resealing means the mutation reaches the timings predicate and not the capture-hash check.
Each mutant is one commit on top of the tip, and the unmutated counter runs from `$S/clone/tools/` with
`--repo $S/clone --tip <commit>`. I confirmed in every receipt that the mutated value reached the captured body
(e.g. `"predicted_ms":NaN`, `"cache_n"` absent, `"prompt_n":-1`, `"predicted_n":true`) and that
`completion_untruncated`, `completion_headers` and `completion_usage` did not fail, so the reseal worked and
collateral is zero.

Two mutant families were run:

- **V (honest tool).** The tool's own `_timings_ok` is left as-is, so the tool grades the mutated body honestly and
  writes `verdict: FAIL`. The counter's kill can come from either the tool's grade or the counter's own recompute.
- **L (lying tool).** Same body mutation, plus the tool's `completion_timings` check forced to `True`. This is the
  decisive series: the only thing that can reject it is the counter's own predicate, which recomputes False against
  the stored True and records `inconsistent:completion_timings`.

## Requested variants (8)

| id | mutation (predicted_ms unless noted) | commit | counter one-liner (verbatim, stdout) | stderr (verbatim) | verdict |
|---|---|---|---|---|---|
| V1 | `-1` | 5069639d | `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V2 | `true` (bool) | a9dc2221 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V3 | `Infinity` | be08f9a5 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V4 | `NaN` | df30d9c3 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V5 | `"3"` (string) | 71b522e3 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V6 | `cache_n` key removed | e3e46b93 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V7 | `prompt_n = -1` | f564dc6a | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |
| V8 | `predicted_n = true` (bool) | c043ab82 | same stdout as V1 | `error: live: ["completion_timings", "verdict"]` | KILLED |

KILLED here means `met=False`, with `completion_timings` as the named failure. Note that `verdict` is also in the set
because the honest tool wrote FAIL. That is the tool and counter agreeing, not an independent counter verdict. The
L-series below isolates the counter.

## Lying-tool variants (isolates the counter's own predicate)

| id | mutation | commit | counter one-liner (verbatim, stdout) | stderr (verbatim) | verdict |
|---|---|---|---|---|---|
| L1 | predicted_ms `-1` | 58f437c9 | `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` | `error: live: ["completion_timings", "inconsistent:completion_timings"]` | KILLED |
| L2 | predicted_ms `true` | 7e3e0ac8 | same stdout as L1 | same stderr as L1 | KILLED |
| L3 | predicted_ms `Infinity` | e0245e86 | same stdout as L1 | same stderr as L1 | KILLED |
| L4 | predicted_ms `NaN` | af9406ef | same stdout as L1 | same stderr as L1 | KILLED |
| L5 | predicted_ms `"3"` | 5196957c | same stdout as L1 | same stderr as L1 | KILLED |
| L6 | cache_n removed | 329b6b4b | same stdout as L1 | same stderr as L1 | KILLED |
| L7 | prompt_n `-1` | 4d666638 | same stdout as L1 | same stderr as L1 | KILLED |
| L8 | predicted_n `true` | 1ee7b20a | same stdout as L1 | same stderr as L1 | KILLED |

Every L-variant is rejected by the counter's own recompute of `completion_timings` against the lying stored value. The
stored check said True and the recompute said False.

## Extra probes (outside the requested 8)

**X1 — SURVIVED (body strictness).** Honest tool, with `timings.extra_nan = NaN` added to an ungraded key. Commit 862bbb98.

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[... timing=4/4 ...]
```
exit 0, verdict REQUEST_OK, and the receipt body really contains bare `NaN`. The counter accepts a non-RFC 8259 body.
This does not defeat the timing predicate itself, since `is_num` rejects NaN in `predicted_ms`. It does show the counter
does not hold capture bodies to strict JSON. Routed as a finding, not a timings kill.

**CM1 — SURVIVED (control gap).** Counter mutant: `and is_int(t.get('predicted_n'))` dropped at line 214 (commit a682db81), run
on the unmutated tip tool.

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[...timing=4/4...]
```
met=True with the bool guard removed. The honest tip receipt has int `predicted_n`, so this is expected on the tip. The
guard is only load-bearing for a bool-typed `predicted_n` equal to `completion_tokens`, and no control names
`predicted_n`. [INFERENCE] A bool `predicted_n` with `completion_tokens` 1 would be accepted by CM1 if the tool also
lied; I did not build that fixture.

**CM2 — SURVIVED (control gap).** Counter mutant: `and t['prompt_n'] >= 0` dropped (commit ba98d6bc). Tip tool.

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[...timing=4/4...]
```
No control names `prompt_n`. The predicate's `prompt_n >= 0` clause is unexercised by the 44 controls. Note V7/L7
(`prompt_n = -1`) are killed only by the predicate, not by a control.

**CM3 — KILLED (controls work where they exist).** Counter mutant: `is_num(predicted_ms)` reduced to
`isinstance(..., (int, float))`, which admits bool and inf (commit ba092f00).

```
tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[... timing=2/4 ...]
```
stderr: `error: escape timing expect=completion_timings fails=[]` (twice, one for the bool control, one for inf). The
`predicted_ms=true` and `predicted_ms=Infinity` controls escape as expected.

## Python `json.loads` vs a strict parser (NaN / Infinity)

Full probe: `out/MT05ToolTimings/json-parser-probe.txt`. Bodies were the captured completion bodies from V3, V4 and X1.

| parser | `NaN` / `Infinity` literal |
|---|---|
| Python `json.loads` (default, used by counter `jbody`, `grade`, receipt load, and the tool itself) | ACCEPTS, yields `float('nan')` / `float('inf')` |
| Python `json.loads(parse_constant=raise)` | REJECTS |
| Node 24.21 `JSON.parse` (RFC 8259 strict) | REJECTS (`Unexpected token 'N'`) |
| `jq` on this host (it is **jaq 3.1.1**, not jq) | ACCEPTS (exit 0) |

So the counter's timings predicate does not depend on the parser for NaN/Infinity: the value is accepted by the parser
and then killed by `is_num` (finite check) and by `>= 0`. The counter is nonetheless **not strict JSON**: X1 shows a
body with bare NaN passes the whole counter. Any consumer that holds the body to RFC 8259 would reject it, the counter
would not.

## Other observations

- **Shared predicate.** The tool's `_timings_ok` and the counter's `completion_timings` clause are the same logic written
  twice. The V-series therefore cannot tell them apart; only the L-series isolates the counter. Any blind spot in one
  (CM1, CM2) is shared by the other.
- **Control coverage.** The 44-control timing family covers 4 keys (predicted_ms -1, bool, Infinity, cache_n removed).
  Not covered by any control: `predicted_n` bool (CM1), `prompt_n` negative (CM2), predicted_ms string, predicted_ms NaN,
  cache_n bool/float. Those branches are checked only by the predicate, so the "4/4" timing family does not measure
  them. Suggested control additions (for the L1 to decide): one control each for `predicted_n=true`, `prompt_n=-1`,
  `predicted_ms="3"`, `predicted_ms=NaN`, with the collateral cap.
- **Accidental duplicate.** During the L-series I once ran the L8 counter with a short tip hash and a stray empty
  argument (the output was discarded). It was harmless: a second identical scoring into the same work dir, and the full-hash
  L8 run was the one recorded.

## Tools

No tools installed or upgraded. Observed on host: Python 3.14.8, `jq` = jaq 3.1.1, node v24.21.0, bun 1.4.3. Pacman not used.

## Files

- `out/MT05ToolTimings/counter-lines.txt` — one line per run: commit, stdout, stderr.
- `out/MT05ToolTimings/{base,V1..V8,L1..L8,X1,CM1..CM3}.{stdout,stderr}` — verbatim counter output.
- `out/MT05ToolTimings/receipts/*.json` — the 17 mutant receipts and the base receipt.
- `out/MT05ToolTimings/clone-commits.txt` — the mutant commit log; `json-parser-probe.txt`; `V3/V4/X1-body.json`.

## Summary tally

Requested mutants: **8/8 KILLED** (V1–V8, `completion_timings`). Lying-tool series: **8/8 KILLED** by the counter's own
predicate (L1–L8, `inconsistent:completion_timings`). Extra: X1 **SURVIVED** (counter accepts bare NaN in the body);
CM1 **SURVIVED**, CM2 **SURVIVED** (no control covers predicted_n bool / prompt_n negative); CM3 **KILLED** (timing 2/4).

```
counter tally: V 8/8 killed, L 8/8 killed, X1 survived (met=True), CM1 survived, CM2 survived, CM3 killed (timing=2/4)
```
