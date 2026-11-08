# RV01Wording — C3: the stated wording vs what the frozen counter enforces

Adversarial review of C3 (`plans/round-99-claims.md:122`; frozen mirror
`.ufo/waves/round-99/claims.json` C3) and its instrument
`tools/round99-autoload-states.py`, against the candidate probe
`.ufo/waves/round-99/candidates/kama-probe.r99.sh`. Base revision
`439fdb3d41b55e5b9e6d7c480d17f2c428bae978`. No tracked file was modified.

**Verdict: `falsifies-wording` (partial).** The probe's code satisfies the four graded
mechanisms; the frozen five-cell counter is green on a strictly narrower property than four
sentences of the plan. One sentence is narrowed by a plan section (C3 Disclosed limits (e)); the
other four are not narrowed anywhere:

1. **Exit code is not graded.** `plans/round-99-claims.md:141` ("the exit code is unchanged") and
   limit (b) (`:164-165`, "an unread autoload stays fail-closed drift"). A probe that answers all
   four unread cells with **exit 0** passes the counter (`met=True`, exit 0) *and* the committed
   77-test harness (77/77). Falsifier: F1.
2. **"non-router" is not isolated.** The frozen claim name lists `non-router` among the separated
   triggers, and `plans/round-99-claims.md:145` describes U4 as "valid JSON without the router role
   or field". U4's body carries *neither*, so a probe that drops the `role == "router"` predicate
   entirely passes all five cells and 77/77. Falsifier: F2.
3. **Field-absent-router is not a cell** (behaviour is disclosed in limit (e), coverage is not):
   a probe that reads a valid router document omitting `models_autoload` as explicit **off** passes
   all five cells and 77/77. Falsifier: F3. This is the one case the plan narrows — C3 Disclosed
   limits (e), `plans/round-99-claims.md:167-168` — so it is a coverage gap, not an un-narrowed
   overreach.
