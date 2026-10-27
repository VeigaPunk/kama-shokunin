# V2Review — round-51 code review: live/replay changes (57a2e25..138af25)

Verdict: **no blocking defect** in the round-51 `tools/kama-live-replay.py` + `tools/kama-llamacpp-live.py` diff — one LOW (docstring-vs-behavior in `server_exe()`), three INFO/residual; both selftests pass at the build commit and `tests/llamacpp-live/check-receipt.py` correctly does **not** need to know `server_exe`.

Reviewed: `git -C kama-shokunin diff 57a2e25bf702b03aa61f9265e968cf68058ecb82 138af25b963450b6520794995605fa7dbbcd87e0 -- tools/kama-live-replay.py tools/kama-llamacpp-live.py` (copy: out/V2Review/diff.patch; 146 lines; only commit touching these files in range: b6bed925). All file:line below are at 138af25b.

## Findings

### LOW-1 — `server_exe()`: fstat/read OSError contradicts the docstring's "any other outcome is opened: False"
- `tools/kama-llamacpp-live.py:744-758`: the second `try` (after readlink/open) has only `finally: os.close(fd)`, no `except OSError`. An `os.fstat`/`os.read` failure (e.g. EIO) propagates out of `server_exe()`, while the docstring (`:736`) says "any other outcome is `opened: False` with its reason".
- Consequence today (not silent): `main()` catches `BaseException` → `_record_internal` (`:2059-2060`), so `receipt['server_exe']` stays `None` → the replay flags `server-exe:absent` (replay.py:363) and the tool records an unrelated `internal_fault`. Loud, but the promised `opened: False` row is lost.
- Proposed fix (unified diff): out/V2Review/server-exe-read-failure-fix.diff — wrap the body in `except OSError → {'opened': False, 'reason': 'exe-read-failed:…'}`; every existing early return and the `finally` close stay intact. Counters are frozen; report only, no in-place edit.

### INFO-1 — replay's `os.stat(server)` eager failure degrades to "could-not-run", no `own_server` row
- `tools/kama-live-replay.py:359`: `se, own = rr.get("server_exe"), os.stat(server)` is evaluated before any isinstance/leg checks. If `server` vanished between the member verification (`:302-307`, realpath + isfile + digest Refused paths) and the post-run stat, the outer `except (OSError, …)` (`:380-384`) turns the run into `refused=could-not-run:FileNotFoundError…` exit 2 — a would-be mismatch becomes "could not run", and `res["own_server"]` is never recorded (the C1 counter reads `own_server` from the result JSON).
- Honest semantics (only external interference explains a vanished member the replay itself extracted and hashed), and the failure is loud. Optional hardening: stat inside its own try and append `own-server:<reason>` as a mismatch instead of refusing. Not required.

### INFO-2 — `--compare` evaluates neither the r50 `model_mapping` leg nor the r51 `server_exe` leg (pre-existing shape)
- `compare()` (`replay.py:245-278`) checks schema/outcome/shas/checks/v5-provenance/projection only; `main --compare` (`:601-620`) adds `provenance()`. The pre-existing docstring line "--compare validates both receipts' provenance like a replay would" (`:54`, context in the diff, unchanged by b6bed925) overstates: a receipt pair whose rerun image was a decoy file compares `match=True` under `--compare` while a full replay fails `server-exe:not-own-member`. The dev/inode leg is inherently per-work-dir (two extractions can never share an inode), so it cannot be added naively; `opened` and `server_exe.sha256` vs `server.sha256` could be. Same omission already true for r50's `model_mapping` — not a regression of this diff; enforcement lives in the C1 counter, not `--compare`.

### INFO-3 (residual, fails safe) — readlink→open TOCTOU and pid reuse in `server_exe()`
- `live.py:739-743`: `os.readlink` then `os.open` on `/proc/<pid>/exe`. Between the two calls the child can exit → OSError → `exe-unreadable:<strerror>` (replay flags `server-exe:exe-unreadable:…`); if the pid were reused in the window, `path` (old process) and the fd bytes (new process) could disagree — but sha/dev/inode all come from the opened fd, so a wrong image still fails the replay's digest and own-member legs. `path` is informational only ("(deleted)" suffix, man-pages 6.19). `_child_running(proc)` is re-checked immediately before (`:2039`). No wrong-pass path found.

### INFO-4 — result document gains `own_server` without a schema bump
- `res` (`replay.py:283`, `SCHEMA = "kama-live-replay/v1"`) gains the `own_server` key (`:361`). Additive, and the preregistered consumer names it ("the replay's result JSON names the same file under `own_server`", C1 docstring); no strict consumer found. Note only.

## Focus-area answers (all verified, no defect)

