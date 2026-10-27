# Z01CheckerDeadWeight — round 58 dead-weight review

Axes: operability (C1 checker/counter), calibration (C2 counter). Advisory seat: no lane file edited; measured
blobs read at e4891d8a4c9c70e97124980c2ec9aee5762a7f0a. Scratch `git clone --shared` under
/fast/scratch/hyaku/kama-r58/Z01CheckerDeadWeight (one clone, removed). Tools used: pyflakes, vulture, ruff
(already installed; no installs).

## Verdict — 6 verified deletions, receipts byte-identical
- `tools/round58-c1-counter.py`: `import json` (pyflakes F401; 150 -> 149 lines). Attacks the C1 counter file.
- `tools/round58-battery-exec-check.py`: write-only crash record (`err = None`, `as exc` capture, `"error": err`
  key). Its only consumer reads `["frames"]`; repo-wide, nothing reads `result.json` or that key. 219 -> 214.
- `tools/round58-battery-exec-check.py`: `FakeTD.cleanup` — no `.cleanup(` call site in any of the 15 variants;
  a variant that calls it is still accepted (item 5b). Attacks the C1 checker file.
- `tools/round58-battery-exec-check.py`: `subprocess.check_output` lambda — CPython 3.14.8 `check_output`
  delegates to the module-global `run` (`inspect.getsource`; direct probe printed `RECORDED`), so the lambda is
  redundant once `run = fake_run` is installed. Attacks the C1 checker file.
Proposed bytes (not applied): `out/Z01CheckerDeadWeight/check-rec.py` (sha256 6dcdc53a...), 
`out/Z01CheckerDeadWeight/round58-c1-counter.pruned.py` (sha256 0d200b1c...).

## Evidence (exact command -> output, exit)
1. `python3 tools/round58-c1-counter.py --repo <clone> --tip e4891d8a... --checker tools/round58-battery-exec-check.py`
   -> `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0 (c1-pristine-buildtip.out).
2. Same with the pruned counter -> full 16-line receipt byte-identical (`diff` empty), exit 0.
3. Same with `--checker check-rec.py` -> receipt byte-identical, exit 0; checker line identical too.
4. `python3 check-rec.py --repo <clone> --tip e4891d8a...` -> `present=1 roster_match=1 kills=1 controls=2
   executed=1 legs=3/3 mutant_assert=1 met=True`, exit 0.
5. Controls at tip dcd694 (receipts from cb1ef102), pruned counter, all exit 1, each `diff` empty:
   base-r57 `genuine=1/1 benign=1/3 noop=1/11 met=False`; always-accept `noop=0/11`; always-reject
   `genuine=0/1 benign=0/3 noop=11/11`; hash-only `genuine=1/1 benign=0/3 noop=11/11`.
   5b. fixture (genuine + `d.cleanup()` inside the `with`) -> `legs=3/3 met=True`, exit 0, pristine and pruned.
6. `python3 tools/round58-c2-counter.py --repo <clone> --tip e4891d8a... --manifest-rev 941acf70...` ->
   `r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`, exit 0 (c2 untouched).
7. `python3 .ufo/waves/round-58/controls/make-variants.py <battery> out; diff -r` -> empty: all 15 committed
   variants reproduce byte-identically; `genuine.py` sha256 69b77a6a... equals the battery blob.

## Retained weight (measured, deliberately not deleted)
- `subprocess.call/check_call`, `Popen`+`allow`, `os.system`, `pathlib.Path.write_bytes` patches: no call site in
  the 15, but each is the barrier that turns a real process/write into a recorded no-op. Deleting them would let
  an unenumerated battery execute or write during scoring with no receipt to show it (~12 lines).
- `clean_env`/`genv` x3, `git()` x3, scratch-default x3 (~30 lines): each tool must run standalone from a bare
  checkout (the freeze names each file); sharing needs a new module in the frozen surface and changes no receipt.
- make-variants B1/B3 use bare `str.replace` without the `once` guard: a drifting anchor silently yields a
  non-variant. Generator output is exact today; fragility only, no deletion.

## Limit (not C1 credit)
A battery that runs all 3 legs and the mutant assert, then raises, is ACCEPTED: fixture (genuine with
`main(); raise RuntimeError("post-leg crash")`) -> `legs=3/3 ... met=True`, exit 0, identical pristine and pruned.
A mid-leg raise -> `executed=0 legs=0/3 met=False`, exit 1. Cause: the caught exception is stored in the now
unread record. Deleting that record changes neither verdict; making a post-leg crash disqualifying would be a
predicate change, so this is reported as a limit only.

## Tradeoffs
Compared: both counters' full text, the checker line, and 4 control receipts. Deletions are verified only against
the frozen 15 variants + 4 controls. Removing `cleanup` changes behaviour only for a battery calling it mid-run
(none exists; an end-of-run call still accepts, item 5b). No c2 deletion candidate: pyflakes clean; `--no-r42`
has a receipted caller (`.ufo/waves/round-58/w1/out/X03ReplayC2.md:35`); the round41 export is load-bearing
(r42 importlib-loads `round41-scorecard-reconcile.py` from the same directory). No c1/c2 claim, counter, variant,
source row, lesson or SCORECARD row was changed or judged.
