# ScoutObjectFormat — repository object format (sha256 / compatObjectFormat)

Seat: `CloseKama22.ScoutObjectFormat` (leaf, no dispatch). Round 23, C1 calibration, one assigned
channel. Read-only on the lane and fleet; every fixture below ran in fresh `mktemp` repos under `/tmp`
with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. Base master
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`; git 2.56.0; date 2026-10-21.

## 0. Verdict

**affects-verdict** — the lane repo's object format silently changes the verdict in both directions,
and over-refuses on a third citation shape. No traceback crash; no command execution.

| Outcome | When | Evidence |
|---|---|---|
| false `failed` (rc 1) | sha256 lane; report cites its commits correctly as full 64-hex | probe `sha256-full`: `defects=2 uncorrected=2 status=failed`; both defects are `landed-omitted` naming the commits the report cites |
| false `clean` (rc 0) | sha256 lane; report cites a fabricated 64-hex token | probe `sha256-fabricated64`: `defects=0 … status=clean`; the sha1 control on the same shape catches it (`sha1-fabricated40`: `landed-unresolved 1`, `unresolved-full-hash 1`) |
| typed refusal (rc 2) | sha256 lane; report cites a *correct* 12- or 40-hex prefix of the native SHA | probe `sha256-prefix12`: `could-not-evaluate: cat-file … unexpected '<64-hex> commit 239'` |
| false `failed`, 4 defects | sha256 lane + `extensions.compatObjectFormat=sha1`; report cites the compat sha1 names | probe `compat-sha1-names`: `defects=4` — 2 `landed-unresolved` (the sha1 names) + 2 `landed-omitted` (the same commits) |
| no effect | sha256 **fleet** only, sha1 lane, correct 40-hex citations | probe `sha256-fleet-only`: rc 0 clean |
| typed refusal (rc 2), safe | `extensions.objectFormat=sha256` or `extensions.compatObjectFormat=sha1` written into an existing sha1 repo | probes `flip-objectFormat`, `flip-compatObjectFormat`: rc 2 `fatal: repo version is 0, but v1-only extension found` |

The trigger is the **lane** repo's format (`--lane-repo`). A sha256 fleet alone is benign because the
report blob, cutoff and `ls-tree` paths work unchanged and the cited objects live in the lane.

## 1. Repro (written artifact, rerunnable)

Script: `.ufo/waves/round-23/build/out/CloseKama22.ScoutObjectFormat/objectfmt-probe.sh`
Transcript: `.ufo/waves/round-23/build/out/CloseKama22.ScoutObjectFormat/objectfmt-probe.out`

```
control-sha1-full        rc=0  summary reports=1 defects=0 … status=clean
sha256-full              rc=1  summary reports=1 defects=2 … status=failed
sha256-fabricated64      rc=0  summary reports=1 defects=0 … status=clean
sha1-fabricated40        rc=1  summary reports=1 defects=2 … status=failed
sha256-prefix12          rc=2  could-not-evaluate: cat-file in …/L5: unexpected '8475877d…e5cd commit 239'
compat-sha1-names        rc=1  summary reports=1 defects=4 … status=failed
flip-objectFormat        rc=2  could-not-evaluate: git rev-parse --verify master^{commit} … repo version is 0, but v1-only extension found:
flip-compatObjectFormat  rc=2  could-not-evaluate: git rev-parse --verify master^{commit} … repo version is 0, but v1-only extension found:
sha256-fleet-only        rc=0  summary reports=1 defects=0 … status=clean
```

The compat row's render (separate one-off run, same fixture shape):

```
round=1 required=2 post_report=0 defects=4
  UNCORRECTED landed-unresolved 9c7ed1d429943b2278227fc5c9dacecc5e29fec8
  UNCORRECTED landed-unresolved db796f8b820bf3825c58832419138cdba23206a7
  UNCORRECTED landed-omitted 8475877df75fd3b6326a217f3935343cafd5ddb488491136aba7fb0e64dc2ac4
  UNCORRECTED landed-omitted a8ed7535bb4138ff8104a6a019d67a275b04d42a059ad6f056563d9fdfbee5cd
