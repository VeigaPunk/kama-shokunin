# SymlinkControl — the ONE discriminating C1 case: intentionally skipped symlink remains a valid install_tree control

Seat: KamaR22.SymlinkControl (reviewer, read-only). Owned path: this file only. No code edits, no runs, no installs.

## The case, canonically

A fault-bearing symlink in the fixture is *not* the discriminating form for the intentional-skip claim — a fault on a skipped entry tests the stat/listdir boundary (a different case, below). The discriminating case for "the skip itself is still valid" is:

**`control:ignored-symlink` — fixture = pinned members + one resolvable soname symlink; instrumented, not faulted.**

- Members (Matrix pins, re-derived and verified arithmetically):
  `llama-server` = `ba28c4bd990ab8de10ba4e075aaaf1898cf6f8d1c8f9de965e86dd577d8ccf31`,
  `libllama.so.0.7.0` = `15bc1cbc5801222026914454b05098f5ca16e34b7c383cb670a857be904c889b`,
  combined `install_tree_sha256` = `a0d631033a76ada09e9fabdb2301c608dbe5f56af0e16d1ae6217065d98c105f`.
- Ignored entry: `os.symlink("libllama.so.0", <dir>/"libllama.so.0")` — i.e. link `libllama.so.0` -> `libllama.so.0.7.0`, a resolvable in-directory soname link (the exact shape a real llama.cpp install carries and `install_links` owns; frozen producer L180-181 doc, worktree L180-181).
- Smallest injection/instrumentation target: `mock.patch.object(module, "sha256_file", ...)` as a *call-recording passthrough* (raises `OSError(EIO, "matrix-injected")` if called with the link's path — a silent tripwire). This is smaller and more correct than patching `builtins.open` or `os.stat`: `install_tree` calls the module-global name `sha256_file` (frozen L197, worktree L200), so one patch point covers both arms and both link/target paths.
- Oracle (three conjuncts, all required — drop any and discrimination is lost):
  1. returned `(tree, combined)` == `(EXPECTED_TREE, EXPECTED_TREE_SHA256)` — membership pin;
  2. `sha256_file` call set == exactly `{llama-server, libllama.so.0.7.0}` (absolute paths), zero calls for `libllama.so.0` — the link is never opened *under any name*: catches "read target then discard", "hash link content under link name" (digest pin alone already catches the latter via map drift), and `os.stat`-follow drift;
  3. no refusal/`error` — `observed == "complete"`.

## Expected frozen/current classes

| arm | expected | why |
|---|---|---|
| frozen (10271460 blob) | `complete` — exact pin, call-set clean | silent-skip bug only swallows *failures*; a healthy skip is already correct |
| current (ApiFix) | `complete` — identical tuple, identical call set | C1 mandates "existing symlink semantics" preserved; `S_ISREG`-skip must precede and survive the fail-closed `lstat` raise |

The two arms must return **equal tuples** — that equality, against the no-link positive control, *is* the claim: a symlink is membership-transparent to `install_tree`.

This row discriminates red in exactly the failure modes C1 must not ship: over-refusal (refusing on an unclassifiable-*looking* but intact entry is out of scope here; refusing merely because a link exists is a break), name-added-to-map, link-content-hashed, target-read. All currently-frozen-correct implementations pass it; only a broken fix fails it — the calibration counterweight to the 16 red-before fault rows.

## Companion boundary case (do not merge it into the control)

`lstat:link:*` fault row — same `include_ignored` fixture, injected `PermissionError`/`FileNotFoundError`/`OSError(EIO)` on `os.lstat(<dir>/libllama.so.0)`:

- frozen: `escaped` — and note the escaped tuple is *pin-equal*: the map is complete because the faulted entry was skippable anyway. Escape detection MUST key on "a tuple was returned while the fault fired" (Matrix `_observe` L125-133 does), never on map-diff — a diff-based oracle turns this row into a false negative and freezes the calibration green.
- current: `refused` — `lstat` output is the *evidence* for the skip decision (worktree L192-197). With classification evidence missing the entry is unverifiable, not skippable; fail-closed refusal is the only C1-conformant outcome. Keep it a separate row: folding a fault into the control would wrongly demand refusal on an intentionally-skippable member.

Matrix `FAULT_CASES` (sandbox L40-57) currently faults only `llama-server`/`libllama.so.0.7.0` on the bare fixture; adding `lstat:link:{permission,missing,oserror}` against an `include_ignored=True` fixture closes the boundary lane.

## Positive control

`control:complete-map-digest` (same fixture minus the link): both arms must return the identical pinned tuple. The pairing `control:complete-map-digest == control:ignored-symlink` (returned tuple and call set) is the semantic assertion — "adding a symlink changes nothing `install_tree` reports." Matrix already encodes both controls (`CONTROL_IDS` L59, `_control_row` L201-214); the delta this report adds is the `sha256_file` call-set/tripwire instrumentation and isolating the link from the bundled `plugins/` subdir (`_make_fixture` L107-111) so a failure attributes to exactly one ignored-entry class.

## False-positive / false-negative risks

1. **Exact-token mismatch (live cross-seat gap).** `_observe` requires `exc.code == "install-tree-unpinnable"` (io-grid L130). ApiFix's worktree raises suffixed codes — `'install-tree-unpinnable:lstat:{name!r}:{strerror}'` (producer L194-196, likewise L188-189, L201-203) — and the producer's own consumer composes `'install-tree-unpinnable:' + ';'.join(problems)` at L1421-1423; `unpinnable-e2e.py` already grades with `setup_error` **startswith** `install-tree-unpinnable:`. Under exact-match, every correct current-arm refusal lands in `error` → `property_pass` false → false red. Canonicalize one rule: either `code == "install-tree-unpinnable"` with detail in a separate field, or prefix-match `code.startswith("install-tree-unpinnable")` in both the matrix and e2e. Decide once, apply everywhere.
2. **Escape keyed on map-diff** (see companion case): any oracle asking "did the returned map lose a member" misses the pin-equal symlink escape. Keep "tuple returned after injected fault == escape", including `(tree, None)` from frozen listdir-swallow (frozen L186-187).
3. **Call-count oracles on `lstat`/`listdir`.** Pin only the `sha256_file` call *set*. Counting `lstat` calls freezes an implementation detail (a `scandir`-based or double-probe implementation is still conformant if the pin and read-set hold).
4. **Patch scope bleed.** `module.os` is the process-global `os` module — `mock.patch.object(module.os, "lstat")` affects every same-process use inside the patch window (tempfile cleanup, other arm's module — sequential here, but keep each patch scoped to the single `install_tree` call, as io-grid L177-178 already does). `module.sha256_file` (L168-175 pattern) has no such bleed; prefer it for the control's instrumentation.
5. **Sorting-order accident.** `sorted(listdir)` puts `libllama.so.0` (link) before `libllama.so.0.7.0` (member): an lstat fault on the link fires before any hashing — the frozen escape for `lstat:link` is pin-equal by ordering, not by luck; keep this in the oracle text so nobody "fixes" the row to expect a partial map.
6. **chmod-based injection.** Do not use real permission bits for this case: root/euid makes `open` succeed anyway (host-permission dependency the spec forbids). Mock-only faults keep the row hermetic — io-grid already complies; keep it that way.
7. **`IsADirectoryError`/dangling-target confusion.** The control's link must resolve in-directory (`libllama.so.0` -> `libllama.so.0.7.0`). A dangling link is a legitimate extra cell but belongs to `install_links` policy (frozen L247-252 records `link-not-to-member`), not to the `install_tree` skip control — a dangling link here would still pass (it's skipped identically) but conflates two policies; keep the resolvable soname shape.
8. **`injection["calls"] == 1` gate** (io-grid L180-186): for the link rows the target string must be `os.fspath(directory/"libllama.so.0")` exactly — a substring match (`"libllama.so.0" in path`) false-fires on `libllama.so.0.7.0`. Exact-path equality is required; a mismatch reads as `injection-not-reached`/`error`, i.e. a false red against a correct arm.

## Source-line references

Frozen blob `10271460cc575fc2280aa831e442726385fc2319`, `tools/kama-llamacpp-live.py` (sha256 `cec67949…0e023`):
- L171-176 `sha256_file`; L178-202 `install_tree`; L185-187 listdir → `return tree, None`; L190-193 lstat → `continue` (the C1 stat-failure swallow); L194-195 `S_ISREG` intentional skip — the semantics C1 preserves; L196-199 read → `continue`; L200-202 combined digest.

Worktree producer (in-flux, observed twice this wave — codes gained `{name!r}`/`strerror` detail between reads):
- L154-159 `SetupError` (`.code`); L178-206 fail-closed `install_tree`; L192-196 lstat → `SetupError('install-tree-unpinnable:lstat:…')`; L197-198 unchanged `S_ISREG` skip; L199-203 read → SetupError; L1418-1424 consumer — `install_tree` then `install_links(server_real, tree)`, `link_problems` → `SetupError('install-tree-unpinnable:' + …)` before any launch (fail-closed ordering confirmed: `install_links` never sees a refused map).

Matrix sandbox `.ufo/waves/round-22/build/sandboxes/Matrix/tests/llamacpp-live/install-io-grid.py`:
- L29-37 pins (verified); L40-57 `FAULT_CASES`; L59 `CONTROL_IDS`; L104-112 `_make_fixture` (link + `plugins/` subdir bundled); L125-133 `_observe` (exact-code check at L130 — risk #1); L136-198 `_fault_row`; L201-214 `_control_row`; L221-235 arm counters/`property_pass`/`baseline_red`.

`tests/llamacpp-live/install-links-grid.py` (worktree) L177-190: `identity()` already maps `module.SetupError` → `problems: [exc.code]` for the `current` arm — same prefix-vs-exact question applies wherever `exc.code` is compared downstream.

## No tooling installed

None needed; `git show`, `grep`, `sed`, Python `hashlib` (pin re-derivation only — no project code executed) already present.

## Append-only coordination update

After this report was written, ApiFix confirmed the chosen common contract: `SetupError.code` will be the bare `install-tree-unpinnable`; operation/path/detail stay in the message and original `OSError` remains chained. Thus Matrix's exact-code check is compatible with the intended producer version; the mismatch above records only the in-flux worktree snapshot observed during this review. Keep the e2e prefix check aligned with that bare token.

Clarification to the control oracle: use the ordered call list or exact path-frequency map (not a set alone): exactly one `sha256_file` call for each real regular member, zero for the symlink pathname. The set phrasing above is shorthand for those exact cardinalities; list/count catches a duplicate target hash after `realpath`.

## Tooling gap

No `lsp` device is mounted in this session (`read xd://lsp` returned “No such tool”); therefore no LSP status/references/definition/diagnostics were available. Source-line evidence above is direct file/blob reading only, not semantic proof from an LSP server.

Correction: a literal `startswith("install-tree-unpinnable:")` e2e check does **not** accept ApiFix's confirmed bare `SetupError.code` when serialized as receipt `setup_error`. CallerRepair reports its sandbox e2e accepts bare and colon-qualified forms, while the integrated lane still only accepts the colon-qualified prefix. L1 must update the integrated consumer to accept the bare token (and retain colon-qualified receipt detail if that path remains supported); do not consider the producer/matrix agreement sufficient to close this caller mismatch.
