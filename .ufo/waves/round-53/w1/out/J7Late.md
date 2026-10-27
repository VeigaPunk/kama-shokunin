# J7Late — C1 time-of-observation probe (kama round 53, w1)

**Verdict: the frozen C1 counter's single `/proc/<pid>/mem` read is a real limit, and the limit in `.ufo/waves/round-53/preregistration.json:44` under-describes it — an in-place rewrite of `libggml-rpc.so`'s `r-x` range made 5 ms after the counter's own `release` file, while the held server was still alive, left `bind=1 sealed=1 code=1 teardown=1 newrow=1 met=True`; the running text really did change (private file mapping, page not copied), yet the rerun receipt's `code_mappings` and the replay's `own_code` still record the archive digest.**

Seat: J7Late (leaf). Lane: kama. Commit measured: `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (build). Base: `4229ea1b9a789148dded1f159c20967d9a01373f`. Host: Linux 7.2.11-arch1-1, Python 3.14.8, `kernel.yama.ptrace_scope = 1`. Counter sha256 at the commit and in the lane: `1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f` (matches `preregistration.json` `counter_sha256`).

## What I ran (all from `$S=/fast/scratch/hyaku/kama-r53/J7Late`)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane rev-parse --show-toplevel                          -> $S/lane
git -C $S/lane checkout --detach c22602bd8d83ab26349d1087e916ca537ee4f9d1
git -C $S/lane rev-parse HEAD                                     -> c22602bd…
git -C $S/lane diff --stat c22602bd bc8e6e7 -- tools/ .ufo/waves/round-48/c2/live/   -> empty
python3 probe.py    -> exit 5 (SystemExit(0) caught by my wrapper AFTER the evidence file
                       was written; the replay itself exited 0 with match=true)
python3 probe2.py   -> exit 0
python3 probe3.py   -> exit 0
python3 probe4.py   -> exit 0
python3 probe5.py   -> exit 0
python3 race_counter2.py -> exit 0 (the frozen counter it drove exited 0, met=True)
```

Every probe launched `tools/kama-live-replay.py` exactly as the counter's `start_replay()` does: `python3 -I -c "invoker" python3 -I <lane>/tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work … --out … --witness-dir …`, isolated `PATH/LANG/HOME/XDG_CACHE_HOME/TMPDIR` + proxies, `start_new_session=True`. The witness handshake is the live tool's: `ready.json {pid, port}` → observer → `release`.

The counter's own order, which the probe reproduces (frozen functions imported from `tools/round53-replay-code-audit.py`, not re-implemented):

* `tools/kama-llamacpp-live.py:2309` `receipt['code_mappings'] = code_mappings(proc.pid)` — hashes every executable file mapping **at its pathname**, one digest per mapping (T0);
* `tools/kama-llamacpp-live.py:2316` `receipt['witness'] = hold_for_witness(…)` — then publishes `ready.json` and holds (T0 is strictly before the hold);
* `tools/round53-replay-code-audit.py:581` `cobs = code_observe(...)` — wait for `ready.json`, `observe()` nonce, `sealed_exe()`, then **one** walk of `/proc/<pid>/maps` reading each executable range from `/proc/<pid>/mem` (`:405`) (T1);
* `tools/round53-replay-code-audit.py:584` writes `wd/release` immediately after that read;
* after the replay exits, `:624` checks the receipt's `code_mappings` and the replay's `own_code` (`tools/kama-live-replay.py:305`/`:521`), both derived from the T0 snapshot.

## Measured timeline (frozen-counter order, probe2)

| instant | measured |
|---|---|
| `code_mappings` done | ≈ `ready.json` − few ms (line order above; run2b `witness.waited_ms` 551) |
| T1 (one mem read done) | **0.506 s** after my first sight of `ready.json` (observe 0.009 s + sealed_exe 0.0001 s + code_observe **0.299 s**; ~0.19 s of the 0.506 s is my own detection/scheduling latency under host load) |
| frozen counter writes `release` (its one read returned) | **0.614 s** after my first sight of `ready.json` (race v2 busy spin) |
| release → server death | **~0.037 s** (race v2: flip at release+5.1 ms, server lived 32.3 ms more) |
| release → replay exit | **0.214 s** (run2b) / 0.265 s (run1b) |
| receipt written | at replay exit, i.e. after the file had already been rewritten (run2b) |

So the code leg samples two states per receipt: a path hash at T0 and one mem pass ending ~0.5–0.6 s later; nothing samples after T1.

## (a) In-place rewrite of `libggml-rpc.so`'s `r-x` range (probe1/2/3)

`libggml-rpc.so` is mapped once in the held server: `…-… r-xp 00012000 103:05 <inode> …/libggml-rpc.so`, range length 131 072 B (run3: `7fdb296b8000-7fdb296d8000`, `off=0x12000`). The archive member digest is `4b6be3e1…f338d`.

