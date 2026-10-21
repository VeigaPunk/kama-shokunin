**Round-21 symlink-aware install pin (appended).** The round-19 note above is
historical for symlinks. `install_tree_sha256` still pins regular files only, so
soname links stay outside it. The round-21 producer adds a second digest that
covers them.

## Install identity: regular-file digest plus link-text digest

source: own-work `tools/kama-llamacpp-live.py:178-203` (`install_tree`) and `:205-226` (`install_links`); `tests/llamacpp-live/check-receipt.py:181-198` (`link_chain_problem`) and `:441-478` (install_links gate block, `--expect-install-links-sha256` at `:468`); `tests/llamacpp-live/install-links-grid.py`; S0xx readlink(2) §DESCRIPTION (Linux man-pages 6.19-1, `man 2 readlink`); S0xx symlink(7) §Symbolic links, relative-path note (man-pages 6.19-1, `man 7 symlink`)
verified-at: 2026-10-21 — producer and gate read at lane tip a29bb84; `python3 tests/llamacpp-live/check-receipt.py --selftest` exit 0; retarget experiment run on a /tmp tree with the producer functions imported (scratch deleted)
recheck: on-release — re-run the gate selftest and `tests/llamacpp-live/install-links-grid.py` after any change to `install_links` or `link_chain_problem`; reopen readlink(2) and symlink(7) when the man-pages package changes

**Rule.** A regular-file tree digest misses soname symlink retargets. Record
link text separately (`install_links`, `install_links_sha256`) and require every
chain to end at a pinned regular member of `install_tree`.

**Observed (retarget experiment).** `libllama.so.0` was retargeted from
`libllama.so.0.1` to `libllama.so.0.2` in a scratch directory of three regular
files. `install_tree_sha256` was `91498d10f3dc37b3fe0e98615b5f45da788e52e2…`
before and after. `install_links_sha256` changed from `89aaeffdc53f2cc9…` to
`cc581641d93513b0…`.

**Gate contract.**
- `install_links` is optional, because receipts from before round 21 lack it.
  When present, its digest must recompute, no link may share a name with a
  regular member, and every chain must reach a pinned regular member through
  same-directory names. Targets containing `/`, `.` or `..` are rejected, and so
  are loops and dangling chains.
- `--expect-install-links-sha256` pins the link digest only when supplied. The
  flagless default records it without an expected value.
- Gate selftest: `9 VALID + 1 NOT-EVALUATED`, 90 mutations and the unreadable
  case rejected.

**Boundaries.**
- *Not execution authentication.* Both digests bind the regular-file bytes and
  link text present in the install directory when the receipt was written. They
  do not show that `llama-server` loaded these files, that the dynamic loader
  chose them, or that they came from upstream release b11755.
- *Link text is not resolution.* `install_links()` records `readlink(2)` output
  verbatim and unresolved; readlink "places the contents of the symbolic link
  path in the buffer buf". The gate resolves a chain itself, one same-directory
  basename at a time, against the recorded text. It never calls `readlink` on the
  live tree at check time. A recorded target that escapes the directory is a gate
  rejection, not a loader result.
- *Loader search is outside the record.* `ld.so` search paths (RPATH, RUNPATH,
  `LD_LIBRARY_PATH`) can resolve a NEEDED name outside this directory. The
  receipt does not record that. [INFERENCE: not observed for this binary.]
- *Relative links are directory-bound.* symlink(7) warns that a relative link
  "may very well cause it to stop working" when moved. That is why the gate
  follows only same-directory names.
- *System NEEDED libraries* (`libc`, `libstdc++`, `libssl`, …) stay outside both
  digests, as before.
