# Sen2Replay — host-safety review of the round-47 replay path (C2 surface)

**Verdict:** as driven by the frozen C2 counter the replay leg is host-safe on this host
(asset URL+sha pinned, both digests verified before extraction, `filter="data"` refused every
crafted traversal/link/device archive, teardown verified on SIGTERM/SIGINT with no orphan,
loopback-only port with procfs ownership proof, log deleted on every receipt path); **six
defects remain in `tools/kama-live-replay.py`, two in the C2 counter, one in the live tool's v4
validation**, the serious one being that replay **executes** the extracted member *before*
comparing it with the receipt's recorded
`server.sha256`, so a v4 receipt is a run-my-archive capability for any caller that does not pin
the asset. Nothing found contradicts the C2 dry-run line (`receipts=1 replay=1 tamper=1 …`).

Reviewed bytes: lane commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` only
(`evidence/reviewed-sha256.txt`: replay `39cd387a…`, live `65301a3c…`, counter `15408dce…`),
Python 3.14.8, Linux 7.2.11. Probe scripts in `demo/`, transcripts in `evidence/`. **Not run:**
the C1 or C2 counters (the L1's measurement; 24 MB of downloads), any llama-server, and any
untrusted binary outside `$S=/fast/scratch/hyaku/kama-r47/Sen2Replay`. No tool installed.

## Findings

| id | sev | site (frozen) | one line |
|----|-----|---------------|----------|
| F1 | Med (High for a caller that trusts an unpinned receipt) | `kama-live-replay.py:145-157` | executes the extracted member before checking it against `rec.server.sha256` |
| F2 | Med-Low | `kama-live-replay.py:143-145` | extracts into a reused `work/server`; a stale member from an earlier run satisfies `member` and runs |
| F3 | Low-Med | `round47-live-replay-audit.py:184-196` (and `kama-live-replay.py:157`) | timeout kills only the direct child; the replay subtree survives |
| F4 | Med-Low | `round47-live-replay-audit.py:158-163` | model URL/sha are not pinned; any https GGUF with a self-consistent digest is accepted |
| F5 | Low | `kama-live-replay.py:61-65` | no download or extraction size cap; no total deadline (per-recv timeout only) |
| F6 | Low | `kama-live-replay.py:61-65` | `.part` file survives an aborted download |
| F7 | Low-Med | `kama-live-replay.py:169`, `:178`, `:260` | crashes surface as exit 1 ("ran and differs") with no `--out` |
| F8 | Low | `kama-live-replay.py:20` vs `:59` | "https only" is not enforced: `file://` always accepted, 302 can downgrade to http/ftp |
| F9 | Info | `kama-llamacpp-live.py:1128-1132`, `:1381` | v4 provenance is recorded, not derived or validated; `log_path: null` is accurate |

### F1 — the binary runs before its digest is checked (bit the counter cannot see)
`replay()` resolves `server` at `:145`, guards only "inside tree and is a file" (`:146`), then
hands it to the live tool at `:157`, which `Popen`s it (`kama-llamacpp-live.py:1479-1526`). The
receipt's `server.sha256` is compared only *after* the run, in `compare()`.

Evidence (`evidence/e2.frozen.out`, C3): receipt records `server.sha256 = 000…0`, the archive
member is a shell script; replay exits 1 with `server.sha256:000…->194d880e…`, **and the script
executed**, writing its argv:
`marker = ['…/w/server/build/bin/llama-server', '-m', '…/w/download/m.gguf', '--alias','sen2','--host','127.0.0.1','--port', <kernel port>, …]`.
So "digest verified before anything is extracted or executed" is true for the *download* and
false for the *member*.

Exploit path (tool standalone): a v4 receipt is plain JSON; whoever hands you one picks
`asset_url`/`asset_sha256`/`member`, and replay runs that content as your uid before any check
can object. Under C2 the counter pins `ASSET_URL`/`ASSET_SHA` (`round47-live-replay-audit.py:153-156`),
so the executed bytes come from the genuine b11909 tarball and the residual path is another
member of the same tarball — which the post-exec compare then flags (replay=0). The counter's
pin, not the tool, is what protects this lane.

