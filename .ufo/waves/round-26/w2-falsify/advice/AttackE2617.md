# ATTACK E26-17 / S130: holds

Target: SKILL.md row `E26-17` (signature `GGML_ASSERT(n_outputs >= 1)`), its registry
entry in `registry/error-signatures-r26.json`, source row `S130`
(`llama-context.cpp:2624`), and the lesson Gate quote for S130.

Verdict per check: (1) holds, (2) holds, (3) holds, (4) holds, (5) holds. No defect
found; no correction required. One non-blocking observation (coarse path description)
recorded under residual risk.

Port block used: 47764 (run 1), 47765 (run 2). Both opened and closed by me; both
killed/exited before I returned. `pgrep -af llama-server` after my runs showed only two
sibling seats' servers (ports 47720, 47734), none of mine.

## Preconditions (verified)

- `ss -ltn` before start: `ports 47764-47767 all free`.
- llama-server sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` == pin (`count-c1.py:SERVER_SHA256`). exit 0.
- fixture model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` == pin (`count-c1.py:MODEL_SHA256`). exit 0.

## (1) Re-run the registered trigger twice — holds

Registry fields for E26-17: channel `startup`, args `["-t","2","--ctx-size","-5"]`,
model `fixture`, no request (startup). The counter prepends
`-m <fixture> --host 127.0.0.1 --port P`. Command run (per run, with its own port):

```
timeout 30 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf \
  --host 127.0.0.1 --port <47764|47765> -t 2 --ctx-size -5
```

- Run 1 (port 47764): `EXIT_CODE=134`; then `port 47764 closed`.
- Run 2 (port 47765): `EXIT_CODE=134`; then `port 47765 closed`.

134 = 128 + SIGABRT(6). `count-c1.py` startup rule is "exits non-zero within 30 s"
(`run_trigger`: `out["error_shown"] = rc is not None and rc != 0`): satisfied, 134 != 0,
exited well within the 30 s `STARTUP_WAIT`.

Signature in the registered channel (startup = stdout+stderr), identical both runs,
at log line 5:

```
/home/runner/work/llama.cpp/llama.cpp/src/llama-context.cpp:2624: GGML_ASSERT(n_outputs >= 1) failed
```

`grep -F 'GGML_ASSERT(n_outputs >= 1)'` matched run1.log:5 and run2.log:5. The registry
signature (no trailing `;`) is a substring of this runtime line. Deterministic across
both runs.

## (2) Fault's own text, not a warning / not an unrelated path / not echoed — holds

- Log head (run1.log:1-5): `initializing ...` → `common_params_print_info` → a generic
  `W ... security: no API key is set and CORS allows all origins` (present on every
  startup, unrelated to this fault) → `load_model: loading model '.../stories260K.gguf'`
  → **then** the assert line. No other `error`/`fail`/`abort` line precedes the assert
  (`grep -niE 'error|fail|abort|assert|invalid|negative'` returned only line 5, the
  assert, and line 54, `ggml_abort` in the backtrace).
