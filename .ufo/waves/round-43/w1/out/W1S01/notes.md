# W1S01 notes — facts not verifiable from the evidence under test

1. **No receipt records an exit code.** `.ufo/waves/round-35/controls/c2-base.out`,
   `.ufo/waves/round-35/c2-after.out`, `.ufo/waves/round-35/c1-noop.out` and
   `.ufo/waves/round-35/c1-after.out` each hold exactly one stdout line (verified with
   `git cat-file -p 895793e:...`, one line each). The exit codes in the drafted Exit-map cells
   (0 / 1 / 2) are derived from the frozen source only — `tools/round35-coverage-audit.py:104-134`
   and `tools/round35-statement-audit.py:151-199` — not from a recorded status. The
   preregistration (`.ufo/waves/round-35/preregistration.json`, `do_nothing`) asserts exit 1 for
   the two do-nothing controls, but the `.out` files do not carry an exit code.

2. **Measured-receipt provenance is not recorded.** `c1-after.out` / `c2-after.out` contain the
   summary line only — no argv, evaluated revision or timestamp. I cannot verify which revision
   produced them; I can verify that the line equals the preregistration `target` verbatim and that
   the file exists at the freeze commit. `.ufo/waves/round-35/c1-working.out` and
   `c2-working.out` print the same target lines, so they are equally target-matching; I did not
   treat them as the measured receipt for want of provenance. No committed `.md`/`.json`/`.txt`
   at 895793e names any of the four `{c1,c2}-{after,working}.out` files
   (`git grep -n -E 'c1-after|c2-after|c1-working|c2-working' 895793e -- '*.md' '*.json' '*.txt'`
   returns only unrelated round-28/round-31 hits). The only receipt names the preregistration
   pins are the two do-nothing controls.

3. **No counter was executed against the lane.** The base and measured lines in the Self-test
   cells are quoted from the committed receipts; I did not re-run either counter, so "met" values
   reported in this notes file are transcribed, not re-derived.

4. **Placement of the rows is not verifiable.** There is no `round35` occurrence in SKILL.md at
   895793e (`git show 895793e:SKILL.md | grep -c round35` = 0, file is 1375 lines), so no existing
   section owns these rows. I validated them inside a throwaway clone under a new
   `### Round-35 instrument registry rows` heading; the gate only requires a 5-column table whose
   header cells match, so any such section works. I cannot verify where the integrator will put
   them.

5. **The lane clone's working tree changed during the session, not by me.** The first
   `git -C /fast/scratch/kama-r43/clone status --porcelain` was empty; a later one showed two
   untracked files, `corpus/knowledge/runtime-health-surface-processes.md` and
   `corpus/lessons/round-43.md`. I wrote nothing inside the clone (every read used
   `git show 895793e:<path>`, `git cat-file`, or the gate at `--rev 895793e`), and I cannot
   attribute those writes from this seat.

6. **The `sha256` pin must be backticked.** `tools/round43-registry-audit.py:78`
   (`SHA_RE = re.compile(r"sha256 `([0-9a-f]{8,64})")`) and its pins clause at
   `tools/round43-registry-audit.py:165` require the form ``sha256 `hex```, not `sha256 hex`.
   Both drafted rows use the backticked form; a plain-space form would count as one C1 pin
   mismatch even though it is textually "sha256 <12 hex>".

7. Tool installs: none. No package manager, network fetch or binary install was used.
