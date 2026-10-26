# Sen1Live — host-safety review of the b11906 live run (round 46)

**Verdict:** the live run as executed at 19:57:39Z (receipts 1-3, 588 ms end to end) is host-clean
on every axis I could observe — no leaked child, no `/tmp` residue, loopback-only, install
byte-identical to the verified tarball, model pinned pre and post, three distinct proven-owned
ports — but the harness leaves
three medium gaps that the receipts cannot detect — an *optional* `--server` that resolves to
**b11755**, a hash-then-exec window on a user-writable install dir with no post-run re-hash, and
a probe work dir **hardcoded to `/tmp`** that defeats both seats' `TMPDIR=$S` — plus six
low-severity host-safety refinements. Nothing I found requires the run to be redone; every gap
has a receipt assertion or a one-line check that catches it, listed below with a validated patch.

I did not run the server, start or stop any process, or write outside my out dir and scratch.
Executions performed: read-only hashing, one `tar` extraction into my own scratch, module import
plus `--selftest` on a **scratch copy** of the harness (in-process loopback listeners, closed), a
probe against a closed port, and two shell demos of `mktemp` cleanup semantics.

## 1. Findings

Severity = host blast radius × likelihood of an undetectable false record. Line numbers are
`kama-shokunin/tools/kama-llamacpp-live.py` at the working tree (`--server` block 1097,
`main` 1360-1795), unless stated.

| id | sev | site | risk (one line) |
|----|-----|------|-----------------|
| F1 | **medium** | :1097, :1399 | `--server` is optional; the PATH default is **b11755**; the receipt records the digest but nothing fails, so a b11755 run files itself as b11906 evidence |
| F2 | **medium** | :1418-1421, :1500 | binary/tree digest is recorded, never compared; 46 ms hash→exec window on a 0755 owner-writable dir; no post-run re-hash (unlike `model_unchanged`) |
| F3 | **medium** | :84, :813, probe:1128 | probe work dir is `mktemp -d /tmp/...` **regardless of `TMPDIR`**; the allowlist cannot carry `KAMA_PROBE_TMPDIR`, so both seats' `TMPDIR=$S` is defeated |
| F4 | low-med | :1477 | harness log uses `mkstemp` with no `dir=` → `/tmp` whenever a caller forgets `TMPDIR`; a SIGKILLed harness leaves it (0600) |
| F5 | low-med | :863-905, :890 | no process-level post-condition: `port_refuses` is a socket proxy, `proc.wait(5)` then `pass`, pdeathsig best-effort (`prctl_ok: 'unknown'`) |
| F6 | low | :340-373, :1447 | port is picked by `bind(:0)` then released before the child binds; contained by the ownership gate, not eliminated |
| F7 | low | :1491-1498 | child inherits the seat's cwd (a repository root); no `cwd=` and no post-run fleet-root assertion |
| F8 | low | :178, procedure | install procedure has no asset→tree linkage and no clean-dir guarantee; `tar` over an existing dir keeps stale members silently |
| F9 | low | :1456-1457 | `--ctx`/`--threads` forwarded unchecked and no rlimit on the child |

### F1 — the default `--server` executes a *different release*, silently
`p.add_argument('--server', default=None, help='… default: shutil.which("llama-server")')` (:1097);
resolution at :1399; the digest is recorded at :1418 but there is no expected value anywhere in
`build_parser` (:1089-1121). On this host:

```
$ command -v llama-server
/home/vgpnk/.local/bin/llama-server
$ readlink -f /home/vgpnk/.local/bin/llama-server
/home/vgpnk/.local/opt/llama-b11755/llama-server      # sha256 b6a31a8e97615a2a…
$ sha256sum /home/vgpnk/.local/opt/llama-b11906/llama-server
c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff
```

Exploit path: a seat omitting `--server` (it is optional and the help text makes it look safe)
runs b11755; `/health`, `/v1/models`, `/props`, `/metrics`, the probe and teardown all behave
identically, so all eleven v3 checks pass and the receipt is filed as b11906 frontier evidence for
S041/S046/S055.
**Check that catches it:** `receipt.captures.props.fields.build_info == "b11906-4d71b42fd"` and
`receipt.server.install_tree_sha256 == 89fbc38997001c02…` (both are already in the receipts;
receipt-1..3 carry `build_info: "b11906-4d71b42fd"` and `install_tree_sha256`
`89fbc38997001c02fe7daae0fcc32c6aa9e7c585f455d8809ddefe42ed7bdf0f`).
**Smallest remediation:** make `--server` required, or add `--server-sha256` and fail setup on
mismatch.

