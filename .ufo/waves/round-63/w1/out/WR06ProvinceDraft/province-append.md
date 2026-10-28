# WR06ProvinceDraft — landing text for PROVINCE.md, SKILL.md and README.md (round 63)

Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (base). The draft was applied only to a
scratch clone (`fbc3d006eac6485b9a33592246c3bdebcd616cd7`, committed by seat, never landed); no lane
file, lane index, lane commit or fleet file was touched. The exact text is the unified diff in §5 (`province-append.patch`);
`git apply --check` passes at the base tip.

## 1. Missing tokens at the tip (the `province` fact)

Commands (read-only on the lane; reconciler run from the lane's `tools/`):

    python3 tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09

Output (exit 1):

    tip=03a6a1d850902a66a13dfad33f89cf3a8b759a09
    r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False
    detail: province: PROVINCE.md lacks registry/ollama-live-claims-r61.tsv (capability live-ollama-lifecycle)

The province fact reads the canonical list (`canonical list as of round 63`, 12 rows, columns
`Capability | What | Evidence pointer | First-working round`) and checks every backticked
`tools/` or `registry/` token of column 3 for substring presence in PROVINCE.md. I re-ran that
check independently (`canon_check.py`, scratch-only helper copied here; output in `canon-tokens.out`):

    canon rows: 12
    (one line per token, 16 in all; full listing in canon-tokens.out; the only False line at the base tip is:)
    live-ollama-lifecycle              registry/ollama-live-claims-r61.tsv          in_PROVINCE=False

Only one token is missing. The other 15 are present at the tip (`tools/kama-ollama-evidence.py`,
`tools/gguf-identity.py`, `tools/kama-context-capacity.py`, `tools/instrument-agreement.py`,
`tools/pin-watch.py`, `registry/engine-pins.tsv`, `tools/digest-ledger.py`,
`registry/digest-ledger.tsv`, `tools/hexrun-census.py`, `registry/hexrun-ledger.tsv`,
`tools/append-only-audit.py`, `registry/append-only-contract.tsv`, `tools/kama-live-replay.py`,
`tools/kama-llamacpp-live.py`, `tools/kama-ollama-live.py`). The round-60 note at PROVINCE.md:189 cites `tools/kama-ollama-live.py` and `registry/ollama-live-pin.tsv` but not the round-61 claim registry, which is the one missing token.

## 2. Readme fact

Reconciler `readme=0` at the base tip. Independently: every non-dot top-level entry of
`git ls-tree --name-only 03a6a1d8` (AGENTS.md, LOG.md, MINT.md, PROVINCE.md, README.md, SCORECARD.md,
SHONEN.md, SKILL.md, considerthese, corpus, plans, registry, tests, tools) is backticked in README.md.
No README addition is required by the reconciler. The draft refreshes two README bullets
(`registry/`, `tools/`) so the v2 completion plane and the claim registries are named there; that is
documentation only and is marked optional in §3.

## 3. What the draft changes (insertion anchors at the tip)

- **PROVINCE.md, Owns table:** one new row inserted after line 17 (`lane instruments`). It names
  `registry/ollama-live-claims-r61.tsv` (closes the province fact), `tools/kama-completion-live.py`
  (schema v2), `tools/round63-c1-counter.py`, `tools/round63-c2-counter.py` and
  `registry/capability-claims-r63.tsv`.
- **PROVINCE.md, tail (after line 188):** a Round-61 note (live-ollama-lifecycle admitted in the
  round-62 canonical list at first-working round 61; supersedes the round-60 "no capability admitted"
  sentence without deleting it), an appended correction (the round-60 pointer `.ufo/l0-questions.md`
  does not resolve at the tip; see §6), and a Round-63 note on the `POST /v1/completions` request plane
  and the round-63 counters. The Round-63 note is outcome-neutral: it states that
  `live-completion-request-plane` enters the canonical list only if the C1 counter reports `met=True`.
  It records no measured verdict, because none is known to this seat.
- **SKILL.md (after line 1641):** a new section `## Round-63 completion request plane and claim registry
  (owner: kama)`: the tool's options and exit map, a three-row table (question, command, exit/output,
  boundary) for the tool and the two counters, the claim-registry columns and placeholder meanings,
  and the freeze pointer. No existing SKILL line is changed.
- **README.md (optional, lines 24 and 26):** the `registry/` and `tools/` bullets gain the round-61/62/63
  claim registries and the three live fixtures. The reconciler does not require this.

## 4. Consequence for the round-41 head facts (must land with the draft)

