# Round 93 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-07
subject: kama round 93. Lane HEAD `c0fbff4277119cd518aa0dbc5cc9fd5137590626`, base `5af794958b0fc08f574aa2e67650282269549b02`, freeze `0f272a3773be25a6cbdaf75f1a7a3ec293b60f8d`.
report: `.ufo/reports/round-93/kama.md` (fleet repo, commit `c6292a8a116ea72729f616ca0e590086f2bfe31a`, author `kama-shokunin`, author date 2026-11-07T00:36:12-03:00, committer date 00:43:47-03:00)

Verdict: status `ok`, **not admitted** (`rejected-honest-stop`). C1 (operability, capability `router-file-repeat`)
verifies: this closure re-ran the frozen counter at base, M1 (`fe5f031c`), the repaired M1b (`b3765799`) and the tip.
C2 (depth) is not verified: its frozen K2 ("a non-author read finds a misstating row or decision") fired through
wave-1 RV02 and SC01; the lane recorded this itself and this closure confirms both RV02 findings against the pinned
upstream bytes. No owned axis is harmed; the admit/reject sample agrees with the lane's gate.

Dispatch digest (`.ufo/watchdog.log`, mutable; copied):
`2026-11-06T23:20:48-03:00 launch kama round=93 pgid=326849 driver=hyaku-inline attempt=1` /
`2026-11-07T00:44:18-03:00 complete kama round=93; hyaku-inline attempt=1`.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H %ad' -- .ufo/reports/round-93/kama.md` | `kama-shokunin c6292a8a…`; committer 00:43:47 (before `complete` 00:44:18) | ok |
| prompt committed by lane identity | same for `.ufo/prompts/kama-round-93.md` | `kama-shokunin dc66a2e8…` (23:20:24) | ok |
| report lands after lane tip | `git log -1 --format='%ad / %cd' c0fbff42` vs report commit | tip 00:42:30/00:42:30; report committer 00:43:47, but report **author** date 00:36:12 precedes the tip it cites | ok (R5 recurs, see defects) |
| SHONEN heading, one line per box | report `## SHONEN`; `SHONEN.md` has 4 boxes | 4 lines, all `[~]` with pointers, no `[x]` | ok |
| cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> refs/heads/master` and `--is-ancestor 5af79495 <h>` for all 28 report hashes | 28/28 ancestors, all descend from base, all authored `kama-shokunin`; `git rev-list --count 5af79495..c0fbff42` = 28 (every round commit cited) | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; remote `c0fbff42…` | ok |
| prompt carries contract | every static (non-placeholder) line of `kimi-shokunin/templates/round-prompt.md` (140 lines) `grep -F` in the prompt (117506 B) | `static=105 missing=0`; §6 hyaku addendum at line 141 | ok |
| counters frozen (K1/K3) | `git diff --stat 0f272a37 c0fbff42 -- tools/round93-router-repeat.py tools/round93-setter-rows.py plans/round-93-claims.md` | empty | ok |
| round shape | report vs `.ufo/waves/round-93/w1/` | one wave `w1`, 12 seats dispatched, 11 reports (CN01, CR01, CR02, EX01, EX02, MT01, MT02, RV01, RV02, SB01, SC01); SC02 unsettled at filing, no `WAVE-DONE`, no `w1-results.json` | conformance defect (disclosed) |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`; W04 duplicates and W01 (S481) only, all pre-existing; none on S600–S603 | ok |
| census before → after | `git show <r>:corpus/SOURCES.md \| grep -cE '^ {0,3}\| S[0-9]{3,}'` | 339 → 343 (S600–S603) | matches report |
| knowledge entries | `git ls-tree <r> corpus/knowledge/ \| wc -l` | 63 → 63 | ok |
| append-only files | `git diff 5af79495 c0fbff42 -- LOG.md corpus/SOURCES.md \| grep -c '^-[^-]'` | 0 | ok |
| pre-report gate (committed evidence) | `.ufo/waves/round-93/measured/gate-final.out` (header `rev=d30f0e1e…`) | `PRE_REPORT round=93 arms=14 failed=4 uncommitted=1`, exit 1: `round75-instruments` (carried, `APPEND_DEBT events=100 unaccepted=21 bad_rows=19`), `round78-instruments` (`LIVE_RECONCILE_SELFTEST pass=1 fail=3`), `round-scope`/`round-clean` (the receipt itself uncommitted while the gate ran) | conformance defect |
| host 8080 listener (round78 arm) | `ss -ltnp \| grep ':8080 '` at closure | `127.0.0.1:8080 … ("ollama",pid=134935)`, `/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama serve` | confirms the report's host note |

