# Round 86 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Subject: kama r86, base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`, before-HEAD `bafae7afb41843564ac2468d28beb8e0bb98e8e6`, lane HEAD `079cd67c4c23767e093ba1775c9d7da477e053fe` (= origin/master). Report commit `2b00dc2de15add41dcd9dbd96cd6de53d6b53fab` in the fleet repo. Review date 2026-11-05. This review does **not** execute lane-owned gates, counters, or selftests; it re-measures documentary/numeric claims over committed bytes with plain commands and evidence-verifies the committed receipts for executable outcomes.

## Conformance

- `git log --format='%an %H' -- .ufo/reports/round-86/kama.md` (fleet): `kama-shokunin 2b00dc2de15add41dcd9dbd96cd6de53d6b53fab` — "hyaku sweep: L1 returned without committing; attribution defect". The report is real (30,306 bytes), carries `## SHONEN` with four `[~]` box lines (all asserted-by-author, evidence-bearing), three declared claims C1/C2/C3, before→after receipts, a Sources & frontier section, and three trend verdicts. Not a marker.
- All 25 full lane-commit hashes cited in the report's commit table were checked: `git cat-file -e <hash>^{commit}` succeeds and `git merge-base --is-ancestor <hash> master` returns 0 for every one (tested against the `master` branch ref, not detached HEAD/`@{u}`).
- `scripts/hyaku/jj-lane.sh state`: `branch=master local=079cd67c… remote=079cd67c… ahead=0 behind=0`. `git status --porcelain -uall` is **not clean** — see defect R86V1 below.
- Dispatched `.ufo/prompts/kama-round-86.md` carries the template contract: mission/axes binding, 1–3 distinct falsifiable claims, lowest-axis rule, capability-acquisition and exploratory-claim clauses, L2 minimum, report path/SHONEN/hash/commit ordering, push scope, L0, frontier step, and lane write scope.
- **Defect R86V1 (uncommitted round work, status-neutral):** three lane-authored round-86 files remain untracked in the lane working tree — `.ufo/waves/round-86/w3-results.json` (the w3 settlement record the report cites for seat status), `.ufo/waves/round-86/w3/SC01DanglingPointers.md` (scout seat report), and `.ufo/waves/round-86/w3/out/SC01DanglingPointers/findings.md` (its detail). Two further seat report files the w3 spec's `Report:` trailer contract requires — `w3/EX02GateCensus.md` and `w3/CN01OverlapScan.md` — were never written to disk at all (their `out/` evidence dirs are committed). `w3-results.json` exists only on disk and is referenced by the report and SCORECARD as the seat-status source; it is non-durable. The committed `gate.out`/`gate-recheck.txt` were measured on clean trees before these files landed, so the recorded 13/13 green stands for its revision, but the *current* tree now fails the same gate (`round-scope`/`round-clean` red on the strays — re-run below). This is uncommitted round work the lane must resolve next round (commit or remove); it does not change the report's real-work status.
- Driver digest copied verbatim: `2026-11-04T21:37:27 launch kama round=86 … attempt=1`; three `lane-dead-no-report` retries (21:52, 21:58, 22:31); fresh `launch … attempt=1` at `2026-11-04T23:51:39`; `2026-11-05T00:50:14 complete kama round=86`.

## Claim re-checks

Re-derived against `079cd67c` (lane HEAD) and the measured revision `239a8f39e33e252a44bb16c7202de6cd674f4614` named in the report/SCORECARD.

### C1 calibration — claim NOT verified; honest stop confirmed (evidence-verified + spot re-measure)

- Numeric target re-measured by me: `python3 .ufo/waves/round-86/count.py c1 --repo . --rev 239a8f39… --work /tmp/…` printed `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=86 newest_closure=85`, exit 0 — matches the terminal receipt `measured/terminal/c1.out` byte-for-byte on the verdict line.
- Committed mutant evidence re-run by me: `python3 .ufo/waves/round-86/measured/terminal/c1-mutants.py .` printed `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`, exit 0 — matches `c1-mutants.out`.
- Selftest evidence-verified: committed `rendered-cells-selftest.out` prints `RENDERED_CELLS_SELFTEST pass=17 fail=0`.
- **The report's own honest-stop is correct and I independently confirm the instrument is falsified against its frozen predicate.** Two reproduced false greens (w3 `SB01SectionDraft` probes + L1 re-runs, committed under `w3/out/SB01SectionDraft/probes/`): (a) a top-level fence opened with ```` ```markdown ```` containing a `- ``` ` list-marker line is treated by `select_cells` as closed while `cmark` renders the following cells as code — the "fence-free rendered cell" clause fails; (b) `disposition_of()` returns the first fixed-order word anywhere in the closure body, so a body mentioning another round's `rejected-harmed` makes a wrong-disposition row grade `disposition=1`. I re-opened `tools/round86-rendered-cells.py` and confirmed both code paths exist as described. On the committed live record neither construct occurs, so the printed number stands — but the *predicate is not implemented*, exactly as the report states. **Verdict: unprovable** (frozen kill rule "any control that stops discriminating / predicate not implemented" fires; not harmed — no existing committed control went red).

