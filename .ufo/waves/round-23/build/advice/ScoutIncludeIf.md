# ScoutIncludeIf — repo-local `include.path` / `includeIf` and command-line `-c` precedence

Seat: `CloseKama22.ScoutIncludeIf` (leaf; no subagent dispatch). Scope: ONE repo-local state
channel — `include.path` and `includeIf` in `$GIT_DIR/config`, and whether the candidate
command-line `-c` values outrank values delivered through those includes — for
`tools/report-landing-audit.py` at base `master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.
git 2.56.0, Linux. All fixtures under `/tmp/kama-r23-scoutinc`; every git invocation used
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`.

Base was audited from the **HEAD blob**, not the worktree: at probe time the lane checkout had
` M tools/report-landing-audit.py` (already carrying `GIT_ISOLATION`), so base bytes were frozen at
`/tmp/kama-r23-scoutinc/audit-base.py`,
`git show 4fe9339f:tools/report-landing-audit.py` → blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`,
sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`. Only `git status`,
`git rev-parse` and `git show` were run in the lane repo: no tracked file, commit, ref, or `.jj`
operation was performed, and no lane/fleet repository was used as an audit fixture.

## 1. Verdict

Two answers, measured separately.

**(a) The precedence question — no-effect.** Command-line `-c` values override included
repo-local values for every key named by the candidate isolation: `i18n.logOutputEncoding`,
`log.follow`, and (probed additionally) `core.sshCommand`, `core.useReplaceRefs`. Included files
cannot outrank command scope, regardless of which include mechanism delivered them:
`include.path`, `includeIf "gitdir:…"`, `includeIf "onbranch:…"`,
`includeIf "hasconfig:remote.*.url:…"`, a chain of includes, tilde/relative include targets, or
the worktree-scope `$GIT_DIR/config.worktree`. End-to-end proof: a minimal argv patch adding the
candidate prefix (`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false`, before `-C`) to the frozen base script made every include-delivered fault
fixture clean or correct-without-execution (§5).

**(b) Include as a state channel at base — affects-verdict / crashes / executes.** An include is
only an indirection for writing the same key into `$GIT_DIR/config`; it reproduces the same C1
fault classes, no new one:

| Class | Include-delivered value | Base audit result |
|---|---|---|
| crashes | `[i18n] logOutputEncoding = ISO-8859-1` via `include.path` or `includeIf` | uncaught `UnicodeDecodeError` traceback, exit 1 |
| affects-verdict | `[log] follow = true` via `include.path` | `failed` (exit 1) → false `clean` (exit 0) |
| executes | `[core] sshCommand = <local script>` (promisor remote, missing object) | script executed during `cat-file --batch-check`; audit still exited 1 with `unresolved-full-hash` |

Caveat that is not a verdict: a **malformed** included value for a boolean key remains fatal even
when a later `-c` supplies a valid value (`log.follow=maybe` + `-c log.follow=false` →
`fatal: bad boolean config value 'maybe' for 'log.follow'`, rc 128), which the base auditor maps to
a typed refusal (exit 2), not a verdict. A FIFO include target blocks git's config parse
indefinitely (audit hangs; no verdict). Both are availability/refusal effects, not false verdicts.

## 2. Mechanism in the audited code (base blob 4fe9339f)

