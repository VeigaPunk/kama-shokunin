# kama round 55 report

Lane: kama (repo = `kama-shokunin`). Round 55, attempt 1. L1 agent id `KamaR55`.
Frozen claims: **C1 operability 8→8** (replay-code counter re-frozen for round 55) and
**C2 calibration 7→7** (cited-path counter frozen with the `superseded` ledger class).
Scores stay operability 8 and calibration 7; no capability enters
(`.ufo/waves/round-55/preregistration.json:11-33`). Base `3a600d2f729828419aaea34cc402c8b0d20fb720`;
freeze `9c60eae6f7ed84f7da93d219a406aadc30958c6c`; w1 build/dispatch
`8abadfedf89f35372645b1e5d6ce4a2109186f90`.

> Skeleton status: every numeric below is copied from a committed receipt or the
> preregistration at the commit named beside it. `[L1: …]` marks a fact that only the
> post-wave L1 can supply; nothing in those markers is pre-judged here.

## Work performed

Declared claims (frozen 2026-10-27T13:20:12Z, `preregistration.json:6`):

- **C1 operability 8→8** — `tools/round54-replay-code-audit.py`,
  `counter_sha256 c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`
  (`preregistration.json:15-20`; digest re-verified with `sha256sum` at the worktree of
  `8abadfed`). Freeze delta: BASE re-frozen to the round-54 tip, the `newrow` source row
  re-pointed at S511, every git call run with inherited `GIT_*` stripped
  (`counter` docstring `tools/round54-replay-code-audit.py:4`; `clean_env`
  `tools/round54-replay-code-audit.py:163-176`; diff `3a600d2f..9c60eae6` = 24 insertions,
  8 deletions).
- **C2 calibration 7→7** — `tools/round54-cited-path-check.py`,
  `counter_sha256 d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`
  (`preregistration.json:22-32`; digest re-verified). Freeze delta: the `superseded`
  ledger class and its fixture scenario; `counter_base` deliberately `0b75a84c…`
  (`preregistration.json:28`) so the drop horizon includes the round-54 re-anchor;
  `CLASSES` now carries `superseded` (`tools/round54-cited-path-check.py:167`);
  diff `3a600d2f..9c60eae6` = 81 insertions, 22 deletions.

Work items:

