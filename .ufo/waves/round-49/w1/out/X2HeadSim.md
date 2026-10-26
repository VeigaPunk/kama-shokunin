# X2HeadSim — round 49 pre-integration check: does append-only-audit v4 survive the round-49 head rewrite?

**Verdict:** v4 stays exit 0 at the simulated round-49 integration, on every shape I measured (round-47/48-shaped head rewrite; head rewrite plus the PROVINCE/coverage re-anchors the gate actually requires; and with a banner replaced *without* being appended). The frozen C2 counter is `met=True` at each of those commits. v4 grades **only two kinds of head edit**: the authority banner at SCORECARD.md:6, and an in-place reword of an *earlier round's* canonical capability rows (parent section = `## Round …`). Both are invisible in practice because the integration commit deletes 8–9 lines, far below the tool's 20-line event threshold — so the head rewrite is safe *by the threshold*, not by the carve-out.

- **Does v4 stay exit 0?** Yes — `append-only-audit.py --to HEAD` exit 0 (`events=5 restored=5 regressed=0 ungraded_lines=82`) and `round49-append-audit-v4-check.py` `fixture=1 lane=1 scenarios=8/8 met=True` (exit 0) at the simulated integration commit and at the final one.
- **Which head edits would v4 grade?** The banner (always, once the commit is an event) and an in-place reword of the round-48 canonical rows (parent section `## Round 48 — …`, non-exempt). Every other head edit is ungraded: `## Axes` rows and `§Planned` pointer (exempt section + exempt origin), the `## Capabilities` mirror intro and rows (exempt twice). An appended byte-exact banner copy restores the banner line (`restored_max=1 held_at_to=1`) — the same mechanism round 48 established.
- **New integration requirement (not in the known list):** the head rewrite cannot pass `tools/round42-selfdesc-reconcile.py` unless PROVINCE.md's instruments cell names both round-49 counters (`province=2 met=False` otherwise), and once PROVINCE.md is edited its sha256 must be re-anchored in the coverage row (`r41=1` otherwise). With both, `mismatches=0 met=True`. Also, the head is **already red at the build tip** for the calibration row (spot-check count 34 vs 35), so the round-49 head re-anchor is a repair, not cosmetic.
- **Pre-existing red gate carried into round 49:** `tools/hexrun-census.py` is `unknown=2` at the base 438127bc, at the build tip, and at the simulated integration: the two 40-hex runs at `corpus/lessons/round-48-verifier-spotcheck.md:21`.

Nothing here edits the lane, the counters, the preregistration or the controls. All work is in my scratch clone (`git clone --shared`), which is deleted.

## 1. Setup and what "the integration" was

```
S=/fast/scratch/hyaku/kama-r49/X2HeadSim; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane rev-parse HEAD   -> 122c4ee95701587cef7f4342c3d175622ec2f4ad
```

Disclosure: the clone's HEAD is `122c4ee9` ("round-49: wave spec kama-r49-w1 … and freeze-time check"), i.e. the build `74558c71` plus one commit that adds four `.ufo/waves/round-49/**` files and **deletes nothing** (`git diff --numstat 74558c71 122c4ee9` → `5/0`, `218/0`, `1121/0`, `664/0`). Every instrument receipt below was taken both at `74558c71` where relevant and at the simulated integration commits, so the comparison is like-for-like. Integration lands on the lane tip, not on the build, so this is the faithful base.

Fixture identity for every commit (asserted `git rev-parse --show-toplevel` = `$S/lane` before each):
`-c user.name=r49x2-fixture -c user.email=r49x2-fixture@invalid -c commit.gpgsign=false`.

| commit | what it is |
|---|---|
| `904c1525ef95292c71bdfd14e36c3028cc047fa2` (**A**) | the head rewrite + `## Round 49` section, round-47/48 shape; `SCORECARD.md 52/8` |
| `000d2989eb24ab688261864e80a7ff2cb92747c4` (**C**) | fixture: banner replaced again (round 49 → "round 50") and **not** appended |
| `70f6cb4dda661695bd1ea1a316f17ea08eddb04c` (**D**) | fixture: the round-49 banner appended byte-exact under a superseded block |
| `34f90e9d5218c99a25efaa7642603588f736bfbf` (**E**) | PROVINCE.md instruments cell + head banner restored + fixture banners kept |
| `2d5e4cc33ceaeaec2495313f2ec126822899c0c9` (**F**) | coverage row re-anchored to the edited PROVINCE.md — the final simulated integration |
| `c4b2175d2ff9466beaed039dc8330176362e7d82` | the *real* round-48 integration, used as the precedent |

