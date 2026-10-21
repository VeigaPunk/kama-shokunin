# Existing-selftest mutation probe

Axes: detector sensitivity; single-fault isolation and exact restoration; bounded operability. This is baseline coverage evidence, not a judgment on the round claim.

## Scope and detector

Used the requested `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23/MutExistingSelftest`; cloned HEAD was `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. No candidate implementation or additional detector was used. Git: `2.56.0`; Python: `3.14.8`; date: 2026-10-21.

All seven executions used this identical detector, with a 120-second subprocess timeout:

```text
cwd: /tmp/kama-r23/MutExistingSelftest
command: /usr/bin/python3 tools/report-landing-audit.py --selftest
complete child environment:
  PATH=/usr/bin:/bin
  HOME=/tmp/kama-r23/MutExistingSelftest
  LC_ALL=C.UTF-8
  GIT_CONFIG_GLOBAL=/dev/null
  GIT_CONFIG_NOSYSTEM=1
```

Below, `S` is `/tmp/kama-r23/MutExistingSelftest/tools/report-landing-audit.py`; `E` is `.ufo/waves/round-23/build/out/MutExistingSelftest/evidence.json`. `E` retains complete stdout/stderr, exact commands/environments, durations, exits, and before/after SHA-256 values for every execution.

## Results

Pristine: exit **0**, `selftest cases=50 failed=0`; empty stderr (`E:56-62`). Each one-line mutant started from pristine bytes, was tested alone, and was restored before the next mutant.

| Mutant | Expected detector | Actual output and exit | Verdict |
| --- | --- | --- | --- |
| Drop `GIT_CONFIG_NOSYSTEM="1"` from `git_env()` (`S:83`) | Existing `--selftest` must reject the mutation to demonstrate sensitivity to loss of system-config isolation. | Exit **0**; `selftest cases=50 failed=0`; stderr empty (`E:79-85`). | **Survived** |
| Replace the `GIT_*`-filtering comprehension with `dict(os.environ)` (`S:82`) | Existing selftest injects a decoy `GIT_DIR` (`S:491-492`); preservation should break isolation. | Exit **2**; stdout empty; refusal below (`E:125-131`). | **Killed**, through fixture-setup refusal, not a failed named assertion. |
| Add `errors="replace"` alongside `text=True` in `git()` (`S:90`) | Existing `--selftest` must reject the mutation to demonstrate sensitivity to lossy Git-output decoding. | Exit **0**; `selftest cases=50 failed=0`; stderr empty (`E:171-177`). | **Survived** |

Exact stderr for the killed mutant:

```text
could-not-evaluate: git add f in /tmp/report-landing-selftest-m29fn6qk/lane: rc=128 fatal: this operation must be run in a work tree
```

The inherited-variable mutant stops at the initial fixture commit (`S:498`, helper `S:465`), before any of the 50 named checks print. It does **not** reach the final `inherited-GIT_DIR-untouched` assertion (`S:804-805`). Nonzero process status kills it; this is not evidence that a particular assertion failed.

## Exact restoration

Pristine SHA-256 (`P`):

```text
09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f
```

| Mutant | Mutated SHA-256, identical before/after detector | Restored detector |
| --- | --- | --- |
| Drop NOSYSTEM | `9e5f20346e9e700257c1c0d39e4bb648f12f64bed0456366cd6beb43f5af6820` | Hash `P` before/after; exit 0, 50 cases, 0 failed (`E:102-108`). |
| Keep GIT variables | `dd4f83f487cd2b4b93ac47e928616bf6058554a024f5080a4ad59a35f0ff5034` | Hash `P` before/after; exit 0, 50 cases, 0 failed (`E:148-154`). |
| Replacement decoding | `7dec8eb9cc7d092402ebb6d5f354ab051082bb24eb8e593251b7f46950122ae9` | Hash `P` before/after; exit 0, 50 cases, 0 failed (`E:194-200`). |

No baseline/restoration failures or timeouts occurred. Final scratch source bytes equal pristine bytes.

## Coverage finding and limits

The existing detector kills **1/3** assigned mutants and misses **2/3** in the recorded environment. The survivors establish a finite suite-sensitivity gap, not that removal of isolation or lossy decoding is acceptable. No hostile system-config fixture or invalid-byte Git-output fixture was added. No revised candidate, fault-grid detector, historical ledger, real lane/fleet audit, network behavior, other Git/Python versions, build, lint, or formatter was verified. No external sources were used. No tools were installed or updated.

## Files written

Permanent artifacts, relative to the lane root:

- `.ufo/waves/round-23/build/advice/MutExistingSelftest.md` — this append-only report.
- `.ufo/waves/round-23/build/out/MutExistingSelftest/evidence.json` — all seven actual detector records.
- `.ufo/waves/round-23/build/out/MutExistingSelftest/drop-nosystem.patch` — captured `git diff` for that mutant.
- `.ufo/waves/round-23/build/out/MutExistingSelftest/keep-git-vars.patch` — captured `git diff` for that mutant.
- `.ufo/waves/round-23/build/out/MutExistingSelftest/decode-replace.patch` — captured `git diff` for that mutant.

Scratch writes: the requested clone populated `/tmp/kama-r23/MutExistingSelftest/`; only its `tools/report-landing-audit.py` was manually edited, then restored exactly. The unchanged selftest created and removed its own fresh `/tmp/report-landing-selftest-*` fixture trees. No helper scripts were created. No lane tracked files, lane index, sibling sources, global configuration, commits/pushes outside the selftest's temporary fixtures, or other agent runtimes were modified/invoked.
