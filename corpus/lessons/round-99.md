# Round 99 — the population the control ran, the records that did not match, and an unread flag that is not "off"

Lane `kama`, round 99, L1 `KamaR99`. Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978` (round 98 closed
`ok`: C1 calibration, C2 operability, C3 depth all verified at `160e22dd`; expansion unchanged,
quality/discernment improved — `corpus/lessons/round-98-verifier-spotcheck.md`). Claims: C1
operability (the budget counter's control mode refuses a population it did not run), C2 calibration
(the lane's round-98 records agree with the committed wave evidence), C3 depth (an unread `/props`
autoload flag reads `router-autoload-unread`, not `router-unloaded`).

## Gate

Every row below was opened this round (2026-11-08); the digest is of the bytes fetched by `curl` in
this round, recorded in `.ufo/waves/round-99/sources/`.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S624 llama.cpp `tools/server/server-models.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.cpp — 2026-11-08, sha256 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` (111 675 B), HTTP 200 | `{"models_autoload",      params.models_autoload},` (line 2030, inside `get_router_props` lines 2021-2046) | The bare `/props` body the probe reads is built from the server's own `params.models_autoload`; the field is the configured state, not a request echo. |
| S625 llama.cpp `common/common.h` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h — 2026-11-08, sha256 `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` (58 830 B), HTTP 200 | `bool models_autoload = true;` (line 705; trailing comment: automatically load models when requested via the router server) | Autoload defaults to true, so an autoload-off router is an explicit `--no-models-autoload` state; an unread answer is never evidence of it. |
| S626 llama.cpp `tools/server/README.md` @ b12177 | **reject** (C, docs lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md — 2026-11-08, sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` (136 429 B), HTTP 200 | `--models-autoload, --no-models-autoload` — for router server, whether to automatically load models (default: enabled) (line 234) | Names the launch flag and its default, not the `/props` JSON field the probe reads; flip: a docs section names `models_autoload` in the props body. |
| S627 llama.cpp `common/arg.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/arg.cpp — 2026-11-08, sha256 `c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67` (224 666 B), HTTP 200 | `params.models_autoload = value;` (line 3682; the `--models-autoload`/`--no-models-autoload` option callback, env `LLAMA_ARG_MODELS_AUTOLOAD`) | The option callback is the only writer of the field the props body reports, so an "off" answer is exactly a configured launch/environment state. |
| S628 llama.cpp `tests/unit/test_router.py` @ b12177 | **reject** (C, code lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tests/unit/test_router.py — 2026-11-08, HTTP **404**, 14-byte `404: Not Found` body, sha256 `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` | No located quote: the path does not exist at the pinned tag. | A seat-reported line-23 assertion cannot be re-opened, so it is not evidence (SC02's claim failed re-opening); flip: the file exists at b12177 and line 23 carries that assertion. |

Registry changes: S624, S625 and S627 admitted (used-by `SKILL.md`, `corpus/knowledge/router-props-autoload.md`),
S626 and S628 rejected rows; no existing row's status/recheck/used-by changed. Census before → after: 363 → 368
rows (`A 345→348`, `B 11`, `C 7→9`; `mined 325→328`, `queued 8`, `rejected 30→32`), validate exit 0
at round start (`controls/census-start.out`, exit token in `controls/census-start-amended.out`) and at round
end (`controls/census-end.out`).

Assimilation: none from `merge/kama/` (the package holds no `/props` autoload theme). `considerthese/2026-11-08.md`
proposal 2 (a counter-requires-its-own-claim scan) is mined as a pre-freeze scan over the three new
counters; the receipt is `controls/counter-literal-scan.out` and the shape it flags is disclosed as
C2 limit (c).

## Mistakes

**M1 — the round-98 wave accounting was written from a directory scan, not from `w1-results.json`.**
Class: `sampling`. Evidence: `corpus/lessons/round-98.md` M3 records that `RV03Intent` and
`EX02BudgetControl` settled inside the same wave; `SCORECARD.md:6431` and `LOG.md:4040` still said
"10 reported, 2 dead" and the LOG credited a "SB01-equivalent" seat that does not exist. Captured-by:
the round-98 non-author spot-check (routed defect 1), not any lane counter — no counter read the wave
accounting against the results file. Fix: the round-99 corrections in `SCORECARD.md` and `LOG.md`
state **12 reported, 0 dead**, the derived **7 attack / 5 non-attack** split naming `EX02BudgetControl`
and `RV03Intent`, re-derived by `tools/round99-record-audit.py` (C2). Shown able to fail: the same
counter prints `mismatches=10` at base (`controls/c2-base.out`) and 0 after the corrections at M2.

**M2 — the round-98 lesson labelled the base census numbers as HEAD.** Class: `labelling`. Evidence:
`corpus/lessons/round-98.md:28` says "tiers measured with the census at HEAD" and quotes the r98
**base** `681c80a4` → 361 rows (A 344, B 11, C 6; mined 324, queued 8, rejected 29); the r98
**tip** `649bb2e9` → 363 rows (A 345, B 11, C 7; mined 325, queued 8, rejected 30). Captured-by: the
round-98 spot-check's row-count cross-check. Fix: this lesson states the two groups with their
revisions, and `tools/round99-record-audit.py` checks 7–8 re-derive both from `git show <rev>:corpus/SOURCES.md`
with the frozen census generator. The r98 lesson bytes are not rewritten (append-only history).

**M3 — the carried round-98 M3 record sat outside that lesson's `## Mistakes` section.** Class:
`sampling`. Evidence: `corpus/lessons/round-98.md` places "M3 — a wave-dir scan that reads only
`out/<Name>/` inferred two live seats were dead" after `## Spot-check`, so a reader scanning `## Mistakes`
missed the record that contradicts the wave accounting. Captured-by: the round-98 spot-check
(routed defect 4). Fix: the record is carried here, inside `## Mistakes` (this row); the r98 file keeps
its bytes.

