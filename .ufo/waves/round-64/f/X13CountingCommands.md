# X13CountingCommands — measured-tip counting

Scope: re-derivation of the requested counts at `23b3fdb1a925129a9961cf551f6d40bf251602cb`; no claim verdict. Frozen claims read from `controls/freeze.txt`. The clean export was created under `/fast/scratch/hyaku/kama-r64/f/X13CountingCommands/tip` with `git archive` of that tip.

## Exact observed outputs

1. `sources-census.sh validate --file $S/tip/corpus/SOURCES.md` ended `file\tok\t/fast/scratch/hyaku/kama-r64/f/X13CountingCommands/tip/corpus/SOURCES.md`; it also emitted W04 duplicate-URL diagnostics and W01 S481 tierC-mind-used diagnostics. The separate requested count was `272`.
2. `digest-ledger.py scan`: `tokens=149 blob=130 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`
3. `hexrun-census.py scan`: `tokens=2094 distinct=406 lane_oid=283 md5_blob=1 upstream_ok=110 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0`
4. `round42-selfdesc-reconcile.py`: `tip=23b3fdb1a925129a9961cf551f6d40bf251602cb r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=1 mismatches=0 maxN=64 met=True`
5. `shortcut-tally.py --rounds 56-63` reported rows: r56 `disclosed:shortcut+survivor`; r57 `disclosed:shortcut+survivor`; r58 `disclosed:survivor`; r59 `disclosed:shortcut`; r60 `disclosed:shortcut`; r61 `disclosed:no-falsify`; r62 `disclosed:no-falsify+shortcut`; r63 `ok`. It emitted per-round details and the r61 no-results note in the command output.
6. `git diff --stat 0c1eff3c 23b3fdb1 -- tools registry | tail -3`:
   ```
    tools/round64-c2-counter.py         | 1825 +++++++++++++++++++++++++++++++
    tools/shortcut-tally.py             |  412 ++++++-
    8 files changed, 4492 insertions(+), 27 deletions(-)
   ```
7. `tools/kama-completion-live.py` diff stat from `0c1eff3c`: `1 file changed, 57 insertions(+), 2 deletions(-)` (59 lines). From freeze `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`: empty diff output (unchanged).

## Calibration observations

Neither scan reported an unknown entry: digest `unknown=0`, hexrun `unknown=0`. Thus no hex run or digest called unknown with a file:line. Counts above are outputs as observed; I did not independently interpret or judge them. Sources census produced numerous W04 duplicate URL warnings; these are warnings, not unknown scan entries.

No tools installed. No builds, tests, lint, formatter, or verification run.