The head rewrite itself (`head-rewrite.patch`, `git diff 74558c71 F -- SCORECARD.md PROVINCE.md`, 63/9 + 1/1) is:

- `SCORECARD.md:6` banner round 48 → round 49 (round-49 wording, "kept current in rounds 43, 44, 45, 46, 47, 48 and 49");
- the round-48 banner appended **byte-exact** under `### Superseded head banners (kept verbatim; round 49)` (`git show 74558c71:SCORECARD.md | sed -n 6p`, 979 bytes + newline);
- `## Axes` re-anchors that the tree actually moved: the calibration row (`corpus/lessons/*verifier-spotcheck.md` count `34`→`35`, latest outside closure `round-48-verifier-spotcheck.md`, "re-anchored round 49") and, after PROVINCE.md was edited, the coverage row's PROVINCE sha256;
- `## Planned` pointer `### Planned (round 49)` → `### Planned (round 50)`;
- the `## Capabilities` mirror intro re-pointed at the round-49 canonical list, with the two reworded rows (v4; witness + bounded member);
- `## Round 49 — …` appended with the frozen claims table, the controls paragraph, the round-49 canonical list (11 rows) and `### Planned (round 50)`.

Deliberate honesty about `### Round-49 measured results`: it is a one-paragraph placeholder ("Pending. This section was committed by the pre-integration head-rewrite check …"). I have no round-49 measurement, so the section does not claim one; the real integrator replaces that paragraph.

Why the re-anchors are *this* small: at the integration tip, `SKILL.md` (sha256 `d5ed2295…`, 1484 lines, `grep -c '^## '` 36), `PROVINCE.md` (186 lines) and `corpus/knowledge/endpoint-identity.md` (`0100ac6d…`, 218 lines) are unchanged from round 48, and the operability row's run facts re-derive identically (`bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`; `tools/pin-watch.py selftest` → `pass=9 fail=0`; `tools/report-landing-audit.py --selftest` → `cases=79 failed=0`; `tools/sources-append-only.py --selftest` → `45/45`; `tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0`; `tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0`). Only the calibration row (spot-check 34→35) and the PROVINCE sha moved. Round 48 touched 8 head lines because its build changed SKILL.md and PROVINCE.md; round 49's build changed neither.

## 2. The frozen C2 counter at the simulated integration — `met=True`

```
python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip <commit> --scratch $S/c2 --out <receipt>
```

| tip | receipt | exit | line |
|---|---|---|---|
| `74558c71` (build) | `c2-build-tip.out` | 0 | `fixture=1 lane=1 scenarios=8/8 met=True` |
| `904c1525…` (**A**) | `c2-A.out` | 0 | `fixture=1 lane=1 scenarios=8/8 met=True`; `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82`; `event dd9f5dc6c0e6 … ungraded 17 <= natively exempt 23`; `event 0718b6abbda6 … ungraded 65 <= natively exempt 65` |
| `000d2989…` (**C**) | `c2-C.out` | 0 | `met=True`, identical lane detail |
| `70f6cb4d…` (**D**) | `c2-D.out` | 0 | `met=True` |
| `2d5e4cc3…` (**F**) | `c2-F.out` | 0 | `met=True`, identical lane detail |

`ungraded_lines 82` = 65 (`0718b6ab`) + 17 (`dd9f5dc6`). The lane's own pre-build control, `.ufo/waves/round-49/controls/base.c2.out` (taken at `438127bc`), reads 89 = 72 + 17, so the round-49 v4 grading of 7 lines is exactly preserved by the integration — the head rewrite neither adds nor removes an event, and the two `SCORECARD.md` events keep their native counts.

`tools/append-only-audit.py --repo $S/lane --to HEAD` (default threshold 20), same commits:

