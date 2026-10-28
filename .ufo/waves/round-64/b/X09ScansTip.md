# X09ScansTip - C2 supporting scans at the freeze commit (wave b)

Freeze commit f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (base 0c1eff3c). Advisory findings only; no ledger, source or git state touched in the lane. Scratch clone used only for the "after" check (removed).
No tools installed or upgraded.

## Scan outputs (run from the lane, `--repo . --rev f6a4ea9a...`; raw files in out/X09ScansTip/)

```
digest-ledger.py scan   (exit 0):
tokens=149 blob=130 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0
hexrun-census.py scan   (exit 1):
tokens=2092 distinct=404 lane_oid=281 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1
round42-selfdesc-reconcile.py --repo . --tip f6a4ea9a... (exit 0):
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=63 met=True
```
Base 0c1eff3c for comparison: digest `tokens=145 ... unknown=0`, hexrun identical to the line above (`unknown=1`).
So the freeze commit's +4 digest tokens are the four SOURCES.md fetched-bytes digests, and the hexrun `unknown=1` is NOT new at the freeze: it came in with the round-63 verifier spot-check commit (0c1eff3c).

## Unknown runs (the whole list)

Only one run is flagged unknown anywhere:

| run | scan | cited at | needs |
|---|---|---|---|
| `72c7713ef48cd5d5d02964ece2975602e3402a08` (40-hex) | hexrun unknown=1 (2 occurrences) | corpus/lessons/round-63-verifier-spotcheck.md:5 and :17 | hexrun-ledger.tsv row, class `upstream` (it is the fleet-repo commit "round-63: kama report" by kama-shokunin, committer 2026-10-28T20:30:56-03:00; `git cat-file -t` in the fleet checkout says commit; GitHub `git/commits/<sha>` returned 200 with the sha echoed, message "round-63: kama report") |

Not an object of the lane repo, so it cannot be lane_oid; the ledger's `upstream` class needs a committed evidence blob that contains the token and the repo text `VeigaPunk/shokunin`.
I built that evidence file in the format of registry's round-43 files (compact JSON `{"repo":...,"response":<api body>}`, no trailing newline): out/X09ScansTip/evidence-72c7713ef48cd5d5d02964ece2975602e3402a08.json (fetched 2026-10-28 via `gh api repos/VeigaPunk/shokunin/git/commits/<sha>`). The L1 must commit it at the path named in the proposed row.

Proposed row (out/X09ScansTip/proposed-hexrun-ledger-rows.tsv, TAB-separated like the ledger):
```
72c7713ef48cd5d5d02964ece2975602e3402a08	upstream	VeigaPunk/shokunin	.ufo/waves/round-64/b/out/X09ScansTip/evidence-72c7713ef48cd5d5d02964ece2975602e3402a08.json		2026-10-28	commit: fleet-repo report commit 'round-63: kama report' by kama-shokunin <kama@shokunin.local> at 2026-10-28T20:30:56-03:00 (git/commits 200, sha echoed); cited at corpus/lessons/round-63-verifier-spotcheck.md:5 and :17
```
(If the L1 prefers the round-43 convention, move the evidence file to `.ufo/waves/round-43/c2/evidence/<sha>.json` and change the 4th cell; any blob at the revision works.)

## What the freeze commit added, and what each needs

