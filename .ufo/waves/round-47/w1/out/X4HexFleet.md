# X4HexFleet - round 47 (r46-D4): the six fleet-repo hexrun unknowns

**Verdict: all six tokens are fleet-repo commits, verified locally; six `upstream` rows and six evidence blobs drafted; the gate drops `unknown` 22 -> 16 (`upstream_ok` 68 -> 74) with no other class moving, and both negative controls fail as they should (`ledger_bad=6`).** Calibration axis: measured (local object identity at the fleet repo, census gate on a fixture).

## 1. What was asked

Round-46 closure D4 (`corpus/lessons/round-46-verifier-spotcheck.md:30,140`: `hexrun-census unknown=21`/`22 at 3a09a1d9`, exit 1). This seat owns the unknowns that are commits of the fleet repo `/home/vgpnk/Projects/shokunin`:

`277ee2ef`, `463f498c`, `6105c587`, `70e6cd5f`, `8bca0cf3`, `b0fd7b7f`.

## 2. Verification (fleet repo, read-only)

Baseline first, at the lane build commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (my `git clone --shared` of the lane, scratch; output retained as `base.out`/`base.details`):

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/hexrun-census.py scan \
    --repo <clone> --rev 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --details
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22
rc=1
```

All six appear in that unknown set; occurrence counts: `6105c587` 70, `b0fd7b7f` 104, the other four 1 each.

Per-token identity (exact outputs, with the invoking command, are in each evidence file; `git -C /home/vgpnk/Projects/shokunin cat-file -t <token>` returned `commit` for all six):

| token | `log -1` subject | author / committer (committer date) | `show --stat` |
|---|---|---|---|
| `277ee2ef32435155212d48b1711413305f017bc3` | round-45: kama report | kama-shokunin / kama-shokunin 2026-10-26T07:52:54-03:00 | `.ufo/reports/round-45/kama.md` +74 |
| `463f498cc8e8af89aa7b3bb594bb4b494a0571de` | round-44: kama report | kama-shokunin / kama-shokunin 2026-10-26T05:25:35-03:00 | `.ufo/reports/round-44/kama.md` +154 |
| `6105c5870859f15ba5372ccbe3835d65b0d9d38b` | round-45: kama dispatch evidence (hyaku inline attempt 1) | kama-shokunin / kama-shokunin 2026-10-26T05:35:20-03:00 | `.ufo/prompts/kama-round-45.md` +599 |
| `70e6cd5f317cd6f7a5431c819bf0f5971fc64f15` | round-43: kama report | kama-shokunin / kama-shokunin 2026-10-26T00:01:30-03:00 | `.ufo/reports/round-43/kama.md` +111, `.ufo/l0-questions.md` +1 |
| `8bca0cf333e7ceab5e734b354c87075c6efec86c` | round-46: kama report | kama-shokunin / kama-shokunin 2026-10-26T17:48:10-03:00 | `.ufo/reports/round-46/kama.md` +150 |
| `b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025` | round-44: kama dispatch evidence (hyaku inline attempt 1) | kama-shokunin / kama-shokunin 2026-10-26T04:34:51-03:00 | `.ufo/prompts/kama-round-44.md` +599 |

Where each is cited in lane documents at `3a09a1d9` (`git grep -n <token> 3a09a1d9 -- '*.md' '*.tsv' ':!.ufo/*'`):

- `277ee2ef`: `corpus/lessons/round-45-verifier-spotcheck.md:13`
- `463f498c`: `corpus/lessons/round-44-verifier-spotcheck.md:13`
- `6105c587`: `SCORECARD.md:2413,2419-2422`, `corpus/lessons/round-45-verifier-spotcheck.md:17,83,84,129`, `registry/claim-outcome-ledger.tsv:2-126` (all 63 self rows)
- `70e6cd5f`: `corpus/lessons/round-43-verifier-spotcheck.md:13`
- `8bca0cf3`: `corpus/lessons/round-46-verifier-spotcheck.md:23`
- `b0fd7b7f`: `SCORECARD.md:2350,2356-2373`, `corpus/lessons/round-44-verifier-spotcheck.md:28,52`, `corpus/lessons/round-44.md:68`, `registry/verdict-ledger.tsv:2-202` (204 rows)

None of the six had a ledger row before this seat (`grep -E '^(277ee2ef|463f498c|6105c587|70e6cd5f|8bca0cf3|b0fd7b7f)' registry/hexrun-ledger.tsv` → no match, rc=1), so no duplicate-row risk.

## 3. Census contract used (why the evidence shape is what it is)

- `upstream` resolves only if the evidence blob contains the token bytes and the `repo` cell text as a byte substring: `tools/hexrun-census.py:248-255` (`want_repo in data`). The cell and the evidence line therefore have to agree; there is no git-API check in the scan.
- The evidence blob is looked up by its lane-relative path **among the blobs of the scanned REV's tree**: `tools/hexrun-census.py:311-329`. A ledger row alone is not enough; the file must be committed at the REV being scanned (this is exactly the `ledger_bad=6` negative below).

Each evidence file is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/<token>.txt`, with the line `# repo: vgpnk/shokunin (fleet)` (the cell text, exact), the canonical fleet origin `https://github.com/VeigaPunk/shokunin.git`, the fleet root, the lane citation, and the literal `cat-file -t`, `log -1 --format='%H %an %cI %s'` and `show --stat` commands and outputs.

