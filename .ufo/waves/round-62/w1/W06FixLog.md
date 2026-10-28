# W06FixLog — post-freeze fix log entry (round 62, kama)

Axis: calibration. Seat: scribe, advisory leaf. This file records the three
post-freeze instrument repairs (defect, red-before, fix, predicate invariance)
and returns the text for `LOG.md`. No verdict on C1/C2, no commit, no edit to
lane source.

Tip at measurement: `65d7cad0fce90e34de37527cde22e97b63b118bf`.
Frozen base: `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`.
Scratch: `/fast/scratch/hyaku/kama-r62/w/W06FixLog` (removed after receipts were
copied to `.ufo/waves/round-62/w1/out/W06FixLog/`).

## Sources read

- `.ufo/waves/round-62/controls/freeze.txt` — C1/C2 predicates and the stated fix list.
- `tools/round62-c1-counter.py` at tip (`git show 65d7cad0:…`) and in the working tree.
- `tools/round62-c1-counter.py:1-24` (frozen predicate docstring), `:130,139,165`.
- `tools/kama-live-replay.py` at `a959fd90`/`6c25a77e` (pre-fix) and at `65d7cad0`/tree.
- `tools/kama-completion-live.py:408` (emits `checks['hold_released']`).
- `.ufo/waves/round-62/measured/c1-before-fix.txt` (captured pre-fix traceback).
- `.ufo/waves/round-62/w1/out/A02C1HoldTamper/c1-hold-tamper-counter-live-receipt.json`
  (genuine live receipt used as the grading input).
- `.ufo/waves/round-62/w1/{A01C1PortRace,M01C1AttackThe,M05C1AttackThe,M06C1AttackThe}.md`.
- `registry/capability-claims-r62.tsv:12` (`live-receipt-replay` bound row).
- `corpus/lessons/round-62.md` (Mistakes rows `vacuous` ×2, `reference-drift` ×2).

## Measured red-before / green-after

All three red states were reproduced in scratch from the pinned bytes; no live
server was started for this seat. Working directory `$S` =
`/fast/scratch/hyaku/kama-r62/w/W06FixLog`.

### 1. `grade()` None guards — tip bytes crash instead of rejecting

```
$ python3 $S/probe.py
receipt: …/A02C1HoldTamper/c1-hold-tamper-counter-live-receipt.json
stored check names: [17 names incl. hold_released]
tip   pristine: checks=17 inconsistent=['unexpected-checks']
tip   tampered: CRASH AttributeError: 'NoneType' object has no attribute 'get'
tree  pristine: checks=18 inconsistent=[]
tree  tampered: checks=18 inconsistent=['completion_envelope', 'completion_finish_reason',
 'completion_model_id', 'completion_fingerprint', 'completion_usage',
 'completion_timings', 'completion_deterministic']
```

The tampered input rewrites `captures.completion.body` to `__kama_mut__` without
updating `body_sha256` — exactly the shape the counter's own `log`/`tamper`
controls produce. Tip line 130 `u = cj.get('usage') or {}` dereferences the
absent parsed body. This is the same crash independently hit live by
`A02C1HoldTamper` and in replay by `M01C1AttackThe`, and captured at
`.ufo/waves/round-62/measured/c1-before-fix.txt`.

### 2. `hold_released` name guard — genuine receipt rejected as extra key

`tip pristine: inconsistent=['unexpected-checks']` above is the defect, isolated
on an otherwise all-true receipt: 17 recomputed checks true, but `out` omits
`hold_released` because the tip guard tests `'hold' in checks` and the tool
emits `hold_released`. `required` then differs from `stored`, so `score()`
returns `met=False`. Tree gates on `'hold_released'` and yields
`inconsistent=[]`.

### 3. `kama-live-replay.py --selftest --scratch <nonexistent>`

```
$ python3 $S/klr-prefix.py --selftest --scratch $S/klr-new     # 6c25a77e bytes
EXIT=1
Traceback (most recent call last):
  File "…/klr-prefix.py", line 582, in _selftest
    d = tempfile.mkdtemp(prefix="klr-st-", dir=root)
FileNotFoundError: [Errno 2] No such file or directory: '…/klr-new/klr-st-xxj06jft'

$ rm -rf $S/klr-new2
$ python3 tools/kama-live-replay.py --selftest --scratch $S/klr-new2   # 65d7cad0 bytes
… 48 × pass …
KLR_SELFTEST pass=48 fail=0
EXIT=0
```

The fixed run also demonstrates the root creation (`$S/klr-new2` exists after
the run) — the pre-fix run never created `klr-new`.

## Text for LOG.md

Paste under the Round 62 section (the L1 owns `LOG.md`; this is text only):

