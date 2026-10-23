# ReviewRepairD5D6Notes — §Repairs items 5 and 6 fact review

VERDICT: holds — every cited fact in `corpus/lessons/round-27.md` §Repairs items 5 and 6 verifies against lane files, git objects and the fleet report; two low-severity citation-precision nits, no fabrication.

Scope: lesson `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-27.md` lines 49–69. All commands run read-only in `/home/vgpnk/Projects/shokunin/kama-shokunin` (tip 324d5d62). Fleet repo read-only. No writes outside this report and `w1a3/out/ReviewRepairD5D6Notes/` (created, unused — all evidence inline).

## Fact table — item 5 (receipt key mislabel)

| # | Claim (round-27.md:49–58) | Evidence | Result |
|---|---|---|---|
| 5a | `final/c1-tip.out:2` and `final/c2-kq36-tip.out:2` read `tree=7e5ff9b5…` | `.ufo/waves/round-26/final/c1-tip.out:2` = `exit=0 tree=7e5ff9b5454dd27f0520cb36a3cbc3a995e48162`; `c2-kq36-tip.out:2` identical | holds |
| 5b | `git cat-file -t 7e5ff9b5` → `commit` | `git cat-file -t 7e5ff9b5` → `commit` (exit 0); full id `7e5ff9b5454dd27f0520cb36a3cbc3a995e48162` | holds |
| 5c | its tree is `f2a981ee…` | `git rev-parse 7e5ff9b5^{tree}` → `f2a981ee8cd405006214fb5b51cd235f34ca8ba8`; `cat-file -p` line 1 = `tree f2a981ee…` | holds |
| 5d | fleet report `kama.md:152-153` rejected AttackE2610 on the ground that `7e5ff9b5` is a commit | `/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/kama.md:152-154`: "Falsify finding rejected: AttackE2610 said the receipt's `tree=7e5ff9b5` is another commit's tree; `git cat-file -t …` prints `commit`." | holds (nit N1: the `commit` verdict word prints on :154, one line past the cited range) |
| 5e | AttackE2610's finding (`advice/AttackE2610.md:79`) was that the receipt names a revision other than landed f4066979, and it inverted the relation | `.ufo/waves/round-26/w2-falsify/advice/AttackE2610.md:79`: "records `tree=7e5ff9b5...`; the landed commit f4066979 has tree `6e6fb5f5...`. `git log --all` shows 7e5ff9b5 is the tree of commit f2a981ee." Seat said 7e5ff9b5 is *the tree of* f2a981ee; reality: f2a981ee is the tree *of commit* 7e5ff9b5. Inversion confirmed. `git rev-parse f4066979^{tree}` → `6e6fb5f5…` matches the seat. `git merge-base --is-ancestor 7e5ff9b5 f4066979` → true; f4066979 ancestor of HEAD and of a720399e | holds |
| 5f | mislabel stands (spot-check line 197); round-26 files not edited | `corpus/lessons/round-26-verifier-spotcheck.md:197`: "…leaves the real mislabel standing: `final/c1-tip.out:2` and `final/c2-kq36-tip.out:2` put a commit id under `tree=`. There is no row impact." `git status --porcelain -- .ufo/waves/round-26/` → 0 lines; only commit touching both receipts is `3550523` (round-26 era); so files byte-unchanged | holds |
| 5g | "The key should read `commit=`" | [INFERENCE] both files carry a commit id under `tree=`; consistent with receipt commit msg `3550523` "landed-tip receipts (C1 counted 17 at 7e5ff9b5…)" | holds |

Corroborating: `w2-falsify/out/AttackE2610/` absent (`ls` → 0 hits), matching spot-check :197.

## Fact table — item 6 (Gate reject reasons)

