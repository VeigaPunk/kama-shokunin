# EX03Autoload — kama round 99, wave 1: C3 instrument and candidate probe attack

Seat `EX03Autoload` (building seat, "autoload"). Scope: independently exercise and attack
`tools/round99-autoload-states.py` and `.ufo/waves/round-99/candidates/kama-probe.r99.sh`.
No tracked lane file was edited; nothing was committed. Lane HEAD at attack start:
`f6e7ccc285e0c1207378f73c394acbfda58bff23` (the round-99 freeze commit); base `439fdb3d…`.
Host: curl 8.23.0, Python 3.14.8, GNU bash 5.3.20; no tool installed or upgraded (none needed).

Frozen bytes verified before grading:

| file | sha256 | check |
|---|---|---|
| `.ufo/waves/round-99/candidates/kama-probe.r99.sh` | `829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21` | worktree == `git show f6e7ccc2:…` == `controls/c3-candidate.out` `probe_sha256` |
| `tools/kama-probe.sh` @ `439fdb3d`/HEAD | `40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e` | `git show HEAD:tools/kama-probe.sh` == `controls/c3-base.out` `base_sha256` |

Receipts: `.ufo/waves/round-99/w1/out/EX03Autoload/` (run outputs, mutation diffs, ad-hoc shapes,
harness results, environment). The lane worktree also carries other seats' in-flight edits
(`LOG.md`, `SCORECARD.md`, `tools/round99-record-audit.py`); none of them was touched by me.

---

## 1. Predicate runs

### 1a. Candidate at the freeze (expected `cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1`)

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 tools/round99-autoload-states.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev f6e7ccc285e0c1207378f73c394acbfda58bff23 --work <scratch>/work \
  --probe-file .ufo/waves/round-99/candidates/kama-probe.r99.sh
```

```
AUTOLOAD_STATES99_CELL base U1-slow-props scenario=slow verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99_CELL base U2-oversize-props scenario=oversize verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99_CELL base U3-nonjson-props scenario=nonjson verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99_CELL base U4-nonrouter-props scenario=nonrouter verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99_CELL base P1-autoload-off scenario=off verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99_CELL tip U1-slow-props scenario=slow verdict=MODEL_UNLOADED reason=router-autoload-unread exit=2
AUTOLOAD_STATES99_CELL tip U2-oversize-props scenario=oversize verdict=MODEL_UNLOADED reason=router-autoload-unread exit=2
AUTOLOAD_STATES99_CELL tip U3-nonjson-props scenario=nonjson verdict=MODEL_UNLOADED reason=router-autoload-unread exit=2
AUTOLOAD_STATES99_CELL tip U4-nonrouter-props scenario=nonrouter verdict=MODEL_UNLOADED reason=router-autoload-unread exit=2
AUTOLOAD_STATES99_CELL tip P1-autoload-off scenario=off verdict=MODEL_UNLOADED reason=router-unloaded exit=2
AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True rev=f6e7ccc285e0c1207378f73c394acbfda58bff23 probe_sha256=829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21 base_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e candidate=yes
exit=0
```

Diff against the committed receipt: the ten `AUTOLOAD_STATES99_CELL` lines are byte-identical to
`controls/c3-candidate.out`; the summary is identical except `rev=` (the committed control pinned
`--rev 439fdb3d`; the probe bytes are the same, `probe_sha256` matches). Wall time 16.0 s for both
passes (two probes × five cells, one 6.5 s delay + one 4.5 MiB body).

### 1b. Base at 439fdb3d without `--probe-file` (expected `mismatches=4`, exit 1)

```
python3 tools/round99-autoload-states.py --repo . --rev 439fdb3d41b55e5b9e6d7c480d17f2c428bae978 \
  --work <scratch>/work2
