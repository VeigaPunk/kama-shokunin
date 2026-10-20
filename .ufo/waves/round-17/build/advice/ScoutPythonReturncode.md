VERDICT: confirm — docs.python.org/3 `Popen.returncode` states `-N` = terminated by signal N (POSIX only); `wait(timeout)` raises `TimeoutExpired`; banner is Python 3.15.0, local runtime docs is 3.14.8.

# Scout — Python `Popen.returncode` / `wait(timeout)` docs (candidate SOURCES row, tier A)

Question: exact negative-returncode sentence, `wait(timeout)` TimeoutExpired semantics, and the page's Python version banner.
Status: read-only. No installs or upgrades performed (no tool was needed beyond python3 3.14.8, curl, grep).
Access: 2026-10-20; fetched with `curl -sSL` to `/tmp/py-subprocess.html` and `/tmp/py-subprocess-314.html`.

## 1. Version banner — the one substantive trap

- `https://docs.python.org/3/library/subprocess.html` (fetched 2026-10-20): `<title>subprocess — Subprocess management — Python 3.15.0 documentation</title>`, footer "Last updated on Oct 20, 2026 (13:43 UTC)." Snapshot sha256 `f6d48eb534364a97de5767657917a6f35621651e9b9d88ba471807939bda9b08`.
- `https://docs.python.org/3.14/library/subprocess.html`: `<title>... Python 3.14.8 documentation</title>`, footer "Last updated on Oct 20, 2026 (13:02 UTC)." Snapshot sha256 `c5bcfd4f8946c5f82dacb7ed766c11051531df6015df6c4c7783e5590c1cf204`.
- Local interpreter: `python3 -VV` → `Python 3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]`; stdlib at `/usr/lib/python3.14/subprocess.py`.

`/3/` is NOT the runtime version. Quote (`/3/`): "Linux >= 5.3 uses os.pidfd_open() + select.poll()" — an event-driven `wait()` note. `/3.14/`: "then (on POSIX) the function is implemented using a busy loop" — matching the installed implementation. The `Popen.returncode` entry and the core `Popen.wait` sentences are byte-identical across both pages; only `wait()`'s implementation note differs. **Recommend the SOURCES row cite `/3.14/`**, i.e. the docs for the interpreter that actually runs the harness. [INFERENCE] citing `/3/` would silently drift with every CPython release and, on the `wait()` note, would describe behaviour the 3.14.8 runtime does not have.

## 2. `Popen.returncode` — exact text (identical on both pages)

URL: https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode

- "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words)
- "returncode is set by a call to the poll(), wait(), or communicate() methods" (13)
- "A None value indicates that the process hadn't yet terminated at the time of the last method call." (18)
- "When shell=True, the return code reflects the exit status of the shell itself" (13) — present in 3.14.8 and 3.15.0 alike (irrelevant here: the harness spawns argv lists, no shell).

Corroboration in the installed stdlib (same claim, machine-readable):
- `/usr/lib/python3.14/subprocess.py:1996-2003` — POSIX active `_handle_exitstatus`: `self.returncode = _del_safe.waitstatus_to_exitcode(sts)` (line 2003), with `-WSTOPSIG` on the stopped branch (1999).
- `os.waitstatus_to_exitcode.__doc__` (3.14.8): "If WIFSIGNALED(status) is true, return -WTERMSIG(status)." Docs page https://docs.python.org/3.14/library/os.html#os.waitstatus_to_exitcode: "If the process was terminated by a signal (if WIFSIGNALED(status) is true), return -signum" (17 words).

So `-9` in a receipt is SIGKILL by the OS mapping, and `0` on the same scale means `WIFEXITED` with `WEXITSTATUS == 0`. That is exactly the authority a fail-capable `teardown_exited` / "no SIGKILL" predicate needs.

## 3. `Popen.wait(timeout=None)` — exact text

URL: https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.wait

- "Set and return returncode attribute." (6)
- "If the process does not terminate after timeout seconds, raise a TimeoutExpired exception." (14)
- "It is safe to catch this exception and retry the wait." (11)
- "This will deadlock when using stdout=PIPE or stderr=PIPE" (10) — not the harness's case (server stdout goes to a temp log file, `kama-llamacpp-live.py:902`, teardown `:656-683`).

`exception subprocess.TimeoutExpired` (`#subprocess.TimeoutExpired`): "Subclass of SubprocessError, raised when a timeout expires while waiting for a child process."; attributes `cmd` ("Command that was used to spawn the child process."), `timeout` ("Timeout in seconds."), `output`/`stdout`/`stderr`.

