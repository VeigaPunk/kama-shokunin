VERDICT: partial — "before (frozen check.py + pair) → after (current check.py + pair + fault controls)" changes the subject and the detector together, so it is two different tests, not one test with two settings; publish the 2×2 and headline the two within-axis deltas.

## Answer to the question

No, the diagonal is not a fair before→after for a calibration claim. Three things change at once:

- **S** — the gate bytes: the frozen copy is `b853576e…` (`.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`); the repair landed *during* this review and is still changing (`dadc777e…` onward);
- **D** — the detector (`pair only` → `pair + fault controls`);
- **M** — the *applicable* mutant population (the round-16 mutants number six applicable on the frozen file; `served_model`/route-match mutants have no before-applicable target at all).

The confound is not merely statistical. The fault-control oracle is **positive** ("the gate must fail this corrupt row"), so for the two new fields it is *defined only on a gate that grades them*. Run unmutated on the frozen gate, those controls are red by design — the before-cell of D1 does not exist. The diagonal therefore compares a D0-only before against a D0∪D1 after, over different denominators, and no reviewer can tell whether the improvement came from the new conjuncts or from the new probes.

There is a second, sharper point: **the pair cannot be made to kill these mutants at all.** Its oracle is the pristine grader's own per-row output, so deleting a conjunct that no row currently violates cannot change any `passed` value. Round-16 measured exactly that: reason mismatches 17→0, exit mismatches 0→0, drift mismatches 0→0, timeouts 0 (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/MutateHarness.md`, "Ignoring exit or drift removed comparisons that rejected no observed row in either probe version."). The 0/5 is a property of the 72-row corpus, not of the gate's weakness. Adding probes cannot fix it; only a detector that supplies a *violating* input can. That is what the fault controls are — so C1's claim is honestly a **detector-coverage** claim plus a **new-invariant liveness** claim, not a "the gate stopped overclaiming" claim.

`check.py:340-347` is the whole graded surface, and the quote is the entire conjunction:
`record["passed"] = (` / `and record["reason"] == expected["reason"]` / `and record["probe_exit"] == expected["exit"]` / `and record["drift"] == (record["verdict"] != "MODEL_OK")`.

## The cleanest pair of numbers

Hold the population fixed as a *behaviourally* defined set of nine, then change one variable per axis.

| subject \ detector | D0 = pair only | D0 ∪ D1 = pair + fault controls |
|---|---|---|
| frozen gate (`b853576e`) | G6: 0/6 killed — **measured**, `.ufo/waves/round-17/build/advice/MutBaselineCheckPy.md` | G6: 0/6 killed (D1 restricted to the five graded behaviours; N3 n/a) |
| repaired gate (working tree) | G6∪N3: 0/9 (must be **re-measured**) | G6∪N3: 9/9 killed (prediction) |

G6 = `ignore-reason`, `ignore-exit`, `ignore-drift`, `casefold-verdict`, `timeout-pass`, `delete-no-requests` — the six applicable to the frozen gate, already measured at 0 killed / 6 applicable / 0 inconclusive. N3 = `ignore-served-model`, `ignore-route-match`, `malformed-to-traceback` — inapplicable to the frozen gate.

**Headline pair 1 — detector recall, gate fixed at the repaired bytes:**
`killed 0/9 → 9/9` on the identical gate. This is the number that supports "the detector now detects what it claims". It deliberately does *not* reuse the measured 0/6, because that is a different subject.

**Headline pair 2 — gate coverage, detector fixed at D0∪D1:**
`killed 0/6 → 6/6` on G6 (N3 reported as **n/a**, never as survived). This is the number that supports "the repair removed the overclaim" without letting the new probe suite take the credit.

**Headline triple 3 — new-invariant liveness, no mutants at all:**
the *pristine* repaired gate must fail every new-invariant fault: 3/3 `served_model` faults, 1/1 route-match fault, 1/1 malformed-row fault. The frozen gate fails only the faults its four conjuncts cover and 0 of the 3 new ones. This is the only number that proves the repair itself, independent of mutation survival.

**Equivalence warning for the after column.** `delete-no-requests` is *equivalent on the repaired gate*: with `route_ok` graded, a probe that reaches no stub yields `route_ok is False` and fails regardless of the guard, so removing the guard changes no observable. Count it as equivalent-with-proof after, not as a survivor (false alarm) and not as a kill (false credit); it also means the guard is now dead weight subsumed by the route invariant.

