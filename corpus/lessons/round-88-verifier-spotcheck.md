# Round 88 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-06
subject: kama round 88. Lane HEAD `64eaf5969e11e8955636dfb52c13eb089f731d9a`, base `9b4c7af16fdd4bba9e4815f4615f4b003f340747`, freeze `fb76e7f26d6582bd087935a00f8dc43af4db912f`, measured commit `138a75437bcd11b72446087e970f5dfc5abf9ccd`
report: `.ufo/reports/round-88/kama.md` (fleet repo, commit `614376b750c64c8689ec9ef8fb8c21cbaefcd9aa`, author `kama-shokunin <kama@shokunin.local>`)

Verdict: status `ok` (real report, real committed work). C2 calibration is **verified** on its frozen predicate. C1 operability is **not verified as a clean claim**: at the measured commit its frozen predicate was green, but that green includes two expectations the round's own oracle falsified, so the measured commit traded operability. At the landed tip the frozen predicate is red (`mismatches=2`). Trend expansion is **harmed**: the round's knowledge admission failed the bar it was admitted under at its landing commit and was repaired later in the same round. Round **not admitted** (`rejected-honest-stop`). No axis is harmed at the landed tip.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an <%ae> %H %ci' -- .ufo/reports/round-88/kama.md` | `kama-shokunin <kama@shokunin.local> 614376b750c64c8689ec9ef8fb8c21cbaefcd9aa 2026-11-06 16:22:42 -0300` | ok |
| report lands last | `git log --format='%h %ci' 9b4c7af1..64eaf596` | lane tip `64eaf596` at 16:21:17, report at 16:22:42 cites `64eaf596` | ok |
| SHONEN heading, one line per box | report `## SHONEN`; `grep -c -E '^\s*- \[[ x~]\]' SHONEN.md` → `4` | 4 lines, all `[~]` with a pointer, no `[x]` | ok |
| required sections | report headings | Work performed, Landed changes, Before → after, Sources & frontier, Trend verdicts, SHONEN, seats, Mistakes, Limits | ok (cross-domain evidence appears only inside the SHONEN adjacency line; D5) |
| cited commits exist and are ancestors of `master` | `git cat-file -t` + `git merge-base --is-ancestor <h> master` for `9b4c7af1 fb76e7f2 68ab526e 138a7543 f77d2ae9 8b5bb69d eb664062 f7be6d47 12eedc6b 64eaf596` and inherited operator commits `3f3846a1 cdc9a5f6` | all `commit`, all ancestors. The nine round commits after the base are authored by `kama-shokunin`. The base `9b4c7af1` is the `protocol-shokunin` r87 spot-check commit. The two operator commits are by `João Pedro Veiga`, as the report says | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `branch=master local=64eaf596… remote=64eaf596… ahead=0 behind=0 head=detached tracked=0 untracked=0`; status empty; remote `64eaf5969e11e8955636dfb52c13eb089f731d9a` | ok |
| fleet repo leftovers | `git status --porcelain` (fleet root) | only ` M .scratch/run15-state.json` (orchestrator-owned; not touched here) | ok |
| prompt carries contract | `.ufo/prompts/kama-round-88.md` (923 lines, committed `ddf6f8f3` by `kama-shokunin`) | §1 MISSION/AXES binding and 1–3 claims, §2b frontier step, §3 L2 floor, §4 report path/SHONEN/hash rule, §5 commit order, push scope, L0 channel, write scope, §6 hyaku addendum | ok |
| dispatch digest | `.ufo/watchdog.log` (mutable; digest copied) | `2026-11-06T15:39:30-03:00 launch kama round=88 pgid=1085765 driver=hyaku-inline attempt=1`; `2026-11-06T16:23:05-03:00 complete kama round=88; hyaku-inline attempt=1` | recorded |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, final line `kama ok`; warnings only: the W04 duplicate-URL-across-scopes notices and the W01 on S481, both present before the round | ok |
| census before → after | awk over committed `corpus/SOURCES.md` at `9b4c7af1` and `64eaf596` | rows 320 → 322; tier A 305 → 307, B 11, C 4; mined 287 → 288, queued 8, rejected 25 → 26 | matches report |

Conformance defects (status-neutral):

