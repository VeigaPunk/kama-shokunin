Verdict: both requested C2 instruments were deterministic at 138af25b; audit v6 agreed 3/3 and the frozen C2 counter agreed 2/2, with both predicates met.

## Target audit: `append-only-audit.py` v6 text output

- Clone: `/fast/scratch/hyaku/kama-r51/X9Agree/lane`; verified clone root with `git -C "$S/lane" rev-parse --show-toplevel`, then detached checkout at `138af25b963450b6520794995605fa7dbbcd87e0`. `git show <tip>:tools/append-only-audit.py` SHA-256 matched the checked-out file: `3d0eaa168c26f006da656e635995f14d43c57c3a9af43ddf1b954f5ca3070c11`.
- Help: `python3 tools/instrument-agreement.py --help` exited 0; accepted `--runs`, `--cwd`, `--normalize`, `--out`, `--selftest`, and a command after `--`.
- Command (instrument): `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/instrument-agreement.py --runs 3 --cwd "$S/lane" --out "$OUT/ia-audit-v6-raw.json" -- python3 "$S/lane/tools/append-only-audit.py" --repo "$S/lane" --to 138af25b963450b6520794995605fa7dbbcd87e0`; exit 0; output `IA runs=3 agree=3 disagree=0 digest=3342e51e3405 exit=0`.
- Per-run digests (all exit 0): run 1 `3342e51e34053f657fec409d5909cb3ec5aaf6d5265c38a2967ae1c09e6c8d0d`; run 2 same; run 3 same. Audit's direct text capture is saved as `X9Agree/audit-v6-text-tip.out` (107 lines; final summary: `commits=341 files=96 events=106 restored=19 partial=0 unrestored=0 ungraded=36 disclosed=51 permitted_lines=58 disclosed_lines=166 bad_disclosures=0 ungraded_lines=205 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0`). Its stderr capture is empty.
- Counterfactual sensitivity check: same command with `--threshold 20`, instrument runs 2, agreed 2/2 at digest `70c93ad390958bf9fe4f22a788ddc1c8ca38c71226c932cd1575bb499016611f`; each instrument run exited 1. Thus changing the threshold changes the measured output/digest; saved receipt is `X9Agree/ia-audit-v6-threshold20.json`. This is a sensitivity probe, not a passing target run.

## Frozen C2 counter

- Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/instrument-agreement.py --runs 2 --cwd "$S/lane" --out "$OUT/ia-c2-counter-raw.json" -- python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py --repo "$S/lane" --tip 138af25b963450b6520794995605fa7dbbcd87e0`; exit 0; output `IA runs=2 agree=2 disagree=0 digest=588d4b4df068 exit=0`.
- Per-run digests (both exit 0): `588d4b4df0689633c940d274ea762e6c2286b3e852b503a40bfe1623a966e410`.
- Direct single-run counter output (exit 0) saved in `X9Agree/c2-counter-direct.out`: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`; lane detail reports tool v6, 106 events, 166 disclosed lines, 58 permitted lines; counter independently found 142 lost lines in whole-file-graded files, with 166 ledger lines. Stderr is empty. This matches the frozen predicate at preregistration.json:31-35.
- Ran the frozen counter at the base `57a2e25bf702b03aa61f9265e968cf68058ecb82` as a control: exit 1, `fixture=0 lane=0 scenarios=0/9 ... met=False`, matching the base control's false verdict. The base v5 tool fails the v6 fixture interface (including unsupported `--disclosures`); this is the expected pre-build distinction, not a new lane defect. Capture: `X9Agree/c2-counter-at-base.out`.

## Normalization and evidence boundaries

The receipts used only instrument-agreement's built-in ISO-UTC timestamp normalization (no caller-supplied rules); each run receives a fresh TMPDIR. The target audit and target counter stdout/stderr contain no timestamp or run-temp path. Independently recomputing `sha256(exit + NUL + stdout + NUL + stderr)` from the saved direct captures exactly reproduced each target IA full digest (`3342…8d0d` and `588d…e410`), so the default normalization did not alter either target capture. Instrument source documents this digest and agreement definition at `tools/instrument-agreement.py:20-30,44-76`; the counter's frozen predicate and output contract are at `tools/round51-append-audit-v6-check.py:49-60`; v6 default threshold and disclosure behavior are at `tools/append-only-audit.py:2-30,1444-1485`.

Instrument selftest: `python3 .../tools/instrument-agreement.py --selftest` exited 0 with `[PASS] deterministic: agree=3 disagree=0`, `[PASS] nondeterministic: agree=2 disagree=1`, `[PASS] declared-volatile: agree=3 disagree=0`, `[PASS] exit-disagreement: agree=2 disagree=1`, `IA_SELFTEST pass=4 fail=0`. This checks the agreement harness' detection behavior; it does not prove instrument correctness (the tool's documented limitation).

## Retained evidence

- `X9Agree/ia-audit-v6-raw.json` — requested 3-run audit receipt, full per-run digests and command.
- `X9Agree/ia-c2-counter-raw.json` — requested 2-run frozen counter receipt, full per-run digests and command.
- `X9Agree/audit-v6-text-tip.out` and `.err` — direct audit text output and empty stderr.
- `X9Agree/c2-counter-direct.out` and `.err` — direct counter output and empty stderr.
- `X9Agree/ia-audit-v6-threshold20.json` — sensitivity receipt.
- `X9Agree/c2-counter-at-base.out` — base control run output.

No lane files or counter/preregistration/control files were modified. I started no external services. Final `pgrep -af '[l]lama-server'` observed an unrelated process owned outside this seat: PID 1211006 running `/home/vgpnk/.local/opt/llama-b11909/llama-server` on loopback port 18199, with model path under `out/Sen2Race/`; I left it untouched. Main-agent integration should retain the above receipts and may run its own post-integration gates.
