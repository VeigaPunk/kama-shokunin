# CR02SetterCounter — attack on frozen C2 counter (depth)

## Scope
Frozen counter `tools/round94-setter-sweep.py` at M2=6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623; SKILL.md + SOURCES.md extracted at M2 into out dir. Each forgery = one targeted SKILL.md (or SOURCES.md) variant run with `--skill-file/--sources-file` (predicate-mode exit 1 by design; "passes" = counter prints `unbound=0 missing=0 derived_disagree=0 decisions=2/2 met=True` despite a misstated row).

## Commands and outputs
- Baseline: `python3 tools/round94-setter-sweep.py --repo . --rev M2 --work <scratch> --skill-file SKILL-M2.md --sources-file SOURCES-M2.md` → rc=1 (by design when overrides given), `SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True` — predicate logic itself met.
- Forgery runs: ~28 variants in out dir (G03, G04, G05, G06, G08, H06, J02, K02, K03, L03, L04, N2, O4, O5a, P1, H01, H02, H03, H04, J01, K04-K06, L01, M01-M02, N1, O1-O2, Q2-Q4). All preserved in out dir as `*.md` (+ `J01/J02 *-sources.md`). Each run ~7-13s download+verify.
- Boundary audit: `curl api.github.com/repos/ggml-org/llama.cpp/git/trees/b12177?recursive=1` — 0 `.c` files under common/+tools/, 0 `.cc/.cxx`; `common/base64.hpp` is the only in-scope `.hpp`, contains no setter line. Outside roots: 942 C++ files (app/, examples/...); `app/llama.cpp`, `app/download.cpp` grep for POP_RE/AIP/Llama_arg → empty. Boundary-hiding forgery impossible at b12177 — noted not proven for Pop pattern hits in app/ bundled paths beyond the two checked.

## Findings

BLOCKER — Value cell unchecked whenever RHS is not an integer literal (`INT_RHS = \d+;` only): P50 free-port → `8080` (G03), P13 parsed-N → `99` (G04) both score perfect. 7+ override rows use non-literal values (`the parsed PORT`), same hole. Source: `tools/round94-setter-sweep.py:53,246-253`. Files: `G03-fakefreeport.md`, `G04-fakeN99.md`.

BLOCKER — Entry cell never checked except D-set non-{other,unrelated} membership: cli→server relabel (G05) scores perfect; declares-row entry→`other` (K02) scores perfect. Only wrong ENTRY among D-set members with effect overrides/default would flip want/got. Source: grade_p lines 236-237 (enum only), 337-338. Files: `G05-entry.md`, `K02-declares-entry-other.md`. NOTE: claims V4 expects an `entry-point` finding; `grep` shows no such string in counter (only docstring prose).

BLOCKER — Effect cell `default`↔`overrides` swap undetectable (G06 P19, G07 P38): both map to D-set the same way, no derived rule distinguishes them, though they decide which rows R18/R19 claim *set* vs *default* — the semantic core of the section. File: `G06-eff.md`, `L01*` (via P91). Source: lines 240-253 (B4/B5 only).

BLOCKER — Condition cell unchecked outside `common/arg.cpp` add_opt blocks, and config.ini-route rows P01-P10 deliberately unchecked: P03/P10 condition → `x` scores perfect (L03, L04) because `arg_block()` returns None for them and the `ex ==` fallback does not apply (they are *not* in add_opt blocks — the exact mis-detection probed). So 10/92 rows (all config-route rows) have prose-level semantic errors invisible. Files: `L03-configroute-cond-garbage.md`, `L04-configroute-cond10.md`. Source: lines 260-276.

DEFECT — Scope cell unchecked for 45/92 non-arg.cpp rows (K03 `totally unrelated scope text` perfect); arg.cpp rows checked only for exact `set_examples` + first-option substring. Files: `K03-scope-garbage.md`. Source: 260-276.

DEFECT — Decision cell must only *name* ids (`\b(Pnn)\b` word search): negation ("NO rows P19..."), wiped prose (P1), dropped config.ini/argv-order sentences all score perfect. Claims V5's `decision-wording` finding does not exist in code; R18/R19 can state the *opposite* port/slot verdict while naming the right ids. Files: `H06-negation.md`, `P1-R18-decision-wiped.md`, plus F10 attempt. Source: 344-345.

