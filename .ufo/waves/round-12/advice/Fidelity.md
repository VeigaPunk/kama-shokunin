# Fidelity — round-12 C1 implementation (author advisory, statically unrun)

Scope: D1 snapshot fidelity only. D2–D5 belong to their routed owners. No
scalar/score, capability, serving-readiness or live-host claim is made.

## Files written (assigned paths only)

- `.ufo/waves/round-12/fidelity.py` — shared gate CLI (`--snapshot`,
  `--manifest PATH|auto|none`, `--repo`, `--selftest`).
- `.ufo/waves/round-12/frozen/corpus/SOURCES.md` — corrective snapshot,
  18,898 bytes, SHA-256 `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`.
- `.ufo/waves/round-12/frozen/expected.json` — frozen manifest, 477 bytes,
  SHA-256 `f879645a8f49557003340ad26786e72cac0f4350e5a0b92f8b24e8317d01a8e0`.
- `.ufo/waves/round-12/advice/Fidelity.md` — this report.
- No README/scaffold retained; round-11 frozen files were not touched.

## Observed artifact provenance (git bytes, not tool-rendered text)

Generated once with `subprocess.check_output(git --no-replace-objects -C
<lane> show 2f7303c...:corpus/SOURCES.md)`, written verbatim:

| Observation | Value |
|---|---|
| source revision/path | `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`:`corpus/SOURCES.md` |
| blob object id (`rev-parse`) | `7de1360655eadada356fe110813c6e1338142551` |
| snapshot bytes / SHA-256 | 18898 / `9dc40d25…093a` |
| `git show` vs `git cat-file blob` bytes | identical (observed during generation) |
| snapshot tail | `…before any claim either way.\n` |
| old round-11 frozen SOURCES | 18793 bytes / `52665cf2…c60142fa1` |
| old frozen == git source | **false** (truncated line 55 + `artifact://1157` display marker tail) |

This independently reproduces D1: the round-11 green digest check proved
integrity against its shipped manifest, not correspondence with
`2f7303c:corpus/SOURCES.md`. The new snapshot corresponds exactly, so the
auxiliary mismatch count is 1 → 0 for this artifact.

The snapshot was generated from `git show` raw stdout; the gate compares with
`git cat-file blob` raw stdout. During generation these were observed
byte-identical for the pinned revision, and both bypass display/formatting, so
no tool-rendered text can enter the comparison.

## Erratum — old round-11 auxiliary snapshot (D1)

The round-11 receipt is not rewritten; it remains byte-identical. Its SOURCES
copy at `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` is **not** the
commit's blob: frozen 18,793 bytes / `52665cf2…c60142fa1`, actual
`2f7303c:corpus/SOURCES.md` 18,898 bytes /
`9dc40d25…093a`. The frozen copy truncates the line-55 search-log text and
appends the tool display line `[Some lines truncated to 768 bytes. Use
artifact://1157:raw:55-55 to read line 55 whole]` with no trailing newline;
that marker is not in the commit. Round-12 supersedes it with the exact copy
above. Corrections must never regenerate a frozen snapshot in place: a later
correction gets a new round directory and its own pinned manifest.

## CLI contract (exact; sent to Runner)

Manifest keys: `schema` = `kama-round-12-frozen/v1`, `snapshot_path`,
`snapshot_sha256`, `source_revision`, `source_path`, `source_oid`,
`source_sha256`, `source_bytes`, `expected_verdict` (must be `clean`).

Source anchor is hard-coded in `fidelity.py`: revision, path, blob OID,
SHA-256 and byte count. Every manifest value must equal those constants,
otherwise `manifest_invalid` exit 2. Changing the manifest cannot redirect the
comparison; `expected_verdict` is informational and never drives exit. The gate
also requires the retrieved blob's OID, SHA-256 and byte count to equal the
code pins; failure means the repository cannot vouch for the anchor and is
`source_unavailable` exit 2 (could-not-evaluate), distinct from snapshot
divergence from a verified anchor (`source_mismatch` exit 1).

Result JSON (stdout, every non-selftest mode): `schema`
`kama-round-12-fidelity/v1`, `finding`, `findings[]`, `checks[]`,
`mismatches`, `exit`, `integrity`, `integrity_result`, `correspondence`,
`pinned`, `snapshot`, `snapshot_sha256`, `snapshot_bytes`, `snapshot_error`,
`snapshot_pin_matches`, `source_revision`, `source_path`,
`source_expected_oid`, `source_expected_sha256`, `source_oid`,
`source_sha256`, `source_bytes`, `source_available`, `source_anchor_matches`,
`source_matches`, `source_error`, `source_diff`, `manifest`,
`manifest_sha256`, `manifest_error`, `expected_verdict`, `expected_matches`.
Only digests, sizes and byte offsets are printed; snapshot content is never
echoed. `mismatches` is the C1 source-correspondence count: 1 only when
`source_matches: false` with `source_anchor_matches: true`, else 0. Integrity
pin and anchor status remain visible in `integrity_result`,
`snapshot_pin_matches` and `source_anchor_matches`, and every failed check is
listed in `checks[]`; neither failure is folded into `mismatches`.

| Mode | Finding / exit |
|---|---|
| snapshot + pin + pinned git blob agree | `clean` / 0 |
| bytes differ from a verified code-pinned git blob (even with a coherent manifest) | `source_mismatch` / 1 |
| snapshot differs from manifest pin | `snapshot_tampered` / 2 |
| pinned revision/path unavailable, or retrieved blob fails the pinned oid/sha/bytes | `source_unavailable` / 2 |
| snapshot missing, symlink or non-regular | `snapshot_unavailable` / 2 |
| malformed/missing manifest, or manifest tries to change the anchor | `manifest_invalid` / 2 |
| no pin and source matches (integrity not checked) | `unpinned` / 2, never clean |
| unexpected exception | `internal_error` / 2 |

