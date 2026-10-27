# Sen2Scratch — round-52 scratch discipline audit (C1, C2, kama-live-replay, kama-llamacpp-live)

**Verdict:** C2 is scratch-clean and both counters' own bodies honour `TMPDIR`/`--scratch`, but C1's operative path still creates `/tmp/kama-probe.XXXXXX` (4 directories per run, files `m<port>.{body,err,hdr}`) because the live tool's probe child never receives a scratch variable under the one name the probe reads, and a read-only `/tmp` flips C1 from `met=True` to `bind=0/3 met=False` while `TMPDIR`/`--scratch` stay writable and used — one defect (medium, carried from round-46 w1 Sen1Live F3, still open), with a one-line fix validated end-to-end (C1 `met=True`, 0 `/tmp` paths, read-only `/tmp`).

Axes: **operability** — claim C1 silently depends on `/tmp` writability outside its declared isolation; **calibration** — no claim value changed: at tip `5dacf2c7` with `TMPDIR` set, C1 `bind=1 sealed=1 teardown=1 newrow=1 met=True` (exit 0) and C2 `fixture=1 lane=1 corr_lost=0 met=True` (exit 0), both re-derived by me; no lane, counter, preregistration or control file was edited.

---

## 1. Scope and setup

| item | value |
|---|---|
| lane (read-only) | `/home/vgpnk/Projects/shokunin/kama-shokunin` |
| clone used for `--repo` | `$S/lane` = `git clone --shared` (toplevel verified = `$S/lane`; 385 MB; HEAD `34d82600`) |
| scratch | `S=/fast/scratch/hyaku/kama-r52/Sen2Scratch`, marker `$S/marker` (2026-10-27T05:08:05Z) |
| TMPDIR under audit | `$S/t` |
| tips | frozen claims `8551ba7f`, build `5dacf2c7` (both ancestors of `5dacf2c7`; `git merge-base --is-ancestor` ok), base `9ff76b1f` |
| tool identity | the four files at `5dacf2c7` are byte-identical to the worktree (`git show <tip>:<f> \| sha256sum` = `sha256sum <f>` for all four) |
| counters run from | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/…`, cwd = fleet root |
| network | github.com 200 (0.10 s), huggingface.co 200 (0.04 s) |
| sandbox | `bwrap 0.13.1`: `bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp` — fresh empty tmpfs on `/tmp`, same uid, shared network; so every `/tmp` path a counter writes is attributable to it |
| installs | none (no pacman per host guard; nothing was needed) |

The `--dev /dev` flag is required only for the audit: without it an unprivileged namespace's inherited `/dev/null` returns `Permission denied` (`git` aborts), a property of device nodes in a user namespace, not of the tools.

**Watcher validity (positive control):** C2 run inside the namespace with no `TMPDIR` produced `/tmp/r52c2-5m5pm951` + 10 children (peak 11 paths, `ns-no-tmpdir-peak-uniq.txt`); with `TMPDIR` set the same run produced **0** paths (`ns-with-tmpdir-peak-uniq.txt`). So the watcher does see real writes, and "0 paths" is not a broken measurement.

## 2. Static inventory (assigned greps)

Commands:

```
grep -n -E '/tmp|mkdtemp|TMPDIR|tempfile|gettempdir|mktemp' <the four tools>
grep -n -E "['\"]/tmp|/tmp/|tmpdir|tempdir"            <the four tools>
grep -n 'var/tmp|dev/shm|/run/user'                    <the four tools>
```

Hardcoded `/tmp` in the four tools: **none**. `/var/tmp`, `/dev/shm`, `/run/user`: **none**. `mkdtemp` without `dir=`: **none**.

| site | code | verdict |
|---|---|---|
| `round52-replay-memfd-audit.py:587-589` | `root = a.scratch or tempfile.gettempdir()`; `S = tempfile.mkdtemp(prefix="r52c1-", dir=root)` | OK (`dir=`); root unvalidated, see F3 |
| `round52-replay-memfd-audit.py:395-398` | per-receipt `HOME`, `XDG_CACHE_HOME`, `TMPDIR` = `$S/{home,tmp}-<tag>` | OK — isolation is explicit |
| `round52-replay-memfd-audit.py:601` | `tf.extractall(tree, filter=… symlinks/hardlinks refused)` inside `S` | OK |
| `round52-replay-memfd-audit.py:642-643` | `finally: shutil.rmtree(S, ignore_errors=True)` | OK on normal exit; see O3 |
| `round52-append-restore-check.py:508-510` | `root = a.scratch or tempfile.gettempdir()`; `mkdtemp(prefix="r52c2-", dir=root)` | OK; F3 applies |
| `round52-append-restore-check.py:539-540` | `finally: rmtree(S)` | OK |
| `kama-live-replay.py:137,375` | `env["TMPDIR"] = os.path.join(work, "tmp")`, `os.makedirs(...)` | OK — live child is confined to `--work` |
| `kama-live-replay.py:462,696` | `mkdtemp(prefix="klr-st-", dir=root)`, `root = a.scratch or gettempdir()` | OK |
| `kama-live-replay.py:214-223` | archive extracted into `--work`; `sealed_member()` fills the memfd from the tar stream (no disk copy of the server) | OK (round-52 design is scratch-frugal) |
| `kama-llamacpp-live.py:1499-1500` | `tempfile.TemporaryDirectory(prefix='kama-install-selftest-')` — **no `dir=`** | F2 |
| `kama-llamacpp-live.py:1579` | `TemporaryDirectory(prefix='kama-live-prov-')` — **no `dir=`** | F2 |
| `kama-llamacpp-live.py:1703` | `TemporaryDirectory(prefix='kama-emit-selftest-')` — **no `dir=`** | F2 |
| `kama-llamacpp-live.py:1971-1972` | `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')` — **no `dir=`** | F2 (unlinked at `:1254` and `:2251-2254`) |
| `kama-llamacpp-live.py:1547,1552` | `os.symlink(tempfile.gettempdir(), …)` | benign: a path string inside the selftest dir, no write to it |
| `kama-llamacpp-live.py:126,1140-1152` | `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')`; `run_probe(...)` → `bash kama-probe.sh check … env=child_env` | **F1**: the allowlist cannot carry `KAMA_PROBE_TMPDIR` |
| `tools/kama-probe.sh:1128` (transitive dep of C1) | `TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX")` | **F1**: ignores `TMPDIR` entirely |

