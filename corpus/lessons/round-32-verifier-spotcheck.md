# kama — round 32 verifier spot-check (closure, non-author)

author: hyaku closure (non-author integrator, @m_kfc)
date: 2026-10-24
lane tip verified: kama-shokunin@907cdcc0a76f8656fde4574c0a50725fcea42fa9 (master; lane HEAD before round: 18464d0866afd5c4b471c8478d72b079d82d1fa8)
report: .ufo/reports/round-32/kama.md (fleet commit 1d9840bb5c30bdc7012ef20399956c1769a2a964, author kama-shokunin <kama@shokunin.local>)
dispatch digest (watchdog.log, mutable — copied per protocol): `2026-10-24T02:48:12-03:00 launch kama round=32 pgid=589693 driver=hyaku-inline attempt=1`; `2026-10-24T03:23:02-03:00 complete kama round=32; hyaku-inline attempt=1`

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report landed by lane identity | `git log --format='%an %ae %H' -- .ufo/reports/round-32/kama.md` | `kama-shokunin kama@shokunin.local 1d9840bb… round-32: kama report` | pass |
| SHONEN heading, one line per box | read of report `## SHONEN` | 4 boxes, all `[~]` with evidence pointers (author-asserted; no non-author `[x]`, correct for a lane report) | pass |
| Cited commits exist + ancestor of branch `master` | `git merge-base --is-ancestor <hash> master` for 9afaf0e9, c4c46ad5, dc4258bd, 967d8852, 3f1a7330, 907cdcc0, base 18464d08 | all OK; `aca07f21…`/`7850a92c…` are synthetic control fixture trees named in committed control receipts, not lane commits | pass |
| Lane repo clean + pushed | `scripts/hyaku/jj-lane.sh state` + `git status --porcelain` | `ahead=0 behind=0`, `tracked=0 untracked=0`, empty porcelain; HEAD detached at master (jj-colocated, expected) | pass |
| Prompt carries template contract | read of `.ufo/prompts/kama-round-32.md` | sections 1–5 (mission/axes, claims, frontier, L2 floor, full report contract, commit/push scope, L0) + §6 hyaku addendum; report path, lands-last, SHONEN heading, hash-citation, write scope all embedded | pass |
| Marker predicate | report content | real work, evidence pointers, checkable commit hashes — not a marker | pass |

## Per-claim re-check

### C1 — calibration 7 → 7 (round-qualified correction counter)

Re-measured by this verifier (not evidence-only):

- Counter freeze pin: `sha256sum .ufo/waves/round-32/count-c2r.py` → `ef298b63…c92e`, matches `count-c2r.sha256` and the report; counter introduced at 9afaf0e9.
- Before: fresh clone at base 18464d08, ran `/usr/bin/python3 .ufo/waves/round-32/count-c2r.py --repo <clone> --tip 18464d0866af… --out /tmp/c1-before.json` → `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False` — matches report and is byte-identical to committed `.ufo/waves/round-32/c1/before-base.json` (diff empty apart from nothing).
- After: same command at data tip 967d88528c1d → `rows 30 base_mismatched 13 exempt 1 valid_corrections 13 false_corrections 0 unresolved 0 append_only True met True` — matches report; receipt equals committed `c2r/c2r-tip.json` except the `tip` field (committed receipt measures dc4258bd; see defect 1). `--list` shows `CR31:11/12/13:C1:p1 ok=True` with distinct keys `(11|C1|p1)`, `(12|C1|p1)`, `(13|C1|p1)`.
- Kill rule, both directions (committed receipts verified; fixture trees are synthetic and not re-runnable here): `c1/controls/KeyCollapse/frozen-counter.json` — frozen counter accepts one collapsed `CR31:C1 collapsed:p1` → `valid 11 unresolved 0 met True`; `repaired-counter.json` — same tree → `false 1 unresolved 3 met False`, collapsed id read `ok=false key="|C1|p1"`. `c1/controls/DupKey/repaired-counter.json` — two corrections on `(11|C1|p1)` → both `ok=false`, `false 2 unresolved 3 met False`. Matches report exactly.
- Preregistration `.ufo/waves/round-32/preregistration.json` frozen at 9afaf0e9, before any data; predicate names met formula and the exact after counts.

Verdict: verified (re-measured).

