# MT01Mutants — round 99 w1 mutation matrix (kama)

Seat: mutation-tester (attack). Lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin`,
base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`, freeze commit (M1's counter bytes)
`f6e7ccc285e0c1207378f73c394acbfda58bff23`. Every instrument byte was read with
`git show f6e7ccc2:<path>`; mutants were byte patches on scratch copies. No tracked lane file
was edited. Commands and outputs below are real; the receipts are copied to
`.ufo/waves/round-99/w1/out/MT01Mutants/logs/` and the machine matrix is
`.ufo/waves/round-99/w1/out/MT01Mutants/matrix.json`.

Frozen instrument hashes (freeze commit, `logs/instrument-hashes.txt`):

```
2ba93f8e08f20c8f6575e5d3c89281b5e3e54c193347abe384774ced5b593932  tools/round99-control-population.py
e76c35b449be9a9680af50480a0871317c6ad88a9a87824ec30262c88ad6d246  tools/round99-router-budget.py
5e2be1391e199aa60adf5045d3cef87cc83115f951e13824ec984e7b87ed08f6  tools/round99-record-audit.py
eee2f880d051716b896bb8994d5742175eb3a90fc811e35fe736beec5d23ca59  tools/round99-autoload-states.py
829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21  candidates/kama-probe.r99.sh
```

## 1. Baselines — the frozen controls reproduce

| run | command (scratch cwd) | output | exit |
|---|---|---|---|
| C1 positive | `python3 round99-control-population.py --repo <lane> --rev f6e7ccc2 --work <w> --counter tools/round99-router-budget.py` | `selected=6 ran=5 … refused=1 … complete=1 population_shaped=1 met=True` | 0 |
| C1 negative (K3) | same, `--rev 439fdb3d --counter tools/round98-router-budget.py` | `selected=- ran=5 … refused=0 … met=False` | 1 |
| C2 base | `python3 round99-record-audit.py --repo <lane> --rev 439fdb3d --work <w>` | `checks=12 mismatches=10 met=False` | 1 |
| C3 base | `python3 round99-autoload-states.py --repo <lane> --rev 439fdb3d --work <w>` | `mismatches=4 base_mismatches=4 flips=0 stable=5 met=False` | 1 |
| C3 candidate | same + `--probe-file cand.sh` | `mismatches=0 base_mismatches=4 flips=4 stable=1 met=True` | 0 |

All five reproduce the freeze receipts (`controls/c1-*`, `controls/c2-base.out`,
`controls/c3-base.out`, `controls/c3-candidate.out`). The C1 line is byte-identical to
`.ufo/waves/round-99/measured/c1.out`.

## 2. Mutation matrix

Killed = a named detector reddens. "Escaped" = every detector the round actually ships stays
green (a coverage finding, not authority to change a contract).

| # | claim | mutant | detector that must redden | actual reddened | verdict |
|---|---|---|---|---|---|
| 1 | C1 | `router-budget`: `ok = int(ok)` (drop `population_ok`) | grader refusal arm | `refused` (mutant exit 0) → `met=False` exit 1 | KILLED |
| 2 | C1 | `router-budget`: `population_ok = 1` | grader refusal + `selected/ran/population_ok` | `refused=0`, `population_shaped=0` → exit 1 | KILLED |
| 3 | C1 | `router-budget`: `population_ok = 0` (blanket refusal, K4) | grader `complete` arm | `complete=0` (`positive_exit=1`) → exit 1 | KILLED |
| 4 | C1 | `control-population`: `refused = 1` | grader-level negative control vs round-98 | negative control: `refused` 0→1, `met=True` exit 0 | KILLED only by the prose K3 control; **ESCAPED the frozen predicate** (byte-identical to `measured/c1.out`) |
| 5 | C1 | `control-population`: skip positive arm, fabricate `positive_*=6/0/1` | K4 blanket counter | `complete` 0→1, `met=True` exit 0 | KILLED only by K4; **ESCAPED the frozen predicate** |
| 6 | C2 | `record-audit` check 4 counts a mismatch as pass | frozen base receipt (`mismatches=10`, `MISMATCH 4`) / forged 6/6 split | base 10→9, `MISMATCH 4` gone; forged split green | KILLED by receipt; **ESCAPED exit-code-only and the split forgery** |
| 7 | C2 | `record-audit` check 9 hardcoded arm list (no receipt re-derivation) | forged gate receipt (no committed control does this) | base output identical to pristine; forged gate passes check 9 | **ESCAPED** |
| 8 | C3 | probe `RT_REASON=$down` → blanket rename | P1-autoload-off | `P1-autoload-off` mismatch | KILLED |
| 9 | C3 | probe `*) return 2` → `*) return 1` (off-for-unread) | U3, U4 | `U3-nonjson-props`, `U4-nonrouter-props` | KILLED (partial; U1/U2 unaffected) |
| 10 | C3 | probe: `return 2` before the fetch (never reads /props) | P1 | `P1-autoload-off` only | KILLED |
| 11 | C3 | probe: absent field in a router doc → `on` | none exists | nothing; `mismatches=0 met=True` exit 0 | **ESCAPED** |
| 12 | C3 | counter `met = mismatches == 0 or stable == len(CELLS)` | frozen base receipt (`met=False`) | base prints `met=True` beside `mismatches=4`, exit 0 | KILLED by base; **ESCAPED the candidate predicate** |
| 13 | C3 | counter `base = {cid: want}` (base pass never runs) | receipt fields `base_mismatches/flips/stable` | base `base_mismatches=0 flips=4`; candidate `0/0/5` vs frozen `4/4/1` | KILLED |

### Receipts (trimmed, exact lines)

**1–2: counter refusal removed / `population_ok` faked**

```
$ python3 round99-control-population.py --repo <clone99> --rev 089c3d5d --counter tools/round99-router-budget.py
CONTROL_POP99 … selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=0 mutant_ok=1
  refused=0 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=False
exit=1
$ … --rev b787a18a --counter tools/round99-router-budget.py
CONTROL_POP99 … mutant_control_exit=0 mutant_ok=1 refused=0 … complete=1 population_shaped=0 met=False
exit=1
```

**3: blanket refusal (K4)**

```
$ python3 round99-control-population.py --repo <clone99> --rev d52339a1 --counter tools/round99-router-budget.py
CONTROL_POP99 … mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6 positive_exit=1
  positive_ok=0 complete=0 population_shaped=1 met=False
exit=1
```

**4: grader hardcodes `refused=1`** — reproduces the positive predicate exactly, so only the
negative control sees it:

```
$ python3 grader-A.py --repo <lane> --rev 439fdb3d --counter tools/round98-router-budget.py
CONTROL_POP99 … selected=- ran=5 … refused=1 … complete=1 … met=True   exit=0   (frozen K3 run: refused=0 met=False exit 1)
$ python3 grader-A.py --repo <lane> --rev f6e7ccc2 --counter tools/round99-router-budget.py
<byte-identical to .ufo/waves/round-99/measured/c1.out>   exit=0
```

**5: grader skips the positive arm** — fabricates the positive receipt:

```
$ python3 grader-B.py --repo <clone99> --rev d52339a1 --counter tools/round99-router-budget.py
CONTROL_POP99 … refused=1 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 met=True
exit=0            (the positive arm never ran; the frozen K4 expectation is complete=0 met=False)
```

**6: check 4 forced green** — base control and forged 6/6 split:

```
$ python3 audit-A.py --repo <lane> --rev 439fdb3d
RECORD_AUDIT99 checks=12 mismatches=9 met=False    (frozen receipt: mismatches=10 with "MISMATCH 4")
$ python3 audit-A.py --repo <tree-base> --tree tree-split-wrong
RECORD_AUDIT99_MISMATCH 8 … ; RECORD_AUDIT99 checks=12 mismatches=1 met=False   (pristine: 2 = {4,8})
```

**7: check 9 without receipt re-derivation** — escapes both controls:

```
$ python3 audit-B.py --repo <lane> --rev 439fdb3d
<byte-identical to the pristine base run: checks=12 mismatches=10 met=False exit=1>
$ python3 audit-B.py --repo <tree-base> --tree tree-gate-forged      # receipt: round-clean arm removed
RECORD_AUDIT99_MISMATCH 8 … ; RECORD_AUDIT99 checks=12 mismatches=1 met=False
# pristine bytes on the same forged tree:
RECORD_AUDIT99_MISMATCH 8 … census base=… tip=…
RECORD_AUDIT99_MISMATCH 9 gate failed arms ['newest-closure','round-scope','round75-instruments','round78-instruments','selfdesc']
RECORD_AUDIT99 checks=12 mismatches=2 met=False
```

**8–10: probe reason mutants** (pristine counter, `--probe-file`):

```
blanket rename : AUTOLOAD_STATES99_MISMATCH P1-autoload-off want=…/router-unloaded got=…/router-autoload-unread
                 cells=5 mismatches=1 base_mismatches=4 flips=5 stable=0 met=False   exit=1
off-for-unread : MISMATCH U3-nonjson-props, U4-nonrouter-props ; mismatches=2 met=False exit=1
no-props-fetch : MISMATCH P1-autoload-off ; mismatches=1 met=False exit=1
```

**11: field absent in a router document** — no cell moves; the direct check shows the verdict
flip the counter cannot see:

```
$ python3 auto-pristine.py --repo <lane> --rev 439fdb3d --probe-file p-field-on.sh
AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True   exit=0
# direct, /props = {"role":"router"} (models_autoload absent), one unloaded entry:
cand.sh:       verdict=MODEL_UNLOADED reason=router-autoload-unread  exit=2
p-field-on.sh: verdict=MODEL_OK       reason=router-unloaded-autoload exit=0
```

**12–13: counter mutants**

```
12 base      : cells=5 mismatches=4 base_mismatches=4 flips=0 stable=5 met=True  exit=0   (frozen: met=False exit 1)
12 candidate : identical to pristine candidate (met=True) — escapes the predicate
13 base      : cells=5 mismatches=4 base_mismatches=0 flips=4 stable=1 met=False exit=1   (frozen: base_mismatches=4 flips=0 stable=5)
13 candidate : cells=5 mismatches=0 base_mismatches=0 flips=0 stable=5 met=True exit=0   (frozen: 4/4/1)
```

## 3. Findings

**F1 (C1, calibration). The frozen C1 predicate line is not the grader's line.**
`plans/round-99-claims.md:44` ends the predicate with `positive_cells=6 positive_exit=0
positive_ok=1 complete=1 met=True`; the emitter (`tools/round99-control-population.py:134`)
prints `complete=1 population_shaped=1 met=True counter_sha256=… rev=…`, i.e. the frozen sentence
is not a contiguous substring of what it says is printed. Real line in
`.ufo/waves/round-99/measured/c1.out:2`. Command: substring test over that line → `False`.
Consequence combined with #4/#5: at the freeze commit no grader-level receipt is committed, and
the measurement receipt in flight (`measured/c1.out`) is the positive run only, so a grader
that hardcodes `refused=1` (and one that skips the positive arm) reproduces `measured/c1.out`
byte-for-byte; the refusal half is asserted in prose (`plans/round-99-claims.md:63-64` "the grader
prints `refused=0 met=False` exit 1 when run against it") but no committed receipt records a
grader-level negative run. This is the same class the round's own claims warn about: a counter
green on a property narrower than its wording.

**F2 (C2, integrity/K1 risk). The graded C2 counter changed after the freeze commit.**
`git -C <lane> status --porcelain` shows ` M tools/round99-record-audit.py`; freeze hash
`5e2be139…`, working-tree hash `59f22d5e…`; mtime `12:03:02` vs freeze commit `11:42:03`. The
one hunk in `read_bytes_at` (`tools/round99-record-audit.py:252`) makes the two historical census
revisions come from git under `--tree` instead of the tree. The untracked
`controls/c2-forged.out` (mtime `12:03:44`) carries `mismatches=2` (checks 1, 2) — a shape the
freeze bytes cannot produce: with the freeze bytes, `read_bytes_at` is called for `R98_BASE` and
`R98_TIP` with the same tree path (`:205-206`), so `got_base == got_tip`, while
`EXPECT_BASE["rows"]="361"` ≠ `EXPECT_TIP["rows"]="363"` — check 8 is false for **every** tree
(measured: both forged trees redden check 8 with `base=…363… tip=…363…`). So either the M2
graded bytes are the changed bytes (the plan's C2 kill rule K1 fires) or the in-flight forged
receipt was not produced by the frozen counter. C2's forged control is not valid at both byte
sets simultaneously. (Not my edit; the change predates this seat's first read.)

**F3 (C2, calibration). The audit's own docstring states the wrong base value.**
`tools/round99-record-audit.py:10` (freeze bytes): "at base `439fdb3d` the same counter prints
`mismatches=9`". Actual at base and in `controls/c2-base.out`: `mismatches=10`
(`plans/round-99-claims.md:93` says 10). A self-declaration that contradicts its own receipt — the
round-98-record defect class this claim is meant to close.

**F4 (C3, calibration). The C3 counter's docstring states the wrong base shape.**
`tools/round99-autoload-states.py:11`: base prints "`mismatches=4 base_mismatches=4 flips=0
stable=1 met=False`"; the actual base run and `controls/c3-base.out` print `stable=5`. Command:
the C3 base baseline above. Same class as F3.

**F5 (C3, depth). The disclosed "absent field stays unread" rule is ungraded, and the ungraded
mutant flips the verdict.** `plans/round-99-claims.md:170` discloses that a router document with
`models_autoload` omitted is graded unread. The five cells do not serve that body: `U4` is
`{"status":"ok"}` (no router role, `tools/round99-autoload-states.py:24,144`), so the
classification `elif doc.get("models_autoload") is False: … else: print("unread")`
(`candidates/kama-probe.r99.sh:907-911`) is never exercised. Mutating that `else` to `print("on")`
keeps the claim green (`mismatches=0 met=True`, #11) while the probe on `{"role":"router"}` flips
from `MODEL_UNLOADED/router-autoload-unread` (fail-closed) to `MODEL_OK/router-unloaded-autoload`
(loadable) — a verdict change, not just a vocabulary one. The claim's own "off requires an explicit
false" rule is therefore not covered by its evidence.

**F6 (C1/C2/C3, calibration). Escape surfaces worth naming for the L1.**
(i) C1's `refused` arm has no committed negative receipt (F1); (ii) C2 check 9's re-derivation has
no control at all — the plan's measurement-time forgery forges the correction text, not the gate
receipt (`plans/round-99-claims.md:108`), so mutant #7 ships green even though check 9's
docstring claims re-derivation (`tools/round99-record-audit.py:15,32`); (iii) C3's verdict-preserving
requirement is asserted only by P1 for the fetch layer — U1/U2's unreadness comes from the
fetch-failure returns, so the tri-state classifier is exercised only by U3/U4 (mutant #9). These do
not change any predicate; they bound what the round's controls actually test.

## 4. Bounds and restoration evidence

- Mutants were applied only to scratch copies under
  `/fast/scratch/hyaku/kama-r99/MT01Mutants/`; the lane's tracked files were read through
  `git show f6e7ccc2:` (hashes above). No lane file was written.
- C1 counter mutants live only as commits in the scratch `git clone --shared` fixture
  (`clone99`, toplevel asserted == the clone path): `089c3d5d` (nopop), `b787a18a` (pop1),
  `d52339a1` (blanket). After the runs the clone was reset to
  `f6e7ccc285e0c1207378f73c394acbfda58bff23` (verified by `rev-parse HEAD`).
- Lane `git status --porcelain` before and after this seat is the same set plus siblings' new
  untracked files (`.ufo/waves/round-99/w1/*`, `w1/out/`); none of the entries are this seat's,
  and `tools/round99-record-audit.py` was already modified before the first read (F2).
- No host service, router, or registered consumer was contacted; every stub bound
  `127.0.0.1:0`. No pacman/tool installs; nothing to record.
- Scratch was removed before yield (`rm -rf /fast/scratch/hyaku/kama-r99/MT01Mutants`); receipts
  were copied first to `.ufo/waves/round-99/w1/out/MT01Mutants/`.