**M4 — the freeze instruments were narrower than all three claims' wording, and the round's own wave
found it before any measurement.** Class: `vacuous` (a green counter on a narrower property).
Evidence: `w1/CR01Records.md` (eight meaning-changing record forgeries pass the frozen C2 bytes),
`w1/EX02Records.md` §3.2 (twelve named forgeries; B2/C2/D/D2/G/H/K/L/M/N/J/V/O escape),
`w1/RV01Wording.md` F1–F4 (C3's exit code, role isolation, absent field and non-boolean field are
stated but ungraded; a truthiness mutant grades `"false"` as `MODEL_OK`), `w1/RV02Counter.md` rows
4/5/7/9/10 (C1's count guard accepts same-count substitutions and a vacuous selection),
`w1/SC01Recon.md` receipt 10 (the candidate's call shape breaks `set -e` on the plain-call
subcommands). Captured-by: the wave's attack seats, not the freeze counters. Fix: amendment 1
re-freezes the three hardened instruments, narrows each claim to what its instrument enforces, adds
C3 cells U5–U7 plus exit grading, and lands the probe call-shape fix. Shown able to fail: the
hardened counters' base controls (`controls/c2-base.out` 10 mismatches; `controls/c3-base.out` 7
mismatches), the twelve-forge matrix (`controls/c2-forge-matrix.out`), the grader-level negative arm
(`controls/c1-grader-base.out`), and the plain-call regression control (`controls/c3-plaincall.out`).

**M5 — a burner-raising counter run under a 900 s job timeout leaked 64 load burners.** Class:
`resource`. Evidence: `controls/regression-timeout-reap.out` — the job was killed with the counter's
`finally: stop_burners` never run, leaving 64 `while True: pass` processes at PPID 1487 and load1 at
94; reaped by exact PID. Captured-by: nothing in the lane's gates (the leak is outside every counter);
detected by the L1's post-timeout `ps` check. Fix: never wrap a burner-raising counter in a tool/job
timeout; run it with no deadline and verify `ps -eo args | grep -c '[w]hile True: pass'` → 0 after.

