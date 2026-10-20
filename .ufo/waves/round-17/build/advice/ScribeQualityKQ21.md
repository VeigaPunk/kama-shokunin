VERDICT: n/a — drafted the KQ21 QUALITY.md row (live-run checks admitted only when a subject-behaviour control flips them); nothing was measured or executed.

# Behaviour

Owned draft written: `.ufo/waves/round-17/build/drafts/quality-kq21.md`. It contains an integration-notes block (to delete before append), the round-17 criteria heading, the KQ21 table row in the existing `ID | Admit | Reject | Motivating lesson` format, and an unknowns block. No lane document was edited. Nothing was run: no gate, no measurement, no llama-server, no fake server, no port bound (8080/34113 untouched).

# Gates

None run (scribe seat; L1 owns measurement). Template check only: the row has four pipe-delimited cells, and the existing QUALITY.md rows use the same columns (`corpus/QUALITY.md:7-8`).

# Touched surfaces

- Written: `.ufo/waves/round-17/build/drafts/quality-kq21.md`, `.ufo/waves/round-17/build/advice/ScribeQualityKQ21.md`.
- Read only: `corpus/QUALITY.md`, `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md`, `.ufo/waves/round-16/falsify/advice/ReviewQualityKq19.md`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`, `corpus/lessons/round-16-verifier-spotcheck.md`.
- Not touched: frozen copies, old receipts, `corpus/QUALITY.md` (no edit), `SOURCES.md`, `MANIFEST.json`, `.ufo/state/`, any sibling lane.

# Findings

1. **Gap in the existing bar.** KQ19 (`corpus/QUALITY.md:109`) grades a probe verdict with a frozen-fail/repaired-pass matrix. No row grades live-run receipt checks the same way. The round-16 review found the live harness lacks that property: `ReviewLiveHarnessCode.md:57-59` says `teardown_exited` and `model_unchanged` "cannot fail for any behavior of the subject." KQ21 closes that gap with a control requirement.
2. **Admission rule.** A live check counts as subject evidence only if a recorded subject-behaviour control makes that same check fail. Each check carries one label: `subject`, `input-integrity`, or `harness-integrity`. Observation-only captures cannot support PASS/VALID. Internal faults must still emit a receipt, shown by an injected-fault control.
3. **Evidence the rule would have caught.** Round-16 `ReviewLiveHarnessCode.md` demonstrated each failure mode the row rejects: a `/health` 200 `{"status":"degraded"}` passing (`:95-102`, M1); self-exit rc 0 passing `teardown_exited` (`:28`, H2); SIGKILL rc -9 passing (`:33`); `loading_envelope_exact` captured but unread (`:68-71`, H1); a teardown exception escaping with no receipt (`:34`, M4).
4. **Gate gap (not fixed here).** `tests/llamacpp-live/check-receipt.py:53-63` `REQUIRED_CHECKS` has ten IDs and no label concept. Grep for `input-integrity` / `harness-integrity` in both `check-receipt.py` and `tools/kama-llamacpp-live.py` returned zero matches. Labels are prose until L1 decides the schema.
5. **ID collision risk.** No `KQ20`/`KQ21` exists in `corpus/`, `tools/`, `tests/`, `registry/` at access. A sibling seat (`ScribeQualityKQ20-2`) is drafting KQ20; L1 must sequence KQ20 before KQ21.

# Sources opened (all accessed 2026-10-20; local paths, no URLs)

- `corpus/QUALITY.md:5` — "new rows; supersession names the old criterion instead of erasing it." (append rule)
- `corpus/QUALITY.md:7-8` — table header `| ID | Admit only when | Reject or limit when | Motivating lesson |` (column shape)
- `corpus/QUALITY.md:17` — "Author and parent-dispatched advisor agreement are not an outside spot-check." (review boundary; KQ21 remains author-appended)
- `corpus/QUALITY.md:109` — KQ19 row; quoted: "the set of changed verdicts equals the expected-loading set" (precedent)
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:33` — "`returncode -9`, `sigkill_sent true`, 10.1 s; `teardown_exited` passed" (kill control)
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:34` — "`ESCAPED KeyError KeyError('returncode')`, `receipt_written False`" (fault row)
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:57-59` — "cannot fail for any behavior of the subject" (direct answer)
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:68-71` — H1 heading and "the 10 `_check(...)` calls at 938-1039 never read it." (loading envelope)
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:118-122` — M4 heading, teardown escape (cross-checked with `:34`)
- `.ufo/waves/round-16/falsify/advice/ReviewQualityKq19.md:40` — "a probe claiming a served model on a loading row passes" (precedent of an ungraded field)
- `.ufo/waves/round-16/falsify/advice/ReviewQualityKq19.md:48-50` — "it can only fail if the probe contradicts itself" (drift as self-consistency; precedent for labelling not counting)
- `tools/kama-llamacpp-live.py:108` — DOC: "the spawned process group must terminate on" (teardown_exited's claim)
- `tools/kama-llamacpp-live.py:922` — `receipt['loading_envelope_exact'] = loading_envelope_exact(loading_503)` (captured, not graded)
- `tools/kama-llamacpp-live.py:938` — `checks.append(_check('health_ready', health_status == 200,` (status-only check)
- `tools/kama-llamacpp-live.py:1021` — `receipt['teardown'] = {'error': f'{type(exc).__name__}: {exc}'}` (teardown exception path)
- `tools/kama-llamacpp-live.py:1026` — `receipt['teardown']['returncode'] is not None,` (teardown_exited expression)
- `tests/llamacpp-live/check-receipt.py:53-63` — `REQUIRED_CHECKS = (` ten IDs, no label field
- `corpus/lessons/round-16-verifier-spotcheck.md:187` — "Live checks `health_ready`, `teardown_*` and `loading_envelope_exact` are weak or ungraded." (routed defect 6)

# Out of scope items

- C2 predicates, receipt `v2` schema, and the controls suite: L1 and the C2 seats.
- llama.cpp source (`/health` handler, signal path) and Python `Popen.returncode` docs: not opened here; the KQ21 draft quotes no llama.cpp or Python source.
- KQ20 content: sibling seat.

# Limitations

- Nothing executed; the citations are read-only checks of text at the stated lines. Line numbers were re-verified by grep on 2026-10-20 before writing.
- The `ReviewLiveHarnessCode.md` findings were not re-run against the current harness; the draft cites them as the round-16 review's findings. [INFERENCE] the harness may have changed since `b8e485c`; the review itself notes concurrent edits.
- The row's control definition admits a fake server as a subject-behaviour fixture. Whether a real llama-server build should be required is L1's call; the draft flags it.
- The draft requires `subject` checks to be flipped by a control that the round's counting command actually runs. That command's existence is C2's responsibility and is not verified here.

# Installs

None. No pacman, uv, npx, cargo or npm transaction was run.
