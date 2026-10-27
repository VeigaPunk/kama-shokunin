# J1Twopass — C1 time-of-observation probe (kama round 55, w1)

**Verdict: the frozen C1 counter's sampling-window limit is accurate in kind and wrong in the two places it is stated — a same-uid process that rewrites `libggml-rpc.so`'s `r-x` range in place (same inode, `O_RDWR` + `pwrite`) and restores it inside the interval between the counter's two reads of that range left every per-receipt leg at its honest value 10/10 (`bind=1 sealed=1 code=1 envnames=1 hostlibs=1 anon=0 twopass=1 rehash=0` — exactly the field values `.ufo/waves/round-55/measured/c1-build.out` prints) while `/proc/<pid>/mem` showed exactly one byte differing from the archive member at the instant of the flip; the same rewrite held across pass 2's read was caught 10/10 (`twopass=0 code=0`).**

Seat: J1Twopass (leaf). Lane: kama. Measured tip: `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
(the round-55 build/freeze commit). Counter bytes imported read-only from
`git show 9c60eae6:tools/round54-replay-code-audit.py`, sha256
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` — equal to
`preregistration.json` `claims.C1.counter_sha256`. Counter archive sha256
`bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` (the frozen digest).
Host: Linux 7.2.11-arch1-1, Python 3.14.8, `kernel.yama.ptrace_scope = 1`. No lane file,
fleet file, jj state or Git index was written; no `pacman` ran; no tool was installed.

## What I ran

I did not edit the counter. `j1_probe.py` imports the frozen module from the lane clone
(`importlib` on the `git show` bytes) and calls its **own `bind_one()`** — the frozen
orchestration, including `start_replay()` (invoker + `python -I` + `--witness-dir`), the
ready handshake, `env_leg`/`observe`/`sealed_exe`, the two `code_observe()` calls, the
`release` write (`tools/round54-replay-code-audit.py:720`), the replay wait and the
post-exit re-hash (`:767-780`). Instrumentation is monkeypatching in my process only:
`mod.code_observe`, `mod.sha_file`, `builtins.open` (to timestamp the `release` write) and
`os.pread` (to timestamp every `/proc/<pid>/mem` read). The attacker is a **separate
same-uid process** (`j1_attacker.py`) that parses the library's `PT_LOAD`/`PF_X` segment,
opens the *unpacked* tree path `O_RDWR`, `pwrite`s one byte at the midpoint of the mapped
`r-x` row, holds, and `pwrite`s the original byte back. Trigger classes: `pin_in` fires
right after pass 1's read of the target range; `pin_post2` right after pass 2 returns;
`none` is the clean characterization.

## The window (26 instrumented runs, 208 range intervals)

| quantity | min | median | max |
|---|---|---|---|
| pass 1 duration (8 ranges) | 6.379 ms | 9.274 ms | 276.498 ms |
| pass 2 duration (8 ranges) | 6.026 ms | 7.875 ms | 8.848 ms |
| **pass 1 end → pass 2 start** | **0.0059 ms** | **0.0074 ms** | **0.0121 ms** |
| **pass 2 end → `release` file** | **0.0075 ms** | **0.0098 ms** | **0.0927 ms** |
| `release` → first post-exit re-hash | 223.01 ms | 223.43 ms | 224.87 ms |
| **pass 1 read of range R → pass 2 read of R** | **5.99 ms** | **8.52 ms** | **252.16 ms** |
| server process lifetime after `release` | 17.53 ms | 20.25 ms | 31.40 ms (n=3) |

Read this as three facts. (1) The two `code_observe()` calls are back-to-back
(`:709`/`:711`): the gap between the *pass boundaries* is 6–12 µs and the counter writes
`release` 8–93 µs after pass 2 returns. (2) That is not the sampling window: each pass is
a **sequential sweep of the 8 archive executable ranges**, so the two reads of the *same*
range are 6.0–252 ms apart (median 8.5 ms, ≈1,150× the boundary gap). Pass 1 is slow only
on the first run after extraction (cold page cache, 234–276 ms); warm it is ~9 ms, and
then the per-range window is compact (5.99–12.4 ms) but still ~1,000× the boundary gap.
(3) The post-exit re-hash runs 223 ms after `release`, i.e. **~200 ms after the server
process has already exited** (it survives 17–31 ms), so the re-hash can only see a rewrite
left in the file; it can say nothing about the running text.

