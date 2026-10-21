# OracleMultipleRoots — round 24 lane advice (kama)

**Scope of this lane:** `--branch` selects a lane branch whose root differs
from `HEAD`; every completeness/availability decision must be rooted at the
*selected branch*, never at `HEAD`.

**Verdict: no candidate diff existed at review time** (the wave's lane
production file `tools/report-landing-audit.py` was still byte-identical to
the r23 base — `git rev-parse 0df800e:tools/report-landing-audit.py` =
`cf706c52233139920da60f8b55d06f031286c4f9` = `git hash-object` of the working
copy, measured 2026-10-21). So the diff-review verdict is *not applicable
yet*; what is delivered here is (1) the base-state review of this axis,
(2) an independent expected-outcome oracle, (3) a bounded, fully offline
fixture recipe executed against the base arm only. Everything said about a
future candidate is a **prediction, not a measurement**.

**Base-state finding (the headline):** the lane side of the audit is *already*
rooted at the pinned selected branch. The multiple-roots hazard is therefore
not in the existing code — it is in the **new** closure/availability check the
repair must add. If that check is rooted at `HEAD` (or `--all`) instead of the
pinned selected-branch tip, it produces two opposite, easily-confused
failures: a **false clean** (missing evidence accepted) and a **false
refusal** (a complete selected branch refused). The fixture below
discriminates exactly those two.

---

## 1. Axes named (godspeed)

| # | axis | what would make it worse |
|---|------|--------------------------|
| A1 | calibration — verdict correctness at the *selected* branch root | required-commit set or evidence availability taken from `HEAD` |
| A2 | operability — a complete selected branch is auditable | blanket refusal (the r23 harm) or a closure check rooted at the wrong root |
| A3 | safety — no fetch, no transport, no repo-configured program | dropping `--no-lazy-fetch`/`--no-replace-objects`, or a check that lets git reach a promisor remote |
| A4 | no-harm — the historical ledger and the real repos are untouched | a closure check that refuses the real lane/fleet |

---

## 2. Base-state observations (path:line)

`tools/report-landing-audit.py` (base blob `cf706c52…`):

- **The selected branch is pinned to a commit, not a name** —
  `resolve_branch()` `:489-499` resolves `refs/heads/<branch>` first (a
  same-named tag cannot substitute) and returns the **tip commit sha**;
  `run()` binds it at `:516` (`tip = resolve_branch(lane_repo, args.branch)`).
- **Every lane-side read uses that pinned tip, never `HEAD`:**
  required commits `:519` → `:329` → `:189-193` (`git log -z … <tip>`);
  the source registry blob `:518` → `:258-260` (`git ls-tree <tip> -- corpus/SOURCES.md`);
  the errata ledger `:520` → `:374-383` (`git show <tip>:registry/report-landing-errata.tsv`).
- **All `HEAD` reads are fleet-side, by design** (there is no `--fleet-branch`):
  fleet report bytes `:310` (`git show HEAD:<rel>`), fleet report listing
  `:429` (`git ls-tree -r … HEAD -- .ufo/reports`), fleet HEAD existence
  `:517`, and the report first-add cutoff `:215-217` (`git log --diff-filter=A … -- <rel>`).
- **Object resolution is repository-wide, not branch-scoped** — `lookup()`
  `:139-176` runs `cat-file --batch-check` per repository over both the lane
  and the fleet repo. A locally present object is therefore found even when it
  is only reachable from another branch. This is the correct semantic and the
  repair must not change it (see finding F2).
