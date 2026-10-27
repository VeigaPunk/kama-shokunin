# W01LessonDraft — round-59 Gate/Mistakes fragment (draft; evidence-only)

Seat: W01LessonDraft (scribe, leaf, advisory). Axes: operability, calibration (7, lowest assigned; nudge inactive).
Frozen controls: `.ufo/waves/round-59/controls/freeze.txt` — base `8f7f58cd161f2b7dfa1709450c3ae79599c12833`, fleet-manifest-rev `c071f0dea9d00d944690534ff8461653eb94df66`, control commit `5d957d24`, `frozen-before-any-seat-result`.

This is a **draft fragment** for `corpus/lessons/round-59.md` §Gate and §Mistakes. It is not lane text and not a closure verdict: the only file this seat wrote is this report. No external S517/S518 spot-check is recorded, so **no discernment progress and no score movement are claimed**. Gate entries are labelled *candidate* deliberately; only the non-author closure converts them to admit/reject.

Seat evidence read as advisory and **not reproduced** here: the seat reports present in `.ufo/waves/round-59/w1/out/` when this seat read them (`*.md`, this file included; the wave was still writing, so no count is asserted — an earlier read saw 38 and a later one 52). Where a row below rests on a seat report, it says so.

## 1. Own receipts executed by this seat

Scratch: `/fast/scratch/hyaku/kama-r59/W01LessonDraft`, `TMPDIR` exported to it, removed before yield. No installs; no lane/fleet/shokuknow writes; no campaign counter was run by this seat.

| # | command | observed | exit |
|---|---|---|---|
| 1 | `curl -sS -m 60 -o s517.html -w 'http=%{http_code} size=%{size_download}\n' https://docs.python.org/3/library/sys.html` | `http=200 size=280618` | 0 |
| 2 | `sha256sum s517.html` | `92259a1a3a5b9cb113edf43284c85b6c4d9a76afb6ff3cb102dcdef92b85408e` | 0 |
| 3 | `curl -sS -m 60 -o ldso8.html -w … https://man7.org/linux/man-pages/man8/ld.so.8.html` | `http=200 size=41398` | 0 |
| 4 | `sha256sum` on (3) and on `.ufo/waves/round-56/sources/ld.so.8.html` | both `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83` | 0 |
| 5 | tag-strip + whitespace-normalise both files, substring-test the quotes | S517 quote present, 18 words; S518 quote present, 6 words; rendered S518 text has `secure-execution` ×11 | 0 |
| 6 | `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` | `0f99f606120d0c884656c6e7a290f0e8f33c2181` | 0 |
| 7 | `git -C …/kama-shokunin rev-parse HEAD` | `4a541190b6d494a4e99116249632e99aab80adcc` | 0 |
| 8 | python count of `^\| <id> \|` rows in `corpus/SOURCES.md` | S200 0, S202 0, S206 1, S210 0, S211 0, S224 0, S230 0, S329 1, S512 1, S513 1, S517 1, S518 1 | 0 |
| 9 | python parse of fleet `MANIFEST.json` kama closure rows | 48 kama closures; last four 54 `rejected-honest-stop`, 55 `admitted`, 56 `rejected-honest-stop`, 57 `rejected-honest-stop`; `r58 False` | 0 |
| 10 | `git -C lane log --oneline 494c1657..HEAD -- tools/round59-c1-counter.py tools/round59-c2-counter.py tests/round59-battery-variants tests/round58-battery-variants` | empty (frozen counter/variants unchanged after introduction) | 0 |
| 11 | `git show --stat` on `5d957d24 494c1657 2c7443ab aca8d006 114fdf78 4a541190` | post-result checker edits: see N9 in §3 | 0 |
| 12 | `awk` recipe over `shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` (read-only) | the 7 rows of `.ufo/waves/round-59/quarantine-slice.txt`, same order, all `payload-absent` | 0 |
| 13 | python counts of `secure-execution` / `LA_SER_SECURE` in committed snapshots | `round-56/sources/ld.so.8.html`: 11 / 0; `round-56/sources/rtld-audit.7.html`: 0 / 3 | 0 |
| 14 | `test -e corpus/lessons/round-59.md` | absent | 1 |
| 15 | `find .ufo -iname '*sys*.html'` | 0 files — no committed S517 byte snapshot | 0 |

