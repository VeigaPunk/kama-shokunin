VERDICT: partial - proposed SKILL.md rows match gate/grid behavior at draft a29bb84 (selftests exit 0); SKILL.md NOT edited; row placement is an [INFERENCE].

# SkillRowLinks: SKILL.md text for C2 (install-links pin)

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Draft under review: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`. Lane tip `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`. Access/date 2026-10-21. Lane not modified; checks ran in a scratch clone of `a29bb84` (removed).

## Observed facts (executed)

| Command (run in scratch clone of a29bb84 unless noted) | Exit | Observed |
|---|---|---|
| `git show --stat a29bb84` | 0 | 7 files; `SKILL.md` not touched; gate `tests/llamacpp-live/check-receipt.py` +123/-2; grid `tests/llamacpp-live/install-links-grid.py` new (332 lines); `tools/kama-llamacpp-live.py` +28 |
| `git show a29bb84:SKILL.md \| grep -n -i "install\|receipt\|soname\|symlink\|expect-"` | 0 | rows at 536, 574, 610, 654; lines 646-648 say the sixth pin "binds the observed regular-file install tree, not soname-symlink destinations". No `install_links` text in SKILL.md at a29bb84 |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `selftest: 9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected` |
| `python3 tests/llamacpp-live/check-receipt.py --help` | 0 | lists `--expect-install-links-sha256 HEX` ("require the recorded install-links (symlink) sha256") |
| `python3 tests/llamacpp-live/install-links-grid.py --selftest` | 0 | `selftest cases=12 failed=0` |
| `python3 tests/llamacpp-live/install-links-grid.py --json` (default arms = frozen+current) | 1 | frozen: link 0/9 changed, regular 2/2, type 1/1, null 0/1 (`status: fail`, 9 wrong); current: link 9/9, regular 2/2, type 1/1, null 0/1, `status: pass`. Exit 1 is by design: the docstring says `--arm frozen` is expected to exit 1 |
| `python3 tests/llamacpp-live/install-links-grid.py --arm current` | 0 | `summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass` |
| `grep -rln SKILL.md --include=*.py --include=*.sh .` | 0 | no test gate parses SKILL.md rows; matches are wave scripts only, so row wording is free-form |

Gate code facts (read at a29bb84, lines 441-476, 181-198): `install_links` is optional for legacy receipts. When present: keys and values must be strings; `install_links_sha256` must equal the recomputation; no link may shadow a regular `install_tree` member; each chain must end at a pinned regular member, with no `/` target, `.`/`..` target, loop, or dangling chain. `--expect-install-links-sha256` on a receipt without the digest fails. Its selftest expects exit 1 for a legacy receipt with the flag (line 1866). Exit 3 is not re-executed here [INFERENCE: mapping from the round-18 row].

Grid real-tree observation (read-only mirror, dated): real `install_links_sha256` `b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10`; `install_tree_sha256` `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`; `back_compat_install_tree_sha256_equal: true`.

## Proposed edits (text only; not applied)

### 1. Receipt-gate row: new round-21 row (existing rows 536/574/610/654 stay intact, per the lane's append-only convention)

Placement: new subsection `## Round-21 install-links pin (owner: kama)` after the round-20 table (after line 659, before `### Offline GGUF declared identity`). Same 7-column layout as the round-20 table.

