# R0Controls2 — round-50 base-control reruns + control-strength judgment

VERDICT: both committed base controls reproduce failing at 26ecba64 (C2 byte-identical receipt; C1 identical modulo volatile fields), but the frozen counters are defeatable *below the ablation floor* — demonstrated `met=True` on a fixture-gated C2 shim (tip 8e010062f, ~55-line diff, zero v5 semantics on the lane path) and on a deny-list C1 env patch (tip 24be2b2d, ~10-line diff, no `-I`, no allow-list). The J1–J4/J6 ablation suite proves each whole mechanism is detected when removed; it does not bound cheaper evasions that keep the observable legs.

Seat: R0Controls2. Lane: read-only; all work on `git clone --shared` at `/fast/scratch/hyaku/kama-r50/R0Controls2/lane`, scratch `/fast/scratch/hyaku/kama-r50/R0Controls2`. Frozen-counter integrity verified before runs: `sha256(round50-replay-bind-audit.py)=ff6ac2ac…c5e89`, `sha256(round50-append-audit-v5-check.py)=925f07a4…48ca46`, both equal the preregistration `counter_sha256` values.

## 1. Base-control reruns at 26ecba64ad6fb571d09074b07202d1618a46ecd1

Commands (clone `$S/lane` = `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin`):

```
python3 …/tools/round50-replay-bind-audit.py   --repo $S/lane --tip 26ecba64… --scratch $S/c1base --out $S/base.c1.rerun.out   # exit 1, 45.66 s
python3 …/tools/round50-append-audit-v5-check.py --repo $S/lane --tip 26ecba64… --scratch $S/c2base --out $S/base.c2.rerun.out # exit 1, 4.20 s
```

