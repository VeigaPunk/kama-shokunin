# CON01Siblings — report (round 70, kama lane)

Seat: connector (cross-lane pattern scan), advisory leaf. Assignment: does any sibling
lane hold an instrument that (a) reconciles a lane's self-description with its tree, or
(b) grades a test-runner/census verdict fail-closed on not-evaluated members — and does
kama's province already cover its own version?

Deliverables: this report and `overlap.md` (table + province answer + one bounded move).
No tracked lane file was written, no sibling repo was written, no git/jj mutation was run,
no subagent was spawned, no tool was installed. Scratch
`/fast/scratch/hyaku/kama-r70/CON01Siblings/` was created and removed (see §Scratch).

## Verdict in one paragraph

Both instrument classes exist in sibling lanes and neither overlaps kama's objects. (a)
Self-description reconcilers: kaidoku (`round-44/c2-counter.py` + rubric), souji
(`souji-declared-evidence.py`, `souji-capability-agreement.py`, `souji-capability-cells.py`),
kake (`freshness-sweep.mjs`), kumitate (`claims-check.mjs`), mori (`mori-pin-check.py`,
`mori-retention-reconcile.py`), chousa (`claims-audit-v2.py`, `inference-ground.py`), mado
(`mado-receipt-citecheck.py`), tsukuroi (`check-path-reconciliation.py`). (b) Fail-closed
not-evaluated: kotodama (`claims-freshness.py`, exit 3), kaidoku (`c2-counter.py`, exit 2
"never a pass"), souji (`souji-capability-cells.py`, UNBOUND → mismatch → exit 1),
tsukuroi (`tsukuroi-census.sh`, unreadable plane → BLOCKED, exit 2), tameshi
(`arm-liveness.py`, ARM_DEAD + vacuous manifest exit 2), kake (exit 2 unreadable). Two
lanes deliberately keep an unevaluable class advisory (kumitate `ROW_NO_SECTIONS` warn →
exit 0; mado `skipped_large` counted, exit from `missing` only) — contrasts, not owners.

