# RV02C1CounterCode — line-by-line review of tools/round63-c1-counter.py

Seat: RV02C1CounterCode (reviewer, leaf, advisory). Judged on: operability. Milestone: review the build.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (freeze amendment 1). Lane tree and the tip
blobs of tools/round63-c1-counter.py, tools/kama-completion-live.py, tools/kama-llamacpp-live.py are
byte-identical (sha256 checked). Line numbers below are the tip's `tools/round63-c1-counter.py` unless
another file is named. Evidence: `.ufo/waves/round-63/w1/out/RV02C1CounterCode/` (runs.txt holds every
counter line verbatim; genuine-receipt.json; probes/*.py).

Verdict-free scope note: these are findings about the counter and its control set, not a judgment of
the C1 claim itself.

## Headline

- Baseline at tip: `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True ... exit=0` (runs.txt B0).
- The counter is sound on the paths the 44 controls exercise, and NaN/Infinity handling is correct where graded.
- Defects found, by severity:
  - HIGH-1 Witness handshake is contaminated by a stale `hold/hold.json`; a healthy tool is reported as
    `no receipt produced`, and the contamination survives reruns in the same `--work` (reproduced).
  - HIGH-2 Unguarded exceptions break the one-line contract: a broken dependency or a malformed receipt
    produces a traceback, no summary line, exit 1 (reproduced).
  - HIGH-3 Six counter-side mutants SURVIVE (met=True with the defect present): M1-M6 below. Per the recipe
    these are defects of the counter or its control set.
  - MED-1 16 of the 41 named checks/conjuncts have no targeted control; 2 of the 44 controls are exact duplicates.
  - MED-2 The `log` control named health_ready does not exercise the health body predicate (M1 proves it).
  - MED-3 Listener ownership and server/model identity are not independently witnessed (see W-OWN).
  - MED-4 The outside POST target is taken from hold.json with no refused-port check (line 398).
  - MED-5 The envelope control is credited at a 30-failure cap, admitting 26 receipt-side failures.
  - LOW: FP_RE trailing-newline/Unicode-digit acceptance; discarded tool stderr; unbound tool exit code;
    fake-foreign tests pid not ownership; a leaked fake socket; a gitignored pyc left by my probe import.

## Mutant results (counter clones, each committed in my scratch clone; unmutated tool; full output in runs.txt)

| id | mutation (tip line) | result | one-line counter output (abridged to head; full in runs.txt) |
|---|---|---|---|
| M1 | health_ready drops body-string equality (160-161) | SURVIVED | `... errors=0 met=True` |
| M2 | score live_port forced True (306-307) | SURVIVED | `... errors=0 met=True` |
| M3 | score live_nonce forced True (309) | SURVIVED | `... errors=0 met=True` |
| M4 | server_digest forced True (255-257) | SURVIVED | `... errors=0 met=True` |
| M5 | models_alias_id id-list conjunct dropped (166-167) | SURVIVED | `... errors=0 met=True` |
| M6 | completion_usage total-sum relaxed to >=0 (209) | SURVIVED | `... errors=0 met=True` |
| M7 | score stored listener_owned gate removed (286-287) | KILLED | `controls_targeted=43/44 ... errors=0 met=False`; `error: escape listener expect=listener_owned fails=[]` |
| D1 | shared port_owned_by forced True, in kama-llamacpp-live.py (dep clone) | KILLED, but NOT by a witness control | `live_ok=0/1 ... errors=1 met=False`; `error: live: ["teardown_port_closed", "verdict"]` |

Full verbatim lines for M1-M7 and D1 are in runs.txt (the line shown above is the full `families[...]` text there).
Note on M1-M6: the genuine receipt still passes, so no control touches the weakened predicate; the survivors
show the control set cannot see these conjuncts.

## HIGH-1 Witness handshake: stale hold/ state and a release/prepare race (witness_run, 374-415)

Code path:
- 377-379 `hold = work/hold`; the dir is reused as-is. Nothing clears `hold/` or the previous `receipt.json`
  (out_path, 380) before `Popen` (381-387).
- 391-398 the loop reads any `hold/hold.json` it finds, including a leftover from an earlier run, and
  calls `observe()` on its port/pid immediately.
- 404 `release` is written as soon as the loop breaks, before the tool has run its own preflight.
- Tool side: kama-completion-live.py 267 calls `prepare_witness_dir()` (kama-llamacpp-live.py 299-305), which
  unlinks `release` and `ready.json` but not `hold.json`. The counter's early `release` (404) is therefore erased
  before the tool reaches `hold_for_witness`; the tool holds until its 90 s hold timeout, and the counter's
  `proc.wait(timeout=60)` (406-409) kills it. Receipt read at 411-414 finds none.
- Tool side (kama-completion-live.py 490-497): `hold.json` is unlinked only if `hold_for_witness()` returns
  normally. A SetupError raised inside it (kama-llamacpp-live.py 341-342, 349) or a SIGKILL from the counter
  leaves `hold.json` behind, so the poison persists into the next run.

Reproduction (runs.txt F2, F2b, F2c):
- Pre-seed `--work/hold/hold.json` with an unregistered loopback port that nothing listens on (47611; checked
  absent from registry/endpoint-consumers.tsv). Run the counter at the tip:
  `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]` /
  `error: live: no receipt produced` / wall 60.28 s. A healthy tool was blamed.
- Rerun the same poisoned `--work`: the same failure (61.48 s), with `hold.json` and `ready.json` still present.
- Clean `--work`, same tip: `met=True`, exit 0.
- Mechanism: the 60 s wall time and the leftover `ready.json` (written by the killed tool) are observed; the
  "release erased by prepare_witness_dir" step is from the code (kama-llamacpp-live.py 299-305), not separately instrumented.

Impact: a false FAIL for a healthy tool, misattributed as "no receipt produced", and the recipe's reused
`--work $S/work` makes one aborted run poison every later mutant run in that scratch.

Fix direction (not applied): clear `hold/` and `receipt.json` before `Popen`; use a fresh hold dir per nonce;
release only after a `ready.json` whose pid and port match this run; count a missing witness as a named
failure, not a generic one.

## HIGH-2 Uncaught exceptions break the one-line contract (exit 1 with no summary)

The contract (docstring 23-27; freeze) is one summary line, exit 0 iff met. These paths escape it:
- Broken dependency at tip: `load_live_mod(tool_path)` (main 669; load 365-371) is unguarded. Reproduced
  (runs.txt F1): a `SyntaxError` at `kama-llamacpp-live.py:2557` produces a traceback and exit 1. No summary line.
- Malformed receipt or hold file, reproduced in-process on the genuine receipt (probes/crashprobe.py, runs.txt P1):
  - `captures.completion.usage` = 5 -> AttributeError at line 204 (`u.get`), because line 203 only guards `or {}`.
  - `captures.models.body` with `data` = 5 -> TypeError at line 164 (`for d in mj.get('data') or []`).
  - `captures` = list -> AttributeError at line 148 (`caps.get`).
  - `teardown` = string -> AttributeError at line 260 (`td.get`).
  - `checks.hold_released` = string -> AttributeError at line 266 (`stored[k].get`).
  - hold.json that is a JSON list or non-dict: `h.get` at line 391-398 is unguarded.
  - receipt.json that is a non-dict: `receipt.get` in grade() (141) and score() (280) is unguarded.
- Not reproducible here but the same class: `load_live_mod` in witness_run (399).

Fix direction: validate `isinstance(..., dict)` at the entry of grade()/score(), wrap load and I/O in a
try that prints a `met=False` summary with a named error, and never let an exception reach exit.

## HIGH-3 Mutation survivors and what they mean

- M1: `health_ready` loses its body predicate and the counter still prints met=True.
- M2: `live_port` witness conjunct is untested. A witness answered from a different port would pass.
- M3: `live_nonce` is untested. A witness whose sent prompt lacks the nonce would pass.
- M4: `server_digest` is only exercised together with `model_digest` (control `tamper` zeroes both).
  A receipt with a wrong server digest alone is not caught by any control.
- M5: `models_alias_id` id-list check is untested.
- M6: `completion_usage` total-token sum is untested; a receipt whose total is inconsistent passes.
Survivors M1-M6 are defects of the control set. The recipe says report them prominently: they are.

## MED-1 Coverage: 16 of 41 named checks/conjuncts have no targeted control; 2 controls duplicate

Computed from build_controls() on the genuine receipt (probes/coverage.py; runs.txt P2). Targeted names: 25.
Untargeted: bad_request_graded, completion_fingerprint, completion_finish_reason, completion_usage,
live_created, live_ctype, live_fp_shape, live_model, live_model_sha, live_nonce, live_port, live_server_sha,
live_status, models_alias_id, props_alias, server_digest.
Duplicates (identical mutated receipt and expected name):
- `tamper` hold_released (531-532) == `hold` (553-554).
- `tamper` teardown child_pre_dead (533-534) == `predead` (549-550).
So 42 distinct mutations back the 44 credited controls.

Fix direction: add one control per untargeted name (the M1-M6 mutants are a ready list), and remove the duplicates or
rename them as distinct mutations.

## MED-2 `log` control does not guard the health predicate (build_controls 526-527; grade 160-161)

The `log` family rewrites `captures.health.body` without re-sealing `body_sha256`. The grader rejects it at
`cap()` (line 154) because the hash no longer matches, so `health_ready` fails for a hash reason. M1 removes the
body-string predicate and the control still "rejects" for the hash reason. So the control names a check it
does not guard. Fix: re-seal (use `edit_body`-style reseal on the health capture) so the body predicate is
the only thing that can fail.

## MED-3 Listener ownership and server/model identity: not independently witnessed (W-OWN)

- observe() computes `listener_owned` with `live_mod.port_owned_by` (line 358), the same primitive the tool
  uses for its own first-answer gate and teardown (kama-llamacpp-live.py 641-659). It is not an outside
  reading.
- The fake-foreign fake (line 698-701) runs the listener inside the counter's own process and passes
  `pid=os.getpid()`. So `listener_owned` is True and the control tests only the pid conjunct. No control tests a
  stranger on the receipt's port (for example, a listener bound after teardown). The `live_owned` control
  (628) only forces the flag to False.
- D1 (port_owned_by forced True in the dep clone) is rejected only by the tool's teardown_port_closed and
  verdict (runs.txt D1), not by any witness control. So the witness ownership conjunct has no direct coverage.
- `live_server_sha` and `live_model_sha` are copied from the tool-written hold.json (observe 360-361) and checked
  for equality against constants. They are self-reported. The hold_for_witness docstring (kama-llamacpp-live.py
  330-333) names /proc/<pid>/exe as the outside observer's view; the counter never reads it.
Fix direction: hash `os.readlink('/proc/<pid>/exe')` for the witnessed pid, and add a control with a foreign
listener bound to the receipt's port after teardown, with pid = the receipt child.

## MED-4 Outside POST target is taken from a file, not validated (observe via witness_run 398)

`observe(h.get('port'), h.get('pid'), …)` contacts whatever port hold.json names. The tool's pick_port refuses
registered consumer ports, but the counter does not re-check: `refused_ports()` (kama-llamacpp-live.py 517) is
loaded (load_live_mod, 399) and never called by the counter. Given the lane rule "never contact a registered
consumer port", the counter should refuse any witness port in `live_mod.refused_ports()`. I did not exercise this
(no contact with registered ports); it is a code-path finding only.

## MED-5 Envelope control credit is wide

`is_hit` credits the envelope control at cap 30 (ENVELOPE_CAP, line 51, 530). On the genuine receipt, the
`tamper`/completion_envelope mutant produces 26 receipt-side failing checks and is still credited (probes/envcount.py,
runs.txt P3). A one-field control that cascades to 26 of 41 is the "breaks the whole receipt" case the is_hit
docstring (492-493) warns about. The eval_selftest plant 2 (508) defends at cap 5, so the policy is inconsistent
between the self-test and the control. Frozen-rule behaviour, reported as calibration risk.

## What I checked and found correct

- grade() vs tool for: health, models, props, envelope, headers, untruncated (body_bytes and Content-Length),
  choice shape, finish_reason, model id, fingerprint shape, id/created, usage sum and cached bound, timings,
  prompt_tokens vs /tokenize, request_bound (request bytes re-hashed, prompt re-read), deterministic,
  bad_request, model/server digests (re-hashed from receipt path), teardown_clean (0 or -15), port_closed.
- NaN/Infinity: is_int excludes floats and bools; is_num uses math.isfinite. Controls with predicted_ms = -1,
  True, inf are rejected by completion_timings (runs.txt P1: NaN usage and timings give met=False, no crash).
- edit_body re-seals body_sha256 and body_bytes and updates Content-Length; controls hdr, trunc, timing,
  shape, idcr, ptok, reqbind touch exactly the named field (reqbind also changes request_sha256 as intended).
- score() conjuncts that are controlled (live_fp_capture, live_ptok, live_object, live_text, live_pid, live_owned)
  are each killed by their named control; the two fakes exercise the same observe() path.
- observe(): the sent prompt is read back from the exact request bytes (line 335); /tokenize uses add_special=True
  like the tool; http() failures (None, InvalidURL, URLError) return status None without crashing (runs.txt P1).
- Exit codes: 0 iff met on the summary path; 1 otherwise.
- The counter leaves no orphan llama-server after a killed tool (pgrep check after F2: zero matches).
- The tool's hold.json is unlinked on normal return (490-497), so a healthy run leaves no state.

## LOW

- L1 FP_RE (line 46; tool 75) ends with `$`, so `'b1-aaaaaaaaa\n'` matches (runs.txt P1). `\d` also matches
  Unicode digits (`'b\u0661-…'` matches). Use `\Z` and `[0-9]`.
- L2 receipt.json is not removed before launch (380); a dead tool leaves the previous receipt readable (the nonce
  check still prevents a false pass, but the diagnostic is misleading). Tool stderr is discarded (DEVNULL, 387), so
  the only diagnostic for a tool crash is the generic `no receipt produced`.
- L3 The tool's exit code is never read (406-409 ignore returncode) and is not bound to the verdict.
- L4 make_fake() never calls server_close (715); each fake leaks its listening socket for the process lifetime.
- L5 Probe imports (not the counter runs) created `tools/__pycache__/round63-c1-counter.cpython-314.pyc` in the
  lane. tools/__pycache__ is gitignored (.gitignore:3). I did not delete it because the directory is shared with other
  seats; disclosed here.

## Reproduction index

- Baseline: `python3 tools/round63-c1-counter.py --repo <lane> --tip 03a6a1d8… --work <scratch>` (≈1.4 s).
- M1-M7, D1: committed mutants in a scratch clone (git clone --shared), run from the clone's tools/ against
  the clone's committed tip; each reset with `git reset --hard HEAD~1` inside the clone.
- F1 fixture: scratch git repo with the three tip files and a broken kama-llamacpp-live.py.
- F2: pre-seeded `--work/hold/hold.json` (port 47611, pid 1, the three pins).
- Probes: out/RV02C1CounterCode/probes/{crashprobe,httpprobe,coverage,envcount}.py.

## Recommended order (advisory; not applied)

1. Handshake: clear hold/ and receipt before launch; per-nonce hold dir; release only after a matching ready.json (HIGH-1).
2. Exception safety: type-check grade/score inputs; guard load and I/O; always print the summary line (HIGH-2).
3. Controls: add targeted controls for M1-M6 and the 16 untargeted names; de-duplicate; re-seal the health capture (HIGH-3, MED-1, MED-2).
4. Witness identity: /proc/<pid>/exe hash; foreign-listener-after-teardown control; refused-port guard (MED-3, MED-4).
5. Cosmetics: FP_RE, stderr capture to work/tool.log, exit-code binding, server_close (LOW).

## Installs and cleanup

- No tools installed or upgraded. No pacman transaction. No edits to lane source, no commits, no writes outside my
  report, my out dir, and my scratch.
- Scratch root /fast/scratch/hyaku/kama-r63/w/RV02C1CounterCode is removed before yielding (receipts and probes copied first).

Counter (tip) one-line output, final clean run: `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` (exit 0). Survivors reported above are counter-side defects, not reflected in this met=True line.
