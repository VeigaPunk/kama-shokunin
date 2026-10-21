# CritExit — round 22 critic: exception class → verdict class for C1

Seat: KamaR22.CritExit (read-only critic). Owned path: this file only. No clone, no edits, no
verification runs, no installs. Dimension: an exception during install identity must yield
*refusal* (subject) or *could-not-evaluate* (harness), never a failed verdict by accident and
never a silent equal digest credited as anything.

Sources read: `tools/kama-llamacpp-live.py` at master 10271460 (lines 154-159 `SetupError`,
178-202 `install_tree`, 213-262 `install_links`, 933-952 `_outcome_exit`/`_record_internal`,
1135-1199 identity selftest, 1330-1340 selftest exit, 1413-1419 main consumer, 1602-1607 catch);
`tests/llamacpp-live/install-links-grid.py` (whole); `tests/llamacpp-live/unpinnable-e2e.py`
(whole); `corpus/QUALITY.md` KQ25; `corpus/lessons/round-21.md` lines 80-108;
`.ufo/waves/round-22/build/advice/SrcExceptions.md`.

## F1 — "returned normally" with an undelivered fault is credited as frozen escape (false red-before)

Counterexample: the matrix patches `os.lstat`/`sha256_file`, but the patch target is not the one
the arm resolves (for example `install_tree` reads `os` from the exec'd module's globals, or
ApiFix inlines the read so `module.sha256_file` is never called). The frozen arm then returns the
complete control tuple. If "escape" means "returned without raising under a fault row", that row
credits red-before without any fault having happened. The same blind spot makes current look
like an escape, which is a false red, the opposite direction.

Silent equal digest is also a real escape, not only an artifact. Frozen `install_tree`
lines 190-193 `continue` on an lstat fault for a *symlink or subdirectory* entry. The entry
would have been skipped anyway, so the returned digest is **byte-equal to control**, while
identity was computed without knowing the entry's type. A matrix that defines escape as
`digest != control` scores this row "no escape" for frozen. It would then also accept a current
arm that keeps swallowing it.

Rejection condition (falsifiable): any fault row whose outcome is credited (as escape or as
refusal) when the injector's call log shows zero raises at the target `(op, path)`. Also any
escape predicate that compares digests instead of "returned normally after ≥1 delivered fault".

Minimum remedy:
- Every fault row records `delivered = count of injected raises at (op, path)`.
- `delivered == 0` is outcome `not-delivered`, which is could-not-evaluate (exit 2) for that arm.
- Escape is "returned a tuple after delivered ≥ 1", with a subtype:
  - `partial` when the map is missing members,
  - `empty-null` for `({}, None)`,
  - `equal-digest` when the tuple equals control.
- All three subtypes count as escapes. `({}, None)` is not a refusal.
- Include lstat-fault-on-symlink and lstat-fault-on-subdirectory rows, both expected `refusal`
  for current.

## F2 — any `SetupError` (or any exception) credited as refusal lets always-refuse pass

Counterexample (KQ25 "always-error classifier"): a current arm whose `install_tree` raises
`SetupError('install-tree-unpinnable')` unconditionally, or wraps `except Exception`, scores
100% refusal on every fault row. The same holds if the fixture accidentally contains a FIFO or
the mock raises `TypeError` inside the call. The positive control catches the unconditional
mutant, but only for the whole run. The `except Exception` mutant passes the control and still
turns mock or programming errors into "refusal" per row.

Rejection condition: a fault row is credited `refusal` without either (a) the injected exception
instance on the `SetupError`'s `__cause__`/`__context__` chain, or (b) reason detail naming the
injected `(op, name)`. Also: `install_tree` catching anything broader than `OSError` (SrcExceptions
item 1 agrees).

Minimum remedy:
- **Matrix:** credit refusal only when all three hold:
  - the exception is the producer module's own `SetupError` class (`module.SetupError`, not a
    re-imported or name-matched copy),
  - its `code` starts with `install-tree-unpinnable`,
  - the injected instance is on its exception chain.
