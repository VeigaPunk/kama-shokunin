# M11C2AttackBinding — C2 binding-family attack (round 62, kama)

Seat: M11C2AttackBinding (mutation-tester, attack item) · 2026-10-28 · axes: calibration
Milestone: falsify the C2 counter via the binding family (binding switched to an unallowed id; case/whitespace variants of an allowed id).
Report receipts: `.ufo/waves/round-62/w1/out/M11C2AttackBinding/`

## Verdict

**FALSIFIED (whitespace subfamily). Binding matching in `tools/round62-c2-counter.py` is not robust: a registry whose binding cell is an allowed id padded with leading/trailing Unicode whitespace scores identically to the pristine registry — covered 12/12, bound 12, errors 0, met-equivalent True. 8 of 26 probe variants ACCEPTED; all case variants, cross-bindings, unallowed ids and fragmenting separators REJECTED.**

Per the seat rule "an ACCEPTED variant is a falsification". The 8 frozen control families do not cover this: control family 3 (`binding`) only substitutes `live`→`selftest` (exact unallowed id) — no family probes whitespace or case, so no control rejects the mutant.

## Frozen bytes probed

| item | sha256 | note |
|---|---|---|
| `tools/round62-c2-counter.py` | `15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929` | `git show master:…`, byte-identical at tips 65d7cad0, dc5e1010 and a25dd0d9 (master advanced twice during the probe; the two instruments were untouched each time; `git status --porcelain` clean) |
| `registry/capability-claims-r62.tsv` | `6f8365c71983bb54058212439a7bc891bae1eb58f2b40a15bd7be91f88e62009` | 12 frozen rows + header |

Method: the master counter module was loaded from a hash-verified scratch copy and `score()`/`parse_registry()` reproduced exactly as the counter calls them; the stub scorer `(True, observed, True, False)` models a green live run so any change in the met-equivalent (`covered==population ∧ mismatches==0 ∧ errors==0 ∧ dead==0 ∧ bound>=population`, the same conjunction `controls()` uses) is attributable to binding acceptance alone. Each variant mutates exactly one cell of one row (smallest behavior-bearing point). Driver: `out/M11C2AttackBinding/binding_attack.py`; raw matrix: `c2-matrix.txt` / `c2-matrix.json`.

## Variant results (ACCEPTED = falsification)

Scoring output format: `covered=<n>/12 bound=<n> errors=<n> mismatches=<n>` + first error.

| # | variant | binding cell | result | scoring output |
|---|---|---|---|---|
| 0 | pristine (control) | `live` | (green) | covered=12/12 bound=12 errors=0 mismatches=0 |
| 1 | case upper | `LIVE` | REJECTED | covered=11/12 bound=11 errors=0 — `binding:live-ollama-lifecycle:LIVE` |
| 2 | case title | `Live` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:Live` |
| 3 | case mixed | `lIvE` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:lIvE` |
| 4 | case on 2nd row | `Selftest` (pin-watch) | REJECTED | covered=11/12 — `binding:pin-watch:Selftest` |
| 5 | case on 3rd row | `Scan` (digest-ledger) | REJECTED | covered=11/12 — `binding:digest-ledger:Scan` |
| 6 | case on 4th row | `CENSUS` (sources-registry) | REJECTED | covered=11/12 — `binding:sources-registry:CENSUS` |
| 7 | whitespace both sides | `␣live␣` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 8 | whitespace lead | `␣live` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 9 | whitespace trail | `live␣` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 10 | whitespace double | `␣␣live␣␣` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 11 | whitespace internal | `li␣ve` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:li ve` |
| 12 | NBSP trailing | `live\u00a0` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 13 | zero-width space | `live\u200b` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:live\u200b` |
| 14 | whitespace on 2nd row | `␣scan` (digest-ledger) | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 15 | cross-binding | `selftest` on sources-registry | REJECTED | covered=11/12 — `binding:sources-registry:selftest` |
| 16 | cross-binding | `live` on digest-ledger | REJECTED | covered=11/12 — `binding:digest-ledger:live` |
| 17 | unallowed id | `free` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:free` |
| 18 | empty id | `` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:` |
| 19 | notobs (1 row) | `notobs` | REJECTED | covered=11/12 — `notobs:live-ollama-lifecycle` |
| 20 | aggregate | every data row `␣<id>␣` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 21 | vertical tab | `live\x0b` | REJECTED | row line destroyed: covered=11/12 errors=2 `cols=3` |
| 22 | form feed | `live\x0c` | REJECTED | same fragmentation path, errors=2 |
| 23 | ideographic space | `live\u3000` | **ACCEPTED** | covered=12/12 bound=12 errors=0 mismatches=0 |
| 24 | case + ideographic | `LIVE\u3000` | REJECTED | covered=11/12 — `binding:live-ollama-lifecycle:LIVE` |
| 25 | space + vertical tab | `␣live\x0b` | REJECTED | row destroyed, errors=2 |

