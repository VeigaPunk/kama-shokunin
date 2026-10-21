# CritRefusalScope — partially

**Scoped result:** trusted-state compatibility is falsified: four clean local fixtures accepted by frozen are refused by current. The narrow C1 promise (no exit-1 traceback, execution, timeout or verdict flip) is **not** falsified by an intentional exit-2 refusal. This is advice for the canonical judge, not an admission or score decision.

## Axes

- Declared axis 7 / calibration: distinguish an unevaluable repository from a clean, fully local repository.
- Compatibility/no-harm: retain clean verdicts for legitimate repository layouts and inert configuration.
- Safety constraints: preserve refusal of genuinely shallow/partial/grafted states; do not trade safe refusal for implicit fetch or execution.

## Base and method

`git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/CritRefusalScope` followed by `git -C /tmp/kama-r23w2/CritRefusalScope rev-parse HEAD` returned exit 0 and `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Git reported `git version 2.56.0`.

Frozen script extracted with `git show 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`. Current script is the untouched cloned committed file.

Executed `python /tmp/kama-r23w2/CritRefusalScope/probe-refusal.py` (exit 0). It imports only the committed grid's fixture helpers, builds eleven fresh local lane/fleet pairs, and invokes each auditor as a subprocess with a 15-second timeout. Every fixture has a single `kama-shokunin` round-1 commit at author time 1000 and a committed fleet report at 2000 citing its full hash. No source registry or errata is required. Git fixture operations use `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and explicit identity. No network fixture was used.

Each arm command is:

`python SCRIPT --lane-repo LANE --fleet-repo FLEET --rounds 1 --no-errata --json`

The exact per-case commands, complete stdout, stderr and return codes are in `/tmp/kama-r23w2/CritRefusalScope/refusal-results.json`. Scratch fixture directories were automatically removed after capture; the harness recreates them.

## Strongest counterexample: explicit false is classified as true

Fixture delta: `git -C LANE config remote.origin.promisor false`. This is a fresh `git init` repository, not a partial clone; it has no remote URL, no promisor packs, and its required objects were created locally.

Observed:

- Frozen exit 0, clean JSON: `required_commits=1`, `defects=0`, `status=clean`.
- Current exit 2, empty stdout; stderr exactly:
  `could-not-evaluate: /tmp/kama-refusal-xdounj8u/lane: partial clone (remote.origin.promisor)`

Cause at `245a37f6`: `tools/report-landing-audit.py:445-448` enumerates configuration **names**, then refuses any matching `remote.*.promisor` without reading its boolean value. Setting the flag explicitly false is incorrectly treated as enabling it.

Upstream evidence: https://git-scm.com/docs/git-config#Documentation/git-config.txt-remote%E2%80%8Bname%E2%80%8Bpromisor — “When set to true, this remote will be used to fetch promisor objects.” (14 words).

**Smallest safe correction:** evaluate matching promisor settings with Git boolean semantics, permitting effective false while retaining refusal for effective true, malformed boolean values, actual promisor-pack markers and real partial-clone configuration. Add a clean false-valued control alongside the genuine partial-clone fault. This is fixable over-refusal, not a necessary consequence of T01: the fixture never was a partial clone.

## Additional scoped counterexamples

| Fixture delta | Frozen | Current | Anchor at 245a37f6 |
|---|---|---|---|
| Create zero-byte `.git/info/grafts` | exit 0; clean, one required commit, zero defects | exit 2; `.../.git/info/grafts rewrites history` | `tools/report-landing-audit.py:438-441` |
| Create `.git/info/grafts` containing only `# no grafts\n` | exit 0; same clean summary | exit 2; same false history-rewrite assertion | `tools/report-landing-audit.py:438-441` |
| Append harmless config subsection bytes `[branch "caf\xe9"]\n\tdescription = harmless\n` | exit 0; same clean summary | exit 2; strict UTF-8 decode failure in `git config --list --name-only` | `tools/report-landing-audit.py:445`, decoding at `:123-127` |

Exact stderr for the empty and comment-only files respectively:

- `could-not-evaluate: /tmp/kama-refusal-333c_dz5/lane: /tmp/kama-refusal-333c_dz5/lane/.git/info/grafts rewrites history`
- `could-not-evaluate: /tmp/kama-refusal-3aewefty/lane: /tmp/kama-refusal-3aewefty/lane/.git/info/grafts rewrites history`

Non-UTF-8 config stderr:

`could-not-evaluate: git config --list --name-only in /tmp/kama-refusal-p4epvas5/lane: output is not UTF-8: 'utf-8' codec can't decode byte 0xe9 in position 85: invalid continuation byte`

Empty/comment-only grafts contain no actual history substitution. However the documented refusal says “grafted,” and the implementation intentionally bans file presence; the judge may regard these two as conservative policy rather than reject the patch. Small correction, if compatibility is required: distinguish no-op content from effective graft records without weakening malformed/effective graft refusal or creating blocking-file reads.

The non-UTF-8 subsection is irrelevant to this audit's ASCII configuration-key checks and is accepted by Git and frozen. The new full configuration census introduces the refusal. Small correction: census using a representation that preserves arbitrary subsection bytes (e.g. surrogateescape or raw bytes), with safe delimiters. The current documentation expressly refuses non-UTF-8 git output, so accepting this tradeoff requires an explicit calibration decision; this finding does not claim a traceback or wrong success verdict.

## Controls that held

Both frozen and current exited 0 with clean JSON, one required commit and zero defects for all seven:

1. Plain repositories.
2. Bare lane clone.
3. Bare fleet clone.
4. Detached linked lane worktree (shared objects and refs).
5. Detached linked fleet worktree.
6. Both repos packed via `pack-refs --all`, `repack -ad`, and `commit-graph write --reachable`.
7. Sparse fleet checkout excluding report paths (`sparse-checkout set --no-cone /absent`); committed report still audited successfully.

Thus linked worktrees, bare repos, packed refs, commit-graphs and sparse fleet checkout did **not** produce a regression in this probe. Unrun cases are not passes.

## Limits and files written

Did not run the full grid, mutation suite, selftest, rounds 10–22 corpus comparison, submodule/reftable probes, multi-user ownership probes, actual partial clones, or Git versions other than 2.56.0. Did not invoke a judge/runtime, change implementation, commit, push, or install/update any tool.

Files written: this report; clone `/tmp/kama-r23w2/CritRefusalScope/` (Git-created clone files); `/tmp/kama-r23w2/CritRefusalScope-frozen.py`; `/tmp/kama-r23w2/CritRefusalScope/probe-refusal.py`; `/tmp/kama-r23w2/CritRefusalScope/refusal-results.json`; Python's imported-grid cache under the clone's `tests/report-audit/__pycache__/`; and temporary fixture trees `/tmp/kama-refusal-*/` (Git metadata/objects/config, lane `f`, fleet `.ufo/reports/round-1/kama.md`, bare clones/worktree metadata, graft markers as specified). Temporary fixture trees were removed by `TemporaryDirectory`. No lane tracked file, lane Git index, fleet root file, domain source, global configuration or secret was written.
