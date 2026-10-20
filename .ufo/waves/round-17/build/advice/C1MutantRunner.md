VERDICT: confirm — .ufo/waves/round-17/c1/mutants.py delivered: 10 intentional single-site mutants located by exact source strings, pair/full detectors, 2x2 grid JSON, pinned matrix digest; all 10 sites locate on the landed check.py and M6/M7 are n/a on the frozen copy.

## Deliverable

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/c1/mutants.py` (new, 1341 lines, mode 0755)

- sha256: `498d1f7fa7f248d7c794db95ac6208a59c13297305226774e6aa4dc6ff88ac1e`
- Only lane write besides this report. No other file created or edited in the lane.
- CLI: `--check PATH [--detector pair|full|both] --out PATH.json`, `--grid --out PATH.json`, `--check PATH --dry-run`, `--selftest`, `--keep-scratch`.
- Exits (L1 directive 6): `0` run completed (counts in JSON) or selftest passed; `2` own fault/refusal (missing/unreadable/non-compiling check, matrix pin mismatch, bad `--out`, failing selftest, invalid baseline cell).

## Mutant set as landed

All mutants are single-site edits; matching is exact source strings or bracket-aware patterns, never line numbers (`mutants.py:453` `MUTANTS = [`). Each spec is an ordered candidate chain; the first unique match wins. No match → `site_found:false`, `status:"site_missing"`, `killed:null` (never counted survived). Non-compiling result → `invalid_mutation`.

| id | name | site on landed check.py | edit |
| --- | --- | --- | --- |
| M0 | ignore-verdict | `check.py:467` `record["verdict"] == expected["verdict"]` | first conjunct neutralized to `True` (deleting it would dangle `and`) |
| M1 | ignore-reason | `check.py:468` `and record["reason"] == expected["reason"]` | line deleted |
| M2 | ignore-exit | `check.py:469` `and record["probe_exit"] == expected["exit"]` | line deleted |
| M3 | ignore-drift | `check.py:472` `and record["drift"] == (record["verdict"] != "MODEL_OK")` | line deleted |
| M4 | casefold-verdict | `check.py:467` | both sides `.casefold()` |
| M5 | timeout-pass | `check.py:443` `record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"` | insert `record["passed"] = True` after it |
| M6 | ignore-served_model | `check.py:473` `and record["served_model_ok"]` | conjunct → `True` |
| M7 | ignore-route-match | `check.py:474` `and record["route_ok"] is not False` | conjunct → `True` |
| M8 | malformed-output-passes | `check.py:455` `record["error"] = (f"malformed probe output: {why_bad}; "` | insert `record["passed"] = True` before its `return record` |
| M9 | reject-all | `check.py:466` `record["passed"] = (` | becomes `record["passed"] = False and (` — F0 must kill it |

M0–M5 reproduce the round-16 MutateHarness.md semantics; M0 and M6–M9 are the `KamaR17` parent additions. Measured against the frozen bytes, only M6 and M7 are `site_missing` (n/a): the frozen copy has no served_model/route invariants (its `passed` expression, `frozen check.py:340`-`347`, grades verdict/reason/exit/drift only). **M8 is applicable on the frozen copy too** — it already turns unparseable probe output into `record["error"]` (`frozen check.py:329`-`336`), so the malformed-passes edit has a real site there. L1's "M6–M8 are n/a on frozen" holds for M6/M7 only; the runner reports what it measures (`--dry-run` totals: 8 found, 2 missing).

## Detectors and output

- `pair`: each mutant is staged into `/tmp/kama-r17-c1mutants-*/<cell>/<id>/check.py` with the nine matrix `*.json`; runs the before probe and `tools/kama-probe.sh`; compares exit plus per-row `(name, passed, verdict, reason, probe_exit, drift, served_model, served_model_ok, route_ok, error, requests)` against the unmutated baseline in the same cell. `requests` is compared as a unique `(method, path)` set (`mutants.py:123` `norm_field`) so retry counts cannot cause false kills; round-16 compared six fields for the same reason.
- Before-probe selection (`mutants.py:700`): round-17 frozen `tools_kama-probe.sh` when its sha256 differs from current, else the round-16 `kama-probe-before.sh`, reproducing the reference 55/17 vs 72/0 pair. Here frozen r17 == current (`36b64978…`), so the r16 probe (`93ee4302…`) is selected and recorded as `baseline.r16_reference`.
- `full`: pair plus `tests/probe-verdicts/fault-controls.py --check <staged copy> --json`; killed when `accepted` differs from the unmutated baseline — a rise is tagged `full:accepted_rose`, a drop `full:accepted_changed`, both per L1's "any observable difference" rule. Controls' own fault (exit 2/unparseable) is tagged `full:controls_fault`; if the baseline controls are unusable the cell says so and falls back to pair.
- 2x2 grid: every JSON has `cells[]`, one per (check, detector). `--detector both` emits two cells for one check; `--grid` emits frozen+current x pair+full. Per mutant evidence carries `killed_by` (`pair:before`, `pair:current`, `full:accepted_rose|changed`, `full:controls_fault`) and `first_failing` (row/field or accepted fault ids) as L1 directed.
- Totals per cell: `applicable` (site_found), `killed`, `survived`, `site_missing`, `invalid`, `inconclusive`. `applicable = killed + survived`; M6/M7 on the frozen cell never enter `survived` (M8 does, because it has a frozen site).

## Guards

- Matrix pin (`mutants.py:646` `matrix_set`) uses exactly round-16 `measure.py`'s formula — `sorted(*.json)`, lines `f"{name} {sha256}\n"`, sha256 of the joined text (`.ufo/waves/round-16/measure.py:286` `def matrix_digest():`) — and refuses unless 9 files, digest `bf9068d8…`, 72 tests.
- Frozen provenance: `--check` resolving to the round-17 frozen copy is pinned to `manifest.json`; a digest mismatch is exit 2.
- `--out` inside `tests/probe-verdicts/` is refused (protects the pinned set digest and `load_matrix`); writes are tmp+`os.replace`.
- Every child runs via `run_cmd` (`mutants.py:716`) with `start_new_session=True`, `PYTHONDONTWRITEBYTECODE=1`, and `os.killpg(..., SIGKILL)` on timeout. check.py is only executed from scratch copies, never imported from the lane.
- Scratch lives under `/tmp/kama-r17-c1mutants-*` and is removed unless `--keep-scratch`.

## Evidence actually exercised (no lane measurement)

- `python3 -c "import ast;ast.parse(...)"` → `AST_OK`.
- `mutants.py --selftest` → exit 0, `"selftest": "pass"`, 30 cases (v1 fixture: M0–M5,M8,M9 found, M6/M7 absent; v2 fixture: all ten found; exact-text checks for M0/M4/M5/M6/M7/M8/M9).
- `--dry-run` on frozen copy → `frozen.verified:true` (sha256 `b853576e…`), totals `site_found 8 / site_missing 2`.
- `--dry-run` on `tests/probe-verdicts/check.py` → totals `site_found 10 / site_missing 0`. The current file changed mid-wave (sha256 `b460b786…`); M6/M7 now match its `served_model_ok` / `route_ok` conjuncts exactly.
- `matrix_set()` → `files 9 digest bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, `pinned_ok True`.
- Expression-level sanity against the landed check.py: baseline rejects each single misbehaviour; M0–M4, M6, M7 each accept their own fault (e.g. M1 `accepts=True`); M9 rejects a fully-good row while baseline accepts it. This proves the edits are semantically live, not cosmetic.
- Stubbed cell (real `run_cell`, fake `run_check`/`run_controls`, no process executed): `applicable 10, killed 1, survived 9`; M9 killed by `pair:before`, `pair:current`, `full:accepted_rose`, `first_failing.row R1`; JSON serializes.
- `run_cmd` timeout test: 1 s cap returned `timed out after 1s; process group killed`, no lingering `sleep 300` in `pgrep`; child env reported `PYTHONDONTWRITEBYTECODE=1`.
- `--check /nonexistent/check.py --dry-run` → `error: --check not found`, exit 2 (a traceback/exit 1 found during testing and fixed).
- `--out tests/probe-verdicts/leak.json` → exit 2, file absent; atomic write to `/tmp` left no tmp siblings.

## Limitations

- Not run end-to-end against the lane (assignment reserves measurement for L1), so no before/after kill counts are claimed here. The counting command is unexercised only in its real child runs; those paths were exercised with stubs.
- fault-controls is invoked with its own default `--probe` (current) for both cells; the before probe is deliberately not forwarded because F0's identity control requires the clean pass-through. Every JSON records the controls path/availability and baseline accepted ids.
- M5/M8 branch semantics are verified structurally (insertion diff + selftest), not by inducing a real timeout or malformed probe row; fault-controls F7/F8 supply that in the `full` cell.
- M6–M8 sites follow the landed lines; if a later rewrite rewords them, they degrade to explicit `site_missing` (n/a), not a false survivor.
- `requests` normalization intentionally hides retry-count changes; route ownership changes still surface.
- A mutant run that fails (timeout/unparseable) where the baseline was clean is killed by design; both-broken runs compare only exit/error text.

## Constraints respected

No `jj`, no git write, no gate/measure/controls run, no server started by me (the only process spawned was a 1 s `sleep` for the kill test), no restricted directory read, no environment dump. A `__pycache__` created beside mutants.py by importlib self-tests was removed; `/tmp` scratch removed. No fleet or sibling file edited.

## Installs

None. `python3` (3.14), stdlib only; no pacman/uv/npx/cargo transactions.
