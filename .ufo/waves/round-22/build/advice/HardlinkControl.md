# HardlinkControl — C1 discriminating case: hardlinked regular basenames

Lane: /home/vgpnk/Projects/shokunin/kama-shokunin. Seat: reviewer, no code edits, no runs.
Owned path: `.ufo/waves/round-22/build/advice/HardlinkControl.md` (this file only).

Worktree state observed mid-review: `tools/kama-llamacpp-live.py` is already fail-closed
in the working tree (uncommitted, diff vs 10271460) and
`tests/llamacpp-live/install-io-grid.py` exists untracked (Matrix draft). Frozen blob
verified: `git show 10271460…:tools/kama-llamacpp-live.py` sha256 =
`cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023`, matching the
grid's `FROZEN_SHA` (install-io-grid.py:24).

## The case

Fixture (single tempdir, no server/permissions/network): three regular basenames where
two are one inode — `llama-server`, `lib.so`, and `hard.so` made by
`os.link(lib.so, hard.so)`. This is exactly the draft's `hardlink` control
(install-io-grid.py:170-172, fixture BODY at :41).

### Positive control (no fault injected)

Expected on BOTH arms — `install_tree(<dir>/llama-server)` returns
`({'llama-server':S,'lib.so':L,'hard.so':L}, D)` where `L == sha256(body)`,
`D == sha256('hard.so L\nlib.so L\nllama-server S\n'.encode())` (sorted order).
Grading must assert full-map equality (`tree == expected`) **and** digest equality,
as the draft does at :186-189 (`result['tree'] == tree and result['digest'] ==
digest and result['fault'] == 0`). Digest-only or set-of-values-only oracles are
blind here (see FP-2).

### Discriminating fault cell

Smallest injection: `patch.object(module.os, 'lstat')` raising `OSError` once,
filtered to `os.fspath(path) == os.fspath(folder/'lib.so')` (draft :76-80, already
present as `stat-lib.so-{permission,missing,io}` at :29-31). One `lstat` call on one
member exercises the narrowest `except OSError` branch — a failure before any byte
is read. Sibling option with the smallest blast radius (module attr, not shared `os`):
`patch.object(module, 'sha256_file', …)` for the `read` stage (draft :82-86).

Expected classes, `stat-lib.so-io` cell:
- **frozen (red)**: silent `continue` at frozen blob l.192-193 → returns
  `({'llama-server':S,'hard.so':L}, D_partial)` — a non-empty, well-formed,
  comparable partial digest. `passed=False` → `violations>0` → exit 1,
  `finding_id=incomplete-install-identity` (draft :281-287).
- **current (green)**: `SetupError` with `.code` starting
  `install-tree-unpinnable:lstat:'lib.so':` and `exc.__cause__ is injected`
  (draft :148-155).

## Why the hardlink pair is the right discriminating content

It defeats every non-basename-keyed completeness notion:

- A fix that keys or deduplicates by inode/`st_nlink`/`st_dev` collapses
  `{lib.so, hard.so}` to one key — silently partial identity that any
  values-level oracle accepts. Only exact-map equality catches it.
- A "coverage" oracle comparing `set(tree.values())` or `combined` digests cannot
  see a dropped member when its hardlinked twin survives: the surviving sha is
  identical. `tree={'hard.so':L}` under an `lstat(lib.so)` fault has the *same*
  digest-value set as the complete tree. Basename-keyed assertion is mandatory.
- The preimage format `'name sha\n'` means a fix deduplicating identical
  *lines* would emit `hard.so L\n` and `lib.so L\n` only once each — still fine;
  but one emitting a single line for both would still hash two identical lines.
  Full-map + independent-digest recompute (draft `expected_tree` :55-58) covers it.

## Honest-saturation note (scope of the claim)

Frozen `install_tree` produces the partial digest, but the frozen receipt path is
transitively backstopped: `main` calls `install_links(server_real, tree)` (frozen
l.1414-1420), and any member listdir-visible but absent from `tree` yields
`'<name>:not-hashed'` (frozen l.258-259) → `SetupError('install-tree-unpinnable:…')`.
Frozen `install_links` also reports `listdir:`/per-name OSError problems (l.233-234,
261-262). Therefore **e2e cannot discriminate on these IO faults** — frozen e2e
already refuses. The C1 red/green lives only at the `install_tree` unit level: the
function silently returned a comparable partial digest; consumers merely happened to
refuse afterward. CallerRepair's `unpinnable-e2e.py` must not be cited as red-before
evidence for this claim. The draft's `paired_problems` field (:130-132) documents
this backstop without grading it — correct.

