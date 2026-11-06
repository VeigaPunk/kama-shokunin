# SN01 Fixture safety — kama round 88, w1

## Scope
Security/safety review of the two round-88 lane tools at `f77d2ae9f2797a19e7548989fb9e64d8f9411d3f`
(`tools/round88-router-cells.py`, `tools/fetch-pinned-model.py`): loopback bind + child teardown
(process group, exceptions, KeyboardInterrupt, timeouts, signals), scratch removal on every path,
TMPDIR/`--work` honouring, fetcher integrity (digest→rename window, `.part`/dest symlinks, leftovers,
redirects, never overwriting a present wrong-digest file). Read-only in the lane; no frozen predicate
changed. Tool bytes reviewed: counter sha256 `576a1b374c9150dbd3f58acf26a69c794bd5ac724911aba29f62291ed3435e21`,
fetcher sha256 `1decfc4c1db3affd740d3df426cf3a1b8e0bda665983e8bc87eb831936953852`, probe at tip
`bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf` (= worktree probe, verified).

## Commands and outputs (exit codes)
1. `python3 counter.py --repo . --rev f77d2ae… --work $S/work` → **exit 0**,
   `ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=rev probe_sha256=bd7a6a22…` (receipt
   `counter-run.out`). Post-run `ss -ltnp | grep llama`: only the operator's `127.0.0.1:1234` pid 1505.
   Work dir empty → scratch removed. **Corroborates the C1 live+canned green.**
2. `TMPDIR=$S/tmpd python3 counter.py --repo . --rev f77d2ae…` (no `--work`) → **exit 0**, `$S/tmpd`
   empty afterwards, `ls -d /tmp/router-cells-*` → 0. TMPDIR honoured; no hardcoded `/tmp` in either tool
   (`grep -n /tmp` → rc 1 in both).
3. `--rev deadbeef…` → **exit 2** `could-not-evaluate: git show … failed`, scratch empty.
4. `--probe-file` harness with `signal.alarm` → KeyboardInterrupt inside the guarded region:
   `A raised: KeyboardInterrupt`, `A leftover llama-server: ''`. Teardown works for KeyboardInterrupt.
5. Probe sleeping past the 60 s `run_probe` timeout → `raised after 60s: TimeoutExpired`,
   `leftover llama-server: ''` (`timeout-path.out`). Teardown works for timeouts.
6. `sigterm-demo.sh` (real `live_cells`, real pinned child): child `LISTEN 127.0.0.1:43969`;
   after `kill -TERM <parent>` → `parent alive: 0`, `child alive: 1`, still `LISTEN 127.0.0.1:43969`,
   PPID 1487 (`sigterm-demo.out`). **Orphan.**
7. `fake_router.py` (squatter pre-bound on the port `free_port()` returns) → `live_cells` rows
   `L01/L02/L03` all `expected==observed`, `SQUAT any llama-server started: none`; the real child's log
   reads `couldn't bind HTTP server socket … exiting due to HTTP server error` (`fetch-g.out`/scratch log).
8. Port occupied + `free_port` forced to it → `CannotEvaluate after 30.8s: router never reported status
   unloaded`, no leftover child (`port-collision.out`). Fail-closed but 30 s wasted.
9. Non-executable server copy **with the correct sha256** → `raised: PermissionError`, i.e. an uncaught
   exception escapes `live_cells`, not `CannotEvaluate`.
10. `fetch_tests.py` F1–F9 + G1–G4 + truncated transfer (`fetch-tests.out`, `fetch-g.out`, `fetch-g2b.out`):
    F1 present-correct → exit 0, mtime unchanged. F2 present-wrong → exit 1, byte-identical, no `.part`.
    F3 bad download → exit 1, no dest, no `.part`. F5 302 to a **different host** (`127.0.0.2`) → exit 0
    fetched. F6 SIGINT mid-download → `.part` (262 144 B) left behind + traceback. F7 dest symlink to
    wrong content → exit 1, target untouched. F9 missing parent dir → created, fetched. Truncated
    `Content-Length` transfer → exit 1, digest mismatch, no leftovers.
11. `git show "--output=…"` → writes a file (6771 B), but the counter's `rev:path` form yields
    `fatal: could not open '…GITOUT2:tools/…' for writing` → **no** write; `--rev --output=…` is rejected
    by argparse. Rev option-injection: not exploitable. Cleared.

## Findings
- **DEFECT SN01-1 — fetcher follows a `.part` symlink: arbitrary file clobber.**
  `fetch.py:51` `part.open("wb")`; `part = dest + ".part"` (`:49`). Evidence `fetch-tests.out` F4: victim
  `victim.txt` (17 B, `ORIGINAL CONTENT\n`) became 1 280 B of download payload; tool printed
  `downloaded digest … != pin … (discarded)`, exit 1, and `part.unlink()` removed the *symlink*, not the
  damage. Exploit: `--dest /tmp/model.gguf` (shared dir) with attacker-created
  `/tmp/model.gguf.part -> ~/.bashrc`; fetch runs as the victim user and truncates `~/.bashrc`. Default
  dest (`~/.cache/…`, `fetch.py:27`) is safe; any `--dest` in a shared dir is not.
  Remediation: `os.open(part, O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o644)`, refuse symlink `dest`/`part`.
