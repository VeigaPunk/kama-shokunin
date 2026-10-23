# Round-30 C1 control arm — CtlAllOracle (mutation tester)

Advisory evidence only. Lane `kama-shokunin`, round 30 pre-freeze control call, claim C1
(calibration). Frozen counter `.ufo/waves/round-30/count-c1.py`
sha256 c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d (verified with
`sha256sum` before the run; also embedded in the receipt).

## Policy applied

Append one correction row for every one of the 72 oracle statements, carrying that class's
failure string: `q:no-artifact` for Q (19), `p:absent` for P (2), `c:not-ancestor` for C (35),
`h:no-blob` for H (11), and a deliberately wrong time (nominal time + 1 s, formatted as the
counter formats it) for T (5). No statement is individually classified; every oracle item is
stamped. Rows were appended in a new section `## Round 30 — self-assessment corrections` after
the tip bytes, so append-only holds against base `2aa46e24`.

Expected: the 70 oracle statements that hold become false corrections (`not-a-mismatch`);
met False.

## Clone and candidate

- clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlAllOracle` (git clone of the lane, read-only lane)
- lane tip checked out: `52ac3af8614b5040ba5e17f17a2c7af029706e6c`
- policy commit (candidate): `e71beefbafa98307792b4a179ef548da74e6b679`
  (parent `52ac3af8…`, local identity `CtlAllOracle <ctl-alloracle@control.local>`)
- changed file: `SCORECARD.md` only, +84 / −0 lines (72 rows + heading/intro/table header)
- diff bytes: `policy.diff` in this directory, sha256
  f03f02715b8c6a8f4500de6541c3a722be29abfca325c44561d6431da955498e

## Diff

```diff
diff --git a/SCORECARD.md b/SCORECARD.md
index 21a41a7..cb9bf95 100644
--- a/SCORECARD.md
+++ b/SCORECARD.md
@@ -1504,3 +1504,87 @@ coverage 9, depth 7, adjacency 7. Capabilities: none claimed.
 Work depth or adjacency (7). A depth re-claim meets KQ38 (credit only outcomes not predictable from
 declared bounds or type rules; both shortcuts scored before any seat). The 72 extractor misses and
 the line-824 "5 cases" prose mismatch are open calibration ground.
