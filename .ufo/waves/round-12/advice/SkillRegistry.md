# SkillRegistry — round-12 SKILL.md correction and gate registry

## Files changed

- `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md` — append-only, 36
  added lines, 0 changed content lines in prior rows. `git diff --numstat`
  reports `36 1`; the single `-` line is the former EOF row re-emitted because
  the committed file had no trailing newline (`\ No newline at end of file`),
  which an append requires. No earlier row, table cell, heading or paragraph
  changed.

## D3 correction (appended, 2026-10-20)

Anchor corrected: `SKILL.md:357` still reads "Admission remains
`corpus/QUALITY.md` KQ11–KQ13"; it is preserved as dated history. The appended
section `## Round-12 correction — admission criteria pointer (D3, 2026-10-20)`
states that admission is the complete applicable `corpus/QUALITY.md` set —
KQ1–KQ14 plus every subsequently appended criterion (round 12 adds KQ15), all
applicable, never a subset, with recorded supersession preserved (KQ14 governs
KQ7's sufficiency) — and that KQ11–KQ13 alone admit nothing.

Static verification of the pointer: `grep -n KQ15
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md` returns line 49
with a KQ15 row, so the "round 12 appends KQ15" reference resolves at write
time. The correction adds no serving capability, probe behavior or endpoint
expectation, and says so in-file.

## Round-12 gate registry row (appended)

Section `## Round-12 local evidence registry (owner: kama)`, additive to the
round-11 registry; prior rows unchanged. Row fields follow PROTOCOL §Gate
standard (name, gate|probe, entry command, verdict map, self-test spelling,
pinned values, write scope, owner).

Static read of the landed `.ufo/waves/round-12/fidelity.py` (read-only; never
executed) confirms the registered interface:

| Field | Registered value | Source observed |
|---|---|---|
| Name | Exact-source snapshot fidelity (D1 corrective snapshot) | SKILL.md |
| Kind | gate | `sys.exit(main())`, exit-bearing verdict |
| Entry command | `python3 .ufo/waves/round-12/fidelity.py --snapshot PATH [--manifest PATH] [--repo PATH]`; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md`; `--manifest` default `auto` → `.ufo/waves/round-12/frozen/expected.json` on the default snapshot; source constants commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`, path `corpus/SOURCES.md` | argparse lines 543–555; `DEFAULT_SNAPSHOT`, `DEFAULT_MANIFEST`, `SOURCE_REVISION`, `SOURCE_PATH`; `resolve_manifest()` |
| Verdict map | 0 clean; 1 failed (`source_mismatch`); 2 could-not-evaluate (`snapshot_tampered`, `snapshot_unavailable`, `manifest_invalid`, `source_unavailable`, `unpinned`, `internal_error`); undeclared nonzero reads could-not-evaluate | `exit_code = 0 if clean else (1 if source_mismatch else 2)`; exception handler returns `internal_error`/2 |
| Self-test | `python3 .ufo/waves/round-12/fidelity.py --selftest` (spelling `--selftest`): real child CLI over temporary snapshot/manifest fixtures and a temporary empty git repo, reading the pinned immutable blob from the live lane repo read-only via `--repo LANE`, asserting exit code and stable finding ID for clean, coherent snapshot+manifest mutation, snapshot tamper, unavailable source, unpinned match/mismatch, manifest anchor redirect, absent manifest, missing snapshot and symlink refusal | `selftest()` `record(...)` cases lines ~456–525; `source_repo = LANE` line 439; `run_git('init', …, empty)`; `TemporaryDirectory`; `invoke()` spawns `sys.executable` |
| Pinned values | `.ufo/waves/round-12/frozen/expected.json` pins snapshot SHA-256 and path, source revision, path, blob OID and content SHA-256, expected clean verdict; default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md` captured byte-exactly via `git show` | `load_manifest()` required fields; code constants; frozen `README.md` provenance statement |
| Write scope | Read-only over the lane repo and git history; no endpoint or live-service access; ordinary runs write nothing; `--selftest` writes and removes isolated temp snapshot/manifest fixtures and a temp empty git repo only | normal path only prints JSON; self-test uses `TemporaryDirectory`; `git_environment` disables prompts/optional locks |
| Owner | kama | section heading and row |

The row's note records: the default invocation uses the committed manifest;
an overridden snapshot without `--manifest` is unpinned and a matching unpinned
snapshot is `unpinned` exit 2, never clean; digest pinning is verified before a
compared verdict; source correspondence is separate from digest integrity and
the manifest cannot redirect the code-constant source anchor; the frozen
expected file pins an immutable revision and does not follow mutable `HEAD`.

## Static findings and limits

- `fidelity.py` landed during this seat's work and was read statically only.
  At the final read, `.ufo/waves/round-12/frozen/expected.json` (477 bytes) and
  `.ufo/waves/round-12/frozen/corpus/SOURCES.md` (18 898 bytes) are present.
  The manifest was read and carries `schema kama-round-12-frozen/v1`,
  `snapshot_path`, `snapshot_sha256`, `source_revision`, `source_path`,
  `source_oid`, `source_sha256`, `source_bytes` and `expected_verdict: clean` —
  the field set the registry row names. Its `source_revision` is the pinned
  `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` and `source_path` is
  `corpus/SOURCES.md`.
- No digest recomputation, byte comparison, fidelity CLI invocation,
  `--selftest`, or `reproduce.py` run was performed by this seat. The manifest
  pins are observed fields, not a re-executed match. **Unrun is not pass.**
- No endpoint, config, environment, service or host surface was read.
- No tool was installed or upgraded.

## Checks for L1

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff -- SKILL.md` — confirm
   pure append; prior registry rows byte-identical.
2. Confirm `frozen/expected.json` snapshot digest equals
   `sha256sum frozen/corpus/SOURCES.md` and that both equal the git blob at the
   pinned revision/path; this seat did not recompute either.
3. Run the gate's `--selftest` once at integration; confirm exit 0 and that the
   case list covers clean/mismatch/tamper/unavailable. Confirm the default
   invocation (no `--snapshot`) exits 0 and an old round-11 frozen SOURCES
   override without a manifest exits 1 `source_mismatch`, not a pass.

## Risk

The row is aligned to the current `fidelity.py` and the observed manifest
fields. If the Fidelity owner changes finding IDs, default-manifest resolution,
or the exit split before integration, the row must be reconciled; the digest
match itself is unverified by this seat.
