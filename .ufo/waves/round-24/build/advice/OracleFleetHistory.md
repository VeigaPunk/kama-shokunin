# OracleFleetHistory — r24 C1 promisor repair: fleet-history / first-add-cutoff oracle

**Lane:** `KamaR23-2.OracleFleetHistory-2` (reviewer/oracle, leaf — no subagents dispatched)
**Base observed:** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (scratch clone `repo/`, detached)
**Scratch (all heavy files):** `/fast/scratch/hyaku/kama-r24/OracleFleetHistory/`
**Artifacts:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/OracleFleetHistory/`
**Production edits:** none — this lane produced no code change; no candidate existed to run.

---

## 1. Verdict

**The first-add cutoff survives the promisor repair only if the candidate keeps two things apart:
(a) the fleet *cutoff* (the author time of the fleet commit that **first** added the report, i.e. the
topologically first add, not the re-add and not the tip), and (b) the fleet *report bytes* (the blob at
HEAD).** A promisor-marked but content-complete fleet must reproduce its plain twin **exactly**
(exit code, cutoff value, required set, post-report set, defect list). A marked fleet whose *history*
is incomplete must be refused as **exit 2 with a content-derived reason** — never by metadata, never by
a verdict.

The r23 harm is reproduced on the fixture below: the frozen base refuses three complete marked fleets
with `partial clone (remote.origin.promisor)` / `partial clone (promisor pack)` (exit 2) although the
same repositories are byte-for-byte complete and their plain twins produce clean/failed verdicts.

**Confidence:** high for the cutoff/parity expectations (measured against the frozen base and raw git
plumbing). The one open policy point is the missing *historical* blob case (§6) — the expected outcome
is stated, the acceptable alternative is stated, and both are unverified against a candidate because
no candidate exists yet.

---

## 2. Axes named

| axis | property under test |
|---|---|
| **A1 cutoff** | cutoff = author time of the fleet commit that first added the report (topologically first add). Not the re-add (3000), not the newest add, not the minimum author time, not the tip, not a working-tree mtime. |
| **A2 marked≡plain** | promisor **metadata** (config key or paired `.promisor`/`.pack` marker) must not change any substantive output: exit, cutoff, `required`, `post_report`, `defects`. |
| **A3 completeness scope** | the required-object check must cover the **whole closure of the fleet evidence root** (its history), not only the tip tree. A missing *historical* object must be detected. |
| **A4 no harm** | the frozen (plain, non-promisor) outcomes must be reproduced verbatim by the current arm; no lazy fetch, no transport invocation, no signature verification, no replace-ref substitution, no deadline change. |

---

## 3. The case (fixture recipe)

Builder: `out/OracleFleetHistory/build_ofh.py` (deterministic; fixed author/committer names, e-mails and
epoch times ⇒ fixed object ids). Recipe summary:

```
fleet repo (linear, branch master, report path .ufo/reports/round-1/kama.md)
  F1  author-time 1000  "round-1: kama report"        ADD    report blob v1
  F2  author-time 2000  "round-1: drop report"         DELETE report
  F3  author-time 3000  "round-1: re-add report"       ADD    report blob v2
  F4  author-time 4000  "round-1: drop report again"   DELETE report
  F5  author-time 5000  "round-1: re-add report again" ADD    report blob v2
  (two delete/readd cycles: the cutoff must stay the FIRST add, not the newest
   re-add 5000 and not the last add before a delete 3000)
lane repo (branch master, author kama-shokunin)
  alpha 66dbbead34edb3c94ef25757657dacb951a94dfe  t=500   "round-1: alpha"   (cited in report as 66dbbea)
  beta  03b3e245662c564d0203f22c727f6ce4ae2f3ad0  t=1500  "round-1: beta"    (uncited)
  gamma 975aebfdf92fc0b9f2751d9a9330dc5487cb5aa5  t=2500  "round-1: gamma"   (uncited)
  foreign ce760034065667ef38ccb053077436766d1ae0c4 t=1600 "round-1: foreign author" (author someone → ignored)
  other   06488039699b085505edc49338ec35a438f5a9a2 t=1700 "round-10: other round"     (other round → ignored)
