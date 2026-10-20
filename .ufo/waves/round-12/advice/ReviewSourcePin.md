# ReviewSourcePin — round 12 frozen manifest trust design

Author advisor, static review only. No runs, builds, tests, endpoint calls or git writes were performed. Unrun != pass. Tools installed/updated: none.

## Evidence read

- `corpus/lessons/round-11-verifier-spotcheck.md` §"Checking frozen input correspondence" and D1 (lines 91–118, 208–212). Observed by the round-11 closure reviewer with read-only `git show 2f7303c…:corpus/SOURCES.md`:
  - actual source SHA-256: `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`
  - frozen snapshot SHA-256: `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1`
  - the frozen copy has a truncated search-log line 55 with a tool display marker (`artifact://1157`). Registry rows are byte-identical; the 9 knowledge blobs match.
- `.ufo/waves/round-11/frozen/expected.json` pins `…/frozen/before/corpus/SOURCES.md` to `52665cf…` and `source_revision` `2f7303c…`. That is the wrong digest, and it was accepted by the round-11 runner (`reproduce.py` lines 29–36) because the runner only checks expected.json against the frozen files. Nothing compares it to git.
- `.ufo/waves/round-12/spec.json` `context` shared interface (CLI, exit codes, manifest fields, `--snapshot` override, `--selftest`, runner modes).
- `.ufo/waves/round-12/claims.json` C1 (before 1 → after 0, delta 0 on scores).
- `corpus/SOURCES.md` registry header (no trust constants present; the file is data, not an anchor).

## Core finding

**A digest pin is integrity, not source authority.** The round-11 expected.json digest proved that the frozen bytes matched what the lane *recorded*, which is a self-consistent check. It did not prove the bytes matched git history. D1 is exactly that failure. Round-12 must make the fixed source commit the authority and keep it out of the snapshot+manifest pair so that coherent mutation of both cannot move it.

Required property: if the snapshot and the manifest are both replaced with the same wrong content, the CLI must still exit 1 (`source_mismatch`), not 0 and not 2.

## Findings (severity order)

**F1 (high) — the source authority must be a code constant, not a manifest field.**
If `source_commit`, `source_path` or the expected source digest are read from the manifest, a coherent edit of manifest + snapshot changes the authority with them. Recommended persisted constants in `fidelity.py`, with no CLI flag or env override:

| Constant | Value | Status |
|---|---|---|
| `SOURCE_COMMIT` | `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` | fixed by spec |
| `SOURCE_PATH` | `corpus/SOURCES.md` | fixed by spec |
| `SOURCE_BLOB_SHA256` | `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` | observed in D1 (round-11 closure, `git show` bytes) |
| `SOURCE_BLOB_OID` | git SHA-1 blob id of `SOURCE_COMMIT:SOURCE_PATH` | NOT observed in evidence; owner derives once with `git rev-parse` and pins it; [INFERENCE] needed until pinned |
| `LEGACY_D1_SNAPSHOT_SHA256` | `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` | selftest/observation only; never a pass value |

Do not add a `--source-commit` or `--source-path` flag. Selftest must not need one (see F5).

**F2 (high) — the manifest is only an integrity pin for the snapshot and a consistency check.**
Manifest fields `snapshot_sha256`, `source_commit`, `source_path` and `expected_verdict` must be read, but:
- `source_commit` and `source_path` in the manifest must equal the constants. Any mismatch → exit 2 (`manifest_invalid`). Never let the manifest redirect authority.
- `expected_verdict` must not affect the exit code. Exit code is computed from findings only. A mutated manifest claiming `clean` against a mismatch must still exit 1. `reproduce.py` compares the manifest's expectation to the CLI result; the CLI itself does not honor it.
- `snapshot_sha256` is checked against the snapshot bytes actually read, for the `snapshot_tampered` finding.

**F3 (high) — the source read must be raw, pinned and replace-free.**
- Use `git cat-file blob <SOURCE_COMMIT>:<SOURCE_PATH>` (byte-raw, no textconv, no smudge filters). Avoid `git show`, `git diff`, and any text-mode subprocess decoding.
- Resolve the commit first: `git rev-parse --verify --end-of-options <SOURCE_COMMIT>^{commit}` must equal `SOURCE_COMMIT` exactly. Abbreviations, refs and `HEAD` are never accepted.
- Pass `--no-replace-objects` (or `GIT_NO_REPLACE_OBJECTS=1`) so grafts/replace refs cannot substitute the blob.
- Unset `GIT_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_INDEX_FILE` in the subprocess environment, or pass the repo explicitly. Residual risk: alternates pointing elsewhere; this is caught only by F4's constant.
- Read with `subprocess.run(..., capture_output=True)` without `text=True`. Never decode.

**F4 (high) — verify the source bytes against the constant before using them as authority.**
After reading the blob:
1. `sha256(source_bytes) == SOURCE_BLOB_SHA256`, else `source_unavailable` (exit 2) with reason `source_identity_mismatch`. Git returning different bytes for a fixed commit means the object store is not trustworthy; it is not a mismatch of the snapshot.
2. If `SOURCE_BLOB_OID` is pinned, recompute `sha1(b"blob %d\0" % len(source_bytes) + source_bytes)` and compare; this is an independent cross-check on the object store.

