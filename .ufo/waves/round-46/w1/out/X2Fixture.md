# X2Fixture — round-46 C2 adversarial fixtures (tool vs frozen recompute vs byte-exact oracle)

**Verdict: the tool and the frozen counter agree on 19 of 20 adversarial fixtures and on the lane's own history (5 events, exit 1), but they agree *while being wrong* on 7 fixtures — on 6 of them a ≥20-line deletion of a declared file passes with exit 0 — and they disagree on 1 (a declared path that is a tree at tip), where the counter is wrong and the tool is right.**

All findings below are reproduced from scratch by one command; no lane file, index, jj state, counter or preregistration was modified.

---

## 1. Method

Fixtures are throwaway repos under `/fast/scratch/hyaku/kama-r46/X2Fixture/fx` (now removed; `run_fixtures.py` rebuilds them in ~2 s). For each fixture the driver records three independent readings:

| reading | what it is |
|---|---|
| **tool** | `python3 kama-shokunin/tools/append-only-audit.py --repo D --to <tip> --json` — exit code, `events`, stderr |
| **counter** | `round46-append-audit-check.py::recompute(D, <tip>)`, imported by path with `importlib` — the frozen independent recomputation |
| **oracle** | byte-exact reading of the contract: `git diff -U0` split into per-file sections and parsed **positionally** (the `---`/`+++` preamble ends at the first `@@`), tip line set from `git cat-file blob` **bytes**, without `split("\n")`'s phantom trailing empty element |

The oracle is what the docstring means literally: `tools/append-only-audit.py:15` "`deleted` = `-` lines of that diff (the `---` header excluded)" and `:17` "deleted lines (exact text) occurring as some *line* of `<file>` at `<to>`". Where the oracle is contested (CRLF, binary), the report says so explicitly.

```
mkdir -p /fast/scratch/hyaku/kama-r46/X2Fixture && export TMPDIR=/fast/scratch/hyaku/kama-r46/X2Fixture
python3 kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/run_fixtures.py "$TMPDIR"          # 20 fixtures
python3 kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/run_fixtures.py "$TMPDIR" --lane   # lane leg
python3 kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/summarize.py                       # evidence.md
```

`AOA_TOOL=<path>` replaces the tool under test (used for the proposed-patch replay in §6); fixtures are git repos whose toplevel is asserted equal to their own directory before the first commit (`run_fixtures.py:79-81`).

## 2. Matrix (20 fixtures)

`tool_vs_counter` = event-tuple set equality **and** tool exit code vs the exit code implied by the counter's events (the C2 lane leg's own predicate). `both_wrong` = tool ≡ counter but both ≠ oracle.

| case | tool rc | tool ev | counter ev | tool vs counter | tool vs oracle | counter vs oracle | both wrong |
|---|---|---|---|---|---|---|---|
| crlf | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | **True** |
| crlf2 (control) | 0 | 1 | 1 | AGREE | match | match | False |
| cr (lone CR inside lines) | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | **True** |
| nonl (no trailing newline) | 0 | 1 | 1 | AGREE | match | match | False |
| ws (trailing-space re-add) | 1 | 1 | 1 | AGREE | match | match | False |
| dups (30 identical lines) | 0 | 1 | 1 | AGREE | match | match | False |
| bin (NUL content) | 0 | 0 | 0 | AGREE | match | match | False |
| utf8 (invalid-UTF-8 tip blob) | **1** | 0\* | 0\* | AGREE\* | DIFFER | DIFFER | **True** |
| mode (mode-only change) | 0 | 0 | 0 | AGREE | match | match | False |
| ren (git mv + mv back) | 0 | 1 | 1 | AGREE | match | match | False |
| merge (evil merge, first parent) | 1 | 2 | 2 | AGREE | match | match | False |
| octo (octopus, deletion vs 1st parent) | 1 | 1 | 1 | AGREE | match | match | False |
| octo2 (octopus takes a side deletion) | 1 | 2 | 2 | AGREE | match | match | False |
| twice (same 25 lines deleted twice) | 1 | 2 | 2 | AGREE | match | match | False |
| large (50 000 lines) | 1 | 1 | 1 | AGREE | match | match | False |
| blank (25 blank lines removed) | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | **True** |
| trunc (30 blank lines → 0-byte file) | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | **True** |
| laneblank (507 blanks from a copy of lane SCORECARD.md) | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | **True** |
| dash (25 lines starting `--`) | 0 | 0 | 0 | AGREE | DIFFER | DIFFER | **True** |
| dir (declared path is a tree at tip) | 1 | 1 | 1 | **DISAGREE** | match | DIFFER | False |