Conformance defects (status-neutral, named): (a) terminal pre-report gate red on four arms — the carried
`round75-instruments` arm, whose `APPEND_DEBT` population keeps growing (r91 95/16, r92 97/18, r93 100/21), the
`round78-instruments` arm red on a non-lane host listener, and two scope arms red only because the receipt was written
into the tree it graded; (b) the report's author date (00:36:12) precedes the tip it cites (00:42:30) — the same defect
as round-92 R5, while lesson §Dispositions R5 states "its author date is checked against the tip before filing";
(c) filed without `WAVE-DONE` (SC02 unsettled), disclosed by the lane under the operator wrap-up notice; (d) planner
seat held by the L1 (validator rejects `planner`), disclosed.

## 2. Claims (step 2) — re-measured vs evidence-verified

### C1 — operability: router model-file verdict repeat-invariant (capability `router-file-repeat`)

Re-measured (counter frozen since `0f272a37`; it reads committed bytes via `git show`, builds fixtures under
`--work`; scratch `/tmp/k93/`, nothing written in the lane). Host load at closure was 72–248 (other fleet lanes):

```
python3 tools/round93-router-repeat.py --repo . --rev 5af794958b0fc08f574aa2e67650282269549b02 --work /tmp/k93/c1-5af79495
→ ROUTER_REPEAT cells=10 mismatches=6 positive_mismatches=1 probe=rev probe_sha256=36631d49…; exit 1   (load 72→244)
  R02–R06 MODEL_OK/router-unloaded-autoload 3/3 runs (4.27–9.11 s); P04 run1 MODEL_OK 5.59 s
… --rev fe5f031cb1b9d33e1160360d892149b8ac3c7771   (load 244)
→ ROUTER_REPEAT could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'; exit 2
… --rev b37657998858b6300fc8fbbbebb7e256239bf0f8   (load 248)
→ cells=10 mismatches=1 positive_mismatches=1; exit 1 — only R01-slow-x1 (ONE listing entry, no repeat) MODEL_OK at 5.82/5.56 s
… --rev c0fbff4277119cd518aa0dbc5cc9fd5137590626   (load 202→154)
→ cells=10 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=1e21c1fb…; exit 0
re-run at load 148: --rev fe5f031c… → cells=10 mismatches=0 positive_mismatches=0 probe_sha256=159c8068…; exit 0
re-run at load 135: --rev b3765799… → cells=10 mismatches=0 positive_mismatches=0 probe_sha256=1e21c1fb…; exit 0
```

Reading: the counter grades M1, M1b and the tip green at loads 135–202 and the base red on all five repeat cells
(R02–R06, the claim's population) — the before → after holds as reported (`controls/c1-base.out` 5/0 exit 1 →
`measured/c1.out` 0/0 exit 0). The two non-green runs at load ≈245 are the counter's fixture sanity refusing
(exit 2, could-not-evaluate) and R01, a single-entry listing whose one 4 s parse deadline expires at that load — the
same shape at base and M1b, outside the repeat claim, and the plan's disclosed load limit (lesson M7 class). Not a
falsification; recorded as a load note.

Evidence-verified (committed receipts, not re-executed — lane-owned suites/gates): harm at base, M, M1b and tip
(`controls/harm-base.out`, `measured/harm-M.out`, `harm-M1b.out`, `harm-tip.out`) are identical after stripping hex
digests and timings (`md5` `9ad6bcbe…` for all four; `diff` base vs tip empty): check.py 77/77, test-snapshot 30/0,
r89 11/0/0, r90 13/0/0, r91 12/0/0, r92 15/0/0, router 1234 `MODEL_OK router-unloaded-autoload`. `tools/kama-probe.sh`
at the tip hashes `1e21c1fb…` = the M1b probe the harm-tip and tip counter graded; `git diff --stat b3765799 c0fbff42 --
tools/ tests/` is empty. RV01 DEFECT-1 (same-size rewrite, mtime restored) reproduces red at `fe5f031c` and green at
`b3765799` 3/3 each (`measured/c1-ctime-rewrite.out`); the gap shapes (hard links, symlinks, one entry two flags,
2048 valid-last) are right at M1b (`measured/c1-gapshapes.out`). **C1: verified. operability: improved.**

