# GitSource — Official Git `git-show` Revision:Path Blob Retrieval Semantics

**Seat:** `GitSource` (scout / `KamaR12.GitSource`)  
**Date:** 2026-10-20  
**Scope:** Official Git documentation on `git-show` and revision:path blob retrieval semantics supporting direct byte extraction for Round 12 historical-evidence repair (claim C1 calibration, addressing verifier spotcheck defect D1).  
**Boundary:** Leaf scout corroboration only; no registry row created; no new claim; tools installed/updated: none.

---

## 1. Documentation Authority & Access Evidence

- **Primary Source:** Official Git Documentation (`git-show` manual, Git 2.49+ / local host 2.55.0)
- **Primary URL:** `https://git-scm.com/docs/git-show`
- **Access Date:** 2026-10-20 (UTC)
- **Supporting Specification URL:** `https://git-scm.com/docs/gitrevisions` (Section *SPECIFYING REVISIONS*)
- **Access Date:** 2026-10-20 (UTC)

---

## 2. Located Quotes & Exact Semantics

### 2.1 Revision:Path File Content Retrieval Semantics (`git-show` §EXAMPLES)
- **Location:** `https://git-scm.com/docs/git-show#_examples`
- **Context/Example:** `git show next~10:Documentation/README`
- **Located Quote (20 words):**
  > "Shows the contents of the file Documentation/README as they were current in the 10th last commit of the branch next."
- **Word Count:** 20 whitespace-delimited words (strictly $\le 25$ words).
- **Semantics:** Specifies that the `<rev>:<path>` syntax passed to `git show` dereferences the tree-ish commit object at `<rev>` and extracts the contents of `<path>` as they existed at that exact revision.

### 2.2 Plain Blob Output Semantics (`git-show` §DESCRIPTION)
- **Location:** `https://git-scm.com/docs/git-show#_description`
- **Context:** Object-type handling distinction (commits vs. trees vs. tags vs. plain blobs).
- **Located Quote (8 words):**
  > "For plain blobs, it shows the plain contents."
- **Word Count:** 8 whitespace-delimited words (strictly $\le 25$ words).
- **Semantics:** Distinguishes blob retrieval from commits, tags, or trees. When resolving a blob object, `git show` suppresses commit metadata, diff logs, and directory formatting, emitting only the target object's plain contents.

### 2.3 Direct Byte Extraction & Uninterpreted Encoding (`git-show` §DISCUSSION)
- **Location:** `https://git-scm.com/docs/git-show#_discussion`
- **Context:** Character encoding handling across Git objects.
- **Located Quote (20 words):**
  > "The contents of the blob objects are uninterpreted sequences of bytes. There is no encoding translation at the core level."
- **Word Count:** 20 whitespace-delimited words (strictly $\le 25$ words).
- **Semantics:** Establishes the core Git invariant that blob payloads are raw, uninterpreted byte sequences with zero encoding transcoding. Direct binary extraction (`subprocess.run(..., capture_output=True)` without text-mode decoding) yields the exact bytes stored in the Git object database.

### 2.4 Supporting Syntax Definition (`gitrevisions` §SPECIFYING REVISIONS)
- **Location:** `https://git-scm.com/docs/gitrevisions`
- **Context:** Subsection `<rev>:<path>, e.g. HEAD:README, master:./README`
- **Located Quote (20 words):**
  > "A suffix : followed by a path names the blob or tree at the given path in the tree-ish object"
- **Word Count:** 20 whitespace-delimited words (strictly $\le 25$ words; excerpt of full sentence terminating at clause boundary).
- **Semantics:** Defines the `:` syntax as resolving the specified relative path inside a tree-ish revision to its immutable underlying blob OID.

---

## 3. Direct Application to Round 12 & Defect D1 Resolution

1. **Defect D1 Ground Truth:**
   - In Round 11, the frozen snapshot `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` diverged from git history (`52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` vs actual `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`) because line 55 was truncated by harness/tool display rendering (`artifact://1157`).
2. **Direct Byte Extraction Principle:**
   - As documented by Git core semantics above, invoking `git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md` (or `git cat-file blob 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`) and piping standard output directly to disk extracts the unmodified, uninterpreted sequence of bytes.
3. **Fidelity Implementation Alignment (`fidelity.py`):**
   - The fidelity verifier MUST read standard output in raw binary mode (`text=False`), computing SHA-256 over raw bytes to ensure zero line-ending normalization or UTF-8 re-encoding, preserving exact correspondence with the immutable Git object database.

---

## 4. Boundary & Non-Claim Status

- **Corroboration Only:** This finding confirms the exact command semantics used by the Round 12 fidelity verification engine (`fidelity.py` and `reproduce.py`).
- **No Registry Row:** No row is added to `corpus/SOURCES.md` (does not increment the 31-row census or create a new S-row).
- **No Score Movement:** Claim C1 remains strictly Calibration $7 \to 7$ ($\Delta 0$), measuring defect resolution $1 \to 0$ without score inflation.
- **Tools Installed/Updated:** None.

---

## 5. Verification Checks Named for L1 Main

Per leaf scout contract, this seat runs no checks, builds, or tests. L1 Main should run:
1. `git show 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md | sha256sum` (confirm output is `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`).
2. `sha256sum .ufo/waves/round-12/frozen/corpus/SOURCES.md` (confirm new snapshot matches the exact source commit SHA-256).
3. `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-12/frozen/corpus/SOURCES.md --manifest .ufo/waves/round-12/frozen/expected.json` (confirm clean exit 0).
4. `python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-11/frozen/before/corpus/SOURCES.md` (confirm exit 1 source mismatch when run without manifest).
5. `git diff --stat -- corpus/SOURCES.md` (confirm no unapproved edits or registry rows created in `corpus/SOURCES.md`).
