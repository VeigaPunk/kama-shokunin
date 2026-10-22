# CaseUnselectedBranch — PG31/PG32 promisor-grid falsification (round 24)

VERDICT: **HOLDS** for the graded contract, with **two fixture weaknesses** (and one
manifest inconsistency) reported separately below. No source defect was found in
`tools/report-landing-audit.py` on the surface this family exercises.

Scope: exactly one bounded selection — `python3 tests/report-audit/promisor-grid.py --arm
both --case PG31-missing-object-unselected-branch-promisor --case PG32-missing-object-
unselected-branch-plain --json` — run twice (once with `--out`, once with `--keep` so the
built fixtures could be inspected directly), plus the read-only static reads and two direct
auditor invocations against the kept fixtures needed to assert the premises, the missing /
present objects, the finding/token pairs, the no-acquisition property and the twin
comparison. No other lane suite, no full grid, no mutation grid, no execution-bearing probe.
No production file other than this report and the `out/` artifacts was written; production
`production/.jj/index`, fleet, sibling lanes, operator config, routing, services and real
object stores were not touched.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, in the pinned clone | PASS — exit 0, stderr empty, 2 graded rows, 0 violations in both arms |
| A2 | Actual missing / present objects asserted on the built fixture | PASS (observed) — side blob `2299c37978265a95cbe835a4b0f0bbf15aad5549` ABSENT; side commit `51fba42571cbc9f974e11a025b18b23bf44f9877` and its tree `d1418e9fdf7f4ffe2f0fb09464981a8d58f49199` PRESENT; the hole is visible under an `--all` walk and invisible under the audited-root walk |
| A3 | PG31 premisor-marked vs PG32 plain twin is content-identical | PASS (observed) — same master commit, side commit, side tree, dropped blob and report blob in both fixtures; only the lane promisor config differs |
| A4 | Exact finding/token pairs | PASS — `defects []`, `raw_defects []`, `kinds []` in the current arm for both rows (expected `defects: []`, `kinds: []`); no token pairs to compare |
| A5 | Content-derived reason IDs | VACUOUS — the current arm refuses nothing on either row (exit 0, empty stderr), so no reason string exists to classify; the *frozen* arm's reason is the forbidden r23 metadata refusal (`partial clone (remote.origin.promisor)`), which the current arm does not reproduce |
| A6 | No objects acquired | PASS (observed twice) — grid pin `objects_acquired {lane: [], fleet: []}` on all four rows; independently, after the grid run **and** two further direct auditor runs, both lane stores still hold exactly 7 objects and the side blob is still absent |
| A7 | Actual twin document comparison | PASS (observed twice) — grid `twins {PG32: true}` / `twins {PG31: true}`, `twin_equal true`, `twin_mismatch []`; independently, the two raw verdict documents differ only in the fleet report path and are byte-identical after path normalization |
| A8 | Original (withdrawn) view kept visible | PASS — for PG31/PG32 the expectation file carries **no** `amended` key, so the graded "amended" column is byte-identical to the "original" column; the current arm reports `withdrawn_original_failures: []` and `met_original: true`. The withdrawn expectation (unknown citation ⇒ exit 2) touches other rows, not these two, and is **not** relabelled here |
| A9 | Frozen (r23) baseline retained and unchanged | PASS — frozen arm PG31 exit 2 with the metadata reason (as the frozen view pins), PG32 exit 0; `amended_view_unmet: ["PG31-…"]` in the frozen arm records the r23 harm the repair removes |

## Snapshot, digests, environment (observed)

```
clone:  git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
            /fast/scratch/hyaku/kama-r24/falsify/CaseUnselectedBranch
        git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
HEAD  =  2e254a1763a9c08aa07fc53081287f506c447d84  (detached; tracked worktree clean,
        only untracked scratch `tmp/`; tree 90d19f20e02caf0c7a52e152f020e98e3c416af3)
```

