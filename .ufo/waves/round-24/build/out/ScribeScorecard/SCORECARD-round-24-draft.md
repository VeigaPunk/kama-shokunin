# CANDIDATE — SCORECARD round-24 block (not appended)

**Status: DRAFT for the L1 (planner seat) to place.** Not appended to
`SCORECARD.md` by this seat (no production edits). Written to
`.ufo/waves/round-24/build/out/ScribeScorecard/SCORECARD-round-24-draft.md`.
Append point if accepted: after the round-23 block, `SCORECARD.md:1188`.

**No round-24 result is claimed.** Every round-24 measurement below is
`UNRUN` — this seat ran no grid, no selftest, no ledger, no parity check and
no mutant population. No number in this block is an observed round-24
outcome; the round-24 rows carry preregistered *expectations* only, and the
round-23 rows carry the numbers the closure independently re-ran.

---

## Round 24 — promisor-marked repository completeness and the round-23 verdict correction

Declared claim C1, **calibration 7 → 7** (narrow), on the lane's **lowest
assigned non-retired axis**: calibration **7** (`SCORECARD.md:23`) against operability
**8** (`SCORECARD.md:19`); saturation line 8/10 on every owned axis,
`SCORECARD.md:132`, so the stagnation nudge is inactive). Repair-first round:
round 23 closed **rejected-harmed** outside the author
(`/home/vgpnk/Projects/shokunin/MANIFEST.json` → `rounds[428]`, closed
2026-10-21T17:44:26Z) — calibration **improved**, operability **harmed**,
coverage / depth / freshness / adjacency **unchanged**; trends expansion
**unchanged**, quality **harmed**, discernment **improved**. Round base
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; preregistration committed at
`d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`
(`.ufo/waves/round-24/preregistration.json`, `LOG.md:1411-1431`).

This block does two things: it corrects the round-23 author verdict as
closed, and it predeclares the round-24 C1 measurements. It claims no
round-24 improvement.

### Correction to the round-23 author verdict (append-only; r23 bytes unchanged)

The round-23 block (`SCORECARD.md:1152-1188`) and the filed round-23 report
(`/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`, fleet commit
`410b511`) stand as filed. Their *verdict* is superseded by the closure:

| Round-23 statement (as filed) | Closed reading | Where |
|---|---|---|
| "Operability is **traded, not unchanged**" | Operability **harmed**. Disclosure of a trade does not waive the no-trade rule. | `SCORECARD.md:1171-1174`; closure `harm_ruling`; `LOG.md:1413-1415` |
| Trend: quality **improved** (KQ34, superseding rows) | Trend: quality **harmed** | `SCORECARD.md:1179-1183`; closure `verdicts`/`trends` |
| "C1 verified on the graded population", calibration 7→7 | Calibration **improved** — that axis reading stands; the round is **not admitted** (`admitted: false`, `verdict: rejected-harmed`) | filed report "Verdict (author)"; closure `rounds[428]` |
| Grid green (faults 26/26, controls 13/13, contracts 4/4) as no-harm | Insufficient: T01 (blobless partial clone) and F23 (promisor pack without config) were **ungraded** `tradeoff`/`contract` rows, so grid green did not establish no-harm. Closure independently reran T01: frozen exit 0 (correct clean verdict) → current exit 2 `partial clone (promisor pack)`; and on a real promisor-marked clone of the lane, frozen auditor rounds 10-22 exit 0 with the same JSON verdict as current on the full clone, current on the promisor clone exit 2. | closure `harm_ruling`; grid rows `tests/report-audit/repo-state-grid.py:670` (F23), `:689` (T01), ungraded-by-design `:13-14`; auditor refusal sites `tools/report-landing-audit.py:455-457`, `:462-465` |
| Declared claim C1 calibration 7→7 on the lowest non-retired axis | **Unchanged and correct** — the axis choice was right; the harm landed on operability, which the round-23 block disclosed but did not rule on | `SCORECARD.md:1154-1155`; `AXES.md` §Working the axes |

