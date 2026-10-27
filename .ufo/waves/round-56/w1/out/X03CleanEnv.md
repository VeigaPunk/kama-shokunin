# X03CleanEnv — hostile git-config environment vs. the round-56 C2 gate

Seat: round-56 w1, leaf executor. Assignment: set hostile `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_NOSYSTEM` in a scratch environment and verify that
`tools/round56-prereg-check.py` still reads committed bytes.

Result: **PASS — the C2 counter is not steerable by git-config environment hostility.**
Under every hostile combination the gate produced byte-identical receipts and the frozen
exits (base `present=0 met=False` exit 1; freeze `present=1 roster_match=1 kills=1
controls=2 met=True` exit 0). Committed-blob binding was confirmed independently against a
tampered working tree. One residual, out-of-vector weakness is reported in §7 (PATH
substitution); it does not touch the frozen kill rule.

## 1. Axes

| Axis | Frozen | This seat's measurement |
|---|---|---|
| operability | 8 -> 8 (C1) | untouched; no changes to counter, battery or targets |
| calibration | 7 -> 7 (C2) | C2 gate survives hostile git config: same output, same exit, same committed blobs |

No score change is claimed or implied. This seat neither edits nor re-scores anything.

## 2. Scope and identity

- Lane `kama-shokunin` treated as read-only; all experiments ran against a single
  `git clone --shared` of the lane at the freeze tip in scratch
  `/fast/scratch/hyaku/kama-r56/X03CleanEnv/work/lane-clone` (`TMPDIR` set to
  `/fast/scratch/hyaku/kama-r56/X03CleanEnv/tmp`). The lane itself was additionally invoked
  read-only (`git -C <lane> show …`) for parity runs.
- Freeze tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`; base tip
  `e10b6d39af450e8d652be9ac2986768b531fe13f`.
- `tools/round56-prereg-check.py` sha256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`
  — both the working-tree file and the committed blob at the freeze tip match the frozen
  digest.
- Environment: `git version 2.56.0`, `Python 3.14.8`, Linux 7.2.11-arch1-1 x86_64.
- Evidence bundle: `out/X03CleanEnv/probe-log.txt`, `out/X03CleanEnv/receipts/`,
  `out/X03CleanEnv/fixtures/`. Scratch was deleted after copying.

The counter's own sanitization (lines 17–25 of the tool):

```python
def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=clean_env())
```

## 3. Hostile fixtures (scratch only)

| Fixture | Content | Naive `git` result |
|---|---|---|
| `h-syntax.cfg` | `[broken` | `fatal: bad config line 1 …` exit 128 (rev-parse and show) |
| `h-badbool.cfg` | `[core] bare = maybe` | `fatal: bad boolean config value 'maybe' for 'core.bare'` exit 128 |
| `h-incdir.cfg` | `[include] path = <scratch dir>` | `warning: unable to access … Is a directory` + `fatal: bad config line 2` exit 128 |
| `fakehome/.gitconfig` | `[core] bare = maybe` | HOME-only hostile global config: exit 128 |
| `xdg/git/config` | `[core] bare = maybe` | XDG-only hostile global config: exit 128 |
| env `GIT_DIR=/nonexistent` | — | exit 128 |
| env `GIT_CONFIG_SYSTEM=h-syntax.cfg GIT_CONFIG_NOSYSTEM=0` | — | exit 128 |
| env `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.bare GIT_CONFIG_VALUE_0=maybe` | env-injected config | `fatal: bad boolean config value 'maybe' for 'core.bare'` exit 128; stripped by the tool (`receipts/env-injection-probe.txt`) |

Important calibration note: a **missing** `include.path` is *not* hostile on git 2.56 — it
only warns and exits 0. Hostility therefore requires a config parse error or a bad boolean,
which is what the fixtures above use. Earlier "hostile" fixtures built on a missing include
were discarded for that reason.

Exact commands and outputs: `probe-log.txt` §A and `receipts/naive-*.err`.

## 4. Gate runs (25 invocations; 24 with the real git binary)

Invocation shape (`<repo>` = scratch clone or the lane; `<envs>` per mode):

```
env <envs> python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-prereg-check.py \
    --repo <repo> --tip <tip> --out receipts/<name>.out
```

