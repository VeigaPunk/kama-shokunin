# ReadIO — C1 discriminating case: member `sha256_file` generic OSError

Seat: KamaR22.ReadIO (reviewer, read-only). Owned path: this file only.
No code edits, no runs, no installs. Line refs: `f:` = frozen blob
`10271460…:tools/kama-llamacpp-live.py`; `w:` = lane working tree (dirty,
already carries the fix; `git status` shows ` M tools/kama-llamacpp-live.py`).
Draft reviewed: `sandboxes/Matrix/tests/llamacpp-live/install-io-grid.py` (`g:`).

## The case (assigned)

- **id**: `read:<member>:oserror` — draft covers both members:
  `read:server:oserror`, `read:library:oserror` (g:FAULT_CASES).
- **injection**: patch the *module attribute* `sha256_file` on the armed
  module only (`mock.patch.object(module, "sha256_file", new=replacement)`,
  g:~167-177). `install_tree` resolves `sha256_file` through module globals
  (f:197 / w:198), so this is the smallest site that covers *every* member-read
  failure — `open` OSError, mid-`read` OSError, `close` OSError — with one
  boundary. Patching `module.open`/`fh.read` instead would couple the matrix to
  sha256_file's internals and break if ApiFix moves to `hashlib.file_digest`
  (SrcHashlib warns it may bypass Python I/O). `patch('builtins.open')` is
  wrong: process-wide, hits harness I/O.
- **exception**: `OSError(errno.EIO, "matrix-injected", path)` via
  `_expected_exception` (g:~122) — generic OSError, not a subclass; distinct
  from sibling cases EACCES/ENOENT/EISDIR.
- **fixture**: two regular members + a server path inside a
  `TemporaryDirectory`. `install_tree` reads only
  `dirname(server_real)` (f:183), so `server_real` need not exist for this
  cell, but the draft creates it anyway — harmless.

## Expected class per arm (with exact producer refs)

- **frozen**: `except OSError: continue` at f:196-199 drops the member;
  `combined` at f:200-201 is a *well-formed sha256 of a partial name/sha
  list* → **escape** ("comparable partial digest"). Both `read:*:oserror`
  rows must observe `escaped` with `tree` missing exactly the injected member.
- **current (lane)**: `except OSError as exc: raise SetupError(
  f'install-tree-unpinnable:read:{name}:{exc}')` at w:196-200 → **refusal**,
  `exc.code` a STRING with the `:read:{name}:{exc}` SUFFIX, not bare.
- **positive control**: unpatched `control:complete-map-digest` (g:~201-214)
  must return `(EXPECTED_TREE, EXPECTED_TREE_SHA256)` — literal pinned
  oracle (g:33-37), verified consistent in `_selftest` via
  `_expected_fixture_pins` (g:239-242). This pins the success-path map/digest
  contract ("preserve regular-file map/digest exactly").
- **symlink semantics**: `control:ignored-symlink-directory` (g:59, 104-112)
  keeps a soname symlink + nested dir in the fixture and still expects the
  full pin — proves the fix didn't start refusing on skipped non-regulars.
- **arm identity**: frozen module loaded by `git show` exec, sha-pinned to
  `cec67949…023` (g:70-87; verified against the blob). Frozen and current are
  distinct `ModuleType`s — per-module `SetupError` classes (g:~128 uses
  `module.SetupError` correctly).

## Findings

1. **BLOCKER (RESOLVED) — `_observe` exact-matches the agreed refusal token.**
   The draft's g:~130 check requires `error_code == "install-tree-unpinnable"`.
   The lane's dirty working tree at w:188/194/200 emits suffixed codes, which
   would make every fault row `error` (false red). Matrix confirmed it keeps
   exact matching and adds `--producer`; ApiFix confirmed its sandbox
   implementation will keep `.code` exactly `install-tree-unpinnable` for all
   failure types, while placing deterministic operation + `repr(member)` +
   `exc.strerror` in the exception detail/message and chaining the original
   OSError. Thus the shared interface is consistent for the sandbox handoff.
   **Residual integration risk:** lane w:188/194/200 is still the suffixed
   implementation and only L1 reconciles it with the sandbox deliverable.
   The existing `main()` consumer prepends
   `'install-tree-unpinnable:' + ';'.join(problems)` (w:1419-1420), so bare
   `.code` does not remove operation/path detail from the receipt reason.
