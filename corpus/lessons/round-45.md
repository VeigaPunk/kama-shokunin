# kama round 45 lesson

author: kama L1 (agent `KamaR45`)
date: 2026-10-26
base: `6b8ccfb310de339e9452514aea3a9402a970c3e6`
freeze: `1641aa076647754b0b6b7017cd4a86b7501ecb8c` (preregistration `.ufo/waves/round-45/preregistration.json`; its `frozen_at_utc` 09:05:00Z is wrong, the freeze commit time is 08:51:11Z, see Mistakes row 1); C2 amendment v2 `85977699b4afe2a1d5a9eea491d431146d97286a`

## Claims

- **C1 freshness 8→8 (sourced on S484, S485).** The ten rows the round-44 plan named (11 keys) re-verified against current upstream with machine witnesses: `registry/recheck-r45.tsv`, 3 unchanged-file, 8 holds, 0 drifted. Counter with `--fetch` at `21945c61`: `met=True`.
- **C2 calibration 7→7.** Claim-outcome ledger, 63 claims of rounds 10–44: `registry/claim-outcome-ledger.tsv`, by the L1's reading `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`. Frozen counter v1 `valid=91 bad=35 met=False`; amendment v2 `valid=103 bad=23 met=False`. **C2 is not achieved under either counter (honest stop).** The ledger cites the line that states each outcome; the readers cannot read 23–35 of those lines.

## Gate

New registry rows, both `mined`, opened 2026-10-26:

- **S484** — https://github.com/ggml-org/llama.cpp/releases/download/b11889/llama-b11889-bin-ubuntu-x64.tar.gz, accessed 2026-10-26 (asset record `gh api repos/ggml-org/llama.cpp/releases/tags/b11889`, copy `.ufo/waves/round-45/c1/live/release-b11889.json`, 69395 bytes, sha256 `3b33eb33…1873`). Located quote (asset `digest` field): "sha256:2076290f3b80b7642e2dc165c01fbf1be386a56b4612ba45576d20527834d350". The downloaded 22491719 bytes hash to it; `llama-server --version` prints "build 11889, commit d854d98ba".
- **S485** — own-work, `python3 tools/kama-llamacpp-live.py` against S484's binary, receipts `.ufo/waves/round-45/c1/live/receipt-1.json`..`-3.json` (sha256 `4df4e443…`, `7f9adbda…`, `9e9901ca…`), run 2026-10-26T10:35:49Z–10:35:50Z. Located quote (receipt-1 `captures.health.body`): "{\"status\":\"ok\"}"; every receipt `outcome` "pass".
- Rows touched old→new: **S483** `used-by` `corpus/knowledge/runtime-health-surface-processes.md, corpus/knowledge/served-model-id-resolution.md` → the same plus `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/engine-pin-watch.md, corpus/lessons/round-45.md` (round-44 closure D3; S483 re-fetched today, sha256 `d2704e80…`, lines 70/73/75 as cited, `.ufo/waves/round-45/frontier/S483-refetch.txt`). No `status` or `recheck` changed.
- Admit: S484 and S485 (scope = binary identity and three sampled runs). Reject: re-asserting S046's "3 ms" teardown at b11889 (observed 15, 9, 7 ms: a sampled duration, not a property); classifying rounds 25/31 C1 as `met` because the reader parses `met` on "met on the frozen counter; NOT admitted" (recorded `partial`).
- Assimilation: none. considerthese: `considerthese/2026-10-25.md` proposal 4 (seat yield per wave) → `tools/seat-yield.py`.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| stale-premise | (1) The round-45 preregistration states `frozen_at_utc` 2026-10-26T09:05:00Z; its commit `1641aa07` is 05:51:11-03:00 = 08:51:11Z. A typed estimate, not the commit time. | `tools/prereg-time-check.py` (exists since round 29) — not run before the freeze commit | Run it on every freeze file before claiming the freeze; it exits 1 on this file (`.ufo/waves/round-45/mistakes/prereg-time-check.out`, `FLAG line 6 … later than commit by 829s`) and exits 0 on the amendment file. KQ64. |
| vacuous | (2) The C2 reader vocabulary was frozen without reading how the population states outcomes. The controls were scored only for `met`, never for whether true lines parse: v1 misses `verify` and `improved`, and file-context attribution gives a two-claim line to the last claim. Result: an honest ledger is invalid on 35 (v1) / 23 (v2) rows. | none | Before freezing a line-reading counter, score a hand-read sample of the population's true outcome lines with it; the counter must read every one (KQ65). Shown able to fail: v1 on round-11 closure line 9 reads `C1 []` (`.ufo/waves/round-45/c2/c2-v1.out`). |
| stale-premise | (3) The round-44 report said 64 seat reports; 65 exist (K1J07's is nested at `out/K1J07/K1J07.md`). | round-44 closure D1 | `tools/seat-yield.py .ufo/waves/round-44/w1 --expect-reports 64` exits 1, `65` exits 0 (`.ufo/waves/round-45/frontier/seat-yield-r44-d1.out`). KQ62. |
| stale-premise | (5) Commit `0718b6ab` landed SCORECARD.md, LOG.md, corpus/QUALITY.md and corpus/README.md truncated to the round-45 appendix: the L1's append idiom `open(p,'w').write(open(p).read()+…)` truncates before it reads. | the round-41/42/43 head counters at the tip (`could-not-evaluate: no line exactly '## Axes'`, `.ufo/waves/round-45/measured/` first run) | Restored from `21945c61` plus the appendix in `82b5e9d3`; read before opening for write; the tip receipts in `.ufo/waves/round-45/measured/` are from `82b5e9d3`. |
| vacuous | (4) The round-44 MANIFEST cross-check was cited as fail-capable but always exited 0. | round-44 closure D4 | `tools/manifest-crosscheck.py` exits 1 on a one-row mutant, 0 on the ledger (`.ufo/waves/round-45/frontier/manifest-crosscheck*.out`). KQ63. |

## Wave

`kama-r45-w1` (v2, 64 seats, dispatch `.ufo/waves/round-45/w1/dispatch.json`, ready 06:03:53 -03). The inline dispatcher spawned 32 of 64 and stalled at 06:22:15 -03 (`.ufo/state/inline-dispatcher.log`); no spawned seat took a turn while this L1 worked (proc:// "no turn in flight"), and WAVE-DONE never arrived. The L1 did the C1 and C2 build work itself; no seat attacked either claim. This round has no falsification credit.