- `tools/report-landing-audit.py:79-85` — `git_env()` removes every inherited `GIT_*` variable and
  sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM="1"`. Repository-local config
  (`$GIT_DIR/config`, and `$GIT_DIR/config.worktree` when enabled) is still parsed by every git
  process, and includes inside it are followed.
- `:87-96` — `git()` runs `git -C <repo> <args>` with `text=True` and no `-c`/flags at base.
- Call sites that therefore parse repo-local includes: `:114`/`:131` `cat-file --batch-check`,
  `:148` `log --format=…`, `:166` `log --diff-filter=A --format=%at`,
  `:211`/`:222` `ls-tree`/`cat-file blob`, `:266` `show HEAD:<report>`,
  `:339` `show <branch>:<errata>`, `:381` `ls-tree -r`, `:403-404` `rev-parse`.
- Verdict paths: `:270` cutoff, `:282` unresolved full hash, `:286-287` pre/post split,
  `:302` `landed-omitted`.
- Consequently an included key is read exactly as if the key had been written literally in
  `$GIT_DIR/config`; only command-line `-c`/flags can outrank it.

## 3. Governing documentation (accessed 2026-10-21)

Both pages display “last updated in 2.56.0”, matching the installed git.

| Page / anchor | Located quote (≤25 words) | Bearing |
|---|---|---|
| git(1), `-c <name>=<value>` — https://git-scm.com/docs/git#Documentation/git.txt--cltnamegtltvaluegt | “Pass a configuration parameter to the command. The value given will override values from configuration files.” (16 words) | `-c` wins over any file value, hence over included values. |
| git-config(1), §Includes — https://git-scm.com/docs/git-config#_includes | “The contents of the included file are inserted immediately, as if they had been found at the location of the include directive.” (22 words) | Included values take the including file's (local) scope; they are not a separate, higher scope. |
| git-config(1), §Conditional includes (`gitdir`) — https://git-scm.com/docs/git-config#_conditional_includes | “If the location of the .git directory matches the pattern, the include condition is met.” (15 words) | `includeIf` is live from repo-local config, matched against the real gitdir. |
| git-config(1), §CONFIGURATION FILE / FILES — https://git-scm.com/docs/git-config#_configuration_file | “The files are read in the order given above, with last value found taking precedence over values read earlier.” (19 words) | File-scope ordering; included content participates at its splice point. |
| git-config(1), §Includes (relative path) — same URL | “the path is considered to be relative to the configuration file in which the include directive was found” (18 words) | A repo can point an include at a path relative to `.git/`. |

Not claimed from docs: the ISO-8859-1 decode traceback, lazy-fetch execution of `sshCommand`, and
the `log.follow` cutoff shift are probe observations, not documented behaviour (see ScoutLazyFetch /
ScoutLogFollow for those channels).

## 4. Reproduction — include delivers the base faults

All fixtures are fresh repos under `/tmp/kama-r23-scoutinc`; lane and fleet are separate repos;
reports were committed under `.ufo/reports/round-1/kama.md`. Audit command shape:
`python3 audit-base.py --lane-repo <lane> --fleet-repo <fleet> --rounds 1 --no-errata`.

1. **Encoding crash via `include.path`** (`f1b`): lane `.git/config` gains
   `[include] path = /tmp/kama-r23-scoutinc/f1b/inc.cfg` where `inc.cfg` is
   `[i18n]\n logOutputEncoding = ISO-8859-1`; lane has subject `round-1: café measure` (UTF-8).
   - `git -C lane config --show-origin --show-scope --get-all i18n.logOutputEncoding` →
     `local	file:/tmp/kama-r23-scoutinc/f1b/inc.cfg	ISO-8859-1`
   - control audit (no include): exit 0, `status=clean`.
   - with include: **exit 1**, stderr traceback ending in
     `UnicodeDecodeError` from `subprocess.run(..., text=True)` at base `:89`, raised in
     `round_commits` (`:148`). Python's uncaught-exit 1 is indistinguishable from a `failed`
     verdict to an exit-code consumer.
   - `git -C lane log -1 --format=%s <b>` output bytes:
     `726f756e642d313a20636166 e9 206d6561737572650a` (invalid UTF-8).

2. **Encoding crash via `includeIf "gitdir:<lane>/.git"`** (`f1c`): same include target, condition
   form. `--show-origin --show-scope` → `local	file:…/inc.cfg	ISO-8859-1`; base audit **exit 1**,
   same traceback. `includeIf "onbranch:master"` (`f1`) behaves identically (exit 1, traceback).
   Observation on git 2.56.0: the trailing-slash form `gitdir:/tmp/…/lane/.git/` did **not** fire
   (`git config --get` rc 1, no value) although the docs say a trailing `/` appends `**`; the
   no-slash form and directory forms do fire. Attacker's pattern choice; the channel stays live.

3. **Verdict flip via `log.follow`** (`f2b`): fleet root commit adds `draft.md` at author 900 with
   the report body; a second commit `git mv`s it to `.ufo/reports/round-1/kama.md` at 1200. Lane has
   `round-1: first` (1000, cited) and `round-1: omitted tail` (1100, uncited). Fleet config includes
   `[log] follow = true`.
   - `git -C fleet log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md` → `1200`
     (normal) vs **`900`** (include active; follows the rename).
   - control audit: exit 1, `UNCORRECTED landed-omitted ad1810e5…`.
   - include active: **exit 0, `required=0 post_report=2 defects=0 status=clean`** — false clean.

4. **Execution via `core.sshCommand` + promisor lazy fetch** (`f3b`): lane has a deleted loose blob,
   `core.repositoryFormatVersion=1`, `extensions.partialClone=origin`,
   `remote.origin.url=example.invalid:repo.git`, `remote.origin.promisor=true`; repo config includes
   `[core] sshCommand = /tmp/kama-r23-scoutinc/f3b/evil-ssh.sh`, where the script appends to a marker
   and exits 255. Report cites the missing 40-hex blob id.
   - `git -C lane cat-file --batch-check` (input `<blob>`) → stdout `<blob> missing`, stderr
     `fatal: Could not read from remote repository.`, rc 0, **marker created**.
   - base audit on that fixture: **exit 1** (`UNCORRECTED unresolved-full-hash <blob>`),
     **marker created** — the repo-configured command ran during the audit.
   - No real host was contacted: the URL is `example.invalid`, and `core.sshCommand` replaces ssh
     entirely. Same result with a `-c core.sshCommand=/bin/false` control: no marker (the `-c`
     override won), fetch still failed. With `--no-lazy-fetch`: no marker and no fetch error.

5. **Replace refs through included config** (`rep2`, hand fixture): repos A/B, `git replace A B`.
   - replacement active: `git cat-file -p A` shows B's tree `0ca5a955…`;
   - `git --no-replace-objects -C rep2 cat-file -p A` shows A's real tree `f1e88d92…`;
   - adding an include `[core] useReplaceRefs = true` does **not** defeat the flag
     (`--no-replace-objects` still returns `f1e88d92…`);
   - `-c core.useReplaceRefs=false` overrides an included `true`; `-c ...=true` overrides an
     included `false`.

6. **Include failure modes** (`f4`, `f8`): `include.path` is additive/multi-valued.
   - target file missing → silently ignored; audit exit 0, clean (no error);
   - target is a directory → every git call exits 128
     (`warning: unable to access '…': Is a directory` / `fatal: bad config line`);
     base audit exit **2** `could-not-evaluate` (typed refusal);
   - malformed included file → same rc 128 → base audit exit **2**;
   - `/dev/null` → harmless; audit exit 0;
   - relative target (`path = rel.cfg`, file at `.git/rel.cfg`) → included as
     `file:.git/rel.cfg` (local scope). End-to-end (`f14`: lane subjects `round-1: work` and
     `round-1: café measure`, report cites both): base audit **exit 1**, traceback tail
     `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 72`;
   - `~/extra.cfg` with fixture `HOME` → `local	file:/tmp/kama-r23-scoutinc/home/extra.cfg`,
     subject bytes `6361 66e9` (ISO), i.e. an include can read a file outside the repository.

## 5. Evidence — `-c` outranks included values

1. **Raw bytes, exact command.** With the ISO include active:
   - without `-c`: `git -C lane log -1 --format=%s <b>` → hex `726f756e642d313a20636166 e9 206d6561737572650a` (byte `e9`);
   - with `git --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
     -c log.follow=false -C lane log -1 --format=%s <b>` → hex
     `726f756e642d313a20636166 c3a9 206d6561737572650a` — valid UTF-8 `round-1: café measure`.
   - reverse direction (direct file value `UTF-8`, `-c i18n.logOutputEncoding=ISO-8859-1`) → byte
     `e9`, showing command scope is last-wins rather than a one-way override.
2. **End-to-end audit with the candidate prefix.** `/tmp/kama-r23-scoutinc/audit-base-iso.py` is the
   frozen base with only the `git()` argv changed to
   `["git", "--no-replace-objects", "--no-lazy-fetch", "-c", "i18n.logOutputEncoding=UTF-8",
   "-c", "log.follow=false", "-C", repo, *args]` (base text mode retained):
   - include-ISO lane (`f1b`): base exit 1 traceback → patched **exit 0, `status=clean`**;
   - includeIf-gitdir ISO lane (`f1c`): base exit 1 → patched **exit 0, clean**;
   - include-`log.follow=true` fleet (`f2b`): base exit 0 false clean → patched **exit 1** with
     `UNCORRECTED landed-omitted ad1810e5…` (`required=2 post_report=0`);
   - include-`sshCommand` promisor lane (`f3b`): base exit 1 with **marker created** → patched
     exit 1, **marker not created**, same `unresolved-full-hash` defect.
3. **Scope ladder, `git config --show-origin --show-scope --get-all`.**
   - include chain (`repo → inc2.cfg → inc.cfg`, `f5`): `local ISO-8859-1` + `command UTF-8` for the
     `-c` run; `local true` + `command false` for `log.follow`; `local /bin/false` +
     `command /bin/true` for `core.sshCommand`.
   - `includeIf "hasconfig:remote.*.url:https://example.invalid/r"` in repo-local config was
     activated by `-c remote.origin.url=https://example.invalid/r` (shows
     `local file:inc-follow.cfg true`), and adding `-c log.follow=false` still yields
     `command false` after it. A `-c` can *activate* an include, but the included values stay local.
   - worktree scope: `$GIT_DIR/config.worktree` with ISO (`d` probe) shows
     `worktree file:.git/config.worktree ISO-8859-1` followed by `command UTF-8`; the command scope
     still wins.
