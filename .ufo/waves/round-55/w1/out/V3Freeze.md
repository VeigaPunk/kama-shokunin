# Round 55 w1 — V3Freeze: freeze-integrity audit (lane kama)

**Verdict: PASS on all four assigned checks — the frozen counters, preregistration hashes, receipt tip fields and C2 re-runs show no drift; one Medium finding outside the four checks: the committed C1 kill battery diverges from the frozen preregistration's mutant contract (roster re-scoped, two stale `met=True` receipts left in the battery dir), disclosed only in driver comments.**

Audited at 2026-10-27, scratch `/fast/scratch/hyaku/kama-r55/w1/V3Freeze` (removed before finish). Lane read-only except the out dir; the only clone made was `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (toplevel verified equal to `$S/lane`). No tools installed or upgraded (record: none used).

## Check 1 — counter sha256 at 9c60eae6 == preregistration counter_sha256 — PASS

```
git show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-replay-code-audit.py | sha256sum
  -> c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af
git show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-cited-path-check.py | sha256sum
  -> d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c
```

- `preregistration.json:16` (claims.C1.counter_sha256) `c81fe971…` — MATCH
- `preregistration.json:27` (claims.C2.counter_sha256) `d70a1729…` — MATCH

## Check 2 — counters byte-identical to the copies used for every committed receipt — PASS (with one precision note)

- Working tree `sha256sum`: `tools/round54-replay-code-audit.py` = `c81fe971…`, `tools/round54-cited-path-check.py` = `d70a1729…` — equal to the preregistration values.
- `git show 9c60eae6…:<counter> | cmp - <worktree counter>` → identical, both files.
- `git rev-parse HEAD` = `8abadfedf89f35372645b1e5d6ce4a2109186f90` — **not** `9c60eae6` literally. `git merge-base --is-ancestor 9c60eae6 HEAD` → yes; `git log 9c60eae6..HEAD` = exactly one commit, "round-55 w1: build measurements green at freeze … dispatch + ready", whose diffstat (17 files) adds only w1 bookkeeping (`build_spec.py`, battery + measured receipts, `w1/dispatch.json`, `w1/spec.json`, `w1/validate.out`, `w1.ready`, `out/swarm-registry.json`).
- `git diff --name-only 9c60eae6 HEAD -- tools/round54-replay-code-audit.py tools/round54-cited-path-check.py corpus/SOURCES.md registry/cited-path-corrections.tsv` → empty. `git log --oneline -- <counters>` → last change at `9c60eae6` (freeze), before that `9a3104c7` (round 54). `git diff --stat 9c60eae6 HEAD -- preregistration.json controls/` → empty (preregistration and red controls untouched since freeze; `measured/` receipts added after, as intended by freeze-before-data).

So the literal "working tree equals 9c60eae6" does not hold at audit time (HEAD moved one pure-bookkeeping commit past it), but no counter byte changed since the freeze commit, hence **every round-55 receipt committed (controls at `9c60eae6`; measured + battery at `8abadfed`) necessarily ran bytes identical to `counter_sha256`**. No drift; the HEAD move itself is expected in-flight wave state and touches no claim surface.

## Check 3 — receipt tip fields — PASS

| receipt | line 1 | expected | |
|---|---|---|---|
| `controls/base.c1.out:1` | `tip=3a600d2f729828419aaea34cc402c8b0d20fb720` | base | MATCH |
| `controls/base.c2.out:1` | `tip=3a600d2f… fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b` | base | MATCH |
| `measured/c1-build.out:1` | `tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c` | build | MATCH |
| `measured/c2-build.out:1` | `tip=9c60eae6… fleet=6c4aba34…` | build | MATCH |
| `c1/battery/control.out:1` | `tip=9c60eae6…` (positive control at freeze tip) | build | MATCH |

The six battery mutant receipts carry fixture-clone tips (`312530a9…`, `aa3c47cd…`, `23dc15da…`, `585a6cb0…`, `ba085a8b…`, `a12e2c0f…`); `git cat-file -e <tip>^{commit}` in the lane → absent for all six, consistent with `run-battery.py`'s flow (reset the shared clone to FREEZE, apply one mutant, `git -c user.name=fx … commit` in the clone, measure there).

## Check 4 — C2 re-run byte-for-byte except fleet rev — PASS

Re-ran the frozen counter from the lane path with `--repo $S/lane` (shared clone), scratch under `$S`, receipts written to `$S` then copied out. The committed receipts pin `fleet=6c4aba34…`; that commit still exists in the fleet repo, so reruns pinned `--fleet-rev` to it.

| run | command (abridged) | exit | result |
|---|---|---|---|
| A | `round54-cited-path-check.py --repo $S/lane --tip 9c60eae6… --fleet-rev 6c4aba34…` | 0 | `met=True`, diff vs `measured/c2-build.out` **empty**; file sha256 `bc59e5e1…` == committed `bc59e5e1…` |
| B | `--tip 3a600d2f… --fleet-rev 6c4aba34…` | 1 | `met=False`, `dropped=1`, diff vs `controls/base.c2.out` **empty**; sha256 `d6a6f550…` == committed `d6a6f550…` |
| C | `--tip 9c60eae6… --fleet-rev HEAD` | 0 | diff vs `measured/c2-build.out` = **line 1 only** (`fleet=666bc1ef…` vs `6c4aba34…`); every leg/scenario/advisory line identical |

Byte-for-byte equality confirmed by both `diff` (empty) and whole-file sha256. The "except fleet rev" exception is empirical: with the fleet pinned, not even line 1 differs; unpinned, only line 1 differs. Full diffs: `V3Freeze/rerun-diffs.txt`; rerun receipts: `V3Freeze/rerun-*.out`.

## Findings

### F1 — Medium: committed C1 kill battery diverges from the frozen preregistration's mutant contract

Frozen contract:
- `preregistration.json:44` — mutants `["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`
- `preregistration.json:19` (C1 target) — "kill battery: each named mutant receipt prints met=False (exit 1) with its named leg failing"
- `preregistration.json:20` (kill_rule) — "falsified if … any battery mutant prints met=True"

Delivered (`c1/battery/`, committed in `8abadfed`):
- `run-battery.py` MUTANTS = {`m-ldpreload` (envnames, kill), `m-text-flip` (code, kill), `m-ldaudit-foreign` (hostlibs, **vector**, `ok := rc==0 and met`, lines 57–60 and 137), `m-member-flip` (rehash, kill)}.
- `m-ldaudit-foreign.out:2` prints `met=True` — the frozen text names this mutant with the hostlibs leg and expects `met=False`.
- `m-ldaudit-writable.out:2` prints `met=True` and is **not produced by the committed driver** (its envnames detail lines count 6 env names, i.e. it was an LD_AUDIT env injection, not a code-leg mutation). Together with `m-extra-in-tree.out` (`met=True`, also not in MUTANTS) these are artifacts of an earlier battery iteration — the committed driver's own comments reference them (`run-battery.py:33-36` "m-extra-in-tree showed…", `:67-68` "the first battery run showed met=True for it").
- The frozen code-leg kill `m-ldaudit-writable` does not exist in the delivered roster; the code leg is killed by `m-text-flip` (`m-text-flip.out:2` `met=False`, `coderuns=0/3`), which the frozen list does not name.
- `corpus/lessons/round-55.md:73-76` still asserts the battery's "named mutants must each fail the frozen counter" and "each battery mutant receipt names the leg it kills" — true for the three kills, false for the vector receipt and the two stale artifacts.

Under the frozen kill_rule's literal text, the battery directory contains two mutant-named receipts printing `met=True`. The technical re-scope is defensible and documented in-driver (`run-battery.py:44-49`: the hostlibs leg guards root-actor plants and the LD_AUDIT vector is void as a same-uid mutant; the preregistration's own `limits` paragraph concedes some vectors are not reproducible as non-root mutants), and the `8abadfed` commit message describes the battery honestly as "3 live kills + 1 vector analysis" — but nothing reconciles the frozen document with what landed, and the stale `met=True` receipts sit in the battery dir where the kill rule's "any battery mutant" literally bites. This is a document/contract drift, not evidence of a counter shortcut; whether it falsifies C1 is a judgment above this seat — recommended for Main/integrator adjudication.

