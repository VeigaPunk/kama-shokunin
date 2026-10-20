# HarnessReview — round-15 read-only review (child CLI vs selfcheck vs marker oracle)

Seat: KamaR15.HarnessReview-3 (leaf reviewer). Root: /home/vgpnk/Projects/shokunin/kama-shokunin.

## Scope and method

- Read-only. No tests, builds, linters, smoke runs, or harness/runner executions. No edits outside this report.
- Commands used were limited to file reads, `grep`, `sha256sum`, `jq` queries over fixture JSON, `git status`/`git diff --stat`/`git diff` on one file, and a strict-JSON parse (duplicate-key and NaN/Infinity rejection) of the committed fixture files. The parse was data inspection only; no harness code was run.
- Checked against: `tools/kama-ollama-evidence.py` (child CLI), `.ufo/waves/round-14/measure.py` (runner, now with an in-flight 2-line repair), `.ufo/waves/round-15/frozen/measure-before.py` (pre-edit snapshot), `tests/ollama-evidence/cases.json` (oracle), `tests/ollama-corpus-guard/*.json` (new guard fixtures), and round-14 lesson receipts for the "fixed oracle" definition.
- Tools installed/updated: none.

## Pending (not failures)

- `tests/ollama-corpus-guard/check.py` does not exist at read time. Only the 12 fixture JSON files are present. Everything that depends on the harness (clone-from-first-case, `--selftest`, `--only`, the zero-child proof) is **pending** and not reviewed.
- The round-15 measure repair is in flight (see Finding 1). I reviewed the current 2-line diff, not a final tree.

## Facts verified (static)

