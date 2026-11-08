# SB01Lesson — round-100 lesson body (kama, wave w1)

Seat `SB01Lesson`. Lane `kama`, round 100, L1 `KamaR100`. Measured commit **M**
`2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`; receipts committed at `3626e06c`; base
`6776c667372a0da8635ebfbda6cbc92d8fb17304`. Lane tip at my reading time `6d0e3abc` (the wave-spec
commit). `git diff 2e27e6f1 6d0e3abc -- SCORECARD.md LOG.md corpus/SOURCES.md
tools/round100-record-audit.py tools/round100-props-status.py` is **empty** — the counters, the probe,
the correction blocks and the SOURCES rows I graded are the measured bytes.

**Scope of this seat.** Draft the round-100 lesson body (`## Gate` + `## Mistakes`) and report. The
draft is at `.ufo/waves/round-100/w1/out/SB01Lesson/round-100-lesson-draft.md`; its text is reproduced
verbatim in §2 below. I did not edit any tracked lane file: `git status --porcelain` in the lane shows
only the untracked wave directories (`.ufo/waves/round-100/w1*`), which are the wave's own.

---

## 1. Behaviour, gates, and what I attacked

### 1.1 C1 — the round-100 record audit (calibration)

`tools/round100-record-audit.py --repo . --rev <M>` reads the two `## Round 100 correction — round-99
records` blocks from `git show <M>:SCORECARD.md` and `git show <M>:LOG.md`, derives the expected facts
from committed wave bytes (`.ufo/waves/round-99/w1-results.json`, `w1-spec.json`,
`.ufo/waves/round-99/measured/c{1,2,3}.out`), and prints
`RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=<resolved>` (exit 0) at M.

The nine checks, all from committed bytes at `<M>`: (1,2) one block each in `SCORECARD.md` and `LOG.md`;
(3,4) each block states the derived attack fractions `4 of 12 (33%)` (policy roles) and `6 of 12 (50%)`
(ledger roles), both re-derived from `w1-spec.json` roles at `tools/round100-record-audit.py:99-101`;
(5) no digit percentage other than those two survives outside a quoted pointer phrase; (6) both state
`12 seats, 0 dead`; (7) every line pointer is revision-bound and quoted, unbound = 0, bound ≥ 3;
(8) every bound pointer's phrase is on that line at that revision; (9) `r99-measured.json` holds the three
round-99 measured predicate lines byte-equal to the committed receipts, each `exit=0`.

I attacked check 7/8 (the pointer grammar) through the counter's **public** `--repo/--rev` path on
scratch commits — the same route the committed forgery driver uses
(`.ufo/waves/round-100/controls/c1_forgeries.py:82-91`: clone `--shared --no-checkout`, checkout base,
copy the three files in, commit, run the counter with `--repo <clone> --rev HEAD`).