- **The r23 harm is branch-agnostic**: `check_history_repo()` `:438-465`
  refuses any repository with a paired `.promisor` pack `:454-457`,
  `extensions.partialclone` `:462`, or a truthy `remote.*.promisor` `:463-465`
  — i.e. *metadata alone* refuses a complete local repository. That refusal
  is the thing round 24 must repair (preregistration `expected_after` #1).
- **Isolation to preserve**: `GIT_ISOLATION` `:93-97` (`--no-replace-objects`,
  `--no-lazy-fetch`, `i18n.logOutputEncoding=UTF-8`, `log.follow=false`,
  `log.showRoot=true`, `log.showSignature=false`, `log.mailmap=false`) and
  `git()` `:111-136` (scrubbed `GIT_*` env, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, 20 s per-call timeout, strict UTF-8 decode,
  `EvalError` on any non-zero rc).

---

## 3. Independent expected outcome (the oracle)

Fixture: a lane repository with **two roots** — `HEAD` = `master`
(commits `C1`@1000 `round-1: work`, `C2`@1100 `round-1: master more`) and
`refs/heads/feature` = an **orphan** commit `C3`@1200 `round-1: feature work`
(no parent ⇒ different root). The fleet report cites `C3`.
Audit invocation: `--lane-repo lane --fleet-repo fleet --branch feature
--rounds 1 --no-errata --json`.

| row | fixture | expected exit | expected findings | base arm (measured) |
|---|---|---|---|---|
| **MR-A** | sibling roots, everything present | 0 | none, `required_commits=1` | 0, none, req 1 ✅ |
| **MR-H** | selected branch **behind** `HEAD` (`feature`=`C1`), `master` has an extra uncited `round-1:` commit | 0 | none, req 1 | 0, none, req 1 ✅ |
| **MR-E** | selected branch **ahead** of `HEAD` by one uncited `round-1:` commit | 1 | `landed-omitted` (that commit), req 2 | 1, `landed-omitted`, req 2 ✅ |
| **MR-B** | promisor-marked lane, an object on the **selected** branch's closure is deleted from the store | **2** (P1) / 0 (P2) | — | 2, but only by the blanket refusal (`partial clone (extensions.partialclone)`) ❌ |
| **MR-C** | an object is missing only on `HEAD`'s branch; the selected branch is whole (no promisor marking) | 0 | none, req 1 | 0, none, req 1 ✅ |
| **MR-C2** | same as MR-C **plus** promisor marking | 0 | none | 2, blanket refusal ❌ |
| **MR-I** | promisor-marked lane; the report cites `C1`, which lives only on `HEAD`'s branch | 0 | none (the citation resolves: resolution is repository-wide) | 2, blanket refusal ❌ |
| **MR-F** | promisor marking only, every object present | 0 | none | 2, blanket refusal ❌ |
| **MR-G** | promisor-marked lane; the report cites an object that exists in **neither** repository | 2 | — (unknown, never "proved absent") | 2, but again only via the blanket refusal ❌ |

✅ = base already behaves as required; ❌ = base is the harm or the gap that
round 24 must repair.

**Policy note (the one row that is not policy-free).** Two readings of
"required object" exist and they disagree on **MR-B** only:

* **P1 (closure)** — every object reachable from the pinned selected-branch
  tip must be present locally; a missing one is unavailable evidence ⇒
  exit 2.
* **P2 (evidence)** — only the objects the audit actually reads must be
  present (walked commits, cited objects, SOURCES/errata/report blobs); a
  missing blob nobody reads is irrelevant ⇒ exit 0.

The AuditRepair lane's own target text names
`git rev-list --objects --missing=print --no-object-names` "on pinned
lane/fleet commit roots", i.e. **P1**. The grid therefore defaults to P1 and
carries `--policy P2` for the alternative; **the candidate must declare which
one it implements**, because MR-B is the only row that separates them.
Consequence of P1 that must be documented: a *legitimately blobless* partial
clone is refused (exit 2), which is the r23 grid row **T01**'s stale
expectation (`tests/report-audit/repo-state-grid.py:596-603` `t_blobless`,
row `:689`, expects exit 0) and **F23**'s stale *reason*
(`:195-215` `f_promisor_pack`, row `:670`; `REASONS` `:695-710` pins the text
`"promisor pack"` at `:704`; under the closure check the same exit 2 arrives
with a different reason). Both rows are `tradeoff`/`contract`, so the grid does
not fail on them, but the "historical parity" statement must name the change
explicitly rather than let it pass silently.

**Real-repository no-harm datum (measured, read-only):**
`git --no-lazy-fetch rev-list --objects --missing=print --no-object-names`
reports **0 missing objects** for the real lane repo
(`kama-shokunin`, `master`: 5635 objects; `--all`: 6044) and for the real
fleet repo (`/home/vgpnk/Projects/shokunin`, `HEAD`: 9374 objects; `--all`:
9402, the fleet has **12** `refs/heads/*`, so several roots really exist).
A closure check rooted at `HEAD` or at `--all` therefore cannot change any
historical verdict **today** — the root choice is a correctness matter, not a
ledger-moving one. (Command form:
`git --no-lazy-fetch rev-list --objects --missing=print --no-object-names <rev> | grep -c '^?'`.)

---

## 4. Bounded offline fixture recipe (executed, base arm only)

Artifact: `.ufo/waves/round-24/build/out/OracleMultipleRoots/multiple-roots-grid.py`
(sha256 `997fcf7ae80d8f5e7eafc119c32db80d3ac01e9fb88c5f5b6cd24f184e56dd5d`).

```
python3 .ufo/waves/round-24/build/out/OracleMultipleRoots/multiple-roots-grid.py \
    --work /fast/scratch/hyaku/kama-r24/OracleMultipleRoots/mrgrid-<arm> \
    --auditor <path to report-landing-audit.py> --policy P1 --json
```

Recipe steps (all local, no network, no execution payload):

1. `git init -q -b master` a lane repo and a fleet repo under the work dir.
2. Lane `master`: two `round-1:` commits by `kama-shokunin` at fixed author
   times; lane `feature`: an **orphan** commit built with
   `git hash-object -w --stdin` → `git mktree` → `git commit-tree` (no parent)
   → `git update-ref refs/heads/feature <sha>`; `HEAD` stays on `master`.
3. Fleet: one report commit at @2000 whose `## Landed changes` section cites
   the selected branch's commit (first-add time is the cutoff).
4. Promisor marking = metadata only: `core.repositoryformatversion=1`,
   `extensions.partialclone=origin`, `remote.origin.url=<local donor>`,
   `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`.
   The donor is a **`cp -a` copy of the lane repo made before any deletion** —
   a local path, so a lazy fetch would succeed *offline* and become
   observable as new files under `.git/objects` (the grid's `fetched_objects`
   guard). No `ssh://`, no `core.sshCommand`, no marker script.
5. "Missing object" = delete one **loose** object file from the lane store
   (`.git/objects/xx/yyyy…`). Premise is verified per row with
   `git rev-list --objects --missing=print <rev>`: the deleted oid must appear
   as `?<oid>` for exactly one root and must not appear for the other.
6. Grid guards per row: no traceback, no timeout, exit/kind match, no new
   object files (no fetch), and for verdict rows the r23 blanket-refusal text
   `partial clone` must **not** appear in stderr — a repair that silences the
   audit with the refusal it replaces fails the row.

Measured base arm (auditor = base blob `cf706c52…`, git 2.56.0):

```
MR-A-multi-root-complete              exit=0 want 0 kinds=[]            req=1  met
MR-H-selected-behind-head             exit=0 want 0 kinds=[]            req=1  met
MR-E-selected-ahead-uncited           exit=1 want 1 kinds=[landed-omitted] req=2 met
MR-B-missing-on-selected-root         exit=2 want 2  forbidden="partial clone"   NOT-MET
MR-C-missing-on-head-root             exit=0 want 0 kinds=[]            req=1  met
MR-C2-promisor-missing-on-head-root   exit=2 want 0  forbidden="partial clone"   NOT-MET
MR-I-citation-outside-selected-root   exit=2 want 0  forbidden="partial clone"   NOT-MET
MR-F-promisor-metadata-only           exit=2 want 0  forbidden="partial clone"   NOT-MET
MR-G-promisor-unknown-citation        exit=2 want 2  forbidden="partial clone"   NOT-MET
```

Raw JSON: `.ufo/waves/round-24/build/out/OracleMultipleRoots/base-arm-P1.json`
and `base-arm-P2.json` (P2 differs only in MR-B, which the base passes with
exit 0).

Supporting probes (also artifacts): `probe3.sh` (missing *ancestor commit* in
a promisor-marked repo) and `probe4.sh` (a lazy fetch from a local donor is
observable as new pack files under `.git/objects`).

---

## 5. Findings for the repair (severity order)

**F1 — HIGH: the closure check must be rooted at the pinned selected-branch
tip, not at `HEAD` and not at `--all`.** `resolve_branch()` `:489-499` and
`run()` `:516` already hand the implementer the pinned tip; the new
availability check must use that exact revision (and the pinned fleet HEAD
`:517` for the fleet side). A `HEAD`-rooted lane check produces *both* wrong
answers: MR-B (missing evidence on the selected branch → false clean/exit 0
or 1 instead of exit 2) and MR-C2 (complete selected branch, missing object
on another root → false refusal exit 2). `--all` is wrong for the same reason
(the real fleet repo has 12 branches). *Evidence:* grid rows MR-B/MR-C/MR-C2;
`--branch feature` is passed to the auditor by the grid.

**F2 — HIGH: object resolution must stay repository-wide.** A citation that
resolves to an object present in the lane store must stay "found" even when
that object is outside the selected branch's closure (MR-I). Scoping the
lookup to the branch closure would turn a resolvable citation into "unknown"
(exit 2) or "absent" (exit 1). The base's `lookup()` `:139-176` is
repository-wide and is the correct semantics; the preregistration's "unknown
citation … exit2 **unless resolved locally by another audited repository**"
matches it. *Evidence:* MR-I; base `lookup()` `:139-176`.

**F3 — MEDIUM: the required-commit set must keep coming from the pinned tip.**
`round_commits()` `:189-193` is fed the tip through `:329`; MR-E/MR-H prove
the base already does this (req 2 / req 1). Any refactor of the closure or
promisor handling that re-roots the commit walk on `HEAD` silently flips
MR-E to a false clean and MR-H to a false failed. Keep `git log <tip>`.

**F4 — MEDIUM: the closure policy must be declared, and its expectation
changes must be documented, not silently inherited.** P1 vs P2 differ on
MR-B; P1 additionally makes r23's `T01` (blobless partial clone, documented
expectation exit 0, `tests/report-audit/repo-state-grid.py:596-603` and row
`:689`) and F23's pinned reason `"promisor pack"` (`:195-215`, row `:670`,
`REASONS` `:695-710`, entry `:704`) stale.
The measurement section of the preregistration already allows "explicitly
documented policy-row expectation changes"; that documentation must exist.