Do **not** report "6 survived → 0 survived" as a single delta, and do not print the diagonal as a mutation score.

Scoring discipline, so the denominators are auditable:
- `killed / applicable`, with non-applicable and `no-coverage` reported as separate columns (PIT vocabulary: "**No coverage** is the same as **Survived** except there were no tests that exercised the line of code", `https://pitest.org/quickstart/basic_concepts/`; a mutant whose target code does not exist in the frozen gate is *non-viable*, not survived).
- Per-cell test strength `killed/(killed+survived)`, stated once with the formula, never an unlabelled `55/17`.

## Controls L1 must also report

- **C0 — detector preflight.** D1 on the pristine repaired gate: every control satisfied, identity wrapper probe = 72 passes / 0 failures / exit 0, `--selftest` all entries rejected (4 malformed + the duplicate-name check). A red D1 preflight makes every "after" number meaningless.
- **C1 — four-cell baseline, re-derived in-run.** `{frozen, repaired}` × `{probe 93ee4302…, probe 36b64978…}`, each with row counts, exit, and `probe_sha256` from the receipt (round-16 already records it: `run-before.json` = `93ee4302…`, `run-after.json` = `36b64978…`). Do not hard-code 55/17 or 72/0; the frozen probe × repaired gate cell is unmeasured and may legitimately move if `served_model`/route-match grading finds a pre-fix defect.
- **C2 — fault non-vacuity.** For each fault: the exact corrupted observable, the one target row, the expected failing row set, and a column "already killed by pre-repair code?" — the four traps in F4 must be avoided or the control proves nothing. Assert **exactly one row flips** (blast radius), not merely "the faulted row fails".
- **C3 — mutant integrity.** Content anchor with exactly-one-match assertion, `python3 -m py_compile` on each mutant, declared post-mutation sha256, and restore to the pristine sha. No line-number patching.
- **C4 — kill attribution.** Per mutant: which detector killed it, on which row, and how many rows changed `passed`. A kill with >1 changed row is collateral and must be re-attributed.
- **C5 — constraint self-check.** `fault-controls.py` recomputes round-16's pin formula (`files = sorted((CHECK.parent).glob("*.json"))`, `EXPECTED_MATRIX_SHA256 = "bf9068d8…"`, `.ufo/waves/round-16/measure.py:281-290`) and fails closed on `9` files / digest mismatch; wraps probes as **bash** (see F8); records each wrapper's `probe_sha256`.
- **C6 — determinism.** D1 twice, identical verdict vector; all stubs bind `127.0.0.1:0` only; `ss -ltnp` clean afterwards.
- **C7 — cost.** Wall clock total and the timeout control's share (≥30 s per subject, `check.py:50`); name the sparse cells if the full 9×9 cross product is not run.
- **C8 — n/a ledger.** Which mutants are inapplicable to which subject and why (no such grading exists in the frozen gate).

## Findings

Line references F1–F12 are to the frozen pre-repair gate `b853576e…` (`.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`), which is the only stable artifact; the live working-tree file was being rewritten during this review and is reviewed separately below.

**F1 — high — the diagonal is confounded; the before-cell of D1 does not exist.** `tests/probe-verdicts/check.py:340-347` is the graded conjunction; `:337-338` records `served_model` from the probe row, and `:347` closes `passed` without it. A suite whose oracle is "the gate must reject this corruption" cannot be run as a detector on a gate that claims nothing about the corrupted field.

**F2 — high — aggregating n/a as "survived" inflates the before number; excluding it silently changes the denominator.** The ticket's mutant set is the round-16 mutants plus (implicitly) new ones; the two new fields have no frozen-gate equivalent. Report `0/6 applicable, 3 n/a` — never `0/9`.

**F3 — high — the pair is structurally unable to kill conjunct-removal mutants, so re-running it under a repaired gate will also find 6/6 survivors.** Evidence: `MutateHarness.md` table (exit mismatches 0, drift mismatches 0) and its own conclusion, "Result: survived 5; killed 0; inconclusive 0." Hence headline pair 1 must be measured, not assumed, and the D0 column must be reported (it is the *control* that shows the pair is still blind).