Wall times: tool 0.032–0.048 s, counter 0.004–0.017 s per fixture; 50 000-line case 0.042 s / 0.016 s. Full per-case events, stderr and oracle tuples: `evidence.md`, `results.json`.

\* `utf8`: neither side produced events at all — the tool exited 1 on a `UnicodeDecodeError` traceback with 0 bytes of stdout, the counter's `recompute` raised; "0" is the parsed-event count, and `AGREE` here means both *failed to answer* (see D4).

## 3. Disagreement with the frozen recompute (1)

### D1 — counter: a declared path that is a tree at tip yields a tree listing as "lines" (counter wrong, tool right)

* Counter: `tools/round46-append-audit-check.py:101-102`
  `p = git(repo, "show", f"{rev}:{path}", check=False)` → `set(p.stdout.split("\n"))`.
  `git show <rev>:<path>` on a **tree** prints a listing and exits 0; the tool instead resolves blob ids (`tools/append-only-audit.py:63-70`, `cat-file --batch-check=%(objectname) %(objecttype)`) and treats a non-blob as absent (`:71-72`).
* Fixture `dir`: `LOG.md` (30 lines, one of them literally `child.txt`) is replaced by a directory `LOG.md/child.txt`.
* Commands and output (verbatim; fixture commit ids are regenerated on every rebuild, so the ids below are the ones in the shipped `results.json`):

```
$ python3 tools/append-only-audit.py --repo D --to HEAD --json
[{'commit': '491b27e4…', 'file': 'LOG.md', 'deleted': 30, 'restored_at_tip': 0,
  'status': 'unrestored', 'restored_by': None}]                       # tool exit 1
$ git -C D show HEAD:LOG.md | cat -A
tree HEAD:LOG.md$
$
child.txt$
$ counter recompute(D, HEAD) → deleted 30, restored_at_tip 1, status partial   # ← disagreement
```
Oracle: `deleted=30, restored_at_tip=0, unrestored` — the tool matches, the counter does not.
* **Impact:** the C2 `lane` leg compares `(commit, file, deleted, restored_at_tip, status, restored_by)` tuples, so on any repo where a declared file is a tree at tip the counter reports `lane=0` against a tool that is correct. Not reachable on the current lane (no declared path is a directory).
* **Proposed fix (counter is frozen — finding, not an edit):** replace `lines_at` with the tool's blob lookup, e.g. resolve `git rev-parse --verify -q <rev>:<path>` **and** require `git cat-file -t <oid> == blob`, else return `set()`.

## 4. Cases where tool and counter agree but both violate the contract (7)

### D2 — header exclusion by prefix discards content lines that begin with `--` (tool `:102`, counter `:115`)

```
            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
```
A deleted content line `-- dash comment 005` is rendered `--- dash comment 005`, which starts with `---` and is dropped as if it were the file header. Fixture `dash`:

```
$ git -C D diff --numstat HEAD^ HEAD -- LOG.md
0	25	LOG.md
$ python3 tools/append-only-audit.py --repo D --to HEAD --json
{… "events": [], "summary": {… "events": 0 …}}              exit 0        ← 25-line deletion invisible
```
Oracle: `deleted=25, restored_at_tip=0, unrestored`.

**This fires on the lane's own audited event.** Byte-exact / numstat counts at `0718b6abbda6` versus the tool's `deleted`:

| file | numstat / oracle | tool | dropped |
|---|---|---|---|
| `LOG.md` | 2292 | 2290 | 2 |
| `SCORECARD.md` | 2421 | 2417 | 4 |

The 6 dropped lines (read-only extraction from the lane, `git diff -U0 0718b6ab^1 0718b6ab`; verbatim in `lane-dash-lines.txt`): `--tip <full-commit>\` reads \`listed 3 observed 6 …`, `--rev <full-commit>\` reads \`registered 10 unregistered 2 …`, and four `--out .ufo/waves/round-20…/round-22…` run lines. `restored_at_tip` is undercounted by the same 4 on `SCORECARD.md` (2416 vs 2420), which is why the status (`partial`) happens to survive here.
* **Proposed fix:** parse `-` lines **by position** inside the file's own diff section (preamble ends at the first `@@`); see `proposed-fixes.diff` hunk 3, which also filters sections to the exact a-side path so a sibling under a directory named like the declared file cannot contribute lines.

### D3 — the phantom empty line makes every deleted blank line count as restored (tool `:77`, counter `:102`)

`frozenset(blob.split("\n"))` contains `""` for **every** newline-terminated file, and `{""}` for a 0-byte file. So a deleted blank line is always "held again at tip".

