# kama round 43 report

author: kama L1 (agent `KamaR43`)
date: 2026-10-25
attempt: 1 of 1 (watchdog: `2026-10-25T22:25:38-03:00 launch kama round=43 pgid=4093527 driver=hyaku-inline attempt=1`; no `lane-dead-no-report kama round=43` line, so nothing was inherited from an earlier attempt)
base: `6897ead55c24ba08c9ac0b09466d4fbfe005a459` (round-42 verifier spot-check, the lane remote tip at launch)
lane tip: `9307b15e0731f91efbd17ea10ef0d579fc1c9065` (`git ls-remote origin refs/heads/master` prints this hash)
measured commit: `25df591a4e50f315b920ec0d0acba6145989e267` (integration commit; the tip adds receipts, the end census and the SCORECARD measured section)
Stale-lane: progressing. The current mission is kama round 43 (respawn-per-round driver); no other mission of this lane is open. The parked worktree `/home/vgpnk/Projects/shokunin/kama-shokunin` is still detached on the mutation-sandbox lineage (round-40 D5, L0 `kama | round-41`, refreshed round 42), so every measurement and commit used fresh clones of the lane remote (`/fast/scratch/kama-r43/{clone,work,meas}`); the parked path served only as the seats' report directory and the `.ready` handoff. `jj-lane.sh` was not used: it refuses the parked worktree's non-tip working copy. Commits are plain `git` under `kama-shokunin <kama@shokunin.local>`.

**Round shape, stated first: the round is short.** One v1 build wave of **38 seats** ran (`kama-r43-w1`, 0 dead). The planned second wave, a 48-seat falsify wave, was generated and validated with `plan` (`.ufo/waves/round-43/w2/spec.json`, `dispatch.json`) and **never dispatched**: the orchestrator closed run 7 (spawn cap 0) while it was being built, and I wrote no `w2.ready`. Round total **38 seats, below the 64-100 band**; no residual call. No claim was attacked by a falsify wave. Re-dispatching the round is the orchestrator's decision.

## Work performed

Declared claims, frozen before data (`.ufo/waves/round-43/preregistration.json`, freeze `895793e0b4c56bdcb939277b8ff0251b26306d4d`): **C1 calibration 7→7**, SKILL.md's instrument registry, its documented `GATE_SELFTEST` line, the SCORECARD calibration row's closure count, the SOURCES search-log correction and README's hidden entries match the tree (counter `tools/round43-registry-audit.py`). **C2 operability 8→8, capability acquisition `hexrun-census`**, every 32-127 character hex run other than 64 that the lane's documents cite is classified (counter `tools/round43-hexrun-audit.py`). **C3 coverage 9→9, assimilation from `merge/kama`**, the vLLM `/health` process map, sourced on rows S480 and S481 opened this round (counter `tools/round43-health-audit.py`). Calibration (7) is the lowest assigned non-retired axis; the stagnation nudge is inactive.

