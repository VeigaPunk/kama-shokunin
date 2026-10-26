# S9Log — round-49 LOG.md `## Round 49` entry (lane kama)

**Verdict: draft delivered, paste-ready, and fact-checked line by line against committed receipts and git objects — with one correction I made to my own framing (the 7 lines v4 re-grades are K2Origin F6's head *mirror* rows, a definition-level false positive, not a lane laundering instance) and one calibration gap I could not close from the lane tree (the head calibration cell still says 34 spot-check files where the tree holds 35, so `r41`/`r42`/`r43` are red at the build).** I ran no counter and no lane tool; every number in the entry is either a committed receipt or a git object I read. Nothing was installed, no server was started, no lane file was edited.

## 1. Deliverable

- `.ufo/waves/round-49/w1/out/S9Log/log.md` (12,710 bytes, 10 lines: heading, C1, C2, routed defects, freeze+build+wave, blank, integration placeholder, blank, lesson).
- Paste at the end of `LOG.md` (`LOG.md` is append-only; the current working-tree file is 2338 lines and already carries a sibling draft at `LOG.md:2331` — see F3).
- Placeholders, all deliberate, all filled at integration:
  - `__WAVEDONE__` — wave settlement (`seat-yield-w1.out`, `w1-results.json`).
  - `__INTEGRATION__` — the integration item list of round 49 (SOURCES/KQ, `SKILL.md` §Round-49 registry, capability rows, PROVINCE cell, post-wave fixes).
  - `__MEASURED__` — the measured commit.
  - `<suffix>` — the second argument of `.ufo/waves/round-49/measured/measure.sh <tip> <suffix>`; the entry says so inline.

## 2. Evidence: what I executed

All commands from `/home/vgpnk/Projects/shokunin/kama-shokunin` unless stated. Clone: `git clone -q --shared … /fast/scratch/hyaku/kama-r49/S9Log/lane`, `git -C … checkout -q --detach 74558c71…`, `rev-parse --show-toplevel` printed the scratch clone before any git call that writes (only the checkout did).

| # | command | output | exit |
|---|---|---|---|
| 1 | `git diff --stat 36d5ed26 74558c71` | `corpus/SOURCES.md \| 2 +`, `tools/append-only-audit.py \| 101 ++`, `tools/kama-live-replay.py \| 27 ++`, `tools/kama-llamacpp-live.py \| 151 ++`; `4 files changed, 251 insertions(+), 30 deletions(-)` | 0 |
| 2 | `git show 36d5ed26:tools/round49-replay-witness-audit.py \| sha256sum` | `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` = prereg `claims[0].counter_sha256` | 0 |
| 3 | `git show 36d5ed26:tools/round49-append-audit-v4-check.py \| sha256sum` | `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` = prereg `claims[1].counter_sha256` | 0 |
| 4 | `git diff --name-only 438127bc 74558c71` | 17 paths: 11 under `.ufo/waves/round-49/`, `corpus/SOURCES.md`, the two frozen counters, and the three tools | 0 |
| 5 | `git diff --stat 438127bc 74558c71 -- SCORECARD.md` | empty — the 72 → 65 change is the definition, not the file | 0 |
| 6 | `git log --oneline -6` (lane) | `122c4ee9` wave spec / `74558c71` build / `36d5ed26` freeze / `438127bc` round-48 closure | 0 |
| 7 | `git cat-file -p 36d5ed26`, `… 74558c71` | freeze parent `438127bc`, build parent `36d5ed26`, both by `kama-shokunin <kama@shokunin.local>` | 0 |
| 8 | `python3 check7.py` (mine, `.ufo/waves/round-49/w1/out/S9Log/check7.py`) | for each of the 7 rows in `X2Lane/regraded-7.tsv`: `section_at_parent = Capabilities`, `section_at_first` = `Round 34 …` (6 rows, first blob `29f9d1e1`) or `Round 41 …` (1 row, `24aa1d34`), `held_at_82b5e9d3 = true`, `held_at_build = true` → `seven-lines.json` | 0 |
| 9 | `python3` count over `.ufo/waves/round-49/census/start.out` | 96 lines, `W04` 93, `W01` 1, `E` 0, last line `exit=0` (S481 is the `W01`) | 0 |
| 10 | `python3` role census of `.ufo/waves/round-49/w1/out/swarm-registry.json` | 71 members: executor 23, scribe 12, reviewer 11, critic 8, connector 5, mutation-tester 4, scout 4, sentinel 2, revenger 1, simplifier 1 (`dispatch.json` `counts.spawn = 71`) | 0 |
| 11 | `ls corpus/lessons/*verifier-spotcheck.md \| wc -l` in the build clone; `grep -n "34" SCORECARD.md:18` | `35`; the `## Axes` calibration cell states `34` | 0 |
| 12 | `git ls-tree -r --name-only 74558c71 \| grep -c "round-49/measured"` | `0` (the build receipt directory is untracked) | 1 (grep, no match) |
| 13 | `wc -l LOG.md`; `grep -n "^## Round 49" LOG.md` | `2338`; `2331:## Round 49 — a replay an outside observer can watch run; …` (a sibling's uncommitted draft) | 0 |

Receipts I read (not executed): `.ufo/waves/round-49/measured/{c1-build,c2-build,aoa-build,aoa-selftest-build,gate-build,r41-build,r42-build,r43-build,pointer-build,digest-build,hexrun-build,sao-build,klr-selftest-build,live-selftest-build,cr-selftest-build,tally-build,r48c1-build,r48c2-build}.out`, all five `.ufo/waves/round-49/controls/*.out`, `.ufo/waves/round-49/freeze/prereg-time-check.out`, `.ufo/waves/round-49/census/start.out`, `.ufo/waves/round-49/{preregistration.json,w1/dispatch.json,w1/out/swarm-registry.json}`, the four seat reports the entry cites, and `X2Lane/regraded-7.tsv`.

## 3. Entry claim → source

| entry statement | source |
|---|---|
| `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, pids 254977/255370/255954, ports 33749/45335/36679, nonces, `provenance-member-sparse` in 0.1 s, `member-is-server-control` executed, `2 rows new … ['\| S494 \|']` | `measured/c1-build.out` verbatim |
| witness mechanism (`--witness-dir`, `ready.json` schema, hold to `release`, 120 s, `witness` keys) | `tools/kama-live-replay.py:42-45`, `:277-278`, `:450-454`; `tools/kama-llamacpp-live.py:52-57`, `:282-303`, `:1269-1274`, `:1865-1869` |
| archive/member bounds and tokens | `tools/kama-llamacpp-live.py:208-209`, `:212-278` (`ARCHIVE_MAX_BYTES = 1 << 30`, `MEMBER_MAX_COUNT = 4096`) |
| `fixture=1 lane=1 scenarios=8/8 met=True`; per-scenario exits; `17 <= 23`, `65 <= 65` | `measured/c2-build.out` verbatim |
| lane events, `ungraded_lines=82`, `regressed=0`, `bad_declarations=0`, exit 0 | `measured/aoa-build.out` verbatim |
| `AOA_SELFTEST pass=30 fail=0` with `launder-through-head`, `binding-v4` | `measured/aoa-selftest-build.out` |
| 72 → 65 / 2349 → 2356 | `base.c2` (v3 at `438127bc`, `ungraded 72`) and `aoa-build.out` (v4 at build, 65/2356); file identity by command 5 |
| the seven lines and their origins / held status | `X2Lane/regraded-7.tsv` + my `seven-lines.json` (command 8) |
| "not a lane loss … mirror-table rows … over-reports head rewrites" | `.ufo/waves/round-49/w1/out/K2Origin.md:3`, `:42-49` (F6), `:60` (proposed mirror rule) |
| controls at `met=False` | `controls/base.c1.out`, `base.c2.out`, `junk-c1-fake-witness.c1.out`, `junk-c2-no-exempt.c2.out`, `junk-c2-word-token.c2.out`; `controls/build_controls.py` |
| freeze timestamp check pass | `freeze/prereg-time-check.out` (`RESULT pass`, `exit=0`) |
| census 93 `W04` / 1 `W01` / 0 `E` | `census/start.out` (command 9) |
| wave 71 seats and the split | `w1/dispatch.json`, `w1/out/swarm-registry.json` (command 10) |
| integration reds: registry, 34 vs 35, hexrun, r48c1 | `gate-build.out`, `r41/r42/r43-build.out`, `hexrun-build.out`, `r48c1-build.out` |

## 4. Findings

- **F1 — the receipts the entry cites are untracked at the build (integration ordering).** `.ufo/waves/round-49/measured/` is in the working tree only: `git ls-tree -r --name-only 74558c71 | grep -c 'round-49/measured'` → `0`, `git status --porcelain` → `?? .ufo/waves/round-49/measured/`. If `LOG.md` lands before the receipts, every "Measured at the build (…/c1-build.out)" citation dangles (round-48 closure R2 is the same class of defect).
  Fix: land `.ufo/waves/round-49/measured/` in the same commit as `LOG.md`, or earlier.
- **F2 — the head calibration cell is stale after the round-48 closure, and three regression counters are red at the build.** `SCORECARD.md:18` states `34` (`run python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `34`), while `ls corpus/lessons/*verifier-spotcheck.md | wc -l` in the build clone prints `35` — the round-48 outside closure added `round-48-verifier-spotcheck.md` after round 48 was measured. Receipts: `measured/r41-build.out` `… mismatches=1 met=False`, `r42-build.out` `met=False`, `r43-build.out` `spot: calibration row states 34, tree holds 35` (exit 1). State at 20:37: the working tree already carries an `SCORECARD.md` edit (`M`, +66/−7) that sets the cell to `35` and names `round-48-verifier-spotcheck.md` as the latest closure — the integration is closing this in flight; I did not run the three counters on it.
  Fix: at the measured commit set the cell's figure to the count then in the tree (the row itself is scoped "at the measured commit"), then re-run `tools/round41-scorecard-reconcile.py`, `tools/round42-selfdesc-reconcile.py`, `tools/round43-registry-audit.py`; all three must be green in `measured/*-final.out`. Not part of either claim — it is the new base's head row.
- **F3 — a sibling's `## Round 49` entry is already in the working tree, and it has no integration line.** `LOG.md:2331-2336` (uncommitted, `M LOG.md`) carries C1/C2/freeze/routed bullets and `- Lesson:` but no `**Round-49 integration:**` line, no counter sha256, no build numbers, no limits. Rounds 47 and 48 both carry an integration line.
  Fix: do not land both entries. Either (a) paste mine (it carries the integration line as a placeholder), or (b) keep the sibling's and append `**Round-49 integration:** …` plus the measured values at integration. Two `## Round 49` headings in one append-only file would also leave the round's record split across two sections with the same title.
- **F4 — an uncommitted widening of the negation rule makes one sentence of the entry stale if it lands.** `git diff tools/append-only-audit.py` shows `NEG_WINDOW` (`tools/append-only-audit.py:220` in the working tree) now accepting `cannot`, `can't`, curly apostrophes and en/em dashes, plus three new rows in `t_binding_v4` (`:929+`), attributed to seat K2Negation F1.
  Fix: if integration lands it, extend the entry's negation list ("not, never, no, nor, neither, non, isn't, aren't, no longer" → add "cannot/can't and curly-apostrophe or dash variants") and keep `AOA_SELFTEST pass=30` (the widening adds fixture rows to one existing case, not new case names — verify with `python3 tools/append-only-audit.py --selftest`).
- **F5 — C2's lane leg is not an independent oracle; the measured section must say so.** Seat V2Ctr (`.ufo/waves/round-49/w1/out/V2Ctr.md` §1–3) shows the counter's binder is a byte-equivalent copy of the tool's (`0/29` probe divergences), the lane-leg bound omits the v3 eligibility predicate and `only=`-region files, and the per-event check is skipped when `ungraded=0`; a patched tool that drops eligibility still prints `met=True` (`V2Ctr/receipt-eligibility-blind-tool-98f4cc5.txt`). My entry does not claim independence (it quotes the preregistration's bound wording), but SCORECARD §Round-49 "What met=True does not show" must carry this row.
- **F6 — the round-48 C1 counter diverges by construction at any v4 tip.** `measured/r48c1-build.out`: `graded tool=2356 counter=2349`, `ungraded_lines tool=82 counter=89`, exit 1. My entry states it in the build paragraph; the measured section should disclose it as round 48 did for the round-47 counter ("fails by construction").

