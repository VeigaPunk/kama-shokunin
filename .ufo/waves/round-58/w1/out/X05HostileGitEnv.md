# X05 — hostile git environment vs the C1 checker and counter (round 58)

Axis: operability (C1). Advisory leaf: findings only, no production file touched, no commit. Tip measured: `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`. Tools read as committed blobs and hash-checked:
`tools/round58-c1-counter.py` sha256 `32f615d8…4b9`, `tools/round58-battery-exec-check.py` sha256 `89ad4e5d…ec5`;
both equal to the worktree copies, so nothing under test drifted from the frozen bytes.
Attacks: the C1 predicate sentence in `controls/freeze.txt`, the counter `tools/round58-c1-counter.py`,
the checker `tools/round58-battery-exec-check.py`. Receipts: `.ufo/waves/round-58/w1/out/X05HostileGitEnv/`.

## Hostile environment built (scratch, now removed)
Decoy repo `$S/decoy` (own `git init`, toplevel asserted, `HEAD=4534ea6` decoy batteries/prereg, wrong roster).
`$H/gitconfig` + `$H/home/.gitconfig`: `user.name=HOSTILE-CONFIG-USER`, `commit.gpgsign=true`,
`gpg.program=$H/bin/gpg-marker.sh`, `core.fsmonitor=$H/bin/fsmonitor-marker.sh`, `core.hooksPath`,
`core.autocrlf=input`, `init.defaultBranch=hostilebranch`, `alias.show`, `safe.directory=*`; marker scripts
append to `$H/markers/`. Every hostile run: `env -i PATH=/usr/bin:/bin TMPDIR=$S PYTHONDONTWRITEBYTECODE=1 …`.

## Result — result unchanged, committed bytes read
| # | command (counter unless noted) | env added | exit | compared to base |
|---|---|---|---|---|
| base | `python3 committed/counter.py --repo LANE --tip TIP --checker-blob TIP:…exec-check.py` | clean `HOME=$S/cleanhome` | 0 | `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True` |
| A | same | `GIT_DIR=$S/decoy/.git GIT_WORK_TREE=$S/decoy GIT_CONFIG_GLOBAL=$H/gitconfig HOME=$H/home` | 0 | `diff` empty; stderr empty |
| B | same | A + `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_COUNT/KEY_0/VALUE_0=commit.gpgsign`, `GIT_CONFIG_PARAMETERS`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE=hostile`, `GIT_CEILING_DIRECTORIES`, `GIT_TRACE2_EVENT=$H/markers/trace2.json` | 0 | `diff` empty; no `trace2.json` written |
| C | same | `HOME=$S/does-not-exist GIT_CONFIG_GLOBAL=$H/gitconfig` | 0 | `diff` empty |
| D | same | `HOME=$S/hostile/ro-home` (mode 0500) | 0 | `diff` empty |
| E | `committed/checker.py --repo LANE --tip TIP` direct | clean | 0 | `present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True` |
| F | same | A | 0 | `diff` empty vs E |
| G | same, cwd inside `$S/decoy` | A + B extras | 0 | `diff` empty vs E |
| I | counter | `XDG_CONFIG_HOME=$H/xdg` (hostile `git/config`) | 0 | `diff` empty |
| J | counter `--repo $FX` | A + hostile **local** `core.fsmonitor/gpgsign/gpg.program/autocrlf` in the measured repo | 0 | `diff` empty vs fixture run |

`ls -A $H/markers` is empty after A–J (no fsmonitor/gpg/hook/trace2 marker): the hostile config was never read.

Committed bytes are what is read (object-vs-worktree test): fixture repo `$FX` built by `git init` in scratch from
the 20 tip blobs; python tree compare: `fixture_paths=20 identical_blobs=20 blob_mismatch=[] variant_blobs_identical=15/15`.
Counter vs `$FX` under env A: exit 0, `met=True`. Worktree then overwritten in place (`WORKTREE GARBAGE`, 20 dirty
files, battery file no longer source), rerun under A: exit 0, `diff` empty — the counters never touch the worktree.

## Why this is not a vacuous pass — leak simulation (the scrub is what saves them)
`leaksim/counter-leak.py` and `leaksim/checker-leak.py` differ from the frozen tools only in `genv()`/`clean_env()`
(scrubbing removed, `return dict(os.environ)`); clean-env run is `diff`-identical to base (copy is faithful).
Under the same hostile env the scrubbing-free copies fail, so each channel is live:
- `GIT_DIR=decoy` → `could-not-evaluate: invalid tip`, exit 2 (counter L1 and checker L4).
- `GIT_CONFIG_GLOBAL` alone → `could-not-evaluate: fixture commit failed`, exit 2 (L2).
- `HOME` alone (no GIT_CONFIG_GLOBAL) → `could-not-evaluate: fixture commit failed`, exit 2 (L3);
  markers `fsmonitor-run`×12, `gpg-run`×2, `hook`×2 recorded.
A non-scrubbing process under the same env also resolves `rev-parse --show-toplevel` to `$S/decoy` and reads
`commit.gpgsign=true` / `user.name` / XDG config, and a hostile-config commit dies with `gpg failed to sign the data`.

## Limits (reported, not predicate changes; no C1 credit claimed)
1. `HOME` is not scrubbed by either tool; safety rests entirely on the two overrides `GIT_CONFIG_GLOBAL=os.devnull`
   and `GIT_CONFIG_NOSYSTEM=1`. L3 shows `HOME` alone is sufficient to break an unscrubbed run, so this is one
   override of margin, not defence in depth. `XDG_CONFIG_HOME` is neutralised only by the same override (I: potent
   when unopposed — `git config --get commit.gpgsign` → `true` — harmless under the counter).
2. Not on the assigned axis, probed for completeness: `PYTHONPATH=$H/pyshadow` (shadowing `json.py`) → exit 1,
   `RuntimeError: hostile-json-shadow`; `PATH` with a shadowing `git` wrapper → exit 2, `invalid tip`. Both fail
   loudly (never a silent wrong verdict), and neither is scrubbed by the tools.
3. Scope: C2 counter not exercised by this seat; the lane working tree is dirty (`.ufo/waves/round-56/measured/*.out`
   modified, `.ufo/scopes/` untracked) but nothing the C1 path reads, and test H2/H3 prove the tools ignore the worktree.

Tooling: none installed (pacman not run). Scratch `/fast/scratch/hyaku/kama-r58/X05HostileGitEnv` removed after the
receipts above were copied out.
