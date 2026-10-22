# ConnReceipts — round-24 receipts, oracle chronology, hash and fixture audit

Lane: `KamaR23-2.ConnReceipts` (connector, leaf — no subagents dispatched).
Scope: wave1 (build) and falsify-wave assignment/dispatch receipts; oracle commit
chronology; final source hash receipts; fixture corrections; wave-64 identity
freshness; L1 planner mapping and role counts.
Mode: **read-only production**; scratch clone only, no builds, no suites, no execution.
Pinned revision audited: `2e254a1763a9c08aa07fc53081287f506c447d84`.
Base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.

Scratch (contract): `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin
/fast/scratch/hyaku/kama-r24/falsify/ConnReceipts` then `git checkout --detach
2e254a1763a9c08aa07fc53081287f506c447d84` → `git rev-parse HEAD` =
`2e254a1763a9c08aa07fc53081287f506c447d84`, `git status --porcelain` empty. Exit 0.
No installs were needed (no tool installed or updated by this lane).

Verdict summary: **HOLDS** on chronology, hash receipts, fixture corrections, seat
counts/roles and identity freshness. **FALSIFIED (1 receipt)** — the
`payload-versions.json` "actual" block claims a spawn that never happened.
**PARTIAL (1 receipt)** — `assignments.json` still holds the map its own recorder
rejected. **OBSERVATION (1)** — a message-less twin commit of the pinned tree.

---

## A. Axes named (godspeed)

1. **Chronology integrity** — oracle expectations must predate the candidate; no retro-fit.
2. **Receipt truthfulness** — every dispatch/assignment receipt must name what actually ran.
3. **Hash identity** — the four pinned artifact hashes must reproduce at the pinned revision.
4. **Fixture immutability** — original44 unchanged, exactly 3 independent opaque cells added.
5. **Seat/identity provenance** — 64 fresh identities, L1 planner mapping 1:1, role counts stable.
6. **No-harm on the corpus** — ledger rows, S095 rejection record, filed r23 corrections intact.

---

## B. Commands run (all exit 0)

```
git -C kama-shokunin rev-parse HEAD                                     # 2e254a1763a9c08aa07fc53081287f506c447d84
git -C kama-shokunin log --format='%H %P %cI %s' -8                     # lineage below
git -C kama-shokunin log --format='%h %cI %s' -- <each oracle file>     # per-file landing commit
git -C kama-shokunin merge-base --is-ancestor <r> 2e254a17              # 7/7 true
git -C kama-shokunin cat-file -p 2e254a17:<path> | sha256sum            # 6 artifacts
git -C kama-shokunin cat-file -p 0df800e8:tools/report-landing-audit.py | sha256sum
python3 (json diff) snapshot-vs-manifest, spec-vs-registry-vs-assignments-vs-spawn
git -C kama-shokunin clone --no-hardlinks … && git checkout --detach 2e254a17…   # scratch
```

---

## C. HOLDS

### C1. Oracle commit chronology is clean and strictly pre-candidate (OBSERVED)

| rev | local time | role |
|---|---|---|
| `0df800e8` | 14:20 | r23 base (frozen auditor) |
| `d1b9d956` | 14:53 | `preregistration.json` |
| `123640b` | 15:04 | `oracle-amendment-1.json` |
| `f66b226` | 15:12 | `oracle-snapshot-before-inspection.json` (44 cases) |
| `aacbd52` | 15:14 | `oracle-supplement-2.json` (3 opaque cells) |
| `ed1cc3a` | 15:44 | **candidate** source commit (`tools/`, `tests/`) |
| `f1e755e0` | 16:39 | source-ledger reconciliation + scorecard |
| `2e254a17` | 16:45 | pinned (64-seat build evidence) |

Every oracle artifact commit is an ancestor of the pinned revision
(`merge-base --is-ancestor` → true for `d1b9d956`, `123640b`, `f66b226`, `aacbd52`,
`ed1cc3a`, `f1e755e0`, `0df800e8`). The four oracle files each landed in their own
commit before the candidate and were not modified afterwards (working tree clean;
only untracked `.ufo/waves/round-24/falsify/`). **No oracle retro-fit after the
candidate is observable in the history.** The withdrawn expectation remains
withdrawn: `oracle-amendment-1.json` is an ancestor of the candidate, so it was
appended before inspection, exactly as claimed.

