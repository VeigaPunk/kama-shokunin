# CallGrid — install-links-grid consumer surface (round 22, C1)

Scope: `tests/llamacpp-live/install-links-grid.py` (owner: CallerRepair). Read-only scout; no edits, no runs.
Base `master` = `HEAD` = `10271460cc575fc2280aa831e442726385fc2319` (observed via `git rev-parse`).
Semantic tooling: no `lsp` device in this seat's toolset → callsites below are from text search plus reading the code. They are literal evidence, not semantic proof.

## Load-bearing observation: the lane checkout is already mutated

`git status` in the lane shows ` M tests/llamacpp-live/install-links-grid.py` and ` M tools/kama-llamacpp-live.py`, both modified at 10:01:4x. Neither change was present when this scout first read the files. The lane producer now carries the fail-closed `install_tree`, with codes `install-tree-unpinnable:listdir`, `:lstat:{name}` and `:read:{name}` (lines 178-205). The lane grid carries a `SetupError` catch in `identity()` (lines 177-190). The contract says seats work in sandboxes and only L1 integrates, so a seat has written into the lane checkout. L1 SHOULD find out who wrote this and decide whether to keep it or reset it to the sandbox flow. Line numbers below refer to the **current lane working tree**; base line numbers are given where they differ.

## Frozen arm (no migration required)

- `FROZEN_REV = 7a6bc911…` (line 49) is loaded with `git show` (lines 68-76). Its `install_tree` body is byte-identical to the one at base `10271460`: only the docstring and the three `except OSError` arms differ from the lane version, checked with `diff` over the two function bodies. It skips listdir, lstat and read errors silently, so the frozen arm stays a valid before-state instrument.
- `7a6bc911` defines `SetupError` (line 154) but has no `install_links`. The frozen arm calls `identity(..., with_links=False)` only (lines 221 and 238).
- Recommendation: keep `FROZEN_REV`. Moving it to `10271460` would give the same `install_tree` but would orphan the round-21 C2 evidence (`SCORECARD.md:1013`, `SKILL.md:685`).

## Current-arm callsites: base behaviour, post-fix effect, and migration status

| # | Location (lane now; base) | Base behaviour | Effect of fail-closed `install_tree` | Migration |
|---|---|---|---|---|
| 1 | `identity()` L177-190 (base L177-184) | `module.install_tree()` is called with no guard | `SetupError` would escape `run()` and reach `main()` L389 → exit 2 for the whole grid | **REQUIRED**. Applied in lane: on `module.SetupError` with `with_links` it returns `problems=[exc.code]`, empty tree and links; the frozen arm re-raises |
| 2 | Real-tree identity L221-225 (base L215-219) | `problems` non-empty → `EvalError("real tree is not pinnable")` | A refused real tree now reaches the same `EvalError` (exit 2), via #1 | Covered by #1 |
| 3 | Mirror pre-mutation check L232-234 (base L226-228) | Mirror identity ≠ real → `EvalError` | A refused mirror is a dict ≠ real, so the same `EvalError` fires | Covered by #1 |
| 4 | Per-cell identity L238-243 (base L232-237) | `changed`, `refused = bool(problems)`, gate over `mtree`/`mlinks` | Refused cell → `changed=True`, `refused=True`, `gate_chain_problems={}` (empty tree/links) | Covered by #1 |
| 5 | Cell `regular-unreadable` L169-170 | `chmod 0` on `regular[-1]`. Base current arm: the skip shrinks the tree, so the digest changes, plus `install_links` reports `:unreadable` and `:not-hashed` | `sha256_file` raises PermissionError → `install-tree-unpinnable:read:<regular[-1]>` → refused. This is the only cell in this grid that reaches the new raise | Behaviour changes; the verdict is kept (`regular` changed 3/3) |
| 6 | Summary `wrong` L253 | `changed != expect_change` | A refused row counts as detection, so the verdict is preserved | None |
| 7 | Selftest `controls-both-arms` L339-342 | Expects `cu regular changed == 3` | Still holds via #1/#5 (uid 1000 observed) | None required. RECOMMENDED: add an assertion (below) |
| 8 | `render()` L286-287 | `+refused` when `refused` | Unchanged | None |
| 9 | `main()` boundary L389 | Any exception → exit 2 | Without #1, `regular-unreadable` would turn `--arm current/both` and `--selftest` into exit 2. With #1 the exit contract (0/1/2) is unchanged | None |

