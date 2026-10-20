# CodeBaseline — advisory review of measure.py baseline pin, schema, frozen copy, tamper behavior

Lane: kama round 11 (`kama-shokunin/.ufo/waves/round-11/`). Seat: `KamaR11.CodeBaseline` (leaf, advisory, non-author). Outside non-author review remains separate.

## Scope and method

- Reviewed: `.ufo/waves/round-11/measure.py` (current revision, sha256 `92c7fde5c845f751fed8274576d4450a2e189ec4c45a0b24fd391f32ea1d23a8`, 585 lines, mtime 2026-10-20 00:43:59 -0300); `.ufo/waves/round-11/legacy-baseline.json` (sha256 `5d704e90a4ad758f375c5d1312dad7c972b7d1d1a105a7dba3250282f7c38af1`, 2066 bytes); `.ufo/waves/round-11/frozen/before/corpus/knowledge/*.md` (9 files); the nine live `corpus/knowledge/*.md` provenance supplements.
- **measure.py was NOT executed**, including `--selftest`, `provenance`, `crosswalk`. Selftest expectations were checked by reading only.
- Evidence came from read-only operations: file reads, `sha256sum`, `head -c`, `wc -c`, `stat`, `grep`, and read-only git subcommands (`cat-file -e`, `ls-files`, `log`, `status`, `show`, `check-ignore`, `rev-parse`). The digests are reproducibility evidence, not a run of the gate.
- Mid-review, `measure.py` changed on disk (mtime 00:43:59, size 28949). My first pass read an earlier revision that said "committed baseline" and "lane commit 2f7303c" in the pin comments. This report reviews the current bytes only; the stale wording is no longer present (see "Already correct").

## Findings, by severity

### F1 — Medium: the tamper pin has no independent, tracked anchor
- `measure.py:62-66` says the baseline pin makes "an edited snapshot cannot bless a mutation." The code only enforces that the baseline bytes equal the constant `BASELINE_SHA256` at `measure.py:99`.
- Both the pin and the baseline are untracked. `git status --short -- .ufo/waves/round-11` → `?? .ufo/waves/round-11/`. `git log --all -- .ufo/waves/round-11` is empty. `git check-ignore` reports nothing.
- An edit that changes both `legacy-baseline.json` and the constant at `measure.py:99` passes with no VCS trace. The guarantee holds only against a baseline-only edit.
- **Smallest repair:** either commit `measure.py` and `legacy-baseline.json` together so that any pin change appears in a reviewable diff, or reword lines 65–66 to say the pin detects baseline-only edits and that `measure.py` itself is not yet tracked.

### F2 — Low/Medium: `--baseline` is only usable with the pinned bytes, and the docs do not say so
- `main()` always calls `check_provenance(root, baseline_path, BASELINE_SHA256)` (`measure.py:576-577`).
- The module usage text (`measure.py:23-25`) describes `--baseline PATH` as a free option. Any copy with different bytes returns `snapshot_tampered` (exit 2). Byte-identical copies still pass.
- No selftest case covers `main()`'s `--baseline` path. The selftest passes its own digest explicitly (`measure.py:412-415`).
- **Smallest repair:** document in the usage block that the value must be byte-identical to the pinned file, or remove the flag under the clean-cutover rule.

### F3 — Low: baseline entries carry an unvalidated, undocumented `missing` key
- Each entry in `legacy-baseline.json` has `"missing": ["source", "verified-at", "recheck"]` (e.g. lines 5–9, 14–18; all nine entries).
- `_valid_entry` (`measure.py:199-206`) checks only `sha256` and `bytes`. It accepts extra keys and never reads `missing`. The docstring does not describe the schema.
- Impact is limited because the digest pins the file. The 27-field count is recomputed from live bytes, not from this key.
- **Smallest repair:** drop `missing` from the baseline, or document it as informational and state that the gate ignores it.

### F4 — Low: `_scan_supplement` fence and duplicate-key handling is latent-fragile
- `_scan_supplement` toggles fences on `line.strip().startswith("```")` (`measure.py:160`). It treats indented fences as toggles and does not recognize `~~~` fences.
- `json.loads` (`measure.py:226`) keeps the last value for duplicate keys. The digest pin covers the current bytes, so this only matters if the pin is weakened.
- No current supplement is affected: I checked that no fence line falls inside any supplement region (see "Already correct").
- **Smallest repair:** none required now. Note as latent if the pin is ever relaxed.

