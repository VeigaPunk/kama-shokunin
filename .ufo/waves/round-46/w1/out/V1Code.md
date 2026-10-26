# V1Code — C1 counter code review (round-46)

**Verdict: 2 real defects (check-fragment.py false `VALID` for non-population ids — medium; counter blesses `removed` while anchored text survives verbatim inside a longer release line — low/medium), 2 low exit-code/UX defects, 1 low note; all four hinted leads (witness ranges-vs-whole-file, dash-in-R, newrow-with-base-id, /tmp use) were tested and REFUTED — the frozen counter matches its docstring everywhere I could reach. Counter integrity verified: working tree == freeze commit 5790944 blob, sha256 `502e6f57036fca803a081f844ea80f19e26c0dd782f329148d72b25b89861997` == preregistration `counter_sha256`.**

Everything below was run on fixtures under `/fast/scratch/hyaku/kama-r46/V1Code/` (now removed; raw outputs copied to `.ufo/waves/round-46/w1/out/V1Code/`). Line numbers refer to `tools/round46-release-recheck-audit.py` (= `counter-frozen.py` copy) and `.ufo/waves/round-46/tools/check-fragment.py` in the lane.

Method: (a) full diff of `round46-release-recheck-audit.py` against `round44-release-recheck-audit.py` (85 insertions, 41 deletions; the delta is exactly the two witness columns + witness rule, note >= 40, the newrow leg, and the frozen-name block); (b) 22 unit probes of `check_row`/`ranges` with a stubbed `git` serving a synthetic two-revision file (rig.py U1–U15); (c) end-to-end probes on a throwaway `git clone --shared` of the lane at 5790944 plus the real L1 upstream `llama.git` (E1–E9, real S037 bytes, pin `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` → blob `b168241076…`, b11906 `4d71b42f…` → blob `b6ebf75233…`). 45/45 final checks pass; the failures along the way were rig construction bugs, listed where relevant.

## Findings by severity

### F1 (medium) — check-fragment.py prints `VALID <id> <verdict>` for ids the counter never scored
- **Where:** `check-fragment.py:70-72`
  ```python
  for i in ids:
      hits = [x for x in lines if x.startswith(f"detail: {i} ")]
      print("\n".join(hits) if hits else f"VALID {i} {verdict.get(i)}")
  ```
  Absence of a `detail:` line is treated as proof of validity. But the counter only ever emits details for **population** ids (`round46-release-recheck-audit.py:333-346`, `for sid, ent in sorted(pop.items()):`); an id outside the 91-row round-44 population produces no output at all, and silence is misread as `VALID`.
- **Repro (real lane + real upstream, one command):**
  ```
  $ python3 kama-shokunin/.ufo/waves/round-46/tools/check-fragment.py frag-s999.tsv $PWD/chk /fast/scratch/hyaku/kama-r46/L1/llama.git
  VALID S999 holds            (exit 0)
  ```
  `frag-s999.tsv` = header + one row `S999  tools/server/server.cpp  704366d7…  b11906  <pb>  <rb>  1  440-462,493-515  440-462,493-515  -  -  holds  note irrelevant`. The counter's own output for the same run (e5.out): `rows=1 valid=0`, 91 `no ledger row` details, **none** for S999 — the row was counted, never scored, and the helper still says `VALID S999 holds`.
