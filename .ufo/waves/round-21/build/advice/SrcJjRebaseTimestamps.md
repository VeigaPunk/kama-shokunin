VERDICT: partial - jj rebase re-stamps rebased commits' committer name, email and time (docs + run); jj git push re-stamps nothing (run, default config); C1's %ct cutoff is rebase-sensitive but flips 0 of 46 commits at a29bb84.

# SrcJjRebaseTimestamps — does jj rewrite committer timestamps? (round-21, kama scout)

Access date 2026-10-21 (`date -u +%F`, exit 0). Lane not modified; no jj command run in the lane.

## Sources opened
- **jj CLI reference**, https://docs.jj-vcs.dev/latest/cli-reference/ (fetched 2026-10-21; unversioned `latest`, page labelled "experimental"). Location: `## jj metaedit`, description paragraph 1, line 2200.
  Quote (18 words): "Whenever any metadata is updated, the committer name, email, and timestamp are also updated for all rebased commits."
  Same section: `--force-rewrite` (lines 2244-2246) "Even if this option is not passed, the committer name, email, and timestamp will be updated if other metadata is updated."; `--update-author-timestamp` (lines 2220-2222) "This updates the author date to the current time, without modifying the author."
- **Revision pin:** `/home/vgpnk/.local/bin/jj` = `jj 0.45.1-7c41cdeb…`, sha256 cd5efc3e…; `git ls-remote --tags https://github.com/jj-vcs/jj.git refs/tags/v0.45.1` gives 7c41cdeb16b6b321c64e789a966b6adf723816a5. Installed `jj metaedit --help` carries the same sentence (out/help-metaedit.txt lines 3-5). Captured in out/evidence.txt, all exit 0.
- **Config:** `jj config get git.sign-on-push` → `false` (exit 0). Config page §Automatically signing commits: push-time signing applies only when enabled.
- **Unreachable:** man.archlinux.org jj-rebase (ECONNRESET); docs.jj-vcs.dev/latest/cli/jj-rebase/ (HTTP 404). Lead, unopened (search snippet only): github.com/jj-vcs/jj/discussions/7691.

## Observed run
out/SrcJjRebaseTimestamps/probe.sh → probe.log (exit 0, 12.3 s). Isolated HOME/XDG/JJ_CONFIG; local bare remote; no network.
Run 1 (probe-run1-exact-revset-failed.log) used `description("x")`, an exact match in jj 0.45.1 because descriptions end in a newline. It matched nothing, so it is superseded and kept.

| step | command (exit) | observed |
|---|---|---|
| S0 | git init, describe, new x3 (0) | T0-T3 committer epoch 1792579955 = author |
| A | describe T0, parent unchanged (0): "Rebased 2 descendant commits." | T1, T2 new ids; committer 1792579957; author 1792579955 kept |
| CUT | CUT=1792579959 (stand-in for report commit) | T1, T2 ct <= CUT (pre) |
| B | `--config user.name=kama-probe-rebaser` rebase -s T1 -d T3 (0): "Rebased 2 commits to destination." | T1, T2 committer becomes kama-probe-rebaser, epoch 1792579961 (post); author name and epoch kept |
| C | identical rebase (0): "Skipped ... already in place." "Nothing changed." | no id change (control) |
| D | bookmark create feat; `git push --bookmark feat` (0) | local = remote 501b95b96753; committer epoch 1792579961 unchanged |

Observed: rebase, including auto-rebase of descendants, re-stamps committer name, email and time. Author name and time are kept. A no-op rebase rewrites nothing. Push at default config rewrites no ids or timestamps.

## Bearing on C1 (landed-omitted cutoff)
- Audit at a29bb84 (`tools/report-landing-audit.py`; copy at out/audit-a29bb84.py): author filter `%an` (l.92); commit time `%ct` (l.86); cutoff = `%ct` of the fleet commit adding the report (l.98); `pre = ctime <= cutoff` (l.121); `"required": len(pre)` (l.141).
- A lane commit authored before a report but rebased after it moves from pre to post and leaves `required`: a silent false negative. `%an` and `%at` survive a jj rebase (observed).
- Sensitivity, my read-only check, not an official audit run: out/cutoff_check.py → cutoff_check.out.txt (exit 0). 66 kama commits at a29bb84; 15 with committer epoch != author epoch. Rounds 10-20: 46 round/checkpoint commits checked; pre/post flips `%ct` vs `%at`: 0; uncited commits hidden: 0. The lane has `.jj`; the fleet root does not (observed).
- Reading: the cutoff is rebase-sensitive in principle. At a29bb84 it flips nothing, so the raw C1 counts are unchanged by this issue. [INFERENCE] A later jj rebase of an older lane commit after its report would hide it silently.
- Advice (L1 decides; [INFERENCE]): key lane-commit time on `%at` or on ancestry. Any change needs its own gate.
- C2: no bearing (install identity hashes file bytes and link text, not timestamps).

## Draft SOURCES row (insert directly after S065; S066 unused)
`| S066 | jj (Jujutsu) CLI reference, jj metaedit — https://docs.jj-vcs.dev/latest/cli-reference/ | docs | A | jj rewrite rule for committer name, email and timestamp of rebased commits; not author fields, not git rebase | §`## jj metaedit`, description paragraph 1 (fetched line 2200); same sentence in installed jj 0.45.1 `jj metaedit --help` (tag v0.45.1 = 7c41cdeb16b6b321c64e789a966b6adf723816a5); page unversioned `latest` | A rebase re-stamps each rebased commit's committer name, email and timestamp, so any committer-date cutoff is not stable across a jj rebase. | queued | 2026-10-21 | on-release | — |`

Validation (python census, exit 0) on a scratch copy of corpus/SOURCES.md@a29bb84 plus this row: 66 rows; 0 malformed (NF != 13); 0 duplicate ids; 0 tier/status/kind/inflation violations; 0 missing used-by paths.
- Status `queued`: opened, and no knowledge entry or lesson cites it. Flip to `mined` once a used-by path cites it.
- Gate fields: URL above; access 2026-10-21; quote 18 words at `## jj metaedit` ¶1.
- Tier A caveat: the page says it "does not match the `jj help` output exactly". A rests on the sentence appearing verbatim in the installed binary's own help.

## Installs/updates
None by this seat. Used existing jj 0.45.1 (~/.local/bin/jj). No pacman use. Scratch /tmp/kama-r21-SrcJjRebaseTimestamps deleted before yield.

## Not executed / [INFERENCE]
- `git.sign-on-push = true` (documented: signs at push, would change ids) not run.
- Lane's own jj config and op log not inspected (no jj run in the lane).
- Attribution of the 15 re-stamped lane commits to jj rewrites vs git amend: not established.

Artifacts (out/SrcJjRebaseTimestamps/): probe.sh, probe.log, probe-run1-exact-revset-failed.log, cutoff_check.py, cutoff_check.out.txt, evidence.txt, help-metaedit.txt, audit-a29bb84.py.
