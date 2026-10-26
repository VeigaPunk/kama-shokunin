# M1Ctr — round-46 C1 counter mutation test (freshness)

**Verdict: the frozen C1 counter (`tools/round46-release-recheck-audit.py`) survived a 46-mutant assault with no defect: 43 mutants killed, 3 survivors — each of the 3 proven behaviorally equivalent on every input reachable under the frozen round-46 contract (2 population-unreachable legs, 1 dead condition shadowed by the witness_new rule). No false-accept and no false-reject behavior was found. Two coverage findings and one dead-logic finding are recorded below; none is a counter defect.**

## 1. Setup

- Scratch (operator directive): `S=/fast/scratch/hyaku/kama-r46/M1Ctr`, `TMPDIR=$S`. Pristine counter copied to `$S/counter/pristine.py`, sha256 `502e6f57036fca803a081f844ea80f19e26c0dd782f329148d72b25b89861997`. The lane's own file was never written: sha256 after the run is identical (`502e6f57…`), i.e. exact-byte restoration evidence by construction (all mutants lived in `$S/counter/mutants/`, scratch removed at the end).
- Upstream: `/fast/scratch/hyaku/kama-r46/L1/llama.git` (read-only; b11889 `d854d98b…`, b11906 `4d71b42f…` both present, verified `git cat-file -t` = commit).
- Population: 91 rows re-derived from `corpus/SOURCES.md` at BASE `0163fea2…` with the counter's own `population()`; blob scan vs b11906: 6 unchanged-blob, 0 absent-at-release, 85 changed.

## 2. Fixture (all-valid ledger, real bytes)

One fixture repo `repos/A` = `git clone --shared` of the lane + one commit (toplevel asserted before every commit; throwaway identity only inside the fixture). The commit carries:

- `registry/release-recheck-b11906.tsv` — a **full 91-row ledger, every row valid**, built from real llama.git bytes: 6 `unchanged-file` (S015 S059 S106 S128 S129 S131), 75 `holds` (text-equal ranges from difflib equal blocks; carry-forward holds row **S035** `tools/server/README.md` from the b11889 holds set; 2-pair holds row **S036** `server-http.cpp`), 7 `holds-reworded` (target **S042** `server-context.cpp`, real witnesses from a real reworded region), 1 `drifted` (**S037** `server.cpp`), 2 `removed` (**S108** `server.cpp` plain absent-first-line window; **S001** `README.md` window whose first ≥3-char line is short and still present — the M30 differentiator).
- `corpus/SOURCES.md` at tip = lane-tip content + `## Round-46 release re-verification` section listing the drifted/removed ids + a newrow row (`| S901 |…b11906 4d71b42f…`).
- Knowledge flags appended to the used-by `corpus/knowledge/*.md` files of the drifted/removed ids.

Every constructed row was validated **with the frozen counter's own `check_row`** before any mutant ran (`check_row validation: all 91 rows valid`). Pristine baseline on A:

```
python3 $S/counter/pristine.py --repo $S/repos/A --tip ec9abd7f109e1f6f4cca29c360e2c294ecefe445 --upstream …/llama.git
→ rc=0  pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=75 reworded=7 drifted=1 removed=2 flags_missing=0 section=1 newrow=1 met=True   (no detail lines)
```

## 3. Violation fixtures (26 variants, each pristine-rejected)

One commit per variant off A; the pristine counter must reject each with an asserted expected detail (asserted in the pristine stage before any mutant ran; all 26 passed). Examples: `v_wp11_dr` (11-char witness_pin → `S037 invalid: witness_pin rule`), `v_note39` (39-char note), `v_wp_in_RF` (witness present in release file), `v_holds_witness` (holds row carrying witnesses), `v_unch_on_changed` (`unchanged-file` verdict on a changed row), `v_hr_all_eq_ooo` (holds-reworded with all pairs text-equal via out-of-order ranges + boundary witnesses), `v_removed_wn`, `v_range_wide` (100-line range), `v_range_eof`, `v_short_range` (<20 non-ws), `v_cited_miss` (S131 pin_lines missing a cited strong line), `v_wrong_pin`, `v_dup`, `v_flag_missing`, `v_sec_list_missing`, `v_newrow_partial`, `v_section_missing`, `v_ws_runs` (must stay **valid**; it does). Full list + shas: `out/M1Ctr/shas.json`, baselines: `out/M1Ctr/baselines.json`.

## 4. Mutants and results