```

Fixture roots (all under `/fast/scratch/hyaku/kama-r24/OracleFleetHistory/fixtures/out/`, rebuilt with
`python3 build_ofh.py`):

| fixture | marking | content | purpose |
|---|---|---|---|
| `lane` | — | complete | plain lane (lane-side marking is another lane's case) |
| `fleet_plain` | none | complete | reference: the substantive verdict a marked twin must reproduce |
| `fleet_marked_cfg` | `remote.origin.promisor=true` (+`remote.origin.url=https://example.invalid/fleet.git`) | complete | A2: config-marked, complete ⇒ must equal `fleet_plain` |
| `fleet_marked_pack` | paired `objects/pack/pack-*.promisor` + `pack-*.pack`, **no** promisor config | complete (repacked) | A2: marker-only marking ⇒ must equal `fleet_plain` |
| `fleet_hist` | none | complete, report **v1 ≠ v2** (v2 adds a 40-hex token `0123456789abcdef0123456789abcdef01234567`) | reference for A1/HEAD-bytes: failed verdict |
| `fleet_hist_marked_cfg` | config-marked | complete, v1 ≠ v2 | A2 on the **failed** side ⇒ must equal `fleet_hist` |
| `fleet_hist_missing` | config-marked | **first-add blob `6d06f68c89213cb1fca438aa91f5b61a39dabc4a` deleted** | A3: incomplete history, complete tip ⇒ must be exit 2 |
| `fleet_skew` / `fleet_skew_marked_cfg` (+ `lane_skew`) | none / config-marked | complete; re-add carries author-time **500** (earlier than the first add 1000); `lane_skew` has an extra uncited commit `10c475bac3d7543111638f968aa37164adf46fb5` at t=700 | A1 sharpness: distinguishes "topologically first add" (1000) from "minimum author time" (500) |

Report blobs: v1 = `6d06f68c89213cb1fca438aa91f5b61a39dabc4a`; v2 (hist) =
`87a06f716a222a7fa8cccbbb414b9d4355129761`; fleet commits (plain) F1
`8b0559d8407ec5bb93f95b1438ff3f885b3bea46` (1000), F2 `603bcebae02a896bcdbeb27cee2f2348ae75f782`
(2000), F3 `a1ad0b24dbb20635537ec08d04af5b2c9e2ef6b9` (3000), F4
`fedc57e8c3997105766d60bf9556e703e49dad97` (4000), F5 `6be21321a5b65214774a19b5ba19cafef344b634`
(5000); the `fleet_hist` twin has the same F1/F2 and F3 `74b6ae90cafadb360b3ff6919d3e18132630ab29`,
F4 `772d84fba9c29f31cf819d5446532cd9f09d9f7b`, F5 `1a82d8215d18ff5e7b937257dcaa08c2604887ae`;
skew re-add F3 `7603d7928dd1e683b9fb14eb0e557d0912f6d1b8` (500).

**No fixture escaped scratch:** the builder refuses any root outside
`/fast/scratch/hyaku/kama-r24/OracleFleetHistory` (hard-coded `ALLOWED` check in `build_ofh.py`), and
the main checkout gained only `.ufo/waves/round-24/build/` (this report + `out/`). No network, no
transport command, no execution payload: the only remote URL present is the non-resolvable
`https://example.invalid/fleet.git`, never contacted (see M9 below).

---

## 4. Measured facts (bounded git plumbing, `out/OracleFleetHistory/measure_ofh.log`)

All commands were run with the tool's isolation flags
(`--no-replace-objects --no-lazy-fetch -c log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`).

* **M1/M1b** `git log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md` in `fleet_plain` →
  `5000`, `3000`, `1000`. The audit's `report_cutoff` takes the **last** entry
  (`tools/report-landing-audit.py:215-217`), i.e. **1000 = the first add**, while the newest re-add
  (5000) is the *first* entry and the intermediate re-add (3000) sits in the middle. Neither re-add can
  become the cutoff.
* **M2** the whole path history is
  `re-add(5000) / drop(4000) / re-add(3000) / drop(2000) / add(1000)`: two delete/readd cycles are
  present, so a tip-only or newest-add reading would take 5000 and a "last add before the newest delete"
  reading would take 3000.
