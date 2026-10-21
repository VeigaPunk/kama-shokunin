# F01-log-output-encoding — falsify report

Row: `("F01-log-output-encoding", "fault", f_log_encoding, 0, [])`
at `tests/report-audit/repo-state-grid.py:539`, builder `:216-223`,
commit `245a37f69628c2c6bb29bbf17897d8fb5946c857`.

## Verdict: HOLDS

(1) The fault premise is real and reproduced against the frozen blob.
(2) The expected outcome (exit 0, no defects) is the *correct* one, not
merely what `current` happens to emit.
(3) I found no near variant of the same channel that `current` still
gets wrong; every variant probed either degrades to an honest exit-2
refusal or keeps the correct verdict. Residual risk named at the end.

## (1) Premise reproduced — frozen arm faults exactly as claimed

Hand-built fixture (NOT importing the grid), `/tmp/kama-r23w2/fix-f01b`:

- `lane/`: `git init -b master`; commit `db796f8b820b…` author
  `kama-shokunin` `@1000 +0000`, subject `round-1: work`; second commit
  `de2594a230fa…` author `someone` subject `note café` (UTF-8 `c3a9`);
  `git config i18n.logOutputEncoding ISO-8859-1`.
- `fleet/`: report `.ufo/reports/round-1/kama.md` =
  `# kama round 1\n\n## Landed changes\n\n- <lane sha>\n`, committed
  `@2000 +0000`.

Premise check: `git -C lane log -1 --format=%s | xxd` emits
`6e6f7465 20636166 e90a` — the raw Latin-1 `e9`, i.e. git really does
re-encode the UTF-8-stored subject to Latin-1 output. Matches the
grid's own `require(b"\xe9" in out, …)` at `repo-state-grid.py:222`.

Frozen arm (blob `4fe9339f:tools/report-landing-audit.py`,
sha256 `09ecd63b…`, extracted via `git cat-file blob`):

    timeout 30 python3 frozen-audit.py --lane-repo lane --fleet-repo fleet \
        --rounds 1 --no-errata --json
    exit=1, stderr= Traceback (most recent call last): …
      File "…subprocess.py", line 1099, in _translate_newlines
        data = data.decode(encoding, errors)
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 62

Root cause in the frozen blob: `git()` runs
`subprocess.run([...], capture_output=True, text=True)` at frozen-audit
lines 87-97 — strict-UTF-8 text mode, no `errors=` — so the Latin-1
`e9` byte kills `communicate()` inside `round_commits` (frozen-audit
line 148) before any verdict logic runs. This is precisely the "exit-1
traceback" class the fault grid penalizes (grid `run_case`:
`traceback` flag → `met=False`, `repo-state-grid.py:624-629`).
**Premise real and observed.**

## (2) Expectation correctness — exit 0 / no defects IS the right verdict

Fixture truth: the cited full-hash commit exists in the lane
(`git cat-file -e db796f8b…` succeeds), is authored `kama-shokunin`,
subject `round-1: work`, timestamp 1000 < report time 2000 → it is a
legitimately "required + landed" commit. There are no omissions, no
fabrications. The encoding fault is orthogonal to the audit question;
the only honest verdict is clean → exit 0, zero defects.

Current arm (`tools/report-landing-audit.py` at 245a37f6,
sha256 `f228f174…`):

    python3 tools/report-landing-audit.py --lane-repo lane --fleet-repo fleet \
        --rounds 1 --no-errata --json
    exit=0, JSON: results[0].round_commits=1, required=1, defects=0,
    summary.status="clean"

Mechanism, verified at the byte level:

    git -C lane log -1 --format=%s          → 6361 66e9    (raw e9)
    git -c i18n.logOutputEncoding=UTF-8 …   → 6361 66c3 a9 (UTF-8 é)

The `-c` in `GIT_ISOLATION` (committed file line 93-96:
`"-c", "i18n.logOutputEncoding=UTF-8"`) overrides the repo-local
config value — command-line config has the highest precedence, repo
`i18n.logOutputEncoding` is never consulted. Decoding is then
byte-level: `proc.stdout.decode("utf-8", errors)` (line 123) with
`surrogateescape` on the lane-log call (line 184), so even output git
cannot re-encode becomes lone-surrogates rather than an exception.
**Expectation is the correct verdict AND current meets it for the
right reason (output forced to UTF-8 before decode), not by luck.**

