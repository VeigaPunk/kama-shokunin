# X1Rerun — Independent C1 measurement, round-55 lane kama (operability)

**VERDICT: CONFIRMED — my independent re-run of the frozen C1 counter reproduces the lane's committed build measurement and base control exactly (all must-agree fields byte-identical after normalising the by-design-volatile pids/ports/inodes/nonces); build tip 9c60eae6 → `met=True` exit 0, base tip 3a600d2f → `newrow=0 met=False` exit 1, matching the frozen preregistration target on both. Separately observed: the C1 kill rule as frozen is NOT discharged by the committed battery — two of the four mutants the preregistration names print `met=True` (see Finding F1).**

---

## 1. Scope and what was run

Seat: `X1Rerun`. Independent C1 measurement only. I did not run the L1's battery harness
(`run-battery.py` — it writes into the lane's `c1/battery/` dir, which is not mine), did not
touch the lane's git index or jj state, and did not write into `measured/`, `controls/` or
`c1/battery/`.

All deliverables: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/`
(this report: `.ufo/waves/round-55/w1/out/X1Rerun.md`).

Scratch (operator directive): `S=/fast/scratch/hyaku/kama-r55/w1/X1Rerun`, `TMPDIR="$S"`,
one live clone `$S/lane` (`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`),
removed at the end (§7). The counter itself was executed from the lane's frozen path and
never edited in place.

### Counter identity (frozen, unchanged)

```
$ sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  ...
```
matches `preregistration.json` `claims.C1.counter_sha256` (line 18) exactly.
The counter bytes in my clone at the build tip are the same file:
`git -C $S/lane show 9c60eae6:tools/round54-replay-code-audit.py | sha256sum` →
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`.
(The copy at the base tip is the round-54 version, `15fef4d2f2985508616ce9b9ca4927459702085ee18abed644580478e50c49e9`,
with `BASE = 0b75a84c…` and `GITDOC_URL = git-scm.com/docs/git#…codeGITDIRcode` — the round-55
delta is exactly `BASE` re-frozen to `3a600d2f…`, the source row re-pointed at S511, and the
`clean_env()` GIT_* strip added; `git diff 3a600d2f 9c60eae6 -- tools/round54-replay-code-audit.py`.)
The kill rule's last clause ("counter bytes at measurement differ from counter_sha256") is therefore not triggered.

---

## 2. Build measurement (independent re-run)

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py \
    --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
    --scratch $S/run-final-build \
    --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-build.out
EXIT=0
```
Receipt `…/w1/out/X1Rerun/c1-build.out`, exit code `…/w1/out/X1Rerun/c1-build.exit` (`EXIT=0`):

```
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
```

Matches the preregistration target verbatim (`preregistration.json:19`):
`bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0`.

## 3. Base control (independent re-run at the round-54 tip)

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py \
    --repo $S/lane --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 \
    --scratch $S/run-final-base \
    --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-base.out
EXIT=1
```
Receipt `…/w1/out/X1Rerun/c1-base.out`, exit code `…/w1/out/X1Rerun/c1-base.exit` (`EXIT=1`):

```
tip=3a600d2f729828419aaea34cc402c8b0d20fb720
bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False
```

`newrow=0`, `met=False`, exit 1 — the do-nothing control is red, as the preregistration
requires (`preregistration.json:19`, controls receipt `.ufo/waves/round-55/controls/base.c1.out`).
This is the important direction: the base tree contains none of the round-55 work, so the
newrow leg (the only leg that can differ) is 0 and the claim does not fire on the base.

## 4. Field-by-field comparison

Full machine-readable table: `…/w1/out/X1Rerun/field-comparison.txt`; comparer:
`…/w1/out/X1Rerun/cmp.py` (normalises only pids, ports, inodes, nonces and the memfd
dev:inode; every other character must match).

Comparisons run:
1. mine-build vs lane `measured/c1-build.out`
2. mine-base vs lane `controls/base.c1.out`
3. mine-build vs mine-build-rerun (a second independent build run)

### Fields that MUST agree — all agree, in all three comparisons

| field | value (identical in all four receipts) |
|---|---|
| leg line, build | `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True` |
| leg line, base | `bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False` |
| **the 8 archive library names** (`own_code`) | `libggml-base.so.0.27.0`, `libggml-cpu-zen4.so`, `libggml-rpc.so`, `libggml.so.0.27.0`, `libllama-common.so.0.7.0`, `libllama-server-impl.so`, `libllama.so.0.7.0`, `libmtmd.so.0.7.0` |
| **range counts** | `8 archive files (16 executable ranges)` and `twopass … byte-identical over 16 range reads` — 16 in every code/twopass detail line of all three runs |
| **host count** | `13 root-owned host files` in every code detail line of all receipts |
| counter vocabulary | `512 tokens from its own download` |
| counter archive | `its own download, read once, frozen digest` |
| envnames b1/b2/b3 | `5 environment variable names recorded, none of LD_PRELOAD/DYLD_INSERT_LIBRARIES` |
| rehash b1/b2/b3 | `8 observed archive paths re-stat'ed and re-hashed after the replay exited, inode and digest unchanged` |
| teardown | `invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok` |
| newrow, build | `2 rows new since base; 1 name the git environment doc: ['| S511 |']` |
| newrow, base | `0 rows new since base; 0 name the git environment doc: []` |
| tip line | `tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c` (build) / `tip=3a600d2f729828419aaea34cc402c8b0d20fb720` (base) |

Comparer output for comparison 1 (mine-build vs lane measured): `detail keys equal set: True  differing keys: 0`,
`whole receipt (normalised) equal: True`. Same for comparison 2 and comparison 3.

### Fields that MAY differ — and do, by design

Only the `bind bN` and `sealed bN` detail lines, and only in: `pid <N>`, `port <N>`,
`mapping inode <N>`, the witness `nonce '<random hex>'`, and the memfd `dev:inode`
`00:01:<N>`. Raw (unnormalised) diff of mine-build vs the lane receipt:

```
9,10c9,10
< detail: bind b1: pid 2444950 port 44005 … mapping dev 103:05 inode 1553737974 recorded, nonce 'kama witness ef1abe56df36c80f' round-tripped
< detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:225061 seals 15 …
---
> detail: bind b1: pid 1188271 port 35845 … mapping dev 103:05 inode 2080399371 recorded, nonce 'kama witness b6a8c8e9d2e13188' round-tripped
> detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:220793 seals 15 …
```
…and the same for `b2`/`b3`. Six changed line pairs in each of the two comparisons, every one a
bind/sealed line, nothing else. `seals 15` and `dev 103:05` are identical in every receipt.

### Independent corroboration of the counts the receipt asserts

* The 13 host-library basenames in the counter's frozen `HOST_LIBS` set
  (`tools/round54-replay-code-audit.py:138-147`) all resolve on this host to root-owned
  `/usr/lib/<name>` files — verified by `find`/`stat`:
  `ld-linux-x86-64.so.2, libbrotlicommon.so.1.2.0, libbrotlidec.so.1.2.0,
  libbrotlienc.so.1.2.0, libcrypto.so.3, libc.so.6, libgcc_s.so.1, libgomp.so.1.0.0,
  libm.so.6, libssl.so.3, libstdc++.so.6.0.36, libz.so.1.3.2, libzstd.so.1.5.7` — 13/13 `owner=root`.
* The 8 archive library names are all present in the host's b11909 install
  (`/home/vgpnk/.local/opt/llama-b11909/`, read-only): `libggml-base.so.0.27.0`,
  `libggml-cpu-zen4.so`, `libggml-rpc.so`, `libggml.so.0.27.0`, `libllama-common.so.0.7.0`,
  `libllama-server-impl.so`, `libllama.so.0.7.0`, `libmtmd.so.0.7.0`.
* The `newrow` leg's arithmetic re-derived independently from the clone:
  S-rows at base `3a600d2f` = 251, at build `9c60eae6` = 252, set difference = **2**
  (`| S510 |` — its `used-by` cell was re-pointed old→new, so the row text differs — and
  `| S511 |`), of which **1** contains the frozen `GITDOC_URL`
  (`git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`). The receipt's
  `2 rows new since base; 1 name the git environment doc: ['| S511 |']` is therefore exactly right,
  including the fact that the S510 re-point counts as a changed row.

## 5. Extra falsification probes I ran (beyond the assigned pair)

**(a) Reproducibility.** A second independent build run (`…/w1/out/X1Rerun/c1-build-rerun.out`,
exit 0, `met=True`) is byte-identical to the first after the same normalisation
(`whole receipt (normalised) equal: True`, `differing keys: 0`). The measurement is stable, not
a one-off.

**(b) The round-55 `clean_env` delta actually holds.** I re-ran the build measurement with a
poisoned environment:
```
$ GIT_DIR=/tmp/nonexistent-foreign-repo GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/tmp/evil-hooks \
  python3 tools/round54-replay-code-audit.py --repo $S/lane --tip 9c60eae6 … \
  --out …/w1/out/X1Rerun/c1-poison-gitenv.out
EXIT=0
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c
bind=1 sealed=1 code=1 teardown=1 newrow=1 … met=True
detail: newrow: 2 rows new since base; 1 name the git environment doc: ['| S511 |']
```
The injected `GIT_DIR`/`GIT_CONFIG_COUNT`/`core.hooksPath` did **not** redirect the counter's
`git rev-parse`/`archive`/`show` calls: the tip resolved to the real commit, the archive was
the real tree, and `newrow` still read 2/1. This exercises the round-55 delta the freeze
claims (S510/S511) and it is green.

## 6. Finding F1 — the frozen C1 kill rule is not discharged by the committed battery

This is a defect in the **frozen** artefacts, not something I may fix in place, so it is
reported, not repaired.

**Where.** `.ufo/waves/round-55/preregistration.json:44` (the `c1_kill_battery` control) names
four mutants:
```
"mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)",
            "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]
```
and `preregistration.json:20` (C1 `kill_rule`) says the claim "is falsified if … **any battery
mutant prints met=True**"; `:19` (target) requires "kill battery: each named mutant receipt
prints met=False (exit 1) with its named leg failing".

**What the committed receipts show.** In `.ufo/waves/round-55/c1/battery/`:

| receipt | leg line | named by the freeze? | prints met=True? |
|---|---|---|---|
| `control.out:2` | `… newrow=1 … met=True` | (positive control, expected True) | n/a |
| `m-ldpreload.out:2` | `… envnames=0/3 … met=False` | yes | no — kills |
| `m-text-flip.out:2` | `bind=0 … code=0 coderuns=0/3 … rehash=3 met=False` | **no** | no — kills |
| `m-member-flip.out:2` | `… rehash=3 met=False` | yes | no — kills |
| `m-ldaudit-writable.out:2` | `… envnames=3/3 hostlibs=3/3 … met=True` | **yes** | **YES** |
| `m-ldaudit-foreign.out:2` | `… hostlibs=3/3 … met=True` | **yes** | **YES** |
| `m-extra-in-tree.out:2` | `… met=True` | no | **YES** |

So two of the four mutants the freeze names print `met=True`, and the kill rule as frozen
fires on its own terms. Two further mismatches compound it:

* The landed runner builds a **different set** than the freeze names:
  `.ufo/waves/round-55/c1/battery/run-battery.py:23-87` defines `m-ldpreload` (:26),
  `m-text-flip` (:38), `m-ldaudit-foreign` (:57) and `m-member-flip` (:69) — it does **not**
  build `m-ldaudit-writable` at all, and it replaces the freeze's "code leg" mutant
  `m-ldaudit-writable` with `m-text-flip`.
* `m-ldaudit-foreign` is reclassified in the runner as `kind="vector"` with the comment
  "expect met=True: the LD_AUDIT vector is void on this glibc" (`run-battery.py:52-62`) and is
  scored `ok = rc == 0 and met` (`run-battery.py:137-138`) — i.e. the harness scores a *passing*
  mutant as success. The commit that landed the battery describes it as
  "kill battery green (3 live kills + 1 vector analysis)" (`git log -1 8abadfed`), but the
  frozen text says "any battery mutant prints met=True" falsifies the claim.

**Command that shows it** (read-only):
```
$ sed -n '2p' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
$ sed -n '2p' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
$ grep -n 'mutants' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/preregistration.json
44:      "mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"],
```
All six battery fixture commits (`585a6cb0…`, `23dc15da…`, `aa3c47cd…`, `a12e2c0f…`,
`ba085a8b…`, `312530a9…`) are **absent** from the lane repo (`git cat-file -e <sha>^{commit}`
fails for each) — they lived in the battery's scratch clone, which the harness deletes
(`run-battery.py:94` at start-up and `:147` at the end, `shutil.rmtree(SCRATCH, ignore_errors=True)`).
So the receipts cannot be re-derived from the lane as committed; the battery is currently a set
of unfalsifiable-by-replay receipts.

**Proposed fix (for the L1; I did not apply it — the preregistration and counters are frozen).**
Two coherent options; the lane must pick one and record it, because as committed the frozen
kill rule is contradicted by the frozen battery's own receipts.

*Option 1 — make the text match the artefacts (freeze amendment, honest scoping).* Amend
`preregistration.json:44` and `:19-20` so the battery names the mutants that are actually
built and killed (`m-ldpreload`, `m-text-flip`, `m-member-flip`), states that
`m-ldaudit-foreign` and `m-ldaudit-writable` are **vector analyses with expected `met=True`**
(the LD_AUDIT vector is void on this glibc; a root-owned foreign-library mapping is not
reachable as a same-uid mutant), and rewrites the kill rule to "any **kill-class** battery
mutant prints met=True" so the vector receipts cannot be read as survivors. Also delete the
orphan `m-extra-in-tree.out` (no `MUTANTS` entry, not named by the freeze) or fold it into the
vector class.

*Option 2 — make the artefacts match the text (re-freeze the battery).* Build a mutant that
actually kills the freeze's "code leg" (`m-ldaudit-writable` is what the freeze named; the
harness instead built `m-text-flip`) and a hostlibs-leg mutant that trips `hostlibs`, then
replace `m-ldaudit-writable.out` and `m-ldaudit-foreign.out` with receipts that print
`met=False` and name their leg, keeping `run-battery.py:137-138` scoring `ok = rc == 1 and
not met and leg_failed` for every entry.

