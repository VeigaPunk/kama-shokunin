# CR02SetterCounter — attack on the frozen C2 counter (kama r93 w1)

## Scope
Attacked `tools/round93-setter-rows.py` (bytes `367eed2f16d4d240170ed0bc8c96f6a9c6f1c2593b2b380e4f467e963f0ea185`
at freeze F, at M2 and in the worktree — K1 holds) beyond disclosed limit L1, using SKILL.md/SOURCES.md copies at
M2 `ee19acbdabc8ac572e82ae56459c364457895b06`. No frozen predicate changed, no lane file edited, nothing judged.

## Commands and outputs (true exit codes)
- `python3 tools/round93-setter-rows.py --repo <clone> --rev ee19acbd… --work <scratch> --archive <pinned>` → **exit 0**,
  `population=48 rows=48 bound=48 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0
  decisions=2 decisions_bound=2 archive_sha256=f50a52f4…` (`baseline-M2.out`) — byte-for-byte the same summary as
  `.ufo/waves/round-93/measured/c2.out`. Uptime at start: load average 89.91 (no timing claim made).
- `probe-argblock.py` (arg_block vs an independent paren-depth reading of every arg.cpp population line) → exit 0,
  `argblock-probe.out`.
- `census.py` (independent port/slot census of `common/`+`tools/server/` @ b12177) → exit 0, `census.out`.
- `forgeries.py` (31 mutations through the real CLI `--skill-file/--sources-file`) → exit 0, `forgeries.out`,
  14 passes / 31.
- `forgeries2.py` (7 placement/id mutations with checkable fields left valid) → exit 0, `forgeries2.out`, 6 / 7.
- P05–P07 re-labelling probe → `p05p06p07-labels.out`.
- `git diff --stat ee19acbd…master -- SKILL.md tools/round93-setter-rows.py corpus/SOURCES.md` → empty: the section,
  the counter and SOURCES are unchanged at the current tip `4854ce0405e5157fb1f0da39d058a95411f33751`, so every
  result below also applies there.

## Findings

**NOTE-1 — the predicate holds at M2, and it is not vacuous.** 47 derived comparisons for 48 rows = 23 in-block
arg.cpp rows × 2 (first long option + `set_examples` list) + 1 for P01 (arg.cpp:1373, outside any
`add_opt(common_arg(` block, rescued by the 2-line `ex ==` fallback). My independent reading of every enclosing block
agrees with `arg_block()` on all 23 rows (`argblock-probe.out`), so **no arg_block mis-detection at M2** and no row
sits in the zero-check state. Ceiling is reached: an arg.cpp population line that is neither in a block nor preceded
by `ex ==` within two lines would silently get *no* derived check (`grade_p`, counter:266-279 fails open, not closed).
Not reachable at M2 or in the b12177 population.

**DEFECT-1 — L1 understates the counter's blindness: 20/38 forgeries bind with a misstated field.** Measured passes,
with the counter line that lets each through:
- value cell on a non-integer right-hand side — P37 "8080", P36 "else 8000", P03 "(0 kept; -1 refused)" bind
  (INT_RHS only pins `port|n_parallel = <int>;`, counter:254). **Not in L1** (B5's docstring documents it).
- arg.cpp *condition* semantics — P11 condition rewritten as "`--embd-gemma-default` is never parsed; 8011 arrives
  only through `--port`" binds: only token containment is checked (counter:270-274). **Not in L1** (L1 names only
  *non-arg.cpp* conditions).
- arg.cpp *effect* — P11 (8011 preset override) relabelled `copies`/`-` and dropped from R16 binds; R16's overriding
  set is recomputed from `seen`, so consistency is self-fulfilling (counter:344). **Not in L1** (L1 names only
  non-arg.cpp effects).
- P-ids are unverified labels — P27/P28 ids swapped, and P28 renamed to `P01` (two rows sharing an Id) both bind;
  rows are keyed by (file,line) (counter:230-236), ids are never deduplicated or compared to anything. **Not in L1.**
- section membership — a misstated row binds under a **second copy of the `##` heading 1700 lines earlier**, and in a
  `###` block appended *after* the section's Limit paragraph: `section_rows` ends only at the next `## ` (counter:142-152),
  so "the section" is neither a unique nor a table-bounded object. **Not in L1.**
