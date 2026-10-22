# FinalCase09 — PG09-omission-lane-promisor (+ graded twin PG10-omission-lane-plain)

**VERDICT: no falsification.** In the CURRENT arm both cells meet the registered live expectation, and the cell discriminates the two bug classes the target names. Not a score claim, not a self-admission.

**Identity:** clone `--no-hardlinks` at `/fast/scratch/hyaku/kama-r24/postfix/FinalCase09/clone`, detached at `92063cfc60e217fa7e2098c568578119b16a1b95`. auditor `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f` | grid `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270` | expectations `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | population `612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`. TMPDIR `/fast/scratch/hyaku/kama-r24/postfix/FinalCase09/tmp` (existing, owned).

**Runs** (exact argv + exits in `out/FinalCase09/run-summary.json`):
1. `python3 tests/report-audit/promisor-grid.py --arm current --case PG09-omission-lane-promisor --case PG10-omission-lane-plain --json --out <scratch>/out/gridrun` → **exit 0**; identical repeat run (`gridrun2`) → exit 0, same normalized-document sha256 `5e00f9f2…` both times.
2. Manual probe `probe_pg09.py`: PG09 fixture rebuilt with the pinned builder `c_omission_lane_promisor`, pinned auditor alone → exit 1, stderr empty (`out/FinalCase09/probe-pg09.json`).

**Premise (observed, probe-pg09.json):** lane promisor-marked by *config only* (`extensions.partialclone` + `remote.origin.promisor=true`; no `.promisor` marker), fleet unmarked; both stores complete (lane/fleet missing sets empty); cited commit `58866b56…` **is in the lane and absent from the fleet**; omitted commit `1acb5ebb…` (author time 1500 ≤ report cutoff 2000) is in the lane, absent from the fleet. The cross-store-absence path is therefore genuinely exercised, not vacuous.

**Pristine observation, both cells:** exit 1; `kinds=[landed-omitted]`; defect token `1acb5ebb06054bf52d84ffdacd8727b95287f34b` = the fixture's omitted commit (`$omitted` resolved); a verdict **document exists for both cells** (not two missing documents) and `twins`/`twin_equal` are true in both directions (identical normalized documents); `objects_acquired={lane:[],fleet:[]}`; no traceback, no internal_error, no timeout, no leak; stderr empty.

**Controls** (new-source, unregistered, built from the pinned bytes in my scratch — discrimination experiments, not candidate proposals):
- **C1** metadata-only refusal → PG09 **exit 2** `partial clone (remote.origin.promisor)`; problems: `exit 2 != 1`, `reason is the r23 metadata refusal`. PG10 stays exit 1/met → **PG09 alone kills this class; the plain twin cannot**.
- **C2** cross-store absence scored "unknown" (content unreadable) → PG09 **and** PG10 exit 2, `round 1: unknown: unavailable required object: 58866b56… is present but its content cannot be served`. Both kill it.
- **C3** cross-store absence masks presence ("absent") → exit stays **1**, but the defect set becomes `{landed-omitted, landed-unresolved, unresolved-full-hash}` ≠ expected → PG09/PG10 catch it **only via the manifest's defect-set comparison, not via the exit code**.

**Residuals / gaps:** (a) frozen/both arms NOT run (CNE2 before a pristine run; sensitivity is CURRENT-arm only), so PG09's frozen column (r23 exit 2, metadata reason) is unmeasured here. (b) Controls are unregistered new-source mutants: they demonstrate discrimination, not that any registered mutant is killed; the mutant driver was not run. (c) The merge guard `status[token] != "found"` makes store order relevant on the "unknown" path; a reversed store order was not probed. (d) The original unknown clause stays WITHDRAWN/NOT-ACHIEVED; nothing here promotes it, and Gitfloor H2 stays open.

**Artifacts:** `.ufo/waves/round-24/postfix/out/FinalCase09/` — pristine + repeat `candidate.json`/`population.json`, three control `candidate.json` + control sources, `probe-pg09.json`, `run-summary.json` (argv, exits, digests, file hashes).

Report: .ufo/waves/round-24/postfix/advice/FinalCase09.md
