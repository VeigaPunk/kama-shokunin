# R57Item20OwnershipScan — counterpart-lane boundary for the canonical self-assessment gate (distinct case 41)

Axes under examination: **calibration** and **operability**, as assigned. Read-only
ownership scan: no shared-file edits, no commits, no sibling-repo writes, no
installations. Tooling authorization read first (`/home/vgpnk/.omp/agent/RULES.md`):
pacman transactions remain paused; nothing was installed or upgraded, so there is
no install/version/channel line to record.

**Term note [INFERENCE].** The fleet's own documents never define "counterpart
lane" (grep over `MISSION.md`, `AXES.md`, `PROTOCOL.md`, root `SCORECARD.md`,
`templates/`: no occurrence), and the round-57 spec is the term's only source
(`.ufo/waves/round-57/w1-spec.json:227,347`). I read it as the lanes the fleet
assigns to the *boundary* of a lane-owned gate — the gate standard, the
fleet-level axes, the reusable craft, and the non-author closure — and report each
with its own text. Every ownership statement below is grounded in a cited line;
only the word's reading is inferred.

## 1. The gate under examination (exact artifacts)

| Artifact | Evidence |
|---|---|
| Canonical capability rows | `SCORECARD.md:117` calls the head `## Capabilities` table a mirror, "not the canonical source: the counters resolve the highest-numbered canonical heading below this line"; the canonical heading is `**Capabilities — canonical list as of round 49**` at `SCORECARD.md:2844` in both the frozen base `b89bdab2` and the current tree `16efcf5e`; the four-column table begins at 2848 and carries 11 rows. |
| Gate instrument (round-42 self-description counter) | `tools/round42-selfdesc-reconcile.py`, sha256 `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`; `canon()` 120–127 selects the highest `canonical list as of round N` marker; `maxn` 167–168 derives from every `^## Round (\d+)` heading; `caps` leg 220–227 compares head mirror names to canonical names and `<n> (opened\|mined\|queued\|rejected)` to the sources census; `--repo` defaults to `.` (line 275). |
| Second lane-owned canonical gate | `tools/capability-repertoire-audit.py`: population = every four-column capability table, canonical = highest `canonical list as of round N`, `met = missing == 0 and unsubstantiated == 0`. Run at frozen base: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (receipt `measured/R57Item20OwnershipScan/cap-audit-base.json`); selftest `CAP_SELFTEST pass=2 fail=0`, exit 0. |
| Committed round-57 claim text | `SCORECARD.md:3149` `## Round 57 …`; C1 at 3155 (bind declared roster to actual battery call sites, operability); C2 at 3156 (re-anchor the SCORECARD verifier-spotcheck count, calibration); `corpus/lessons/round-57.md:1-9`. |
| Frozen controls | `.ufo/waves/round-57/controls/freeze.txt` (base `b89bdab2`, `frozen before wave seat findings`), `freeze-amendment.txt` (claim ordering correction), `base-c1.out`, `noop-c1.out`, `noop-c2.out`, `c1-noop.py`. |

## 2. Owner map (who owns which layer)

| Layer | Owner | Grounding |
|---|---|---|
| Canonical capability list **content** (heading, rows, first-working rounds) | kama | `PROVINCE.md:17` owns "lane instruments (the capability repertoire, `SCORECARD.md` canonical list)"; `SCORECARD.md:117` names the counters, not another lane, as the resolver; `PROVINCE.md:173` (round-42 note) registers the instruments the list cites. |
| Gate **instance** (script + expected values in-repo + registry home) | kama | `PROTOCOL.md:377`: "A **gate** is a committed, re-runnable verdict script a lane owns: it reads surfaces, compares them against expected values persisted in its own repo, and returns a verdict. A tool that cannot fail is a **probe**." `PROTOCOL.md:398`: "a child lane's *registry home* is its own `SKILL.md`". |
| Fleet **gate standard** (verdict codes, self-test clause, two evidences) and closure-record gate | protocol lane | `PROTOCOL.md:377-405` §Gate standard; `PROTOCOL.md:207` "Integrator of record … the round's `protocol` lane"; `PROTOCOL.md:222` "The closure record is a gate, not prose". `MISSION.md:21` gives protocol "protocol soundness, gate integrity". |
| Fleet-level **axes** | protocol + aggregator | `AXES.md:4` "Every shokunin works its own subset; the protocol and aggregator lanes own the fleet-level axes"; `AXES.md:15` defines calibration as "Self-assessment quality … SHONEN.md/SCORECARD entries match observed repo state"; `MISSION.md:22` gives aggregator "cross-lane quality, mint/dormancy calls, corpus review". |
| Reusable **gate-craft pattern** (mutation controls, fail-closed arms, no-permissiveness audits) | tameshi | `tameshi-shokunin/PROVINCE.md:7-12` owns "the method … hermetic suites, mutation testing, fail-closed arms, verdict-line discipline, no-permissiveness audits"; `14-16` "every lane's gate remains its own; tameshi owns only the reusable craft (a pattern is admitted from evidence in TWO independent lanes before it is claimed general). Never edits a sibling's gate code". |
| **Admit/reject verdict** on kama's claims | non-author closure / integrator | `corpus/lessons/round-56-verifier-spotcheck.md:3` "author: hyaku closure (non-author integrator, @m_opus)"; `PROTOCOL.md:207-224` (integrator assigns lane statuses); `corpus/lessons/round-57.md:16` "dispatched members are lane authors"; the round-57 wave context says "This is a build/attack mixed wave, not judgment". |
| Same-shaped self-assessment gates in sibling lanes | each sibling for its own lane | `tsukuroi-shokunin/tools/check-self-assessment.py` measures its own SCORECARD/SHONEN (`tsukuroi-shokunin/SCORECARD.md:792,893` claim rows), `--repo` optional (line 1094), no `kama` reference; `souji-shokunin/tools/souji-capability-agreement.py` and `souji-capability-cells.py` require their own `--root` (line 103) and carry no `kama` reference; claim rows `souji-shokunin/SCORECARD.md:344,412`. |

