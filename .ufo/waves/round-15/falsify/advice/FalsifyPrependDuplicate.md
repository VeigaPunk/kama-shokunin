# FalsifyPrependDuplicate: round-15 attack on tests/ollama-corpus-guard/PrependDuplicate.json

Scope: reading only. No checks, tests, builds, or child processes run. Tools used: read, glob, grep, one read-only binary string scan. No installs (pacman paused host-wide per operator ruling; none attempted).

## Verdict

No fail finding. The fixture meets the stated contract, and the runner predicate in `.ufo/waves/round-14/measure.py` rejects duplicate corpora before any child process is spawned.

## Fixture evidence (PrependDuplicate.json, lines read 1-120)

| test id | envelope | raw entries | distinct stripped | duplicate present | expected_rejected | correspondence |
|---|---|---|---|---|---|---|
| PrependDuplicate-array | array | 17 (n15 at idx 0 and 16) | 16 | yes | true | OK |
| PrependDuplicate-object | object | 17 (n15 at idx 0 and 16) | 16 | yes | true | OK |
| PrependDuplicate-padded-strip-collision | array | 17 ("  n15  " at idx 0, "n15" at idx 16) | 16 | yes, only after strip | true | OK |
| PrependDuplicate-valid-unique-array | array | 16 (n00..n15) | 16 | no | false | OK |
| PrependDuplicate-valid-unique-object | object | 16 (n00..n15) | 16 | no | false | OK |

- Every rejected entry has at least 16 distinct stripped names, so the minimum-corpus guard does not fire. The rejection can only come from the duplicate guard.
- Every valid control has exactly 16 entries, all distinct, so it satisfies the minimum without duplicates.
- Envelopes are only `array` or `object`, and `expected_rejected` is a JSON boolean on all five entries. The JSON structure of each object is complete (name, names, envelope, expected_rejected).
- Test ids are unique across all matrix files. The `PrependDuplicate-` prefix appears only in this file (grep over tests/ollama-corpus-guard).

## Harness load-time predicate (check.py load_matrix, lines 192-211)

- Stripped distinct count is computed with `str.strip()`. Expected true requires `distinct != len(stripped)`. Expected false requires `distinct == len(stripped)`. All five fixtures pass this predicate.
- The `distinct < 16` rejection cannot mask any PrependDuplicate case, because every entry has 16 or more distinct names.

## Runner predicate (round-14 measure.py)

- `load_cases` (109-128): accepts bare array or `{"cases": [...]}`. The `object` envelope that check.py emits is therefore accepted by the runner's envelope handling.
- `corpus_problems` (350-364): declares `name.strip()` for string names with non-empty strip. It reports `duplicate case names` when `len(declared) != len(set(declared))`, and `unique < 16` as a separate problem. For each PrependDuplicate rejected fixture it produces exactly `duplicate case names`.
- `run` (367-425): calls `corpus_problems` before the `tool_present` branch. When corpus problems exist, every record is an `unmeasured_record` with `observed_exit: None` and no `measure_case` call is made. No `subprocess.run` occurs on this path. Only `load_cases` and `tool.is_file()`/`sha256_file` run before it, and neither spawns a process.
- `main` (477-489): a corpus rejection yields `verdict_exit` 1, so process exit is 1. The error string contains `duplicate case names`, which check.py's `DUPLICATE_REASON` requires.

## Grader predicate (check.py grade, lines 478-624)

- Rejected branch requires: exit 1, verdict_exit 1, error includes `duplicate case names`, passed 0, failed = total = len(names), total = len(names), tool_present True, `observed_exit` null count = total, marker count 0, audit process events 0, audit Popen events 0. The corpus branch of the runner satisfies each of these by construction, since every record has `observed_exit: None` and `passed: False`.
- Accepted branch requires exit 0, passed = total, marker count = total, Popen count = total. This depends on the classifier and template behaving as expected; it is not a PrependDuplicate-specific defect.

## Audit surface cross-check (read-only)

- The PROCESS_EVENT_PREFIXES tuple (`subprocess.Popen`, `os.system`, `os.posix_spawn`, `os.fork`, `os.exec`) was compared with the audit-event strings present in the local CPython 3.14 build. A byte scan of `/usr/lib/libpython3.14.so.1.0` shows `os.exec`, `os.fork`, `os.forkpty`, `os.posix_spawn`, and `os.system`. `/usr/lib/python3.14/subprocess.py` lines 1549 and 1858 call `sys.audit("subprocess.Popen", ...)`. No `os.spawn*` audit string exists in this build, so the prefix list matches the real process-creation audit surface.

## Residual notes (outside this fixture; not fail findings)

1. Unnamed or blank-named cases are excluded from `corpus_problems`' declared set, and their record name falls back to `case-NN`. A corpus that names one case literally `case-03` and leaves the case at index 3 unnamed would produce two records named `case-03` with no duplicate error. No matrix entry in the committed corpus-guard directory exercises this. Recorded as a bounded observation, not a requested feature.
2. The audit prefix list is the only process-creation observation. It depends on Python's audit events. A non-audited spawn path (for example, a C extension calling `fork` directly) would not be observed. check.py's LIMITS already states this.

## Verification gaps

- Nothing was executed. The fixture was verified by reading lines 1-120 and by grep of the matrix directory. The JSON well-formedness of PrependDuplicate.json is inferred from the visible structure, not from a parser run; L1 should confirm it when running the gate.
- The valid-control acceptance path depends on the classifier and template fixture behaving as expected. This report does not assess that.

## Tool/install record

None. No installs or updates were performed, and pacman was not invoked.
