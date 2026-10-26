# Sen1Witness — host-safety review of witness mode (round 49, lane kama)

**Verdict:** witness mode tears the held server down correctly on every death of the live tool (SIGTERM 0.25 s, SIGKILL 0.2 s via PDEATHSIG, terminal Ctrl-C 0.2 s) and binds loopback only, **but the announcement protocol is not host-safe: five defects are reproduced against the frozen tip** — a symlink at `ready.json.tmp` is followed for write (arbitrary file clobber, cross-uid in a non-sticky writable dir), a pre-existing `release` makes the witness vacuous (`released=true, waited_ms=0, match=true`), a pre-existing `ready.json` lets a *foreign* server satisfy every observation the C1 counter makes, `--witness-timeout inf` is accepted (no deadline; the replay then dies with an uncaught `OverflowError` after spawning its live child), and `kill <replay-pid>` orphans the held server for the whole timeout. None of these refutes C1 *as the counter runs it today* (fresh `mkdtemp` scratch, observation before `release`); all five are frontier items, each with a check and a validated patch.

## Provenance of what was reviewed

| item | value |
|---|---|
| frozen tip measured | `122c4ee95701587cef7f4342c3d175622ec2f4ad` (build `74558c71` in the tree; witness code identical) |
| `tools/kama-llamacpp-live.py` | `72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c` |
| `tools/kama-live-replay.py` | `636074f9628f8c6106a0b5508dd7a15e8d677ea89cfbe0cd2a665f85ddd1e01a` |
| `tools/round49-replay-witness-audit.py` (frozen, unchanged) | `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` (matches the preregistration) |
| clone | `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (read-only use) |
| scratch | `/fast/scratch/hyaku/kama-r49/Sen1Witness` (`TMPDIR` inside it), removed at exit |
| installs | none (no pacman, no uv, no downloads outside the tools' own replay fetch) |

Every real run used `tools/kama-live-replay.py --witness-dir <S>/…/wd` (or the live tool directly on frozen `--server`/`--model` paths) against receipt `.ufo/waves/round-48/c2/live/receipt-1.json` and the read-only b11909 install; each server was on a loopback port chosen by the tool and is confirmed gone (`ss`, `/proc/<pid>`, `pgrep -af Sen1Witness` → rc=1).

## Findings

| # | severity | defect | file:line | reproduced by | the check that catches it |
|---|---|---|---|---|---|
| F1 | **high** | `ready.json.tmp` is opened for write without `O_NOFOLLOW`/`O_EXCL`: a planted symlink redirects the announcement into any file the operator can write, and `ready.json` is left as a symlink to it | `tools/kama-llamacpp-live.py:294-297` | `scripts/probe-symlink-fifo.py` (A) | refuse a witness dir with group/other write bits or foreign owner; write via `O_CREAT\|O_EXCL\|O_NOFOLLOW`, per-pid name, mode 0600; require `ready.json` to be a regular non-symlink file |
| F2 | **high (witness evidence)** | `release` is tested with `os.path.exists`: a planted file, directory or FIFO releases the hold instantly, so `witness.released` is true with zero observation | `tools/kama-llamacpp-live.py:298-305` | `scripts/runBC-orphan-planted-release.py` (C), `scripts/probe-symlink-fifo.py` (C) | accept only a regular file whose `st_mtime_ns` ≥ the announcement's; the preregistered predicate must require `waited_ms > 0` as well as `released` |
| F3 | **medium-high** | `ready.json` is written only at readiness and never cleared or freshness-checked; a pre-existing file is what a poller reads, and it passes all four C1 observations while naming a server that is not the replay's child | live `:294-297` (no clear), counter `:301-305` (single read, no freshness), `:324-326` (released only) | `scripts/probe_foreign_ready.py` (H) | refuse a witness dir holding `ready.json`/`release`; counter: require `ready.json` mtime > replay start, `pid`/`port` equal to `rr.witness.pid/port`, and the pid's ancestor chain to contain the replay |
| F4 | **medium** | `--witness-timeout` is validated only by `> 0`: `inf` and `1e12` pass, so the hold has no deadline; the replay then builds `subprocess.run(timeout=600+inf)` and dies with an uncaught `OverflowError` **after** spawning its live child (no rerun receipt, no replay output, child abandoned) | live `:1593-1596`; replay `:277-283` | `scripts/probe-inf-pdeathsig.py` (F1/F2) | reject non-finite or > 3600 s **before** any download in the replay and before the server starts in the live tool; require exit 2 with no `pgrep` hit afterwards |
| F5 | **medium** | SIGTERM to the **replay** is not forwarded: the live tool and the server keep listening for the remainder of the timeout (measured 15.11 s of `OPEN`), unbounded with F4 | replay `:280-283` (plain `subprocess.run`, no handler/`start_new_session`), live `:1738-1739`, `:1011`,`:1022`, `:1760-1761` | `scripts/runBC-orphan-planted-release.py` (B) | after SIGTERM to the replay, require the announced port to refuse within N s; or have the replay install a handler that signals the child's process group |
| F6 | low-medium | during the hold the server is an unauthenticated inference endpoint for **every local account**: `/props` and `/tokenize` answered 200 as `nobody`; `ready.json` is 0644 and names port+pid; no `--api-key` (supported per S494 README:215) | live `:1716-1725`, `:295` | `scripts/runA-exposure-sigterm.py` | from a second uid require 401/denied on `/props` and `/tokenize`; require `ready.json` mode 0600 and dir mode without group/other access |
| F7 | low | an unwritable or vanished witness dir fails only after all checks, as `PermissionError`/`FileNotFoundError` recorded as an internal error | live `:294-297` | `scripts/unit-hold.py` (t8, t9) | preflight probe write at argument validation; require `setup_error=witness-dir-…`, exit 2, before the server starts |

### F1 — symlink at `ready.json.tmp` is followed (arbitrary file clobber)

`hold_for_witness` builds `tmp = os.path.join(wdir, 'ready.json.tmp')` and does `open(tmp, 'w')` (`tools/kama-llamacpp-live.py:294-295`). The open follows a symlink and truncates the target; `os.replace` then renames the symlink itself over `ready.json` (`:297`), so the observer reads a file outside the directory.

```
$ python3 scripts/probe-symlink-fifo.py
A: nobody planted ready.json.tmp rc=0
A: hold released=False
A: victim now b'{"schema": "kama-live-witness/v1", "port": 4321, "pid": 1908961, "written_utc": '
A: ready.json islink=True -> .../unit/x-world-writable/operator-notes.txt mode=0o644
B: raised PermissionError: ... '/fast/scratch/.../unit/x-sticky/ready.json.tmp'      # sticky dir: kernel refuses
D: raised IsADirectoryError: ... 'ready.json.tmp' -> 'ready.json'                    # pre-existing dir: loud
```

Exploit path (measured, dir mode 0777 owned by the operator, symlink planted by uid `nobody`): any account that can create a file in the witness dir wins the race against the announcement and destroys a chosen file of the operator's with an attacker-known JSON body — e.g. `~/.bashrc`, `~/.ssh/authorized_keys` (truncated to a JSON line, so an overwrite, not an append), or a lane receipt. `fs.protected_symlinks=1` stops the cross-uid case only in **sticky** world-writable dirs (`/tmp`, `/var/tmp`); a non-sticky shared dir — a group-shared project dir, a `chmod 0777` scratch — is clobberable. The same user's own stale symlink is followed anywhere.

Impact: operator-file integrity loss with the operator's own authority, plus a `ready.json` that is a symlink out of the dir. The write happens after every check and after the 75 MB fetch, so a run can be destroyed at the last step.

### F2 — a pre-existing `release` makes the witness vacuous

`os.path.exists(release)` (`:300`) accepts a plain file, a directory or a FIFO, and does not care when it appeared. Measured against the real replay tool, with one stale file pre-seeded:

```
$ python3 scripts/runBC-orphan-planted-release.py        # section C
C: pre-seeded wd -> ['release']
C: replay exit 0 at +0.09s after ready
C: rerun witness={'dir': '…/C/wd', 'pid': 2110992, 'port': 37413, 'released': True,
                  'schema': 'kama-live-witness/v1', 'waited_ms': 0} outcome=pass
