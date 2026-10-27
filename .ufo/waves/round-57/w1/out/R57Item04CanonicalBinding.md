# R57Item04CanonicalBinding — content-bound canonical capability-row audit + omission control

Seat: `R57Item04CanonicalBinding` (scribe), kama round 57, wave `kama-r57-w1`.
Axes: calibration + operability. Bounded leaf; no subagent dispatch.
Role of this file: seat report. Distinct-case evidence is separate
(`.ufo/waves/round-57/reports/R57Item04CanonicalBinding-case25.md`).

## Behavior delivered

An independent (no lane-counter import) prototype that audits the lane's
canonical capability table by **content at a revision**, not by a count or an
instrument's self-description, plus a differential omission control.

- `canon-row-audit.py --repo <lane> --tip <commit> [--scorecard <file>]
  [--rows-file <json>] [--out <receipt>]`
  - derives the table from the single highest-numbered
    `**Capabilities — canonical list as of round N**` heading at the tip;
  - `bind`: every backticked path token in a row's evidence cell must resolve at
    the tip (`git cat-file -e`);
  - `rounds`: the row's first-working round must be ≤ N and a matching
    `## Round <n>` heading must exist;
  - `mirror`: name **and** first-working round **and** the `what` text must match
    the `## Capabilities` head mirror, in both directions;
  - `distinct`: row names unique, whole-row content digests unique;
  - `omitted` / `extra`: symmetric difference between the supplied row set and
    the derived canonical set;
  - `canonical_reads`: rows actually hashed and bound — a `met=True` with
    `canonical_reads=0` is vacuously green and is rejected by the harness;
  - every row emitted as a content address `row <name> sha=<16 hex>`.
  - exit 0 met, 1 not met, 2 could not evaluate (fail closed on missing
    canonical heading or missing mirror table).
- `noop-omission-control.py`: reads nothing, prints
  `canonical_reads=0 ... met=True`, exit 0 (the frozen-style do-nothing control).
- `omission-harness.py`: runs baseline + 5 injections; a control passes only when
  the audit's exit code and `met=` agree with the injection.

## Evidence, exact commands and exits

All receipts under
`.ufo/waves/round-57/w1/out/R57Item04CanonicalBinding/`. Tips are immutable git
commits; `HEAD` was `7b74e2f2515a6f598918488fa5144658ff29925f` when the receipt
set was regenerated (an earlier pass ran at `7c873d7b4e3839489a93d6334cdf93fe5d34d19f`,
same verdicts).

```
$ python3 canon-row-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip HEAD --out baseline.out
tip=7b74e2f2515a6f598918488fa5144658ff29925f
canon=round49@2844 rows=11 mirror=11 supplied=11
bind=11 canonical_reads=11 omitted=0 extra=0 distinct=0 mismatches=0 met=True
row sources-registry sha=647d88ead2530b9d first=10 bind=ok
row ollama-offline-evidence-replay sha=809951d6c28233e8 first=14 bind=ok
row live-llamacpp-lifecycle sha=cdb724ad36b8b3d7 first=16 bind=ok
row gguf-declared-identity-replay sha=3701c7fa245bc7ec first=20 bind=ok
row context-capacity-receipt sha=3c91cbe06a0eaf17 first=25 bind=ok
row instrument-agreement sha=0e2ce2c3e5ca2bf0 first=30 bind=ok
row pin-watch sha=7d9c83320b5cde45 first=41 bind=ok
row digest-ledger sha=4d1f3549e1526eb8 first=42 bind=ok
row hexrun-census sha=a6bebc4a071ebd74 first=43 bind=ok
row append-only-audit sha=548c757ebdfe9994 first=46 bind=ok
row live-receipt-replay sha=47c9bdc5e5cf5192 first=47 bind=ok
exit=0
```

```
$ python3 omission-harness.py
control=baseline     met=True exit=0 bound=11                                   verdict=PASS
control=noop         met=True exit=0 canonical_reads=0                          verdict=PASS(rejected)
control=drop-one     met=False exit=1 omitted=1                                 verdict=PASS
control=drop-all     met=False exit=1 omitted=11                                verdict=PASS
control=bad-evidence met=False exit=1 bind=10                                   verdict=PASS
control=bad-round    met=False exit=1 bind=10                                   verdict=PASS
summary canon=round49 rows=11 controls=6 failed=0 met=True
exit=0
```

`drop-one` removes `append-only-audit`; `drop-all` supplies `[]`; `bad-evidence`
points `digest-ledger` at `tools/does-not-exist-r57.py`; `bad-round` sets
`pin-watch` first-working to `99`. Each injection is caught, and each injection
is also the shape a do-nothing instrument takes.

Cross-check of the frozen C1 calibration figure, derived independently of the
lane counters (`c1-crosscheck.out`):

```
commit       rounds  maxRoundHeading  canonRound  canonRows  mirrorRows
b89bdab2     57              56          49         11          11
89dc4f52     57              56          49         11          11
7c873d7b     57              56          49         11          11
7b74e2f2     57              56          49         11          11
worktree     58              57          49         11          11
```

## Gates

- read-only: the audit's only write path is the optional `--out` receipt
  (`readonly-proof.out`); all lane reads are `git cat-file -p/-e` and
  `git rev-parse`; no `git commit|push|jj`, no index or ref writes.
- fail-closed: exit 2 on a missing canonical heading or missing mirror table;
  never a vacuous 0.
