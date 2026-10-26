# X4HexUp2 — round-47 hexrun census, token range a4b4feae..e1e006f1

**Verdict:** the range is closed — 6 upstream rows for the llama.cpp objects the b11889 recheck ledger cites plus 1 row for the b11889 tag commit take the census from `unknown=22` to `unknown=16` (`upstream_ok` 68 → 74, `ledger_bad` 0); a further 2 advisory rows outside the llama.cpp set take it to `unknown=14`, and no token sorting in `a4b4feae..e1e006f1` is left unknown. The rows only classify once the evidence files are **committed as blobs at the measured tip**: at a tip where they are merely present in the worktree the same ledger scores `ledger_bad=6`.

## 1. Baseline reproduced

```
$ git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ python3 kama-shokunin/tools/hexrun-census.py scan --repo $S/lane \
    --rev 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --details
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22
exit 1
```
This is the D4 state (22 at `3a09a1d9`, 21 at the round-46 tip) on my own clone, before any of my rows.

Range membership, from the frozen `--details` stream (`detail: <token> len=40 occurrences=N class=unknown`, 22 lines) intersected with the range and with the blob cells of `registry/release-recheck-b11889.tsv` (fields 5 and 6, 29 distinct blobs):

| token | in b11889 ledger | ledger line | path (row) | repo | class |
|---|---|---|---|---|---|
| a4b4feae…159a | release_blob | 19 (S111) | common/common.cpp | ggml-org/llama.cpp | primary |
| bf3e0838…b022 | pin *and* release blob | 12 (S059) | gguf-py/gguf/gguf_reader.py | ggml-org/llama.cpp | primary |
| c4ce9072…7016 | release_blob | 9 (S047) | tools/server/server-queue.cpp | ggml-org/llama.cpp | primary |
| d5a66a49…c4c4 | release_blob | 15, 38, 40 (S107, S130, S132) | src/llama-context.cpp | ggml-org/llama.cpp | primary |
| e1e006f1…45d6 | release_blob | 92 (S479) | tools/server/server-models.cpp | ggml-org/llama.cpp | primary |
| d854d98b…326d | — (the b11889 commit itself) | corpus/SOURCES.md:235 | tag target b11889 | ggml-org/llama.cpp | primary |
| b0fd7b7f…4025 | — | SCORECARD.md:2350 | fleet commit | VeigaPunk/shokunin | advisory |
| c03c1a14…c222 | — (recheck-r45.tsv:5,6 `new_ref`) | registry/recheck-r45.tsv:5,6 | linux v7.3 ref | torvalds/linux | advisory |

## 2. Verification (each token is the blob of that row's path at that row's commit)

Upstream clone (scratch, nothing written outside it):
`git clone --filter=tree:0 --bare https://github.com/ggml-org/llama.cpp.git up`

```
git -C up ls-remote --tags origin refs/tags/b11889
d854d98bae598388ecea1ed84396587e5edc326d	refs/tags/b11889
git -C up ls-remote --tags origin refs/tags/b11906
4d71b42fd87db24b8b7c808c151b713aa4459cfd	refs/tags/b11906

git -C up rev-parse d854d98bae598388ecea1ed84396587e5edc326d:common/common.cpp
a4b4feaee3c066dbc2a4e72d6089dfcd8e0e159a
git -C up rev-parse d854d98bae598388ecea1ed84396587e5edc326d:gguf-py/gguf/gguf_reader.py
bf3e083800b01c822989c096f0d875dc750ab022
git -C up rev-parse d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-queue.cpp
c4ce90721b9498506a7b0b13841fb5cf2ede7016
git -C up rev-parse d854d98bae598388ecea1ed84396587e5edc326d:src/llama-context.cpp
d5a66a49990b6ea12bbfb887e19399ad8944c4c4
git -C up rev-parse d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-models.cpp
e1e006f1018fdcfd76f9f20f5a1a638c7f3245d6

git -C up cat-file -t <each of the five>          -> blob   (d854d98b -> commit)
git -C up rev-parse 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad:<same five paths>
b59e66e3… / bf3e0838… / 3352c3cb… / 9ee64b56… / 606eab4f…   (= each row's pin_blob cell)
```

Both directions agree with the ledger cells, so path↔commit↔blob pairing is consistent, not just the digest. Raw transcript: `w1/out/X4HexUp2/verify-upstream.txt`.

Advisory tokens, verified separately (commands and outputs inside each evidence file):
* `b0fd7b7f…` — `git -C /home/vgpnk/Projects/shokunin cat-file -t` → `commit`, `rev-parse ^{commit}` → itself, `branch -r --contains` → `origin/main`, `origin/master`, remote `https://github.com/VeigaPunk/shokunin.git`.
* `c03c1a14…` — `curl -sS -o /dev/null -w '%{http_code}' -I https://raw.githubusercontent.com/torvalds/linux/c03c1a14…/net/ipv6/tcp_ipv6.c` → `200`. It is a **commit** ref, not a blob: `git hash-object` of the lane byte copies `.ufo/waves/round-45/c1/upstream/S048_tcp_ipv6.c/new` and `S048_in6.h/new` gives `7fa4ed2f…` and `5a47339e…`, and `.ufo/waves/round-45/c1/upstream/fetch.log` lines 8 and 10 fetch it as the raw ref for both S048 paths.

## 3. Gate

Fixture = a fresh repo whose object store is an `alternates` link to the lane's read-only `.git/objects` (no second lane clone, no checkout of 272 MB); the tree is the lane tree at `3a09a1d9` plus the evidence files committed with an explicit fixture identity (`X4HexUp2 fixture <X4HexUp2@fixture.invalid>`), `git rev-parse --show-toplevel` asserted equal to the fixture dir before the commit.

