partially — M14–M19 reproduce as 6/6 KILLED, but three NEW, behavior-changing single-line mutants in those element families SURVIVE the committed grid. Each new mutant is killed by an additional bounded witness; pristine and exact-restored bytes meet that witness. This is a detector-coverage finding, not a counterexample to the pristine auditor’s invariant or a score/integration judgment.

# MutRetestC — isolated mutation retest

## Scope, axes, and provenance

Axes: (1) correct verdict versus refusal, (2) detector sensitivity, (3) exact restoration/lane noninterference, and (4) bounded repeatability. Only assigned mutation probes were performed. Independent runs used concurrent, separate fresh fixtures; no subagents were dispatched.

Target: `245a37f69628c2c6bb29bbf17897d8fb5946c857` (`245a37f6`). The following commands completed successfully:

```text
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/MutRetestC-2
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -C /tmp/kama-r23w2/MutRetestC-2 rev-parse HEAD
245a37f69628c2c6bb29bbf17897d8fb5946c857
```

All subsequent commands below ran in `/tmp/kama-r23w2/MutRetestC-2`. Runtime observations: `git --version` → `git version 2.56.0`; `python3 --version` → `Python 3.14.8`. No tools were installed or updated. No REA devices, other runtime, commits/pushes/jj commands against the clone or lane, or global configuration changes were used. The prescribed test programs make commits only in their fresh fixture repositories, with explicit fixture identity and global/system Git configuration disabled.

Complete captured commands, exit codes, stdout, stderr, actual grid rows, and hashes for new-mutant pristine/mutated/restored runs are in:

`.ufo/waves/round-23/falsify/out/MutRetestC-2/results.json`

SHA-256: `f14f02dd2903eb0065146f720de1df572707175116fa2de22d38b0b09f9d9f3a` (182358 bytes).

## Assigned M14–M19 retest

Each command used the prefix `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. All six wrapper commands exited **0**; every wrapper’s own pristine grid passed. A killed mutant’s inner grid exit is **1**, not an infrastructure failure. Exact command suffixes and observed program output:

```text
python3 tests/report-audit/isolation-mutants.py --only M14-promisor-config
M14-promisor-config KILLED grid=1 rows=['F06-lazy-fetch-command']
mutants=1 killed=1 surviving=[]

python3 tests/report-audit/isolation-mutants.py --only M15-object-format
M15-object-format KILLED grid=1 rows=['F15-sha256-lane']
mutants=1 killed=1 surviving=[]

python3 tests/report-audit/isolation-mutants.py --only M16-top-level
M16-top-level KILLED grid=1 rows=['F21-nested-subdirectory-lane']
mutants=1 killed=1 surviving=[]

python3 tests/report-audit/isolation-mutants.py --only M17-ref-shadow
M17-ref-shadow KILLED grid=1 rows=['F13-ref-named-abbreviation']
mutants=1 killed=1 surviving=[]

python3 tests/report-audit/isolation-mutants.py --only M18-branch-heads
M18-branch-heads KILLED grid=1 rows=['F12-tag-shadows-branch']
mutants=1 killed=1 surviving=[]

python3 tests/report-audit/isolation-mutants.py --only M19-errata-hex
M19-errata-hex KILLED grid=1 rows=['F17-errata-revision-correction']
mutants=1 killed=1 surviving=[]
```

Definitions at `245a37f6`: `tests/report-audit/isolation-mutants.py:45-57`. The wrapper writes each mutant into its own temporary file (`:99-109`), so the clone’s original auditor was never changed by these six runs. An explicit final current-arm grid on that original auditor also exited 0 with 26/26 faults, 8/8 controls, zero violations, tracebacks, auditor command executions, and timeouts.

## Three new surviving mutants

Each mutation changed exactly one displayed source line in its own initially byte-identical copy under `.mut-probe-C/`. No mutant was combined with another. The existing detector was invoked unchanged:

```text
/usr/bin/python3 tests/report-audit/repo-state-grid.py --arm current --current /tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/<NAME>.py --json
```

For **each of the three names**, this same command ran on pristine, mutated, and restored bytes. All nine grid invocations exited **0**, reporting:

```text
faults_met=26 faults=26 controls_met=8 controls=8 violations=0
tracebacks=0 commands_executed=0 timeouts=0
failed_rows=[]
```

Thus all three are **SURVIVED by the committed grid**, not inconclusive baselines. Open/tradeoff rows remain ungraded; the statement above concerns the 34 graded rows only.

### N01-origin-only-promisor — M14 family

Exact one-line replacement at `tools/report-landing-audit.py:447` at `245a37f6`:

```diff
-                r"remote\..+\.promisor", line):
+                r"remote\.origin\.promisor", line):
```

Plausible defect: treating only `origin` as a promisor remote. Existing F06 sets both `extensions.partialClone=origin` and `remote.origin.promisor=true` (`tests/report-audit/repo-state-grid.py:277-285`); the untouched extension check masks the narrowed regex. F23 also retains its independent promisor-pack refusal. The grid still passes.

Additional witness: clean SHA-1 lane/fleet fixture; set only `remote.backup.promisor=true` and `remote.backup.url=ssh://example.invalid/x.git`; verify no `extensions.partialclone` key and no `.promisor` marker. There are no missing objects and no network operation is requested. The contract at `tools/report-landing-audit.py:48-55,445-448` requires the configured promisor repository to be refused.