## 3. Dynamic results

All counters: `--repo $S/lane --tip <full>`; "paths" = distinct `/tmp` paths seen by a 0.1–0.2 s poller inside the namespace.

| # | run | exit | claim line | `/tmp` paths created |
|---|---|---|---|---|
| 1 | C1, host, `TMPDIR=$S/t`, no `--scratch` | **0** | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` | 14 × `/tmp/kama-probe.*` (polled); also 3 × `/tmp/tmp.*` that are **not** ours (absent in ns runs) |
| 2 | C1, ns, `TMPDIR=$S/t` | **0** | `met=True` (same legs) | 4 × `/tmp/kama-probe.<6>` each with `m<port>.{body,err,hdr}`; residue after exit **0** |
| 3 | C1, ns, `TMPDIR=$S/t --scratch $S/t`, **`/tmp` read-only** | **1** | `bind=0 sealed=1 teardown=1 newrow=1 bound=0/3 met=False`, `bind b1..b3: replay exit 1 match False` | 0 (nothing can be written) |
| 4 | C1, ns, **`/tmp` read-only**, probe patched (fixture commit `3753f28b`) | **0** | `bind=1 sealed=1 teardown=1 newrow=1 met=True` | **0** |
| 5 | C2, host, `TMPDIR=$S/t` | **0** | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` | 0 |
| 6 | C2, ns, `TMPDIR=$S/t` | **0** | `met=True` | 0 |
| 7 | C2, ns, **no `TMPDIR`** (positive control) | **0** | `met=True` | peak 11: `/tmp/r52c2-5m5pm951/*` |
| 8 | C2, ns, `TMPDIR=/nonexistent-Sen2Scratch` | **0** | `met=True` | peak 1: `/tmp/r52c2-h3hd06hr` (silent fallback) |
| 9 | `kama-llamacpp-live.py --selftest`, ns, no `TMPDIR` | **0** | `selftest: ok` | sampled 5: `/tmp/kama-live-prov-35_rthw9/*` |
| 10 | same, `TMPDIR=$S/t` | **0** | `selftest: ok` | 0 |
| 11 | `kama-live-replay.py --selftest --scratch $S/t`, ns | **0** | `KLR_SELFTEST pass=31 fail=0` | 0 |
| 12 | same, no `--scratch`, no `TMPDIR`, ns | **0** | `pass=31 fail=0` | 61: `/tmp/klr-st-a_m1jxzx/*` |