```
# fixture tip 751d4d9d44d349af5f51ee587ec29f88d7f1058e
python3 kama-shokunin/tools/hexrun-census.py scan --repo $D --rev 751d4d9d… --ledger $S/ledger-base.tsv
   tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22
python3 … --ledger $S/ledger-with-primary.tsv      # frozen ledger + the 6 rows above
   tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=74 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=16
python3 … --ledger $S/ledger-with-all.tsv          # + the 2 advisory rows
   tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=76 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=14
```

`exit 1` in all three runs (14 unknown remain, all outside the range). `tokens`/`distinct` are unchanged, so appending rows adds no population. Per-token detail for the 8 rows: all `class=upstream_ok` in the `all` run (`w1/out/X4HexUp2/gate/all.details.txt`). No token with prefix in `[a4b4feae, e1e006f1]` is unknown in any of the three runs.

## 4. Integration caveats (measured, not asserted)

1. **Evidence must be a blob at the measured tip.** Same ledger, run against the lane clone at `3a09a1d9` where the evidence files exist only as untracked worktree files:
   ```
   … --repo $S/lane --rev 3a09a1d9… --ledger $S/ledger-with-primary.tsv
   tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=6 unknown=16
   ```
   The six rows flip to `ledger_bad` (the failing class), not `unknown` — `tools/hexrun-census.py:248` (`upstream_ok` reads `ctx.evidence`, filled only from blobs at REV at `:311`). Ship the evidence files in the same commit as the ledger rows.
2. **One row per token.** A ledger copy that carried a token twice scored `ledger_bad=79` against 0 for the de-duplicated copy (`tools/hexrun-census.py:265`, `if len(rows) > 1: return "ledger_bad"`). With several seats drafting rows this round, the integration must de-duplicate by token before adding rows; my advisory rows say so in their `note` cell.
3. The evidence files live under `.ufo/`, which `is_document` excludes (`tools/hexrun-census.py:96`), so they cannot inflate the token population.

## 5. Finding: `registry/recheck-r45.tsv` mixes commit refs into a blob-shaped column

`registry/recheck-r45.tsv:5` and `:6` (`S048:tcp_ipv6.c`, `S048:in6.h`) put `c03c1a14507dfaf8b856c2608f9ac216021fc222` in `new_ref` beside the pin side `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`. Both are **commits**, not file blobs — `git hash-object` of the stored byte copies gives `7fa4ed2f…` and `5a47339e…`, while `fetch.log:8,10` fetch them as raw commit refs. The column name says nothing about the object type, and the census therefore sees a bare hex run. Command that shows it:

```
$ git cat-file blob 3a09a1d9:/.ufo/waves/round-45/c1/upstream/S048_tcp_ipv6.c/new | git hash-object --stdin
7fa4ed2fd4f166a9c0454c2f4ee4cd3b541b4c84      # != c03c1a14…, != pin 8d3ae592…
```
Proposed fix (not applied — the file is frozen): retitle the `pin_ref`/`new_ref` header cells to `pin_ref (commit|blob)`/… or add a row per ref to `registry/hexrun-ledger.tsv`; the advisory row in `w1/out/X4HexUp2/rows-advisory.tsv` is the ready-made ledger side (repo `torvalds/linux`, evidence `curl -I` → 200).

## 6. What stays unknown (all outside my range)

14 tokens remain after the advisory rows: `0a14a962`, `20259355`, `27384beb`, `277ee2ef`, `463f498c`, `4ab280a6`, `547934af`, `6105c587`, `66ab8482`, `70e6cd5f`, `80a9f2d7`, `8bca0cf3`, `9706b3ac`, `ec82db00` — every one sorts below `a4b4feae` or above `e1e006f1`. Five of them (`0a14a962`, `27384beb`, `4ab280a6`, `80a9f2d7`, `9706b3ac`) already have evidence files written into `hexrun-evidence/` by other seats this wave, so they are in flight, not mine.

## 7. Files, tooling, scratch

Written:
* `.ufo/waves/round-47/hexrun-evidence/{a4b4feae…,bf3e0838…,c4ce9072…,d5a66a49…,e1e006f1…,d854d98b…,b0fd7b7f…,c03c1a14…}.txt` — 8 evidence files (command, output containing the token, repo name).
* `.ufo/waves/round-47/w1/out/X4HexUp2/rows.tsv` — the 6 primary rows (7 TAB cells each, header present).
* `.ufo/waves/round-47/w1/out/X4HexUp2/rows-advisory.tsv` — the 2 advisory rows.
* `.ufo/waves/round-47/w1/out/X4HexUp2/ledger-append-primary.proposed.diff` / `ledger-append-all.proposed.diff` — the rows as unified diffs against `registry/hexrun-ledger.tsv` (frozen file **not** edited).
* `.ufo/waves/round-47/w1/out/X4HexUp2/gate/{base,primary,all,uncommitted-evidence}.txt` and `.details.txt`, `verify-upstream.txt`, `evidence/` (byte-identical copies, sha256 checked).

Read-only observation for integration order (not mine, not touched): at the time of writing, the lane worktree has two tracked files modified — `tests/llamacpp-live/check-receipt.py` and `tools/gguf-identity.py` — while `3a09a1d9` is the measured build tip. My rows are measured against the tip commit tree, not the worktree, so they are unaffected.

No installs were needed (python3, git ≥ 2.4x, curl present); nothing was added to any PATH directory and no pacman transaction was run. Scratch `/fast/scratch/hyaku/kama-r47/X4HexUp2` (one `--shared` lane clone, one bare tree-less upstream clone 16 MB, one fixture repo) was removed after the copies above were taken.
