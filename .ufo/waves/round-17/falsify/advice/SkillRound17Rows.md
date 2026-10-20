VERDICT: partial — the table is mostly accurate, but seven cells misstate command behavior, exit conditions, source attribution, or temporary write scope.

## Findings

### High — C2 controls exit condition omits required failure counters

`SKILL.md:575` says “0 accepted_bad 0 and good_ok, 1 otherwise, 2 own fault.” In `tests/llamacpp-live/controls.py:687-696`, exit 0 additionally requires `gate_flip_bad == 0` and `inconclusive == 0`; either can make the command exit 1 even when `accepted_bad == 0` and `good_ok` is true. The row already describes the gate-flip arm but omits both counters from the zero predicate. State the complete condition: `accepted_bad=0`, `gate_flip_bad=0`, `inconclusive=0`, and `good_ok`.

### Medium — C1 fault-controls self-test cell names the wrong option and scratch behavior

`SKILL.md:571` says “`--list`; asserts matrix digest and 72 tests in its scratch copy.” `fault-controls.py --list` only prints the fault table and exits; it does not load or validate the matrix. The actual `--selftest` path (`tests/probe-verdicts/fault-controls.py:633-649,656-707,726-729`) checks the source matrix's nine files, 72 rows, and digest without a scratch copy. The full measurement path stages and verifies the scratch copy (`:744-760`). Replace `--list` with `--selftest`; distinguish its source-matrix validation from the full run's scratch-copy check.

### Medium — Live v2 command does not select the pinned server

`SKILL.md:573` omits `--server`, while the preceding instruction at `SKILL.md:544` says “always pass `--server` with the absolute path.” The tool help and `tools/kama-llamacpp-live.py:949-951,998-1002` show that omission resolves `shutil.which("llama-server")` from `PATH`. Thus this entry command does not itself select the pinned b11755 binary and can run a different build. Include the absolute `--server` path in the command cell.

### Medium — In-receipt source-binding pin overstates S042/S043 attribution

`SKILL.md:573` claims the in-receipt `source_binding` names S036, S042, and S043. In `tools/kama-llamacpp-live.py:871-885`, the `health_ready` binding passes `None` for its row; `:887-900` binds only `loading_envelope_graded` to `S036`; `:901-920` passes `None` for the teardown spans. The round-17 receipt's `source_binding[*].row` likewise has `null` for `health_ready` and `teardown_graceful`, with `S036` only on the loading record. The code spans and hashes are present, but S042/S043 are not bound as row IDs in the receipt; correct the pin claim or record those IDs.

### Medium — Exit-2 receipt guarantee is too broad for preflight setup failures

The `SKILL.md:573` exit map groups “setup error or internal fault” with “receipt still written.” Preflight checks in `tools/kama-llamacpp-live.py:997-1041` return exit 2 before the receipt object is created at `:1042`. Reproduction in the clone with `--server /no/such/llama-server ... --out /tmp/SkillRound17Rows-setup-error.json` returned 2 and left no receipt. Qualify the guarantee as applying to post-initialization internal faults; preflight setup errors can produce no receipt.

### Low — Mutant `--dry-run` is not a standalone self-test command

`SKILL.md:572` lists `--selftest`, `--dry-run` in the self-test cell. The CLI at `.ufo/waves/round-17/c1/mutants.py:1320-1330` requires `--check PATH` before the dry-run branch; `--grid` is handled first and runs the grid instead. Bare `--dry-run` returned 2 (`--check (or --grid) is required`), while `--check tests/probe-verdicts/check.py --dry-run` returned 0. Give the complete site-scan invocation and do not label it a self-test.

### Low — Three write-scope cells omit self-test temporary files

`SKILL.md:570` says “stdout only” although `tests/probe-verdicts/check.py:541-545` writes two temporary matrix files during `--selftest`; `SKILL.md:574` says “stdout” although `tests/llamacpp-live/check-receipt.py:1324-1332` writes temporary receipt JSONs; and `SKILL.md:577` says “stdout” although its self-test builds a temporary git repository and script copy (`.ufo/waves/round-13/measure.py:829-845,891-940`). These are cleaned temporary writes, not persistent lane artifacts, but the write-scope cells should say so (or explicitly define the column as persistent-output scope).

## Verified cells

