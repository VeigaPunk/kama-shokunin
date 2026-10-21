partially — the six requested retests reproduce the declared result (five killed; M02 survives), but the committed grid misses three additional harmful, single-line mutants in the replacement-reference/signature-isolation family. All three survive the full current-arm grid and are killed by bounded supplemental rows. The pristine committed auditor passes those supplemental rows; this is a coverage finding, not a demonstrated defect in the shipped auditor or an integration verdict.

## Axes and scope

- Behavioral correctness: preserve unresolved-citation/omission verdicts and prevent repository-configured program execution.
- Detector sensitivity: exercise separate Git plumbing consumers and fleet cutoff logging, not only remove an isolation flag globally.
- Isolation/restoration: private clone only; unchanged committed detectors; exact auditor-byte restoration after every new mutant.

No subagents, integrations, commits, pushes, jj commands, installs, system changes, or REA devices. Git 2.56.0; Python 3.14.8. Fixture configuration/identity comes from the committed grid's `env()` (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, explicit author/committer); supplemental fixtures reuse it. New source URLs use example.invalid only. The signature fixture's program only touches a temporary marker and exits 1.

## Identity and commands

Executed:

```text
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/MutRetestA
exit 0; Cloning into '/tmp/kama-r23w2/MutRetestA'... done.

git -C /tmp/kama-r23w2/MutRetestA rev-parse HEAD
exit 0; 245a37f69628c2c6bb29bbf17897d8fb5946c857
```

All commands below ran with cwd `/tmp/kama-r23w2/MutRetestA`.

### M01–M06 retests

Ran each exact command `python3 tests/report-audit/isolation-mutants.py --only NAME`, concurrently using Python subprocesses. Every command exited 0, stderr empty. Exact stdout:

```text
M01-replace-objects KILLED grid=1 rows=['F03-replace-hides-omission', 'F04-replace-fabricated-citation', 'F05-replace-fleet-report']
mutants=1 killed=1 surviving=[]

M02-lazy-fetch survived grid=0 rows=[]
mutants=1 killed=0 surviving=['M02-lazy-fetch']

M03-log-encoding KILLED grid=1 rows=['F22-utf16-log-cutoff']
mutants=1 killed=1 surviving=[]

M04-log-follow KILLED grid=1 rows=['F07-log-follow-cutoff']
mutants=1 killed=1 surviving=[]

M05-log-showroot KILLED grid=1 rows=['F08-log-showroot-cutoff']
mutants=1 killed=1 surviving=[]

M06-log-signature KILLED grid=1 rows=['F09-signature-program']
mutants=1 killed=1 surviving=[]
```

Definitions: `tests/report-audit/isolation-mutants.py:28-34` at 245a37f6. Each invocation first passed its pristine grid. The harness writes temporary mutant copies rather than overwriting the original auditor (`:92-109`). M02's survivor status does not establish a lazy-fetch escape: promisor refusal still precedes lookup (`tools/report-landing-audit.py:426-448`). Notably, M03 is killed by F22, not F01.

## New mutation probes

The unchanged committed detector command, called **G** below:

```text
python3 tests/report-audit/repo-state-grid.py --arm current --current /tmp/kama-r23w2/MutRetestA/tools/report-landing-audit.py --json
```

Supplemental command, called **S** below:

```text
python3 tests/report-audit/mut-retest-a-probes.py --current /tmp/kama-r23w2/MutRetestA/tools/report-landing-audit.py
```

S imports the unchanged grid and uses its `run_case()` and 30-second auditor timeout (`repo-state-grid.py:600-635`). It builds fresh temporary repositories, verifies the replacement/program-execution premise, and runs all three new rows on every invocation. Thus the same bounded detector runs on pristine, mutated, and restored bytes. It is not added to the committed grid.

Observed common G output on pristine, each of N01/N02/N03, and each restoration:

```text
exit=0 faults_met=26/26 controls_met=8/8 tracebacks=0 commands_executed=0 timeouts=0 violations=0
```

Only the 34 graded rows count here. O01/O02/T01 remain ungraded; their inclusion in the JSON is not a pass claim.

### N01 — omit replacement isolation for ls-tree

Family: M01, replacement-reference neutralization. Plausible faulty assumption: tree-listing plumbing does not need replacement isolation.

Exact one-line replacement at `tools/report-landing-audit.py:114`, 245a37f6:

