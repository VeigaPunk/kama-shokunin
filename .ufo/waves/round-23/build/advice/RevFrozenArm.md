# RevFrozenArm: how the frozen 4fe9339f arm should load the auditor, and its confounds

Seat: CloseKama22.RevFrozenArm (leaf reviewer). Date: 2026-10-21. Findings only: no production edits, no commits, no installs (none needed; used `/usr/bin/python3` 3.14.8 and `/usr/bin/git` 2.56.0 as found).

## Pinned inputs

- **Frozen arm:** `git cat-file -p 4fe9339f:tools/report-landing-audit.py`. Git blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`, sha256 `09ecd63b…b3b3f`, 40404 bytes, 847 lines.
- **Candidate arm:** lane working copy `tools/report-landing-audit.py` (uncommitted, `M`). **It changed three times during this review** (12:15:19 43694 B sha `4494764e…`; 12:15:39 44436 B; 12:17:56 44555 B). Everything below is measured on the **79d9e124 copy**: sha256 `79d9e124e8171b47…`, 44555 B, 921 lines, git blob `9755654acd11e72c10c2702bd85c429a75aee58d`. The lane file was unchanged at report time. Candidate verdicts are version-specific (see F11).
- Lane HEAD `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, working copy `M tools/report-landing-audit.py`.

## Recommendation

Load **each arm as a subprocess** of the same interpreter, using an immutable copy of the blob, a pinned env, explicit absolute repo arguments, and one shared `cwd`. Do not import the blob in-process. Each reason below is measured, not inferred.

| Axis | In-process import from temp file | Subprocess (`python3 -B <blob>`) |
|---|---|---|
| Locale / UTF-8 mode per arm | Fixed at harness startup; `os.environ` edits do not change it (E-I) | Set per run via `env=` (canary verified) |
| Exit semantics | Uncaught exception surfaces as Python exception (E-B); must be emulated as rc 1 | Native rc 1 + traceback, rc 2 for EvalError |
| Module identity | Same module name silently aliases arms (E-C) | Separate processes |
| Bytecode writes | Writes `__pycache__` beside blob (E-D) | None with `-B` |
| cwd | Process-global `os.chdir` | `cwd=` per run |
| Selftest side effects | Transient `os.environ["GIT_DIR"]` (restored, E-J2) | Isolated |

Wall time for the whole probe (9 fixtures × 4 locale profiles × 2 arms, plus experiments) was 7.65 s, so speed is not a reason to prefer in-process.

## Findings (severity order)

All experiments are in `/tmp/kama-r23-review/RevFrozenArm/loader_probe.py`, output `loader_probe.out`. Fixtures are deterministic: rebuild SHAs equal (9/9). Only `/tmp` fixtures were used, never the real lane or fleet.

**F1 HIGH. The frozen arm's verdicts depend on the process's preferred encoding. The candidate's do not.**
- Evidence: frozen `git()` calls `subprocess.run(..., text=True)` (`frozen/…:90`), so stdout is decoded with the locale. Candidate `git()` decodes bytes as UTF-8 explicitly (`current:107-126`).
- Locale matrix, rc (`loader_probe.out` lines 9-48):

| Fixture | frozen, utf8-pinned | frozen, ascii-forced | candidate, all 4 profiles |
|---|---|---|---|
| control | 0 | 0 | 0 |
| ctrl-nonascii (valid café subject, no fault) | 0 | **1** `decoding with 'ANSI_X3.4-1968' codec failed` | 0 |
| ctrl-report-utf8 (valid café in report) | 0 | **1** (same) | 0 |
| f1-logenc | 1 `UnicodeDecodeError 0xe9` | 1 (ASCII, not the fault) | 0 |
| f2-report-bytes | 1 `UnicodeDecodeError 0xff` | 1 (ASCII) | 2 `cannot read report` |
| f3-replace-omit | 0 (false clean) | 0 | 1 `landed-omitted` |
| f4-replace-fake | 0 (false clean) | 0 | 1 `unresolved-full-hash`, `landed-unresolved` |
| f5-lazyfetch | 1 + **MARKER** (command ran) | 1 + MARKER | 2 `partial clone`, no marker |
| f6-follow | 0 | 0 | 0 |

