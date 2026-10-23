# CtlWorkingTree — control (executor)

## Policy

The claim C1 requires a **committed** self-assessment correction: for each base statement the
frozen extractor finds false at its writing revision, one row under the frozen heading
`## Round 29 — self-assessment corrections` naming the statement id and stating the check's
observed value.

This control applies the **correct** rows (built by running the frozen counter and recording its
own printed observed values) but writes them to the **working tree only** — they are never
committed. The counter is then scored at `--tip ctl` and again at `--tip HEAD`.

The hypothesis under test: the counter reads committed objects only, so an uncommitted fix is
invisible and the claim cannot be met by working-tree edits alone.

## Exactly what the policy read

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json`
  (C1.claimed_work, C1.predicate, C1.target, controls_planned_before_data).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` (docstring:
  class checks, correction-row grammar, the "reads committed objects only" promise; and the
  `corrections()` / `main()` code that parses rows from `repo.blob(tip, "SCORECARD.md")`).
- Counter sha256 verified **before every run**:
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — matches the frozen value.
- The frozen counter's own first run at the freeze commit (`--tip ctl --list`), whose
  `mismatches[]` array supplied the 11 statement ids and their exact observed values.
- The clone's `SCORECARD.md` at the freeze commit (working tree file, to append to).

## Exactly what the policy did NOT read / did not do

- Did not read any lane blob at any revision other than through the frozen counter's own
  outputs; did not hand-compute a single observed value.
- Did not modify the frozen counter (byte-identical sha256 before and after; verified again at
  the end of the run).
- Did not edit any tracked file in the lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin`
  (its `git status --porcelain` shows only the untracked `.ufo/waves/round-29/controls/` output
  dir; `git log -1` still `827d136`).
- Did not commit the correction rows in the scored clone: `git diff 827d136 ctl` is **empty**
  (`change.diff` is 0 bytes) and `git status --porcelain` shows ` M SCORECARD.md`.
- Did not commit anything else either; the scored clone's branch `ctl` still points at
  `827d136546b8`.
- Did not start any model server; no llama-server was launched.
- Did not touch sibling lanes, MANIFEST.json, .ufo/state or .ufo/watchdog.log.

## Counter line (scored runs, frozen counter, unchanged)

`--tip ctl` (`counter.out`, `receipt.json`):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

`--tip HEAD` (`counter-head.out`, `receipt-head.json`) — identical:

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
```

`met` value: **False** (both runs).

## Interpretation

The counter **refuses** the policy. The 11 correct rows exist in the working tree but the
counter sees `correction_rows 0`, `valid_corrections 0`, `unresolved 11`, `met False`. The
mechanism is visible in the receipt: `append_only True` (the committed tip SCORECARD.md at
827d136 still begins with the base bytes) and `tip 827d136546b8` — the counter reads
`repo.blob(tip, "SCORECARD.md")`, a committed object, and never the file on disk. The working
tree is invisible to it, exactly as its docstring promises ("Reads committed objects only
(git --no-replace-objects); never the working tree").

### Diagnostic (not the scored run)

To show that the rows themselves are correct and the failure is attributable solely to
non-commit, a second scratch clone `repo-committed-check` (same sandbox root, same base commit)
was given the *identical* SCORECARD.md content and the rows were committed there. Result
(`diagnostic-committed.out`, `diagnostic-committed.json`):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 83c83e1e6cef
```

So the same row set that yields `unresolved 0 / met True` when committed yields
`unresolved 11 / met False` when left in the working tree. This isolates the variable: the
counter's gate is commit reachability, not row content.

## Does the policy skip the claimed work?

**Yes — it skips the deliverable, and it also does the work.**

- It performs the measurement half of C1 (runs the frozen check and records the observed
  values) and constructs the correct rows.
- It skips the **delivering** half: preregistration C1.claimed_work requires the correction rows
  to be *appended to SCORECARD.md* as part of the lane's state, i.e. to exist in the committed
  tree that the tip points at. Leaving them uncommitted means the lane at the measured tip
  carries no corrections; the self-assessment stays false there.
- Because the claim is measured at a lane **tip**, an uncommitted edit can never satisfy it:
  there is no tip commit that contains the rows, so `--tip ctl` and `--tip HEAD` both resolve
  to `827d136546b8` and both score `unresolved 11`.

This is a genuine miss of the claim as stated, and a working control: it shows the counter is
not fooled by a fix that exists only on disk.

## Tooling

No tool was installed or updated in this run (no pacman, no uv tool, no new binary). Everything
used was already present: `/usr/bin/git`, `/usr/bin/python3`, `/usr/bin/sha256sum`,
`/usr/bin/du`, `/usr/bin/wc`, `/usr/bin/tail`.

## Files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlWorkingTree/REPORT.md` — this report.
- `.../CtlWorkingTree/receipt.json` — scored receipt, `--tip ctl`.
- `.../CtlWorkingTree/counter.out` — scored stdout for `--tip ctl` (with `exit=0`).
- `.../CtlWorkingTree/receipt-head.json` — scored receipt, `--tip HEAD`.
- `.../CtlWorkingTree/counter-head.out` — scored stdout for `--tip HEAD` (with `exit=0`).
- `.../CtlWorkingTree/change.diff` — `git diff 827d136 ctl` in the scored clone: **empty (0 bytes)**, because the policy commits nothing.
- `.../CtlWorkingTree/worktree.diff` — the actual policy change (the 11 uncommitted rows), `git diff` in the scored clone.
- `.../CtlWorkingTree/diagnostic-committed.json` / `.../diagnostic-committed.out` — diagnostic run with the identical rows committed in a second clone.

Report: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlWorkingTree/REPORT.md