- **Freeze landed** — preregistration, both frozen counters, two red base controls, the
  S511 row, the `superseded` ledger row, the round-55 lesson and the start census in
  `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (`git show --stat 9c60eae6`: 10 files,
  16 117 insertions).
- **C1 build measurement** — `measured/c1-build.out` (landed in `8abadfed`; receipt
  `tip=9c60eae6…` line 1, leg line 2 `met=True`). All three v5 receipts replayed:
  `bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 twopass=3/3 anon=0`,
  8 archive libraries / 16 executable ranges byte-equal from `/proc/<pid>/mem`
  (`c1-build.out:5`), 5 env names with no `LD_PRELOAD` (`:6`), 8 paths re-hashed after
  exit (`:8`), `newrow=2 … 1 name the git environment doc: ['| S511 |']` (`:24`).
- **C1 kill battery** — `.ufo/waves/round-55/c1/battery/` (landed in `8abadfed`;
  harness `run-battery.py`, `FREEZE` pinned at `run-battery.py:14`). Receipts and their
  exact leg lines are in the measurement table below.
- **C2 build measurement** — `measured/c2-build.out` (landed in `8abadfed`; line 1
  `tip=9c60eae6… fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b`, line 2
  `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`).
- **Wave built and dispatched** — v2 wave `kama-r55-w1`: 64 seats in one swarm
  (`w1/spec.json` 64 items; `w1/dispatch.json` `counts {spawn:64,resume:0,total:64}`,
  64 entries in `taskCall.tasks`; `w1/out/swarm-registry.json` 64 members), role split
  executor 16, scout 10, reviewer 7, scribe 7, critic 6, mutation-tester 5, revenger 4,
  sentinel 4, connector 3, simplifier 2; `w1/validate.out`, `w1.ready` present.
- `[L1: wave outcome — one bullet per seat group (executors, mutation-testers, critics, reviewers, scouts, sentinels, scribes, simplifiers, revengers, connectors; the 64-seat roster and every seat name are in `w1/spec.json` items and `w1/out/swarm-registry.json` members) with the receipt path each landed; name any seat that contradicted a receipt or found a falsifying vector.]`
- `[L1: falsification/disposition bullets — which attack seats falsified which predicate or vector, and which of the preregistration's stated limits `preregistration.json:49` a seat narrowed, widened or emptied.]`
- `[L1: integration bullets — the SCORECARD `## Round 55` section, the LOG.md round-55 entry, the `corpus/README.md` frontier paragraph, and the SKILL.md registry re-anchor, each with the commit that carries it.]`

## Landed changes

| Change | LOG.md entry | Lane commit |
|---|---|---|
| Preregistration, both frozen counters (round-55 deltas), red base controls, start census, S511 row + used-by re-point, `superseded` ledger row, round-55 lesson | `[L1: LOG.md round-55 entry line range]` | `9c60eae6f7ed84f7da93d219a406aadc30958c6c` |
| C1/C2 build measurements, C1 kill battery (7 receipts + harness), v2 wave spec/validate/dispatch/registry/ready | `[L1: same or a second LOG.md paragraph]` | `8abadfedf89f35372645b1e5d6ce4a2109186f90` |
| `[L1: wave seat evidence commit(s) — the out/ tree at closure]` | `[L1: LOG.md pointer]` | `[L1: hash]` |
| `[L1: SCORECARD round-55 section, README frontier paragraph, SKILL.md registry re-anchor]` | `[L1: pointer]` | `[L1: hash]` |

No fleet-repo, sibling-lane or shokuknow mutation is claimed. `[L1: if any fleet-side file
(report, l0-questions) was committed, name the fleet commit here.]`

## Before → after measurements

Commands (both frozen, both run from a `git clone --shared` of the lane):

```
python3 tools/round54-replay-code-audit.py --repo <clone> --tip <full commit> --scratch <dir> --out <receipt>
python3 tools/round54-cited-path-check.py  --repo <clone> --tip <full commit> --scratch <dir> --out <receipt>
```

### C1 operability 8→8

- **Base control** — `.ufo/waves/round-55/controls/base.c1.out` (committed `9c60eae6`),
  `tip=3a600d2f…`, line 2:
  `bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False`;
  exit 1 as asserted at `preregistration.json:19` and `build_spec.py:25` (the receipt
  file itself carries no exit field — see the evidence limitation below).
- **Build measurement** — `.ufo/waves/round-55/measured/c1-build.out` (committed
  `8abadfed`), `tip=9c60eae6…`, line 2:
  `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True`;
  exit 0 as asserted at `preregistration.json:19`. Three replays, each from the
  committed round-48 v5 receipts; pids/ports/inodes vary by design across the three
  replay blocks occupying `c1-build.out:5-24`.
- **Flipping leg is `newrow` only** — the base control is red solely because S511 is
  absent at `3a600d2f`; every operative leg (`bind sealed code teardown twopass rehash
  bound/…`) is already green at base (`base.c1.out:2` vs `c1-build.out:2`). The delta
  the claim lands is the S511 row + the hermetic-git/newrow re-point, not a new
  observation leg this round.
- **Kill battery** — `.ufo/waves/round-55/c1/battery/`, all receipts committed
  `8abadfed`; line 2 of each receipt unless noted:

| Receipt | `tip=` (fixture clone) | Leg line | Verdict |
|---|---|---|---|
| `control.out` | `9c60eae6…` | `bind=1 … newrow=1 … met=True` | positive control passes |
| `m-ldpreload.out` | `585a6cb0…` | `… envnames=0/3 … met=False` | envnames leg kills |
| `m-text-flip.out` | `a12e2c0f…` | `bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 … coderuns=0/3 … rehash=3 met=False` | code/bind legs kill |
| `m-member-flip.out` | `ba085a8b…` | `… rehash=3 met=False` | rehash leg kills |
| `m-ldaudit-writable.out` | `23dc15da…` | `… code=1 … met=True` | no kill; **not a `MUTANTS` entry** in `run-battery.py:23-85` |
| `m-ldaudit-foreign.out` | `aa3c47cd…` | `… hostlibs=3/3 … met=True` (kind `vector`, harness comment `run-battery.py:52-56`, label `:59`) | no kill by design; LD_AUDIT vector void on this glibc |
| `m-extra-in-tree.out` | `312530a9…` | `… met=True` | no kill; **not a `MUTANTS` entry** — orphan receipt |

- Kill-rule disposition: `preregistration.json:20` falsifies the claim "if any battery
  mutant prints met=True". Receipts `m-ldaudit-writable.out` and `m-ldaudit-foreign.out`
  (`preregistration.json:44` names both; its description `:43` reads "each expected to fail
  the frozen counter with its named leg") print `met=True`; the current
  harness calls the latter a `vector`, and the build commit message reports "3 live
  kills + 1 vector analysis". The conflict is reported verbatim; it is not resolved
  here. `[L1: ruling/position — either the three `MUTANTS` kills are the battery and the
  two `met=True` receipts are disclosed as vectors/orphans, or the kill rule as written
  is not met.]`
- `[L1: battery exit codes — the `.out` receipts record `met=` but not `exit=`; record
  the observed exits here, or state them as re-derivable only by rerun.]`

### C2 calibration 7→7

- **Base control** — `.ufo/waves/round-55/controls/base.c2.out` (committed `9c60eae6`),
  `tip=3a600d2f… fleet=6c4aba34…`, line 2:
  `fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=1 met=False`,
  and the dropped citation is named verbatim: ``dropped citation `SCORECARD.md:
  corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)``
  (`base.c2.out:22`). Exit 1 as asserted at `preregistration.json:31`.
- **Build measurement** — `.ufo/waves/round-55/measured/c2-build.out` (committed
  `8abadfed`), line 2:
  `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`.
  Exit 0. The superseded scenario line: `fixture ok: superseded re-pointed citation
  discloses, forged superseded is bad` (`c2-build.out:17`), matching
  `registry/cited-path-corrections.tsv:46`.
- `[L1: X2C2Rerun stability — independent reruns at the freeze tip, verdict stability,
  wall time, and the field-by-field comparison against `measured/c2-build.out`.]`
- `[L1: separability evidence — K1DoNothing's two single-row flips (S511 only → C1 green,
  C2 red; superseded row only → C2 green, C1 red) with receipt paths, or the seat's
  contrary finding.]`

### Evidence limitations recorded now (not re-measured this seat)

- The receipts carry `tip=`, the aggregate leg line and `detail:` lines only; **no
  `exit=` field** exists in any of the eleven base/build/battery `.out` files
  (4 base/build + 7 battery). Exit codes
  live in `preregistration.json:19,31` and `build_spec.py:25-26`.
- Battery receipts are produced against per-mutant fixture-clone commits, so `tip=`
  differs per receipt; only `control.out` carries `tip=9c60eae6…`.
- `run-battery.py` prints its per-mutant summary (`leg=… exit=… met=…`,
  `run-battery.py:146`) to stdout; no summary file is committed.

## Sources & frontier

- **Census before** — `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate
  --root /home/vgpnk/Projects/shokunin kama` → **exit 1**, receipt
  `.ufo/waves/round-55/census/start.out` (102 lines; line 102 `census_start_exit=1`):
  `E11 S510 missing used-by corpus/lessons/round-54.md` plus standing W01/W04 warnings
  (S189, S191, S481, S499, S509, S510 duplicate URLs).
- **Census after** — `[L1: rerun the same command at round end, paste the output and
  exit code; commit `.ufo/waves/round-55/census/end.out`. Exit 0 is required for
  conformance. NB: `corpus/lessons/round-55.md:98-101` already pre-claims that receipt
  and its exit 0, and no `end.out` exists at `8abadfed` — commit it or correct the
  lesson.]`
- **Rows added** — one: **S511**, tier B, mined (`corpus/SOURCES.md:264`), git-config(1)
  `GIT_CONFIG_COUNT` (HTML copy `.ufo/waves/round-55/sources/git-docs-git-config.html`),
  opened 2026-10-27, 23-word located quote in `corpus/lessons/round-55.md:32-43`.
- **Rows touched old→new** — one: S510 `used-by` old `corpus/lessons/round-54.md` → new
  `corpus/lessons/round-55.md` (`corpus/SOURCES.md:263`; recorded
  `corpus/lessons/round-55.md:52-56`). No other cell changed: diff
  `3a600d2f..9c60eae6 -- corpus/SOURCES.md` is 2 insertions / 1 deletion.
- **Rejected candidate** — proc(5) `maps` pathname semantics: rejected with flip
  condition (`corpus/lessons/round-55.md:44-51`).
- **Frontier** — no knowledge entry admitted; no capability enters. Round-55 frontier
  ground is the replay-code identity and cited-path dispositions already carried by the
  two counters. `[L1: frontier rows advanced this round, if any wave seat opened a new
  row; and the `corpus/README.md` frontier paragraph pointer.]`
- **Assimilation** — none from shokuknow (`corpus/lessons/round-55.md:115`).
- **considerthese disposition** (`corpus/lessons/round-55.md:103-113`): proposal 2 landed
  as KQ97 (round 54); proposals 1 and 4 pending with owner named; proposal 3 partially
  served by the battery receipts, standing tally pending.
- `[L1: rows added by tier tally (mined/rejected/correction) with the final numbers.]`

## Trend verdicts

- **Expansion — `[L1: improved|unchanged|harmed|unprovable-but-better]`.** `[L1: evidence
  — knowledge entries admitted (none declared at freeze), corpus ground covered, or the
  explicit reason expansion did not move.]`
- **Quality — `[L1: …]`.** `[L1: evidence — which measurement strengthens, which
  falsification the wave produced, and whether the battery/kill-rule conflict above
  counts as harm to measurement integrity.]`
- **Discernment — `[L1: …]`.** `[L1: evidence — the outside non-author closure's routed
  defects handled, and whether any independent non-author verifier beyond the wave seats
  ruled this round.]`

## SHONEN

One line per box of `SHONEN.md` (boxes at lines 5, 7, 9, 11); `[x]` only with a named
non-author verifier, `[~]` with a resolvable pointer, `[ ]` untouched.

- `[L1: [x]|[~]|[ ]]` SKILL.md contains real decision tables, error patterns,
  checklists, cited sources — `[L1: pointer; note that SKILL.md:1598-1599 still pin
  C1 base `0b75a84c` and `scenarios=N/14`, stale after this freeze.]`
- `[L1: …]` At least one end-to-end domain task executed and logged in LOG.md —
  `[L1: LOG.md round-55 entry line, or state that no LOG entry landed.]`
- `[L1: …]` Instructions executable by an agent without oral context — `[L1: pointer.]`
- `[L1: …]` No cross-domain bleed (PROVINCE.md still accurate) — `[L1: pointer; the
  freeze touched only tools/, corpus/, registry/, .ufo/waves/round-55/.]`

## Notes for the closure

- **Round shape** — 1 v2 wave, 64 seats, one batched swarm (attack + verification
  together); role split as in *Work performed*. `[L1: seats settled vs dead; attack
  share; seats that yielded no artifact.]`
- **Dead seats / provider exhaustion** — `[L1: tally and cause, or "none".]`
- **Stale-lane** — respawn-per-round driver; no other mission of this lane open
  (`[L1: confirm at round end]`).
- **Open L0 question** — the ed135b3c keep/remove/keep-with-retraction ruling remains
  operator-owned (forwarded in rounds 52, 53, 54 at `.ufo/l0-questions.md:184-187`);
  no round-55 claim depends on it. `[L1: forward again if still unanswered.]`
- **Tool installs** — none this seat (no pacman, no uv/npx; system `python3` and `git`
  only). `[L1: same line for the L1 seat; record tool/version/channel/reason if any.]`
- **Scratch** — `[L1: state that every seat's `/fast/scratch/hyaku/kama-r55/...` tree was
  removed and that no `/tmp` path is cited as evidence.]`
- **Filing** — report path `{{FLEET_ROOT}}/.ufo/reports/round-55/kama.md`; lane commit
  `round-55` + fleet report commit `[L1: hashes]`.

## Reported conflicts (for the canonical judge; no adjudication here)

1. `preregistration.json:44` lists `m-ldaudit-writable` and `m-ldaudit-foreign` among
   the battery mutants (`:43` description: "each expected to fail the frozen counter with
   its named leg"); `preregistration.json:20` falsifies the claim if any mutant
   prints `met=True`; both receipts print `met=True`
   (`c1/battery/m-ldaudit-writable.out:2`, `c1/battery/m-ldaudit-foreign.out:2`), while
   `run-battery.py:59` labels `m-ldaudit-foreign` a `vector` (comment `:52-56`) and the build commit
   message says "3 live kills + 1 vector analysis".
2. `c1/battery/m-extra-in-tree.out` and `c1/battery/m-ldaudit-writable.out` are not
   produced by the committed harness (`MUTANTS` at `run-battery.py:23-85` has
   `m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`, `m-member-flip`), so two receipts
   in the battery directory are unattributable to the frozen harness revision.
3. `corpus/lessons/round-55.md:98-101` states the round ends with census exit 0 and
   receipt `.ufo/waves/round-55/census/end.out`; that receipt does not exist at
   `8abadfed` (only `census/start.out`, exit 1).
4. `SKILL.md:1598` pins the C1 counter's base as `0b75a84c` and `SKILL.md:1599` states
   `scenarios=N/14` / "fourteen constructed scenarios"; the frozen round-55 state is base
   `3a600d2f` (`preregistration.json:7`) and 15 scenarios
   (`measured/c2-build.out:2`).
5. Base controls are red on metadata legs only: `newrow=0` for C1 and `lane=0`/`dropped=1`
   for C2 (`controls/base.c1.out:2`, `controls/base.c2.out:2`), while every operative
   C1 observation leg is green at base.
