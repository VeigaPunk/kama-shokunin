# J8AllNever - round 53, C2 ablation control: blanket `never` disclosure

**Verdict: control passes.** Replacing every class in `registry/cited-path-corrections.tsv` with `never` / evidence `-` on a fixture clone of the build commit makes the frozen C2 counter fail: `bad=2 stale=1 undisclosed=2 disclosed=12 met=False`, exit 1. The same clone at build tip `c22602bd8d83ab26349d1087e916ca537ee4f9d1` yields `bad=0 stale=0 undisclosed=0 disclosed=14 met=True`, exit 0, byte-for-byte matching `.ufo/waves/round-53/measured/c2-build.out` counts. So `met=True` at the build is not a blanket-disclosure artifact.

## Fixture

- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r53/J8AllNever/lane`; `git -C <clone> rev-parse --show-toplevel` printed `/fast/scratch/hyaku/kama-r53/J8AllNever/lane` (asserted equal before committing).
- Ablation commit: `5ca9f7c2745aedbc8653a3883538f7f4bb1f93e6` ("fixture: C2 ablation - blanket never disclosure for every ledger row"), parent `c22602bd`, identity `-c user.name=fx -c user.email=fx@invalid`, one file changed: `registry/cited-path-corrections.tsv | 16 ++++++++--------` (8 insertions, 8 deletions).
- Changed rows (file lines, ablated copy): 16 deleted->never (`.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`), 21 untracked->never (`.ufo/watchdog.log`), 22-26 upstream->never (`tools/server/server-{schema,common,schema,task,chat}.cpp`), 27 fixed->never (`tests/report-audit/…`). The seven `never` rows were already `never`/`-`.
- Ledger observed at the build: 15 data rows = 14 unresolved disclosures + 1 `fixed` row (the seat brief says 14 rows; the counter's `unresolved=14` is the disclosure count).

## Commands and results

Frozen counter sha256 `1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080` == preregistration `C2.counter_sha256` (unchanged; `counter.sha256`).

1) Build-tip reproduction (clone, unmodified tree):

```
$ TMPDIR=/fast/scratch/hyaku/kama-r53/J8AllNever python3 tools/round53-cited-path-check.py \
    --repo /fast/scratch/hyaku/kama-r53/J8AllNever/lane \
    --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 \
    --fleet-rev ee9f7341bd98de0fcd85f6c01f689301589b27e9 \
    --scratch /fast/scratch/hyaku/kama-r53/J8AllNever --out .../c2-build-repro.out
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1 fleet=ee9f7341bd98de0fcd85f6c01f689301589b27e9
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
exit=0
```

2) Ablation at `5ca9f7c2`, fleet at the build's rev:

```
fixture=1 lane=0 scenarios=8/8 cited=682 unresolved=14 disclosed=12 undisclosed=2 bad=2 stale=1 dropped=0 met=False
detail: undisclosed SCORECARD.md `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`: [('.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp', 'missing')]
detail: undisclosed SCORECARD.md `.ufo/watchdog.log`: [('.ufo/watchdog.log', 'missing')]
detail: bad ledger line 16 (SCORECARD.md `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` never): .ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp was a path in some commit
detail: bad ledger line 21 (SCORECARD.md `.ufo/watchdog.log` never): .ufo/watchdog.log was a path in some commit
detail: stale ledger line 27 (SKILL.md `tests/report-audit/…`): token resolves or is not cited
exit=1
```

The same run with the fleet left at current HEAD (`git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` = `d2a6c59aaabcbde2d4a946c31d0276bb2c3d7887`, drifted since the build) produces an identical line: `bad=2 stale=1 undisclosed=2 disclosed=12 met=False`, exit 1. The ablation result is therefore attributable to the ledger change alone, not to fleet drift.

## Mechanism (frozen counter, file:line)

- `tools/round53-cited-path-check.py:265-268` - `never` re-derives as "token in no lane/fleet commit history"; line 267 consults `lane.hist()` and `fleet.hist()`. Both flipped tokens were committed paths: `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` in lane history (last touched by the round-31 snapshot commits; the build row's `deleted 9874e455...` is the truthful class) and `.ufo/watchdog.log` in fleet history (checked with `git -C <fleet> log --all --format= --name-only`, one hit), so `never` is contradicted and the rows are bad.
- `:251-252` + `:354-359` - a row whose token is unresolved and whose class is not `fixed` but returns `None` is stale; that is what catches the reclassified `fixed` row (SKILL.md `tests/report-audit/…`), which is no longer cited at tip because the build corrected it in place to `tests/report-audit/`.
- `:362` - both flipped tokens also land in `undisclosed`, since a bad row does not enter `disclosed`.

## Calibration observation (not a defect to fix in place)

Of the 14 disclosures, 12 still pass under blanket `never`: the five `upstream` rows and the `untracked` row are only checked by their own class's evidence (`:280-303` fetches the pinned raw URL; `:305-313` requires a file on disk under the fleet root), and under `never` neither proof is exercised - the counter only asserts "absent from history", which is true for llama.cpp's `tools/server/*.cpp` and for a never-committed log. The control therefore bites solely through the two tokens that were once committed. Recorded as a C2 limit for the lane's next-round planning, not remediated (counters and ledger are frozen; this seat reports only).

## Housekeeping

- No tools installed or upgraded. No llama-server started by this seat (`pgrep -af llama-server` shows only `X6Battery`'s round-52 replay servers under its own scratch path); nothing to tear down.
- Lane repo, fleet repo and `/home/vgpnk/Projects/shokuknow` untouched (read-only git only). No jj/git mutation outside the scratch clone.
- Scratch `/fast/scratch/hyaku/kama-r53/J8AllNever` removed after copying the receipts below.

## Artifacts (this directory)

- `J8AllNever.md` - this report
- `c2-abl-never.out`, `c2-abl-never-fleetpinned.out` - ablation receipts (exit 1)
- `c2-build-repro.out` - build-tip reproduction (exit 0)
- `c2-abl-never.patch` - `git diff c22602bd 5ca9f7c2 -- registry/cited-path-corrections.tsv`
- `cited-path-corrections.abl-never.tsv` - the ablated ledger (sha256 `a613eaccd576fb1c63d3a7c851a515f5ef27e733a91e54a01e36f28f1383d9f2`)
- `counter.sha256` - frozen counter digest