### C2 — depth: port and slot-count setters P01–P48, decisions R16/R17 (sourced S600–S603)

Re-measured (counter frozen; downloads the pinned codeload archive, sha256 checked):

```
python3 tools/round93-setter-rows.py --repo . --rev 5af794958b0fc08f574aa2e67650282269549b02 --work /tmp/k93/c2-5af79495
→ SETTER_ROWS population=48 rows=0 bound=0 … missing=48 … archive_sha256=f50a52f4…ea13; exit 1
… --rev ee19acbdabc8ac572e82ae56459c364457895b06
→ SETTER_ROWS population=48 rows=48 bound=48 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 decisions=2 decisions_bound=2; exit 0
… --rev c0fbff4277119cd518aa0dbc5cc9fd5137590626 → identical; exit 0
```

The counting predicate is met. K2 (non-author read) — **fired; confirmed by this closure** against the raw
upstream files at `b12177` (`curl -sfL https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`):
- `common/arg.cpp` (sha256 `c69c0e07…`, equal to S596): lines 2524–2531 are the `else` branch's `--parallel`, and
  line 2529 is `params.n_parallel = value;` — the same variable as P03. `SKILL.md:1987` labels P06 parameter `-` and
  effect `unrelated`, which the section's own glossary (`SKILL.md:1978`) defines as "another variable, or text". P05,
  P07 likewise. The row misstates under its own vocabulary.
- `common/arg.h` (`42f21df7…`) lines 91–95: `operator<` compares `strcmp(args[0], other.args[0])`;
  `common/preset.cpp` (`793ad2c7…`) line 44 iterates `options` (a `std::map`) to build argv. `--port`
  (`arg.cpp:3318`) sorts before `--vision-gemma-4b-default` / `--vision-gemma-12b-default`, whose lambdas set
  `params.port = 8014;` (`arg.cpp:4753`, `4764`). `server-models.cpp` (`cab14969…`) lines 268–286
  `unset_reserved_args` remove no preset model option and line 316 sets `LLAMA_ARG_PORT` from the router's port —
  so R16's router-child clause (child listens on P41's port) is overridden for such a preset. Source read only, as
  the lane says (not run on a live child).

**C2: not verified** (agrees with the author). Axis grade **depth: unchanged** — score stays 7, no admitted move; not
harmed, because the misstatement is marked in the same round (`SKILL.md` §Round 93 correction, lesson M4/M6/M8,
QUALITY KQ151 with a receipt that fails: `measured/kq151-twins.out`) and the rows' text cells are archive-exact.

### Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured: base 5 repeat-cell mismatches exit 1 → M1/M1b/tip 0/0 exit 0 |
| depth | unchanged | C2 not verified (K2 fired on P05–P07 and R16); score 7 unchanged; not harmed (marked correction) |
| freshness | unchanged | no freshness row change in `git diff 5af79495 c0fbff42 -- SCORECARD.md` |
| coverage | unchanged | score 9 unchanged; row text re-anchored to `PROVINCE.md` only |
| calibration | unchanged | score 7 unchanged; row re-pointed to the round-92 closure; honest C2 call credited under discernment |
| adjacency | unchanged | score 7 unchanged; CN01 found no sibling contradiction |