**Locality proof.** Of the 20 non-kama lane repositories plus the fleet root's own
`SCORECARD.md` (21 roots), **0** carry a `canonical list as of round N`
heading; kama's carries 9 (highest round 49). Kama's gate source contains no
sibling/home path (`grep -n "home/vgpnk\|\.\./\|tsukuroi\|souji\|tameshi\|kumitate\|protocol\|aggregator"`
→ no matches). The canonical list is therefore an exclusive lane surface, and no
sibling implementation reads it.

## 3. Owner overlap

**Overlap is at the rule and verdict layers, not at the artifact layer.** Kama owns
the gate instance and the canonical rows; protocol owns the gate standard that the
instance must satisfy and the closure record; aggregator shares the fleet-level
axes; tameshi owns only the reusable craft; the non-author closure owns
admit/reject. No lane claims kama's canonical rows, and kama claims no other lane's
gate.

**O1 — rule vs instance.** Any text that presents the canonical gate as a general
"gate integrity" result, or as a reusable pattern, crosses the boundary at once:
gate integrity is protocol's axis (`MISSION.md:21`) and the pattern is tameshi's
only after evidence in two independent lanes (`tameshi-shokunin/PROVINCE.md:14-16`).
Kama's safe claim is the instance: this lane's canonical rows, this lane's
instrument, expected values in this repo (`PROTOCOL.md:377,398`).

**O2 — instrument vs verdict.** The lane cannot certify its own gate. Round 56 is
the concrete precedent: the non-author closure ruled C2 "**unprovable**" on the
no-op receipt and routed "strengthen C2-style calibration gates to bind actual
executed battery entries … a roster literal/no-op harness must fail"
(`corpus/lessons/round-56-verifier-spotcheck.md:14,44`). Round 57 repeats the split:
the lesson records "no independent verifier of this round is available before
filing; dispatched members are lane authors" (`corpus/lessons/round-57.md:16`), and
the wave is declared "not judgment". A lane-authored green is evidence, never an
admission.

**O3 — two in-lane authorities already bind the same rows.** `capability-repertoire-audit`
binds canonical **names and evidence-pointer resolution** (`listed 11 observed 11
missing 0 unsubstantiated 0 met True` at the frozen base, exit 0) and compares every capability name carried by any
capability-shaped table in the file against the canonical table. The round-42 `caps` leg binds the head **mirror** table to canonical names plus the `opened/mined/queued/rejected`
census counts (`tools/round42-selfdesc-reconcile.py:220-227`). A third
"canonical-row execution/content binding" leg — the C2 worded in the seat context —
is a new predicate over the same rows, not an extension of either: canonical rows
carry evidence **paths** (`SCORECARD.md:2848-2860`), not runnable commands, so
execution binding has to define per-row call sites the way round-57 C1 does for the
battery (`SCORECARD.md:3155`, S516). It needs an explicit owner decision (kama
integration, one instrument) or it becomes a third green that can disagree with the
other two.

