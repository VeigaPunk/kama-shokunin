# SC02SuperlinearSweep — kama round 92 wave 1 (operability)

Seat: SC02SuperlinearSweep. Lane: kama-shokunin. Lane read-only except this report and my out dir.

## Scope

Sweep the whole probe at M2 for any remaining super-linear or fork-per-item construct on
listener-controlled data, beyond the three round-92 fixes; re-measure the round-91 SC02 F1-F3
shapes at M2 and BASE; attribute each candidate with a one-construct-changed copy.

Revisions measured (full hashes, probe sha256):

- **M2** = `fa8aedb73d18448383c7a4d75405aba448fe8e38`, `tools/kama-probe.sh` sha256
  `36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962` (matches the frozen
  counter's `measured/c2.out`).
- **BASE** = `ed018ca0fa956c5052b3dc6b714a2cb72973da21`, probe sha256
  `0aa43573be3a52fa22d9b419049814133324e423dcd22429f107ad28ee0a75da`.

Method: lane-owned stub HTTP servers on free 127.0.0.1 ports (never 1234; GET only), one held-out
cell per body shape; attribution by candidate copies of the probe with exactly one construct
changed (candidates in my scratch, never in the lane). Every answer body is under the probe's
4 MiB cap except where noted. Host: 32 cores, load 20-140 during these runs (`/proc/loadavg`
printed next to every number) — **the load was high and rising, so every timing below is a
within-run doubling ratio, and several runs are reported as ratio-only**.

## Commands and outputs (exit codes)

| # | Command (cwd = my scratch) | Exit | Result |
|---|---|---|---|
| 1 | `git -C wt checkout --detach fa8aedb7…` / `git show …:tools/kama-probe.sh` | 0 | probe bytes as above |
| 2 | `python3 driver.py A` (F1-F3 shapes at M2 and BASE) | 0 | receipt `phaseA.out` |
| 3 | `python3 basef3.py` (BASE F3c/F3d shapes) | 0 | receipt `basef3.out` |
| 4 | `python3 driver_c.py` / `driver_d.py` / `driver_e.py` (candidate battery) | 0/1 | receipts `phaseE1/E3/E4.out` |
| 5 | `python3 attrib.py` (isolated json_array construct, min-of-3, interleaved) | 0 | receipt `jmicro2.out` |
| 6 | `python3 final2.py` (interleaved probe-level json_array attribution) | 0 | receipt `final2.out` |
| 7 | `python3 final3.py` (rows fixed, listener bytes doubled) | 0 | receipt `final3.out` |
| 8 | `python3 wide.py` (print_table width amplification) | 0 | receipt `wide.out` |
| 9 | `python3 det2.py` (output determinism, fixed port) | 0 | 3/3 runs byte-identical, sha `e739300147fb2c1d` |
| 10 | `python3 dl.py` (router autoload, N unloaded candidates) | 0 | verdict `router-unloaded-autoload` at every N |
| 11 | `python3 mixed2.py` (one wide row among narrow rows) | 124 (host load) | partial, see F5 |
| 12 | `python3 verdict.py` (missing / fast-invalid / slow model file) | 0 | receipt `verdict.out` |
| 13 | `python3 fg2.py` / `fg3.py` (candidate-count verdict flip, M2 and BASE) | 0 | receipts `fg2.out`, `fg3.out` |

No tool was installed or upgraded (none needed). No network access was used.

## Findings

**F1 — NOTE (the round-92 fixes hold; re-measured F1-F3 at M2 and BASE).**
`tools/kama-probe.sh` at M2 is linear on all three round-91 shapes; BASE is quadratic on all three.
Within-run doubling ratios (N→2N), `phaseA.out` / `basef3.out`:

| shape (N→2N→4N) | M2 seconds | M2 ratio | BASE seconds | BASE ratio |
|---|---|---|---|---|
| F1 jstr, 100k→200k→400k backslashes | 0.37→0.53→0.84 | 1.43, 1.58 | 4.14→16.16→57.50 | **3.90, 3.56** |
| F2 jstr, 100k→200k→400k quotes | 0.33→0.44→0.69 | 1.33, 1.57 | 4.00→15.43→60.63 | **3.86, 3.93** |
| F3a router_refine wildcard, 10k→20k→40k unloaded | 0.56→0.84→1.53 | 1.50, 1.82 | 3.44→15.72→64.69 | **4.57, 4.11** |
| F3b router_refine same-id, 10k→20k→40k | 0.52→0.89→1.45 | 1.71, 1.63 | 4.23→16.47→69.01 | **3.89, 4.19** |
| F3c served_persist snapshot, 4k→8k→16k path ids | 0.53→0.54→0.76 | 1.02, 1.41 | 36.52 (4k) → killed at 120 s | **>3** |
| F3d served_persist snapshot, 25k→50k→100k slash-free id | (M2 n=50k→200k: 0.26→0.43) | 1.15, 1.43 | 2.71→7.41→31.20 | **2.73, 4.21** |

So the three round-92 fixes (`AWK_JSTR` one-pass escape, `cand+=(...)` array, one-pass
`AWK_NORM` `served_persist`) are effective; the quadratic behaviour they targeted is gone at M2.

**F2 — DEFECT (operability): `json_array`'s string append is super-linear in the number of rows,
amplified by the listener's answer size.** `tools/kama-probe.sh:252-258`:

```
json_array() { local out='' first=1 r
  for r in "$@"; do
    if [ "$first" -eq 1 ]; then out=$r; first=0; else out="$out,"$'\n'"$r"; fi
  done
  printf '%s' "$out"; }
```

Each iteration copies the whole accumulated string, so the cost is O(R² · L) for R rows of
L bytes each. R is the registry row count (operator-controlled), but L is the **listener's**
served-model length — one hostile /v1/models answer is copied into every registry row, and the
probe then re-copies the accumulated string once per row. Measured on a one-row registry whose
single stub answers with one 200 000-byte id (`phaseE3.out`, load 23-28 — the cleanest window):

| rows (payload 200 000 B/row) | M2 seconds | M2 ratio | cand-json_array seconds | cand ratio |
|---|---|---|---|---|
| 8 → 16 | 1.32 → 2.79 | 2.11 | 1.26 → 2.59 | 2.05 |
| 16 → 32 | 2.79 → 6.47 | 2.32 | 2.59 → 5.30 | 2.05 |
| 32 → 64 | 6.47 → 15.86 | 2.45 | 5.30 → 10.49 | 1.98 |

Ratios > 2 (2.11 → 2.45) versus the one-construct-changed copy's flat ≈2.0 is the signature of a
quadratic term. Attribution, isolated construct only (`attrib.py`, min-of-3, interleaved,
total output fixed at 3.2 MB so only R changes): string-append 1.262→3.273→5.361→9.147 s at
R=16/32/64/128 versus array-append 0.594→0.920→1.694→2.563 s (ratio 2.12/3.56/3.16/3.57).
Probe-level, interleaved, non-JSON path (`final.out`, `final2.out`): M2 16→32→64 rows =
2.86→6.29→13.94 s (ratios 2.20, 2.22) versus cand-json_array 2.13→4.66→12.88 s
(ratios 2.19, 2.76) — the JSON path shows the wider gap (M2 15.86 s vs cand 10.49 s at 64 rows).
**Caveat on the attribution copy:** my `cand-json_array.sh` joins with `","` where the original
joins with `",\n"`, so its stdout is 1-1 600 023 bytes shorter than M2's at the same row count
(e.g. 64 rows: 12 846 140 B vs 11 246 117 B). The attribution is therefore on *time*, not on
byte-identity; a byte-preserving fix must keep the `",\n"` separator (e.g. build the separator
into the array elements), which is what I recommend below. This is **not** a listener-only shape:
it needs several registry rows, so R is operator-chosen and L is listener-chosen; the defect is
the O(R²·L) term, not a fork per listener item.

**F3 — DEFECT (operability, same construct): `print_table`'s per-cell padding is super-linear in
the listener's widest answer.** `tools/kama-probe.sh:261-297` computes one width per column and
then pads *every* row's cell to that width with `printf -v pad '%-*s'`, so a single wide
listener row inflates every other row's output. Measured with one 200 000-byte id per row,
non-JSON path (`wide.out`, load 92-102): M2 8→16→32 rows = 4.97→11.79→24.70 s
(ratios 2.37, 2.10) versus cand-print_table (padding removed) 5.97→12.30→23.70 s
(ratios 2.06, 1.93) and output bytes 1 802 578→3 404 973→6 609 741 versus 1 602 498→3 204 882→
6 409 650 (the padded copy emits 200 091 more bytes per row block). Removing the padding removes
the super-linear term, so the amplification is attributable to `print_table`'s padding, not to
the listener answer itself.

**F4 — NOTE (bounded): no fork-per-item construct survives on listener-controlled data.**
Every per-item loop over listener data in the M2 probe is now a single pass:
`served_ids` (one python per body, `probe-M2.sh:398`), `model_matches` (one awk,
`:464`), `router_match` (one awk, `:479`), `router_entries` (one python, `:777`),
`served_persist` (one awk, `:1490`), `AWK_JSTR` (one awk, `:225`). The router file-state check
`router_file_states` (`:782`) takes the candidate list as **command-line arguments**
(`"${cand[@]}"`, `:849`) — one argv word per candidate, so its cost is O(R) argv growth, and
the python side loops `for idx in sys.argv[3:]` (`:752`) re-opening the body per index: the
the per-index work is `os.stat`/`os.open` per candidate, i.e. O(R) syscalls with a 4 s internal
deadline (`MAX_STEPS`/`DEADLINE`, `router_py.py`). Measured at N=20 000 unloaded candidates with
model-file args (`phaseD.out` D3 / `phaseE4.out` E6): 0.75 s and 0.75 s respectively, verdict
`MODEL_UNLOADED`/`router-model-missing` — no timeout, no false green at that scale. The *shared*
deadline is nevertheless harmful — see F6.

**F5 — NOTE (partial, host-load limited): one wide listener row among narrow rows is
super-linear in the number of registry rows.** `mixed2.py` (1 wide + 7 narrow rows, 200 000-byte
id) gave M2 38.16 s at load 121-126 for **1 950 bytes** of stdout — the wide row's served model
is *not* in the table output, so this shape exercises the row-count term (F2/F3) without the
byte amplification. The run was cut off by the 280 s cap before the attribution copy finished,
so the ratio is not attributed; treat as a partial number, not a finding.

**F6 — DEFECT (operability, false green): the router model-file check has ONE shared deadline
for all candidates, so a listener can flip `MODEL_UNLOADED` to `MODEL_OK` by repeating a
slow-to-parse model file.** `tools/kama-probe.sh:782-791` runs **one** python process for **all**
candidates (`timeout 8 python3 -c "$ROUTER_PY" "$body" files "$@"`), and `ROUTER_PY` gives that
process a single process-wide budget: `MAX_STEPS, DEADLINE = 4_000_000, time.monotonic() + 4.0`
(`router_py.py:14`). `gguf_state` returns `-` ("undecidable") once that shared budget is spent
(`router_py.py:54`), and `router_refine` counts only `missing|invalid` as bad
(`probe-M2.sh:845-849`), so an undecided candidate counts as *loadable* and
`nbad < ncand` sets `unloaded=1` → `RT_VERDICT=MODEL_OK`, `RT_REASON=router-unloaded-autoload`.

Reproduced at M2 (`fg2.out`, `fg3.out`): a router listing N unloaded entries whose
`status.args` all name the same large-but-invalid GGUF (`slow.gguf`, 4.8 MB, 200 000 tensor
infos) is graded

| N candidates (all naming the same invalid file) | M2 verdict | M2 reason | M2 exit |
|---|---|---|---|
| 1 | `MODEL_UNLOADED` | `router-model-invalid` | 2 (drift) |
| 2 | `MODEL_UNLOADED` | `router-model-invalid` | 2 |
| 5 | `MODEL_UNLOADED`¹ | `router-model-invalid`¹ | 2¹ |
| 6 … 60 | `MODEL_OK` | `router-unloaded-autoload` | **0 (no drift)** |

¹ the N=5 boundary moved between runs: at load 114-126 the flip was at N=5 (`fg2.out`,
first run), at load 68-105 the flip was at N=10 (`fg2.out`, final run). The threshold is a
**race against the shared 4 s deadline**, so it moves with host load and machine speed.

The per-candidate states show the mechanism exactly (isolated `ROUTER_PY` run, one process,
6 candidates): `['invalid', '-', '-', '-', '-', '-']` — only the first candidate is decided; the
rest hit the shared budget and are abandoned. So the same listener body is graded "drift, the
model file is invalid" at small N and "green, the router will autoload it" at larger N: **the
verdict is a function of the listener's candidate count and of host load, not of the model's
state.** A listener that names one bad file many times (or many files, the first of which is
slow) suppresses the drift verdict. The `missing` control is unaffected
(`router-model-missing` at N=1 and N=6, M2 and BASE) because the file stat fails immediately
and never spends the budget, so the flip needs a file that is *slow* to parse — i.e. exactly the
shape a real multi-gigabyte GGUF has.

**This is a carried defect, not a round-92 regression, and it is nondeterministic:**
`fg3.out` shows M2 and BASE producing *different* verdicts for the same N=6 body in the same
run (M2 → `MODEL_UNLOADED`/`router-model-invalid`, BASE → `MODEL_OK`/`router-unloaded-autoload`),
and an earlier run at higher load had both at `MODEL_OK` (`fg3.out`, first run). The mechanism
is revision-independent (BASE has the same `router_file_states` and the same `ROUTER_PY`), but
the verdict it produces is load-dependent, so a round that measures it once can record either
answer. It is outside the frozen C2 predicate (the counter's D9/L-cells never name a slow model
file) and outside the C1 rows, so it does not falsify C2's 15 cells — but it is a real
operability/harm defect (a false green, and a nondeterministic one) that a future round should
own.

**F7 — NOTE (no defect): the listener's header cannot drive the `curl -w` parsing into a
super-linear shape.** `fetch` (`probe-M2.sh:348-375`) parses `w` with `${w%%|*}`,
`${w#*|}`, `${w%%|*}` again and `${w##*|}`; measured in isolation these are O(n) with a
constant factor ≈2 (`micro3.py`: 400 000-byte `w`, 0.004–0.015 s per operation, all four
operations < 0.016 s) because the `|` separators are near the ends of the string, and bash's
pattern removal is O(n·pattern) not O(n²). A 400 000-byte `Content-Type` header is refused by
curl itself (exit 100, `ct.py`), so the reachable `w` is bounded. `${s//…}` global replacements
are also safe here: a *matching* replacement is the slow case (59 s for 400 000 bytes,
`micro4.py`) but no listener-controlled value reaches a matching global replacement — `jstr` uses
awk now and `persist_clean` (`:1475`) sees only probe-generated fields (its `tr` is bounded by
the field length).

## Deliverables

- Report: `.ufo/waves/round-92/w1/SC02SuperlinearSweep.md` (this file).
- Out dir `.ufo/waves/round-92/w1/out/SC02SuperlinearSweep/`: receipts `phaseA.out` (F1-F3 at
  M2 and BASE), `basef3.out` (BASE F3c/F3d), `phaseE1.out` (control-char id, slash id),
  `phaseE3.out` (json_array attribution, JSON path), `phaseE4.out` (print_table attribution),
  `final.out`, `final2.out`, `final3.out` (interleaved attributions), `jmicro2.out` (isolated
  construct), `wide.out` (print_table width), `rg.out`, `dl.py`/`verdict.py` (router shapes), plus
  the harness and driver scripts so every number is reproducible.
- No lane tracked file was modified; scratch `/fast/scratch/hyaku/kama-r92/SC02SuperlinearSweep/`
  removed after copying.

## Recommended next step (not mine to execute)

F2 and F3 are one-construct fixes each: build `json_array` from an array while keeping the
`",\n"` separator byte-for-byte, and drop the per-cell width padding in `print_table`. A
byte-preserving `json_array` and an unpadded `print_table` do not change what the probe prints,
so the frozen `round92-linear-paths.py` counter (D1-D9 byte-equality cells) should still pass.
F6 needs a separate fix: give `router_file_states` a per-candidate budget (or decide each
candidate independently) so one slow file cannot make the remaining candidates "undecidable" and
flip the verdict to `MODEL_OK`. That is the L1's call.

VERDICT: partial — the three round-92 paths are confirmed linear at M2 and quadratic at BASE
(F1), but two super-linear constructs remain outside the frozen predicate — `json_array`'s
O(R²·L) string append and `print_table`'s width padding, both amplified by the listener's answer
length (F2, F3) — and the router model-file check shares one 4 s deadline across all
candidates, so a listener that repeats a slow-to-parse model file flips `MODEL_UNLOADED` to
`MODEL_OK` at a load-dependent threshold (F6: a carried, nondeterministic false green that BASE
reproduces, so it does not falsify C2).
