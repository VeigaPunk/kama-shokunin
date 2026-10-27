# W01LessonReview — round 56 (kama): Gate and Mistakes completeness of `corpus/lessons/round-56.md`

Seat: W01LessonReview (leaf, no subagent dispatch). Axes named: **calibration** (primary — lesson
fidelity against the contract, its own receipts and the tree) and **operability** (secondary — the
Gate's source rows and counters). Judged on calibration.

Tip under review: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (lane `HEAD`; base
`e10b6d39af450e8d652be9ac2986768b531fe13f`). Lane tree read-only; this seat wrote only
`.ufo/waves/round-56/w1/out/W01LessonReview*` and its scratch, then removed the scratch.
No counter was edited, no battery/census/measurement run was executed to decorate the review
(the battery writes into `measured/`, outside this seat's write bounds; see Limits).

Contract applied: `templates/round-prompt.md` §2b.1 (Gate: URL, access date, ≤25-word located
quote for **every new row**; every `status`/`recheck`/`used-by` change logged old→new),
§2b.2 (census before→after pasted with exit codes), §2b.3 (one mined mistake:
class · evidence · captured-by · fix, and "a fix counts only once shown able to fail"), plus
`corpus/QUALITY.md` KQ45/KQ96 (quote re-checked and re-counted at the cited copy), KQ60
(census summary names every warning class with its count), KQ63 (a "shown able to fail" check
exits nonzero and the receipt carries the exit), KQ79 (report quotes the census whole).

## Verdict

The Gate is **structurally present but quantitatively defective**: both new rows carry URL,
access date, section and a located quote inside the ≤25-word bound, but one declared word count
is wrong, the census delta the round itself created is absent, and the row-touch/append-only
ledger line the contract requires is missing. The Mistakes section is **incomplete against the
lesson's own header claim**: it carries one row (round-55 defect 2) while the header says the
round "answers … routed defects 1, 2, 4, 5, 6, 7, 9, 10", and the one row's "fix shown able to
fail" sentence is **false as written** — the pasted sweep exits 0. Two further defect classes are
visible at the tip and are not recorded at all: every C1/C2 measurement receipt the lesson cites,
and the lesson file itself, are **untracked** at `efc6b3ec`; and the C1 target's "fails the
battery's expected-detected assertion" is **never exercised** by the committed battery.

Severity order: **S1** untracked lesson + cited receipts (the row-1 class recurring in-round, and
the S512 `used-by` cell names an unresolvable path); **S2** false "fix shown able to fail";
**S3** header's eight-defect claim unsupported (only defect 2 recorded); **S4** unexercised kill
clauses (C1 mutant expectation inverted; C2 designation-mutation clause has no fixture);
**S5** Gate word-count error (S513: 16 declared, 18 actual); **S6** census after-measurement
absent (`end.out` does not exist) and the before-sentence violates KQ60; **S7** no row-touch /
append-only statement; **S8** no evidence line for the round's own LOG entry (0 `Round 56` lines
in `LOG.md`).

## Measured facts (exact commands, outputs, exits)

Receipts beside this report: `review-measurements.out`, `review-hashes.out` (both `tee`d from the
runs below, `TMPDIR=/fast/scratch/hyaku/kama-r56/W01LessonReview`).

1. **The lesson is not in the tip tree.**

   ```
   $ git rev-parse HEAD
   efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
   $ git ls-files --error-unmatch corpus/lessons/round-56.md
   error: pathspec 'corpus/lessons/round-56.md' did not match any file(s) known to git
   Did you forget to 'git add'?
   exit=1
   $ git show efc6b3ec:corpus/lessons/round-56.md >/dev/null; echo show_exit=$?
   show_exit=128
   $ git status --porcelain -- .ufo/waves/round-56 corpus/lessons/round-56.md
   ?? .ufo/waves/round-56/build_spec.py
   ?? .ufo/waves/round-56/census/
   ?? .ufo/waves/round-56/measured/
   ?? .ufo/waves/round-56/w1.ready
   ?? .ufo/waves/round-56/w1.ready.dispatched
   ?? .ufo/waves/round-56/w1/
   ?? corpus/lessons/round-56.md
   ```

   The freeze commit `efc6b3ec` contains only `controls/base-c1.out`, `controls/base-c2.out`,
   `preregistration.json`, `sources/ld.so.8.html`, `sources/rtld-audit.7.html`,
   `corpus/SOURCES.md` (+4), and the four tools (`git show --stat efc6b3ec`).

2. **Every measured receipt the lesson cites is untracked.**

   ```
   $ for f in .ufo/waves/round-56/measured/{base-c1,build-c1,build-c2,m-drop-ldaudit}.out \
              .ufo/waves/round-56/census/{start,end}.out; do
       printf '%s: ' "$f"; git ls-files --error-unmatch "$f" >/dev/null 2>&1; echo "tracked_exit=$?"; done
   .ufo/waves/round-56/measured/base-c1.out: tracked_exit=1
   .ufo/waves/round-56/measured/build-c1.out: tracked_exit=1
   .ufo/waves/round-56/measured/build-c2.out: tracked_exit=1
   .ufo/waves/round-56/measured/m-drop-ldaudit.out: tracked_exit=1
   .ufo/waves/round-56/census/start.out: tracked_exit=1
   .ufo/waves/round-56/census/end.out: tracked_exit=1
   ```

   `census/end.out` additionally **does not exist on disk** (`test -e` → exit 1), so the lesson's
   `## Census before→after` "After" line cites an artifact that is neither tracked nor present.

3. **The declared word counts.** `len(quote.split())`: S512 quote = **15** (matches the lesson's
   "15 words"); S513 quote = **18** (the lesson says "16 words"). Both are inside the ≤25 bound.
   Measured by this seat over the committed snapshots (tags stripped, entities decoded, whitespace
   collapsed — `review-hashes.out` §S512/S513): each quote occurs **once**, S512 inside §DESCRIPTION
   (`.ufo/waves/round-56/sources/rtld-audit.7.html`, sentence split at lines 89-91 across markup) and
   S513 at §`LD_AUDIT` (`.ufo/waves/round-56/sources/ld.so.8.html`). A byte-literal `grep` for either
   quote fails because both snapshots split the sentence across markup and line breaks — the
   Gate's quotes are correct, only S513's count is wrong.

4. **Frozen digests hold.** `sha256sum` of `tools/round56-replay-code-audit.py` =
   `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` and of
   `tools/round56-prereg-check.py` =
   `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, identical at the worktree,
   at `HEAD`, and to the preregistration digests (`git cat-file blob efc6b3ec:<path> | sha256sum`
   for both).

5. **Registry append-only, round commit.** `python3 tools/sources-append-only.py --from
   e10b6d39af450e8d652be9ac2986768b531fe13f --to efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` →
   `added S512 (allowed)` / `added S513 (allowed)` / `no append-only violations`, **exit 0**.
   `git diff --stat e10b6d39 efc6b3ec -- corpus/SOURCES.md` = 4 insertions (+2 rows, +2 blank
   lines), 0 deletions: no existing row's `status`/`recheck`/`used-by` changed.

6. **Receipt exit codes (round-55 defect 4).** Five of the six receipts carry `exit=`; the
   exception is `measured/build-c2.out`, which is 2 lines (`tip=…`, `present=1 … met=True`) and
   `grep -c 'exit='` → `0`, while the preregistration C2 target states "exit 0" for that run.
   `census/start.out` also records no exit code (its `exit 0` in the lesson is the re-derived exit
   of an equivalent replay, per `.ufo/waves/round-56/w1/out/X06Census.md` §Contradictions).

7. **C1 kill leg is not exercised as the lesson asserts.** `tools/round56-env-leg-battery.py:50`
   runs the mutant as `run("m-drop-ldaudit", mutant, "missed", …)`; `run()` (line 30) passes iff
   `returncode == 0 and fields["ld_audit"] == expected`, so the committed battery **passes** the
   kill leg. The lesson's "prints missed and fails the battery's expected-detected assertion" is a
   counterfactual (`--expect detected` against the mutant) that no receipt records; no battery
   exit is recorded anywhere. Read statically — this seat did not run the battery (it writes into
   `measured/`, outside its write bounds).

8. **C2 kill clause 4 has no fixture.** `tools/round56-prereg-check.py` has no selftest and no
   designation-mutation control; `grep -rn designation .ufo/waves/round-56/{measured,controls}`
   returns nothing. The preregistration's "if a one-field designation mutation remains green"
   clause is therefore unmeasured.

9. **The lesson's one "fix shown able to fail" is false.** The pasted sweep is
   `for p in …; do test -e "$p" || echo "missing $p"; done`, whose status is the last `echo`:

   ```
   $ for p in .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out \
              .ufo/waves/round-55/c1/battery/m-extra-in-tree.out; do
       test -e "$p" || echo "missing $p"; done; echo "sweep_exit=$?"
   missing .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
   missing .ufo/waves/round-55/c1/battery/m-extra-in-tree.out
   sweep_exit=0
   ```

   The lesson says "the same `test -e` sweep exits nonzero for each absent named receipt". It
   exits 0 (KQ63). The two receipts are indeed absent (both `missing` lines above; deletion commit
   confirmed: `git log --diff-filter=D` attributes both to `c2c05e30`, matching the round-55
   spot-check defect 2), so only the demonstration is wrong, not the premise.

10. **Census warning counts.** `census/start.out` (99 lines) = **97 W04, 1 W01, 0 E**. The live
    freeze-tip run adds exactly one line — `kama W04 S513 duplicate url
    man7.org/linux/man-pages/man8/ld.so.8.html across scopes` — i.e. **98 W04, 1 W01, 0 E**
    (peer receipt `.ufo/waves/round-56/w1/out/X06Census/start-vs-live.diff:7`; this seat did not
    rerun the census). The lesson writes only "(standing W01/W04 warnings)", which names no count
    (KQ60) and omits that the round's own new row adds a W04.

11. **No LOG entry.** `grep -c 'Round 56' LOG.md` → `0`; `LOG.md` is unmodified in the worktree.

## Claimed-defect ledger (header says "answers … defects 1, 2, 4, 5, 6, 7, 9, 10")

| Defect (round-55 spot-check) | Observed state at `efc6b3ec` | Support in the lesson |
|---|---|---|
| 1 roster diverged / re-freeze | Landed in the preregistration: roster = 1 `kill` (`m-drop-ldaudit`) + `control` + `positive-control`, `vector_analyses: {}` | **none** — no Gate/Mistakes sentence records the closure |
| 2 stale lesson-named receipts | Recorded as Mistakes row 1; premise reproduced | recorded (fix demo false — S2) |
| 4 receipts carry no exit codes | Partial: `measured/build-c2.out` and `census/start.out` carry none | **none** |
| 5 leg assertion too weak | Partial: battery compares field equality (`:30`), but the kill leg's expectation is inverted (`:50`) | **none** |
| 6 anchor revision element (S510/S511) | Unfixed: those rows are byte-unchanged in the round commit, no `supersedes S51x —` row exists | **none** (carried, unrecorded) |
| 7 uncommitted late outputs | Recurred and now includes this lesson and all `measured/`, `census/` files (facts 1–2); round-55 still carries 305 uncommitted entries (`V04LateOutputs.md`) | **none** |
| 9 attack-share classification basis | `.ufo/waves/round-56/w1/spec.json` records 64 items with roles (`reviewer 16, critic 8, mutation-tester 8, executor 8, scout 8, sentinel 4, revenger 4, scribe 4, connector 2, simplifier 2`) but no attack/non-attack classification or count | **none** |
| 10 stale SCORECARD labels | Fixed **in the worktree only** (`M SCORECARD.md`): depth row → "evidence re-anchored round 55"; calibration row → `42` closures incl. round 55, "latest outside closure … round-55-verifier-spotcheck.md (admitted)" | **none**; the edit is uncommitted |

## Proposed corrections (precise; not applied — this seat edits no lane file)

All are appends to `corpus/lessons/round-56.md`, preserving the round-55 wording as history (KQ26).

**C1 — Gate, S513 word count.** Replace `(16 words)` with `(18 words)` in the S513 bullet.
Supporting sentence to add: "Recounted at the committed snapshot:
`len("A list of user-specified, ELF shared objects to be loaded before all others in a separate
linker namespace".split()) == 18`; the quote is at §`LD_AUDIT` (lines wrapping across markup, so a
byte-literal grep fails — strip tags and collapse whitespace, as in
`.ufo/waves/round-56/w1/out/X07Anchors/x07-quote-anchor-check.py`)."

**C2 — Gate, census delta for the new row.** Append after the S513 bullet:

> The round's own registry append adds one warning class instance: live at `efc6b3ec`,
> `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` prints
> `98 W04, 1 W01, 0 E`, exit 0, where the pre-freeze horizon printed `97 W04, 1 W01, 0 E`
> (`.ufo/waves/round-56/census/start.out`, 99 lines). The added line is
> `kama	W04	S513 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes`
> (S67/S79 already carry that URL); W04 does not change lane status
> (`.ufo/waves/round-56/w1/out/X06Census/start-vs-live.diff:7`).

**C3 — Gate, row-touch / append-only statement (contract §2b.1).** Append: "No existing row's
`status`, `recheck` or `used-by` changed this round: `git diff --stat e10b6d39 efc6b3ec --
corpus/SOURCES.md` = 4 insertions, 0 deletions, and `python3 tools/sources-append-only.py --from
e10b6d39af450e8d652be9ac2986768b531fe13f --to efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` prints
`added S512 (allowed)` / `added S513 (allowed)` / `no append-only violations`, exit 0."

**C4 — Gate, candidates preamble.** Prepend the round-55 form ("Candidates considered this
round …"), naming S512 and S513 as the only candidates opened, with the evidence that
`.ufo/waves/round-56/sources/` holds exactly those two snapshots. (Advisory: the contract requires
Gate lines only for new rows; the preamble is the round-55 precedent, not a hard obligation.)

**C5 — Gate, optional snapshot digests.** S512/S513 bullets omit the snapshot byte count/digest
that round-55 Gate lines carry. If added, use
`a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153` for `rtld-audit.7.html`
(receipt `.ufo/waves/round-56/w1/out/X07Anchors.md`).

**C6 — Mistakes row 1, replace the false demonstration.** Replace the final sentence ("Fix shown
able to fail: the same `test -e` sweep exits nonzero for each absent named receipt.") with:

> Fix shown able to fail: `m=0; for p in .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
> .ufo/waves/round-55/c1/battery/m-extra-in-tree.out; do test -e "$p" || { echo "missing $p";
> m=1; }; done; (exit $m)` prints both `missing` lines and exits **1**; the bare form quoted in
> the row exits **0** because its last command is `echo` (KQ63), which is why the earlier wording
> was wrong. The absence premise itself is unchanged and reproduced at `efc6b3ec`.

**C7 — New Mistakes row 2 (in-round recurrence, the highest-severity gap).**

> **class: stale-premise — the lesson and the receipts it cites are uncommitted at the freeze.**
> Evidence: `git ls-files --error-unmatch corpus/lessons/round-56.md` exits 1 and
> `git show efc6b3ec:corpus/lessons/round-56.md` exits 128; all four `.ufo/waves/round-56/measured/`
> receipts and `census/start.out` are untracked; S512's `used-by` cell names
> `corpus/lessons/round-56.md`, which therefore does not resolve at the tip. Captured-by: none —
> KQ95 grades `SCORECARD.md`/`SHONEN.md`/`SKILL.md` pointers only, and no criterion covers a
> lesson's own cited artifacts (same gap row 1 names). Fix: land the lesson, `measured/`, `census/`
> and `SCORECARD.md` in a successor commit that cites the receipts' sha256s, and treat
> `git ls-files --error-unmatch <path>` exiting nonzero as the failing condition this fix must
> prevent (the check is already discriminating: it exits 1 for every untracked path above and 0 for
> `controls/base-c1.out`).

**C8 — New Mistakes row 3 (unexercised kill clauses).**

> **class: vacuous — a target clause no committed control exercises.** Evidence: the C1 member
> `m-drop-ldaudit` runs as `--expect missed` (`tools/round56-env-leg-battery.py:50`), so the
> battery's expected-detected assertion the C1 target names never runs; the C2 kill rule's
> "one-field designation mutation" clause has no fixture (`grep -rn designation
> .ufo/waves/round-56/{measured,controls}` → nothing) and `tools/round56-prereg-check.py` carries no
> selftest. Captured-by: KQ20 (a grading counts only when something can make it fail) and KQ25
> (a kill needs the subject's declared verdict and a completed run) — the round did not apply them
> to its own kill legs. Fix: run the mutant under `--expect detected`, commit that receipt with its
> exit (expected nonzero at the battery), and add one designation-flip fixture that the C2 counter
> must reject; show the fix failing by running the same two fixtures against the frozen counters.

**C9 — New Mistakes row 4 (the eight-defect header claim).** Either substantiate the header or
narrow it. If kept, append the disposition table from §"Claimed-defect ledger" above with one line
per defect (1, 4, 5, 6, 7, 9, 10) naming what landed, what is carried, and the evidence pointer;
defects 6, 7, 9 have no landed fix at `efc6b3ec` (S510/S511 rows byte-unchanged; 305+ uncommitted
entries; no attack classification in `spec.json`), so they must read "carried, not answered".

**C10 — Census section, replace the placeholder "After" line.** The committed text ("final output
and exit code are recorded in … `end.out` and this section is finalized after the end-of-round
run") is a promise, and `end.out` does not exist. Before the report is filed (KQ79 quotes the
census whole) run the frozen command at the landed tip, paste its output, and write, e.g.:
"After: same command → exit 0; `… census/end.out`; counts `N W04, M W01, 0 E`." Also correct the
"Before" line to the KQ60 form: "97 W04, 1 W01, 0 E (exit 0 re-derived by replay; `start.out`
records no exit code)". The `end.out` must be committed with its exit code, not left untracked.

**C11 — Criterion proposal (feeds `captured-by`).** KQ95 currently grades only
`SCORECARD.md`/`SHONEN.md`/`SKILL.md` pointers. Extending it (or adding KQ98) to "every path a
round lesson cites resolves at the round's landed tip, or is disclosed in
`registry/cited-path-corrections.tsv` under the existing `untracked` class" would have captured
rows 1 and 2 of the corrected Mistakes section; row 1's `captured-by: none` stays accurate for the
round as filed.

## Findings recap

- Gate rows exist for both new rows and the S512 quote/count/§ are correct; **S513's declared word
  count is wrong (16 → 18)**.
- Gate omits the census evidence the round itself changed (S513's W04) and carries a KQ60-invalid
  before-sentence; the after-measurement and `end.out` are absent.
- Gate omits the required row-touch/append-only line (nothing changed: 4 insertions, 0 deletions,
  append-only exit 0).
- Mistakes has the contract's single required row with class/evidence/captured-by/fix, but its
  "fix shown able to fail" demonstration exits 0 — false as written (KQ63) — and the section does
  not cover the round's own untracked lesson/receipts, the inverted C1 kill expectation, the
  fixture-less C2 designation clause, or defects 1, 4, 5, 6, 7, 9, 10 that the header claims.
- Counter digests and the C1 detection facts the lesson states are otherwise supported: both
  frozen sha256 match, base `ld_audit=missed exit=0`, build `ld_audit=detected exit=0`, mutant
  `ld_audit=missed exit=0` (receipts read as files; the mutant's *battery* assertion is the gap).

## Bounds, touched surfaces, out-of-scope

- **Touched:** `.ufo/waves/round-56/w1/out/W01LessonReview.md`, `review-measurements.out`,
  `review-hashes.out`. Scratch `/fast/scratch/hyaku/kama-r56/W01LessonReview` created with
  `TMPDIR` set and removed before yield. No lane product file, jj state, git index or fleet-root
  file was written; no tool was installed (nothing was needed).
- **Not run (and why):** `tools/round56-env-leg-battery.py` (writes `measured/` — outside this
  seat's write bounds; fact 7 is a static read), the C1 counter, the C2 checker, and the census
  (peer receipts `X06Census` and the committed controls were used; fact 10 is peer-measured and
  labelled as such). The live man7 pages were not re-fetched; the committed snapshots were read.
- **Out of scope:** claim predicate/kill-rule changes (frozen; advisory only), SCORECARD/LOG edits,
  the report, and any judgment of admission.
- **Artifacts cited from peers (read, not authored):**
  `.ufo/waves/round-56/w1/out/X07Anchors.md` (S512 anchor check, snapshot sha256),
  `.ufo/waves/round-56/w1/out/X06Census.md` (+ `start-vs-live.diff`) for the live census delta,
  `.ufo/waves/round-56/w1/out/V04LateOutputs.md` for the inherited 305 uncommitted round-55
  entries.
