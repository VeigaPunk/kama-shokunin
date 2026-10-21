# OldGitFloor: git floor for `--no-lazy-fetch` and `--no-replace-objects` (round-23)

Seat: CloseKama22.OldGitFloor (executor, leaf). Base for comparison: master 4fe9339f.
Full evidence: `out/OldGitFloor/findings`, `out/OldGitFloor/probe-output.txt`, `out/OldGitFloor/provenance.txt`.

## Verdict

1. **The floor for `--no-lazy-fetch` is git 2.45.0, not 2.44.** Git 2.44.0 refuses the option.
2. **Fail-closed on older git: yes.** Global `--no-lazy-fetch` on git 2.24.1, 2.43.2 and 2.44.0 exits 129 with
   `unknown option: --no-lazy-fetch` plus usage, prints nothing on stdout, and does not run the repo-configured
   promisor command. Nothing is evaluated: no output, no fetch (marker absent).
3. **`--no-replace-objects` is not a floor problem.** It is accepted and honored on every tested binary, 2.24.1
   through 2.56.0. It is documented since git.txt v1.7.0 and absent at v1.6.5.
4. **Do not use the env form as an older-git fallback.** `GIT_NO_LAZY_FETCH=1` is silently ignored on 2.43.2 and
   2.44.0. There the repo-configured command runs and `cat-file` exits 0 with `missing`. It is honored only on
   2.45.0 and 2.56.0.
5. **No tested mechanism is fail-closed below 2.45 except refusal.** Omitting the flag runs the promisor command
   on every version tested. The env form fails open. Only the flag itself (refusal) or a version gate in the tool gives a typed refusal.

## Measured matrix (`out/OldGitFloor/probe-output.txt`; script `out/OldGitFloor/probe-floor.sh`)

| case | 2.24.1 | 2.43.2 | 2.44.0 | 2.45.0 | 2.56.0 |
|---|---|---|---|---|---|
| L0 no flag (control) | 128 fatal, command ran | 0 "missing", command ran | 0 "missing", ran | 0 "missing", ran | 0 "missing", ran |
| L1 `git --no-lazy-fetch cat-file --batch-check` | 129 unknown option, no run | 129, no run | 129, no run | 0 "missing", no run | 0 "missing", no run |
| L2 `cat-file --batch-check --no-lazy-fetch` | 129 | 129 | 129 | 129 | 129 |
| L3 `GIT_NO_LAZY_FETCH=1` env | 128, **ran (ignored)** | 0 "missing", **ran (ignored)** | 0 "missing", **ran (ignored)** | 0 "missing", no run (honored) | 0 "missing", no run (honored) |
| R0 control (replacement active) | size 133 | 133 | 133 | 133 | 133 |
| R1 `--no-replace-objects` | size 107 (orig) | 107 | 107 | 107 | 107 |
| R2 env `GIT_NO_REPLACE_OBJECTS=1` | 107 | 107 | 107 | 107 | 107 |
| R3 `-c core.useReplaceRefs=false` | 107 | 107 | 107 | 107 | 107 |

L2 refuses on every version, so the flag is global-position only. Git 2.44.0 and below exits 129 with no output and no fetch;
git 2.45.0 and above accepts it.

## Consumer effect: `tools/report-landing-audit.py`

Working copy, sha256 `79d9e124e8171b47dc69f5af657bcf938fcb77a4915f7758d50eccd6c72f226c`:

- `GIT_ISOLATION` (lines 91-95) starts with `--no-replace-objects, --no-lazy-fetch`. Every `git()` call
  (line 113) carries it.
- On 2.43.2 the first call (`rev-parse --show-object-format`) returns rc 129. `git()` raises `EvalError` (line 119),
  `main()` prints `could-not-evaluate: ... rc=129 unknown option: --no-lazy-fetch` and exits 2 (lines 909-911). Stdout is empty.
  Evidence: `out/OldGitFloor/e2e/err._tmp_kama-r23-ogf_probe_bin_v2.43.2.txt`.
