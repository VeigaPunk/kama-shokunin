# Round 12 Safety sentinel: fidelity/runner trust boundary

Seat: KamaR12.Safety (sentinel, author advisor; this is not independent closure).
Scope: read scope, paths, env, subprocess, writes and manifest attacks for
`fidelity.py` and `reproduce.py`. I ran only read-only git, `ls`, `stat` and `sha256sum` probes.
I did not run fidelity, the runner, tests or selftest, so nothing here counts as a pass. No endpoint calls,
no installs.

## Timeline of review

1. **Contract pass:** at first, neither file nor `frozen/` existed. I derived S1–S7 from the spec
   and measured repository facts, and sent them to `KamaR12.Fidelity` and `KamaR12.Runner`.
2. **First fidelity.py (428 lines):** I found D-a…D-e (below) and sent them to Fidelity.
3. **Final state (605-line fidelity.py, 1524-line reproduce.py, frozen artifacts):** I re-read the files
   statically. The verdicts below describe this final state only. The authors may still edit, so L1 must
   re-read before running.

## Measured boundary facts

| Fact | Evidence |
|---|---|
| Lane repo is its own git root, HEAD `79fa2577…`, not a partial clone | `rev-parse --show-toplevel HEAD`; config has only `remote.origin.url`, no promisor or `extensions.*` |
| Fleet repo ignores the lane and **lacks the source commit** | fleet `.gitignore:1:*-shokunin/`; fleet `cat-file -t 2f7303c…` → `fatal` |
| Source `2f7303c…:corpus/SOURCES.md` = blob `7de13606…2551`, SHA-256 `9dc40d25…093a` | `ls-tree`; `cat-file blob` and `show` give the same digest |
| Old round-11 frozen SOURCES SHA-256 `52665cf2…fa1` (D1 confirmed) | `sha256sum` |
| **The old truncated snapshot is committed at HEAD** (blob `e03f233b…`), which makes it a self-correspondence target | `git cat-file -e HEAD:.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` |
| No `refs/replace`, grafts, alternates or shallow file | `for-each-ref refs/replace` returned nothing; `ls` → absent |
| Inherited env has `GIT_PAGER`, `GIT_EDITOR`, `GIT_TERMINAL_PROMPT` | `env` |
| New snapshot: regular file, 18898 bytes, SHA-256 `9dc40d25…093a` = source | `stat`, `sha256sum frozen/corpus/SOURCES.md` |
| `frozen/expected.json` pins snapshot_sha256, source revision/path/oid/sha256/bytes, `expected_verdict: clean` | file content |
| `frozen/README.md` existed at the first check and was **absent** at the final check | `ls frozen` |

## Contract findings S1–S7 → final status

| ID | Sev | Exploit path | Final status (static) |
|---|---|---|---|
| S1 | HIGH | A manifest names `source_revision=HEAD` and `source_path=` the round-11 frozen file. That committed truncated file then matches itself, so the old snapshot reads `clean` and the C1 1→0 result is fabricated | **Closed.** Constants `SOURCE_REVISION/PATH/BLOB_OID/SHA256/BYTES` (fidelity.py:46–50). `load_manifest` requires every manifest field to equal them, else `manifest_invalid` exit 2. Selftest `manifest-cannot-redirect-anchor` uses the real HEAD revision |
| S2 | HIGH | Resolving the repo from cwd (the fleet root) gives a false `source_unavailable` | **Closed.** The default `LANE = WAVE.parents[2]`, and the resolved `--show-toplevel` must equal `--repo` (no upward discovery). The runner passes `--repo ROOT` explicitly |
| S3 | MED | `refs/replace` or `GIT_DIR`/`GIT_OBJECT_DIRECTORY`/alternates env substitutes the source bytes | **Closed.** fidelity: `GIT_*` scrubbed, plus `GIT_NO_REPLACE_OBJECTS`, `GIT_NO_LAZY_FETCH`, `GIT_CEILING_DIRECTORIES`, `--no-replace-objects`, argv list, `stdin=DEVNULL`, timeout 120. The blob oid, SHA-256 and length are verified. The runner also scrubs `GIT_*` and uses `--no-replace-objects` (reproduce.py:368–369) |
| S4 | MED | An uncaught exception exits 1, the `source_mismatch` code, so a crash reads as a mismatch | **Closed.** `main` catch-all → `internal_error` exit 2. The runner requires a JSON object plus an exact field set |
| S5 | MED | Integrity and correspondence are conflated when no manifest is used | **Closed.** Separate `integrity`, `integrity_result`, `correspondence`, `pinned`, `snapshot_pin_matches` and `source_matches` fields. A matching unpinned snapshot gives finding `unpinned`, exit 2, never clean. The runner asserts these fields exactly per case (reproduce.py:131–269, 580–598) |
| S6 | LOW | Symlinked or special-file snapshot/manifest (`/dev/zero` makes the read unbounded) | **Closed.** Both reject `is_symlink()` and `not is_file()`. Selftest `symlink-snapshot-rejected` covers it. Output carries digests, sizes, offsets and the last git stderr line only |
| S7 | LOW | Fixtures write into the live tree, or the selftest walks into the enclosing repo | **Closed for the CLI.** All fixtures live in `TemporaryDirectory`, and the empty-repo control is a temp `git init`. Reads of the live repo run with `GIT_OPTIONAL_LOCKS=0`. See R-1 for the runner |

