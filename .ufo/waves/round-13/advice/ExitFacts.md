# Round 13 — ExitFacts (fidelity.py Verdict Selection & Registry SKILL Mapping)

**Seat:** `KamaR13.ExitFacts` (scout)  
**Lane:** `kama-shokunin`  
**Date:** 2026-10-20 UTC  
**Scope:** Static read of Round 12 `fidelity.py` verdict selection and `SKILL.md` Round 12 evidence registry row; enumeration of `source_mismatch`, `snapshot_tampered`, and `source_unavailable` finding IDs, exit codes, and exit classes from actual code.  
**Boundary:** Leaf scout report only. Read-only analysis; no test, build, lint, format, or gate scripts executed. Unrun $\neq$ pass. Tools installed/updated: none.

---

## 1. Executive Summary & Core Discrepancy Identification

In `corpus/QUALITY.md:49`, criterion KQ15 contains two inaccurate formulations identified by the Round 12 verifier spotcheck (`corpus/lessons/round-12-verifier-spotcheck.md` §Routed defects and dispositions D1):

1. **Exit Code vs. Finding ID Formulation:**
   - *KQ15 Assertion:* `"...mismatch, snapshot tamper and unavailable source each have distinct nonzero exits."`
   - *Actual Implementation (`fidelity.py` & `SKILL.md`):* The exits are **not** three distinct nonzero exit codes. Rather, `source_mismatch` maps to exit code `1` (protocol class `failed`), while `snapshot_tampered` and `source_unavailable` share exit code `2` (protocol class `could-not-evaluate`). Their distinction is maintained through **stable distinct finding IDs** (`source_mismatch`, `snapshot_tampered`, `source_unavailable`), not three distinct exit integers.
   - *Exact Literal Audit Mapping for KQ16:* `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`.

2. **Capture vs. Comparison Mechanism:**
   - *KQ15 Assertion:* `"A frozen historical copy is compared byte-for-byte with the blob fetched directly as git show <pinned-commit>:<source-path>..."`
   - *Actual Implementation (`fidelity.py:272–273`, `SKILL.md:396`, and verifier spotcheck):* Artifact *capture* is performed via `git show`, whereas programmatic runtime *comparison* is performed via `git cat-file blob <pinned-commit>:<source-path>`.
   - *Exact Literal Audit Phrase for KQ16:* `capture: git show; comparison: git cat-file blob`.

---

## 2. Code-Grounded Verdict Selection in `fidelity.py`

File location: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py`

### 2.1 Docstring Exit Contract (`fidelity.py:24–27`)
```python
Exit codes: 0 clean; 1 source_mismatch; 2 snapshot_tampered,
source_unavailable, snapshot_unavailable, manifest_invalid, unpinned or
internal_error.  All modes emit one JSON result object on stdout and never
print snapshot contents, only digests, sizes and byte offsets.
```

### 2.2 Priority Ordering (`fidelity.py:65–73`)
Finding resolution evaluates findings deterministically using `PRIORITY`:
```python
PRIORITY = (
    'snapshot_unavailable',
    'manifest_invalid',
    'snapshot_tampered',
    'source_unavailable',
    'source_mismatch',
    'unpinned',
    'clean',
)
```
- Every exit-2 finding outranks `source_mismatch` (exit 1).
- `snapshot_tampered` (rank 3) outranks `source_unavailable` (rank 4), which outranks `source_mismatch` (rank 5).

### 2.3 Primary Finding and Exit Code Assignment (`fidelity.py:315–319`)
```python
    finding = next(fid for fid in PRIORITY
                   if any(item['id'] == fid for item in findings))
    exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)
```
Exit code calculation is strictly tri-state:
- Exit `0`: if `finding == 'clean'`
- Exit `1`: if `finding == 'source_mismatch'`
- Exit `2`: for all other findings (`snapshot_tampered`, `source_unavailable`, `snapshot_unavailable`, `manifest_invalid`, `unpinned`, and `internal_error`)

### 2.4 Internal Error Safety Fallback (`fidelity.py:611–623`)
```python
    except Exception as error:  # noqa: BLE001 - exit 1 would mean source_mismatch
        write_json({
            'schema': SCHEMA_RESULT,
            'finding': 'internal_error',
            'findings': [{'id': 'internal_error',
                          'detail': f'{type(error).__name__}: {error}'}],
            'mismatches': 0,
            'exit': 2,
            'integrity': 'not_checked',
            'pinned': False,
        })
        return 2