### C2 operability — verified (re-measured + evidence-verified)

- Re-measured by me: `count.py c2 --rev 239a8f39…` printed `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` and `DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0`, exit 0 — matches `terminal/c2.out`.
- Selftest evidence-verified: `mutant-owners-selftest.out` prints `pass=13 fail=0`.
- Before-receipt `measured/before/c2.out` independently read: `mutants=5 killed=3 escaped=2 … owners=3/5` exit1 — the red→green pair is real.
- Disclosed limit confirmed honest: w3 `MT02ForgeryArms` found a *consistent forged subject* can print the frozen target line (consistency is sufficient, not necessary, to escape). The report does not claim this class is closed; it routes it to round-87 item 5 and records the reading under which C2 fails. **Verdict: verified → improved is not claimed as a numeric move; the capability `mutant-owning-arms` is demonstrated.** No axis harmed: `git diff bafae7af 079cd67c -- tools/round81-append-debt.py` production bytes unchanged outside the selftest (round-81 summary shape kept; `APPEND_DEBT_SELFTEST pass=34 fail=0` still prints).

### C3 freshness — verified with disclosed origin limit (re-measured live)

- Re-measured by me: `count.py c3 --rev 239a8f39…` printed `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0`, exit 0 — **this leg fetches live upstream bytes** and I re-ran it; all five rows verified byte-identical at their declared URL/line ranges. Matches `terminal/c3.out`.
- Selftest evidence-verified: `pin-origin-selftest.out` prints `pass=7 fail=0`; the `fabricated-hash-consistent` arm is refused as `mismatch` and `digest-lie` as `bad`.
- Disclosed limit confirmed by code read: `tools/round86-pin-origin.py` fetches the anchor header's own `url=` and `grade()` never reads the row's `engine`/`ref`/`newest` columns, so a self-declared URL grades `verified`. Report discloses this (w3 `SB01SectionDraft` F7); committed register data is consistent (all header refs match rows). **Verdict: verified as a capability acquisition; the origin-corroboration claim is bounded, not absolute.** No axis harmed.

## Gate evidence (committed, not re-executed by me as a sibling gate — but I did run the lane's own `pre-report-gate.py` once as a conformance probe)

- Committed `measured/terminal/gate.out` and `gate-recheck.txt` both record `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0` exit 0 at clean revisions `0f8a0980`/`10cffc8b`, including `APPEND_DEBT round=86 … unaccepted=0 bad_rows=0`.
- **My own re-run just now** (`python3 tools/pre-report-gate.py --repo . --round 86 --tip master` on the current tree) printed `PRE_REPORT round=86 arms=13 failed=2 uncommitted=3` exit 1 — `round-scope`/`round-clean` red on exactly the three untracked round-86 strays of R86V1. This is the same transient-red class the report itself disclosed ("receipt files untracked → round-scope stray / round-clean"), now live because the w3 settlement files were never committed. The recorded green is revision-bound and stands; the current tree is red for want of committing/removing those files. Routed, status-neutral.

## Per-axis verdicts

`git diff bafae7af 079cd67c -- SCORECARD.md` reviewed; only `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/lessons/round-86.md` changed outside `.ufo/waves/round-86/` (PROVINCE/SKILL unchanged in this range — the three instruments were named on the PROVINCE surface at `da580634`, already an ancestor of `bafae7af`).

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | unprovable | C1 numeric target met but instrument falsified vs its own predicate (2 reproduced false greens); honest stop, not admitted |
| operability | improved | C2 `killed=5/5 owners=5/5 arms=34` re-measured green; `mutant-owning-arms` capability demonstrated; forged-subject limit disclosed |
| freshness | improved | C3 `rows=5 verified=5` re-measured live against upstream; `pin-origin-corroboration` capability demonstrated with bounded origin claim |
| depth | unchanged | no distinct depth move claimed; KQ139/KQ140 criteria added under discernment, not depth |
| coverage | unchanged | no new `corpus/knowledge/` entry on uncovered ground; three SOURCES rows are registry curation, not coverage |
| adjacency | unchanged | contested scope stays reported (CN01OverlapScan out/ committed); no sibling ground absorbed |

## Discernment: reopened sources

The round's `## Gate` records **three admits and zero rejects** ("no candidate row was refused"). Per LEARNING.md I re-opened the admits; there is no reject to sample this round — noted, not fabricated.