**Finding (falsifies-wording).** `BOUND_RE` (`tools/round100-record-audit.py:63-64`) and `ANY_PTR_RE`
(line 65) both recognise a revision token only as **lowercase** hex `[0-9a-f]{7,40}`. A pointer whose
revision is uppercase hex, a short hash, or a symbolic ref is matched by *neither* regex: it is not
counted as bound and not flagged as unbound. The claim says every pointer is bound and re-resolves
(`plans/round-100-claims.md:44`; `claims.json` C1 name: "bind every SCORECARD/LOG/lessons line pointer to
a revision where its quoted phrase sits on that line (>=3)"). The counter goes green on a block whose
pointer does **not** re-resolve, whenever the revision is spelled outside that one dialect.

Evidence — `out/SB01Lesson/c1-pointer-grammar-matrix.out`, all `checks=9 mismatches=0 met=True` (exit 0)
against a `SCORECARD.md` pointer to line 9999 (a line that does not exist; `SCORECARD.md` is 6536 lines
at 6776c667):

| case | pointer | verdict |
|---|---|---|
| G1 uppercase 40-hex | `` `SCORECARD.md@2E27E6F1E6B2514EC8AC5D6344998B3DB61E16D6:9999` `` | green (rc 0) |
| G2 short hex (6) | `` `SCORECARD.md@6776c6:9999` `` | green (rc 0) |
| G3 symbolic ref | `` `SCORECARD.md@master:9999` `` | green (rc 0) |
| G4 lessons sub-path | `` `corpus/lessons/sub/dir.md:9999` `` | green (rc 0) |
| G5 plain unbound | `` `SCORECARD.md:9999` `` | **red**, check 7 (rc 1) |
| G6 in-dialect wrong line | `` `SCORECARD.md@6776c667:9999` `` | **red**, check 8 (rc 1) |

The decisive pair is `out/SB01Lesson/c1-twin-case-control.out`: **the same stale pointer**, differing
only in the hex's case, grades differently.

```
T1-upper  pointer=SCORECARD.md@6776C667:6431  -> checks=9 mismatches=0 met=True   (rc=0)
T2-lower  pointer=SCORECARD.md@6776c667:6431  -> RECORD_AUDIT100_MISMATCH check8  (rc=1)
```

Line 6431 at `6776c667` is the **stale** line — the exact round-99 defect the round-100 correction exists
to fix (`corpus/lessons/round-99-verifier-spotcheck.md:117`; the phrase is absent at 6431 and present at
6446, both verified by `git show 6776c667:SCORECARD.md | sed -n '6431p;6446p'`). T1 therefore re-opens
defect 1 and the frozen counter accepts it.

The committed forgery set does not reach this: `controls/c1-forgeries.out` F1–F7 all use the
lowercase-hex spelling the regex already accepts (F3 is `SCORECARD.md@6776c667:6447`, one line off —
in-dialect). I verified the counter's bytes are unchanged between M and the tip (both
sha256 `6fcc628ebe29d0979490ac307177800193f394ed11f75ba89d5e1b425c384386`), so this is a property of the
frozen instrument, not of drift.

Also observed, not part of my verdict: `.ufo/waves/round-100/claims.json` still carries
`"measured": "pending"` for both C1 and C2 (round-99 spot-check defect 4, `…spotcheck.md:122`, recurring
unchanged), and no counter reads that file.

### 1.2 C2 — the `/props` status gate (depth)

`tools/round100-props-status.py --repo . --rev <M> --work <scratch>` runs the lane's own probe
(`bash tools/kama-probe.sh check --port … --expect fixture-model --id r100 --json`) against a
loopback stub router on an ephemeral port and grades nine cells on the triple (verdict, reason, exit).
At M it prints `ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`
(exit 0).

The probe change is real and is at `tools/kama-probe.sh:901-904`:
`pcode=$(curl … -w '%{http_code}' …) || return 2` then `[ "$pcode" = 200 ] || return 2`. At base
(`6776c667`) the same function is `tools/kama-probe.sh:890-895` and has no status gate at all.

