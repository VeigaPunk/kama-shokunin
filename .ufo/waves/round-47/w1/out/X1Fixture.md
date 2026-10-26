# X1Fixture — C1 adversarial fixtures for append-only-audit v2 (round 47, lane kama)

**Verdict: 18 constructed repos, 18/18 events agree with `git diff --numstat` and with the hand-derived
expectation; the ten assigned attack shapes find no numstat disagreement and no literal contradiction of the
v2 docstring, but they expose three soundness defects (the audited set is taken from the tip tree only; the
tool never resolves `declared_at`; a declared binary file is skipped silently), two metric artifacts
(blank-line and final-newline restoration), one contract-pattern trap (`**`, `[`, zero-match rows) and one
tool/counter shape divergence (CRLF contract). Of the eight, only the unresolved-`declared_at` and
CRLF-contract faults are visible to the frozen counter's contract leg; the other six are shared with it.
All eight are latent on the lane at
3a09a1d93dcc16799cf6c4b48786e6440af134c4: no file the contract declares was ever deleted or renamed in the
lane's history, so the C1 measurement numbers are unaffected.**

## 1. Instrument under test (pinned before any fixture ran)

```
$ git -C kama-shokunin show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/append-only-audit.py | sha256sum
5d47bc77e9bde41a1af1fcba449e60fd027d9ed30fbf2770a5a53f177856f874  -
$ sha256sum kama-shokunin/tools/append-only-audit.py      # working tree at lane tip 46a924e0
5d47bc77e9bde41a1af1fcba449e60fd027d9ed30fbf2770a5a53f177856f874  tools/append-only-audit.py
$ python3 append-only-audit-pinned.py --selftest --scratch $S
AOA_SELFTEST pass=15 fail=0        # exit 0
```
Bytes are the measured v2 (identical to the lane blob at the build commit and to the lane working tree at
the time of this run). Contract at 3a09a1d9: `sha256 57ac17253522ec12c311341e564cd38e52a189aa0d0044c1d7a666f443c76608`
— same bytes as the lane working tree.

## 2. Method

One git repo per case under `$S/fx/<case>` (`git init -q` in its own dir, `rev-parse --show-toplevel`
asserted equal to that dir before the first commit, identity only via `-c`/env, `GIT_CONFIG_GLOBAL=/dev/null`).
Each repo carries `registry/append-only-contract.tsv` at its tip and is audited exactly as a lane user would:

```
python3 append-only-audit-pinned.py --repo $S/fx/<case> --to HEAD --json
```
For every reported event the driver recomputes `git -C <repo> diff --numstat --no-renames <parent> <commit> -- <file>`
and compares the deletion cell with `deleted`, then compares the whole event list field by field
(`commit, file, deleted, restored_max, restored_best, restored_by, status`) and the exit code with a literal
expectation stated per case in `run_cases.py`. `--files <path>` controls were run on the cases where the
contract expansion is the suspect. The frozen counter's own `read_contract` / `contract_files` / `recompute`
were imported (read-only) and run on the same repos (`counter_crosscheck.py`).

Suite exit code 0 (all 18 as expected): `run.log`. Machine-readable result: `results.json`.

## 3. Cases

`rc` is the tool's exit code; `d` deleted; `max` restored_max; `by` restored_by. Every event's `deleted`
equalled the `--no-renames` numstat deletion cell (checked per event in `results.json` → `numstat`).

