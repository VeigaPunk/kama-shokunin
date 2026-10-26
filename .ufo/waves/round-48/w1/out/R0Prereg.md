# R0Prereg — round-48 freeze integrity (lane kama)

**Verdict: PASS — every freeze-integrity check holds (predicates equal, counter hashes match the freeze commit, counters byte-identical at the build, time-check exit 0, frozen_at_utc 38 s before the freeze commit, v3 tool / v5 receipts / S492 absent at the freeze); the controls reproduce semantically 5/5, byte-identical 3/5 ex `tip=`, with the two byte-diff classes explained below as benign wall-clock/path-length artifacts (reported as mismatches with cause and proposed fix, not fixed in place — counters and controls are frozen).**

All checks run against the freeze commit `12284ba39fb1b46b43d43ee82423bebe08c700dc` ("FREEZE") and build commit `380bcdff9c8af06997c482f6eb03db926a794a2b` ("BUILD"); FREEZE is an ancestor of BUILD (`git merge-base --is-ancestor` → 0). Scratch `/fast/scratch/hyaku/kama-r48/R0Prereg-3` (removed at end). No tool installs/upgrades were needed or performed; pacman untouched. No subagents spawned; the lane was not mutated (read-only git only).

## 1. Predicate sentences: preregistration.json == counters' docstrings — MATCH

Extracted the sentence after the `PREDICATE (same sentence in the preregistration):` marker up to the blank line (the following `Output:` format block is not part of the sentence), whitespace-normalized, compared with `claims[].predicate` in `.ufo/waves/round-48/preregistration.json`, on the FREEZE commit content (`git show 12284ba…:<path>`):

- C1: `tools/round48-append-audit-v3-check.py:107-113` == prereg `claims[C1].predicate` → **EQUAL** (ends `… stable from the round-48 base; selftest=1 contract=1 lane=1 fixture=1 stable=1.`)
- C2: `tools/round48-live-replay-v5-audit.py:102-109` == prereg `claims[C2].predicate` → **EQUAL** (ends `… and the pinned revision is a source row; receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1.`)

Working-tree counters are byte-identical to the FREEZE versions (§2), so the equality holds for the working tree too.

## 2. counter_sha256 vs `git show 12284ba…:<path> | sha256sum` — MATCH

| counter | prereg `counter_sha256` | sha256 of `git show 12284ba…:<path>` | match |
|---|---|---|---|
| `tools/round48-append-audit-v3-check.py` | `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` | same | ✅ |
| `tools/round48-live-replay-v5-audit.py` | `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09` | same | ✅ |

Blob identity FREEZE↔BUILD: `git rev-parse 12284ba…:<path>` == `git rev-parse 380bcdff…:<path>` for both counters (C1 blob `b311529a536c…`, C2 blob `69aa6705132a…`) → **both counters byte-identical at BUILD** ✅. Working-tree counters hash equal to the FREEZE bytes ✅ (this matters because the controls builder scores the working-tree counters).

`.ufo/waves/round-48/preregistration.json` itself is byte-identical across working tree, FREEZE and BUILD (sha256 equal) — the freeze was not touched by the build.

## 3. `.ufo/waves/round-48/freeze/prereg-time-check.out` shows exit 0 — PASS

File content: `rev=12284ba39…`, `committer_time=2026-10-26T19:20:12-03:00 max_future=86400`, `ok line 6: 2026-10-26T22:19:34Z (at/before commit)`, `ok line 41: 2026-10-26T22:09:23Z (at/before commit)`, `RESULT pass: no timestamp later than the committer time`, last line `exit=0`. The `committer_time` inside it equals my own `git show -s --format=%cI 12284ba…` output. Line 6 of `preregistration.json` is `"frozen_at_utc": "2026-10-26T22:19:34Z"` and line 41 is the `observed` HF-revision timestamp — the two lines the control cites. Note: this receipt is committed at BUILD (absent at FREEZE), consistent with the BUILD commit message ("freeze-time receipt"); its content reports on the FREEZE commit.

## 4. frozen_at_utc precedes the freeze commit time — PASS