## Race outcome

**Evasion — flip + restore inside the pass1(R)→pass2(R) interval, 3 ms hold, 10 runs**
(each: trigger → write 0.047–0.062 ms, hold 3.054–3.066 ms, restore always before pass 2's
read of R, `restore_before_pass2_read=true`):

```
run 1..10   twopass=True  code=True  rehash=0  bind=True
            detail: "twopass rN: both observation passes byte-identical over 16 range reads"
            mem_obs.bytes_differing_from_archive = 1   (10/10)
```

Every per-receipt leg the counter derives from `bind_one()` is at its honest value
(`bind=1 sealed=1 code=1 envnames=1 hostlibs=1 anon=0 twopass=1 rehash=0`, the same
values `c1-build.out` prints), so a run of this kind feeds an unchanged `met=True` roll-up
(`teardown`/`newrow` are outside `bind_one` and were not re-run here) — while the server's
mapped text really was different: the probe reads `/proc/<pid>/mem` over the 128 KiB `r-x`
row 1.5 ms after the trigger and finds exactly one byte unequal to the counter's own
archive member. Same inode 10/10
(`inode_before == inode_after`); the file digest after the run equals the archive member
digest `4b6be3e1…f338d` 10/10 (one run's *before*-hash raced the replay's extraction and
read the empty file, `e3b0c442…`; the after-hash is the member digest in all ten — a probe
artifact, not a counter observation).

**Detection control — the same flip held 400 ms, 10 runs:** `twopass=False code=False`
10/10, with both messages present:

```
code rN: executable bytes differ between the two observation passes
code rN: mapped bytes <lo>-<hi> (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
```

and `rehash=1` in 9/10 (the 10th restored before the re-hash, which fired at +223 ms).
So a rewrite that is still in place at the second read, or left in place at exit, is
caught — round 54's re-hash does close the round-53 "flip after the read and leave it"
hole.

**Post-pass-2 — flip right after pass 2 returns, 5 ms hold, 5 runs (+3 with a liveness
poller):** `twopass=True code=True rehash=0`, `mem_obs=1` 5/5+3/3. The write lands 0.05 ms
after pass 2 ends (the `release` is written ~0.01 ms after pass 2), the server is still
alive for 17–31 ms, and the restore lands ~218 ms before the re-hash. Nothing observes it.

## Is the preregistration's sampling-window limit accurate?

The frozen sentence (`preregistration.json:49`, C1 clause): *"the counter samples state
(two passes and a post-exit re-hash), so a library rewritten and restored between those
instants is not observed"*.

**Accurate in kind — confirmed.** A rewrite+restore between two observation instants is
not observed: 10/10 in the inter-read window, 5/5+3/3 after pass 2.

**Wrong in the two places it is *stated* in prose**, and under-quantified where it is a
limit:

1. **`tools/round54-replay-code-audit.py:64-66` (leg (vi)) is false as written.**
   *"the observation is two-pass: both passes read every archive range and the two
   snapshots must be byte-identical, so a library rewritten while the pass runs does not
   pass unnoticed (J7Late facet 3)"*. In 10/10 evasion runs the write landed **while pass
   1 was running** (e.g. run 1: `write@2489.5 ms`, `pass1=[2448.0, 2724.5] ms`) and passed
   unnoticed, because the byte was restored before pass 2 read that range. The leg
   notices a rewrite that is *still present* at the second read — not one made "while the
   pass runs".

2. **The two-pass structure adds no byte-change detection over the per-pass archive
   comparison.** `code_observe()` already appends *"mapped bytes … differ from the archive
   member"* whenever `got != want` in either pass, so `snaps1 != snaps2` ⟹ at least one
   pass differed from the member ⟹ the code leg failed too (observed in all 10 detection
   runs, both messages together). Its only marginal power is detecting a change in the
   *set* of executable archive ranges between the passes (dict-key mismatch, `:714-715`).
   The round-54 hardening that actually bought something is the post-exit re-hash
   `:767-780`.