Read but not re-executed: `controls/{c1-candidate,c1-candidate-final,c1-oldchecker,c1-oldchecker-final,c2-base,c2-after,c2-after-current-head}.{out,exit}`, `census/start.out`, `variant-count.out` (`variants=5`), `SCORECARD.md` §Axes calibration row, `corpus/SOURCES.md` rows S206/S329/S512/S513/S517/S518, `corpus/lessons/round-34.md`, `round-36.md`, `round-58.md`.

## 2. §Gate — draft

### 2.1 Admit candidates

**S517 — ADMIT CANDIDATE (tier A, mined; already a registry row, `corpus/SOURCES.md:270`).**
URL https://docs.python.org/3/library/sys.html#sys.setprofile — accessed 2026-10-27 by this seat (HTTP 200, 280,618 bytes, sha256 `92259a1a…b85408e`); page title "sys — System-specific parameters and functions — Python 3.15.2 documentation"; footer "Last updated on Oct 27, 2026 (16:42 UTC)." Located quote, **18 words**: “only on call and return, but the return event is reported even when an exception has been set”. Scope: profile call/return events only — it does **not** establish per-line execution, consumption of a returned value, or an outcome for an external operation (S01S517 and K11SourceClaim read the same boundary). Provenance gap: no committed S517 byte snapshot exists (receipt 15); the quote and date are committed only in `corpus/SOURCES.md:270` and the round-58 lesson.

**S518 — ADMIT CANDIDATE (tier A, mined; `corpus/SOURCES.md:271`, supersedes S513 for the expanded scope).**
URL https://man7.org/linux/man-pages/man8/ld.so.8.html — accessed 2026-10-27 by this seat (HTTP 200, 41,398 bytes, sha256 `d9b7737e…f0379f83`, **byte-identical to the committed round-56 snapshot**, receipt 4); colophon "man-pages 6.19", "2026-08-03". Located quote, **6 words**: “LD_AUDIT is ignored in secure-execution mode.” Corroboration for the S513 overturn: the committed S512 snapshot `rtld-audit.7.html` contains `secure-execution` **0** times and the only secure token is `LA_SER_SECURE` (3), so S513's overlap reason was false for exactly the topic its flip condition named.

### 2.2 Reject candidates — source

**S513 — REJECT retained (claim-scoped; `corpus/SOURCES.md:266`, status `rejected`).** Rejected because the broad ld.so(8) manual overlapped S512 (`rtld-audit(7)`) for the narrow LD_AUDIT-name predicate; S518 supersedes that disposition only for the secure-execution/token subject and does not rehabilitate S513 for the name-only claim (S02S518, S03S513 agree). Flip condition as recorded: a future claim about secure-execution, dynamic string tokens or loader namespace semantics.

No other source row is proposed for rejection this round. The quarantine slice below is the second reject family.

### 2.3 Reject candidates — quarantine slice (`payload-absent`, register read-only)

The slice at `.ufo/waves/round-59/quarantine-slice.txt` re-derives byte-for-byte from the campaign register with the recorded `awk` recipe (receipt 12). Six ids are **not** registry rows (receipt 8); S206 is one (see 2.4). Prior hand-check verdicts: `corpus/lessons/round-36.md:47-57` (2026-10-24, L1 direct fetch; wave-2 seats re-opened five ids). Round-59 re-open: seat `S05Quarantine.md` (2026-10-27; no per-URL dates stated; verdicts agree with round 36).

| id | candidate verdict | URL | accessed | located quote (≤25 words) / finding |
|---|---|---|---|---|
| S200 | **REJECT candidate — absent as quoted** | https://arxiv.org/abs/2312.07104 | 2026-10-24; re-opened r59 | none locatable: the cell `DOI not in Semantic Scholar` does not occur; it is a status fragment, not a page sentence |
| S210 | **REJECT candidate — absent as quoted** | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide | 2026-10-24; re-opened r59 | cell `Page Not Found` absent; page carries `python3 -m sglang.launch_server` (5 words) |
| S211 | **REJECT candidate — absent as quoted** | https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-推理引擎.md | 2026-10-24; re-opened r59 | the claimed token `still-live` occurs nowhere in the page text read (chapter is reachable; the token is not) |
| S224 | **REJECT candidate — compound quote not located** | https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ | 2026-10-24; re-opened r59 | claimed span `render-only servers always return 200` (5 words) absent; page carries `check_health()` and 503 on `EngineDeadError` |