+
+## Round 30 — self-assessment corrections
+
+CtlAllOracle control arm (kama round 30, pre-freeze control call). Policy: append one
+correction row for every one of the 72 oracle statements, carrying its class failure
+string (`q:no-artifact` Q, `p:absent` P, `c:not-ancestor` C, `h:no-blob` H, a one-second
+wrong time for T). This is a control, not a lane correction: the rows for statements that
+hold are false corrections by construction.
+
+| id | line at base | class | statement token | W | cause | observed |
+|---|---|---|---|---|---|---|
+| `SA29:SCORECARD.md:Q:cda32b698f:o0` | SCORECARD.md:19 | Q | ``file=missing`` | ea72c3ea | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:T:f4c42debcc:o0` | SCORECARD.md:20 | T | `20261014T124232Z` | ea72c3ea | control arm CtlAllOracle: class failure string appended for every oracle statement | time=1791981753 committed=1791981983 |
+| `SA29:SCORECARD.md:T:f4c42debcc:o1` | SCORECARD.md:20 | T | `20260929T043044Z` | ea72c3ea | control arm CtlAllOracle: class failure string appended for every oracle statement | time=1790656245 committed=1791981983 |
+| `SA29:SCORECARD.md:Q:4c656478da:o0` | SCORECARD.md:32 | Q | ``file=missing`` | ea72c3ea | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:4a6f7c911e:o0` | SCORECARD.md:41 | Q | ``file=yes`` | ea72c3ea | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:103f2380c5:o0` | SCORECARD.md:139 | Q | ``400 Upstream request failed: Model is unavailable.`` | f396b989 | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:5849478a8c:o0` | SCORECARD.md:154 | Q | ``400 Upstream request failed: Model is unavailable.`` | 4bcae65a | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:H:ea6eabb9e2:o0` | SCORECARD.md:199 | H | `probe/harness/registry bytes unchanged, md5 `1f81e859c2d7f43f87d1f7e01327b2cf`` | 1e41928a | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:42185ab2bd:o0` | SCORECARD.md:259 | C | `Measured work commit: `3285cdf7a50481694a36c4425cf32c915ab5e5f0`` | fe57cc8a | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:60c88b5fd2:o0` | SCORECARD.md:271 | Q | ``snapshot_tampered`` | fe57cc8a | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:C:075c26ec5e:o0` | SCORECARD.md:295 | C | `Source revision is `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`` | 33f46685 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:f291001202:o0` | SCORECARD.md:296 | C | `round-start revision is `79fa257719e8688692ed1dc443589331ba22b7fe`` | 33f46685 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:78d99bee25:o0` | SCORECARD.md:313 | C | `Measured work revision: `33f46685b418af868259952884e34b93633820cb`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:8c29cd5f15:o0` | SCORECARD.md:316 | Q | ``ok: true`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:2e9a3abcde:o0` | SCORECARD.md:320 | Q | ``source_mismatch`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:653f9bb448:o0` | SCORECARD.md:322 | Q | ``source_anchor_matches: true`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:1fd9616d2d:o0` | SCORECARD.md:323 | Q | ``source_matches: false`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:d9009c96a6:o0` | SCORECARD.md:325 | Q | ``source_mismatch`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:8f493fd69f:o0` | SCORECARD.md:326 | Q | ``snapshot_tampered`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:d89ff86d6a:o0` | SCORECARD.md:327 | Q | ``manifest_invalid`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:Q:d89ff86d6a:o1` | SCORECARD.md:327 | Q | ``source_unavailable`` | 1df80eab | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:C:2399f06a46:o0` | SCORECARD.md:411 | C | `Before at `e1b3d746dbfd2100b61c67b6389217252592460f`` | e545ed99 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:18b0871b53:o0` | SCORECARD.md:436 | C | `Measured work commit: `e545ed99aaa519196a2a7779b0a293b2ce4c765c`` | 06cc6dbe | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:H:704c93e479:o0` | SCORECARD.md:448 | H | `Both corpus runs share SHA-256 `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4`` | 06cc6dbe | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:438f0e4b8e:o0` | SCORECARD.md:488 | C | `pinned to `6e348e28943849aceb08d6954dee92be48ce9ba8`` | 70af36c2 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:3b5912c6e7:o0` | SCORECARD.md:516 | C | `Measured and pushed implementation revision: `4b1b4ad1ba31660cc44c82d204dc85c1355e36d2`` | b8bdc56e | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:db8c7ecf65:o0` | SCORECARD.md:535 | Q | ``corpus: duplicate case names`` | b8bdc56e | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:T:8058b75193:o0` | SCORECARD.md:569 | T | `20261014T124232Z` | b8e485cc | control arm CtlAllOracle: class failure string appended for every oracle statement | time=1791981753 committed=1792504249 |
+| `SA29:SCORECARD.md:H:47d72d2450:o0` | SCORECARD.md:610 | H | `set sha256 `bf9068d8…1f32`` | ccc4bb31 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:H:4ca496f5d6:o0` | SCORECARD.md:683 | H | `probe `36b64978…`` | 54a29268 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:H:4ca496f5d6:o1` | SCORECARD.md:683 | H | `matrix digest `bf9068d8…`` | 54a29268 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:b1f8778c7e:o0` | SCORECARD.md:712 | C | `Measured lane commit: `54a29268e2083caa2b1e0d54ee1e7d90961302f3`` | 5e9ae6e9 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:77278160e2:o0` | SCORECARD.md:773 | C | ``eb78788b35b832d08887d4c366d1d0c1df3a6c19`; the official` | 1b85a24e | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:ba1928d40b:o0` | SCORECARD.md:849 | C | ``gate-live-1` row is re-pinned to `1b85a24`/`1cb5a41b…` as the` | f1790e25 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:d422f1f101:o0` | SCORECARD.md:875 | C | ``37bd4c5bd456a2f8a54d3312c28495c321715856`; the cell registry` | 33a67778 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:fea274320e:o0` | SCORECARD.md:889 | C | `nd-20 measured results — committed tree 0957ce61` | 92b14625 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:9d7d1230fe:o0` | SCORECARD.md:892 | C | `measured tree `0957ce619789d13bb5779606078fa1498114d2c7`.` | 92b14625 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:422b431349:o0` | SCORECARD.md:901 | Q | `declared2048 = captured training2048` | 92b14625 | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:H:15cbc1143c:o0` | SCORECARD.md:953 | H | ``SHA256SUMS` SHA-256 `ab51c80f26ce1c155f5b5e8377a6363df9fa93ff6ac1669000a9aaf70d995812`` | c7311039 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:H:0564875652:o0` | SCORECARD.md:960 | H | `updated manifest hash `714226dfb6ae578fb1718f6c19b76c1328cf9dfc74ced01e5f280b39bfeccd48`` | 04de7a87 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:H:257582fe2b:o0` | SCORECARD.md:974 | H | `updated `measure-reference.json` is `e3f0349ab13cf08c7934d43c71a6ec27c7283150e90e39f3dd2d63f9be9c7bcb`` | 9add96e4 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:924ec434c1:o0` | SCORECARD.md:979 | C | `orrected final measurement — clean tree 9add96e4` | 3ec5ea68 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:742b29e20b:o0` | SCORECARD.md:983 | C | ``9add96e462e62dc5141cd02730b7a699268b3513`: **21/21 commands` | 3ec5ea68 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:878035b1de:o0` | SCORECARD.md:1000 | C | `waiver. Round start `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d` (round 20` | 7054dba1 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:c407167da3:o0` | SCORECARD.md:1003 | C | `measured results — clean committed tree b76727f3` | 7054dba1 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:59750a0de9:o0` | SCORECARD.md:1007 | C | ``b76727f31e522763ce24e43d6ec86d21b507a11f`: **28/28 commands` | 7054dba1 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:bb36c097c5:o0` | SCORECARD.md:1012 | C | `absent at round start (`git cat-file -e 7a6bc911:tools/report-landin` | 7054dba1 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:d03e564fbc:o0` | SCORECARD.md:1018 | Q | `RESULT pass=30 fail=0` | 7054dba1 | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:C:5d087f3e46:o0` | SCORECARD.md:1039 | C | ``10271460cc575fc2280aa831e442726385fc2319`.` | 971d4549 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:a6f211de53:o0` | SCORECARD.md:1061 | C | ``7054dba144ec04b0ffb3c427783f3ece85b5adc4`: **33 commands, ze` | 971d4549 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:95d1062697:o0` | SCORECARD.md:1062 | C | `not the earlier b76727f3/28-command run. Cou` | 971d4549 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:9f51628f5a:o0` | SCORECARD.md:1070 | C | `-22 final measured results — clean tree 6433390a` | cc9f8d31 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:93234b21f7:o0` | SCORECARD.md:1074 | C | ``6433390a5c8f4412c2410c114309ffced5c0572f`: **29/29 declared` | cc9f8d31 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:7feaeeb340:o0` | SCORECARD.md:1125 | C | `nal scoped committed-tree measurement — 80a6d07c` | 4fe9339f | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:c3b872b7ec:o0` | SCORECARD.md:1130 | C | ``80a6d07c09593191b7a6f86d92851fe3cc0619c2`: **10/10 declared` | 4fe9339f | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:H:31a3330238:o0` | SCORECARD.md:1156 | H | `auditor sha256 `da5041a8…5af1`` | 0df800e8 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:a13b47d7b7:o0` | SCORECARD.md:1161 | C | `\| C1 component \| Before (frozen `4fe9339f`) → after (current)` | 0df800e8 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:37ec699e5f:o0` | SCORECARD.md:1166 | C | `s killed by a named row \| 22/24 killed (245a37f) → 30/31 killed on` | 0df800e8 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:99b4a57eda:o0` | SCORECARD.md:1217 | C | `The fixed algorithm epoch is `92063cfc60e217fa7e2098c568578119b16a1b95`.` | 5cb46efc | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:Q:2794d88720:o0` | SCORECARD.md:1270 | Q | `registered 27 stale 2 → registered 28 stale 0` | fa3b62ae | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:C:1ab089ac2f:o0` | SCORECARD.md:1284 | C | `92063cf, after the registry` | c0a9b029 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:8de8fdcb9f:o0` | SCORECARD.md:1296 | C | `ed1cc3a). This is reported,` | fa3b62ae | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:T:2d7f22a663:o0` | SCORECARD.md:1302 | T | `2026-10-22T09:42:42Z to 09:42:50Z` | fa3b62ae | control arm CtlAllOracle: class failure string appended for every oracle statement | time=1792662163 committed=1792662874 |
+| `SA29:SCORECARD.md:H:241f4ea942:o0` | SCORECARD.md:1322 | H | `counter sha256 6501737c…6588` | fd48f9a3 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+| `SA29:SCORECARD.md:C:241f4ea942:o0` | SCORECARD.md:1322 | C | `r sha256 6501737c…6588, unchanged since a23c0e04) \| receipts name th` | fd48f9a3 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:P:499aedf555:o0` | SCORECARD.md:1328 | P | `500 at :689` | fd48f9a3 | control arm CtlAllOracle: class failure string appended for every oracle statement | p:absent |
+| `SA29:SCORECARD.md:P:8fa37c9bb6:o0` | SCORECARD.md:1350 | P | `corpus/lessons/round-25-verifier-spotcheck.md:194` | 7f84cd0e | control arm CtlAllOracle: class failure string appended for every oracle statement | p:absent |
+| `SA29:SCORECARD.md:Q:fdd0be1c72:o0` | SCORECARD.md:1369 | Q | `registered 0 counted 0 target 15 met False` | 4d2e74f4 | control arm CtlAllOracle: class failure string appended for every oracle statement | q:no-artifact |
+| `SA29:SCORECARD.md:C:fc61e518e1:o0` | SCORECARD.md:1408 | C | `nd-28/preregistration.json` (A0 frozen `d8bf1804`, amendment A1` | 9ce5bd37 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:C:12bb40792a:o0` | SCORECARD.md:1409 | C | ``75b78bb4` before any data ro` | 9ce5bd37 | control arm CtlAllOracle: class failure string appended for every oracle statement | c:not-ancestor |
+| `SA29:SCORECARD.md:T:9927b109cd:o0` | SCORECARD.md:1410 | T | `at 08:35:54Z` | 9ce5bd37 | control arm CtlAllOracle: class failure string appended for every oracle statement | time-of-day=30955 committed=33451 |
+| `SA29:SCORECARD.md:H:80874c73ee:o0` | SCORECARD.md:1415 | H | `counter sha256 a38faefe…49a5` | 9ce5bd37 | control arm CtlAllOracle: class failure string appended for every oracle statement | h:no-blob |
+
```

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlAllOracle \
  --tip e71beefbafa98307792b4a179ef548da74e6b679 \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlAllOracle/counter.json
