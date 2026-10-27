# MT04FalsifiableGaming — round 60 w1, C2 counter `falsifiable()` falsification probe

Axes: **calibration** (do accepted predicates actually test the documented statement?) and
**operability** (does the counter accept/evaluate/bind/score without silent failures?).
Method: importlib-load the pristine `tools/round60-c2-counter.py` against the committed
receipt `.ufo/waves/round-60/live/receipt.json`; run `safe_compile` → `evaluate` →
`falsifiable` on 18 crafted predicates (2 controls + 16 adversarial), then a full
`score()`+`controls()` pass on a synthetic all-vacuous registry. Lane bytes never written;
no live Ollama needed (C2 is static); no git/jj mutations anywhere.

## Baseline (detector sanity, pristine bytes)

| id | expr | safe_compile | evaluate | falsifiable | verdict |
|----|------|--------------|----------|-------------|---------|
| P01 (honest control) | `c['tags']['models'][0]['name'] == 'kama-b61c98ad5747:latest'` | accept | True | True | counts as sensitive — baseline passes |
| P02 (trivial control) | `True` | accept | True | False | killed — baseline conclusive, not inconclusive |

Pristine hashes: counter `d2e9a722416b8e482224dc2e6e17ced14bb87fb0ebd7de4464b04776b86a8fe5`,
receipt `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6`; identical after
all probes (`hashes_stable: true` in probe-results.json). Receipt `caps_ok=True`, 10 captures,
population = 14 lines (matches the frozen claim).

## Survivors — accepted, verdict-bound, `falsifiable()=True`, yet semantically irrelevant

All eight evaluate `True` (bind `confirmed`), flip under some capture mutation, and test
nothing the quoted statement documents. Exact expressions:

1. `c['ps-before'] == c['tags-empty']` — the two captures have **identical bodies and equal sha256** (`a6fe9ec6e26a38d99fca418b69826e0238b7a2bb319ff05eb153a6fcfd1fa28d`), so this is a tautology on the committed receipt; it flips only because the two chains are different paths.
2. `c['tags-empty']['models'] == c['ps-before']['models']` — same tautology, field level.
3. `str(c['ps-before']) == str(c['tags-empty'])` — stringification dressing on the same pair.
4. `any(m['name'] or True for m in c['tags']['models'])` — reads `name` but `or True` makes name content irrelevant; passes falsifiability only via the empty-list mutation, so it degenerates to "tags.models is non-empty".
5. `c['ps-after']['models'][0]['name'] == c['ps-after']['models'][0]['model']` — different keys, always equal in the committed data; `name==model` is incidental here.
6. `c['version']['version'] == '0.40.11'` — genuine capture read, but attachable to **any** quote: nothing links predicate fields to the quoted sentence.
7. `1 if c['version']['version'] == '0.40.11' else 0` — IfExp with constant branches, same attachment freedom.
8. `c['v1-models-empty']['data'] is None` — flips only under the `sent` mutation (a string is not None); reads a field no statement mentions.

**End-to-end demo (the headline):** a synthetic 14-row registry whose 5 evaluated predicates
are survivors 1/4/3/7/5 and whose other 9 rows are `not-observable` fillers scores
`met=true, errors=0, covered=14/14, evaluated=5, sensitive=5, bound=5, receipt_ok=true`,
**and** all five control families still reject their own mutants on it
(`tautology 1/1, verdict_flip 5/5, quote_corrupt 14/14, drop_line 14/14, tamper 1/1`).
The counter therefore cannot distinguish a fully vacuous registry from an honest one: the
tautology control replaces predicates with `True` (killed — no `c` chain), but every
"reads *some* capture" tautology sails through. Root cause: the docstring's contract
("predicate is falsifiable … its recorded verdict equals its evaluation") is enforced,
but there is no quote↔predicate semantic linkage. Full machine-readable evidence:
`.ufo/waves/round-60/w1/out/MT04FalsifiableGaming/probe-results.json` (`demo` key).

## Killed mutants (actual outputs, for calibration of the detector itself)

