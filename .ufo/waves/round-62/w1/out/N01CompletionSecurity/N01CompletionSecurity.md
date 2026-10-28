# N01CompletionSecurity — security review, round 62 kama (run 2, wave w1)

Seat: security review of `tools/kama-completion-live.py` and `tools/round62-c1-counter.py`
at tip `65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master` == HEAD at review
time), base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3` per
`.ufo/waves/round-62/controls/freeze.txt`.

Read-only seat: no lane source, ledger, scorecard or registry file was modified; nothing was
committed, staged, or checked out; no mutating git/jj command was run; the lane Git index was
untouched. The only files written inside the lane are this report and its `out/` evidence and repro directories.
No tool was installed or upgraded (python3 stdlib only; no pacman/uv/npx/cargo). Scratch root
`/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity` — every command passed it explicitly as
`TMPDIR`/`-p`; it is deleted after the receipts below were copied out.

Concurrent state, disclosed: while this review ran, another seat edited `tools/round62-c1-counter.py` in the working tree (3 uncommitted in-place lines;
worktree sha256 `a3498308…` vs tip blob `275610b5…`). Every citation to that file is a line that edit does not change, **except F0**, where the tip blob was extracted with
`git show 65d7cad:tools/round62-c1-counter.py` and tested directly against the tip-blob tool's receipt. `tools/kama-completion-live.py` in the working tree is byte-identical to the tip
(`71ac4f2c…`).

This is not a verdict on C1 or C2. It is a review of the two instruments named in the freeze as
C1's fix, and every claim about their behaviour below is either measured on this host or cited to
a line.

## Summary

| # | Severity | Surface | File:line |
|---|----------|---------|-----------|
| F0 | **High** | committed counter cannot accept the committed tool's receipt (`hold` vs `hold_released`), so `met=True` is unreachable at the tip | `tools/round62-c1-counter.py:165` vs `tools/kama-completion-live.py:408-412` |
| F1 | **High** | graded POST routed through ambient proxy env; no redirect/proxy refusal | `tools/kama-completion-live.py:101` |
| F2 | Medium | 30x followed off-loopback, response treated as the graded capture | `tools/kama-completion-live.py:101`, `tools/round62-c1-counter.py:73` |
| F3 | Medium | counter trusts `hold.json` for target + identity; hold dir never cleared; no refused-port check | `tools/round62-c1-counter.py:226,238-248,245-246,261-272,270-271` |
| F4 | Medium-Low | counter reads a response with no body cap | `tools/round62-c1-counter.py:74` |
| F5 | Medium | child env admits `LD_LIBRARY_PATH`/`LLAMA_ARG_THREADS`/`XDG_CACHE_HOME`; not recorded (regression vs lineage) | `tools/kama-completion-live.py:233-235` |
| F6 | Medium-Low | digest pin evaluated pre-exec only; loaded model/executable never re-derived | `tools/kama-completion-live.py:190-203,241-244` |
| F7 | Low | `hold.json` non-atomic symlink-following write; `release` unauthenticated; dir mode unenforced | `tools/kama-completion-live.py:220,398-399,403` |
| F8 | Low | `receipt['hold']` overwritten; witness record discarded | `tools/kama-completion-live.py:407,468` |
| F9 | Low | setup faults before the `try` escape as traceback + rc=1 (same code as "a check failed") | `tools/kama-completion-live.py:204-205,220,515` |
| F10 | Low | nonce binding has a fail-open empty default and a tautological clause | `tools/round62-c1-counter.py:186,202,203,369,171` |
| F11 | Low | `isinstance(x, int)` accepts JSON booleans in usage/timings grading | `tools/kama-completion-live.py:337-352`, `tools/round62-c1-counter.py:131-145` |
| F12 | Low | graded `listener_owned` is a constant; receipt carries no ownership evidence | `tools/kama-completion-live.py:263-276`, `tools/round62-c1-counter.py:159-160` |
| F13 | Info | six smaller items (fingerprint not bound, capped-prefix hashing, path disclosure, symlinked log/out, one-shot port gate, pdeathsig residual) | see below |

---

## F0 (High) — the committed counter cannot accept the committed tool's receipt

**File:** `tools/round62-c1-counter.py:165` (tip blob: `if 'hold' in (receipt.get('checks') or {}):`)
versus `tools/kama-completion-live.py:408-412` (`check('hold_released', released, …)`, recorded whenever
`--hold-dir` is in force — which the counter always passes, 233).

At the tip the tool records a check named `hold_released`; `grade()` looks for a check named `hold`,
never recomputes `hold_released`, and then compares the two key sets:

```python
if set(stored) != required:            # 181-182
    inconsistent.append('unexpected-checks')
