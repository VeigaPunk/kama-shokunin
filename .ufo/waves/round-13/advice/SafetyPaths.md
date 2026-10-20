# SafetyPaths — round-13 measure.py subprocess/read-scope review (sentinel)

Reviewed statically: `.ufo/waves/round-13/measure.py` (905 lines, 38531 B, sha256 `261ee99db0217515463ce83f8ea0ecd65dde8d468ff1a106435e252e2d6b8efc`, observed by `sha256sum`/`wc -lc`) and `frozen/expected.json` (sha256 `21b6c4ac…9196`). I did NOT run measure.py in any mode (live, frozen, `--selftest`, `--help`). No tools installed.

Axes: subprocess construction · env/config/endpoint leak · git replacement-source confusion · filesystem writes · read scope.

## Verdict
No high or medium defect in the final code. One low bug (L1). Two earlier issues, A–E, were sent to Measure against sha `3f2b98eb…`; all are closed in the final code (see the closure table).

## Findings

| Sev | Issue | Exploit path | Evidence | Smallest remediation |
|---|---|---|---|---|
| Low (L1) | `-h/--help` gives non-JSON stdout and exit 0 | `Parser` subclass (L141-143) overrides only `error()` and keeps argparse `add_help=True`. `--help` prints the docstring and raises `SystemExit(0)`, which is a BaseException, so it gets past `except Exception` (L887). A wrapper that checks only the exit code would read 0 = `clean`. | Docstring (L55-56): "All modes emit exactly one JSON object on stdout". Exit map: 0 = clean (L106-111). | `Parser(..., add_help=False)` in `build_parser` (L853), or catch `SystemExit` in `main` and emit `probe_error`. |
| Info (I1) | In frozen mode, the before-side provenance is only the manifest label | L577 compares the manifest's `before.revision` string to `BEFORE_REVISION`. It never checks the before bytes against git. A coherent rewrite of the before snapshot plus its manifest would pass. This limit is declared at L124-125. | I observed `git --no-replace-objects cat-file blob 941bb32…:corpus/QUALITY.md \| sha256sum` = `157495271d…cf`, which equals frozen/before and manifest L10. Today the label is true; this observation is not a property of the code. | L1 receipts should include one live-mode run, which does the git-backed read. Optional: in frozen mode, compare before bytes with `cat-file blob BEFORE_REVISION:corpus/QUALITY.md`. |
| Info (I2) | Live mode currently fails closed | `worktree_matches_head` (L392, L450) requires the worktree QUALITY to equal `HEAD:corpus/QUALITY.md`. I observed HEAD = `941bb32…` and ` M corpus/QUALITY.md` (`git status --porcelain`). Until L1 commits, live mode returns `documentation_mismatch` with `worktree_not_at_measured_revision`. | git status/rev-parse output (observed). | This is the correct fail-closed behaviour. L1 must commit before the live run. |

## Closed checks (static, cited lines)
- **Subprocess construction (git):** L273-279. Argv list with `shell=False`, `stdin=DEVNULL`, `capture_output`, `timeout=30`, and `git --no-pager --no-replace-objects -C LANE`. Non-zero exits and OSError/timeout become `GateError`, then `probe_error` (exit 3), never clean (L280-284, L871-886). It only calls `rev-parse` (HEAD, and `--verify --end-of-options REV^{commit}`) and `cat-file blob`, none of which write.
- **Env:** L259-268. Every `GIT_*` variable is stripped, then `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0` and `GIT_CEILING_DIRECTORIES=LANE.parent` are set. `commands` records argv only (L274). Env values are never printed. Git stderr is truncated to 200 chars (L283). No network, endpoint or credential path exists: `cat-file blob` and `rev-parse` never call the global `credential.*`/`filter.lfs` config (observed in `git config --show-origin --list`). Lazy fetch is disabled, and no `extensions`/`promisor` config was found.
- **Replacement-source confusion:**
  - `--no-replace-objects` is set both as a flag and in the env.
  - I observed zero `refs/replace` refs, no `info/grafts`, no `objects/info/alternates`, no attributes on `corpus/QUALITY.md` and no `/etc/gitconfig`.
  - The historical path is the constant `QUALITY_GIT_PATH` (L79, L313). It is never derived from `--quality`.
  - The before revision rejects a leading `-`, uses `--end-of-options` and `^{commit}`, and records the resolved OID (L300-309). Clean also requires `oid == BEFORE_REVISION` and before-missing == 2 (L389, L446-447).
  - `cat-file blob` applies no textconv or filters.
- **Read scope:**
  - Live clean requires `--quality` to resolve to `LANE/corpus/QUALITY.md` and not be a symlink (L390-391, L448-449).
  - Frozen snapshots reject absolute paths, and the resolved path must satisfy `is_relative_to(manifest dir)` (L484-489).
  - Frozen `--quality` must resolve to one of the two pinned inputs (L561-570).
  - Outputs are digests, sizes and paths; file contents are never printed.
  - Residual: a symlinked live `--quality` target is read (digest only) before it is rejected. This is harmless.
- **Filesystem writes:** Live and frozen modes have no write sites; the only output is `print` on stdout (L900). `--selftest` writes only inside `tempfile.TemporaryDirectory` (L766-781). Its location follows the inherited `TMPDIR` and it is cleaned up on exit. Children run as `[sys.executable, '-I', '-B', script, ...]` with `shell=False`, `stdin=DEVNULL` and `timeout=120` (L783-791). `-I` ignores `PYTHON*`/user-site and `-B` suppresses bytecode writes.
- **Frozen pins vs bytes (observed sha256sum):** before `157495…cf` = git blob at 941bb32. After `596f87…da` = current worktree `corpus/QUALITY.md`. Both match manifest L10/L19.

## Closure of pre-review items A–E (sent to Measure, sha 3f2b98eb…)
| Item | Status | Where |
|---|---|---|
| A: selftest subprocess/tempfile vs "in-memory" | L1 superseded the assignment (per Measure's message): selftest is retained with `-I -B` children, and frozen/ is in the write scope | L783-786 |
| B: before revision not bound to the pin | fixed | L389, L446-447, L577-580 |
| C: arbitrary `--quality` could be clean | fixed | L390-391, L448-449 |
| D: frozen snapshot path escape | fixed | L484-489 |
| E: final bytes not bound to HEAD | fixed | L380, L392, L450 |

## Limits
- This is static review plus read-only git/sha256 fact commands (`rev-parse`, `cat-file blob`, `for-each-ref`, `config --list`, `check-attr`, `status`, `hash-object` without `-w`). None of these executed the gate.
- I did not exercise the claims about the child-process environment or TMPDIR at runtime. [INFERENCE] The `-I`/`-B` semantics come from Python's documented behaviour.
- This review covers only safety and scope. Textual-semantics adequacy belongs to the ReviewProbe/Attack* lanes.