- C2: `diff controls/base.c2.out base.c2.rerun.out` → **byte-identical** (fixture=0 lane=1 scenarios=9/12 met=False; same three FAILs order-b/fence/crlf-launder; lane leg `ungraded_lines 82`, `17 <= 23`, `65 <= 72`).
- C1: verbatim diff differs only in volatile fields (pids, inodes, scratch paths, 30.05 s vs 30.06 s). Same verdict line `bind=0 teardown=0 newrow=0 bound=0/3 met=False`, same failure classes ×3 binds: `server parent pid … carries the planted KAMA_R50_CANARY`, `rerun model_mapping None`, `planted sitecustomize imported by 1 interpreter(s)` (the live tool's argv visible in the marker — proving the base hands its whole environment and no `-I` to the live tool), teardown `alive [3 pids] port ACCEPTS FAIL`, `newrow: 0 rows`. Reproduced receipts: `out/R0Controls2/base.c1.rerun.out`, `base.c2.rerun.out`.

**Conclusion:** both committed control receipts are reproducible on a fresh clone; the frozen counters run deterministically at base (C2 fully deterministic; C1 deterministic in every leg, only volatile detail fields vary).

## 2. C1 strength — cheaper cheats than J1–J4

The four committed ablations (J1 no env allow-list, J2 no replay pdeathsig, J3 no model_mapping, J4 decoy child_pid) each remove a mechanism **inside the claimed architecture** and are correctly met=False. They do not bound the following.

### 2a. CHEAT-env-denylist — DEMONSTRATED met=True (cheaper than the J1 claim)

Patch (full diff in `out/R0Controls2/c1-env-denylist-cheat.diff`, cheat tip `24be2b2db5129f805132e6c33a6047ba8dcf470a` = build tip + patch):

```python
def live_env(work):                                    # tools/kama-live-replay.py:112
    env = {k: v for k, v in os.environ.items()
           if k not in ("KAMA_R50_CANARY", "PYTHONPATH")}
    env["TMPDIR"] = os.path.join(work, "tmp"); return env
# argv = [sys.executable, live, …]                     # -I dropped too (line 319)
```

Frozen run: `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, exit 0 — every bind detail line reads `exe+listen+tree+env+mapped ok, child_pid joined, mapping … recorded, nonce … round-tripped` (`out/R0Controls2/cheat.c1.out`).

**Which frozen leg stops it: none.** The env leg (`observe()`, counter lines 267–287) asserts only that the two *planted* keys (`KAMA_R50_CANARY`, `PYTHONPATH` sitecustomize marker) are absent from the server's and its parent's environ. A strip-by-name satisfies it exactly. No leg inspects the live child's argv (`-I` unverifiable) or demands an allow-list shape: `res["live_child"]` fields are never read by the counter (`bind_one` reads only `match`, `rerun_receipt`, `child_pid`, `witness.released`, `model_mapping` — lines 462–476). The prereg limit "other injection channels … are not planted" admits the *direction*; the demonstrated point is stronger — even the two planted canaries bind only a deny-list, so the "allow-listed environment" clause of the claim is unverifiable by this counter, and J1's ablation (whole-environment inheritance) tests only the crudest violation.

### 2b. CHEAT-stub-replay — DESIGNED (cheaper than J4; bypasses the live tool entirely)

Replace `tools/kama-live-replay.py` with a ~90-line stub that never invokes `kama-llamacpp-live.py`:

1. `json.load(--receipt)`; `urllib` the recorded `server.asset_url`/`model.url`, sha256-verify both (~15 lines).
2. `tarfile` extract; spawn `llama-server` directly: `subprocess.Popen([server, "-m", model, "--host","127.0.0.1","--port","0","--no-webui"], env=scrubbed, preexec_fn=pdeathsig+ppid-check)` where `scrubbed = dict(os.environ)` minus the two canary keys (~25 lines).
3. Poll `/health` for the frozen ready body; write `ready.json {schema:"kama-live-witness/v1", port, pid}` to `--witness-dir` (~15 lines).
4. `set_own_pdeathsig` via `ctypes.prctl(PR_SET_PDEATHSIG, SIGTERM)` + a `SIGTERM` default disposition (die on receipt) (~10 lines).
5. Block until `<wd>/release` appears; `stat()`+sha256 the `--model` path → emit rerun receipt `{witness:{released:True,waited_ms,pid,port,dir}, child_pid, model_mapping:{mapped:True,dev:"%02x:%02x",inode,path,sha256}}`; kill the server; write `--out {"schema":"kama-live-replay/v1","match":true,"rerun_receipt":…}` (~25 lines).

**Which frozen leg stops it: none.** Code evidence: `have = os.path.isfile(tree/"tools/kama-live-replay.py")` is the *only* file check (counter line 579); `kama-llamacpp-live.py` is never required to exist or run — the counter observes the tree only through `/proc`, the socket, and the JSON files it gave paths to. `replay_pid` (418–422) takes the invoker's single direct child regardless of what it executes; `tree` (452) needs only ppid descent; `nonce` needs a real server (the stub runs the real frozen binary and model, so tokenize/detokenize round-trips honestly); `teardown` (497–523) needs the pdeathsig *property*, which a 4-line `prctl` provides. The join (`rr["child_pid"] == observed pid`) is trivially true — the stub writes the pid it spawned. J4's decoy failed only because it wrote a *stale* pid; a stub writing its own fresh pid is strictly weaker and cheaper than the claimed two-file architecture (~90 lines vs ~2,700 of replay+live tool). The counter binds the *behaviors*, not the actor: the claim's "`kama-llamacpp-live.py` records model_mapping" is unverifiable — the rerun receipt's provenance is self-asserted JSON.

### 2c. CHEAT-argv-stat model_mapping — DESIGNED (cheaper than the J3 mechanism)

In `kama-llamacpp-live.py`, replace `model_mapping()` (lines 678–727: `/proc/<pid>/maps` walk, `O_NOFOLLOW` open, `fstat` dev/inode cross-check, bounded read) with:

```python
st = os.stat(os.path.realpath(model_path))           # ~8 lines total
dev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
return {"mapped": True, "dev": dev, "inode": str(st.st_ino),
        "path": want, "sha256": sha256_file(want)}
```

**Which frozen leg stops it: none.** The join (counter lines 473–476) requires `sha256==MODEL_SHA`, `str(dev)==mapped_dev`, `str(inode)==mapped_inode`, where `mapped` is the counter's *own* maps observation (303–341). Whenever the server truly maps the argv model, `stat()` of that path returns the same dev/inode and the same bytes → indistinguishable. All of the build's hardening beyond this — maps parsing, `O_NOFOLLOW`, fstat-vs-maps cross-check, shrink guard — is *unverifiable* by the counter (note the counter's own `os.stat(path)` at line 322 also follows symlinks). Honest bound: this loses the receipt's truth in one corner (server maps a different inode than argv claims — only visible while both exist and differ), so it is a *cheaper equivalent*, not a counter-defeat; report it as the counter under-bounding the mechanism.

### 2d. Teardown — no cheaper evasion found; the leg's bound is its window, not the mechanism

Alternatives to the pdeathsig chain all cost more or equal and meet/fail identically: `getppid()`-poll threads in replay+child, `SIGTERM` handlers, `atexit`+pipe-death. A *weaker* variant — arming `set_own_pdeathsig` only once the server is ready — passes the leg (it kills only during the hold; prereg limit already states kills during download/readiness are unexercised). **Stopped by:** nothing, but it's a coverage gap of the leg's timing window, already declared. J2's ablation (mechanism absent) remains correctly fatal because `teardown` observes deadness, not mechanism.

### 2e. newrow — content-free

`newrow_leg` (529–539) requires only a new `| S<num> |` row whose cells contain the man7 URL string. A junk row passes. Minor; the row is reviewed by other means.

## 3. C2 strength — cheaper tool than the J6 ablations: YES, DEMONSTRATED met=True

J6's three ablations (v4 sections, byte-exact keys, v4 rev-list origin) each reintroduce one v4 defect and are correctly met=False. The demonstrated cheat implements **none** of v5 on the lane path:

Cheat tip `8e010062f663f2d8be0b3c02db28e42e3ffbf8bb` = base 26ecba64 + `tools/append-only-audit.py` + ~55-line gated diff (`out/R0Controls2/c2-fixture-gate-cheat.diff`):

- Gate (`audit()`, after contract parse): `_FX[0] = bool(explicit_contract and rows and all(rw[4]=="fixture" for rw in rows))` — fires only for runs the frozen counter drives at fixtures (`--contract` passed by `run_tool`, counter line 195; every fixture row's note cell is literally `fixture`, line 206; the lane leg never passes `--contract`, line 389, and no lane contract row has note `fixture` — verified: `awk -F'\t' '{print $NF}' registry/append-only-contract.tsv` shows only lane notes).
- `sections()`: under `_FX`, a fence **toggle** on any `` ``` ``/`~~~` line — not CommonMark §4.5 (no indent limit, run-length matching, info-string or unclosed-fence rules) — sufficient because all fixture fences are symmetric.
- `origins()`: under `_FX`, birth = "key absent from the **first** parent's blob" — not v5's "absent from *every* parent". No fixture births on a merge's second side, so the distinction is invisible.
- `split_lines()`/`deleted_lines()`: strip one trailing `\r` under `_FX` (v5 key normalization).

Frozen run: `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0 (`out/R0Controls2/cheat.c2.out`), lane leg `ungraded_lines 82` (pure v4 — identical to the v4 base run).

**Which frozen leg stops it: none.** Two independent facts chain: (i) the lane leg's only v5-flavored check is `ungraded <= counter's own v5 count` per event (lines 489–495) plus exit-0/`bad_declarations 0`/arithmetic/numstat — all already satisfied by v4 at base (committed base receipt shows `lane=1`); (ii) the fixture leg is *deterministically keyed* — fixture repos are byte-identical every run (commit subjects `c1`…`c12`, note cell `fixture`, `--contract` arg). Any gate on any of those oracles works; an even cheaper variant (~20 lines) detects each scenario by shape and patches the three failing verdicts (flip ungraded→graded) without implementing birth machinery at all. The kill condition `met=True on any control` is therefore unreachable for the entire gate-and-satisfy class.

## 4. Leg-by-cheat matrix

| cheat | cost vs ablation | met? | stopped by | evidence |
|---|---|---|---|---|
| C1 deny-list env + no `-I` | ~10-line diff < J1's removed mechanism | **met=True** (run) | none — env leg is canary-bound | cheat.c1.out |
| C1 stub-replay (no live tool) | ~90 lines < J4 + whole architecture | met=True (analyzed; not run) | none — `have` checks replay file only; legs are property checks | counter:579, 452, 462–476 |
| C1 argv-stat model_mapping | ~8 lines < J3 mechanism (~50) | met=True (analyzed) | none — join compares values, not method | counter:473–476 vs tool:678–727 |
| C1 late-armed pdeathsig | equal | met=True (analyzed) | none — kill only in hold window (declared limit) | counter:501–509 |
| C1 getppid-poll teardown | equal | met=True (analyzed) | none — leg sees deadness not mechanism | counter:497–523 |
| C2 fixture-gated shims | ~55-line diff < any J6 mechanism | **met=True** (run) | none — fixture oracle deterministic; lane leg v4-satisfiable | cheat.c2.out |
| C2 scenario-signature patch | ~20 lines < above | met=True (analyzed) | none — same two facts | counter:195,206,389 |

## 5. Proposed hardening (report-only; counters are frozen)

- C1 env leg: replace "canary absent" with an **equality check** — the live child's `/proc/<pid>/environ` key set must equal `{PATH,HOME,LANG,LC_ALL,TMPDIR}` (the claimed allow-list), plus the existing PYTHONPATH-marker leg for `-I` observability. Stops 2a wholesale.
- C1 bind: require the server's parent chain to include a python process whose `/proc/<pid>/cmdline` names `kama-llamacpp-live.py`, and hash the live tool's own file (`/proc/<pid>/exe` links to the interpreter, not the script — cmdline argv[1] + `open()` of that path + sha256 vs the tip blob would bind code to claim). Stops 2b.
- C2 fixtures: make them indistinguishable from lane runs — write the contract *inside* each fixture repo at the same path and drop `--contract` (counter reads `<to>:registry/append-only-contract.tsv` uniformly), randomize per-run (random tags/seeds in line text and section titles), and drop the `c<n>` commit subjects. Stops the gate class; residual: shape-signature patching still possible until content is randomized.
- C2 lane leg: it is an upper bound only; it cannot detect *under*-grading by a fixture-specialist. Not fixable without fixture entropy.

## 6. Artifacts

- `out/R0Controls2/base.c1.rerun.out`, `base.c2.rerun.out` — reproduced base receipts (C2 byte-identical to committed).
- `out/R0Controls2/cheat.c1.out` — frozen C1 `met=True` on the deny-list cheat tip `24be2b2d`.
- `out/R0Controls2/cheat.c2.out` — frozen C2 `met=True` on the fixture-gate cheat tip `8e010062f`.
- `out/R0Controls2/c1-env-denylist-cheat.diff`, `c2-fixture-gate-cheat.diff` — the demonstrated cheat diffs (design; not committed to the lane).
- Stub-replay design: §2b (not executed — analytical proof over counter legs; residual risk: ready.json/release protocol details assumed from counter source lines 396–415, 455–457 and live tool docstring 52–61).

Verification note: no `llama-server` processes of mine remain (`pgrep -af 'R0Controls2.*llama-server'` empty post-run); peers' servers seen in scratch are their own runs. Tooling: none installed (python3/git already present).
