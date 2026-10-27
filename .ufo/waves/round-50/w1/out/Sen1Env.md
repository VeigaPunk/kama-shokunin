# Sen1Env — round 50 environment-injection battery against the built replay+live chain

**Verdict:** the round-50 build does isolate the *live tool* and the *server* (14/14 vectors: the server and its parent carry exactly `PATH HOME LANG [LC_ALL] TMPDIR`, never the planted canary, never `PYTHONPATH`/`LD_*`/`XDG_*`/`BASH_ENV`; `-I`+`-P`+`-s` kill `PYTHONPATH`, `PYTHONSTARTUP`, `XDG_CONFIG_HOME`, user-site `.pth`/`usercustomize`, script-dir and cwd `sitecustomize`; the counter's own `sitecustomize` marker stayed empty in every run) — **but the live tool hands `PATH` and `HOME` on to `tools/kama-probe.sh`, which resolves `bash`, `python3`, `curl` and `ss` through that `PATH` and runs `python3` without `-I`**, so five vectors execute code *inside* the replay, and one of them replaces the receipt's two probe rows and the fresh `match=True` still holds. Second, independent defect: `model_mapping`'s dev equality is a false negative on btrfs, which flips the frozen counter's verdict (`met=True` on `/fast`, `met=False` on `/home`, same tip, correct chain).

Measured at tree `97c864bead3ee4a2f629574e77263d33834ec98a` (`git archive` of the lane clone, identical to HEAD for the three tools), receipt `.ufo/waves/round-48/c2/live/receipt-1.json`, every replay witnessed (`--witness-dir`), environment built exactly as the frozen C1 counter builds it (`round50-replay-bind-audit.py:376 prepare_env`: `PASS_ENV` + scratch `HOME`/`XDG_CACHE_HOME`/`TMPDIR` + `KAMA_R50_CANARY` + `PYTHONPATH`→`sitecustomize` marker), started through the same `python3 -I -c` invoker.

## Method

```
S=/fast/scratch/hyaku/kama-r50/Sen1Env
O=<lane>/.ufo/waves/round-50/w1/out/Sen1Env
git clone --shared <lane> $S/lane && git -C $S/lane archive 97c864be | tar -x -C $S/tree
python3 $O/sen1env_battery.py --tree $S/tree --receipt <lane>/.ufo/waves/round-48/c2/live/receipt-1.json \
        --outdir $O --workroot $S/work --vector <V> --hold 1
```
`sen1env_battery.py` adds one injection per run, waits for `ready.json`, then while the server is held snapshots **every descendant of the invoker** (`/proc/<pid>/{stat,comm,cmdline,exe,environ,maps}`), releases, and reads the replay JSON, the rerun receipt and every marker file. Records: `runs/<V>/<V>.json` (record), `replay.json`, `rerun-receipt.json`, `invoker.log`, marker files. Aggregate: `table.tsv`, `summary.json`, `summary.out`.

## Vector table (receipt-1, 14 runs, all `match=True exit=0`, witness pid == rerun `child_pid` 14/14)

| # | injects | live/server env seen | fired? | evidence |
|---|---|---|---|---|
| V0 | counter baseline (control) | `HOME LANG PATH TMPDIR` | no | — |
| V1 | `PYTHONSTARTUP=<marker.py>` | same | **no** (`-I`/`-E`, non-interactive) | `runs/V1-pythonstartup/` |
| V2 | `XDG_CONFIG_HOME` with `python/{sitecustomize,usercustomize}.py`, `pythonrc` | same (key dropped) | **no** | `runs/V2-xdg-config/` |
| V3 | `HOME` with `.local/lib/python3.14/site-packages/{zz-sen1env.pth,usercustomize.py}` | same | **YES — 12 lines** | `runs/V3-home-pth/mark-home.txt` |
| V4 | `PATH` head with `python`/`python3`/`python3.14` wrappers | same | **YES — 6 lines** | `runs/V4-path-python/mark-pathpython.txt` |
| V5 | `PATH` head with a `bash` wrapper | same | **YES — 2 lines** | `runs/V5-path-bash/mark-pathbash.txt` |
| V6 | `LD_PRELOAD=<constructor .so>` + `LD_LIBRARY_PATH` | same (both keys dropped) | only **invoker + replay** (2 pids), never live/server | `runs/V6-ld-preload/mark-ld.txt` |
| V7 | `LC_ALL=LANG=en_US.utf8` | `HOME LANG LC_ALL PATH TMPDIR` | no code; no output change | `runs/V7-locale-utf8/` |
| V8 | `TMPDIR=<hostile dir with sitecustomize.py>` | `TMPDIR=<work>/tmp` (override wins) | **no** | `runs/V8-tmpdir/` |
| V9 | `sitecustomize.py` planted in the live tool's script dir **and** cwd | same | **no** (`-I`⇒`-P`) | `runs/V9-scriptdir/` |
| V10 | `BASH_ENV=ENV=<marker.sh>` | same (keys dropped) | **no** | `runs/V10-bashenv/` |
| V11 | `LC_ALL=LANG=tr_TR.utf8` (not generated here) | `… LC_ALL …` | no code; **bash `setlocale` warning lands in `probes[].stderr_tail`** | `runs/V11-locale-bogus/rerun-receipt.json` |
| V12 | `PATH` head with a `bash` that answers both probe calls itself | same | **YES — receipt's probe rows are the wrapper's literals** | `runs/V12-path-bash-forge/` |
| V13 | `PATH` head with a `curl` wrapper | same | **YES — 4 probe requests pass through it** | `runs/V13-path-curl/mark-curl.txt` |

Counters over all 14: `match=True` 14, canary key present in live/server 0, `sitecustomize` canary marker non-empty 0, server `TMPDIR` always `<work>/tmp`.

## F1 (medium) — `PATH` is handed on, and the probe resolves `bash`/`python3`/`curl`/`ss` through it

- `tools/kama-live-replay.py:88` `LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")`; `tools/kama-llamacpp-live.py:125` `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')`, applied at `:1858`.
- `tools/kama-llamacpp-live.py:1061` `argv = ['bash', str(probe), 'check', …]` (no absolute path) run at `:1067` with `env=child_env`.
- `tools/kama-probe.sh:82` `command -v python3`, bare `python3` at `:184,:338,:404,:432,:620,:1071`; `ss` at `:246`; `curl` at `:294,:326`.
- The frozen counter feeds that `PATH` itself: `round50-replay-bind-audit.py:113 PASS_ENV` includes `PATH`. Its env leg only tests the canary key and the `PYTHONPATH` marker.

Exploit path (measured, not theoretical): a caller whose `PATH` starts with an attacker directory (CI image, wrapper shim, a stale `~/.local/bin`) gets code execution as a descendant of the live tool, inside the witness window, with the live tool's `PATH/HOME/TMPDIR` and its full argv readable from `/proc/<ppid>/cmdline` (the `--out` receipt path and the `--witness-dir`).

Evidence:
- `runs/V12-path-bash-forge/rerun-receipt.json` — both probes: `argv` still names the real `…/tools/kama-probe.sh`, `probe.sha256` is the real probe digest, `exit 0/2`, and `result` is byte-for-byte the wrapper's literal `{"rows":[{"verdict":"MODEL_OK","reason":"matched"}]}` / `MODEL_MISMATCH/served-id-mismatch`; `probe_model_ok=True`, `probe_mismatch=True`, replay `match=True`. `mark-forge.txt` records the live tool's whole command line read from `/proc/$PPID/cmdline`.
- `runs/V5-path-bash/mark-pathbash.txt` — the two `bash <probe> check …` invocations, answered by the wrapper.
- `runs/V13-path-curl/mark-curl.txt` — the probe's four HTTP calls (`/v1/models` body fetch, `/health`) pass through a `PATH`-supplied `curl`, so even the probe's *inputs* are interceptable.
- `c1-forge-path.stdout` — **the frozen counter run with the forging `PATH` reports `bind=1 teardown=1 newrow=1 bound=3/3 met=True`** while its own `c1-forge-marker.txt` shows all 8 probe invocations (3 receipts × 2 + teardown) were answered by the wrapper. The counter's own nonce/exe/listen/mapped join is untouched and still passes; what is not bound is the receipt's probe evidence, and the env leg cannot see the channel.

Smallest remediation: stop resolving names through an inherited `PATH` — in `kama-live-replay.py:112 live_env` set `env['PATH'] = '/usr/bin:/bin'` (the server is executed by absolute path and the probe needs only system `curl`/`ss`/`python3`), and invoke the probe with an absolute interpreter (`/usr/bin/bash`) at `kama-llamacpp-live.py:1061`. (If the canonical fix must stay inside the counter: `PASS_ENV` should not carry `PATH` — but the defect is in the tool, which advertises "isolated".)

## F2 (medium) — `HOME` is handed on, and the probe's `python3` is not isolated

`kama-probe.sh` runs `python3` without `-I`/`-s` and the live tool passes `HOME` (`kama-llamacpp-live.py:125,:1858`). A `.pth` or `usercustomize.py` in `$HOME/.local/lib/python3.14/site-packages` therefore executes in every replay.

Evidence (`runs/V3-home-pth/mark-home.txt`, 12 JSON lines), one interpreter:
```
{"via": "pth", "pid": 3618012, "ppid": 3617969, "argv": ["-", "/tmp/kama-probe.p2yx92/m42303.body"],
 "cwd": "…/tree", "isolated": 0, "no_user_site": 0,
 "env_keys": ["HOME","LANG","PATH","PWD","SHLVL","TMPDIR","_"]}
```
`isolated: 0`, `no_user_site: 0`, parent = the probe's `bash`, argv = the probe's own `python3 - <body>`. Replay still `match=True`; probe rows still credited to the real probe digest. This is the same class as the round-49 R1 hijack the build claims to close ("a PYTHONPATH/sitecustomize hijack of the inherited environment met the counter") — closed for the live tool, open for the probe through `HOME` and `PATH`.

Smallest remediation: `python3 -I` at every `kama-probe.sh` call site (one `PY='python3 -I'` variable), and set `HOME` in `live_env` to the per-run scratch home (the counter already does that for itself; the tool should not rely on it).

## F3 (medium, measurement validity) — `model_mapping` dev equality is a false negative on btrfs

`tools/kama-llamacpp-live.py:710-713` compares the `dev` field of the `/proc/<pid>/maps` line with `stat().st_dev` and returns `mapped:False, reason:'mapped-file-is-not-the-model-path'`; the frozen counter repeats the same comparison at `round50-replay-bind-audit.py:333`. On this host's btrfs subvolume mount `/home` (`/dev/mapper/root[/@home]`) the maps dev is `00:1e` (the block device) while `stat` reports `00:38` (the subvolume's anonymous dev) **with the same inode** for every file; `/fast` (xfs) agrees.

