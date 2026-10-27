# J7Prefix — round 52, lane kama: C2 ablation control (non-verbatim restoration)

**Verdict: the C2 control holds.** A fixture clone of build `5dacf2c7` whose 18 `Restored lines (round 52)` blocks have every restored line prefixed with `> ` (fences kept) is rejected by the frozen C2 counter — `fixture=1 lane=0 scenarios=8/8 corr_lost=306 row_lost=10 disclosed=10 met=False`, exit 1 — and by the tip's own frozen `tools/append-only-audit.py` — exit 1, `unrestored 18 regressed 45`. The same harness reproduces the build's verdict bit-for-bit at the unmodified build commit (`met=True`, exit 0) and at the lane tip `34d82600` (`met=True`), so the failure is caused by the ablation and nothing else. No counter or tool defect found; two calibration observations recorded below.

## Fixture and mutation

- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; detached at build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`. `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r52/J7Prefix/lane` before any commit.
- Mutation script (own file, not the lane's): `$S/mutate_prefix.py` — state machine over `#{2,3} Restored lines (round 52)` sections, CommonMark-fence aware (0–3 spaces, 3+ backticks/tildes opening without a backtick in the info string; close = same char, at least as many, spaces/tabs only); every **non-empty line inside a fence** in the section gets `> `; fence lines and blank lines untouched. Sections matched `^#{2,3} Restored lines \(round 52\)` — 18 of them (LOG.md, SCORECARD.md `###`, corpus/QUALITY.md, corpus/README.md, 14 lessons); SKILL.md:1558 and corpus/lessons/round-52.md:12 mention the title in prose only and were left alone.
- Result: `files=18 lines=155` (`mutation-counts.json`), `git diff --stat 5dacf2c7 b8162c74` → `18 files changed, 155 insertions(+), 155 deletions(-)`. The 155 equals the build's own restored-line count (`corpus/lessons/round-52.md:12`), i.e. the ablation is exhaustive: no restored line stays verbatim.
- Five-backtick fence lines in the 18 files: `90` at `5dacf2c7`, `90` at `b8162c74`, `90` at `2ea844eb` — fences preserved as required.
- Fixture commit (identity `fx <fx@invalid>`, `-c commit.gpgsign=false`): `b8162c7477146e83a13ced4033c156d62659f3d7` "J7Prefix ablation: restored round-52 lines prefixed with '> ' (not verbatim)". Diff: `out/J7Prefix/mutant.diff`.
- Supporting 1-file probe on branch `single` off the same build: only `corpus/QUALITY.md`'s 2 restored lines prefixed → `2ea844eb3d92d3cedef9342918406545d4d78c40` (`out/J7Prefix/single.diff`).

## Commands, outputs, exit codes

Baseline (control-of-control, unmodified build `5dacf2c7`, my clone, my invocation):

```
$ python3 tools/round52-append-restore-check.py --repo $S/lane --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S/c2base --out $S/c2-build-repro.out
tip=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
detail: lane: tool v6 threshold 1 exit 0 events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10; ledger lines 10
exit=0
```
(byte-identical head/summary to `.ufo/waves/round-52/measured/c2-build.out`; evidence `out/J7Prefix/c2-build-repro.stdout`)