### F2 — hash recorded, never compared; 46 ms window on a writable install tree
Order in `main`: `server_sha = sha256_file(server_real)` :1418 → `install_tree` :1419 →
`install_links` :1420-1421 → `Popen` :1500. Measured on the installed b11906 tree (lane module,
read-only):

```
sha256_file 0.1 ms; install_tree 45.8 ms (51 files); install_links 0.3 ms
total pre-exec window 46.2 ms
```

`/home/vgpnk/.local/opt/llama-b11906` is `drwxr-xr-x vgpnk` — anything running as this user can
replace `llama-server` or a `libllama*.so` during those 46 ms (or after the run, before the next
round), and the receipt still shows the pre-swap digest. The asymmetry is telling: the *model*
gets a post-run re-hash (`model_unchanged` :1726-1729) but the install tree does not.
**Check that catches it:** (a) the proposed `install_unchanged` check (post-teardown
`install_tree` re-hash, patch hunk 9); (b) cross-seat equality of
`server.install_tree_sha256` between X1Live and X1Replica — same asset, two independent
extractions, so a contaminated install is visible without trusting either seat; (c) an
independent tree comparison against the asset (see F8, run below: 0 mismatches).
**Smallest remediation:** the patch hunks plus `--server-sha256` (F1).

### F3 — every probe writes to `/tmp`, whatever `TMPDIR` says
`CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')` (:84) is used verbatim as the
probe's environment (`subprocess.run(..., env=child_env)` :813-814), but `kama-probe.sh` reads
**only** `KAMA_PROBE_TMPDIR`:

```
$ TMPDIR=$S bash -x tools/kama-probe.sh check --port 9 --expect x --json --timeout 1 --connect-timeout 1
++ mktemp -d /tmp/kama-probe.XXXXXX
+ TMP_ROOT=/tmp/kama-probe.QdEdWi
```

Ten probe invocations per wave (2 per harness run × 3 X1Live + 2 X1Replica runs) each create a
`/tmp/kama-probe.*` dir holding `*.body`, `*.hdr`, `*.err` (:290-292). The trap is
`EXIT INT TERM` (probe :93), and `subprocess.run(timeout=PROBE_TIMEOUT=60)` (:72, :813) kills on
timeout with **SIGKILL**, which the trap cannot catch. Isolated demo (my own dir, removed after):

```
created /tmp/kama-probe.lOGVsv
Killed
SIGKILL-leftover survives: /tmp/kama-probe.lOGVsv
demo cleaned
```

