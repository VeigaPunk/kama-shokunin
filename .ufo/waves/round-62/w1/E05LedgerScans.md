# E05LedgerScans — digest-ledger + hexrun-census scans at the round-62 tip (w1)

Seat: leaf executor (operability, judged on operability). Item: run

```
python3 tools/digest-ledger.py scan --repo . --rev master [--details]
python3 tools/hexrun-census.py scan --repo . --rev master --details
```

and report both token lines, confirming `unknown=0` and `ledger_bad=0`. This is a
measured instrument check, not a verdict on C1/C2.

## Environment / pinning

| fact | value |
|---|---|
| lane tip (`git rev-parse master`) | `65d7cad0fce90e34de37527cde22e97b63b118bf` — "round-62: live request-plane tool, capability-claims registry, canonical list + ledger classifications" |
| `tools/digest-ledger.py` @ tip | clean, sha256 `7f51d87259499a2a2b9923edeba30c0b9c6e7948b910cd10aa39b8af2ba10784`, last commit `be8169a6` |
| `tools/hexrun-census.py` @ tip | clean, sha256 `40c81cd8624eb50b6a2c26c6b5bbb2237459c03334cb87e060a331c8ccca0001`, last commit `c328cadf` |
| `registry/digest-ledger.tsv` @ tip | clean, sha256 `78d32f4f81bc0b9e475b3d534d6d5c82604d7a7dee6c6825fca8f083aa6e083c`, 20 lines (header + 19 rows), last commit `65d7cad0` |
| `registry/hexrun-ledger.tsv` @ tip | clean, sha256 `27d3dfcce43df1bfcb57fd93b4d0cc3f206ba2276a87834faddc2aa8c4730957`, 124 lines (header + 123 rows), last commit `65d7cad0` |
| python3 / git | 3.14.8 (GCC 16.2.1) / 2.56.0 |
| scratch | `/fast/scratch/hyaku/kama-r62/w/E05LedgerScans/` (created with `mkdir -p`, passed explicitly; no `TMPDIR` inheritance) |

Working tree carries two pre-existing modifications from other seats (`M corpus/SOURCES.md`,
`M tools/round62-c1-counter.py`). Neither is read by these scans: both take `--repo . --rev
master` and enumerate **committed** blobs at the rev, so the token line is a function of the
tip tree only. The four instrument/ledger files above are byte-identical on disk and at tip
(`git status --porcelain` empty for them; `git cat-file -p master:<path> | sha256sum` equals
the on-disk digest for all four).

Scans are read-only (`git ls-tree`/`cat-file --batch`); they write nothing and create no
temporary files, so no sandbox clone was required and no lane file was touched.

## Token lines (verbatim)

`python3 tools/digest-ledger.py scan --repo . --rev master --details` — exit **0**

```
tokens=143 blob=125 external_ok=9 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0
```

`python3 tools/hexrun-census.py scan --repo . --rev master --details` — exit **0**
(stdout is the one-line contract; `--details` writes per-token lines to stderr)

```
tokens=2051 distinct=392 lane_oid=271 md5_blob=1 upstream_ok=108 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0
```

**Confirmation asked for: `unknown=0` and `ledger_bad=0` on both scans.** Also, digest
`wrong_unflagged=0`. Exit 0 on both is exactly the tools' contract for
`ledger_bad + unknown (+ wrong_unflagged for digest) == 0`.

Reproduction at the frozen tip in the counters' own `TIPREV` form
(`--repo <lane> --rev 65d7cad0fce90e34de37527cde22e97b63b118bf`) produces byte-identical
token lines (`digest-scan-tiprev.txt`, `hexrun-scan-tiprev.txt`), and a second pass
(`*-pass2.txt`) is identical too: the measurement is stable and rev-pinned, not
working-tree-dependent.

## Details — every flagged token is a declared ledger row

`--details` on digest-ledger prints only unexplained/flagged tokens: exactly 2 lines, and
`blob+external_ok+external_absent+unverifiable+wrong_flagged = 125+9+1+7+1 = 143 = tokens`.
hexrun-census prints 392 per-token lines (`271+1+108+9+3+0 = 392 = distinct`), so the class
counts and the detail lines agree one-for-one — no token is counted in one class and
reported in another.

| scan | token | class | ledger row | substance |
|---|---|---|---|---|
| digest | `5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2` | `wrong_flagged` | `registry/digest-ledger.tsv:7` (`wrong`, `correct=5585f6027df2…50f2`) | S472 sglang output digest as first written; known wrong, correction recorded in the amendment + round-38 lesson |
| digest | `bcc55c92e8456e9515f58309953cf005b383a5b93c2dcaf3e68a2b09e8f7ea3e` | `external_absent` | `registry/digest-ledger.tsv:5` (`external`) | over-1-MiB fetched dockerfile.html; the declared path lives only in the parked worktree, absent in this checkout — declared external and honestly counted absent, not `ledger_bad` |
| hexrun | `0957ce619789d13d894ef21bc863486bcb35b56c` (40) | `wrong_flagged` | `registry/hexrun-ledger.tsv:45` | documented hand-splice exemplar (404 on both repos, `cat-file` rc128), correction `0957ce619789d13bb5779606078fa1498114d2c7` |
| hexrun | `35ce313293052f8362e0829e7512bc9bc3d336c` (39) | `wrong_flagged` | `registry/hexrun-ledger.tsv:74` | truncated tag oid; correct 40-hex `35ce313293052f8362e0829e7512bc9bc3d336c9` |
| hexrun | `907cdcc0a76f8656fde4574c0c50725fcea42fa9` (40) | `wrong_flagged` | `registry/hexrun-ledger.tsv:113` | one-digit lane-tip typo; correct `907cdcc0a76f8656fde4574c0a50725fcea42fa9` |

