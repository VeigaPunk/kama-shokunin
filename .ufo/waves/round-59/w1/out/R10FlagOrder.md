# R10FlagOrder — argv reorder, `--flag=value` forms, and syntactically-similar invocations (round 59 C1/C2 counter CLI)

Round 59, kama, wave w1, leaf falsification seat. Axes under test: operability + calibration.
Targets: `tools/round59-c1-counter.py` at measured tip `aca8d0067ea25627c5015c2193c843965148bc8e` and `tools/round59-c2-counter.py` at measured tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35` with `--fleet-ref HEAD`. Frozen controls: `.ufo/waves/round-59/controls/freeze.txt` (untouched; never read-modified).

Seat work is falsification, not judgment. Every verdict below names the attacked claim/clause and the exact command, observed output, and exit code. "Unrun is not passed" — nothing here is claimed without a recorded run.

## Environment, bounds, method

- Host `python3` 3.14.8, `git` 2.56.0. No installs were needed; none performed (RULES.md tooling directive recorded; pacman pause respected).
- Scratch: `/fast/scratch/hyaku/kama-r59/R10FlagOrder` (created; `TMPDIR` set explicitly on every invocation; removed before yield — verified below). Never `/tmp`.
- Lane tree and fleet repo strictly read-only: all lane/fleet-bound calls are `rev-parse`/`show`/`ls-tree`/`status --no-optional-locks` plus the frozen-shape counter runs. Variant runs went against a `git clone --no-hardlinks` of the lane in scratch (both frozen tips verified resolving in the clone). Forge fixture: a fresh git repo in scratch, `git -C "$D" init`, `git rev-parse --show-toplevel` asserted equal to `$D` before committing, identity passed inline via `-c user.name=… -c user.email=…` scoped to that one command inside the fixture. No counters, targets, kill rules, or fixtures altered after seeing results.

## Baselines reproduced (as frozen, both pass)

C1, frozen shape vs lane, wall 4.4s:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e --work <scratch>/canon-work
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
(detail: genuine/B1/B2/B3 accept exit=0; N01–N16 reject exit=1)
exit=0
```

C2, frozen shape at three fleet refs — all `rows=44 mismatches=0 met=True`, exit 0:

| `--fleet-ref` | resolved fleet | result |
|---|---|---|
| `HEAD` (current) | `0f99f606120d0c884656c6e7a290f0e8f33c2181` | met=True |
| `58cffd1f…` (measured) | `58cffd1f42723048bcfe48eb0bc2f346caa9b77f` | met=True |
| `3f3dd973…` (goal-stated HEAD) | `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` | met=True |

## Findings (severity-ordered)

### F1 — HIGH — C1 `--checker` substitution yields receipts byte-identical to the genuine measured run

Attacked clause: freeze C1 sentence "…emits a decoy `--counter`, or routes its argv to `python3 other-script --counter` must not meet." The counter's own argv surface carries the same-shaped hole against itself: `--checker PATH` (help text: "external checker path for pre-data shortcut controls") replaces the checker under test with any path, and the counter's stdout/`--out` receipt contains **no field recording which checker ran**.

Evidence — four full battery runs, outputs byte-identical (`diff` × 3 → `IDENTICAL`), all `met=True` exit 0:

1. canonical vs lane (above);
2. canonical shape vs scratch clone → `tip=aca8d006… met=True`, identical;
3. reordered + all-equals + short tip: `--work W --tip=aca8d0067 --repo=<clone> --out=…` → `tip=aca8d0067ea25627c5015c2193c843965148bc8e … met=True`, identical (short sha silently resolved to the full 40-hex);
4. decoy: `--checker <scratch>/decoy-checker.py --repo=<clone> --tip=aca8d0067 …` where the decoy decides each leg **by fixture directory name only** (exit 1 iff basename starts with `N`; exit 0 otherwise) and never executes or inspects the real checker → `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`, identical receipt.