- Control under host git 2.56.0 passes that call and fails later only because the trivial fixture lacks the report file.
  Evidence: `out/OldGitFloor/e2e/err._usr_bin.txt`.

So on git below 2.45.0 the tool refuses at its first git call, and every call carries the flag, so no run reaches a verdict.
The base blob (4fe9339f) has no `GIT_ISOLATION`, so it has no such floor. Its fault-grid exposure comes from the L1 probe brief and was not re-measured here.

The other six `GIT_ISOLATION` tokens return rc 0 on 2.24.1 through 2.45.0 when `--no-lazy-fetch` is removed.
That is acceptance only. Unknown config keys are silently ignored by git, so it does not prove they are honored.
Only `--no-lazy-fetch` raises the floor.

## Floor implication (decision for L1, not made here)

- Keeping the flag makes the audit tool require git >= 2.45.0. Older git gets exit 2 and a message that names the flag.
  That is fail-closed but refuses every run.
- If older git must be supported, the only fail-closed route is a version gate that refuses before any repo access
  (for example, parsing `git --version`). I did not implement or measure that.
- Do not fall back to `GIT_NO_LAZY_FETCH`, and do not drop the flag on old git: both were measured to execute the
  repo-configured command.
- Note: a promisor fetch failure without the flag is `missing` at exit 0 on 2.43.2 through 2.56.0, and exit 128 on
  2.24.1. The flag is what turns this into a non-fetch on >=2.45.0.

## Provenance

- git.txt: `--no-replace-objects` absent at v1.6.4 and v1.6.5; present at v1.7.0 line 260, v2.43.0, v2.44.0, v2.45.0.
- git.txt: `--no-lazy-fetch` absent at v2.43.0 and v2.44.0 (0 matches); present at v2.45.0 lines 182-187
  ("equivalent to setting the GIT_NO_LAZY_FETCH environment variable to 1") and at v2.46.0 line 183.
- RelNotes/2.45.0.txt line 120 documents the option, under the "Performance, Internal Implementation, Development
  Support etc." heading (line 105). RelNotes/2.44.0.txt has no "lazy" match.
- Binaries: official Arch Linux Archive packages (archive.archlinux.org), extracted with bsdtar into /tmp. No
  pacman, no installs. sha256 of the packages is recorded in `out/OldGitFloor/findings`.

## Not verified

- Signatures are unverified. The host keyring lacks the packager key, and I did not import keys.
- 2.43.0 and 2.43.1 were not run; only 2.43.2 was. No runtime older than 2.24.1 was tested, so the
  `--no-replace-objects` floor below 2.24.1 rests on git.txt v1.7.0 documentation.
- The consumer test used trivial /tmp fixtures, not the full fault grid. The 2.44.0 consumer path was checked
  only at argv level.
- No fault fixture was run against the real lane or fleet repos.

## Installs and files

Installs: none. Downloads only: git 2.24.1-4, 2.43.2-1, 2.44.0-1 and 2.45.0-1 packages and their `.sig` files into
/tmp/kama-r23-ogf/pkg. Scratch repos are under /tmp/kama-r23-ogf. Nothing written to the system, `~/.local/bin`,
or the lane's `.git`/`.jj`.

Written by this seat:
- `.ufo/waves/round-23/build/advice/OldGitFloor.md` (this report)
- `.ufo/waves/round-23/build/out/OldGitFloor/findings`
- `.ufo/waves/round-23/build/out/OldGitFloor/probe-floor.sh`
- `.ufo/waves/round-23/build/out/OldGitFloor/probe-output.txt`
- `.ufo/waves/round-23/build/out/OldGitFloor/cases/*.stderr` (40 files)
- `.ufo/waves/round-23/build/out/OldGitFloor/provenance.txt`
- `.ufo/waves/round-23/build/out/OldGitFloor/e2e/` (2 stderr files, 2 empty stdout files)

Checks for the main agent to run: re-run `probe-floor.sh` with the same arguments once the candidate
`GIT_ISOLATION` is final, and rerun the audit tool under PATH pointing at a git 2.44.0 build. I ran neither as a
gate; this seat ran only the probes above.
