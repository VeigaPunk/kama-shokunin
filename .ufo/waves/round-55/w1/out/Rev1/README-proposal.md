# Proposal note (not applied): closing the K1Cheat plant class and the vacuous battery arm

Frozen artifacts (preregistration, counters, controls, battery receipts) were not edited.
This note and `proposal-counter.patch` are proposals only.

## 1. Counter (round 56, preregister before data)

`proposal-counter.patch` has two hunks:

- `LD_AUDIT` added to `BAD_ENV` (`tools/round54-replay-code-audit.py:146`). The honest
  server environment carries 5 names (`PATH HOME LANG LC_ALL TMPDIR`; see
  `.ufo/waves/round-55/controls/base.c1.out` detail lines), so no honest run is affected.
  This trips the end-to-end fixture in `fixture.patch` at the envnames leg.
- The host set is asserted equal to the frozen 13-name set at 13 distinct paths, not a
  subset (`code_observe`, after the `finally` at line 567). The honest build maps exactly
  13 host files, so the equality holds; the `fixture.patch` plant (a root-owned foreign
  library named `libzstd.so.1.5.7`) currently passes with **14** host files and
  `met=True` (`c1-audit-LD_AUDIT.in-set-basename.met-True.out`), which is exactly
  K1Cheat's "+1 counted as benign" case re-pointed.

`LD_LIBRARY_PATH` **cannot** simply join `BAD_ENV`: the honest live tool sets it itself
(`tools/kama-llamacpp-live.py:2195`, `child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)`),
so flagging the name would fail the honest replay. That vector needs the host-set
equality (or a path/package-database binding), not an env-name check.

## 2. Battery (next round, receipts committed before data)

- Replace the `m-ldaudit-foreign` arm's DSO with a **conforming** glibc audit module
  (exports `la_version`). The frozen arm used `/usr/lib/libexpat.so.1`, which ld.so
  rejects (`ERROR: ld.so: object ... cannot be loaded as audit interface: undefined
  symbol: la_version; ignored.`), so that receipt (`c1/battery/m-ldaudit-foreign.out:2`,
  `met=True`) proves nothing about the vector; a conforming module loads and its
  constructor runs (`probe.json` probeC, `probe2.json`).
- Add an **anon-page** arm: a host-set-named, root-owned audit module that `mmap`s an
  anonymous RWX page and calls it. Expected: `envnames=3/3 hostlibs=3/3 anon=6 met=False`
  (two passes x three runs), which exercises the anon leg that no frozen receipt
  exercises. Evidence that the leg fires: `c1-audit-anon.in-set-basename.<...>.out`
  and `probe.json` probeA.
- Fix the frozen mutant list (`preregistration.json:44`) to name the arms actually run
  (`m-text-flip`, not the stale `m-ldaudit-writable`), and keep the vector-analysis arms
  out of any rule that says "each named mutant receipt prints met=False"
  (`preregistration.json:19-20`).
