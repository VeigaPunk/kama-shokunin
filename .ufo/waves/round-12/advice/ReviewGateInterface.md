# Round 12 — ReviewGateInterface (static specification review)

Author advisor, not independent closure. Scope: shared fidelity CLI contract, `--manifest` defaults, snapshot override, expected source. No execution: `fidelity.py` does not exist yet in `.ufo/waves/round-12/` (only `record.json`, `spawn-result.json`, `validation.json`, `dispatch.json`, `spec.json`, `claims.json`, `advice/swarm-registry.json`), so this is a specification review, not a static review of code. Unrun != pass.

Tools installed/updated: none.

## Evidence read

- Shared CLI contract: `.ufo/waves/round-12/spec.json:2` and `dispatch.json:229` (`--snapshot PATH [--manifest PATH] [--repo PATH] [--selftest]`; "Default manifest …/frozen/expected.json").
- Fidelity task text: `spec.json:9` / `dispatch.json:234`: "Support --snapshot and --manifest, --repo optional. NO manifest means no integrity pin, explicitly unpinned but source comparison still valid; default invocation uses committed manifest. --selftest only temp git repo/fixtures."
- Runner task text: `spec.json:14` / `dispatch.json:239`: "Old snapshot fixed path .ufo/waves/round-11/frozen/before/corpus/SOURCES.md … coherent snapshot+manifest mutation source_mismatch … expected-manifest-only corruption snapshot_tampered … missing source revision source_unavailable."
- Round-11 pattern: `.ufo/waves/round-11/reproduce.py:17-18` (`ROOT = parents[3]`), `:29` (loads `frozen/expected.json`), `:31-37` (digest pre-check, JSON `error: snapshot_tampered`, exit 2), `:77-78` / `:85-86` (findings matched by `name`, tamper matched by `error`, two different payload shapes).
- Round-11 pin: `.ufo/waves/round-11/frozen/expected.json:15` pins the old before `SOURCES.md` at `52665cf2…`, which is the digest the closure proved is not the source-commit blob (`corpus/lessons/round-11-verifier-spotcheck.md:101-110`, D1; closure-observed actual `9dc40d25…`, not re-verified here).
- Claims: `claims.json:3` `before` = `79fa2577…` (round-12 start HEAD), while source commit = `2f7303c…`. Distinct identities.

## Findings, by severity

### F1 (high) — `--manifest` default contradicts "no manifest" and makes the D1 observation unreachable as specified
- The spec gives two incompatible readings of omission: "NO manifest means no integrity pin" vs "default invocation uses committed manifest" (`spec.json:9`). The CLI has no explicit opt-out flag; the only way to get "unpinned" is omission, which is also the default.
- The stated purpose, "Snapshot override without manifest allows observing old mismatch rather than tamper", only works if omitting `--manifest` disables the default. If the default applies on snapshot override, `--snapshot <old D1 file>` yields `snapshot_tampered` (exit 2) and the runner's "before mismatch exit 1" cannot be produced.
- Silent-downgrade risk: if the default `frozen/expected.json` is missing/unreadable and the code falls through to "unpinned", the gate would pass with no integrity pin. Missing default or explicitly passed manifest must be exit 2, never unpinned.
- Resolution (recommend): add an explicit mutually exclusive `--unpinned` flag (no `--manifest` value). Without it, the default manifest is always loaded; unreadable/absent manifest = exit 2. Runner calls the old snapshot with `--unpinned`, never with bare omission.

### F2 (high) — expected source must not come from the manifest
- `spec.json:2` says the manifest "pins snapshot SHA-256, source commit/path and expected clean verdict". If the code reads `source_commit`/`source_path` from the manifest, the coherent snapshot+manifest mutation the runner is meant to catch can point the comparison at any commit/path the attacker chooses, and `source_mismatch` is never reached.
- Resolution: `SOURCE_COMMIT = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad"` and `SOURCE_PATH = "corpus/SOURCES.md"` as module constants. A manifest field that disagrees with the constant = exit 2 (new finding ID, e.g. `manifest_invalid`, which the spec does not list). "Expected clean verdict" must not affect the exit code; exit derives only from the comparison.
- Stronger anchor (recommend): also pin the git blob object id of `corpus/SOURCES.md` at that commit as a constant. Object ids are content-addressed; a manifest cannot override it.

