# GateRegistry — kama round-11 advisory: registry row fields for measure.py

Status: advisory, non-author, read-only. No edits to SKILL.md, measure.py, the baseline, the corpus or any other repo file. No checks, selftests, hashes, git commands or network/endpoint access were run. No public URL was opened; no source quotes are cited.
Installs/updates: none performed; no install record exists for this seat.

## Scope read

- `kama-shokunin/SKILL.md:294-307` — last gate section, `## Local gate/probe registry`, ends before `## Cited sources` at `:308`.
- `kama-shokunin/.ufo/waves/round-11/measure.py` — 584 lines, read in full (docstring `:1-78`, helpers `:91-212`, `check_provenance` `:215-324`, `check_crosswalk` `:327-374`, `run_selftest` `:377-549`, `main` `:552-584`).
- Context only: `PROTOCOL.md:377-411` (registry schema), `kama-shokunin/.ufo/waves/round-11/legacy-baseline.json` (read, not hashed), `verification-spec.json`, advice files `Simplify.md`, `ReviewContract.md`, `Planner.md`, `MutationPlan.md`.

## 1. Current registry (`SKILL.md:294-306`)

Header (`:301`): `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`. Owner is stated once in prose (`:296`): "Owner for every row: kama."

Rows present: `Registered reconciliation` (`kama-probe.sh check`), `Consumer provenance`, `Listener census`, `Invocation history` (`kama-probe.sh snapshot`). **No row for `measure.py`.** Its modes `provenance` and `crosswalk` and its `--selftest` are absent from the section, and the section's only lane-local pin statement (`:296-299`) names only `registry/endpoint-consumers.tsv` and `tools/test-snapshot.sh`.

## 2. Exact row fields for measure.py (proposed; 7 requested fields)

Two rows are proposed, because `crosswalk` mode is a separate exit surface with no pinned baseline.

### Row A — provenance

| Field | Value | Evidence |
|---|---|---|
| name | `Round-11 provenance supplement (measure.py provenance)` | `measure.py:2-3`, `:30` |
| kind | `gate` (it can exit 1; protocol: "a tool that cannot fail is a probe", `PROTOCOL.md:378-379`) | `measure.py:29` |
| command | `python3 .ufo/waves/round-11/measure.py provenance` — optional `--root DIR`, `--baseline PATH` (an explicit relative `--baseline` resolves against cwd) | `measure.py:17`, `:21-25`, `:575` |
| exit mapping | `0` clean (`findings` empty) · `1` failed (any finding: `missing-file`, `prefix-mutation`, `missing-field`, `duplicate-field`, `missing-supplement-heading`, `verified-at-live-claim`) · `2` could-not-evaluate (`invalid-root` `:570-573`; `invalid-baseline` `:224,:228,:233,:242,:246`; `snapshot_tampered` `:236-239`; `invalid-input` `:267`; argparse usage errors, Python default `2`). Uncaught Python exceptions would exit `1` and read as failed; none observed in code review, none exercised. | `measure.py:29`, `:570-573`, `:224-267` |
| self-test | `python3 .ufo/waves/round-11/measure.py --selftest` — 13 isolated cases in one `tempfile.TemporaryDirectory` (`:390`), asserting exit code and finding names (`:418-420`). Expected stdout last line `selftest: 13/13 passed`; exit `0` if all pass, `1` otherwise, `2` on setup `OSError` (`:539-541`, `:549`). Case count verified by reading `:433-537`, not by running. | `measure.py:19`, `:376-378`, `:433-537`, `:548-549` |
| pinned baseline | Pinned-value path: `.ufo/waves/round-11/legacy-baseline.json` (9 entries; each records `sha256`, `bytes`, `missing` = `source`, `verified-at`, `recheck`; 27 missing fields in total — read at `legacy-baseline.json:2-83`). Pinned digest lives in code: `BASELINE_SHA256 = 5d704e90a4ad758f375c5d1312dad7c972b7d1d1a105a7dba3250282f7c38af1` (`measure.py:99`). Informational only: `BASELINE_REVISION = 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad` (`measure.py:100`). **The on-disk file's current sha256 was not computed in this seat** (checks not run); the only prior observation is a one-file match in `Planner.md:12`, which does not cover the baseline file. | `measure.py:94-100`, `:62-68` |
| write scope | None. Reads `--root` files and the baseline; writes only to stdout. Selftest writes only inside a temp directory removed on exit. | `measure.py:213-272`, `:390`, `:572-580` |
| owner | `kama` (per `SKILL.md:296`, "Owner for every row: kama.") | `SKILL.md:296` |

### Row B — crosswalk

