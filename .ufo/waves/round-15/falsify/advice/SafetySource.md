# SafetySource — round-15 falsification (sentinel, read-only)

Attack surface: read-only baseline/source-row evidence, and whether any candidate
tool touches host credential, database, or config paths. Candidates are the
committed ones at `70af36c` ("round-15: enforce duplicate corpus admission before
replay children"). I edited nothing except this report. I ran no gates, tests,
builds, or linters, and installed nothing (pacman is paused host-wide, and no
install was needed).

Axes: (a) baseline provenance integrity, (b) source-row cell integrity,
(c) host-path access by the tools, (d) zero mutation and zero child processes on
rejection, (e) scope of the guard diff.

## Verdict: no Fail finding on this surface

### (a) Baseline provenance — holds
- `git show 6e348e2:.ufo/waves/round-14/measure.py | sha256sum` gives `fda61e00…4b60d`.
  That equals `frozen/measure-before.py` and `frozen/manifest.json.sha256`, and
  matches the manifest's `source_commit 6e348e2…`.
- Candidate `.ufo/waves/round-14/measure.py` at HEAD has sha256 `46c5866d…45257`.
  `diff -u frozen/measure-before.py measure.py` shows exactly two added lines,
  after `problems = []`:
  `if len(declared) != unique: problems.append("duplicate case names")`.
  Nothing else changed. The existing stripped-name `declared` and `unique`, the
  minimum check, and the `run` branch order are all preserved.
- The working tree is clean for every committed candidate. The only paths that
  `git status --porcelain` reports are untracked falsify-wave files under
  `.ufo/waves/round-15/falsify/`.

### (b) Source rows — hold
- The S034 citation "`corpus_problems` lines 350–362 … at start commit 6e348e2"
  is exact. In the frozen baseline, `def corpus_problems` is at L350 and
  `return problems, unique` is at L362, and the only predicate is
  `if unique < MINIMUM_UNIQUE_CASES:` (L358). The same function is at L350–364
  in HEAD, so the citation depends on its commit qualifier, and it carries one.
- Diff `6e348e2..HEAD -- corpus/SOURCES.md`: exactly one existing row changed
  (S012). Its only changed cell is the final `used-by` cell, which went from
  `runtime-health-surface-matrix.md, served-identity-crosswalk.md, ollama-evidence-replay.md`
  to the same three plus `corpus/lessons/round-15.md`. Row S034 was appended.
  A search-log paragraph was appended. No other line was removed.
- Plain row count: `grep -c '^| S0'` gives 34 rows (tier A 31, tier C 3). The
  baseline census `sources-before-census.json` shows 33 rows (A30, C3, mined 23),
  so the change is consistent with exactly one added own-work tier-A row. The
  baseline validate warning `W04 S031 duplicate url docs.ollama.com/api/tags` is
  a pre-existing condition. It was not introduced in round 15.
- No round-15 `sources-final-*` census exists yet. This is a temporal state:
  L1 records the final census after owners finish. It is not a defect.

### (c) Host credential, database, and config access — none
- I grepped `measure.py`, `tests/ollama-corpus-guard/check.py`, and
  `tools/kama-ollama-evidence.py` for `.omp`, `agent.db`, `sqlite`, `.ssh`,
  `.ollama`, `/etc/`, `.config`, credential, token, socket, urllib, http,
  `shell=True`, `/proc/`, pacman, and sudo. There were no hits.
  The only environment and home-directory references are:
  - `os.environ.get("PATH")` (measure.py L203, check.py L317);
  - `expanduser()` on caller-supplied `--tool`, `--cases`, and `--runner` values
    (measure.py L93/L433-434, check.py L719).
- Children of both runners get a replaced environment containing only PATH,
  HOME, TMPDIR, LANG, and LC_ALL, with HOME and TMPDIR set to a per-test or
  per-case temp dir (measure.py L199-208, check.py L312-322). Every spawn uses
  `-I -B`, list argv, `shell=False`, `stdin=DEVNULL`, and a bounded timeout
  (measure.py L230-251, check.py L362-386).
- The classifier opens only the `--tags` and `--ps` paths it is given, read-only,
  regular files only, with a byte bound (L137-169).
- `../scripts/sources-census.sh` has no `.omp`, `agent.db`, sqlite, HOME, `~/`,
  `.config`, credential, curl, wget, or `/etc/` references.
- `resume_continuity` is absent from measure.py, the corpus-guard directory,
  `tools/`, and SKILL.md, so the zero-mutation contract for
  `resume_continuity_v1` is not applicable to this surface.

### (d) Zero mutation on rejection — holds by source
- In HEAD measure.py, the side effects that happen before the decision are all
  read-only:
  - `load_cases` reads the cases file;
  - `tool.is_file()`;
  - `sha256_file(tool)` reads the tool.

  `corpus_problems` is evaluated at L374. When it reports problems, the
  `if corpus:` branch (L377-380) builds `unmeasured_record`s only. The first
  write and first spawn are `tempfile.TemporaryDirectory` (L382) and
  `measure_case` → `subprocess.run` (L240), and both live only in the `elif`
  branch. A duplicate corpus with at least 16 unique names therefore leaves no
  filesystem mutation and starts no child process.
- On rejection, all of the harness's own staging lands inside its
  `TemporaryDirectory`, with subdirectories named by index (`test-{index:03d}`):
  the marker, the audit file, the wrapper, the launcher, and `cases.json`. The
  committed `tests/ollama-evidence/cases.json` is only read and deep-copied
  (check.py L236-250, L350).
- Marker and audit paths are embedded as `repr()` literals rather than passed
  through the environment (check.py L272-273, L301), so the build-wave HostSafety
  F2 risk does not occur in the landed code. Accepted controls require
  `marker == total` and `Popen == total` (L596-604), which is the positive
  control for the rejected cases' `marker == 0` and `process events == 0`.

### (e) Guard scope — holds
The two-line diff adds only `len(declared) != unique`. It adds no blank-name
handling, Unicode normalization, or raw-key handling, which matches
`integration-review.json` `rejected_or_bounded[0]`.

## Out-of-scope observation (no remediation requested)
- In the classifier's own `--selftest` (tools L401-408), `subprocess.run` has no
  `env=`, so its children inherit the caller's environment. The registered gate
  never reaches this path: the runner invokes the classifier with
  `--tags/--ps/--expect`, and the wrapper uses `runpy`. The child still opens
  only its staged capture files, so no credential, database, or config access
  follows from it. I am recording this as an observation only, under the
  no-scope-expansion rule.

## Severity summary
| Item | Severity | Status |
|---|---|---|
| Baseline sha and commit correspondence | — | holds |
| S034 line citation and S012 single-cell change | — | holds |
| Host credential, database, and config path access | — | none found |
| Rejection zero mutation and zero child processes | — | holds by source; L1 to execute the gate |
| Classifier selftest env inheritance | Info | outside the gate path; no action |

## Commands run (all read-only)
- `diff -u`;
- `sha256sum`;
- `git log`, `git status --porcelain`, `git show <rev>:<path>`, `git show --stat`,
  `git diff 6e348e2 HEAD -- corpus/SOURCES.md`;
- `grep -c` / `uniq -c` row counts;
- `grep` of `../scripts/sources-census.sh`;
- tool `read`s and `grep`s of the files cited above.
