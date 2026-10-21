# kama — round 23 lesson

Author: L1 (CloseKama22 identity, dispatched as kama round-23 coordinator).
Round base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.

## Declared claim

C1, **calibration** (lowest assigned non-retired axis, 7; operability 8):
`tools/report-landing-audit.py` promised "Errors are never verdicts" and its
`git_env` docstring said the audited repositories "cannot be redirected"
(base `:79-81`, introduced in `1471344`). Repository-local git state in the
audited lane/fleet repositories still crashed it into exit 1 (the `failed`
code), flipped verdicts, or ran repo-configured programs. The claim is a
finite fault grid, `tests/report-audit/repo-state-grid.py`, with a frozen
arm (the `4fe9339f` blob) and a current arm, plus
`tests/report-audit/isolation-mutants.py`. It is narrow D4 movement, not
untrusted-repository safety: KQ32 stays in force.

## Gate

All rows opened 2026-10-21 by the L1 (pages fetched and quotes located by
exact string match); build-wave scribes SrcGitEnv, SrcGitReplace,
SrcGitConfig, SrcPartialClone, SrcGitLogFollow, SrcGitRepoLayout and
SrcPythonDecode opened the same pages independently (advice files under
`.ufo/waves/round-23/build/advice/`).

- S089 https://git-scm.com/docs/git (2.56.0) — OPTIONS: "Do not use
  replacement refs to replace Git objects." and "Do not fetch missing objects
  from the promisor remote on demand." Supports F03–F05 and F06.
- S090 https://git-scm.com/docs/git-replace (2.55.0, 2.56.0 no changes) —
  "Replacement references will be used by default by all Git commands except
  those doing reachability traversal". Supports F03–F05.
- S091 https://git-scm.com/docs/git-config (2.56.0) — `log.follow`/
  `log.showSignature`: "If true, makes git-log[1], git-show[1], and
  git-whatchanged[1] assume --show-signature."; `i18n.logOutputEncoding`:
  "Character encoding the commit messages are converted to when running git
  log and friends." Supports F01, F07–F09, F14, F22.
- S092 https://git-scm.com/docs/partial-clone (2.56.0) — "no check as to
  whether the missing object is actually a promisor object is performed".
  Supports F06/F23 refusals.
- S093 https://git-scm.com/docs/git-log (2.56.0) — "if iconv(3) fails to
  convert the commit, we will quietly output the original object verbatim."
  and "If true, git log will act as if the --follow option was used when a
  single <path> is given." Supports F18/F19 and F07.
- S094 https://git-scm.com/docs/gitrepository-layout (2.49.1→2.56.0 no
  changes) — "Note that the grafts mechanism is outdated" and "Such refs can
  be exchanged between repositories while grafts are not." Supports F10/F11
  and the O01 alternates limit.
- S095 https://docs.python.org/3.14/library/stdtypes.html#bytes.decode
  (3.14.9) — "If 'strict' (the default), a UnicodeError exception is
  raised." Supports F01/F02/F16 mechanism.

