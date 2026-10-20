VERDICT: partial — keep survivors.py new, but six H-faults are F1–F8 run variants, H2/H5 need row guards, and the frozen detector invocation is missing mandatory flags.

# Scope and method

Read-only review of the C2 plan as written in `.ufo/waves/round-18/build/make_spec.py:97-115` (items C2FaultControls, C2Survivors, C2AppendOnly, C2Provenance) against the frozen inputs, the round-17 advice, and the current detector code (byte-identical to the frozen detector at review time: `sha256sum tests/probe-verdicts/fault-controls.py` = `d3eaade…` = `.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py`). No commands that execute a detector, check.py, tool or server; no scratch clone; no installs. One lane write: this Report.

Axes named before reading: **calibration** (will the after-count actually be zero, and for the right reason), **operability** (can L1 re-run the count from committed bytes without a false green), **weight** (one authority per rule; no second copy of a derivation).

# Q1 — could survivors.py reuse round-17 mutants.py?

**It could import ~60–95 generic lines, but the mutant table, grid and detector logic are not reusable; the net saving does not pay for the coupling. Recommendation: new, small survivors.py; copy `run_cmd` and the matrix digest formula, do not import the frozen runner.**

- Reusable surface is small. `run_cmd` (`.ufo/waves/round-18/frozen/round-17_c1_mutants.py:716-749`) already has the correct process-group behaviour (`start_new_session=True` :730; `os.killpg(proc.pid, signal.SIGKILL)` :740) needed for the escaped-sleep fault. `sha256_file` :639-644, `replace_unique_literal` :350-354 and `emit` :1104-1130 are another ~40 lines. That is the whole overlap.
- The core is not reusable. `MUTANTS` is M0–M9 (:453-622) with candidate fallbacks (`apply_mutant`, :624-632); C2 needs H1–H7 as *single-site exact-string* edits with `site_missing`, never skipped (`make_spec.py:101`). `run_cell`'s kill predicate is "any observable diff" — `if diffs: killed_by.append(f"pair:{tag}")` :966-967 — not the plan's `accepted>0 or exit!=0` rule.
- `run_controls` is hard-wired to the current detector: `FAULT_CONTROLS = MATRIX_DIR / "fault-controls.py"` :100 and `run_cmd([sys.executable, str(FAULT_CONTROLS), "--check", …])` :782. The plan needs frozen vs current detector bytes; the frozen runner cannot be edited, so reuse would require monkeypatching a module global — a hidden second authority.
- Importing the frozen file is only possible through `importlib` (hyphenated basename) and turns an evidence artifact marked "Never edit" into a runtime library. Its `LANE = RUNNER_DIR.parents[3]` (:91) resolves to the lane root from both `.ufo/waves/round-17/c1` and `.ufo/waves/round-18/frozen` by coincidence, but its `MATRIX_DIR`, `PROBE_CURRENT`, `FROZEN_CHECK` and pinned `EXPECTED_MATRIX_SHA256` (:92-108) are round-17 constants that survivors.py would have to override anyway.
- Copy the digest formula, not the module: `matrix_set` (:646-675) defines the matrix-set sha256 the detector pins (`EXPECTED_MATRIX_SHA256`, fault-controls.py:70-73). survivors.py should recompute that formula for its input record.

# Q2 — are the planned faults redundant with F1–F8?

**No semantic duplicates: each H corruption is chosen precisely because its same-field F fault misses it. But six of the nine planned faults are structural variants of existing fault entries, and implementing them as new top-level faults duplicates the target-attribution and F6-cache machinery. Fold them as extra runs inside F1/F4/F5/F6/F8; keep new fault ids only for the escaped-sleep mechanism.**

| H mutant | existing fault | why the existing fault misses it | cheapest representation |
|---|---|---|---|
| H1 reason case-insensitive | F1 appends `"-forged"` (`fault-controls.py:283`) | suffix changes more than case (advice `MutC1Preregistered.md:42`) | extra run `mode=reason`, `variant=case` in F1 |
| H2 verdict `.strip()` | F4 lowercases (`:288`) | lower-case is not whitespace (advice `:62`) | extra run `mode=verdict`, `variant=pad` in F4, rows restricted (see H2 trap) |
| H3 route ignores method | F6 hits `/health` (`:242`) | wrong path, not wrong method on `/v1/models` (advice `:83`) | extra run in F6 with a POST-`/v1/models` touch + cached replay |
| H5 normalised ids | F5 forces `"kama-forged-id"` (`:292`) | a different id is not a normalisation difference (advice `MutC1Preregistered2.md:15`) | extra run `mode=served`, `variant=case` in F5, rows restricted |
| H6 no-request branch passes | F6 or F8 | F6 sends `/health`; F8 sends malformed bodies (advice `MutC1Preregistered2.md:46`) | extra run in F6: cached replay with no stub request |
| H7 grade last row | F8 | F8 supplies "no distinct first and last objects" (advice `MutC1Preregistered2.md:56`) | extra run in F8: `{"rows":[null, <valid row>]}` |
| crash: nested JSON | F8 non-JSON variants | `RecursionError` escapes `except JSONDecodeError` (`MalformedNonUtf8.md:6`) | F8 malformed variant (raw body) |
| crash: 5,000-digit int | F8 non-JSON variants | `ValueError` from the int-string limit escapes (`MalformedNonUtf8.md:6`) | F8 malformed variant (raw body) |
| crash: escaped sleep | F7 hang | F7's wrapper has no child; `TimeoutPath.md:51`: "F7 detection is not evidence of process-tree cleanup." | new postcondition-bearing run (child-liveness), not a `classify_run` target |

