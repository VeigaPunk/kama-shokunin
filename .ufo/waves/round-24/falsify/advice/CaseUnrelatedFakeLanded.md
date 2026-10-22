# CaseUnrelatedFakeLanded — r24 FRESH FALSIFICATION (read-only production)

Scope: fixture family **UnrelatedFakeLanded**, bounded selection
`PG22-unknown-citation-incomplete-promisor` (policy) and
`PG37-unused-missing-blob-with-fabricated-citation-plain` (control twin).

## Verdict

**HOLDS** — the two rows are met under the live (amended) view, and the
originally withdrawn expectation stays visible and unmet (never relabelled
passed). No source defect was found in scope. Fixture/harness weaknesses are
listed separately below (F1–F4) and do not change either row's verdict.

## Base observed (not inferred)

- Clone: `/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeLanded/clone`
  (`git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin clone`)
- `git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84` →
  `HEAD is now at 2e254a1 round-24: land completed 64-seat build evidence and
  explicitly carry residual closure debt`
- `git rev-parse HEAD` → `2e254a1763a9c08aa07fc53081287f506c447d84`;
  `git status --porcelain` → empty (clean tree, detached at the pinned base).
- Re-clone/checkout with explicit exit codes (second scratch, `clone2`):
  `CLONE_EXIT=0`, `CHECKOUT_EXIT=0`, `git rev-parse HEAD` → `2e254a1…`, 0 dirty files.
- Pinned artifacts (sha256, in the clone at that base) match the contract:
  - `tools/report-landing-audit.py` → `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`
  - `tests/report-audit/promisor-grid.py` → `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`
  - `tests/report-audit/promisor-grid-expectations.json` → `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
  - `tests/report-audit/promisor-mutants.py` → `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`
- Grid run reported the same hashes: `auditor_sha256.current = ea51bc35…`,
  `auditor_sha256.frozen = da5041a8…` (the r23 blob `0df800e:tools/report-landing-audit.py`),
  `expectations_sha256 = d86b7bea…`.
- Environment: `git version 2.56.0`, `Python 3.14.8`. **No packages were
  installed or updated** (no tool was needed; nothing to record).

## Exact commands and exits

```
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeLanded/tmp \
  python3 tests/report-audit/promisor-grid.py --arm both \
    --case PG22-unknown-citation-incomplete-promisor \
    --case PG37-unused-missing-blob-with-fabricated-citation-plain --json
