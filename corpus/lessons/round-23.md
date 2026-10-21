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