**Count correction — falsify-wave lane reports: 69, not 68.** Observed by
this seat: `.ufo/waves/round-23/falsify/advice/` holds **69** `.md` lane
reports (70 directory entries, the 70th being `swarm-registry.json`).
The literal stale count is `corpus/lessons/round-23.md:178` — "73 seats
dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow, RowF09SignatureProgram,
CritOpenHonesty)" — which is internally inconsistent (73 − 4 = 69). The filed
fleet report does **not** state 68 falsify reports: it gives 73 falsify seats
with 4 dead and a 141-seat round total
(`.ufo/reports/round-23/kama.md:148-155`), i.e. 69 durable reports and 5
seats without a report (build `RevClaimScope` + the 4 dead falsify seats).
Correction location: the lesson line 178, not the filed report. Both files
stay byte-unchanged; this block is the append.
`RowC03FabricatedFull.md` is durable (6618 bytes, 16:10:15Z) although its
session `.md` is empty and its final response aborted at 16:10:50Z
(closure `routed_checks`).

**Identity-evidence correction — the killed-FIFO-process count, and a live
conflict between two glosses.** Both glosses are reproduced verbatim; this
seat does not adjudicate between them, and the L1 owns the final wording.

- Gloss A (preregistration `expected_after[6]`, and `LOG.md:1417-1420` at
  `d1b9d95`): "40 of the 56 killed FIFO-process identities were retained, not
  full identity evidence."
- Gloss B (CritEvidence's retained-transcript reading,
  `.ufo/waves/round-24/build/out/CritEvidence/r23-corrections-append.md`, and
  the `LOG.md` "Round-24 correction provenance refinement" append in the
  working tree): "56 was a matching-process count, while a different listing
  pattern kept 40 truncated identity rows (38 git, gpg-agent, scdaemon), not
  56 identified FIFO-blocked git processes. Only 19 retained rows could be
  linked to FIFO fixtures; 16 counted identities were not retained. The
  matching count became zero after cleanup, but this does not independently
  prove every victim's identity or blocking cause."
- Corrected reading carried by Gloss B (verbatim): "56 round-owned fixture
  processes (git plus at least two gpg daemons) were killed; 40 identities
  retained in the session transcript, only partly shown to be FIFO-blocked."
- Why they differ: the 56 is
  `ps -eo pid,args | grep -E 'repo-state-grid-|/tmp/kama-r23' | grep -v grep | wc -l`
  at 16:33:38Z; the 40 rows come from the *different* pattern
  `'repo-state-grid-|kama-r23|refusal'` with `head -40`
  (`.ufo/waves/round-24/build/out/CritEvidence/provenance.txt`,
  `r23-ps-listing-line156.txt`, transcript sha256
  `114ffef5714e88e39fe4e3b80155d4f9c036dea99634c7ab5099821f9f1860db`).
  37 of the 40 provably match the counting pattern, 3 are truncated before
  the path.
