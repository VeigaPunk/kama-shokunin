# CodeOpaqueDiagnosis — `RepoStore.missing` / `missing_reachable` / `opaque_hole` falsification (round 24)

VERDICT: **HOLDS** for the graded (amended) local-object contract on the surface this family
attacks. **No source defect was found** in `tools/report-landing-audit.py` in
`RepoStore.missing`, `missing_reachable`, `unknown_citation` or `opaque_hole` at the pinned
revision. The diagnostic is **conditional** (it never runs on a clean audit), it distinguishes
**missing blob** from **missing non-leaf**, its root set is **store-wide over present objects
including dangling ones**, and there is **no full-closure precondition**: unrelated holes never
block a verdict. Two **sharp edges** (SE1, SE2) and three **fixture/expectation notes** (FN1–FN3)
are reported below; none of them falsifies the amended contract, but SE1 bounds what the
"opaque hole ⇒ unknown" rule can mean in a two-store audit.

Scope: one bounded family — 25 checks over four fixture scripts of my own construction, run in a
private scratch clone at the pinned commit, plus read-only static reads of the three target
functions and one read-only timing measurement on the real fleet repository. **No full grid was
run** (neither `tests/report-audit/promisor-grid.py` nor any of its rows), no mutation grid, no
auditor `selftest`, no network, no transport, no execution payload. PM08 was **not** executed
(static reading only). Nothing in production was edited: `production/.jj/index`, the fleet, the
sibling lanes, operator config, routing, services and the real object stores were not touched.

## Pinned artifacts and hashes (observed)

