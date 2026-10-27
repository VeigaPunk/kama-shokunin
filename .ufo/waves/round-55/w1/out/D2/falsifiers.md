# Falsifiable content — every claim in the proposed entry, and what refutes it

The entry is admitted only if each row below survives. "Run here" marks what this seat
actually executed; the rest name the command the lane or the outside closure must run,
and the committed receipt that already speaks to it. Nothing was re-run to decorate a
claim: the round-53/55 receipts are committed evidence, and re-running them costs a
network replay (C1, ~60 s per tip) or several.

| # | Claim (entry location) | Check command | Pass | Refutation | Run here |
|---|---|---|---|---|---|
| F1 | The six §"failure it answers" receipts print the verdicts quoted | `python3 .ufo/waves/round-55/w1/out/D2/check-citations.py` | `checks=34 ok=34 fail=0 met=True`, exit 0 | any `FAIL:` line; exit 1 | **yes** (`D2/check-citations.out`, exit 0) |
| F2 | Each hardening leg is visible in the counter's output (`envnames`, `hostlibs`, `anon`, `twopass`, `rehash`, `newrow`; C2 `dropped`, `bad`, `stale`, `superseded`) | read the summary line of `measured/c1-build.out:2` and `measured/c2-build.out:2` | every token present in a `met=True` line | a `met=True` line lacking a leg token, or a leg that never appears | **yes** (F1 checks those tokens) |
| F3 | A `kill` mutant fails the hardened counter on its named leg, and a mutant that passes is labelled `vector` | `python3 .ufo/waves/round-55/c1/battery/run-battery.py` (network, ~4 counter runs) | exit 0, each line `-> ok`; `kind=kill` rows show the named leg in `detail:` | a `kind=kill` row with `met=True` or `-> BATTERY-FAIL`; or a `kind=vector` row counted as a kill | no — committed receipts read only (`m-ldpreload.out:2`, `m-text-flip.out:2`, `m-member-flip.out:2` fail their legs; `m-ldaudit-foreign.out:2` passes as a void vector) |
| F4 | The archive reference is outside the measured tree's control | rewrite `<scratch>/counter-archive.tar.gz` with same-layout bytes after download, then call `Archive.member()` on the frozen module | member bytes equal the download's, not the rewrite | `member()` returns the rewritten bytes (the Sen1Mem F1 shape) | no — the pre-hardening shape is `Sen1Mem/out-archive-ref.txt:1-12`; the hardened code is `tools/round54-replay-code-audit.py:448-453` (read once, parse those bytes) |
| F5 | The observation's blind interval is exactly as declared (two passes + post-exit re-hash; a flip-and-restore inside it is unobserved) | J7Late's probe: flip then restore before the read; and a flip after the counter's `release` | `transient_mem_equal_member: true` and `met=True` (limit holds) | a verdict change from an in-interval flip-and-restore | no — `J7Late/run1-inplace-rename-evidence.json` (run1b a2) records the transient case |
| F6 | A counter base must precede the change it credits; a same-tip base lets the do-nothing control pass | re-freeze C2 `BASE` to the measured tip and run the base control | base prints `met=True` (the failure), then with `BASE=0b75a84c` prints `dropped=1 met=False` | base control `met=False` at a same-tip base (then the round-55 revert was unnecessary) | no — the failed attempt is recorded in `corpus/lessons/round-55.md` §Mistakes; the committed base control is `controls/base.c2.out:2` (`dropped=1 met=False`) |
| F7 | Each cited mechanism has a row + revision + section + committed copy (KQ6) | `check-citations.py` opened-copy checks; plus `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | all 9 copies present with their tokens; census exit 0 | a missing copy, a quote not in the row's section, or a C row supporting a claim | partly — copies checked here (9/9); census not run by this seat |
| F8 | The entry adds ground beyond KQ94/KQ95 (KQ12 overlap) | read `corpus/QUALITY.md:474-475` (KQ94, KQ95) against §The rule | KQ94/KQ95 state predicates; the four leg-admission tests appear in neither | a criterion already stating "a leg counts only when a control kills the previous counter" | **yes** (read; KQ94/KQ95 carry the predicates, no leg-admission rule) |

Two claims are deliberately *not* made, and a reviewer should treat any appearance of
them as a defect in the entry:

- That the hardened C1/C2 counters are now sound. Round 55's own battery shows the
  `hostlibs` leg has no live kill on this glibc (`m-ldaudit-foreign` is a void
  vector), and the declared limits (basename binding, sampling windows, model/data
  segments, byte-identical host install) remain.
- That a passing mutant is a kill. The committed battery receipts and the frozen
  preregistration disagree on exactly this point (`preregistration.json:19,44` vs
  `run-battery.py:57-67` and `m-ldaudit-{writable,foreign}.out:2`); the entry is
  written to the driver's classification, and the disagreement is reported to the
  closure rather than smoothed over.

## Acceptance test for the entry as a corpus file

1. `check-citations.py` exits 0 (F1/F2/F7 above) — it reads only committed lane bytes.
2. Every row of the decision table names (a) a leg token or ledger class that exists
   in a committed counter, and (b) the shortcut receipt that motivated it: F1's
   checks cover (b); F2 covers (a).
3. `corpus/README.md` gains its index row and `corpus/QUALITY.md` gains no new
   criterion from this entry (KQ12) — the proposal asks for neither; if a reviewer
   wants a criterion, it belongs in QUALITY.md as a KQ9x row citing
   `corpus/lessons/round-55.md`, not inside the knowledge entry.