4. **Includes cannot be switched off by `-c`, but do not need to be.** On the tilde/include fixture,
   `git -C f13 -c include.path=/dev/null config --show-scope --get-all
   i18n.logOutputEncoding` still prints `local ISO-8859-1` — `include.path` is additive and has no
   negation. The override works by pinning the key, not by suppressing the include.
5. **Observed non-matches.** `includeIf "gitdir:…/.git/"` (trailing slash) did not fire in git
   2.56.0; `include.path` of a missing file and `/dev/null` have no effect. None of these reduces
   the channel, since the no-slash gitdir, `onbranch`, `hasconfig`, plain `include.path`, chain,
   relative and tilde forms all fire.

## 6. Residuals / boundaries (do not overclaim)

- **Malformed boolean is not cured by `-c`.** `[log] follow = maybe` in a direct or included config
  plus `-c log.follow=false` → `fatal: bad boolean config value 'maybe' for 'log.follow'`, rc 128.
  The base auditor turns that into exit 2 `could-not-evaluate` (typed refusal, no traceback), never
  a verdict. This matches ScoutLogFollow §7 for direct repo-local config; include delivery is
  identical.
- **FIFO include target blocks the audit indefinitely.** `include.path` pointing at a named pipe
  made `git config` hang past a 2 s timeout (`blocked=true`); a selected hostile repo could hang the
  audit rather than yield a verdict. Not a verdict flip; a separate availability concern (cf.
  SentinelResourceDoS).
