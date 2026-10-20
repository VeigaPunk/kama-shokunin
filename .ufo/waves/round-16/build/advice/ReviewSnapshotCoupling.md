# ReviewSnapshotCoupling — does MODEL_LOADING break snapshot tests or history row parse?

Read-only review of `tools/test-snapshot.sh` and `tools/kama-probe.sh` `cmd_snapshot` /
`diff_baseline`, against the landed C1 edit.

**State reviewed** (working tree, mid-wave): `tools/kama-probe.sh` sha256
`d0d48d8d6a5d96553adb773ae7f75d4d0f47e19be6b2d7d8a1c9b7a83f6db8fe`,
`tools/test-snapshot.sh` sha256 `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646`.
Both files changed under me during this review (the whitelist was absent on my first read and
present on the second; the new snapshot case appeared later). Line numbers below are current as
of that read. I ran no lane gate, harness, matrix or snapshot — L1 owns measurement. The only
command touching the artifacts was `bash -n tools/test-snapshot.sh` (syntax parse, `syntax-ok`).

## Answer

**No existing test breaks, and no existing history row needs reinterpretation.** The single
history-parse coupling is `diff_baseline`'s hand-written verdict whitelist; it is now extended, so
a persisted `MODEL_LOADING` row round-trips. The residual risk is not behavioural, it is
structural: that whitelist is a second copy of the vocabulary with nothing tying it to `VOCAB`.

## A. Existing tests in `tools/test-snapshot.sh`: unaffected

1. The new branch is 503-gated: `if [ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then`
   (`tools/kama-probe.sh:501`). The fixture never emits 503 — `/v1/models` is `self.send_response(200)`
   (`tools/test-snapshot.sh:53`), every other path is `self.send_response(404)` (`:59`) — so every
   fixture classification is byte-identical to before.
2. The exact-shape assertions pin keys, not the vocabulary: `assert doc["summary"] == {...}`
   (`tools/test-snapshot.sh:107`) and `assert set(row) == {"id", "consumer_path", ...}`
   (`:111`). Neither mentions a verdict token list.
3. The pinned baseline row is unchanged: `EXPECTED_ROW=$(printf 'fixture-a\tMODEL_OK\tmatched\tfixture-model\t%s\tyes' ...)`
   (`:117`). The stable-rerun assertions `transitions=0 exit=0` (`:128`), DELTA byte-stability
   (`:131`) and latest.tsv byte-stability (`:132`) still hold because the sampled state is
   `MODEL_OK` both runs.
4. `verdict_vocabulary` is emitted from `$VOCAB` in every JSON payload but never asserted here;
   the only document comparison is `assert stdout_doc == doc` (`:104`), i.e. file vs stdout of the
   same run.
5. The malformed-anchor case still passes: `printf 'garbage garbage garbage\n' > "$HIST/latest.tsv"`
   (`:151`) has an empty verdict field, which matches no alternative in the closed whitelist. The
   whitelist was extended, not wildcarded, so `:155-158` (`malformed-row-dropped`, no phantom
   `row-absent`) keeps its meaning.
6. Nothing else in the repo parses probe stdout: a grep of `.ufo` for `probed=|not_http|verdict_vocabulary`
   matches only `.ufo/waves/round-16/frozen/kama-probe-before.sh`. `tests/ollama-*` target
   `tools/kama-ollama-evidence.py`, not this probe.

## B. History row parse: the one gate that matters, now correct

- Writer persists the verdict verbatim, with no validation on write:
  `printf '%s\t%s\t%s\t%s\t%s\t%s\n' "${EV_IDS[i]}" "${EV_VERDICT[i]}" ...` (`tools/kama-probe.sh:1090-1092`),
  header `#@snapshot_id ...` (`:1086`), gated only by "something changed" (`:1085`).
- Reader trusts only the literal set: `*\ MODEL_OK\ *|...|*\ NOT_HTTP\ *|*\ MODEL_LOADING\ *`
  (`tools/kama-probe.sh:937`).