**F5 (medium) — selftest must not weaken authority.**
- `clean`: real `--repo` (read-only), real frozen snapshot, real manifest.
- `mismatch`: copy of the snapshot with one byte changed, default manifest updated in a temp copy → must exit 1 only if the manifest pin is consistent; otherwise exit 2. Document which.
- `tamper`: snapshot byte changed, manifest unchanged → `snapshot_tampered`, exit 2.
- `unavailable`: `--repo` pointing at an empty temp directory → `source_unavailable`, exit 2.
- Never fabricate a git repo at `SOURCE_COMMIT` for selftest; a fixture commit cannot be the pinned id. Fixtures for the source path are a red flag.
- All writes under `tempfile.mkdtemp()`; the lane tree is read-only.

**F6 (medium) — precedence and reporting.**
Define and emit all findings in JSON, with exit precedence:
`source_unavailable` (2) = `snapshot_tampered` (2) > `source_mismatch` (1) > `clean` (0).
Even when exit 2 is returned for a tamper, the source comparison still runs and is reported (`source_sha256`, `snapshot_sha256`, `first_diff_offset`, `source_len`, `snapshot_len`). Otherwise a tamper hides the D1-type mismatch.
Comparisons are byte-exact. No CRLF normalization, no trailing-newline trimming, no `errors='replace'`.

**F7 (medium) — snapshot creation must be byte-exact and tool-independent.**
The new snapshot at `frozen/corpus/SOURCES.md` must be created from `git cat-file blob` output redirected to the file, not via `read`/`write`/`edit` tooling. D1 came from tool-rendered text (`artifact://1157` marker). The runner or owner must record the snapshot SHA-256 and check it equals `SOURCE_BLOB_SHA256`. If the snapshot's sha differs from the source constant, the design's "clean" claim is false and the manifest must not be written to claim clean.

**F8 (low) — old evidence is not rewritten.**
`round-11/frozen/expected.json` must remain immutable. Its wrong digest is preserved; an erratum (new file or appended disclaimer in the round-11 lesson, per D1 in that lesson's routed list) names `52665cf…` as the truncated copy and points to round-12 `9dc40d…`. The round-12 old-snapshot control (no manifest) is expected to exit 1 with `source_mismatch`, not 0.

## Attack matrix for L1 (not run)

| Case | Snapshot | Manifest | Expected exit | Finding |
|---|---|---|---|---|
| Clean | new frozen copy (`9dc40d…`) | default, pins `9dc40d…`, commit/path constants, `expected_verdict: clean` | 0 | `clean` |
| Old D1 observation, no manifest | old frozen (`52665cf…`) | none | 1 | `source_mismatch` |
| Tamper only | flipped byte | original | 2 | `snapshot_tampered` |
| Coherent attack, snapshot + manifest mutated together | `X` ≠ source | manifest pins `sha(X)`, `expected_verdict: clean` | **1** | `source_mismatch` (must NOT be 0/2) |
| Manifest redirects commit | new snapshot | `source_commit` = other commit | 2 | `manifest_invalid` |
| Manifest redirects path | new snapshot | `source_path` = other path | 2 | `manifest_invalid` |
| Object-store substitution | any | any | 2 | `source_unavailable`/`source_identity_mismatch` |
| Repo missing commit | any | default | 2 | `source_unavailable` |

The coherent-attack row is the central requirement: it must fail for source reasons, independent of snapshot and manifest.

## Checks for L1 to run once after integration (not run by this seat)

1. `git cat-file -s 2f7303c…:corpus/SOURCES.md` and sha256 of `git cat-file blob` output; confirm `9dc40d…` and derive the blob OID for `SOURCE_BLOB_OID` if pinned.
2. Confirm `fidelity.py` contains no manifest-read path for `SOURCE_COMMIT`/`SOURCE_PATH` authority and no CLI flag overriding the constants (grep for `source_commit`, `source_path`, `expected_verdict` usage in exit logic).
3. Run the attack matrix above through the actual CLI, including the coherent-mutation row expecting exit 1.
4. Confirm `round-11/frozen/expected.json` is byte-unchanged (`git diff` against the before commit should show no change to it).
5. Confirm the frozen snapshot's sha equals the manifest pin and the constant.

## Residual risk / verification gaps

- `SOURCE_BLOB_OID` is not observed in the evidence; pinning it is an owner action not yet done.
- `SOURCE_BLOB_SHA256` comes from the round-11 closure's observation of `git show` output, not from a run by this seat.
- A coherent edit of `fidelity.py` and its constants is out of scope; the trust root is the committed code plus git history. Recommend the reviewer diff `fidelity.py` constants against this report.
- Object-store alternates may point elsewhere; F4's constant check detects it, but only if the constant itself is correct.
- No claim is made about the other 8 round-11 knowledge blobs beyond the closure's report.
