# X4Hex — round 48, hexrun-census unknown `d0012618` (fleet report commit)

**Verdict: pass.** The single unknown at the round-48 build is the round-47 fleet report commit `d0012618894c7154683d97bb594b2dd5abbed013`, verified to exist in the fleet repo and cited once in the lane at `corpus/lessons/round-47-verifier-spotcheck.md:22`; the assigned evidence file is written, the ledger row is drafted, and a fixture clone holding exactly build + evidence + row reports `unknown=0 upstream_ok=92` exit 0, while four negative controls fail closed (`ledger_bad=1`, exit 1).

Env: `/fast/scratch/hyaku/kama-r48/X4Hex` (removed at the end), one live clone at a time (`lane` for the baseline, then `fixture` for the gate). No tool installed or upgraded.

## 1. Baseline — `unknown=1`, reproduced at the build

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/hexrun-census.py scan \
    --repo <clone of the lane> --rev 380bcdff9c8af06997c482f6eb03db926a794a2b --details
tokens=1803 distinct=288 lane_oid=184 md5_blob=1 upstream_ok=91 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=1
detail: d0012618894c7154683d97bb594b2dd5abbed013 len=40 occurrences=1 class=unknown
rc=1
```
288 detail lines (`out/X4Hex/base.out`, `base.details`); this is the only `class=unknown` and it occurs once in the whole document population. Tool selftest: `python3 …/hexrun-census.py selftest` → `selftest pass=18 fail=0`, rc 0.

## 2. The token is a real fleet commit, not a lane object

Read-only, against `/home/vgpnk/Projects/shokunin` (fleet; origin `https://github.com/VeigaPunk/shokunin.git`):

```
$ git -C /home/vgpnk/Projects/shokunin cat-file -t d0012618894c7154683d97bb594b2dd5abbed013
commit                                    rc=0
$ git -C /home/vgpnk/Projects/shokunin log -1 --format='%H %an %cI %s' d0012618894c7154683d97bb594b2dd5abbed013
d0012618894c7154683d97bb594b2dd5abbed013 kama-shokunin 2026-10-26T18:49:55-03:00 round-47: kama report   rc=0
$ git -C /home/vgpnk/Projects/shokunin show --stat --format='' d0012618…
 .ufo/reports/round-47/kama.md | 149 ++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 149 insertions(+)             rc=0
$ git -C /home/vgpnk/Projects/shokunin log --format='%an %H' -- .ufo/reports/round-47/kama.md
kama-shokunin d0012618894c7154683d97bb594b2dd5abbed013   rc=0
$ git -C /home/vgpnk/Projects/shokunin rev-parse d0012618…:.ufo/reports/round-47/kama.md
6ef7c613b081af3e32e4d0e3a8a81d0d77a32ee5   rc=0
$ git -C … merge-base --is-ancestor d0012618… master   rc=0   (also rc=0 against main)
```
The spot-check line (`corpus/lessons/round-47-verifier-spotcheck.md:22`) records exactly this command and output: `kama-shokunin d0012618894c7154683d97bb594b2dd5abbed013 round-47: kama report`, and that path was touched by this commit alone (149 lines; `wc -l` on the blob = 149).

It is absent from the lane's object store, which is why the census cannot call it `lane_oid`:
```
$ git -C <lane clone at 380bcdff…> cat-file -t d0012618…
fatal: git cat-file: could not get object info   rc=128
```
Under the frozen contract (`tools/hexrun-census.py:29-31,248-272`) the correct class is therefore `upstream`, whose evidence must be a committed blob carrying both the token and the `repo` cell text.

## 3. Evidence file (assigned path, written)

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/hexrun-evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt` — 3042 bytes, sha256 `7a5d2a7ece3b206e0b03fe379823b100ec304c8fe2fbfde85dfa4f977b7efe1d` (identical copy in `out/X4Hex/evidence/`).

Header: token, `# repo: vgpnk/shokunin (fleet)`, fleet origin/root, lane + build (`380bcdff…`), citation `corpus/lessons/round-47-verifier-spotcheck.md:22`, seat/date; then every command above with its output and rc, plus the lane-clone failure and the baseline census line. It sits under `.ufo/`, so it is not a census document and adds no tokens (`tokens=1803 distinct=288` unchanged through the gate).

## 4. Draft ledger row

`out/X4Hex/rows.tsv` (header + 1 row, 7 TAB fields each), and the full proposed ledger `out/X4Hex/ledger-copy.tsv` (lane ledger 106 lines + this row = last line; only the last line differs from the lane file):

```
d0012618894c7154683d97bb594b2dd5abbed013	upstream	vgpnk/shokunin (fleet)	.ufo/waves/round-48/hexrun-evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt		2026-10-26	commit not blob: commit 'round-47: kama report' by kama-shokunin, committer 2026-10-26T18:49:55-03:00, adding .ufo/reports/round-47/kama.md (149 lines, blob 6ef7c613b081af3e32e4d0e3a8a81d0d77a32ee5); cited corpus/lessons/round-47-verifier-spotcheck.md:22 as the fleet commit that filed the r47 report; fleet-repository object only (lane clone cat-file rc128), so bound to .ufo/waves/round-48/hexrun-evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt
```