- **If that token were missing** (the state I first observed), the failure is not cosmetic:
  1. row dropped — `warn "latest.tsv: dropping malformed baseline row for id='$id'"` (`:940`);
  2. DELTA gains a `baseline-note malformed-row-dropped` line (`:941`) — exit code still comes from
     `eval_rows`, not from this path (`:846`, `:862`);
  3. the same run then re-adds it as `row-added verdict=MODEL_LOADING ...` (`:962`) because it is
     no longer in `PV_V`, so N_TRANS increments and the row count churns every run;
  4. latest.tsv is rewritten with a fresh `#@snapshot_id` (`:1085-1093`) — tracked file churn
     (`registry/history/.gitignore`: "the normalized baseline and ledger are tracked");
  5. if the loading row is the *only* baseline row, `PV_V` empties and the rebaseline branch
     re-records `baseline recorded (N rows)` every run (`:955`) while `N_TRANS` stays 0 — i.e. the
     run reports `transitions=0` and still mutates DELTA.md, directly contradicting
     `tools/test-snapshot.sh:132` ("unchanged snapshot leaves latest.tsv byte-stable") and
     `corpus/knowledge/snapshot-history.md:34` ("byte-stable").
  Operational weight: a real llama.cpp cold start spans more than one snapshot interval, so this is
  the steady state for the whole warmup, not a corner case.
- With the token present, an unchanged loading baseline yields `DELTA_LINES=()` and writes nothing
  (`:1078`, `:1085`) — the invariant is restored.
- No migration: the old classifier cannot emit `MODEL_LOADING`, so no existing `latest.tsv` row
  (all three are `DEAD` / `connection-refused`) needs reinterpretation, and DELTA rows are never
  re-read.

## C. DELTA.md format: unchanged

Transition lines are formatted as `- $ts $rid ${fields[k]} ${vals_old} -> ${vals_new}`
(`tools/kama-probe.sh:963-975` area; field list `local fields=(verdict reason served_model port file_match)`
at `:966`). `MODEL_LOADING` is a *value*, not a field, so no line shape changes; row-absent prints
`(was verdict=$(persist_clean "${PV_V[$rid]}") port=...)` (`:982`), which remains readable as
`was verdict=MODEL_LOADING`. Nothing programmatically parses DELTA.md (same grep as A.6).

## D. Tracked state and the matrix path