- determinism: same bytes → same row digests and same summary line; the passes at
  `7c873d7b` and `7b74e2f2` produced identical row digests and identical
  `canon=`/`bind=`/`omitted=`/`mismatches=` fields, differing only in `tip=`.

## Touched surfaces

Written (all inside the designated wave report area, nothing else):

- `.ufo/waves/round-57/w1/out/R57Item04CanonicalBinding/` (tools + receipts)
- `.ufo/waves/round-57/w1/out/R57Item04CanonicalBinding.md` (this report)
- `.ufo/waves/round-57/reports/R57Item04CanonicalBinding-case25.md` (case 25)
- scratch `/fast/scratch/hyaku/kama-r57/R57Item04CanonicalBinding/` (transient;
  receipts copied to the wave path first, then the scratch tree was removed)

Not written: any tracked lane file, `tools/`, `corpus/`, `registry/`, fleet root,
sibling repos, `~/.local/bin`, PATH. No tool install or update was needed, so there
is no channel/version/reason to record.

## Findings

1. **Calibration — the frozen C1 figure "expected 46" re-derives nowhere in the
   tree.** Across `b89bdab2`, `89dc4f52`, `7c873d7b`, `7b74e2f2` the greatest
   `## Round <n>` heading is 56 and the highest canonical table is round 49 with
   **11** rows. The only 46 in the frozen control set is the typed string in
   `controls/c1-noop.py:3` (`print("mismatches=0 maxN=46 met=True")`), i.e. the
   do-nothing instrument's constant. Reported verbatim for the canonical judge;
   this seat does not resolve C1.
2. **Calibration — canonical row count is 11 at every audited revision**, and
   canonical and mirror agree name-for-name with identical `what` text. No stale
   row count is observable from the content side at these commits.
3. **Calibration — content binding catches what a count cannot.** On the frozen
   `controls/no-canonical/SCORECARD.md` (round-49 canonical block removed, mirror
   kept) the audit falls back to round 48 and reports
   `bind=9 mismatches=2 met=False`, because the round-48 canonical `what` text of
   `append-only-audit` (first 46) and `live-receipt-replay` (first 47) differs
   from the round-49 mirror text. A name/count counter is blind to this.
4. **Operability — omission is differentially detected.** The do-nothing control
   (`canonical_reads=0 met=True exit 0`) is rejected by construction; dropping one
   real row yields `omitted=1 met=False exit 1`; dropping all yields
   `omitted=11`; a broken evidence pointer and an unevidenced first-working round
   each cost exactly one bound row.
5. **Observed external change, not mine.** During this seat the lane gained commit
   `7b74e2f2` ("round-57: bind prereg roster to executed calls") and the worktree
   `SCORECARD.md` carries an uncommitted `+11` lines with a
   `## Round 57 — no-op control and stale calibration census` heading at line
   3149 (another seat's write; `git status` shows ` M SCORECARD.md`). The audit
   reads at commits, so its receipts are unaffected; the worktree line moves the
   max heading to 57.

## Advisories (non-author duties — this seat is a lane author, so advise only)

- **SOURCES S515 spot-check (non-author, required this round).** `corpus/SOURCES.md:268`
  carries S515 for `git-config(1)` environment pairs
  (`https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`),
  tier `B`, status `mined`, recheck `180d`, lesson `corpus/lessons/round-56.md`,
  and an 18-word quote: "all environment pairs GIT_CONFIG_KEY_<n> and
  GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime
  configuration". A non-author must re-open the URL this round and report the
  located quote at ≤25 words. This seat did not open the URL and does not assert
  the quote is currently locatable. A lane snapshot exists at
  `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` (830605 bytes,
  15:07) from another seat; its contents were not verified here.
- **Admit/reject spot-check (non-author, required).** One decision from the
  round-56 admit/reject record must be re-derived by a non-author; this seat is a
  lane author and does not perform it.
- **Round-56 outside defects.** Both `corpus/lessons/round-56.md` and
  `corpus/lessons/round-56-verifier-spotcheck.md` exist; the lesson author should
  confirm each outside defect is addressed in the lesson text before the round
  closes. Not judged here.
- **Proposal 3 of `considerthese/2026-10-26`** (self-description counter shortcut
  tally) is the proposal this round opens; the audit above is a content-side
  instrument for that tally, not a decision on it.

## Out of scope / known limits

- Repairing C1 (`tools/round42-selfdesc-reconcile.py`) or C2 — other seats own
  those; nothing outside this seat's scratch and report paths was edited.
- The audit does not judge whether a row's `what` claim is *true*; it binds the
  claim to committed evidence paths, the round heading, and the mirror.
- Table parsing assumes the four-column capability layout and a contiguous table
  run; a row split across lines would be missed (none observed at the audited
  revisions).
- Row digests are content addresses truncated to 16 hex, sufficient for
  distinctness here, not a cryptographic commitment.
- `--scorecard` (on-disk override) is used only for the frozen control trees and
  the mutation runs; it is not used for the lane baseline.

## Artifacts

`.ufo/waves/round-57/w1/out/R57Item04CanonicalBinding/`:
`canon-row-audit.py`, `omission-harness.py`, `noop-omission-control.py`,
`distinct-case-25.py`, `baseline.out`, `baseline-run.txt`, `harness.out`,
`case25.out`, `c1-crosscheck.out`, `readonly-proof.out`, `rows/`, `case25/`.

Report: .ufo/waves/round-57/w1/out/R57Item04CanonicalBinding.md
Case-25 evidence: .ufo/waves/round-57/reports/R57Item04CanonicalBinding-case25.md
