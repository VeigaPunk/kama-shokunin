# CaseMissingFleetReport — oracle case: committed fleet report blob absent in a partial clone

Reviewer: KamaR23-2.CaseMissingFleetReport-2 (leaf lane, no subagents)
Wave: round-24, base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
Subject under test: `tools/report-landing-audit.py` (round-24 promisor repair)
Host: git 2.56.0, Python 3.14.8, Linux 7.2.11-arch1-1
Artifacts: `.ufo/waves/round-24/build/out/CaseMissingFleetReport/`
(`case-missing-fleet-report.py`, `mutants.py`, `evidence/`, `mutants/`)

## Verdict: the case is specified, executed and discriminating

One offline oracle case, built and run against the base auditor, with the
expected exits/findings fixed **before** any candidate implementation existed.
The case fails the base auditor on two checks and passes the intended repair
shape, and it kills the two wrong implementations that the round-24 repair
could plausibly produce.

## 1. The case (fixture recipe, deterministic, offline)

Subject: the **fleet report blob** — the committed bytes of
`.ufo/reports/round-1/kama.md` — is committed at fleet `HEAD`, but its blob
is absent from the local object store of a partial (promisor) clone.

Recipe (all local, no network, no executed payload; see
`out/CaseMissingFleetReport/case-missing-fleet-report.py`, function `build`):

1. `lane/` — `git init -b master`; one commit `round-1: work` by
   `kama-shokunin` at author epoch 1000 → `cf56bf65fccc4ceb9371b472f84a4f93dd0a2384`.
2. `fleet-origin/` — `git init -b master`; commit `round-1: kama report` at
   epoch 2000 adding `.ufo/reports/round-1/kama.md`, whose `## Landed changes`
   cites the lane commit → fleet commit `5690301da7c95ea241a76d18cdee5e6fe0fd7abc`,
   report blob `fbda4c375e543144c3965da64143ad8a306ec6f1`.
   `git config uploadpack.allowFilter true`.
3. `fleet-partial/` — `git -c protocol.file.allow=always clone --no-checkout
   --filter=blob:none --no-local file://…/fleet-origin fleet-partial`
   → promisor metadata present (`remote.origin.promisor=true`, a
   `*.promisor` pack marker with its `*.pack` companion), **report blob
   absent locally**, commits and trees present.

The promisor remote deliberately stays a reachable **local** `file://`
origin: if the auditor ever lazy-fetched, the missing blob would materialize
locally and the run would be detectable afterwards. No `core.sshCommand`, no
remote program, no network URL is configured anywhere in this fixture.

Fixture identity is reproducible: two independent builds (work/run2,
work/run3) produced byte-identical object ids (lane `cf56bf65…`, fleet
`5690301d…`, report blob `fbda4c37…`).

## 2. Expected exits / findings (fixed before implementation)

Derived from `.ufo/waves/round-24/preregistration.json`:
*"An unavailable required commit/tree/blob/report object: exit2
could-not-evaluate, never a clean or failed verdict."* — and from the
preregistration's oracle clause "missing evidence created only by offline
local fixture setup".

| # | expectation | value |
|---|---|---|
| E1 | exit code | **2** (could-not-evaluate) |
| E2 | stdout | no verdict document, **no findings at all** |
| E3 | stderr | starts with `could-not-evaluate:` and names the unavailable required object (the report path, or `missing`/`unavailable`/`cannot read`) |
| E4 | stderr | must **not** be a promisor-metadata-only reason (`partial clone (extensions.partialclone)`, `partial clone (remote.…promisor)`, `partial clone (promisor pack)`) |
| E5 | forbidden findings | `landed-section-missing`, `landed-omitted`, `landed-unresolved`, `landed-ambiguous`, `unresolved-full-hash` must appear nowhere in stdout/stderr |
| E6 | no traceback, no timeout (bounded, own process group) | required |
| E7 | the report blob is **still absent** after the run | required (no lazy fetch) |