### F3 (high) — `--selftest` cannot produce clean/mismatch cases with a fixed commit
- A temp repo cannot contain commit `2f7303c…` unless the CLI accepts a commit override. The spec requires `--selftest` to "invoke actual CLI for clean/mismatch/tamper/unavailable" in temp fixtures, but also says the source commit is fixed. Only `source_unavailable` is achievable with a fixed commit.
- Options the fidelity owner must choose explicitly (I cannot pick): (a) selftest imports the module and passes fixture commit/path through function arguments, with the CLI entry point still using constants; (b) a selftest-only environment variable honored only inside the `--selftest` child process. Option (b) is an attack surface unless gated. Undecided = unimplementable; name it in the report to Main.

### F4 (medium) — `--snapshot` required vs `--selftest` alone
- Usage `--snapshot PATH [--manifest …]` shows `--snapshot` unbracketed (required). `--selftest` must run without a snapshot. Make `--snapshot` required only when not `--selftest` (mutually exclusive group), or the runner's selftest call exits 2 with usage.

### F5 (medium) — exit 2 is overloaded; exit alone cannot discriminate
- Exit 2 = `snapshot_tampered` = `source_unavailable` = argparse usage error (argparse default) = "could-not-evaluate" in the registry standard. Round-11 runner checked exit plus JSON key; round-12 needs the same.
- The spec defines no stdout schema. Round-11 used two shapes (`error` for tamper, `findings[].name` for mutants). Recommend one schema: `{"schema":…, "verdict":"clean|source_mismatch|snapshot_tampered|source_unavailable", "exit":N, "findings":[{"id":…}]}` with stable IDs, and the runner asserting on `findings[].id`, not exit alone.

### F6 (medium) — check precedence undefined
- Coherent snapshot+manifest mutation with source available must yield `source_mismatch` (1), not `snapshot_tampered`. Manifest-only corruption must yield `snapshot_tampered` (2). Source unavailable plus tamper: unspecified.
- Recommend fixed order: load → constants check (F2) → read git blob → compare to snapshot bytes → compare digest to manifest (if pinned). Report all findings; exit precedence `source_mismatch` (1) only when no exit-2 finding exists, or define explicitly. Whatever is chosen, write it into the registry row and selftest.

### F7 (medium) — git environment and replace refs can redirect the source
- `git show` honors replace refs and environment (`GIT_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NO_REPLACE_OBJECTS`) and config (including filters/textconv). A poisoned `refs/replace/2f73…` or ambient `GIT_DIR` can make `2f73…:corpus/SOURCES.md` return other bytes.
- Recommend: subprocess without shell; env sanitized (drop `GIT_*` path variables; set `GIT_NO_REPLACE_OBJECTS=1`); `git -C <repo> rev-parse --verify --quiet <commit>^{commit}` must equal the full 40-hex constant; read with `git -C <repo> cat-file blob <commit>:corpus/SOURCES.md` (raw bytes, no textconv); compare blob oid to the pinned constant (F2).
- `--repo` default is unspecified; default to `ROOT = Path(__file__).resolve().parents[3]` as round-11 does (`round-11/reproduce.py:17`), not CWD.

### F8 (medium) — source-absence and git-failure mapping
- Commit missing, path absent at commit, non-repo `--repo`, empty output, and git non-zero exit must all map to `source_unavailable` (exit 2), never `source_mismatch` (exit 1) or clean. Spec does not say; the selftest should assert each.

