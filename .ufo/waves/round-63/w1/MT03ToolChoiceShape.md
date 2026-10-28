# MT03ToolChoiceShape — C1 operability: choice-shape falsification

Seat: MT03ToolChoiceShape (mutation-tester, leaf). Round 63, kama lane, claim C1-r63.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (amendment 1 tip).
Scope: forge the `completion` capture (and, where needed, `completion2`) inside the
committed `tools/kama-completion-live.py` so the receipt violates the choice-shape
property (two choices / index != 0 / empty text / non-null logprobs) while
`body_sha256` and `body_bytes` (and `content-length`) are resealed; score each with the
unmutated counter. No verdict on the claim is given here; this is evidence for L1.

## Method

- Clone: `git clone -q --shared` of the lane into `$S/clone-base` (T0 = 03a6a1d8), then
  one clone per mutant `$S/m-<k>`, each edited only inside its clone with `edit`,
  `git add -A` + commit (`-c user.name=seat`), tip = that commit. Every clone asserted
  with `git rev-parse --show-toplevel`.
- Mutation point: immediately after `c = caps['completion']` (tool line 355) the body is
  parsed, one field is changed, the body is re-serialised and resealed
  (`body_sha256`, `body_bytes`, `content-length`). The `ok_env`/envelope path is untouched.
- Two grader variants per defect:
  - **lazy**: the tool's own `completion_choice_shape` predicate is replaced by `ok_env`
    (the receipt would be stamped REQUEST_OK by a grader that only checks the envelope).
  - **intact**: the tool's own predicate is left as committed (tool self-rejects).
- Counter: the unmutated `tools/round63-c1-counter.py` run from `$D/tools/` with
  `--repo $D --tip $T --work $S/work/run-<k>`, `PYTHONDONTWRITEBYTECODE=1`.
- Counter-side probes (only to answer the masking question and to test the choice-shape
  clauses): clones `c-CM1..3` (from m-L3b) and `c-BOOL` (from m-L6) each with one counter
  clause removed, committed, and scored by the counter from its clone path.
- Tools: none installed or upgraded. `llama-server` (`~/.local/bin`, pre-existing) and
  the pinned model (sha256 270cba1b... verified) were used as-is. No pacman, no sudo.
- Live contact: only the lane tool on unregistered loopback ports, launched by the
  counter; no registered consumer port, no foreign llama-server touched.

## Baseline (positive control)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0. The unmutated tip is met=True, so non-met mutant results below are not baseline noise.
The baseline receipt's `completion` body is `choices[0]` with `index 0`, `text " ground. She liked"`,
`logprobs null`, `content-length 619` = `body_bytes`.

## Tool mutants (12) — all KILLED

Unmutated counter, one line each (stdout verbatim; stderr `error:` line in the second line).
All 12 print `met=False`. In every case the rejection happens at the **live stage**
(`live_ok=0/1`), so no control is credited for these receipts.

| id | defect in capture (resealed) | grader | receipt verdict (tool) | KILLED by |
|---|---|---|---|---|
| m-L1 | two choices, both index 0 | lazy | REQUEST_OK | completion_choice_shape |
| m-L2 | choices[0].index = 1 | lazy | REQUEST_OK | completion_choice_shape |
| m-L3a | choices[0].text = "" (completion only) | lazy | FAIL | completion_choice_shape, completion_deterministic, verdict |
| m-L3b | text "" in completion AND completion2 | lazy (det intact: "" == "") | **REQUEST_OK** | completion_choice_shape, completion_deterministic |
| m-L3c | text "" (completion only) | lazy choice + lazy det | **REQUEST_OK** | completion_choice_shape, completion_deterministic |
| m-L4 | choices[0].logprobs = {} | lazy | REQUEST_OK | completion_choice_shape |
| m-L5 | choices[0].logprobs = false (falsy, non-null) | lazy | REQUEST_OK | completion_choice_shape |
| m-L6 | choices[0].index = false (bool) | lazy | REQUEST_OK | completion_choice_shape |
| m-I1 | two choices | intact | FAIL | completion_choice_shape, verdict |
| m-I2 | index = 1 | intact | FAIL | completion_choice_shape, verdict |
| m-I3 | text "" | intact | FAIL | completion_choice_shape, completion_deterministic, verdict |
| m-I4 | logprobs = {} | intact | FAIL | completion_choice_shape, verdict |

Counter lines (identical prefix for all 12; `met=False`, `live_ok=0/1`, `controls_targeted=0/0`):

```
m-L1  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
m-L2  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
m-L3a tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "completion_deterministic", "inconsistent:completion_choice_shape", "verdict"]
m-L3b tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "completion_deterministic", "inconsistent:completion_choice_shape", "inconsistent:completion_deterministic"]
m-L3c tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "completion_deterministic", "inconsistent:completion_choice_shape", "inconsistent:completion_deterministic"]
m-L4  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
m-L5  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
m-L6  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
m-I1  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "verdict"]
m-I2  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "verdict"]
m-I3  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "completion_deterministic", "verdict"]
m-I4  tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "verdict"]
```

Reading: the lazy-grader receipts (L1–L6 and the masking pair L3b/L3c) are stamped
REQUEST_OK by the tool itself; the counter's recomputation from captured bytes is what
rejects them, and it names the choice-shape check (and, for the empty-text pair,
completion_deterministic) plus the stored-vs-recomputed `inconsistent:` entry. The
intact-grader receipts are rejected by the tool's own predicate too (verdict FAIL) and the
counter independently recomputes the same failure.