**F4 — high — four fault variants are pre-killed by existing code and would certify nothing.**
- *route-match*: `check.py:323` `if server is not None and not record["requests"]:` already fails a probe that never reached the stub, so a "no requests at all" fault is caught by old code. The fault must keep `requests` non-empty but wrong-path (e.g. `GET /health` plus a fabricated row) — that is the only case the new invariant adds.
- *malformed output*: `check.py:329-332` already catches invalid JSON, missing `rows`, and `rows: []` (`IndexError`). Only a **non-object row** reaches `row.get(key)` at `:338` and raises `AttributeError`, which is absent from the except tuple at `:332` → traceback. `rows: []` and invalid JSON must not be counted as evidence of the repair; use `{"rows": ["not-an-object"]}`.
- *verdict case*: on a MODEL_OK row the unchanged drift conjunct already rejects a lowercase verdict — `false == ("model_ok" != "MODEL_OK")` is False — so that control is pre-killed by the frozen gate and certifies nothing about the casefold repair. Target a **non**-MODEL_OK row instead (`AuthAndDead.closed-port-connection-refused` → `dead`, `ForeignControls.not-found-json` → `foreign_service`, `LoadingEnvelope.canonical-alias` → `model_loading`), where drift is `true` on both sides and only the strict verdict equality rejects the corruption.
- *served_model*: only 11/72 rows carry a non-`-` id, and exactly one row grades join order — `ReadyControls.second-data-id-match`, ids `['kama-ready','tiny-vocab']` → `kama-ready,tiny-vocab`. A single-id fault leaves order/join defects undetected; add a swap-order fault and a "reports an id where the row must report `-`" fault.

**F5 — medium-high — exit 1 cannot distinguish a graded failure from a harness crash.** `check.py:493` `code = 0 if doc["failures"] == 0 else 1`, and an uncaught `AttributeError` also exits 1 — but prints **no JSON document at all**. A control implemented as `returncode != 0` is therefore vacuous for the malformed case. Require: parseable JSON, `tests` equal to the expected row count, the faulted row `passed is False` with a non-null `error` (or the named mismatched field), and no `Traceback` on stderr.

**F6 — medium — line-addressed mutants are unsafe against a repaired file.** The round-16 mutants are written as e.g. "delete original line 342" (`MutateHarness.md` table). After the repair shifts lines, a line patch deletes a different expression and fabricates a kill; a mutant that fails `py_compile` is also killed trivially. Anchor on the exact expression text with a single-match assertion.

**F7 — medium — baselines must be derived per subject, not carried.** Round-16's `72/0` is on probe `36b64978…` (the current bytes), so it is portable; the `55/17` is on `93ee4302…` under the *frozen* gate. Under the repaired gate the frozen cell is unmeasured. `measure.py:382-383` correctly pins only breadth (`EXPECTED_TESTS = 72`, `EXPECTED_LOADING = 17`), not pass counts — keep that split and add pass counts to the re-derived baseline instead.

**F8 — medium — the HARD CONSTRAINT needs an in-suite verifier, and wrappers must be bash.** `measure.py:287` globs `*.json` non-recursively, so a `faults/` subdirectory of JSON fixtures would escape the pin — a pin hole, not a solution. Generate fixtures in-suite or in a temp dir, and assert `9` files + `bf9068d8…`. Also `check.py:273-275` invokes `argv = ["bash", str(probe), *PROBE_ARGV_TAIL[:1],` — a `.py` wrapper is passed to bash and cannot work.

**F9 — medium — provenance and blast radius.** `check.py:486` records `probe_sha256`; assert each wrapper's sha differs from `36b64978…` so the run proves the wrapper was used, and assert that exactly one row changed `passed`.

**F10 — low — cost.** `check.py:50` `PROBE_TIMEOUT = 30`; the timeout fault costs 30 s per subject. Either declare the sparse matrix (`timeout` fault × {pristine, `timeout-pass`}) or budget ~5 min for nine mutated subjects plus pristine.

