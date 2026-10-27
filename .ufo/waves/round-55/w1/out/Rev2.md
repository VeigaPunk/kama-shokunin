# Rev2 — Sen4Fixture coverage: `clean_env` audit of both frozen counters at 9c60eae6

**Verdict: the `GIT_*` strip is complete and verified end to end (every git call in both counters goes through a helper that passes `-C` and a `GIT_*`-free environment; a full `GIT_DIR` + `GIT_CONFIG_COUNT/core.hooksPath` + `GIT_CONFIG_PARAMETERS` + `GIT_INDEX_FILE` poison changes neither receipt, mutates no foreign repo, and runs no hook) — but `clean_env` is *not* hermetic: the inherited `XDG_CONFIG_HOME`/`HOME` global attribute file reaches `git archive`, which C1 never validates against the commit, and a single `* export-ignore` line there (or in the audited tree's own `.gitattributes`) turns the C1 counter into a Python traceback with exit 1 and no receipt.** One HIGH-class defect (D1) with a verified fix; nothing wrong found in C2's fixture env.

Measured 2026-10-27 10:53–11:05 UTC on host `7.2.11-arch1-1`, counters at the frozen bytes
`tools/round54-replay-code-audit.py` sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`
and `tools/round54-cited-path-check.py` sha256 `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`
= the preregistration's `counter_sha256` values, identical in the worktree (8abadfed) and at
`9c60eae6` (evidence/01). `--repo` was my own `git clone --shared` of the lane
(`/fast/scratch/hyaku/kama-r55/w1/Rev2/lane`, toplevel asserted). Nothing in the lane or the fleet was
written; the counters were never edited in place — the patches below live only in this out dir and were
run from there.

---

## 1. Is every git call wrapped? (yes, both counters — measured, not read)

The wrapper census is a PATH shim (`$S/bin/git`: append `"$*"` to `$GITLOG`, `exec /usr/bin/git "$@"`);
no tracer was used. A clean run of each counter produced the complete call list.

| counter | git calls in a clean run | outside the helper | `cwd=` on git | `shell=True` | calls without `-C` |
|---|---|---|---|---|---|
| C1 `round54-replay-code-audit.py` | **4** | 0 | 0 | 0 | 0 |
| C2 `round54-cited-path-check.py` | **384** | 0 | 0 | 0 | 0 |

C1 (evidence/02) — the whole list, `--tip 9c60eae6`:

```
-C …/lane rev-parse --verify 9c60eae6…^{commit}
-C …/lane archive --format=tar 9c60eae6…
-C …/lane show 9c60eae6…:corpus/SOURCES.md
-C …/lane show 3a600d2f…:corpus/SOURCES.md
```

C2 (evidence/03): 263 calls with `-C <fixture D>`, 97 with `-C <lane>`, 24 with `-C <fleet>`;
subcommands `show 274, ls-tree 28, rev-parse 28, add 21, commit 21, cat-file 7, log 3, init 1, rm 1`.
Every one of them is the helper `git()` (`:207-212`) or the fixture's local `g()` (`:684`), and every
`g()` call site is inside `fixture()` (`:673-815`).

Static cross-check on the frozen bytes (no other spawn path exists):

- C1: `subprocess.run` only at `:176` (`git()`); the single `subprocess.Popen` at `:641` launches the
  replay, not git; `INVOKER` at `:155` only re-execs `sys.executable`. `tools/kama-live-replay.py`
  contains **0** occurrences of `git` and `tools/kama-llamacpp-live.py` has none as a command.
- C2: `subprocess.run` only at `:208` (`git()`) and `:684` (fixture `g()`).
- Neither counter uses `os.system`, `shell=True`, `os.popen`, or `os.chdir`.

The two env regimes are different by design and both are sound for their scope:

- `git()` (both counters), `:163-180` / `:198-212`: blacklist — `os.environ` minus `GIT_*`, then
  `extra` applied **after** the strip (`clean_env({"GIT_CONFIG_COUNT":"1"})` keeps it; evidence/12).
  No call site passes a stripped channel back in; C2's fixture passes only `GIT_CONFIG_GLOBAL`,
  `GIT_CONFIG_NOSYSTEM` and the four identity variables.
- C1's replay chain `prepare_env()`/`start_replay()` (`:613-643`): whitelist —
  `PASS_ENV = ("PATH","LANG", proxies…)` plus scratch-local `HOME`, `XDG_CACHE_HOME`, `TMPDIR`,
  `PYTHONPATH`. No `GIT_*`, no `LD_*` reaches the replay or the live child, which is stronger than
  the strip; the census confirms the replay spawns no git anyway.

## 2. The C1 Archive downloads (no git — checked)

`ARCHIVE_URL`/`MODEL_URL` are fetched with `urllib.request.build_opener(urllib.request.ProxyHandler({}))`
at `:904-921`, i.e. proxies from the environment are *ignored*, and both bodies are hashed against the
frozen digests (`ARCHIVE_SHA` `bf94332a…`, `MODEL_SHA` `270cba1b…`) before use; the archive bytes are
held in memory (`Archive(apath)`, `:920-921`) and never re-read from disk. No git, no `git lfs`, no
credential helper, no config lookup participates. A hostile `https_proxy` cannot reach these two
requests (it *is* passed to the replay via `PASS_ENV`, but the replay's own download is digested too).

## 3. C2's fixture env, and why `GIT_CONFIG_GLOBAL=os.devnull` is safe

`fixture()` builds one env (`:678-680`) and uses it for every `g()`:

```
clean_env({GIT_AUTHOR_NAME/EMAIL, GIT_COMMITTER_NAME/EMAIL, GIT_CONFIG_GLOBAL: os.devnull,
           GIT_CONFIG_NOSYSTEM: "1"})
```

Why that is safe, in order of what it closes:

1. `clean_env` already removed every inherited `GIT_*`, including `GIT_CONFIG_COUNT/KEY_n/VALUE_n` and
   `GIT_CONFIG_PARAMETERS` (that is the round-53 F2 channel); measured dropped-list in evidence/12.
2. `GIT_CONFIG_GLOBAL=/dev/null` is set **after** the strip, so it survives and replaces the global
   config file that would otherwise be read from `$XDG_CONFIG_HOME/git/config` or `$HOME/.gitconfig`
   — both inherited, neither a `GIT_*` name.
3. `GIT_CONFIG_NOSYSTEM=1` removes `/etc/gitconfig` (absent on this host anyway).
4. The repo is a fresh `git init`, so before its first commit there is no repo-local config to carry
   `core.hooksPath`.
5. The `:701-702` guard checks both `--show-toplevel` **and** `--absolute-git-dir` against `D`, so the
   `-C` + `GIT_DIR` mismatch that defeated round 53 now fails closed.

The devnull is load-bearing, not decoration (evidence/16): the *same* hostile `HOME` that C2 ignores
makes a plain `git init` install an **executable** `pre-commit` from `init.templateDir`, and that hook
fires on the next commit (`TMPL-HOOK-RAN: PRESENT`). Under the counter, with that same `HOME`, the
receipt is body-identical and no marker appears (`GIT_CONFIG_GLOBAL=/dev/null` + `NOSYSTEM=1` block
`init.templateDir` as well as `core.hooksPath`) — evidence/11.

End-to-end falsifiers for the C2 write path (evidence/10):

```
$ GIT_DIR=$S/decoy/.git GIT_INDEX_FILE=$S/idx GIT_NAMESPACE=fx \
  GIT_ALTERNATE_OBJECT_DIRECTORIES=$S/decoy/.git/objects GIT_CEILING_DIRECTORIES=$S \
  GIT_DISCOVERY_ACROSS_FILESYSTEM=1 GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath \
  GIT_CONFIG_VALUE_0=$S/hooks GIT_CONFIG_PARAMETERS="'core.hooksPath=$S/hooks'" GIT_CONFIG_NOSYSTEM=0 \
  python3 tools/round54-cited-path-check.py --repo $S/lane --tip 9c60eae6… --scratch $S/e2
fixture=1 lane=1 scenarios=15/15 … met=True        exit=0     (identical body to the clean run)
decoy after: HEAD=35490115… commits=1 status=0      hook marker: absent   index file: absent
```

## 4. Every inherited channel that could still redirect a git call

`clean_env` = "drop `GIT_*`". Measured keep/drop sets (evidence/12). The `GIT_*` set is genuinely
closed; these survive:

| channel | survives strip | reaches | measured effect |
|---|---|---|---|
| `HOME` | yes | global config (`~/.gitconfig`) and, when `XDG_CONFIG_HOME` is unset, `~/.config/git/attributes` | `[core] attributesFile=…` or that attributes file changes `git archive` (33348 → **0** entries) → C1 crash |
| `XDG_CONFIG_HOME` | yes | `$XDG/git/config` (incl. `core.attributesFile`, `core.hooksPath`, `init.templateDir`) and `$XDG/git/attributes` | `* export-ignore` there → archive **0** entries → C1 crash; a hostile `HOME` alone is inert while XDG is set (evidence/14) |
| `PATH` | yes | which `git` binary runs | shim logged all 384 C2 / 4 C1 calls; a substituted `git` fabricates every receipt field |
| `LD_PRELOAD`, `LD_AUDIT`, `LD_LIBRARY_PATH` | yes | the git process itself | a constructor .so loaded in **405** `git` processes during one C2 run (evidence/13) |
| `PAGER` | yes | pager | inert here (`capture_output=True` = pipe, no tty, no `--paginate`) |
| `TMPDIR` | yes | `S = mkdtemp(dir=--scratch or tempfile.gettempdir())` (C1 `:886-888`) | only without `--scratch`; `mkdtemp` is mode 0700 |
| `/etc/gitconfig` (system config) | n/a (file, not env) | all git calls; C2's fixture disables it, C1 does not | absent on this host; not modifiable by me, so untested |
| `--repo`'s own `.git/config` and `.git/info/attributes` | n/a (not inherited) | its reads/archives | auditor-controlled inputs, not ambient env |
| `GIT_*` (all, incl. `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`, `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_NAMESPACE`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CEILING_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_PREFIX`, `GIT_OBJECT_DIRECTORY`, `GIT_ATTR_NOSYSTEM`, `GIT_CONFIG_GLOBAL/NOSYSTEM`) | **no** | — | dropped, verified by dump and by the poison runs |