Post-run hygiene (after every run):

```
find /tmp -maxdepth 1 -newer $S/marker -user $USER      # 9 entries, all other seats'/harness:
  msdk_req.txt, uv-setuptools-*.lock, w5-mado-m52-selftest.{N3CRkQ,mXIFQV,j6a2TM,qoP0Qm},
  claude-1000, omp-worker-stderr-plq23v, hsperfdata_vgpnk
grep -E 'r52c1-|r52c2-|klr-st-|kama-probe\.|kama-llamacpp-live-|kama-live-|work-b[0-9]|wd-b[0-9]|tmp-b[0-9]|canary-' → none
ls -d /tmp/kama-probe.*                                 → none (probe trap cleaned up)
pgrep -af '(^|/)llama-server( |$)'                      → none
git -C $S/lane status --porcelain                       → clean (counters are read-only on --repo)
find /home/vgpnk/Projects/shokunin -maxdepth 1 -newer $S/marker → nothing
```

So, answering the assigned question directly: **C2 lands nothing in `/tmp`** (0 paths, host and ns); **C1 lands 4 `/tmp/kama-probe.*` directories per run and removes them again**; nothing from either counter *remains* in `/tmp`, and none of the counters' own bodies touched `/tmp` — the writes come from the probe child.

What the counters did put under `TMPDIR=$S/t` during a C1 run (polled, then removed at exit): `r52c1-*/{tree, counter-model.gguf, work-b1..3, tmp-b1..3, home-b1..3, canary-b1..3, wd-b1..3, b1..3.json/log, kill.log}` — i.e. the 75 MB-per-replay downloads, the extracted tree and the whole replay environment stayed in scratch.

## 4. Findings

### F1 (medium, carried from round-46 w1 Sen1Live F3 — still open) — C1's probe writes `/tmp` regardless of `TMPDIR`/`--scratch`

* Where: `tools/kama-probe.sh:1128` (contract: `TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX")`) reached from `tools/kama-llamacpp-live.py:1151` (`subprocess.run(argv, …, env=child_env)`) with `child_env` allowlisted by `kama-llamacpp-live.py:126` (`CHILD_ENV_KEYS` — `TMPDIR` yes, `KAMA_PROBE_TMPDIR` no). The probe never consults `TMPDIR`, so the live child's `TMPDIR=<work>/tmp` (`kama-live-replay.py:137`) is dropped for the probe subtree.
* Show it:
  * writable `/tmp`: `c1-ns-tmp-peak-uniq.txt` — 4 probe dirs, contents `m<port>.body/.err/.hdr`; host poll caught 14 (`c1-host-tmp-poll-uniq.txt`).
  * read-only `/tmp`, writable `TMPDIR`+`--scratch`:
    `bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp --remount-ro /tmp sh -c 'TMPDIR=$S/t python3 tools/round52-replay-memfd-audit.py --repo $S/lane --tip 5dacf2c7… --scratch $S/t'` → `bind=0 sealed=1 teardown=1 newrow=1 bound=0/3 met=False` (exit 1), every leg `replay exit 1 match False`; probe alone: `mktemp: failed to create directory via template '/tmp/kama-probe.XXXXXX': Read-only file system`, `probe-exit=1`.
* Impact: C1's predicate cannot be met on a host with a read-only, full, noexec-probe or reaper-swept `/tmp` although the counter's declared scratch is writable — a false negative for operability, and a `/tmp` write the counter's isolation explicitly claims not to make (`round52-replay-memfd-audit.py:29`). On this host `/tmp` holds 331,759 entries. Secondary: `kama-probe.sh:92-93` traps `EXIT INT TERM` only, so a `SIGKILL` of a running probe (the C1 counter `reap()`s with `SIGKILL`, and the teardown leg kills the invoker) leaves `/tmp/kama-probe.*` behind — **[INFERENCE]**, not observed in any run (residue 0 each time).
* Smallest remediation (validated, `proposed-F1-probe-tmpdir.diff`):