## Masking question: can completion2 determinism mask an empty-text receipt?

Short answer: **not at the counter**; **yes at the tool**.

- Tool side (`tools/kama-completion-live.py`, `det` predicate ~line 452–457): determinism
  is `c2 text == c text` and never requires non-empty text. Evidence: m-L3b receipt has
  `completion` text `""` and `completion2` text `""`, stored `completion_deterministic`
  passed, stored `completion_choice_shape` passed (lazy), verdict **REQUEST_OK**
  (`work/run-L3b/receipt.json`, `captures.completion(2).body` both `text:""`). Empty-text
  identity passes the tool's determinism check by itself, so the tool's grade cannot
  reject empty text on determinism alone.
- Counter side: `completion_deterministic` carries an explicit clause
  `ch0.get('text') not in (None, '')`, and `completion_choice_shape` carries
  `ch0.get('text') != ''`. Two independent clauses, plus a dedicated control family
  member (`shape` with `text: ''`). Probes:

```
c-CM1 (counter: drop choice-shape text clause; tool m-L3b)
      tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_deterministic", "inconsistent:completion_deterministic"]
c-CM2 (counter: drop determinism non-empty clause; tool m-L3b)
      tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]
      error: live: ["completion_choice_shape", "inconsistent:completion_choice_shape"]
c-CM3 (counter: drop BOTH clauses; tool m-L3b)
      tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=3/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
      error: escape shape expect=completion_choice_shape fails=[]
```

So CM1 and CM2 are each KILLED by the surviving clause (the two are redundant), and
CM3 shows that with both clauses gone the live stage **accepts** the empty-text receipt
(`live_ok=1/1`) and the only remaining rejection is the `shape text ''` control
escaping (`shape=3/4`, met=False). Determinism therefore cannot mask an empty-text
receipt in the committed counter, but the protection is two clauses plus one control;
a single counter edit that removes both would be caught only by that one control.

## Counter-side finding (SURVIVED) — prominent

**c-BOOL: the counter's bool guard on `index` is unprotected by any control.**
Counter mutant: `and not isinstance(ch0.get('index'), bool)` removed from
`completion_choice_shape` (tools/round63-c1-counter.py line 192). Tool: m-L6 (lazy,
`choices[0].index = false`). Unmutated counter KILLS m-L6 (see table); the mutated counter
does not:

```
c-BOOL (counter: no bool guard on index; tool m-L6)
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

`met=True` with the defect present: `False == 0` is `True` in Python, so `index: false`
passes `ch0.get('index') == 0`, and the `shape` family (two-choices, index 1, text "",
logprobs {}) has no member that exercises a bool index. Result: the choice-shape
clause for `index` has a single point of defence (the bool guard) that no control names.
Under the freeze's kill rule ("any control not rejected by its named check") this is a
coverage gap in the control set, not a fail of the current tip (the committed counter
rejects m-L6). Recommended for L1 (not applied here; no lane edits): add a `shape` control
`choices[0].index = False` expecting `completion_choice_shape` and a control for
`completion2` text "" (the determinism non-empty clause currently has no named control;
CM2 shows it is only backed by the choice-shape clause).

Also noted, not a survivor: a falsy non-null `logprobs` (m-L5, `false`) is rejected by the
committed `is None` clause; the only logprobs control is `{}`. A counter mutant changing
`is None` to a truthiness test would be caught by the `{}` control (not run; no separate
probe needed for this report).

## Other observations (tool side)

- The tool's own `completion_choice_shape` predicate is the only tool-side guard on the
  property; it is a single expression and is trivially relaxable (m-L1..L6 show this).
  The counter does not trust it (`inconsistent:` entries in every lazy run), so the
  tool-side laxity is caught; the tool's stored verdict is not evidence.
- The tool's determinism predicate does not require non-empty text (see masking section).
  This is a tool-side gap that the counter covers only through its own clauses.
- No change to any lane source, no commit to the lane, no lane index/jj touch.

## Verdict table for L1 (no verdict on the claim)

- Tool mutants: 12/12 KILLED (12 `met=False` lines above).
- Masking probe: determinism cannot mask an empty-text receipt at the committed counter (CM1/CM2 killed by the surviving clause); tool-side determinism alone does accept `""==""` (m-L3b REQUEST_OK).
- Counter-side: 1 SURVIVED (c-BOOL, bool-index guard, met=True).

## Evidence

- Receipts and outputs: `.ufo/waves/round-63/w1/out/MT03ToolChoiceShape/receipts/*.json`
  (base, 12 tool mutants, 4 counter probes), `counter-outputs.txt` (all one-liners + stderr),
  `mutants/*.patch` (each mutant's diff vs its base commit, i.e. the forged tool or counter line).
- Mutant tips (scratch, deleted at yield): the commit SHA of each mutant and counter probe is listed in `out/MT03ToolChoiceShape/tips.txt`; these are not lane commits.
- Scratch root `/fast/scratch/hyaku/kama-r63/w/MT03ToolChoiceShape` removed before yield.
- Tooling: no install or upgrade. Used the pre-existing `~/.local/bin/llama-server` binary and the pinned model (sha256 270cba1b... verified by the counter).