- **Keys outside the override set still apply.** Sampled include-delivered keys against the exact
  audit commands: `log.showSignature=true` (end-to-end audit stayed clean), `color.ui=always`,
  `log.decorate=full`, `log.date=iso`, `core.abbrev=4` all produced byte-identical
  `--format=%H%x1f%an%x1f%at%x1f%s%x1e` output; `core.fsmonitor=<script>` was **not** invoked by
  any of `rev-parse`, `ls-tree`, `cat-file`, `show`, `log` (marker absent each time). This is a
  finite sample, not proof for every key.
- **Includes are a read channel.** `~/` expansion and relative paths let repo-local config make git
  read files outside the repository into local scope (fixture `HOME` only; no user file was read).
  The values remain below command scope.
- Scope is the C1 fault grid: this is not general untrusted-repository hardening, and no claim is
  made that every repo-local include is harmless once the two keys/flags are pinned.

## 7. Not verified

- Did not run the lane worktree's in-progress `GIT_ISOLATION` implementation (it was modified during
  the probe and is L1's integration); precedence was measured on the frozen base plus a minimal
  prefix patch whose argv is byte-identical to the candidate's constant.
- Did not enumerate every config key an include could set; sampled keys are listed in §6.
- Did not use any real network transport: promisor fixtures used `example.invalid` and a local
  `core.sshCommand` marker script that exits before any connection. `--no-lazy-fetch` was tested on
  the audit's `cat-file --batch-check` path only.
- Did not test `includeIf "worktree:"`, `gitdir/i:` or case-insensitive variants, top-level
  `--config-env`, or git versions other than 2.56.0.
- Did not test `/dev/zero` or other unbounded include sources; only the FIFO hang was exercised.
- Did not run the selftest (50/50), historical ledger rounds 10–22, or any landing gate; those are
  other seats' checks.
- No tools installed or upgraded.

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/ScoutIncludeIf.md`
  (this report; the only repo file written by this seat).
- Scratch evidence under `/tmp/kama-r23-scoutinc/`: `audit-base.py` (frozen base),
  `audit-base-iso.py` (base + candidate argv prefix), `harness.py`, `harness2.py`, `harness3.py`,
  `results.json`, `results2.json`, `results3.json`, fixture repos/fixtures (`f1…f14`, `gd`, `rep2`,
  `home`, marker/scripts), fetched doc text (`git.html`, `git-config.html` and `.txt` conversions,
  `conditional-includes.txt`, `scopes2.txt`).
