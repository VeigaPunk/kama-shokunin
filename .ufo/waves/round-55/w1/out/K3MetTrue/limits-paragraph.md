### What `met=True` does not show (round 55)

Measured at `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (C1 operability 8→8,
`tools/round54-replay-code-audit.py`; C2 calibration 7→7,
`tools/round54-cited-path-check.py`). Receipts: build
`.ufo/waves/round-55/measured/c{1,2}-build.out`, base controls
`.ufo/waves/round-55/controls/base.c{1,2}.out`, kill battery
`.ufo/waves/round-55/c1/battery/`. Copies of every receipt named below are in
`.ufo/waves/round-55/w1/out/K3MetTrue/receipts/`.

- C1 samples state at instants; the sampling window is not covered. The counter
  observes each server's archive ranges in two `/proc/<pid>/mem` passes and re-stat's
  and re-hashes every observed archive path once after the replay exits
  (`tools/round54-replay-code-audit.py:64-69`, `:714-717`, `:779-803`); a library
  rewritten and restored between those instants, or after the post-exit re-hash, is
  not observed (`tools/round54-replay-code-audit.py:87-90`). The build receipt
  (`measured/c1-build.out`, `twopass=3/3 rehash=0`) and the kill battery
  (`m-member-flip.out` `rehash=3 met=False`, `m-text-flip.out` `code=0 met=False`)
  show only that mutations landing inside the window are caught. The round-53
  disclosure "a mutation after the counter's single memory read is not observed"
  (SCORECARD.md round-53 §What `met=True` does not show) is closed in part by the
  twopass and rehash legs; the window between and after the instants (J7Late facets 2
  and 4 in part) remains open and is the residual limit.
- C1 binds the 13 root-owned host libraries by basename to the frozen set, never
  byte-compared. `HOST_LIBS` is a frozenset of 13 basenames
  (`tools/round54-replay-code-audit.py:134-146`); classification admits any root-owned
  executable mapping whose basename is in the set and fails only a *new* name
  (`:555-564`). The build receipt's `hostlibs=3/3` and its "13 root-owned host files"
  detail line admit the 13 by name; no receipt compares their bytes against any
  reference. The round-53 disclosure "does not compare the 13 root-owned host
  executable libraries against a byte reference" is only partially closed: J5Preload's
  arbitrary root-owned plant now fails the hostlibs leg (a new name), but the frozen
  13 remain content-uncompared. Round 54 Planned item 1 asked for a "verified
  allowlist/provenance"; the allowlist landed, provenance did not.
- C1 cannot distinguish a byte-identical host install from an archive-derived one.
  The predicate compares mapped bytes against the counter's own download of the
  release archive — bytes, not provenance — so a replay whose archive bytes came from
  a byte-identical host install still meets (`tools/round54-replay-code-audit.py:72-93`,
  the frozen Limits sentence). No receipt can show origin; the archive comparison
  establishes equality of bytes only. This is the round-53 disclosed limit ("a
  byte-identical host installation remains indistinguishable from an archive-derived
  one"), re-disclosed by round 54 Planned ("keep the byte-identical host-install …
  limits explicit") and still open at the freeze.
- C1 does not compare the model's mapped bytes or data segments. `mapped_model`
  (`tools/round54-replay-code-audit.py:362-392`) stat's the on-disk model file at the
  mapped path once during `observe` (`:412`) and records only its dev and inode; no
  `/proc/<pid>/mem` read of the model mapping, no second pass, no re-hash of the model
  path, and data segments of every mapping are outside the compared ranges (the 16
  two-pass range reads cover archive members only, `measured/c1-build.out` `code b*`
  lines). The rerun-receipt cross-check compares the recorded dev/inode, not bytes
  (`:739-741`). The round-53 disclosure "Data/RELRO segments and the model's mapped
  bytes are not compared" is NOT closed: round 54 Planned item 1's "explore the
  model's mapped bytes without relying on a pathname" did not land — the round-55
  counter still relies on the pathname hash.
- C1's hostlibs leg has no live kill in the battery: the kill is root-gated. The
  battery's hostlibs entry `m-ldaudit-foreign` is graded `kind="vector"` and *passes*
  (`m-ldaudit-foreign.out` `met=True`; runner `run-battery.py:40-51`, grading
  `:127-130`): on this glibc a non-root actor cannot load a root-owned foreign
  library via `LD_AUDIT`, and any same-uid foreign mapping fails the code/archive
  classification before it reaches the hostlibs leg. The leg's adversarial coverage
  for the root-actor threat model is therefore by-design (a new root-owned library
  fails name classification, `:563-564`) plus this void-vector receipt — the battery
  demonstrates the leg is not reachable by a non-root mutant, not that it kills one.
  (The same design-only gating applies to the anon leg: `anon=0` in every receipt,
  and no same-uid mutant injects an anonymous executable page without tripping
  another leg — the preregistration's own limits line concedes this.)
- C2 is an existence/disposition instrument, not a truth or reachability checker. The
  counter asks whether each cited path resolves or is disclosed by a ledger row whose
  class re-derives from git history (`tools/round54-cited-path-check.py:8-13`,
  `evaluate` `:640-678`); it never inspects the cited content. The build receipt
  (`measured/c2-build.out`, `cited=693 unresolved=14 disclosed=14`) shows pointers
  resolve or are rowed, not that the cited content supports the citing claim. The
  round-53 disclosure stands open. What the round-53 disclosure bundled in is now
  split: J12Hide's "hide a dead SKILL.md citation and remove its ledger row meets the
  counter" is closed by the dropped leg guarding all three surfaces
  (`:648-658`) — `base.c2.out` `dropped=1 met=False` is the red-before receipt, and
  the new `superseded` class (`:461-477`, row
  `registry/cited-path-corrections.tsv:46`) rows a live citation re-pointed to a
  cited, resolving replacement. The disposition half of the round-53 finding is
  closed; the truth half is not.
- C2 validates upstream rows against the surface-stated digest at the frozen commit,
  not the semantic content of the citing claim. The upstream check requires a full
  40-hex ref, pins owner/repo for inventory tokens, and sha256-compares the fetched
  bytes to the surface-stated digest or frozen pin (`tools/round54-cited-path-check.py:526-568`);
  the M10/M11 scenarios fail closed and the M12 contrast discloses
  (`measured/c2-build.out`). This closes the round-53 J11BadFixed disclosure ("an
  upstream row can point at content with a different digest (or a mutable ref) and
  still pass on HTTP 200") for the mutable-ref and wrong-digest classes. The residual
  is digest-not-content: bytes at the pinned commit are validated, but whether the
  pinned llama.cpp file says what the lane's citation claims it says is not measured —
  and a surface that states a wrong digest discloses as long as the upstream serves
  those bytes (the check is self-referential to the surface's stated digest).
- C2's prose-shaped root tokens are advisory only and do not gate. Prose evidence
  claims surface as `advisory:` detail lines (`tools/round54-cited-path-check.py:51-52`,
  `:236-241`, `:587-600`); the build receipt carries four
  (`measured/c2-build.out`: `SCORECARD.md:425` `.ufo/waves/round-13/frozen/expected.json--quality`,
  `SCORECARD.md:597` `tools/registry`, `SCORECARD.md:2171` `corpus/knowledge/...`,
  `SKILL.md:652` `registry/docs/git`), none of which affects `met`. The round-53
  K4Cheat disclosure ("prose citations were invisible") is closed invisibility-wise —
  they now surface — but a prose evidence claim naming a wrong path is visible and
  still passes.
