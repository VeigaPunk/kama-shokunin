VERDICT: partial — the three audited tools write no lane files, run no git writes and read no session stores. The seats' own py_compile/import steps did leave untracked `__pycache__` files in the lane, which owners removed after I flagged them.

Seat: KamaR17.SentinelSeatWrites-2 (read-only). Snapshot times 12:16–12:34 -03, 2026-10-20. Lane tip `git rev-parse master` = cff9e62f05aa7cfb9059444f62eb787100719713.
Audited bytes (sha256 at 12:34):
- `tools/sources-append-only.py` c477a172…
- `tests/probe-verdicts/fault-controls.py` e47c32e1…
- `.ufo/waves/round-17/c1/mutants.py` 22890052…
- `tests/probe-verdicts/check.py` (context only) b460b786…

## Invariants checked (all hold at 12:34)
- **Matrix set unchanged.** `tests/probe-verdicts/*.json` = 9 files. The set digest, recomputed with the round-16 `measure.py:286-290` formula, = `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, which equals `EXPECTED_MATRIX_SHA256` (`measure.py:281`). No new `*.json` and no `run-*.json` anywhere under `tests/`, `tools/` or `.ufo/waves/round-17/`.
- **Frozen copies intact.** `sha256sum -c` against `.ufo/waves/round-17/frozen/manifest.json` gives all 5 OK.
- **No git writes.** No audited file calls a git write. Only `sources-append-only.py:200` calls git: `["git", "-C", repo, "show", f"{rev}:{path}"]`. `mutants.py` and `fault-controls.py` contain no `git` call (grep found none).
- **No session-store access.** None of the three files reads `interactive-sessions`, `.omp` or `.config` (grep found none). `fault-controls.py:281` copies the environment into the child (`env = dict(os.environ)`) but never prints it.

## Findings

### F1 — MEDIUM (process; fixed in flight; can recur): `__pycache__` written into the lane outside the owned files
- **Exploit path:** each item's Acceptance says "You may run `python3 -m py_compile`…". `py_compile` (and any `importlib` load) writes `<dir>/__pycache__/*.pyc` next to the source file. `.gitignore` only covers `.ufo/interactive-sessions/` and the uncommitted `.ufo/state/`; `git check-ignore` returned rc=1 for `tools/__pycache__/x.pyc` and `tests/probe-verdicts/__pycache__/x.pyc`.
- **Evidence (observed with `git status --porcelain --untracked-files=all`):**
  - 12:21:02 `?? tools/__pycache__/sources-append-only.cpython-314.pyc`
  - 12:25:00–12:25:38 `?? tests/probe-verdicts/__pycache__/check.cpython-314.pyc` (inside the pinned matrix directory; rewritten once)
  - ~12:33 `?? tests/llamacpp-live/__pycache__/check-receipt.cpython-314.pyc` and `controls.cpython-314.pyc` (C2 seats, outside my three files but the same pattern)
- **Impact:** files outside "Write ONLY the file(s) your item names". They are not ignored, so a broad stage or snapshot would pick them up. [INFERENCE] jj snapshots every non-ignored working-copy file on its next command, so these `.pyc` files would enter the working-copy commit unless `jj-lane.sh commit … -- <paths>` limits what it takes. A `.pyc` does not change the `*.json` glob or the bf9068d8 digest.
- **Status:** I messaged each owner (SourcesAppendOnly, C1HarnessGrading, C1MutantRunner, C1FaultControls, C2Controls). SourcesAppendOnly confirmed it switched to `ast.parse`. At 12:34, `find tests tools .ufo/waves/round-17 -name __pycache__ -o -name '*.pyc'` returns nothing.
- **Smallest remediation:**
  1. Add `__pycache__/` to `.gitignore`.
  2. In the spec template, replace "python3 -m py_compile" with `python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" FILE`, or require `PYTHONDONTWRITEBYTECODE=1`.

### F2 — LOW (fixed in flight): git-option injection in `sources-append-only.py`
- **Before (read at ~12:21):** `git_show` passed `f"{rev}:{path}"` straight from argv. `--from=--output=/x` would reach git as an option. `git show` accepts the diff option `--output=<file>`, "Output to a specific file instead of stdout" (https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---outputltfilegt). [INFERENCE] That would write an arbitrary file, possibly inside the lane; I did not execute it.
- **Now:** `sources-append-only.py:197`: `if rev.startswith("-") or ":" in rev:` → ParseError, exit 2. The owner reports that `--from=--output=/tmp/x` exits 2 with no file written. I did not re-run it.
- **Residual (calibration, not write):** `sources-append-only.py:202` `text=True` has no `UnicodeDecodeError` handling (grep found none). A blob that is not UTF-8 would end in an uncaught traceback, and Python exits 1 on that, the same code the tool uses for "at least one append-only violation". [INFERENCE] I did not run it. **Remediation:** catch `UnicodeDecodeError` as ParseError so it exits 2.

### F3 — LOW (process cleanup): timeouts kill only the direct child
- `mutants.py:646-649` and `:724-727` use `subprocess.run(..., timeout=...)` with `CHECK_TIMEOUT = 600` and `CONTROLS_TIMEOUT = 900` (`:79-80`). On timeout, CPython kills only that child.
- **Exploit path:** a mutant hangs `fault-controls.py` past 900 s, and `fault-controls.py` is SIGKILLed.
  - Its `with tempfile.TemporaryDirectory(prefix="kama-fault-controls-")` (`fault-controls.py:445`) never cleans up, so `/tmp/kama-fault-controls-*` is left behind.
  - Its child `check.py` and the wrapper/probe processes, plus their loopback stubs on 127.0.0.1:0, are orphaned until they exit on their own.
- **Not affected:** the lane itself (scratch is under `/tmp`). [INFERENCE] I did not trigger this.
- **Already safe:** inside `fault-controls.py`, the wrapper is `exec python3 - "$@"` (`:144`). So `check.py`'s own timeout kill reaches the sleeping F7 process (`:185 time.sleep(...)`), and no orphan is left there.
- **Smallest remediation:** call `subprocess.run(..., start_new_session=True)` and, on `TimeoutExpired`, `os.killpg(proc.pid, SIGKILL)` in both `mutants.py` runners. This needs `Popen`, because `run()` hides the pid.

### F4 — LOW (calibration of the counting command): `mutants.py` does not pin the matrix set
- `mutants.py:597`: `h.update(f"{f.name}:{sha256_bytes(data)}\n"...)`. This is a different line format from `measure.py:289` (`f"{f.name} {…}\n"`), so its digest can never equal bf9068d8.
- The only gate is `:797` `if len(matrix) != 9:`. A swapped matrix with nine files would be mutated and counted silently.
- **Remediation:** use the `measure.py` formula and refuse when the digest ≠ `bf9068d89e4c…`.
- This affects calibration, not writes. It is in scope because it bears on the "nine files stay byte-identical" constraint.

## Clean (write discipline holds)
- **`fault-controls.py`**
  - All scratch lives in `tempfile.TemporaryDirectory(prefix="kama-fault-controls-")` (`:445`). It byte-copies `check.py` and the `*.json` files into that directory (`:319-322`).
  - It writes the wrapper (`:325`) and the F6 cache (`:209-212`) only there, and runs `check.py` with `cwd=scratch` (`:283`).
  - It only reads the lane matrix dir (`:262`, `:321`, `:395`). It never imports `check.py`.
- **`mutants.py`**
  - Scratch goes to `tempfile.mkdtemp(prefix="kama-r17-c1mutants-")` (`:802`) and is removed in `finally` (`:956`) unless `--keep-scratch` is given.
  - The receipt is written atomically via `mkstemp` + `os.replace` (`:970-974`).
  - `emit` refuses any `--out` inside the matrix dir (`:965-968`: "refusing --out inside {MATRIX_DIR} (matrix set is pinned)").
  - `--selftest` touches nothing in the lane (`:1077`).
  - [INFERENCE] A SIGKILL between `mkstemp` and `os.replace` would leave a `<name>.XXXX` temp file next to `--out`.
- **`check.py` (current)**: the new selftest writes `a.json` and `b.json` only under `TemporaryDirectory(prefix="kama-check-selftest-")` (`check.py:534-538`, "Proven in a temp dir — never in the real matrix directory").
- **`kama-probe.sh`**: in `check --port` mode it writes only to `mktemp -d "${KAMA_PROBE_TMPDIR:-/tmp}/kama-probe.XXXXXX"` (`kama-probe.sh:1128`) and removes it via `trap cleanup EXIT` (`:92-93`). History writes happen only on the `snapshot` path (`:1023-1099`).

## Context calibration (jj risk R1)
- The context says `registry/history/.lock` is not gitignored. It is ignored: `git check-ignore -v` → `registry/history/.gitignore:3:.lock` (committed in 83bee7f). `.ufo/state/` is ignored only through an **uncommitted** worktree edit (`git diff master -- .gitignore`: `+.ufo/state/`).
- The worktree also has uncommitted edits to `AGENTS.md` (+1 VCS line), `.ufo/waves/round-13/measure.py`, `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/check-receipt.py`. These belong to other items. I note them only because R1's round-13 gate compares the worktree with HEAD.

## Limitations
- This is static review plus repeated `git status` / `ls` snapshots. I executed none of the three tools, `measure.py` or any gate.
- I did not write peer transcripts and did not read any `history://`.
- The audit covers the bytes listed above. Later edits by owners are not covered.
- I sent five short coordination messages to the owners; I made no edits.
- The `ss -ltnp` listeners on 8787–8796 and 37433 belong to other processes; I started no servers.
- Installs: none.
