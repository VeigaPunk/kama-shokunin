# FindingExit — outer `test_failed`/1 vs child findings vs marker evidence

Seat: `KamaR15.FindingExit-3` (connector, leaf). Root: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Read-only apart from this report. I ran no runner, harness, classifier, test, build, linter or smoke run.
Bytes read: `tests/ollama-corpus-guard/check.py` at tag `#9540` (732 lines; an earlier `#3FBD` was
superseded mid-read), `.ufo/waves/round-14/measure.py` `#6643` (repaired), `.ufo/waves/round-15/frozen/measure-before.py`,
`tools/kama-ollama-evidence.py`, `PROVINCE.md`, `corpus/QUALITY.md` (KQ1–KQ18), `corpus/lessons/round-14-verifier-spotcheck.md`
(latest verifier), `corpus/lessons/round-15.md`, `SKILL.md:463-505`, and the landed round-15 advice.
Tools installed/updated: none (pacman paused host-wide per operator ruling; nothing needed).

## Axes

- **C1 calibration (declared, lowest 7):** red/green must be admitted from evidence attributed to the right layer, never from one outer finding or exit.
- **Operability (8, must not regress):** valid unique-corpus measurement keeps passing; no predicate change that could break the predicted green.
- **Boundary (PROVINCE / KQ1, KQ4, KQ13, KQ17):** no layer's exit 0 is served-model identity, liveness or readiness.

## Evidence: three nested CLIs, three meanings per exit code

| Layer | Bytes | Finding field | 0 | 1 | 2 |
|---|---|---|---|---|---|
| Harness `check.py` | `:632-675` | `finding_id` | `clean`: ≥1 record, all passed | `test_failed`: any failed record **or** `error_document` (HarnessError/unexpected exception: matrix absent/invalid/empty, runner or classifier absent, `--only` no match, no exit-0 template) | — |
| Runner `measure.py` (harness child) | `:367-425,477-489` | none; free-text `error` only | all fixtures passed | any fixture failed, corpus problem, tool absent, MeasureError, exception | — |
| Classifier via wrapper (harness grandchild) | `tools/kama-ollama-evidence.py:91-98` | `finding_id` | `loaded_same_digest` | `available_not_loaded`, `remote_inventory`, `identity_conflict` | `unknown`, `invalid_input` |

Every guard corpus clones `tests/ollama-evidence/cases.json:2-17` (`loaded_same_digest`, exit 0), the first `expected_exit == 0` fixture (`check.py:226-251`).

### Per-record signatures [INFERENCE from code; nothing executed]

N = `len(names)`; D = distinct stripped names (≥16 by `check.py:189-197`; D < N for rejected rows, `:198-203`).

| Run | Row | Harness record | Runner exit / `verdict_exit` / `error` | Runner records | Classifier results | `classifier_invocations` (marker) | audit Popen / all events |
|---|---|---|---|---|---|---|---|
| frozen | rejected | fails | 0 / 0 / absent | N measured | N × `loaded_same_digest`/0 | N | N / ≥N |
| frozen | valid | passes | 0 / 0 / absent | N measured | N × `loaded_same_digest`/0 | N | N |
| repaired | rejected | passes | 1 / 1 / `corpus: duplicate case names` | N unmeasured, `observed_exit` null | none | 0 | 0 / 0 |
| repaired | valid | passes | 0 / 0 / absent | N measured | N × `loaded_same_digest`/0 | N | N |
| any | could-not-evaluate | no records | n/a | n/a | n/a | n/a | n/a (outer `test_failed`/1, `error` set, `total` 0) |

## Connections and contradictions