| Item | Digest / value | Cross-check |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` | matches the assignment |
| auditor `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | matches the assignment's source tool; equals the grid's reported `auditor_sha256.current` |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | matches the assignment's runner |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | matches the assignment's manifest; equals the grid's `expectations_sha256` |
| frozen auditor (r23 base blob `0df800e8…`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | equals `derived_from.frozen_auditor_sha256` pinned inside the expectations file |
| population | `population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, `population_size 47` | fixed47 population, unchanged by this run |
| toolchain | `git version 2.56.0` (≥ 2.45 floor satisfied), `Python 3.14.8` | pre-existing; **no install or update was performed** in this lane |

## A1 — the assigned command (observed)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseUnselectedBranch
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnselectedBranch/tmp \
    python3 tests/report-audit/promisor-grid.py --arm both \
      --case PG31-missing-object-unselected-branch-promisor \
      --case PG32-missing-object-unselected-branch-plain --json \
      --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseUnselectedBranch/grid
EXIT=0     (stderr empty)
```

Grid summary (observed):

```
frozen : graded=2 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_met=1/2  amended_view_unmet=["PG31-missing-object-unselected-branch-promisor"]
         withdrawn_original_failures=[]  twin_mismatch=[]
current: graded=2 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_unmet=[]  withdrawn_original_failures=[]  twin_mismatch=[]
         twin_pairs_compared=["PG31-…","PG32-…"]
```

Per-row observations (observed):

| Row | arm | exit | defects / raw_defects | kinds | expected (amended) | met |
|---|---|---|---|---|---|---|
| PG31-missing-object-unselected-branch-promisor | current | 0 | `[]` / `[]` | `[]` | exit 0, kinds `[]`, defects `[]` | `met_amended true`, `met_original true` |
| PG32-missing-object-unselected-branch-plain | current | 0 | `[]` / `[]` | `[]` | exit 0, kinds `[]`, defects `[]` | `met_amended true`, `met_original true` |
| PG31-…-promisor | frozen | 2 | n/a (no document) | n/a | frozen pins exit 2, reason_class `metadata` | `met_frozen true`, `met_amended_frozen false` |
| PG32-…-plain | frozen | 0 | `[]` / `[]` | `[]` | frozen pins exit 0 | `met_frozen true`, `met_amended_frozen true` |

Frozen PG31 stderr (exact, observed):
`could-not-evaluate: …/current/000/lane: partial clone (remote.origin.promisor)` — the r23
metadata blanket refusal, i.e. the harm the round-24 repair removes. The current arm
produces **no stderr at all** on either row, so the `reason_forbidden` list
(`"partial clone ("`, `"promisor pack"`) is satisfied vacuously and the r23 reason is not
reproduced.

Verdict document (both current rows, identical after path normalization): one round, report
committed, `cutoff 2000`, `round_commits 1`, `required 1`, `defects []`, `status "clean"`,
`errata_rows 0` — a real audit ran, not an empty or short-circuited document.

## A2/A3 — the fixture premises, asserted directly on the kept fixtures (observed)

The second run (`--keep`) left the built fixtures at
`…/tmp/promisor-grid-db7psk9n/{current,frozen}/{000,001}/`. `current/000` = PG31 (marked),
`current/001` = PG32 (plain). Directly measured with `git --no-lazy-fetch
--no-replace-objects` (never a network or transport call):

| Assertion | PG31 (current/000) | PG32 (current/001) |
|---|---|---|
| lane refs | `refs/heads/master 58866b563cd900df310588effe79028efc104c33`, `refs/heads/side 51fba42571cbc9f974e11a025b18b23bf44f9877` | identical |
| master commit (the audited root, cited by the report) | `58866b563cd900df310588effe79028efc104c33` @ author time 1000 | identical |
| side commit / side tree | `51fba425…` / `d1418e9f…` @ 1200, subject `side: file` | identical |
| dropped side blob | `2299c37978265a95cbe835a4b0f0bbf15aad5549` — **ABSENT** (`cat-file -e` exit 1) | identical (ABSENT) |
| side commit / tree still present | present / present | present / present |
| `rev-list --objects --missing=print --all` | `?2299c37978265a95cbe835a4b0f0bbf15aad5549` (exactly one hole) | identical |
| `rev-list --objects --missing=print refs/heads/master` | `(none)` — the audited-root closure is complete | identical |
| lane promisor metadata | `remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=<absent-remote.git>` | **none** |
| lane store size | 7 objects | 7 objects (byte-identical object list) |
| fleet report | `.ufo/reports/round-1/kama.md`, blob `0cf7ed5cd6dec335553d165dc587baa224ab302b`, content `# kama round 1 / ## Landed changes / - 58866b56…` | identical blob sha |
| fleet refs | `refs/heads/master 18f93ab89cc2c01b191efa72b0721eb6e023be6b` (report @2000, init @1900) | identical |

So the two fixtures are content-identical twins and the only difference is the lane promisor
configuration; the missing object is a **blob** of an unselected `side` branch, unreachable
from the audited root `refs/heads/master`.

## A4/A6/A7 — independent re-verification outside the grid's own bookkeeping (observed)

Two direct invocations of the pinned auditor against the kept fixtures (read-only, local,
`--no-errata`, exactly the argv the grid uses, `cwd` = fixture dir):

```
$ python3 tools/report-landing-audit.py --lane-repo …/current/000/lane \
      --fleet-repo …/current/000/fleet --rounds 1 --json --no-errata
EXIT=0   stderr 0 bytes
$ python3 tools/report-landing-audit.py --lane-repo …/current/001/lane \
      --fleet-repo …/current/001/fleet --rounds 1 --json --no-errata
EXIT=0   stderr 0 bytes
```

- **Finding/token pairs**: both documents carry `results[0].defects == []` and
  `summary.by_kind` all zero, `summary.status "clean"` — matching the expected
  `defects: []` / `kinds: []` exactly. There is no token to resolve.
- **Twin comparison, raw**: `diff` of the two raw documents reports exactly one differing
  line — the `"report"` path (`…/current/000/fleet/…` vs `…/current/001/fleet/…`).
  After replacing the fixture root by a placeholder, `diff` reports **no** difference: the
  two verdict documents are byte-identical. The grid's own `twin_equal: true` is therefore
  not an artifact of over-aggressive normalization (the only differing byte is the fleet
  report path, which the grid replaces by design).
- **No objects acquired**: after the grid run *and* these two extra auditor runs, both lane
  stores still contain exactly the same 7 objects and the side blob
  `2299c379…` is still absent; `objects/pack/` is empty in both lanes (no pack, no
  `.promisor` marker) and no `FETCH_HEAD` exists in either lane. The promisor remote URL points at a non-existent local path
  (`…/absent-remote.git`), so no network/transport channel was even reachable. Static
  cross-check of the isolation in the pinned source: `GIT_ISOLATION = ("--no-replace-objects",
  "--no-lazy-fetch", …)` is prepended to **every** `git` call
  (`tools/report-landing-audit.py:138`, `:162`); `--no-lazy-fetch` is thus on the auditor's
  own git invocations, not only on the grid's probes. (This is a static read only; PM08 was
  **not** executed.)