Under either option, the counter bytes stay untouched (`counter_sha256` still matches) and the
base control and build measurement are unaffected — my measurements in §2-§4 stand either way.

**Also noted for the same freeze (lower severity).** `preregistration.json:44` names
`m-ldaudit-writable` as the "code leg" mutant, but the runner's code-leg mutant is
`m-text-flip`; and the receipts `m-ldaudit-writable.out` and `m-ldaudit-foreign.out` carry
`envnames` detail lines showing **6** environment variable names where the control and the
other receipts show **5** (`m-ldpreload.out`'s envnames line is the failure line
`env: server environment carries LD_PRELOAD`, `m-extra-in-tree.out` shows 5) — i.e. those two
were built from an earlier harness revision and are stale relative to the committed
`run-battery.py`. The freeze text and the battery harness disagree about which mutants exist;
the fix must settle that list in one place.

## 7. Housekeeping

* No tool was installed or upgraded in this wave (nothing in `~/.omp/agent/RULES.md` applied):
  the frozen counter, `git`, `python3`, `find`/`stat` and `sha256sum` sufficed. No `pacman`,
  `uv`, `npm` or `cargo` transaction was run.
* No tracer was wrapped around the counter (`strace`/`ltrace` never used).
* No service was started, stopped or restarted by me. The counter starts and tears down its own
  `llama-server` on loopback ports; after all my runs `pgrep -af llama-server` shows only two
  processes belonging to another seat's scratch (`J5EnvNames`), and `pgrep -af X1Rerun` returns
  nothing — no leftovers of mine.
