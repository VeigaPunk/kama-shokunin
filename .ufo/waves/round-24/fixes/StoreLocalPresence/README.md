# StoreLocalPresence — root-cause fix for the store-local presence inference

Seat: `KamaR23-2.AuditRepair-2` (leaf). Pinned base: lane revision `2e254a1` ("round-24: land
completed 64-seat build evidence …"), i.e. the production candidate the 64 falsifiers read
(`tools/report-landing-audit.py` sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`).

**No production write was made** (the lane file is untouched while the falsifiers read `2e`); this
fix lives only in a new scratch clone and in this directory. The earlier build artifacts
(`build/out/AuditRepair/`, `build/advice/AuditRepair.md`) were **not** overwritten.

Artifacts:

- `report-landing-audit.py` — the **ca162c9c producer version**, sha256
  `ca162c9cdd5884f0f3ef33a05b999c401ab60c633e47962f424c8c4e5db86235` (1443 lines).
  It carries **both** lookup fixes: the store-local presence inference *and* the
  per-canonical-object reconciliation of `unknown` against a known `wrongtype`
  (the two sections below describe them; the sections were written in that order,
  the second fix is already in this file).
- `report-landing-audit.patch` — unified diff of that version against the pinned `2e254a1`
  (+122/−11, one tracked file)
- scratch clone: `/fast/scratch/hyaku/kama-r24/StoreLocalPresence` (checked out at `2e254a1`)

## The defect (confirmed, not re-run as a falsifier)

`lookup()` inferred "this store holds the object" from the **global** bare answer — the merge of
every audited store — while classifying a token per store. A blob that lives in the fleet only was
therefore "present" in the lane, and the lane's `^{}` probe (which cannot see it) turned that into
`unknown` (an unreadable object) instead of `absent` there.

Measured on the pinned `2e` with a blob written only into the fleet and cited in
`## Landed changes`:

| order | `lookup(stores, [blob], "^{commit}")` | audit |
|---|---|---|
| `(lane, fleet)` | `unknown` | exit 2 `unknown: unavailable required object: 28d34a63… is present but its content cannot be served` |
| `(fleet, lane)` | `wrongtype` | — |

So the pinned candidate refuses a citation that is a *known* local blob (exit 2) where the
original contract wants the proved mismatch `landed-unresolved` (exit 1) — a false refusal caused
by cross-store state, exactly the class of harm this repair is about.

## The fix (minimal, root cause only)

`tools/report-landing-audit.py:211-229` — the presence that drives the per-store classification is
now **this store's own** bare answer (`here = lookup((store,), tokens)`), never the merge of all
stores:

```python
    for store in stores:
        # what THIS store holds under the bare name: the presence must be
        # the store's own, never the merge of every store, or an object
        # that lives in one repository would make it look present (and
        # unreadable) in the other
        here = lookup((store,), tokens) if peel else None
        ...
            if line.endswith(" missing"):
                if (here is not None and here[token] == "found"
                        and status[token] != "found"):
                    unresolved.append(token)
                continue
```

Nothing else changed: no reverse-order workaround, no metadata classifier, no completeness gate,
no change to the ambiguity rule, no weakening of the unreadable-tag case.

Notes on the two details the review asked to check:

- **Merge priority (wrongtype vs unknown).** The two states can never come from different stores
  for the same token: an object id fixes the object, so a token that is a tag in one store is the
  same tag in the other. The only way to see both is a short prefix token, and then the bare answer
  is `ambiguous` (rank 3), which keeps the round-23 ambiguity behaviour. The `unknown` >
  `wrongtype` precedence therefore only decides a case that cannot arise across stores.
- **Genuine unreadable tag.** A tag that is present in a store and whose target the store cannot
  serve: the store's own bare answer is `found`, the peel fails, the `^{}` probe in that store
  answers `missing` → `unknown` → exit 2. Not weakened: the selftest case
  `known-tag-with-unavailable-target-is-unknown` still passes.

## Bounded regression evidence (offline, local, no network)

New selftest cases (both in the file's own selftest, on the pinned fixture):

- `fleet-only-blob-citation-is-a-failed-finding` — a blob written only into the fleet and cited in
  `## Landed changes` → exit 1 with `landed-unresolved` for that blob (not exit 2).
- `lane-only-blob-citation-is-a-failed-finding` — the mirrored case (the blob only in the lane) →
  exit 1 with `landed-unresolved`.

Measured on the fixed candidate:

- `python3 tools/report-landing-audit.py --selftest` → **64 cases, 0 failed** (62 before this fix,
  plus the two new store-local presence cases).
- direct `lookup()` probe, both store orders: fleet-only blob → `wrongtype`, lane-only blob →
  `wrongtype`, a commit in the lane → `found` — order-independent (the pinned code gave
  `unknown` / `wrongtype` for the first two).
- the audit of a draft citing either blob → exit 1 with `landed-unresolved` (the pinned code gave
  exit 2).
- historical ledger parity: `--lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --fleet-repo
  /home/vgpnk/Projects/shokunin --rounds 10- --json` → exit 0 and the `--json` document
  **byte-identical** to the round-23 base output (`cmp` clean).

No full suite was run (the reviewer's instruction); no installs, no network, no pacman
transaction, no commits or pushes; fleet, sibling and operator state untouched.


## Second defect (same fix, per-canonical-object reconciliation)

Review hypothesis confirmed by measurement, not assumed: a **tag object present in both audited
repositories**, whose target is a blob that only one of them can serve.

- The lane holds the tag, not the target blob → the lane's `T^{}` probe answers `missing` →
  `unknown` there.
- The fleet holds the tag *and* the target blob → the fleet's `T^{}` resolves to the blob →
  conclusive `wrongtype` there.
- Before this fix the aggregate was `unknown` (exit 2), because `unknown` outranked `wrongtype`
  in the merge: the unknown must not outrank a **known** wrongtype for the **same canonical bare
  object**. No hash collision is needed: the tag has one object id, the same in both stores.

The fix (candidate `:213-305`): each store now reports the **canonical object id** it holds for a
token (new helper `bare_objects()`, `:184`), and the per-store peel outcomes are collected as
`token -> {object id: {states}}`. The reconciliation is per canonical object: a store that proves
the object is a known non-commit has proved the mismatch, so another store's inability to serve
that object does not make the citation unknown. Objects behind one *abbreviated* name are **not**
reconciled (different canonical ids): there the uncertainty stands, so no blind rank flip was
introduced.

Measured (same fixture, both store orders, target blob in the fleet only / in the lane only / in
neither):

| target blob | `lookup(T)` (both orders) | audit |
|---|---|---|
| in the fleet only | `wrongtype` | exit 1, `landed-unresolved` for the tag |
| in the lane only | `wrongtype` | exit 1, `landed-unresolved` for the tag |
| in neither | `unknown` | exit 2, `unknown: unavailable required object: <tag> is present but its content cannot be served` |

The genuine unreadable tag is therefore still refused when its target is unavailable **everywhere**
(CNE 2), and a tag that lives in only one audited repository is still not resolved by
cross-store graph reasoning (the existing case `known-tag-with-unavailable-target-is-unknown`
passes).

New selftest regressions: `same-tag-in-both-stores-is-a-known-mismatch` and
`tag-target-missing-everywhere-is-unknown`. `--selftest` → **66 cases, 0 failed** (64 before this
second fix); the historical ledger `--rounds 10-` stays exit 0 with a `--json` document
byte-identical to the round-23 base output.


## Third proposal (v2): the selected-round errata scope and the committed-ledger read

Two reported consumer defects of the ledger helper, fixed in the root dataflow (not in the
fixture). **The ca162 version above is kept as filed**; this proposal is a versioned subfile:

- `report-landing-audit-v2.py` — sha256
  `aa289cc79bfabf9f54299db2659349b308f6c37687bac2a213b7efb1fdc4179d` (1458 lines)
- `report-landing-audit-v2.patch` — unified diff against the pinned `2e254a1` (the integration base)
- `report-landing-audit-v2-vs-ca162.patch` — the delta of this proposal alone

### 1. CodeErrataBoundary F1 — a row of an unselected round could fail a clean audit

`apply_errata()` looked up **every** hex correction of the ledger and counted **every** row whose
correction did not resolve as `errata-invalid`, so a row for a round that was not audited made a
clean selected-round audit fail (exit 1) — against the defined selected population and against the
round-23 selftest case `unselected-round-row-ignored`.

Fixed at the dataflow level (candidate `:609-646`): the hexed correction lookup inputs **and** the
invalid comprehension are both restricted to `e["round"] in selected`; the unmatched and refusal
loops already were. Consequences: no object of an unselected round is read any more (that read
was a guess), and a row of an unaudited round can no longer produce a verdict about this audit.

Measured (a clean round-1 audit, one errata row for round 2 with an unresolvable correction):

| version | exit | errata_invalid |
|---|---|---|
| pinned `2e` (production) | 1 | 1 |
| ca162 fix | 1 | 1 |
| **v2** | **0** | **0** |

New selftest case `unselected-invalid-correction-is-ignored` (exit 0, `errata_invalid` 0,
`errata_unmatched` 0). The round-23 case `unselected-round-row-ignored` and the other 49
round-23 cases are unchanged.

### 2. CodeRequiredReads — the committed errata read was a bare git error

`load_errata()` read the committed ledger with a bare `git show`, so a missing or unreadable
ledger produced a raw git message instead of the reason class the other required reads use.
Fixed (candidate `:584-598`): the committed read is wrapped with
`required_read(f"{tip}:{ERRATA} in {lane_repo}", exc)`, which keeps the original cause and the
path inside the message and adds the `unavailable required object:` class. No upfront gate was
added; the `--errata PATH` branch is untouched.

### Verification of v2

- `--selftest` → **67 cases, 0 failed** (66 before this proposal, plus the new
  `unselected-invalid-correction-is-ignored`).
- historical ledger: `--lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --fleet-repo
  /home/vgpnk/Projects/shokunin --rounds 10- --json` → exit 0 and the `--json` document
  **byte-identical** to the round-23 base output (`cmp` clean); every committed ledger correction
  belongs to a selected round, so nothing changes for the real history.
- No full suite was run (wave 2 is live); no installs, no network, no pacman transaction, no
  commits or pushes; the production file is untouched.


## Fourth proposal (v3): six behavioural consumer regressions + proof driver

No source or wiring assertion was added (User PM08): the six regressions are **behavioural** —
they assert exit codes and finding kinds of a real audit. The frozen 47-cell table is untouched.

New artifacts (the ca162c9c and v2 versions stay filed as they are):

- `report-landing-audit-v3.py` — sha256
  `f9c9d4d3eb99ed6ab3f8c23b56824dc97054c0ea62fed6ef2a7aa5b4673bf801` (1458 lines): the v2
  source plus the three missing consumer regressions.
- `report-landing-audit-v3.patch` — unified diff against the pinned `2e254a1` (integration base).
- `report-landing-audit-v3-vs-v2.patch` — the delta of this proposal alone.
- `proof-driver.py` — the bounded CLI proof driver (offline, temporary directories, subprocess
  exit codes): it runs each scenario against the **pinned production file** (before-pinned), the
  **ca162c9c producer version** (before-ca162) and **v3** (after-v3), and prints the exit code,
  the finding kinds and the refusal reason.

The six consumer regressions (all in the candidate's own selftest, all behavioural):

| # | regression (selftest case) | expectation |
|---|---|---|
| 1 | `fleet-only-blob-citation-is-a-failed-finding` | exit 1, `landed-unresolved` |
| 2 | `fleet-only-tree-citation-is-a-failed-finding` | exit 1, `landed-unresolved` |
| 3 | `fleet-only-tag-citation-is-a-failed-finding` | exit 1, `landed-unresolved` |
| 4 | `errata-correction-naming-a-fleet-only-blob-is-invalid` | exit 1, `errata_invalid` 1 |
| 5 | `same-tag-in-both-stores-is-a-known-mismatch` | exit 1, `landed-unresolved` for the tag |
| 6 | `unselected-invalid-correction-is-ignored` | exit 0, `errata_invalid` 0 |

The mirror and unreadable-target positive controls stay: `lane-only-blob-citation-is-a-failed-finding`,
`known-tag-with-unavailable-target-is-unknown`, `tag-target-missing-everywhere-is-unknown`.

### CLI before/after (proof driver, offline)

| scenario | before-pinned (production 2e) | before-ca162 (ca162c9c) | after-v3 |
|---|---|---|---|
| fleet-only blob | **exit 2** `unknown: unavailable required object: 28d34a63…` | exit 1 `landed-unresolved` | exit 1 `landed-unresolved` |
| fleet-only tree | **exit 2** `unknown: unavailable required object: a1eb0c81…` | exit 1 `landed-unresolved` | exit 1 `landed-unresolved` |
| fleet-only tag | **exit 2** `unknown: unavailable required object: a41c20ec…` | exit 1 `landed-unresolved` | exit 1 `landed-unresolved` |
| errata correction naming a fleet-only blob | **exit 2** `unknown: unavailable required object: 28d34a63…` | exit 1 `landed-unresolved` + `errata_invalid` | exit 1 `landed-unresolved` + `errata_invalid` |
| same canonical tag in both stores, target blob observable in one | **exit 2** `unknown: unavailable required object: 0548ca40…` | exit 1 `landed-unresolved` | exit 1 `landed-unresolved` |
| unselected round's invalid correction | **exit 1** | **exit 1** | exit 0 |

The red-before facts for the four object-shape scenarios and for the same-canonical-tag scenario
are the **pinned production** behaviour (exit 2 where the contract wants exit 1); the fresh falsifier
report `CritNoExtraScope` carries the same fleet-only-blob fact, and the same-canonical-tag fact
was measured in this seat's bounded probe before the reconciliation (the unit-level red that the
driver now completes at CLI level). The unselected-round row is red in both earlier versions and
green only after the selected-scope fix.

### Verification of v3

- `--selftest` → **70 cases, 0 failed** (67 before this proposal, plus the three new consumer
  regressions).
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output.
- No full suite (wave 2 is live); no production write; no installs, no network, no commits.


## Fifth proposal (v4): the open-range fleet listing read joins the required-read class

`CaseFleetTree M1` reported the same consumer-read gap as the round-1 path: in the **default/open
range** (`--rounds 10-`, i.e. `parse_rounds()`) the fleet listing
`git ls-tree -r --name-only HEAD -- .ufo/reports` failed with a bare git error, while the
round-1 path already named the missing tree.

New artifacts (v3 and the earlier versions stay filed):

- `report-landing-audit-v4.py` — sha256
  `f457f8cb9dfbaf7b41686b59338bb8997c98a861226b47e5a946acfb1fd7bdb8` (1528 lines)
- `report-landing-audit-v4.patch` — unified diff against the pinned `2e254a1` (integration base)
- `report-landing-audit-v4-vs-v3.patch` — the delta of this proposal alone
- `proof-driver.py` now also runs the `after-v4` column (the six consumer regressions are
  unchanged by this proposal: the v4 column reproduces the v3 column exactly).

What changed (bounded to the reported consumer read):

1. `parse_rounds()` (candidate `:678-690`) — **only** the fleet listing read is wrapped:
   `required_read(".ufo/reports at fleet HEAD (tip tree <oid>, <repo>)", exc)`, with the fleet
   tip tree id when it can be read. No upfront gate, no change to the round selection, no
   change to the expected 47 cells.
2. `git()` (candidate `:166-178`) — a timeout or a broken git is now tagged `fatal` on the
   EvalError; `root_tree(repo, root, cause)` skips its diagnostic call when the cause is fatal,
   so a timed-out read never spends a second 20 s. Every existing diagnostic tree read passes its
   cause along, so the rule applies to all of them, not only the new one. The per-call deadline
   (20 s) is unchanged.
3. New bounded selftest case `open-range-listing-names-the-missing-fleet-tree`: the fleet's tip
   tree is deleted and the default open range is audited; the refusal must name that tree id and
   carry the `unavailable required object` class.

### Verification of v4

- `--selftest` → **71 cases, 0 failed** (70 before, plus the new diagnostic case); the 50
  round-23 cases and the six consumer regressions are unchanged.
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output
  (`cmp` clean).
- the proof driver: the `after-v4` column equals the `after-v3` column on all six consumer
  regressions.
- No full suite (wave 2 is live); no production write; no installs, no network, no commits.


## Sixth artifact: `proof-driver-replay.py` — the pinned, registerable replay probe

The earlier `proof-driver.py` (kept filed as it is) read the **mutable production file** as its
"before" side; after integration that would silently stop being a red-before. The replay driver
fixes that and is the probe Main and the third seats can register:

- **The before side is extracted exactly from the pinned lane revision**:
  `git --no-replace-objects --no-lazy-fetch show 2e254a17:tools/report-landing-audit.py`, and the
  extracted bytes are checked against the known baseline sha256
  `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` **before** they are
  written to a temporary file. A mismatch is an input error; the mutable production file is never
  read as the before side.
- **The lane repository root is derived from this file's location**
  (`.ufo/waves/round-24/fixes/StoreLocalPresence/` → the repository root), not from a host path;
  the driver runs from any working directory.
- **`--after PATH`** binds the tool under test explicitly (default: the v4 proposal next to the
  driver), so Main and the third seats can bind a verified pinned tool.
- **`--only NAME`** takes one of the six consumer names (`fleet-only-blob`, `fleet-only-tree`,
  `fleet-only-tag`, `errata-fleet-only-blob`, `same-tag-both-stores`,
  `unselected-invalid-correction`); `--text` prints the human table, the **JSON document is the
  default**.
- **The JSON records** the before commit and source sha256, the after path and sha256, the number
  of consumers, and for every consumer the exact CLI outcome (exit, finding kinds, errata_invalid,
  the refusal line) beside the **independent expectation** (exit and kinds) taken from the
  contract, plus a per-side `matches_expectation` flag.
- **Exit convention**: 0 = the measurement completed (the JSON carries the comparison), 2 = an
  input error (a bad `--after`, an unreadable pinned revision, a baseline mismatch, an unknown
  `--only`). The probe makes **no admission claim**: it measures, it does not gate.

Measured with the pinned extraction (default `--after` = the v4 proposal, sha256
`f457f8cb9dfbaf7b41686b59338bb8997c98a861226b47e5a946acfb1fd7bdb8`):

| consumer | expected | before (pinned 2e254a17) | after (v4) |
|---|---|---|---|
| fleet-only-blob | exit 1, `landed-unresolved` | **exit 2** `unknown: unavailable required object: 28d34a63…` | exit 1 `landed-unresolved` |
| fleet-only-tree | exit 1, `landed-unresolved` | **exit 2** (`a1eb0c81…`) | exit 1 `landed-unresolved` |
| fleet-only-tag | exit 1, `landed-unresolved` | **exit 2** (`a41c20ec…`) | exit 1 `landed-unresolved` |
| errata-fleet-only-blob | exit 1, `landed-unresolved`, errata_invalid 1 | **exit 2** (`28d34a63…`) | exit 1, errata_invalid 1 |
| same-tag-both-stores | exit 1, `landed-unresolved` | **exit 2** (`0548ca40…`) | exit 1 `landed-unresolved` |
| unselected-invalid-correction | exit 0 | **exit 1** (errata_invalid 1) | exit 0, errata_invalid 0 |

The red-before side is therefore reproducible from the pin alone, and the counting is durable: the
JSON names the consumers, their expectations and both sides' outcomes, so a final gate can count
them without re-deriving anything.


## Seventh artifact: v5 — the opaque fallback is scoped to the audited root (`CodePerRunCache F2`)

A real no-harm gap: the **opaque** fallback (a missing tree or commit that hides names) was
computed over the whole store, so unrelated unreachable garbage in a repository could make an
ordinary audit refuse (exit 2) where the original local contract wants the ordinary finding
(exit 1) — the reported `1 -> 2 -> 1` on the same audited content.

New artifacts (v4 and the earlier versions stay filed):

- `report-landing-audit-v5.py` — sha256
  `faea33d3cf437acb6c277a22e44839699105ee732f7fc79e8a98aae19540e6f3` (1557 lines)
- `report-landing-audit-v5.patch` — unified diff against the pinned `2e254a1` (integration base)
- `report-landing-audit-v5-vs-v4.patch` — the delta of this proposal alone
- `proof-driver-replay.py` — its default `--after` is now the v5 proposal; the six consumer
  red-before proof is unchanged and still reproduced (all six `matches_expectation` true on v5)

What changed (`missing_reachable()`, candidate `:733-760`): the two walks now have **two root
sets**, and the cache tuple `(missingAll, opaqueRelevant)` keeps its shape:

- `missingAll` — **store-wide**: all present commit/tree/tag roots plus the pinned root. A
  dangling commit, tree or tag that references a missing object is still seen, so a citation of
  such an object is still unknown (exit 2): the known-reference diagnosis is **not** dropped.
- `opaqueRelevant` — **the pinned root only**: a missing tree or commit is only "opaque" when it
  hides names *behind the audit's own root*. Unreachable garbage is not a dependency of the audit
  and must not block it.

No upfront gate, no source or policy retrofit, the 47-cell table unchanged. Consequences:

- PG46/PG47 (a missing non-leaf tree **in the selected root**) + an unresolved citation → still
  exit 2 (the tree is in the pinned root's closure).
- PG48 (the same hole, every citation resolved) → still exit 0.
- an explicitly cited missing blob behind a dangling **present** tree → still exit 2
  (`missingAll` is store-wide).
- unreachable opaque garbage + an ordinary fabricated citation → exit 1 with
  `unresolved-full-hash` (the ordinary local contract), not exit 2.

New behavioural regressions (both in the candidate's selftest):

- `unreachable-opaque-garbage-does-not-block` — a dangling present tree whose blob is deleted,
  plus an ordinary fabricated citation → exit 1, `unresolved-full-hash` for the fabricated hash.
- `cited-missing-behind-a-dangling-tree-is-unknown` — the same fixture with the **deleted blob
  cited** → exit 2 (the blob is referenced by a present object the store cannot serve).

### Verification of v5

- `--selftest` → **73 cases, 0 failed** (71 before, plus the two new regressions); the 50
  round-23 cases and the six consumer regressions are unchanged.
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output.
- `proof-driver-replay.py` with the pinned before and the v5 after: all six consumers match their
  independent expectation; the before side stays red (exit 2 ×5, exit 1 ×1) from the pin alone.
- the v5 patch applies cleanly to the pinned `2e254a1` and reproduces the file byte-for-byte.
- No full suite (wave 2 is live); no production write; no installs, no network, no commits.


## Eighth artifact: v6 — a real opaque-hole regression for the F2 scoping (the v5 fixture was stale)

The L1's static review was right: the v5 regression fixture built a dangling present **tree** with a
**deleted blob** — a blob hole, not an opaque one — and that shape already passes on the pinned
`2e254a17` tool, so it proved nothing about the F2 scoping.

New artifacts (v5 and the earlier versions stay filed; the registered six-consumer driver keeps its
six consumers and now binds v6 by default):

- `report-landing-audit-v6.py` — sha256
  `326839ba68a86f0d186805f6d3115f0249e7cba0c22fa12d3d497a48328f9d62` (1557 lines)
- `report-landing-audit-v6.patch` — unified diff against the pinned `2e254a1` (integration base);
  verified to apply cleanly and reproduce the v6 file byte-for-byte
- `report-landing-audit-v6-vs-v5.patch` — the delta of this proposal alone (the algorithm is
  unchanged from v5; only the regression fixture is corrected)
- `opaque-garbage-proof.py` — the bounded red-before proof for this case (pinned extraction,
  baseline sha256 verified, one fixture, both sides measured)

**The algorithm does not change in v6** — the root scoping of v5 stands. What changed is the
fixture, now a genuine opaque hole:

- a dangling **present commit** (`git commit-tree`) that names a **real tree object the store
  cannot serve** (the tree is deleted, its blob stays present); no ref reaches the commit or the
  tree, and the selected root is complete;
- the selftest asserts the walk semantics directly: the store-wide `missingAll` walk **includes**
  the deleted tree, the all-present-roots no-blob walk classifies it as **opaque**, and the
  selected-root no-blob walk **does not**;
- the behavioural assertion: an ordinary fabricated citation → exit 1 with the fabricated hash as
  an `unresolved-full-hash` finding (the original local contract);
- the previous v5 case is **retained and renamed** as the blob positive control
  (`unreachable-missing-blob-does-not-block`), and the cited-missing-behind-a-dangling-tree control
  (exit 2) is kept unchanged.

Bounded red-before proof (`opaque-garbage-proof.py`, pinned before vs v6):

| side | outcome |
|---|---|
| before (pinned `2e254a17`, sha256 `ea51bc35…`) | **exit 2** `unknown: unavailable required object: 1234567890abcdef… could be hidden behind the missing tree or commit de0d3c5a78eb…` |
| after (v6, sha256 `326839ba…`) | exit 1, `unresolved-full-hash` for the fabricated hash |

### Verification of v6

- `--selftest` → **75 cases, 0 failed** (73 in v5, plus the corrected opaque fixture and the
  renamed blob control); the 50 round-23 cases and the six consumer regressions are unchanged.
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output.
- `proof-driver-replay.py` with the pinned before and the v6 after: all six consumers still match
  their independent expectation; the before side stays red from the pin alone.
- the v6 patch applies cleanly to the pinned `2e254a1` and reproduces the file byte-for-byte.
- No full suite; no production write; no installs, no network, no commits.


## Ninth artifact: v7 + `proof-driver-replay-v2.py` — the errata correction consumer, isolated

The L1's static review was right about row 4 of the six-consumer proof: the scenario cited the same
fleet-only blob in the **report and in the ledger**, so the pinned tool aborted on the *report*
lookup (exit 2) before the errata row was ever consulted. That red was a **body-root bug, not an
independent proof of the correction consumer** — it is marked as such here, and the v1 driver's raw
receipts stay unmodified.

**v1 driver** (`proof-driver-replay.py`) and its six raw receipts stay as filed; **v2**
(`proof-driver-replay-v2.py`) differs in ONE scenario and adds a control.

New artifacts (v6 and the earlier versions stay filed):

- `report-landing-audit-v7.py` — sha256
  `c19568547d50b6d752d1d3caf20fbcc935305ab2964c9569d03eda5b5b400d37` (1578 lines)
- `report-landing-audit-v7.patch` — unified diff against the pinned `2e254a1` (integration base);
  verified to apply cleanly and reproduce the v7 file byte-for-byte
- `report-landing-audit-v7-vs-v6.patch` — the delta of this proposal alone
- `proof-driver-replay-v2.py` — the versioned driver: the same pinned before, the same five
  untouched consumers, **row 4 isolated**, and an explicit **no-errata control** per case; its
  default `--after` binds v7, and Main/W3 can bind any verified tool explicitly with `--after`

**The isolated correction case** (v2 driver and the v7 selftest): the report's `## Landed changes`
cites a **known LANE blob A** (different bytes from B) — an ordinary `landed-unresolved` on its own —
and the selected ledger row `landed-unresolved A` is corrected with a **fleet-only blob B**.

| side | with the ledger | without the ledger (the control) |
|---|---|---|
| before (pinned `2e254a17`) | **exit 2** `errata line 1: unknown: unavailable required object: 55743606… is present but its content cannot be served` | exit 1, `landed-unresolved` (the ordinary body) |
| after (v7) | exit 1, `landed-unresolved` + `errata_invalid` 1 | exit 1, `landed-unresolved` |

So the before red now comes from the **correction consumer** (the errata line is named in the
refusal), while the control shows the body's own ordinary finding — the two are independent.

**The embedded v6 regression had the same mask** (the report cited the same fleet-only blob that
the ledger corrected), so v7 replaces it: the masked case is **retained and renamed**
`errata-correction-naming-the-cited-fleet-only-blob-is-invalid` (a valid control: the report's own
fleet-only blob is an ordinary finding and the ledger row that repeats it is invalid), and the
isolated case is added with its own body control
(`known-lane-blob-citation-is-an-ordinary-finding` +
`errata-correction-naming-a-fleet-only-blob-is-invalid`). **No generic code algorithm change** — the
v6 source is unchanged apart from the fixtures.

### Verification of v7

- `--selftest` → **77 cases, 0 failed** (75 in v6, plus the isolated fixture and its body
  control); the 50 round-23 cases, the 47 cells and the other five consumers are unchanged.
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output.
- `proof-driver-replay-v2.py` with the pinned before and the v7 after: the five untouched consumers
  match their expectations, and row 4 is red in the correction consumer with the body control green
  (exit 1) — the isolation the review asked for.
- the v7 patch applies cleanly to the pinned `2e254a1` and reproduces the file byte-for-byte.
- No full suite; no production write; no installs, no network, no commits.


## Tenth artifact: v8 — the tag regression, isolated, and the prose made accurate

The L1's v7 review was right again: the embedded tag regression copied **both** the tag **and** its
target into the lane, so both stores could serve the target — the case was already green on the
pinned `2e254a17` tool and proved nothing about the reconciliation.

New artifacts (v7 and the earlier versions stay filed):

- `report-landing-audit-v8.py` — sha256
  `0a96fc42de8282bbadf81e445bed211ab5a7a54f264d3b4cbebddf007be4d918` (1637 lines)
- `report-landing-audit-v8.patch` — unified diff against the pinned `2e254a1` (integration base);
  verified to apply cleanly and reproduce the v8 file byte-for-byte
- `report-landing-audit-v8-vs-v7.patch` — the delta of this proposal alone

### The tag case, now in three phases (the classification is unchanged)

| phase | target observable in | expected | selftest case |
|---|---|---|---|
| control | both stores | exit 1, `landed-unresolved` (already green on 2e — kept as a control) | `same-tag-in-both-stores-known-mismatch-is-a-control` |
| **the regression** | the fleet only (after the lane's copy is unlinked, before the fleet's) | exit 1, `landed-unresolved` (the pinned tool: exit 2) | `same-tag-with-the-target-only-in-the-fleet-is-a-mismatch` |
| mirror control | the lane only | exit 1, `landed-unresolved` | `same-tag-with-the-target-only-in-the-lane-is-a-mismatch` |
| retained | nowhere | exit 2 (the content cannot be read) | `tag-target-missing-everywhere-is-unknown` |

Bounded proof of the regression (the v2 replay driver's case 5, which already used the "target only
in the fleet" shape and is left unchanged): before (pinned `2e254a17`) → **exit 2** `unknown:
unavailable required object: 0548ca40… is present but its content cannot be served`; after (v8) →
exit 1 with `landed-unresolved` for the tag.

### Prose made accurate (no behaviour change)

- `RepoStore.missing()` and `missing_reachable()` now describe **the object ids that present local
  objects reference but the repository cannot serve** — not "the local history": a dangling tree
  or commit is a present local object, not history.
- `unknown_citation()` likewise: "the store whose **present local objects** reference the cited
  token but cannot serve it".
- The two refusal messages now say `is referenced by local objects in <repo>` instead of
  `is referenced by the history of <repo>` (the dangling case is not history).
- The blob positive control's comment now says what the case does: the **fabricated citation is
  UNRELATED and absent**, so the ordinary finding stands; the dangling blob itself is cited in the
  **next** control, which is unknown (exit 2).

### Verification of v8

- `--selftest` → **79 cases, 0 failed** (77 in v7, plus the isolated tag phases and the mirror);
  the 50 round-23 cases, the 47 cells and the other five consumers are unchanged.
- historical ledger: `--rounds 10-` → exit 0, `--json` byte-identical to the round-23 base output.
- the v8 patch applies cleanly to the pinned `2e254a1` and reproduces the file byte-for-byte.
- No full suite and no grid run here (Main runs the final suite once); no production write; no
  installs, no network, no commits.


## Eleventh artifact: v9 — the walk's prose, sharpened (no algorithm or fixture change)

The L1's prose detail was right: the first walk does **not** name every missing object of the store
— the descendants hidden behind a missing tree cannot be enumerated. That is exactly why the
second walk exists.

- `report-landing-audit-v9.py` — sha256
  `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f` (1637 lines)
- `report-landing-audit-v9.patch` — unified diff against the pinned `2e254a1` (integration base);
  verified to apply cleanly and reproduce the v9 file byte-for-byte
- `report-landing-audit-v9-vs-v8.patch` — the delta of this proposal alone (docstrings only)

The wording now says: the first walk walks from every present object of the store and names the
unavailable ids it **encounters** (a dangling commit, tree or tag that references a missing object
is seen, so a citation of it is still unknown); the descendants hidden behind a missing tree cannot
be enumerated, which is why the second walk exists — it identifies the **opaque boundaries of the
pinned root** (the missing trees and commits behind the audit's own root, whose names are hidden),
rooted at the pinned root only, so unreachable garbage is not a dependency of the audit.
`RepoStore.missing()` uses the same "known unavailable object ids" wording.

**No algorithm change, no fixture change, no new test**: the code and the fixtures are byte-identical
to v8 apart from the two docstrings (the file compiles; the v9 patch is docstring-only).


## Twelfth artifact: `proof-driver-replay-v3.py` — a strict observer (v1 and v2 stay filed)

The L1's review of the v2 driver found two real **observer** bugs (the tool was never at fault):

1. `matches_expectation` compared **only the exit code**: wrong findings, or an ignored selected
   ledger row, could still go green.
2. The first five fixtures' drafts omitted the valid work commit `a`, so `audit_round` added a
   `landed-omitted` finding — an unrelated omission that could mask the acceptance of a wrong
   type.

v3 fixes the observer, not the tool:

- **Strict match**: exit **AND** the exact finding kinds **AND** `errata_invalid` must equal the
  declared expectation (`match_rule: "exit AND exact kinds AND errata_invalid"`). The raw kinds
  and `errata_invalid` are recorded for both sides and for the control.
- **No unrelated omission**: every fixture cites the valid lane commit in `## Landed changes`, so
  the findings under test stand alone. The expectations were **not** relaxed to include
  `landed-omitted`; the expected kinds stay exactly `["landed-unresolved"]`.
- **Distinct control expectations**: the no-ledger control of every case has its own expectation
  (`errata_invalid` 0 — the ledger is what makes row 4 invalid), so the body's own outcome is
  visible next to the ledger's.
- **Full pin**: the before side is extracted from the full commit
  `2e254a1763a9c08aa07fc53081287f506c447d84` with `--no-replace-objects --no-lazy-fetch` and
  checked against the known baseline sha256 `ea51bc35…` before it is written to a temporary file.
- **`--after` is required**: there is no default proposal to go stale (a missing `--after` is an
  input error, exit 2).
- The lane root is derived from the driver's location; the raw old v1/v2 receipts stay filed and
  are **qualified** by this section (their `matches_expectation` was exit-only and their first
  five drafts carried an unrelated omission).

Measured with `--after report-landing-audit-v9.py` (pinned before `2e254a17…`, baseline sha256
verified):

| consumer | expected (exit / kinds / errata_invalid) | before | after | after control (no ledger) |
|---|---|---|---|---|
| fleet-only-blob | 1 / `landed-unresolved` / 0 | **exit 2** | 1 / `landed-unresolved` / 0 ✓ | 1 / 0 ✓ |
| fleet-only-tree | 1 / `landed-unresolved` / 0 | **exit 2** | 1 / `landed-unresolved` / 0 ✓ | 1 / 0 ✓ |
| fleet-only-tag | 1 / `landed-unresolved` / 0 | **exit 2** | 1 / `landed-unresolved` / 0 ✓ | 1 / 0 ✓ |
| errata-fleet-only-blob | 1 / `landed-unresolved` / **1** | **exit 2** (`errata line 1: unknown: unavailable required object: 55743606…`) | 1 / `landed-unresolved` / 1 ✓ | 1 / 0 ✓ (the body is ordinary) |
| same-tag-both-stores | 1 / `landed-unresolved` / 0 | **exit 2** | 1 / `landed-unresolved` / 0 ✓ | 1 / 0 ✓ |
| unselected-invalid-correction | 0 / `[]` / 0 | **exit 1** (`errata_invalid` 1) | 0 / `[]` / 0 ✓ | 0 / 0 ✓ |

All six after-sides match **strictly**; all six before-sides are red; every control matches its own
distinct expectation. No core algorithm, fixture or 47-cell change; the tool candidate is
unchanged (v9).


## Thirteenth artifact: `opaque-garbage-proof-v2.py` — the same strict observer for the one-fixture proof

The same observer defect as in the replay driver v2: `opaque-garbage-proof.py` (kept filed
unmodified) compared **only the exit code**, so wrong findings could go green. v2 fixes the
observer, not the tool:

- **Strict match**: exit **AND** the exact finding kinds **AND** `errata_invalid` must equal the
  declared expectation.
- **Full pin**: the before side is extracted from the full commit
  `2e254a1763a9c08aa07fc53081287f506c447d84` with `--no-replace-objects --no-lazy-fetch` and
  checked against the known baseline sha256 `ea51bc35…` before it is written to a temporary file.
- **`--after` is required** (no default proposal to go stale).
- **The valid work commit is cited** in the fixture, so no unrelated `landed-omitted` finding can
  mask the finding under test — the expected kinds stay exactly `["unresolved-full-hash"]`.
- The JSON retains the **raw kinds** of both sides, **both source sha256s** and the **CID of the
  deleted tree** (and the dangling commit's id).

Measured with `--after report-landing-audit-v9.py`:

| side | outcome |
|---|---|
| before (pinned `2e254a17…`, sha256 `ea51bc35…`) | **exit 2** `unknown: unavailable required object: 1234567890abcdef… could be hidden behind the missing tree or commit de0d3c5a78eb…` — strict match false |
| after (v9, sha256 `b9be4f42…`) | exit 1, kinds `["unresolved-full-hash"]`, `errata_invalid` 0 — **strict match true** |

Fixture: the dangling present commit `20c9531457e8…` names the deleted real tree
`de0d3c5a78ebb524b88e2de2df5532c83733a68d` (its blob stays present); no ref reaches the commit or
the tree; the selected root is complete; the report cites the valid work commit and an ordinary
fabricated hash. This is the **real unreachable non-leaf supplement**, not the blob positive case.

No core, selftest or 47-cell change; the tool candidate is unchanged (v9).