3. **The magnitude is not disclosed.** "between those instants" reads as two adjacent
   instants (the pass boundaries are 6–12 µs apart), while the real per-range exposure is
   6.0–252 ms (median 8.5 ms) — and for a range already read in pass 1, the exposure runs
   until the server exits, 17–31 ms after the release. A reader who takes "two passes" as
   a narrow window under-estimates the exposure by ~1,000×.

4. **The re-hash cannot cover the post-pass-2 window at all.** It fires 223 ms after the
   release, ~200 ms after the server has exited. So the only thing standing between a
   same-uid writer and an unobserved run of modified text after pass 2 is that the writer
   must restore before a re-hash it can trivially outrun — 5/5+3/3.

The counter's *Limits* paragraph (`:87-92`) is closer ("a path digest at receipt time in
the live tool, and one or two `/proc/<pid>/mem` passes during the hold"), but it also
does not say that "one or two passes" means 16 sequential range reads spanning up to
~0.5 s, nor that the live tool's digest is taken **before** the hold
(`tools/kama-llamacpp-live.py:2354` precedes `hold_for_witness` at `:2359`).

## Defect and proposed fix

- **Defect A (documentation, falsified claim):**
  `kama-shokunin/tools/round54-replay-code-audit.py:64-66` — leg (vi) claims detection of
  a rewrite made while the pass runs; measured 0/10 (10/10 unnoticed when restored before
  the second read of that range).
  Reproduce:
  `J1_S=$S TMPDIR=$S python3 j1_probe.py race --runs 10 --hold-ms 3 --trigger pin_in`
  → `twopass=True code=True rehash=0` ten times, with `mem_obs.bytes_differing_from_archive == 1`.
- **Defect B (limit under-specified in the frozen prerequisite):**
  `kama-shokunin/.ufo/waves/round-55/preregistration.json:49` — the C1 limit names "two
  passes" without the per-range sweep interval (6.0–252 ms), the 17–31 ms of server life
  after the release, or the re-hash's 223 ms post-release position.
  Reproduce:
  `J1_S=$S TMPDIR=$S python3 j1_probe.py race --runs 5 --hold-ms 5 --trigger pin_post2`
  → `twopass=True code=True rehash=0` 5/5 with `mem_obs=1`, `server_lifetime_after_release_ms`
  17.5–31.4, `release_to_rehash 223.1–223.5 ms`.
- **Proposed fix (text, not applied — both files are frozen and a defect here is a
  finding):** `.ufo/waves/round-55/w1/out/J1Twopass/proposed-doc-limits.patch` — rewords
  leg (vi) to state the per-range sweep interval and that the leg is a set-change
  detector, and extends the Limits paragraph and the future preregistration sentence with
  the measured numbers.

No code change is proposed to the observation itself: the window is inherent to sampling
`/proc/<pid>/mem` at instants, and the frozen predicate only asserts what was read at
those instants. A real close would need a different instrument (e.g. a page-table write
watch, `bpf`/`fanotify` on the tree, or comparing `/proc/<pid>/smaps` dirty/soft-dirty
bits), which is outside this seat.

## Constraints and cleanup

- The lane was read only through a `git clone --shared` in my scratch; every counter run
  used that clone as `--repo`. No `git add/commit/checkout/stash/reset`, no jj mutation,
  no write under `kama-shokunin/` except this report and `w1/out/J1Twopass/`.
- Every replay was started by the frozen `bind_one()` on a loopback port and every tree
  was reaped by it (`reap(p, snap.items())`); `pgrep -af llama-server` after the series
  shows no process I started.
- One live clone at a time; scratch removed after the report was written. No counter was
  wrapped in a tracer. All evidence files cited below were copied out of scratch before
  removal.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/summary.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/char1.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/race-evade.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/race-detect.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/race-post2.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/race-post2-lifetime.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/j1_probe.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/j1_attacker.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J1Twopass/proposed-doc-limits.patch`
