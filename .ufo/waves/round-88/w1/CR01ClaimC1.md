# CR01ClaimC1 — C1 (operability) falsification, kama r88 w1

## Scope

C1 only: re-ran the frozen counter `tools/round88-router-cells.py` at M=138a7543… and B=9b4c7af1…,
checked the freeze-byte conjunct, and attacked (a) oracle independence, (b) cheat probes via
`--probe-file`, (c) rev-bytes vs worktree, (d) the `sleeping`/`unknown` → `MODEL_UNLOADED` mapping
against S581, (e) predicate identity. No tracked lane file was modified; the only clone is my scratch
clone at M; every router child was lane-owned on a free loopback port and killed.

## Commands and outputs (true exit codes)

1. `python3 tools/round88-router-cells.py --repo <lane> --rev 138a7543… --work <scratch>` → exit 0;
   `ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=rev probe_sha256=bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf`
   (`out/CR01ClaimC1/receipts/m.out`; identical to `measured/c1.out:19`).
2. Same at B → exit 1, `mismatches=11`, `probe_sha256=0943fb46…` (`receipts/b.out`).
3. `git diff --quiet fb76e7f2… 138a7543… -- tools/round88-router-cells.py` → exit 0; sha256 at F and at
   M both `576a1b374c9150dbd3f58acf26a69c794bd5ac724911aba29f62291ed3435e21`.
4. Rev-bytes proof: clone at M, `tools/kama-probe.sh` worktree replaced by `#!/bin/bash\necho CHEAT`
   (`git -C wt status --porcelain` → ` M tools/kama-probe.sh`), counter `--repo wt --rev M` → exit 0,
   `mismatches=0`, `probe_sha256=bd7a…` (`receipts/c-revbytes.out`).
5. Cheat probes with `--probe-file`: first-entry status, no id match → 3 mismatches; any-`loaded`
   precedence across all entries, no id match → 2 mismatches (C09/C10/C11 discriminate); expect-keyed
   body-hash lookup table, no router logic → **0 mismatches**, `probe_sha256=e88bff72…` (`receipts/cheat-hash2.out`).
6. Three live scenarios on the pinned b11755 child (`receipts/scenario-*.json`):
   - `--no-models-autoload`, unloaded → probe `[exit 2, MODEL_UNLOADED, router-unloaded]`, completion **400** `model is not loaded`;
   - default autoload, unloaded → probe `[exit 2, MODEL_UNLOADED, router-unloaded]`, completion **200**, status_after `loaded`;
   - `--sleep-idle-seconds 2`, after load then sleep (status_before `sleeping`) → probe `[exit 2, MODEL_UNLOADED, router-sleeping]`, completion **200**, status_after `loaded`.
