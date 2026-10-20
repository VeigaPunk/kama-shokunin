# ReviewRegistry — round-12 Gate standard and registry review

Seat: `KamaR12.ReviewRegistry` (reviewer, leaf, author advisor — not independent closure).
Scope: static review of the canonical Gate standard, the kama registry in `SKILL.md`, and the
proposed round-12 fidelity row. No sibling gate was executed; no verification was run; no file
outside this report was written. Tools installed or updated: none.

## Axes

A1 schema completeness against the canonical row fields · A2 verdict-map conformance ·
A3 self-test and pin completeness · A4 write-scope accuracy · A5 closure-evidence reachability.

## Sources read

- Canonical contract (read-only, out-of-tree per the assignment): `~/Projects/kimi-shokunin/skills/shokunin/protocol/PROTOCOL.md:388-437` (§Gate standard: Verdict 393-397, Self-test 398-402, Two evidences 403-410, Registry 411-419, Scope 420-424, Closure consequence 425-430, Delivery 431-435); `PROTOCOL-APPENDIX.md` rows "Gate standard" (l.35-36, 46) and "Registry home" (l.51).
- kama registry: `SKILL.md:11-14` (vocabulary and exit codes), `:294-306` (round-5 gate/probe table), `:369-374` (round-11 table). The file ends at line 374; **no round-12 row exists yet.**
- Round-12 contract: `spec.json:9` (Fidelity: `--manifest` optional, "NO manifest means no integrity pin"), `spec.json:24` (SkillRegistry: "Append gate registry for round12 fidelity … with command, 0clean/1failed/2could-not-evaluate, --selftest, pinned frozen expected path, temporary writes selftest only, kama owner"), and the shared-interface CLI contract (exit map: `source_mismatch` 1, `snapshot_tampered` 2, `source_unavailable` 2, `clean` 0).
- Round-11 precedent: `.ufo/waves/round-11/measure.py:1-35` (scope statement, exit-code block); closure `corpus/lessons/round-11-verifier-spotcheck.md:17, 101-110, 180-188`.

## Findings — proposed round-12 row (blocking before the row is appended)

**F1 (high, A1/A3) — `--manifest` has no spelling for the unpinned observation.** The CLI default is `frozen/expected.json`, and an omitted `--manifest` therefore applies that default. The runner is specified to call the old round-11 snapshot "with no manifest" (`spec.json`, Runner item). Under the default rule, that call reads `snapshot_tampered` (2), not the intended `source_mismatch` (1). The row cannot express a reproducible old-observation command. **Fix:** name an explicit opt-out spelling (for example `--manifest none`) in the CLI and the row; state that the default applies only when the flag is omitted, and that the opt-out is not a pinned run.

**F2 (high, A2) — `unpinned (legacy)` must be visible in output and in the row.** Canonical: "a baseline without digests is reported `unpinned (legacy)`" (`PROTOCOL.md:409-410`). A no-manifest run that exits 0 or 1 would otherwise read as a pinned verdict. **Fix:** the CLI emits an explicit `integrity: unpinned (legacy)` field, and the row states that a no-manifest `clean` is not a pinned clean.

**F3 (high, A2) — Finding precedence is unspecified.** Canonical: tamper is "not a compared verdict" (`PROTOCOL.md:408-410`). The spec lists `source_mismatch` (1) and `snapshot_tampered` (2) without an order. When a snapshot is edited without a matching manifest update, both findings can hold. **Fix:** the row states `snapshot_tampered` takes precedence (exit 2), and the CLI tests tamper before comparison. Without this, the same input can exit 1 or 2 depending on implementation order.

**F4 (high, A3) — The pin is not independent of the artifacts it pins.** The manifest pins "snapshot SHA-256, source commit/path" (spec). A coherent edit of snapshot and manifest passes the digest check. If the manifest's commit is also repointed to a commit containing the edited bytes, the verdict is `clean`. The canonical rule is that expected values must be "independent of the recomputation" (`PROTOCOL.md:400`). **Fix:** the CLI holds source commit `2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` and path `corpus/SOURCES.md` as code constants; a manifest that disagrees with them is a tamper finding (2). The row records the same commit and path as lane-owned values, so an edit to the manifest's commit is visible from the registry.

**F5 (high, A1) — `kind` is missing.** Canonical row fields: name, `gate|probe`, entry command, verdict map, self-test command and spelling, pinned-value path, write scope, owner (`PROTOCOL.md:414-416`). The proposal provides command, verdict words, `--selftest`, pinned path, write scope and owner. It omits `name` and `kind`. The tool can fail (exit 1), so it is a **gate** by definition (`PROTOCOL.md:391-392`).

**F6 (medium, A2) — An uncaught Python exception exits 1.** Under the verdict clause, `1` is `failed`, so an unhandled crash in the CLI would be reported as a failed verdict rather than could-not-evaluate. **Fix:** the CLI catches all exceptions at the top level and exits 2; the row states this mapping.

**F7 (medium, A3) — Self-test expectations are not located.** Canonical: the self-test asserts "both the exit code and a stable expected finding-id, with the expected values committed in the owning repo" (`PROTOCOL.md:398-401`). The proposal says `--selftest` only. **Fix:** the row lists the four cases with exit code and finding ID (clean 0, `source_mismatch` 1, `snapshot_tampered` 2, `source_unavailable` 2), the file that commits those expected values, and the requirement that the selftest invokes the actual CLI as a child process.

