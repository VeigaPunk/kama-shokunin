# Sec1 — hermetic-environment review of both round-55 counters

**Verdict: no inherited channel lets a lane-user-environment attacker execute code through either
counter (all three git call sites run under `clean_env`, `shell=True`/`os.system` appear nowhere, and
the replay runs under an 8-name allowlist with the server on a 5-name allowlist) — but the counters are
not hermetic in the config sense the freeze claims: `clean_env()` strips only `GIT_*`, so inherited
`HOME`/`XDG_CONFIG_HOME` still reach every git call (proven: a malformed `~/.gitconfig` turns C2 into
`exit 2 could-not-evaluate` with the attacker path echoed in the verdict line, and
`[i18n] logOutputEncoding=utf-16` crashes the `moved` branch into a traceback with `exit 1` and **no
receipt file**). The two-line fix is already in the tree — C2's own fixture sets exactly it.**

Review target: both counters at `9c60eae6f7ed84f7da93d219a406aadc30958c6c`; `git diff 9c60eae6 HEAD --
tools/` is empty, so the measured tree's counters are the frozen ones. Host: git 2.56.0, Python 3.14.8.
Lane tip at review time was `8abadfed` (the w1 build commit); the stated freeze commit is present and one
commit past base `3a600d2f`, as claimed.

---

## 1. Subprocess inventory (each call site, and its environment)

| site | what runs | env | verdict |
|---|---|---|---|
| `tools/round54-replay-code-audit.py:176` | `git -C <repo> <plumbing>` | `clean_env()` | under `clean_env` ✔ |
| `tools/round54-cited-path-check.py:208` | `git -C <repo> <plumbing>` | `clean_env()` | under `clean_env` ✔ |
| `tools/round54-cited-path-check.py:684` | `git -C <fixture> <cmd>` | `clean_env({…, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1})` | under `clean_env` + config closed ✔ |
| `tools/round54-replay-code-audit.py:641` | replay invoker (`python -I -c INVOKER`, not git) | `prepare_env()` allowlist | see §3 |

`grep -n 'subprocess'` on both counters returns exactly these (plus `TimeoutExpired` at C1:724 and the
`INVOKER` string at C1:155–156). `grep -n 'shell=True\|os.system\|os.popen\|pty\.'` on both counters:
`NONE`. No git call escapes the helper, and the replay (`tools/kama-live-replay.py`) contains no `"git"`
invocation at all (`grep -n '"git"'` → no hit in the replay), so the git surface is fully covered by
`clean_env`.

---

## 2. F1 — [MEDIUM, calibration] `clean_env()` strips `GIT_*` only; inherited user config still reaches git

**Defect lines.** `tools/round54-replay-code-audit.py:170` and `tools/round54-cited-path-check.py:202`:

```python
env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
```

Git's user-scope config search is **not** driven by `GIT_*`: it reads `$HOME/.gitconfig` and
`$XDG_CONFIG_HOME/git/config`. Both variables are inherited by every product git call, so the freeze's
stated invariant ("every git call runs with inherited `GIT_*` stripped", C1:164–169, C2:199–201) does not
hold for config redirection. The counter's own fixture already knows the closure
(`round54-cited-path-check.py:679–680`: `GIT_CONFIG_GLOBAL: os.devnull, GIT_CONFIG_NOSYSTEM: "1"`), so the
asymmetry between the fixture path and the product path is the defect signature.

