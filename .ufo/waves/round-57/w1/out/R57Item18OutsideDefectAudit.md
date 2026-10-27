# R57Item18OutsideDefectAudit — round-56 non-author routed defects, re-evaluated against the tree

Seat: R57Item18OutsideDefectAudit (item `round57/OutsideDefectAudit/18`; revenger; leaf member, no dispatch).
Axes under observation: operability + calibration (lane `SCORECARD.md:6`, `shokunin.conf:52`); the
historical `MISSION.md:29` conflict is reported, not resolved. Read-only over the lane: no shared
file, index, ref or source-tree write by this seat; no tool installation was needed or performed.

**Measured tips.** The lane was landing round-57 commits during this seat's run, so every figure
names its tip. First read `b89bdab2…` (round-56 closure tip); repair and fixture tests `8640e34c…`;
append-only audit `16efcf5e…` and `77e7f5ee…` (2026-10-27T15:14:56-03:00, the headline tip);
the independent binding check ran at `8a7f1976…` after writing began.
`git status --porcelain` at the first read showed only in-flight round-57 seat directories; no
tracked file was modified by this seat.

**Assignment.** Re-evaluate the four routed defects that the round-56 **non-author** closure filed
(`corpus/lessons/round-56-verifier-spotcheck.md`, §"Routed defects for next round") against the
current tree, and report exact scope. No verdict authority: this seat reports reachable state.

## Verdict table

| # | Round-56 routed defect (condensed from the closure's wording) | Where round 57 landed it | Scope verdict at `77e7f5ee` |
|---|---|---|---|
| 1 | Resolve the `MISSION.md` vs prompt/config/SCORECARD axis-authority conflict through the operator/L0 channel; do not silently claim calibration in place of freshness | `SCORECARD.md:6` discloses it; the round-57 prompt repeats it; no L0 answer; no lesson row | **OPEN — operator/L0-owned.** Disclosed in SCORECARD, absent from the round lesson; not closed and not silently resolved. |
| 2 | Strengthen C2-style calibration gates to bind **actual executed battery entries** and test **SCORECARD/SHONEN disagreement**; a roster-literal/no-op harness must fail | `tools/round56-prereg-check.py` AST call-site check (commit `7b74e2f2`); `SCORECARD.md` §Round 57; S516 | **PARTIAL / OPEN.** The plain roster-literal no-op now fails (`met=False`, exit 1), but the check binds *call-site presence anywhere in the module*, not execution: a dead-function harness and an `if False:` harness each still print `met=True`, exit 0. SCORECARD and SHONEN are never read (deleting both leaves `met=True`). Second clause has no implementation or evidence. |
| 3 | Revisit S513's rejection rationale and record the disagreement as a lesson/quality criterion if retained | none | **OPEN.** S513 remains `rejected` with the same rationale; no round-57 lesson row; no new `corpus/QUALITY.md` criterion. |
| 4 | The existing report audit records inherited append-only audit exit 1 and invalid `declared_at`/SCORECARD bindings; route for repair rather than treating the audit as clean | none; round 57 added new unrestored events | **OPEN and WORSENED.** `bad_declarations=4` unchanged; `unrestored` 2 (round-56 tip) → 6 (`77e7f5ee`), four new round-57 events, five graded lines; audit exit 1. |

