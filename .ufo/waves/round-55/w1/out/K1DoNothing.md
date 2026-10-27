# K1DoNothing — round-55 do-nothing control audit (C1/C2 causal separability)

**Verdict: PASS — both base controls reproduce red on my own clones with the frozen counters, and each claim's work alone flips exactly its own counter (S511 alone → C1 green/C2 red; superseded row alone → C2 green/C1 red). No defect found; the freeze's causal-separability claim is confirmed.**

Seat: K1DoNothing (leaf, no subagents). Frozen counters taken byte-exact from the freeze commit
`9c60eae6f7ed84f7da93d219a406aadc30958c6c` via `git show` (lane read-only) into scratch; sha256 verified
against the preregistration (`counter_sha256`):

```
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  round54-replay-code-audit.py   (C1, matches preregistration C1.counter_sha256)
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  round54-cited-path-check.py    (C2, matches preregistration C2.counter_sha256)
```

(copy: `out/K1DoNothing/frozen-counter-sha256.txt`). Clone: one `git clone --shared
/home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, checked out at base
`3a600d2f729828419aaea34cc402c8b0d20fb720`; `git rev-parse --show-toplevel` asserted equal to `$S/lane`
before every fixture mutation; fixture commits used `-c user.name=fx -c user.email=fx@invalid`; my own git
calls ran with the host's inherited `GIT_*` names stripped (`env -u GIT_DIR -u GIT_CONFIG_COUNT ...`;
host only exports GIT_EDITOR/GIT_PAGER/GIT_TERMINAL_PROMPT). Counters were never edited.

## 1. Base controls reproduced (red)

Commands (receipts in `out/K1DoNothing/`):

```
python3 $S/frozen/round54-replay-code-audit.py --repo $S/lane --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 --scratch $S/c1s-base --out out/K1DoNothing/base.c1.out   # exit 1
python3 $S/frozen/round54-cited-path-check.py --repo $S/lane --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 --scratch $S/c2s-base --out out/K1DoNothing/base.c2.out   # exit 1
```

- C1: `C1_BASE_EXIT=1`; leg line `bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False` — **byte-identical** to the committed `.ufo/waves/round-55/controls/base.c1.out` leg line; per-receipt `own_code` 8-library list also identical (md5 `11ef8f46…` both). Every leg green except newrow, as preregistered.
- C2: `C2_BASE_EXIT=1`; leg line `fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=1 met=False` — identical to committed `controls/base.c2.out` except the fleet rev (`fleet=666bc1ef…` here vs `fleet=6c4aba34…` in the committed receipt; fleet HEAD has since moved, which is expected and does not touch the lane leg numbers). Dropped citation line identical: ``detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)``.

The base controls genuinely measure the base tree with the frozen counters: the do-nothing tree fails
exactly on the two preregistered legs (C1 `newrow=0`, C2 `dropped=1`) and on nothing else.

## 2. Causal separability — each change alone flips only its own counter

Fixture A (S511 only): inserted the exact S511 row from the freeze after the S510 row in
`corpus/SOURCES.md`; clone diff vs base = `1 file changed, 1 insertion(+)`, the single added row
(copy: `out/K1DoNothing/fixture-s511.row.txt`). Committed as `3aee3e07a3ed2826bc32c03252f9ee4a982c8385`
(`out/K1DoNothing/tip-a.txt`).

Fixture B (superseded ledger row only): appended the freeze's exact 6-line block (5 comment lines + the
`SCORECARD.md … superseded … corpus/lessons/round-53-verifier-spotcheck.md` row) to
`registry/cited-path-corrections.tsv`; block sha256 `d4830410…` equals the freeze ledger tail's; clone diff
vs base = `1 file changed, 6 insertions(+)`. Committed as `37bb15d11d2b9fa2227fb93adb558106291ef319`
(`out/K1DoNothing/tip-b.txt`).

| tree | C1 (replay-code-audit) | C2 (cited-path-check) |
|---|---|---|
| base `3a600d2f` | exit 1, `newrow=0`, met=False | exit 1, `dropped=1`, met=False |
| base + S511 `3aee3e07` | **exit 0, `newrow=1`, met=True** (`newrow: 1 rows new since base; 1 name the git environment doc: ['| S511 |']`) | **exit 1, `dropped=1`, met=False** (unchanged; same dropped line as base) |
| base + superseded `37bb15d1` | **exit 1, `newrow=0`, met=False** (unchanged) | **exit 0, `dropped=0`, `fixture=1 lane=1 scenarios=15/15`, met=True** |

Receipts: `out/K1DoNothing/expA.c1.out`, `expA.c2.out`, `expB.c1.out`, `expB.c2.out`.

Result: S511 alone flips C1 to green with every other C1 leg already green on the base tree; C2 is
indifferent to it. The superseded row alone flips C2 to green (fixture scenarios still 15/15, lane leg
`dropped=0` because the row discloses the round-52→round-53 re-point per
`tools/round54-cited-path-check.py:461-479` — token not cited at tip, replacement cited and resolving at
tip, token cited in the surface at BASE `0b75a84c` per `git show 0b75a84c:SCORECARD.md` line 18 and
resolving there, row not in the BASE ledger so the `base_citelines` clause applies); C1 is indifferent to
it. This matches the preregistration `separability` paragraph: the claims are causally separable —
"C1's SOURCES row is not a C2 surface; C2 touches no C1 path."

## 3. Hygiene / limits observed

- No llama-server leftovers from my runs (each receipt `teardown: invoker SIGKILLed … alive [] port refuses ok`; `pgrep -af llama-server` shows only sibling seat J5EnvNames's own held server in its own scratch — not mine, left running).
- C1 runs each re-download the archive/model per the counter's design (~17 s/run; 3 C1 runs total).
- Receipts' volatile fields (pids, ports, inodes, nonces, fleet rev) differ from the committed controls by design; all preregistered-comparable fields agree byte-for-byte.
- No defects to report: counters, preregistration and controls treated as frozen throughout; no lane file was edited in place.

Evidence index (all under `kama-shokunin/.ufo/waves/round-55/w1/out/K1DoNothing/`): `base.c1.out`,
`base.c2.out`, `expA.c1.out`, `expA.c2.out`, `expB.c1.out`, `expB.c2.out`, `tip-a.txt`, `tip-b.txt`,
`fixture-s511.row.txt`, `fixture-superseded.block.txt`, `frozen-counter-sha256.txt`.