**F8 (medium, A5) — Closure evidence paths are missing.** Closure verifies "self-test tally, frozen-run verdict, the revision measured" as committed evidence (`PROTOCOL.md:427-430`), and a gate with a mutable input also needs a frozen run with a committed expected verdict (`PROTOCOL.md:403-405`). The proposal names neither the frozen-run command nor the output file. **Fix:** the row names the frozen-run command, `frozen/expected.json` as the expected verdict, the committed selftest-tally path, and the output field that carries the measured revision (git HEAD and source commit).

**F9 (medium, A4) — Write scope is incomplete.** "temporary writes selftest only" omits three facts: (a) the CLI reads git objects through read-only `git show`, with no checkout or index write; (b) `--repo` redirects the git root, which is an attack surface, and a non-default `--repo` is not the fleet verdict; (c) the CLI never writes `frozen/`, the manifest, or the snapshot. Canonical scope is "read-only over surfaces it does not own" (`PROTOCOL.md:420-422`).

**F10 (low, A1) — Owner is not a row field.** The owner statement is a header sentence (`SKILL.md:296`) and the proposal says "kama owner" in prose. Canonical lists owner as a row field (`PROTOCOL.md:416`). The new row carries it explicitly.

## Findings — existing registry rows (conformance defects; route to kama owner; do not rewrite prior rows)

**C1 (high, A2) — Exit `1` is mapped to something other than `failed`.** Canonical fixes `1` as `failed` fleet-wide (`PROTOCOL.md:393-394`). kama rows use it otherwise: `SKILL.md:13-14` ("1 probe error"), `:303` ("1 could-not-evaluate/probe error"), `:304` and `:305` ("1 probe error"), `:306` ("1 could-not-evaluate/probe or persistence error"). Changing `tools/kama-probe.sh` is out of round-12 scope (`tools/` is off-limits). **Route** as a conformance defect with a dated correction note appended in the next kama round; do not edit the prior rows in place.

**C2 (medium, A1) — Kind mislabel.** `SKILL.md:374` registers `probe: measure.py crosswalk`, yet its exit `1` means "absent/incomplete metadata". A tool that can fail is a gate (`PROTOCOL.md:391-392`). Route the reclassification to kama.

**C3 (medium, A3/A5) — Crosswalk gate has no frozen run.** Row `:374` runs against the live tree (`--root .`). Canonical requires a frozen run with a committed expected verdict when the verdict depends on a mutable artifact (`PROTOCOL.md:403-405`). The row names none. Route as a conformance defect.

**C4 (low, A2) — Scope statement omits the D1 limit.** Row `:373` ("Legacy provenance integrity", gate, exit 0 clean) does not state that a clean run proves digest integrity and prefix preservation only, not correspondence with the source commit. The closure documents this gap as D1 (`round-11-verifier-spotcheck.md:101-110`). Add a disclaimer in the next kama round, not in place.

**C5 (low) — Legacy rows fold pins, spelling and owner into one column.** `SKILL.md:301-306` and `:371-374` combine self-test spelling with pinned values. This does not match the canonical field set (`PROTOCOL.md:414-416`). Not blocking. The round-12 row uses the full field set.

## Field checklist for the round-12 row

| Canonical field | Proposed (spec) | Status |
|---|---|---|
| name | not specified | **missing** |
| gate \| probe | not specified | **missing** → `gate` |
| entry command | `fidelity.py --snapshot …` | partial: default-manifest semantics and opt-out unstated (F1) |
| verdict map | 0 clean; 1 failed; 2 could-not-evaluate | partial: 2 covers tamper, unavailable, usage and crash; precedence unstated (F3, F6) |
| self-test command and spelling | `--selftest` | partial: expected finding IDs and location missing (F7) |
| pinned-value path | `frozen/expected.json` | partial: snapshot path and source anchor missing (F4) |
| write scope | temporary writes, selftest only | partial: read-only `git show`, `--repo`, no `frozen/` writes (F9) |
| owner | kama | ok, explicit per row (F10) |
| closure evidence paths | not specified | **missing** (F8) |
| unpinned status | not specified | **missing** (F2) |

## Checks for L1 (named, not run)

1. Confirm the new row is appended and rows `SKILL.md:301-306` and `:369-374` are byte-unchanged against the before revision.
2. Resolve the before-revision discrepancy: `claims.json` names `79fa257…`, while the round-11 closure names `fe57cc8…` as the round-after HEAD (`round-11-verifier-spotcheck.md:17`). Confirm which is the round-12 before.
3. Confirm `fidelity.py`, `reproduce.py`, `frozen/**` and `frozen/expected.json` are tracked, not untracked. Earlier session evidence on 2026-10-15 showed `?? .ufo/` untracked; this review did not verify current tracking.
4. Run `fidelity.py --selftest` and check exits and finding IDs against F7.
5. Run the no-manifest spelling and confirm `unpinned (legacy)` appears in output (F1, F2).
6. Run a coherent snapshot-and-manifest mutation and confirm exit 1, not 0 (F4).
7. Run a manifest-only commit repoint and confirm it is not `clean` (F4).
8. Run a forced uncaught exception and confirm exit 2 (F6).
9. Confirm the precedence case: edited snapshot with unchanged manifest gives exit 2 (F3).

## Residual risk and gaps

- The fidelity CLI does not yet exist. Every finding above is specification-level. Implementation-level claims (exit codes, finding IDs) are unverified.
- The canonical PROTOCOL was read from `~/Projects/kimi-shokunin` as the assignment directed. That path is outside the kama contract root; the access was read-only.
- I did not confirm whether `tools/test-snapshot.sh` asserts stable finding IDs (C-row `:303`, `:306`); the row text does not say.
