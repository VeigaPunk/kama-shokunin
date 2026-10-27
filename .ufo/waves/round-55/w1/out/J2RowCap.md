# J2RowCap — ROW_CAP leg, static + unit probe (round 55, lane kama)

**Verdict: both clauses of the ROW_CAP leg (C1 leg iii) are implemented correctly and both can fail — proven on synthetic maps rows with a fake mem fd and again on a real kernel child — but at the frozen b11909 configuration NEITHER branch can ever fire, so the frozen C1 measurement carries no evidence for either; a guard-deleting mutant would still print met=True. No defect in the frozen counter's logic; one unbounded-cost gap (per-row cap, no total budget) and one kill-battery coverage gap.**

Counter under test: `tools/round54-replay-code-audit.py`, sha256
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` — matches the
preregistration's `claims.C1.counter_sha256` and both frozen commits
(`9c60eae6` and `8abadfed`; `.ufo/waves/round-55/preregistration.json:16`).
All runs used my own `git clone --shared` at
`/fast/scratch/hyaku/kama-r55/w1/J2RowCap/lane` (toplevel verified = the clone).
The lane was read only; the counter was never edited in place.

## The clauses, at their frozen line numbers

`tools/round54-replay-code-audit.py:145` — `ROW_CAP = 64 << 20`;
`tools/round54-replay-code-audit.py:519-536` inside `code_observe`:

```
519  probs.append(f"code: {path} is not a regular member of the archive")   # member check
521  lo, hi = (int(v, 16) for v in f[0].split("-"))
522  off = int(f[2], 16)
523  length = hi - lo
524  if length > ROW_CAP:                                    # CLAUSE A
525      probs.append(f"code: maps row {f[0]} of {member} is {length} bytes; not read")
526      continue
527  if off + length > len(data):                            # CLAUSE B
528      probs.append(f"code: maps row {f[0]} of {member} extends past the member "
529                   f"({off + length} > {len(data)} bytes)")
530      continue
531  want = data[off:off + length]
533  got = os.pread(mem, length, lo)
```

Both are checked *before* the `os.pread`, so a refused row is never read — the
"at most 64 MiB" and "not zero-padded" wording is honoured literally, not by
truncating a read.

## Harness

`.ufo/waves/round-55/w1/out/J2RowCap/j2-rowcap-unit-harness.py` (receipt:
`j2-rowcap-unit-harness.json`). It imports the frozen counter by path
(`importlib.util.spec_from_file_location`) — no edit, no copy of its logic — and
shadows only `mod.open` and `mod.os` so that `/proc/<pid>/maps` is served from a
synthetic row list and `/proc/<pid>/mem` from a `FakeMem` pread store.

```
S=/fast/scratch/hyaku/kama-r55/w1/J2RowCap; export TMPDIR="$S"
python3 .ufo/waves/round-55/w1/out/J2RowCap/j2-rowcap-unit-harness.py \
        --counter "$S/lane/tools/round54-replay-code-audit.py" --real-kernel \
        --receipt .ufo/waves/round-55/w1/out/J2RowCap/j2-rowcap-unit-harness.json
-> 42/42 harness checks passed; 0/0 defect probes reproduced   (exit 0)
```

### Clause A can fail (synthetic, fake mem fd)

```
[PASS] clause-A: oversized row reported as a problem
       :: hit=['code: maps row 7f4001000000-7f4005001000 of libggml.so.0.27.0 is 67112960 bytes; not read']
[PASS] clause-A: no pread longer than ROW_CAP :: calls=[4 x 4096] ROW_CAP=67108864
[PASS] clause-A: oversized row not counted as compared :: ranges=4
[PASS] clause-A: code leg fails
```

### Clause B can fail (synthetic, fake mem fd)

```
[PASS] clause-B: past-the-end row reported as a problem
       :: hit=['code: maps row 7f4002000000-7f4002001000 of libggml.so.0.27.0 extends past the member (10240 > 8192 bytes)']
[PASS] clause-B: the past-the-end row was not read :: pread offsets=[4 good rows only]
[PASS] clause-B: past-the-end row not counted as compared :: ranges=4
[PASS] clause-B: not zero-padded into a byte-equal verdict
[PASS] clause-B: code leg fails
```

### Both clauses at their exact boundaries (no off-by-one)

```
[PASS] boundary-A: a row of exactly ROW_CAP bytes is READ (the cap is inclusive)
       :: preads at the cap row=[(..., 67108864)]
