# ResProseCorrections — residual review of SKILL.md meaning-cell/prose corrections

Item: `SKILL.md` diff `e49b4cf7..9ce5bd37` (data commit → landed tip). Seat:
KamaR28.ResProseCorrections, read-only; no counter/server run, no lane writes
except this file. LSP not applicable (prose diff review; no server mounted for
this file class — `xd://lsp` unmounted, so judgment rests on direct file reads
and the committed reviewer artifacts, not grep-as-proof).

## Verdict: holds, with two residual notes

Every changed cell and sentence is supported by the wave-2 advice file that
motivated it and/or by the pinned source. Counted cells are byte-unchanged.
All reviewer-reported defects within the changed surface were corrected.

## 1. Counted cells untouched — verified mechanically

`git show <commit>:SKILL.md | grep '^| F28-' | awk -F'|' '{print
$2"|"$3"|"$4"|"$5"|"$7}'` is byte-identical between `e49b4cf7` and `9ce5bd37`
(md5-equal extracted streams; 34 rows both sides). Only column 5 (meaning)
changed, and only in rows the lesson's gate table names as admitted
(round-28.md:195). Final receipt at tip confirms the count is undisturbed:
`final/c1-9ce5bd37.out` reports `registered 34 counted 26 target 18 met True`;
`final/c1-A0-9ce5bd37.out` 34/34.

## 2. Per-edit support check

### Intro prose (SKILL.md:1147-1159 at tip)

- "completion response's `generation_settings` (not `/props`
  `default_generation_settings`)": disambiguation is accurate — the two objects
  are distinct (ScoutSkillContradictions.md:16 item 2; the completion response
  carries `generation_settings`, `/props` carries `default_generation_settings`).
- "Numbers are converted to the field's C++ type before the bound check or
  clamp (`server-schema.cpp:531-545`): a fractional value is truncated toward
  zero first": the pinned file places `field_num<T>::eval` at exactly 531-546
  (checked with line numbers): `T tmp = data.at(n).template get<T>()` at :541
  precedes `tmp < min || tmp > max` at :542, and the soft branch clamps `get<T>()`
  at :539. Truncation-toward-zero and wrap are measured, not inferred:
  `n_probs 2.5→2` (F28-26), `t_max_predict_ms -1.5→-1→200` and `top_k 5e9→
  705032704` (RowReview04.md:10-11,20). This is the CriticDepthAxisPostData F1
  "explain the actual order once" correction (advice/:42).

### Meaning cells

| Row | Landed text supported? | Basis |
|---|---|---|
| F28-03/04 "bound is checked after conversion to an integer" | yes | Critic F1 correction; pinned :531-546 |
| F28-05 "(half context)" + conversion clause | yes | schema L60 desc literally states "0 = half context"; conversion clause per F1 |
| F28-07 "-1.5 becomes -1 and passes"; "-1 or 0 sets no … limit (> 0 only)" | yes | RowReview04:10-12 (probe_t_float 200, probe_t_zero 200; server-task.h:69, server-context.cpp:2085); near-verbatim reviewer correction |
| F28-08 "5000000000 is stored as 705032704" | yes | RowReview04:20 live probe (wrap 5e9 mod 2^32 = 705032704); "top-k disabled" source-backed per :19 |
| F28-09 "top-p filter is disabled; temperature and the other samplers are unchanged" | yes | CriticDepthAxisPostData F2 (:44-52, proposed wording); DataG03 saved response retains temperature 0.8/top_k 40/min_p 0.05; RowReview05 held |
| F28-11 "keep values within the float32 range or read the stored value back, since a finite value can still saturate" | yes | RowReview06:39-43 corrected sentence (minor rephrase, same claim) |
| F28-14/16/17/21/22 uniform "generic float32 conversion, not a field bound … (field-omitted value X)" | yes | RowReview07:10 (base 1.0), RowReview08 (base 1.0 repeat_penalty), RowReview09:5 (base 0.0 frequency_penalty), RowReview11:11-12 (bases 5.0 / 0.10000000149011612). "No limits" verified: snapshot L123, L130, L133, L161, L164 are `field_num` + `set_desc` only. Removes the over-general "beyond the float range"/"largest finite float" wording each reviewer flagged. |
| F28-19 | yes | near-verbatim RowReview10:16 replacement (adds "so a negative value is refused rather than clamped" — supported by `set_hard_limits` L154) |
| F28-20 | yes | near-verbatim RowReview10:24 replacement; drops the "mode actually used" overreach Critic F2 flagged |
| F28-25 "one observed point … uint32 wrap modulo 2^32 … -1 sentinel stored as 4294967295" | yes | RowReview13 (probe 4294967297→1 falsified "wrap to 0"); Critic F3; snapshot L175 comment "seed is uint32_t", L177 desc "-1 = random"; DataG08 notes recorded -1→4294967295 |
| F28-27 "checked after conversion to an integer … this bounds 400 (not every 400)" | yes | Critic F1 (:34-36, n_keep-style truncation) + ScoutSkillContradictions:47 ("the 400 as their own request error" is true only for the bounds message; other 400 classes exist) |
| F28-33 "empty list falls back to the launch's default stop strings (none with this argv)" | yes | RowReview17:12,18 — handler falls back to `params_base.antiprompt` when result list empty (snapshot L435-450); fixture argv had none |
| F28-34 "dropped without an HTTP error (the server log warns)" | yes | RowReview17:32 — LOG_WRN per unmatched name/char observed in server.log; HTTP stays 200 |

