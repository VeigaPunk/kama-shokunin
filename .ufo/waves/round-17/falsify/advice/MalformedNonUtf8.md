VERDICT: partial — all six assigned payloads fail per row, but decoder-limit exceptions still abort the matrix.

# Scope
Attacked C1 malformed/non-UTF-8 handling in `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py` at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. All executions used a `/tmp` clone and one `--only` closed-port matrix row to exercise output grading without a stub-request short circuit. No lane files other than this report were written. No tools were installed or updated.

## Finding — Medium: JSON decoder exceptions outside `JSONDecodeError` escape the row handler

`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:388-391` wraps `json.loads(stdout)` with only `except json.JSONDecodeError`; the docstring at `:385-386` says malformed output is recorded “per-row failure, never a traceback.” `grade()` calls this parser at `:460`, while `main()` catches only `HarnessError` around the complete record list at `:643-647`; JSON is emitted only after that list completes at `:666-669`.

Two additional decoder-boundary probes escaped this path. A JSON document containing 60,000 nested arrays raised `RecursionError: Stack overflow ... while decoding a JSON array`; a JSON document containing a 5,000-digit integer raised `ValueError: Exceeds the limit (4300 digits) ...`. In both cases check.py exited 1 with empty stdout, non-JSON output, and a traceback on stderr instead of a parseable per-row failure. This can abort the whole matrix before its results document is emitted. The F8 table in `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:166-187` covers selected malformed forms, null, and non-UTF-8, but not these decoder-limit exceptions.

## Assigned payload results

Each run selected `AuthAndDead.closed-port-connection-refused`; the wrapper emitted the listed stdout and returned normally. For all six assigned cases: check.py exit 1, outer JSON parsed successfully, one record with `failures=1` and `passed=false`, and no traceback. Each record contained a non-empty `error` describing the output problem.

| Wrapper output | Observed per-row error |
|---|---|
| Non-UTF-8 bytes `ff fe 80` | `stdout is not JSON` (strict decode marker then JSON parse failure) |
| `{"rows":[null]}` | `rows[0] is NoneType, not an object` |
| `{"rows":["x"]}` | `rows[0] is str, not an object` |
| `{"rows":[{"verdict":1}]}` | `rows[0].verdict is not a string` |
| 2,000,000 `x` bytes | `stdout is not JSON`; outer record stayed parseable |
| Valid JSON followed by a second JSON document | `stdout is not JSON (Extra data: ...)` |

Additional decoder-boundary probes (not part of the six requested cases):

| Wrapper output | Observed check.py result |
|---|---|
| `{"rows":` + 60,000 `[` + `1` + 60,000 `]` + `}` (120,010 bytes) | Exit 1; stdout empty; traceback with `RecursionError` |
| `{"rows":[` + 5,000 `9` digits + `]}` (5,011 bytes) | Exit 1; stdout empty; traceback with `ValueError` (4,300-digit conversion limit) |

## Commands and verification

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.MalformedNonUtf8-clone && git -C /tmp/KamaR17.MalformedNonUtf8-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.MalformedNonUtf8-clone log -1 --oneline` — exit 0; HEAD was the assigned commit.
- For each mode in `nonutf8`, `null`, `string`, `verdict-int`, `two-megabytes`, `trailing-json`, `deep-nesting`, and `huge-integer`, ran the following command with the corresponding `MODE` value; stdout/stderr were captured in `/tmp/KamaR17.MalformedNonUtf8-<mode>.json` and `.stderr`, and the check.py exit code was captured immediately after it:

  `MODE=<mode> PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.MalformedNonUtf8-clone/tests/probe-verdicts/check.py --only AuthAndDead.closed-port-connection-refused --probe /tmp/KamaR17.MalformedNonUtf8-probe.sh --json`

  The six assigned modes each returned check.py exit 1 with parseable JSON and a failed row; the two additional modes each returned check.py exit 1 with empty stdout and a traceback. A Python JSON postprocessor exited 0 for each assigned-case output and verified `tests=1`, `failures=1`, `passed=false`.
- Setup correction: the first wrapper revision expected `MALFORMED_MODE` while the initial invocations supplied `MODE`; those attempts exited 1 before emitting test payloads and were discarded. The wrapper was corrected to consume `MODE`, then all listed cases were rerun. Results above are only from the corrected runs.
- LSP review unavailable: `read xd://lsp` returned “No such tool” and the mounted-device list did not include LSP; no LSP status, references, definition, or diagnostics were available. Source evidence was read directly and behavior was exercised end-to-end in the clone. No full fault-controls suite, build, or lint was run; this review was limited to the assigned probes and the two additional decoder-boundary probes.
