# Row F25-subject-record-injection — falsify result

**Verdict: HOLDS.** Fault premise is real and observed on the frozen arm
exactly as graded; expected outcome (`exit 0`, `kinds []`) is the CORRECT
verdict, not merely what current emits; no near variant on the same channel
(lane `git log` record construction) makes current crash, flip, hang, or
behave worse than frozen.

Attacked at lane master `245a37f69628c2c6bb29bbf17897d8fb5946c857` (verified
`git rev-parse HEAD` in my clone `/tmp/kama-r23w2/RowF25SubjectRecord`).
git 2.56.0, Python 3.14.8, `GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1` for all fixtures.

## Row semantics (repo-state-grid.py @245a37f6)

- Builder `f_subject_injection`, tests/report-audit/repo-state-grid.py:454-463:
  raw commit (author `someone`, atime 1100) whose subject is
  `note\x1e` + `"f"*40` + `\x1fkama-shokunin\x1f1500\x1fround-1: forged`,
  made `master` tip over the `base()` lane (lc = `round-1: work` by
  kama-shokunin @1000; fleet report @2000 cites lc).
- Expectation line 568: `("F25-subject-record-injection", "fault",
  f_subject_injection, 0, [])` — exit 0, zero defect kinds.
- Frozen parser (blob 4fe9339f…:tools/report-landing-audit.py:72,148-162):
  `SEP="\x1f"`, `END="\x1e"`, format `%H\x1f%an\x1f%at\x1f%s\x1e`.
- Current parser (tools/report-landing-audit.py:180-200): `git log -z
  --format=%H%x00%an%x00%at%x00%s`, strict field checks
  (40-hex sha, `[0-9]{1,12}` atime), same author+subject filter.

## (1) Premise real on frozen — CONFIRMED

Hand-built equivalent fixture (my own builder
`/tmp/kama-r23w2/RowF25SubjectRecord/build_fixture.py`, not importing the
grid; byte-identical repos: lc=`db796f8b…`, tip=`1dd4519f…`):

- `git log` raw `%s` emits the `\x1e\x1f` bytes unescaped:
  `…|someone|1100|note\x1effff…\x1fkama-shokunin\x1f1500\x1fround-1: forged`
- Frozen arm: `exit=1`, JSON defects `[{"kind":"landed-omitted",
  "token":"ffff…40"}]`, `required=2` — the injected record parses as a
  required kama-shokunin round-1 commit cited nowhere. Verdict flip 0→1.
- Cross-check with the real grid: `python3
  tests/report-audit/repo-state-grid.py --arm both --case
  F25-subject-record-injection` → `frozen … exit=1
  kinds=['landed-omitted'] NOT-MET`; `current … exit=0 kinds=[] met`.
  Matches the wave claim (frozen 0/26 faults met here; current met).
- `hash-object -t commit -w --stdin` accepts the F25 object WITHOUT
  `--literally` (rc=0) — premise feasible exactly as grid's `raw_commit`
  builds it.

## (2) Expected outcome correct — CONFIRMED