Installed implementation, for the receipt's `term_wait_ms` reading:
- `/usr/lib/python3.14/subprocess.py:1274-1275` — `def wait(self, timeout=None):` docstring "Wait for child process to terminate; returns self.returncode."
- `/usr/lib/python3.14/subprocess.py:2052-2087` — active POSIX `_wait` (confirmed via `inspect.getsourcelines(subprocess.Popen._wait)` → 2052): busy loop, `raise TimeoutExpired(self.args, timeout)` at 2076, sleeps `min(delay*2, remaining, .05)` at 2077-2078.
- Round-16 receipt `.ufo/waves/round-16/live/receipt.json` `teardown`: `{"returncode": 0, "sigkill_sent": false, "sigterm_sent": true, "term_wait_ms": 3}` — consistent with `wait()` returning a real child exit (not a poll artefact). [INFERENCE] a 3 ms reading is plausible under the ≤50 ms busy-loop ceiling; it is an observation, not a mechanism fingerprint, so no check should grade `term_wait_ms` magnitude against a sleep interval.

## 4. Consequences for C2 predicates (advice only; not measurements)

- `teardown_exited` graded as `returncode == 0 and sigterm_sent and not sigkill_sent` is fully sourced by §2+§3; grading `returncode is not None` alone is what the docs permit the current tool to get away with (any of `0`, `-9`, `-15` satisfies it).
- Because `returncode` only updates on `poll()`/`wait()`/`communicate()`, a predicate that reads `proc.returncode` must have run one of those first. `kama-llamacpp-live.py:663` (`if proc.returncode is None:  # F5: killpg only while child is alive`) reads a value whose freshness is only as of the last call — docs-supported, and harmless (a stale `None` only means an extra SIGTERM attempt), but it must not be cited as proof of liveness.
- `Popen.wait` *returns* the returncode ("Set and return"), so a v2 check may assert the returned integer equals the recorded `returncode`; the docs make that identity normative.
- No doc statement exists that `returncode == 0` proves the child chose to exit; it only proves normal exit with status 0. "Documented graceful exit" still needs the llama.cpp shutdown row, not this one.

## 5. Candidate SOURCES row (next free id observed: S042; S041 is the last row)

Registry head verified at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:53`; no S042 exists yet. If a sibling claims S042 first, take the next free id — the content is what matters.

```
| S042 | Python `subprocess` docs (3.14 branch) — https://docs.python.org/3.14/library/subprocess.html | docs | A | CPython 3.14 POSIX child exit-status and timeout semantics used by kama's live harness teardown predicates; not llama.cpp behaviour | §`Popen.returncode` (`#subprocess.Popen.returncode`) and §`Popen.wait(timeout=None)` (`#subprocess.Popen.wait`), page banner "Python 3.14.8 documentation", last updated 2026-10-20 (13:02 UTC); signal mapping corroborated by `os.waitstatus_to_exitcode` (`https://docs.python.org/3.14/library/os.html#os.waitstatus_to_exitcode`) | A negative `returncode -N` means termination by signal N on POSIX; `wait(timeout)` raises `TimeoutExpired` if the child does not terminate within `timeout` and is safe to catch and retry; `returncode` is refreshed only by `poll`/`wait`/`communicate`; excluded: 3.15's event-driven wait note, which does not describe the 3.14.8 runtime. | mined | 2026-10-20 | on-release | tools/kama-llamacpp-live.py, tests/llamacpp-live/check-receipt.py |
```

Caveats for the integrator:
- Do not pin the HTML sha256 as a contract: the page carries a version switcher and a build timestamp, so the digest changes on any docs rebuild. Cite banner + section text; keep the digest only as the snapshot record of this read.
- `kind: docs`, `tier: A` matches the precedent of S005/S035 (`docs`, `A`) for first-party documentation, and the row is `mined` (opened, read, quoted now).
- Keep `/3.14/` in the URL. If the lane later runs a different interpreter, re-check the banner rather than editing the quote.
- The row deliberately excludes llama.cpp shutdown semantics: `SIGTERM`→`returncode 0` says nothing about llama.cpp's documented graceful path, which C2 must source elsewhere (S035-S037 neighbourhood, plus a signal/shutdown code read).

## 6. Remaining unknowns

- Whether Python 3.15's stdlib actually implements the pidfd/kqueue `wait()` note. Only 3.14.8 is installed; the 3.15 claim is docs-only and unverified here. [INFERENCE] irrelevant to the lane while the runtime is 3.14.8, but it is the reason to pin `/3.14/`.
- Whether `docs.python.org/3.14/` retargets to 3.14.9 on a point release (it will). The `returncode`/`wait` prose has been stable across 3.14.8 and 3.15.0 as read today, so the quote ages well, but the banner cell must be re-read on the row's `recheck`.