C2's *read* vocabulary (`show`, `ls-tree -z`, `log -z`, `cat-file`, `rev-parse`) is in practice
config-insensitive for this repository: `-z` disables path quoting, the tree has no non-ASCII paths,
the tip has no signed commits (`%G? = NNN`), no `$Format` placeholders exist in the three receipts, so
`log.showSignature`/`core.quotePath`/`export-subst` have nothing to act on today. C1 has no such
margin because it archives.

## 5. D1 — HIGH (measurement attribution): C1's archived tree is unvalidated; the inherited attribute file (or the tree's own `.gitattributes`) crashes the counter

**Source.** `tools/round54-replay-code-audit.py:892`

```python
arc = git(a.repo, "archive", "--format=tar", tip).stdout      # no -c, no attribute neutralisation
```

`:898` `tarfile.open(fileobj=io.BytesIO(arc))` — no `try/except`; the result is extracted and replayed.
The counter contains **no** `ls-tree`, `cat-file`, `hash-object` or `read-tree` (grep: none), so nothing
compares the archive with the commit it claims to measure. `clean_env` cannot help: the channel is the
global *attribute file*, not a `GIT_*` variable.

**Reproduced, two independent ways.**

```
$ HOME=$S/empty-home XDG_CONFIG_HOME=$S/attr3-xdg python3 tools/round54-replay-code-audit.py \
    --repo $S/lane --tip 9c60eae6… --scratch $S/c1e --out $S/c1e.out
Traceback (most recent call last):
  … File "…/round54-replay-code-audit.py", line 898, in main
    with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
tarfile.ReadError: file could not be opened successfully: … - method tar: ReadError('end of file header')
exit=1     receipt: none
```

