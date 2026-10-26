# Sen1Witness — host-safety review of witness mode (round 49, lane kama)

**Verdict:** witness mode is host-safe in its *teardown* paths (the held server dies with the live tool in 0.25 s on SIGTERM and 0.2 s on SIGKILL, with the replay in 0.1 s, and a terminal Ctrl-C tears everything down) and binds loopback only, **but its announcement protocol is not host-safe on the frozen build**: a symlink at `ready.json.tmp` is followed for write (arbitrary file clobber, cross-uid in a non-sticky writable dir), a pre-existing `release` makes the witness vacuous (`released=true, waited_ms=0, match=true`), a pre-existing `ready.json` lets a *foreign* server satisfy every observation C1's counter makes, `--witness-timeout inf` is accepted (no deadline; the replay then dies with an uncaught `OverflowError` after spawning its live child), and `kill <replay-pid>` orphans the held server. In the **current working tree** (which moved twice during this review) F1, F4, F5, F7 and the pre-start stale-file cases are closed; **still open there**: the announcement and the release are not bound to the run (a `ready.json` planted after the live tool's own `prepare_witness_dir()`, or replaced during the hold, is what a poller reads — measured — and a `release` created before the announcement ends the hold with `waited_ms: 0`, `released: true`), and every local account can use the held server. Both remaining items have a patch, validated 4/4, with the patched C1 counter still `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` on the frozen tip.

## Two states were reviewed (the tree moved while I worked)

| state | `tools/kama-llamacpp-live.py` | `tools/kama-live-replay.py` | role |
|---|---|---|---|
| frozen build `74558c71` (my assigned contract; clone at `122c4ee9`) | `72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c` | `636074f9628f8c6106a0b5508dd7a15e8d677ea89cfbe0cd2a665f85ddd1e01a` | findings F1–F7 below, all reproduced |
| working tree, copy at 20:39:43 (`wt2`) | `954c2276398926bfe524bf39979815f8718fdd532ba2737bdc7103d04a5ece94` | `d086d22dfa0c879221fe2790c6b1ecc865032d80b71ebd9592e564cb544ef79d` | status probes W1–W7 |
| working tree, 20:39:45–58 (final, `wt4` base) | `0b31f8e6bd98f978c98e6029bfa322c37bac6ae09f9ebf4d770a3fe9ab88a3ba` | `f615d9a0ee0402a59820ff47df2dbc44eb868ba1c28c4d4dedc108f901e16894` | remaining-fix patch + validation |

The two working-tree copies differ only in the `--witness-timeout` validation (4 lines in the live tool, `:1667-1673`; 3 lines in the replay, `:522-525`); `prepare_witness_dir`, `hold_for_witness` and the announcement are byte-identical, so the W probes apply to the final tree. The tree's own comments now cite "round-49 seat Sen1Witness F1/F4" (`kama-llamacpp-live.py:344,1670`, `kama-live-replay.py:526`) — the integration is landing these as I review, so **every status below is pinned to a digest, not to a moment**.

