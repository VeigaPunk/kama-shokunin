# Round 12 — Runner (author advisor; static implementation, not closure)

Scope: implement `.ufo/waves/round-12/reproduce.py` against the landed fidelity
CLI, then report. I did not execute `reproduce.py`, `fidelity.py`, or any case.
`unrun != pass`; L1 owns the single acceptance run. No Fidelity-owned file was
edited. Tools installed/updated: none.

## Files

- Wrote `.ufo/waves/round-12/reproduce.py` (only implementation file).
- Wrote this report (`.ufo/waves/round-12/advice/Runner.md`).
- Did not touch `fidelity.py`, `frozen/**`, round-11 evidence, registry,
  verifier files, MANIFEST, host/config/env/services, or routing.

## Implemented runner behavior

One JSON receipt on stdout; no receipt file is written. Per the parent's
preferred boring design, `--output` is **deleted** rather than guarded: L1 can
capture stdout directly. Mutants and the empty repository live in one
`tempfile.TemporaryDirectory`; the lane tree is read-only. All child processes
use argv lists (never a shell), a 600 s timeout, inherited `GIT_*` overrides
removed, replace objects and lazy fetching disabled.

Cases and hardcoded assertions (exit + primary `finding` + `mismatches` +
independent fields):

| Case | Invocation | Expected | Asserted fields |
|---|---|---|---|
| before | old round-11 SOURCES, `--manifest none --repo ROOT` | `source_mismatch`, exit 1, mismatches 1 | `pinned:false`, `integrity:not_checked`, `integrity_result:not_checked`, `correspondence:mismatch`, `snapshot_pin_matches:null`, `source_matches:false`, `source_anchor_matches:true`, `snapshot_sha256:52665cf2…2fa1` |
| after | new SOURCES, explicit `--manifest frozen/expected.json --repo ROOT` | `clean`, exit 0, mismatches 0 | `pinned:true`, `integrity:checked`, `integrity_result:match`, `correspondence:match`, `snapshot_pin_matches:true`, `source_matches:true`, `source_anchor_matches:true`, `snapshot_sha256:9dc40d25…093a`, `manifest_sha256` equals the frozen manifest |
| selftest | `--selftest` | exit 0 | schema `kama-round-12-selftest/v1`, `passed:11`, `failed:0`, exact 11 named cases, every case `ok:true` (clean, coherent, snapshot-tampered, pin-only corruption, source-unavailable, unpinned-matching, unpinned-mismatch, manifest-redirect, absent-manifest, snapshot-unavailable, symlink-rejected) |
| coherent | temp snapshot + temp manifest, one appended byte and copied manifest pin re-computed | `source_mismatch`, exit 1, mismatches 1 | `pinned:true`, `integrity:checked`, `integrity_result:match`, `correspondence:mismatch`, `snapshot_pin_matches:true`, `source_matches:false`, `source_anchor_matches:true`, `snapshot_sha256` equals mutant, `manifest_sha256` equals temp manifest |
| tamper | exact new snapshot + temp manifest with only `snapshot_sha256` changed to zeros | `snapshot_tampered`, exit 2, mismatches 0 | `pinned:true`, `integrity:checked`, `integrity_result:mismatch`, `correspondence:match`, `snapshot_pin_matches:false`, `source_matches:true`, `source_anchor_matches:true`, `snapshot_sha256:9dc40d25…093a` |
| repoint | old snapshot + manifest pinning its digest but naming `fe57cc8a…` and the round-11 frozen path | `manifest_invalid`, exit 2, never clean | `pinned:false`, `integrity:not_checked`, `integrity_result:not_checked`; primary finding is exact |
| unavailable | new snapshot + valid manifest, `--repo` a temp `git init` repository with no HEAD | `source_unavailable`, exit 2, mismatches 0 | `pinned:true`, `integrity:checked`, `integrity_result:match`, `correspondence:unavailable`, `snapshot_pin_matches:true`, `source_matches:null`, `source_anchor_matches:null`, `snapshot_sha256:9dc40d25…093a` |

`mismatches` is treated as the CLI's source-correspondence-only counter:
1 iff `source_matches` is false and `source_anchor_matches` is true, else 0.
Integrity/pin failures never inflate it. For C1, the runner additionally derives
the same tally from those two fields, so the before/after count is independent
of the CLI's aggregate:

