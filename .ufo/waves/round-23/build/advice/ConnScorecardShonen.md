# ConnScorecardShonen — where round 23's C1 and D4 record must land (append-only map)

Seat: CloseKama22.ConnScorecardShonen (connector, read-only). Lane base
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Observed facts below are from that
tree; I made no production edits, ran no build/test, made no installs. Only
file written: this one.

## Verdict

Three files, three different answers. **SCORECARD** gets one appended round
block (declaration + measured table + no-harm + sources + window/trend lines +
a `### D4 disposition` subsection + `Planned`). **corpus/README.md** gets one
appended frontier-disposition section. **SHONEN.md** gets **nothing**: the last
change to it is round 17 (`git log --oneline -- SHONEN.md` → `54a2926 …`), it has
no newline-terminated tail (`wc -l` 11, `awk NR` 12, last byte `.`), and rounds
18–22 recorded their SHONEN verdicts in the round report (`../.ufo/reports/round-22/kama.md:214-224`),
never in SHONEN.md.

Two contradictions must be stated, not smoothed:

1. `SKILL.md:732-738` still says the audit is "supported only on this trusted
   lane and fleet repository" and that "UTF-8/error/top-level handling … remain
   unclaimed". After this round two of those three (UTF-8, error) have a finite
   grid behind them. If SCORECARD claims the grid without an appended SKILL
   qualification, the two files contradict. SKILL is qualified by an **appended**
   correction block; its existing sentences are not rewritten.
2. The lane checkout is dirty: `git status --porcelain` shows
   ` M tools/report-landing-audit.py` (the candidate `GIT_ISOLATION` fix is
   uncommitted). Any before/after measured from this working tree is fiction.
   Measure a committed clean tree and cite its `commands.json` `measured_commit`
   (the round-22 precedent, `SCORECARD.md:1056-1068`).

## Direct answer — the exact append set

| # | File | Append after | Rows/lines to add (all new, nothing rewritten) |
|---|---|---|---|
| 1 | `SCORECARD.md` | line 1150 (EOF, newline present) | `## Round 23 — …` heading; declaration ¶; `### Round-23 measured results — clean tree <hash>` + 5-column table with the one C1 row; no-harm ¶; sources ¶; capabilities/window line; trends line; `### D4 disposition — … (D4)` ¶; `Planned:` ¶ |
| 2 | `corpus/README.md` | line 315 (EOF, newline present) | one `## Frontier disposition — round 23 — …` section: advanced (exactly 1), unchanged, remains-open, non-claim, lesson pointer. A 3-column coverage-map table row **only** if a *new* `corpus/knowledge/*.md` file is created |
| 3 | `SHONEN.md` | — | **none** (rationale in C below) |
| 4 | `corpus/QUALITY.md` | line 171 (EOF) | new `## Criterion added — round23 …` section + one `KQ34` row narrowing `KQ32`; `KQ32` at `:165` untouched. (Not in my file set; required so the SCORECARD D4 ¶ has a target.) |
| 5 | `SKILL.md` | after line 771 (or inside the round-23 correction block) | appended correction/qualification of `:732-738`; never an edit of those lines |
| 6 | `corpus/lessons/round-23.md` | new file | the pointer target both appends cite; no SCORECARD/README claim may point at a nonexistent lesson |
| 7 | `LOG.md` | line 1373 (EOF) | one `## round23 — …` section (lowercase `roundN`, the `:1332`/`:1355` form). Out of this ticket's three-file scope but required by `AXES.md` §Working the axes ("log evidence in LOG.md") |

## Anchor evidence observed at base