kama's province covers its census by name in two round notes but covers **neither**
instrument in the Owns instruments row (`PROVINCE.md:17`), and neither is in the SCORECARD
canonical capability list (15 rows, `SCORECARD.md:3669`). The reconciler is registered only
as a tier-A census member (`tools/round65-host-census.py:59-60`) and a SKILL.md registry
row (`SKILL.md:1433`). This is internally consistent — the reconciler's `province` fact
only iterates canonical capability rows (`tools/round42-selfdesc-reconcile.py:47-48,373-379`)
— but it is a self-coverage blind spot of exactly the class mori fixed on its own pin
registry (`mori-pin-check.py:898-901`: "the registry floor and `dropped` cannot see the
reconciler's own row").

## Command ledger (every command, decisive output, exit code)

All commands ran from `/home/vgpnk/Projects/shokunin` (fleet root) or with an absolute
lane path; read-only git was not needed and not used beyond `grep`/`ls`/`sed`/`head` and
one read-only Python import of kama's own census module. Output shown is the decisive
lines as printed (long streams were piped through `head`, noted per row).

| # | command | observed output (decisive lines) | exit |
|---|---|---|---|
| 1 | `mkdir -p /fast/scratch/hyaku/kama-r70/CON01Siblings` and the out dir; `ls -d /home/vgpnk/Projects/shokunin/*-shokunin` | 21 lane repos: audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama, kasegi, kengaku, kotoba, kotodama, kumitate, lore, mado, mori, revenger, souji, tabi, tameshi, tsukuroi | 0 |
| 2 | `cat /home/vgpnk/.omp/agent/RULES.md \| head -60` | tooling directive text; no install needed this run | 0 |
| 3 | `cat kama-shokunin/.ufo/waves/round-70/controls/freeze.txt` | C1 base `mismatches=10 … province=4`, exit 1; C2 base `refused_fixture_exit=0`; census base `HOST_CENSUS pass=21 fail=1 refused=0 total=22 …`, exit 1 | 0 |
| 4 | `cat kama-shokunin/PROVINCE.md` | domain = local model serving/endpoint health; Owns table; round-65/67 host notes | 0 |
| 5 | per-lane hit count, all 20 non-kama lanes: `grep -rlE 'selfdesc\|self-descri\|not_evaluated\|not-evaluated\|fail-closed\|fail_closed' --include='*.py' --include='*.sh' --include='*.md' --include='*.tsv' --include='*.txt' <lane> \| wc -l` | counts 60–1522 per lane (kasegi 1432, kumitate 1522 highest); density is dominated by wave artifacts, hence the tool-scoped scans below | 0 |
| 6 | `grep -rn 'selfdesc\|self-descri' --include='*.py' --include='*.sh' --include='*.md' . \| grep -v '^./kama-shokunin/' \| head -40` | no sibling instrument; hits are fleet reports (`.ufo/reports/round-*/…`) and `.ufo/l0-questions.md:236` (kama's own NTFS `\|`-path limit naming `round42-selfdesc-reconcile.py --selftest`); kagi round-32 `corpus/self-description-sweep.sh` is prose about its own sweep, not a reconciler named as such | 0 |
| 7 | `grep -rn 'not_evaluated\|not-evaluated' --include='*.py' --include='*.sh' . \| grep -v '^./kama-shokunin/' \| head -40` | `kotodama-shokunin/tools/harness/claims-freshness.py` (many lines: 1639, 1714-1753, 1799-1803, 1873-2013); `mado-shokunin/.ufo/waves/round-56/.../selfcheck.py:6,226` (wave artifact, excluded) | 0 |
| 8 | per-lane tool-dir scan: `grep -rlnE 'fail[-_ ]closed\|not_evaluated\|not-evaluated\|not_evaluable' <lane>/tools <lane>/scripts <lane>/*.py` | chousa(inference-ground, digest-in-tree, research-gate.sh), kaidoku(round-41..63 counters, receipt-audit, annotation-sweep), kake(canonical_audit.py, freshness-sweep.mjs), kotodama(harness/claims-freshness.py, r8_checks.py, receipt_guard.py + gates), kumitate(many scripts incl. wave-census, claims-check, counter-rerun), mado(mado-action-plan.py, mado-receipt-citecheck.py), mori(mori-census.sh, mori-pin-check.py, mori-retention-reconcile.py), souji(cand-*.sh, souji-landing-gate.py, souji-capability-agreement.py, souji-evidence-cache.py, souji-seat-audit.py), tabi(round39/46 probes), tameshi(arm-liveness, mutate-and-run.sh, tally-audit-v3, evidence-disposition…), tsukuroi(tsukuroi-census.sh, check-boundary-contract.py, check-path-reconciliation.py, check-recheck-commands.py) | 0 |
| 9 | reconciler scan: `grep -rlnE 'reconcil' <lane>/tools <lane>/scripts` | kaidoku(round-26/36/38 c2 counters, round-44/49 runners), kotodama(d2/d4 assemblers, check-evidence-coupling, exercise-handoff-e2e, harness/r8_checks), kumitate(sources-check, surface-probe), mado(mado-verify.sh), mori(mori-pin-check, mori-retention-reconcile, mori-routed-check), souji(souji-citation-reconcile, souji-preservation-evidence), tsukuroi(check-path-reconciliation) | 0 |
| 10 | `ls kama-shokunin/tools/ \| head -60` and `grep -rlE 'not_evaluated\|selfdesc' kama-shokunin/tools/` | kama tools list incl. `round42-selfdesc-reconcile.py`, `round65-host-census.py`; selfdesc/not_evaluated hits in `round42-selfdesc-reconcile.py`, `round43-registry-audit.py`, `round58/63/64-c2-counter.py`, `round65-host-census.py`, `kama-llamacpp-live.py`, `kama-ollama-evidence.py` | 0 |
| 11 | `grep -n 'round42\|round65\|selfdesc\|self-descript\|census' kama-shokunin/PROVINCE.md` | line 17 lists instruments; 248, 264-265 name `round65-host-census.py`; 269 names "self-description reconciler selftest"; **no `round42` token anywhere** | 0 |
| 12 | `grep -n 'round42\|round65\|selfdesc\|census' kama-shokunin/SCORECARD.md` | `round42-selfdesc-reconcile.py` appears only as the derivation tool (lines 141, 147, 2286, 3166 …), never as a capability row | 0 |
| 13 | `grep -n 'province' kama-shokunin/tools/round42-selfdesc-reconcile.py` | 47-48: "province every `tools/` or `registry/` token in a canon row's evidence cell"; 373-379: `bad("province", "PROVINCE.md lacks {tok} (capability …)")` | 0 |
| 14 | Python: enumerate canonical capability table (first attempt) | **failed**: my predicate looked for a header containing `First working round` in `l.startswith('\|')` form and found 0 tables → `IndexError` | **1** |
| 15 | `grep -n 'canonical list as of round' SCORECARD.md \| tail -3` and `grep -nE '^\| *Capabilit…'` | canonical lists at 3560(r67), 3613(r68), **3669(r69)**; headers `\| Capability \| What it can now do \| Evidence pointer \| First-working round \|` at 3673 | 0 |
| 16 | Python: parse rows under header line 3673 | 15 rows: sources-registry, ollama-offline-evidence-replay, live-llamacpp-lifecycle, gguf-declared-identity-replay, context-capacity-receipt, instrument-agreement, pin-watch, digest-ledger, hexrun-census, append-only-audit, live-receipt-replay, live-ollama-lifecycle, worktree-landing-check, receipt-pointer-audit, newest-closure-counter | 0 |
| 17 | Python: substring extract from `PROVINCE.md` line 17 | `round42` 0 hits, `round65` 0 hits, `host-census` 0 hits, `selfdesc` 0 hits; `census` 1 hit = `hexrun-census`; `self-description` 1 hit = append-only-audit entry. Row length 2086 chars, ends `…(the newest non-author closure, fail-closed on an undated one; round 69) \|` | 0 |
| 18 | Python: import `kama-shokunin/tools/round65-host-census.py` (read-only) and print `len(MEMBERS)` | `members 22`; tier-A members include `("A", "round42-selfdesc-reconcile selftest", ["tools/round42-selfdesc-reconcile.py", "--selftest", …])`; 12 tier A, 10 tier B | 0 |
| 19 | `sed -n '100,165p' kama-shokunin/tools/round65-host-census.py` | refusal marker → `refused += 1`; `TimeoutExpired` → `refused += 1` ("recorded, not a verdict"); `OSError` → `failed`; verdict line prints `refused=`; **`return 0 if failed == 0 else 1`** | 0 |
| 20 | `head -45 kama-shokunin/.ufo/waves/round-70/controls/refused-member-control.py` | two synthetic fixtures only: `synthetic-pass` + `synthetic-refused` (refusal marker `invalid path`); all-pass = two passing members; counter = pair (refused exit ≠0, allpass exit 0) | 0 |
| 21 | `ls kaidoku-shokunin/tools/round-44 tools/round-49` then `head -45 kaidoku-shokunin/tools/round-44/c2-counter.py` | r44 holds `c2-counter.py`, `c2-rubric.json`, `c2-controls.py`, `control-fixtures/`; docstring: exit 0 iff `mismatches==0`, every entry evaluable and ≥1 evaluated; exit 2 = "COULD-NOT-EVALUATE, never 'not a pass': it never counts toward the target" | 0 |
| 22 | `head -60 kaidoku-shokunin/tools/round-44/c2-rubric.json` | categories (a) evidence-pointer existence, (b) headline numbers, (c) SHONEN `path:line`, (d) planned rows vs next round, (e) claim verdict vs receipt exit, (f) README coverage-map count; 3 targeted entries, 77 excluded | 0 |
| 23 | `sed -n '3405,3420p' kaidoku-shokunin/SCORECARD.md` | R38-C2 row: "calibration — SCORECARD `## Owned axes`/`## Capabilities`, SHONEN boxes, PROVINCE Core/Frontier rows vs observed repo state"; 1 mismatch → 0 | 0 |
| 24 | `head -40 souji-shokunin/tools/souji-declared-evidence.py`, `sed -n '108,170p'` | classes A/B/C; `Counts line: assertions=<N> resolved=<R> skipped=<S> mismatches=<M>`; `Exit 0 iff M == 0`; `skipped` increments for unclassifiable spans and digests whose cell names no single path | 0 |
| 25 | `head -30 souji-shokunin/tools/souji-capability-cells.py`, `sed -n '285,320p'` | `SUMMARY items= bound_run= bound_record= unbound= mismatches=`; `UNBOUND` → `counts["mm"] += 1`; `return 0 if counts["mm"] == 0 else 1`; docstring exit 2 = could-not-evaluate | 0 |
| 26 | `sed -n '1,20p' souji-shokunin/tools/souji-capability-agreement.py` | K1 capability rows re-run in a private clone at REV; `SUMMARY … mismatches= rows= pointers= rev=`; "Exit 0 iff mismatches=0, 1 otherwise, 2 could-not-evaluate" | 0 |
| 27 | `sed -n '30,80p' kotodama-shokunin/tools/harness/claims-freshness.py` and `sed -n '1965,2030p'` | exit constants `0 all claims fresh · 1 at least one stale · 2 malformed/unusable baseline · 3 could-not-evaluate`; "a claim with neither field … is *could-not-evaluate*, never fresh: part 3 must exit non-zero"; summary line prints `N could-not-evaluate … clauses N (N hold, N contradict, N not evaluated)` | 0 |
| 28 | `head -35 tsukuroi-shokunin/tools/tsukuroi-census.sh`, `grep -n exit` | "any plane unreadable live -> BLOCKED arm fires, never a fake pass"; exit map `0 HEALTHY \| 1 DEGRADED \| 2 BLOCKED (worst plane wins)`; `BLOCKED > DEGRADED > HEALTHY` | 0 |
| 29 | `head -30 tameshi-shokunin/tools/arm-liveness.py`, `grep -n 'exit\|ARM_DEAD'` | `ARM_DEAD` when a pinned input cannot move the arm; vacuous manifest (zero rows) exits 2; selftest arms 1-3 cover live/dead/vacuous | 0 |
| 30 | `head -22 tameshi-shokunin/PROVINCE.md` | "verification-fixture craft — the reusable method … fail-closed arms, verdict-line discipline"; "every lane's gate remains its own; tameshi owns only the reusable craft (a pattern is admitted from evidence in TWO independent lanes before it is claimed general)" | 0 |
| 31 | `head -50 kumitate-shokunin/scripts/claims-check.mjs`, `grep -n 'ROW_NO_SECTIONS\|process.exit'` | `ROW_NO_SECTIONS` = warn, "topic-form row: member completeness unchecked"; selftest line 1000 "ROW_NO_SECTIONS: topic-form row → warn, exit 0" and 1003 "--strict promotes ROW_NO_SECTIONS → DRIFT exit 1"; fail-closed exit 2 for wave census, n/a here | 0 |
| 32 | `head -40 kumitate-shokunin/scripts/wave-census.mjs` | "Fail-closed (exit 2): the round dir is missing, holds no dispatch file, or a dispatch file does not parse"; absent reports are named, not counted as pass | 0 |
| 33 | `head -35 mori-shokunin/tools/mori-retention-reconcile.py`, `head -30 mori-census.sh` | reconciliation schema v2, `RETENTION_RECONCILED` / `_MISMATCH`; census verdict `MORI_CENSUS: CLEAN\|DRIFT`, exit 0/1/2 | 0 |
| 34 | `sed -n '120,140p' mori-shokunin/tools/mori-pin-check.py`, `sed -n '895,925p'` | `PIN_CHECK=met\|unmet … mismatches= unparsed= dropped= rebound= …`; `met` requires nine zero counts; **self-row arm**: "a measured tree that ships this instrument must pin it … deleting it left the registry green at 30 pins" → `dropped += 1`, verdict unmet | 0 |
| 35 | `head -30 chousa-shokunin/tools/inference-ground.py`, `head -25 chousa-shokunin/tools/claims-audit-v2.py` | inference bullets must cite S-ids and ground verbatim in cited spans, polarity flip refused; claims-audit flags self-assessment statements committed files contradict (r62: 14, r63: 4 statements) | 0 |
| 36 | `head -22 mado-shokunin/tools/mado-receipt-citecheck.py`, `grep -n 'skipped\|return'` | "MISSING paths are named, never silently skipped. Files over the 4 MiB read cap are skipped and counted"; verdict line `skipped_large=<s> verdict=TARGET_MET\|TARGET_MISSED`; `return 0 if not missing else 1` (skips do not gate) | 0 |
| 37 | `head -25 tsukuroi-shokunin/tools/check-path-reconciliation.py` | reconciles two historical counting methods over frozen inputs; "Exit 0 every fixed cohort explained, 1 unexplained/failed, 2 could not evaluate" | 0 |
| 38 | `head -22 kake-shokunin/scripts/canonical_audit.py`, `head -16 kake-shokunin/scripts/freshness-sweep.mjs`, `grep -n 'process.exit\|unreadable'` | freshness-sweep §paths re-checks every cited FS path in SKILL.md + `corpus/**/*.md` vs live FS; "Exit contract: 0 = clean · 1 = drift · 2 = unreadable/invalid input · 64 = usage error" | 0 |
| 39 | `grep -rn 'round42-selfdesc\|round65-host-census\|HOST_CENSUS\|REFUSED_MEMBER' --include='*.md' --include='*.py' --include='*.sh' --include='*.mjs' . \| grep -v '^./kama-shokunin/' \| head -20` | only fleet-level `.ufo/l0-questions.md:236`, `.ufo/prompts/kama-round-6{6,7,8,9}.md:132`, `.ufo/reports/round-*/kama.md`; **0 sibling-lane hits** | 0 |
| 40 | `grep -rln 'PROVINCE' kama-shokunin/tools/*.py` | six tools read PROVINCE: kama-completion-live, round42-selfdesc-reconcile, round53/54-cited-path-check, round65-province-host-audit, round67-worktree-landing-check | 0 |
| 41 | `git -C kama-shokunin status --porcelain` | ` M PROVINCE.md`, ` M SCORECARD.md`, `?? .ufo/waves/round-70/w1.ready`, `?? .ufo/waves/round-70/w1.ready.dispatched`, `?? .ufo/waves/round-70/w1/out/` — the two modified tracked files are the L1's concurrent round-70 record repair, not this seat; my writes are only under `w1/out/` | 0 |
| 42 | `git -C kama-shokunin diff --stat -- PROVINCE.md SCORECARD.md` | `PROVINCE.md \| 2 +-` (one line), `SCORECARD.md \| 23 ++++++++++++++++++-----` | 0 |
| 43 | Python: compare `git show HEAD:PROVINCE.md` line 17 with the worktree line 17 | HEAD len **1625** ends `... compare every check; round 47) \|`; worktree len **2086** ends `... fail-closed on an undated one; round 69) \|`; the L1's repair appends round-67/68/69 instrument entries to the Owns row | 0 |
| 44 | Python: token count on the worktree row 17 | `round42` 0, `selfdesc` 0, `round65` 0, `host-census` 0, `round70` 0; row length 2086; tail verbatim as quoted below | 0 |
| 45 | `grep -c 'round42' PROVINCE.md`; `grep -c 'round-42' PROVINCE.md`; `grep -cF '<anchor>' PROVINCE.md`; `grep -c 'round69-newest-closure-counter' PROVINCE.md` | `0`, `1`, `1`, `1` — the "no round42 token" claim holds and the edit anchor is unique | 0 |
| 46 | `head -22 tabi-shokunin/scripts/check-freshness.mjs`; `grep -n 'process.exit\|exitCode'` | pinned expected path `.ufo/rounds/fleet-round-1-interactive-20261015/freshness.expected.json`, pin table `corpus/evidence/fleet-round-1-freshness/pins.tsv`, three declared public targets, `fail(finding, detail, exit = 1)`; exit assigned once at line 218 | 0 |
| 47 | `head -26 kumitate-shokunin/scripts/cap-run.mjs`; `head -16 mori-shokunin/tools/mori-gate-registry.py` | cap-run = sandboxed child runner (cgroup cap, PID namespace), not a reconciler; mori-gate-registry = audits the lane's stated gate standard (eight-cell tables, entry path resolves, real `--selftest` branch) | 0 |
| 48 | `rm -rf /fast/scratch/hyaku/kama-r70/CON01Siblings` and `test -e` | scratch removed (`SCRATCH_REMOVED`) | 0 |

Failure recorded, not hidden: command 14 was my own parser assumption and exited 1; it
was corrected in commands 15-16 by locating the canonical table via its exact header row.
No lane or sibling byte was touched by that failure (it only read `SCORECARD.md`).

## Exact bytes the L1 must land (clause 1 of the proposed move)

File: `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md`, the Owns instruments row
(line 17 today). **Re-read the row immediately before editing**: the L1's concurrent
round-70 repair is editing that same cell (HEAD's row is 1625 chars and ends at round 47;
the worktree row is 2086 chars and ends at round 69). The anchor below is the post-repair
cell text, verified unique in the worktree (`grep -cF` → 1). It currently ends:

```
… `tools/round69-newest-closure-counter.py` (the newest non-author closure, fail-closed on an undated one; round 69) |
```

Replace that final `" |"` with the following, keeping the row on one line:

```
, `tools/round42-selfdesc-reconcile.py` (the lane's self-description reconciles with the measured tip: SCORECARD head, axes, planned, retired, saturation, capabilities, receipts, README and PROVINCE; round 42), `tools/round65-host-census.py` (tier-A/B census of the lane's registered self-tests with refusals recorded; round 65) |
```

That is the only byte-level change proposed. It adds no SCORECARD row, claims no
capability, and changes no counter. Exact-match anchor for the edit tool: the substring
`` `tools/round69-newest-closure-counter.py` (the newest non-author closure, fail-closed on an undated one; round 69) | `` is unique in PROVINCE.md (verified by the row tail above).

Clause 2 is an implementation constraint for C2, not a file patch:
`tools/round65-host-census.py` must derive its exit from one `not_evaluated` tally that
both the refusal-marker path (line 129) and the `subprocess.TimeoutExpired` path
(line 143) increment, and the verdict line's `not_evaluated=` must print that same
tally. Today both increment `refused` while `main()` ends `return 0 if failed == 0 else 1`
(line 158), which is the fail-open; the frozen control exercises only the refusal route.

## What I could NOT verify

- No sibling instrument was executed. Every sibling exit semantic above is read from
  docstrings and code paths in the working tree, not from an observed run. I did not run
  any sibling selftest, census or gate.
- No git history of any sibling was read; "what it does" is the working tree's own
  description plus the code path that computes the verdict.
- kama's base reconciler reading (`mismatches=10`, `province=4`, exit 1) was not re-run;
  it is quoted from the frozen `freeze.txt`. Consequently the four failing `province`
  facts are not enumerated here.
- The census's real-run green line (`pass=22 fail=0 not_evaluated=0`) is the freeze's
  target, not something I observed; I imported the module only to count `MEMBERS` (22)
  and confirm the tier-A reconciler arm.
- Whether adding two names to `PROVINCE.md:17` perturbs any other counter was not
  measured: the six PROVINCE-reading tools (command 40) were identified, not run. The
  risk is confined to citation/path checks whose targets (`tools/round42-selfdesc-reconcile.py`,
  `tools/round65-host-census.py`) exist at the tip, and to the round-65 province host
  audit's surface list, which does not enumerate Owns-row cells.
- I did not inspect whether a sibling's PROVINCE.md explicitly refuses "self-description
  reconciliation" as its domain; I read the Owns/Refuses lines of ten lanes (souji,
  tsukuroi, mori, mado, chousa, kotodama, kaidoku, kumitate, tameshi, kengaku) and found
  no such refusal.

## Scratch

`/fast/scratch/hyaku/kama-r70/CON01Siblings/` created for this seat; no fixture, clone or
temp tree was needed. Removed before yield; `test -e` after removal prints nothing.
Nothing was written under `/tmp`, to `~/.local/bin`, or to any path on PATH. No tool was
installed or upgraded this run, so there is no install record to carry.
