# Round 71 — frozen claims, counters, kill rules (kama)

Frozen before any seat scores. Base revision: `f3ee44f47a9680437eeae63a8fa8807552a65119`
(branch `master`, equals the remote tip at freeze time). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Round shape: ONE v1 wave, 12 seats (band 8–16). L1 holds the planner seat; the bounded planning
data-walk rides the scout and connector items. Claims are causally separable: C1 is the report-gate
instrument, C2 the census waiver boundary, C3 the province host re-derivation; each counter runs alone.

A rule changed after a seat scores is not the claim's rule (kumitate r42). The predicate sentence below
is the same sentence in the plan, the counter's code comment and the receipt label.

## C1 — calibration: one registered pre-report gate derives the round's pre-report verdict and grades round-worktree cleanliness

- Axis: calibration (held 7; lowest assigned non-retired axis, so the floor is met).
- Type: capability acquisition (`pre-report-gate`), plus the calibration move.
- Predicate: `python3 tools/pre-report-gate.py --repo <lane> --round <N> --tip <rev>` prints one
  `PRE_REPORT round=<N> arms=5 failed=<f> uncommitted=<u>` line and exits 0 only when the four
  reconciled instruments (selfdesc reconciler, newest-closure counter, receipt-pointer audit,
  worktree-landing check) are all green AND no path under `.ufo/waves/round-<N>/` is uncommitted;
  it exits 1 naming every failed arm otherwise.
- Counter (same command before and after): `python3 tools/pre-report-gate.py --repo . --round 70 --tip master; echo EXIT=$?`
  - before: the file does not exist (exit 2, `No such file or directory`); the four instruments
    themselves are the round-start state: reconciler `mismatches=1 met=False` exit 1 and newest-closure
    `STALE_CALIBRATION` exit 1 (the round-70 closure landed after its report — scheduled staleness) while
    receipt audit and WLC exit 0; `git status --porcelain -uall -- .ufo/waves/round-70` carries 26 uncommitted files (14 status entries) inherited from round 70.
    Receipts: `.ufo/waves/round-71/measured/before/{reconciler,newest-closure,receipt-audit,wlc,git-status}.out`.
  - after: at the report tip `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0`, exit 0.
- Target: `failed=0 uncommitted=0` at the report tip with exit 0, and exit 1 on each defect fixture below.
- Kill rule (each fixture must exit 1 and name the arm): (i) an uncommitted file under the round's wave
  dir; (ii) a stale newest-closure pointer; (iii) a missing declared self-record path; (iv) a dirty
  (byte-changed) declared path.
- Do-nothing control: `controls/pre-report-shortcut.py` reproduces the lane's current practice — run the
  four instruments and OR their exits — on a fixture at `af6eb6c2` (the round-70 green tip) carrying the
  same 26 inherited round-70 files. It prints `SHORTCUT_CONTROL arms=4 failed=0 uncommitted=26`, exit 0: the
  shortcut meets the instrument exits and cannot see the uncommitted class, so the target is unreachable
  by doing nothing.
- Sourced grounding: `git-status` porcelain-format row opened this round (script-stable status records the
  cleanliness arm parses); `S052` (pytest exit codes) re-opened for the fail-closed-on-no-verdict rule.

## C2 — operability: the census waiver boundary is a registered gate that kills the five known shims

- Axis: operability (held 8).
- Predicate: `python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py` prints
  `BOUNDARY cases=7 killed=5 survivors=0` and exits 0; it exits 1 if any named shim survives, if a
  waiver covers an evaluated failing member (that fixture must exit nonzero), or if the landed census
  bytes are killed by mistake.
- Counter (same command before and after): `python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py; echo EXIT=$?`
  - before: tool absent; the frozen round-70 control run over the five shims prints
    `s4-refusal-as-fail … PASS (hole)`, `s5t-hardcoded-total … PASS (hole)`,
    `s6w-waiver-swallows-failure … PASS (hole)`, `s8r-second-call-silent … PASS (hole)`,
    `s10d-refusal-branch-deleted … PASS (hole)` — `killed=0`
    (`.ufo/waves/round-71/measured/before/shim-control-table.out`, produced by
    `.ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py`; shims retained at
    `/fast/scratch/hyaku/kama-r71/l1/shims` and re-embedded by the tool).
  - after: `BOUNDARY cases=7 killed=5 survivors=0`, exit 0.