(`$S/attr3-xdg/git/attributes` = one line `* export-ignore`; same result with
`HOME=<dir>/.gitconfig` `[core] attributesFile=<file with that line>` — evidence/06, /07.)

And with no environment poison at all, only a committed `.gitattributes` in my clone (fixture commit
`dd47b97d`, `* export-ignore`): archive = 0 entries, frozen counter = same traceback, exit 1, no receipt
(evidence/08). The patch below turns that into `could-not-evaluate: the archived tree is unreadable: …`,
exit 2.

**Impact.** Fail-closed, so no false pass: the receipt is never written. But (a) the verdict is decided
by ambient state instead of the tree, and it silently degrades from "measured" to "crashed"; (b) exit 1
is exactly the code the frozen target/kill-rule uses for "prints `met=False` … with its named leg
failing", so a crashed battery or base-control receipt can be read as a legitimate kill by anything
that checks only the exit code; (c) the second form means the counter does not establish its own
disposition ("the replay of the receipts at `--tip`") — an in-tree `.gitattributes` is a lane
self-mutation the counter cannot see. Not a claim falsification: `met=True` was never printed in any
poisoned run.

**Proposed fix** (`c1-fix.diff`, 69 lines, applies to the frozen bytes with `patch -p1 --dry-run`; full
patched text `round54-replay-code-audit.patched.py`):

1. `clean_env` adds `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1` and
   pops `LD_PRELOAD`/`LD_AUDIT`/`LD_LIBRARY_PATH` (extras still win, so the C2 fixture style is
   preserved).
2. `git archive` runs with `-c core.attributesFile=/dev/null` — this is the load-bearing part: it
   replaces the *global* attribute file (which is an XDG/HOME file, unreachable by any `GIT_*` strip).
   Measured: XDG poison 0 → 33348 entries.
3. After extraction, the file list must contain every `100644`/`100755` path of
   `git ls-tree -r -z --full-tree tip` (the lane has 8 `120000` symlinks that `git archive` omits, so
   the check must filter by mode), else `could-not-evaluate … exit 2`.
