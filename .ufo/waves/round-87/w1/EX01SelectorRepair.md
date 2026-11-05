# EX01SelectorRepair — kama r87 w1, C1 successor selector

## Scope

Built `tools/round87-rendered-cells.py` from `tools/round86-rendered-cells.py` at freeze
`94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (full-file candidate + unified diff), per
`plans/round-87-claims.md` R1–R4:

- **R1**: `FENCE_CLOSE` rebuilt without the `CONTAINER` prefix — a closer is ≤3 leading spaces,
  opener's fence char at least as long, then only spaces/tabs; a list-marker or blockquote-marked
  line is content, never a closer (CommonMark 0.31.2 §4.5, §5.2/§5.1). Openers keep container
  support (round-86 `a2-list-fence` case).
- **R2**: disposition is the single token after `verdict ` on the closure's own verdict line
  (new `VERDICT` regex; `disposition_of` rewritten). A line whose post-`verdict` token names no
  disposition (the committed closure's C2/C3 `Verdict: verified…` lines) is not the closure's
  verdict line; missing or conflicting verdict lines are mismatches. `DISPOSITIONS` vocabulary
  unchanged.
- **Coupling refinement (required by frozen probe P-C + kill rule, beyond R1/R2's letter)**:
  the gate receipt must be carried at **every `measured at `REV`` citation** in the authority
  cell; citations inside a sentence carrying another round's own token (a self-coupled,
  superseded terminal-gate claim) are exempt; non-measurement mentions (superseded history,
  delivered tips) stay outside the coupling. Replaces the round-86 any-one-revision loop.
- R3/R4 respected: `fixture`, `grade`, `render`, `A`, `B`, `GOOD_*`, `CouldNotEvaluate` and the
  three-fact population untouched; selftest gained two arms (`pa-list-marker-closer-content`,
  `pb-verdict-line-disposition`), declared subjects = R1 and R2.

No tools installed or updated; no pacman transaction; no mutating git command anywhere
(`git clone --shared` + `checkout --detach` per contract; `rev-parse --show-toplevel` asserted
before and after the checkout).

## Commands and outputs (exit codes)

Working clone `/fast/scratch/hyaku/kama-r87/EX01SelectorRepair/wt`, detached at
`94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`, `git status --porcelain` empty; all checks re-run
from the **delivered** candidate bytes; receipts in the out dir.

1. `python3 <out>/round87-rendered-cells.py --selftest` → `RENDERED_CELLS_SELFTEST pass=19
   fail=0`, **exit 0** (`selftest.out`): all 17 round-86 arms pass; new P-A/P-B arms pass.
2. `python3 .ufo/waves/round-87/controls/c1-probes.py <out>/round87-rendered-cells.py` →
   `C1_PROBES probes=3 escapes=0 control=red`, **exit 0** (`c1-probes.out`) — exact frozen line;
   control red, P-A/P-B/P-C all red.
3. `python3 <out>/round87-rendered-cells.py --repo <wt> --rev 94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`
   → `RENDERED_CELLS facts=3 mismatches=2 gate=1 closure=0 disposition=0 newest_gate=86
   newest_closure=86`, **exit 1** (`c1-live-at-freeze.out`) — expected on the uncorrected
   SCORECARD; findings: closure row names round-85 vs newest round-86; row does not name
   `round86 rejected-honest-stop`.
4. Case-(d) fixtures (`case-d.out`): list-marker, blockquote-marked and four-space-indented
   closer lines all fail to close — candidate 3/3 red, **exit 0**; round-86 selector **escaped**
   the list-marker and blockquote closers (mismatches=0, exit 0 each; before-evidence, exit 1).
5. Receipts scan (`receipts-scan.out`, **exit 0**): `rendered()` bytes over the frozen SCORECARD
   identical old vs new (722018 = 722018); R2 scan of the frozen round-86 closure: exactly one
   disposition-token verdict line (`verdict \`rejected-honest-stop\``, line 76) →
   `disposition_of = rejected-honest-stop`.