## False-positive / false-negative risks

- FP-1 Silent no-op injection: mitigated by `result['fault'] != 1 → RuntimeError`
  (:146-147, honest could-not-evaluate) and `cause_is_fault` identity check (:125).
  A fix switching to `os.stat`/`os.scandir` makes the cell could-not-evaluate, not
  vacuous-green. Watchpoint: a future fix calling `os.path.realpath` inside
  `install_tree` would hit the injected `lstat` indirectly — `posixpath.realpath`
  consumes some OSErrors, so `fault` could count 1 while the exception never
  surfaces as the refusal cause.
- FP-2 Content/inode-coverage oracles (above): draft avoids via exact-map+digest.
- FP-3 Patching `module.os` mutates the shared `os` module process-wide for the
  patch window (:116-117). Single-threaded evaluate + exact-path filters make stray
  calls pass through; `install_links` is called after `ExitStack` closes (:130-132),
  so its `realpath`/`lstat` run unpatched. Keep it that way.
- FP-4 `except (InjectedInterrupt, Exception)` (:126) correctly admits the custom
  KeyboardInterrupt subclass but lets `SystemExit`/`GeneratorExit` escape the
  `observe`→`main` boundary — `main` catches only
  `(OSError, RuntimeError, ValueError, TimeoutExpired)` (:288), so such a fix would
  crash the grid with traceback instead of a clean could-not-evaluate 2. Minor.
- FP-5 Token-grammar churn: the worktree raise sites have already been rewritten
  twice during this review (current: `'install-tree-unpinnable:lstat:{name!r}:…'`,
  producer l.193-200). The grid expects prefix `install-tree-unpinnable:<stage>
  [:repr(member)]:` (:148-152). If ApiFix reshapes the token again, green rows go
  false-red. Recommend L1 freeze the grammar
  `install-tree-unpinnable:<stage>[:<member-repr>][:<detail>]` before integration.
- FP-6 `os.link` requires hardlink-capable FS (fine on tmpfs/ext4; exotic FS →
  OSError → could-not-evaluate 2, honest). No `chmod`-based permission tricks in
  the fault path — injected `PermissionError` works under root, satisfying the
  no-host-permissions contract.
- FP-7 Ordering: `sorted(os.listdir)` puts `hard.so` before `lib.so`; a fault on
  `lib.so` leaves `{'hard.so','llama-server'}` — still a non-empty comparable
  partial, the strongest violation shape (not `{}`/`None`).

## Smallest-injection summary

- Unit surface only; `server_real` existence is never checked — `install_tree` uses
  `os.path.dirname` (frozen l.183 / current l.184). Fixture could drop
  `llama-server`, but keeping it is faithful and free.
- One `lstat` OSError on one member = minimal semantic step; one
  `sha256_file` OSError = minimal scope; `builtins.open`/`LateReader` (:88-113) is
  the most brittle (module has no `open` attr — `create=True` correctly used :119)
  but uniquely covers mid-read failure.
- Hardlink **fault** variants (`stat-hard.so-*`) are optional: red/green outcomes
  are identical to plain members; their only added value is asserting a fix
  refuses faults on multiply-linked members too. Cheap to add, not required.

## Owned / referenced paths

- Owned: `.ufo/waves/round-22/build/advice/HardlinkControl.md`
- Reviewed: `tools/kama-llamacpp-live.py` (worktree l.178-203 fail-closed;
  frozen blob l.178-202 silent-skip, l.213-262 links backstop, l.1414-1420 consumer),
  `tests/llamacpp-live/install-io-grid.py` (Matrix draft, reviewed whole),
  `tests/llamacpp-live/install-links-grid.py` (:177-190 identity oracle,
  FROZEN_REV :49 points at older 7a6bc911 — io-grid correctly uses 10271460),
  `tests/llamacpp-live/install-tree-grid.py`, `unpinnable-e2e.py`, `controls.py`.