`frozen_at_utc = 2026-10-26T22:19:34Z` (preregistration.json:6); FREEZE committer time `2026-10-26T19:20:12-03:00` = `2026-10-26T22:20:12Z` → precedes by 38 s ✅. (Observation, not a mismatch: the FREEZE *author* time is `18:56:32-03:00` = `21:56:32Z`, i.e. the author finished writing ~23 min before the freeze stamp; the lane's canonical control checks committer time, under which the check passes.)

## 5. v3 tool, v5 receipts, S492 absent at FREEZE — PASS

- **v3 tool**: `tools/append-only-audit.py` exists at FREEZE but declares only `append-only-audit/v2` (no `append-only-audit/v3` string in it); at BUILD it declares v3. Tree-wide `git grep -l 'append-only-audit/v3' 12284ba…` hits only round-47 wave-out proposals (`.ufo/waves/round-47/w1/out/Rev1Restore*`), the controls builder, and the frozen C1 counter itself — no lane tool at v3 before the build ✅.
- **v5 receipts**: `git cat-file -e 12284ba…:.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` and `…/install.txt` all fail (absent) at FREEZE; all present at BUILD ✅.
- **S492**: `git grep -l 'S492' 12284ba…` → 0 files; `corpus/SOURCES.md` at FREEZE has no S492 row; BUILD has S492/S493 ✅.
- Observation (not leakage): the 40-hex revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` itself appears in 102 historical files at FREEZE (e.g. `.ufo/waves/round-21/build/out/AuditLaneDocHashes-6/candidates.tsv:5`) — earlier rounds recorded the same repo revision; what the build adds is the S492 *row*.

## 6. Controls reproduce — SEMANTICALLY 5/5; byte-identical 3/5 ex `tip=`; two explained artifact classes

Builder integrity: my copy of `.ufo/waves/round-48/controls/build_controls.py` sha256 = `c892d0c9dd0e897711b9a5a9f69c480b9c7d151acabfd53340a78b420a309d8a` == prereg `controls.builder` ✅; all six controls files and the builder are byte-identical between working tree, FREEZE and BUILD.

Command (run twice, 19.8 s and 18.5 s, both exit 0):
```
TMPDIR=$S python3 $S/ctl-src/build_controls.py /home/vgpnk/Projects/shokunin/kama-shokunin $S/ctl
```
First lines of all five regenerated `.out` files equal the frozen ones — leg verdicts identical:
```
base                  c1 selftest=0 contract=0 lane=0 fixture=0 stable=0 … fixture_fail=11 met=False
base                  c2 receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False
junk-c1-v2-relabel    c1 selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=11 met=False
junk-c1-drop-scorecard c1 selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=8 files=88 lane_events=3 lane_failures=0 ungraded_lines=0 fixture_fail=11 met=False
junk-c2-r47-relabel   c2 receipts=1 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False
```
Byte diff after dropping `tip=` lines (full diffs in `controls-regen/diff.txt`):
- `base.c1.out`, `junk-c1-drop-scorecard.c1.out`: **IDENTICAL** ✅
- `junk-c1-v2-relabel.c1.out`: **DIFFERS** — 10 `detail: fixture …:` lines carry per-fixture commit hashes (`8c9a6d59…` frozen vs `a09bc13d…` regen, etc.). Every expectation and verdict on those lines is identical (`want 20/0/24/25/40`, `graded=None` in both, `fixture_fail=11` in both). Cause: the C1 counter's fixture commits do not pin `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` (no such env anywhere in `tools/round48-append-audit-v3-check.py`), so fixture commit hashes vary with wall clock between runs. The docstring's "deterministic" (line 90) holds for the leg's verdict and expectations, not for the hashes echoed into `detail:` lines.
- `base.c2.out`, `junk-c2-r47-relabel.c2.out`: **DIFFERS** — one `detail: recordcheck all-right-control:` line each; both show `exit 2 executed=False outcome=None` (the v4 live tool refusing the five-flag invocation — the intended base behavior); only the truncated argparse-usage fragment inside the line shifts (`…r-asset-sha256 … error: unre` frozen vs `…sha256 … error: unrecognized` regen). Cause: the C2 counter truncates captured stderr to its last 300 chars (`tools/round48-live-replay-v5-audit.py:269`), and the argparse "unrecognized arguments" error echoes the full invocation including scratch paths, so the window cut depends on the scratch path length (the L1's scratch vs mine). Empirically confirmed with the v4 tool from the base clone: two archive-path lengths (57 vs 91 chars) → same `exit=2`, different `stderr[-300:]` fragment.

**Mismatch report (both benign, no semantic difference; counters/controls are FROZEN — proposed fixes for future counters, not to be applied in place):**
1. `tools/round48-append-audit-v3-check.py` fixture leg: pin `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` (e.g. both `2000-01-01T00:00:00Z`) in the fixture `git commit` env so fixture hashes — and the `detail:` lines embedding them — reproduce byte-for-byte.
2. `tools/round48-live-replay-v5-audit.py:269`: redact or basename-ify scratch paths (or truncate the captured stderr per line) before echoing it into `detail:` lines, so the echoed fragment does not depend on the runner's scratch path length.

## 7. Residual notes (no action required this round)

- The lane's time control allows `max_future=86400` (timestamps up to 24 h after the commit); both checked timestamps are before the commit, so nothing turns on it here. A tighter bound would strengthen future freeze checks.
- `freeze/prereg-time-check.out` is committed at BUILD, not FREEZE (the BUILD message names it "freeze-time receipt"); its content is about the FREEZE commit and matches independent git data.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R0Prereg.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R0Prereg/prereg-time-check.out` (copy of the cited lane receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R0Prereg/controls-frozen/{base.c1.out, base.c2.out, junk-c1-v2-relabel.c1.out, junk-c1-drop-scorecard.c1.out, junk-c2-r47-relabel.c2.out}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R0Prereg/controls-regen/{same five, builder-stdout.txt, diff.txt}`