```
# laneblank: byte copy of the lane's SCORECARD.md, then every blank line stripped
$ python3 tools/append-only-audit.py --repo D --to HEAD --json
"deleted": 507, "restored_at_tip": 507, "status": "restored"          exit 0
# blank: 25 blank lines deleted, 0 blank lines left in the file
"deleted": 25, "restored_at_tip": 25, "status": "restored"            exit 0
# trunc: file of 30 blank lines truncated to 0 bytes
"deleted": 30, "restored_at_tip": 30, "status": "restored"            exit 0   (tip bytes: 0)
```
Oracle in all three: `restored_at_tip=0, unrestored`. The lane's declared files carry 507/285/103/143/60 blank lines, so this is not a contrived shape.
* **Proposed fix:** when the blob text ends with `"\n"`, drop the final `""` before making the set (`proposed-fixes.diff` hunk 2); a 0-byte blob then has no lines.

### D4 — an undecodable blob crashes the tool with exit 1 instead of the contract's exit 2 (tool `:51`, `:315-319`; counter `:94`, `:254`)

`subprocess.run(..., text=True)` decodes stdout with the locale codec in strict mode; the tool catches only `AuditError` (`:317`), while its contract says "Exit: … 2 could not evaluate" (`:30`). Fixture `utf8`: 25 text lines deleted, then the tip blob rewritten as `b"\xff\xfe\x00\x81 …"`:

```
$ python3 tools/append-only-audit.py --repo D --to HEAD --json ; echo $?
tool_exit=1
    data = data.decode(encoding, errors)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
stdout bytes: 0
```
The frozen counter fails the same way and further out: `recompute` raises `UnicodeDecodeError` (recorded as `counter_error` in `results.json`) and `main` only catches `EvalError` (`:254`), so no `selftest=… met=…` line is printed at all.
* **Proposed fix:** capture bytes and decode with `errors="surrogateescape"` in both tools (`proposed-fixes.diff` hunk 1). Equality stays byte-faithful and the tool then *reports* the event (see §6: `deleted=25 restored_at_tip=0 unrestored`, exit 1), which is the correct verdict rather than a crash.

### D5 — universal-newline translation folds `\r`, so CRLF text equals LF text (tool `:51`, counter `:94`)

Python's text mode translates `\r\n` and lone `\r` to `\n` (`subprocess` `_translate_newlines`, verified: `printf 'a\r\nb\rc\n'` → `'a\nb\nc\n'`). Git's line content keeps the `\r` (`core.autocrlf` unset; lane has no `.gitattributes`).

```
# crlf: 25 lines deleted while the file used CRLF, then restored with LF endings
$ git -C D cat-file blob <event>^1:LOG.md | od -c | head -1
0000000   c   r   l   f       l   i   n   e       0   0   0  \r  \n   c
$ git -C D cat-file blob HEAD:LOG.md     | od -c | head -1
0000000   c   r   l   f       l   i   n   e       0   0   0  \n   c
$ python3 tools/append-only-audit.py --repo D --to HEAD
event d8a8651dd2e1 LOG.md deleted=25 restored_at_tip=25 status=restored restored_by=7e79406b0827
summary commits=3 events=1 restored=1 partial=0 unrestored=0          exit 0
```
Oracle: `restored_at_tip=0, unrestored`. Fixture `cr` shows the second effect: a line containing a lone `\r` is split into phantom fragments, and the head fragment then matches an unrelated tip line → `restored_at_tip=25` while the byte text differs.
* **Proposed fix:** read bytes, decode with `surrogateescape` and no newline translation (hunk 1); "exact text" then means byte text.
* **Live exposure:** none today — the lane has no `.gitattributes` and the five files contain 0 `\r`; this is a definitional hole, not a current misreport.

## 5. Agree, and correct as specified (definitional notes for the L1)

