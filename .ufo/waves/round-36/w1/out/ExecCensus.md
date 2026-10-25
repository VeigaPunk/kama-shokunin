# ExecCensus — sources-census validate (kama)

## Command

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

No `--today`, no `--out`, no `--file`. Stdout and stderr were captured under the seat directory; the script itself wrote only to those pipes.

## Exit code

```
0
```

## Final ok line

Last stdout line (line 94 of 94, trailing newline present). Fields are tab-separated:

```
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

That is the only `ok` line. It is the script's validate success emit (`lane<TAB>ok<TAB>registry-path`) for the kama target.

## Scoped findings

- stderr: empty (0 lines).
- stdout: 94 lines. Codes: `W04` × 93, `ok` × 1. `E`-codes: 0.
- Contract (script header): exit 0 means clean or warnings; W-codes do not change status. The 93 `W04` lines are "duplicate url … across scopes" and do not contradict the final ok line or exit 0.
- `corpus/SOURCES.md` was not modified. Before and after the run: size `181743`, mtime_ns `1792888036112479233`, sha256 `57352f20b1de70c01405adea6f77bf165006e6cdafda459f4dd985f87f679a46`.

## Files changed

- Report only: `.ufo/waves/round-36/w1/out/ExecCensus.md`.
- Seat scratch (not lane corpus): `.ufo/waves/round-36/w1/out/ExecCensus/validate.out`, `.ufo/waves/round-36/w1/out/ExecCensus/validate.err`.
- No edit to `corpus/SOURCES.md`, fleet repo, sibling lanes, git index, or jj state.

## Behavior

Read-only validate of lane `kama` against `/home/vgpnk/Projects/shokunin`. Registry resolved to `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. Validation accepted the registry (exit 0, final ok line) while reporting cross-scope URL warnings.

## Remaining risks

- The 93 `W04` warnings remain. Fixing them would mean editing `corpus/SOURCES.md`, which this seat must not do.
- `--today` was not pinned; the script used its default UTC date. That does not affect the recorded exit code or ok line for this run (no `E08`).
- Other census modes (`census`, `overdue`, `shared`) were not run. Out of assignment.

## Blockers

None.
