# Distinct case 41 — independent boundary test for the canonical self-assessment gate

Seat: R57Item20OwnershipScan. Case: counterpart-lane boundary; owner overlap.
Read-only; no shared edits; no installs. Main report:
`.ufo/waves/round-57/reports/R57Item20OwnershipScan-case41.md`.

## Test

`measured/R57Item20OwnershipScan/ownership-scan.py`, run from the lane root:

```
python3 .ufo/waves/round-57/measured/R57Item20OwnershipScan/ownership-scan.py
```

Test is revision-pinned: gate and control bytes are read through git at `HEAD`
because the working tree lost three control files mid-wave. First run at 15:15
(`ownership-scan-run1.out`, before that move) → `OWNERSHIP_SCAN pass=14 fail=0`.
Revision-pinned run (`ownership-scan.out`), exit 0:

```
PASS A1_gate_repo_default_dot :: --repo default "." present at HEAD
PASS A2_gate_no_sibling_ref :: sibling refs=none
PASS B_canonical_heading_exclusive :: canonical heading in 0 of 21 non-kama roots
PASS C1_maxn_derived :: base ^## Round N max=56; Round 57 present=False
PASS C2_counter_has_no_46 :: literal 46 absent from the gate source
PASS C3_46_only_in_frozen_artifacts :: HEAD control carriers=['c1-noop.py', 'canonical-noop/SCORECARD.md', 'no-canonical/SCORECARD.md', 'noop-c1.out', 'noop-c2.out'] lane SCORECARD historical carrier line=2676 worktree_churn=D .ufo/waves/round-57/controls/c1-noop.py D .ufo/waves/round-57/controls/noop-c1.out D .ufo/waves/round-57/controls/noop-c2.out ?? .ufo/waves/round-57/controls/noop-fixture/
PASS D_canonical_audit_green :: listed 11 observed 11 missing 0 unsubstantiated 0 met True
PASS E_sibling_scoped:check-self-assessment.py :: no kama reference
PASS E_sibling_scoped:souji-capability-agreement.py :: no kama reference
PASS E_sibling_scoped:souji-capability-cells.py :: no kama reference
PASS F1_gate_is_lane_owned :: PROTOCOL.md §Gate standard
PASS F2_fleet_axes_owner :: AXES.md line 4
PASS F3_tameshi_refuses_product_gate :: tameshi PROVINCE Owns/Refuses
PASS G_verdict_non_author :: round-56 spot-check author line
OWNERSHIP_SCAN pass=14 fail=0
```

Each check can fail: a sibling path in the gate, a canonical heading in another
lane, `46` in the gate source, a non-green canonical audit, a `kama` reference in
a sibling gate, a missing ownership sentence, or an author-side verdict line would
each turn its check red.

## Boundary matrix

| Claim | Exact evidence |
|---|---|
| Gate instance is lane-owned | `PROTOCOL.md:377` "A **gate** is a committed, re-runnable verdict script a lane owns: it reads surfaces, compares them against expected values persisted in its own repo, and returns a verdict. A tool that cannot fail is a **probe**."; `PROTOCOL.md:398` "a child lane's *registry home* is its own `SKILL.md`". |
| Gate standard and closure are protocol's | `PROTOCOL.md:377-405` §Gate standard; `PROTOCOL.md:207` "**Integrator of record.** … the round's `protocol` lane"; `PROTOCOL.md:222` "The closure record is a gate, not prose"; `MISSION.md:21` protocol "protocol soundness, gate integrity". |
| Fleet-level axes are protocol + aggregator | `AXES.md:4` "Every shokunin works its own subset; the protocol and aggregator lanes own the fleet-level axes"; `AXES.md:15` calibration = "Self-assessment quality … SHONEN.md/SCORECARD entries match observed repo state"; `MISSION.md:22` aggregator "cross-lane quality, mint/dormancy calls, corpus review". |
| Reusable craft is tameshi's, never the lane gate | `tameshi-shokunin/PROVINCE.md:7-12` owns "the method … hermetic suites, mutation testing, fail-closed arms, verdict-line discipline, no-permissiveness audits, before/after proof"; `:14-16` "every lane's gate remains its own; tameshi owns only the reusable craft (a pattern is admitted from evidence in TWO independent lanes before it is claimed general). Never edits a sibling's gate code". |
| Verdict is the non-author closure's | `corpus/lessons/round-56-verifier-spotcheck.md:3` "author: hyaku closure (non-author integrator, @m_opus)"; `:14` C2 ruled "unprovable" on the no-op; `:44` routes "bind actual executed battery entries … a roster literal/no-op harness must fail"; `corpus/lessons/round-57.md:16` "dispatched members are lane authors". |
| Canonical rows are kama's | `PROVINCE.md:17` owns "lane instruments (the capability repertoire, `SCORECARD.md` canonical list)"; `SCORECARD.md:117` "a mirror, not the canonical source: the counters resolve the highest-numbered canonical heading below this line"; canonical heading `**Capabilities — canonical list as of round 49**` at `SCORECARD.md:2844` (base and tip), table from 2848, 11 rows. |
| No sibling lane reads or claims the canonical rows | `canonical list as of round N` count: 0 in the fleet root and all 20 non-kama `*-shokunin` repos, 9 in kama (highest 49). `tools/round42-selfdesc-reconcile.py` contains no `home/vgpnk`, `../`, or sibling-lane token; `--repo` defaults to `.` (line 275). |
| Same-shaped sibling gates are lane-local | `tsukuroi-shokunin/tools/check-self-assessment.py`: own-lane claim rows `tsukuroi-shokunin/SCORECARD.md:792,893`, `--repo` optional (line 1094), no `kama` token; `souji-shokunin/tools/souji-capability-agreement.py` line 103 requires its own `--root`, claim row `souji-shokunin/SCORECARD.md:344`, no `kama` token; `souji-capability-cells.py` claim row `:412`, no `kama` token. |

