# CallE2E — unpinnable-e2e producer invocation and local permission sandbox

Seat: KamaR22.CallE2E (scout, read-only). Lane /home/vgpnk/Projects/shokunin/kama-shokunin,
HEAD = master = 10271460cc575fc2280aa831e442726385fc2319 (observed `git rev-parse`).
Last commit touching `tests/llamacpp-live/unpinnable-e2e.py`: 7054dba (round-21). No edits, no
verification runs, no installs. LSP not used (no `lsp` device on this seat); callsites below are
from `rg` text search plus direct reads, so "semantic proof" is not claimed.

## Owned paths (for migration)
- `tests/llamacpp-live/unpinnable-e2e.py` — owner CallerRepair. Only this file needs a change on
  this surface.
- Producer `tools/kama-llamacpp-live.py` — owner ApiFix (referenced, not owned here).

## Consumer surface: every callsite into the producer from unpinnable-e2e.py

| # | Site | Kind | Migration |
|---|------|------|-----------|
| 1 | `unpinnable-e2e.py:56-59` exec of producer source into `types.ModuleType("producer")` | loader; module-level code only | No. `SetupError` becomes reachable as `producer.SetupError` (defined `kama-llamacpp-live.py:154`). |
| 2 | `unpinnable-e2e.py:73` `producer.install_tree(str(pristine / "llama-server"))` in-process on the pristine copy | direct `install_tree` consumer | **Yes.** See F1. |
| 3 | `unpinnable-e2e.py:74-75` `producer.install_links(..., tree)[2]` | direct `install_links` consumer | No. Signature/return unchanged by C1; on success `tree` is the identical map. |
| 4 | `unpinnable-e2e.py:84-88` `subprocess.run([python, PRODUCER, --server, --model, --model-sha256, --out])` | subprocess producer invocation, three mutated copies | No code change for the three existing cases (F2); token contract dependency (F3). |
| 5 | `unpinnable-e2e.py:89-100` receipt grading: `exit==2`, `setup_error.startswith("install-tree-unpinnable:")`, `child_pid is None`, `argv is None` | oracle | No change if F3 holds; else must change. |
| 6 | `unpinnable-e2e.py:106` `except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired)` → exit 2 | error contract | **Yes**, together with #2 (F1). |

Producer path these reach (observed): `main()` try block `kama-llamacpp-live.py:1413-1419`
(`sha256_file(server_real)` → `install_tree` at :1414 → `install_links(server_real, tree)` at
:1415 → `SetupError('install-tree-unpinnable:' + ';'.join(link_problems[:8]))` at :1418), caught
at :1602-1603 into `receipt['setup_error']`; `_outcome_exit` :933-936 maps any non-null
`setup_error` to `('setup-error', 2)`. `receipt['argv']` is set only at :1456 and `child_pid` only at
:1499, both after :1414, so any SetupError raised inside `install_tree` still yields
`argv is None` and `child_pid is None` (pre-launch refusal holds).

## Findings

