VERDICT: partial — refused-count repair confirmed on round-18's own 95-refusal artifact (frozen 0 → current 95) with no fleet file changed, but the producer-shape note's integer branch presumes a producer-side count that no existing producer write carries, and the delivered C2 counter has no committed full run (its artifact binds c6dc46f/2af03fed; lane master is 1c325b2/87cad1ca).

Seat: KamaR18.ConnectKumitate-3 (round-18 falsify, connector). Item: cross-axis overlap — refused-count correction and producer-shape offer to kumitate; no fleet tooling ownership absorption. Read bound honored: only `/home/vgpnk/Projects/shokunin/kumitate-shokunin/SKILL.md` and `/home/vgpnk/Projects/shokunin/kumitate-shokunin/corpus/README.md` were opened on the kumitate side; lane evidence was read in the clone `/tmp/kama-r18-falsify-ConnectKumitate/repo` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Advice only: nothing edited, admitted, integrated, judged or shipped. No official full counting invocation was run against the live lane; the mode-2/selftest/family-d runs below executed in the clone.

## Axes

- Calibration (declared lowest, 7): primary. The refused-count survivor is one of C2's named set (`corpus/lessons/round-18.md:22,134,175`), and the L1 hand-off to kumitate is part of that statement's scope.
- Operability (8): no-harm. Nothing here touches `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/`, a port, or a live run.

## Evidence

### 1. The correction is the committed file, and its selftest is green

- `git -C /tmp/kama-r18-falsify-ConnectKumitate/repo rev-parse HEAD` → `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
- `sha256sum .ufo/waves/round-18/dispatch-provenance.py` → `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f`, identical to the C2Provenance delivery record (`.ufo/waves/round-18/build/advice/C2Provenance.md`, "Delivered files").
- Refusal path: predicate at `.ufo/waves/round-18/dispatch-provenance.py:178-179` (`REFUSED_TASK_RE`), observation at `:411-422`, precedence at `:502-503` (prose count wins over the legacy tally; empty observation falls back to the tally).
- `PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` → `selftest: 30/30 checks passed`, exit 0. The refusal checks are at `:797-813` (distinct-label dedupe, mixed refused+spawned) and `:866-867` (parseable-empty → 0).

### 2. Round-18's own refusal is a correct 95/0 — and the frozen tool is still 0

Input: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/refused-result-1.json`, sha256 `83533c134a04ddab64771a02e3b7e41ab2fc89740dbc57ff219609e6e664d6cf`. Keys are `text`, `details`; `details` is `{'projectAgentsDir': None, 'results': [], 'totalDurationMs': 0}`. The phrase `Background job limit reached` occurs 95 times; the regex yields 95 matches, 95 distinct labels, 0 duplicates.

Executed in the clone (each `--out` under a fresh `/tmp/kama-r18-falsify-ConnectKumitate/exp.*` path):

- current (`dispatch-provenance.py --attempt-result <file> --label refused`) → exit 0, entry `refused: 95`, `spawned: 0`, `spawned_method: null`, `parseable: true`, `result_sha256: 83533c…`.
- frozen round-17 copy (`--attempt-result` same file, `.ufo/waves/round-18/frozen/round-17_dispatch-provenance.py`, sha256 `11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df`, matches `.ufo/waves/round-18/frozen/SHA256SUMS:3`) → exit 0, `refused: 0`, `spawned: 0`, same `result_sha256`.

This converts the build seat's `[INFERENCE]` at `.ufo/waves/round-18/build/advice/ConnectKumitate.md:25` into an observed before/after pair on the round's own evidence.

### 3. The official C2 arm pins only the 82 — and the committed artifact binds the parent counter

