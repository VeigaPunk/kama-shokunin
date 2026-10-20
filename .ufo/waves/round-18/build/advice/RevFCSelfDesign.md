VERDICT: confirm — advice's four detector survivors are real, match the frozen bytes line-for-line; SC-1–SC-4 below kill each without touching check.py.

# RevFCSelfDesign — self-consistency assertions for fault-controls.py

Reviewer seat KamaR18.RevFCSelfDesign-2, 2026-10-20. Read-only seat; this Report is the only
write. No scratch clone, no execution of the detector, measure scripts, or gates; no servers,
no ports, no installs (Python 3.14.8, git, coreutils reused as found).

Reviewed: `.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md` against frozen
`.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py`
(sha256 `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`, 815 lines).
Deliverable: a specification of self-consistency assertions that kill every named survivor,
with an adversarial analysis of each assertion.

Review axes: **calibration** (does the detector reject malformed/off-target outcomes and catch
its own weakenings?) and **operability** (are the self-checks hermetic, fast, and independent
of the check.py under test?). The design below aims to advance calibration without adding
network, runtime, or check.py dependencies.

## 0. Identity check of the attacked artifact

- `git diff --stat 54a29268e2083caa2b1e0d54ee1e7d90961302f3 e75cf680b53484a61709ee1b2787d8dbc6419f74 -- tests/probe-verdicts/fault-controls.py` is empty; `git show` at both commits yields
  sha256 `d3eaadeb…312`, identical to the frozen copy and to the advice's "before/restored"
  hash. The advice's line citations therefore map 1:1 onto the frozen bytes; all anchors below
  are cited at frozen line numbers and were verified present.
- Advice anchor verification: `if target:` → frozen :523; "stdout is not parseable" → :502-504
  (insertion region :493-501); "a shared cache cannot tell rows apart" → :100, `_per_row` call
  → :156; F6 per-run cache → :575; "if not positive[\"detected\"]:" → :764; "without invoking
  check.py" → :637; `do_selftest` → :656. No drift. (Read-verified; the mutations themselves
  were not re-run — the advice's own 27 logged runs are that evidence.)

## 1. Findings (severity-ordered)

**F-1 (medium) — the only detector self-check is static table validation; it cannot see any
behavioral weakening.** The frozen help describes selftest as `"validate the fault table against
the real matrix"` (`.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:636-637`);
its implementation at `:656-707` checks matrix digest/breadth, row membership, port modes,
hang arity, F4 non-MODEL_OK coverage and family coverage, but never calls `classify_run`
(`:482`), `run_fault` (`:559`) or the gate in `main` (`:764`). The advice reports: `"The pristine,
four mutant, and four restored selftests all produced exactly the same JSON and exit 0"`
(`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:108`). Root cause, not an accident.

