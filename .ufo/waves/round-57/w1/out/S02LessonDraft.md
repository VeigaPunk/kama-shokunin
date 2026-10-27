# S02LessonDraft — §Gate and §Mistakes additions for `corpus/lessons/round-57.md`

Seat: `S02LessonDraft` (scribe, leaf; no subagent dispatch). Axis framing per lane `shokunin.conf:52`
/ SCORECARD (operability + calibration); the `MISSION.md:29` conflict is recorded, not resolved. No
source-tree, lesson, SCORECARD, fleet, or git mutation by this seat; the only writes are this file,
`.ufo/waves/round-57/reports/R57Item07LessonDraft-case7.md`, and copied receipts under
`.ufo/waves/round-57/reports/case7-receipts/`. Tooling: no installs, no pacman transactions.

State of the target at the final observation (`8a7f19760242bbe523fa2d7d1b22528b587633c1`):
`corpus/lessons/round-57.md` is **committed and tracked**, so it is append-only. The draft below is
therefore **additions only** — one appended Gate section and appended Mistakes rows — and rewrites no
filed line. The filed lesson already carries `calibration-staleness`, `discernment-disagreement`, and
`no-op-counter` rows (the middle one appended by another seat after this seat's first read); this
draft does not duplicate them. Tip log and every command/exit are in the case-7 evidence file.

## Proposed appended section (exact text; append at end of `corpus/lessons/round-57.md`)

```markdown
## Gate — round-56 outside closure, spot-check advice, and S516 count correction (appended)

- **Round-56 outside closure recorded.** `corpus/lessons/round-56-verifier-spotcheck.md` (non-author, committed at the base `b89bdab2cc114735ec5d331c6c610134258f7864`) rules C1 operability **improved** within its synthetic-child scope, C2 calibration **unprovable** (its own no-op receipt `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0), discernment **harmed** (S513 rejection disagreement), so the all-claims admission rule is not met. The round-57 claims are one routed repair (C1, round-56 routed defect 2) and one stale-fact correction surfaced by the frozen counter (C2, `42`→`43`); they do not re-claim round-56 C2, and no round-56 predicate or target is amended after data.
- **S515 re-open confirmed; no existing row cell changed.** Fetched live 2026-10-27 at https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT, §GIT_CONFIG_COUNT, page “git-config last updated in 2.56.0”. Located quote: “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration” (18 whitespace-delimited words); the round-56 snapshot `.ufo/waves/round-56/sources/git-docs-git-config.html` still carries the same sentence. `git diff b89bdab2 8a7f1976 -- corpus/SOURCES.md` is one insertion (S516) with no existing row cell changed.
- **S516 quote-count correction.** The filed S516 Gate counts its `main()` quote as “(5 words)”; whitespace-delimited tokens are **6**: `results.append(run("base-old-counter",` / `OLD,` / `"missed",` / `OUT` / `/` / `"base-c1.out"))`. The lane's own convention is whitespace-delimited (`corpus/SOURCES.md:194`). The quote is a byte substring of `tools/round56-env-leg-battery.py` at base line 70, inside the cited `main()` lines 69–83; the ≤25-word rule is unaffected and the S516 admit stands. Append this correction rather than editing the filed line.
- **Admit/reject decisions spot check — advisory only.** The 64 dispatched seats are lane authors; their reports are not the outside spot-check. Advice to the closure: re-affirm the S512/S514/S515 admits (quotes located under 25 words; S515 re-opened live this round) and record the S513 disagreement with its observed counts — the reopened `ld.so(8)` snapshot carries `Dynamic string tokens` ×4 and `secure-execution` ×11, the topics S513's own flip names — rather than silently keeping the reject; narrow S513 in a superseding row or propose the S513-derived QUALITY criterion while holding admission until outside closure agreement, consistent with §Planned (round 57) item 2's KQ98 hold.
- **Citation check at tip `8a7f1976`.** Under the counter's own brace expansion, §Round 57's receipt tokens resolve to `.ufo/waves/round-57/controls/base-c1.out`, `.ufo/waves/round-57/measured/c2-committed-tip.out`, `.ufo/waves/round-57/measured/noop-c1.out` and `.ufo/waves/round-57/measured/c1-committed-tip.out`; all four exist at that tip (`git cat-file -e`). `tools/round42-selfdesc-reconcile.py` checks cited receipts only for rounds 40–41 (`RECEIPT_ROUNDS`), so its `receipts=0` says nothing about round-57 citations; repeat the per-path check at the final tip.
- **Assimilation: none.** `considerthese/2026-10-26.md` proposal 3 (“Keep a running count of counters that a shortcut can satisfy”) is opened by this round's defect class but not implemented; proposal 4 remains pending; no proposal file was edited.
```

## Proposed appended `## Mistakes` rows (exact text)

