VERDICT: confirm - Python 3.14.8 documents a non-integer `sys.exit` argument producing exit code 1; the frozen gate also uses 1 for `INVALID`.

## Source opened
- Requested page: https://docs.python.org/3.14/library/sys.html#sys.exit
- Page title/version observed in the fetched reader: “sys — System-specific parameters and functions — Python 3.14.8 documentation”. The requested 3.14 URL resolves to that version; fetched 2026-10-21.
- Exact quote (15 words), §`sys.exit`, optional-argument paragraph: “any other object is printed to stderr and results in an exit code of 1.” This is a verbatim substring of the page's sentence beginning “If another type of object is passed…”.
- The same section says `sys.exit` raises `SystemExit` and exits only when that exception is not intercepted (page paragraph immediately following the argument semantics).
- Supporting page: https://docs.python.org/3.14/library/exceptions.html#SystemExit, title/version “Built-in Exceptions — Python 3.14.8 documentation”. §`SystemExit` says an unhandled `SystemExit` exits without a traceback and a non-integer value yields exit status one (HTML lines 857–863).

## Executed observations
- `curl -fsSL -o /tmp/kama-r20-SrcPySysExit/sys.html https://docs.python.org/3.14/library/sys.html`: exit 0; downloaded 263004 bytes. The exceptions page fetch also exited 0 (144074 bytes).
- `python3 --version`: exit 0; `Python 3.14.8` (matches docs version).
- On this Python 3.14.8 interpreter: `sys.exit(0)` -> exit 0; `sys.exit(1)` -> exit 1; `sys.exit("INVALID gate")` -> exit 1; uncaught `RuntimeError("crash")` -> exit 1. Each status was printed by the executed loop.
- Frozen lane evidence: `git rev-parse HEAD` -> `37bd4c5bd456a2f8a54d3312c28495c321715856`; `git diff --quiet 37bd4c5bd456a2f8a54d3312c28495c321715856 -- tests/llamacpp-live/check-receipt.py tests/llamacpp-live/install-tree-grid.py` -> 0 (both files match the frozen bytes). At `tests/llamacpp-live/check-receipt.py:2233,2236`, the gate prints `INVALID ...` and returns 1. At `tests/llamacpp-live/install-tree-grid.py:110-113`, `code == 1` is classified as `rejected`.

[INFERENCE] Since a gate's observed `INVALID` verdict and an uncaught Python exception can both have process status 1, status alone cannot distinguish them. The instrument must observe the gate's verdict output (here, the `INVALID ` prefix), not map every status 1 to a verdict.

## Draft registry entry
The 11-column SOURCES row and the located quote are also in `build/out/CloseKama18.SrcPySysExit-2/sources-row.md`. No tool was installed or updated. No lane source, index, or git state was changed; only the requested advice report and designated new output file were written.