Forbidden verdicts, in words: **exit 1 with `landed-section-missing`** (the
missing blob read as an empty report — the harm named in this lane's target),
exit 1 with `landed-omitted` (an uncited lane commit derived from an
unreadable report), and exit 0 `clean` (the round silently skipped = guessed
completeness).

## 3. Premises — all established before the auditor runs

From `evidence/case-matrix.json` (`premises`):

| premise | observed |
|---|---|
| P1 report blob absent in the partial clone (`git --no-lazy-fetch cat-file -e fbda4c37…`) | true |
| P2 the same blob present in the origin | true |
| P3 the path is committed at the partial clone's HEAD (`rev-parse HEAD:.ufo/reports/round-1/kama.md` → `fbda4c37…`) | true |
| P4 commit and tree listing are local (`cat-file -e HEAD^{commit}`, `ls-tree -r HEAD -- .ufo/reports` lists the report) | true |
| P5 promisor metadata present (`remote.origin.promisor=true`, `pack-5b40ff94….promisor` + `pack-5b40ff94….pack`) | true |
| P6 control: the same content in the complete origin audits **clean** (exit 0, no defects, `required: 1`, `cutoff: 2000`) | true |
| P7 the partial clone is not shallow and is a top-level repository | true |

P6 matters: it proves the fixture's report is well formed and defect-free,
so any non-clean verdict in the partial clone is produced by the missing
blob, not by the fixture.

## 4. Base observation (`0df800e`) — right exit code, wrong reason

`python3 repo/tools/report-landing-audit.py --lane-repo …/lane --fleet-repo
…/fleet-partial --rounds 1 --no-errata --json`

* exit **2**
* stderr: `could-not-evaluate: …/fleet-partial: partial clone (promisor pack)`
* stdout: empty; no findings; blob still absent afterwards

The base refuses the fleet repository on **promisor metadata alone**
(`tools/report-landing-audit.py:454-457` promisor-pack marker, `:462-465`
`extensions.partialclone` / `remote.*.promisor`), before it ever looks for
the report. So the base satisfies E1, E2, E5, E6, E7 and **fails E3 and E4**:
the exit code is right only incidentally, the *reason* is the blanket
refusal that round-24 is removing. After the repair, the same fixture must
still be exit 2 — but for the evidence reason (E3/E4).

## 5. Mutant matrix — the case discriminates the wrong repairs

Mutants are the base auditor with one named change each
(`out/CaseMissingFleetReport/mutants.py`, patches in `out/.../mutants/*.patch`).

| arm | exit | findings | blob absent after | case verdict |
|---|---|---|---|---|
| base `0df800e` | 2 | – | yes | **fail** (E3, E4) |
| **M1** metadata refusal removed (the repair shape) | 2 | – | yes | **pass (all checks)** |
| **M2** unreadable report read as an empty report | 1 | `landed-section-missing`, `landed-omitted` | yes | **fail** (E1, E2, E3, E5) |
| **M3** round skipped when its report is unreadable | 0 | – | yes | **fail** (E1, E3, E5) |
| **M4** `--no-lazy-fetch` isolation dropped (negative control) | 0 | – | **no** | **fail** (E1, E3, E5, E7) |

M1 stderr (the expected repaired refusal):
`could-not-evaluate: round 1: cannot read .ufo/reports/round-1/kama.md at fleet HEAD: git show HEAD:.ufo/reports/round-1/kama.md in …/fleet-partial: rc=128 fatal: bad object HEAD:.ufo/reports/round-1/kama.md`
— the object-level unavailability of the required report blob, raised at the
base's `tools/report-landing-audit.py:308-313` (the `git show HEAD:<rel>`
read whose `EvalError` already becomes a `could-not-evaluate`), with no
findings and no fetch.

M2 stdout: `summary.status="failed"`, `by_kind.landed-section-missing=1`,
`by_kind.landed-omitted=1`, defect token
`cf56bf65fccc4ceb9371b472f84a4f93dd0a2384` — literally the "section-missing
verdict" this lane exists to forbid, produced by
`tools/report-landing-audit.py:333` from a report that was never read.

M3 stdout: `summary.status="clean"`, `reports=0` — the round vanished and
the audit claimed completeness.

M4 exists only to prove E7 has teeth: without `--no-lazy-fetch`
(`tools/report-landing-audit.py:93`, `GIT_ISOLATION`) the auditor pulls the
missing blob from the **local** `file://` origin, the blob materializes in
the partial clone (`blob_absent_after_run=false`) and the audit returns a
clean exit 0 verdict — i.e. the case detects a lost isolation flag rather
than a missing blob.

