# CtlDoNothing — do-nothing control (round 30, kama lane, C1 calibration)

## Policy

Do nothing. No policy code, no file edit, no correction row. SCORECARD.md is left exactly as
the lane has it. The clone is the lane remote; the counter is the LANE copy, unmodified.

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r30/ctl/CtlDoNothing`
- Lane tip checked out: `52ac3af8614b5040ba5e17f17a2c7af029706e6c` ("round-29 verifier spot-check
  (integrator, hyaku): non-author admit/reject"), the tip named by the round-30 context.
- Protocol step 2 (commit the policy with a local identity): the policy is a no-op, so the commit
  is empty. `git commit --allow-empty` with local identity `ufo-control CtlDoNothing
  <ctl-donothing@localhost>` → candidate commit `3d7714a01bdfbd7c106ca67ff7457f74a11e8ffa`.
  Its tree is byte-identical to the lane tip: both trees are
  `45c05ee28cb573d0996d069bfc742ac269f72f22`. `git status --porcelain` in the clone: empty.
- `change.diff` (lane tip → candidate commit): 0 bytes, by construction — the correct artefact
  for a do-nothing policy.
- Counter used: the LANE copy `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py`,
  sha256 `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` — re-verified after the
  run, unchanged from the frozen preregistration hash. The counter was NOT copied, patched or run
  with a variant.

## Commands (verbatim)

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
/usr/bin/python3 .ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlDoNothing \
  --tip 3d7714a01bdfbd7c106ca67ff7457f74a11e8ffa \
  --out .ufo/waves/round-30/controls/CtlDoNothing/counter.json
# -> statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 3d7714a01bdf
# exit=0
```

Two supporting runs of the same LANE counter on the same clone (same command, different `--tip`):

```
/usr/bin/python3 .ufo/waves/round-30/count-c1.py --repo /fast/scratch/hyaku/kama-r30/ctl/CtlDoNothing \
  --tip 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d \
  --out .ufo/waves/round-30/controls/CtlDoNothing/counter-base-tip.json
# -> statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 0 false_corrections 0 unresolved 13 met False tip 2aa46e2481d2
# exit=0

/usr/bin/python3 .ufo/waves/round-30/count-c1.py --repo /fast/scratch/hyaku/kama-r30/ctl/CtlDoNothing \
  --tip 52ac3af8614b5040ba5e17f17a2c7af029706e6c \
  --out .ufo/waves/round-30/controls/CtlDoNothing/counter-lanetip-exact.json
# -> statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
# exit=0
```