1. **Frozen snapshot intact.** `frozen/measure-before.py` sha256 = `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, equal to `frozen/manifest.json` `sha256`. Its size and visible structure match the pre-edit round-14 `measure.py`.
2. **Oracle unchanged.** `tests/ollama-evidence/cases.json` sha256 = `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`, the oracle pinned in `corpus/lessons/round-14.md:121-122`. It has 51 entries, 51 unique names, and no NaN/Infinity or duplicate keys under a strict parse. New guard fixtures live in separate files, so they do not move this oracle.
3. **In-flight repair diff** (`git diff -- .ufo/waves/round-14/measure.py`, +2 lines only): in `corpus_problems` (current `measure.py:350-364`) it adds `if len(declared) != unique: problems.append("duplicate case names")`. The pre-edit function tested only `unique < MINIMUM_UNIQUE_CASES`, so a duplicated corpus with ≥16 stripped-unique names passed. The docstring (`:13-14`) and `LIMITS[3]` (`:77`) already promised rejection. The `run()` corpus branch (`if corpus:`) still returns unmeasured records before the `elif tool_present:` branch that calls `measure_case`, so the reject path spawns zero children. The corpus branch is reached before any `subprocess.run`.
4. **Fixture matrix (static, 12 files, 50 entries).**
   - Ids: 50 total, 50 unique across files.
   - Keys: only `name, names, envelope, expected_rejected`. `envelope` ∈ {array, object}; `expected_rejected` is boolean in every entry.
   - Invalid duplicate controls (`expected_rejected: true`): every one has stripped-unique ≥16 (16 for most; 32 for `DistantDuplicate.Array32…`). Under the pre-edit guard they would pass the `unique < 16` check, so they exercise the defect.
   - Valid controls (`expected_rejected: false`): stripped-unique equals the entry count in every case (16, 17, or 32), so none is a duplicate.
   - No blank or whitespace-only names. Whitespace/tab collisions (`WhitespaceCollision`, `TabCollision`, `PrependDuplicate-padded-…`, `TriplicateName-…strip_equivalent`) are the strip-collision class.
   - Cross-check with the repaired rule (`len(declared) != unique` on stripped names): all `expected_rejected: true` entries are rejected, and all `false` entries pass the duplicate check. This is a static trace; no runner was run.

## Findings (severity order)

### F1 — medium, repair in flight: duplicate guard (verify, do not assume closed)
- Pre-edit defect: `corpus_problems` (`.ufo/waves/round-14/measure.py` pre-edit `:350-362`) counted only distinct stripped names. A corpus with 17+ entries and 16 stripped-unique names was accepted and child-spawned.
- Current state: the 2-line repair closes the defect statically. Proof still needed from the harness: a red-before through the real CLI (`measure.py --tool <recording fake>`) with recorded child invocations = 0. That is pending check.py.
- Residual gap (low, not covered by any fixture): the duplicate check counts only non-empty string names after strip. A corpus with 16 unique names plus two blank or missing `name` fields passes the guard. Those cases run as `case-NN` fallbacks and reach child spawns. Suggest, if the owner agrees, counting blank/missing names as a corpus problem. Not required by the round-15 contract.

### F2 — low/medium: duplicate check disagrees between child-CLI selftest and runner
- `tools/kama-ollama-evidence.py` `run_selftest` (`:359-365`) checks duplicates on raw names (`case.get('name')`, no strip). The runner (`measure.py` `corpus_problems`) canonicalizes with strip. Two committed names `n00` and `n00 ` therefore pass the CLI selftest and fail the runner.
- Not triggered today: the committed cases.json has 51 distinct raw names, no whitespace collisions. The two gates can still disagree on the same file. Option: strip in the CLI too, or document the divergence. Note that editing the CLI changes `tool_sha256` recorded by every runner output.

### F3 — low: runner staging and parsing is laxer than the child CLI (oracle divergence)
- `measure.py` `load_cases` (`:115`) uses plain `json.loads`: NaN/Infinity accepted, duplicate keys silently last-wins. The CLI selftest rejects both for cases.json (`read_json_file`, `:164-165` with `_pairs`/`_constant`). Current cases.json is strict-clean, so no present divergence.
- `measure.py` `measure_case` child-stdout parse (`:269`) uses plain `json.loads`. The CLI emits strict JSON (`emit`, `allow_nan=False`, `:306-307`). A non-conforming child printing NaN or duplicate keys would be accepted by the runner.
- `write_capture` (`:189-196`) comment says "Byte-identical staging rule shared with the classifier's selftest." That is **inaccurate**: the runner uses `ensure_ascii=False` with no `allow_nan=False`; the CLI `_fixture_text` (`:310-313`) uses `ensure_ascii=True, allow_nan=False`. Same JSON semantics for valid input, not byte-identical.
- A lone-surrogate string in a fixture makes `write_text` raise `UnicodeEncodeError` (a `ValueError`, not `OSError`). `measure_case` only catches `OSError` (`:236`), so the whole run is aborted by `main`'s catch-all (fail closed), instead of one per-fixture `unsupported` record as the CLI selftest does (`fixture_write_failed`, `:390-392`).

### F4 — low: `--help` is not JSON in the runner
- `measure.py` `build_parser` (`:458-472`) keeps argparse's default `-h`. `Parser.error` is overridden, but `--help` raises `SystemExit(0)` that `main` does not catch (`:475-487`). Output is plaintext, not "one JSON object" as the module docstring states. The child CLI documents this exception explicitly (`:464-465`); the runner does not.

### F5 — info: child environment differs (not a defect)
- Runner child uses a minimal env (`child_environment`, `:199-208`, HOME/TMPDIR in case dir, stdin DEVNULL). CLI selftest children inherit the full environment and use cwd=case_dir (`:394-408`). The child runs under `-I -B`, which already ignores PYTHON* variables, so behavior is the same for the classifier. Recorded for completeness.

### F6 — info: no "import-only" selfcheck exists in the tree
- `tools/kama-ollama-evidence.py --selftest` spawns isolated child processes (`:394-408`) and never imports itself (docstring `:61-63`). The runner also spawns the child. Any future check that imports `corpus_problems` or `classify` directly would prove function logic only. It would not prove argv parsing, single-object stdout, exit-code mapping, the zero-child rule, or the tool sha. The R1 proof must go through `measure.py --tool <recording fake>`, not an import. Pending for check.py.

### F7 — info: "marker oracle" = fixed fixture literals + oracle sha
- The oracle is the literal `expected_exit` / `expected_finding` in cases.json, plus the cases.json sha `4a4de0…`. Round-14 already records these as "same-oracle checks, not two independent semantic or runtime authorities" (`corpus/lessons/round-14.md:140-142`). The runner's readiness/scope/schema checks (`measure.py:316-323`) mirror the CLI constants. This is consistent, not independent.

## Residual risk and verification gaps

- Harness not built: clone-from-first-case, `expected_rejected` assertion, `--only`, `--selftest`, and the zero-child red/green proof are all unobserved. Pending check.py.
- Fixture-level equality ("every fixture identical except names/envelope") depends on the harness; the fixture files alone cannot show it.
- Receipts that pin the round-14 `measure.py` sha (`.ufo/waves/round-14/*.json`) become stale once the repair lands. Flagged for the census owner, not reviewed here.
- F3 and F4 do not affect the current committed corpus; they are oracle-hygiene gaps in the runner.
- Static reasoning only. No measured results are asserted by this report.

## Report trailer

Report: .ufo/waves/round-15/build/advice/HarnessReview.md — read-only findings; pending items listed separately; no tests or harness runs executed; no tools installed.