* **M3/M5** closure scan `git rev-list --objects --missing=print --no-object-names HEAD`:
  `fleet_marked_cfg` → 0 missing lines; `fleet_marked_pack` (paired `.promisor`+`.pack` markers, no
  config) → 0 missing lines. Both are complete ⇒ a content-based completeness check does **not** refuse
  them.
* **M4** the marked config twin yields the identical add list `5000, 3000, 1000` as the plain twin ⇒ marking
  does not change the cutoff source.
* **M6** `fleet_hist_missing` (first-add blob deleted): the closure scan reports
  `?6d06f68c89213cb1fca438aa91f5b61a39dabc4a` (1 missing), while the **tip-only** scan
  (`git ls-tree -r HEAD` → `87a06f71…` + `cat-file --batch-check`) reports **nothing missing**, and
  `git show HEAD:.ufo/reports/round-1/kama.md` succeeds. ⇒ a tip-tree-only check cannot see the
  missing historical object; only a closure scan can. This is the operational meaning of
  *"(not tip-only object checks)"*.
* **M6 (cont.)** in the same repo `git log --diff-filter=A --format='%H %at' -- <report>` still succeeds
  offline (rc=0, all three add commits: 5000, 3000, 1000) — the add list does not need the deleted blob.
* **M9** reading the missing object with the isolation flags fails *without any fetch attempt*:
  `git show 8b0559d8…:.ufo/reports/round-1/kama.md` → `fatal: bad object …` (rc=128),
  `git cat-file blob 6d06f68c…` → `fatal: git cat-file 6d06f68c…: bad file` (rc=128). `--no-lazy-fetch`
  holds; `remote.origin.url` was `https://example.invalid/fleet.git` and was never contacted.
* **M10** `fleet_skew`: the add list is `7603d79… 500` (re-add) then `8b0559d8… 1000` (first add) — git's
  default `--date-order` keeps children before parents, so the **last** entry is the *topologically first
  add* (1000), not the minimum author time (500). The skew twin is complete (0 missing).
* **M11** `lane_skew`: alpha 500, mid 700, beta 1500, gamma 2500 (all `kama-shokunin`, round-1).

Completeness/marking table (`rev-list --objects --missing=print … | grep -c '^?'`):

```
lane                   missing=0   promisor_cfg=-      promisor_markers=0
fleet_plain            missing=0   promisor_cfg=-      promisor_markers=0
fleet_marked_cfg       missing=0   promisor_cfg=true   promisor_markers=0
fleet_marked_pack      missing=0   promisor_cfg=-      promisor_markers=1
fleet_hist             missing=0   promisor_cfg=-      promisor_markers=0
fleet_hist_marked_cfg  missing=0   promisor_cfg=true   promisor_markers=0
fleet_hist_missing     missing=1   promisor_cfg=true   promisor_markers=0
fleet_skew             missing=0   promisor_cfg=-      promisor_markers=0
fleet_skew_marked_cfg  missing=0   promisor_cfg=true   promisor_markers=0
```

---

## 5. Expected outcome table (frozen reference vs. required candidate behaviour)

Frozen reference = the **base 0df800e** tool on the *plain* fixtures
(`out/OracleFleetHistory/base_behaviour.log`; command
`python3 repo/tools/report-landing-audit.py --lane-repo <lane> --fleet-repo <fleet> --branch master --lane kama --rounds 1 --no-errata --json`).
The candidate does not exist yet ⇒ every "candidate" column below is **unverified**.

