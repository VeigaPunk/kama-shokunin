# Round 94 — non-author closure spot-check (hyaku closure; verifier: hyaku-closure @m_zfl session, non-author)

Lane tip `32f8e347604856a8f2a3cbf73c54592c926b0bf4`, base `e6f1dccecbad6dea44a129dabc928822c458e824`. Dispatched as non-author integrator; no lane file edited except this spot-check origin.
Dispatch/complete digest (copied from closure prompt, `.ufo/watchdog.log` mutable):
2026-11-07T22:59:09-03:00 launch kama round=94 pgid=3469328 driver=hyaku-inline attempt=1;
2026-11-07T23:35:21-03:00 lane-dead-no-report kama round=94; retry same round (hyaku-inline attempt=1: L1 ended without a landed report: FAIL report_of (missing, unchanged, no SHONEN heading, or < 400B): .ufo/reports/round-94/kama.md);
2026-11-07T23:35:28-03:00 launch kama round=94 pgid=963924 driver=hyaku-inline attempt=2;
2026-11-08T02:03:04-03:00 complete kama round=94; hyaku-inline attempt=2.

## 1. Step-1 conformance

- Report committed in fleet repo by lane identity: `git log --format='%an %H %s' -- .ufo/reports/round-94/kama.md` → 4 commits `e19c4021 04a53a85 87dbfa13 fd953b39` all `kama-shokunin` (round-94: kama report …). PASS.
- `SHONEN` heading + one line per box: `grep -n "^## SHONEN" .ufo/reports/round-94/kama.md` → line 244; 4 box lines (`- [~]` ×4, each with pointer). PASS. Report 20966 B, substantive → not a marker. PASS.
- Cited commits exist and are ancestors of lane branch `master`: `git -C kama-shokunin merge-base --is-ancestor <hash> master` → 285f1783 YES, a27656a4 YES, 6aa5fa6b YES, e6f1dcce YES, 32f8e347 YES; `git merge-base --is-ancestor e6f1dcce 32f8e347` YES. Lane HEAD = cited tip; `git ls-remote origin refs/heads/master` = `32f8e347…` matches local. PASS.
- No uncommitted round work: `jj-lane.sh state` → `branch=master local=32f8e347… remote=32f8e347… ahead=0 behind=0 tracked=0 untracked=0`; `git status --porcelain` empty. PASS.
- Prompt `.ufo/prompts/kama-round-94.md` carries mission/axes binding, 1–3 falsifiable claims + lowest-axis rule, §2b frontier step, §3 L2 minimum (≥8 in one batched call), §4 report contract with 6 sections, §5 commit-then-push + push scope + L0. DEFECT (status-neutral, routed): §4 omits the commit-hash citation rule verbatim (citing HEAD at filing is required only by PROTOCOL land-last clause, not restated in the prompt); the lane nonetheless cited tip + measured revs in report header. No other template item missing.

## 2. Claims re-check (evidence-verified per Gate standard — lane-owned counters, never executed by closure)

Note: I did not execute sibling gates. All numeric claims are verified against committed receipts + ledger; discernment/quote checks below were re-opened separately.

