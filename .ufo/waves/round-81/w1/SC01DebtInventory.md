# SC01 — independent inventory of the round-79/80 append-only debt (scout, kama round 81 w1)

**Verdict: the ten-event debt is exactly as the plan declares, and the landed late register matches my independent inventory cell-for-cell (88/88 rows, 0 mismatches, 0 extras, 0 missing).**

All numbers below are read from committed bytes at the audit revision `2c1faed0354dbb3cb9f869cb1af4a9302dfcfd4e`; nothing was read from the worktree as evidence, and I did not read `tools/round81-append-debt.py` or `tools/round81-late-rows.py` (objects under test).

## Receipt

```text
cmd : python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
        --repo /home/vgpnk/Projects/shokunin/kama-shokunin --json > $S/audit.json
exit: 1              (expected: the tool exits 1 when it has findings; stderr empty)
out : 183683 bytes, sha256 169454b8660af975f439b4793560b0055b9943f4074ab284ff5649becd35df20
schema: append-only-audit/v3  definition=v6   to=2c1faed0354dbb3cb9f869cb1af4a9302dfcfd4e
summary: commits=677 files=156 events=264 restored=102 partial=0 unrestored=63 ungraded=94 disclosed=5
         permitted_lines=634 disclosed_lines=10 bad_disclosures=0 ungraded_lines=436
         regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```

