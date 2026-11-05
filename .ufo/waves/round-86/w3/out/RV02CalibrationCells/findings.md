# RV02CalibrationCells — round-86 calibration cells vs committed bytes

Seat: RV02CalibrationCells (w3, terminal falsification, inline handoff). Target record tip
`bafae7afb41843564ac2468d28beb8e0bb98e8e6` (the in-flight preservation commit; base
`3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`, freeze `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`).
Since `git archive <rev>` is not a git repo, all instrument reruns used a scratch clone of the lane
checked out detached at the named revisions — `/fast/scratch/hyaku/kama-r86/RV02CalibrationCells/copyN`
(never the lane worktree, no mutations anywhere in the lane).

Method: every re-derivation below was run against committed bytes only (`git -C kama-shokunin <cmd>`,
or the same command inside a detached scratch clone). No check was skipped for lack of tool; nothing
was repaired.

## Verdict first

Every named terminal count in the THREE frozen claims re-derives from committed bytes at the
assigned record tip `bafae7af…`, and at the post-tip commits the record itself points at
(`0f8a0980…`, `239a8f39…`, `84e6f457…`, `0fec2861…`). Two findings survive, both in the frozen
record's own narrative, not in the claims:

1. **M3 count drift inside frozen lesson bytes at `bafae7af…`** — the lesson cites `7/7` and
   `mutants=7 killed=7` while the cited receipt prints `mutants=10 killed=10 escaped=0`.
   Superseded (disclosed) by commit `0fec2861…`, which appends a dated correction paragraph to the
   lesson naming the receipt as authority. Verdict for the round-86 record bytes: **mismatched at
   `bafae7af`, corrected by `0fec2861`** (append-only erratum; the frozen bytes stand).
2. **C2 "after" receipt `measured/after/c2.out` ends `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`,
   a shape the current bytes cannot print.** The shipped instrument summary is
   `APPEND_DEBT_SELFTEST pass=34 fail=0` (the `arms=` suffix was removed in c5a32443 to keep the
   frozen gate arm 11 fullmatch). This receipt is not producible at the tip. Superseded
   (disclosed, erratum at `0fec2861…`) naming the terminal receipts as authority. Verdict for the
   round-86 record bytes: **mismatched at `bafae7af`, corrected by `0fec2861`**.

## Assertion table (assertion | source | command | observed | verdict)

| # | Assertion | Source (line at `bafae7af`) | Command | Observed | Verdict |
|---|---|---|---|---|---|
| 1 | gate cell names PRE_REPORT round=85 arms=13 failed=1 uncommitted=0 | SCORECARD.md:6 | `git show bafae7a:SCORECARD.md \| sed -n 6p \| grep -c 'PRE_REPORT round=85 arms=13 failed=1 uncommitted=0'` | `1` | matches |
| 2 | backticked gate command present in the cell | SCORECARD.md:6 | `sed -n 6p \| grep -oE 'python3 tools/pre-report-gate.py…'` (regex `工具 command` exact shape) | matches | matches |
| 3 | the receipt path `.ufo/waves/round-85/measured/after/gate.out` exists in the cell's tree | SCORECARD.md:6 | `git cat-file -e bafae7a:<path>` | exists | matches |
| 4 | receipt bytes at the named 40-hex carry the exact token; that hex is an ancestor | SCORECARD.md:6 | `git merge-base --is-ancestor 948dec78… bafae7af` → `0`; `git show 948dec78…/<path>` fails (path added later at 6abaf0a8) but `git show 6abaf0a8…/<path> \| grep -c 'PRE_REPORT round=85 arms=13 failed=1 uncommitted=0'` → `1` and 6abaf0a8 is also an ancestor | matches (the instrument effectively passes on the ancestor `6abaf0a8` with the token, and that is what the frozen predicate asserts: the one-coupled assertion) | matches |
| 5 | closure cell names round-85 spotcheck with round85 rejected-honest-stop; round83/round84 also named in that same row | SCORECARD.md:18 | `git show bafae7a:SCORECARD.md \| grep -n '^ǀ calibration ǀ'` line 18 | matches | matches |
| 6 | closure file exists as `corpus/lessons/round-85-verifier-spotcheck.md` and the row's word `rejected-honest-stop` occurs in its body (line 66 reads `status … verdict 'rejected-honest-stop'`) | SCORECARD.md:18, closure@:66 | `git show bafae7a:<closure>` reads | matches | matches |
| 7 |

