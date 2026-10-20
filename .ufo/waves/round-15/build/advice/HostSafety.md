# HostSafety — Kama round 15 static safety review (sentinel, read-only)

Scope: static review of the trust boundaries in
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py`
(sha256 `fda61e00…4b60d`, which is byte-identical to
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py`.
That means GuardRepair had not landed when I read it). I also reviewed the
planned harness contract (spec items GuardRepair and GuardHarness) and
`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py`.
I edited nothing except this report. I ran no tests or verification.

Axes: forbidden-access (db/auth/session/config), install need, rejection
zero-mutation, child-process isolation, and proof integrity (no false zero-child claim).

## Verdict

- **Forbidden access: none required.** measure.py imports only stdlib
  (argparse, hashlib, json, os, subprocess, sys, tempfile, pathlib). It reads
  only `--tool` (to compute sha256 and check is_file) and `--cases`. The
  classifier opens only its `--tags`/`--ps` paths. Its subprocess use is limited
  to its own `--selftest` path. A grep of both files found no
  `agent.db`/sqlite/`.omp`/credential/socket/urllib/http/pacman/sudo/`shell=True`
  hits.
- **Installs: none needed.** Both the repair and the harness are stdlib-only.
  No tool was installed or updated.
- **resume_continuity_v1: not applicable** to this surface. Neither file has
  any resume or run-state path.

## Findings

### F1: High (correctness, the R1 bug itself). Duplicate corpora with ≥16 unique names reach child spawn
- **Exploit path:** `corpus_problems` (measure.py L350-362) only checks
  `unique < MINIMUM_UNIQUE_CASES`. Take a corpus of 16 distinct names plus
  one repeated name. It gives `unique == 16`, so `corpus` is empty and `run`
  enters `tempfile.TemporaryDirectory` and calls `measure_case`. That spawns
  `sys.executable -I -B <tool>` once per fixture. The docstring (L13-14) and
  `LIMITS[3]` promise that "duplicated corpora fail before any child runs".
  That promise is false.
- **Impact:** a duplicated corpus can produce exit 0 / `verdict_exit 0`. The
  receipt then double-counts one name's evidence while claiming
  ≥16-unique coverage. This is a fabricated-coverage defect, not a host
  compromise: children are confined to index-named dirs
  (`root / f"{index:02d}"`), so names never become paths.
- **Smallest remediation (matches GuardRepair):** in `corpus_problems`, after
  computing `unique`, add `if len(declared) != unique:
  problems.append("duplicate case names")`. Keep the minimum check. No other
  change is needed. The rejection branch in `run` (L376-379) already runs
  before the `TemporaryDirectory` is created and before any `subprocess.run`.
  The repaired path therefore makes **zero filesystem mutations and zero
  child processes**. Its only pre-decision side effects are read-only:
  `load_cases`, `tool.is_file()`, and `sha256_file(tool)`.

### F2: High (proof integrity, harness pitfall). Marker path must not travel via environment
- **Exploit path:** `child_environment` (L199-208) replaces the whole child
  environment with PATH, HOME=case_dir, TMPDIR=case_dir, LANG and LC_ALL.
  Suppose GuardHarness passes the marker location in an env var, or derives
  it from TMPDIR/HOME. The wrapper then writes nowhere, or writes inside the
  runner's per-case temp dir, which gets deleted. The marker count reads 0
  even when children ran. That fabricates the "zero child invocations" proof
  for every expected-rejected case.
- **Remediation:** embed the absolute marker path into the wrapper source as
  a literal (`repr(str(path))`). The wrapper must append its line *before*
  `runpy.run_path(tool, run_name="__main__")`. It must fail closed (uncaught
  OSError gives a non-zero exit) if the append fails. Use one marker file per
  test, absent at start. Accepted controls must reach `marker == total`
  through the same wrapper and marker mechanism. That positive control is
  what makes `marker == 0` on rejected cases meaningful. Without it, the
  harness is not evidence.

### F3: Medium (harness isolation)
- Invoke the runner with list argv: `[sys.executable, "-I", "-B", runner,
  "--tool", wrapper, "--cases", cases]`. Also set `shell=False`,
  `stdin=DEVNULL`, a bounded timeout, and `capture_output`. Treat a timeout
  as a test failure, never as a pass.
- Name temp subdirectories by test index, never by the fixture's `name`/test
  id. Fixture JSON is untrusted data (e.g. `"../x"`).
- Clone `cases.json[0]` with `copy.deepcopy`. Never write back to
  `tests/ollama-evidence/cases.json`. Remove the temp root with
  `TemporaryDirectory`.
- `--runner PATH` executes arbitrary local Python by design. The default must
  resolve relative to `check.py`'s `__file__`, not the CWD.

### F4: Low (residual, out of R1 scope, do not expand). Undeclared names bypass both guards
- Fixtures whose `name` is missing, non-string, or blank are excluded from
  `declared` (L353-355). 16 distinct names plus N nameless fixtures pass
  both the old and the repaired guard and spawn N extra children, labelled
  `case-NN`. This is not a duplicate under the strip-identity contract.
  Record it as a limitation only.
- Identity is `str.strip()` and case-sensitive, with no Unicode
  normalization. NFC/NFD look-alike names count as distinct. This is
  consistent with ValidBoundaries (`N00` accepted). Limitation only.

## Limitations / disclosure
- This is a static review. GuardRepair (measure.py), GuardHarness (`check.py`)
  and `tests/ollama-corpus-guard/*.json` were **pending** (the directory was
  absent) at review time. Findings F2 and F3 are advisory against the
  harness contract, not against landed code. L1 must confirm them after the
  edits land.
- Incidental disclosure: one repo-wide grep for `resume_continuity` matched a
  line inside
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/interactive-sessions/20261015T050057Z/*.jsonl`
  (a session transcript). I did not read or use that file beyond the grep
  hit snippet. Future greps should exclude `.ufo/interactive-sessions/`.
- Commands run (read-only): `cmp` and `sha256sum` on measure.py and the
  frozen snapshot, `cat` of the frozen manifest, `ls` of the test dirs, and a
  read-only `python3 -c` count of cases.json (51 cases / 51 unique; case 0 is
  `loaded_same_digest`, expected exit 0).