## Overlap summary

- Artifact layer: no overlap. The canonical list and its evidence pointers live
  only in kama; no sibling gate references them.
- Rule layer: the gate's outer contract is protocol's (`PROTOCOL.md:377-405`); the
  fleet-level calibration definition is protocol+aggregator (`AXES.md:4,15`); the
  reusable honesty pattern is tameshi's and needs two-lane evidence
  (`tameshi-shokunin/PROVINCE.md:14-16`). Kama may claim only its instance.
- Verdict layer: non-author closure owns admit/reject
  (`round-56-verifier-spotcheck.md:3`); lane-dispatched seats are authors
  (`round-57.md:16`).
- In-lane overlap: `capability-repertoire-audit` (names + evidence resolution;
  `listed 11 … met True` at base) and the round-42 `caps` leg (head mirror names +
  census counts, `round42-selfdesc-reconcile.py:220-227`) already bind the same
  canonical rows. An execution/content-binding leg is a new predicate over the
  same rows and needs one owner, not a third independent green.

## Expected-value boundary (observed, not resolved)

- Frozen base receipt `controls/base-c1.out`: `… mismatches=1 maxN=56 met=False`,
  exit 1; its only detail is the imported round-41 calibration run expecting `42`.
- `maxN=56` derives from 57 `^## Round (\d+)` headings at `b89bdab2`
  (`base-derivation.txt`), not from any canonical-row count.
- The literal `46` is absent from the gate source. `maxN=46` occurs in five
  round-57 control files (`c1-noop.py:3`, `noop-c1.out:3`, `noop-c2.out:4`,
  `canonical-noop/SCORECARD.md`, `no-canonical/SCORECARD.md`), in `SCORECARD.md:2676`
  only as a historical round-46 regression line, and in round-46–50 wave artifacts.
- Working-tree churn observed during the seat (not performed here):
  `git status --porcelain .ufo/waves/round-57/controls/` → `D c1-noop.py`,
  `D noop-c1.out`, `D noop-c2.out`, `?? noop-fixture/`. The committed control bytes
  remain at `HEAD`; the test reads them there.
- Current tree (`16efcf5e`) adds `## Round 57` at `SCORECARD.md:3149`; the
  committed-tip receipt `measured/c2-committed-tip.out` reads
  `mismatches=0 maxN=57 met=True`, exit 0.

## Advisory spot checks (author seat; advice only)

- **S515** (`corpus/SOURCES.md:268`): quote found in
  `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` at
  §`GIT_CONFIG_COUNT`, offset 21592 after tag-strip/entity-decode, 18 words. Row
  uses ASCII `process's`; source uses U+2019 `process’s`; row anchor cites the
  round-56 snapshot. Substantively supported; precision notes only.
- **S516** (`corpus/SOURCES.md:269`, own-work, tier A): at base `b89bdab2` the
  stated anchor `main()` lines 69–83 holds the named calls — 69
  `comparator_selftest`, 70 `run("base-old-counter", …)`, 71
  `run("round56-counter", …)`, 80 `run("m-drop-ldaudit", …)`, 81–82
  `assert_mutant_breaks_detection(...)`; the lesson quote is line 70. Tier A is
  permitted for `own-work` source code (`CORPUS.md:93-96`). Advice: admit is
  grounded; the quote line is 70, inside the stated range.

## Limits

No verdict on the round's claims; no admission or score claim; no fleet gate-integrity
claim; no claim that either canonical instrument subsumes the other; axis-authority
conflict (`MISSION.md:29`) left unresolved per the seat spec. No shared file edited.