The reconciler's `r41` counter (imported unchanged, `tools/round41-scorecard-reconcile.py`) pins
SHA-256 values and line counts of SKILL.md and PROVINCE.md in the SCORECARD round-41 head table.
The base values match the base files; the draft changes both files, so the `r41` count rises:

| Fact pinned in SCORECARD (round-41 head) | Base value (tip 03a6a1d8) | Draft value (fbc3d006) |
|---|---|---|
| `SKILL.md` sha256 (depth row) | `ea303f2dcb84…` | `d02efe119d14…` |
| `SKILL.md` lines (depth row) | 1641 | 1655 |
| `grep -c '^## ' SKILL.md` (depth run) | 44 | 45 |
| `PROVINCE.md` sha256 (coverage row) | `a60591b77ac8…` | `b65e31fe43dd…` |
| `PROVINCE.md` lines (coverage row) | 188 | 197 |

Measured on the draft tip: `r41=6 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=0 rel=0 mismatches=12`.
Five of the six `r41` details are the new values above; the sixth (`coverage run ... no stdout line == '36'`) is
present at base too and is not caused by this draft. The head table must be re-derived in the same landing
(the freeze already assigns the head re-derivation to the L1 after measurement). If the L1 wants the
SKILL section and the PROVINCE tail held back, the Owns row alone (`province=0`) moves the total to 9
(`r41=3`: PROVINCE sha and lines plus the base coverage fact), not 8.

Full digests are kept out of this document; the reconciler receipts in this directory carry them.

## 5. Exact landing text (unified diff against 03a6a1d8)

Applies with `git apply province-append.patch` at `03a6a1d8` (checked with `git apply --check` in a
fresh scratch clone).

