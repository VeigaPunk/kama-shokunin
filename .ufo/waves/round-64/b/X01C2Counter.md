# X01C2Counter - round-64 C2 counter build (wave b)

Seat: X01C2Counter (executor, leaf). Milestone: build C2 instrument. Judged on: calibration.
Base `0c1eff3c`, freeze `f6a4ea9a`. Work in scratch clone `/fast/scratch/hyaku/kama-r64/b/X01C2Counter/clone`
(removed before yield). No lane file, reconciler or tally file edited. No commit outside my own clone.
Tools installed: none (stdlib python3, git, pgrep, bash only). No pacman.

## Deliverables (all under `.ufo/waves/round-64/b/out/X01C2Counter/`)

| file | what |
|---|---|
| `round64-c2-counter.py` | the counter, 1825 lines, sha256 `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e`. Goes to `tools/round64-c2-counter.py` |
| `capability-claims-r64.tsv` | 12 rows; r63 quotes/bindings kept; new `outcomes` column (`true` or `true,host-busy`); patterns of instrument-agreement and append-only-audit now bind `pass=N fail=0`; digest-ledger/hexrun/IA/AOA/KLR patterns must end their line (`eol`) |
| `capability-regress-r64.tsv` | header + 12 rows, cols `cap tool_path find replace`. Built by `receipts/merge_regress.py` from the four executor parts (X02 rows 1-3, X03 rows 4-6, X04 rows 7-9, X05 rows 10-12). **No stand-in rows were needed; all 12 are the executors' rows.** Goes to `registry/capability-regress-r64.tsv` |
| `scorecard-canonical-r64.md` | draft block `**Capabilities — canonical list as of round 64**`; the 12 table rows are byte-identical to the round-63 rows (diffed). Insert it inside the Round-63 section (e.g. before `### Round-63 record corrections`), NOT under a `## Round 64` heading (that would move `maxN` to 64 and fail the reconciler banner) |
| `controls-table.md` | family table + all 120 controls with the failure each must produce |
| `receipts/` | counter outputs (base, freeze, stub, trial B + stderr + `detail.json`), mutant outputs, `mut.py` harness, tip-mutant shas |

Counter flags: `--repo --tip --work` as frozen; `--print-pins` prints the sha256 of every pinned file at `--tip` (use it to re-pin);
`--probe-work` (internal: the guard only, used by the counter on itself).

## Design (what each frozen field is, and what it cannot be satisfied by)

