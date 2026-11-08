# MT01ProbeMutants — round-96 wave 1, probe mutants against the frozen C1 cells

Seat: `MT01ProbeMutants` (mutation tester). The lane repo was read-only for this seat: no commit, push,
jj, or tracked-file edit. All fixtures, mutants and receipts lived in
`/fast/scratch/hyaku/kama-r96/MT01ProbeMutants` and were copied here before that tree was deleted.

## 1. Mutation target and instrument bytes

| object | bytes tested | sha256 |
|---|---|---|
| `tools/kama-probe.sh` (pristine) | lane worktree, identical before and after the seat | `11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709` |
| `tools/round96-router-budget.py` (pinned grade copy) | `counter-pinned-b3289c18.py`; byte-identical to the lane counter at final HEAD `bb4a997a` | `41876c9ba9d0a62d402b03939d79bdbfd9336a69b223f635b36439d5386cc2a6` |

Lane HEAD at final grade: `bb4a997a210793934ac931f47326c8a81bdc7e00` (amendments 4/5); the frozen
claims commit is `58001b71`, base `5d43528b`. The counter did not change between amendment 3
(`b3289c18`, the pinned copy) and `bb4a997a`; the probe changed in none of the amendments.

Concurrency disclosure: HEAD moved three times while this seat ran (`bbdfc930` → `4a0f6a35` →
`b3289c18` → `bb4a997a`). Amendment 2's W12 fixture was still malformed and amendment 3 replaced it with
the interleaved shape (the same defect this seat reproduced). The **authoritative grade is the pinned
`b3289c18`/`bb4a997a` counter bytes above**; the earlier logs are kept and labelled `superseded` in
`MANIFEST.txt`. The probe bytes were identical for every run, so the mutant set never changed.

Arithmetic the fixtures price: a tensor header costs 6 steps at `nd = 1`
(name `u64`+skip 2, `nd` 1, dims 1, type+offset 2); `MAX_STEPS = 5_000_000` ⇒ ceiling ≈ 833 333 headers;
`mid.gguf` at 700 000 headers costs 4 200 000 steps.

## 2. Mutants (exact single-occurrence byte edits of ROUTER_PY)

| id | edit | sha256 |
|---|---|---|
| M1-nostepcap | both `if steps[0] > MAX_STEPS: raise Unknown()` checks deleted (need + per-element string loop) — infinite budget | `e874a0f7290e1593dbad8e61a8782cdddd2f4f90e2d4c5cf2ec42026d64d2e94` |
| M2-maxsteps4m | `MAX_STEPS = 5_000_000` → `4_000_000` | `580b44e9809be7dbaad85b3dcb6448857a1b286b1b4d9b4c4537a91f49326b2e` |
| M3-noheadercharge | per-header charge removed: `need()` increments `steps[0] += charge[0]`, and `charge[0] = 0` around the tensor-info loop (bounds/`Bad` checks kept) | `994e9b140c2996bf0e9549f23a977f593994047eac68309beabca5e9bccc1e80` |
| M4-maxmeta100m | `MAX_META = 512 * 1024 ** 2` → `100 * 1024 ** 2` | `6b5f6db4b802b5e5d34864f5a53508d8edacfa7d4923282949a9e4f4ae1709bf` |
| M5-noctime | memo key drops `st.st_ctime_ns` | `b46dd34772b8ee5f4eb30921334201905a79801d9da67ff65bfd917c20ff4496` |

`mutants.diff.txt` carries the full diffs; each edit tested with `str.count(old) == 1`.

## 3. Detector and baseline

Detector: the counter's own fixture set (`build_fixtures`, `SLOW_FILES = 40`), its own `Runner`, `Stub`,
`router_body` and the frozen per-cell `(verdict, reason)` expectation. One probe invocation per cell
(`W10-rewrite` uses its three-invocation rewrite sequence exactly as `evaluate_pass` does), natural load,
one run per cell. The counter module was imported from the pinned bytes; no counter byte, predicate or
fixture was modified.

