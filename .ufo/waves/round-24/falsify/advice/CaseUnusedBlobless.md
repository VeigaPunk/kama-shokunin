# CaseUnusedBlobless — UnusedBlobless family (PG28-unhydrated-blobless-lane, PG36-unused-missing-blob-plain): the amended exit-0 expectation HOLDS

Seat: `KamaR23-2.CaseUnusedBlobless` (reviewer, leaf). Round 24 falsification stage, read-only production.
Pinned clone: `/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/repo`
(`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached at
**`2e254a1763a9c08aa07fc53081287f506c447d84`**, `git status --porcelain` empty before and after).
Auditor under observation: `tools/report-landing-audit.py`, sha256
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the contract's `ea51bc35…`).
Frozen arm auditor: `git cat-file blob 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`,
sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (matches
`oracle-snapshot-before-inspection.json` `frozen_auditor_sha256`).
Fixed expectation source: `tests/report-audit/promisor-grid-expectations.json`, sha256
`d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (matches the contract's `d86b7bea…`
and the hash the grid itself reports).
Grid population: `population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88`,
`population_size 47`. Host: git 2.56.0, Python 3.14.8. `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/tmp`
for every subprocess. No network, no transport, no execution payload, no production mutation.

## Verdict

**HOLDS** — both assigned rows meet the live *amended* expectation on the current arm (exit 0, no findings,
no findings' tokens, empty stderr, no objects acquired), the PG28↔PG36 twin documents are identical (verified
independently of the grid's own comparison), and the withdrawn original expectation for PG28 stays visible and
is **not** relabelled passed. The frozen arm reproduces the historical r23 metadata refusal for PG28 (exit 2,
`partial clone (promisor pack)`) — history, not a target. **No source defect** was found on any path this
family exercises. Three **fixture-level** observations (F1–F3 below) are reported separately from source
findings; none of them changes a verdict.

## Exact commands, exits and finding/token pairs

### 1. The assigned bounded selection (exact command, twice)

```
cd /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/repo
export TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/tmp
python3 tests/report-audit/promisor-grid.py --arm both --case PG28-unhydrated-blobless-lane \
        --case PG36-unused-missing-blob-plain --json
```
exit **0** (run 1), exit **0** (run 2, semantically identical rows), stderr **0 bytes**.
(An additional `--out <dir>` invocation of the same selection was used to write `population.json` /
`candidate.json` artifacts; it changes no behaviour.)

Grid-reported rows (current arm = the graded view):

| arm | case | kind | exit | amended | original | frozen | defects | kinds | tokens | stderr | objects acquired | twin_equal |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| current | PG28-unhydrated-blobless-lane | policy | **0** | met | **not met (withdrawn)** | – | `[]` | `[]` | none | empty | `true` |
| current | PG36-unused-missing-blob-plain | control | **0** | met | met | – | `[]` | `[]` | none | empty | `true` |
| frozen | PG28-unhydrated-blobless-lane | policy | **2** | **not met** | – | met | `null` (no document) | `null` | none | `could-not-evaluate: <lane>: partial clone (promisor pack)` | `{}` | `null` (no document) |
| frozen | PG36-unused-missing-blob-plain | control | **0** | met | – | met | `[]` | `[]` | none | empty | `{}` | `null` |

* `current` arm: `violations 0`, `violating_cases []`, `withdrawn_original_failures ["PG28-unhydrated-blobless-lane"]`,
  `twin_pairs_compared ["PG28-unhydrated-blobless-lane","PG36-unused-missing-blob-plain"]`, `twin_mismatch []`,
  `tracebacks 0`, `timeouts 0`, `harness_leaks 0`.
* `frozen` arm: `violations 0` (it is graded against its own frozen view), `amended_view_unmet ["PG28-unhydrated-blobless-lane"]`
  — i.e. the r23 base would not satisfy the amended live row, which is the historical baseline, not a defect.
* The **withdrawn** original row for PG28 (exit 2, `reason_class "unavailable"`) is still present in the fixed
  expectation file and is reported as withdrawn by the grid (`met_original False`). It is not counted as achieved.

### 2. Independent rebuild, premise assertions and sharpness probes (my own, outside the grid's grading)

```
python3 /fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/probe_unused_blobless.py
```
exit **0** — **44 checks, 0 failed** (full log: `out/CaseUnusedBlobless/probe.out`).
The probe rebuilds both fixtures from the pinned clone's own builders into my scratch root, re-derives every
premise with independent `git --no-lazy-fetch` plumbing, runs the current auditor itself, and compares the twin
documents by hand.

**PG28 premise (observed):**
* lane promisor facts: `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`,
  `pack-8a32dfc9….promisor` marker present → `promisor_backed True`
  (`extensions.partialclone` is *absent*: a `git clone --filter=blob:none` writes the `remote.*` keys, not that
  extension key — the fixture's promisor predicate is still satisfied, and the audit's own
  `promisor_facts`-equivalent reads the `remote.*` keys).
* lane missing exactly one object: `56d7b323865c731da81e0225cf109d66f0480919` (the `f` blob);
  opaque (tree/commit) hole set **empty** (`rev-list --objects --missing=print --filter=blob:none`).
* lane carries **no** `corpus/SOURCES.md` (`git ls-tree` empty) → the audit's registry read is "absent", the
  legacy shape, and no blob is ever needed; fleet complete and plain.
* the clone's `remote.origin.url` = `file://…/probe/pg28/lane-origin`, that directory **exists** and **holds the
  missing blob** → a lazy fetch would have succeeded, so the `--no-lazy-fetch` isolation is load-bearing here,
  not vacuous (same hazard peer `KamaR23-2.CaseFleetBlobless` reports for the fleet lane; every probe of mine
  used `git --no-lazy-fetch`).
* auditor run: exit 0, stderr empty, document `status clean`, `summary.defects 0`, `by_kind` all zero,
  `results[0].required 1`, `round_commits 1`, `cutoff 2000`.
* object acquisition: independent `cat-file --batch-all-objects` inventory diff before/after →
  `lane []`, `fleet []` (the grid independently reports `objects_acquired {}` on every row of both arms).

**PG36 premise (observed):**
* lane carries **no** promisor metadata; exactly one missing object
  `b2c475fedd466685003f05a02c7bd772186c0429`, matched against `git ls-tree refs/heads/master -- notes/unused.txt`
  → it *is* the `notes/unused.txt` blob; opaque hole set **empty**; fleet complete.
* auditor run: exit 0, stderr empty, finding kinds `[]`; no objects acquired.

**Actual twin document comparison (mine, not the grid's):** the two verdict documents, with the fixture paths
replaced by `<lane>`/`<fleet>` (the same normalisation the grid uses), are **identical**
(`json.loads(...) == json.loads(...)` → `true`), including `summary.by_kind` all-zero and `results[0].required 1`.

**Sharpness probes — the boundary the family claims (all offline, local, no payload):**

| probe | fixture | observed |
|---|---|---|
| S1 | PG28 shape + the **missing blob cited** by the report | exit **2**; `could-not-evaluate: round 1: unknown: unavailable required object: 56d7b323865c731da81e0225cf109d66f0480919 is referenced by the history of <lane> but the repository cannot serve it`; names the OID; not the metadata refusal; **no verdict document** |
| S2 | PG36 shape + the **missing blob cited** (report amended inside the fixture fleet) | exit **2**; `…unavailable required object: b2c475fedd466685003f05a02c7bd772186c0429 is referenced by the history of <lane> but the repository cannot serve it`; no verdict document |
| S3 | blobless lane that **does** carry `corpus/SOURCES.md` (registry blob unavailable) | exit **2**; `…unavailable required object: master:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300) in <lane>: git cat-file blob …: fatal: bad file`; no verdict document |

Consequence: PG28/PG36's exit 0 is **not** a blanket "blobless ⇒ ignore holes" rule. The source refuses exactly
where the hole is *used* (S1, S2) or *required* (S3), and does not refuse where the hole is genuinely unrelated
(PG28, PG36).

### 3. Static source check (the paths these rows exercise)

* `tools/report-landing-audit.py:136-139` — `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)`;
  the single wrapper at `:161-163` prepends it to **every** git call, so no lane/fleet git invocation can
  materialise a missing blob.
* `:365-386` `load_source_urls` — `ls-tree` empty ⇒ `source_urls = None` (legacy lane, PG28 shape);
  a *present but unreadable* registry ⇒ `required_read` ⇒ exit 2 (probe S3 confirms the distinction is enforced,
  not assumed).
* `:188-267` `lookup` — the cited lane commit resolves `found` in the blobless clone (commit object present),
  so the store-wide missing walk is never reached for these rows.
* `:419-447` `refuse_unknown` and `:689-717` `unknown_citation`/`opaque_hole` — the only callers of
  `RepoStore.missing()` (`:698`, `:714`) are reached from the *unresolved-citation* path (`:436`, `:442`) and the
  errata path (`:571`, `:577`). For PG28/PG36 no citation is unresolved, so the store-wide
  `rev-list --objects --missing=print` diagnosis never runs and an unrelated missing blob can never become a
  precondition. This is exactly the amended policy's "unrelated hole does not block", implemented as a
  *path-dependent* rule rather than a blanket refusal.
* No blanket metadata/unknown/full-closure refusal on the current arm: `reason_class` is `null` on both rows and
  no refusal text is emitted (stderr empty on both).

## Source flaws

**None found.** No source defect was observed in the audited path for this family, and no minimal correction is
proposed. The three registered boundaries that the family depends on are all implemented as claimed:
`actual required unavailable ⇒ CNE2` (S3, and the audit's own `required_read`), `known wrong type ⇒ failed1`
(not exercised by these two rows; untouched by me), `unrelated blob hole does not block` (PG28, PG36).

## Fixture flaws (reported separately; none changes a verdict)

* **F1 (low, observational) — PG28's declared twin is not a marked/unmarked pair of the same content.** PG28's
  lane is a real blobless clone with **no** `corpus/SOURCES.md` whose missing object is the `f` blob; PG36's lane
  is a plain repository **with** `corpus/SOURCES.md` whose missing object is `notes/unused.txt`. The population
  contains no plain twin of PG28's own shape (a plain lane without a registry whose `f` blob is missing), so no
  row isolates "promisor metadata alone" for PG28's exact content; the marked/unmarked pair for PG36's shape is
  PG35 (outside my selection). The *verdict* equality is nonetheless real and independently verified above;
  the twin *label* overstates the isolation, nothing more.
* **F2 (low) — PG28's premise "every missing blob is one the audit never reads" holds only because the lane has
  no registry at all.** The sibling shape (blobless lane that *does* carry a registry) is outside PG28; it is
  covered elsewhere in the population (PG13 lane / PG43 fleet report) and by my probe S3 in my own scratch. No
  expectation cell needs to change; the manifest may simply note the dependency.
* **F3 (observational) — the frozen arm performs no twin comparison.** In the frozen arm PG28 refuses, so its
  verdict document is `null` and `twins`/`twin_equal` are `null`, `twin_compared 0`, while
  `twin_pairs_in_manifest 1` still reports. Honest (no false equality is asserted), but a reader must not read
  `twin_pairs_in_manifest` as evidence of a comparison in that arm.

No expected cell was changed, no fixture was made to fit the candidate, and no manifest row was edited.

## Observed vs inferred

**Observed (commands, exits, stderr, JSON documents, object inventories, missing-id sets, promisor facts,
sha256 digests):** every exit code and stderr string quoted above; the grid's own `met_amended` / `met_original` /
`withdrawn_original_failures` / `twin_*` / `objects_acquired` fields; my 44 probe checks; the three sharpness
probes S1–S3; the byte-equality of the 44 shared expectation rows against
`.ufo/waves/round-24/oracle-snapshot-before-inspection.json` and the identity of the 3 extra rows as the
supplement-2 opaque cells `PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`,
`PG48-opaque-unused-tree-no-unresolved-token` (independent additions, not a rewritten original expectation);
`population_size 47` = original 44 + 3.

**Inferred:** that exit 0 with no findings is the *correct* verdict under the amended policy — this rests on the
amendment's own wording ("an incomplete but locally sufficient repository is not refused merely because an
unrelated historical blob, branch, or unused file is missing") plus probes S1–S3, which show the boundary is
enforced where it must be. The oracle's amended view remains the authority; I did not re-derive the policy.

**Unverified / out of scope:** the other 45 grid rows and every other falsification seat; the mutation probes
(including the PM08 no-lazy-fetch deletion, which is static-only and was **not** executed); the Git ≥ 2.45 floor
on an older Git (this host has 2.56.0 only; the inherited L0 prerequisite stays open); live serving capability;
any claim about remote repository completeness or remote abbreviation uniqueness; anything in production
(`production/`, `.jj/index`, fleet, routing, services, operator config, real object stores) — all read-only
here.

## Files written

* `.ufo/waves/round-24/falsify/advice/CaseUnusedBlobless.md` (this report)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/grid-exact.json` (exact-command output, exit 0)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/grid-exact-repeat.json` (second run, exit 0)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/grid-exact.err` (empty)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/probe_unused_blobless.py` (independent probe, 44 checks)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/probe.out`, `probe.err` (probe log / empty stderr)
* `.ufo/waves/round-24/falsify/out/CaseUnusedBlobless/population.json`, `candidate.json` (grid `--out` artifacts)
* scratch, outside the lane tree: `/fast/scratch/hyaku/kama-r24/falsify/CaseUnusedBlobless/{repo,probe,tmp}`

Nothing else was created or modified: no production file, no expectation cell, no manifest row, no service,
no configuration, no object store. No external source was read (no URL, no S-row added; the source-ledger
supplement at this pinned revision stays as filed, S105 included).

## Installs

None. No pacman transaction, no system upgrade, no service or configuration mutation, no network access, no
model override. Only tools already present were used: git 2.56.0, Python 3.14.8.

Report: .ufo/waves/round-24/falsify/advice/CaseUnusedBlobless.md
