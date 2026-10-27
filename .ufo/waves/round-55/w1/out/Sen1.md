# Sen1 — security review of the round-55 C1 kill battery

**Verdict:** no write escape — the harness writes only its own receipt dir and its own scratch, takes no user-controlled path, and confines every git mutation to a scratch clone; but its pass criterion is not the frozen preregistration's: 2 of the 4 preregistered mutants printed `met=True`, one preregistered mutant has no harness entry (its stale receipt, `met=True`, is still in the receipt dir), a non-preregistered mutant carries the code leg, and the per-leg check is a bare name substring that a *passing* leg's own detail line satisfies. **Severity: high for the C1 evidence chain (F1/F2), medium for reproducibility (F3/F4), low for the rest. The counter's own defense against the LD_AUDIT channel holds (probe below).**

Frozen inputs reviewed: `.ufo/waves/round-55/c1/battery/run-battery.py` (152 lines, committed at lane tip `8abadfed`), the seven receipts beside it, `tools/round54-replay-code-audit.py` (`sha256 c81fe971…79af` = `preregistration.json claims.C1.counter_sha256`), `preregistration.json` `controls.c1_kill_battery`.

---

## 1. Write surface — line by line (no escape)

| `run-battery.py` | write / action | target | verdict |
|---|---|---|---|
| 13-18 | constants `LANE`, `FREEZE`, `COUNTER`, `OUT`, `SCRATCH`, `LIVE` | literals only | no input-derived path; `name` in `OUT/{name}.out` (103) is a table key, never a path fragment → no traversal |
| 93 | `os.makedirs(OUT)` | lane `…/c1/battery` | the battery's designated receipt dir (docstring 5-6); *outside* `w1/out`, by design — it does not touch `measured/`, `controls/` or any other lane dir |
| 94-95 | `rmtree(SCRATCH)` + `makedirs` | `/fast/scratch/hyaku/kama-r55/c1/battery` (fixed) | outside every seat scratch; see F4 |
| 97 | `env` = inherited minus `GIT_*` | — | correct; every subprocess (98, 108-109, 120, 129-131, 135) is passed `env=env`, so no inherited `GIT_DIR`/`GIT_CONFIG_COUNT` can redirect a write |
| 98 | `git clone --shared LANE clone` | `SCRATCH/lane` | read-only on the lane; writes objects only into the clone |
| 120-135 | `reset --hard`, anchor-uniqueness check, file write, `add`, fixture `commit`, `rev-parse` | clone only | mutation confined; `src.count(old) != 1` (125) correctly refuses an ambiguous anchor; commit uses an explicit fixture identity |
| 103-110 | counter `--scratch SCRATCH/run-<name> --out OUT/<name>.out` | as given | inherited `env` (GIT_ stripped) |
| 147 | `rmtree(SCRATCH)` | fixed scratch | skipped on all four early `return 2` paths (100, 124, 127, 134) — docstring 6 ("removed on exit") is false there |

Counter side (`round54-replay-code-audit.py`): `main()` writes only under `S = mkdtemp(dir=--scratch)` (`tree/`, `counter-model.gguf`, `counter-archive.tar.gz`, `*-{tag}.log`, `canary-*`, `work-*`, `wd-*`, `{tag}.json`) plus `--out` (964-965); the replay gets `HOME`/`XDG_CACHE_HOME`/`TMPDIR` redirected into `S` (615-620); its only git calls are `rev-parse`, `archive`, `show` (891-892, 865) through `clean_env()` (170-176) — no checkout, no write to `--repo`. `/proc` is read-only (`mem`, `maps`, `exe`, `environ`, `stat`).

⇒ A run of the battery can damage exactly three places: its receipt dir, its fixed scratch, and (through the counter) `--scratch`/`--out` inside them. Nothing reached the lane tree, the fleet root or `~`.

## 2. Receipts vs. their mutant definitions

Expected failure is the leg named in `MUTANTS` (or, for the vector entry, `met=True`):

| receipt | named leg | detail line that names it | header | matches definition? |
|---|---|---|---|---|
| `control.out` | all legs pass | `code b1: 8 archive files … byte-equal`, `envnames b1: 5 … none of LD_PRELOAD…`, `rehash b1: 8 … unchanged` (5-21) | `met=True` | yes |
| `m-ldpreload.out` | `envnames` | `envnames b1: env: server environment carries LD_PRELOAD` (9,15,21) | `envnames=0/3 code=1 hostlibs=3/3 met=False` | yes — and the premise holds: `/usr/lib/libzstd.so.1.5.7` is root-owned and in `HOST_LIBS` (138-144), so code/hostlibs admit the mapping and the env **name** is the sole kill |
| `m-text-flip.out` | `code` | `code b1: code: replay own_code.members['…libggml-rpc.so'] None != archive digest` (11,25,39), `code: rerun code_mappings has no entry …` (10,24,38) | `code=0 coderuns=0/3 rehash=3 met=False` | yes — but it also trips `rehash` (17,31,45) |
| `m-member-flip.out` | `rehash` | `rehash b1: …/libggml-cpu-zen4.so changed after the observation: … digest dfd7… != 2f47…` (9,15,21) | `rehash=3 code=1 met=False` | yes |
| `m-ldaudit-foreign.out` | `hostlibs` (prereg) / "vector" (harness) | none — `envnames b1: 6 environment variable names recorded` (6,12,18) | `met=True` | **no kill; the receipt shows a no-op** (F6) |
| `m-ldaudit-writable.out` | `code` (prereg) | none — `code=1`, `met=True` | `met=True` | **no kill; and this mutant is not in the harness at all** (F1) |
| `m-extra-in-tree.out` | — (not in the harness) | none — `met=True` | `met=True` | orphan receipt, cited in a comment (run-battery.py:36-37) (F5) |