```markdown
## Round 62 — post-freeze instrument repairs: C1 counter grading, replay selftest scratch (2026-10-28)

- Three post-freeze repairs to round-62 instruments. Each defect was reproduced red from the
  pinned bytes and the repaired state reproduced green in scratch, and no frozen predicate text
  changed: `tools/round62-c1-counter.py` lines 1–24 (the C1-r62 docstring) are byte-identical to
  `65d7cad0:tools/round62-c1-counter.py` (`cmp` clean), and
  `.ufo/waves/round-62/controls/freeze.txt` is unmodified since `6c25a77e`.
- `grade()` None guards (`tools/round62-c1-counter.py:130,139`). Defect: the tamper control
  rewrites `captures.completion.body` without updating its `body_sha256`; `cap()` correctly
  returns `None`, then `grade()` read `cj.get('usage')` and raised
  `AttributeError: 'NoneType' object has no attribute 'get'` instead of rejecting the receipt.
  Red: tip bytes crash on the tamper family (`A02C1HoldTamper` live run, `M01C1AttackThe`
  replay, `.ufo/waves/round-62/measured/c1-before-fix.txt`). Fix: `(cj or {}).get('usage')`
  and `(cj or {}).get('timings')`. Green: the same receipt now rejects on seven disagreeing
  replay checks (`completion_envelope`, `completion_finish_reason`, `completion_model_id`,
  `completion_fingerprint`, `completion_usage`, `completion_timings`,
  `completion_deterministic`). Predicate unchanged because the repair only stops dereferencing
  an absent body; the graded check set and the “every graded check recomputed true” clause are
  untouched.
- `hold_released` name guard (`tools/round62-c1-counter.py:165`). Defect: the counter gated on
  `checks['hold']`, which the tool never emits (`tools/kama-completion-live.py:408` emits
  `checks['hold_released']`); a genuine receipt therefore recomputed 17 true checks yet was
  rejected with `inconsistent=['unexpected-checks']`. Red: reproduced with the tip bytes against
  the captured live receipt; `M05C1AttackThe`/`M06C1AttackThe` hit the same key mismatch. Fix:
  gate on `'hold_released'`. Green: `inconsistent=[]` on the same receipt. Predicate unchanged:
  the clause names the emitted check; no clause was added or removed. Boundary retained: the
  check stays conditional, so deleting `checks['hold_released']` also drops it from the graded
  set and still yields `inconsistent=[]` (measured, 18→17 checks) — the repair restores the
  emitted check, it does not make the check mandatory.
- `kama-live-replay.py` selftest scratch root (`tools/kama-live-replay.py:582`). Defect:
  `--selftest --scratch <nonexistent>` called `tempfile.mkdtemp(dir=root)` before `root`
  existed, raising `FileNotFoundError: …/klr-st-xxxx` and exiting 1. Red: reproduced from
  `6c25a77e:tools/kama-live-replay.py`. Fix: `os.makedirs(root, exist_ok=True)` before
  `mkdtemp` (committed in `65d7cad0`; blob sha256
  `29b473989fbbe01dd72cbb075d8096fde3b8d45c0c1395566de16d4c14fd605c`). Green:
  `KLR_SELFTEST pass=48 fail=0` exit 0 from a nonexistent scratch root. Predicate unchanged:
  the repair only lets the frozen C2 template
  `python3 %T/tools/kama-live-replay.py --selftest --scratch %S/klr`
  (`registry/capability-claims-r62.tsv:12`) emit its frozen pattern; template and pattern are
  untouched.
- Disposition: the two counter repairs are present only as uncommitted working-tree changes at
  tip `65d7cad0` (counter sha256
  `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415` in the tree vs
  `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d` at the tip), and the tip
  bytes still reproduce both defects; the replay fix is committed. A tip-measured C1 green is
  attributable to the tip instrument only after the L1 commits the counter repair.
```

## Why the frozen predicate text is unchanged

- `cmp` of `git show 65d7cad0:tools/round62-c1-counter.py | sed -n '1,24p'` against the working
  tree's lines 1–24 is clean (`head-docstring.txt` vs `wt-docstring.txt`, both 1226 bytes). The
  docstring is the frozen C1-r62 sentence.
- `git diff` of the working-tree counter is exactly three one-line hunks at 130, 139 and 165 —
  all inside the grading body, none in the docstring, usage block or acceptance clause.
- `freeze.txt` is tracked since `6c25a77e` and has no working-tree modification (`git status`
  silent for it).
- The C2 side changes no registry row: the `live-receipt-replay` row already froze the command
  and pattern; the repair only makes its scratch root creatable.

## Findings for the canonical judge (advisory)

1. **Commit boundary.** Tip-committed counter bytes cannot produce `met=True`: a genuine
   receipt is rejected `unexpected-checks`, and a non-parsing tampered body crashes the process.
   The `met=True` output in `A01C1PortRace` was produced by the working-tree counter file, and
   `M01C1AttackThe`/`A02C1HoldTamper` show the tip-byte failures. Until the L1 commits the two
   repairs, no C1 green is attributable to the tip instrument.
2. **Conditional guard limit.** Deleting `checks['hold_released']` from a receipt yields
   `inconsistent=[]` (18→17 graded checks), so the hold-release check is enforced only when the
   receipt records it. This is a byte-edit path against receipt grading; attack seats own its
   disposition. Recorded here because the name-guard repair could otherwise be read as making
   the check mandatory.
3. **No grading semantics widened.** The None guards turn an absent body into `False` for its
   dependent checks; the acceptance clause (`alltrue and verdict_ok and live and not
   inconsistent`) is unchanged.

## Not claimed / out of scope

- No C1 or C2 verdict, no full live counter rerun by this seat (`A01C1PortRace`'s `met=True`
  is cited, not re-derived here), no `--selftest` claim beyond the two runs shown.
- No tool installed or upgraded; `pacman` not invoked (host-wide pause).
- No commit, push, or mutating git/jj command; no sibling-lane or fleet-repo access.

## Artifacts

`.ufo/waves/round-62/w1/out/W06FixLog/`: `probe.py` + `probe.out` (tip vs tree grade on
pristine/tampered receipt), `guard-boundary.out` (key-deletion boundary),
`klr-before.out` (pre-fix `FileNotFoundError`), `klr-after.out` (48/48 pass),
`head-counter.py` (tip counter bytes), `klr-prefix.py` (`6c25a77e` replay bytes),
`head-docstring.txt` / `wt-docstring.txt` (predicate `cmp` pair).

Report: .ufo/waves/round-62/w1/W06FixLog.md
fixes_logged=3 red_reproduced=3 green_reproduced=3 predicate_text_changed=0 counter_repair_committed=0