EXIT=0            # stdout 13832 B -> out/grid-run.json, stderr 0 B
```
(`cwd` = the pinned clone; `--arm both` = frozen r23 base + current candidate.)

```
$ TMPDIR=…/tmp python3 verify_unrelated_fake.py     # my independent re-check
EXIT=0
```
Artifacts: `out/CaseUnrelatedFakeLanded/grid-run.json`,
`grid-run.stderr` (empty), `independent-verify.json`,
`git-calls-PG22.log`, `git-calls-PG37.log`, `verify_unrelated_fake.py`.

## Grid result (runner-graded, live view)

`arms.current`: graded 2, **violations 0**, tracebacks 0, timeouts 0,
harness leaks 0, `twin_compared 2`, `twin_mismatch []`,
`withdrawn_original_failures ["PG22-unknown-citation-incomplete-promisor"]`.

| case | view | exit | findings (kind, token) | met |
|---|---|---|---|---|
| PG22 | amended (live) | 1 | `('landed-unresolved','0123456789abcdef0123456789abcdef01234567')`, `('unresolved-full-hash','0123456789abcdef0123456789abcdef01234567')` | `met_amended: true` |
| PG37 | original (= live; no `amended` entry) | 1 | identical pair | `met_amended: true` |
| PG22 | original (withdrawn) | 1 | — | `met_original: false` → reported as withdrawn, not counted as achieved |
| PG37 | original | 1 | identical pair | `met_original: true` |

`arms.frozen` (r23 base, history only): PG22 exit **2** with
`could-not-evaluate: <lane>: partial clone (remote.origin.promisor)`
(the r23 blanket metadata refusal; `met_amended_frozen false`); PG37 exit 1
already correct (`met_amended_frozen true`). So for this family the repair is
narrow: it removes the metadata-conditioned refusal and leaves the plain
twin's behaviour untouched.

No refusal string of any kind in the current arm: `stderr == ""`, stdout is
the verdict document only, and the forbidden phrases `partial clone (` /
`promisor pack` appear nowhere in stdout (`stdout_forbidden_metadata_strings: []`).

## Independent verification (premises asserted, not taken from the runner)

I rebuilt both fixtures with the **pinned** builders
(`c_unknown_citation_incomplete`, `c_unused_missing_blob_fabricated_plain`)
imported read-only from the pinned `promisor-grid.py`, then probed the stores
myself (`--no-lazy-fetch` everywhere; inventory = `cat-file --batch-all-objects`).

- **Promisor marking**: PG22 lane `promisor_backed = True` (config only:
  `extensions.partialclone`, `remote.origin.promisor=true`,
  `remote.origin.url` → an **absent local path**); PG37 lane and both fleets
  `promisor_backed = False`.
- **Actual missing objects**: lane missing set = exactly
  `['b2c475fedd466685003f05a02c7bd772186c0429']` — identical to the OID the
  builder dropped (`notes/unused.txt` blob). Fleet missing set = `[]`.
- **Blob hole, not an opaque hole**: the unfiltered
  `rev-list --objects --missing=print` walk reports that one OID; the
  `--filter=blob:none` walk reports nothing → no missing tree/commit, so no
  name-hiding hole. (Matches oracle-supplement-2's rule: blob-only unrelated
  holes do not make a citation unevaluable.)
- **Objects that are present**: lane commit `9bad795e…`, lane tip tree,
  `corpus/SOURCES.md` blob, fleet report blob — all present in their stores.
- **Fabricated token**: `0123456789abcdef0123456789abcdef01234567` is absent
  from *both* stores **and absent from the missing set** of both stores → it
  is not "known to name unavailable referenced local content", so the ordinary
  local verdict applies (amendment prospective_expected[2]).
- **Lane store is genuinely consulted despite the promisor marking**: the
  report also cites the lane commit `9bad795e…`, which exists **only** in the
  lane (`cat-file -e` in the fleet → rc=128) and in the lane → rc=0. The
  verdict carries **no** defect for it, so the lane store was queried and
  resolved it; only the fabricated token is unresolved. (PG22 alone could not
  show this — see F2.)
- **Finding/token pairs**: both cases produce exactly two uncorrected defects,
  `landed-unresolved` and `unresolved-full-hash`, both with token
  `0123456789abcdef0123456789abcdef01234567`, `corrected_by: []`,
  `summary.status = "failed"`, `uncorrected: 2`. No extra defect, no
  `landed-omitted` / `landed-ambiguous` / `landed-section-missing`.
- **No objects acquired**: object inventory before/after the auditor run is
  identical in both stores (`objects_acquired = {lane: [], fleet: []}`), for
  both cases; the dropped blob is still absent after the run.
- **No lazy fetch, no transport**: I put a logging `git` shim first on `PATH`
  and captured **every** git invocation the auditor made — 28 calls per case,
  every one carrying `--no-lazy-fetch` (plus `--no-replace-objects` and the
  log/signature/mailmap neutralisations). Subcommands actually used:
  `cat-file` (9), `rev-parse` (10), `rev-list` (4), `log` (2), `for-each-ref`,
  `ls-tree`, `show` (1 each). **Zero** `fetch`/`clone`/`ls-remote`/
  `upload-pack`/`push` invocations. The two `rev-list` walks are the
  store-wide diagnosis (`--missing=print`, and the `--filter=blob:none`
  variant) — diagnosis, not a precondition.
- **Twin comparison is real, not vacuous**: the runner reports
  `twin_compared 2`, `twins {PG22: true}` and `{PG37: true}` in the current
  arm, i.e. the PG22 and PG37 verdict documents are equal after path
  normalisation. I reproduced the same equality independently
  (`documents_equal_normalised: true`; raw equality is false only because the
  fixture paths differ).

## Original (withdrawn) expectation stays visible

- The expectations file still carries PG22's **original** row (exit 2,
  `reason_class "unavailable-or-unknown"`) unchanged; the live policy comes
  from the `amended` row (exit 1 + the two defects). The grader reports
  `met_original: false` for PG22 and lists it under
  `withdrawn_original_failures`; the overall exit stays 0 because a withdrawn
  expectation is not a violation. **No relabelling as passed.**
- Integrity of the expectation table (checked against the pre-inspection
  snapshot, not against the candidate):
  - `oracle-snapshot-before-inspection.json`: 44 cases; the expectations file:
    47 cases = the **same 44 rows byte-identical** (JSON-compared, 0 differing
    rows) + 3 new independent opaque cells `PG46/PG47/PG48`, whose exits
    (2/2/0) and reason classes match `oracle-supplement-2.json`.
  - Chronology from the pinned clone's history: `f66b226` 15:04:12 "freeze
    independent 44-case original and amended oracle before candidate
    inspection", `aacbd52` 15:12:55 "append independent opaque-dependency
    oracle supplement before candidate inspection", candidate `ed1cc3a`
    15:14:18 "restore local promisor verdicts …" (last change to
    `tools/report-landing-audit.py`, the grid runner and the expectations
    file). The oracle predates the candidate; the expectation cells were not
    edited to fit it.
  - PG37 has no `amended` entry → it is graded on its `original` view, as the
    snapshot's `views.amended` prescribes.

## Fixture flaws (reported separately from source flaws)

These do not change either row's verdict; they bound what the family proves.

- **F1 (medium, fixture limitation).** PG22's promisor marking points
  `remote.origin.url` at an **absent local path**
  (`<tmp>/absent-remote.git`, `mark_config`). The row therefore cannot falsify
  "the promisor remote is never contacted": the worst a lazy fetch could do
  is fail fast on a local path (no network egress is even possible), and there
  is no trap file to detect the attempt. The auditor's own selftest
  (`tools/report-landing-audit.py`, "promisor-remote-is-never-contacted")
  uses an `ssh://example.invalid` trap for exactly that. PG22 proves
  *metadata-independence of the verdict*, not *absence of remote contact*.
  (Related, from peer `CaseFleetBlobless`: blobless fixtures keep a
  **reachable** `file://` origin, where a stray probe without
  `--no-lazy-fetch` can materialise the missing blob. **This family is not
  exposed**: PG22's origin path is absent, and every probe I ran used
  `--no-lazy-fetch`; the dropped blob was still absent after the audit.)
- **F2 (low, fixture limitation).** The fabricated token is absent from both
  stores, so PG22 on its own cannot distinguish "promisor-marked lane
  consulted" from "promisor-marked lane skipped". I closed the gap
  out-of-family using the fixture's own second citation (lane commit present
  only in the lane, resolved with no defect) — the row itself does not pin it.
