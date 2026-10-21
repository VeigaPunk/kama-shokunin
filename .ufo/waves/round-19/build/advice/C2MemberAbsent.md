VERDICT: partial - explicit-member `absent` status and the exit rule are confirmed on both the tested copy and lane HEAD `7229fa9`; default-set absent members are silently dropped (or the default set is replaced) while the grid exits 0, so "absent is reported, not silently skipped" holds only for `--members`.

# C2MemberAbsent: absent-member grid check (round 19)

**Question.** Ask `install-tree-grid.py` for a member absent from the receipt tree; confirm the `absent` status and the exit rule.

**Versions tested (both re-run; identical except the new selftest).**
- A. Copy taken at 03:20 (lane HEAD `8bf99ca` plus the uncommitted round-19 working tree): grid sha `467d44d8…`, gate `afc9e79b…`.
- B. Lane HEAD `7229fa9` (round-19 commit that now holds both files; `git show 7229fa9:<path> | sha256sum` equals the snapshot: grid `49a42f81…`, gate `10912f24…`). The lane rewrote both files at 03:33, after my copy. B's gate adds two selftest mutants (`tree-sha-absent-expect`, `tree-sha-malformed-expect`); every gate step gave identical exits.

**Receipt and pins.** `.ufo/waves/round-18/live-recovery/receipt-1.json` (sha `89728a02…`; schema v3; outcome pass; 51-member `install_tree`; tree sha `6c216313…`). Pins equal receipt-recorded values and on-disk hashes: server `b6a31a8e…` (installed `llama-server`), probe `36b64978…`, tool `83eac5c0…`, impl `e404b91a…`. Model `270cba1b…` is receipt-recorded only; the model file was not re-hashed.

**Reproduce.** `bash /tmp/kama-r19-C2MemberAbsent/out/reproduce.sh` (A) and `SRC=lane-now bash /tmp/kama-r19-C2MemberAbsent/out/reproduce.sh` (B). Logs: `out/reproduce.log`, `out/reproduce-lane-now.log`. Hashes: `out/index.sha256`. Step numbers below match `### NN` labels in the logs.

## Absent status: confirmed
`--members libllama-absent-probe.so.0.0.0`, not in `server.install_tree`, yields row `absent`. No gate runs for it (B L92-94; the JSON row carries only `member` and `status`, step 04). Output `rejected=0/1`, exit 1 (step 01). Step 02 is the pre-pin variant, also exit 1.

## Exit rule: confirmed as implemented
B L118-120: baseline not VALID gives exit 2; otherwise `0 if rejected == len(rows) else 1`. Absent rows are counted in `len(rows)` but never in `rejected`, so any absent row forces exit 1. Exit 0 is impossible with an absent row.

| step | run | exit | key stdout |
|---|---|---|---|
| 01 | absent only, pin on | 1 | `rejected=0/1`, `absent` |
| 03 | `libggml-base` + absent | 1 | `rejected=1/2` |
| 05 | two absent | 1 | `rejected=0/2` |
| 06 | zero model pin (baseline INVALID) + absent | 2 | `baseline=INVALID`; exit 2 takes precedence |
| 07 | default members, pin on (control) | 0 | `rejected=3/3` (matches C2's pinned count) |
| 08 | default members, pre-pin (control) | 1 | `rejected=0/3`, all `accepted` (matches C2's pre-pin count) |
| 13 | lane `--selftest` (B only) | 0 | `selftest: ... absent member ... passed` |

## Finding 1: absent default members are silently dropped (Medium, latent)
B L80: `members = args.members or [m for m in DEFAULT_MEMBERS if m in tree]`. B L81-82: if none are present, `members = sorted(tree)[:3]`. The absent branch (L92-94) is never reached for default names.
- Step 09: the gate accepts a receipt with `libllama.so.0.7.0` removed and its digest recomputed (exit 0).
- Step 10: default grid, pin on: exit 0, `members=2 rejected=2/2`, no row for `libllama.so.0.7.0`.
- Steps 12a/12b: all three defaults removed: exit 0, `members=3 rejected=3/3`, on `LICENSE`, `ggml-rpc-server`, `libggml-cpu-alderlake.so`.
- B's new selftest always passes `--members` (L155), so it never exercises this path.
- The real round-18 tree has all three defaults (step 07), so no current result changes. Latent risk: the runner's `tree-grid-pin` (run.py L67, source read, not executed) uses default members and passes iff exit 0 (run.py L95, source read). A tree missing a default would pass with reduced coverage. [INFERENCE: how likely such a tree is.]

## Finding 2: exit 1 conflates "absent" with "survived" (Low)
Docstring B L17-18: 1 = "a mutant survived". Absent-only (step 01) and a survivor run (step 08) both exit 1; only the status word differs. `absent` is not in the exit contract, and `rejected=0/1` reads like a survivor.

## Proposed fix: tested, not applied
Replace B L80-82 with `members = args.members or list(DEFAULT_MEMBERS)` and delete the fallback. Diff: `out/lane-now-proposed/grid.diff` (and `out/proposed/grid.diff` for A).
- Steps P1/P2: a missing default becomes an `absent` row and exit 1 (was exit 0).
- Controls unchanged: P3 real tree, pin on, exit 0 at 3/3; P4 pre-pin, exit 1 at 0/3; P5 explicit absent, exit 1.
- [INFERENCE, untested] Mapping requested-absent to exit 2 ("bad input") would keep exit 1 meaning "survived". That needs a docstring change and a check of the runner's `want` expectations.

## Gaps and disclosures
- One read-only `git status --short -- .ufo/waves/round-19/build/advice` ran in the lane. It may refresh the index stat cache; no content changed. Other lane git calls were `log`, `show`, and `rev-parse`.
- The first run's `pgrep` matched two `check-receipt.py` processes running from the lane path (PIDs 415891, 416261) that this work did not start. A copy-path check afterwards found none (leftover step, exit 1).
- Not run: the lane's `run.py` (it writes lane artifacts) and model-file hashing.
- Only lane write: this report, per the trailer. Installs or updates: none.
