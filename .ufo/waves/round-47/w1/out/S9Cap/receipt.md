# S9Cap receipt - round-47 canonical capability entries

Seat: S9Cap (scribe, leaf). Lane: kama. Wave: `.ufo/waves/round-47/w1` (attack + frontier).
Lane revision under test: build commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4`;
scratch clone HEAD `46a924e027f05614558c45ff02bf7a94ca57d3e1` (lane tip, one commit after the build).
Lane tree was never written: every edit below lives in the scratch clone.

## Environment

| item | value |
|---|---|
| host | Arch, linux 7.2.11-arch1-1, x64 |
| python | Python 3.14.8 |
| git | git version 2.56.0 |
| scratch | `/fast/scratch/hyaku/kama-r47/S9Cap` (`TMPDIR` set to it; removed at seat end) |
| clone | `git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, `git -C $S/lane rev-parse --show-toplevel` -> `$S/lane` (asserted) |
| packages installed / upgraded | none (nothing was needed; host pacman transactions are paused) |

## Evidence of the draft's contract

`tools/capability-repertoire-audit.py` contract (docstring, lines 1-29): population = every markdown
table with four columns whose last header cell contains "First working round"; canonical = the first
capability table after the line matching `canonical list as of round N**`, highest N winning;
`listed` = canonical names, `observed` = union over the file; `missing = observed - listed`;
`unsubstantiated` = canonical rows with no evidence-cell path token that resolves at the revision;
`met = missing == 0 and unsubstantiated == 0`; exit 0/1/2.

## Runs

