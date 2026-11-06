# CR02ThresholdCounter — C2 counter attack (round 91, wave w1a2)

## Scope

Attacked `tools/round91-threshold-rows.py` (C2's frozen counter) with a scratch fixture repo
(`corpus/SOURCES.md` from M2 + a forged `SKILL.md` per variant) covering every forgery class my seat
names, plus three it did not. Re-ran the committed control and the predicate. Lane read-only; counter
bytes untouched; no tool installs.

M2 = `3f317ecd211e80929c673e306e3230be287fdf20`; counter sha256 `fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661`
identical at F `9a41912a598cad00f7ff08391586a0ef3732bbed`, at M2 and in the worktree (K1/K3 intact).

## Commands and outputs (exit codes)

1. `python3 tools/round91-threshold-rows.py --repo . --rev 3f317ecd…` → `rows=14 bound=14 unbound=0
   duplicates=0 engines=3 fetch_failures=0`, **0** (`c2-at-M2.out`; load 40.78). Predicate reproduced.
2. Same with `HTTPS_PROXY=http://127.0.0.1:1` (offline simulation): `unbound=14 … fetch_failures=14`, **1**
   (`c2-offline.out`).
3. `python3 .ufo/.../controls/c2-forgeries.py --lane . --scratch <scratch>` → **0**, identical to
   `controls/c2-forgeries.out` except the four fixture `rev=` hashes (`rerun-c2-forgeries.out`).
4. `python3 …/c2-forge-cr02.py --lane . --rev 3f317ecd…` → 14 variants, **0** (`c2-forge-cr02.out`).
5. `python3 …/audit-landed-rows.py 3f317ecd… .` → `AUDIT rows=14 non_exact=0`.
6. Line-ending simulation (module import, stubbed `fetch`): `lineendings.out`.

Upstream bytes fetched once and sha256-checked against S593/S594/S595 before any row was built.

## Findings

**DEFECT-1 — ten non-threshold rows meet the predicate (reproduced false green).** V1 binds
`#define COM_DBG(...) LOG_DBG("cmn  %12.*s: " …` (printf width 12), `COMMON_RECURSIVE_LIMIT 128`, a
**commented-out** enum member `//COMMON_SAMPLER_TYPE_TFS_Z = 5,`, a prose comment (`between 0.0 and 1.0`),
a log-level comment, a bind-address comment, `// Default is 5 minutes.`, `# SPDX-License-Identifier:
Apache-2.0`, and two mkdocs fence markers: `rows=10 bound=10 engines=3`, exit 0 (`c2-forge-cr02.out`).
V7 (`<details>`) and V8 give the same. **n>=10 carries no evidential weight.**

**DEFECT-2 — `engines` counts words, not engines.** V12: ten bound rows all citing S593 common.h with
engine cells `https b12177` / `raw b12177` / `github b12177` → `engines=3`, exit 0. B4 only needs the
first word to be a substring of the URL, and `https`/`raw`/`github` are substrings of any
raw.githubusercontent URL. **e>=3 is defeated**, so V4's single remaining gate is word choice, not
engine diversity.

**DEFECT-3 — pin is a substring.** V2: `llama.cpp b1217`, `ollama v0.40.1`, `vllm v0.32` (prefixes of the
real tags) all bind, exit 0 — a row may name a pin that does not exist while citing the real tag's digest.

**DEFECT-4 — value is a substring.** V4: value `600 s` binds against `int32_t timeout_read        = 3600;`
("600" inside "3600"); `99`/`9931` and `5`/`512` likewise. The row states 600 s where the line says 3600.
B2's wording is literally honest; the claim's summary "the value occurs in the literal" is not token-wise.

**DEFECT-5 — B7 is a substring, and its docstring overstates it.** V5: name ``max`` binds against
`int models_max = 4;`. B7 claims to test "the row names the parameter, flag or constant the line sets" but
tests only "a backticked token of length>=3 occurs in the literal". `COM_DBG`, `Apache-2.0`, `progress`,
`start`, `end`, `https`, `raw`, `github` all pass and none is a parameter.

**DEFECT-6 — SOURCES.md is not comment/fence-aware, and first-wins shadows the visible row.** V9: an
HTML-commented `| S593 | … common/common.cpp | …` above the real row shadows it, and a SKILL row citing
S593 binds against **common.cpp line 1930** (a loop header) while every reader of rendered SOURCES.md sees
S593 = common.h. V10 is the same with a fenced row. Silent identity change; the K2 reviewer read of the
rendered file cannot catch it.

**DEFECT-7 — section boundary is column-0 only.** V8: ` ## Appendix` (1 space; 1–3 spaces still render as
an `<h2>`) does not end the section, so appendix rows are harvested (`rows=10`). V13: a fence opened before
the heading hides it (`rows=0`, exit 1 — safe, but a silently empty population with no diagnostic). V14 (a
`## Next` heading inside a fence) is renderer-correct; recorded, not claimed.

**DEFECT-8 — a malformed row poisons the (S,line) pair.** V6: a literal containing a raw `|` gives
`cells=9`, but `(cells[4], cells[5])` is registered *before* grading, so the next well-formed row with the
same pair is reported `duplicate` and never bound (`rows=2 bound=0 unbound=1 duplicates=1`) — a false red.
A pipe-spanning literal itself does not bind (safe).

**DEFECT-9 — not reproducible offline; `fetch_failures` is per row.** 14 rows over 3 URLs, one
`curl -sfL` attempt each, 60 s, no retry, no pinned bytes. Network down → `unbound=14 fetch_failures=14`,
exit 1, indistinguishable from rows not binding, with no `could-not-evaluate` (contrast exit 2 for a bad
`--rev`). V11: three rows on one dead URL give `fetch_failures=3`.

**DEFECT-10 — the line anchor degenerates on CR-only bodies.** `split("\n")` yields one line, so
`1 <= n <= 1` and *any* line-1 row binds if its literal occurs anywhere (`lineendings.out`: LF bound,
CRLF bound, CR-only line 634 `literal-not-at-line`, CR-only line 1 bound). Unreachable from these
upstreams (LF); CRLF is benign for single-line literals.

**NOTE-1** — accepted URL shapes (V3): jsDelivr CDN mirror, `…#L632`, `?cachebust=1`, `?raw=1`, and a
source cell with two URLs (real-first and mirror-first). All bind; the only rejected shape was a blockquoted
source row (`> | S9108 | …`, `source-absent`). No host/path/query validation beyond substring, and
`curl -sfL` follows redirects, so the fetched bytes need not come from the named host.

**NOTE-2** — `controls/c2-forgeries.out` is not byte-reproducible: four `rev=` values are fixture commit
hashes that depend on commit time. Every verdict and count reproduces.

**NOTE-3** — V6's pipe case, the blockquoted SOURCES row and V13 all fail closed; no row bound whose literal
was absent from the stated line.

**BLOCKER: none.** The forgeries defeat the instrument, not the artifact: `AUDIT rows=14 non_exact=0` shows
every landed row is exact under whole-token checks, cites a single-occurrence S row, and no `<details>`,
indented heading, CR-only file or shadowed source is present at M2. The receipt `rows=14 bound=14 … exit 0`
is true, and C2's known-limit paragraph is honest about the K2 reviewer read — but it discloses only
prose/decision semantics, not the mechanical escapes (pin/value/name substrings, `engines` word counting,
SOURCES shadowing).

## Smallest safe correction (next round; this freeze forbids changing these bytes)

(1) B4 pin = whole URL path segment, engine name taken from the S row not the SKILL cell; (2) B2 value =
whole numeric token (neighbours non-digit/non-dot); (3) B7 = whole identifier; (4) `sources()` through the
same comment/fence stripper, fail loudly on a repeated `S###` instead of `setdefault`; (5) register the
`(S,line)` pair only after B1; (6) `engines` counted from S rows; (7) `fetch_failures` per URL plus a
distinct exit for "no network"; (8) section boundary accepts 0–3 leading spaces. Record the escape list in
the round-91 lesson so the C2 known limit is stated as measured.

## Deliverables

`.ufo/waves/round-91/w1a2/out/CR02ThresholdCounter/`: `c2-forge-cr02.py` (14 variants),
`c2-forge-cr02.out`, `audit-landed-rows.py`, `lineendings.out`, `rerun-c2-forgeries.out`, `c2-at-M2.out`,
`c2-offline.out`, `counter-hash.out`, `load.txt`.

VERDICT: holds — predicate reproduced at M2 (14/14, exit 0, counter bytes = F); nine forgery classes bind
and five escape the disclosed K2 limit, but none is realized in the landed 14 rows.