**F5 — MEDIUM: promisor state detection must not become a refusal again.**
The repair prompt names `partialclonefilter` and *paired* markers as
promisor-state signals. My rows exercise `extensions.partialclone` +
`remote.origin.promisor` + `remote.origin.partialclonefilter` + a real
`objects/pack/*.promisor` marker would be produced by any fetch — so the
detection must be state-based (config/filter/marker), not "a pack exists".
The grid's `forbidden_reason_seen` guard makes any relapse into the blanket
refusal visible (MR-C2/MR-I/MR-F/MR-G).

**F6 — MEDIUM: `--no-lazy-fetch` is load-bearing for the new check.**
`GIT_ISOLATION` `:93-97` is what makes the closure probe and the citation
lookup offline. Measured: `git cat-file --batch-check` **without**
`--no-lazy-fetch` on a missing object in a promisor repo performs a lazy
fetch (probe4: it fetched from the local donor and restored the object,
writing a new pack plus a `.promisor` marker into the lane store);
`git rev-list --objects --missing=print` printed `?<oid>` without fetching in
both the promisor and the non-promisor case (probes 1-3), but that must not
be relied on as the only barrier. The grid's `fetched_objects` guard turns a
lost `--no-lazy-fetch` into a failed row.

**F7 — LOW (fleet-side, adjacent lane): the fleet closure root is the fleet
`HEAD` `:517`, and the fleet closure from `HEAD` spans the whole fleet
history (9374 objects, 12 branches).** Any blob missing anywhere in that
history becomes "unavailable evidence" → exit 2 → a refusal of an otherwise
complete fleet. Measured: the real fleet closure currently has 0 missing
objects, so nothing moves today, but the fleet lanes (CaseCompleteFleet,
CaseMissingFleetTree/Blob) own this row, not this one.