| # | command | exit | result | artifact |
|---|---|---|---|---|
| 1 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 3a09a1d9 --out .../caps-baseline.json` | 0 | `listed 10 observed 10 missing 0 unsubstantiated 0 met True` (`canonical_line 2452`, `capability_tables 12`) | `caps-baseline.out`, `caps-baseline.json` |
| 2 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --out .../caps-after.json` (working tree, draft applied) | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (`canonical_line 2683`, `capability_tables 13`) | `caps-after.out`, `caps-after.json` |
| 3 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 81d0ebb4 --out .../caps-tip-committed.json` (tip mode, committed draft) | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | `caps-tip-committed.out`, `caps-tip-committed.json` |
| 4 | `python3 tools/capability-repertoire-audit.py --selftest` | 0 | `CAP_SELFTEST pass=2 fail=0` | `caps-selftest.out` |
| 5 | per-row `path_exists(repo, 3a09a1d9, token)` over all 11 canonical rows (tip semantics) | n/a | every row substantiated; `all_rows_substantiated_at_tip True` | `caps-tip-tokens.out` |
| 6 | `python3 tools/round42-selfdesc-reconcile.py --repo $S/lane --tip 3a09a1d9` | 1 | `r41=1 … retired=0 saturation=0 caps=0 province=0 … mismatches=1` (r41 = stale calibration row, verified below) | `selfdesc-baseline.out` |
| 7 | `python3 tools/round42-selfdesc-reconcile.py --repo $S/lane --tip 81d0ebb4` | 1 | same single r41 detail (stale calibration row: claims 32, tree holds 33) | `selfdesc-good.out` |
| 8 | reconcile at variant `0c661cf3` (PROVINCE edited, coverage hash not re-anchored) | 1 | `r41=2 … mismatches=2`; detail `coverage sha256 PROVINCE.md cited 659a5101… observed 929f3e3e…` | `selfdesc-variant-no-anchor.out` |
| 9 | reconcile at variant `99667497` (canonical table without the PROVINCE edit) | 1 | `r41=1 … province=3 … mismatches=4`; detail names `registry/append-only-contract.tsv`, `tools/round47-append-audit-v2-check.py`, `tools/kama-live-replay.py` | `selfdesc-variant-no-province.out` |
| 9b | reconcile at variant `ae7e2801` (canonical block added, head mirror / §Retired / §Saturation left at round 46) | 1 | `r41=1 … retired=1 saturation=1 caps=1 … mismatches=4` | `selfdesc-variant-no-mirror.out` |
| 10 | `python3 tools/append-only-audit.py --repo $S/lane --to 3a09a1d9` | 1 | `event dd9f5dc6 SCORECARD deleted=31 restored_max=24 partial`; `0718b6ab LOG deleted=2292 restored_max=2292 restored`; `0718b6ab SCORECARD deleted=2421 restored_max=2420 partial`; `QUALITY 375/375 restored`; `README 663/663 restored`; `summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0` | `append-only-v2-at-tip.out` |
| 11 | controls (see `controls.out`), each `capability-repertoire-audit.evaluate(dir, None)` on a constructed tree | 0 | 6 rows, below | `controls.out` |
| 12 | `git ls-tree --name-only <rev> corpus/lessons/ \| grep -c 'verifier-spotcheck\.md$'` for `3a09a1d9` and `46a924e0` | 0 | `33` both times; `SCORECARD.md:18` claims `32`, so r41 is a stale row this round repairs | this receipt, `companion-head-and-province.md` |
| 13 | `sha256sum SKILL.md`, `wc -l`, `grep -c '^## '` on the committed tip and on the lane working tree | 0 | tip `46a924e0`: `1ad95066…`, 1442 lines, 34 headings (depth row correct there); working tree (round-47 SKILL rows, uncommitted): `ddb80f6e…`, 1463 lines, 35 headings, so the depth row moves when they land | this receipt, `companion-head-and-province.md` |

### Controls (row 11)

| case | rc | line |
|---|---|---|
| draft applied, evidence paths present | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| canonical row's only pointer dead (`tools/live-replay.py`) | 1 | `listed 11 observed 11 missing 0 unsubstantiated 1 met False` |
| both pointers of the new row dead | 1 | `listed 11 observed 11 missing 0 unsubstantiated 1 met False` |
| tool pointer dead, receipt pointer alive | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| new row removed from the canonical table only (mirror keeps it) | 1 | `listed 10 observed 11 missing 1 unsubstantiated 0 met False` |
| round-47 marker removed (round-46 table becomes canonical) | 1 | `listed 10 observed 11 missing 1 unsubstantiated 0 met False` |
| marker present, table absent | 1 | `listed 10 observed 11 missing 1 unsubstantiated 0 met False` |

## Synthetic commits (scratch clone only)

Built to exercise the counters' `--tip` path without touching any branch, index or ref:
`GIT_INDEX_FILE=<temp> git read-tree HEAD|81d0ebb4` -> `git add`/`git update-index --cacheinfo`
-> `git write-tree` -> `git -c user.name=S9Cap -c user.email=s9cap@local.invalid commit-tree <tree> -p HEAD`.
`git -C $S/lane rev-parse --show-toplevel` was asserted before the first of them. No ref was created;
the objects are unreachable and died with the scratch clone.

| commit | tree | content |
|---|---|---|
| `81d0ebb401cf99888d51d16858c5c1ff2835b7dd` | HEAD + patched `SCORECARD.md`, `PROVINCE.md` | the full draft |
| `0c661cf324c21459759a3d9909ffd24df56971ba` | `81d0ebb4` with the `## Axes` coverage sha reverted | omission control |
| `99667497d338ab9b793fcbd254a1c28826d83490` | `81d0ebb4` with `PROVINCE.md` at HEAD and the coverage sha reverted | omission control |
| `ae7e28010c5f81ed12888a90640583db5192acbc` | pristine SCORECARD + canonical block only, PROVINCE patched | omission control |

## Effect of the draft

`git -C $S/lane diff --shortstat` -> `2 files changed, 24 insertions(+), 6 deletions(-)`
(`SCORECARD.md` +23/-5, `PROVINCE.md` 1 line rewritten).

| file | pristine (`3a09a1d9`) | drafted |
|---|---|---|
| `SCORECARD.md` | sha256 `8964ee368abaf5f89cea0cab4282be35b233f8fb92c878137880a4236f04c814` | `f5f1cd1affaf5f05806f19bc097b2b3cec38557d2b19534a05e59bd545324f4f` |
| `PROVINCE.md` | sha256 `659a5101ce0a8bc08d2c63a23d52049cd97e183d92f226568607ebf11bc9fc49` (186 lines) | `929f3e3eef20fa90429ca0c5a96a63821cff6aeca912ac55bad3a82b4bd3a079` (186 lines) |
| patch | - | `proposed.patch` sha256 `2d95bffcc2beb6cf7ae6386ef49f5d3e816b2e40d4b79ea8dd3f250889204853` |

