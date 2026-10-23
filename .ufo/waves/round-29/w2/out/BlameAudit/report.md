# BlameAudit — round 29 w2

Seat: BlameAudit. Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. No lane files mutated. No tools installed.

## Question

For each of the 11 correction rows under `## Round 29 — self-assessment corrections` in the working-tree `SCORECARD.md`, does the commit that `git blame --line-porcelain` names for that statement's line at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` equal the 10-hex field embedded in the row sid (`SA29:<file>:<class>:<hash10>:<idx>`)?

## Verdict

**11/11 mismatch.** None of the 10-hex sid fields is a prefix of the blame commit, and none resolves as a commit. The field is `sha256(line-at-base).hexdigest()[:10]`, not a revision prefix. The separate **W** column (8 hex) **does** match the blame commit on all 11 rows.

Confidence: high.

## Axes

1. Blame commit vs sid hash10 (the assigned comparison) — all mismatch.
2. What the hash10 actually is — sha256 of the base line, all 10 distinct lines match.
3. Table W column vs blame commit — all 11 match (8-hex prefix).

## Evidence

Correction rows (working tree), lines 1454–1464 of `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`. Exactly 11 rows; every `file` is `SCORECARD.md`. "line at base" values: 20, 20, 192, 211, 740, 823, 824, 833, 834, 1349, 1375.

Command (line ranges are the table's base line numbers; porcelain final-line field echoes them):

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin blame --line-porcelain \
  -L 20,20 -L 192,192 -L 211,211 -L 740,740 -L 823,824 -L 833,834 \
  -L 1349,1349 -L 1375,1375 \
  2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d -- SCORECARD.md
```

The commit named for a line is the 40-hex at the start of its porcelain header (same field `count-c1.py` `blame()` keeps: `^([0-9a-f]{40}) \d+ \d+`, `.ufo/waves/round-29/count-c1.py:128-136`).

| base line | porcelain commit |
|---|---|
| 20 | `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` |
| 192 | `1e41928aba2b81dd65ea75084918a7fadf453720` |
| 211 | `40660352d4a9eb00a5d6195f0f064f5c64618143` |
| 740 | `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` |
| 823 | `7229fa95eb122310e9e5334ad799ee3006293ebd` |
| 824 | `7229fa95eb122310e9e5334ad799ee3006293ebd` |
| 833 | `7229fa95eb122310e9e5334ad799ee3006293ebd` |
| 834 | `7229fa95eb122310e9e5334ad799ee3006293ebd` |
| 1349 | `7f84cd0e7662432b7b93e7586f86a40b06e5fdae` (header `7f84cd0e… 1338 1349 1`: origin line 1338, final line 1349) |
| 1375 | `d183ec572a5eed5bedeb4bce0da02707d51df3dd` |

Sid construction in the frozen counter (not a revision):

```python
# count-c1.py:179 and :226
lsha = hashlib.sha256(line.encode()).hexdigest()[:10]
sid = f"{fname}:{cls}:{lsha}:{k}"
```

Recomputed on `git cat-file -p 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` (104553 bytes, no CR, 1441 lines after dropping a trailing empty split, same split as `extract()`). `sha256(line.encode()).hexdigest()[:10]` equals the sid hash10 on every named line: `f4c42debcc`, `980355388a`, `4f8083e30a`, `312b3e69b1`, `0ccd533544`, `4c5d902830`, `f1021c03db`, `a7e98b1030`, `1c6c1f3e4c`, `17a7db7c81`.

`git rev-parse --verify --quiet <hash10>^{commit}` returns exit 1 for all ten distinct hash10 strings (empty stdout/stderr). They are not commit prefixes in this repo.

## Table

`match` = blame commit startswith the sid's 10-hex. The row's W cell is recorded below the table; it is the first 8 hex of the blame commit on every row (not the assigned comparison).

| sid | blame commit | match |
|---|---|---|
| `SA29:SCORECARD.md:Q:f4c42debcc:0` | `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` | mismatch |
| `SA29:SCORECARD.md:Q:f4c42debcc:2` | `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` | mismatch |
| `SA29:SCORECARD.md:P:980355388a:0` | `1e41928aba2b81dd65ea75084918a7fadf453720` | mismatch |
| `SA29:SCORECARD.md:Q:4f8083e30a:0` | `40660352d4a9eb00a5d6195f0f064f5c64618143` | mismatch |
| `SA29:SCORECARD.md:P:312b3e69b1:0` | `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` | mismatch |
| `SA29:SCORECARD.md:Q:0ccd533544:0` | `7229fa95eb122310e9e5334ad799ee3006293ebd` | mismatch |
| `SA29:SCORECARD.md:Q:4c5d902830:0` | `7229fa95eb122310e9e5334ad799ee3006293ebd` | mismatch |
| `SA29:SCORECARD.md:Q:f1021c03db:0` | `7229fa95eb122310e9e5334ad799ee3006293ebd` | mismatch |
| `SA29:SCORECARD.md:Q:a7e98b1030:0` | `7229fa95eb122310e9e5334ad799ee3006293ebd` | mismatch |
| `SA29:SCORECARD.md:P:1c6c1f3e4c:0` | `7f84cd0e7662432b7b93e7586f86a40b06e5fdae` | mismatch |
| `SA29:SCORECARD.md:P:17a7db7c81:0` | `d183ec572a5eed5bedeb4bce0da02707d51df3dd` | mismatch |

W column vs blame (all match): `ea72c3ea`, `ea72c3ea`, `1e41928a`, `40660352`, `c6dc46fa`, `7229fa95`, `7229fa95`, `7229fa95`, `7229fa95`, `7f84cd0e`, `d183ec57`.

## Reading

The assigned equality does not hold, and it cannot hold under the frozen extractor: the 10-hex in `SA29:<sid>` is a line digest, while the writing revision is the blame commit stored in the row's W cell (8 hex here). Calling that digest a revision prefix is a mislabel of the sid, not a wrong blame. Rows `:0` and `:2` on line 20 share one line, one digest, and one blame commit; the index is the per-class match index on that line (`k` in `extract()`), not a second revision.

## Unknowns

None on this comparison. Full-file blame without `-L` was not re-run; `-L` still prints the origin commit and the final line number at the base, which matched every table line.