- **D1** The SCORECARD capability row `router-mode-readiness` (tip line 204) describes the repaired rule (sleeping and autoload-unloaded graded `MODEL_OK`). Its first evidence pointer, `ROUTER_CELLS cells=17 mismatches=0` at `138a7543`, certifies the earlier rule, which graded those states `MODEL_UNLOADED`. The landed rule's only green is the post-freeze 3-cell `repair/oracle-cells.py`.
- **D2** `measured/harm-tip.out` records `ORACLE_CELLS rev=master`, a symbolic revision rather than a hash. It still resolves: the receipt's `probe_sha256=99dd1ab8…` equals `sha256(git show 64eaf596:tools/kama-probe.sh)`. But a verdict must name the revision it measured (§Gate standard, Two evidences).
- **D3** The terminal gate is red on `round75-instruments` (`bad_rows=19`, carried from r87 R4; `measured/gate-final.out` `failed=1`). Status-neutral under §Gate standard, Closure consequence. Routed again.
- **D4** The answering model per seat is still not recorded in `w1-results.json` (r87 R11 carried).
- **D5** The report has no separate cross-domain-evidence section. Its content (CN01 found no contested scope; kengaku:57 and kagi:43 corroborate) appears only in SHONEN box 4.

## 2. Claim re-checks

Method: measurements I ran myself are marked **re-measured** (`git show`, `git diff`, `sha256sum`, `grep -c`, `awk`, `diff`, `curl`). Lane-owned counters, gates and selftests (`round88-router-cells.py`, `oracle-cells.py`, `round42-selfdesc-reconcile.py`, `round69-newest-closure-counter.py`, `pre-report-gate.py`) were **not executed**. For those I checked the committed receipts for revision, bytes and verdict; they are marked **evidence-verified**.

### C1 — operability: llama.cpp router-mode readiness verdicts in `tools/kama-probe.sh`

Re-measured:

- Counter bytes: `git show <r>:tools/round88-router-cells.py | sha256sum` → `576a1b374c9150db…` at `fb76e7f2`, `138a7543`, `8b5bb69d` and `64eaf596`, so the counter was never edited after freeze. `git log 9b4c7af1..64eaf596 -- tools/round88-router-cells.py` → only `fb76e7f2`.
- The receipts ran the probe bytes they claim. `sha256(git show <r>:tools/kama-probe.sh)` equals each receipt's `probe_sha256`:
  - base `0943fb46…` (`controls/c1-base.out`)
  - M `bd7a6a22…` (`measured/c1.out`)
  - repair `cbdfa744…` (`repair/c1-frozen-at-repair.out`)
  - tip `99dd1ab8…` (`measured/harm-tip.out`)
- Probe vocabulary `grep -c` at base → M → tip: `MODEL_UNLOADED` 0 → 9 → 10, `router_refine` 0 → 2 → 2, `sleeping` 0 → 1 → 5, `models_autoload` 0 → 0 → 3. The autoload branch exists only after the repair.
- `git diff --stat 9b4c7af1 64eaf596 -- tests/` is empty, so the harm-suite inputs are unchanged.
- S581 at the pinned commit (`curl` raw README @ `704366d7`, sha256 `714c067b…`, matching the Gate row), line 2337: "Any new incoming task will automatically trigger the model to reload." The source the lane opened **before freeze** already contradicted the frozen canned expectation C05 `sleeping → MODEL_UNLOADED`.

Evidence-verified receipts:

| revision | frozen counter (`ROUTER_CELLS`) | oracle cells (completion = ground truth) | harm suites |
|---|---|---|---|
| base `9b4c7af1` | `mismatches=11` exit 1; forgeries F1 `8`, F2 `4` | `mismatches=1` (no-autoload unloaded graded OK) | `tests=72 passes=72`, `RESULT pass=30 fail=0` |
| M `138a7543` | `mismatches=0` exit 0, `probe=rev` | `mismatches=2` (S1 sleeping, A1 autoload-unloaded: probe `MODEL_UNLOADED`, oracle 200) | same |
| repair `8b5bb69d` / tip `64eaf596` | `mismatches=2` exit 1 (C05, C12) | `mismatches=0` | same |