1. **Exit codes run opposite across layers on the rejected rows.** The frozen red's outer `test_failed`/1 happens *because* the runner child returned 0 and every grandchild returned `loaded_same_digest`/0. The repaired green's outer `clean`/0 depends on runner exit 1 with zero grandchildren. So rolling exits up ("all zero = good"), or reading the harness's 1 as the classifier's "failed captured policy" or the runner's 1 as "duplicate rejection", reverses or overstates the result. `SKILL.md:463-466` ("Do not transfer exit meanings across tools") applies to this third tool too.
2. **`test_failed` puts two classes under one ID.** A measured contract failure and a could-not-evaluate `error_document` share both ID and exit. The only way to tell them apart is `error` present plus `total: 0` plus `records: []` (`check.py:656-675`). By analogy with KQ16 (`QUALITY.md:61`: distinct IDs even when exits are shared; rejects collapsing `snapshot_tampered`/`source_unavailable`) and KQ17 (`:72`: outer finding kept separate from subfindings), outer `test_failed`/1 is never by itself the red. `SKILL.md:495` calls exit 1 a "failed test contract". That is wrong for `error_document`, where nothing was measured.
3. **Child findings are dropped from harness JSON.** `grade()` keeps runner aggregates and `null_observed_exit_records` (`check.py:508-523`). `stdout_tail` keeps only the last 600 chars (`:70,108-113,614`). The runner's trailing `limits` block alone is 773 chars; with `verdict_exit`/`error`, the post-records trailer is 840 chars (rejected) or 797 (accepted). I computed this statically: `ast.literal_eval` of `measure.py:73-79` `LIMITS`, laid out like `run()`'s `json.dumps(indent=2)`; no lane code ran. So every tail falls inside the limits/error trailer, and no per-case runner `name`/`observed_finding`/`observed_exit` survives. Two things follow:
   - The latest verifier's method (`round-14-verifier-spotcheck.md:52,80`: recount record tallies, record names equal corpus names, expected/observed literals, and outer exit equals `verdict_exit`, without executing sibling commands) cannot be applied to round-15 harness output. Only runner self-reported `passed`/`total` plus marker/audit counts can be recounted.
   - The runner's own `unique_case_names` (`measure.py:412`) is discarded too. That is the exact R1 mechanism, "unique ≥ 16 minimum yet total > unique", which `:142` still labels `[INFERENCE from static code]`.
4. **Marker evidence is anchored only in full-matrix runs.** `check.py` already pre-creates the marker and audit files so "missing" never reads as 0 (`:336-341`). Rejected rows already require marker 0, all audit events 0, Popen 0, N null `observed_exit` records and `tool_present` (`:525-572`); this is AttackSentinel and HarnessSafety H3 adopted. A zero marker is meaningful only next to a same-run valid row that recorded marker == N with the same wrapper (`only: null`). `--only <rejected row>` returns `clean`/0 with unanchored zeros; `only` is recorded at `:647`. Audit coverage limits:
   - The audit witness is Python-level. `subprocess.Popen` is audited at the top of POSIX `_execute_child` (`/usr/lib/python3.14/subprocess.py:1858`), before the `posix_spawn` gate that requires `cwd is None` (`:1860-1865`).
   - `multiprocessing.util.spawnv_passfds` calls `_posixsubprocess.fork_exec` directly (`/usr/lib/python3.14/multiprocessing/util.py:523`). Whether that C path raises a matching event was not verified.
   - The runner's only spawn site is `measure_case` `subprocess.run` (`measure.py:239-251`). The "before ANY child" claim is therefore bounded to this benign runner (`check.py:84-95` LIMITS).
5. **`child_count` (`:612`) duplicates `observed.classifier_invocations` (`:500`).** It counts classifier-wrapper entries spawned by the runner, which are the harness's grandchildren. The harness always spawns the runner itself. Receipts should cite `classifier_invocations` plus `runner_popen_events`/`runner_process_events` and describe `child_count` that way (agrees with `AttackClaim.md:48`).
6. **`--selftest` is the same mode as the gate** (`check.py:43-44,687-691`). A gate run plus a selftest run is one measurement repeated, not corroboration (`round-14-verifier-spotcheck.md:86`). `SKILL.md:495` lists them in separate gate and self-test columns.
7. **The docstring repeats the R1 error.** `check.py:4-7` says "proves … rejects every corpus that contains duplicate declared case names … while corpora of at least 16 distinct names still measure", and `--help` prints it (`:678-681`).
   - (a) A finite literal matrix cannot prove "every corpus". This is the same generalized-promise class R1 found in `measure.py:13-14,77`; `SKILL.md:501-504` and `round-15.md:9` correctly say finite.
   - (b) "Corpora of at least 16 distinct names still measure" is false for exactly the rejected rows (16 distinct plus a duplicate). It restates the minimum/injectivity conflation that KQ18 (`QUALITY.md:87`) and Gate row `round-15.md:16` reject, and contradicts `SKILL.md:491`.
   - Owner: GuardHarness/L1. Suggested text: "grades the committed literal matrix: corpora with a duplicate among nonblank stripped declared names are rejected before any runner-spawned classifier child; corpora of ≥16 names, all distinct after strip, still measure."
8. **The harness output has no boundary fields.** `check.py` output carries no `scope`/`readiness`, unlike the runner (`measure.py:399-402`) and the classifier (`:85-86`). Every `clean`/0 and child `loaded_same_digest`/0 here is cloned offline fixture metadata. `PROVINCE.md:17-29` records nothing listening on 8080/34113 and no `MODEL_OK` from retired samples; KQ1/KQ4/KQ13/KQ17 and Gate row `round-15.md:18` all apply. No layer's 0 may be quoted as served identity or readiness.
9. **Latent identity split for blank names.** `check.py:189-190` counts whitespace-only names as the stripped value `""`. `corpus_problems` drops them (`measure.py:350-355`). No committed row uses blank names (`HarnessReview.md:27`), and `round-15.md:89-92` puts blank names out of scope. A retained runner `unique_case_names` would expose any such split per record.