The 9 `unverifiable` hexruns are each a declared row with its reason, not silence
(`registry/hexrun-ledger.tsv` line → token): 34 `efb50993…` (Hyprland runtime-dir token in a
pasted `ss` line), 67 `61e82ee2…`, 68 `860f26ac…`, 69 `932ea3dc…`, 70 `87eb156b…` (MD5 of
earlier `tools/*.sh` / `registry/endpoint-consumers.tsv` blobs), 71 `0000…0000`, 72
`0000…01000000` (`/proc/net/tcp6` address words, not digests), 73
`f7a779ba0a3544dc9e3673c7eb0b3d77` (mission id), 75 `3ad0df68…4ff` (65-char over-long run in
a sha256 slot). The single `md5_blob` and the 108 `upstream_ok` runs resolve mechanically
(MD5 of a committed blob; a run that a committed evidence file contains with its `repo` cell
text).

## Why the zero is measured, not vacuous

Both token-line fields asserted zero are live. Four dir-mode fixtures in scratch (no git, no
ledger beyond the fixture's own) drive each field nonzero and flip the exit to 1:

| fixture | command | line | exit |
|---|---|---|---|
| one fabricated 64-hex citation, no ledger row | `digest-ledger.py scan --dir …/neg/du` | `tokens=1 … ledger_bad=0 … unknown=1` | 1 |
| duplicate digest-ledger rows for one token | `digest-ledger.py scan --dir …/neg/dl` | `tokens=1 … ledger_bad=1 … unknown=0` | 1 |
| one fabricated 40-hex citation, no ledger row | `hexrun-census.py scan --dir …/neg/hu` | `tokens=1 distinct=1 … ledger_bad=0 unknown=1` | 1 |
| hexrun ledger row with an unknown class | `hexrun-census.py scan --dir …/neg/hl` | `tokens=1 distinct=1 … ledger_bad=1 unknown=0` | 1 |

The tip populations behind the zeros are large and spread across all classes (143 digests,
392 distinct hexruns, 12 non-`blob`/non-`lane_oid` classes exercised), so `unknown=0
ledger_bad=0` is a computed classification result over a non-empty population, not an empty
scan.

Supplementary instrument health (same tip, stock python): `python3 tools/digest-ledger.py
selftest` → `selftest pass=11 fail=0` (exit 0); `python3 tools/hexrun-census.py selftest` →
`selftest pass=18 fail=0` (exit 0).

## Binding to the C2 rows (context, not a verdict)

- `registry/capability-claims-r62.tsv:9` (`digest-ledger`) and `:10` (`hexrun-census`) bind
  exactly `python3 %T/tools/<tool> scan --repo %R --rev TIPREV` with frozen pattern
  `unknown=0`, verdict `true`, observed `unknown=0`.
- `tools/round62-c2-counter.py:90,95` carry the same run templates; `:186` substitutes
  `%R`→repo and `TIPREV`→tip hash. My `--rev <tip>` run is that bound run verbatim, and the
  frozen pattern `unknown=0` is present in both token lines — so both bound rows re-emit
  their frozen pattern at `65d7cad0`.
- `SCORECARD.md:3272` "**Capabilities — canonical list as of round 62**" carries each of
  `digest-ledger` and `hexrun-census` exactly once with its frozen prefix text.

This seat does not measure the counters' predicates, the 12-row sensitivity/control matrix,
or C1's request plane; it reports the two scans only.

## Tool installs

None. No pacman transaction was attempted (host-wide pause); no uv/npx/binary install was
needed; stock `python3 3.14.8` and `git 2.56.0` ran every command.

## Receipts (durable)

Under `.ufo/waves/round-62/w1/out/E05LedgerScans/`:

- `digest-scan-details.txt` — digest token line + its 2 `detail:` lines (stdout, verbatim)
- `digest-scan-tiprev.txt`, `digest-scan-pass2.txt` — same line at `--rev <tip>` and on a second pass
- `hexrun-scan-tokenline.txt`, `hexrun-scan-tiprev.txt`, `hexrun-scan-pass2.txt` — hexrun token line per run
- `hexrun-scan-details.txt` — all 392 per-token `detail:` lines (stderr, verbatim)
- `neg-controls.txt` — the four sensitivity fixtures and their lines/exits
- `digest-selftest.txt`, `hexrun-selftest.txt` — `selftest pass=11 fail=0`, `pass=18 fail=0`

Scratch `/fast/scratch/hyaku/kama-r62/w/E05LedgerScans/` (`digest-*`, `hexrun-*`, `neg/`)
was `rm -rf`'d after copying. Lane checkout read-only; the only files this seat wrote under
the lane are this report and the receipts above.

## Tally

```
digest-ledger scan --repo . --rev master  tokens=143 blob=125 external_ok=9 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0  exit=0
hexrun-census  scan --repo . --rev master  tokens=2051 distinct=392 lane_oid=271 md5_blob=1 upstream_ok=108 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0  exit=0
unknown=0 ledger_bad=0 on both at tip 65d7cad0fce90e34de37527cde22e97b63b118bf
```