Apply with `patch -p1 -d kama-shokunin < proposed.patch` (the clone emits `i/`…`w/` prefixes;
`git apply -p1` also works). `tools/capability-repertoire-audit.py` at the tip is sha256
`8f9c60baca48c2661ba893ae776edaeaec43a9431d8b3a40337e5ec8dc25d00e`.

## Merge with S9Scorecard (received after these runs)

S9Scorecard adopted the canon verbatim, places it inside `## Round 47`, and merged the head moves;
its measurement at commit `1d9102972faf84d38ee0a78e37ded85193ad040c` (base `46a924e0` + section +
head moves) reads `r42 mismatches=0 met=True` / `maxN=47`, `r41 mismatches=0 met=True`,
`planned-pointer-check met=True`. Its section-only variant `7ba2c796` reads `mismatches=9` =
`r41 1 + banner 1 + planned 1 + retired 1 + saturation 1 + caps 1 + province 3`; the last five
reproduce this receipt's controls/omissions. Two moves this seat's companion list did not own are
required and are now recorded there: `SCORECARD.md:18` calibration `32` → `33` (33 blobs verified at
both revisions, run 12 above) and, once `## Round 47` exists, `SCORECARD.md:6` banner 46 → 47 and
`SCORECARD.md:53` planned pointer 47 → 48 with a `### Planned (round 48)` heading. The block must
be applied once: `proposed.patch` and the section draft overlap on the canon and the four companion
edits. A further live head move, not forced by the canon list: `SCORECARD.md:16` depth anchors
`SKILL.md` (tip `1ad95066…`/1442/34 is correct; the uncommitted round-47 SKILL is
`ddb80f6e…`/1463/35, so hash, lines and run fact all move with it) - run 13.

## Artifact hashes

```
02d39c08f0410612c118d06b9aa676e47a264684b59c85cd48126afd2290ff5d  append-only-v2-at-tip.out
cfbb031b1ce73d86d32bf11ac0f83c9d45006f37f9743a07c23172a637388725  canonical-round-47.md
256392db6ccf9c7a76485c1f8f83bc85c59ccff0276ccd88f1081abc3a13a5d4  caps-after.json
b9c3569e4208d66d8b90dbb9d0898675c8a25f3869f12bb1f57c4d66ed5c820a  caps-after.out
f93d2650430213642fbcfaa1e5f9fbd226fc061813b067205ef32843736f74bb  caps-baseline.json
47051c5f5f734141912ab3fc0db9a55825456b71c97d1295bdf199a5acb2bf35  caps-baseline.out
3362721bcba397e6fcbe8f739e1407f06db882ae75414aa7225aafae739d3813  caps-selftest.out
1c8769c74944d2310f01a948e26a114d63660c7ff5b9fe2a980d84086708bde4  caps-tip-committed.json
b9c3569e4208d66d8b90dbb9d0898675c8a25f3869f12bb1f57c4d66ed5c820a  caps-tip-committed.out
7a2a10d44325154b21e649e7b0f204e3593b3b292f80981a0dc4f3fba95f78c5  caps-tip-tokens.out
b1ac49f7acc1435183d953b4ad68e467ac394032d00d56f4d3ccda60efc900c0  companion-head-and-province.md
abb9330294c4181065be644dc10aeb5bfeba6cec6859cb71c4577e5551eb62e3  controls.out
f4713c91e0075538581248d106b0226d51232fff247f5f6d7210a46dac68f0f4  mirror-capabilities.md
2d95bffcc2beb6cf7ae6386ef49f5d3e816b2e40d4b79ea8dd3f250889204853  proposed.patch
33a06b54b82cfda1ea02afee7453725bd8cd4e9c6a8ad67e10d09b12aaa587aa  selfdesc-baseline.out
70ef6b622afd72105abcf98d0dd72c85310516c43bfb528062104ddfb7a319ad  selfdesc-good.out
8e88540867b0aebd2fb80f70da2a51eec1e7d2b87d6cc06b6ede3f33c351cdb7  selfdesc-variant-no-anchor.out
34aac40286036241aae181b7a025643a3473696578d8cba109c605735ffe29bc  selfdesc-variant-no-province.out
737e5046fb006f1067ba9d9e81dba0f0bfddfaa7ce60ab80f9ef385e1c15c31a  selfdesc-variant-no-mirror.out
```