Matrix: both repos (scratch clone, lane) x both tips x four modes — `clean`,
`hostile-syntax`, `hostile-badbool` (+ hostile HOME + `GIT_CONFIG_COUNT` injection),
`hostile-incdir` — i.e. 16 runs; plus `combined-hostile` (`HOME`, `XDG_CONFIG_HOME`,
`GIT_DIR`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_CONFIG_GLOBAL`,
`GIT_CONFIG_NOSYSTEM=0`) and `hostile-system` (`GIT_CONFIG_SYSTEM=h-syntax.cfg`) at both
tips on the clone (4 runs); plus the tampered-worktree run (1); plus `hostile-inject`
(`GIT_CONFIG_COUNT` -> `core.bare=maybe`) at both tips on the lane (2); plus one extra
real-PATH base run (1). That is 24 real-git receipts; the 25th is the PATH-shim forgery
from §7.

Every real-git run at the base tip produced, exit 1:

```
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
```

Every real-git run at the freeze tip produced, exit 0:

```
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
```

Receipt digests collapse to exactly two values across all real-git modes and both repos:

```
860ad630ebe98cbdbb69166f1a67802cac148d33ad791031b05705413bfc6e5d  every real-git base receipt
01d95f526ed731b1fe0c4fd3aa72457d27662d261736d31d8e3eb88f1dd9ae1c  every real-git freeze receipt
```

The only base-tip receipt with the freeze digest is the PATH-shim forgery (§7), which is
labelled as such in `probe-log.txt` §F.

## 5. What the tool actually hands to git

A scratch `git` shim on `PATH` captured the child environment. With hostile
`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=0`, `HOME`, `GIT_CONFIG_COUNT`, `GIT_DIR` and
`GIT_WORK_TREE` all set, the child received exactly:

```
argv: -C <clone> rev-parse --verify efc6b3ec…^{commit}
GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1
HOME=<scratch fakehome>
```

No `GIT_DIR`, `GIT_WORK_TREE`, `GIT_OBJECT_DIRECTORY`, `GIT_CONFIG_SYSTEM` or
`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_*` reached git. Every `GIT_*` variable is stripped, then the
two config anchors are forced. `GIT_CONFIG_GLOBAL=/dev/null` also supersedes `~/.gitconfig`
and `$XDG_CONFIG_HOME/git/config`, which is why the hostile HOME/XDG fixtures are inert.

(`ghost-child-env.txt` in `fixtures/`; the shim was used only to observe the child env and
returned 128.)

## 6. Committed-bytes binding

In the scratch clone only, the working tree was tampered at the freeze checkout:

- `tools/round56-env-leg-battery.py`: `base-old-counter` and `round56-counter` both changed
  `control`/`positive-control` -> `kill`, so a disk read yields 3 kills / 0 controls;
- `.ufo/waves/round-56/preregistration.json`: `base-old-counter` changed `control` -> `kill`,
  so a disk read yields 2 kills / 1 control and a roster mismatch.

Naive disk reads see the tamper (`probe-log.txt` §D, `git diff` shown there). The gate at the
committed freeze tip, with hostile `GIT_CONFIG_GLOBAL` + `GIT_CONFIG_NOSYSTEM=0` + hostile
HOME, still printed `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0, and its
receipt was byte-identical to the untampered freeze run (`cmp` = identical,
sha256 `01d95f52…`). The counter reads `git show <tip>:<path>` blobs (lines 39–40), never the
worktree.

Independent instrument (`git cat-file blob`, no `git show`, no Python AST reuse of the tool)
at the freeze tip:

```
prereg_blob_sha256=fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68
battery_blob_sha256=79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c
roster_equal=1
kills=1
controls=2
```

(`receipts/independent-blob-anchor.txt`, produced by `anchor.py` reading committed blobs only.)

## 7. Residual finding (out of the assigned vector, advisory)

`clean_env()` strips and pins git configuration but keeps `PATH`, and `git()` invokes bare
`"git"`. A hostile `PATH` entry can therefore substitute the binary and forge the verdict
entirely. Demonstrated in scratch with a shim that answers `rev-parse` with the freeze tip and
`show` with a self-consistent 3-entry roster (1 kill, 2 controls), while the true tip is the
base commit where the files are absent:

```
PATH=<scratch>/spoof-bin:$PATH python3 tools/round56-prereg-check.py --repo <clone> --tip e10b6d39…
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Real `PATH`, same tip: `present=0 … met=False`, exit 1. This requires the caller to run the
gate with an attacker-controlled `PATH`; the fleet invocation does not, and the C2 kill rule
(roster/predicate fidelity) is untouched, so no claim is falsified. Proposed hardening for a
later round (does not change this counter now): resolve the binary once, e.g.
`GIT = "/usr/bin/git"` or `shutil.which("git")` with an assertion that the resolved path is
under `/usr/bin`, and keep the resolved value for both calls.

Other checks that did **not** reveal defects:

- `GIT_CONFIG_NOSYSTEM=0` alone, and hostile system configs, are neutralized by the forced
  `GIT_CONFIG_NOSYSTEM=1`.
- `--out` receipts contain only the gate's own deterministic text; hostile stderr never
  leaks into them.
- Non-fatal config settings (pager, `url.*.insteadOf`, include of a missing file) cannot
  alter blob reads in the first place, so the parse-error/bad-boolean fixtures are the real
  adversarial cases — and both are defeated.

## 8. Lane integrity and hygiene

- Lane `HEAD` still `efc6b3ec…`; no tracked lane file was written by this seat. Scoped
  `git --no-optional-locks status` shows only pre-existing untracked round-56 wave files.
- One early read-only `git status --porcelain` in the lane may have refreshed index stat
  cache only; no add/commit/reset, no jj command, no lane mutation, no fixture inside the
  lane.
- `measured/` was not touched; battery/`measured` writes belong to other seats.
- Scratch removed after evidence copy. No tool installs (git and python3 already present; no
  package manager was invoked).

## 9. Proposed defect list

1. Advisory (not this round's kill rule): harden `git()` against `PATH` substitution as in
   §7. Verification for a future round: with a hostile `PATH` shim the gate must fail closed
   (`could-not-evaluate`, non-zero) instead of printing `met=True`.

## 10. Tooling

No tools installed or upgraded; no package manager invoked (git 2.56.0 and Python 3.14.8
were already present).

Report: .ufo/waves/round-56/w1/out/X03CleanEnv.md
