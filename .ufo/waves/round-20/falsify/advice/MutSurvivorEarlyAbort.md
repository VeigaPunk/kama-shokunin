VERDICT: confirm - the completion-witness guard prevents this false kill; deleting it is caught by the early-abort control.

## Mutant and expected detector
- Scope: one private copy of `.ufo/waves/round-18/c2/survivors.py`; no lane source, registry, or committed evidence edits.
- Mutation: delete exactly source lines 976-977 inside `selftest_arm`:
```python
    if not selftest_enumeration_matches(base_run, run):
        return "inconclusive", "selftest did not enumerate the baseline case set"
```
- The named-target test at source lines 978-987 remains intact. This is one behavior-bearing guard removal, not a change to the expected contract.
- Pinned control: `registry/error-injection-fixtures/survivor-arm-probe.py:12-35`, copied unchanged into scratch; SHA-256 `bf031256913317e688362adc0f663f6fce77228eba00a265c11adfc8deb95014`.
- These are fixed subprocess-record replays, not newly executed selftest processes: baseline exit 0, stdout `10/10 selftest cases passed\n`; both subject records exit 1 and contain `FAIL target assertion\n`.
- Early-abort record has no summary; positive control appends `9/10 selftest cases passed\n`. Only the latter may be credited as a kill.
- `tools/error-verdict-census.py:208-216` maps arm `inconclusive` to `could-not-evaluate`; registry cells at `registry/error-injection-cells.json:15-16` pin these two expected classes.

## Exact commands and observed outputs
Same bounded detector command on pristine, mutated, and restored bytes (cwd `/tmp/kama-r20-MutSurvivorEarlyAbort`, outer timeout 30 s):
```sh
/usr/bin/python3 /tmp/kama-r20-MutSurvivorEarlyAbort/detector.py
```
Detector executes these exact commands, each with timeout 10 s:
```sh
/usr/bin/python3 /tmp/kama-r20-MutSurvivorEarlyAbort/survivor-arm-probe.py /tmp/kama-r20-MutSurvivorEarlyAbort/lane/.ufo/waves/round-18/c2/survivors.py early-abort
/usr/bin/python3 /tmp/kama-r20-MutSurvivorEarlyAbort/survivor-arm-probe.py /tmp/kama-r20-MutSurvivorEarlyAbort/lane/.ufo/waves/round-18/c2/survivors.py complete-target-failure
```
Detector requires respectively `inconclusive` and `killed`, returning 0 for that pair, 1 for a mismatch, and 2 for execution/parse/pinned-fixture errors. Its unchanged SHA-256 was `855003e44fc6e42dd06fba2adf3687b1ae0b51a3fbdbf6a97d90aca78f80ff29` in all three runs.
| Subject bytes | Early-abort outcome | Positive-control outcome | Detector exit |
|---|---|---|---|
| Pristine | inconclusive | killed | 0 |
| Mutated | killed (false credit) | killed | 1 |
| Restored | inconclusive | killed | 0 |
All six fixture invocations exited 0 with empty stderr. Exact stdout JSON for pristine/restored early-abort:
```json
{"outcome": "inconclusive", "reason": "selftest did not enumerate the baseline case set"}
```
Exact stdout JSON for mutated early-abort and all three positive controls:
```json
{"outcome": "killed", "reason": "targeted selftest assertion failed: target assertion"}
```
Mutation verdict: **killed** by the bounded detector (0 -> 1 -> 0), specifically because the removed guard falsely credits the early abort. No baseline failure or infrastructure failure occurred. This confirms only the assigned control, not an exhaustive selftest-completion guarantee.

## Restoration and cleanup evidence
- SHA-256 before: `c4c29c5a1d5d8a3981bfff58934d59c03cbb8f76f1dcf540edd8556ec4813890`.
- SHA-256 mutated: `0a05e7b35592dc77d4c7ec0c37de3d9de84c96a0bb00d3f867173670bd456dce`.
- Restored the captured two lines exactly; SHA-256 after: `c4c29c5a1d5d8a3981bfff58934d59c03cbb8f76f1dcf540edd8556ec4813890`.
- `cmp -- /tmp/kama-r20-MutSurvivorEarlyAbort/survivors.pristine.py /tmp/kama-r20-MutSurvivorEarlyAbort/lane/.ufo/waves/round-18/c2/survivors.py` and `cmp -- /tmp/kama-r20-MutSurvivorEarlyAbort/survivors.pristine.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py` both exited 0; `sha256sum` printed the same restored digest for all three files.
- `rm -rf -- /tmp/kama-r20-MutSurvivorEarlyAbort && test ! -e /tmp/kama-r20-MutSurvivorEarlyAbort && printf 'scratch_removed=true\n'` exited 0, output `scratch_removed=true`.
- No full survivors suite, server, model load, Git/JJ operation, install, or tool update was performed.

Report: .ufo/waves/round-20/falsify/advice/MutSurvivorEarlyAbort.md