1. **Four SOURCES.md fetched-bytes digests (S529-S532)**: corpus/SOURCES.md rows for proc_pid_fd (3a50ddef...ff27e), proc_pid_stat (0f04d789...6700f), proc_pid_environ (93394d9e...62c46), proc_pid_cmdline (1fc68168...a91f15). Each equals the sha256 of the committed blob `.ufo/waves/round-64/source/proc_pid_<name>.html` (verified by hashing git blobs), so the scanner classes them `blob`. **No ledger row needed.** The scan is unknown=0 because those source files are committed.
2. **40-hex ids in freeze.txt** (`0c1eff3cb9ac...` line 2; also c1-base.txt): lane objects (`git cat-file -e` ok). Also outside scan scope (`.ufo/` is excluded by both tools) and not unknown. **No row needed.** The 73 40-hex ids in census/start.out are all already in hexrun-ledger.tsv and also out of scope.
3. **Library digests in tools/round64-c1-counter.py** (LIBS table, lines 83-137, plus MODEL_SHA/SERVER_SHA lines 48-49, 233): **not seen by either tool** - both scan only `.md`/`.tsv` outside `.ufo/`, so `.py` files are a scope gap, not an `unknown`. Checked by hand over the freeze diff's added lines (out/X09ScansTip/scope-gap.txt): of the 30 distinct 64-hex runs in the counter, 3 are already in digest-ledger.tsv (MODEL_SHA `270cba1b...` row 6, SERVER_SHA `b6a31a8e...` row 21, libllama-server-impl `e404b91a...` row 3) and **27 have no ledger row** (UNCLASSIFIED in my scan). All 29 LIBS entries (28 libraries + llama-server) re-hash on this host from /home/vgpnk/.local/opt/llama-b11755/<name> to exactly the pinned value, and the same-named members of the retained S038 archive llama-b11755-bin-ubuntu-x64.tar.gz (extracted to scratch) are byte-identical (0 mismatches).
   Proposed: 27 `external` rows in out/X09ScansTip/proposed-digest-ledger-rows.tsv, same columns as digest-ledger.tsv (digest, class, subject, path, correct, verified-at, note), e.g.
```
574946133f3fd58a87cf4c7b70955a51fe71a6b7841b75eb419074d56b791e2f	external	libggml-base.so.0.27.0 of the installed llama.cpp b11755 tree (S038; member of the pinned library table LIBS in tools/round64-c1-counter.py, which ...)	/home/vgpnk/.local/opt/llama-b11755/libggml-base.so.0.27.0		2026-10-28	installed library re-hashed by seat X09ScansTip, <bytes> bytes; sha256sum matches and the same-named member of the retained S038 archive is byte-identical
```
   These rows are **optional for the scan** (digest-ledger counts only cited tokens in scanned documents; unreferenced rows do not change any count - see below). They matter if the C2 pin table or a later scan scope extends to `.py`; today the evidence for those 27 is the counter itself plus this report.

## After-check (scratch clone of f6a4ea9a with the 28 proposed rows + evidence file committed)

```
digest-ledger.py scan: tokens=149 blob=130 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   (unchanged)
hexrun-census.py scan: tokens=2092 distinct=404 lane_oid=281 md5_blob=1 upstream_ok=110 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0   (exit 0)
reconcile: ... mismatches=0 maxN=63 met=True
```
So the single hexrun row turns hexrun unknown 1 -> 0 (exit 1 -> 0), and the 27 digest rows are accepted (ledger_bad=0) without changing the digest line.

## Observations (calibration)
- `hexrun-census.py scan` exits 1 at the freeze and at base: a standing ledger gap since the round-63 spot-check, so the "ledger scans" milestone is not green until the one row above lands. The reconciler is green at maxN=63 (it has no round-64 conjunct yet: that is the wave-b executor item).
- Scanner scope gap: neither tool reads `.py` or `.ufo/`; 27 pinned digests (and the 40-hex ids in freeze.txt/start.out) are uncovered by design. A C2 counter that claims "no cited digest unexplained" should state that scope.
- The "four fetched-bytes digests" are blob-class (committed html), not external; they need no row.

Receipts (out/X09ScansTip/): digest-scan.txt, digest-scan-details.txt, hexrun-scan.txt, hexrun-scan-details.txt (405 lines), reconcile.txt, scope-gap.txt, proposed-digest-ledger-rows.tsv (27 rows), proposed-hexrun-ledger-rows.tsv (1 row), evidence-72c7713e....json, after-digest-scan.txt, after-hexrun-scan.txt.

Counter line (item asks): `tokens=2092 distinct=404 lane_oid=281 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=1` (hexrun) / `... unknown=0` (digest) / `mismatches=0 ... met=True` (reconcile)
