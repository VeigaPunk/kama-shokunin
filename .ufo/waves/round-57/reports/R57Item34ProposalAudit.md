# R57Item34ProposalAudit — considerthese 2026-10-26 proposal 3: disposition, relevance, and independent test

Seat: `R57Item34ProposalAudit` (item `round57/ProposalAudit/34`, scribe, leaf — no subagent dispatch).
Distinct case: 55 (separate evidence file: `.ufo/waves/round-57/reports/R57Item34ProposalAudit-case55.md`).
Axes in scope: operability + calibration (judged on calibration, operability). Wave base: `b89bdab2cc114735ec5d331c6c610134258f7864`; lane HEAD read at 2026-10-27T18:12Z was `8640e34cad02adcd247ba0862da63f6fb2aab0df`.
Scope honoured: read-only on the lane except this report path and its receipts; no commits, pushes, jj/git mutations, fleet files, sibling repos, or source-tree writes. No tools installed or upgraded (none needed).

## 1. Proposal 3, exact text

`considerthese/2026-10-26.md:33` (Self-improvement suggestions, item 3; the file's window is 2026-10-23 through 2026-10-26, rounds 39–45):

> **Keep a running count of counters that a shortcut can satisfy:** each SCORECARD section now has a “What `met=True` does not show” paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed.

The assignment context names it “the self-description counter shortcut tally” and says it is “opened this round”; the uncommitted round-57 lesson draft says the same (`corpus/lessons/round-57.md:16`: “`considerthese/2026-10-26.md` proposal 3 (counter-shortcut tally) was opened; this round addresses a concrete counter no-op defect but does not implement a multi-round tally”). That file is modified/untracked relative to the wave base (`git cat-file -p b89bdab2:corpus/lessons/round-57.md` → `fatal: path ... exists on disk, but not in 'b89bdab2...'`; `git status --porcelain -- corpus/lessons/round-57.md` → ` M`), so it is worktree text, not frozen base bytes.

## 2. Exact prior disposition

| When | Record (exact) |
|---|---|
| Round 46 | `LOG.md:2314`: “r46-D3 to the frontier as this round's lesson Mistakes row — `considerthese/2026-10-26.md` proposal 3, a running count of counters a shortcut can satisfy, written with a check that can fail” |
| Round 47 | `corpus/lessons/round-47.md:37`: “considerthese: … proposal 3 (running count of counters a shortcut can satisfy) → Mistakes row 1's check (seat X9Tally)” |
| Round 47 (planned round 48) | `SCORECARD.md:2735`: “promote the shortcut tally (`.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py`) to `tools/` with its `--check`”; `LOG.md:2324`: “Frontier, not claims: `considerthese/2026-10-26.md` proposal 3 … promoted to `tools/` with its `--check`” |
| Round 48 | `LOG.md:2327`: “shortcut tally promoted (X9Tally)”; addition commit `c4b2175d` (2026-10-26 19:51:07 -0300, “round-48: integration (measured) — … shortcut tally …”); `tools/shortcut-tally.py:10-13` names the proposal and the round-47 draft; `SKILL.md:1476` registry row (“Round-48 shortcut tally … `selftest pass=7 fail=0`”); standing run `.ufo/waves/round-48/measured/tally.out` (rev `c4b2175d`, 443 bytes, `exit=0`, only round-47 `detail:` lines, no per-round rows); measured results commit `1541a0dd` |
| Rounds 49–53 | per-round receipts: `tally-build.out` in every round, plus `tally.out` (49, 51, 52), `tally.int.out` (50), `tally-int.out` (51); every `measure.sh` runs `python3 tools/shortcut-tally.py --repo . --rev "$TIP"` with **no** `--rounds` and **no** `--check` |
| Rounds 54–56 | dark: no tally receipt (round-55 `measured/` holds only `c1-build.out`, `c2-build.out`; round-56 `measured/` has none); `grep -rn "shortcut-tally.py.*--check"` over rounds 40–56 measured receipts → no match |
| Round 55 correction | Seat `S6Considerthese` (`.ufo/waves/round-55/w1/out/S6Considerthese.md`) found the frozen disposition table false for proposal 3: “`tools/shortcut-tally.py` has been the standing tally for proposal 3 since round 48 … The true residual is not ‘a standing tally is pending’ but **run cadence**: the tally was dark in round 54 … and round 55”. The corrected lesson text (`corpus/lessons/round-55.md`): “**taken up round 47** (seat X9Tally draft …) and **promoted to the lane tool `tools/shortcut-tally.py` v2 in round 48** … This round's battery receipts add per-mutant kill evidence; no outside closure verdict on the tally itself exists yet.” |
| Round 57 | opened, not implemented (worktree lesson draft line 16 above); an outside closure verdict on the tally still does not exist |

Summary: proposal 3 is not pending — it landed as `tools/shortcut-tally.py` v2 in round 48. The open residual is its run cadence and its ability to read the recent record, not its existence.

## 3. Relevance to the round-57 claims

### 3.1 The claim formulations conflict in the record (reported verbatim, not resolved)

- Assignment context: “C1 calibration—repair the stale canonical capability row count, counter currently reports maxN=56 instead of expected 46; before output mismatch=1. C2 operability—distinct, actual canonical-row execution/content binding; a no-op currently reports met=True exit 0.”
- Frozen control file `.ufo/waves/round-57/controls/freeze.txt`: “claims=C1 calibration stale canonical-table count; C2 operability canonical-row execution binding” and “noop_C1=met=True exit=0 despite skipping data / noop_C2=met=True exit=0 despite skipping data”.
- Pre-data correction `.ufo/waves/round-57/controls/freeze-amendment.txt`: “supersedes the earlier round-57 freeze's claim ordering only … C1 is the frozen round56-prereg-check no-op control defect, operability axis … C2 is the tools/round42-selfdesc-reconcile.py stale calibration count, calibration axis: its base output says the calibration run expects 42 but the actual committed outside verifier spotcheck count is 43 … C1 and C2 are distinct axes, each measured independently.”
- Committed `SCORECARD.md` §Round 57 (HEAD line 3149): “C1 is the frozen round-56 prereg checker no-op defect (operability); C2 corrects the verifier-spotcheck count (calibration).” Table: C1 “bind declared roster to actual battery call sites”, C2 “re-anchor the SCORECARD verifier-spotcheck count”.

These are three different orderings/targets for C1/C2. Per the seat role, they are reported for the canonical Rust judge; this scribe does not resolve them. Note also that the assignment's “maxN=56 instead of expected 46” is not what the frozen receipts show: `.ufo/waves/round-57/controls/base-c1.out` = `mismatches=1 maxN=56 met=False` with detail “no stdout line == '42' (exit 0)”; `tools/round42-selfdesc-reconcile.py:13` defines `maxN` as the greatest `## Round N` heading number, and `.ufo/waves/round-57/measured/c2-committed-tip.out` records `mismatches=0 maxN=57 met=True` at tip `8640e34c`.

### 3.2 Relevance of proposal 3 to C1 (roster call-site binding / no-op must fail)

None direct. `tools/shortcut-tally.py` consumes SCORECARD disclosure prose and `.ufo/waves/round-N` mutation reports; it never executes a battery roster, so it cannot distinguish a declared roster from an executed one. Independent fixture evidence (case 55): a round whose only artifact is a literal no-op `controls/c1-noop.py` is invisible to the tally; the row reads `unreadable:no-claim-ids` when the disclosure names no claim id, and a disclosure that merely names `K1Cheat` and `C2` counts as one shortcut and passes `--check 5` (`fixture-57-named.out`). The only transferable element is methodological: the tally's selftest contains must-fail cases (`check-fails`, `unreadable-round`, `contradictory-report`, `selftest pass=7 fail=0`), the same “a check that cannot fail is not a check” rule C1 needs.

### 3.3 Relevance of proposal 3 to C2 (stale self-description count)

Indirect but same defect class. The tally is itself a self-description reader, and at the wave base it is stale and inert in exactly C2's class:

- default range is hard-coded `40-47` (`tools/shortcut-tally.py:895`), and no standing `measure.sh` overrides it, so the “running count” has not trended a new round since round 48;
- run over `--rounds 40-56` at base `b89bdab2`, `exit=0` with seven unreadable rounds (48, 49, 50, 51, 52, 53, 54); round 55 `ok` but with the frozen id family matching nothing (“naming blind spot, not a zero”); round 56 `no-disclosure`;
- the gate only goes red when asked: `--check 99` → `exit=1`, `latest=56 shortcuts=- limit=99 result=FAIL (unreadable rounds [48, 49, 50, 51, 52, 53, 54])`. No measured receipt invokes `--check`, so the standing receipts print `exit=0` while the instrument cannot read the seven most recent rounds.

So proposal 3 is relevant to C2 as a second instance of the same stale-self-description defect, and a running count that “lets João see whether counter design is getting harder to fool” would have to count its own unreadability and stale default to be honest. It contributes no repair to either frozen target this round.

### 3.4 Assimilation

None, consistent with the assignment (“Assimilation: none”). No proposal text was edited; no multi-round tally was implemented. This audit adds evidence only.

## 4. Non-author spot-check duties (advise only)

### 4.1 S515 re-open — Git config runtime environment pairs

- URL reopened this round: `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`
- Access: 2026-10-27T18:12:29Z (15:12:29 -0300); `curl -L --fail --silent --show-error` exit 0, 830605 bytes, sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a` — byte-identical to the lane snapshot `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html`.
- Location: anchor id `Documentation/git-config.txt-GITCONFIGCOUNT` (raw HTML line 5846); quote spans raw lines 5850–5852.
- Located quote (18 words, ≤25): “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration”. Page source uses `process&#8217;s` (U+2019), not ASCII `'`.
- Revision element: page carries “git-config last updated in 2.56.0”, matching the S515 row's revision claim.
- Verification: the ASCII-apostrophe variant (`process's`) is **not** present in the retrieved page; the word count is unchanged at 18. The SOURCES S515 row and the round-56 lesson render the quote with ASCII `'`; this is a transcription difference, not a wrong quotation, and the S515 admit stands. Follow-on text in the same section: “The config pairs are zero-indexed. Any missing key or value is treated as an error.”

### 4.2 One admit/reject decision spot check — S513 REJECT (advise only)

- Decision under check: round-56 Gate, `corpus/SOURCES.md:266` / `corpus/lessons/round-56.md` — “S513 — REJECT … `ld.so(8)` … this broad loader manual overlaps the dedicated rtld-audit(7) source S512 for the claim's only need … flip: a future claim about secure-execution, dynamic string tokens, or loader namespace semantics.”
- Re-opened live 2026-10-27: `https://man7.org/linux/man-pages/man8/ld.so.8.html` (exit 0, 41398 bytes, sha256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`, section anchors include `id="ENVIRONMENT"`, `id="DESCRIPTION"`). The named quote is present: “A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace” (18 words).
- Re-opened `https://man7.org/linux/man-pages/man7/rtld-audit.7.html` (exit 0, 26769 bytes, sha256 `a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153`): S512's quote is present — “the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries” (15 words) — so the “dedicated source covers the claim's only need” premise holds.
- The round-56 outside spot-check (`corpus/lessons/round-56-verifier-spotcheck.md`, “S513 reject — disagree”) holds that ld.so(8) also carries secure-execution and dynamic-string-token detail absent from the dedicated source and that the reject should narrow its scope or say why those topics are out of scope.
- Advice (no verdict claimed, seat is not the lane author): the reject is defensible for the LD_AUDIT-name claim and the row already conditions re-admission on those exact topics (“flip: …”); the outside's point is about rationale precision, not about re-admitting the source. The uncommitted round-57 lesson draft already records this as `discernment-disagreement` and says “Preserve the disagreement, do not claim discernment improvement, and re-open S513 before any later reuse of its gate decision” — that is the correct disposition; my addition is only that the flip clause already supplies the narrowing the outside asked for, so no wording change is needed for the current claim. Note also that the S515 ADMIT is consistent with my re-open (quote, location and revision marker all verify).

### 4.3 Round-56 outside defects and the lesson draft (status only)

The round-56 outside spot-check routes two defects that bear on this wave: “Strengthen C2-style calibration gates to bind actual executed battery entries and test SCORECARD/SHONEN disagreement; a roster literal/no-op harness must fail”, and “Revisit S513's rejection rationale and record the disagreement as a lesson/quality criterion if retained”.

- The first is the round-57 C1 target (`SCORECARD.md` §Round 57: “bind declared roster to actual battery call sites”); the author's measured receipt `.ufo/waves/round-57/measured/noop-c1.out` records the no-op fixture now at `present=1 roster_match=1 kills=1 controls=2 met=False`, `exit=1`, against tip `8caa23a2…`.
- The second is addressed as `discernment-disagreement` in the round-57 lesson draft (§4.2 above).
- Status caveat: `corpus/lessons/round-57.md` is ` M` in the worktree and absent from the wave base `b89bdab2` (verified by `git cat-file`), so its lesson-addressing is uncommitted at this read; I did not edit it. The remaining routed items (MISSION axis conflict, inherited append-only audit) belong to other seats or the closure, not to this item.

## 5. Commands, exact exits, artifacts

| # | Command (cwd lane unless noted) | Exact result |
|---|---|---|
| 1 | `curl -L --fail --silent --show-error -o git-config-live-2026-10-27.html https://git-scm.com/docs/git-config` (scratch) | exit 0; 830605 bytes; sha256 `706b1566…` |
| 2 | quote/word/anchor check over that HTML | 18 words; U+2019 present; ASCII variant absent; anchor line 5846; quote lines 5850–5852; `git-config last updated in 2.56.0` present |
| 3 | `curl … ld.so.8.html`, `curl … rtld-audit.7.html` (scratch) | exit 0 / exit 0; 41398 / 26769 bytes; sha256 `d9b7737e…` / `a95aa3fb…`; S513 quote 18 words present; S512 quote 15 words present |
| 4 | `python3 tools/shortcut-tally.py --repo . --rev b89bdab2…` | exit 0; `rounds=40-47`; rows 40–47 only |
| 5 | `… --rounds 40-56` | exit 0; rows 40–56; `unreadable:mutation-report` for 48,49,50,51,52,53; `unreadable:no-section` for 54; round 55 `ok` with naming-blind-spot note; round 56 `no-disclosure` |
| 6 | `… --rounds 40-56 --check 99` | exit 1; `latest=56 shortcuts=- limit=99 result=FAIL (unreadable rounds [48, 49, 50, 51, 52, 53, 54])` |
| 7 | `python3 tools/shortcut-tally.py --selftest --scratch <scratch>/selftest` | exit 0; `selftest pass=7 fail=0` |
| 8 | fixture repo (controls-only no-op) `… --rounds 57-57` | exit 0; `status=unreadable:no-claim-ids`; no output line references the control; documented sources exclude `controls/` |
| 9 | fixture `… --rounds 57-57 --check 0` | exit 1; `latest=57 shortcuts=- limit=0 result=FAIL (unreadable rounds [57])` |
| 10 | fixture with `Seat K1Cheat: … yet C2 reports met=True.` `… --check 5` | exit 0; `shortcuts=1 ids=K1Cheat counters=C2 … status=ok`; `latest=57 shortcuts=1 limit=5 result=PASS` |
| 11 | `grep -rn "shortcut-tally.py.*--check" .ufo/waves/round-4*/measured .ufo/waves/round-5*/measured` | no match |
| 12 | `git cat-file -p b89bdab2:corpus/lessons/round-57.md` | `fatal: path … not in 'b89bdab2…'`; worktree file is ` M` (uncommitted round-57 draft) |
| 13 | `git log --diff-filter=A --format='%h %ci %s' -- tools/shortcut-tally.py` | `c4b2175d 2026-10-26 19:51:07 -0300 round-48: integration (measured) … shortcut tally …` |

Receipts (byte copies from scratch, wave path): `.ufo/waves/round-57/reports/R57Item34ProposalAudit.receipts/` — `tally-base.out`, `tally-base-40-56.out`, `tally-check99.out`, `selftest.out`, `fixture-57.out`, `fixture-57-check0.out`, `fixture-57-named.out`, `s515-quote-check.txt`, `source-hashes.txt`.

Scratch: `/fast/scratch/hyaku/kama-r57/R57Item34ProposalAudit/` (created explicitly; receipts copied here before cleanup). No installs, no upgrades, no `pacman` transactions.

## 6. Findings for the judge

1. **Proposal 3's premise is already false**, and has been since round 48: the standing tally exists (`tools/shortcut-tally.py`, commit `c4b2175d`, `SKILL.md:1476`). Its open residual is run cadence, not existence (already recorded by round-55 seat S6Considerthese).
2. **The tally's unit is disclosure prose, not executed controls.** A literal no-op in `.ufo/waves/round-57/controls/` is invisible; a disclosure naming a seat and claim passes the gate. It therefore cannot audit either frozen round-57 target and must not be cited as a shortcut detector.
3. **The tally's own standing run cannot read rounds 48–54** and its default range stops at 47; plain invocation exits 0 with seven unreadable rounds while `--check` exits 1. No measured receipt uses `--check`. This is a concrete instance of the stale/inert self-description class the round-57 C2 target repairs (whichever ordering the judge adopts).
4. **Claim orderings conflict across the assignment, `freeze.txt`, `freeze-amendment.txt` and committed SCORECARD §Round 57**; reported verbatim in §3.1, unresolved by this seat.
5. **S515 admit verifies** (18-word quote, anchor, revision marker), with an ASCII-vs-U+2019 transcription note; **S513 reject is defensible for this claim**, with the round-56 outside disagreement preserved as the lesson draft's `discernment-disagreement` and S513 to be re-opened before any later reuse.
6. **Assimilation: none**, as assigned.

## 7. Out of scope / not done

No edits to proposals, SCORECARD, LOG, lessons, SOURCES, counters, controls, tools, or any shared file; no frozen counter re-run just to decorate this report (base/tip counter values are quoted from the committed `.ufo/waves/round-57/controls/` and `measured/` receipts); no judgment of C1/C2, no verdict on S513, no fleet actions.

Report: `.ufo/waves/round-57/reports/R57Item34ProposalAudit.md`
Case 55: `.ufo/waves/round-57/reports/R57Item34ProposalAudit-case55.md`
