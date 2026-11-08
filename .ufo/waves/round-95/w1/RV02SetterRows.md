# RV02SetterRows — K2 read of the round-95 setter section (kama r95 w1)

## Scope

Read-only K2 read of `SKILL.md` `## Listen port and slot-count setters (round 95 revision)` at `bba10f75`
(SKILL.md unchanged since M2 `beef8922`; `git diff c798e831..ca531563 -- SKILL.md` = +145 lines, the new section only;
SKILL.md sha256 `417c6f43…53b08dc6`).
All 106 P-rows compared to the pinned b12177 archive; P93–P106 and the relabelled P15–P17 read against ±40 lines
and callers; all 9 R20/R21 decision rows read for prose truth and id-set completeness. Counter blob
`f9218a69771392cadc54037f8522158eee449b16` = `c798e831:tools/round95-setter-sweep.py` (unchanged since freeze).
No lane file edited; no runtime probe started (only the pinned binary's `--help` read).

## Commands and outputs (exit codes)

1. `curl -sSL -o llama-b12177.tar.gz https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177; tar xzf` → exit 0;
   sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` (matches pin).
2. Python check of all 106 Text cells vs the archive (counter `split_cells` semantics: strip, backtick unwrap,
   `\|`→`|`) → exit 0; **106/106 match, 0 mismatches**.
3. `python3 tools/round95-setter-sweep.py --repo . --rev beef8922 --work <scratch> --archive <scratch>/llama-b12177.tar.gz`
   → exit 0; `SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0
   derived_checked=47 derived_disagree=0 entries=7 decisions=9 decisions_bound=9 met=True`.
4. Re-derivation with the counter's exact patterns (`tools/round95-setter-sweep.py:66-71`): round-94 `CFG_SUBSTR`
   → 92 lines, round-95 → 106; added = exactly the 14 P93–P106 lines; removed = 0. `common/preset.cpp:339`
   (`preset.name == "*"`) is **absent from both**.
5. Id-set equality script: all 9 decision ids equal the table's (param, entry) default/overrides rows; every such
   pair has a decision row.
6. `/home/vgpnk/.local/opt/llama-b12177/llama-{perplexity,imatrix,server,cli} --help` → exit 0; perplexity and
   imatrix both list `-np, --parallel N … (env: LLAMA_ARG_N_PARALLEL)`; server default −1, cli default 1.
7. `sha256sum server-context.cpp server-schema.cpp` → `e0e43f22…a973`, `7f4d7c35…6b54` (match the plan's S616/S617).

## Findings
### B1 — BLOCKER: the router-child slot count is still undecided and its carrier is still invisible

`SKILL.md:2267-2268` says the round-94 silence is cured ("its decision rows were silent for `cli` and
`router-child`") and `:2269-2272` "each entry now has its own `R20`/`R21` row … not a summary that silently omits
its entry." The 9 rows (`SKILL.md:2391-2399`) are port×{server,cli,router-child,shared,other} +
n_parallel×{server,cli,shared,other}: **no `R21 | n_parallel | router-child` row**, and no P-row for the carrier
that carries the router's argv into every child:

- `server-models.cpp:400` `base_preset(ctx_preset.load_from_args(argc, argv)),`;
- `server-models.cpp:771-774` comment "overlay router's own CLI args on top of every model preset so that e.g.
  `llama-server --temp 0` is honoured by all child processes" + `preset.merge(base_preset);`;
- `common/preset.cpp:479` (`load_from_args` keys by `LLAMA_ARG_*`) and `:37` (`to_args` renders `opt.args.back()`
  = `--parallel`);
- `common/arg.cpp:2515-2523` registers `-np/--parallel` (env `LLAMA_ARG_N_PARALLEL`) for `LLAMA_EXAMPLE_SERVER`;
  `server-models.cpp:268-286` does **not** unset `LLAMA_ARG_N_PARALLEL`, while `:316` overwrites only
  `LLAMA_ARG_PORT` — the asymmetry that decides port and not slots;
- `server.cpp:126-131` resolves the child's −1 to 4 only for an instance.

Grounding: round-94 receipt `.ufo/waves/round-94/w1/out/SC01SetterSweep/receipts/exp7_rt_par7.log:23-25` shows child argv `--parallel` `7`
and `n_slots = 7`; SC01 F1 named these carrier lines and measured 4/7/5/6/9. The counter cannot see them (step 4:
`server-models.cpp:400/:774`, `preset.cpp:37` not selected), so `missing=0`/`met=True` says nothing. A
router-child starter still has no row; item 2's promise and the plan's closure of SC01 F1 are false for this entry.
### B2 — BLOCKER: `R21 other` omits P16, which its own condition says reaches `other` tools

`SKILL.md:2297` (P16): Entry `cli`, Scope `LLAMA_EXAMPLE_COMMON`, Condition "reachable in llama-cli and **other
tools**, not llama-server". `SKILL.md:2399` (R21 other): ids `P52, P53, P54` only. Source: `arg.cpp:1405-1411`
(`add_opt` adds on `in_example(ex)` **or** `inherit_common && in_example(LLAMA_EXAMPLE_COMMON)`; the `else` at
`2524-2531` leaves `examples = {COMMON}`, `arg.h:23`), so `--parallel`/`-np` is registered for every non-server
example; `perplexity.cpp:1998` parses with `LLAMA_EXAMPLE_PERPLEXITY` and `:2008-2013` consumes `n_parallel`;
`imatrix.cpp:1832,1869` likewise. Empirical (step 6): the pinned `llama-perplexity --help` and `llama-imatrix
--help` both list `-np, --parallel N` with `(env: LLAMA_ARG_N_PARALLEL)`. The relabel `other`→`cli` moved the row
out of R21 other; the counter derives `want` from the Entry cell, so `met=True` cannot catch it. Per this seat's
litmus (a setter row for that parameter+entry missing from the set) this is a BLOCKER.
### B3 — BLOCKER: the claimed `preset.name == "*"` pattern token is not in the pattern; no row shows the `[*]` route

`SKILL.md:2263-2264`: "The pattern now includes the config.ini section-scoping lines
(`COMMON_PRESET_DEFAULT_NAME`, `preset.name == "*"`)". `CFG_SUBSTR` (`round95-setter-sweep.py:67-70`) has
`COMMON_PRESET_DEFAULT_NAME` but no `preset.name == "*"`; `POP_RE:66`/`ENTRY_SUBSTR:71` do not match it. Step 4:
`common/preset.cpp:339` `        if (preset.name == "*") {` is absent from both populations; the counter docstring
(`:14-16`) repeats the false claim. Line 339 is the selector routing `[*]` to `global` (`:341` `global = preset;`,
`:343` `out[preset.name] = preset;`); P08 (`arg.cpp:764`) only consumes `global`. So the `[*]` half of the shared
precedence, which `R20/R21 shared` (`SKILL.md:2394,2397`) require as tokens, has no source row.
### D1 — DEFECT: the `:43` copy does not carry llama-cli's own `port` into the embedded server

`SKILL.md:2265-2266` and P100's Condition (`:2381`: "the CLI's own `port` and `n_parallel` reach the embedded
server") are false for port: `cli-server.h:43` `        common_params server_params = params; // copy`, then
`:44` `        server_params.port = port;` (free port from `:35`), then `:48`
`            int res = llama_server(server_params, 0, nullptr);`. R20 cli (`:2392`) states the correct fact ("never
uses the parsed `params.port`"), so the section contradicts itself; the frozen C2 "Before" repeats it. The counter
docstring (`:12-13`) says only `n_parallel` — the accurate half.
### D2 — DEFECT: `R21 other` describes perplexity's clamps as sequential

`SKILL.md:2399`: "(`max(4, n_parallel)`, **then** `max(1, n_batch / n_ctx)`)". `perplexity.cpp:2008-2013` is if/else
on `hellaswag || winogrande || multiple_choice`: one clamp or the other, never both. P53/P54 (`SKILL.md:2334-2335`)
restate the expressions without the branch guard.
### NOTES

- N1 P106 (`:2387`) calls `n_cmpl` "the per-request slot field"; `server-schema.cpp:64-65` is `field_num("n_cmpl")`
  bounded by the slot count — completions-per-request, not a slot field.
- N2 P96 (`:2380`) "a named section is a `--models-preset` preset, never the caller's params": in the config.ini
  route the map is discarded except `default` (`arg.cpp:763-768`), so a named config.ini section has no effect;
  that reading belongs to the other `load_from_ini` caller.
- N3 P95 (`:2379`) "every other key keeps its own section" — subject should be the section name; P93–P106 Text
  cells are not backtick-quoted (P01–P92 are), which the counter accepts. N4: the frozen C2 predicate quotes
  `fabricated=0 derived_disagree=0`, but the counter prints `fabricated=0 derived_checked=47 derived_disagree=0`
  (step 3) — not a literal substring; all named metrics are present.
- N5 `R21 cli` (`:2396`) omits the config.ini `[default] parallel` route (round-94 c1 measured 5; `R21 shared`
  states it) and calls the same option's env a "plus"; `R21 shared` "1 for every tool" omits the server's −1
  substitution (`arg.cpp:1372-1373`), which P37 discloses.
- N6 The plan's token list requires "`auto` for router" but no R20/R21 `router` row exists (want never holds it);
  its parenthetical "(server, cli, router-child, shared, other) — 9 decision rows" reads as 5×2 while only 4 R21
  rows exist.
### Row-level verdict for the audit targets

P93, P94, P97, P99, P101–P105 hold. P95/P96 hold in substance (N2/N3). P98 holds as a line but its router-carrier
role is undisclosed (B1). P100 misstates port (D1). P106 holds with N1. P15/P16/P17 Text and Conditions hold; the
`other`→`cli` relabel creates B2. All 9 id sets equal the table's default/overrides rows — the table itself is
incomplete (B1/B2/B3), so `met=True` is not prose truth.

## Deliverables

- `out/RV02SetterRows/rowcheck.json` — 106-row text check, 9 decision id-set comparisons, absent carriers, sha256.
- `out/RV02SetterRows/counter.out` — full counter output at `beef8922` (exit 0).
- `out/RV02SetterRows/help-parallel.txt` — pinned-binary `--help` receipts + binary sha256s.
- This report. Scratch `/fast/scratch/hyaku/kama-r95/RV02SetterRows` removed after receipts were copied; no
  burner and no llama process started by this seat.

VERDICT: falsified — the counter meets, but the section still decides no router-child slot count (carrier absent from the pattern, no R21 row), R21 `other` omits the `--parallel` setter its own P16 condition says reaches other tools, and the claimed `preset.name == "*"` pattern token is not in the pattern.
