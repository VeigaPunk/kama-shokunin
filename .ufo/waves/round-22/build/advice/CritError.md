# CritError — round 22 C1 critic: which exceptions install identity may catch

Seat: KamaR22.CritError (read-only critic). Owned path: this file only. I made no edits, ran no verification and installed nothing.
Dimension: `BaseException` versus `OSError`. A fail-closed `install_tree` must turn I/O failures into a refusal, but it must not catch operator interrupts or programming faults.

## Evidence read

- Frozen `tools/kama-llamacpp-live.py` at `10271460` (lane HEAD = master), lines 154–202. `SetupError(Exception)` is at 154 and `Terminated(Exception)` at 162. `install_tree` has three `except OSError` sites: `listdir` returns `{}, None`, while the `lstat` and `sha256_file` sites `continue`.
- The producer calls it at lines 1413–1419. The SIGINT/SIGTERM/SIGHUP handlers that raise `Terminated` are installed only at 1466–1470, after `install_tree`. So a Ctrl-C during `install_tree` arrives as the built-in `KeyboardInterrupt`, which is a `BaseException` and not an `Exception`.
- The outer handlers at 1602–1607 map `except SetupError` to `setup_error=<code>` and `except BaseException` to `_record_internal`, which gives `internal:<Type>`. Both exit 2. The selftest (1264–1271) and controls `k18` pin `internal:KeyboardInterrupt` as the interrupt token.
- `_emit` uses `json.dumps(..., ensure_ascii=True)` (1308), so a reason code holding a member name cannot break the receipt.
- Lessons and quality: `corpus/lessons/round-21.md` (C2 fail-closed install identity), `corpus/QUALITY.md` round-21 row ("a skipped unreadable member"), and S051 (which exceptions escape `except Exception`). Also `advice/SrcExceptions.md` (OSError maps errno to a subclass; EIO stays plain `OSError`).

## Contract breach observed (for L1)

The lane checkout is dirty, which repeats round-21 M4. `git --no-optional-locks status --porcelain` shows uncommitted edits to `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/install-links-grid.py`; the file has 1791 lines against 1790 in the frozen blob. The `install_tree` diff replaces each site with `raise SetupError('install-tree-unpinnable:{listdir|lstat:<name>|read:<name>}') from exc`. The grid diff makes `identity()` catch `module.SetupError`. I don't know who wrote them; it was not this seat. L1 must revert these edits and attribute them before integrating. The review below covers both the frozen code and this draft.

## Finding

On this dimension, the draft is correct. It catches exactly `OSError`, so `KeyboardInterrupt`, `Terminated`, `TypeError`, `AttributeError`, `ValueError` (including `UnicodeEncodeError` from the `.encode()` on a surrogate-escaped name) and `MemoryError` all propagate to the outer `BaseException` handler. That handler emits a receipt with `internal:<Type>` before any launch. The grid catches `module.SetupError`, which is the exact class of the loaded module, and not `Exception`.

The risk is a later "fail closed harder" move. Three plausible ones would each be a regression with false provenance:

| Mutant | What it does to a Ctrl-C or a programming fault inside `install_tree` | Impacted axes |
|---|---|---|
| `except BaseException` or bare `except:` → `SetupError` | `KeyboardInterrupt` and `SystemExit` become `install-tree-unpinnable:…`. The operator's interrupt is reported as a bad install directory, and the k18 token `internal:KeyboardInterrupt` is lost for that window. | operability, calibration |
| `except Exception` → `SetupError` | `TypeError`, `AttributeError` or `NameError` from a refactor, a `ValueError`, or `Terminated` (an `Exception` subclass, reachable if the handlers are ever installed earlier) become "unpinnable". An internal fault is filed as host evidence about the directory. | calibration, provenance |
| Caller catches `Exception`/`BaseException` around `install_tree` (grid, e2e or matrix) | Any crash counts as a green "refusal". The red-before/green-after count inflates with faults that are not refusals. | calibration (measurement) |

None of these changes the exit code, because every path exits 2. An exit-code-only oracle therefore cannot tell them apart; only the `setup_error`/`internal_fault` token and the propagated exception type can.

### Strongest local counterexample

Replace the `lstat` site's `except OSError` with `except Exception`, then inject `side_effect=TypeError` into `os.lstat`.

