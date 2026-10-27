# X01SiblingOverlap — evidence file (kama round 57, wave kama-r57-w1)

Read-only seat. The lane was not edited; no commit, push, jj or git mutation was issued. Every
fixture is a private git repository under `/fast/scratch/hyaku/kama-r57/X01SiblingOverlap/fx/`,
created from `git archive <rev>`; each fixture asserted `git rev-parse --show-toplevel` equal to
its own directory before `git add`/`commit`. Counter exports used `TMPDIR` pinned to
`/fast/scratch/hyaku/kama-r57/X01SiblingOverlap/tmp` (the round-41 counter calls `mkdtemp`).
Lane `$LANE` = `/home/vgpnk/Projects/shokunin/kama-shokunin`. Receipts in this directory are copies of
the scratch outputs (`receipts/`, `fixtures/`). No tool was installed or updated.

## Pins

| Name | Revision | Use |
|---|---|---|
| `B` (freeze base) | `b89bdab2cc114735ec5d331c6c610134258f7864` | round-56 tip; base of `controls/freeze.txt` |
| `H` (seat start) | `8640e34cad02adcd247ba0862da63f6fb2aab0df` | HEAD when the seat began reading the amendment commits |
| `H3` (seat end) | `3d2d5d4d6cba3028ec5358832a67f192cc0e41ec` | HEAD re-read later; 16efcf5e, 77e7f5ee, 3d2d5d4d landed during the seat |
| `7c873d7b` | `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` | commit whose `controls/freeze-amendment.txt` re-labels the claims |

Exports: `base-export` = B, `head-export` = 7c873d7b, `head2-export` = 8640e34c, `head3-export` = 3d2d5d4d.

## E1 — the frozen counters at the base and at head (exact stdout, exit)

Command (base): `cd base-export && python3 tools/round42-selfdesc-reconcile.py --repo $LANE --tip b89bdab2cc114735ec5d331c6c610134258f7864`
```
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
```
exit 1 (`receipts/r42-base.out`, stderr empty).

Command (round-41 leg alone, base): `python3 tools/round41-scorecard-reconcile.py --repo $LANE --tip b89bdab2…`
```
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
```
exit 1 (`receipts/r41-base.out`).

Count at the base, run inside `base-export`: `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` printed `43`.
`git ls-tree --name-only b89bdab2… corpus/lessons/ | grep -c 'verifier-spotcheck.md$'` → `43`; the 43rd file is `corpus/lessons/round-56-verifier-spotcheck.md`, added by commit `b89bdab2` itself (`git show --stat b89bdab2` → `1 file changed, 46 insertions(+)`). The SCORECARD calibration row at the base still says `→ \`42\``.

Command (head 7c873d7b): same counter with `--tip 7c873d7b4e3839489a93d6334cdf93fe5d34d19f` → identical stdout (`tip=7c873d7b…`, `r41=1 … maxN=56 met=False`), exit 1 (`receipts/r42-head.out`).

Command (head 3d2d5d4d): `python3 tools/round42-selfdesc-reconcile.py --repo $LANE --tip 3d2d5d4d6cba3028ec5358832a67f192cc0e41ec`
```
tip=3d2d5d4d6cba3028ec5358832a67f192cc0e41ec
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=57 met=True
```
exit 0 (`receipts/r42-head3.out`).

Capability census (`tools/capability-repertoire-audit.py`, existing lane instrument):
- base: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`receipts/cap-base.out`)
- 7c873d7b: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`receipts/cap-head.out`)
- 3d2d5d4d: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`receipts/cap-head3.out`)
- `--selftest`: `CAP_SELFTEST pass=2 fail=0`, exit 0 (`receipts/cap-selftest.out`); this exact command is a run fact in the calibration row.

Round-56 prereg checker (`tools/round56-prereg-check.py`, head2-export tools):
- at 3d2d5d4d: `tip=3d2d5d4d… present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 (`receipts/prereg-head3.out`).

## E2 — where `maxN` comes from, and the "expected 46" target

Source, `tools/round42-selfdesc-reconcile.py` (base and head identical):
- line 167: `rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]`
- line 168: `maxn = max(rounds)`
- line 190: banner requires `Latest measured round: <maxn>` in the head.
- line 195: planned requires `### Planned (round <maxn+1>)`.
- `maxN` is not a canonical-row count and is not counted in `mismatches`.

Base: the largest `^## Round N` heading is 56 (`grep -n '^## Round ' SC.base.md | tail -1` → `## Round 56 — LD_AUDIT …`). At 3d2d5d4d it is 57.

