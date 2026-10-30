# SB06DoesNotShow — round 64, wave f, kama

Seat: SB06DoesNotShow (scribe, leaf, no subagent dispatch). Axes: operability + calibration.
Milestone: draft limits list (`What met=True does not show` for SCORECARD §Round 64).
Draft only: no lane source, no SCORECARD edit, no commit, no verdict on any claim.

## Deliverable

`.ufo/waves/round-64/f/out/SB06DoesNotShow/does-not-show-draft.md` — the bullet list (12 C1 bullets, 15 C2 bullets,
one sentence each, every bullet tied to a survivor, an unmodelled vector or an acknowledged limit with a `path:line`),
plus a prose-ready paragraph for `SCORECARD.md` in the round-52/53 style.

Receipts: `.ufo/waves/round-64/f/out/SB06DoesNotShow/receipts/` (`c1-at-tip.out`, `c1-at-tip.err`,
`c2-at-tip.out`, `mutant-live_status.out`, `mutant-finish_reason-gate.out`).

## What the draft contains

**C1 (13 bullets).** Each wave-b item named in the seat brief is covered with a quoted line: MT01 `O3`/`O4` and
MT08 `f2` (the pre-existing non-dumpable own-uid holder, `unreadable_old` recorded and never graded); MT05 `F2`
(`/proc/<pid>/mem` write into the live server) and `F5` (in-process environment-value rewrite); CR03 `K1c`/`K2`/`K3`
(tool-side holder bookkeeping graded for agreement, not provenance) and `K5` (a holder that exists only after the
release); MT13 (the probe-level checks and the draw that no control names); RV02 `D7` (the `/usr/lib` blanket
exemption, still present at the tip and recorded as "Not fixed as a hashing defect" by the wave-f reviewer RV08);
S531/S532 (initial-environment-only, argv-is-what-the-process-says); and the "91 controls are 30 families with
repeats" counting, stated precisely as 79 in-memory mutations of the counter's own snapshot plus 12 live forged
tools.