| tip | receipt | exit | summary |
|---|---|---|---|
| **A** | `aoa-default-A.out` | 0 | `commits=321 files=92 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=82 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0` |
| **C** | `aoa-C-default.out` | 0 | `events=5`, same summary shape |
| **F** | `aoa-F-default.out` | 0 | `commits=325 … events=5 restored=5 … regressed=0 … bad_declarations=0` |

So the integration commit is not itself an event (8 deletions at A, 9 cumulative at F, threshold 20), and nothing it deletes is graded or lost at the default threshold.

## 3. Which head edits would v4 grade — per deleted line

Helper: `head-del-detail.py` (in this directory) recomputes only the v4 definitions the tool uses for a single `(commit, file)` pair — parent section per deleted position, `origin(l)`, exempt-title membership — and reproduces the tool's own `graded` count exactly (A: `graded=3`, tool `graded=3`).

Cross-check with the tool itself at `--threshold 1` (a documented CLI option; analysis only, not the counter):

| commit | receipt | event line |
|---|---|---|
| **A** `904c1525` | `aoa-threshold1-A.out` | `deleted=8 graded=3 ungraded=5 restored_max=1 held_at_to=1 status=partial` |
| **C** `000d2989` | `aoa-C-threshold1.out` | `deleted=1 graded=1 ungraded=0 restored_max=0 held_at_to=0 status=unrestored` |
| **D** `70f6cb4d` | `aoa-D-threshold1.out` | `event 000d2989eb24 … restored_max=1 held_at_to=1 status=restored restored_best=70f6cb4dda66 restored_by=70f6cb4dda66` |
| **E** `34f90e9d` | `aoa-E-threshold1.out` | `deleted=1 graded=1 ungraded=0 restored_max=1 held_at_to=1 status=restored` (the round-50 fixture banner, held by its appended copy) |
| `c4b2175d` (real round-48 integration) | `head-del-detail-c4b2175d.out`, `aoa-threshold1-A.out` | `deleted=8 graded=1 ungraded=7 … status=restored` |

Per-line classification at **A** (`head-del-detail-A.out`):

```
parent:6     parent_section=None          origin=[]                GRADED
parent:18    parent_section='## Axes'     origin=['## Axes']       ungraded   (calibration row)
parent:53    parent_section='## Planned'  origin=['## Planned']    ungraded   (pointer to round 50)
parent:117   parent_section='## Capabilities' origin=['## Capabilities'] ungraded (mirror intro)
parent:130   parent_section='## Capabilities' origin=['## Capabilities','## Round 48 — …'] ungraded (mirror append-only-audit row)
parent:131   parent_section='## Capabilities' origin=['## Capabilities','## Round 48 — …'] ungraded (mirror replay row)
parent:2790  parent_section='## Round 48 — …' origin=['## Capabilities','## Round 48 — …'] GRADED (round-48 canonical append-only-audit row)
parent:2791  parent_section='## Round 48 — …' origin=['## Capabilities','## Round 48 — …'] GRADED (round-48 canonical replay row)
graded=3 ungraded=5
```

Reading it:

1. **The banner is the one head line v4 always grades.** Its parent section is `None` (before the first `## `), so it cannot be exempt; a commit that deletes it and is an event is `ungraded=0` on that line. `restored_max=1` at A, D and E comes from the byte-exact appended copy: at **D** the deletion is `restored` (`restored_by=70f6cb4d`), and at **C**, where the fixture replaced the banner and appended nothing, the same line is `graded=1 … status=unrestored`, so round 48's device still works under v4 and its absence is still visible.
2. **`## Axes` re-anchors are ungraded by design** — parent section exempt *and* origin exempt. That is the carve-out working: the head may be re-derived in place.
3. **The `## Capabilities` mirror is ungraded even when its rows are reworded**, because both the parent section and the first-appearance title are exempt. The mirror therefore cannot launder a canonical row: deletion of the *canonical* copy is still graded by the parent-section test (2790/2791 above), which is the correct outcome — v4's two-condition rule (`parent section exempt AND origin ∩ exempt`) closes the K1Regions hole for the head/canonical pair.
4. **The refusal path is real but unreachable at integration scale**: at **C** the lost banner is graded (`graded=1 status=unrestored`, exit 1 at threshold 1) while the frozen counter is still `met=True` and the default audit still exits 0. That is the round-48 seat L1Lowthr sub-threshold boundary on the exact path this round's integration walks: a round that replaces the banner and forgets the append is caught by nothing the integration runs.

