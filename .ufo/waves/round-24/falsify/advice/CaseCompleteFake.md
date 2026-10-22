# CaseCompleteFake — PG23/PG24/PG25 promisor-grid falsification (round 24)

VERDICT: **HOLDS** for the graded (amended) contract on all three rows — the assigned
selection exits 0 with 0 violations in both arms, the exact finding/token pairs, the exact
twin equality and the no-acquisition property all hold. The **originally registered**
expectation for PG23/PG24 (unknown citation ⇒ exit 2) is **not achieved and stays visibly
unachieved** (`met_original: false`, listed in `withdrawn_original_failures`); it is not
relabelled passed anywhere. **No source defect** was found in `tools/report-landing-audit.py`
on the surface this family exercises. Two fixture-level observations (F1, F2) and one
informational observation (F3) are reported separately below.

Scope: exactly the assigned bounded selection —
`python3 tests/report-audit/promisor-grid.py --arm both --case PG23-unknown-citation-complete-promisor --case PG24-unknown-citation-fleet-promisor --case PG25-unknown-citation-plain --json`
— run in my own scratch clone at the pinned commit (twice: once plain, once with `--keep` so
the built fixtures could be inspected directly), plus static source reads of the auditor and
the runner, plus three direct auditor invocations against the kept fixtures, plus one extra
bounded offline probe (a reachable local `file://` promisor remote) that closes the
"no lazy fetch" gap the fixture's dead remote leaves open. No other lane suite, no full
47-row grid, no mutation grid, no selftest, no execution-bearing probe (PM08 was **not**
executed). No production file other than this report and the `out/` artifacts was written;
production `production/.jj/index`, fleet, sibling lanes, operator config, routing, services
and real object stores were not touched.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Assigned command, exit, in the pinned clone | PASS — exit 0, stderr empty, 3 graded rows, **0 violations in both arms** (current and frozen) |
| A2 | Actual missing / present objects asserted on the built fixture | PASS (observed) — **zero** missing objects in lane and fleet under three independent walks (audited root, `--all`, and the auditor's own `present_roots` traversal); the fabricated token is **absent** from both stores (bare and `^{commit}` lookups both answer `… missing`) |
| A3 | Marked vs plain twins are content-identical | PASS (observed) — identical lane commit `58866b56…`, fleet commit `6d6ce9c9…`, report blob `a712c668…`, 5 lane objects / 9 fleet objects each; the **only** difference is the promisor config on the intended side (lane for PG23, fleet for PG24, none for PG25) |
| A4 | Exact finding/token pairs | PASS — current arm, all three rows: `defects` and `raw_defects` both `[(landed-unresolved, 0123456789abcdef0123456789abcdef01234567), (unresolved-full-hash, 0123…4567)]`, `kinds [landed-unresolved, unresolved-full-hash]` — equal to the amended expectation's `defects`/`kinds` for PG23/PG24 and to the original (=live) expectation for PG25 |
| A5 | Content-derived reason IDs | VACUOUS for the current arm — the pinned auditor refuses nothing on these rows (exit 1, **stderr 0 bytes**), so no reason string exists to classify; the `reason_forbidden` list (`"partial clone ("`, `"promisor pack"`) is satisfied vacuously. The **frozen** arm's reason is exactly the forbidden r23 metadata refusal (`partial clone (remote.origin.promisor)`) and the current arm does not reproduce it |
| A6 | No objects acquired | PASS (observed four times) — grid pin `objects_acquired {lane: [], fleet: []}` on all six rows; independently, after the grid run **and** three further direct auditor runs the lane still holds 5 objects, the fleet 9, the token is still absent from both, no `FETCH_HEAD` exists, no pack was written, and refs / config / remotes / reflog are byte-identical before and after |
| A7 | Actual twin document comparison | PASS (observed twice) — grid `twins {PG25: true}` on PG23, `{PG25: true}` on PG24, `twin_equal true` on all three, `twin_mismatch []`, `twin_pairs_compared` = all three cases; independently, the three raw verdict documents differ in **exactly one line** (the `report` path) and are **byte-identical** after replacing the fixture root by a placeholder (unified diff: no difference) |
| A8 | Original (withdrawn) expectation kept visible and **not** relabelled passed | PASS — PG23 and PG24 carry an `amended` key whose expectation differs from `original`; in the current arm `met_original: false` for both and both appear in `withdrawn_original_failures: ["PG23-…", "PG24-…"]`, while `met_amended: true`. PG25 carries **no** `amended` key, so its graded column is its `original` column (`met_original: true`, `met_amended: true`). The original registration (exit 2, `reason_class: unknown-citation`) is **not met and not claimed** |
| A9 | Frozen (r23) baseline retained, not an improvement target | PASS — the frozen arm satisfies its own frozen pins (`met_frozen` true on all three) and **fails** the amended view exactly on the two promisor-marked rows (`amended_view_unmet: [PG23-…, PG24-…]`): that is the r23 harm the repair removes. `met_amended_frozen` is true for PG25, i.e. the plain control is unchanged between r23 and r24 (no-harm) |
| A10 | No lazy fetch / transport, even with a **reachable** remote | PASS (observed, extra probe) — with the lane's `remote.origin.url` repointed at a real local repository that **holds** the cited 40-hex token, the pinned auditor still exits 1 with the same two findings, acquires nothing, leaves the token absent from the lane and writes no `FETCH_HEAD` |

## Snapshot, digests, environment (observed)

```
clone:  git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
            /fast/scratch/hyaku/kama-r24/falsify/CaseCompleteFake/repo
        git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
HEAD  =  2e254a1763a9c08aa07fc53081287f506c447d84  (detached; tracked worktree clean)
```

| Item | Digest / value | Cross-check |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` | matches the assignment; the clone's tree is byte-identical to the production tree at the same commit (`diff` of the grid script: empty) |
| auditor `tools/report-landing-audit.py` | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | matches the assignment's source tool; equals the grid's reported `auditor_sha256.current` |
| runner `tests/report-audit/promisor-grid.py` | sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | matches the assignment's runner |
| manifest `tests/report-audit/promisor-grid-expectations.json` | sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | matches the assignment's manifest; equals the grid's reported `expectations_sha256` |
| frozen auditor (r23 base blob `0df800e8…`) | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` | equals `derived_from.frozen_auditor_sha256` pinned inside the expectations file |
| population | `population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`, `population_size 47` | fixed47 population; identical to the value recorded by L1 in `build/out/GridOracle/{population,candidate}.json` — my run used the same population and an **unchanged** manifest |
| toolchain | `git version 2.56.0` (≥ the inherited 2.45 floor), `Python 3.14.8` | pre-existing; **no install or update was performed** in this lane |

## A1/A4/A5 — the assigned command (observed)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/CaseCompleteFake/repo
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseCompleteFake \
    python3 tests/report-audit/promisor-grid.py --arm both \
      --case PG23-unknown-citation-complete-promisor \
      --case PG24-unknown-citation-fleet-promisor \
      --case PG25-unknown-citation-plain --json
EXIT=0     (stderr empty, 18654 bytes of JSON on stdout)
```

Grid summary (observed):

```
frozen : graded=3 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_met=1/3  amended_view_unmet=["PG23-unknown-citation-complete-promisor",
                                                    "PG24-unknown-citation-fleet-promisor"]
         withdrawn_original_failures=[]  twin_mismatch=[]  twin_compared=0 (no documents to compare)
current: graded=3 violations=0 tracebacks=0 timeouts=0 harness_leaks=0
         amended_view_unmet=[]  withdrawn_original_failures=["PG23-…","PG24-…"]  twin_mismatch=[]
         twin_compared=3  twin_pairs_compared=["PG23-…","PG24-…","PG25-…"]
```

Per-row observations (observed):

| Row | arm | exit | defects / raw_defects | kinds | met |
|---|---|---|---|---|---|
| PG23-unknown-citation-complete-promisor | current | 1 | `[(landed-unresolved, 0123…4567), (unresolved-full-hash, 0123…4567)]` / same | `[landed-unresolved, unresolved-full-hash]` | `met_amended true`, **`met_original false`** (withdrawn) |
| PG24-unknown-citation-fleet-promisor | current | 1 | same | same | `met_amended true`, **`met_original false`** (withdrawn) |
| PG25-unknown-citation-plain | current | 1 | same | same | `met_amended true`, `met_original true` |
| PG23-…-promisor | frozen | 2 | n/a (no document) | n/a | `met_frozen true`, `met_amended_frozen false` |
| PG24-…-promisor | frozen | 2 | n/a (no document) | n/a | `met_frozen true`, `met_amended_frozen false` |
| PG25-…-plain | frozen | 1 | same defects | same | `met_frozen true`, `met_amended_frozen true` |

Frozen stderr (exact, observed):

```
PG23: could-not-evaluate: …/current/000/lane: partial clone (remote.origin.promisor)
PG24: could-not-evaluate: …/current/001/fleet: partial clone (remote.origin.promisor)
```

— the r23 blanket metadata refusal, i.e. exactly the harm the amended contract removes, and
exactly the string the current arm must not produce (`reason_forbidden`). The current arm
produced **no stderr at all** on all three rows.

Verdict document (current arm, identical for all three rows after path normalization): one
round, `report_committed true`, `cutoff 2000`, `round_commits 1`, `required 1`,
`post_report []`, `source_url_hashes []`, `defects` = the two pairs above;
`summary.status "failed"`, `summary.defects 2`, `summary.uncorrected 2`,
`by_kind {landed-unresolved 1, unresolved-full-hash 1}`, `required_commits 1`,
`errata_rows 0`. A real audit ran; the document is neither empty nor short-circuited, and
`landed-omitted` is 0 because the lane commit *is* cited.

## A2/A3 — the fixture premises, asserted directly on the kept fixtures (observed)

The `--keep` run left the built fixtures at
`…/CaseCompleteFake/promisor-grid-dbv6gwha/current/{000,001,002}/` (000 = PG23, 001 = PG24,
002 = PG25). Directly measured with `git --no-lazy-fetch --no-replace-objects` (never a
network or transport call):

| Assertion | PG23 (000, lane marked) | PG24 (001, fleet marked) | PG25 (002, plain) |
|---|---|---|---|
| lane store size | 5 objects | 5 | 5 |
| fleet store size | 9 objects | 9 | 9 |
| missing objects, audited root (`refs/heads/master` / `HEAD`) | `[]` | `[]` | `[]` |
| missing objects, `--all` walk | `[]` | `[]` | `[]` |
| missing objects, auditor's own `present_roots` traversal (all present commit/tree/tag roots) | `[]` | `[]` | `[]` |
| opaque holes (missing tree/commit) | `[]` | `[]` | `[]` |
| fabricated token `0123…4567` present in lane / fleet | false / false | false / false | false / false |
| token bare lookup (`cat-file --batch-check`) | `0123…4567 missing` | `0123…4567 missing` | `0123…4567 missing` |
| token peeled lookup (`^{commit}`) | `0123…4567^{commit} missing` | same | same |
| promisor config | lane: `remote.origin.promisor=true`, `extensions.partialclone=origin`, `remote.origin.url=<…>/absent-remote.git`; fleet: none | lane: none; fleet: same three keys | none in either |
| `FETCH_HEAD` present | false | false | false |
| packs in `objects/pack` | `[]` | `[]` | `[]` |
| lane master commit | `58866b563cd900df310588effe79028efc104c33` | identical | identical |
| fleet master commit | `6d6ce9c90cc7904557d3069ea08d4d50c6cf937a` | identical | identical |
| fleet report blob | `a712c6689de5a00eaa6a3b9c269694387aa94adc` | identical | identical |
| report body | `# kama round 1` / `## Landed changes` / `- 58866b56…` / `- 0123…4567` | identical | identical |

So the three fixtures are content-identical twins and the only difference is the promisor
configuration on the intended side. The "complete promisor" claim of PG23/PG24 is literally
true: the marked repository has **no** hole at all, neither under the audited root nor under
any other walk. The fabricated token sits in the `## Landed changes` section (asserted by
`fake_in_landed_section: true` in my independent re-build), which is why both an
`unresolved-full-hash` (whole-report 40-hex scan) and a `landed-unresolved` (Landed-section
citation scan) are raised for it.

## A4/A6/A7 — independent re-verification outside the grid's own bookkeeping (observed)

Three direct invocations of the pinned auditor against the kept fixtures (read-only, local,
`--no-errata`, exactly the argv the grid uses, `cwd` = fixture dir):

```
$ python3 tools/report-landing-audit.py --lane-repo …/current/000/lane \
      --fleet-repo …/current/000/fleet --rounds 1 --json --no-errata
EXIT=1   stderr 0 bytes
$ … --lane-repo …/current/001/lane --fleet-repo …/current/001/fleet --rounds 1 --json --no-errata
EXIT=1   stderr 0 bytes
$ … --lane-repo …/current/002/lane --fleet-repo …/current/002/fleet --rounds 1 --json --no-errata
EXIT=1   stderr 0 bytes
```

- **Finding/token pairs**: each document carries `results[0].defects` =
  `{unresolved-full-hash, landed-unresolved}` on the token `0123…4567`, with
  `corrected_by []` on both, and `summary.by_kind` = `{landed-unresolved 1,
  unresolved-full-hash 1}` — exactly the amended expectation's `kinds` and `defects`.
- **Twin comparison, raw**: `diff` of the three raw documents reports exactly **one**
  differing line each — the `"report"` path (`…/current/000/fleet/…` vs `…/current/001/fleet/…`
  vs `…/current/002/fleet/…`). After replacing the fixture root by a placeholder, the
  documents are **byte-identical** (unified diff: no difference). The grid's `twin_equal:
  true` is therefore not an artifact of over-aggressive normalization.
- **No objects acquired**: after the grid run *and* these three extra auditor runs, the lane
  still holds exactly 5 objects and the fleet 9; the token is still absent from both; no
  `FETCH_HEAD` exists; `objects/pack/` is empty in both; and refs, config, remote list and
  reflog are byte-identical before and after each run.

## Why exit 1 is the correct verdict here (observed source, not inference)

- The lane commit `58866b56…` cited in the report is present, so `lookup()` returns `found`
  and `refuse_unknown()` skips it (`tools/report-landing-audit.py:430-431`); the
  store-wide missing-object diagnosis is therefore never computed for a resolved citation.
- The fabricated token is `absent` in both stores, and the stores have **no** missing object
  at all: `unknown_citation()` (`:689-701`) finds no missing id equal to or prefixed by the
  token, and `opaque_hole()` (`:705-717`) finds no missing tree/commit that could hide it.
  Both are therefore `None`/`(None, None)` and no refusal is raised.
- The token is consequently a proved **local** absence → `unresolved-full-hash`
  (`:477-478`) and `landed-unresolved` (`:496-498`) — a failed verdict, exit 1.
- This is exactly the amended contract: `oracle-amendment-1.json` `prospective_expected[0]`
  ("Promisor metadata alone never changes local-object resolution or a clean/failed
  verdict"), `[3]` ("Complete marked versus unmarked twins, including fabricated citations,
  retain identical substantive verdicts") and `[5]` ("Do not claim remote repository
  completeness or remote abbreviation uniqueness"). The amended expectation cells for
  PG23/PG24 encode precisely this (exit 1, the two kinds, the `$fake` token), and the
  fixture is a true twin of PG25, so the row is internally consistent.

## A10 — extra bounded probe: a **reachable** promisor remote (observed)

The grid's `mark_config()` points `remote.origin.url` at a **non-existent** path
(`<tmp>/absent-remote.git`). A lazy fetch there would fail, so the in-row evidence cannot
distinguish "never attempted" from "attempted and failed" (both surface as exit 2 and would
fail the row anyway). I closed that gap with one bounded, offline, `file://`-only probe
(no network, no execution payload):

- Rebuilt the PG23 shape with the grid's own builder, then repointed the lane's
  `remote.origin.url` at a **real** local repository that **holds** the cited 40-hex token
  (`c4da532a21493aff5ad4695f88f7bd77b7882a29`); the lane does not hold it; the fleet report
  cites it.
- Current auditor: **exit 1**, defects `[(landed-unresolved, c4da53…), (unresolved-full-hash,
  c4da53…)]`, stderr empty, `objects_acquired {lane: [], fleet: []}`, the token **still
  absent** from the lane afterwards, no `FETCH_HEAD` written. A lazy fetch would have
  resolved the token and removed both findings; it did not happen, and no transport was
  invoked against a remote that was reachable.
- Frozen r23 auditor on the same fixture: exit 2 with `partial clone (remote.origin.promisor)`
  — the historical baseline only, never a target.
- Static cross-check (read only, PM08 **not** executed): `GIT_ISOLATION = ("--no-replace-objects",
  "--no-lazy-fetch", …)` (`tools/report-landing-audit.py:138`) is prepended to **every** git
  call, so the isolation is on the auditor's own invocations, not only on the grid's probes;
  the auditor contains no `fetch`/`remote`/`ls-remote` call and no promisor-specific code path
  (the only mentions of "promisor" in the file are in the module docstring).

## Fixture observations (reported separately from source findings)

**F1 (low) — the in-row evidence for "no lazy fetch" is only indirect.** `mark_config()`
(`tests/report-audit/promisor-grid.py:197-201`) sets the remote URL to a path that does not
exist, so within PG23/PG24 a lazy fetch would *fail* rather than succeed; the row then fails
on the exit code, but the row cannot distinguish "never attempted" from "attempted and
failed". Minimal correction (production is read-only for this lane; **not applied**): point
`remote.origin.url` at a real local repository that holds an object the report cites, so a
fetch would change the verdict instead of only its exit code. My probe above is exactly that
variant and it passes, so the *source* is sound; the fixture alone is weaker than the
contract it is used to certify.

**F2 (low) — the "completeness" premise is rooted at the audited branch only.** The grid
records `lane_missing`/`fleet_missing` from `missing_objects(repo, "refs/heads/master")`
(`tests/report-audit/promisor-grid.py:293-296`, called at `:463`), i.e. rooted at the audited
root. For this family that premise is `[]`, which is also the *expected* value, so the
premise cannot fail; completeness of the whole store is not asserted by the row. I
compensated with two extra walks (the `--all` walk and the auditor's own `present_roots`
traversal over every present commit/tree/tag): both report **zero** holes, so the premise
"complete" is true for the fixtures as built today — but a future builder regression that
left a hole outside the audited root would not be caught by this row. Minimal correction
(not applied): record `missing_objects(repo, "--all")` as a distinct premise field.

**F3 (informational) — one underlying defect, two graded pairs.** The two expected pairs
(`landed-unresolved` and `unresolved-full-hash`) both name the *same* fabricated token: they
come from two independent scans of one citation (the whole-report 40-hex scan at `:477` and
the Landed-section abbreviation scan at `:496`). The graded `defects` list therefore has
length 2 for one substantive defect; `summary.defects 2` must not be read as "two
independent defects". This is the auditor's kind taxonomy, not a defect, but it matters for
any score that counts defect rows.

**F4 (informational, no harm found) — the graded expectation for PG23/PG24 is PG25's
expectation.** The three fixtures are byte-identical twins, so the "twin" property the row
asserts is nearly tautological; what the row genuinely exercises is "promisor metadata must
not cause a refusal", and that *is* exercised (the frozen arm exits 2 with the metadata
reason on exactly these two rows and exits 1 on PG25). No harm found; recorded so the row's
sensitivity is not over-estimated.