```

so every hold-mode receipt — i.e. every receipt the counter itself produces — carries one
"unexpected" key and `score()` returns `met=False`.

Measured (`09-tip-grade-mismatch.txt`), feeding the clean receipt `01-clean-receipt.json` (17 checks,
`hold_released` among them) to both versions of the file:

```
tip 65d7cad (committed):                    met=False inconsistent=['unexpected-checks']
working tree (peer edit, not at tip):       met=True  inconsistent=[]
```

The tip blob's sha256 is `275610b5…`; the passing version is the working tree's `a3498308…`, which
differs by three uncommitted in-place edits, one of which is exactly
`if 'hold'` → `if 'hold_released'`.

**Impact:** the frozen measured state ("C1 met=True at tip 65d7cad") cannot be reproduced from the
committed instrument pair. Either the recorded measurement was taken with an uncommitted counter
(a provenance defect in the measurement), or the C1 predicate is unmet at the tip (a coverage
defect). Either way, no verifier starting from the tip bytes obtains `met=True`. This is the
strongest operability finding in this review and it is a correctness defect, not a matter of
degree: the counter's own key-set strictness turns a naming slip into a permanent false negative.

Note on the other measurements in this report: `01-clean-counter.out` (`met=True`) and
`03-proxy-counter-receipt.json` were produced by the **working tree** counter at 09:30, which
already carried that peer edit. Every finding below except this one is about code that is
byte-identical at the tip (the tool's sha256 `71ac4f2c…` matches the tip blob exactly; none of the
counter lines I cite fall in the three edited lines).

**Smallest remediation:** commit the `'hold'` → `'hold_released'` fix that is already in the
working tree, and add a counter selftest that runs `grade()` on a committed fixture receipt —
the strict key-set comparison is good design, but nothing currently exercises it against the
tool's real key names, which is why this shipped.

## F1 (High) — the graded POST is sent through whatever proxy the environment names

**File:** `tools/kama-completion-live.py:101` (`with urllib.request.urlopen(req, timeout=timeout)`,
inside `http_post`, 83-118).

`http_post` uses the module-level convenience `urllib.request.urlopen`, i.e. the default opener.
That opener honours `http_proxy`/`HTTP_PROXY`/`all_proxy` captured from the environment and follows
30x. The dependency the tool imports addresses this exact class with a purpose-built opener
(`tools/kama-llamacpp-live.py:971-980`: `_NoRedirect` + `ProxyHandler({})`), and the tool uses that
hardened opener for `/health` (143), `/v1/models` (286) and `/props` (294) — but **not** for the
request plane, which is the one surface C1 exists to grade (307-309, 383-384).

Measured, on this host, my own listener on `127.0.0.1:0`:

* `05-proxy-capture-probe.json` — with `http_proxy=http://127.0.0.1:<PP>` set before the process's
  first `urlopen`, `tool.http_post` hands the proxy the **absolute-form** request line
  `POST http://127.0.0.1:41183/v1/completions`; the proxy answers and the caller sees the proxy's
  body. `_live.http_get` under the same env goes `DIRECT` (no proxy) — the positive control.
* `02-proxy-tool-receipt.json` — the real tool, run with only `http_proxy` added to the
  environment, returns **`verdict=REQUEST_OK`, rc=0, zero failed checks**, with
  `completion`/`completion2`/`bad_request` bodies invented by the proxy, while the pinned child's
  own log (`02-proxy-tool-server.log`, 989 bytes) shows `model loaded` → `listening` →
  `cleaning up before exit` and **no completion request at all**.
