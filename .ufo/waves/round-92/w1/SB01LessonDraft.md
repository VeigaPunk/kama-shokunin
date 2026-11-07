# SB01LessonDraft — round-92 lesson draft

## Scope

Drafted the round-92 lesson at `.ufo/waves/round-92/w1/out/SB01LessonDraft/round-92-draft.md` (not `corpus/`),
from `plans/round-92-claims.md`, `controls/*.out`, `measured/*.out`, `corpus/lessons/round-91.md` and
`round-91-verifier-spotcheck.md`. Re-opened S593-S597 and the pinned `llama-server --help`; built one paired B6
fixture in own scratch; no tracked lane file edited; no tool installed or updated.

## Commands and outputs (exit codes)

| command | observed | rc |
|---|---|---|
| `curl -sS -m 60` x5, then `sha256sum` | `c69c0e07…` arg.cpp, `d4d343db…` server.cpp, `c3010a3c…` common.h, `0b0ea669…` config.go, `e963af06…` envs.py — all equal the SOURCES anchors (`source-digests.out`) | fetches returned the pinned bytes (rc not captured separately) |
| `/home/vgpnk/.local/opt/llama-b12177/llama-server --help` | binary sha256 `ba272ee3…`; help line 468 `-np … (default: -1, -1 = auto)` | 0 (output read; rc not separately captured) |
| read-only `git show` / `git diff --stat` in lane | R08 at `18153ebb:SKILL.md:1941` (section 1920); S593-S597 at `corpus/SOURCES.md:348-352`; correction 703-712; counter diffs F..M1 and F..tip empty | output observed (rc not separately captured) |
| fixture: `mktemp -d -p <own scratch>`, `git init -q`, toplevel assert, commit "129" | toplevel equals `$D`; commit `ba63bc35f92457f9f9903ad303e0b032d59659ff` | 0 |
| `python3 tools/round92-server-defaults.py --repo "$D" --rev ba63bc35… --binary …/llama-server` | `rows=15 bound=15 unbound=0 … help_checked=7 help_disagree=0 supersedes=14` | 0 |
| commit "128" (`590a4040a22f6c1b75cf6bb4edb83cb14187fd7a`), same counter | `R08 bound=0 … why=literal-not-at-line`; `rows=15 bound=14 unbound=1` | 1 |
| `sed -n '128p' server.cpp` / `'129p'` | 128 is blank; 129 is `params.n_parallel = 4;` | 0 |
| `uptime` at 21:47 / 21:53 | load average 37.38 / 38.85 (1 m) | 0 |

Counter bytes: `tools/round92-server-defaults.py` sha256 `a49e8984…`, `tools/round92-linear-paths.py` `64e7b35a…`
— identical at freeze, M1/M2 and worktree. Probe at M2 sha256 `36631d49…`, base `0aa43573…`.

## Findings

- **NOTE — Gate rows.** S596/S597 digests equal their rows and the quotes sit at `arg.cpp:1373` and
  `server.cpp:127` (binding literal 129); S593-S595 re-opened with equal digests. `source-digests.out`;
  `controls/sources-opened.out:1-9`.
- **NOTE — Gate rejects.** `envs.py:26` is a `TYPE_CHECKING` declaration (block at line 14), never a run-time
  default; `common.h:464` (`n_parallel = 1`) is overridden by `arg.cpp:1373` and resolved at `server.cpp:129`.
  Both rejected with flips in the draft Gate.
- **NOTE — M1 evidence.** v0 compared `latest.tsv` whole and failed base against itself: D7 `equal_to_base=0`
  (`controls/c2-base-v0.out:11`), `positive_mismatches=1` (`:20`), diagnosis `:22-24`; fix `stable()`
  (`tools/round92-linear-paths.py:207-209`, used `:258`), frozen base passes D7 (`controls/c2-base.out:8`).
- **NOTE — M2 evidence.** The pre-freeze P0 battery is now on disk: `controls/c1-forgeries-v0.out:4-6` shows
  `CASE P0-candidate expected_exit=0 exit=1 UNEXPECTED` with `R08 bound=0 … why=literal-not-at-line` at rev
  `4f1794e4…` (header `:1-3`: v0 cited 128; `c1-forgeries.out` is the post-fix run). The draft cites this and adds
  this seat's paired control: positive 129 rc 0 (`b6-positive-129.out:9,17-18`), mutant 128 rc 1 with
  `literal-not-at-line` (`b6-mutant-128.out:10,18-19`); `server.cpp:128` is blank. The v0 file was untracked at
  drafting.
- **DEFECT — M3 (r91 M4 recurrence).** The C2 probe change staled the round-90 reason-row receipt
  (`measured/r90-reason-rows-stale.out:26-27`, `bound=0 unbound=24 receipt=stale`, rc 1 at `83f9e3d4`), and the
  frozen harm list (`controls/harm.sh:11-16`) again names six sections (five suites plus the operator-router check)
  and not `tools/round90-reason-rows.py`.
  Fix landed: recapture at the M2 probe (`measured/r90-reason-recapture.out:26-27`, rc 0) with the 24
  (cell, reason, verdict) triples identical (only `probe_sha256` differs), then rebind at the tip
  (`measured/r90-reason-rows-tip.out:26-27`, `bound=24 receipt=current`, rc 0 at `d5a06431`).
- **NOTE — measured claims and counter identity.** C1 `measured/c1.out:17-18` rows=15 bound=15 help 7/0
  supersedes=14 rc 0 at `18153ebb`; base `controls/c1-base.out:2-3` rows=0 rc 1. C2 `measured/c2.out:17-18`
  cells=15 mismatches=0/0 rc 0 at `fa8aedb7` (load 78.95 at `:1`; max L cell 3.43 s at `:11`); base
  `controls/c2-base.out:17-18` mismatches=6 rc 1 (L1-L5 killed 120 s, L6 53.98 s). Harm base/M all rc 0
  (`controls/harm-base.out`, `measured/harm-M.out`).
- **NOTE — dispositions.** R2 correction present at `corpus/SOURCES.md:703-712`; R3 met by 12 distinct per-seat
  roots in `w1-spec.json`; R1 carried with no round-92 receipt; R4/R5 are the measured claims above. Lane tip is
  now `d5a064313522392bf7f8498d1a54c0cfd0ad314b`; both measured revisions are ancestors of `master`.

## Deliverables

- `.ufo/waves/round-92/w1/out/SB01LessonDraft/round-92-draft.md` (lesson draft, 75 lines)
- `.ufo/waves/round-92/w1/out/SB01LessonDraft/source-digests.out`
- `.ufo/waves/round-92/w1/out/SB01LessonDraft/b6-positive-129.out`
- `.ufo/waves/round-92/w1/out/SB01LessonDraft/b6-mutant-128.out`

VERDICT: holds — lesson draft written with every required row, quote, mistake and disposition evidenced; M2's pre-fix failure is on disk (controls/c1-forgeries-v0.out) and independently re-demonstrated, and the r91-M4 recurrence is recorded as DEFECT with its recapture receipts.