The value 46 appears in the lane tree as: `controls/c1-noop.py` (`print("mismatches=0 maxN=46 met=True")`), `controls/noop-c1.out` (literal `maxN=46`), `controls/noop-c2.out` (literal `maxN=46`), the first-working round column of `append-only-audit`, and prose. No formula in the counter produces 46.

Fixture fx7 (`fixtures/fx7-maxn46-probe.r42.out`): headings `## Round 47` … `## Round 56` demoted to `### Round N`; banner set to `Latest measured round: 46`; calibration count fixed to 43 (so the remaining legs are not the cause):
```
$ counter=r42 exit=1
tip=6fb1ee1d9948b03ff9e16332fa8bdf5c911eb920
r41=0 banner=0 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=46 met=False
detail: planned: section does not name '### Planned (round 47)'
```
exit 1. Forcing maxN to 46 therefore fails the planned leg; the frozen target as written is not reachable without breaking the counter's own banner/planned legs.

## E3 — canonical table selection (the stale-table path)

Marker lines `**Capabilities — canonical list as of round N**` in `B:SCORECARD.md`: lines 676 (16), 747 (17), 1957 (34), 2214 (41), 2261 (42), 2308 (43), 2451 (46), 2685 (47), 2789 (48), 2844 (49). Both `round42` `canon()` (line 120–127) and `capability-repertoire-audit.py` select the highest N present; neither compares it with `maxN` or with the latest round.

Rows per canonical table at B: round 48 = 11 rows; round 49 = 11 rows; names identical. Count of backticked `run` facts in the eleven round-49 rows: 0 (each row is `name | description | evidence path(s) | first-working round`).

Control `controls/no-canonical/SCORECARD.md` (frozen by 89dc4f52) contains the markers 16…48 and no round-49 table. Placed on the base tree (`fixtures/ctl-no-canonical-on-base`):
```
$ counter=r42 exit=1
tip=71b61ba952273f5f39bdd29c8f5ef5ac130c415a
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
```
`caps=0`: the counter fell back to the round-48 table without a finding. Capability census on the same fixture: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`fixtures/ctl-no-canonical-on-base.cap.out`).

Control `controls/canonical-noop/` is a partial tree (no `tools/`, no `.ufo/`, no `.git`). Placed as a fixture (`fixtures/ctl-canonical-noop`):
- r42: `r41=29 … receipts=9 … mismatches=38 maxN=56 met=False`, exit 1
- cap: `listed 11 observed 11 missing 0 unsubstantiated 10 met False`, exit 1
Its red result is caused by absent files (evidence paths and receipts point at `tools/`, `.ufo/`), not by canonical-row binding.

## E4 — canonical-row and run-fact binding fixtures (all from B; `fix_count` = calibration count 42→43 applied to every fixture)

Fixture definitions are the exact edits listed. `r42` = `tools/round42-selfdesc-reconcile.py`; `cap` = `tools/capability-repertoire-audit.py`; exits in brackets.

| fixture | edit (on top of count repair) | r42 | cap | file |
|---|---|---|---|---|
| fx0-base-frozen | none (frozen base) | `mismatches=1 met=False` [1] | `unsubstantiated 0 met True` [0] | `fixtures/fx0-base-frozen.*.out` |
| fx1-count-repair | calibration `42`→`43` | `mismatches=0 maxN=56 met=True` [0] | `met True` [0] | `fixtures/fx1-count-repair.*.out` |
| fx2b-canon-dangling-provinced-reanchored | round-49 pin-watch evidence → `tools/pin-watch-gone.py`; token appended to PROVINCE.md; PROVINCE sha256/line count re-anchored in the coverage row | `mismatches=0 met=True` [0] | `unsubstantiated 1 met False` [1] | `fixtures/fx2b-*.out` |
| fx2-canon-dangling-provinced (no re-anchor) | same without coverage re-anchor | `r41=2 … mismatches=2 met=False` [1] | `unsubstantiated 1 met False` [1] | `fixtures/fx2-*.out` |
| fx3-canon-evidence-erased | round-49 pin-watch evidence → `none` | `mismatches=0 maxN=56 met=True` [0] | `unsubstantiated 1 met False` [1] | `fixtures/fx3-*.out` |
| fx4-canon-row-deleted | round-49 pin-watch row deleted | `r41=0 … retired=1 saturation=1 caps=1 … mismatches=3 met=False` [1] | `listed 10 observed 11 missing 1 … met False` [1] | `fixtures/fx4-*.out` |
| fx5b-headmirror-dangling-reanchored | `## Capabilities` head-mirror pin-watch evidence → `tools/pin-watch-gone.py`; PROVINCE token + coverage re-anchor | `mismatches=0 met=True` [0] | `met True` [0] | `fixtures/fx5b-*.out` |
| fx5-headmirror-dangling (no re-anchor) | as fx5b without re-anchor | `r41=2 … met=False` [1] | `met True` [0] | `fixtures/fx5-*.out` |
| fx6-runfact-echo | calibration run command → `echo verifier-spotcheck; echo 43`, expected `43` kept | `mismatches=0 maxN=56 met=True` [0] | `met True` [0] | `fixtures/fx6-*.out` |
| fx11-canon-evidence-wrong-real-file | round-49 pin-watch evidence → `corpus/SOURCES.md` | `mismatches=0 met=True` [0] | `unsubstantiated 0 met True` [0] | `fixtures/fx11-*.out` |
| fx8-head-as-committed | 8640e34c tree | `maxN=57 met=True` [0] | `met True` [0] | `fixtures/fx8-*.out` |