Old:
```python
        proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
```
New:
```python
        proc = subprocess.run(["git", *(GIT_ISOLATION[1:] if args[0] == "ls-tree" else GIT_ISOLATION), "-C", str(repo), *args],
```

- G: exit 0, 26/26 faults and 8/8 controls; **SURVIVED**.
- Missing row: **N01-source-tree-replace**. The real committed SOURCES.md does not register `https://example.invalid/source/1234567890abcdef1234567890abcdef12345678`. A replacement of the lane tip exposes a decoy tree whose SOURCES.md does. Verify ordinary ls-tree returns the decoy blob while `--no-replace-objects ls-tree` returns the original blob. The report's Notes cite that otherwise nonexistent full hash inside the URL.
- Expected auditor result: exit 1, `['unresolved-full-hash']`, no execution/traceback/timeout.
- Actual auditor result under N01: exit 0, `[]`, no execution/traceback/timeout. S exits 1 with exactly this row not met: **KILLED by supplemental row**.
- Pristine and restored S: exit 0; this row is exit 1 with `['unresolved-full-hash']` and met.
- Consumer bypassed: `load_source_urls()`'s ls-tree at `tools/report-landing-audit.py:248`; exemption construction and classification at `:256-287`.

### N02 — omit replacement isolation for raw blob reads

Family: M01. Plausible faulty assumption: an exact blob ID read cannot be redirected by replace refs.

Exact one-line replacement at `tools/report-landing-audit.py:114`, 245a37f6:

Old:
```python
        proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
```
New:
```python
        proc = subprocess.run(["git", *(GIT_ISOLATION[1:] if args[:2] == ("cat-file", "blob") else GIT_ISOLATION), "-C", str(repo), *args],
```

- G: exit 0, 26/26 faults and 8/8 controls; **SURVIVED**.
- Missing row: **N02-source-blob-replace**. Keep the true lane tip/tree intact; replace the original SOURCES.md blob with a blob registering the same fabricated source URL used in N01. Verify ordinary cat-file returns forged bytes and `--no-replace-objects cat-file` returns original bytes.
- Expected auditor result: exit 1, `['unresolved-full-hash']`, no execution/traceback/timeout.
- Actual auditor result under N02: exit 0, `[]`, no execution/traceback/timeout. S exits 1 with exactly this row not met: **KILLED by supplemental row**.
- Pristine and restored S: exit 0; this row is exit 1 with `['unresolved-full-hash']` and met.
- Consumer bypassed: exact raw-blob census read at `tools/report-landing-audit.py:256`. The existing F03–F05 replacement fixtures do not exercise a populated source census (`repo-state-grid.py:233-268`).

### N03 — re-enable signature display in fleet cutoff log

Family: M06, signature program suppression. Plausible defect: a diagnostic log option is accidentally left on the cutoff query, overriding the global `log.showSignature=false` setting.

Exact one-line replacement at `tools/report-landing-audit.py:204`, 245a37f6:

Old:
```python
    out = git(fleet_repo, "log", "--diff-filter=A", "--format=%at", "--",
```
New:
```python
    out = git(fleet_repo, "log", "--show-signature", "--diff-filter=A", "--format=%at", "--",
```

- G: exit 0, 26/26 faults and 8/8 controls; **SURVIVED**.
- Missing row: **N03-fleet-signature-program**. Put the signed report-add commit in the **fleet**, configure fleet-local `log.showSignature=true` and a harmless `gpg.program`, prove an unisolated cutoff-format log touches the marker, then remove the marker before running the auditor. This mirrors the lane signature fixture but covers the separate fleet log consumer.
- Expected auditor result: exit 0, `[]`, `executed=false`, no traceback/timeout.
- Actual auditor result under N03: exit 0, `[]`, **`executed=true`**, no traceback/timeout. S exits 1 with exactly this row not met: **KILLED by supplemental row**. Exit/kind-only checking would miss it.
- Pristine and restored S: exit 0; this row is exit 0 with `[]`, `executed=false`, and met.
- Existing F09 signs only a lane commit (`repo-state-grid.py:319-336`); cutoff logging is `tools/report-landing-audit.py:203-206`.

## Before/after hashes and restoration

Actual SHA-256 of original auditor before the six retests, and after all probes:

```text
f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7
```

The original is never overwritten by the six built-in mutant invocations; their temporary files are removed by TemporaryDirectory. For the new mutations, the actual executed bytes were hashed independently in G and S; their hashes matched. Each one-line change was reversed before the restored detectors ran.

