# ScoutShowSignature — repo-local `log.showSignature` (plus `log.decorate`, `format.pretty`, `log.date`, `color.ui`, `core.pager`, `log.abbrevCommit`) vs `tools/report-landing-audit.py` (round 23, C1 calibration)

Seat: `CloseKama22.ScoutShowSignature` (leaf, no dispatch). Scope: ONE repo-local state
channel family — the seven listed config keys — against the audit at base
`master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (git 2.56.0). Base was audited from the
**HEAD blob**, not the working tree: the lane checkout's `tools/report-landing-audit.py` is
modified (`git status --porcelain` → ` M`) and its uncommitted `GIT_ISOLATION` now includes
`-c log.showSignature=false` (line 92, mtime 2026-10-21 12:14:30 -0300). The base blob
contains **0** occurrences of `showSignature`/`gpg.program`
(`git show 4fe9339f:tools/report-landing-audit.py | grep -ci …` → `0`); base blob is 847
lines, sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f2`.

## 1. Verdict

| key (repo-local) | parsed `git log` records changed? | `cat-file` output changed? | verdict |
|---|---|---|---|
| `log.showSignature` | **yes, iff a displayed commit is signed** — verification text is prepended *inside* the `--format` record | no | **affects-verdict** (conditional) + **executes** when paired with repo-local `gpg.program` / `gpg.ssh.program` |
| `log.decorate` | no (`full`/`auto`, 40-hex + subject format has no `%d`) | no | no-effect |
| `format.pretty` | no (explicit `--format` wins) | no | no-effect |
| `log.date` | no (`%at` is raw epoch) | no | no-effect |
| `color.ui` | no (`always`/`true`; custom format has no color slots) | no | no-effect |
| `core.pager` | no (stdout is a pipe; pager never launched — marker never written) | no | no-effect (and does not execute) |
| `log.abbrevCommit` | no (`%H` full) | no | no-effect |

Among the seven keys tested, only `log.showSignature` moves the audit's parsed bytes. With a signed commit that
`round_commits()` accepts (author `<lane>-shokunin`, subject `round-N:`/`checkpoint(rN)`), it
turns a true `clean` (exit 0) into a false `failed` (exit 1) carrying a garbage
`landed-omitted` token. On an unsigned history it is inert.

The measurement is one row of the ticket’s fault grid: a fresh reproduction under
`/tmp/kama-r23-show-sig` at base vs repo-local config, then the same fixture with the
candidate clause `-c log.showSignature=false` alone (base copy patched on disk in /tmp).
Baseline control is `clean` exit 0; the showSignature run is `failed` exit 1; the clause run
returns the baseline bytes `log sha256 6adfc143c314cedd…` and exit 0.

## 2. Mechanism in the audited code (base blob 4fe9339f)

- `tools/report-landing-audit.py:79-84` — `git_env()` sets only
  `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. `$GIT_DIR/config` is still read;
  the docstring (`:80-81`) claims "neither the audited repos nor the selftest fixtures can be
  redirected", which this channel falsifies (same shape as the C1 calibration).
- `:87-98` — `git()` runs `git -C <repo> <args>` with `text=True`; no `-c` isolation at base.
- `:147-162` — `round_commits()` runs
  `git log --format=%H\x1f%an\x1f%at\x1f%s\x1e <branch>` (no pathspec, so **every** commit in
  the branch is displayed, including merges). It splits on `\x1e`, takes `fields[0]` as the
  sha (`:158`), checks `fields[2]` is digits (`:157`), then filters
  `author == f"{lane}-shokunin" and pat.match(subject)` (`:160`) and appends
  `{"sha": sha, ...}` (`:161`).
- With `log.showSignature=true`, git prints the gpg/ssh verification block **before** the
  formatted line of a signed commit, still inside the same `\x1e`-delimited record. So
  `fields[0]` becomes `"Good \"git\" signature for …\n<real sha>"` (or `"No signature\n<sha>"`,
  or three `gpg:` lines) — `sha` is no longer a 40-hex token.
- `:285-304` — for each `pre` commit, `landed-omitted` is emitted unless
  `commit["sha"].startswith(<cited token>)` (`:301-304`). A polluted `sha` never matches, so
  each signed qualifying commit becomes an uncorrectable false `landed-omitted`; `int(atime)`
  still parses (the polluted field is `fields[0]`, digits field is untouched), so the run
  reaches a verdict instead of raising.
- `:165-167` — `report_cutoff()` uses `--format=%at` and `int(out[-1])`. Signature text
  precedes the epoch line, so the last whitespace token is still the epoch: **inert** (proved
  below with a signed report commit: output `Good …\n1200\n` → cutoff 1200).
- `:266`, `:339` — the only `git show` calls are blob selectors (`HEAD:<rel>`,
  `<branch>:<ERRATA>`); blob show has no commit signature and is byte-identical (proved).
- `:114-116` — `cat-file --batch-check` output is unaffected by every key tested.

## 3. Reproduction

Fixture (`/tmp/kama-r23-show-sig/probe.py`, `extra2.py`; fresh repos, every git child gets
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`): lane `a`@1000 "round-1: work", `b`@1100
"round-1: measure", `c`@1150 "checkpoint(r1) save" (all `kama-shokunin`), late@1300; fleet
report at 1200 cites `a`,`b`,`c`. Baseline: `clean`, exit 0, `required=3`.
Audit invocation (base blob saved as `/tmp/kama-r23-show-sig/base-audit.py`):