The three shipped kills are genuine. Two receipts in the frozen receipt dir are `met=True` against the frozen target's wording.

## 3. Findings

### F1 (high, evidence) — the shipped mutant set is not the frozen preregistration's
`preregistration.json controls.c1_kill_battery.mutants` (frozen before data) is:
`m-ldpreload (envnames leg)`, **`m-ldaudit-writable (code leg)`**, **`m-ldaudit-foreign (hostlibs leg)`**, `m-member-flip (rehash leg)` — "each expected to fail the frozen counter with its named leg", and `claims.C1.target` repeats "each named mutant receipt prints met=False (exit 1) with its named leg failing".

Shipped `MUTANTS` (run-battery.py:23-85) is `m-ldpreload(envnames)`, **`m-text-flip(code)`**, **`m-ldaudit-foreign(hostlibs, kind="vector", "expect met=True")`**, `m-member-flip(rehash)`.

- `m-ldaudit-writable` has no entry; its receipt survives and prints `met=True` — the preregistered code-leg kill did not kill.
- `m-text-flip` is not preregistered and was created to make the code leg fail.
- `m-ldaudit-foreign` is reclassified from a kill into a pass, exempted at 137-138 (`if kind == "vector": ok = rc == 0 and met`). The prereg's own `kill_rule` says "the claim is falsified if … any battery mutant prints met=True".

Command showing it: `git -C kama-shokunin show 9c60eae:.ufo/waves/round-55/preregistration.json` → `mutants` list above; `sed -n '23,85p' .ufo/waves/round-55/c1/battery/run-battery.py`; `head -2 .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out` → `met=True`.
The substitution is disclosed **only** in the commit subject (`8abadfed … "kill battery green (3 live kills + 1 vector analysis)"`) — not in `preregistration.json disclosure` (I printed it: it names only the C2 BASE revert) and not in `corpus/lessons/round-55.md`, whose line 76 states "each battery mutant receipt names the leg it kills" and line 110 "each names its killed leg" — false for the two `met=True` receipts.
Impact: C1's stated kill evidence and the artifacts do not correspond; a verifier reading the frozen target must score the battery as failed, and a verifier reading the harness scores it green.
Smallest remediation (frozen files: propose, do not edit): in round 56 restore one preregistered mutant per leg and either (a) use a code-leg mutant that kills the *code* leg as preregistered, or (b) amend `disclosure`/lessons with the pre-freeze finding ("the LD_AUDIT vector is void because libexpat exports no la_version; the code leg is carried by a tree pre-start byte flip") and remove `m-ldaudit-writable.out` + `m-extra-in-tree.out` from the receipt dir or mark them superseded. Patch proposal: `w1/out/Sen1/run-battery.proposed.patch` (adds a counter-sha gate, per-leg predicates, per-run scratch, `summary.out`; it scores the shipped receipts exactly as the table above).

### F2 (medium, harness correctness) — the kill verdict is a leg-name substring, not a leg failure
run-battery.py:140-142:
```python
leg_failed = f"{leg} " in "\n".join(
    ln for ln in text.splitlines() if ln.startswith("detail: "))
ok = rc == 1 and not met and leg_failed
```
Every leg prints a detail line whether it passes or fails, so the name alone is present in a *passing* receipt. Proven against the frozen receipts (`w1/out/Sen1/leg-check.out`):
- `control.out` (all legs passing): `leg_failed=True` for `bind`, `sealed`, `code`, `twopass`, `envnames`, `rehash`; `False` only for `hostlibs`, `newrow`.
- Relabelling: `m-member-flip` with `leg="code"` → harness prints `ok` although its code leg passed `3/3` (`code=1, coderuns=3/3`); `m-text-flip` with `leg="rehash"` → `ok`.
The harness never reads the header field that decides the leg (`code=0`, `envnames=0/3`, `rehash=3`, `hostlibs=3/3`), so an attribution mistake is invisible. In this round the shipped labels happen to be right, but `m-text-flip` really trips *two* legs (`code` and `rehash`), so even correct-looking attributions are not exclusive.
Smallest remediation: assert the leg's own counter (`coderuns=0/3`, `envnames=0/3`, `hostlibs=0/3`, `rehash>0`) plus the failure phrase, as in the proposed patch (verified: it keeps the three shipped kills green and turns the `m-member-flip`-as-`code` mislabel into `BATTERY-FAIL` — `w1/out/Sen1/predicate-check.out`).

