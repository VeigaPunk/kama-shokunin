# Round 13 — ReviewNoHarm (axis calibration, six-axis invariants, criterion precision)

Scope: read-only review of the planned KQ16 supersession of KQ15's two propositions, and of the six SCORECARD axes. Only this file was written. No gate, selftest, reproduce script, mutant, build, or test was executed. `fidelity.py` was not run. Git commands were read-only (`status`, `log`, `help show` text, `config --local --list`, `check-attr`). No tool was installed or updated. Status at review time: `corpus/QUALITY.md` is unchanged (49 lines, same bytes as HEAD `941bb32`); no KQ16 row exists yet. Pending edits are not reviewed here; re-read when notified.

## Verdict

No axis harm and no score inflation are visible in the current tree. The planned KQ16 wording is directionally correct for the two routed propositions. Two precision points need attention before the claim "criterion discrepancies 2 -> 0" is stated: one residual KQ15 imprecision sits outside the fixed denominator, and the `git show` capture half is documented, not receipt-observed.

## Findings by severity

**F1 — medium. A third KQ15 imprecision is outside the denominator and must not be silently absorbed or hidden.**
- KQ15 (`corpus/QUALITY.md:49`) says: "An overridden snapshot without its manifest may only expose a mismatch, never authorize a pass."
- Code: a byte-matching unpinned snapshot returns finding `unpinned`, exit 2 (`.ufo/waves/round-12/fidelity.py:238-241` emits it; `:70` priority; `:319` maps it to 2). An unpinned byte mismatch returns `source_mismatch`, exit 1 (`:304-306`, `:319`).
- The gate's own docstring says so (`fidelity.py:19-22`). `SKILL.md:400-401` says so: "a matching unpinned snapshot is `unpinned` (exit 2, could-not-evaluate)".
- So "may only expose a mismatch" is wrong for the matching case. "Never authorize a pass" is correct.
- Action: either route it as a third KQ15 item for the next round, or get explicit approval to add it. Do not fold it into KQ16 silently. Any claim should read "fixed two-proposition denominator 2 -> 0; a third KQ15 imprecision is known and open".

**F2 — low. The `capture: git show` half is documented, not receipt-observed.**
- Gate source retrieval is `git rev-parse --verify <rev>:<path>` for the OID (`fidelity.py:261-268`) and `git cat-file blob <rev>:<path>` for bytes (`:271-279`). `git show` does not appear anywhere in `fidelity.py`.
- The `git show` claim for the frozen copy comes from `SKILL.md:396` ("captured byte-exactly via `git show`") and `corpus/lessons/round-12.md:14`. No receipt records the command that wrote `frozen/corpus/SOURCES.md`.
- Receipts do show byte identity: the after-record snapshot SHA-256 equals the cat-file source SHA-256, `9dc40d25…` (`.ufo/waves/round-12/acceptance.json`, record `after` and `source`).
- Local checks: `git help show` says textconv is not enabled by default for `git show`; no `.gitattributes` exists; `git check-attr -a corpus/SOURCES.md` returned nothing; `git config --local --list` shows no textconv or filter entries. Global and system config were not inspected.
- [INFERENCE] `git show` on this plain blob yields the same bytes as `cat-file blob`. That is supported by the receipt's byte identity and S032 documentation, not by a fresh `git show` run.
- Recommendation: keep the literal `capture: git show; comparison: git cat-file blob`, and scope it to snapshot creation. Note that the gate reads the OID via `rev-parse --verify` and the bytes via `cat-file blob`.

**F3 — low. KQ16 boundary and probe scoping.**
- The old phrase "distinct nonzero exits" remains in `QUALITY.md:49` because the file is append-only. Any mutation or documentation check that searches the whole file will fail on historical bytes. The check must be scoped to the KQ16 row or section.
- The round-12 section heading says "author-appended; no outside review yet". The KQ16 heading should say the same, since author agreement is not an outside spot-check (`QUALITY.md` "Review boundary").
- The exit-map literal `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` matches `fidelity.py:319`. Stable finding IDs are distinct; the could-not-evaluate classes share exit 2. Adding "all could-not-evaluate classes exit 2 (`manifest_invalid`, `unpinned`, `snapshot_unavailable`, `internal_error`)" is accurate per `:319` and `SKILL.md:396`, and does not widen scope.

**F4 — low. Citation label drift in KQ15 (not one of the two propositions).**
- KQ15's motivating column cites `lessons/round-12.md` Mistakes "(frozen-snapshot correspondence)". The Mistakes table row is classed `evidence-fidelity` (`corpus/lessons/round-12.md:63`). The reference is correct; the label is paraphrase. Record only; no change required.

**F5 — info. Other surfaces need no edit for KQ16.**
- `SKILL.md:381-382` already applies to "every subsequently appended criterion", so a QUALITY.md append is sufficient. No SKILL, SCORECARD, or code change is implied. This keeps "other surfaces unchanged" true.

## Six-axis invariants (SCORECARD top table and erratum)

| Axis | Current value | Evidence | Round 13 effect |
|---|---|---|---|
| operability | 8 | `SCORECARD.md:19`; erratum `:211-213`; round-12 `:300` | none (KQ16 is a criterion row only) |
| freshness | 8 | erratum `:211`; round-12 `:300` | none |
| depth | 7 | `:21`; `:243`; `:300` | none |
| coverage | 9 | erratum `:212`; round-12 `:300` | none |
| calibration | 7 (7 -> 7, delta 0) | `:23`; `:240`; round-12 `:299-300` | claim is textual precision only; no numeric move |
| adjacency | 7 | `:24`; `:243`; `:300` | none |

No axis value can change from a `QUALITY.md` append. The round-13 SCORECARD entry does not exist yet and must keep calibration at 7 -> 7. Mission-level axis authority is outside this review.

## Residual risk and verification gaps

- KQ16 is unlanded; this review covers the planned wording in `spec.json` and `dispatch.json` only.
- `fidelity.py` behavior was read statically, not executed. Exit mappings are read from code and the recorded receipts, not from a fresh run.
- The frozen snapshot creation command is not receipt-observed (F2).
- F1 remains open unless the owner approves its inclusion.
- The local git version (2.55.0) differs from the S032 manual revision cited (2.56.0). Not relevant to KQ15/KQ16 wording; noted only.

Tools installed/updated: none.