```diff
diff --git a/PROVINCE.md b/PROVINCE.md
index dad4d473..f546eadd 100644
--- a/PROVINCE.md
+++ b/PROVINCE.md
@@ -15,6 +15,7 @@ drift, served-model reconciliation, probe conventions.
 | endpoint-drift detection + invocation history | `tools/kama-probe.sh snapshot`, `registry/endpoint-consumers.tsv`, `registry/history/{latest.tsv,DELTA.md}` |
 | endpoint-consumers cross-lane registry | `corpus/knowledge/consumer-registry.md`, `cross-lane-scope.md` |
 | lane instruments (the capability repertoire, `SCORECARD.md` canonical list) | `tools/kama-ollama-evidence.py` (offline Ollama capture replay), `tools/gguf-identity.py` (GGUF declared identity), `tools/kama-context-capacity.py` (fixture context-capacity receipt), `tools/instrument-agreement.py` (run agreement), `tools/pin-watch.py` with `registry/engine-pins.tsv` (newer-release triggers for the pinned SGLang, vLLM and llama.cpp lines), `tools/digest-ledger.py` with `registry/digest-ledger.tsv` (classification of every SHA-256 the lane's documents cite), `tools/hexrun-census.py` with `registry/hexrun-ledger.tsv` (classification of every other 32-127 character hex run: git object ids, MD5 sums, over-long or abbreviated runs; round 43), `registry/staged-refusals.tsv` (staged package items the lane refuses, with rounds offered, reason and flip; round 43); `tools/append-only-audit.py` with `registry/append-only-contract.tsv` and `tools/round47-append-audit-v2-check.py`, `tools/round48-append-audit-v3-check.py` (append-only audit of the contract-declared self-description set: every commit deleting >= 20 lines from one of those files, with a deleted count equal to git numstat, the largest share of those lines any commit in the event's window holds again and the commit that restored them; round 46, v2 round 47, v3 round 48 with per-row regions, binding declarations and `regressed` in the exit semantics); `tools/kama-live-replay.py` (re-acquire a live receipt's server archive and model from the URLs its provenance records, verify both sha256 values, re-run the lifecycle and compare every check; round 47) |
+| live serving request planes and their claim registries (round 61 `live-ollama-lifecycle`; round 63 `POST /v1/completions` receipt v2 and the capability-claim bindings) | `tools/kama-ollama-live.py` with `registry/ollama-live-pin.tsv` and `registry/ollama-live-claims-r61.tsv` (the lane-owned Ollama v0.40.11 child on an unregistered loopback port with a scratch HOME and model store; registered consumers are not contacted); `tools/kama-completion-live.py` (the lane-owned `/v1/completions` request plane on the pinned b11755 fixture, receipt schema `kama-completion-live/v2`); `tools/round63-c1-counter.py` and `tools/round63-c2-counter.py` (round-63 counters, exit 0 iff `met=True`); `registry/capability-claims-r63.tsv` (each canonical capability bound to the run template that re-executes its evidence at the tip) |
 
 **Observed state (lane baseline `c390918`, tracked snapshot `20261014T124232Z`):**
 `bash tools/kama-probe.sh check` evaluates 3 registry rows — `model_ok=0`, `drift=3`,
@@ -186,3 +187,11 @@ endpoint or runtime was sampled.
 **Round-43 note - the hex-run census and the health process map (2026-10-25).** `tools/hexrun-census.py` reads git objects and committed documents only; for an `upstream` ledger row it reads a committed evidence file, never the network, so the GitHub API queries that produced the evidence ran once, in round 43, by `gh api` under the operator's authenticated session, and are not part of the tool. `corpus/knowledge/runtime-health-surface-processes.md` is a source reading of two GitHub API objects (S480, S481); it names which vLLM process answers `/health` and samples no endpoint. The adjacent processes the staged round-13 amendment names (the agentic-api gateway, the Semantic Router) stay refused: a gateway and a route-selection product are dispatch-side surfaces (`corpus/knowledge/cross-lane-scope.md`), reported to the owning lane, not absorbed.
 
 **Round-60 note — live Ollama lane-owned sample, not a registered consumer (2026-10-27).** `tools/kama-ollama-live.py` and `registry/ollama-live-pin.tsv` add a v0.40.11 child-process instrument and source-grounded captured observations (`corpus/knowledge/ollama-live-lifecycle.md`; S519–S523). The single receipt uses the lane's fixture GGUF and an unregistered loopback port under a scratch HOME/model store; it neither contacts nor changes the three registered consumers, whose last recorded state remains `DEAD`. This is not service restoration, readiness for configured consumers, model quality or general Ollama behavior. The round's claim/counter was falsified: no `live-ollama-lifecycle` capability is admitted, and child cleanup after SIGKILL remains a defect. Extending the existing lane-owned unregistered-child exception from llama.cpp to Ollama remains pending operator decision at `.ufo/l0-questions.md` (`kama | round-60`).
+
+**Round-61 note — `live-ollama-lifecycle` re-claimed under the v2 harness (2026-10-28).** `tools/kama-ollama-live.py` v2 adds `--hold-dir` outside contact, `pdeathsig` on the child, graded `/api/show` and the `child_pre_dead` teardown record. Its claim rows are in `registry/ollama-live-claims-r61.tsv`, counted by `tools/round61-c1-counter.py` and `tools/round61-c2-counter.py`, with receipt `.ufo/waves/round-61/live/receipt.json`. The round-61 record states that these changes close the round-60 falsification classes. The capability is in the round-62 canonical list at first-working round 61. This supersedes the round-60 note's statement that no `live-ollama-lifecycle` capability is admitted. The held ground is the lane-owned child only: the pinned Ollama v0.40.11 binary, the lane's GGUF fixture, an unregistered loopback port, and a scratch HOME and model store. A hold-window contact proves that one port is live; it does not prove registered-consumer health. The three registered consumers are not contacted and keep their recorded `DEAD` state.
+
+*Appended correction, round 63:* the round-60 note's pointer `.ufo/l0-questions.md` does not resolve at tip `03a6a1d8` (`git cat-file -e` fails, and the file is absent from the working tree). The operator decision it names is not recorded in this tree; this note neither reopens nor closes it.
+
+**Round-63 note — `POST /v1/completions` request plane (receipt v2) and the round-63 claim registry (2026-10-28).** `tools/kama-completion-live.py` (schema `kama-completion-live/v2`) is the lane's request-plane fixture for the pinned llama.cpp b11755 build: it starts its own digest-pinned llama-server child on a free unregistered loopback port, sends one `/v1/completions` request, a malformed request and an identical second request for the determinism check, and records captured headers, body bytes and request bytes with their sha256. `--hold-dir` opens an outside-observer window: the child stays up for outside contact until a release file appears in that directory, and `hold.released` is recorded only if it did. `tools/round63-c1-counter.py` (C1, operability) re-derives the receipt from captured bytes, makes its own outside request during the hold window, and credits the 44 targeted controls only when each is rejected by the check it names within the collateral cap. `tools/round63-c2-counter.py` (C2, calibration) binds each of the twelve canonical capabilities to a run template in `registry/capability-claims-r63.tsv`, re-executes it at the tip, and requires `tools/round42-selfdesc-reconcile.py` to report `mismatches=0`. The round-62 counters are not amended and remain the round-62 honest-stop record.
+
+The round-63 canonical list keeps the round-62 twelve rows. `live-completion-request-plane` enters that list only if the C1 counter reports `met=True`. The `/v1/completions` frontier named in the round-31 and round-32 notes above is narrowed to the lane's pinned fixture and to the extent of that verdict. What the request plane shows is one loopback fixture's answer to one request: not model quality, not text content (no check asserts the generated text), and not served identity or health of a registered consumer.
diff --git a/README.md b/README.md
index f88ae8d9..6d4a49ed 100644
--- a/README.md
+++ b/README.md
@@ -21,8 +21,8 @@ under the [shokunin skill](https://github.com/VeigaPunk/shokunin).
 - `considerthese/` — operator-authored daily reflections; mined one proposal per round, never edited
 - `corpus/` — the lane's memory: `knowledge/` entries, `lessons/`, `SOURCES.md` registry, `QUALITY.md`, coverage map and frontier in `corpus/README.md`
 - `plans/` — early planning notes
-- `registry/` — registered consumers and invocation history, outcome registries, `engine-pins.tsv`, `digest-ledger.tsv`
+- `registry/` — registered consumers and invocation history, outcome registries, `engine-pins.tsv`, `digest-ledger.tsv`, the live-run pin and claim rows (`ollama-live-pin.tsv`, `ollama-live-claims-r61.tsv`) and the per-round capability claim registries (`capability-claims-r62.tsv`, `capability-claims-r63.tsv`)
 - `tests/` — fixtures and regression suites for the probe and the live-fixture tools
-- `tools/` — the probe, the instruments and the per-round counters (`tools/round<N>-*.py`)
+- `tools/` — the probe, the instruments, the live fixtures (`kama-llamacpp-live.py`, `kama-ollama-live.py`, `kama-completion-live.py`) and the per-round counters (`tools/round<N>-*.py`)
 
 The listing covers non-hidden top-level entries only: the hidden `.gitignore` names the paths git ignores (`.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`), and the hidden `.ufo/` directory holds the round work directories `round-5/`–`round-10/`, `reports/` (the round-5 report) and `waves/` (`round-11/`–`round-43/`).
diff --git a/SKILL.md b/SKILL.md
index bdedba14..ce059518 100644
--- a/SKILL.md
+++ b/SKILL.md
@@ -1639,3 +1639,17 @@ predicates and counter sha256s: `.ufo/waves/round-55/preregistration.json`; rece
 |---|---|---|---|---|
 | Round-55 C1 replay-code audit (frozen round-54 counter) | measurement: `python3 tools/round54-replay-code-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | as the round-54 registry row, plus `envnames=N/3 hostlibs=N/3 anon=N twopass=N/3 rehash=N`; base `3a600d2f` (newrow re-pointed at S511), frozen sha256 `c81fe971…79af` | no selftest; kill battery `.ufo/waves/round-55/c1/battery/run-battery.py` (control + 3 live kills + 1 vector analysis) | read-only |
 | Round-55 C2 cited-path check (frozen round-54 counter, `superseded` class) | measurement: `python3 tools/round54-cited-path-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | as the round-54 registry row with `scenarios=N/15` (superseded honest/forged pair added); counter BASE stays `0b75a84c` (drop horizon); frozen sha256 `d70a1729…6510` | fifteen constructed scenarios incl. the superseded pair; ledger classes add `superseded` | read-only |
+
+## Round-63 completion request plane and claim registry (owner: kama)
+
+`tools/kama-completion-live.py --work DIR --out RECEIPT` runs one lifecycle on the lane's pinned llama.cpp b11755 fixture: its own digest-pinned `llama-server` child on a free unregistered loopback port, then `/health`, `/v1/models`, `/props`, `POST /v1/completions`, `POST /tokenize`, a malformed POST graded for a well-formed error, and an identical second POST for the determinism check. Options: `--hold-dir DIR --hold-timeout S` open an outside-observer window (the tool writes `hold.json` there and records `hold.released` only if a release appeared inside the window), `--nonce STR`, `--port N`, and `--model PATH --model-sha256 HEX` (digest verified before use). Exit 0 `REQUEST_OK` (every evaluated check passed); 1 an evaluated check failed; 2 setup error, not evaluated, or internal fault. The receipt schema is `kama-completion-live/v2`.
+
+| Question | Command | Exit / output | Boundary |
+|---|---|---|---|
+| Does one request-plane lifecycle answer correctly on the fixture? | `python3 tools/kama-completion-live.py --work DIR --out RECEIPT` | 0 `REQUEST_OK`; 1 an evaluated check failed; 2 not evaluated | One loopback fixture and one request set; text content is never asserted; registered consumers are not contacted |
+| Does the receipt re-derive from captured bytes, with an outside request inside the hold window? | `python3 tools/round63-c1-counter.py --repo REPO --tip REV --work DIR` | one line; exit 0 iff `met=True` | Tip read from git objects, never the working tree; a control counts only when its named check fails within the collateral cap (5 failing checks; 30 for the envelope break) |
+| Is each canonical capability's evidence re-executed at the tip, and is the check sensitive? | `python3 tools/round63-c2-counter.py --repo REPO --tip REV --work DIR` | one line; exit 0 iff `met=True` | `context-capacity-receipt` may end `host-busy` (exit 2, `host-not-idle-before-K1`), one of its two declared outcomes; the counter requires `tools/round42-selfdesc-reconcile.py` at `mismatches=0` |
+
+`registry/capability-claims-r63.tsv` has one row per bound capability with columns `cap`, `quote`, `binding`, `run`, `pattern`, `verdict`, `observed`, `note`. `run` is the command template, where `%T` is the tip tree, `%S` the scratch directory, `%R` the repository and `TIPREV` the tip revision. The counter executes each `run` in an allowlisted environment (`PATH`, `HOME`, `LANG`, `LC_ALL`, and `TMPDIR` set to the scratch directory), recomputes the verdict from live output, and treats `observed` as a recorded claim to check, never as evidence. `verdict` is `true` for every row except `context-capacity-receipt`, which records `host-busy`.
+
+The round-63 claim freeze is `.ufo/waves/round-63/controls/freeze.txt`. The round-62 counters `tools/round62-c1-counter.py` and `tools/round62-c2-counter.py` are not amended and remain the round-62 honest-stop record. The request plane enters the canonical capability list only through a C1 `met=True` measured at the landed tip; the freeze records that a relabelled v1-schema tool is rejected by that counter (`controls/c1-relabel.txt`).
```