The cells that never reach the new raise are `link-*`, `subdir-*`, `type-*` and `null`. They only change symlinks, directories or the content of readable files. `lstat` succeeds for dangling, looping and outside symlinks, and `install_tree` skips anything that is not a regular file. So the listdir and lstat fault classes are **not** exercised by this grid. Matrix (`install-io-grid.py`) owns those.

## Findings on the lane-applied migration (for CallerRepair / L1)

1. **Null-digest comparable in a refusal (low).** The refused identity is `{"install_tree_sha256": None, "install_links_sha256": None, ...}`. It never compares equal to a real identity, because a refused real tree raises `EvalError` first. Still, it is the "null digest" shape this round's claim forbids as an identity. RECOMMENDED: drop the digest keys from the refusal and add `"setup_error": exc.code`, so the row is visibly a refusal rather than a digest.
2. **`with_links` as the arm discriminator (low).** The new `if not with_links: raise` ties "frozen arm" to "no links". The frozen install_tree cannot raise anyway, so this is safe, but it is implicit. The except clause binds `module.SetupError` per exec'd module, which is correct: the frozen and current modules have distinct `SetupError` classes.
3. **Refusal reason narrowed (info).** In the base, `problems` for `regular-unreadable` were `[<n>:unreadable, <n>:not-hashed]` from `install_links`. Now `install_links` never runs on that cell, and `problems` holds the single `install-tree-unpinnable:read:<n>`. `install_links`'s `not-hashed` branch (producer L259-260) becomes reachable only through a race between the two listdirs.
4. **Missing pin (medium for C1 evidence).** No selftest check asserts that the read failure is refused and that the exact code is recorded. RECOMMENDED check after `rows = …` (L346):
   `checks.append(("unreadable-refused-not-digest", rows["regular-unreadable"]["refused"] and rows["regular-unreadable"]["problems"] == ["install-tree-unpinnable:read:" + "llama-server"]))`. In the selftest tree the sorted regular names are `LICENSE`, `libggml.so.0.27.0`, `libllama.so.0.7.0`, `llama-server`, so `regular[-1]` is `llama-server`.
5. **Host-permission dependence (pre-existing, unchanged).** `regular-unreadable` relies on `chmod 0` denying reads. The seat observed `id -u` = 1000. Run as root, both arms would see "same" for that cell, giving exit 1 and a failing selftest. [INFERENCE] This is not introduced by C1; note it in the docs rather than fixing it here.
6. **Docs (L1/QualityDraft).** Docstring L13-15 ("any problem = refusal") SHOULD mention the `SetupError` refusal. `SKILL.md:685` and `SCORECARD.md:1013` describe the grid outcomes, which stay valid. `SCORECARD.md:1032` lists "unreadable-member fail-closed rule for `install_tree` consumers outside the live producer" as frontier debt, which this round closes.

## Adjacent (not this surface; owned elsewhere)

- `tests/llamacpp-live/unpinnable-e2e.py:73-75` calls `producer.install_tree` on the pristine copy with no guard. A refusal now propagates as an exception. Owners are CallE2E and CallerRepair.
- The producer self-test (`tools/kama-llamacpp-live.py:1136, 1158`) is success-path only. The live producer (L1415-1420) catches `SetupError` at the run boundary.

## Owned paths

- Written: `.ufo/waves/round-22/build/advice/CallGrid.md` (this file only).
- Surface owner: CallerRepair → `tests/llamacpp-live/install-links-grid.py`.

## Proposed checks for L1, after integration (not run)

- `python3 tests/llamacpp-live/install-links-grid.py --selftest` → 0
- `python3 tests/llamacpp-live/install-links-grid.py --arm current --json` → 0, with `regular-unreadable` showing `current.refused=true` and `problems[0]` starting with `install-tree-unpinnable:read:`
- `--arm frozen --json` → 1 (unchanged before-state); `--arm both --json` → 1, with `back_compat_install_tree_sha256_equal=true`

No tools were installed or updated.
