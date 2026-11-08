# SB01LessonDraft — candidate `corpus/lessons/round-94.md` rows (round-94 w1)

Seat `SB01LessonDraft` (leaf, calibration axis). Draft only; nothing in this file is committed.
Every claim below was checked by running the frozen counters at the named revision, or by
reading the pinned archive bytes.

Revisions used (full hashes):
- base `e6f1dccecbad6dea44a129dabc928822c458e824`
- freeze `285f17832d0e26364366bbf19888d68f1838249b`
- C1 measured `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`
- C2+C3 measured `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623`
- lane tip at read time `11d2770b5e61e997245dce74eadeff8b3ce9ea1f`

Pinned archive: `https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177`
sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` (re-fetched, digest equal).

---

## Part A — candidate `## Gate` admit/reject entries for S604–S615

**Basis for the decisions.** The frozen C2 counter
(`tools/round94-setter-sweep.py`, bytes identical at `6aa5fa6b` and at the tip — `git diff
--stat 6aa5fa6b 11d2770b -- tools/round94-setter-sweep.py` empty) re-run against M2
reproduces the committed receipt `.ufo/waves/round-94/measured/c2.out` **byte for byte**
(`diff` empty), exit 0, last line
`SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True`
and `SETTER_DIGEST f50a52f4…ea13`.