- The filed round-23 statements this corrects are
  `.ufo/reports/round-23/kama.md:34-35` ("56 orphaned FIFO-blocked git
  processes from this round were killed"), `corpus/lessons/round-23.md:109-110`
  and `:174` (M7, "56 blocked `git` processes"). Those bytes stay immutable;
  the correction is appended here.

Both corrections are **status-neutral**: a seat count and an
evidence-completeness statement. Neither changes a verdict, an axis score or
an admission decision.

### Round-24 C1 — preregistered expectations and measurements

Preregistered at `.ufo/waves/round-24/preregistration.json` before
implementation. "Before": r23's blanket refusal returned could-not-evaluate
on complete promisor-marked clean repositories and on genuine-omission
repositories. "After" (preregistered, **not observed**):

1. Complete local promisor-marked lane and fleet clones with valid cited
   commits: exact same substantive clean/failed findings as otherwise
   identical full clones, **not** exit 2.
2. A genuine omitted pre-cutoff lane commit remains landed-omitted exit 1
   with promisor metadata.
3. An unavailable required commit/tree/blob/report object: exit 2
   could-not-evaluate, never a clean or failed verdict.
4. A missing citation in any promisor-backed repository is unknown, not
   proved absent: exit 2 unless resolved locally by another audited
   repository.
5. No lazy network fetching, transport invocation, signature verification,
   replace-ref substitution or config-caused hangs; existing global Git
   isolation and deadlines preserved.
6. Metadata-only declarations do not establish incompleteness; content
   completeness and availability of required evidence determine the outcome.
7. Round-23 filed evidence unchanged; the two corrections above appended.

| C1 component | Preregistered expectation (not observed) | Counting command | Expected exit | Status |
|---|---|---|---|---|
| Promisor-marked completeness (rows 1-4, 6 of `expected_after`) | complete promisor clone → same substantive finding as the full clone; genuine omission → landed-omitted exit 1; unavailable required object → exit 2; unknown citation → exit 2 unless resolved locally | `python3 tests/report-audit/promisor-grid.py --arm both --json` (frozen arm = r23 base) | [INFERENCE — not fixed by the preregistration: the frozen arm is red by design, as in `tests/report-audit/repo-state-grid.py:16-19`, so `--arm both` exits 1] | **UNRUN** — and the named grid file does not exist yet (see gate below) |
| Isolation preserved (row 5) | 0 lazy fetches, 0 transport invocations, 0 signature verifications, 0 replace-ref substitutions, 0 config-caused hangs; global Git isolation and deadlines intact | same command; exec/timeout counters in the JSON | same | **UNRUN** |
| Retained round-23 grid, policy rows restated, non-promisor no-harm | r23 graded rows keep their verdicts except the explicitly documented promisor policy-row expectation changes; non-promisor rows unchanged | `python3 tests/report-audit/repo-state-grid.py --arm both --json` | 1 (frozen red by design) | **UNRUN** |
| Existing selftest | unchanged | `python3 tools/report-landing-audit.py --selftest` | 0 | **UNRUN** |
| Historical parity (rounds 10-22, with and without errata) | current ledger byte-identical to frozen; `--no-errata` still exits 1 with the raw defects | recipe line `nh-history-parity` (`.ufo/waves/round-23/recipe.json`) | 0 | **UNRUN** |
| Mutation sensitivity | every new isolation element killed by a named row; any survivor reported | `python3 tests/report-audit/isolation-mutants.py --json` | 0 | **UNRUN** |

**Gate on the first row.** `tests/report-audit/promisor-grid.py` is the
preregistered counting command and it does not exist at the round base:
`git cat-file -e 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tests/report-audit/promisor-grid.py`
→ `fatal: path 'tests/report-audit/promisor-grid.py' does not exist`, and
the working tree at `d1b9d95` holds only `isolation-mutants.py` and
`repo-state-grid.py` under `tests/report-audit/`. Until round 24 lands that
harness, row 1 is **UNRUN**, not failed; the preregistration's oracle
(fixed expected exits and finding IDs) must be encoded in it before the
measurement can count anything.

### Trend verdicts — round 24

No trend is claimed. Expansion, quality and discernment are **unresolved**
for round 24 at drafting time; the only trend statements that stand are the
round-23 closure's (expansion unchanged, quality **harmed**, discernment
improved). The round-24 trend row may be filled only from the L1's single
post-integration run of the recipe above.

**Planned:** accept or reject the round-23 verdict correction above with the
CritEvidence conflict resolved by the operator; then land the round-24
promisor repair with its grid, run the five measurements once on the
committed tree, and fill this block's table from that receipt. Open channels
carried from round 23 remain debt, not claims resolved: alternates / gitfile
redirect, `--shared`-of-partial bypass, second Landed section, ambiguity
overwrite, errata CR, `--errata` FIFO, memory ceilings, and the unisolated
sibling gates (`citation-provenance.py`, `sources-append-only.py`).