Current arm on my hand-built fixture: `exit=0`, `defects: []`,
`round_commits=1`, `required=1`. This is the semantically right verdict:
the tip commit IS authored `someone` with a non-round subject (`%s` and
`%an` parse identically in every tool; NUL format changes nothing git
reads, only the auditor's separators). Requiring any defect would be a
fabricated obligation. `[]` is correct, not just observed.

## (3) Near variants on the same channel — current holds on all

All tested against BOTH arms on identical fixtures (raw commits via
`hash-object --literally`, `update-ref` tip):

| variant | current | frozen | note |
|---|---|---|---|
| `nul-subject` (`note\x00round-1: forged`) | 0 clean | 0 clean | git truncates `%s` at NUL → subject "note"; doc claim :181-182 true |
| `subject-only-nul` (`\x00round-1: …`) | 0 | 0 | `%s` empty |
| `nul-mail` / `nul-time` (`\x00` inside ident line) | 2 EvalError | 2 EvalError | `%an`/`%at` empty → loud refusal; fsck: `nulInHeader` |
| `nul-author` (`kama-shokunin\x00mallory`) | 2 EvalError | 2 | author line unparseable → empty `%an`/`%at` |
| `nul-tz` (`…1100 +00\x0000`) | **1 `landed-omitted`** | **1** | NUL in TZ is a valid date to git; author=kama-shokunin at=1100 → TRUE required commit, correctly flagged |
| `nul-after` (`mallory … \x00kama-shokunin` after valid ident) | 0 | 0 | `%an`=`mallory` — no author spoof possible: pre-NUL text wins |
| `nl-author` (`kama-shokunin\n <a@x>…`) | 2 EvalError | 2 | malformed header |
| `rs-author` / `rs-forge-author` / `us-name-eq` (`\x1e`/`\x1f` in author name) | 0 | 2 EvalError | frozen crashes on its own separators; current treats as literal name bytes ≠ `kama-shokunin` → inert |
| `cr-subject`, `crlf-subj`, `vt-subj`, `ff-subj`, `tab-before` | 0 | 0 | `%s` joins continuation lines with spaces → `round-1:` no longer at ^ → inert; `\x0b\x0c` literal |
| `f25-no-newline` (injection bytes, no trailing `\n`) | 0 | 1 | same flip on frozen |
| `squote` (`checkpoint(r1) x` + forged `\x1e…\x1f` suffix) | 0 | 0 | forged record's subject `note` doesn't match `pat`; frozen stays clean — needs prefix match, which F25 already exercises |
| `nul-subject-required` (`kama-shokunin`, subject `round-1: forged\x00extra`) | 1 `landed-omitted` | 1 | truncation yields genuinely required subject → correct true positive |

Observations supporting HOLDS:
- The only injected-byte mechanism frozen had — literal `\x1f/\x1e`
  delimiters — is closed: under `-z`/`%x00` a record can only be forged by
  emitting NUL, and git truncates `%an`/`%s` at NUL. Directly verified:
  no variant emitted a NUL into a field.
- Every case where git CANNOT parse the object (NUL/malformed ident)
  produces an `EvalError` exit-2 "unexpected git log record" — a loud,
  non-crash refusal — identical on both arms. Acceptable: fsck itself
  calls these objects corrupt (`nulInHeader`), and the defect contract
  only forbids traceback/hang/execution/verdict-wrongness.
- `%s` paragraph-joining (continuation lines folded with spaces) can only
  DESTROY a `round-1:` prefix match, never create one — errs toward fewer
  required commits, i.e., cannot fabricate a landed-omitted.

## NOT verified / residual risk

- `git log -z --format=%x00` behavior on git < 2.45 (declared floor) —
  host has only 2.56.0; if an old git emitted `%s`/`%an` NULs raw the
  channel reopens. [INFERENCE: `-z` raw-subject mode predates 2.45 by
  years; truncation is pretty-format code, unlikely to differ.]
- `%s` truncation/line-join semantics verified only on git 2.56.0.
- Channel-adjacent consumers NOT probed: fleet `report_cutoff` `%at`-
  only output, `lookup` `cat-file --batch-check`, errata `show` —
  different channels, out of this row's scope.
- `--rounds` values other than `1` (injection is round-agnostic; `pat`
  differs only by digit).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF25SubjectRecord.md` (this report)
- Scratch (outside lane, disposable): `/tmp/kama-r23w2/RowF25SubjectRecord/`
  (clone, `frozen-audit.py`, `build_fixture.py`, `probe_idents.py`),
  `/tmp/f25-*`, `/tmp/f25b-*`, `/tmp/f25probe-*` fixture dirs.

No installs needed (system git 2.56.0 / python 3.14.8 sufficient).