* `03-proxy-counter-receipt.json` + the counter's stdout — `python3 tools/round62-c1-counter.py`
  under the same env prints `live_ok=1/1 … errors=0 met=True`, i.e. C1's whole live leg,
  including the counter's *own* outside contact (`post`, same `urlopen` at 73), is answered by
  the proxy. The proxy log shows the counter's nonce prompt
  (`r62-2a680fe4cb under the`) arriving at the proxy, not at the child.

**Exploit path (no privilege, no code change):** any environment that exports `http_proxy`, or a
runner that inherits one (corporate CI, a shell profile), silently converts both instruments into
a rubber stamp: the tool still spawns, hashes and tears down the real server — every cheap check
passes — and the only evidence that a completion was ever served is a body the proxy wrote. A
deliberate attacker who can influence the environment gets the same result plus control of the
prompt, and can replay the nonce it sees to satisfy the counter's witness.

**Impact:** the receipt cannot distinguish "the pinned server answered" from "an intermediary
answered", and carries no field that would let a verifier tell. This is fabricated provenance in
the sense of the seat rubric: not a crash, a false-positive instrument.

**Smallest remediation:** build the POST opener once as
`urllib.request.build_opener(urllib.request.ProxyHandler({}), _live._NoRedirect)` (the handler is
already imported and hardened) and use it in `http_post`; record `'http': 'direct'` in the receipt;
make the same substitution in `round62-c1-counter.py:post`. Two call sites, no interface change.

## F2 (Medium) — a 30x is followed and its body graded

**File:** `tools/kama-completion-live.py:101`; same defect in `tools/round62-c1-counter.py:73`.

Measured (`04-http-client-probe.json`): against a listener that answers `302 Location:
http://127.0.0.1:<CANARY>/sink`, `tool.http_post` returns the canary's `CANARY-BODY` with
`status=200` — urllib followed the redirect and (per urllib's 302 rule) re-issued it as `GET
/sink`. The counter's `post` does the same. The dependency's `http_get` on the same listener
surfaces `302` with an empty body and never touches the canary.

**Impact:** the prompt leaves loopback to whatever host a `Location:` names, and a foreign
document becomes the graded capture; it directly contradicts the module docstring's "The
registered consumers are never contacted; the tool serves on loopback only" (20-21). Precondition
is a listener that can answer the picked port — which F13's one-shot gate and a port squatter can
provide — so it compounds F1 rather than standing alone.

**Remediation:** the same `_NoRedirect` opener.

## F3 (Medium) — the counter's outside leg is steered by an unauthenticated file, and the hold dir is never cleared

**File:** `tools/round62-c1-counter.py:226` (`os.makedirs(hold, exist_ok=True)` — no cleanup),
`238-248` (poll `hold.json`, then immediately `post(port, …)`), `245-246` (`port`/`pid` taken from
the file), `261-272` (witness built from response + file), `270-271` (`server_sha256`/`model_sha256`
copied from the file, not measured).

The tool's own witness preparation clears stale state (`kama-llamacpp-live.py:290-325` removes
`ready.json`, `release`, tmp and probe files) but **not** `hold.json`; the tool unlinks `hold.json`
only on its normal path (403). The counter clears nothing.

Measured (`06-hold-poison.json`), with a planted `hold.json` naming my listener and `pid: 999999`,
and a stub tool that exits `1` immediately (`tool_receipt: false` — the counter never got a receipt):

* the counter generated its fresh nonce `r62-ee618d0b00` and **POSTed it to the port in the file**:
  `{"prompt": "r62-ee618d0b00 under the", …}` arrived at my listener;
* `witness.server_sha256`/`model_sha256` equal the pinned digests **because I wrote them into the
  file** (`witness_digests_equal_pins: true`), and the fingerprint/text/model came from my
  impostor body;
* `listener_owned` was `null` (so `met` stayed false here), but nothing in the code ordered the
  contact after an ownership check.

Measured (`07-leftover-hold-state.txt`): a real-tool run SIGKILLed by the counter's own 60 s wait
leaves `hold.json` **and** `ready.json` in the hold dir — exactly the stale state the next run in
that work dir will read.

**Impact:**
1. *Bound violation, not just noise*: the counter never calls `_live.refused_ports()` or consults
   `registry/endpoint-consumers.tsv` (`08-no-refused-port-check-in-counter.txt`), so a stale or
   planted `port` can direct the counter's request at a **registered consumer port** (8080,
   34113), which the standing rules forbid it to contact.
2. *Evidence provenance*: the "own live nonce-bound contact" can be answered by something that is
   not the served endpoint, and two of the witness's identity predicates are file echoes rather
   than measurements.
3. *Operability*: reusing a work dir after a killed run fails the next run. The counter breaks out
   of the poll loop on the stale file, writes `release` (277) **before** the tool's
   `prepare_witness_dir` (222) deletes it; the tool then holds for its full `--hold-timeout 90`
   while the counter waits only `proc.wait(timeout=60)` (279), kills the tool, and reports
   `live: no receipt produced` — with the tool's stderr discarded (235), so there is no clue.

**Smallest remediation:** delete/require-empty the hold dir before spawning; require
`hold.json.schema == 'kama-completion-hold/v1'` and a fresh `at`; reject `port` that is not in the
ephemeral range or is in `refused_ports()`; require `port_owned_by(pid, port) is True` *before*
the POST; hash `/proc/<pid>/exe` and the model file in the witness instead of copying digests;
wait at least the tool's hold timeout.

## F4 (Medium-Low) — the counter reads response bodies without a cap

**File:** `tools/round62-c1-counter.py:74` (`r.read()`), inside `post` (67-79).

Measured (`04-http-client-probe.json`): a listener that declares a 64 MiB body makes
`counter.post` return `bytes_read: 67108864`; the tool's `http_post` on the same listener returns
`bytes: 65536, truncated: True`. The tool caps at `BODY_CAP + 1` (103, 106) and flags truncation;
the counter has no cap and no truncation concept.

**Impact:** a misbehaving or hostile listener on a port that F3 can steer the counter to can
exhaust or stall the verifier — the tool's own discipline is not carried into the checker.

**Remediation:** mirror the tool: `read(BODY_CAP + 1)`, and treat truncation as a failed contact.

## F5 (Medium) — the child environment admits loader and behaviour channels, and the receipt does not record them

**File:** `tools/kama-completion-live.py:233-235`.

```python
env = {k: v for k, v in os.environ.items()
       if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH',
                'LLAMA_ARG_THREADS', 'XDG_CACHE_HOME')}