[PASS] boundary-A: a row of ROW_CAP + 1 bytes is refused and not read
[PASS] boundary-B: a row ending EXACTLY at the member's end is allowed and compared :: ranges=5
[PASS] boundary-B: a row ending ONE byte past the member's end is refused and not read
       :: ['... extends past the member (8193 > 8192 bytes)']
```

### Both clauses on the real kernel (no fake mem fd)

A child process mmaps real files through libc `mmap` (python's `mmap` refuses a
length past EOF). Real `/proc/<pid>/maps` + real `/proc/<pid>/mem`:

```
[PASS] real-kernel: the real >ROW_CAP row is refused as a problem
       :: 'code: maps row 7f993be00000-7f993fe01000 of libggml-cpu-huge.so is 67112960 bytes; not read'
[PASS] real-kernel: the real past-EOF row is refused as a problem
       :: 'code: maps row ... of libggml-past-eof.so extends past the member (8192 > 4096 bytes)'
       :: 'code: maps row ... of libggml-partial-eof.so extends past the member (8192 > 6144 bytes)'
[PASS] real-kernel: the four legitimate real mappings were read and accepted
```

### The guards are load-bearing (four mutants, written to scratch only)

```
[PASS] mutant-M1  without the ROW_CAP guard the oversized row IS read
                  :: oversized preads=[(..., 67112960)]     # 64 MiB+4 KiB allocated
[PASS] mutant-M2  without the past-the-end guard the row IS read
[PASS] mutant-M3  a zero-padding "fix" ACCEPTS the past-the-end row
                  :: accepted snaps=[...] code problems=[]
[PASS] mutant-M4  with a small member, the oversized row is still refused without
                  the ROW_CAP guard (clause B catches it, different message)
```

M3 is the clause's own hazard demonstrated end-to-end: replacing the refusal with
`data[off:off+length].ljust(length, b"\0")` makes the row byte-equal **because the
kernel really does zero-fill the tail past EOF**. Verified independently on this
host: a 6144-byte file mapped over 8192 bytes reads back `b"B"*2048 + b"\0"*2048`
for its last page, and a 4096-byte file mapped over 8192 raises `EIO [5]` on the
page past EOF. A zero-padding implementation would therefore accept executable
bytes that are not member bytes — exactly what clause B forbids. The frozen
counter does not do this.

## Finding 1 (operability, material): both branches are DEAD at the frozen configuration

The frozen measurement (`measured/c1-build.out`) prints `code=1 … met=True` and
`newerow=1`, but neither branch of leg (iii) can fire, because the counter can only
read an executable maps row that names a *regular member of its own archive*
(`:517-520`), and for the frozen release that is a closed set with known geometry.

Proof in the harness (`scenario_frozen_geometry`), computed from the release tarball
the counter itself downloads, `/home/vgpnk/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz`
(51 regular members):

```
[PASS] frozen-geometry: CLAUSE A is DEAD — the largest executable row any frozen member can
       produce is 6766592 bytes (6.453 MiB) in llama-b11909/llama-connect; ROW_CAP = 67108864