```
Unhandled runtime exceptions explicitly return exit code `2` with finding `internal_error` to prevent unhandled errors from ever mapping to exit `1` (`source_mismatch`) or exit `0` (`clean`).

---

## 3. Enumeration of Key Findings: ID, Exit Code, Class, and Trigger

| Finding ID | Exit Code | Protocol Exit Class | Triggering Code Conditions in `fidelity.py` | Priority Rank |
|---|:---:|---|---|:---:|
| `source_mismatch` | **1** | `failed` | `fidelity.py:298–311`: Snapshot read successfully, source anchor verified (`anchor_matches is True`), but snapshot bytes do not equal retrieved git source blob (`snapshot_bytes != source_bytes`). Reports byte offset of first difference and lengths. `mismatches` count = 1. | 5 |
| `snapshot_tampered` | **2** | `could-not-evaluate` | `fidelity.py:228–236`: Manifest provided and loaded, snapshot bytes read, but snapshot SHA-256 digest fails to match the manifest's pinned digest (`sha256(snapshot_bytes) != manifest['pin']`). Represents mutated/corrupted input snapshot. | 3 |
| `source_unavailable` | **2** | `could-not-evaluate` | `fidelity.py:251–296`: Inability to obtain or vouch for historical git blob anchor:<br>1. Repository unusable (`git_toplevel` error).<br>2. Repo toplevel does not match requested root (`toplevel != repo_path`).<br>3. `git rev-parse --verify SOURCE_REVISION:SOURCE_PATH` fails.<br>4. `git cat-file blob SOURCE_REVISION:SOURCE_PATH` fails.<br>5. Retrieved blob fails immutable constants (`oid != SOURCE_BLOB_OID`, `sha256 != SOURCE_SHA256`, or `len != SOURCE_BYTES`). | 4 |

### Additional Exit-2 Finding IDs in `fidelity.py`
For completeness, the remaining finding IDs mapping to exit `2` (`could-not-evaluate`) are:
- `snapshot_unavailable` (Exit 2, Priority 1): Snapshot file missing, unreadable, or symlink refused (`fidelity.py:207–216`).
- `manifest_invalid` (Exit 2, Priority 2): Manifest JSON invalid, wrong schema, symlink refused, or contains attempted override of hardcoded anchor constants (`fidelity.py:128–176, 220–224`).
- `unpinned` (Exit 2, Priority 6): Snapshot provided with `--manifest none` (or unpinned override), snapshot bytes match source bytes, but integrity is unpinned; a matching snapshot cannot be certified clean without an integrity pin (`fidelity.py:237–242`).
- `internal_error` (Exit 2): Uncaught exception during command evaluation (`fidelity.py:611–623`).

---

## 4. `SKILL.md` Evidence Registry Mapping

File location: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:395–397`

Under `## Round-12 local evidence registry (owner: kama)`:

| Field | Registry Entry Specification |
|---|---|
| **Name** | `Exact-source snapshot fidelity (D1 corrective snapshot)` |
| **Kind / entry command** | `gate: python3 .ufo/waves/round-12/fidelity.py --snapshot PATH [--manifest PATH] [--repo PATH]`; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md`, default manifest `auto` $\to$ `.ufo/waves/round-12/frozen/expected.json`; immutable source constants commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`, path `corpus/SOURCES.md` |
| **Verdict map (code $\to$ class)** | `0 clean; 1 failed (source_mismatch); 2 could-not-evaluate (snapshot_tampered, snapshot_unavailable, manifest_invalid, source_unavailable, unpinned, internal_error); any undeclared nonzero code reads could-not-evaluate` |
| **Self-test** | `python3 .ufo/waves/round-12/fidelity.py --selftest` (spelling `--selftest`): real child CLI over temporary snapshot/manifest fixtures and a temporary empty git repo, reading the pinned immutable blob from the live lane repo read-only (`--repo`), asserting exit code and stable finding ID for clean, coherent snapshot+manifest mutation, snapshot tamper, unavailable source, unpinned match and mismatch, manifest anchor redirect, absent manifest, missing snapshot and symlink refusal |
| **Pinned values** | `.ufo/waves/round-12/frozen/expected.json` pins snapshot SHA-256 and path, source revision, path, blob OID and content SHA-256, and expected clean verdict; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md` captured byte-exactly via `git show`, never tool-rendered text |
| **Write scope** | Read-only over the lane repo and git history; no endpoint or live-service access; ordinary runs write nothing; `--selftest` writes and removes isolated temporary trees only |
| **Owner** | `kama` |

### Concordance Between Registry and Code
The registry table entry directly matches `fidelity.py`:
1. Exit 0 maps exclusively to `clean`.
2. Exit 1 maps exclusively to `failed` (`source_mismatch`).
3. Exit 2 maps to `could-not-evaluate` and groups all non-clean non-mismatch conditions: `snapshot_tampered`, `snapshot_unavailable`, `manifest_invalid`, `source_unavailable`, `unpinned`, and `internal_error`.
4. The registry explicitly notes that default snapshot was captured byte-exactly via `git show`, while runtime comparison checks the immutable git blob directly.

---

## 5. Verification Limits & Grounding Boundaries

1. **Read-Only Static Inspection:**  
   All line citations and logic paths in this report were gathered via static file reading of `fidelity.py`, `SKILL.md`, `corpus/QUALITY.md`, and `round-12-verifier-spotcheck.md`. No test, gate, or reproducer scripts were run during this investigation.
2. **Receipt Grounding:**  
   The exit code and finding distributions reported in `.ufo/waves/round-12/acceptance.json` (e.g., `before` $\to$ exit 1 `source_mismatch`, `snapshot-tampered` $\to$ exit 2 `snapshot_tampered`, `source-unavailable` $\to$ exit 2 `source_unavailable`) are treated as verified committed historical receipts, not fresh executions.
3. **Scope Bounds:**  
   This scout report provides the factual basis for the Round 13 criterion update (KQ16 superseding KQ15's exit code and capture/comparison phrasing) and probe construction. No modifications to code, gates, registries, or historical receipts were made.