Counters, preregistration and controls are untouched. Scratch: `/fast/scratch/hyaku/kama-r49/Sen1Witness` (`TMPDIR` inside it), deleted at exit. No installs (no pacman, no uv; only the tools' own fetches).

## Findings against the frozen build (F1–F7)

| # | severity | defect | file:line | reproduced by | the check that catches it |
|---|---|---|---|---|---|
| F1 | **high** | `ready.json.tmp` is opened for write without `O_NOFOLLOW`/`O_EXCL`: a planted symlink redirects the announcement into any file the operator can write; `ready.json` is then left as a symlink to it | `tools/kama-llamacpp-live.py:294-297` | `scripts/probe-symlink-fifo.py` (A) | refuse a dir with group/other write bits or a foreign owner; write with `O_CREAT\|O_EXCL\|O_NOFOLLOW`, per-pid name, 0600; require `ready.json` to be a regular non-symlink file |
| F2 | **high (witness evidence)** | `release` is tested with `os.path.exists`: a planted file, directory or FIFO releases the hold instantly, so `witness.released` is true with nothing observed | `tools/kama-llamacpp-live.py:298-305` | `scripts/runBC-orphan-planted-release.py` (C), `probe-symlink-fifo.py` (C) | a release must be a regular file created after the announcement; the receipt's `waited_ms` must be > 0 |
| F3 | **medium-high** | `ready.json` is written only at readiness and never cleared or freshness-checked: a pre-existing file is what a poller reads, and it passes all four counter observations while naming a server that is not the replay's child | live `:294-297`, counter `:301-305`, `:324-326` | `scripts/probe_foreign_ready.py` (H) | refuse a dir holding `ready.json`/`release` (or remove them before the server starts); poller: require mtime > replay start, `pid`/`port`/`nonce` equal to `rr.witness`, and the pid's ancestors to contain the replay |
| F4 | **medium** | `--witness-timeout` validated only by `> 0`: `inf`/`1e12` pass, so the hold has no deadline, and the replay builds `subprocess.run(timeout=600+inf)`, which dies with an uncaught `OverflowError` **after** spawning its live child (no replay output, child abandoned) | live `:1593-1596`, replay `:277-283` | `scripts/probe-inf-pdeathsig.py` (F1/F2) | finite and ≤ 3600 s, checked before any download; exit 2 with no process left |
| F5 | **medium** | SIGTERM to the replay is not forwarded: the live tool and server keep listening for the rest of the timeout (15.11 s measured), unbounded with F4 | replay `:280-283`, live `:1738-1739`, `:1000-1022`, `:1760-1761` | `scripts/runBC-orphan-planted-release.py` (B) | after SIGTERM to the replay, the announced port must refuse within N s |
| F6 | low-medium | during the hold the server is an unauthenticated inference endpoint for every local account (`/props`, `/tokenize` → 200 as `nobody`), `ready.json` is 0644 and names port+pid, no `--api-key` (available per S494 README:215) | live `:1716-1725`, `:295` | `scripts/runA-exposure-sigterm.py` | from a second uid, `/props` and `/tokenize` must be denied; `ready.json` 0600 |
| F7 | low | an unwritable/vanished witness dir fails only after all checks, as `PermissionError`/`FileNotFoundError` recorded as an internal error | live `:294-297` | `scripts/unit-hold.py` (t8, t9) | write probe at argument validation; `setup_error=witness-dir-…`, exit 2, before the server starts |

### F1 — symlink at `ready.json.tmp` is followed (arbitrary file clobber)

```
$ python3 scripts/probe-symlink-fifo.py
A: nobody planted ready.json.tmp rc=0
A: hold released=False
A: victim now b'{"schema": "kama-live-witness/v1", "port": 4321, "pid": 1908961, "written_utc": '
A: ready.json islink=True -> .../unit/x-world-writable/operator-notes.txt mode=0o644
B: raised PermissionError: ... '/fast/scratch/.../unit/x-sticky/ready.json.tmp'   # sticky dir: kernel refuses
D: raised IsADirectoryError: ... 'ready.json.tmp' -> 'ready.json'                 # pre-existing dir: loud
```

Exploit path (measured: dir 0777 owned by the operator, symlink planted by uid `nobody`): any account able to create a file in the witness dir wins the race against the announcement and destroys a file of the operator's choosing with an attacker-known JSON body — `~/.bashrc`, a lane receipt, `~/.ssh/authorized_keys` (truncated to an invalid line: destruction, not takeover). `fs.protected_symlinks=1` saves only the **sticky** world-writable case (`/tmp`, `/var/tmp`); a non-sticky shared dir — a group-shared project dir, a `chmod 0777` scratch — is clobberable, and the operator's own stale symlink is followed anywhere. The write happens after every check and after the 75 MB fetch, so the run is destroyed at the last step.

### F2 — a `release` that predates the announcement makes the witness vacuous

```
$ python3 scripts/runBC-orphan-planted-release.py          # section C
C: pre-seeded wd -> ['release']
C: replay exit 0 at +0.09s after ready
C: rerun witness={'dir': '…/C/wd', 'pid': 2110992, 'port': 37413, 'released': True,
                  'schema': 'kama-live-witness/v1', 'waited_ms': 0} outcome=pass
C: replay match=True exit-implied=0 mismatches=[]
```

The server was announced and torn down 0.09 s later, before any observer could look, and the receipt records `released: true`. C1's preregistered predicate says "holds its rerun server up for an outside observer … and sees the server gone after release"; the counter implements part of that through this receipt field (docstring `:52-53`, check `:324-326`), so `released=true, waited_ms=0` is exactly the artifact the claim publishes. A FIFO releases identically (`released=True waited_ms=0`). The counter's own measurement survives (it observes first, then writes `release`, `:309-313`), but the field is free for any other consumer: the L1 dry run, a later verifier re-running into the same `--witness-dir`, a human.

### F3 — a pre-existing `ready.json` is what the poller reads

```
$ python3 scripts/probe_foreign_ready.py
H: pre-planted ready.json in the replay's witness dir: pid=2304344 port=43041
H: a poller's first read of ready.json during the replay: +0.00s pid=2304344 port=43041 same_as_foreign=True
H: exe sha == frozen b11909: True
H: listeners on the announced port: LISTEN 127.0.0.1:43041 users:(("llama-server",pid=2304344,fd=3))
H: tokenize pieces [' k', 'am', 'a', ' w', 'it', 'n']
H: detokenize ' kama witness deadbeefdeadbeef'
H: replay exit 0 … match=True
H: the replay's own server pid was 2321552, observed pid was 2304344 -> bound=False
```

Every check `observe()` makes (exe sha = frozen b11909, LISTEN inode owned by the pid, `-m` = frozen model, nonce round-trip against the counter's own vocabulary) passes on a server that is **not** the rerun's child, because `ready.json` is trusted by whoever polls it and nothing binds it to the run. Composed with F2 (a `release` for the receipt check) all five conditions of the C1 witness leg can hold while the replay's own server is never witnessed. `[INFERENCE]` for the composition — the halves are measured separately; it cannot be run against the counter's own scratch, which is fresh by construction (`tempfile.mkdtemp` `:417`, `rmtree` `:471`, per-tag `makedirs` `:294`), and a pre-created dir instead kills the counter with a `FileExistsError` traceback (loud, exit 1). The window is real for any other consumer, including a re-run in the same operator dir: my own first A re-run read a two-run-old `ready.json` at +0.0 s (`evidence/stale-ready-in-reused-wd.out`).

### F4 — `inf` has no deadline, and the replay dies after spawning its child

```
$ python3 scripts/probe-inf-pdeathsig.py
F1: ready {'schema': 'kama-live-witness/v1', 'port': 35073, 'pid': 2227981, …} at +0.3s
F1: +4.8s live=True server=True port=OPEN
F1: +5.3s live=True server=True port=OPEN          # nothing ends this hold but a release or a signal
F2: replay exit 1 after 2.6s
F2: replay.log tail: OverflowError: cannot convert float infinity to integer
F2: replay.json written=False rerun receipt=False
```

`if not args.witness_timeout > 0` (`live:1595`) accepts `inf` and `1e12` (`unit-hold.py` t11); `nan`, `0`, `-1` are refused. `subprocess.run` had already spawned the live child and `Popen.__exit__` does not signal it: the replay exits 1 with no output and no receipt, and in the earlier run of the same case the child had already downloaded and extracted the tree (`work/download`, `work/server` present, no `rerun-receipt.json`). Impact: an unbounded unauthenticated inference service on the host, plus a replay that crashes leaving an untracked child.

### F5 — `kill <replay-pid>` orphans the hold; Ctrl-C does not

```
$ python3 scripts/runBC-orphan-planted-release.py           # section B
B: SIGTERM replay 2013626 (live tool [2025401], server 2027016)
B: +0.32s replay=-15 live=[2025401] server=True port=OPEN
B: all gone at +15.11s (port CLOSED:ConnectionRefusedError)
B: rerun witness={'…': …, 'released': False, 'waited_ms': 15016} outcome=pass

$ python3 scripts/probe_signals.py
ctrl-c: SIGINT to the replay's process group (what a terminal Ctrl-C does)
ctrl-c: server gone +0.2s port=CLOSED:ConnectionRefusedError replay_exit=-2
```

`subprocess.run` (`replay:282`) creates no new session, so Ctrl-C reaches the live tool's handler (`live:1738-1739`), which raises `Terminated` and runs the `finally` teardown; a supervisory `kill` reaches only the replay. With F4 the orphan window is unbounded.

### F6 — who can reach the held server

`--host 127.0.0.1` (`live:1719`), confirmed: `LISTEN 0 512 127.0.0.1:44499 … users:(("llama-server",pid=1994390,fd=3))` — not reachable off-host, reachable by every local account:

```
$ python3 scripts/runA-exposure-sigterm.py
as nobody /props: rc=0 out=200 b'{"default_generation_settings":{…'
as nobody /tokenize: rc=0 out=200 b'{"tokens":[{"id":409,"piece":" k"},…'
ready.json mode 0o644 uid 1000
```

For the whole hold (120 s default, up to 3600 s after the F4 fix, unbounded on the frozen build): a loaded model, `/props` (model path), `/slots`, generation and the CPU/memory that goes with it, free to any local user. `--api-key` exists in the frozen b11909 (`.ufo/waves/round-49/c1/server-README-caa8191d.md:215`) but the frozen counter calls `/tokenize` without an auth header, so keying the server is a joint change (server + counter) and not something to slip into this round; the smallest safe steps now are a private witness dir, 0600 `ready.json`, a small timeout, and documenting that a witness run is a single-user operation.

## Status against the current working tree (measured, not read)

| finding | status in the tree | evidence |
|---|---|---|
| F1 temp-name symlink | **closed** — `prepare_witness_dir()` unlinks pre-existing names, then `O_CREAT\|O_EXCL\|O_NOFOLLOW` | W2: `raised SetupError: witness-dir-unusable:File exists`, victim intact |
| F2 pre-existing `release` | **closed** — removed before the server starts | W1: hold ran the full 3 s, `released False, waited_ms 3005` |
| F2 residual: `release` created **before** the announcement | **open** — still `os.path.exists(release)` | W6 receipt: `released True, waited_ms 0` (my driver wrote it in the pre-announcement window) |
| F3 pre-existing `ready.json` | **closed** — removed at start, and the tool removes its own announcement when the hold ends | W6 poller saw *only* the planted one it wrote after prepare; the tool's own write replaced it |
| F3 residual: `ready.json` planted after `prepare_witness_dir()` | **open** — measured, deterministic | W6: planted at +1.98 s, poller read it at +1.98 s, `[('exe-frozen', True), ('listen-owned', True), ('model-frozen', True), ('nonce', True)]` |
| F3 residual: `ready.json` replaced during the hold | **open** | W7: tool announced pid 2873730; replaced with 2869068; a later poller read the foreign one and all four observations passed |
| F4 `inf`/huge timeout | **closed at both CLIs** (`0 < x <= 3600`) | V4: live rc=2, replay rc=2, no download; `probe_worktree.py` W4/W5 were run on the pre-fix copy and show the failure |
| F5 replay SIGTERM | **closed** — the hold also ends when the live tool's parent changes | `worktree-replay-sigterm.out`: `server gone +0.1s`, `orphaned: true, waited_ms: 50` |
| F6 multi-user exposure | **open** — no `--api-key`, announcement 0644, `/props` and `/tokenize` answer for any uid | W-probe `foreign server` reused by W6/W7; A-run measurement |
| F7 unwritable dir | **closed** — write probe at validation | W3: `rc=2 --witness-dir unusable (witness-dir-unwritable:Permission denied)` |

W6 in full (the residual both ways):

```
W6 planted foreign ready.json at +1.98s (live tool pid 2871083)
W6 poller read at +1.98s: {'schema': 'kama-live-witness/v1', 'port': 44211, 'pid': 2869068, …}
W6 observations on the announced pid: [('exe-frozen', True), ('listen-owned', True), ('model-frozen', True), ('nonce', True)]
W6 replay exit 0 rerun witness={'…': …, 'pid': 2871330, 'released': True, 'waited_ms': 0}
W7 the tool's own announcement {'port': 36527, 'pid': 2873730, …}
W7 replaced during the hold; a later poller reads {'port': 44211, 'pid': 2869068, …}
W7 observations: [('exe-frozen', True), ('listen-owned', True), ('model-frozen', True), ('nonce', True)]
```

The exploiting condition is only "an account that can write the witness dir" — the same condition `prepare_witness_dir()` cannot remove, because the plant happens *after* it.

## Proposed fix

Two diffs, both applying to the tree they were cut from:

* `frozen-tip-74558c71-hardening.diff` (205 lines, `a/tools/…`): the whole set against the frozen commit — dir ownership/mode and stale-name refusal, `O_EXCL|O_NOFOLLOW` + 0600 + per-pid temp, the announcement-mtime release gate, `timeout_s` in the receipt, finite/bounded timeouts in both tools, and the counter's freshness + pid/port/nonce binding. Kept for the record: the tree implemented most of it in a different shape (removal instead of refusal), so this diff is not what should land now.
* `worktree-r50-hardening.diff` (128 lines): **only what is still open**, cut against the current tree (`0b31f8e6`/`f615d9a0`) —
  1. `_released(release, announced_ns)`: a release must be a regular file with `st_mtime_ns >=` the announcement's; `announced_ns` captured right after `os.replace`.
  2. `nonce` (`os.urandom(8).hex()`) in `ready.json` and in the receipt's `witness` block, `timeout_s` alongside, and `ready.json` written 0600 instead of 0644.
  3. Counter (frozen file; **r50 proposal only**): `_fresh()` — `ready.json` mtime ≥ replay start; `waited_ms > 0`; `rr.witness.pid/port` (and `nonce` when present) must equal the announcement that was observed.

Validation of the frozen-tip diff (`scripts/validate-patch.py`, run in a full lane layout with the patched `tools/`): **9/9** — world-writable/stale/planted refusals, `inf` refused, a legitimate real-server hold `outcome=pass` with `ready.json` 0600, a FIFO release ignored, and a post-announcement release releasing at +350 ms.

Validation of the worktree diff (`scripts/validate-patch2.py`, `SEN1_WT=wt4/tools`): **4/4**

```
V1-early-release-ignored: PASS witness={… 'released': False, 'timeout_s': 3.0, 'waited_ms': 3005}
V2-late-release-releases: PASS witness={… 'released': True, 'nonce': '034e0e815c2d3dc3', 'waited_ms': 350} outcome=pass
V3-ready-0600: PASS mode=0o600
V4-inf-refused: PASS live_rc=2 replay_rc=2 downloaded=False
```

and the patched C1 counter on the **frozen tip** (my own clone, `--scratch` under my scratch) still says:

```
$ python3 lane/tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71… --scratch $S/cnt
witness=1 cap=1 newrow=1 witnessed=3/3 met=True        (exit 0)
```

so the new freshness/binding gates do not disturb the legitimate path; what they do reject is exactly W6/W7 and the `waited_ms: 0` case.

## Verified safe (with the evidence that says so)

* **Cross-filesystem witness dir.** The temp is built from `wdir` (`live:294`) and `os.replace` renames inside that directory (`:297`), so no cross-device rename can occur and the witness dir need not share a filesystem with the work dir. `[INFERENCE]` for a *network* witness dir: no `fsync` around the rename, so a crash can lose the announcement and an attribute-cached NFS client can see it late — both end in the observer timing out (loud), never a silent pass, unless a stale or planted `ready.json` is present (F3).
* **PDEATHSIG chain (live tool → server).** `_preexec_pdeathsig` (`live:593-602`) with `start_new_session` (`:1760-1761`); SIGKILL of the live tool kills the server in 0.2 s (`probe-inf-pdeathsig.py`: `F1: server gone +0.2s after SIGKILL`). The replay→live-tool hop has no PDEATHSIG — that is F5, now closed in the tree by the ppid watch.
* **Child dies during the hold.** `_child_running` in the loop (`live:300-302`), `released=False`, and `verify_live(… 'post-witness')` fails the run: `t10-child-dies released=False waited_ms=150`.
* **`nan`, `0`, negative timeouts** are refused (`t11`); on the frozen build a negative value reaches the live tool through the replay and is rejected there — after the 75 MB download (`probe_signals.py`: `negative: replay exit 2 … --witness-timeout must be > 0`), which the tree's early replay check now avoids.
* **Dangling `release` symlink** does not release (`t4`: `released=False waited_ms=500`); `os.path.exists` follows it and finds nothing. The pathological direction is F2.
* **`ready.json` pre-existing as a symlink** is not followed by the write path (`t7`: victim unchanged), because `os.replace` renames over it; only the temp name was dangerous (F1).

## Notes for the lane (not defects)

* On the frozen build the receipt has **no witness block when the hold is interrupted**: `receipt['witness']` is assigned only after `hold_for_witness` returns (`live:1874`). Run A: `setup_error: terminated:signal 15`, `witness: None`, `wd now: ['ready.json']` — a server was published and the receipt never says so. (The tree removes the announcement afterwards, so the observable trace is gone entirely; recording `status: announced` before waiting would keep the receipt truthful.)
* On the frozen build every run leaves `ready.json` behind; the tree removes it, which also means a consumer can no longer re-read it after the replay exits — the counter's post-exit check uses its stored pid/port (`:327-329`), so it is unaffected.
* `waited_ms` alone cannot distinguish "released promptly" from "timeout expired"; the diff adds `timeout_s` and the counter gate `waited_ms > 0`.
* The counter's protection against F2/F3 today is incidental (`mkdtemp` + `rmtree` + `makedirs`), not protocol; any future counter or verifier that reuses a witness dir inherits both holes.

## Evidence index (all under `.ufo/waves/round-49/w1/out/Sen1Witness/`)

| file | what ran | exit |
|---|---|---|
| `evidence/unit-hold.out` | `python3 scripts/unit-hold.py` — 12 unit cases on the frozen tool | 0 |
| `evidence/probe-symlink-fifo.out` | `scripts/probe-symlink-fifo.py` — cross-uid symlink (A), sticky (B), FIFO (C), `ready.json` dir (D) | 0 |
| `evidence/runA-exposure-sigterm.out` | `scripts/runA-exposure-sigterm.py` — real replay: `ss`, `/proc`, as-`nobody`, SIGTERM live tool | 0 |
| `evidence/runBC-orphan-planted-release.out` | `scripts/runBC-orphan-planted-release.py` — B replay SIGTERM, C planted release (+ receipt extract) | 0 |
| `evidence/probe-inf-pdeathsig.out` | `scripts/probe-inf-pdeathsig.py` — `inf` hold + SIGKILL, replay `inf` | 0 |
| `evidence/probe-foreign-ready.out` | `scripts/probe_foreign_ready.py` — H foreign announcement | 0 |
| `evidence/probe-signals.out` | `scripts/probe_signals.py` — Ctrl-C group SIGINT, negative timeout through the replay | 0 |
| `evidence/stale-ready-in-reused-wd.out` | second A run in the same witness dir — stale announcement read at +0.0 s | 1 (the driver crashed on the dead pid; that is the finding) |
| `evidence/validate-patch.out` | `scripts/validate-patch.py` — frozen-tip diff, 9 cases | 0 (9/9) |
| `evidence/probe-worktree-status.out` | `scripts/probe_worktree.py` — W1–W7 on the tree copy | 0 |
| `evidence/worktree-replay-sigterm.out` | replay SIGTERM against the tree — F5 fix | 0 |
| `evidence/validate-worktree-patch.out` | `scripts/validate-patch2.py` — remaining-fix diff, 4 cases | 0 (4/4) |
| `evidence/patched-counter-on-frozen-tip.out` | patched counter, frozen tip | 0 (`met=True`) |
| `evidence/receipts/` | 23 rerun receipts / replay outputs / `ready.json` / planted `release` cited above | — |
| `frozen-tip-74558c71-hardening.diff`, `worktree-r50-hardening.diff` | proposed edits (`a/tools/…` → `b/tools/…`) | both `git apply --check` clean on their base |
| `scripts/` | 10 re-runnable probes/validators (`SEN1_S`, `SEN1_LANE`, `SEN1_WT` to relocate) | — |

Wrote: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/frozen-tip-74558c71-hardening.diff`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/worktree-r50-hardening.diff`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/scripts/` (10 files), `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/Sen1Witness/evidence/` (13 logs + `receipts/` 23 files).
