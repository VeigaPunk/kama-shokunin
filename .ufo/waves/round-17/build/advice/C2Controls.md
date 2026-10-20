VERDICT: confirm — C2 counting command landed at `tests/llamacpp-live/controls.py`; frozen arm counts 6 accepted-bad behaviours (+1 inconclusive), current v2 pair counts 0/0/0 and the good control is accepted.

# Files written

| path | sha256 | mode |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py` | `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06` | 0755, 26791 bytes |

Nothing else was written. Scratch (`/tmp/C2Controls-*`, the suite's own
`TemporaryDirectory` sandboxes) was removed before finishing; the two live
processes still visible under `/tmp/KamaR17-C2LiveTool-2/` belong to the
sibling seat `KamaR17-C2LiveTool-2`, not to me.

# CLI

```
tests/llamacpp-live/controls.py --tool PATH --gate PATH [--probe PATH] [--json] [--only ID]
```

`--only` accepts `k0..k8`. Default probe is `<lane>/tools/kama-probe.sh`.
Every control runs exactly the item's command shape:

```
python3 <staged TOOL> --server <fake> --model <32-byte file> \
  --model-sha256 <digest> --alias fakealias --probe <probe> --out <receipt>
python3 <GATE> <receipt>
```

(`sys.executable` is used instead of the literal `python3`, and the tool is a
byte-identical staged copy — below.)

# Controls

| id | shape | targeted failure | expected failed-check tokens |
|---|---|---|---|
| k0 | ≥3 exact loading 503s on `/v1/models`, ≥1 on `/health`, then ready; SIGTERM handler `exit 0` | none — must be ACCEPTED (tool 0, gate 0) | — |
| k1 | `/health` 200 `{"status":"degraded"}` after loading | health body not graded against `{"status":"ok"}` | `health` |
| k2 | 3× `/v1/models` + 1× `/health` 503 `{"error":{"message":"Busy","type":"unavailable_error","code":"503"}}` | loading envelope not exact (message, string code) | `loading`, `envelope` |
| k3 | exits rc 0 itself right after the 2nd probe run's `/v1/models` is flushed | teardown passes on a self-exit (`sigterm_sent false`) | `teardown` |
| k4 | ignores SIGTERM (`SIG_IGN`) → needs SIGKILL | teardown graded only as "reaped" | `teardown`, `sigkill`, `kill`, `graceful` |
| k5 | SIGTERM handler exits rc 1 | teardown accepts any returncode | `teardown`, `graceful`, `signal`, `returncode`, `exit_status` |
| k6 | tool `teardown()` monkeypatched to raise `RuntimeError` | receipt must still be written, exit 2 | `teardown`, `fault` |
| k7 | listens (raw accept backlog), never answers; `--ready-timeout 2` | readiness must fail closed | — |
| k8 | default SIGTERM disposition (killed, rc −15) | teardown must require a harness-initiated graceful exit | `teardown`, `graceful`, `signal`, `returncode`, `exit_status` |

Every serving fake answers the loading 503s with the exact llama.cpp
envelope before going ready, so the v2 `loading_observed` /
`loading_envelope_exact` checks have real evidence on the good control too
(L1 decision 1). `/v1/models` then serves `data[0].id == --alias`,
`owned_by: "llamacpp"`; `/props` serves `model_alias`; `/metrics` serves 501;
`/slots` a list; unknown paths 404. The Server header is `llama.cpp`.

# How each control is judged

* **k0 accepted** iff tool exit 0, receipt written, gate exit 0.
* **k1–k5, k7, k8 rejected** iff a receipt was written and (tool exit ≠ 0 or
  gate exit ≠ 0). k6 is stricter: receipt written and tool exit ∉ {0, null}.
* **accepted-bad** = a bad control that was accepted, or that escaped
  (nonzero exit with no receipt, e.g. an uncaught traceback). Escapes are
  flagged per-row (`escaped: true`).
* **attribution** (L1 decision 4): each control declares lowercase substrings
  of the check ids it targets. A rejected run whose failed checks cover none
  of them is `inconclusive` — reported, never counted as detection, and it
  makes the exit code 1.
* **gate-flip arm** (L1 decision 5): for every bad control whose receipt has
  failing checks, a copy with only those `passed` flags flipped to true is
  re-run through the gate. Gate exit 1 (INVALID) is a rejection; gate exit 0
  increments `gate_flip_bad`. The row records `receipt_setup_error` so a
  rejection that could come from `setup_error` alone (rather than
  re-derivation) is visible: k3, k6, k7 here; k1, k2, k4, k5, k8 had
  `setup_error: null`, so their flips do isolate check re-derivation.

# Measured result (advice, not a verdict — L1 owns the official run)

Both arms were run from the lane root. Frozen arm:

```
python3 tests/llamacpp-live/controls.py \
  --tool .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py \
  --gate .ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py --json
