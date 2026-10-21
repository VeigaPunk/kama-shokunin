# StatIO — C1 discriminating case: member `lstat` generic `OSError` (round 22, C1)

Seat: KamaR22.StatIO (leaf, read-only). Owned path: this file only. No code edits, no runs, no installs.

## The ONE case
**`stat-lib.so-io`** — inject a generic `OSError` (exact class `OSError`, not a subclass) at `os.lstat(<dir>/lib.so)` during `install_tree(str(dir/'llama-server'))` in a temp dir containing exactly two regular members `{'llama-server', 'lib.so'}`.

Chosen over `stat-llama-server-io` because `lib.so` fails while the *primary* artifact stays pinned: the escaped identity is demonstrably "partial but comparable" — the strongest red instance of the axis-7 claim.

## Expected classes (verified against blobs/sources below)
- **frozen arm** `master@10271460` (blob sha256 `cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023`, re-verified this session): `install_tree` L191–193 is `try: st = os.lstat(full)` / `except OSError:` / `continue`. Result class = **returned `(tree, digest)` with `tree == {'llama-server': sha(server)}` and a non-`None` comparable digest** — silent partial identity. Distinct from the `listdir` arm, where frozen returns `(tree, None)` at L185–187; a checker keyed on `digest is None` would wrongly call the lstat case clean. Compare `tree` membership AND digest against the oracle, not just `None`.
- **current arm** (uncommitted working tree, observed during build): `tools/kama-llamacpp-live.py:192-196` raises `SetupError(f'install-tree-unpinnable:lstat:{name!r}:{strerror-or-typename}')` `from exc`. Result class = **refused with `code` starting `install-tree-unpinnable:lstat:` and `__cause__ is the injected exception`** (the draft grid now asserts `cause_is_fault`, which requires the `from exc` chain — keep it).
- Oracle (producer-independent): expected complete map = `{n: sha256(body)} `and digest = `sha256(''.join(f'{n} {tree[n]}\n' sorted))`; a returned pair equal to the oracle with `fault == 0` is the positive-control shape; a returned pair *missing* `lib.so` is the violation.

## Smallest injection target
`module.os.lstat` via `unittest.mock.patch.object` — same object as global `os.lstat`, but the wrapper delegates non-matching paths to the captured original and equality-matches via `os.fspath(path) == os.fspath(dir/'lib.so')`, so exactly one call raises. Smaller targets do not exist: `install_tree` has no private lstat alias, and patching `os` wholesale would break `os.path.join/fspath`. Filesystem tricks (chmod on dir) give PermissionError at *listdir*, not per-member lstat, and violate "no real host permissions dependency" — mock is REQUIRED for member precision. Inject `OSError(...)` exactly: `PermissionError`/`FileNotFoundError` arms exist separately (`stat-*-permission`, `stat-*-missing`); the `io` arm is what discriminates a producer that narrowed its except clause to a subclass.

## Positive control
`control-regular` (same `BODY`, `stage=None`, `fault == 0`): must return the complete 2-member map and oracle digest on BOTH arms — this is what makes the frozen arm's partial-map row a *regression delta* rather than a harness artifact. Companion controls `symlink`/`fifo`/`directory` prove intentional-skip semantics are preserved (they must not appear in the map and must not trip the lstat fault matcher since they are still regular-entry skipped only post-lstat… correction: symlink/fifo/dir DO reach `os.lstat` and are skipped by `S_ISREG` — the fault matcher must only arm on the named member, which it does).

## False-positive risks
1. **Reason-format coupling** — matcher `reason.startswith(expected_reason + ':')` (grid ~L149–152) requires a detail suffix after `lstat:{name!r}`. If the producer ever emits a bare `install-tree-unpinnable` or `install-tree-unpinnable:lstat:{name}` token, the row false-fails. Recommend `reason == base or reason.startswith(base + ':')`. Contract's own wording `SetupError('install-tree-unpinnable')` (no detail) would fail today's matcher [INFERENCE — formats still converging this build].
2. **`repr` vs plain name** — producer now uses `{name!r}`; matcher uses `repr(member)`. They are in sync as observed, but any revert to `{name}` on either side false-fails lstat/read rows only (member-free listdir rows stay green) — flag in review.
3. **Shared-`os` blast radius** — `install_links` (paired-problems call at grid ~L130–132) also calls `os.lstat`; under the same patch its failure lands in `problems` (`'{name}:{exc.strerror}'` → `'lib.so:None'` for a bare `OSError('…')` whose `.strerror` is `None`). Informational only today; if paired_problems ever joins `good`, expect `'lib.so:None'` not `'lib.so:not-hashed'`.
4. **Retry producers unobservable** — `fault != 1` → `RuntimeError` → exit 2. A producer that lstat-retries once is masked as "unavailable", not judged.
5. **`--arm both` in a clone** — frozen arm runs `git show` from CWD repo; a sandbox clone resolves the shared object fine, but `--current-source` must point at the *patched* producer (clones see base). Otherwise `--arm both` reports red/red and looks like a failed fix.
6. **`{name!r}` of weird names** — a name containing `'` makes `repr` use double quotes; oracle uses `repr()` too so it still matches, but any consumer regex on `lstat:([^.]+)` would break — use `repr` consistently or match the token prefix only.

## Exact source references
- Frozen blob `10271460` `tools/kama-llamacpp-live.py`: `sha256_file` L171–176; `install_tree` L178–202 — listdir catch `return tree, None` L184–187; **lstat catch `except OSError: continue` L191–193** (this seat's site); nonregular skip L195; read catch L196–199; digest + return L200–202.
- Current working tree `tools/kama-llamacpp-live.py` (uncommitted, observed): `install_tree` L178–203; lstat refusal L192–196 (`from exc`, `{name!r}`, strerror fallback); consumer `install_tree`/`install_links`/`link_problems → SetupError('install-tree-unpinnable:'+…)` L1418–1423; receipt records `install_tree_sha256` L1435–1436.
- Grid draft `tests/llamacpp-live/install-io-grid.py` (untracked, mutable during build): `ERRORS['io']=OSError` L25–26; `FAULTS` incl. `stat-lib.so-io` via L29–31; `observe`/lstat wrapper L61–86, fault counter L64/77–79, `patch.object(module.os,'lstat',stated)` L117; refusal matcher L148–156; controls L157–190; `frozen_source` pin + sha L196–203 (sha verified); selftest incl. `stat-refusal-deleted` fixture L245; exits 0/1/2 L276–290.
- Frozen-line caveat: line numbers above are blob-relative; the working-tree `install_tree` shifted +1 to +2 from the `{name!r}`/strerror format changes observed mid-build — re-resolve before citing in final receipts.

## Red/green outcome for this case
- frozen `--arm frozen`: `stat-lib.so-io` → `status=returned`, `tree={'llama-server': …}`, digest non-`None` ≠ oracle ⇒ violation counted ⇒ finding `incomplete-install-identity`, exit 1. Red as required.
- current `--arm current`: same case → `status=refused`, reason prefix `install-tree-unpinnable:lstat:'lib.so':`, `cause_is_fault`, `fault==1` ⇒ pass; `control-regular` ⇒ complete map ⇒ pass; exit 0. Green as required.

## Tooling
No installs or updates.
