VERDICT: FINDINGS — the v2 `own` leg verifies the RESOLVED member file, so a symlink at `<work>/server/<member>` reopens the round-50 J4Decoy class (HIGH); plus two crash-class defects (pre-`try` member-shape AttributeError that orphans the replay tree, unguarded OSError in `own_exe`) and two nits.

Seat: V1Review — review of the frozen C1 counter `tools/round51-replay-exe-audit.py`
as a diff against `tools/round50-replay-bind-audit.py` (`diff -u`, at
`out/V1Review/c1-v2.diff`). Frozen bytes verified: `git show
804bde75164444bdf0fe6783d7aa45774bf562bd:tools/round51-replay-exe-audit.py` sha256
`e5753c453c30…5155` == working-tree file. Build receipt
`measured/c1-build.out` (copied to `out/V1Review/cases/`) records `met=True` at
73bf2a7a — the nominal path works. Case drivers and captures are in
`out/V1Review/cases/`; the proposed fix is `out/V1Review/own_exe-fix.patch`
(applies to `tools/round51-replay-exe-audit.py`), with the patched file at
`out/V1Review/round51-replay-exe-audit-patched.py`.

---

## HIGH — `own` checks the resolved file, not the extracted one: symlink member reopens J4Decoy

**Where:** `tools/round51-replay-exe-audit.py:369` (`ms = os.stat(member_path)`),
the `os.open`+`os.fstat` of `/proc/<pid>/exe` at 355-361 (correct — that resolves
to the real running image), and the `own_server` leg at 495-498
(`os.path.realpath` on both sides). All three own legs compare *resolved* file
identity, so nothing requires a regular file to exist at the member path.

