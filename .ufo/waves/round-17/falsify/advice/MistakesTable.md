VERDICT: partial — M1/M4 reproduce, but M2 attribution and M6/M7 evidence need qualification.

# Round 17 Mistakes M1–M7 review

Attacked lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; scope was the evidence pointers, captured-by labels, and fail-capable demonstrations in `corpus/lessons/round-17.md:85-91`.

## Findings (severity ordered)

### MEDIUM — M2 `captured-by` conflates detection with admission control

`corpus/lessons/round-17.md:86` says “none — fail-capability was never an admission condition.” The cited `.ufo/waves/round-17/build/advice/RevengerPlannerWalk.md:75-80` says outside closures caught four cases, lane seats caught three round-16 cases, and L1's smoke caught another; `:81-87` says each still passed admission. Thus the recurring defects were detected, but detection was not an admission condition. “None” is inaccurate for a column named `Captured-by`; distinguish “caught by review/seats” from “no admission gate blocked them.” The seven-instance count and the routed-debt diagnosis otherwise match the report (`:70-87`).

The frozen-arm evidence is real: `runs/fault-controls-frozen.json:155-156` records 5 detected / 3 accepted; `runs/controls-frozen.json:1-2,179` records 6 accepted-bad and 1 inconclusive. The lesson's measurement invocations are not copy-paste commands, however: `round-17.md:156-158` uses `--check <check.py>` and `:166` uses `--tool ABS --gate ABS`. C2's exact frozen command is recoverable in `build/advice/C2Controls.md:78-86`; C1's frozen path must be supplied from the pinned run artifact. This is a reproducibility gap, not a contradiction in the frozen counts.

### MEDIUM — M6 does not give durable support for all three named misroots

`corpus/lessons/round-17.md:90` attributes fleet-root writes to `ScoutPythonReturncode`, `ScoutReceiptSchemaConsumers`, and `RevengerS041Edit`, but provides no report path/line for those disclosures. The independently retained corroboration I found, `.ufo/waves/round-17/build/advice/ScoutR16SummaryBug.md:64-65`, names only `RevengerS041Edit.md` at the fleet root and its own transient misplaced copy. The current reports for the two Scout seats do not provide a locator for that event. [INFERENCE] Those two claims may rely on ephemeral disclosures; the lesson's wording is not independently auditable from its listed evidence.

The cleanup sweep does exist in the current worktree: `.ufo/waves/round-17/falsify/advice/MisrootSweep.md:42-47` says “Both paths are now absent from the fleet root.” But it is not in the attacked commit (`git cat-file` check below returned `NOT_COMMITTED`), and M6 does not identify it by path. Preserve it as post-commit corroboration, not as evidence present in `54a2926`.

The two bound-slip observations do resolve: `build/advice/ConnectKumitate.md:67` discloses a recursive grep without the required exclusion; `build/advice/ConnectKake.md:182-184` discloses targeted reads of kake `corpus/knowledge/` outside the three permitted files. The M6 statement that no mechanical guard exists is candid rather than overclaimed.

### LOW — M7's cited refusal supports missing paths, not an absolute-path rule

`SKILL.md:575` requires absolute paths for the live controls command. The implementation at `tests/llamacpp-live/controls.py:640-644` checks `os.path.isfile(path)` and returns 2 with “not found”; it does not reject relative paths categorically. A relative path that resolves from the caller's working directory is accepted, while an unresolved relative or unset-shell-variable value can take this refusal branch. I reproduced the generic not-found branch (command below, exit 2), not the historical invocation: the exact first failed argv/output is not retained in the lesson. The captured-by description is plausible, but should say “path-resolution refusal” and cite the actual failed invocation if available.

### LOW — M3 exposes five nonconformant reports; it is not a nonzero-exit gate

The cited counter does classify the strict round-16 falsify directory as 34 confirm / 40 partial / 0 refute / 5 nonconformant, with the five files listed. My rerun below reproduced that. Its contract explicitly says `count-verdicts.py:30-33`: “0 when counting completed (any verdict mix)”; it exits 0 on those five nonconformant reports. The M3 wording “shown able to fail” is accurate only as “shows the reports failing the first-line format,” not as a failing process/gate. The row should keep that distinction explicit.

## Verified pointers and re-runs