Evidence:
- `btrfs_maps_dev.out` — one script: `…/out/Sen1Env/runs/V0-baseline/replay.json` and the lane `README.md` → `maps dev 00:1e ino 238208440` vs `stat dev 00:38 ino 238208440` (DIFFER); `/fast/…/tree/README.md` → equal.
- `findings/btrfs-model-mapping/rerun-receipt-btrfs.json` — `{"mapped": false, "reason": "mapped-file-is-not-the-model-path", "dev": "00:1e", "inode": "238208361", "path_dev": "00:38", "path_inode": "238208361"}`; the xfs twin is `mapped: true`.
- Paired frozen-counter control, same clone, same tip `97c864be`, run ~16 s each:
  - `c1-fast-scratch.stdout` → `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (mapping dev `103:05`).
  - `c1-home-scratch.stdout` → `bind=0 teardown=1 newrow=1 bound=0/3 met=False`, every leg: `no mapping of pid N is a file hashing to the frozen model (24 file mappings)` + `rerun model_mapping {… 'path_dev':'00:38', 'dev':'00:1e' …} does not record the observed mapping None`.

Impact: C1's bind leg — and therefore the preregistered claim — is a function of the filesystem that hosts `--scratch`/`TMPDIR`, not of the chain. The failure text (`mapped-file-is-not-the-model-path`) is indistinguishable from the round-49 R1 defect the leg exists to catch, so a btrfs-hosted rerun would report the *exact* failure it is meant to detect on a fully correct chain. L1's own dry runs were on `/fast`, so the claim stands where it was measured; any later rerun on `/home`, `/tmp`-on-btrfs or a btrfs root would report `met=False`.

Smallest remediation: bind on the maps *pathname* (already equal to the resolved `--model` path) plus `st_ino` plus the sha256 of the opened file; keep `dev` as a recorded observation, and use it only when it agrees. Drop the `dev` conjunct at `kama-llamacpp-live.py:711` (same at `round50-replay-bind-audit.py:333` — the counter is frozen, so this is a next-round item; until then C1's own receipt should record the scratch filesystem alongside the verdict).

## F4 (low) — the probe's temp dir ignores the isolated `TMPDIR`

`tools/kama-probe.sh:1128` `TMP_ROOT=$(mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX")`. The live tool sets `TMPDIR=<work>/tmp` for the probe, but every probe body still lands in shared `/tmp` — visible in `runs/V4-path-python/mark-pathpython.txt` and `runs/V13-path-curl/mark-curl.txt` (`/tmp/kama-probe.edelf3/m46281.body`). The isolated `TMPDIR` is defeated for probe state; from F1/F2 hostile code can also pre-seed `/tmp/kama-probe.*` names. Fix: `"${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}"`.

## Measured clean (no finding)

- **Canary never reaches the chain:** `KAMA_R50_CANARY` absent from the live tool's and the server's `/proc/<pid>/environ` in 14/14; present only in the replay itself, which is the invoker's child (inheritance by design, and the invoker is the counter's own process). The counter's own test (`round50-replay-bind-audit.py:354-358`) is key membership (`environ_keys` then `canary in keys`); this battery searched whole environs for the canary *value* as well — 0 hits outside the replay. The counter's `PYTHONPATH` `sitecustomize` marker stayed empty in 14/14 — the replay's and live tool's `-I` are real (`sys.flags.isolated` on the probe's interpreter is 0, which is exactly F2).
- **`-I` ⇒ `-E`/`-s`/`-P` holds:** `PYTHONPATH`, `PYTHONSTARTUP`, `PYTHONHOME`-style names, `XDG_CONFIG_HOME`, `~/…/site-packages/*.pth` **for the live tool**, and a `sitecustomize.py` planted in the live tool's own script dir or cwd are all inert (V1, V2, V9; the V3 marker belongs to the probe, not the live tool).
- **`LD_PRELOAD`/`LD_LIBRARY_PATH`/`LD_AUDIT` are dropped for the descendants:** the constructor fires only in the invoker and replay (`mark-ld.txt`: `lib <invoker-pid>`, `lib <replay-pid>`), and neither key appears in the live/server env. (`LD_PRELOAD` in the *invoker* is the caller's own environment; the frozen counter does not pass it — `PASS_ENV`.)
- **`TMPDIR` is overridden, not inherited** (`<work>/tmp` in both children), and the `sitecustomize.py` planted inside the hostile `TMPDIR` never imported.
- **`BASH_ENV`/`ENV` are dropped** (V10) — otherwise every probe `bash` would source them.
- **Locale:** `LC_ALL`/`LANG` are forwarded (allow-list) and reach both children; with `en_US.utf8` and with an ungenerated `tr_TR.utf8` the receipt's probe verdicts, health/props/slots/models/metrics captures and `match` are unchanged; server stdout lines differ only in timestamps/ports. The only caller-locale text that lands in the receipt is bash's `setlocale` warning in `probes[].stderr_tail` (V11), which no check reads.
- **Join and teardown:** witnessed pid == rerun `child_pid` in 14/14; every run left no process behind (`pgrep -f llama-server` showed only another seat's `X8WitnessPort` processes).

## Boundaries of this packet

- Only receipt-1 was replayed (the assignment's scope); the channel is per-replay, not per-receipt.
- No decimal-comma locale is generated on this host (`locale -a`: `C C.utf8 en_US.utf8 POSIX`) and `LOCPATH` is not in the allow-list, so locale-dependent numeric formatting of the server's `/metrics`/props could not be exercised — stated as untested, not as clean.
- The forging wrapper was used to *demonstrate* reach and was stopped at the receipt: I did not attempt the decoy-`ready.json`/receipt-patch chain that the leaked `--witness-dir`/`--out` argv makes feasible; that is `[INFERENCE]` from `runs/V12-path-bash-forge/mark-forge.txt`.
- `c1-forge-path.*` is a coverage probe of the counter's env leg, **not** a lane measurement; the C1 measurements in this packet are `c1-fast-scratch.*` (met=True) and `c1-home-scratch.*` (met=False).
- No pacman, no installs. `gcc` (pre-installed) compiled the `LD_PRELOAD` object. Scratch was `/fast/scratch/hyaku/kama-r50/Sen1Env` and was removed after the records were copied out; the lane, the fleet repo and `shokuknow` were never written.

## Files

- `sen1env_battery.py` — the battery (14 vectors, `/proc` snapshot, witness release).
- `runs/<V>/` — `record`, `replay.json`, `rerun-receipt.json`, `invoker.log`, marker files.
- `table.tsv`, `summary.json`, `summary.out`, `summarize.py` — the table above, machine-readable.
- `c1-fast-scratch.{out,stdout}`, `c1-home-scratch.{out,stdout}` — the paired F3 control.
- `c1-forge-path.{out,stdout}` (+ `/fast/.../work/c1-forge-marker.txt` copied as quoted evidence) — F1 coverage probe.
- `findings/btrfs-model-mapping/rerun-receipt-{btrfs,xfs}.json` — the F3 receipts.
- `btrfs_maps_dev.py`, `btrfs_maps_dev.out` — the minimal dev-mismatch reproducer.