### F9 (medium) — manifest self-integrity is circular in the round-11 pattern
- Round-11 loads `expected.json` and verifies inputs against it (`round-11/reproduce.py:29-37`). The manifest's own digest is pinned nowhere. Only the git comparison (after F2) is independent. Recommend pinning the manifest SHA-256 as a constant or in the `SKILL.md` registry row, and having the runner reference that external pin.
- The round-11 pre-check passing on `52665cf…` (`round-11/frozen/expected.json:15`) proves digest self-consistency only, the exact point D1 makes. The new gate must not reuse that pre-check as source authority.

### F10 (low) — relative path resolution and snapshot provenance
- Relative `--snapshot`/`--manifest`/`--repo` resolution (cwd vs ROOT) is unspecified. Runner should pass absolute paths; CLI should resolve against cwd and say so in help.
- The new snapshot's creation command is not recorded. Require the manifest or a sidecar to record the exact `git cat-file blob` command and blob oid, so the bytes can be re-derived without tool-rendered text.

### F11 (low) — identity labelling
- `claims.json` `before` (`79fa2577…`) is the round-12 start HEAD; source commit is `2f7303c…`. Runner's "measured HEAD" must be labelled separately from the source constant.

## Checks for L1 (named, not run)

1. `grep -n "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad" .ufo/waves/round-12/fidelity.py` — constant present; no `commit` read from manifest.
2. Old snapshot with `--unpinned`: expect exit 1, finding ID `source_mismatch`. Old snapshot with no flag: expect `snapshot_tampered` (documents F1 choice).
3. Missing/unreadable default manifest: expect exit 2, never a clean verdict.
4. `--selftest` alone: must not exit 2 for usage (F4).
5. Coherent snapshot+manifest mutation in a temp copy: expect exit 1 `source_mismatch` (F2/F6).
6. Manifest-only mutation: expect exit 2 `snapshot_tampered`.
7. Replace-ref/`GIT_DIR` poisoning in an isolated temp repo: expect no redirection (F7).
8. New snapshot `sha256sum` equals the digest of `git -C <repo> cat-file blob 2f7303c…:corpus/SOURCES.md` bytes (independent of tool rendering).
9. Old round-11 frozen files byte-identical before/after (no writes).

## Residual risk

- Specification-only: every finding above is static, from text. Actual behaviour of the fidelity CLI is unobserved.
- F3 and F1 need decisions from the fidelity owner (`KamaR12.Fidelity`) and the main agent before implementation; I did not choose on their behalf.
- D1 hashes are closure-observed, not re-verified here.

## Post-landing static read of fidelity.py (no execution)

Read: `.ufo/waves/round-12/fidelity.py` (landed, 611 lines), `frozen/expected.json`, and the presence of `frozen/corpus/SOURCES.md`. Static only; the snapshot's bytes and the pinned blob's oid/sha/size were not computed here.

- F1 closed: `resolve_manifest` maps `auto` to the default manifest only for the default snapshot, `none` to unpinned, and a missing or invalid manifest to `manifest_invalid` (exit 2).
- F2 closed: `load_manifest` rejects any manifest whose `source_revision`, `source_path`, `snapshot_path`, `source_oid`, `source_sha256`, `source_bytes` or `expected_verdict` differs from the code constants. `expected_matches` is informational and does not affect exit.
- F3 closed: the selftest reads the pinned blob read-only from `LANE` and writes only inside a temporary directory. The missing-source control uses a temporary `git init` repository.
- F4 closed: `--snapshot` defaults to `None`; `--selftest` returns before evaluation.
- F5/F6 closed: `PRIORITY` is applied via `next(...)`; exit is `0` only for `clean`, `1` only for `source_mismatch`, and `2` otherwise.
- F7 closed: `git_environment` strips every `GIT_*` variable, sets `GIT_NO_REPLACE_OBJECTS=1`, and each git call passes `--no-replace-objects`. Read path is `rev-parse --verify` then `cat-file blob`.
- F8 closed: retrieval failures are `source_unavailable`; a retrieved blob that fails the pinned oid, sha256 or byte count is `source_anchor_mismatch`, exit 2, as landed after the owner's correction. Snapshot divergence from a verified anchor is `source_mismatch`, exit 1.