**F8 — INFO: the base is not wrong about `HEAD` on the fleet side.** The
fleet report bytes are read at fleet `HEAD` `:310` and the cutoff at `:215-217`;
there is no `--fleet-branch`. A candidate that introduces one must keep the
default equal to today's `HEAD` behaviour, or the historical ledger's cutoff
semantics shift.

---

## 6. Residual risk and verification gaps

* **No candidate was reviewed.** Every statement about the repair is a
  prediction from the base code plus the preregistration/assignment text.
  Unrun ⇒ unverified.
* **The grid was executed only against the base arm** (`--arm base`), and only
  the rows listed above. It is not the wave's `tests/report-audit/promisor-grid.py`
  (that file is the GridOracle lane's deliverable); mine is an independent
  oracle with a different axis (multiple roots) and can be run beside it.
  Two independent runs into two fresh work dirs produced identical
  (exit, kinds, required, fetched, forbidden) tuples for all nine rows —
  deterministic (measured).
* **A *failed* lazy fetch is not observable by my fixture**: with a local
  donor, a failed fetch adds no objects, so only a *successful* fetch is
  caught. Execution of repo-configured programs is covered by the r23 grid
  rows F06/F27 (marker scripts) — deliberately not reproduced here (no
  execution payload in this lane).
* **Policy row**: MR-B's expected exit depends on P1/P2; the grid carries
  both. If the candidate implements P2, run the grid with `--policy P2`.
* **Not covered here**: sha256 repositories, `objects/info/alternates`, `.git`
  gitfile redirection, `info/grafts`, shallow repositories, `--report` draft
  audits against a promisor-marked lane, non-UTF-8 git output, the
  `git log`/`ls-tree` timeout path, and every fleet-side row except the
  read-only completeness measurement quoted above.
* **Cross-lane coordination**: the r23 grid's T01/F23 rows and the
  `REASONS` map will need the documented policy change (F4); the GridOracle
  lane should be told that the multiple-roots axis has its own oracle
  (artifact path above) so the two are not confused.

---

## 7. Named files

* Advice: `.ufo/waves/round-24/build/advice/OracleMultipleRoots.md` (this file).
* Oracle/fixture grid: `.ufo/waves/round-24/build/out/OracleMultipleRoots/multiple-roots-grid.py`.
* Base-arm evidence: `.ufo/waves/round-24/build/out/OracleMultipleRoots/base-arm-P1.json`,
  `…/base-arm-P2.json`, `…/base-arm-P1.err` (empty).
* Probes: `.ufo/waves/round-24/build/out/OracleMultipleRoots/probe3.sh`,
  `…/probe4.sh`.
* Scratch (not part of the deliverable): `/fast/scratch/hyaku/kama-r24/OracleMultipleRoots/`
  (`mrgrid-base/`, `mrgrid-base-p2/`, `probe1/`…`probe4/`, `summarize.py`).
* Reviewed production file (unmodified by me):
  `tools/report-landing-audit.py` (base blob `cf706c52233139920da60f8b55d06f031286c4f9`).
* No packages were installed or updated in this lane; git 2.56.0 and
  python3 (stdlib only) were already present.