- `c2/survivors.py:170-178`: `EVIDENCE["refused-result"]` is round-17's file (`7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c`), `EXPECTED_REFUSED = 82`; family d runs both sides at `:1294-1338`.
- Delivered counter reproduced at the pinned revision: `python3 .ufo/waves/round-18/c2/survivors.py --family d --json --out <fresh>` → exit 0, `tool.sha256: 87cad1ca…`, `expected_refused: 82`, `frozen: "refused 0, expected 82"`, `current: "refused 82"`, `before: miscount`, `after: correct`. `--selftest` → `selftest: 60/60 checks passed`, exit 0.
- Official output `.ufo/waves/round-18/runs/c2-survivors.json` family d item has the same 82/0/correct result, but its `tool.sha256` is `2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d` — the c6dc46f counter, not the delivered `87cad1ca…`. `runs/commands.json:2` records `"measured_commit": "c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d"`. `runs/c2-counter-selftest.stdout` is likewise the parent's 57/57 with the old check name `(b) an inconclusive arm prevents a kill`; the delivered counter replaces that one check with four (`selftest` line 34 `(b) targeted selftest kill survives an other-arm exit 2`). `git diff --stat c6dc46f..HEAD -- .ufo/waves/round-18/c2/survivors.py` → 26 lines, all in `combine_arms` and its selftest, so the family-d path is unchanged; the whole-counter post-repair rerun is absent. `runs/corrected.py` (untracked, mtime 20:17, after the 20:13 commit) would emit `corrected-commands.json` / `c2-survivors-corrected.json`, but neither exists. The round-18 refusal artifact is not among the counter's inputs in either artifact.
- `c2-survivors.exit` is 2 (the disclosed family-b inconclusive pair under the parent classifier, `corpus/lessons/round-18.md:162-165`); family d itself is closed, and the delivered `combine_arms` change is the unre-measured classification seam.

### 4. A fresh container-shaped hole in the repair (limit, not a kill)

All four probes used the current tool in the clone, each creating its own ledger; all exits 0:

| input | `refused` | `parseable` |
|---|---|---|
| `{"text": "KamaR18.X: Background job limit reached (100). Wait."}` | 1 | true |
| raw text (not JSON) | 1 | false |
| bare JSON string `"KamaR18.X: Background job limit reached (100). Wait."` | 0 | true |
| `{"error": "KamaR18.X: Background job limit reached (100). Wait."}` | 0 | true |

Cause: `refused_observations` scans only strings under `text` (`_iter_texts`, `dispatch-provenance.py:389-408,411-422`), and the raw-text fallback is enabled only when JSON parsing fails (`:495-499`). A parseable non-dict result, or prose under a non-`text` key, is still prose-blind. The C2Provenance report discloses "restricted to result `text` fields (or the raw UTF-8 fallback for non-JSON input)" but not the bare-JSON-string case. Under this wave's rules this is a fresh-survivor class, separate from the named round-17 denominator; it must stay visible and must not be scored as a named kill.

### 5. The producer-shape note over-aims the integer branch

The note as written (`.ufo/waves/round-18/build/advice/ConnectKumitate.md:23-27,37-39`) says: refusal is prose with empty `details.results`; kama's ledger zero-fills a missing integer; the attempt log already held `refused: 95`; "If they want the producer to emit an integer, their own routing rule applies."

Kumitate's own producer contract, from the two bound files:

- `SKILL.md:41-44`: `run` emits `ufo-swarm-wave-dispatch-v1` (`{taskCall|null, resumeSends[]}`) and persists the registry/dispatch pair in one critical section — before any task result exists.
- `SKILL.md:44-48`: `record --registry --assignments` fills `agentId`s after the task call returns; `settle --registry [--results] …` emits `ufo-swarm-results-v1` covering every registry member as operator rows or honest `cancelled`/`aborted`.
- `SKILL.md:456-458`: "an absent row proves nothing about a lane, so `failed` is never minted from absence." A wholly refused task call has `details.results: []` (above), so there are no member rows to carry a per-lane refusal count.
- `SKILL.md:18`: swarm output is "None — advisory evidence only; swarm lanes NEVER enter a `NativeRoundHandoff`."