**F1 (migration required, site #2 + #6).** After C1, `install_tree` raises `SetupError` on
listdir/lstat/read failure. In the e2e, that call is in-process; `SetupError` subclasses
`Exception` only (`kama-llamacpp-live.py:154`), not `OSError`/`RuntimeError`/`ValueError`, so it
escapes the tuple at `:106` → uncaught traceback → Python exit 1. Exit 1 is documented in the
script docstring (`:15-16`) and SKILL.md:707 as "a case launched or was not refused", so a pristine
copy that cannot be pinned would be misreported as a violated property instead of
could-not-evaluate. Proposed minimal change (CallerRepair): add `producer.SetupError` handling —
either catch it around `:73` and report `could-not-evaluate: pristine install_tree <code>` → exit 2,
or extend the except at `:106`. Because `producer` is bound inside the `try`, the cleanest form is
a local `try/except producer.SetupError as exc: raise RuntimeError(f"pristine install_tree:
{exc.code}")` around `:73`. Frozen behaviour (`return tree, None` / silent `continue`,
`kama-llamacpp-live.py:184-199`) currently lets a partial pristine `tree` through; `:74-75`
`install_links(..., tree)` would then flag `:not-hashed` for read failures but NOT for
listdir failure (install_links reports `listdir:<strerror>`) nor for lstat failure of a member
install_tree skipped (install_links lstats again). [INFERENCE] reachability on a pristine copy is
low: `copy_tree` (`:35-44`) already read every regular file with `shutil.copy2` into a fresh
`TemporaryDirectory`, so only races/tmpfs faults reach it — but the exit-code contract still must
not depend on luck.

**F2 (no change, site #4).** The three subprocess cases do not exercise the new install_tree
failure branch. With C1 semantics (lstat non-regular → skip, preserved):
- `hwcaps-directory` (`:61-62`): `glibc-hwcaps` lstat is a directory → skipped by install_tree;
  refused by install_links `:241-243` (`glibc-hwcaps:loader-searched-subdirectory`).
- `hwcaps-symlink-to-dir` (`:63-64`, link to `tempfile.gettempdir()`): lstat symlink → skipped;
  same install_links refusal.
- `dangling-soname` (`:65-67`): symlink → skipped; refused `:249-251` `link-not-to-member`.
Round-21 observed tokens (`.ufo/waves/round-21/runs/7054dba1/c2-unpinnable-e2e.stdout:2-4`):
`install-tree-unpinnable:glibc-hwcaps:loader-searched-subdirectory` ×2 and
`install-tree-unpinnable:libggml.so:link-not-to-member;libggml.so.0:link-not-to-member`;
summary `cases=3 refused=3 failures=0`. These remain the expected after-state rows.
Consequence: this script gives NO red-before/green-after signal for C1; the matrix (Matrix seat,
`tests/llamacpp-live/install-io-grid.py`) is the C1 oracle. Do not claim e2e as C1 evidence.

**F3 (shared token contract, sites #4/#5).** The e2e oracle requires the colon prefix
`install-tree-unpinnable:` (`:92`, docstring `:11`); docs say `install-tree-unpinnable:…`
(`corpus/knowledge/llamacpp-loading-lifecycle.md:344`). The assignment text names the new raise
as `SetupError('install-tree-unpinnable')`. If ApiFix emits the bare token (no colon) from
install_tree, the three existing cases still pass (they refuse via :1418), but any future
subprocess case hitting install_tree's branch fails `startswith` and the docs' token shape
diverges. Recommendation to ApiFix: emit `install-tree-unpinnable:<name>:<strerror>` /
`install-tree-unpinnable:listdir:<strerror>`, mirroring install_links' problem strings
(`:234`, `:261`). Then no consumer change at `:92`. If ApiFix keeps the bare token, CallerRepair
must widen `:92` to `setup == "install-tree-unpinnable" or setup.startswith("install-tree-unpinnable:")`.

**F4 (local permission sandbox).** Observed sandbox properties of the e2e:
- All mutation happens in `tempfile.TemporaryDirectory(prefix="kama-unpinnable-")` (`:70`) on
  copies; the real install `~/.local/opt/llama-b11755` (`:30`) is only read (listdir, readlink,
  `shutil.copy2`). No chmod, no ownership change, no host-permission dependency in any existing
  case.
- `copy_tree` (`:35-44`) raises `RuntimeError` on any entry that is neither symlink nor file
  (e.g. an `openvino-licensing/` subdir that install_links would record as `install_unpinned`)
  and `PermissionError` (OSError) on an unreadable real member → exit 2. So host permission
  faults surface as could-not-evaluate, before the producer runs. Unchanged by C1.
- `hwcaps-symlink-to-dir` targets the host temp dir; the producer only lstats/realpaths it,
  never traverses it. Unchanged by C1.
- The producer subprocess inherits the environment and writes only `--out` inside the temp dir
  plus its log (`kama-llamacpp-live.py:1474`, reached only after argv is set, i.e. not on refusal
  paths).
- Seat runs as uid 1000 (observed `id -u`). [INFERENCE] A chmod-000 member case would refuse
  under uid 1000 but be bypassed under root (`os.access`/`open` succeed), so adding a real-permission
  subprocess case to e2e would introduce the host-permission dependency the matrix design forbids.
  Recommendation: do NOT add permission-based cases here; if CallerRepair adds one anyway, guard
  `os.geteuid() == 0` → could-not-evaluate (exit 2). Round-21 falsify already observed real-perm
  producer refusals (`.ufo/waves/round-21/falsify/advice/C2UnpinnableEndToEnd.md:14-15`:
  `...:libllama-common.so.0.7.0:unreadable`, `...:listdir:Permission denied`) — after C1 the
  `unreadable` case's token source moves from install_links (`os.access`, :256-257) to
  install_tree (read failure) if ApiFix raises there first; its text then depends on F3.

## Adjacent callers (not this surface; named so nothing is silently dropped)
- `tests/llamacpp-live/install-links-grid.py:179` `module.install_tree(str(server))` — owner
  CallerRepair / scout CallLinks.
- `tools/kama-llamacpp-live.py:1135`, `:1157` in `_install_identity_selftest` — owner ApiFix.
  chmod-0 block `:1191-1198` only calls `install_links`, not `install_tree`.
- `tests/llamacpp-live/controls.py` runs the producer (`:4`, `:1800`); no `install_tree` call found
  by `rg` — scout CallProducer's surface.
- `.ufo/waves/round-21/recipe-final.json:369-376` runs e2e with no args, expected exit 0,
  timeout 300 — Recipe seat should carry this command unchanged into round-22.
- Docs mentioning the e2e/token: `SKILL.md:695`, `SKILL.md:707`,
  `corpus/knowledge/llamacpp-loading-lifecycle.md:344`, `corpus/lessons/round-21.md:134-143`.
  No doc change required by this surface unless F3 goes bare-token.

## Proposed checks for L1 (not run)
- `python3 tests/llamacpp-live/unpinnable-e2e.py` → expect exit 0, three rows identical to
  round-21 stdout lines 2-4, `summary cases=3 refused=3 failures=0`.
- `python3 tools/kama-llamacpp-live.py --selftest` (producer install identity selftest).
- Optional F1 probe without host perms: run e2e with `producer.install_tree` patched to raise
  `producer.SetupError('install-tree-unpinnable:x')` (unittest.mock in a throwaway harness) →
  expect exit 2 `could-not-evaluate`, not a traceback.

## Remaining unknowns
- ApiFix's final token text (F3) — not yet observable in a sandbox at time of writing
  (`.ufo/waves/round-22/build/sandboxes/` absent when listed).
- Whether CallerRepair adds new e2e cases.

Tools installed/updated: none.