- Target: all five named shims killed, landed census bytes accepted, fail-waiver fixture nonzero.
- Kill rule: the landed `tools/round65-host-census.py` bytes must stay green on the boundary cases
  (specificity), and the five shims must each be named with the check that kills them.
- Do-nothing control: the round-70 control on the same five shim files — 5 holes, exit 0 (receipt above).

## C3 — freshness: every province host-surface claim is re-derived on this host and stale ones carry a dated, verdict-checked correction

- Axis: freshness (held 8).
- Predicate: `python3 tools/round71-province-host-claims.py --repo . --base f3ee44f4` prints
  `PROVINCE_HOST_CLAIMS markers=11 tags=12 extra=4 contradicted=<c> uncovered=<u>` and exits 0 only when
  every contradicted claim carries a later `correction-on-host (DATE) \`province-host:TAG\`` line whose
  claimed present/absent verdict agrees with a live host probe; deleting or rewriting a base marker line
  exits 1 (`REWRITTEN`).
- Counter (same command before and after): `python3 tools/round71-province-host-claims.py --repo . --base f3ee44f4; echo EXIT=$?`
  - before: `contradicted=14 uncovered=14`, exit 1 (receipt `measured/before/province-markers.out`:
    11 marker lines, 12 tags, 0 corrections; host probes at freeze time).
  - after: `contradicted=14 uncovered=0`, exit 0.
- Target: `uncovered=0`, exit 0, with the four prose claims (Windows host, `python3` alias, NTFS path,
  `ss`/`flock` absence) carried as declared extra surfaces.
- Kill rule: (i) corrections carrying a flipped verdict leave `uncovered>0`; (ii) a correction naming the
  wrong tag clears nothing; (iii) deleting a base marker line exits 1.
- Do-nothing control: appending tag-matching correction lines without probing the host (the shortcut that
  skips the re-derivation) — the flipped-verdict fixture must leave `uncovered=14`; the tool's selftest
  runs exactly that arm. Append-only rule (KQ7) means the marker lines stay.

## Round populations and expected deltas

| Population | Before | Expected after | Command |
|---|---|---|---|
| gate-registry registered rows | 79 | 82 (three new tools registered in SKILL.md) | `python3 tools/gate-registry-check.py --repo . --mode worktree` |
| capability rows | 15 | 17 (`pre-report-gate`, `province-host-claims`) | canonical `## Capabilities` rows in SCORECARD.md |
| knowledge entries (pinned count) | 39 | 39 or 40 (one new entry only if admitted) | the pinned counting command in the coverage row |
| SOURCES registry rows | 281 | 282 (one new `git-status` row) | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` |
| uncommitted round-70 files (`-uall`) | 26 (14 status entries) | 0 (committed under the round-71 evidence commit) | `git status --porcelain -uall -- .ufo/waves/round-70` |

Scores are held (operability 8, calibration 7): all three moves are instrument repairs/acquisitions,
not new domain claims; no axis is harmed. No new serving-runtime or endpoint sample is taken.

## Wave plan (one v1 wave, 12 seats)

3 executors (C1/C2/C3 tools), 2 scribes (knowledge entry + lessons/corrections), 1 scout (host census),
1 connector (sibling overlap + inherited-defect inventory), 1 reviewer, 1 critic, 1 mutation-tester,
1 sentinel, 1 labrat (attack share 5/12 = 42%). Residual: none. Planner: L1.

## Freeze annex — post-wave corrections (appended 2026-11-03; no predicate changed)

Three factual slips in this freeze were found by the wave seats and are corrected here as an annex, not
by editing the text above (the predicates, counters and kill rules are unchanged):

1. **C1's `--round` label.** The counter line says `--round 70` while the target line says
   `PRE_REPORT round=71`. The counter is the same command with the report's round: the before/control
   receipts use `--round 70` (the inherited wave dir, 26 files) and the after receipt uses `--round 71`
   (`failed=0 uncommitted=0`). Both receipts are committed; the report names which N each used.
2. **The population command.** `gate-registry-check.py` takes `--repo`/`--rev`/`--selftest` (omitting
   `--rev` already means the worktree); `--mode worktree` exits 2.
3. **The population delta.** The gate's declared regex is
   `^(?:\.ufo/waves/round-[^/]+/count-[^/]+|tools/round[0-9]+-[A-Za-z0-9._-]+)\.py$`, so only
   `tools/round71-province-host-claims.py` enters it: measured `79 → 80`, not 82. The other two tools
   are documented SKILL rows outside that population (lesson Mistake 1).