## Why exit 0 is the correct verdict here (observed source, not inference)

- The report's single citation is the lane master commit `58866b56…`, which is present, so
  `lookup()` returns `found` and `refuse_unknown()` skips it
  (`tools/report-landing-audit.py:430-431`). The store-wide missing-object diagnosis is
  therefore never even computed for this fixture (`store.missing()` is reached only from
  `unknown_citation()` / `opaque_hole()`, lines 698 and 714, i.e. only for a citation that no
  audited repository resolves).
- The hole is a **blob**, so it is not an opaque hole (a missing tree or commit), and it is
  unreachable from the audited root `refs/heads/master`; `round_commits()` enumerates
  `git log master` (line 291), so the unselected `side` branch is outside the audited
  history.
- This is exactly the amended contract, `oracle-amendment-1.json` `prospective_expected[4]`
  ("Incomplete but locally sufficient repositories are not refused merely because an
  unrelated historical blob, branch, or unused file is missing") and
  `prospective_expected[0]`/`[3]` (promisor metadata alone never changes a clean/failed
  verdict; marked and unmarked twins keep identical substantive verdicts).

## Fixture weaknesses (reported separately from source findings)

**F1 (medium) — the fixture's own premise never asserts that the hole exists.** The grid
records the premise with `missing_objects(lane, "refs/heads/master")`
(`tests/report-audit/promisor-grid.py:293-296`, called at `:463`), which is rooted at the
*audited* branch. For this family that premise is `[]` — "no missing object" — even though
a blob **is** missing (my direct `--all` walk finds exactly one hole). Consequently:
(i) the recorded premise for PG31/PG32 reads as "nothing is missing" and understates the
fixture, and (ii) the graded expectation (exit 0, clean) is satisfied **identically if the
hole were absent**: if a future builder change stopped deleting the side blob, PG31 and PG32
would still be exit 0, still twin-equal, and the row would still report `met`. The row
therefore does not, on its own, prove the "unrelated hole does not block" property; it
proves the "promisor metadata does not refuse" property (which the frozen arm's exit 2 with
`partial clone (remote.origin.promisor)` shows is genuinely exercised).
Minimal correction (not applied — production is read-only for this lane): have the builder
assert the hole explicitly, e.g. after the drop, require that the side blob is absent while
the side commit and its tree are present, and/or record `missing_objects(lane, "--all")`
in the premise as a distinct field, so that a regression in the drop step fails the
premise (exit 2) instead of silently passing.

**F2 (low) — the fixture does not exercise the missing-object machinery at all.** Because the
only citation resolves, the auditor never computes the store-wide hole list, so PG31/PG32
say nothing about how the auditor *treats* a known-missing unrelated object; they only
show that it never looks. A stronger twin would keep the hole in the store while making it
*visible* to the auditor (for example by citing it, which is what the ungraded open row
`PG40-missing-cited-unselected-branch-object-promisor` attempts). Relatedly, the side
commit's subject is `side: file`, which does not match the auditor's required-candidate
pattern `^(?:round-1:|checkpoint\(r1\))` (`tools/report-landing-audit.py:300`); a side
commit that *were* a round-1 candidate would be a sharper test of "unselected branch is
outside the audited history".

**F3 (low, manifest not source) — `PM07`'s `expect_rows` names PG31/PG32, but the mutant
cannot be distinguished there.** `PM07-full-all-missing-gate` roots the traversal at `--all`
instead of `present_roots(repo)` (`tests/report-audit/promisor-mutants.py:381-384`), but
`present_roots()` already enumerates *every* present commit/tree/tag
(`tools/report-landing-audit.py:635-648`), a superset of `--all`; and in PG31/PG32 the
traversal is not even computed (all citations resolve). The mutant is therefore
observationally identical on these rows. The mutant's own prose already says so ("Redundant
on a candidate whose traversal already starts from every present object: there it is
observationally identical, survives, and is credited with no kill"), so this is not a
contradiction in the runner's semantics — but the `expect_rows` list reads as if PG31/PG32
could kill PM07, and they cannot. The gap that matters: **no mutant in the inventory
attacks the "unrelated hole must not become a blanket precondition" contract that PG31/PG32
were written for** (PM03/PM04/PM10 all target the *cited* hole, PG33/PG34/PG46/PG47).

## Source findings

**None.** On the surface this family exercises (promisor-marked lane, complete audited-root
closure, one missing blob reachable only from an unselected branch, one resolvable citation),
`tools/report-landing-audit.py` at `2e254a17` produces the ordinary clean verdict, refuses
nothing, names no metadata reason, acquires nothing, and produces a document identical to
its unmarked twin's. I did not find a defect to correct in the source.

## Observed vs inferred

- Observed (executed and read back): every exit code, every stderr byte, every digest, both
  fixture layouts, the missing/present status of each object, the defect/token lists, the
  object inventories before/after, the raw document diff, the grid's per-row grades, the
  twin comparison.
- Inferred (source reading, not executed): that the missing-object diagnosis is never
  computed for this fixture (from `refuse_unknown`/`unknown_citation`/`opaque_hole`
  control flow), that `round_commits` excludes the `side` branch (from `git log <branch>`),
  that `present_roots` is a superset of `--all` (from the two code paths), and that the
  auditor's own git calls all carry `--no-lazy-fetch` (from `GIT_ISOLATION`; the flag was
  read statically only — PM08 was not executed).

