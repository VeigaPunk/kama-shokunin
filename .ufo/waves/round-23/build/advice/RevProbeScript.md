# RevProbeScript: review of the L1 fault probe (round 23)

Scope: `/tmp/kama-r23-probe/probe.sh` (sha256 `3e9a6e4d…`) and its outputs, checked against the frozen base and the candidate `tools/report-landing-audit.py`. Findings only. No production or lane-tracked file was edited.

## Pins
- Frozen base: `4fe9339f…` blob extracted to `/tmp/kama-r23-probe/frozen-audit.py` (sha256 `09ecd63b…`, 847 lines).
- Candidate: the lane working tree is still moving (uncommitted ` M tools/report-landing-audit.py`; it grew 864 → 919 → 921 → 924 lines during this review). Snapshots tested: `79d9e124…` (921 lines) and `68476410…` (924 lines, latest). Every exit code below is identical on both, except the F1-round row, which was run on `79d9e124…` only.
- git 2.56.0, Python 3.14.8.

## Findings (severity order)

- **[High] F-1. The shipped f3 row does not reproduce claim (c) and cannot be trusted.** The replace fixture depends on ambient git identity and fails silently without it. In 4 of the 5 probe output directories there is no replace ref and the verdict is the honest `landed-omitted`. The claim is real: with identity pinned it reproduces (frozen exit 0 clean, replace=1). Details in §2c.
- **[High] F-2. The shipped f6 row cannot fail.** Its rename out-and-back never changes the earliest `--diff-filter=A` commit, and the fixture has no omitted round commit, so exit 0 is correct for that fixture. The `log.follow` cutoff fault is real. A redesigned fixture reproduces it: frozen exit 0 clean with cutoff 1000, where the correct verdict is exit 1. Details in §2f.
- **[Medium] F-3. The grid misses one real frozen execution channel.** Repo-local `log.showSignature=true` runs the configured `gpg.program` during `git log`. Frozen creates the marker; the candidate blocks it (`-c log.showSignature=false`). Details in §2F7.
- **[Medium] F-4. The candidate adds a partial-clone preflight refusal beyond the stated direction.** Any `remote.<name>.promisor`, `extensions.partialclone`, or `.promisor` pack now yields exit 2 before a verdict, even when no command would run. The real lane and fleet have none of these (read-only check), so current audits are unaffected. It is a policy choice that needs explicit sign-off. Details in §4.3.
- **[Medium] F-5. Probe reporting hides crashes and fixture failures.** Frozen crashes exit 1, the same code as a `failed` verdict; only stderr shows the traceback. The probe suppresses JSON-parse errors (`2>/dev/null`, probe.sh:30), has no rc checks (`set -u` only, probe.sh:3), and masks a failed commit at probe.sh:51.
- **[Low] F-6. The f5 extension line is unnecessary, and f5 has no non-executing control.** `remote.origin.promisor=true` alone triggers the lazy fetch on git 2.56.0. Add a `core.sshCommand=false` control; frozen exit 1, no marker.
- **[Low] F-7. Candidate isolation list is partly unmeasured.** `log.showRoot=true` and `log.mailmap=false` have no rows. `core.quotePath=true` was removed between the two snapshots; its effect was not measured either way.
- **[Info] F-8. An in-lane grid already exists.** `tests/report-audit/repo-state-grid.py` pins identity (lines 46-47), asserts the replace is effective (239-240) and a promisor pack is observed (211). `tests/report-audit/isolation-mutants.py` has 23 mutants. I grepped both but did not review or run them. I recommend that grid supersede probe.sh; probe.sh should not be cited as evidence in its current form.

Confirmed sound as shipped: control, f1 (crash), f2 (crash), f4 (false clean), f5 (execution, verdict correct).

## 1. Re-run of probe.sh against the frozen blob
Command: `AUDIT=/tmp/kama-r23-probe/frozen-audit.py bash /tmp/kama-r23-probe/probe.sh`. Run once; output in `/tmp/kama-r23-probe/run.Fvm6/`.

| case | exit | evidence | soundness |
|---|---|---|---|
| control | 0 | clean, required 1, cutoff 2000 | sound |
| f1-logenc | 1 | traceback, `UnicodeDecodeError` 0xe9 | sound fault (crash) |
| f2-report-bytes | 1 | traceback, `UnicodeDecodeError` 0xff | sound fault (crash) |
| f3-replace-omit | 1 | `landed-omitted` 4312b0…, required 2, **no replace ref** | **fixture bug** (F-1) |
| f4-replace-fake | 0 | clean, replace ref present | sound (false clean) |
| f5-lazyfetch | 1 | `unresolved-full-hash` abcdef… ×2, **marker created** | sound (execution) |
| f6-follow | 0 | clean, cutoff 2000, required 1 | **not a reproduction** (F-2) |