```
python3 base-audit.py --lane-repo …/lane --fleet-repo …/fleet \
    --branch master --lane kama --rounds 1 --no-errata --json
```

13 configs × {lane, fleet} = 26 applications per fixture. Unsigned fixture: **26/26 inert**
(verdict clean exit 0; `log` bytes sha256 `643ea7ab…`, `cat-file` bytes `07eda116…` for every
row). Signed fixture (commit `a` and the fleet report commit signed with a throwaway
ed25519 ssh key, `gpg.ssh.allowedSignersFile` repo-local): **25/26 inert**; the single
non-inert row:

| repo-local config | exit | summary | parsed log bytes | defect |
|---|---|---|---|---|
| none (control) | 0 | `clean` | `6adfc143c314cedd…` | none |
| `log.showSignature=true` @lane | **1** | `failed` | `f88d4bbdb138fdd0…` | `landed-omitted` token = `Good "git" signature for test@example.invalid with ED25519 key SHA256:wABLmh9udpFTUiKmlDzxda1fxyDBllPIlD05lDN+M+0\nb6af2589347b350bc5f245728372de7bbf37a032` |
| `log.showSignature=true` @fleet | 0 | `clean` | unchanged | none (cutoff log = `Good …\n1200`, still parses `1200`; blob show identical) |
| `log.showSignature=true` + `-c log.showSignature=false` (patch) | 0 | `clean` | `6adfc143c314cedd…` (baseline exact) | none |

Rendered false verdict (signed fixture, repo-local `true`, base script):

```
round=1 required=3 post_report=1 defects=1
  UNCORRECTED landed-omitted Good "git" signature for test@example.invalid with ED25519 key SHA256:wABLmh9udpFTUiKmlDzxda1fxyDBllPIlD05lDN+M+0
b6af2589347b350bc5f245728372de7bbf37a032
summary reports=1 defects=1 corrected=0 uncorrected=1 errata_unmatched=0 errata_invalid=0 status=failed
```

The false token even embeds the real commit id (after a newline); the citation set never
matches it (`startswith` against `b6af258…` is false for the whole string).

E-state (signature present but unverifiable — `gpg.ssh.allowedSignersFile` removed, `%G?` =
`E`, matching the real lane repo’s signed commit): the record prefix is `No signature\n<sha>`
and the audit still exits **1** with `landed-omitted` = `No signature\n<sha>`. So a merely
*unverifiable* signature poisons too; the repo does not need a trusted key.

Unsigned control (26/26): no signature block is printed for unsigned commits, so
`log.showSignature=true` is inert on an all-unsigned history, including `git show` of blobs.

Malformed-value edges (all on the unsigned fixture): `log.showSignature=maybe`,
`log.abbrevCommit=maybe`, `color.ui=maybe` → git `fatal: bad boolean config value`, audit
exit **2** (typed `EvalError`, no verdict); `format.pretty=maybe` →
`fatal: invalid --pretty format`, exit 2; `log.date=maybe` → `fatal: unknown date format`,
exit 2; `log.decorate=maybe` and `core.pager=/nonexistent/pager` → exit 0 `clean`. These are
pre-existing typed refusals, not verdicts; they remain exit 2 under the patch.

## 4. The six inert keys — byte evidence

Each was set in `lane/.git/config` and `fleet/.git/config` separately and the audit re-run.
In every case the verdict, `git log --format=%H\x1f…` bytes (sha256), `git cat-file
--batch-check` bytes, `report_cutoff` output and `git show HEAD:<report>` bytes were
identical to the no-config control (2×13 rows in the unsigned fixture; 2×13 in the signed
fixture except the showSignature row above). In particular:

- `log.decorate=full|auto` — no `%d`/`%D` in the format, so no decoration is emitted; the
  ref-name decoration has no insertion point.
- `format.pretty=oneline|raw|format:%H` — explicit `--format=` wins; blob `git show` is raw
  regardless.
- `log.date=relative|raw|iso` — `%at` is the raw epoch placeholder, independent of the
  human date mode.
- `color.ui=always|true` — no color slots (`%C…`) in the custom format; capture is a pipe.
- `core.pager=<shell writing a marker>` — marker file **never created** by any audit
  invocation; the pager is not launched on a non-tty (and the audit never passes
  `--paginate`). So `core.pager` is neither a byte channel nor an execution channel here.
- `log.abbrevCommit=true` — assumes `--abbrev-commit`, which only affects `%h`; the audit
  reads `%H`.

## 5. Execution gateway (`log.showSignature` + repo-local signature program)

`log.showSignature=true` makes git verify signatures, i.e. run the configured program for
signed commits. In the fixture with a hand-crafted PGP-signed commit (author
`kama-shokunin`, subject `round-1: pgp signed`, fake `gpgsig` block):

| repo-local config | marker written during audit | exit / status |
|---|---|---|
| `gpg.program=<marker script>`, showSignature unset | **no** | 0 clean |
| `gpg.program=<marker script>`, `log.showSignature=true` | **yes** | 0 (verdict depends on the program’s stdout) |
| same, plus `-c log.showSignature=false` | **no** | 0 clean |
| `gpg.ssh.program=<marker script>`, `log.showSignature=true` (ssh-signed commit) | **yes** | 0 |
| same, plus `-c log.showSignature=false` | **no** | 0 clean |

So `showSignature` is the gateway; `gpg.program`/`gpg.ssh.program` is the executed key. A
program that prints nothing leaves the verdict `clean`; one that prints verification text
(or arbitrary text) corrupts records as in §3. This is the same shape as the C1
`core.sshCommand` lazy-fetch execution, but gated by `log.showSignature` + a signed commit.
On the **real** lane history the gateway is live: `git -c log.showSignature=true log
--format=… master` (read-only) invoked the system gpg and printed
`gpg: Signature made …`, `gpg: using RSA key B5690EEEBB952194`,
`gpg: Can't check signature: No public key` for commit `5396a876…`.

## 6. `-c log.showSignature=false` is sufficient and wins over repo-local `true`

- Command-line `-c` has command scope and overrides file scopes:
  `git -c log.showSignature=false log --format=%H\x1f… master` yields sha256
  `6adfc143c314cedd…`, byte-identical to the no-config baseline (which is `6adfc143…`).
- On-disk patched base copy (`["git", "-C", str(repo)…` → `["git", "-c",
  "log.showSignature=false", "-C", str(repo)…`, `/tmp/kama-r23-show-sig/patched-audit.py`)
  returns exit 0 `clean` on the signed fixture with repo-local `true`, and writes no
  `gpg.program`/`gpg.ssh.program` marker.
- `--no-show-signature` on the `log` call also restores the default, but `-c` in the global
  position is the form that covers every git call (including `git show`) from the single
  wrapper.
- Limit: `-c log.showSignature=false` does **not** cure a malformed local boolean
  (`log.showSignature=maybe`): git validates the local value and exits 128, audit exit 2
  before and after. That is a typed refusal (`EvalError`), not a verdict, so the C1
  “errors are never verdicts” property holds; it is simply not curable this way.

## 7. Real-history status: record bytes moved, verdict not flipped today

- Lane (`/home/vgpnk/Projects/shokunin/kama-shokunin`, 96 commits on `master`): `%G?` census
  `95 N`, **`1 E`** = `5396a876c466fcaa2c0b78715793ec280dfced6a`, PGP `gpgsig`, author
  `João Pedro Veiga <jpveigao10@gmail.com>`, subject
  `Merge pull request #2 from VeigaPunk/devin/wiki-link`, reachable from `master`.
  `git -c log.showSignature=true log --format='%H%x1f%an%x1f%at%x1f%s%x1e' master`
  changed stdout sha256 `b6aecfe7…` → `b2bb1fe8…`, adding exactly the three `gpg:` lines;
  exit 0. Because the author is not `kama-shokunin` and the subject does not match
  `round-N:`/`checkpoint(rN)`, `round_commits()` skips that record at `:160` — **so no
  current kama verdict changes from `log.showSignature` alone**. A signed round commit by
  `kama-shokunin` would (fixture §3), and the gpg invocation already happens on real
  history whenever the key is enabled.
