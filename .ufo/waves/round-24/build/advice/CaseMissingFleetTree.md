# CaseMissingFleetTree — offline oracle case: fleet ancestor tree missing for report traversal

Lane: reviewer (leaf, no dispatch). Scope: ONE oracle case, specified and constructed offline.
Base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (auditor blob sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`).
Host: git 2.56.0, python 3.14.8. No installs. No network. No production file touched.

## Verdict

The case is specified, constructed and measured. Expected exits and findings were fixed in
`build/out/CaseMissingFleetTree/expected.json` **before** the fixture existed and before any
candidate implementation existed. The frozen r23 base and the current in-flight candidate both
answer the four rows as the preregistration requires: a genuinely unavailable required tree is
**could-not-evaluate (exit 2)** — never a clean or failed verdict — while a *complete*
promisor-marked fleet is audited normally (exit 0, clean), which is the r23 operability harm this
round removes.

## Acceptance points (what the candidate must satisfy)

1. **Missing required fleet ancestor tree ⇒ exit 2, no verdict.**
   The fleet history traversal that establishes a report's first-add cutoff diffs the tree of every
   commit on the path. With F1's root tree absent, the cutoff is *unknown*; unknown is not absence.
   No clean verdict, no failed verdict, no defect list, no guessed cutoff.
   (preregistration `expected_after` bullet 3)
2. **The refusal must be availability-based, not metadata-based.**
   MFT-1 (promisor-marked, tree absent) and MFT-2 (identical, no promisor metadata) differ only
   in configuration and must reach the same outcome. A candidate that refuses one and answers the
   other has implemented metadata policy, not the preregistered policy.
3. **Complete + promisor-marked ⇒ exit 0 with the ordinary clean verdict.**
   Metadata alone must not refuse. (preregistration `expected_after` bullet 1)
4. **No transport, no program execution, no deadline change.** The promisor remote points at a
   local canary repository; after the audited run the canary's refs are unchanged, no `FETCH_HEAD`
   appears, no pack is added.
5. **No traceback, no unhandled exception**: exit 2 goes through the typed `EvalError` path
   (`could-not-evaluate: …` on stderr), never a Python traceback and never rc 1.

## The case

Fixture family: one lane repository and one fleet repository, in a 2×2 of
{promisor-marked, unmarked} × {ancestor tree absent, complete}.

| object | value |
|---|---|
| lane commit (`round-1: work`, author `kama-shokunin`, author time 1000) | `db796f8b820bf3825c58832419138cdba23206a7` |
| fleet F1 (author time 2000) — first add of `.ufo/reports/round-1/kama.md` | `ebcb436228cc3c28fd415f5afcce3312e1151be4` |
| fleet F2 (author time 2100, adds `notes.txt`) — fleet HEAD | `7f914f947d8ace9307969488a9397dd63f9f98b2` |
| F1 root tree — **removed from the object store** in MFT-1/MFT-2 | `32a58a74577e6abdafe1bec0f017e6df4c79f382` |
| report body | `# kama round 1\n\n## Landed changes\n\n- <lane commit sha>\n` |

Construction, entirely local and offline:

1. `git init -b master` lane and fleet (`gc.auto=0`, `maintenance.auto=false`).
2. lane: one commit `round-1: work` by `kama-shokunin` at author time 1000.
3. fleet: F1 adds the report (author time 2000) citing the lane commit by full 40-hex; F2 adds
   `notes.txt` (author time 2100) and is HEAD.
4. **The deletion**: `git rev-parse F1^{tree}` → `32a58a74…`; the loose object file
   `.git/objects/32/a58a74…` is unlinked. The tree is genuinely absent from the object database;
   every other object, including HEAD's tree and the report blob, stays present.
5. **Promisor marking** (metadata only): `remote.origin.url=<local canary repo>`,
   `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
   `extensions.partialclone=origin`.
6. The canary is a real local git repository with one commit; it exists only to make any lazy
   fetch observable.

Reproducible artifacts: `build/out/CaseMissingFleetTree/case_missing_fleet_tree.py`
(builder + premise checks + measurements + runner), `expected.json` (pre-registered expectations),
`fixture.json` (oids + premise results), `measurements.json`, `audit.json` (frozen base),
`audit-candidate-wip.json`, `grid-row-fragment.py` (paste-ready grid rows).

## Pre-registered expected exits / findings

`build/out/CaseMissingFleetTree/expected.json` (written first; the numbers below are copied from it).

| row | fixture | expected exit | expected verdict / findings | frozen base |
|---|---|---|---|---|
| MFT-1 | marked + ancestor tree absent | **2** | no verdict, no findings | 2 (metadata refusal) |
| MFT-2 | unmarked + ancestor tree absent | **2** | no verdict, no findings | 2 (availability refusal) |
| MFT-3 | marked + complete | **0** | `summary.status=clean`, 0 defects | 2 ← **known r23 harm** |
| MFT-4 | unmarked + complete | **0** | `summary.status=clean`, 0 defects | 0 |

MFT-3 is a **policy row**: the frozen base's exit 2 there is the over-refusal r24 removes, so a
grid that scores both arms against one expectation needs a per-arm expectation for it.

## Premise checks (all measured before the auditor runs)

| premise | MFT-1 | MFT-2 | MFT-3 | MFT-4 |
|---|---|---|---|---|
| report blob readable at fleet HEAD (`git show HEAD:<report>`) | yes | yes | yes | yes |
| fleet HEAD tree present | yes | yes | yes | yes |
| F1 root tree absent (`cat-file -e`) | yes | yes | n/a | n/a (present) |
| `git log --diff-filter=A --format=%at -- <report>` completes | **rc=128** | **rc=128** | rc=0 | rc=0 |

The rc=128 rows are the anti-vacuity check: the traversal that produces the cutoff genuinely
needs the deleted tree, so the row is not a case where a missing object happens to be irrelevant.
Base stderr for that failure: `fatal: unable to read tree (32a58a74577e6abdafe1bec0f017e6df4c79f382)`.

## Measured git behaviour (no auditor involved)

| command (all with `--no-replace-objects --no-lazy-fetch`, `GIT_CONFIG_GLOBAL=/dev/null`) | MFT-1/MFT-2 | MFT-3/MFT-4 |
|---|---|---|
| `git rev-list --objects --missing=print --no-object-names HEAD` | rc 0, one line `?32a58a74577e6abdafe1bec0f017e6df4c79f382` | rc 0, no `?` line |
| `git rev-list --objects --no-object-names HEAD` (no `--missing`) | **rc 128** `fatal: bad tree object 32a58a74…` | rc 0 |
| `git cat-file --batch-check` on the tree | `32a58a74… missing` | `32a58a74… tree 31` |
| `git log --format=%H HEAD` (commit traversal) | rc 0 — commits readable, only the tree is gone | rc 0 |
| `git fsck --no-progress` | rc 2 | rc 0 |

Consequence for the repair: the missing ancestor tree **is** discoverable by an explicit closure
check (`rev-list --objects --missing=print`), and the promisor metadata does not hide it from that
check (MFT-1 and MFT-2 give the identical `?` line). The plain closure listing fails loudly
instead, and the report traversal fails loudly instead — so both a closure-check implementation
and a fail-closed traversal implementation answer exit 2 here.

**Transport note (bounded, opt-in, not a graded row).** One deliberate control probe repeated a
single `cat-file` lookup with the isolation flags dropped, in a throwaway copy of the fleet:
git then ran its own `upload-pack` against the **local** canary
(`fatal: git upload-pack: not our ref 32a58a74…`, rc 1). The canary's refs did not change and no
`FETCH_HEAD` was written. This documents that `--no-lazy-fetch` is load-bearing for a
promisor-marked repository. It is file transport to a local directory — no network, no
fixture-configured program — and it is not part of any graded row; the probe is behind
`--unsafe-probe` and off by default (`measurements-unsafe-probe.json`).

## Results

### Frozen base (`0df800e`, auditor sha256 `da5041a8…`)

| row | exit | stderr | verdict document | canary / FETCH_HEAD |
|---|---|---|---|---|
| MFT-1 | 2 | `could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)` | none | untouched |
| MFT-2 | 2 | `could-not-evaluate: git log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md in <fleet>: rc=128 fatal: unable to read tree (32a58a74…)` | none | untouched |
| MFT-3 | 2 | `could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)` | none | untouched |
| MFT-4 | 0 | — | `summary.status=clean`, 0 defects | untouched |

MFT-1's base reason is the blanket metadata refusal
(`tools/report-landing-audit.py:438-466`, refusals at `:457` promisor pack and `:465` config), not
the missing object: the right answer for the wrong reason. MFT-3 is the harm itself.
Base anchors: `GIT_ISOLATION` `:93`, `git()` `:111-137`, `report_cutoff()` `:215-217`,
`audit_round()` `:302-314` (cutoff call at `:314`).

### In-flight candidate (AuditRepair scratch; auditor blob pinned at sha256 `5cf9c72a6c3d633df259002caf4b82451dca317fa4cb9d67c9308cc7f52bc2bd`)

| row | exit | stderr | verdict | expected |
|---|---|---|---|---|
| MFT-1 | 2 | `could-not-evaluate: <fleet>: unknown: unavailable required object: 1 object(s) reachable from 7f914f94… are missing locally: 32a58a74577e6abdafe1bec0f017e6df4c79f382; promisor evidence: …` — **availability** reason naming the missing object, no metadata refusal | none | 2 ✓ |
| MFT-2 | 2 | `… git log --diff-filter=A --format=%at -- <report> … rc=128 fatal: unable to read tree (32a58a74…)` — fail-closed on git's own error | none | 2 ✓ |
| MFT-3 | 0 | — | `clean`, 0 defects | 0 ✓ |
| MFT-4 | 0 | — | `clean`, 0 defects | 0 ✓ |

The candidate's own availability state agrees: on the MFT-1 fleet
`build_store()` reports `promisor_backed=True`, `missing=['32a58a74577e6abdafe1bec0f017e6df4c79f382']`,
`absence_is_proof=False`; on the MFT-3 fleet `missing=[]`, `absence_is_proof=True`
(candidate anchors in the pinned blob: `promisor_state` `:510`, `missing_reachable` `:555`,
`build_store` `:565`, the refusal raised at `:583-587`, cutoff call site `:362`).
No traceback, no `FETCH_HEAD`, canary unchanged, no new pack in all four rows.

Two earlier candidate blobs were also observed during the wave (`60e3b3a8…`, `906a1e18…`); the
first of them refused MFT-1 only because git's traversal failed, while the pinned blob refuses
**before** the traversal with an explicit required-object check. The candidate is a WIP that moves
during the wave, so the pinned copy `candidate-wip-5cf9c72a.py` is what this observation is bound
to; re-run the four rows against the integrated candidate.

## Grid rows for the integrator

`build/out/CaseMissingFleetTree/grid-row-fragment.py` gives paste-ready builders
(`f_missing_fleet_ancestor_tree`, `f_missing_fleet_ancestor_tree_unmarked`,
`c_complete_fleet_promisor`), the three CASES rows, the REASONS entries, and two proposals:

* **REASONS any-of.** A single substring cannot express "the refusal must name an unavailable
  object": two sound implementations word it differently (`unable to read tree (…)` from git vs
  `… are missing locally` from an explicit closure check). The fragment contains the 6-line patch
  that lets a REASONS value be a tuple of alternatives. Without it, pin only `could-not-evaluate`.
* **No-transport marker.** Return the fleet's `.git/FETCH_HEAD` path as the row's marker: the
  grid's existing `executed` flag then means "a transport was attempted", which is the assertion
  that matters for a promisor-backed row.

## Containment

* Every fixture object lives under `/fast/scratch/hyaku/kama-r24/CaseMissingFleetTree/`:
  `fixtures/<variant>/{lane,fleet,canary}`, plus the extracted frozen auditor
  `frozen-audit.py`. Nothing under `/tmp` was created by this lane (the builder contains no
  `tempfile`/`mkdtemp`/`/tmp` reference; grep-verified), and no heavy clone exists outside the
  scratch root.
* Repository writes by this lane are exactly: `.ufo/waves/round-24/build/out/CaseMissingFleetTree/`
  (8 files) and this advice file. No tracked file was edited, no commit, no push, no lane Git index
  write, no sibling or fleet repository touched. Only read-only git plumbing was run against the
  lane repository (`cat-file`, `log`, `diff`, `status`); `status` may refresh the index stat cache,
  but no tracked file changed.
* The fleet/lane repositories used by the auditor are the synthetic fixtures, never the real
  kama/fleet repositories.
* No network transport and no repository-configured program execution in any graded row.

## Residual risks and verification gaps

1. **How the refusal is produced differs between the two missing rows.** In the pinned candidate
   blob, MFT-1 is refused by an explicit required-object check (`build_store` refuses a
   promisor-backed repository whose reachable closure has holes, naming the missing object), while
   MFT-2 — the same hole in an *unmarked* repository — is refused only because git's own traversal
   fails (`rc=128 fatal: unable to read tree`), since the candidate checks the closure only for
   promisor-backed repositories ("a repository without promisor evidence is left exactly as round 23
   left it"). Both answers are exit 2 and both are sound, but they come from different mechanisms:
   a mutation that removes the explicit check would still pass MFT-2 and would be caught by MFT-1,
   while a mutation that removes only the fail-closed git error would be caught by MFT-2. Keeping
   both rows is what makes the pair discriminating.
2. **The candidate's closure check is root-wide.** The pinned blob refuses on *any* missing object
   reachable from the root, including objects the audit never reads. That is a deliberate,
   conservative policy; it is the over-refusal direction and belongs to the unneeded-object case,
   not to this one. Do not read this row as covering it.
3. **The candidate is a WIP**; the observation above is bound to auditor sha256 `5cf9c72a…`
   (three blobs were observed during the wave). Re-run the four rows against the integrated
   candidate.
4. **The refusal wording is deliberately not pinned** (see the REASONS any-of proposal). An
   implementation that refuses for the right reason with different words still passes.
5. **Not run here (out of lane bounds):** the full grid, the candidate selftest, the historical
   parity run, mutation sensitivity. Unrun = unverified.
6. **Git floor:** `--no-lazy-fetch` needs git ≥ 2.45; the host has 2.56.0, so the isolation flag is
   exercised, but an old-git floor is not re-verified in this lane.
7. **Fixture shape:** the missing object is produced by deleting a loose object from an otherwise
   complete local repository plus declared promisor metadata. That is exactly the "required object
   unavailable" state, but it is not a genuine `file://` partial clone; the genuine hydrated
   partial clone is a separate lane's case.

## Not claimed

* Nothing about the candidate's final wording, structure or its selftest.
* No claim that the audit is safe against arbitrary untrusted repositories.
* No new serving capability, no score claim, no closure of the inherited parser/alternates/
  gitfile/size-limit findings.

## Files written by this lane

* `.ufo/waves/round-24/build/advice/CaseMissingFleetTree.md` (this file)
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/expected.json` — pre-registered expectations
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/case_missing_fleet_tree.py` — builder, premise
  checks, measurements, runner
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/grid-row-fragment.py` — grid rows for the
  integrator
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/fixture.json` — oids and premise results
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/measurements.json`,
  `measurements-unsafe-probe.json` — git-behaviour measurements
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/audit.json` — frozen base results
* `.ufo/waves/round-24/build/out/CaseMissingFleetTree/audit-candidate-wip.json` — candidate WIP results
