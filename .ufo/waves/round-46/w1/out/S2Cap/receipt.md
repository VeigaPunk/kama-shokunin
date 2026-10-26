# Receipt index — S2Cap (round 46)

All runs executed in a `git clone --shared` of the lane at
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, in scratch
`/fast/scratch/hyaku/kama-r46/S2Cap/lane` (removed after the run; the `.json`
receipts name it in their `repo` field). Working directory for every command is
the clone root; `TMPDIR=/fast/scratch/hyaku/kama-r46/S2Cap`.

Scratch commits (throwaway clone, identity passed per-commit with `-c`, never in the lane):

| ref | commit | content |
|---|---|---|
| c1 | `78be6d4e3dda1b5f3f25efff26e851258c9eb46a` | `proposed.patch` applied (entry + head counts + PROVINCE clause + coverage digest) |
| c2 | `ba67ee8334c55b428859d2c354f9710ba579b9b7` | c1 + `proposed-calibration-reanchor.patch` |
| armA | — | c2 minus the head mirror row |
| armB | `d459fa495fdbf5f136fe430a2563301af3677c89` | c2 minus the canonical fragment (mirror row kept) |
| armC | — | c2 with the canonical evidence cell stripped of every resolving path |
| armD | `b3c5b7c9a5b0b1998a3d824ecbd38c09389d7af3` | c2 with a non-existent second evidence token added |

| file | command | output (first line) | exit |
|---|---|---|---|
| `01-capaudit-baseline.out/.json` | `python3 tools/capability-repertoire-audit.py --repo . --tip 4a2a4d55… --out 01-capaudit-baseline.json` | `listed 9 observed 9 missing 0 unsubstantiated 0 met True` | 0 |
| `02-selfdesc-baseline.out/.txt` | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 4a2a4d55…` | `mismatches=1 maxN=45 met=False` (`r41=1`, calibration `31` vs tree `32`) | 1 |
| `03-capaudit-patch.out/.json` | `… --tip 78be6d4e…` | `listed 10 observed 10 missing 0 unsubstantiated 0 met True`, `canonical_line 2452`, `capability_tables 12` | 0 |
| `04-selfdesc-patch.out/.txt` | `… --tip 78be6d4e…` | `mismatches=1` (`r41=1` only; `province`/`caps`/`retired`/`saturation` green) | 1 |
| `05-c2counter-patch.out` | `python3 tools/round46-append-audit-check.py --repo . --tip 78be6d4e…` | `selftest=1 fixture=1 lane=1 table=1 lane_events=5 lane_unrestored=0 lane_partial=2 met=True` | 0 |
| `06-appendonly-selftest.out` | `python3 tools/append-only-audit.py --selftest` | `AOA_SELFTEST pass=10 fail=0` after 10 `pass …` lines | 0 |
| `07-appendonly-lane-base.json/.exit` | `python3 tools/append-only-audit.py --repo . --to 4a2a4d55… --json` | `events 5, restored 3, partial 2, unrestored 0`; `0718b6ab SCORECARD.md 2417/2416 partial` | 1 |
| `08-appendonly-lane-patch.json/.exit` | same at `78be6d4e…` | same 5 events, `0718b6ab SCORECARD.md 2417/2412 partial` | 1 |
| `09-capaudit-full.out/.json` | `… --tip ba67ee83…` | `listed 10 observed 10 missing 0 unsubstantiated 0 met True` | 0 |
| `10-selfdesc-full.out/.txt` | `… --tip ba67ee83…` | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=45 met=True` | 0 |
| `11-c2counter-full.out` | `… --tip ba67ee83…` | `selftest=1 fixture=1 lane=1 table=1 … met=True` | 0 |
| `12-appendonly-lane-full.json/.exit` | `… --to ba67ee83…` | 5 events, `0718b6ab SCORECARD.md 2417/2411 partial` | 1 |
| `13-armA-no-mirror-row-capaudit.out` | `… --tip armA` | `listed 10 … met True` | 0 |
| `14-armA-no-mirror-row-selfdesc.out` | `… --tip armA` | `caps=1 mismatches=1` — head names lack `append-only-audit` | 1 |
| `15-armB-no-canon-capaudit.out` | `… --tip d459fa49…` | `listed 9 observed 10 missing 1 … met False` | 1 |
| `16-armB-no-canon-selfdesc.out` | `… --tip d459fa49…` | `retired=1 caps=1 mismatches=2` | 1 |
| `17-armC-bad-evidence-capaudit.out` | `… --tip armC` | `unsubstantiated 1 met False` | 1 |
| `18-armB-no-canon-c2counter.out` | `python3 tools/round46-append-audit-check.py --repo . --tip d459fa49…` | `… table=1 … met=True` — the counter's table leg is satisfied by the mirror row alone | 0 |
| `19-armD-bogus-token-capaudit.out` | `… --tip b3c5b7c9…` | `unsubstantiated 0 met True` — a non-existent second evidence token rides along | 0 |
| `20-armD-bogus-token-selfdesc.out` | `… --tip b3c5b7c9…` | `province=1 mismatches=1` — only the lane's own leg catches it | 1 |

Patch applicability, in the clone:

```
git checkout 4a2a4d55 -- . && git apply --check ../proposed.patch        # OK
git checkout 4a2a4d55 -- . && git apply --check ../proposed-full.patch   # OK
git checkout ba67ee83 -- . && git apply --check -R ../proposed-full.patch # OK
```

No tool was installed or upgraded for this seat (python3 + git only).