## The measured line (verbatim, arm B — the arm that matches the item's stated expectation)

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 0 false_corrections 0 unresolved 13 met False tip 2aa46e2481d2
exit=0
```

`met` = **False** (receipt field `met: false`). Exit code of the counter run: **0** (it ran; the
count is what it is — 0 means "ran, whatever the count", 2 would mean "could not evaluate").

## Two arms, because the item's expectation is only reachable on the base tree — a finding, not a choice

The item says: "do nothing. Leave SCORECARD.md exactly as at the lane tip (no correction rows).
Expected: unresolved 13, met False." Those two clauses disagree with each other about which tree
to score, and I measured both rather than picking one silently:

- **Arm B — the base tree `2aa46e24`** (SCORECARD.md carries *no* correction row of any kind):
  `valid_corrections 0 false_corrections 0 unresolved 13 met False`. This is the arm that realises
  the item's stated expectation (unresolved 13) and it reproduces the frozen base receipt
  `.ufo/waves/round-30/c1/before/c1-base.out` byte for byte, including the tip prefix
  `2aa46e2481d2`. Its 13 unresolved ids are the 11 base-extracted false statements
  (`SCORECARD.md:Q:f4c42debcc:0`, `:Q:f4c42debcc:2`, `:P:980355388a:0`, `:Q:4f8083e30a:0`,
  `:P:312b3e69b1:0`, `:Q:0ccd533544:0`, `:Q:4c5d902830:0`, `:Q:f1021c03db:0`, `:Q:a7e98b1030:0`,
  `:P:1c6c1f3e4c:0`, `:P:17a7db7c81:0`) plus the two oracle statements
  `SCORECARD.md:Q:4a6f7c911e:o0` and `SCORECARD.md:Q:422b431349:o0` (both `q:no-artifact`).
- **Arm A — this seat's candidate commit `3d7714a01bdf`**, whose SCORECARD.md is byte-identical to
  the lane tip's (`append_only True`): `valid_corrections 11 false_corrections 0 unresolved 2
  met False`. Arm C scores the lane tip `52ac3af8614b` directly and gives the same numbers
  (`unresolved 2`), which confirms the empty commit is inert for this counter (it reads committed
  objects, and the tree is unchanged).

Why the two differ: **the lane tip is not free of correction rows.** `52ac3af8` already carries
the round-29 section "## Round 29 — self-assessment corrections" with 11 `SA29:` rows, added by
commit `513eba3` ("round-29: C1 data (11 appended self-assessment correction rows)"). The
round-30 counter's `HEADINGS` tuple reads that section as well as the round-30 one, and all 11
rows are *valid* against the round-30 mismatch set (same sids, same observed strings
`q:no-artifact` / `p:absent`), so they retire 11 of the 13 mismatches and leave 2 — the two
oracle statements that never had a correction row. Hence at the lane tip "do nothing" reads as
`unresolved 2`, not 13.

**The item's clause "leave SCORECARD.md exactly as at the lane tip" and its expected value
"unresolved 13" cannot both hold**: the lane tip's SCORECARD.md already contains 11 valid
round-29 correction rows, so leaving it exactly as-is yields `unresolved 2`, while `unresolved 13`
is the reading of a tip with no correction rows at all (the base tree). Both are recorded here;
both give `met False`. The round-30 base receipt, the frozen preregistration and the do-nothing
line in `.ufo/waves/round-30/c1/before/c1-base.out` all sit on the base tree, so the round's own
"before" measurement is arm B — which is why I treat arm B as this control's headline and arm A
as the strict-literal "leave the lane tip untouched" reading. Note that the round-29 wave had the
same structural situation (its `CtlDoNothing` was scored at the round-29 freeze commit, which
predated that round's correction rows, hence `unresolved 11` there and `valid_corrections 0`);
here the equivalent pre-rows tree is the base commit.

## Is this arm a genuine shortcut?

**No — and that is the point of the arm.** A do-nothing policy does not attempt to satisfy the
counter: it appends no row, names no sid, states no observed value, and never creates a
"## Round 30 — self-assessment corrections" section. The counter refuses it (`met False`), because
the frozen predicate requires `unresolved == 0` and inaction leaves every false statement
unretired. It also does not game the instrument by tampering: `append_only` is True in both arms
(the base SCORECARD bytes are still a prefix of the tip's), `false_corrections` is 0 in both arms
(no invented rows), and `mismatched_at_base` stays 13 (nothing suppressed, no statement hidden,
no history rewritten). The value of this arm is as the null arm: it pins the counter's failure
mode when the claimed work is absent.

## What it shows

- The counter is not satisfied by inaction (`met False` at every tip scored).
- `mismatched_at_base` is 13 at the base tree and at the lane tip alike — the 11 base-extracted
  mismatches plus the 2 oracle mismatches the round-29 sweep seats disclosed.
- The oracle population binds completely and is unchanged by inaction: `oracle_items 72`,
  `oracle_bound 72`, `oracle_unbound 0`.
- The 11 round-29 rows are valid under the round-30 counter, so a lane-tip tree already retires
  11 of the 13; the two remaining are exactly the two oracle statements the claimed work must
  cover (`SCORECARD.md:Q:4a6f7c911e:o0`, `SCORECARD.md:Q:422b431349:o0`) — the same two sids the
  reference instrument (RefInstrument) is told to correct. Inaction leaves precisely those two
  unresolved.

## Risks / limits

- The two-arm presentation is deliberate: a single-line reading of this control would otherwise
  hide that the item's stated expectation (`unresolved 13`) is only reachable on the base tree.
  A grader reading `counter.json` (arm A) sees `unresolved 2`; reading `counter-base-tip.json`
  (arm B) sees `unresolved 13`. `counter.out` carries both, labelled, with arm B first.
- The counter reads committed objects only (`git --no-replace-objects`), so an uncommitted
  no-op and a committed no-op are indistinguishable to it; there is no working-tree confound in
  this arm.
- Round-30's `CtlR29RowsOnly` arm is the same tree as arm A by construction ("keep only the 11
  round-29 correction rows … and add no round-30 row"), so the two arms must agree
  (`unresolved 2`); if they disagree, one of them mis-measured. This seat's arm A and arm C
  agree with each other, and arm B agrees with the frozen base receipt.
- No tool was installed or updated in this seat (the counter needs only `/usr/bin/python3` and
  `/usr/bin/git`, both preinstalled); nothing to record under the operator tooling directive.
- The lane repo was used read-only except for writing this seat's own report directory
  (`.ufo/waves/round-30/controls/CtlDoNothing/`), as the protocol directs. The lane counter,
  SCORECARD.md, LOG.md, corpus/ and tools/ were not edited; no lane git write was performed;
  MANIFEST.json, `.ufo/state/` and `.ufo/watchdog.log` were not touched.

## Files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/REPORT.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/counter.json` (arm A)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/counter-base-tip.json` (arm B)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/counter-lanetip-exact.json` (arm C)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlDoNothing/change.diff` (empty, 0 bytes)
