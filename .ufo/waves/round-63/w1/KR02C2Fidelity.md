# KR02C2Fidelity — C2 predicate audit and attacks on tools/round63-c2-counter.py

Seat: KR02C2Fidelity (leaf, advisory). Attack item: read freeze.txt C2 predicate clause by clause against the counter; attack the host-busy exception. Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09. No verdict on the claim is given here; findings and evidence only. No lane file was edited, no commit was made in the lane. Scratch `/fast/scratch/hyaku/kama-r63/w/KR02C2Fidelity` (clone + work dirs) is removed after receipts were copied to `.ufo/waves/round-63/w1/out/KR02C2Fidelity/`.

## 1. Measured tip (honest counter, unmutated, from the lane)

`python3 tools/round63-c2-counter.py --repo <lane> --tip 03a6a1d8… --work <scratch>` →
`population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` (exit 1; receipt `out/KR02C2Fidelity/tip.out`).

Only `selfdesc_mismatches=8` keeps `met=False`; every other conjunct is green, and the 12 control families are credited (baseline met). `host_busy=1`: the context-capacity row was scored as host-busy, so its K1 cell was not measured in this run (see §4.2).

## 2. Clause table (freeze.txt C2 predicate, sentence by sentence)

Enforcing lines refer to tools/round63-c2-counter.py at 03a6a1d8.

| # | Predicate clause | Enforced by | Status |
|---|---|---|---|
| 1 | 12 frozen capabilities in MANIFEST | `_MANIFEST` L50-118, `MIN_ROWS` L120, `population` L514 | enforced (MIN_ROWS is tautological: population is built from `_MANIFEST`) |
| 2 | appears exactly once in newest canonical list | `canonical_rows` L140-162 (highest N, L149-151); `canon_problems` L165-182: `can_n != 63` L171, duplicates across all slugs L175-177, subset L175 | enforced; extra non-frozen rows are accepted (predicate allows) |
| 3 | frozen row prefix | prefix list L52-…; check L178-181 (`startswith`) | enforced |
| 4 | newest list is "(round 63)" | L171 | enforced; detection is `HEAD_RE` L41 + substring 'canonical list' L149; table read is a 40-line window L156 with no end-of-table stop | 
| 5 | covered by a row of registry/capability-claims-r63.tsv | header must equal COLS L124-125/L195; column count L199-201; unbound cap L286-288; duplicate row L289-291; `covered` L328; `covered==population` in `is_met` L387 | enforced |
| 6 | binds exactly its manifest run template | binding id L296-299; run equality L300-302; pattern equality L303-305; quote ≥8 chars and substring of prefix L293 | enforced |
| 7 | executed live | `run_bound` L342-371, `bash -c` with cwd=tip tree L354-355 | **partly**: an existing `work/tip` is re-used without re-extraction (`checkout_tip` L481-482), see §4.4 |
| 8 | allowlisted environment (PATH, HOME, LANG, LC_ALL, TMPDIR only) | `ENV_KEYS` L42, env filter L504, TMPDIR set L505 | enforced by variable name; PATH value, `python3` resolution and the inherited cwd contents are not constrained (N4) |
| 9 | verdict true = pattern emitted and exit 0 | `verdict_fn` L215-217 (`not dead and pat in out and rc == 0`) | enforced |
| 10 | host-busy = exit 2 host-not-idle-before-K1 | `refusal_fn` L229-231; alt branch L363-370 (`rc == 2 and alt in out and not dead`) | enforced for rc and text |
| 11 | …"with a foreign llama-server listed by pgrep before and after" | `pgrep_foreign` L336-339; `before`/`after` L352/L364-366 require only non-empty lists | **not enforced** (N1, N2) — see §4.2 |
| 12 | host-busy only for context-capacity-receipt | `alt` present only in that template (L72-79); recorded host-busy requires `alt` L310-312 | enforced |
| 13 | outcome equals recorded verdict or is one of the row's two declared outcomes | `ok` L319-321 | enforced literally; for alt rows any of {true, host-busy} passes regardless of the recorded verdict (N6) |
| 14 | verdict sensitive: pattern removed until absent → false | `strip_all` L220-226, `is_sensitive` clause 1 L240 | enforced; clause is tautological for pattern-based verdicts (N7) |
| 15 | verdict sensitive: exit code changed (0→1, else→0) → false | `is_sensitive` L241 (`1 if rc == 0 else 0`) | enforced; exercised by planted defect 3 (checked: mutant E kills it) |
| 16 | sensitivity counted for every bound row | `facts['sensitive']` L317, `sensitive == bound` L532, `(outcome == 'true' and not sensitive)` L322 | enforced |
| 17 | sensitivity self-test rejects all 4 planted defective verdict functions | `sensitivity_selftest` L250-267; count checked L530 (`== 4`) | **partly**: planted #1 L256-257 (always true), #2 L258-259 (ignores pattern), #3 L260-261 (ignores rc) — 3 verdict functions; the 4th, L265-266, is a positive assertion on `is_sensitive('a')` and the round-62 expression, not a planted verdict function (N10). Planted #1 is deletable without loss of 4/4 (mutant F) |
| 18 | no bound target path is dead | `dead` L347-351 (first `tools/*.py` of each template, existence in tip tree); dead ⇒ mismatch L322, `is_met` L388 | partly: one path per template; `--model` path and other scripts a tool imports are not checked (N11) |
| 19 | mismatches=0 | L322-327; `is_met` L387 | enforced for verdict and sensitivity; the observed field is weak (N8) |
| 20 | reconciler `tools/round42-selfdesc-reconcile.py --repo REPO --tip TIP` reports mismatches=0 | `selfdesc_mismatches` L466-476; `selfdesc == 0` L528 | **partly**: exit status ignored (L474-476); the reconciler executed is the tip's copy (L470-471), so tip controls it (N9); its check is text-to-text self-consistency |
| 21 | 12 control families rejected, each by the failure it names | `controls` L392-463: 11 registry mutants L411-432, canon-drop L454-462; `hit` requires the named tag L450; expected tags L435-439 | enforced for the named tag; no collateral cap (N12); families touch only registry/canonical text, never a tool or a live verdict |
| 22 | credited only while the unmutated baseline is met | `baseline` L526, `credited` L527 | enforced |
| 23 | errors=0 | L542 prints `facts.errors + len(canon_mismatch)`; baseline requires both zero L526 | enforced for the baseline; control evaluation errors are not tallied (control rescoring raising would crash the run) |
| 24 | counter exit 0 iff met | L528-532, L551 | enforced |
| 25 | kill rule: sensitivity self-test count below 4/4 | L530 | enforced (count-only, see 17) |
| 26 | freeze kill rule: "bound run whose live outcome is neither declared outcome" | L320 | enforced |