- L1-covered passes reproduced: effect relabel on non-arg rows (P41, P28→`default` 80, P46→`-`/`unrelated`), trace
  text promoted to setter (P34 as `copies`, and as `overrides` + added to R16), decision wording (R17 ids only inside a
  negation; R17 restating P12 as 4 slots; extra false clause about P48 in R16), repeated id in the overriding set.
Caught (proves the checks that do exist fire): text edit, fabricated key, duplicate key, 11-cell row, integer value
mismatch, scope permutation, scope extra name, decision value, short overriding set, wrong source id, stale duplicate
S-row placed first, comment/fence hiding, row before the heading, heading variant, unrelated-pairing.

**DEFECT-2 (K2 candidate, adjudication is the reviewer's) — P05/P06/P07 parameter and effect cells contradict the
section's own vocabulary.** The lines are an option declaration (`{"-np", "--parallel"}, "N",` arg.cpp:2526), an
`n_parallel` assignment (`params.n_parallel = value;` :2529) and an env declaration
(`.set_env("LLAMA_ARG_N_PARALLEL")` :2531), but the rows say parameter `-`, effect `unrelated`. The vocabulary in the
section is "`declares` (names an option or env, sets nothing) … `unrelated` (another variable, or text)". The counter
is indifferent: P05/P07 → `n_parallel`/`declares` and P06 → `n_parallel`/`copies` all still print bound=48
(`p05p06p07-labels.out`). Counter-measure that does not cost a decision change: define `unrelated` in the section as
also covering "a setter the condition confines to a non-llama-server start" (relabelling P06 `overrides` would drag it
into R17's overriding set, which is wrong for llama-server).

**NOTE-2 — P37's condition omits a refusal the counter cannot see.** `--port 0` with 2+ TCP hosts is rejected before
the bind (`server-http.cpp:135-137`, "`--port 0 is not supported with multiple TCP addresses`", `init` returns false),
so R16's "0 binds any free port" holds for the single-TCP-host default only. No population row shows the listen port
set otherwise, so K2's second clause does not fire; the condition is incomplete, not contradicted.

**NOTE-3 — POP_RE is a line pattern; the census of what it misses is closed and harmless here.** Missed shapes are
every `*_port =` / `*_parallel =` assignment (`\b` fails after `_`): `params.reuse_port = true;` (arg.cpp:3328),
`serv_addr.sin_port = htons(0);` (http.h:301), `const auto bound_port = srv->bind_to_any_port(host);`
(server-http.cpp:509), `cparams.n_seq_max = params.n_parallel;` (common/common.cpp:1729), `SERVER_ENV_ROUTER_PORT`
(server-models.cpp:1235). Each value reaches a named row (P30/P37/P43/P41) or sets nothing of the listen port, so the
disclosed "value through another name" limit covers them; none changes what R16/R17 state.

**NOTE-4 — K3 is not enforced by the counter.** B6 accepts any S-id whose cells contain `/b12177/<file>`; nothing checks
"opened this round". Today each of the 9 files maps to exactly one first-wins S-row (`census.out`), so a swap is caught
(P27→S598 fails); a future SOURCES edit is the only thing standing between a stale citation and a green.

**NOTE-5 — the `comment_inside_cell` and `dupe_heading_no_rows` variants pass correctly** (the renderer strips the
comment, an empty second heading adds no rows): not gaps, recorded so the pass count is honest.

## Deliverables (in `.ufo/waves/round-93/w1/out/CR02SetterCounter/`)
`baseline-M2.out`, `argblock-probe.py`/`argblock-probe.out`, `census.py`/`census.out`, `forgeries.py`/`forgeries.out`,
`forgeries2.py`/`forgeries2.out`, `p05p06p07-labels.out`, `snippets.txt`, `SKILL-M2.md`, `SOURCES-M2.md`.

VERDICT: partial — the C2 predicate reproduces exactly at M2 (48/48, both decisions bound, 47 derived checks) and no
shipped row misstates a field the counter checks, but 20/38 forged variants bind, four of those classes (arg.cpp
effect, symbolic value, arg.cpp condition semantics, id/placement) are absent from L1, and P05–P07's parameter/effect
cells are a live K2 candidate.