**F-2 (medium) — survivor (b) is killed only by an external, non-inheritable control.** The
advice says it was `"KILLED by the two-arm JSON decision comparison"` but `"SURVIVED both
current-only decisions and every selftest"` (`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:70`).
The frozen classifier rejects non-JSON stdout at `:502-504` (`"stdout is not parseable"`), but
the frozen-arm comparison was round-17 evidence; round 18 has no frozen arm, so C2 must
internalize the kill (SC-1 V1-V3, SC-2 crash run). The advice also states no exit-2 or outer
timeout counterexample was injected (`MutFaultControlsSelf.md:70`); that is an untested coverage
gap [INFERENCE — based on the advice's recorded limitation].

**F-3 (medium) — survivor (d) is output-invisible on an honest check.py.** The mutation
disables only the abort gate at frozen `:764-767` (`"if not positive[\"detected\"]:"`), retaining
F0 diagnostics; the advice says `"the disabled branch is never distinguished"` because both
available check.py versions pass F0 (`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:104`).
Any self-consistency scheme that only runs an honest positive control cannot kill it; a
deliberately failing positive double is required (SC-4).

**F-4 (low) — F6 isolation rests on a per-run cache name, with no content identity check.**
The frozen table is per-row (`:99-102`, quote: `"each row gets its own check invocation"`) and
F6 uses it at `:156`; cache paths include the run index at `:575`, but the prepass at `:580-583`
checks only `Path(cache).exists()` and `Path(cache + ".rc").exists()` — not that cached content
belongs to the run's row. The advice reports F6 `"SURVIVED aggregate/per-fault decisions and
selftest"` (`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:93`); SC-3 adds
structural + content-identity assertions.

**F-5 (info) — the advice's decision comparison is a harness, not a committed meta-test.**
The advice explicitly limits it to `"an external observation of outputs, not a claim that a
committed meta-test enforces it"` (`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:11`).
Round 18 cannot inherit that control; the detector must carry its own kills, with
`.ufo/waves/round-18/c2/survivors.py` as external rerun backstop.

**F-6 (info) — reviewed advice text is faithful to the frozen code.** Survivor (a)'s reported
source anchor `if target:` is present at frozen `:523`; F6's `_per_row("f6", "/health", F6_ROWS)`
is at `:156`; and the F0 gate is at `:764-767`. Advice's frozen vector is
`"T T T T F F T F"` (`.ufo/waves/round-17/falsify/advice/MutFaultControlsSelf.md:28`).
That vector's consistency with F8 is plausible from the frozen exit/JSON checks at `:493-504`
[INFERENCE — source consistency read, not an independent run].

## 2. Design: self-consistency assertions SC-1 … SC-4

Constraint honored throughout: nothing below reads, stages, or invokes the check.py under
test. Ground truth is (i) the detector's own documented detection rule (`:15-22` docstring:
"DETECTED <=> every run exits 1 AND prints parseable JSON in which every faulted row has
\"passed\": false", plus the targeted-conjunct rule at `:107-109`), (ii) the frozen round-16
matrix JSONs (already digest-pinned at `:73-75`), and (iii) detector-owned literals. Selftest
stays honest to its `:637` promise "without invoking check.py".

### SC-1 — golden `classify_run` vectors (kills (a), (b) at unit level)