## Residual risk / verification gaps

1. **F1 stands**: the graded expectation for PG31/PG32 is not sensitive to the presence of
   the hole. My independent `--all` walk establishes that the hole is present in the
   fixtures as built today; a future builder regression that silently stopped deleting the
   blob would not be caught by this row.
2. The "no objects acquired" evidence rests on the promisor remote pointing at a
   non-existent local path. A *successful* lazy fetch is impossible here; the observable
   evidence is therefore "no fetch happened and no object appeared", which is exactly the
   pin the round contract requires, but it does not distinguish "never attempted" from
   "attempted and failed" (both would surface as exit 2 and fail the row anyway).
3. `--selftest`, the full 47-row grid, `repo-state-grid.py`, the mutation grid and the
   auditor's own selftest were **not** run (out of scope for this bounded lane).
4. `PG40-missing-cited-unselected-branch-object-promisor` — the open, ungraded cell of the
   same family — was not executed and remains an open traversal-scope question for L1; my
   F2 observation explains why the graded twin of that family cannot substitute for it.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseUnselectedBranch.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseUnselectedBranch/grid-PG31-PG32.json` — assigned run stdout (both arms, 2 cases)
- `…/out/CaseUnselectedBranch/grid-PG31-PG32.stderr.txt` — empty stderr capture
- `…/out/CaseUnselectedBranch/grid-PG31-PG32-keep.json` — second run with `--keep` (fixtures retained for direct inspection)
- `…/out/CaseUnselectedBranch/verdict-PG31-direct.json`, `…/verdict-PG32-direct.json` — direct auditor verdicts (both exit 0, empty stderr)
- `…/out/CaseUnselectedBranch/verdict-PG31-direct.stderr.txt`, `…/verdict-PG32-direct.stderr.txt` — empty stderr captures
- `…/out/CaseUnselectedBranch/grid/population.json`, `…/grid/candidate.json` — the grid's own `--out` dump (population sha `612b0a74…`, 47 rows)

Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseUnselectedBranch`
(clone + `tmp/` fixtures + direct-run outputs).

