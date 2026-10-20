# ReviewSelftest — isolation obligations for `fidelity.py --selftest` (round 12)

Author advisor, static review only. No `fidelity.py` existed at review time
(`.ufo/waves/round-12/frozen/` absent), so this is a specification review of the
shared interface plus the round-11 precedent. No selftest, CLI, build, or test was
run. Unrun != pass.

Read-only fact checks performed (git plumbing and hashing only, no repo writes):
- `git --version` → 2.55.0 at `/usr/bin/git`; `python3 --version` → 3.14.7.
- Source blob `2f7303c…:corpus/SOURCES.md`: 18898 bytes, 0 CR bytes,
  SHA-256 `9dc40d25…2093a`. This equals the D1 "actual before" hash in the round-11
  lesson. Round-11 frozen copy `frozen/before/corpus/SOURCES.md`: `52665cf2…42fa1`.
  The mismatch D1 describes is real and reproducible by read-only hashing.
- Kama root has no `.gitattributes`, so no eol/textconv/filter attributes apply to
  SOURCES.md in that repo.
- Host git global config sets `user.name`/`user.email`, `init.defaultbranch`, and
  `filter.lfs.*`. Env sets `GIT_EDITOR`, `GIT_PAGER`, `GIT_TERMINAL_PROMPT`. No
  `GIT_DIR`/`GIT_INDEX_FILE` is set in this shell. Temp commits would inherit host
  identity unless the selftest pins its own.
- `/tmp` is tmpfs (writable, not inside any git worktree).

## Axes

A. Hermeticity (no live writes, no reads of pinned real history for fixtures).
B. Discrimination (each finding can actually be produced, and asserted by name).
C. Source correspondence kept separate from digest integrity.
D. Environment determinism (host git config, `GIT_*` env, PATH).
E. Exit-code hygiene (1/2/0 must not collide with tracebacks or argparse errors).

## Precedent (round-11) and what to reuse / avoid

Reuse, supported by observed code:
- `tempfile.TemporaryDirectory(prefix=…)` for all fixtures (`round-11/measure.py:394`).
- Child invocation via `sys.executable` plus `Path(__file__).resolve()`, not bare
  `python3` on PATH (`measure.py:576-578`).
- Assert exit code AND sorted finding-name set, not only exit (`measure.py:422-424`).
- Default root derived from `__file__` (`parents[3]`), not cwd. Same depth holds for
  `round-12/fidelity.py`.

Avoid, each observed in round-11:
- `round-11/reproduce.py:89-90` uses `subprocess.run([... 'git' ... 'rev-parse' ...],
  check=True)`. A missing git or nonzero git raises `CalledProcessError`; an uncaught
  Python exception exits **1**, which is the `source_mismatch` code.
- `measure.py:589` catches only `OSError` around selftest setup. Any other exception
  is a traceback exit 1.
- `measure.py:576-578` has no `timeout=` on child subprocesses.

## Findings (severity order)

**F1 — high: uncaught exceptions exit 1 and masquerade as `source_mismatch`.**
Missing `git` (`FileNotFoundError`), `CalledProcessError`, `UnicodeDecodeError`, or
manifest JSON errors must each map to `source_unavailable` or `snapshot_tampered`
with exit 2. Exit 1 must only come from a computed inequality. Obligation: `main()`
wraps the whole evaluation and emits a JSON finding for every exception path.

**F2 — high: `git -C DIR` walks up into any enclosing repository.**
If `--repo` (or a selftest temp dir) sits inside another worktree, `git -C` silently
reads the outer repo's objects, giving a false `clean` or a wrong blob. Obligation:
use `git --git-dir=<repo>/.git` (or `GIT_DIR` set explicitly), or verify that
`rev-parse --show-toplevel` equals the requested root. Set
`GIT_CEILING_DIRECTORIES` to the parent of the fixture dir. Selftest must include a
non-repo directory nested under a repo and expect `source_unavailable`, not `clean`.

