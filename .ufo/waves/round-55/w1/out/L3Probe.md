# L3Probe — round 55 / w1 — C1 observation-window probe

Verdict: PASS — the frozen C1 counter at 9c60eae6f7ed84f7da93d219a406aadc30958c6c met=True in 5/5 timed runs (16.50–16.68 s wall, spread 0.18 s), and the twopass agreement window is not externally observable: the receipt records only the agreement verdict, never pass timestamps, per-pass hashes, or a window extent — exactly what the preregistration's frozen sampling limit discloses ("the counter samples state ... a library rewritten and restored between those instants is not observed"). No defect found; no edits proposed.

## What I ran

Scratch `S=/fast/scratch/hyaku/kama-r55/w1/L3Probe` (`TMPDIR=$S`), one shared clone:

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # rev-parse toplevel == $S/lane, tip 9c60eae6 present
sha256sum $S/lane/tools/round54-replay-code-audit.py
  -> c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  (== preregistration C1 counter_sha256)

for i in 1..5:
  ~/.local/bin/time -o $S/run$i.time -f "elapsed_s=%e user_s=%U sys_s=%S exit=%x maxrss_kb=%M" \
  python3 $S/lane/tools/round54-replay-code-audit.py --repo $S/lane \
    --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --scratch $S/scratch-run$i \
    --out <out>/receipt-run$i.json > $S/run$i.stdout 2> $S/run$i.stderr
```

Lane read-only throughout; clone verified via `git rev-parse --show-toplevel`; receipts written directly to this out dir; every run's stderr is 0 bytes.

## Wall times (all exit 0; full table in timing.tsv)

| run | start UTC | elapsed s | user s | sys s | maxrss KB | summary line |
|----|-----------|-----------|--------|-------|-----------|--------------|
| 1 | 13:55:42 | 16.67 | 4.91 | 1.46 | 726984 | met=True |
| 2 | 13:55:59 | 16.64 | 4.92 | 1.42 | 728456 | met=True |
| 3 | 13:56:15 | 16.68 | 4.95 | 1.56 | 727092 | met=True |
| 4 | 13:56:32 | 16.54 | 4.94 | 1.49 | 727736 | met=True |
| 5 | 13:56:49 | 16.50 | 5.07 | 1.55 | 727144 | met=True |

Mean 16.606 s, min 16.50, max 16.68, spread 0.18 s (1.1%). All 5 runs: exit 0, `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True` — identical verdicts to the L1 build measurement `measured/c1-build.out`. Run-to-run variance is dominated by server startup + archive/model download (each replay re-downloads); the measurement itself is stable.

## Receipt per-run detail (twopass/rehash), identical across all 5 receipts

Each receipt carries, per committed round-48 v5 receipt (b1, b2, b3):

```
detail: twopass b<n>: both observation passes byte-identical over 16 range reads
detail: rehash b<n>: 8 observed archive paths re-stat'ed and re-hashed after the replay exited, inode and digest unchanged
```

i.e. 3 twopass + 3 rehash lines per receipt, 16 executable range reads per pass, 8 archive files observed, 0 problems. Copy of record: `receipt-run1.json` … `receipt-run5.json` in this directory.

## Why the twopass agreement window is not observable from outside

The two passes run back-to-back inside `bind_one` (`tools/round54-replay-code-audit.py:709-717`):

```
709  first  = code_observe(pid, utree, arc, cprobs, collect=True, own=got)
711  second = code_observe(pid, utree, arc, cprobs, collect=True, own=got)
714  if first["snaps"] != second["snaps"]:
715      cprobs.append("code: executable bytes differ between the two observation passes")
717  cobs["ranges"] = first["ranges"] + second["ranges"]
```

1. **The receipt records only the verdict, never the window.** The per-pass evidence (`snaps`, a `{path|range: sha256}` dict collected in `code_observe`, lines 523-524) lives and dies as a local; only the boolean comparison at line 714 escapes — rendered as the `twopass b<n>` detail line (line 799) or the problem string. No pass timestamps, no per-pass digests, no window extent appear in the receipt, so from the receipt alone you cannot tell when each pass ran or how far apart they were. Nothing else writes to the receipt between the passes either (lines 709-717 contain only the two calls and the comparison).

2. **The observation is invisible to the observed.** Each pass reads `/proc/<pid>/maps` then `os.pread`s `/proc/<pid>/mem` (`code_observe`, lines 467-560) — no ptrace attach/stop, no writes, no signal to the target. Between the passes the server keeps running normally; a target cannot detect that it was sampled, let alone when the sampling bracket opened or closed. (Watching the *counter's* own syscalls would reveal its reads, but that is instrumentation — explicitly out of scope for this probe — and still would not certify anything about the window to a third party reading the receipt.)

3. **This matches the preregistration's frozen sampling limit.** `preregistration.json` → `limits`: "the counter samples state (two passes and a post-exit re-hash), so a library rewritten and restored between those instants is not observed". The counter's own docstring (lines 87-89) is the same disclosure: "the counter samples state - a path digest at receipt time in the live tool, and one or two /proc/<pid>/mem passes during the hold; a library rewritten and restored between those instants, or rewritten after the post-exit re-hash, is not observed". The window's external unobservability is the flip side of that limit: the counter certifies byte-agreement at its sampling instants only, and the receipt is deliberately silent about everything in between. A rewrite-and-restore confined to the inter-pass gap (or post-rehash) is undetectable by design and by disclosure — consistent, not contradictory.

The window itself is real but tiny: pass 1 → pass 2 is separated only by the duration of one full maps+pread sweep (16 range preads, milliseconds), versus the 16.6 s whole-run wall dominated by server startup, downloads, three sequential replays and the teardown wait.

## Hygiene / leftovers

- `pgrep -af llama-server` before and after: no processes (every replay torn down; teardown line present in each receipt).
- Counter bytes unchanged (sha256 == preregistration `counter_sha256`); counters/controls untouched; lane clone removed with scratch.
- Tooling: no installs/updates needed (`~/.local/bin/time` GNU time already present; pacman untouched per host guard).

## Artifacts

- `.ufo/waves/round-55/w1/out/L3Probe/receipt-run{1..5}.json` — the five `--out` receipts cited above
- `.ufo/waves/round-55/w1/out/L3Probe/timing.tsv` — per-run wall/user/sys/exit/rss
