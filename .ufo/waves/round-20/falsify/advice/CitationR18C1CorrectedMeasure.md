VERDICT: confirm - registry row, bound-document cite token, and pinned blob digest match exactly.

- Registry row `registry/required-citations.json:100-106` (`:101-105` fields): id `r18-c1-corrected-measure`; rev `1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e`; path `.ufo/waves/round-18/runs/c1-measure.json`; SHA-256 `83e8a1ed95d0c71739aef9f5e1295e14f05d9cc004b56ad19c796ebe1864e1b3`; doc `corpus/lessons/round-18.md`.
- Bound document token: `corpus/lessons/round-18.md:470` is `cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/c1-measure.json, sha256=83e8a1ed95d0c71739aef9f5e1295e14f05d9cc004b56ad19c796ebe1864e1b3)`, matching the row's revision, path, and digest.
- Pinned bytes: ran `set -o pipefail && git show 1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e:.ufo/waves/round-18/runs/c1-measure.json | sha256sum`; output was `83e8a1ed95d0c71739aef9f5e1295e14f05d9cc004b56ad19c796ebe1864e1b3  -`, matching the row and token.
- No registry or document changes made.