C: replay match=True exit-implied=0 mismatches=[]
```

The server was announced, then torn down 0.09 s later, before any observer could look — and the receipt records `released: true`. The preregistered C1 predicate says "holds its rerun server up for an outside observer … and sees the server gone after release"; the counter implements the first half partly through that receipt field (docstring `:52-53`, check `:324-326`), so a receipt with `released: true, waited_ms: 0` is exactly the artifact C1 publishes as its witness. A FIFO releases the hold identically (`scripts/probe-symlink-fifo.py` C: `released=True waited_ms=0`).

Impact: `witness.released=true` is not evidence of a witness. C1's *measurement* survives because the counter observes first and only then writes `release` (counter `:309-313`), but the receipt it publishes carries a field that any other consumer — L1's dry run, a later verifier re-running a receipt into the same `--witness-dir`, a human — can be given for free. With a reused operator dir, the second run is always vacuous.

### F3 — a pre-existing `ready.json` is what the poller reads (misattribution)

`hold_for_witness` writes `ready.json` only at readiness and never removes a file already there; neither the replay nor the live tool clears the dir at start (grep: no `unlink` on `ready.json`/`release`), and both leave `ready.json` behind after teardown (`wd after -> ['ready.json']` in runs A, B, C, G, I). A poller that reads `ready.json` — the counter's loop is exactly that (`:301-305`) — therefore sees whatever was there *before* the download finished, i.e. for up to `READY_WAIT=600 s`.

Measured with a real frozen b11909 server kept alive under a different live-tool run, its `ready.json` copied into the replay's witness dir:

```
$ python3 scripts/probe_foreign_ready.py
H: pre-planted ready.json in the replay's witness dir: pid=2304344 port=43041
H: a poller's first read of ready.json during the replay: +0.00s pid=2304344 port=43041 same_as_foreign=True
H: exe sha == frozen b11909: True
H: listeners on the announced port: LISTEN 127.0.0.1:43041 users:(("llama-server",pid=2304344,fd=3))
H: tokenize pieces [' k', 'am', 'a', ' w', 'it', 'n']
H: detokenize ' kama witness deadbeefdeadbeef'
H: replay exit 0 ... match=True
H: the replay's own server pid was 2321552, observed pid was 2304344 -> bound=False
```

Every observation the counter makes in `observe()` (exe sha = frozen b11909, LISTEN inode owned by the pid, `-m` = frozen model, nonce round-trip with pieces matching the counter's own vocabulary) passes on a server that is **not** the rerun's child. Composed with F2 (a planted `release` for the receipt check), all five conditions of the C1 witness leg can hold while the replay's own server is never witnessed. `[INFERENCE]` — the two halves are measured separately; the composition against the frozen counter was not run, and cannot be run against the counter's own scratch: it uses `tempfile.mkdtemp` (`round49-replay-witness-audit.py:417`), `rmtree` (`:471`) and a per-tag `os.makedirs` (`:294`), so its witness dirs are fresh by construction (a pre-created dir instead raises `FileExistsError` and kills the counter with a traceback — loud, exit 1). The window is real for any other consumer of `--witness-dir`, including a re-run in the same operator dir: my first A re-run read a two-run-old `ready.json` at +0.0 s (`evidence/stale-ready-in-reused-wd.out`).

### F4 — `--witness-timeout inf`, no deadline, and an uncaught `OverflowError` in the replay

`if not args.witness_timeout > 0` (`live:1595`) accepts `inf` and `1e12` (`scripts/unit-hold.py` t11: `inf → gt0=True`, `1e12 → gt0=True`; `nan`, `0`, `-1` are rejected). The hold loop then has no deadline:

```
$ python3 scripts/probe-inf-pdeathsig.py
F1: live tool --witness-timeout inf
F1: ready {'schema': 'kama-live-witness/v1', 'port': 35073, 'pid': 2227981, …} at +0.3s
F1: +4.8s live=True server=True port=OPEN
F1: +5.3s live=True server=True port=OPEN           # nothing ends this hold but a release or a signal
```

The replay mirrors the value into `subprocess.run(timeout=timeout + witness_timeout)` (`replay:282-283`), and CPython's selector cannot take an infinite timeout:

```
F2: replay exit 1 after 2.6s
F2: replay.log tail: OverflowError: cannot convert float infinity to integer
F2: replay.json written=False rerun receipt=False
```

`subprocess.run` had already spawned the live child, and `Popen.__exit__` does not signal it: the replay's own log shows the traceback, the child is abandoned mid-flight (in the earlier run of the same case the child had already downloaded and extracted the tree before exiting without a receipt — `work/download`, `work/server` present, no `rerun-receipt.json`). Impact: an unbounded unauthenticated inference service on the host, and a replay that crashes with no receipt and no record of the child it started. `--witness-timeout 1e12` is accepted by the same `> 0` test and ends only through the loop's other exits (`t12`: the hold was ended by an external `release`, not by its deadline).

### F5 — SIGTERM to the replay orphans the hold; Ctrl-C does not

`subprocess.run` (`replay:282`) does not use `start_new_session`, so the replay, the live tool and the server sit in the caller's process group. Two very different outcomes:

* `kill <replay-pid>` (SIGTERM to the replay only) — not forwarded; the live tool keeps holding until its own timeout:

```
$ python3 scripts/runBC-orphan-planted-release.py        # section B
B: SIGTERM replay 2013626 (live tool [2025401], server 2027016)
B: +0.32s replay=-15 live=[2025401] server=True port=OPEN
…
B: all gone at +15.11s (port CLOSED:ConnectionRefusedError)
B: rerun witness={'…': …, 'released': False, 'waited_ms': 15016} outcome=pass
```

* Ctrl-C in a terminal (SIGINT to the group) — the live tool's handler (`live:1738-1739`) raises `Terminated`, the `finally` teardown runs, the server is gone in 0.2 s:

```
$ python3 scripts/probe_signals.py
ctrl-c: SIGINT to the replay's process group (what a terminal Ctrl-C does)
ctrl-c: server gone +0.2s port=CLOSED:ConnectionRefusedError replay_exit=-2
ctrl-c: rerun witness=None outcome=setup-error setup_error=terminated:signal 2
```

So the operator's *interactive* interrupt is safe and the *supervisory* one (`kill`, a job runner, a CI timeout) is not; with F4 the orphan window is unbounded. SIGKILL of the live tool is safe (PDEATHSIG), see below.

### F6 — who can reach the held server

`--host 127.0.0.1` (`live:1719`), confirmed by `ss`: `LISTEN 0 512 127.0.0.1:44499 … users:(("llama-server",pid=1994390,fd=3))` — not reachable off-host, reachable by every local account. Measured as uid `nobody` during a hold:

```
$ python3 scripts/runA-exposure-sigterm.py
as nobody /props: rc=0 out=200 b'{"default_generation_settings":{…'
as nobody /tokenize: rc=0 out=200 b'{"tokens":[{"id":409,"piece":" k"},…'
ready.json mode 0o644 uid 1000
```

The window is the whole hold (default 120 s, up to 3600 s after the F4 fix, unbounded today): a loaded model, `/props` (model path), `/slots`, generation, and the resulting CPU/memory, for free, to any local user — including a compromised service account. `--api-key` is available in the frozen b11909 (`.ufo/waves/round-49/c1/server-README-caa8191d.md:215`), and `ready.json` at 0644 hands every local user the port. Mitigation is a design choice for r50 (the frozen counter calls `/tokenize` without an auth header, so an api-key must be announced *and* the counter updated in the same change); the smallest safe step now is a private witness dir + 0600 `ready.json` + a small timeout, and documenting that a witness run is a single-user operation.

## Verified safe (with the evidence that says so)

* **Cross-filesystem witness dir.** `tmp` is built from `wdir` (`live:294`) and `os.replace` renames it inside the same directory (`:297`), so no cross-device rename can occur; the protocol needs no shared filesystem with the work dir. `[INFERENCE]` for a *network* witness dir: no `fsync` before/after the rename, so a crash can lose the announcement and an attribute-cached NFS client can see it late — both end in the observer timing out (loud), never a silent pass, unless a stale `ready.json` is present (F3).
* **PDEATHSIG chain (live tool → server).** `_preexec_pdeathsig` (`live:593-602`) plus `start_new_session` (`:1760-1761`); SIGKILL of the live tool kills the server in 0.2 s and the port refuses (`scripts/probe-inf-pdeathsig.py`: `F1: server gone +0.2s after SIGKILL`). The replay→live-tool hop has no PDEATHSIG, which is F5.
* **Child dies during the hold.** The loop polls `_child_running` (`live:300-302`), the hold returns `released=False`, `verify_live(… 'post-witness')` fails the run: `t10-child-dies released=False waited_ms=150`.
* **`nan`, `0`, negative timeouts** are refused (`t11`), and the *frozen replay* passes a negative value through to the live tool, which rejects it — after downloading 75 MB (`probe_signals.py`: `negative: replay exit 2 … refused 'no-rerun-receipt:exit=2: … --witness-timeout must be > 0'`), i.e. loud but wasteful; the replay has no early range check (same fix as F4).
* **Dangling `release` symlink** does not release (`t4`: `released=False waited_ms=500`) — `os.path.exists` follows and finds nothing; the pathological direction is F2.
* **`ready.json` pre-existing as a symlink** is not followed by the write path (`t7`: victim unchanged) — because `os.replace` renames over it; only the *temp* name is dangerous (F1).

## Proposed fix (diff, validated 9/9)

`proposed-witness-hardening.diff` (unified, `a/tools/…` → `b/tools/…`, applies to `122c4ee9`):

1. `witness_dir_problems()` — refuse a dir not owned by the euid, group/other-writable, or holding `ready.json`, `release` or a stale `ready.*.json.tmp`; checked at argument validation (`live:1593`) and re-checked in the hold.
2. `_write_ready()` — `os.open(…, O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)` under `ready.<pid>.json.tmp`, then `os.replace`; `unlink` on any failure.
3. `_released()` — only a regular file with `st_mtime_ns >=` the announcement's releases the hold.
4. `--witness-timeout` must be finite and in `(0, 3600]`; the witness block gains `timeout_s`.
5. `kama-live-replay.py` — the same range check at the top of `replay()` (before any download) and `OverflowError` added to the refused-exception tuple.
6. `round49-replay-witness-audit.py` (frozen; **r50 proposal only**) — require `ready.json` mtime ≥ replay start, `waited_ms > 0`, and `rr.witness.pid/port == ready.pid/port`.

Validation (`scripts/validate-patch.py`, patched tree in `patch/wt`, full lane layout so the tool's sibling `kama-probe.sh`/`registry/` resolve):

```
1-world-writable-refused: PASS rc=2 err=--witness-dir unusable: group-or-other-writable
2-planted-tmp-symlink-refused: PASS rc=2 victim='KEEP'
3-stale-ready-refused: PASS
4-planted-release-refused: PASS
5-inf-refused: PASS rc=2
6-hold-0600-fifo-ignored: PASS ready=True mode=0o600 witness={… 'released': False, 'timeout_s': 3.0, 'waited_ms': 3004}
6b-hold-outcome-pass: PASS outcome=pass
7-fresh-release-releases: PASS witness={… 'released': True, 'waited_ms': 350}
8-replay-inf-refused: PASS rc=2 spawned_download=False refused=witness-timeout-out-of-range
9/9 cases pass
```

The legitimate path still works end-to-end (case 6/6b: a real b11909 server, `outcome=pass`), and the patched live tool stays compatible with the **unmodified** counter: the counter's dir is `0755` owned by the caller, fresh, and its `release` is a regular file created after the announcement — so `released=true, waited_ms>0` and the counter's existing check passes. Note the counters' own defence against F2/F3 is incidental (`mkdtemp` + `makedirs`), not part of the protocol, so a future counter that reuses a dir inherits both holes.

## Notes for the lane (not defects)

* The receipt has **no witness block when the hold is interrupted**: `receipt['witness']` is assigned only after `hold_for_witness` returns (`live:1874`). A run killed during the hold therefore leaves no record that a server was published, while `ready.json` sits in the dir — see run A (`setup_error: terminated:signal 15`, `witness: None`, `wd now: ['ready.json']`). Recording the announcement before waiting (`status: announced`) would keep the receipt truthful under interruption.
* Every frozen run leaves `ready.json` (and any `release`) in the witness dir; with F3's fix at start, a re-run in the same dir fails loudly instead of silently reusing it.
* `waited_ms` without `timeout_s` cannot distinguish "released promptly" from "timeout expired"; the diff adds `timeout_s`.
* C1's counter is unchanged and its result is not contradicted here: the fresh `mkdtemp` scratch (`:417`), `rmtree` (`:471`) and per-tag `makedirs` (`:294`) close F2/F3 for today's measurement, and `observe()` runs before `release` is written (`:309-313`).

## Evidence index (all under `.ufo/waves/round-49/w1/out/Sen1Witness/`)

| file | command | exit |
|---|---|---|
| `evidence/unit-hold.out` | `python3 scripts/unit-hold.py` (imports the frozen tool; 12 cases) | 0 |
| `evidence/probe-symlink-fifo.out` | `python3 scripts/probe-symlink-fifo.py` (A world-writable, B sticky, C FIFO, D readydir) | 0 |
| `evidence/runA-exposure-sigterm.out` | `python3 scripts/runA-exposure-sigterm.py` (real replay: `ss`, `/proc`, as-nobody, SIGTERM live tool) | 0 |
| `evidence/runBC-orphan-planted-release.out` | `python3 scripts/runBC-orphan-planted-release.py` (B replay SIGTERM, C planted release) | 0 |
| `evidence/probe-inf-pdeathsig.out` | `python3 scripts/probe-inf-pdeathsig.py` (F1 inf hold + SIGKILL, F2 replay inf) | 0 |
| `evidence/probe-foreign-ready.out` | `python3 scripts/probe_foreign_ready.py` (H foreign ready.json) | 0 |
| `evidence/probe-signals.out` | `python3 scripts/probe_signals.py` (Ctrl-C group SIGINT, negative timeout) | 0 |
| `evidence/validate-patch.out` | `python3 scripts/validate-patch.py` (9 cases on `patch/wt`) | 0 (9/9) |
| `evidence/stale-ready-in-reused-wd.out` | second `runA` in the same witness dir (stale announcement read at +0.0 s) | 1 (driver crash on the dead pid — that is the finding) |
| `evidence/receipts/*` | rerun receipts / replay outputs / `ready.json` / planted `release` cited above | — |
| `proposed-witness-hardening.diff` | unified diff (205 lines) for `tools/` | — |
| `scripts/*.py` | every probe, re-runnable with `SEN1_S=<scratch>` (the heavy ones fetch the pinned archive/model as the tools do) | — |

Wrote: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/proposed-witness-hardening.diff`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/scripts/` (9 files), `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/evidence/` (8 logs + `receipts/` 15 files).