**Attack:** the cheating replay writes `<work>/server/<member>` as a symlink to
the host's byte-identical install (`/home/vgpnk/.local/opt/llama-b11909/
llama-server`) and execs it — exactly the J4Decoy decoy v2 was built to close,
laundered through one symlink. `own_exe`: `fstat(/proc/pid/exe)` yields the host
file's dev:ino; `os.stat(member_path)` follows the link to the same dev:ino;
bytes hash to `SERVER_SHA`. `server_exe`/`own_server` legs are equally
resolved-file-based and the replay emits them honestly. No race needed — the
receipt member (`llama-b11909/llama-server`) is unchanged.

**Evidence** (`cases/case_member_symlink.{py,out}` — the real host binary running
the frozen model on a loopback port, member path = symlink):

```
own_exe returned: ('00:38', '238037577')   <- fstat of /proc/<pid>/exe
host install dev:ino: 00:38:238037577      <- identical
probs: []
VERDICT: BYPASS - own records no problem; dev:ino and sha legs all satisfied
realpath(member) inside realpath(work)? False
```

The replay tool shares the blind spot (`tools/kama-live-replay.py:359-368` at the
build tip — `os.stat(server)` emits `own_server`/`server_exe` dev:ino), so
fixing the counter alone is sufficient for *detection*.

**Fix:** in `own_exe`, `os.lstat(member_path)` and require `S_ISREG`, then
require `realpath(member_path)` inside `realpath(<work>)` (also covers symlinked
`server/` dirs, `..` and absolute member strings). In `own_exe-fix.patch`;
verified in `cases/case_patch_verify.out` cases A and C.

## MEDIUM — `bind_one` member-shape crash before `try`: skips `finally: reap()`, orphans the tree

**Where:** `tools/round51-replay-exe-audit.py:449`
`member = ((load(rpath) or {}).get("provenance") or {}).get("server", {}).get("member")`
runs after `start_replay` (process tree + log file already live) but before the
`try:` at 451 whose `finally:` reaps the tree and closes the log. If
`provenance` or `server` exists but is not a dict (e.g. `"server": null` →
`.get("member")` on `None`), `.get` raises `AttributeError` → propagates out of
`bind_one`: no `detail`, no `reap`, no `log.close()`, counter dies with a
traceback and exit 1 (no `met=` line — also conflates "crashed" with "not met";
the contract's exit-2 covers only the rev-parse/archive git failure).

**Evidence** (`cases/case_member_shape_crash.{py,out}` — real `bind_one`,
receipt `{"provenance":{"server":"not-a-dict"}}`, stubbed `start_replay`):
`AttributeError` escaped; `invoker alive=True (reap() never ran)` — the invoker/
replay/server tree is orphaned and runs unattended until the replay's own
`pdeathsig` chain un-winds it. Driver reaped the leftover.

**Trigger assessment:** the frozen receipts are well-formed and `load()` fails
soft on bad JSON (`:115-120`), so this needs a valid-JSON receipt with a malformed
`server` shape — a different tip's receipts or a tampered tree receipt (the
counter reads the mutable extracted copy in its own scratch, at `main` 589-596).
Cheap fix: type-guard the chain (in the patch); moving `member` computation
above `start_replay` would also remove the orphan window.

## LOW — `own_exe` unguarded read path: OSError escapes, counter crashes exit 1

**Where:** `tools/round51-replay-exe-audit.py:360-365` — `os.fstat(fd)`,
`os.dup(fd)`, `os.fdopen`, and the hash read sit under `finally` only, no
`except`. `os.open` at 355 is guarded. The counter's own convention is fail-soft
(`sha_file:104-112`, `environ_keys`, `mapped_model` all fold OSError into
`probs`); `own_exe` departs from it.

**Evidence** (`cases/case_fd_exhaustion.{py,out}` — fd table exhausted to
EMFILE, `os.open` succeeds, `os.dup` raises):
`UNGUARDED: OSError: Too many open files escaped own_exe (probs=[])`.
Through `bind_one` (try/finally only) → `main` (no except around legs) →
traceback + exit 1, no `met=` line. Reachability in a real run is low (fd
exhaustion or a mid-read EIO), hence LOW. fd hygiene itself is clean:
`os.close(fd)` is in `finally`, the `with` closes the dup'd fd; a leak exists
only if `os.fdopen` throws after `os.dup` succeeds — negligible.

**Fix:** `except OSError` appends `own: /proc/<pid>/exe unreadable: …` and
returns `None` (verified, `case_patch_verify.out` case D).

## Nits

- **Duplicate own messages, one cause** — when the receipt lacks
  `provenance.server.member`, `oprobs` gains three lines for a single root cause
  (`:465`, `:490-493`, `:494-498`). Evidence: `cases/case_member_absent_dups.out`
  (also demonstrates `observe()`'s fail-soft convention live).
- **`--out` edge** — `--out dir/` (trailing slash): `os.makedirs` at `:577` is
  fine, but `open(a.out,"w")` at `:629` raises `IsADirectoryError` → crash exit 1.
  Parent creation itself is correct (verified for bare filename and `sub/`
  cases) and does run before anything is written — but also before the
  could-not-evaluate exit, so it leaves directories behind on an exit-2 run.
  Tiny; consider `a.out.rstrip("/")` or a try around the write.

## Verified clean (named areas)

- **ready-None path** (`:453-457`): own gets exactly one explanatory line,
  `pid=port=None` short-circuits `observe` and every post-release leg under the
  `pid is not None` guard (`:482`), `release` is still written (replay can exit),
  `(False, False)` returned cleanly — `cases/case_ready_none.out`. `wait_ready`
  validates `pid`/`port` as ints (`:418`), so no KeyError. `pid_alive(None)`
  would return False anyway (`:219-223`, `stat_fields(None)`→None), unreachable.
- **(bind, own) tuple** — `bind_one` returns `(not probs),(not oprobs)` (`:521`);
  `main` consumes `b, o` and counts `bound/owned` independently (`:612-615`). A
  bind-clean leg with own problems cannot inflate `bound`.
- **met line** — `met = bool(bl and ol and tl and nl)` (`:622`), output fields
  `bind= own= teardown= newrow= bound= owned= met=` (`:624-626`) match the
  preregistration's `bind=1 own=1 teardown=1 newrow=1`. Base control
  `bind=1 own=0 teardown=1 newrow=0 met=False` is the expected signature: the
  v5 replay emits no `server_exe`, so `se` fails → `owned=0`.
- **`--out` parent creation** — verified: `makedirs(dirname(abspath))` with
  `exist_ok` works for `receipt.json` and `sub/receipt.json`.
- **fd/dup hygiene** — covered above; no leaks on any covered path.
- **Format contract** — counter `got` is `"%02x:%02x", str(ino)` (`:367`);
  replay emits the same (`tools/kama-live-replay.py:360`, `414-415` at build
  tip); the build receipt shows `103:05:143945881` — consistent.
- **Archive extraction** — `main` drops sym/link members and applies
  `tarfile.data_filter` (`:594-596`); the counter's own tree can't contain
  hostile paths. (The member-path attack is the replay's scratch, not this.)
- **`newrow_leg`** — `check=False` fails soft (`:558-560`); base/tip `rows`
  differencing and the `EXE_URL` hit are correct.

## Residual risk / scope notes

- **Inode identity ≠ provenance.** Even with the symlink fix, the counter cannot
  show member bytes came from the re-downloaded archive — a byte-identical file
  planted at the member path by any means (copy, hardlink on the same
  filesystem) satisfies every own leg (`cases/case_member_identity_b.out`).
  The honest claim is "the running file is at `<work>/server/<member>` and has
  the frozen bytes", which is what J4Decoy lacked; "extracted from the archive
  it re-acquired" overstates it.
- **Receipt is read from the mutable tree copy** (`:449` loads `rpath` inside
  the extracted tree the replay can write). The load happens ~immediately after
  `Popen`, before the replay's interpreter is even up, so a member rewrite can't
  realistically win the race — but anchoring `member` from the in-memory
  `git archive` tar (already held in `arc`, `:588`) costs nothing.
- Crash exit 1 is indistinguishable from honest "not met" by exit code alone
  (the absent `met=` line distinguishes it by output).
- LSP device unavailable in this seat's tool inventory; caller/reference checks
  done via `diff -u` + targeted `grep` + line-anchored reads of both counters and
  the replay emission code at the build tip.
- Did not re-run the full counter (~4 live replays); `measured/c1-build.out`
  evidences the nominal path and my cases exercise the changed code directly.
- Known-item register checked: SKILL-registry gap for the new counters, r41-43
  run_bad, census E11, lane=0 on the old C2, hexrun unknown=2 — all listed in
  the assignment; nothing to add.

## Proposed fix

`out/V1Review/own_exe-fix.patch` (unified diff; full patched file alongside):
1. `own_exe(pid, member_path, work, probs)` gains `work`; after hashing:
   `lstat` → require `S_ISREG` → require `realpath(member)` inside
   `realpath(work)` → then the existing `stat`/sha legs.
2. The `fstat/dup/fdopen/read` block gains `except OSError` → problem + `None`
   (`finally` still closes `fd`).
3. `bind_one` member chain type-guards `provenance`/`server`.
Verification (`cases/case_patch_verify.out`): symlink member → "not a regular
file"; honest regular member → only the sha leg fires (expected — sleep isn't
the frozen server); absolute member → "resolves outside the replay work dir";
EMFILE → fail-soft `None` + problem. Hardlink members are intentionally still
accepted (same inode = same file identity).

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V1Review.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V1Review/c1-v2.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V1Review/own_exe-fix.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V1Review/round51-replay-exe-audit-patched.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V1Review/cases/` — drivers + captures (`case_member_symlink`, `case_member_identity_b`, `case_member_shape_crash`, `case_fd_exhaustion`, `case_ready_none`, `case_member_absent_dups`, `case_patch_verify`), plus `c1-build.out`.