**F11 — medium — the `served_model` derivation must be total, or the new invariant is only accidentally right.** The probe's rule is the first non-empty group among `data[].id`, `models[].id`, `models[].name`, `models[].model`, `doc.id`, deduped, joined with `,`, else `-` (`tools/kama-probe.sh:357-367`, `:526-529`). `check.py` must reproduce that precedence over the stub's body — parsing `body_json` **and** `body_text` (the probe parses the body file regardless of content type, `:401-424`), otherwise a future `body_text` row containing an array would derive `-` and grade a correct probe as wrong. Currently 11 rows are non-`-` (`LoadingRace.InverseHealthLoadingModelsOk`, `.InverseWildcardExpect`, `.InverseHealthLoadingIdMismatch`, and all eight `ReadyControls.*`), which is the exact expected-value table for the fault controls.

**F12 — low — `--only` is the right targeting mechanism and is already available.** `check.py:442-444` `parser.add_argument("--only", action="append", default=[], metavar="NAME",` plus `:468-476` filtering and a hard error on unknown names, so each fault can be a one-row run without a second fixture set. Note the JSON doc's `tests` becomes 1; controls must not assume 72.

## Landed implementation snapshot (live file; `dadc777e…` → `32be75de…`, 12:22–12:34)

The repair landed while this review ran and the file changed at least five times. One blocker persists in every snapshot I read (`dadc777e…`, `e3eb484e…`, `d8f07c53…`, `32be75de…`); two defects seen in an earlier snapshot were closed in flight and are recorded only so they are not re-reported. The matrix pin is intact throughout: 9 files, set digest `bf9068d8…`.

**L1 — blocker, still present at `32be75de…`: the module does not import.** `check.py:46` `CHECK_DIR = Path(__file__).resolve().parent` and `:533` `tmp_path = Path(tmp)` both use `Path`, but `from pathlib import Path` is absent from the import block (`:34-44`). Observed on every snapshot: `NameError: name 'Path' is not defined` on `exec_module`. Every gate run in this state dies on a traceback, so the "after" column is unmeasurable and any receipt written now is void. Restore the import before any measurement.

**L2 — closed in flight (present at `dadc777e…`).** An unreachable duplicate of the old parse plus the old four-conjunct `passed` sat after `return record`; at `e3eb484e…` the grader ends at `:474` and `except OSError` follows directly.

**L3 — wired as designed (verify once, then stop reading it).** `:444` records the stub's requests per row; `:451-456` turns malformed probe output into a recorded `error`, never a raise; `:459-472` grades `served_model_ok` and `route_ok is not False`, with `route_ok` initialized to `None` at `:409` so closed-port "not applicable" cannot be confused with "field absent". `expected_served_model` is keyed on the observed verdict at `:460`; keep it, but not as the casefold rationale (F4).

**L4 — closed in flight (present at `dadc777e…`).** `--selftest` now really exercises the duplicate-name guard (`:508-545`, in a temp dir, never the matrix dir), matching its docstring at `:29-31`; `tempfile` and `load_matrix(directory=…)` are now used instead of being dead surface.

**L5 — low — the selftest's reported count no longer matches its name.** `:547` `"malformed_tests": len(results)` now counts five entries (four malformed tests plus the duplicate-name check), while `:29-30` still says "4 embedded malformed tests". A receipt reader cannot tell what `5/5` measures. Report `malformed_tests: len(SELFTEST_MALFORMED)` and a separate `duplicate_name_checked: true`, or rename the field.

## Limitations

- Read-only design review: I ran no harness, matrix, mutant runner, control suite, or lane gate. Every claim above is static reading of the cited lines.
- `9/9 killed` and `6/6 killed` are predictions from the fault design, not measurements; if any survives, that survivor *is* the round's finding.
- [INFERENCE] the repaired gate leaves the frozen probe's 55/17 unchanged (the frozen probe emits `served_model` at `.ufo/waves/round-16/frozen/kama-probe-before.sh:806` and fetches `/v1/models` at `:418`). This must be measured as control C1, not assumed.
- The measured before-cell (0/6 applicable, 3 n/a, 0 killed) is `.ufo/waves/round-17/build/advice/MutBaselineCheckPy.md`, a separate seat's scratch-only run against the frozen bytes; I did not reproduce it.
- The 11-row served_model table and the 1 closed-port row exclusion were derived by static extraction over the nine matrices (72 rows: 71 stub, 1 closed); no row was executed.

## Installs

None.