## 3. Discernment spot-check (LEARNING.md) — `corpus/lessons/round-93.md` `## Gate`

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S600 llama.cpp `common/http.h` @ b12177 | admit (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/http.h, sha256 `949e44f9…2de1` equal | agree | line 324 is verbatim `int port = ntohs(serv_addr.sin_port);`, after `serv_addr.sin_port = htons(0);` (line 301): primary source for the free-port helper P27 |
| S603 llama.cpp `tools/server/server-models.h` @ b12177 | admit (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.h, sha256 `304c0136…a6a1` equal | agree | line 80 is verbatim `int port = 0;`; `server-models.cpp:1218` `inst.meta.port = common_http_get_free_port();` replaces it at spawn — grounds P46 as stated |
| `tools/server/server-models-sched.cpp:423` as a listen-port setter | reject (names another port) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models-sched.cpp, sha256 `b786ea09…` | agree | line 423 is verbatim the quoted `child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT) + "=" + std::to_string(models.base_params.port));` — it exports the **router's** own `base_params.port` to the child environment; the child's listen port comes from `server-models.cpp:316` (`LLAMA_ARG_PORT`) |
| codeload archive as a SOURCES row | reject (input, not a teaching source) | the C2 counter fetched https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 and printed `archive_sha256=f50a52f4…ea13` (three runs above) | agree | the archive is the counter's pinned input; every taught line is cited through a per-file raw row whose digest this closure re-measured equal (S600–S603, S596, S599) |

Newly written SOURCES row re-opened: **S601** (`tools/server/server-connect.cpp` @ b12177) — sha256 `2a505b29…c9df`
equal; quote `"--port", std::to_string(port),` is line 208 verbatim, 3 words (≤25). Agree. Also S602 line 92
`int port    = 9931;` verbatim (4 words). Cosmetic: the anchor cells read `opened2026-11-07` (missing space).

Sample result: 2 admits + 2 rejects, all agree. The round's one disagreement (RV02/SC01 vs the author's C2 table)
became lessons M4/M6/M8 and QUALITY KQ151 citing M4 — a grounded criterion, not an unlearned disagreement.

## 4. Trend verdicts

- **expansion: improved** — capability `router-file-repeat` admitted to `SCORECARD.md` and re-measured here (base
  exit 1 → M1/M1b/tip exit 0); four tier-A rows S600–S603 opened (digests re-verified here) and mined into
  `SKILL.md`. No new knowledge file (63 → 63).
- **quality: improved** — a load-dependent false green (repeat listings of an invalid GGUF graded `MODEL_OK`) is gone
  at every revision this closure ran under moderate load, harm suites unchanged; a wave-found stale-state regression in
  the fix (RV01 DEFECT-1) was repaired in round with a failing-before receipt; the probe-bound r90 receipt staled by C1
  was re-bound (KQ148); the C2 overstatement is marked, not left standing.
- **discernment: improved** — spot-check agrees on 2/2 admits and 2/2 rejects; the author took the unfavourable
  reading of its own K2 on two seats' findings and turned it into KQ151 (lesson M4); KQ150 cites M1 with a receipt
  showing it able to fail.

## 5. Routed defects (lane must answer next round)

- **R1 (carried, r87 L0):** `round75-instruments` red; `APPEND_DEBT unaccepted` 18 → 21 (events 97 → 100) — account
  the three new events or state why they are not debt.
- **R2:** superseding rows for P05–P07 (a label for "setter the pinned program never registers") and R16/R17 scoped
  per M6/M8 (argv-order rule, config-file / llama-cli / AIP setters) — not prose only (SCORECARD §Planned r94 item 5).
- **R3:** stale capability rows. `SCORECARD.md:296`/`6163` `router-file-repeat` still names the four-field key
  `(device, inode, size, mtime)` and evidence `fe5f031c` (the revision RV01 DEFECT-1 falsified); the tip key adds
  `st_ctime_ns` (`b3765799`). `SCORECARD.md:297`/`6164` `setter-rows` cites the C2 decision rows without saying C2 is
  not verified. Corrections sweep every mention (§Evidence standard).
- **R4:** the C1/C2 counters' disclosed gaps (CR01 15/19 wrong probes pass; CR02 20/38 forged tables bind; MT01 12/16
  and MT02 16/26 mutants survive) and the load-sensitive single-entry cell R01 / fixture sanity (this closure: exit 2 at
  load 244, R01 red at 248) — a counter whose cells flip with host load should report could-not-evaluate, not a verdict.
- **R5 (recurs):** report-commit author date precedes the cited tip again; the R5 disposition claims a check that did
  not hold.
- **R6:** read SC02ProbeVerdictSweep's output (unsettled at filing) and grade it against C1 next round.
- **R7:** a terminal gate receipt that grades its own uncommitted file is red by construction (`round-scope`,
  `round-clean`); write it outside the graded tree or commit before grading.

## 6. SHONEN note for the operator

All four boxes are `[~]`. Boxes 2 (end-to-end task: C1 probe graded over 10 router listings, EX02 live b12177 router vs
a completion oracle) and 3 (instructions executable without oral context: this closure re-ran both frozen counting
commands from `plans/round-93-claims.md` text alone at base, M and tip) look checkable by a non-author. Box 1 waits on
R2; box 4 rests on CN01 and the PROVINCE round-93 line. Promotion is operator-owned.
