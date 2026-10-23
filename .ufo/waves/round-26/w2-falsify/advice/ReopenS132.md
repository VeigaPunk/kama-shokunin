# ReopenS132 — attack on SOURCES row S132 (KQ31 supersession of S107)

ATTACK S132 (KQ31 supersession of S107): partial — the row's substance holds (URL, commit,
release label, every anchor line range, sha256, the `supersedes S107 —` prefix, the correction's
content and its fit chain); two minor Gate-text defects and one residual entry-citation drift.

Scope of this seat: `corpus/SOURCES.md:144` (row S132), the Gate prose and quote at
`corpus/lessons/round-26.md:19-23,45`, and the routing text at
`corpus/lessons/round-25-verifier-spotcheck.md:213-217`. Read-only; no lane production file was
edited. No llama-server was started (this item names no port block). No tools installed.

## 1. Fresh fetch, snapshot identity, release label

```
$ curl -sS -w '\nHTTP %{http_code}\n' -o llama-context.704366d.fresh.cpp \
    https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp
HTTP 200   (curl_exit=0)
$ sha256sum llama-context.704366d.fresh.cpp
2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5
$ wc -l llama-context.704366d.fresh.cpp
4719
$ sha256sum .../.ufo/waves/round-26/sources/llama.cpp-704366d/llama-context.cpp
2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5
$ cmp -s llama-context.704366d.fresh.cpp .../sources/llama.cpp-704366d/llama-context.cpp ; echo $?
0        # snapshot_equals_fresh=yes
$ curl -sS -o /dev/null -w '%{http_code}\n' -L '<row URL with #L219>'
200
$ git ls-remote https://github.com/ggml-org/llama.cpp refs/tags/b11755 'refs/tags/b11755^{}'
704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755        (exit 0)
```

