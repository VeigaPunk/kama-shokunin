# ReceiptFacts — Round 12 Historical acceptance.json Recorded Outputs

author: KamaR13.ReceiptFacts (scout)  
Date: 2026-10-20 UTC  
Target: Parse/read round 12 `acceptance.json` historical recorded outputs for mismatch, tamper, and unavailable; report exact fields and exits without executing lane code.  
Root: `/home/vgpnk/Projects/shokunin/kama-shokunin`  
Report: `.ufo/waves/round-13/advice/ReceiptFacts.md`  

---

## 1. Axes & Posture (Godspeed)

- **calibration (C1)**: Grounds the 2 -> 0 criterion discrepancy reduction for KQ15 -> KQ16 (finding IDs vs exit classes, and capture vs comparison methods) in static receipt facts; score 7 -> 7.
- **operability**: Unchanged; no serving runtime, probe, or endpoint code executed or modified.
- **freshness**: Unchanged; historical receipt parsing does not alter runtime freshness.
- **coverage**: Unchanged; addresses calibration precision debt, not new surface.
- **depth**: Unchanged; historical verification artifact analysis.
- **adjacency**: Unchanged; no fleet, orchestrator, or sibling boundary modification.
- **quality**: Supported by round 12 D4 knowledge-interpretation grounding rather than gate machinery.
- **discernment**: Improved; separates stable finding IDs from exit classes and verifies actual historical execution data.

---

## 2. Receipt Scope & Static Boundary

Artifact parsed statically:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/acceptance.json`

Boundary constraints:
- **No lane code executed**: Neither `reproduce.py`, `fidelity.py`, `--selftest`, nor test/gate suites were executed.
- All data below are static observations of committed historical receipts (`acceptance.json`, `fidelity.py`), preserving round 12 receipt ground truth.

Top-level receipt metadata:
- Command: `["python3", "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/reproduce.py"]`
- Working directory (`cwd`): `"/home/vgpnk/Projects/shokunin"`
- Outer exit: `0`
- Inner result schema: `"kama-round-12-reproduction/v1"`
- Measured commit: `"33f46685b418af868259952884e34b93633820cb"`
- Status: `ok: true`, `exit: 0`, `errors: []`, `failures: []`
- Pinned anchor in receipt:
  - Revision: `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`
  - Path: `corpus/SOURCES.md`
  - Blob OID: `7de1360655eadada356fe110813c6e1338142551`
  - SHA-256: `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`
  - Bytes: `18898`
  - Old snapshot SHA-256: `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1`

---

## 3. Recorded Outputs for Mismatch, Tamper, Unavailable

### 3.1 Mismatch (`source_mismatch`)
Recorded across three receipt records: `records.before`, `records.coherent`, and child fixtures in `records.selftest`.

1. **`records.before`** (historical round-11 snapshot evaluation against code anchor, unpinned):
   - Command: `["/usr/bin/python3", ".../fidelity.py", "--snapshot", ".../round-11/frozen/before/corpus/SOURCES.md", "--manifest", "none", "--repo", ".../kama-shokunin"]`
   - Exact exit: `1`
   - Exact `finding`: `"source_mismatch"`
   - Exact `mismatches`: `1`
   - Exact `correspondence`: `"mismatch"`
   - Exact `integrity`: `"not_checked"`
   - Exact `integrity_result`: `"not_checked"`
   - Exact `pinned`: `false`
   - Exact `source_anchor_matches`: `true`
   - Exact `source_available`: `true`
   - Exact `source_matches`: `false`
   - Exact `source_diff`: `{"first_difference_offset": 18283, "snapshot_bytes": 18793, "source_bytes": 18898}`
   - Exact `findings`:
     - `{"id": "unpinned", "detail": "no manifest pin: snapshot integrity not checked; a clean verdict cannot be certified"}`
     - `{"id": "source_mismatch", "detail": "snapshot differs from 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md at byte offset 18283 (snapshot 18793 bytes, source 18898 bytes)"}`
   - Exact `checks`:
     - `{"id": "source_anchor", "ok": true}`
     - `{"id": "source_correspondence", "ok": false}`

2. **`records.coherent`** (coherent snapshot + manifest mutation attack control):
   - Exact exit: `1`
   - Exact `finding`: `"source_mismatch"`
   - Exact `mismatches`: `1`
   - Exact `correspondence`: `"mismatch"`
   - Exact `integrity`: `"checked"`
   - Exact `integrity_result`: `"match"`
   - Exact `pinned`: `true`
   - Exact `snapshot_pin_matches`: `true`
   - Exact `source_anchor_matches`: `true`
   - Exact `source_available`: `true`
   - Exact `source_matches`: `false`
   - Exact `source_diff`: `{"first_difference_offset": 18898, "snapshot_bytes": 18924, "source_bytes": 18898}`
   - Exact `findings`: `[{"detail": "snapshot differs from 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md at byte offset 18898 (snapshot 18924 bytes, source 18898 bytes)", "id": "source_mismatch"}]`

3. **`records.selftest` mismatch fixtures**:
   - `coherent-snapshot-and-manifest-mutation`: `exit: 1`, `finding: "source_mismatch"`, `mismatches: 1`
   - `unpinned-source-mismatch`: `exit: 1`, `finding: "source_mismatch"`, `mismatches: 1`

---

### 3.2 Tamper (`snapshot_tampered`)
Recorded in `records.tamper` and child fixtures in `records.selftest`.

1. **`records.tamper`** (pin corruption on pristine snapshot bytes):
   - Command: `["/usr/bin/python3", ".../fidelity.py", "--snapshot", "/tmp/.../ts", "--manifest", "/tmp/.../tm", "--repo", ".../kama-shokunin"]`
   - Exact exit: `2`
   - Exact `finding`: `"snapshot_tampered"`
   - Exact `mismatches`: `0` (source correspondence matched: bytes equal source anchor)
   - Exact `correspondence`: `"match"`
   - Exact `integrity`: `"checked"`
   - Exact `integrity_result`: `"mismatch"`
   - Exact `pinned`: `true`
   - Exact `snapshot_pin_matches`: `false`
   - Exact `source_anchor_matches`: `true`
   - Exact `source_available`: `true`
   - Exact `source_matches`: `true`
   - Exact `source_diff`: `null`
   - Exact `findings`: `[{"detail": "snapshot sha256 9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a does not match manifest pin 0000000000000000000000000000000000000000000000000000000000000000", "id": "snapshot_tampered"}]`
   - Exact `checks`:
     - `{"id": "snapshot_pin", "ok": false}`
     - `{"id": "source_anchor", "ok": true}`
     - `{"id": "source_correspondence", "ok": true}`

2. **`records.selftest` tamper fixtures**:
   - `snapshot-tampered` (mutated snapshot with clean expected manifest): `exit: 2`, `finding: "snapshot_tampered"`, `mismatches: 1`
   - `pin-only-corruption-exact-snapshot` (clean snapshot with corrupt manifest pin): `exit: 2`, `finding: "snapshot_tampered"`, `mismatches: 0`

---

### 3.3 Unavailable (`source_unavailable`)
Recorded in `records.unavailable` and child fixtures in `records.selftest`.

1. **`records.unavailable`** (source repository unavailable/empty control):
   - Command: `["/usr/bin/python3", ".../fidelity.py", "--snapshot", ".../SOURCES.md", "--manifest", ".../expected.json", "--repo", "/tmp/.../empty"]`
   - Exact exit: `2`
   - Exact `finding`: `"source_unavailable"`
   - Exact `mismatches`: `0`
   - Exact `correspondence`: `"unavailable"`
   - Exact `integrity`: `"checked"`
   - Exact `integrity_result`: `"match"`
   - Exact `pinned`: `true`
   - Exact `snapshot_pin_matches`: `true`
   - Exact `source_anchor_matches`: `null`
   - Exact `source_available`: `false`
   - Exact `source_bytes`: `null`
   - Exact `source_diff`: `null`
   - Exact `source_error`: `"fatal: Needed a single revision"`
   - Exact `findings`: `[{"detail": "git rev-parse 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md failed: fatal: Needed a single revision", "id": "source_unavailable"}]`
   - Exact `checks`:
     - `{"id": "snapshot_pin", "ok": true}` (anchor and correspondence checks not executed due to unavailable source)

2. **`records.selftest` unavailable fixtures**:
   - `source-unavailable` (empty repository): `exit: 2`, `finding: "source_unavailable"`, `mismatches: 0`
   - `snapshot-unavailable` (absent snapshot): `exit: 2`, `finding: "snapshot_unavailable"`, `mismatches: 0`
   - `symlink-snapshot-rejected` (symlink snapshot rejected): `exit: 2`, `finding: "snapshot_unavailable"`, `mismatches: 0`

---

## 4. Synthesis of Discrepancies (KQ15 Errata Grounding)

### 4.1 Exit Classes vs. Stable Finding IDs
- **Literal audit phrase**:
  `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