Baseline (`pristine`, final counter): **12/12 cells green**, `MUTDIFF pristine killed=0 flipped=[]`.
The counter's own predicate receipt agrees (two natural passes, one run each):
`ROUTER_BUDGET96 cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1 … rev=b3289c18…`,
exit 0 (`counter-confirm-final.log`). The margin guard needed `--allow-clock` on this host at
`--slow-files 40` in some runs (W03 45–118 s across runs); `--allow-clock` only disables that guard, cell
grading is unchanged. Because the baseline is green, every flip below is a killed mutant.

## 4. Results at the pinned counter (`mismatches=0` baseline)

| mutant | W01 | W02 | W03 | W04 | W05 | W06 | W07 | W08 | W09 | W10 | W11 | W12 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pristine | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | 12/12 green |
| M1-nostepcap | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | **SURVIVED** |
| M2-maxsteps4m | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | **FLIP** | ok | **KILLED by W11** |
| M3-noheadercharge | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | **SURVIVED** |
| M4-maxmeta100m | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | **SURVIVED** |
| M5-noctime | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | **SURVIVED** |

Only cell that flips: **W11-700k**, mutant M2.

    MUTCELL M2-maxsteps4m W11-700k ok=0 got=MODEL_OK/router-unloaded-autoload \
      want=MODEL_UNLOADED/router-model-invalid 2.69s
    MUTSTATE M2-maxsteps4m mid: state "-" (pristine: "invalid")

`mid.gguf` (700 000 headers) needs 4 200 000 steps: decidable at 5 000 000, undecidable at 4 000 000 →
`-` → loadable. The C1 discriminator works for the central `MAX_STEPS` change.

Per-fixture graded file state (`MUTSTATE`, from the probe's own `ROUTER_PY files 0`):

| fixture | pristine | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|
| slow_0 (600 000 headers) | invalid | invalid | invalid | invalid | invalid | invalid |
| big (1 200 000 declared) | - | - | - | - | - | - |
| mid (700 000 headers) | invalid | invalid | **-** | invalid | invalid | invalid |
| strbig (6 000 000×9 B) | - | - | - | - | - | - |

## 5. Detection gaps (surviving mutants)

A surviving mutant is a coverage finding only; this seat changes no frozen predicate.

### G1 — M1 (step budget removed entirely) survives all 12

No frozen fixture can distinguish a bounded budget from an unbounded one:

- the largest step counts actually taken are `slow_*.gguf` 600 000 headers = 3 600 004 steps and
  `mid.gguf` 700 000 headers = 4 200 000 steps, both below 5 000 000;
- `big.gguf` is rejected by `MAX_TENSORS` before the tensor loop, so `MAX_STEPS` is never reached;
- `W12-strings` *does* reach the loop (pristine raises `Unknown` at element 5 000 001), but the complete
  parse under M1 returns `ok`, and `file_state` maps both `ok` and `-` to `-`:
  `for want in ("missing", "invalid"): … return want` then `return "-"`. The graded cell is
  `MODEL_OK/router-unloaded-autoload` under both variants, and the per-fixture state is `-` under both.
  W12 therefore exercises the step loop but is **invariant to the cap**; it cannot kill any budget change.

Would-kill control `WK-budget` (54 000 112 B: a well-formed 6 000 000 × 9-byte interleaved string array
plus a bad-offset tensor header, so the unbounded parse ends `invalid`):

    pristine          -> "-"        (cap hit)
    M1-nostepcap      -> "invalid"  (full parse, bad offset)
    M2-maxsteps4m     -> "-"        (4M cap hit)

Graded: `MODEL_OK/router-unloaded-autoload` vs `MODEL_UNLOADED/router-model-invalid`. A cell of this
shape (budget-capped file whose unbounded parse is *invalid*) is the missing discriminator.

### G2 — M3 (per-header charging removed) survives all 12

The fixture set has nothing between the 833 333-header ceiling and `MAX_TENSORS = 1 000 000`: the largest
fixture is `mid.gguf` at 700 000 headers, which is decidable under the frozen budget, so removing the
6-step charge changes no graded state (all four `MUTSTATE` values identical to pristine). Removing the
charge raises the effective ceiling to `MAX_TENSORS`, exactly the invariant the C2 step table names and
the C1 counter does not measure.

Would-kill control `WK-ceiling` (36 000 048 B, 900 000 headers, short data section):

    pristine          -> "-"        (5 400 000 steps > 5M)
    M2-maxsteps4m     -> "-"        (4M cap)
    M3-noheadercharge -> "invalid"  (headers uncharged; data-section check reached)

### G3 — M4 (`MAX_META = 100 MiB`) survives all 12

The maximum header position any fixture reaches is `mid.gguf`'s 28 000 048 B (`slow_*` 24 000 048 B;
`big.gguf` is count-rejected before the tensor loop; `strbig.gguf` stops at the step cap at about
45 000 000 B). All are below 100 MiB, so the meta cap never binds and the mutant is invisible.