[PASS] frozen-geometry: CLAUSE B is DEAD — clause-B hits over all frozen members: []
```

* **Clause A** needs a row > 64 MiB. The longest executable `PT_LOAD` page-rounded
  span in the entire release is 6.45 MiB — a 10× margin. It cannot fire.
* **Clause B** needs `off + length > len(member)`. For all 51 members every
  executable `PT_LOAD`'s page-rounded end lies inside the file. It cannot fire.

Independently confirmed against the real captured server maps from round 53
(`.ufo/waves/round-53/w1/out/K1Cheat/maps-during-hold.txt`, 24 `r-xp` rows): for
the 8 archive-tree rows, `off + len(hi-lo)` vs the member size is
`0x125000+0x15000<0x182438`, `0x2e6000+0xb9000<0x5080a0`, … — no row trips either
clause. Largest real executable row: 3,854,336 bytes = 3.68 MiB (`libcrypto.so.3`,
a host file); largest archive-tree row 2.69 MiB.

**Consequence for the claim:** a mutant that deleted *either* guard would still
print `met=True` on the frozen build. The C1 kill battery cannot see the
difference. The only thing standing behind leg (iii) in the frozen evidence is the
source text plus this report's harness.

**Consequence for the kill battery — `grep` over the frozen receipts:**

```
$ cd .ufo/waves/round-55/c1/battery
$ grep -l "not read\|extends past the member" *.out
(no match in control.out, m-ldpreload.out, m-text-flip.out, m-ldaudit-foreign.out, m-member-flip.out)
```

The preregistration's battery (`preregistration.json:44`) names four mutants —
`m-ldpreload` (envnames), `m-ldaudit-writable` (code), `m-ldaudit-foreign`
(hostlibs), `m-member-flip` (rehash). None targets leg (iii). The four mutants in
`run-battery.py` (`m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`,
`m-member-flip`) likewise target envnames / code-byte-compare / hostlibs / rehash.
So leg (iii) — the clause this seat was assigned — has **zero** live kill coverage.

Proposed two mutants that would make both branches reachable, with the caveat that
they are a design and were not executed: `J2RowCap-proposed-fix.diff` §(2).

**Adjacent observation, outside this seat's leg (for routing, not a verdict of
this report):** the preregistration names `m-ldaudit-writable (code leg)` as a
battery mutant, but the frozen `run-battery.py` defines `m-text-flip` in the code
leg and no `m-ldaudit-writable` at all (`grep -o '"m-[a-z-]*":' run-battery.py`
lists only `m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`, `m-member-flip`), and
no receipt for it remains in `.ufo/waves/round-55/c1/battery/`. Related: the
prereg's `kill_rule` says "the claim is falsified if … any battery mutant prints
met=True", while the runner deliberately classifies `m-ldaudit-foreign` as
`kind="vector"` and requires `met=True` for it (`run-battery.py:59,137-138`). Both
are battery/calibration questions, not this leg's; I record them with the exact
evidence so the seat that owns the battery can act on them.

## Finding 2 (operability, lower): ROW_CAP bounds a row, not the leg

`ROW_CAP` is documented as "a single maps row is read at most 64 MiB" (`:145`) and
the predicate repeats the per-row wording — that is exactly what the code does, so
this is *not* a violation. It is an unstated cost bound: the number of executable
mappings of one tree file is bounded only by the audited process's own address
space, and each may be up to `ROW_CAP`.

Measured on the real kernel, 20 executable mappings of one 64 MiB sparse file:

```
exec rows for the 64 MiB member: 20
counter compared ranges: 20
TOTAL bytes read from /proc/pid/mem: 1342177280 = 1.25 GiB
elapsed: 0.24 s   per-row cap: 67108864
```

The preregistration's `limits` string does not mention it. Proposed fix (additive,
`ROW_BUDGET`, verified to compile and to leave every existing behaviour intact):
`J2RowCap-proposed-fix.diff` §(1).

## No other defect found in this leg

Checked and clean:

* `int(v, 16)` on the maps range and `int(f[2], 16)` on the file offset — correct
  bases for `/proc/<pid>/maps` (`:521-522`).
* Both guards run **before** the single `os.pread` (`:533` is the only read of
  `/proc/<pid>/mem` in the whole counter — `grep -n "os.pread"` finds one hit), so
  no path exists that reads a row without passing both.
* A refused row is not added to `seen` and not counted in `compared`, so it cannot
  silently satisfy the `REQUIRED` check (`:570-572`) or the two-pass comparison.
* `off + length > len(data)` uses the whole member's byte length, and the archive
  member is read once at download (`Archive`, `:445-465`), so the comparison cannot
  be moved by the replay rewriting the file (Sen1Mem F1 holds for this leg).

## Risks and blockers

* **Blocker to any repair in this seat: none.** Everything above was measured.
* The proposed battery mutants in `J2RowCap-proposed-fix.diff` §(2) are a design;
  running the battery spawns three live replays and was out of scope for a
  read-only leaf seat. The counter patch in §(1) *was* verified: `patch -p1
  --dry-run` OK, applies, `py_compile` OK, and the patched counter passes 41/42
  harness checks (the single failure is the deliberate "bytes equal the frozen
  sha256" assertion, which must fail for any patch).
* Clause B's guard would refuse an honest mapping of an ELF whose executable
  `PT_LOAD` is the *last* segment in the file with a non-page-aligned end — the
  kernel maps the whole last page and zero-fills past EOF, so `off + length` can
  exceed `len(member)`. I scanned 8,447 ELF files (`/usr/lib`,
  `/usr/lib/x86_64-linux-gnu`, `/usr/bin`, `/usr/local/lib`,
  `/home/vgpnk/.local/opt/llama-b11909`): **0** have their last `PT_LOAD` by file
  offset executable, and **0** executable `PT_LOAD`s page-round past the file size.
  So the class is real but not reachable with toolchain-produced ELF, and refusing
  is the safe direction (it never accepts non-member bytes). Recorded as a known
  edge, not a defect.
* Tooling: no install or upgrade was needed; nothing was added to PATH.

## Artifacts written

```
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J2RowCap.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J2RowCap/j2-rowcap-unit-harness.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J2RowCap/j2-rowcap-unit-harness.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J2RowCap/J2RowCap-proposed-fix.diff
```