| Item | Value |
|---|---|
| Lane commit under test | `2e254a1763a9c08aa07fc53081287f506c447d84` (`round-24: land completed 64-seat build evidence and explicitly carry residual closure debt`) |
| Scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CodeOpaqueDiagnosis/repo`, detached at the above, `--no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin` |
| Source under test | `tools/report-landing-audit.py`, sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the expected `ea51bc35…`) |
| Preregistration | `.ufo/waves/round-24/preregistration.json`, sha256 `6dde0d72343c9b8e64ec6e3ae4c9b382dfa3daaf9d0f6afd3f274cfac30e844c` |
| Oracle amendment (live) | `.ufo/waves/round-24/oracle-amendment-1.json`, sha256 `930b087a218f880a55c4507b7f11309eae130e2b5dd2111e27d5653b39c8f82f` |
| Oracle snapshot (pre-inspection) | `.ufo/waves/round-24/oracle-snapshot-before-inspection.json`, sha256 `1f5a469989b24b6b321b6b9a39533dad00f7e4daba80dca5f1321e888b142b0e` |
| Oracle supplement (3 opaque cells) | `.ufo/waves/round-24/oracle-supplement-2.json`, sha256 `4600a8c3951d26b68ee2562d5967cecfe9b00d66443ac10e6d371956e5d34368` |
| Tooling (pre-existing, nothing installed) | git `2.56.0`, Python `3.14.8` |

The frozen r23 auditor (`0df800e8…`, sha256 `da5041a81…`) was **not** executed; it is history in
this report, never a target.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | **Conditional diagnostic only** — the store-wide walk is not an audit precondition | PASS (observed) — an in-process call counter on `missing_reachable` shows **0** walks on a clean audit (exit 0) and **1** walk on the unresolved-citation path (exit 2). The walk is memoised per store (`RepoStore._missing`) and reached only from `unknown_citation` / `opaque_hole`, which are reached only from `refuse_unknown` / `apply_errata` on a token that no store resolves. |
| A2 | **Missing blob ≠ missing non-leaf** | PASS (observed) — a missing blob referenced by a present tree is in `missing` and **not** in `opaque` (S2, S12, S20). A missing **tree** (S4, S5, S16, S21), a missing **commit** (S8) and a missing commit hidden behind a present **tag** (S14) are in `opaque`. End-to-end: a blob hole + a fabricated citation yields **exit 1 `unresolved-full-hash`** (S3, S12) while a tree hole + the same fabricated citation yields **exit 2** naming the tree (S4). |
| A3 | **Store-wide present roots, including dangling** | PASS (observed) — a blob referenced only by a **dangling present commit** is in the store-wide `missing` set although a root-only walk never reports it (S7: `blob_in_missing=True`, `blob_in_rooted_walk=False`); a blob under a **dangling present tree with no commit at all** is likewise found (S20); objects in a **promisor-marked pack** still feed the root set (S22: `roots_before=11 roots_after=11`, dangling blob still found). `present_roots` is `cat-file --batch-all-objects` filtered to commit/tree/tag, i.e. exactly "present objects, reachable or not". |
| A4 | **No full-closure precondition** | PASS (observed) — with a missing tree present and **every** citation resolving locally, the audit is **exit 0 / no defects** (S5); with an unrelated missing blob (S2), an unrelated fleet-side blob hole (S14c) and a gitlink entry whose commit is absent (S18) the audit is likewise **exit 0 / exit 1 findings**, never a refusal. The refusal text is confined to the unresolved-token path. |
| A5 | **Refusal content and determinism** | PASS (observed) — the refusal always names the unavailable object: the cited token when the store references it (`… is referenced by the history of <repo> but the repository cannot serve it`, S6), the missing tree/commit when it could hide the token (`… could be hidden behind the missing tree or commit <oid> in <repo>`, S4/S16/S21), and the required report when the read itself fails (S14b). Two identical runs produce **byte-identical** stderr (S10). No traceback, no metadata refusal. |
| A6 | **Promisor metadata changes nothing** | PASS (observed) — the same fixture with `remote.origin.promisor=true` + `extensions.partialClone=origin` + an unreachable `ssh://example.invalid` URL keeps the identical substantive verdict (S9: exit 2 naming the tree, `core.sshCommand` touch-trap **never fired**, `trap=False`); a promisor marker **without** a URL (S13a) and `extensions.partialClone` pointing at a URL-less origin (S13b) both keep the ordinary exit 1 finding; a promisor-marked **pack** does not blind the root set (S22). |
| A7 | **Wrong-type citation stays a finding under an unrelated opaque hole** | PASS (observed) — with a missing tree present, a citation of a **present blob** is still the normal `landed-unresolved` **finding** (exit 1, no refusal) (S17); a present **tag** whose target is unavailable is refused only when the audit actually dereferences it (cited in the Landed section → exit 2 `… is present but its content cannot be served`; cited in the body only → no peel, no refusal, matching the supplement's "requires an actual dereference" rule). |
| A8 | **Cost fits the auditor's own deadline** | PASS (observed) — `present_roots` + both walks take **0.04 s** on the pinned lane clone (2348 roots) and **0.09 s** on the real fleet repository (5436 roots), against `GIT_TIMEOUT = 20` s per git call. The walk is therefore not an operability hazard at the real fleet scale. |

## Exact commands, exits and finding/token pairs (observed)

Every auditor invocation below is the same shape, run in the scratch clone against a fixture of
my own construction:

```
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeOpaqueDiagnosis/work/tmp \
python3 /fast/scratch/hyaku/kama-r24/falsify/CodeOpaqueDiagnosis/repo/tools/report-landing-audit.py \
  --lane-repo <fixture>/lane --fleet-repo <fixture>/fleet \
  --branch master --lane kama --rounds 1 --json
```

| Case | Exit | stdout verdict / stderr | finding/token pairs |
|---|---|---|---|
| S1 baseline | 0 | JSON, `summary.status = clean` | `defects = []` |
| S2 unrelated missing blob | 0 | JSON, clean | `defects = []`; blob in `missing`, **not** in `opaque` |
| S3 blob hole + fabricated token `0000…0` | **1** | JSON | `[("unresolved-full-hash", "0000000000000000000000000000000000000000")]`, stderr empty (no refusal) |
| S4 missing tree + fabricated token | **2** | stdout empty | stderr `could-not-evaluate: round 1: unknown: unavailable required object: 0000…0 could be hidden behind the missing tree or commit 690824ded37f89eb78120f0c21d5cd49e831c831 in <fixture>/lane` |
| S5 missing tree, all citations resolve | 0 | JSON, clean | `defects = []` (tree still in `opaque`) |
| S6 cited missing blob `78981922613b…` | **2** | stdout empty | stderr `… unavailable required object: 78981922613b2afb6025042ff6bd878ac1994e85 is referenced by the history of <fixture>/lane but the repository cannot serve it` |
| S7 dangling present commit + missing blob | — | module-level | blob in store-wide `missing`; **not** in a root-only walk |
| S8 missing commit (dangling child's parent) | — | module-level | commit in `missing` **and** in `opaque` |
| S9 same as S4 + promisor metadata | **2** | stdout empty | identical stderr to S4; `trap=False` (no remote contact) |
| S10 determinism | 2 / 2 | stdout empty | stderr **identical** across both runs |
| S11 call counting | 0 → 2 | — | `clean_walks=0`, `unresolved_walks=1` |
| S12 promisor metadata + blob hole | **1** | JSON | `[("unresolved-full-hash", "0000…0")]`; blob **not** in `opaque` |
| S13a promisor marker, no URL | **1** | JSON | `[("unresolved-full-hash", "0000…0")]` |
| S13b `extensions.partialClone` without URL | **1** | JSON | `[("unresolved-full-hash", "0000…0")]` |
| S14 tag-hidden missing commit | — | module-level | commit in `missing` **and** `opaque` |
| S14b fleet report blob itself missing | **2** | stdout empty | stderr `could-not-evaluate: unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree 0bc0c93…, <fixture>/fleet): git show HEAD:.ufo/reports/round-1/kama.md … rc=128 fatal: bad object` |
| S14c unrelated fleet-side blob hole | 0 | JSON, clean | `defects = []` |
| S15 walk cost, pinned lane clone | — | module-level | `roots=2348 present_roots=0.01 s walks=0.03 s missing=0 opaque=0` |
| S16 fleet store's opaque hole named | **2** | stdout empty | stderr `… could be hidden behind the missing tree or commit 1d8a51e902b83ff328d25236037c634b2d1eeb5e in <fixture>/fleet` |
| S17 present blob cited under an opaque hole | **1** | JSON | `[("landed-unresolved", "78981922613b2afb6025042ff6bd878ac1994e85")]`, stderr empty |
| S18 gitlink entry, commit absent | **1** | JSON | `[("unresolved-full-hash", "0000…0")]`; gitlink oid in neither `missing` nor `opaque` |
| S19 walk cost, real fleet repo | — | module-level | `roots=5436 present_roots=0.02 s walks=0.07 s missing=0 opaque=0` |
| S20 dangling present tree, no commit | — | module-level | blob in `missing`, not in `opaque` |
| S21 cited blob hidden behind a missing subtree | **2** | stdout empty | stderr `… unavailable required object: 07e18a1de2b5e2bc5b7b177991626bf18519d307 could be hidden behind the missing tree or commit b443071579c136455b2aaa8320dd1f4bee424376 in <fixture>/lane` (cited blob in neither `missing` nor `opaque`; the tree is) |
| S22 promisor-marked pack feeds the root set | — | module-level | `roots_before=11 roots_after=11`; dangling blob still in `missing` |

Total: **25 checks, 25 as expected** (11 + 7 + 4 + 3); the four scripts were run twice each with
identical results.

## Findings

**SE1 (medium, sharp edge — not a contract violation).** `opaque_hole(stores)` is *store-agnostic
and token-agnostic*: it returns the first audited store that has **any** missing non-leaf object
and the lexicographically lowest such OID, and the refusal is raised for **every** unresolved
citation. Consequence, measured in S16: a missing subtree that lives in the **fleet** store turns a
**lane**-side unresolved citation into exit 2, naming the fleet's tree. Under the amended contract
this is the written rule ("a missing tree/commit may conceal the dependency names and makes that
unresolved citation unevaluable", and "unrelated unavailable objects must not become a blanket
precondition" — which the code honours by not refusing when *no* citation is unresolved), but the
blast radius is the whole two-store audit, and the named OID may be unrelated to the citation.
No correction is proposed: the rule as written intends this. L1 should record that the opaque-hole
refusal is **global to the audited store set**, not per-store, so that no future row assumes
per-store attribution.

**SE2 (low, sharp edge).** The refusal names `sorted(opaque)[0]` — the *lowest* missing non-leaf
OID of the first store with a hole — not the object that could actually hide the cited token. The
message wording is honest ("could be hidden behind"), and the choice is deterministic (S10), but a
reader may take the named OID as the culprit. No correction proposed; flagging only.

**FN1 (fixture note).** Two of my first-pass expectations were wrong, not the code: S5's
`landed-omitted` came from my own fixture citing only two of three required round-1 commits, and
S14b's expectation ("name the fleet blob") was wrong because deleting the **report** blob is a
`required_read` failure whose correct refusal names the report path, not the blob OID
(`unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD`). Both were corrected
in the fixture/expectation and re-run; the recorded artefacts contain the corrected versions.

**FN2 (fixture note).** The sibling `CaseFleetBlobless` hazard (a blobless clone whose
`remote.origin.url` points at a reachable local origin, so a stray probe without
`--no-lazy-fetch` materialises the missing blob and turns an exit 2 into a false clean exit 0)
**does not apply to my fixtures**: no fixture of mine is a partial clone of a reachable origin,
the promisor-marked ones point at the unreachable `ssh://example.invalid`, and the auditor's own
`GIT_ISOLATION` carries `--no-lazy-fetch` on every git call. S9 additionally arms a
`core.sshCommand` touch-trap and observes that it never fires.

**FN3 (fixture note).** The auditor's `--no-lazy-fetch` isolation means a *promisor-marked* fixture
in my family cannot accidentally hydrate, but the same isolation is why the **promisor** rows of
the graded grid need their own fixtures; my results say nothing about those rows and must not be
read as covering them.

**No correction to production source is proposed.** Nothing in the attacked surface is wrong
against the amended contract.

## Observed vs inferred

- **Observed** (executed, exit codes and bytes captured): every exit code, every stderr string,
  every finding/token pair, every `missing`/`opaque` membership, the walk-call counts, the
  walk timings and the promisor-marker behaviour above. All are reproducible from the scripts and
  result JSONs in `out/CodeOpaqueDiagnosis/`.
- **Inferred** (static reading, not executed here): that `missing_reachable`'s `root` argument is
  effectively vestigial — `present_roots` already contains every present object, so the
  `roots.append(root)` branch can only fire when the root object is absent, in which case the
  audit has already failed earlier at `resolve_branch` / `git log`. **Not executed**, so stated as
  a reading of `tools/report-landing-audit.py:651-676` at the pinned revision.
- **Inferred** (static): the `opaque`/`missing` split relies on `rev-list --objects
  --missing=print --no-object-names --stdin` for every missing id and the same walk with
  `--filter=blob:none` for the non-blob subset. The measured behaviour (S2/S3/S8/S14/S20) is
  consistent with git using the tree-entry type for missing blobs/trees and the parent/tag link
  for missing commits; the *mechanism* inside git was not dissected.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CodeOpaqueDiagnosis.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeOpaqueDiagnosis/probe.py` — fixture builder + S1–S11 (conditionality, blob vs non-leaf, dangling roots, determinism)
- `…/out/CodeOpaqueDiagnosis/probe2.py` — S12–S15 (promisor metadata, tag-hidden commit, fleet-side holes, walk cost)
- `…/out/CodeOpaqueDiagnosis/probe3.py` — S16–S19 (cross-store opaque attribution, wrong-type citation under an opaque hole, gitlink, real-fleet timing)
- `…/out/CodeOpaqueDiagnosis/probe4.py` — S20–S22 (commit-less dangling tree, opaque-tree-hides-cited-blob, promisor-pack roots)
- `…/out/CodeOpaqueDiagnosis/s23.py` / `s23b.py` — the known-tag-with-unavailable-target dereference check, in the two shapes (body citation vs Landed-section citation)
- `…/out/CodeOpaqueDiagnosis/probe-results.json`, `probe2-results.json`, `probe3-results.json`, `probe4-results.json` — machine-readable case → expectation → observation → pass records
- `…/out/CodeOpaqueDiagnosis/s23-tag-dereference.txt`, `…/s23b-tag-in-landed-section.txt` — captured stderr of the two tag-dereference shapes
- Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/CodeOpaqueDiagnosis/` — `repo/` (detached clone at the pinned commit), `work/` (all fixture roots, `TMPDIR`), `probe*.py`, `probe*-results.json`

Production `production/.jj/index`, the fleet, the sibling lanes, operator config, routing,
services and the real object stores were not touched. No network, transport or execution payload
was used; no lazy fetch was triggered (the `core.sshCommand` trap never fired); PM08 was not
executed; no mutant was executed; no tool was installed or updated (git 2.56.0 and Python 3.14.8
were already present).

Observation for L1 (not mine, not corrected): `git status` in the fleet working tree shows
modified `.ufo/state/*.report-baseline` files and `.ufo/watchdog.log`, and in the lane tree a
modified `.ufo/waves/round-24/build/advice/GridOracle.md` plus untracked `.ufo/waves/round-24/fixes/`.
My only production interaction was **read-only** git (`rev-parse`, `count-objects`, `ls-tree`,
`cat-file --batch-all-objects`, `rev-list --objects --missing=print`) for the S19 timing
measurement; none of those write, and I changed no production file other than this report and the
`out/CodeOpaqueDiagnosis/` artefacts. The listed modifications therefore come from sibling lanes
or L1 tooling.

## Unverified items

- The **graded 47-row grid was not run** — no row of `tests/report-audit/promisor-grid.py` was
  executed, in either arm. My results are about the *auditor source*, not about the grid's
  bookkeeping; they neither confirm nor refute any row's expectation metadata.
- The auditor's own `--selftest` and the mutation grid were **not** run; my S-series fixtures are
  independent of the candidate's selftest fixtures (different repo shapes, different hole kinds,
  different citation tokens) and the selftest's own `blob-hole-is-not-an-opaque-hole` /
  `missing-tree-is-an-opaque-hole` assertions were not relied upon.
- The **frozen r23 arm** (`0df800e8…`) was not executed and its source was not diffed against the
  pinned candidate; the r23 rows are history here, never a target.
- The **real production lane and fleet** were only *read* for one timing measurement (S19) and one
  root-count (S15 used my clone, not production). No audit was run against production repos, so no
  production verdict of any kind is claimed.
- The **transport / lazy-fetch** question is answered only for the shapes I built (unreachable ssh
  URL with a touch-trap). I did not attempt, and could not attempt, a reachable-origin partial
  clone; the sibling `CaseFleetBlobless` observation stands for that family.
- **PG-row mapping**: I did not execute PG46/PG47/PG48 or the supplement's three opaque cells
  through the grid's builders. My S21 is the *shape* of `opaque-tree-hides-cited-blob` and S5/S4
  are the *shape* of `opaque-unused-tree-no-unresolved-token` /
  `opaque-tree-with-unresolved-fabricated-token`, but the grid's own fixtures and its expectation
  columns were not exercised.
- The **Git floor** prerequisite (`>= 2.45`, inherited and still open at L0) was not probed: the
  host runs git `2.56.0`, so `--no-lazy-fetch` is available here; nothing here shows what happens
  on an older git, where `--no-lazy-fetch` is rejected and the isolation itself becomes an
  `EvalError`.
- `missing_reachable`'s handling of a **shallow** or **grafted** repository was not probed (the
  auditor refuses those earlier in `check_history_repo`); and the **sha256 object format** refusal
  was not probed.

Report: .ufo/waves/round-24/falsify/advice/CodeOpaqueDiagnosis.md