**Finding (falsifies-wording).** The claim is that the probe reads the router's **bare** `/props` body
only on a final HTTP 200 (`plans/round-100-claims.md` C2 title; `claims.json` C2 name: "the probe reads
the router's bare /props body only on a final HTTP 200"). The counter's stub answers by
`path = self.path.split("?")[0]` (`tools/round100-props-status.py:103`), so it **strips the query
string**: `/props` and `/props?model=fixture-model` are the same cell. A probe that reads the
model-qualified path — which upstream's own README documents as routing to an instance
(`tools/server/README.md:2157-2160`, "The router uses the `model` query parameter") and which the probe's
own header calls out as unsafe (`tools/kama-probe.sh:57`: "`/props?model=` would route to, and may load
an instance") — grades green.

Evidence — `out/SB01Lesson/c2-probe-mutant-matrix.out`, all through the counter's public `--probe-file`
path:

| mutant | change to the frozen tip probe | verdict |
|---|---|---|
| M1 | read 64 body bytes *before* the 200 gate | **green** (rc 0) |
| M2 | read `/props?model=fixture-model` instead of the bare path | **green** (rc 0) |
| M3 | read `/props/` (trailing slash) | **red** (rc 1) — the stub 404s it |
| M4 | drop the 200 gate entirely (the base defect) | **red** (rc 1), 6 mismatches |
| M5 | fully JSON-parse the body *before* the 200 gate | **green** (rc 0) |

M4 is the control: the counter does catch the actual base defect, so M1/M2/M5 are green because the
*observable* (verdict, reason, exit) is unchanged — not because the counter is blind to them. The
inference that M2 is a real distinction is confirmed constructively: I copied the counter to scratch and
patched only the stub's line 103 to keep the query string, and the **same M2 mutant then fails**
(`P1-200-router-off` and `P2-200-router-on` mismatch, `mismatches=2 met=False`, rc 1). The frozen stub's
query-stripping is what hides it.

So the counter grades "the status gate is honoured on these nine answers", not the claim's stated
"the router's **bare** `/props` body". The disclosed limits (`plans/round-100-claims.md` C2 limits (a)-(e))
say the cells are stub-fed, that a non-router intermediary's 200 is still read, that only the
`router_autoload()` read changes, that other non-200 statuses are not each graded, and that a slow 200 is
the round-99 cell. **None discloses that the stub cannot distinguish the bare path from a
model-qualified one** — the claim's word "bare" is unfalsifiable against this counter.

Also observed, not part of my verdict: M1/M5 (reading the body bytes before the gate) show the counter
cannot see *when* the body is read, only what the probe concludes from it. The claim's wording ("reads
… only on a final HTTP 200") is stronger than the instrument.

### 1.3 Out of scope

I did not re-measure the freeze-time controls (`c1-base.out`, `c1-forgeries.out`, `c2-base.out`,
`c2-candidate.out`, `c2-mutant-blanket.out`, `c2-prefreeze-p2guess-*.out`, `c2-regression-r99.out`,
`census-start.out`) beyond reading them, and I did not re-run the census (no
`controls/census-end.out` exists in the tree — the round-100 census-end receipt is measurement-time and
not yet committed). I did not evaluate the `plans/round-100-claims.md` disclosed limits for
completeness beyond the two claims I attacked, and I did not touch `SKILL.md`, `SCORECARD.md`, `LOG.md`,
`corpus/SOURCES.md` or the fleet repo.

---

## 2. The drafted lesson body, verbatim

File: `.ufo/waves/round-100/w1/out/SB01Lesson/round-100-lesson-draft.md`

````markdown
# Round 100 — the correction of the round-99 records, and a `/props` body that is read only on HTTP 200

Lane `kama`, round 100, L1 `KamaR100`. Base `6776c667372a0da8635ebfbda6cbc92d8fb17304` (round 99 closed
`admitted`; C1/C2/C3 verified at `00394f3b`, `corpus/lessons/round-99-verifier-spotcheck.md`). Claims: C1
calibration (the round-100 correction of the round-99 records agrees with the committed round-99 wave
evidence on nine enumerated checks, every line pointer revision-bound and re-resolving), C2 depth (the
probe reads the router's bare `/props` body only on a final HTTP 200).

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

**M1 — the round-99 correction bound its line pointers to a revision, but the counter that grades
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
revision is graded, not skipped. Shown able to fail: `out/SB01Lesson/c1-pointer-grammar-matrix.out` —
G1 (uppercase 40-hex rev), G2 (6-hex short rev), G3 (symbolic `master` ref) and G4 (a `corpus/lessons/`
sub-path) all print `checks=9 mismatches=0 met=True` (exit 0) while pointing at a line that does not
exist; `out/SB01Lesson/c1-twin-case-control.out` is the decisive pair: the **same** stale pointer
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
````

---

## 3. Commands run (all evidence reproduced from committed bytes)

Sources re-opened (HTTP 200 each; digests match `.ufo/waves/round-100/sources/*.txt`):

```
curl -sS -o <file> -w '%{http_code}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.cpp
curl -sS -o <file> -w '%{http_code}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-common.cpp
curl -sS -o <file> -w '%{http_code}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/tests/unit/test_router.py
curl -sS -o <file> -w '%{http_code}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md
```
→ `out/SB01Lesson/sources-reopen-receipt.out`

C1 attack (scratch clone `git clone --shared --no-checkout`, base checkout, files copied in, one commit
per case, counter run with `--repo <clone> --rev HEAD`):

```
python3 tools/round100-record-audit.py --repo "$D" --rev HEAD
```
→ `out/SB01Lesson/c1-pointer-grammar-matrix.out`, `out/SB01Lesson/c1-twin-case-control.out`,
`out/SB01Lesson/c1-pointer-grammar-forgeries.out`

C2 attack (counter's public `--probe-file` path; mutants are rewrites of the frozen tip probe):

```
python3 tools/round100-props-status.py --repo "$D" --rev 2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6 \
  --work "$S/mut" --probe-file "$S/mut/probe.sh"
```
→ `out/SB01Lesson/c2-probe-mutant-matrix.out`

Control patch (scratch copy of the counter only, to show the stub's query-stripping is what hides M2):

```
python3 - <<'PY'   # tools/round100-props-status.py:103
p = pathlib.Path("…/faithful/counter.py"); t = p.read_text()
t = t.replace('        path = self.path.split("?")[0]\n', '        path = self.path\n', 1)
PY
```
→ M2 against the frozen stub: `cells=9 mismatches=0 met=True` (rc 0); M2 against the patched stub:
`MISMATCH P1-200-router-off`, `MISMATCH P2-200-router-on`, `cells=9 mismatches=2 met=False` (rc 1).

---

## 4. Surfaces touched

- **Written (mine, untracked):** `.ufo/waves/round-100/w1/SB01Lesson.md` (this report),
  `.ufo/waves/round-100/w1/out/SB01Lesson/round-100-lesson-draft.md`,
  `.ufo/waves/round-100/w1/out/SB01Lesson/{c1-pointer-grammar-matrix.out,
  c1-pointer-grammar-forgeries.out, c1-twin-case-control.out, c2-probe-mutant-matrix.out,
  sources-reopen-receipt.out}`.
- **Read only:** `tools/round100-record-audit.py`, `tools/round100-props-status.py`,
  `tools/kama-probe.sh`, `tools/round99-autoload-states.py`, `plans/round-100-claims.md`,
  `.ufo/waves/round-100/{claims.json,r99-measured.json,measured/,controls/,sources/}`,
  `corpus/{SOURCES.md,lessons/round-99.md,lessons/round-99-verifier-spotcheck.md,
  knowledge/router-props-autoload.md}`, `SKILL.md`, `SCORECARD.md`, `LOG.md`.
- **Scratch:** `/fast/scratch/hyaku/kama-r100/SB01Lesson/` (fixture clone + probe mutants + fetched
  sources), deleted before this report is filed.
- **No tracked lane file edited; no `git add/commit/stash/checkout/switch/reset/pull/push` in the lane;
  no jj command run; no fleet-repo file touched; no host service touched; no burner started.**
- **Note on lane state.** `git status --porcelain` shows `corpus/knowledge/probe-answer-bounds.md` and
  `corpus/knowledge/router-mode-readiness.md` as modified. Their mtimes are `20:15:50`, before my first
  write (`20:23`), and their diffs are round-100 knowledge-file appends by another seat — **not mine**.
  I left them untouched.

## 5. Findings carried to the L1

1. **C1's pointer grammar is one dialect wide.** A stale or non-resolving pointer written with an
   uppercase-hex, short-hex or symbolic revision grades green, and the *same* pointer at the stale line
   6431 flips the verdict on the hex's case alone. Fix: widen `BOUND_RE`/`ANY_PTR_RE` to accept any
   revision git resolves (or normalise to the resolved commit first), and add a forgery to
   `c1_forgeries.py` that spells the revision outside the accepted dialect.
2. **C2's stub cannot tell the bare `/props` from a model-qualified one.** The claim says "bare"; the
   stub strips the query string (`round100-props-status.py:103`), so a probe reading
   `/props?model=…` grades green. Fix: have the stub answer the model-qualified path differently (as
   upstream does — it routes to an instance), or narrow the claim's wording to the status gate and carry
   bareness as a separate, disclosed limit.
3. `plans/round-100-claims.md` C1/C2 limits (a)–(f) do not disclose either gap; an amendment would have
   to state them.

VERDICT C1 falsifies-wording the counter's `BOUND_RE`/`ANY_PTR_RE` (`tools/round100-record-audit.py:63-65`) accept only lowercase-hex revisions, so a pointer spelled `6776C667`/`master`/`6776c6` is neither bound nor unbound — the stale `SCORECARD.md@…:6431` pointer grades `checks=9 mismatches=0 met=True` while the lowercase spelling of the same pointer fails check 8 (twin control).
VERDICT C2 falsifies-wording the claim says the probe reads the router's **bare** `/props` body, but the stub strips the query string (`tools/round100-props-status.py:103`), so a probe reading `/props?model=fixture-model` grades `met=True`; the same mutant fails once the stub keeps the query.