Rows are new; no existing row's status, recheck or used-by changed. Rejected
candidates: SrcGitLogFollow's separate `log.follow` row (same claim as S091,
kept once); SrcPythonDecode's subprocess row (S044/S064 already register the
page; no new anchor needed). `ScoutLogFollow.md` attributes a non-linear
history caveat to `--follow` that FollowFixture did not find in the 2.56.0
text; it is not registered.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Instrument self-exemption: an isolation promise ("audited repos cannot be redirected") and an exit promise ("Errors are never verdicts") were never in the gate's own fault population | base `tools/report-landing-audit.py:42-45,79-81`; frozen grid arm 0/26 faults met, 8 tracebacks, 2 executed programs, 1 hang; `RevengeEnvDocstring.md` | none (KQ32 restricted use but did not test the claim) | grid with one fault row per named channel and pinned refusal reasons, plus one mutant per isolation element; KQ34. Shown able to fail: frozen arm violates all 26 faults; 22/24 mutants killed |
| M2 | Unchecked fixture premise: the L1 probe's f3 `commit-tree` silently failed without an identity and f6 could not flip, so a cell could "pass" with no fault present | `.ufo/waves/round-23/probe/probe.sh:42-43`; `RevProbeScript.md`, `CritSeparability.md`, `MutProbeSensitivity.md` (9/9 probe-exit mutants survived) | KQ30 (fixture must establish its fault) — applied late | every grid builder `require()`s its premise and a failed premise exits 2. Shown able to fail: during integration F23's blobless premise failed and the grid exited 2 until `uploadpack.allowFilter` was set |
| M3 | Operator-shell leak: the L1 exported `GIT_CONFIG_GLOBAL=/dev/null` and identity variables into the persistent shell while probing, which hid the credential helper and made the first helper push fail (commit kept, no landed hash) | jj-lane push rejected for `e0f04346`; `git credential fill` failed until the variables were unset | jj-lane remote verification (no `landed` line) | probes set git environment per command only; push retried after `unset`, landed `34b23761` |

## Integration and boundaries

- Decode policy: strict UTF-8 by default (undecodable output → exit 2);
  surrogateescape only for the lane log records and the fleet report listing,
  which match ASCII fields and are never emitted (CritRefusalPolicy).
- Log records are NUL-delimited (`-z`, `%x00`), closing `\x1f`/`\x1e`
  injection from names and subjects (RevRoundCommits S11, grid F25).
- Refusals (exit 2, reason pinned in the grid): non-UTF-8 output, shallow,
  info/grafts, promisor config or pack, non-sha1 object format, non-top-level
  path, ref-named citation, unparseable log record, any unanticipated
  exception (catch-all).
- Defensive-only (no grid row needs them, mutant survives): `--no-lazy-fetch`
  (the promisor refusal runs first) and the 40-hex `%H` check (signature
  display is disabled). Kept; `--no-lazy-fetch` sets a git ≥ 2.45 floor
  (OldGitFloor: 2.44.0 rejects it with exit 129 → audit exit 2).
- Declared tradeoffs: partial clones and shallow clones are refused even when
  every cited object is local (grid T01; RevCalibrationAxis, CritNoHarm).
- Open (both arms, reported not graded): objects through
  `objects/info/alternates` (O01) or a `.git` gitfile redirect (O02) resolve
  as local; peel/cross-repo ambiguity overwrite (RevLookup F1); only the first
  `## Landed changes` section is read (RevSourcesBlob F1); CR inside an errata
  line (RevErrataPath O2); `log.follow` path-vs-lineage contract kept as path
  (FollowFixture); sibling tools `citation-provenance.py` and
  `sources-append-only.py` remain unisolated (ConnFleetAuditors,
  SiblingGitSurvey).

## Falsify-wave integration and coordinator replacement (appended)

Appended by KamaR23-2, the replacement L1 after the host session froze and
was killed (SIGHUP, 2026-10-21 13:10:51 -03) while the first L1
(CloseKama22) was integrating the falsify wave. Everything above this
section was written at `245a37f6` and stays unchanged; corrections below
are append-only.

Inherited and re-verified: the uncommitted auditor, grid and mutant edits
(F27–F30, C09–C12, contract kind for F17/F21/F23/F24, M26–M31, mutant kill
only on grid exit 1, 20 s git timeout); the uncommitted SKILL, QUALITY,
README and knowledge appends (each rewritten to the measured state below);
the round recipe. Discarded: nothing. Added by the replacement: an
info/grafts check that ignores blank and `#` lines as git does (S101;
control C13, mutant M32), and a grid timeout that kills the auditor's whole
session (frozen-arm FIFO rows had left blocked git grandchildren running —
56 such processes from this round were killed).

Measured in a clean clone of `e876b953e9da28d2dffd29c923052bc626148c27` (git 2.56.0, Python 3.14.8; grid
population `f29fab8d…364a`, current auditor `da5041a8…5af1`, frozen
`09ecd63b…3b3f`):