**F3 — high: inherited `GIT_*` env and host config leak into child git.**
Child env must drop all `GIT_*` keys before running git: at least `GIT_DIR`,
`GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`,
`GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CONFIG_PARAMETERS`, `GIT_NAMESPACE`.
Set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=os.devnull` for selftest fixtures
(git ≥2.32; 2.55 present). Temp commits must set identity explicitly
(`GIT_AUTHOR_*`/`GIT_COMMITTER_*` or `-c user.name= -c user.email=`) so they do not
depend on the host's `user.*`. Use `-c commit.gpgsign=false`.

**F4 — high: byte correspondence can be silently broken by text decoding.**
`subprocess.check_output(['git','show',…])` with `text=True`/`universal_newlines`
applies newline translation and decoding; hashing the result is not a byte
comparison. Obligation: capture `bytes` only, hash bytes, never `str`. Prefer
`git cat-file blob <rev>:<path>` (plumbing, raw blob, fails on trees). `git show`
on a directory path prints a tree listing and exits 0, which a naive compare would
treat as content. [INFERENCE from git documentation of `show` tree output; not
exercised here.]

**F5 — high: revision/path/object-type failures must classify as `source_unavailable`.**
Cases the selftest must cover, each with exit 2 and finding `source_unavailable`:
bogus 40-hex revision; valid revision with missing path; path that is a tree
(`corpus`, `corpus/knowledge`); short or ambiguous revision if the manifest allows
it (recommend rejecting non-40-hex pins outright as `snapshot_tampered` or invalid
manifest, not as mismatch); `git` absent from PATH. The missing-git case is produced
by launching the child with `env PATH=<empty temp dir>` and `sys.executable` as an
absolute path. A git failure must never reach the mismatch branch.

**F6 — high: the "can fail" cases and the "correspondence" claim must stay separate
in the selftest's own output.** Selftest uses hermetic temp repos with
self-generated commits. It does NOT reference `2f7303c…` and does NOT claim that the
real `corpus/SOURCES.md` corresponds to history. Real-history correspondence is only
the default-manifest run against the pinned blob. Selftest success is evidence that
the CLI can produce each finding; it is not calibration evidence and does not move
any score (the calibration 7→7 delta in `round-12/claims.json` depends on the real
run, not on selftest). Label selftest output accordingly.

**F7 — medium: the cases that matter most are the discriminating ones.**
Minimum selftest matrix (each asserts exit code, sorted finding names, empty stderr
or no traceback, and that `snapshot`/`manifest` temp bytes are unchanged afterwards):
1. clean: temp repo, snapshot = blob bytes, manifest pins that snapshot digest and
   that temp commit → exit 0, findings `[]`.
2. source_mismatch: temp repo whose blob differs by one byte from the snapshot,
   manifest **coherently** regenerated for the snapshot → exit 1, `source_mismatch`.
   This is the key test that digest integrity alone is not correspondence.
3. snapshot_tampered: same as clean but manifest's snapshot digest NOT regenerated
   → exit 2, `snapshot_tampered`, and git must not be consulted (assert the finding
   is tamper, not mismatch).
4. source_unavailable variants (F5).
5. snapshot override without manifest (see F8) → exit 1 `source_mismatch`, with an
   explicit integrity-unchecked marker in the JSON.
6. non-repo nested directory (F2) → exit 2.
7. Oversized/invalid manifest JSON → exit 2, JSON finding, no traceback.

**F8 — medium: default-manifest vs snapshot-override rule is ambiguous.**
Shared interface says the default manifest is `frozen/expected.json`, and also that
"snapshot override without manifest allows observing old mismatch rather than
tamper." Read together: `--snapshot X` with no `--manifest` must skip the manifest
pin, otherwise the old snapshot reports `snapshot_tampered` (exit 2) instead of the
intended `source_mismatch` (exit 1). The rule must be stated in the CLI help and in
the JSON (e.g., `integrity: "not-checked"`), so a reader cannot mistake the unpinned
run for an integrity-verified one. Selftest case 5 pins this. Owner must decide;
this report does not pick a side.

**F9 — medium: `--selftest` argument interaction is unspecified.**
`--selftest --snapshot … --manifest …` must either reject the combination (exit 2,
usage) or ignore the paths entirely. Selftest must never read the real
`frozen/expected.json` or real snapshot, and never write under `frozen/`. Recommend
rejecting extra path arguments with exit 2 to keep the mode unambiguous.

**F10 — low: argparse usage errors also exit 2.**
Exit 2 is shared by `snapshot_tampered`, `source_unavailable`, and argparse. Selftest
must assert the JSON `finding` name on every exit-2 case, not the exit code alone.

**F11 — low: subprocess timeouts and cleanup.**
Every git and child call needs `timeout=` (round-11 omitted it). `TemporaryDirectory`
cleanup must run on exception paths; use a context manager around the whole matrix.
Git objects are 0444 but deletable on Linux within a writable dir; no action needed
beyond ensuring the dir itself is removed.

## Obligations for the fidelity owner (summary)

- Child process: `sys.executable`, `Path(__file__).resolve()`, `cwd` set to a temp dir,
  `timeout=`, env scrubbed of `GIT_*` with `GIT_CONFIG_NOSYSTEM=1`,
  `GIT_CONFIG_GLOBAL=os.devnull`.
- Git: `--git-dir` explicit, `GIT_CEILING_DIRECTORIES` set, `cat-file blob`,
  bytes-only capture, `-c commit.gpgsign=false` for fixture commits.
- Exit contract enforced by a top-level `try/except BaseException` mapping to
  exit 2 with a JSON finding. Exit 1 reserved for `source_mismatch`.
- `--selftest` hermetic: one temp dir, fixture repos, no reads of pinned real
  files, no writes outside the temp dir; output labels it as CLI discrimination only.
- Missing-git: child launched with PATH pointing to an empty temp dir.

## Checks for L1 (main agent, after integration; not run by me)

1. `python3 .ufo/waves/round-12/fidelity.py --selftest; echo $?` — expect 0 and the
   full matrix named in F7.
2. Hash the whole `frozen/` tree and the temp path listing before and after
   `--selftest`; expect no change.
3. `env -i PATH=/nonexistent /usr/bin/python3 …fidelity.py --snapshot … ; echo $?` —
   expect exit 2, `source_unavailable`, no traceback.
4. `grep -n 'text=True\|universal_newlines\|shell=True\|check=True' fidelity.py` — expect
   no hits in the git-capture path.
5. Run the selftest from a non-repo cwd and from a cwd inside the kama repo; results
   must match.
6. Inspect that default `--repo` and default manifest derive from `__file__`, not cwd.

## Residual risk

- Selftest only proves discrimination for the cases it constructs. It cannot prove
  absence of other mismatch sources (e.g., alternate git objects or grafts in the
  pinned repo). Those require the real-history run and are outside selftest scope.
- F8 remains an owner decision; until resolved, the real-history default run and the
  override run may be confused by a reader.

Tools installed or updated by this seat: none.