`classify_run` (:482) is pure. The selftest builds synthetic records from real matrix rows:
`ok_record(name)` sets `verdict/reason/probe_exit` to the row's `expected`, `drift =
(verdict != "MODEL_OK")`, `served_model = contract_served_model(test)` (`:417-453`,
matrix-derived), `requests = [{"method":"GET","path":"/v1/models"}]` for stub rows, `error`
absent — i.e. `failed_conjuncts` (:455-479) computes `set()`. Then corrupt exactly one field
per vector. Required vectors (expected values are the assertion):

| id | fault | input | expect |
|---|---|---|---|
| V1 | F1 (target reason) | exit 1, stdout `Traceback …` (non-JSON) | `(False, "not parseable")` |
| V2 | F1 | exit 2, stdout `""`; and exit 124, stdout `""` | `(False, "check exited 2/124 …")` |
| V3 | F1 | exit 1, parseable, every row `passed:false` with verdict lower-cased and drift recomputed from that value | `(False, "NOT on the targeted 'reason'")` |
| V4 | F1 | exit 1, parseable, every row failing exactly `{reason}` | `(True, …)` |
| V5 | F0 | exit 0 all passed → `(True,…)`; exit 0 one row `passed:false` → `(False, "positive control")` |
| V6 | F1 | exit 1, parseable, one `--only` row absent from records | `(False, "missing rows")` |
| V7 | F1 | exit 1, parseable, one row `passed:true` | `(False, "faulted rows still passed")` |
| V8 | F1 | exit 9 (`WRAPPER_EXIT`, :68) | raises `OwnFault` |
| V9 | F1 | exit 1, JSON `{"records": 3}` | `(False, "lacks a records list")` |

Kills: V1/V2 vs (b) — the mutant's inserted early return (`exit_code != 0` → True) flips V1/V2
to `(True, "any nonzero exit counts")`. V3 vs (a) — `if False and target:` (:523) falls
through to the final `return True` (`:539-541`), flipping V3; V4 keeps the opposite direction
honest, so "fixing" (a) by never detecting also fails. Each vector asserts both `ok` and a
stable `why` fragment (substring), so diagnostic loss is a failure, not a courtesy.

No circularity: inputs come from matrix JSON + the detector's own re-derivation helpers; the
expected outputs are the documented detection rule, not observations of check.py.

### SC-2 — reference-harness end-to-end runs (kills (a), (b), (c), (d) at pipeline level)

Use a selftest-only `ref_check_runner` callable injected into the production driver; do **not**
create, stage, or invoke a fake `check.py`/probe executable. The normal path retains
`run_check`; selftest supplies the runner directly to the same `run_fault`/suite-driver
functions. Thus `--selftest` keeps its `:637` contract `"without invoking check.py"` literally,
and does not read, stage, or invoke the check.py under test.

`ref_check_runner(scratch, only_rows, env_extra)` synthesizes only detector-owned stdout/exit
pairs; it never creates a process, binds a socket, or touches a probe. It uses `FAULT_MODE`
from `env_extra` (normal `run_check` inherits env at `:354-355`) and the pinned matrix rows:

- `pass` → honest `records` with every requested row `passed:true`, exit 0; configurable
  negative-positive mode → exit 1, used only to attack the F0 gate;
- `reason|verdict|drift|exit|served` → JSON records with each requested row `passed:false`
  and only that mode's target conjunct failing, exit 1;
- F6 prepass (`FAULT_MODE=pass` plus `FAULT_CACHE`) → write row identity and rc to that cache
  path, return honest positive records; F6 replay → read the cached row identity and emit
  rows failing only `{route}` on match, only `{reason}` on mismatch;
- `malformed` → exit 1 with non-JSON traceback-style stdout.

Selftest uses a ref fault table built through the same `_per_row` helper (`:99-102`, no hang
run) and drives the real `run_fault` → `classify_run` → suite-decision path with that runner.
Factor the driver portion of `main` into a shared function accepting the runner; normal main
passes `run_check`, while selftest passes `ref_check_runner`. Assert the golden vector:

- ref-positive (`pass`) detected True; ref F1 (`reason`) detected True;
- ref X1 `{"target":"verdict", runs:[{mode:"reason",…}]}` (off-target) detected **False** —
  kills (a) at pipeline level (mutant flips it True);
- ref crash (malformed non-json) detected **False** — kills (b) at pipeline level;
- ref F6 per-row all detected True, with cache identity and isolation checks from SC-3 — kills
  (c) at pipeline level;
- aggregation unit vectors on a fabricated entry list: `detected_n == sum`, `accepted_n ==
  len-detected_n` (`:778-779`), return 0 iff accepted==0 (`:807`).

The ref runner's behavior is independent of check.py: inputs are the fault mode, selected
matrix row names, and detector-owned truth table; expected outcomes are the documented
detection rule, not observations of the check.py under test.

Scope line (deliberate): SC-2 exercises detector decision logic, not wrapper corruption
fidelity — the wrapper's field-mutation behavior against the real probe stays covered only by
the production suite. The ref runner supplies canned outcomes, not a mock implementation of
check.py grading logic; it does not parse probe output or implement probe/check semantics.

### SC-3 — F6 isolation assertions (kills (c), both shapes)

1. Structural (pure, no execution): inspect the actual `FAULTS` table; every fault whose run
   mode needs per-row isolation (`f6`) must have exactly one row per run, and the run-row
   multiset must equal `F6_ROWS`. Mutant (c) rewrote the table to one 4-row run (`:156`) →
   fails. Build the ref F6 row list with the same `_per_row` helper to exercise runtime
   isolation separately.
2. Cache-path/content isolation: keep the per-run cache files within the selftest's temporary
   directory. After ref F6, assert the cache directory contains one distinct cache path per
   F6 run and each file names the matching prepass row (`:575` creates indexed names; `:580-583`
   checks existence only today). No new suite-JSON field is needed. A shared path collapses
   the count or row identity and fails; shared content is also caught by SC-2's
   contamination signal (off-target failure → not detected → golden mismatch).

### SC-4 — positive-control gate, unit + driver path (kills (d))

1. Unit: factor the gate at `:764-767` into a pure `positive_gate(positive) -> (bool, msg)`
   called from the shared suite driver used by `main`; vectors: `{"detected": False,…}` →
   False, `{"detected": True,…}` → True. Kills a (d)-shaped edit inside the predicate.
2. Driver-level: selftest invokes that same production suite-driver function with
   `ref_check_runner` configured to fail its honest-mode F0 (exit 1). Assert: return code
   **2**, returned reason identifies the suite as invalid (main prints `"suite INVALID"` at
   `:765-766`), and the runner call log shows exactly one F0 invocation followed by no
   F1..Fn invocations (the gate precedes fault execution). Pair this with SC-2's healthy-F0
   case continuing into F1 to reject an unconditional abort. Kills (d) exactly as mutated at
   `:764` — disabled gate continues to fault execution — and catches omitted F0 collection
   through the missing-F0 call-log entry.

### Wiring (the MutControlsSelf analog, R7)

`--selftest` must include SC-1..SC-4 and fail with a named problem group per layer
(`classify-vector`, `ref-pipeline`, `f6-isolation`, `positive-gate`). Acceptance for C2:
applying each of mutants (a)-(d) to the new file flips `--selftest` to nonzero/mismatch, and
`.ufo/waves/round-18/c2/survivors.py`'s named-survivor count for fault-controls goes to 0.
The suite JSON contract otherwise stays unchanged.

## 3. Per-survivor kill matrix

| survivor | site (frozen) | killed by |
|---|---|---|
| (a) drop targeted conjunct | `:523` `if target:` | SC-1 V3 (+V4 direction guard); SC-2 off-target X1 |
| (b) any nonzero = detected | `:493-504` early return | SC-1 V1,V2; SC-2 crash run |
| (c) shared F6 cache | `:156`, `:575` | SC-3 structural + cache checks; SC-2 ref F6 contamination |
| (d) F0 gate bypass | `:764` | SC-4 unit + shared-driver exit-2 contract |

## 4. Attack: can a broken detector satisfy the assertions?

- **Call-site bypass of `classify_run`** (unit vectors pass, pipeline broken): killed — SC-2
  drives the same production `run_fault`/`classify_run` path end-to-end.
- **Ref-vs-production branching** (honest only with the selftest runner, weakened with the
  normal runner): the selftest and production paths share `run_fault`, `classify_run`, F6
  cache handling and the suite gate; only the injected `check_runner` differs. A mutant that
  branches on runner identity could evade this selftest; that is outside the four named
  mutations, must be called out in code review, and remains backstopped by survivors.py.
  Residual.
- **Literal forging** (edit golden vectors / expected ref vector to match mutated behavior):
  SC-1 and SC-2 expectations are literals, so a mutant can forge them — but it must forge
  SC-1 V3, SC-2 X1 and SC-3 coherently while keeping V4/ref-F1 true-positive, and still pass
  the SC-4 driver contract. Any purely self-referential scheme can be satisfied by a mutant
  that forges every layer; that class is not killable without an external oracle and remains
  with survivors.py. Mitigate by deriving the ref expected-vector from `ref_check_runner`'s
  behavior table programmatically (a forge must then edit table + expectations consistently),
  and by keeping the ref vector in selftest JSON output so dishonest edits are reviewable.
- **Selftest bypass** (`--selftest` returns 0 unconditionally; driver ignores it): neither
  the selftest's normal exit-0 check nor SC-4 alone can detect a complete bypass of
  `do_selftest`; only an external mutant that deliberately bypasses selftest, or review of
  its control flow, can. Keep that as an explicit residual, not a claimed kill.
- **SC-3 point-fixes**: restoring the table shape but sharing the cache path, or restoring
  the path but sharing content, trips the cache-path/content assertion or SC-2 contamination
  signal respectively; only a coherent ref-side forge (above) escapes.

## 5. Residual risk and verification gaps

- I verified all mutant anchor sites, the selftest's static-only nature, and the env-inheritance
  and cache-prepass mechanics by reading the frozen bytes; I did not re-run the mutations or a
  prototype selftest (read-only seat, no scratch authorized). The SC-2/SC-3 ref-harness design
  is specified, not executed — C2's first scratch run should confirm the golden vector
  empirically before pinning it.
- The ref runner's behavior table must be kept in review-sync with `classify_run`'s documented
  rule; drift there degrades SC-2 silently (only the external rerun would notice).
- Exit-2 and timeout witnesses remain unexercised even in the new pipeline vectors (SC-2's
  crash run is exit-1/non-JSON, matching the advice's observed witness); V2 covers them at unit
  level only. [INFERENCE carried from the advice's limitation list.]
- Advice numbers (3→0 accepted on frozen, 8/0 on current, vector `T T T T F F T F`) were not
  independently reproduced here; identity of the attacked bytes was, which is the part this
  design depends on.

## 6. Installs / updates

None. No pacman, uv, npx, or binary installs; no services started; no ports bound; no lane
writes besides this Report.