DEFECT — Row id is free: renaming P38→P93 everywhere (P-row + R18 id list + R18 decision text) scores perfect (N2). Duplicates keyed only on (file,line); no id-sequence/anchoring check. File: `N2-rename-id-everywhere.md`. N1 (rename without R18 fix) correctly fails `setter-set`.

DEFECT — Source check is substring per file, SOURCES.md itself is ungraded: fabricated S999 row citing arg.cpp + P12 source→S999 scores perfect (J02). SOURCES.md rows can be invented/edited freely. K3 (cite unfrozen source) is therefore not mechanised. File: `J02-fake-source-row.md`. Source: 254-256. (J01 swap to wrong-file S-id correctly fails `source`.)

DEFECT — HTML comments/fences do hide rows, but `missing` catches it (H01b outside-section, H02 dup-heading duplicates=92, H03 fence-open missing=38) — not exploitable alone; only usable combined with N2 id-shuffling. Backtick-stripping allows formatting-only differences (O4 no-backticks perfect, benign). Files: `H01b-outside-section.md`, `H02-dup-heading.md`, `H03-fence-open.md`, `O4-no-backticks.md`.

NOTE — Checks that *do* work: wrong integer literal (G01 `value-literal`, G02), scope order in add_opt blocks (L01 P13 `derived`), param/token mismatch (H04 `parameter-token`), effect `copies` moving a row out of D-set (K01), dash-param (O1), declares-with-value (O2), fabricated line/off-by-one/.c (M01/M02 `fabricated`), R18 param header (K05 `header`), dropped decision id (K06 `setter-set`), wrong derived option in condition (K04 `derived`). Files in out dir.

NOTE — M2 measured receipt claims counter bytes identical to freeze; my runs never modify the counter.

FIELD — Smallest safe correction (does not change frozen predicate; for L1 to adopt in round 95+): (1) apply `INT_RHS`-style literal check to *all* value cells (reject words where the source line has a literal; require prose citation only for truly symbolic RHS, with a named quantifier `free-port|parsed-N|AIP_HTTP_PORT` checked against the source token); (2) add entry-cell exact check against a frozen per-key table (derived from an explicit reviewed mapping artifact like `controls/c2-build-candidate.py` output), and effect∈{default,overrides} membership check per row family; (3) extend derived checks to config-route rows (condition must contain the route's own token, e.g. `load_from_ini`/`apply_to_params`, scope must equal a frozen set); (4) decision cell: require it to state the default value literal (9931/1/4/-1) and to forbid negation via a simple `no |not |none of these|never` blacklist, or grade decision prose against a frozen template; (5) treat SOURCES.md as graded artifact — validate new S-rows against census schema + require the row's `anchor` cite the claimed line number. Without at least (1)-(3) a wrong port/slot/default/default-vs-override claim is a perfect-score forgery — the K2 semantic gate remains the only protection, contrary to C2's stated "counter grades the mechanism" claim.

## Deliverables
Out dir `.ufo/waves/round-94/w1/out/CR02SetterCounter/`: SKILL-M2.md, SOURCES-M2.md, and ~38 forgery variants listed in Commands. Catalog table below.

| Forgery file | Misstatement | Counter result |
|---|---|---|
| G03-fakefreeport.md | P50 value 8080 for free-port syscall | perfect (BLOCKER) |
| G04-fakeN99.md | P13 value 99 for parsed `-np N` | perfect (BLOCKER) |
| G05-entry.md | P50 entry cli→server | perfect (BLOCKER) |
| K02-declares-entry-other.md | P18 declares entry server→other | perfect (BLOCKER) |
| G06-eff.md | P19 overrides→default | perfect (BLOCKER) |
| L03/L04 | config-route condition→`x` | perfect (BLOCKER) |
| K03-scope-garbage.md | non-arg.cpp scope garbage | perfect (DEFECT) |
| H06-negation.md / P1-R18-decision-wiped.md | R18 decision negated/wiped | perfect (DEFECT) |
| N2-rename-id-everywhere.md | P38 renamed P93 everywhere | perfect (DEFECT) |
| J02-fake-source-row.md | invented S999 | perfect (DEFECT) |
| O4-no-backticks.md | text cell without backticks | perfect (benign) |
| G01/G02/L01/J01/H04/K04-K06/M01-M02/N1/O1-O2/Q2-Q4 | literals, derived, header, fabricated, duplicates | caught (NOTE) |

VERDICT: holds — counter's frozen predicate met, but semantic misstatements (value, entry, effect) score perfectly; K2 remains the only semantic gate.
