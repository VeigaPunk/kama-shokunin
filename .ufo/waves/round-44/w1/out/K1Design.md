# K1Design — round 44, C1 design attack (population and predicate)

**Verdict:** C1's population is complete for rows that pin a *file* at 704366d76 but not for the pin itself —
S038 (the release-identity row, `on-release`, the row `registry/engine-pins.tsv` names as the pin's source)
and S477 (the tag inventory the watch table is built from) are both excluded and both now stale;
the predicate's byte equality is checked on the ledger's single `path`, which for two rows is not the file
the row's statement cites (S047 is scored `VALID` on `server-queue.cpp` lines 26-38/529-534/575-577 that are
`task_resets_idle_timer` and `post_tasks`, while its `server.cpp` signal evidence is never read), and
20 of 91 rows carry their strongest line citations in `teaches`, which the cited-line rule never looks at.

Freeze held throughout: lane read-only, all work from `git -C …/shared/llama.cpp show/diff/grep`, counter and
preregistration untouched. Commands below were run from `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## 1. Completeness — pin-dependent rows outside the frozen population

Population re-derived with the frozen counter's own loader (receipt
`out/K1Design/population-and-coverage.txt`):

```
python3 - <<…  import tools/round44-release-recheck-audit.py; population(git show 9d9cc93e:corpus/SOURCES.md)
derived population at base 9d9cc93e: 91
  pin 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad count 89
  pin c0fd78626405c6d9b934efef0ec7291fcc20e3d6 count 1    (S001)
  pin ad1b88ca0d37a2171efba1c04f1a3531c78f1b52 count 1    (S015)