Impact: response bodies from a loopback port (low sensitivity) surviving outside the seat scratch,
against the operator rule that `/tmp` is never evidence and is reaped.
**Check that catches it:** `host-checks.sh pre|post` (`tmp-clean: /tmp/kama-probe.*`; currently
clean because the completed runs' traps fired), or the `bash -x` line above.
**Remediation:** patch hunk 2 — set `KAMA_PROBE_TMPDIR` from the harness temp root.

### F4 — log file location depends on an unset `TMPDIR`
`:1477-1478` `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')` with no `dir=`:

```
$ env -u TMPDIR python3 -c "import tempfile;print(tempfile.gettempdir())"   -> /tmp
$ TMPDIR=$S     python3 -c "import tempfile;print(tempfile.gettempdir())"   -> $S
```

Both seat commands pass `TMPDIR=$S`, and receipts 1-3 record
`teardown.log_path = /fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log`, so this run is
compliant; the residue is a harness SIGKILL (unlink at :1736 never reached) leaving a 0600 log in
`/tmp`.
**Check that catches it:** assert `receipt.teardown.log_path` starts with `$TMPDIR`, plus the
`/tmp` globs above. **Remediation:** patch hunk 7 (`dir=child_cwd`), which also makes log and
child cwd one authority.

### F5 — a leaked child is only *inferred* from the socket
`teardown` (:863-905) signals `killpg` only while `_child_running` (:872, :883), then
`proc.wait(timeout=5)` with a bare `pass` on timeout (:890). The only post-condition is
`port_refuses` (:910) — recorded as `teardown_port_closed` (:1694) and required to be `child`-owned
:1698. A child that survived and dropped its listener, or never bound (loading), would satisfy
neither positively: the receipt would say `port_refuses=True` while a process lives.
`_preexec_pdeathsig` (:456-474) is best-effort and honestly recorded as `prctl_ok: 'unknown'`
(:1498), so a harness SIGKILL is not guaranteed to take the child with it.
Observed now: `pgrep -a llama-server` → exit 1 (none); `ss -ltnp | grep llama-server` → none.
**Check that catches it:** `host-checks.sh pre|post` process/listener lines (must stay
`llama-server-none`) and the proposed `child_gone` receipt check (patch hunk 9).

### F6 — port pick/release race: contained, not eliminated
`pick_port` (:340-373) binds `127.0.0.1:0`, closes, and lets the child re-bind; the receipt
records the caveat (`port_pick_note` :1447-1449). Measured with two barrier-synchronised
processes × 300 rounds (`portrace.py`, my scratch):

```
rounds 300 identical-port rounds 0
```

So concurrent picks do not collide in practice; the wave's own receipts agree — three runs started
19:57:39.317Z, .532Z and .745Z (port picks ~50 ms apart, prior port released each time) took
33179, 46073 and 44923, all proven `child`-owned. What protects the record is the ownership gate —
first HTTP contact proves the listener is an fd of the child (:637-644), otherwise every body is
discarded (:679, :693, :705) and setup fails. The explicit `--port` branch (:352-365) treats any
non-`ConnectionRefusedError` as "free", which still fails closed (the child's bind fails →
`server-exited-early-rc1`).
**Check that catches it:** `receipt.port_refusal_set ⊇ {8080,34113}` and
`port_listener_ownership == 'child'` (receipt-1..3: `[8080, 34113]`, `child`), `ss -ltnp` empty for
that port afterwards, and a registry-coverage audit — `refused_ports()` = `{8080, 34113}` while a
broader "port-ish token" scan of the 37-line `registry/endpoint-consumers.tsv` found no other
port (the one extra hit, `30`, is a comment about `Qwen3-Coder-30B`).
Footnote: `--out` has no lock; two runs sharing one path silently keep the last receipt
(`_emit` :1311-1331 atomic replace). Distinct `--out` per run is required.

### F7 — the child inherits the seat's cwd
`popen_kwargs` (:1491-1498) sets `stdin/stdout/stderr/start_new_session/preexec_fn/env` and **no
`cwd=`**, so `llama-server` runs in whatever directory the seat started in — for this wave, the
fleet root `/home/vgpnk/Projects/shokunin`, which the host guard forbids writing. `--offline`,
`--no-webui`, absolute `--model` keep today's behaviour write-free:
`git -C /home/vgpnk/Projects/shokunin status --porcelain -uall` → one pre-existing sibling edit
(`.scratch/goal-20261026-hyaku-run9.md`, mtime 17:00, after the 16:57 runs), zero new paths.
**Check that catches it:** the `fleet-status` lines of `host-checks.sh pre|post` must match.
**Remediation:** patch hunks 5, 6 and 8 (`cwd=child_cwd`, with the model passed as realpath so a
relative `--model` still works).

### F8 — the install is not linked back to the asset it came from
The item's step (1) is "extract, install the extracted tree at `/home/vgpnk/.local/opt/llama-b11906/`";
`tar` over an existing directory never removes stale members and `install_tree` (:178) hashes
whatever is present. Verified this run (X1Live's tarball, before its scratch was reaped): tarball
`sha256 064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3`, listing 62 entries
(1 dir, 10 symlinks, 51 files; no absolute paths, no `..`, no setuid/setgid bits), and

```
fresh members 51 links 10 / install members 51 links 10
only fresh [] / only install [] / digest mismatches [] / link mismatches {}
```

i.e. `install-verdict MATCH`. `install.txt` and all three receipts agree on
`install_tree_sha256 89fbc38997001c02…`, `install_links_sha256 5cb9f4865c8e1315…`, no unpinned
links.
**Check that catches it:** `host-checks.sh install <tarball> <install-dir>` (exercised on the
b11755 pair: `install-verdict MATCH`, exit 0), run before the live runs; plus the X1Live vs
X1Replica `install_tree_sha256` equality.
**Remediation:** extract into `mktemp -d` under the seat scratch, verify the tree, then move into
place; record both digests.

### F9 — no bound on `--ctx` / `--threads`, no rlimit
`'-c', str(args.ctx)` and `'-t', str(args.threads)` (:1456-1457) are forwarded with only `type=int`
validation; a typo (`--ctx 256000`) sizes a KV cache the host must allocate, and no
`resource.setrlimit` is applied in `_preexec_pdeathsig` (:456). **Check:** assert
`receipt.ctx <= 4096` and `1 <= threads <= os.cpu_count()`. **Remediation:** patch hunks 1 and 4
(`MAX_CTX = 4096`, L1 to confirm the bound).

## 2. Host checks the wave should run (read-only, no server)

`out/Sen1Live/host-checks.sh` — `pre`/`post` write to stdout only (no files, no `/tmp`, no service
calls); `install` extracts the tarball into a `mktemp -d` under `$TMPDIR` and removes it.

```
pre_before_first_run  = bash host-checks.sh pre     # exit 0
post_after_last_run   = bash host-checks.sh post    # exit 0
expected: `diff <(pre) <(post)` empty on every line except `utc`
install_gate          = bash host-checks.sh install <tarball> <install-dir>   # exit 0 => MATCH
```

Exercised output (`out/Sen1Live/pre.txt`): `llama-server-none`, `llama-server-listeners-none`,
`tmp-clean` ×3, `fleet-status-count 1` (pre-existing sibling edit), `model-pin-match yes`,
`server-sha256 c949950e…`, `server-realpath …/llama-b11906/llama-server`,
`refused-ports 8080 34113`. Receipt assertions to add to the wave's review:
`port_listener_ownership == "child"`, `teardown.port_refuses is True`,
`server.install_tree_sha256 == 89fbc389…`, `captures.props.fields.build_info == "b11906-4d71b42fd"`,
`model.sha256 == model_sha256_post == 270cba1b…`, `port_refusal_set == [8080, 34113]`.

## 3. Proposed harness patch (not applied — remediation scope not granted)

`out/Sen1Live/proposed-checks.diff`, against `kama-shokunin/tools/kama-llamacpp-live.py`
(hunk order = file order):

1. `@@ -71` `MAX_CTX` constant (F9).
2. `@@ -809` `run_probe`: pass `KAMA_PROBE_TMPDIR = tempfile.gettempdir()` in the probe env (F3).
3. `@@ -1352` new receipt field `server.install_tree_sha256_post` (F2).
4. `@@ -1406` `main`: `1 <= ctx <= MAX_CTX`, `1 <= threads <= cpu_count` (F9).
5. `@@ -1449` `--model` argv uses `os.path.realpath` so a relative path survives the cwd change (F7).
6. `@@ -1466` `child_cwd = tempfile.gettempdir()`, validated and recorded (F7).
7. `@@ -1475` log `mkstemp(..., dir=child_cwd)` (F4).
8. `@@ -1495` `cwd=child_cwd` in `popen_kwargs` (F7).
9. `@@ -1668` new `child_gone` check + `teardown.child_gone` (F5) and new `install_unchanged`
   check (F2).

Validation of the patch: `patch -p1 --dry-run` and real apply onto a copy → exit 0 and
byte-identical to the edited file; `python3 -m py_compile` ok; `--selftest` ok
(`selftest: ok; closed tcp6 listeners ::1:45371, ::ffff:127.0.0.1:36171`). Hunks 3 and 6 add two
receipt fields and hunk 9 adds two checks — a v3 schema change the L1 must accept before S484/S485
rows model it.

## 4. Not a finding (checked, sound)

`--host 127.0.0.1` (:1454) with `http_get` on `127.0.0.1` (:483-495) and an ownership gate that
only counts *loopback* LISTEN inodes (:413-433) — a wildcard bind is "unproven", not accepted.
`--offline`, `--no-webui`, `--host`, `--port` all exist at b11906 (`common/arg.cpp` 3981, 3499,
3343, 3359 at `4d71b42f`), so the hard-coded argv cannot fail on an unknown flag. Refused ports are
re-derived from the registry on every run and fail closed if it is unreadable (:315-337). Child env
is an allowlist, so proxy/`HF_`/`SSL_*` variables and `LD_PRELOAD` never reach the server. Receipts
are written 0600 and atomically; no `.kama-live-*` sibling survives today.

## 5. Tooling and scratch

No tool installed, upgraded or fetched (pacman untouched). Scratch `/fast/scratch/hyaku/kama-r46/Sen1Live`
created and removed at the end; every artifact cited from it was copied into the out dir first.

## 6. Absolute paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live/host-checks.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live/proposed-checks.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live/pre.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live/install-check-b11755.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/Sen1Live/portrace.py`
