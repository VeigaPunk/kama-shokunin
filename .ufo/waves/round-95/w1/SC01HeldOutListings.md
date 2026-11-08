# SC01HeldOutListings — round 95 wave 1, seat SC01 (held-out listing shapes for C1)

## Scope

Seat SC01HeldOutListings (leaf, no dispatch). Lane `kama-shokunin`. Attack surface: **C1
operability** — `tools/kama-probe.sh`'s `ROUTER_PY` file-state decision and the round-95 pass limit.
No tracked lane file was edited.

Revisions (full hashes): round-95 probe (`M1`) `f63256607916cdeb35580a7af315b5f4b54eba18`; round-94
base (`B`) `2011161d5e5612fa953708cf54084b7f10ce99b1` (byte-identical to the counter's
`BASE=a27656a4…`; `git diff --stat 2011161d a27656a4 -- tools/kama-probe.sh` printed nothing). Both
extracted with `git show <rev>:tools/kama-probe.sh`, driven against **lane-owned stub HTTP
listeners on free 127.0.0.1 ports** (ephemeral, port 0). `127.0.0.1:1234` was never contacted; no
POST/load/unload was sent anywhere. Fixtures: the counter's own `gguf()` helper
(`tools/round95-router-budget.py:144`) — "slow" = 600 000 tensor infos, F32 ne0=1 → `invalid`
(3 600 004 parser steps; 2.4 s/file idle, 8 s/file at load1≈150); "ok" = 1 tensor, data present.

## Commands and outputs (exit codes)

```
$ python3 -u harness2.py                      # exit 0; out/.../h2.log
$ python3 -u sweep.py --ks 2,4,6,8,12,16     # exit 0; out/.../sweep.log
$ python3 -u repeat.py 8 10 r95               # exit 0; out/.../rep_r95.log
$ python3 -u repeat.py 8 3 base              # exit 0; out/.../rep_base.log
$ python3 -u multipath.py                    # exit 0; out/.../multipath.log
$ timeout 35 python3 r95-probe-router.py work/h3b.json files 0  # exit 124, stdout ''
$ timeout 60 python3 r95-probe-router.py work/h3b.json files 0  # exit 0, stdout '0\tinvalid'
```

### H1–H8 as specified (r95 = f6325660 probe, base = 2011161d probe)

| shape | ncand | r95 verdict/reason | r95 wall | base verdict/reason | base wall | load1 | agree |
|---|---|---|---|---|---|---|---|
| H1 8 slow + 8 valid interleaved | 16 | MODEL_OK / router-unloaded-autoload | 19.13 s | MODEL_OK / router-unloaded-autoload | 19.63 s | 110.35 | yes |
| H2 2048 entries, 64 distinct slow | 2048 | MODEL_UNLOADED / router-model-invalid | 327.9 s | MODEL_OK / router-unloaded-autoload | 61.15 s | 146.79 | **no** |
| H3 1 entry, same slow path via 8 flag spellings | 1 | MODEL_UNLOADED / router-model-invalid | 11.14 s | MODEL_UNLOADED / router-model-invalid | 12.29 s | 153.13 | yes |
| H3b 1 entry, 8 **distinct** slow paths | 1 | MODEL_OK / router-unloaded-autoload | 35.73 s | MODEL_UNLOADED / router-model-invalid | 40.62 s | 158.74 | **no** |
| H3c 1 entry, 20 distinct slow paths | 1 | MODEL_OK / router-unloaded-autoload | 35.6 s | MODEL_UNLOADED / router-model-invalid | 51.8 s | 118.31 | **no** |
| H4 missing first, slow last | 2 | MODEL_UNLOADED / router-model-missing | 2.7 s | MODEL_UNLOADED / router-model-missing | 2.8 s | 92.80 | yes |
| H5 padded-valid next to same-size invalid | 2 | MODEL_OK / router-unloaded-autoload | 0.4 s | MODEL_OK / router-unloaded-autoload | 0.3 s | 92.80 | yes |
| H6 `loading` beside unloaded candidates | 2 | MODEL_LOADING / router-loading | 2.7 s | MODEL_LOADING / router-loading | 3.1 s | 90.81 | yes |
| H7 relative path in `status.args` | 1 | MODEL_OK / router-unloaded-autoload | 0.5 s | MODEL_OK / router-unloaded-autoload | 0.4 s | 89.47 | yes |
| H8 1 entry, 5 M-string token array | 1 | MODEL_OK / router-unloaded-autoload | 1.4 s | MODEL_OK / router-unloaded-autoload | 1.3 s | 87.43 | yes |

### K-sweep — one candidate naming K **distinct** slow files (ncand = 1, r95 budget 35 s)