**O4 — expected value: control literal vs derived predicate.** The seat context
says the counter "currently reports `maxN=56` instead of expected `46`". Observed:
`maxN=56` is the maximum of the frozen base's 57 `^## Round (\d+)` headings
(`measured/R57Item20OwnershipScan/base-derivation.txt`: `round_headings=57 maxN=56
distinct_round_numbers=49`), and the literal `46` does **not** occur in the gate
source at all (`grep -n "46" tools/round42-selfdesc-reconcile.py` → no match).
`maxN=46` occurs in the round-57 frozen control tree in five files
(`controls/c1-noop.py:3`, `controls/noop-c1.out:3`, `controls/noop-c2.out:4`, and the
two fixture scorecards `controls/canonical-noop/SCORECARD.md` and
`controls/no-canonical/SCORECARD.md`), in the lane SCORECARD only as a historical
round-46 regression line (`SCORECARD.md:2676`), and in round-46–50 wave artifacts;
the gate has none (`git grep -n "maxN=46" HEAD` enumerates every carrier). So
"expected 46" is a control/historical literal — the round-46 maximum — not the
round-57 derived value; it is the same vacuity class round 56 removed. The committed round-57 C2 text instead
names the real disagreement (expected 42, observed 43; `SCORECARD.md:3156`), and the
committed-tip receipt at `8640e34` reads `mismatches=0 maxN=57 met=True`, exit 0
(`measured/c2-committed-tip.out`) because the tree now carries the round-57 heading.
Owner boundary: derived values belong to the lane's SCORECARD + instrument; frozen
controls own only their own fixtures. I do not resolve which text governs.

**O5 — source-row ownership at the gate's own evidence.** Two rows carry the
canonical gate's evidence and both are kama-authored:
`corpus/SOURCES.md:269` **S516** (own-work, tier A, anchor `main()` lines 69–83 at
`b89bdab2`) and `corpus/SOURCES.md:268` **S515** (Git config runtime env pairs).
Advisory only, because dispatched seats are lane authors:
- **S515 re-open (advice):** the quote is located in the fresh round-57 snapshot
  `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` at §`GIT_CONFIG_COUNT`,
  character offset 21592 after tag-strip and entity decode; it is 18 words. The row
  writes `process's` with ASCII `'`, the source carries `process’s` (U+2019), and the
  row's `anchor` cites the round-56 snapshot. Substantively the row is supported;
  the two character/snapshot notes are precision, not a rejection ground.
- **S516 admit (advice: ADMIT is grounded).** At base `b89bdab2`, `main()` lines
  64–83 contain the named call sites: line 69 `comparator_selftest`, line 70
  `run("base-old-counter", …)`, line 71 `run("round56-counter", …)`, line 80
  `run("m-drop-ldaudit", …)`, lines 81–82 `assert_mutant_breaks_detection(...)`;
  the lesson's quoted string is line 70, inside the stated anchor. Tier A is
  permitted for `own-work` source code / the lane's own re-runnable gate output
  (`CORPUS.md:93-96`). One precision note: the quote line is 70, not the range
  start; the range 69–83 is otherwise accurate.

**O6 — three claim texts and a moved tree (open boundary, not resolved).**
- Seat context (pre-amendment): C1 calibration = stale canonical capability row
  count, "`maxN=56` instead of expected `46`"; C2 operability = canonical-row
  execution/content binding.
- `controls/freeze-amendment.txt`: C1 = round-56 prereg no-op (operability),
  C2 = round-42 stale calibration count (calibration); it says it supersedes "the
  earlier round-57 freeze's claim ordering only".
- Committed `SCORECARD.md:3155-3156`: C1 = roster call-site binding (operability),
  C2 = verifier-spotcheck count re-anchor (calibration), consistent with the
  amendment.
The tree also moved during the wave: five commits after the frozen base
(`89dc4f52`, `7c873d7b`, `7b74e2f2`, `8640e34c`, `16efcf5e`), adding
`## Round 57` at `SCORECARD.md:3149`. Concurrent seats also left uncommitted work
in the working tree at the time of writing — the control deletions below, an
untracked `noop-fixture/`, and a one-line addition to `corpus/lessons/round-57.md`
(`git diff --stat` → `1 file changed, 1 insertion(+)`: an
`inherited-append-only-governance` row). This seat wrote none of those and
attributes none of them; they are reported as observed state.

**Observed concurrent change (not this seat).** Between the first and second test
runs, `.ufo/waves/round-57/controls/` lost three tracked files in the working tree
and gained an untracked directory — `git status --porcelain .ufo/waves/round-57/controls/`
→ `D c1-noop.py`, `D noop-c1.out`, `D noop-c2.out`, `?? noop-fixture/`. The
committed bytes remain at `HEAD` (`git cat-file -p HEAD:.ufo/waves/round-57/controls/noop-c1.out`
still prints `mismatches=0 maxN=46 met=True`), and the test now reads the gate and
control bytes through git at `HEAD` rather than the mutable working tree. This is
control-artifact ownership in motion mid-wave: reported, not repaired.

