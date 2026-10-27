# M1C1Mut — round-55 C1 counter mutation test

**Verdict: 15/15 mutants applied cleanly (one site each, sha256-recorded), 21 counter runs (budget ≤25). 3 survivors — `drop-BAD_ENV`, `drop-rehash`, `newrow-always-true` — each with a live killing case on its battery-style attack tree; 4 killed (2 by redundant legs on m-text-flip, 1 by the positive control, 1 by the hostile-env pair); 8 equivalent on every runnable case (no live vector exists, consistent with the frozen root-gated limits). One freeze-consistency defect found in preregistration vs executed battery.**

## Method and cases

- Detector: the frozen counter `tools/round54-replay-code-audit.py` (sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`, verified before and after all work), invoked as `python3 <mutant> --repo <clone> --tip <tip> --scratch <run> --out <receipt>` in a scratch `git clone --shared` of the lane.
- Pristine copies and single-site mutants live at `w1/out/M1C1Mut/mutants/` (`.py` + `.diff`, sha256s in `results.json`). Mutants were applied to a copy of the frozen counter bytes; the lane file was never edited (after-hash identical).
- Cases: `clean` = tip `9c60eae6f7ed84f7da93d219a406aadc30958c6c`; `base` = `3a600d2f729828419aaea34cc402c8b0d20fb720`; `t-ldpreload` = `17b4c9ea1887dcdffdaf39c1fe612441850bbfe0`, `t-text-flip` = `fcc9fc51e0a81fcef6b089976148ddf491e35ad7`, `t-member-flip` = `0d812a4de0b0d044aec4cdd6bc25009154e0a982` — three fixture commits in my clone, each parent `9c60eae`, carrying the battery driver's exact `tools/kama-llamacpp-live.py` patches (same anchors, same payloads as `.ufo/waves/round-55/c1/battery/run-battery.py` `MUTANTS`); `hostile` = clean tip with `GIT_OBJECT_DIRECTORY=<empty dir>` injected into the counter's environment.
- Verdicts: **survived** = a case the pristine counter fails prints `met=True` under the mutant (the removed check was the sole defense for that vector); **killed** = some case detects the mutation (attack still caught, false positive on the honest tree, or hard failure under the hostile env); **equivalent** = met identical to pristine on every runnable case (coverage finding: no live vector exists). Pairs for survivors use my own pristine runs on the same tree tips (P-ldpreload/P-text-flip/P-member-flip) plus the frozen receipts (identical content).
- Runs: 17 + 3 pristine pair runs + 1 G1 repeat for the verbatim error = 21 of the allowed 25; ~17–19 s each, 3-way parallel.

## Results

| # | Mutant (site, `tools/round54-replay-code-audit.py`) | Case | Pristine / mutant | Verdict |
|---|---------------------------------------------------|------|-------------------|---------|
| A1 | drop mem compare, `got != want` (L540) | t-text-flip | met=False / met=False exit 1 | **killed** — redundant |
| A2 | compare only first page (`length = hi - lo` → `min(length, 4096)`, L523) | t-text-flip | met=False / met=False exit 1 | **killed** — redundant |
| A3 | accept any uid (drop `st.st_uid != 0`, L558) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| A4 | drop writable test (drop `os.access(path, os.W_OK)`, L558) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| A5 | skip `HOST_LIBS` basename check (L563) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| A6 | drop `REQUIRED` member loop (L570) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| A7 | accept `/memfd:` by name only (drop dev+inode match, L511) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| A8 | skip `KERNEL_MAPS` (L503) | clean | met=True / met=False exit 1, `anon=12` | **killed** — false-positives honest tree |
| B1 | drop `BAD_ENV` check (L437) | t-ldpreload | met=False / **met=True exit 0** | **survived** |
| B2 | `env_leg` also reads values (L433) | t-ldpreload | met=False / met=False exit 1 | **equivalent** for met (values-read is output-invisible — see finding 3) |
| C1 | drop descendant gate (`bind_one`, L697) | clean | met=True / met=True exit 0 | **equivalent** — no live vector |
| D1 | drop twopass snapshot compare (L714) | clean | met=True / met=True exit 0 | **equivalent** — see finding 4 |
| E1 | drop rehash leg (L770–L780) | t-member-flip | met=False / **met=True exit 0** | **survived** |
| F1 | `newrow_leg` → `return True` (L873) | base | met=False / **met=True exit 0** | **survived** |
| G1 | `clean_env` strips only `GIT_DIR` (L170) | hostile | met=True exit 0 / **exit 2** | **killed** — hostile env reaches git |

Receipts: `w1/out/M1C1Mut/<Run>.out`; frozen counterparts in `w1/out/M1C1Mut/frozen/`; run metadata in `w1/out/M1C1Mut/results.json`.

## Killing cases (survivors)

1. **B1 `drop-BAD_ENV`** — `P-ldpreload.out:2` (pristine, my tree): `envnames=0/3 … met=False`, `detail: envnames b1: env: server environment carries LD_PRELOAD`; `B1-drop-BAD_ENV-check.out:2` (mutant, same tree): `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True`, exit 0. The `/usr/lib/libzstd.so.1.5.7` preload is admissible to the code leg (root-owned, in `HOST_LIBS`); **envname inspection is the sole defense against injection-environment planting**. Same pair vs the frozen battery receipt `frozen/m-ldpreload.out`.
2. **E1 `drop-rehash`** — `P-member-flip.out:2`: `rehash=3 met=False`, `detail: rehash b1: …/libggml-cpu-zen4.so changed after the observation … digest != archive`; `E1-drop-rehash.out:2`: `rehash=0 met=True` exit 0. Mapped pages are untouched by a post-launch file rewrite; **the post-exit re-hash is the sole defense**.
3. **F1 `newrow-always-true`** — `frozen/base.c1.out:1-2`: `tip=3a600d2…`, `newrow=0 … met=False` exit 1; `F1-newrow-always-true.out`: `newrow=1 … met=True` exit 0 on the identical base tip. Confirms the round-55 newrow re-freeze (S511 row) is load-bearing for the red-at-base property; the mutant passes every other leg, so the base control pins exactly this leg.

## Killed mutants

- **A1/A2 (t-text-flip)**: the pre-launch `libggml-rpc.so` flip is additionally caught by three other legs — `rehash=3` (file left flipped at exit), `bind=0` (replay `exit 1 match False` — the live tool's own `own_code` verify refuses, `verified: False`), `code=0` (missing `code_mappings` entry + `own_code.members` digests). Notably, `A1-drop-mem-compare.out` contains **zero** `mapped bytes … differ` lines — the counter's own `/proc/mem` compare never fires on this vector even in pristine; the battery does not isolate the counter-side compare. An isolating vector would need the flip placed *after* the live tool's `own_code` verification. **Coverage finding, not a contract break** (predicate still fails on the attack).
- **A8 (clean)**: `anon=12` — `[vdso]`/`[vsyscall]`/`[vvar]`/`[vvar_vclock]` executable rows are misclassified `code: anonymous executable mapping` → `coderuns=0/3`, met=False on the honest tree. The `KERNEL_MAPS` skip is load-bearing for honest runs; the mutation is killed by the positive control.
- **G1 (hostile)**: `G1-strip-only-GIT_DIR` with `GIT_OBJECT_DIRECTORY=$S/empty-objects` inherited → `exit 2`, `could-not-evaluate: git rev-parse --verify 9c60eae6f7ed84f7da93d219a406aadc30958c6c^{commit}: fatal: Needed a single revision` (`G1-strip-only-GIT_DIR.out` absent — exit-2 path writes no receipt; verbatim text in run log). Pristine `G0-pristine-hostile` under the identical env: `met=True` exit 0. The inherited `GIT_*` variable reaches `git` only under the mutant — **the `clean_env` strip is load-bearing** (demonstrated as denial; a crafted object-store redirection could likely flip a measurement — left unexercised, disclosed).
- **B2 (t-ldpreload)**: `envnames=0/3`, `met=False` — `BAD_ENV` retained, attack still caught. The value read itself produces no observable change in any receipt field (see finding 3).

## Equivalent mutants (no live vector — coverage findings)

A3, A4, A5, A6, A7, C1, D1 print `met=True` on the only cases they could be run against; each is a genuine weakening (a foreign root-owned host lib, a missing `ggml-cpu` mapping, a foreign executable memfd, a non-descending announced pid, a mid-hold map change would pass) but **no runnable tree-only vector reaches them**:

- A3/A4/A5 (uid / writable / hostlibs-basename): both LD_AUDIT vectors are empirically void on this glibc (`frozen/m-ldaudit-foreign.out` `met=True`, `frozen/m-ldaudit-writable.out` `met=True`), and any *same-uid* plant additionally fails the writable test — a single-test bypass can't be demonstrated without root. This matches the frozen limits (root-actor / K1Cheat class is "covered by design and receipts, not by a same-uid mutant").
- A6 (`REQUIRED`): honest runs always map all four required members; no vector removes one.
- A7 (`/memfd:` name-only): no vector creates a second executable memfd.
- C1 (descendant gate): every tree-only way to announce a non-descending pid co-fails another leg — a same-uid foreign `llama-server` fails `sealed`/`bind` (not memfd-sealed, wrong exe owner), and a detached honest server survives replay exit → `teardown` fails. The gate's Sen1Mem F2 class is unreachable without a cooperating non-descendant honest server.
- D1 (twopass): byte-divergence between passes is strictly redundant with the per-pass archive compare (`want` is fixed; `snap = sha(got)`), **but** the snapshot-compare additionally fires on a *mapping-set change* between passes (row appears/disappears — e.g., a mid-hold `munmap`), which no other leg catches and no vector exercises. Not redundant in full; unvectorized today.

## Findings

1. **Survivors pinpoint the three single-defense legs** — `envnames` (B1 vs `m-ldpreload`), `rehash` (E1 vs `m-member-flip`), `newrow` (F1 vs base): each is the sole barrier for its vector; removing it lets a real attack or the base control pass (`met=True`). This is the expected, healthy result — the kill battery is correctly scoped on these three.
2. **Counter-side mem compare is unisolated** — `m-text-flip` never reaches it (zero `mapped bytes differ` lines in the pristine battery receipt `frozen/m-text-flip.out` and in `A1-drop-mem-compare.out`); the counter's `/proc/mem` byte-compare shares its kills with the replay's own `own_code` verify + `rehash`. Worth a note in a future battery pass (e.g., flip post-`own_code`-verify, pre-`Popen`).
3. **The counter cannot enforce its own "values are never read" contract** — `env_leg` (L430–L440) documents that it reads environment *names* only, but nothing observes the read itself: mutant B2 reads full values into the returned list and every receipt field stays identical. The contract is self-asserted, not checked.
4. **Freeze-consistency defect — preregistration vs executed battery**: `.ufo/waves/round-55/preregistration.json` `controls.c1_kill_battery.mutants` names `["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`, and `claims.C1.target`/`kill_rule` require *each named mutant receipt* to print `met=False` and declare the claim falsified if "any battery mutant prints met=True". Reality: `run-battery.py`'s `MUTANTS` executes `{m-ldpreload, m-text-flip, m-ldaudit-foreign, m-member-flip}` — `m-ldaudit-writable` was never in the final driver and its (met=True) pre-freeze receipt was deleted from the battery dir at ~11:13 while I worked (I preserved a copy: `frozen/m-ldaudit-writable.out`); `m-text-flip` *is* executed and caught but is *not* named; `m-ldaudit-foreign` is named as a met=False mutant but is `kind="vector"` — `m-ldaudit-foreign.out:2` prints `met=True` by design, which trips the kill rule's letter. Proposed amendment in `out/M1C1Mut/prereg-fix.md`: name the executed set, declare the vector-analysis kind and its expected `met=True`, scope the kill rule to kill-kind mutants, and note `m-ldaudit-writable` as a dropped pre-freeze vector.
5. **Tooling**: none installed; system python3 3.14.8 + git used. All git mutations were confined to my scratch clone (`rev-parse --show-toplevel` asserted before each commit; fixture identity `fx <fx@invalid>` used only there).

## Restoration evidence

- Lane counter sha256 before: `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`; after: `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` (also `round54-cited-path-check.py` `d70a17…`). Lane `git status` shows only siblings' `w1/out/*` activity; I wrote only `w1/out/M1C1Mut*`.
- All mutant copies lived in `/fast/scratch/hyaku/kama-r55/w1/M1C1Mut/` (removed after deliverables were copied); llama-server processes: none of mine survived (`pgrep` leftovers belong to sibling `J5EnvNames` runs — untouched).
- Deliverables: this report; `w1/out/M1C1Mut/` = 21 receipts (`*.out`), `mutants/` (15 `.diff` + 15 `.py` + `pristine.py` + `mutdrive.py`), `frozen/` (8 cited artifacts), `results.json` (tree tips, mutant sha256s, run metadata), `prereg-fix.md`.

Report: .ufo/waves/round-55/w1/out/M1C1Mut.md
