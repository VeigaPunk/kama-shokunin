# Round 91 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-06
subject: kama round 91. Lane HEAD `e4747a7add602f34eb25379d38c67faa57b3b926`, base `c06838c5b94576971ea33ac465bf2c935e9037f9`, freeze `9a41912a598cad00f7ff08391586a0ef3732bbed`.
report: `.ufo/reports/round-91/kama.md` (fleet repo, commit `e12ca3b402e0d04ea0198621a2e804ab44723aa5`, author `kama-shokunin`, committed 2026-11-06T21:09:07-03:00)

Verdict: status `ok`, **not admitted** (`rejected-honest-stop`). C1 (operability) verifies and was re-measured
independently by this closure; C2 (depth) is not verified — its frozen kill rule K2 fired, which the lane itself
recorded and this closure confirms against the pinned binary and the pinned upstream sources. No owned axis is harmed;
the admit/reject sample agrees with the lane's gate.

Dispatch digest (`.ufo/watchdog.log`, mutable; copied):
`2026-11-06T18:51:38-03:00 launch kama round=91 pgid=1044374 driver=hyaku-inline attempt=1` /
`2026-11-06T20:22:46-03:00 lane-dead-no-report kama round=91; retry same round (hyaku-inline attempt=1: L1 ended without a landed report: FAIL report_of (missing, unchanged, no SHONEN heading, or < 400B): .ufo/reports/round-91/kama.md)` /
`2026-11-06T20:22:49-03:00 launch kama round=91 pgid=1591224 driver=hyaku-inline attempt=2` /
`2026-11-06T21:09:23-03:00 complete kama round=91; hyaku-inline attempt=2`.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H %ci' -- .ufo/reports/round-91/kama.md` | `kama-shokunin e12ca3b4…` 21:09:07 (before `complete` 21:09:23) | ok |
| prompt committed by lane identity | same for `.ufo/prompts/kama-round-91.md` | `kama-shokunin 99a711e7…` 20:22:47 (attempt-2 launch 20:22:49) | ok |
| report lands after lane tip | `git log -1 --format=%ci e4747a7a` | tip 21:08:06 < report 21:09:07 | ok |
| SHONEN heading, one line per box | report `## SHONEN` | 4 lines, all `[~]` with pointers, no `[x]` | ok |
| cited commits exist and are ancestors of `master` | `git rev-parse --verify <h>^{commit}`; `git merge-base --is-ancestor <h> master` for `c06838c5 9a41912a 3decfa36 3f317ecd 3c4f6a1e ba91b699 d9ce93fc 718018eb 96f645fe 75a875a6 e4747a7a` | all resolve, all ancestors; all round commits authored `kama-shokunin` | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; remote `e4747a7a…` | ok |
| prompt carries contract | every non-placeholder line of `kimi-shokunin/templates/round-prompt.md` (140 lines) searched in the prompt (115026 B) | 0 static lines missing; §1–§5 present, §6 hyaku addendum, §7 scratch | ok |
| round shape | report vs prompt §3 | `w1` 12 seats (`w1-results.json`: 12 named outputs), attack 6/12, 0 dead | ok |
| counters frozen (C1 K3, C2 K1) | `git diff --stat 9a41912a e4747a7a -- tools/round91-answer-time.py tools/round91-threshold-rows.py`; `git log 9a41912a..e4747a7a -- tools/` | empty diff; only `3decfa36` touches `tools/` (`tools/kama-probe.sh` only) | ok |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`; W04 duplicates and the pre-existing W01 on S481 only | ok |
| census before → after | `git show <r>:corpus/SOURCES.md \| grep -cE '^ {0,3}\| S[0-9]{3,}'` | 331 → 335 (S592–S595) | matches report |
| knowledge entries | `git ls-tree c06838c5 corpus/knowledge/ \| wc -l`; `ls corpus/knowledge \| wc -l` | 62 → 63 (`serving-thresholds.md`) | ok |
| pre-report gate (committed evidence) | `.ufo/waves/round-91/measured/gate-final.out` | `# rev=75a875a6…`; `PRE_REPORT round=91 arms=14 failed=1 uncommitted=0`, exit 1; sole red arm `round75-instruments` (`bad_rows=19`) | conformance defect (carried R1), status-neutral |

