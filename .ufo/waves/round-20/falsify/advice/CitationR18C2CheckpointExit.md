VERDICT: confirm - the registry row, its bound document cite token, and the pinned Git blob agree exactly.

- Registry row `registry/required-citations.json:94-99` specifies id `r18-c2-checkpoint-exit`, revision `101f3991d3570bc9350fbf9c5561f4be1185699d`, path `.ufo/waves/round-18/runs/c2-survivors.exit`, SHA-256 `5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985`, and doc `corpus/lessons/round-18.md`.
- The bound document contains the corresponding token at `corpus/lessons/round-18.md:469`; its revision, path, and digest match the row exactly.
- Ran `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 101f3991d3570bc9350fbf9c5561f4be1185699d:.ufo/waves/round-18/runs/c2-survivors.exit | sha256sum`; output was `5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985`, and the pipeline exit was 0.
- `git show` bytes were `65 78 69 74 3d 32 0a` (`exit=2\n`), with pipeline exit 0. Thus the cited digest matches the exact pinned blob bytes.
- No registry or document changes made.