Production lane `production/.jj/index`, fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload
was used; PM08 was not executed. No tool was installed or updated (git 2.56.0 and Python
3.14.8 were already present).

## Unverified items

- The full population (47 rows) was not run; only PG31 and PG32 were executed, twice each
  (grid run + direct auditor run), and the `--keep` fixtures were inspected directly.
- The frozen (r23) arm was exercised only through the grid's frozen blob
  `0df800e8…`; I did not diff the r23 auditor source against the pinned one beyond reading
  its refusal message.
- No mutation was executed against these rows (PM07 and the other mutants were read, not
  run); F3 is a static reading of the mutant definition plus the source control flow.
- The auditor's `selftest` and the grid's `--selftest` were not run.
- Whether the `absent-remote.git` path could ever be reachable in another environment was
  not probed (no network use was permitted and none was attempted).

Report: .ufo/waves/round-24/falsify/advice/CaseUnselectedBranch.md

---

## Append (after a cross-lane hazard notice; nothing above is removed)

**A10 — lazy-fetch materialisation hazard checked against this lane's fixtures (observed).**
A sibling lane (`KamaR23-2.CaseFleetBlobless`, PG43) reported that a stray `git` probe
without `--no-lazy-fetch` against a **blobless clone** keeps `remote.origin.url` pointing at
a *reachable* `file://` origin, so the probe lazy-fetches and materialises the missing blob:
the premise evaporates and the auditor can return a false `clean` exit 0 instead of the
correct exit 2. I checked my own `--keep`ed PG31/PG32 fixtures against that hazard:

- **Not structurally exposed.** PG31/PG32 do not use the grid's `blobless_clone()` builder;
  they build an ordinary local repository and mark it with promisor *config* whose
  `remote.origin.url` points at `…/current/000/absent-remote.git` (verified: the path does
  not exist). A stray probe could at most attempt a fetch from a missing path — it cannot
  materialise an object.
- **No materialisation actually occurred.** Re-verified after all of my probes, including
  the one `git rev-parse refs/heads/side:side.txt` issued *without* `--no-lazy-fetch`:
  side blob `2299c37978265a95cbe835a4b0f0bbf15aad5549` still **ABSENT** in both fixtures,
  both lane stores still hold exactly 7 objects, and the `--all` missing walk still reports
  exactly one hole (`?2299c379…`). Every object-content probe I ran
  (`cat-file -e`, `cat-file --batch-all-objects`, `rev-list --missing=print`) did carry
  `--no-lazy-fetch`; the `--no-replace-objects` flag was carried on the presence probes as
  well.
- **Auditor-side isolation is unaffected:** every git call the pinned auditor makes is
  prefixed with `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)`
  (`tools/report-landing-audit.py:138`, applied at `:162`), so the two direct auditor runs
  against the kept fixtures could not have materialised the blob either — consistent with the
  unchanged 7-object stores.

Consequence for this report: **no conclusion changes**. The PG31/PG32 verdict (exit 0, clean,
twin-identical, no acquisition) stands, and the F1 finding is *strengthened* rather than
weakened — the hole really is still present in the kept fixtures at the end of my inspection.
The observation is recorded because the same manual-inspection hazard would apply to any
blobless-clone fixture (`c_hydrated_blobless_*`, `c_unhydrated_blobless_lane`,
`c_fleet_unhydrated_blobless`) and because the general rule for anyone probing a `--keep`ed
grid fixture is: **every** git probe must carry `--no-lazy-fetch`.

Report: .ufo/waves/round-24/falsify/advice/CaseUnselectedBranch.md
