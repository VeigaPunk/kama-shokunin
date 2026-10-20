VERDICT: confirm — all 7 NonLoadingStatuses oracles (verdict, reason, exit) are correct against the landed `classify()` and the C1 rule; all 7 also pass on the frozen probe (they are the non-loading control family). Findings: one factually wrong `why` sentence, one wording nit, and one measured redundancy class inside the 5xx trio — no oracle needs changing.

Scope: `tests/probe-verdicts/NonLoadingStatuses.json` @ lane commit b8e485c, tested file
unmodified (`git diff --exit-code` → 0; `git hash-object` = `2c8ad1bc053c71e1bb4666d80af0d9cd99f93dec`
= `git ls-tree b8e485c`). Judged against `tools/kama-probe.sh:399-449`
(`body_has_model_array`, `body_is_llamacpp_loading`), `:451-566` (`classify`), and the C1
rule as stated in the round-16 assignment.

## What I ran (commands, exits, output excerpts)

1. `python3 --version` → `Python 3.14.8`, exit 0.
2. Current probe, exactly the 7 family rows:
   `python3 tests/probe-verdicts/check.py --json --only <each of 7 names>` →
   **exit 0**, `tests=7 passes=7 failures=0`, wall 3.76 s. Every row returned exactly its
   `expected` triple with `probe_exit=2`, `drift=true`; excerpt:
   `[PASS] NonLoadingStatuses.ok200-json-envelope ... verdict=FOREIGN_SERVICE reason=schema-unrecognized exit=2`
   … `[PASS] NonLoadingStatuses.err429-envelope ... verdict=FOREIGN_SERVICE reason=non-2xx-non-model-http exit=2`.
   Receipt: `/tmp/NonLoading-current.json` (probe sha `6edd3c4cfdf3…`).
3. Frozen-probe control, same 7 rows,
   `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh` → **exit 0**,
   `tests=7 passes=7 failures=0`. Frozen artifact identity checked first:
   `sha256sum` = `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` =
   `.ufo/waves/round-16/frozen/manifest.json:sha256`. So **0 of 7 rows discriminate the C1
   delta**; that is correct for this family and consistent with L1's 17-row changed set.
4. Mutation testing: 8 probes copied to `/tmp/kama-r16-FamilyNonLoadingStatuses/`, each differing
   from the landed probe only at the 503 gate (`tools/kama-probe.sh:503`) or the 2xx reason split
   (`:558-561`); each run through `check.py --probe <mutant> --json` with the same 7 `--only`
   names. Every mutant run exited **1** (failures), with this kill matrix:

   | mutant | rows that failed it |
   |---|---|
   | drop `F_CODE = 503` entirely (`m_any`) | all 7 |
   | accept any 5xx (`m_5xx`) | err500, err502, err504 |
   | accept any 4xx/5xx (`m_ge400`) | err500, err502, err504, err404, err429 |
   | accept 502/503/504 (`m_gw`) | err502, err504 |
   | accept 404/503 (`m_404`) | err404 only |
   | accept 429/503 (`m_429`) | err429 only |
   | always `schema-unrecognized` on 2xx (`m_always_schema`) | ok200-plain only |
   | always `non-model-2xx` on 2xx (`m_always_nonmodel`) | ok200-json only |

5. Canonical duplicate scan over all 72 rows (routes + `default_route` + `expected`, ignoring
   `name`/`family`/`why`/`expect`/`port_mode`): 5 duplicate groups exist corpus-wide, **none
   contains a NonLoadingStatuses row**. Also scanned every family for the exact loading envelope:
   the only other non-503 carriers are `AuthAndDead.401/403-carrying-loading-envelope`
   (different statuses and oracles), so no cross-family duplicate.
6. `pgrep -x llama-server` → exit 1 (empty). No server started, no port bound; 8080/34113 never
   probed.

## Row-by-row (observed = expected on both probes)