Observed auditor exits pristine/mutated/restored: **2 / 0 / 2**. Pristine stderr was:

```text
could-not-evaluate: /tmp/mut-retest-c-gap-06ck35jf/lane: partial clone (remote.backup.promisor)
```

Mutant stdout reported `status=clean`, `defects=0`, `required_commits=1`; stderr was empty. The added detector exits **0 / 1 / 0** and therefore kills the mutant.

Grid row that should exist: `FX-C1-promisor-nonorigin-only`, kind `fault`, expected exit **2**, required diagnostic `remote.backup.promisor`. Its fixture must omit the extension and pack-marker signals so the remote-name regex is independently necessary.

### N02-skip-fleet-history — M15/M16 repository-validation family

Exact one-line replacement at `tools/report-landing-audit.py:475` at `245a37f6`:

```diff
-    for repo in (lane_repo, fleet_repo):
+    for repo in (lane_repo,):
```

Plausible defect: validating only the lane and forgetting the other audited repository. Existing format and top-level rows exercise the lane (`tests/report-audit/repo-state-grid.py:390-395,556,564`); no graded row requires `check_history_repo(fleet_repo)` to run.

Additional witness: SHA-1 lane with one cited commit; **SHA-256 fleet** containing its otherwise ordinary report. The fixture verifies fleet object format `sha256` and a 64-hex fleet HEAD. Expected refusal is the same non-SHA-1 contract, applied to the other repository, not a new contract.

Observed auditor exits pristine/mutated/restored: **2 / 0 / 2**. Pristine stderr was:

```text
could-not-evaluate: /tmp/mut-retest-c-gap-d_qzq59k/fleet: object format 'sha256', not sha1
```

Mutant stdout reported `status=clean`, `defects=0`, `required_commits=1`; stderr was empty. Added detector exits **0 / 1 / 0**.

Grid row that should exist: `FX-C2-sha256-fleet`, kind `fault`, expected exit **2**, required diagnostic `object format 'sha256'`. Keep the lane ordinary SHA-1 to isolate fleet validation.

### N03-casefold-branch — M18 branch-qualification family

Exact one-line replacement at `tools/report-landing-audit.py:456` at `245a37f6`:

```diff
-                   f"refs/heads/{branch}^{{commit}}").strip()
+                   f"refs/heads/{branch.lower()}^{{commit}}").strip()
```

Plausible defect: normalizing a branch name before qualifying it. Existing F12 uses lower-case `master` (`tests/report-audit/repo-state-grid.py:363-368`), which is unchanged by `.lower()`.

Additional witness: `refs/heads/topic` points at the cited first commit, while `refs/heads/Topic` points at a later pre-report `round-1: more` lane commit omitted from the report. Both exact refs are verified, then the auditor is invoked with `--branch Topic`. Correct qualification must retain the selected name (`tools/report-landing-audit.py:451-459`).

Observed auditor exits pristine/mutated/restored: **1 / 0 / 1**. Pristine/restored kinds were exactly `['landed-omitted']`; the mutant reported `status=clean`, `defects=0`, `required_commits=1`. All stderr was empty. The witness detector itself exits **0 / 1 / 0**: the pristine auditor’s intentional exit-1 defect verdict is the expected baseline, not a detector failure.

Grid row that should exist: `FX-C3-case-distinct-branch-selection`, kind `fault`, invoke `--branch Topic`, expected exit **1**, kinds `['landed-omitted']`. The current grid runner only forwards round/errata-related extras (`tests/report-audit/repo-state-grid.py:600-609`), so this row also needs branch-argument forwarding in that runner. The scratch witness already exercises the actual CLI; no production or grid change was integrated.

