# X7BatteryReplay — round 55 C1 kill battery, independent replay

**Verdict: zero receipt divergence — the control and all four mutants reproduce
line-for-line in my own clone with identical verdicts and exit codes; but the
battery's `m-text-flip` "code leg" mutant does not exercise the counter's own
`/proc/<pid>/mem` comparison (its flipped byte lies outside every LOAD segment),
so the battery carries no kill for the mechanism the C1 predicate is built on.**

Measured at lane tip `8abadfed` (counter `tools/round54-replay-code-audit.py`
sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` = the
preregistered value). Frozen artifacts (`c1/battery/*.out`, the counter,
`preregistration.json`) were read only; nothing in the lane was edited.

## Method

Scratch `S=/fast/scratch/hyaku/kama-r55/w1/X7BatteryReplay`. One live clone:
`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`,
`git -C $S/lane rev-parse --show-toplevel` → `$S/lane` (asserted in every script
before any commit). The L1's harness was **not** run (it writes the L1's
receipts); its `MUTANTS` patch table was loaded with `importlib` (`main()` is
`__main__`-guarded) so the mutants are byte-identical, and all clone/commit/run/
compare logic is mine (`out/X7BatteryReplay/scripts/replay-battery.py`).

Per mutant: `git reset --hard 9c60eae6…`, apply exactly one patch to
`tools/kama-llamacpp-live.py`, `git -C $S/lane -c user.name=fx -c user.email=fx@invalid
commit`, then the frozen counter:

```
python3 <lane>/tools/round54-replay-code-audit.py --repo $S/lane --tip <fixture commit> \
        --scratch $S/run-<name> --out $O/<name>.out
```

All git/counter calls run with inherited `GIT_*` stripped.

## Reproduction result — `divergence-report.txt`, exit 0

| mutant | leg | my exit | my verdict line (line 2) | L1 receipt |
|---|---|---|---|---|
| `control` (freeze tip) | all | **0** | `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 … rehash=0 met=True` | identical |
| `m-ldpreload` | envnames | **1** | `… envnames=0/3 … met=False` | identical |
| `m-text-flip` | code | **1** | `bind=0 sealed=1 code=0 … coderuns=0/3 … rehash=3 met=False` | identical |
| `m-member-flip` | rehash | **1** | `… rehash=3 met=False` | identical |
| `m-ldaudit-foreign` | hostlibs | **0** | `… 6 env names … hostlibs=3/3 … rehash=0 met=True` | identical |

`compare.py` normalizes only run-varying values (`pid`, `port`, `inode`, nonce,
`rnd`-suffixed tmpdir, `dev`, whole-file digests, fixture `tip=`) and then
compares: 24/24, 24/24, 48/48, 48/48, 24/24 lines; **`verdict divergences: 0`,
`details identical after normalization`** for all five. My `control.out` is also
identical (normalized) to `measured/c1-build.out` — the freeze tip still prints
`met=True` in my environment.

L1 receipt bytes were unchanged during my run (sha256 of all five match my
snapshot `out/X7BatteryReplay/l1-receipts-cited/`; all hashes and the counter/
archive identity in `evidence-identity.txt`). The two stale receipts
present when I started (`m-ldaudit-writable.out`, `m-extra-in-tree.out`, tips
`23dc15da…`/`312530a9…`, not commits in the lane, no `MUTANTS` entry) were
removed by the L1 in `c2c05e30` while I was measuring; the on-disk set now
matches what the harness can produce.

## Defect 1 (operability) — `m-text-flip` never exercises the counter's own memory read

`c1/battery/run-battery.py:32-40` states the intended mechanism: *"the server
maps the flipped content, the counter's /proc/&lt;pid&gt;/mem vs archive-member
compare fails. Offset -0x3000 verified live"*. That is false. The patch at
`run-battery.py:46,48` flips `size-0x3000` of `libggml-rpc.so` = file offset
**0x4b120**, inside `.strtab`:

```
$ readelf -lW <archive>/llama-b11909/libggml-rpc.so   # file size 0x4e120
   LOAD 0x0..0x11e40 [R  0x1000]
   LOAD 0x12000..0x31469 [R E]        <- the only executable extent
   LOAD 0x32000..0x3a6a0 [R  0x1000]
   LOAD 0x3b270..0x3c860 [RW 0x1000]
   -> 0x4b120 is inside NO LOAD segment; it is 59584 bytes past the last one
```

(archive `llama-b11909-bin-ubuntu-x64.tar.gz` sha256 `bf94332a…e695b`, downloaded
by me; `elf-offset-analysis.txt`). Live confirmation — a process that
`dlopen()`ed that library maps file offsets `0x0`, `0x12000`, `0x32000`,
`0x3b000`, `0x3c000` and nothing above `0x3d000`, so **the flipped byte is never
in the server's address space**. The counter only reads executable mapped
ranges (`tools/round54-replay-code-audit.py:494-541`), so its comparison at
`:540-541` cannot fire.

Measured, three independent ways:

1. **The receipt itself.** `code: mapped bytes … differ from the archive member`
   appears **0 times** in `c1/battery/m-text-flip.out` and 0 times in my
   reproduction, although the code leg does fail (`code=0/3`). Its 10 code
   problems per block are all the *replay's self-report* cross-check
   (`round54-replay-code-audit.py:757`, `:764`, `:766`) plus the rehash leg
   (`:777`): the whole-file digest the replay hashed differs from the archive
   member, which the counter then cross-checks. Nothing there reads memory.
2. **Discrimination.** In a scratch copy of the counter with the mem-compare
   branch (`:540-541`) deleted, the `m-text-flip` fixture yields a *completely
   identical* verdict (`disc-frozen-m-text-flip.out` vs
   `disc-nomemcmp-m-text-flip.out`: both `bind=0 sealed=1 code=0 … met=False`,
   normalized diff empty). The branch contributes nothing to this kill.
3. **Construction.** A "pure-memread" counter (replay-report cross-check and
   rehash leg removed, so its code evidence is *only* its own `/proc/<pid>/mem`
   read) is a **sound instrument** — on the unmutated freeze tip it prints
   `met=True`, exit 0 (`pure-memread-control.out`). On the `m-text-flip` fixture
   it prints `bind=0 sealed=1 **code=1 coderuns=3/3** … rehash=0 met=False`
   (`pure-memread-m-text-flip.out`): **the code leg passes.**

Positive control that the mechanism is fine and merely unexercised: flipping a
byte at **0x30000** (inside `.text`, exec LOAD `0x12000..0x31469`) produces
`code: mapped bytes 7f…-7f… (offset 00012000) of llama-b11909/libggml-rpc.so
differ from the archive member` ×6 (2 passes × 3 blocks) and kills `code`
(`coderuns=0/3`) both under the frozen counter (`probe-in-text.out`) and under
the pure-memread counter (`pure-memread-in-text.out`).

**Consequence.** C1's predicate leads with *"every executable mapping … whose
mapped bytes, read by the counter from /proc/&lt;pid&gt;/mem in each of two
passes that agree, equal that member's bytes in the counter's own download"*.
No battery mutant kills that clause: `m-text-flip` is invisible to it,
`m-member-flip` and `m-ldaudit-foreign` leave `code=1`, `m-ldpreload` leaves
`code=1`. A counter that lost its memory comparison entirely would still grade
this battery green (proof 2). This does **not** by itself trigger C1's kill rule
(no mutant that the harness grades as a kill prints `met=True`); it is an
evidence-coverage defect, and the same "vacuous kill rule" class the round-55
lesson mines.

For the record the parallel mutant is honest: `m-member-flip` flips `size-32` of
`libggml-cpu-zen4.so` = `0x182418`, also outside every LOAD segment (103255
bytes past the last), and the harness comment at `run-battery.py:71-75` says
exactly that — *"mapped pages unchanged, the observed path's file digest
changes"* — which is what the receipt shows (`code=1`, `rehash=3`).

## Defect 2 — the harness's leg attribution cannot distinguish a killed leg from a green one

`run-battery.py:140-141` decides the named leg failed by grepping:

```python
leg_failed = f"{leg} " in "\n".join(
    ln for ln in text.splitlines() if ln.startswith("detail: "))
```

Every *passing* leg also emits a `detail: <leg> bN: …` line (e.g.
`detail: code b1: 8 archive files (16 executable ranges) byte-equal …`), so the
grep is true for `code`, `envnames`, `rehash`, `bind`, `sealed`, `twopass`
whether they passed or failed. Applied to the delivered positive control
(all-green, `met=True`) the predicate reports `leg_failed=True` for all six
(`leg-attribution-check.out`, section 1). Applied to `m-ldpreload.out` with
`leg="code"` — where the summary says `code=1 coderuns=3/3`, i.e. the code leg
**passed** — it returns `True` and the harness would print
`leg=code … -> ok` (section 2). So `ok = rc == 1 and not met and leg_failed`
(`:142`) reduces in practice to `rc == 1 and not met`: the battery grades "the
counter failed", not "the named leg failed". The delivered verdicts happen to be
correct (each kill's summary line does show its named leg red), but the harness
does not verify it.

## Note 3 — prereg's mutant list is out of sync with the harness

`preregistration.json:44` names four mutants
`["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)",
"m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]` and `:43`
calls them *"each expected to fail the frozen counter with its named leg"*.
The harness's `MUTANTS` table has `m-ldpreload, m-text-flip, m-ldaudit-foreign,
m-member-flip`: `m-ldaudit-writable` is not implemented at all, `m-text-flip`
(the real code-leg mutant) is not named. With `:20` (*"falsified if … any
battery mutant prints met=True"*), `m-ldaudit-foreign` — a prereg-named mutant,
documented in the harness as `kind="vector"`, `run-battery.py:59` — prints
`met=True`, which I reproduce (exit 0). That is the L1's open ruling, not mine
to resolve; my replay supplies the independent exit codes it was missing.

## Note 4 — exit codes the receipts do not carry (Sc3Report's open item)

Recorded here as measured, `replay-summary.txt`: control **0**, `m-ldpreload`
**1**, `m-text-flip` **1**, `m-member-flip` **1**, `m-ldaudit-foreign` **0**.
All eight battery receipts record `met=` only; the harness prints its summary
(`run-battery.py:145-147`) to stdout and commits no summary file, so a reader
cannot re-derive the exits from the lane today.

## Note 5 — `rehash` wording

`round54-replay-code-audit.py:777-779` compares the on-disk digest against the
*archive* digest, not against a digest captured at observation time, so it fires
for a file modified **before** the observation as well, yet reports *"changed
after the observation"*. Observed for both flip mutants. The leg's effect matches
the predicate ("every observed archive path still hashes to its member"); only
the message is inaccurate.

## Proposed fix

`out/X7BatteryReplay/proposed-run-battery.patch` (full text also as
`fixed-run-battery.py`; validated against all five delivered receipts — graded
`False, True, True, True, False` exactly matching each summary line, and `False`
for every leg on the positive control). Two hunks:

1. `m-text-flip` flips **0x30000** (inside `.text`, exec LOAD
   `0x12000..0x31469`) instead of `size-0x3000`; comment states the real
   mechanism and the reason for the offset. Receipt evidence that the fixed
   mutant works: `probe-in-text.out` (`coderuns=0/3`, 6 mem-compare hits).
2. Replace the detail-line grep with `leg_failed(text, leg)`, reading the
   per-leg verdict from the receipt's summary line (line 2).

Prereg is frozen, so the `m-ldaudit-writable` / `m-text-flip` naming and the
`met=True` vector conflict are for the L1 to rule on, not for a patch here.

## Limits of this replay

Same host, same glibc 2.44, same archive; one full pass per mutant (the L1's own
`m-member-flip` comment records that its first attempt flipped only the first
glob hit and had to be repeated). Volatile fields differ from the L1's receipts
by design; nothing else does. Ports/pids/inodes are the counter's own.
`m-ldaudit-foreign`: glibc rejects the DSO before mapping it — `ld.so: object
'/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol:
la_version; ignored`, and libexpat is absent from `/proc/<pid>/maps`, so the
hostlibs leg stays unreachable for a non-root actor, as documented.

Tooling: nothing installed or upgraded; no `pacman`, no service started or left
running (all my runs tore their own servers down — `teardown=1` in every
receipt; the `llama-server` processes visible on the host belong to peer
`J5EnvNames`' scratch, not mine). Two `__pycache__` directories were created in
`.ufo/waves/round-55/c1/battery/` as a side effect of importing the harness
module and were removed immediately; `git status --porcelain
.ufo/waves/round-55/c1/` is empty.
