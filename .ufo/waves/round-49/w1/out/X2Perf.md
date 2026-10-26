# X2Perf — cost of the v4 origin pass (round 49, lane kama, build 74558c71)

**Verdict: `origins()` is linear in unique blobs × lines plus a second linear term in distinct line texts (~0.07 µs per scanned line + 0.45–0.67 µs per distinct text); on the real lane the pass costs 0.09 s of a 0.78 s run (+13 %) and +8.4 MiB of 39 MiB peak RSS (+27 %), while on the spec-shaped fixture (1500 commits rewriting a 3000-line exempt head) it costs 3.38 s of a 43 s run (+8 %, +4.1 s CPU) and +1,146 MiB peak RSS (+198 %, ~250 B per distinct text) — memory, not time, is the pass's scaling cost, and the booleans-instead-of-frozensets prototype (out/X2Perf/proposed-origin-flag.diff) removes 992 of those MiB (down to +26 % over v3) with byte-identical output and a 36/36 selftest.**

Scope: this seat measured cost only. The two round-49 counters, the preregistration and the controls were read, not run and not modified; the lane was used read-only through a `--shared` clone. All fixtures live in scratch and are removed.

## Environment

- Python 3.14.8 (GCC 16.2.1), git 2.56.0, Linux 7.2.11-arch1-1, 32 cores, 30 GiB RAM.
- Timings: GNU time 1.9, already present at `/home/vgpnk/.local/bin/time` (`/usr/bin/time` is absent on this host; nothing was installed, nothing pacman).
- Host load 8–18 during the runs (other round-49 seats); every number below is a median of 3–5 runs and CPU time (`user+sys`, which includes git children) is reported beside wall time because wall time carries ~±1 s noise on the 35–45 s runs.
- `--json` output was captured for every run; exit codes are recorded. The synthetic fixtures exit 1 by construction (their 50 dated tail lines are rewritten every commit and never restored: `status=unrestored`), which is fixture behaviour, not a tool fault.

## 1. The lane (real cost)

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1`.

```
/home/vgpnk/.local/bin/time -v -o lane-v4.time python3 tools/append-only-audit.py \
    --repo $S/lane --to 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --json
/home/vgpnk/.local/bin/time -v -o lane-v3.time python3 $S/append-only-audit-v3.py \
    --repo $S/lane --to 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --json      # tool at 438127bc
```

| | v4 (74558c71) | v3 (438127bc tool, same tip) | delta |
|---|---|---|---|
| wall, 5 reps: 0.81/0.82/0.78/0.78/0.78 s vs 0.75/0.69/0.69/0.68/0.69 s | **0.78 s** | 0.69 s | **+0.09 s (+13 %)** |
| max RSS, 5 reps | **39,952 kB** | 31,392 kB | **+8,560 kB (+27 %)** |
| exit | 0 | 0 | — |
| summary (v4 at 319 commits; v3 receipt is its 438127bc-tip run) | files 92, events 5, ungraded_lines 82 | files 92, events 5, ungraded_lines 89 | the 7 lines |

The pass runs for one file only: `SCORECARD.md` (the lane's only `exempt=` row; the `only=` rows produce `titles == ∅` and never call it). In-run instrumentation (`receipts/lane-instr.txt`, instrumented copy in `instrumented-copy.diff`):

```
INSTR origins_s=0.098 calls=2 blobs=96 lines=132573
INSTR origins_s=0.109 calls=2 blobs=96 lines=132573
INSTR origins_s=0.094 calls=2 blobs=96 lines=132573
INSTR origins_s=0.079 calls=2 blobs=96 lines=132573
INSTR origins_s=0.094 calls=2 blobs=96 lines=132573
INSTR_DISTINCT file=SCORECARD.md distinct=2143
```

So: 0.094 s median, two events on the file (`dd9f5dc6`, `0718b6ab`) but one real pass — the per-file cache at `tools/append-only-audit.py:434`/`:448` works (the 1,498 repeat calls are dict hits) — 96 unique blobs, 132,573 lines, 2,143 distinct texts. That is 12 % of the run's wall time and 21 % of its RSS, on a 0.78 s run whose 0.59 s is 467 git subprocesses and the event loop.

## 2. The spec fixture (1500 commits rewriting a 3000-line exempt head)

Builder: `out/X2Perf/build_fixture.py` (plumbing-only commits, fixture-local identity `aoa-x2perf`, `rev-parse --show-toplevel` asserted equal to the fixture dir before the first commit, index file inside the fixture `.git`). Contract row: `score.md  A-corr  NOTES.md:2  exempt=## Axes@NOTES.md:2`; `score.md` = `## Axes` + 3000 head lines + `## Round 1` + 50 dated lines. The first commit adds `score.md` (an add, no deletion); each of the 1,500 later commits rewrites the head with fresh text (and the 50 dated lines), so 1,499 of them are events (`receipts/A-v4.json`: commits 1,501, events 1,499, deleted_total 4,571,950).