### C2 — operability 8 → 8 (registry gate occurrence → meaning)

Evidence-verified per PROTOCOL §Gate standard (Closure consequence): this verifier did not execute the lane's gate; committed evidence verified instead.

- Registry row: SKILL.md round-32 block registers gate v2 with entry command, exit map (0/1/2 declared), `--selftest` spelling, pinned values (`c2/SUMMARY.md`, `selftest-final.out`), write scope — schema complete per §Registry. Round-17 and round-26 counters moved from prose to real rows in the same block.
- Self-test tally: `c2/selftest-final.out` tail `GATE_SELFTEST pass=6 fail=0`, lane-tip arm names revision 967d88528c1d — revision measured is recorded.
- Frozen-run verdict: `c2/gate-tip.out` (committed 3f1a7330) `registered 10 unregistered 0 defective 0`; red intermediate `c2/gate-data-tip.out` (defective 1: count-c2r.py pinned path missing at dc4258bd) committed in 967d8852 — the gate caught its own registry row before the receipt landed; green at 967d8852.
- Do-nothing controls (v1 bytes from base): `controls/thin-row-v1.out`, `empty-exit-v1.out`, `nonexistent-path-v1.out`, `prose-only-v1.out` each read `registered 9 unregistered 0` + `EXIT_CODE=0` — occurrence-only gate passed every defective fixture, matching the report.
- v2 before-state: `before-base.out` — base tree exits with `unregistered` for the round-17 and round-26 prose-only counters.
- v2 fixture arms: `controls/thin-v2.out` (thin-row + empty-entry + empty-exit-map, defective 3), `controls/noexit-v2.out` (empty-exit-map, defective 1), `controls/badpath-v2.out` (missing-path:.ufo/waves/round-999/count-c999.py, defective 1) — each named defect printed.
- Mutation arms: `MutNoExitMap-vs-CtlNoExitMap.out` exit 0 (check load-bearing), `MutNoPath-vs-CtlBadPath.out` exit 0 (load-bearing), `MutNoThin-vs-CtlThin.out` still exit 1 via empty-entry/empty-exit-map (entanglement disclosed, matching SUMMARY and report), `MutNoExitMap-vs-CtlBadpath.out` negative control stays exit 1.

Verdict: verified on substance (evidence-verified, not executed); citation defect routed (defect 2 below).

### Reconciliations (routed defects 5–6, not claims)

- RefRepair pointer: `grep -n "w2/out/RefRepair" SCORECARD.md` → line 1723 still carries the drift in the round-31 attempt-3 table; the round-32 appended correction names the true receipt path `.ufo/waves/round-31/controls/RefRepair/receipt.txt` (verified to exist). Correction is appended, not a rewrite — append-only discipline held.
- w2 seat census: re-ran `find .ufo/waves/round-31/w2/out -maxdepth 1 -type d | wc -l` → 44 (43 seat dirs + `out`); `grep -rli instrumentdup .ufo/waves/round-31/w2/out` prints nothing. Matches the appended record (44 planned / 43 dirs / ConnInstrumentDup unverifiable).

### KQ36 re-runs (spot)

Committed receipts match the report: r29 `statements 69`, r30 `statements 141 … valid_corrections 13 unresolved 0 met True`, r31-c1 `registered 18 counted 17 target 12 met True not-counted ['K31-10']`, r31-c2 `unresolved 3 met False`.

## Axis harm check

`git diff 18464d08 907cdcc0a -- SCORECARD.md` — append-only round-32 sections; scores held (calibration 7, operability 8, depth 7, freshness 8, coverage 9, adjacency 7); capabilities table untouched. `corpus/knowledge/` last touched round-31 (expansion surface unchanged). SKILL.md +15 lines (registry block), LOG.md +32 (round-32 entry with pointers), PROVINCE.md +11 / corpus/README.md +13 (dispositions). No axis harmed.

## Discernment spot-check (LEARNING.md — checked from outside)