`--manifest auto` (default) uses `frozen/expected.json` only for the default
snapshot path (explicit default or omitted). An overridden snapshot with no
`--manifest` is unpinned; `--manifest none` is the explicit unpinned mode.
The old round-11 snapshot is therefore called with `--repo <root>` and no
manifest: expected `source_mismatch` exit 1. A matching unpinned snapshot is
`unpinned` exit 2 per KQ15, not a clean substitute for a pin.

Git reads are offline/read-only: argv lists, no shell, `--no-pager
--no-replace-objects cat-file blob`, `GIT_*` scrubbed plus
`GIT_NO_REPLACE_OBJECTS`, `GIT_NO_LAZY_FETCH`; `--repo` must be the repository
root (`rev-parse --show-toplevel` equality). Snapshot/manifest symlinks and
non-regular files are rejected before reading.

`--selftest` emits `schema` `kama-round-12-selftest/v1`, `passed`, `failed`,
`checks[]`; exit 0 all pass, 1 any fail, 2 could-not-run. It invokes this file
as a child CLI for eleven cases: clean, coherent snapshot+manifest mutation,
manifest-only corruption (mutated snapshot), pin-only corruption (exact
snapshot, zero pin), missing source (temp `git init` empty repo), matching
unpinned, unpinned mismatch, manifest anchor redirect, absent manifest, absent
snapshot, symlink snapshot. Fixtures are temporary snapshot/manifest files; the
pinned blob is read read-only from this repository's immutable history and no
live file is written. Coherent mutation is asserted to remain
`source_mismatch` exit 1 (mismatches 1) because correspondence uses the code
anchor, not the manifest digest.

Exact expected observations for the required controls:

- old round-11 SOURCES, no manifest: `source_mismatch`, exit 1, mismatches 1,
  `pinned: false`, `integrity: not_checked`, `correspondence: mismatch`.
- new snapshot, default manifest: `clean`, exit 0, mismatches 0,
  `integrity_result: match`, `correspondence: match`.
- coherent snapshot+manifest mutant: `source_mismatch`, exit 1, mismatches 1,
  `snapshot_pin_matches: true`, `source_matches: false`.
- manifest corruption with a mutated snapshot (selftest `snapshot-tampered`
  fixture): `snapshot_tampered`, exit 2, mismatches 1 (`source_matches:
  false`, `snapshot_pin_matches: false`).
- pin-only corruption with a pristine snapshot (zero/wrong pin): Runner's
  manifest-only-corruption case and selftest `pin-only-corruption-exact-snapshot`:
  `snapshot_tampered`, exit 2, mismatches 0 (`source_matches: true`,
  `snapshot_pin_matches: false`).
- `mismatches` depends only on snapshot-vs-source, never on the pin: pristine
  snapshot + bad pin = 0; divergent snapshot + bad pin = 1. Main's receipt
  states the actual runner observation.
- empty repo / missing commit: `source_unavailable`, exit 2, mismatches 0,
  `source_available: false`, `correspondence: unavailable`.

## Verification status

**Unrun ≠ pass.** I executed no gate, no `--selftest`, no `reproduce.py`, and
no build/test/lint/formatter. All statements above are static design plus the
permitted one-shot `git show` artifact generation and digest measurements.
`reproduce.py` is Runner-owned and was not run.

L1 checks, in order (from the lane root):

```sh
python3 .ufo/waves/round-12/fidelity.py
python3 .ufo/waves/round-12/fidelity.py --selftest
python3 .ufo/waves/round-12/fidelity.py --snapshot .ufo/waves/round-11/frozen/before/corpus/SOURCES.md
python3 .ufo/waves/round-12/reproduce.py
```

Expected: clean/0; selftest 11/11 exit 0; old snapshot source_mismatch/1; runner
overall exit 0 with measured HEAD recorded. The committed receipt must carry
`finding`, `mismatches`, `source_anchor_matches` and `source_matches` for both
the old round-11 snapshot and the new snapshot; this seat has no executed
receipt to quote.

## Risks / limits

1. Every mode and the selftest require the lane object database to contain
   `2f7303c`; a shallow or foreign copy yields `source_unavailable` (selftest
   exit 2) rather than a false clean.
2. `--repo` must be the repository root; subdirectories are rejected by the
   toplevel equality check.
3. `manifest_sha256` is reported but not code-enforced. Enforcing it would turn
   the required coherent snapshot+manifest attack into exit 2 instead of the
   specified `source_mismatch` exit 1; external pinning belongs in the runner
   receipt/report, not in the comparison.
4. The auto-pin decision is path-based: a byte-identical copy of the snapshot
   at another path is unpinned and exits 2 `unpinned`, not 0.
5. Selftest's clean fixture reads the same live blob the gate reads; the
   old-round-11 mismatch control, not selftest, establishes historical
   correspondence for C1.
6. The anchor-failure branch (`source_unavailable` when a retrieved blob fails
   the pinned oid/sha/bytes) has no selftest fixture: synthesizing the fixed
   commit with different content is not possible in a temp repository, and
   corrupting the lane object database is out of scope. It is a static guard
   only; the missing-source fixture exercises the adjacent retrieval failure.
7. `mismatches` deliberately counts only verified-anchor source mismatches;
   pin failures remain in `integrity_result`/`snapshot_pin_matches`, so a
   tampered snapshot still reports `mismatches: 1` for its correspondence
   failure rather than 2.
8. Tools installed or updated: none.