→ AUTOLOAD_STATES99 cells=5 mismatches=4 base_mismatches=4 flips=0 stable=5 met=False rev=439fdb3d41b55e5b9e6d7c480d17f2c428bae978 probe_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e base_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e candidate=no
exit=1
```

All ten cell lines byte-identical to `controls/c3-base.out`. Reproduced exactly as claimed.

## 2. Syntax

```
bash -n .ufo/waves/round-99/candidates/kama-probe.r99.sh   # rc=0
bash -n tools/kama-probe.sh                               # rc=0
```

## 3. Mutation matrix (scratch copies only; tracked candidate untouched)

Each mutant is a copy of the frozen candidate under scratch; exact unified diffs and per-mutant
sha256 are in `out/EX03Autoload/mutants.diff`. Every run used the same counter invocation as §1a
with `--probe-file <mutant>`.

| # | mutant | edit | sha256 (short) | caught by | result |
|---|---|---|---|---|---|
| 1 | `blanket` | `sed s/router-unloaded/router-autoload-unread/g` over the whole file | `544dd63b` | **U1–U4** (4 mismatches) | exit 1 — but **P1 stays stable** (see F8) |
| 2 | `off-for-unread` | non-JSON → `print("off")`; post-hoc size re-check → `return 1` | `c460d2cf` | **U3 only** | exit 1; the oversize half is inert (F11) |
| 3 | `curl-fail-off` | fetch failure/timeout → `return 1` | `a42c184b` | **U1 + U2** | exit 1 |
| 4 | `nonrouter-off` | non-router valid JSON → `print("off")` | `05a5be56` | **U4 only** | exit 1 |
| 5 | `off-branch-unread` (the committed `controls/c3-mutant-blanket.out`) | `off) return 2` | `53943ad2` (= committed receipt) | **P1 only** | exit 1; reproduces the committed control byte-for-byte |
| 6 | `no-fetch` | `router_autoload()` returns 0 unconditionally | `2026049b` | **all five** (`MODEL_OK/router-unloaded-autoload`) | exit 1 |
| 7 | `on-as-unread` | `on) return 2` | `abe64209` | **none** | **ESCAPES**, `met=True` exit 0 |
| 8 | `field-absent-on` | router doc, field missing → `print("on")` | `e9b8c989` | **none** | **ESCAPES**, `met=True` exit 0 |
| 9 | `str-false-off` | field `in (False, "false", 0)` → `print("off")` | `2f98eb0d` | **none** | **ESCAPES**, `met=True` exit 0 |
| 10 | `exit0` | `cmd_check` drift exit forced to 0, verdict/reason unchanged | `7cbcf1ae` | **none** | **ESCAPES**, `met=True` exit 0, every cell prints `exit=0` |

Cell-to-cause attribution: in the probe both U1 and U2 ride the same `curl` non-zero return
(`kama-probe.r99.sh:894`), so a single-branch mutation trips both together; only a mutant that
branched on curl's exit status (28 timeout vs 63 size abort) would separate them. U3 catches only
the JSON-parse branch, U4 only the role check, P1 only the explicit-off branch.

Survivor context (the lane's separate 77-case probe harness, `tests/probe-verdicts/check.py`,
run with the same scratch TMPDIR):

```
mut-on-as-unread     tests=77 passes=74 failures=3   (caught outside the C3 counter)
mut-field-absent-on  tests=77 passes=77 failures=0   (escapes both instruments)
mut-str-false-off    tests=77 passes=77 failures=0   (escapes both instruments)
mut-exit0            tests=77 passes=8  failures=69  (caught outside the C3 counter)
```

## 4. Ad-hoc `/props` shapes (base vs candidate)

Stub: `/v1/models` one `unloaded`, not-failed entry with an existing `status.args[0]`; `/props`
per row (receipt `out/EX03Autoload/adhoc-props-shapes.out`).

| `/props` answer | base | candidate | covered by the plan's wording? |
|---|---|---|---|
| 401 + `{"error":{"message":"Unauthorized"}}` (non-router JSON) | `router-unloaded` | **`router-autoload-unread`** | yes as "non-router"; the reason does not distinguish auth failure |
| 401 + `{"role":"router","models_autoload":false}` | `router-unloaded` | **`router-unloaded`** (off) | literally yes (body shape only); semantically wrong — status ignored (F9) |
| 500 + same router-false body | `router-unloaded` | **`router-unloaded`** (off) | same as above |
| 200 + `{"role":"router","models_autoload":"false"}` (string) | `router-unloaded` | **`router-autoload-unread`** | **not covered** by plan limit (e), only by `corpus/knowledge/router-props-autoload.md:21` (F6) |
| 200 + `{"role":"router"}` (field absent) | `router-unloaded` | **`router-autoload-unread`** | limit (e) asserts this; no cell tests it (F5) |
| 200 + `{"role":"router","models_autoload":null}` | `router-unloaded` | **`router-autoload-unread`** | same family as the string case |
| 200 + empty body | `router-unloaded` | **`router-autoload-unread`** | yes as "not JSON" |

Both probes, every row: verdict `MODEL_UNLOADED`, exit 2 (the fail-closed verdict is stable).

## 5. Mixed `unloaded` entries: the new reason is masked by a failed sibling

Two matching entries, `/props` non-JSON (unread), existing model file
(`out/EX03Autoload/adhoc-mixed-entries.out`):

| entry order (`/v1/models` `data`) | base | candidate |
|---|---|---|
| `[unloaded failed:true, unloaded]` | `MODEL_UNLOADED/router-unloaded-failed` | **`MODEL_UNLOADED/router-unloaded-failed`** |
| `[unloaded, unloaded failed:true]` | `MODEL_UNLOADED/router-unloaded` | **`MODEL_UNLOADED/router-autoload-unread`** |

Cause: `down` is taken from the **first** unloaded entry (`kama-probe.r99.sh:945`) and the new
substitution requires `$down = "router-unloaded"` (`kama-probe.r99.sh:972`). With a failed first
entry, a matching not-failed unloaded entry plus an unread `/props` still reports
`router-unloaded-failed`. Plan:140–141 states the new reason unconditionally; see F2.

## 6. Without `python3`

Probe run with `PATH` = a symlink farm containing every `/usr/bin` entry **except** `python3*`;
scenarios `/props` = explicit `true` and explicit `false` (`out/EX03Autoload/no-python3.out`):

```
SCEN on   base verdict=MODEL_OK reason=matched exit=0    cand verdict=MODEL_OK reason=matched exit=0
SCEN off  base verdict=MODEL_OK reason=matched exit=0    cand verdict=MODEL_OK reason=matched exit=0
```

The candidate's `router_autoload` `HAVE_PY` branch (`kama-probe.r99.sh:891`, `return 2`) is
**unreachable through `check`**: `router_entries` gates on the same flag and yields nothing
(`kama-probe.r99.sh:858–859`), so `router_refine` returns at `any_status=0` before calling
`router_autoload`. Both probes therefore report `MODEL_OK` for a router whose only matching entry
is unloaded — a false green, identical at base and tip. Plan limit (c) (plan:166–168) claims the
candidate "returns unread, while the base returned off"; that difference cannot be observed and the
observed behaviour is worse than the limit says.

## 7. Counter error paths

```
python3 tools/round99-autoload-states.py --repo . --rev HEAD --work <s> --probe-file /nonexistent/probe.sh
→ FileNotFoundError traceback at tools/round99-autoload-states.py:188, exit=1
python3 tools/round99-autoload-states.py --repo . --rev deadbeef --work <s>
→ AUTOLOAD_STATES99 could-not-evaluate: git rev-parse --verify deadbeef^{commit} rc=128, exit=2
```

A mistyped `--probe-file` is reported through the "not met" exit (1), not the documented
"could-not-evaluate" exit (2) — the `except` at `round99-autoload-states.py:196` catches
`RuntimeError`/`TimeoutExpired` but not `OSError` (F10).

## 8. Findings

Severity: **D** = defect in frozen wording/instrument (predicate still met); **G** = coverage gap
proved by a surviving mutant; **N** = nit.

| id | sev | finding | file:line | command / evidence |
|---|---|---|---|---|
| F1 | D | The counter's own docstring misquotes its do-nothing control: `stable=1` where the committed receipt and the plan say `stable=5`. A grader copying the docstring expects a receipt that never occurs. | `tools/round99-autoload-states.py:11`; contrast `controls/c3-base.out:16`, `plans/round-99-claims.md:149` | §1b run; `grep -n 'stable=' tools/round99-autoload-states.py .ufo/waves/round-99/controls/c3-base.out plans/round-99-claims.md` |
| F2 | D | Plan:140–141 ("a matching `unloaded`, not-failed entry on an unread answer now reads …`router-autoload-unread`") is false when an earlier matching entry is `unloaded failed:true`: the candidate keeps `router-unloaded-failed`. The sentence has no ordering qualifier and no cell covers multi-entry lists. Shape is duplicate-id (contrived for llama.cpp), but the code rule is order-dependent. | `.ufo/waves/round-99/candidates/kama-probe.r99.sh:945` (first `down` wins), `:972` (substitution condition) | §5, `out/EX03Autoload/adhoc-mixed-entries.out` |
| F3 | D | Plan:141–142 says "the exit code is unchanged", but the five cells compare only `(verdict, reason)` and never assert the exit. The `exit0` mutant (correct vocabulary, drift exit 0) passes `met=True`. The 77-case harness catches it (69 failures), so the lane is not blind lane-wide — the C3 predicate is. | `tools/round99-autoload-states.py:207–210`; `plans/round-99-claims.md:141` | §3 row 10; `out/EX03Autoload/mutation-matrix-2.out` |
| F4 | D | Limit (c) describes an unreachable branch and understates the real behaviour: without `python3` no router refinement occurs at all and both probes answer `MODEL_OK/matched` for an unloaded-only router. | `plans/round-99-claims.md:166–168`; `kama-probe.r99.sh:858–859`, `:891` | §6, `out/EX03Autoload/no-python3.out` |
| F5 | G | No cell covers a router document with the field **absent**; `field-absent-on` survives the counter and the 77-case harness. Limit (e)'s assertion ("graded unread") is therefore unverified by any instrument. | `plans/round-99-claims.md:170–171`; `kama-probe.r99.sh:910` | §3 row 8; `out/EX03Autoload/harness-mutants.out` |
| F6 | G | No cell covers a **non-boolean** field; `str-false-off` (`"false"`/`0` accepted as off) survives both instruments. Plan limit (e) mentions only omission; only `corpus/knowledge/router-props-autoload.md:21` says "not boolean". | `plans/round-99-claims.md:170–171`; `corpus/knowledge/router-props-autoload.md:21` | §3 row 9, §4 |
| F7 | G | No cell exercises the **explicit-on** state; `on-as-unread` survives the five-cell counter (the 77-case harness catches it, 3 failures). The three-state table's `on` row is not measured by C3. | `tools/round99-autoload-states.py:141–145` (5 cells: 4 unread + 1 off) | §3 row 7 |
| F8 | D | "positive control: a blanket rename fails it" (plan:147–148, K4 plan:161–162) is only true for the off-branch→unread mutation (`53943ad2…`, the committed control). A literal rename of every `router-unloaded` also rewrites the comparison at `:972`, so **P1 stays `router-unloaded`** and U1–U4 fail instead (4 mismatches). | `plans/round-99-claims.md:147–148`, `:161–162`; `kama-probe.r99.sh:972` | §3 row 1 |
| F9 | D | HTTP status is never inspected: a 401 or 500 whose body is `{"role":"router","models_autoload":false}` reads **off** (`router-unloaded`). "Explicit off" is defined by body shape only; no 2xx requirement is stated or tested. | `kama-probe.r99.sh:893–894` (curl without `-f`), `:907–910` | §4 |
| F10 | N | Missing `--probe-file` path raises an uncaught `FileNotFoundError` and exits 1 ("not met") instead of 2 ("could-not-evaluate"). | `tools/round99-autoload-states.py:188` | §7 |
| F11 | N | The post-hoc `wc -c` size re-check is dead on curl ≥8.4 (curl aborts at `--max-filesize` with exit 63 first); U2's discrimination rests on the curl abort, so a mutation of the re-check alone is inert. | `kama-probe.r99.sh:894–895` | §3 row 2 (`U2` unchanged) |

No BLOCKER: the C3 predicate itself (`mismatches=0 …, met=True`, exit 0 at the freeze probe bytes)
reproduces exactly, and the base control (`mismatches=4`, exit 1) is red as required. The defects
are in the claim's After paragraph, the disclosed limits and the counter's cell coverage — the
standing failure class ("a counter green on a property narrower than the wording") applies to
F2–F9.

## 9. Required plan narrowings (for the L1; I do not edit the plan)

1. **F3 (highest):** either assert `exit == 2` for every cell in
   `tools/round99-autoload-states.py` (the `verdict_reason` tuple already carries it) or strike
   "and the exit code is unchanged" from the After paragraph and limit (b). Do not leave the
   fail-closed claim resting on an unmeasured field.
2. **F1:** change `tools/round99-autoload-states.py:11` to `stable=5` so the docstring matches the
   committed control; the predicate line (`:7`) is correct.
3. **F4:** replace limit (c) with the observed fact — without `python3` the probe performs no router
   refinement at all (`router_entries` gates first) and reports `MODEL_OK` for an unloaded-only
   router; the candidate's `HAVE_PY → unread` branch is unreachable through `check`. Mark the
   no-python3 false green as carried (base identical), not as a round-99 state.
4. **F5/F6:** extend limit (e) to "field absent **or not a JSON boolean**" and state that neither
   case is exercised by the five cells (the code and `corpus/knowledge/router-props-autoload.md:21`
   already say unread; the counter does not test it). Optionally add U5 `{"role":"router"}` expecting
   `router-autoload-unread`.
5. **F7:** state that the five cells grade the unread/off split only; the explicit-on leg is covered
   by the 77-case harness, not by C3 — or add a P0 `{"role":"router","models_autoload":true}` cell
   expecting `MODEL_OK/router-unloaded-autoload` (the 77-case harness already exercises explicit-on
   answers — `mut-on-as-unread` fails 3 cases there — so an on cell is safe to calibrate against it).
6. **F8/K4:** restate the P1 positive control as "the explicit-off branch returns the unread state"
   (the committed `c3-mutant-blanket.out`, sha `53943ad2…`). A literal rename of every
   `router-unloaded` does not flip P1; it flips U1–U4 through the rewritten comparison.
7. **F2:** qualify plan:140–141 with "when the first matching `unloaded` entry is not `failed`", or
   fix `:972` to key the substitution on `ra=2` regardless of `$down` (a code change, out of scope
   for this wave). If neither, record it as a disclosed limit.
8. **F9:** define "explicit off" as a valid router props document **on a 2xx response** (or disclose
   that HTTP status is not part of the read); today a 401/500 carrying a router-shaped `false` body
   is graded off.

## 10. What holds (positive evidence)

- The frozen candidate produces exactly the committed 10 cell lines; the summary differs only in
  `rev=`; exit 0. The base control is red (4 mismatches, exit 1) with the committed cell lines.
- The four unread causes named by the claim (slow, oversize, non-JSON, non-router) each flip from
  `router-unloaded` to `router-autoload-unread`; the explicit boolean `false` stays
  `router-unloaded`; verdict and exit stay `MODEL_UNLOADED` / 2 in every case I ran.
- A probe that never fetches `/props` (all-on) is caught by all five cells; each single-branch
  regression I built that maps one unread cause to "off" is caught by the cell for that cause
  (U3/U4/U1+U2 respectively, P1 for the off branch). The counter is not vacuous — it is narrower
  than the claim's prose, not blind.
- The counter is fast (~16 s) and self-contained (loopback stub, ephemeral port, scratch work dir
  removed on exit); `bash -n` is clean on both probes; repeat runs were stable (12 counter runs, no
  flake).

## 11. Bounds compliance / cleanup

- Wrote only `…/w1/out/EX03Autoload/*` and this report; no tracked lane file, no fleet repo, no
  lane jj state, no Git index mutation. Fixtures and clones lived only in
  `/fast/scratch/hyaku/kama-r99/EX03Autoload/`, deleted before yield.
- No `git add/commit/stash/checkout/switch/reset/pull/push`, no mutating `jj`, no pacman, no host
  service, no sysctl change, no process kill, no operator router or registered consumer contacted.
- No tool installed or upgraded. Stubs bound 127.0.0.1 ephemeral ports only.