- **DEFECT SN01-2 — digest→rename TOCTOU: the installed object is never re-verified.**
  `fetch.py:58` `digest(part)` … `:63` `os.replace(part, a.dest)`. Evidence `fetch-g2b.out` (instrumented
  *copy* widening the real window): exit 0 and `sha256=270cba1b…` printed while the installed file hashes
  `fd9aa312…` = the attacker's bytes — a false green in the tool's own receipt. `fetch-g.out` G1 proves the
  same without instrumentation: after a `.part`-symlink install `dest` *is* a symlink, so editing its
  target silently changes `dest`'s digest while the printed line still claims the pin.
  Remediation: hash through the fd, rename by fd/path with `renameat` + re-digest `dest` afterwards
  (or compare `st_dev/st_ino` of the fd with the installed path).
- **DEFECT SN01-3 — counter can grade a squatter: the "independent oracle" shares the socket with the probe.**
  `counter.py:91-95` `free_port()` closes the socket, `:194` `Popen` binds it later; `child.poll()` is never
  checked. Evidence item 7: a local fake on the returned port yields `L01/L02/L03` expected==observed with
  **no llama-server running** (real child died with `couldn't bind`). A receipt claiming `live=3` all-ok can
  therefore be produced with zero llama.cpp. Remediation: require the child's own `server is listening` log
  line and `child.poll() is None` before every cell; treat a bind failure as could-not-evaluate and retry on
  a fresh port.
- **DEFECT SN01-4 — SIGTERM/SIGKILL leaks the router child and its scratch.**
  `counter.py:196` `start_new_session=True`, teardown only in the `finally` at `:213-221`; no SIGTERM
  handler. Evidence item 6: parent dead, child alive and still `LISTEN 127.0.0.1:43969` (PPID reparented).
  Any `timeout`-driven or CI-cancelled run leaves an orphan router holding a loopback port plus a
  fully-populated model copy in a scratch tree that is never removed.
  Remediation: `SIGTERM`/`SIGINT` handler doing `killpg(..., 15)` then exit 143, and
  `prctl(PR_SET_PDEATHSIG, SIGTERM)` (or `atexit`) on the child.
- **DEFECT SN01-5 — environment faults surface as exit 1 (mismatches) instead of exit 2 (could-not-evaluate).**
  `counter.py:194` (`Popen`) sits outside the guarded block; `:261` catches only `CannotEvaluate`.
  Evidence item 9 (`PermissionError`) and item 5 (`TimeoutExpired` raised out of `main`'s handler set):
  traceback + exit 1, leaving `router.log`/`models` behind (cleaned only by `:276`). A receipt with exit 1
  reads as "the probe disagreed", which is a different fact from "the fixture was broken".
  Remediation: `except OSError as e: raise CannotEvaluate(...)` around `Popen`, and catch `TimeoutExpired`
  in `main`.
- **NOTE SN01-6 — fetcher does not pin the host.** Item 10/F5: a 302 to a *different* host is followed and
  the fetch succeeds. The digest is the only integrity anchor (so content is still gated), but the
  docstring's "pinned upstream file" provenance is not enforced, and `--url` is unvalidated (SSRF if ever
  fed untrusted input). Remediation: compare `r.geturl()`'s host to `huggingface.co`, or drop `--url`.
- **NOTE SN01-7 — SIGINT leaves `<dest>.part`.** Item 10/F6: 262 144 B `.part` survived the signal, plus a
  traceback. Next run truncates it, so no functional harm; contradicts the documented exit-2/FETCH_PINNED*
  contract. Remediation: `try/finally` unlinking `part` unless the replace succeeded.
- **NOTE SN01-8 — fetcher error paths raise tracebacks and exit 1.** `.part` a directory
  (`IsADirectoryError` raised *inside* the `except OSError` at `fetch.py:57`), `dest` a directory,
  `dest` unreadable (`fetch-g.out` G3a/G3b/G4): no `FETCH_PINNED*` line at all. Fail-closed, cosmetic.
- **NOTE SN01-9 — port collision costs 30.8 s then exit 2.** `port-collision.out`; `wait_status` polls the
  full 30 s. Fail-closed, but a flake turns a measured receipt into could-not-evaluate.
- **NOTE SN01-10 — model TOCTOU in the counter.** `counter.py:187-191` digests `MODEL` then
  `shutil.copyfile`s it; a swap in between loads unverified bytes into the child. Requires write access to
  the cache dir (same class as SN01-2).

Positive confirmations (each exercised, not inferred): child binds **loopback only**
(`LISTEN 127.0.0.1:43969`, argv `--host 127.0.0.1`; stub servers bind `127.0.0.1` explicitly);
teardown is correct on the normal path, on `CannotEvaluate` (bind failure), on KeyboardInterrupt and on the
probe timeout; scratch is removed on every exit path I could drive (items 1-3); TMPDIR honoured; the fetcher
refuses a present wrong-digest file (F2) and leaves nothing behind on a bad or truncated download (F3,
item 10); `127.0.0.1:1234` was never contacted (only read in `ss`; operator pid 1505 unchanged throughout).

## Deliverables
`.ufo/waves/round-88/w1/out/SN01FixtureSafety/`: `counter-run.out`, `counter-tmpdir.out`,
`port-collision.out`, `timeout-path.out`, `sigterm-demo.out` (+`sigterm-demo.sh`, `sigterm_child.py`),
`fetch-tests.out`, `fetch-g.out`, `fetch-g2b.out`, `fetch_tests.py`, `fake_router.py`, and the reviewed
bytes `counter.py`, `fetch.py`. No tool installed, nothing upgraded (no need).

VERDICT: falsified — the C1 17/17 predicate reproduces green at tip, but the tool pair is not safe as
asserted: SIGTERM/SIGKILL leaks the router child, a loopback squatter can fake all 3 live cells, and the
fetcher follows a `.part` symlink (arbitrary file clobber) and installs an unverified object after its own
digest check.