## 6. What this case does not claim

* It does not test a transport or a repository program: the only remote in
  the fixture is a local `file://` path; no `core.sshCommand`, no `gpg.*`,
  no `include.*` and no network URL is configured. M4 exercises git's own
  local fetch path, and it is a negative control, not the subject.
* It does not claim anything about missing lane commits/trees/blobs
  (sibling lanes `CaseMissingLaneTree`, `CaseMissingLaneBlob`,
  `CaseMissingAncestor`), about a missing fleet *tree*
  (`CaseMissingFleetTree`), about hydrated/complete promisor clones
  (`CaseHydratedFleet`, `CaseCompleteFleet`), about unknown or cross-repo
  citations (`CaseUnknownCitation`, `CaseCrossRepoFound`) or about marker
  metadata alone (`CaseMarkerFleet`).
* It does not close the inherited parser/alternates/gitfile/size-limit
  findings (preregistration `not_claimed`).
* It does not propose the repair itself: E3 pins the *reason class*
  (evidence-level unavailability), not a wording.

## 7. Containment

* All fixture material (lane, fleet origin, partial clone, mutants, run
  outputs) lives under
  `/fast/scratch/hyaku/kama-r24/CaseMissingFleetReport/`. The case script
  writes nothing outside its `--work` directory; it uses no `tempfile`, no
  `/tmp`.
* Base observation was taken from a scratch clone
  (`git clone --no-hardlinks … /fast/scratch/hyaku/kama-r24/CaseMissingFleetReport/repo`,
  detached at `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`); the fleet
  repository, sibling lanes, `.jj` and the lane Git index were not touched,
  and nothing was committed or pushed.
* The only writes to the lane repository are the two candidate scripts and
  the evidence under
  `.ufo/waves/round-24/build/out/CaseMissingFleetReport/`; this report is
  `.ufo/waves/round-24/build/advice/CaseMissingFleetReport.md`. No
  production file was modified.
* No tool was installed or updated by this lane (nothing to record beyond
  the host's git 2.56.0 / Python 3.14.8).

## 8. Reproduction

```
cd /fast/scratch/hyaku/kama-r24/CaseMissingFleetReport
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo
git -C repo checkout 0df800e896f6bce285a81e794ad4ae1d1e6c3a71
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/CaseMissingFleetReport
python3 $OUT/mutants.py --base repo/tools/report-landing-audit.py --outdir work/mutants
python3 $OUT/case-missing-fleet-report.py --work work/run4 \
  --auditor repo/tools/report-landing-audit.py \
  --auditor work/mutants/mutant-M1-no-metadata-refusal.py \
  --auditor work/mutants/mutant-M2-empty-report.py \
  --auditor work/mutants/mutant-M3-skip-round.py \
  --auditor work/mutants/mutant-M4-no-lazy-fetch.py
```

Script exit: 0 when every arm meets its expectation, 1 when an arm does not,
2 when the fixture premise itself could not be established. At base the
script exits **1** (the base arm fails E3/E4) — that is the intended red
state of this case before the repair lands.

## 9. Residual risk / gaps

* E3/E4 are reason-class checks, not wording checks: an implementation that
  refuses with a different but equally specific message (e.g. "promisor clone
  lacks required object …") is accepted by E3 but rejected by E4 only when
  the message is one of the three metadata-only strings listed above. A
  repair that keeps a metadata refusal *and* adds an object check would be
  accepted — deliberate, because the substantive outcome (exit 2, no
  findings) is the contract; but a reviewer should read E4 as "the reason
  must not be metadata-only", not as "the reason must be exactly this".
* The case is one fixture with one missing object (the report blob). It does
  not cover the case where the fleet report is available but a *cited* lane
  object is unavailable; that is the sibling lanes' subject.
* M4 shows that a lost `--no-lazy-fetch` is observable **only because** the
  promisor remote is a reachable local origin. Against an unreachable remote
  the same defect would produce a fetch error rather than a materialized
  blob; the case would then still see exit ≠ 2 with the reason elsewhere.
  This limitation is inherent to keeping the fixture offline.