| # | construction | tool (rc) | numstat | verdict |
|---|---|---|---|---|
| C01 | `assets/blob.bin` (NUL) loses 35 lines; text sibling loses 35 | rc 1, 1 event: `plain.txt d=35 max=0 unrestored` | binary `-\t-\tassets/blob.bin`; `0\t35\tassets/plain.txt` | as constructed; binary silently skipped |
| C02a | declared file `git mv` out of the contract, then back | rc 0, 1 event: `doc.md d=30 max=30 restored by=c3` | rename-detecting numstat also `0\t30` (rename out) | correct |
| C02b | declared file `git mv` to a **sibling path inside** the contract | rc 0, **0 events** | `0\t30\tdata/doc.md` | **D1**: move invisible via contract; `--files` → `d=30 unrestored` rc 1 |
| C03 | declared file deleted, recreated byte-identical | rc 0, 1 event `d=30 max=30 restored by=c3` | `0\t30` | correct |
| C04 | only 25 **blank** lines deleted, then 25 unrelated blank lines added | rc 0, 1 event `d=25 max=25 restored by=c3` | `0\t25` | **D3**: restoration is vacuous |
| C05a | side branch deletes 30 lines; merge lands the side tree | rc 1, 2 events `c2 d=30 max=0`, `cm d=30 max=0` | `0\t30` twice | correct final verdict; **D8** order effect |
| C05b | same, `merge -s ours` (side deletion never lands) | rc 0, 1 event `c2 d=30 max=30 restored by=cm` | `0\t30` | **D8**: credited to the merge, not to `c3` |
| C06 | 60 000-line file, 30 000 deleted, 20 distinct-blob window commits, restored | rc 0, 1 event `d=30000 max=30000 restored by=c23` (24 commits) | `0\t30000` | correct; no scale failure |
| C07a | CRLF file, 25 lines restored with **LF** endings | rc 1, 1 event `d=25 max=0 unrestored` | `0\t25` | correct (byte identity) |
| C07b | CRLF file, 25 lines restored with CRLF (control) | rc 0, `d=25 max=25 restored by=c3` | `0\t25` | correct |
| C08 | `\ No newline at end of file` **on both sides**, hunk header 26 | rc 1, `d=26 max=0 unrestored` | `1\t26` | correct: markers neither counted nor swallowing a line |
| C08b | final newline removed in the event commit | rc 1, `d=26 **max=1** partial restored_best=c2` | `1\t26` | **D7**: phantom line restored in the event commit |
| C09 | contract rows `corpus/lessons/**/*.md`, `docs/c[1].md`, one zero-match row | rc 0, **0 events** | `corpus/lessons/r1.md` lost 30: `0\t30` | **D4**: `r1.md` unaudited; files = `['corpus/lessons/sub/r2.md','docs/c1.md']` |
| C10 | three `declared_at` rows that resolve to nothing (absent file, line 999, line without "append") | rc 1, normal event `d=35` | `0\t35` | **D2**: tool accepts all three; counter rejects all three |
| C10b | `declared_at` without `:line` | rc 2 `could-not-evaluate: … bad path, rule or declared_at` | — | correct refusal (counter also probs) |
| C11 | contract written with CRLF endings | rc 1, normal event `d=27` | `0\t27` | **D6**: tool accepts what the counter rejects |
| C12 | contract absent at the audited tip | rc 2 `could-not-evaluate: git show …` | — | correct refusal |
| C13 | declared file **deleted and left deleted** (40 lines) | rc 0, **0 events**, `files=0` | `0\t40` | **D1**: the violation the audit exists for is invisible |

Expectations vs. reality, one line each: every `deleted` above was also recomputed by hand from the
constructed history; the four shapes where a plausible expectation was *not* met were my own construction
errors, re-derived and re-run (C05a/C05b: `rev-list --topo-order --reverse` is `c1,c3,c2,cm`, so `c3` is not
in `c2`'s window; C06: the restore commit is `c23`, not `c22`; C08b: the child line text was literally `L4`,
not `L line 4`, so `held=0` was correct until the construction was fixed). No substantive finding rests on a
corrected expectation; D1–D7 were each observed on the first run of their case.

## 4. Defects

### D1 (severe, purpose-defeating) — the audited set is the *tip* tree, so a deleted or moved-out declared file is never audited
`tools/append-only-audit.py:22` (docstring: "expanded over `git ls-tree -r --name-only <to>`"),
`:105-107` (`expand`), consumed at `:192-201`; the same shape in the frozen counter at
`tools/round47-append-audit-v2-check.py:32` and `:264-268`.