| Fact | Path:line | Observed |
|---|---|---|
| SCORECARD ends, last line is the D4 non-claim | `SCORECARD.md:1149-1150` | "registered-URL classification is not upstream-source validation or D4 / untrusted-repository hardening." |
| Head axes table is historical (score 7, last change round 1) | `SCORECARD.md:17-24`, calibration row `:23` | must not be rewritten; score stays 7 |
| Capabilities table / entry rule | `SCORECARD.md:124-128` | "none enter through this rollout" |
| Saturation line 8 / window N=4 | `SCORECARD.md:132` | untouched by a 7→7 round |
| Move log stops at round 9 | `SCORECARD.md:68-75` | rounds 10–22 did **not** append to it; do not start now |
| Round-22 declaration form to mirror | `SCORECARD.md:1037-1054` | declared axis + start master + before/after + counting command + "appended after the official clean-tree run" |
| Round-22 measured block to mirror | `SCORECARD.md:1070-1093` | 5 columns: Claim / Axis-score / Before → after / Counting commands / Evidence |
| D-item subsection precedent | `SCORECARD.md:1056` | `### Round-22 correction of round-21 measured-record lag (D1)` |
| Carried frontier list | `SCORECARD.md:1029-1032`, `:1106-1108` | crash-as-kill, receipt-header, system-library identity, K05/other-engine; "trusted-repo audit hardening … not acquired here" |
| Capability window precedent | `SCORECARD.md:1053-1054` | "No capability row added; window 2 of4 since round20" → round 23 is **3 of 4** |
| Prior discernment credit | `SCORECARD.md:1102-1104` | D2/D4 learning already credited in R22 |
| D4 debt text | `corpus/lessons/round-22.md:116-123` | five channels out of scope + "selftest fallback/GIT_DIR assertion debt, prelaunch races, chain bound, JSON duplicate-key/Unicode limits remain unclaimed" |
| Trust restriction | `SKILL.md:732-738`, `:771` | "supported only on this trusted … repository"; "D4 … remains frontier" |
| README frontier bullets | `corpus/README.md:66-79` | corpus gaps only; no audit/D4 bullet → nothing to correct there |
| README round-22 append form | `corpus/README.md:301-315` | deepening ¶ + "Frontier unchanged: …" + non-claim |
| README disposition heading precedent | `corpus/README.md:121` | `## Frontier disposition — round 11` |
| KQ32 row | `corpus/QUALITY.md:165` | "explicitly limited to the trusted … repositories until … demonstrated separately" |
| KQ append form | `corpus/QUALITY.md:167-171` | new `## Criterion added …` section, new numbered row |
| Report frontier count line | `../.ufo/reports/round-22/kama.md:198` | "Frontier rows advanced: **0**" → round 23 must say **1** and mean D4 only |
| Base defects claimed | `tools/report-landing-audit.py@4fe9339f:45`, `:87-97` | "Errors are never verdicts."; `text=True`; `git_env` docstring `:80-81` claims no redirection |

## A. SCORECARD.md — appended block skeleton

Replace every `<…>` with the clean-tree measurement. Do not write numbers that
were not produced by the cited command. Do not pre-write the verdict word
(`verified`) before the run.

```markdown
## Round 23 — repository-local git state cannot decide a report verdict

Declared C1 calibration **7 → 7**, the lowest assigned non-retired axis
(operability 8); no stagnation waiver. Round-start branch master:
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.

Before (base blob): `git_env`'s docstring says neither audited repos nor
fixtures "can be redirected" (`tools/report-landing-audit.py@4fe9339f:80-81`)
and the module says "Errors are never verdicts" (`:45`), yet `text=True`
(`:89-91`) plus no ref/fetch isolation lets repository-local
`i18n.logOutputEncoding`, non-UTF-8 committed bytes, `git replace`,
fabricated `refs/replace/<40-hex>` and a promisor remote's configured command
change, crash or execute during the audit. After criterion: git output is
decoded as strict UTF-8 (undecodable output is an EvalError, never a
traceback verdict) and every git call carries
`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false`; every fault the frozen arm crashed, flipped or executed
becomes typed refusal (exit 2) or the correct verdict, with controls
unchanged. Counting command: `<grid command> --arm both --json`. The measured
revision/counts are appended after the official clean-tree run.

This works the existing calibration gap, not a new capability: the audit is
still supported only on the trusted fleet/lane repositories and this is not
untrusted-repository hardening. Channels outside the grid are named below.
Sources <S0NN–S0MM or "none added">; motivating lesson
`corpus/lessons/round-23.md`. Other axis scores held. No capability row added;
window 3 of 4 since round 20.

### Round-23 measured results — clean tree <hash>

`python3 .ufo/waves/round-23/run.py --recipe <recipe> --out
.ufo/waves/round-23/runs/<hash>` measured committed `<full 40-hex>`: **<N>/<N>
declared exits**, zero timeouts/mismatches, harness exit 0 (`commands.json`).

| Claim | Axis/score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 repository-local git state cannot decide the report verdict | calibration 7 → 7; <verdict> | faults <F>; crash/flip/execute <K>/<F> → typed refusal or correct verdict <F>/<F>; controls <C>/<C> in both arms; selftest <cases> cases/<failed> failed; historic rounds 10–22: <D> raw defects, all <D> corrected by the unchanged ledger, uncorrected 0 | `<grid command> --arm both --json` (frozen <exit>, current <exit>) | `runs/<hash>/c1-*.stdout`; base script SHA<…>, fixed SHA<…>, grid SHA<…> |

No-harm: <each command> met its declared exit — <list, e.g. error census,
install-io/install-links grids, citation provenance, SOURCES guard, snapshot
selftest, census validate>. No live model server launched or registered
consumer sampled.

Sources command `<absolute census argv>`: rows <a>→<b>, missing 0; validate
exit 0. <S0NN–S0MM ground C1 / no rows added.>

### D4 disposition — local git state narrowed to a finite grid (D4)

`corpus/lessons/round-22.md:116-123` left D4 as report-audit Git-config/
history trust and UTF-8/error-handling debt. This round covers exactly the
channels in the grid — <a> log-output re-encoding, <b> non-UTF-8 committed
bytes, <c> `git replace` of an omitted commit, <d> fabricated
`refs/replace/<40-hex>`, <e> promisor lazy fetch with a repo-configured
command — which now refuse or resolve correctly. The guard is git-global, not
per-call-site. KQ32 (`corpus/QUALITY.md:165`) is narrowed by an appended
criterion row (KQ34), not rewritten. Still open and unclaimed: alternates and
`clone --shared`, the selftest fallback/GIT_DIR assertion debt, prelaunch
races, chain bound and JSON duplicate-key/Unicode limits
(`lessons/round-22.md:121-123`). `--no-lazy-fetch` on a git that predates
the option is an EvalError (refusal, not a silent fallback); only git 2.56.0
is measured, so the version floor is unmeasured. This is not
untrusted-repository hardening.

Trends: expansion **unchanged** (no new entry/capability); quality
**<improved-bounded | unchanged>** on the measured instrument behavior;
discernment **unchanged** — implementing prior outside D4 feedback is not a
new non-author verdict, and round 22 already credited its learning
(`SCORECARD.md:1102-1104`).

Planned: keep <crash-as-kill leaves, receipt-header minimization,
system-library (outside-directory) identity, K05/other-engine serving,
unreadable-member fail-closed rule, external-library/loader identity> explicit;
next round should be a capability/frontier move (window 3 of 4). Await outside
R23 admit/reject sampling. No next round is started.
```

