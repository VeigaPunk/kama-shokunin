# CaseUnknownCitation — provenance, containment and premise evidence

Round 24, leaf lane `CaseUnknownCitation`. Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(preregistration `.ufo/waves/round-24/preregistration.json`).

## 1. What the case is

A fleet report cites a full 40-hex commit that is **absent from both audited
repositories** while the audited lane is **promisor-backed** and the cited
commit **exists in the lane's promisor remote**. Local absence therefore
proves nothing: the outcome must be could-not-evaluate (exit 2) and must
**not** be reported as an `unresolved-full-hash` defect.

Policy source (preregistration `expected_after`):

* `[3]` "An unavailable required commit/tree/blob/report object: exit2
  could-not-evaluate, never a clean or failed verdict."
* `[4]` "A missing citation in any promisor-backed repository is unknown, not
  proved absent: exit2 unless resolved locally by another audited repository."
* `[6]` "Metadata-only declarations do not establish incompleteness; content
  completeness and availability of required evidence determine the outcome."

The expectation file `expected.json` was written **before** the base
auditor was run and before any candidate existed.

## 2. Arms

| arm | lane | fleet | required outcome | base 0df800e observed |
|---|---|---|---|---|
| A-main | `lane-filter`: `remote.origin.url` + `remote.origin.partialclonefilter=blob:none` | `fleet`: report cites the unknown commit in `## Notes` | exit 2, no defect kinds | exit 1, `["unresolved-full-hash"]` (token `29e8ea69…`) |
| B-control | same `lane-filter` | `fleet-clean`: same report without the unknown citation | exit 0, no defect kinds | exit 0, no defect kinds |
| C-full | `lane-full`: `+ extensions.partialclone=origin` + `remote.origin.promisor=true` | `fleet`: report cites the unknown commit in `## Notes` | exit 2, no defect kinds | exit 2, `could-not-evaluate: … partial clone (remote.origin.promisor)` |
| D-store-lane | `lane-filter` + a commit object present in the store but unreachable from the pinned root | `fleet-side`: report cites that object in `## Notes` | exit 0, no defect kinds | exit 0, no defect kinds |
| E-store-full | `lane-full` + the same store-positive object | `fleet-side` | exit 0, no defect kinds | exit 2, `could-not-evaluate: … partial clone (remote.origin.promisor)` |

A-main and B-control are one pair: the same promisor lane, the same report
except for the one unknown citation. A-main exit 2 **together with** B-control
exit 0 is what attributes the refusal to the unknown citation and not to the
promisor metadata. No refusal wording is pinned, so the expectation is not
coupled to the candidate's message text.

D/E are the **witness row**: a citation that is in the lane's object store but
not reachable from the pinned root must be *found*, not unknown. Without them,
A/B/C do not falsify an implementation that decides "unknown citation" by
enumerating the closure (the unknown sha is unreachable too, so such an
implementation reaches the same answer). The hole was found in review by the
`CaseMissingAncestor` lane; the witness object is `064ab85244cfa7f72ca54449e69e19cffb03aa9b`,
present in `lane-filter` and `lane-full`, absent from every fleet, and listed
**0 times** by `rev-list --missing=print --objects --no-object-names master`.

The unknown citation sits in `## Notes`, not in `## Landed changes`, so the
only defect kind that could ever be produced for it is `unresolved-full-hash`
(the full-hash scan). `landed-unresolved` / `landed-ambiguous` cannot fire.

## 3. Fixture (reproducible)

Builder: `build_case.py` (deterministic: fixed names, fixed author/committer
times, fixed content). Runner: `run_case.py`. Scratch root:
`/fast/scratch/hyaku/kama-r24/CaseUnknownCitation/` (fixture in `fixture/`).

```
fixture/origin/       lane's promisor remote: O1 (cited, local) + O2 (never fetched)
fixture/lane/         lane base copy: O1 only
fixture/lane-filter/  A-main + B-control + D-store-lane lane (filter-only promisor remote)
fixture/lane-full/    C-full + E-store-full lane (canonical partial-clone configuration)
fixture/fleet/        round-1 report citing O1 (Landed) and O2 (Notes)
fixture/fleet-clean/  round-1 report citing O1 only
fixture/fleet-side/   round-1 report citing O1 (Landed) and the witness object (Notes)
```

Resolved ids (also in `fixture-manifest.json`):