- **ApiFix:** raise inside the `except OSError as exc:` block or use `raise ... from exc`, so the
  chain survives. If problems are aggregated and raised after the loop, the chain is lost and a
  correct fix gets no credit.
- **Matrix classification of other outcomes:**
  - An exception that *is* the injected `OSError` (raw leak) is a subject contract violation:
    verdict, exit 1.
  - Any other exception type raised during the call is could-not-evaluate (exit 2). That covers
    `TypeError` and `AttributeError` from the mock, and `UnicodeEncodeError`, which belongs to
    UnicodeNames.

## F3 — code token without `:` splits an existing prefix contract

The shared interface names the token `SetupError('install-tree-unpinnable')`. Existing consumers
key on the colon form:
- the producer main path raises `'install-tree-unpinnable:' + ';'.join(problems)` (line 1418);
- `unpinnable-e2e.py:91` requires `setup.startswith("install-tree-unpinnable:")`.

A bare token would be a genuine refusal that any colon-prefix consumer scores as "not refused"
(exit 1, a failed verdict). Today it is latent, because no e2e case reaches `install_tree`'s
fault paths. It becomes live the moment a case does.

Rejection condition: any consumer whose refusal predicate is false for the code `install_tree`
emits.

Minimum remedy: emit `install-tree-unpinnable:<op>:<name>:<errno-name>`, for example
`install-tree-unpinnable:lstat:libllama.so.0:EIO`.
- Take the errno name from `errno.errorcode.get(exc.errno)`, with fallback `type(exc).__name__`.
- Do not use `exc.strerror`: SrcExceptions item 3 shows it is None for `OSError('msg')`.

This keeps one prefix authority, and F2's option (b) comes for free.

## F4 — the existing callers turn a correct refusal into could-not-evaluate or a raw traceback

Both are CallerRepair's paths:

- **`install-links-grid.py`:**
  - `identity()` (line 177) calls `install_tree` unguarded.
  - The `regular-unreadable` cell (line 169, `chmod 0`) is exactly a member-read fault.
  - After the fix, `SetupError` escapes `run()` and lands in `main`'s `except Exception` (line 389).
  - Result: the *whole grid* exits 2 instead of the row reading `current=changed+refused`.
  - `--selftest` runs the same cell through an unwrapped `run()` (line 332), so it also goes
    0 → 2.
  - A genuine verdict is erased into could-not-evaluate: the regression KQ25 forbids ("an error
    remains visible and non-passing" cuts both ways; a refusal must stay a verdict).
  - Rejection condition: `--arm current` or `--selftest` exits 2 on a tree where the only fault is
    the grid's own `regular-unreadable` mutation.
  - Remedy:
    - In `identity()`, catch exactly the producer's `SetupError` with an
      `install-tree-unpinnable` prefix and return an identity carrying the refusal code
      (`changed=True`, `refused=True`).
    - Keep `EvalError` for the real/mirror baseline (lines 216-218 and 233 semantics unchanged:
      an unpinnable *real* tree stays exit 2).
    - Catch nothing else.

- **`unpinnable-e2e.py:73`:**
  - The pristine `install_tree` call sits under `except (OSError, RuntimeError, ValueError,
    TimeoutExpired)` (line 106).
  - `SetupError` is none of these, so it exits as an uncaught traceback. Python uses exit 1 for
    that, the file's "a case launched or was not refused" code.
  - Rejection condition: a pristine-copy `SetupError` yields exit 1 or a traceback.
  - Remedy: treat `producer.SetupError` from the pristine scan as a failed precondition, exit 2,
    with the code printed. Leave the existing pristine-`problems` → exit 1 behavior untouched,
    since it is legacy semantics outside C1.

## F5 — calibration scope: the frozen *main consumer* is already mostly fail-closed

Frozen main passes `tree` into `install_links` (line 1415). `install_links` flags every regular
member absent from `tree` as `not-hashed`, or as `unreadable` via `os.access` (lines 256-259).
So at frozen, listdir, lstat-on-regular and read faults injected *only* into `install_tree` are
already refused by main.

Main-path frozen escapes reduce to install_tree-only lstat faults on symlink or subdirectory
entries (F1's equal-digest rows) and transient faults that `install_links` does not re-hit. That
statement is [INFERENCE] from code reading, not run.

The raw-`install_tree` consumers have no such backstop: `install-links-grid` frozen/current
`identity()`, the `unpinnable-e2e` pristine scan, and the selftest at line 1135.

Rejection condition: L1 or a report states "before, consumers silently accept partial identity"
from function-level matrix rows without separating it per consumer.

Remedy: report red-before at the `install_tree` API level, and list each consumer separately with
its own before-state. Main-path red covers only the equal-digest rows.

## F6 — exit precedence and global mocks

- **Precedence:** pin one documented order: any could-not-evaluate row → exit 2; else any escape
  or contract violation → 1; else 0.
  - Counts are always printed, so a higher-precedence 2 does not erase a verified escape count
    (KQ17 wording).
  - The frozen arm's red-before is the expected exit 1 *with zero* could-not-evaluate rows.
- **Global patching:** patching the process-wide `os.lstat`/`os.listdir` also hits
  `tempfile`/`shutil.rmtree` cleanup and the harness's own setup. A harness exception there must
  be exit 2, never credited.
  - Remedy: inject through the exec'd module's globals (a module-scoped `os` proxy plus
    `module.sha256_file`) and filter on exact `(op, path)`.
  - Positive control: run once with the proxy armed for a path that does not exist. It must return
    the pinned control tuple and record `delivered == 0`, proving pass-through is exact.
- **Selftest mutants the matrix must score:**

  | Mutant | Required matrix exit | Finding |
  |---|---|---|
  | always-refuse | 1 | control mismatch |
  | `except Exception` widening, fed an injected `TypeError` | 2, not refusal | F2 |
  | raw-`OSError` leak | 1 | F2 |
  | undelivered-patch | 2 | F1 |
  | frozen-blob unavailable | 2 | — |

## Impacted axes

- operability8 (axis7, assigned): a refusal must be an actionable reason token on exit 2.
- Measurement integrity: escape/refusal credit (F1, F2, F6).
- No-harm: F4, the existing grids regressing to 2 or to a traceback.
- Calibration honesty: F5.

These are fixable defects in the proposed approach, not tradeoffs the judge must reject, provided
the remedies land in the owning seats' files.

## Owned paths (who must change what)

- `tools/kama-llamacpp-live.py` (ApiFix):
  - catch only `OSError`;
  - raise inside the `except` or use `from exc`;
  - emit the colon-form code with op, name and errno name.
- `tests/llamacpp-live/install-io-grid.py` (Matrix):
  - add a delivery log;
  - use the escape subtypes, chain-tied refusal credit, the outcome classes, the pinned
    precedence and the module-scoped injection;
  - add the selftest mutants.
- `tests/llamacpp-live/install-links-grid.py` and `tests/llamacpp-live/unpinnable-e2e.py`
  (CallerRepair): the narrow `SetupError` handling in F4.
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/CritExit.md`.

## Proposed checks (for L1 after integration; not run here)

- `python3 tests/llamacpp-live/install-io-grid.py --selftest`
- `python3 tests/llamacpp-live/install-io-grid.py --arm both --json`
  - frozen: exit 1, no could-not-evaluate rows;
  - current: 0.
- `python3 tests/llamacpp-live/install-links-grid.py --selftest`: 0.
- `python3 tests/llamacpp-live/install-links-grid.py --arm current`: 0, with
  `regular-unreadable` showing `current=changed+refused`.
- `python3 tools/kama-llamacpp-live.py --selftest`: 0.

## Tooling

No installs or updates. Tools used: file reads, ripgrep, `git log`/`git status`, `sed`.
