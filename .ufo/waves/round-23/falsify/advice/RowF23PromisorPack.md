# Row F23 — promisor-pack-without-config — falsify report

Reviewer: CloseKama22.RowF23PromisorPack-2
Target: tests/report-audit/repo-state-grid.py row F23 (`f_promisor_pack`,
lines 194–212 of committed grid at 245a37f69628c2c6bb29bbf17897d8fb5946c857).
Auditors: frozen blob 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py
(→ /tmp/frozen-audit.py) vs committed tools/report-landing-audit.py
(→ /tmp/current-audit.py). Host: git 2.56.0, Python 3.14.8.

## Verdict: partially

Premise real and observed; expected outcome correct; near variants of the same
channel still evade current and reproduce the frozen failure mode (a false
defect verdict instead of refusal).

## (1) Premise — real, reproduced by hand

Hand-built fixture in /tmp/f23hand (no grid import): `git init` lane with one
commit LC=db796f8b820bf3825c58832419138cdba23206a7 authored by kama-shokunin
subject "round-1: work" at epoch 1000; `uploadpack.allowFilter=true`; blobless
clone `git -c protocol.file.allow=always clone -q --no-checkout
--filter=blob:none --no-local file://…/lane blobless`; then `git config --unset`
remote.origin.promisor / remote.origin.partialclonefilter /
extensions.partialclone (all three absent in `git config --list` afterward).
Fleet report cites LC under `## Landed changes` and the blob hash
6e98d181389d343031fd578c6a775ce0889a8b0d in a Notes line; fleet commit at
epoch 2000.

Observed premise facts (exit + output):
- `ls blobless/.git/objects/pack/` → `pack-….idx`, `.pack`, `.promisor`, `.rev` — marker present.
- `git -C blobless cat-file -e $BLOB` → rc=1 — blob missing.
- `git -C blobless config --list | grep -i 'clone\|promisor'` → empty — config stripped.

## (2) Frozen arm — fault observed, worse than "met 0/26" suggests

`python3 /tmp/frozen-audit.py --lane-repo blobless --fleet-repo fleet --json
--rounds 1 --no-errata` → **exit 1**, JSON verdict `uncorrected=1`,
defect `unresolved-full-hash` on token 6e98d18… (the promisor-remote blob
cited under `## Notes`, outside `## Landed changes`).

The frozen auditor has no promisor/partial-clone awareness at all (no
`check_history_repo`; `run()` goes straight from `--verify HEAD^{commit}` to
`load_source_urls`; `git()` is a bare `git -C` with no `--no-lazy-fetch`). It
did not crash or hang because the stripped config made lazy fetch
non-triggerable and every object it needed (commit LC, the report blob) was
local. Instead it emitted a **wrong defect verdict**: it treated a missing
promisor-remote object as fabrication. That is the literal harm the fixture
docstring names — "absence there is not evidence" — and it is why mere
exit-code refusal is the right expectation, not just a hygiene nicety.

## (3) Expected outcome — exit 2, reason "promisor pack" — CORRECT

`python3 /tmp/current-audit.py` (same argv) → **exit 2**,
stderr `could-not-evaluate: /tmp/f23hand/blobless: partial clone (promisor pack)`.
Committed check at tools/report-landing-audit.py:442–444 refuses when
`objects/pack` contains `*.promisor` whose `*.pack` companion exists;
lines 445+ refuse `extensions.partialclone` or truthy `remote.*.promisor` in
`--null --list` output.

Correctness argument: with missing objects in the store, any absence the
auditor measures (cat-file misses, missing blobs cited in reports) is
unattributable — lazy-fetchable or genuinely absent. The frozen arm
demonstrates the concrete harm of running anyway (false defect). Refusal
before any object read also avoids lazy-fetch hangs/network (the auditor
additionally passes `--no-lazy-fetch` in GIT_ISOLATION, line 93). The pinned
reason "promisor pack" correctly distinguishes this refusal from config-based
and shallow refusals.

## (4) Near variants of the same channel

| Variant | Setup delta | Current result | Expected | Verdict |
|---|---|---|---|---|
| **V1 marker deleted** | F23 fixture + `rm .git/objects/pack/*.promisor` (config still stripped) | **exit 1**, `unresolved-full-hash` on the blob (frozen-identical false verdict) | refuse (objects missing, provable) | **EVADES — defect** |
| **V2 promisor pack via alternates** | pack+idx+.promisor+.rev moved to /tmp/f23hand/altobj; `.git/objects/info/alternates` → `/tmp/f23hand/altobj` | **exit 1**, `unresolved-full-hash` false verdict; objects resolve through the alternate | refuse (a promisor pack is still attached) | **EVADES — defect** (overlaps declared-open O01 alternates) |
| V3 config kept, marker deleted | clone keeps promisor config; `rm *.promisor` | exit 2 `partial clone (remote.origin.promisor)` | refuse | caught |
| V4 promisor=false + `fetch --filter` | `git init`, `remote.origin.promisor=false`, `fetch --filter=blob:none` | git itself rewrote promisor→true and wrote the marker; blob present (fetchable) | — | channel closed by git |
| V5 stray orphan `.promisor` file (no `.pack`) | `touch objects/pack/fake.promisor` in complete repo | proceeds normally | proceed | correct (companion `.pack` gate) |
| V6 real promisor pack in fleet repo | pack+marker copied into fleet2 `.git/objects/pack` | exit 2 `partial clone (promisor pack)` | refuse | caught (both repos checked, line 475–476) |
| V7 `git repack -a -d` in stripped clone | — | repack fails on missing blob (`fatal: unable to read 6e98d18…`) and marker survives | — | no natural repack path to V1 |

V1 evidence: `git -C blobless-nomarker fsck` prints `broken link from tree
a33984f… to blob 6e98d18… / missing blob 6e98d18…` — the incomplete state IS
detectable without the marker; the auditor's refusal is fingerprint-based, not
completeness-based, so the failure mode is a wrong defect verdict, not a
refusal. Severity: medium — requires filesystem surgery on the object store
(or O01's alternates channel for V2), but produces exactly the frozen false
verdict the fix was meant to eliminate.

## Not verified / residual risk

- Other open rows not tested (O01 alternates-with-foreign-objects, O02
  gitfile, errata channels, sibling tools).
- Did not test `GIT_COMMON_DIR` env indirection (auditor scrubs GIT_* anyway)
  or bare-repo `--lane-repo` with promisor packs (same code path, likely caught).
- V2 overlaps declared-open O01; counted here only because it exercises the
  promisor-pack detection surface specifically.
- Working tree is dirty (sibling edits mid-wave); all runs used the committed
  blobs, verified `git rev-parse HEAD` = 245a37f69628c2c6bb29bbf17897d8fb5946c857.
- No tools installed; no installs needed.

## Files written

- `.ufo/waves/round-23/falsify/advice/RowF23PromisorPack.md` (this report)
- Scratch only under /tmp/f23hand (fixtures), /tmp/frozen-audit.py,
  /tmp/current-audit.py, /tmp/committed-grid.py — outside the lane.
