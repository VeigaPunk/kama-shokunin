VERDICT: partial - the round-18 receipt reproduces 0/3 unpinned and 3/3 pinned, but the lane grid (sha256 6f51803c, 03:45:14) counts a gate that dies on mutants as 3/3 rejected with exit 0 even without a pin; the attached patch fixes that, adds the --json schema assertion, and extends the lane's own selftest. All of it executed in a seat-local copy; no official round-19 measurement was run.

# GridJsonSchema - round-19 BUILD advice (seat-local)

Axes: operability and calibration (C2). Subject: `tests/llamacpp-live/install-tree-grid.py`. The lane was not modified; this report is the only file written in it. Evidence lives under `/tmp/kama-r19-GridJsonSchema/out/`.

## Deliverable
- `out/GridJsonSchema.patch`: 391 lines, paths `a/` and `b/` for `tests/llamacpp-live/install-tree-grid.py`. Base is the lane file at sha256 `6f51803c47db597e...`, the version at 03:45:14. Apply from the lane root with `git apply` or `patch -p1`.
- `out/install-tree-grid.final.py`: patched file, sha256 `32f2df59d91fd6bc...`.
- `out/receipts/*.json` (argv, exit, stdout, stderr per run) and `out/RECEIPTS-INDEX.md`. The final evidence is the `rebase2-*` set; `orig-*`, `new-*`, `rebase-*` and `final-*` are earlier series against superseded bases, kept for trace.

## What the patch does (only this file)
1. `schema_problems(doc)` asserts `kama-install-tree-grid/v1`: exact key sets and scalar types; `members` and `rejected` re-derived from `rows`; a VALID baseline must have at least one row (an empty grid would pass vacuously); an INVALID baseline has none, matching the lane's short-circuit; every gated row's status must equal `_member_status(gate_exit, stdout)`.
2. `_member_status`: `accepted` only on exit 0; `rejected` only on exit 1 that printed an `INVALID` verdict line; otherwise `error`. The lane's current code marks exit 1 `rejected` without checking for a verdict, and maps any unknown exit to `accepted`.
3. `main` asserts every document before printing. On failure: message on stderr, exit 3, nothing on stdout.
4. The per-run temp directory is redacted from row `stdout`, so `--json` is byte-identical across runs. Text output and exit codes for the real gate are unchanged.
5. An unparseable receipt, or one without `server`, exits 2 as the docstring promises. The lane exits 1 by traceback for the latter.
6. Selftest: I kept the lane's `run_selftest` (it drives the real gate fixture) and added: schema check on every `--json` case; repeated pinned run must match; the two bad-receipt exits; a crashing gate and an exit-4 gate, both expected to give `error` with exit 1; the exit-3 path via in-process injection; 20 schema mutations plus 3 valid documents.

## Findings
- F1 (calibration, the one that matters): with a gate that raises on mutants, the lane's current grid reports `baseline=VALID members=3 rejected=3/3 tree_pin=off`, exit 0 (`receipts/rebase2-lane2-crash-unpinned.json`). The patched grid reports `rejected=0/3`, exit 1, all rows `error`. The schema cannot see this on its own, since the document is self-consistent; the check is the verdict-line rule. GridDefaults.md (R9) reported the same gap.
- F2: the round-18 counts reproduce. Unpinned exit 1 `rejected=0/3`; pinned exit 0 `rejected=3/3`; text output byte-identical between the lane base and the patch. The three pinned rejected rows all print `INVALID` (the schema passing on a `rejected` row requires it).
- F3: `--json` is not byte-stable on the lane base because each row's `stdout` contains a random temp directory name. Fixed by item 4 under "What the patch does".
- F4: absent requested member exits 1 (`rejected=1/2`, `absent libnot-there.so`) on both bases. Exit 1 reads as "a mutant survived". Left unchanged: the lane's selftest pins it, and GridDefaults.md flags it as an owner decision.
- F5: the producer's `install_tree()` digest on the live tree equals the receipt's `install_tree_sha256` and the pin: 51 members, `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`.

