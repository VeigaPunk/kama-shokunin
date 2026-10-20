# Round 13 — SourceCat: git-cat-file manual inspection and raw blob proof

author: KamaR13.SourceCat (UFO-FSD scout)  
Target: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/advice/SourceCat.md  
Scope: Static documentation analysis only. Reopened official Git manual independently. No test, build, linter, gate execution, or sibling check was run. Zero tools installed or updated.

---

## 1. Axes (Godspeed)

- **calibration (C1):** Primary axis. Provides verified manual grounding for the second routed KQ15 proposition error (distinguishing capture via `git show` from independent byte comparison via `git cat-file blob`), enabling criterion discrepancy reduction from 2 → 0 under score 7 → 7.
- **quality:** Improved documentation precision. Accurately cites first-party Git documentation (Docs/A) for command output semantics while strictly bounding documentation as specification of method, not empirical proof of verification outcome.
- **harm none:** Leaf-only execution. No subagent dispatch, no changes to corpus/code outside this assigned advice report, no unverified claims of executed checks.

---

## 2. Independent Manual Verification

The official `git-cat-file` manual was independently opened across two authoritative channels:
1. **Host installed manual:** `man 1 git-cat-file` (via `man -P cat git-cat-file`) for `Git 2.55.0` (dated 2026-06-29).
2. **Upstream canonical documentation:** `https://git-scm.com/docs/git-cat-file` (Git 2.56.0 manual, last updated 2026-09-28; reopened 2026-10-20).

Both versions carry identical text in the `OUTPUT` section defining the behavior of the explicit `<type> <object>` invocation.

---

## 3. Located Quote: Explicit `<type>` Emits Raw Contents

Under section **`OUTPUT`** (paragraph 5):

> **“If &lt;type&gt; is specified, the raw (though uncompressed) contents of the &lt;object&gt; will be returned.”**

- **Word count:** 15 whitespace-delimited words (meets strict constraint: $\le 25$ words).
- **Location:** `git-cat-file(1)`, section `OUTPUT`, lines 189–190 of man page / paragraph `<p>` under `div.paragraph` in upstream HTML.
- **Direct Semantic Proof:** When `<type>` is explicitly passed as `blob` (e.g. `git cat-file blob <revision>:<path>`), Git emits the uninterpreted raw bytes directly from the object database without pretty-printing (`-p`), header prepending, or working-tree smudge conversions.

---

## 4. The `--filters` / `--textconv` Caveat

The manual explicitly defines `--filters` and `--textconv` as separate operational modes under `OPTIONS`:
- **`--filters`:** *“Show the content as converted by the filters configured in the current working tree for the given &lt;path&gt; (i.e. smudge filters, end-of-line conversion, etc).”*
- **`--textconv`:** *“Show the content as transformed by a textconv filter.”*

### Boundary and Distinction:
- The standard synopsis form `git cat-file <type> <object>` operates without `--filters` or `--textconv`.
- Because `git cat-file blob <rev>:<path>` does not invoke smudge filters or end-of-line conversions, the bytes emitted are identical to the repository object stored in git history.
- **Caveat:** If an invocation were to supply `--filters` or `--textconv`, output would undergo working-tree transformations rather than reflecting pure immutable object bytes. To guarantee raw byte comparison, the comparator invocation must strictly use explicit `<type> <object>` (`cat-file blob`) without `--filters` or `--textconv`.

---

## 5. Epistemic Boundary: Contract Specification vs. Outcome Proof

- **Contract Specification (Docs/A):** The manual provides first-party proof of the *comparator method's semantics*—specifically, that `git cat-file blob <rev>:<path>` retrieves uncompressed, unfiltered historical object bytes independently of working-tree state or manifest files.
- **Not Outcome Proof:** Citing `git-cat-file` documentation proves how Git behaves, but it **never** proves empirical correctness, endpoint readiness, or the outcome of any specific byte comparison (e.g., whether `corpus/SOURCES.md` matches `2f7303c...` or whether a gate returns clean). Outcome proof requires static evaluation of the retrieved bytes or observation of committed execution receipts (`acceptance.json`).

---

## 6. S033 Registry Candidate (for Sources Executor and L1 Planner)

| Field | Entry |
|---|---|
| **id** | `S033` |
| **source** | `Git git-cat-file manual — https://git-scm.com/docs/git-cat-file` |
| **kind** | `docs` |
| **tier** | `A` |
| **scope** | `Byte-preserving raw blob comparison for kama evidence verification, not endpoint truth or outcome proof` |
| **anchor** | `OUTPUT, explicit <type> raw contents; manual last updated in Git 2.56.0 (2026-09-28), opened 2026-10-20` |
| **teaches** | `Specifying <type> (e.g. blob) emits raw uncompressed object bytes without working-tree filters or textconv transformation, providing an independent comparator method.` |
| **status** | `mined` |
| **opened** | `2026-10-20` |
| **recheck** | `on-release` |
| **used-by** | `corpus/lessons/round-13.md`, `corpus/QUALITY.md` |

---

## 7. Synthesis with KQ15 / KQ16 Propositions

In Round 12 verifier spotcheck (`round-12-verifier-spotcheck.md` D1):
- KQ15 at `corpus/QUALITY.md:49` mistakenly cited `git show <pinned-commit>:<source-path>` as the comparator source.
- Actual implementation (`.ufo/waves/round-12/fidelity.py:271–273, 442–444`) uses `git cat-file blob <revision>:<path>`.
- The correct decoupled formulation for KQ16 is:
  - **Capture:** `git show` (S032: plain blob contents display).
  - **Comparison:** `git cat-file blob` (S033: independent raw uncompressed object emission).

---

## 8. Limits

- Findings are based purely on static manual inspection (local `man` and online documentation).
- No code, gate scripts, test runners, or censuses were executed.
- No git commits or branches were created.

Report: .ufo/waves/round-13/advice/SourceCat.md