## 5. Correction I made to my own draft (calibration record)

My first draft described the 7 re-graded `0718b6ab` lines as "the K1Regions laundering shape actually present on the lane". Seat K2Origin's F6 (`.ufo/waves/round-49/w1/out/K2Origin.md:42-49`) shows the opposite reading: they are head `## Capabilities` *mirror* rows whose text was legitimately born in the dated sections that first listed the capability, and the contract declares the head table re-derived in place (`registry/append-only-contract.tsv:3`) — so v4's byte-text-global origin over-reports the lane's own head rewrites. My git-only re-derivation supports the facts and not the laundering reading (parent section `Capabilities`, origin dated, all seven held at `82b5e9d3` and at the build). The delivered entry says "not a lane loss", names K2Origin F6, and adds the wave's definition-level limits (sibling-order dependence, fenced fake `## ` titles, CRLF byte-keying) to the limits sentence.

## 6. Out of scope / not done (deliberate)

- No counter, tool, selftest or server run: `round49-replay-witness-audit.py` and `round49-append-audit-v4-check.py` were not executed by me (≈20 s + ≈10 s, network); the entry's numbers are the build receipts, labelled as such.
- No network fetch; no llama-server started (`pgrep -f llama-server` not needed — none was launched from my scratch); no pacman/uv/npx/install.
- No lane, fleet, sibling-lane or shokuknow write; no git mutation in the lane (`--shared` clone, detached checkout inside my scratch only); no subagents; no `agent://all`.
- Not mine: SCORECARD/QUALITY/README/lesson text, `SKILL.md` registry, capability/PROVINCE rows — the integration line is a placeholder for those.

## 7. Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Log/log.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Log/seven-lines.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Log/check7.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Log.md`