Showing command (receipt side): `grep -H met= .ufo/waves/round-55/c1/battery/*.out` → `m-ldaudit-writable.out:…met=True`, `m-ldaudit-foreign.out:…met=True`, `m-extra-in-tree.out:…met=True` vs preregistration lines above. Proposed fix (full text): `V3Freeze/proposed-amendment.md` — do NOT edit the frozen preregistration; archive the stale receipts, append an amendment note to the lesson, add a battery MANIFEST distinguishing kill/vector/control receipts.

### F2 — Informational: fleet rev must be pinned to reproduce C2 receipts

Both committed C2 receipts pin `fleet=6c4aba34…`; the fleet repo's HEAD is a moving jj working-copy commit (`4dd6935e…` by plain `rev-parse` minutes before the counter resolved `666bc1ef…` in run C). Unpinned reruns differ from the committed receipts in the `fleet=` line only (run C demonstrates exactly that). Reproduction recipe: pass `--fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b`.

## Residual risk and verification gaps

- The `.out` receipts do not embed the counter's digest; "copies used for every committed receipt" is established transitively (no counter byte changed since `9c60eae6`; worktree `cmp`-identical to the frozen blobs). A measurement run from an out-of-git modified copy would be unobservable — no evidence of that exists.
- C1 was not re-run (not among this seat's four checks; ~20 s + archive/model downloads + llama-server starts). C1 receipts were audited for tip fields, leg lines and roster consistency only.
- The battery mutant tips are fixture-clone commits absent from the lane repo, so their descent from `9c60eae6` could not be verified from the lane alone; the driver's `reset --hard FREEZE` before each mutant supports it.
- `m-text-flip`'s kill relies on offset `-0x3000` in `libggml-rpc.so` staying unreached at runtime (`run-battery.py:31-36`); host/load-order changes could weaken that kill — battery design belongs to the builder/integrator seats, flagged here only as a residual.

## Evidence copies (sha256-verified against the lane files)

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/V3Freeze/`: `base.c1.out` `3d6736a3…`, `base.c2.out` `d6a6f550…`, `c1-build.out` `4f8f277b…`, `c2-build.out` `bc59e5e1…`, `battery-{control,m-ldpreload,m-text-flip,m-member-flip,m-ldaudit-foreign,m-ldaudit-writable,m-extra-in-tree}.out`, `run-battery.py` `49a57a15…`, `rerun-c2-tip9c60eae-fleet6c4aba34.out` `bc59e5e1…`, `rerun-c2-tip3a600d2f-fleet6c4aba34.out` `d6a6f550…`, `rerun-c2-tip9c60eae-fleetHEAD.out` `8c42f44b…`, `rerun-diffs.txt` `1cf010e1…`, `proposed-amendment.md`.