Source references: round-42 `caps` leg compares names only (lines 223–224); round-42 `province` leg only checks `tools/`/`registry/` tokens appear in PROVINCE.md (lines 258–263); round-42 `rel` leg only checks that a run fact's text contains a needle (lines 265–268); round-41 `run_fact` accepts any stdout line equal to the expected text, regardless of the command (`round41-scorecard-reconcile.py` lines 131–140); round-41 `coverage` row hashes PROVINCE.md (`aa7915a8…` `(186 lines)`), so PROVINCE edits without re-anchoring fail the r41 leg (fx2, fx5).

## E5 — prereg checker (C1 of the 7c873d7b / 8640e34c amendment) against dead code

Source at 8640e34c `tools/round56-prereg-check.py` lines 61–71: `invoked` = labels of every `run(...)`/`assert_mutant_breaks_detection(...)` Call found by `ast.walk`, anywhere in the file; `executed = expected <= invoked`.

Fixture `fx10-prereg-deadcode` (from 8640e34c): `tools/round56-env-leg-battery.py` unchanged except appended
```
def _never_called():
    run('<label>')        # one line per roster label of .ufo/waves/round-56/preregistration.json battery.roster
```
Result: `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 (`fixtures/fx10-prereg-deadcode.prereg.out`). Control `fx9-prereg-head` (unchanged 8640e34c): `met=True`, exit 0 (`fixtures/fx9-prereg-head.prereg.out`). The amended C1 predicate ("executes none … rejected") is bypassed by dead code that merely contains the calls.

## E6 — frozen no-op controls

- `controls/c1-noop.py`: one `print("mismatches=0 maxN=46 met=True")`; `controls/noop-c2.out` prints `canonical_table_reads=0 self_description_reads=0 summary=mismatches=0 maxN=46 met=True`. Neither reads the lane; these are literal prints. They show that a hard-coded print can print `met=True`, which is not a test of any counter. The meaningful do-nothing tests in this seat are E4 fx6/fx3/fx11 (run the actual counter on a fixture) and E5 fx10.

## E7 — claim labels across freeze, dispatch, amendment, SCORECARD

- `controls/freeze.txt` (89dc4f52): `claims=C1 calibration stale canonical-table count; C2 operability canonical-row execution binding`, `base_counter=1`, `noop_C1=met=True exit=0 despite skipping data`, `noop_C2=met=True exit=0 despite skipping data`.
- `controls/freeze-amendment.txt` (7c873d7b, "correct frozen claim targets before data"): "supersedes the earlier round-57 freeze's claim ordering only, not its base/control evidence. C1 is the frozen round56-prereg-check no-op control defect, operability axis … C2 is the tools/round42-selfdesc-reconcile.py stale calibration count, calibration axis … update only the stale self-description count and require `mismatches=0`. C1 and C2 are distinct axes."
- `w1-dispatch.json` / `w1-spec.json` (89dc4f52 and later unchanged): X01 prompt says `C1 stale maxN and C2 canonical-row execution binding`; the Round-57 item text says `C1 stale count and C2 row-content execution target`.
- `SCORECARD.md` at 8640e34c and 3d2d5d4d §`## Round 57`: `C1 — bind declared roster to actual battery call sites | operability 8→8`; `C2 — re-anchor the SCORECARD verifier-spotcheck count | calibration 7→7`. `awk '/^## Round 57/…' | grep -ci canonical` → `0`.
- `corpus/lessons/round-57.md` at 3d2d5d4d: class `calibration-staleness` (round-42 counter, count 42 vs 43) and class `no-op-counter` (round-56 roster no-op); no canonical-row class.
- Round-56 outside closure (`b89bdab2:corpus/lessons/round-56-verifier-spotcheck.md`, lines 14, 44): C2 unprovable because `c2-noop-control.out` shows `met=True` for a literal roster; routed: "Strengthen C2-style calibration gates to bind actual executed battery entries … a roster literal/no-op harness must fail."