- `python3 tests/report-audit/repo-state-grid.py --arm both --json` → exit 1
  (frozen red by design). Current: faults 26/26, contracts 4/4, controls
  13/13, tracebacks 0, executed 0, timeouts 0. Frozen: faults 0/26,
  contracts 1/4, controls 13/13, tracebacks 9, executed 3, timeouts 2.
- `python3 tests/report-audit/isolation-mutants.py --json` → exit 0; 31 mutants, 30 killed on grid exit 1, each with its failed rows listed (M16/M19/M22/M24 by contract rows F21/F17/F23/F24); survivor M20 (40-hex `%H` check)
- `python3 tools/report-landing-audit.py --selftest` → 50/50, exit 0.

### Corrections

- The frozen arm's traceback count is 9, not the 8 written above (F26 was
  added after the count; ScribeLogEntry, ConnQualityRules).
- `--no-lazy-fetch` is not defensive-only: a `remote.<n>.partialclonefilter`
  remote passes every refusal and lazy-fetches through `core.sshCommand`
  without it (CritDefensiveOnly P01/P02). Grid F27 now grades that channel
  and kills M02.
- The 40-hex `%H` check (M20) stays defensive-only, but not because
  signature display is disabled: no repository-local state reached it
  (CritDefensiveOnly). Its survival is reported, not credited.
- "Frozen 0/26" is not 26 fair isolation wins: F17, F21, F23 and F24 are
  contract changes (now kind `contract`), and F06, F13, F16, F26 pin
  current's own refusal wording (CritFrozenFairness). The catch-all alone
  removes all 9 tracebacks while meeting only F24 (CritSeparabilityW2).
- S095's `teaches` asserted a subprocess text-mode mechanism its page does
  not document (SrcS095). Status S095 mined→rejected; S096 supersedes it
  with the narrowed claim; S097/S098 anchor text mode and the TextIOWrapper
  strict default. S099 supersedes S092 (anchor is §Handling Missing
  Objects, SrcS092). S100 supersedes S091 (scope covers the transport key;
  adds `gpg.program` for F09, SrcS091). No other status, recheck or used-by
  changed.

### Gate — rows opened by the replacement L1 (2026-10-21)

- S096 https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode
  (3.14.9; `/library/` 301-redirects here) — "If 'strict' (the default), a
  UnicodeError exception is raised."
- S097 https://docs.python.org/3.14/library/subprocess.html (3.14.9),
  `subprocess.run()` — "opened in text mode using the specified encoding and
  errors or the io.TextIOWrapper default".
- S098 https://docs.python.org/3.14/library/io.html (3.14.9),
  `io.TextIOWrapper` errors — "Pass 'strict' to raise a ValueError exception
  if there is an encoding error (the default of None has the same effect)".
- S099 https://git-scm.com/docs/partial-clone (2.56.0), §Handling Missing
  Objects — "no check as to whether the missing object is actually a
  promisor object is performed".
- S100 https://git-scm.com/docs/git-config (2.56.0), `gpg.program` —
  "Pathname of the program to use instead of "gpg" when making or verifying
  a PGP signature."
- S101 https://raw.githubusercontent.com/git/git/v2.56.0/commit.c
  `read_graft_line` — "strbuf_rtrim(line); if (!line->len || line->buf[0] ==
  '#') return NULL;"