```text
claim.before.source_correspondence_mismatches  = 1
claim.after.source_correspondence_mismatches   = 0
claim.source_correspondence_mismatches.delta   = 1
```

The receipt persists `head_before`, `head_after`, `measured_commit`, every
fidelity/control subprocess's full argv/stdout/stderr/exit, the source-blob read
(command/exit/hash/length, without copying source bytes), the manifest
expected/observed object and digest, per-case checks/observed fields, and
`claim.before`/`claim.after`.

## Independent source anchor

Before invoking fidelity, the runner reads the immutable source blob itself:

```text
git --no-pager --no-replace-objects -C <lane> cat-file blob \
  2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md
```

Code constants: OID `7de1360655eadada356fe110813c6e1338142551`, SHA-256
`9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a`,
18898 bytes. Checks: retrieved OID/SHA/length equal those constants; the new
snapshot equals the retrieved bytes and equals the pinned source SHA-256; the old
snapshot differs and equals the D1 frozen SHA-256 `52665cf2…2fa1`. The manifest
is independently validated against the same constants (`schema`,
`snapshot_path`, `snapshot_sha256`, `source_revision`, `source_path`,
`source_oid`, `source_sha256`, `source_bytes`, `expected_verdict:clean`). A
coherent snapshot+manifest edit therefore fails source correspondence; a
manifest repoint fails manifest validation before it can redirect the anchor.

Exit map: 0 all expectations; 1 an expectation failed; 2 could not evaluate
(missing CLI/artifacts, malformed manifest/output, source unavailable, selftest
failure, fixture setup failure, or HEAD changing mid-run). Malformed stdout,
missing fields, an unexpected could-not-evaluate finding, and non-string primary
findings are exit 2, not a false pass.

## Static evidence read

- Final `fidelity.py` (626 lines, refreshed): `PRIORITY` has no
  `source_anchor_mismatch`; anchor failure is `source_unavailable`; `mismatches`
  is computed as `int(source_matches is False and anchor_matches is True)`.
  Selftest defines the 11 fixtures above, including pin-only corruption with
  `mismatches:0`.
- `frozen/expected.json` read exactly: schema `kama-round-12-frozen/v1`,
  snapshot SHA-256 `9dc40d25…093a`, source revision `2f7303c…`, path
  `corpus/SOURCES.md`, OID `7de13606…2551`, source SHA-256 `9dc40d25…093a`,
  bytes `18898`, expected verdict `clean`. These equal the runner constants.
- `frozen/corpus/SOURCES.md` is 18898 bytes (directory listing), matching the
  pinned source length. Its digest was not recomputed by this seat.
- D1 hashes (`old frozen 52665cf2…2fa1` vs source `9dc40d25…093a`) are taken
  from the round-11 verifier spot-check, not re-observed here.

## L1 checks (not run by this seat)

1. `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/reproduce.py`
   - expect exit 0, `ok:true`, `measured_commit` equal to the committed HEAD.
   - expect `claim.source_correspondence_mismatches` 1 → 0 (delta 1).
   - expect records `before`/`after`/`selftest`/`coherent`/`tamper`/`repoint`/
     `unavailable` each with `matches_expected:true` and full argv/stdout/stderr/
     exit.
   - expect `selftest` `passed:11`, `failed:0` unless fidelity legitimately adds
     a fixture; the runner asserts `passed == len(checks)`, not a fixed 10.
2. Confirm receipt `independent.source_checks` all true and
   `independent.manifest_checks` all true.
3. Confirm `head_before` equals `head_after` and the worktree has no new writes
   beyond the committed round-12 files.

## Residual risks

- The runner is coupled to the CLI's stable JSON contract (`finding`,
  `mismatches`, integrity/correspondence fields). If fidelity changes a name,
  the runner exits 2 as could-not-evaluate rather than silently passing.
- The repoint case asserts `manifest_invalid`; if fidelity maps that manifest to
  another could-not-evaluate id, the runner reports exit 2, never `clean`.
- The empty-repo control relies on fidelity resolving a valid repository
  top-level and failing the pinned revision lookup; that is the current code
  path, but it remains an unexecuted dependency.
- `source_correspondence_mismatches` is a construction/reproduction check of the
  D1 repair, not a fresh discovery, scalar score increase, serving-readiness
  test, or capability claim. Old frozen round-11 bytes were not modified.
