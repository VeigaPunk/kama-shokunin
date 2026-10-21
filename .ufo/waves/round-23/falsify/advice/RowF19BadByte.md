# F19-bad-byte-round-subject — falsify review (CloseKama22.RowF19BadByte-2)

Verdict: **HOLDS.** (1) The fault premise is real and observed in the frozen arm; my
hand-built rebuild reproduces it exactly. (2) The expected outcome (exit 1,
`["landed-omitted"]`) is the correct one, not merely what current does. (3) No near
variant of the bad-byte channel was found that the committed auditor gets wrong.

## The row at 245a37f6

- `tests/report-audit/repo-state-grid.py:561-562` — `("F19-bad-byte-round-subject",
  "fault", f_bad_round_subject, 1, ["landed-omitted"])`.
- Builder `tests/report-audit/repo-state-grid.py:414-428`: base lane (one cited
  `round-1: work` commit at t=1000, `tests/report-audit/repo-state-grid.py:112-117`),
  then a raw `hash-object -t commit -w` child of the cited tip with message
  `b"round-1: caf\xe9\n"` at t=1100, `refs/heads/master` repointed to it
  (`tests/report-audit/repo-state-grid.py:84-93`). Fleet report (t=2000) cites only
  the good parent. `run_case` (`:600-635`) adds `met = no traceback ∧ no exec ∧ no
  timeout ∧ exit==1 ∧ kinds==["landed-omitted"]`.

## Method

Rebuilt the fixture BY HAND in /tmp with raw plumbing only (init / hash-object -t
commit -w / update-ref; `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`),
no grid import — `/tmp/kama-r23w2/RowF19BadByte/drive.py`. Ran both arms from
committed bytes: frozen = `git cat-file blob 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(sha256 09ecd63bdc3a5be5…), current = `git show HEAD:tools/report-landing-audit.py`
at 245a37f6 (sha256 f228f17420134a4a…; the lane working tree is dirty, so the
working-tree copy was never used). git 2.56.0, Python 3.14.8.

## (1) Premise real and observed in frozen — YES

Hand-built F19 (raw commit subject bytes `round-1: caf\xe9\n`, verified with
`git cat-file commit | xxd`):

- frozen arm: exit 1, `Traceback (most recent call last)` in stderr,
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 72`
  raised in subprocess text-mode `_translate_newlines` — i.e. inside
  `subprocess.run`, which frozen `git()` calls with `text=True`
  (frozen blob lines 89-96) from `round_commits` (frozen lines 148-159,
  `\x1f`/`\x1e` SEP/END framing, strict decode). Frozen `main` catches only
  EvalError/OSError (frozen lines 835-843), no broad handler → traceback escapes.
  Same trigger isolates to the byte: the body-bad-byte variant (byte in commit
  body only) does NOT crash frozen (byte never reaches log stdout), while both
  F19 and the F18 mirror (byte in any log-emitted field) crash it.
- Committed grid cross-check (clean clone of 245a37f6, both arms):
  `python3 tests/report-audit/repo-state-grid.py --case F19-bad-byte-round-subject
  --case F18-bad-byte-unrelated-subject` →
  `frozen F19 … exit=1 kinds=unparseable tb=1 … NOT-MET` /
  `current F19 … exit=1 kinds=['landed-omitted'] tb=0 … met`;
  `frozen faults=0/2 tracebacks=2` / `current faults=2/2 violations=0`,
  grid exit 1 (expected while frozen arm runs). Matches the L1 declaration for
  this row.

## (2) Expected outcome correct — YES (exit 1, landed-omitted)

Current `round_commits` (`tools/report-landing-audit.py:180-200`) reads
`git log -z --format=%H%x00%an%x00%at%x00%s` with `errors="surrogateescape"`; NUL
framing means commit text cannot inject or shift fields, so the bad byte stays
inside the subject field and cannot corrupt sha/atime parsing. The record for my
rebuild: `ddf5d0de…448\0kama-shokunin\01100\0round-1: caf<0xe9>` — author intact,
`round-1:` prefix intact, atime 1100 ≤ cutoff 2000, uncited →
`landed-omitted` (`tools/report-landing-audit.py:317-337`), exit 1
(`:515-517`). Observed: `required=2 round_commits=2`, defects
`[landed-omitted ddf5d0de28abf0a67b23258c4805d97ae0068443]`, exit 1, no traceback.