## Source findings

**None.** On the surface this family exercises (a promisor-marked but **complete** lane
(PG23) or fleet (PG24), one fabricated citation that exists nowhere, one resolvable lane
commit), `tools/report-landing-audit.py` at `2e254a17` produces the ordinary failed verdict
with the exact two findings, refuses nothing, emits no metadata reason, acquires nothing,
contacts no remote (even a reachable one), and produces a document identical to its unmarked
twin's. I did not find a defect to correct in the source.

## Observed vs inferred

- Observed (executed and read back): every exit code, every stderr byte, every digest, the
  kept fixture layouts, the missing/present status of every object, the defect/token lists,
  the object inventories and refs/config/reflog before and after, the raw document diffs,
  the grid's per-row grades, the twin comparisons, the probe's fetch outcome.
- Inferred (source reading, not executed): that the store-wide missing-object diagnosis is
  never computed for a resolved citation and is empty for the fabricated one (from
  `refuse_unknown`/`unknown_citation`/`opaque_hole` control flow), and that the auditor's own
  git calls all carry `--no-lazy-fetch` (from `GIT_ISOLATION`; the flag was read statically
  only — PM08 was not executed).

## Residual risk / verification gaps

1. **F2 stands**: the row's completeness premise is branch-rooted; my extra `--all` and
   `present_roots` walks establish completeness today, but a future builder regression
   outside the audited root would not fail the row.