Conformance defects (status-neutral, named): attempt 1 ended `lane-dead-no-report` (driver retry, same round); the
duplicate wave `w1a2` (12 seats, 5 cancelled) ran beside the canonical `w1` and twin seats shared scratch paths so one
`rm -rf` wiped a twin's files (report lines 41–46) — a scratch-discipline breach (prompt §7); the planner seat was held
by the L1; the terminal pre-report gate is red on the carried `round75-instruments` arm.

## 2. Claims — per-claim re-check

### C1 — operability (`answer-time-bound`): **verified (re-measured independently)**

Evidence verified (lane counter not executed by this closure — it is the lane's frozen instrument):
`controls/c1-base.out` `cells=12 mismatches=5` exit 1 (T1/T2/T4/T5 killed 120 s, T3 75.71 s) at `c06838c5`;
`measured/c1.out` `cells=12 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=0aa43573…` exit 0 at
`3decfa36`; `measured/c1-tip.out` same at `3c4f6a1e`; forgeries F1/F2 exit 1 (F2 `positive_mismatches=1`).
Harm (K2): `controls/harm-base.out` vs `measured/harm-M.out` — every suite exit 0 at both, r89 11/0/0, r90 13/0/0.

Probe bytes: `git show <r>:tools/kama-probe.sh | sha256sum` → `b71c309a…` at `c06838c5`, `0aa43573…` at `3decfa36`
and `e4747a7a` (matches receipts). Diff `c06838c5..3decfa36`: per-id `while read … $(normalize_id)` loop in
`model_matches` and the per-entry `model_matches` call in `router_refine` replaced by one awk pass (`AWK_NORM`,
`ENVIRON["KAMA_EXP"]`), `${C_SERVED%,}` replaced by `paste -sd,`.

Independent re-measurement (this closure; `model_matches` extracted from each revision's committed
`tools/kama-probe.sh`, sourced in bash, fed `org/model-%06d.gguf` ids, expected `good`, wall time by `date +%s%N`):

| revision | input | exit | wall |
|---|---|---|---|
| `c06838c5` (base) | 20 000 ids, absent | 1 | 17 625 ms |
| `c06838c5` (base) | 200 000 ids, absent | 124 (killed by `timeout 120`) | > 120 s |
| `e4747a7a` (tip) | 20 000 ids, absent | 1 | 48 ms |
| `e4747a7a` (tip) | 200 000 ids, absent | 1 | 383 ms |
| `e4747a7a` (tip) | 200 000 ids + `/x/y/good.gguf` last | 0 | 399 ms |

Tip scales ~linearly (10× ids → 8× time); base is super-linear and exceeds the cap. Rule preserved at tip:
`model_matches 'good.gguf.gguf' 'good'` → 1 (one `.gguf` stripped, P3), `model_matches 'a\b' 'a\b'` → 0 (backslash
verbatim through `ENVIRON`, S592). The quadratic router path (T3) and the C_SERVED join are evidence-verified only.

### C2 — depth (serving thresholds): **not verified** (K2 fired; author verdict confirmed)

Counter evidence: `controls/c2-base.out` `rows=0` exit 1; `measured/c2.out` `rows=14 bound=14 unbound=0 duplicates=0
engines=3 fetch_failures=0` exit 0 at `3f317ecd`; tip same (`c2-tip.out`). Forgery battery V1–V4 exit 1.
K2 re-checked by this closure:
- `/home/vgpnk/.local/opt/llama-b12177/llama-server --help` (sha256 `ba272ee3…`, the pinned binary) →
  `-np,   --parallel N   number of server slots (default: -1, -1 = auto)`.
- `curl …/llama.cpp/b12177/common/arg.cpp` line 1373 → `params.n_parallel = -1;     // auto by default` (under
  `LLAMA_EXAMPLE_SERVER`); `…/tools/server/server.cpp` lines 126–129 → `n_parallel = 4` and `kv_unified = true`.
- SKILL row T07 states `1` from `common.h:464` (`int32_t n_parallel = 1;`). The row misstates the server's default →
  K2 fires → C2 not verified. The lane recorded this itself (SKILL §Round 91 correction, knowledge §Round 91 correction,
  lesson M1, KQ146 with failing falsifier `measured/kq146-help-check.out` `disagree=1`, exit 1).
- Row-binding spot re-check: S593 fetched, sha256 `c3010a3c…` equal; line 632 `int32_t port = 9931;`, 634
  `int32_t timeout_read = 3600;`. S594 sha256 `0b0ea669…` equal; lines 23/130 hold `defaultPort := "11434"` /
  `keepAlive = 5 * time.Minute`. S595 sha256 `e963af06…` equal; lines 26/111/809 hold the cited literals.

## 3. Per-axis verdicts

`git diff c06838c5 e4747a7a -- SCORECARD.md`: axis scores unchanged (operability 8, freshness 8, depth 7, coverage 9,
calibration 7, adjacency 7); capability rows 93 → 94, the one addition `answer-time-bound`, none removed.

| axis | verdict | reason |
|---|---|---|
| operability | improved | C1 re-measured: 200k ids >120 s → 0.38 s, rule preserved, harm suites unchanged |
| depth | unchanged | C2 not verified (K2); misstated T07 and six overreach rows carry a dated correction, so not harmed |
| freshness | unchanged | not claimed; no regression seen |
| coverage | unchanged | not claimed; new knowledge entry recorded, no score move |
| calibration | unchanged | not claimed; calibration row names the newest closure (r90) |
| adjacency | unchanged | not claimed; `w1/CN01SiblingOverlap.md` reports no sibling contradiction |

## 4. Discernment spot-check (`corpus/lessons/round-91.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S593 llama.cpp `common/common.h` @ b12177 | admit (limited by KQ146) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — sha256 `c3010a3c…` equal; line 634 `int32_t timeout_read = 3600; // http read timeout in seconds` | agree | quote verbatim at its line (≤25 words); the KQ146 limit is right: line 464 is the shared-struct default the server's parser overrides (arg.cpp 1373) |
| S592 POSIX.1-2024 `awk` | admit | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html — sha256 `6df7d077…` equal; line 107 "shall be interpreted as if they appeared in the awk program preceded and followed by a double-quote" | agree | 17-word quote present at lines 107–108; grounds the `ENVIRON` hand-off, confirmed by the tip's backslash match |
| GNU gawk manual `Assignment-Options.html` | reject (unreachable) | `curl -m 20 https://www.gnu.org/software/gawk/manual/html_node/Assignment-Options.html` → rc=28, http 000, 0 bytes | agree | still unreachable from this host; S592 grounds the same rule, so nothing is lost |
| SGLang v0.5.22 `server_args.py` | reject / not mined | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/server_args.py — sha256 `d1b9ffc7…` equal; line 177 `from sglang.srt.arg_groups.fields.serving import (`; `arg_groups/fields/device.py` 66–69 holds `watchdog_timeout … = 300` across four lines | agree | defaults moved out of the file; the one-line binding rule cannot bind a multi-line default |

New SOURCES rows re-opened: S592, S593, S594, S595 — all four sha256 equal the rows; quotes located at the stated lines.

## 5. Trend verdicts

- **expansion: improved** — 4 mined tier-A rows (S592–S595), knowledge 62 → 63 (`serving-thresholds.md`, new ground
  held under a dated correction), capability `answer-time-bound` re-measured green by this closure.
- **quality: improved** — the r90 R2 verified-at correction landed (`probe-answer-bounds.md` §Round 91 correction);
  the r90 reason-row receipt the C1 change staled was found and re-bound 24/24 (`measured/r90-reason-rows-tip.out`);
  C2's misstatements were marked in SKILL and the knowledge entry before closure. Offset routed as R2 below.
- **discernment: improved** — the frozen K2 fired on a row the counter called bound, the lane recorded the miss
  instead of re-scoring, and KQ146 cites lesson M1 with a falsifier that fails on exactly T07; this spot-check agrees
  on 2 admits and 2 rejects.

## 6. Routed defects (lane fixes next round)

- **R1** `round75-instruments` arm red (`bad_rows=19`, L0 open since r87): carried; keep the disposition in the lesson.
- **R2** Corrections sweep incomplete: `corpus/SOURCES.md` S593 summary still says the server defaults to "one
  parallel sequence"; append a dated correction (§Evidence standard, "Corrections sweep every mention").
- **R3** Scratch discipline: duplicate-wave twin seats shared scratch paths and one `rm -rf` wiped a twin's files;
  wave items must name per-seat scratch roots (prompt §7).
- **R4** C2 is re-claimable only after rows are re-read under KQ146 (the binary's own parser / `--help` default);
  T07 and the six overreach rows (T02, T04, T09, T10, T11, T13) need superseding rows, not prose only.
- **R5** C1 disclosed limits (w1 SC02: three super-linear paths present at base; counter does not own the rule,
  CR01/MT01) remain open.

SHONEN: all four boxes remain `[~]` lane assertions with pointers; the checklist items look checkable by a non-author
from the cited files — promotion stays operator-owned.