4. **Non-boolean field values are not graded.** A truthiness mutant grades
   `{"role":"router","models_autoload":"false"}` as `MODEL_OK` / `router-unloaded-autoload`,
   **exit 0**, and passes the five cells and 77/77. Falsifier: F4. The plan's After sentence
   (`:139-140`, "1 explicit off (a valid router props document whose field is `false`)") and the
   probe header (`:58-62`, "only an explicit `{"role":"router","models_autoload":false}` reads
   `router-unloaded`") are not enforced.
5. **HTTP status is not consulted.** A 401/500 whose body is
   `{"role":"router","models_autoload":false}` reads `router-unloaded` (explicit off), not
   `router-autoload-unread`; the probe has no status check and no cell sends a non-200 `/props`
   answer. Falsifier: F5 (lower severity; outside the claim's four body/fetch triggers).

The two named attacks in the seat brief **do** fail: a blanket rename fails P1 (F6), and
off-for-every-non-on is the base control itself, 4 mismatches (`controls/c3-base.out`). The
positive control is adequate for those; the holes are on the adjacent ungraded outcomes.

---

## 1. Every `/props` outcome `router_autoload` can see, and which cell grades it

Source: `.ufo/waves/round-99/candidates/kama-probe.r99.sh:890-916` (tri-state function),
`:972-976` (reason selection in `router_refine`). Behaviour verified by driving the candidate and
the base probe over 13 stub `/props` outcomes (`w1/out/RV01Wording/driver-cand.out`,
`driver-base.out`); a cell is "graded" only when one of the five `CELLS` rows
(`tools/round99-autoload-states.py:141-146`) distinguishes that outcome.

| # | `/props` outcome | `router_autoload` → | Graded by | Note |
|---|---|---|---|---|
| 1 | `python3` absent (`HAVE_PY=0`, probe `:891`) | 2 unread | **none** | Disclosed limit (c) `:166`; ungraded |
| 2 | connect fail / empty reply after `/v1/models` answered (curl rc 6/7/52/56) | 2 unread | **none** | `reset-props` driver row: unread; at verdict level a fully closed port is `DEAD` before `/props` is consulted |
| 3 | timeout (curl rc 28; 6.5 s body, `TIMEOUT` 5) | 2 unread | **U1** | graded |
| 4 | body over 4 MiB, curl rc 63 (`--max-filesize`) | 2 unread | **U2** | graded |
| 5 | body over cap but curl rc 0, caught by the `wc -c` recheck (`:896`) | 2 unread | U2 outcome | the two guards are not separated |
| 6 | empty body / truncated JSON | 2 unread | **none** | same Python exception path as U3, but no cell |
| 7 | non-JSON (HTML) | 2 unread | **U3** | graded |
| 8 | valid JSON, non-dict (array/string/number/null) | 2 unread | **none** | `json-array` driver row: unread |
| 9 | dict, `role` absent | 2 unread | **U4** | graded, but conjointly with #11 |
| 10 | dict, `role` present but != `"router"` (e.g. `worker`) | 2 unread | **none** | `role-worker-false` driver row: unread; mutant F2 changes it to off and stays green |
| 11 | router doc, `models_autoload` absent | 2 unread | **none** | `absent-field-router` driver row: unread; limit (e); mutant F3 changes it to off and stays green |
| 12 | field `true` | 0 on → `MODEL_OK` / `router-unloaded-autoload` | **none in C3** | `field-true-fast` driver row; protected only by the K5 19-cell regression (all W cells serve `true`, `tools/round99-router-budget.py:375,531`) |
| 13 | field `false` | 1 off → `MODEL_UNLOADED` / `router-unloaded` | **P1** | graded |
| 14 | field non-boolean (`null`, `0`, `1`, `"false"`) | 2 unread | **none** | strict `is True`/`is False` (`:905-908`); mutant F4 changes `1`/`"false"` to **on** (`MODEL_OK`, exit 0) and stays green |
| 15 | HTTP 401/403/500 with a non-props body | 2 unread | **none** | status is never read (`curl` without `-f`, `:894-895`); `http-401-error-json`/`http-403-html` unread |
| 16 | HTTP 401/500 with props-shaped `false` body | **1 off** → `router-unloaded` | **none** | `http-401-router-false`, `http-500-props-false`: explicit off from a non-200 answer |

**Blind spots, named.** No cell covers: `HAVE_PY=0`; connect fail/reset; empty body; a non-dict JSON
document; a role present-but-not-`"router"`; a router document that omits the field; any
non-boolean field value; any non-200 `/props` status; the `models_autoload:true` on path (only K5);
and **no cell compares the exit code** (see F1). U4 grades a conjunction — `{"status":"ok"}` has
neither `role` nor the field — so it cannot isolate either of the two predicates the claim lists.

---

## 2. "An unread flag is not an off flag": absent field and 401

**Valid router document omitting the field.** The candidate returns 2 → `router-autoload-unread`
(`driver-cand.out:absent-field-router`). That is the right fail-closed line, and it is not even
reachable from a grounded server: S624 shows the bare props body is built with
`{"models_autoload", params.models_autoload}` (`sources/s624-server-models-props.txt:5-16`,
upstream `tools/server/server-models.cpp:2030`), and S625 defaults that field to `true`
(`sources/s625-common-models-autoload.txt:6-7`, `common/common.h:705`). So absence can never be a
real "off" state; reading it as unread is defensible. The naming is a category stretch — the
document *was* read, the flag is *absent* — but the reason names the autoload state, not the fetch,
and limit (e) already narrows this case. **No claim overreach here; no cell coverage either**
(F3).

**401.** The seat's premise ("a 401 answer (unread)") is not what the code does. The probe never
inspects the status: `curl -sS ... -o body` without `-f` (`:894-895`), then it parses whatever body
arrived. A 401 with an HTML/error-JSON body is unread *incidentally*, because the body is not a
router props document (`http-401-error-json` → unread). A 401 whose body parses as
`{"role":"router","models_autoload":false}` reads **`router-unloaded`**, i.e. an explicit off state
produced by an unauthenticated answer (`driver-cand.out:http-401-router-false`); same for 500.
Underllama.cpp this is not producible — the auth layer, not the props handler S624 describes,
writes a 401 body — but the vocabulary's stated definition is body-only and no cell constrains it.
Required narrowing sentence: "The probe does not consult the HTTP status of `/props`; only the body
is graded. 401/403/500 bodies are `router-autoload-unread` only when they fail the four body
checks; a non-200 body that parses as a router props document is graded as its explicit state."

---

## 3. Positive-control attacks (executed)

Harness: the real five-cell counter, `--probe-file` scratch copies; base revision pinned
`439fdb3d…` so `base_mismatches` is derived from the committed base bytes.

| probe | 5-cell result | 77-test harness | receipt |
|---|---|---|---|
| candidate (control) | `mismatches=0 … met=True`, exit 0 | 77/77 | `run-cand.out`, `harness-cand` not re-run (committed `controls/c3-harness-candidate.out` 77/77) |
| **F1** unread reasons forced non-drift (`EV_DRIFT` bypassed for `router-autoload-unread`) | **`mismatches=0 met=True`, exit 0**, cells print `exit=0` | **77/77** | `run-mutE.out`, `harness-mutE.out` |
| **F2** `role == "router"` predicate removed | **`mismatches=0 met=True`, exit 0** | **77/77** | `run-mutB-role-blind.out`, `harness-mutB.out` |
| **F3** field-absent valid router doc → off | **`mismatches=0 met=True`, exit 0** | **77/77** | `run-mutA-absent-off.out`, `harness-mutA.out` |
| **F4** truthiness (`if models_autoload:` on, any present falsy off) | **`mismatches=0 met=True`, exit 0** | **77/77** | `run-mutC-truthy.out`, `harness-mutC.out` |
| **F6** blanket rename (explicit false → unread) | `mismatches=1` at P1, `met=False`, exit 1 | — | `run-mutD-false-unread.out` |
| off for every non-on (base semantics) | `mismatches=4`, `met=False`, exit 1 | — | `controls/c3-base.out` |

So: **no**, a blanket rename cannot pass P1; **no**, off-for-every-non-on cannot pass. But four
narrower mutations of the *documented* vocabulary pass both committed instruments. F4 is the most
consequential: `{"role":"router","models_autoload":"false"}` becomes
`MODEL_OK / router-unloaded-autoload / exit 0` — a false green on model loadability — because no
cell and no fixture ever presents a non-boolean field value.

Commands (run from the lane repo; scratch under
`/fast/scratch/hyaku/kama-r99/RV01Wording/`):

```
python3 tools/round99-autoload-states.py --repo . --rev 439fdb3d41b55e5b9e6d7c480d17f2c428bae978 \
  --probe-file <scratch>/probe-<mutant>.sh --work <scratch>/work-<mutant>
TMPDIR=<scratch>/tmp-hX python3 tests/probe-verdicts/check.py --probe <scratch>/probe-<mutant>.sh
```

The counter invokes the probe **without** `--timeout` (`tools/round99-autoload-states.py:126-127`);
U1 relies on the probe's default `TIMEOUT=5`, although `plans/round-99-claims.md:144` says "probe
`--timeout 5`". Behaviourally equivalent today (a longer default would flip U1 to `MODEL_OK` and
fail), so this is documentation drift only.

---

## 4. Findings by severity

**F1 — BLOCKER (C3 outcome asserted but ungraded: exit code).**
`plans/round-99-claims.md:141` and limit (b) `:164-165` assert the unread autoload stays
fail-closed drift with an unchanged exit code. `tools/round99-autoload-states.py:207-208` compares
only `(verdict, reason)`; the per-cell `exit` is printed (`run_pass`) and never compared —
`UNREAD`/`OFF` are 2-tuples (`:141-146`). Scratch mutant `probe-mutE-unread-nondrift.sh` (one
condition added to the port-mode drift decision at candidate `:1446-1447`) prints
`… verdict=MODEL_UNLOADED reason=router-autoload-unread exit=0` for U1–U4 and still
`mismatches=0 … met=True`, exit 0; the 77-test harness also passes 77/77 because no fixture reaches
the new reason. Fix is one line: compare `(verdict, reason, exit)` against
`(*UNREAD, 2)` / `(*OFF, 2)`; or narrow limit (b) to "exit is recorded, not graded".

**F2 — MAJOR (the claim's `non-router` trigger is not isolated).**
Frozen claim name (`claims.json` C3) lists `(slow, oversize, non-JSON, non-router)`; plan
`:145` says U4 is "valid JSON without the router role or field". U4's body is
`{"status":"ok"}` (`tools/round99-autoload-states.py:24`) — no role *and* no field — so the cell
passes for a probe that never checks the role. Scratch mutant `probe-mutB-role-blind.sh` (the
`doc.get("role") != "router"` disjunct dropped at candidate `:903`) returns
`router-unloaded` for `{"role":"worker","models_autoload":false}` (`driver-mutB.out`) yet passes
`mismatches=0 met=True` and 77/77. No plan sentence narrows this. Required amendment: either add a
`{"role":"worker","models_autoload":false}` cell (expected `router-autoload-unread`) or state in
C3 that the role predicate is a code-reading claim, not cell-graded.

**F3 — MAJOR (field-absent router document is disclosed but not graded).**
Plan Before `:132` and probe header `:58-60` put "carried no explicit router `models_autoload`" in
the unread class; limit (e) `:167-168` states the grading rule. The candidate implements it
(`driver-cand.out:absent-field-router` → unread), but no cell instantiates it: scratch mutant
`probe-mutA-absent-off.sh` (absence → off) passes `mismatches=0 met=True` and 77/77. Because
limit (e) **narrows** this case, this is not an un-narrowed overreach — but limit (e) must be read
as behaviour, not coverage. Required sentence: "Limit (e) is a code-reading claim; a mutant that
maps the absent field to `router-unloaded` passes all five cells." A sixth cell
(`{"role":"router"}` → `router-autoload-unread`) would close it.

**F4 — MAJOR (non-boolean field values ungraded; a truthiness mutant grades a model loaded).**
The After sentence (`:139-140`) defines exit state 1 as a document "whose field is `false`"; the
header (`:60-61`) says only the explicit literal reads `router-unloaded`. A truthiness mutant
(`probe-mutC-truthy.sh`, candidate `:905-908` replaced) yields:
`field-string-false` → `MODEL_OK / router-unloaded-autoload / exit 0`,
`field-int-1` → same, `field-null` → `router-unloaded`. Five cells `mismatches=0 met=True`; 77/77.
This is the round's standing failure class at its most dangerous: the reason vocabulary's stated
type strictness is invisible to both instruments, and the mutant's failure direction is a false
green on loadability. `"models_autoload":"false"` is not a shape llama.cpp emits (nlohmann
serialises the bool), so the fix is scope, not necessarily a cell; but the plan must say the type
check is ungraded (or add a non-boolean cell expecting unread).

**F5 — MINOR (HTTP status is not consulted).**
`driver-cand.out` rows `http-401-router-false` and `http-500-props-false` read
`router-unloaded` (explicit off) from a non-200 answer; `http-401-error-json` and `http-403-html`
read unread only because their bodies fail the body checks. No cell sends a non-200 `/props`
answer. Required sentence as in §2, or a 401/403 cell.

**F6 — INFO (the named positive control works).**
Blanket rename fails P1 (`run-mutD-false-unread.out`: `want=MODEL_UNLOADED/router-unloaded
got=MODEL_UNLOADED/router-autoload-unread`, `mismatches=1`, exit 1); off-for-every-non-on is the
base control (`controls/c3-base.out`: 4 mismatches, exit 1). P1 is a stability cell, not a
discriminator for the unread side; its presence does not cover F1–F4.

---

## 5. Required narrowing / amendment sentences

Exact sentences the plan needs (one per finding; none exist today except F3's limit (e)):

- **A1 (F1, after `:141` / in limit (b)):** "The five cells grade `(verdict, reason)` only; each
  cell's exit code is recorded in the receipt and is not compared. A probe that answers U1–U4
  with exit 0 passes `met=True`; the fail-closed exit is asserted by code review, not by this
  counter."
- **A2 (F2, C3 cell list `:143-146`):** "U4's body omits both the router role and the field, so the
  cell does not isolate the role predicate: a probe that accepts any JSON object's
  `models_autoload` as the answer passes all five cells. The `non-router` separation is a
  code-reading claim."
- **A3 (F3, limit (e) `:167-168`):** "Limit (e) states the candidate's behaviour, not a cell; a
  mutant that grades a field-absent router document as `router-unloaded` passes all five cells."
- **A4 (F4, after `:140`):** "Non-boolean values (`null`, `0`, `1`, `"false"`) are not graded; a
  truthiness mutant grades `"false"`/`1` as `MODEL_OK` with exit 0 and passes the five cells and
  the 77-test harness."
- **A5 (F5, new limit (f)):** "The probe does not consult the `/props` HTTP status; only the body
  is graded. A non-200 body that parses as a router props document is graded as its explicit
  state."

If the L1 prefers to keep the claim as measured rather than amend, the minimum honest set is A1
(asserts a property the instrument cannot see) and A2 (lists a trigger the instrument cannot
isolate); A3 is already narrowed by limit (e); A4/A5 are scope additions.

---

## 6. Residual risk and verification gaps

- The cells are stub-fed, not a live router (disclosed limit (a)); S624/S625 ground the body shape
  but the 401 path and the exact 4 MiB/server behaviour are not re-observed.
- The `models_autoload:true` (on) path is outside the five cells; it is protected only by K5's
  19-cell regression, where every cell's props body is `true`
  (`tools/round99-router-budget.py:375`). If K5 is waived or skipped, a probe that breaks the on
  path passes C3.
- `HAVE_PY=0` behaviour (limit (c)) is ungraded; the counter always runs with `python3`.
- The absent-field and non-boolean outcomes are unreachable from a real llama.cpp body, so their
  severity is about the *vocabulary contract*, not live misgrading — except that the instruments
  would not detect a regression that moved them.
- I did not run the 19-cell K5 regression (C1/C3 executor territory, minutes-long); no claim here
  depends on its result.

## 7. Receipts and cleanup

All receipts under `.ufo/waves/round-99/w1/out/RV01Wording/`: `run-cand.out`,
`run-mutA-absent-off.out`, `run-mutB-role-blind.out`, `run-mutC-truthy.out`,
`run-mutD-false-unread.out`, `run-mutE-unread-nondrift.out`, `harness-mutA.out`,
`harness-mutB.out`, `harness-mutC.out`, `harness-mutE.out`, `driver-cand.out`, `driver-base.out`,
`driver-mutA.out`, `driver-mutB.out`, `driver-mutC.out`, the five mutant probes and
`stub-driver.py`. Scratch `/fast/scratch/hyaku/kama-r99/RV01Wording/` removed before yield.
No tool installed or upgraded. No tracked lane file touched; `git` used read-only
(`git show`, `git diff --stat`).