Fold mechanics are already present:

- `run_fault` loops `fault["runs"]` (`fault-controls.py:559-607`) and prefixes the diagnostic with `run["variant"]` (`:601`), so extra runs need no new fault id or classifier path; `detected = all(runs_detected)` keeps `accepted>0` as the kill signal when the H mutant is the subject.
- The claim counts killed/survived per **named mutant**, not per fault id, so the run `variant` label preserves "which corruption" without six new top-level entries. If L1 wants one fault id per H for the report, keep the ids but still share one parameterised wrapper mode (see below).

Two calibration traps in the fault table:

- **H2 must target `LoadingEnvelope.canonical-alias` only.** `expected_served_model` is keyed on the *observed* verdict (`check.py:339-366`): padding `MODEL_OK` breaks the drift conjunct, padding `MODEL_MISMATCH` makes the expected served id `"-"` and breaks `served_model_ok`, and the detector's external mirror still records the target `verdict` as failed (`failed_conjuncts`, `fault-controls.py:462-478`) — so those rows keep the fault "detected" and H2 survives. The advice says exactly this: "A whitespace-padded `MODEL_LOADING` verdict with otherwise correct fields is a suitable distinguishing input" (`MutC1Preregistered.md:62`). [INFERENCE from code; the executor should confirm with a scratch run.]
- **H5 must exclude `"-"` rows.** The DEAD and MODEL_LOADING rows carry served_model `"-"`; upper-casing `"-"` is a no-op, so the fault is not even detected on pristine check.py and would fail the suite's F0-style green requirement. Restrict H5 to `ReadyControls.expect-exact-id` and `ReadyControls.expect-different-id`.

Dead field to wire or delete:

- `_per_row(mode, touch, rows)` writes `"touch": touch` (`fault-controls.py:99-102`) but nothing reads it: the wrapper hardcodes `hit("/health")` (`:242`) and `run_fault` never exports a touch/method environment variable. If H3/H6 become F6 runs, pass `FAULT_TOUCH` (and a method) through; otherwise delete the field. Leaving it as unread metadata is a silent trap for the next reader.

Crash faults should not be measured twice:

- `mode="malformed"` already runs the real probe and then emits an arbitrary body (`fault-controls.py:253-264`; F8 table `:166-187`), so nested JSON and the 5,000-digit int fit as F8 variants. On frozen check.py both traceback → F8 becomes accepted; on fixed check.py they become per-row errors → F8 detected. That is the before→after, with one measurement path.
- Escaped sleep is the only genuinely new fault mechanism. It cannot be expressed as "traceback/exit not per-row" (`make_spec.py:101`): both frozen and current check.py already produce a parseable per-row timeout failure (`TimeoutPath.md:43-51`). It needs a post-run child-liveness assertion (wrapper records the `sleep` PID; detector asserts the PID is gone), and the frozen run must reap the leaked child itself.

# Q3 — is a separate dispatch-provenance copy the simplest fix?

**Yes. The per-wave copy is the established shape, the round-17 bytes are evidence, and the delta is local. A shared module or monkeypatch wrapper would be more code and a second authority.**

- The lane already carries per-wave copies: `git ls-files` shows `.ufo/waves/round-16/dispatch-provenance.py` and `.ufo/waves/round-17/dispatch-provenance.py`; round-17 is a 907-changed-line fork of round-16, not a shared import. A new `round-18/dispatch-provenance.py` is the convention, not new invention.
- The before side depends on the old bytes: `ProvenanceRerun.md:1` — "the 0→79 spawn fix and policy/hash receipts validate, but refused attempts are still undercounted" — and family (d) is exactly "frozen records 0, current records 82". Editing the round-17 file in place would make its committed ledger unreproducible and is outside C2's ownership.
- The delta is small and local. `tally_counts` (`round-17_dispatch-provenance.py:365-378`) counts only literal `refused`/`spawned` keys or `status`/`state` strings; `parse_attempt_result` (`:459-487`) needs a text scan for `([\w.-]+): Background job limit reached`, counting distinct task IDs. The round-17 payload has 82 messages, 82 IDs, 82 unique (`refused-result-1.json:4`), and no spawn text. Record `refused_method`/`refused_methods` symmetrically with `spawned_method` (docstring `:72-90`) so a future reader knows how 82 was derived; add the four selftest cases; keep modes 1–3 (the round-18 ledger and validation still need them).
- Required provenance for the copy: name the source path and its sha256 (frozen copy `11ebb2c0…`) in the docstring, state that refusal extraction is the only behavioural delta, and rewrite the round-17 defect narrative (`:1-48`) rather than copying it verbatim. After the change, the sentence "`refused` keeps the round-16 legacy tally" is false.
- Mode 2 takes `refused-result-1.json` only; `attempts.json` is not an input. Use a fresh `--out` ledger per arm (frozen/current) so the entries do not share a file.
- Do not build a 30-line wrapper that imports the round-17 module and monkeypatches `extract_counts`: it leaves the buggy parser as the only implementation, adds importlib plumbing for a hyphenated filename, and makes the round-18 ledger depend on a historical evidence file.

