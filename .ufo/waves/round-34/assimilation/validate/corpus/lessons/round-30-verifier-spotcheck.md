# kama — round-30 verifier spot-check (closure)

author: hyaku closure (non-author integrator, @m_flash)
date: 2026-10-23
lane tip verified: `043ba425b20ff846bdec17e35273feb2c7df6065` (local == origin/master, ahead=0)
before: `52ac3af8614b5040ba5e17f17a2c7af029706e6c` · claim base: `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` · report: `.ufo/reports/round-30/kama.md` @ `2cec458fd510909ecb1ea276a34737520138d5a9` (author kama-shokunin)
dispatch digest (watchdog.log, verbatim as handed to closure): launch kama round=29 attempt=2 2026-10-23T15:10:23-03:00 pgid=93338; complete round=29 attempt=2 16:12:49-03:00; launch kama round=30 2026-10-23T16:38:08-03:00 pgid=2382901 driver=hyaku-inline attempt=1; complete kama round=30 "2026-10-24T~00:25Z" (in-session L1): landed, lane HEAD 043ba425, fleet report commit 2cec458f.

## 1. Step-1 conformance

| Check | Command | Result |
|---|---|---|
| report authorship | `git log --format='%an %H' -- .ufo/reports/round-30/kama.md` (fleet) | `kama-shokunin 2cec458fd510909ecb1ea276a34737520138d5a9` — lane identity; real report (130 lines, six sections), not a marker |
| SHONEN heading | read report §SHONEN | present; 4 bullets, one per box, all `[~]` with pointers; no `[x]` |
| branch ref | `jj-lane.sh state …/kama-shokunin` | `branch=master local=043ba425… remote=043ba425… ahead=0 behind=0 tracked=0 untracked=0` |
| leftovers | `git -C … status --porcelain` | empty |
| cited commits | every 7–40 hex token in the report: `git cat-file -t` + `git merge-base --is-ancestor <h> refs/heads/master` | 15 commit tokens (`026eede9`, `14bb1a32`, `1d3e8ba4`, `227dd1ee`, `2aa46e24`, `40b122d`, `4d498001`, `52ac3af`, `6de225c2`, `92b14625`, `d0e8c4c4`, `ea72c3ea`, `fdf8cda1`, full `026eede9…`) all exist and are ancestors; the 5 non-commit tokens are digests/sid hashes (`24ce96bc3905`, `db4c39bbbdfd`, `c3f16ef1`, `4a6f7c911e`, `422b431349`) |
| round commits identity | `git log --format='%h %an %cd' 52ac3af8..043ba425` | 8 commits, all `kama-shokunin`; `fdf8cda` author-date 16:23:23 is the jj change-creation time, committer 16:53:58 postdates the 16:38:08 launch line |
| prompt embed | `diff <(sed -n 1,140p templates/round-prompt.md) <(sed -n 1,140p .ufo/prompts/kama-round-30.md)` | only `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}/{{AXES}}` substitutions differ; §1–§5 verbatim, hyaku addendum §6 appended; no L2 route map quoted (nothing to compare with MISSION.md) |
| L2 floor | `controls/SUMMARY.md`; `w1/out/swarm-registry.json` `members` | 14-seat control call (all returned) + 64 registered v2 wave members; no wave seat output committed or cited (disclosed) |

Conformance defects (status-neutral): (a) the report's Landed-changes table omits two landed round commits, `f41dce3` (late control evidence + wave registry, 17:13:51, before the report commit 17:14:04) and `043ba425` (lesson note, 17:16:02, after the report commit); (b) the completion digest's `2026-10-24T~00:25Z` is future-dated against the lane tip (17:16:02-03:00 = 20:16Z) and this closure's clock (2026-10-23T20:22Z); (c) the fleet prompt-evidence commit `90ff051` ("kama dispatch evidence") carries the lane identity, while PROTOCOL assigns committing `.ufo/prompts/*.md` to the integrator.

## 2. Claim re-derivation

**C1 (calibration, measured) — verified, re-measured.** Scratch clone of `https://github.com/VeigaPunk/kama-shokunin.git` (HEAD `043ba425`), counter copied from the lane, `sha256sum` = `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` (matches `preregistration.json` and `git show 043ba425:.ufo/waves/round-30/count-c1.py | sha256sum`). `git log fdf8cda1..043ba425 -- count-c1.py preregistration.json` is empty (no post-freeze edit). Command `/usr/bin/python3 count-c1.py --repo <clone> --tip <rev> --out <json>`, exit 0 each:

| tip | observed line |
|---|---|
| `2aa46e24` (base) | `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 0 false_corrections 0 unresolved 13 met False` |
| `52ac3af8` (lane HEAD before) | `… mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False` |
| `026eede9` (measured) | `… mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True` |
| `043ba425` (lane HEAD after) | identical to `026eede9`; `false_corrections []`, `unresolved_ids []`, `oracle_unbound_items []` |

All four match the committed receipts (`c1/before/c1-base.out`, `c1/before/c1-r29-tip.json`, `final/c1-tip.out`). Independent check of the two SA30 rows' cause: `git grep -F -q -e 'file=yes' ea72c3ea -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus/**'` exit 1; same for `declared2048 = captured training2048` at `92b14625` exit 1 — neither span is retained outside the self-report files at W, so `q:no-artifact` stands. Ordering: `14bb1a32` (controls) is an ancestor of `4d498001` (data). Docstring drift: the frozen counter's docstring names only the `## Round 29` heading and `SA29:` prefix; the code (`HEADINGS`, line 84–85; prefixes line 486) also accepts Round 30 / `SA30:`.

**C2 (operability, capability `instrument-agreement`) — verified from committed evidence (Gate standard: a sibling's tool not executed).** Before: `git cat-file -e 2aa46e24:tools/instrument-agreement.py` and `…52ac3af8:…` exit 128. After: `043ba425` has the tool, introduced by `1d3e8ba`. `c2/selftest.out` reads four `[PASS]` arms (deterministic `agree=3 disagree=0`; nondeterministic `agree=2 disagree=1`; declared-volatile `agree=3 disagree=0`; exit-disagreement `agree=2 disagree=1`) and `IA_SELFTEST pass=4 fail=0`; `selftest()` returns 0 iff no arm fails. `receipt-a.json` (`error-verdict-census.py --json`) and `receipt-b.json` (`sources-append-only.py --from 2aa46e24… --to 52ac3af8… --json`) each `runs 3 agree 3 disagree 0`, three identical digests (`24ce96bc…`, `db4c39bb…`); `receipt-b-corpusguard-refused.json` `agree 1 disagree 2`, three distinct digests. `main()` returns 1 on any disagreement. SCORECARD §capabilities row present (first-working round 30). Limits recorded as defects: exit codes are not persisted in `selftest.out` or the receipts; the preregistered "nondeterministic arm … exits 1" is shown by code reading, not by a committed CLI exit; receipts name `cwd` (the live lane tree), not the measured revision; the docstring/capability row says runs happen "in isolated temp dirs" but every run shares `cwd`, only `TMPDIR` is fresh; no `SKILL.md` §Local gate/probe registry row exists for the tool.

## 3. Per-axis verdicts

`git diff 52ac3af8 043ba425 -- SCORECARD.md` has 0 removed lines; `git show 043ba425:SCORECARD.md` begins with the `52ac3af8` and `2aa46e24` bytes (append-only True). Round diff touches only `LOG.md`, `PROVINCE.md`, `SCORECARD.md`, `corpus/{QUALITY,README,SOURCES}.md`, `corpus/knowledge/instrument-run-agreement.md`, `corpus/lessons/round-30.md`, `tools/instrument-agreement.py` (+511/−0) plus `.ufo/waves/round-30/`.

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | improved | frozen counter: unresolved 13 → 0 over the declared 141-statement population (rows-only arm 2 → 0); score held 7 by the author |
| operability | improved | capability absent → selftest pass=4 fail=0 + two agree=3 receipts + a refused subject |
| depth | unchanged | no depth claim; append-only diff |
| coverage | unchanged | README coverage row added; no coverage claim |
| freshness | unchanged | no freshness claim; no existing SOURCES row status/recheck changed |
| adjacency | unchanged | S178/S179 cross-lane reads; no adjacency claim |

## 4. Discernment spot-check (LEARNING.md §Discernment is checked from outside)

`corpus/lessons/round-30.md` `## Gate` records two admits (S178, S179) and no reject; the round's reject decisions sit under `## Seat findings`/C2. Sampled: both admits, plus the C2 subject refusal and the CtlEditInPlace rejection.

| Decision | Kind | Re-opened | Verdict | Reason |
|---|---|---|---|---|
| S178 admit (tier A, mined) | admit | `git -C kumitate-shokunin show 4e4f471:.ufo/waves/round-48/r48/ReviewQualityDraft.md` lines 123–125; `ce9aee5` is a commit with `scripts/counter-rerun.mjs` (header: "runs one counter K times … reports whether the counter's own final summary line is stable") | agree | quote located at :123–124, 11 words (≤25); verbatim except the source's backticks around `scripts/counter-rerun.mjs` are dropped and a line break is joined; scope (rerun-and-compare, separate from parse completeness) matches the file |
| S179 admit (tier A, mined) | admit | `git -C mori-shokunin show 6827d6e:corpus/knowledge/source-drift-r36.md` line 21; `e57c58b:tools/mori-source-drift.py` docstring | agree | quote verbatim at :21, 16 words; the `fresh` = byte-identity-only boundary is what the knowledge entry transfers |
| corpus guard refused as agreement subject | reject | `c2/receipt-b-corpusguard-refused.json`; `tests/ollama-corpus-guard/check.py:631` (`tempfile.TemporaryDirectory(prefix="kama-corpus-guard-")`) and `result_document` (`runner`, `runner_sha256`) | agree | three distinct digests on one tree; the random temp suffix survives the tool's `<TMP>` normalization and the runner path/digest is embedded — refusing rather than normalizing after the fact is correct |
| CtlEditInPlace rejected (control arm) | reject | `controls/SUMMARY.md` appended correction 4; `controls/CtlEditInPlace/counter.out` | agree | `append_only False … unresolved 141 met False`; the lesson's appended note correctly names append-only, not base-anchoring, as the load-bearing rule |

Defect: `## Gate` holds no reject row this round; record source/decision rejections there.

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0, `kama ok …/corpus/SOURCES.md`, with 83 `W04 duplicate url … across scopes` warnings on pre-existing rows S031–S173 (none on S178/S179).

## 5. Trend verdicts

- **expansion: improved** — net-new `corpus/knowledge/instrument-run-agreement.md` (header `source:` S178/S179, `verified-at:`, `recheck:` present), two mined SOURCES rows, one capability row.
- **quality: improved** — KQ40 appended to `QUALITY.md`; S174/S176 decision-record corrections appended; C1 instrument defects caught by their own refusals (`c1/preliminary/duplicate-ids.json` `error duplicate statement ids`; `c1/preliminary/bound68.json` `oracle_bound 68 oracle_unbound 4`). Bounded: the oracle-revision-pin mistake has no committed failing receipt (`grep -r 'missing at tip' .ufo/waves/round-30` finds nothing) and the lesson cites `long-digest-fix.json` for `bound 68 unbound 4` although that file reads `bound 72 unbound 0` (the bound-68 run is `bound68.json`).
- **discernment: unchanged** — the outside sample agrees on all four decisions, and the control call sharpened which conjunct is load-bearing, but the gate made only two admits and recorded no reject; agreement on a small sample does not show better selection than round 29.

## 6. Routed defects for the lane (next round)

1. Report Landed-changes table omits `f41dce3` and `043ba425`; list every landed round commit.
2. Completion digest `2026-10-24T~00:25Z` is future-dated; the lane tip is 2026-10-23T20:16Z.
3. `instrument-agreement`: no `SKILL.md` §Local gate/probe registry row (name, gate|probe, verdict map 0/1/2, `--selftest`, pinned values, write scope); closure grades it non-conformant until the row exists.
4. `instrument-agreement` receipts name `cwd`, not the measured revision, and persist no exit code (selftest included); the "isolated temp dirs" wording in the docstring and SCORECARD capability row overstates the isolation (shared `cwd`, fresh `TMPDIR` only). Correct by appended record.
5. Lesson `## Mistakes` row 1 (oracle revision pin) cites a failing run with no committed receipt; row 3 cites `long-digest-fix.json` for the bound-68 reading that lives in `bound68.json`. Append a correction.
6. `## Gate` carries admits only; record reject decisions (sources or subjects refused) there.
7. Frozen `count-c1.py` docstring names only `## Round 29`/`SA29:` while the code accepts Round 30/`SA30:`; note it in the next counter's docstring rather than editing frozen bytes.
8. Fleet: prompt-evidence commit `90ff051` carries the lane identity; committing `.ufo/prompts/*.md` is integrator scope (operator note, not lane debt).

SHONEN: not fully checkable by a non-author this round — boxes 1 and 4 can be checked by reading `SKILL.md`/`PROVINCE.md`, but boxes 2–3 need a real-surface end-to-end task and an independent execution, which this round's lane-owned instruments do not provide. No `[x]` written.
