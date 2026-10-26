# X4HexUp1 — round 47: the b11889-ledger upstream blobs in [0a14a962..9706b3ac] are ledgered

**Verdict: PASS.** All 5 census-unknown tokens in my range that sit in `registry/release-recheck-b11889.tsv` are confirmed git blobs of their row's path at b11889 in `ggml-org/llama.cpp`; with my 5 ledger rows plus their committed evidence the census goes **unknown 22 → 17** (`upstream_ok` 68 → 73, `ledger_bad` 0 → 0). Nothing was edited in the lane: rows are drafted in `rows.tsv` and evidence lands in the shared `hexrun-evidence/` directory for the L1 to commit at integration.

## Scope

Baseline at the frozen lane tip, unmodified ledger (exit 1):

```
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ python3 kama-shokunin/tools/hexrun-census.py scan --repo $S/lane --rev 3a09a1d93dcc16799cf6c4b48786e6440af134c4
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22
rc=1
```

`--details` gives 22 `class=unknown`; 13 sort inside my range `[0a14a9620961ff627348952112b4a9a6a0513c43 .. 9706b3ac58d5c30bdbf06c17b61151070421a64a]`, 9 after it. Of those 13, exactly **5** appear in `registry/release-recheck-b11889.tsv` (checked cell-by-cell against all 11 columns, so I know the column): that is my assignment. The other 8 in-range tokens are in no b11889 row and I left them alone (inventory at the end for the L1).

## Upstream identity

The `release` cell of every row is the string `b11889`; the ledgers elsewhere call b11887 a lightweight tag, and b11889 is the same shape:

```
$ git init -q --bare up
$ git -C up fetch --filter=blob:none --depth=1 https://github.com/ggml-org/llama.cpp.git refs/tags/b11889:refs/tags/b11889
$ git -C up cat-file -t b11889
commit
$ git -C up rev-parse 'b11889^{commit}'
d854d98bae598388ecea1ed84396587e5edc326d
```

So the row's "release commit" is `d854d98b…`. The two pin commits involved (`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, `ad1b88ca0d37a2171efba1c04f1a3531c78f1b52`) were fetched bloblessly the same way.

## The five tokens

`rev-parse <commit>:<path>` in the blobless bare clone; every one matches the ledger cell and the pin-side cell (the reverse check that the token names the release file and not the pin file).

| token | path | b11889 blob | pin blob (`704366d7` / `ad1b88ca`) | ledger rows |
|---|---|---|---|---|
| `0a14a9620961ff627348952112b4a9a6a0513c43` | `tools/server/server-schema.cpp` | `0a14a962…` MATCH | `54e126aa0c3572895042cd0a8c4faf4a0eb0b9f7` | S140–S173, S190–S191 (36 rows; release_blob at line 46–79, 90–91) |
| `27384bebf697fec4e22df899fdbc345da4e89e91` | `tools/quantize/README.md` | `27384beb…` MATCH | `27384beb…` (identical at `ad1b88ca`) | S015 (line 3; pin_blob **and** release_blob) |
| `4ab280a6196c9dbac0716475eafb53cbbeb35ce4` | `src/llama-kv-cache.cpp` | `4ab280a6…` MATCH | `b7dfadef4638f6221608f48aff0a1f83df281063` | S113 (line 21), S135 (line 43) |
| `80a9f2d7270d072967c9ad243864147cbd1e175e` | `tools/server/server-common.cpp` | `80a9f2d7…` MATCH | `3ea20c3d2f813018d7306751b1b769a374f1a521` | S126 (34), S127 (35), S137 (44), S180–S189 (80–89) |
| `9706b3ac58d5c30bdbf06c17b61151070421a64a` | `common/arg.cpp` | `9706b3ac…` MATCH | `267b84874912508f5ce205916a1abaaf6fd878b8` | S054 (line 10), S056 (11), S110 (18) |

Full command-and-output receipts, each containing its token and the repo name, are in `.ufo/waves/round-47/hexrun-evidence/<token>.txt`. All 36 `0a14a962` rows and all 13 `80a9f2d7` rows were resolved with the same command; the census's own accounting (`occurrences=72` and `26` = the token twice per file across the b11889 and b11906 ledgers) confirms the row coverage.

A by-product worth noting: row S015's `unchanged-file` verdict is corroborated at the object level — the pin and the release blob for `tools/quantize/README.md` are the same object `27384beb…`.

## Gate

Evidence must be a blob **at the census rev**, so I committed it in a fixture clone of the lane at the frozen tip (`git -C $S/fix rev-parse --show-toplevel` = `$S/fix`, verified before the fixture commit), appended my rows to a copy of the ledger, and scanned that commit:

```
$ git -C fix rev-parse HEAD
4db8e535aeab903f136c5cd4b1ebebfbc7f1ef78           # tip 3a09a1d9 + 11 evidence blobs, nothing else

# control: evidence present, ledger unchanged
$ python3 .../hexrun-census.py scan --repo fix --rev 4db8e535…
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   (rc=1)

# gate: evidence present, ledger copy = 83 registry lines + my 5 rows
$ python3 .../hexrun-census.py scan --repo fix --rev 4db8e535… --ledger $S/ledger-v2.tsv
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=73 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=17   (rc=1)

$ ... --details 2>&1 >/dev/null | grep -E '0a14a962|27384beb|4ab280a6|80a9f2d7|9706b3ac'
detail: 0a14a9620961ff627348952112b4a9a6a0513c43 … class=upstream_ok
detail: 27384bebf697fec4e22df899fdbc345da4e89e91 … class=upstream_ok
detail: 4ab280a6196c9dbac0716475eafb53cbbeb35ce4 … class=upstream_ok
detail: 80a9f2d7270d072967c9ad243864147cbd1e175e … class=upstream_ok
detail: 9706b3ac58d5c30bdbf06c17b61151070421a64a … class=upstream_ok
```

**Unknown count drop: 22 → 17 (−5), upstream_ok 68 → 73 (+5), ledger_bad stays 0, tokens/distinct unchanged.** The control leg proves the drop comes from the rows and not from the evidence blobs alone (evidence is `.txt`, so `is_document` at hexrun-census.py:96 never counts them as population; population comes from the `is_document` gate at :322).

## Integration finding (ordering, not a counter defect)

The counter's evidence contract is strict: `upstream_ok` needs `row.evidence` to be a blob path in the tree at REV containing both the token and the repo string (hexrun-census.py:248-256, evidence paths collected at :311-312 and :327-329 from the tree at REV), and any failure falls to `ledger_bad` (hexrun-census.py:257-272). Running the appended ledger against the **unmodified** lane tip — i.e. committing the rows while the evidence is still only in the worktree — shows exactly that:

```
$ python3 .../hexrun-census.py scan --repo lane --rev 3a09a1d9… --ledger $S/ledger-v2.tsv
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=5 unknown=17   (rc=1)
```

So the lane's integration commit must add `registry/hexrun-ledger.tsv` rows **and** `.ufo/waves/round-47/hexrun-evidence/*.txt` in the same commit; rows alone turn 5 unknowns into 5 `ledger_bad` and buy nothing.

Second, mechanical: `resolve` rejects a token with more than one ledger row (hexrun-census.py:265-266), so the 36 rows that share `0a14a962…` (and the 13 that share `80a9f2d7…`) get **one** ledger row each, not one per registry row. My `rows.tsv` therefore has 5 rows; appending it twice would produce `ledger_bad=5`.

No defect found in the frozen counter, preregistration or controls while doing this.

## For the L1 (left untouched, out of my scope)

- **In range but in no b11889 row (8):** `20259355…` and `547934af…` and `66ab8482…` (`registry/recheck-r45.tsv`), `6105c587…` (`SCORECARD.md`, `registry/claim-outcome-ledger.tsv`, the claim-outcome counters), `277ee2ef…` (round-45 lesson), `463f498c…` (round-44 lesson), `70e6cd5f…` (round-43 lesson), `8bca0cf3…` (`corpus/lessons/round-46-verifier-spotcheck.md` — the D4 closure token itself). The three r45 ones are round-45 ledger blobs, not b11889 blobs, so the b11889 ledger cannot cover them.
- **Out of range (9)** all still unknown at the tip, including `d854d98bae598388ecea1ed84396587e5edc326d`, which is the b11889 tag target (19 occurrences) — the release-commit sibling of my five, and the natural next seat.

## Files written

- `.ufo/waves/round-47/hexrun-evidence/0a14a9620961ff627348952112b4a9a6a0513c43.txt`
- `.ufo/waves/round-47/hexrun-evidence/27384bebf697fec4e22df899fdbc345da4e89e91.txt`
- `.ufo/waves/round-47/hexrun-evidence/4ab280a6196c9dbac0716475eafb53cbbeb35ce4.txt`
- `.ufo/waves/round-47/hexrun-evidence/80a9f2d7270d072967c9ad243864147cbd1e175e.txt`
- `.ufo/waves/round-47/hexrun-evidence/9706b3ac58d5c30bdbf06c17b61151070421a64a.txt`
- `.ufo/waves/round-47/w1/out/X4HexUp1/rows.tsv` (5 ledger rows, 7 columns, no header)
- `.ufo/waves/round-47/w1/out/X4HexUp1/gate.txt` (raw gate receipt)

No tool installed or upgraded (nothing needed). Scratch `/fast/scratch/hyaku/kama-r47/X4HexUp1` removed; no `/tmp` path is cited.