### "Fields measured with no countable row" paragraph

- `echo` moved out of the `field_bool` list to "the `field_json` `echo`":
  correct — snapshot L306 `add((new field_json("echo"))` (ReviewSkillSectionIntro
  finding 1).
- `include_usage` removed from the bool list; new clause "read only inside
  `stream_options` (a top-level `include_usage` or a non-object `stream_options`
  is ignored with 200)": supported — snapshot L26-28 declares it as a
  `field_nested` subfield; DataG16/G17 probes (top-level ignored 200, non-object
  dropped 200, nested non-boolean 400). Covers findings 2 and 3
  (stream_options is now named inside the clause). The dropped name from the
  `field_bool` enumeration is accurate: it is a nested subfield, not a
  top-level `field_bool`.

### Instrument registry rows

- Count-c1 exit map gains "an uncaught error (e.g. malformed registry JSON)
  exits 1 with a traceback and no receipt": verified in `count-c1.py:531`
  (`json.loads` outside the `try`), `:639-643` (only `CannotEvaluate` is
  caught), `finish()` at `:646-649` — a failed `--out` write also escapes.
  ReviewInstrumentRegistry P2 :3.
- Echo-recheck write scope gains "and its `<out>.server.log` sidecar":
  verified `tools/echo-recheck.py:187-190` (opens `str(out)+".server.log"`),
  `:335-338` (pre-existence → CannotEvaluate). ReviewInstrumentRegistry P2 :2.

## 3. Reviewer-reported defects left uncorrected: none in scope

Sweep of all 33 advice files (grep for defect markers + full reads of the
admitted seats): every row whose meaning was flagged (F28-05/07/08/09/11/14/
16/17/19/20/21/22/25/27/33/34 plus F28-03/04 under critic F1) was corrected.
ReviewSkillSectionIntro findings 1-3 all corrected. ReviewInstrumentRegistry
P2s both corrected. ReviewGateRegistryCheck's occurrence-only finding was
already disclosed in the pre-diff text ("occurrence check only") — admitted as
a statement, not a code change. Rows reviewers marked "holds, no correction"
(F28-01/02/06/10/12/13/15/18/23/24/26/28/29/30/31/32) were not edited.

## 4. Residual notes (not defects)

- F28-21/22: RowReview11's suggested text also mentioned negative-side
  saturation; the landed text omits it. Omission, not overclaim — the flagged
  defect (implying the declaration itself clamps to "the largest finite float")
  is removed.
- F28-20 retains reviewer's own phrase "confirm the effective mode", which
  still lightly shades toward stored-setting-as-mode; it is the reviewer's
  proposed wording, so consistent with the admission.
- New text "read the stored value back" / "clients send -1 or a uint32-range
  seed" are prescriptive clauses of the same register the reviewers themselves
  used; none asserts an unmeasured behavior.

## 5. New unsupported claims introduced: none found

The only additions beyond reviewer text are "(half context)" (schema L60,
verbatim semantics) and the `(not /props default_generation_settings)`
disambiguation (scout's own distinction). Both are source-backed.

Residual risk: none identified in the changed surface; unchanged cells were
outside this item.