Why omission — and not a crash (frozen) or a clean verdict (flip) — is right:
the lane's own claim text (`round-1:` prefix) and identity (`%an`) are intact, so
the commit is a lane round commit; an undecodable tail cannot erase the claim.
Exit 2 refusal would only be defensible if the bytes could change semantics —
they cannot (see channel-boundary probes below). `cited_elsewhere` is correctly
False. When the same sha is cited, current correctly suppresses the omission
(exit 0) — probed via an appended citation of the bad commit.

## (3) Near variants of the same channel — none break current

All fixtures in /tmp/kama-r23w2/RowF19BadByte/fixtures/, driver `drive.py`
(`python3 drive.py` runs every case against both arms):

| variant (byte placement) | current | frozen | assessment |
|---|---|---|---|
| subject, round prefix intact (F19) | exit 1, landed-omitted | traceback | correct |
| subject, non-round (F18 mirror) | exit 0 | traceback | correct |
| subject after `checkpoint(r1)` | exit 1, landed-omitted | traceback | correct |
| truncated UTF-8 seq `caf\xf0\x9f` | exit 1, landed-omitted | traceback | correct |
| author name `kama-shokunin\xe9` | exit 0, clean | traceback | see note |
| committer name bad byte | exit 1, landed-omitted | exit 1, landed-omitted | correct (attribution is by author) |
| commit body bad byte, clean subject | exit 1, landed-omitted | exit 1, landed-omitted | correct (body not in `%s`) |
| `encoding ISO-8859-1` header | exit 1, landed-omitted | exit 1, landed-omitted | correct (git transcodes; byte survives as valid UTF-8) |
| raw NUL in subject | channel impossible | — | `git hash-object` refuses: `nulInCommit … fatal: refusing to create malformed object` |
| non-digit author time (`1f00`) | channel impossible | — | `git hash-object` refuses: `badDate: invalid author/committer line - bad date` |
| ASCII ctrl bytes `\x01\x1f` in subject | exit 1, landed-omitted | exit 1, landed-omitted | correct (decodes fine; no injection under NUL framing) |
| bad-byte commit cited in report | exit 0 | traceback | correct (cited ⇒ not omitted) |

Current: 0 tracebacks, 0 executions, 0 timeouts across all 13 probes; verdicts
never flip from the semantic ground truth. The two git-level fsck refusals pin
the channel boundary: an F19 byte must be non-NUL, and `%at` stays digits, so no
field-count or date-parsing break is reachable through this channel. The
injection sibling (`\x1e`/`\x1f` in subjects) is grid row F25, out of scope here.

**Design note (not a defect):** with the bad byte in the *author name*
(`kama-shokunin\xe9`), current emits a clean exit 0 — the commit is not counted
because `%an` ≠ `kama-shokunin`. This is self-consistent with the tool's
identity model (`tools/report-landing-audit.py:198`: only `{lane}-shokunin`
round-prefixed commits form the required set; the same outcome occurs for any
legitimate other author). An auditor *could* argue unverifiable authorship
deserves a defect, but current applies one uniform rule and never flips a
verdict, so I record it as an observation only.

## Not verified

- Other grid rows (F01-F17, F20-F26, controls, O01/O02, T01) — own attackers cover them.
- Frozen-arm behavior under git < 2.45 (host git 2.56.0) and whether `hash-object`
  fsck strictness (nulInCommit/badDate refusals) is identical on older git.
- The lane checkout's dirty working tree (`tools/report-landing-audit.py` modified
  mid-session by a sibling) — all arms here run committed bytes only.

## Files written

- `.ufo/waves/round-23/falsify/advice/RowF19BadByte.md` (this report)
- /tmp/kama-r23w2/RowF19BadByte/{drive.py,current-audit.py,fixtures/*} (scratch)
- /tmp/kama-r23w2/frozen-audit.py, /tmp/kama-r23w2/grid-clone (scratch)

No tools installed (python3/git predate the task); nothing to record under the
tooling directive.
