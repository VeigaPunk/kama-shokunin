# Round 63 non-author closure spot-check — kama

author: hyaku closure (non-author integrator, @m_zfl)

Lane-round: kama 63. Lane HEAD before `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`, after `7a0e49f80efc989f288ef7b46d4914c5d415846a`. Report under check: `.ufo/reports/round-63/kama.md` (fleet commit `72c7713ef48cd5d5d02964ece2975602e3402a08`). I did not author this round; I wrote only this file. Reviewer role: non-author integrator of record.

**Verdict: `rejected-honest-stop`, `admitted=false`, status `ok`.** C1 is falsified by the lane's own wave (and the lane says so); C2's frozen predicate is met on committed evidence but its discriminating power is not shown, so no axis moves. No axis is harmed.

Dispatch digest (`.ufo/watchdog.log`, copied because the log is mutable):
`2026-10-28T18:36:06-03:00 launch kama round=63 pgid=2237173 driver=hyaku-inline attempt=1`;
`2026-10-28T20:32:14-03:00 complete kama round=63; hyaku-inline attempt=1`.

## 1. Step-1 conformance

| Check | Command / observation | Result |
|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-63/kama.md` → `kama-shokunin 72c7713ef48cd5d5d02964ece2975602e3402a08` (committer date 20:30:56, after lane tip committer date 20:30:00; "lands last" holds) | ok |
| SHONEN heading | `grep -c '^## SHONEN'` → `1`, four `[~]` lines (one per SHONEN box, author-asserted) | ok |
| cited commits exist and are ancestors of `master` | `git cat-file -t` → `commit` and `git merge-base --is-ancestor <h> master` true for `675cac02…`, `03a6a1d8…`, `f7f1b378…`, `7a0e49f8…`, base `7ee8cbdf…` | ok |
| pushed, clean | `jj-lane.sh state` → `branch=master local=7a0e49f8… remote=7a0e49f8… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty; `git ls-remote origin refs/heads/master` → `7a0e49f80efc989f288ef7b46d4914c5d415846a` | ok |
| prompt carries template contract | `.ufo/prompts/kama-round-63.md` (689 lines): 1–3 claims, lowest axis, ≥8 L2 batch, §2b frontier step, report path, SHONEN requirement, hash-citation rule, L0 channel, census command all present (grep) | ok |
| sections | Sources & frontier, Trend verdicts, Stale-lane all present in the report | ok |
| wave | 61 seat reports in `.ufo/waves/round-63/w1/*.md`; report states 64 seats, 3 scouts dead on a provider error (I cannot re-open the provider message; the 3 items are accounted for in the lesson Gate) | consistent |

Conformance defects (status-neutral): (a) the report's author date (20:19:14) predates the lane tip's commit date (20:28:33 author, 20:30:00 committer) while the committer date follows it; the report cites the final pushed hash correctly, so ordering holds on committer time. (b) The freeze amendment 1 moved the C1 evaluator before the wave and is disclosed in `controls/freeze.txt`; the counter sha256 at `675cac02` (`6ffb4c80…`) differs from the sha256 at `03a6a1d8`/`f7f1b378`/`7a0e49f8` (`35af5c98…`, identical across the last three — no instrument change after the wave), and `round63-c2-counter.py` is `a5c83ea9…` at all four. (c) `considerthese/2026-10-26.md` could not be located at the fleet-root path I tried, so I did not re-open it (see §4).

## 2. Per-claim re-check

Method note: C1 and C2 both rest on lane-owned counters that start live servers or execute the tip's own tools. Per PROTOCOL §Gate standard (Closure consequence) I did not execute them; I verified their committed evidence and re-measured the plain facts around them.

### C1 — operability, strict outside-bound live request plane (lane verdict: falsified)