- `utf8-pinned` = `LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONUTF8=1`. `C-locale` (`LC_ALL=C`) and `host-lang` (`LANG=en_US.UTF-8`) produce the same rows as utf8-pinned. On this host `LC_ALL=C` is UTF-8 mode (canary `utf-8 1 utf-8`), so it is not an ASCII pin. `ascii-forced` = `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` (canary `ANSI_X3.4-1968 0 ascii`).
- Consequence: the L1 probe's (a)/(b) crashes and (c)/(d)/(e) false-clean/execution results reproduce for the frozen arm under UTF-8. But under ASCII the frozen arm also crashes on valid content, so a locale crash can be mistaken for the fault. The grid needs (i) one pinned UTF-8 profile for both arms and (ii) valid non-ASCII controls, which the L1 probe lacks.

**F2 HIGH. In-process import changes how the same behavior is classified.**
- E-B: frozen f1 and f2 in-process raise `UnicodeDecodeError` into the harness (`raised UnicodeDecodeError`). Subprocess gives rc 1 with traceback. A harness must map exceptions to rc 1, or it records the same behavior as two categories.
- E-I: after `os.environ.update(LC_ALL=C, PYTHONUTF8=0, PYTHONCOERCECLOCALE=0)`, `locale.getpreferredencoding(False)` is still `UTF-8` and f1 still raises. Encoding is fixed at interpreter start, so an in-process arm cannot be pinned.

**F3 HIGH. Reusing a module name silently aliases the arms.**
- E-C: `SourceFileLoader("x", frozen).load_module()` then the same name for the candidate gives `a is b` = True, `a.__file__` = candidate, and `GIT_ISOLATION` present on the "frozen" object. A frozen arm loaded this way runs candidate code.
- E-C2: `spec_from_file_location` without `sys.modules` registration keeps them distinct. Subprocess avoids the question.

**F4 MEDIUM. Default repo paths come from the blob's location, not the lane.**
- `main()` computes `here = Path(__file__).resolve().parent.parent` (`frozen/…:814`; `current:888`). Lane default = `here`, fleet default = `here.parent`.
- E-A: blob at `<lane>/tools/` with no args → rc 2. With `--fleet-repo` only → rc 0. Blob in a temp dir with no args → rc 2 for every fixture. A harness that omits repo args turns every arm into could-not-evaluate, and the grid looks like uniform refusal.
- Hazard (code-derived, NOT executed to avoid touching real repos): a blob at the real `kama-shokunin/tools/` with no args would audit the real lane and the real fleet, because `here.parent` is `/home/vgpnk/Projects/shokunin`, which is a git repo (see Real repos below). The contract forbids this for fault fixtures. Always pass explicit `--lane-repo`/`--fleet-repo` to fixtures.

**F5 MEDIUM. In-process import writes bytecode.**
- E-D: in-process import writes `__pycache__/report-landing-audit.cpython-314.pyc` beside the blob. A blob placed in the lane's `tools/` would add an untracked directory to the lane checkout. `-B` subprocess and plain script runs write nothing.

**F6 MEDIUM. cwd and relative paths change results.**
- E-E, both arms: `--report 1=draft.md` from cwd `/tmp` → rc 2 `cannot read draft.md`. From the fixture root → rc 0. Relative `--lane-repo lane` from the wrong cwd → rc 2. Candidate matches frozen here.
- `Path(__file__)` in F4 is resolved at call time, so a relative blob path plus `os.chdir` moves the defaults. In-process `os.chdir` is process-global.

**F7 MEDIUM. Shared side-effect files create false attribution.**
- E-G: f5's `core.sshCommand` writes `<fixture>/marker`. After the frozen run, a candidate run without reset reports `marker True`, which looks like "candidate executed the command". After reset: no marker. Reset markers before every run.

