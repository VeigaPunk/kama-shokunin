# SC02Lesson — round-83 lesson scribe (`corpus/lessons/round-83.md`)

Seat: SC02Lesson, leaf scribe, kama round 83 wave 1, 2026-11-04. Lane
`/home/vgpnk/Projects/shokunin/kama-shokunin` read-only throughout: no production file written, no
commit, no gate run. Lane tip read as `743c1060` (freeze) and `eae884ad` (mid-wave); base
`30d8eac394a8714fad3dc792b74a45a25b4366a2` and sealed `b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`
are the plan's.

Deliverable: `.ufo/waves/round-83/w1/SC02Lesson/round-83.md` — 80 lines, five sections in order.

## Behavior

1. Read `plans/round-83-claims.md` in full first; its blockquotes, fact tables, target lines and
   control lists were treated as frozen text and never edited.
2. Polled `.ufo/waves/round-83/w1/SK01SourceOpen/sources.json` (landed ~2.5 min after the seat
   started) and took the six rows' status, bytes, sha256, line numbers and quotes from it; no fetched
   fact was invented. Cross-checked by re-fetching all six URLs myself — every sha256 matches
   (`S566 eafc1b53…`, `S567 3ed17118…`, `S568 209087c3…`, `S569`/`S570 67ee4e2b…`, `S571 cc28e3b8…`).
3. Wrote the lesson: title/opening (plan, base, sealed, three claims and axes), `## Gate` (six rows,
   all `admit`, all dated 2026-11-04), `## Corrections` (the plan's three lines byte-equal plus one
   bullet per stale fact), `## Mistakes` (one row) and `## Frontier`.
4. Validated the lesson's correction container end-to-end in a scratch clone: filed the lesson and
   EX03's draft counter, appended the L1-side record backing, committed inside the clone, ran the
   counter — green; `--enumerate` and `--no-corrections` stay red as the plan requires.
5. Probed EX01's draft `--late` module in the same clone: green selftest and one red-capacity
   mutation for the three new arms.

## Gates

| gate | command | receipt | exit |
|---|---|---|---|
| lesson shape: lines, section order, six gate rows, quote words, block byte-equality | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/check-lesson.py` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/check-lesson.out` | 0 |
| C2 counter, honest (clone `166c2e0b`) | `python3 tools/round83-selfrecord-round82.py --repo .` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/probe-selfrecord-honest.out` | 0 |
| C2 `--enumerate` | same + `--enumerate` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/probe-selfrecord-enumerate.out` | 1 (`stale=3`) |
| C2 `--no-corrections` | same + `--no-corrections` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/probe-selfrecord-no-corrections.out` | 1 (`mismatches=3`) |
| EX01 draft selftest (clone `b946472a`, draft sha256 `3868a3ee…`) | `python3 tools/round81-append-debt.py --selftest` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/probe-selftest-green.out` | 0 (`pass=28 fail=0`) |
| unbound-path mutant (module from `0687b245`) | same | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC02Lesson/probe-selftest-unbound-mutant.out` | 1 (`pass=25 fail=3`) |

Scratch: `S=/fast/scratch/hyaku/kama-r83/SC02Lesson` (one `git clone --shared` plus the curl
cross-checks), deleted before yield; `git rev-parse --show-toplevel` was asserted equal to `$S/clone`
before every mutation, and all clone commits name `-C $S/clone`.

## Findings

1. **C2's `fix` leg cannot be satisfied by the plan's named containers.** `LOG-CORRECTION` lines and
   `#### round-<N> correction` blocks are excluded by the predicate's own "outside any
   correction-restatement region" rule: a run with only those containers prints `mismatches=3
   corrected=0 unbacked=3` exit 1 (`.ufo/waves/round-83/w1/EX03SelfRecord/final-records-only.out`),
   and ordinary receipt-binding lines outside them turn the same run green (`final-honest.out`). The
   L1 must append the latter or C2 goes red; the lesson's correction prose names the constraint.
2. **EX01's receipts are `not-run`.** `EX01LateBinding/EX01.json` declares the three arms
   `implemented-not-run` under a fleet rule forbidding test runs mid-wave, so no round-83 receipt yet
   shows them able to fail. The lesson states that plainly and cites this seat's executed probe
   instead of an unobserved claim; the L1 can reproduce with `EX01LateBinding/prove.py`.
3. **S571's DESCRIPTION sentence wraps** at 2146→2147, so no byte-exact single-line quote exists at
   2146. The Gate row says so; a C3 recheck row must not read the wrap as absence.
4. **`sources.json` carries a seventh row (`S571b`)** — a second `--line-porcelain` anchor on the same
   fetch, not one of the six named sources. The Gate table keeps six rows and names S571b inside
   S571's reason.
5. **The lane's filed lesson is the L1's integration, not this seat's draft bytes.** At 11:02 the L1
   wrote `corpus/lessons/round-83.md` (97 lines) from this draft: same three correction lines, byte-
   equal to the plan (verified), same Mistakes class, plus a `## Freeze divergences` section and a
   revised Mistakes evidence pointer (`.ufo/waves/round-83/measured/before/c1-debt-legB.out`, `KQ135`).
   Its Gate table is 8 cells per row and carries the access date only in the intro; this seat's draft
   carries it in every row as the item requires. The L1 owns that file; the difference is recorded, not
   edited by this seat.

## Out of scope / not done

- No lane write, no `git add`/commit in the lane, no `pre-report-gate.py`, no message outside the seat.
- Did not run C1's legs A/B/C or C3's counter: other seats own those receipts; the lesson names the
  claims, not their measured outcomes.
- One process deviation, disclosed: a single-line edit to my own `check-lesson.py` was made with
  `sed -i` before switching to `edit`; the receipt postdates the corrected file.

## Artifacts

- `.ufo/waves/round-83/w1/SC02Lesson/round-83.md` — the deliverable lesson.
- `.ufo/waves/round-83/w1/SC02Lesson/check-lesson.py`, `check-lesson.out` — shape gate and receipt.
- `.ufo/waves/round-83/w1/SC02Lesson/probe-selfrecord-{honest,enumerate,no-corrections}.out`.
- `.ufo/waves/round-83/w1/SC02Lesson/probe-selftest-{green,unbound-mutant}.out`.