Lesson coverage of the four routed defects (wave condition "round-56 outside defects must be
lesson-addressed"): round-57 `corpus/lessons/round-57.md` §Mistakes carries two rows —
`calibration-staleness` (round-57's own C2, **not** a round-56 routed defect) and `no-op-counter`
(routed defect 2, first half only). Routed defects **1, 3 and 4 have no row** in the lesson or in
`SCORECARD.md` §Round 57, and defect 2's SCORECARD/SHONEN half is not addressed. Net: 1 of 4
routed defects is partially lesson-addressed; 3 are absent.

## D1 — MISSION vs config/prompt/SCORECARD axis authority — OPEN, operator-owned

```
$ sed -n '14,30p' /home/vgpnk/Projects/shokunin/MISSION.md
Historical example — the upstream fleet's initial nine-lane config, not the
current roster (axes preserved):
...
  kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }
$ sed -n '52p' /home/vgpnk/Projects/shokunin/shokunin.conf
kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
$ sed -n '6p' SCORECARD.md | cut -c1-260
**Current authority (round 57):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35).
$ grep -n "kama | round-35" /home/vgpnk/Projects/shokunin/.ufo/l0-questions.md
145:kama | round-35 | MISSION.md:29 still says operability + freshness; shokunin.conf and the round prompt say operability + calibration. ... Which pair is the assigned authority?
```

No answer line follows line 145 (the surrounding entries are other lanes' questions), and the
round-57 prompt itself instructs seats not to resolve the conflict. The round-57 lesson contains no
MISSION/axis row (`grep -n "MISSION" corpus/lessons/round-57.md` → no output). Scope: the
disclosure obligation is met in SCORECARD and the prompt; the routed action (operator/L0 ruling) is
unmet and outside this lane. Round 56's own report already recorded it as open
(`.ufo/reports/round-56/kama.md` §"Audit, open decisions, and tooling": "`kama | round-35` asks
which authority owns the lane axis pair").

## D2 — executed-entry binding and SCORECARD/SHONEN disagreement — PARTIAL

**What changed.** Commit `7b74e2f2` added an AST scan to `tools/round56-prereg-check.py`:
lines 61–71 collect every call named `run` or `assert_mutant_breaks_detection` whose first argument
is a string constant, over `ast.walk(tree)` (the whole module), then require
`expected <= invoked`. Blob sha256: `c7b0d787…` at `b89bdab2` (pre-repair) → `dee6f922…` from
`7b74e2f2` through `77e7f5ee` (post-repair).

**Measured behaviour** (own clone at `/fast/scratch/hyaku/kama-r57/R57Item18OutsideDefectAudit/clone`,
guarded with `git -C … rev-parse --show-toplevel`; fixtures copied to
`receipts/fixture-v{1,2,3,5}-*.py`, driver `receipts/drive.py`, full JSON `receipts/fixture-results.json`):

| Fixture (all keep the exact preregistered ROSTER literal) | pre-repair counter | post-repair counter |
|---|---|---|
| genuine round-56 battery (3 live `run(...)` calls in `main()`) | `met=True` exit 0 | `met=True` exit 0 |
| v1 plain no-op: no calls at all, `main(): return 0` | `met=True` exit 0 | **`met=False` exit 1** |
| v2 dead-function harness: the three calls exist only inside an uncalled `_never_called()`; `main(): return 0` | `met=True` exit 0 | **`met=True` exit 0** |
| v3 unreachable harness: the three calls sit under `if False:` inside `main()` | `met=True` exit 0 | **`met=True` exit 0** |
| v5 genuine battery, `SCORECARD.md` and `SHONEN.md` deleted from the tip | — | **`met=True` exit 0** |

v2's battery was also executed: `python3 fixture-v2…py` printed nothing and exited 0 (no receipt
directory created), i.e. no battery entry runs — and the post-repair counter still reports
`met=True`.

Exact post-repair output for v2:

```
$ python3 receipts/prereg-check-post-repair.py --repo <clone> --tip b317fd8cd47e2b8b9a9a7621b4678789ed69beed
tip=b317fd8cd47e2b8b9a9a7621b4678789ed69beed
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

**Scope reading.** The routed defect asks for binding to *executed* entries. The landed check binds
to *declared call sites*; reachability and runtime execution are unbound. Round-57's claim
(`corpus/lessons/round-57.md:7`) says "bind … to calls in the battery's `main`, so a no-op harness
cannot satisfy the counter"; v2 and v3 falsify that sentence as written (both are no-op harnesses
that satisfy it). The SCORECARD section discloses the weaker reading — "C1 does not assert that
every runtime effect of a battery call was executed; it checks the call-site inventory in the
committed battery AST" — so the *implementation* is honestly described in SCORECARD but the *claim*
and its S516 anchor ("`main()` lines 69–83") are stronger than the code (`ast.walk(tree)`).

**Second clause (SCORECARD/SHONEN disagreement) has no implementation.** The counter reads only
`PREREG` and `BATTERY`; `grep -n "SCORECARD\|SHONEN" tools/round56-prereg-check.py` → no output. v5
proves it: deleting both self-assessment files leaves `met=True`, exit 0. No other tool tests this
disagreement (`grep -ln "SHONEN" tools/*.py` → only the round-53/54 cited-path checks, which verify
that cited paths resolve, not that SCORECARD and SHONEN agree). At the tip the disagreement is
concrete and untested: `SHONEN.md` holds 4 `[~]` boxes and 0 `[x]`/`[ ]` while `SCORECARD.md`
reports operability 8 / calibration 7.

**Negative-control reproducibility.** `measured/noop-c1.out` records
`fixture=/fast/scratch/hyaku/kama-r57/noop-control`, `tip=8caa23a2e223b96308aee981ff7897c612365523`,
`met=False`, exit 1. That tip is not in lane history (`git cat-file -e 8caa23a2…` → exit 1, no
output), so the lane's only committed no-op receipt cannot be reproduced from the lane; its fixture
directory still exists only under scratch. This is the same "quoted output, no committed receipt"
class the round-56 closure raised.

## D3 — S513 rejection rationale and quality criterion — OPEN

```
$ sed -n '266p' corpus/SOURCES.md
| S513 | ld.so(8) — https://man7.org/linux/man-pages/man8/ld.so.8.html | docs | A | broad dynamic-linker environment and token handling; … | §LD_AUDIT, Linux man-pages 6.19 (2025-05-17), HTML snapshot … | REJECTED: this broad loader manual overlaps the dedicated rtld-audit(7) source S512 for the claim's only need (the LD_AUDIT variable loads auditor objects); flip: a future claim about secure-execution, dynamic string tokens, or loader namespace semantics | rejected | 2026-10-27 | on-release | — |
$ grep -n "S513" corpus/lessons/round-56.md corpus/lessons/round-57.md corpus/QUALITY.md
corpus/lessons/round-56.md:15: … S513 — REJECT … (unchanged row text)
$ grep -c "KQ98" corpus/QUALITY.md
0
```

The row is unchanged, the round-57 lesson has no S513 row, and `KQ98` remains a proposal cited only
from SCORECARD plans (`.ufo/waves/round-56/w1/out/W01LessonReview.md:258`), not an adopted
`corpus/QUALITY.md` criterion. The outside disagreement lives only in the round-56 verifier lesson
(outside the lane); nothing in the lane records it. D3 is open, and the only lane-side artefact is
the rejected row itself.

*Advisory reading, not a verdict:* the row's rationale is claim-scoped ("for the claim's only
need") with a flip that retains the row for future secure-execution/token/namespace claims. The
outside verifier objected that the flip names topics the source already contains; on the row's
wording the flip means "revisit this row when such a claim exists", not "this source lacks those
topics". If the lane wants that reading to bind, one sentence in S513's `note` is the minimal fix.

## D4 — report-audit append-only exit 1 and invalid bindings — OPEN, WORSENED

The round-56 report's audit record (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-56/kama.md`,
§"Audit, open decisions, and tooling") states exit 1, `unrestored=2`, `bad_declarations=4`, and names
the four invalid `declared_at` bindings. Re-measured at `77e7f5ee` (receipt
`receipts/audit-final2.out`):

```
$ python3 tools/append-only-audit.py --repo . --to 77e7f5eef2b0c759b7509056c7c511255477496d
summary commits=389 files=108 events=131 restored=75 partial=0 unrestored=6 ungraded=45 disclosed=5 permitted_lines=60 disclosed_lines=10 bad_disclosures=0 ungraded_lines=229 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=4
exit=1
```

The four unbound declarations are byte-for-byte the round-56 four:

```
declaration SCORECARD.md         corpus/README.md:761  unbound: does not say append-only for SCORECARD.md
declaration corpus/QUALITY.md    corpus/README.md:761  unbound: does not say append-only for corpus/QUALITY.md
declaration corpus/README.md     corpus/README.md:761  unbound: does not say append-only for corpus/README.md
declaration corpus/lessons/*.md  corpus/README.md:1239 unbound: does not say append-only for corpus/lessons/*.md
```

The pointed lines at the tip are ordinary prose, not declarations:
`corpus/README.md:761` = `  context-capacity rows' scope already excludes.`;
`corpus/README.md:1239` = `- Carried over unchanged and not re-measured here: the b11906 ledger population at`.
The lessons declaration actually sits at `corpus/README.md:1245`
("Lesson files under `corpus/lessons/` are append-only as the `A-corr` contract row declares …").
`registry/append-only-contract.tsv` was last changed at `24e906f0` (round 49); round 56 and round 57
did not touch it.

`unrestored` grew from 2 at the round-56 tip (`.ufo/waves/round-56/measured/append-only-audit-at-784.out`:
`unrestored=2`) to 6 at `77e7f5ee`; four new events, all round-57:

```
event 8640e34cad02 SCORECARD.md            deleted=2 graded=1 ungraded=1 status=unrestored
event 16efcf5eedf4 LOG.md                  deleted=1 graded=1 ungraded=0 status=unrestored
event 16efcf5eedf4 SCORECARD.md            deleted=2 graded=2 ungraded=0 status=unrestored
event 16efcf5eedf4 corpus/lessons/round-57.md deleted=1 graded=1 ungraded=0 status=unrestored
```

One is diagnosable to a byte. `8640e34` replaced the round-56 authority banner at `SCORECARD.md:6`
and appended a "round 56" banner under `## Historical pre-integration authority text — round 56`
(tip line 3179). The appended line is **not** byte-identical to the deleted one:

```
$ git show 8640e34^:SCORECARD.md | sed -n '6p'    > banner-deleted.txt   # 903 B, sha256 a8f4d5dccd21195b748b6055e946ff85b07b3a8792d5ee15e32274fb3e7ea9d9
$ git show 8640e34:SCORECARD.md  | sed -n '3179p' > banner-appended.txt # 903 B, sha256 537acd9e901f419627f10ea0f8754abae6275c805a4e27b20725ab20662edc7b
$ cmp -l banner-deleted.txt banner-appended.txt | head -1
839 162 164        # first differing byte at offset 838
deleted  tail: “… kept current through round 56; round-55 measurements, verdicts and limits remain in §Round 55.”
appended tail: “… kept current through round 56; the round-55 authority is kept under §Historical head sections.”
```

`[INFERENCE]` The appended variant matches the round-56 *worktree* banner text that round-56 seat
V03 flagged (it asserts a round-55 banner that then did not exist), rather than the corrected
committed line that `8640e34` deleted. Either way the graded line is not restored, so the round-57
integration reproduces the round-56 D7 class (banner replacement without byte-exact preservation)
and the audit remains red with a larger unrestored set. The routed defect's instruction — repair,
do not treat the audit as clean — is unmet.

## Non-author source spot-check (advisory; this seat is a lane author)

**S515 required re-open.** Re-opened live this round (2026-10-27) at
`https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`; the page header
reports `git-config last updated in 2.56.0` (2026-09-28). Located quote, §`GIT_CONFIG_COUNT`
(paragraph following the `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` headings), **18 words**:

> all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration

This matches the round-56 lesson quote (`corpus/lessons/round-56.md:18`) in wording and section.
One byte-level note: the live page renders a typographic apostrophe (`process’s`); the lesson
normalises it to ASCII (`process's`). Wording is unchanged, so this is not a substantive drift, and
the lesson does not label the quote "verbatim" (KQ45's byte-exact rule is not triggered).

**Admit/reject spot check (one, as required; advisory).** S514 ADMIT (`git(1)` §GIT_DIR): the quote
is present in the round-56 snapshot and the revision marker (`2.56.0`) is in the anchor cell —
agree. S513 REJECT (`ld.so(8)` §LD_AUDIT): the located quote is present in the round-56 snapshot
("A list of user-specified, ELF shared objects to be loaded …"), the row is coherent as a
claim-scoped redundancy rejection with a flip; the outside closure's disagreement is a reading of
the flip, not a misquote. Recommend one clarifying sentence in the S513 `note` (see D3) rather than
reopening the row; no lane decision is taken here.

## Frozen-claim / control observations inside this scope

- The round's own freeze ordering conflicts. `.ufo/waves/round-57/controls/freeze.txt` says
  "claims=C1 calibration stale canonical-table count; C2 operability canonical-row execution
  binding", while `controls/freeze-amendment.txt`, `corpus/lessons/round-57.md` and
  `SCORECARD.md` §Round 57 say C1 = no-op battery roster control (operability) and C2 = stale
  verifier-spotcheck count (calibration). The assignment prompt uses the first ordering. Both
  orderings are in the committed tree; no seat resolves it here.
- `controls/base-c1.out` and `controls/base-c2-frozen.out` are identical except the `base_c1_exit=1`
  line, and both are the **round-42** counter output at `b89bdab2` (`r41=1 … maxN=56 met=False`),
  not the prereg counter. `controls/noop-c1.out` is a printer with a round-42-shaped summary
  (`mismatches=0 maxN=46 met=True`); `controls/noop-c2.out` is an instrument that reports
  `canonical_table_reads=0 self_description_reads=0`. So the frozen control pair does not include a
  base or no-op run of the amended C1 target; the only such negative receipt is the un-reproducible
  `measured/noop-c1.out` (see D2).
- The "maxN=56 instead of expected 46" phrasing in the assignment does not describe a live mismatch.
  `maxN` is defined in `tools/round42-selfdesc-reconcile.py` as the greatest `^## Round (\d+)` in
  SCORECARD; at `b89bdab2` it is 56 (with `r41` red: the calibration row expected `42` while the
  tree held 43) and at `77e7f5ee` it is 57 (`r41` green after the row was corrected to 43). The
  `maxN=46` string appears only in the frozen no-op fixtures. The round-57 calibration claim is the 42→43 correction;
  at `77e7f5ee` both counters are green (`receipts/counters-final.out`):
  `round41 … mismatches=0 met=True`, `round42 … mismatches=0 maxN=57 met=True`.

## Assimilation and consideration

Assimilation: none. `considerthese/2026-10-26.md` proposal 3 ("keep a running count of counters that
a shortcut can satisfy") was opened this round; this seat produces one datum it would tally — the
plain roster no-op is now killed, two further matching-roster no-op classes survive `met=True`, and
the SCORECARD/SHONEN disagreement clause has no implementation — but implements no tally and
changes no shared file.

## Distinct case 39

The independent case test lives in its own evidence file:
`.ufo/waves/round-57/w1/out/R57Item18OutsideDefectAudit/case39-independent.md`. It runs a
from-scratch clone + five-fixture matrix against both counter blobs and reproduces the routed
defect 4 declaration set without the audit tool. Result: routed defect 2 not closed (two no-op
classes survive; no SCORECARD/SHONEN read); routed defect 4 confirmed unrepaired.

## Limits and confidence

- The lane moved through `b89bdab2 → 7b74e2f2 → 8640e34 → 16efcf5e → 77e7f5ee` during the seat's
  run; each figure is pinned to its tip and may be superseded by later round-57 integration.
  Re-measure at the final tip before closure.
- High confidence in every observed line: each is a command output quoted above and re-runnable at
  its tip; fixtures are deterministic and their sources are preserved under `receipts/`.
- `[INFERENCE]` marks: the provenance of the appended banner variant (D4) and the reading of S513's
  flip (D3). No verdict, score, or admission is asserted.
- Live divergence observed at the final read (2026-10-27T15:18-03, tip `8a7f1976`), **not by this
  seat**: `git status --porcelain` shows ` D .ufo/waves/round-57/controls/{c1-noop.py,noop-c1.out,noop-c2.out}`
  and a new untracked `controls/noop-fixture/` (created 15:17). The three tracked control bytes remain
  readable at HEAD (`git show HEAD:.ufo/waves/round-57/controls/noop-c1.out` prints the
  `mismatches=0 maxN=46 met=True` fixture line), so every citation above still resolves; the
  worktree deletion is another actor's in-flight change and was left untouched.
- Tool installs/upgrades: none. Scratch `/fast/scratch/hyaku/kama-r57/R57Item18OutsideDefectAudit/`
  was created explicitly, receipts were copied here first, and the clone was removed after capture.

Report: .ufo/waves/round-57/w1/out/R57Item18OutsideDefectAudit.md