**Exploit path (attacker controls the lane user's environment, not the repo).** Set `HOME` to a directory
with a hostile config, then run the counter normally.

**Evidence 1 — the config is read (probe against the frozen helper, `clean_env()` verbatim):**

```
$ python3 probe1.py     # imports the frozen C1 module, calls its own m.git()/m.clean_env()
clean_env keeps HOME: '/fast/scratch/.../evilhome'
git archive rc=0 bytes=10240 stderr=b''
$ python3 probe2.py
1 config read through inherited HOME: rc=0 out=b'attacker'
1b config read through inherited XDG_CONFIG_HOME: rc=0 out=b'xdgattacker'
D hostile safe.directory readable=b'*'
```

**Evidence 2 — live denial lever on the real counter (`exit 2`, attacker path echoed):**

```
$ HOME=$S/h-bad python3 tools/round54-cited-path-check.py --repo $S/lane --tip 9c60eae… --scratch $S/sc-bad
EXIT=2
could-not-evaluate: git rev-parse --verify 9c60eae6f7ed84f7da93d219a406aadc30958c6c^{commit}:
fatal: bad config line 1 in file /fast/scratch/hyaku/kama-r55/w1/Sec1/h-bad/.gitconfig
```

A malformed inherited `~/.gitconfig` converts a **red base control (`exit 1`)** into `exit 2
could-not-evaluate` — the wave's control evidence is suppressible by ambient environment, and the receipt
line quotes the attacker-chosen path. C1 shares the helper, so the same lever applies before any git work.

**Evidence 3 — content primitive on a parsed git output (`i18n.logOutputEncoding`):**

```
$ python3 -c "…m.git(LANE,'log',BASE,'HEAD','-1','--format=%H','--',<path>)"
h-clean -> raw b'4229ea1b9a789148dded1f159c20' | decoded '4229ea1b9a789148dded1f159c20'
h-utf16 -> raw b'\xff\xfe4\x002\x00…'  → .decode() raises UnicodeDecodeError
```

`round54-cited-path-check.py:505` uses `git(… "log" … "--format=%H" …).stdout.decode()` (strict UTF-8), so
the config-controlled bytes decide whether a `moved` row can be validated at all. See F2 for the
consequence. Today the lane ledger has **no** `moved` row (`registry/cited-path-corrections.tsv` classes:
`never`×7, `upstream`×5, plus one each of `deleted/fixed/externalized/superseded/untracked`), which is why
the hostile-config run of the frozen counter is byte-identical to the clean one:

```
$ HOME=$S/h-clean  … --out $S/c2-clean.out  → EXIT=0  fixture=1 lane=1 scenarios=15/15 … met=True
$ HOME=$S/h-utf16  … --out $S/c2-utf16.out  → EXIT=0  fixture=1 lane=1 scenarios=15/15 … met=True
$ diff c2-clean.stdout c2-utf16.stdout && echo IDENTICAL
IDENTICAL
```

So the primitive is live **only** through the denial lever until a `moved` row exists; the class is part of
the frozen contract (`CLASSES`, C2:167) and is exercised by neither the ledger nor the fixture (F2).

**Impact.** Availability/integrity of the counter's *verdict*, not of the repository: an attacker cannot
forge a green (no config key on this command set makes a red row pass — `dropped`/`bad`/`stale` all read
blobs and object existence, which config cannot fabricate), but can force `exit 2`, and can crash the
process into `exit 1` with no receipt. Both are "evidence unavailable" outcomes that look like measurement
results to a runner that only reads `met=` / exit status.

**Smallest remediation** (verified, §6): close the user-scope config search in the shared helper.

```diff
     env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
+    env["GIT_CONFIG_GLOBAL"] = os.devnull      # HOME/.gitconfig and XDG_CONFIG_HOME/git/config
+    env["GIT_CONFIG_NOSYSTEM"] = "1"           # /etc/gitconfig
     env.update(extra or {})
     return env
```

Applied to both helpers in `fix-clean_env.diff` (identical hunk, C1:170, C2:202). A second belt would be
`env["HOME"] = <scratch>` / dropping `XDG_CONFIG_HOME`; the two `GIT_CONFIG_*` lines are sufficient
because `GIT_CONFIG_GLOBAL` replaces the whole global scope, `GIT_CONFIG_NOSYSTEM` the system scope, and
the repo-local config (owned by the clone) is legitimately read. The fixture's `extra` still wins because
`env.update(extra)` runs last.

---

## 3. F2 — [LOW, calibration/operability] the `moved` branch crashes into `exit 1` with no receipt

`round54-cited-path-check.py:505` is the only strict `.decode()` on git output in either counter, and
`main()` catches only `EvalError` (`round54-cited-path-check.py:841–843`). Any `UnicodeDecodeError`
therefore escapes: traceback, interpreter exit status **1**, `--out` never written, scratch
`shutil.rmtree` still runs (verified — the mkdtemp below `--scratch` is removed, only the empty operator
`--scratch` root remains).

Demonstrated end-to-end on my clone (one extra `moved` row added there for the probe; nothing in the lane
was touched):

```
# repo-local i18n.logOutputEncoding=utf-16 (what a hostile $HOME/.gitconfig achieves globally)
EXIT_A=1
  File ".../round54-cited-path-check.py", line 512, in check_row
    last = git(lane.path, "log", BASE, lane.rev, "-1", "--format=%H", "--", e).stdout.decode().strip()
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
$ ls c2-moved-a.out → No such file or directory          # no receipt

# same tree, no encoding override
EXIT_B=1
fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=0 met=False
detail: bad ledger line 47 (SCORECARD.md `…/utils.hpp` moved): blob … at its last commit != blob … at tip
```

(line 512 in my patched clone = line 505 frozen; the patch adds 7 lines.)

**Two defects for the price of one:** (a) a crash is indistinguishable from "not met" by exit status and
leaves *no* receipt, so a wave runner records a verdict it did not obtain; (b) the frozen 15 scenarios
cover neither `moved` (`C2:501–513`) nor `untracked` (`C2:574–580`) — both are in `CLASSES` (C2:167) — so
the counter's own fixture cannot catch this class at all.

**Smallest remediation** (report-only, counters are frozen): in the `moved` branch, treat an undecodable or
non-SHA log line as a row defect instead of an exception, e.g.
`raw = git(...).stdout.decode("utf-8", "replace").strip()` then
`if not re.fullmatch(r"[0-9a-f]{40}", raw): return "moved: no readable last commit for " + e`; and add a
16th fixture scenario for a true `moved` row plus an `untracked` one. Optionally widen `main()`'s handler to
`except (EvalError, UnicodeDecodeError)` → `return 2`, since a crash is "could not evaluate", never "not
met".

---

## 4. F3 — [LOW] the envnames leg detects two names, not the class it documents

`round54-replay-code-audit.py:146` `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")`, enforced at
`env_leg` (C1:429–442) which records **names only** (values are never read — good). `LD_AUDIT`,
`LD_LIBRARY_PATH`, `LD_DEBUG`, `GLIBC_TUNABLES` would be *recorded, not rejected*. The battery's own
`c1/battery/m-ldaudit-foreign.out` confirms this is the intended reading: `met=True` with `envnames b1: 6
environment variable names recorded` — an extra name is tolerated.

The reason this is not exploitable is upstream of the counter: the replay builds the server environment
from an allowlist, `tools/kama-live-replay.py:128` `LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")`
plus `TMPDIR` — exactly the **5** names every frozen receipt records. No `LD_*` can enter through the
counter's own `PASS_ENV`. Note for calibration: if a future replay adds any `LD_*` key, this leg will not
flag it; the detector's docstring ("a code-injection variable is present") is broader than its list.

---

## 5. F4 — [LOW, process cleanup] the counter's death does not tear down its process tree

`start_replay` spawns the invoker with `start_new_session=True` and **no** `preexec_fn`
(`round54-replay-code-audit.py:641`); the replay binds *itself* to the invoker
(`kama-live-replay.py:140–146`, called at `:945`). So the chain only holds for invoker → replay → live →
server. A SIGKILLed/OOM-killed counter leaves invoker, replay and llama-server running; `reap()`
(C1:662–676) is in-process and dies with the counter. Reproduced with the counter's own `INVOKER` string
and the replay's own `set_own_pdeathsig()`, no service started:

```
counter-stand-in pid 84731, invoker 84807, replay-stand-in 84886
after SIGKILL of the counter: invoker alive=True child alive=True
after SIGTERM of the invoker: invoker alive=False child alive=False
```

Smallest remediation: `preexec_fn=lambda: prctl(PR_SET_PDEATHSIG, SIGTERM)` on the invoker Popen (same
helper the replay uses), or set `PR_SET_PDEATHSIG` in the `INVOKER` one-liner itself.

---

## 6. Environment classification (children only)

### 6a. `clean_env()` — every git call (C1:176, C2:208, C2:684)

| inherited | risk | note |
|---|---|---|
| `HOME` | **MEDIUM** | user config read on every call → F1 (denial, latent content flip) |
| `XDG_CONFIG_HOME` | **MEDIUM** | same channel, proven (`probe2` 1b) |
| `PATH` | LOW-inherent | `["git", …]` resolves through it; unavoidable for any tool, but it is the one exec-relevant name; not closed by this review |
| `SSL_CERT_FILE` / `SSL_CERT_DIR` | LOW | honoured by `ssl.create_default_context` in the counter's own `urlopen`; cannot forge the frozen digests |
| proxies (`http_proxy`, `https_proxy`, `no_proxy`, any case) | LOW for C1 parent / **MEDIUM** for C2 | C1's downloads use `ProxyHandler({})` (C1:904, 917; also the loopback witness client at C1:319) → proxies ignored; **C2's upstream fetch uses bare `build_opener()` (C2:298) → proxies honoured**. Both fetch paths are digest-gated (see 6c) |
| `TMPDIR`, locale, `PAGER`, rest | LOW | no exec, no parsed output |
| `GIT_*` | — stripped | ✔ (the freeze's claim) |

### 6b. `prepare_env()` — the replay tree (C1:613–631, `PASS_ENV` at C1:154)

| var | risk | note |
|---|---|---|
| `PATH` | LOW residual | the replay's exec surface is `sys.executable` (absolute) and `sys.executable -I <live>` (`kama-live-replay.py:500–518`); the server is exec'd from a sealed memfd (`--server-fd`). No bare-name lookup anywhere in the replay → inert today, the one name that becomes live if the replay ever runs `["tar"/"git"/…]` |
| `LANG` | LOW | the replay parses JSON and exit codes, not localized text |
| `http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY` | MEDIUM (availability/privacy) | the replay's `fetch()` uses `urllib.request.urlopen` with **no** `ProxyHandler` (`kama-live-replay.py:170–182`), so the ~75 MB model/archive downloads go through the operator's proxy; no CA-bundle variable is in `PASS_ENV`, so TLS still uses the system store and the pinned digests (`--model-sha256`, `--server-asset-sha256`) still decide |
| `NO_PROXY` / `no_proxy` | LOW | narrows the above |
| replaced/planted: `HOME`, `XDG_CACHE_HOME`, `TMPDIR` → under `S`; `KAMA_R51_CANARY`; `PYTHONPATH` → canary dir | — | ✔ `-I` on both replay invocations makes the planted `PYTHONPATH` inert for the replay itself; it is a tripwire for any non-`-I` python the server might spawn |

Not passed at all: `LD_*`, `SSL_CERT_*`, `GIT_*`, `PYTHONHOME`, `REQUESTS_*`, `CURL_*` — correct.

### 6c. Integration/integrity cross-check (why the proxy channel is not an integrity break)

Both counters verify externally supplied bytes against frozen digests: C1 `ARCHIVE_SHA` constant at
C1:132 compared at C1:921, `MODEL_SHA` at C1:128 compared at C1:907, `SERVER_SHA` at C1:124 compared on
the running image at C1:608 and on the announced exe at C1:399; C2 compares upstream bytes to
`UPSTREAM_DIGESTS`/`UPSTREAM_COMMIT` (C2:173–186). A hostile proxy or a hostile trusted CA can force
`exit 2` (unavailable) but cannot produce a matching digest for different bytes. **No false pass was found
through any environment channel.**

---

## 7. Scratch, temp and receipt-write surface

| item | evidence | assessment |
|---|---|---|
| counter scratch | C1:887 `mkdtemp(prefix="r53c1-", dir=root)`, C2:831 `r53c2-`, fixture C2:677 `r54c2-fx-` | 0700, unpredictable suffix, removed in `finally` (verified empty after every run, including the crash run) |
| `--scratch` root | C1:886 / C2:830 `os.makedirs(root, exist_ok=True)` | left in place by design (operator dir); default umask 755 |
| fixture paths | C2:691–692 `makedirs(dirname, exist_ok=True)` + `open(full,"w")` on fixed relative names inside a 0700 mkdtemp | no traversal possible from the scenario table |
| archive extraction | C1:899–900 `filter=lambda m,dest: None if (m.issym() or m.islnk()) else tarfile.data_filter(m,dest)` | symlink/hardlink members refused, then `data_filter` (no absolute/`..`) |
| `prepare_env` dirs | C1:618 `makedirs(..., exist_ok=True)`; C1:623 `makedirs(cdir)` **without** `exist_ok` | fails closed on a pre-existing path; all under the 0700 `S` |
| receipt write | C1:964 / C2:854 `open(a.out, "w")`, parent `makedirs(..., exist_ok=True)` | the only write outside mkdtemp: **follows symlinks, no `O_NOFOLLOW`/`O_EXCL`**. Operator-chosen path, so informational — but in this wave many seats write under one `out/` tree, so a pre-planted symlink at a receipt path would be followed. Hardening: `os.open(path, O_WRONLY|O_CREAT|O_TRUNC|O_NOFOLLOW, 0o644)` |
| log handles | C1:638 `open(S/tag.log,"wb")`, closed in `finally` (C1:812, 858) | ✔ |

No predictable scratch path, no `/tmp` fallback in the wave harness (I passed `--scratch` everywhere), no
symlink following on the mkdtemp side.

---

## 8. Probed and **negative** (so this review is calibratable, not just a list of worries)

All probes call the frozen counter's own helper with `HOME` pointed at a hostile dir, git 2.56.0:

| candidate channel | result |
|---|---|
| `[alias] log/show/archive/rev-parse/ls-tree/cat-file = !cmd` | builtins win (rc 0 / usage 129), marker never created |
| `[tar "tar"] command` / `[tar "tar.gz"] command` | config is read (`config --get` returns it) but `git archive --format=tar` uses the builtin writer: no exec |
| `[log] showSignature=true` + `[gpg] program = …` | no exec, output unchanged (`--format=%H` suppresses it) |
| `core.pager` / `pager.log` under `capture_output` | no exec (no tty) |
| `diff.external`, `diff.<drv>.textconv` on `log --name-only` / `show rev:path` | no exec, output unchanged |
| `core.fsmonitor`, `core.hooksPath` on rev-parse/show/ls-tree/cat-file/archive | no exec (no index refresh, no hook-triggering command) |
| `color.ui=always`, `core.quotePath=false` on `log -z --name-only` | output unchanged (`-z` disables quoting/colouring) |
| `i18n.logOutputEncoding` on `ls-tree -z` / `log -z --name-only` | paths unchanged (only `--format=%H` output is re-encoded → F2) |

---

## 9. Fix verification (in my own clone only)

`fix-clean_env.diff` (both helpers, one hunk each) applied to `$S/lane` and committed there with a fixture
identity (`fx <fx@invalid>`), toplevel asserted equal to `$S/lane` before the commit:

```
$ HOME=$S/h-bad    python3 $S/lane/tools/round54-cited-path-check.py --repo $S/lane --tip 2f1d02b0…  → EXIT=0  met=True
$ HOME=$S/h-utf16  … same tip                                                    → EXIT=0  met=True
$ HOME=$S/h-utf16 (additionally [core] hooksPath + [alias] log = !echo pwned)     → EXIT=0  met=True
$ HOME=$S/h-clean  python3 $S/lane/tools/round54-replay-code-audit.py --repo $S/lane --tip 2f1d02b0…
  EXIT=0  bind=1 sealed=1 code=1 teardown=1 newrow=1 … met=True   (newrow: 2 rows new, 1 names S511)
  detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
```

The `exit 2` lever is closed, C1/C2 verdicts are unchanged, `git archive` still reconstructs the tree
under the closed config (`code`/`newrow` legs green), and teardown is clean.

---

## 10. Hygiene

- Lane, fleet repo, `shokuknow`, sibling lanes: read-only. No write, commit, fetch or jj command in the
  lane. The only commits are in my own `git clone --shared` clone (fixture identity, toplevel asserted).
- Two llama-server processes belonging to another seat (`/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/…`,
  pids 3521908, 3523374) were running throughout; I did not touch them. My own counter runs left **zero**
  servers (`pgrep -af llama-server | grep $S` → 0; the only other pids are the J5EnvNames pair).
- No tracer, no `pacman`, no tool installation, no service started by hand.
- `$S` removed at the end; the receipts below were copied out first.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/fix-clean_env.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c1-hostile.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c1-patched.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-clean.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-utf16.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-bad.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-patched-bad.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-moved-a.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c2-moved-b.stdout`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/probe1.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/probe2.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/probe3.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/p4.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/demo_orphan.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/c_standin.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sec1/child_replay.py`