4. The five files the legs actually use (`tools/kama-live-replay.py`, `corpus/SOURCES.md`, the three
   receipts) are byte-compared with `git show tip:<path>`, else `could-not-evaluate … exit 2` — this
   also covers `export-subst`/eol transforms that keep the file list intact.
5. `tarfile.open` is wrapped: `TarError` → `could-not-evaluate: the archived tree is unreadable: …`,
   exit 2 (no traceback, no exit 1).

**Verified** (evidence/15):

| run | result |
|---|---|
| patched, clean | `bind=1 … met=True` **exit 0** |
| patched, `XDG_CONFIG_HOME` with `* export-ignore` (crashed the frozen counter) | `bind=1 … met=True` **exit 0** |
| patched, in-tree `.gitattributes` fixture `dd47b97d` | `could-not-evaluate: the archived tree is unreadable: …` **exit 2**, no receipt |
| `c2-hardening.diff` (same `clean_env` hardening; no demonstrated defect in C2's reads) | receipt **body-identical** to the frozen run, `15/15 … met=True`, exit 0 |

## 6. What is sound — checked so the lane does not over-correct

- The frozen `GIT_*` strip closes the round-53 F1/F2/F3/F4 channels in **both** counters: full poison
  runs left the decoy repo at 1 commit/clean, ran no `core.hooksPath` hook, wrote no `GIT_INDEX_FILE`,
  and produced byte-identical C2 receipts and an unchanged C1 `met=True` (evidence/05, /10).
- C2's fixture cannot be redirected or made to execute from config: template-dir and hooks-path
  injection are blocked by `GIT_CONFIG_GLOBAL=/dev/null` + `GIT_CONFIG_NOSYSTEM=1`, and the
  `--absolute-git-dir` guard covers `-C`/`GIT_DIR` disagreement (evidence/11, /16).
- C1's replay chain is a whitelist, so `GIT_*` and `LD_*` never reach the replay or the live child; the
  `PATH` channel remains only for the counter's own four calls.
- C1's independent clean run reproduces the frozen measurement exactly: same summary line, same 22
  detail lines, `--tip 9c60eae6`, 16.8 s, exit 0.

## 7. D2 — LOW (reproducibility): the C2 receipt stamps a moving fleet revision

`--fleet-rev` defaults to `HEAD` (`:823`). My clean runs stamped `fleet=4dd6935e…` and `fleet=666bc1e…
while the frozen `measured/c2-build.out` and `controls/base.c2.out` stamped `fleet=6c4aba34…` — all
three with the same verdict and counts. The receipt's fleet revision is therefore a function of when it
ran, and fleet-root citations are resolved at that moving tree ("in the fleet tree at `--fleet-rev`").
Verdict-stable in the three samples I have, but a verifier re-running the frozen counting command gets a
different `fleet=` line and a different fleet tree; pinning `--fleet-rev 6c4aba34…` in the
preregistration's counting command would make the measurement reproducible.

## 8. Confidence

- D1: **high** — three independent reproductions (two environment forms, one in-tree form), exit codes
  and absence of a receipt recorded, and a fix that is verified both to close the environment channel
  and to fail closed on the in-tree one.
- "Every git call is wrapped, `-C`-only, and `GIT_*`-clean": **high** — call census (384 / 4 calls, none
  outside the helpers) plus a full poison run in each counter.
- "C2's fixture env is safe": **high** for config-driven hooks/templates/redirection; **medium** for
  `PATH`/`LD_*` (proved present and open, not turned into a false pass — a substituted git binary is
  outside any env strip).
- Channel list: **high** for env names (dump + poison), **medium** for `PAGER`/`TMPDIR` (reasoned from
  `capture_output`/`mkdtemp`, not adversarially exercised), **untested** for `/etc/gitconfig` (absent).

## Files

- `evidence/01-counter-bytes.txt` … `evidence/16-template-hook-potency.txt` — raw commands and outputs
  quoted above.
- `receipts/` — `c1a.out` (C1 clean), `c1b.out` (C1 under `GIT_*` poison), `e1.out`/`e2.out`/`e3.out`
  (C2 clean / `GIT_*` poison / hostile `HOME`), `q1.out`/`q2.out`/`p3.out` (patched C1 clean, patched C1
  under XDG poison, patched C2).
- `c1-fix.diff`, `c2-hardening.diff`, `round54-replay-code-audit.patched.py`,
  `round54-cited-path-check.patched.py` — proposed fixes, never applied to the lane.

Tooling: nothing installed (a throwaway `.so` was compiled with the host `cc` inside my scratch and
deleted). No llama-server of mine is left running: `pgrep -af llama-server` shows only seat
J5EnvNames' `kama-r48-live` pair, untouched; the servers my runs started were torn down by the
counters' own teardown leg (three runs, `alive []`). Scratch `/fast/scratch/hyaku/kama-r55/w1/Rev2`
removed after the evidence and receipts were copied out.
