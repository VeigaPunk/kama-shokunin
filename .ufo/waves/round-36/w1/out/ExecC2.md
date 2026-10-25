# ExecC2

Seat: ExecC2. Axis: coverage. Tool not edited. No git add/commit/stash/checkout/switch/reset/pull/push. No mutating jj. No subagent. Predicate not changed.

Scored tip (git show, not HEAD): `e5a8ececf3d60fd53b36bb74299693a29e8f74b6` (`cat-file -t` = commit). HEAD at measurement: `9014843cb7de8fbe87a97954c13832b67d55f046`. Working-tree `tools/round36-coverage-audit.py` porcelain empty (tracked, unmodified). sha256 `b052a9fe251bedac50641bae7fd79f08c8727691e8c75257968419a50d738b60`.

## Base command

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
```

```
named 0 file_exists 0 cited_new 0 met False
```

exit 1

## Selftest

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 --selftest
```

```
SELFTEST base_met=False outside_met=False old_id_met=False pass=1
base named 0 file_exists 0 cited_new 0 met False
```

exit 0

## Behavior

Do-nothing at the frozen tip holds: named=0, file_exists=0, cited_new=0, met False. Selftest pass=1 (base_ok, outside_ok, old_ok). Matches the already-printed controls. Tool left unchanged.

## Files changed

- `.ufo/waves/round-36/w1/out/ExecC2.md` (this report only)

## Remaining risks

Score is the committed tip via `git show`, not the working tree and not HEAD `9014843`. A later uncommitted coverage entry would not change this base line.

## Blockers

None.
