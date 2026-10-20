# FalsifyMiddleDuplicate: scoped attack on tests/ollama-corpus-guard/MiddleDuplicate.json

Scope: fixture correctness, envelope/expected correspondence, and the runner predicate that decides
rejection. Read-only. No gate, test, or runner execution. Tooling: none installed (metadata grep of
the host libpython only).

## Verdict

No fail finding. The fixture meets every attacked property, and the runner's rejection path returns
before any child process is created. Two residual, non-fixture gaps are recorded below.

## Fixture facts (tests/ollama-corpus-guard/MiddleDuplicate.json#9C90)

| test | envelope | expected_rejected | len(names) | distinct stripped | duplicate |
|---|---|---|---|---|---|
| MiddleDuplicate-inserted-mid-array | array | true | 17 | 16 | `n07` at index 7 and 12 |
| MiddleDuplicate-inserted-mid-object | object | true | 17 | 16 | `n07` at index 7 and 12 |
| MiddleDuplicate-duplicate-removed-array | array | false | 16 | 16 | none (`n00`..`n15`) |
| MiddleDuplicate-duplicate-removed-object | object | false | 16 | 16 | none (`n00`..`n15`) |

- Duplicate is truly present after strip in both rejected entries. No whitespace variants.
- Valid controls are exactly `n00`..`n15`, 16 distinct. None of the names collide with another file's test id (grep of `"name"` across tests/ollama-corpus-guard shows only this file's own ids).
- Envelope and boolean correspondence is correct: rejected entries are the only ones with a repeated name; each valid control matches its envelope.
- Rejected corpora sit at exactly 16 distinct. The loader minimum (`check.py:194`) passes at the boundary, and the runner minimum (`measure.py:360`, `unique < 16`) does not fire. So the rejection is attributable to the duplicate guard alone, which is the stated purpose of the boundary.

## Predicate walk (fail-closed check)

Loader (`check.py:192-211`): strips names, requires distinct >= 16, requires `expected` true iff `distinct != len(stripped)`. All four entries pass.

Runner (`round-14/measure.py`):
- `corpus_problems` (350-364): `declared` = stripped non-empty string names; `len(declared) != unique` appends `duplicate case names`. For MiddleDuplicate rejected: 17 != 16, flagged.
- `run` (367-385): corpus check runs before the `elif tool_present:` branch that calls `measure_case`, so the rejected path creates zero child processes. Every record is `unmeasured_record` with `observed_exit` None (count 17).
- `main` (477-489): one JSON object on stdout; exit 1 on verdict.

Grader rejected branch (`check.py:528-575`): exit 1, verdict 1, error contains `duplicate case names`, passed 0, failed 17, total 17, tool_present true, null-exit records 17, marker count 0, audit process events 0, Popen events 0. Each is satisfied by the corpus-return path above.

Valid branch (`check.py:577-604`): exit 0, passed 16, failed 0, total 16, marker 16, Popen 16. `measure_case` launches exactly one `subprocess.run` per case (`measure.py:240`), so Popen count equals 16.

Mutation reasoning (no execution): if the guard were removed, the rejected grade fails on marker 17 != 0 and exit 0 != 1. If the guard fired after launch, marker > 0 fails. If the guard over-rejected, valid controls fail on exit 1. Each defect class is detected by the fixture.

## Residual gaps (non-blocking; no fixture change requested)

1. **Audit surface excludes `os.spawn*`.** `PROCESS_EVENT_PREFIXES` (`check.py:79-85`) is `subprocess.Popen`, `os.system`, `os.posix_spawn`, `os.fork`, `os.exec`. A grep of the host libpython (`/usr/lib/libpython3.14.so.1.0`, `python3.14`) finds audit literals `os.exec`, `os.fork`, `os.forkpty`, `os.posix_spawn` and no `os.spawn*` literal. [INFERENCE] `os.spawnv`-style launches are not audited on this interpreter, so a regressed runner that spawned the real classifier through `os.spawn*` (bypassing the wrapper marker) would pass the rejected grade. This is outside the committed runner and the harness's own LIMITS disclaim malicious-runner coverage; recorded as a bounded hole, not a fixture defect.
2. **Empty-name mismatch between loader and runner.** The loader counts `""` as a distinct stripped value (`check.py:192-193`); the runner excludes empty names from `declared` (`measure.py:353-355`). Any corpus where `""` is the sole duplicate would be a loader-declared rejected control that the runner accepts. The grader then fails closed (marker > 0 or exit mismatch). No false pass, but the two predicates disagree. Not exercised by MiddleDuplicate.
3. **Position coverage is redundant, not additive.** The runner is set-based, so the mid-position duplicate exercises the same branch as the adjacent, prepend, and append fixtures. It adds coverage of the envelope and boundary (17 entries, exactly 16 distinct), not of a new code path.

## Verification gaps

- No runtime execution performed, per assignment. All predicate conclusions are from source reading and reasoned against the grader.
- Template validity (`load_template`, `tests/ollama-evidence/cases.json`) assumed; it governs valid-control pass, not the rejected path.
