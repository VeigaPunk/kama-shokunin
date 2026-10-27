source: S517 — Python 3.15.2 `sys.setprofile`, https://docs.python.org/3/library/sys.html#sys.setprofile (anchor `#sys.setprofile`, page footer "Last updated on Oct 27, 2026"); code `tools/round58-battery-exec-check.py` @ lane tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a, roster `.ufo/waves/round-56/preregistration.json` @ same tip; freeze dcd69473dd7e33b316e2ba238a48e5119a6cd809
verified-at: 2026-10-27 (round 58) — page opened live; checker read at the tip above; three fixture probes in `.ufo/waves/round-58/w1/out/W08KnowledgeEntry/probe.receipt.txt` (genuine accept, posix_spawn escape, post-main raise)
recheck: `python3 tools/round58-c1-counter.py --repo . --tip <rev> --checker tools/round58-battery-exec-check.py` (accept genuine + 3/3 benign, reject 11/11 no-op, exit 0 = met); S517 recheck on-release

# Battery execution evidence — what a profile hook does and does not establish

Round 57 bound a battery roster to its call sites by AST walk; dead code, an unused
function, an early return and a rebound `run` all satisfied it (freeze: benign 1/3,
noop_rejected 1/11). Round 58 loads the committed battery as `__main__` in a child
interpreter, records `sys.setprofile` call events, and requires every roster label to
reach a `run` frame that issued a counter invocation. This entry fixes what that
evidence is worth; it is instrument knowledge about a lane tool, not about serving.

## What it establishes

- **Entry only.** A function named `run` or `assert_mutant_breaks_detection` whose
  `co_filename` is the battery file was entered, and the first parameter was bound to
  the roster label (a `str`). A same-named function in an imported module, or code
  compiled from a string, produces no frame: the evidence is conservative, not broad.
- **Argv shape under the frame.** While that frame was on the stack, a call reached one
  of the four replaced entry points (`run`, `call`, `check_call`, `check_output`) with
  `--counter` as an *exact* argv element — `"--counter" in argv` on a list, so
  `--counterfoo` does not count. Attribution goes to the innermost watched frame.
- **The real entry path.** `__name__ == "__main__"`, so a battery that never invokes
  `main()` earns nothing; the roster match itself is a separate *static* AST literal
  equality, not execution evidence.

## What it does not establish

- **That any leg ran.** The four entry points are replaced by a recorder returning a
  canned `CompletedProcess(argv, 0, "ld_audit=detected\n", "")`. No real exit code,
  stderr or counter output exists, and a battery branching on returncode sees only
  success. Label + `--counter` is argv shape, never leg correctness.
- **Leg result semantics.** `assert_mutant_breaks_detection` passes on being invoked at
  least once with at least one subprocess call per invocation; whether the mutant was
  killed, or the assertion asserts anything, is not read. A no-op outside the 11
  enumerated variants (wrong `--repo`, duplicate label, a `--counter` naming the wrong
  counter) survives and is a LIMIT, not C1 credit.
- **That nothing ran or wrote.** The harness wraps those four points and raises in
  `Popen`/`os.system`, but `os.posix_spawn`, `os.spawn*`, `os.exec*` and `ctypes` are
  unwrapped, surface only as unread `c_call` events (S517: "A C function is about to be
  called"), and really execute; `open()` writes are not swallowed either. Probed: a
  battery calling `os.posix_spawn("/usr/bin/touch", ...)` inside a watched `run` frame
  wrote its marker and still scored `met=True`. "Hermetic" covers the patched paths.
- **That the battery ran clean.** The child writes an exception to `result.json["error"]`
  but the parent reads only `["frames"]`; a battery raising after `main()` still scored
  `met=True` (probed). The claim's "0 evaluation errors" counts checker exit codes
  (2/other), not battery exceptions.
- **Threads.** S517: "The function is thread-specific ... it does not make sense to use
  this in the presence of multiple threads." Subprocess calls issued from a worker
  thread are unattributed — a false reject, never a false credit.

## Reuse boundary

The evidence answers one question: did each declared leg's call occur while its declared
label was in scope, with the counter argv element present? It is the right instrument
for "roster literal intact, call graph hollow" and the wrong one for "the legs are
right". Any later claim that a battery *executed* its legs needs a real leg receipt with
exit codes and outputs; this hook cannot supply it.