The same probe against candidate `79d9e124…` (`/tmp/kama-r23-probe/run.5027/`, once): control 0; f1 0; f2 2 (`output is not UTF-8`); f3 1 (replace still absent); f4 1; f5 2 (`partial clone (extensions.partialclone)`, no marker); f6 0.

## 2. Per-claim soundness

**(a) f1, sound.** `i18n.logOutputEncoding` is repo-local (probe.sh:39). The frozen `git()` (frozen-audit.py:87-97) decodes with `text=True`, so byte 0xe9 raises. This is an auditor defect, not a fixture artifact.

**(b) f2, sound.** Invalid bytes committed in the fleet report (probe.sh:41) reach the same decode site. The candidate returns exit 2 `output is not UTF-8`, a typed refusal.

**(c) f3, unsound as shipped; the claim is real.**
- probe.sh:43 runs `git commit-tree` with no identity. probe.sh:6 sets `GIT_CONFIG_GLOBAL=/dev/null`; `mk()` (probe.sh:7-9) sets no `user.*`; `cm()` (probe.sh:10-18) sets identity only for `commit`.
- Without `-e` or rc checks, `Y` is empty and `git replace "$X" ""` fails silently.
- Observed stderr in my re-run: `fatal: unable to auto-detect email address (got 'vgpnk@plazir27.(none)')` and `error: failed to resolve '' as a valid ref`.
- Identity probe: `env -i … git commit-tree` → rc 128, "unable to auto-detect email address". With `EMAIL` set alone → rc 128, "empty ident name".
- Of the five probe output directories, only `run.xpxV` has a replace ref (`4312b0…`; log `unrelated|round-1: work`; exit 0 clean). This matches the L1 observation. `run.Fvm6`, `run.Ihdu`, `run.uCZq`, `run.m2TW` have no replace ref and exit 1.
- Pinned fixture (`probe-fixed.sh` f3-replace-omit): frozen exit 0 clean, replace=1, so the claim reproduces. Candidate: exit 1 `landed-omitted`.

**(d) f4, sound.** The replace ref is present in every f4 run. Mechanism: `printf FAKE | git cat-file --batch-check` with the ref returns `FAKE commit 140`; with `--no-replace-objects` it returns `FAKE missing`. The auditor's `lookup` accepts the requested oid with the replacement's type, so the fabricated citation counts as found. A paired control was added (same report, no ref): exit 1 `unresolved-full-hash` on frozen and on candidate.

**(e) f5, sound.** The marker comes from the auditor run, because the commands after the promisor config (probe.sh:48) touch only the fleet repo, which has no promisor config. The verdict stays correct. The `extensions.partialClone` line (probe.sh:47) is not needed. Experiment `/tmp/kama-r23/RevProbeScript/promisor-noext` (git 2.56.0): plain `cat-file --batch-check` with only `remote.origin.promisor=true` creates the marker; with `--no-lazy-fetch` there is no marker.

**(f) f6, unsound (cannot fail).**
- The fleet `.git/config` has `log.follow=true` (probe.sh:51; observed in `run.Fvm6/f6/fleet`).
- History: `2000 round-1: report` (A), `2200 mv` (R096), `3000 back` (R100).
- Cutoff is the oldest `--diff-filter=A` commit time. With follow the list is `2000`; with `-c log.follow=false` it is `3000`, `2000`. The cutoff is 2000 either way.
- Probe.sh:51 also contains a silent no-op `git commit -q -m mv 2>/dev/null`.
- Redesigned fixture (`probe-fixed.sh` `f6()`): draft `old/k.md` at t=1000, renamed into place at t=2000, omitted round commit at t=1500.
  - frozen, unset: cutoff 2000, exit 1 `landed-omitted` (correct).
  - frozen, `log.follow=true`: cutoff 1000, exit 0 clean (**false clean**).
  - candidate, `log.follow=true`: cutoff 2000, exit 1 (fixed).

**F7, new row, not in the L1 grid: real frozen execution.** Repo-local `log.showSignature=true`, with `gpg.program` and `gpg.openpgp.program` pointing at a marker script, and one commit carrying a fake `gpgsig` header. Frozen: marker created, exit 0 clean. Candidate (`-c log.showSignature=false`, snapshot line 97): no marker, exit 0.

## 3. Corrected grid (`/tmp/kama-r23/RevProbeScript/probe-fixed.sh`, sha256 `492d1c42…`)
Identity is pinned, every fixture step is checked, replace and precondition assertions are in place, and paired controls are included. Each target was run once.

