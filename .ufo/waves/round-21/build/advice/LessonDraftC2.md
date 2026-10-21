VERDICT: confirm - the C2 lesson draft below matches the measured numbers at a29bb84 (frozen link 0/9, current 9/9, controls 3/3 both arms, null 0/1 both, back-compat equal, gate selftest 6+1/77 at 7a6bc91 -> 9+1/90 at a29bb84), and states the two limits the code and selftest show.

# LessonDraftC2 — round-21 lesson section for C2 (symlink-aware install identity)

Scope: text draft only. Lane not modified; scratch clone `/tmp/kama-r21-LessonDraftC2/lane` at `a29bb84abbb8b4d328f5970a89e448330a3a42ac` (removed at end). Acceptance: every command run; exits below.

## Draft lesson text (proposed for `corpus/lessons/round-21.md`)

```
## C2 symlink-aware install identity (operability 8 -> 8)

Debt. Round 19 named it (`round-19.md:53-57`): `install_tree()` pins regular
files only, so the launcher's `libllama.so.0` / `libggml.so.0` soname symlinks
were skipped and retargeting one left `install_tree_sha256` unchanged. Round 20
kept it as a named limit (`round-20.md`, recovery section).

Change. `install_links(server_real)` in `tools/kama-llamacpp-live.py` records
{basename: readlink text} for every symlink in the server's directory and a
combined `install_links_sha256` over sorted `name -> text` lines. `install_tree()`
is unchanged, so `install_tree_sha256` is byte-identical to the frozen producer
(back-compat). `tests/llamacpp-live/check-receipt.py` validates `install_links`
(optional for legacy receipts), recomputes the digest, requires each chain to end
at a pinned regular member (no `/` target, no loop, no dangling target, no link
shadowing a member), and accepts `--expect-install-links-sha256`.

Measurement. `tests/llamacpp-live/install-links-grid.py` mirrors the real tree
`~/.local/opt/llama-b11755` in copies and applies 13 cells (9 link-only, 2
regular, 1 type, 1 null). Frozen arm = `install_tree()` read from
`7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`; current arm = working tree at
`a29bb84`.

| Class | Cells | Frozen changed | Current changed |
|---|---|---|---|
| link (retarget, dangling, outside, dotdot, delete, add, same-resolution, loop) | 9 | 0/9 | 9/9 |
| regular controls | 2 | 2/2 | 2/2 |
| type control | 1 | 1/1 | 1/1 |
| null | 1 | 0/1 | 0/1 |

Back-compat: `install_tree_sha256` equal across both arms on the real tree
(`6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`). Real-tree
`install_links_sha256` observed: `b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10`.
Gate selftest: 6 VALID + 1 NOT-EVALUATED, 77 mutations at 7a6bc911 -> 9 VALID +
1 NOT-EVALUATED, 90 mutations at a29bb84.

Limits. (1) Not execution authentication: the digests recompute over the bytes
and link text observed at capture, and over receipt self-report. They do not show
which binary executed or that bytes are upstream-authentic. (2) A consistent
retarget onto another pinned member stays VALID without
`--expect-install-links-sha256` (`check-receipt.py` selftest case
`links-retarget-unpinned-valid`, exit 0); only a supplied links pin rejects it
(`links-retarget-pinned`, exit 1). (3) Legacy receipts without `install_links`
remain accepted as optional. (4) Only symlinks directly in the server's directory
are recorded; `install_tree` still covers regular files only. The grid's 13 cells
are a fixed synthetic population, not a census of other installs.
```

## Evidence (every command run in scratch clone at a29bb84; all exits observed)

| Command | Exit | Observed |
|---|---|---|
| `git clone -q …/kama-shokunin /tmp/kama-r21-LessonDraftC2/lane && git -C … checkout -q a29bb84…` | 0 | HEAD printed `a29bb84abbb8b4d328f5970a89e448330a3a42ac` |
| `python3 tests/llamacpp-live/install-links-grid.py --selftest` | 0 | `selftest cases=12 failed=0` |
| `python3 tests/llamacpp-live/install-links-grid.py --arm both --json` | 1 | expected: frozen arm is the before-state instrument; frozen wrong = 9 link cells; current status pass, wrong `[]` |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` (a29bb84) | 0 | `selftest: 9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected` |
| `git show 7a6bc91…:tests/llamacpp-live/check-receipt.py > check-receipt.base.py` then `python3 check-receipt.base.py --selftest` | 0 / 0 | `selftest: 6 VALID and 1 NOT-EVALUATED receipts accepted; 77 mutations + unreadable case rejected` |

Saved copies: `.ufo/waves/round-21/build/out/LessonDraftC2/{grid-both.json,gate-selftest-current.txt,gate-selftest-base-7a6bc91.txt}`.

Grid JSON (`grid-both.json`) fields used: `summary.frozen.by_class.link` = 9 cells, 0 changed; `summary.current.by_class.link` = 9 cells, 9 changed; `null` 1 cell 0 changed in both; `regular` 2 cells 2 changed in both; `type` 1 cell 1 changed in both; `back_compat_install_tree_sha256_equal: true`; `real_identity` install_tree equal across arms.

Code facts (read, [INFERENCE] only where marked):
- `tools/kama-llamacpp-live.py:205-222` `install_links()` — `os.listdir(dirname)` non-recursive, `S_ISLNK` filter, sha256 over sorted `f'{n} -> {links[n]}\n'`. Subdirectory symlinks not covered [INFERENCE from non-recursive listdir; not executed].
- `tests/llamacpp-live/check-receipt.py:1977-1979` comment and case `links-retarget-unpinned-valid` expect 0; `:2001` `links-shadows-member`.
- The grid copies files (`install-links-grid.py:90-91`, `:144-146`) before mutating them; the real tree's unchanged state was NOT independently re-hashed before/after this run (no pre-run snapshot taken), so no-mutation of `~/.local/opt/llama-b11755` is [INFERENCE] from the copy code, not observed.

## Named limits / not claimed

- No live server, no model load, no network, no download performed.
- Existing lesson claims unchanged; C1 (report landing audit) not assessed here.
- Lesson wording deliberately avoids "closed" for symlink identity overall: it closes the R19 named debt for chain-to-pinned-member identity in the install directory only.

## Tooling record

No install or update performed. Used existing `git`, `python3`, `cp`, `sha256sum`, `ls`. No pacman, no sudo. Scratch `/tmp/kama-r21-LessonDraftC2` removed after evidence copy.