### F5 — Nit: frozen copy is not referenced by the gate
- `frozen/before/corpus/knowledge/*.md` (9 files, 138376 bytes total) match the baseline's pre-append bytes exactly: full-file sha256 and size equal the baseline `sha256` and `bytes` for all nine (verified below).
- `measure.py` never reads `frozen/`, and nothing pins those copies. The directory is untracked. The same bytes are reproducible from `HEAD`: `git show HEAD:corpus/knowledge/<f>.md` matches for all nine.
- **Smallest repair:** state in the docstring that `frozen/` is a manual, non-gated copy, or remove it and cite `HEAD` as the source of truth.

### F6 — Nit: directory-walk wording
- `measure.py:21-22` says the default root is "three directories above this file." `LANE_ROOT = Path(__file__).resolve().parents[3]` (line 92) is the kama-shokunin directory, which is correct under the reading "above this file's directory." The wording is ambiguous enough to misread; consider naming `parents[3]`.

## Already correct (verified)

- **Pin matches the live baseline.** `sha256sum legacy-baseline.json` = `5d704e90…8af1` = `BASELINE_SHA256` (`measure.py:99`).
- **Pinned revision comment is accurate.** `measure.py:62-64`: the entries describe source files at `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad`, and the baseline "lands with this round, not in that earlier revision." Confirmed: `git cat-file -e 2f7303c…:.ufo/waves/round-11/legacy-baseline.json` and `…/measure.py` both fail with "exists on disk, but not in '2f7303c…'". Commit `2f7303c` exists (2026-10-19 22:05:55 -0300, "Integrate remote documentation; preserve local round log").
- **Revision wording.** `measure.py:95-100`: `BASELINE_REVISION` "identifies the original source files, not the addition of the baseline file" and "informational only." The only use is the payload key `baseline_revision` (`measure.py:311`).
- **Evaluation order.** The docstring (`measure.py:67-69`) matches the code: JSON parse and non-empty (225–233), then digest (234–239), then per-entry schema (240–248).
- **Exit codes.** Docstring (`measure.py:29`) matches returns: `snapshot_tampered` 2 (239), `invalid-baseline` 2, `invalid-root` 2 (574), finding-based failure 1 (324, 373).
- **Check names.** Docstring names (`prefix-mutation`, `missing-field`, `duplicate-field`, `missing-supplement-heading`, `verified-at-live-claim`) match the emitted finding names (`measure.py:276, 289, 293, 297, 302`).
- **Live-claim guard.** The regex and negation window (`measure.py:126-142`) match docstring lines 50–58.
- **Prefix bytes.** For all nine baseline entries, `head -c <bytes> <live file> | sha256sum` equals the baseline `sha256`. The live files are longer than their `bytes` values by the appended supplement (e.g. `alias-endpoint-normalization.md` 10729 vs 7595).
- **Frozen copies.** Full-file sha256 and size of all nine `frozen/before` files equal the baseline entries.
- **Supplement anchors.** The three supplements that quote a pre-append sha256 (alias-endpoint-normalization, consumer-registry, cross-lane-scope) quote values that match the baseline. `served-model-identity.md` says its bytes were "committed in `c6199a2` … and unchanged at HEAD": `c6199a2` is dated 2026-09-28 23:15:05 -0300 with subject "round-1: operability axis". Its sha256 equals the baseline entry, and so does HEAD. `listener-census.md`'s pre-append bytes match the `ea72c3e` / HEAD baseline entry.
- **HEAD carries the pre-append bytes.** `git show HEAD:corpus/knowledge/<f>.md | sha256sum` equals the baseline `sha256` for all nine files.
- **Supplement shape.** Each of the nine supplements has exactly one column-zero `source:`, `verified-at:`, `recheck:` line and one `## Provenance supplement` heading. No supplement region contains a fence line, so fence exclusion does not change any count.
- **Selftest expectations (by reading, not run).** The 13 cases in `run_selftest` (`measure.py:377-549`) map to the findings and exit codes they assert. The 9 cases with `expect_code=2` / `expect_error` are consistent with the evaluation order above.

## Verification gaps

- No execution. `provenance`, `crosswalk`, and `--selftest` were not run, so the selftest pass count and the exact JSON outputs are unobserved.
- The crosswalk entry `corpus/knowledge/served-identity-crosswalk.md` exists but was not measured.
- Liveness claims in the supplements were not revalidated (out of scope; no endpoint contacted).
- The frozen-copy and HEAD digests were computed read-only; I did not re-derive the baseline from HEAD with the gate.

## Installs and tool changes

None. No packages were installed, updated, or upgraded. No environment was changed.

## Write set

This report only. No edits to `measure.py`, `legacy-baseline.json`, `frozen/`, the corpus, or git state.
