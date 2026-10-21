# RevengeSkip — original `install_tree` skip semantics, reversed (round 22, C1)

Seat: `KamaR22.RevengeSkip` (read-only revenger). Base read: `master` = `10271460cc575fc2280aa831e442726385fc2319`.
No verification runs, no installs, no production edits. Owned path: this file only.

VERDICT: confirm C1 framing — `install_tree` has exactly one intentional skip (nonregular entries, docstring-stated) and three undocumented silent-failure skips (`listdir`/`lstat`/`sha256_file` → skip/empty), byte-identical from origin (b8e485c, round 16) through base. The fleet's own R21 design names the same three conditions *problems* in `install_links`; the silent skips in `install_tree` are the residual debt.

## 1. Reconstructed original contract (b8e485c, "round-16: MODEL_LOADING verdict…")

Body (verbatim, `git show b8e485c:tools/kama-llamacpp-live.py`):

```python
def install_tree(server_real):
    """{basename: sha256} for every regular file in dirname(server_real),
    plus a combined digest over the sorted 'name sha' lines. Symlinks are
    skipped as members (they are not regular files)."""
    tree = {}
    directory = os.path.dirname(server_real)
    try:
        entries = sorted(os.listdir(directory))
    except OSError:
        return tree, None
    for name in entries:
        full = os.path.join(directory, name)
        try:
            st = os.lstat(full)
        except OSError:
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        try:
            tree[name] = sha256_file(full)
        except OSError:
            continue
    combined = hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()
    return tree, combined
```

Success contract to preserve exactly: map `{basename: hex64}` over regular files only, digest = sha256 over `'{name} {hexdigest}\n'` lines sorted by name; `lstat` (never `stat`/`isfile`) so symlinks are never followed; `sorted(listdir)` for determinism. Current def at `tools/kama-llamacpp-live.py:178`; body **byte-identical** b8e485c → 1027146 (normalized function-level diff: `BODY_IDENTICAL`; no ± line inside `install_tree` in `git diff b8e485c 1027146` — that diff only inserts `install_links` after it and moves call sites in `main`).

## 2. Intent discrimination, skip site by skip site

| Site | Code | Class | Evidence of intent (or absence) |
|---|---|---|---|
| nonregular skip | `if not stat.S_ISREG(st.st_mode): continue` | **INTENDED** | Docstring sentence exists for exactly this; R16 design: `.ufo/waves/round-16/build/advice/LiveHarness.md:10` "over regular files only, symlinks excluded"; R19 lesson codified it as the pin's definition. Unstated side effect [INFERENCE]: also keeps FIFOs/devices out of the read set; never use `isfile` (follows links). |
| enumeration failure | `except OSError: return tree, None` after `os.listdir` | **UNINTENDED silent skip** | No docstring sentence, no commit message, no selftest cell, no lesson claims it. R21 later made the identical condition a *problem* in `install_links` (`listdir:{exc.strerror}` → refusal) — the fleet's own later design contradicts the silent return. |
| stat failure | `except OSError: continue` after `os.lstat` | **UNINTENDED silent skip** | Same absence of any intent record; R21 `install_links` makes failed lstat/readlink a refusal problem. |
| read/hash failure | `except OSError: continue` after `sha256_file` | **UNINTENDED silent skip** — the core C1 harm | A partial map still yields a *valid, comparable* `combined` digest over survivors: silent wrong pin. R21 `install_links(..., tree)` explicitly flags exactly this as `not-hashed` (`'libllama.so.0.7.1:not-hashed'` selftest cell), proving the lane already classes it unpinnable — but only via the second, TOCTOU-exposed layer. |

No commit body anywhere in the lane records a rationale for the three silent skips (prior seat RevengeInstallTreeIntent R21 reached the same: "No original rationale is recorded anywhere in the lane").

## 3. Lesson lineage the fix must honor