- Draft (correct): the receipt shows `setup_error=internal:TypeError` with `internal_fault` set.
- Mutant: the receipt shows `setup_error=install-tree-unpinnable:lstat:<name>` with `internal_fault` absent, and the exit is still 2.

Any matrix that only tests OSError rows passes both versions. The finite matrix as currently described ("precise stdlib/sha256_file failures") has no row that kills this mutant. [INFERENCE: Matrix's `install-io-grid.py` does not exist yet in any sandbox, so I am judging the spec, not code.]

## Falsifiable rejection condition

Reject C1 if any of the following holds for the current arm:

1. **Interrupt row.** Injecting a `KeyboardInterrupt` instance as `side_effect` on `os.listdir`, on `os.lstat`, or on the module-global `sha256_file` while `install_tree` runs must propagate the same instance (`is`, not merely `isinstance`). C1 fails if `install_tree` returns, raises `SetupError`, or wraps the interrupt in an exception whose `__cause__` is it.
2. **Programming-fault row.** The same three sites with an injected `TypeError` must propagate it unchanged. C1 fails if it becomes `SetupError` or a return value.
3. **OSError row (the claim itself).** At each site, `OSError(errno.EIO, os.strerror(errno.EIO), path)` and `PermissionError`/`FileNotFoundError` built with the three-argument form must raise `module.SetupError` with `.code` starting `install-tree-unpinnable`. C1 fails if an unmapped errno (EIO) escapes raw, because that means the catch was narrowed to named subclasses.
4. **Producer end to end.** In one in-process producer run, a `KeyboardInterrupt` injected into `install_tree`'s `os.lstat` must yield `setup_error == 'internal:KeyboardInterrupt'` with `internal_fault` set. An injected `OSError(EIO)` must yield `setup_error` starting `install-tree-unpinnable` with no `internal_fault`. C1 fails if the two tokens are swapped or equal.
5. **Caller discipline.** C1 fails if any C1 consumer (`install-links-grid.py identity()`, `unpinnable-e2e.py`, `install-io-grid.py`, the producer `_selftest`) catches `install_tree` failure with `except Exception`, `except BaseException` or bare `except:` instead of `module.SetupError`.

Rows 1 and 2 behave identically in the frozen arm, because frozen also catches only `OSError`. They are no-harm controls that must be equal in both arms, not red-to-green cells, and they must stay out of the "escaping versus refused" denominators. Counting them as refusals is itself a rejection under the round-20 QUALITY row ("errors vanish from the denominator").

## Minimum remedy (advice, not an implementation)

- **ApiFix.** Keep exactly `except OSError as exc: raise SetupError(...) from exc` at the three sites, as the draft already does. Add no wider catch inside `install_tree` or around its call at 1414; the existing outer `BaseException` handler is the single place that records interrupts.
- **Matrix.** Add rows 1–4. Inject sentinel subclasses defined in the harness (`class InjectedInterrupt(KeyboardInterrupt)`, `class InjectedFault(TypeError)`) and catch only those sentinels at the harness's observation boundary. A real operator Ctrl-C must still kill the harness instead of being scored. Patch `module.sha256_file` in the loaded module's globals, not `hashlib`, so the patch actually reaches the call. Include named mutants (`except Exception`, `except BaseException`, `except (FileNotFoundError, PermissionError)`) that rows 2, 1 and 3 must each kill.
- **CallerRepair.** Keep `except module.SetupError`, as in the draft grid. In `unpinnable-e2e.py` line 73, the pristine-scan `install_tree` call will now raise on an unreadable copy. Let that propagate to the script's exit-2 boundary rather than adding a broad catch.

## Out of this dimension (routed, not judged)

- An open of a regular member swapped for a FIFO between `lstat` and `open` blocks forever instead of raising, so it is neither a refusal nor an escape. This belongs to KamaR22.CritRace.
- `UnicodeEncodeError` on a non-UTF-8 member name already refuses pre-launch as `internal:UnicodeEncodeError` in both arms. Relabelling it `install-tree-unpinnable` would need an explicit name check, not a wider `except`.

## Tooling

No installs or updates. Read-only commands only: `git --no-optional-locks status/diff/rev-parse/show` and `wc`.
