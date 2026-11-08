# Round 99 wave-1 recon — SC01Recon (scout)

Independently re-derived the plan's before-values and mapped the surfaces the three frozen claims
touch. Base revision `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`; instruments live at the freeze commit
`f6e7ccc285e0c1207378f73c394acbfda58bff23`. Nothing tracked was edited; all runs in
`/fast/scratch/hyaku/kama-r99/SC01Recon` (deleted at exit). Receipts: `./out/SC01Recon/01..11`.

Measured with: `git show` extracts of the frozen blobs, `python3` runs of the three counters and the
round-98 counter, `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census`, one `git clone
--shared` fixture, materialized tree mirrors (`--tree`), and scratch copies of both probes with a
loopback stub.

## 1. Plan value vs re-derived value

| # | Plan / claims.json value | Re-derived here | Verdict |
|---|---|---|---|
| C1-b | r98 counter, W14 line dropped: `ROUTER_BUDGET98_CONTROL cells=5 cells_ok=5 … survived=1 ok=1`, exit 0 | identical line, `probe_sha256=40ab387e…`, exit 0 (`01`) | match |
| C1-a | grader at M1 prints `… complete=1 met=True`, exit 0 | `… complete=1 population_shaped=1 met=True counter_sha256=e76c35b4… rev=f6e7ccc2…`, exit 0 (`02`) | value match, **literal mismatch M1** |
| C1-dn | grader vs r98 counter: `refused=0 met=False` exit 1 | `selected=- ran=5 … refused=0 … population_shaped=1 met=False`, exit 1 (`03`) | match |
| C1-pos | unmodified r99 counter accepts a complete population | `ROUTER_BUDGET99_CONTROL cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1`, exit 0 | match |
| C2-b | base: `checks=12 mismatches=10 met=False`, exit 1 | identical (`04`) | match |
| C2-a | at M2: `checks=12 mismatches=0 met=True`, exit 0 | reproduced at a scratch-clone commit carrying the corrections (`11` §A) | match with frozen bytes |
| C2 census base | `681c80a4` → 361 (A 344, B 11, C 6; mined 324, queued 8, rejected 29) | exactly that | match |
| C2 census tip | `649bb2e9` → 363 (A 345, B 11, C 7; mined 325, queued 8, rejected 30) | exactly that; freeze tip 366 (A 347, B 11, C 8; 327/8/31) | match |
| C2 split | 7 attack / 5 non-attack, derived | 7 = RV01SelfAssess, RV02BudgetCells, CR01Boundary, CR02Wording, MT01Forgeries, SN01StepFlips, RV03Intent; 5 = SC01SiblingScan, SC02SourceReopen, EX01SelfAssessControl, EX02BudgetControl, CN01Overlap | match (membership note M5) |
| C2 results | seats=12, results=12, 0 dead | seats=12, len=12, all outputs non-empty (min 636 chars), dead=[] | match |
| C2 gate | `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1`, six FAIL arms | 14 arm lines, 6 `exit=\d+ FAIL`, verdict exact; selfdesc, newest-closure, round-scope, round-clean, round75-instruments, round78-instruments | match |
| C2 pointers | `SCORECARD.md:6431`, `LOG.md:4040` | both are the stale wave lines; SB01-equivalent sentence at `LOG.md:4044` | match |
| C3-b | base `cells=5 mismatches=4 base_mismatches=4 flips=0 stable=5 met=False`, exit 1 | identical; all five cells `MODEL_UNLOADED/router-unloaded` exit=2 (`06`) | match |
| C3-a | candidate `cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True`, exit 0 | identical, `probe_sha256=829fbde5…`, `base_sha256=40ab387e…`, `candidate=yes` (`07`) | match |
| C3 cells | U1–U4 flip to `router-autoload-unread`, P1 stays `router-unloaded`, verdict `MODEL_UNLOADED`, exit unchanged | exactly that, exit=2 in all five | match |
| C3 harness | `tests=77 passes=77 failures=0` on the candidate | identical (needs a writable `TMPDIR`) | match |

## 2. Mismatches (each with the command that shows it)

**M1 — C1's frozen predicate line is not what the grader prints.** The plan quotes
`CONTROL_POP99 … complete=1 met=True`; the emitted line has `population_shaped=1` between them plus
`counter_sha256=`/`rev=` (grader lines 152–160; `02`). A grader matching the plan's literal string fails.
`plan:40-42` vs `out/SC01Recon/02-c1-grader-at-freeze.out`.