```

The lineage deliberately excludes `LD_LIBRARY_PATH` (`kama-llamacpp-live.py:126`,
`CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')`), sets it to the install directory
when the server runs from a sealed memfd (2195), and records the resulting key set as
`child_env_keys` (2200). The new tool does the opposite: it inherits the caller's
`LD_LIBRARY_PATH`, adds two more behaviour-affecting variables, and records none of them.

**Impact:** `server_digest` hashes the ELF (177-179) — not the shared libraries the dynamic loader
will bind. A caller-controlled (or merely stale) `LD_LIBRARY_PATH` changes what actually runs while
argv and both digests stay clean. `LLAMA_ARG_THREADS` is a real llama.cpp env override for `-t`, so
the effective thread count can differ from the `-t` recorded in `receipt['argv']`.
`XDG_CACHE_HOME` moves cache reads. None of this is a remote attack; it is a provenance hole in an
instrument whose claim leans on "digest-pinned" (docstring line 14) and on the receipt being a
complete record of inputs.

**Remediation:** override `LD_LIBRARY_PATH` to `os.path.dirname(server)` (or drop the key), drop
`LLAMA_ARG_*`, and record `child_env_keys` (and the effective `LD_LIBRARY_PATH`) in the receipt.

## F6 (Medium-Low) — the pin is checked before exec only, and the loaded identity is never re-derived

**File:** `tools/kama-completion-live.py:190-203` (hash, compare, return) then `241-244` (spawn).
The tool contains no use of `_live.model_mapping`, `_live.server_exe`, `install_tree` or
`code_mappings` (grep: no matches), although it imports that module precisely for these
primitives.

**Impact:** classic check-then-use. A local principal who can write the model or server path swaps
the file after `sha256_file` and before `Popen`/mmap; the receipt's `model_digest`/`server_digest`
stay true, and `receipt['model']['sha256']` becomes a statement about a file that is no longer the
one being served. Round 50 added exactly this defence to the lineage (`model_mapping` at 679,
`server_exe` at 731) after the same class of finding; the new sibling did not inherit it.