Detector = (exit code, stdout) of the counter per fixture; **killed** = any difference vs the pristine baseline on any fixture in the mutant's set (A for all; plus the paired violation fixture; M18/M19/M27 additionally run on **all 27 fixtures**). Mutants are exact byte replacements in a scratch copy (occurrence-indexed where the target line appears twice); per-mutant sha256 in `out/M1Ctr/results.json`.

| id | category | mutation (old → new) | verdict | killed by (evidence) |
|----|----------|----------------------|---------|----------------------|
| M01 | witness length | `len(wp) < 12` → `< 5` | killed | v_wp11_dr: rc 1→0, false accept (met=True) |
| M02 | witness length | HR `len(wn) < 12` → `< 5` | killed | v_wn11_hr: false accept |
| M03 | witness length | drifted `len(wn) < 12` → `< 5` | killed | v_wn11_dr: false accept |
| M04 | P construction | `P` from `pr[:1]` only | killed | A: rc 0→1, reworded 7→0 (witnesses in later ranges lost) |
| M05 | R construction | `R` from `rtext[0:r[1]]` (file head) | killed | v_wn_outside: false accept |
| M06 | PF/RF construction | PF/RF swapped | killed | A: rc 0→1 (witness_new rule fires) |
| M07 | RF construction | `RF := ""` | killed | v_wp_in_RF: false accept |
| M08 | in leg | `wp not in P` → `wp in P` | killed | A: rc 0→1 |
| M09 | not-in leg | HR `wn not in R` → `wn in R` | killed | A: rc 0→1 |
| M10 | witness-presence leg | holds/unchanged witness check → `if False:` | killed | v_holds_witness: false accept |
| M11 | note length | `< 40` → `< 30` | killed | v_note39: false accept |
| M12 | note length | `< 40` → `<= 40` | killed | A: rc 0→1, drifted 1→0 (note exactly 40 chars rejected) |
| M13 | newrow leg | drop `RELEASE_COMMIT in x` | killed | v_newrow_partial: newrow 0→1, rc 1→0 |
| M14 | newrow leg | `not in base_ids` → `in base_ids` | killed | A: newrow 1→0 |
| M15 | section leg | `and` → `or` in section scan | killed | v_section_missing: section 0→1 |
| M16 | section leg | SECTION constant mutated | killed | A: section 1→0 |
| M17 | cited-line rule | strong coverage dropped (`if strong:` → `if strong and False:`) | killed | A (4 rows lose weak coverage) + v_cited_miss: false accept |
| M18 | cited-line rule | weak `elif` leg → `elif False:` | **survived** | equivalent-on-population (finding F1) |
| M19 | cited-line rule | strong `n <= len(ptext)` filter dropped | **survived** | equivalent-on-population (finding F2) |
| M20 | blob check | `release_blob` leg dropped | killed | v_rel_blob: false accept |
| M21 | changed check | blob-equality derive inverted | killed | A: valid 91→0 |
| M22 | changed check | flag check dropped | killed | v_changed_flag: reason flips to `unchanged-file rule` |
| M23 | holds rule | `all(eq)` → `any(eq)` | killed | v_holds_partial: false accept |
| M24 | unchanged rule | `changed == "0"` leg dropped | killed | v_unch_on_changed: false accept |
| M25 | unchanged rule | lines-equality flipped | killed | A: unchanged 6→0 |
| M26 | holds-reworded rule | `and not all(eq)` dropped | killed | v_hr_all_eq_ooo: rc 1→0 false accept (see §6) |
| M27 | drifted rule | tail → `return True` | **survived** | equivalent, proven dead leg (finding F3) |
| M28 | removed rule | `wn != "-"` → `wn == "-"` | killed | v_removed_wn: false accept |
| M29 | removed rule | `first in rset` → `not in rset` | killed | A: removed 2→0 |
| M30 | removed rule | first-line `>= 8` → `>= 3` | killed | A: removed 2→1 (S001 short-first-line window) |
| M31 | range geometry | width `>= 80` → `>= 800` | killed | v_range_wide: false accept |
| M32 | range geometry | `len(pr) != len(rr)` leg dropped | killed | v_counts: false accept |
| M33 | range geometry | pin inside-file `+ 100` slack | killed | v_range_eof: reason flips to `< 20` |
| M34 | range geometry | release `r and` None-guard dropped | killed | A: crash, empty stdout (rc 0→1) |
| M35 | 20-char rule | `< 20` → `< 2` | killed | v_short_range: false accept |
| M36 | population | `on-release` cell mutated | killed | A: pop 91→0 |
| M37 | population | ROW regex `S\d{3,}` → `S\d{4,}` | killed | A: pop 91→0 |
| M38 | release cell | `b11906` → `b11889` | killed | A: all rows invalid |
| M39 | population identity | `pin_commit` leg dropped | killed | v_wrong_pin: false accept |
| M40 | ws collapse | `ws()` → strip-only (no whitespace collapse) | killed | v_ws_runs: rc 0→1 (collapsed witness no longer found in raw P) |
| M41 | excerpt | off-by-one slice `lines[r[0]:r[1]+1]` | killed | A: holds 75→0 |
| M42 | dup tracking | duplicate-id detection dropped | killed | v_dup: `duplicate ledger rows` detail disappears |
| M43 | ledger header | header `==` → `!=` | killed | A: ledger emptied |
| M44 | met composition | `missing == 0` dropped from `met` | killed | v_flag_missing: rc 1→0 (met=True with flags_missing=1) |
| M45 | flags leg | knowledge-file scan dropped | killed | v_flag_missing: flags_missing 1→0 |
| M46 | flags leg | SOURCES-section listing scan dropped | killed | v_sec_list_missing: detail disappears |

