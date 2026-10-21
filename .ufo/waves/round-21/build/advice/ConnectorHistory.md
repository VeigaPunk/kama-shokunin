VERDICT: confirm - R21 closes R19 TreeCap debt and R20 routed defects without double-crediting prior claims

## 1. Verified Evidence & Observed Exits
- `python3 tools/report-landing-audit.py --no-errata` -> exit 1 (9 defects: 1 hash mashup r20, 8 omitted r10x1 r18x3 r20x4).
- `python3 tools/report-landing-audit.py` -> exit 0 (`summary reports=11 defects=9 corrected=9 uncorrected=0 status=clean`).
- `python3 tools/report-landing-audit.py --selftest` -> exit 0 (`selftest cases=15 failed=0`).
- `python3 tests/llamacpp-live/check-receipt.py --selftest` -> exit 0 (`9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations`).
- `python3 tests/llamacpp-live/install-links-grid.py --selftest` -> exit 0 (`selftest cases=12 failed=0`).
- `python3 tests/llamacpp-live/install-links-grid.py --arm current` -> exit 0 (`link=9/9 regular=2/2 type=1/1 null=0/1`).
- `python3 tests/llamacpp-live/install-links-grid.py` -> exit 1 (frozen arm misses all symlink cells: `link=0/9`; current `link=9/9`).

## 2. R19 / R20 Promises Closed by R21
- **Symlinked soname identity** (`SCORECARD.md:921` Planned row): CLOSED by R21 C2. Implements `install_links()` (`tools/kama-llamacpp-live.py:202-230`), `--expect-install-links-sha256` in gate (`tests/llamacpp-live/check-receipt.py:170-192, 438-470, 2301-2304`), and 13-cell grid (`tests/llamacpp-live/install-links-grid.py:1-332`).
- **R19 TreeCap debt** (`corpus/lessons/round-19.md:53-57, 77` [M3]; `round-19-verifier-spotcheck.md:206`): CLOSED by R21 C2. R19's `install_tree()` only pinned regular files; soname symlinks escaped. R21 records `{basename: link text}` and digests `name -> text\n`.
- **R20 closure routed defects D1 & D2** (`MANIFEST.json:10112` notes): CLOSED by R21 C1 via `registry/report-landing-errata.tsv:3-7`. D1 (r20 report line 7 spliced hash `0957ce619789d13d894ef21bc863486bcb35b56c`) and D2 (r20 Landed changes omitting commits `33a6777`, `0957ce6`, `92b1462`, `846e366`) are machine-audited by `tools/report-landing-audit.py:1-404` across rounds 10-20.

## 3. R19 / R20 Promises Remaining Open
- **Historical crash-as-kill leaves outside 15-cell set** (`SCORECARD.md:920`, `corpus/lessons/round-20.md:88-91` naming `MutantsGridCrash`, `GateSelftestCrash`, `KillCensus`): REMAINS OPEN. R21 does not touch `tools/error-verdict-census.py`.
- **Broader receipt-header minimization** (`SCORECARD.md:920-921`, `corpus/lessons/round-20.md:113-115`): REMAINS OPEN.
- **K05/other-engine serving evidence** (`SCORECARD.md:921-922`, `.ufo/reports/round-20/kama.md:64`): REMAINS OPEN.
- **Carried R19 debts: TreeDeterminism, GridDefaults, SentinalSecrets** (`round-19-verifier-spotcheck.md:206-207`, `round-20/kama.md:64`): REMAIN OPEN.
- **Outside non-author spot-check sample for discernment** (`SCORECARD.md:841, 938`): REMAINS OPEN.
- **Host-level debts:** Dead positive controls / `qwen-coder.service` (`corpus/lessons/round-4-recensus.md:25-27`, `corpus/lessons/round-20.md:90-91`) and L0 archive question `kama|round-17` (`MANIFEST.json:10112`): REMAIN OPEN (operator-owned).

## 4. AXES "No Double Credit" Assessment
- **C1 Calibration (7 -> 7/8):** No double credit.
  - Distinct from R19 C1 (`tools/citation-provenance.py`): R19 audited micro-syntax `cite(<rev>, <path>, sha256=...)` inside in-repo docs against git blobs. R21 C1 audits fleet reports (`.ufo/reports/round-N/kama.md`) against git log histories for commit existence and landed-commit completeness.
  - Distinct from R20 C1 (`tools/error-verdict-census.py`): R20 fixed error-vs-kill exit classifications in test scripts.
  - Zero shared counting artifacts or recycled tokens; R19's 17 required citations remain undisturbed (`citation-provenance.py` exits 0).
- **C2 Operability (8 -> 8):** No double credit.
  - R19 C2 credited regular-file pinning (`install_tree_sha256`) and member swaps in `install-tree-grid.py` (`SCORECARD.md:828-836`). It explicitly disclaimed symlink security (`TreeCap` debt).
  - R21 C2 specifically targets the blind spot: frozen arm catches 0/9 link mutations; current arm catches 9/9 link mutations. Regular and type controls pass on both.
  - Back-compatibility is preserved (`install_tree_sha256 equal=True`), operability score is held at 8 -> 8 (delta 0), and no duplicate capability row is claimed.