```
## Round-21 install-links pin (owner: kama)

This section adds an optional soname-symlink pin. It does not change the six
required receipt pins. Round-20 line 646-648 remains true of
`--expect-install-tree-sha256`: that pin binds regular files only. The optional
`--expect-install-links-sha256` binds soname-symlink names and link text, when the
receipt carries `server.install_links`. Legacy receipts lack the field and remain valid
unless the flag is passed. Round-20 row 654's tally (77 mutations at `37bd4c5`) is
superseded by the round-21 self-test count below; that count is dated, not perpetual.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Live receipt gate with install-links pin | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT --require-schema v3 --expect-model-sha256 H --expect-server-sha256 H --expect-server-impl-sha256 H --expect-install-tree-sha256 H --expect-install-links-sha256 H --expect-probe-sha256 H --expect-tool-sha256 H` | 0 VALID/clean; 1 INVALID/failed; 2 unreadable/could-not-evaluate; 3 NOT-EVALUATED/could-not-evaluate | `--selftest`: `9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected` at `a29bb84` (dated) | six required digests as before, plus optional install-links digest; each symlink chain re-derived from `install_links`: `/` or `.`/`..` targets, loops, dangling chains and shadowing a regular member are INVALID | stdout only | kama |
```

### 2. New grid row

Same section, next row after the gate row:

```
| Install-links symlink-retarget grid | measurement; default run covers both arms: `python3 tests/llamacpp-live/install-links-grid.py [--tree DIR] [--arm frozen\|current\|both] [--json]`; `--selftest` | 0 every selected arm detects all 9 link, 2 regular and 1 type cell and no null cell; 1 an arm misses a cell or flags the null cell (the default `both` run exits 1 because the frozen arm is the before-state instrument and misses 9 link cells); 2 could-not-evaluate (missing tree, unusable git, copy failure) | `--selftest`: `selftest cases=12 failed=0` at `a29bb84` (dated) | frozen arm at `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`; default tree `~/.local/opt/llama-b11755`, read only, mirrored into a temporary directory and removed | stdout; `--json` optional | kama |
```

Note: the `\|` escapes inside the bracket are needed in a Markdown table. Use the same `\|` convention elsewhere in the lane if one exists [INFERENCE: not checked].

### 3. Decision-table row (install identity)

The lane's decision table (SKILL.md line 127 onward) uses `Symptom | First check | Verdict | Action`. The row below belongs in the round-21 section directly after the grid row, as its own small table with the same four columns:

```
| Symptom | First check | Verdict | Action |
|---|---|---|---|
| Soname symlink retargeted (e.g. `libllama.so.0` now points elsewhere), but `install_tree_sha256` is unchanged | Compare `install_links_sha256` against the recorded digest: `python3 tests/llamacpp-live/check-receipt.py RECEIPT --require-schema v3 ... --expect-install-links-sha256 H`. The regular-file tree pin alone cannot see a link-only change. | `install_tree_sha256` unchanged, `install_links_sha256` changed: INVALID (exit 1) against the old pin. A broken chain reports its reason (e.g. `chain ends at ..., not a pinned install_tree member`). | Treat the install identity as changed even though the tree pin passes. Re-pin only after the operator authorizes the retarget. Never edit the receipt to match. |
```

Verified basis: the link-only grid cells (9/9) show `install_tree_sha256` unchanged and `install_links_sha256` changed under the current arm, and the frozen arm reports no change (0/9). Gate reasons quoted are from the grid's real output (`link-dangling`, `link-absolute-outside`, `link-dotdot`, `link-loop`).

## Findings

1. The gate row's flag set now has six required pins plus one optional `--expect-install-links-sha256`. Writing "seven pins" would be wrong: the flag is optional. [observed: gate code and `--help`]
2. The grid's default exit is 1 by design. Without the note in the grid row, a reader could take exit 1 as a broken gate. [observed: exit 1 default; docstring]
3. Legacy receipts: passing the new flag to a pre-round-21 receipt is INVALID, not NOT-EVALUATED. [observed in selftest expectation, line 1866; not re-executed as a standalone run]
4. Gate exit 3 for the new flag is inherited from the row-610 contract [INFERENCE].
5. `SKILL.md` is not machine-parsed by any `.py`/`.sh` test gate at `a29bb84`. Free-form wording is safe, but keep tallies dated. [observed grep]

## Out of scope / not done

- `SKILL.md` not edited (deliverable is text only).
- No live server, no model download, no write to `~/.local/opt`, no lane writes.
- Installed tools: none. Only `git`, `python3` (stdlib) used.
- Outputs saved: `.ufo/waves/round-21/build/out/SkillRowLinks/` (gate selftest, gate help, grid selftest, grid json, grid current arm).