The concrete proof that the producer's numbers are dispatch-side, not outcome-side: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/validation-95.json:1-16` is `validator: "ufo-swarm-wave.mjs run"`, `exit: 0`, `counts: {spawn: 95, resume: 0, total: 95}`, `taskCall_sha256: fe887fc4…` — for exactly the wave whose attempt record is `"result": "refused", "refused": 95, "spawned": 0` (`build/attempts.json:5-7`). Joining the producer's `counts.spawn` to spawned outcomes would report 95 spawned for a 0-spawn wave. (The successful falsify wave has plan = outcome = 76: `falsify/validation.json` `counts.spawn 76`, and its spawn result begins "Spawned 76 background agents" per `falsify/attempts.json` `result_head`.)

A `refused` integer would therefore have to be a wave-level outcome field minted at `settle`, supplied by the driver that holds the task result, and carried by a results schema that today is member-row shaped. That is a kumitate-owned design change, not the "shape note" the round frames. `[INFERENCE]`: the driver, not the producer's `run`, holds the OMP result — `SKILL.md` says `run` emits the taskCall and `record` consumes assignments, but the origin script was not opened (read bound).

No kama counter joins producer counts: `grep -rn 'counts.*spawn\|\["spawn"\]' .ufo/waves/round-18/c1 .ufo/waves/round-18/c2` returned nothing, so the hazard is reader-level, not a present miscount.

### 6. No fleet tooling ownership was absorbed

- `git diff --name-only e75cf680b53484a61709ee1b2787d8dbc6419f74..HEAD | wc -l` → 275 changed paths. Filtering for `kumitate|shokunin/scripts|ufo-fsd|hyaku|registry/` matches exactly one path: `.ufo/waves/round-18/build/advice/ConnectKumitate.md`. No `kumitate-shokunin/`, `scripts/`, `config/ufo.json`, or `crates/` file changed; no producer script was patched from this lane.
- The policy resolver remains lane-side (`POLICY_PATH` at `dispatch-provenance.py:157`, `POLICY_VERSION_RE` at `:173`, note scans at `:220,260`) and the C2 counter re-reads `UFO_CONFIG_PATH` from the tool's own docstring (`c2/survivors.py:1300-1308`). That is round-17 debt already disclosed, not new absorption; this round neither moved nor extended it.
- Path skew stands unresolved and must be quoted, not picked: kumitate `SKILL.md:9` names `/home/vgpnk/Projects/origin-work/ufo-fsd-alpha`; the kama tool invokes `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs` (tool docstring, mode 1).

## Proposed move (one, bounded)

**Split refusal provenance by the surface that observes it, and use round-18's own 95-refusal pair as the proof.**