| Item | Observed | Basis |
|---|---|---|
| Base (red-before) | `.ufo/waves/round-63/controls/c1-base.txt`: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False`, exit 1, v1 tool rejected for missing checks | evidence-verified |
| Tip | `.ufo/waves/round-63/measured/c1-final.out`: `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True` | evidence-verified (tip `f7f1b378…` in `measured/final.tip`) |
| Counter bytes after the wave | `git show <c>:tools/round63-c1-counter.py \| sha256sum` identical at `03a6a1d8`, `f7f1b378`, `7a0e49f8` | re-measured |
| Falsification | `w1/MT15C1FakeConsistent.md` plus receipts: `w1/out/MT15C1FakeConsistent/forge.out` and `sleeper.out` both `met=True 44/44 eval_selftest=3/3 errors=0` (rc=0); `forge-A-realchild.patch` (7265 B), `forge-B-sleeper-delta.patch` (1941 B) committed; `sleeper-serverlog.txt` (58 B) reads `sleeper server.log bytes: 0` — a seat-written note, so forgery B's "no llama-server ran" rests on the seat's receipt, not on a log I could re-observe | evidence-verified |
| Mechanism check | `grep -c '/exe' tools/round63-c1-counter.py` → `0`; counter obtains ownership via `live_mod.port_owned_by(pid, port)` (line 358) where `live_mod` is `load_live_mod(tool_path)` loaded from the tip (lines 365, 399, 669) — the answering process is never bound to the pinned binary and the helper comes from the tree under judgment | re-measured by grep |

Ruling: the predicate sentence says the listener "is the receipt's child" on the "pinned llama.cpp fixture"; the counter satisfies "is the child" with an inherited socket fd and does not check that the process is llama-server. Two forged clones pass the frozen counter. The claim does not verify. The lane agrees (SCORECARD "Round-63 measured results": "falsified by the round's own wave"). The v2 tool's proxy-leak fix (EX06: round-62 tool leaked both POSTs, v2 made 0 proxy connections) is a real but unclaimed side effect; it is not an admitted improvement. Capability `live-completion-request-plane` correctly did not enter the table.

### C2 — calibration, 12 capabilities bound to live runs, sensitivity that can fail, self-description reconciled

| Item | Observed | Basis |
|---|---|---|
| Base | `controls/c2-base.txt`: `error: registry absent … would be 0/12`, exit 1 | evidence-verified |
| Shortcut control | `controls/c2-shortcut.txt`: `mismatches=2 … selfdesc_mismatches=8 sens… controls_rejected=0/12 met=False`, "baseline not met - control credit withheld (would be 12/12)", exit 1 | evidence-verified |
| Tip | `measured/c2-final.out`: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True`, exit 0 | evidence-verified |
| Reconciler | `measured/reconcile-final.out`: `tip=f7f1b378… r41=0 banner=0 … province=0 rel=0 mismatches=0 maxN=63 met=True` | evidence-verified |
| Plain facts the reconciler asserts | `PROVINCE.md` sha256 `bd1afe5e…` and 190 lines match the SCORECARD coverage row; `SKILL.md` sha256 `ea303f2d…` 1641 lines match; `ls corpus/knowledge/*.md \| grep -v 'engine-sides\|processes' \| wc -l` → `38` matches the new "38"; `wc -l registry/capability-claims-r63.tsv` → `13` (header + 12 rows); SCORECARD §Round 63 canonical list has 12 rows | re-measured |
| Wave survivors | KR03 S1/S2, KR02 X/Y/F (the counter runs the tip's own tools and reconciler, so a tip tool that prints the frozen string passes); MT20 (8-character quote floor, no control), MT21 (no control exercises the reconciler conjunct), RV03 F1 (reused `--work`), RV04 D1 (idle outcome of the context-capacity row scores a mismatch); the lane lists them in its lesson §Wave results and SCORECARD "What `met=True` does not show" | evidence-verified from seat reports named in the lane lesson |
| New observation (mine) | the SCORECARD calibration row (line 18) still says "latest outside closure `corpus/lessons/round-57-verifier-spotcheck.md` (rejected-honest-stop), including round 57"; `ls corpus/lessons/*verifier-spotcheck.md` lists closures through `round-62-verifier-spotcheck.md` (this file adds 63). The row is unchanged from base (`git diff 7ee8cbdf 7a0e49f8 -- SCORECARD.md`) and the reconciler reports 0, so the very self-description C2 claims "reconciled" still carries a pointer five closures stale. [INFERENCE: the round-59 counter's `latest outside closure` pointer may be defined over a fleet ref; either way the row misstates the corpus a reader sees.] | re-measured by `ls`/diff |

Ruling: the frozen predicate is met on committed evidence (red-before receipts show the fix is the only delta, `sens_selftest=4/4`, MT17 killed the old formula), but (i) the lane's own wave shows the counter certifies tip-tree tools by running them and leaves the reconciler conjunct and the quote floor without a control, and (ii) a stale calibration cell survives the 0-mismatch reconciler. Calibration is not shown to improve; the score stays 7 (the lane also keeps 7 and says "no claim is admitted by its author"). Because C1 does not verify, the round cannot be admitted in any case.

### SCORECARD diff (owned axes not harmed)

`git diff 7ee8cbdf 7a0e49f8 -- SCORECARD.md`: scores unchanged (operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7); the head banner, §Planned pointer, §Retired (12 capabilities), §Saturation, coverage-row evidence (36→38 files, PROVINCE sha/lines) and a new §Round 63 section were changed; the Capabilities mirror gained `live-ollama-lifecycle` (a round-61 row correctly carried to the mirror; no round-63 row). No score went down and no evidence cell lost a pointer.

## 3. Per-axis verdicts

| Axis | Verdict | Evidence |
|---|---|---|
| operability (assigned; C1) | **unchanged** | C1 falsified (MT15: two forgeries pass 44/44); score held at 8 |
| calibration (assigned; C2) | **unchanged** | frozen predicate met on committed evidence but the counter's discrimination is not shown and the calibration row keeps a stale latest-closure pointer; score held at 7 |
| freshness | unchanged | not claimed; SCORECARD row untouched |
| depth | unchanged | `SKILL.md` byte-identical (sha256 `ea303f2d…`) |
| coverage | unchanged | no new coverage-map ground; row evidence re-derived (38 files verified) |
| adjacency | unchanged | not claimed; row untouched |

No exploratory claim was declared. No axis `harmed`.

## 4. Discernment spot-check (LEARNING.md)

Sources re-opened by me on 2026-10-28 (raw bytes fetched with `curl`):

| Item | Decision | Re-opened source | agree/disagree | Reason |
|---|---|---|---|---|
| S527 llama.cpp `server-task.cpp` @ `704366d7…` | admit | `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-task.cpp`; sha256 `4c3f413b…233495` equals the row's | agree | lines 374–377 read `json finish_reason = "length"; if (stop == STOP_TYPE_WORD \|\| stop == STOP_TYPE_EOS) { finish_reason = "stop"; }`; `usage_json_oaicompat` at 357–364 holds completion_tokens/prompt_tokens/total_tokens/`prompt_tokens_details.cached_tokens`; `to_json_oaicompat` starts at 366; tier A pinned code for the scope |
| S528 `server-common.cpp` @ `704366d7…` | admit | same repo path `…/tools/server/server-common.cpp`; sha256 `b4f4aae7…954d442` equals the row's | agree | lines 148–149 read `{"predicted_n", n_gen}, {"predicted_ms", t_gen_ms()}`; surrounding block lists the `timings` field names; tier A, scope limited to field names |
| `/tokenize` README reading, no new row | reject (same-scope duplicate) | S526's pinned `tools/server/README.md`; sha256 `714c067b…a75a6a37` equals S526's | agree | line 692 reads "`add_special`: (Optional) Boolean indicating if special tokens, i.e. `BOS`, should be inserted.  Default: `false`"; same URL as S526, so a second row would duplicate it |
| quarantine S210 (`Page Not Found`) | reject | `https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide` (HTTP fetch 1,308,980 bytes) | agree | `grep -ci 'page not found'` → `0`; quote absent |
| quarantine S211 (`still-live`) | reject | `https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-…引擎.md` (587 lines) | agree | `grep -ci 'still-live\|still live'` → `0` |
| quarantine S224 (`render-only servers always return 200`) | reject | `https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/` (386,143 bytes) | agree | the only `render` hits are `renderers/` navigation links; `always return` not present; `check_health` appears once; quote absent |
| `considerthese` suggestion 3 reversal (shortcut tally exists) | admit reversal | `git log --diff-filter=A -- tools/shortcut-tally.py` → `c4b2175d round-48…`; `measured/shortcut-tally-r55-62.out` | agree on the premise; source file not re-opened | the tool exists since round 48 and prints `no-disclosure` for rounds 56–62; I did not locate `considerthese/2026-10-26.md`, so the suggestion text itself is not re-verified |

Newly written `corpus/SOURCES.md` rows re-opened: S527 and S528 (above). Their quotes are ≤25 words and located in the fetched bytes. `git show <c>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`: base `266`, tip `268`; matches the report. `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, `ok` on `corpus/SOURCES.md`, W04 cross-scope duplicate-URL warnings only (S524, S526, S528), no E-codes.

Agreement on admits (2/2 rows + 1 no-row decision) and rejects (3/3 quarantine rows). Defect to learn: none from the gate. The lane's own note that its checker split two-literal strings across lines (S202/S206/S230 present) is consistent with SC04's findings; I did not re-open those three.

## 5. Trend verdicts

- **expansion: unchanged.** S527/S528 are two correct tier-A rows that move response fields inside the already-held `completion-request-plane` entry from observation to source-backed (entry `source:` line cites S526; sections cite S527/S528: `grep -c 'S527\|S528'` → 6) but no new coverage-map row or capability entered and C1 is falsified.
- **quality: improved.** The round-62 vacuities have committed red-before receipts (`c2-shortcut.txt`, `c1-mutants-prewave.txt`), the knowledge entry gained a per-field grading section, and QUALITY gained KQ102–KQ106 (`git diff … -- corpus/QUALITY.md` shows all five). Open flaws are recorded rather than left unmarked (KR06's unsupported `completion_fingerprint` bound, MT12 ENVELOPE_CAP). No admitted entry failed my re-check.
- **discernment: improved.** My spot-check agrees with the lane's gate on both admits (S527, S528) and rejects (S210, S211, S224, plus the no-duplicate-row decision), so the lane's self-graded `unchanged` ("no non-author spot-check on record") is superseded by this file.

## 6. Routed defects (lane fixes next round)

1. **C1 counter provenance** — the round-64 plan already names it (`/proc/<pid>/exe` re-hash, argv, a counter-owned hold window, replay of the round-63 forgeries). Additionally load `kama-llamacpp-live.py` from the counter's own tree or pin its sha, so a tip clone cannot redefine `port_owned_by` (MT15 "helper provenance", [INFERENCE: untested by the seat]).
2. **SCORECARD calibration row stale** — update "latest outside closure … round-57 … including round 57" to the actual newest closure and make the reconciler fail on it (observed here: closures exist through round 62/63).
3. **C2 counter** — add controls for the reconciler conjunct and the quote floor (MT20/MT21), pin each bound tool and the reconciler by sha256 or run a planted regression copy, accept the idle `context-capacity-receipt` outcome (RV04 D1), refuse a reused `--work` tip tree (RV03 F1).
4. **`tools/shortcut-tally.py`** — extend to the round-56-to-63 report format (it prints `no-disclosure` for rounds 56–62).
5. **KR06** — `completion_fingerprint` 9–40 hex bound is not source-backed (a 7-character `git rev-parse --short` would false-fail).

## 7. Notes for the operator

SHONEN boxes are not fully checkable by a non-author from this round: SKILL.md was unchanged, the end-to-end task's live outcome is falsified, and executable-without-oral-context review is open. No `[x]` written; no promotion, mint, or other-lane action taken.
