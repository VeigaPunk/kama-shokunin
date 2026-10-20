# SourceShow — S032 `git-show` Manual Evidence, Scope & Capture Mechanics

**Seat:** `SourceShow` (scout / `KamaR13.SourceShow`)  
**Date:** 2026-10-20 UTC  
**Target:** Open S032 `git-show` manual; locate plain blobs quote and scope; distinguish capture mechanics from independent verification.  
**Report Path:** `.ufo/waves/round-13/advice/SourceShow.md`  
**Lane Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`  
**Boundary:** Leaf scout; read-only static inspection; no checks executed; no subagent dispatch; tools installed/updated: none.

---

## 1. Named Axes & Context Binding

- **Active Axis:** **Calibration** (Claim C1: score $7 \to 7$, $\Delta 0$; lowest assigned axis 7 vs operability 8). Bounded textual criterion correspondence: resolving two routed KQ15 discrepancies ($2 \to 0$):
  1. Finding IDs vs exit classes: `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`.
  2. Capture vs comparison mechanics: `capture: git show; comparison: git cat-file blob`.
- **Other Axes (Unchanged):** Operability (8), Freshness (unchanged), Coverage (unchanged), Depth (unchanged), Adjacency (unchanged), Quality (improved via Round 12 D4 knowledge interpretation, not gate machinery), Discernment (improved via outside review sampling), Expansion (unchanged; census row addition is verification instrumentation, not domain expansion).

---

## 2. Documentation Authority & S032 Registry Record

- **Source Identifier:** S032
- **Document Title:** Git git-show manual
- **Primary Canonical URL:** `https://git-scm.com/docs/git-show`
- **Versioned URL Anchor:** `https://git-scm.com/docs/git-show/2.56.0` (manual last updated in Git 2.56.0, 2026-09-28)
- **Local Host Git Environment:** Git 2.55.0 (`git show --help` man page inspected statically)
- **Access Date:** 2026-10-20 (opened in Round 12, re-verified Round 13)
- **Registry Entry (`corpus/SOURCES.md:44`):**
  - **Tier:** A
  - **Kind:** docs
  - **Status:** mined
  - **Scope:** Byte-preserving historical blob retrieval for kama evidence capture, not endpoint truth
  - **Recheck:** on-release
  - **Used-by:** `corpus/lessons/round-12.md`

---

## 3. Located Quotes & Exact Context

All quotes are verified verbatim from the official Git documentation (`git-show(1)`):

### 3.1 Plain Blobs Output Semantics (Primary S032 Quote)
- **Section:** `DESCRIPTION` (`https://git-scm.com/docs/git-show#_description`)
- **Context:** Contrasts object-type formatting (commits display log/diff; tags display tagger/object; trees display names via `ls-tree`; blobs display contents).
- **Exact Quote (8 words):**
  > "For plain blobs, it shows the plain contents."
- **Word Count:** 8 whitespace-delimited words (strictly $\le 25$ words).
- **Observed Fact:** When passed a blob object or revision:path referencing a blob, `git show` suppresses commit metadata, log headers, and diff decorations, outputting only the plain blob contents.

### 3.2 Core Byte Storage Invariant (Grounding Quote)
- **Section:** `DISCUSSION` (`https://git-scm.com/docs/git-show#_discussion`, paragraph 2)
- **Context:** Character encoding handling across Git core objects.
- **Exact Quote (20 words):**
  > "The contents of the blob objects are uninterpreted sequences of bytes. There is no encoding translation at the core level."
- **Word Count:** 20 whitespace-delimited words (strictly $\le 25$ words).
- **Observed Fact:** Git's core object database treats blob payloads as raw, uninterpreted byte arrays without transcoding, line-ending translation, or character set conversion.

### 3.3 Revision:Path Syntax Semantics (Syntax Grounding)
- **Section:** `EXAMPLES` (`https://git-scm.com/docs/git-show#_examples`, item 3)
- **Context:** Explaining `git show next~10:Documentation/README`.
- **Exact Quote (20 words):**
  > "Shows the contents of the file Documentation/README as they were current in the 10th last commit of the branch next."
- **Word Count:** 20 whitespace-delimited words (strictly $\le 25$ words).
- **Observed Fact:** The `<revision>:<path>` syntax directly addresses the historical state of the file at that revision.

---

## 4. Scope & Epistemic Boundaries

1. **Declared Scope:**
   - `"Byte-preserving historical blob retrieval for kama evidence capture, not endpoint truth"` (`corpus/SOURCES.md:44`).
2. **Explicit Negative Boundaries:**
   - **Not Endpoint Truth:** S032 documents Git tool behavior; it attests nothing regarding local runtime serving endpoints, Ollama/vLLM health, or model weights.
   - **Not Outcome Proof:** S032 validates the capture command's intended semantics; it does not prove that any specific captured file matches historical commit bytes or passes integrity checks.
   - **Not Verification Comparator Authority:** S032 documents `git show`, not the comparator (`git cat-file blob`).
3. **Inference vs Observed Fact on "Byte-Preserving":**
   - **Observed:** S032 text asserts "plain contents" (DESCRIPTION) and "uninterpreted sequences of bytes" (DISCUSSION).
   - **Inference (`[INFERENCE]`):** The term "byte-preserving" in S032's scope cell is an inference from local repository conditions: no Git smudge/clean filters or textconv attributes are assigned to `corpus/SOURCES.md`, ensuring that `git show` stdout matches the raw blob bytes identically.