One deviation to disclose: my A commit reworded the two rows in **both** the mirror and the round-48 canonical list (a single `replace_all` edit), which the round-47/48 precedent does not do (their previous canonical list stays byte-intact). That is what makes A `graded=3` and `status=partial` instead of `graded=1 status=restored` like `c4b2175d`. The measured lesson stands either way: an in-place reword of a previous round's canonical rows is graded; appending a new canonical list leaves the old one byte-intact and nothing is graded. **Recommendation for the integrator: append the round-49 canonical list; do not reword the round-48 one.**

## 4. Gates the integration must also satisfy (measured, and not in the given list)

`python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip <commit>`:

| tip | receipt | exit | line |
|---|---|---|---|
| `74558c71` (build) | `selfdesc-build.out` | 1 | `r41=1 … mismatches=1 met=False`; `detail: r41 calibration run …verifier-spotcheck… no stdout line == '34' (exit 0)` |
| **A** (head rewrite only) | `selfdesc-A.out` | 1 | `r41=0 … province=2 … mismatches=2 met=False`; `province: PROVINCE.md lacks tools/round49-append-audit-v4-check.py (capability append-only-audit)`; `… lacks tools/round49-replay-witness-audit.py (capability live-receipt-replay)` |
| `34f90e9d` (**E**) | — | 1 | `r41=1 … mismatches=1`: `r41 coverage sha256 PROVINCE.md cited aa7915a8… observed 8ec1bef7…` |
| `2d5e4cc3` (**F**) | `selfdesc-F.out` | 0 | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=49 met=True` |

Three consequences, all new relative to the integration items I was given:

1. **The head is red at the build tip.** `corpus/lessons/round-48-verifier-spotcheck.md` (the base commit `438127bc`) makes the spot-check count 35 while the calibration row still says 34, so `r41` fails before the integration starts. The calibration row re-anchor is a **repair** the integration performs, not a cosmetic re-anchor. (`SCORECARD.md:18`.)
2. **PROVINCE.md is a required integration target.** The round-49 capability rows cite `tools/round49-append-audit-v4-check.py` and `tools/round49-replay-witness-audit.py`; `round42-selfdesc-reconcile.py` requires the instruments cell (`PROVINCE.md:17`) to name them, and it does not (`province=2`). The fix I validated is the same shape round 48 used: append the counter names into the `tools/append-only-audit.py` parenthetical and add `tools/round49-replay-witness-audit.py` after `tools/kama-live-replay.py` (see `head-rewrite.patch`).
3. **Editing PROVINCE.md breaks the coverage row.** Its sha256 and line count are cited (`SCORECARD.md:17`); after the edit the sha256 is `8ec1bef74888ffcfc4b10d79474906c4067d4ebe72adb4af25260528ba8c9fce` (186 lines, unchanged) and `r41` fails until it is re-anchored. Two `## Axes` deletions, both ungraded by v4.

