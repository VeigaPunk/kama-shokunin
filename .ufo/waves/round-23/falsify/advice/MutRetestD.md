partially — The six assigned M20–M25 statuses reproduce: five killed, M20 survives. Three NEW single-line mutants in those element families also survive the complete committed current-arm grid. Added bounded rows distinguish pristine/mutated/restored behavior for all three. This is a detector-coverage finding, not a falsification of the unmodified C1 implementation or permission to change its contract.

# MutRetestD — round-23 scoped mutation retest

## Axes and isolation

Axes: detector sensitivity; verdict/refusal fidelity; exact-byte restoration and lane isolation. No implementation improvement was integrated.

Executed in `/tmp/kama-r23w2/MutRetestD`, cloned with:

```text
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/MutRetestD
git -C /tmp/kama-r23w2/MutRetestD rev-parse HEAD
```

Observed exit 0 and HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Runtime observations: `git version 2.56.0`; `Python 3.14.8`. No installs/updates, subagents, commits, pushes, jj commands, REA devices, global configuration edits, or lane tracked-file edits.

All fault repositories were fresh `/tmp` fixtures. Commands used per-process `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`; grid helpers set explicit author/committer identities (`tests/report-audit/repo-state-grid.py:43–80` at `245a37f6`). No real network service was contacted by these added fixtures; the partial clone fixture uses a local `file://` repository.

## Assigned commands and actual outputs

Working directory for each command: `/tmp/kama-r23w2/MutRetestD`. These six independent commands ran concurrently:

```text
python3 tests/report-audit/isolation-mutants.py --only M20-log-sha-shape
python3 tests/report-audit/isolation-mutants.py --only M21-newlines
python3 tests/report-audit/isolation-mutants.py --only M22-promisor-pack
python3 tests/report-audit/isolation-mutants.py --only M23-strict-decode-catch
python3 tests/report-audit/isolation-mutants.py --only M24-catch-all
python3 tests/report-audit/isolation-mutants.py --only M25-timestamp-shape
```

Every outer command exited **0**, with empty stderr. Outer exit 0 means the experiment completed, not that the mutant passed. Exact first output lines:

```text
M20-log-sha-shape survived grid=0 rows=[]
M21-newlines KILLED grid=1 rows=['C08-cr-only-report']
M22-promisor-pack KILLED grid=1 rows=['F23-promisor-pack-without-config']
M23-strict-decode-catch KILLED grid=1 rows=['F02-report-invalid-utf8', 'F16-errata-invalid-utf8']
M24-catch-all KILLED grid=1 rows=['F24-huge-round-number']
M25-timestamp-shape KILLED grid=1 rows=['F26-huge-author-timestamp']
```

Each command's second line reports `mutants=1`, the corresponding killed count, and the survivor list; complete stdout/stderr and argv/exit records are under `out/MutRetestD/<name>.{stdout,stderr,command.json}`.

Expected detector: the committed `isolation-mutants.py` first requires a passing pristine grid, then runs exactly one source replacement against the same current-arm grid (`tests/report-audit/isolation-mutants.py:74–84,92–112` at `245a37f6`). M20–M25 definitions are at `:58–70`. Behavior-bearing audit points at that revision: M20 `tools/report-landing-audit.py:194–197`; M21 `:127`; M22 `:442–444`; M23 `:123–126`; M24 `:918–924`; M25 `:195–199`.

## Three new single-line survivors

Command executed once, exit **0**, empty stderr:

```text
python3 mutation-probe.py
```

The clone-only harness creates one separate auditor file per probe. For each it runs **pristine → mutated → finally-restored** bytes through both (1) the unchanged complete current grid and (2) one additional row using the grid's own `run_case` detector. The same selected row and expected result are retained across all three phases. Per-auditor timeout remains 30 seconds; each full-grid subprocess is additionally bounded at 180 seconds. No baseline was failing or inconclusive.

Full-grid command for each phase, substituting the exact probe filename below:

```text
python3 /tmp/kama-r23w2/MutRetestD/tests/report-audit/repo-state-grid.py --arm current --current /tmp/kama-r23w2/MutRetestD/.mutation-probes/<name>.py --json
```

For **each** D01–D03, the full grid's observed pristine/mutated/restored exits were **0 / 0 / 0**. Every phase reported `faults_met=26/26`, `controls_met=8/8`, `violations=0`, `tracebacks=0`, `commands_executed=0`, `timeouts=0`. Execution counts refer to the grid's fault-program markers, not to ordinary Python/Git subprocesses. The two `open` rows and one `tradeoff` row remain ungraded, as specified by the committed detector (`tests/report-audit/repo-state-grid.py:526–591,624–635,674–686` at `245a37f6`).

