# V2Review — round-50 code review (kama-live-replay.py, kama-llamacpp-live.py)

Verdict: **sound build — 0 blocking, 2 Low, 2 Info; every enumerated review surface checked with fixtures; C1 and C2 independently reproduced met=True at the tip on my own clone.**

Scope: `git diff 26ecba64ad6fb571d09074b07202d1618a46ecd1 97c864bead3ee4a2f629574e77263d33834ec98a -- tools/kama-live-replay.py tools/kama-llamacpp-live.py` (replay: +63/−3; live: +58/−1). All paths below are `tools/...` relative to the lane root. No LSP server answered any file in this seat's toolset (no `lsp` device available), so caller/definition checks are text grep + read — recorded per protocol; semantic claims are backed by executed fixtures, not grep alone.

## Findings

### L1 (Low, doc/code mismatch) — `model_mapping()` never enforces "no larger than when it was mapped"
- Where: `tools/kama-llamacpp-live.py` model_mapping() (def at :677), docstring sentence "…, a regular file no larger than when it was mapped" vs the check at the `if not stat.S_ISREG(st.st_mode) or sdev != dev or str(st.st_ino) != ino:` guard: only S_ISREG + dev + inode are checked; the mapped span from the maps row (`f[0]`–`f[1]`) is never compared with `st.st_size`.
- Shows: `f3_truncate.py` (out dir copy) — child mmaps a 400,000-byte file, `os.truncate(path, 200_000)` (same dev/ino), then `model_mapping()` records `{'mapped': True, 'size': 200000, 'sha256': e7208989…}` — a file smaller than its mapping is accepted, contradicting the docstring.
- Not a false pass: any content change moves the digest, and the replay compares the rerun's `model_mapping.sha256` against the receipt's model sha (`kama-live-replay.py:346-347`), so the truncated file is refused one line later (fixture prints exactly that).
- Fix (one of): capture the matched row's span and add `if st.st_size > span: return {'mapped': False, 'reason': 'model-larger-than-mapped', …}`; or reword the docstring to drop the size clause. Either is a finding-fix, not an in-place edit (tool is past its measured run).

### L2 (Low, threading) — `preexec_fn` runs while the selftest holds a live observer thread
- Where: `kama-live-replay.py:331-332` `subprocess.run(…, preexec_fn=_child_pdeathsig)` with `_child_pdeathsig` defined at :318-323 (calls the cached ctypes `prctl` and `os.getppid()` in the forked child); `_selftest` starts `kick = threading.Thread(target=observer)` at :503-504 and then calls `replay(…, witness_dir=wdir, …)` **in-process** at :505-506 while that thread is alive.
- Why it matters: CPython documents `preexec_fn` as unsafe in the presence of threads — between `fork()` and `exec()` the child can deadlock if another thread held an allocator/ctypes lock at fork time. Round 50 introduced this combination (the base had no `preexec_fn`); production `replay()` is single-threaded so only the selftest's witness case is exposed, and a manifest deadlock would hang `--selftest` (operator-visible, not silent).
- Shows: code read (lines above) + Python `subprocess` docs (preexec_fn thread-unsafety); the risk is probabilistic, not reproducible on demand. `KLR_SELFTEST pass=23 fail=0` at the tip (command below) shows it does not manifest on this host/run.
- Fix: run the witness case's `replay()` in a subprocess, or move the observer into a child process (`python -c` poller) so no thread is alive when `subprocess.run(preexec_fn=…)` forks.

### I1 (Info, diagnostics honesty) — `set_own_pdeathsig()` return discarded; `live_child.pdeathsig` claimed unconditionally
- `kama-live-replay.py:587` calls `set_own_pdeathsig()` and ignores its boolean; `res["live_child"] = {"isolated": True, …, "pdeathsig": "SIGTERM"}` (:316) and the child-side `if prctl is not None:` (:319) silently degrade to "no signal armed" when prctl is unavailable. On Linux prctl(1, SIGTERM) does not fail in practice, and a silent degradation cannot pass C1 (the teardown leg would leave the tree alive → met=False), so this is a receipt-honesty nit, not an operability hole.
- Fix: record the boolean (e.g. `res["own_pdeathsig"] = set_own_pdeathsig()`), or `ap.error` when `prctl` is None on Linux.

### I2 (Info, cosmetic) — `'model-mapping:None'` possible in a mismatch string
- `kama-live-replay.py:342-344`: `f"model-mapping:{mm.get('reason') if isinstance(mm, dict) else 'absent'}"` prints `None` when the rerun's `model_mapping` is a dict with `mapped != True` and no `reason`. The real live tool always writes a `reason` (template default `None` at live:1763 is replaced by either the record or `{'mapped': False, 'reason': 'server-not-running'}`), so this needs a hand-forged rerun receipt. Fix: `mm.get('reason') or 'unmapped'`.

## Verified non-issues (each exercised, not assumed)