One line, `key=value` fields, ends `met=True|False`, exit 0 iff met. Exit 2 `work-reused` (no scoring) when `--work` holds `tip/` or `run/`
(an empty pre-existing `tip/` counts; that was RV03 F1's silent case). `--tip` is resolved to a 40-hex commit and printed (`tip=`, RV03 F12).
Runs use group kill on timeout (RV03 F9), env = PATH HOME LANG LC_ALL + TMPDIR (= `--work`) + PYTHONDONTWRITEBYTECODE; nothing is written outside `--work`.

- `covered=12/12 mismatches=0`: canonical list is the newest and is round 64 (`canon-round`), each of 12 rows once with its 48-char prefix; registry row binds the manifest `run`/`pattern`/`binding`/`outcomes` exactly, `quote` is a >=8-char substring of the prefix, `observed` equals the recorded outcome's text exactly (no blank/fragment skip, RV03 F5), a duplicate row is an error (MT20 a). Live outcome must be a declared one.
- `pinned=13/13 deps_pinned=2/2`: sha256 of the 12 tools + `round42-selfdesc-reconcile.py` against the embedded table (a table that is not 13 long is `pin-table`), read from tip blobs. Beyond the frozen 13 I also pin the two files the pinned tools load by path (`tools/round41-scorecard-reconcile.py`, `.ufo/waves/round-25/count-c2.py`); this is stricter than the freeze and cannot loosen it.
- `regress_flipped=12/12`: per row the table's `find` must occur exactly once in the tip tool, `replace != find`, one-line, and the regressed source must `compile()` (a syntax break is not a behaviour flip). It is applied to an overlay tree (tip tree with `tools/` copied; every other top-level entry symlinked, because the tip tree is 461 MB / 35k files), the row's template re-run there; the unmutated run must be a declared outcome and the regressed run `false`.
- `printers_rejected=12/12`: a printer file (prints the row's pattern, `sys.exit(0)`; the context-capacity printer also writes the idle receipt it was asked for with `--out`) replaces the tool in an overlay. It must first be ACCEPTED by the verdict function (otherwise the rejection would be vacuous), the row's regression must work on the real tool, and the same regression must not apply to the printer (counted only with reason `regress-inapplicable`). A second control family uses decoy printers (printer + the whole original source commented out, so the regression applies once and the printer must stay accepted = not flipped).
- `idle_ok=1`: follows the **L1 amendment (IRC, KamaR64)** exactly: host-busy accepted only on exit 2, receipt `error == host-not-idle-before-K1`, `exit_code 2`, no cell run, `host_idle.ok false`, non-empty `other_pids_seen`, and every pid present in BOTH `pgrep -x llama-server` snapshots (before and after the run, zombies dropped through `/proc/<pid>/stat`) is in `other_pids_seen`. Idle accepted only on exit 0 + the pattern + receipt `summary.cells>=1`, `observed>=1`, `all_ports_closed`, `exit_code 0`, no error, `host_idle.ok true`, `other_pids_seen == []` (the pattern alone is vacuous on an empty cell list and is never accepted alone, X10). The idle outcome is also proved live: the byte-identical tool copy runs with a fake `pgrep` (prints nothing, exit 1) first on its PATH (X10's fixture) and must be accepted as `true`. 21 controls (3 positive, 18 negative); each clause has its own control (cells 0 with observed 1, ports open, receipt exit code 2, foreign pid seen, standing pid omitted, invented set, empty set, no host_idle, ran a cell, ...). Disclosed limit of the amended rule: it detects an omitted or invented-without-standing-pids set; a printed set that is a superset of the true one (extra pids) is not detectable from pgrep snapshots.
- `work_reuse_refused=1`: the counter re-invokes itself with `--probe-work` on its own `--work` (must exit 2 `work-reused`, print no `met=`), on a fresh `--work` (must exit 0 `work-free`, so the guard is not always-refuse), and in-process on an empty `tip/` and on a `run/`-only dir.
- `closure_ptr=1 recon_mismatches=0`: the calibration row = the single `| calibration |` row of the current `## Axes` table (rows before its first `###`; the historical table below carries a second calibration row, which made my first version print `closure-norow`). Its single `latest outside closure \`corpus/lessons/round-N-verifier-spotcheck.md\`` must be the highest N among `git ls-tree corpus/lessons` at the tip. Then the TIP reconciler (pinned, X06) runs as a subprocess on two fixture commits made in a `--shared --no-checkout` clone of the lane under `--work` (plumbing: `read-tree`, `hash-object`, `update-index`, `write-tree`, `commit-tree`; the lane is never written): pointer (and `including round`) repaired vs. a stale older round. Repaired must print `closure_ptr=1`, stale `closure_ptr=0` and more mismatches and a `detail: closure_ptr:` line. `recon_mismatches` is the tip run's count and counts only with exit 0, `mismatches=0`, `met=True` (MT21 B: a count beside a non-zero exit, or no count, is not zero).
- `tally_disclosed=8/8 tally_selftest=1`: `shortcut-tally.py --rounds 56-63 --json` at the tip; a round counts when its status is neither `no-disclosure` nor `unreadable:*`. `tally_selftest=1` needs the tool's own `--selftest` to exit 0 with `fail=0` and mention `no-disclosure`, AND my own fixture repo (a round-56 section with no disclosure block) to still print `no-disclosure`.
- `sens_selftest=4/4`: four planted defective verdict functions handed to the structural sensitivity function (RV03 F8: no witness term now). The structural column itself is gone from the fields: RV03 F3 showed it equals the verdict function; sensitivity is now the regression flip and the printer refusal.
- `controls_rejected=N/120`, `families[...]`: credited only while the baseline (every field above) is met; `met` also needs the control count to equal `EXPECT_CONTROLS` (120), so a removed or added control fails. Escapes print to stderr as `control-escape:`. Extra fields printed: `population`, `recon[...]`, `tally[...]`.

Wall time at trial B: 48-56 s alone, 85 s with four counters concurrent (host shared with other seats). The context-capacity tip run alone waits ~21 s.

## Counter output lines (counter sha `c8b725e5...`)

**Clone tip with every other part stubbed at base** (tip `6d768e8a`: base `f6a4ea9a` + my counter + registry r64 + the 12-row regression table; base reconciler/tally/SCORECARD; `receipts/c2-StubA.out`):
```
tip=6d768e8a6b62 population=0 covered=12/12 mismatches=1 pinned=12/13 deps_pinned=2/2 regress_flipped=11/12 printers_rejected=11/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=1 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,...,62:no-disclosure,63:ok] families[] met=False
```
(`mismatches=1`, `regress_flipped=11/12`, `printers_rejected=11/12`: hexrun-census scan prints `unknown=1` at `f6a4` (the round-63 closure's fleet commit `72c7713e` has no ledger row; X04's row fixes it); `population=0`, `errors=1`: newest canonical list is round 63; `pinned=12/13`: base reconciler.)

**Base tip `0c1eff3c`** (do-nothing control, `receipts/c2-Base.out`): `covered=0/12 ... pinned=12/13 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 tally_disclosed=1/8 tally_selftest=0 controls_rejected=0/120 errors=2 ... met=False`.
**Freeze tip `f6a4ea9a`** (`receipts/c2-Freeze.out`): identical field values, `met=False`. (`work_reuse_refused=1` is a property of the counter, not the tip.)

**Trial tip B** (`955102b2`: stub A + X06 reconciler + X06 SCORECARD calibration-pointer patch + X07 tally + X04 hexrun ledger row + my canonical block; all applied only in my clone; `receipts/c2-TrialB.out`, exit 0):
```
tip=955102b297f8 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=63,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```
Per-row at trial B (stderr): every row `regress=flipped printer=(True,'regress-inapplicable')`; context-capacity tip outcome `host-busy` (host never idle: operator servers 1706355, 242776 and orphan 3262613 stand); the other 11 rows `true`.
This is a trial, not a verdict: it shows the counter reaches `met=True` when the parts the L1 integrates are present and the scans are clean.

## What remains for met=True at the lane tip (L1 integration list)

1. `tools/round64-c2-counter.py` (sha above), `registry/capability-claims-r64.tsv`, `registry/capability-regress-r64.tsv` (header + 12 rows) committed.
2. SCORECARD: the canonical block (see placement note) and X06's one-substitution pointer repair in the calibration row (`scorecard-calibration-closure.patch`); both are needed for `population`, `errors`, `closure_ptr`.
3. X06's reconciler and X07's tally committed byte-exact (`3d9aff8f...` and `85db3cff...` at my read). **The reconciler pin is embedded in the counter** (`PINS[tools/round42-selfdesc-reconcile.py]`); if X06 changes the file again, re-pin with `python3 tools/round64-c2-counter.py --repo R --tip T --print-pins`.
4. X04's hexrun ledger row for `72c7713e` (or X09's proposed rows) and a final `digest-ledger`/`hexrun-census` scan at the integrated tip: both rows are `eol`-anchored `unknown=0` and scan the lane documents at `--tip`, so any hex run the L1's new files (this wave's reports, lessons) add and nobody ledgers makes them `false`.
5. Do not add `corpus/lessons/round-64-verifier-spotcheck.md` before scoring: the pointer must equal the newest file at the scored tip, so the measured tip must precede the outside closure. After the closure files it, the calibration row is stale by construction and the counter (and reconciler) flip at that later tip.
6. Commit the counter's sha256 before wave f (freeze text: the output line and control-family table are frozen then); `controls-table.md` is that table.

## Falsifiers I ran against my own counter (advisory; scored from the clone path; KILLED = `met=False`)

Counter mutants (copy of the counter, one edit, scored against trial tip B). First batch ran on the 111-control version.

| id | mutation | result | named by |
|---|---|---|---|
| C1 | dup-row error record removed | KILLED 109/111 | `registry/dup-identical`, `dup-conflict` |
| C2 | 8-char quote floor removed | KILLED 109/111 | `quote-short`, `quote-empty` (MT20 c survivor) |
| C3 | `recon_mismatches` dropped from TARGETS | KILLED 109/111 | `gate-recon-unknown` + control count 110!=111 (MT21 A) |
| C4 | reconciler verdict ignores exit code | KILLED 110/111 | `recon-exit-1-with-zero` (MT21 B) |
| C5 | host-busy intersection check removed | KILLED `idle_ok=0` | idle controls |
| C6 | work-reuse guard returns False | KILLED `work_reuse_refused=0` | work controls |
| C7 | tally counts `no-disclosure` as disclosed | KILLED 109/111 | `tally-all-no-disclosure`, `tally-one-no-disclosure` |
| C8 | regression `find` count check `!=1` -> `<1` | KILLED 110/111 | `find-twice` |
| C9 | pin compare removed | KILLED 108/111 | `pin-tool-edit`, `pin-reconciler-edit`, `dep-edit` |
| C10 | closure pointer equality removed | KILLED 109/111 | `closure-stale-pointer`, `closure-pointer-above-newest` |
| C11 | idle `cells>=1` clause removed | **SURVIVED** (111/111 `met=True`) on first batch; I added controls `idle-cells-zero-observed-one`, `idle-ports-open`, `idle-exit-code-in-receipt`; re-run: KILLED `idle_ok=0` | |
| C12 | canonical round test removed | KILLED 110/111 | `canon-old-round` (RV03 m3) |
| C13 | `replace == find` no-op test removed | KILLED 110/111 | `noop-regression` |
| C14 | `flip_status` always `flipped` | KILLED 109/111 | `flip-unchanged`, `flip-busy-unchanged` |
| C15 | printer rejected even if it flips | KILLED 110/111 | `printer-that-flips-is-not-rejected` |
| C16 | `eol` anchor removed | KILLED 109/111 | `eol-anchor-digest`, `eol-anchor-trailing-text` |
| C17 | planted `mismatch increase` clause removed | **SURVIVED** on first batch (111/111); refactored to `planted_verdict` with 6 controls; re-run: KILLED 119/120 `planted-no-increase` | |
| C18 | printer need not be accepted first | KILLED 110/111 | `printer-not-accepted` |
| C19 | duplicate row scored instead of errored | KILLED 109/111 | `dup-identical`, `dup-conflict` |
| C20 | population clause removed from `gate()` | KILLED 110/111 | `gate-population` |

Tip mutants (unmutated counter; mutated tip commits in a second shared clone; `receipts/tipmut-*.out`): all `met=False`.

| id | tip edit | fields below target |
|---|---|---|
| T1 | `pin-watch.py` replaced by a printer of its pattern | `pinned=12/13 regress_flipped=11/12 printers_rejected=11/12` |
| T2 | reconciler `mism = 0` (KR03 S1) | `pinned=12/13 closure_ptr=0` (reconciler still prints `mismatches=0`) |
| T3 | SCORECARD pointer set back to round 57 | `closure_ptr=0 recon_mismatches=1` |
| T4 | tally status always `ok` | `tally_selftest=0` (fixture no longer prints `no-disclosure`) |
| T5 | newest canonical list loses the pin-watch row | `population=0 errors=1 recon_mismatches=3` |
| T6 | hexrun ledger row removed | `mismatches=1 regress_flipped=11/12` (`unknown=1`) |
| T7 | regression table: pin-watch `find` twice | `regress_flipped=11/12 printers_rejected=11/12` |
| T8 | registry row `run` template tampered | `covered=11/12 errors=1` |

Tally: counter mutants 20 = 20 KILLED after fixes (2 first-batch survivors C11, C17 that exposed missing controls; the 18 others were run on the 111-control version, the nine controls added afterwards cannot unkill them); tip mutants 8/8 KILLED.

## Residual risks and limits (for the falsify wave)

- The tally tool is not in the frozen pin table (13 files), so a hollow tally is held only by `tally_selftest` (its own selftest must mention `no-disclosure` and my external fixture must stay `no-disclosure`); a tally that prints `disclosed:*` for rounds 56-63 and still gets the fixture right is not caught. Same for the other unpinned tip tools (round41 counter and round-25 count ARE pinned as deps).
- Regression quality is the executors' (X02-X05): e.g. `if new is None and False:` is a real behaviour change but the counter only proves it flips the row's verdict, not that it is the semantically most relevant line.
- `printers_rejected` credits only `regress-inapplicable`; a printer carrying the original source in a live branch that is never executed (decoy, executed-comment) is covered by the decoy control only in the commented-out form.
- Superset-invented `other_pids_seen` under the amended host-busy rule (see idle_ok).
- `closure_ptr` and the reconciler's pointer clause are coupled to X06's text (`closure_ptr=` token and `detail: closure_ptr:` line); a reworded reconciler needs `planted_verdict` updated.
- `tally_selftest` is coupled to X07's selftest naming `no-disclosure`.
- Live rows depend on host state: the pinned llama.cpp/ollama binaries and the stories260K model must exist; hexrun/digest scans read the lane at `--tip`.
- Host: other seats' servers ran concurrently; two concurrent counters were run on distinct `--work` roots with no flake (4 concurrent at the end: all as expected); no port in the registered set was touched; nothing of mine was left running.
- Not exercised: a truly idle host (idle outcome proved only through the fake-`pgrep` fixture), a counter run against the real lane repo (`--repo` was my clone), the 900 s timeout path.

## Counter line (trial tip B, final counter)
`tip=955102b297f8 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True`
Stub-at-base line: `... covered=12/12 mismatches=1 pinned=12/13 regress_flipped=11/12 printers_rejected=11/12 idle_ok=1 closure_ptr=0 tally_disclosed=1/8 tally_selftest=0 controls_rejected=0/120 errors=1 ... met=False`