**8 ACCEPTED (7, 8, 9, 10, 12, 14, 20, 23) · 17 REJECTED · 1 green control.**

### Mechanism (observed, from master bytes)

`parse_registry()` normalizes every cell before any comparison — `cells = [c.strip() for c in ln.split('\t')]` — and `score()` then tests exact equality `t['id'] == row['binding']` against the manifest's allowed ids (`census/selftest/live/cell/scan`, one per capability). `str.strip()` removes leading/trailing Unicode whitespace (incl. `\xa0`, `\u3000`), so padded variants parse to the allowed id and are indistinguishable from pristine; case is preserved and rejected. Separately, `text.splitlines()` treats `\x0b/\x0c/\x85/\u2028/\u2029` as line breaks, so those characters fragment the row into `cols=` errors rather than reaching the binding test. The same strip applies to **all** cells (quote, run, pattern, verdict, observed), and the frozen TSV contract reads as byte-exact — the counter admits padded bytes the contract text does not.

Scope honesty: an accepted variant still resolves to the allowed template — `run_bound()` executes `tpl['run']` from the manifest, never the row's `run` cell — so live execution semantics are unchanged. The falsification is at the registry-bytes/contract level: the counter cannot distinguish the pristine frozen registry from a whitespace-mutated one (single-cell ` live ` mutant committed as fixture `4860400b019b96a588be48cce2b0d9416e8a5252` vs pristine `c936a693daa334ef6ea00309d903d136a6ec5880`, diff in `out/…/fixtures.txt`).

## End-to-end status (recorded, not attributable)

- Pristine live baseline: full real-counter battery on the pristine fixture → `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=8 canonical=62 controls_rejected=8/8 errors=0 met=False`, exit 1 (`out/…/c2-pristine-live.txt`). Per role rules **a baseline failure is inconclusive** — the mutant end-to-end run was therefore not launched. The scoring-layer pristine control (variant 0) is green and is the baseline for the matrix above.
- [INFERENCE] The 8 live mismatches are environmental: `run/` TMPDIR artifacts are empty (no `cc.json`, no `ollama/` dir) after ~3 min wall, consistent with fleet-contention failures of the live/scan rows, not binding behavior. No further attribution attempted (operator wrap-up: no new jobs).
- `--no-live` finding (advisory, read from master source): the stub scorer returns `sensitive=False`, so `mismatches` ≥ row count and `met=False` for **any** registry; and `controls()` still executes the full live battery even under `--no-live`. It can neither certify met nor cheaply re-score.

## Restoration evidence

Lane files never modified (all mutations in scratch/fixture). `out/…/restoration.txt`: lane working tree and master blobs for both instruments hash `15d11f1c…` / `6f8365c7…` before and after; `git status --porcelain` on the three cited paths empty; scratch copies byte-identical. Tooling installs: none. Scratch `/fast/scratch/hyaku/kama-r62/w/M11C2AttackBinding` deleted after receipt copy.

## Tally line

`binding-family r62 C2: 26 probes → 8 ACCEPTED (whitespace-padded allowed ids, incl. NBSP/ideographic-space and all-rows aggregate) / 17 REJECTED (case, cross-binding, unallowed, empty, notobs, \x0b/\x0c fragmentation) → FALSIFIED: parse_registry() str.strip() normalization makes binding matching whitespace-insensitive; no control family covers it`
