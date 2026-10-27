# J6Timing — twopass race characterization (C1, kama round 55)

**Verdict: a between-passes rewrite of the loaded `libggml-cpu` file is covered, not a practical bypass — the frozen counter printed `met=False` in 10/10 runs; the two-pass leg itself tripped in 15/30 replays (9/10 runs) and the per-pass archive comparison caught 22/30; the only escapes were the counter's own disclosed sampling gap (2/30 replays fully clean, 0/10 runs, and no escape at all when the rewrite was left on disk).**

Scratch: `/fast/scratch/hyaku/kama-r55/w1/J6Timing` (removed at the end). All receipts below are copied into
`.ufo/waves/round-55/w1/out/J6Timing/`.

---

## 1. Instrument integrity (before data)

| check | command | result |
|---|---|---|
| frozen counter bytes | `sha256sum kama-shokunin/tools/round54-replay-code-audit.py` | `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` = prereg `claims.C1.counter_sha256` |
| baseline at the freeze tip | `round54-replay-code-audit.py --repo <clone> --tip 9c60eae6... --scratch …/scratch-base --out …/receipts/base.out` → exit 0 | `bind=1 sealed=1 code=1 teardown=1 newrow=1 … twopass=3/3 rehash=0 met=True` (16.5 s); corroborated by the lane's own `.ufo/waves/round-55/c1/battery/control.out` |
| environment | `cat /proc/sys/kernel/yama/ptrace_scope` | `1` (counter reads only its descendants) |

`met=True` at the unmutated tip means every limb below is attributable to the mutant, not to a degraded environment.

## 2. Fixture and mutant (the probe, not a lane change)

```
S=/fast/scratch/hyaku/kama-r55/w1/J6Timing
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" checkout -q 9c60eae6f7ed84f7da93d219a406aadc30958c6c
# apply mutate-live-tool.diff (tools/kama-llamacpp-live.py, +111 lines), then
git -C "$S/lane" -c user.name=fx -c user.email=fx@invalid commit -m "J6Timing fixture mutant: …"
# => 2fc5c271956d278b417fd50f7a3c348ea4a7c10a   (parent 9c60eae6f7ed84f7da93d219a406aadc30958c6c)
```

`git -C "$S/lane" rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r55/w1/J6Timing/lane` (asserted before the
fixture commit; the only touched file is `tools/kama-llamacpp-live.py`, so `corpus/SOURCES.md` rows and therefore
the `newrow` leg are unchanged — `newrow=1` in every receipt).

What the mutant does (`mutate-live-tool.diff`, function `_j6_flipper_start`, call site at what is
`tools/kama-llamacpp-live.py:2464-2473` in the fixture):