| id | expr | compile | evaluate | falsifiable | why |
|----|------|---------|----------|-------------|-----|
| P02 | `True` | accept | True | False | no `c` chain to mutate |
| P05 | `sorted(c['tags-empty']['models']) == sorted(c['ps-before']['models'])` | accept | True | **False** | predicted survivor, actually killed: `sorted(None)` raises → `evaluate` None → no flip. Wrapper functions that raise on `None` mute sensitivity. |
| P09 | `c['tags']['models'][:0] == []` | accept | True | False | `chains()` drops Slice slices → silent auto-reject of an honest read |
| P10 | `c['tags']['models'] == c['tags']['models']` | accept | True | False | same path on both sides; mutation hits both |
| P11 | `c['tags']['fabricated_field'] == 'x'` | accept | **None** | False | nonexistent field → silent skip; see diagnostic gap |
| P12 | `c['generate']['done'] != False` | accept | True | False | `!=` on scalar leaves never flips (`None != False` is still True) while `==` flips under `none` — structural asymmetry |
| P15 | `any(m == m2 for m, m2 in zip(...))` | reject `call not allowed` | — | — | zip closed |
| P16 | `len(c['tags']['models']) == 1 or True` | accept | True | False | top-level `or True` removes the only flip channel (contrast P04-vs-P07: `or True` survives only inside a comprehension) |
| P17 | `c['version'].__class__ == dict` | reject `node Attribute not allowed` | — | — | attribute escape closed |
| P18 | `(c := c) == c` | reject `node NamedExpr not allowed` | — | — | walrus escape closed |

## Operability / diagnostic findings

- **Silent skip on `evaluate` None** (P11): a predicate naming a nonexistent capture field leaves `errors` at 0; `met` flips only through the aggregate `good_rows == len(rows)` check. Demo B: 14 rows, one P11 row → `errors=0, good=13, met=False`. The operator sees a bare failure with no pointer to the malformed predicate.
- **Slice blind spot** (P09): `chains()` ignores `Slice` subscripts, so slice-based predicates are auto-rejected with no diagnostic — indistinguishable from a genuine tautology.
- **Flip channels are only** leaf→`None` (kills `==`), leaf→`"SENTn"` string, leaf→`""`/`[]`/`{}`. Integer/bool leaves are only supportable with `==`; `!=` on them is structurally impossible to certify (P12).

## Proposed tightening (fix-shaped, not applied to the lane)

1. **Quote↔predicate linkage (main fix):** derive required capture roots from the row's quote text — e.g. quote contains `api/tags` → `chains(tree)` must include a root in `{tags, tags-empty}`; `api/ps`/`expires` → `{ps-before, ps-after}`; `version` → `{version}`; `api/show` → `{show}`; `api/generate` → `{generate}`; `/v1/` → `{v1-*}` — and require `chains(tree) ∩ required ≠ ∅` before counting the row.
2. **Reject always-equal cross-capture Eq:** for `Compare(Eq|Is)` whose two sides are `c`-chains, reject when the two captures' committed bodies have equal sha256 (`ps-before` vs `tags-empty` case).
3. **Reject constant dressing in the AST:** `BoolOp` with a `Constant` operand (`or True`, `and False`), `IfExp` whose branches are both `Constant`, and unary `not` of a `Constant`.
4. **Surface `evaluate` None:** count skipped predicates in `errors` (or a separate diagnostic counter) instead of the aggregate-only failure.
5. **Close the Slice blind spot:** teach `chains()` to descend `Slice` subscripts or reject `Slice` explicitly in `safe_compile` with a message.
6. **Document or normalize the `==`/`!=` asymmetry** (e.g. add a value-substitution mutation mode) so honest `!=` predicates are certifiable.

## Commands, exit codes, bounds

- `TMPDIR=$S python3 $S/probe.py` (S=`/fast/scratch/hyaku/kama-r60/MT04FalsifiableGaming`) → exit 0, all outputs above; results JSON + probe source copied to `.ufo/waves/round-60/w1/out/MT04FalsifiableGaming/`.
- `bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status` → `/fast/scratch/hyaku 27% used, 591.2G free` — no ENOSPC.
- Restoration evidence: lane tree never written; `sha256(counter, receipt)` identical before/after every probe (`hashes_stable: true`). No tool installs this seat (none needed). Scratch dir removed at yield; no lane git operations, no commits, no live server, no touched ports.