## 4. Gate (as X4HexUp1's item prescribes)

Fixture: `git clone --shared --no-checkout <lane-clone> <scratch>/fixture`, detached at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (asserted `rev-parse --show-toplevel` = fixture dir), evidence blobs added and committed with fixture-only identity (`X4HexFleet-fixture <x4hexfleet@fixture.invalid>`), producing fixture commit `fb37f58a52f9cb20632f8667f6bb61201dc30382`. Ledger: a copy of `registry/hexrun-ledger.tsv` plus the six rows (`ledger-copy.tsv`, 89 lines).

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/hexrun-census.py scan \
    --repo <scratch>/fixture --rev fb37f58a52f9cb20632f8667f6bb61201dc30382 \
    --ledger <scratch>/ledger-copy.tsv --details
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=74 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=16
rc=1
```

- Every one of the six flips to `class=upstream_ok` (`gate.details`).
- Unknown-set diff: removed exactly the six, added none (`removed=6 added=0`), `unknown` 22 -> 16, `upstream_ok` 68 -> 74. No other class changed.
- `rc` stays 1 because 16 unknowns remain; they are the other seats' ranges (`0a14a962`..`9706b3ac` and `a4b4feae`..`e1e006f1` scoped to `registry/release-recheck-b11889.tsv`, plus the `recheck-r45.tsv` / `d854d98b` tokens). This seat is not a closure of D4 on its own.

Negative controls (both retained in this directory):

- Same new ledger, but scanned at `3a09a1d9` where the evidence files do not exist yet: `upstream_ok=68 ... ledger_bad=6 unknown=16` (`neg-noevidence.out`) - evidence must be a blob at REV.
- Same fixture, but the ledger's six cells relabelled to `example/none`: `upstream_ok=68 ... ledger_bad=6 unknown=16` (`neg-badrepo.out`) - the repo cell really is matched against the blob.

## 5. Rows for integration

`rows.tsv` (this directory) is the exact append to `registry/hexrun-ledger.tsv`, header order `token class repo evidence correct verified-at note`, class `upstream`, `verified-at` 2026-10-26. The six evidence files are already written to the lane's evidence directory; they are untracked until the integrator commits them.

Integration requirements for the gate to hold at the tip:
1. Commit the six `.ufo/waves/round-47/hexrun-evidence/<token>.txt` blobs and the `rows.tsv` lines in the same integration commit that is scanned (evidence is located by path in the scanned tree).
2. Do not echo the rows under a second repo label; the census treats two rows for one token as `ledger_bad`.

## 6. Findings and risks

1. **Naming inconsistency, not a tool defect.** The seat item prescribes the repo cell text `vgpnk/shokunin (fleet)` (source: `.ufo/waves/round-47/w1/build_spec.py:153`). The fleet repo's GitHub origin is `https://github.com/VeigaPunk/shokunin.git` (`git -C /home/vgpnk/Projects/shokunin remote get-url origin`), and the 31 existing rows naming `VeigaPunk/shokunin` in `registry/hexrun-ledger.tsv` span lines 2-66. The rows follow the item's cell, and the evidence records the canonical origin on its own line, so both spellings appear in every evidence blob and either cell would pass `tools/hexrun-census.py:255`. If the ledger is to carry one slug for the fleet repo, relabelling these six cells to `VeigaPunk/shokunin` needs no evidence change (the substring is already there); leaving `vgpnk/shokunin (fleet)` keeps the item literal. This is a consistency choice for the L1, not a verification failure.
2. **Evidence is untracked in the lane right now** (`git status --porcelain .ufo/waves/round-47/hexrun-evidence` -> `?? .ufo/waves/round-47/hexrun-evidence/`). The six rows are only valid once the integrator commits the blobs; until then a tip scan would count them as `ledger_bad` (proved by `neg-noevidence.out`).
3. **Directory is shared with sibling seats.** `hexrun-evidence/` also holds 11 blobs from X4HexUp1/X4HexUp2/X4HexR45 at the time of writing (17 files total, 6 mine); I wrote only my six `<token>.txt` files and left theirs untouched. Their rows are not in my `rows.tsv`; the merged ledger must take each seat's rows once (no duplicates per token).
4. **No tool installs, no service starts.** Nothing outside the prescribed evidence paths, my out directory and scratch was written; the only commit was made in the scratch fixture, with a fixture-only identity, after asserting the fixture toplevel.

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/277ee2ef32435155212d48b1711413305f017bc3.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/463f498cc8e8af89aa7b3bb594bb4b494a0571de.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/6105c5870859f15ba5372ccbe3835d65b0d9d38b.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/70e6cd5f317cd6f7a5431c819bf0f5971fc64f15.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/8bca0cf333e7ceab5e734b354c87075c6efec86c.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexFleet/rows.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexFleet/evidence/` (copies of the six)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexFleet/{base.out,base.details,gate.out,gate.details,neg-noevidence.out,neg-badrepo.out,ledger-copy.tsv}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexFleet.md`