## Additional detector and restoration evidence

The additional detector is `.mut-probe-C/gap-witnesses.py` in the clone, which reuses committed grid fixture helpers and runs each auditor as a subprocess with a **30-second** timeout. Exact command, separately for each name and each byte phase:

```text
/usr/bin/python3 /tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/gap-witnesses.py --current /tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/<NAME>.py --only <NAME>
```

All nine additional-witness runs completed without tracebacks or timeouts. Grid subprocesses had a 180-second outer bound; witness subprocesses a 90-second outer bound. The prescribed six wrapper tool calls had 300-second bounds. Restorations were in a `finally` block, before running the restored detectors.

| Copy | Pristine SHA-256 | Actual mutated SHA-256 from grid | Exact-restored SHA-256 |
|---|---|---|---|
| N01-origin-only-promisor | P | `e70f4752091dcfc3024f366c8e3e998e2b285eec30a8100ededf569ba441513e` | P |
| N02-skip-fleet-history | P | `2d1a4fb59a9f89b0b2ae975aa7266d8c6c04a795bff7fc072d27474985cde65d` | P |
| N03-casefold-branch | P | `04c9441a73441f589ceece9c9dc1d8506cf465c5773158241ca2b8269dc8bfd2` | P |

`P = f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.

Independent `sha256sum` before/after also observed P for the original `tools/report-landing-audit.py`; final hashes of all three restored copies were P. The unmodified clone’s grid and mutant driver before/after hashes were respectively:

- `tests/report-audit/repo-state-grid.py`: `72c1e53083a33da9d5beb065c2483f3c1456c1489b6cca26f2842453f74836da`.
- `tests/report-audit/isolation-mutants.py`: `67905fba80566d5407add57d43301f60b69d71dcf9d166fdc0dd0aacbee74d17`.

Scratch witness script SHA-256: `6a56ad75ca413bf5be081a3321932552bc87563510fe670839783685b8f2fc33`.

For M14–M19 the original file was unchanged throughout; their temporary mutant files were created/removed by the committed wrapper. I did not capture per-mutant temporary-file hashes for those six, so do not claim them. Their original-before/original-after hash and actual killed output are recorded above.

## Source anchor

Opened official Git partial-clone documentation, section “Using many promisor remotes”:

https://git-scm.com/docs/partial-clone#_using_many_promisor_remotes

Quote (8 words): “Many promisor remotes can be configured and used.” The section lists `remote.<name>.promisor = true`, corroborating why an origin-only mutation is behaviorally narrower. This source is corroboration; the recorded fixture outputs establish the local behavior.

## Boundaries and files written

Not verified: frozen-arm fairness/results; `--selftest`; rounds 10–22 ledger equivalence; other isolation-mutant selections; the Git 2.45 version floor or older Git; real network access; arbitrary repository-local channels; independent alternates/gitfile, second-section, errata-CR, or sibling-tool invariants. Existing open/tradeoff rows were traversed by the current grid but are not graded passes or new verification of their contracts. These probes do not prove mutation completeness or falsify pristine C1.

Persistent lane files written (new, scoped artifacts only):

1. `.ufo/waves/round-23/falsify/advice/MutRetestC.md` — this report, written once.
2. `.ufo/waves/round-23/falsify/out/MutRetestC-2/results.json` — complete captured evidence, written once.

Scratch files written in the isolated clone, in addition to files produced by the required `git clone`:

3. `/tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/N01-origin-only-promisor.py` — created pristine, one-line mutated, exact-restored.
4. `/tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/N02-skip-fleet-history.py` — created pristine, one-line mutated, exact-restored.
5. `/tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/N03-casefold-branch.py` — created pristine, one-line mutated, exact-restored.
6. `/tmp/kama-r23w2/MutRetestC-2/.mut-probe-C/gap-witnesses.py` — bounded additional detector.

The clone itself is the complete new tree `/tmp/kama-r23w2/MutRetestC-2/`, including its private `.git`. Test-owned transient fixture trees were under `/tmp/isolation-mutants-*`, `/tmp/repo-state-grid-*`, and `/tmp/mut-retest-c-gap-*`, removed by their temporary-directory contexts. No lane tracked file, lane index, `.jj`, sibling source, global config, or domain source was written.

Tooling note: a raw-reader formatting mismatch was reported once to `xd://report_issue`. Raw ranged reads included a display footer and omitted terminal newlines; reconstruction was accepted only after its SHA-256 matched the independently observed pristine hash. No installation or update resulted.
