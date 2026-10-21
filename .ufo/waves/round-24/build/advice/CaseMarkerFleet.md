# CaseMarkerFleet — paired marker-only complete fleet oracle case (round 24)

Seat: `KamaR23-2.CaseMarkerFleet-2` (leaf member; no subagent dispatch).
Date: 2026-10-21. Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Auditor under test: `tools/report-landing-audit.py`, blob sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`
(base blob and current worktree blob are byte-identical — the case fails for
the candidate as it stands, not only for the frozen arm).
git 2.56.0, Python 3.14.8.

## Verdict

**The case is specified, preregistered, constructed and measured; it fails at
base exactly as preregistered, and it is satisfiable without any trade-off.**

At base a fleet repository that carries promisor *marker metadata* and holds
every required object locally is refused with `exit 2` ("partial clone"),
while an otherwise identical ordinary fleet clone yields a real verdict. The
marker arm must equal the plain arm — same exit, same defect multiset, same
report cutoff (`2000`), same required count — and it must never exit 2 while
its content is complete.

## Oracle (preregistered before the fixture builder existed)

`out/CaseMarkerFleet/oracle-case-marker-fleet.json`
(sha256 `cc94d9ec91da77cc38825079d9948ca6e9a5ed1d896440795c6bf1c34bae41c3`,
written 2026-10-21 14:57, before `build/case-marker-fleet.py` was written).

| variant | lane commits | expected exit | expected defects | cutoff | required |
|---|---|---|---|---|---|
| V1-clean | `LC@1000 round-1: work` (cited) | 0 | `[]` | 2000 | 1 |
| V2-omission | `LC@1000` (cited) + `X@1500 round-1: more` (uncited) | 1 | `["landed-omitted"]` | 2000 | 2 |

Arms, per variant: **plain** (ordinary complete fleet, no promisor metadata)
and **marker** (byte-identical object store copied from the plain fleet, plus
marker metadata only: `core.repositoryformatversion=1`,
`extensions.partialclone=origin`, `remote.origin.promisor=true`,
`remote.origin.partialclonefilter=blob:none`, `remote.origin.url` naming a
path that does not exist, `protocol.allow=never`).

## What the base does (measured)

Refusal site — `tools/report-landing-audit.py:462-465` inside
`check_history_repo` (`:438-465`), reached for both repositories from
`run()` at `:514-515`:

```python
462:        if key == "extensions.partialclone" or (
463:                re.fullmatch(r"remote\..+\.promisor", key)
464:                and git_bool(value)):
465:            raise EvalError(f"{repo}: partial clone ({key})")
```

Measured against the base auditor (`out/CaseMarkerFleet/obs-base.json`):

| variant | plain arm | marker arm |
|---|---|---|
| V1-clean | exit 0, defects `[]`, cutoff 2000, required 1 | **exit 2** — `could-not-evaluate: …/fleet-marker: partial clone (extensions.partialclone)` |
| V2-omission | exit 1, defects `[landed-omitted 29e8ea69cc44bbb72af22255c5231a7d13b577e0]`, cutoff 2000, required 2 | **exit 2** — same refusal |

This is the r23 harm the round repairs: *metadata alone* decides the outcome.
The refusal fires before any content check, so a repository whose content is
entirely present locally is indistinguishable from one with promisor holes.

## The case is not vacuous — measured premises

All premises are asserted by the builder and recorded in
`obs-base.json → variants.*.premises` (each is a hard failure, not a note):

- `same-head` — plain and marker fleet have the identical HEAD
  (`ebcb436228cc3c28fd415f5afcce3312e1151be4`);
- `same-object-count` (6 = 6) and `same-commit-graph`;
- `marker-extensions-partialclone`, `marker-remote-promisor`,
  `marker-filter` — the marker arm really carries the metadata;
- `plain-has-no-marker` — the plain twin carries none;
- `no-missing-objects` — `git --no-lazy-fetch rev-list --objects --all
  --missing=print` prints **no** `?` line in the marker arm (0 holes);
- `no-promisor-pack` — no `*.promisor` marker next to a pack;
- `fsck-connectivity-clean` — `git --no-lazy-fetch fsck --connectivity-only`
  exits 0 in the marker arm;
- `report-present-locally`, `cited-commit-present-in-lane`,
  `lane-complete`;
- `plain-cutoff-2000` and `marker-cutoff-2000` — the cutoff the oracle names
  is 2000 in both arms, so the marker metadata does not move the cutoff;
- `absent-origin-absent` + `protocol-never` + `lane-has-no-remote` — the
  transport is *impossible*, not merely unused.

## Discriminating boundary (why the marker metadata is not the whole story)

Same marker metadata, one required object genuinely absent (the committed
report blob removed from the object store):

- `git --no-lazy-fetch rev-list --objects --all --missing=print` prints
  `?855b5554aa04cf42fa9276fae2e891ee32df8d63`;
- `git --no-lazy-fetch fsck --connectivity-only` → `missing blob
  855b5554aa04cf42fa9276fae2e891ee32df8d63`, rc 2;
- the audit exits 2 (no verdict) and adds no object
  (`obs-unknown-citation.json`, `obs-base.json → boundary`).

A second boundary probe (marker-backed repository citing an object that
exists nowhere locally) must stay *unknown* (exit 2), never
`unresolved-full-hash`: base exits 2 ("partial clone"), the probe below exits
2 with "citation(s) not available locally in a promisor-backed repository:
unknown, not absent" — `out/CaseMarkerFleet/obs-unknown-citation.json`.

## Satisfiability probe (scratch only — NOT a production edit, NOT a candidate for integration)

`out/CaseMarkerFleet/make-probe.py` + `out/CaseMarkerFleet/auditor-probe.py`
(sha256 `58da34f452534812bd958ec4160a786f096ed11aa704316e2200e3a1ea01de6d`):
two edits on a copy of the base blob — (1) `check_history_repo` records a
promisor-backed repository instead of refusing it; (2) `lookup` turns a
citation missing in every audited repository into an `EvalError` when some
audited repository is promisor-backed. Nothing else changes.

`out/CaseMarkerFleet/obs-probe.json`:

| variant | plain arm | marker arm |
|---|---|---|
| V1-clean | exit 0, `[]`, cutoff 2000, required 1 | **exit 0, `[]`, cutoff 2000, required 1** (identical) |
| V2-omission | exit 1, `[landed-omitted 29e8ea69…]`, cutoff 2000, required 2 | **exit 1, `[landed-omitted 29e8ea69…]`, cutoff 2000, required 2** (identical) |

Boundary hole → still exit 2; unknown citation → still exit 2; no fetch, no
new objects in either arm (`store_before == store_after`, no `FETCH_HEAD`).
So the oracle costs nothing: metadata-only repositories can be evaluated while
genuine unavailability keeps refusing.

## What the repair must satisfy (contract for the implementation)

1. `check_history_repo` (`:438-465`) must stop treating promisor *metadata*
   as evidence of incompleteness. The decision must be driven by **content
   completeness/availability**, not by `extensions.partialclone`,
   `remote.*.promisor` or `remote.*.partialclonefilter`.
2. When a required object is unavailable, the outcome is exit 2
   (could-not-evaluate) — never a clean or failed verdict, never a guess.
3. A citation that cannot be resolved locally in a promisor-backed repository
   is *unknown* (exit 2) unless another audited repository resolves it.
4. `--no-lazy-fetch` (`GIT_ISOLATION`, `:93-97`) must stay: the probe and the
   boundary measurement show the completeness check itself does not fetch
   (`rev-list --missing=print` and `fsck` run with `--no-lazy-fetch`).
5. `report_cutoff` (`:215-218`) must be unaffected: the marker arm's cutoff
   is 2000, equal to the plain twin's.

## Integration: the grid fragment and a required grid change

`out/CaseMarkerFleet/grid-fragment.py` is a drop-in for the new
`tests/report-audit/promisor-grid.py` (which does not exist yet at base; the
GridOracle seat owns it). It supplies four control rows — P01 marker/clean,
P02 marker/omission, P03 plain/clean, P04 plain/omission — plus the
equality pairs P01≡P03 and P02≡P04 (same exit, same defect multiset, same
cutoff, same required count).

**Required change to the r23 grid model:** the r23 grid carries ONE expected
exit per case, applied to both arms
(`tests/report-audit/repo-state-grid.py:630-693` for the `CASES` rows and
`run_case` at `:717-759`). The marker rows need **per-arm expectations**: the
frozen/base arm expects exit 2 with the reason "partial clone", the repaired
arm expects 0/1 with the defect kinds. The fragment states the shape it needs
(`{"frozen": (exit, kinds, reason), "current": (exit, kinds, reason)}`), and
the reason string must be pinned so an unrelated startup error cannot pass as
the intended refusal (the r23 `REASONS` table, `:695-710`).

Measured with the fragment runner (`out/CaseMarkerFleet/run-grid-fragment.py`
→ `obs-fragment-rows.json`): all eight arm-expectations met, both equality
pairs true.

## No-harm / containment proof

- Every fixture repository is under
  `/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/run/<UTC>/…`; the scratch
  clone is `…/CaseMarkerFleet/repo` (pinned at `0df800e`, clean status).
- No git root at or above the scratch path: `git -C /fast`,
  `/fast/scratch`, `/fast/scratch/hyaku`, `/fast/scratch/hyaku/kama-r24`,
  `…/CaseMarkerFleet` all answer `fatal: not a git repository`.
- `find /tmp -maxdepth 1 -newermt '2026-10-21 17:50'` → no entries: no
  fixture escaped to `/tmp`.
- No network transport and no repo-configured program: the marker's remote
  url names a path that does not exist, `protocol.allow=never` forbids every
  transport, and no `core.sshCommand`/`gpg.program`/`credential.helper` is
  installed anywhere in the fixture. The auditor's own
  `--no-lazy-fetch` (`:93-97`) is kept in every run.
- Object stores are unchanged by every run (`store_before == store_after`,
  pack lists equal, no `FETCH_HEAD`).
- The lane repository's tracked files and index are untouched by this seat;
  the only writes are the sanctioned
  `.ufo/waves/round-24/build/out/CaseMarkerFleet/` and
  `.ufo/waves/round-24/build/advice/CaseMarkerFleet.md`. No commit, no push,
  no `.jj`, no operator config (`~/.gitconfig` does not exist).
- Determinism: the lane commit `db796f8b820bf3825c58832419138cdba23206a7`
  and the omission token `29e8ea69cc44bbb72af22255c5231a7d13b577e0` are
  identical across all 7 fixture runs (fixed identities and author/committer
  dates).
- No installs were needed or made by this seat.

## Residual risk and verification gaps (unrun = unverified)

- **Not run:** the candidate suite, the full r23 grid, the historical
  rounds 10–22 ledger, and any sibling case. This seat measured only its own
  bounded fixture. The claim that the repair is no-harm elsewhere is
  therefore unverified here.
- The probe's exact wording is *not* a design recommendation: it shows the
  oracle is reachable, not that this is the best implementation. In
  particular, the probe leaves the promisor-*pack* refusal
  (`:455-457`) in place, and that refusal still fires on a real blobless
  clone — a repository with a promisor pack is a different channel from a
  marker-only repository and is out of this case's scope.
- Whether the repair should also narrow `:455-457` (promisor pack) is
  undecided here; my fixture never produces a `.promisor` pack, so my case
  says nothing about it.
- Only `remote.origin.*` is modelled. A marker configuration using a
  differently named remote (`remote.upstream.promisor`) is covered by the
  same regex (`remote\..+\.promisor`) and was not separately measured.
- Only sha1 objects and `master` were exercised; `--branch` pinning,
  `log.follow`, `log.showRoot` and the 40-hex scanners are unchanged by this
  case and were not re-measured.
- The `--report N=PATH` draft path was not exercised (the case uses the
  committed fleet report, `report_committed: true`).
- The `protocol.allow=never` guard is a fixture-local safety net; a repaired
  auditor that needed to consult the promisor remote for any reason would be
  blocked by it (intended: it must not).

## Files

- Advice: `.ufo/waves/round-24/build/advice/CaseMarkerFleet.md` (this file).
- Artifacts: `.ufo/waves/round-24/build/out/CaseMarkerFleet/`
  - `oracle-case-marker-fleet.json` — the preregistered expectation.
  - `grid-fragment.py` — drop-in builders + rows + equality pairs.
  - `case-marker-fleet.py` — fixture builder/runner (both variants, premises,
    boundary probe).
  - `make-probe.py`, `auditor-probe.py` — scratch satisfiability probe (not
    production).
  - `run-grid-fragment.py`, `unknown-citation-probe.py` — runners.
  - `obs-base.json`, `obs-probe.json`, `obs-unknown-citation.json`,
    `obs-fragment-rows.json`, `obs-recheck.json` — observations
    (`obs-recheck.json` = end-of-seat rerun driven purely from this out
    directory; it reproduced marker==plain in both variants and boundary
    exit 2).
  - `case_marker_fleet.py` — byte-identical alias of `case-marker-fleet.py`
    (import-name alias for `unknown-citation-probe.py`).
  - `run-log.txt` — commands, versions, hashes, containment proof.
- Scratch only: `/fast/scratch/hyaku/kama-r24/CaseMarkerFleet/` (clone,
  builders, `run/<UTC>/…` fixtures, `obs/`).
