VERDICT: refute - no seat-authored KamaR21 or kama round-21 misroot at the fleet root; the two paths naming kama round 21 are driver-owned and must not be relocated
Attacked: hypothesis that kama round-21 or KamaR21 seat output sits in fleet-root untracked or modified paths (`git status --porcelain`). Read-only; fleet root and lane untouched.
Snapshot: 2026-10-21T08:27:21-03:00. Fleet HEAD: 7fd7c78 at start; 9881be6 (08:19:35, mori); 5d4a2ee (08:24:47, mori); 38a7cd5 (08:26:52, souji) at snapshot.

## 1. Porcelain paths at 08:27:21 (`git -C /home/vgpnk/Projects/shokunin status --porcelain`, EXIT 0)
| st | path | names kama r21 / KamaR21 | evidence | disposition |
|---|---|---|---|---|
| M | .ufo/watchdog.log | YES | uncommitted line 583: `2026-10-21T07:17:03-03:00 launch kama round=21 pgid=1279637 driver=hyaku-inline attempt=1`; file 585 lines, sha256 95327509... | driver runtime: do NOT relocate |
| M | .ufo/state/kama.report-baseline | YES, by value | `21 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; HEAD has `20 ...` (commit b3c9d68) | driver state: do NOT relocate |
| M | .ufo/state/kagi.report-baseline | no | `25 e3b0...` (was 24) | driver write for line 585 `launch kagi round=25` |
| M | .ufo/state/mori.report-baseline | no | `20 e3b0...` (was 19) | driver write for line 584 `launch mori round=20` |
| M | .ufo/state/tabi.report-baseline | no | `20 e3b0...` (was 19) | driver write for line 582 `launch tabi round=20` |
| ?? | .ufo/waves/round-20/ | no | sole file `residual/ResidualFrozen.md`; line 72 `spec.wave = registry.wave = tabi-round-20-w1`; `final/` and `w1/` are empty (git-invisible) | another lane's round-20 output; kama must not move it |

Cleared before 08:27:21, neither naming kama round 21: `.ufo/l0-questions.md` (+1 line 79, souji r20) and `.ufo/reports/round-20/souji.md` committed in 38a7cd5; `.ufo/reports/round-20/mori.md` (untracked at my second check) committed in 9881be6 and 5d4a2ee, the designed landing path (lane-addendum.md:167).

## 2. Why the two matches are driver-owned
- The four baseline changes each pair with one launch line (582-585) added in the same watchdog.log diff.
- Code path, verified by grep: scripts/hyaku/inline.sh:100 calls `record_report_baseline`, defined at scripts/shokunin-watchdog.sh:120-138, which writes `$UFO/state/<lane>.report-baseline`; inline.sh:103 appends the launch line.
- shokunin-watchdog.sh:108 says a missing report is the empty byte stream; e3b0... is sha256 of empty input, so the kama r21 report was absent at launch (no `.ufo/reports/round-21/kama.md` exists). Runtime attribution by timing: [INFERENCE].
- Driver runtime is never lane-committed (scripts/hyaku/fleet-commit.sh:32; jj-lane.sh:513-514). Lanes must not touch `.ufo/state/*` or `.ufo/watchdog.log` (lane-addendum.md:170, :177). The relocation rule (lane-addendum.md:172-176) covers seat-written files naming the lane/round: zero kama candidates.

## 3. Searches with no kama r21 / KamaR21 hit (grep tool; "no match" unless noted)
- `KamaR21`, `kama-shokunin...round-21`, `kama R21`, `round-21...kama` over: .ufo/l0-questions.md, .ufo/state/, .ufo/reports/ (round-20, round-21), .ufo/waves/round-21/, .ufo/waves/shokunin-train-20261101-w21/, .ufo/prompts/, .ufo/gates/, .ufo/scopes/, .ufo/round-44/, .ufo/round-10/, .ufo/lane-watch.sh, .ufo/history-pin.json, MANIFEST.json, LOG.md, SCORECARD.md, CORPUS.md, PROTOCOL.md, README.md, shokunin.conf, templates/, scripts/. Only hit: `.ufo/reports/round-20/kama.md:67` ("round 21 was not started"), tracked and clean.
- Ignored content: .tower/ and .ufo/waves/shokunin-train-20261014-w9, -20261101-w10, -w11: no hit.
- Positive controls matched (grep works): mori.md and ResidualFrozen.md on `round-20`; stray tree on `souji|verify`.
- l0-questions.md: round-21 entries shown are mado (line 78); line 50 cites a `round21` filename only; no line co-names kama and round-21.

## 4. Supplementary, outside porcelain scope
- Ignored stray tree `bash: /home/vgpnk/Projects/shokunin/souji-shokunin/tests/tools/` holds one 10139-byte file named by a bash error string, a souji round-4 verifier receipt (mtime 2026-10-18 14:01); ignored via .gitignore:1 (`*-shokunin/`). Not kama.
- Empty `.ufo/waves/round-21/w1/`: created 2026-10-20 05:56:08 with its parent; `w1` mtime 2026-10-21 05:55:57, so an entry was created and removed there [INFERENCE]. Timing is 4 min after kake's round-21 launch (05:51:51); writer unverified [INFERENCE]. Not kama by name or timing (kama r21 launched 07:17:03).
- Tracked, clean, stale: `.ufo/state/kama.round` = `1` (last commit 17c1fad, 2026-09-29) and `kama.mission` = `2684953` (last commit 99efc52, 2026-10-15). inline.sh has no `.round`/`.mission` writes (grep: no match).
- Tracked dispatch evidence: `.ufo/prompts/kama-round-21.md` (commit 6806f4d, 07:17:01). `.ufo/reports/round-21/` holds kagi, kaidoku, kake, kotodama, mado; no kama.md yet (expected landing path, lane-addendum.md:167).

## 5. Commands and exits (absolute paths, read-only)
- `git -C /home/vgpnk/Projects/shokunin status --porcelain`: EXIT 0 at start, 08:24:30, 08:27:21. `--untracked-files=all`: EXIT 0. `diff`: EXIT 0. `diff --stat`: EXIT 0 (6 files, +9/-4). `--ignored=matching`: EXIT 0.
- `ls-files --stage kama-shokunin`: EXIT 0, empty. `check-ignore -v kama-shokunin`: EXIT 0 (.gitignore:1). `ls-files -v -- .ufo/state`: EXIT 0, all `H`. `check-ignore -v --no-index -- .ufo/state/kama.round`: EXIT 1 (not ignored).
- `log -1` on kama.round and kama.report-baseline, `log --grep kama -i -5`, `log -4`, `show --stat HEAD`: all EXIT 0. `ls-files` on round-21 dirs, round-20/kama.md, prompts/kama-round-21.md: EXIT 0.
- `find ... -maxdepth 1 -name 'bash*'`, `find "...bash: " -type f | wc -l` (1), `find ... -type d | wc -l` (8), `du -sh`, `stat`, `find .ufo/waves/round-21 -printf`: all EXIT 0. `sha256sum` x3 and `wc -l watchdog.log` (585): EXIT 0.
- Grep, glob, read calls: results as cited (no exit codes).

## 6. Hygiene
- Tools installed or updated: none. /tmp scratch: none. Processes started: none.
- Writes: this report and an identical copy at `falsify/out/KamaR21.MisrootSweep/MisrootSweep.md` (cmp checked). No moves, deletes, or edits to the lane or fleet.
- Limits: committed content sampled, not exhaustively scanned; ignored content outside the dirs above not scanned; runtime attribution is [INFERENCE].