1. **Kama C2 (own file, no fleet edit):** add one corroborating item to family d — `refused-count-r18`, expected `95`, frozen `0` → current `95`, subject sha256 pinned `83533c…`, corroborated by `build/attempts.json:5-7` `refused: 95`. Keep the round-17 `refused-count` 82 item and the named universe exactly as they are; the 95 arm is a corroborating subject for the same statement, not a new named survivor, so the named-universe total does not move. Declare the container limit from §4 in the family-d notes (and the lesson's residual limits), so it remains visible rather than disappearing into "no general immunity".
2. **Kumitate note (wording only):** replace "if they want the producer to emit an integer" with the observation-boundary statement: `run` writes the dispatch pair before the result; `settle --results` writes member rows with honest absence; a wave-level refusal count has no existing field and would be a dispatch-record schema change supplied by the driver. Kama keeps the count; if a producer count ever exists, kama should compare prose count vs producer count and surface disagreement instead of silently preferring prose (the current `refused_observations` takes precedence at `:502-503`).
3. **No fleet edits, no new script in the orchestration repo, no policy resolver moved.** The note stays advisory per `SKILL.md:18`.

Why this is the non-obvious move: the round's own refusal record is the cheapest independent subject for the repair (it was not used to develop it), and the same record proves why the refused count cannot move upstream — the only producer artifact from that wave says `spawn: 95` while zero spawned. The build seat framed the issue as "producer may emit an integer"; the observation boundary says the producer's `run` cannot, and splitting plan from outcome is the actual hand-off question.

## Risks

- **Post-repair counter artifact missing.** The delivered `c2/survivors.py` (`87cad1ca…`) has no committed full run: the committed artifact binds `2af03fed…`/`c6dc46f`, and `runs/corrected.py` produced no outputs. L1 must produce a *new* full artifact at the delivered revision; the committed one must not be read as binding it. My family-d-only run is not a substitute for families a/b/c/e.
- **Counter output changes.** Adding the second subject changes the official C2 artifact. L1 must write a new run artifact, never overwrite the existing one (`corpus/lessons/round-18.md:167-168`: corrected reruns are new artifacts). The counter will still exit 2 for family-b under the parent classifier; the delivered `combine_arms` may change that, and that change is unmeasured until the full rerun.
- **Not a held-out post-repair case.** The refusal artifact mtime is `2026-10-20 16:55:54 -0300` (19:55Z); the repaired file is `18:02:32 -0300` (21:02Z), and the repair seat cites only the round-17 82 (`build/advice/C2Provenance.md`). It is an independent same-round subject, not a case minted after the repair; say that rather than "fresh replay".
- **The container hole is a real survivor.** If a future OMP result wraps prose in a bare JSON string or a non-`text` key, the count silently returns 0. The lane keeps the parser, so it should test each observed container; the producer integer would mask this class, not fix it.
- **Producer change is bigger than a shape note.** A wave-level refusal field needs a results/dispatch schema slot and a driver-supplied result; asking for it in this round would violate the same `Constants live once` rule (`SKILL.md:805-806`) by minting a second refusal parser before the lane's own is drift-checked against the harness prose.
- **Path skew.** Cite both origin paths; do not select one (`build/advice/ConnectKumitate.md:47` already says this).
- **`settle --results` semantics unopened.** The move does not depend on them; the note should say `run` cannot carry the count and leave `settle` to kumitate.

## Verification (executed; advice only)

All in `/tmp/kama-r18-falsify-ConnectKumitate/repo` at `1c325b2…`, `PYTHONDONTWRITEBYTECODE=1`, scratch ledgers under `/tmp/kama-r18-falsify-ConnectKumitate/`:

- `git clone -q … && git switch -q -c seat/ConnectKumitate 1c325b2…` → 0; `rev-parse HEAD` → `1c325b2…`.
- `sha256sum .ufo/waves/round-18/dispatch-provenance.py` → `93705f17…`; `…/c2/survivors.py` → `87cad1ca…`; `…/frozen/round-17_dispatch-provenance.py` → `11ebb2c0…` (matches `frozen/SHA256SUMS:3`); `…/build/refused-result-1.json` → `83533c13…`.
- `python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` → `selftest: 30/30 checks passed`, exit 0.
- `python3 .ufo/waves/round-18/c2/survivors.py --selftest` → `selftest: 60/60 checks passed`, exit 0 (the delivered counter; the committed `runs/c2-counter-selftest.stdout` is the parent's 57/57).
- `python3 .ufo/waves/round-18/c2/survivors.py --family d --json --out <fresh>` → exit 0, `tool.sha256 87cad1ca…`, `expected_refused 82`, `frozen 0, expected 82`, `current refused 82`, `before miscount`, `after correct`; input is the clone's round-17 file.
- `python3 .ufo/waves/round-18/dispatch-provenance.py --attempt-result .ufo/waves/round-18/build/refused-result-1.json --label refused --out <fresh>` → exit 0, `refused 95`, `spawned 0`, `parseable true`, `result_sha256 83533c…`.
- `python3 .ufo/waves/round-18/frozen/round-17_dispatch-provenance.py --attempt-result <same> --label refused --out <fresh>` → exit 0, `refused 0`, `spawned 0`, same `result_sha256`.
- Four container probes (table in §4) → `text` 1, raw 1, bare JSON string 0, `error` key 0; all exit 0.
- `git diff --name-only e75cf68…HEAD` → 275 paths; fleet-path filter → only `.ufo/waves/round-18/build/advice/ConnectKumitate.md`.
- Read-only lane reads: `c2-survivors.json` family d (`expected 82`, `frozen 0`, `current 82`), `c2-survivors.exit` = 2, `build/attempts.json:5-7`, `build/validation-95.json:1-16`, `build/refused-result-1.json` (95 distinct labels), `falsify/validation.json`, `falsify/attempts.json`.
- Listener/process check: `pgrep -af kama-r18-falsify-ConnectKumitate` → none; `ss -ltn | grep -E ':(8080|34113)\b'` → none. No server was started by this seat.

The full official C1/C2 counts were not rerun; the L1 rerun is the admitting measurement. My numbers are the tool selftests, mode-2 invocations on committed evidence, and the delivered counter's family-d-only run.

Reproduction (run in the clone; each `--out` path fresh and outside the repo):

```bash
# current vs frozen on round-18's own refusal
python3 .ufo/waves/round-18/dispatch-provenance.py --attempt-result \
  .ufo/waves/round-18/build/refused-result-1.json --label refused --out /tmp/exp/cur.json
python3 .ufo/waves/round-18/frozen/round-17_dispatch-provenance.py --attempt-result \
  .ufo/waves/round-18/build/refused-result-1.json --label refused --out /tmp/exp/frz.json
# delivered counter, family d only
python3 .ufo/waves/round-18/c2/survivors.py --family d --json --out /tmp/exp/d.json
```

Container probe (the four inputs in §4, one subprocess per input; `tool` is the current `dispatch-provenance.py`, `--label refused`, fresh `--out` each):

```python
import json, os, subprocess, tempfile
cases = {
 "text-key": json.dumps({"text": "KamaR18.X: Background job limit reached (100). Wait."}).encode(),
 "raw-text": b"KamaR18.X: Background job limit reached (100). Wait.",
 "bare-json-string": json.dumps("KamaR18.X: Background job limit reached (100). Wait.").encode(),
 "error-key": json.dumps({"error": "KamaR18.X: Background job limit reached (100). Wait."}).encode(),
}
for name, blob in cases.items():
    d = tempfile.mkdtemp(prefix="kama-r18-cases-")
    p = os.path.join(d, "r.json"); open(p, "wb").write(blob)
    out = os.path.join(d, "l.json")
    subprocess.run(["python3", tool, "--attempt-result", p, "--label", "refused",
                    "--out", out], check=True)
    e = json.load(open(out))["entries"][-1]
    print(name, e["refused"], e["parseable"])
```

## Limits

- Advice only; no judgement, admission, edit, integration or shipment. No mutants were created; the four container probes are subject-shape probes, not mutants.
- Kumitate read bound: only `SKILL.md` and `corpus/README.md`; the origin `ufo-swarm-wave.mjs` and `provenance.rs` were not opened. The producer-verb reading is from `SKILL.md:37-48`; the claim that `run` does not hold the OMP result is `[INFERENCE]` (the driver executes the taskCall).
- `settle --results` field-level semantics and the `ufo-swarm-results-v1` schema were not opened; the "needs a schema slot" statement is `[INFERENCE]` from `SKILL.md:44-48`.
- The 95-refusal artifact predates the repaired file and was not used by the repairing seat; it is independent same-round evidence, not a post-repair held-out case.
- The delivered counter was exercised only for family d and `--selftest`; families a/b/c/e at `87cad1ca…` were not rerun, and the full post-repair artifact is L1's (or the counter owner's) to produce. `runs/corrected.py` was read, not executed.
- Clone `.ufo` evidence is committed at the pinned revision; hashes above bind those bytes. Working-tree-only artifacts would not be in the clone.

## Installs

None. No pacman transaction (host-wide pause respected), no uv/npx/official-binary install, no tool upgraded.