## (3) Near variants of the same channel — all still handled correctly

| Variant | Setup | Result |
|---|---|---|
| Bogus encoding name | `git config i18n.logOutputEncoding x-bogus-enc` | exit 0 clean — `-c` still wins, value never used |
| Malformed `.git/config` | truncated `[i18n` section | exit 2 `could-not-evaluate: git rev-parse … rc=128 fatal: bad config line 1` — honest EvalError refusal, not a traceback/verdict |
| `i18n.commitEncoding=UTF-16` | repo config | Auditor's forced `-c i18n.logOutputEncoding=UTF-8` still emits UTF-8; `%an`/`%at`/`%s` intact, verdict unaffected |
| `i18n.commitEncoding=ISO-8859-1` | repo config | No effect on input decode; stored UTF-8 bytes still read as UTF-8 |
| Commit `encoding ISO-8859-1` header + Latin-1 subject | raw commit via `hash-object` | git correctly recodes `caf\xe9`→`caf\xc3\xa9`; subject parsed fine |
| Commit `encoding UTF-16` header + ASCII body (wrong label) | raw commit | git detects body is valid ASCII/UTF-8, passes through; `round-1: work` still matches |
| Commit `encoding x-not-an-enc` | raw commit | raw passthrough, no crash |
| UTF-16LE-stored author + `encoding UTF-16` | raw commit | `%an` emitted **raw** (author identity is byte-exact, never recoded) — can't be spoofed/mangled by encoding games |
| `core.fsmonitor=/tmp/evil.sh` | repo config | Not executed by `git log`/`cat-file`; dead for this channel |

Key invariant observed empirically: git treats `i18n.commitEncoding`
and the commit `encoding` header as *declared interpretation of stored
bytes*, but when stored bytes are already valid UTF-8/ASCII git passes
them through; and `i18n.logOutputEncoding` — the only knob that
controls the *output* byte stream the auditor decodes — is
authoritatively pinned to UTF-8 by `-c`. There is no repo-local way to
make `git log` emit non-UTF-8 bytes under the current command line.

### Residual (not exploitable via F01's channel, honest boundaries)

- A commit whose stored subject bytes decode (under its *declared*
  encoding header) to non-`round-1:` text will not be counted. This is
  not a defect: git's own canonical interpretation of the commit's
  subject is that text, so "not a round-N commit" is the faithful
  answer — the same answer a human running `git log` would get.
- `encoding` headers that produce invalid UTF-8 output →
  `surrogateescape` → subject pattern can't match `round-1:` on
  lone-surrogate text (correct — it isn't that text), and `%an` is
  compared byte-exact so equality still holds for ASCII names.

## What I did NOT verify

- I did not run the full 34-case grid end-to-end (only the F01 row
  logic, exercised directly via my own fixture on both arms).
- `git log` stderr warnings under exotic encodings (auditor ignores
  stderr on rc=0; warnings would not change stdout fields).
- Other rows' channels (replace/promisor/mailmap/etc.) — out of scope.
- Python-version sensitivity: reproduced on `/usr/bin/python3`
  (3.14). The `UnicodeDecodeError` path in `text=True` mode is
  version-stable.

## Evidence files

- Fixture: `/tmp/kama-r23w2/fix-f01b/{lane,fleet}` (+ `fix-ce`,
  `fix-f01` earlier variant).
- Frozen blob: `/tmp/kama-r23w2/frozen-audit.py`
  (sha256 `09ecd63bdc3a…`, = `4fe9339f:tools/report-landing-audit.py`).
- Captured outputs: `/tmp/kama-r23w2/fix-f01b/{frozen,cur}.{out,err}`,
  `/tmp/kama-r23w2/v{1,2,3}.{out,err}`.
- Clone: `/tmp/kama-r23w2/RowF01LogOutput` @ `245a37f6` (verified
  `rev-parse HEAD`).
- No writes to lane checkout, no commits/pushes, no installs
  (pacman untouched; used system git 2.56.0 + python3.14 only).