**M6 — two wave seats ran the round-98 budget counter's load leg concurrently, and the 128 burners
host-deferred the fleet.** Class: `resource`/`sampling`. Evidence: `ps` at 12:36 showed 128
`while True: pass` children of SC01Recon/SB01Entry's counter runs and load1 168 against the
dispatcher's `LOAD_MAX` 144; the seats had been asked for derivations, not a regression. Captured-by:
the host gate and the dispatcher log, not the wave briefs. Fix: a wave brief must forbid
burner-raising counters unless the L1 budgets one at a time; a seat that starts one owns its reaper
on every exit path.


## Measurements at `00394f3b` (amendment 1)

- C1: `CONTROL_POP99 … selected=6 ran=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_exit=0
  positive_ok=1 complete=1 mutant_cell_lines=5 positive_cell_lines=6 population_shaped=1 met=True`
  exit 0 (`measured/c1.out`); the round-98 counter accepts the same drop (exit 0,
  `controls/c1-before.out`), the hardened counter refuses it with the id sets (exit 1,
  `controls/c1-candidate-mutant.out`), the unmodified counter accepts six cells (exit 0,
  `controls/c1-positive.out`), and the grader-level negative arm prints `refused=0 … met=False`
  (exit 1, `controls/c1-grader-base.out`).
- C2: `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=00394f3b` exit 0 (`measured/c2.out`); base
  `mismatches=10` (exit 1, `controls/c2-base.out`); 14 of 15 forged variants are caught
  (`controls/c2-forge-matrix.out`; J's negated arm sentence escapes as disclosed), and the `--rev`
  clone replay catches the forged M2 with no frozen byte edited (`controls/c2-forged-rev.out`).
- C3: `AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True` exit 0
  (`measured/c3.out`); base `mismatches=7` (exit 1, `controls/c3-base.out`); the plain-call control
  is green for on/off/non-router (`controls/c3-plaincall.out`) and the verdict matrix is 77/77
  (`controls/c3-harness.out`).
- The round-98 19-cell budget regression at `00394f3b` is `controls/c3-regression.out`; it runs with
  `--burners 0` (a plain second pass) so the vocabulary change is graded on cell expectations
  without repeating M5/M6's host harm.

## Routed-defect answers

- **Round-98 spot-check defects 1–4 and 6** (stale wave counts, seat accounting, census mislabel, M3
  placement, under-enumerated gate disclosure) — answered by C2's corrections and this lesson; checks 1–11
  of `tools/round99-record-audit.py` grade them.
- **Defect 5** (M2's red-before receipt and the counter-level `n != len(selected)` fix) — answered by C1:
  `controls/c1-before.out` is the round-98 acceptance of the dropped-cell mutation (exit 0) and
  `controls/c1-candidate-mutant.out` is the successor's refusal (exit 1).
- **Wave-1 findings (amendment 1):** C1's count guard failed on identity and on a vacuous
  selection (RV02/EX01/MT01); C2's freeze bytes passed eight meaning-changing record mutations and
  could not run its own `--tree` forge (CR01/EX02/SC01); C3 left the exit, role, absent-field and
  non-boolean clauses ungraded and the candidate's call shape broke `set -e` on the plain-call
  subcommands (RV01/MT01/SC01/SN01); a new reason row under the frozen reason-codes table could not
  bind (CN01). Each is answered in `plans/round-99-amendment-1.md` and the ledger.
- **Defect 7, carried unchanged:** the slow `/props` **verdict** stays fail-closed `MODEL_UNLOADED`
  (C3 changes only the reason vocabulary); `round75-instruments` `bad_rows=19` (L0 r87/r89 still open);
  `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080; the pass-level
  wall-clock wrapper (SC01); the ctime memo shape; the C1 checks 13–14 receipt-needle limit; the frozen
  `--control` count check (now fixed by C1 for the population count). Also carried: the round-90
  `reason-rows` receipt is stale at base (`REASON_ROWS … bound=0 unbound=24 receipt=stale`, exit 1), so
  the reason table C3 edits was already unbound before this round; a re-capture bound to the round-99
  probe is routed to round 100, not claimed here.