Hold / non-candidate rows, recorded so the reject list is not inflated:

- **S202 — HOLD (present, not appended).** https://docs.docker.com/reference/compose-file/services/ — quote, **18 words**: “service_healthy : Specifies that a dependency is expected to be "healthy" (as indicated by healthcheck ) before starting”. Not appended: no admitted entry cites it. Flip: an admitted entry cites it.
- **S206 — NOT a candidate; already a registry row.** `corpus/SOURCES.md:209`, status `mined`, opened 2026-10-24, used-by `corpus/knowledge/serving-alias-contract.md`; the anchored quote is the Chinese span `对于vLLM/SGLang，可通过模型列表接口 <EAS_ENDPOINT>/v1/models 获取。` (3 whitespace tokens; `v1/models` appears 4 times on the page per the round-34 record). See mistake N12.
- **S230 — HOLD (present; duplicate of lane row S329).** https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py — sentence, **16 words**: “Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead.” S329 holds the same URL (status `mined`, used-by `corpus/knowledge/sglang-native-route-deprecation.md`), so a second row would duplicate the URL.

### 2.4 Pending for the non-author spot-check

- Admit candidates: **S517**, **S518** (re-open the page, locate the quote; for S518 also confirm the S512 snapshot lacks `secure-execution`).
- Reject candidates: **S513** (claim-scoped retain), **S200**, **S210**, **S211**, **S224**.
- Status: **not recorded**. `corpus/lessons/round-59.md` does not exist (receipt 14); the highest lane spotcheck is round 57 per the committed receipt `c2-after-current-head.out` (`maxN=57`, `rows=44`); no kama r58 closure exists in the fleet MANIFEST (receipt 9). `corpus/lessons/round-58.md` §Gate's "Spot-check set" is a proposal, not a verdict (K13AdmitRejectReview reached the same reading). Until an independent record exists, this Gate satisfies the *shape* of "at least one admit and one reject" only as a candidate set — not as a sampled outcome.

Merge note: if merged, place this in §Gate after the round-58 Gate, and keep the words *candidate* / *pending*. Do not relabel to ADMIT/REJECT without the outside record.

## 3. §Mistakes — draft (pointer and fix)

New this round (N), then carried-forward known rows (C) with their round-59 status.

