# K2Design evidence bundle — reproduction

Seat K2Design, round 46, C2 design critique (calibration). Nothing here writes to the
lane; every command is read-only on a git clone.

## What was run, on what

- Lane repository: a `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin`
  made under `/fast/scratch/hyaku/kama-r46/K2Design/lane`, used read-only and removed
  after the seat (the absolute paths recorded in the `# command:` headers of the
  receipts point at that removed clone; the same commands work against any clone of the
  lane, and the tool is `tools/append-only-audit.py` in it).
- The receipts were produced with the clone checked out at `96d3291` (lane head at the
  time of the seat). The tool blob is `768f078e62bd0585c5d3c85dda36426aa6d6b1cb` there
  and at the landing commit `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`.
- Fixtures: throwaway git repos created with `tempfile.mkdtemp` under the seat scratch
  directory; each driver asserts `git rev-parse --show-toplevel` equals its own
  directory before the first commit.

## Re-run

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /some/where/lane
python3 analysis.py /some/where/lane 0163fea2dab3f282ebd70c71da9ab5de4cedf733   # e04
mkdir -p /some/where/fx
python3 fixtures.py /some/where/lane/tools/append-only-audit.py /some/where/fx   # e05
```

`e02`/`e03`/`e03b` are direct runs of the tool:

```
python3 <lane>/tools/append-only-audit.py --repo <lane> --to <rev> [--json]
```

`e06`/`e08` are `git -C <lane> grep|show|log` readings recorded with their commands.

## Receipts

| file | produced by |
|---|---|
| `e01-tool-identity.txt` | `git rev-parse 96d3291:tools/append-only-audit.py 4a2a4d55:…`, `sha256sum`, `git log --follow` |
| `e02-audit-base-0163fea2.txt` | tool `--json` at the base revision, exit 1 |
| `e03-audit-landing-96d3291.txt`, `e03b-audit-at-4a2a4d55.txt` | tool at both landing tips, exit 1, same 5 events |
| `e04-analysis.txt` | `analysis.py <lane> <base>` |
| `e05-fixtures.txt` | `fixtures.py <tool> <scratch>` (F1 blank lines, F2 duplicate text, F3 merge, F4 per-file threshold) |
| `e06-declarations.txt` | append-only declarations at `0163fea2` in the lane and the fleet `PROTOCOL.md` |
| `e07-tool-lines.txt` | the cited lines of `tools/append-only-audit.py` |
| `e08-repair.txt` | `82b5e9d3` depth re-anchor and the unchanged tip axis scores |

No tool was installed or upgraded for this seat.