| repo | commits | unique blobs U | blob lines L | U·L | distinct texts | v4 wall | v3 wall | ΔCPU (v4−v3) | v4 RSS | v3 RSS | ΔRSS | origins in-run | µs/line |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lane | 319 | 96 | 1,380 | 132,573 | 2,143 | 0.78 | 0.69 | — | 39 MiB | 31 MiB | +8 MiB | 0.094 | 0.71 |
| A (spec) | 1,501 | 1,500 | 3,053 | 4,579,500 | 4,575,003 | **43.43** | 42.02 | **+4.14** | **1,725 MiB** | 579 MiB | **+1,146 MiB** | **3.381** | 0.74 |
| B (L/2.9) | 1,501 | 1,500 | 1,053 | 1,579,500 | 1,575,003 | 32.53 | 31.81 | — | 608 MiB | 187 MiB | +421 MiB | 0.823 | 0.52 |
| C (U/3) | 501 | 500 | 3,053 | 1,526,500 | 1,525,003 | 7.51 | 6.54 | +1.08 | 614 MiB | 207 MiB | +407 MiB | 0.984 | 0.64 |
| D (blob/8) | 1,501 | 187 | 3,053 | 570,911 | 570,353 | 5.61 | 5.22 | — | 233 MiB | 91 MiB | +142 MiB | 0.314 | 0.55 |
| G (repetitive) | 1,501 | 1,500 | 3,053 | 4,579,500 | 3,050 | 33.82 | 33.81 | −0.25 | 591 MiB | 578 MiB | +12 MiB | 0.312 | 0.07 |

Commands (each run: `/home/vgpnk/.local/bin/time -v -o <receipt> python3 <tool> --repo $S/fix-<X> --to HEAD --json`), 3–5 reps per cell, `receipts/*-v[34].time` and `*.json`.

Comparability: v4 and v3 produce **identical** `ungraded_lines` and event lists on every fixture (e.g. A: 4,497,000 ungraded lines both, 1499 events both, `deleted_total` 4,571,950 both), so the wall/CPU delta is the pass and nothing else — the only audit-path difference between the two tools is `origins()` plus the `binds()` rewrite, and `binds()` runs on declarations only (`receipts/A-v4.json` vs `receipts/A-v3.json`).

## 3. Is `origins()` linear in unique blobs × lines? — Yes, as a sum of two linear terms

The pass (`tools/append-only-audit.py:431-449`) is one `cat-file --batch-check` over all commits (`:436`), then per **unique** blob (`:439` skips a blob id already seen, so 1,501 commits with 187 distinct blobs cost 187 — fixture D) one `sections(body)` pass plus one dict lookup per line (`:442-446`), and one insert per text not yet in `orig` (`:446-447`). No nested loop, no rescan; work is Θ(commits + Σ_b L_b + distinct).

Two clean experiments separate the terms:

- **Same product, different factors** — A is 1,500 × 3,053 (4.580 M lines), E is 3,051 × 1,553 (4.738 M lines), both fully churned: 2.792 s vs 3.167 s (micro-warm, `receipts/micro-origins-warm.txt`, `micro-origins-EF.txt`). U doubled and L halved and the time moved 13 % — the product, not either factor, drives it.
- **Same U·L, 1,500× fewer distinct texts** — G has A's exact shape (1,500 blobs × 3,053 lines) but a frozen head: only the 50 dated lines are fresh per commit, so 3,050 distinct texts instead of 4,575,003. Cost 0.312 s vs 3.381 s. Same scan, 11× cheaper ⇒ the scan term is small and the distinct-text insert term is the large one.
- **Doubling the product** — F (3,000 × 3,053 = 9.159 M lines) 6.276 s = 2.25× A.

