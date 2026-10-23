VERDICT: partial — help/version and healthy-log exclusions exist in A3, but the limits need narrower F3 provenance, baseline scope, and an explicit conservative-rejection tradeoff.

## Axes and scope

Primary axis: **calibration** (what implementation and evidence establish). Secondary exposure: **coverage**, because overlap rejection can discard genuine faults; **operability**, because the exclusion is a particular runnable baseline, not every healthy execution. These are review findings, not an X1 verdict or axis score.

Reviewed `corpus/knowledge/echo-discriminating-counters.md:56-68` and `corpus/lessons/round-27.md:36-39` against the frozen counter and the committed control dispatch. No lane source edits, counter execution, live server, nested dispatch, installation, or forbidden scratch reads.

## Findings and smallest safe corrections

### 1. Repair 2's concrete help/version and healthy-log statement is supported by code, not by a completed control receipt

The requested lines are in `.ufo/waves/round-27/count-c1.py`:

- `480-490`: `run_baseline` launches **default** profile and collects responses from `BASELINE_REQUESTS` (`144-153`). Non-200 baseline responses prevent evaluation.
- `491-495`: the server is stopped, port closure is required, and its captured log is appended.
- `496-503`: both `--help` and `--version` run with stdout **and stderr** captured; nonzero exit or empty text prevents evaluation; their text joins the baseline.
- `343-348`: `occurs` compares lowercase text directly and with whitespace removed.
- `652-656`: a matching signature receives `f:in-baseline-or-help`.
- `691-694`: rows carrying a reason are not counted.

Thus the literal wording “excludes help/version text and a healthy-run log” is accurate statically. It does **not** establish exclusion of every warning/log path: the healthy sample has seven specified requests, one model, and only the default profile, whereas row execution also uses other profiles (`134-139`, `660-669`). Nor does this code independently compare against arbitrary file/model content. The entry acknowledges such residual classes, but repair 2's heading “Counter F2/F1/F3” can be read as closing all three.

**Smallest correction:** retain the implementation statement, specify “the captured default-profile baseline responses/log and captured help/version output,” and explicitly leave F3 and unsampled warning paths **unscored**, not repaired by those checks. Do not change the frozen counter. No runtime discrimination was verified by this seat.

### 2. The limits give file/model echoes a stronger preregistration provenance than the file contains

`corpus/knowledge/echo-discriminating-counters.md:58-64` groups file/model reads, logs/help, and transformed echoes, then says the counter names “them” in preregistration `controls_required`.

Actual `.ufo/waves/round-27/preregistration.json:21-35` includes:

- `30`: `log-help-warning`;
- `33`: `echo-assembly` (several request parts; case, escapes, token ids, schema dumps);
- **no explicit file-content or model-content echo class**.

The explicit F3 assignment is instead `.ufo/waves/round-27/w1-controls/spec.json:52-54`: `CtlFileEcho`, targeting content read from a file or fixture model, including GGUF metadata, chat templates and vocab pieces. The corresponding dispatch member is `dispatch.json:80-84`.

**Smallest correction:** cite preregistration for log/help and transformed-request classes, and cite the `0ec32cac` control-wave spec/dispatch for file/model echoes. Preserve the statement that no committed A3 receipt establishes their refusal. This is a fixable citation/scope defect, not evidence that a shortcut scored.

### 3. Missing limit: occurrence rejection is conservative, not proof of causal echo

Strongest local static counterexample to a causal interpretation:

```json
{"method":"POST","path":"/v1/chat/completions","body":{"unused_note":"'messages' is required"}}
```

Take signature `'messages' is required`. The pinned source `.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp:1326-1386` reaches a **fixed literal** throw when `messages` is absent (`1385-1386`); it does not splice `unused_note` into that throw. Nevertheless, `count-c1.py:351-372` exposes that unrelated JSON value, and `585-587` adds `f:in-request`.

[INFERENCE] This illustrates an authentic fixed-literal fault rejected by the occurrence rule because irrelevant request data coincides with its signature. This was **not executed**; it is not a complete registry row, does not establish passage of other clauses, and claims no counted result.

The existing “necessary, not sufficient” caveat discusses surviving shortcuts but not genuine faults discarded by the rule. Textual overlap cannot itself prove that the server echoed that text.

**Smallest correction:** add: “This is a conservative eligibility rule: overlap with irrelevant request data can also reject a genuine server-owned signature; rejection does not establish causal echo.” Treat any coverage cost as a reviewer-assessed tradeoff, not a reason to weaken the frozen predicate or silently claim no axis harm.

## w1-controls death and dispatch provenance

The wave is correctly identified as **pre-data**, not a failed data measurement. Commit `0ec32cac09b58a213450ff9f67c319100f21ac27` records 37 dispatched seats at 05:41:33Z. `w1-controls/spec.json:4` explicitly says no data seat runs in the wave. Its membership includes controls, mutations, reconnaissance and repairs (`spec.json:102-154`), so “37-seat control wave” is a wave label, not 37 independent echo-control receipts.

At assigned tip `324d5d62e61276af312c8eb42f678004aec245d1`, the committed `w1-controls/` tree contains only six dispatch/specification files, not control reports or receipts. This supports the entry's receipt boundary. The attempt-2 orchestrator death at 06:19:06Z is supplied by the canonical assignment and recorded in `a3/plan.json:8` / `corpus/lessons/round-27.md:3-9`; the earlier dispatch commit does not itself record individual worker terminal states or provider refusals.

**Safe wording:** “The attempt-2 orchestrator died; the dispatched control wave has no committed A3 control receipts.” Do not infer that every worker had the same terminal state. C1 remains withdrawn before data; this seat does not score its counter.

## Commands and observed evidence

All commands were read-only, completed successfully with exit **0**, and started no persistent process. Paths below are absolute in the commands; other pointers above are relative to the lane root.

```text
$ timeout 20s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
exit 0

$ timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --no-patch --format=fuller 0ec32cac
commit 0ec32cac09b58a213450ff9f67c319100f21ac27
[author metadata trimmed]
CommitDate: Fri Oct 23 02:41:50 2026 -0300
    round-27: wave 1 (pre-data control wave + repairs + recon) spec, validation and dispatch record (37 seats, dispatched 05:41:33Z)
exit 0

$ timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 324d5d62e61276af312c8eb42f678004aec245d1 .ufo/waves/round-27/w1-controls/
.ufo/waves/round-27/w1-controls/dispatch.json
.ufo/waves/round-27/w1-controls/dispatched-payload.json
.ufo/waves/round-27/w1-controls/solution-spaces.json
.ufo/waves/round-27/w1-controls/spawn-result.txt
.ufo/waves/round-27/w1-controls/spec.json
.ufo/waves/round-27/w1-controls/validate.err
exit 0
```

Static excerpts were obtained with the `read` tool using the exact file:line selectors cited above (tool reads have no process exit code), including `spec.json:52-54:raw`, `preregistration.json:21-35:raw`, and `count-c1.py:572-588:raw`. The timestamp in `w1-controls/spawn-result.txt:1` is `2026-10-23T05:41:33.096709Z`. No test, replay, full counter, or live probe was run; all dynamic outcomes remain unverified by this seat.