| Field | Value | Evidence |
|---|---|---|
| name | `Round-11 served-identity crosswalk entry (measure.py crosswalk)` | `measure.py:72-77` |
| kind | `gate` by the protocol definition (it exits 1 on findings). Its own docstring calls it a "count" (`:6-11`, `:72-77`), which invites a probe reading; the parent must choose one explicitly (see F9). | `measure.py:342`, `:354`, `:361`, `:365`, `:369` |
| command | `python3 .ufo/waves/round-11/measure.py crosswalk` (no `--baseline`; uses the fixed entry path) | `measure.py:18`, `:109`, `:569-580` |
| exit mapping | `0` clean (entry present; trio exactly once at column zero; `S001 S010 S011 S012 S016` each present; markdown table present; no live `verified-at` claim) · `1` failed (`missing-file`, `missing-field`, `duplicate-field`, `missing-source-id`, `missing-table`, `verified-at-live-claim`) · `2` could-not-evaluate (`invalid-entry` on read `OSError`, `:343-344`; invalid root `:570-573`). | `measure.py:29`, `:337-344`, `:362-374` |
| self-test | Same flag `python3 .ufo/waves/round-11/measure.py --selftest`; crosswalk cases are 11–13 (`:508-538`). The selftest is shared, so one run covers both rows; the expected summary is the same 13/13 line. | `measure.py:508-538` |
| pinned baseline | None. Pinned expected values are code constants: `CROSSWALK_ENTRY_REL` (`:110`), `REQUIRED_SOURCE_IDS` (`:111`). No frozen snapshot or expected-verdict file exists for this mode; the entry is a mutable tree file. | `measure.py:110-111`, `:336` |
| write scope | None (read-only; stdout only). | `measure.py:335-374`, `:579` |
| owner | `kama` | `SKILL.md:296` |

Recommended table text (to place after `SKILL.md:306`, before the blank line and `## Cited sources` at `:308`), in the lane's existing 5-column shape:

- `measure provenance` | gate: `python3 .ufo/waves/round-11/measure.py provenance` | 0 clean; 1 failed (finding); 2 could-not-evaluate (invalid root/baseline, `snapshot_tampered`) | `python3 .ufo/waves/round-11/measure.py --selftest` (13 cases, `selftest: 13/13 passed`); pinned baseline `.ufo/waves/round-11/legacy-baseline.json`, digest `5d704e90…8af1` in `measure.py:99` | None (stdout only); owner kama
- `measure crosswalk` | gate: `python3 .ufo/waves/round-11/measure.py crosswalk` | 0 clean; 1 failed (finding); 2 could-not-evaluate (unreadable entry) | same selftest (crosswalk cases 11–13); no pinned snapshot, required ids in `measure.py:111` | None; owner kama

## 3. Findings (ordered by weight)

**F1 — blocker for registry conformance. Missing row.** `SKILL.md:294-306` has no `measure.py` row. `PROTOCOL.md:398-402` makes the lane's own `SKILL.md` the registry home, and every gate the lane runs needs a row. Smallest repair: insert the two rows above after `SKILL.md:306`.

**F2 — decision blocker: measure.py may be deleted.** `advice/Simplify.md:19-22` recommends deleting `measure.py` ("delete"; crosswalk called "tautological"). `advice/ReviewContract.md:45,67` (K1) says the file must exist and that its checks are unimplemented. The file now exists (584 lines). The parent must decide before the row lands. If deleted, no row is added, and any mention of the script in `SKILL.md` must also go (none today). Smallest repair: decide, then either add Rows A/B or add nothing.

**F3 — schema shape: the 5-column table does not carry the protocol's 8 fields.** `SKILL.md:301` columns are `Name | Kind/entry command | Exit map | Self-test/pinned values | Write scope`. `PROTOCOL.md:401-403` requires name, `gate|probe`, entry command, verdict map (code → class), self-test command and spelling, pinned-value path, write scope, owner. Owner is prose only (`SKILL.md:296`), and the pinned path is merged into the self-test column (`:303`, `:306`). Smallest repair: keep the 5-column layout for measure rows, as proposed above, and state the owner in each row or keep prose; no column-count change required by this seat.

**F4 — cross-lane exit-code conflict (existing rows).** `SKILL.md:303` and `:306` map `kama-probe.sh` as `0 clean; 2 failed/drift; 1 could-not-evaluate/probe error`. `PROTOCOL.md:380-382` pins `0 = clean` and `1 = failed` fleet-wide, with other codes declared and mapped. The kama probe's `1` is "could-not-evaluate", so it conflicts with the fleet pin. `measure.py:29` uses `1 = failed`, `2 = could-not-evaluate`, which is protocol-compatible. The two rows in one section therefore use opposite meanings for `1` and `2`. Smallest repair (owner kama, not this wave): remap the `kama-probe.sh` rows to the fleet verdict map, or declare the mapping explicitly in each row. Route to owner.

