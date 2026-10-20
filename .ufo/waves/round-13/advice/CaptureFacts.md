# Round 13 — CaptureFacts: Source Retrieval, Capture vs. Comparison Operations

**Seat:** `KamaR13.CaptureFacts` (scout)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Target:** Read Round 12 `reproduce.py` and `fidelity.py` source retrieval operations, distinguish actual capture operation from independent source comparison; identify exact lines.  
**Boundaries:** Leaf scout seat. Read-only static investigation; no gate/build/test/linter/formatter/smoke commands executed. No LSP server was mounted in this session; evidence rests on static file and AST inspection, not grep output as proof. Tools installed/updated: none.

---

## 1. Executive Summary & Core Discrepancy

In `corpus/QUALITY.md:49`, criterion **KQ15** defines the admission and falsification rules for frozen historical snapshots. Round 12 verifier spotcheck (`corpus/lessons/round-12-verifier-spotcheck.md` §Routed defects and dispositions D1, line 147) routed two precision defects in KQ15:

1. **Finding IDs vs. Exit Classes:** KQ15 claimed mismatch, tamper, and unavailable source have "distinct nonzero exits", whereas code and registry map `source_mismatch` to exit `1` and both `snapshot_tampered` and `source_unavailable` to shared exit `2` (stable distinct finding IDs; audit literal: `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`).
2. **Capture vs. Comparison Mechanisms:** KQ15 asserted that:
   > *"A frozen historical copy is compared byte-for-byte with the blob fetched directly as `git show <pinned-commit>:<source-path>`..."*

Static inspection of Round 12 implementation (`fidelity.py` and `reproduce.py`) demonstrates that **`git show` is never invoked by the comparator or reproduction runner**. Rather:
- **Actual Capture:** Performed offline once using `git show` (raw stdout) to generate the corrective snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md`, bypassing tool-display truncation (S032).
- **Independent Comparison:** Performed programmatically at runtime by `fidelity.py` and `reproduce.py` using `git cat-file blob <revision>:<path>` against hardcoded anchor constants.
- **Required Audit Phrase for KQ16:** `capture: git show; comparison: git cat-file blob`.

---

## 2. Source Retrieval in `fidelity.py` (Exact Code & Line Citations)

File: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py`

### 2.1 Immutable Anchor Constants (`fidelity.py:44–48`)
The historical source anchor is hardcoded as immutable constants independent of CLI arguments or manifest contents:
```python
SOURCE_REVISION = '2f7303c242319c1dc96c6bcf7702ac18b3ca1aad'
SOURCE_PATH = 'corpus/SOURCES.md'
SOURCE_BLOB_OID = '7de1360655eadada356fe110813c6e1338142551'
SOURCE_SHA256 = '9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a'
SOURCE_BYTES = 18898
```

### 2.2 Git Execution Safety Wrapper (`fidelity.py:80–111`)
Git commands are invoked directly via `subprocess.run` (no shell) with inherited `GIT_*` environment variables stripped and replace objects suppressed:
```python
def git_run(repo, *arguments):
    command = ['git', '--no-pager', '--no-replace-objects']
    if repo is not None:
        command += ['-C', str(repo)]
    command += list(arguments)
    ...
```

### 2.3 Repository Root Validation (`fidelity.py:114–121, 251–259`)
- Line 115: `git_run(repo, 'rev-parse', '--show-toplevel')`
- Line 256: Ensures `toplevel == repo_path`, rejecting execution against misdirected or unvouched repositories.

### 2.4 Programmatic Source Retrieval & Verification (`fidelity.py:261–286`)
In `evaluate()`:
- **Lines 261–262:** Verifies the commit-ish path OID:
  ```python
  oid_output, oid_error = git_run(
      repo_path, 'rev-parse', '--verify', f'{SOURCE_REVISION}:{SOURCE_PATH}')
  ```
- **Lines 271–274:** Retrieves the actual source blob bytes via `git cat-file blob`:
  ```python
  blob, blob_error = git_run(
      repo_path, 'cat-file', 'blob',
      f'{SOURCE_REVISION}:{SOURCE_PATH}')
  ```
