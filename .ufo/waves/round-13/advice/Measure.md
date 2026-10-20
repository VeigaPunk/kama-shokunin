# Round 13 — Measure: KQ16 textual criterion gate and frozen evidence

Author: KamaR13.Measure (leaf executor). No gate execution, build, test, linter, commit or push by this seat. All statements below are static reads, byte comparisons, or a stdlib `ast.parse`; none is an executed gate result.

## Files written

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.ufo/waves/round-13/measure.py` | 39463 | source under test; final sha256 `2399d64dcde477dd26f6f1092819b6392fc812dc5a64a949f8e075d6a0918fd6` |
| `.ufo/waves/round-13/frozen/before/corpus/QUALITY.md` | 8619 | `157495271d58d6deb56260b093923961e40fb8402ed7475bc4a05c88cdd173cf` |
| `.ufo/waves/round-13/frozen/after/corpus/QUALITY.md` | 12469 | `596f87caf560a5b6c70e7796597a9d2788b9074149ae99f205b73ef2dbb813da` |
| `.ufo/waves/round-13/frozen/expected.json` | 962 | pins both snapshots; manifest SHA-256 `21b6c4ac37e115cbbc9358a06f8d458cddbde27a4de727b1609e98ba15c49196` |

The before snapshot is the exact `git cat-file` blob at `941bb32c3f591bc63cbf7579b2b6c552228307cd:corpus/QUALITY.md` (8619 bytes). The after snapshot is byte-identical to the final `corpus/QUALITY.md` (12469 bytes, sha `596f87ca…813da`), confirmed by `cmp -s`; Criterion confirmed no further edits. Raw prefix holds: `after.startswith(before)`. The KQ15 line plus LF hashes to `b559befa6bf3bbdabd00482d6a6630bbfbefdf8d4371f74d998f6e1f9c07618c`, matching Criterion and ReviewPreservation. Static row parse: exactly one `| KQ16 |` row, four cells, both exact literals in the admit cell, exit pairs 1/2/2, forbidden phrase absent, no reversed comparison/capture and no KQ15 comparison formulation.

## Behavior

`measure.py` is a bounded textual KQ16 gate, not a runtime, serving, capability, or semantic-admission gate.

Interface (settled for the SKILL registry):

- live unpinned: `python3 .ufo/waves/round-13/measure.py [--quality PATH] [--before-revision REV]`. Defaults: `LANE/corpus/QUALITY.md` and `941bb32c3f591bc63cbf7579b2b6c552228307cd`. Historical bytes come from `git cat-file blob <resolved>:corpus/QUALITY.md`; `rev-parse HEAD` records the actual measured revision; `HEAD:corpus/QUALITY.md` must equal the worktree bytes for a clean verdict.
- frozen pinned: `--manifest .ufo/waves/round-13/frozen/expected.json [--quality PATH]`, default selection the after snapshot. Both input digests are verified before content; `--quality .ufo/waves/round-13/frozen/before/corpus/QUALITY.md` yields exit 1 / `documentation_mismatch`, `--quality .ufo/waves/round-13/frozen/after/corpus/QUALITY.md` yields exit 0 / `clean`.
- `--selftest`: spawns this CLI as real `[sys.executable, '-I', '-B', …]` children over isolated temporary fixtures. Ten cases: before red (exit1, missing2), after green (exit0, missing0), missing exit-map literal (exit1, missing1), missing capture/comparison literal (exit1, missing1), reintroduced `distinct nonzero exits`, reintroduced KQ15 comparison formulation, contradictory `comparison: git show`, conflicting `source_unavailable=1`, missing KQ16 row (exit1, missing2), altered pinned snapshot (exit2, `snapshot_tampered`). Each asserts exit plus stable finding id and, where applicable, the missing count. A green selftest is gate self-consistency only.

Stable findings and exits: `clean` 0, `documentation_mismatch` 1, `snapshot_tampered` 2, `probe_error` 3. `snapshot_tampered` is explicitly scoped in JSON to the round-13 frozen QUALITY input digest, not round-12 SOURCES/model-source provenance. Evaluation modes emit exactly one JSON object on stdout; `--help` is conventional argparse plaintext and is excluded from that statement. Commands are recorded as argv only, never env. The `--selftest` help text no longer carries an author-execution claim.

Checks: exactly one KQ16 table row (`^\|\s*KQ16(?![\w-])`); only its admit cell; only in the appended region after the byte-prefix check; exact literals; whitespace-tolerant forbidden phrase `distinct\s+non-?zero\s+exits?`; bounded contradiction literals; raw byte prefix; KQ15 line reported; frozen digests. Fenced blocks and HTML comments are masked. Git reads use `--no-pager --no-replace-objects -C LANE`, stripped `GIT_*` plus fixed noninteractive env, `--end-of-options` before the revision, `stdin=DEVNULL`, timeout, argv only. Live clean additionally requires the pinned start revision, before missing count exactly 2, the canonical non-symlink lane path, and worktree/HEAD equality. Frozen clean additionally requires the manifest-declared before revision to be the pinned start and before missing count 2. Frozen snapshot paths must stay inside the manifest directory. Per L1, the low ReviewProbe items are retained as limits rather than new enforcement.

## Limits

- The 2 -> 0 denominator counts adoption of two exact wordings from the outside D1 finding (`corpus/lessons/round-12-verifier-spotcheck.md:147`); the historical text has no KQ16 row, so both literals are missing there by construction. This gate did not discover the discrepancy.
- Textual conformance is not semantic truth. The exit map holds for the primary finding only; the literal cannot verify that qualifier. Capture provenance is author-attested; byte identity cannot reveal the producing command.
- Exact literal matching penalizes legitimate paraphrase; a paraphrase of the forbidden wording can evade detection. Quoting the superseded phrase in the admit cell fails even when negated.
- Manifest pins prove input immutability, not correspondence or a verdict; a coherent snapshot+manifest rewrite remains possible. Frozen mode does not re-fetch history.
- The original in-memory mutation-control request is satisfied by the L1-revised, Gate-standard `--selftest` child fixtures; no separate in-memory mutant report is emitted.
- `expected.json`'s `kq15_line_sha256` is informational: the whole pinned before digest plus raw byte prefix implies the historical KQ15 line is preserved, but the line digest is not separately compared.
- Frozen snapshot symlink flags are recorded, not separately gated; manifest path containment plus SHA-256/byte pins are the frozen enforcement. Live clean does gate a non-canonical or symlinked `--quality`.
- Row discovery uses Python `splitlines()`; exotic separators (form feed, U+2028) inside masked regions are outside scope and could shift indices only outside LF-structured documents.
- Git reads strip `GIT_*` and disable replace/lazy/prompt/optional locks but do not force `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`; `cat-file blob` reads raw object bytes.
- Execution status: this seat performed only `ast.parse` and standalone byte/digest calculations. No child process, gate, build, test, linter or historical gate was run here; L1 owns the post-integration `--selftest` and frozen reproduction receipts.
- Required separate human/code review remains: `.ufo/waves/round-12/fidelity.py:24-25,64-72,271-273,319`, `.ufo/waves/round-12/reproduce.py:80`, and the recorded `.ufo/waves/round-12/acceptance.json` receipts. Those are observations, not fresh executions.
- This gate supplies no quality-axis evidence. Any quality attribution must cite round-12 D4's corrected served-identity-crosswalk knowledge interpretation, not this gate machinery.

## Risks / blockers

No blocker. Residual risk is false confidence from the literal wording: the gate can be green while semantic/exit-precedence questions remain, which is why the limits and `human_review_required` are inside the JSON and not only in this report. No tool installs. No commits or pushes.
