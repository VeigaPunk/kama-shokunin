# CritScores — r24 axis-claim separability

**Verdict: NOT SEPARABLE AS PREREGISTERED.** The calibration rule in C1
("no guessed absence") and the operability repair the r23 closure asked for
(H1) conflict on the closure's own named witness. H2 (the git floor) is not
addressed at all. On base `0df800e8`, most of what C1 would count is
restoration of r23's self-inflicted harm, not calibration movement. With the
accounting corrections below, **calibration 7 → 7** and **operability 8 → 8**
can be defended. A verdict of "operability harm undone" cannot. No capability
row, no frontier advance, and no scalar increase is supported.

Scope: critic only. I ran no auditor, grid, selftest or suite. I made no
production edits and installed nothing. My probes are git primitives on fresh
synthetic fixtures under `/fast/scratch/hyaku/kama-r24/CritScores`, plus
read-only `cat-file` calls on the real lane and fleet. Script:
`.ufo/waves/round-24/build/out/CritScores/probe.sh`. Outputs:
`.ufo/waves/round-24/build/out/CritScores/observed.txt`. The AuditRepair
scratch at `d1b9d95` had no auditor diff when I checked, so I could not
evaluate a candidate. All candidate behaviour below is derived from the
preregistration wording. Where a claim was not run it is marked [INFERENCE].

## S1 — Calibration and operability cannot both pass the closure's own witness (a tradeoff, not a fixable bug)

**Counterexample.** The closure's non-author real-lane control (from
`out/CritNoTrade/closure-r428.txt` harm_ruling):
- lane: a `--filter=blob:none` file:// clone of the real lane, which is complete but carries promisor metadata;
- fleet: the real fleet;
- rounds 10–22.

Its results: frozen `4fe9339f` gave rc 0, and r23 gave rc 2. Route H1 says to
"restore correct ordinary complete-promisor/filtered-clone cases … do not
silently reclassify them out of no-harm controls".

**Evidence.**
- `tools/report-landing-audit.py:325` runs `lookup()` on every 40-hex token before `apply_errata` (`:387`). The exit code is 0 only if nothing is uncorrected and no errata row is unmatched (`:538`).
- `registry/report-landing-errata.tsv` has a round-20 `unresolved-full-hash` row for token `0957ce619789d13d894ef21bc863486bcb35b56c`. That token is in fleet `HEAD:.ufo/reports/round-20/kama.md` (1 line).
- `cat-file --batch-check` reports the token **missing** in both the real lane and the fleet. Neither repo has local promisor config (observed.txt P3).
- Preregistration `expected_after[3]` says "missing citation in any promisor-backed repository … exit2 unless resolved locally by another audited repository". The token is not resolved anywhere, so the candidate must return exit 2 on that witness [INFERENCE: no candidate exists yet].
- `expected_after[0]` restricts the restoration claim to "valid cited commits". That excludes the witness by construction.

**Why the code cannot fix this.** If the token existed on the promisor remote,
round 20 would have no defect, the errata row would be unmatched, and the exit
would be 1. If the token is absent, the errata row corrects the defect and the
exit is 0. Which one applies cannot be known without a lazy fetch, so exit 2 is
the honest calibration answer. That answer still loses a previously correct
rc 0 verdict, which is exactly how the closure defines operability harm. The
other way out is to treat the errata row as proof of absence, which would be a
calibration regression.

**Impacted axes:** operability (H1 still harmed on this witness); calibration
(if the candidate passes the witness, it guessed absence).

**Smallest safe correction:**
1. Add a synthetic graded no-harm row: a complete promisor-metadata lane, a report citing an errata-corrected spliced full hash, run with errata. Expect exit 2.
2. In the author verdict, record operability as **"H1 partially repaired; residual harm on the closure witness (rc 0 at `4fe9339f` → rc 2)"**.
3. Route the trade to the operator, as H1's alternative allows.

Do not let `expected_after[0]`'s "valid cited commits" wording act as a
reclassification.

## S2 — H2 (git ≥ 2.45 floor) is outside the claim and stays harmed

- `tools/report-landing-audit.py:55` ("git >= 2.45 is required") and `:92-93` (`--no-lazy-fetch` in `GIT_ISOLATION`) are both kept by the preregistration ("preserve … --no-lazy-fetch").
- The closure, route H2, says the floor must be an operator-approved prerequisite, "not an unchanged axis".

**Impacted axis:** operability.

**Correction:** add no code. State in SCORECARD that H2 is unchanged and
awaits an operator ruling. Without that ruling the round cannot report
operability as no-harm.

## S3 — A full-closure check over-refuses, and the existing fixtures cannot detect it

**What is prescribed.** The AuditRepair prompt (spec.json) specifies
`git rev-list --objects --missing=print --no-object-names` on the pinned
commit roots.

**What the probe found (observed.txt P1).** I built a 3-commit lane that
rewrites `f`, then made a blobless clone of it with `allowFilter`:
- The full closure prints two `?` lines. These are historical blobs that no audit step reads.
- Every read the auditor actually makes returns rc 0 with lazy fetch disabled: commit-only `log`, `ls-tree` of the tip, `cat-file` of the tip blob, and `log --diff-filter=A -- f`.
- `--filter=blob:none` closure shows nothing missing.
- No fetch occurred.