| row (path:line) | observed | why assessment |
|---|---|---|
| `ok200-json-envelope` :2-16 | FOREIGN_SERVICE / schema-unrecognized / 2 | accurate: 200 ⇒ gate skipped; no `data`/`models` array; CT `application/json` selects `schema-unrecognized` (`:558-561`) |
| `ok200-plain-envelope` :18-32 | FOREIGN_SERVICE / non-model-2xx / 2 | accurate. Verified its body bytes are identical to row 1 (`json.dumps(...,separators=(',',':'))` = the `body_text`), so CT is the only variable — a true differential pair, and the two CT mutants kill exactly one row each |
| `err500-envelope` :34-48 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | outcome + cause right; "error page" is imprecise (see Nit) |
| `err502-envelope` :50-64 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | accurate: the 503 test precedes the body matcher in an `&&` chain (`:503`), so a 502 body is never parsed |
| `err504-envelope` :66-80 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | accurate |
| `err404-envelope` :82-96 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | oracle right, rationale wrong (see Low finding) |
| `err429-envelope` :98-112 | FOREIGN_SERVICE / non-2xx-non-model-http / 2 | accurate |

No `why` in this file cites a `file:line` or upstream path (regex scan for `path:digits` over all
7: none), so the frozen-numbering citation risk **does not apply inside this matrix**.

## Findings by severity

- **Low — `err404-envelope` `why` is factually wrong about its own stub** (`:85`): "a route-less
  service echoing the body". The row defines an explicit `/v1/models` route that returns
  `404` **with** the envelope body (`:84-93`); a truly route-less service under
  `default_route: null` answers an empty 404 (that is how `/`, `/health`, `/metrics` behave in
  every row, see the `404| @ /` evidence fragment). Oracle unaffected (the non-2xx branch ignores
  the body), but the sentence points a reader at the `default_route` shape this row does not use —
  a conflation the build advice repeats ("404 is the schema's default_route shape"). Suggested
  text: "an explicit 404 route echoing the loading body".
- **Nit — `err500-envelope` `why`** (`:37`): "generic non-model error page". The body is JSON;
  an actual HTML page would take the earlier `html-non-model` branch (`:549-553`), not
  `non-2xx-non-model-http`. "response" is the accurate noun.
- **Low (coverage, not correctness) — the 5xx trio is mutually non-discriminating.** All five
  non-2xx rows share one oracle triple and one code branch (`:556-565`). Measured: `err500`'s
  kill set `{m_any, m_5xx, m_ge400}` is a strict subset of `err502`'s, and `err502`/`err504` have
  *identical* kill sets across all six gate mutants (including `m_gw`). `err404` and `err429` are
  interchangeable under every class-level mutant; each only catches a mutant keyed to its own
  literal status (`m_404`, `m_429`), and `m_404` is the more plausible of those two (a server can
  404 before its model route mounts). So the family evidences "the matcher requires 503" with
  **one class-level row plus literal pins**, not 7 independent confirmations. Recommendation: keep
  the literals as cheap documented pins (especially 404 and 502), do not add more 5xx rows, and do
  not count 7 rows as 7 independent checks in prose.
- **Info (adjacent file, not this matrix):** `build/advice/MatrixNonLoadingStatuses.md` cites
  "classify() (lines 415-525)", "line 477-479", "lines 513-523", "lines 458-461, 514-521". Those
  are *frozen* line numbers: frozen `classify()` starts at `:415`, landed at `:451`; the terminal
  FOREIGN block is frozen `:513-523`, landed `:556-565`. The oracle values themselves are right;
  if L1 quotes the advice, update the numbers.

## Residual risk / verification gaps

- No 1xx/3xx row. `fetch()` uses curl without `-L` (`tools/kama-probe.sh:286-301`), so a 302/307
  carrying the envelope would land `FOREIGN_SERVICE/non-2xx-non-model-http` untested. Out of the
  family's stated 4-10 budget, so a gap, not a defect.
- The 500/502/504 interchangeability rests on my six gate mutants plus two specific-literal
  mutants; [INFERENCE] that no realistic future mutant separates 502 from 504 other than one keyed
  to a single literal.
- These rows are python-independent: the 503 gate is never reached, and the `body_has_model_array`
  grep fallback also yields `has_models=0` for this body. [INFERENCE] — I did not exercise a
  python-less run (that branch is another seat's item).
- Only this family was exercised; I did not re-run the full matrix or `measure.py`.
- Mutation probes are synthetic edits of the landed script in `/tmp`; the landed probe's behavior
  is established by the two real runs (current and frozen).

## Limitations

No lane file was modified; scratch stays in `/tmp/kama-r16-FamilyNonLoadingStatuses/` and was
removed after writing. No model server was started (`pgrep -x llama-server` → exit 1).

Installs: none.
