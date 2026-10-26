# U1DiffModels report

Verdict: of 65 files / 17 commits between b11889 and b11906, only tools/server/server-context.cpp and server-models.cpp among the 16 population paths changed (commit c6fb3b5be, mtmd capabilities refactor); no population row depends on the change. Server-context ranges shift +3; S479 unchanged.

Evidence (read-only git on /fast/scratch/hyaku/kama-r46/L1/llama.git; scripts inline, run from scratch):
- `git diff --stat d854d98.. 4d71b42..` -> 65 files; `-- common tools/server` -> 3 files (server-context.cpp 15, server-models.cpp 2, tests/utils.py 2); common/ no change.
- `git rev-parse <commit>:<path>` for the 14 other population paths: blob ids equal at both commits.
- `git diff -U0` hunks, server-context.cpp: 1014,1020,1024,1399,1708,5130 (b11889 coords), net +3; server-models.cpp: 536 only (comment). No population range intersects.
- Python check: all 26 server-context range pairs and the 2 server-models pairs: b11889 text == b11906 text at +3 / +0; pin text == b11906 text for S042 S060 S109 S114-S125 S133 S138 S479 (S121 modulo indentation, which the counter's text-equal strips). S037/S043/S108 differ pin vs release (b11889 holds-reworded), file blob identical to b11889.
- Behavioural check: has_cap_chat/has_cap_tts/allow_* unchanged semantics; no row cites them.
- Defects found: none. Note for the ledger author: reuse b11889 release_lines +3 on server-context rows.
- Tools installed: none.

Full map: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/U1DiffModels/map.md