Would-kill control `WK-meta` (117 000 112 B: a 4 500 000 × 26-byte string array header, then a
bad-offset tensor):

    pristine          -> "invalid"  (512 MiB cap not reached; full header parsed)
    M4-maxmeta100m    -> "-"        (raises at 104 857 600 B)

### G4 — M5 (`ctime` removed from the memo key) survives all 12 — structural

`SEEN` is a dict inside one `python3 -c "$ROUTER_PY"` process. Every counter cell starts a new probe
process, and `W10-rewrite` performs the same-size rewrite **between** invocations, so the memo key never
spans the rewrite and cannot be observed. `W08-hardlink-x8`'s paths share one inode with identical
`ctime`, so dedup is exercised without the `ctime` term. The W10 cell therefore proves only that a later
invocation re-reads the file — true for any cache-free process — not that `ctime` is in the key.

In-process control (two `file_state` calls in ONE process around a same-size rewrite with mtime
restored):

    pristine          first "invalid"  -> after rewrite "-"        (memo_seen 2, re-parsed)
    M5-noctime        first "invalid"  -> after rewrite "invalid"  (memo_seen 1, stale)

Cross-process control (the counter's W10 shape, rewrite between invocations):

    pristine          first "invalid"  -> after rewrite "-"
    M5-noctime        first "invalid"  -> after rewrite "-"

The mutation is behaviour-bearing, but no fixture can reach it through the probe CLI; closing this needs
an instrument change (one `ROUTER_PY` process held across the rewrite), not another cell.

## 6. What the counter does catch

M2 (`MAX_STEPS` 5M → 4M) is killed by W11 at the first cell that needs 4.2M steps; this is the claim's
central arithmetic and the frozen set measures it correctly. M2's other 11 cells stay green, so the kill
is specific: no incidental cell reddens.

## 7. Restoration and cleanup evidence

- The lane `tools/kama-probe.sh` was never written: sha256 `11e5b01b…e709` at first read, at every
  mutant install (all installs target scratch copies) and at final check.
- `git -C <lane> status --porcelain -- tools/ plans/ SKILL.md` is empty; the only lane changes are other
  seats' `.ufo/` outputs and the main agent's amendments.
- Mutant and fixture bytes existed only under
  `/fast/scratch/hyaku/kama-r96/MT01ProbeMutants`; receipts were copied here first, then the tree was
  removed. No `~/.local/bin` or PATH directory was touched, no commit/push/jj was run.
- No tool was installed or updated by this seat.

## 8. Receipts in this directory

| file | content |
|---|---|
| `receipts-final.log` | authoritative per-cell lines for pristine + five mutants (pinned `b3289c18` counter) |
| `receipts-final/*.json` | per-variant cell rows, probe/counter shas, internal fixture states |
| `counter-confirm-final.log` | the frozen counter's own predicate at `b3289c18` (`mismatches=0 load_stable=1`, exit 0) |
| `controls.json`, `receipts-controls.log` | WK-budget / WK-ceiling / WK-meta / WK-ctime would-kill controls |
| `mutants/*.sh`, `mutants.diff.txt` | pristine and mutant probe bytes plus exact diffs |
| `hashes.txt` | pinned hashes and fixture sizes |
| `superseded/` | pre-amendment runs at `bbdfc930`/`4a0f6a35` (W12 baseline red before amendment 3; kept for audit, not used above) |