2. **Escape evidence too thin (medium).** `returned_identity` is a bare bool
   (g:~196). For C1 the escape is only damning if the returned `combined` is a
   *valid comparable digest of a partial map*. Record `missing_members`,
   `partial_members`, and `combined_well_formed` (recompute the tree-sha over
   the returned map). Also split `escape_kind`: `partial-digest`
   (lstat/read cells) vs `null-digest` (`({}, None)` at f:187 — still a
   violation but a different shape; SrcMock flagged the same split).
3. **`injected_calls == 1` brittleness (low).** Activation requires exactly
   one target-path call (g:~181). If ApiFix ever re-reads a member (verify
   pass), a correct producer flips to `injection-not-reached`/`error`. The
   check prevents vacuous green (good — keep it), but note in the docstring
   that `calls ≥ 1` is the semantic, with `== 1` as the strict pin.
4. **Subcode discrimination is otherwise free.** The activation counter
   already proves the injected boundary fired, so a bare family match in
   `_observe` cannot mask a wrong-boundary refusal — a `lstat` refusal on a
   `read` case still shows `injected_calls == 0` → `error`. Asserting
   `:read:<member>` in the code (finding 1a) is belt-and-braces, cheap to add.
5. **`--arm frozen` exits 1 on the *expected* red (info, correct).**
   g:265-268: frozen arm uses `property_pass`, so before-state evidence is a
   property violation → exit 1. `--arm both`/`--selftest` encode red-before/
   green-after correctly via `baseline_red` + `property_pass`. Docstring could
   state the exit-1-on-frozen intent explicitly for the recipe author.
6. **No permission dependence confirmed.** Mock-only injection (g:136-178) —
   no `chmod 0`, immune to root/uid effects (unlike install-links-grid's
   `regular-unreadable`, CallGrid finding 5). Satisfies "no real host
   permissions dependency".
7. **Mid-read fidelity (info).** Mocked `OSError` at the `sha256_file`
   boundary covers the contract (any OSError reaching install_tree) but not a
   *partial* `fh.read` — SrcHashlib notes a mid-read raise also propagates
   identically through f:197-199, so observable behavior is the same; one
   case suffices, no second read-position case needed.
8. **Lane tree is dirty (context).** Working tree = "current" arm; someone
   wrote the fix + CallerRepair migration into the lane (also CallGrid's
   finding). If L1 reverts the lane to base, `--arm current` red is *true* red
   until the fix lands — Matrix's `current` arm reads the working-tree file
   (g:80-87), so this is by design; flag for L1 ordering.
9. **Case is non-vacuous vs the `install_links` backstop.** In `main()` a
   frozen silent drop still surfaces: the member is absent from `tree`, so
   `install_links(..., tree)` reports `<name>:not-hashed` (w:258-259) →
   `install-tree-unpinnable:` refusal (w:1418-1420). This cell is still the
   discriminating C1 case because (a) `install_tree`'s own contract returns
   the comparable partial digest to *any* caller — the claim is about the
   returned identity, not only `main`'s path; (b) the receipt embeds
   `install_tree`/`install_tree_sha256` verbatim (w:1432-1433); and (c)
   `_install_identity_selftest` (f:1136-1141) compares `tree` directly —
   a silent drop is an AssertionError crash, not a refusal. The matrix tests
   `install_tree` in isolation, exactly where the before/after observable
   differs.


## Owned paths

- Written: `.ufo/waves/round-22/build/advice/ReadIO.md` (this file only).
- Surface owner: Matrix → `tests/llamacpp-live/install-io-grid.py`
  (in its sandbox clone).

## Proposed checks for L1 (not run)

- `python3 tests/llamacpp-live/install-io-grid.py --selftest` → 0 after the
  code-format agreement (finding 1).
- `--arm frozen --json` → 1, all 16 faults `escaped` (before evidence);
  `--arm current --json` → 0, all `refused`, `incomplete_identity_escapes: 0`,
  `controls_ok: true`.