Other gates at **F**: `tools/capability-repertoire-audit.py --repo . --tip HEAD` → `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (exit 0, `caps-F.out`) — the appended round-49 canonical list resolves as the highest canonical heading with 11 rows; `tools/digest-ledger.py scan --repo .` → `tokens=129 blob=113 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` (exit 0, `digest-F.out`).

## 5. Pre-existing red gate carried into round 49 (not caused by the build or by me)

`python3 tools/hexrun-census.py scan --repo <clone> --rev <commit>` exits 1 at all three of `438127bc` (base), `74558c71` (build) and HEAD=**F**:

```
tokens=1833 distinct=296 lane_oid=190 md5_blob=1 upstream_ok=92 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=2
detail: 15710a2a8286bf12d55d943f17028178fe8d421a len=40 occurrences=1 class=unknown
detail: dcc079e7e56d3312ec70e0bd5b3c7f885b1242e8 len=40 occurrences=1 class=unknown
```

Both runs occur once, in `corpus/lessons/round-48-verifier-spotcheck.md:21`, in the identity row's `git log --format='%an <%ae> | %H %ci %s' -- .ufo/reports/round-48/kama.md` output — i.e. **fleet-repo** commit ids, which are not lane objects and so classify `unknown`. Receipts: `hexrun-base.out`, `hexrun-F.out`. The round-48 measured record claims `hexrun-census unknown=0` at `c4b2175d`; the closure lesson that landed at `438127bc` is what reddens it. Fix (integration's call, not mine): two `registry/hexrun-ledger.tsv` rows declaring them unverifiable-from-the-lane with the reason, or a pointer sentence next to the citation.

## 6. Risks, limits, non-findings

- **Scale of evidence.** Every number above is from my own runs in my own clone; the receipts named are in this directory. Fixture commit ids are **not** lane objects and must never be cited in lane text — my `### Superseded head banners` notes cite only short prefixes (`904c1525ef95`, `000d2989eb24`, `70f6cb4d`), which the hex-run census (32–127 chars) does not count; a real integration must cite the real lane ids only. I checked that these notes did not add unknown runs (unknown stayed 2, and its members are the two round-48 lesson runs above).
- **A remains `partial` at threshold 1** (`restored_max=1` of `graded=3`) because of the disclosed `replace_all` deviation (round-48 canonical rows). At the default threshold the commit is not an event, so this is invisible; the faithful pattern (`c4b2175d`) is `graded=1 … status=restored`.
- **The carve-out is positional.** `section()` is the last `## ` title at or before a line, so any incidental `## …` heading inside the head silently de-exempts everything after it. The tree shows the mechanism at work: at `383f1fc7`, `## Seat notes — S2Events (not part of the section text above)` sat at line 2580, and two mirror rows' recorded origins carry that title. A stray seat note placed at the top of SCORECARD.md would turn head deletions into graded ones (fails closed, not open) — but it also means the exempt set is not a property of the *text*, only of its position history.
- **`### Round-49 measured results` is a placeholder.** Do not mistake this simulation for the measurement; the C1/C2 claims are unmeasured here (I ran neither `round49-replay-witness-audit.py` nor any llama-server).
- **Non-findings, deliberately not reported again.** SKILL.md's instrument registry, the SCORECARD/LOG/lesson/QUALITY/README round-49 entries and `corpus/lessons/round-49.md` (named by S494/S495 `used-by`) are the known scribe items; my simulation deliberately did not touch them, and the head counters above do not depend on them.

## 7. Reproduction (exact commands, in order)

```
S=/fast/scratch/hyaku/kama-r49/X2HeadSim; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
# apply head-rewrite.patch to SCORECARD.md and PROVINCE.md, then:
git -C "$S/lane" -c user.name=r49x2-fixture -c user.email=r49x2-fixture@invalid \
    -c commit.gpgsign=false commit -qam "round-49 integration simulation"
git -C "$S/lane" rev-parse HEAD                       # 2d5e4cc3… after the fixture commits
python3 tools/append-only-audit.py --repo "$S/lane" --to HEAD                  # exit 0
python3 tools/append-only-audit.py --repo "$S/lane" --to HEAD --threshold 1    # exit 1, analysis only
python3 tools/round49-append-audit-v4-check.py --repo "$S/lane" --tip HEAD --scratch "$S/c2" --out "$S/c2.out"
python3 tools/round42-selfdesc-reconcile.py --repo "$S/lane" --tip HEAD        # exit 0 at F only
python3 tools/capability-repertoire-audit.py --repo "$S/lane" --tip HEAD       # listed 11 observed 11 met True
python3 tools/digest-ledger.py scan --repo "$S/lane"                           # unknown=0
python3 tools/hexrun-census.py scan --repo "$S/lane" --rev HEAD                # exit 1, unknown=2 (pre-existing)
```

`head-del-detail.py` reproduces §3 for any commit: `python3 head-del-detail.py --repo "$S/lane" --commit <rev>`.

No tools were installed or upgraded for this seat (nothing was needed); no llama-server was started, so `pgrep -f llama-server` was never applicable; the scratch clone and `$TMPDIR` were removed before this report was written.

## 8. Blockers

None. The two things I could not measure are the round-49 claims themselves (out of scope for this seat: no witness counter run, no server started) and the real integrator's final head text (I modelled it from the round-47/48 precedent and the tree's measured values).
