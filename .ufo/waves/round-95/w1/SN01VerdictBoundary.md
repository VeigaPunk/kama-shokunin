# SN01VerdictBoundary — round-95 C1 boundary audit (operability)

Seat SN01VerdictBoundary, lane `kama-shokunin`. Scope: the C1 change to `tools/kama-probe.sh`'s router file-state
decision and its derived pass limit — the verdict-vs-bytes boundary, the `-` (undecidable) branch, and the derived
wrapper against the work it must allow.

**Revisions measured.** The lane changed under me mid-session: `f6325660` (the C1 commit named in
`plans/round-95-claims.md`) was falsified by wave-1 RV01 and repaired in `c810f51e` ("M1b"), filed by
`plans/round-95-amendment-3.md`, then narrowed by `plans/round-95-amendment-4.md`. `git log --oneline -3` at filing:
`2afb280a`, `a9b5014c`, `5fcca5b4`; `git diff c810f51e HEAD -- tools/kama-probe.sh` is empty ⇒ `c810f51e` is the
filed probe, and the verdicts below are for it.

## Scope

Measured: per-file state / wall time / steps / stopping bound for eight hostile inputs; the `/props`-latency arm
(round-94 SC02 F4); whether the derived allowance can be smaller than the work the pass must do. Not measured (not my
item): the counter's 10 cells, C2's setter rows, C3's freeze audit, the harm suites. No counter, harm suite or lane
test was run. Exit codes below are the probe's.

## Commands and outputs (exit codes)