- **R19** (`corpus/lessons/round-19.md:53-57`): "The sixth pin is therefore regular-file identity, not complete install identity; a symlink-aware pin is named debt." The nonregular skip is the *defined* pin; do not widen membership to links.
- **R20**: pin wording "observed bytes, not authentication" (M3).
- **R21** (`corpus/lessons/round-21.md:21-26, 84-92, 133-143`): `install_links` records fail-closed problems — unreadable members, failed lstat/readlink, control-character names, non-regular/non-link, `not-hashed` for members `install_tree` failed to hash; caller refuses with `install-tree-unpinnable`; `install_tree_sha256` unchanged (back-compat). C1 completes this by moving refusal to the source.
- **Fleet precedents for the silent-skip class**: `corpus/lessons/round-5.md:9-13` (souji) — silent omission from a digest scope (`find -type f`) is a false-SAFE defect, fixed fail-closed (`symlink-present`); `corpus/lessons/round-12.md:76` M14 — silently dropped `readlink` OSError.

## 4. Consumer census — what "refuse incomplete identity" must not break

- `tools/kama-llamacpp-live.py` `main` (~1413-1417): `install_tree(server_real)` then `install_links(server_real, tree)`; `except SetupError` at ~1602 maps `exc.code` to `receipt['setup_error']`, exit 2. `SetupError` (`:154-159`) carries a single stable code token — prefer exactly `'install-tree-unpinnable'`; appending detail to the token would churn `tools/error-verdict-census.py` classifications, so keep the token stable (a subtype is not needed; put any detail in an adjacent receipt field if L1 wants it).
- Selftest `_install_identity_selftest` (~1130-1207): exercises success paths, retarget immutability (`moved[0] != (tree, tree_sha)`), and `install_links` problems — **no cell exercises the three silent skips**, so a fail-closed `install_tree` cannot break it; L1 may add cells.
- `tests/llamacpp-live/check-receipt.py:410-421`: `install_tree_sha256` accepted `allow_none=True` ("null only when the producer could not list the directory"); `--expect-install-tree-sha256` requires hex64. Post-fix, null can only accompany a recorded `setup_error`, which the gate already grades INVALID — no gate change forced by C1.
- `tests/llamacpp-live/install-tree-grid.py` (R19): mutates receipt JSON, never calls the producer function — unaffected.
- `tests/llamacpp-live/install-links-grid.py`: frozen arm loads `git show 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d:tools/kama-llamacpp-live.py` via `exec` into a module (`frozen_producer`), expected red on frozen; unaffected by the fix.
- `tests/llamacpp-live/controls.py:128-129`: tree timing only.
- `tools/error-verdict-census.py:228`: writes a synthetic receipt with an `install_tree` block — text-level, unaffected.
- OBSERVATION (not owned by me): `tests/llamacpp-live/install-io-grid.py` (Matrix's deliverable) is already present in the **lane checkout** (header pins `FROZEN = 10271460cc…`, `FROZEN_SHA cec67949…`, finite fault population over listdir/lstat/read × {permission, missing, io, isdir} + late-read, controls incl. symlink/directory/hardlink/KeyboardInterrupt/ValueError). Contract says seat output belongs under `.ufo/waves/round-22/build/` until L1 integrates — flagging for L1; I did not touch it.

## 5. Residuals the fail-closed fix does NOT close (name, don't fix)

- TOCTOU between `install_tree` and `install_links`, and between fault windows generally (see CritRace): a member can vanish/appear between the two calls so one layer sees clean state.
- `os.access(full, os.R_OK)` in `install_links` returns True as root even on chmod-0 members (PermRoot): deterministic `unittest.mock` injection at `os.listdir`/`os.lstat`/`sha256_file` is the right matrix; permission-based fixtures are root-sensitive.
- Legacy receipts (pre-R21) keep their symlink gap by design.

## 6. Exact owned paths / evidence

- Written by me: `.ufo/waves/round-22/build/advice/RevengeSkip.md` (this file). Read-only seat: no production edits, no sandbox, no verification runs, no tool installs.
- Evidence commands (all rc 0): `git show b8e485c:tools/kama-llamacpp-live.py`; `git diff b8e485c 1027146 -- tools/kama-llamacpp-live.py`; normalized body diff b8e485c vs 1027146 → identical; `git log --reverse -S 'def install_tree' -- tools/kama-llamacpp-live.py` → b8e485c only.

Confidence: high for body identity, skip-site classification and consumer census (all read directly); medium only for the R16 lineage documents' interpretive weight (cited from R21 RevengeInstallTreeIntent, which executed its own checks).