## Verification (run in `/tmp/kama-r19-GridJsonSchema`; exit codes observed)
| command (abbreviated) | exit | observed |
|---|---|---|
| `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-GridJsonSchema` | 0 | copy made |
| `python3 -m py_compile tests/llamacpp-live/install-tree-grid.py` (final file) | 0 | compiles |
| `python3 tests/llamacpp-live/install-tree-grid.py --selftest` (final, working copy, lane gate) | 0 | "...pinned --json repeatability, schema matrix and exit-3 path passed" |
| same selftest on the lane base (`out/lane-now2/`) | 0 | lane's own: "baseline, member rejection, absent member and bad receipt passed" |
| `--selftest` on seven scratch mutants M1-M7 (count wrong; verdict not required; any-nonzero rejected; assertion unwired; empty VALID allowed; redaction removed; unknown exit accepted) | 1 each | each names its failing case, e.g. M3 `gate uncaught-exception: statuses ['rejected'], want ['error']` |
| real receipt, unpinned, text (lane base and patch) | 1 | `baseline=VALID members=3 rejected=0/3 tree_pin=off` |
| real receipt, pinned, text (lane base and patch) | 0 | `baseline=VALID members=3 rejected=3/3 tree_pin=on` |
| pinned `--json` twice (patch) | 0, 0 | raw bytes equal; `schema_problems` returns `[]` |
| crash gate, unpinned (lane base) | 0 | `rejected=3/3` (defect F1) |
| crash gate, unpinned (patch) | 1 | `rejected=0/3`, rows `error` |
| absent member (both) | 1 | `rejected=1/2` |
| unparseable receipt (both) | 2 | documented exit |
| receipt `{}` (lane base / patch) | 1 / 2 | traceback vs documented exit |
| `check-receipt.py` on the receipt with the tree pin | 0 | `VALID` |
| `git apply --check` of the patch on the lane base (in a scratch git repo) | 0 | checks the file |
| `patch -p1 --dry-run -i GridJsonSchema.patch` on the lane base | 0 | applies cleanly |
| `diff -u` of base vs patched file | 1 | expected (differences present); 391 lines |

Commands ran against the gate `check-receipt.py` at sha256 `a0dc1d07...` and receipt `.ufo/waves/round-18/live-recovery/receipt-1.json` at sha256 `89728a02...`, both the lane's current files. Pins were taken from that receipt and checked against the files: model `270cba1b...`, server `b6a31a8e...`, impl `e404b91a...`, probe `36b64978...`, tool `83eac5c0...`. The official runs remain L1's. No installs or updates (`patch`, `git` and `python3` 3.14.8 were already present). No subagents (leaf seat; no task tool). No listeners started; `pgrep` for the grid, gate and `llama-server` finds nothing after the runs.

## Lane drift (affects how L1 applies the patch)
The lane grid changed during this seat: `e3a48957` at 03:39:10 (another seat's `run_selftest`); `2acfec23` next; `6f51803c` at 03:45:14. I rebased twice. The current patch applies to `6f51803c` only. Re-run `git apply --check` before applying if the lane file has moved again.

## Owner decisions and checks
- Decide whether an absent requested member should exit 2 (bad input) rather than 1 (survived). Not changed here.
- The crash-as-error rule changes behavior only when the gate emits no verdict; the real gate's verdicts are unchanged (see F2). Confirm before adopting.
- Outside this seat, not verified by me: GridDefaults.md reports `tools/kama-llamacpp-live.py:198-199` (`except OSError: continue`) silently drops an unreadable file from `install_tree`, so a self-consistent receipt can be incomplete. Producer change, not in this patch.
- Docs (SCORECARD, lesson) are L1's. If adopted, note `kama-install-tree-grid/v1` and exit 3.
- After integration, run from the lane root: `python3 tests/llamacpp-live/install-tree-grid.py --selftest` (expect 0). Then the pinned grid on `.ufo/waves/round-18/live-recovery/receipt-1.json` with `--tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c --json` (expect 0, `rejected=3`), and the same without `--tree-sha` (expect 1, `rejected=0/3`).