Residual, static:

- Superseded by the final read below: the anchor-failure branch is `source_unavailable` (exit 2), not `source_anchor_mismatch`; it has no selftest fixture and is a static guard.
- Superseded by the final read below: a final-component symlink of the default snapshot is `snapshot_unavailable` (exit 2); other spellings of the default path are `unpinned`.
- L1 checks to run: `sha256sum` and `wc -c` of `frozen/corpus/SOURCES.md` against `9dc40d25…` and `18898`; `git rev-parse 2f7303c…:corpus/SOURCES.md` against `7de13606…`; default invocation exit 0; `--selftest` exit 0 with all eleven records passing (11/11).

## Final code static read (post-release, no execution)

Read: final `fidelity.py` (617 lines) and `frozen/expected.json`. Static only; no digest, blob oid or selftest was computed or run.

Confirmed:

- Manifest matches the code constants exactly: `source_revision` 2f7303c…, `source_path` and `snapshot_path` `corpus/SOURCES.md`, `source_oid` 7de13606…, `source_sha256` 9dc40d25…, `source_bytes` 18898, `expected_verdict` `clean`. `snapshot_sha256` equals `source_sha256`, consistent with a byte copy (not verified here).
- Anchor failure is merged into `source_unavailable` (exit 2). The detail names the anchor mismatch. No `source_anchor_mismatch` remains in the docstring, `PRIORITY` or exit mapping. `source_mismatch` can be primary only with a verified anchor.
- `PRIORITY` is `snapshot_unavailable, manifest_invalid, snapshot_tampered, source_unavailable, source_mismatch, unpinned, clean`. Exit is `0` only for `clean`, `1` only for `source_mismatch`, otherwise `2`.
- `mismatches = int(source_matches is False and anchor_matches is True)`.
- A final-component symlink of the snapshot is `snapshot_unavailable` (`is_symlink` on the `abspath`). Other spellings of the default path resolve to `unpinned`.

Actionable defects:

1. Expectation defect, not a code defect. Manifest-only corruption against a pristine snapshot yields `snapshot_tampered`, exit 2, `mismatches` 0, because `source_matches` is True. The statement "manifest-only corruption … mismatches 1" holds only when the snapshot also diverges, as in the selftest `snapshot-tampered` fixture. Runner and registry expectations for expected-manifest-only corruption must assert `mismatches` 0, or not assert it.
2. Coverage gap. No selftest record exercises a pin-only failure with a pristine snapshot; the `snapshot_pin` branch is covered only where the snapshot also diverges. Optional: add a record with the clean snapshot and a wrong-digest manifest, expecting `snapshot_tampered`, exit 2, `mismatches` 0.
3. The anchor-failure branch remains untested (already recorded as a static guard).

No other defects found in the manifest, precedence, exit mapping, git invocation or selftest isolation.

Checks for L1 (not run): default invocation exit 0, `finding` clean, `mismatches` 0; `sha256sum` and `wc -c` of `frozen/corpus/SOURCES.md` equal `9dc40d25…` and `18898`; `git rev-parse 2f7303c…:corpus/SOURCES.md` equals `7de13606…`; `--selftest` exit 0 with eleven records (11/11); wrong-digest manifest with pristine snapshot gives `snapshot_tampered`, exit 2, `mismatches` 0.

Status update (owner-reported, consistent with the landed file): Defect 1 is resolved in the report and Runner contract: pin-only corruption against a pristine snapshot is `snapshot_tampered`, exit 2, `mismatches` 0, `source_matches` true; mutated-snapshot tamper remains `mismatches` 1. Defect 2 is resolved: selftest has an eleventh fixture `pin-only-corruption-exact-snapshot` (clean snapshot with zero-digest manifest) asserting `snapshot_tampered`, exit 2, `mismatches` 0. The `--selftest` L1 expectation is 11/11, not 10. Defect 3 (anchor branch) remains a documented static guard.