The anchor's sha256 `2a25e556…b94aa5` equals the fresh bytes and the lane snapshot bytes; the
snapshot is byte-identical to the fresh fetch (so the Gate's "fetched bytes equal the lane
snapshot" claim at `round-26.md:14-16` holds for this row); `b11755` is that commit, so the row
title's "(release b11755)" holds.

## 2. Per-cell verdicts on `corpus/SOURCES.md:144`

Proof lines are from the fresh fetch (identical to the snapshot), printed with
`nl -ba llama-context.704366d.fresh.cpp | sed -n '…'`.

| Cell | Claim | Verdict | Proof |
|---|---|---|---|
| URL | commit 704366d76, path src/llama-context.cpp | holds | blob URL HTTP 200; raw fetch HTTP 200, 4719 lines, sha256 = anchor |
| title | "@ 704366d76 (release b11755)" | holds | `git ls-remote … refs/tags/b11755` → 704366d76 (exit 0) |
| anchor | "line 219" | holds | `:219 cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;` |
| anchor | "constructor lines 377-393" | holds | ctor starts `:168 llama_context::llama_context(`; `:377` GGML_PAD(n_ctx,256); `:380` unified assign; `:382` `n_ctx / n_seq_max`; `:383` pad; `:389-392` non-divisible reassign + `LLAMA_LOG_WARN … rounding down`; `:393` closes the else |
| anchor | "409-417" | holds | `:409-412` INFO block `n_ctx_seq < n_ctx_train`; `:414-417` WARN block `n_ctx_seq > n_ctx_train` |
| anchor | "llama_init_from_model lines 4114-4118" | holds | function starts `:4021`; `:4114` YaRN `if`; `:4116` `model->hparams.n_ctx_train = cparams.n_ctx_orig_yarn / cparams.rope_freq_scale;`; `:4118` closes |
| anchor | "raw sha256 2a25e556…b94aa5" | holds | section 1 |
| scope | "constructor's zero-value fallback, padded/split context, comparison logs and YaRN adjustment; not default launch policy, server-level per-slot ceiling, HTTP surfaces or other builds" | holds | the four included items are exactly the four ranges above; the exclusion "not default launch policy" is the corrected boundary (section 4). Full-tree check: `grep -rn "n_ctx *== *0" <tar.gz of 704366d>` returns only `src/llama-context.cpp:219` as a zero→`n_ctx_train` selection (`common/fit.cpp:198,270` is a fit-side guard, `tools/server/server.cpp:180` gates `--kv-unified-per-slot`, `src/llama-context.cpp:4034` is an error check) — so "in this constructor only" is true repo-wide at this commit |
| teaches prefix | starts `supersedes S107 —` | holds | codepoints of the cell: `… 's','u','p','e','r','s','e','d','e','s',' ','S','1','0','7',' ',0x2014,' ','i','n'`; `startswith('supersedes S107 — ')=True`. KQ31 (`corpus/QUALITY.md:164`) satisfied; `git cat-file blob 1560e4d8…:corpus/SOURCES.md` → `grep -c '| S132 |'` = 0 (newly opened), and the S107 row is byte-identical at base and tip (`diff <(grep '| S107 |' base) <(grep '| S107 |' tip)` empty → "S107_row_unchanged=yes"), so "the old row stays intact" holds |
| teaches | "in this constructor only, params.n_ctx == 0 selects hparams.n_ctx_train (219)" | holds | `:219`; section 4 |
| teaches | "context is padded and, for a non-unified cache, n_ctx_seq is divided and padded and n_ctx may be reset to its product with n_seq_max (377-393)" | holds | `:377`, `:382`, `:383`, `:389-390` |
| teaches | "logs n_ctx_seq below or above n_ctx_train without clamping it (409-417)" | holds | `:409-417` only log; assignments to `cparams.n_ctx` are at {219, 377, 390} and to `cparams.n_ctx_seq` at {380, 382, 383} in the whole constructor (regex scan of the fresh file) — no clamp |
| teaches | "custom YaRN scaling adjusts n_ctx_train at 4114-4118" | holds | `:4114-4118` |
| used-by | `corpus/knowledge/context-capacity.md, corpus/lessons/round-26.md` | holds | `grep -rn S132` over SKILL.md, corpus/, registry/ returns only `context-capacity.md:258` and `round-26.md:45`; `registry/error-signatures-r26.json` has 0 matches for S132 (correct: only S114-S130 are counted rows) |

## 3. Gate quote at `corpus/lessons/round-26.md:45` — DEFECT (minor)

```
$ nl -ba corpus/lessons/round-26.md | sed -n '45p'
45  | S132 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L219 | 2026-10-23 | line 219: `params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx;` |
$ grep -cF 'params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx;' llama-context.704366d.fresh.cpp
0        (grep_exit=1)
```

- Word count: 7 words inside the backticks (9 with the `line 219:` prefix) — the "at most 25
  words" rule at `round-26.md:22-23` holds.
- Located: `:219` does contain the ternary — the pointer holds.
- Verbatim: FAILS. The source line is column-aligned:
  `cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`
  The Gate quote is the whitespace-collapsed rendering, so it is not a source line, contrary to
  the table's own rule at `round-26.md:22-23` ("Quotes are the source line, cut to at most 25
  words"). Measured across the whole table against fresh fetches of all seven cited files at
  704366d (each row's quote extracted from its code span and tested on its cited line): 21 of the
  22 rows quote a literal substring; S132 is the only non-literal one. Max quote length is 25
  words (S127), so S132's 7 words satisfy the size rule and fail only on verbatim fidelity.
- Smallest correction (line 45, replace the backticked text with a literal substring, 7 words):

  `params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`

  (verified literal: `'params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;' in src` → True),
  or quote the whole line `cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`
  (also verified literal). This matters only as fidelity to the Gate rule: S132 is not a counted
  row, so no counter clause reads this quote.

## 4. Correction content and its match to the routing — holds (with one Gate-prose overstatement)

Defect 3 (`round-25-verifier-spotcheck.md:213-217`) routes supersession rows for S106, S109 and
S113, and records: "The lane also reports S107 and S112 corrections; I did not verify those."
It gives no S107 correction text, so the correction can only be checked against the lane's filed
S107 defect. That defect is `.ufo/waves/round-25/a2-falsify/advice/ReopenS107.md` F1 (lines 48-79):

> F1 (medium): the teaches cell states line 219 as a server rule, and fit overrides it on default
> launches … Smallest correction: replace "An unset n_ctx resolves to n_ctx_train (line 219)," with
> "An n_ctx of 0 in llama_context_params resolves to n_ctx_train (line 219); common fit, outside
> this row, sets n_ctx before this line on a default launch (S106 fit.cpp 267-272),".

S132's teaches reproduces exactly that correction — constructor-only scope, "does not establish
default-launch behavior", fit assigning beforehand, cited to S106. The chain is verified at the
landed tip:

```
common/common.h:483                bool fit_params = true;   # fetched at 704366d
tools/server/server-context.cpp:1217   llama_init = common_init_from_params(params_base);
common/common.cpp:1245             if (params.fit_params) {
common/common.cpp:1270                 common_fit_params(params.model.path.c_str(), &mparams, &cparams, …
common/common.cpp:1714             cparams.n_ctx             = params.n_ctx;
common/fit.cpp:198                 const bool     n_ctx_auto = cparams->n_ctx == 0;
common/fit.cpp:267                 const uint32_t n_ctx_max       = min<uint64_t>(hp_nct * n_streams, UINT32_MAX);
common/fit.cpp:271-272             if (n_ctx_auto) { cparams->n_ctx = n_ctx_max;
```

so on a default launch the constructor at `llama-context.cpp:219` sees a nonzero `n_ctx`, and
"common fit may assign n_ctx beforehand (S106)" is correct and correctly hedged (`--fit off`
leaves 0 and the fallback fires). Note (not a defect): S132 cites S106, which S131 now
supersedes; S106's own anchor still names the line 270 comment and the 272 assignment, so the
pointer remains valid, and the round-25 report proposed the same S106 cite.

**DEFECT (minor, Gate prose only), `round-26.md:19-21`:** "S131-S135 are KQ31 supersession rows …
for S106, S107, S109, S112 and S113, routed by `round-25-verifier-spotcheck.md` defect 3". Defect
3 routes only S106/S109/S113; it explicitly says the S107 and S112 corrections were lane-reported
and unverified. For S132 (S107) and S134 (S112) "routed by … defect 3" is an overstatement.
Smallest correction: "S131, S133 and S135 are routed by `round-25-verifier-spotcheck.md` defect 3;
S132 and S134 carry the S107 and S112 corrections that defect 3 records as lane-reported but
unverified".

## 5. Residual (adjacent, not part of S132's claim; no routed-defect cover)

The row's correction did not propagate into the knowledge entry's own citations, which S132 lists
as used-by:

```
corpus/knowledge/context-capacity.md:95-96   "unset context falls back to the training context and is split (S107, line 219)."
corpus/knowledge/context-capacity.md:222-223 "Behavior when the training context is re-adjusted at load (YaRN; S107 4113-4117)"
corpus/knowledge/context-capacity.md:258-261 erratum: S131-S135 "correct … the scope of S107 and S112" (no citation repair)
```

These are the round-25 ReopenS107 F2/F3 findings (YaRN range is 4114-4118, not 4113-4117; the
split is at 381-393, not 219). Defect 3 did not route them, so this is reported as residual, not
as an S132 defect: either repair the two citations or state in the erratum that they remain open.
No claim in S132 itself is contradicted by them.

## 6. Limits and housekeeping

- No llama-server was started by this seat (no port block in this item). `pgrep -af llama-server`
  at exit showed one process, PID 1665632 on port 47719, which is another seat's, not mine.
- No tool installs or updates.
- No lane production file was edited; no commit, push, jj command, or git index write. Read-only
  git used: `cat-file blob <base>:corpus/SOURCES.md`, `ls-remote`.
- Post-check lane change, not by this seat: at `2026-10-23 01:01:39 -0300` the working tree
  gained `fit.cpp`, `README.md` and `llama-kv-cache.cpp` (directory 13 → 16 entries;
  `ls --time-style=full-iso`). Each file's sha256 equals its SOURCES anchor and my fresh fetch, and
  `cmp -s` against my scratch copies exits 0 (`fit.cpp` 1f83da2a…, `README.md` 714c067b…,
  `llama-kv-cache.cpp` d0739eaf…). **They are untracked at the landed tip**, so the repair is
  worktree-only and a commit is owed:
  `git rev-parse HEAD` → f4066979096e3452ae731c0e09e50155c6d8258a;
  `git ls-tree -r --name-only HEAD -- .ufo/waves/round-26/sources | wc -l` → 13;
  the same listing `| grep -c 'fit.cpp\|README.md\|llama-kv-cache.cpp'` → 0 (exit 1);
  `git status --porcelain -- .ufo/waves/round-26/sources/` → `??` for all three.
  Therefore the Gate sentence at `round-26.md:14-16` ("the fetched bytes equal the lane snapshot …
  sha256 in each row's anchor cell") still FAILS at the measured commit for S131, S134 and S135,
  the defect seat `KamaR26.ReopenS131` reports and this seat endorses. S132 is unaffected:
  `llama-context.cpp` is tracked and `cmp`-identical to the fresh fetch. C1's counted rows are also
  unaffected: the 17 counted rows cite only `server-context.cpp`, `server-common.cpp`, `gguf.cpp`
  and `llama-context.cpp`, all inside the 13 tracked snapshot files.
- Scratch (all under `/fast/scratch/hyaku/kama-r26w2/ReopenS132/`): `llama-context.704366d.fresh.cpp`,
  `fit.fresh.cpp`, `common.h`, `server-context.fresh.cpp`, `server-common.fresh.cpp`,
  `gguf.fresh.cpp`, `README.fresh.md`, `llama-kv-cache.fresh.cpp`, `SOURCES.base.md`,
  `llama.tar.gz` and the extract `llama.cpp-704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/`.
- Files written in the lane: this report only,
  `.ufo/waves/round-26/w2-falsify/advice/ReopenS132.md`.