**F5 — entry path is round-scoped and location-fragile.** The command path `.ufo/waves/round-11/` is a wave directory, and `measure.py:92` computes `LANE_ROOT = Path(__file__).resolve().parents[3]`. Moving the script breaks root resolution and the default baseline path (`:93`). Smallest repair: if the script is kept, the registry row must name the exact path; relocating it to `tools/` is an implementation change, out of scope here.

**F6 — no committed run for the "two evidences" clause.** `PROTOCOL.md:390-397` requires a gate whose verdict depends on mutable artifacts to ship a run over a committed input snapshot with its committed expected verdict. `measure.py provenance` depends on the mutable legacy files. `frozen/before/corpus/knowledge/` holds 9 files, but there is no expected-verdict file, and `measure.py:575` resolves the default baseline under `--root`, so a frozen run needs an explicit `--baseline` (otherwise exit `2` `invalid-baseline`). Smallest repair: either commit one expected verdict for `--root .ufo/waves/round-11/frozen/before --baseline .ufo/waves/round-11/legacy-baseline.json` with its expected exit and finding counts, or write "no committed snapshot run; unpinned" in the row. The frozen copies' bytes against the baseline were not compared in this seat.

**F7 — date-dependent verdict.** `measure.py:114-115` and `:125-131` make the `verified-at-live-claim` guard depend on the UTC run date (`_utc_run_date`). The static phrases "live revalidated today/live revalidation today" match on any date; the dated form matches only on the matching date. The selftest also uses today's date (`:379`). Smallest repair: note "verdict depends on UTC run date for dated live-claim wording" in the row's exit mapping.

**F8 — pinned bytes are in an untracked directory (reported, not re-checked here).** `ReviewContract.md:48` (K4) reports `git status` showing `?? .ufo/waves/` on 2026-10-20. I did not run git. If accurate, the baseline's pin and the `lane commit 2f7303c…` note (`measure.py:62-63`) are not backed by committed bytes. Smallest repair: commit the wave directory or record the digest in a tracked file; route to owner.

**F9 — crosswalk kind is ambiguous.** `measure.py:6-11` and `:72-77` call crosswalk an "existence/provenance count" with "no wording judgment", yet `:342`, `:354`, `:361`, `:365`, `:369` make it exit `1` on findings. Under `PROTOCOL.md:378-379` a tool that can fail is a gate. Smallest repair: pick `gate` explicitly in the row and state the semantic limit in its write-scope/limits text, as in Row B.

**F10 — low: uncaught exception exit code.** `main` (`measure.py:552-584`) has no broad handler. An unexpected Python exception exits `1` and would read as `failed` under the fleet map. None observed; none exercised. Smallest repair: none required unless the parent wants the `2` mapping for internal errors.

## 4. What is already correct (grounded in the read)

- Baseline shape matches the contract: 9 entries, 3 missing fields each, 27 total (`legacy-baseline.json:2-83`).
- Pinned-digest order is fail-closed: JSON parse → non-empty → digest → entry schema, before any file is measured (`measure.py:62-68`, `:221-248`).
- Exit codes in the docstring (`:29`) match the returns: findings → `0 if ok else 1`; invalid root → `2`; baseline and input errors → `2`; selftest → `0`/`1`/`2`.
- Read-only design: the provenance and crosswalk paths call only `read_bytes`/`read_text` (`:222`, `:260`, `:336`); the selftest writes only under `tempfile.TemporaryDirectory` (`:390`).
- Selftest asserts both exit codes and finding names (`:418-420`), which matches `PROTOCOL.md:385-389`.
- Protocol-compatible verdict vocabulary for measure.py rows: `0 clean`, `1 failed`, `2 could-not-evaluate`.

## 5. Out of scope / not observed

- No measurement, selftest, digest computation, git command, or endpoint access was run in this seat.
- Current baseline sha256 vs `BASELINE_SHA256`: not observed.
- Frozen-copy bytes vs baseline: not observed.
- Whether `--root frozen/before` yields any specific verdict: not observed.
- Round-11 wave outputs beyond the files listed above were not read.

## 6. Checks the parent should run (not run here)

1. `python3 .ufo/waves/round-11/measure.py --selftest` — expect `selftest: 13/13 passed`, exit 0.
2. `sha256sum .ufo/waves/round-11/legacy-baseline.json` — expect `5d704e90a4ad758f375c5d1312dad7c972b7d1d1a105a7dba3250282f7c38af1`.
3. `python3 .ufo/waves/round-11/measure.py provenance` and `... crosswalk` — record exit codes and counts; the verdict is date-dependent (F7).
4. After the row lands, re-read `SKILL.md:294-310` to confirm placement before `## Cited sources`.
