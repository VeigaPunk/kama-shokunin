VERDICT: n/a — read-only inventory: four finding ids (exits 0-3), exit 4 is free for a distinct could-not-evaluate finding, and demoting `worktree_matches_head` breaks 0 of the 10 selftest assertions.

# Scope and method

Read-only static read of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/measure.py` (910 lines, sha256 `2399d64dcde477dd26f6f1092819b6392fc812dc5a64a949f8e075d6a0918fd6`) and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-13/frozen/expected.json`. The live file is byte-identical to `.ufo/waves/round-17/frozen/round-13_measure.py`; the frozen manifest pins the same digest (`.ufo/waves/round-17/frozen/manifest.json:9`). All line numbers below are for that exact byte string. No command from the module, no lane gate, and no port was used.

# 1. Every declared exit code and finding id

Single source of truth is `FINDINGS` at `measure.py:107-112`, repeated verbatim in the docstring exit table at `measure.py:54-55`.

| Exit | Finding id | Declared at | Actually emitted by |
|---|---|---|---|
| 0 | `clean` | `measure.py:108` `'clean': 0,`; docstring `measure.py:54` `"0 clean"` | `run_live` (`:457`); `run_frozen` (`:585` `finding, code = content_verdict(selected)`, returned at `:625`); `run_selftest` (`:851`); `--help` (argparse `SystemExit(0)`, docstring `:55-57` "`--help`, which is conventional argparse plaintext") |
| 1 | `documentation_mismatch` | `measure.py:109` `'documentation_mismatch': 1,`; docstring `:54` | `run_live` when any clean conjunct fails (`:448-457`); `run_frozen` on prefix/manifest/pinned-start/before-count failure (`:586`); `content_verdict` `:261` `return ('clean', 0) if ... else ('documentation_mismatch', 1)`; `run_selftest` when any case fails (`:851`) |
| 2 | `snapshot_tampered` | `measure.py:110` `'snapshot_tampered': 2,`; docstring `:55` | Only `run_frozen` digest/byte mismatch: `:553` `return finish(result, 'snapshot_tampered', ['digest_mismatch'])`. `run_live` can never return 2. |
| 3 | `probe_error` | `measure.py:111` `'probe_error': 3,`; docstring `:55` "`3 probe_error (unmeasured)`" | `main()`: `GateError` handler `:887,891`; catch-all `except Exception` `:900,904`. `Parser.error` raises `GateError` (`:148`), so usage errors are 3, not argparse's 2. |

Docstring quote: `measure.py:54-55` "Exit codes / stable findings: 0 clean; 1 documentation_mismatch; 2 snapshot_tampered; 3 probe_error (unmeasured)."

Two important emission facts:

- `finish()` is the only receipt finalizer: `measure.py:374` `result['verdict_exit'] = FINDINGS[finding]`. An id absent from `FINDINGS` raises `KeyError`, which `main()`'s catch-all turns into `probe_error`/3 — not a crash, but a silent downgrade.
- `load_manifest` rejects manifest finding values outside `FINDINGS` and rejects `probe_error`: `measure.py:479` `if entry['finding'] not in FINDINGS or entry['finding'] == 'probe_error':`.

## Text-checked exit classes that are not gate finding ids

`EXIT_MAP_LITERAL` (`measure.py:82`) and `EXPECTED_EXITS` (`:84-88`) make the gate *grade the wording* `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`. Those are the round-12/QUALITY vocabulary, not this module's ids: only `snapshot_tampered` is a `FINDINGS` key. `source_mismatch` and `source_unavailable` are checked as text (`contradiction_problems`, `:200-203`) and are never passed to `finish()`. A future repair must not assume `finish(result, 'source_unavailable')` works.

`expected.json` declares no exit integers at all. It contains only `schema`, `criterion`, `denominator`, `denominator_basis`, and per-arm `revision/path/snapshot/sha256/bytes/missing_assertions/finding/kq15_line_sha256`; the only finding values are `"finding": "documentation_mismatch"` (before) and `"finding": "clean"` (after). It therefore constrains only frozen-mode findings, not the live finding set.