- The assert IS the failure, not a bystander line: the backtrace shows the non-zero exit
  is produced by the assert itself —
  `ggml_abort` (#3) ← `llama_context::graph_reserve(...)` (#4) ← `sched_reserve` (#5) ←
  `llama_context::llama_context` (#6) ← ... ← `load_model` (#13). This defeats **F1**
  (the counter limit where a warning on an unrelated startup failure would count): there
  is no separate failure; the assert is the sole, named cause.
- **F2/F3** (echo through a decoded request field / query / header / argument file): this
  is a startup row with no HTTP request and no file-valued argument. The string
  `GGML_ASSERT(n_outputs >= 1)` does not occur in the args `-t 2 --ctx-size -5`. The
  counter's `e_not_echoed` (`sig not in req_bytes`, where `req_bytes` is built from the
  trigger key + args + request fields) therefore holds. No echo path.

## (3) Pinned source line and 'meaning (code)' cell — holds

- Fresh fetch at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (access 2026-10-23),
  `src/llama-context.cpp`, from
  `raw.githubusercontent.com`: sha256
  `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5`.
- Lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/llama-context.cpp`:
  same sha256; `diff -q` reports IDENTICAL. Matches the S130 anchor sha256 and the
  `count-c1.py:SOURCE_SHA256["llama-context.cpp"]` pin.
- Fresh line 2624 is `    GGML_ASSERT(n_outputs >= 1);`, inside
  `ggml_cgraph * llama_context::graph_reserve(...)` (signature opens at line 2621). The
  URL `#L2624` resolves to the assert line exactly.
- Row's `meaning (code)` cell: "a negative context passes argument parsing; graph
  reservation then asserts `n_outputs >= 1` (`llama-context.cpp:2620-2624`) and aborts
  with a backtrace." Each clause is supported:
  - "passes argument parsing": the process reached `load_model` (log line 4) before any
    error — arg parsing accepted `--ctx-size -5`.
  - "graph reservation then asserts `n_outputs >= 1`": backtrace frame #4 is
    `graph_reserve`, and 2624 is that assert.
  - line range `2620-2624`: 2621 is the function head, 2624 the assert — the range spans
    head-through-assert; the runtime itself prints `:2624`. Consistent, not misstated.
  - status/exit claim "exit status 134, SIGABRT, observed": matches both my runs (134).

## (4) 'next action' cell supported, not overreach — holds

Cell: "A supervisor sees a crash (signal 6), not a usage error. Check the launch flags
for a negative or non-numeric context before suspecting the build."
- "signal 6" = SIGABRT; exit 134 = 128+6 — supported by the observed exit.
- "not a usage error" — supported: arg parsing accepted the value; the failure is an
  abort during context/graph reservation, not an arg-parse rejection.
- "Check the launch flags for a negative ... context" — the trigger is `--ctx-size -5`;
  the advice points back at the operator-supplied flag, no broader claim. No overreach.

## (5) SOURCES S130 cells and lesson Gate quote — holds

- `corpus/SOURCES.md:142` S130: URL ends `#L2624` (correct line); anchor cell repeats
  sha256 `2a25e556...94aa5` (matches fresh fetch); `teaches` is scoped to "commit
  704366d76 only; not other builds" (honest); type `code`, tier `A`, `mined`, access
  `2026-10-23`, used-by `SKILL.md, registry/error-signatures-r26.json`. The embedded
  prose repeats the meaning cell and defers the live trigger/next-action to the SKILL
  row — consistent.
- `corpus/lessons/round-26.md:43` Gate quote: "line 2624: `GGML_ASSERT(n_outputs >= 1);`"
  — verbatim equal to fresh line 2624 (with the trailing `;`); ≤25 words; URL `#L2624`.

## Counted-predicate corroboration (static clauses I could check directly)

- Clause (b) new-at-base: `git -C <lane> grep -F -e 'GGML_ASSERT(n_outputs >= 1)'
  1560e4d8 -- SKILL.md corpus` → exit 1 (not present at base). Holds.
- Clause (g) one-fault/one-row: trigger `--ctx-size -5` differs from every other
  registered trigger; the signature is neither substring nor superstring of the other
  two startup signatures ("failed to open GGUF file", "invalid magic characters: '")
  and does not appear in their channel text. Holds.

## Residual risk / verification gaps

- Non-defect nuance: the `meaning (code)` cell says "graph reservation then asserts," but
  the observed path reaches `graph_reserve` via the auto memory-fit probe
  (`common_fit_params` → `common_get_device_memory_data_impl` →
  `llama_context::sched_reserve`, backtrace frames #11→#8→#5), not the post-fit "real"
  context build. The cell's wording is coarse but not wrong (graph reservation does
  assert); no correction required. If a future round wants maximal precision, it could
  add "(during the memory-fit probe, `common_fit_params`)". Optional, not a defect.
- I did not re-run the full frozen counter (it is lane-wide, needs the host lock, and the
  landed-tip receipt `final/c1-tip.out` already records `registered 17 counted 17 met
  True`); this seat verified the E26-17/S130 row in isolation. Clauses (e),(b),(g) for
  this row are confirmed above; clauses (a),(c),(d),(f) were read against the frozen
  `count-c1.py` logic and the pinned artifacts and are consistent.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/AttackE2617.md` (this report)
- Scratch (not in lane): `/fast/scratch/hyaku/kama-r26w2/AttackE2617/{run1.log,run2.log,fresh-llama-context.cpp}`