```

The preregistration's id list is exactly this set (91 ids, `prereg-only: []`, `derived-only: []`), but the same
frozen sentence says **"90 pinned at 704366d76 = b11755"** (`.ufo/waves/round-44/preregistration.json`,
C1 `statement`). 89 + 1 + 1 = 91; **89** are pinned at 704366d76. The release observation in the same entry
(`newer=117`) is right: the local clone holds 117 `bN` tags above b11755 and both `b11888` and `b11889`
(`git -C …/shared/llama.cpp tag --list 'b*' | …`). No mechanism reads the prose, so this is a statement defect,
not a scoring one — but it is the only quantitative sentence in C1 and it is wrong by one.

Full list with the reason each is out: `out/K1Design/completeness.tsv`. The three that matter:

| key | locator | why out of population | why it matters |
|---|---|---|---|
| **S038** | `corpus/SOURCES.md:50` | source is `releases/tag/b11755` (+ `api.github.com/.../releases/tags/b11755`); population regex only accepts `blob\|tree` / `raw.githubusercontent` | it is the **only** llama.cpp row whose cadence is literally the release event; its anchor is the pin's definition (`tag b11755 → 704366d76`) and its teaches is the asset digest; it is `registry/engine-pins.tsv:4`'s `source` (item 3) |
| **S477** | `corpus/SOURCES.md:230` | own-work `git ls-remote` command, not a ggml file; cadence `30d` | teaches "115 bN tags above b11755", "highest b11887". At b11889 the local clone has 117 above and b11888/b11889 exist. The number C1's own statement relies on ("pin-watch has reported as behind") is produced by a row the ledger cannot flag |
| **S041 / S046 / S055** | `corpus/SOURCES.md:53,58,67` | own-work live receipts, cadence `every round` | their scope is "b11755 runs"; they are what makes the endpoint claims true of the *installed* build, and no release trigger will ever recheck them |

Also out, with reasons in the TSV (none pin-sensitive): S026 (`/pull/18001`, rejected), S028 (`/issues/4746`, 90d,
rejected), S014 and S058 (pinned `ggml-org/**ggml**`, a different repo — on-release pinned rows with no release
recheck at all), S039 (HF GGUF, every round). And the registries/artifacts that bind to the pin without being rows:
`registry/digest-ledger.tsv:2,3`, `registry/error-signatures-r26.json:3`,
`registry/request-field-outcomes-r28.json:3`, `corpus/knowledge/engine-pin-watch.md:51`,
`SKILL.md:681,1064,1139,1144,1238`, `tools/kama-llamacpp-live.py:56`
(`LLAMA_COMMIT = '704366d76…'`).

Two rows *in* the population are misdescribed by the claim's wording: S001 and S015 have URL ref `master`
(a moving ref); their pin is taken from the anchor's 40-hex. So "source is a … file pinned to a commit" is
exact for 89 of 91, not 91.

## 2. Is "re-verified at b11889" the right freshness question for rows pinned on purpose?

**What the claim does show:** each population row's anchored excerpt still exists in the b11889 bytes, at a
recorded location, re-derivable from the pin/release blobs — i.e. the lane can say *which* of its pinned excerpts
upstream has moved and where they moved to. That is a real, fail-capable measurement: 6 of 91 draft rows already
fail it (`S001 S015 S037 S043 S059 S108` → TODO), and the failures are the `server.cpp` entrypoint refactor
(`f3269ef96 server: refactor server entrypoint`, 773 lines changed; 134 commits, +2481 lines in `tools/server`
between pin and release).

**What it does not show:**

- **It is not a truth question about the row.** A row pinned at 704366d76 stays true of 704366d76; b11889 is a
  different object. The lane already says this correctly at `corpus/knowledge/engine-pin-watch.md:53-56`
  ("The b11755 entries still describe b11755. Whether b11887 changed the surfaces they describe … has not been
  checked"). The C1 ledger should inherit that framing: `holds` means "upstream still contains this text",
  never "the lane's claim is still true of current llama.cpp", and `drifted` must not be read as falsification.
  The claim's own phrase "re-verified at b11889" invites the stronger reading.
- **The running system is b11755.** The installed tree, `libllama-server-impl.so` digest
  (`registry/digest-ledger.tsv:3`), the live harness constant (`tools/kama-llamacpp-live.py:56`) and every
  SKILL.md fixture section are bound to 704366d76. A b11889 verdict has no bearing on endpoint behaviour of the
  binary the lane serves; conversely a repin would invalidate those fixtures without touching this ledger.
- **New release content is out of scope.** `server.cpp:187` registers `/tts` and `server.cpp:189` registers
  `/v1/realtime` at b11889; `server-schema.cpp:248-266` adds a dedupe-then-limit rule for `dry_sequence_breakers`
  (a duplicate-laden request rejected at b11755 is accepted at b11889). No row is missing, no row is drifted —
  `holds=81` coexists with a route inventory that is now incomplete. C1 measures fidelity of what is written,
  not completeness against the release.

**Candidate counterexamples I ran (and their outcome):**

- S036 teaches a universal: "Every non-frontend path, `/v1/models` and `/health` included, answers 503 … before
  the API-key check". Two new non-frontend paths exist at b11889. They do **not** break it:
  `vendor/cpp-httplib/httplib.cpp:10351-10361` runs `pre_routing_handler_` before the WebSocket upgrade, and
  `tools/server/server-http.cpp` at release still calls the state gate (308-329) before the API-key middleware
  (348-360). S036's `holds` is defensible.
- S042 ("the handler's only 200 body is `{"status":"ok"}`"): release `server-context.cpp:5606-5617` still
  `res->ok({{"status","ok"}})` and `ok()` at 5171-5174 still sets 200 + compact JSON. Holds.
- S479 ("`max_model_len` occurs 0 times"): `git grep -c max_model_len <release> -- tools/server/server-models.cpp`
  → no match; the guard is at release 2325-2326. Holds.
- S054/S056 (repeated-flag semantics): the whole `common/arg.cpp` delta is HF `finalize_file` plumbing; the
  warning block and host-clear still hold (837-845, 3345-3351). Holds.
- S047 (signal ordering): survives at release — `server.cpp:29-38` unchanged (`exit(1)` on second signal),
  install at 651-652 precedes `start_loop()` at 671, `running` mechanics unchanged (`server-queue.cpp:134,279`).
  `return 0` at 688. The statement is fine; the *ledger row is testing the wrong file* (see below).

**So the right question depends on the row.** For a row whose `teaches` is a quote of anchored lines, byte
relocation at b11889 is the right freshness test. For a row whose `teaches` is a behavioural statement whose
supporting lines live outside the anchor (or in a second file), byte equality is necessary and insufficient,
and what the ledger records is a *relocation*, not a re-verification. Concretely: **20 of 91 rows put STRONG
line citations in `teaches` that their `pin_lines` do not cover**, because `cited()` reads only cells 1 and 5
(`tools/round44-release-recheck-audit.py`, docstring "Cited lines: numbers in the source and anchor cells",
and `cited()` at the implementation). List in `out/K1Design/population-and-coverage.txt`. Example:
`S114`'s teaches says "`get_slots` refuses when `params.endpoint_slots` is false (`server-context.cpp:5365-5367`)";
the draft anchors **5366 only** → release 5684. At the pin 5365-5367 is the refusal block; at b11889 line 5365
is `return format_oai_sse(json {{ "error", res_json }});` and the refusal is at 5683 — the row reads `holds`
while the reference a reader would follow ("5365-5367") now points at unrelated code. Same shape at S116
(teaches 3078-3085, ledger 3084; statement does survive at release 3224-3235).

## 3. Does `registry/engine-pins.tsv:4`'s `source` cell (S038 only) misdescribe the dependency?

**Yes — it is the right row for the tag→commit mapping and the wrong description of what depends on the pin.**

- `registry/engine-pins.tsv:4`: `llama.cpp … b(\d+)  b11755  S038`.
- `corpus/SOURCES.md:50` (S038) scope: "identity of the official b11755 Linux x64 CPU binary kama ran; **not
  runtime behaviour**"; `used-by`: one file (`corpus/knowledge/llamacpp-loading-lifecycle.md`).
- What actually depends on the pin: 89 population rows (`S035`…`S191`, `S479`), the two JSON outcome registries,
  the installed library digest, the live harness constant. None of that is S038's scope, and S038's own
  `used-by` says so.
- The cell is also **inconsistent across rows**: `sglang` → `S474` is the tag-inventory row; `vllm` → `S327 S363`
  are doc rows; `llama.cpp` → `S038` is the release-asset row, while the llama.cpp tag-inventory row `S477`
  (`corpus/SOURCES.md:230`) is omitted. The column means a different relation per engine.
- And the watch table contradicts the registry: `corpus/knowledge/engine-pin-watch.md:51` lists
  "rows to recheck: **S038 and the entries citing it**", i.e. the lane already knows the dependency is the
  entries, while `engine-pins.tsv` names one.
- Finally the registry records the **tag only** — `704366d76` appears nowhere in the file — so the commit the
  C1 ledger keys on cannot be recovered from the registry that declares the pin; it must be read out of S038's
  anchor prose (or S477's). That is the misdescription that bites: the pin's stated source is the one
  `on-release` llama.cpp row C1's population drops (item 1).

Smallest safe correction (proposed, not applied): `out/K1Design/proposed-engine-pins.diff` —

```diff
-llama.cpp	https://github.com/ggml-org/llama.cpp.git	b(\d+)	b11755	S038
+llama.cpp	https://github.com/ggml-org/llama.cpp.git	b(\d+)	b11755	S038 S477
```

I did **not** propose rewriting `engine-pin-watch.md:45-51`: it is a dated measurement (`Result at
2026-10-25T20:03Z`) and a fresh `ls-remote` is the only authority for it. What I can say from local evidence is
that b11888 and b11889 exist and 117 `bN` tags sort above b11755 in the shared clone, so the table's
"b11887 / 115" is behind the release C1 is rechecking against — the integrator should re-run
`tools/pin-watch.py check --pins registry/engine-pins.tsv` rather than hand-edit the row.

## Defects (exact location, command that shows it, proposed fix)

**D1 — S047 is scored `VALID` on ranges from the wrong file.** `tools/round44-release-recheck-audit.py`
`check_row()` (and `population()`'s single `path`) cannot express a row whose statement cites two files.
S047 (`corpus/SOURCES.md:59`) is pinned to `tools/server/server-queue.cpp`
but its anchor is "`server.cpp` `signal_handler` 29-38 (statics 26-27), handler install 529-534, `start_loop`
call 575-576, `return 0;` 590". The draft (`out/K1Design/frag_s047_draft.tsv`) records
`pin_lines=26-28,29-38,132-136,141-143,278-280,529-534,575-577` **of server-queue.cpp** — 26-38 there is
`task_resets_idle_timer`/`server_queue::post`, 529-534 is `post_tasks()`, 575-577 a comment. Evidence:

```
$ python3 .ufo/waves/round-44/tools/check-fragment.py c1 …/frag_s047_draft.tsv …   → VALID S047
$ python3 .ufo/waves/round-44/tools/check-fragment.py c1 …/frag_s047_honest.tsv …  → S047 invalid: pin_lines miss cited lines [26, 27, 29, 30, 31]
```
(the honest row covers only the server-queue ranges 132-136,141-143,278-280 and is **rejected**; the wrong-file
row is **accepted**). The row's `server.cpp` half is never read, so "re-derivable from upstream bytes" is false
for exactly the rows that need two files (S043 (`corpus/SOURCES.md:55`) is the mirror: path `server.cpp`, anchor also cites
`server-queue.cpp`; its draft is invalid for an unrelated reason). Fix (future rounds; frozen now): allow
`path:lines` elements in `pin_lines`/`release_lines`, or require that every `<file> <lines>` mention in the
anchor resolves to a declared path, and reject the row when a cited file has no path. At minimum the ledger
`note` for S043/S047 must name the second file and its release position.

**D2 — `cited()` ignores the `teaches` cell.** `tools/round44-release-recheck-audit.py`, `cited(c)` builds from
`c[1] + " " + c[5]` only. 20/91 rows carry STRONG citations in `teaches` that `pin_lines` need not cover
(receipt `out/K1Design/population-and-coverage.txt`); S114/S116 are the worked examples above. Fix: include
`c[6]` in `cited()` so the pin range must contain the taught statement's own references, or add a ledger column
for the release position of the `teaches` citation.

**D3 — population prose count.** `.ufo/waves/round-44/preregistration.json`, C1 `statement`:
"(90 pinned at 704366d76 = b11755)" vs 89 derived (S001→c0fd7862, S015→ad1b88ca). The prereg id list is
correct, so this is a sentence-level error. Fix: the round-44 SOURCES section and this round's scorecard should
state 89 + 1 + 1 = 91.

**D4 — S038 is `on-release` and unrechecked, with no other mechanism.** `corpus/SOURCES.md:50`; population rule
in `tools/round44-release-recheck-audit.py` (`URL` regex). Its b11889-relevant facts (tag→commit, asset digest)
are not derived anywhere this round. What *is* derivable offline: `git -C <clone> rev-parse b11755^{commit}` →
`704366d76…`, `b11889^{commit}` → `d854d98b…` (both verified). Fix: one line in the round-44 SOURCES section
recording that S038's tag→commit relation was re-derived at b11889 time and that its asset digest stays
unverified without network; do not let the section imply S038 was covered by the ledger.

**D5 — the "behind" trigger is owned by an out-of-population row.** `corpus/SOURCES.md:230` (S477, cadence 30d)
and `corpus/knowledge/engine-pin-watch.md:51`. Fix: as D4, plus re-run `tools/pin-watch.py check` for the date.

**D6 — draft rows that cannot pass as written** (found by running the frozen counter on the draft; integrator
will hit these):
```
$ … check-fragment.py c1 frag_s059_draft.tsv  → detail: S059 invalid: ranges do not parse or counts differ
$ … check-fragment.py c1 frag_s043_draft.tsv  → detail: S043 invalid: unknown verdict
```
S059 is `changed=0` with `pin_lines=-`: `unchanged-file` still needs a parseable pin range carrying ≥20
non-whitespace chars (and `release_lines` textually equal to it). S043/S037/S108 still carry the literal verdict
`TODO`. The section is also absent and the ledger absent at the freeze commit:
`python3 … ; "Round-44 release re-verification" in git show HEAD:corpus/SOURCES.md → False`,
`git cat-file -e HEAD:registry/release-recheck-b11889.tsv` → absent; the draft scores
`pop=91 rows=91 valid=85 unverified=6 … flags_missing=0 section=0 met=False` — i.e. `met` is gated on the
section, not on the six rows alone.

**D7 — `holds` vs `holds-reworded` mis-set risk.** S043's anchor says "`sigaction` for SIGINT and SIGTERM
529-534, installed after `load_model` (507…)". At b11889 that text exists at 320-325 and is called at 545/652
(and the router path disables it at 763), so the anchored *sentence* about b11755 is fine while the release
numbers moved. If S043 is later filed as `holds` on a relocated range, the note must say the pin remains the
authority (engine-pin-watch.md:53-56's framing); otherwise the ledger reads as a claim about current llama.cpp.

## Receipts (absolute paths)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design.md` — this report
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/completeness.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/population-and-coverage.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/proposed-engine-pins.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/frag_s047_draft.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/frag_s047_honest.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/frag_s043_draft.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/frag_s059_draft.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/check-s047_draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/check-s047_honest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/check-s043_draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Design/check-s059_draft.out`

Tooling: nothing installed, nothing upgraded; no network fetch, no pacman, no service touched. Scratch
`/fast/scratch/hyaku/kama-r44/K1Design` removed below after copying the fragments out.
