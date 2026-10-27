K1Design2 — C1 design critic (round-50 counter `tools/round50-replay-bind-audit.py`, frozen): VERDICT — the counter met=True at the measured tip (reproduced: `bind=1 teardown=1 newrow=1 bound=3/3`), but four of its legs prove strictly less than the predicate's wording; two are demonstrated soundness holes (ambient `sitecustomize`/`.pth` under `-I` invisible to both canaries; model *weights* unbound behaviorally and temporally), the rest are stated limits with smallest next-counter fixes.

Measurement run (this seat): `python3 tools/round50-replay-bind-audit.py --repo $S/lane --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch $S/ctr --out $S/c1-receipt.txt` → exit 0, `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (receipt copied to `w1/out/K1Design2/c1-receipt.txt`; `pgrep -f llama-server` clean after). Lane clone was `git clone --shared` under `$S`; lane untouched.

## What each binding leg actually proves — and does not

| leg | counter site | proves | does not prove |
|---|---|---|---|
| exe | `observe()` L345-347 | the *running image* behind `/proc/<pid>/exe` is the frozen server digest | that ready.json's pid is the only server; argv sanity |
| listen | L348-350 | *a* LISTEN socket on loopback:port whose inode ∈ the server's fd set | that no non-loopback listener exists on the port (`listen_inodes` filters to `0100007F`/`::1`, L213 — a 0.0.0.0 second bind is ignored, not rejected) |
| nonce | L360-370 | the server's tokenizer tables equal the counter's own GGUF decode | anything about the weights — no `/completion`, no logits (F2 below) |
| tree | `replay_pid` L418-422, `descends_from` L297-306 | the announced pid descends from the invoker's *unique* direct child | an unbroken pdeathsig chain; >1 invoker child fails closed (limit, F4) |
| env | `observe` L353-358; marker L480-485 | exactly `KAMA_R50_CANARY` absent from the exec-time environ of server+its parent; the *planted* PYTHONPATH sitecustomize never imported | allow-listing; absence of `PYTHONPATH` itself; any other injected name; ambient site channels (F1) |
| mapped | `mapped_model` L309-340; join L473-476 | at counter hash-time: some file-backed mapping whose pathname stat()s to the same dev+ino and hashes to `MODEL_SHA`; the tool's receipt names the same dev+ino (join also pins the live tool's path-equality search, `kama-llamacpp-live.py` L696) | that the bytes the server *read* were these bytes (in-place rewrite window, F2); that weights match the vocab; btrfs-class dev mismatch (F3) |
| join | L462-478 | exit 0, `match` true, `witness.released`, `child_pid` == observed pid, mapping joined, server gone, port refuses | — (sound) |
| teardown | L497-526 | one SIGKILL of the invoker during the witness hold clears the ppid snapshot within 30 s + port refuses; `pid_alive` starttime match (L244-248) already defeats naive pid reuse *of snapshotted pids* | post-snapshot forks (never in `snap`), kills at other phases/links, the pdeathsig arm window (F5) |
| newrow | `newrow_leg` L529-539 | some new `| S<digit>` row contains `proc_pid_maps.5.html` | the row the claim also names — S497 `PR_SET_PDEATHSIG(2const)` — exists (F6) |

## Findings

### F1 (soundness, demonstrated): the two canaries cannot see ambient site customization — `python -I` still imports `sitecustomize` and executes `.pth` code lines from site-packages

`observe()` checks only `KAMA_R50_CANARY` in `/proc/<pid>/environ` (L357) and afterward the marker file written only by *the counter's own planted* `sitecustomize.py` (L480-485). Neither can see:

- **`PYTHONPATH` leaked but silent.** A replay forwarding the whole environment (including `PYTHONPATH=<canarydir>`) leaves `PYTHONPATH` in the live tool's `/proc/<pid>/environ` — but the env leg greps only the canary *name*. With `-I` honored, no descendant interpreter ever imports the planted `sitecustomize` → marker empty → **the leak is invisible**. If `-I` were *also* dropped in the same variant, the marker catches it — i.e. the env leg certifies exactly one named variable and one file, not isolation.
- **Ambient `sitecustomize.py` / code-executing `.pth` files.** `-I` removes PYTHONPATH, user site, cwd and script dir — but `site` still runs, imports any `sitecustomize` found in system **or venv** site-packages, and executes `import …` lines in `.pth` files there. Demonstrated on this host (`evidence/ambient-sitecustomize.txt`): a `sitecustomize.py` and an `evil.pth` planted in `venv-ambient/lib/python3.14/site-packages` both execute under `venv-ambient/bin/python -I` (`isolated 1`, `sitecustomize in sys.modules: True`, `ambient sitecustomize ran: True`, `pth ran: yes`). On this very host `/usr/lib/python3.14/site-packages/distutils-precedence.pth` already executes under `-I`. A lane interpreter carrying an ambient sitecustomize (venv `bin/python` is exactly how such a file ships) gives the live tool a **hijacked interpreter that leaves no canary trace** — the R1 PYTHONPATH hijack channel re-opens through a hole the marker structurally cannot cover.

Smallest counter change: (a) in `observe`, replace the single-key check with `keys ⊆ {"PATH","HOME","LANG","LC_ALL","TMPDIR"}` for server *and* parent — one line stronger, subsumes the canary and detects `PYTHONPATH` leaks; the receipt's `child_env_keys` (recorded at `kama-llamacpp-live.py` L1858-1860, never read by the counter) is the same-shape fix joining receipt to `/proc`. (b) Add an ambient probe before the legs: run `python3 -I -c "import sitecustomize"` against the *same* interpreter that will run the replay and fail closed (exit 2, "could-not-evaluate") if it imports, plus a scan for `.pth` files containing `import` in that interpreter's `site.getsitepackages()` — otherwise the env/marker leg is vacuous on that host. (Next counter generation: have the live tool record `sys.flags.isolated` + `sorted(os.environ)` at startup and join it.)

### F2 (soundness, demonstrated + structural): the model leg binds tokenizer + a hash at hash-time; the weights the server ran are unbound in both dimensions

Two independent gaps stack:

- **Behavioral**: `observe`'s nonce leg (L360-370) exercises only `/tokenize` and `/detokenize` — GGUF *tokenizer* tables, not the weights. Demonstrated (`evidence/same-vocab-swap.txt`): `model-evil.gguf` = the frozen model with one byte flipped in the tensor region → `sha256` differs, the counter's own `gguf_tokens` returns the identical 512-token vocabulary. A swap model serving the same tokenize/detokenize answers produces byte-identical nonce evidence.
- **Temporal**: both digests are taken *after* the server mmap'd the file — the live tool hashes at receipt time (`kama-llamacpp-live.py` L714-727), the counter re-hashes during the hold (L337). `llama.cpp` mmaps `MAP_PRIVATE`, so an in-place rewrite between "server reads the pages" and "counter hashes" makes the server run bytes neither digest ever saw; restoring good bytes before the hash leaves every check green. dev+inode are unchanged by an in-place rewrite, so the join (L473-476) does not catch it either.

Smallest counter change: (a) cheap temporal narrowing — have the live tool record `st_mtime_ns`/`st_ctime_ns` in `model_mapping` and the counter fail the leg when `ctime` ≥ the server's `/proc/<pid>/stat` starttime (shrinks the window to before launch; still not airtight). (b) real fix — bind a *weight-sensitive* surface: freeze a deterministic `/completion` transcript (fixed prompt, `temperature=0`, fixed seed/n_predict, frozen expected tokens or logits) alongside `MODEL_SHA` in the next counter, so the nonce leg probes the loaded tensors, not only the tokenizer.

### F3 (availability, demonstrated, stated limit): dev join fails closed on btrfs subvolumes — on this host's `/home`, by 38-vs-1e

`mapped_model` requires `major:minor` from `/proc/<pid>/maps` to equal `stat().st_dev` (counter L333; live tool L711 same rule). On btrfs subvolumes `stat()` reports the subvolume's anonymous device while `maps` reports the real device. Demonstrated on this host (`evidence/btrfs-dev-mismatch.txt`): file under `/home` (btrfs subvol `@home`) → `st_dev 00:38`, `maps dev 00:1e`, same inode → both `model_mapping()` and `mapped_model()` reject: every rerun would record `model-mapping:mapped-file-is-not-the-model-path` and the bind leg fails closed. The counter's scratch is xfs (`/fast`, `/tmp`) so measurement is fine; the *mechanism* is filesystem-sensitive wherever `--work` lands on btrfs — worth a sentence in the tool docstring or a mountinfo-based join (`/proc/<pid>/mountinfo` maps the maps-device to the mount, then compare inodes) if the lane ever measures outside xfs.

### F4 (limit, stated + sharpened): `replay_pid` is a single-child assumption; a middleman also silently breaks the pdeathsig chain

`replay_pid` (L418-422) returns the invoker's unique direct child. Two edges: (a) a second invoker child → `rp=None` → bind fails *closed* (fine, stated limit). (b) Sharper: `descends_from` passes a server nested below a middleman (invoker→sh→replay→tool→server), but **pdeathsig is per-edge** (`S497`: cleared at fork, armed against the immediate parent) — a middleman that neither sets pdeathsig nor dies with its parent breaks the teardown chain the claim asserts, and `teardown_leg`'s snapshot cannot see that break because it never checks chain contiguity. Smallest counter change: in `bind_one`, assert the ppid chain is contiguous — `server.ppid == live-tool`, `live-tool.ppid == rp`, `rp.ppid == invoker` — or equivalently that every intermediate node's pdeathsig edge exists; and make `replay_pid` pick "the invoker child whose cmdline contains `kama-live-replay.py`" instead of `kids[0]`, turning the >1-child case from a silent `None` into a checked fact.

### F5 (limit, demonstrated): teardown's snapshot misses post-snapshot forks; and the arm-window race orphans the replay entirely

- `teardown_leg` snapshots `descendants(p.pid)` *before* `SIGKILL` (L505-509) and afterward only rechecks snapshotted pids (L513-518). A descendant forking between snapshot and kill is never in `snap`; after the invoker dies it reparents to init, and `reap`'s `descendants(p.pid)` rescan (L426) cannot find it either (the ppid chain is severed) → a grandchild survives both the verdict and the cleanup. The starttime match (L244-248) already covers pid reuse of snapshotted pids; this residual class is uncovered.
- Arm-window race, demonstrated (`evidence/pdeathsig-arm-window.txt`): parent killed *between* the child's `exec` and its `prctl(PR_SET_PDEATHSIG)` → the child is reparented before it ever arms, `prctl` then arms against the *new* parent (init/subreaper), and it survives indefinitely (case B: `ppid_before 1494` … `STILL ALIVE`). `kama-live-replay.py set_own_pdeathsig()` (L104-108) samples `os.getppid()` *after* interpreter boot, so its `getppid()!=parent` guard cannot catch a parent that died earlier — this is exactly the invoker→replay edge (the replay's own arming happens at `main()` L587, after argparse), the edge the R2 fix added and the one the counter's teardown leg exercises only *after* arming is complete.

Smallest counter change: (a) snapshot the invoker's session id (`/proc/<invoker>/stat` field 5 — `start_new_session=True` makes it `p.pid`) and after the kill rescan `/proc` for *any* live pid with that sid, treating leftovers as both verdict failure and `reap` targets; catches post-snapshot forks regardless of reparenting. (b) Arm the replay's pdeathsig in the *invoker's* `preexec_fn` (the counter owns `INVOKER`, L114-115 — add a `prctl`+`getppid` guard there, mirroring `kama-live-replay.py` L314-318): the edge then exists before the replay's interpreter boots, shrinking the orphan window from "whole interpreter startup" to "fork→preexec microseconds", guarded. The analogous tool-side residual (a `SIGKILL` landing before `set_own_pdeathsig` at L587) is inherent to self-arming and worth one docstring line as a bound.

### F6 (defect, minor): `newrow` does not require the S497 row the claim names as teardown's source

The claim is "sourced on S496 `proc_pid_maps(5)`; S497 `PR_SET_PDEATHSIG(2const)` grounds the teardown mechanism". `newrow_leg` (L529-539) requires only a new `| S<digit>` row containing `proc_pid_maps.5.html` (L537) — an ablation deleting the S497 row (present at tip, `corpus/SOURCES.md` L250) still passes. Smallest counter change: `hit = [ln for ln in new if MAPS_URL in ln] and [ln for ln in new if "PR_SET_PDEATHSIG" in ln]` — one extra conjunct.

## Non-findings checked

- Symlink swap on the counter's hash path: `sha_file` follows symlinks, but `os.stat` precedes it and the dev+ino equality (L333) pins the object — a dangling or wrong-target symlink is skipped, not passed.
- `(deleted)` maps pathnames: `os.stat` fails → candidate skipped → fails closed.
- `reap` killpg: invoker has `start_new_session=True` (L404) so `os.killpg(p.pid)` (L434) covers the invoker's pgid correctly; the server's own session (live tool L1887) is reached via the descendants list, which is exactly why post-snapshot reparented forks escape (F5).
- `hold_for_witness`'s `getppid` poll (live tool L358-359) is an independent mid-hold parent-death tripwire; it does not cover the pre-`set_own_pdeathsig` window or post-hold phases (F5 stands).

## Files

- Report: `kama-shokunin/.ufo/waves/round-50/w1/out/K1Design2.md` (this file)
- `w1/out/K1Design2/c1-receipt.txt` — counter receipt at tip, exit 0, met=True
- `w1/out/K1Design2/c1-run.log` — full counter stdout
- `w1/out/K1Design2/evidence/ambient-sitecustomize.txt` — F1 demo
- `w1/out/K1Design2/evidence/same-vocab-swap.txt` — F2 demo
- `w1/out/K1Design2/evidence/btrfs-dev-mismatch.txt` — F3 demo
- `w1/out/K1Design2/evidence/pdeathsig-arm-window.txt` — F5 demo

No lane files touched; no tool installs needed (stdlib only); scratch `$S` cleaned.