| case | frozen `4fe9339f` | candidate `79d9e124` / `68476410` |
|---|---|---|
| control | 0 clean | 0 clean |
| f1-logenc | 1 traceback | 0 clean |
| f1-round (inline experiment `f1round/`; non-ASCII round commit, omitted) | 1 traceback | 1 `landed-omitted` (79d9e1 only) |
| f2-report-bytes | 1 traceback | 2 `not UTF-8` |
| f3-control-no-replace | 1 `landed-omitted` | 1 |
| f3-replace-omit | **0 clean, replace=1** | 1 `landed-omitted` |
| f4-control-no-replace | 1 | 1 |
| f4-replace-fake | **0 clean, replace=1** | 1 `unresolved` |
| f5-control-ssh-false | 1 | 2 `partial clone` |
| f5-lazyfetch | 1, **marker** | 2 refusal, no marker |
| f6-follow-unset | 1 `landed-omitted`, cutoff 2000 | 1 |
| f6-follow-true | **0 clean, cutoff 1000** | 1 `landed-omitted`, cutoff 2000 |
| f7-showsignature | 0, **marker** | 0, no marker |

Candidate behavior matches the L1 claim on every fault row: each is either the correct verdict or a typed refusal, with no marker. Controls are unchanged, except that f5-control-ssh-false changes 1 → 2 because the candidate refuses promisor-configured repos (F-4).

## 4. Other observations
1. **Exit-code collision.** On frozen, a traceback exits 1, the same as a `failed` verdict. Classify crashes by stderr containing `Traceback`; the JSON-parse failure is hidden by `2>/dev/null`.
2. **Silent fixture failures.** `set -u` only (probe.sh:3) and no rc checks. The failed commit-tree (F-1) and the no-op commit (f6) both pass silently.
3. **Partial-clone refusal (candidate `68476410`, `current-snapshot-2.py:446-451`).** Refuses on a `.promisor` pack, `extensions.partialclone`, or any `remote.<name>.promisor`, with `could-not-evaluate: … partial clone (…)`. Exit 1 → 2 for promisor-configured repos even when no command could run. `--no-lazy-fetch` alone already blocks execution (promisor-noext), so the refusal is defense in depth and also a policy choice. Read-only checks on the real repos: `git config --get-regexp` finds none of `remote.*.promisor`, `extensions.partialclone`, `log.follow`, `log.showsignature`, `log.mailmap`, `i18n.logoutputencoding`, `core.sshcommand`; `.git/objects/pack` has no `*.promisor` file. Current audits are unaffected.
4. **Isolation list.** `current-snapshot-2.py:94-97`: `log.showRoot=true` and `log.mailmap=false` have no rows. `core.quotePath` was removed between snapshots. `log.showSignature` is now measured (F7).
5. **Surrogates.** `round_commits` decodes with `errors="surrogateescape"`. The subject feeds only `pat.match` and is never printed (grep), so I found no crash path there.
6. **Version claim.** The candidate docstring requires git ≥ 2.45. Only 2.56.0 is available here.

## 5. Residual risk and verification gaps
- Not run: selftest (50/50), historical rounds 10–22, errata paths.
- `repo-state-grid.py` and `isolation-mutants.py`: grepped only, not reviewed or run.
- git < 2.45 behavior of `--no-lazy-fetch` and `--no-replace-objects`: untested.
- `log.mailmap`, `log.showRoot`, and `core.quotePath` effects: no fixtures.
- Identity was pinned in my grid; behavior under a user's own identity was not run separately.
- Each run was a single execution; nothing was repeated to check for flakiness.
- No network I/O by design: lazy-fetch fixtures use `example.invalid`, with `core.sshCommand` set to `touch …; false` or `false`. Not traced with strace.

## 6. Tooling
None installed or updated. Used the existing git 2.56.0 and Python 3.14.8.

## 7. Files written
- `.ufo/waves/round-23/build/advice/RevProbeScript.md` (this report, new)
- `.ufo/waves/round-23/build/out/RevProbeScript/probe-fixed.sh` (copy of the corrected grid, optional artifact)
- `/tmp/kama-r23/RevProbeScript/`: `current-snapshot.py` (79d9e124…), `current-snapshot-2.py` (68476410…), `probe-fixed.sh`, `promisor-noext/`, `f1round/`, `id/`, `fixed.ApKP/` (frozen), `fixed.zy6k/` (79d9e1), `fixed.Raug/` (68476410)
- `/tmp/kama-r23-probe/frozen-audit.py` (frozen blob), `/tmp/kama-r23-probe/run.Fvm6/` (L1 probe vs frozen), `/tmp/kama-r23-probe/run.5027/` (L1 probe vs candidate)

No lane-tracked file, git index, or git config was written. Lane git reads used `GIT_OPTIONAL_LOCKS=0`.