# 2. Which code is free

Taken: 0, 1, 2, 3. **Exit 4 is the lowest free code** (5+ are also free); the module contains no numeric exit 4 anywhere — the only numeric literals reaching `sys.exit` are those in `FINDINGS` (`:107-112`) plus the selftest's `0 if failed == 0 else 1` (`:851`).

Qualifier worth carrying into the repair: 3 *is already* the module's could-not-evaluate class ("unmeasured"), so a new finding that merely means "could not evaluate" duplicates 3 semantically; the downstream spec (`make_spec.py:106`) nevertheless requires "a distinct declared exit". Exit 4 satisfies that, and `PROTOCOL.md:379-382` permits it: "`0` = `clean` and `1` = `failed` fleet-wide; every other code a gate exits (`2`, `3`, `64`, …) is declared". The lane registry row already anticipates undeclared codes reading as could-not-evaluate (`SKILL.md:430`), but the row lists only 0/1/2/3, so adding 4 requires a registry append — outside the `JjRound13Gate` write scope (its target is only `measure.py` + `expected.json`), so route it to L1/[INFERENCE].

Cross-gate note: round-16's measure.py already assigns 4 a different meaning — `SKILL.md:534` "4 frozen snapshot does not match its manifest". No collision inside round-13, but the two gates must be read per-registry, not lane-wide.

# 3. Which selftest assertions break if `worktree_matches_head` leaves `clean`

**None of the ten cases would fail.** The mutation is invisible to `--selftest`.

Mechanism, in three observed facts:

1. `worktree_matches_head` is computed and consumed only in `run_live`: `measure.py:397` `worktree_matches_head = final == head_quality`, the receipt field `:408`, the `checks` field `:432`, the observation `:446-447` `worktree_not_at_measured_revision`, and the `clean` conjunct `:455` `and worktree_matches_head`. `run_frozen` (`:508-625`) never reads it.
2. Every selftest child runs frozen mode: `measure.py:788-791` `child = [sys.executable, '-I', '-B', ..., '--manifest', str(manifest_path), '--quality', str(quality)]`. `run_selftest` never invokes `run_live`.
3. The per-case assertion is only four conjuncts: `measure.py:807-820` `parsed`, `observed['exit'] == case['expected_exit']`, `observed['finding'] == case['expected_finding']`, and `missing_ok`. Nothing asserts `checks.worktree_matches_head`, the `observations` list, `mode`, or any receipt field.

The ten cases (`measure.py:706-767`), all frozen mode:

| # | Case | Expected exit / finding / missing |
|---|---|---|
| 1 | `before_red` (`:706`) | 1 / `documentation_mismatch` / 2 |
| 2 | `after_green` (`:707`) | 0 / `clean` / 0 |
| 3 | `missing_exit_map_literal` (`:708`) | 1 / `documentation_mismatch` / 1 |
| 4 | `missing_capture_comparison_literal` (`:714`) | 1 / `documentation_mismatch` / 1 |
| 5 | `reintroduced_mistaken_wording` (`:720`) | 1 / `documentation_mismatch` / 0 |
| 6 | `reintroduced_kq15_comparison` (`:726`) | 1 / `documentation_mismatch` / 0 |
| 7 | `contradictory_comparison_roles` (`:736`) | 1 / `documentation_mismatch` / 0 |
| 8 | `conflicting_exit_class` (`:745`) | 1 / `documentation_mismatch` / 0 |
| 9 | `missing_kq16_row` (`:754`) | 1 / `documentation_mismatch` / 2 |
| 10 | `altered_pinned_snapshot` (`:763`) | 2 / `snapshot_tampered` / `None` (unchecked) |

Consequence: a mutant that deletes `and worktree_matches_head` (`:455`), or deletes both the `checks` entry and the observation while leaving listeners none the wiser, still scores 10/10 green. `after_green` remains 0/`clean` because frozen mode never compares against HEAD. The old `worktree_matches_head` receipt in `.ufo/waves/round-13/acceptance.json:448,499` is a historical observation, not re-read by any test.

