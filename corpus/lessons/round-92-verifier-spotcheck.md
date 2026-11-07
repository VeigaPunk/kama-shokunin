# Round 92 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-06
subject: kama round 92. Lane HEAD `378220d3777b62de849847585bf0da7200b3b1c7`, base `ed018ca0fa956c5052b3dc6b714a2cb72973da21`, freeze `309eadafd4d0557a056c1bf61455c59778cf5e1d`.
report: `.ufo/reports/round-92/kama.md` (fleet repo, commit `c5f4676301ed2e63f79b7845d834ad80602268e9`, author `kama-shokunin`, author date 2026-11-06T23:05:08-03:00, committer date 23:07:12-03:00)

Verdict: status `ok`, **not admitted** (`rejected-honest-stop`). C2 (operability, capability `linear-probe-paths`)
verifies and was re-measured by this closure at base, M2 and tip. C1 (depth) is not verified: its frozen K2 ("a
non-author read finds a misstating row") fired on R01 and R08 through wave-1 SC01; the lane recorded this itself and
this closure confirms it against the pinned upstream bytes. No owned axis is harmed; the admit/reject sample agrees
with the lane's gate.

Dispatch digest (`.ufo/watchdog.log`, mutable; copied):
`2026-11-06T21:16:12-03:00 launch kama round=92 pgid=3971739 driver=hyaku-inline attempt=1` /
`2026-11-06T23:07:44-03:00 complete kama round=92; hyaku-inline attempt=1`.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H %ad' -- .ufo/reports/round-92/kama.md` | `kama-shokunin c5f46763…`; committer 23:07:12 (before `complete` 23:07:44) | ok |
| prompt committed by lane identity | same for `.ufo/prompts/kama-round-92.md` | `kama-shokunin eda9d8c1…` | ok |
| report lands after lane tip | `git log -1 --format='%ad / %cd' 378220d3` vs report commit | tip 23:06:51/23:06:52; report committer 23:07:12, but report **author** date 23:05:08 precedes the tip it cites | ok (note: author-date anomaly, see defects) |
| SHONEN heading, one line per box | report `## SHONEN`; `SHONEN.md` has 4 boxes | 4 lines, all `[~]` with pointers, no `[x]` | ok |
| cited commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` for all 13 report hashes + base | 14/14 ok | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; remote `378220d3…` | ok |
| prompt carries contract | every static (non-placeholder) line of `kimi-shokunin/templates/round-prompt.md` (140 lines) `grep -F` in the prompt (115902 B) | `static=105 missing=0`; §6 hyaku addendum present | ok |
| round shape | report vs `.ufo/waves/round-92/w1/` | one wave `w1`, 12 seat reports (CN01, CR01, CR02, EX01, EX02, MT01, MT02, RV01, RV02, SB01, SC01, SC02), attack 6/12 | ok |
| counters frozen (K1/K3) | `git diff --stat 309eadaf 378220d3 -- tools/round92-server-defaults.py tools/round92-linear-paths.py plans/round-92-claims.md` | empty | ok |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`; W04 duplicates and pre-existing W01 (S481) only | ok |
| census before → after | `git show <r>:corpus/SOURCES.md \| grep -cE '^ {0,3}\| S[0-9]{3,}'` | 335 → 339 (S596–S599) | matches report |
| knowledge entries | `git ls-tree <r> corpus/knowledge/ \| wc -l` | 63 → 63 (`serving-thresholds.md` modified: §Round 92 revision) | ok |
| append-only files | `git diff ed018ca0 378220d3 -- LOG.md corpus/SOURCES.md \| grep -c '^-[^-]'` | 0 deleted lines in each | ok |
| pre-report gate (committed evidence) | `.ufo/waves/round-92/measured/gate-final.out` | `PRE_REPORT round=92 arms=14 failed=1 uncommitted=0`, exit 1; sole red arm `round75-instruments` | conformance defect (carried) |

Conformance defects (status-neutral, named): (a) the terminal pre-report gate is red on the carried
`round75-instruments` arm, and its `APPEND_DEBT` population keeps growing — r90 `events=94 unaccepted=15`, r91
`events=95 unaccepted=16`, r92 `events=97 unaccepted=18` (`bad_rows=19` constant; grep `APPEND_DEBT` in the three
`gate-final.out`); (b) the fleet report commit's author date (23:05:08) precedes the lane tip it cites (23:06:51); the
committer date (23:07:12) is after it, so the landed bytes post-date the tip, but the commit was evidently amended or
re-created after authoring; (c) the planner seat was held by the L1 (validator rejects `planner`), disclosed.

## 2. Claims (step 2) — re-measured vs evidence-verified

### C1 — depth: serving defaults R01–R15 under KQ146 (sourced S596, S597)

Re-measured (counter frozen since `309eadaf`; it reads committed bytes via `git show`, fetches pinned upstream files
and runs the pinned binary's `--help` only):

```
python3 tools/round92-server-defaults.py --repo . --rev ed018ca0 --binary /home/vgpnk/.local/opt/llama-b12177/llama-server
→ SERVER_DEFAULTS rows=0 bound=0 … supersedes=0 binary_sha256=ba272ee3…; exit 1
… --rev 18153ebb5f9e2ae83f53e7fef57ee579bc409331
→ SERVER_DEFAULTS rows=15 bound=15 unbound=0 duplicates=0 engines=3 fetch_failures=0 help_checked=7 help_disagree=0 supersedes=14; exit 0
… --rev 378220d3777b62de849847585bf0da7200b3b1c7
→ identical to M1; exit 0
```

Plain re-derivations: `grep -cE '^\| R(0[1-9]|1[0-5]) '` over `git show 378220d3:SKILL.md` → 15 (base: 0).
`llama-server --help` at the pin prints `--port … (default: 9931)`, `--timeout … (default: 3600)`,
`--sse-ping-interval … default: 30`, `--cache-ram … (default: 8192, 0 for decision …` — equal to R01–R04.

K2 (non-author read) — **fired; confirmed by this closure.** Re-opened at `b12177` (all sha256 equal to the rows):
- `common/arg.cpp` (`c69c0e07…`): lines 4608–4616, the `--embd-gemma-default` preset sets `params.port = 8011;` and
  `params.n_parallel = 32;` — R01 ("started without `--port` … listens on 9931") and R08 ("started without `-np` runs
  4 slots") are false for that start.
- `tools/server/server-http.cpp` (`aad15b75…`): line 93 `enabled = getenv("AIP_MODE", "") == "PREDICTION";`, line 96
  `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));`, line 125 `port = gcp.port;` — the parsed port is replaced.
- `tools/server/server-models.cpp` (`cab14969…`): line 1218 `inst.meta.port        = common_http_get_free_port();`.
- `tools/server/server.cpp` (`d4d343db…`): lines 116/126–130 confirm R08's value 4 is the role-conditional auto
  resolution.

The values in R01–R15 are the parser/entry-point defaults and bind; the R01/R08 decision cells overstate. The lane's
dated `SKILL.md` §Round 92 correction, KQ149 and lesson M4 state exactly this. **C1: not verified** (agrees with
author). Axis grade **depth: unchanged** — score stays 7, no measured move admitted; not harmed, because the
overstatement is marked in the same round (a correction note, rows byte-identical) and the table supersedes the
round-91 T07 misstatement with a help-checked row.

### C2 — operability: three probe paths linear (capability `linear-probe-paths`)

Re-measured (counter frozen; scratch under `/tmp/k92/c2`, nothing written in the lane):

```
python3 tools/round92-linear-paths.py --repo . --rev ed018ca0… --work /tmp/k92/c2
→ LINEAR_PATHS cells=15 mismatches=6 positive_mismatches=0 probe=rev probe_sha256=0aa43573…; exit 1
  (L1–L3 killed at 120.10 s; L4 73.74 s, L5 67.93 s, L6 25.88 s — this host's load; the committed control shows L4/L5 killed, L6 54 s)
… --rev fa8aedb73d18448383c7a4d75405aba448fe8e38
→ LINEAR_PATHS cells=15 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=36631d49…; exit 0
… --rev 378220d3777b62de849847585bf0da7200b3b1c7
→ identical; exit 0; D1–D9 equal_to_base=1; slowest large cell L1 2.58 s
```

Evidence-verified (committed receipts, not re-executed — lane-owned suites/gates): harm at M2
(`measured/harm-M.out`) equals `controls/harm-base.out` line-for-line after stripping revision digests and timings
(`diff` empty): check.py, test-snapshot, r89, r90, r91 suites, router 1234 `MODEL_OK router-unloaded-autoload`. The
probe change staled the r90 reason receipt (`measured/r90-reason-rows-stale.out`: bound=0, exit 1) and the lane
re-captured it (`measured/r90-reason-rows-tip.out`: `bound=24 unbound=0`, exit 0, `receipt=current`) — repaired in
round, not a residual harm. Doubling receipt `measured/c2-doubling.out`: 0.31/0.37/0.59 s and 0.49/0.83/1.64 s per
doubling (≈linear). **C2: verified. operability: improved.**

### Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C2 re-measured base 6 mismatches exit 1 → M2/tip 0/0 exit 0 |
| depth | unchanged | C1 not verified (K2 fired on R01/R08); score 7 unchanged; not harmed (marked correction) |
| freshness | unchanged | SCORECARD row unchanged (`git diff ed018ca0 378220d3 -- SCORECARD.md`) |
| coverage | unchanged | row text extended (round-92 sources) but score 9 unchanged; no new surface claimed |
| calibration | unchanged | score 7 unchanged; the honest C1 not-verified call is credited under discernment, not as a claim |
| adjacency | unchanged | row untouched; CN01 found no sibling contradiction |

## 3. Discernment spot-check (LEARNING.md) — `corpus/lessons/round-92.md` `## Gate`

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S597 `tools/server/server.cpp` @ b12177 | admit (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server.cpp, sha256 `d4d343db…` equal | agree | line 127 is verbatim the quote (`n_parallel is set to auto, using n_parallel = 4 and kv_unified = true`, inside `SRV_TRC`), guarded by line 116 `role_type != SERVER_ROLE_ROUTER`; primary source for the scope |
| S598 `tools/server/server-http.cpp` @ b12177 | admit (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.cpp, sha256 `aad15b75…` equal | agree | line 96 quote verbatim, line 93 AIP_MODE guard, line 125 `port = gcp.port;` makes the override effective; grounds the R01 correction |
| S595 `vllm/envs.py` lines 26/111 as the default's anchor | reject (declaration, not the reader) | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py, sha256 `e963af06…` equal | agree | line 14 `if TYPE_CHECKING:` encloses line 26 `VLLM_ENGINE_READY_TIMEOUT_S: int = 600`; the run-time reader is the lambda at 811–813 served by `__getattr__` (line 2291) — a type declaration is not the default the process reads |
| S593 `common/common.h:464` as llama-server slot-count anchor | reject (shared struct overridden) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h, sha256 `c3010a3c…` equal; `common/arg.cpp:1372–1373` | agree | line 464 is `n_parallel = 1`, but `arg.cpp:1373` `params.n_parallel = -1;     // auto by default` under `ex == LLAMA_EXAMPLE_SERVER` overrides it for the server |

Newly written SOURCES row re-opened: **S599** (`tools/server/server-models.cpp` @ b12177) — sha256 `cab14969…` equal;
quote `inst.meta.port        = common_http_get_free_port();` is line 1218 verbatim, 7 words (≤25). Agree.

Sample result: 2 admits + 2 rejects, all agree. The one disagreement in the round (RV02 passed R01/R08, SC01 found the
overstatement) became lesson M4 and QUALITY KQ149 citing it — a grounded criterion, not an unlearned disagreement.

## 4. Trend verdicts

- **expansion: improved** — capability `linear-probe-paths` admitted to `SCORECARD.md` and re-measured by this closure
  (base exit 1 → M2/tip exit 0); four tier-A rows S596–S599 opened (digests re-verified here) and mined into
  `corpus/knowledge/serving-thresholds.md` §Round 92 revision. No new knowledge file (63 → 63).
- **quality: improved** — the round-91 T01–T14 table (T07 misstated the server's slot count) is superseded by R01–R15,
  each llama.cpp option row help-checked against the pinned binary (re-measured `help_checked=7 help_disagree=0`);
  S593's "one parallel sequence" teaches cell corrected by appended note; the R01/R08 overstatement is marked, not left
  unmarked; the probe-bound r90 receipt staled by C2 was re-bound.
- **discernment: improved** — spot-check agrees on 2/2 admits and 2/2 rejects; the author took the unfavourable reading
  of its own K2 on a scout's finding the designated reviewer missed, and turned it into KQ149 (lesson M4); KQ147/KQ148
  each cite their lesson row (M1, M3).

## 5. Routed defects (lane must answer next round)

- **R1 (carried, r87 L0):** `round75-instruments` red; `APPEND_DEBT unaccepted` grew 16 → 18 (events 95 → 97) this
  round — account the two new events or state why they are not debt.
- **R2:** superseding rows for R01 and R08 under KQ149 (every setter named or excluded: presets, `AIP_MODE`, router
  child), not prose only (lane planned r93 item 4).
- **R3:** the C1 counter cannot discriminate decision-cell overreach (CR02: 14 wrong tables pass; MT02 16/23 counter
  mutants exit-identical; V7 `TYPE_CHECKING` binds) — the successor counter the lane planned (r93 item 2) must be shown
  able to fail on the R01/R08 class before it counts.
- **R4:** `json_array` quadratic path (SC02) outside C2, and the C2 counter's disclosed gaps (CR01 five forgeries, MT01
  4 surviving mutants) — lane planned r93 items 1 and 3.
- **R5:** report-commit author date precedes the cited tip; land reports with an author date at or after the lane tip
  (evidence-timestamp rule, §Evidence standard).
- **R6 (carried):** RV02 NOTE-1 (R03 wording).

## 6. SHONEN note for the operator

All four boxes are `[~]`. Boxes 2 (end-to-end task: C2 probe graded on stub listeners, LOG §Round 92) and 3
(instructions executable without oral context: this closure re-ran both frozen counting commands from
`plans/round-92-claims.md` text alone, at base, M and tip) look checkable by a non-author. Box 1 is checkable once the
R01/R08 superseding rows land (R2); box 4 rests on CN01 and the PROVINCE round-92 line. Promotion is operator-owned.