| K | r95 verdict/reason | wall | base verdict/reason | wall | load1 | agree |
|---|---|---|---|---|---|---|
| 2 | MODEL_UNLOADED / router-model-invalid | 12.81 s | MODEL_UNLOADED / router-model-invalid | 14.87 s | 117.70 | yes |
| 4 | MODEL_UNLOADED / router-model-invalid | 25.36 s | MODEL_UNLOADED / router-model-invalid | 24.13 s | 122.43 | yes |
| 6 | **MODEL_OK / router-unloaded-autoload** | 35.59 s | MODEL_UNLOADED / router-model-invalid | 42.13 s | 127.75 | **no** |
| 8 | **MODEL_OK / router-unloaded-autoload** | 35.72 s | MODEL_UNLOADED / router-model-invalid | 49.46 s | 137.91 | **no** |
| 12 | MODEL_OK / router-unloaded-autoload | 35.78 s | MODEL_OK / router-unloaded-autoload | 60.64 s | 146.91 | yes (both green) |
| 16 | **MODEL_OK / router-unloaded-autoload** | 35.44 s | MODEL_UNLOADED / router-model-invalid | 40.48 s | 136.60 | **no** |

### Repeat — the **same** H3b listing (body sha256 `d70b1a542d1612a4`) 10× against r95

run1 `MODEL_OK router-unloaded-autoload` 35.78 s load1 137.17; runs 2–10 all `MODEL_UNLOADED
router-model-invalid` at 22.78 / 18.32 / 17.58 / 22.94 / 25.46 / 17.05 / 16.29 / 17.75 / 30.65 s
(load1 117.36 / 105.07 / 99.49 / 92.67 / 101.76 / 95.74 / 93.78 / 85.71 / 90.89). Base, same listing,
3 runs: `MODEL_UNLOADED router-model-invalid` at 56.99 / 51.38 / 60.12 s (load1 130.37 / 140.93 /
145.20).

## Findings

**F1 — BLOCKER: the count-derived limit is sized from the wrong quantity; one multi-path candidate
truncates the pass and false-greens.** `tools/kama-probe.sh:829` sets
`local limit=$((20 + 15 * ncand))` where `ncand` counts **candidate entries**, but one candidate's
work is the number of **distinct files** its `status.args` names: `file_state`
(`tools/kama-probe.sh:779-793`) collects *every* path-flag occurrence (`-m`, `--model`, `-mm`,
`--mmproj`, `-md`, `--model-draft`) and parses each distinct inode once, so one candidate can consume
N parses while the budget allows one. K-sweep: at ncand = 1 the budget is 35 s; at K = 6 distinct
slow files the parse needs ~40 s, `timeout` kills the python child, `router_file_states` returns
**no** line for that candidate, `nbad` stays 0, and `tools/kama-probe.sh:928` (`if [ "$nbad" -lt
"$ncand" ]; then unloaded=1; fi`) classifies the unloadable model as **loadable** → `MODEL_OK
router-unloaded-autoload`. Base grades the same listing correctly because its per-file 15 s deadline
and 60 s constant happen to cover K ≤ 8 here. Mechanism confirmed directly: `timeout 35 … files 0` →
**exit 124, stdout empty**; `timeout 60 … files 0` → **exit 0, stdout `0\tinvalid`** — the verdict
turns on whether the wall clock outran the parse, not on the bytes. This is the defect the round set
out to close (round-94 closure routed "truncated candidates stayed loadable" as D3/SC02 F2-F3,
CR01 F3/F8, MT01 M02/M10). The fix moves the constant 60 s to `20 + 15*ncand`, fixing the
*many-candidates* case (F4) but opening the *one-candidate-many-files* case, which no frozen cell
contains (every counter cell names one path per entry, so `ncand` equals the parse count there).

**F2 — BLOCKER: the round-95 verdict is still not a function of the bytes.** Repeat above: the
**same listing** (identical body sha256) graded `MODEL_OK router-unloaded-autoload` on run 1 and
`MODEL_UNLOADED router-model-invalid` on runs 2–10 — the verdict flipped with host load only. C1's
claim sentence is "the router file-state verdict is a function of the file's bytes"; for a
multi-path candidate it is a function of bytes **and** wall clock, the same defect class the round
claimed to eliminate. The frozen counter cannot see this: all ten cells use one path per entry.

