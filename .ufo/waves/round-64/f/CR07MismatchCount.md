# CR07MismatchCount — C2 calibration count: what the round-64 C2 instrument actually counts

Seat: CR07MismatchCount (leaf critic, wave f, round 64 kama). Milestone: calibration counting. Judged on: calibration.
Base `0c1eff3cb9ac4c11402ab0124c35842f06a436fc`, freeze `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`,
measured tip `23b3fdb1a925129a9961cf551f6d40bf251602cb`. Scratch `S=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount`
(clone at `$S/clone`, `--shared` clone of the lane, tip checked out; every edit and every mutant commit was made in
the clone only; the lane was never written, never committed, never `git add`ed).
Tools installed: none (stdlib `python3`, `git`, `pgrep`, `bash` only). No pacman.

## 1. The counter's own mismatch fields, at both tips

Run with the frozen recipe (`python3 tools/round64-c2-counter.py --repo <clone> --tip <rev> --work <fresh>`;
receipts `out/CR07MismatchCount/c2-base.out`, `c2-tip.out`):

```
BASE  0c1eff3cb9ac4c11402ab0124c35842f06a436fc  exit 1
tip=0c1eff3cb9ac4c11402ab0124c35842f06a436fc population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 met=False

TIP   23b3fdb1a925129a9961cf551f6d40bf251602cb  exit 0
tip=23b3fdb1a925129a9961cf551f6d40bf251602cb population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True
```

Both base and tip receipts match the lane's committed receipts byte-for-byte on the counter line
(`.ufo/waves/round-64/controls/c2-base.txt`, `c2-prewave-tip.txt`), so the instrument reproduces.

### The mismatch count, computed the way the counters print it

The three fields the item names are **not** one number, and they are not the same quantity:

| field | base `0c1eff3c` | tip `23b3fdb1` | what it counts |
|---|---|---|---|
| `mismatches=` | **0** | **0** | registry-row mismatches only: a bound row whose live outcome is undeclared, or whose recorded `observed` text ≠ the pattern the live run produced (`score()` in `tools/round64-c2-counter.py`, lines 536–597). It says nothing about the SCORECARD/SHONEN prose. |
| `recon_mismatches=` | **0** | **0** | the reconciler's own count, `tools/round42-selfdesc-reconcile.py` `evaluate()`: `r41+banner+planned+retired+saturation+caps+receipts+readme+province+rel+(1-closure_ptr)`. |
| `tally_disclosed=` | **1/8** | **8/8** | rounds 56–63 whose `shortcut-tally` status is neither `no-disclosure` nor `unreadable:*`. |
| `closure_ptr=` | 0 | 1 | the calibration row's `latest outside closure` pointer == newest `corpus/lessons/round-N-verifier-spotcheck.md` at the tip. |

