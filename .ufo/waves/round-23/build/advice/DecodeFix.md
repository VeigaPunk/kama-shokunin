VERDICT: decode part implemented in a scratch clone and delivered as a patch. NOT verified here: selftest, probes, lint and format were not run (executor card; the parent owns the gate). Static reading only.

Axes: calibration (7, assigned lowest) and operability (8). Scope is the decode path only. Probe F3-F6 (replace refs, fabricated replace ref, promisor lazy fetch, log.follow) are not addressed by this patch.

## Rationale

1. One choke point. `git()` decodes stdout strictly as UTF-8 and maps failure to `EvalError` (exit 2). Base used `subprocess.run(text=True)`. CPython 3.14.8 applies `_translate_newlines` (decode, then CRLF/CR to LF; `/usr/lib/python3.14/subprocess.py:1098-1100`) on the text-mode result path (`:2193-2200`). That decode sits outside base's `except OSError` (base `:92`). `main()` catches only `EvalError` and `OSError` (base `:835-843`), so the escape was a traceback, exit 1. This matches L1 probe (a) and (b).
2. Valid UTF-8 unchanged. Base text mode also applied CR/CRLF to LF after decoding. The patch repeats that normalization after strict decode, so for valid UTF-8 the strings the audit compares are the same as before. Base's decode codec was the locale codec; the patch fixes it to UTF-8, which is the intended change.
3. Log encoding pinned. `git log` re-encodes subjects and author names to `i18n.logOutputEncoding`. Probe (a) shows a repo-local latin-1 value crashes `round_commits`. [INFERENCE] the mechanism is latin-1 bytes reaching the UTF-8 decode; not re-observed here. `LOG_UTF8` is passed to both `log` calls.
4. Dead code removed. Base `load_source_urls` wrapped two `git()` calls in `except UnicodeDecodeError` (base `:212`, `:224`). They can no longer fire.
5. Diagnostic corrected. Base `audit_round` (base `:265-269`) labelled every failure of `git show HEAD:rel` as "not committed in fleet HEAD", which would misreport a committed non-UTF-8 report. The message is now `cannot read <rel> at fleet HEAD: <git reason>`. Exit code unchanged.

## Changes

Scratch clone `/tmp/kama-r23/DecodeFix` (base `4fe9339f`, git 2.56.0). Line numbers are in the patched file.

- `tools/report-landing-audit.py:74-75` new `LOG_UTF8 = ("-c", "i18n.logOutputEncoding=UTF-8")`.
- `:90-108` `git()`: no `text=True`; `input` encoded UTF-8; stderr decoded with `errors='replace'` for messages only; stdout decoded strictly, then CRLF/CR to LF; `UnicodeDecodeError` becomes `EvalError("... output is not UTF-8: ...")`.
- `:159-160` `round_commits` and `:177-178` `report_cutoff`: `*LOG_UTF8` before `log`.
- `:221` and `:229` `load_source_urls`: dead `try/except` removed.
- `:273-274` `audit_round`: wording as in Rationale 5.
- `:43` docstring Exit line: non-UTF-8 report or git output listed under exit 2.
- `:804-850` selftest, inside the existing temporary-directory block before `finally:`. Four checks:
  - `latin-1-log-encoding-evaluates`: lane config `i18n.logOutputEncoding=ISO-8859-1`; round-1 commit subject `round-1: café`; valid UTF-8 report citing the full hash. Expects rc 0, status clean, required 1.
  - `invalid-utf8-fleet-report-is-error`: report with byte `\xff` committed at fleet HEAD. Expects `EvalError`; `main()` maps it to exit 2 (base `:835-837`).
  - `utf8-errata-blob-evaluates` (control): committed `registry/report-landing-errata.tsv` containing `# no rows`. Expects rc 0.
  - `invalid-utf8-errata-blob-is-error`: same fixture, errata blob with `\xff`. Expects `EvalError`, exit 2.

Patch: `out/DecodeFix/decode.patch` (`git diff -- tools/report-landing-audit.py`; 166 lines; 73 insertions, 21 deletions; applies to base `4fe9339f`).

## Checks run

None. Per the executor card, no selftest, probe, lint or format was run. I read the full patch once for syntax and indentation.

## What the parent should run (expected, not observed)