Tally: **43 killed / 3 survived / 0 inconclusive**. Every killed mutant has its fixture, rc transition and first differing output line recorded in `out/M1Ctr/results.json` and `out/M1Ctr/mutants.tsv`.

## 5. Findings (survivors)

- **F1 (M18, equivalent-on-population).** The weak-number fallback (`elif weak and not any(covered(n) for n in weak)`) can only fire when the filtered strong set is empty while weak numbers exist. Scan over the frozen population: **0 of 91 rows** have weak-only citations (and 0 rows cite a strong line beyond EOF), so no legitimate round-46 ledger row can reach the leg. Not a defect — the leg is a safety net — but it is **untestable within the frozen contract**: a killing fixture would need a population row citing only weak numbers, which would require changing the frozen BASE `0163fea2…`. Coverage gap, no action possible in-place.
- **F2 (M19, equivalent-on-population).** Dropping the `n <= len(ptext)` filter on strong cited lines changes nothing: no population row cites a strong line beyond its pinned file's length (same scan). Same shape as F1.
- **F3 (M27, equivalent — dead condition).** In the drifted rule, `not all(r is None for r in rr)` is implied by the witness_new rule that runs immediately before it: if every release element were `-`, then `R` is the empty string and `wn not in R` is true for every `wn` (and `len(wn) < 12` already rejects `-`/empty), so `check_row` returns at the witness_new rule and never reaches the tail. Empirically zero output difference on all 27 fixtures. Harmless redundant logic in the counter; recording it so a future editor doesn't mistake it for load-bearing.

## 6. Note on M26 (killed — the leg is load-bearing only via out-of-order ranges)

For in-order ranges the `not all(eq)` leg of the holds-reworded rule is shadowed: an all-eq row has `P == R ⊆ RF`, so the witness_pin rule (`wp not in RF`) already rejects it (demonstrated by `v_hr_all_eq`: no output difference for M26). The leg **is** reachable through out-of-order range lists with boundary witnesses: `v_hr_all_eq_ooo` pins S001's duplicated line `-H "Content-Type: application/json" \` (pin lines 790/1403, release lines 799/814/879/1494, all non-adjacent), sets `pin_lines=790,1403` / `release_lines=814,799`, and uses the boundary string `…json" \ -H "Content-Type: application/json" \…` as both witnesses (in P/R, absent from PF/RF). Pristine rejects it (`holds-reworded rule`), M26 accepts it (rc 1→0, met=True) — killed. The counter does enforce "holds-reworded means actually reworded".

## 7. Integrity / commands

- Lane counter untouched before/after: `sha256sum tools/round46-release-recheck-audit.py` = `502e6f57…` both times. No tool installs were needed (python 3.14.8, git present); pacman untouched. Fixture commits only inside `$S/repos/A` (`git rev-parse --show-toplevel` asserted == fixture dir before every commit); no git/jj mutation in the lane or fleet repo.
- Reproduce: `python3 m1.py build` (construct+validate ledger) → `python3 m2.py repos` (27 fixture commits) → `python3 m2.py pristine` (baselines + assertions) → `python3 m2.py mutants M01 M46` (sweep). Scripts and full machine results copied to the out directory.
- Scratch `/fast/scratch/hyaku/kama-r46/M1Ctr` removed after artifact copy (declared disposable by the operator directive).

Report: .ufo/waves/round-46/w1/out/M1Ctr.md