**F3 — DEFECT: `MAX_STEPS` under-counts the string-array path, so the work bound is not a bound on
work.** `tools/kama-probe.sh:686` charges `steps[0] += n // 64` for a string array of length n,
while `skip_strings` (`:676-706`) performs n loop iterations plus a 1 MiB read per refill. Measured
on `work/fx/sa_*.gguf`: n=1 000 000 → 15 642 steps / 0.26 s (16.4 µs/step); n=5 000 000 → 78 173
steps / 0.90 s; n=20 000 000 → 312 662 steps / 4.26 s — ~13–16 µs per counted step versus ~0.7 µs
for the tensor path (`slow_0` = 3 600 004 steps / 2.43 s), so one `MAX_STEPS` buys ~20× more work
here; only `MAX_META` (512 MiB) really caps it. H8 graded `ok` at both revisions in 1.3–1.4 s, so
this did **not** flip a verdict at the sizes I ran — a bound weakness, not a false green.

**F4 — NOTE: H2 confirms the round-95 fix works for the many-candidates case.** Base truncates at
its 60 s constant and reports `MODEL_OK router-unloaded-autoload` (false green, 61.15 s); r95 allows
`20 + 15*2048` = 30 740 s, grades every candidate and reports `MODEL_UNLOADED router-model-invalid`
(327.9 s, rc=2) — the W03 discriminator generalised, as the claim says.

**F5 — NOTE: H5, H6 and H7 are unchanged between revisions.** H5 (valid file with zero-padded slack
beside a same-size invalid file) and H7 (relative path in `status.args`) both grade `MODEL_OK
router-unloaded-autoload` at **both** revisions: H7 is the documented round-89 rule (relative path →
undecidable → `-` → loadable); H5's padded-valid file parses `ok` (the slack is trailing, so `start +
off + nbytes > size` never trips) and the same-size invalid file is a *different inode*, so the
ctime-keyed memo (`tools/kama-probe.sh:605`) does not confuse them — an independent false-green
channel C1 does not address. H6 (`loading` beside an `unloaded` candidate with an invalid file)
reports `MODEL_LOADING router-loading` at both revisions: `router_refine`
(`tools/kama-probe.sh:905-930`) collects only `unloaded`-and-not-failed candidates for the file check,
but the `loading` value short-circuits at `:930` before the unloadable verdict is reported — it hides
a known-bad file behind a sibling's status.

**F6 — NOTE: H1 and H3 agree at both revisions.** H3 (one entry naming the same slow path through 8
flag spellings) costs 11.14 s at r95 — one parse, because `gguf_state` memoises on `(dev, ino, size,
mtime, ctime)`. H1 (8 slow + 8 valid interleaved) grades `MODEL_OK router-unloaded-autoload` at both
revisions: the valid candidates keep `nbad < ncand` true, so the verdict is loadable by the round-89
"a loadable matching entry still wins" rule. Neither is a round-95 regression.

## Deliverables

`.ufo/waves/round-95/w1/SC01HeldOutListings.md` (this report) and
`.ufo/waves/round-95/w1/out/SC01HeldOutListings/`: `h2.log` (H1–H8), `sweep.log` (K-sweep),
`rep_r95.log` / `rep_base.log` (repeats), `multipath.log`, `results2.json`, drivers `harness2.py`,
`sweep.py`, `repeat.py`, `multipath.py`, `loadtest.py`.

## Not run / limits of this seat

- **Not run:** the 64-burner synthetic-load arm of `loadtest.py` (written, not executed — the L1
  asked me to file). Shapes R2 (4 cand × 3 files), R3 (16 cand × 3 files), R4 (40 cand × 3 files)
  were **not run**; `multipath.py`'s R1 (1 cand naming `--model`/`--mmproj`/`--model-draft`, the
  argv llama.cpp renders for a child) ran at natural load and agreed at both revisions (17.32 s /
  23.11 s, load1 146.12 / 141.69). **Not run:** a path under `/proc`, `/sys`, `/dev`; a
  `status.args` that is not a list of strings; a `failed: true` sibling.
- I did **not** run the frozen counter `tools/round95-router-budget.py` (the L1 owns it); all
  findings above come from the probe bytes directly. Host load was 85–160 throughout (32 cores, many
  sibling lanes); every cell carries its own `load1`, no cell is a single-load measurement.
- Scratch `/fast/scratch/hyaku/kama-r95/SC01HeldOutListings/` removed after copying receipts. No
  burner was ever started (`pgrep -af SC01R95` → none); every stub listener and probe child I started
  was killed (`pgrep -af SC01HeldOutListings` → none).

VERDICT: falsified — the count-derived pass limit is sized from candidate entries, not from the
distinct files those candidates name, so one multi-path candidate truncates the pass and grades an
unloadable model `MODEL_OK` (F1), and the same listing's verdict still flips with host load (F2) —
C1's "verdict is a function of the bytes" does not hold.
