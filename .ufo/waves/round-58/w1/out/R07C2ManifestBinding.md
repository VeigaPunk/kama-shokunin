# R07C2ManifestBinding — manifest pin

Axes: operability, calibration.

## Finding

The supplied C2 manifest revision pin cannot be verified in the available Git object database. The requested pinned revision `941acf70583a2b3a1d33460b31967e0efd291f3e` is unavailable: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -t 941acf70583a2b3a1d33460b31967e0efd291f3e` exited 128 with `fatal: git cat-file: could not get object info`. Accordingly the attempt to read its `MANIFEST.json` exited 128 (`fatal: path 'MANIFEST.json' does not exist in '941acf70583a2b3a1b33460b31967e0efd291f3e'`—the revision is unavailable, so this path result is not evidence that the file was absent).

At the current checked-out HEAD `e4f207f544315612a6ea55b5b7a1cc2d2d4b4a79`, the tree search found no `MANIFEST.json` path. Therefore I cannot confirm the kama r56 and r57 rows from either pinned bytes or HEAD. The supplied frozen claim's description of the pinned-manifest check and round-56 rejected-honest-stop value remains assignment-provided, not independently verified here.

## Measured-tip wording

Once a round-58 closure row is appended, the prior closure-pointer observation is expected to become stale: a live highest-round pointer will advance to round 58. Phrase the result as a snapshot, e.g. “At measured tip `<commit>`, the row named the highest-numbered outside-closure spotcheck then present (round N), repeated N, and matched the kama lane_round N verdict in MANIFEST.json at the pinned manifest revision `<rev>`.” State the exact measured tip and manifest revision. Do not imply the pointer remains current after closure append; re-evaluate the row and counters at the new measured tip rather than treating the expected movement as a retroactive failure.

## Checks and gaps

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 941acf70583a2b3a1d33460b31967e0efd291f3e:MANIFEST.json` — exit 128; pinned path/revision unavailable.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -t 941acf70583a2b3a1d33460b31967e0efd291f3e` — exit 128; object unavailable.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only HEAD | grep -E '(^|/)MANIFEST\.json$' | head -20` — command chain exited 128 because preceding pinned `cat-file` failed; no HEAD path output was produced.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` — exit 0, `/home/vgpnk/Projects/shokunin/kama-shokunin`.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --oneline` — exit 0, `e4f207f5 round-58: validated 72-seat v2 wave spec and dispatch`.

Residual gap: obtain the canonical pinned manifest bytes and a valid HEAD tree path before asserting r56/r57 row contents.