Notes on the skeleton:

- If the L1 declares calibration 7→8 instead, the head table at `:23` is still
  historical and stays untouched, but the round block must then also append a
  line explaining the saturation line 8 (`:132`) rather than editing it. 7→7 is
  the precedent-consistent choice (R21/R22 both held 7).
- "Frontier advanced" for the D4 item counts as **one**; it is not a new
  knowledge row, so README and report must not count it as expansion.
- The three files must agree on one phrase for the boundary: *supported on the
  trusted fleet/lane repos; the grid is not untrusted-repository safety*.

## B. corpus/README.md — appended section skeleton

Choose by artifact, not by taste:

- **B1 (expected):** no new knowledge file, only `lessons/round-23.md` (and
  optionally a `§Round-23` deepening inside `knowledge/error-is-not-a-verdict.md`
  or `knowledge/llamacpp-loading-lifecycle.md`). Use the disposition heading;
  add **no** coverage-map table row (round-22 precedent, `:301-315`).
- **B2:** a *new* `corpus/knowledge/<file>.md` is created → additionally append
  `## Coverage map — round 23 addition` with the 3-column header
  `| Entry | Covers | Round |` and one row.

```markdown
## Frontier disposition — round 23 — repository-local git state (D4, narrow)

`tools/report-landing-audit.py` now decodes git output as strict UTF-8
(undecodable output is could-not-evaluate, exit 2) and runs git with
`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false`. The fixed fault grid in `corpus/lessons/round-23.md`
turns the channels that previously crashed, flipped or executed a verdict into
typed refusal or the correct verdict; controls are unchanged. KQ32
(`QUALITY.md:165`) is narrowed by appended KQ34; its row is not rewritten.

Frontier advanced: one — report-audit local Git state (D4), narrowly.
Unchanged: every bullet under `## Frontier` above (lines 66-79) and the
model-serving frontier (external-system-library identity, receipt-header
minimization, historical crash-as-kill leaves, K05/other-engine serving, real
registered-consumer reconciliation). Remains open and unclaimed inside D4:
alternates and `clone --shared`, the selftest fallback/GIT_DIR assertion debt,
prelaunch races, chain bound and JSON duplicate-key/Unicode limits, and the
`--no-lazy-fetch` git-version floor. Not claimed: untrusted-repository safety,
command-execution safety beyond the named channels, or a new
knowledge/capability surface. No new endpoint sample or service restoration is
asserted.
```

If B1 also deepens an existing knowledge entry, add one sentence naming it
(exact `knowledge/<file>.md` §Round-23), as `:303-304` does for round 22.

## C. SHONEN.md — append nothing (with the reason that survives audit)

- Last change `54a2926` (round-17); `git log --oneline 54a2926..HEAD -- SHONEN.md`
  is empty. Rounds 18–22 all left it alone.
- None of the four items moves. C1 repairs an instrument, so it is not a new
  decision table (`:5-6`), not an end-to-end domain task (`:7-8`), not a new
  oral-context proof (`:9-10`), and does not touch the province (`:11-12`).
- Promotion marks require a named non-author verifier; there is none for R23.
  Writing `[x]` or a new `→ Author assertion:` line would be a discernment
  overclaim.
- No province edit is needed either: `grep -ni 'audit|security|untrusted|hardening'
  PROVINCE.md` returns nothing, so the round's narrow instrument repair does not
  touch a stated write boundary.
- If L1 wants the round visible from SHONEN, the legal place is the report's
  `## SHONEN` section (`../.ufo/reports/round-22/kama.md:214-224` form), keeping
  every item `[~]`. Do not append to `SHONEN.md` unless instructed explicitly —
  and if so, add the missing trailing newline first (last byte is `.`).