2. **F1 stands**: the in-row "no fetch" evidence is indirect (dead remote); the probe
   supplies the direct evidence, but the fixture itself does not.
3. This lane ran **only** PG23/PG24/PG25 (3 of 47 rows). The full population, the
   `--selftest`, `repo-state-grid.py`, the mutation grid, the auditor's own selftest and the
   historical-parity recipe were **not** run (out of scope for this bounded lane).
4. The behaviour of the *other* promisor families (blobless clones, errata splice, missing
   cited blob, opaque tree) was not re-verified here; sibling lanes own those.
5. The frozen arm was exercised only through the grid's frozen blob `0df800e8…`; I did not
   diff the r23 auditor source against the pinned one beyond reading its refusal message.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseCompleteFake.md` (this report)
- `…/.ufo/waves/round-24/falsify/out/CaseCompleteFake/grid-PG23-PG24-PG25.json` — assigned run stdout (both arms, 3 cases)
- `…/out/CaseCompleteFake/grid-PG23-PG24-PG25.stderr.txt` — empty stderr capture
- `…/out/CaseCompleteFake/grid-keep.json` — second run with `--keep` (fixtures retained for direct inspection)
- `…/out/CaseCompleteFake/grid-keep.stderr.txt` — empty stderr capture
- `…/out/CaseCompleteFake/verdict-PG23-direct.json`, `verdict-PG24-direct.json`, `verdict-PG25-direct.json` — direct auditor verdicts (all exit 1, empty stderr)
- `…/out/CaseCompleteFake/verdict-PG2{3,4,5}-direct.stderr.txt` — empty stderr captures
- `…/out/CaseCompleteFake/independent-verification.json` — independent premise verification (missing/present objects, promisor facts, report body, token placement, per-row state deltas)
- `…/out/CaseCompleteFake/lazy-fetch-probe.json` — the reachable-remote probe (A10)
- `…/out/CaseCompleteFake/fixture-verification.txt` — the evidence sheet in plain text

Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CaseCompleteFake`
(clone, `verify.py`, `probe.py`, the kept grid root `promisor-grid-dbv6gwha`, and the raw
run outputs).

