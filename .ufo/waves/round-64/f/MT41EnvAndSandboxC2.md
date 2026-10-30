# MT41EnvAndSandboxC2 — round 64 wave f — C2 environment / sandbox axis

Seat: mutation-tester. Lane: kama. Tip under test: `23b3fdb1a925129a9961cf551f6d40bf251602cb`
(C1 amendment 1b). C2 counter under test: `tools/round64-c2-counter.py`,
sha256 `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e` (byte-identical to the
freeze commit; verified before and after every mutant).

Scratch clone: `/fast/scratch/hyaku/kama-r64/f/MT41EnvAndSandboxC2/clone`
(`--shared` clone of the lane, checked out at the tip). Evidence:
`.ufo/waves/round-64/f/out/MT41EnvAndSandboxC2/`.
No lane file was edited; no lane commit was made; the real lane was never written.

## Verdicts (one line each, as printed by the counter)

```
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```

That is the pristine counter at the tip, in the operator's normal environment.

## F1 — SURVIVED: the verdict is caller-environment dependent (PYTHONPATH shadows a stdlib module the counter imports)

**The counter sanitises the environment it hands to the 12 bound commands, but not its own
interpreter environment.** The counter is launched as `python3 tools/round64-c2-counter.py`, so the
caller's `PYTHONPATH` sits on `sys.path` *before* the stdlib and shadows any stdlib module the
counter imports. The counter's own `clean_env()` (line 214) strips `GIT_*` only, and it is used for
the counter's git calls — not for the counter's own process.

Demonstration (`pypath-shadow-test.sh`, `pypath-shadow/subprocess.py`): a `subprocess.py` in the
caller's `PYTHONPATH` rewrites the git REF argument. The counter is asked to score the **base tip**
(`0c1eff3c…`, whose honest verdict is `met=False`, `controls/c2-base.txt`) but reads every byte
from the measured tip:

| case | counter one-liner (abridged) | exit |
|---|---|---|
| A. honest counter, base tip | `population=0 covered=0/12 pinned=12/13 … controls_rejected=0/120 errors=2 … met=False` | 1 |
| B. same base tip + `PYTHONPATH` shadow | `population=12 covered=12/12 pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 closure_ptr=1 tally_disclosed=8/8 controls_rejected=120/120 errors=0 … met=True` | **0** |
| C. control: same shadow, ref unchanged | `population=0 covered=0/12 … errors=2 … met=False` | 1 |

Case B is a **false pass**: the counter certifies the base tip as `met=True` with all 120 controls
"rejected", while the tree it actually scored is a different commit. Case C is the control that
proves the effect comes from the ref rewrite and not from the shadow breaking the counter.

Why this is a calibration (not operability) defect: the C2 predicate says the counter "trusts
nothing recorded and nothing it can check itself" and that the verdict is a function of the tip
bytes. The tip bytes are read through the caller's `PYTHONPATH`. The same hole exists for any
stdlib module the counter imports (`hashlib`, `json`, `re`, `subprocess`, `argparse`, `shutil`, …);
`hashlib` alone would forge every `pinned=13/13` check.

Field/control that decides: `pinned` (13/13 vs 12/13) and `population` (12 vs 0) — both computed
from bytes the caller controls. No declared control family covers this: the 120 controls all feed
*synthetic* records into the scoring functions; none runs the counter under a hostile interpreter
environment.

Honest scope: this is an *instrument* weakness, not a defect of the 12 bound tools or the registry.
Round-56 seat X03CleanEnv already found the `GIT_CONFIG_COUNT` variant of this class for an
earlier counter; the round-64 counter fixed the `GIT_*` half (`clean_env`) but not `PYTHONPATH`.

## F2 — SURVIVED: a planted regression can write through the overlay symlinks, out of `--work`, and the counter still prints met=True

The tip export carries **8 committed symlinks** whose targets are absolute paths in the real lane
(`git ls-tree -r 23b3fdb1` mode `120000`):

```
.ufo/waves/round-36/w3/out/MutRowPipe/probe/{.ufo,SCORECARD.md,SKILL.md,corpus/knowledge,corpus/lessons,registry,tests,tools}
   -> /home/vgpnk/Projects/shokunin/kama-shokunin/<same name>      (8 symlinks)
```

