# SC02Lesson — seat report (kama round 78, wave 1)

author: kama SC02Lesson (scribe) · date 2026-11-04 · lane `/home/vgpnk/Projects/shokunin/kama-shokunin`

Scope honored: writes only `corpus/lessons/round-78.md`, the appended `corpus/QUALITY.md`
criterion, this seat dir, and `.ufo/waves/round-78/w1/SC02Lesson.md`. Read-only git only;
no commit/add/stash/checkout/switch/reset/pull, no jj mutation, no `pre-report-gate.py`
(L1's), no edits to SCORECARD.md, SKILL.md, corpus/README.md, corpus/SOURCES.md,
corpus/knowledge/**, registry/**, LOG.md, plans/**. No tool installs (pacman transactions
are paused host-wide; nothing needed one). Leaf seat: no subagents, no `agent://all`.

## Deliverables

| Path (absolute) | What |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-78.md` | the round lesson: three-claim account, `## Gate`, four value-bound `## Corrections`, two `## Mistakes`, `## Attack dispositions` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md` | appended `## Criteria added — round 78` with KQ129 (only appended bytes; no existing line moved) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/SC02Lesson/git-rev-parse-2026-11-04.html` | retained fetched copy of the external candidate (sha256 below) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/SC02Lesson.md` | findings digest (dispatch `Report:` trailer path) |
| this file | seat report |

## Gate evidence

**Own-work row.** Candidate: the round-78 counters for the instrument class C2 extends.
Status at cut: `tools/round78-append-registers.py` and `tools/round78-live-reconcile.py`
present; `tools/round78-selfrecord-round77.py` absent (`ls tools/ | grep -c
round78-selfrecord` → 0; `git ls-files tools/round78-selfrecord-round77.py` → empty). All
four committed pre-freeze receipts re-read and matching the plan's quoted lines:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/measured/before/c1-facts.out` — `SELFRECORD_R77_ENUM claims=6 stale=4 corrected=0`, EXIT=1; pins F3 old `gate=arms:8/word:eight/newest:round77-instruments/tally:18` (annotation `newest named=False`), F4 old `pointer=section:Mistakes 4`, F5/F6 olds as the plan states.
- `.../measured/before/c2-append.out` — `APPEND_REGISTERS … events=248 accepted=53 exempt=56 permitted=28 out_of_region=4 restored=99 disclosed=5 unaccounted=3`, EXIT=1, three `APPEND_REGISTERS_FINDING unaccounted` lines (`05a039805ba5dcca3e14091a447c88c07c971664`, `0fca5e18d408ab92717bbd9e26e7a4b4a1bcd7ac`, `21458716fbf3961312455ff78a12c9ca3a241a9e`).
- `.../measured/before/c3-noserver.out` — `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, PROBE_EXIT=2, EXIT=2.
- `.../measured/control/c3-feasibility.out` — `registry_rows_evaluated=3 model_ok=1 drift=2 exit=2`; rows `MODEL_OK` (matched, `runtime=llama.cpp`, served `stories260K.gguf`), `MODEL_MISMATCH` (served-id-mismatch), `DEAD` (connection-refused).

**External candidate — admit.** https://git-scm.com/docs/git-rev-parse, accessed
2026-11-04 (`curl -fsSL`, exit 0, 122459 bytes). Retained copy:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/SC02Lesson/git-rev-parse-2026-11-04.html`,
sha256 `00e3b1aaf8ae9df59a7a6bb8224e19e825c628b7a0cd69a4f03aeda79c2be587` (identical to the
scratch fetch). Located quote, 18 words (word count re-counted from the retained copy,
whitespace unfolded across its three line wraps): "Verify that exactly one parameter is
provided, and that it can be turned into a raw 20-byte SHA-1" — `--verify` option paragraph
under "Options for Output", anchor `Documentation/git-rev-parse.txt---verify`, retained
lines 2720–2722 (paragraph 2720–2723). `corpus/SOURCES.md` holds no row for this URL
(grep `docs/git-rev-parse` → no matches).

**Duplicate rejection — reject.** https://git-scm.com/docs/git-cat-file is already held by
S071 (`corpus/SOURCES.md:83`) and S083 (`corpus/SOURCES.md:95`); S083's scope cell already
names the adjacent ground ("Distinguishing process failure uses exit status"). Flip: the
`-e` option's own exit-0/exit-2 documentation, as an anchor neither row holds, reopens the
URL.

## Mistake rows (as recorded in the lesson)

**1. `unresolvable-cited-hash`.** Evidence (run this round, exit codes pasted):

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -t 6c1550a141babaca092cfcc3106f792d695652200
fatal: Not a valid object name 6c1550a141babaca092cfcc3106f792d695652200
exit=128
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --verify 6c1550a141babaca092cfcc3106f792d695652200
fatal: Needed a single revision
exit=128
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -t 6c1550a14babaca092cfcc3106f792d695652200
commit            # exit 0; rev-parse --verify resolves it
```

The round-77 spot-check passed its "every cited lane commit exists and is an ancestor" check
with the tip abbreviated to `6c1550a1` — abbreviation repairs a wrong-width token, so the
check could not catch the literal defect. Captured-by: none (no rule required a
resolvable/width-checked cited hash). Fix: every cited full hash is `git cat-file -e`-able;
C1's counter resolves `at` with `git rev-parse --verify` plus a 40-hex width check.

**Census conflict, verbatim for the canonical judgment.** The seat instruction (and frozen
plan §C1 ruling (a)) says the round-77 record cites the 41-character variant. A
case-insensitive census of the record set found the exact string in **zero** committed
record bytes:

| File | exact-41 count | hexlen histogram (≥38) |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/.ufo/reports/round-77/kama.md` (183 lines) | 0 | 5×40 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-77-verifier-spotcheck.md` | 0 | 11×40 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-77.md` | 0 | 2×40, 1×64 (sha256) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-77-claims.md` | 0 | 4×40 |
| `/home/vgpnk/Projects/shokunin/.ufo/prompts/closure/kama-round-77.md` | 0 | 5×40 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md` (worktree) | 0 | 106×40, 32×64 |
| `/home/vgpnk/Projects/shokunin/MANIFEST.json` | 0 | 1×39, 2166×40, 6×41, 7×42, 2×43, … (the six 41-hex runs are not the tip variant) |

The only occurrences of the 41-character string anywhere this seat can read are inside
round 78's own wave dispatch text (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1-dispatch.json`
and `w1-spec.json`), quoting the claim itself. The unresolvable-string fact re-derives
(exit 128 above); the 41-character citation's location inside a round-77 record does not
re-derive from anything this scribe can read. The mistake row records both.

**2. `stale-line-pointer`.** Evidence (run this round):

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 6c1550a14babaca092cfcc3106f792d695652200:LOG.md \
  | awk 'NR>=3126 && NR<=3142 {printf "%d|%s\n", NR, substr($0,1,150)}'
3130|before the outside closure that changes a path outside `LOG.md`, `SCORECARD.md`,
...
3137|## Round 77 — baseline receipts bind, two registers account, the round-76 facts are graded (2026-11-04)
```

Line 3130 is mid-sentence of the round-76 correction; the `## Round 77` heading is at 3137
— identical at the sealed revision and in the worktree. The round-77 report points readers
to `LOG.md:3130`. `grep LOG\.md registry/cited-path-corrections.tsv` → no matches, so the
miss was never disclosed there. Captured-by: none at the round-77 cut (KQ95 requires the
pointer to resolve or be disclosed; neither held). Fix: duty D9; appended pointer
corrections naming old and new anchors, never in-place rewrites; C1's F4 is the same class
for the SCORECARD pointer.

## Corrections written (unexecuted by this seat)

Four blocks in `corpus/lessons/round-78.md` §Corrections, exact §C1 shape, `at=` the sealed
revision `6c1550a14babaca092cfcc3106f792d695652200` (40-hex, resolves: `cat-file -t` →
`commit`), date `2026-11-04`, each followed by one prose line; olds are the committed
pre-freeze derivations (`measured/before/c1-facts.out`):

- F3 old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18` new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22`
- F4 old=`pointer=section:Mistakes 4` new=`pointer=section:Freeze divergences item 3`
- F5 old=`provenance=missing:corpus/knowledge/register-cutoff-split.md` new=`provenance=missing:none`
- F6 old=`coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md` new=`coverage-map=missing:none`

The C1 counter (`tools/round78-selfrecord-round77.py`) had not landed at this cut, so these
blocks are written to the frozen plan's shape and are not asserted executed here.

## Other verification

- Lane tip read per plan: `git -C <lane> rev-parse master` → `2bd07a8aeef822bd6b8b9137df4439f1499b08c9` (HEAD detached; no `@{u}`, no `--abbrev-ref HEAD` used for the tip read).
- Base `c62ffd3aea930b98375f805cc3dfb821a703148b` and freeze `11f46d644ed08d11758874a92d79214b3577a8a0` both resolve (`cat-file -t` → `commit`).
- Short hashes named by the plan resolve: `05a03980`, `0fca5e18`, `21458716`, `10f37171`, `c2aa7fb2` → `commit` each.
- Round-77 lesson's Mistake-1 anchor re-checked and still holding: at base `cc6e1d3c`, `tools/round76-append-exempt.py:76-86` is `introduction_history` (both register introductions) and lines 140-152 apply the earliest-introduction `precedes` cutoff to every row — no stale anchor to report there.

## Limits

- Did not run any claim counter, gate, census, or the C1 counter (absent at cut); no execution of the wave's work is asserted by this seat.
- The SOURCES row for the admitted external candidate is not appended (outside this seat's writes); the sources seat / L1 decide tier and append.
- Attack dispositions are a placeholder by design; the L1 integrates findings after the wave settles.

## Scratch

`$S=/fast/scratch/hyaku/kama-r78/SC02Lesson/` (mkdir -p; `TMPDIR=$S`): held only the fetched
`rev-parse.html` (copied into the seat dir, sha256 identical). Removed before yield.
