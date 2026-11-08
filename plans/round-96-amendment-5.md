# Round 96 — amendment 5 (authoritative predicate statements; the identity clause binds the amended commits)

Date: 2026-11-08. Author: L1 `KamaR96`. Supersedes the *identity clause* of the three predicates in
`plans/round-96-claims.md` only; every property, cell, tolerance and kill rule stands as amended by
`plans/round-96-amendment-2.md` and `-3.md`. Reason: wave-1 `CR02DisclosureCounter` B1 showed that the
frozen wording "the counter's bytes identical to this freeze commit" makes C3 unsatisfiable — amendment 1
had to repair the counter's own regex after F, so the frozen-bytes arm can never pass while the amended
bytes are not the freeze bytes. The lane chose to repair correctly and restate the clause rather than keep
a predicate whose only satisfying reading is a broken instrument.

## Identity

| Claim | Counter | Reference revision (bytes identical here and at M) |
|---|---|---|
| C1 | `tools/round96-router-budget.py` | `b3289c18` (amendments 1–3; unchanged by 4 and 5) |
| C2 | `tools/round96-depth-audit.py` | `20317286` (amendment 4) |
| C3 | `tools/round96-disclosure-audit.py` | `20317286` (unchanged since amendment 2's follow-up `4a0f6a35`; re-verified) |

Verified: `git show <rev>:<counter> | sha256sum` equals the working file's digest at the measuring tip.
Kill rule K3 binds these revisions, not the freeze commit.

## Predicates (authoritative)

1. **C1** — `python3 tools/round96-router-budget.py --repo . --rev b3289c18 --work <private> --slow-files 96`
   prints `ROUTER_BUDGET96 cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1`
   and exits 0; the base control (`--rev 5d43528b --burners 0 --allow-clock`) prints `mismatches=1
   positive_mismatches=1` with W11-700k red and every other cell green.
2. **C2** — `python3 tools/round96-depth-audit.py --repo . --rev 20317286` prints
   `DEPTH_AUDIT checks=14 mismatches=0 met=True`, exit 0; at `5d43528b` it prints `mismatches=14`, exit 1.
3. **C3** — `python3 tools/round96-disclosure-audit.py --repo . --rev 20317286` prints
   `DISCLOSURE_AUDIT checks=6 mismatches=0 met=True`, exit 0; at `5d43528b` it prints `mismatches=3`, exit 1.

## Measurements (this amendment's own runs)

- C1 base control (probe at `5d43528b`, counter at `b3289c18`): `cells=12 mismatches=1
  positive_mismatches=1 load_cells=12 load_stable=1 probe_sha256=b49d961a… rev=5d43528b w03_seconds=84.5`,
  exit 1 — W11-700k `ok=0`, W12-strings `ok=1`.
- C1 at M1 (`b3289c18`): see `measured/c1.out`.
- C2: `.ufo/waves/round-96/measured/c2.out` (`checks=14 mismatches=0 met=True`, exit 0).
- C3: `.ufo/waves/round-96/measured/c3.out` (`checks=6 mismatches=0 met=True`, exit 0).

## Disclosed (not repaired)

`CR02DisclosureCounter` B2–B5: the C3 instrument grades literal presence, so a comment that names
1 000 000 as a *non-binding* figure and a docstring that disagrees with the wrapper on a different
number are both ungraded; the capability-row check accepts any resolvable ancestor, not the row's own
claim revision. These are the round-97 frontier, recorded here rather than silently widened.
