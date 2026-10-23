# CriticNoHarm — round 29 attempt 2, wave 2

## Scope and axes

Reviewed the working-tree delta against base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` in `/home/vgpnk/Projects/shokunin/kama-shokunin`, including committed round-29 changes and the inherited uncommitted document edits. `git rev-parse 2aa46e24 HEAD` returned that base and HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`.

Axes: operability, freshness, depth, coverage, calibration, adjacency. Also checked capability identity and promotion-mark preservation.

**Finding: no structural no-harm defect found in the assigned five-file comparison.** This is not a round-admission decision, calibration-axis-fit finding, or a rerun of C1.

## Observed delta

Commands executed, with the repository path above supplied to `git -C`:

- `git --no-pager diff --no-ext-diff --unified=6 2aa46e24 -- SCORECARD.md`
- `git --no-pager diff --no-ext-diff --unified=3 2aa46e24 -- LOG.md SHONEN.md corpus/QUALITY.md`
- `git --no-pager diff --no-ext-diff --unified=5 2aa46e24 -- corpus/SOURCES.md`
- `git --no-pager diff --no-ext-diff --word-diff=porcelain --unified=0 2aa46e24 -- SHONEN.md`
- `git --no-pager diff --no-ext-diff --numstat 2aa46e24 -- SCORECARD.md LOG.md SHONEN.md corpus/QUALITY.md corpus/SOURCES.md`

The numstat output was:

```text
27  0  LOG.md
63  0  SCORECARD.md
1   1  SHONEN.md
14  0  corpus/QUALITY.md
4   0  corpus/SOURCES.md
```

1. **Scores and capabilities preserved.** `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` has one append hunk, `@@ -1436,6 +1436,69 @@`, after the baseline EOF at line 1441. The axes table at lines 17–24 and capabilities table at lines 124–126 are unchanged. The added round-29 C1 row at line 1475 explicitly says `calibration 7 → 7 (no promotion by the author; closure rules)`. Lines 1497–1498 retain operability 8, freshness 8, coverage 9, depth 7, adjacency 7, and say `Capabilities: none claimed`. No pre-existing score, capability identity, or saturation declaration changed.

2. **LOG is a pure append.** `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:1834-1860` is the sole addition. Lines 1843–1844 explicitly retain calibration 7 and deny promotion. The baseline document is not rewritten.

3. **QUALITY is a pure append.** `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:278-291` adds KQ38 and KQ39. No prior criterion is deleted or edited. KQ38 at line 283 explicitly calls its earlier receipts prior falsifiers, not a retroactive rescore; KQ39 at line 289 explicitly says RefPaste does not settle calibration-axis fit.

4. **SOURCES is exactly four added rows.** `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:186-189` adds S174, S175, S176, S177, directly after S173. The complete diff contains no other additions or deletions. A targeted search for `^\| S17[4-7] \|` found exactly these four rows. Existing rows and subsequent sections are unchanged. This establishes the requested delta shape, not independent verification that the source pages were opened.

5. **SHONEN's only replacement is strictly corrective.** `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md:8` replaces:
   - `8 bad fake-server shapes rejected, frozen pair accepted 6`
   - with `8 adverse controls rejected: 7 bad server shapes + 1 injected teardown fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3 inconclusive`, plus the dated correction pointer.

   The `[~]` marks at lines 5, 7, 9, 11, the author-assertion attribution, lane-owned-control scope, and `no non-author mark` qualification are unchanged. This does not manufacture promotion or increase the historical control totals.

## Strongest candidate counterexample examined

**Candidate:** the in-place SHONEN edit could disguise a control-population change as improved operability or erase an adverse result.

Direct local evidence supports the narrower corrected wording instead:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:525-578` defines K1–K8; K6 at lines 558–564 is `kind='inprocess', shape='k0', inject='RuntimeError'`, not an eighth bad server shape.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json:2` records `accepted_bad: 6`. K1/K2/K4/K5/K8 have accepted receipts (lines 20–56, 75–117, 153–174). K6 at lines 118–135 has `accepted: true`, `escaped: true`, `receipt_written: false`, `gate_exit: null`, `tool_exit: 4`. K3 at lines 58–73 has `inconclusive: true`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/ShonenProvince.md:39-47` already distinguishes seven server shapes, the teardown-fault control, five accepted receipts, the receiptless escape, and K3's inconclusive outcome. The new wording preserves these distinctions rather than inventing them.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeShonenBox2/evidence.md:5-14` identifies the same static evidence and explicitly disclaims a new controls run.

**Result:** this candidate does not establish harm. The introduced qualifications are supported corrections; the numerical population and author-only status are not upgraded.

Also checked the possible append-only interaction statically: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:39-40,310-311` requires the tip SCORECARD bytes to begin with the base SCORECARD bytes; it does not apply that prefix guard to SHONEN. The observed SCORECARD diff preserves that prefix. `sha256sum` returned the assigned frozen counter identity `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`. This is not an executed C1 result for a future integrated tip.

## Impacted axes and smallest safe correction

- Demonstrated harmed axes: none in this scope.
- Operability/freshness/depth/coverage/calibration/adjacency: no score change; no capability or promotion upgrade.
- Smallest content correction required by this review: none.
- Calibration-axis suitability and round admission remain for the canonical judge; unchanged scores and append-only documents do not establish those conclusions.

## Evidence identity and limits

Working-document SHA-256 values observed with `sha256sum`:

```text
c1bd9cb7f85414b8cf026cc7ddd17cbbc8d1f1937854b6e74f03169d9bcd8b02  SCORECARD.md
c894150bf0242a208f9348305ec759cc900f799052a566661f88c4f96f38a57a  LOG.md
99f17aa4d2852ba8147a6c096b6d0f130a3e711818fadb51ad8e640cf9ed1c73  SHONEN.md
ce17f4beec25b48fa0e8abc55fc4f594ccf2d2c5390f3a2720c061a8d1c6d1ed  corpus/QUALITY.md
85d24ee1dc8c59563db3e2218ca0ad7d38293a60b05cd98629b8a8b46779f5ab  corpus/SOURCES.md
```

Only read-only diffs, searches, file reads, revision identification, and hashes were exercised. No counter, test, build, linter, formatter, controls suite, judge, or other agent runtime was invoked. No tools were installed. No lane source, Git index, jj state, or fleet state was changed.

The requested trailer destination `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/CriticNoHarm.md` is outside the assignment's hard write boundary. This full report is therefore written only at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-CriticNoHarm-3/report.md`; the integrator may place it at the trailer destination.