First-draft code defects D-a…D-e are all fixed in the final fidelity.py:
- D-a: `first_difference` now returns `limit` after the loop. Before, an empty snapshot caused `UnboundLocalError`, and a prefix got an off-by-one offset.
- D-b: catch-all added.
- D-c: regular-file and symlink guards plus git timeout added.
- D-d: `expected_verdict` must be `clean`, and the runner asserts `expected_matches`.
- D-e: the dead `or True` argument was removed.

## Residual findings (final state)

**R-1 CLOSED after report: `reproduce.py --output` could overwrite any file in the lane.** The first
guard only required a path beneath ROOT, so the receipt could atomically replace a pinned or immutable
file such as `frozen/expected.json` or `MANIFEST`. The final `resolve_output` (reproduce.py:924–947) confines output
to `WAVE/receipts/`, rejects the directory itself, and refuses existing paths. A negligible
exists→replace race remains (local only).

**R-2 CLOSED after report: anchor failure was labelled `source_mismatch`, exit 1.** In final
fidelity.py, a retrieved blob that fails the oid/SHA-256/length constants is reported as
`source_unavailable`, exit 2 (fidelity.py:286–294). It ranks above `source_mismatch`, and
`source_anchor_matches` / `checks[source_anchor]` keep the distinction. An interim id,
`source_anchor_mismatch`, was withdrawn, but reproduce.py:107, 117 still list it (dead, harmless).
The anchor-failure branch is not exercised by the selftest, so treat it as an untested guard.

**R-5 MEDIUM (integration, static): the runner's tamper control conflicts with the new mismatch count.**
fidelity.py:323 now counts only correspondence failures: `mismatches = int(source_matches is False and
anchor_matches is True)`. The runner's `manifest_digest_corruption` case (reproduce.py:241–262) uses
the exact snapshot with a zeroed pin, so `source_matches` is true and fidelity emits `mismatches: 0`. The
runner still expects `min_mismatches: 1`, so a correct control fails and the runner exits 1 (the C1
receipt would be falsely red). Fix: expect `mismatches: 0` there. I sent this to Runner. The selftest tamper
case uses the mutant snapshot, where `mismatches: 1` is consistent.

**R-3 INFO: runner finding check.** Non-clean cases check that the expected id is in a
heuristic union (`finding_ids`), not that `payload['finding'] == expected`. With the exact exit plus the
exact `pinned`/`integrity_result`/`correspondence`/`manifest_error`/`snapshot_error` fields, I found
no way for a wrong primary to pass. Adding `"finding"` to each case's `fields` would make this
explicit.

**R-4 INFO: `frozen/README.md` was removed.** Fidelity confirms this was intentional (parent
instruction): `frozen/` holds only `corpus/SOURCES.md` and `expected.json`. The provenance statement
("written directly from git show stdout bytes") now lives in the fidelity.py docstring and
`advice/Fidelity.md`.

No endpoint, credential, host-config, service or fleet-repo access appears in either file.
Every subprocess uses an argv list, and neither file uses `shell=True`. The runner records commands and
streams, but never `os.environ` values.

## Checks for L1 (not run by this seat)

1. Re-read both files, since authors may have edited them after this review. Grep for `shell=True`, `os.system`,
   `urllib|requests|socket|http`, and writes outside `TemporaryDirectory` / `--output`.
2. `python3 .ufo/waves/round-12/fidelity.py --selftest` → exit 0, `failed: 0`, 11 named cases.
3. `python3 .ufo/waves/round-12/reproduce.py` with **cwd = fleet root** and without `--output` → exit 0. Then run
   `git status --porcelain` in the lane (only the intended round-12 files) and in the fleet repo (unchanged).
4. Old snapshot `--manifest none` → `source_mismatch`, exit 1, `mismatches: 1`. New snapshot
   with the explicit manifest → `clean`, exit 0, `integrity_result: match`, `correspondence: match`.
5. Spot attack in a temp copy only: a manifest with `source_revision` = HEAD and `source_path` = the round-11
   frozen path → `manifest_invalid`, exit 2.
6. An empty temp snapshot with `--manifest none` → JSON `source_mismatch` with
   `first_difference_offset: 0`, and no traceback.
7. R-5 was still open at my final check: reproduce.py:244 still says `min_mismatches: 1` for
   `manifest_digest_corruption`. It must be 0, or the runner exits 1 on a correct control. Fidelity's
   selftest now has 11 cases, adding `pin-only-corruption-exact-snapshot` with `mismatches: 0`. The runner's
   `SELFTEST_REQUIRED_CASES` check is a subset check, so the extra case is compatible.

Tooling: no tools installed or updated.
