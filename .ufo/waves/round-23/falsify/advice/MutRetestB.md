partially — the six existing M07/M09–M13 kill results reproduce, but the unchanged grid misses all three new, behavior-changing single-line mutants below. This is a detector-coverage finding, not a demonstrated failure of pristine C1 and not permission to change the contract.

# Scope and axes

Seat: `CloseKama22.MutRetestB-2`. Axes: verdict stability; bounded execution without tracebacks/program execution; detector sensitivity; exact byte restoration. No production fix, integration, commit, push, nested agent, other runtime, or REA device was invoked.

The required isolated clone was created with:

```sh
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/MutRetestB
git -C /tmp/kama-r23w2/MutRetestB rev-parse HEAD
```

Observed exit 0; HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857`. All source references below are at that revision. Runtime: `git version 2.56.0`; `Python 3.14.8`. No tools were installed or updated. All fault repositories were fresh temporary repositories using the grid's isolated configuration and explicit fixture identity.

# Existing assigned mutants

Command, cwd `/tmp/kama-r23w2/MutRetestB`:

```sh
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 tests/report-audit/isolation-mutants.py --only M07-log-mailmap --only M09-strict-default --only M10-log-surrogates --only M11-listing-surrogates --only M12-shallow-check --only M13-grafts-check --json
```

Observed exit 0, elapsed 85.61 seconds, output: `pristine: passed`, `mutants: 6`, `killed: 6`, `surviving: []`. Every mutant had `grid_exit: 1`, `killed: true`, `error: null`, with the following failed rows:

| Mutant | Auditor location | Failed grid rows |
|---|---|---|
| M07-log-mailmap | `tools/report-landing-audit.py:96` | F14-mailmap-fifo |
| M09-strict-default | `tools/report-landing-audit.py:108` | F02-report-invalid-utf8; F16-errata-invalid-utf8 |
| M10-log-surrogates | `tools/report-landing-audit.py:184` | F18-bad-byte-unrelated-subject; F19-bad-byte-round-subject |
| M11-listing-surrogates | `tools/report-landing-audit.py:418` | F20-quotepath-open-range |
| M12-shallow-check | `tools/report-landing-audit.py:437` | F10-shallow-lane |
| M13-grafts-check | `tools/report-landing-audit.py:441` | F11-grafts-lane |

There is **no M08 entry** in `tests/report-audit/isolation-mutants.py:28-71`; it was not silently counted as tested. Mutation definitions for this slice are at lines 35-44. The driver's acceptance of grid failures is at lines 109-112; these six were determinate row failures, not pristine failures or mutant grid exit 2.

Recorded results and exact built-in replacements: `out/MutRetestB/existing-mutants.json`. Its built-in mutant hashes are explicitly marked as derived from the executed driver's replacements, not separately measured ephemeral-file hashes. That driver writes temporary mutant files without changing the auditor (`tests/report-audit/isolation-mutants.py:99-112`).

# New single-line mutants

Each new source copy initially contained the exact committed auditor bytes. Only its indicated line was edited. Three independent source copies were exercised concurrently, with no sibling or lane source edits.

## N01-ignore-log-bytes — SURVIVED existing grid

Family: M10 log-output decoding. Location: `tools/report-landing-audit.py:184`.

Exact whole-line replacement, Python string notation preserving indentation:

```text
old: '              branch, errors="surrogateescape")'
new: '              branch, errors="ignore")'
```

Existing full grid on the mutant: **exit 0**, faults **26/26**, controls **8/8**, violations **0**, tracebacks **0**, executions **0**, timeouts **0**.

Missing row: **NEW-invalid-byte-author-not-lane**. Add a raw commit whose author name is the bytes `kama-\xffshokunin`, subject `round-1: foreign author`, author time 1100, over a cited normal lane commit. Prove Git emits the raw invalid author byte. Expected auditor exit **0**, no defects: this author is not exactly `kama-shokunin`. Ignoring bad bytes turns that distinct author into the lane identity and invents an omission.

Bounded witness outputs, pristine / mutant / restored:

- exit **0 / 1 / 0**;
- defect kinds **[] / ["landed-omitted"] / []**;
- witness expectation met **true / false / true**.

Why current rows miss it: F18/F19 mutate the subject, not the author (`tests/report-audit/repo-state-grid.py:414-428`). Dropping a non-prefix bad subject byte still leaves their tested classification unchanged. Author equality is behavior-bearing at `tools/report-landing-audit.py:198`.

## N02-ignore-listing-bytes — SURVIVED existing grid

Family: M11 report-path listing decoding. Location: `tools/report-landing-audit.py:418`.

```text
old: '                         "--", ".ufo/reports", errors="surrogateescape")'
new: '                         "--", ".ufo/reports", errors="ignore")'
```

Existing full grid on the mutant: **exit 0**, faults **26/26**, controls **8/8**, violations **0**, tracebacks **0**, executions **0**, timeouts **0**.

Missing row: **NEW-invalid-byte-round-directory**. Alongside valid round 1, commit a raw-byte path `.ufo/reports/round-\xff2/kama.md`, set fleet-local `core.quotePath=false`, and use `--rounds 1-`. Prove the listing emits the byte and the sanitized round-2 path does not exist. Expected exit **0**, selecting only the real round 1. Ignoring the byte manufactures a round-2 candidate and then tries to read a nonexistent report.

Bounded witness outputs, pristine / mutant / restored:

- exit **0 / 2 / 0**;
- defect kinds **[] / null / []**;
- witness expectation met **true / false / true**.

Observed mutant stderr tail includes: `rc=128 fatal: path '.ufo/reports/round-2/kama.md' does not exist in 'HEAD'`.

Why current F20 misses it: its invalid byte is in `caf\xe9.md`, which remains outside the round-directory pattern even when dropped (`tests/report-audit/repo-state-grid.py:431-446`). The open-range pattern is at `tools/report-landing-audit.py:419-422`.

## N03-repeat-lane-health — SURVIVED existing grid

Family: M12/M13 repository-health refusal coverage. Location: `tools/report-landing-audit.py:475`.

```text
old: '    for repo in (lane_repo, fleet_repo):'
new: '    for repo in (lane_repo, lane_repo):'
```

This is a single-element repository-selection error: the lane gets checked twice and the fleet never gets checked. It is not a special-case fixture exception.

Existing full grid on the mutant: **exit 0**, faults **26/26**, controls **8/8**, violations **0**, tracebacks **0**, executions **0**, timeouts **0**.

Missing row: **NEW-shallow-fleet-cutoff**. Publish a report at time 2000 citing the lane commit at 1000; add uncited lane work at 2500; update the fleet report at 3000. Put the fleet tip in its `.git/shallow`. Prove fleet history has one visible commit and the first-add query now returns 3000. Expected auditor exit **2**, stderr containing `shallow repository`. Without fleet refusal, previously post-report work becomes an apparent omission.

Bounded witness outputs, pristine / mutant / restored:

- exit **2 / 1 / 2**;
- defect kinds **null / ["landed-omitted"] / null**;
- witness expectation met **true / false / true**.

Restored stderr: `could-not-evaluate: /tmp/kama-r23-MutRetestB-N03-repeat-lane-health-m6ij18ds/fleet: shallow repository`.

Why current rows miss it: F10 and F11 establish shallow/grafted state only in the lane (`tests/report-audit/repo-state-grid.py:348-360,551-552`). The production refusal itself is at `tools/report-landing-audit.py:436-441`; the fleet report cutoff is at lines 203-206. A corresponding fleet-grafts row would strengthen the same missing repository dimension, but was **not run** in this assignment.

# Detector commands and actual phase results

For each phase, this driver ran the same full existing grid plus the same bounded missing-row witness for each of the three copies. The full grid was not modified. The witness reused `run_case` and its 30-second subprocess bound (`tests/report-audit/repo-state-grid.py:600-635`); each full-grid invocation additionally had a 180-second outer bound.

Exact commands executed from the clone, with edits/restoration between commands:

```sh
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 mutation-probes/probe-detectors.py --phase pristine --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/MutRetestB/pristine.json
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 mutation-probes/probe-detectors.py --phase mutated --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/MutRetestB/mutated.json
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 mutation-probes/probe-detectors.py --phase restored --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/MutRetestB/restored.json
```

Observed driver exits: **0 / 0 / 0**; elapsed **7.76 / 7.97 / 7.70** seconds. Driver exit 0 means records were captured, not that its additional witnesses passed. Witness `met` and auditor exits above are the verdict evidence.

Within every phase, each copy used:

```text
python3 tests/report-audit/repo-state-grid.py --arm current --current /tmp/kama-r23w2/MutRetestB/mutation-probes/<name>.py --json
```

All **nine** full-grid runs exited **0** with faults **26/26**, controls **8/8**, no graded violations, tracebacks, recorded executions, or timeouts. All three new mutants therefore **survived the existing grid**, while all three were **killed by their proposed additional witnesses** after passing pristine and restored witnesses. All witness observations also had `traceback=false`, `executed=false`, `timed_out=false`.

The grid's graded comparison is explicit at `tests/report-audit/repo-state-grid.py:627-630`; open/tradeoff rows are not promoted to graded passes by this report.

# Restoration and hashes

Common pristine/restored SHA-256, called H0 below:

```text
f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7
```

| Source copy | Pristine | Mutated measured SHA-256 | Restored |
|---|---|---|---|
| N01-ignore-log-bytes.py | H0 | `f8ca890b9fe242b56afeffbd4ca5486a86ee23ab639ca22ce95610d46824668b` | H0 |
| N02-ignore-listing-bytes.py | H0 | `881e319f892676bc7063d6ee7f6a7a4e6980e65db336ffff1903842d676d0324` | H0 |
| N03-repeat-lane-health.py | H0 | `ae0753de3e49ebad640e233a9f0026e318ff136447564af5896085c1bee42548` | H0 |

Each phase record includes before/after hashes around its detectors; they match within every run. After exact inverse edits, this command returned H0 for the original auditor and every copy:

```sh
sha256sum tools/report-landing-audit.py mutation-probes/N01-ignore-log-bytes.py mutation-probes/N02-ignore-listing-bytes.py mutation-probes/N03-repeat-lane-health.py mutation-probes/probe-detectors.py
```

The driver hash was `da1cdb8343b54438859077b32c551acc5d169c9b22463bf161a6b0147641a2fd`. No mutation remains applied; the clone's original `tools/report-landing-audit.py` was never edited.

# External documentation evidence

- URL: https://docs.python.org/3/library/codecs.html#error-handlers — quote (10 words): “Ignore the malformed data and continue without further notice.” This supports why `ignore` is not a lossless substitute for `surrogateescape`.
- URL: https://git-scm.com/docs/git-log — quote (12 words): “Use mailmap file to map author and committer names and email addresses”. This identifies the M07 configuration family; the observed grid failure, not the documentation, establishes its kill.

# Files written and limits

Persistent authored files, in addition to repository contents created by the required `git clone`:

1. `/tmp/kama-r23w2/MutRetestB/mutation-probes/N01-ignore-log-bytes.py` — created, single-line mutated, restored exactly.
2. `/tmp/kama-r23w2/MutRetestB/mutation-probes/N02-ignore-listing-bytes.py` — created, single-line mutated, restored exactly.
3. `/tmp/kama-r23w2/MutRetestB/mutation-probes/N03-repeat-lane-health.py` — created, single-line mutated, restored exactly.
4. `/tmp/kama-r23w2/MutRetestB/mutation-probes/probe-detectors.py` — fixture/recording driver, retained in the isolated clone for reproducibility.
5. `.ufo/waves/round-23/falsify/out/MutRetestB/existing-mutants.json` — captured existing-mutant findings plus explicitly derived hashes.
6. `.ufo/waves/round-23/falsify/out/MutRetestB/pristine.json` — exact full-grid stdout/stderr, exits, hashes, witness rows.
7. `.ufo/waves/round-23/falsify/out/MutRetestB/mutated.json` — same for mutants.
8. `.ufo/waves/round-23/falsify/out/MutRetestB/restored.json` — same after restoration.
9. `.ufo/waves/round-23/falsify/advice/MutRetestB.md` — this append-only report.

Temporary files were also generated and automatically removed by the unchanged mutation/grid drivers under `/tmp/isolation-mutants-*` and `/tmp/repo-state-grid-*`, and by the proposed witnesses under `/tmp/kama-r23-MutRetestB-N01-ignore-log-bytes-*`, `/tmp/kama-r23-MutRetestB-N02-ignore-listing-bytes-*`, and `/tmp/kama-r23-MutRetestB-N03-repeat-lane-health-*` (fixture worktrees and Git metadata). No lane tracked file, lane index, `.jj`, sibling source, global configuration, or credential/environment value was inspected or modified.

Not verified: frozen arm, selftest, rounds-10–22 ledger identity, other pre-existing mutants, fleet-grafts witness, open/tradeoff remediation, alternate Git/Python versions, or general repository-local attack surface beyond these detectors. These unrun checks are not passes. No production invariant, calibration score, or integration decision is inferred from surviving mutants.

Append-only precision note: the Python documentation quotation above has **9**, not 10, words; it remains within the 25-word limit. The environment statement concerns shared/persistent state and intentional inspection: per-command Git isolation variables and per-fixture identity variables were set as required, and the existing grid constructs subprocess environments. No environment dump, secret reading, or shared-shell export occurred.
