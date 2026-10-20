# Harness — round-14 offline evidence replay measurement

Report (lane-relative): `.ufo/waves/round-14/advice/Harness.md`
Owner: KamaR14.Harness (leaf). No subagent dispatch, no background jobs, no
sibling in-flight content reads, no commits.

## Owned artifact

- New `.ufo/waves/round-14/measure.py`: 491 lines, 17134 bytes,
  sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`,
  mode 755, stdlib-only Python 3.
- No other files written. This report is the only other artifact.

## Graded tuple (L1-expanded contract)

A fixture passes only when ALL six assertions hold for its child CLI run:

1. process exit code == fixture `expected_exit`;
2. parsed single-JSON-object `finding_id` == fixture `expected_finding`;
3. `schema` == `kama-ollama-evidence/v1`;
4. `verdict_exit` == the observed process exit code;
5. `readiness` == `unknown`;
6. `scope` == `offline-captures-not-runtime`.

Each mismatch is appended to the record's `reasons` as an explicit
expected-vs-observed string; a pass has an empty `reasons` list. Records retain
independent `expected_exit`/`observed_exit` and
`expected_finding`/`observed_finding`, plus `observed_schema`,
`observed_verdict_exit`, `observed_scope`, and the constant per-record
`readiness: "unknown"`. A parse failure or missing `finding_id` is a graded
failure, never a pass.

## Corpus gate

Before any child runs, `cases.json` must declare at least 16 unique case names
(stripped, exact/case-sensitive). Below that floor, no child is spawned; every
fixture is recorded failed with a `corpus:` reason, `total` remains the fixture
count, `passed` is 0, exit is 1, and a top-level `error` names the shortfall.
The run reports `unique_case_names` and `minimum_unique_cases` (16). Fixtures
reported landing 49 objects with unique `[a-z0-9_]` names; the harness will
recompute the count from the committed file at L1 run time rather than trusting
that report.

## CLI and staging

Defaults resolved from the script location (lane root is
`Path(__file__).resolve().parent.parents[2]`):

- `--tool` default `<lane>/tools/kama-ollama-evidence.py`
- `--cases` default `<lane>/tests/ollama-evidence/cases.json`

One JSON object on stdout under harness schema `kama-round-14-measure/v1`
(never the domain schema), with `total`, `passed`, `failed`, `records`,
`verdict_exit`, plus `scope`, `readiness`, `tool`, `tool_present`,
`tool_sha256`, `cases`, `cases_sha256`, `child_command`, `timeout_seconds`,
`unique_case_names`, `minimum_unique_cases`, `limits`, and `error` only on
top-level/corpus failure. Exit 0 only when at least one fixture exists and every
record passed; otherwise exit 1; no timestamps, no liveness inference.

Per run: one `tempfile.TemporaryDirectory()`; per fixture an integer-only
subdirectory `NN/` (case `name` is evidence text, never a path component).
`tags.json` and `ps.json` paths are always passed; a null/absent value creates no
file (nonexistent temp input) while the flag remains present; a JSON string is
written verbatim (empty/malformed/duplicate-key bodies); any other JSON value is
written as `json.dumps(value, ensure_ascii=False) + "\n"`. Child argv is a list
`[sys.executable, "-I", "-B", <tool>, "--tags", <tmp>, "--ps", <tmp>,
"--expect", <expect>]`, `shell=False`, cwd the case directory, minimal env
(`PATH`, `HOME`/`TMPDIR` in the case dir, `LC_ALL=C.UTF-8`), 30 s timeout.

## Absent-tool / fail-closed paths

- `--tool` not a regular file: nothing is spawned, `tool_present=false`,
  `tool_sha256=null`; after the corpus gate, every valid fixture records
  `observed_exit=null`, `observed_finding="unsupported"`, `reasons=["tool
  absent: <path>"]`, `passed=false`. Thus `total=len(cases)`, `passed=0`,
  `failed=total`, exit 1: the L1 before-run measures "0 supported" by
  construction, not an old classifier result. No fallback classifier exists in
  the file (no kama-probe import/exec, no domain logic).
- Child timeout or `OSError` on spawn: `unsupported` failure for that fixture.
- Missing/unreadable/non-UTF-8/invalid cases JSON: one JSON error object,
  `total=0`, exit 1.
- Invalid fixture definition (non-string `expect`/`expected_finding`,
  non-integer or boolean `expected_exit`): failed `invalid fixture` record with
  a reason; never skipped.

## Safety / read-only properties

Cases are read only; the tool is only `Path.is_file()`-tested and hashed, never
created/chmod/touched; all writes stay inside the disposable temp tree plus the
stdout JSON; argv is a list with `shell=False`; `-I -B` prevents env/user-site
and bytecode writes; the tool is never imported; no network use; diagnostic
tails are bounded to 600 chars and contain no fixture bodies beyond a failing
child's own echo.

## Evidence retained / not run

Consulted statically: round-14 `spec.json` item contract, prior lane
`.ufo/waves/round-13/measure.py` for exit/JSON/error conventions, and the wave
registry listing. Per contract I did not read sibling in-flight file contents;
the Fixtures landing details above arrived by peer message and are treated as
reported, not measured. At first write time both were still pending; the cases
file is now reported landed, while the classifier tool was not independently
confirmed and is measured only by the L1 run.

Per lane contract this seat ran no builds, tests, formatters, or smoke runs. L1
owns post-integration execution. Recommended commands (not executed here, run
from the lane root):

1. `python3 .ufo/waves/round-14/measure.py --tool .ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py`
   — expect exit 1, `total` = fixture count, `passed` 0, `failed` = total,
   every record `observed_finding: "unsupported"` and a tool-absent reason.
2. `python3 .ufo/waves/round-14/measure.py` after the tool lands — expect exit 0
   only if all six assertions hold for all fixtures, same `cases_sha256` as
   run 1.

## Limits / risks

1. The six-field gate now assumes the classifier emits `schema`,
   `verdict_exit`, `readiness`, and `scope` on every exit path including
   invalid input; that is its stated contract, and the Classifier selftest was
   asked to assert the same tuple.
2. A caller-supplied tool that deliberately fabricates all six matching fields
   cannot be distinguished by any runner; fixtures remain the reference cases.
3. `expected_exit` accepts any integer literally (domain fixtures use 0|1|2).
4. Fixed 30 s per child; no per-case override.
5. Relative `--tool`/`--cases` resolve against the invoking cwd.
6. String fixture values are raw bytes; structured values are re-serialized
   (semantically identical JSON).
7. Duplicate fixture names are allowed as long as the unique-name count meets
   the 16 floor; temp dirs are index-keyed.
8. The schema/readiness/scope assertions are interface-scope assertions, not
   evidence of device readiness or liveness; readiness stays unknown.

## Tooling

No installs or upgrades; nothing needed beyond system Python 3 stdlib.