Ruling: **not verified**. The frozen predicate is literally met at M, and none of the frozen kill clauses fire there. But the green at M includes two cells whose frozen expectations were wrong by the round's own oracle definition (completion 200 → `MODEL_OK`) and by S581:2337. So the measured commit regressed two router states that base graded correctly (oracle cells 1 → 2 mismatches on different states). That is a trade at the measured commit (AXES: "a trade anywhere is not an improvement"). The repaired tip removes the trade, but then the frozen predicate is red, and the repaired rule is graded only by an instrument written after the data. Neither revision gives a clean verification.

Non-author judgment on the landed change: **better**. It fixes a real false green: base printed `MODEL_OK` for a model a `--no-models-autoload` router refuses with `400 model is not loaded`. The tip follows the runtime's answer on every observed cell. The axis is graded `unprovable-but-better`. That records a judgment, not an admission, because C1 was declared measurable, not exploratory.

### C2 — calibration: SCORECARD self-description vs repo state

Re-measured:

- Live `## Axes` table (awk over rows between `## Axes` and the next heading): base `live_rows=7 calibration_rows=2` → M `6 / 1` → tip `6 / 1`.
- The single live calibration row at M points to `corpus/lessons/round-87-verifier-spotcheck.md`. That is the newest committed verifier spot-check at M (`git ls-tree -r --name-only 138a7543 corpus/lessons | grep verifier-spotcheck | sort -V | tail -1`).
- Moved rows are verbatim: `diff <(git show 9b4c7af1:SCORECARD.md | sed -n '18,19p') <(git show 138a7543:SCORECARD.md | sed -n '27,28p')` → empty.
- Instruments are byte-identical at base, M and tip: `round42-selfdesc-reconcile.py` `3d9aff8f…`, `round41-scorecard-reconcile.py` `c9bb4eae…`, `round69-newest-closure-counter.py` `edf6c49a…`.
- No score cell moved. The `git diff 9b4c7af1 64eaf596 -- SCORECARD.md` axis lines show depth 7, coverage 9, adjacency 7 and calibration 7 rewritten with the same scores; operability and freshness are untouched. SKILL hash re-anchored: the cited `1c6c2973…` equals `sha256(git show 64eaf596:SKILL.md)`.

Evidence-verified: base `mismatches=4 met=False` / `STALE_CALIBRATION` exit 1. The pointer-only partial control stays at `mismatches=4`. M gives `mismatches=0 met=True` / `NEWEST_CLOSURE … row_current=true` exit 0 (`measured/c2.out`, `# rev=138a7543…`). Gate arms `selfdesc` and `newest-closure` are ok at `12eedc6b` (`measured/gate-final.out`).

Ruling: **verified**. The do-nothing and partial controls stay red, and the instruments predate the round.

## 3. Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| operability | unprovable-but-better | C1 not verified (trade at M, frozen predicate red at tip); landed probe judged better by this non-author reviewer (§2 C1) |
| calibration | improved | C2 verified (§2 C2) |
| freshness | unchanged | no claim; score 8 unchanged. The pinned-fixture restore (`r78` selftest 0/4 → 4/0) is a prerequisite, not a claim |
| depth | unchanged | score 7 unchanged; SKILL +31 lines (decision table for router states) |
| coverage | unchanged | score 9 unchanged |
| adjacency | unchanged | score 7 unchanged; CN01 found no contested scope |

## 4. Discernment spot-check (`corpus/lessons/round-88.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S581 llama.cpp server README @ `704366d7` (b11755) | admit (A, mined) | `curl` raw URL → sha256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` (matches row); line 1849 is the quoted sentence verbatim; status list at 2059 | agree | Primary doc at the exact commit of the pinned binary. The quote is located exactly and has 18 words (≤25). The lane under-read its own admitted source: line 2337 contradicts the frozen sleeping rule (captured as M5/KQ141) |
| S582 llama.cpp server README @ master `954de248` | reject | `curl` raw URL → sha256 `eafc1b53…` (matches row); line 2265 `The \`status\` object can be:` verbatim; `diff` of the status block vs S581 lines 2059–2125 → identical | agree | The text adds nothing over S581, and citing a revision newer than the pinned build would bind the verdict to bytes the binary was not built from. The stated flip condition is sound |
| `corpus/knowledge/router-mode-readiness.md` | admit (reason corrected in-round) | `git show 138a7543:corpus/lessons/round-88.md` Gate row 3: "New coverage ground … every row of its observation table is a committed receipt"; `git show 9b4c7af1:corpus/knowledge/served-identity-crosswalk.md:28` already carries the router `status.value` vocabulary; `git log -- measured/router-lifecycle.out repair/pilot-live-1234-after.out` → first landed at `eb664062`/`8b5bb69d`, after `138a7543` | agree with the final admission; **disagree with the admission as landed at `138a7543`** | Both stated grounds were false at landing (prior art held; receipts not yet committed). The corrected reason (verdict rule checked against completions, plus the `400 model is not loaded` signature) is true at the tip. Basis for expansion `harmed` (§5) |
| round-87 C1 successor selector | reject (not re-frozen) | `corpus/lessons/round-87-verifier-spotcheck.md` §2 C1 | agree | Five rejected closures on lane-authored prose selectors; dropping the line and requiring an outside oracle (KQ142) is the right call |