## E8 — shared-file and sibling scan (read-only git)

- `git --no-optional-locks log --oneline -8 --format='%h %ad %s' --date=iso` at seat time: `8640e34c 15:08:48 round-57: record measured counter outcomes`, `7b74e2f2 15:06:45 round-57: bind prereg roster to executed calls` (touched `tools/round56-prereg-check.py`, `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-57.md`), `7c873d7b 15:05:51`, `89dc4f52 14:42:40`.
- `git diff --stat 8640e34c 3d2d5d4d`: 6 files, 20 insertions, 5 deletions — `.ufo/waves/round-57/measured/{c1,c2}-committed-tip.out`, `LOG.md`, `SCORECARD.md` (round-57 table claims re-worded, S516 cited), `corpus/SOURCES.md` (+1 row), `corpus/lessons/round-57.md`.
- `git --no-optional-locks status --porcelain` at seat time: untracked `.ufo/scopes/`, `.ufo/waves/round-57/{ClaimFalsifier,NoopAttack,SourceAudit,reports,sources,w1/…}` (sibling seat outputs, not committed).
- Prompt-target scan (`w1-spec.json`, 64 items): `tools/round42-selfdesc-reconcile.py` is named only in E01CounterRepair ("Implement in private scratch copy only"); `corpus/lessons/round-57.md` only in S02LessonDraft. No other item names a file, so no prompt-level overlap beyond these two.
- `considerthese/2026-10-26.md` proposal 3 (counter-shortcut tally): `tools/shortcut-tally.py` already exists at B (v2, round 48; its docstring says it "promotes the round-47 draft … `considerthese/2026-10-26.md` proposal 3 to a lane tool"). The round-57 lesson's line `Assimilation: none. … proposal 3 (counter-shortcut tally) was opened; this round … does not implement a multi-round tally` does not cite that tool.

## E9 — axis authority (cited, not resolved)

- `/home/vgpnk/Projects/shokunin/shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`.
- `SCORECARD.md` line 6 (at B and at 3d2d5d4d): `MISSION.md:29 still says operability + freshness, an open L0 question since round 35`.
- Round-56 outside closure routed this conflict to the operator/L0 channel. This seat uses operability + calibration as the dispatch states.

## Commands used (all reproducible from the pins above)

```
git -C $LANE archive <rev> | tar -x -C <dir>               # exports and fixtures (rev = B, 7c873d7b, 8640e34c, 3d2d5d4d)
git init -q <fixture>; git -C <fixture> rev-parse --show-toplevel   # asserted == <fixture> before commit
TMPDIR=<scratch>/tmp python3 <export>/tools/round42-selfdesc-reconcile.py --repo <fixture|$LANE> --tip HEAD|<rev>
TMPDIR=<scratch>/tmp python3 <export>/tools/capability-repertoire-audit.py --repo <fixture|$LANE> --tip HEAD|<rev>
python3 <export>/tools/round56-prereg-check.py --repo <fixture|$LANE> --tip HEAD|<rev>
python3 tools/capability-repertoire-audit.py --selftest
```
Fixture edits were applied by Python string edits to the fixture's own SCORECARD.md / PROVINCE.md / battery file (never to `$LANE`).

## Limits

- Fixtures test presence and string disposition; they do not test whether a repaired counter is correct. fx11 shows an existing real file passes; fx6 shows a stdout line passes.
- `capability-repertoire-audit.py` counts a row as substantiated if ANY path token resolves (code read at lines ~141–146; not separately fixture-tested).
- The round-57 tips moved during the seat; counters were re-run at 3d2d5d4d only. The 16efcf5e and 77e7f5ee commits were not individually read beyond the stat above.
- Calibration-count lessons (E1) show the defect is recurrent: the round-47 section records `red at the base: the spot-check count 32 → 33` (SCORECARD.md line 2723 at B).