Consequence: any re-run receipt (`tip=… met=True`) cannot prove the tip's checker bytes were exercised. The recorded round-59 measurement (which passed no `--checker`) stands; the finding is that the class of defect the predicate excludes for battery legs — routing the work to a different script while keeping the shape — is open on the counter's own surface, invisibly in its receipts. Non-binding fix surface: echo checker provenance (path + sha256 + `tip-blob` vs `external`) into the receipt line.

### F2 — MEDIUM — C2 accepts a forged fleet repo; `--fleet-rep` vs `--fleet-ref` differ by one silent letter

Attacked clause: C2 kill rule "no current external verdict available → claim not met"; predicate "fleet closure verdict … from named repo/ref inputs".

Forge fixture (scratch): `MANIFEST.json` = `{"rounds":[{"type":"closure","lane":"kama","lane_round":57,"verdict":"rejected-honest-stop"}]}`, committed as `fa2d3ef83985b3b1f9e2b7d97547c3afdad2a800` (toplevel asserted, inline `-c` identity).

```
python3 …/round59-c2-counter.py --repo <lane> --tip 2c7443ab… --fleet-repo <forge> --fleet-ref HEAD
tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=fa2d3ef83985b3b1f9e2b7d97547c3afdad2a800 maxN=57 manifest=rejected-honest-stop
rows=44 mismatches=0 met=True
exit=0
```

Same result via the abbreviation `--fleet-rep <forge>` — argparse `allow_abbrev` silently binds it to `--fleet-repo`, not `--fleet-ref`; in a copied command line the two are near-indistinguishable while semantically opposite. The receipt does bind the consulted sha (honest output), but nothing marks non-canonical fleet provenance, so the counter alone cannot enforce the kill rule. Naming fleet inputs by flag is the frozen design ("named repo/ref inputs"), so this is an audit-surface finding, not evidence the recorded measurement used a non-canonical fleet (it did not — baseline above).

### F3 — MEDIUM — duplicate flags silently last-wins in both counters

C1, differential proof via fast-fail probes (both exit 2, different messages, no warning):

```
--repo <clone> --repo <nogit> --tip <tip> --checker <absent>  → could-not-evaluate: invalid tip        (repo = LAST value)
--repo <nogit> --repo <clone> --tip <tip> --checker <absent>  → could-not-evaluate: checker file absent (repo = LAST value)
```

C2, full runs, both `met=True` exit 0 — the fleet rev the verdict is computed against is decided by argv order alone:

```
--fleet-ref 58cffd1f… --fleet-ref HEAD   → fleet=0f99f606… (last wins)
--fleet-ref HEAD --fleet-ref 58cffd1f…   → fleet=58cffd1f… (last wins)
```

Duplicate `--checker` is likewise accepted without error (probe: both-absent duplicates → `checker file absent` exit 2).

### F4 — LOW — C2 honors `GIT_*` environment; C1 strips it (asymmetric hijack surface)

C1's `git()` strips `GIT_*` variables from the child env; C2's does not (source). Runtime proof on C2, argv identical to the canonical run:

```
env GIT_DIR=<forge>/.git python3 …/round59-c2-counter.py --repo <lane> --tip 2c7443ab… --fleet-ref HEAD
could-not-evaluate: unresolvable lane tip or fleet ref
exit=2
```

An env-only difference redirects C2's repo lookups. Not an argv finding; recorded because it is the same class of invisible-input variation as F1/F2.

### F5 — LOW — misattributed diagnostics on missing inputs (both counters)

C1: `--repo <nogit>` → `could-not-evaluate: invalid tip` (a repo failure reported as a tip failure). C2: missing `--repo` and missing `--fleet-repo` both collapse to `could-not-evaluate: unresolvable lane tip or fleet ref`. Every case fails closed (exit 2); cost is triage misdirection only.

### F6 — LOW — C1 empty `--work=` silently ignored; unset fallback targets the shared hyaku root