### C2. fixed47 = original44 unchanged + 3 independent opaque cells (OBSERVED)

Deep JSON compare of the pre-candidate snapshot (`f66b226`, 44 cases) against the
shipped manifest at `2e254a17` (`tests/report-audit/promisor-grid-expectations.json`, 47 cases):

- changed cells among the 44: **0** (field-by-field, whole-record equality)
- removed cells: **0**; added cells: **3** —
  `PG46-opaque-tree-hides-cited-blob`, `PG47-opaque-tree-with-unresolved-fabricated-token`,
  `PG48-opaque-unused-tree-no-unresolved-token`
- the three match `oracle-supplement-2.json` rows exactly (exit 2 / 2 / 0;
  `reason_class` unavailable / unavailable / null; PG48 is the clean-twin exit-0 cell)
- the three builders (`c_opaque_tree_hides_cited_blob`, `c_opaque_tree_fabricated_token`,
  `c_opaque_unused_tree_clean`) exist in the shipped runner and are auto-registered in
  `BUILDERS`; the runner's selftest asserts `builders-present` for every manifest case

So the L1's "fixed47 = original44 unchanged + 3 independentopaque cells" claim is
structurally true in the shipped bytes. (Fixture *semantics* are another lane's scope.)

### C3. Final source hash receipts reproduce exactly at the pinned revision (OBSERVED)

`git cat-file -p 2e254a17:<path> | sha256sum`:

| artifact | sha256 | bytes | pin in wave contract |
|---|---|---|---|
| `tools/report-landing-audit.py` | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | 64727 | `ea51bc35…` ✓ |
| `tests/report-audit/promisor-grid.py` | `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` | 46583 | `b034e159…` ✓ |
| `tests/report-audit/promisor-grid-expectations.json` | `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` | 45580 | `d86b7bea…` ✓ |
| `tests/report-audit/promisor-mutants.py` | `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` | 44513 | `6e0b9d62…` ✓ |

No drift: the same four 8-hex prefixes at `ed1cc3a`, `f1e755e0` and `2e254a17`.
The r23 frozen pin also reproduces: `0df800e8:tools/report-landing-audit.py` =
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`, equal to
`derived_from.frozen_auditor_sha256` in the snapshot. `S105.json`'s recorded snapshot
digest `54d4532c…` equals the sha256 of the committed reader bytes (257625 B).

### C4. Corpus/ledger receipts intact (OBSERVED)

Distinct `S###` ids in `corpus/SOURCES.md`: 101 at `d1b9d95` (matches the
`sources-before.json` census "rows 101", source blob unchanged) → 105 at `f1e755e0`
→ 105 at `2e254a17`. `S105` is filed with the explicit rejected-S095 rationale and the
original S095 teaches cell remains filed (3 S095-referencing lines, incl. the S105 row).
Filed r23 corrections are present as text at `LOG.md:1417-1420` ("69 durable lane
reports, not 68 …; 40 of the 56 killed FIFO-process identities were retained").

### C5. Falsify-wave seats: 64, roles stable, L1 planner mapping 1:1 (OBSERVED)

- `spec-pinned-2e254a17.json` items: 64, names unique.
- role counts in the spec: reviewer 45, mutation-tester 6, scout 3, critic 6,
  connector 4 (= 64) — identical in the dispatch registry (64 members, **0** role
  mismatches), in the on-disk `advice/swarm-registry.json` (64 members, 64 unique
  agentIds, same role distribution) and in `spawn-result.json`
  `details.progress` (64 entries, 64 unique ids, same role distribution).
- `assignments.json` values ≡ `details.progress` ids (set equality, both directions).
- `dispatch-attempts.json`: exactly one attempt, `2026-10-21T19:46:01.903515+00:00`,
  `spawned: 64`, `error: null`; `spawn-result.json` carries the same utc.

### C6. Wave-64 identities are new, not dead-seat replacements (OBSERVED)

Falsify ids ∩ build ids = ∅ (both the seat-name sets and the agent-id sets);
falsify ids 64/64 unique; build ids 64/64 unique. No falsify seat re-uses a build
seat identity. The build wave's first dispatch attempt spawned **0** (`error:
"Background job limit reached (100)"`, 17:50:07Z) and therefore left no partial or
dead seats; the retry at 17:53:07Z spawned 64.

### C7. Wave1 (build) receipt chain is internally consistent (OBSERVED)

`build/spec.json` 64 items → `build/assignments.json` keys ≡ spec names →
`build/advice/swarm-registry.json` keys ≡ spec names with **0** role mismatches →
`assignments.json` values ≡ registry agentIds ≡ the 64 ids in `build/spawn-result.json`.
Build role counts: executor 3, reviewer 29, scout 8, critic 8, connector 5, scribe 7,
sentinel 1, mutation-tester 1, simplifier 1, revenger 1.

### C8. Draft payload corrections are contained and documented (OBSERVED)

`spec.json` (draft, `ed1cc3a` pin) differs from the pinned specs in exactly two
prompts — `SrcFsckReject` (+380 chars: reopen S105, explicit REJECTED
subprocess/TextIOWrapper inference check) and `ConnSources` (+122 chars: S102→S105
consumer scan, used-by old→new table) — plus the shared context. The two pinned specs
(`f1e755e0`, `2e254a17`) have **0** prompt differences; only the context differs, and
only in the pinned commit hash. Drafts spawned 0 seats.

---

## D. FALSIFIED / PARTIAL receipts (report-only; no production edit)

### F1 — FALSIFIED: `payload-versions.json` "actual" names a spawn that never happened

Claim in `.ufo/waves/round-24/falsify/payload-versions.json`:

```json
"actual": {"spec": "spec-pinned-f1e755e0.json", "dispatch": "dispatch-pinned-f1e755e0.json",
           "revision": "f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d", "seats": 64,
           "role_counts": {"reviewer":45,"mutation-tester":6,"scout":3,"critic":6,"connector":4}}
```

Contradicted by four independent receipts:

1. `payload-selection.json` lists `spec-pinned-f1e755e0.json` under
   `unspawned_drafts` with `spawned: 0`, and records
   `consumed_spec/dispatch = spec-pinned-2e254a17.json / dispatch-pinned-2e254a17.json`,
   `revision: 2e254a17…`, `seats: 64`.
2. `dispatch-attempts.json` holds **exactly one** attempt (19:46:01.903515Z,
   `spawned: 64`); there is **no** attempt at the `f1e755e0` pin time (19:39Z), and
   `payload-versions.json` itself is stamped 16:39 local — i.e. it was written
   *before* any spawn of this wave.
3. `spawn-result.json` utc equals that single attempt.
4. The contract actually delivered to all 64 seats (including this lane) is the
   `taskCall.context` of `dispatch-pinned-2e254a17.json`: it contains
   `2e254a1763a9c08aa07fc53081287f506c447d84` and **not** `f1e755e0…`, while
   `dispatch-pinned-f1e755e0.json` contains the opposite. Distinctive phrases from
   the delivered contract ("fixed47 expectations are original44 unchanged +3
   independentopaque cells", "Report: trailer is relative to …") are present in both
   pinned contexts, so the commit hash is the only discriminator — and it resolves
   to `2e254a17`.

Verdict: **the falsify wave ran on the `2e254a17` payload**; the `actual` block is a
stale pre-launch plan mislabeled as an actual. `payload-selection.json`'s note
("actual field was intended payload metadata before launch, not a spawn receipt")
acknowledges the tension, but the file still stores `seats: 64` under a key literally
named `actual` and names a revision that was never spawned. Its `role_counts` are
correct for the wave that ran (they match C5 exactly).

Minimal correction (L1-owned; **not applied** — production is read-only for this lane):
rename the block `actual` → `planned`, or set `seats_spawned: 0` and add
`consumed_revision: 2e254a1763a9c08aa07fc53081287f506c447d84`; the role counts may
stay as they are.

### F2 — PARTIAL: `assignments.json` keeps the map its own recorder rejected

`.ufo/waves/round-24/falsify/assignment-recording.json` records
`first_record_error: "unknown_member: SrcRevList-3 is not a validated member name"`,
`raw_map: assignments.json`, `corrected_map: assignments-recorded.json`, and the rule
that the runtime `-N` disambiguation suffix belongs to the id, not to the registry key.

- `assignments-recorded.json` (corrected): keys are the validated spec item names
  (`CritNoTrade`, `SrcRevList`); ids `KamaR23-2.CritNoTrade-3`, `KamaR23-2.SrcRevList-3`;
  identical id values to `assignments.json`.
- `assignments.json` (raw, still under the canonical filename): keys
  `CritNoTrade-3`, `SrcRevList-3` — keys the registry rejects.
- `advice/swarm-registry.json` is consistent with the **corrected** map
  (`CritNoTrade` → `KamaR23-2.CritNoTrade-3`).

So the correction happened and is documented, but a consumer that reads
`assignments.json` (the canonical name, and the one the assignment contract points
at) gets a map the recorder itself rejected. The two renamed ids are explained by the
build wave having already taken `KamaR23-2.CritNoTrade-2` / `KamaR23-2.SrcRevList-2`
— i.e. the runtime suffix avoided a live collision, it did not reuse a dead seat.

Minimal correction (L1-owned; **not applied**): make `assignments.json` the corrected
map, or add `{"superseded_by": "assignments-recorded.json"}` inside it.

### F3 — OBSERVATION (no action): message-less twin of the pinned commit

`1d3420c30122249d62bf7752d84bfde0748adf53` has an empty commit message and the
**identical tree** as the pinned commit
(`git rev-parse 1d3420c^{tree}` = `git rev-parse 2e254a17^{tree}` =
`90d19f20e02caf0c7a52e152f020e98e3c416af3`); it survives only as
`refs/jj/keep/1d3420c…`. No content divergence, so no hash or receipt claim is
affected. Recorded for awareness only — this lane does not touch `.jj` refs.

---

## E. Secondary observation: identity strings carry no wave discriminator

Both round-24 waves use the same lagging prefix `KamaR23-2.` (round-23's waves used
`CloseKama22.`). Uniqueness currently holds only because the build wave took the
`-2` suffix and the falsify wave took unsuffixed / `-3` ids, and the two waves use
disjoint seat names. A future re-run of either wave would need fresh suffixes, and no
id string alone says which wave it belongs to. Not a defect in this wave's receipts
(no collision exists); recorded so the L1 does not treat id uniqueness as a
cross-wave guarantee.

---

## F. Unverified items (not claimed)

- No grid, selftest or mutation-probe run was performed (out of lane; suite reruns
  prohibited). All statements about the 47 cells are *structural* (file content), not
  behavioural.
- Fixture *semantics* of PG46–PG48 (do they really produce exit 2/2/0) were not
  measured here; only their wiring into the shipped runner was checked statically.
- Whether all 64 falsify advice reports land durably is L1-owned.
- The r23 filed figures "69 durable lane reports" and "40 of 56 killed FIFO-process
  identities" were not re-derived from r23 lane files (out of lane); only the filed
  correction text at `LOG.md:1417-1420` was read.
- `refs/jj/*` internals were listed but not modified; the lane `.jj/index` was not touched.

---

## G. Files written by this lane

- `.ufo/waves/round-24/falsify/advice/ConnReceipts.md` (this report)
- `.ufo/waves/round-24/falsify/out/ConnReceipts/receipts-audit.json` (machine-readable receipt:
  commands, hashes, chronology table, contradictions F1–F3 with minimal corrections)

No production file, lane index, fleet, routing, service or object store was modified.

## H. Addendum (append-only) — blobless-fixture premise hazard

Source: peer report from `KamaR23-2.CaseFleetBlobless` (PG43 fleet-unhydrated-blobless
lane). Statically corroborated here against the shipped bytes at `2e254a17`; no source
defect claimed, nothing edited.

**Hazard (observed by peer, static corroboration here).** The blobless clone built by
`tests/report-audit/promisor-grid.py` keeps `remote.origin.url` pointing at the
**reachable** local `file://` origin, so any probe *without* `--no-lazy-fetch` lazily
fetches and materialises the missing blob; the premise then evaporates and the auditor
can return a false "clean" exit 0 instead of the correct exit 2. Peer A/B: blob absent
→ exit 2 (content-derived refusal); blob materialised by one stray
`git cat-file -e HEAD:<path>` → exit 0 "clean".

Static corroboration in the shipped tree:

- `tests/report-audit/promisor-grid.py:214-224` — `blobless_clone()` clones from
  `file://{origin}` and leaves the clone's promisor remote pointing at that reachable
  local origin.
- `tests/report-audit/promisor-grid.py:196-201` — `mark_config()` instead sets
  `remote.origin.url` to `<tmp>/absent-remote.git` (unreachable), so the
  promisor-marked *non-blobless* family cannot materialise a missing object even under
  a stray probe. The blobless family has no equivalent guard.
- Runner helpers are safe: `git_nofetch` (:109-111), `missing_objects` (:294-298),
  `object_exists` (:301-307, also `--no-replace-objects`), `object_inventory` (:309-313)
  all pass `--no-lazy-fetch`.
- Candidate auditor is safe: `tools/report-landing-audit.py:138-141` defines
  `GIT_ISOLATION` with `--no-lazy-fetch`, and every git call funnels through the single
  helper at :162.

**Affected cells (static, from the shipped manifest).** The four blobless cells:
`PG05-hydrated-blobless-lane`, `PG06-hydrated-blobless-fleet`,
`PG28-unhydrated-blobless-lane`, `PG43-fleet-unhydrated-blobless-report-required`.
Note the amended view of PG28 expects exit 0 (a locally sufficient unhydrated blobless
lane must not be refused) and PG43's original view expects exit 2 (required report
missing) — i.e. for PG43 a materialised blob converts a required-object refusal into a
false clean exit 0, which is exactly the failure mode the peer reproduced.

**Blast radius.** None of the graded path: no expectation drift, no manifest change, no
hash change, no change to the 44+3 structure. The hazard is confined to manual
inspection of a retained (`--keep`ed) blobless fixture, or to a future probe path that
forgets `--no-lazy-fetch`.

**Minimal correction (L1-owned; NOT applied — this lane is read-only on production).**
In `blobless_clone()`, after the clone succeeds, re-point the clone's promisor remote at
an unreachable path, mirroring `mark_config()`, e.g.
`git(dest, "remote", "set-url", "origin", str(Path(tmp, "absent-remote.git")))`.
`hydrate()` copies object files offline (shutil), so the hydrated cells PG05/PG06 are
unaffected; `extensions.partialclone=origin` and `remote.origin.promisor=true` remain,
so the blobless structure is preserved while the missing-blob premise becomes
non-evaporable.

**Operational note.** Any manual inspection of a retained blobless fixture must use
`git --no-lazy-fetch …` (or the auditor's `GIT_ISOLATION`) for every probe.

## I. Addendum (append-only) — H1 correction converged with the case lane; validation anchor

Peer `KamaR23-2.CaseFleetBlobless` confirmed convergence: the minimal correction
recorded in H1 (re-point the clone's promisor remote at an unreachable path after
`blobless_clone()`, mirroring `mark_config()`) is identical to that lane's own F1
finding, and its affected-cell list (PG05, PG06, PG28, PG43) matches its A3 note that
the fix must be validated **family-wide**, not per cell. Its A5 measurement of the A/B
(blob `PRESENT_NOW`, holes 2 → 1, objects 7 → 8, a second promisor pack
`pack-9ea1ce01…` against the clean arm's single pack with 7 objects and both holes)
establishes that the two arms are provably distinct stores, i.e. the observed
exit-2 → exit-0 swing is premise-dependence, not auditor nondeterminism. Nothing was
edited by either lane.

Static anchor now available for the L1's validation of the fix (observed in the shipped
runner at `2e254a17`): `tests/report-audit/promisor-grid.py:808-810` and `:822-826`
already implement a **no-acquisition pin** — the grid computes the object-set delta
around the auditor run and raises the problem "the audit acquired objects: …" if any
object appeared. Consequences for the fix:

- the grid's own pin makes *auditor-side* acquisition observable, so the unreachable-URL
  correction can be validated by the existing no-acquisition check rather than by a new
  probe;
- the case lane's stronger variant — a live *bait* origin that really holds the missing
  object — turns a stray acquisition into a visible pin violation instead of a silent
  success, which is the sharper fixture for the same family-wide requirement;
- validation scope must cover all four blobless cells (PG05, PG06, PG28, PG43), because
  the shared builder path is what the correction changes, and the hydrated pair must
  stay intact (`hydrate()` copies object files offline).

No production edit, no lane index, fleet, routing or service change.

---

Report: .ufo/waves/round-24/falsify/advice/ConnReceipts.md