The counter runs the bound commands with `cwd = tree` — the tip export for the `tip` rows, and an
overlay whose top-level entries are symlinks *into* the tip export for the `reg`/`prn`/`dec` rows.
The export is extracted with `git archive | tar -x`, so these symlinks are materialised as real
symlinks inside `--work`. A bound command that writes a **relative** path therefore reaches through
them. Mechanism proof in scratch (`proof-writethrough.sh`): the file appears in the victim
directory, not in the tree it was written from.

End-to-end mutant (`symlink-escape-mutant.sh`, mutant **T3**): the committed symlink is re-pointed
at a scratch victim (the real lane is never written), and the **unpinned** tip file
`registry/capability-regress-r64.tsv` plants a one-line regression that writes
`.ufo/waves/round-36/w3/out/MutRowPipe/probe/tools/EVIL-WRITETHROUGH`.

```
tip=77376c6cb325 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 … met=True
  victim (outside --work): 1 entry   EVIL-WRITETHROUGH
  inside --work export:    0 entries
  inside the scratch clone: 0 entries
```

**SURVIVED** — the write escaped `--work` and the counter still reports `met=True` with
`controls_rejected=120/120`. The planted regression came from the *unpinned* regress table, so the
counter's `regress_flipped=12/12` is computed over a regression that escapes the sandbox. The
counter has no field that observes *where* a bound command wrote.

Two related mutants, same axis:

* **T2** (`registry/capability-regress-r64.tsv` plants a write to `registry/EVIL-WRITETHROUGH`,
  which lands in the tip export because the overlay's `registry` entry is a symlink into the export):
  `tip=d967ca46a35a … controls_rejected=120/120 errors=0 … met=True`, `EVIL-WRITETHROUGH in export: 1`
  → **SURVIVED**.
* **T1** (`tools/shortcut-tally.py`, the executed-but-**unpinned** tally reader, writes into the
  repo under judgment and into the export at run time):
  `tip=38373a7ebd42 … controls_rejected=120/120 errors=0 … met=True`,
  `lane_clone_tree changed=YES`, `EVIL-TALLY-IN-LANE-CLONE in clone: 1`,
  `EVIL-TALLY-IN-TIP-EXPORT in export: 1` → **SURVIVED**. Note `tools/shortcut-tally.py` is
  executed three times by the counter but appears in neither `PINS` nor `DEP_PINS`, so its bytes are
  unverified; the C2 predicate's "13 bound files" does not include it.

Whether the shipped (unmutated) tip's 12 bound tools would actually exploit this was not
demonstrated — none of them writes a relative path today (checked: no relative `open()`/`makedirs()`
in any of the 12). The defect is that the counter *cannot tell* if one did: there is no
write-observation control at all.

## F3 — SURVIVED (coverage): the counter's own environment/sandbox guards are not graded by its 120 controls

Mutants of the counter (committed in the scratch clone, run from the clone path against the committed
tool). Base mode = the operator's environment; hostile mode = `HTTP_PROXY`/`HTTPS_PROXY`/`http_proxy`/
`https_proxy`, `PYTHONPATH`, `PYTHONSTARTUP`, `GIT_DIR`, `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/
`GIT_CONFIG_VALUE_0`, `GIT_CONFIG_GLOBAL`, `GIT_ASKPASS`, `GIT_TERMINAL_PROMPT`, `LANG=C LC_ALL=C`.

| # | mutant (one-line change) | base | hostile | verdict |
|---|---|---|---|---|
| E1 | `Runner.env = dict(os.environ)` (the ENV_KEYS allowlist removed) | `met=True` | `mismatches=3 regress_flipped=9/12 printers_rejected=9/12 … met=False` | **SURVIVED** |
| E2 | overlay top-level symlinks point at the **lane clone** instead of the tip export | `met=True` | `met=True` | **SURVIVED** |
| E3 | bound commands' `TMPDIR` = `/tmp` (leaves `--work`) | `met=True` | `met=True` | **SURVIVED** |
| E4 | the counter's own scratch env `TMPDIR` = `/tmp` (leaves `--work`) | `met=True` | `met=True` | **SURVIVED** |
| E5 | `clean_env()` stops stripping `GIT_*` | `met=True` | `errors=1 met=False  (cannot resolve eb87f37ddc1b960aa2909aa2a3a02524f5ddc843)` | **SURVIVED** |

Reading: **none** of the five environment/sandbox mutants is caught by the counter's own 120-control
battery in the operator's environment; all five still print `met=True` with
`controls_rejected=120/120`. E1/E5 only flip under the *hostile* environment — i.e. the counter
detects them by accident of the hostile env breaking the run, not by any named control. E2, E3 and
E4 are invisible in **both** environments; E2 in particular lets a bound command read the lane
clone's working tree instead of the tip export and the counter certifies the tip anyway.

Field/control that decides: none. The declared families are
`canon=4/4, closure=5/5, flip=11/11, gate=16/16, idle=21/21, pattern=5/5, pins=5/5, printer=2/2,
reconciler=11/11, registry=17/17, regress=11/11, selftest=1/1, tally=8/8, work=3/3` — every one is
a scoring-function control fed synthetic records. **There is no environment family, no sandbox
family, and no write-observation family.** The C2 predicate's "executes live in an allowlisted
environment" and "Every scratch path is under `--work`" are asserted in prose and are not graded by
the instrument that certifies them.

## F4 — honest-run integrity (no defect): the counter as shipped writes nothing outside `--work` and nothing into the lane

Measured, not inferred:

* **Tree hashes, before/after** (`integrity.sh`): lane-clone worktree hash
  `ca4036c4f8bec9da991f9de2388c102a3d0e691939bfc30b062f1c0d738a58e1` → identical;
  `git status --porcelain` 0 lines before and after; `.git/index` sha256 identical
  (`781dbf0dbf9a11655537d6bbfa86a3d973c9d958991d8f28e3d721211d0495ab`); `show-ref` sha256 identical;
  `.git/objects` file count 1 → 1 (no object writes into the clone).
* **Tip export vs a fresh `git archive` of the same tip**: `diff -rq` → **0 differing lines**; the
  export is not mutated by the honest run.
* **`strace -f` over the whole run** (1.87 M syscalls, `trace-strace.log`): every write-shaped
  syscall outside `--work` was `/dev/null`, `/dev/nvidia*`, or the **creation** of the 8 committed
  symlinks above *inside the export* (the tar extraction of the tip). **Zero** writes to `/tmp`,
  `$HOME/.cache`, `$HOME/.local`, `$HOME/.config` or the real lane. `find $HOME /tmp -newer <stamp>`
  during the run returned only unrelated host activity (chromium cache, codex logs, wireplumber, a
  sibling seat's jj lock) — nothing attributable to the counter.
* No `__pycache__`/`.pyc` in the export: `PYTHONDONTWRITEBYTECODE=1` is honoured.

So the *shipped* instrument is clean; what is missing is any check that would *notice* if it were
not (F2/F3).

## F5 — environment battery on the pristine counter (the four required runs)

| caller environment | one-liner | exit |
|---|---|---|
| normal | `population=12 covered=12/12 … controls_rejected=120/120 errors=0 … met=True` | 0 |
| hostile (proxy + PYTHONPATH + PYTHONSTARTUP + GIT_DIR + GIT_CONFIG_COUNT + GIT_CONFIG_GLOBAL + GIT_ASKPASS + GIT_TERMINAL_PROMPT + `LANG=C LC_ALL=C`) | `population=12 covered=12/12 mismatches=0 pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 … controls_rejected=120/120 errors=0 … met=True` | 0 |
| `env -i` (empty env) | `errors=1 met=False  (internal FileNotFoundError: [Errno 2] No such file or directory: 'bash')` | 1 |
| `env -i PATH=/usr/bin:/bin HOME=$HOME` | `population=12 covered=12/12 mismatches=1 pinned=13/13 regress_flipped=11/12 printers_rejected=11/12 … controls_rejected=0/120 … met=False` | 1 |
| locale `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` | `population=12 covered=12/12 mismatches=0 … controls_rejected=120/120 errors=0 … met=True` | 0 |

Reading:

* The **hostile** environment does **not** change the verdict (the required property) — the
  counter's `ENV_KEYS` allowlist plus `clean_env()` do their job for the *variables named in the
  brief*; the benign hostile run is exactly byte-identical to the normal run.
* `env -i` fails **closed** (`errors=1 met=False`, exit 1): no false pass. But it is an *internal*
  error, not a declared refusal — `env -i` removes `bash`, which the counter needs for its
  `bash -c` run templates, so the counter raises `FileNotFoundError` instead of reporting "no
  environment".
* `env -i` + a minimal PATH/HOME also fails closed, for a subtler reason: `mismatches=1`,
  `regress_flipped=11/12`, `printers_rejected=11/12`, `controls_rejected=0/120` and
  `note: baseline not met - control credit withheld`. The failing row is
  `live-llamacpp-lifecycle: tip=false` — the bound tool resolves its server through
  `shutil.which('llama-server')`, and a minimal PATH has none. The counter correctly refuses to
  certify and correctly withholds control credit, but the reason is an *environment dependency of
  the instrument*, not of the lane (see F6).
* The **locale** does not change the verdict.

## F6 — observation: the live rows bind the server through the caller's PATH, not through the engine pin

`registry/engine-pins.tsv` pins `llama.cpp b11755`. The `live-llamacpp-lifecycle` row's template
is `python3 %T/tools/kama-llamacpp-live.py --model … --model-sha256 …`; the tool locates its server
with `shutil.which('llama-server')` (line 2111) and the counter's pattern for that row is only
`"outcome": "pass"` — the counter never compares the receipt's server digest with the engine pin.
The bound tool's env carries the caller's PATH verbatim (PATH is one of the four allowlisted keys).
Direct confirmation (`path-engine-test.sh`, `out-path-b11755.out`, `out-path-b11909.out`): the bound
tool under a PATH resolving `llama-server` to a different installed build reports a different server
and the **same** verdict —

```
PATH -> .../llama-b11755/llama-server  sha256=b6a31a8e97615a2a…  outcome: pass
PATH -> .../llama-b11909/llama-server  sha256=35ac50fb2cfd9c4f…  outcome: pass
counter under each PATH: population=12 covered=12/12 mismatches=0 pinned=13/13 … controls_rejected=120/120 errors=0 … met=True
```

The engine pin is therefore not enforced by the C2 counter or by the bound tool's own checks. This
is the C1 counter's business (it binds the server by digest); it is recorded here because it is the
same PATH-inheritance channel as F1/F3, and why the minimal-PATH run in F5 fails.

## Restoration evidence

`tools/round64-c2-counter.py` sha256 after every mutant and at the end of the battery:
`c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e` — identical to the pristine
value (`RESTORE counter sha256=… pristine=… match=yes` on all 7 restore points). The scratch clone
was reset to `23b3fdb1a925129a9961cf551f6d40bf251602cb` with `git status --porcelain` empty at the
end. The real lane `/home/vgpnk/Projects/shokunin/kama-shokunin` was never written: the only
absolute paths the strace shows under it are the 8 *symlink targets* the export reproduces, and the
T3 mutant re-pointed its symlink at a scratch victim before running.

## What I did NOT establish

* Whether any of the **shipped** 12 bound tools would in fact write through the symlinks (none
  writes a relative path today). F2 shows the counter cannot tell, not that the lane escapes.
* Whether F1 is reachable without the caller's cooperation: it needs the caller's `PYTHONPATH` to
  contain a shadowing module. In this lane the counter is run by the L1 in a controlled shell, so
  F1 is a **hardening gap in the instrument**, not an exploited lane escape. It is still a
  calibration defect: the counter certifies "the tip's bytes were checked" while the bytes it
  checked came from wherever the caller pointed it.
* `PYTHONSTARTUP` and `GIT_CONFIG_COUNT` were not tested as *shadow* vectors against the counter's
  own interpreter: `PYTHONSTARTUP` only fires for interactive interpreters (the counter is not one),
  and `GIT_CONFIG_COUNT` is stripped by `clean_env()` for the counter's git calls (E5 shows that
  stripping is load-bearing: without it the counter cannot even resolve its own tip under a hostile
  env).

## Tools

No tool was installed or upgraded for this seat: the host's `strace` (`/usr/bin/strace`), `git`,
`python3` (3.14) and `bash` were sufficient. No `pacman` transaction was performed (pacman is
paused host-wide).

## One-line summary

```
C2 environment axis at 23b3fdb1a925: pristine met=True (covered=12/12 mismatches=0 pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0); hostile caller env met=True (unchanged); env -i met=False (errors=1, fail-closed); locale met=True; MUTANTS: E1 SURVIVED, E2 SURVIVED, E3 SURVIVED, E4 SURVIVED, E5 SURVIVED, T1 SURVIVED (wrote into the lane clone and the export), T2 SURVIVED (wrote into the export), T3 SURVIVED (wrote OUTSIDE --work through the tip's committed symlinks) — all still met=True with controls_rejected=120/120; counter verdict is caller-environment dependent via PYTHONPATH (base tip scored as met=True, exit 0).
```