## 6. Open items for the L1 (not drafted here)

1. **Dangling pointer in PROVINCE.md (base defect).** The round-60 note cites `.ufo/l0-questions.md`.
   `git cat-file -e 03a6a1d8:.ufo/l0-questions.md` fails and `ls .ufo/l0-questions.md` fails in the
   working tree. The draft appends a correction line; it does not restore or reword the file. Whether the
   operator decision still exists is for the L1 to establish.
2. **Round-41 head values** (§4) must be re-derived in the same landing as SKILL.md and PROVINCE.md, or the
   `r41` count stays at 6 (9 with the Owns row alone).
3. **Pre-existing `r41` coverage fact.** `coverage run ... no stdout line == '36'` fails at base and at the draft tip.
   It is not caused by this draft and is outside the province/readme items.
4. **Other head facts still failing** (not drafted): banner (`Latest measured round: 63`), `### Planned (round 64)`,
   Retired (`12 capabilities`), Saturation (`first-working rounds ...`), and the head Capabilities table, which lists
   11 names against the 12-row round-63 canon (`live-ollama-lifecycle` missing from the head table).
5. **Measured verdict sentence.** `live-completion-request-plane` is not in the round-63 canon by freeze. The
   Round-63 PROVINCE note is outcome-neutral. After C1 and C2 are measured, the L1 may add one sentence
   stating the verdicts; this seat does not know them and wrote none.
6. **Cited-path check (`tools/round54-cited-path-check.py`)** reports `met=False` at base (`bad=1`, `dropped=1`);
   the draft tip reports the same findings, with `cited` 744 to 749 and no new unresolved entries.
   Pre-existing, not caused by this draft.
7. **Digests in this directory.** `reconcile-*.out` and `cited-path-*.json` contain full SHA-256 values printed by the
   tools. If the L1 commits these receipts, run `tools/digest-ledger.py scan` and `tools/hexrun-census.py scan` on the
   resulting tip. The draft tip itself scanned clean (`unknown=0`).

## 7. Tally

    province_missing=1 (registry/ollama-live-claims-r61.tsv)  base: province=1 mismatches=8 met=False
    draft fbc3d006: province=0 readme=0 r41=6 mismatches=12 maxN=63 met=False (r41 +5 from pinned SKILL/PROVINCE values; see §4)