## Findings

1. **R1 kills P-A** (`c1-probes.out:2`): `- ``` ` inside the shadow fence no longer closes it;
   the shadow's green cells stay hidden and the stale live cells keep the grade red.
2. **R2 kills P-B** (`c1-probes.out:3`): the body's `rejected-harmed` (not on the verdict line)
   is ignored; the verdict token `rejected-honest-stop` makes the row naming
   `round85 rejected-harmed` a mismatch.
3. **P-C required the coupling refinement** (`c1-probes.out:4`). The live authority paragraph
   names **five** 40-hex revisions (`0f8a0980…`, `239a8f39…`, `948dec78…` ×2, `6abaf0a8…`), two
   of them round-85 history; a first strict "every named revision" build false-failed the live
   gate (mismatches=3, gate=0). Discriminator adopted: only `measured at `REV`` citations
   couple, except citations in sentences carrying another round's own token (the round-85
   `Terminal gate measured at …` re-citation is self-coupled and exempt). Safety measured:
   `0f8a0980…` and `239a8f39…` are both ancestors of the freeze (`merge-base --is-ancestor`
   exit 0) and both carry `.ufo/waves/round-86/measured/terminal/gate.out` with the exact
   `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0` token (1 matching line each) → live
   `gate=1` preserved.
4. **Live residual = exactly the L1's correction work**: `mismatches=2` are closure (row names
   round-85, newest is round-86) and disposition (row lacks `round86 rejected-honest-stop`);
   the disposition finding now names the true verdict token, which is precisely the token the
   corrected calibration row must carry for C1 after-predicate 1 (`mismatches=0` at R).
5. **Residual constructs that could still hide a live cell** (question d):
   (i) a container-marked fence **opener** outside a real fence (`- ``` `, `> ``` `,
   `1. ``` `) opens a phantom block that swallows every following cell until a column-0 closer —
   CommonMark-faithful and not present in the frozen SCORECARD (all 42 fence lines are
   column 0; `rendered()` bytes identical old vs new, `receipts-scan.out`), but any future
   prose quoting a fence marker inside a list can hide cells;
   (ii) R1 freezes the closer cap at three **absolute** spaces, so a deeper-indented
   cmark-legal closer inside a list container would leave the block open — fail-closed (hides
   later cells → red/exit 2), never a false green;
   (iii) verdict-token residual: prose `verdict <disposition-word>` outside the closure's
   verdict line can still flip the extracted token; the frozen round-86 body carries exactly one
   disposition-token verdict line (`receipts-scan.out` R2_SCAN), so the live predicate is safe.

## Deliverables

- `.ufo/waves/round-87/w1/out/EX01SelectorRepair/round87-rendered-cells.py`
  (sha256 `fbdf11760f926d092a008a91d2c0c90c02682cb0df6c9d739948ad83573fb8ce`)
- `.ufo/waves/round-87/w1/out/EX01SelectorRepair/selector.diff` (197 lines, 10 hunks)
- Receipts in the same dir: `selftest.out`, `c1-probes.out`, `c1-live-at-freeze.out`,
  `case-d.out`, `receipts-scan.out`, `sha256s.txt`, `measured-rev.txt`
- Driver sources (copies kept as receipts): `round87-case-d.py`, `round87-receipts.py`

Scratch dir removed before yield. L1 integration note: gate arms that run this instrument's
`--selftest` (C2's `round86-instruments`) must run the **round87** file's selftest after
integration; the arm's `<prefix> pass=<n> fail=0` shape is unchanged
(`RENDERED_CELLS_SELFTEST pass=19 fail=0`).

VERDICT: successor selector verified at 94e8fe7b — probes `escapes=0 control=red` exit 0, selftest 19/0, live `mismatches=2` naming exactly the closure/disposition cells the L1 correction must clear; P-C required a measured-at coupling refinement documented in selector.diff.