```markdown
| class | evidence | captured-by | fix |
|---|---|---|---|
| axis-conflict (inherited, round-56 routed defect 1) | `MISSION.md:29` says `kama: { cwd: kama-shokunin/, axes: "operability + freshness (local model serving/endpoints)" }`; `shokunin.conf:52` says `kama\|kama-shokunin\|operability + calibration (local model serving and endpoint health)`. The frozen amendment `controls/freeze-amendment.txt` orders C1 operability / C2 calibration; the seat-context claim text ordered them the other way. | No gate compares the lane config row to `MISSION.md`; each round restates the conflict in prose only. | Record both lines verbatim and route to L0; do not resolve in-lane. Fix shown able to fail: a line comparison of the two files is itself the check, and it currently returns two different axis strings. |
| vacuous-target limit (inherited, round-56 routed defect 2; partial repair) | `git show 89dc4f52:.ufo/waves/round-57/controls/c1-noop.py` prints `mismatches=0 maxN=46 met=True`, exit 0, reading no input, so the round-42 counter's `mismatches=0` target stays forgeable. The C1 repair binds AST call sites only: a battery whose calls all sit under `if False:` yields `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 (`case7-receipts/new-checker_static-calls.txt`). | Round-56 §9 do-nothing rule and round-56 lesson line 29; no gate requires the round-42 counter itself to fail a no-op, and no gate compares SCORECARD claims with `SHONEN.md`. | State C1's limit as a call-site inventory, never “executed battery entries”; leave the round-42 counter no-op and the absent SCORECARD/SHONEN disagreement test as open routed defects. Fix shown able to fail: the `if False:` fixture fails a runtime-execution predicate while passing the frozen C1 predicate. |
| landing/contract (inherited, round-56 routed defect 4) | Committed `.ufo/waves/round-56/measured/append-only-audit-at-784.out` records `unrestored=2 ... bad_declarations=4` and `threshold=1 exit=1`, naming `corpus/README.md:761` (three declarations) and `corpus/README.md:1239` (`corpus/lessons/*.md`); neither line declares the corresponding file(s) append-only. | No gate binds a contract pointer to the line's actual declaration; round 56 reported but did not repair the inherited state. | Re-point the four declarations to lines that declare append-only, in an append-only new section; route the two unrestored SCORECARD head events (`e81d90e6`, `4bd7521a`). Fix shown able to fail: rerun `python3 tools/append-only-audit.py --to <tip>` and require `bad_declarations=0`; the committed receipt is 4. |
| claim-target conflation (round 57's own) | Frozen `controls/base-c1.out`: `r41=1 ... mismatches=1 maxN=56 met=False`, and its only detail is the calibration run expecting `42` against 43 committed spotcheck blobs at `b89bdab2`; `caps=0`, and `canon()` selects the round-49 table (11 rows). `maxN` then moved 56→57 when the `## Round 57` SCORECARD section was appended, changing no measured file: it is `max(^## Round N)` (`tools/round42-selfdesc-reconcile.py:167-168`). `maxN=46` exists only as the hardcoded literal of the no-op controls; no counter or SCORECARD field expects `46`. | The seat-context claim text paired C1 with calibration and named a “stale canonical capability row count” and an “expected 46”; the frozen amendment and this lesson assign C1=operability, C2=calibration `42`→`43`, and no artifact derives 46 or a canonical-row mismatch. | Record `maxN` as the maximum `## Round N` heading, separate from canonical selection (round 49, 11 rows) and from the r41 stale literal (42→43); future claim text must name the field it measures. Fix shown able to fail: `grep -rn "maxN=46" .ufo/waves/round-57/` returns only no-op artifacts while the real counter printed 56 then 57. |
| quote-count (round 57's own, S516) | The filed Gate counts the S516 quote `results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))` as 5 words; whitespace-delimited tokens are 6, the convention fixed by `corpus/SOURCES.md:194` (“17 whitespace-delimited words”). The quote is byte-present at base battery line 70. | No gate re-counts a quoted passage's words; the closure spot-check asked only for a ≤25-word located quote. | Append the correction (6 words) in the Gate appendix; the admit stands because the quote is located and ≤25 words. Fix shown able to fail: `len(quote.split())` returns 6 against the filed 5. |
| receipt-check coverage (round 57's own) | `tools/round42-selfdesc-reconcile.py` checks cited receipts only for `RECEIPT_ROUNDS = (40, 41)`; its `receipts=0` is silent about round-57 citations, which the lesson and §Round 57 rely on. | The counter inherited a fixed two-round receipt window; no round advanced it while round sections kept adding cites. | Add the round to `RECEIPT_ROUNDS` when its section lands, or check cited paths in the round's own gate; at `8a7f1976` the four brace-expanded paths of §Round 57 all exist. Fix shown able to fail: cite a deleted path in §Round 57 and the counter still reports `receipts=0`. |
```

## Evidence summary (full receipts in the case-7 file)

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip b89bdab2cc...
r41=1 ... mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1

$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip 8a7f1976
r41=0 ... mismatches=0 maxN=57 met=True
exit=0

$ git show 89dc4f52:.ufo/waves/round-57/controls/c1-noop.py   # worktree copy since deleted
mismatches=0 maxN=46 met=True
exit=0

old checker, matching-roster no-op : present=1 roster_match=1 kills=1 controls=2 met=True  exit=0
new checker, same no-op            : present=1 roster_match=1 kills=1 controls=2 met=False exit=1
new checker, genuine battery       : present=1 roster_match=1 kills=1 controls=2 met=True  exit=0
new checker, calls under `if False:`: present=1 roster_match=1 kills=1 controls=2 met=True  exit=0
```

- C2 predicate reproduced (`mismatches=1`→`0`) at the named tips; its target stays forgeable.
- C1 predicate reproduced; the binding is a static AST inventory, not execution.
- S515 re-opened live; 18-word quote located; snapshot matches; SOURCES diff base→`8a7f1976` is one
  insertion (S516), no existing cell changed.
- S516 quote present at base line 70; filed word count 5 is wrong (6).
- S513 disagreement and the four invalid append-only declarations reproduced from committed bytes.
- §Round 57's four brace-expanded cited paths all exist at `8a7f1976`; the counter does not check
  round-57 receipts (`RECEIPT_ROUNDS` = 40, 41).

## Conflicts reported verbatim (not resolved here)

1. Seat-context claim text: "C1 calibration—repair the stale canonical capability row count, counter
   currently reports maxN=56 instead of expected 46; before output mismatch=1. C2 operability—distinct,
   actual canonical-row execution/content binding; a no-op currently reports met=True exit 0."
   `controls/freeze-amendment.txt`: "C1 is the frozen round56-prereg-check no-op control defect,
   operability axis ... C2 is the tools/round42-selfdesc-reconcile.py stale calibration count,
   calibration axis ... expects 42 but the actual committed outside verifier spotcheck count is 43".
   The filed lesson and SCORECARD follow the amendment; the context text swaps the axes and names
   `46`, which exists only as the no-op fixture's literal.
2. `MISSION.md:29` (operability + freshness) vs `shokunin.conf:52` (operability + calibration):
   recorded, routed to L0, not resolved.
3. `corpus/lessons/round-56.md` still says the independent spot-check is "pending at report time";
   the closure file now exists at the base. Recorded in the appended Gate text; round-56 bytes are not
   edited (append-only).

## Findings

1. C2 remains a one-line factual correction, not counter fidelity; its `mismatches=0` target is
   reachable by a no-input script (`controls/c1-noop.py`).
2. C1 is real for the frozen predicate but bounded to static call sites; the local name `executed`
   invites an overclaim. Recommend the appended Gate/Mistakes text state the limit explicitly.
3. The S516 Gate word count is wrong by one (5 filed vs 6 whitespace-delimited) — a small but exact
   calibration defect in the round's own gate.
4. The self-description counter's receipts check covers rounds 40–41 only; round-57 citations are
   unchecked by it, so the closure must run the per-path check at the final tip.
5. Of the four round-56 routed defects, the filed lesson now records defect 3 (discernment) and
   partially defect 2 (no-op binding); defects 1 (axis authority) and 4 (append-only contract) are
   not recorded anywhere in round-57 artifacts, and the C2-strengthening half of defect 2
   (SCORECARD/SHONEN disagreement test) is absent.
6. Live worktree churn observed while this seat worked: the frozen control bytes
   `.ufo/waves/round-57/controls/{c1-noop.py,noop-c1.out,noop-c2.out}` are tracked at `89dc4f52` but
   were deleted from the working tree by another seat (`git status` shows `D ...`), and a
   `controls/noop-fixture/` directory appeared at 15:17. Their committed bytes are archived at
   `case7-receipts/frozen-*`; citations in the drafted rows use the committed blob path so they stay
   auditable if the deletion is committed.

## Out of scope (not touched)

§Claims rewording, §Census text, trend verdicts, LOG/SCORECARD/QUALITY/SOURCES edits, any counter or
checker repair, commits/pushes, any claim of a non-author spot-check. `considerthese/2026-10-26.md`
proposal 3 implementation is out of scope (assimilation: none).

## Artifacts

- `.ufo/waves/round-57/w1/out/S02LessonDraft.md` (this report)
- `.ufo/waves/round-57/reports/R57Item07LessonDraft-case7.md` (distinct case-7 evidence)
- `.ufo/waves/round-57/reports/case7-receipts/{old-checker_noop,new-checker_noop,new-checker_genuine,new-checker_static-calls}.txt` (this seat's runs)
- `.ufo/waves/round-57/reports/case7-receipts/frozen-{c1-noop.py,noop-c1.out,noop-c2.out}` (frozen control bytes from `89dc4f52`)
- Scratch `/fast/scratch/hyaku/kama-r57/S02LessonDraft/` removed after receipts were copied.