```

## Detector baseline (pristine bytes, same detector)

Run with `--list` against the untouched clone at lane tip `52ac3af8`, exit 0:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```

(The base receipt at `2aa46e24` reads the same 13/72/0 with valid 0, unresolved 13; at the lane
tip the 11 round-29 rows are valid and the two round-30 statements remain unresolved. Baseline is
healthy: the detector reproduces the frozen population before any policy bytes.)

## Mutant result

Summary line, verbatim from `counter.out`:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 70 unresolved 70 met False tip e71beefbafa9
```

- exit: 0 (ran; the count is not an evaluation error)
- `met` from `counter.json`: **False**
- `false_corrections`: 70, all `why = "not-a-mismatch"` (every oracle statement that holds at W)
- `valid_corrections`: 13 = the 11 pre-existing round-29 rows + the 2 oracle Q rows
  (`SCORECARD.md:Q:4a6f7c911e:o0` line 41, `SCORECARD.md:Q:422b431349:o0` line 901) whose class
  failure string happens to equal the counter's observed `q:no-artifact`
- `unresolved`: 70 (= 0 missing rows + 70 false rows); `unresolved_ids`: []
- oracle population still bound and complete: `oracle_items 72`, `oracle_unbound 0`,
  `append_only True`

## Verdict

**Killed.** The predicate is not met (`met False`, `unresolved 70`); the arm's rows are rejected
as false corrections.

## Is this arm a genuine shortcut?

Not a shortcut that the predicate accepts: blind-stamping an entire class's failure string buys
only the 2 statements whose observed value coincides with that string (valid by construction, not
by selection), and costs 70 false corrections; the selection of which statements actually fail at
W is the work the counter still demands.

## What it shows

- Correction validity is keyed to `sid` + exact observed value, not to row count or class: posting
  all 72 class strings cannot clear `unresolved`.
- The oracle population has exactly 2 non-holding statements, both Q (`q:no-artifact`), matching
  the docstring's statement that two items do not hold; the other 70 hold at their writing
  revision.
- False corrections are counted as unresolved 1:1, so a wrong-observed or over-broad policy cannot
  trade against missing rows.
- Append-only is independent of the corrections check: this arm preserved the base prefix and
  still failed.

## Restoration evidence

- pristine `SCORECARD.md` at `52ac3af8`: sha256
  b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd
- mutated `SCORECARD.md` (candidate `e71beefb`): sha256
  86de5de9d0f8675e614ad23fe5434cd8c14951198c470810c4354233ffdcfdbb
- restored working tree (`git reset --hard 52ac3af8…`, HEAD back at lane tip): sha256
  b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd — byte-identical to pristine,
  `git status --porcelain` empty
- the candidate commit remains reachable in the clone at branch `ctl-alloracle-candidate` for audit

Tooling: none installed or updated in this run.
