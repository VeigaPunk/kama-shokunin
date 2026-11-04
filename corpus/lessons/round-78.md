# kama round 78 — lesson

author: kama SC02Lesson (scribe seat, round 78 wave 1)

Lane: kama. Round 78, one v1 build-and-attack wave of 12 seats (3 executor, 3 scribe,
1 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/12 = 33 %).
Base: `c62ffd3aea930b98375f805cc3dfb821a703148b`.
Freeze commit: `11f46d644ed08d11758874a92d79214b3577a8a0`, the commit adding
`plans/round-78-claims.md`; this lesson treats the plan's blockquote predicates as frozen
text and does not edit the plan. Assigned lesson axes: calibration (7, the lane's lowest
non-retired assigned score, so C1 satisfies the lowest-axis duty), freshness and
operability — one claim each. Lane tip at the scribe cut, read as the plan directs with
`git -C <lane> rev-parse master` (git HEAD is detached, so a HEAD-based read is not a tip
read): `2bd07a8aeef822bd6b8b9137df4439f1499b08c9`.
This is a source-and-receipt account at the scribe cut, not a claim that unexecuted
counters passed. At the cut, `tools/round78-append-registers.py` and
`tools/round78-live-reconcile.py` are present in the tree; `tools/round78-selfrecord-round77.py`
is not yet landed, so the correction blocks below are written to the frozen plan's shape and
are not asserted executed by this seat.

## The round's three claims