* **The write is allowed and the text changes.** `open(path, O_RDWR)` succeeds (owner is the replay's uid, mode 755, `nlink=1`); `pwrite` of one flipped byte at file offset `0x22000` (range offset 65536) leaves the inode unchanged and the running mapping byte changes `0x29 -> 0xd6`:
  `inplace_mem_vs_member: {"equal": false, "n_diff_bytes": 1, "mem_byte_at_flip": "d6", "member_byte_at_flip": "29"}` (run1b; identical in run2b and run3b). `/proc/pid/mem` reads the mapping itself (get_user_pages on the VMA), so this is the page the CPU fetches code from.
* **Private file mapping, not yet copied.** The VMA is `r-xp` with `VmFlags: rd ex mr mw me sd` (no `sh`), `Shared_Clean 0`, `Pss == Rss`; before the read `Rss 64 kB` of the 128 kB range, after the counter-style read `Rss 128 kB` (the read itself faults the rest in from the page cache). The external `pwrite` is therefore visible in a mapping the server never write-faulted: no COW copy existed, and a persistent flip is visible even on pages that were not resident before the read.
* **The counter catches a flip that is still there at its read.** Frozen `code_observe` over the flipped file: `code: mapped bytes 7fd4…-7fd4… (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member` (run1b T2, run2b second read). Restore returns memory and file to `4b6be3e1…` and the verdict to clean.
* **A transient flip+restore with no read in between leaves nothing.** run1b (a2): flip then restore before reading → `transient_mem_equal_member: true`, `code_observe` clean. The observation channel has no history.

## (b) Rename-over instead (probe1)

`mv` a modified copy (`sha256 f18527e3…`) over the path:

* `/proc/<pid>/maps` keeps the old inode and its pathname gains ` (deleted)`:
  `… r-xp 00012000 103:05 952551930 …/libggml-rpc.so (deleted)`; `os.stat(path)` is a different file (`inode 952709920`, digest `f18527e3…`).
* The running text is **unchanged**: `mem_equal_member: true`, `n_diff_bytes: 0` — the server keeps executing the old, archive-identical inode.
* The frozen counter **fails closed**: `code: …/libggml-rpc.so (deleted) is not a regular member of the archive`, and `libggml-rpc.so` drops out of `code_observe`'s `files` (7 of 8). So a rename-over persisted to T1 is refused, not missed; the refusal over-states the danger (executed bytes are fine), so it is a precision cost, not a soundness hole.

## What the rerun receipt recorded, and when

Both rerun receipts produced by the build's own tools (copies in the out dir) show the T0 snapshot, not the state at any later time:

* run2b: the file was rewritten in place at T1+8 ms and stayed rewritten until the server died and the receipt was written (`outcome: pass`, `witness.waited_ms: 551`), yet the receipt's entry is `{"path": "…/libggml-rpc.so", "dev": "103:05", "inode": "1753088598", "opened": true, "size": 319776, "uid": 1000, "sha256": "4b6be3e1…f338d"}`, and the replay's `own_code.members["llama-b11909/libggml-rpc.so"]` is the same archive digest with `verified: true`; `match: true`, `mismatches: []`.
* run1b: after the rename-over, the receipt still names the mapped old inode `952551930` with the archive digest, and `own_code` is verified — although the path then held inode `952709920` with digest `f18527e3…` for the rest of the run.

The replay's `verify_code` (`kama-live-replay.py:305`) hashes archive members **named by the receipt** straight from the archive stream, so it is self-consistent with the T0 snapshot and cannot observe a later change; the counter's receipt half (`:624`) compares that same snapshot with the archive. The only second time sample is the single mem pass.

## End-to-end on the frozen counter (race v2)

I drove the frozen counter itself (`--repo $S/lane --tip c22602bd… --scratch … --out …`) and watched `<scratch>/r53c1-*/wd-b1/release` — a file the counter writes as its first statement after `code_observe()` returned (`:584`) — with a busy spin:

* flip landed **5.1 ms** after that release file's mtime; `server_alive: true`; the server lived **32.3 ms** more;
* the counter printed `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`, exit 0, including `detail: code b1: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem …` — while, for 32 ms of that run, `libggml-rpc.so` in the run's tree was not the archive's bytes.

This also reproduces `.ufo/waves/round-53/measured/c1-build.out` exactly at the build commit (`met=True`), independent of the lane.

Caveat, stated rather than papered over: the counter's server is not my descendant (`ptrace_scope=1`), so I could not read *its* `/proc/pid/mem`; the "text really changed" part rests on runs 1–3, where the same byte at the same offset of the same mapping of a server I did parent produced `n_diff=1`. My first race attempt (v1) flipped 0.118 s after release on a loaded host, when the server was already dead — it shows only that the counter re-reads nothing after exit; v2 is the one cited.

## Is the single read a real limit?

Yes — measured, not inferred — and it has four distinct facets, only the first of which the preregistration states:

1. **Post-read, persistent (disclosed, `.ufo/waves/round-53/preregistration.json:44`).** Confirmed twice: the frozen counter certified a run with the library rewritten immediately after its own release (32 ms of live server, `met=True`), and a counter-order replica left the flip in place through receipt emission (`match: true`, `own_code verified`, pristine digest). Nothing in the counter or the replay re-reads memory or the path after T1.
2. **Pre-read, transient (not disclosed).** The receipt hash (T0) and the mem pass (T1) are ~0.5–0.6 s apart; a flip made and reverted inside that interval leaves both samples clean (run1b (a2)). The disclosed limit says "rewritten after that read"; the honest statement is "any rewrite whose lifetime does not intersect the two sample instants is not observed".
3. **The "single read" is a pass, not an instant (not disclosed).** `code_observe` reads 8 ranges in `/proc/<pid>/maps` order and the pass takes 0.21–0.36 s (run5: `libggml-rpc.so` read at **0.0163 s** of the pass, after `libggml-cpu-zen4.so` at 0.0 s and `libllama.so` at 0.0142 s; last range at 0.210 s; the 8 tree ranges total 12 869 632 B and the other 13 executable rows in maps are host files the pass only `stat`s; all 21 executable rows total 23 162 880 B; the pass interleaves archive-member extraction with the preads). A rewrite of a range already read, during the rest of the pass, is unobserved by that pass.
4. **The receipt's `code_mappings` and the replay's `own_code` are pre-hold snapshots (not disclosed).** They are taken at T0, before `ready.json` (`kama-llamacpp-live.py:2309` then `:2316`), and re-derived from the same snapshot after exit (`kama-live-replay.py:521`), so the "recorded in code_mappings and own_code" half of the leg adds no second time sample — proven by run2b, where the receipt (written ~0.2 s after the rewrite) still carries the archive digest.

Precision note: a rename-over that persists to T1 is refused (fails closed) because the maps pathname gains ` (deleted)`; the executed text is still archive-identical, so this is an over-refusal, not a miss.

## Proposed fix (counter and preregistration are frozen — nothing edited in place)

`counter-post-exit-rehash.diff` (in the out dir; applies with `patch -p1` clean, no fuzz, and the patched file byte-compiles) adds, after the replay exits, a re-hash of every path the T1 observation named, comparing inode and digest with the archive member:

```
+                for path, (dev, ino, member) in sorted(cobs["files"].items()):
+                    want = hashlib.sha256(arc.member(member)).hexdigest()
+                    try:
+                        st, got = os.stat(path), sha_file(path)
+                    except OSError as exc:
+                        cprobs.append(f"code: {path} not re-readable after the replay: {exc.strerror}")
+                        continue
+                    if str(st.st_ino) != ino or got != want:
+                        cprobs.append(f"code: {path} changed after the observation: inode "
+                                      f"{st.st_ino} != {ino} or digest {got} != {want}")
```

That closes facet 1 for changes that outlive the read (the case both my end-to-end runs exercised) and narrows the window to the live-server tail, but it cannot close facets 2 and 3 — a state-sampling counter cannot see history. The structural fix for round 54 is a two-phase witness (hold the server until the receipt is written, then let the counter take a second mem pass and a second path hash, and compare the two snapshots), plus an honest limit line in the next preregistration, e.g.:

> C1: the counter samples state twice per receipt — a path digest before the hold and one `/proc/<pid>/mem` pass (~0.2–0.4 s, one range at a time) during it; a library rewritten and restored between those instants, or rewritten after the pass, is not observed. `code_mappings` and `own_code` are derived from the pre-hold hash and are not re-observed.

## Probe limits and risks

* Single library (`libggml-rpc.so`), single byte at offset `0x22000`, one host; the mechanism is generic (all 8 archive mappings are `r-xp` private file mappings) but only this one was exercised.
* Latencies are host-load dependent (≈20 sibling seats live): the race needed a busy-spin watcher; an earlier sleeping watcher flipped 118 ms after release, by which time the server had exited.
* run4's later trials are not used: after the first pass the server's pages were resident, so passes ran in ~2 ms and the flips landed after them (an artifact of the warm cache, not a boundary measurement); run5's per-range timeline is the evidence for facet 3 instead.
* No lane file was written, no `pacman`/install ran, no service was touched; every probe used its own scratch, loopback ports, and every replay exited 0 with the port refusing afterwards. Other seats' held servers (`K2Design`, `J1SwapChecked`) were left untouched.
* `pgrep -af 'llama-server|kama-live-replay|kama-llamacpp-live' | grep J7Late` → none; scratch removed after this report was written.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/j7-summary.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/counter-post-exit-rehash.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/probe.py`, `probe2.py`, `probe3.py`, `probe4.py`, `probe5.py`, `race_counter.py`, `race_counter2.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/run1-inplace-rename-evidence.json`, `run2-counter-order-evidence.json`, `run3-residency-evidence.json`, `run4-pass-offline-evidence.json`, `run5-pass-timeline-evidence.json`, `race-v1-late-flip-evidence.json`, `race-frozen-counter-evidence.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/rerun-receipt-run1.json`, `rerun-receipt-run2.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J7Late/run1-probe.log`, `run2-probe.log`, `run3-probe.log`, `run4-probe.log`, `run5-probe.log`, `race-v1.log`, `race-v2.log`, `race-v2-counter-stdout.log`
