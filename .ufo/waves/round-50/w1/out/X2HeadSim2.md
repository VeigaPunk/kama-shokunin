# X2HeadSim2 — round-50 pre-integration check: append-only-audit v5 at a simulated integration

**Verdict: v5 stays exit 0 and the frozen C2 counter stays `met=True` on a faithful integration rehearsal at both the build (`97c864be`) and the lane tip (`3b79eadd`) — but neither sees the integration's own head edits at its default threshold: only the authority banner is graded (at `--threshold 1`, `deleted=4 graded=1 ungraded=3 status=restored`), and the counter still reports `met=True` on a mutant that drops the byte-exact banner append (`restored_max=0 status=unrestored` at `--threshold 1`). Independently, the calibration row is already stale at the build (`round42-selfdesc-reconcile` → `r41=1 … met=False`) and must be re-anchored to 36 at integration; the E11 used-by rows clear once `corpus/lessons/round-50.md` exists.**

Scratch clone only (`git clone --shared` of the lane); no lane file, counter, preregistration or control was touched. Rehearsal commits have fixture identity (`r50x2-fixture`) and live only in my scratch. No llama-server was started by this seat (the only `llama-server` processes on the host belong to `Rev1Base`'s scratch, not mine); no pacman, no installs.

## 1. What was rehearsed

Two bases, identical edits — base A the seat-specified build `97c864bead3ee4a2f629574e77263d33834ec98a` → commit `dacbdc2cec280de82dd7783e32823c77b67afff4`; base B the lane tip `3b79eaddf38246c637cc7ba1a94ab363422876b6` (three commits past the build) → commit `fa08ff60fe49d4318924ac773f1609ceb37a4026`. Full diff: `proposed-integration.diff`; lesson text: `round-50-lesson.md`.

| Edit | Rehearsed form | Line |
|---|---|---|
| authority banner | `**Current authority (round 50):**`, `Latest measured round: 50.`, `kept current in rounds 43, …, 49 and 50` | SCORECARD.md:6 |
| superseded banner | round-49 banner appended byte-exact under `### Superseded head banners`, one line of provenance above it | SCORECARD.md:2758 (provenance), :2760 (banner) |
| `## Planned` pointer | `` `### Planned (round 51)` `` | SCORECARD.md:53 |
| `## Axes` re-anchor | calibration row `→ 36`, latest closure `round-49-verifier-spotcheck.md`, `evidence re-anchored round 50` | SCORECARD.md:18 |
| capability mirror | `Mirror of the round-50 canonical capability list that §Round 50 carries` | SCORECARD.md:117 |
| `## Round 50` | authority, claim table, controls, disclosed limits, scores held, canonical list (11 rows), `### Planned (round 51)` + numbered items, `### Round-50 measured results` | SCORECARD.md:2876 onward (`### Planned (round 51)` at :2915) |
| lesson | claims + the three `used-by` gate rows (S496/S497/S498 quotes) | corpus/lessons/round-50.md:1 |

Byte check for the banner (the one graded line): `git show 97c864be:SCORECARD.md | sed -n 6p | sha256sum` = `afb94e914b91ef8aa8320ff628a1f624b7befdeb1bd1f769c4fec94a5a2640ce` (984 bytes) = the appended line at `git show <rehearsal>:SCORECARD.md | sed -n 2760p`.

## 2. Does v5 stay exit 0? Yes, at the default threshold — on both bases

`python3 tools/append-only-audit.py --repo . --to <commit>` (exit 0 on both):

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 graded=14 ungraded=17 restored_max=14 held_at_to=14 status=restored
event 0718b6abbda6 LOG.md deleted=2292 graded=2292 ungraded=0 restored_max=2292 held_at_to=2292 status=restored
event 0718b6abbda6 SCORECARD.md deleted=2421 graded=2349 ungraded=72 restored_max=2349 held_at_to=2349 status=restored
event 0718b6abbda6 corpus/QUALITY.md deleted=375 graded=375 ungraded=0 … status=restored
event 0718b6abbda6 corpus/README.md deleted=663 graded=663 ungraded=0 … status=restored
summary commits=328 files=95 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```

Base B is byte-identical except `commits=331`. The frozen C2 counter (`tools/round50-append-audit-v5-check.py --repo <clone> --tip <commit> --scratch <dir> --out …`) exits 0 on both: `fixture=1 lane=1 scenarios=12/12 met=True`, lane `tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`, `event dd9f5dc6c0e6 ungraded 17 <= v5 natively exempt 23`, `event 0718b6abbda6 ungraded 72 <= v5 natively exempt 72`.

Cause: the tool only opens an event at the default threshold of 20 deleted lines (`tools/append-only-audit.py:448`, `:1122`, skip at `:520`), and the lane leg runs it with no `--threshold` (`tools/round50-append-audit-v5-check.py:388-395`). The rehearsal commit deletes 4 SCORECARD.md lines, so it is not an event at all.

## 3. Which head edits would v5 grade? Only the banner, and only below the threshold

`python3 tools/append-only-audit.py --repo . --to <rehearsal> --threshold 1 --json` (exit 1) — the rehearsal's own event:

```
{'commit': 'dacbdc2c…', 'file': 'SCORECARD.md', 'deleted': 4, 'graded': 1, 'ungraded': 3,
 'restored_max': 1, 'restored_best': 'dacbdc2c…', 'held_at_to': 1, 'status': 'restored'}
```

`git diff 97c864be sim-r50 -- SCORECARD.md | grep '^-'` prints exactly four deleted lines, and the classification follows from their parent sections (`sections()` ignores nothing here — no fences were added):

| Deleted line | Parent `## ` section | v5 class | Why |
|---|---|---|---|
| SCORECARD.md:6 authority banner | none (before the first `## `) | **graded** | origin title is `None`, so no exempt title intersects; `restored` only because the old banner is appended byte-exact at :2760 |
| SCORECARD.md:18 calibration row | `## Axes` | ungraded | exempt title, eligible (`count(## Axes)` unchanged), origin born in `## Axes` |
| SCORECARD.md:53 `## Planned` pointer | `## Planned` | ungraded | same |
| SCORECARD.md:117 capability mirror | `## Capabilities` | ungraded | same |

The same run classifies the last two real integration commits the same way: `24e906f034bc SCORECARD.md deleted=8 graded=1 ungraded=7 status=restored` and `c4b2175d2ff9 deleted=8 graded=1 ungraded=7 status=restored`. So the lane's head protocol (banner preserved byte-exact, exempt head sections re-derived in place) has exactly **one load-bearing graded line — the banner — and only at `--threshold 1`**.

## 4. The frozen C2 counter does not grade the head protocol (mutant M1)

Mutant `e9096c9693f89e3b8c57301c87735eebdfc79e69` (parent `97c864be`): the same head edits **without** the byte-exact append (the round-48 defect shape — banner rewritten in place, superseded text lost).

| Run | Compliant rehearsal | Mutant M1 |
|---|---|---|
| `append-only-audit --to <c>` (default) | exit 0, events 5, `ungraded_lines=89`, `regressed=0` | exit 0, events 5, `ungraded_lines=89`, `regressed=0` — identical |
| `append-only-audit --to <c> --threshold 1` (rehearsal event) | `deleted=4 graded=1 ungraded=3 restored_max=1 status=restored` | `deleted=4 graded=1 ungraded=3 restored_max=0 held_at_to=0 status=unrestored` |
| frozen C2 counter | `fixture=1 lane=1 scenarios=12/12 met=True` (exit 0) | `fixture=1 lane=1 scenarios=12/12 met=True` (exit 0) |
| `round42-selfdesc-reconcile` | `mismatches=0 met=True` | `mismatches=0 met=True` |

**Finding (instrument gap, not a lane defect):** a round that breaks SCORECARD.md:6's own declared preservation protocol — the line that scopes the `exempt=` region — passes both the frozen counter and the head reconcile. The tool sees it (`--threshold 1`, `unrestored`, exit 1), the counter does not. Proposed fix for round 51 (counters are frozen; this is a proposal, not a patch): make the counter run the tool **twice** — once at the contract threshold and once at `--threshold 1 --files SCORECARD.md`, requiring (a) tool exit 0 at the contract threshold, and (b) every head-region deletion (lines before the first `## `, or a small explicit head set) `restored` at threshold 1 — or give the tool a `--head` mode that always grades the pre-first-heading region. Alternatively lower the event threshold for files whose contract row carries `exempt=`, since integration commits are structurally sub-20 (measured: 8, 8, 9, 4 lines across rounds 47-50).

## 5. E11 used-by clears once the lesson exists

- At the build `97c864be`: `bash scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md` → **exit 1**, exactly `E11 S496 / S497 / S498 missing used-by corpus/lessons/round-50.md` (plus the long-standing W04 set and one W01, unchanged).
- At both rehearsal commits: **exit 0**, `file ok`, zero `E…` codes (receipt `sim-census-validate.out`, `simtip-census.out`). S496 and S497 also list `corpus/knowledge/llamacpp-loading-lifecycle.md`, which already exists; the lesson file is what the census needs.
- The rows' `opened` is `2026-10-27` for all three and the census resolves `TODAY` as `date -u +%F` (`scripts/sources-census.sh:90`), so E08 does not fire on this host.

## 6. Head re-anchors the instruments demand at integration

- **The build is already stale.** `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 97c864be` → exit 1, `r41=1 … mismatches=1 maxN=49 met=False`, detail `r41 calibration run … verifier-spotcheck … no stdout line == '35' (exit 0)`: there are 36 `corpus/lessons/*verifier-spotcheck.md` blobs at the build, not the 35 the head cites. Re-anchoring to `36` + latest closure `corpus/lessons/round-49-verifier-spotcheck.md` + `re-anchored round 50` turns it into `r41=0 … mismatches=0 maxN=50 met=True` at both rehearsal bases (`sim-r42.out`, `simtip-r42.out`). **The L1 must land this, or the measured commit fails the round-42 regression.**
- **Any SKILL.md edit breaks the depth anchor.** The known integration item (two round-50 counters into SKILL.md's instrument registry) changes the depth row's `sha256` and line count. Mutant M2 `3878d813331460023269d636103d8450e4dd493a` (a two-line append to SKILL.md, no re-anchor): `r42` exit 1, `r41=2`, details `depth sha256 SKILL.md cited 0ad48efc… observed 9d8db5e0…` and `depth lines cited 1504 observed 1506`. Recipe: after the SKILL edit, re-anchor `SKILL.md` sha256, `(N lines)`, and `grep -c '^## ' SKILL.md` (37 only if the registry rows add no `## ` heading), and bump that row's `re-anchored round 50`.
- Everything else in the head-table reconciles at the build (`r41=1` is only the calibration row), including the `## Saturation` vector/first-working list, `## Retired` counts (6 axes / 11 capabilities), `## Capabilities` names vs the canonical list, the census-count claim and the `tools/`/`registry/` tokens against PROVINCE.md.

## 7. Other integration-relevant measurements

- **No slack on the `0718b6abbda6` bound.** The counter's lane detail is `event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72` — equality, not slack. Any future change that makes the tool ungrade one more line of that event than the counter's own v5 count permits flips `lane=0`. My rehearsal (which adds 90 lines, including a canonical capability list) leaves it at exactly 72.
- **`--threshold 1` is red by construction.** At the build it exits 1 with `events=102 restored=19 partial=4 unrestored=60 ungraded=19` and `ungraded_lines=201`; the 60 unrestored are the sub-20 dated-section deletions across LOG/SOURCES/corpus lessons/README (the debt §Planned already carries). So "v5 stays exit 0" is a statement about the contract threshold only.
- **The preregistration's after-build ablations are not in the tree.** `.ufo/waves/round-50/controls/` holds only `base.c1.out` and `base.c2.out` (both `met=False` at `26ecba64`); the `controls` cell of `.ufo/waves/round-50/preregistration.json` requires post-build ablations for both claims (C1: no env allow-list, no replay parent-death signal, no `model_mapping`, decoy `child_pid`; C2: v4 fence-blind sections, byte-exact origin keys, v4 first-in-rev-list origin). Until integration lands them, neither claim has ablation evidence — this is not in the known-items list.
- **Base of the measurement.** The lane tip is `3b79eadd` (wave spec, the S498 tick-parity build-fix `3d42897b`, build regression receipts), three commits past the build. The rehearsal is instrument-identical on both bases, so the L1 can measure on its integration commit at the tip; the frozen counters' sha256 at the build already match the preregistration (`ff6ac2ac…` / `925f07a4…`, re-derived).

## 8. Limits of this rehearsal

- Only the append-only instruments and the head reconcile were run; C1 (`tools/round50-replay-bind-audit.py`, ~46 s and ~228 MB of downloads) was not re-run — outside this seat's question and already dry-run by the L1 at the build.
- My `## Round 50` section abbreviates the canonical list's `what it can now do` cells and states that; the L1's integration should carry the full round-50 wording. Names, evidence pointers and first-working rounds are the head mirror's, and `round42` reconciles (`caps=0 province=0 saturation=0`).
- The rehearsal's own numbers (4 deleted / 1 graded / 3 ungraded) are about the rehearsal commit; the two archived integration commits measured 8/1/7. Nothing in the rehearsal's prose claims a measured value.

## 9. Artifacts (this directory)

`proposed-integration.diff` (SCORECARD.md + lesson, build→rehearsal), `round-50-lesson.md`, `commands.txt` (every command and exit), `sim-aoa-default.out`, `sim-r50-threshold1.json`, `sim-c2-counter.out`, `sim-census-validate.out`, `sim-r42.out`, `simtip-aoa-default.out`, `sim-tip-threshold1.json`, `simtip-c2.out`, `simtip-census.out`, `simtip-c2-stdout.out`, `mut-nobanner-aoa-default.out`, `mut-nobanner-threshold1.json`, `mut-nobanner-c2.out`, `mut-nobanner-r42.out`, `mut-skill-r42.out`, `r42-at-build.out`.