| Claim | Axis | Re-derived (committed bytes) | Reported | Verdict |
|---|---|---|---|---|
| C1 per-file GGUF parse budget | operability | `measured/c1.out` tail: `ROUTER_BUDGET cells=19 mismatches=0 positive_mismatches=0 load_stable=1 … load1_nat=232.08 burners=96`; `controls/c1-base.out`: `cells=19 mismatches=3 load_stable=0 load1_nat=246.26 exit 1`; matched pair `measured/c1-M1-burners0.out` `load1_nat=249.15 burners=0 exit 0`; `controls/harm-base.out` `tests=77 passes=77 failures=0` + `RESULT pass=30 fail=0`, exits 0 | predicate met on 19 cells; filed **not verified (honest stop)**, narrowed in `plans/round-94-amendment-1.md` | **does NOT verify** — correctly filed. Wave seats falsify the as-worded load-independence: SC02 F1–F4, CR01 F3/F6/F7/F8 pass the counter while misgrading real listings, MT01 BLOCKER-1 (plan F1 control false; per-invocation shape M02 green at load1 323). |
| C2 per-entry-point port/slot setters (92 rows) | depth | `measured/c2.out` tail: `SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True`; `controls/c2-base.out`: `SETTER_SWEEP 92 0 0 0 0 92 0 0 … met=False exit 1` | counter met; filed **not verified** (K2 fired) | **does NOT verify** — correctly filed. RV02 (92/92 bound) is semantic-blind; SC01 F1 (R19 silent for cli/router-child; "1 slot" falsified 1/4/5/6/0 auto→4) + F2 (`AIP_HTTP_PORT` inherited by router child beats `--port`; child logged overriding 39547 with 18230) + CN01 F4 falsify R18/R19. Counter met, semantics false. Honest stop upheld. |
| C3 frontier census + lesson self-check | calibration | `corpus/SOURCES.md` rows `grep -cE '^\| S[0-9]'` → **355**; `controls/census-start.out` tail says 343 at base; `corpus/lessons/round-94.md` has `## Gate` + `## Mistakes` (155 lines); `sources-census.sh validate --root … kama` exit 0 (re-run at closure, W04 pre-existing duplicates only); S604 quote line 150→151 repaired | 343 → 355, exit 0; one reject with flip; **verified** | **VERIFIES**. Census delta, repair (curl `preset.cpp` lines 149–153: line 151 is `opt.handler_string(params, val);`, 150 is `if (opt.handler_string) {`), Gate/Mistakes presence, sourced claim (S604 cited by C2). S604 census re-run exit 0 post-repair confirmed in report. |

Per-axis grades: **operability — unprovable** (19-cell predicate true; load-independence not established on this host; honest stop with narrowing as deliverable; no evidence it is worse than base — live-router EX02 base false-green 2/2 vs M1 stable 2/2 — but that is corroboration, not verification of the as-filed claim). **depth — unprovable** (counter met, R18/R19 semantics falsified by SC01 F1/F2; dated `SKILL.md` §Round 94 correction c1–c4 supersedes frozen rows; R20/R21 routed). **calibration — improved** (C3 verified end-to-end; S604 misstatement repaired; frozen-predicate token defect M6 honestly logged).

No owned axis harmed: harm-base green both base and tip; scores unchanged (operability 8, depth 7, calibration 7); `git diff e6f1dcce 32f8e347 -- SCORECARD.md` shows score deltas none claimed; exit-2 unevaluability is disclosed, not hidden.

## 2b. Pre-file falsification ledger (Amendment 59)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane kama --round 94` → `PREFILE-FALSIFICATION: pass claims=3 rows=14 attack_seats=8 findings=0`, exit **0** (re-run at closure; same as report §Sources & frontier gate). Ledger `.ufo/waves/round-94/claim-falsification.tsv` covers every claim in `claims.json` (C1 ×5 rows, C2 ×5, C3 ×2, MT01 ×2); every attack seat that produced an artifact appears (RV01, RV02, CR01, CR02, MT01, MT02, CN01, CN02 = 8); each `falsifies-wording` row names its narrowing (`plans/round-94-amendment-1.md`). All four falsifies-wording rows (SC02 C1, SC01 C2, CN02 C3, MT01) are **real and reconciled**: lane narrowed C1, filed C2 not verified, repaired S604 + landed missing receipts. No unreconciled failing row. Ledger not edited.

## 3. Discernment spot-check (LEARNING.md — outside the lane)