| Item | Gate decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S193 (round-32 Gate's one admission; own-work tier A) | admit | `git show c4c46ad5b87d:tools/gate-registry-check.py` docstring "Contract" section | agree | Quote "A path is registered iff it occurs in a cell of a row of such a table." verbatim in the source (line 15 of the file at that commit; lesson says line 22 — location/word-count imprecision, see defect 3). Tier A scoped to the gate's own population and semantics is honest for own-work; used-by paths (lesson, SKILL.md) exist. |
| Round-32 Gate reject sample | none recorded ("zero rejections") | `git diff 18464d08 907cdcc0a -- corpus/SOURCES.md` | n/a — verified the zero | The Gate logged zero rejections; the SOURCES diff shows exactly one row added (S193) and no rejected rows, so no reject candidate exists to sample this round. |
| Standing reject S104 (compensating reject-side sample from the registry) | reject (round-24, carried) | `curl https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c` lines 138–152 | agree | `mark_object` returns 0 for a promisor object before the `HAS_OBJ` branch, exactly as the rejection reason claims — fsck green cannot prove local completeness for promisor objects; flip condition is stated and remains unmet. |

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, final line `ok …/corpus/SOURCES.md`; 193 `| S` rows (W04 cross-scope duplicate-url warnings intentional, unchanged since round 11). Matches report (192 → 193).

## Trend verdicts (closure's own, from the evidence above)

- expansion — **unchanged.** No `knowledge/` admission (dir untouched this round); S193 is an own-work instrument row, not covered-ground knowledge; census +1 row is the S193 instrument row only.
- quality — **improved.** The two round-31-closure instrument defects (non-injective key, occurrence-only gate) are repaired with fail-capable controls and mutation arms; two routed record defects (pointer drift, seat census) reconciled by append with re-run commands; the r29/r30/r31 counters re-run byte-stable at the new tip; no admitted entry failed its re-check this round.
- discernment — **improved.** Both kill rules were hunted by the lane before admission and are receipted red-handed in both directions (KeyCollapse frozen-accepts/repaired-refuses; DupKey uniqueness refusal); my non-author sample agrees with the one admit (S193) and with the compensating standing reject (S104); the report holds the axis scores instead of self-promoting and discloses its own entanglement and limits.

## Routed defects for round 33

1. **Report-internal receipt-lineage contradiction (record precision).** Report "Receipt lineage honesty" says `c2r/c2r-tip.json` measures 967d88528c1d and is committed in 3f1a7330; the committed receipt's `tip` field reads dc4258bdb08d and `git log --diff-filter=A` shows it committed in 967d8852. The report's own C1 section states the dc4258bd measurement correctly — the honesty bullet contradicts it. Fix by appended correction naming the superseded sentence.
2. **C2 citation overbroad / three stale receipt files (evidence standard).** Report and `c2/SUMMARY.md` cite `c2/controls/*-v2.out` for "each fixture exits 1 with its named defect"; `thin-row-v2.out`, `empty-exit-v2.out`, `nonexistent-path-v2.out` contain the base-tree clean output (byte-identical to `before-base.out`, `registered 7 unregistered 2 defective 0`, no named defect). The genuine fixture arms are `thin-v2.out`, `noexit-v2.out`, `badpath-v2.out` (verified above). Replace or relabel the three stale files, or correct the citation — a pointer whose bytes don't show the claimed output is not evidence.
3. **S193 quote location imprecision (trivial).** Lesson says quote at line 22, 16 words; source at c4c46ad5 has it at line 15, and it is 17 words (≤25 contract satisfied). Correct the lesson's parenthetical by append if touched next round.
4. **Receipt completeness (minor).** `gate-tip.out` and the v2 control receipts record no `EXIT_CODE` line and gate-tip.out names no revision inline (revision survives only in the commit message and the selftest lane-tip arm). The v1 controls and mutation arms do record exit codes; make gate run receipts record `EXIT_CODE=` and the evaluated revision like the v1 controls do.

Non-blocking observation for the operator: SHONEN boxes 1–4 all carry `[~]` (author-asserted). Box 2's evidence (round-16/17 live receipts, round-32 kq36 live re-run) is committed and resolvable, and boxes 1/3/4 are checkable by a non-author against committed bytes — the boxes look fully checkable in a promotion review; writing `[x]` is operator/promoter-owned and was not done here.

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `cc4698035927` (round-32 verifier spot-check: correct lane tip citation):

`````text
lane tip verified: kama-shokunin@907cdcc0a76f8656fde4574c0c50725fcea42fa9 (master; lane HEAD before round: 18464d0866afd5c4b471c8478d72b079d82d1fa8)
`````