Production lane `production/.jj/index`, fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload
was used; PM08 was not executed. No tool was installed or updated (git 2.56.0 and Python
3.14.8 were already present).

## Unverified items

- Only PG23, PG24 and PG25 were executed: the assigned grid selection (twice) plus three
  direct auditor runs plus one extra probe. The other 44 rows of the fixed47 population were
  not run in this lane.
- The grader's internal `check_exit2_form` path (typed could-not-evaluate, content-derived
  reason, no verdict document) was **not** exercised by these rows — the current arm never
  refuses here — so the reason-content pin is untested by this family.
- No mutation was executed against these rows (PM07 and the other mutants were read, not
  run).
- The auditor's `selftest` and the grid's `--selftest` were not run.
- Whether the `absent-remote.git` path could ever be reachable in another environment was
  not probed (no network use was permitted and none was attempted); my probe used a
  deliberately reachable local `file://` remote instead.

Report: .ufo/waves/round-24/falsify/advice/CaseCompleteFake.md

---

## Append — source-ledger supplement (scope note, nothing above is removed)

The pinned-revision ledger note for this stage (`S105` records the explicit rejected `S095`
cross-API inference; only mutable used-by cells reconciled; the original `S095` *teaches* row
stays filed; current rows 105; source-census final verification is **L1-owned after this
stage**) is **outside this lane's scope**: this lane is a bounded fixture-family
falsification of PG23/PG24/PG25 and performs no source census, no ledger edit and no
reconciliation of used-by cells. Nothing in this report should be read as verifying or
amending row 105 or row 95. The only ledger-adjacent fact observed here is that the
fixed47 population hash my run used (`612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`,
47 rows) and the manifest hash (`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`)
are identical to the values recorded by L1 in `build/out/GridOracle/{population,candidate}.json`,
i.e. **no expectation cell was changed by this lane** — a statement about the manifest's
bytes, not about the ledger.

Report: .ufo/waves/round-24/falsify/advice/CaseCompleteFake.md