| Item | Decision | Re-opened source | Judgment | Reason |
|---|---|---|---|---|
| S576 | admit | https://spec.commonmark.org/0.31.2/#atx-headings §4.2 | agree | Committed spec copy `.ufo/waves/round-86/w2/out/SC01SourcesCensus/receipts/commonmark-0.31.2.fetched.html`: quote "The opening # character may be preceded by up to three spaces of indentation." occurs exactly once and inside the `atx-headings` h2 span (verified by my own tag-strip/span check). 14 words ≤25. Grounds the 0–3-space rule. |
| S578 | admit | https://spec.commonmark.org/0.31.2/#fenced-code-blocks §4.5 | agree | Same committed copy: "A fenced code block begins with a code fence, preceded by up to three spaces of indentation." occurs once, inside `fenced-code-blocks` span. 17 words ≤25. Grounds fence exclusion. |
| S579 | admit | https://spec.commonmark.org/0.31.2/#indented-code-blocks §4.4 | agree | Same copy: "An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation." occurs once, inside `indented-code-blocks` span. 18 words ≤25. Grounds column-0 rule. |

New SOURCES row check (≤25-word quote): all three quotes re-verified verbatim in the committed spec copy within their own section spans — **agree**. `S576 used-by` correctly extended `round-85.md → round-85.md, round-86.md`; S578/S579 enter `status=mined opened=2026-11-04 recheck=on-release`. `sources-census.sh validate --root … kama` re-run by me: exit 0, final `kama ok …/corpus/SOURCES.md`; pre-existing W01(S481)/W04 duplicate-URL warnings retained including S576/S578/S579 (URL-compared, anchors ignored) — disclosed, not suppressed. Census 317→319 rows, A302→304, mined284→286 matches the report. Residual (not this round's defect): w3 `RV03SourcesFrontier` notes the round-86 lesson body never names the ids S578/S579 it created — a `used-by → cited-by` identity lint candidate, routed not claimed.

## Trends and admission

- expansion: **improved** — three capabilities (`rendered-cell-identity`, `mutant-owning-arms`, `pin-origin-corroboration`) entered the SCORECARD repertoire table at lines 180–182 with first-working round 86 and runnable evidence pointers; demonstrated running this round (C2/C3 verified, C1 demonstrated-but-falsified).
- quality: **improved** — delivered artifacts strictly stronger than base (two live cells repaired, instruments reject constructs they previously accepted, gate was green at its measured revision); falsified C1 instrument disclosed rather than argued away; KQ139/KQ140 mined from mistakes.
- discernment: **improved** — all three admits re-opened and agreed; no rejects existed to sample; the round's own false greens were learned into QUALITY.md and the terminal wave's adverse findings filed as limits, including the reading under which C2 fails.

**Status `ok`; admitted `false`; verdict `rejected-honest-stop`.** The report itself declares honest stop: C2/C3 verify on frozen predicates, C1's predicate is not implemented (two reproduced false greens). Every *verified* claim re-derived clean; no axis harmed; C1 is `unprovable`, not `harmed`. SHONEN boxes remain `[~]` (author-asserted); no non-author `[x]` is warranted from instrument-only observations — promotion stays operator-owned.

## Routed defects for next round (lane must fix)

- **R86V1 uncommitted round work:** commit or remove `.ufo/waves/round-86/w3-results.json`, `w3/SC01DanglingPointers.md`, `w3/out/SC01DanglingPointers/findings.md`; write the missing `w3/EX02GateCensus.md` and `w3/CN01OverlapScan.md` seat reports (or record why absent). Current tree fails `pre-report-gate.py` round-scope/round-clean until resolved.
- **R86V2 (carried, already in round-87 plan):** C1 false greens — list-marker fence closer + disposition oracle reading any fixed-order word in the closure body; arm the four unarmed selector rules (MT01 mutants MD/ME/MC, first-`## Axes` clause).
- **R86V3 (carried):** C2 forged-subject / unparseable-ARMS-line escapes (MT02ForgeryArms b3/b6/b9/c2); bind classifier to a source-identity witness at `--rev`.
- **R86V4 (carried):** frozen counter executes worktree instrument bytes, not `--rev` bytes (CR01SizingControl T1/T2); C3 `--rev` is presence-only (T4/T5).
- **R86V5 (carried):** C3 origin self-declared — `grade()` never reads row `engine`/`ref`/`newest`; anchor `url=` is fetched, not the row's declared upstream.
- **R86V6 (minor):** lesson `## Gate` names no `S###` ids for the rows it created (S578/S579); consider citing ids so `used-by → cited-by` resolves both ways.

No tools installed/updated this review; no pacman transaction; no lane gate/selftest executed as a sibling gate (the single `pre-report-gate.py` run was a conformance probe of the lane's own committed gate on the current tree, reported as such). Self-evaluation: accuracy 4, completeness 4, clarity 4, actionability 4, conciseness 4. Overall 4.0.