- **F3 (low, harness limitation).** The grid's twin comparison cannot detect
  a mismatch when one side yields no document: in the frozen arm PG22's
  document is `null`, so `twins {PG37: None}` and `twin_equal: None`
  (incomparable, not `False`). In the current arm both sides have documents,
  so my rows' no-harm comparison is real — but a future row whose expected
  exit is 2 on one side would silently skip the twin comparison instead of
  failing it.
- **F4 (low, runner API trap).** `promisor-grid.py`'s helper is
  `git(repo, *args, data=None, …)`; a caller that passes `stdin=` gets it
  swallowed as an env var and an **empty** stdin. I hit this in my own
  harness (the missing-object walk silently returned `[]`). No call site in
  the pinned runner does this today, so it is latent, not live. Note for L1
  only.
- **F5 (harness honesty note).** My first transport detector flagged
  `--no-lazy-fetch` because the flag contains the substring "fetch"; the
  re-run used a corrected matcher and the per-case logs (copied to the out
  directory) are the raw evidence.

## Source flaws

**None found in scope.** The behaviour the two rows exercise matches the
amended contract in the source: `lookup()` classifies the fabricated token as
absent in both stores; `unknown_citation()` finds no matching OID in the
missing set; `opaque_hole()` finds no missing tree/commit (blob-only hole);
`missing_reachable()` runs the two `--missing=print` walks over every present
object as a diagnosis, never as a precondition; every git call carries
`GIT_ISOLATION` (`--no-lazy-fetch`, `--no-replace-objects`, signature/log/
mailmap neutralisation), and `git_env()` strips inherited `GIT_*` variables.