* Scratch removed at the end of the run: `rm -rf /fast/scratch/hyaku/kama-r55/w1/X1Rerun`
  (the clone and all run directories). No `/tmp` path is cited as evidence.
* The lane was read-only to me: `git -C <lane> status --porcelain` shows only other seats'
  untracked `w1/out/*` entries; I made no commit, no index change and no jj change anywhere.

---

## Evidence index (all paths absolute)

Reports / deliverables:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-build.out` — my build measurement (exit 0, `met=True`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-build.exit`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-base.out` — my base control (exit 1, `newrow=0 met=False`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-base.exit`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-build-rerun.out` — second independent build run (exit 0)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-poison-gitenv.out` — build run with poisoned `GIT_DIR`/`GIT_CONFIG_COUNT` (exit 0, `met=True`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/c1-build.stdout`, `…/c1-base.stdout` — full stdout of the two assigned runs
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/field-comparison.txt` — the field-by-field table
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X1Rerun/cmp.py` — the comparer used

Lane artefacts read (not written):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/preregistration.json` (lines 18-20, 31-32, 43-45)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/measured/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/controls/base.c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery/{control,m-ldpreload,m-text-flip,m-member-flip,m-ldaudit-writable,m-ldaudit-foreign,m-extra-in-tree}.out`, `run-battery.py:23-87,135-138`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py:130,138-147,160-179,466-560,876-972`
