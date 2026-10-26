# V1Live — code review of the round-49 change to `tools/kama-llamacpp-live.py`

Verdict: **No correctness-blocking defect found; two robustness findings (TOCTOU in `verify_archive_member`, stale-pid announce in `hold_for_witness`) with proposed fixes, plus selftest-coverage gaps.** The reviewed change is coherent with the frozen C1 counter contract (`tools/round49-replay-witness-audit.py`) and the frozen preregistration; all bounds verified by fixtures behave as documented on python 3.14.8.

Reviewed object: `git diff 438127bc01ff3b99f98468549d58046f932490ef 74558c71c38ceaeace15fd4cf8aa9d84977584b1 -- tools/kama-llamacpp-live.py` (229 diff lines; +151/-30). All fixtures ran against the lane tip file loaded unmodified (importlib) from a `git clone --shared` of the lane. No tools were installed; nothing was mutated in the lane, fleet repo, or PATH.

Key line references are to the tip file `tools/kama-llamacpp-live.py` at `74558c71c38ceaeace15fd4cf8aa9d84977584b1`.

---

## Findings

### F1 (medium) — `verify_archive_member()`: S_ISREG + size cap are checked on `os.stat(path)`, then a second, non-atomic `open(path)` happens; the guards describe the pre-swap object

- `tools/kama-llamacpp-live.py:227-239` — `st = os.stat(archive)` (228), `S_ISREG` (231), `st.st_size > ARCHIVE_MAX_BYTES` (233), then separately `arc = open(archive, 'rb')` (236). The stat and the open are two independent path lookups.
- Demonstrated hazard (fixture `evidence/fixture_toctou.py`, output `evidence/fixture_toctou.out`):
  1. stat on a regular file passes (`S_ISREG True size 13`); the path is then replaced by a FIFO; `open(path, O_RDONLY)` with no writer **blocks > 2 s** (`open(path) BLOCKED >2s after stat passed on the same path (TOCTOU window)`). A swapped-in FIFO therefore hangs the harness indefinitely at record time — exactly the failure the round-49 docstring says it defends against ("a FIFO or device path would block or stream forever").
  2. stat on a small regular file passes the size cap; the path is then swapped to a 2 GiB sparse regular file; `open()`+`fstat()` reports `fs.st_size = 2147483648`, so the hashing loop would read 2 GiB (the cap was never re-checked on the object actually read).
- Minimal proposed fix (applies cleanly; `proposed/fix-combined.diff`): single syscall pattern — `fd = os.open(archive, os.O_RDONLY | os.O_NONBLOCK)`, `os.fstat(fd)` for both S_ISREG and the size cap, then `os.fdopen(fd, 'rb')`. `O_NONBLOCK` is inert for regular files, so no flag-clearing is needed; a FIFO at open time is opened without blocking and then rejected by `S_ISREG` on the fd. This also removes the second path lookup entirely.
- Related, same class: `main()` computes `server_size` with a fresh `os.path.getsize(server_real)` at `tools/kama-llamacpp-live.py:1666` after `sha256_file(server_real)` (1661); a `--server` file replaced between the hash and the getsize is compared against a size from a different object than the one hashed. Sharing one descriptor for hash+size (e.g. `sha256_file` returning `(hexdigest, size)`) closes it.

### F2 (low–medium) — `hold_for_witness()` announces `ready.json` before re-proving the child is alive; a dead-pid announce is possible