What the repair must therefore add (from `make_spec.py:106-110`): live-mode cases proving divergent-but-clean → new finding/exit, committed-clean → `clean`/0, and content-failure → `documentation_mismatch`/1. Those are new assertions; none of the ten current ones change.

# 4. Constraints the new live cases must satisfy (grounded, not optional)

- **Git is hard-pinned to `LANE`.** `measure.py:278` `argv = ['git', ..., '-C', str(LANE)] + list(args)` and `:271` `'GIT_CEILING_DIRECTORIES': str(LANE.parent)`. A TemporaryDirectory repo passed via `--quality` is *not* the repository read; `LANE` is derived from `__file__` (`:71-72` `LANE = WAVE.parents[2]`). To sandbox live mode without touching the lane, copy the script into a synthetic lane layout `<tmp>/lane/.ufo/waves/round-13/measure.py` so `LANE` resolves to `<tmp>/lane`, or add an explicit repo-root option. [INFERENCE from the path derivation; the copy approach is the minimal no-flag route.]
- **Pinned start is compared to the module constant, not argv.** `measure.py:394` `before_is_pinned_start = oid == BEFORE_REVISION` (constant `941bb32c...`, `:80`). A fresh `git init` fixture cannot produce `clean`/0: passing `--before-revision <fixture-oid>` still fails `before_is_pinned_start`, hence `documentation_mismatch`/1. The sandbox must contain the literal commit `941bb32c3f591bc63cbf7579b2b6c552228307cd` (e.g., clone the lane read-only into /tmp) or the comparison must be parameterized. [INFERENCE]
- **Canonical path check binds the sandbox to its own `LANE`.** `measure.py:396` `canonical_quality = Path(quality_path).resolve() == DEFAULT_QUALITY.resolve()`; `DEFAULT_QUALITY = LANE/'corpus'/'QUALITY.md'` (`:75`). Running the lane's script with a temp `--quality` yields `canonical_quality=False` → 1. The synthetic-lane copy satisfies this automatically.
- **Live mode requires a resolvable HEAD and before commit.** `:382` `head = measured_head(commands)` (optional=False), `:384` `resolved_before`, `:385` `historical_quality`; failures raise `GateError` → 3. A sandbox with an unborn HEAD gives 3, not the new finding.
- **Adding the id to `FINDINGS` is mandatory.** Otherwise `finish()`'s `FINDINGS[finding]` (`:374`) raises and `main()` reports `probe_error`/3 (`:892-904`); the new finding would be indistinguishable from an internal fault. `selftest_manifest` needs no change: it hardcodes `before` finding `documentation_mismatch` (`:661`).
- **Ordering of the live verdict.** Today `clean` is a conjunction (`:448-456`). The spec requires divergence-but-otherwise-clean → new could-not-evaluate finding, while content failure stays `documentation_mismatch`/1. That means the content verdict must be evaluated before the worktree verdict, otherwise a divergent + content-broken file would be misreported as could-not-evaluate.

# Limitations

- Static reading only. The "0 of 10 assertions break" result is [INFERENCE] from the control flow (`--manifest` in every child argv; `worktree_matches_head` referenced only inside `run_live`); I did not execute `--selftest`, which belongs to the downstream executor/L1.
- I did not audit `assess()` internals (`:149-245`) beyond what the exit/finding question needs; the `missing_assertions` values are taken from the frozen manifest and the selftest table.
- `expected.json` is a two-snapshot frozen manifest, not an exit registry; it cannot arbitrate the live exit map.
- The registry-declaration gap (`SKILL.md:430` lists only 0/1/2/3) is an observed conformance duty for whoever lands exit 4; whether L1 folds it into an existing item was not decided here.
- No lane gate, measurement, endpoint, or port was touched; no `jj`/git write was run.

# Installs

None.