- Fleet (`/home/vgpnk/Projects/shokunin`, 1025 commits): `1024 N`, `1 E` =
  `550ddf97ce599d941ee64b4b46b4fb21faf3313d` (same foreign author, merge). All 20 committed
  `.ufo/reports/round-*/kama.md` paths: `--diff-filter=A --format=%at` last token identical
  with `-c log.showSignature=true|false` (sweep printed no `DIFF`); all 20
  `git show HEAD:<path>` blob sha256 identical with/without the key. Fleet calls are inert.
- Neither repo’s local config currently sets `log.showSignature`
  (`git config --local --get log.showSignature` → rc 1 in both). Latent channel, not live.

## 8. Documentation (all accessed 2026-10-21)

- `log.showSignature` — https://git-scm.com/docs/git-config#Documentation/git-config.txt-logshowSignature
  (page lines 5773-5775): “If true, makes git-log[1], git-show[1], and git-whatchanged[1]
  assume `--show-signature`.” (9 words). The `git-show` clause is commit-show only; the
  audit’s `show` calls are blob selectors and stayed byte-identical.
- `log.decorate` — same page, lines 5713-5714: “Print out the ref names of any commits that
  are shown by the log command.” (15 words).
- `format.pretty` — same page, line 4207: “The default pretty format for
  log/show/whatchanged command.” (7 words) — a default, so an explicit `--format` wins.
- `log.date` — same page, lines 5704-5705: “Set the default date-time mode for the `log`
  command.” (9 words).
- `color.ui` — same page, lines 2345-2347: “Set it to `always` if you want all output not
  intended for machine consumption to use color” (17 words).
- `core.pager` — same page, lines 3115-3118: “Text viewer for use by Git commands (e.g.,
  less). … The order of preference is the `$GIT_PAGER` environment variable, then
  `core.pager` configuration …” ; `pager.<cmd>` lines 6584-6585: pagination is for a
  subcommand “when writing to a tty.” The audit captures stdout through a pipe.
- `log.abbrevCommit` — same page, lines 5699-5700: “If `true`, make git-log[1], git-show[1],
  and git-whatchanged[1] assume `--abbrev-commit`. You may override this option with
  `--no-abbrev-commit`.” (first sentence 9 words).
- Config precedence / local scope — https://git-scm.com/docs/git (lines 346-347): “Pass a
  configuration parameter to the command. The value given will override values from
  configuration files.” (16 words). https://git-scm.com/docs/git-config (lines 733-735):
  “`$GIT_DIR/config` — Repository specific configuration file.”; the audit’s `git_env()`
  disables only global/system scopes, so this file is still read.

## 9. What I did NOT verify

- Did not run the base or candidate selftest. Source inspection only: the selftest fixtures
  create fresh repos and only commit with `-c commit.gpgsign=false` (no `-S`, no crafted
  `gpgsig`, no `log.showSignature` config), so the channel is inert for the existing 50/50
  selftest; I did not execute it.
- Did not run the audit against the real lane/fleet repos (bounds). Real-repo evidence is
  read-only `git log`/`git config`/`git show` queries only; no fixture repo was pointed at
  them, and no repo-local config was written there.
- Did not test signed **tags**, GPG keyring trust states beyond “no public key” (`E`) and
  ssh `Good`/`No signature`, or `gpg.format=openpgp` with a real private key. The mechanism
  does not depend on verification succeeding (E-state poisons too).
- Did not test git versions other than 2.56.0, nor `extensions.worktreeConfig` (repo-local
  `config.worktree`) for these keys — `git -C` reads it when enabled, so it is the same
  channel in a second file.
- Did not test whether a run with repo-local `log.showSignature=true` and a signing program
  that emits `\x1e`/`\x1f` can fabricate records; the arbitrary-output property of a
  repo-configured program makes that plausible but it was not measured.
- No tool installs or upgrades were needed or performed.

## 10. Files written

- `.ufo/waves/round-23/build/advice/ScoutShowSignature.md` (this report; append-only).
- Scratch only, outside the lane: `/tmp/kama-r23-show-sig/base-audit.py`,
  `probe.py`, `extra2.py`, `patched-audit.py`, `matrix.json`, `probe.err`, `extra2.err`,
  `real-lane-sig.log`, `real-lane-sig.err`, `sigkey{,.pub,.allowed}`,
  `fakegpg.sh`, `fakessh.sh`, `failgpg.sh`, markers, and fixture repos under
  `/tmp/kama-r23-show-sig/repro/{unsigned,signed,foreign,gpgprog}`.
- No lane file, no out/ artifact, no registry/lesson write.