SOURCES row re-opened: `corpus/SOURCES.md:336` (S581). The quote "`llama-server` can be launched in a **router mode** that exposes an API for dynamically loading and unloading models." is found verbatim at README line 1849 of the pinned commit (18 words, ≤25). Census validate exit 0 (§1).

Criteria check: `corpus/QUALITY.md:683-685` KQ141/KQ142/KQ143 exist and each cites its lesson (M5, M1, M4).

## 5. Trend verdicts

- **expansion: harmed.** At its landing commit `138a7543`, the admitted entry `router-mode-readiness.md` failed the bar it was admitted under: "new coverage ground" was false (prior art at `served-identity-crosswalk.md:28`), and the "committed receipt" rows did not exist yet. It was repaired in-round at `eb664062`. LEARNING's harmed condition and the kengaku r25 precedent ("errata appended, but the admissions failed their own bar at landing") apply. The genuine growth is a trade, not an improvement: `pinned-fixture-restore` was demonstrated cleanly (`controls/fetch.out`, refusal control, r78 selftest 0/4 → 4/0), and the router rule has its D1 pointer defect.
- **quality: unprovable-but-better.** The router `status` vocabulary had been held as "source reads only" (`corpus/README.md:234` at base). It was re-verified live on lane-owned b11755 children (`measured/router-lifecycle.out`). LEARNING's `improved` also requires "no admitted entry failing its re-check", and the round's own new entry failed RV02's re-check at `138a7543`, so `improved` cannot be graded. The failure was marked and corrected, not left standing, so `harmed` does not apply either.
- **discernment: improved.** The non-author spot-check agrees with the gate on the source admit (S581) and the source reject (S582). The two in-round disagreements (CN01 admission reason, CR01 rule vs oracle) became lessons M4/M5 with grounded criteria KQ143/KQ141.

## 6. Routed defects (lane owes next round)

- **R1** C1 successor: freeze a router-cells counter with held-out cells. It must take every canned expectation from S581 or the runtime oracle, not lane prose, and cover the sleeping and autoload configurations, MT01's 6 escapes and SN01's counter defects (oracle socket identity, SIGTERM child leak, environment faults as exit 2). Already listed in SCORECARD §Planned (round 89).
- **R2** D1: annotate or re-point the `router-mode-readiness` capability row's evidence so it names a green for the landed rule, not the `138a7543` green of the superseded rule.
- **R3** D2: re-issue tip receipts with a hash, not `rev=master`.
- **R4** `round75-instruments` `bad_rows=19` (r87 R4, still red).
- **R5** `tests/probe-verdicts/check.py` cannot grade `MODEL_UNLOADED` rows (RV01/EX02).
- **R6** Record the answering model per seat (r87 R11).
- **R7** When a source is opened before freeze, sweep it against every frozen expectation. S581:2337 was in hand when C05 was frozen (M5 records this; KQ141 binds it).

## 7. Notes for the operator

- All four SHONEN boxes look checkable by a non-author from the cited files: SKILL §"Round-88 router-mode readiness" (decision table, `400` signature, S581), `LOG.md:3660` with `measured/router-lifecycle.out`, the commands in SKILL, and the PROVINCE round-88 paragraph. Promotion is operator-owned; nothing is marked here.
- The report says the `selfdesc` L0 question (r87) may be closable: the arm is green at `12eedc6b` with unchanged instruments.