```diff
--- a/tools/kama-probe.sh
+++ b/tools/kama-probe.sh
@@ -1125,7 +1125,7 @@ main() {
   if [ "$HAVE_PY" -eq 0 ]; then
     warn "python3 not found — using grep fallbacks for JSON-pointer and model-id parsing"
   fi
-  TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX")
+  TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}/kama-probe.XXXXXX")
```

  Validation: patched in `$S/lane`, committed there with a fixture identity (`git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit`, toplevel asserted = `$S/lane`), fixture commit `3753f28b`; the frozen C1 counter at that tip under **read-only `/tmp`** returns `bind=1 sealed=1 teardown=1 newrow=1 met=True` (exit 0) with **0** `/tmp` paths (`c1-fix-ro-tmp.txt`, `c1-fix-ro-tmp-peak-uniq.txt` is 0 bytes). The probe then uses the live child's `TMPDIR=<work>/tmp`, inside the replay work dir.

### F2 (low) — the live tool's own temp trees resolve through the ambient `TMPDIR` and it has no `--scratch`

* Where: `kama-llamacpp-live.py:1499-1500`, `:1579`, `:1703` (`TemporaryDirectory(...)` without `dir=`) and `:1971-1972` (log `mkstemp` without `dir=`).
* Show it: `kama-llamacpp-live.py --selftest` in the namespace with no `TMPDIR` → sampled `/tmp/kama-live-prov-35_rthw9/{rel,a.tar.gz,many.tar,sparse.tar.gz}` (`st-live-selftest-notmpdir-peak-uniq.txt`); with `TMPDIR=$S/t` → 0 paths (`st-live-selftest-tmpdir-peak-uniq.txt`). The two shorter-lived trees (`kama-install-selftest-`, `kama-emit-selftest-`) are reached from the same `--selftest` path (`:1633-1634` calls, `:1633`/`:1634`), so they also resolve to `gettempdir()` — sampler timing, not absence, explains that only one name was caught (`0.1 s` poll).
* In the counter path this is harmless (the replay always exports `TMPDIR=<work>/tmp`, `kama-live-replay.py:137`); it bites only on direct invocation with `TMPDIR` unset. The L1's build battery happened to be confined because `measured/measure.sh:11` does `export TMPDIR="$S"` before `run live-selftest …` (`live-selftest-build.out:1` passes no `TMPDIR` itself). `mkstemp`'s log is unlinked on every path I can reach (`:1254` in `teardown`, `:2251-2254` at the end, `FileNotFoundError` tolerated); a `SIGKILL` would leave `kama-llamacpp-live-*.log` behind — **[INFERENCE]**.
* Fix (optional): pass `dir=os.environ.get('TMPDIR')` explicitly, or give the live tool the replay's `--scratch` and use it for all four sites.

### F3 (low) — the scratch root is neither validated nor normalised

* Where: `round52-replay-memfd-audit.py:587`, `round52-append-restore-check.py:508` (`root = a.scratch or tempfile.gettempdir()`), `kama-live-replay.py:696`.
* (a) relative `--scratch` writes into the cwd: `cd $S/relcwd && python3 …/round52-append-restore-check.py --repo $S/lane --tip 5dacf2c7… --scratch rel` → exit 0, `met=True`, and a residue directory `./rel` is left in the cwd (`find . -maxdepth 2` → `./rel`). With cwd = the fleet root — the documented start directory — that is a write outside the seat's scratch and a host-guard violation waiting to happen.
* (b) a mistyped scratch is silently ignored: `TMPDIR=/nonexistent-Sen2Scratch` → `tempfile.gettempdir()` skips it, `met=True`, and the run's scratch appears at `/tmp/r52c2-h3hd06hr` (peak 1 path). No warning, and for C1 that is ~300 MB in `/tmp`.
* Fix: `root = os.path.abspath(a.scratch) if a.scratch else tempfile.gettempdir()`, then refuse (exit 2) when `root` is not a writable directory or lies inside `--repo` / the fleet root.

### Observations (not defects)

