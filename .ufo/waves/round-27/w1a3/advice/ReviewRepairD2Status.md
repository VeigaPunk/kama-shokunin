VERDICT: holds — item 2's counter claims verify against the frozen A3 bytes and "met only vacuously" is honest (no non-author control receipt was ever committed, no data seat ran); item 8's "not fixed" is accurate because count-c2.py is unchanged since round 26 and still reads parsed cell values from the receipt.

Reviewer: KamaR27A3.ReviewRepairD2Status (leaf; evidence for the later non-author reviewer, never the verdict).
Scope: corpus/lessons/round-27.md §Repairs items 2 (lines 36–39) and 8 (lines 72–74).
Frozen counter verified: `sha256sum .ufo/waves/round-27/count-c1.py` →
`49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765` — matches the stated A3 hash.
Working tree clean on all four files checked (`git status --porcelain` empty).

## Item 2 (lesson lines 36–39): HOLDS

Claim under review: the A3 counter "compares JSON-decoded request strings and
excludes help/version text and a healthy-run log"; the pre-data receipt part is
"met only vacuously (no data seat ran)". Routed defect (spot-check line 234,
F2): round-26 `count-c1.py:384` checked echo on raw bytes only — confirmed:
`git show eb09e742:.ufo/waves/round-26/count-c1.py` (sha256
`6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`) line 384 is
`c["e_not_echoed"] = sig not in req_bytes` where `req_bytes` (lines 371–374)
is `"\n".join([trig_key, args, path, headers, body_text])` — raw serialised
request, never JSON-decoded.

A3-counter evidence (all in `.ufo/waves/round-27/count-c1.py`):

- **JSON-decoded request strings compared.** `json_strings` (lines 351–362)
  recursively collects every decoded string key and value of the request body
  at any depth; `request_surfaces` (365–372) = request path + decoded strings
  + `json.dumps(body)` + `json.dumps(body, ensure_ascii=False)` (both
  serialisations, so neither raw-escape nor raw-UTF8 forms slip through);
  `static_checks` lines 585–587 append `f:in-request` when
  `occurs(sig, s)` hits any surface (`occurs`, 347–348: case-insensitive
  verbatim or whitespace-squashed). Predicate clause (f) states the same
  surfaces (docstring lines 44–48). The round-26 `\u00XX`-escape vector
  (spot-check lines 104–110) is now caught because decoding resolves the
  escape before comparison.
- **--help/--version text excluded.** `run_baseline` lines 496–502 runs the
  pinned `llama-server` with each of `--help`, `--version` (fixed env,
  non-zero exit or empty output → CannotEvaluate) and appends the output to
  `parts`; line 503 returns `"\n".join(parts)`. `main` line 652 stores it as
  `baseline`; lines 653–656 add `f:in-baseline-or-help` to every row whose
  signature `occurs` in it. So a signature present in help/version output is
  refused.
- **Healthy-run log excluded (F1 class).** `run_baseline` lines 480–495: the
  "default"-profile server runs the seven BASELINE_REQUESTS (144–153; all
  must return 200 or CannotEvaluate), the server is stopped (492–494, port
  must close), then line 495 appends `srv.log.read_text(...)` — the
  healthy-run server log — to the compared surface. Same `f:in-baseline-or-help`
  rejection applies. This matches F1's description in round-26.md:80
  ("warning lines on an unrelated startup failure count"): a signature that
  appears only as a healthy startup/warning log line can no longer be
  credited.
- **File-content echo (F3 class).** Not named in the lesson sentence but
  covered in the counter: `held_at_base`/`base_text` (lines 234–240, 268–272)
  + `b:held-at-base` (531–534) refuse any signature present (verbatim or
  squashed) in any tracked base file; clause (d) via `literal_elsewhere`
  (278–294, 569–571) refuses signatures found in any other literal of the
  pinned snapshot; and `e:bad-request` (576–581) plus `PROFILES` ownership of
  every argv (clause e, docstring 30–31; `PROFILES` 134–139) removes the
  row-controlled file argument that carried the F3 echo.
- **Message frame (context, X1).** Clause (h) implemented at lines 707–709:
  `h:same-message-frame` fires when the error message with the signature cut
  out (case-folded, non-blank) equals an earlier counted row's frame —
  "one message frame, one row".