1. `python3 tools/report-landing-audit.py --selftest`: the four new cases print `ok`, `failed=0`, exit 0.
2. `AUDIT=<integrated>/tools/report-landing-audit.py bash /tmp/kama-r23-probe/probe.sh`. Control stays exit 0. F1 expected exit 0 (base: traceback, exit 1). F2 expected exit 2 (base: traceback, exit 1). F3-F6 unchanged, since this patch does not touch them.
3. Lane gate `python3 tools/report-landing-audit.py --rounds 10-` with errata: status should match base (L1 reports rounds 10-22 clean).

## Not verified

- No fixture was executed. The latin-1 and invalid-byte behaviour rests on L1 base probe output and git's documented re-encoding.
- The Python file was not compiled.
- Behaviour on histories with mixed encodings beyond the single fixture is unverified.

## Lane checkout (not in this patch; not modified)

`git -C kama-shokunin status --short` shows ` M tools/report-landing-audit.py`. `git diff --stat` reports 26 insertions and 9 deletions. I read that diff, read-only. It already contains a decode mapping and the same `audit_round` wording. It also has a `GIT_ISOLATION` tuple (`--no-replace-objects`, `--no-lazy-fetch`, `-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`) applied to every git call.

Differences from this patch:
- it keeps the two dead `UnicodeDecodeError` wrappers in `load_source_urls`;
- it has no selftest cases;
- it pins the log encoding globally rather than per `log` call. This is equivalent for current call sites.

The L1 must reconcile these. This seat did not write to that working copy.

## Residual, out of scope (flagged)

- `main()` prints `render(doc)` to stdout. Under a non-UTF-8 stdout encoding, non-encodable errata text raises `UnicodeEncodeError`, which `main()` does not catch. Not a git-decode path; not changed.
- Documentation still says UTF-8 hardening is unclaimed: `SKILL.md` around lines 736-738 and 770-771, and `corpus/QUALITY.md` KQ32 at line 165. The L1 should update these at integration. Not edited (not assigned).
- Stderr diagnostics no longer get CR normalization. This affects message text only.

## Tooling

No installs or updates. Observed: git 2.56.0; Python 3.14.8 (`/usr/lib/python3.14/subprocess.py`).

## Files written

- `/tmp/kama-r23/DecodeFix/tools/report-landing-audit.py` (scratch clone edit)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/DecodeFix/decode.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/DecodeFix.md` (this report)

Coordination: one short note sent to `CloseKama22.ConnPlanningWalk` describing the `git()` shape.

## Addendum: live worktree divergence (appended after the report above)

Read-only check of `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py` (sha256 d0a96599..., 919+ lines, uncommitted). It is not my base and I did not change it.

- Live `git()` (`:107-126`) already has strict UTF-8 as default and an `errors=` parameter. `round_commits` (`:179-181`) and the `parse_rounds` ls-tree listing (`:417-418`) pass `errors="surrogateescape"`. Its docstring says these callers only match ASCII fields and never emit the text.
- Live `GIT_ISOLATION` (`:91-95`) pins `-c i18n.logOutputEncoding=UTF-8` for every git call. My `LOG_UTF8` hunks are therefore redundant on live and should be dropped at integration.
- Live still has the two `except UnicodeDecodeError` wrappers in `load_source_urls` (about `:245` and `:256`). They are dead once `git()` raises EvalError, so remove them at integration.
- Either/or for L1 on the fixture (cited round-1 commit whose subject is raw latin-1 bytes, no encoding header; `-c` does not re-encode bytes git assumes are UTF-8):
  - S, strict everywhere (decode.patch as delivered): expected exit 2 with EvalError "output is not UTF-8". Not executed. The same refusal applies to any non-UTF-8 byte anywhere in branch history, because `round_commits` reads the whole log.
  - L, surrogateescape at `round_commits` and the listing (live): reported exit 0 with required 2 by the connector's measurement.
- Recommendation: L at those two sites and S everywhere else. Its verdict-safety argument: the only fields the verdict uses from `round_commits` are the sha, author equality with the ASCII lane name, the digit-only time, and the ASCII round-prefix match. `parse_rounds` uses only the regex fullmatch on ASCII round paths. Any non-ASCII bytes in those fields cannot change the verdict.
- Not rebased: a rebase onto an uncommitted, moving worktree would be stale on arrival. L1 integrates against a committed base.
- The sha256 and the 919+ line count above are ConnPlanningWalk's measurement at the time of its message. I did not re-measure them; the line numbers cited are from my read-only grep of the live file.