**Missing required objects already fail closed (P2, P4).** A missing commit
makes `log` fail with "Failed to traverse parents", rc 128. A missing tree
makes the path-limited log fail with "unable to read tree", rc 128. A missing
subtree makes `ls-tree -r HEAD -- .ufo/reports` fail with "Could not read",
rc 1. `git()` turns all three into EvalError, so exit 2. The only channel where absence becomes data is
`cat-file --batch-check` inside `lookup()` (`:139-176`).

**Why the grid cannot tell the designs apart.**
- r23 T01 builds a single commit with `base()` (`tests/report-audit/repo-state-grid.py:113-118`, `:596-602`).
- `out/CaseHydratedLane/hydrated_lane_case.py:108-109` adds `f` and then `g`, so the HEAD tree holds every blob.
- Both are fully hydrated at checkout, so a design that demands the full closure passes them.

**Impacted axes:** operability (the realistic blobless clone from a filtering
server still refuses, where `4fe9339f` gave a verdict [INFERENCE: not run]);
calibration credit (rows pass even for an over-refusing design).

**Correction (pick one):**
- Define required evidence as commits plus trees (rely on fail-closed `git()` reads, or use `rev-list --filter=blob:none`), plus the blobs actually read: tip SOURCES, tip ERRATA and fleet HEAD reports.
- Or keep the full closure and record "blobless clone with unhydrated history" as a residual refusal.

Either way, add one graded row in which a historical blob of a rewritten path is missing.

## S4 — Against base `0df800e8`, most of the delta is restoration; split the rows before counting

The frozen arm is the harmed r23 state. That state refuses every config- or
paired-pack-promisor repo (`:450-465`), so every "complete promisor → correct
verdict" row reads as a win. Grid rows should be classified like this:

| Class | Definition | Credit |
|---|---|---|
| R: restore | `0df800e` exit 2, `4fe9339f` correct | 0. Operability verdict "repaired to the pre-r23 verdict" |
| C: calibration | both `4fe9339f` and `0df800e` guessed absence, current exit 2 | C1's counted calibration delta |
| U: unchanged | same exit and reason, or reason wording only | no-harm |

Against this base, the only C-class shape I can find is the filter-only
promisor with an unknown citation: r23 F27, now `exit1 → exit2`.
- `promisor_remote_config` creates a promisor remote from `partialclonefilter` alone (`out/SrcPromisorCode/evidence.md`, git v2.56.0 `promisor-remote.c:148-163`).
- r23 does not refuse filter-only remotes (`:462-464`).
- Its grid pins exit 1 (`repo-state-grid.py:674-675`; `.ufo/waves/round-23/final/grid-both.json` current F27 exit 1).

Other unknown-citation rows were already exit 2 in r23 because the whole repo
was refused. They are U-class with a changed reason, not credit.

**Relabels in the retained r23 grid must be reported as relabels, not gains.**
Population `f29fab8d…364a` will change.
- T01: `tradeoff` → graded control exit 0. Controls go 13 → 14. This is required by the closure, not a new win.
- F27: fault exp 1 → contract exp 2. Faults go 26 → 25, contracts 4 → 5.
- F23: stays exit 2. Its pinned reason `"promisor pack"` (`:704`) becomes the unknown-citation wording.
- F06: stays exit 2. Its reason `"partial clone"` (`:697`) changes.

F23 is **not** an operability repair. Its r23 trade (`SCORECARD.md:1170-1173`)
is kept and re-justified as honest uncertainty. That is a reclassification of
a declared trade, so it must be stated explicitly and named in the operator
route.

**Measurement safety.** Do not run `4fe9339f` (no `--no-lazy-fetch`) on
fixtures that have missing lookups and a reachable file:// origin. Doing so
would invoke a lazy-fetch transport. Take the pre-r23 reference from the
retained r23 frozen column (T01 exit 0 at `4fe9339f` in `grid-both.json`), or
from the preregistered expected outcomes.

## S5 — The bookkeeping errata are separable from C1 and are not credit

The corrections "69 not 68" and "40 of 56 identities" are already appended at
`LOG.md` round-24 section (commit `d1b9d95`; the `40 of the 56` line is
`LOG.md:1419`). That commit touches only `preregistration.json` and `LOG.md`,
so the code base remains `0df800e8`. These corrections stand without any code
change. Following the precedent at `SCORECARD.md:1012` ("bookkeeping, not the
credited move"), they must not appear in C1's before → after count.

## Required SCORECARD shape (draft guidance for ScribeScorecard and L1)

- C1 **calibration 7 → 7**. Count only C-class rows, plus no-harm on U and R.
- **operability 8 → 8**, verdict **"partially repaired"**:
  - repaired on complete config- or paired-marker promisor clones with resolvable citations;
  - residual harm on S1's witness;
  - H2 unchanged;
  - S3 scope stated.
- Admission is subject to an operator ruling on S1 and H2.
- No capability row. No frontier advance. The quality trend must not read "improved" while any operability harm remains.

## Records

- Installs/updates: none.
- Scratch: `/fast/scratch/hyaku/kama-r24/CritScores` (synthetic fixtures `lane`, `clone`, `loose`, `loose-objects-backup`, `lstree`). No `/tmp` use. No fleet, sibling or lane-index writes.
- Unverified: candidate behaviour (no candidate diff existed); `4fe9339f` verdict on the multi-commit blobless shape.