* O1 `db796f8b820bf3825c58832419138cdba23206a7` — cited, present in both lanes.
* O2 `29e8ea69cc44bbb72af22255c5231a7d13b577e0` — the unknown citation;
  a commit in `origin`, absent from `lane`, `lane-filter`, `lane-full`,
  `fleet`, `fleet-clean`.
* W `064ab85244cfa7f72ca54449e69e19cffb03aa9b` — the witness object: a
  commit in the store of `lane-filter` and `lane-full`, unreachable from
  `refs/heads/master`, absent from every fleet.

Report first-add cutoff: fleet commit `f82060d5f7b8aba52b61cb2216ed8740a27b2383`,
author time 2000. Lane required commit: O1, author time 1000, subject
`round-1: work`, cited in `## Landed changes` → no `landed-omitted`.

## 4. Premises actually observed (git 2.56.0, offline)

1. `git -C fixture/origin cat-file -t 29e8ea69…` → `commit`: the cited object
   **exists in the promisor remote's store**; the lane simply never fetched it.
2. `git --no-lazy-fetch -C fixture/lane-filter cat-file -e 29e8ea69…` → absent;
   same for `lane-full`, `fleet`, `fleet-clean`.
3. Closure of the pinned lane root is **complete**:
   `git --no-lazy-fetch -C fixture/lane-filter rev-list --objects --missing=print --no-object-names master`
   lists exactly 3 objects and **no** `?`-prefixed missing line (same for
   `lane-full`). So the case is *not* a required-object case: the only thing
   that can make it exit 2 is the unknown-citation rule `[4]`. The
   closure-scope policy (required-objects-only vs whole-closure) therefore
   cannot change this case's outcome — it is decided by the citation rule.
4. Premise that local absence is uninformative (probe in `premise-probe.txt`,
   local `file://` to a **nonexistent** path, no network, no script, no data
   transfer): in a repo with `remote.origin.url` +
   `remote.origin.partialclonefilter=blob:none`, a plain
   `git cat-file -e <missing>` makes git **ask the promisor remote**
   (`fatal: Could not read from remote repository`), while
   `git --no-lazy-fetch cat-file --batch-check` answers `missing` with rc 0.
   Hence: git itself treats such a repository as promisor-backed; the
   auditor's `--no-lazy-fetch` isolation is what makes the *absence*
   observable, and the auditor — not git — must decide that the absence is
   unknown rather than proved.
5. No fetch during the audit: after every arm run the lane still lacks O2,
   has no new pack and no `FETCH_HEAD` (`run_case.py` reports
   `fetch_observed=false` for all three arms, base and candidate alike).

## 5. Containment proof (no fixture escaped the scratch)

* The builder writes through `Builder.guard()`, which raises `BuildError` for
  any path not under the fixture root. Negative test executed:
  `guard('/tmp/escape-attempt')` → `BuildError: write escapes fixture root`.
* `fixture-manifest.json` lists all 132 written paths; the check
  "path not under root" returns **0** offenders.
* `run_case.py` re-checks containment independently: every audited repo's
  `rev-parse --show-toplevel` equals the fixture path, every
  `remote.origin.url` resolves under the root, and no lane has
  `.git/objects/info/alternates` → `containment_problems=[]`.
* Nothing was written to `/tmp`; the heavy fixture (1.2 MiB) lives only under
  `/fast/scratch/hyaku/kama-r24/CaseUnknownCitation/`.
* The production repository was not modified by this lane. At the time of
  writing, `git status` in the lane repo shows `M LOG.md` and the untracked
  wave directories — both from L1's own round-24 integration commit
  `d1b9d95` (which touches no file under `tools/` or `tests/`; the auditor
  under test is still byte-identical to the base).

## 6. Reproduction

```sh
ROOT=/fast/scratch/hyaku/kama-r24/CaseUnknownCitation
OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/CaseUnknownCitation
python3 "$OUT/build_case.py" --root "$ROOT/fixture" --reset
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show \
    0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py \
    > "$ROOT/base-audit.py"
python3 "$OUT/run_case.py" --root "$ROOT/fixture" --auditor "$ROOT/base-audit.py" \
    --label base-0df800e --expected "$OUT/expected.json" --json
# candidate: same command with --auditor <candidate tools/report-landing-audit.py>
```

`run_case.py` exits non-zero if any arm misses its expectation, if the
containment check fails, or if a fetch was observed.