### D01-timestamp-upper-bound — SURVIVED

Family: M25, timestamp shape. Exact one-line replacement at `tools/report-landing-audit.py:195` at `245a37f6`:

```diff
-                or not re.fullmatch(r"[0-9]{1,12}", atime)):
+                or not re.fullmatch(r"[0-9]{1,13}", atime)):
```

Existing F26 uses **5,000** digits (`tests/report-audit/repo-state-grid.py:466–477`), so both guards still reject it. The missing boundary row uses a real raw Git commit whose author timestamp is `1000000000000`; the fixture checks that `git log -1 --format=%at` emits those exact 13 digits. The report cites the earlier base commit.

Row that should exist: `D01-thirteen-digit-author-timestamp`, fault, expected exit 2 with reason `unexpected git log record`, pinning the current 12-digit refusal boundary.

Actual added-row outputs, pristine / mutant / restored:

- **2**, `met=true`, stderr: `could-not-evaluate: unexpected git log record '85e7a4cdb2169ed88da00df971245c448fb250fd' '1000000000000'`.
- **0**, `kinds=[]`, `met=false`, empty stderr.
- **2**, `met=true`, same unexpected-record reason.

All three had `traceback=false`, `timed_out=false`, `executed=false`. The mutant turns an existing refusal into a clean verdict; no claim is made that accepting every 13-digit timestamp is independently an incorrect substantive omission verdict. This row tests the current guard's contract rather than redefining it.

### D02-decode-bom-stripping — SURVIVED

Family: M23/M21, strict UTF-8 decoding and byte-to-text fidelity. Exact one-line replacement at `tools/report-landing-audit.py:123` at `245a37f6`:

```diff
-        out = proc.stdout.decode("utf-8", errors)
+        out = proc.stdout.decode("utf-8-sig", errors)
```

The new fixture commits these report bytes: `b"\xef\xbb\xbf## Landed changes\n\n- " + cited_commit.encode() + b"\n"`. Under the current UTF-8 decoder the BOM remains before `##`, so the anchored heading matcher (`tools/report-landing-audit.py:168–170`) does not recognize that heading. The mutant silently strips it. Existing invalid-UTF-8 rows still refuse under both codecs, so they do not detect this semantic change.

Row that should exist: `D02-committed-report-utf8-bom`, control, expected exit 1 and exactly `landed-omitted`, `landed-section-missing`, pinning the current anchored-heading behavior on committed report bytes.

Actual added-row outputs, pristine / mutant / restored:

- **1**, `kinds=['landed-omitted', 'landed-section-missing']`, `met=true`.
- **0**, `kinds=[]`, `met=false`.
- **1**, same two kinds, `met=true`.

All stderr tails empty; no traceback, timeout or execution marker. This demonstrates a missing byte-decoding/heading control, not an assertion that the planner should adopt a different BOM policy.

Primary-source support: https://docs.python.org/3.14/library/codecs.html#module-encodings.utf_8_sig — “an optional UTF-8 encoded BOM at the start of the data will be skipped.” Opened during this probe; page labels itself Python 3.14.9, while the executed interpreter is 3.14.8.

### D03-promisor-symlink-skip — SURVIVED

Family: M22, promisor-pack refusal. Exact one-line replacement at `tools/report-landing-audit.py:443` at `245a37f6`:

```diff
-                p.suffix == ".promisor" for p in path.iterdir()):
+                p.suffix == ".promisor" and not p.is_symlink() for p in path.iterdir()):
```

The missing row reuses F23's actual incomplete blobless clone with promisor config removed (`tests/report-audit/repo-state-grid.py:194–212`). It renames each real `.promisor` marker to a sibling `.marker` file and replaces the original pathname with a relative symlink to that file. The fixture requires the marker to remain a resolving symlink. Existing F23 has regular marker files, so the new skip remains invisible to it.

Row that should exist: `D03-symlink-promisor-pack`, fault, expected exit 2 with reason `promisor pack`.

Actual added-row outputs, pristine / mutant / restored:

- **2**, `met=true`, stderr contains `partial clone (promisor pack)`.
- **1**, `kinds=['unresolved-full-hash']`, `met=false`, empty stderr.
- **2**, `met=true`, stderr again contains `partial clone (promisor pack)`.