**F8 LOW (confirmed). Harness `GIT_*` env never reaches either arm.**
- Both `git_env()` implementations strip `GIT_*` (`frozen:79-84`, `current:98-104`). E-H: with `GIT_DIR=/nonexistent` and `GIT_CONFIG_GLOBAL=/etc/passwd` in the harness env, both arms return rc 0. You cannot pin git via `GIT_*`. The usable pins are PATH (only `/usr/bin/git` 2.56.0 on PATH), `LC_*`/`LANG`, `PYTHONUTF8`/`PYTHONCOERCECLOCALE`, cwd, and argv.

**F9 LOW (confirmed). The selftest is loader-neutral.**
- E-J: `--selftest` via subprocess gives frozen `selftest cases=50 failed=0` and candidate `cases=50 failed=0`, with identical case-name sets. E-J2: in-process frozen `selftest()` gives rc 0, 50 cases, `GIT_DIR` restored. Still do not run the selftest in the same process as fixtures.

**F10 STRUCTURAL. The candidate is a moving target.**
- The lane file changed at 12:15:19, 12:15:39, and 12:17:56 during this review. Pin the candidate by committed blob (or copied file) with sha256 and git blob id, and write both into every grid manifest. Do not reuse these numbers for a different revision.

**F11 CANDIDATE SCOPE CHANGE. The f5 flip comes from a new refusal, not from `--no-lazy-fetch`.**
- `current:426-448` `check_history_repo` (called at `current:476`) refuses `extensions.partialclone`, `remote.*.promisor`, promisor packs, shallow repos, grafts, non-sha1, and non-top-level paths. f5 now gives rc 2 `…/lane: partial clone (extensions.partialclone)` with no marker (`f5-lazyfetch.cand.err`). The earlier 4494764e candidate had no such check and gave rc 1 without marker. So the f5 row changed between versions.
- Direct git, no auditor, same promisor fixture: plain `cat-file --batch-check` runs the `sshCommand` (marker YES). With `git --no-lazy-fetch`, no marker. The flag works at git level, but no grid fixture isolates it, because the refusal fires first. Attribute f5 to the partial-clone refusal in any report.
- "Controls unchanged" must list the shapes the new checks refuse (shallow, grafted, partial, non-top-level, non-sha1). Each one flips a frozen rc 0 control to candidate rc 2 by design. I did not run any such control.

**F12 (read-only check). Real repos pass the new shape checks.**
- `…/kama-shokunin` and `…/shokunin` both report: sha1, not shallow, no grafts, no promisor packs, no `extensions.partialclone` or `remote.*.promisor` keys, top-level. The historical ledger was not run.

**F13 LOW residual (identical in both arms). Text-mode output uses the stdout encoding.**
- E-K: a non-ASCII errata token under ASCII stdout gives `UnicodeEncodeError` traceback, exit 1, and no summary line in both arms. Exit stays 1 because such runs already fail (unmatched or invalid errata). Not a verdict flip, but the summary is lost. `--json` (ASCII-escaped) was not run under ASCII.

**F14 (code-read, not executed). Live state in ledger runs.**
- Frozen resolves `--branch` separately at each use (`round_commits` at `frozen:147`, `load_source_urls` at `:208`, `load_errata` at `:339`) and reads fleet `HEAD` (`ls-tree HEAD` at `:381`, `show HEAD:rel` at `:266`, cutoff `log` at `:166`). A lane tip moving mid-run can mix commits. Candidate pins the tip once (`resolve_branch` at `current:451`, `tip` at `:477`) but still reads fleet `HEAD`. For a ledger run, pass `--branch <sha>` (expected to work for both; not executed) and audit a fixed fleet snapshot clone.