| # | class | evidence pointer | captured by | fix |
|---|---|---|---|---|
| N1 | synthetic-observation-as-execution | `tools/round59-battery-outcome-check.py:30-34` (`result_for` docstring: "return its synthetic observed state"), `:59-76` (`fake_run`; `rc = 0 if expected == observed else 1`). Verified by this seat's read of the code. | K02PredicateParity, R14CandidateScope | Replace the synthetic observation with the child's parsed `ld_audit` stdout and real exit; keep counter/fixtures frozen; re-measure at the hardened tip. Not applied. |
| N2 | label-cardinality-unbound | `tools/round59-battery-outcome-check.py:186` (`len(frames) == len(expected_labels)`); mutant `names_ok=True` survived: M04DropLabelSet (mutant sha256 `279a3e3d…c121e2`), R16CheckerTamper. Reported, not reproduced here. | M04DropLabelSet, R16CheckerTamper | Add a fixture with an extra duplicate frame carrying an existing label, enumerated before data. |
| N3 | faulted-leg-return-unbound | `:197` (`and not returns_ok.get(fault, False)`); removing it still reports `met=True` exit 0 (R16). Contrast M02DropFaultPropagation: removing `outcome.get("exit") == 1` at `:196` gives `noop_rejected=14/16 met=False` (killed). Reported, not reproduced here. | R16CheckerTamper, M02DropFaultPropagation | Add a fixture whose fault leg returns `True` while the run exits 1, enumerated before data. |
| N4 | battery-input-not-substitutable | `tools/round59-c1-counter.py:76-85` reads battery and every fixture from `git show <tip>:<path>`; `--checker` is the only override (`:49-50`). Battery mutations (always-`True` mutant assert, removed `--expect` value, always-zero exit map) were therefore **unscored** by R03/R09/R11. | R03MutationAssert, R09NoExpect, R11MainExit | Coverage limit of the frozen counter; if wanted, a battery-override control is added before data in a later round, never after. |
| N5 | executable-path-unbound | `:191` checks `len(calls) == 1` plus flag presence only; N16 is rejected for its second call, not for the `other-script` route. A single-call `python3 other-script --counter …` is a source-grounded **inference**, not a measured result (R05). | R05OtherScript | Bind the declared runner path (argv[0]/script identity) or enumerate a single-call other-script control before data. |
| N6 | c2-shortcut-spellings-meet | `tools/round59-c2-counter.py:60-61`: `typed_count` matches only `N (outside closures on record`; `pinned_fleet_revision` matches only a 40-hex word. X09 built four fixtures — `44 verifier-spotcheck files`, `spotchecks=44`, `fleet c071f0de`, `fleet sha256 d9b7737e…f0379f83` — each `mismatches=0 met=True` exit 0. Reported, not reproduced here. | X09C2ReplayAfter §5 | Normalise the count and pin detection (word/`=` forms, any 8–64 hex in fleet context) or freeze such controls pre-data. As written, the kill rule's "any shortcut control meets" is triggered. |
| N7 | c2-counter-self-mutation-uncontrolled | M12C2Clauses forced each of the 8 `mismatches` values to `0` in a scratch counter copy: every probe `met=True` exit 0. Contrast X09 §4 row-edit controls: each of 7 fields alone produced exactly one mismatch, exit 1. Reported, not reproduced here. | M12C2Clauses, X09C2ReplayAfter | No counter-mutation control exists in the frozen set; add one before data in a later round. |
| N8 | c2-spotcheck-record-unenforced-and-unrecorded | `freeze.txt:13` requires "preserving a real outside admit/reject spot-check record for S517 and S518"; the counter never reads spot-check content (path shape + round + MANIFEST token only; X09 §6). No outside record exists: freeze context, S04CurrentClosure, K08ManifestAbsence, K12NoTrade, K13AdmitRejectReview. | X09C2ReplayAfter, K12NoTrade, K13AdmitRejectReview | Obtain and record the outside spot-check; report calibration unmet on this clause; do not narrow the predicate. |
| N9 | post-result-tool-edit (disclosed) | `controls/c1-candidate.out` records tip `494c1657…` and `met=False`; the tool under test was then edited at `2c7443ab` (checker + receipts) and `aca8d006` (checker only), and the measured tip is `aca8d006` (`c1-candidate-final.out`). Counter and variants unchanged after `494c1657` (receipt 10, empty). | this seat's commit-stat read | Disclose; the measured tip carries the hardened checker (round-58 precedent). No counter/fixture edit. |
| N10 | population-label-drift | Checker prints `runs=5 passed=5/5` (baseline + four one-leg fault runs) while the frozen predicate says "genuine leg coverage=3/3"; the counter summary `genuine=1/1 benign=3/3 noop_rejected=16/16` is a third population (20 fixtures). | K02PredicateParity | Label the three populations explicitly in the lesson text; do not let one stand for another. |
| N11 | s517-open-receipt-absent-at-read-time | K11SourceClaim found no round-59 S517 opening artifact and `corpus/lessons/round-59.md` absent when it read the tree; "S517 opened this round" was then unsupported. This draft supplies a receipt (URL, 2026-10-27, sha256 `92259a1a…`). | K11SourceClaim; this seat | Record the fetch receipt (URL, date, digest) with the Gate entry; do not assert an opening that has no receipt. |
| N12 | seat-report-wording | `S05Quarantine.md` says of S206 "no admitted entry cites it in this assignment"; `corpus/SOURCES.md:209` is a `mined` S206 row used by `corpus/knowledge/serving-alias-contract.md` (receipt 8). The seat's operative verdict ("present; do not append") is still correct because the row already exists. | this seat's row read | Cite a row's own status and used-by instead of "no admitted entry cites". |
| C1 | stale-count-recurrence — **fixed in the Axes row this round** | Round-58 lesson Mistakes row; round-58 reported the typed `44` as still stale. At `494c1657` the `## Axes` calibration row lost the typed `44 (outside closures on record…` and the pinned `941acf70…` and gained the derivation command (`git show 494c1657 -- SCORECARD.md`; `c2-base.out` `typed_count=1 pinned_fleet_revision=1` → `c2-after-current-head.out` both `0`). Residual, measured: the string and the pin still occur elsewhere in historical SCORECARD text (phrase at line 2676; pin in the two round-58 C2 claim rows), outside the row the counter reads. | round-58 lesson; this seat's diff read | Nothing to fix in the frozen row semantics; do not let a historical-section string stand for the row. The row still spells other typed numbers (e.g. `204 rows` verdict-ledger) the predicate does not cover. |
| C2 | counter-controls-blind-to-mutants / unlisted-noop-survivors — **partly fixed** | Round-58 lesson rows. Round 59 added `tests/round59-battery-variants/{N12…N16}` pre-data (5 files at `494c1657`; `variant-count.out` `variants=5`), all rejected at `aca8d006` (`c1-candidate-final.out`). Survivors remain: N2, N3, N5 above. | round-58 lesson; receipts | Enumerate the survivors before data; keep the frozen sets unchanged this round. |
| C3 | wrong-doc-version — **disclosed** | Round-58 lesson: S517 anchor said "Python 3.14 docs" vs page title "Python 3.15.2 documentation". Round-59 fetch confirms title and date; no committed S517 byte snapshot exists (receipt 15). | round-58 Gate re-read | Keep the corrected anchor; the remaining gap is provenance (quote+date only) — commit a snapshot such as S518's. |
| C4 | misroot-and-stray-writes — **mitigated, not removed** | Round-58 lesson. `tools/round56-env-leg-battery.py:10-14` still hard-codes the absolute lane paths (`LANE`, `OUT`); the round-59 harness neutralises the writes: `tools/round59-battery-outcome-check.py:97-100` maps `Path.write_text`/`write_bytes`/`mkdir` and `tempfile.TemporaryDirectory` to virtual storage, and blocks `Popen`/`os.system`. | round-58 lesson; this seat's code read | Keep the interception; a battery run outside the harness still writes the lane (the round-58 `o.bin`/receipt-rewrite class). |
| C5 | harness-confinement — **unchanged** | Round-58 lesson: the audit hook is in-process, not a sandbox; reads are not confined. No round-59 seat probed this class (X06 used per-variant fixture trees, `git -C "$D"` toplevel asserted). | round-58 lesson | Re-test with an escape probe in a later round; do not represent the harness as a sandbox. |