- **maps line split / string forms / chunk loop** — `f1_mapping.py`: real `mmap` child on xfs; 2.5 MB file (three 1 MiB chunks), directory with spaces, symlinked `--model` path. `split(None, 5)` preserves spaces in the pathname; kernel dev `103:05` equals `'%02x:%02x'` formatting and inode string equals `%lu`; realpath+`O_NOFOLLOW` resolves the symlink and still matches the kernel-resolved dentry. Unmapped child → `model-path-not-in-maps` (fail-closed). Same dev form (`103:05`) appears in the counter's own receipts, so the record/observe formats agree.
- **maps-read vs hashed-open race** — the maps row's (dev, ino) must equal `fstat()` of the `O_NOFOLLOW|O_NONBLOCK` fd before hashing; a path swapped between read and open trips either `mapped-file-is-not-the-model-path` (different inode at the path) or `model-path-not-in-maps` (kernel's ` (deleted)` suffix breaks `f[5] == want`). `f2_swap.py`: unlink + replace while mapped → `{'mapped': False, 'reason': 'model-path-not-in-maps'}`; a fresh map of the new file binds correctly. A false pass needs identical dev+ino+sha256, i.e. the same inode with identical bytes — exactly the documented in-place-rewrite limit.
- **multiple mappings** — same file in several segments dedups by `(dev, ino)`; two different inodes at the path → `model-path-maps-several-files` (fail-closed). Code path live:695-703 (harness `hits` list).
- **Old v4/v5 originals and the rerun-only requirement** — correct as built. `compare()` (replay:239-273) compares only named keys, so an original without `model_mapping` is unaffected by the rerun's extra key; the round-50 check reads only the rerun receipt (replay:341-347). `f5_compare.py`: `compare(orig-without, rerun-good) == []`, `compare(orig-without, rerun-absent) == []`, while the replay-level check yields `model-mapping:absent` / `model-mapping:server-not-running` / `model-mapping:sha256:…` exactly when the rerun lacks or mismaps the record. Rerunning the three round-48 receipts at the tip works because the tip live tool always records the mapping; a rerun executed by a pre-round-50 `--live` copy is refused — which is precisely the "no model_mapping record" ablation surface.
- **hold_for_witness interplay** — mapping is recorded while `_child_running(proc)` (:1999-2005) and *before* the witness hold (:2007-2014), so the window the counter observes names the same pid the receipt's `child_pid` carries (`child_pid = proc.pid` at :1896; `hold_for_witness` refuses a dead child before announcing, :340-341, and ready.json pid is that child). Record-time dev/ino therefore equals observation-time dev/ino; confirmed end-to-end by the counter: "child_pid joined, mapping dev 103:05 inode … recorded" for all three receipts.
- **Teardown chain** — invoker→replay (`set_own_pdeathsig`, own-pid recheck closes the already-dead-parent race, replay:100-109), replay→live tool (`_child_pdeathsig` with `me` captured pre-spawn + child-side getppid recheck, replay:317-323), live tool→server (pre-existing `_preexec_pdeathsig` SIGKILL, live:661). `f4_pdeathsig.py`: child armed by `set_own_pdeathsig()` dies of SIGTERM within 5 s of its parent's SIGKILL. Counter leg measured "after 0.10 s alive [] port refuses ok". Placement is right: `set_own_pdeathsig()` at :587 runs before `replay()` does the ~75 MB download, so a kill during download also unwinds (that kill timing is outside the frozen counter, noted as gap below).
- **Environment isolation** — `live_env()` passes exactly PATH/HOME/LANG/LC_ALL + TMPDIR=replay-work/tmp (replay:87, 112-115); `python -I` additionally defeats PYTHONPATH/sitecustomize. Counter bind leg (which includes the canary-environ and marker checks) passed 3/3 on my run.
- **Resource cleanup** — hashing fd closed in `finally` (live:724-726 area), maps handle via `with`; child reaped by `subprocess.run`; no new leaks introduced by the diff.
- **Callers** — grep over `tools/`: no other tool calls the changed functions; the round-47/48/49 counters invoke the replay with unchanged argv, and `--compare`/`--selftest` paths were exercised at the tip.

## Independent counter runs (my clone, tip 97c864bead3ee4a2f629574e77263d33834ec98a)

- `python3 tools/round50-replay-bind-audit.py --repo $S/lane --tip 97c864be… --scratch $S/c1 --out $S/c1.out.json` → `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0, 17.5 s. Receipt copied to `out/V2Review/c1.out.json`.
- `python3 tools/round50-append-audit-v5-check.py --repo $S/lane --tip 97c864be… --scratch $S/c2` → `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0, 5.8 s (outside my two-file scope; run for the wave record).
- `python3 tools/kama-live-replay.py --selftest --scratch $S/klr-st` → `KLR_SELFTEST pass=23 fail=0`, exit 0 (includes `witness-passthrough`, the L2 path).
- `pgrep -af llama-server` after all runs → no matches (no leftovers).

## Residual risk and verification gaps

- Proxy/CA environment: `live_env()` strips proxy and `SSL_CERT_*` variables from the live child. The replay itself does the fetching (keeping the counter-passed proxy vars) and hands local paths to the child, so this host is fine (both counters green); on a host where the *live tool itself* had to fetch through a proxy, the allow-list would break it. Portability note only.
- Kills during download/readiness are not exercised (frozen counter limit). The uncovered window for the replay's own pdeathsig is interpreter start → `set_own_pdeathsig()` at :587 (argparse only).
- The L2 deadlock is probabilistic; one clean selftest run is evidence of health, not of impossibility.
- Non-xfs fail-closed behavior (btrfs subvolume dev mismatch) is documented in the preregistration limits and not re-tested here; scratch and counter scratch are both xfs (`stat -f -c %T` → `xfs`).
- `--scratch` must pre-exist for `--selftest` (`tempfile.mkdtemp(dir=root)` raises FileNotFoundError otherwise) — pre-existing behavior outside this diff; first selftest invocation in this review hit it before `mkdir`.

## Tooling record

No tools installed or upgraded (none needed); pacman untouched. No lane file was modified; all runs used my `git clone --shared` clone (detached to the tip; the two reviewed files are byte-identical between the lane workdir HEAD 3b79eadd and the tip, so fixture evidence transfers). No llama-server process was started outside the frozen counter.

— seat V2Review, 2026-10-26
