# CritStorageSafety — r24 fresh falsification of 2e254a1763a9c08aa07fc53081287f506c447d84

Verdict: **PARTIAL.** The production auditor's no-fetch boundary holds. Fixture containment holds. Two filed evidence claims are **falsified** by the wave's own artifacts. The grid has three harness defects, one of them new in r24 (process-group cleanup after the leader is reaped). None of these changes a graded verdict of the auditor.

Scope: static source reading plus one benign offline fixture build (no auditor execution, no clone, no transport). Production checkout, `.jj`, index, fleet, sibling lanes, config and services were not touched.

## Snapshot

- Scratch: `/fast/scratch/hyaku/kama-r24/falsify/CritStorageSafety/repo` (`git clone --no-hardlinks`, detached). `git rev-parse HEAD` returned `2e254a1763a9c08aa07fc53081287f506c447d84` (exact base observed).
- Pins (`sha256sum`, exit 0), all match the assignment:
  - `tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`
  - `tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`
  - `tests/report-audit/promisor-grid-expectations.json` `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
  - `tests/report-audit/promisor-mutants.py` `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`
- Frozen r23 auditor `0df800e:tools/report-landing-audit.py` sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`. This equals the `auditor_sha256` filed in `build/out/CaseCompleteFleet/base-run.json` and `build/out/CaseMarkerFleet/obs-base.json`. The frozen `GIT_ISOLATION` already carries `--no-replace-objects --no-lazy-fetch`.
- Manifest: 47 graded cases and 1 open row (PG40).
- Tools: git 2.56.0, python3 (already present). **Nothing was installed or updated.**

## What holds