```
$ python3 append-only-audit-pinned.py --repo fx/c13-file-deleted-at-tip --to HEAD
summary commits=2 files=0 events=0 restored=0 partial=0 unrestored=0            # exit 0
$ python3 append-only-audit-pinned.py --repo fx/c13-file-deleted-at-tip --to HEAD --files data/doc.md
event fc630cf6cabb data/doc.md deleted=40 restored_max=0 status=unrestored …    # exit 1
```
C02b is the same mechanism with a rename inside the declared set (`files=['data/doc2.md']`, 0 events;
`--files data/doc.md` → `deleted=30 unrestored`). Deleting a declared file is the primary append-only
violation and it is the one shape the contract path cannot report. The tool's own selftest cannot catch this:
`declared-file-removed` passes an explicit `--files` list (`tools/append-only-audit.py:343-348`). The frozen
counter inherits it: on the same repo `contract_files` returns `[]` and `recompute` returns `[]`
(`counter-crosscheck.log`), so the `lane` leg scores agreement with the blind spot.

Proposed fix (round 48; the counter is frozen, so this cannot be repaired inside round 47's measurement):
expand over the union of paths that appeared anywhere in the audited history — `git log --no-renames
--format= --name-only <to>` — keep the tip set as `files_at_tip` for reporting, and diff the union set. A
contracted pattern that is non-empty at tip but whose file is gone at tip would then produce an `unrestored`
event as it should.

### D2 (medium, divergence) — `declared_at` is shape-checked only, never resolved
`tools/append-only-audit.py:97` accepts any `[^:]+:\d+`; nothing opens the file or the line. C10 (absent
`MISSING.md`, line `README.md:999` of a 2-line file, `README.md:2` with no declaration) → tool audits
normally, `exit 1`, no diagnostic. The counter's contract leg does resolve them
(`round47-append-audit-v2-check.py:289`, `:294`):
```
contract line 2: declared_at path MISSING.md absent at tip
contract line 3: README.md:999 does not hold a line containing 'append'
contract line 4: README.md:2 does not hold a line containing 'append'
```
So the tool can audit a contract whose declarations are fiction; only the counter's separate leg protects the
claim. Proposed fix: resolve each row at parse time against `<to>` (`cat-file -e <to>:<path>`, line range,
declaration token) and exit 2 `could-not-evaluate` on an unresolvable row — or, if the tool must stay
tolerant, emit `declarations: [{row, path, line, resolved: bool}]` in `--json` and a `declarations=0/N` count
in the text summary so the leniency is visible.

### D3 (medium, metric attack) — an all-blank-line deletion is "restored" by blank lines added elsewhere
`tools/append-only-audit.py:207-216` (held over line *values*), `:217-218` (status). C04:
```
git diff -U0 c1 c2 → @@ -31,25 +30,0 @@  with 25 "-" lines that are empty        (25 deleted)
git diff -U0 c2 c3 → @@ -15,0 +16,25 @@  with 25 "+" lines that are empty        (elsewhere)
tool: deleted=25 restored_max=25 restored_by=c3 status=restored                    exit 0
```
No blank line was restored; 25 different empty lines were inserted 15 lines higher. This is not a docstring
contradiction — the preregistration's `limits` already say "a line restored elsewhere in the file counts" —
but for empty lines that sentence makes the verdict vacuous: any commit that adds blank lines flips the
status, and a whitespace cleanup that removes 25 blank lines becomes an `event` at all. Proposed fix
(deterministic, no position tracking): when every distinct line in `D` is empty or whitespace-only, set
`vacuous: true` and never reach `restored` without that flag (text: `status=partial vacuous=1`); a
hunk-anchored measure is the deeper alternative.

### D4 (medium, contract coverage) — `**` means "at least one directory level", `[` is a character class, zero-match rows are silent
`tools/append-only-audit.py:106` (`fnmatch.fnmatchcase` on the full path); counter `:265` identical.
```
fnmatch.translate('corpus/lessons/**/*.md') → (?s:corpus/lessons/(?>.*?/).*\.md)\z   # r1.md NOT matched
fnmatch.translate('docs/c[1].md')           → (?s:docs/c[1]\.md)\z                   # matches docs/c1.md
```
C09 tree holds `corpus/lessons/r1.md`, `corpus/lessons/sub/r2.md`, `docs/b1.md`, `docs/c1.md`, the literal
`docs/c[1].md`; tool `files=['corpus/lessons/sub/r2.md','docs/c1.md']`. `r1.md` then loses all 30 lines:
`0\t30\tcorpus/lessons/r1.md` in numstat, **0 events, exit 0**. The literal `docs/c[1].md` cannot be named at
all, and `corpus/lessons/**/nomatch/*.md` (zero matches) is accepted without a word. The lane's current row
is `corpus/lessons/*.md` (single star, 79 matches at the measured commit), so this is a trap for the next
contract edit, not a present miscount. Proposed fix: reject `**` (or implement globstar explicitly) and any
pattern whose expansion is empty, with the offending row number; document that `[` cannot be escaped in a
path pattern.

### D5 (low-medium) — a declared binary file is skipped without a trace
`tools/append-only-audit.py:170` (`parts[1].isdigit()` drops the `-` of a binary numstat), summary `:221-224`.
C01: `assets/blob.bin` loses 35 of 40 lines, `numstat -\t-\tassets/blob.bin`, `git diff --stat` says
`Bin 470 -> 55 bytes`; tool reports only the text sibling, and `summary` has no field that says a declared
file was skipped (`files=2 events=1`). The docstring documents the skip, but a contract is allowed to declare
an archive or a lockfile, and the audit then silently covers less than it says. Proposed fix: collect
`skipped_binary: [paths]` into `--json` and `skipped=N` into the text summary.

### D6 (low, tool lenient where the counter is strict) — a CRLF contract is accepted by the tool and rejected by the counter
`tools/append-only-audit.py:87` (`lines[0].rstrip("\r") != HEADER`) and `:96` (cell `.strip()`) vs
`round47-append-audit-v2-check.py:248` (`lines[0] != HEADER`). C11 (header bytes
`b'path\trule\tdeclared_at\tnote\r\n'`): tool audits and reports `deleted=27`, exit 1; counter
`contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note`, `files=[]`. If the lane's
contract ever acquired CRLF endings the tool would keep auditing while the claim's `contract` leg fails.
Proposed fix: drop `.rstrip("\r")` in the tool (match the frozen definition), or widen both together.

### D7 (low) — a final-newline change creates a line that is deleted and restored in the same commit
`tools/append-only-audit.py:207-216`. C08b: parent ends `…L line 4\n`; child ends `…L line 4` (no newline).
`numstat 1\t26`; the hunk contains `-L line 4` / `+L line 4` / `\ No newline at end of file`. `D` therefore
holds one `L line 4`, the child holds one, `K` holds none → `held=1` at the **event commit itself**:
`deleted=26 restored_max=1 status=partial restored_best=c2`. numstat agrees with the count, so no
disagreement — but the measure credits a restoration that is only a terminator change. Proposed fix: build `K`
as `M_parent - D - A_common` (subtract the added multiset as well) so a `-x/+x` pair netts to zero.

### D8 (informational, definitional) — restoration credit depends on merge topology
`tools/append-only-audit.py:207` (`window = commits[i:]`). C05a: topo order `c1,c3,c2,cm`; `c3` still holds
all 40 lines yet `c2`'s window is `[c2, cm]`, so `restored_max=0`; the final verdict (both events unrestored,
exit 1) is nonetheless the right one for the audited tip. C05b (`-s ours`): the side event is credited to
`cm`, not to the `c3` that already held the lines. This is exactly what the docstring defines, and the tool's
selftest merge case passes only because the merge commit lands after the side commit. No fix proposed; noted
because a lane that resolves a deletion by merge order will see restorations attributed to the merge commit.