- **Protocol load:** `skill://shokunin` (installed at `~/.agents/skills/shokunin`), `skill://godspeed`, `skill://swarm`, the round prompt in full, fleet `AXES.md`; the lane `SCORECARD.md` (head and §Planned round 43), `SHONEN.md`, `PROVINCE.md`, `corpus/lessons/round-42.md`, `round-42-verifier-spotcheck.md`, `considerthese/2026-10-25.md`, and the staged `merge/kama` package (`MERGE-REPORT.md`, r12 and r13 amendments).
- **Freeze (commit `895793e0`, evidence `.ufo/waves/round-43/`):** preregistration, the three counters, `controls/build_controls.py` and base plus seven shortcut controls (`junk-c1-fillerrows`, `junk-c1-flagpaste`, `junk-c1-sidefilesonly`, `junk-c2-stub`, `junk-c2-rowonly`, `junk-c3-rowsonly`, `junk-c3-fabricated`, every one `met=False`), census start receipts, and the 73 base-unexplained hex runs (`c2/base-unresolved.tsv`). The counters were not changed after the freeze. Correction: the committed `controls/freeze.c{1,2,3}.out` are byte copies of the base receipts; the counters scored at the real freeze commit are `controls/freeze-measured.c{1,2,3}.out` (C1 `mismatches=45` there). Found by seats W1X02 and W1R01.
- **Wave 1 (build, 38 seats):** two independent builds of `tools/hexrun-census.py` (B landed, A kept as evidence, `w1/out/W1X01/`); eight executors queried GitHub for the 64 unresolved object ids and committed 62 API responses as evidence; 19 registry rows drafted by eight scribes; the small-fix patch; two entry drafts merged; Gate, rows and assimilation scratch; the staged-refusals ledger; Mistakes and KQ drafts; four scouts re-opened the sources; four connectors scanned siblings and coupling; two critics and one mutation-tester attacked the frozen counters. Reports: `.ufo/waves/round-43/w1/out/*.md` (38), results `w1/kama-r43-w1-results.json`.
- **C1 work (commit `6fd85332`):** 19 registry rows under `SKILL.md` §Round-43 registry completion (the 16 counters of rounds 35-42 that the lane's own gate had reported unregistered since round 35, plus the three round-43 counters), each with a SHA-256 pin and the exit codes its source returns; the two retired-counter rows given their real flags; the round-42 search-log correction (closure defect D-C); the calibration row's closure count 28→29; README's hidden-entry sentence; SCORECARD head and §Round 43 re-derived; `PROVINCE.md` hash re-anchored.
- **C2 work (commits `6fd85332`, `a2c70a73`):** `tools/hexrun-census.py` (18-case selftest), `registry/hexrun-ledger.tsv` (65 upstream rows with committed evidence under `.ufo/waves/round-43/c2/evidence/`, 9 unverifiable with reasons, 2 wrong with their correct tokens), the capability row `hexrun-census` in the round-43 canonical list.
- **C3 work (commits `1af8d516`, `6fd85332`, `a2c70a73`):** `corpus/knowledge/runtime-health-surface-processes.md`, rows S480 (v0.31.0 release, docs/A) and S481 (PR 58552, community/C), API copies and a `preload.py` copy at tag v0.31.0 under `.ufo/waves/round-43/c3/`, README coverage block and frontier disposition, `PROVINCE.md` Owns row and round-43 note, the lesson Gate with the Assimilation set.
- **Integration:** wave findings applied to the entry (the shipped route is one 200/503 route in `preload.py:73-75`; the three states are the PR description's, so the entry says so; `preload.py` at tag and merge commit are byte-identical, so the first-draft limit was closed with a committed copy). The merged entry cites two PR commit ids and the merge commit; each got a ledger row.
- **Tooling:** the L1 installed nothing. No seat reported an install; `gh` (already installed and authenticated) served the API reads. No pacman.

## Landed changes

Each change maps to a `LOG.md` entry (§Round 43) and to the commit that carries it. Commits are in the lane remote; the helper `jj-lane.sh` was not usable (above).

| Change | LOG entry | Lane commit |
|---|---|---|
| Freeze: preregistration, three counters, controls, census start, base-unresolved list | §Round 43, freeze bullet | `895793e0b4c56bdcb939277b8ff0251b26306d4d` |
| C3 API copies (release, PR 58552) | §Round 43 C3 | `1af8d5163163d8cf413887123d7b09beb14c6b75` |
| Integration: C1 rows and small fixes; C2 tool and ledger; C3 entry, rows, lesson, scratch; SCORECARD head, README, PROVINCE, QUALITY KQ54-KQ57, staged-refusals ledger; freeze-measured receipts | §Round 43 C1, C2, C3, Frontier | `6fd853327ae7a94776332f46f949c5a760def1d8` |
| Entry reads `preload.py` at tag v0.31.0; ledger rows for the PR commit ids and merge commit | §Round 43 C3 | `a2c70a731972ea1868d1289779a5e60ae3bb9651` |
| Wave-1 specs, dispatch, results, 38 seat reports; planned wave-2 spec (not dispatched); lesson wave findings | §Round 43 wave bullet | `25df591a4e50f315b920ec0d0acba6145989e267` |
| Measured receipts, end census, SCORECARD measured results, LOG wave and measured lines | §Round 43 | `9307b15e0731f91efbd17ea10ef0d579fc1c9065` |

Fleet repo: this report and an L0 line are committed through `fleet-commit.sh --as kama`.

Wave 1 role mix (38): executor 13, scribe 13, scout 5, connector 4, critic 2, mutation-tester 1. `@m_flash` roles (executor, scribe, critic): 28 of 38 (74%). **Attack seats (critic, mutation-tester): 3 of 38 (8%); the 25% attack share was to be met by wave 2 and is not met.** §3 floor mapping: the planner seat is held by the L1 (the validator rejects `planner`); the planning data walk was the prototype scans before the freeze. Reviewer seats: none ran (all 17 were in wave 2). Dead seats: **0**; seat W1K02 needed three nudges (80 minutes) and wrote its report. Answering models were not recorded; no claim depends on a seat's model. Misroot sweep (`git -C /home/vgpnk/Projects/shokunin status --porcelain`): untracked `.tower/`, `.ufo/state/disk-guard.log`, `.ufo/waves/round-30/`, `demo-cwd.txt`, none written by a kama seat; seat W1C03 reported creating three files at the fleet root and moving them into its seat directory, and none remain there.

Inherited state: the parked worktree's dirty porcelain (round-35/36 carry, the mutation-sandbox lineage, untracked seat reports) was neither authored nor resolved by this round; named, not touched (operator-owned L0). `corpus/lessons/round-42-verifier-spotcheck.md` routed six defects: item 1 D-C fixed (C1 `dc`); item 2 counters prove facts not sufficiency: **not closed**, wave 1 re-proved it (limits below); item 3 spot count restated (C1 `spot`, 29); item 4 README hidden entries (C1 `hidden`); item 5 operator-owned, open; item 6 the S-id cross-check, narrowed: a base prototype (`.ufo/waves/round-43/frontier/sid-prototype.out`) finds 298 URL-attributed S-id pairs in lesson prose, none naming a registered row wrongly and 13 naming staged or quarantined ids; the round-36 misattributions were descriptor-based and stay open for round 44. No `corpus/lessons/operator-*.md` teaching exists.

## Before → after measurements

All counters scored in a fresh clone of the lane remote at the measured commit `25df591a`; receipts under `.ufo/waves/round-43/`.

- **C1, calibration 7→7.**
  - Command: `python3 tools/round43-registry-audit.py --repo <clone> --tip <full commit> --out <receipt>`.
  - Base `6897ead5`: `unreg=16 defect=0 flags=2 pins=19 selftest=1 dc=1 spot=1 hidden=2 pop=28 registered=12 mismatches=42 met=False` (exit 1), `controls/base.c1.out`.
  - Measured `25df591a` (and the tip): `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=31 registered=31 mismatches=0 met=True` (exit 0), `c1/after.out`. Kill rule met False→True.
  - Limits, not repaired (counter frozen): W1R01 met the counter with one mega-row of 11 inserted lines and a decoy calibration row, leaving the self-description false (all 19 paths in one cell, one flag, a false exit map). The landed tree has 19 individual rows, so it is the honest tree, but `met=True` is necessary, not sufficient.
- **C2, operability 8→8, capability `hexrun-census`.**
  - Command: `python3 tools/round43-hexrun-audit.py --repo <clone> --tip <full commit> [--seed N] --out <receipt>`.
  - Base: `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` (exit 1), `controls/base.c2.out`; the base census of the same documents: 210 distinct runs, 136 lane objects, 1 MD5 of a blob, **73 unexplained** (64 upstream oids, 7 MD5s, one 39-hex, one 65-hex).
  - Measured: `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` (exit 0) at seeds 43, 7 (`c2/after.out`, `after-seed7.out`) and 1337 (at the tip); live scan `tokens=778 distinct=215 lane_oid=138 md5_blob=1 upstream_ok=65 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=0`; selftest `pass=18 fail=0` (`c2/selftest.out`); capability census `listed 8 observed 8` → `listed 9 observed 9 missing 0 unsubstantiated 0 met True` (`c2/capability-audit-after.out`).
  - Limits, not repaired: W1R02 met the counter with a 78-line tool that answers the twelve fixtures by directory name and imports the counter's own census; an `upstream` row whose evidence is a copy of the citing document is valid under the frozen semantics; the evidence files are committed bytes the counter cannot tie to GitHub (the closure re-queries a sample). The two implementations were not differentially tested (planned seat W2B09).
- **C3, coverage 9→9, assimilation.**
  - Command: `python3 tools/round43-health-audit.py --repo <clone> --tip <full commit> --base 6897ead55c24ba08c9ac0b09466d4fbfe005a459 --out <receipt>`.
  - Base: `entry=0 rows=0 coverage=0 gate=0 refetch=1 census=1 met=False` (exit 1), `controls/base.c3.out`.
  - Measured: `entry=1 rows=1 coverage=1 gate=1 refetch=1 census=1 met=True` (exit 0), `c3/after.out`; `refetch=1` means every frozen and every Gate quote also occurs in a live `gh api` fetch (control `junk-c3-fabricated` reads `refetch=0`).
  - Limits, not repaired: W1R02 met the counter with a keyword-shell entry over stub copies and two true but irrelevant live quotes; the entry's prose is checked by keyword, not read. The entry's sentences were checked against the sources by seats W1C01 and W1C04 and by the L1 (the preload.py digest at tag and merge commit), not by a reviewer wave.
- **Separability.** Not run (planned seat W2D08 belonged to the undispatched wave 2). K04's prediction: the claims are separable except that the two ledger rows for the PR commit ids the entry cites couple C2 to C3, and C1's NEWSET contains the other claims' counters. The head counters of rounds 41 and 42 still read `met=True` at the measured commit (`c1/r41-after.out`, `r42-after.out`).

## Sources & frontier

Registry rows went from **220 to 222** (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md`, exit 0 both times; `census-{start,end}-counts.out`).

| Measure | Start | End |
|---|---|---|
| Tier A | 210 | 211 |
| Tier B | 7 | 7 |
| Tier C | 3 | 4 |
| Status mined | 201 | 203 |
| Status queued | 8 | 8 |
| Status rejected | 11 | 11 |
| Missing | 0 | 0 |

Census command `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`: exit **0** at start and exit **0** at end (`census-{start,end}-fleetroot.out`); it reads the parked worktree's registry, not the tip (round-40 N4, still open). The same command on a mirror of the clone: exit 0, 93 W04, 0 E at start and end (`census-{start,end}-mirror.out`).

Rows added, both `mined`, opened 2026-10-25 (fetch `2026-10-26T01:46:17Z`, `.ufo/waves/round-43/c3/fetch-time.txt`; each re-fetched by an independent seat):

| Row | Tier, kind | Source | Located quote |
|---|---|---|---|
| S480 | A, docs | https://github.com/vllm-project/vllm/releases/tag/v0.31.0 (API copy 60454 bytes) | "a `/health` endpoint (#58552)" |
| S481 | C, community | https://github.com/vllm-project/vllm/pull/58552 (API copy 25514 bytes) | "Add an HTTP `/health` endpoint to the weight cache daemon parent process." |

- Rows touched old→new: none (no `status`, `recheck` or `used-by` changed).
- Frontier rows advanced: the health-probe frontier item (K05 stays runtime-blocked); the entry `corpus/knowledge/runtime-health-surface-processes.md` cites S480, S481 and the held S004. Round-43 is the sourced claim (C3).
- Lesson Gate: `corpus/lessons/round-43.md` §Gate (URLs, access date, quotes, the assimilation table).
- **Assimilation: one theme, runtime-health, from `merge/kama`.** Staged round-12 rows S430, S431 admitted and merged into one entry (renumbered by document to S480, S481; S441 collapses into S481); the round-13 rows S438, S439, S442, S443 refused with scope reasons and flips, S440 refused as a duplicate of the held S004. Source repo read-only: nothing was written into `/home/vgpnk/Projects/shokuknow` and no campaign tool was run.
- Id collision check (scratch, committed `.ufo/waves/round-43/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice,renumber-map.tsv}` and `guard/`): lane ids 220, staged ids 142, collisions 9 (`S330 S333 S334 S335 S346 S347 S352 S353 S363`), none adopted; the staged S430 and S431 do not collide, and adopted ids continue the lane registry at S480 (CORPUS rule 2). Renumber map: S430→S480 (release), S431→S481 (PR). Guard proof: an indented colliding row gives a nonempty collisions file with the 0-3-space pattern and an empty one with the column-zero-only pattern. The full id lists are in the committed `reg-ids` and `staged-ids`. Quarantine slice: 7 data rows (S200, S202, S206, S210, S211, S224, S230, all `payload-absent`); none appended.
- **considerthese:** `considerthese/2026-10-25.md` proposal 3 (ledger of repeatedly refused staged items) implemented as `registry/staged-refusals.tsv` (73 distinct refused items, 6 stale flips, one quarantine row the registry contradicts) and KQ57; proposal 1's non-64 hex-run half is C2.
- **Mistakes mined (lesson `## Mistakes`, five rows):** the registry gate never ran at round end (16 counters unregistered for eight rounds); the documented self-test line stale; the round-42 search-log line contradicting the Gate (D-C); a stale closure count in the calibration row; the digest ledger blind to non-64 runs (73 unexplained). KQ54-KQ57 added.
- **Held-entry defects found by wave 1, reported not edited:** `corpus/knowledge/served-model-id-resolution.md:46` cites a `CANNOT-ANSWER.md` that exists nowhere in the lane; eight held sentences need the process qualification (list in the lesson).

## Trend verdicts

- **expansion: improved.** One admitted entry on ground the lane did not hold (`weight cache daemon`, `vllm preload` had 0 hits at base), two mined rows (220→222), one new capability (`hexrun-census`, 73 unexplained runs to 0), a staged-refusals ledger. Not falsify-wave checked.
- **quality: unprovable-but-better.** The registry gate is green for the first time since round 35 (`registered 31 unregistered 0 defective 0`, selftest `pass=6 fail=0`), and the entry was corrected by source reading before landing; but wave 1 showed each counter is met by a shortcut, and no falsify wave ran, so the counters do not prove the quality. The closure judges.
- **discernment: unchanged.** Admit and reject decisions are recorded for the spot-check (two admits S430, S431; five refusals with flips), the wave's own attackers found the counters weak, and four seats' scope rulings were adopted; no outside discernment check of this round exists yet and the planned attack wave did not run.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources: `SKILL.md` now registers all 31 counters (§Round-43 registry completion; `.ufo/waves/round-43/c1/gate-after.out`); author assertion, no named non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md: `tools/hexrun-census.py scan` over the lane's own documents (`.ufo/waves/round-43/c2/scan-after.out`); the live llama.cpp lifecycle evidence of rounds 16-18 stands; no non-author mark.
- [~] Instructions executable by an agent without oral context: the 19 new rows give each counter's flags and exit codes (`SKILL.md` §Round-43 registry completion); independent execution review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate): `PROVINCE.md` round-43 note and `corpus/lessons/round-43.md` §Assimilation set refuse the gateway and router sources; no non-author review.

Open L0 questions: `kama | round-41` and `kama | round-42` (parked-worktree disposition) stay open and are refreshed by a `kama | round-43` line in this report's fleet commit; earlier kama L0s, round-35 (MISSION.md axes pair) and round-39 (validator band and planner), have no recorded answer and were routed around. The round's falsify wave and its 26 seats short of the 64-seat floor were not dispatched because run 7 closed; the next run re-dispatches round 43.