| Item | Decision | Re-opened source (command) | Agree / disagree | Reason |
|---|---|---|---|---|
| S604 `common/preset.cpp` @ b12177 | **admit** (A, code, mined) | `curl -s https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/preset.cpp` lines 149–153: `if (opt.handler_string) {` at 150, `opt.handler_string(params, val);` at **151** | **agree** | Quote ≤25 words (`opt.handler_string(params, val);`, 2 words), correctly located after repair; grounds config.ini/`--models-preset` mechanism cited by C2 P-rows. Verifier's curl confirms line 151 verbatim. |
| S607 `tools/server/server-common.cpp` @ b12177 | **admit** (A, code, mined) | `curl -s https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-common.cpp` lines 2234–2238: `return std::getenv(SERVER_ENV_ROUTER_PORT) != nullptr;` | **agree** | Quote verbatim at cited line; grounds router-child detection. Digest equal to `sources-opened.out` (sha256 `b686729e…`). |
| The codeload archive itself as a SOURCES row | **reject** (input, not a teaching source; flip: GitHub stops serving per-file raw URLs for the tag) | Lesson Gate row (`codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177`, sha256 `f50a52f4…ea13`) | **agree** | Binary archive is the counter's pinned population input (`TARBALL_SHA256`), not learned knowledge; rejection is evidence of taste with a falsifiable flip. Same digest re-derived in `measured/c2.out` (`SETTER_DIGEST f50a52f4…`). |

`corpus/SOURCES.md` row count re-derived at closure: **355** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`); `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit **0** (W04 duplicate-URL warnings pre-existing, none new for S604–S615; W01 S481 tierC pre-existing). New-row quotes ≤25 words hold for sampled rows (S604 2 words).

## Trend verdicts (with evidence)

- **expansion: unchanged** — agree with lane. 12 rows extend depth on an existing surface (setter rows, router-child env); no new surface opened; narrow claim is a narrower object than declared. No new capability beyond the budget instrument (not an expansion credit while C1 is unverified).
- **quality: improved** — agree with lane, with its caveat. Probe change demonstrated at matched band (base `mismatches=3 load_stable=0` exit 1 @246.26 vs M1 `mismatches=0 load_stable=1` exit 0 @249.15) and live router (EX02 2/2 vs 2/2); S604 + three falsified setter statements superseded by dated corrections; harm suites unchanged. But the certifying counter does not establish load-independence (SC02 F1 / CR01 survivors / MT01 M02). Claim filed not verified rather than upgraded — the honesty is the improvement; the instrument gap remains.
- **discernment: improved** — agree with lane. The lane's own wave falsified C1 wording and C2 K2; both taken: C1 narrowed (amendment 1, 4 residuals routed to r95), C2 filed not verified, missing receipts landed (`controls/*`, forgery collections replace withdrawn `.py` batteries), dead seat recorded as settled-with-deliverables (`MT01ProbeMutants.settlement.md`). C2 counter's semantic blindness (20/38 forgeries bind) disclosed, not papered over.

## Routed defects (lane must fix/write next round; status-neutral on this closure)

- **D1** (prompt fidelity, operator-side): commit-hash citation rule not verbatim in §4 — see §1. Operator driver template: add the hash rule to §4.
- **D2** (carried): `round75-instruments` red — `APPEND_DEBT round=94 events=101 accepted=53 late=26 pending=3 unaccepted=22 bad_rows=19` + late-line-96 hash mismatch (R1; L0 r87/r89 open). `round78-instruments` live-reconcile red — host Ollama on 127.0.0.1:8080 (operator-owned, not lane debt).
- **D3** (routed to round 95 by lane): C1 residuals — work-proportional budget (SC02 F2), count-derived wrapper ceiling (SC02 F3/M10), gate fixture the new probe decides (SC02 F1), `/props` not deciding verdict (SC02 F4); counter coverage M02/M12/M14/M10 + CR01 F3/F6/F7/F8; K1 worded to counter exit condition. C2 R20/R21 (slot count for cli/router-child, `AIP_HTTP_PORT` precedence, `[default]`/`[*]` scoping). M5/M6 process fixes (freeze carries named receipts; predicate quotes literal counter line).
- **D4** (note for operator, not a bar): promotion is operator-owned. Report boxes are all `[~]` (lane-dispatched wave seats are still the lane per LEARNING.md); no promotion review should treat them as `[x]`.

## Admission

`admitted = false`, `verdict = rejected-honest-stop`. C1 and C2 do not verify as filed (honest stops, correctly disclosed); C3 verifies. No axis harmed. This is a rejection for non-verification, not for harm or for a marker — the lane's narrowing, corrections, and disclosed residuals are the deliverable this round.
