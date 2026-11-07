# SC02ProbeVerdictSweep — round 93 wave 1

Seat: SC02ProbeVerdictSweep (scout). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Scope: sweep `tools/kama-probe.sh` at **M1 = `fe5f031cb1b9d33e1160360d892149b8ac3c7771`**
(`probe_sha256=159c80688c5d903ea776e3e548a980f64e6ddedf43b8d7a35ab4724acab48dbb`) against
**BASE = `5af794958b0fc08f574aa2e67650282269549b02`**
(`probe_sha256=36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962`) for any
remaining verdict that depends on the number of entries a listener sends, or on host load/time.

Frozen claims read first: `plans/round-93-claims.md` (C1 rule = memo `SEEN` keyed by
`(st_dev, st_ino, st_size, st_mtime_ns)`; C1 disclosed limit = "many **distinct** slow files
still share the one deadline"; "undecidable stays loadable", round-89 rule, unchanged).

Host: 32 CPUs. Load was 30–90 naturally and 100–294 under synthetic load (every number
below carries its `load1`; timing cells are load-sensitive). No tool was installed or
upgraded — nothing to record beyond "no installs".

## Commands and outputs

All stubs are lane-owned children on free loopback ports, killed by the harness.
Scratch: `/fast/scratch/hyaku/kama-r93/SC02ProbeVerdictSweep/` (removed at yield).
Full transcripts: `.ufo/waves/round-93/w1/out/SC02ProbeVerdictSweep/RECEIPTS.md`.

```
# 1. counter at M1, natural load (4 runs, load1 34/46/64/68) -> exit=0 each
$ python3 tools/round93-router-repeat.py --repo . --rev fe5f031... --work <scratch>
ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev ... load1=46.22

# 2. counter at M1, synthetic load 200 burners -> exit=1
$ python3 counter_under_load.py <scratch> fe5f031... 200
ROUTER_REPEAT_CELL R03-slow-x64 ok=0 ... run1=MODEL_OK/router-unloaded-autoload/5.11s
ROUTER_REPEAT_CELL P04-slow-x1-mixed ok=0 ... run1=MODEL_OK/router-unloaded-autoload/5.87s
ROUTER_REPEAT cells=10 mismatches=5 positive_mismatches=1 probe=rev ... load1=256.31
# counter exit=1 wall=129.5s

# 3. counter at BASE, same load -> the BASE loader cannot decide the fixture
$ python3 counter_under_load.py <scratch> 5af794... 200
ROUTER_REPEAT could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'
# counter exit=2

# 4. fixed-load repeated trials (200 burners): the SAME bytes flip at both revs
$ python3 harness12.py <scratch> 200 10
FLIP cell=P04 rev=BASE flips=3/10 want=MODEL_UNLOADED/router-model-missing load1=178.27
FLIP cell=P04 rev=M1  flips=5/10 want=MODEL_UNLOADED/router-model-missing load1=244.18
FLIP cell=R03 rev=BASE flips=10/10 want=MODEL_UNLOADED/router-model-invalid load1=288.12

# 5. memo effect, ONE file named by N candidates (identical bytes both revs)
$ python3 harness11.py <scratch> memo
MEMO n=8    BASE wall=4.04s states={'invalid': 6, '-': 2} | M1 wall=0.66s states={'invalid': 8}
MEMO n=64   BASE wall=4.19s states={'invalid': 7, '-': 57} | M1 wall=0.60s states={'invalid': 64}
MEMO n=1024 BASE wall=6.53s states={'invalid': 7, '-': 1017} | M1 wall=0.71s states={'invalid': 1024}

# 6. DISTINCT slow files, fresh files per rev
$ python3 harness6.py <scratch> distinct
distinct-k4 BASE rc=2 MODEL_UNLOADED/router-model-invalid 2.32s
distinct-k4 M1  rc=2 MODEL_UNLOADED/router-model-invalid 2.39s
distinct-k8 BASE rc=0 MODEL_OK/router-unloaded-autoload    4.32s
distinct-k8 M1  rc=0 MODEL_OK/router-unloaded-autoload    4.35s

# 7. ONE file, ONE entry, cache warm, load varied
$ python3 harness11.py <scratch> onefile 0,64,128
burners=0   BASE rc=2 MODEL_UNLOADED/router-model-invalid 0.77s load1=69.78
burners=0   M1  rc=2 MODEL_UNLOADED/router-model-invalid 0.80s load1=68.51
burners=256 BASE rc=2 MODEL_UNLOADED/router-model-invalid 3.87s load1=105.45
burners=256 M1  rc=0 MODEL_OK/router-unloaded-autoload    5.15s load1=123.11

# 8. /props latency vs the probe's --timeout 5
$ python3 harness4.py <scratch> props-threshold
props-ok-d4.9 BASE rc=0 MODEL_OK/router-unloaded-autoload 5.08s
props-ok-d5.0 BASE rc=2 MODEL_UNLOADED/router-unloaded     5.12s
props-ok-d5.0 M1  rc=2 MODEL_UNLOADED/router-unloaded     5.12s

# 9. timeout-8 kill and stdout buffering
$ python3 timeout_buffer_demo.py
SIGTERM case: rc=-15 lines_seen=5124 bytes=65502
$ python3 timeout_kill_demo.py <scratch>          # a SHORTER timeout, on purpose
TK k=8   timeout=3 rc=124 wall=3.00s lines=6/8   nbad=6   ncand=8   -> MODEL_OK
TK k=256 timeout=8 rc=0   wall=4.54s lines=256/256 states={'-':256} -> MODEL_OK

# 10. MAX_STEPS boundary (host-load independent)
$ python3 steps_boundary.py <scratch>
tensors=600000 wall=2.15s '0\tinvalid' ; tensors=650000 wall=2.29s '0\tinvalid'
tensors=675000 wall=2.31s '0\t-'      ; tensors=700000 wall=2.36s '0\t-'

# 11. argv candidate
$ python3 argv_test.py
getconf ARG_MAX = 2097152 ; n=131072 rc=0 lines=131071
```

## Findings

**F1 — DEFECT (reproduced): the C1 counter's own P-cell flips under host load, so the
frozen predicate is not load-invariant.** At M1 under synthetic load the counter prints
`mismatches=5 positive_mismatches=1` and exits **1** (kill rule K1), where at natural load
it prints `mismatches=0 positive_mismatches=0` and exits 0 (4/4 reproductions). The false
green is `MODEL_OK / router-unloaded-autoload` — the round-92 SC02 F6 signature. The
flipped cells include **P04**, a *P* cell, so `positive_mismatches` becomes 1 (the
counter counts `cid.startswith("P")` as positive). At **fixed** load the flip is
nondeterministic at both revs (`P04 flips=3/10` BASE, `5/10` M1): same bytes, same
listing, same load, two different verdicts — a time-dependent verdict.

**F2 — DEFECT (reproduced, mechanism): the deciding budget is the ROUTER_PY **wall
DEADLINE**, which is per-*call*, not per-file.** `tools/kama-probe.sh` line 563 (identical
at M1 and BASE): `MAX_STEPS, DEADLINE = 4_000_000, time.monotonic() + 4.0` — evaluated
once at **module import**, so an absolute wall-clock budget for the whole
`router_file_states` invocation, shared by every candidate in it. Line 623 checks it only
every 4096 steps. When one parse of the slow file crosses 4 s the state becomes `-`; the
round-89 rule ("undecidable stays loadable") keeps the candidate loadable; `router_refine`
(line 870) computes `nbad < ncand` → `unloaded=1` → `MODEL_OK / router-unloaded-autoload`.
Evidence with **ONE file and ONE entry** (entry count 1, so it cannot be the cause):
`harness11.py onefile` — at `burners=0` both revs say `MODEL_UNLOADED/router-model-invalid`;
at `burners=256` **M1** says `MODEL_OK/router-unloaded-autoload` (5.15 s) while BASE still
says `MODEL_UNLOADED/router-model-invalid` (3.87 s). `steps` is re-initialised per file
(line 596ff) but `DEADLINE` is not, so BASE can decide a *later* candidate after an
*earlier* one burned the shared budget, whereas M1 spends the budget once and every
candidate inherits that one outcome. The memo removes the **count** dependence, not the
**time** dependence.

**F3 — DEFECT (reproduced): the memo fix removes the count dependence, but the verdict is
still not determined by the listing.** `MEMO n=1024`: M1 = 0.71 s, all 1024 states
`invalid`; BASE = 6.53 s, 1017 states `-` — the intended repair, real. But the same
*bytes* still flip under load (F1/F2), so "the verdict does not change when entries
repeat a model file" holds only while one parse finishes inside 4 s.

**F4 — NOTE (bounded, partly disclosed): the DISTINCT-file threshold is ~8 entries and is
itself load-dependent.** `harness6.py distinct`: k=1..6 → `MODEL_UNLOADED/router-model-invalid`
at both revs; **k=8** → `MODEL_OK/router-unloaded-autoload` at both revs (4.32 s / 4.35 s).
An earlier run at load1≈86 flipped already at k=4 while a run at load1≈43 did not — the
threshold is a function of host speed, not a fixed entry count. The round-93 disclosure
("many **distinct** slow files still share the one deadline") names the mechanism but
implies a stable threshold; observed: 8 at load ≈48, 4 at load ≈86. Pre-existing at BASE
too (identical at both revs).

**F5 — NOTE (bounded): the `timeout 8` wrapper does kill the ROUTER_PY child and the kill
does lose stdout lines, but the 4 s inner DEADLINE fires first — the 8 s timeout is a
backstop, not the mechanism.** Line 806: `timeout 8 python3 -c "$ROUTER_PY" "$body" files "$@"`.
Python block-buffers stdout to a pipe, so a SIGTERM drops the unflushed tail
(`timeout_buffer_demo.py`: SIGTERM leaves 5124 of 200000 lines). Forcing a shorter timeout
reproduces the consequence end to end (`timeout_kill_demo.py`): `TK k=8 timeout=3 rc=124
lines=6/8` → `nbad=6 < ncand=8` → `MODEL_OK / router-unloaded-autoload`. With the real
`timeout 8` the child always exits by itself first (every measured run `rc=0`, all lines
present), so F1/F2 is the inner deadline, not the kill.

**F6 — NOTE (bounded): MAX_STEPS (4,000,000) is host-load *independent*; only the wall
DEADLINE is load-dependent.** `steps_boundary.py`: 600000/650000 tensors → `invalid`;
675000+ → `-` (undecided → loadable → `MODEL_OK`). The boundary is a step count and does
not move with load. This pins F2 on the wall clock specifically.

**F7 — NOTE (bounded, not a C1 regression): `/props` latency alone flips the verdict, at
both revs.** `router_autoload` (line 819) fetches `/props` with `--max-time "$TIMEOUT"`
(default 5 s). `harness4.py props-threshold`: `/props` delayed 4.9 s →
`MODEL_OK/router-unloaded-autoload` at both revs; 5.0 s → `MODEL_UNLOADED/router-unloaded`
at both revs (the autoload branch is skipped, so the reason degrades to the generic
`router-unloaded`). Identical at BASE and M1 → round-88 `/props` design, not the round-93
change. Needs a listener whose `/props` takes ≥ the probe timeout.

**F8 — NOTE (bounded): the `router_refine` counter is order-sensitive in the reason, not
in the verdict.** Lines 867-870: `unloadable` is set from the **first** `missing|invalid`
seen; the verdict turns on `nbad < ncand`. `harness2.py order`: `missing-then-invalid` →
`router-model-missing`; `invalid-then-missing` → `router-model-invalid`; both revs
identical, both verdicts `MODEL_UNLOADED`. Only the reason string follows listing order
(consistent with the counter's P04, which lists missing first and expects
`router-model-missing`).

**F9 — NOTE (bounded): the argv candidate is unreachable.** `router_file_states` passes
one index per candidate as an argv word (`"${cand[@]}"`, line 869). `getconf ARG_MAX` is
2097152 and 131072 argv words exec fine; the 4 MiB `MAX_BODY` cap bounds the entry count
far below that (the counter's `router_body` refused a cell ≥ 4 MiB at n=24576).

## Deliverables

- `.ufo/waves/round-93/w1/out/SC02ProbeVerdictSweep/` — the scratch harness (removed at
  yield). Every command quoted above is self-contained; the harness sources are quoted
  in this report's transcript.
- This report: `.ufo/waves/round-93/w1/SC02ProbeVerdictSweep.md`.

## What the L1 should do with this

C1's *rule as written* is implemented and observable: `MEMO n=1024` shows M1 at 0.71 s /
all-`invalid` where BASE is 6.53 s / 1017 undecided — the count dependence the rule
targets is genuinely gone. But the *outcome* it was meant to protect is not
load-invariant: at load1=256 the frozen counter at M1 itself prints
`mismatches=5 positive_mismatches=1` and exits 1 (a *positive* cell, P04, flips to a
false green), and at fixed load the flip is nondeterministic (P04 3/10 at BASE, 5/10 at
M1). The deciding budget is the wall-clock `DEADLINE` at line 563, evaluated once per
process and shared by every candidate, so a single slow parse that overruns 4 s makes
every candidate naming that file undecided, and round-89's "undecidable stays loadable"
turns that into `MODEL_OK / router-unloaded-autoload`.

The minimal change that closes F1/F2 is to make the parse budget **per file** (a fresh
deadline per file, or one proportional to the files a listing names) instead of a single
wall clock for the whole `router_file_states` call; and to stop the false green
altogether, to stop treating an *undecided* (`-`) candidate as "fine" — that second part
changes the round-89 rule and is out of scope for this wave, but it is where the false
green comes from.

VERDICT: partial — the C1 memo repair removes the entry-count dependence for repeats
(M1: 1024 repeats of one file = 0.71 s, all decided), but the verdict is still decided
by a 4 s wall-clock deadline shared across the whole call: under load the frozen counter
at M1 prints `mismatches=5 positive_mismatches=1` and exits 1 (a positive cell flipping
to a false green), and at fixed load the same bytes flip nondeterministically at both
revs (P04 3/10 at BASE, 5/10 at M1).