Lane tip (extra datum, spec commit `34d82600`, no mutation): `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0 — `out/J7Prefix/c2-lanetip.stdout`.

Ablation (primary, `b8162c74`):

```
$ python3 tools/round52-append-restore-check.py --repo $S/lane --tip b8162c7477146e83a13ced4033c156d62659f3d7 --scratch $S/c2 --out $S/c2-mutant.out
tip=b8162c7477146e83a13ced4033c156d62659f3d7
fixture=1 lane=0 scenarios=8/8 corr_lost=306 row_lost=10 disclosed=10 met=False
detail: fixture corr-in-place: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 ok
detail: fixture corr-fenced-reappend: tool exit 0 (want 0) own unheld 0 (want 0) own graded 1 ok
detail: fixture cutoff-after-intro: tool exit 1 (want 1) bad_disclosures 1 (want 1) ok
detail: fixture cutoff-before-intro: tool exit 0 (want 0) bad_disclosures 0 (want 0) ok
detail: fixture only-outside: tool exit 0 (want 0) own unheld 0 (want 0) own graded 0 (want 0) ok
detail: fixture only-inside: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 (want 1) ok
detail: fixture exempt-inside: tool exit 0 (want 0) own unheld 0 (want 0) own graded 0 (want 0) ok
detail: fixture exempt-dated: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 (want 1) ok
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 18, 'partial': 0, 'regressed': 45, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: unheld lines in A-corr files: {'LOG.md': 44, 'SCORECARD.md': 42, 'corpus/README.md': 40, 'corpus/lessons/round-26.md': 34, ...}
detail: lane: tool v6 threshold 1 exit 1 events 127 disclosed_lines 10; own graded 6023; own unheld A-corr 306, A/A-row 10; ledger lines 10
exit=1
```

Single-file probe (`2ea844eb`, 2 lines): `fixture=1 lane=0 scenarios=8/8 corr_lost=4 row_lost=10 disclosed=10 met=False`, exit 1; `unheld lines in A-corr files: {'corpus/QUALITY.md': 4}`; tool leg `exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 1, ...}` — `out/J7Prefix/c2-single.stdout`.

Frozen tool, run as a CLI from the tip's own bytes (blob `63e1dd24…` identical at `5dacf2c7`, `b8162c74`, `HEAD`; sha256 `343e8c18cab102fceb0c8735b60916015f2bfc6dbe4423e45471c7558c97d459`):

| tip | exit | summary |
|---|---|---|
| `5dacf2c7` (build) | 0 | events 109, restored 67, unrestored 0, regressed 0, bad_disclosures 0, bad_declarations 0 |
| `b8162c74` (ablation) | 1 | events 127, restored 67, **unrestored 18**, **regressed 45**, bad_disclosures 0, bad_declarations 0 |
| `2ea844eb` (2-line probe) | 1 | events 110, restored 67, **unrestored 1**, **regressed 1**, bad_disclosures 0, bad_declarations 0 |

Attribution (`out/J7Prefix/tool-summary.txt`): the 18 new events at the ablation tip are exactly the 18 mutated files, all `status=unrestored`; the 45 changed historical events keep `status=restored` (window-max, `tools/append-only-audit.py:127`) with `held_at_to < restored_max` and are counted by `summary.regressed` (`tools/append-only-audit.py:738`) — consistent with the documented contract (`tools/append-only-audit.py:124-137`), so the `restored` + `held_at_to=0` pairing in JSON is by design, not an inconsistency.

## Why corr_lost=306 and not ~155: exact additive decomposition

The ablation write is itself a deletion event: the prefix commit removes all 155 verbatim restored lines (so the historical losses are no longer held) **and** leaves the historical events' losses unheld. The counter's per-file numbers split exactly, with zero residual (`out/J7Prefix/decomposition.txt`, base column = `.ufo/waves/round-52/controls/base.c2.out`):

```
file                                         base prefix mutant  additive
LOG.md                                         22     22     44  ok
SCORECARD.md                                   19     23     42  ok
corpus/QUALITY.md                               2      2      4  ok
corpus/README.md                               20     20     40  ok
corpus/lessons/round-1.md                       2      2      4  ok
corpus/lessons/round-16.md                     11     11     22  ok
corpus/lessons/round-18.md                      4      4      8  ok
corpus/lessons/round-19.md                      6      6     12  ok
corpus/lessons/round-25.md                     10     10     20  ok
corpus/lessons/round-26.md                     17     17     34  ok
corpus/lessons/round-27.md                     13     13     26  ok
corpus/lessons/round-28.md                      6      6     12  ok
corpus/lessons/round-32-verifier-spotcheck.md    1      1      2  ok
corpus/lessons/round-38.md                     11     11     22  ok
corpus/lessons/round-4-recensus.md              1      1      2  ok
corpus/lessons/round-40.md                      1      1      2  ok
corpus/lessons/round-42.md                      4      4      8  ok
corpus/lessons/round-43.md                      1      1      2  ok
totals base=151 prefix=155 mutant=306 mismatches=0
```

`151 + 155 = 306` in every one of the 18 files. The expected "≈155-ish" figure in the seat brief undercounts by construction: a non-verbatim restoration costs the historical losses *and* its own deletions. The 2-line probe confirms the same additivity at 1-line granularity (`2 + 2 = 4`) and shows the counter is not hiding small losses at its default threshold — the frozen tool grades every deletion (`threshold` default 1).

## What the control demonstrates (calibration)

1. **Verbatim is load-bearing.** Only the byte-identical re-append satisfies C2; a blockquote prefix inside an intact fence — the smallest semantic no-op a reader would call "still the same text" — fails both the counter (`corr_lost≠0`, `lane=0`) and the tool (`regressed`/`unrestored`), so the round-52 claim is not satisfiable by an approximation.
2. **The counter's own region/fence logic is not the tool's.** All eight constructed scenarios still pass under the ablation (`scenarios=8/8`), including fenced-verbatim-reappend, only=/exempt= and both ledger-cutoff directions; the ablation changed only the lane leg. The fixture leg is therefore independent of the lane it measures.
3. **The ledger leg is insensitive, correctly.** `row_lost=10 disclosed=10` and `bad_disclosures 0` at both tips: the 10 remaining A/A-row rows key-match and were untouched by a mutation confined to A-corr files. A prefix ablation cannot launder an A-corr loss into the ledger.
4. **Both instruments agree on direction and count families.** Counter: 306 unheld A-corr lines / 18 files / tool exit 1. Tool: 18 unrestored + 45 regressed events, exit 1. Neither reports a false pass.

## Observations (no defect claimed; counters are frozen)

- **O1 (wording/readability, counter `tools/round52-append-restore-check.py:72-73` + detail line):** the counter's `detail: lane: unheld lines in A-corr files` prints per-file totals that mix historical losses with the measured tip's own deletion events; here 151 of the 306 come from history and 155 from the fixture commit. A `corr_lost` number can therefore be read as one cause when it is two. Not fixable in place (frozen); proposed wording for a future counter revision: `detail: lane: unheld lines in A-corr files (event=…, tip-event=…)`. No code change proposed against this round.
- **O2 (environment, not this seat):** `pgrep -af llama-server` shows two `kama-llamacpp-live.py` runs with a live child under `/fast/scratch/hyaku/kama-r52/R1Old/…` (loopback `127.0.0.1:42983`) at report time. They are not mine — this seat started no server process and tore nothing down. Flagged for the owner/orchestrator; not touched.
- No proposed fix to the frozen counters or to `tools/append-only-audit.py`: the control's purpose is served and its `restored`+`held_at_to` split is documented behaviour.

## Limits / risks

- The fixture's identity is `fx <fx@invalid>` in my own `--shared` clone; nothing was written to the lane, its index or its jj state (all lane access read-only). The one committed diff is `out/J7Prefix/mutant.diff` and `single.diff`.
- `corr_lost=306` is tip-specific and includes the fixture commit's own deletions; comparing it to the base control's 151 requires the decomposition above (identical result obtained independently in all 18 files).
- Scratch `/fast/scratch/hyaku/kama-r52/J7Prefix` (clone, c2 scratch dirs, `__pycache__`) removed before finishing; no `/tmp` paths cited. No tools installed or upgraded this wave.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/c2-mutant.out`, `c2-mutant.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/c2-build-repro.out`, `c2-build-repro.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/c2-lanetip.out`, `c2-lanetip.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/c2-single.out`, `c2-single.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/tool-build.events.json`, `tool-mutant.events.json`, `tool-single.events.json`, `tool-summary.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J7Prefix/mutation-counts.json`, `decomposition.txt`, `mutate_prefix.py`, `mutant.diff`, `single.diff`