### F3 (medium, integrity) — the counter bytes are never checked against the freeze
The harness execs `COUNTER = LANE/tools/…` (15) — the lane *working copy*, not the file at `FREEZE` — and neither hashes it nor records which counter produced a receipt. C1's `kill_rule` includes "if the counter bytes at measurement differ from counter_sha256"; the battery enforces nothing, so a post-freeze edit to the counter would be measured silently. Currently dormant: `sha256sum tools/round54-replay-code-audit.py` = `c81fe971…79af` = prereg. Remediation: gate on the hash and write it into the receipt dir (in the patch).

### F4 (medium-low, isolation) — fixed shared scratch, wiped at start, no `try/finally`
`SCRATCH` is the constant `/fast/scratch/hyaku/kama-r55/c1/battery` (17), removed at 94 and 147. Two concurrent battery runs (or a run from another seat) delete each other's clone mid-flight; a killed run leaves a 100+ MB tree; the four `return 2` paths leave the clone behind. Remediation: `mkdtemp` under the root and wrap the body in `try/finally` (in the patch).

### F5 (low, provenance) — stale receipts in the frozen receipt dir, no summary, unresolvable tips
- `m-ldaudit-writable.out` (mtime 10:30) and `m-extra-in-tree.out` (10:37) predate the harness file (10:42), have no entry in `MUTANTS`, and both print `met=True`; `m-extra-in-tree` is nonetheless cited as design evidence in the harness comment at 36-37.
- No artifact records the battery's own verdict or the per-run exit codes; `met=False` + a two-line receipt implies exit 1, but the receipt dir does not carry it.
- Every mutant tip in the receipts is absent from the lane (`585a6cb0`, `a12e2c0f`, `aa3c47cd`, `ba085a8b`, `23dc15da`, `312530a9` → `git cat-file -e` fails): the fixture clone was removed, so receipt↔mutant binding rests on filename plus the current table — impossible for the two stale ones.
Remediation: `summary.out` with harness sha, counter sha, exit codes and the gate verdict per row (patch), and archive/supersede the stale receipts.

### F6 (low, claim accuracy) — "LD_AUDIT is void on this glibc" is false; the vector is void for one file
Comment at 54-56 and 61-62 claims the LD_AUDIT vector for loading a root-owned foreign lib is "empirically void on this glibc". glibc here is 2.44 and honours LD_AUDIT: `/usr/lib/libexpat.so.1` is refused only because it exports no `la_version` (`ERROR: ld.so: … undefined symbol: la_version; ignored.`, `mapped_expat=0`), while a 30-byte `la_version` object is mapped (`mapped_aud=5`). Live probe (one counter run on my own clone, `w1/out/Sen1/ldaudit-la_version.out`): a loaded auditor is caught — `code b1: code: executable mapping …/libaud.so … is neither an archive file under the unpacked tree nor a root-owned host file (uid 1000 …)`, `met=False`, exit 1. So the counter is not blind, and the first half of the comment (same-uid mapping fails the code classification) is confirmed; but the receipt offered as "the evidence that the live hostlibs kill is root-gated" is a no-op receipt and proves nothing beyond "a non-loadable name is tolerated". Note `BAD_ENV` (counter:146) does not list `LD_AUDIT`, so the envnames leg would never name it — the code leg is the whole defense. The prereg's `limits` already declare the residual (host libs bound by basename, not byte-compared), so this is a wording/evidence defect, not a counter hole.

### F7 (info) — receipt text that invites misreading
- `rehash … changed after the observation: inode 349752383 != 349752383 or digest A != B` prints *both* comparisons unconditionally; only the digest differs. A reader sees a bogus inode change.
- `m-text-flip` trips `rehash` as well (`rehash=3`), so the rehash kill is not exclusive to `m-member-flip`.

## 4. Process hygiene
- `pgrep -af llama-server` at review start and again immediately after my counter run: empty (exit 1) both times. At the final check `pgrep -af llama-server` shows 2 live processes, **not mine**: every one traces to `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames` (peer seat, loopback ports 40863/40689); `pgrep -af llama-server | grep -c Sen1` = 0, and my scratch is deleted. A peer's live run is out of my scope, so nothing was killed. My one counter run tore its own servers down (`teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`), and `cleanup` of `/fast/scratch/hyaku/kama-r55/w1/Sen1` completed (`ls -d` → no such file).
- No tracer, no pacman, no tool install, no service touched. Lane read-only: `git rev-parse HEAD` = `8abadfed` before and after; my only clone is `--shared` in my own scratch (removed).
- Harness not re-run (it would write the L1's receipts); its predicate was replayed in-process instead (`leg-check.py`, `predicate-check.out`).

## 5. Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/leg-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/leg-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/predicate-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/ldaudit-la_version.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/probe-mutant.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/probe-commit.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/probe-provenance.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/libaud.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sen1/run-battery.proposed.patch`
