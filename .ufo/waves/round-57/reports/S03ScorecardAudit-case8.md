# S03ScorecardAudit — distinct case 8: independent differential test of the self-assessment counter

Seat: `S03ScorecardAudit` (scribe), kama round 57, wave `kama-r57-w1`. Bounded leaf, no dispatch.
Assigned case 8: inspect SCORECARD and SHONEN mismatches against observed repo state and devise an
exact measurable self-assessment mismatch counter. This file is the **independent execution record**
for that case; the seat report is `.ufo/waves/round-57/w1/out/S03ScorecardAudit.md`, and every
receipt named here lives in `.ufo/waves/round-57/w1/out/S03ScorecardAudit/`.

Read-only on the lane: no source edits, no commits, no installs, pacman untouched.
Scratch: `/fast/scratch/hyaku/kama-r57/S03ScorecardAudit/` (fixtures, `mut46/`, `out/`, `tmp/`).

## What the case's test had to answer

Three questions, each answered by a measurement rather than by reading the counter's docstring:

1. Is the frozen counter correct at its frozen base, and what is the one real stale value?
2. Is the `maxN=56` / `expected 46` disagreement a counter defect?
3. Do the counter's capability and round legs bind to anything outside the document — i.e. can a
   self-consistent edit of SCORECARD change the declared repertoire or the measured round without
   changing the verdict?

## Test 1 — reproducibility and the real stale value

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ TMPDIR=<scratch>/tmp python3 tools/round42-selfdesc-reconcile.py \
      --repo . --tip b89bdab2cc114735ec5d331c6c610134258f7864 \
      --out <scratch>/out/counter-base.out
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1
```

Byte-equal to the committed frozen control `.ufo/waves/round-57/controls/base-c1.out`
(`mismatches=1 maxN=56 met=False`, same detail). Independent census of the disputed count:

```
$ for c in b9d5a091 b89bdab2 7c873d7b 7b74e2f2 8640e34 16efcf5e 77e7f5ee 8a7f1976; do
      echo "$c $(git ls-tree --name-only $c corpus/lessons/ | grep -c verifier-spotcheck)"; done