### Confirmed good (round-46 D1/D2 fixes hold under attack)
C07a/C07b: `\r` stays part of the line, an LF recopy restores nothing and a CRLF recopy restores 25.
C08: on a hunk with `\ No newline` on both sides the parse yields exactly the 26 the hunk header and numstat
say (the markers are neither counted nor allowed to consume a line). C03 delete+recreate, C02a rename
out/back, C06 60 k lines with 24 commits and a 20-blob window, and the C10b/C12 refusal paths (exit 2) all
behaved as specified.

## 5. Lane relevance at 3a09a1d9 (read-only, `git -C` on a `--shared` clone)

```
contract at 3a09a1d9 == working tree: 57ac1725…; 7 rows; expansion 85 files (79 corpus/lessons/*.md + 6)
rows matching zero files: none
git log --diff-filter=D --name-only  -- <each declared path|corpus>   → empty
git log --diff-filter=R -M --name-status -- <each declared path|corpus> → empty
```
So today's C1 numbers (85 files, 5 events) are unaffected by D1/D4, and no declared file has been deleted or
renamed: every defect above is latent on this lane, not active. It becomes active the first time a declared
file is deleted, renamed, or a contract row is edited to a `**`/`[` pattern.

## 6. What the frozen counter cannot see (and what it can)

