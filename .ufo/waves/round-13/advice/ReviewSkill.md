# ReviewSkill — round 13: does KQ16 apply through the SKILL criteria pointer?

Scope: read-only review. No corpus, SKILL, code, or LOG edits. No builds, tests, gates, or `fidelity.py` runs. Only read-only `git show` and `sha256sum` (see Limits). Tools installed or updated: none.

## Verdict

- **KQ16 applies automatically** once it is appended as a new row in `corpus/QUALITY.md`. No `SKILL.md` edit is required for applicability.
- **Minimal cutover:**
  1. Append a `Criteria added — round 13` section with one KQ16 row at the end of `corpus/QUALITY.md`. Leave line 49 (KQ15) byte-intact.
  2. Use the KQ14 supersession convention in the ID cell: `KQ16 (supersedes KQ15's exit-class and capture/comparison formulations only; KQ15 otherwise preserved)`.
  3. Append a `LOG.md` entry. `AGENTS.md` requires one for every change.
- **Do not edit** `SKILL.md:382` (`round 12 appends KQ15`) or add a new pointer. The generic clause already covers later rows, and `SKILL.md:378-380` says dated corrections are history, not rewritten.
- `corpus/README.md:21` (`follow QUALITY.md`) and fleet scripts need no change; none enumerate KQ IDs.

## Evidence

1. **Current pointer** (`SKILL.md:380-384`): admission is judged against "KQ1–KQ14 plus every subsequently appended criterion (round 12 appends KQ15) — all applicable, never a subset, with each row's recorded supersession preserved". The generic phrase "every subsequently appended criterion" covers KQ16 without edits.
2. **Supersession convention**: `corpus/QUALITY.md` ID cell for KQ14, `KQ14 (supersedes KQ7's sufficiency, preserves its append-only rule)`. KQ16 should follow this form.
3. **No enumerations**: a case-sensitive grep of `KQ[0-9]+` over `scripts/`, `CORPUS.md`, `LEARNING.md`, and `MISSION.md` returns no matches. In `kama-shokunin`, `KQ15` appears only in `QUALITY.md`, lesson prose, `LOG.md`, and the round-12 registry. `corpus/README.md` and `SCORECARD.md` do not list IDs.
4. **KQ16 not yet present** (`corpus/QUALITY.md` last criterion row is KQ15 at line 49). This is pending mid-flight work, so applicability is conditional on the row being appended.
5. **KQ15 literal claims vs code** (`corpus/QUALITY.md:49`; `.ufo/waves/round-12/fidelity.py`):
   - "distinct nonzero exits" is inaccurate. `fidelity.py:319` maps `0 if clean else (1 if source_mismatch else 2)`. `snapshot_tampered` exits 2 (`:502`, `:511`); `source_unavailable` exits 2 (`:519`); `source_mismatch` exits 1 (`:305`, `:535`). Finding IDs are distinct; exit 2 is shared.
   - "compared with the blob fetched directly as `git show`" is inaccurate. `fidelity.py` contains no `show` call except `--show-toplevel` (`:115`). Comparison uses `rev-parse --verify` (`:261-262`) and `cat-file blob` (`:271-272`).
   - Capture by `git show` is consistent with `SKILL.md:396` ("captured byte-exactly via `git show`"), `lessons/round-12.md:14-15`, and `round-12-verifier-spotcheck.md:147`. The literal `capture: git show; comparison: git cat-file blob` is therefore accurate.
6. **Precedence clause KQ16 should add**: `fidelity.py:55-56` says every exit-2 finding outranks `source_mismatch`. A snapshot that is both tampered and divergent exits 2 with `finding=snapshot_tampered`, and `source_mismatch` remains only in `findings`. Without this clause, the `source_mismatch=1` literal invites a wrong reading.
7. **Frozen anchor**: `.ufo/waves/round-12/frozen/expected.json` pins `source_sha256` `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` at commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`. Read-only `git show 2f7303c:corpus/SOURCES.md | sha256sum` returned that same digest. The working-tree `corpus/SOURCES.md` has a different digest (`1f25e0…`), so KQ16 should name the pinned commit, not `HEAD`.

## Required literal phrases (for the criterion writer)

- `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
- `capture: git show; comparison: git cat-file blob`

Both match the code and registry above.

## Limits

- Applicability is textual. I did not read KQ16's final bytes, because the writer has not appended them yet. Re-check when notified.
- The SKILL pointer names KQ15 explicitly and covers later rows only generically. That is sufficient for KQ16 but is a reader-facing trap. Preserving it is intended.
- Whether `git show` applies textconv or filters to blobs is not established here. The S032 quote covers only plain-content behavior. KQ16 should describe capture as the frozen-copy procedure, not as byte-identity by construction. [INFERENCE]
- Executed: read-only `git show 2f7303c:corpus/SOURCES.md | sha256sum`, and `grep`/`sed`/`cat` reads. Not executed: `fidelity.py` (any mode), `--selftest`, `sources-census.sh`, or any gate.
- Tools installed or updated: none.