**C2 (16 bullets).** X01's `## Residual risks and limits` section is quoted line by line (`:112`–`:120`); the
tally statements are lane-authored text read by regular expressions (X07 `:92`, plus RV05's P2/P3 boundary and
attribution defects); the regression table holds one regression per row and only has to flip that row's verdict
(the lane's own round-65 item at `SCORECARD.md:3374` says the same); and a pin fixes bytes, not behaviour on
another host (the registry's own command carries an absolute `HOME`-dependent model path, RV04 D4). Also carried:
the tally tool is outside the 13-file pin table; `work_reuse_refused=1` is a property of the counter, not of the
tip; the idle outcome was proved only through a fake-`pgrep` fixture and the `all_ports_closed: true` pattern is
printed in both declared outcomes; the busy rule admits a superset-invented `other_pids_seen`; printer rejection
credits only `regress-inapplicable`; the closure pointer is stale by construction once the next closure files; and
the wave-f reviewer's D2 (regression-table errors never reach `errors`) and D3 (the tally's exit code is unchecked).

## Measured by this seat (new evidence, beyond the brief)

Two mutants of the **amended** C1 counter at the tip, run from the scratch clone against the unmodified committed
tool. **Both SURVIVED** — each still prints `met=True` with the full `91/91` table, so the amendment did not close
the wave-b `m03`/`m06`/`m07` survivors:

    m_live_status (drop `f.add('live_status')` from probe_fails): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    m_finish_gate (drop `and (p.get('finish_reason') != 'length' or uc == n)` from probe_fails): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True

The cause is structural, not a re-run artefact: `live_status` (`tools/round64-c1-counter.py:721`), `live_ctype`
(`:723`), `live_model` (`:727`), `live_created` (`:732`), `live_fp_shape` (`:735`) and the finish-reason gate
(`:743`) are all present at the tip, and **no control in the 91 names any of the five** — the 79 `add()` calls in
`build_controls` cover 21 families and none of those five names appears in that set (the finish-reason gate is a
sub-clause inside the graded `live_run_field` check, which no control isolates, so dropping it alone leaves the
family's own witness failing on a different sub-clause). This is a new, measured limit not previously recorded for
the amended instrument, and it is why the draft lists the "five probe-level checks are unmodelled" bullet separately
from the wave-b citations.

Honest runs at the measured tip `23b3fdb1a925129a9961cf551f6d40bf251602cb`, both green (no flake to re-run):

    C1: tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    C2: tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True

## Provenance, bounds, tools

- Clone: `S=/fast/scratch/hyaku/kama-r64/f/SB06DoesNotShow`, `D=$S/clone` via `git clone -q --shared
  /home/vgpnk/Projects/shokunin/kama-shokunin`; `git -C D rev-parse --show-toplevel` asserted equal to `$D`;
  checked out `23b3fdb1a925129a9961cf551f6d40bf251602cb`. Every mutating git call named `-C "$D"` explicitly and ran
  only inside that clone; the two counter mutants were committed there with the seat identity
  (`seat <seat@seat.invalid>`), never in the lane.
- No command against the lane mutated anything: read-only `git show`, `git log`, `git diff`, `git rev-parse`,
  `git cat-file`, plus `sed`/`grep` reads of tracked files. No `git add`, no `git add -N`, no commit, no jj command.
- Lane reads were limited to `/home/vgpnk/Projects/shokunin/kama-shokunin`; the fleet repo
  `/home/vgpnk/Projects/shokunin` and `/home/vgpnk/Projects/shokuknow` were not read except the fleet-root SCORECARD
  I was asked to draft into (read-only). No fleet-root tracked file (`LOG.md`, `SCORECARD.md`, `MANIFEST.json`) was
  written.
- Writes: only `.ufo/waves/round-64/f/SB06DoesNotShow.md` (this file) and
  `.ufo/waves/round-64/f/out/SB06DoesNotShow/` (draft + receipts). No `~/.local/bin` or PATH directory was created,
  modified or deleted.
- Ports: the counters opened their own unregistered loopback ports and tore them down; no registered port (8080,
  34113) was touched, no foreign process was signalled or killed. No server of mine was left running.
- Tools installed or upgraded: **none**. No pacman transaction (pacman is paused host-wide). Standard-library
  Python 3 and the pinned `llama-server` already present were used.
- Scratch root `/fast/scratch/hyaku/kama-r64/f/SB06DoesNotShow` is removed at yield, after the receipts were
  copied into the out dir.

## Notes for the L1

- The draft is a **draft**: the paragraph under "Draft text for the SCORECARD paragraph" is the integration-ready
  form; the bullet lists above it are the per-limit evidence with `path:line`. The existing round-64
  `What met=True does not show` line at `SCORECARD.md:3389` already carries a short form of the same list (items
  a–k); the draft supersedes it with citations and adds the unmodelled-probe-check bullet and the wave-f reviewer
  findings RV04 D2/D3, RV05 P2/P3 and RV08 D7.
- Nothing here is a verdict on C1 or C2, and nothing here admits or denies any capability.
- Two of the C1 bullets rest on wave-b reports measured against the **freeze-commit** instrument `f6a4ea9a`, not the
  amended tip instrument; the draft says so where it matters (MT01/MT08/MT05/CR03 were scored pre-amendment, and
  the amendment's own `freeze.txt` lists those five as "Survivors acknowledged and NOT fixed"). The L1 may want to
  re-measure any of them against `23b3fdb1` before the paragraph is asserted as current.
- The `m_live_status` and `m_finish_gate` survivors are the only items in this report that are **new measured
  facts** rather than citations; they are reproducible with the recipe in the item (mutate the counter in the
  clone, commit, score with `--tip 23b3fdb1`).

## One-line outputs

    C1 counter at 23b3fdb1a925: tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    C2 counter at 23b3fdb1a925: tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True
    mutant m_live_status (SURVIVED): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    mutant m_finish_gate (SURVIVED): tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True
    tally (this item is a drafting item; the tally line the C2 counter reads at the tip is inside the C2 line above): tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok]