**M2 — the frozen C2 counter's docstring misstates its own before-value.** `mismatches=9` at
`tools/round99-record-audit.py:10` (freeze commit); actual, plan and `controls/c2-base.out` all say 10.
`git show f6e7ccc2:tools/round99-record-audit.py | sed -n 10p` vs `04`.

**M3 — the frozen C2 counter cannot grade a tree, and the recorded forged receipt needs post-freeze
bytes.** Under `--tree` the frozen `read_bytes_at` reads the tree's `corpus/SOURCES.md` for **both**
census revisions: honest mirror → `mismatches=1` (check 8, 366/366), forged → `mismatches=3` (1,2,8),
mirror without SOURCES.md → exit 2. The working tree already replaces that branch (sha
`5e2be139…`→`59f22d5e…`, uncommitted) and then gives 0 / 2 — the 2 matching the untracked
`controls/c2-forged.out`. Consequences: C2 kill rule K1 ("the counter's bytes change after the freeze
commit") is live if the edit is committed at M2; and C2 limit (d) ("grades the two frozen historical
revisions, never the tip") is false for the frozen bytes. `./out/SC01Recon/11-c2-frozen-counter-tree-path.out`.

**M4 — the plan's forged-control description does not match its receipt.** Plan ¶C2 says the forged
mirror keeps the census mislabel (i.e. check 7 should fire); the receipt shows only checks 1–2. A
forge that also mislabels the lesson census sentence yields `mismatches=3` (1,2,7) with the
working-tree bytes. `11` §B.

**M5 — the 7/5 split's membership is the counter's role table, not the record's.** `ATTACK_ROLES`
(`tools/round99-record-audit.py:60`) excludes `connector`, so `CN01Overlap` is non-attack and
`RV03Intent` (revenger) is attack. The round-98 SCORECARD/LOG counted CN01 among the attack seats and
omitted RV03Intent: same cardinality 7/5, different membership, and the correction silently adopts the
counter's partition. `out/SC01Recon/09-round98-w1-results.json` + `SCORECARD.md:6432-6433`.

**M6 — C3's frozen counter docstring misstates its base value.** `flips=0 stable=1` at
`tools/round99-autoload-states.py:11-12`; actual, plan and `controls/c3-base.out` say `stable=5`.

**M7 — C3 plan limit (c) is inverted.** "the function returns 2 only when `HAVE_PY` is set" — the code
returns 2 exactly when `HAVE_PY != 1` (`[ "$HAVE_PY" -eq 1 ] || return 2`, candidate:891). The second
clause ("absent python3 the candidate returns unread") is the true behaviour.

**M8 — C3's regression receipt is cited before it exists, with the wrong counter label.**
`controls/c3-regression.out` is absent; the committed `corpus/knowledge/router-props-autoload.md`
already cites it as `ROUTER_BUDGET99 cells=19 mismatches=0`, while plan ¶C3 says the frozen **round-98**
counter prints `ROUTER_BUDGET98 cells=19 …`.

**M9 — the plan's census-start claim is unbound.** Plan ¶Frontier: "census start
`controls/census-start.out` (exit 0, 363 rows)". The committed receipt has no exit token and no row
count (`grep -c census_exit` → 0, `grep -c 363` → 0), unlike round-98's which ends `census_exit=0`.

**M10 — an opened candidate with no registry row.** `sources/s627-arg-models-autoload.txt` is committed
at freeze (arg.cpp `--models-autoload`, the flag's definition) but `grep -c S627 corpus/SOURCES.md` → 0
and neither the plan (three rows: S624/S625/S626) nor the round-99 lesson mentions it.

**M11 — SKILL.md is the C3 after-state's unwritten half and nothing grades it.** No
`router-autoload-unread` row exists (`grep` → 0 hits); `SKILL.md:1867` still lumps "a `/props` that
failed, was over the 4 MiB cap, or was not JSON" into `router-unloaded`. The C3 counter reads only the
probe, so the claim can be green while the exported reason table keeps the old lumping.

**M12 — a real behaviour regression in the candidate probe, invisible to the five cells.** Moving
`router_autoload` out of the `if` condition (`router_autoload "$port"; ra=$?`) disables errexit's
exemption. `check` masks it (`eval_rows || exit_code=$?`), but the plain-call paths
(`classify` at candidate:1319 `cmd_listeners`, :1383 `cmd_consumers`) abort with no row: measured
no `PLAIN_CALL` line and rc=2 for a non-router `/props`, rc=1 for an explicit **off** `/props`; the
base probe printed `MODEL_UNLOADED/router-unloaded` with rc=0 in both cases. Readable-autoload-true
`/props` behaves identically in both probes. `./out/SC01Recon/10-c3-probe-plain-call-regression.out`
(the `cmd_consumers` case is the same two-statement shape at :1383 — inference, not separately run).

**M13 — the C1 do-nothing receipt carries a misleading token.** `population_shaped=1` is printed for
the round-98 counter, which has no population logic at all: the grader defaults `population=1` when
neither `selected` nor `ran` appears (`tools/round99-control-population.py:126-130`). `03`.

## 3. Lines the predicates actually depend on

* `tools/round98-router-budget.py@439fdb3d:653-675` — control branch: `n = len(natural)` (655),
  `survived`/`caught` (656–657), `ok = survived if …` (669), print (670), return (675). **No
  `selected`/`ran` comparison.** The `want_cells` comparison at `:715` is in the natural pass only and
  unreachable from `--control` (so lesson M2's "unreachable from `--control`" is right).
* `tools/round99-router-budget.py@f6e7ccc2:672-696` — `want_selected` (676), `population_ok` (679),
  `ok = int(ok and population_ok)` (694), the `ROUTER_BUDGET99_CONTROL` line (695–700).
* `tools/round99-control-population.py` — `patch_drop` (55-66, exactly one anchor), `invoke` (108-118),
  `refused`/`complete`/`population`/`met` (126-134), the predicate print (135-140).
* `tools/round99-record-audit.py` — 12 `chk()` call sites (178-232), `correction_blocks` (65-75),
  `census_counts` (87-101, `^(?:FLEET|file)\t` regex), `read_bytes_at` (252-256; the byte under
  dispute), gate regexes (215-216).
* `tools/round99-autoload-states.py` — stub answers (84-99), `verdict_reason` (125-138), CELLS (141-145),
  base leg `BASE` (52) + `git show BASE:tools/kama-probe.sh` (187), tip leg (188), scoring (207-225).
* candidate probe — `set -euo pipefail` (93); `router_autoload` tri-state (891-917: `|| return 2`,
  on/off/unread python, `case` 0/1/2); `router_refine` call shape (951-954) and remap (970-976);
  `main "$@"` (1741).
* counts: `LEGACY_CELLS` 13 (incl. `W10-rewrite`), `NEW_CELLS` 6, `R97_CELLS` 17, `CELLS` 19 — so the
  population check (`n == want_selected`) is consistent in all four `--cells` modes; no blanket-refusal
  mode was found.

## 4. Not measured / open

* **K5, the round-98 19-cell regression on the candidate probe: NOT RUN.** The L1 ordered it stopped
  (64 burners under host load ≈165). I have 5 of 19 natural cells green with the candidate
  (`W14–W18 ok=1`, from the partial `c3-regression3` receipt) and no load pass; do not read this as a
  regression result. The candidate keeps `router-unloaded-autoload`/`router-model-*` cells unchanged by
  construction (the remap only fires on `down == router-unloaded` with `ra == 2`), but that is reasoning,
  not measurement.
* `measured/c2.out`, `measured/c3.out`, `controls/c3-regression.out`, `controls/census-end.out` do not
  exist: M2/M3 are still pending, so C2/C3 are only measurable at a fixture commit (C2) or with
  `--probe-file` (C3) today. C1's M1 = the freeze commit and is already green (`measured/c1.out`
  matches my rerun byte for byte).
* Untracked at freeze and still uncommitted: `LOG.md`, `SCORECARD.md`, `tools/round99-record-audit.py`,
  `corpus/lessons/round-99.md`, `controls/{c2-forged,c3-harness-candidate,c3-mutant-blanket}.out`,
  `measured/`. The wave is therefore attacking a freeze commit whose C2/C3 after-states live only in
  the worktree; M2 must carry them, and that is where K1 bites (M3 above).

## 5. Tooling

No installs, no upgrades, no pacman. Only `python3`, `bash`, `curl`, `git` (read-only verbs plus
`clone --shared` and fixture commits inside my scratch), `sha256sum`, `ps`.