- **M1 — resolved and reproduced.** `corpus/SOURCES.md:53` is S041; the read-only diff `b8e485c`→`ccc4bb3` changes the old 13:49:38 / port 32845 anchor to 14:06:27 / port 37527 / tool hash `b8c5e8d4…`, and adds the loading-envelope clause to `teaches`. `round-16.md:147-149` records the amendment. The committed `build/advice/ReviewSourcesHistoryRule2.md:60-85` contains the complete pairwise ledger and identifies only `726f737`→`ccc4bb3` as a rule-2 violation. `CORPUS.md:116-118` is the append-only rule; `corpus/QUALITY.md:123` is KQ22.
- **M2 — references resolve.** `build/advice/RevengerPlannerWalk.md` supports the seven recurring instances; KQ20/KQ21 are `corpus/QUALITY.md:121-122`. Frozen bad-control counts match the run artifacts above. Note versioning: `build/advice/C1FaultControls.md:16-19` is an earlier intermediate run (its “current” hash `b460…` accepts one F8 variant); the final `runs/fault-controls-current.json:3-4,155-156` pins hash `ddc3…` and accepted 0. Use the final run for the lesson's current result.
- **M3 — resolved.** `build/advice/RevengerSummaryProducer.md` explains the keyword-priority count; `.ufo/waves/round-17/count-verdicts.py` is present and the rerun below lists the five strict first-line nonconformants.
- **M4 — resolved and reproduced; residual correctly remains open.** The round-16 ledger `falsify/provenance-ledger.json:45-56` binds the `spawned` attempt to 79 tasks but records `spawned: 0`; `spawn-result.json:4,9-16` has “Spawned 79 background agents” and pending rows. The round-16 tool's `dispatch-provenance.py:162-181` only counts literal `refused`/`spawned` keys or those exact `status`/`state` values. The committed round-17 `build/advice/ScoutR16DispatchProvenanceBug.md` and `provenance-0to79-demo.txt:1-6` resolve. My rerun gives old 0 / new 79. The open refusal residual is also confirmed: `build/refused-result-1.json:4` contains 82 per-task refusal messages, while `build/provenance-ledger.json:24-29` records `refused: 0`.
- **M5 — premises and counterchecks resolve.** The committed build context (`build/spec.json:2,49`) contains both stale claims: `.ufo/state/` and `registry/history/.lock` were supposedly unignored, and the impossible `36/43/0 + 5`. `registry/history/.gitignore:3` is `.lock`; `git log --follow` dates that file to `83bee7f round-2`. `build/advice/ConnectMado.md:19-21` records `git check-ignore -v registry/history/.lock .ufo/state/x` and the actual matching rules. The recount is independently supported by `RevengerSummaryProducer.md:54,89-101` and the M3 rerun. `.gitignore` changed from `cff9e62` only by adding `.ufo/state/` and `__pycache__/`. This is a manual correction, not a pre-dispatch guard; the false premise was already in the build context.
- **M6 — partial support.** The bound-slip reports resolve as above; the misroot support is incomplete as detailed in the finding.
- **M7 — source resolves; original run is not reproducible from the cited evidence.** The code path and absolute-path instruction resolve, but the historical argv is absent.

## Exact commands run (exit codes)

Clone and checkout (0):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.MistakesTable-clone && git -C /tmp/KamaR17.MistakesTable-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
```

M1 guard pair (first 1, second 0):

```sh
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from ccc4bb3 --to master
```

The first printed both S041 `anchor` and `teaches` violations; the second reported no append-only violations and allowed S042–S046.

M3 strict count (0; five nonconformant names listed):

```sh
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/count-verdicts.py .ufo/waves/round-16/falsify/advice --json
```

M4 same-input demo (both 0; old `spawned=0`, new `spawned=79`):

```sh
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-16/dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json --label spawned --out /tmp/KamaR17.MistakesTable-m4/l16.json
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json --label spawned --out /tmp/KamaR17.MistakesTable-m4/l17.json
```

M4 refusal residual count (0; 82 messages, ledger `refused=0`):

```sh
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; t=json.load(open(".ufo/waves/round-17/build/refused-result-1.json"))["result"]["text"]; print("per-task refusal messages:", t.count("Background job limit reached (100)")); print("named task entries:", t.count("KamaR17.")); print("ledger refused:", json.load(open(".ufo/waves/round-17/build/provenance-ledger.json"))["entries"][0]["refused"])'
```

M7 generic missing-path refusal (2; no fake/server started):

```sh
cd /tmp/KamaR17.MistakesTable-clone && PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/controls.py --tool not-a-tool --gate tests/llamacpp-live/check-receipt.py --json
```

Other read-only checks: `git diff b8e485c ccc4bb3 -- corpus/SOURCES.md` (0); `git diff cff9e62 54a2926 -- .gitignore` (0); `git log --follow --oneline -- registry/history/.gitignore | tail -5` (0; `83bee7f round-2`); target-tree `git cat-file -e` checks confirmed the four build/advice reports and build ledger are committed but the M6 `falsify/advice/MisrootSweep.md` is not. Owned `/tmp/KamaR17.MistakesTable-*` scratch was removed (0).

## Residual risk and limitations

- M4's spawned-count defect is fixed and demonstrated; `refused: 0` for the 82-refusal input remains an explicitly open bug.
- M5's process remedy is not enforced by a mechanical gate; it detects stale premises only when a seat runs and records the check.
- The current M6 sweep is worktree evidence, not part of the attacked commit. No protected session/transcript/history/credential stores were read. No packages or tools were installed; no lane file other than this assigned report was written.