# SourceReject — round 22 C1 (axis7 operability): os.access precheck rejection

Seat: KamaR22.SourceReject (scout, read-only). Base master = 10271460cc575fc2280aa831e442726385fc2319 (observed via `git rev-parse master`).
No source rows edited, no production edits, no verification runs, no installs.

## Source evidence (observed)

- URL/anchor: https://docs.python.org/3.14/library/os.html#os.access — `id="os.access"` present in raw HTML.
- Version/date: "Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)". Fetched 2026-10-21; raw HTML sha256 `a88a57fd6da9cbe9c95954b693d65cb7a14bbbab455477fab8c1cd65ad4eda11`.
- Admonition type: **Note**, not "Warning" (the page renders it as `Note`). Cite it as a Note.
- Primary quote (24 words):
  > "Using access() to check if a user is authorized to e.g. open a file before actually doing so using open() creates a security hole"
- Supporting quote, second Note in the same entry (12 words):
  > "I/O operations may fail even when access() indicates that they would succeed"
- The same entry recommends EAFP (`try: open(...) except PermissionError`) instead of the precheck. It also says `access()` uses the **real** uid/gid unless `effective_ids=True`.

## Finding: reject an os.access-only fix for install_tree

Frozen `tools/kama-llamacpp-live.py:178-202` `install_tree` silently drops failures:
- `os.listdir` OSError → `return tree, None` (empty map plus a null digest),
- `os.lstat` OSError → `continue`,
- `sha256_file` OSError (open *or* mid-read) → `continue`,
and then computes a valid-looking combined digest over the surviving members.

An os.access-only fix adds `os.access(full, os.R_OK)` (or relies on `install_links`'s existing `:256` `unreadable` check) and leaves those `except OSError: continue/return` paths in place. Reject it, because it cannot satisfy C1's "all consumers refuse incomplete identity":
1. **Gap between check and open (TOCTOU).** The check passes, then `open`/`read` inside `sha256_file` fails. `install_tree` still hits `continue` and returns a partial digest. This is the gap the primary quote describes.
2. **access True but I/O fails.** EIO mid-read, network or FUSE filesystems, ACL/LSM denials: the supporting quote says this outright. Only an `OSError` raised from the real read is ground truth.
3. **Different identity.** `access` checks the real uid while `open` uses the effective uid. As root, `access(R_OK)` is True for a mode-0 file because of the capability override, so the precheck says nothing about permissions.
4. **Wrong coverage.** `access` does not cover the `listdir` failure (`return tree, None`) or the `lstat` failure, which are two of the three silent paths C1 names.
5. **Not for every consumer.** `install_tree` is also called directly by `tests/llamacpp-live/install-links-grid.py:178`, `tests/llamacpp-live/unpinnable-e2e.py:73`, and the selftest `tools/kama-llamacpp-live.py:1135,1157`. The producer's cross-check (`install_links(..., tree)` → `not-hashed`, `:258`, raised at `:1417-1419`) protects only the producer path, and only when `install_links`'s own later scan sees the same entries.

Required shape (same as the shared interface): EAFP. Let each `listdir`/`lstat`/`sha256_file` `OSError` raise `SetupError('install-tree-unpinnable…')`. `os.access` MAY stay as a diagnostic in `install_links`, but never as the gate.

## Flip condition (rejection → acceptable)

The rejection flips only if **both** of these hold:
(a) every `OSError` from `listdir`, `lstat`, and `open`/`read` in `sha256_file` already raises `SetupError` (EAFP), so `os.access` is advisory only and not the mechanism;
(b) the Matrix fault-injection grid shows **0** incomplete-identity escapes under the os.access-only arm, including the cells "access True + open raises", "access True + read raises mid-stream", "listdir raises", and "lstat raises".
[INFERENCE] (b) cannot hold without (a): mocking `os.access` to True while `open` raises is exactly the case the docs warn about. So os.access-only stays rejected in practice. The other flip is upstream: the CPython docs drop both Notes, which is not expected.

## Mistake-mining (related, inside C1)

- `tools/kama-llamacpp-live.py:1194`: `if not os.access(lib, os.R_OK) and install_links(server)[2] != [...]`. As root (or with CAP_DAC_READ_SEARCH), `os.access` is True after `chmod 0`, so the assertion is skipped and the test passes vacuously. That is a host-permission dependency, which C1 forbids for the new matrix. Matrix and CallerRepair SHOULD inject failures with `unittest.mock` (`os.listdir`/`os.lstat`/`open`/`sha256_file` side_effect `OSError(errno.EACCES/EIO)`), not with `chmod`.
- `tests/llamacpp-live/install-links-grid.py:170` has the same pattern: the cell uses `os.chmod(d / regular[-1], 0)`. Its outcome depends on the uid it runs under. CallerRepair's scope.
- Observed in the lane checkout: `install-links-grid.py:176-184` already catches `module.SetupError` and reads `exc.code`. ApiFix MUST keep a `.code` attribute (or CallerRepair must adapt). This is an interface point.

## Owned paths

- Written: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/SourceReject.md` (this file only).
- Scratch outside the lane: `/tmp/os314.html` (fetched docs HTML; not part of the deliverable).

## Proposed checks (L1, after integration; not run)

- `python3 tests/llamacpp-live/install-io-grid.py --arm both --json`: frozen arm exit 1, current arm exit 0.
- `python3 tools/kama-llamacpp-live.py --selftest` (or the repo's selftest entry), run once as non-root and once as root, to expose the vacuous `:1194` branch.

## Remaining unknowns

- Whether ApiFix keeps `install_links`'s `os.access` `unreadable` diagnostic. Allowed either way, provided it is not the gate.
- The exact name of the `SetupError` code attribute in ApiFix's clone has not been verified here.