Receipts (absolute):

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/audit.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/audit-command.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/inventory.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/inventory-lines.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/INV.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC01DebtInventory/LATE_DIFF.json`

## 1. Population — 63 undeclared (unrestored) deletion events, all ancestral to the base

Observed: the audit's `events[]` has 264 entries with statuses `restored=102`, `ungraded=94`, `unrestored=63`, `disclosed=5`. All 63 `unrestored` events carry a non-empty `undisclosed[]`.

Observed: `git merge-base --is-ancestor <event-commit> e7d2fd729cf8204c89c32534303bc9f2a97fcee4` returns 0 for **63/63** events — the population at the declared base is identical to the population at the audit tip (the tip `2c1faed0` is a descendant of the base, and every event is an ancestor of the base, so no later commit can add or restore one).

Totals (`INV.json`): **63 event records** (one per commit+file pair) over **51 distinct commits**, **477 undisclosed entries** (`line_sha256` units) = **551 undisclosed lines** (entries with `count`>1 repeat a hash; the 389 accepted-register entries account for 463 of those lines).

The population is dominated by record prose: `SCORECARD.md`/`LOG.md`/`corpus/lessons/*` in-place edits, one 288-entry `corpus/SOURCES.md` CRLF→LF normalization (round-65 `ea33a78f2b`, 362 lines), and one **`removal`**-class event on the register itself (round-79 `5785cdff64`, 38 rows).

## 2. What the frozen `registry/append-only-accepted.tsv` already covers

Observed: the frozen register holds **389 rows** (390 lines incl. header, 6 tab fields each) over **42 distinct commits**. It covers **53 of the 63 event records** and **389 of the 477 entries** — full cell-for-cell agreement on (commit, file, line_sha256, count, class). Two independent checks:

- Every one of the 389 register rows has an exact counterpart in the audit's undisclosed set → `register_rows_without_inventory_counterpart = 0` (no stale rows).
- `count` and `class` agree on all 389 matched rows → 0 cell mismatches.

## 3. Why the remainder is exactly ten events

Observed, and byte-anchored rather than assumed:

1. The register was **introduced in round-75**, commit `10f37171fb696c542586cbee96ea4a509ab74afc` (`round-75: interpretation pins … accepted-history register and declaration repair, gate arm 8 …`).
2. **All 42** commits referenced by register rows are **strict ancestors** of `10f37171fb` (checked individually; 0 are descendants or equal). The newest referenced commit is round-74 `9e2b547f09`.
3. **All 9** commits of the remainder are **strict descendants** of `10f37171fb` (`merge-base --is-ancestor 10f37171fb <c>` = 0 for each, and `c != 10f37171fb`).
4. Therefore the frozen register cannot contain a row for any of them — the round-75 predicate needs a row committed *before* the register's own introduction, and these events postdate it. That is the structural unsatisfiability the plan calls out; it is a property of the commit graph, not of missing rows.

The remainder is 6 round-79 commits / 7 event records plus 3 round-80 commits / 3 event records = **9 commits, 10 event records, 88 lines**:

| commit | date | round | file | entries | lines | deleted | class | subject |
|---|---|---|---|---|---|---|---|---|
| `1cda04569f30005adc89f98aa02909d6659fdf99` | 2026-11-04 | 79 | `SCORECARD.md` | 4 | 4 | 4 | `in-place-edit` | round-79: disclose the register-counter red and name the R78V6 plan paths with |
| `223c881a3ae74679ed5c8cbc713f331f97a12338` | 2026-11-04 | 80 | `SCORECARD.md` | 2 | 2 | 2 | `in-place-edit` | round-80: name the defect receipts explicitly and keep round numbers out of su |
| `28debbcf50c4cfe9ca6d3077508cc14aa8c7365a` | 2026-11-04 | 80 | `SCORECARD.md` | 1 | 1 | 11 | `in-place-edit` | round-80: record the three measured claims, the round-79 correction and the ro |
| `4af44f78303f04a6ea32ea62cac586f89688d73a` | 2026-11-04 | 79 | `SCORECARD.md` | 6 | 6 | 6 | `in-place-edit` | round-79: C2 honest stop on the scored gate (arm 8 red on the round's own in-p |
| `4af44f78303f04a6ea32ea62cac586f89688d73a` | 2026-11-04 | 79 | `corpus/lessons/round-79.md` | 2 | 2 | 2 | `in-place-edit` | round-79: C2 honest stop on the scored gate (arm 8 red on the round's own in-p |
| `5785cdff641fb210966c93168a6ff922b82af414` | 2026-11-04 | 79 | `registry/append-only-accepted.tsv` | 38 | 38 | 38 | `removal` | round-79: restore the accepted-history register (the 38 post-introduction rows |
| `5fcef757a64e0e7736904c68e101d96f60a5d847` | 2026-11-04 | 80 | `SCORECARD.md` | 1 | 1 | 1 | `in-place-edit` | round-80: keep the correction subsection out of the receipt-pointer round reso |
| `9100605d6cfa2c467c1fd2468eef502f162e5d3d` | 2026-11-04 | 79 | `corpus/lessons/round-79.md` | 16 | 16 | 16 | `in-place-edit` | round-79: claim receipts at 5ac1a8dd (C1 green, C2 pass=26, C3 census, control |
| `b574397576eaed3fbbf3568f102b8a2a155600d8` | 2026-11-04 | 79 | `SCORECARD.md` | 12 | 12 | 14 | `in-place-edit` | round-79: repair the SCORECARD planned section, re-anchor the retired/saturati |
| `f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f` | 2026-11-04 | 79 | `SCORECARD.md` | 6 | 6 | 9 | `in-place-edit` | round-79: re-anchor the operability/depth/coverage evidence hashes at the roun |

Reconciliation of raw deletions to the 88 (observed): the ten records delete **103** lines in total, of which the contract grades **88**; the other **15** are `ungraded` (outside the graded population) — `b574397576` 2/14, `f4a35f6c21` 3/9, `28debbcf50` 10/11. Every graded line is undisclosed, so `graded = undisclosed = 88`. The late register therefore owes exactly 88 rows, not 103.

### Class ambiguity check

Observed: **no** event and **no** entry carries more than one mechanical class (`events_with_multiple_classes = 0`; every `undisclosed[].classes` is a single-element list). The single `class` cell is therefore unambiguous for all 63 events and all 88 late rows. The only non-`in-place-edit` class in the whole population is `removal` on the 38 `registry/append-only-accepted.tsv` rows of `5785cdff64` (round-79 restored the 38 post-introduction rows that had been removed); the late register reproduces that class verbatim.

## 4. Diff against the landed `registry/append-only-late.tsv` — **match**

The file landed while I worked: 89 lines (header + 88 rows), 6 fields each, committed at `f6cb5303171cc73dc570ace06f99125266e5b956` (`round-81: repay the ten inherited post-introduction append-only events with late-acceptance rows`) and clean in `git status --porcelain`. Cell-by-cell against my inventory:

| check | result |
|---|---|
| rows | 88 |
| duplicate (commit,file,hash) keys | 0 |
| late keys absent from my inventory | 0 |
| my inventory keys absent from the late register | 0 |
| `count`/`class` cell mismatches | 0 |
| notes violating `round-N accepts round-M` with N>M | 0 |
| introducing commit a strict descendant of all 9 event commits | true |

Per-event row counts match my inventory exactly: `1cda04569f:SCORECARD.md`=4, `223c881a3a:SCORECARD.md`=2, `28debbcf50:SCORECARD.md`=1, `4af44f7830:SCORECARD.md`=6, `4af44f7830:corpus/lessons/round-79.md`=2, `5785cdff64:registry/append-only-accepted.tsv`=38, `5fcef757a6:SCORECARD.md`=1, `9100605d6c:corpus/lessons/round-79.md`=16, `b574397576:SCORECARD.md`=12, `f4a35f6c21:SCORECARD.md`=6.

## Appendix — the 88 undisclosed lines of the ten events

One row per undisclosed entry, exactly the cells the late register must carry (`count` is always 1 here).

```tsv
commit	file	line_sha256	count	class
1cda04569f30005adc89f98aa02909d6659fdf99	SCORECARD.md	86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e	1	in-place-edit
1cda04569f30005adc89f98aa02909d6659fdf99	SCORECARD.md	88d34850ef76373a0ed4f47b67be1013ad766a4d020999ab185004a150495a98	1	in-place-edit
1cda04569f30005adc89f98aa02909d6659fdf99	SCORECARD.md	8e5a52b160aedcaee21b9bbb318a0951cbdd5cb6302691dc356bb7ea030dd4be	1	in-place-edit
1cda04569f30005adc89f98aa02909d6659fdf99	SCORECARD.md	9488c25bf65fd039efffd761d07df6880ab9cc7bfe87966d7db6f05d4491f315	1	in-place-edit
223c881a3ae74679ed5c8cbc713f331f97a12338	SCORECARD.md	3eceadfb5e773755a3cbbdd4f93593ba60a0cebbc8f95d82c2810a3e7f7dbf90	1	in-place-edit
223c881a3ae74679ed5c8cbc713f331f97a12338	SCORECARD.md	a0631296dd419fff2430de82f093510843e257a337eb68af0ccbab9046298c99	1	in-place-edit
28debbcf50c4cfe9ca6d3077508cc14aa8c7365a	SCORECARD.md	d894d647e7a7c4ca3bdcfa53bf112b0d39151573c157e006dcb839101838a449	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	1fcfaadf95a07eba33fcec70fc47826df7ddb42b7c92ba9eba6463727c84b1eb	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	33149e47836faca4f4dbea1694eb1b076d3846a0706ff54eaa6f4a54d667ff85	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	77281f66a047bba8c2dca1fe31dadb62f4b4ea8fc35fff63c18d853232479a90	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	9a659e0983714505d1dfe90e5ef35471d19d66f875ccd2b6a29aa0ba8f00f1f6	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	d6fc4a3a4c88d16958dd53e51fef3c407b4f37af9449b99f9a22d307dfa07a6b	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	SCORECARD.md	dc7e77a984ea25fd481d2b4d8462fec5988ce0b5fcbad9ea4613249834cd7afc	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	corpus/lessons/round-79.md	4f975e4f8555d4a7b1d8b29295958f04c603da9514c196427a95a51a63bb23f7	1	in-place-edit
4af44f78303f04a6ea32ea62cac586f89688d73a	corpus/lessons/round-79.md	d217400656a81df399157a05ec6d167fe28fc9c8cd5cb11ea6af239d12703785	1	in-place-edit
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	00224a10d2750e62d2e1a718582a9b31e63487da0ab59fcb6ee5a7c0bf55e68a	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	016b426d7923200a4dedf191e628ca688f05f842dd4ce85edeb6a9256822e828	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	0aea4c628cd5f6a2c7512babd193553e43760bc84db0031831bf0ab7104b8204	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	1bd9ac171886b0b4dde91d0bcb92d1edbb715d7f7fe7e7ecd288736df942a6b1	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	28c4db37647094cab14d61bc56ac4d52ba84ffd0abbb28500dbc60e3e55879e0	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	323fdbb6422d37658b814e46d6da803b2c9a05f0724994a878bbceb24d777aa3	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	345ebdbc499430d3d8cd811ade5e95f457cfc73b3b0561e04128f5c910da7d36	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	38095c1fc74ec67142e1cc839babba6df57b8f07995834cee67e002913f82bf4	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	3cc52e779ede31f87320f24c491f98b5be1c8a8f54e83b7305c2e0c77c756c5f	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	3dfce508587e96d71ba72a70f4666aab1f9701c85832291c9cfbeefef497f899	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	3e2ca423fd88328eb746c402ef1f957ed7670b594718aa8f5623ec1282a47745	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	3e8bc8882cfb07550f5ccfeffb1887b3bd8f76404b47d4aa45c6b3b6b205c442	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	43cab9be584850ae8f0091a529b654786ef2e26910ff73673ae2e1b09903c0cb	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	4ad33c1d62d566d4d2a21a787e10c540995756e1b38b30e31c718f0a1caa3e10	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	4b919c983d204016c9d2619ed55c962b8372f397ac2cfdec0c8b6b89f2409926	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	514c7829720110402013ca877dc5345dbad8973531325b7ed776d91e9dad9a01	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	52183481f3d779f0c570f3fa953fbdad8f2fb569aa5f77f00539a6af68c4f626	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	53aa224b641d8ae50459f89e3cb1e1a617d5756e6721b13f62313550a75d055f	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	54d38c3615ff4e126255677b0b678fbcf3d81e6a4c622af227f895ce5cb57fad	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	78c6357966351f6bab678f1339368fc8b9ecf4c4cbd74651ce5026f5dc12dd90	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	7bff71c88f054b4056f6116024c79e077d7c4f9b972a94584ff76867a044d589	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	854fa756df0b8c9868f0c2721e6baeed6ed46eef6469eae221ce8a7a2dd0100b	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	86eb1e132a9aecff6ce8c7769a5961d023b49d3c8353de6b5019f0929c48b610	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	90990887ac56be8eb3567b39787c23ed583e5d5d082432ac4f530cf402ee635c	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	9a5f8a3281095546f4ffd237fcde84de3f58acf44b11ff9c44e607bed9eaae78	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	a4e5148705a70c6aa407641276527f096dd9fc714c1a1541a1c3cb1b0d4ee92d	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	a8b93414563b61040b23fb1356d8c0eb1674e0280f95bf57a70c6b228f618272	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	b78ac2a99410b4a3d322209d3a3163a10bc0c9c6f5ded760b25f99c36553868c	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	ce66c8699fa9e831b223e1eb7ba3c687de1fa0b972b5f5cd20275e22e8d928e4	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	d142eea0d40da6810134c835a9b2266b4907910ab2ae976bc9a6ba97746e2d61	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	d4f954ac1c00b4572ec16a2fdfeab23bfcbc9063f93f1dd4ca251bc14c5b90d3	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	d6550eec84dc608175b973430ebcce20c9dbf7e14239e5726fe98275adfab355	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	df6871936c8e4db9e01668d1fc1d43cd99f00c88871f8ca86e520361ca9bec8e	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	e95fd8a4477f9bc0c95760d6d65891598705d53cc8ba6952e2d15bec5cb053f3	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	f4d016fadf0d7eba58cc54332f9f704fd45efdf49df598ff2a3d30c7b3573c57	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	f69d97613301756c5c74a6ddf6c15412587766372ce5de8c815f4197e53b1e26	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	fa01c60ff5fe6ef1bf5c16f2bf01878fd3e2a08ffbce4019a8dd9770279d0d1a	1	removal
5785cdff641fb210966c93168a6ff922b82af414	registry/append-only-accepted.tsv	fe598b53b78aacc1dae360346fc67b6a8240706c761e051fa02a56729994a8e2	1	removal
5fcef757a64e0e7736904c68e101d96f60a5d847	SCORECARD.md	fe16f47e6176647849399e329e22b4ed7e7ac22c326638a691277364e0da5d5d	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	063920c3a6536193f3cb6f0478d7b299e475a96aa6e82e2dbd5a4b45538ba172	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	301bc0abf123faf3c04f57b4a8ad6a2704f0bc5c9ec46b0aefda791d9a746b0f	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	3bb8436b8d10f13068c93f3a33f0a69f966810d8dc392808ff5a807f2bfc7066	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	48fc535801a982a88503b3b8d07e92043251ac6db92ea26d2087b5220b548a7b	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	5c35cf3ffea710b202bf038b7a0e384684d15ce34e48b146637dc06703eda5bb	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	5eb14313275a36e19960d1de2f70a8bb8ddeb9d34da5a4bfacc7f1dc585ac461	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	70e89c06580a22f3130d685a8a44d283e6447a9a42597eb4358665cac91ca8b5	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	77e63cc6e3254667f30f22188f9f70afe4c157b8538ea9603606b7de31194cb4	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	7946464cbde8c7736e27224381107e16e2a07613f46473ca999f06469ac36a93	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	8236c0a453d72a39e88219969d430bb065125808865cc1268d85e4e00d04c253	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	825e504fb003d9b4d79eade8abb28f33351c5ef13acb542a53858e928da36de6	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	ad8e8c16ada4cbb6d33be9efbd1862aa40b1cb80881a9dbd2784c638e263f15d	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	bece5465fa10c5a80fa98f6c7efa06b92f44f6517249d0a760c573d78f2c9dda	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	ea41e185ee3e82d8e34424009dd91932a2cef8b1f795ac9162824b6f90a9d982	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	ed3f13baaaba58344e0042dbae52c56df7d30ca40b093a50eeeb8632ab126177	1	in-place-edit
9100605d6cfa2c467c1fd2468eef502f162e5d3d	corpus/lessons/round-79.md	f8d311761565dfc0c5d451c24297ab809419f5d6ee0f5eae7fb094eef3f88f6d	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	07899019c2ce5b9056a3ab72b78a5d9437e2c30e6994b8daa382cad1efd28226	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	1be92dcfb05f4523ae7db98f141fb9de359aaa4bd540167716ba02ceec029410	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	220ce96fe482f534a0f60047eb00732d601ba1818bd27c02ee11475758c3d248	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	4759bb7b03347ad819e48b0654ac1e91c4ff6f18665bc218a83f1ff4d6a03676	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	4bef054ee00f74747a3e993e3f1250aa0a40b71fd22b1d6901fd2a943b712193	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	7987af60d8e29c76d8bc5d3eb0211e108eca09ec351c77d1450969fbeb6e2b2b	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	96a09376b1e0f2f8ee4c1eb43fdfd9e6576ddceb0a4a42125ee826b9fb4d6f2e	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	c694ca68fa12b3185cb4d4747e5a30a7a9b19b7bd68c4bd2a7a2136a8d037e42	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	cca48b38ee3278c2aef22951bb4ad625316efbd9e469ba815c1ef94b6dccc879	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	de63c835bff91b41fec40f4ac9aea5c5089d2590912408a14bcdbf1acf109df0	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	f05bc558d39bca9ad667075c1b22e3bab39f67db45b861a32ddda78077c93ccb	1	in-place-edit
b574397576eaed3fbbf3568f102b8a2a155600d8	SCORECARD.md	f1a632eff9e0b126740ba1c447281fa2ec6e83db71f117a7c6bbab392485eda8	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	1db2175ef349fc5417ac07ff45ca7a24563eca00592d54d295aa996bcffb65f8	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	1e4ad651571c39c4c251b7922f844ee19a0c1b809767246496b3ba1f3831f814	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	28aebb27f2e3341206be3f165ae3635a898ada39eeb77688abcef12270dab940	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	85e94ef5bbd319becad18183ac0c05b5bb236fd9d3e0556180539c65a536ea8e	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	c5349039c8e8ee7e379c0bf17c77b76d80d0fd09d62002531870f96b94fb3111	1	in-place-edit
f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f	SCORECARD.md	ca6a54bfdb3d06aeb87a353904753c94f867bf02593c7b23b68e893612f8f799	1	in-place-edit
```

## Confidence and remaining unknowns

- **Observed (high):** the 63/53/10 split, the 88-row inventory, the ancestry proofs, the 389-row register coverage, and the 88/88 late-register match — each is a direct read of committed bytes plus a per-row comparison; commands and exit codes are above.
- **Observed (high):** no event has more than one class, so no `class` cell is ambiguous.
- **Inference (medium):** that the 15 `ungraded` deleted lines are excluded by the contract's graded population rather than by a pattern exemption specific to those rounds — the audit reports only counts, so the *reason* for each of the 15 is not re-derived here. It does not affect the 88.
- **Not verified (out of scope by seat rules):** the behaviour of `tools/round81-append-debt.py` / `tools/round81-late-rows.py` (objects under test — not read, not graded) and any `APPEND_DEBT` line; the grading seat owns that. I established the *input population* those tools must reproduce.
- **Not re-run:** nothing. No failure occurred, so there is no dead-seat evidence to report.