**The mismatch count at the base tip is 0 and at the tip is 0.** That is the answer to "compute the mismatch count":
the counter's *own* mismatch counter reads 0 in both trees, and the two trees differ on nine other fields.
The base tip's real calibration defect — the calibration row pointed at round 57 while the newest closure was
round 63 — is caught by `closure_ptr=0`, **not** by `mismatches` or `recon_mismatches`. I confirmed this by hand:
the tip's reconciler run directly against the base tip prints
`r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=0 mismatches=1 maxN=63 met=False`
with `detail: closure_ptr: calibration row latest outside closure is round-57; newest at tip is round-63`.
So `recon_mismatches=0` at the base tip is **not** evidence that the base tree was calibrated — it is the counter
reading a *different* reconciler (the base's own, which lacks the `closure_ptr` conjunct) and getting a clean
bill. The base's own reconciler at the base tip prints `mismatches=0 maxN=63 met=True`. The instrument's
`closure_ptr` conjunct is the only thing that sees the base's staleness.

### `controls_rejected=120/120` measures the counter, not the calibration

`controls_rejected` is the count of the counter's **own 120 planted control mutations** that its own scoring
functions reject. It is a self-test of the instrument. It is credited only while the unmutated baseline is met
(`controls_rejected=0/120` at the base tip, stderr: `note: baseline not met - control credit withheld`), so at
120/120 it asserts "the counter rejects every defect it was told to reject", not "the lane is calibrated".
It is orthogonal to the calibration axis: the counter's own `mismatches`/`recon_mismatches` are 0/0 in the very
tree where the calibration pointer was stale.

## 2. Every calibration self-assessment the lane makes, and whether it is read

The lane's calibration self-description lives in four places. I checked each against the code and then attacked
each with a tip mutant scored by the **unmutated** counter (committed in the clone, `git commit` as `seat`, run
`cd clone/tools && python3 round64-c2-counter.py --repo clone --tip <mutant> --work <fresh>`).

### (a) SCORECARD `## Axes` calibration row (`SCORECARD.md:18`)

The row carries: score `**7**`; three `run` facts (`tools/capability-repertoire-audit.py --selftest` →
`CAP_SELFTEST pass=2 fail=0`; a `glob` one-liner → `verifier-spotcheck population present` (exit 0);
`tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0`); five path tokens; the closure
pointer `corpus/lessons/round-63-verifier-spotcheck.md` + `including round 63`; and two numeric self-claims —
`registry/verdict-ledger.tsv` (204 rows, `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`) and
`registry/claim-outcome-ledger.tsv` (126 rows, `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`).

**Read and observed:**
- score `7` — `round41-scorecard-reconcile.py` compares it to a frozen `EXPECTED` vector (not to repo state).
- the three run facts — the r41 reconciler executes them in a throwaway export of the tip and compares stdout
  (`RUN_RE`), so a falsified expectation **is** caught (mutant M11 below: KILLED).
- the five path tokens — the r41 `PATH` fact requires each to exist at the tip (so a *deleted* file is caught).
- the closure pointer and `including round 63` — the `closure_ptr` conjunct (M5: KILLED).
- the first-working-round column of the canonical list — the reconciler's `saturation` conjunct requires the
  stated `first-working rounds …` list to equal the canonical list's (M6: KILLED).

**Never read (not one instrument looks at them):**
- **the two numeric ledger self-claims** — `204 rows`/`126 rows` and both `agreement=…` blocks. Nothing in
  `tools/round64-c2-counter.py`, `tools/round42-selfdesc-reconcile.py`, `tools/round41-scorecard-reconcile.py`
  or `tools/shortcut-tally.py` mentions `verdict-ledger` or `claim-outcome-ledger` (`grep` over all four: no
  hits). The lane's own `tools/round44-verdict-ledger-audit.py` and `tools/round45-claim-outcome-audit-v2.py`
  derive those figures; they are in no pin table and no registry row. Mutant M2 falsified both blocks and both
  row counts to flattering values — **SURVIVED**.
  (I recomputed both ledgers by hand at the tip, using each audit tool's own documented comparison rule:
  verdict-ledger `agree=69 overclaim=2 underclaim=16 other=0 absent=15` and claim-outcome
  `agree=58 overclaim=1 underclaim=2 other=1 absent=1` — receipt
  `out/CR07MismatchCount/ledger-figures-recomputed.txt`. So the *stated* figures happen to be true at the tip.
  The gap is that the C2 instrument cannot tell, and the row is what the axis treats as the lane's
  calibration claim.)
- **the closure verdict word** — `(rejected-honest-stop)` next to the pointer. Mutant M10 rewrote it to
  `(admitted-clean, all claims verified)`: **SURVIVED** (`closure_ptr=1`, because the conjunct checks the round
  number and the `including round` clause, never the verdict text). The lesson file itself says
  `**Verdict: rejected-honest-stop, admitted=false, status ok**` (`corpus/lessons/round-63-verifier-spotcheck.md`),
  so the word is a self-assessment about the outside closure that the instrument never reads.
- **the named deriver** — the row says the population and pointer "are derived at the measured tip by
  `python3 tools/round59-c2-counter.py --repo <repo> --tip <rev> --fleet-ref HEAD`". That counter is a *path
  token* to the r41 reconciler, so its existence is checked, but it is never executed and never pinned.
  Mutant M8 deleted `tools/round59-c2-counter.py` outright: **SURVIVED** (`pinned=13/13` — it is not in the pin
  table).

### (b) SCORECARD §Round-63 `What met=True does not show` (`SCORECARD.md:3346`)

The round-63 disclosure paragraph is read by **nothing** in the C2 chain:
- the counter greps SCORECARD only for the calibration row (`calibration_row`) and the canonical list
  (`canonical_rows`); `grep -n "Round 63" tools/round64-c2-counter.py` → no hits.
- the reconciler reads the head, `## Axes`, `## Planned`, `## Retired`, `## Saturation`, `## Capabilities`,
  the `## Round 40/41` receipt sections (`RECEIPT_ROUNDS = (40, 41)`), README and PROVINCE — the round-63
  section is none of those.
- `shortcut-tally.py` reads the round-63 section only to classify its *status*; it never compares the paragraph
  against repo state.

Mutant M4 deleted the entire round-63 `What met=True does not show` paragraph: **SURVIVED** with `met=True`
— and the only visible effect was that round 63's tally status flipped from `ok` to
`disclosed:shortcut+survivor` (the v3 statement reader picked up other text). The counter still prints
`tally_disclosed=8/8`. So the round's own limits paragraph can be deleted and the calibration claim still holds.
Note this is *not* a round-64 disclosure gap: the round-64 section at the tip has no
`What met=True does not show` block at all (only `## Round 64`, the canonical list, `### Planned (round 65)`),
and `shortcut-tally.py --rounds 56-63` does not read round 64 anyway — the frozen range stops at 63.

### (c) SHONEN.md boxes (4 boxes, all `- [~]`)

SHONEN.md is **never opened** by any of the four C2-chain tools: `grep -c SHONEN` returns 0 for
`round64-c2-counter.py`, `round42-selfdesc-reconcile.py`, `round41-scorecard-reconcile.py` and
`shortcut-tally.py`. Only `tools/round53-cited-path-check.py` and `tools/round54-cited-path-check.py` read it,
and neither is pinned or bound by the C2 registry. Yet AXES.md:15 names it as the calibration signal:
*"SHONEN.md/SCORECARD entries match observed repo state"*, and the fleet `CORPUS`/`AXES` contract is what makes
this item's mismatch count meaningful.

- Mutant M1 flipped all four boxes `[~]` → `[x]` and rewrote every `→ Author assertion:` into
  `→ Verified by the non-author closure spot-check:` — a false non-author-verification claim on a file that
  says in the same line "no named non-author verifier": **SURVIVED** (`met=True`, `controls_rejected=120/120`).
- Mutant M9 deleted `SHONEN.md` outright: **SURVIVED** (`met=True`).

This is the sharpest finding: the file AXES.md names as *the* calibration surface can be deleted from the tip
and the C2 calibration claim is still met.

### (d) Capability rows (the 12 canonical rows of §Round 64)

The rows' `| Capability | What it can now do | Evidence pointer | First-working round |` cells:
- the **slug and the 48-char prefix** are graded (`canon_problems` requires each row's text to start with the
  counter's own frozen prefix);
- the **evidence pointer** is graded only indirectly — the reconciler's `province` conjunct requires each
  `tools/`/`registry/` token in a canon row's evidence cell to appear in PROVINCE.md; there is no existence
  check on the pointer itself. Mutant M3 repointed `live-llamacpp-lifecycle`'s evidence at
  `.ufo/waves/round-16/live/receipt-DOES-NOT-EXIST.json`: **SURVIVED**. (The `.ufo/` token is outside the
  `province` clause's `tools/`/`registry/` filter, so nothing checked it.)
- the **description beyond the 48-char prefix** is not graded at all. Mutant M7 rewrote `live-llamacpp-lifecycle`'s
  description to claim "score consumer health with 99.9% uptime SLA compliance" — a claim the lane's own
  operability axis explicitly disclaims ("not consumer health"): **SURVIVED**.
- the **first-working round** *is* graded (M6 KILLED), via the reconciler's `saturation` conjunct.

## 3. Mutant table (tip mutants, scored by the unmutated counter)

`KILLED` = the pair prints `met=False` (exit 1); `SURVIVED` = the pair prints `met=True` (exit 0).
One-line output pasted in the report; full receipts under `out/CR07MismatchCount/mut-*.out`.

| id | mutant | verdict | field that moved |
|---|---|---|---|
| M1 | SHONEN.md four boxes `[~]`→`[x]`, author assertions rewritten as a claimed non-author verification | **SURVIVED** | none (`met=True`, `controls_rejected=120/120`) |
| M2 | calibration row's two `agreement=…` blocks and both row counts falsified | **SURVIVED** | none (`mismatches=0`, `recon_mismatches=0`) |
| M3 | round-64 canon row evidence pointer → nonexistent file | **SURVIVED** | none |
| M4 | round-63 `What met=True does not show` paragraph deleted | **SURVIVED** | only round-63 tally status `ok`→`disclosed:shortcut+survivor`; `tally_disclosed` stayed 8/8 |
| M5 | *positive control* calibration row closure pointer rolled back to round-57 | **KILLED** | `closure_ptr=0`, `recon_mismatches=1`, `met=False` |
| M6 | *positive control* round-64 canon row `sources-registry` first-working round 10→3 | **KILLED** | `recon_mismatches=1`, `met=False` |
| M7 | round-64 canon row description falsified beyond the 48-char prefix | **SURVIVED** | none |
| M8 | `tools/round59-c2-counter.py` (the row's named deriver) deleted | **SURVIVED** | `pinned=13/13` (not in the pin table) |
| M9 | `SHONEN.md` deleted from the tip | **SURVIVED** | none |
| M10 | calibration row's closure verdict word `rejected-honest-stop`→`admitted-clean, all claims verified` | **SURVIVED** | `closure_ptr=1` (the conjunct checks the round number only) |
| M11 | *positive control* calibration row's `CAP_SELFTEST pass=2 fail=0` expectation falsified | **KILLED** | `recon_mismatches=1`, `met=False` |
| M12 | tip's **unpinned** `tools/shortcut-tally.py` made to report every round as disclosed | **KILLED** | `tally_selftest=0`, `met=False` (the counter's own fixture caught the hollow tally) |
| M13 | tip's `tools/capability-repertoire-audit.py` replaced by a **printer** of the calibration row's run-fact pattern | **SURVIVED** | none (`met=True`) — the tool is unpinned and outside the 12-row registry, so the printer family never sees it |

M5, M6 and M11 are positive controls: they prove the instrument *does* reach the closure pointer, the
first-working-round column and the run-fact expectations — so the survivals above are holes in coverage, not a
blind counter. M13 is the most pointed: the counter's own printer family proves that a *bound* tool cannot
merely print its pattern, yet the calibration row's own run fact is executed by a tool that is neither pinned nor
in the registry, so a printer of `CAP_SELFTEST pass=2 fail=0` satisfies it and the counter stays `met=True`.

## 4. Answer to the three questions the item poses

1. **Mismatch count at the base tip and at the tip, with the counters' own commands.** Base `0c1eff3c`:
   `mismatches=0`, `recon_mismatches=0`, `tally_disclosed=1/8`, `closure_ptr=0`, `met=False` (exit 1).
   Tip `23b3fdb1`: `mismatches=0`, `recon_mismatches=0`, `tally_disclosed=8/8`, `closure_ptr=1`, `met=True`
   (exit 0). The printed `mismatches`/`recon_mismatches` are 0 in both trees; the base tree's genuine calibration
   defect (pointer round-57 vs newest round-63) is visible only as `closure_ptr=0`, and only when the *tip's*
   reconciler is used — the base's own reconciler reports `mismatches=0 met=True` on that same tree.
2. **Is `controls_rejected=120/120` a measure of calibration or of the counter?** Of the counter. It is the
   counter's own 120 planted defects, each scored by the counter's own functions, credited only while the
   unmutated baseline is met (0/120 at the base tip). It is a self-test of the instrument, and it is 120/120 in
   trees whose calibration self-description is demonstrably false (M1, M2, M3, M4, M7, M8, M9, M10, M13).
3. **What does a do-nothing control score on each field?** The base tip is the do-nothing control and its line is
   the BASE line in §1: `population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2
   regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0
   recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2
   met=False`. The instructive part: the two fields a reader would take for the calibration mismatch count
   (`mismatches`, `recon_mismatches`) read **0** on the do-nothing tree, and `sens_selftest=4/4` and
   `work_reuse_refused=1` read *passing* on it — those are properties of the counter, not of the tree. The
   fields that actually discriminate the do-nothing tree are `population`/`covered` (0/12), `pinned` (12/13),
   `regress_flipped`/`printers_rejected` (0/12), `idle_ok` (0), `closure_ptr` (0), `tally_disclosed` (1/8),
   `tally_selftest` (0) and `errors` (2).

## 5. Impacted axis and the smallest safe correction

Impacted axis: **calibration** (the counter proves the 12 *capability* rows were executed; it does not measure
whether the lane's *self-description* matches the repo — which is what AXES.md:15 asks of this axis).
Impacted claims: C2 only. C1 is untouched by every mutant here.

Smallest safe correction, in decreasing value per line changed, all inside the C2 instrument (no lane-file edits):
1. **Pin and close the two calibration surfaces the axis names.** Add `SHONEN.md` to the counter's inputs and
   require each of its four boxes to carry a state the counter can check (e.g. `[~]` boxes must name the
   open item they assert, and an `[x]` box must cite a non-author verifier that exists at the tip). Today
   M1/M9 pass with the file deleted.
2. **Read the two numeric ledger self-claims.** Either add `registry/verdict-ledger.tsv` and
   `registry/claim-outcome-ledger.tsv` to the reconciler's facts (the lane already has the two audit tools that
   derive them) or drop the figures from the calibration row. Today they are decoration: M2 passes.
3. **Read the closure verdict word.** Widen the `closure_ptr` conjunct to the lesson's `Verdict:` line so
   `rejected-honest-stop` vs `admitted-clean` is graded (M10 passes today).
4. **Pin the tools the calibration row itself names and executes** — `tools/capability-repertoire-audit.py`,
   `tools/instrument-agreement.py` (already pinned), and the row's named deriver `tools/round59-c2-counter.py` —
   and extend the printer family to them, so M8 and M13 die. This is the same treatment the 12 registry rows
   already get.
5. **Grade the canonical rows' evidence pointers for existence** (M3 passes today), and grade the *whole*
   description cell rather than a 48-char prefix (M7 passes today).
6. **Report the mismatch count under a name that says what it is.** `mismatches` currently means "registry rows
   whose live outcome disagreed"; the axis's number lives in `recon_mismatches` and `closure_ptr`. Printing
   `selfdesc_mismatches=` (the reconciler's total) beside the registry count — and printing it at the base tip
   from the *tip's* reconciler, which is what shows the base's staleness — would make the base→tip delta legible
   in one line.

None of these is required for the counter's own `met=True` to be honest about what it proves: the counter does
prove the 12 registry rows were executed rather than printed (M5/M6/M11/M12 killed show the instrument has
teeth where it is aimed). The gap is between that and the axis's stated signal.

## 6. Reproduction

```
S=/fast/scratch/hyaku/kama-r64/f/CR07MismatchCount; D=$S/clone
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $D
git -C $D checkout -q 23b3fdb1a925129a9961cf551f6d40bf251602cb
# base and tip receipts (mutant scripts + runner in out/CR07MismatchCount/)
(cd $D/tools && python3 round64-c2-counter.py --repo $D --tip 0c1eff3cb9ac4c11402ab0124c35842f06a436fc --work $S/work-base)
(cd $D/tools && python3 round64-c2-counter.py --repo $D --tip 23b3fdb1a925129a9961cf551f6d40bf251602cb --work $S/work-tip)
# one mutant: edit in $D, commit, score with the unmutated counter from $D/tools
```

Evidence files: `.ufo/waves/round-64/f/out/CR07MismatchCount/` — `c2-base.out`/`.err`, `c2-tip.out`/`.err`,
`mut-*.out` for all 13 mutants, `mut_*.py` and `mutants*.sh` (the mutant generators and runner), and
`ledger_check.py` (my independent recomputation of the two ledger figure sets). The scratch root is removed
before yield; the receipts are copied into the out dir first.

```
tip=23b3fdb1a925129a9961cf551f6d40bf251602cb population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True
```
