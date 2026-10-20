# UFO-FSD Connector: IntegrityConnection (Round 12)

**Author:** `KamaR12.IntegrityConnection` (connector; author advisor, not closure)  
**Lane:** `kama-shokunin` (`/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Date:** 2026-10-20  
**Target:** Connect KQ14 and D1: content correspondence vs pointer bounds vs digest integrity. Propose minimal falsification obligations shared fidelity CLI should satisfy; static review, no runs.  
**Tools installed/updated:** none.

---

## 1. Context & Named Axes

Per the Godspeed posture and UFO-FSD connector charter, we analyze the round's declared axes without smoothing contradictions into scalar estimates:
- **`calibration`** (Primary focus, claim C1, lowest assigned axis 7 vs operability 8): Exact-source frozen evidence correspondence; repair of auxiliary snapshot defect D1 ($1 \to 0$ mismatch reduction); separate source correspondence from digest integrity; zero scalar score inflation ($7 \to 7$, $\Delta 0$).
- **`quality`**: Durability and precision of admission criteria and falsification controls; synthesis connecting KQ14 (semantic/human boundary, pointer bounds $\neq$ content correspondence) and defect D1 (digest integrity $\neq$ source correspondence) into KQ15.
- **`operability`**: Unchanged; no serving capability, endpoint integration, daemon alteration, or live probe claimed.
- **`freshness`**, **`depth`**, **`adjacency`**: Strictly unchanged; local historical-evidence repair and cross-lane boundary hygiene.

---

## 2. Evidence: The Tripartite Triangulation (KQ14 vs D1 vs KQ15)

Through static evaluation of the Round 11 closure spot-check (`corpus/lessons/round-11-verifier-spotcheck.md:101-118`), the quality ledger (`corpus/QUALITY.md`), and the Round 11 reproduction architecture (`.ufo/waves/round-11/reproduce.py`), three distinct epistemic layers emerge:

```
+---------------------------------------------------------------------------------------+
| Epistemic Dimension   | Verification Mechanism      | Necessary Defect Caught / Limit  |
+---------------------------------------------------------------------------------------+
| 1. Pointer Bounds     | Shape-only `test -e`,       | Catches missing path, truncated  |
|    & Textual Coverage | `wc -l`, line counters      | file extents; CANNOT prove       |
|    (KQ7 / KQ14)       |                             | content validity or pin fidelity |
+-----------------------+-----------------------------+----------------------------------+
| 2. Digest Integrity   | SHA-256 hash match against  | Catches local file drift or      |
|    (Static Manifest)  | pinned manifest/expected    | in-flight tampering; CANNOT      |
|    (D1 Vulnerability) | (e.g. `expected.json`)      | prove historical git origin      |
+-----------------------+-----------------------------+----------------------------------+
| 3. Source / Content   | Exact byte-for-byte stream  | Catches corrupt capture, tool    |
|    Correspondence     | compare against immutable   | display truncations, pagination  |
|    (D1 / KQ15)        | blob (`git cat-file blob`)  | markers; CANNOT replace human/   |
|                       |                             | source semantic interpretation   |
+---------------------------------------------------------------------------------------+
```

### 2.1 The Pointer Bounds / Shape-Evidence Limitation (KQ14)
KQ14 established that "a correction ledger separately records textual coverage, pointer bounds, content correspondence and terminal unknown/dead states... a zero uncorrected count or in-bounds pointer alone proves the old claim true; shape-only `test -e`/`wc -l` is used to infer file-body pin presence or absence."
- In Round 10/11, shape-only checks (e.g. `wc -l ~/.config/opencode/opencode.json` $\implies 5$) established presence and bounds, but could not attest to whether internal configuration bodies carried a live pin.
- Pointer bounds define *structural existence*, never *semantic truth*.

### 2.2 The Digest Integrity Circularity (Defect D1)
In Round 11, `reproduce.py` checked:
$$\text{sha256}(\text{snapshot on disk}) \stackrel{?}{=} \text{expected.json}[\text{snapshot}]$$
- The snapshot was generated from tool-rendered terminal output (`read` tool footer with pagination marker `artifact://1157` and severed line 55 at byte 768).
- The corrupted file on disk hashed to `52665cf2...`.
- `expected.json` was populated with `52665cf2...`.
- The digest comparison returned green (exit 0, `frozen_digests_verified: 11`).
- **Defect D1 proves:** A self-consistent digest check proves only that the file on disk matches the author's declared manifest. It provides zero guarantee that the artifact corresponds to git history (`2f7303c...:corpus/SOURCES.md`, actual SHA-256 `9dc40d25...`).

### 2.3 The Content Correspondence Boundary (KQ15 & KQ14)
Even when exact source correspondence is verified by comparing snapshot bytes against `git cat-file blob 2f7303c...:corpus/SOURCES.md`:
- Source correspondence verifies that the frozen snapshot is an authentic byte-for-byte replica of an immutable git commit.
- However, per KQ14's continuing ceiling: verifying that a snapshot matches git history does **not** prove that the claims made in that historical text are true or that cited upstream endpoints behave as documented. Content correspondence anchors the historical artifact; human/source review establishes semantic claims.

---

## 3. The Proposed Move: Decoupled Falsification Obligations for `fidelity.py`

To resolve D1, satisfy KQ14/KQ15, and prevent coherent snapshot+manifest spoofing, the shared CLI `fidelity.py` must enforce **four decoupled falsification obligations**:

### Obligation 1: Immutable In-Code Source Anchors (Anti-Coherent Tamper)
Authority must reside in code constants, never in manifest fields or CLI arguments:
```python
SOURCE_COMMIT = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad"
SOURCE_PATH = "corpus/SOURCES.md"
SOURCE_BLOB_OID = "7de1360655eadada356fe110813c6e1338142551"
SOURCE_BLOB_SHA256 = "9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a"
```
*Obligation:* If a caller supplies a coherent snapshot + manifest mutation pointing to a different commit or recomputing the manifest hash over non-source bytes, the CLI must compare against `SOURCE_COMMIT` and emit exit 1 (`source_mismatch`), NOT exit 0 (`clean`) or exit 2 (`snapshot_tampered`).

### Obligation 2: Raw Object Extraction without Environment Poisoning
Source extraction must bypass smudge filters, textconv, replace refs, and git environment overrides:
```python
env = {
    "PATH": os.environ.get("PATH", ""),
    "HOME": os.environ.get("HOME", ""),
    "LC_ALL": "C",
    "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
}
# Execute raw blob retrieval:
# git --no-pager --no-replace-objects -C <repo> cat-file blob <SOURCE_COMMIT>:<SOURCE_PATH>
```
*Obligation:* The extracted stream must match `SOURCE_BLOB_SHA256` (and `SOURCE_BLOB_OID` if verified). If the git object store fails to return the expected blob, the outcome is exit 2 (`source_unavailable`), never a false mismatch.

### Obligation 3: Separation of Manifest Integrity from Source Correspondence
The CLI must compute and output two distinct boolean results:
1. `source_correspondence`: `sha256(snapshot_bytes) == sha256(git_blob_bytes)`
2. `digest_integrity`: `sha256(snapshot_bytes) == manifest["snapshot_sha256"]` (when manifest is present)

*Exit Map:*
- `clean` (Exit 0): `source_correspondence == True` AND `digest_integrity == True`
- `source_mismatch` (Exit 1): `source_correspondence == False` AND (`digest_integrity == True` OR `--manifest` omitted/unpinned)
- `snapshot_tampered` (Exit 2): `digest_integrity == False` (manifest exists, but snapshot hash does not match manifest pin)
- `source_unavailable` (Exit 2): Git repository, commit, or blob cannot be resolved or is corrupted.

### Obligation 4: Unpinned Override Semantics
To allow observing the historical defect D1 without triggering `snapshot_tampered`:
- Invoking `fidelity.py --snapshot .ufo/waves/round-11/frozen/before/corpus/SOURCES.md` with no manifest explicitly operates in **unpinned observation mode**.
- The CLI evaluates source correspondence directly against `SOURCE_COMMIT:SOURCE_PATH`.
- Because the Round 11 snapshot differs from `9dc40d25...`, the CLI emits exit 1 (`source_mismatch`).
- This formalizes the $1 \to 0$ transition: Round 11 snapshot produces 1 mismatch; Round 12 corrective snapshot (`.ufo/waves/round-12/frozen/corpus/SOURCES.md`) produces 0 mismatches.

---

## 4. Second-Order Effects & Contradiction Analysis

1. **The Circularity Trap (Digest vs Source):**
   - *Tension:* Engineers instinctively trust cryptographic hashes (`expected.json`). However, a digest over a flawed snapshot immortalizes the flaw.
   - *Resolution:* Manifests verify *transport/storage integrity* against tampering; `git show` / `git cat-file blob` verifies *historical correspondence*. Neither can substitute for the other.
2. **The Selftest Paradox:**
   - *Tension:* A pure `--selftest` in an isolated temp directory cannot easily synthesize commit `2f7303c...` without risking injection hooks or flags that weaken production enforcement.
   - *Resolution:* The CLI must support an isolated, read-only `--repo` flag pointing to the lane root for clean/mismatch tests against the real object store, or use isolated mocked blobs strictly gated within `--selftest` child invocations, while production CLI flags strictly forbid commit/path overrides.
3. **The Semantic Ceiling (KQ14):**
   - *Tension:* A green `source_mismatch: 0` run might be misconstrued as proof that the underlying registry claims are true.
   - *Resolution:* The CLI report and quality documentation must explicitly reiterate that exact snapshot fidelity is an evidence-preservation property, not empirical verification of external model endpoints or runtime behavior.

---

## 5. Verification Checks Named for L1 Main

This seat performed **no executions, tests, or builds**. Upon integration, L1 Main must verify:
1. `git cat-file blob 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md | sha256sum` yields `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`.
2. `sha256sum .ufo/waves/round-12/frozen/corpus/SOURCES.md` matches `9dc40d25...` identically.
3. Static check that `fidelity.py` pins `SOURCE_COMMIT` and `SOURCE_PATH` as constants and rejects overrides via CLI or manifest.
4. Old Round 11 snapshot evaluation produces exit 1:
   `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-11/frozen/before/corpus/SOURCES.md` $\implies$ exit 1 (`source_mismatch`).
5. New Round 12 snapshot evaluation produces exit 0:
   `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-12/frozen/corpus/SOURCES.md` $\implies$ exit 0 (`clean`).
6. Tampered snapshot produces exit 2:
   Mutating one byte in a temporary snapshot with default manifest $\implies$ exit 2 (`snapshot_tampered`).
7. Coherent mutation attack produces exit 1:
   Mutating a snapshot and updating its manifest hash in a temporary directory $\implies$ exit 1 (`source_mismatch`).
8. `python3 .ufo/waves/round-12/fidelity.py --selftest` $\implies$ exit 0 across isolated controls.
9. Full reproduction via `python3 .ufo/waves/round-12/reproduce.py` $\implies$ overall exit 0.