- `snapshot` into the default history would dirty the tracked `registry/history/latest.tsv` /
  `DELTA.md` during a loading window and would falsify `PROVINCE.md:19` ("every row in
  `registry/history/latest.tsv` is `DEAD` connection-refused").
- The C1 matrix cannot do this: `snapshot --port` is refused before any classification —
  `die "snapshot refuses --port: a matrix probe has no registry baseline to persist"` (`:163`).
  C2's live harness must therefore use `check --port` (or `listeners`) only; any `snapshot` call
  there would be a scope violation, not just a nuisance. [INFERENCE on C2's intended invocation:
  the contract says "runs kama-probe against it"; `--port` is the only mode that cannot persist.]

## E. `listeners` summary: new key, no consumer breaks

Counter arm `MODEL_LOADING) n_loading=$((n_loading+1))` (`tools/kama-probe.sh:731`), JSON summary
gains `"model_loading": %s` (`:742`), text line gains `model_loading=%s` (`:746-747`). The
`probed == sum(parts)` invariant is preserved and both surfaces agree. No test pins the listeners
summary — `SKILL.md:305` explicitly claims none ("No isolated listener-census self-test claimed"),
and `SKILL.md:209` documents only the `check` schema keys. No hit outside the frozen probe.

## F. Exit contract: unchanged, so the stub matrix stays unambiguous

Both gates key on `MODEL_OK` only: `if [ "$C_VERDICT" = "MODEL_OK" ]; then EV_OK=1; ... else EV_DRIFT=1`
(`:846`) and `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi` (`:862`). `MODEL_LOADING` is
therefore drift / exit 2, matching the shared matrix schema ("exit 0 iff MODEL_OK else 2"). It adds
a verdict but no new exit class.

## G. Prose contracts that the edit makes false (no automated test catches these)

These are existing, reader-facing contracts and each currently asserts a six-verdict vocabulary:

- `SKILL.md:11-13` — "Verdict vocabulary is shared with `tools/kama-probe.sh`: `MODEL_OK` | … `NOT_HTTP`."
- `corpus/knowledge/endpoint-identity.md:3` — "The verdict vocabulary is fixed: `MODEL_OK`, … and `NOT_HTTP`."
- `corpus/knowledge/consumer-registry.md:84-85` — "The **live verdict** column uses the binding vocabulary: `MODEL_OK` | … `NOT_HTTP`."
- `registry/endpoint-consumers.tsv:31-32` — "MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP".
- `corpus/knowledge/snapshot-history.md:66` — "`bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0`" plus
  its enumerated case list; the landed case adds checks, so the recorded count and the case list
  become historical. L1's run is the authority for the new total. `:28`/`:34` describe the columns
  and byte-stability and stay accurate only in the fixed state.
- `PROVINCE.md:19` is conditional on D and stays true of the untouched tracked file.

Advisory, not a test break: if the docs/skill items do not land these updates, the lane ships a
tool and a corpus that disagree about the vocabulary.

## H. The landed snapshot test case: traced, sound (no defect found)

`tools/test-snapshot.sh:162-184` seeds `fixture-a MODEL_LOADING` plus `fixture-z MODEL_LOADED` and
runs `snapshot` with the dead fixture still registered as `fixture-b`. Trace: `fixture-z`'s
`MODEL_LOADED` matches no whitelist alternative (the pattern requires a trailing space after the
token, so it cannot prefix-match `MODEL_LOADING`); it is dropped with the warning and the
`baseline-note` the case asserts. `fixture-a` survives into `PV_V`, so the row-absent line
`(was verdict=MODEL_LOADING ...)` at `:982` is emitted, and the negatives at `:171-183` would catch
any silent drop. `fixture-b` is `DEAD`, so exit 2 is the honest `eval_rows` result, not an artifact
of N_TRANS. The case is correctly placed *after* the malformed-baseline case and *before* the
`--port`/symlink cases, so it does not disturb the `snap2` byte-stability pair or the `snap3`/`snap4`
transitions that diff against the earlier baseline. Good coverage choice: `MODEL_LOADED` is exactly
the near-miss a prefix wildcard would wrongly accept.

## I. Residual risk (main finding)

**The whitelist (`tools/kama-probe.sh:937`) and `VOCAB` (`:60`) are independent literals.**
`VOCAB` feeds only JSON/text emission; the history reader repeats the enum by hand. Nothing asserts
they agree, and the whitelist has no shared source of truth. Consequence: the next verdict added to
`VOCAB` alone silently re-enters the churn loop of B — history rows written by the new probe are
discarded by the next run, DELTA grows, and the tracked baseline dirties — with no failing test
until someone adds another explicit case. The landed test closes the regression for `MODEL_LOADING`
specifically, not for the class.

Cheapest durable fixes, L1's call (I do not edit):
1. derive the case from `VOCAB` at runtime (e.g. `case " $VOCAB " in *" ${v:-} "*) : ;;`), removing
   the second copy; or
2. keep the literal whitelist and make the test generic: seed one row per token in `$VOCAB` and one
   near-miss, so any future divergence fails `test-snapshot.sh`.

Either leaves every existing assertion in the file untouched.

## Limitations

- Static review; no probe, harness, matrix or snapshot was executed against the lane, so the
  claims above are code-path traces, not run evidence. L1's `test-snapshot.sh` run is the
  measurement.
- The probe and test files changed twice during this read; if they change again after the shas
  quoted above, re-check `MODEL_LOADING` presence at the two anchors (`:937`, `:60`) before
  relying on this report.
- No tool was installed or upgraded for this review.