Fit over A–F (G pins the scan term, since its distinct count barely registers): `t ≈ 0.068 µs × (U·L) + b × distinct`, with b = 0.45 µs (B) / 0.48 (D) / 0.58 (C) / 0.60 (E) / 0.62 (F) / 0.67 (A) — i.e. b rises with the size of the map because the inserts become memory-bound (`orig` is resident). Worst case, when every line of every blob is new text, distinct = U·L and the two terms collapse into **0.6–0.74 µs per line**, which is exactly the µs/line column for A/B/C/D. So: linear in unique blobs × lines, with a per-line constant that is not constant across scales (0.34 µs at 0.57 M lines → 0.69 µs at 9.2 M lines) — mildly superlinear wall clock through allocator/cache pressure, but no algorithmic extra pass.

## 4. Memory is the pass's real cost

ΔRSS per distinct text, from the paired runs: A 1,146 MiB / 4.575 M = **250 B**; B 268 B; C 267 B; D 249 B. That is one `str` key reference (the strings are shared with `Repo._raw`), one dict slot (~30 B) and a **1-element `frozenset` (~216 B)** created at `:446` (`fresh = collections.defaultdict(set)` at `:443`). The map is Θ(distinct texts over the file's whole history) and is never released for the run (`:448`).

On the lane the decomposition is different: the map is tiny (2,143 texts ≈ 0.5 MiB) and the whole +8.4 MiB is the **blob body cache** — `origins()` reads the file's blob at *every* commit (`:436-442`, into `Repo._raw` at `:358-364`), while v3 read only blobs from the first event's window onward. Evidence: `v4 − v3 = 8,560 kB` but `v4 − prototype = 0.2 MiB` (below RSS noise) while the prototype keeps the blob cache and only drops the frozensets.

## 5. Findings and proposed fixes (not applied to the lane)

**F1 — `origins()` keeps a frozenset per distinct text: ~250 B/text, Θ(history text diversity), +1,146 MiB on the spec fixture.**
`tools/append-only-audit.py:443-447`. Only one question is ever asked of the map — `org.get(text, frozenset()) & titles` at `:483` — so the set-valued value is unnecessary. Proposed text: `out/X2Perf/proposed-origin-flag.diff` (45-line unified diff; `origins(f, titles)` stores `True` when the text's first appearance lies under one of *this file's* exempt titles, `fresh.get(ln, False) or (t in titles)`), applied to a copy only. Measured (`receipts/proto.txt`, `proto-cpu.txt`):
- `--selftest`: `AOA_SELFTEST pass=36 fail=0`.
- Output byte-identical: `lane-proto.json == lane-v4.json` and `A-proto.json == A-v4.json` (`json equal: True`).
- A: RSS 750,016 / 751,012 kB vs v4 1,766,296 kB (−58 %); Δ vs v3 = +153 MiB, i.e. only the dict (v4's +1,146 MiB falls to +153 MiB).
- Time unchanged within noise: A CPU 44.94 s vs v4 43.06 s (±2 s noise floor) — the frozenset is a *memory* cost, not the time term.

**F2 — the pass runs even when no deleted line needs it: any event on an exempt-covered file triggers a full-history pass.**
`tools/append-only-audit.py:477` (`org = origins(f) if titles else {}`) is evaluated before the loop at `:479-484` decides whether a deleted line's parent section is even eligible. Fixture G demonstrates it: 1,499 events, every deleted line in the dated `## Round 1` section, zero eligible deletions, and the pass still costs 0.312 s and +12 MiB (`receipts/G-times.txt`, `G-instr.err`); on an A-shaped churned history with tail-only events the same shape pays 3.4 s. Proposed fix (needs a design decision, so text only): first build `need = {text for pos, text in dl if psec[pos - 1] in eligible}`; if empty, skip `origins()` entirely; otherwise resolve only `need` and merge across events with a retained per-file scan cursor (the blob walk stays Θ(U·L) in total, the map becomes Θ(|needed texts|)).

**F3 — the pass extends the blob cache backwards past the first event (the lane's entire +8.4 MiB).**
`tools/append-only-audit.py:436-442`: `r.list_lines(b)` caches every historical blob body in `Repo._raw` for the rest of the run, and v3 never read the pre-event commits. Cost is bounded by the file's own history (132,573 lines on the lane ≈ 8 MiB at ~63 B/line), so it is small here; on a long-lived exempt file it duplicates the file's whole text history in memory. Proposed fix: consume blobs through one `git cat-file --batch` stream and drop the line list after the blob's origin contributions are recorded (only the distinct-text answers need to survive).

**F4 — informational, no defect:** the frozen preregistration's `limits` (`.ufo/waves/round-49/preregistration.json`) say nothing about the tool's runtime or peak memory, so the v4 pass is unbounded by the contract. The lane's own numbers (0.09 s, +8.4 MiB) are negligible; the spec-shaped ceiling measured here is what an unbounded contract permits (~3.4 s, +1.1 GiB per churned exempt file).

No correctness divergence was observed anywhere: on all four churned fixtures v3 and v4 agree line for line, and the lane shows exactly the 7-line delta the build claims.

## 6. Risks and limits of this measurement

- Wall time is noisy under host load 8–18 (A v4 range 40.76–52.47 s, v3 36.28–44.76 s): the paired CPU deltas (A +4.14 s, C +1.08 s, G −0.25 s) and the in-run instrumentation (3.38 / 0.98 / 0.31 s) are the trustworthy attributions; G's negative CPU delta marks the ±0.4 s noise floor below which the pass is invisible there.
- The fixtures use uniform 17-byte lines with no renames and the file present in every commit; the lane's prose lines are longer, so absolute µs/line is a model, not a prediction. The *shape* (two linear terms, ~250 B/text) is what transfers.
- The micro harness (`out/X2Perf/micro_origins.py`) warms the blob cache before timing, so it measures the pass without the `cat-file` calls; the in-run numbers include them (on the lane the first event's window has already cached all 96 blobs, so the two agree closely).
- One Python build and one host; no claim about other interpreters.

## 7. Non-interference

- Lane: read-only. `git clone --shared` into `$S/lane`; no index/jj mutation, no write to the lane's sources, counters, contracts or registry. The lane's HEAD moved while this seat ran (`122c4ee9` → `24e906f0` → `7fab24e7`, the L1's integration commits) — none of that is mine; all measurements use the frozen build tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, which still resolves. `git diff 74558c71 -- tools/append-only-audit.py` shows the integration touched only `binds()`/`NEG_WINDOW`/selftest (107+/7−, seat K2Negation F1); **`origins()` is unchanged**, so the measured pass is the pass at HEAD as well (verified: `git diff 74558c71 -- tools/append-only-audit.py | grep -E 'origins|origin_cache|fresh|org\.get'` is empty).
- My own out dir: the L1's snapshot commit `24e906f0` already tracks `out/X2Perf/build_fixture.py`, `micro_origins.py` and `instrumented-copy.diff`; the working tree carries my later fixes to `build_fixture.py` (8 insertions / 7 deletions: the fixture `registry/` dir, the `stride` and `mode` arguments, and removal of an unused helper) — the version that built A–G. Everything else under `out/X2Perf/` is new and untracked. Nothing outside `out/X2Perf/` was written.
- Fixtures: `git init` inside `$S/fix-*` with fixture-local identity and `rev-parse --show-toplevel` asserted before the first commit; nothing committed outside `$S`.
- No llama-server was started (`llama-b11909` untouched); no service started or stopped; no pacman; no tool installed or upgraded (GNU time 1.9 already present in `~/.local/bin`).
- Scratch `/fast/scratch/hyaku/kama-r49/X2Perf` removed after the receipts were copied; `/tmp` was not used.

## Deliverables

- `receipts/` (44 files) — every timing receipt (`lane-v4.time`, `lane-v3.time`, `lane-reps.txt`, `reps.txt`, `A|B|C|D|G-v[34].time|json`, `cputime.txt`, `instr-*.err`, `instr-times.txt`, `lane-instr.txt`, `lane-instr-distinct.err`, `micro-origins*.txt`, `micro-rss.txt`, `proto.txt`, `proto-cpu.txt`, `G-times.txt`, `G-instr.err|json`, `lane-proto.json`, `A-proto.json`, `env.txt`).
- `measurements.tsv` — the table in machine-readable form.
- `build_fixture.py` — the fixture builder (commits/head lines/tail lines/stride/mode).
- `micro_origins.py` — the isolated origins pass harness.
- `instrumented-copy.diff` — the measurement-only instrumentation of the v4 tool.
- `proposed-origin-flag.diff` — F1 as a full unified diff (measured, not applied).

---

Wrote:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/measurements.tsv
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/build_fixture.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/micro_origins.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/instrumented-copy.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/proposed-origin-flag.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Perf/receipts/ (44 files)