## 4. Distinct case 41 — independent test

`measured/R57Item20OwnershipScan/ownership-scan.py` is a runnable, read-only test
that asserts each boundary claim and can fail: gate `--repo` default and
lane-locality; canonical-heading exclusivity across 21 non-kama roots (20 lane
repos plus the fleet root); `maxN` derivation at the frozen base; absence of `46`
from the gate; the five frozen control carriers of `maxN=46`; the second canonical
gate's green run; sibling gate scoping; the three fleet ownership texts; the
non-author verdict owner. Gate and control bytes are read through git at `HEAD`
(the working tree lost three control files mid-wave), and the check reports that
working-tree churn in its own detail line rather than depending on it.

Results: first run at 15:15 (`measured/R57Item20OwnershipScan/ownership-scan-run1.out`)
→ `OWNERSHIP_SCAN pass=14 fail=0`, exit 0; after the concurrent control move, the
revision-pinned run (`measured/R57Item20OwnershipScan/ownership-scan.out`) →
`OWNERSHIP_SCAN pass=14 fail=0`, exit 0. The separate transcript is
`.ufo/waves/round-57/OwnershipScan/41/evidence.md`.

Note on cold starts: the gate parses committed bytes through git, so an empty
result would indicate a wrong revision or path, not server indexing. No such
empty result occurred.

## 5. Boundary statement — what this seat does not claim

- No verdict on round-57 C1/C2, no claim that either counter is sufficient, no
  fleet gate-integrity claim, no admission, no score or capability move.
- No claim that `capability-repertoire-audit` subsumes the round-42 `caps` leg, or
  vice versa; they bind different predicates over the same rows (O3).
- No claim on the axis-authority conflict (`MISSION.md:29` operability+freshness vs
  the lane config); the seat spec says not to resolve it.
- No shared file was edited; the receipts below are new wave-path artifacts.

## 6. Commands and exact results

1. `python3 tools/capability-repertoire-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864 --out .ufo/waves/round-57/measured/R57Item20OwnershipScan/cap-audit-base.json` → `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0.
2. `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`, exit 0.
3. `python3 .ufo/waves/round-57/controls/c1-noop.py` → `mismatches=0 maxN=46 met=True`, exit 0 (independent confirmation that the literal is fixture output).
4. `grep -n "46" tools/round42-selfdesc-reconcile.py` → no match (exit 1).
5. `git cat-file -p b89bdab2:SCORECARD.md` → 3165 lines; parse: `round_headings=57 maxN=56`; `canonical_headings=9 highest_canonical_round=49`; no `## Round 57`.
6. `wc -l SCORECARD.md` (current tree `16efcf5e`) → 3181; `grep -n '^## Round 57'` → line 3149.
7. `grep -n "home/vgpnk\|\.\./\|tsukuroi\|souji\|tameshi\|kumitate\|protocol\|aggregator" tools/round42-selfdesc-reconcile.py` → no matches.
8. `git grep -n "maxN=46" HEAD` → carriers: 5 under `.ufo/waves/round-57/controls/` (`c1-noop.py`, `noop-c1.out`, `noop-c2.out`, `canonical-noop/SCORECARD.md`, `no-canonical/SCORECARD.md`), `SCORECARD.md:2676` (historical round-46 line), and round-46–50 wave artifacts; the gate is not a carrier.
9. `python3 .ufo/waves/round-57/measured/R57Item20OwnershipScan/ownership-scan.py` → `OWNERSHIP_SCAN pass=14 fail=0`, exit 0.
10. `git status --porcelain .ufo/waves/round-57/controls/` → `D c1-noop.py`, `D noop-c1.out`, `D noop-c2.out`, `?? noop-fixture/` (concurrent seat; control bytes intact at `HEAD`).

Report artifacts:
- this report: `.ufo/waves/round-57/reports/R57Item20OwnershipScan-case41.md`
- distinct-case transcript: `.ufo/waves/round-57/OwnershipScan/41/evidence.md`
- receipts: `.ufo/waves/round-57/measured/R57Item20OwnershipScan/{ownership-scan.py,ownership-scan.out,ownership-scan-run1.out,cap-audit-base.json,base-derivation.txt}`

Report: `.ufo/waves/round-57/reports/R57Item20OwnershipScan-case41.md`
