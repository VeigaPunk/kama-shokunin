# Round 100 — the correction of the round-99 records, and a `/props` body read only on HTTP 200

Lane `kama`, round 100, L1 `KamaR100`. Base `6776c667372a0da8635ebfbda6cbc92d8fb17304` (round 99 closed
`admitted`; C1/C2/C3 verified at `00394f3b`, `corpus/lessons/round-99-verifier-spotcheck.md`). Measured commit M
`2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6` (the freeze). Claims, as filed after `plans/round-100-amendment-1.md`:
C1 calibration (nine enumerated checks over the round-100 correction of the round-99 records), C2 depth (nine
loopback answers to the probe's `/props` read grade as listed; six router-shaped non-200 answers no longer read as
explicit autoload states). The Gate and Mistakes drafts are the scribe seat SB01Lesson's
(`.ufo/waves/round-100/w1/out/SB01Lesson/round-100-lesson-draft.md`), integrated by the L1; M5 and M6 are the L1's.

## Gate

Every row below was re-opened this round with `curl` on 2026-11-08 (all HTTP 200); the digests are
byte-identical to the freeze-time receipts in `.ufo/waves/round-100/sources/`.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S629 llama.cpp `tools/server/server-http.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.cpp — 2026-11-08, sha256 `aad15b757323f36b81235182c4a0a35d448399012ae3ef4fed9902b716fa17ea` (39 157 B), HTTP 200 | `res.status = 401;` (line 291) and `{"message", "Invalid API Key"},` (line 295); `res.status = 503;` (line 315) and `{"message", "Loading model"},` (line 319) | The two refusals the router can answer *before* the handler — a bad API key and a not-ready server — are 401 and 503, each with an error document. A `/props` answer under either status is a refusal, never the router's configuration. |
| S630 llama.cpp `tools/server/server-common.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-common.cpp — 2026-11-08, sha256 `b686729ed7d098e2f0c3da1ba28325d0e6d30721dab09f71cb9b53f342710ddb` (79 532 B), HTTP 200 | `json format_error_response(const std::string & message, const enum error_type type) {` (line 93) then `int code = 500;` (line 95); cases 400/401/403/404/500/501/503 | Every handler error carries a non-200 status with an error document (`code` is initialised to 500 and every case overwrites it). No error path can answer 200, so "read the body only on 200" is the only rule that keeps an error document out of the autoload answer. |
| S631 llama.cpp `tools/server/tests/unit/test_router.py` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/tests/unit/test_router.py — 2026-11-08, sha256 `fed2ff448c55422d64c4667aa40a8922e2f3fab01420ea35ccbfa875dfacd1ef` (33 103 B), HTTP 200 | `assert res.status_code == 200` (line 20) before `assert res.body["models_autoload"] is False` (line 23) | Upstream's own router test reads the autoload field only after asserting a 200. The field is read under a status the test has already pinned, which is the same order the probe now uses. This is also the path S628 missed (S628's URL was `tests/unit/test_router.py`; the file lives under `tools/server/tests/unit/`). |
| README llama.cpp `tools/server/README.md` @ b12177 — **as a source for "`/props` returns 200"** | **reject** (C, docs lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md — 2026-11-08, sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` (136 429 B), HTTP 200 | `GET /props`: Get server global properties. (line 930) — response format only; the only `HTTP status code 200` (line 489) is under `/health` | The README documents the `/props` **body** (lines 930–1026) and never states a status code for it: its only "HTTP status code 200" belongs to `GET /health` (line 489). It also never mentions `models_autoload` (`grep -c models_autoload` → 0). So the README is not evidence that "`/props` returns 200" — the status is not in it. This is the same rejection reason as S626 (a docs lead that names the flag/default, not the field), applied to a status rather than a field. Flip: a docs section states the status `/props` answers with. |

Registry changes: S629, S630 and S631 admitted (tier A, mined; used-by `SKILL.md`,
`corpus/knowledge/router-props-autoload.md`). **S628 → S631 (old→new):** S628 keeps `rejected` — its
cited URL `tests/unit/test_router.py` is still a 404 at b12177 (14-byte `404: Not Found`), so nothing
about S628's status changes; S631 is a **new row** at the correct path `tools/server/tests/unit/test_router.py`
(HTTP 200, 33 103 B), carrying the assertion S628 could not re-open. This is the round-99 verifier
spot-check's defect 3 (`corpus/lessons/round-99-verifier-spotcheck.md:121`) answered: re-file the test at
the path where it exists and admit it. S628's own used-by stays `—`.

Census before → after: 368 → 371 rows (`A 348→351`, `B 11`, `C 9`; `mined 328→331`, `queued 8`,
`rejected 32`); validate exit 0 at round start (`controls/census-start.out`, exit 0).

## Mistakes

**M1 — the round-100 correction bound its line pointers to a revision, but the counter that grades
"bound" only recognises one spelling of that revision, so a stale pointer can be re-introduced in
another spelling and still grade green.** Class: `vacuous` (a green counter on a narrower property than
the claim states). Evidence: `tools/round100-record-audit.py:63-66` — `BOUND_RE` matches
`` `<path>@[0-9a-f]{7,40}:<line>` ("<phrase>") `` with a **lowercase-hex** revision token, and
`ANY_PTR_RE` matches the same `[0-9a-f]{7,40}`; a token whose revision is uppercase hex, a short hash, or
a symbolic ref (`master`, `HEAD`) is matched by *neither* regex, so it is neither counted as bound nor
flagged as unbound. Captured-by: the round-100 wave (this seat's forgery matrix, below), not the
freeze-time control set. Fix: the counter's revision-token grammar must accept every revision git
resolves (`git rev-parse --verify <rev>^{commit}`), or the pointer must be normalised to the resolved
commit before matching; and the unbound scan must be widened so a pointer that resolves to *some*
revision is graded, not skipped. Shown able to fail: `.ufo/waves/round-100/w1/out/SB01Lesson/c1-pointer-grammar-matrix.out` —
G1 (uppercase 40-hex rev), G2 (6-hex short rev), G3 (symbolic `master` ref) and G4 (a `corpus/lessons/`
sub-path) all print `checks=9 mismatches=0 met=True` (exit 0) while pointing at a line that does not
exist; `.ufo/waves/round-100/w1/out/SB01Lesson/c1-twin-case-control.out` is the decisive pair: the **same** stale pointer
`SCORECARD.md@…:6431` (the exact round-99 defect) fails check 8 when written `6776c667` and grades
green when written `6776C667` — the verdict flips on the hex's case alone. The committed forgery set
(`controls/c1-forgeries.out`, F1–F7) does not reach this: every one of its forgeries uses the
lowercase-hex spelling the regex already accepts.

**M2 — the round-99 wave mix was written as "58% attack", an arithmetic wrong under either attack-role
set.** Class: `arithmetic`. Evidence: `corpus/lessons/round-99-verifier-spotcheck.md:119` ("5 attack + 1
connector = 6/12 = 50%"); the wrong figure is at `SCORECARD.md@6776c667:6500` ("58% attack"), and the
LOG twin `LOG.md@6776c667:4065` names `CN01Overlap (attack)` and is right. The derived values are 4 of 12
(33%) for the policy role set (`reviewer`, `critic`, `mutation-tester`, `labrat`: RV01Wording, RV02Counter,
CR01Records, MT01Mutants) and 6 of 12 (50%) for the ledger set (adding sentinel and connector: SN01Bounds,
CN01Overlap) — both re-derived from `.ufo/waves/round-99/w1-spec.json` by
`tools/round100-record-audit.py:88-101`. Captured-by: the round-99 non-author verifier spot-check
(defect 2), not a lane counter. Fix: the round-100 correction blocks state the two derived fractions and
no other digit percentage (checks 3–5). Shown able to fail: `controls/c1-forgeries.out` — F1 (a stray
"58%") exits 1 on check 5, and F5 (the old "7 of 12 (58%)" share in the LOG) exits 1 on checks 4 and 5.

**M3 — the round-100 positive control's expectation was guessed before the freeze, and the guess was
wrong.** Class: `expectation`. Evidence: `.ufo/waves/round-100/controls/c2-prefreeze-p2guess-base.out`
— the first draft expected P2 to read `MODEL_UNLOADED/router-model-invalid/2`; the base probe actually
answers `MODEL_OK/router-unloaded-autoload/0`, so the counter would have failed its own positive control
(the same receipt prints `MISMATCH P2-200-router-on want=MODEL_UNLOADED/router-model-invalid/2
got=MODEL_OK/router-unloaded-autoload/0`). Captured-by: the L1's pre-freeze run, before the freeze
commit — the wrong guess was corrected rather than shipped. Fix: the expectation was set from the base
probe's observed answer before the freeze (`tools/round100-props-status.py:61-64`, `P2_WANT`), and the
wrong guess is kept as a committed receipt so the correction is auditable. Shown able to fail:
`controls/c2-prefreeze-p2guess-candidate.out` prints `mismatches=1 met=False` (exit 1) on the P2 cell
alone, and `controls/c2-mutant-blanket.out` shows the same P2 cell failing when the probe refuses every
`/props` answer.

**M4 — the round-99 correction's line pointer was unbound and drifted, the round-100 correction bound it
to a revision, and the binding is only checked for one revision spelling.** Class: `citation`.
Evidence: `corpus/lessons/round-99-verifier-spotcheck.md:117` — the round-99 blocks cited
`SCORECARD.md:6431` unbound and the sentence had moved to `SCORECARD.md:6446` by the round-99 tip when
the round-100 plan block was inserted above it; the fix binds the pointer
(`SCORECARD.md@6776c667:6446` ("10 reported, 2 dead")) and grades it (checks 7–8). Captured-by: the
round-99 non-author verifier spot-check (defect 1). Fix: every pointer in both correction blocks is
written `` `<path>@<rev>:<line>` ("<phrase>") `` and re-resolved at that revision. Shown able to fail:
`controls/c1-forgeries.out` — F2 (an unbound `LOG.md:4040`) exits 1 on check 7 and F3 (a pointer one
line off) exits 1 on check 8; the M1 gap above is the residue: binding is graded only for lowercase-hex
revisions, so the *same* stale pointer in another spelling grades green.

**M5 — both round-100 claims were frozen with wording wider than their counters.** Class: `vacuous` (the
Amendment-59 class itself). Evidence: C1 — presence-only checks and substring phrases (`w1/EX02RecordForge.md`
G1/G2/G3/G9/G10/G11/G14, `w1/CR01Records.md` FA–FC, `w1/RV01WordingC1.md` N1–N7, `w1/SB01Lesson.md` M1 above);
C2 — `-L`, `000`-as-200, 204/304 admission (`w1/EX01PropsForge.md` BS-1..BS-3) and a query-reading probe
(`w1/SB01Lesson.md` §1.2) all grade green. Captured-by: the round's own wave (the pre-file ledger,
`.ufo/waves/round-100/claim-falsification.tsv`), not the freeze-time forgery set, which tested only shapes the
author already had in mind. Fix: `plans/round-100-amendment-1.md` narrows both claims to the counters' properties
before filing and lists what is not claimed; QUALITY KQ153–KQ155 make the three missing shapes (revision
spellings, behavioural universals, path identity) pre-freeze requirements. Shown able to fail: the wave receipts
above are the failing runs; the narrowed sentences name only checks the committed controls exercise
(`controls/c1-forgeries.out` F1–F7, `controls/c2-base.out`, `controls/c2-mutant-blanket.out`).

**M6 — the freeze edited `SKILL.md` without re-anchoring the `## Axes` depth row, so the lane's registered axes
reconciler went from green at base to red at M.** Class: `citation`. Evidence: `w1/CN01Overlap.md` §4c —
`python3 tools/round41-scorecard-reconcile.py --repo . --tip 2e27e6f1` → `hash_bad=1 lines_bad=1 run_bad=1
mismatches=3 met=False` (base `6776c667`: `mismatches=0`). Captured-by: the connector seat, not the freeze
controls; neither round-100 counter reads the axes table. Fix: the integration commit re-anchors the depth row
to the final `SKILL.md` bytes (sha256 `7f8eed74…`, 2536 lines, 61 headings); the reconciler is re-run at the
filing tip (`.ufo/waves/round-100/controls/axes-reconcile-tip.out`). Shown able to fail: the M receipt above.

## Routed-defect answers (round-99 spot-check §Defects)

1. Stale `SCORECARD.md:6431` pointer — answered by C1 (revision-bound pointers in both correction blocks,
   checks 7–8); residue: the grammar binds only backticked lowercase-hex spellings (M1, KQ153).
2. "58% attack" — answered by C1 (both derived fractions stated; no other digit percentage, check 5).
3. S628 wrong path — answered by S631 (new admitted row at `tools/server/tests/unit/test_router.py`); S628 keeps
   `rejected`, no status/used-by change (old→new: none). QUALITY KQ154 records the class.
4. `claims.json` `"measured": "pending"` — round 99's file is not rewritten; `.ufo/waves/round-100/r99-measured.json`
   carries the three measured lines (check 9). Round 100's own `claims.json` records its measured lines at filing.
5. Carried pre-report arms — still red as disclosed; the round-100 gate receipt is
   `.ufo/waves/round-100/measured/pre-report-gate.out`.

## considerthese

`considerthese/2026-11-08.md` proposal 1 (gate-receipt continuity) is mined as a one-time scan, not a tool:
rounds 90–94 carry `measured/gate-final.out`, round 95 only `controls/prefile-gate.out`, rounds 96–97 neither,
rounds 98–99 `measured/pre-report-gate.out`; round 100 adds `measured/pre-report-gate.out`. The newest full
14-arm gate run before this round was round 99, zero closed rounds old (command:
`for r in 90 … 99; do ls .ufo/waves/round-$r/measured/{gate-final,pre-report-gate}.out .ufo/waves/round-$r/controls/prefile-gate.out; done`).