---

## 5. Distinction: Capture Mechanics vs Independent Verification

A primary defect identified in outside verifier spot-check D1 (`corpus/lessons/round-12-verifier-spotcheck.md:144–147`) and round-12 advice (`AttackSourceCuration.md:58–73`) was that KQ15 conflated capture with verification:

$$\text{Conflated Formulation (KQ15): } \text{"compared byte-for-byte with the blob fetched directly as git show..."}$$

Static analysis of the codebase reveals the true operational division:

### 5.1 Capture Mechanics (`git show`)
- **Operation:** Operational generation of auxiliary snapshot file `.ufo/waves/round-12/frozen/corpus/SOURCES.md`.
- **Execution:** One-shot capture command:
  ```sh
  git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md > .ufo/waves/round-12/frozen/corpus/SOURCES.md
  ```
- **Governing Authority:** S032 (`git-show` manual). It explains why running `git show <rev>:<path>` produces the clean file content suitable for freezing as a snapshot.

### 5.2 Independent Verification & Comparator Mechanics (`git cat-file blob`)
- **Operation:** Automated verification of snapshot correspondence and historical anchor integrity.
- **Code Reality (`fidelity.py` and `reproduce.py`):**
  - `fidelity.py:271–274`:
    ```python
    blob, blob_error = git_run(
        repo_path, 'cat-file', 'blob',
        f'{SOURCE_REVISION}:{SOURCE_PATH}')
    ```
  - `reproduce.py:80`:
    ```python
    blob_rec, blob = git("cat-file", "blob", SPEC, keep=False)
    ```
- **Plumbing Isolation:** Verification executes `git cat-file blob` in a sanitized subprocess with `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null` (`fidelity.py:80–90`).
- **Governing Authority:** S033 (`git-cat-file` manual §OUTPUT: "If `<type>` is specified, the raw (though uncompressed) contents of the `<object>` will be returned"). S032 does *not* document `git cat-file`.

### 5.3 Comparative Summary Table

| Dimension | Capture Mechanics | Verification / Comparison |
|---|---|---|
| **Command** | `git show <rev>:<path>` | `git cat-file blob <rev>:<path>` |
| **Git Layer** | Porcelain (log/inspection family) | Plumbing (object database retrieval) |
| **Documenting Source** | **S032** (`git-show` manual) | **S033** (`git-cat-file` manual) |
| **Timing & Frequency** | Once, during snapshot preparation | Every verification / gate execution |
| **Code References** | Historical capture script / log | `fidelity.py:271–274`, `reproduce.py:80` |
| **Output Property** | "plain contents" (S032 DESCRIPTION) | "raw contents of the object" (S033 OUTPUT) |
| **KQ16 Literal Audit Phrase** | `capture: git show` | `comparison: git cat-file blob` |

---

## 6. Independence Caveat

- Neither `git show` nor `git cat-file blob` provides external or statistical independence: both query the same underlying `.git/objects/` object store in the same repository.
- Their independence is strictly operational and procedural:
  1. The frozen snapshot was captured once via `git show`.
  2. The verifier independently dereferences the immutable blob OID (`7de1360655eadada356fe110813c6e1338142551`) via `git cat-file blob`.
  3. Correspondence is confirmed by byte-for-byte equality against code-pinned constant `SOURCE_SHA256 = '9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a'`.
- S032 docs/A evidence prevents circular method authority by referencing official Git documentation rather than own-work fiat, but it cannot certify the truth of the file contents.

---

## 7. Observed Facts vs Inference vs Unresolved Gaps

- **Observed Facts:**
  - `git show` manual DESCRIPTION states literally: `"For plain blobs, it shows the plain contents."` (8 words).
  - `git show` manual DISCUSSION states literally: `"The contents of the blob objects are uninterpreted sequences of bytes. There is no encoding translation at the core level."` (20 words).
  - `corpus/SOURCES.md:44` documents S032 as docs/A mined, used-by `corpus/lessons/round-12.md`.
  - `fidelity.py:271–274` and `reproduce.py:80` call `git cat-file blob`, not `git show`.
  - `corpus/QUALITY.md:49` (KQ15) inaccurately asserted comparison directly with `git show`.
- **Inference (`[INFERENCE]`):**
  - "Byte-preserving" holds because repository configuration lacks custom smudge/clean/textconv filters for Markdown files.
- **Unresolved Gaps:**
  - None within S032 scope. S033 addition is assigned to `Sources`; KQ16 supersession wording is assigned to `Criterion`.

---

## 8. Named Verification Checks for L1 Main

Per the leaf scout contract, this seat performed only read-only static inspection and executed no tests or verification runs. L1 Main should run:
1. Verify exact quote and location in official Git manual:
   ```sh
   git show --help | grep -F "For plain blobs, it shows the plain contents."
   ```
2. Verify S032 row in SOURCES:
   ```sh
   grep '^| S032 ' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
   ```
3. Verify comparator implementation uses `git cat-file`:
   ```sh
   grep -n "cat-file" /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py
   ```