**Remediation:** after readiness, derive `model_mapping(proc.pid, model)` and
`server_exe(proc.pid)` and grade them as checks, recording the result.

## F7 (Low) — hold-dir write and release semantics

**File:** `tools/kama-completion-live.py:398-399` (`with open(os.path.join(hold,'hold.json'),'w')`,
then `json.dump`), `403` (unlink), `220` (`os.makedirs` with the ambient umask).

* The write is neither atomic nor symlink-safe, while the dependency's witness primitive is both
  (`kama-llamacpp-live.py:337-350`: `O_EXCL|O_NOFOLLOW`, per-run tmp name, `os.replace`). The tool
  even documents that hardening in its import graph but bypasses it for its own document.
* The directory is created `0777 & ~umask` (observed `drwxr-xr-x`); the code never checks that the
  caller-supplied `--hold-dir` is not group/world-writable.
* `hold_for_witness` treats `release` as a bare existence token (353, 363); its content is never
  authenticated, and `hold.json` carries no value the release must echo.

**Impact:** with a hold dir writable by another principal (a pre-existing `1777` directory passed
as `--hold-dir`, or any reused shared path), a planted `hold.json` symlink makes the tool write its
JSON over any file the user can write, and an empty `release` ends the graded window with no
observer — `hold_released` is then a claim about a file someone else created. Same-principal
preconditions keep this Low.

**Remediation:** use the dependency's `O_EXCL|O_NOFOLLOW` + `os.replace` pattern; reject a hold dir
with `st_mode & 0o077`; put a nonce in `hold.json` and require `release` to contain it.

## F8 (Low) — the receipt discards its own witness record

**File:** `tools/kama-completion-live.py:407` (`receipt['hold'] = w`) then `468`
(`receipt['hold'] = {'dir': args.hold_dir, 'released': released}`).

Measured (`01-clean-receipt.json`): `hold == {"dir": ".../clean/hold", "released": true}`. The
witness dict returned by `hold_for_witness` — `schema`, `port`, `pid`, `waited_ms`, `orphaned` —
is gone. The `hold` schema key also changes shape between hold and non-hold runs.

**Impact:** a verifier cannot bind the observer window to the pid/port the tool announced from the
receipt alone; it must trust side files (which is what the counter does, feeding F3). This is an
auditability defect, not an exploit.

**Remediation:** keep `w` and add `released` into it (one line), or record it under
`hold.witness`.

## F9 (Low) — setup faults escape as tracebacks and share the "a check failed" exit code

**File:** `tools/kama-completion-live.py:204-205` (`refused_ports()`, `pick_port()` — both raise
`_live.SetupError`), `220` (`os.makedirs` on an existing non-directory), `515`
(`receipt, rc = run(args)` with no handler).

These statements sit **before** the `try` at 232, outside the `except Exception` that produces a
`SETUP_ERROR` receipt (412-421). An unreadable `registry/endpoint-consumers.tsv`, a refused
`--port`, a hold path that is a file, or an exhausted port-pick loop all produce a traceback and
exit 1 — the code documented as "at least one evaluated check failed" (38-40) — and no `--out`
receipt is written.

**Impact:** setup breakage is indistinguishable from a graded failure to anything reading the exit
code, and leaves no receipt to explain it. On the operability axis this is the difference between
"the instrument rejected the tip" and "the instrument could not run".

**Remediation:** wrap the whole body of `run()` (or convert `_live.SetupError`/`OSError` to a
`SETUP_ERROR` receipt with rc 2).

## F10 (Low) — the nonce binding fails open

**File:** `tools/round62-c1-counter.py:186` (`NONCE = ''`), `369` (`NONCE = nonce or ''`),
`203` (`NONCE in (witness.get('sent_prompt') or '')`), `171` (`nonce_match`), and `202`
(`witness.get('nonce_prompt') == witness.get('sent_prompt')`).