Per-file: `python3 measure_files.py <parser> fixtures receipts/<f>.json` — instrumented copy of the probe's embedded
`ROUTER_PY`; `steps` = the probe's own counter, `stop` = source line that raised. End-to-end: `python3 run_probe.py
<label> <probe.sh> <body.json> <props_delay> <expect>` — lane-owned stub router on an ephemeral 127.0.0.1 port; probe
run `check --json --port N --expect X --timeout 2 --connect-timeout 1`; stub killed in a `finally`. Receipts:
`receipts/probe_runs.jsonl` (41 runs) + three `*_states*.json` files.

### (b) The `-` branch — state / wall s / steps / stopping bound

`f6325660` (M1) vs `c810f51e` (M1b, filed):

| case | M1 state / wall s / steps | M1b state / wall s / steps | stopped by |
|---|---|---|---|
| 1M-tensor header | `-` / 8.57 / 4 000 001 | `-` / 8.58 / 4 000 001 | `MAX_STEPS` (Unknown) |
| KV array 49M strings | **`ok` / 27.43 / 766 008** | `-` / 0.99 / 4 000 001 | M1: **nothing — walked to the end**; M1b: `MAX_STEPS` |
| KV array 50M strings | `ok` / 34.95 / 781 641 | `-` / 0.92 / 4 000 001 | M1: nothing (≤ `MAX_ARR`); M1b: `MAX_STEPS` |
| 200 MB tensor infos | `-` / 4.96 / 4 000 001 | `-` / 2.47 / 4 000 001 | `MAX_STEPS` |
| FIFO | `invalid` / 0.000 / 0 | `invalid` / 0.000 / 0 | `S_ISREG` check before open |
| directory | `invalid` / 0.001 / 0 | `invalid` / 0.001 / 0 | `S_ISREG` check before open |
| permission-denied | `-` / 0.000 / 0 | `-` / 0.000 / 0 | `os.open` `OSError` → `-` |
| `/proc/self/mem` | `invalid` / 0.000 / 0 | `invalid` / 0.000 / 0 | `NO_OPEN` realpath prefix |
| sparse 200 MB, 0 tensors | `ok` / 0.003 / 4 | `ok` / 0.000 / 4 | header only |

M1b's per-element step charge (`c810f51e` `tools/kama-probe.sh` `skip_strings`: `steps[0] += 1` inside the element
loop) turns the 27–35 s array walk into a bounded `-`. At M1b **no** hostile file keeps the pass busy: per-file wall
time is bounded by `MAX_STEPS` (4 000 001 steps ⇒ ≤ ~9 s here); `MAX_STEPS` alone stops the two array and the two
large-tensor cases — neither the derived wrapper nor `NO_OPEN` was needed.

### (c) Does the derived wrapper ever get smaller than the work it must allow?

`ncand` counts candidate **entries**; the memo `SEEN` (`tools/kama-probe.sh:605`) dedupes by **inode**. Two
under-pricings, both measured. **One entry, several distinct paths.** `file_state` parses *every* `-m`/`--model`/`-mm`/`--mmproj`/`-md` occurrence
in `status.args`, but M1's `ncand` counts the entry once. One unloaded entry naming four distinct 400 MB slow files
⇒ `ncand=1` ⇒ allowance `20 + 15*1 = 35 s`, work ≈ 4×13 s. M1: **`MODEL_OK` / `router-unloaded-autoload`, wall
35.72 s** — killed at 35 s, the state line never arrived, `nbad(0) < ncand(1)` ⇒ `unloaded=1`
(`tools/kama-probe.sh:928`). Same bytes, allowance raised (`probe_limit_raised.sh`, `20 + 600*ncand`):
**`MODEL_UNLOADED` / `router-model-invalid`, wall 39.46 s** — the verdict follows the wrapper, not the bytes. Two
and four entries behave the same (M1 `MODEL_OK` at 50.65 / 80.82 s; raised allowance `MODEL_UNLOADED` every time);
base probe `a27656a4` (constant `timeout 60`) gives `MODEL_OK` at 60.68 / 60.50 s.

**Repaired at M1b.** `c810f51e` adds a `count` verb to `ROUTER_PY` counting *path occurrences* (`path_count`)
and prices the allowance `20 + 25 * npaths` (`tools/kama-probe.sh:862`), falling back to `ncand` only if the count
is non-numeric or `< 1`. My three multi-path listings at M1b: `MODEL_OK / router-unloaded-autoload` at 13.48 / 6.40 /
13.82 s — but there the *files* are `-` (the 49M-element array now exceeds `MAX_STEPS`), so `MODEL_OK` is the
round-89 "undecided ⇒ loadable" rule, not a truncation artifact. With files that *decide* `invalid` slowly
(700k-tensor headers, four distinct inodes), M1b gives **`MODEL_UNLOADED` / `router-model-invalid`** for the
one-entry/four-path listing (8.42 s) and the four-entry listing (11.92 s), matching M1 (8.31 / 8.57 s): no truncation
and no wrapper-dependent verdict.

### (a) Round-94 SC02 F4: slow `/props` on a healthy (valid-file) listing

Stub router; four unloaded entries whose `-m` path is a **valid** GGUF; `/props` delayed; `--timeout 2`;
`router_autoload` uses `curl --max-time "$TIMEOUT"` (`tools/kama-probe.sh:874`). M1 and M1b agree exactly: delay 0 ⇒
`MODEL_OK` / `router-unloaded-autoload`, exit 0; delay 3 and 6 ⇒ `MODEL_UNLOADED` / `router-unloaded`, exit 2
(`receipts/probe_runs.jsonl` lines 1–3 M1, 36–38 M1b). The timeout makes `router_autoload` return 1 ⇒ `autoload=0` ⇒
the file-state block is skipped (`tools/kama-probe.sh:919`) ⇒ the verdict falls through to `down` ⇒ `MODEL_UNLOADED` /
`router-unloaded` for a **healthy** router. Unchanged by the repair. **C1's disclosure covers this** (frozen plan C1
disclosed-limit item (c); amendment 4): it claims only that the bytes determine the *per-file* decision, and this is
not a false green — a healthy router is graded drifted, not healthy.

## Findings

| # | label | finding | evidence |
|---|---|---|---|
| 1 | NOTE | The `/props` latency arm (round-94 SC02 F4) reproduces identically at both revisions: a healthy router grades `MODEL_UNLOADED / router-unloaded` when `/props` exceeds `--timeout`. Covered by C1's own disclosure, which claims only that the bytes determine the *per-file* decision — and it is not a false green (a healthy router is graded drifted, not healthy). Routed to round 96. | `receipts/probe_runs.jsonl` lines 1–3 (M1), 36–38 (M1b); `tools/kama-probe.sh:874` (`--max-time "$TIMEOUT"`), `:919` (`ncand > 0 && router_autoload` gate); frozen plan C1 disclosed-limit item (c); amendment 4 routed list |
| 2 | NOTE | The `ncand`-vs-paths under-count of M1 `f6325660` reproduces and is repaired at M1b `c810f51e`. RV01's DEFECT-3 / BLOCKER-1 territory, independently reproduced (identical bytes, two allowances, two verdicts) and independently confirmed repaired. | `receipts/probe_runs.jsonl` lines 8–13 (M1 `MODEL_OK` at 35.72/50.65/80.82 s vs raised-allowance `MODEL_UNLOADED` at 39.46/37.04/67.71 s) and 27–28 (base probe `MODEL_OK` at 60.68/60.50 s); `c810f51e` `tools/kama-probe.sh` `path_count` + `:862` |
| 3 | NOTE | At M1b the derived allowance cannot be smaller than the work it must allow: `npaths` (path occurrences) ≥ distinct parses, and the inode memo only ever *reduces* the work, so hard links over-provision. | `receipts/probe_runs.jsonl` lines 34–35, 39–41; `tools/kama-probe.sh:605` |
| 4 | NOTE | The M1b per-path allowance unit is a host-speed assumption, not a byte-derived bound: the wrapper is still a wall clock (`timeout`), and its 25 s per-path unit is compared against a per-file work bound (`MAX_STEPS`) — two different units. | the `loadburn.py` runs (2.53 s at load1 95 → 8.11 s under 96 burners); amendment 4's "the wrapper is still a wall clock". My burners were always killed in a `finally`; `pgrep` reported `burner_survivors: []` on every run |
| 5 | NOTE | A hostile file can still be slow-and-*decided* at M1b (`invalid`, 5.95 s, 3 500 004 steps) — inside the 25 s per-path allowance; it decides, not defers. | `receipts/m1b_per_file_states.json` case `F1b` |

**No BLOCKER and no DEFECT found against the filed revision `c810f51e` on the C1 boundary.** The two conditions that
would contradict C1's sentence — a verdict depending on the wrapper rather than the bytes, and an unbounded pass —
were both reproduced against `f6325660` and are absent at `c810f51e`. The one limit that remains open is open by the
lane's own disclosure (the `/props` wall clock, routed to round 96).

## Deliverables

- `.ufo/waves/round-95/w1/out/SN01VerdictBoundary/probe_runs.jsonl` — 41 end-to-end probe runs (M1 / M1b / base /
  raised-allowance / F4 delays / multi-path listings): verdict, reason, exit code, wall seconds.
- `.ufo/waves/round-95/w1/out/SN01VerdictBoundary/{per_file_states,m1b_per_file_states,per_file_states_2}.json` —
  per-file state/wall/steps/stop at M1, at M1b (filed), and a second M1 array batch.
- This report: `.ufo/waves/round-95/w1/SN01VerdictBoundary.md`.

Scratch `/fast/scratch/hyaku/kama-r95/SN01VerdictBoundary/` removed after copying receipts. No tracked lane file
edited; no mutating git ran in the lane; no burner of mine leaked; no request sent to 127.0.0.1:1234; no tool installed.

VERDICT: holds — the two wrapper-dependent verdicts I reproduced against f6325660 (ncand under-counting paths, and
the uncounted 49M-string-array walk) are absent at the filed c810f51e, whose per-file decision is a pure function
of the bytes; the slow-/props arm (round-94 SC02 F4) reproduces identically at both revisions and is covered by
C1's own disclosed limit, routed to round 96.