- **Observed fact**:
  `source_mismatch` emits exit `1`. Both `snapshot_tampered` and `source_unavailable` emit exit `2` (the shared "could-not-evaluate / integrity / validity failure" class).
- **KQ15 wording error**:
  `corpus/QUALITY.md:49` stated: *"mismatch, snapshot tamper and unavailable source each have distinct nonzero exits"*.
- **Ground truth from receipt**:
  They do **not** have three distinct exit codes. They have distinct, stable **finding IDs** (`source_mismatch`, `snapshot_tampered`, `source_unavailable`), but share exit code `2` for tamper and unavailable.

### 4.2 Capture vs. Comparison Methods
- **Literal audit phrase**:
  `capture: git show; comparison: git cat-file blob`
- **Observed fact**:
  - In `acceptance.json` (`source.blob_record.cmd`) and `fidelity.py:272`:
    Comparison retrieves the historical blob via `git cat-file blob 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`.
  - In `advice/Fidelity.md:19-21`:
    Initial snapshot generation/capture was authored via `git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`.
- **KQ15 wording error**:
  `corpus/QUALITY.md:49` referred only to `git show <pinned-commit>:<source-path>` without distinguishing capture mechanics from independent comparison mechanics.

---

## 5. Confidence, Unknowns, and Tooling

- **Confidence**: High (100% grounded in static JSON byte parsing of committed artifact `acceptance.json` and static code inspection of `fidelity.py`).
- **Remaining unknowns**: None for receipt field and exit enumeration.
- **Tooling report**: Tools installed/updated: **none**.