Measured with the module default: `'' in 'no-nonce-anywhere'` is `True`, and `'' == NONCE` is
`True`, so both nonce predicates are vacuously satisfied when the counter's nonce is empty
(`nonce or ''`). Separately, `nonce_prompt` and `sent_prompt` are assigned from the same local
`nprompt` at 267-268, so 202 can never be false for a real witness; the fake-control family at
462-466 makes them differ, i.e. the control exercises a state the live path cannot produce.

**Impact:** a defence-in-depth hole and a control that does not test the live path. If any future
caller or exception path leaves `nonce` empty, the counter accepts a receipt with `nonce: ""` and
a witness whose prompt contains no nonce, with no error.

**Remediation:** refuse an empty nonce (`len(nonce) >= 8`, else an error entry); drop 202;
require `receipt['nonce']` to be a non-empty string in `grade`.

## F11 (Low) — JSON booleans satisfy the integer accounting checks

**File:** `tools/kama-completion-live.py:337-352`; identical predicates in
`tools/round62-c1-counter.py:131-145`.

`bool` is a subclass of `int` in Python, so `isinstance(True, int)` is true. Measured:
`{"completion_tokens": true, "prompt_tokens": true, "total_tokens": 2}` satisfies the whole
`completion_usage` predicate (`True + True == 2`), and `predicted_n: true` satisfies
`completion_timings`.

**Impact:** a server (or a proxy under F1) that emits booleans instead of counts grades true on
the two checks that are supposed to prove usage/timing accounting. Low because the pinned server
does not do this; relevant because the instrument's job is to grade bodies it did not write.

**Remediation:** `isinstance(x, int) and not isinstance(x, bool)` in both files.

## F12 (Low) — `listener_owned` is graded as a constant, with no evidence in the receipt

**File:** `tools/kama-completion-live.py:263-276`: the gate rejects a non-owned listener, then
records `check('listener_owned', True, …)` unconditionally. The counter re-derives it as
`bool(receipt['checks']['listener_owned']['passed'])` (`round62-c1-counter.py:159-160`).

**Impact:** the counter's "re-derives … from captured bytes" holds for the body checks but not for
this one — it reads the receipt's own assertion, and the receipt stores a bare boolean with no
inode, pid or fd link, so no third party can re-check ownership after the fact. Everything else
about the gate is correct (fail-closed on `None`, loopback-only inodes — 599-660).

**Remediation:** record `{'pid', 'inodes', 'fd_targets'}` in the receipt and recompute the
predicate from them in the counter.

## F13 (Info) — smaller items

* **Fingerprint is shape-checked, never bound.** `kama-completion-live.py:332` and
  `round62-c1-counter.py:127-130` accept any `^b\d+-[0-9a-f]{9,40}$`. My impostor's
  `b9999-cafebabefeed` passed; nothing ties it to the pinned server's build. Under F1 this is the
  field a proxy would fabricate. (Measured in `06-hold-poison.json`.)
* **`body_sha256` covers the capped prefix only.** `_cap` (120-127) hashes `result['body']`, which
  is already `raw[:BODY_CAP]`; `body_truncated` is recorded but never graded in either file. A
  >64 KiB response is graded on its first 64 KiB and the truncation is inert.
* **Absolute paths in the receipt.** `server.path`, `model.path`, `server_log`, `hold.dir`
  (192-193, 210, 246, 468) embed `/home/...`; the receipt is durable evidence under `.ufo/`.
* **`--out` and `server.log` follow symlinks.** `518` (`open(args.out,'w')`) and `239`
  (`open(log_path,'wb')`) would write through a symlink planted in a shared work dir. Caller
  scratch in practice; the hold dir is the one place the caller does not fully control.
* **The port gate is one-shot.** Ownership is checked at 263 and not again before the graded POSTs
  (307+) or after teardown (451). A squatter that binds after the child dies and before the POSTs
  receives the prompt and supplies the answer. This is A01C1PortRace's surface; recorded here so
  the two reviews agree rather than diverge. `pick_port` itself (546-580) documents the
  release/rebind race honestly.