- Probe matrix: self-test completed 72/72 rows and rejected 5/5 schema cases. Matrix count is 9 files / 72 rows / 17 `MODEL_LOADING`; fault-controls self-test reported exact set digest `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.
- Receipt gate self-test: 2 valid receipts accepted; 26 v1 + 13 v2 mutations and the unreadable case rejected (39 mutations total).
- `sources-append-only.py --selftest`: 14/14; the pinned `b8e485c` → `ccc4bb3` comparison flagged S041 (anchor and teaches cells), exit 1 as specified.
- Round-13 self-test: 13/13; committed `--quality corpus/QUALITY.md` run exited 0. `expected.json` was unchanged between `cff9e62` and the round commit.
- Model file SHA-256 matched the command pin: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- `count-verdicts.py` self-test passed 16 classifier cases plus the directory scan; `dispatch-provenance.py` passed 28/28.

## Commands and observed exit codes

The clone was created at `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; all Python invocations below ran from `/tmp/SkillRound17Rows-clone` with `PYTHONDONTWRITEBYTECODE=1`.

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/SkillRound17Rows-clone && git -C /tmp/SkillRound17Rows-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3` — exit 0.
- `--help`, all exit 0: `tests/probe-verdicts/check.py`; `tests/probe-verdicts/fault-controls.py`; `.ufo/waves/round-17/c1/mutants.py`; `tools/kama-llamacpp-live.py`; `tests/llamacpp-live/check-receipt.py`; `tests/llamacpp-live/controls.py`; `tools/sources-append-only.py`; `.ufo/waves/round-13/measure.py`; `.ufo/waves/round-17/count-verdicts.py`; `.ufo/waves/round-17/dispatch-provenance.py` (each invoked as `python3 <path> --help`).
- Self-tests, all exit 0: `tests/probe-verdicts/check.py --selftest` (72 rows, 5 schema cases); `tests/probe-verdicts/fault-controls.py --selftest` (9 files, 72 rows, pinned digest); `.ufo/waves/round-17/c1/mutants.py --selftest`; `tests/llamacpp-live/check-receipt.py --selftest` (2 valid, 39 mutations); `tools/sources-append-only.py --selftest` (14/14); `.ufo/waves/round-13/measure.py --selftest` (13/13); `.ufo/waves/round-17/count-verdicts.py --selftest` (16 classifier cases plus directory scan); `.ufo/waves/round-17/dispatch-provenance.py --selftest` (28/28).
- `tests/probe-verdicts/fault-controls.py --list` — exit 0; printed the fault list only.
- `.ufo/waves/round-17/c1/mutants.py --dry-run` — exit 2; missing required `--check`.
- `.ufo/waves/round-17/c1/mutants.py --check tests/probe-verdicts/check.py --dry-run` — exit 0; 10/10 sites found.
- `tools/sources-append-only.py --repo /tmp/SkillRound17Rows-clone --from b8e485c --to ccc4bb3` — exit 1; S041 anchor and teaches cells flagged.
- `.ufo/waves/round-13/measure.py --quality corpus/QUALITY.md` — exit 0.
- Live setup-failure probe: `tools/kama-llamacpp-live.py --server /no/such/llama-server --model /no/such/model.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --out /tmp/SkillRound17Rows-setup-error.json` — exit 2; output path absent.
- `sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf /home/vgpnk/.local/opt/llama-b11755/llama-server` — exit 0; model digest matched the pin.
- `git -C /tmp/SkillRound17Rows-clone diff --quiet cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- .ufo/waves/round-13/frozen/expected.json` — exit 0 (unchanged).
- `ss -ltnp` and `ps -o pid,ppid,stat,cmd -p 637909,637910` — exit 0. The observed Python listeners were sibling `KamaR17.RerunMutantGrid-clone` check.py processes, not this seat; this seat started no llama-server or C2 fake process. The check.py self-test's ephemeral stubs completed and closed.
- Owned `/tmp/SkillRound17Rows-*` scratch was removed before finishing.

## Limitations and installs

- No LSP device was mounted (`read xd://lsp` returned “No such tool”), so status/references/definition/diagnostics were unavailable. Grep was used only to locate source lines; findings rely on direct source reads, command outputs, receipt fields, and the scoped git diff.
- Did not run the full fault-injection measurement, mutant grid, full C2 controls matrix, or a real b11755 lifecycle run; no claim is made about their run results.
- Installs/updates: none.