`root_for(arg)`: `arg or os.environ.get("TMPDIR") or os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"), "kama-r59")`. `--work=` (empty) is falsy → silently falls back to `TMPDIR` (probe accepted the value and ran to `checker file absent`, exit 2 — no parse error). Runtime residue cannot demonstrate the fallback location because the counter `rmtree`s its work dir in `finally` (observed: 0 leftover `r59-c1-*` dirs). If both `--work` and `TMPDIR` are unset, the work root is the shared `/fast/scratch/hyaku/kama-r59` — a cross-seat shared directory; not exercised (outside my scratch bounds). Code-cited.

## Invariants that held (tested, no finding)

- **Argv order is fully invariant** in both counters (C1 full-run diff `IDENTICAL` across permutations; C2 identical output lines for permuted orders).
- **`--opt=value` / `--opt value` / mixed forms**: identical binding and output everywhere tested (both counters).
- **Abbreviations** (`--rep --ti --chec --wo`, one-letter `--r --t --c` on C1; `--r --t` on C2) accepted with same semantics — CLI support confirmed, no behavior change.
- **Refusals fail closed, exit 2 with usage**: unknown flags (`--frobnicate`, `--verbose` → "unrecognized arguments"), extra positional, `--` separator, option-like value (`--tip --fleet-ref` → "argument --tip: expected one argument"), ambiguous prefix (`--fleet` → "ambiguous option: --fleet could match --fleet-repo, --fleet-ref"), empty values (`--tip=`, `--repo=`, `--fleet-ref=`).
- **Rev flexibility is honest**: short shas (`aca8d0067`, `2c7443ab`) and expressions (`<tip>~0`) accepted; output always binds the resolved full 40-hex tip and fleet.
- **C2 `--out` receipt** byte-identical to stdout (diff → `OUT-FILE-IDENTICAL-TO-STDOUT`); C1 `--out` likewise written on the success path (decoy receipt file checked).
- `--help` exit 0 on both; surfaces match the sources read for this seat.

## Observations

- **Fleet drift vs assignment**: the goal states fleet HEAD `3f3dd97345ef…`; the fleet's actual HEAD is `0f99f606120d…` ("rounds ledger: tabi r40 closure (rejected-honest-stop) — hyaku, non-author"), with `3f3dd973` its ancestor. C2 is `met=True` at all three fleet refs (table above) — the round-59 calibration row verdict is stable across this drift. Recorded, not resolved: fleet is read-only for this seat.
- C2 is also `met=True` at the lane's current HEAD `4a541190b6d4…` (not only the frozen measured tip); each receipt binds the tip actually named.
- Lane worktree untracked population grew 22 → 70 entries during the seat window (siblings landing `.ufo/waves/round-59/w1/out/*`, wave flags, controls `c2-after.*`); `status --porcelain` hash `988baeb9…` → `5e1affe…`, HEAD constant `4a541190` ("round-59: freeze swarm dispatch evidence"). My seat's lane-bound operations were read-only plumbing and the frozen-shape counter runs; no lane writes from this seat.
- External S517/S518 spot-check remains unrecorded; no discernment progress is claimed or implied by this seat. No score or capability claim is made.

## Verification gaps

- The decoy space under `--checker` is unbounded; one decisive name-based decoy demonstrated, not an exhaustion of the class.
- C1's work-root fallback location is code-cited, not runtime-proven (work dir always removed in `finally`).
- C1 `--out` binding exercised on the success path only (early exits return before writing).
- C2 field batteries at other tips/fleet refs not swept — this seat's scope was the argv surface.

## Bounds compliance & cleanup

No source edits; no commits or pushes; lane and fleet read-only throughout; scratch `/fast/scratch/hyaku/kama-r59/R10FlagOrder` removed before yield (verified absent). No tool installs (python3/git preexisting; nothing added to PATH directories).