| # | fixture | frozen base | **required candidate** | cutoff | required | post_report | defects |
|---|---|---|---|---|---|---|---|
| OFH-1 | `fleet_marked_cfg` | exit 2 `partial clone (remote.origin.promisor)` | **exit 0 clean**, identical to `fleet_plain` | 1000 | 1 | `975aebfd…`(2500), `03b3e245…`(1500) | none |
| OFH-1b | `fleet_marked_pack` | exit 2 `partial clone (promisor pack)` | **exit 0 clean**, identical to `fleet_plain` | 1000 | 1 | `975aebfd…`, `03b3e245…` | none |
| OFH-2 | `fleet_hist_marked_cfg` | exit 2 (metadata refusal) | **exit 1 failed**, identical to `fleet_hist` | 1000 | 1 | `975aebfd…`, `03b3e245…` | `unresolved-full-hash 0123456789abcdef0123456789abcdef01234567` |
| OFH-3 | `fleet_hist_missing` | exit 2 (metadata refusal) | **exit 2 could-not-evaluate, content-derived**: the message must identify the missing object `6d06f68c89213cb1fca438aa91f5b61a39dabc4a` (or at minimum state that a *required object is missing*), **not** the r23 metadata sentence `partial clone (remote.origin.promisor)` | — | — | — | — |
| OFH-4 | `fleet_skew_marked_cfg` | exit 2 (metadata refusal) | **exit 1 failed**, identical to `fleet_skew` | 1000 | 2 | `ee124a68…`(2500), `ec3ce607…`(1500) | `landed-omitted 10c475bac3d7543111638f968aa37164adf46fb5` (`cited_elsewhere:false`) |
| REF-1 | `fleet_plain` | exit 0, cutoff 1000, required 1, post_report 2, no defects | **unchanged** (non-promisor no-harm) | 1000 | 1 | `975aebfd…`, `03b3e245…` | none |
| REF-2 | `fleet_hist` | exit 1, defect `unresolved-full-hash 0123…4567` | **unchanged** | 1000 | 1 | `975aebfd…`, `03b3e245…` | as above |
| REF-3 | `fleet_skew` | exit 1, `landed-omitted 10c475b…` | **unchanged** | 1000 | 2 | `ee124a68…`, `ec3ce607…` | as above |

Frozen base summary of the "before" arm (`base_behaviour.log`): `fleet_plain` exit 0 · `fleet_marked_cfg`
exit 2 · `fleet_marked_pack` exit 2 · `fleet_hist` exit 1 · `fleet_hist_marked_cfg` exit 2 ·
`fleet_hist_missing` exit 2 · `fleet_skew` exit 1 · `fleet_skew_marked_cfg` exit 2.
⇒ The r23 blanket refusal hits **four** fixture fleets that are either complete (O1, O1b, O2, O4) or
genuinely incomplete but for a *content* reason (O3).

Note on OFH-2: the marked twin must reproduce the **failed** verdict, not only the clean one — the
prereg's expected_after requires "exact same substantive clean/**failed** findings as otherwise
identical full clones".

---

## 6. Mutant discrimination (for the mutation lane)

| mutant | fixture that kills it | expected kill signature |
|---|---|---|
| cutoff = newest add (`out[0]`, 5000) | OFH-1 | exit 1 with `landed-omitted` for `03b3e245…`(1500) and `975aebfd…`(2500) instead of exit 0 |
| cutoff = last add before the newest delete (3000) | OFH-1 | exit 1 with the same two omissions instead of exit 0 |
| cutoff = minimum author time among adds (500) | OFH-4 | exit 0 (required 1, no omission) instead of exit 1 with `landed-omitted 10c475b…` |
| cutoff = tip / worktree mtime | OFH-1 | cutoff ≠ 1000 ⇒ required set changes ⇒ wrong exit or wrong `required` count |
| metadata-only refusal (r23 as-is, `check_history_repo` lines 438-466) | OFH-1, OFH-1b, OFH-2, OFH-4 | exit 2 instead of 0/0/1/1 |
| tip-tree-only completeness check (`ls-tree -r HEAD` + `cat-file`) | OFH-3 | exit 0/1 (a verdict) instead of exit 2 |
| no completeness check at all | OFH-3 | same as above |
| report bytes taken from the **first-add** blob instead of HEAD | OFH-2 | exit 0 (no `unresolved-full-hash`) instead of exit 1 |
| refusal reason derived from metadata even when the content is incomplete | OFH-3 | message `partial clone (remote.origin.promisor)` instead of a missing-object message ⇒ *same exit, wrong reason* — the mutation harness must compare the message, not only the exit code |
| lazy fetch / transport re-enabled (remove `--no-lazy-fetch`) | static-only | must **not** be executed: the fixture's promisor remote is `https://example.invalid/fleet.git`; the flag must be checked statically, never triggered |

---

## 7. Residual risk / open policy point (one, explicitly)