Check that catches it: `sha256_file(server)` before `:157`, refuse unless it equals
`rec.server.sha256`. Patch: `proposed-kama-live-replay.diff` (adds the check and a
`member-digest-mismatch` selftest case). Verified: `evidence/patch-verify.out` F2 →
`exit 2, member-digest-mismatch, marker_written=False`; selftest 11/11
(`evidence/selftest-patched.out`).

### F2 — non-hermetic extraction into a reused `--work`
`extract()` writes into `work/server` without clearing it (`:143-145`). Second replay against the
same `--work`, whose archive contains only `README`: exit 0, `match=True`, and the "server" it
ran is the *first* run's script (`sha eb6758…`, `evidence/e2.frozen.out` C5).
Impact: a reused `--work` (nothing in the contract forbids it) supplies the executed bytes, and a
replay is not reproducible from its archive alone. Check: assert the member's provenance is the
archive just downloaded. Fix: `shutil.rmtree(tree, ignore_errors=True)` before `extract` (patch).
Verified: `patch-verify.out` F3 → `member-absent` (exit 2).

### F3 — timeout leaves the replay subtree running
`run_replay` is `subprocess.run(…, timeout=1200)` with no session/group (`:186-190`); `replay()`
uses the same shape for the live tool (`:157`).
Evidence: C9 (outer timeout on replay, the counter's shape) → fake live tool **alive**, grandchild
alive; C8 (`replay --timeout 3`) → live tool dead, grandchild **alive**
(`evidence/e2.frozen.out`).
Why it does not leak a *server* today: the live tool sets `PR_SET_PDEATHSIG` and its own session
(`kama-llamacpp-live.py:461-472`, `:1521-1522`); verified — a child with that preexec dies when its
parent is SIGKILLed (`evidence/pdeathsig.out`: `alive = False`). What leaks is the live tool
process itself (bounded by its own ready/probe timeouts), which then runs while the counter's
`finally: shutil.rmtree(S)` deletes the tree under it. Exploit path: a hung replay (stalled
download, unresponsive server) at t=1200 s → counter returns/reports while an orphan writes into a
half-deleted scratch. Check: after a forced timeout, assert no descendant of the replay pid exists.
Fix: `Popen(start_new_session=True)` + `killpg` on `TimeoutExpired` (patch:
`proposed-round47-counter.diff`).

### F4 — the model is not pinned, only scheme-checked
`round47-live-replay-audit.py:158-163` accepts any `https://` model URL whose
`provenance.model.sha256` equals `model.sha256` — i.e. self-consistency, not identity, while
`ASSET_URL`/`ASSET_SHA` are pinned exactly. Evidence: `patch-verify.out` F7 — frozen
`check_receipt` passes a receipt with `model.url = https://example.invalid/other.gguf`; the patched
one refuses it. Impact: a committed receipt can point the replay (and the C2 claim "re-acquires and
digest-verifies both") at an arbitrary GGUF that a C++ parser then reads. Fix: `MODEL_URL`/`MODEL_SHA`
constants + equality (patch). Check: `check_receipt` must reject a receipt whose model URL is not the
recorded huggingface URL / not `270cba1b…`.

### F5 — no cap on bytes (download or extraction), no total deadline
`:63` copies with `shutil.copyfileobj` until EOF; `timeout=120` is a per-socket-operation timeout;
`acquire()` hashes only the finished file (`:91`). Evidence: `fetch()` copied 64 MiB before any
hash (`e2.frozen.out` C6); a 522 910-byte tar.gz extracted to 536 870 912 bytes — **1028×, 0.88 s,
no cap** (`evidence/e11.frozen.out` E11a). A trickling origin keeps a fetch alive indefinitely
(each recv under 120 s). Impact: a receipt (or a hijacked redirect target, F8) fills the filesystem
holding `--work` before a digest can object. Fix: counting copy loop + `max_bytes`
(patch, `download-too-large`; verified `part_left=False`).

### F6 — partial-download residue
`:61-65` has no `try/finally`; a reset mid-body raises out of `fetch` leaving `dest + ".part"`.
Evidence: `e2.frozen.out` C7a → `dest.bin.part`, 4096 bytes. Debris under `--work` that a later
reader can mistake for evidence. Fix: `finally: unlink(tmp)` (patch; F5 row verifies it).

### F7 — a crash is reported as "it ran and differs"
`replay()` catches `(OSError, ValueError, tarfile.TarError, TimeoutExpired, URLError)` (`:169`)
but not `http.client.HTTPException` (an incomplete body, realistic on a flaky download) nor
`TypeError` (a Python without `filter=` support, i.e. < 3.12 unbackported; **code reading only —
no such interpreter on this host, not exercised**). `main()` then writes
`--out` without creating its parent (`:260`).
Evidence: `e2.frozen.out` C7b — `http.client.IncompleteRead` escapes `replay()`;
`evidence/e14.frozen.out` — `--out` inside a not-yet-created `--work` → traceback at `:260`,
**exit 1, no J**; the same refusal with an existing out dir → `exit 2,
provenance-model-digest-differs…`; `evidence/selftest-missing-scratch.out` — `--selftest
--scratch <missing>` → traceback at `:178`, exit 1.
Impact: exit 1 is the contract's "ran and differs"; a crash is indistinguishable from a real
mismatch to any wrapper reading codes rather than J (the C2 counter does read J, so it fails
closed, but its detail line would be misleading). Fix: final `except Exception` → refused/exit 2;
`makedirs(dirname(out))`; `makedirs(scratch)` (patch). Verified: F6 → `exit 2, out_written True,
traceback False`.

### F8 — "Network: https only" is not what the code does
`:20` claims https-only; `:59` accepts `file://` unconditionally (the selftest needs it, nothing
else gates it). Evidence: C1 — a `file://` receipt replays to `exit 0, match=True` in the normal
(non-selftest) path. And the gate inspects only the URL it is given: `urllib` re-targets from the
`Location` header and permits http/https/ftp (`/usr/lib/python3.14/urllib/request.py:676`);
`evidence/e11.frozen.out` E11b — `302 Location: http://…` accepted, `ftp://…` accepted,
`file://…` refused by urllib. Impact: an https→http downgrade mid-transfer (integrity still pinned
by the sha256, so the risk is disclosure/metadata, not substitution) and a receipt that reads local
files into `--work` (content still gated by a digest the receipt author must know). Fix:
`--allow-file-urls` (default off) + post-redirect `r.geturl()` scheme check (patch; the selftest
passes `allow_file=True`), or correct the docstring if `file://` is intended.

## v4 diff review (`bbcc6dc2..3a09a1d9`, `tools/kama-llamacpp-live.py` +30/−4)

* **Recorded, not fetched** — the four new args are stored verbatim (`:1381-1386`); grep shows the
  live tool's only outbound request is the loopback `http_get` (`:493`). ✓
* **Digest args validated** as 64 hex and lowercased (`:1359-1366`). ✓
* **`--server-asset-url` / `--server-member` are unvalidated** (`:1128-1132`): a live run can emit
  a receipt that replay must refuse (`kama-live-replay.py:84`, `member` absolute or with `..`), or
  one whose URL no fresh host can reach. The tool should apply replay's member rule at parse time
  so it cannot publish an unreplayable receipt. (Operability, not host safety.)
* **`teardown.log_path: null` is accurate** for every emitted receipt: `teardown()` unlinks inside
  `finally` (`:919-923`) and `main()` unlinks again (`:1745-1755`). The only residue is a SIGKILLed
  run, which emits no receipt at all. ✓
* **Child isolation** — `CHILD_ENV_KEYS` allowlist (`:89`), recorded as `child_env_keys`
  (receipt-1: `HOME, LANG, PATH, TMPDIR`); replay additionally forces `TMPDIR=work/tmp`
  (`kama-live-replay.py:150`); verified in C10 (child sees `TMPDIR=…/w/tmp`; a sentinel variable in
  the caller's env also reaches the live tool, which is expected — only the allowlist reaches
  llama-server). ✓
* No shell interpolation in either tool: all `Popen`/`run` calls take argv lists. ✓

## Verified-safe (negative results, with the probe)

1. **Digest before extraction**: wrong asset digest → `tree` absent, sentinel member never written
   (C4); wrong model digest → same (E12).
2. **Member guards**: absolute, `../..`, empty member refused (E12: `unsafe-member`,
   `unsafe-member`, `provenance-missing`); backslash accepted as a filename char then
   `member-absent` (no traversal).
3. **`filter="data"`** (`:100`) against 11 crafted archives (E1): `../../x` refused
   (`OutsideDestinationError`); absolute name re-rooted *inside* the tree (no escape);
   absolute/escaping symlink refused; hardlink to `/etc/passwd` refused; chardev and FIFO refused;
   setuid cleared (`04755→0755`); a pre-existing symlink directory inside the tree refused
   (`link/pwn.txt` → `OutsideDestinationError`); `a/../b.txt` sanitised to `b.txt`; scan for
   files outside the tree: none.
4. **realpath+isfile member guard** (`:146`).
5. **Teardown on signals** (E15): SIGTERM and SIGINT → child reaped, `leftover_after=[]`,
   `port_refuses=True`, `log_path=None`, TMPDIR empty; a child that ignores SIGTERM is SIGKILLed
   after 10 s (`sigkill_sent=True`, rc `-9`) and reaped.
6. **PR_SET_PDEATHSIG** works here (pdeathsig.out).
7. **Loopback only, ownership proven**: receipt-1 `argv` has `--host 127.0.0.1 --port 37903`,
   `port_listener_ownership: child`, `teardown_graceful` / `teardown_port_closed` true.
8. **Writes confined** to `--work` and `--out` (C11 listing: `download/m.gguf`,
   `download/srv.tar.gz`, `server/build/bin/llama-server`, `rerun-receipt.json`; `tmp/` created,
   left empty).
9. The counter's tamper legs do reach the clean refusal (`exit 2`, J written) with the counter's
   paths, because `S` exists (`e14.frozen.out`, second case) — so `tamper=1` is not a crash-pass.

## Scope note (lane state)

`git status` in the lane shows `tools/kama-live-replay.py` modified in place (+26/−5, mtime
18:34 local) after the build commit: it adds a `notes` field, an `original:no-evaluated-check`
mismatch, a `live-exit:<rc>` mismatch and a `try/finally` in `fetch`. None of that touches the
scheme gate, the size cap, the tree reuse or the member digest, so all findings above still hold;
but the reviewed bytes, line numbers and the shas in `evidence/reviewed-sha256.txt` are the
committed ones at `3a09a1d9`. If those edits are meant to be the build they need a commit, and the
line numbers shift by ~+9 after `:61`.

## Files written

```
.ufo/waves/round-47/w1/out/Sen2Replay.md                      this report
.ufo/waves/round-47/w1/out/Sen2Replay/proposed-kama-live-replay.diff
.ufo/waves/round-47/w1/out/Sen2Replay/proposed-round47-counter.diff
.ufo/waves/round-47/w1/out/Sen2Replay/demo/                   e1,e2,e11,e12,e15,fake_live,pdeathsig,mkpatch,verify_patched
.ufo/waves/round-47/w1/out/Sen2Replay/evidence/               transcripts, receipt-1.json, reviewed-sha256.txt
```