rc=1
```

Control unchanged: the committed selftest still passes at base —
`python3 tools/report-landing-audit.py --selftest` → `selftest cases=50 failed=0`, rc 0.

## 2. Mechanism — observed at base

1. **Scanner is SHA-1-shaped.** `tools/report-landing-audit.py:66-67`:
   `FULL = [0-9a-f]{40}` and `ABBREV = [0-9a-f]{7,40}`, both wrapped in
   `(?<![0-9A-Za-z]) … (?![0-9A-Za-z])`. A 64-hex run matches neither: the start lookbehind and the
   end lookahead fail at every offset. Direct check:
   `FULL.findall(<64-hex>) == []`, `ABBREV.findall(<64-hex>) == []`, while the same 40-hex string
   matches `FULL`. Consequence in `audit_round`: `full_tokens` is empty (no full-hash check at all)
   and `cited` is empty.
2. **Native hashes are 64-hex.** `round_commits` reads `git log --format=%H`
   (`tools/report-landing-audit.py:164-165`), which on a sha256 repo prints 64 hex (probe
   `sha256-full` defects carry 64-hex tokens). With `cited` empty, the omission test at
   `:318-321` (`commit["sha"].startswith(t)`) is false for every pre-cutoff commit, so each one is
   appended as `landed-omitted` — a defect the report cannot fix, because the correct citation is
   exactly the string the scanner cannot see.
3. **`cat-file` echo must be 40 hex.** `lookup` parses `cat-file --batch-check` output and rejects
   the line unless the echoed object name has exactly 40 hex chars
   (`tools/report-landing-audit.py:145-147`, `re.fullmatch(r"[0-9a-f]{40}", parts[0])`). On a sha256
   repo `cat-file` resolves a 12- or 40-hex prefix and echoes the full 64-hex name, so a *correct*
   abbreviated citation raises `EvalError` → exit 2. Non-resolving tokens still print `missing`, so
   the refusal depends on whether the citation is right.
4. **compatObjectFormat.** In a `sha256 + extensions.compatObjectFormat=sha1` repo, a compat sha1 name
   resolves bare but not when peeled:
   ```
   $ printf 'db79…06a7^{commit}\ndb79…06a7\n' | git -C <compat-repo> cat-file --batch-check
   db79…06a7^{commit} missing
   db79…06a7 commit 140
   ```
   `audit_round` looks up citations with `peel="^{commit}"`, so compat citations become
   `landed-unresolved`, while `round_commits` still yields 64-hex native SHAs that no citation can
   match → the same commits are also `landed-omitted` (4 defects for 2 commits).
5. **No format awareness in the tool.** `grep -in "sha256\|object.format\|objectFormat"
   tools/report-landing-audit.py` → no matches. Neither `git()` (`:97-105`) nor `git_env()` (`:88-95`)
   probes `rev-parse --show-object-format`; `--show-object-format` is not called anywhere.
6. **The real repos are sha1** (read-only check): `git -C <lane> rev-parse --show-object-format` →
   `sha1`; same for the fleet root.

## 3. Reachability / scope — observed

- Writing the extension into the *existing* v0 repo is rejected by git itself before the auditor can
  form a verdict: `fatal: repo version is 0, but v1-only extension found: objectformat` (and
  `compatobjectformat`), and the auditor reports `could-not-evaluate` rc 2. So the real lane cannot be
  flipped into sha256 by repo config.
- The channel therefore needs an audited repo that was *created* sha256 (`git init
  --object-format=sha256`) and passed as `--lane-repo`/`--fleet-repo`, or a compat repo created the
  documented way. That is an accepted input path (the CLI takes arbitrary repo paths), not a config
  flip of the fleet.

## 4. Governing docs (accessed 2026-10-21)

| URL | Quote (≤25 words) |
|---|---|
| https://git-scm.com/docs/git-config#Documentation/git-config.txt-extensionsobjectFormat | "Specify the hash algorithm to use. The acceptable values are `sha1` and `sha256`. If not specified, `sha1` is assumed." (19 words) |
| https://git-scm.com/docs/git-config#Documentation/git-config.txt-extensionscompatObjectFormat | "Specify a compatibility hash algorithm to use. The acceptable values are `sha1` and `sha256`." (14 words) — and "It currently exists only to allow development and testing of the underlying feature and is not designed to be enabled by end users." (23 words) |
| https://git-scm.com/docs/git-init#Documentation/git-init.txt---object-formatltformatgt | "Specify the given object `<format>` (hash algorithm) for the repository. The valid values are `sha1` and (if enabled) `sha256`." (19 words) |

The object format is a per-repository extension, so it is exactly the kind of repository-local state
the tool's docstring claims cannot redirect it (`git_env` only pins global/system config). The pages
do not document the auditor's failure; the verdicts above are probe results.

## 5. Meaning for the C1 candidate direction [INFERENCE]

- The listed candidate controls (`--no-replace-objects`, `--no-lazy-fetch`,
  `-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`, bytes-mode reads) do **not** touch this
  channel: `-c` cannot change a repo's object format, and the 40-hex cap is in the scanner/parser, not
  in git output. A fix must be its own move.
- Cheapest correct move consistent with "Errors are never verdicts": probe
  `git rev-parse --show-object-format` once per repo and raise `EvalError` (exit 2) when it is not
  `sha1`, before any scanning. That turns three wrong verdicts into one typed refusal and costs one git
  call. A stronger but larger move is length-aware `FULL`/`ABBREV`/`lookup`, which would also make the
  tool audit sha256 repos correctly; it does not remove the need to decide whether non-sha1 is
  supported.
- Severity for the current fleet is low (both repos are sha1; flipping is refused), but the failure is
  silent on the false-clean side and unavoidable for a report author on the false-failed side, so it
  belongs in the fault grid as a verdict-flip, not a crash row.

## 6. Not verified

- Did not run the audit against the real lane or fleet (contract); the control is the committed
  selftest only.
- Did not test the `--report N=PATH` draft path, `--errata`, or historical errata corrections on a
  sha256 lane; they use the same `lookup`/`round_commits` code, but no probe row exists.
- Did not test a sha256 repo reached through `clone`/`--shared`, alternates, or a partial clone; only
  fresh `git init` repos.
- Did not test `core.repositoryFormatVersion=1` without a changed hash, nor any other extension.
- No tools installed or updated; no files outside the two paths below were written.

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/ScoutObjectFormat.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/CloseKama22.ScoutObjectFormat/objectfmt-probe.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/CloseKama22.ScoutObjectFormat/objectfmt-probe.out`

## 8. Amendment (appended; sections 0-7 unchanged as record)

Closure check: a sha256 lane with at least one pre-cutoff round commit **cannot** reach exit 0.
- every citation invisible (full 64-hex): all pre commits become `landed-omitted` → rc 1
  (probe `sha256-full`);
- any citation in 7-40 hex that resolves: `lookup` raises before defects are computed → rc 2
  (probes `sha256-prefix12`, and a mixed full+prefix run observed
  `could-not-evaluate: cat-file … unexpected '33e42661…92f8 commit 237'`, rc 2);
- any citation in 7-40 hex that does not resolve: `landed-unresolved` plus the same omissions → rc 1.

The only remaining escape is a report with no pre-cutoff commits (probe `sha256-fabricated64`), which
is also where the false-clean shows. This makes the false-failed branch total, not incidental.