- **server_exe()** (`live.py:730-762`): O_RDONLY on `/proc/<pid>/exe` is right per the frozen source — man7.org proc_pid_exe(5), man-pages 6.19 (fetched 2026-10-27): "attempting to open it will open the executable", `' (deleted)'` suffix on unlinked path, ptrace `PTRACE_MODE_READ_FSCREDS` governs dereference (EACCES/EPERM → `exe-unreadable:…`, `:742-743`). `import stat` present (`live.py:78`). fstat → regular-file check → size-bounded 1 MiB read loop hashing exactly `st.st_size` bytes; early EOF → `exe-shrank-while-hashed`; growth beyond the snapshot is never read (digest = prefix at fstat time — fails safe downstream). fd closed in `finally` on every path. Non-Linux: readlink raises OSError → `opened: False`. Except LOW-1, matches its docstring.
- **Receipt skeleton key**: `'server_exe': None` in the skeleton (`live.py:1798`); both `_child_running` branches assign it (`:2041` real, `:2044` `server-not-running`) — placed at `:2045` **before** the witness hold, so the image is recorded before the counter's kill-during-hold teardown leg can remove the child. Mirrors the r50 `model_mapping` precedent exactly.
- **Own-member check placement** (`replay.py:359-368`): after `compare()` (`:347`) and the `model_mapping` leg (`:349-354`), before `live-exit` (`:369`) — no early return between, so legs accumulate. Compares against `want_srv` (`:306`), which is a verified str by then (member digest Refused otherwise, `:307-308`); string-normalized `'%02x:%02x'` dev and `str(inode)` on both sides; `own_server` recorded even on mismatch.
- **os.stat(server) failure modes**: see INFO-1 (→ refused exit 2, not a crash).
- **Selftest fakes mirror the real tool**: fake `x=os.stat(s)` stats the same `--server` path a real child execs, so dev/inode equal what `fstat(/proc/<pid>/exe)` shows for that exec (`live.py` opens the link, kernel gives the underlying file). `noexe-live` (key renamed → `server-exe:absent`), `copy-live` (shutil.copy → same sha `h(s)`, different inode → isolates `not-own-member`), `badsha-live` (digest `'4'*64` → isolates the sha leg before the inode elif). All three pass.
- **Docstrings**: replay module paragraph (`replay.py:54-59`) accurately describes opened/`own_server`/mismatch strings; `server_exe` docstring quote verified verbatim against man-pages 6.19.

## check-receipt.py — does NOT need to know server_exe (verified, not a gap)
- No top-level key whitelist (grep for key-set rejections: none; `unexpected check id` governs only `checks[]`, `check-receipt.py:1040-1043`).
- Selftest at the build commit: `python3 tests/llamacpp-live/check-receipt.py --selftest` → exit **0**, "16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected" (out/V2Review/check-receipt-selftest.out).
- Tolerance probe: round-48 `receipt-1.json` VALID exit 0; with synthesized `server_exe` + `model_mapping` added → VALID exit 0 (out/V2Review/check-receipt-server_exe-tolerance.out).
- Convention: last change to check-receipt.py is r48 (c4b2175d) — r50 already added `model_mapping` to the producer without touching it. Design intent is explicit in both tools: "recorded the same way, never a check id" (`live.py:2038`); the running-image legs are enforced by the replay counter and the C1 counter, not by the receipt gate. Extending check-receipt now would deviate from that precedent without adding enforcement the counters don't already have.

## Commands and exit codes (scratch clone: `git clone --shared … $S/lane`, then `git -C $S/lane checkout 138af25b…`; toplevel asserted)
- `git … diff 57a2e25 138af25 -- tools/kama-live-replay.py tools/kama-llamacpp-live.py` → 146-line patch.
- `python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S/st` → exit **0**, `KLR_SELFTEST pass=26 fail=0`, including `pass server-exe-absent`, `pass server-exe-not-own-member`, `pass server-exe-digest-differs` (out/V2Review/replay-selftest.out).
- `python3 $S/lane/tests/llamacpp-live/check-receipt.py --selftest` → exit **0** (above).
- Quote check: `read https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html` (local `man 5 proc` predates the exe section).
- No llama-server started by this seat (selftests are offline, file:// fakes); no pacman/tool installs used; no installs to record.

## Residual risk and verification gaps
- LOW-1's trigger (post-open EIO) was reasoned, not reproduced on live /proc — the diff driver in the fix note is the proposed demonstration.
- The real `server_exe()` ↔ `/proc/<pid>/exe` path on a genuine llama-server run is exercised by the C1 counter's build receipts (met=True), which this seat did not re-run (out of seat scope; ~75 MB × 3 replays + live servers). The offline selftest covers the replay-side logic with fakes only.
- `--compare` non-enforcement of the r50/r51 legs is reported as INFO-2; changing it is a lane decision, not a b6bed925 regression.

## Files written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review/diff.patch
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review/check-receipt-selftest.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review/replay-selftest.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review/check-receipt-server_exe-tolerance.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V2Review/server-exe-read-failure-fix.diff
