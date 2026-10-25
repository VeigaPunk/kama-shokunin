# R42B19 measurements (raw commands and outputs)

Seat root: `/fast/scratch/kama-r42/seats/R42B19` (private clone of the read-only lane clone).
Every run below used `TMPDIR=/fast/scratch/kama-r42/seats/R42B19/tmp` (or a private `leak*` dir for the leak measurement).

## 1. Base digest census (row 1)

```
$ python3 tools/digest-ledger.py scan --repo <clone> --rev 0b606b03bf0b2a87b791aa537f6c72c941624cf0 --details
tokens=94 blob=84 external_ok=0 external_absent=0 unverifiable=0 wrong_flagged=0 ledger_bad=0 wrong_unflagged=1 unknown=9
detail: wrong_unflagged 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2 (first 8 characters match a real digest)
detail: unknown <9 lines, one per digest>
EXIT=1
```
Full receipt: `digest-scan-base.out`.

```
$ python3 tools/digest-ledger.py scan --repo <clone> --rev c8c92db4bdf1c64357b995e0fe8d2a4f481fe995 --details
tokens=96 blob=86 external_ok=4 external_absent=0 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0
detail: wrong_flagged 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2 class=wrong
EXIT=0
```
Full receipt: `digest-scan-claimtip.out`.

No gate caught the class at base — the two round-41 counters pass at base while 10 digests are unexplained:

```
$ python3 <0b606b03:tools/round41-scorecard-reconcile.py> --repo <clone> --tip 0b606b03 --out round41-c1-at-base.out
axes=6 facts=24 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True
EXIT=0

$ python3 <0b606b03:tools/round41-pinwatch-audit.py> --repo <clone> --tip 0b606b03 --seed 42 --out round41-c2-at-base.out
tool=1 contract=1 live=1 sourced=1 capability=1 met=True seed=42
EXIT=0
```

`tools/citation-provenance.py:32` re-hashes only tokens of the form
`cite(<rev>, <path>, sha256=<64 lowercase hex>)`, so an unregistered cited digest is never read.

## 2. Round-41 counter temp export (row 2)

Base blobs never remove the export:

```
$ git show 0b606b03:tools/round41-scorecard-reconcile.py | grep -c "atexit\|rmtree"   -> 0
$ git show 0b606b03:tools/round41-pinwatch-audit.py       | grep -c "atexit\|rmtree"   -> 0
$ grep -n "mkdtemp" <base blobs>   -> round41-scorecard-reconcile.py:184, round41-pinwatch-audit.py:208,221
```

Measured per-run residue on this host, private `TMPDIR`, base counter bytes:

```
$ TMPDIR=.../leak1 python3 <0b606b03:round41-scorecard-reconcile.py> --repo <clone> --tip 0b606b03
mismatches=0 met=True   EXIT=0
$ ls -1 .../leak1        -> r41c1-41mitn9z
$ du -s --bytes .../leak1 -> 225502574      (du -sh -> 259M)

$ TMPDIR=.../leak2 python3 <0b606b03:round41-pinwatch-audit.py> --repo <clone> --tip 0b606b03 --seed 42
met=True   EXIT=0
$ ls -1 .../leak2        -> r41c2-9eiak0h7
$ du -s --bytes .../leak2 -> 225518375      (du -sh -> 259M)
```

Fixed counters at the claim tip:

```
$ grep -n "atexit" tools/round41-scorecard-reconcile.py tools/round41-pinwatch-audit.py
tools/round41-scorecard-reconcile.py:187:                atexit.register(shutil.rmtree, export, True)  # round 42: remove the export (R41A10-10)
tools/round41-pinwatch-audit.py:211:    atexit.register(shutil.rmtree, export, True)  # round 42: remove the export (R41A10-10)
```

SIGKILL gap, measured not inferred (fixed counter at claim tip, private `TMPDIR`):

```
$ setsid env TMPDIR=.../killtmp python3 tools/round41-scorecard-reconcile.py --repo <clone> --tip c8c92db &
$ sleep 2; ls -1 .../killtmp  -> r41c1-idn0js2h
$ kill -9 <python pid>
$ sleep 3; ls -1 .../killtmp  -> r41c1-idn0js2h     (atexit never ran; du -sh .../killtmp -> 41M)
```

## 3. Head sections at base (row 3)

```
$ python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip 0b606b03 --out base-c1.repro.out
r41=0 banner=4 planned=3 retired=4 saturation=3 caps=4 receipts=0 readme=11 province=5 rel=6 mismatches=40 maxN=41 met=False
EXIT=1
```
Byte-identical to `.ufo/waves/round-42/controls/base.c1.out` except that the control builder appends the literal `exit=1` line.
Full receipt: `base-c1.repro.out`.

Base head text (blob `0b606b03:SCORECARD.md`): banner at lines 6-13 ("actual round 5, blocked attempt",
"operability and freshness", "adds **zero** verified completed rounds"); `## Capabilities` at 135-141
("30 opened ... 17 mined ... 5 rejected", one row); `## Saturation` at 143-145 ("8/10 on every owned axis",
"N = 4 ... no capability entering the table"); §Planned and §Retired at the round-5/round-3 state
(R41A10 §2-§6 quotes them).

## 4. Separability of C1 from C3 (rows 4 and 5)

Pre-filter facts (blobs `dd9f5dc:SCORECARD.md`, `2793eb5:SCORECARD.md`): freshness run fact counted every
registry row (`...print(sum(1 for r in recheck if r))` -> `220`), coverage run fact counted every knowledge
file (`glob('corpus/knowledge/*.md')` -> `35`).

Post-filter facts (`c8c92db:SCORECARD.md:15,17`): rows `<=477` -> `218`; knowledge files excluding
`engine-sides` -> `34`; head `## Capabilities` states "Registry counts are not restated here".

Committed separability receipt vs its before-filter copy:

```
$ cmp controls/sep-c1-only.c1.before-filter.out controls/sep-c1-only.c1.out   -> identical (exit 0)
$ md5sum controls/sep-c1-only.c1.before-filter.out controls/sep-c1-only.c1.out
d4ee65aadc1b9180586be01abaddaaae  controls/sep-c1-only.c1.before-filter.out
d4ee65aadc1b9180586be01abaddaaae  controls/sep-c1-only.c1.out
$ head -2 controls/sep-c1-only.c1.out
tip=279ed0d3e17db97e8467c7ac8c7defe7af1273f5
r41=2 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=42 met=False
```

Independent rebuild of the sep-c1-only tree from the post-filter claim tip `c8c92db` (same file set as
`controls/build_separability.py` sepC1: drop `tools/digest-ledger.py`, `registry/digest-ledger.tsv`,
`corpus/knowledge/context-capacity-engine-sides.md`, `corpus/lessons/round-42.md`,
`.ufo/waves/round-42/{c3,assimilation}`, restore `corpus/SOURCES.md` and `corpus/README.md` from base):

```
$ python3 tools/round42-selfdesc-reconcile.py --repo <sep tree> --tip a71c6f8b29d658f193f109f9c0ce6266523666b8
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=42 met=True
EXIT=0
```
Full receipt: `sep-c1-only.repro.out`. Fixture repo identity verified before commit:
`git -C <sep tree> rev-parse --show-toplevel` == `<sep tree>`; identity passed per-command with
`-c user.name=r42b19 -c user.email=r42b19@fixture.invalid`.