* `nonl` — deleting 25 lines from a file without a trailing newline reports `deleted=26`: adding the final newline re-renders the last kept line as a delete+add. Text-equality and `restored_by` are right.
* `ws` — re-adding the same lines with one trailing space is `unrestored`, exit 1: "exact text" is strict. Correct as specified.
* `dups` — 30 identical lines cut to 5 reports `restored_at_tip=25, restored, exit 0`. Explicitly allowed ("duplicates may share one line", `:17-18`), but it is a real weakening of the gate: a mass deletion that leaves one copy passes.
* `bin` — a declared file with NUL bytes makes git print `Binary files … differ`; there are no `-` lines, so 0 events and exit 0. Consistent with the literal definition at `:15`, but the purpose clause ("deletes at least N lines") is defeated: binary declared content can be destroyed invisibly. Worth an explicit out-of-scope note in the contract text.
* `mode` — mode-only change: no event (correct).
* `ren` — `git mv LOG.md LOG2.md` is a 30-line deletion event; `git mv` back makes `restored_by` the rename-back commit (correct).
* `merge` — the evil merge is an event against its first parent (`deleted=25`), and the earlier mainline event's `restored_by` is the **side-branch** commit `a34be7db782a`, which is later in rev-list order but never restores anything on the mainline. This is what `:20-21` specifies ("first commit after the event commit in the rev-list order"), so it is correct — but a `restored_by` consumer should not read it as a repair commit.
* `octo` — the octopus's own first-parent deletion (30) is counted once; the other parents delete nothing.
* `octo2` / `twice` — the same logical 25 lines appear as two events (side commit + octopus; two separate deletions). Per-commit first-parent diffing, by design; event counts inflate accordingly.
* `large` — 50 000-line file, one 25-line event, tool 0.042 s / counter 0.016 s, identical tuples.

## 6. Proposed patch (validated, **not applied**)

`proposed-fixes.diff` (three hunks: byte I/O with `surrogateescape`, phantom-line removal, section-filtered positional parsing). Checked with `patch -p1 --dry-run` against a pristine copy (`dryrun_rc=0`) and replayed through the same 20 fixtures with `AOA_TOOL=<patched copy>`:

* tool `--selftest` → `AOA_SELFTEST pass=10 fail=0`;
* patched tool vs oracle: **20/20 match** (was 13/20), `both_wrong=0` (was 7);
* the 8 remaining disagreements are now all counter-only (`crlf`, `cr`, `utf8`, `blank`, `trunc`, `laneblank`, `dash`, `dir`) — i.e. exactly D1–D5, all on the frozen counter's side;
* `laneblank` under the patch: `deleted=507, restored_at_tip=0, unrestored`, exit 1.

This is a proposal for the L1/parent to decide on; the tool and counter on the lane were not modified.

## 7. Lane leg (read-only sanity, `96d329186e777080c03ac89fdd2366714d504dc3`, 295 commits)

* `tool` == `counter`: 5 events, same tuples, `tool_rc=1` (`lane.json`), matching the C2 spec's 5 events (0718b6ab ×4 files, dd9f5dc6 ×1).
* Independent `git log --numstat -m --diff-merges=first-parent` sweep (no diff text): **exactly the same 5** `(commit,file)` pairs, no extra, none missing → no missed event on the real history.
* Byte-exact recheck of each reported event agrees on status: `0718b6ab` `LOG.md` 2292/2292, `corpus/QUALITY.md` 375/375, `corpus/README.md` 663/663 → restored; `SCORECARD.md` 2421/2420 and dd9f5dc6 31/24 → partial. The tool's `2417/2416` on `SCORECARD.md` is D2's 4 dropped `--` lines.
* Runtime: tool 0.679 s, counter 1.633 s (per-commit `git` spawns scale with 295 commits × 5 files).

## 8. Residual surfaces not covered

* **Pathspec prefix leak:** `git diff … -- <f>` also matches `<f>/…`; the tool's existing `---` prefix rule happens to mask a child section's *header*, but a child file losing ≥20 lines would be attributed to `<f>` as deletions. The proposed hunk 3 removes the class (section filter); untested beyond the `dir` fixture.
* **`.gitattributes` with a textconv driver or `-diff`:** diff text and blob text would come from different transformations (both tools), so `restored_at_tip` compares apples to oranges; a `-diff` marker hides content entirely like `bin`.
* **Counter `--files` gap:** `recompute` hardcodes the five names (`:104-115`), so an audit run with `--files` has no independent calibration path.

## 9. Environment / tooling

No installs, no upgrades, no pacman, no network. `git 2.56.0`, `Python 3.14.8`. Lane, fleet repo, jj state and Git index untouched (read-only `git show`/`git diff`/`git log` only; the lane's `tools/` blobs equal `HEAD`). All fixture commits carry the throwaway identity `x2-fixture <x2-fixture@invalid>` and were verified to land in their own repo (toplevel asserted per fixture). Scratch `/fast/scratch/hyaku/kama-r46/X2Fixture` removed after the run.

## 10. Paths written

```
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/run_fixtures.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/summarize.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/results.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/matrix.tsv
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/matrix.out.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/lane.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/lane.out.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/evidence.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/lane-dash-lines.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/proposed-fixes.diff
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/results.patched-tool.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/matrix.patched-tool.tsv
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X2Fixture/matrix.patched-tool.out.txt
```
