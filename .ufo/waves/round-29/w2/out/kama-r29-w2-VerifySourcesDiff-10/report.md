# VerifySourcesDiff — round-29 w2 verification (seat `kama-r29-w2-VerifySourcesDiff-10`)

## Item under verification

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 2aa46e24 -- corpus/SOURCES.md`:
claimed (a) exactly 4 rows added (S174–S177), (b) zero in-place changes to existing rows,
(c) each new row has 11 cells with no `|` inside cells, (d) ids sequential after S173,
(e) status `mined`, (f) opened `2026-10-23`.

## Verdict: PASS — all six claims verified true. No defects found.

| Claim | Result | Evidence |
|---|---|---|
| 4 rows added, ids S174–S177 | TRUE | diff contains exactly 4 `+` lines, all `| S174 |`…`| S177 |`; `diffstat`: `1 file changed, 4 insertions(+)` |
| zero in-place changes | TRUE | 0 `-` lines in diff; byte-exact check: `base.txt + 4 inserted lines` rebuilds the worktree file and matches its sha256 `85d24ee1…46779f` exactly — no row moved, edited, or re-wrapped, EOF newline preserved |
| 11 cells, no `|` inside cells | TRUE | base header (base line 11) has 11 columns (`id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by`), separator has 11 `---` groups; each new row: strict split ` | ` → 11 cells, raw `|` count → 0 inside cells, escaped `\|` count → 0 |
| ids sequential after S173 | TRUE | base file contains exactly rows S1…S173, all unique, strictly sequential; S174–S177 absent at base; worktree census S1…S177 unique/sequential; new rows sit at worktree lines 186–189, immediately after base row S173 (base line 185) and before the blank + `## Paths` section |
| status `mined` | TRUE | cell 8 = `mined` in all 4 rows |
| opened `2026-10-23` | TRUE | cell 9 = `2026-10-23` in all 4 rows |

## Structural detail (observed, beyond the claim)

- Single hunk `@@ -183,6 +183,10 @@` — the 4 rows are a pure tail-append to the table, inserted after base line 185 (S173), before `## Paths`.
- New-row `kind`=`docs`, `tier`=`A`, `recheck`=`on-release`; `used-by` cells reference `corpus/knowledge/self-assessment-at-writing.md` and `.ufo/waves/round-29/count-c1.py` — consistent with the round-29 C1 corpus purpose.
- Base blob `dccc147`, worktree blob `2ea93a5` (index line `index dccc147..2ea93a5 100644`).

## Commit status of the delta

- `git status --porcelain corpus/SOURCES.md` → ` M corpus/SOURCES.md` (unstaged worktree modification).
- `git log --oneline 2aa46e24..HEAD -- corpus/SOURCES.md` → empty: no commit between base and HEAD touches the file. HEAD = `513eba3ba51a142c9936553e3a85918345eb5c4c` (the data commit). The entire S174–S177 delta is therefore uncommitted attempt-1 worktree state, exactly as inherited.

## Fingerprints

- `git diff 2aa46e24 -- corpus/SOURCES.md` output sha256: `108cd40477e9480405ae4b26f9de1cc80880173705b26c58f7f4326e54b7b217` (6103 bytes).
- Worktree `corpus/SOURCES.md` sha256: `85d24ee1dc8c59563db3e2218ca0ad7d38293a60b05cd98629b8a8b46779f5ab`.
- Base `2aa46e24` resolves to `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` (matches lane base fact).

## Residual risk / gaps

- Scope was the diff's shape and row metadata only. The *content* accuracy of S174–S177 (e.g., claims about git-blame/git-merge-base/git-grep/pretty-formats manuals) is other seats' territory (per-source scouts) — not assessed here.
- `opened`/`recheck`/`status` cell *validity* versus any schema beyond literal values was not checked (header does not define an enum; `mined`/`on-release`/`2026-10-23` match the convention used by existing mined rows S171–S173).

## Tooling

No installs; used stock `git` and `python3` only. Scratch dir `/tmp/kama-r29-w2-VerifySourcesDiff-10/` (diff + base dumps). Lane repo untouched; no index/jj mutations (read-only `git diff/show/log/status/rev-parse` only).