- Shared with the counter by construction (it re-implements the same definitions): D1, D3, D4, D5, D7, D8.
  Demonstrated by running the counter's own `read_contract`/`contract_files`/`recompute` on the same repos —
  C13 `files=[] events=[]`, C02b `files=['data/doc2.md'] events=[]`, C09 `r1.md` absent from `files`,
  C04 `restored` (`counter-crosscheck.log`). Independent ground truth here is only `git diff --numstat`, which
  none of these defects violate: they are coverage and semantics faults, not counting faults.
- Caught by the counter's own legs: D2 (`declared_at` resolution, contract leg) and D6 (header byte-exactness).
  Both are places where the tool is *more permissive* than the frozen definition.

## 7. Reproduce

```
S=/fast/scratch/hyaku/kama-r47/X1Fixture        # scratch of this seat, removed after the run
python3 run_cases.py "$S" "$S/pin/append-only-audit.py" "$S/results.json" \
    /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py     # exit 0
python3 counter_crosscheck.py fx/c13-file-deleted-at-tip fx/c02b-rename-inside-contract \
    fx/c09-contract-patterns fx/c01-binary-nul fx/c04-blank-lines                          # exit 0
```
`fixtures.tar.gz` holds the 18 repos exactly as audited (also rebuildable from `run_cases.py`;
`GIT_CONFIG_GLOBAL=/dev/null`, so no host config is needed). `SHA256SUMS` covers every artefact.

## 8. Limits, risks, disclosures

- Constructed repos with `threshold=20` and one contract per repo; this exercises the tool's definitions, not
  the lane's real history (that is the counter's `lane` leg). Nothing here was run against a mutated lane:
  the shared clone was used only for `show`/`ls-tree`/`log`, and all fixtures live under the seat scratch.
- Four expectations were corrected after the first run because my fixture construction/ordering was wrong, not
  the tool's output (C05a/C05b window direction, C06 commit name, C08b line text); each corrected value was
  re-derived by hand from the constructed history and the run was repeated from empty repos. Disclosed so the
  record shows the goalposts did not move on D1–D7.
- No tool installs or upgrades were needed (pacman untouched, nothing added to PATH). No service was started;
  no network access was used. Scratch `/fast/scratch/hyaku/kama-r47/X1Fixture` was removed after the
  artefacts were copied.
- Wall-clock timings are not quoted: the host was under other lanes' load during this wave, so C06's runtime
  number would not be a measurement.
