# WR02KnowledgeDraft — round-63 strict response grading (v2) landing text

Seat: WR02KnowledgeDraft (leaf, drafting). Judged on: operability. Milestone: draft landing text.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (freeze base 7ee8cbdf; amendment 1 at 03a6a1d8).
No corpus file edited. No commit, no mutating git/jj. Scratch removed after receipts were copied.

## Outputs

- Draft (the deliverable): `.ufo/waves/round-63/w1/out/WR02KnowledgeDraft/knowledge-append.md`
  — preface for L1 (not appended text) + the appended section, 45 lines (cap 80).
- Evidence in `.ufo/waves/round-63/w1/out/WR02KnowledgeDraft/`:
  `live-tip-receipt.json` (+ stdout/stderr, both empty), `hashes.txt`, `quote-check.txt` (24 fragments, 0 mismatches),
  `fixture-tally.tsv` (per-check pass/fail over the round-63 receipt tree, excluding this seat's receipt).

## What I did

1. Read the existing entry `corpus/knowledge/completion-request-plane.md` in the working tree and at HEAD 03a6a1d8.
   The working tree has an **uncommitted** section already titled `## Round-63 strict response grading, schema
   kama-completion-live/v2 (S527, S528)`; HEAD does not. My draft is written so L1 **replaces** that section
   (see F1), rather than appending a second copy under a near-identical heading.
2. Read the tip tool's check block (`git show 03a6a1d8:tools/kama-completion-live.py`, lines 198–480) and diffed the
   check names against round 62 (`7ee8cbdf`).
3. Verified the pinned source myself from the retained bytes (`.ufo/waves/round-63/source/`):
   - `server-task.cpp.704366d76` sha256 4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495 (matches S527 row)
   - `server-common.cpp.704366d76` sha256 b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442 (matches S528 row)
   Quoted 24 fragments by line number; all match after whitespace normalisation (`quote-check.txt`).
4. Ran the tip tool once live (no hold window) from a `git archive` of the tip's `tools/` and `registry/` (read-only):
   `python3 kama-completion-live.py --work <scratch>/run1/work --out <scratch>/run1/receipt.json --nonce wr02-r63-kn-1`
   → exit 0, `verdict REQUEST_OK`, 22 evaluated checks, all passed. Port auto-picked, unregistered loopback.
   Tool sha256 e24bc944… (`hashes.txt`). Server: `llama-server` b11755 via `~/.local/bin` symlink, sha b6a31a8e…
   (pinned). Model `~/.cache/kama-shokunin/models/stories260K.gguf`.
   First attempt exited 1 only because `registry/endpoint-consumers.tsv` was not in my archive (setup error,
   not a tool defect); re-run with `registry/` archived succeeded.
5. Mapped each completion-response check to a ground: **source** (pinned bytes, line-cited), **observed** (live
   receipt), or **own** (the tool's bound). Mapped failure signatures from the round-63 receipt tree (see `fixture-tally.tsv`).

## Findings

### F1. The entry already carries an uncommitted round-63 section (overlap)
The working tree (`git diff`: `corpus/knowledge/completion-request-plane.md` +47/-3, `corpus/SOURCES.md` +2, `PROVINCE.md` +2)
already holds `## Round-63 strict response grading, schema ... (S527, S528)`. Appending my section as written would
produce two sections on the same topic. The preface in `knowledge-append.md` tells L1 to replace it. Recommendation:
land the replacement, not an append.

### F2. The working-tree section has errors my draft corrects
| # | Working-tree text | What the tip and pinned bytes show |
|---|---|---|
| a | "Round 63 adds **nine** checks" | Six check names are new (`completion_headers`, `completion_untruncated`, `completion_choice_shape`, `completion_id_created`, `completion_prompt_tokens`, `completion_request_bound`). Two are strengthened (`completion_usage`, `completion_timings`). `completion_finish_reason` is **unchanged** from v1, yet the table lists it as a round-63 row. "nine" appears in neither the tool nor the counter. |
| b | `completion_choice_shape`: `index` 0 "source (S527 366–386)" | Source shows only that the field is emitted (`{"index", index},` line 382). The value 0 is not in the retained bytes (`index` is set outside them). Observation-only. |
| c | `completion_choice_shape`: `logprobs` null "unless probabilities were requested" | Gate is `!stream && probs_output.size() > 0` (line 369). Accurate in spirit; the draft states the gate exactly. |
| d | "observed (620 bytes in the round-63 run)" | Byte count is not constant. Live tip run: 621. EX01C1Repeat, seven repeat runs of the same request: 607–623. Draft states the range and that only `Content-Length` equality matters. |
| e | `completion_untruncated` failure signature "truncation flag set, or length differs" | Observed: `trunc_cl` (120 of 900 bytes) fails `completion_envelope`, not `completion_untruncated`, because the body is unparseable and every body check is gated by `if ok_env:`. Only `pad` (cap 65,536, CL 70,448) fails `completion_untruncated`. Draft records both. |
| f | Ground for `completion_timings` / `completion_usage` implicit | Not stated that the whole block after `completion_envelope` is gated by `if ok_env:` (tool lines 368–437). Draft states it. |
| g | "source" grounds cited as S527 366–393 only | `timings` is attached at S527 lines 399–401 (`if (stats.is_set()) { res["timings"] = stats.to_json(); }`), outside the cited range. See F3. |

### F3. Source-row fixes needed in SOURCES.md (for the L1 when the rows land)
- **S527 (`server-task.cpp`)**: add lines **399–401**. The `timings` object exists in the completion response only via this
  attachment, and only when `stats.is_set()`. Without it, the entry's `timings` claim has no source.
- **S528 (`server-common.cpp`)**: teaches text says "`timings` **always** names …". Change to "when present" (per S527 399–401).
- **Bad-request source**: the `{code, message, type}` object and `invalid_request_error` → 400 mapping are in
  `server-common.cpp` **lines 91–133** (`format_error_response`, verified lines 95–97, 128–132). S528's row cites only 139–160,
  so `completion_bad_request` has no source row. Add 91–133 (or a third row).
- **Wrapper**: the `{"error": …}` wrapper that the grader expects is not in the retained bytes; it is observed only.
- **Id**: `gen_chatcmplid()` (lines 181–182) produces `chatcmpl-` + 32 characters; the completion route's id assignment
  (`oaicompat_cmpl_id = …`) is not in the retained files. The live id is `chatcmpl-` + 32 chars (length 41); the draft
  says so and keeps the id observed.

### F4. Grader defects found at tip 03a6a1d8 (routed to L1; not fixed here)
1. **`completion_fingerprint` accepts a trailing newline.** `FINGERPRINT_RE = ^b\d+-[0-9a-f]{9,40}$` (tip line 75):
   `$` matches before a final newline, so `b11755-704366d76\n` passes. Receipt `RV01ToolV2/receipts/fp_newline.json`
   is `REQUEST_OK` with `system_fingerprint` = `'b11755-704366d76\n'` (verified in Python: `re.match` True, `re.fullmatch` False).
   Fix: `fullmatch` or `\Z`. This check is on the calibration/operability path, so it counts.
2. **Non-object `usage` yields `SETUP_ERROR`, not `FAIL`.** `u = cj.get('usage') or {}` (line 407) followed by `u.get(...)`
   raises on a truthy string. Receipt `RV01ToolV2/receipts/usage_str.json`: `setup_error: AttributeError: 'str' object has no attribute 'get'`,
   verdict `SETUP_ERROR`. The receipt records 14 evaluated checks, all passing (`completion_envelope`, `completion_choice_shape`, `completion_fingerprint`, `completion_id_created`, `completion_headers`, `completion_untruncated`, `completion_finish_reason`, `completion_model_id`, `models_alias_id`, `props_alias`, …); the crash stops the run before `completion_usage` is recorded, so no check names the defect. A grader that cannot grade a malformed field should record a graded `FAIL` on
   `completion_usage` (the exit-code mapping treats `SETUP_ERROR` as not-evaluated, which hides the defect).
   A missing `usage` does fail normally (`or {}`).
3. **Invalid UTF-8 passes.** `_cap` decodes the body with `errors='replace'`; the body sha256 is over raw bytes, so the receipt
   is self-consistent. Receipt `RV01ToolV2/receipts/nonutf8.json` has `text` `' � mat on the floor'` and is `REQUEST_OK`.
   The draft lists this under "Not asserted"/open defects.

Minor, not graded: the tool's module docstring still says "lane-owned live request plane (round 62)" in its first line; the
schema note below it correctly says v2/round 63.

### F5. SC01 quote not on disk at drafting time
The item asks for the quote "located by seat SC01 after you verify it yourself". At drafting time there is no
`.ufo/waves/round-63/w1/out/SC01ServerTask*` artefact (`find` over `.ufo/waves/round-63` returned nothing). Its
scratch directory exists (`/fast/scratch/hyaku/kama-r63/w/SC01ServerTask`) but I did not read its outputs. I located
and verified every quote myself from the same sha-matched bytes (24 fragments, 0 mismatches). **L1: reconcile these
against SC01's quotes when SC01 lands; if they differ, the pinned line wins.**

### F6. Source id placeholders
The draft uses `SNEW-task` (server-task row) and `SNEW-common` (server-common row) instead of S527 / S528, as the
item asks for `SNEW`. The preface maps them to the working-tree numbers. L1 assigns final ids.

### F7. Gating nuance missing from the working-tree table
The working-tree table lists nine rows as if independent. In the tip tool, `completion_headers` through
`completion_deterministic` are all inside `if ok_env:`. Receipts confirm it: `trunc_cl` reports one check (`completion_envelope`).
The draft says so in its scope paragraph.

## Per-field tally (round-63 receipt tree, excluding this seat; `fixture-tally.tsv`)

| check | pass | fail | example failing receipt (fixture) |
|---|---|---|---|
| completion_envelope | 133 | 8 | RV01 trunc_cl |
| completion_headers | 133 | 0 | — |
| completion_untruncated | 132 | 1 | RV01 pad |
| completion_choice_shape | 129 | 4 | MT03 I1 |
| completion_finish_reason | 133 | 0 | — |
| completion_model_id | 132 | 1 | EX05 c_y5_alias_empty |
| completion_fingerprint | 133 | 0 | — (defect F4.1 passes fp_newline) |
| completion_id_created | 133 | 0 | — |
| completion_usage | 132 | 0 | — (defect F4.2 SETUP_ERROR usage_str) |
| completion_timings | 124 | 8 | MT05 V1–V8 |
| completion_prompt_tokens | 128 | 4 | RV01 tokenize_mismatch |
| completion_request_bound | 129 | 3 | MT07 M3 |
| completion_deterministic | 127 | 3 | MT03 I3 |
| bad_request_graded | 139 | 0 | — |

## Verification performed by this seat
- Live run at the tip: `REQUEST_OK`, 22/22 evaluated checks passed (`live-tip-receipt.json`).
- 24 source fragments re-read at the cited pinned lines (`quote-check.txt`): 0 mismatches.
- Defect F4.1 reproduced by a direct regex test on the fixture value.
- Defects F4.2 and F4.3 read from fixture receipts (`usage_str`, `nonutf8`) and from the tip code path; not re-run live
  (a canned server is needed; the receipts are from the round-63 tree).

Not run: the two counters (`round63-c1-counter.py`, `round63-c2-counter.py`) and the self-description reconciler. Not in this item's scope; other seats own them.

## Tools installed or upgraded
None. The seat used python3 stdlib and the existing `llama-server` b11755 (PATH symlink, operator-provided). Pacman not used.

## Host and bounds
- Only read-only git was run in the lane (`show`, `status`, `diff`, `archive` into scratch). Nothing committed, no mutating command against the lane or fleet.
- The lane path reports the enclosing fleet repo in `git status` (`?? kama-shokunin/` at fleet root). Observation only; I did not touch it.
- The live run used the lane tool on an auto-picked unregistered loopback port, from a scratch copy of the tip's
  `tools/` and `registry/`. No registered consumer port was contacted. Foreign llama-servers (1234, 45669) untouched.
- Scratch `/fast/scratch/hyaku/kama-r63/w/WR02KnowledgeDraft` removed after receipts were copied into the out dir.

## Landing checklist for L1
1. Replace the uncommitted round-63 section in `corpus/knowledge/completion-request-plane.md` with `knowledge-append.md`'s section (do not append).
2. Add S527 lines 399–401 and fix S528 "always" → "when present"; add `format_error_response` lines 91–133 for the bad-request source.
3. Reconcile source quotes with SC01's when it lands (F5).
4. Decide on F4 (three grader defects). The fingerprint newline and the `SETUP_ERROR` mapping are both grader-correctness issues on the operability axis.

Tally: 14 completion check rows drafted; 3 grader defects; 3 source-row corrections; 24/24 quote fragments verified; live tip run REQUEST_OK 22/22.
