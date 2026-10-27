# X9Agree — determinism receipt (round 52 w1, lane kama)

**VERDICT: PASS — both instruments agree 3/3 at the build; digests `5b3472bd794b…` (frozen C2 counter) and `20900375a7c8…` (append-only-audit v6), and both reproduce the L1's own build receipts and the frozen base control byte-for-byte from an independent clone.**

Axes named: (1) run-to-run determinism of the two C2-path instruments at the frozen build; (2) sensitivity — the digest must move when the measured tree moves, or agreement is worthless.

## Setup and pinning

Scratch `S=/fast/scratch/hyaku/kama-r52/X9Agree`, `TMPDIR=$S`.

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # exit 0
git -C $S/lane rev-parse --show-toplevel  -> /fast/scratch/hyaku/kama-r52/X9Agree/lane
git -C $S/lane rev-parse HEAD             -> 34d8260051bbab8859485e8209fcf4be19dc9a2b
```

The clone HEAD (34d82600) is newer than the build; every measurement pins the tree with `--tip` / `--to`, so the clone HEAD cannot enter a count. Counter bytes are identical at the freeze, the build and the clone HEAD (`git diff --stat 8551ba7f..HEAD -- tools/…` empty; worktree matching):

| file | sha256 (first 16) at 8551ba7f / 5dacf2c7 / 34d82600 / worktree |
|---|---|
| `tools/round52-append-restore-check.py` | `29dfd886d858f24d` (all four) |
| `tools/append-only-audit.py` | `343e8c18cab102fc` (all four) |
| `tools/instrument-agreement.py` | `8b9a88463e86c1e7` (all four) |

So this receipt measures the *frozen* counters, not an edited variant.

## Agreement counters at the build 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8

```
python3 tools/instrument-agreement.py --runs 3 --cwd $S/cwd --out …/ia-c2-frozen.json \
  -- python3 tools/round52-append-restore-check.py --repo $S/lane --tip 5dacf2c70f947…
IA runs=3 agree=3 disagree=0 digest=5b3472bd794b exit=0        # exit 0

python3 tools/instrument-agreement.py --runs 3 --cwd $S/cwd --out …/ia-append-only.json \
  -- python3 tools/append-only-audit.py --repo $S/lane --to 5dacf2c70f947…
IA runs=3 agree=3 disagree=0 digest=20900375a7c8 exit=0        # exit 0
```

Full digests (`sha256(exit\0normalized stdout\0normalized stderr)`):

- frozen C2 counter, tip 5dacf2c7 — `5b3472bd794bfdb93ccfe9b79aae13119bc4303368a240dafa13980a48823a8c`, exit 0, 11 stdout lines, 0 stderr bytes. Substantive first line: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`.
- `append-only-audit.py --to 5dacf2c7` — `20900375a7c8b74258dc42762be2777605ff502bd3ca7c67c79099444e180695`, exit 0, 110 stdout lines (`event` rows + summary), 0 stderr bytes. Summary: `commits=350 files=99 events=109 restored=67 partial=0 unrestored=0 ungraded=37 disclosed=5 permitted_lines=58 disclosed_lines=10 bad_disclosures=0 ungraded_lines=210 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0`.

## Agreement is not bought by normalization

`instrument-agreement.py` normalizes only its own temp dir (line 46, `text.replace(tmpdir, "<TMP>")`) plus the caller-declared rules; the only rule in force here is the tool's default ISO-timestamp rule (`DEFAULT_NORMALIZE`, line 39). Neither instrument emits a scratch path or a timestamp:

- two raw runs of each command with *different* `TMPDIR` values: `raw_diff_lines=0` for both; 0 hits of the ISO pattern; no `<TMP>` marker in the captured stdout.
- independent replication of the tool's digest formula from those raw runs reproduces `5b3472bd794bfdb9…` and `20900375a7c8b742…` exactly (both runs each), so `agree=3` means byte-identical output, not normalized-away output.

## Sensitivity: the digest tracks the tree

Added control (my own, not in the seat spec), same clone, base tip instead of build tip:

```
IA runs=2 agree=2 disagree=0 digest=47a824bf6b3e exit=1   # c2 counter at --tip 9ff76b1f
IA runs=2 agree=2 disagree=0 digest=006751a61c29 exit=0   # append-only-audit --to 9ff76b1f
```

Both differ from the build digests, and the C2 base run reproduces the frozen control exactly:

```
diff -u .ufo/waves/round-52/controls/base.c2.out …/c2-base.raw.stdout
-> only difference: the control file's trailing harness line `exit=1` (measure.sh trailer)
```

i.e. `corr_lost=151 row_lost=10 disclosed=165 met=False`, `own unheld A-corr 151, A/A-row 10; ledger lines 165` — the frozen base contract value, exit 1, from a different clone and scratch.

Likewise, my independent-clone runs reproduce the L1's own battery:

- `…/c2-build.raw.stdout` vs `.ufo/waves/round-52/measured/c2-build.out`: body 11 lines, `diff=0` (only the harness `$ ` header and `exit=` trailer stripped).
- `…/aoa-build.raw.stdout` vs `measured/aoa-build.out`: body 110 lines, `diff=0`.

## Instrument sanity

```
python3 tools/instrument-agreement.py --selftest
[PASS] deterministic / nondeterministic / declared-volatile / exit-disagreement
IA_SELFTEST pass=4 fail=0   (exit 0)
```

The nondeterministic and exit-disagreement arms show the tool *detects* drift, so `agree=3` is a measurement, not an unresponsive instrument.

## Limits and observations (no lane defect found)

1. **C1 is not covered by this seat.** I instrumented only the two C2-path instruments named in the assignment. For the record: `controls/base.c1.out` carries live process furniture (`pid 563321`, `port 46167`, inode numbers, nonces). `[INFERENCE]` Running `instrument-agreement.py` over `round52-replay-memfd-audit.py` *without* caller-declared `--normalize` rules for pid/port/inode would and should report `disagree`, because the tool alone only normalizes its own temp dir (`tools/instrument-agreement.py:46-48`). Agreement on C1 therefore has to be stated per declared normal rule, not "same digest" alone.
2. **Latent fragility, not a current defect:** the counters create their scratch with `tempfile.mkdtemp(dir=<TMPDIR>)` — `tools/round52-append-restore-check.py:510`, `tools/append-only-audit.py:784,1499` — i.e. *random-suffixed* paths inside the directory `instrument-agreement.py` normalizes as `<TMP>`. Today neither counter prints those paths (measured above: `raw_diff=0`), so agreement is honest. If a future counter prints its scratch path, `<TMP>/r52c2-<rand>/…` survives normalization and the tool will report a spurious `disagree`; the counter would then need a `--normalize` rule or must stop echoing scratch paths. Worth carrying as a known property of the instrument pair.
3. `--runs` accepts 2 as the floor (`tools/instrument-agreement.py:137-139`); my build runs use the assigned N=3, my added base control uses the floor N=2 (labelled as such in `agreement.json`).

## Tooling

No installs, no upgrades (`pacman` untouched; nothing needed). No `llama-server` was started by this seat; `pgrep -af llama-server` shows only another seat's process under `/fast/scratch/hyaku/kama-r52/V6Registry/…`, none of mine. Scratch clone removed after the receipt was written.

## Commands (verbatim, exit codes)

```
S=/fast/scratch/hyaku/kama-r52/X9Agree; export TMPDIR=$S; mkdir -p "$S/cwd"
git clone --shared …/kama-shokunin "$S/lane"                                              # 0
T=$PWD/tools   (T=/home/vgpnk/Projects/shokunin/kama-shokunin/tools)
python3 $T/round52-append-restore-check.py --repo $S/lane --tip 5dacf2c7…                 # 0  met=True
python3 $T/append-only-audit.py --repo $S/lane --to 5dacf2c7…                             # 0  events=109
python3 $T/instrument-agreement.py --runs 3 --cwd $S/cwd --out …/ia-c2-frozen.json -- …   # 0  agree=3
python3 $T/instrument-agreement.py --runs 3 --cwd $S/cwd --out …/ia-append-only.json -- … # 0  agree=3
python3 $T/instrument-agreement.py --runs 2 --cwd $S/cwd --out …/ia-c2-base.json -- … --tip 9ff76b1f…  # 0 agree=2 digest=47a824bf6b3e exit=1
python3 $T/instrument-agreement.py --runs 2 --cwd $S/cwd --out …/ia-append-only-base.json -- … --to 9ff76b1f…  # 0 agree=2 digest=006751a61c29
python3 $T/instrument-agreement.py --selftest                                             # 0  pass=4 fail=0
diff -u .ufo/waves/round-52/controls/base.c2.out …/c2-base.raw.stdout                     # 1 (only the `exit=1` trailer, expected)
```