## Proposed move (one, bounded)

**Keep the runner child's per-test evidence in each `check.py` record, and admit red/green from per-record signatures, never from the outer finding.**

(a) **Additive `check.py` change, no predicate change** (GuardHarness/L1 own it; about 15–20 lines in `grade()` after `:523`, plus the result document):
- **Runner fields:** `observed.unique_case_names`, `minimum_unique_cases`, `runner_cases_sha256`, `runner_tool_sha256` (labelled as the wrapper hash; see HarnessSafety H4), `runner_scope`, `runner_readiness`, copied from runner keys `measure.py:399-420`.
- **`observed.record_names`:** the runner's record names. These equal the literal `names`, because `case_name` returns the unstripped nonblank name (`measure.py:131-136`).
- **`observed.child_results`:** a sorted list of `{observed_finding, observed_exit, passed, count}` over runner records.
- **`expected.distinct_stripped`:** carry `distinct` from `load_matrix:190` into the test record.
- **Top level:** `source_cases_sha256` and `template_name`.
- **Schema:** stays `kama-corpus-guard-test/v1`; it is not yet committed and has no consumers.

(b) **L1 receipt rule (no code).**

RED: frozen runner, `only: null`, no `error` key, `total` equal to the matrix size. All of the following must hold:
- The set of failed records is exactly the set of `expected_rejected` rows.
- Each failed record shows:
  - runner exit 0, `verdict_exit` 0, `error` null;
  - `passed == total == N`;
  - `unique_case_names == distinct_stripped` (≥16, below N);
  - `child_results == [loaded_same_digest/0/true × N]`;
  - `classifier_invocations == runner_popen_events == N`.
- Every valid row passes in the same run.

GREEN: repaired runner, `only: null`, outer `clean`/0.
- Each rejected row shows:
  - exit 1 and `verdict_exit` 1;
  - `error == "corpus: duplicate case names"` exactly — with D ≥ 16 the minimum conjunct must not also fire (KQ18 independent conjuncts);
  - `unique_case_names == distinct_stripped`;
  - `child_results == [null/null/false × N]`;
  - zero invocations and zero audit events.
- Each valid row shows `child_results == [loaded_same_digest/0/true × N]` and invocations == Popen == N.

Never admit:
- outer `test_failed`/1 alone as the red;
- an `error`-bearing `test_failed` as the red;
- an `--only` run as anchored admission;
- `--selftest` as a second corroboration;
- any 0 as readiness.

Optional extra checks (L1 decision; they cannot break the predicted green): require exact `error` equality and `unique_case_names == expected.distinct_stripped` on rejected rows, and `record_names == names` on every row.

## Affected axes

- **Calibration: improves.** Child findings and outer finding are attributed separately, as KQ17 does for the classifier. R1's static inference becomes runner-observed per record. The receipt becomes recountable by a verifier who does not execute anything, as in the round-14 method. Numeric score stays 7 → 7.
- **Operability: unchanged.** Part (a) adds no predicate. The optional checks fire only on a runner/harness divergence.
- **Freshness, depth, coverage, adjacency: unchanged.** No runtime, API fact, classifier policy or boundary change.

## Risks

- `check.py` was edited during this round; apply after the current edits settle and re-read its tag first.
- The retained fields are still self-reported by the code under test. They corroborate but do not independently authenticate (KQ16: a same-repository read is not independent authority). The independent witnesses remain the marker and the audit hook.
- If (a) is declined, per-case child evidence is unrecoverable from `check.py` output without re-running the runner outside the harness, which would be a second, unmatched execution path.
- Record size grows slightly: about 50 rows with ≤33 names each.

## Verification (L1, once, after edits; not run here)

- `python3 tests/ollama-corpus-guard/check.py --runner .ufo/waves/round-15/frozen/measure-before.py`, then apply the RED rule.
- `python3 tests/ollama-corpus-guard/check.py`, then apply the GREEN rule. `--selftest` is only a same-measurement repeat.
- Confirm by static diff that the `check.py` change touches only `grade()`, the result/error documents and the carried `distinct`.

## Limitations

- Everything above is static. The signature table is `[INFERENCE]`; no red or green outcome is asserted.
- The one computation was Python `ast`/`json` over the `LIMITS` constant; no lane code was executed.
- The C-level audit behavior of `_posixsubprocess.fork_exec` was not checked.
- Line anchors refer to `check.py#9540` and `measure.py#6643`; both files were edited during this round.

Report: .ufo/waves/round-15/build/advice/FindingExit.md — connector advice only; no tests or runs; no tools installed.