No traceback, timeout or execution marker. The mutant misclassifies unavailable promised-object evidence as a substantive report defect.

Primary-source support: https://git-scm.com/docs/partial-clone#_handling_missing_objects — “These promisor packfiles consist of a "<name>.promisor" file with arbitrary contents”. The documentation supports the marker mechanism; symlink handling is established by this local experiment, not asserted from that quote.

## Hashes and exact restoration

Observed pristine source SHA-256 before and after all experiments:

```text
f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7
```

The tracked auditor in the clone was never modified. The committed runner writes its variants to auto-removed temporary files. Its six mutant-byte hashes below are reconstructed deterministically from the committed runner's exact one-match replacements; their temporary filenames were not retained. The three new variants were hashed from their actual on-disk bytes by each full-grid invocation and restored in `finally` to byte equality, not merely equivalent text.

| Mutant | Mutated SHA-256 |
|---|---|
| M20-log-sha-shape | `0c79bf7dd386c87d47b592065b0ca9c7869abaaca0f7f5995a0ac9fa879d829b` |
| M21-newlines | `50648f4553eff15b180c5868d71ef432e4c32ccb76364f86ac167530c89046b2` |
| M22-promisor-pack | `8679c1f0cb23ec8814f1f063169437e3a43c7e2b0f3075ef39fdce86cd6cf097` |
| M23-strict-decode-catch | `c8d6c61ec42c94684f097df4d4d035f9cb2dab4a78881afe91490fd29582aa60` |
| M24-catch-all | `501cb0dfe64f40a928f92faae47623c37027f4a92c731736622a1b1a3ed877bf` |
| M25-timestamp-shape | `7e8edfc934c4d295bb84686bc3c011fa1b81bcffacec470215900a17e0a6eae4` |
| D01-timestamp-upper-bound | `5bf3c4d74f601375bbee9ed06dd8879e8ef8c15213896ee14266600aea9a92bf` |
| D02-decode-bom-stripping | `0374ce905433f373f505dc2ca95441afb45302896b6c9bc591f1f1ac618ba97d` |
| D03-promisor-symlink-skip | `62fec66c34c61b5bb61604081f21206e074dc33376ea3eb53175db12548cd013` |

For each D probe, before and restored SHA-256 both equal the pristine hash above and `restored_exact=true`. Each restored added row meets its original expectation. The final current grid on the untouched cloned auditor also exited **0**, 26/26 faults, 8/8 controls, zero graded violations/tracebacks/marker executions/timeouts. Exact command and output: `out/MutRetestD/assigned-source.restored.grid.{command.json,stdout.json,stderr}`. These restoration runs use the same bounded detector; they are not baseline-failure kills.

## Evidence files and scope not verified

Lane-relative paths in this report are beneath `.ufo/waves/round-23/falsify/` unless explicitly qualified. Machine-readable phase outputs and exact argv/exit/hash records are in `out/MutRetestD/`; `new-mutant-results.json` and the three `D*.result.json` files contain complete new-probe records. `files-written.json` individually names and hashes **all 65 other evidence files**, names itself and this report, and names all four authored clone-only files:

- `/tmp/kama-r23w2/MutRetestD/mutation-probe.py` — retained reproducible experiment source, not an integrated test.
- `/tmp/kama-r23w2/MutRetestD/.mutation-probes/D01-timestamp-upper-bound.py` — restored exact pristine bytes.
- `/tmp/kama-r23w2/MutRetestD/.mutation-probes/D02-decode-bom-stripping.py` — restored exact pristine bytes.
- `/tmp/kama-r23w2/MutRetestD/.mutation-probes/D03-promisor-symlink-skip.py` — restored exact pristine bytes.

Other writes were the isolated Git clone and automatically removed fixture trees `/tmp/isolation-mutants-*`, `/tmp/repo-state-grid-*`, `/tmp/MutRetestD-*`. The only scoped report written is `.ufo/waves/round-23/falsify/advice/MutRetestD.md`; it is written once, append-only thereafter. No lane tracked source/test/docs/index was changed.

Not verified: frozen-arm results; M01–M19; auditor selftest; rounds 10–22 ledger/no-errata byte equivalence; old-Git compatibility; sibling tools; alternates or gitfile fixes; arbitrary non-ValueError exception paths; BOM draft/committed parity; remote/network behavior; any broader security isolation guarantee. Open/tradeoff rows were executed by the complete grid but their success is not claimed. No production fix, grid extension, contract revision, integration, or shipping decision was made.