**F15 (code-read). Drafts use the wall clock as cutoff.**
- `cutoff = int(time.time())` (`frozen:275`, `current:308`) applies to `--report` drafts with no fleet commit. Fixtures use 1000-3000 epoch seconds, so nothing flips. A future-dated fixture would make verdicts clock-dependent.

## Recommended loader and identity checklist

```python
PINNED = {"PATH": "/usr/bin:/bin", "HOME": scratch_home,     # only /usr/bin/git on PATH
          "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8", "PYTHONUTF8": "1"}
subprocess.run([sys.executable, "-B", arm_blob,
                "--lane-repo", abs_lane, "--fleet-repo", abs_fleet,
                "--branch", lane_sha, "--rounds", "1", "--no-errata", "--json"],
               cwd=fixture_root, env=PINNED, stdin=subprocess.DEVNULL,
               capture_output=True, timeout=120)
```

- **Blobs:** frozen = `git show 4fe9339f:tools/report-landing-audit.py`, unmodified. Candidate = the committed blob of the candidate revision, not the mutable working tree. Copy both to `<arms>/<arm>/tools/report-landing-audit.py` at the same depth, mode 0444, and record sha256 and git blob id.
- **Fixtures:** build once under `/tmp` with fixed `GIT_*_DATE`, verify rebuild SHAs equal, and run both arms sequentially on the same directories. Reset markers before every run. Never point at real repos.
- **Preflight canary** under PINNED: `locale.getpreferredencoding(False) == 'UTF-8'` and `sys.flags.utf8_mode == 1`. Log `git --version`, `sys.executable`, and both blob hashes in the manifest.
- **Locale sweep** is a separate frozen-only axis, labelled "baseline environment sensitivity". It is not part of the fault-grid comparison.
- **Comparison:** rc, `--json` defect kinds, and marker presence. Keep rc 1 with traceback ("crash") separate from rc 2 ("refusal") and from verdicts 0/1. Do not compare raw stderr across arms beyond the traceback class.
- **Controls to add:** `ctrl-nonascii` and `ctrl-report-utf8`. Both gave rc 0 for both arms under UTF-8 here, and the L1 probe lacks them.

## Not verified

- Full candidate diff. I read the 4494764e diff (219 lines before the 79d9e124 change) and the 79d9e124 partial diff against 4494764e. The `lookup` ref-shadow refusal (`current:162`) and `resolve_branch` precedence (`current:451`) are code-read only.
- The candidate's mailmap and `log.follow` claims. My f6 fixture did not discriminate (rc 0 for both arms), and I did not investigate further (other reviewers cover those channels).
- The historical ledger (rounds 10-22) was not run. Real-repo results are read-only config and shape checks.
- Stdin inheritance with a real remote was not exercised. I used `example.invalid`, with no network.
- `--no-lazy-fetch` support on git versions other than 2.56.0 was not tested.
- `--branch <sha>` for the ledger was code-read, not executed.

## Side effects and files written

- **Lane checkout:** only this report, `.ufo/waves/round-23/build/advice/RevFrozenArm.md` (untracked). No tracked file, index write, `.jj`, fleet root, or global config was intentionally changed. Caveat: I ran `git -C <lane> status --short` about three or four times. `status` can opportunistically refresh `.git/index` stat info. I did not use `--no-optional-locks`. No other command I ran writes to the lane.
- **Scratch (`/tmp/kama-r23-review/RevFrozenArm/`):** `frozen/report-landing-audit.py` (extracted blob), `current-snap.py` (79d9e124), `current-snap-4494764e.py`, `frozen-vs-current.diff` (4494764e), `frozen-vs-current-79d9e124.diff`, `loader_probe.py`, `loader_probe.out`, `arms/{frozen,cand}/tools/` (copies plus `__pycache__` from in-process imports), `fx/` (deterministic fixtures, `draft.md`, `errata.tsv`, `pyc-test/`, `direct-lazy/`, markers), `home/`, and per-fixture `*.json`/`*.err` results.
- No commits, pushes, jj commands, installs, updates, or subagents.