## 4. Conflicts to report verbatim (for the canonical judge)

1. **Fleet HEAD.** Assignment: "Current fleet HEAD is /home/vgpnk/Projects/shokunin at 3f3dd97345ef1aedfdaec818c9e58675d4f41e3f". Observed now (`git -C /home/vgpnk/Projects/shokunin rev-parse HEAD`, receipt 6): `0f99f606120d0c884656c6e7a290f0e8f33c2181`. The committed receipt `controls/c2-after-current-head.out` prints `fleet=3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`. Seats S04CurrentClosure, K08ManifestAbsence, R12AssertionSemantics and K06C2ReferenceDrift also read `0f99f606…`; X08/X09 replayed the counter against `c071f0de`, `58cffd1f`, `3f3dd973`, `0ffe9271` and live `HEAD` — every one `mismatches=0 met=True`, because the r57 verdict token is unchanged. This seat did not run the counter, so it records the divergence only.
2. **C1 measured tip.** `controls/c1-candidate.out`: `tip=494c165759a644a56ec81bb51a7837b028817d89` … `genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False` (exit 1). `controls/c1-candidate-final.out`: `tip=aca8d0067ea25627c5015c2193c843965148bc8e` … `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` (exit 0). K14FrozenTarget reads the first as a wrong-tip conflict; the second postdates two checker edits (N9).
3. **C2 `met=True` vs the frozen sentence.** `c2-after-current-head.out` reports `mismatches=0 met=True` (exit 0) at `maxN=57 manifest=rejected-honest-stop`; the frozen sentence additionally requires "a real outside admit/reject spot-check record for S517 and S518", which is unrecorded. K12NoTrade states the pass "establishes agreement with the latest existing closure, not the required current external discernment/spot-check progress". Both the artifact text and the seat text are recorded; the judgment is not this seat's.

## 5. What this fragment does not establish

- No outside verification of S517, S518 or S513; no admit/reject outcome is sampled. Gate entries are candidates.
- No counter was executed by this seat; every numeric counter claim above is either a committed receipt I read or a seat report I name.
- The wave is advisory (64 dispatched leaves; seat reports were still arriving while this seat read them, so no count is asserted); seat consensus is not evidence (freeze line 17).
- Steady-state unknowns: actual glibc secure-execution behaviour was not tested; S517's page may change without a committed snapshot to diff against.
