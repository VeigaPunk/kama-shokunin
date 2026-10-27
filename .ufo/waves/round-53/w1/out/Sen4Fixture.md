# Sen4Fixture — round 53, lane kama: fixture-safety audit of C2 `fixture()`

**Verdict: UNSOUND as written — `fixture()` does *not* "never commit into `--repo` or the fleet": an inherited `GIT_DIR` makes its `git -C D` calls operate on a foreign repository (10 fixture commits landed in a scratch stand-in; the repo named by `--repo` itself mutated 358→368 commits), and an inherited `GIT_CONFIG_COUNT*`/`core.hooksPath` makes its own `git commit` execute an arbitrary hook; scratch teardown *is* sound on every Python-level exit path (success, exit 1, exit 2, EvalError inside `fixture()`, SIGINT) except a direct `fixture()` call on EvalError and SIGTERM.**

Measured 2026-10-27 03:15–03:25 UTC on host 7.2.11-arch1-1, counter
`tools/round53-cited-path-check.py` at frozen build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`
(git blob `790cdd7353870b40eaed9067fbf2cb1e6a42b7a1`, identical at build commit, at lane tip `bc8e6e7f`
and in the worktree; sha256 `1afb8b9d…`),
`--repo` = my own `git clone --shared` of the lane (clone HEAD `bc8e6e7f`, 358 commits, clean before and
after every run), tip `c22602bd…`, scratch `/fast/scratch/hyaku/kama-r53/Sen4Fixture`.
Nothing in the lane outside this seat's out dir (`.ufo/waves/round-53/w1/out/Sen4Fixture*`) and nothing in the fleet was written; the counter was never edited in place; the fix below lives only in my out dir.

---

## F1 — HIGH (mutation, integrity): inherited `GIT_DIR` overrides `-C`; the fixture commits into a repository the caller never named

**Source.** `tools/round53-cited-path-check.py:389-391` builds the fixture environment as
`dict(os.environ, …)` — every inherited `GIT_*` variable survives. `:393-397` runs
`git -C D <cmd>` with that environment; `:410-412` initialises `D` and guards only the *worktree*:

```
410    g("init", "-q")
411    if os.path.realpath(g("rev-parse", "--show-toplevel")) != os.path.realpath(D):
412        raise EvalError("fixture repository is not the scratch directory")
```

With `GIT_DIR` set (and `GIT_WORK_TREE` unset) git resolves the worktree to the cwd, which `-C D` has
already made `D` — so `--show-toplevel` prints `D`, **the guard passes**, while the object store, index,
refs and `HEAD` all belong to `$GIT_DIR`. `git add -A` / `git commit` at `:406-407` therefore write the
fixture's commits into the foreign repo. `:456 shutil.rmtree(D)` removes only the scratch dir.

**Exploit path.** Any environment that exports an absolute `GIT_DIR`: a git hook (git exports `GIT_DIR`
to hooks), a CI/IDE wrapper, a systemd unit, an operator shell that ran `export GIT_DIR=$(git rev-parse
--absolute-git-dir)`. The counter is then run exactly as documented; it reports a normal receipt and
destroys the repo named by `GIT_DIR` — or by `--repo`, when they coincide.

**Evidence (reproduced, exit codes recorded).**

Scratch decoy *called* by `--repo` (evidence/04-repo-arg-mutated.txt):

```
$ GIT_DIR=$S/evB/.git python3 tools/round53-cited-path-check.py --repo $S/evB --tip c22602ba… --scratch $S/evB-scratch
BEFORE: HEAD=bc8e6e7f… commits=358 status=0
fixture=1 lane=0 scenarios=8/8 cited=682 unresolved=45 … met=False        exit=1
AFTER:  HEAD=bd8e478d… commits=368 status=110
--- HEAD tree is fixture content, not the lane:
SCORECARD.md SHONEN.md SKILL.md corpus/x.md registry/cited-path-corrections.tsv tools/a.py
```

Same shape with `--repo` = the untouched lane clone and `GIT_DIR` = a foreign clone
(evidence/03-gitdir-escape.txt): decoy `358 → 368` commits, `refs` hash changes, worktree 110 entries
dirty, its `c0` commit tree is `tools/a.py, tools/gone.py, corpus/x.md, SHONEN.md, SKILL.md,
SCORECARD.md` ("decoy commit c0 tree" block) — i.e. the fixture's own files are now committed history of
a repo it was never pointed at, and **`fixture=1` (8 of 8 calibration scenarios) is still reported**.
The lane clone itself stayed `HEAD=bc8e6e7f, status=0` because `GIT_DIR` named the decoy, not the lane.

The fleet was deliberately **not** used as the target (read-only constraint); the decoy clone is
mechanically identical (a normal repo reachable by absolute `GIT_DIR`). Under
`GIT_DIR=/home/vgpnk/Projects/shokunin/.git` the same 10 commits and ref rewrite land on the fleet.

**Impact.** Silent, irreversible history replacement of a repo the counter promises to treat as
read-only (docstring: "Read-only on `--repo` and `--fleet`"), producing a receipt whose `fixture=1` is
valid while the repository is destroyed — the same damage class as the fixture commit that once deleted
4,606 fleet paths.

**Smallest remediation.** One helper, used by *every* git invocation (proposed-fix.diff, hunk 1):

```python
def clean_env(extra=None):
    """Environment for every git call: inherited GIT_* redirection is dropped."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra or {})
    return env
```

plus `env=clean_env()` in `git()` (`:116`) and `env = clean_env({…fixture identity…})` at `:389`, plus a
second guard after init (belt and braces):

```python
if os.path.realpath(g("rev-parse", "--absolute-git-dir")) != os.path.realpath(os.path.join(D, ".git")):
    raise EvalError("fixture git dir is not the scratch directory")
```

**Fix verified** (evidence/09-patched-verify.txt, patched copy `round53-cited-path-check.patched.py`,
sha256 `2e2e0e30…`): clean run still `fixture=1 lane=1 scenarios=8/8 … met=True`; under
`GIT_DIR=<foreign clone>` the decoy stays `HEAD=bc8e6e7f commits=358 status=0` and the run is still
`met=True`; `GIT_INDEX_FILE` creates nothing outside; the hook never runs.

## F2 — HIGH (code execution): inherited env git-config reaches `core.hooksPath`, so the fixture's own `git commit` runs an attacker hook

`fixture()` already nulls `GIT_CONFIG_GLOBAL=/dev/null` and sets `GIT_CONFIG_NOSYSTEM=1` (`:391`), but the
environment-config channel (`GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0`, `GIT_CONFIG_VALUE_0`) still applies and
takes precedence. `git commit -q` (`:407`) runs `pre-commit`.

**Evidence** (evidence/07-hooks-exec.txt, marker written outside scratch, exit 0, `met=True`):

```
$ GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=$S/hooks \
  python3 tools/round53-cited-path-check.py --repo <clone> --tip c22602ba… --scratch $S/evH-scratch
fixture=1 lane=1 … met=True   exit=0
hook marker file: PRESENT
```

Any `GIT_CONFIG_KEY_n` also works (`core.worktree` was tested and is ignored by `-C` discovery in this git
version — evidence/06-worktree-vectors.txt — so F2 is the load-bearing config channel). Same fix as F1
(strip `GIT_*`); patched run: `hook marker: absent`.

## F3 — MEDIUM (calibration integrity): the measurement path is equally poisonable — the receipt's `fleet=` revision is attacker-selected

`git()` (`:115-119`) also inherits the environment, and `Repo`/`evaluate` read `--repo` and `--fleet`
through it. With `GIT_DIR=<ln-clone>` the counter printed `fleet=bc8e6e7f…`, which is the decoy's `HEAD`
(decoy BEFORE line in evidence/03-gitdir-escape.txt), not the fleet revision, and `unresolved` jumped
`14 → 45` (`undisclosed=31`) while the same content reported `fixture=1 8/8`. So the receipt's revision
stamps and counts can be chosen by the caller's environment; in this instance the verdict happened to be
`met=False`, but a decoy that contains the tip yields a full pass over foreign content (F1 run). This is a
correctness defect independent of the mutation (read-path provenance), fixed by `env=clean_env()` in `git()`.

## F4 — LOW (write outside scratch): `GIT_INDEX_FILE` (and object-dir variants) escape the scratch tree

`GIT_INDEX_FILE=$S/evC/idx` → a real index is written outside scratch containing the fixture's staged
blobs (`SCORECARD.md, SHONEN.md, SKILL.md, corpus/x.md, registry/cited-path-corrections.tsv, tools/a.py`),
while the run reports `met=True` (evidence/05-index-file-escape.txt). `GIT_OBJECT_DIRECTORY` fails closed
here (`could-not-evaluate … Needed a single revision`, exit 2, decoy empty, evidence/06) only because the
read path breaks first; the same strip fixes both.

## F5 — LOW (cleanup): `fixture()` has no `try/finally`; a direct call leaks `D` on EvalError

`shutil.rmtree(D, ignore_errors=True)` sits at `:456` on the success path only. `main()`'s
`finally: shutil.rmtree(S)` (`:473`, `:500`) masks this for CLI use, so the defect is visible only when
`fixture()` is imported/called directly (evidence/08-cleanup.txt):

```
ok call   -> 8 leftover: []
err call raised: EvalError
leftover after EvalError: ['afile', 'r53c2-fx-jrwka4k5']      # D leaked
```

Patched (`try/finally` around the body): `err call -> 8 leftover: ['afile']` — only the sentinel file I
created remains.

---

## Cleanup on every exit path (verified)

| exit path | mechanism | scratch root afterwards | evidence |
|---|---|---|---|
| success, `met=True` | `main()` `finally` `:500` | 0 entries | 02-baseline-clean.txt |
| `met=False` (exit 1) | same | 0 entries | 03-gitdir-escape.txt (`scratch root entries: 0`) |
| `could-not-evaluate` before `fixture()` (bad tip) | same | 0 entries | 08-cleanup.txt E1 |
| EvalError **inside** `fixture()` (`GIT_WORK_TREE` makes `git init` refuse) | same (`S` removal also removes the leaked `D`) | 0 entries | 08-cleanup.txt E2 |
| EvalError inside `fixture()` with `GIT_DIR`+`GIT_WORK_TREE` (guard fires) | same | 0 entries | 06-worktree-vectors.txt |
| SIGINT (KeyboardInterrupt) | `finally` | 0 entries | 10-signals.txt |
| SIGTERM | default disposition, no handler | **1 entry leaked** (`r53c2-1681_3zs`, exit 143) | 10-signals.txt |
| direct `fixture()` call + EvalError | none (F5) | `D` leaked | 08-cleanup.txt E3 |

SIGTERM leakage is a documented limitation, not a regression (no `finally` runs on default SIGTERM); if it
matters, `signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))` restores the `finally`, which I did not
add to keep the patch minimal.

## What *is* safe (checked, so the lane does not over-correct)

- Every git call passes `-C` (`:116`, `:394`); no `cwd=` anywhere, no `os.chdir`, no `shell=True`.
  Process cwd is therefore irrelevant: running the counter **from inside** the lane clone with a clean
  environment leaves it `HEAD=bc8e6e7f commits=358 status=0`, `met=True`, scratch 0 entries
  (evidence/11-cwd-and-relative-gitdir.txt).
- Relative `GIT_DIR=.git` (what git exports to hooks) is re-anchored by `-C D` to `D/.git` — measured
  harmless (`met=True`, lane clean, from a foreign cwd). Only an **absolute** `GIT_DIR` escapes
  (same evidence file).
- `GIT_WORK_TREE` alone is refused by `git init` (`fatal: GIT_WORK_TREE … not allowed without specifying
  GIT_DIR`), and `GIT_DIR`+`GIT_WORK_TREE` is caught by the `:411` worktree guard
  (`could-not-evaluate: fixture repository is not the scratch directory`, exit 2, decoy untouched).
- `w()`/`at()` join constant relative names onto `D` (`:398-403`, `:423-431`); no caller-controlled path
  reaches the filesystem.
- `GIT_CEILING_DIRECTORIES`, `GIT_DISCOVERY_ACROSS_FILESYSTEM`, `GIT_NAMESPACE`,
  `GIT_ALTERNATE_OBJECT_DIRECTORIES` are covered by the same `GIT_*` strip; none can write.

## Files

- `proposed-fix.diff` — unified diff (sha256 `6773cf89…`) against `tools/round53-cited-path-check.py`:
  `clean_env()`, `env=` on both git entry points, `--absolute-git-dir` guard, `try/finally` cleanup.
- `round53-cited-path-check.patched.py` — full patched text (sha256 `2e2e0e30…`), parses, passes 8/8.
- `evidence/01-source.txt` … `evidence/10-signals.txt` — raw outputs quoted above.

Tooling: nothing installed. No llama-server started by me (`pgrep -af llama-server` shows only K2Design's
`kama-r48-live` pair on 127.0.0.1:35203, untouched). Scratch `/fast/scratch/hyaku/kama-r53/Sen4Fixture`
removed after the evidence was copied out.