```

| arm | tool sha256 | gate sha256 | accepted_bad | gate_flip_bad | inconclusive | good_ok | exit |
|---|---|---|---|---|---|---|---|
| frozen (before) | `b8c5e8d4…f4fe4` | `6b9576a1…9ced6` | **6** | 0 | 1 | true | 1 |
| current (after) | `76a34e42…b175` | `14a0d285…76d3c` | **0** | 0 | 0 | true | 0 |

Frozen per-control outcome (tool exit / gate exit / teardown check passed):

| id | tool | gate | receipt | failed checks | outcome |
|---|---|---|---|---|---|
| k0 | 0 | 0 | yes | — | GOOD-OK |
| k1 | 0 | 0 | yes | — | **ACCEPTED-BAD** (health body never read) |
| k2 | 0 | 0 | yes | — | **ACCEPTED-BAD** (loading envelope never graded) |
| k3 | 2 | 1 | yes | — | INCONCLUSIVE (rejected, but `teardown_exited` passed: self-exit rc 0 was accepted by the check set) |
| k4 | 0 | 0 | yes | — | **ACCEPTED-BAD** (returncode −9 + `sigkill_sent true` scored as a pass) |
| k5 | 0 | 0 | yes | — | **ACCEPTED-BAD** (returncode 1 scored as a pass) |
| k6 | 4 (wrapper escape code) | — | **no** | — | **ACCEPTED-BAD / ESCAPED** (KeyError('returncode') in `finally`, no receipt) |
| k7 | 2 | 1 | yes | — | rejected (`ready-timeout`, exit 2) |
| k8 | 0 | 0 | yes | — | **ACCEPTED-BAD** (rc −15 scored as a pass) |

Current per-control outcome:

| id | tool | gate | failed checks | attributed | gate flip | outcome |
|---|---|---|---|---|---|---|
| k0 | 0 | 0 | — | — | — | GOOD-OK |
| k1 | 1 | 1 | `health_ready` | yes | INVALID (exit 1, 1 flipped, no setup_error) | rejected |
| k2 | 1 | 1 | `loading_envelope_graded` | yes | INVALID (exit 1, 1 flipped, no setup_error) | rejected |
| k3 | 2 | 1 | `teardown_graceful`, `teardown_port_closed` | yes | INVALID (exit 1, 2 flipped, `setup_error: post-probes:child-exited-rc0`) | rejected |
| k4 | 1 | 1 | `teardown_graceful` | yes | INVALID (exit 1, 1 flipped, no setup_error) | rejected |
| k5 | 1 | 1 | `teardown_graceful` | yes | INVALID (exit 1, 1 flipped, no setup_error) | rejected |
| k6 | 2 | 1 | `teardown_graceful`, `teardown_port_closed` | yes | INVALID (exit 1, 2 flipped, `setup_error: internal:RuntimeError`) | rejected |
| k7 | 2 | 1 | `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded` | — (none expected) | INVALID (exit 1, 3 flipped, `setup_error: ready-timeout`) | rejected |
| k8 | 1 | 1 | `teardown_graceful` | yes | INVALID (exit 1, 1 flipped, no setup_error) | rejected |

Reading of the two arms: the frozen pair accepted 6 of the 8 corrupt
behaviours (k3 was rejected but its teardown check still passed, so it is
inconclusive; only k7 failed closed) and lost its receipt on the teardown
fault; the current v2 pair rejects all 8
through the specific check that grades each misbehaviour (all attributed),
and the gate independently re-rejects doctored receipts whose failing checks
were flipped to true.

# Design choices

* **Staging (L1 decision 3 / sentinel 1).** Every run copies `--tool` to
  `<tmp>/<id>/lane/tools/<basename>` and, when the lane registry exists,
  copies `registry/endpoint-consumers.tsv` to
  `<tmp>/<id>/lane/registry/endpoint-consumers.tsv`. The frozen tool resolves
  its registry from its own path (`tools/kama-llamacpp-live.py:52-53`), so
  running the frozen file in place would otherwise die with
  `registry-unreadable` before launch on every control, including k0. The
  staged copy is byte-identical, so `tool_sha256` in the JSON still names the
  path the caller passed.
* **Fake isolation (sentinel 5).** The fake lives alone in `<tmp>/<id>/srv/`,
  because the tool hashes every regular file beside `--server`
  (`install_tree`, `tools/kama-llamacpp-live.py:146-170`). Its pid file is
  created after launch, so it never enters the recorded tree.
* **Cleanup (sentinel 2).** The fake writes `srv/fake.pid` before serving.
  After each control the suite reads that pid, verifies
  `/proc/<pid>/cmdline` names that exact `fake_server.py`, then
  `killpg(SIGKILL)` (the tool starts the child with `start_new_session`, so
  the fake's pgid equals its pid). A belt-and-braces second pass runs in the
  per-control `finally`, and no fake survived any run (`pgrep -af
  fake_server.py` empty; the only matches afterwards were the sibling seat's).
  No listener on 8080/34113 was ever created.
* **K6 in a child process (L1 decision 6 / sentinel 3).** The tool runs
  under `python3 -B -c <wrapper>`: `importlib` loads the staged tool
  (`__main__` guard never runs), `teardown` is replaced by a function that
  writes `k6.fired` and raises. The wrapper catches `BaseException`, prints
  the traceback, and exits 4, so the v1 escape is observable and this
  process's signal dispositions are untouched. If a receipt is written while
  `k6.fired` is absent, the suite declares its own fault (exit 2) instead of
  grading real teardown — a deliberate guard against a vacuous K6 after a
  rename or an indirect call (sentinel follow-up). A missing receipt is
  classified as an escape, not a fault.
* **TMPDIR (sentinel 4)** is set to the control workdir so the tool's
  `mkstemp` log lands in the sandbox.
* **Per-control timeout 180 s (L1 decision 6).** k4 costs the tool's 10 s
  SIGTERM grace plus the SIGKILL wait.
* **Loading window.** The fake's loading counter is per path
  (`{"/v1/models": 3, "/health": 1}`), so the two-phase readiness loop
  records at least one verbatim 503 before ready, and a v2 loading check has
  evidence on every serving control.
* **Attribution tokens, not ids.** Check ids were renamed between v1 and v2
  (`teardown_exited` → `teardown_graceful`; `loading_envelope_exact` is now
  graded as `loading_envelope_graded`), so expected failure is expressed as
  substrings matched against the *failed* check ids of the receipt.

# JSON shape

The item's required keys are all present exactly once:
`schema`, `tool_sha256`, `gate_sha256`, `controls[].{id,tool_exit,gate_exit,receipt_written,failed_checks,accepted}`,
`accepted_bad`, `good_ok`. L1 decisions 4 and 5 require additional fields, so
each control row also carries `expected_failed`, `attributed`, `inconclusive`,
`rejected`, `escaped`, `teardown_ok`, `gate_flip`, `tool_stderr_tail`, and
the top level adds `gate_flip_bad` and `inconclusive`.

Exit codes: 0 iff `accepted_bad == 0 and gate_flip_bad == 0 and
inconclusive == 0` and the good control was accepted; 1 otherwise; 2 when
this suite's own machinery fails (bad path, staging error, K6 patch miss).
`good_ok` is `null` under `--only` without k0.

# Known limitations

* `attributed` is a substring heuristic. It is necessarily weaker than exact
  ids across a receipt-schema change; a future check named, say,
  `teardown_port_release` still matches `teardown`, but a wholly renamed
  concept would not. L1 decisions 4's "mismatch = inconclusive" keeps a
  missed rename from being counted as detection, so the failure mode is a
  red run, never a false green.
* The gate-flip arm cannot isolate check re-derivation when the receipt also
  carries `setup_error` (k3, k6, k7 here): the gate rejects on the setup
  error before it can disagree about a flipped check. Rows expose
  `receipt_setup_error` so this is visible; k1, k2, k4, k5, k8 are the
  non-trivial flips in this measurement.
* k3's "self-exit after the probe captures" is anchored to the second
  `curl`-user-agent `/v1/models` request (the lead of the second
  `kama-probe.sh` run). A replacement probe that does not send a curl
  user-agent would make k3 exit late, and k3 would then be rejected as a
  teardown/graceful failure only if the harness notices; a non-curl probe
  would disable the trigger. The current probe is `curl`
  (`tools/kama-probe.sh:294`).
* k7's receipt also fails `loading_envelope_graded` on the current v2 tool
  (nothing was ever observed). That is v2 conservatism on a never-ready run,
  not a defect of this suite; k7 declares no expected check because its
  contract is only "must be rejected".
* The fake is not llama.cpp: it reproduces the documented surfaces and the
  signal/exit behaviours, so these controls grade the *harness*, never the
  runtime. [INFERENCE] a real llama-server whose `/health` body differs from
  `{"status":"ok"}` would be graded exactly like k1.
* The current tool was edited by sibling seats during this work; two early
  runs saw in-flight states (`NameError: source_bindings`, a `KeyError:
  'teardown_exited'` from a `DOC` table mid-rename). Those runs are not
  reported as measurements. The current figures are pinned to tool
  `76a34e42…` / gate `14a0d285…`; L1 MUST re-run after the v2 files settle.
* `model_unchanged` is never exercised as a failing check (its only failure
  is external mutation); it is not part of any control's targeted set.

# Installs / privilege / privacy

* No installs, upgrades or service restarts.
* No `llama-server` and no real model: all servers were generated fakes on
  ephemeral loopback ports chosen by the tool; the model was a 32-byte temp
  file with its own digest.
* No port 8080/34113 or registry-listed port was bound or probed; the final
  `ss -ltnp` check showed nothing listening on the pins.
* No file outside `tests/llamacpp-live/controls.py`, this report, and
  removed `/tmp` scratch was touched. No `jj`/git write command was run.
