# EX03 — round-82 receipt-revision replay (executor)

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; clone `<S>/clone` (`git clone --shared`, `rev-parse --show-toplevel` = `<S>/clone`). Each receipt: `git checkout --detach <its # rev:>` in that clone + its `# cmd:` verbatim from the clone root; nothing copied in; `# rev:`/`# cmd:`/`# defect:` and `EXIT=` excluded from comparison.
Lane tip `bacae0726d7c53455bd083bc6d478bbcd6e7fffc` at first read → `384ef1d5bcbf737183571398ecb0955ea5074609` at last (three L1 advances during the seat, touching only SCORECARD.md/PROVINCE.md; `git diff bacae072 origin/master -- measured/` empty). All 5 named revs are ancestors of every tip.
15 files under `measured/`; 12 carry `# rev:` (headerless: `census-validate.out`, `late-rows-round82.tsv`, `late-rows-round82.err`). Table paths are relative to `<lane>/.ufo/waves/round-82/measured/`; `EX03.json` carries each absolute path, command and both exits.

| receipt | rev | EXIT decl/run | verdict | note |
|---|---|---|---|---|
| after/c1-green.out | a251cbab | 0/0 | reproduces | byte-identical |
| after/c1-json.out | 962bd251 | 0/1 | differs | 30 of 44 lines; run red (mismatches=1 unbacked=1) |
| after/c1-selftest.out | a251cbab | 0/0 | differs | body is the last of 20 lines |
| after/c2-debt.out | a251cbab | 0/0 | reproduces | byte-identical, pending=2 |
| after/c2-debt-selftest.out | 5fe3c58c | 0/0 | reproduces | byte-identical |
| after/c2-late-delta.out | a251cbab | 0/0 | reproduces | byte-identical |
| after/c2-selftest.out | b0064016 | 0/0 | reproduces | byte-identical, 13 lines |
| before/c1-enum.out | bfdd7a70 | 1/— | unrunnable | tool absent at rev (added b0064016) |
| before/c2-debt-base.out | bfdd7a70 | 1/1 | reproduces | byte-identical |
| before/c2-late-delta-base.out | bfdd7a70 | 1/— | unrunnable | tool absent; body unreachable from any rev |
| control/c1-no-corrections.out | a251cbab | 0/1 | differs | last of 7 lines; EXIT=0 is false |
| defects/c2-debt-register-level-before.out | b0064016 | 1/1 | reproduces | `bad_rows=15` red-before TRUE |

**7 reproduces · 3 differs · 2 unrunnable.** First differing line, receipt | rerun: `c1-json` #31 `<end of body>` | `    {`; `c1-selftest` #1 `SELFRECORD_R81_SELFTEST pass=19 fail=0` | `PASS honest mismatches=0 unbacked=0 corrected=5`; `c1-no-corrections` #1 `SELFRECORD_R81 claims=6 mismatches=5 corrected=0 unbacked=0` | `SELFRECORD_R81_FACT F1 unanswered declared=sc81c2-pending=1 witness=sc81c2-pending=4`.
Red-before claim: `defects/c2-debt-register-level-before.out` at `b0064016` really prints `bad_rows=15` (31/31 body lines, sha256 match, exit 1); its complement `before/c2-debt-base.out` at `bfdd7a70` reproduces `bad_rows=0 unaccepted=5`, so the red-before/repair pair is genuine.

## Findings
1. `before/c1-enum.out` and `before/c2-late-delta-base.out` name `bfdd7a70`, which holds neither round-82 tool (both added in its direct child `b0064016`). `c1-enum`'s body reproduces at `b0064016` (`stale=5`, exit 1), so only its header is wrong; `c2-late-delta-base`'s `new=0 bad=15` exists at no committed rev — `b0064016` already carries the 15 rows (`new=15 bad=0`) — so it was a worktree-only capture.
2. `control/c1-no-corrections.out` records `EXIT=0`, but the command exits 1 at `b0064016`, `962bd251` and `a251cbab`; the frozen plan's control 2 requires exit 1. The instrument is right, the receipt is wrong.
3. `after/c1-json.out` names `962bd251` (pre-repair) and is a 30-of-44-line prefix of a red run (`mismatches=1 unbacked=1`, exit 1) filed under `after/` with `EXIT=0`; `--json` is green/exit 0 only from `a251cbab`, where no receipt was taken.
4. `after/c1-selftest.out` is a tail capture: its claim `pass=19 fail=0` is corroborated (19 PASS lines), but the receipt cannot print its own body from its rev.
5. Supplementary, not a verdict: at `384ef1d5` the three claim commands still print their target first lines, exit 0.