* **O1** Round-52's memfd design is scratch-frugal by construction: `sealed_member()` (`kama-live-replay.py:223`) fills the memfd from the archive's tar stream and the server runs from `/proc/<pid>/fd/N`, so no extra disk copy exists to be confused with the image (matches the `sealed` legs I re-derived: seals 15, nlink 0, `/memfd:` link, frozen digest, for b1–b3).
* **O2** Counter exit-code discipline held: 0 met, 1 not met, and the read-only-`/tmp` failure surfaced as exit 1 with named legs, not a traceback.
* **O3** Neither counter installs a signal handler (`grep -n 'signal.signal|SIGTERM|SIGINT|atexit'` → no hits in either), so an interrupted run skips the `finally` `rmtree` and leaves `S` (up to ~300 MB of downloads for C1) in scratch. Scratch-local, `/tmp`-free; a `SIGTERM` handler that removes `S` and reaps would close it.
* **O4** `--repo` read-only discipline holds: `git -C $S/lane status --porcelain` empty after ten counter runs, and the fault-injected read-only-`/tmp` run also left it clean (fixture repos are `git init`ed under `S/fx-*`, `round52-append-restore-check.py:356-372`, with `-c user.name=r52c2-fixture -c user.email=r52c2@invalid -c commit.gpgsign=false` on every command, `:99`).

## 5. Consequence for the wave

* No claim moves: C1 and C2 are `met=True` at `5dacf2c7` under the prescribed `TMPDIR` (runs 2 and 6; same values as `measured/c1-build.out`, `measured/c2-build.out`). Nothing here contradicts the build receipts.
* The C1 *witness* is unaffected (the memfd legs stay `sealed=1` even with a read-only `/tmp`, run 3), so the wave's claim is intact; what fails is operability on hosts whose `/tmp` the counter does not control. F1's one-line probe patch removes that dependency and is the only change I would ask integration to carry (round 53).
* By this audit, nothing was written to the lane, the fleet root, sibling lanes or the counters. `$S` (clone included) was removed at the end; the only paths I wrote are this report and its out directory. Note for the integrator: the lane worktree already shows other seats' in-flight edits (`git status`: `M corpus/QUALITY.md corpus/SOURCES.md tests/llamacpp-live/check-receipt.py tools/kama-live-replay.py`) — not mine; every `file:line` above is anchored to the bytes of tip `5dacf2c7` (`git show 5dacf2c7:<f>`), which is what the counters extract, so later worktree edits do not move these citations.

## 6. Reproduction

```sh
S=/fast/scratch/hyaku/kama-r52/Sen2Scratch
git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
TIP=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
CNT=/home/vgpnk/Projects/shokunin/kama-shokunin/tools
# host, TMPDIR only
TMPDIR=$S/t python3 $CNT/round52-replay-memfd-audit.py --repo $S/lane --tip $TIP --out $S/c1.out   # exit 0
TMPDIR=$S/t python3 $CNT/round52-append-restore-check.py --repo $S/lane --tip $TIP                # exit 0
# namespace (attributable /tmp), writable and read-only
sh $S/c1-ns.sh                                                                                    # 4 /tmp/kama-probe.*
bwrap --bind / / --dev /dev --proc /proc --tmpfs /tmp --remount-ro /tmp \
  sh -c 'TMPDIR='"$S"'/t python3 '"$CNT"'/round52-replay-memfd-audit.py --repo '"$S"'/lane --tip '"$TIP" --scratch '"$S"'/t'   # exit 1 met=False
# patched probe, fixture commit in the clone only
git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -qam 'fixture: probe TMPDIR'       # -> 3753f28b
bwrap … --remount-ro /tmp sh -c 'TMPDIR='"$S"'/t python3 '"$CNT"'/round52-replay-memfd-audit.py --repo '"$S"'/lane --tip 3753f28b…'  # exit 0, 0 paths
```

## 7. Deliverables

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen2Scratch/` — 33 receipts + `SHA256SUMS` (`sha256sum -c` clean): `c1-host.{txt,out}`, `c1-host-tmp-poll-uniq.txt`, `c1-host-scratch-poll-uniq.txt`, `c1-ns.{txt,out}`, `c1-ns-tmp-peak-uniq.txt`, `c1-ro-tmp.{txt,out}`, `c1-fix-ro-tmp.{txt,out,log}`, `c1-fix-ro-tmp-peak-uniq.txt` (0 bytes = 0 `/tmp` paths), `c2-host.txt`, `ns-{no,with}-tmpdir.txt`, `ns-no-tmpdir-peak-uniq.txt`, `ns-with-tmpdir-peak-uniq.txt`, `c2-ghost-tmpdir-peak-uniq.txt`, `st-{live,klr}-selftest-{notmpdir,tmpdir}{,.txt}`/`-peak-uniq.txt`, `find-tmp-newer.txt`, `proposed-F1-probe-tmpdir.diff`, and the four audit drivers `c1-driver.sh`, `c1-ns.sh`, `c2-ns.sh`, `st-ns.sh`.