**The missing *historical* blob (O3).** The prereg names the mechanism
("`git rev-list --objects --missing=print --no-object-names` on pinned lane/fleet commit roots") and the
rule ("an unavailable **required** object evidence ⇒ exit 2"), while M6 shows that the audit's own
traversal (the add list) still succeeds offline without that blob. Two defensible candidate behaviours:

* **Primary expectation (declared here): exit 2, content-derived.** The fleet evidence root is the
  first-add commit (the cutoff source) and HEAD (the report bytes); the first-add blob lies in the
  closure of the first-add commit, so the required closure is not available ⇒ exit 2. The reason must
  name the missing object.
* **Narrow alternative (acceptable only with documentation): exit 0 with cutoff 1000**, if the candidate
  documents that the missing blob is never read by the audit *and* shows that the cutoff was established
  from the first add without fetching (M6 shows git can). A candidate that returns a verdict while the
  closure is provably incomplete, *without* that documentation, is a defect.
* **Never acceptable:** exit 1 (a failed verdict) for O3, or exit 2 whose reason is the promisor
  metadata.

Root-choice robustness: pinning the fleet completeness root at HEAD or at the first-add commit gives the
same answer for every fixture here (HEAD's closure contains the first-add blob), so the expectations
above do **not** depend on that choice — only a tip-tree-only scan does (M6).

Inherited behaviour that must **not** change in this wave (prereg `not_claimed`: inherited findings are
not closed here): the cutoff is `min`-over-add-list-of-`git log --diff-filter=A` **in git's default
`--date-order`**, which yields the topologically first add (M1/M10). The current arm must reproduce the
frozen cutoff values (1000 in REF-1/2/3) exactly; a "cleanup" that re-derives the cutoff by
`--reverse`/topo/min-time and changes those numbers is a behaviour change, not a repair.

---

## 8. Verification gaps (unrun ⇒ unverified)

* **No candidate was run** — none exists; every "required candidate" cell in §5 is a specification, not
  an observation.
* **No full-suite / grid / selftest run** (out of scope for this lane and prohibited by the assignment).
* The frozen-base numbers in §5 come from the **base** tool in the scratch clone at `0df800e`
  (`repo/tools/report-landing-audit.py`), i.e. the "before" arm — not the candidate.
* The `--no-lazy-fetch` behaviour was verified only by M9 (a missing object fails without contacting
  the remote). No network was available or used; the "no transport invocation" property of the candidate
  is therefore **unverified** by execution and can only be checked statically.
* Whether the candidate pins the fleet completeness root at HEAD or at the first-add commit was not
  observable (no candidate); §7 shows the expectations are root-choice independent.
* Interaction with the lane-side marking (a promisor-marked **lane**) is out of this lane's scope
  (`CaseCompleteLane`/`CaseMarkerLane`); the lane here is plain and complete in every fixture.

---

## 9. Files

Named artifacts (copied to `.ufo/waves/round-24/build/out/OracleFleetHistory/`):

* `build_ofh.py` — deterministic offline fixture builder (recipe; refuses roots outside the scratch).
* `measure_ofh.sh` / `measure_ofh.log` — bounded git-plumbing premise measurements (M1-M11).
* `base_behaviour.sh` / `base_behaviour.log` — frozen-base (0df800e) outputs for all eight fleet fixtures.
* `facts.json` — fixed object ids, times and paths of the fixture (copy of `fixtures/out/facts.json`).

Code under review (base): `tools/report-landing-audit.py:215-217` (`report_cutoff`, the
`git log --diff-filter=A --format=%at` add-list whose last entry is the first add),
`tools/report-landing-audit.py:302-357` (`audit_round`: cutoff use, `pre`/`post` split at lines 330-331,
HEAD report bytes at 306-313), `tools/report-landing-audit.py:438-466` (`check_history_repo`: the r23
blanket promisor refusals — pack marker at 454-457, config keys at 461-466), and the existing
`tools/report-landing-audit.py:673` selftest assertion `first-add-cutoff-not-readd` (the frozen base
already covers the delete/re-add cutoff in the *unmarked* case; this lane's contribution is the same
property **under promisor marking**, plus the tip-only-completeness axis).
