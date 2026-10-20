# SnapshotRecon — Round 11 Snapshot Corruption Reconnaissance (Defect D1)

**Seat:** `KamaR12.SnapshotRecon` (scout)  
**Lane:** `kama-shokunin` (`/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Date:** 2026-10-20  
**Scope:** Static analysis of Round 11 defect D1 from `corpus/lessons/round-11-verifier-spotcheck.md`, `.ufo/waves/round-11/frozen/expected.json`, and `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` against git commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.  
**Axes:**  
- `calibration`: (C1 calibration: exact-source frozen evidence correspondence, old auxiliary snapshot mismatch $1 \to 0$ in new corrective snapshot; explicit separation of source correspondence from digest integrity).  
- `operability`: (unchanged; leaf scout, no runtime or endpoint mutation).  
- `quality`: (accurate defect characterization supporting KQ15; historical evidence honesty).  
- `freshness`, `depth`, `adjacency`: (unchanged).  

---

## 1. Ground Truth Context & Defect D1 Authority

In `corpus/lessons/round-11-verifier-spotcheck.md:101-118`, the independent closure reviewer (`CloseKamaR11`) identified **Auxiliary snapshot defect D1**:
- The frozen snapshot of `corpus/SOURCES.md` captured in Round 11 failed literal comparison against the pinned historical source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
- While all nine knowledge blobs in `.ufo/waves/round-11/frozen/before/corpus/knowledge/` matched their git blobs byte-for-byte, `SOURCES.md` did not.
- The closure review established that a green digest check in `reproduce.py` proved only integrity against the shipped `expected.json` file, not correspondence with git history.

---

## 2. Characterization of the Old Corruption

Static byte and line analysis comparing the historical git blob (`2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`) with the Round 11 frozen copy (`.ufo/waves/round-11/frozen/before/corpus/SOURCES.md`):

### 2.1 File Metrics & Digest Discrepancy

| Metric | Git Blob (`2f7303c...:corpus/SOURCES.md`) | Round 11 Frozen Snapshot (`frozen/before/corpus/SOURCES.md`) | Delta |
|---|---|---|---|
| **SHA-256** | `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` | `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` | Mismatch |
| **Byte Size** | 18,898 bytes | 18,793 bytes | -105 bytes |
| **Total Lines** | 60 lines | 63 lines | +3 lines |
| **Differing Lines** | Line 55 (truncated) | Line 55 (truncated) + Lines 61–63 (tool marker) | Lines 55, 61–63 |

### 2.2 Exact Line 55 Truncation

Line 55 is the third entry in `## Search log`: `- **2026-10-19 — community claims sweep.**`.

- **Committed Git Line 55 (964 bytes, ending with complete sentence):**
  ```markdown
  - **2026-10-19 — community claims sweep.** Question: do community posts establish a native Ollama Prometheus `/metrics` endpoint or a universal LLM health-check convention? Queries: `Ollama Prometheus /metrics endpoint monitoring issue forum blog`; `site:reddit.com/r/ollama "Prometheus" "/metrics" Ollama`; `universal LLM health check endpoint convention forum blog health readiness`; `LLM universal health check endpoint /health inference server convention github issue`. Where: public web-search index (Reddit, GitHub issue trackers). Identified 39 (10, 9, 10, 10), screened 39 at title/snippet, included 3 (S027–S029), excluded 36 (non-community docs, gateway/proxy material, off-topic, unverifiable anecdote; one Reddit post blocked on fetch → Leads). Stop: the sweep yields project-specific requests, not a cross-engine contract; more anecdotes cannot establish universality. No absence claim about an Ollama `/metrics` route is drawn from this sweep.
  ```

- **Frozen Snapshot Line 55 (769 bytes, truncated at 768-byte buffer boundary):**
  ```markdown
  - **2026-10-19 — community claims sweep.** Question: do community posts establish a native Ollama Prometheus `/metrics` endpoint or a universal LLM health-check convention? Queries: `Ollama Prometheus /metrics endpoint monitoring issue forum blog`; `site:reddit.com/r/ollama "Prometheus" "/metrics" Ollama`; `universal LLM health check endpoint convention forum blog health readiness`; `LLM universal health check endpoint /health inference server convention github issue`. Where: public web-search index (Reddit, GitHub issue trackers). Identified 39 (10, 9, 10, 10), screened 39 at title/snippet, included 3 (S027–S029), excluded 36 (non-community docs, gateway/proxy material, off-topic, unverifiable anecdote; one Reddit post blocked on fetch → Leads). St…
  ```
  - Byte offset 0 to 765: Byte-identical between git blob and frozen copy.
  - Byte offset 765 to 769: Instead of `op: the sw...`, the frozen file contains `t\xe2\x80\xa6\n` (`t…\n`).
  - Missing content: The final 198 bytes of line 55 were severed.

### 2.3 Tool-Rendered Pagination Artifact (Lines 61–63)

At the end of the frozen file, three extra lines were captured:
```markdown
[Line 61: \n]
[Line 62: \n]
[Line 63:] [Some lines truncated to 768 bytes. Use artifact://1157:raw:55-55 to read line 55 whole]
```
This is the standard presentation footer emitted by the Cursor / agent harness `read` tool when displaying long lines in an interactive terminal or truncated tool response. The author in Round 11 saved tool-rendered text into `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` rather than extracting raw bytes via `git show`.

### 2.4 Preserved Registry Integrity

Lines 1–54 and lines 56–60 are 100% byte-identical to the git blob. Specifically:
- Registry table (lines 12–42) containing rows S001 through S030 is untouched.
- 30 rows: 27 Tier A, 3 Tier C; 17 mined, 8 queued, 5 rejected.
- Census metrics and knowledge citations derived from the table rows in Round 11 were uncorrupted by D1.

---

## 3. Why the Internal Digest Passed in Round 11

In `.ufo/waves/round-11/reproduce.py:28-37`:
```python
expected = json.loads((WAVE / 'frozen/expected.json').read_text())
mismatches = []
for name, digest in expected['inputs'].items():
    path = ROOT / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        mismatches.append(name)
if mismatches:
    print(json.dumps({'error': 'snapshot_tampered', 'inputs': mismatches}))
    return 2
```

In `.ufo/waves/round-11/frozen/expected.json:13`:
```json
".ufo/waves/round-11/frozen/before/corpus/SOURCES.md": "52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1"
```

### 3.1 The Circular Verification Loop
1. When the Round 11 author created the frozen snapshot tree, they generated `expected.json` by hashing the local files already placed in `.ufo/waves/round-11/frozen/`.
2. The already-corrupted file on disk hashed to `52665cf2...`.
3. That corrupted hash was committed as the expected digest in `expected.json`.
4. `reproduce.py` checked only:
   $$\text{sha256}(\text{file on disk}) \stackrel{?}{=} \text{expected.json}[\text{file}]$$
5. Because the file on disk was unchanged since `expected.json` was generated, the equality held (`52665cf2... == 52665cf2...`).

### 3.2 Absence of Historical Source Correspondence Verification
1. Neither `reproduce.py` nor `measure.py` ever invoked `git show` or queried `source_revision: 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`.
2. `measure.py provenance` only measured the 9 files defined in `legacy-baseline.json`. `SOURCES.md` was not in `legacy-baseline.json`.
3. `SOURCES.md` was merely an auxiliary frozen input inside `expected['inputs']`.
4. **Core Failure:** The verification checked **digest integrity** against a local manifest, but conflated it with **source correspondence** against git history. Digest integrity verifies that a local artifact has not been modified since a manifest was authored; it does not verify that the manifest or artifact faithfully represents the historical commit it purports to freeze.

---

## 4. Architectural Prescriptions for Round 12 (Claim C1)

To resolve defect D1 under Claim C1 ($7 \to 7$, mismatch $1 \to 0$):

1. **Immutability of Prior Evidence:**
   - Round 11 frozen files (`.ufo/waves/round-11/frozen/**`) must NOT be edited or overwritten.
   - Defect D1 must be resolved via a new, separate corrective snapshot under `.ufo/waves/round-12/frozen/`.
2. **Raw Byte Extraction:**
   - `.ufo/waves/round-12/frozen/corpus/SOURCES.md` must be produced directly from `git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md` (exact 18,898 bytes, SHA-256 `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`). Tool-rendered strings or pagers must never be used.
3. **Separate Source Correspondence from Digest Integrity:**
   - The CLI (`fidelity.py`) must report source correspondence separately from manifest digest integrity.
   - Pinned manifest (`.ufo/waves/round-12/frozen/expected.json`) must pin the snapshot SHA-256, source commit (`2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`), and source path (`corpus/SOURCES.md`).
4. **Explicit Exit Code Semantics:**
   - Exit `0`: `clean` (both source correspondence with git blob and snapshot manifest integrity pass).
   - Exit `1`: `source_mismatch` (snapshot bytes do not match git blob at pinned commit).
   - Exit `2`: `snapshot_tampered` (snapshot bytes do not match manifest) or `source_unavailable` (git commit/blob cannot be resolved).
5. **Fail-Capable Controls & Reproduction:**
   - Evaluating old Round 11 snapshot without manifest must yield exit 1 (`source_mismatch`), documenting the $1 \to 0$ transition.
   - Isolated `--selftest` and runner (`reproduce.py`) must verify clean, mismatch, tamper, and unavailable exit conditions.

---

## 5. Unrun Disclaimer (Contract Compliance)

Per leaf subagent constraints, **no verification runs, builds, or tests were executed by this seat**. The byte counts, line lengths, SHA-256 digests, and tool-marker strings reported above were obtained via read-only static inspection and git object inspection. No files outside this report were created or modified.

---

## 6. Verification Checks Named for L1 Main

Upon integration of Round 12, L1 Main should run:
1. `git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md | sha256sum`  
   Confirm exact match: `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`.
2. `sha256sum .ufo/waves/round-12/frozen/corpus/SOURCES.md`  
   Confirm exact match with git blob hash above.
3. `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-11/frozen/before/corpus/SOURCES.md`  
   Confirm exit 1 (`source_mismatch`) when run against the old Round 11 snapshot.
4. `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-12/frozen/corpus/SOURCES.md`  
   Confirm exit 0 (`clean`) when run against the new corrective snapshot with default manifest.
5. `python3 .ufo/waves/round-12/fidelity.py --selftest`  
   Confirm exit 0 across all synthetic isolated controls.
6. `python3 .ufo/waves/round-12/reproduce.py`  
   Confirm overall exit 0 and verified 1 $\to$ 0 mismatch reduction receipt.

---

Tools installed/updated: none.