# Plan defects to fix before L1 measures

1. **Frozen detector invocation is incomplete.** The frozen copy resolves `MATRIX_DIR = SELF.parent` and `LANE = MATRIX_DIR.parents[1]` (`fault-controls.py:61-62`), which from `.ufo/waves/round-18/frozen` yields `LANE=.ufo/waves` and a nonexistent `DEFAULT_PROBE` (`:64`). With no `--matrix-dir`, `main` refuses at the pinned-digest check (`if staged_digest != EXPECTED_MATRIX_SHA256`, `:750`) and exits 2. The plan's command is only `fault-controls.py --check <mutant> --json` (`make_spec.py:101`); the frozen arm must add `--matrix-dir <lane>/tests/probe-verdicts --probe <lane>/tools/kama-probe.sh`. Without this, every mutant would be falsely "killed" by the `exit!=0` rule.
2. **`exit!=0` conflates detection with the detector's own fault.** fault-controls exits 0/1/2 (`fault-controls.py:24`); exit 2 is "own fault", not a kill. Define killed = `exit==1 and accepted>0`; survived = `exit==0 and accepted==0`; exit 2 = detector fault (survivors.py exit 2, never a verdict).
3. **No baseline guard.** Run the unmutated check.py through each detector first; if it is not `accepted==0`/exit 0, stop with exit 2. The plan says "where the unmutated check.py gives accepted==0 exit 0" (`make_spec.py:101`) but does not say what happens otherwise.
4. **Family (b) will not kill F0-bypass.** The plan's example assertion "F0 must run and be ACCEPTED by a correct check.py" does not exercise the failure branch. `MutFaultControlsSelf.md:104` records the bypass "SURVIVED every decision, every selftest, and the *entire* JSON comparison after deleting only timing." Add a failing-F0 fixture (a reject-all check.py) asserted to make the suite exit 2. "Main-run numbers" also misses (a) (only `why` changes, `:48`) and (c) (`runs` 4→1 and `check_exit`, `:81`): compare the normalized full JSON minus `seconds`, not just totals.
5. **Family (e) escaped sleep is not observed by its stated predicate.** "accepted = traceback/exit not per-row" (`make_spec.py:101`) is true of both frozen and current check.py for this fault. Either measure child liveness (PID recorded by the wrapper, asserted absent) or drop it from family (e) and keep it only as the fault-controls postcondition. The nested-JSON and huge-int faults are already F8 variants; measuring them again in family (e) is duplicate work.
6. **Family (b)/(c) subject not fixed.** State which check.py the mutated fault-controls main run uses (use the current check.py for both arms; the detector bytes are the variable) and which matrix; family (c) is correctly a selftest-only detector.
7. **Output schema and digests unnamed.** Name the document schema and record: current check.py, both fault-controls, both append-only, both provenance, probe, matrix-set digest (round-17 formula, `round-17_c1_mutants.py:646-675`), and `refused-result-1.json`. The plan says "record sha256 of every input" but names neither the schema nor the matrix digest.

# Preserved contract

- Keep the plan's core: single-site exact-string edits, `site_missing` never skipped, frozen/current paired report, sha256 of every input, exits 0/1/2.
- The F0 positive control, targeted-conjunct attribution (`fault-controls.py:523-538`) and per-row F6 cache (`:99-103`, `:559-585`) are load-bearing; new runs must not bypass them.
- `.ufo/waves/round-18/frozen/round-17_c1_mutants.py` and the round-17 dispatch-provenance copy stay frozen, unimported and unedited.

# Tradeoff

Folding the H faults into F1/F4/F5/F6/F8 reduces the fault table by six entries and reuses the existing attribution/cache code, but it gives up one-fault-per-mutant ids. The kill signal and the `variant` label survive; if L1 wants per-H fault ids for the Report's attribution table, keep the ids and only share the wrapper mode/prepass code. Either way, the H2/H5 row guards and the frozen-detector flags are mandatory for the after-count to mean anything.

# Limitations

- No execution: no detector, check.py, tool or server was run; no scratch clone. The H2/H5 kill analyses are [INFERENCE] from `check.py:339-366` and `fault-controls.py:450-479` and should be confirmed by the executor with one scratch run.
- The concurrent C2FaultControls/C2CheckPyRobust deliveries were not present at review time, so the review is against the frozen/current bytes.
- No LSP device was needed (no deletion proposed) and none was used.
- Installs: none.