* a **same-uid daemon thread inside the live tool** (the server's parent, same uid as the counter);
* it rewrites **one byte per `libggml-cpu-*.so` variant** in the unpacked tree, located from that file's ELF
  program headers at `exec PT_LOAD.p_offset + 0x10` — i.e. inside `_init`, which is mapped `r-xp` but runs only
  at `dlopen` time (already past), so the rewrite cannot change what the server executes or crash it;
* **tight loop** (`pread`+`pwrite` on an open fd, per file) from **immediately before `ready.json`** (the thread is
  started just before `hold_for_witness`, which writes `ready.json` as its first act) **until `release`** appears in
  the witness dir; at exit it appends one JSON line to `J6_FLIP_LOG` with flips/window/orig/final bytes.

Offsets are identical for all variants except `libggml-cpu-sapphirerapids.so` (`0x16010` vs `0x15010`);
`libggml-cpu-zen4.so` is the one this host loads, and it is the only one the counter observes.

**Mechanism (why a file rewrite is visible at all).** The counter compares its `/proc/<pid>/mem` reads against its
own archive bytes (`tools/round54-replay-code-audit.py:541`). A read-only private file mapping shares the page-cache
page, so a same-uid `pwrite` to the mapped `.so` changes what `/proc/<pid>/mem` returns. Verified independently
before the series (`mmaptest2.py`, `LD_LIBRARY_PATH=/home/vgpnk/.local/opt/llama-b11909`):

```
exec row: lo=0x7f15489b7000 hi=0x7f1548adc000 file_off=0x15000 len=0x125000
file byte at 0x15010 = b'\x85' ; mem byte = b'\x85'
after flip: mem byte = b'\x84' ; file byte = b'\x84'
VISIBLE_IN_MEM: True
```

This is also why the battery's `m-member-flip` was a rehash-only kill: it flipped at EOF-32, outside every
`PT_LOAD`, so no mem read could see it. The J6Timing flip is inside the mapped exec page, which is what puts the
two-pass leg in play.

## 3. The 10 frozen-counter runs

Command per run (`run10.py`; each run gets its own `--scratch`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py \
  --repo $S/lane --tip 2fc5c271956d278b417fd50f7a3c348ea4a7c10a \
  --scratch $S/run$i --out $S/logs/mut$i.out
```

All ten exited **1** (`met=False`). Summary lines (`receipts/mut*.out` line 2):

```
run1  bind=1 sealed=1 code=0 teardown=1 newrow=1 … coderuns=0/3 … twopass=1/3 rehash=0 met=False
run2  … coderuns=2/3 … twopass=2/3 rehash=1 met=False
run3  … coderuns=0/3 … twopass=1/3 rehash=1 met=False
run4  … coderuns=1/3 … twopass=2/3 rehash=3 met=False
run5  … coderuns=1/3 … twopass=1/3 rehash=2 met=False
run6  … coderuns=1/3 … twopass=3/3 rehash=1 met=False
run7  … coderuns=1/3 … twopass=1/3 rehash=1 met=False
run8  … coderuns=1/3 … twopass=1/3 rehash=2 met=False
run9  … coderuns=0/3 … twopass=1/3 rehash=2 met=False
run10 … coderuns=1/3 … twopass=2/3 rehash=0 met=False
```

| metric (10 runs = 30 replays) | count |
|---|---|
| runs with `met=True` | **0/10** |
| runs where the two-pass leg tripped (≥1 replay) | **9/10** |
| runs where the rehash leg tripped (≥1 replay) | 8/10 |
| replays where the two-pass leg tripped | **15/30 (50 %)** |
| replays where the rehash leg tripped | 13/30 (43 %) |
| replays where the per-pass archive comparison tripped | 22/30 (73 %) |
| replays reported fully clean (no leg) | 2/30 (7 %) |

## 4. Per-replay legs, joined with the flipper's own log

`correlate.py` (→ `correlate.json`) joins each flipper log line (its `tree` path names the run and `work-bN`) with
that replay's detail lines. `code` = "mapped bytes … differ from the archive member"; `twopass` = "executable
bytes differ between the two observation passes"; `rehash` = "changed after the observation".

```
run  rp   flips  win_s left_fl  code twopass rehash
  1  b1  842324  0.545   False  True   False  False
  1  b2  198436  0.126   False  True    True  False
  1  b3  290668  0.192   False  True    True  False
  2  b1  833980  0.544   False False   False  False   <-- all clear (both passes read the archive byte)
  2  b2  273882  0.178    True False   False   True   <-- passes clean, caught only by rehash
  …    (full table in correlate.json / receipts/mut*.out)
  6  b1  885892  0.564   False  True   False  False   <-- both passes agree on the FLIPPED byte
  6  b3  200088  0.128   False  True   False  False   <--   caught by the archive comparison only
 10  b3  163408  0.106   False False   False  False   <-- all clear
```

Derived facts (`correlate.py` output):

* `left_flipped == rehash_trip` for **all 30** replays (13/13): the rehash leg is a deterministic function of the
  byte left on disk at exit — no race there.
* `twopass_trip ⊂ code_trip` for all 30 replays: the two-pass mismatch is reported as a `code:` problem
  (`tools/round54-replay-code-audit.py:714-715`) and the `twopass` leg is computed from exactly those problems
  (`:827`).
* 8/30 replays had **both** passes read the archive byte (code clean). Of those, 6 were caught anyway because the
  flipper left the file flipped (rehash); the remaining **2/30** were fully clean.
* The toggle rate is 1.49–1.60 Mflips/s across 14 files (per-file period ≈ 9 µs) — the state sampled by pass 1 and
  pass 2 is effectively independent, which is why the observed two-pass trip rate is 50 % (15/30).

**Did the counter ever report a flipped twopass?** Yes — 15/30 replays, e.g. `receipts/mut1.out`:

```
detail: code b2: code: mapped bytes 7fb6c9207000-7fb6c932c000 (offset 00015000) of llama-b11909/libggml-cpu-zen4.so differ from the archive member
detail: code b2: code: executable bytes differ between the two observation passes
detail: rehash b2: 8 observed archive paths re-stat'ed and re-hashed after the replay exited, inode and digest unchanged
```

(the third line is the *restore-before-exit* case: the file was clean again at rehash time, and the rewrite was still
caught by the pass reads.)

And the complementary case — a rewrite **resident across both passes** (both snapshots agree, so the two-pass leg
passes) is still caught, because each pass compares against the counter's own archive (`mut1.out`, b1):

```
detail: code b1: code: mapped bytes 7f5f8f807000-7f5f8f92c000 (offset 00015000) of llama-b11909/libggml-cpu-zen4.so differ from the archive member
detail: code b1: code: mapped bytes 7f5f8f807000-7f5f8f92c000 (offset 00015000) of llama-b11909/libggml-cpu-zen4.so differ from the archive member
detail: rehash b1: 8 observed archive paths re-stat'ed and re-hashed after the replay exited, inode and digest unchanged
```

## 5. Conclusion — bypass or covered

**Covered.** Three independent sampling instants are defended differently, and the data shows each doing its job:

1. **Per-pass archive comparison is the operative guard.** Each pass reads every executable range from
   `/proc/<pid>/mem` and compares it with the counter's own archive bytes (`:541`). Any rewrite resident at a read
   fails the run — 22/30 replays, including 7/30 where both passes agreed on the flipped byte and the two-pass leg
   was silent. A same-uid rewrite of the *loaded* library cannot hide from this while it is resident, because the
   page-cache page is exactly what the server's mapping and the counter's read share.
2. **The two-pass agreement is a corroborating window, not the sole guard.** It fired in 15/30 replays and never
   fired without the code leg also firing (`twopass_trip ⊂ code_trip`). Its real contribution is diagnostic: it
   distinguishes a rewrite that *changed between the passes* from a rewrite that was *statically present*, which is
   the information the code leg alone cannot convey. No condition was found in which the two passes disagreed and
   the counter failed to report it.
3. **The post-exit rehash is deterministic** for anything left on disk: 13/13 left-flipped replays tripped, and
   0 left-clean replays tripped.

Residual gap (already disclosed at `tools/round54-replay-code-audit.py:87-90`: "a library rewritten and restored
between those instants … is not observed"): 2/30 replays were reported fully clean while the target byte was being
rewritten ~1.5 M times/s around them. That is a sampling gap, not a between-passes hole — a rewrite that is reverted
before every sampling instant is by construction invisible to a state-sampling counter. It also does not escalate
to a run-level bypass here: a run needs all three replays clean (`met` requires `coderuns=3/3`, `twopass=3/3`,
`rehash=0`), i.e. ≈ 7 %³ ≈ 0.03 % under independence; observed 0/10. Note also that this experiment cannot turn the
gap into code execution: the flipped byte is in `_init`, which the running server never re-executes. Flipping hot
`.text` instead would put a modified instruction in the executed image, but it would also risk a `SIGILL` that
fails the `bind` leg and confuses the attribution — the same reason the battery used `libggml-rpc`'s cold tail.

## 6. Findings (frozen counter; reported, not applied)

**F1 — the two-pass leg has no detection power beyond the code leg (by construction).** `code_observe` already
compares each pass's `/proc/<pid>/mem` read against the counter's own archive member
(`tools/round54-replay-code-audit.py:541`); the two-pass problem is appended only when the two *snapshots* differ
(`:714-715`) and the `twopass` leg is then defined as "no such problem in `cprobs`" (`:827`). A byte pair that
differs between passes cannot both match the archive, and a byte pair that agrees but differs from the archive is a
code problem regardless. Empirically: 0/30 replays where `twopass` tripped alone, 7/30 where the archive comparison
was the only trip. This is not a soundness bug — the predicate requires both limbs, and it is worded correctly — but
the SCORECARD/C1 predicate should not credit the two-pass limb with independent detection: it is the limb that makes
a changing rewrite *legible*, while the archive comparison is the limb that *catches* it.

**F2 — observability: a tripped two-pass leg leaves no `twopass` detail line.** The trip is emitted under the `code`
prefix (`detail: code bN: code: executable bytes differ between the two observation passes`, `:715`), while a
`twopass bN:` line is written only when the passes agreed (`bind_one`'s `if not cprobs` block). A reader grepping
receipts for `twopass ` therefore sees only the passing replays. Proposed (NOT applied — counter is frozen), as a
minimal second line at the trip site:

```diff
--- a/tools/round54-replay-code-audit.py
+++ b/tools/round54-replay-code-audit.py
@@ -712,6 +712,8 @@ def bind_one(tree, rpath, S, tag, vocab, arc, detail):
                         if second is not None:
                             anon = sum(1 for pr in cprobs if pr.startswith("code: anonymous executable"))
                             if first["snaps"] != second["snaps"]:
                                 cprobs.append("code: executable bytes differ between the two observation passes")
+                                detail.append(f"twopass {tag}: executable bytes differ between the two "
+                                              f"observation passes")
                             cobs = first
```

(`detail` is the list `bind_one` already appends to; this adds one line per tripped replay and changes no leg.)

**F3 — the residual gap quantified (disclosure, not a defect).** A restore-before-exit attacker whose rewrites are
never resident at a pass read would have been clean on 8/30 replays (27 %) in this series; with the toggle actually
leaving the byte flipped half the time, 2/30 (7 %) were clean and the other 6 were caught only by the rehash. Both
numbers sit inside the frozen limits statement (`:87-90`); the C1 predicate should keep that limit wording if it is
ever restated.

## 7. Limits of this experiment

* One byte per variant, at `exec PT_LOAD + 0x10` (`_init`, size 0x1b): the probe measures *detection of a file
  rewrite*, not execution of foreign code. Flipping hot text would risk a server `SIGILL` and confound attribution.
* All 14 `libggml-cpu-*` variants are flipped (like the battery's `m-member-flip`), but only `libggml-cpu-zen4.so`
  is mapped on this host, so only its flip is observable by the counter; the other 13 flips are inert.
* The flipper is a same-uid thread in the live tool, i.e. inside the replay's process tree and not traced
  (no `strace`/`ltrace` anywhere); it starts before `ready.json` and stops at `release`, covering `env_leg`,
  `observe` (tokenize/detokenize), `sealed_exe`, both `code_observe` passes, and the replay's exit.
* 10 runs × 3 replays = 30 binds; the teardown replay is `SIGKILL`ed before any `release`, so it contributes no
  flipper log line and no legs (it is the `teardown` limb, green 10/10).
* Two-pass independence: the observed 50 % trip rate matches the independent-state model for a ≈9 µs per-file
  toggle period against a multi-ms observation window; it is not evidence of a specific scheduling correlation.

## 8. Hygiene / tooling

* `pgrep -af llama-server` after the series → 0 processes; the counter's own `reap()`/teardown closed every server
  (each receipt: `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`).
* No writes to the lane, the fleet root, sibling lanes or `shokuknow`: the fixture clone and all scratch lived under
  `/fast/scratch/hyaku/kama-r55/w1/J6Timing` (now removed); deliverables are only in this out dir and this report.
* Tooling: no installs or upgrades were needed (python3 3.14.8, git, readelf/objdump already present); `pacman` was
  not run.

## 9. Artefact index (this directory)

| path | what |
|---|---|
| `mutate-live-tool.diff` | the fixture patch (live tool; +111 lines) |
| `fixture-commit.txt` | fixture commit / parent / identity |
| `receipts/base.out` | my unmutated control at 9c60eae (exit 0, `met=True`) |
| `receipts/mut1.out … mut10.out` | the ten frozen-counter receipts (exit 1 each) |
| `series.json` | per-run summary parsed from the receipts |
| `j6-flip.log` | one line per covered replay: tree, window, flips, orig/final bytes |
| `correlate.py`, `correlate.json` | per-replay join of flipper log ↔ counter legs |
| `run10.py` | the 10-run driver |
| `mmaptest2.py` | the page-cache/mem visibility micro-test |
