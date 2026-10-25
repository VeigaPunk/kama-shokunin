# Review — C1 predicate parity and base-tip behaviour

Seat: L1Kama37.BrainySparrow (kama lane, round 37, w1)
Files read:
- `tools/round37-statement-audit.py` (290 lines, read in full: 1-63, 64-290)
- `.ufo/waves/round-37/preregistration.json` (C1 and C2 claims)

No file was edited. The counter was executed read-only; the lane jj state, git index
and fleet repo were not touched.

## 1. Is the C1 predicate sentence byte-identical in both files?

**Yes.** `PREDICATE` (the module constant at
`tools/round37-statement-audit.py:26-33`) and
`claims[C1].predicate` (`preregistration.json`) compare equal as Python strings:

```
IDENTICAL True
len_counter 319 len_prereg 319
sha256(counter) = cc881b7550bb68864f6e9254e6d9252e5cba8c9148ff53d0cde8a2e9012079bd
sha256(prereg)  = cc881b7550bb68864f6e9254e6d9252e5cba8c9148ff53d0cde8a2e9012079bd
```

The module docstring's rendering of the same sentence, whitespace-normalised, is also
equal to `PREDICATE` (`docstring_norm_identical: True`), so the file's own claim
"Predicate (identical in the preregistration, this file, and the receipt)" holds for the
two artefacts I can check here. I did not have a receipt artefact in scope.

## 2. Counting command at tip `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`

Command (verbatim from the assignment):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round37-statement-audit.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
```

Output line:

```
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
```

Exit code: **1**.

This matches the frozen do-nothing control byte for byte
(`.ufo/waves/round-37/controls/c1-noop.out`: same line, `noop_exit=1`), so the control
receipt and a live run agree at the base tip.

Fact derivation was checked independently of the printed line, at the same tip:
- `git show <tip>:.ufo/waves/round-36/census-end.out` fails → `census_tip is None`
  (path "exists on disk, but not in <tip>"), and the same path is also absent from the
  fleet `HEAD`, so R36-D1 cannot be satisfied at any tip currently reachable.
- `seat-exit-codes.json` at the tip contains `"name": "ScribeLog"`, `"name": "RevQ206"`
  and `"rc": 1` eight times; the two seat logs contain `rate_limit` and `429`.
- `corpus/lessons/round-36.md` blob at the tip is `6fb1ec15…d8ea` = `LESSON_BLOB`;
  `.ufo/reports/round-36/kama.md` blob at fleet `HEAD` is `8b7408e6…1604` = `REPORT_BLOB`.
  So `lesson_unchanged 1 report_unchanged 1` is genuinely re-derived, not assumed.
- `--selftest` at the same tip prints
  `SELFTEST empty_met=False bad_met=False good_met=True pass=1` and exits 0, so the
  accept path is reachable in principle (fabricated clean rows), while the real tip
  still yields `met False`.

## 3. Can a missing `corpus/lessons/round-37.md` meet the target?

**No.** `main()` does
`lesson = git_show(args.repo, args.tip, "corpus/lessons/round-37.md") or ""`; an absent
file yields `""`, `rows_of("")` returns `{}`, and every one of the four ids increments
`uncorrected`. `met` requires `uncorrected == 0`, so `met False`. The base-tip run above
is exactly that case: `git cat-file -e <tip>:corpus/lessons/round-37.md` exits 128 and
the counter prints `uncorrected 4 … met False` with exit 1. There is no fallback path,
no default lesson, and no other file name consulted.

## 4. Findings

### F1 (high) — R36-D3 does not join the named seats to `rc=1`

`holds()` for `R36-D3` (`tools/round37-statement-audit.py`, R36-D3 branch) checks
`'"name": "ScribeLog"' in exitcodes`, `'"name": "RevQ206"' in exitcodes`, and
`exitcodes.count('"rc": 1') >= 2` as three independent facts. The prereg statement is
"seat-exit-codes.json records ScribeLog and RevQ206 at rc=1", i.e. a per-entry pairing.

Demonstrated false accept: rewrite the real JSON so `ScribeLog`/`RevQ206` have `rc: 2`
and two unrelated seats have `rc: 1`; `holds("R36-D3", "R36-D3: ScribeLog RevQ206 429", …)`
still returns `True` (mutant `"rc": 1` count 8, but none belongs to the named seats).
The same mutation is what kill_rule calls "restates a forbidden … rc class" for the row,
yet it is invisible on the fact side. Fix would be to parse the JSON and assert
`rc == 1` for the two named entries; I did not edit the counter, per assignment.

### F2 (medium) — R36-D1 tests "contains", not "ends"

The statement is "census-end.out is tracked at the tip and ends 'kama ok'"; `holds()`
does `"kama\tok" in census_tip`. A census whose last line is a failure still passes:

```
holds D1 contains-not-last: True   # census_tip = "kama\tok\tx\nkama\tFAIL\n"
```

Because the census file is absent at the base and at fleet `HEAD`, this leniency only
bites once a tip commits a census file with a stale/duplicated ok line. It also accepts
an ok line whose third column is an arbitrary path (`kama\tok\tx`), while the do-nothing
control's fabricated row uses the real `SOURCES.md` path.

### F3 (medium) — duplicate correction rows: last occurrence wins, wrong restatements survive

`rows_of()` overwrites `found[sid]` on every matching line. A first row that restates a
forbidden id followed by a clean row passes:

```
dup last-good -> uncorrected 3 false_corrections 0 ... (D2B accepted)
  rows = "R36-D2B: … S359" then "R36-D2B: … (clean)"
