VERDICT: confirm - The registry pin, round-18 lesson cite token, and pinned Git bytes match exactly.

## Evidence
- `registry/required-citations.json:45-49` identifies `r18-terminal-evidence`, revision `101f3991d3570bc9350fbf9c5561f4be1185699d`, path `.ufo/waves/round-18/build/terminal-evidence.json`, SHA-256 `44b0694d00c03c2b7af9c0f93e7e83aef073be115bb37fc5d8a33051fd2e371f`, and doc `corpus/lessons/round-18.md`.
- `corpus/lessons/round-18.md:462` contains the corresponding token with the same revision, path, and SHA-256: `cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/build/terminal-evidence.json, sha256=44b0694d00c03c2b7af9c0f93e7e83aef073be115bb37fc5d8a33051fd2e371f)`.
- Ran `git show 101f3991d3570bc9350fbf9c5561f4be1185699d:.ufo/waves/round-18/build/terminal-evidence.json | sha256sum`: output was `44b0694d00c03c2b7af9c0f93e7e83aef073be115bb37fc5d8a33051fd2e371f` (match); `wc -c` reported 32075 bytes. The revision resolves to a commit and the path resolves to blob `efe876288f17aa5482c5aaa6bf82354f9f9c7b6f`; direct blob hashing produced the same SHA-256.
- `git merge-base --is-ancestor <rev> HEAD` succeeded; current HEAD was `92b146253fd3a8c4bfade94c909dc63b13d6f4a8`. The worktree copy at the cited path also hashed to the pinned digest.

## Findings
- No mismatch found for the assigned citation row, token binding, or pinned bytes.

## Residual risk and verification gaps
- This verifies only this named citation; it does not establish exhaustive citation coverage or the cited JSON's substantive claims.
- No LSP device/status endpoint was exposed in the available tools. The token was located textually and confirmed by direct reading at line 462; grep output is not treated as semantic proof.