Scope note: the counter faithfully implements the predicate as written. Several survivors below are predicate-level (the freeze lets tip-controlled tools and a pattern-bearing output certify themselves), not transcription errors. Both kinds are reported.

## 3. Mutant results (each committed in a scratch clone; counter run from the clone's tools/ path where the counter was mutated; all other counters unmutated)

Clone commit IDs and descriptions: `out/KR02C2Fidelity/mutants.txt`.

| id | mutation (commit) | counter one-line output (verbatim) | status |
|---|---|---|---|
| A | `tools/sources-append-only.py --selftest` prints `45/45 selftest cases passed`, returns 0 (7ee62bfd) | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` | **SURVIVED on facts**: identical to honest tip; met=False only because of the reconciler's 8. Would be met with any reconciler at 0 |
| X | A + `round42-selfdesc-reconcile.py` stub printing `mismatches=0`, exit 1 (a505cf75) | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | **SURVIVED** (met=True with a rigged sources tool and a reconciler whose exit status is 1) |
| Y | X + `kama-context-capacity.py` prints `host-not-idle-before-K1` and exits 2 unconditionally + registry `observed` column blanked (1bfa816f) | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | **SURVIVED** (the K1 cell never runs; observed column empty; all 12 control families still credited) |
| Z | Y + counter `is_sensitive` exit-code clause deleted (f46a76ca), run from clone path | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=3/4 controls_rejected=12/12 errors=0 met=False` | **KILLED** by the self-test (planted #3 needs the exit clause) |
| F | Y + counter planted defect #1 replaced by an unconditional `n += 1` (882668ca), run from clone path | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | **SURVIVED** (self-test reads 4/4 with planted #1 gone; the 4th count is the positive check) |
| S (stale tree) | tip 3a6cab61 = 03a6 + `sources --selftest` prints `selftest broken: planted regression`, exit 1; run with `--work` reused from the honest run | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=1 mismatches=2 canonical=63 selfdesc_mismatches=9 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | **SURVIVED on the sources row**: the bound `sources-registry` run is `true` (stale honest tool executed); the 2 mismatches are from live-ollama, see §4.4 |
| S-fresh | same tip, fresh `--work` | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=1 mismatches=2 canonical=63 selfdesc_mismatches=9 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | **KILLED**: sources row false (broken tool caught) |

Also observed: the honest counter's 12 control families are green at every baseline-met run (12/12 in tip, A, X, Y, F), so none of the families detects a rigged tool or a rigged reconciler — they mutate registry text only.

## 4. Findings (ranked; each cites the enforcing or missing line)

### 4.1 Self-certifying tools (predicate-level, code faithful) — A, X, Y, F
- The verdict is produced by tip-tree code (`run_bound` L342-371 runs `%T/tools/...` at the tip). Sensitivity (L220-241) is applied to the **output text**, not to the computation. A tool that prints the frozen pattern and exits 0 passes every clause of the predicate.
- Clause 14's tautology: `strip_all` (L220-226) guarantees the pattern is absent, so `verdict_fn(stripped)` is False for every pattern-based verdict. Clause 1 therefore only rejects verdict functions that ignore the pattern; it measures nothing about the tool.
- Evidence: A's facts line equals the honest line; X and Y reach `met=True`; F reaches `met=True` with planted #1 deleted.
- No control family perturbs a tool (L411-432 mutate registry text only). The 12 families cannot detect this class.
- Smallest correction (for the L1): pin the bound tools and the reconciler by sha256 of their bytes at the tip (or by a golden output on a planted regression copy), and add one family that mutates a bound tool's selftest to a regression and requires `met=False`.

### 4.2 Host-busy exception (clause 11 and 12) — N1, N2, N6
- `host_busy=1` at the measured tip: the context-capacity row was accepted as host-busy and the K1 cell (`all_ports_closed` true) was not measured. Clause 13 accepts either declared outcome for alt rows (L319-321), so this row cannot fail while the host is busy, and its recorded verdict is not checked.
- Acceptance needs only: `rc == 2`, the text in `out`, `not dead`, and `pgrep -x llama-server` returning a non-empty list before and after (L352, L363-366). Not checked: that the PIDs are foreign (not the lane's own children, not leaked from an earlier row), that they match the refusal's `other_pids_seen`, or that they are the same processes before and after. Mutant Y shows a refusal-only tool passing (`met=True`). In-process probe (`inprocess.txt` §3; `pgrep_foreign` replaced by injection, so this shows the dependence only, not real host behaviour): an empty list gives `false`; a one-element list naming a PID that is not a llama-server gives `host-busy`. The exception is decided by list non-emptiness alone.
- Host state at this measurement (pgrep -x llama-server, read at my start): seven processes, including operator servers on ports 1234 and 45669, a llama-b11755 child on port 34885 of unknown owner, and llama-server children under sibling-seat scratch paths (`/fast/scratch/hyaku/kama-r63/w/MT20C2DupAndObserved/…`). The context row's pass/fail is therefore set by concurrent processes, not by the lane's K1 cell. [INFERENCE that the sibling children are concurrent seat runs: from their paths.]
- Smallest correction: require the refusal's `other_pids_seen` to be a subset of the pgrep set before and after and to exclude PIDs whose `/proc/<pid>/cwd` or cmdline lies under the lane's own scratch; or refuse `host-busy` at the tip unless the K1 cell has also run on an idle host in the same wave (a non-alt cell measurement).

### 4.3 Reconciler (clause 20) — N9
- `selfdesc_mismatches` (L466-476) returns the first `mismatches=N` regardless of exit status; the tip's copy is executed (L470-471), so the tip controls its own count. Mutant X: exit 1 with `mismatches=0` → `selfdesc_mismatches=0` → `met=True`.
- What `mismatches=0` certifies: the head text repeats numbers from the SCORECARD's own Axes table and canonical table (reconciler docstring); it is a self-consistency check. It does not compare the lane's self-scores with any measured outcome.
- Measured here: the reconciler's 8 at 03a6 are r41=1, banner=1, planned=2, retired=1, saturation=1, caps=1, province=1 (receipts=0, readme=0, rel=0). The freeze says the head is re-derived after measurement. Any re-derivation is a new tip; C2 must be re-measured at that tip (the 03a6 line cannot be cited for the final tip).
- Smallest correction: require `rc == 0` and `mismatches=0` from the reconciler; run it from a copy pinned by sha.

### 4.4 Stale and non-fresh scratch (clause 7; `checkout_tip` L479-490, `run` dirs)
- `checkout_tip` returns an existing `work/tip` without re-extracting (L481-482). Blobs (registry, SCORECARD) come from the new tip, but bound tools run from the old tree. Evidence: `sources-append-only.py --selftest` at the reused tree prints `45/45 selftest cases passed` while `git show 3a6cab61:tools/sources-append-only.py` prints `selftest broken: planted regression` (exit 1); the per-row run scores `sources-registry` as `true`. In the same reused run, the reconciler's r41 operability row (which exports the real tip) fails the sources selftest, so two authorities disagree on one tool (selfdesc 9 vs bound true). Fresh run: sources row correctly false.
- Scratch is not cleaned between runs: `live-ollama-lifecycle` in the reused `--work/ollama` returned `verdict: FAIL` (`v1_single_id_equals_list_id: false`, `child_pre_dead: false`, rc 1); a fresh `--work` returns MODEL_OK. The live row's verdict depends on its scratch history. (Receipt: `out/KR02C2Fidelity/inprocess.txt` §5.)
- Smallest correction: `checkout_tip` raises when `work/tip` exists unless its contents match the rev (e.g. remove and re-extract); the counter creates a `mkdtemp` run directory per invocation.

### 4.5 Observed field (clause 19, axis calibration) — N8
- L324-327 check the self-described `observed` only when non-empty (`if row['observed'] and ...`), and by substring (`row['observed'] not in want_obs`). In-process with the honest outcomes: blank → mismatches 0; `selftest` (a substring of the pattern) → mismatches 0; `FORGED` → mismatches 1. Mutant Y blanks the column and the counter reads `met=True`.
- Smallest correction: `observed` must equal the output's pattern (or the alt text) exactly, and empty is a mismatch.

### 4.6 Self-test count (clause 17) — N10, and a survivor
- The predicate names 4 planted defective verdict functions. The code has 3 (L256-261). The fourth (L265-266) asserts `is_sensitive('a')` is true and that the round-62 expression differs on pattern 'a' — a positive check, not a planted defect.
- Mutant F: planted #1 replaced by `n += 1` → `sens_selftest=4/4` → `met=True`. With the positive check kept, 4/4 is reachable with one planted verdict function rejected.
- Positive: each clause has a planted killer — strip clause by planted #2 (ignores pattern), exit clause by planted #3 (ignores rc). Mutant E (exit clause deleted) → `sens_selftest=3/4` → KILLED.
- Smallest correction: four planted defects, each rejected by name (pattern-ignoring, rc-ignoring, always-true, and the one removed here), with the count equal to the number of planted defects only.

### 4.7 Control families (clause 21) — N12
- All 12 families mutate registry or canonical text (L411-432, L454-462), and scoring reuses live results from `_EXEC_CACHE` (L378-381): the controls never re-execute a bound run. The `expect` table (L435-439) is correct for the named tags; there is no collateral cap, although the C1 freeze gained one (AMENDMENT 1) for the same vacuity pattern. Each family is credited only if the baseline is met (L526-527), so at this tip the 12/12 printed is a function of the baseline, not of the families.
- The `drop` family's `covered` tag is produced by any registry defect that reduces coverage; the `binding` family's tag is produced by any binding defect. The rule is "named tag present", which is satisfied by any defect that produces that tag.

### 4.8 Smaller items
- N4: allowlist names only (L42, L504); PATH contents and `python3` resolution unconstrained.
- N11: dead check covers only the first `tools/*.py` in each template (L348-351); `--model` path and any tool a bound tool imports are not checked; `dead` is a pre-run check.
- N13: the canonical table window is 40 lines and stops only at `##`/`###` (L156-158), so a long table or a row past line 40 is silently not read (fails closed as "uncovered").
- N14: parser divergence with the reconciler: the counter's `HEAD_RE` accepts a non-bold heading (L41, L149); the reconciler requires `round N**` (its `canon`). Tested: a non-bold "canonical list as of round 64" in prose makes the counter read 64 and fail closed; no pass-side divergence found.
- N15: `rec` is lower-cased (L306), so `TRUE` is accepted; cosmetic.
- N16: `checkout_tip` fails open on a partial extraction (L481-482 treats an existing directory as complete).

## 5. Clauses that are enforced as written (no finding)
Canonical list round 63 and prefixes (L165-182); registry coverage, duplicates, unbound caps, column shape (L185-205, L283-293, L328); binding, run and pattern equality (L296-305); quote check (L293); verdict function (L215-217); refusal function and its exit-2 requirement (L229-231); mismatch rule for true outcomes (L322); sensitivity count and `sensitive == bound` (L317, L532); dead-as-mismatch (L322, L388); baseline gating of control credit (L526-527); controls' named-tag rule (L450); canon-drop control (L454-462); exit iff met (L528-532, L551); `ENV_KEYS` allowlist (L42, L504-505). Mutant E confirms the exit-code clause is exercised.

## 6. Counts
- Counter runs on the lane tip: 1 (tip) — the one-line output is in §1.
- Mutant runs: A, X, Y, Z, S, S-fresh, F (7 counter runs) plus 2 in-process probes; host-busy monkeypatch probe ×2; per-row reuse probe ×2.
- Killed: Z, S-fresh. Survived: A (on facts), X, Y, F, S (sources row). No unresolved runs.
- Tools installed: none. Pacman not used. No registered consumer port was contacted; live runs were only through the lane's counter/tools on unregistered loopback ports; no foreign llama-server was touched.

Tally line for this item: `KR02C2 attacks: killed=2 survived=5 (A-facts, X, Y, F, S-reuse); clauses with no/partial enforcement: N1, N2, N4, N6, N7, N8, N9, N10, N11, N12 (see §2 rows 7, 8, 11, 13, 14, 17, 18, 19, 20, 21)`