- **Lines 280–294:** Validates the retrieved blob against all three immutable anchor constants:
  ```python
  source_available = True
  source_bytes = blob
  anchor_matches = (source_oid == SOURCE_BLOB_OID
                    and sha256(blob) == SOURCE_SHA256
                    and len(blob) == SOURCE_BYTES)
  checks.append({'id': 'source_anchor', 'ok': anchor_matches})
  if not anchor_matches:
      findings.append({
          'id': 'source_unavailable',
          'detail': f'retrieved git blob {source_oid} sha256 '
                    f'{sha256(blob)} bytes {len(blob)} is not the '
                    f'pinned blob {SOURCE_BLOB_OID} sha256 '
                    f'{SOURCE_SHA256} bytes {SOURCE_BYTES}; the '
                    f'repository cannot vouch for the pinned anchor'})
  ```

### 2.5 Byte-for-Byte Comparison (`fidelity.py:296–311`)
- **Lines 296–298:** Compares snapshot bytes with retrieved source bytes:
  ```python
  if snapshot_bytes is not None:
      source_matches = snapshot_bytes == source_bytes
      checks.append({'id': 'source_correspondence',
                     'ok': source_matches})
  ```
- **Lines 299–311:** If bytes differ, identifies exact offset via `first_difference` and appends `source_mismatch` finding:
  ```python
  if not source_matches:
      offset = first_difference(snapshot_bytes, source_bytes)
      source_diff = {'first_difference_offset': offset,
                     'snapshot_bytes': len(snapshot_bytes),
                     'source_bytes': len(source_bytes)}
      findings.append({
          'id': 'source_mismatch',
          ...})
  ```

### 2.6 Selftest Pinned Source Blob Retrieval (`fidelity.py:443–447`)
In isolated `selftest()`, the source blob is also retrieved via `cat-file blob`:
```python
source, error = git_run(
    source_repo, 'cat-file', 'blob',
    f'{SOURCE_REVISION}:{SOURCE_PATH}')
```

**Key Finding:** Across all 626 lines of `fidelity.py`, `git show` appears **0 times** (the string `"show"` appears only in `'--show-toplevel'` at line 115).

---

## 3. Source Retrieval in `reproduce.py` (Exact Code & Line Citations)

File: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/reproduce.py`

### 3.1 Pinned Constants (`reproduce.py:15–19`)
```python
REV, SPATH = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad", "corpus/SOURCES.md"
SPEC = f"{REV}:{SPATH}"
OID = "7de1360655eadada356fe110813c6e1338142551"
SHA = "9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a"
NBYTES = 18898
```

### 3.2 Git Subprocess Helper (`reproduce.py:49–50`)
```python
def git(*args: object, keep: bool = True) -> tuple[dict, bytes]:
    return run(["git", "--no-pager", "--no-replace-objects", "-C", ROOT, *args], keep=keep)
