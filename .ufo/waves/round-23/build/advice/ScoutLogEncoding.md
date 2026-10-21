# ScoutLogEncoding — repo-local `i18n.logOutputEncoding` / commit `encoding` headers

Question: does repository-local commit/log encoding state make
`tools/report-landing-audit.py` (base `4fe9339f`, blob
`fcc255ce5115a749dfbd09cf992ba9851a2dc90a`, 847 lines, sha256
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`) crash,
flip a verdict, execute, or do nothing? And exactly which `--format`
placeholders are re-encoded; does `-c i18n.logOutputEncoding=UTF-8` repair
Latin-1-`encoding`-header commits; what happens for headerless invalid bytes?

**Verdict: `crashes` (error becomes the `failed` verdict at exit 1).**
A repo-local `i18n.logOutputEncoding` (or `i18n.commitEncoding`, which is the
documented default fallback) set to a single-byte encoding makes `git log`
emit non-UTF-8 bytes; `git()` decodes with `text=True` (strict) and the
`UnicodeDecodeError` is uncaught, so the process exits **1**, which the
docstring reserves for `failed`. This is not command execution and not a clean
false clean/failed defect set; correctly labeled commits are already UTF-8
under default config, and re-encoding never changes the ASCII name/prefix the
logic compares.

## Mechanism (base code)

- `tools/report-landing-audit.py:90` — `subprocess.run(..., capture_output=True, text=True, ...)`.
  Text mode decodes stdout with the locale encoding (UTF-8 here) and
  `errors='strict'`; only `OSError` is caught (`:92`).
- `tools/report-landing-audit.py:148` — `git log --format=%H<SEP>%an<SEP>%at<SEP>%s<END> master`.
  `%an` and `%s` come from the per-commit buffer and are subject to
  `i18n.logOutputEncoding` re-encoding; `%H`/`%at` are generated.
- `tools/report-landing-audit.py:160` — author equality `f"{lane}-shokunin"`
  and subject regex `^(?:round-N:|checkpoint\(rN\))` are ASCII, so conversion
  corrupts text but cannot flip these predicates for the round-selection path.
- `tools/report-landing-audit.py:835-843` — only `EvalError` and `OSError` map
  to 2 (`could-not-evaluate`). A `UnicodeDecodeError` escaping `round_commits`
  reaches the top level as a traceback and exits 1.
- Raw blob paths are *not* affected by log encoding: `:266`
  `git show HEAD:<report>`, `lookup`'s `cat-file --batch-check`, `ls-tree`,
  `cat-file blob` emit stored bytes with no transcoding (verified byte-identical
  under default/UTF-8/ISO configs).
- Guards already exist for two decode sites (`:176`, `:212`, `:223`), but not
  for `round_commits` (`:148`), `show HEAD:<report>` (`:266`), or
  `git show <branch>:registry/report-landing-errata.tsv` in `load_errata`.

## Git rule (documented)

- `https://git-scm.com/docs/git-log#Documentation/git-log.txt---encodingltencodinggt`
  — accessed 2026-10-21, located quote: “if an object claims to be encoded in
  X and we are outputting in X, we will output the object verbatim”.
  Same page: “Likewise, if iconv(3) fails to convert the commit, we will
  quietly output the original object verbatim.” Output defaults to UTF-8 for
  non-plumbing commands.
- `https://git-scm.com/docs/git-config#Documentation/git-config.txt-i18nlogOutputEncoding`
  — accessed 2026-10-21, located quote: “Character encoding the commit messages
  are converted to when running git log and friends.” `i18n.logOutputEncoding`
  falls back to `i18n.commitEncoding`, then UTF-8; lacking an `encoding` header
  implies UTF-8 (`git-log` Discussion, same access date).

## Byte-level observations (`git 2.56.0`, fresh repos under `/tmp`, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`)

Subjects dumped with `od`; configs: default / `-c logOutputEncoding=UTF-8` /
`-c logOutputEncoding=ISO-8859-1`.

| fixture | default | `-c UTF-8` | `-c ISO-8859-1` |
|---|---|---|---|
| `encoding ISO-8859-1` + Latin-1 `na\xefve` | `6e 61 c3 af` valid | `6e 61 c3 af` valid | `6e 61 ef` **invalid** |
| no header + raw `na\xefve` | `6e 61 ef` **invalid** | `6e 61 ef` **invalid** | `6e 61 ef` **invalid** |
| `encoding UTF-8` + raw `na\xefve` | `6e 61 ef` **invalid** | `6e 61 ef` **invalid** | (same, verbatim) |
| `encoding X-BOGUS` + raw `na\xefve` | `6e 61 ef` **invalid** | **invalid** | **invalid** |
| no header, valid UTF-8 `→` | `e2 86 92` valid | valid | valid (iconv fails → verbatim) |
| `encoding ISO-8859-1`, body actually UTF-8 | `c3 83 c2 af` valid (double-encoded) | same | `c3 af` |
| `%an` = Latin-1 `na\xefve` with `encoding ISO-8859-1` | `6e 61 c3 af` | `6e 61 c3 af` | `6e 61 ef` **invalid** |

Also: repo-local config and `-c` precedence — with repo config
`i18n.logOutputEncoding=ISO-8859-1`, plain `git -C lane log` yields `...61 ef...`;
`git -C lane -c i18n.logOutputEncoding=UTF-8 log` yields `...61 c3 af...`
(command-line `-c` wins). `i18n.commitEncoding=ISO-8859-1` alone produces the
same invalid bytes because it is the output default. `logOutputEncoding=UTF-16`
emits `ff fe ... 00` per record, even for `--format=%at` (so it would also
crash `report_cutoff` at `:166` in either repo).

## Audit-level results at base (fleet/lane fixtures under `/tmp`)

| scenario | command outcome |
|---|---|
| clean fixture, no encoding config | rc=0 `status=clean` |
| lane repo config `i18n.logOutputEncoding=ISO-8859-1` (Latin-1-header commit present) | **rc=1**, stdout empty, traceback `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xef ...` |
| lane repo config `i18n.commitEncoding=ISO-8859-1` | **rc=1**, same traceback |
| lane repo config `i18n.logOutputEncoding=UTF-8` | rc=0 `status=clean` |
| no header + raw `\xef`, no config | **rc=1**, same traceback |
| no header + raw `\xef`, repo config `UTF-8` | **rc=1**, same traceback |
| candidate-sim (base + `--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false` + strict-decode→`EvalError`) with repo config ISO | rc=0 `status=clean` |
| candidate-sim, headerless raw `\xef` | **rc=2**, `could-not-evaluate: git log ... output is not UTF-8: ...byte 0xef...` |

Control: base `--selftest` → `selftest cases=50 failed=0` (fresh temp repos, so
repo-local encoding config never applies there).

Latent trigger on the real lane history (read-only scan of a `--no-hardlinks`
clone at base; no config written): `master` has 97 log records; under
`-c i18n.logOutputEncoding=ISO-8859-1` the entire `%H%x1f%an%x1f%at%x1f%s%x1e`
output fails strict UTF-8 decode at byte 935, with offending records such as
`3d79fc5780fb8b57ae06e9f94e9006a0828fa812 | Jo\xe3o Pedro Veiga | considerthese: 2026-10-21 daily reflection`
(6 of 97 records become invalid; author `João` is fully Latin-1 representable).
Default and `-c UTF-8` are valid UTF-8. So a single repo-local
`git config i18n.logOutputEncoding ISO-8859-1` in the lane checkout suffices to
reproduce the crash on real history, and the offending commit need not be a
round commit (records are decoded as one stream).

## Direct answers

1. **Which placeholders are re-encoded?** `%an` and `%s` (commit-buffer text:
   identity lines and log message) are re-encoded per commit; `%H` and `%at`
   are generated and remain ASCII for single-byte targets, though a multibyte
   target encoding (UTF-16) prefixes BOM/NUL bytes to every record including
   `%at`-only output.
2. **Does `-c i18n.logOutputEncoding=UTF-8` make Latin-1-header commits valid
   UTF-8?** Yes: `encoding ISO-8859-1` + Latin-1 body yields `c3 af` under
   `-c UTF-8`, and the command-line value overrides a repo-local ISO setting.
   Note the default (no config) already converts such commits to UTF-8; the
   fault requires the repo to set a non-UTF-8 target (or `commitEncoding`).
   It does not repair mislabeled headers (double-encoded but valid UTF-8;
   ASCII prefix/name preserved, so verdict unchanged).
3. **Raw invalid bytes with no `encoding` header?** Git assumes UTF-8, sees
   input and output encodings equal, and emits the object verbatim, so output
   stays invalid under default, `-c UTF-8`, and any single-byte target; base
   crashes with exit 1. Only a strict-decode guard converts this to a typed
   refusal (candidate-sim: exit 2). The same applies to `encoding UTF-8` with
   invalid bytes and unknown headers whose iconv conversion fails.

## Scope / boundaries

- This channel is `crashes`, not `executes`; no repo-configured command is run.
- No clean verdict flip was found: re-encoding preserves ASCII author names,
  round-subject prefixes, and hex timestamps, so `round_commits`,
  `report_cutoff`, and the ASCII lookups are content-stable. The observable is
  exit 1 (`failed`) from an uncaught traceback.
- `-c i18n.logOutputEncoding=UTF-8` fixes config-driven transcoding (the probe
  (a) fault and UTF-16-style targets) but not headerless/raw-invalid bytes and
  not blob reads; the load-bearing candidate change for those is
  bytes-mode output with strict UTF-8 decode → `EvalError` (exit 2).
- Observed repo state: the lane working tree currently has an **uncommitted**
  `tools/report-landing-audit.py` (864 lines) carrying a `GIT_ISOLATION` tuple
  with `-c i18n.logOutputEncoding=UTF-8` and strict decoding. I did not edit
  it; my measurements are against the committed base blob above.

## Not verified

- The actual in-flight candidate (uncommitted, not a commit); `audit-cand-sim.py`
  is base + the minimal isolation/strict-decode change, a simulation.
- The base audit was not run against the real lane/fleet repos or their reports
  (contract); real-lane evidence is read-only history bytes in a scratch clone.
- Only git 2.56.0 and Python 3.14 (UTF-8 locale) were exercised; no other git
  builds, platforms, or encodings beyond UTF-8/Latin-1/UTF-16 were tested.
- `%ae`/`%b` were not dumped individually, but conversion is commit-buffer
  scoped (observed on `%an` and `%s`).

## Files written (all under this lane)

- `.ufo/waves/round-23/build/advice/ScoutLogEncoding.md` (this report)
- `.ufo/waves/round-23/build/out/ScoutLogEncoding/`: `repro_bytes.py`,
  `repro_audit.py`, `repro_extra.py`, `audit-cand-sim.py`, `audit-base.py`
  (extracted base blob), `selftest-base.txt`, `s1-base.err/out`,
  `s1-cand.err/out`, `s2-base.err/out`, `s2-cand.err/out`.

Tooling: no installs or upgrades; all fixtures ran in fresh repos under
`/tmp/kama-r23/ScoutLogEncoding` with `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_NOSYSTEM=1`; no network hosts were contacted.