7. S581 fetched at 704366d (sha256 `714c067b…`, `receipts/s581-readme-704366d.md`): autoload default
   line 1993; status list 2059-2121; sleeping section 2335-2341 ("Any new incoming task will
   automatically trigger the model to reload", line 2337).
8. Predicate grep: full sentence only at `plans/round-88-claims.md:71-74`; counter docstring `:1-21`
   defines output/exit but not the sentence; `measured/c1.out:19-21` has the summary line + `exit=0` +
   `# counter bytes freeze vs M: identical`.

## Findings

**BLOCKER — the `sleeping → MODEL_UNLOADED` mapping is contradicted by the claim's own oracle.**
`receipts/scenario-sleeping.json`: a loaded model left idle on the pinned b11755 child reports
`status.value=sleeping`; the M probe returns exit 2 `MODEL_UNLOADED router-sleeping`, while a real
`POST /v1/chat/completions` answers **200** and the entry returns to `loaded`. S581 README:2337 says a new
task auto-reloads a sleeping model. The frozen oracle rule (plan:58-62: HTTP 200 → `MODEL_OK`) would
therefore grade this cell `expected=MODEL_OK observed=MODEL_UNLOADED`; it is never run. Canned C05
(`tools/round88-router-cells.py:67`) authors the opposite of the source, and `live_cells` (:183-215 only
unloaded/loaded) cannot catch it. Consequence: a healthy sleeping router is exit-2 drift
(`tools/kama-probe.sh` at M, header :35-50).

**DEFECT — `unloaded → MODEL_UNLOADED` (drift) is completion-equivalent only under `--no-models-autoload`,
the flag the counter pins (`tools/round88-router-cells.py:194`).** With the default autoload
(README:1993) a fresh pinned router lists `unloaded`; the M probe returns exit 2 `MODEL_UNLOADED` while the
completion answers 200 (`receipts/scenario-autoload-unloaded.json`). The plan motivates the verdict with
the 400, which occurs only with the flag, then applies the verdict to every router. The counter's L01/L03
agreement is thus selected by its own child configuration, not measured across configurations.

**NOTE — the `sleeping` choice is disclosed but not resolved.** `corpus/knowledge/router-mode-readiness.md:48`
calls it "graded not-ready by choice"; the same file's table (:42) sends it to drift. The claim cannot have
both the completion oracle (200 → OK) and C05 (sleeping → UNLOADED) as its ground truth; one must be scoped.

**DEFECT (instrument strength) — the 17/0 green is overfittable.** An expect-keyed body-hash table passes
17/17 (`receipts/cheat-hash2.out`) with no id/status matching for the canned cells and only a naive
"any loaded wins" for the live cells (all live bodies are single-entry). Cheaper id-keyed cheats fail
(3 and 2 mismatches), so C09/C10/C11 do discriminate; but no cell is held out from the probe author, and
the live grid never exercises multi-entry matching. `mismatches=0` certifies 17 verdicts, not router logic.

**NOTE (a) — oracle independence is real; coverage is not.** The oracle is a different endpoint and a real
completion; it produced 200 where the probe said UNLOADED, so it is not derived from the probe. The defect
is that the live grid contains only the flag/state where the two agree. Also the probe runs *before* the
oracle, so a stronger probe that used a completion as its own evidence would load the model and flip
L01/L03 to expected `MODEL_OK`; plan:47-50 forbids the probe from sending a completion, so the ordering
penalizes the better probe.

**NOTE — operator-router provenance gap.** `controls/pilot-live-1234.out` records only `GET /v1/models`
(four ids, all `unloaded`) plus the probe JSON; no `/props` or startup flags. The knowledge table's
"autoload on, `--sleep-idle-seconds 600`" (:25) is therefore unsourced in this round's receipts, and the
contract forbids probing 1234. If true, the M probe will report that router as exit-2 drift whenever idle.

**NOTE (e) — predicate sentence is not identical in all three places.** The summary line and `exit=0` are
byte-identical (plan:72, `measured/c1.out:19-20`); the full sentence, including the freeze-byte conjunct,
appears only in the plan. The counter's summary also omits the revision (`probe=rev` only), so a receipt
without the wrapper header cannot be tied to M.

**Unknown string → `MODEL_UNLOADED` (C14): no source contradiction found.** S581 defines no unknown value;
grading it not-ready is conservative and matches the probe's pre-r88 "`?` never ready" rule. Not a defect.

## Smallest safe correction

Add live cells for `sleeping` and for default-autoload `unloaded` (both cheap on the pinned child). The
counter's own oracle will print `expected=MODEL_OK observed=MODEL_UNLOADED`, forcing the design decision
the current grid hides: either grade those states as a non-drift cold-start verdict (e.g. keep
`MODEL_UNLOADED` informative but not exit-2 drift, reserving drift for `failed:true`/`incomplete`), or
scope the drift claim to `--no-models-autoload` routers — S581 documents no `/v1/models` or `/props` field
exposing that flag, so the first option is the executable one. Do not edit the frozen counter to make the
new cells pass.

## Deliverables

`out/CR01ClaimC1/receipts/`: `m.out`, `b.out`, `c-revbytes.out`, `cheat-hash2.out`, `cheat-hash2.sh`,
`canned-hashes2.json`, `scenario-autoload-unloaded.json`, `scenario-sleeping.json`, `router-exp.py`,
`probe-M.sh`, `s581-readme-704366d.md`. No lane tool was modified; scratch removed.

VERDICT: partial — the frozen 17-cell predicate reproduces exactly at M (exit 0, counter bytes identical, base 11 mismatches), but C1's readiness claim is falsified for `sleeping` and default-autoload `unloaded`: the probe reports exit-2 drift where the claim's own completion oracle returns 200.