| Probe | Before SHA-256 | Mutated SHA-256 | Restored SHA-256 | G exit pristine / mutated / restored | S exit pristine / mutated / restored |
|---|---|---|---|---|---|
| N01 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 5b45fba35146834036c4c0153b7e9dc60fbebc5adbc9bc1027299c57ce796736 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 0 / 0 / 0 | 0 / 1 / 0 |
| N02 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 313872b41c90556fc95041e1199977abc104536862547ee5822a5784990b3d31 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 0 / 0 / 0 | 0 / 1 / 0 |
| N03 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 2bdd0414414cb75a4ce6ced30b2101030c0571e4238a364a75ccc1017380f501 | f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7 | 0 / 0 / 0 | 0 / 1 / 0 |

Each immediately preceding restored run also supplies the next probe's pristine bytes/result. All restored supplemental rows have exits `[1, 1, 0]`, kinds `[['unresolved-full-hash'], ['unresolved-full-hash'], []]`, and no execution, traceback, or timeout.

Unchanged detector hashes, before and after:

```text
72c1e53083a33da9d5beb065c2483f3c1456c1489b6cca26f2842453f74836da  tests/report-audit/repo-state-grid.py
67905fba80566d5407add57d43301f60b69d71dcf9d166fdc0dd0aacbee74d17  tests/report-audit/isolation-mutants.py
```

Supplemental harness SHA-256:

```text
3385ac5d4c3fcff5ca9188e258d98f4121d2fc1b343385cfc885376771ba702f  tests/report-audit/mut-retest-a-probes.py
```

## Evidence, limitations, and files written

Raw command/exit/stdout/stderr records, including every graded/ungraded grid row and auditor hash, are in `.ufo/waves/round-23/falsify/out/MutRetestA/results.json` (six retests; sixteen detector invocations).

Execution caveats: the first six async bash requests were rejected by the host background-job cap; those commands did not execute there and were then successfully run with asyncio subprocesses. The first direct G/S invocation used a relative `--current`, producing exit 1 because the auditor path was resolved in fixture cwd (`can't open file .../tools/report-landing-audit.py`). These two baseline invocation failures are retained as `label=pristine`, treated as **inconclusive**, and never counted as kills or passes. All accepted comparisons use the absolute path shown above.

Primary-source support (each quote <=25 words):

- https://git-scm.com/docs/git-replace — “Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck).” This includes both newly covered plumbing consumers.
- https://git-scm.com/docs/git-log/2.56.0#Documentation/git-log.txt---show-signature — “Check the validity of a signed commit object by passing the signature to `gpg` `--verify` and show the output.” This explains the fleet-side execution observed under N03.

Not verified: frozen arm; M07 and later built-in mutants; selftest; rounds 10–22 ledger/no-errata comparison; other repo-local channels; older Git/Python versions; non-Linux behavior. No unrun check is counted as a pass. No claim that the existing committed auditor fails the new rows: it passed all three.

Files written or modified by this seat, beyond the required cloned checkout/Git database at `/tmp/kama-r23w2/MutRetestA/`:

1. `.ufo/waves/round-23/falsify/advice/MutRetestA.md` — this append-only report, written once.
2. `.ufo/waves/round-23/falsify/out/MutRetestA/results.json` — raw evidence, written once.
3. `/tmp/kama-r23w2/MutRetestA/tools/report-landing-audit.py` — three separate one-line mutations, each restored exactly; final bytes equal the starting bytes.
4. `/tmp/kama-r23w2/MutRetestA/tests/report-audit/mut-retest-a-probes.py` — retained runnable supplemental fixture/detector script, 111 lines; no integration into tracked detectors.
5. `/tmp/kama-r23w2/MutRetestA/tests/report-audit/__pycache__/repo-state-grid.cpython-314.pyc` — generated by importing the grid.

The invoked committed harnesses also created and removed their own `/tmp/isolation-mutants-*/M01-replace-objects.py`, `M02-lazy-fetch.py`, `M03-log-encoding.py`, `M04-log-follow.py`, `M05-log-showroot.py`, `M06-log-signature.py` and fixture trees under `/tmp/repo-state-grid-*`; supplemental fixture trees were under `/tmp/mut-retest-a-probes-*` (including temporary fake-gpg/marker files). No lane tracked files, index, .jj, global config, sibling sources, or credentials were written.