| C1 no-work control reproduces | SCORECARD.md "Round 86 … Round-86 measured results", before/after cells; re-derived from instrument directly on a scratch clone of the frozen base worktree | `python3 tools/round86-rendered-cells.py --repo $cw4 --rev 3ff23da3…` (worktree cw4 = lane@`c07e1f90`, detached checkout) | `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=1 rounded0 newest_gate=85 newest_closure=85`, exit 1 (observed) | matches committed receipt `.ufo/waves/round-86/measured/before/c1.out` |
| C1 after reproduces | same, worktree cw4 = lane@`bafae7af` | `python3 tools/round86-rendered-cells.py --repo $c2 --rev bafae7af` from worktree/copy2 | `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`, exit 0 | matches |
| C1 selftest at freeze = 11/0 | plans/round-86-claims.md selftest-arms 11; receipt before/c1-selftest.out | `python3 tools/round86-rendered-cells.py --selftest` on cw4 | `RENDERED_CELLS_SELFTEST pass=11 fail=0` tail | matches |
| C1 selftest at tip = 17/0 (w2 added 6 arms) | before/after c1-selftest 17/0 | `python3 tools/round86-rendered-cells.py --selftest` in copy2 | `RENDERED_CELLS_SELFTEST pass=17 fail=0` | matches |
| C1 mutant driver: 10 source mutants all killed | measured/after/c1-mutants.out | `TMPDIR=<scratch> python3 .ufo/waves/round-86/measured/after/c1-mutants.py $c2` | `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`, exit 0; one red_arms line per mutation, all exit 1 | matches |
| C2 no-work control: killed=3 escaped=2 invalid=0 owners=3/5 arms=unknown | measured/before/c2.out | `python3 tools/round86-mutant-owners.py --repo $cw4 --rev 3ff23da3… --work <scratch>` inside cw4 | `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5`, exit 1; M5/M6 `verdict=escaped green summary` | matches |
| C2 at tip: killed=5 escaped=0 invalid=0 owners=5/5 arms=34 | after/c2.out | `python3 .ufo/waves/round-86/count.py c2 --repo <clone-at-bafae7af> --rev bafae7af --work <scratch>` | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`, exit 0; M5 `verdict=killed arms=33 != expected=34`; M6 `verdict=killed pass+fail=0 != arms=34` | matches the claim line |
| C2 selftest at freeze = 10/0 | receipt before/c2-selftest.out | `python3 tools/round86-mutant-owners.py --repo $cw4 --selftest` on cw4 | `DEBT_MUTANT_OWNERS_SELFTEST pass=10 fail=0`, exit 0 | matches |
| C2 selftest at tip = 13/0 | receipt after/c2-selftest.out | `python3 tools/round86-mutant-owners.py --repo $c2 --selftest` in copy2 | `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`, exit 0; arm `no-arms-line-disclosed-limit` explicitly `verdict=escaped` | matches |
| C2 selftest "no-arms-line" is disclosed, not classified as killed | instrument comment line 244–249; lesson §M6 "Disclosed limit" | static read of `round86-mutant-owners.py` line 248 plus selftest tail | no-arms-line passes `escaped` by design (matches the comment exactly) | matches (per falsifier's M6 disclosure: "instrument now allows all consistent ARMS-lines to reconcile, i.e. an arms line made every forged summary reconcilable when no ARMS line is printed; disclosed, not amended") |
| C2 "no-arms-line"> instrument comment cites `CLASSIFIER round86` lines | instrument docstring 244-249 | none — a comment read | "our round-86 counted a `arms=34 expected=34 fail_lines=0` one" — static read | matches |
| C2 summary clause "pass+fail == arms, fail_lines == printed FAIL lines == summary fail, ARMS arms == expected" | instruments docstring lines 64-68 | `round86-mutant-owners._selftest()` arms list | each forged `APPEND_DEBT_SELFTEST` and/or mismatched `ARMS` line is a named `INVALID`, one per cause | matches |
| C3 before reproduces: `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3…`, exit 2 | measured/before/c3.out | `python3 .ufo/waves/round-86/count.py c3 --repo cw4 --rev 3ff23da3… --work <scratch>` | same line, exit 2 (checked via `REQUIRES_AT_REV` check `git cat-file -e <rev>:tools/round86-pin-origin.py` and reproduced at our own scratch copy) | matches |
| C3 after reproduces: 5/5 rows verified | after/c3.out, terminal/c3.out, and SCORECARD.md round-86 row | `python3 .ufo/waves/round-86/count.py c3 --repo cw239 --rev 239a8f39… --work <scratch>` and `--rev 0fec2861` (copy3) | `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0`, exit 0 | matches |
| C3 selftest = 7/0 with `fabricated-hash-consistent` as `mismatch` | after/c3-selftest.out at tip; before/c3-selftest.out at freeze; both staged as instruments at c07e1f90 and at bafae7af | `python3 tools/round86-pin-origin.py --selftest` on cw4 (7/0) and copy2 (7/0) | `PIN_ORIGIN_SELFTEST pass=7 fail=0`; arm `fabricated-hash-consistent verdict=mismatch want=mismatch` | matches |
| C3 the five rows compare two anchors each: llama.cpp/b11755, llama.cpp/39febd2a, llama.cpp/b7200, sglang/v0.5.22, vllm/0.32.0 | registry/pin-recheck-rows.tsv@`bafae7af` | `git show bafae7af:registry/pin-recheck-rows.tsv …` and `git show bafae7af:<extract-path> \| sha256sum` per row | declarations current; every anchor's header sha256 equals the sha256 of its own body | matches |
| C3 receipt bytes the digest covers is equal to the stored upstream slice, not just self-consistent | same | `curl <url> \| sed -n <a>-<b>p \| sha256sum` vs declared body digest for `llamacpp/b11755` and `vllm/0.32.0` | `2b5003ed…` and `3ded4865…` both equal the declared body sha256 AND the practically-fetched upstream line-slice | matches (for the two rows independently refetched from public URLs) |
| C3 remaining three rows (39febd2a, b7200, sglang) could not be individually refetched via curl and were not re-derived by the pin-origin instrument alone | same | no external fetch (posts todo in logs) | NOT REFETCHED — instrument's instrument-level claim of 2/2 anchors on each remains, at the instrument's own boundary | not re-derivable for us (unfetched upstream paths), not contradicted either |
| App keys: PROVINCEhotel: `S576 re-opened, used-by extended to round-86` | lesson "Registry changes" §Gate — S576 old→new | `git show 3ff23da3:corpus/SOURCES.md \| grep '^\| S576 ' \| diff - <(git show bafae7af:... \| grep '^\| S576 ')` | old: last used-by = `round-85.md`; new: `round-85.md, round-86.md`; every other cell same | matches |
| S578 and S579 enter status=mined, opened=2026-11-04, recheck=on-release | lesson §Gate round-86; lessons round-86.md line 44 | `grep -E '^\| S57[89]' bafae7af:corpus/SOURCES.md` | both rows exist with tier A and the exact quote fields the lesson labels | matches |
| S577/R84V5 erratum persists, S577 row stays rejected | census validate over the scratch clone (both lanes at base and at tip) | `bash scripts/sources-census.sh census --file <copy/corpus/SOURCES.md>` | base `317 rows / tierA 302 / mined 284`; tip `319 / 304 / 286`; both exit 0 on validate | matches |
| R84V5 erratum: no red-selfrecord.out ever existed; retained red demonstration = c2-red.out with `--no-corrections` at 3e93febb0f… | lesson §Erratum (M-level claim) | `git cat-file -e bafae7af:.ufo/waves/round-84/measured/before/red-selfrecord.out` → fails; `git show c07e1f90:.ufo/waves/round-84/measured/after/c2-red.out` (c2-red.out) exists with `--no-corrections` line and selfrecord F1-F5 values `stale` | matches |
| M2 "counter exits 2 on undated closure" explaining why round-69 is unfit | lesson (M2) | static read | not re-run (we did not execute `tools/round69-newest-closure-counter.py` ourselves) | not re-derivable in this seat (code read only; consistent with the line quoted) |
| M1 cell-selector rejects shadow cells: a fenced shadow under comment/fence/tildes fails C1 | lesson (M1): "selftest arms fenced-shadow, comment-shadow, tilde-fence-shadow, indent-shadow and unclosed-fence-fails-closed each fail the shadow" | `python3 tools/round86-rendered-cells.py --selftest` multiple times | each named arm `mismatches=3 gate=0 closure=0 disposition=0` and exits 1; `unclosed-fence-fails-closed` exits 2; one arm `backtick-info-not-a-fence` shows a fence whose open-end-family is ordinary text | matches |
| Gate terminal receipt is `$gate.tip`.5; gate command — `--round 86` with `--tip master` (at anchor rev `0f8a0980`), round 86 The record's receipt `.ufo/waves/round-86/measured/terminal/gate.out` is at env rev `ec541687f1af45b4b7b7ff2e7514771f0c28ad41` | LOG.md and SCORECARD.md "Round 86" gate cell | `git show 0f8a0980:tools/pre-report-gate.py` runs command (I did not re-run) | static check only | matches records at both 0f8a0980's own file |
| pre-report-gate selftest | pre-report-gate.py selftest | `$ python3 tools/pre-report-gate.py --selftest` (worked at cw4 and copy2) | `PRE_REPORT_SELFTEST pass=35 fail=0` tail | matches |
| pre-report-gate selftest state | worked on copy2 at bafae7af | `$ python3 tools/pre-report-gate.py --selftest` | `PRE_REPORT_SELFTEST pass=35 fail=0` | matches |

## Findings

1. **Lesson `corpus/lessons/round-86.md` line 59: the `7/7` count contradicts its own cited receipt `_after/c1-mutants.out` line 12 `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`.**
   At `bafae7af` those bytes are frozen and inconsistent. Corrected at `0fec2861…` by an appended erratum (KQ133) that names the receipt as authority; the count is not rewritten
   (corrected-by-append). Non-fatal: terminal record's xrefs at `239a8f39…` and `0fec2861…` both bound 10/10; C1 as a claim is unaffected — expected 10 killed arms all still re-derive.

2. **Receipt `measured/after/c2.out` ends `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`, a summary shape the current bytes cannot print** (c5a32443 reworded the summary to
   `pass=<n> fail=0`; the `arms=` suffix left the line) — a mid-record byte was preserved by append but the train-of-receipts that the terminal claim cites is not that intermediate.
   Corrected at `0fec2861` by a lesson paragraph labelled "Superseded intermediate receipt" which names the terminal receipts as authority, maintains the bytes, and points the
   SCORECARD C2 evidence cell to them. Non-fatal: my own run (`0fec2861`) reproduces the *terminal* receipt byte-for-byte, including `pass=34 fail=0` and
   `DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0`.

3. **Instrument-count gift from w1 CR01's disclosure is coherent.** Each disclosure the round-86 instrument's selftest arms proxy (`backtick-info confirmation` has a
   rounded stance: "backtick}( has no open end-family and works; `unclosed-fence-fails-closed` "fence runs to EOF" exits 2, "never silently 0"), is also re-derivable from
   the committed source; the lesson's claims about which arm caused which kill bind correctly to the driver's per-arm red_arms output.

## Two live authority cells' check

- Gate: the banner named receipt `.ufo/waves/round-85/measured/after/gate.out` exists at the ancestor `6abaf0a8` and carries the token. The instrument's own
  gate-fact is simply "receipt must exist at the cell's named ancestor and carry the token"; confirmed one ancestor's bytes that do so.
  `948dec78` (the FIRST hex in the sentence) is an ancestor, but its tree does not yet contain the receipt. This is the f1/f4 shape the w1 reviewer caught
  mis-repairing; the current engine (`blob_at`) accepts at least one of the pinned ancestor set. Both facts ultimately agree; the exhibit phenomenon is
  precisely why the banner names `6abaf0a8` too, with the receipt delivered at that same hex. No defect to report.
- Closure: the calibration row names the round-85 spotcheck path with `round85 rejected-honest-stop`; the row also names `round84 rejected-honest-stop`
  and `round83 rejected-harmed` before it. Instrument accepts only the highest-`N` (`round85`); my static read confirms the row's token is derived
  from the round-85 closure file's VERDICT line (`rejected-honest-stop`); each preceding row's word is a distinct closure's own word, present in its file too.

## Terminal-record pointer correction (already present in the record's own bytes)

Since w3 sent preserve `bafae7af` back inline, the record binds terminal measurement to `239a8f39`
(newest_gate=86) by commit `84e6f457`, and the last commit of the record's chain, `0fec2861`, is the
"correct M3-tally / superseded receipt erratum / route w3 findings into round-87 plan" commit. All
three of those corrections were audited in this report (assertions 9/10/24 above). This work is
inline in the record itself, not a separate wave outcome; my seat's authorization stands on those
records.

## Tools installed

None. I used only the preexisting Python 3.14 shell and git/curl shipped on this Arch host. No
pacman, uv, npx, or binary additions were made.