```

### 3.3 Independent Source Blob Retrieval & Falsification (`reproduce.py:79–92`)
`reproduce.py` performs an independent check of the git object database outside of `fidelity.py`:
- **Line 79:** `oid_rec, oid_b = git("rev-parse", "--verify", SPEC)`
- **Line 80:** `blob_rec, blob = git("cat-file", "blob", SPEC, keep=False)`
- **Lines 81–90:** Validates both the retrieved source blob and the snapshot files:
  ```python
  src = sha(blob)
  source_checks = {
      "oid": oid_rec.get("exit") == 0 and oid_b.decode("utf-8", "replace").strip() == OID,
      "sha256": blob_rec.get("exit") == 0 and src == SHA,
      "bytes": blob_rec.get("exit") == 0 and len(blob) == NBYTES,
      "new_matches": new is not None and sha(new) == src,
      "new_pinned": new is not None and sha(new) == SHA,
      "old_differs": old is not None and sha(old) != src,
      "old_pinned": old is not None and sha(old) == OLD_SHA,
  }
  ```
- **Lines 91–92:** `if not all(source_checks.values()): errors.append("independent source anchor/correspondence checks failed")`

**Key Finding:** In `reproduce.py`, `git show` appears **0 times**. The runner independently retrieves the source via `git cat-file blob` at line 80.

---

## 4. Distinguishing Actual Capture Operation from Independent Source Comparison

| Dimension | Actual Capture Operation | Independent Source Comparison |
|---|---|---|
| **Git Command** | `git show <revision>:<path>` | `git cat-file blob <revision>:<path>` |
| **Execution Context** | One-shot artifact generation during round development | Automated runtime evaluation inside gate and runner |
| **Callsite Location** | Manual / CLI shell pipeline (documented in notes) | `fidelity.py:271–274, 443–447`; `reproduce.py:80` |
| **Output Target** | Disk file `.ufo/waves/round-12/frozen/corpus/SOURCES.md` | In-memory `bytes` object compared against snapshot bytes |
| **Cited Documentation** | S032 (`git show` manual DESCRIPTION & DISCUSSION) | S033 (`git cat-file` manual §OUTPUT) |
| **Sourced Quote** | "For plain blobs, it shows the plain contents." | "If `<type>` is specified, the raw (though uncompressed) contents of the `<object>` will be returned." |
| **Protocol Role** | Evidence preservation (prevention of truncation) | Falsification check (enforcing source correspondence) |
| **KQ15 Inaccuracy** | Stated as the *comparison* command in `QUALITY.md:49` | Omitted from KQ15; actually used by code and verifier |

### 4.1 Historical Context & Why Capture Used `git show`
In Round 11, the frozen snapshot `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` had been captured through a tool session that truncated long lines and appended the display marker:
`[Some lines truncated to 768 bytes. Use artifact://1157:raw:55-55 to read line 55 whole]`.
Because Round 11's gate only verified digest self-consistency against `expected.json` (transport integrity), the truncation went undetected (Defect D1).

In Round 12, to obtain a pristine, untruncated copy of `2f7303c:corpus/SOURCES.md`:
- Authoring used `git show <rev>:<path>` raw stdout directly redirected to file.
- S032 was opened at [Git git-show manual](https://git-scm.com/docs/git-show) (Git 2.56.0), where DESCRIPTION states: *"For plain blobs, it shows the plain contents."*
- `SKILL.md:396` explicitly records: `"default snapshot .ufo/waves/round-12/frozen/corpus/SOURCES.md captured byte-exactly via git show, never tool-rendered text"`.
- `corpus/lessons/round-12.md:14–15` explicitly records: `"Capture uses git show (S032); the same measurement command independently reads the pinned historical blob with git cat-file blob for comparison."`

### 4.2 Why Programmatic Comparison Uses `git cat-file blob`
For automated evaluation in code (`fidelity.py` and `reproduce.py`):
- `git cat-file blob` is Git plumbing specifically designed for raw byte extraction without user-facing pagination, diff formatting, or log formatting.
- `cat-file` ensures exact byte fidelity without risk of log-family decorations.
- Round 12 verifier spotcheck (`corpus/lessons/round-12-verifier-spotcheck.md:59–62`) independently used `cat-file blob` to verify the 1 → 0 count.
- S033 (opened in Round 13) provides the documentation grounding for this plumbing comparator: §OUTPUT states *"If `<type>` is specified, the raw (though uncompressed) contents of the `<object>` will be returned."*

---

## 5. Bounded Evidence Matrix for KQ16 Formulation

To satisfy the Round 12 verifier spotcheck D1 disposition (`round-12-verifier-spotcheck.md:147`) and round criteria:

1. **Exact Required Phrases:**
   - Literal: `capture: git show; comparison: git cat-file blob`
   - Literal: `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
2. **Preservation:**
   - Old KQ15 text in `corpus/QUALITY.md:49` remains untouched (append-only history).
   - KQ16 appends as the superseding row for these two precision defects, leaving KQ14 semantic boundaries, manifest integrity requirements, and historical receipts intact.

---

## 6. Limits and Verification Boundary

- **No Fresh Execution:** All citations are derived from static source reading of committed files (`fidelity.py`, `reproduce.py`, `round-12.md`, `round-12-verifier-spotcheck.md`, `SKILL.md`, `QUALITY.md`). No gate scripts, tests, or reproduction commands were executed by this seat.
- **Receipt Observations:** Mentions of test outcomes or counts are observations of committed receipt data (`acceptance.json`), never fresh runs.
- **Leaf Boundary:** No subagents or background tasks dispatched.
- **No Servicing Claims:** These findings pertain solely to calibration C1 (source correspondence precision debt). No claims are made regarding model serving, live runtime operability, or capability acquisition.

Report: .ufo/waves/round-13/advice/CaptureFacts.md