Every one of the 12 new S-rows was re-verified against the archive bytes **and** against the
raw URL (`https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`): for all 12 the
raw-URL sha256 equals the archive-member sha256 equals the digest recorded in
`corpus/SOURCES.md` at M2. All 12 quotes are ≤ 25 words. Two of the twelve carry a wrong
line number (S604, and — see the note — the S607 anchor is fine but its row text is a
different line); details below.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S604 `common/preset.cpp` @ b12177 | **admit** (A, code, mined) — **quote line is wrong, see DEFECT-1** | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/preset.cpp` — 2026-11-07, sha256 `793ad2c7f4589376cceab11a3172e2b5f80adf645182a71b5a2398aa377cbb25` | `opt.handler_string(params, val);` — **line 151**, inside `apply_to_params` (def. line 142) | Grounds the config.ini/`--models-preset` mechanism rows P44 (`preset.cpp:142`), P45 (`preset.cpp:285`), P46 (`preset.h:47`), P47 (`preset.h:70`). The committed SOURCES row and the committed lesson both say "line 150"; line 150 is `if (opt.handler_string) {` and the quoted statement is line 151. |
| S605 `common/common.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/common/common.cpp` — 2026-11-07, sha256 `1b41b3613a10d579e2808bf5e1a73531980ca836d0f4d23dba22d7130d78985e` | `config_directory = common_get_env("XDG_CONFIG_HOME");` (line 1009) | Grounds the user config.ini path (`fs_get_config_directory`, line 1001). Verified exact. |
| S606 `tools/cli/cli-server.h` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/cli/cli-server.h` — 2026-11-07, sha256 `d463b06b589e9967b25c746f9f751ab484efe37f696a3032d3f5b0f89f4e205d` | `port = common_http_get_free_port();` (line 35) | Grounds the llama-cli embedded-server entry point (`cli_server::start`, lines 34–50). Verified exact. |
| S607 `tools/server/server-common.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/server/server-common.cpp` — 2026-11-07, sha256 `b686729ed7d098e2f0c3da1ba28325d0e6d30721dab09f71cb9b53f342710ddb` | `return std::getenv(SERVER_ENV_ROUTER_PORT) != nullptr;` (line 2236, in `server_role::is_managed_by_router`, lines 2235–2237) | Grounds router-child detection. Verified exact. |
| S608 `tools/server/server-common.h` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/server/server-common.h` — 2026-11-07, sha256 `335a09e65306cb14d18760b2be6710d586b08a23316c79d7ebfab3148e82ba1b` | `#define SERVER_ENV_ROUTER_PORT "LLAMA_SERVER_ROUTER_PORT"` (line 765; the archive line continues `// its presence makes the process a child`) | The env var name that marks a router child. Verified exact. |
| S609 `tools/server/server-models-sched.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/server/server-models-sched.cpp` — 2026-11-07, sha256 `b786ea0917ec1d9578c273b6f3930cf9ba90865be7878c18d6337d2f1cfdd54a` | `child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT) + "=" + std::to_string(models.base_params.port));` (line 423) | The measure child also gets the router-port env. Verified exact. **Note the flip:** round 93's Gate *rejected* this same line as a listen-port setter; round 94 admits it only as the child-env export, which is what the line says — the flip condition it named ("a later pin reads `SERVER_ENV_ROUTER_PORT` as the child's listen port") has **not** occurred and is not claimed. |
| S610 `common/arg.h` @ b12177 | **admit** (A, code, mined) | `…/b12177/common/arg.h` — 2026-11-07, sha256 `42f21df75ada0e5bba795a40edc02724f0e0be03db288b64eed6057c1dfa261b` | `return strcmp(args[0], other.args[0]) < 0;` (line 95, in `common_arg::operator<`, lines 91–96) | Preset argv ordering decides which setter is parsed last. Verified exact. |
| S611 `common/preset.h` @ b12177 | **admit** (A, code, mined) | `…/b12177/common/preset.h` — 2026-11-07, sha256 `ec0f5014821f2894f39cef96503cf36b84baf73742aa425f419eb2a5bd0e32f3` | `common_presets load_from_ini(const std::filesystem::path & path, common_preset & global) const;` (line 70; the declaration at line 47 is `apply_to_params`) | Declarations of the preset apply/load mechanism. Verified exact. |
| S612 `tools/cli/cli-context.h` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/cli/cli-context.h` — 2026-11-07, sha256 `e1ae9fc601d08e968b3bb03ee6ac0a2bfa252b6e8c1f591656337a5ed0dc8c04` | `#include "cli-server.h"` (line 6) | cli-context pulls in the embedded-server helper. Verified exact. |
| S613 `tools/imatrix/imatrix.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/imatrix/imatrix.cpp` — 2026-11-07, sha256 `a1be01b2f39ac2a9879afc895c05e1b72356e39f19496d99dca093bcf104b8ab` | `params.n_parallel = n_seq;` (line 1869) | imatrix's own slot count, not llama-server's. Verified exact. |
| S614 `tools/perplexity/perplexity.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/perplexity/perplexity.cpp` — 2026-11-07, sha256 `42a39345830f9d0745e6e6da2bb35cc021210d5fd39f2224f6914327fc0088c0` | `params.n_parallel = std::max(4, params.n_parallel);` (line 2009; line 2012 is the else-branch `std::max(1, params.n_batch / n_ctx)`) | perplexity clamps n_parallel; a different tool. Verified exact. |
| S615 `tools/rpc/rpc-server.cpp` @ b12177 | **admit** (A, code, mined) | `…/b12177/tools/rpc/rpc-server.cpp` — 2026-11-07, sha256 `0bef22416395b1abe4e84046e7a1ffc0a89ab6bf04d3e6bf468f87a82f453ba0` | `int                      port        = 50052;` (line 80) | rpc-server's own port default and argv parser (lines 132, 136). Verified exact. |
| S593, S596–S603 @ b12177 | **re-opened**, admitted for the P-rows that cite them | the rows' URLs — 2026-11-07, digests equal the archive members | `params.port = 8011;` (S596 line 4613) | Every P-row's text cell is the archive line byte for byte (`measured/c2.out` B2). I re-verified all 9 re-opened digests against the archive: `common.h` `c3010a3c…`, `arg.cpp` `c69c0e07…`, `server.cpp` `d4d343db…`, `server-http.cpp` `aad15b75…`, `server-models.cpp` `cab14969…`, `http.h` `949e44f9…`, `server-connect.cpp` `2a505b29…`, `server-http.h` `29c53f7f…`, `server-models.h` `304c0136…` — all equal to the archive members and to the SOURCES digests. All 9 re-opened quotes were re-read at their stated lines: S593 634, S596 1373, S597 127, S598 96, S599 1218, S600 324, S601 208, S602 92, S603 80 — **all exact**. |
| The codeload archive itself as a SOURCES row | **reject** (input, not a teaching source) | `https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177` — 2026-11-07, sha256 `f50a52f4…ea13` | n/a (binary archive) | The archive is the counter's pinned population input (`TARBALL_SHA256` in `tools/round94-setter-sweep.py`); what kama learns is cited per file through the raw rows above. Flip: GitHub stops serving per-file raw URLs for the tag. |

`status`/`recheck`/`used-by` changes on existing rows: none (the `corpus/SOURCES.md` diff
base→M2 is 12 insertions, 0 deletions — `git diff e6f1dcce 6aa5fa6b -- corpus/SOURCES.md |
grep -c '^-[^-]'` → `0`). S604–S615 are new rows (`mined`, recheck `on-release`, used-by
`SKILL.md`). Census before→after: **343 → 355 rows** (both counts re-derived by
`git show <rev>:corpus/SOURCES.md | grep -cE '^ \| S[0-9]{3,} '`); the round's census command
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama` exits **0** (re-run this session; output `kama ok
…/corpus/SOURCES.md`; the W04/W01 warnings it prints are the pre-existing duplicates and
S481, none on S604–S615).

**Recommended correction to the committed lesson's S604 row** (one cell):

> `opened2026-11-07: "opt.handler_string(params, val);" (line 151, inside apply_to_params)`

---

## Part B — candidate `## Mistakes` rows

Format per the round-93 house style: class · evidence pointer · captured-by · fix · how the
fix is shown able to fail.

**M1 — a counter drafted from scratch instead of extending the proven one.** Class: reinventing
a frozen counter. Evidence: the first `tools/round94-setter-sweep.py` draft carried B4/B5
derived checks (value-cell and arg-block env/example rules) that contradicted the round-93
counter's actual semantics; it reported 155 mismatches on a correct section
(`/fast/scratch/hyaku/kama-r94/l1-controls/` early run, `SETTER_SWEEP … 155`). Captured-by: the
pre-freeze control run against the just-authored section, before commit. Fix: discarded the
draft and re-based the counter on `tools/round93-setter-rows.py`'s `grade_p`/`arg_block`/
`split_cells`, extending only the population patterns, the entry cell, and the R18/R19 decision
model; the re-based counter then bound 92/92 with `derived_disagree=0`. Shown able to fail:
mutant line-edit (35→36) → `SETTER_ROW P50 unbound fabricated`, `met=False`; base rev (no
section) → `met=False`.

*Seat verification (this session, both arms re-run at M2 with the committed counter):*
- mutant arm — editing P50's line cell 35→36 in a copy of `SKILL.md` gives
  `SETTER_ROW P50 unbound fabricated` and
  `SETTER_SWEEP 92 92 2 91 1 1 0 1 derived_checked=47 derived_disagree=0 decisions=1/2 pop=92
  met=False`, exit 1. **Reproduces the committed text exactly.**
- base-rev arm — running the counter at `e6f1dcce` (no round-94 section) prints 92 ×
  `SETTER_MISSING` and `SETTER_SWEEP 92 0 0 0 0 92 0 0 … met=False`, exit 1. **Reproduces.**
- **Caveat on the evidence pointer:** the "155 mismatches" receipt is *not* in the lane — the
  only committed artifacts under `.ufo/waves/round-94/` are `controls/c2-build-candidate.py`,
  `measured/c1.out`, `measured/c2.out`. The 155 figure appears nowhere in the lane or in the
  L1 scratch (`grep -rl '155'` over `/fast/scratch/hyaku/kama-r94/l1-controls/` finds only
  upstream llama.cpp files). The *claim* is plausible and the fix is verified, but the receipt
  is uncommitted and unreplayable — the same defect class as round-93's M1 correction
  ("the v0 counter bytes are not committed … v0 is not presented as replayable").

**M2 — the population pattern silently omitted the router-port env route.** Class: pattern list
treated as complete. Evidence: the first population computation (POP_RE + config-route +
entry-anchors, without `SERVER_ENV_ROUTER_PORT`/`LLAMA_SERVER_ROUTER_PORT`) yielded 88 lines
and missed `server-models.cpp:1235`, `server-common.cpp:2236`, `server-common.h:765`,
`server-models-sched.cpp:423` — the very child-detection rows the round-93 verifier routed here
(R6/SC02). Captured-by: re-deriving the population with the env names added before freeze, not
by a seat. Fix: added both env tokens to the config-route pattern; population 88 → 92, and the
four rows are now P-rows with SOURCES S607–S609. Shown able to fail: the base-rev run lists all
92 as `SETTER_MISSING`.

*Seat verification:* I re-derived the population from the frozen counter's own `population()`
with the two env tokens removed from `CFG_SUBSTR`: **88**, and the four lines it then adds are
**exactly** `tools/server/server-common.cpp:2236`, `tools/server/server-common.h:765`,
`tools/server/server-models-sched.cpp:423`, `tools/server/server-models.cpp:1235` — the same
four the row names, and `pop88.txt` in the L1 scratch has 88 lines and contains none of them.
**Arithmetic reproduces.** The base-rev "92 × `SETTER_MISSING`" arm reproduces (above).
*Correction to the row:* "the very child-detection rows the round-93 verifier routed here
(R6/SC02)" — the r93 closure's **R6** is *"read SC02ProbeVerdictSweep's output … and grade it
against C1 next round"*, and SC02 was the **probe-verdict** seat, not the setter sweep. The
setter-sweep routing was **R2** (with the M6/M8 findings behind it) and the config.ini gap
was **SC01**. The four lines are the router-port env rows; R2 is the defect they answer.

**M3 — scope cells authored as prose, not the block's `set_examples`.** Class: derived cell
filled by intent rather than by the archive. Evidence: 18 rows went `unbound derived` because
the scope cell read `llama-server`/`llama-server, llama-cli` while `arg_block` extracts the
literal `set_examples` names (`LLAMA_EXAMPLE_SERVER`, `LLAMA_EXAMPLE_CLI, LLAMA_EXAMPLE_SERVER`,
…); `derived_checked=47 derived_disagree=18`. Captured-by: the pre-freeze control run. Fix:
scope cells set to the exact comma-separated `set_examples` names per block (builder constants
`SV`/`CS`/`EG`); `derived_disagree=0`. Shown able to fail: reverting one scope cell re-opens a
`derived` disagreement.

*Seat verification:* the single-cell arm reproduces exactly — setting P12's scope cell to
`llama-server` gives `SETTER_ROW P12 unbound derived` and
`SETTER_SWEEP … derived_checked=47 derived_disagree=1 … met=False`, exit 1. The builder
constants `SV`/`CS`/`EG` are present in the committed
`.ufo/waves/round-94/controls/c2-build-candidate.py` (lines 20–22). **The bulk arm reproduces in
kind but not in number:** rescoping *all* 34 `common/arg.cpp` rows to `llama-server` /
`llama-server, llama-cli` gives `derived_disagree=23` and 23 `unbound derived` rows, not 18 —
so the "18 rows / `derived_disagree=18`" figure belongs to a partial draft that no committed
artifact records. The **claim's substance** — that prose scope cells disagree with
`arg_block` and that the fix is scope=`set_examples` — is confirmed by the committed section
(currently 0 disagreements across 47 derived checks).

---

## Part C — audit of the committed `## Mistakes` rows

The task asks specifically: *flag any committed Mistake row whose "shown able to fail" evidence
is missing or wrong.*

| committed row | shown-ability arm as written | seat re-run | verdict |
|---|---|---|---|
| M1 | mutant line-edit (35→36) → `SETTER_ROW P50 unbound fabricated`, `met=False`; base rev (no section) → `met=False` | both reproduce exactly (exit 1 each) | **evidence present and correct**; only the *155-mismatches* evidence pointer is uncommitted |
| M2 | the base-rev run lists all 92 as `SETTER_MISSING` | 92 × `SETTER_MISSING`, exit 1 — reproduces | **evidence present and correct**; the *attribution* "R6/SC02" is wrong (should be R2/SC01) |
| M3 | reverting one scope cell re-opens a `derived` disagreement | `derived_disagree=1`, `met=False`, exit 1 — reproduces | **evidence present and correct**; the "18 rows / `derived_disagree=18`" figure is unreplayable |

**No committed Mistake row has a missing or wrong "shown able to fail" arm.** All three arms
re-run and reproduce. The defects I did find are in the *evidence pointers* (M1's 155 receipt,
M3's 18-row figure) and in *attribution* (M2's R6/SC02) — not in the failure demonstrations
themselves.

---

## Part D — defects found in the committed round-94 artifacts

**DEFECT-1 — the S604 quote's line number is wrong in two committed files.** `corpus/SOURCES.md`
at M2 (row S604) and `corpus/lessons/round-94.md` (Gate table, S604 row) both say the quote
`opt.handler_string(params, val);` is at **line 150** of `common/preset.cpp` @ b12177. Line 150
is `if (opt.handler_string) {`; the quoted statement is at **line 151**. Verified by
`sed -n '150p'` (gives `if (opt.handler_string) {`) and `grep -n 'handler_string(params, val)'`
(gives `151`). All **eleven other** new quotes are at their stated lines exactly, so this is an
isolated off-by-one, not a systematic offset. The S604 anchor cell
(`apply_to_params` lines 142–160, `load_from_ini` line 285) is otherwise correct —
`apply_to_params` is defined at 142 and `load_from_ini` at 285.
*Why it matters:* the census validates row shape, not quote line numbers, so
`sources-census.sh validate` still exits 0 with the wrong line in place — the error is invisible
to the round's own check. The lesson's Gate column also says the quote is "line 150, inside
`apply_to_params`", which is the same wrong pointer.

**DEFECT-2 — the C2 predicate's printed fields do not match what the counter prints.** The
frozen predicate (`plans/round-94-claims.md:58-60`) says the counter prints
`SETTER_SWEEP population=<n> rows=<n> bound=<n> unbound=0 missing=0 duplicates=0 fabricated=0
derived_disagree=0 entry_points=<e> decisions=<d> decisions_bound=<d> …`. The counter prints
**positional** numbers instead:
`SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92
met=True` (`tools/round94-setter-sweep.py:354`). Consequences:
- no `population=`/`rows=`/`bound=`/`unbound=`/`missing=`/`duplicates=`/`fabricated=` keys are
  printed at all — a reader (or a script) matching the frozen predicate string against the
  receipt sees none of them;
- **`entry_points=<e>` is never printed by anything** — `grep -rn entry_points` over the repo
  finds it only in `plans/round-94-claims.md`, never in the counter, the receipt, or any other
  file. The claim's headline new dimension (the per-entry-point `entry` cell) has **no counter
  metric**, so "the counter grades the entry-point dimension" is true only of the per-row
  `entry-enum` check, not of any aggregate;
- `decisions=2/2` is a single token, not `decisions=<d> decisions_bound=<d>`.
The round-93 counter had the same class of drift in the other direction (`SETTER_ROWS
population=48 rows=48 … decisions=2 decisions_bound=2`, matching its plan), so round 94 is a
regression against the previous round's receipt convention.

**DEFECT-3 — six committed P-rows violate the counter's own documented B4 pairing.** The
counter's docstring (`tools/round94-setter-sweep.py:13-16`) states: "parameter `-` <=> effect in
{copies, declares, unrelated}; parameter port/n_parallel <=> effect in {default, overrides,
copies, unrelated}". Under that pairing, `port`/`n_parallel` with effect `declares` is
**excluded**. Six committed rows use it: P12, P14, P15, P17 (`n_parallel`/`declares`) and P18,
P20 (`port`/`declares`). The counter's *code* does not enforce the documented pairing — it only
rejects `param == "-"` with effect default/overrides and `param != "-"` with effect `unrelated`
(`tools/round94-setter-sweep.py:241-246`) — so these six bind silently. Round 93's counter
enforced the strict iff (`if (param == "-") != (effect == "unrelated")`,
`tools/round93-setter-rows.py:250`), so this is a **loosening of the frozen rule between
rounds**, and the rows that now rely on it are exactly the r93 **KQ151 twins** (P12/P15 pair on
`arg.cpp:2515`/`2526`, P14/P17 on `2523`/`2531`, P18/P20 on `3318`/`3323`) — the rows the round
was supposed to relabel. The twins are now *consistent with each other* (both `declares`), so
the r93 M4 defect is genuinely fixed; but they are fixed by **not** using the label the section
defines for "a setter the pinned program never registers", and the plan's own text ("P05–P07
relabelled under a `declares-unregistered`-class label **the section defines**") is not
satisfied — the round-94 section defines no `declares-unregistered` class, and its effect
vocabulary is never given a glossary at all (round 93's section had one at `SKILL.md:1978`).

**NOTE-1 — the r93 lesson's M4 defect is closed for the twins but the section has no glossary.**
The round-94 section defines the **Entry** vocabulary inline (`SKILL.md:2085-2087`) but never
defines the **Effect** vocabulary it uses in the same table. Round 93's section defined both
(`SKILL.md:1978`). With no glossary, "does this row's label agree with the section's own
vocabulary" is unanswerable for effect — the exact question KQ151 asked.

**NOTE-2 — the committed `## Gate` table's URL column says "raw URL", not the URL.** All twelve
new rows carry the literal text `raw URL — 2026-11-07, sha256 …` in the URL/access-date column
(`corpus/lessons/round-94.md:20-31`). The round-93 Gate table spelled the URLs out
(`https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`, 4 occurrences in
`corpus/lessons/round-93.md`). The C3 claim requires the Gate block to record "URL, access date
and ≤25-word located quote per row"; as committed it records a *pointer* to a URL, not the URL.
The URLs are recoverable from `corpus/SOURCES.md`, so nothing is lost, but the claim's own
wording is not met by the artifact.

**NOTE-3 — the committed lesson has no `## Dispositions` section for the r93 closure's R1–R7.**
Round 93's lesson ended with "## Dispositions of the round-92 closure (R1–R6)". Round 94's
lesson (`corpus/lessons/round-94.md`) has only `## Gate` and `## Mistakes`; the r93 closure's
seven routed defects (R1 append-debt, R2 superseding rows, R3 stale SCORECARD rows, R4 counter
gaps, R5 report author date, R6 SC02 output, R7 terminal gate receipt) are addressed only in
`plans/round-94-claims.md`, not in the lesson. R3 in particular is **not** addressed anywhere:
`SCORECARD.md` is unchanged base→M2 (`git diff --stat e6f1dcce 6aa5fa6b -- SCORECARD.md`
empty) and both capability rows (lines 296 and 6163) still name the four-field key
`(device, inode, size, mtime)` and the falsified revision `fe5f031c`, and line 297/6164 still
cites the C2 decision rows without recording that C2 was not verified. `grep -c 'round-94'`
on `SCORECARD.md` → `0`.

**NOTE-4 — the frozen claim's "counters' bytes identical to this freeze commit" is not
checkable as written.** The freeze commit `285f1783` contains **only** `plans/round-94-claims.md`
(`git show --stat` → 1 file) — neither counter existed at the freeze. Round 93 committed its
counters *with* the freeze (`0f272a37` added the counters and 16 control files in the same
commit), so round 94's freeze is structurally weaker than round 93's, and the C2 kill rule "K1
the counter changes after this commit" has no counter-at-freeze to compare against. What
*can* be checked holds: `tools/round94-setter-sweep.py` and `tools/round94-router-budget.py` are
byte-identical at their landing commits and at the tip (`git diff --stat` empty in both cases).

**NOTE-5 — the C1 counter's `BASE` is round 93's base, not round 94's.** `tools/round94-router-budget.py:105`
sets `BASE = "5af794958b0fc08f574aa2e67650282269549b02"` (round 93's base). `measured/c1.out`'s
`base_sha256=36631d49…` is the probe at that rev (verified), while round 94's own base
`e6f1dcce` has probe sha256 `1e21c1fb…`. The counter's do-nothing comparison therefore runs
against a probe two revisions older than the round's stated base. This is defensible — it is the
last revision before the per-file deadline — but it is undocumented in the counter and is not
the revision the claim's base names.

**NOTE-6 — C1's receipt does not record the exit code.** `measured/c1.out` ends with the
`ROUTER_BUDGET … rev=a27656a4… load1_nat=232.08 burners=96` line; there is no `exit=` line
(contrast round 93's `measured/c2.out`, which ends `exit=0`). `measured/c2.out` likewise has no
`exit=` and no `rev=` — its `rev` is only inferable from the caller. Round 93's c2 receipt had
both (`rev=ee19acbd… skill=rev`, `exit=0`).

**NOTE-7 — load was high during the C1 measurement and the receipt records it.** `c1.out` says
`load1_nat=232.08 burners=96`, and the per-cell runtimes show the load effect plainly
(`R08-distinct-slow-k4`: 8.59 s/9.13 s natural vs 13.93 s/15.01 s under load — a 1.6× ratio
for the same cell). This is the behaviour C1 is about, measured honestly. Host load during my
own re-runs was 129–200 (`uptime`), so my C2 re-run's 6.4 s wall time is not a timing claim.