```

The predicate says "contains a correction row naming its id, the row carries no wrong-id
restatement"; under last-wins, the file can carry a forbidden restatement and still be
scored corrected. This is also how an "append-only" lesson can be gamed: append the
clean row last and never retract the bad one.

### F4 (medium/low) — D2A has no forbidden-id set, but its statement names the wrong id

`forbidden_in()` returns `None` for `R36-D1` and `R36-D2A`. The D2A statement reads "the
staged native_api.mdx row is S371, not the lesson's S366", so `S366` is the wrong id the
statement names, and the C1 kill_rule says "a correction row that restates a forbidden
wrong id … fails the claim". A row `R36-D2A: S371 native_api miswritten (lesson claimed
S366)` is scored corrected (`uncorrected` drops by exactly one, `false_corrections 0`).

The counter's reading is defensible — only D2B and D3 carry explicit "must not restate"
clauses, and mentioning `S366` while naming `S371` is a corrective, not a restatement —
but it is an interpretation the frozen text does not settle. Either the kill_rule should
be read as covering only D2B/D3, or `forbidden_in` should gain a D2A branch that rejects
`S366` as the claimed id. Recorded as ambiguity, not as a proven counter bug.

### F5 (low) — row detection is `"<id>:"` substring anywhere on the line

`rows_of()` scans every line for `sid + ":"`; prose such as "as noted for R36-D2B: …"
counts as a correction row, and the required Markdown table form (`| R36-D2B | … |`)
would not be detected at all. The lesson author must therefore emit exactly
`ID: …` lines. Not a defect against the frozen text (which says "correction row"),
but a format constraint that is nowhere stated in the preregistration.

### F6 (low) — counter and preregistration are untracked at the tip

`git ls-tree <tip> tools/` contains no `round37-*` file and `git ls-files
.ufo/waves/round-37/` is empty in the lane. The predicate pins the r36 lesson blob and
the r36 report blob, but nothing pins the counter's own bytes to a commit, so the
scoring logic is not reproducible from the tip tree; the tip's committed bytes alone
cannot re-run C1. Worth pinning `tools/round37-statement-audit.py` (and the
preregistration) at whatever tip the claim is scored against.

## 5. Residual risk and verification gaps

- Only the base tip was exercised as instructed. A future tip has no committed
  `census-end.out` (absent at base and at fleet `HEAD`), so R36-D1 is currently
  unsatisfiable from committed bytes regardless of the lesson file; if the census is
  only on disk it will score `census_tip is None` and the claim fails on D1 alone.
- C2 was out of scope and not run; its do-nothing receipt is present in
  `.ufo/waves/round-37/controls/c2-base.out`.
- I did not verify a "receipt" predicate copy (none was named in scope), and I did not
  edit `round37-statement-audit.py` — F1/F2/F3 are reported, not patched.

## Verdict

Predicate parity: **pass** (byte-identical, 319 chars, equal SHA-256). Base-tip run:
`uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`,
exit **1**, identical to the frozen no-op control. A missing
`corpus/lessons/round-37.md` **cannot** meet C1 (4 uncorrected, exit 1). The counter
carries three leniency defects against its own frozen statements (F1 high, F2/F3
medium) that should be fixed or explicitly accepted before C1 is scored on any tip that
actually supplies the lesson file.