### Mistakes (continued)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M4 | Seat wrote fault fixtures into the real fleet repository: a falsify probe resolved its pack directory by upward git discovery from a non-repository path and created four zero-byte `.promisor` markers in `/home/vgpnk/Projects/shokunin/.git/objects/pack` (12:50:16 and 12:58:00 -03), which made the current audit refuse the real fleet | `.ufo/waves/round-23/falsify/fleet-contamination/promisor-markers.txt`; `falsify/out/RowF06LazyFetch-2/probe-variants.sh:56`; CritAxisScore, CritTradeoffHarm H1 | the wave contract forbade fleet writes but nothing checked a fixture's repository root | fixture builders must assert `rev-parse --show-toplevel` equals the fresh temp dir before writing into `.git`; the markers were removed by the first L1 and are absent at the replacement's check; C10 makes an orphan marker (no paired `.pack`) a control, so a stray marker no longer refuses a complete repository. Shown able to fail: M29 (drop the pairing) is killed by C10 |
| M5 | Seat misroot: scribe ScribeLogEntry wrote its report and draft under the fleet root (`/home/vgpnk/Projects/shokunin/.ufo/waves/round-23/falsify/…`) via a relative path | moved byte-exact into this lane (`falsify/advice/ScribeLogEntry.md` sha256 `e4eeeee5…bffb`, `falsify/out/ScribeLogEntry/LOG-round-23-entry.md` `2232b195…f292`), `cmp` equal, fleet copies removed | the wave context's absolute-path rule (not enforced) | swept before the report |
| M6 | Over-refusal shipped as isolation: the first integration refused any existing info/grafts file, so a complete repository with a comment-only grafts file went from a correct frozen verdict to exit 2 (CritRefusalScope) | replacement re-run of CritRefusalScope's probe on the working tree: `empty-grafts` and `comment-grafts` frozen 0 → current 2; the other nine cases equal | none (no control row) | C13 control + `grafts_effective` (S101); re-run: both cases now 0; M32 (refuse any grafts file) is killed by C13 |
| M7 | Harness leak: the grid's timeout killed only the auditor, leaving git children blocked on fixture FIFOs | 56 blocked `git` processes under `/tmp/repo-state-grid-*` / `/tmp/kama-r23w2/` (12:18–13:29 -03) | none | `run_case` starts each auditor in its own session and kills the session on timeout; after the final grid run 0 such processes remained |

### Falsify-wave disposition

73 seats dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow,
RowF09SignatureProgram, CritOpenHonesty, killed with the host session, no
output). Integrated: F27 (filter-only promisor), F28 (shallow fleet), F29
(broken branch + same-named tag), F30 (include FIFO, git timeout), C09–C13,
contract kind, mutant kill rule, M26–M32 (MutRetestA–D, CritDefensiveOnly,
CritAxisScore, CritRefusalScope, ConnQualityRules, SentinelDoSW2 hang half).
Reported open, not claimed (the claim covers the graded rows only; these
falsify any wider reading):

- near variants of graded channels still flip or refuse differently:
  `i18n.commitEncoding=UTF-16` (RowF22), the `resolve_branch` fallback when
  `refs/heads/<name>` exists but is unusable (RowF12), enclosing-repository
  variants of the subdirectory check (RowF21), promisor near variants
  (RowF23), timestamp near variants (RowF26), fenced/commented "Landed"
  headings (RowC04);
- a second `## Landed changes` section is ignored in both arms
  (ExecSecondLanded, measured 0/3 faults met in both arms);
  prefix-ambiguity overwrite (ExecAmbiguityFixture, 6/6 unmet in both arms);
  gitfile/linked-worktree redirect and FIFO `HEAD` (RevengeGitfile; the
  hang half is now bounded by the git timeout, not graded);
  `--shared`-of-partial bypass (CritTradeoffHarm H2, both arms);
- `--errata` naming a FIFO blocks; no memory ceiling on git output or on
  the SOURCES URL alternation (SentinelDoSW2);
- other kama/fleet gates that call git are unisolated (ConnSiblingTools);
- surviving detector-coverage mutants proposed by MutRetestA–D that the
  replacement did not add (e.g. N01 log-byte ignore, N02 listing-byte
  ignore, N03 casefold branch, D02 BOM stripping, D03 promisor symlink).

Declared trades, reported for the operator under the no-trade rule: a
complete blobless partial clone (T01) and a paired promisor pack without
promisor config (F23) are refused (exit 2) where frozen gave a verdict, and
git ≥ 2.45 is required.