- **C1 — calibration.** `python3 tools/round78-selfrecord-round77.py --repo .` must print
  `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0`, exit 0, only when each of
  the six facts the round-77 self-record declares re-derives from the tree or is answered by
  a committed value-bound correction block at the sealed revision
  `6c1550a14babaca092cfcc3106f792d695652200` (the round-77 tip, not the base, because the
  record's own values were written there). Allowed to claim: the record's facts are
  value-bound and each non-re-deriving fact is answered by exactly one valid correction.
  Not allowed to claim: that round 77's work was green, that a correction makes an
  underlying value true beyond its re-derivation, or anything about counters this module
  does not read. Base: `SELFRECORD_R77_ENUM claims=6 stale=4`, exit 1.
- **C2 — freshness.** `python3 tools/round78-append-registers.py --repo . --to c62ffd3aea930b98375f805cc3dfb821a703148b`
  must print `APPEND_REGISTERS to=c62ffd3aea930b98375f805cc3dfb821a703148b events=248 …
  unaccounted=0 introductions=1/1 rotation_safe=1`, exit 0, only when every base audit
  deletion event sits in exactly one of six buckets whose sum equals `events`, each bucket
  row is committed at the audited revision or earlier, register rows naming an event commit
  outside the audited population are reported on a separate `APPEND_REGISTERS_OUT_OF_POPULATION`
  line and change no bucket, the two registers' sha256 prefixes are printed, and rotation
  detection rejects a reintroduced path carrying new rows. Allowed to claim: the frozen base
  population is accounted once at the audited revision. Not allowed to claim: register rows
  are correct in substance, or that the frozen command stays green under later appends —
  out-of-population rows are excluded by design, which is what keeps the frozen command
  stable. Base: `events=248 … unaccounted=3`, exit 1, with three `APPEND_REGISTERS_FINDING
  unaccounted` lines for the round-77 SCORECARD deletions `05a03980`, `0fca5e18`, `21458716`.
- **C3 — operability.** `python3 tools/round78-live-reconcile.py --repo .` must print
  `LIVE_RECONCILE rows=3 model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp
  served=stories260K`, exit 0, only when it starts the pinned llama-server child on a
  loopback port that is neither a registered consumer port nor currently listening, writes a
  three-row scratch registry under its own scratch root, grades the rows `MODEL_OK` /
  `MODEL_MISMATCH` / `DEAD`, requires the live row's evidence to name `runtime=llama.cpp`
  and the pinned fixture model, refuses any registered consumer port before probing, tears
  the child down and writes a receipt carrying the child's exit status. Allowed to claim:
  the lane's reconciliation verdict path is exercised end-to-end against a live pinned
  child. Not allowed to claim: any registered consumer is reachable — the scratch registry
  is evidence, not a registry row, the three registered consumers keep their recorded `DEAD`
  state, and the counter is a trial instrument, not a readiness gate for configured
  consumers. Base: `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2` (no server).

## Gate

- **Own-work row (the round's own instrument class).** The round's own-work candidate is
  the instrument class C2 extends: the round-78 counters — `tools/round78-selfrecord-round77.py`
  (calibration, self-record facts), `tools/round78-append-registers.py` (append-only audit
  family, extending `append-registers`) and `tools/round78-live-reconcile.py` (live
  reconciliation verdicts). Status at this scribe cut (2026-11-04):
  `tools/round78-append-registers.py` and `tools/round78-live-reconcile.py` are present;
  `tools/round78-selfrecord-round77.py` is not yet landed. The pre-freeze before/control
  receipts are committed under `.ufo/waves/round-78/measured/` and this scribe re-read all
  four; each matches the plan's quoted lines: `before/c1-facts.out`
  (`SELFRECORD_R77_ENUM claims=6 stale=4 corrected=0`, EXIT=1; F3 old value
  `gate=arms:8/word:eight/newest:round77-instruments/tally:18`), `before/c2-append.out`
  (`events=248 accepted=53 exempt=56 permitted=28 out_of_region=4 restored=99 disclosed=5
  unaccounted=3`, EXIT=1, three `unaccounted` findings), `before/c3-noserver.out`
  (`registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, EXIT=2) and
  `control/c3-feasibility.out` (`registry_rows_evaluated=3 model_ok=1 drift=2 exit=2`,
  `MODEL_OK` / `MODEL_MISMATCH` / `DEAD` against the pinned child). The SOURCES row append
  itself is the sources seat's and the L1's write; this Gate records the candidate, not an
  append.
- **External candidate, opened and decided this round — admit.** Git git-rev-parse
  `--verify`, URL https://git-scm.com/docs/git-rev-parse, access date **2026-11-04**
  (fetched live by this seat, `curl -fsSL`, exit 0, 122459 bytes; copy retained at
  `.ufo/waves/round-78/w1/SC02Lesson/git-rev-parse-2026-11-04.html`, sha256
  `00e3b1aaf8ae9df59a7a6bb8224e19e825c628b7a0cd69a4f03aeda79c2be587`). Located quote,
  **18 words**: "Verify that exactly one parameter is provided, and that it can be turned
  into a raw 20-byte SHA-1" (whitespace unfolded across the page's line wraps). Location:
  the `--verify` option paragraph under "Options for Output", anchor
  `Documentation/git-rev-parse.txt---verify`, retained lines 2720–2722 (paragraph
  2720–2723). Scope: the checking command a correction's `at=` revision must satisfy —
  exactly one parameter resolving to an object-database name — not abbreviation-uniqueness
  semantics (held by S082) and not git-cat-file's batch output (held by S083). No
  `corpus/SOURCES.md` row holds this URL this cut. Decision: admit as the round's external
  candidate on the resolvable-hash ground; tier and the row append are the sources seat's
  and the L1's call.
- **Rejected candidate (duplicate), checked this round — reject.** Git git-cat-file,
  https://git-scm.com/docs/git-cat-file. Reason: already held twice — S071 and S083 both
  cite this URL, and S083's scope cell already names the adjacent ground ("Distinguishing
  process failure uses exit status; the earlier peel nuance is own-work"). A third row would
  duplicate the claim, the same ruling round 77's L1 applied to S549 against
  S073/S085/S093. **Flip:** the `-e` option's own documented exit-0/exit-2 behavior, as a
  distinct anchor neither S071's nor S083's batch-output scope holds, reopens the URL.

## Corrections

Exactly four value-bound blocks, one per stale fact (F3, F4, F5, F6), in the shape §C1 of
the frozen plan specifies; `at` names the sealed revision and each `old` re-derives there
(F3–F6 olds are the committed pre-freeze derivations in
`.ufo/waves/round-78/measured/before/c1-facts.out`).

- `corrected F3` old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18` new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  At the sealed revision `SKILL.md`'s pre-report-gate registry row (line 309 there) still described eight arms with prose `eight` and the round-76 self-test tally 18, and did not name the gate module's newest arm `round77-instruments` (`newest named=False` in the committed derivation), while the landed gate module carries nine arms and the round-77 gate-selftest receipt prints `pass=22`; the new value states the gate module's own shape.
- `corrected F4` old=`pointer=section:Mistakes 4` new=`pointer=section:Freeze divergences item 3` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  At the sealed revision the record's last freeze-divergence sentence pointed the C3 predicate/ruling divergence at §Mistakes 4 — which is the mutating-git breach — instead of §Freeze divergences item 3; this pointer correction is appended and no filed bytes are rewritten.
- `corrected F5` old=`provenance=missing:corpus/knowledge/register-cutoff-split.md` new=`provenance=missing:none` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  At the sealed revision `corpus/knowledge/register-cutoff-split.md` carried no `source:` or `source-correction:` line citing at least one `S###` row id; the new value declares that provenance duty covered.
- `corrected F6` old=`coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md` new=`coverage-map=missing:none` at=`6c1550a14babaca092cfcc3106f792d695652200` date=`2026-11-04`
  At the sealed revision neither round-77 knowledge entry had a coverage-map row in `corpus/README.md`; the new value declares the coverage-map duty covered for both entries.

## Mistakes

1. **`unresolvable-cited-hash`** — a cited revision token that no git object answers, passed
   by a check that never tested resolvability.
   *Evidence pointer:* the frozen plan's own scope ruling names the class
   (`plans/round-78-claims.md:86-89`): round 77's record cites a 41-character tip
   `6c1550a141babaca092cfcc3106f792d695652200` that no object answers, while the real tip is
   `6c1550a14babaca092cfcc3106f792d695652200`. This scribe re-derived the core fact at the
   wave cut: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -t
   6c1550a141babaca092cfcc3106f792d695652200` → `fatal: Not a valid object name
   6c1550a141babaca092cfcc3106f792d695652200`, exit 128; `git rev-parse --verify` on the
   same string exits 128 (`fatal: Needed a single revision`); the 40-character tip prints
   `commit` and `rev-parse --verify` resolves it. The round-77 non-author spot-check's
   conformance table passed "every cited lane commit exists and is an ancestor" while
   listing the tip as the 8-character abbreviation `6c1550a1` among 20 hashes — an
   abbreviation silently repairs a wrong-width token, so that check could not have caught
   the record's literal defect.
   *Census conflict, recorded verbatim for the canonical judgment:* a case-insensitive
   census of the round-77 record set this round — fleet report
   `/home/vgpnk/Projects/shokunin/.ufo/reports/round-77/kama.md`,
   `corpus/lessons/round-77-verifier-spotcheck.md`, `corpus/lessons/round-77.md`,
   `plans/round-77-claims.md`, the fleet closure prompt
   `/home/vgpnk/Projects/shokunin/.ufo/prompts/closure/kama-round-77.md`, worktree `LOG.md`
   and fleet `MANIFEST.json` — finds the exact 41-character string in **zero** committed
   record bytes; every ≥38-hex token in those files is 40 characters or a 64-character
   digest (`MANIFEST.json` separately carries six other 41-hex runs, none equal to the tip
   variant), and the string's only occurrences anywhere this seat can read are inside
   round 78's own wave dispatch text quoting the claim. The unresolvable-string fact itself
   re-derives (exit 128 above); the location of a 41-character tip citation inside a
   round-77 record does not re-derive from anything this scribe can read.
   *Captured-by:* none — no rule required a cited full hash to be resolvable or
   width-checked; the spot-check's ancestor check tested existence and ancestry of
   abbreviated tokens, not the record's literal bytes.
   *Fix:* every cited full hash is `git cat-file -e`-able; C1's counter resolves a
   correction's `at` with `git rev-parse --verify` plus a 40-hex width check; and a report
   audit grades the record's literal token width, never a repaired abbreviation.
2. **`stale-line-pointer`** — a record cites a line anchor that never held in the landed
   bytes.
   *Evidence pointer:* the round-77 report
   (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-77/kama.md`) routes readers to the LOG
   §Round 77 entry at `LOG.md:3130`; the round-77 spot-check's conformance defect 1 records
   that the heading is at `LOG.md:3137` and that `LOG.md:3130` never resolved. Re-derived
   by this seat at the wave cut, at the sealed revision and in the worktree (identical in
   that range):
   `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show
   6c1550a14babaca092cfcc3106f792d695652200:LOG.md | awk 'NR>=3126 && NR<=3142 {printf
   "%d|%s\n", NR, substr($0,1,150)}'` → line 3130 is the middle of a round-76 correction
   sentence ("before the outside closure that changes a path outside `LOG.md`,
   `SCORECARD.md`,") and the `## Round 77 — baseline receipts bind, two registers account,
   the round-76 facts are graded (2026-11-04)` heading is at line 3137.
   `registry/cited-path-corrections.tsv` has no `LOG.md` row, so the miss was never
   disclosed there.
   *Captured-by:* none at the round-77 cut — KQ95 requires an evidence pointer to resolve
   at the measured commit or be disclosed in `registry/cited-path-corrections.tsv`;
   neither held, and the pointer surfaced only through the spot-check's manual read.
   *Fix:* route as round-78 duty D9; pointer repairs are appended corrections naming the
   old and the new anchor (KQ26), never in-place rewrites; C1's F4 correction is the same
   class for the SCORECARD divergence pointer, and a report's line pointers are re-derived
   at the tip before the report is committed.

## Attack dispositions

The L1 integrates the wave's attack findings into this section after the wave settles;
this seat files no attack of its own and pre-judges nothing.