- **Impact:** a seat fragment with a mistyped id (S109→S190) or an id that is not `on-release`/`mined|queued` at base gets a green `VALID` line from the very tool whose job is per-row verification. This can put an unscored row into a seat's receipt as if the frozen counter had blessed it.
- **Proposed fix (black-box, no counter change):** parse `valid=V` from the counter summary line; the fragment ids without a `detail:` line must number exactly V. If there are more, print `NOT-IN-POPULATION <id>` for the surplus instead of `VALID` (and keep exit 0 semantics or fold into F4's fix). Alternative: import the clone's frozen counter module and assert `id in population(show(BASE, SOURCES))`.

### F2 (low/medium) — counter accepts verdict `removed` while the anchored text survives verbatim inside a longer release line
- **Where:** `round46-release-recheck-audit.py:287-291`
  ```python
  rset = {x.strip() for x in rtext}
  for p in pr:
      first = next((x.strip() for x in ptext[p[0] - 1:p[1]] if len(x.strip()) >= 8), None)
      if first is None or first in rset:
          return False, "removed: pin text still present"
  ```
  The survival check is exact-**line** membership only. A pin line absorbed verbatim as a substring of a longer release line escapes. The witness rule (line 272: `wp not in P or wp in RF`) does not catch it, because the witness may be *any* >= 12-char pin-only text from the ranges — not the surviving line.
- **Repro (unit, stubbed git world, rig.py U6):** pin line 10 = `survivor line shared tail epsilon`; release line 10 = `a much longer release line wrapping survivor line shared tail epsilon into prose`; ledger row `pin_lines=3-6,10  release_lines=-,-  witness_pin="the listener answers before any model load beta"  verdict=removed` → `check_row` returns **True**. The genuinely-rewritten block (3-6) supplies a legitimate witness while line 10's text survives.
- **Contract note:** the frozen docstring defines `removed` by exact-line absence, so this row is contract-compliant — this is a soundness gap against the *claim semantics* (preregistration C1: "removed" = the anchored statement vanished), not a docstring/code mismatch. Bounded in practice: the row still needs a pin-only witness and the flags legs.
- **Proposed fix (for a future freeze, not in place):** check **every** >= 8-char stripped line of each pin range for exact-line membership, not just the first — strictly stronger, and unlike a substring check over the whole release text it does not over-reject legit removed rows whose range happens to start with a generic line (`return 1;`).

### F3 (low) — unhandled non-git exceptions exit 1, which the contract reads as "not met"; docstring promises 2 for "could not evaluate"
- **Where:** `round46-release-recheck-audit.py:376-378` catches only `EvalError`; line 391 `return 0 if met else 1`. Any other exception aborts with a traceback and Python's exit 1 — indistinguishable from a legitimate `met=False`. Reachable path: line 232 `ptext = show(up, pin, path).splitlines()` — `show` (lines 126-128) returns `None` when `git show <rev>:<path>` fails while `blob`'s `rev-parse` succeeded (path exists at the pin as a tree/symlink-like object), e.g. a population row whose URL is a `/tree/` link. A `UnicodeDecodeError` from `subprocess text=True` under a non-UTF-8 locale is the same class.
- **Repro (unit, rig.py U11):** stub `show` to return a failed CompletedProcess while `blob` succeeds → `AttributeError: 'NoneType' object has no attribute 'splitlines'` propagates out of `check_row`; in `main()` the process exits 1.
- **Impact:** fail-closed (a crash marks the claim false), but the docstring's exit taxonomy ("Exit 0 met, 1 not met, 2 could not evaluate") is violated; an operator reading exit 1 concludes the re-verification failed rather than that the counter could not run.
- **Proposed fix:** broaden the handler — `except Exception as e: print(f"could-not-evaluate: {e}", file=sys.stderr); return 2` — or guard `show()` returning `None` in `check_row` (raise `EvalError`).

### F4 (low) — check-fragment.py exits 0 even when every fragment row is invalid
- **Where:** `check-fragment.py:73-77` — after printing per-row reasons it `return 0` unconditionally (only setup/eval failures return 2). The docstring documents the printing contract, but a scripted caller (`check-fragment.py frag chk && next-step`) cannot detect failure by exit code.
- **Repro (E6):** fragment with a wrong `pin_blob` → stdout `detail: S037 invalid: blob mismatch (want b168241076 b6ebf75233)`, **exit 0**.
- **Proposed fix:** return 1 when any id printed a detail line instead of `VALID` (keep printing the reasons).

### F5 (low, note) — ledger rows for ids outside the population are silently ignored by the counter
- **Where:** `round46-release-recheck-audit.py:333-346` iterates population ids only. A junk row (e.g. S999) inflates `rows=` but is never validated or rejected; E5's run shows `rows=1 valid=0` with no S999 detail. Inherited verbatim from round44 (same loop). Harmless for `met` (unverified counts population only), but it lets junk sit in a receipt unflagged. Docstring says "one row per population id", so this is within contract — noting for the record.

## Hinted leads tested and REFUTED (no defect; evidence per lead)

1. **"Witness built from ranges vs whole file"** — code matches the frozen docstring exactly. `P`/`R` are ws of the *claimed* pin/release ranges (lines 256-257, dash elements excluded from R via `for r in rr if r`), `PF`/`RF` are ws of the *whole* files (line 258); `witness_pin` must be in P and absent from RF (272-273), `witness_new` in R and absent from PF (275-276, 279-280) — exactly the preregistration's "pin-only and release-only text". Probes: U3 valid witnesses inside ranges → True; U5 witness inside the pin *file* but outside the claimed ranges → rejected `witness_pin rule`; U9b witness_new in the release *file* but outside R → rejected; U4 witness_new also present in the pin file → rejected; U7 witness_pin present in the release file → rejected. End-to-end on real bytes (E4b): S037 `holds-reworded` with `witness_pin="if (is_router_server) {"`, `witness_new="std::optional<server_models_routes> models_routes;"`, note 76 chars → `valid=1`, no detail, exit 1 only because the other 90 rows are absent (fixture ledger holds one row).
2. **"A dash release range in R"** — dashes cannot leak: `holds` rejects any dash element (U2 → `holds needs every pair text-equal`, since `eq` is False for a None pair, line 255/268); `holds-reworded` requires `all(r is not None)` (line 277); `drifted` permits a trailing dash with witnesses drawn from the non-dash part of R (U9 → True; U9b shows witness_new must come from the non-dash R); `removed` requires all dashes (E4d on real bytes → `removed: pin text still present`, the file is alive); `unchanged-file`'s string comparison (line 263) cannot match a dash because `pin_lines` parses with `allow_dash=False` (U12c).
3. **"newrow when the id exists at base"** — lines 356-358 build `base_ids` from **all** `| S###` lines at BASE (226 ids, superset of the 91-row population) and require `group(1) not in base_ids`. Direct dissection on real data: `base_ids size: 226; S001 in base_ids: True`; the boolean expression on a base-id line carrying `b11906` + `4d71b42f…` evaluates False; zero hits over the freeze tip. Fixtures: E3a duplicate `| S001 |` row with both tokens at tip → `newrow=0`; E3b `| S901 |` with both tokens → `newrow=1`; E3c `| S902 |` with `b11906` but no commit token → `newrow=0`; E3d both rows → `newrow=1`. No defect. *(Transparency: my first rig run printed E3a `newrow=1` — a rig artifact: v1 generated the same fixture directory for all four E3 variants because `"E3a"[3:]` is empty. Three controlled reruns — solo fixture, fixed rig, direct dissection of lines 356-358 — all give `newrow=0`; the counter is correct.)*
4. **"/tmp use"** — `grep -n '/tmp\|tempfile\|TemporaryDirectory\|mkstemp\|mkdtemp'` over both counters and check-fragment.py: **no matches** (exit 1). check-fragment materializes its fixture at `<scratch>/clone` (lines 40-45), refuses a scratch inside the lane (37-39; E8: `refusing: scratch inside the lane`, exit 2, nothing written), and removes the clone in `finally` (78-79). The counter writes only the caller-supplied `--out` (387-389; E1 verified the receipt equals stdout). No /tmp dependency anywhere.

## Verified good (plumbing, end-to-end on real lane + real upstream)

- **Counter integrity:** working-tree counter byte-identical to `5790944:tools/round46-release-recheck-audit.py` (diff empty); sha256 `502e6f57…` matches preregistration `counter_sha256`. check-fragment checks out FREEZE (line 45) and runs the clone's copy (line 64) — i.e. always the frozen counter.
- **E1:** counter at the freeze tip (no ledger) reproduces the frozen control `controls/base.c1.out` summary exactly: `pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 newrow=0 met=False`, exit 1; `--out` receipt equals stdout.
- **E2a/E2b:** exit 2 + `could-not-evaluate:` on stderr for a bogus `--tip` and for an upstream lacking `4d71b42f…` — matches the docstring's exit taxonomy on its specified paths.
- **E4a/E4d/E4e (real S037 bytes):** `holds` on a changed file → `holds needs every pair text-equal`; `removed` while the file is alive → `removed: pin text still present`; wrong `pin_blob` → `blob mismatch (want b168241076 b6ebf75233)` — blob re-derivation and verdict guards all enforce.
- **E4c/E7a/E7b (flags leg):** a valid `drifted` row with no section and untouched used-by files → `flags_missing=5` = 1 (SOURCES section) + 4 (each existing `corpus/knowledge/*.md` used-by); with the section line and all four knowledge files carrying `S037` + `b11906` → `flags_missing=0`; deleting one knowledge-file line → `flags_missing=1` with `detail: S037 not flagged in corpus/knowledge/llamacpp-loading-lifecycle.md`.
- **E6b:** check-fragment happy path — the E4b row as a fragment → `VALID S037 holds-reworded`.
- **E9:** check-fragment's `HEADER` string equals the counter's `HEADER` (13 columns, same order) — fragment rows cannot be silently misaligned.
- Unit coverage of the verdict machine: U1 holds-equal valid; U8a unchanged-file valid; U8b unchanged-file rejects witnesses; U13 note < 40 rejected; U14 holds needs changed=1; U15 non-40-hex URL ref falls back to the first 40-hex run of the anchor cell; U10/U10b cited-line rule (strong numbers must lie in pin_lines, uncovered strong line rejected); U12a-f range parsing bounds (1-81 rejected, 0 rejected, dash in pin_lines rejected, inverted rejected, dash allowed in release_lines, empty rejected).

## Coverage gaps (honest)

- **`met=True` / exit 0 was not exercised end-to-end** — it requires all 91 population rows valid, i.e. L1's in-flight ledger; that branch is `return 0 if met else 1` (line 391) with `met` fully determined by the four legs, each tested individually (unverified via E1/E4, flags via E7, section/newrow via E3).
- The `UnicodeDecodeError` variant of F3 was not reproduced end-to-end (it needs an upstream blob with non-UTF-8 bytes under a non-coercing locale); the demonstrated crash path is the `show()`-returns-None one.
- `cited()`'s strong/weak heuristics were spot-checked (U10/U10b) against synthetic cells, not exhaustively over all 91 real anchor cells; no escaped-pipe (`\|`) rows exist at base (grep count 0), so `cells()` splitting is safe for the frozen population.
- C2 (`tools/append-only-audit.py`) is outside this item's scope; not reviewed.

## Residual risk

F1 is the finding that can mislead a seat **this round**: a mistyped or foreign fragment id gets a green `VALID` line from the helper (mitigation while unfixed: a seat should confirm its ids appear in the frozen control's 91-id list, or check that the counter's `valid=V` equals the number of `VALID` lines printed). F2/F3/F5 are fail-closed or contract-compliant looseness; none invalidate the frozen contract. Per the freeze rules these are findings, not in-place fixes — the counter and check-fragment.py were not modified.

## Tooling record

No tools installed or upgraded (none needed); pacman untouched. No lane file was written except this report and the evidence copies under `out/V1Code/`; fixtures were `git clone --shared` throwaways with `rev-parse --show-toplevel` asserted before every commit; scratch removed at the end.

## Evidence files (copied before scratch removal)

`rig.py` (fixture driver, all probes), `counter-frozen.py` (byte-identical freeze copy), `e1.out`, `e2a.out`, `e2b.out`, `e3a.out`–`e3d.out`, `e4a…e4e.out`, `e5.out/.err`, `e6.out/.err`, `e6b.out/.err`, `e7a.out`, `e7b.out`, `e8.out`, `frag-s999.tsv`, `frag-badblob.tsv`, `frag-ok.tsv` — all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/V1Code/`.