- `tools/kama-llamacpp-live.py:287-300` — `ready.json` (with the child's pid) is written unconditionally; `_child_running(proc)` appears only inside the poll loop. The caller's last liveness proof (`verify_live(proc, port, 'post-probes')`, line 1838) precedes the call, so the window is small, but if the child exits in between — or during the hold before the observer reads — the observer finds a pid that is already gone. The counter fails closed (`round49-replay-witness-audit.py:327-329` reports "server still alive or port still accepting" / `observe` problems), so the practical impact is a flaky/failed C1 run, not a false pass.
- Minimal proposed fix (`proposed/fix-combined.diff`): gate the announce on `_child_running(proc)` before writing, and withdraw `ready.json` if the child dies right after the announce or during the hold, returning `released=False`.

### F3 (low) — selftest coverage gaps for the new bounds and the witness feature

`_provenance_selftest()` covers size-mismatch, sparse, not-regular, absent, not-a-file, digest tokens (lines 1387-1393). Not covered, all verified by my fixtures to behave as documented:

- member-count cap boundary (`provenance-archive-too-many-members`): fixture `evidence/fixture_verify_bounds.py` — 4096 entries pass, 4097 → `provenance-archive-too-many-members`;
- `provenance-archive-too-large` (needs a > 1 GiB file; cheap with `ftruncate`);
- EOFError/TarError mapping: truncated gzip fixture → `provenance-archive-unreadable` (see F-ok below);
- duplicated member name → last occurrence wins (no assertion anywhere; see F4);
- witness feature entirely: `hold_for_witness` (release/timeout/child-exit paths), `--witness-dir`/`--witness-timeout` validation, and the receipt `witness` block are untested by `--selftest`.

### F4 (info) — "last occurrence wins, as extraction does" is interpreter-version-sensitive

Verified on the runtime here (python 3.14.8): `TarFile.getmember()`/`extractfile()` return the **last** occurrence (`getmember offset 2048` for three same-named members; content `b'MIDDLE'`), so `verify_archive_member`'s last-wins loop matches extraction. Older CPython tarfile implementations returned the first match; if the lane's `python3` is ever pinned to an older interpreter, verified-member identity could diverge from extracted-member identity. Cheap hardening: assert single occurrence during the walk, or name the expected interpreter in the tool's docstring.

---

## Checklist results (all verified, no findings)

| Item | Result | Evidence |
|---|---|---|
| S_ISREG guard before open | works for a pre-existing FIFO: `provenance-archive-not-regular` (residual race = F1) | fixture output |
| size cap 1 GiB and member-count cap 4096 walk streaming with count cap | 4096 pass / 4097 refused, `provenance-archive-too-many-members` | fixture output |
| sparse check (`found.sparse is not None`) before reading | PAX GNU-sparse fixture → `provenance-member-sparse`; selftest passes (build's own fixture) | fixture output; `--selftest` exit 0 |
| declared-size == `--server` size before hashing | `provenance-member-size-mismatch` | fixture output |
| error-token mapping incl. EOFError | truncated gzip (EOF in the compressed stream) → `provenance-archive-unreadable` | fixture output |
| order: sparse/size before a member byte is hashed | code lines 260-267 (checks precede `extractfile`) | inspection |
| `ready.json` atomic | `os.replace(tmp, ready.json)` (line 292) | inspection |
| release polling, child-exit termination, timeout bound | loop condition (lines 295-297) | inspection |
| signals during hold | SIGINT/SIGTERM/SIGHUP → `Terminated` → teardown runs in `finally` (lines 1723-1727, 1868-1875) | inspection |
| teardown after hold | guaranteed (`finally` → `teardown`); replay timeout includes witness timeout (`kama-live-replay.py:281`) | inspection |
| receipt `witness` fields | `{schema, dir, port, pid, released, waited_ms}` matches docstring and counter contract | inspection |
| argument validation | `--witness-dir` must exist; `--witness-timeout` > 0 incl. `nan` rejected (`parser.error`, exit 2) — verified: `0`, `-5`, `nan` rejected; `inf`/`1` accepted | command runs |
| replay integration | `argv[-2:-2]` splice before `--out`; both v5-archive and witness flags coexist (lines 274-279) | inspection |
| counter contract alignment | witness leg reads `ready.json {pid, port}`, observes `/proc/<pid>/exe`, LISTEN inode, `-m`, nonce round-trip, then writes `release`, requires `witness.released` true and pid gone (lines 292-340) | inspection |

Command traces (all exit codes):
```
$ python3 tools/kama-llamacpp-live.py --selftest
selftest: ok; closed tcp6 listeners ::1:39205, ::ffff:127.0.0.1:46217
selftest exit=0

$ python3 .../evidence/fixture_verify_bounds.py
4096 index entries: PASS (no raise)
4097 index entries -> provenance-archive-too-many-members
duplicate member verified against LAST occurrence -> (...)
FIFO -> provenance-archive-not-regular
truncated gzip -> provenance-archive-unreadable
fixture exit=0

$ python3 .../evidence/fixture_toctou.py
stat S_ISREG: True size 13
open(path) BLOCKED >2s after stat passed on the same path (TOCTOU window)

$ git -C <clone> apply --check proposed/fix-combined.diff   # clean
$ python3 -c "ast.parse(open('live.fixed.py').read())"       # parses
```

## Residual risk / verification gaps
- F1's in-function race was demonstrated via the vulnerable primitive (stat-pass → open-block) rather than a statistically reproduced race inside the running function; the fix removes the primitive.
- The full C1/C2 counters and the three round-48 receipt witnesses were not run by this seat (leaf code review; L1's dry run reports `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` and `fixture=1 lane=1 scenarios=8/8 met=True`). The counter's contract was read (`tools/round49-replay-witness-audit.py`) and cross-checked against the implementation.

## Deliverables (absolute)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/evidence/fixture_verify_bounds.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/evidence/fixture_verify_bounds.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/evidence/fixture_toctou.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/evidence/fixture_toctou.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/evidence/selftest.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Live/proposed/fix-combined.diff