* **pdeathsig is correct.** `_FORKED_PPID[0] = os.getpid()` is set before `Popen` (240) and
  compared inside the child (`kama-llamacpp-live.py:662-674`), closing the parent-died-before-
  `prctl` race; `hold_for_witness` additionally aborts when `os.getppid()` changes (359-360).
  Measured: the tool killed by the counter left no child process (`07-leftover-hold-state.txt`
  and a `/proc/*/cmdline` scan after the run). Residual: the `prctl` return value is ignored and no
  `prctl_ok` is recorded (the dependency records `'unknown'` honestly); there is no `setsid`, so a
  server that forked would escape the SIGTERM path (llama-server does not fork at this version).

---

## What holds (verified, so the fixes stay narrow)

* **argv safety** — the child command is a list, never a shell string; `os.path.realpath` on the
  server path plus a pinned sha256 before spawn; `--alias`, `--prompt` and `--port` are passed as
  discrete argv elements (or JSON), so no injection surface. `--port` is an `int` and is checked
  against `refused_ports()` and a live-connect probe (`pick_port`).
* **Env narrowing** — no `LD_PRELOAD`, no `PYTHONPATH`, no `TMPDIR` reaches the child; stdin is
  `DEVNULL`. F5 is about the three keys that are *too* permissive, not a missing whitelist.
* **Loopback discipline on the inventory plane** — `/health`, `/v1/models`, `/props` and every
  readiness poll go through the no-proxy/no-redirect opener.
* **Body caps** — `BODY_CAP + 1` read with an honest truncation flag on every tool capture.
* **Witness preparation** — stale `ready.json`/`release` removed and writability proven before the
  server starts (`kama-llamacpp-live.py:290-325`).
* **Ownership predicates fail closed** — `port_owned_by` returns `None` when it cannot decide and
  the tool treats that as not-owned; only loopback-bound LISTEN inodes count.
* **Teardown** — SIGTERM, then SIGKILL only on the child this process spawned; port closure is
  re-measured rather than assumed.

## Reproduction

Scratch root `S=/fast/scratch/hyaku/kama-r62/w/N01CompletionSecurity` (deleted after the evidence
below was copied out). Every run used `TMPDIR=$S` and loopback ports I bound myself; no registered
consumer port was contacted; no process I did not spawn was signalled.

```
# normal path (working-tree counter; the tip blob fails this, see F0)
TMPDIR=$S python3 tools/round62-c1-counter.py --repo <lane> --tip 65d7cad --work $S/clean
#   -> tool_present=1 live_ok=1/1 … errors=0 met=True   (01)

# F1/F2: proxy env + redirect, component and end-to-end
TMPDIR=$S python3 probe_http.py     > 04-http-client-probe.json
TMPDIR=$S python3 probe_proxy.py    > 05-proxy-capture-probe.json
TMPDIR=$S python3 probe_proxy_forgery.py   # tool -> REQUEST_OK, child serves nothing (02)
TMPDIR=$S python3 run_counter_proxy.py     # counter -> met=True, proxy answers   (03)

# F3: planted hold.json, stub tool that never produces a receipt
TMPDIR=$S python3 reproduce_poison.py      # nonce POSTed to the planted port     (06)
```

Evidence in `.ufo/waves/round-62/w1/out/N01CompletionSecurity/evidence/`:
`01-clean-counter.out`, `01-clean-receipt.json`, `02-proxy-tool-receipt.json`,
`02-proxy-tool-server.log`, `03-proxy-counter-receipt.json`, `03-proxy-counter-server.log`,
`04-http-client-probe.json`, `05-proxy-capture-probe.json`, `06-hold-poison.json`,
`07-leftover-hold-state.txt`, `08-no-refused-port-check-in-counter.txt`,
`09-tip-grade-mismatch.txt`.

Note on `04`: its `*_with_proxy_env` sub-test sets the environment *after* the process's first
`urlopen`, and urllib caches its default opener at that first call, so that sub-test shows a
direct route by construction and is **not** evidence against F1. `05` sets the environment before
the first call and is the decisive measurement; `04`'s redirect and flood sub-tests are unaffected
by that ordering.

## Tally

```
n01_completion_security files=2(tools/kama-completion-live.py,tools/round62-c1-counter.py) tip=65d7cad findings=14 high=2 medium=3 medium_low=2 low=6 info=1 lane_edits=0 read_only=1
```