## D. Never-touch list (append-only discipline)

- `SCORECARD.md:6-13` authority ¶, `:17-24` axes table, `:45-55` Planned,
  `:68-75` Move log, `:124-132` capabilities/saturation, and every round
  section from `:190` to `:1150` — including `:1106-1109` ("trusted-repo audit
  hardening … not acquired here") and `:1149-1150` (the R22 D4 non-claim).
  Round 23 supersedes by appending, never by editing.
- `corpus/README.md:66-79` frontier bullets.
- `corpus/QUALITY.md:165` KQ32 cell.
- `SKILL.md:732-738` and `:771` sentences.
- `tools/report-landing-audit.py` — the working tree copy is someone else's
  uncommitted change; measure from a clean clone/commit.

## Risks

1. **Measuring from the dirty worktree** → before/after invented; KQ28 requires
   the reported commit to resolve and the clean-tree receipt to name it.
2. **Overclaim creep**: "untrusted", "safe", "security guarantee", "hardened
   for arbitrary repos" in any appended sentence. The grid covers five named
   channels; alternates/`clone --shared` and the rest of `lessons/round-22.md:121-123`
   stay open. Grep the appended text for those words before commit.
3. **Score inflation**: writing 8 in the round block while the head table says 7
   and saturation is 8; or writing "verified" before the run.
4. **Capability row**: any new row resets/evades the stagnation window and
   contradicts R17–R22 precedent; round 23 is hardening of an instrument.
5. **README coverage-map row without a new knowledge file** → an indexed entry
   that does not exist.
6. **Double-crediting discernment** for the same D4 feedback already credited at
   `SCORECARD.md:1102-1104`.
7. **`--no-lazy-fetch` version floor**: on a git without the option the audit
   refuses everything (EvalError). Fine as fail-closed, but if unstated it is an
   operability surprise. The round block must state git 2.56.0 measured and the
   floor unmeasured; if the L1 adds a fallback, that is a separate product
   decision and changes the boundary text.
8. **Report/README/SCORECARD frontier counts disagreeing** (0 vs 1 vs "two
   items"). Fix the number once: D4 advanced = 1 row, expansion = 0.

## Proposed checks for L1 (not run here)

```sh
git diff --numstat -- SCORECARD.md corpus/README.md SHONEN.md   # expect 0 deletions
git diff -U0 -- SCORECARD.md corpus/README.md | grep '^@@'      # expect +1151 and +316
git diff -- SHONEN.md                                           # expect empty
python3 tools/report-landing-audit.py --rounds 10-22 --no-errata --json   # on the committed tree
python3 tools/report-landing-audit.py --rounds 10-22 --json               # expect exit 0
grep -nEi 'untrusted|security guarantee|safe on|hardened for arbitrary' <appended ranges>
```

Source census, only if rows were added:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`
and `… validate`; paste argv and exit. [INFERENCE] If round 22's five required
commits are added to the 49/12-report baseline (`SCORECARD.md:1141-1143`), the
rounds 10–22 run should be 54 required over 13 reports with the same 9
corrected defects — an arithmetic expectation, not a result.

## Not verified

- Any fault-grid, selftest or ledger number: no round-23 grid exists yet in this
  tree and I ran none. `.ufo/waves/round-23/probe/` holds only L1's probe
  (`probe-4fe9339f.stdout/.exit`, script), not a grid.
- Whether round 23 creates a new knowledge entry (decides README B1 vs B2).
- Whether round 23 adds SOURCES rows (decides the sources ¶).
- The git version that introduced `--no-lazy-fetch`; only 2.56.0 appears in the
  assignment and probe.
- `corpus/lessons/round-23.md` does not exist yet (`ls corpus/lessons | tail` →
  round-20/21/22 only), so both appends currently point at a file the round must
  create.

Owned paths: this file only
(`.ufo/waves/round-23/build/advice/ConnScorecardShonen.md`). Installs: none.