H1. **The auditor has a single git choke point.** `rg 'subprocess|os\.system|os\.popen|os\.exec|spawn'` over the tool finds exactly one launch: `subprocess.run(["git", *GIT_ISOLATION, "-C", repo, ...], timeout=GIT_TIMEOUT)` at line 162. Every git call therefore carries `--no-replace-objects --no-lazy-fetch` and a 20 s deadline. This includes both diagnosis walks in `missing_reachable` (`-c core.commitGraph=false rev-list --objects --missing=print [--filter=blob:none] --stdin`). The walks use no `--missing=print-info` or `--missing-only` (the supplement's version constraint is met).

H2. **Fixture containment holds** for `make_root`, `fresh_root`, `init_repo` and `write_under`.
- `make_root` accepts `TMPDIR` only under `/fast/scratch/hyaku/kama-r24`; otherwise it uses that directory.
- `init_repo` verifies `--show-toplevel` equals the fixture (the r23 M4 check).
- `/fast/scratch/hyaku/kama-r24` is not inside any git repository (`rev-parse` returned 128, "not a git repository").
- Fixture run observed: root `/fast/scratch/hyaku/kama-r24/falsify/CritStorageSafety/tmp/promisor-grid-iqt_qaku`; lane top level equals the lane; `rmtree` left nothing behind.

H3. **The premise probes really are no-fetch.** `object_exists`, `missing_objects` and `object_inventory` all pass `--no-lazy-fetch` (`object_exists` also passes `--no-replace-objects`). After marking, the remaining plain `git()` calls in `build()` are:
- `rev-parse <c>:path` (reads only trees that are present),
- `config --list`,
- `rev-parse --absolute-git-dir`.

None of them reads a missing object.

H4. **No broad kill.** `rg 'pkill|killall|kill -|os\.kill\(|killpg\(0|killpg\(-1'` finds no match under `tests/report-audit` or the tool. Group kills target only the PID of a session the harness itself created.

H5. **The acquisition pin works in the one cell that can detect it.** In PG43 (`c_fleet_unhydrated_blobless`, amended exit 2, names `$report_blob`), the fleet is a real `--filter=blob:none` clone whose promisor remote is the live `file://<tmp>/fleet-origin`. A lazy fetch there would succeed and show up in the `object_inventory` before/after difference.

## Falsified evidence claims

F1. **PM08's "static verification" cannot tell the mutant from the pristine source.**
- Claim, `build/advice/MutationOracle.md:139-140`: "the runner verifies PM08 statically (the flag is present in the pristine source and absent in the mutant)".
- Code, `promisor-mutants.py:738-739`: `present_after = marker in applied`, with marker `--no-lazy-fetch`.
- Counterexample (pure text application, nothing executed): the alternative `'"--no-lazy-fetch",\n                 '` matches once. The mutated `GIT_ISOLATION` becomes `("--no-replace-objects", "-c", "i18n.logOutputEncoding=UTF-8", ...)`, yet `"--no-lazy-fetch" in mutated` is still `True`: 4 occurrences before, 3 after, at lines 60, 137 and 659 (docstring and comments).
- Filed evidence agrees with the counterexample, not the claim: `build/out/MutationOracle/sensitivity-promisor-grid.json:809-812` and `proxy-run-r23-grid.json:163-166` record `"--no-lazy-fetch present before=True after=True"` and `static_after: true`.
- Impact: the evidence for the no-lazy-fetch axis is overstated. The flag *is* present (H1), but PM08's recorded check proves nothing. This is a fixable defect, not a tradeoff.
- Smallest correction: make the static check structural. Parse `GIT_ISOLATION` (`ast.literal_eval` of the tuple, or `ast` over the module) and require `"--no-lazy-fetch" in GIT_ISOLATION` before and `not in` after. Also check that line 162 is the only subprocess launch. Correct the MutationOracle.md wording by appending (reports are append-only).

F2. **"The grid has no transport-capable fixture" is false.**
- Claim, `MutationOracle.md:136-138`: "the grid has no transport-capable fixture on purpose".
- Counterexample: `blobless_clone()` (promisor-grid.py:214-224) clones `file://{origin}` with `--filter=blob:none`. `build()` moves the original repository to `tmp/lane-origin` or `tmp/fleet-origin` and never deletes it. So PG05, PG06, PG28 and PG43 each have `remote.origin.promisor=true` and a reachable `file://` remote.
- A PM08 mutant that reads a missing blob (PG43 must read the report blob) would invoke the local `git-upload-pack` transport.
- The pristine auditor stays safe through H1. The claim matters because PM08's "not executed" safety rationale depends on it. If the runner ever executes PM08 (for example via `--only`), the result is a transport invocation, not a no-op.
- Smallest correction: append a correction that names PG05, PG06, PG28 and PG43 as local-transport-capable. Optionally have `run_grid` refuse `execution == "static-only"` mutants unconditionally. It already skips them in the main loop (lines 731-747); keep that guard explicit.

## Harness defects (fixable; graded verdicts unchanged)

D1. **The premise facts are computed but never enforced or emitted.** (Impacted axis: oracle provenance.)
- `build()` computes `premise = {lane_promisor, fleet_promisor, lane_missing, fleet_missing, fake_present, ...}` (lines 458-466). Only `selftest()` reads it (lines 902-912). `run_case` and `main` neither check it nor copy it into `candidate.json`.
- Observed in the fixture: `"premise" in run_case.__code__.co_names/co_consts` is `False`.
- The module docstring (lines 5-7) says "every premise is checked ... before an auditor runs". Only the ad-hoc `raise Premise` sites (errata, cited hidden blob, cross-repo, drop-not-loose) are real gates.
- Strongest silent-pass counterexample `[INFERENCE]`: if a hydrated blobless cell degraded to a plain full clone, it would still meet exit 0 and stay `twin_equal` with its plain twin, with no recorded fact showing the promisor premise was lost. Two ways this could happen:
  - git ignores the filter when the server does not honor it ("filtering not recognized by server, ignoring"; rc 0, no promisor config), or
  - a complete cell acquires an unintended hole.
- Smallest correction: in `main` after `built = ...`, assert per builder the premise the case name declares (`*_promisor`/`marker`/`hydrated` → `promisor_backed`; `complete`/`hydrated` → `lane_missing == fleet_missing == []`; `unhydrated` → non-empty). Raise `Premise` otherwise, and copy `built["premise"]` into `obs`.

D2. **New in r24: the process group is killed after its leader has been reaped.** (Impacted axis: owned-process-group cleanup.)
- `run_auditor` (promisor-grid.py:700-720) calls `os.killpg(proc.pid, SIGKILL)` in `finally` on every path. On normal exit, `proc.communicate()` has already called `wait()` and reaped the session leader.
- If no group member survives, the PID/PGID number is free. A recycled PID that becomes a group leader (any process calling `setsid`) could be SIGKILLed. The window is microseconds `[INFERENCE: not reproduced, deliberately not probed]`.
- r23 `repo-state-grid.py:737-739` only `killpg`s inside `except TimeoutExpired`, while the leader is unreaped. So r24 regressed the owned-group property.
- Smallest correction: keep the leader as an unreaped zombie until the group is killed. Drain the pipes with `proc.stdout.read()`/`proc.stderr.read()` under a deadline (threads, or `selectors`), then call `os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOWAIT)`, then `os.killpg(proc.pid, SIGKILL)`, then `proc.wait()`. Alternatively, `killpg` only on the timeout path and rely on `survivors()` (which already flags leaks) for normal exits.

D3. **A nested session escapes the outer kill and leaks the grid root.** (Impacted axes: process cleanup and storage.)
- `promisor-mutants.run_grid` (lines 459-487) documents "a timeout kills the grid and every git child it started". But the grid starts every auditor with `start_new_session=True` (promisor-grid.py:702), so `killpg(getpgid(grid))` does not reach the in-flight auditor or its git child.
- Because the grid dies by SIGKILL, its `finally: shutil.rmtree(root)` (line 1082) never runs. The fixture root stays under `/fast/scratch/hyaku/kama-r24`: contained, but leaked.
- In the pristine auditor the orphan is bounded by `GIT_TIMEOUT=20` per call `[INFERENCE]`. Under a mutant with its timeout removed, it may not be bounded.
- Smallest correction: either run the grid's auditors in the grid's own group (drop `start_new_session` and kill the auditor's children through a per-case cgroup or prctl subreaper), or have `run_grid` follow its SIGKILL with a sweep of `/proc/*/cmdline` for the grid root it can derive (the `--json` doc has no root unless `--keep`). The simplest option is to pass `--out`/`TMPDIR` to a runner-owned directory and `rmtree` it after the kill. Fix the docstring either way.

D4. **Minor (exit contract):** `root = make_root()` sits outside the `try` in `main` (line 961) and `selftest` (line 935). A missing or unwritable `/fast/scratch/hyaku/kama-r24` raises an uncaught `OSError`, so Python exits 1 ("graded violation") instead of 2 ("could not evaluate"). `promisor-mutants` maps rc 1 without rows to could-not-evaluate, so there is no downstream false kill. Correction: move `make_root()` inside the existing `try`.

## Coverage gap (tradeoff to record, not a defect)

G1. **In config-marked cells the acquisition pin cannot see a lazy fetch.**
- `mark_config` points `remote.origin.url` at `tmp/absent-remote.git`. Fixture observation: `exists False`.
- A lazy-fetch attempt in PG03/07/09/11/13/15/17/19/... therefore fails without adding objects. `object_inventory` cannot tell "attempted and failed" from "never attempted", and the expected exit 2 matches either way.
- Only the blobless cells (H5/F2) can detect a fetch, and among them only PG43 forces a missing-object read.
- The no-lazy-fetch guarantee therefore rests on H1 (static) plus PG43 (one live cell), not on the 20+ promisor cells. A safe strengthening needs no transport: point the config-marked `remote.origin.url` at a non-existent path inside a directory the grid then checks is still absent (it already is). The honest statement is that a failed fetch is not observable without transport or execution, so record this as a coverage limit in the evidence.

## Observed vs inferred

- Observed: pins; the single subprocess site; `GIT_ISOLATION` contents (current and frozen); the PM08 text mutation leaving 3 marker occurrences; filed `static_after: true`; `blobless_clone` retaining a `file://` origin (source); the premise facts not used by `run_case`; the r23 vs r24 `killpg` placement; fixture containment and absent remote.
- Inferred: the PID-reuse window in D2, the orphan bound in D3, and the hydrated silent-degradation path in D1. None of these was exercised, by design: they would need execution-bearing or racy probes.

## Commands (exit codes)

- `git clone -q --no-hardlinks …; git checkout -q --detach 2e254a17…; git rev-parse HEAD` → 0
- `sha256sum tools/report-landing-audit.py tests/report-audit/*` → 0
- `git show 0df800e:tools/report-landing-audit.py | sha256sum` → 0 (`da5041a8…`)
- `python3` pure-text application of PM08 alternatives to the tool source → 0 (counts 1/0/1; marker 4→3)
- `git -C /fast/scratch/hyaku/kama-r24 rev-parse --show-toplevel` → 128 (not a repository, as wanted)
- `TMPDIR=…/CritStorageSafety/tmp python3 <import promisor-grid; build(lane_mark="config", drop=("sources_blob",))>` → 0. This is one benign offline fixture; no auditor, no clone. Output is in `out/CritStorageSafety/fixture-facts.txt`.

## Files written

- `.ufo/waves/round-24/falsify/advice/CritStorageSafety.md`
- `.ufo/waves/round-24/falsify/out/CritStorageSafety/fixture-facts.txt`

## Not verified

- No grid, mutation or selftest run (out of scope by contract).
- PM08 not executed (static only).
- The Git ≥ 2.45 floor (L0, inherited) is not re-assessed here.
- Isolation-mutant M02 against r23 F06 (execution-bearing) is not examined.

## Addendum (appended 2026-10-21 19:52 UTC): peer report from KamaR23-2.CaseFleetBlobless

Peer-reported, **not reproduced by this lane**. In the PG43 blobless fleet fixture, one stray `git cat-file -e HEAD:<path>` run without `--no-lazy-fetch` lazy-fetches the report blob from the reachable `file://` origin. The auditor then returns exit 0 "clean" instead of the correct exit 2. The peer's A/B run: blob absent gave exit 2; blob materialised gave exit 0. The peer judged the grid's own helpers safe and called it "no source defect".

How this fits the findings above:

- **It corroborates F2.** The blobless cells really are transport-capable: a lazy fetch succeeds and acquires objects.
- **It strengthens D1.** The peer limits the risk to manual inspection of `--keep` fixtures. The premise check that would catch the hazard already exists: `lane_missing`/`fleet_missing` in `build()`. But nothing enforces it, and `run_case` takes its `before` inventory only after `build()` returns. So any fetch during fixture setup, or before a re-run, is invisible to the acquisition pin, and PG43 would turn into a silent exit 0 that is graded NOT-MET rather than refused as a premise failure. With D1 enforced (`c_fleet_unhydrated_blobless` must have `fleet_missing` non-empty and containing `report_blob`), the same event becomes exit 2 "fixture premise", not a graded result.
- **Operator guidance:** probe any kept fixture only with `git --no-lazy-fetch --no-replace-objects …`.