| # | Claim (round-27.md:59–69) | Evidence | Result |
|---|---|---|---|
| 6a | `lessons/round-26.md:63` held the metrics message "at base" via ScoutMetricsSource.md "and two round-18 advice files" | `corpus/lessons/round-26.md:63` reads exactly that (one round-16 file + "two round-18 advice files") | holds |
| 6b | Actual count is **three** round-18 + **three** round-16 advice files | `git grep -l 'does not support metrics' a720399e -- .ufo/waves` → the six named files all match (ProbeArgvEffects.md:32,249,…; ScoutLlamaMetricsProps.md:33,36; ScoutLlamaNewerTags.md:77; CriticC2ToyModel.md:51; RevengerRound1Live.md:201; ScoutMetricsSource.md:19,39,59). Same command at round-26 base `1560e4d8` → 11 paths, of which advice files are exactly those six | holds |
| 6c | Spot-check line 195 supports the repair | `round-26-verifier-spotcheck.md:195`: "`invalid_request_error` has about 49 call sites, but `authentication_error` has exactly one fault (the invalid-key 401), so 'shared by many faults' is false for that half"; :193 corrects only the round-18 count ("two → three") | holds — and repair item 6 goes further than :193: the spot-check's own grep at base found only ScoutMetricsSource.md among round-16 advice, yet all three round-16 files contain the message at 1560e4d8 and a720399e; the repair's "three and three" is the correct ground truth |
| 6d | CriticAxisFit called its point "a measured caveat, not a kill" (`round-26/w1-build/advice/CriticAxisFit.md:105`) | CriticAxisFit.md:105 verbatim: "Given the counter is frozen, this stays a measured caveat, not a kill." | holds |
| 6e | reject was L1 discretion | [INFERENCE] sound: the seat explicitly declined to kill (:92 "does **not** flip the axis"), so citing its caveat as reject reason overstates it | holds |
| 6f | `authentication_error` has one fault (invalid-key 401); "shared by many faults" true only of `invalid_request_error` | Pinned sources `.ufo/waves/round-26/sources/llama.cpp-704366d/`: `authentication_error` literals at server-common.cpp:100 (`case ERROR_TYPE_AUTHENTICATION:`), server-http.cpp:295 (the `"Invalid API Key"` 401 envelope), README.md:2328; `grep ERROR_TYPE_AUTHENTICATION` → only the :99 `case`, zero call sites, so the label is emitted by exactly one fault (server-http.cpp:295). `ERROR_TYPE_INVALID_REQUEST` → 52 mentions across the tree | holds |
| 6g | `round-26.md:67` called both labels "error-type labels shared by many faults" | Verified verbatim at :67 | holds |

## Findings (by severity)

- **N1 (low):** item 5 cites `kama.md:152-153` for the rejection ground, but the decisive "`prints `commit`" lands on :154. The rejection sentence starts at :152, so the cite is defensible; a `:152-154` range is tighter.
- **N2 (low):** item 6's parenthetical `git grep -l 'does not support metrics' a720399e -- .ufo/waves` returns 57 paths, not the six named — the "three and three" count is the advice-file subset. At base `1560e4d8` the same command returns 11 paths with exactly those six advice files, so naming the base revision or filtering `advice/` makes the citation airtight. Descriptively the claim is correct at both revisions.

No other defects. The repairs are descriptive (round-26 files untouched, confirmed clean), so every repair obligation is met by accurate prose — which it is.

## Commands run (all exit 0 unless noted)

- `git cat-file -t 7e5ff9b5` → `commit`; `git rev-parse 7e5ff9b5^{tree}` → `f2a981ee8cd405006214fb5b51cd235f34ca8ba8`
- `git rev-parse f4066979^{tree}` → `6e6fb5f591615e910954e374e60ce98ed5e2021a`
- `git merge-base --is-ancestor 7e5ff9b5 f4066979` → true; `f4066979` ancestor of `a720399e` → true
- `git grep -l 'does not support metrics' a720399e -- .ufo/waves` → 57 paths (6 advice, as named)
- `git grep -l 'does not support metrics' 1560e4d8 -- .ufo/waves` → 11 paths (6 advice, as named)
- `git status --porcelain -- .ufo/waves/round-26/` → 0 lines; `git log --oneline -- .ufo/waves/round-26/final/*.out` → only `3550523`
- `grep -rn authentication_error .` in pinned sources → 3 hits (2 code, 1 README); `ERROR_TYPE_AUTHENTICATION` → 1 hit (the switch `case`); `ERROR_TYPE_INVALID_REQUEST` → 52 hits

## Residual risk / verification gaps

- "At base" in the repair was verified at `1560e4d8` (the base revision the spot-check itself greps at :193) and at `a720399e` (the integrator commit the repair cites); both agree. No other base candidate exists.
- The `invalid_request_error` "many faults" half is supported by 52 enum mentions; the exact "about 49 call sites" figure from spot-check :195 was not independently recounted (enum mentions include non-call-site lines) — consistent, not byte-exact.
- No tools installed; no installs needed.