Spelling follows the five round-47 fleet rows at `registry/hexrun-ledger.tsv:95-99` (`vgpnk/shokunin (fleet)`) and the evidence header matches it verbatim; the census requires that exact substring.

## 5. Gate — fixture clone with the evidence committed

`git clone --shared <lane> $S/fixture`; `git -C $S/fixture rev-parse --show-toplevel` = `$S/fixture` asserted before the commit; detached at `380bcdff9c8af06997c482f6eb03db926a794a2b`; evidence copy + row appended to `registry/hexrun-ledger.tsv`; committed with `-c user.name=X4Hex -c user.email=x4hex@fixture.invalid` (nothing written to any other repo's config or history):

```
88a841cca70c55200f52abce5d21d43f74c78d1a  fixture: round-48 hexrun evidence + ledger row for d0012618… (X4Hex gate)
 .../d0012618894c7154683d97bb594b2dd5abbed013.txt | 62 +++++
 registry/hexrun-ledger.tsv                        |  1 +
```
Lane build tree untouched: `git -C $S/fixture status --porcelain` empty after the commit (`out/X4Hex/gate-fixture.txt`).

```
$ hexrun-census.py scan --repo $S/fixture --rev 88a841cc… --ledger out/X4Hex/ledger-copy.tsv --details
tokens=1803 distinct=288 lane_oid=184 md5_blob=1 upstream_ok=92 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=0
detail: d0012618894c7154683d97bb594b2dd5abbed013 len=40 occurrences=1 class=upstream_ok
rc=0                                        (out/X4Hex/gate.out, gate.details)

$ hexrun-census.py scan --repo $S/fixture --rev 88a841cc…        # ledger read from the commit, no override
tokens=1803 distinct=288 … upstream_ok=92 … ledger_bad=0 unknown=0          rc=0   (gate-repo.out, gate-repo.details)
```
Both the `--ledger <copy>` path the item names and the committed-ledger path reach `unknown 0`.

## 6. Negative controls — the binding is real, not the row's presence

Each variant changes only the appended line (`diff` against `ledger-copy.tsv` with that line dropped prints nothing):

| Control | Change | Result |
|---|---|---|
| `neg-noevidence` | census at the build `380bcdff…` (evidence not committed there), ledger copy | `upstream_ok=91 ledger_bad=1 unknown=0`, rc=1 |
| `neg-badrepo` | row `repo` → `vgpnk/nonexistent (fleet)` (text absent from the evidence) | `upstream_ok=91 ledger_bad=1 unknown=0`, rc=1 |
| `neg-badfile` | row `evidence` → a committed file that has the repo text but not the token | `upstream_ok=91 ledger_bad=1 unknown=0`, rc=1 |
| `neg-badpath` | row `evidence` → `.ufo/waves/round-48/hexrun-evidence/nosuchfile.txt` | `upstream_ok=91 ledger_bad=1 unknown=0`, rc=1 |

Artifacts: `neg-*.out`, `neg-noevidence.details`.

## 7. Integration notes / risks

1. Landing needs **both** files: the evidence blob at `.ufo/waves/round-48/hexrun-evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt` and the row in `registry/hexrun-ledger.tsv` (line 107 if appended). The row alone yields `ledger_bad=1` (neg-noevidence/neg-badpath).
2. A census at the build rev keeps reporting `unknown=1`/`ledger_bad=1` by construction — neither file is at `380bcdff…`. Zero is a property of the integrated tip; my gate demonstrates it on a fixture commit that differs from the build only by these two additions.
3. Repo-cell spelling in the fleet rows is split (`vgpnk/shokunin (fleet)` lines 95-99 vs `VeigaPunk/shokunin` 34 rows, e.g. line 100): both bind because each evidence file carries the same string. If this row's cell is rewritten on landing, the evidence header line 2 must be rewritten identically, or the row goes `ledger_bad` (neg-badrepo). Not a defect — the census checks substring presence, and both spellings name the same repo.
4. No defect found in `tools/hexrun-census.py`, `registry/hexrun-ledger.tsv`, or the round-47 evidence series; nothing frozen was edited. The lane was not committed to; the only lane writes are the assigned evidence file and this wave's out directory.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/hexrun-evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X4Hex.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X4Hex/rows.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X4Hex/ledger-copy.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X4Hex/evidence/d0012618894c7154683d97bb594b2dd5abbed013.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X4Hex/{base.out,base.details,gate.out,gate.details,gate-repo.out,gate-repo.details,gate-fixture.txt,neg-noevidence.out,neg-noevidence.details,neg-badrepo.out,neg-badfile.out,neg-badpath.out}`
