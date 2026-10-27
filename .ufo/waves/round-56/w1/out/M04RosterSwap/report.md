# M04RosterSwap — C2 roster designation mutation

- Mutant: in scratch clone, changed `tools/round56-env-leg-battery.py` ROSTER entry `m-drop-ldaudit` designation from `kill` to `control`; preregistration left unchanged.
- Detector: frozen `tools/round56-prereg-check.py` (SHA-256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`), invoked against committed tips in the scratch clone.
- Source baseline hashes: checker `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`; battery `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`; preregistration `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68`.

## Commands and outputs

All commands ran with `TMPDIR=/fast/scratch/hyaku/kama-r56/M04RosterSwap/tmp`; checker path was `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-prereg-check.py`.

Pristine base control:
```
python3 tools/round56-prereg-check.py --repo <scratch-clone> --tip e10b6d39af450e8d652be9ac2986768b531fe13f
 tip=e10b6d39af450e8d652be9ac2986768b531fe13f
 present=0 roster_match=0 kills=0 controls=0 met=False
exit=1
```
Pristine freeze tip:
```
python3 tools/round56-prereg-check.py --repo <scratch-clone> --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
 tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
 present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```
Mutant committed tip `b257987fec72877ac8506b7cfd3049795285ee36`:
```
tip=b257987fec72877ac8506b7cfd3049795285ee36
present=1 roster_match=0 kills=1 controls=2 met=False
exit=1
```
Restored committed tip `831a87450f7fa045bc0700d4e71ca5fefee33a43`:
```
tip=831a87450f7fa045bc0700d4e71ca5fefee33a43
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Receipts are `c2-base-pristine.out`, `c2-freeze-pristine.out`, `c2-mutant.out`, and `c2-restored.out` beside this report. The pristine/restored battery SHA-256 is `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`; restored blob diff against freeze battery was empty (0 changed lines).

## Verdict and restoration

**Killed.** The pristine freeze detector was green; the designation-only mutant was rejected with `roster_match=0`, `met=False`, exit 1; restoring exact battery bytes returned green. Scratch clone and TMPDIR were removed after receipts were copied.