- **KQ37 makes the rule a criterion.** `corpus/QUALITY.md:219` row KQ37 names
  exactly these surfaces (request path; JSON-decoded key/value at any depth;
  either serialisation; one row per message frame) and requires "a non-author
  shortcut-control receipt for each echo class the counter names … committed
  before any data seat".

**"Met only vacuously" — honest.** The KQ37/A3 precondition requires a
committed *non-author* shortcut-control receipt per class before data.
`git ls-tree -r HEAD .ufo/waves/round-27/w1-controls/` lists only 6 committed
files (dispatch.json, dispatched-payload.json, solution-spaces.json,
spec.json, spawn-result.txt, validate.err) — the 37-seat control wave's
dispatch records; zero advice/out receipts were committed (dispatch.json
counts: `"spawn": 37`; `controls-dispatched-at.txt` = 2026-10-23T04:55:48Z).
The 1431 committed `round-27/controls/*` receipts are L1-authored
(self-controls from `a712902`, amendment A2), not the non-author receipts the
rule names. With the precondition unmet and no data seat dispatched (plan
C1.disposition: withdrawn before data), the guard rule was never violated —
"met only vacuously" states exactly that, and the absence of the required
receipts is disclosed in the same repair item and §Claims lines 13–21.
[INFERENCE] Vacuous satisfaction is a statement about the rule's truth-value,
not a claim that receipts exist; the sentence's parenthetical makes that
explicit rather than hiding the gap.

## Item 8 (lesson lines 72–74): HOLDS

Claim under review: "`count-c2.py` reads cell values from the receipt: **not
fixed** this round" (round-25 defect 5 / round-26 defect 8; spot-check line
240).

- **Unchanged since round 26.** `git log --format='%h %s' -3 master --
  .ufo/waves/round-25/count-c2.py` → newest is `7f84cd0` (round-26 commit);
  `git log 7f84cd0..HEAD -- that file` is empty; HEAD blob sha256
  `2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b` equals
  the working-file sha256.
- **Cell values still come from the receipt.** `.ufo/waves/round-25/
  count-c2.py`: `json.load(open(path))` line 166, `cells = d.get("cells")`
  line 170; `cell_ok` (117–160) trusts receipt-asserted fields —
  `props_n_ctx`, `total_slots`, `models_n_ctx_train`, `kv_pool_n_ctx`
  (118–120), `slots_n_ctx` (122–125), `argv` (126–130), `log_lines`
  (131–139), `requests` status/token/timing fields (147–156). The counting
  loop (173–182) counts ids whose receipt cells pass `cell_ok`.
- **Round-26 repair bound only the `raw` hash map, not the parsed values.**
  `raw_bound` (84–114) checks each cell's `raw` values equal sha256 of the
  committed `final/raw/<id>.<suffix>` files — but nothing re-parses those
  raw files to derive `log_lines`, `kv_pool_n_ctx` or request timings, so a
  receipt whose parsed fields disagree with the committed raw bytes still
  counts. That is exactly defect 8's "reads cell values from the receipt";
  it remains open. The lesson's stated reason (attempt-2 seat died; task
  never resent) is consistent with the zero commits to the file this round.

## Residual risk / verification gaps

- Static reading only: count-c1.py's live path (Server/main) was not executed
  — this seat has no port block; "excludes help/version and healthy-run log"
  is verified by code path (baseline string → `occurs` → `f:in-baseline-or-help`),
  not by an observed run. [INFERENCE] that path behaves as written is
  supported by `CannotEvaluate` exits on baseline failures (489, 494, 501).
- Whether the author-committed `round-27/controls/*` receipts cover every
  echo class KQ37 names is outside this item's two-sentence scope; the
  non-author receipts the rule actually requires are absent either way.
- The vacuously-met phrasing could be misread as "receipts were committed but
  unused"; the parenthetical "(no data seat ran)" and the §Claims withdrawal
  paragraph prevent that reading in context.
- Round-26 raw-binding caveat: defect 8 stays open even though `raw_bound`
  binds cell `raw` hashes — the parsed fields counted are still receipt text.