b9d5a091 42
b89bdab2 43      <-- frozen base: the row is already stale here
7c873d7b 43
7b74e2f2 43
8640e34 43
16efcf5e 43
77e7f5ee 43
8a7f1976 43
```

Answer: the counter is correct; the stale value is the calibration row's `42` (true at the round-56
measured implementation tip, true through the round-56 final lane tip `6e706d15`, and falsified only
by the non-author round-56 verifier spot-check `b89bdab2`, which adds the 43rd blob).
The capability legs are all `0` at the base — the failure is not a capability row count.

## Test 2 — is `expected 46` a real expectation?

None of the tree's own surfaces expect 46, so the test is whether the counter would accept it.
Scratch copies of `round42-selfdesc-reconcile.py` and its imported
`round41-scorecard-reconcile.py`; one scratch-only edit (`maxn = max(rounds)` → `maxn = 46`):

```
$ python3 <scratch>/mut46/round42-selfdesc-reconcile.py --repo <lane> --tip HEAD
tip=16efcf5eedf4887df188790eec48afbb023e7991
r41=0 banner=1 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=46 met=False
detail: banner: head lacks 'Latest measured round: 46'
detail: planned: section does not name '### Planned (round 47)'
exit=1
```

Derivation census on the same tree: `max(^## Round N)=57`; `max(Current authority (round N))=57`;
highest canonical-list heading `49`; canonical first-working max `47`. `46` occurs only in
`SCORECARD.md:2676`, the round-46 measured receipt (`… maxN=46 met=True`), and in the wave's
do-nothing control `controls/c1-noop.py` (`print("mismatches=0 maxN=46 met=True")`, zero reads).
Answer: `46` is a ten-round-old receipt value, not an expectation; a counter expecting it is red
from round 47 onward. The seat-context claim has the direction of the defect backwards.

## Test 3 — differential fixture attack on the document-vs-document legs

Construction (idempotent, all inside scratch):

```
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
ROOT=/fast/scratch/hyaku/kama-r57/S03ScorecardAudit
for v in faithful f1-empty f2-rename f3-maxn; do
  mkdir -p "$ROOT/fixtures/$v"
  ( cd "$LANE" && git archive HEAD SCORECARD.md README.md PROVINCE.md SKILL.md \
        corpus tools registry tests | tar -x -C "$ROOT/fixtures/$v" )
  ( cd "$ROOT/fixtures/$v" && git init -q . && git add -A \
        && git -c user.email=seat@local -c user.name=seat commit -qm "fixture base $v" )
  test "$( cd "$ROOT/fixtures/$v" && git rev-parse --show-toplevel )" = "$ROOT/fixtures/$v" \
        || { echo "TOPLEVEL MISMATCH"; exit 1; }      # guard satisfied before any commit
done
python3 "$ROOT/make-variant.py" "$ROOT/fixtures/<v>/SCORECARD.md" … <v>   # see MANIFEST for hash
```

`make-variant.py` sha256 `ead2fa5149da8a529917c1c1bb21aa9270f8a617bb7f4a84fe028d55c976b747`.
Only `SCORECARD.md` differs between the four fixtures (diffs: `variant-*.diff`); the subset omits
`.ufo`, which is why every fixture run carries the constant `r41=1 receipts=9`.

Variants (base tip when built: `8640e34cad02adcd247ba0862da63f6fb2aab0df`):

| fixture | variant commit | SCORECARD sha256 | edit |
|---|---|---|---|
| `faithful` | `c7e89be35eaaa275809d0d144af880b309b0e2a6` | `883b91b59d372fa8873b8ba15e3fca624d0ff60efc13803bf9689be140a8163d` | none (control) |
| `f1-empty` | `8c13ccee307889dbf1d32b16a668201a04c2fa0e` | `dcabef00026c445dc0aa714b18e529d3bbd997a3a71ea6372ac69d8fe352adbf` | 11 canonical rows and 11 head-mirror rows deleted; §Retired `11 capabilities`→`0`; §Saturation first-working list → `(none)` |
| `f2-rename` | `d77edfea0e247872f5db6a48b9226976a41f3f86` | `2f74bec1ea0704db5382bf44892b58b19641298c6374570859a95e27262a699c` | `\| pin-watch \|`→`\| pin-watch-renamed \|` in all 8 capability-shaped tables |
| `f3-maxn` | `5d5e1c47732d093e552cbf27aaebf7a7c9e3b559` | `0f1dc27c1965402b12040ccc5ab842e91bc914e0b802d66f34bfce4da027f4ec` | fabricated `## Round 99` heading; banner `Latest measured round: 99`; `### Planned (round 100)` |

Post-edit integrity checks on the fixtures (so the attack is self-consistent, not a broken file):

```
f1-empty : canonical rows = 0 ; "6 axes and 0 capabilities" ; "capability first-working rounds (none)"
f2-rename: 8 occurrences of "| pin-watch-renamed |"
f3-maxn  : line 6 "Latest measured round: 99" ; line 3160 "### Planned (round 100)" ; line 3183 "## Round 99 — fabricated heading"
```

Frozen counter, same invocation for each fixture:

```
$ TMPDIR=<scratch>/tmp python3 <lane>/tools/round42-selfdesc-reconcile.py \
      --repo <scratch>/fixtures/<v> --tip HEAD --out <scratch>/out/counter-<v>.out
faithful  tip=c7e89be35eaaa275809d0d144af880b309b0e2a6
          r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=0 province=0 rel=0 mismatches=10 maxN=57 met=False   exit=1
f1-empty  tip=8c13ccee307889dbf1d32b16a668201a04c2fa0e
          r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=0 province=0 rel=0 mismatches=10 maxN=57 met=False   exit=1
f2-rename tip=d77edfea0e247872f5db6a48b9226976a41f3f86
          r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=0 province=0 rel=0 mismatches=10 maxN=57 met=False   exit=1
f3-maxn   tip=5d5e1c47732d093e552cbf27aaebf7a7c9e3b559
          r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=0 province=0 rel=0 mismatches=10 maxN=99 met=False   exit=1
```

Delta against the control: **0, 0, 0**. `caps`, `retired`, `saturation` and `province` stay 0
while the declared repertoire is emptied, renamed, or the measured round is inflated by 42.

Control for the interpretation — the same fixtures through the lane's existing capability census
(so "the frozen counter is blind" is not confused with "the lane is blind"):

```
$ python3 <lane>/tools/capability-repertoire-audit.py --repo <fixture> --tip HEAD
faithful : listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1
f1-empty : listed 0  observed 11 missing 11 unsubstantiated 0  met False  exit 1   <-- kill
f2-rename: listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1   <-- survive
f3-maxn  : listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1   <-- survive
lane     : listed 11 observed 11 missing 0  unsubstantiated 0  met True   exit 0
```

`unsubstantiated 1` is the fixture artifact (`.ufo/waves/round-16/live/receipt.json` is outside the
archive subset); it is identical in all four fixtures and 0 on the lane.

## What the case measured, and what it did not

Measured (receipts, tips and exits above):

- the frozen counter reproduces its frozen base receipt exactly; the only failing leg at the base is
  the calibration spot-check literal `42` against a committed `43`;
- `maxN=56` is the correct base derivation and `46` is a stale receipt value that the counter's own
  banner/planned legs reject;
- the frozen counter's capability legs accept an emptied repertoire, a consistent rename and a
  fabricated round with **zero** added mismatches;
- the existing capability census kills deletion and resolves evidence paths but not the rename;
- one live SCORECARD mirror drift (a dropped evidence token) and one unresolvable cited derivation
  (`scripts/sources-census.sh`) exist at the tip and are invisible to every leg.

Not measured / not claimed: no repair was attempted or claimed (E01CounterRepair owns the repair and
the lane integrated it at `7b74e2f2`); the ledger statistics were checked by direct row counting, not
by `round44/45-*` audits (they require `--fleet`); no axis score, capability admission or verdict is
claimed; counter outputs are valid only for the `tip=` line printed with them, and the lane HEAD
advanced through `89dc4f52`, `7c873d7b`, `7b74e2f2`, `8640e34`, `16efcf5e`, `77e7f5ee` and
`8a7f1976` during this wave, so no receipt is valid without its own `tip=`.

Report: .ufo/waves/round-57/w1/out/S03ScorecardAudit.md
Case-8 evidence: .ufo/waves/round-57/reports/S03ScorecardAudit-case8.md