## Residual risks / verification gaps

- **R1 (observability, not a contract violation).** PG22's exit-1 document
  carries no indication that the audited lane was a promisor-marked,
  incomplete repository; a consumer of the JSON alone cannot see that local
  evidence was incomplete. The amendment forbids a blanket refusal and forbids
  remote-completeness claims, so this is a disclosure question, not a defect —
  but L1 should know the verdict is a *local* verdict.
- **R2.** The "unrelated hole must not block" property is pinned here only
  for the *blob*-hole shape; the tree-hole shape is covered by PG46/PG47/PG48
  (other families, not mine).
- **R3.** The Git floor is untested by my measurement: `--no-lazy-fetch`
  requires Git ≥ 2.45 and the host runs 2.56.0. The inherited L0 prerequisite
  stays open.
- **R4.** My run exercised **2 of 47** rows; no whole-grid claim is made, and
  `promisor-mutants.py` (mutation sensitivity) was **not** run — outside my
  assigned selection.
- **R5.** "No transport" is proven at the command level (no transport verb was
  ever issued; every call isolated). A socket-level check (`strace`/`unshare`)
  was not run; the fixture's only remote URL is an absent local path, so
  network egress was not possible in the first place.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CaseUnrelatedFakeLanded.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CaseUnrelatedFakeLanded/`
  `grid-run.json`, `grid-run.stderr` (empty), `independent-verify.json`,
  `git-calls-PG22.log`, `git-calls-PG37.log`, `verify_unrelated_fake.py`
- Heavy scratch (not in production): `/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeLanded/`
  (`clone/`, `clone2/`, `verify/`, `tmp/`, `out/`). Production was not
  modified: no edit to `production/.jj/index`, fleet, sibling, operator
  config, routing, services or object stores; only L1 integrates.

## Appendix (appended after the peer cross-check, content above unchanged)

Coverage cross-reference for F1 (from peer `CaseFleetBlobless`, relayed here so
L1's coverage view is complete): the "promisor remote is never contacted"
property is **not** falsifiable in my family (absent `remote.origin.url` ⇒
nothing to contact), but it *is* exercised elsewhere in round 24 — PG43's
blobless fixture keeps a **live local `file://`** origin that really holds the
missing report blob (auditor exits 2, fleet inventory stays at 7 objects, no
`FETCH_HEAD`, no new pack, no loose object, remote's own store untouched:
HOLDS on the pinned candidate), and CaseLaneTree's bait-origin run shows the
auditor acquires nothing even when the origin serves the object. My rows
therefore falsify **metadata-independence of the verdict** only; the
"never contacted" property rests on PG43 and the bait-origin run, not on
PG22/PG37. No change to my verdict or to any expectation.

Report: .ufo/waves/round-24/falsify/advice/CaseUnrelatedFakeLanded.md
