VERDICT: partial — round-16 stub matrix + mutation evidence versus tameshi's fixture
conventions: the matrix is behaviorally sound and reproduces exactly (72/72 exit 0;
frozen 55/72 exit 1, failing set == the 17 MODEL_LOADING rows), but three convention
gaps are confirmed: stale source anchors in 10/72 fixture rationales, a helper-only
matrix-gate selftest, and a frozen witness that carries integrity but not prior exposure.

## Axes

- A1 calibration/claim validity — C1 red arm, 17-row flip.
- A2 provenance/evidence integrity — anchors, digests, receipts.
- A3 gate self-verification — the instrument proving its own exits and attribution.
- A4 determinism/cost — single-run flakiness, suite runtime.
- A5 convention conformance — tameshi `corpus/QUALITY.md` 1–20; kama `SKILL.md` gate vocabulary.

## What I ran (literal exits)

| command | exit | result |
|---|---|---|
| `python3 tests/probe-verdicts/check.py --json --selftest` | 0 | 72/72, selftest 4/4, `probe_sha256` `6edd3c4cfdf3f86c…` |
| `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` | 1 | 55/72; stale set == the 17 `MODEL_LOADING` rows (`True`) |
| decoy probe (human line says expected DEAD, JSON contradicts) over `--only AuthAndDead.closed-port-connection-refused` | 1 | `passed=False`, error `unparseable probe output` — fail-closed |
| clean JSON probe, same row | 0 | `passed=True` |
| JSON row correct but exit 0 (expected 2) | 1 | `passed=False` — exit cross-checked |
| `check.py --bogus-flag` / `--probe /nonexistent/…` | 2 / 2 | argv classified |
| fixture scan for `kama-probe.sh:<n>` refs | — | 10/72 rows cite line numbers |
| `grep -rniE "prior.exposure\|10:17\|previously run"` over LOG/SKILL/lesson/PROVINCE/README/SCORECARD | 1 (no match) | no exposure disclosure in repo |
| `pgrep -x llama-server` | 1 | none (I started none; contract satisfied) |

No `measure.py` invocation (forbidden by the contract); nothing bound or probed 8080/34113;
no server started; all output redirected into `/tmp/kama-r16-ConnectTameshiConventions/`.

## Matched conventions (checked, no gap)

- Literal triple oracle in data: every row pins `{verdict, reason, exit}`; graded as the
  conjunction of all three plus `drift == (verdict != MODEL_OK)` (`check.py` `grade()`).
- Hermetic per-row stub on an ephemeral loopback port, fresh handler class per test, no
  live path or fixed port (`check.py:131-135`, `:349`); 71 stub rows + 1 closed-port row.
- Fail-closed schema: unknown keys, non-int status, exit out of `{0,2}`, and a
  `MODEL_OK`+exit-2 inconsistency all abort with exit 2 before any probe runs.
- One checker rejects the old and accepts the repair on retained bytes: the same
  `check.py --probe P` produced `run-before.json` exit 1 / 55 passes and
  `run-after.json` exit 0 / 72 passes, expectations unchanged, frozen bytes not rewritten.
- Instrument identity in every measurement receipt: `run-before/after.json` carry
  `parsed.probe_sha256` (`93ee4302…`, `6edd3c4c…`) and the live receipt carries
  `probe.sha256` `6edd3c4c…` == `sha256sum tools/kama-probe.sh`; `git status` clean.
- Frozen witness integrity before replay: `measure.py:286` calls `verify_frozen()`
  (sha256 + byte count + `git cat-file` blob, exit 4 on any mismatch) before the runs;
  stdout: `frozen snapshot verified: sha256 93ee4302…`.
- Rejections kept: the 17 frozen failures are retained with reason and evidence strings,
  and the receipt gate self-test runs 16 mutations as child CLIs with literal exits
  (`tests/llamacpp-live/check-receipt.py:939-967`; `controls.txt`:
  `selftest: 16 mutations + unreadable case all rejected`).

## Top 3 gaps

### G1 — 10/72 fixture rationales cite lines that now address other code (QUALITY 2, 14)

Every `why` anchor lands on the **frozen** probe's numbering; `tools/kama-probe.sh`
is now 1136 lines against the snapshot's 1092 (+44) and the shift is non-uniform
(+7 / +36 / +43 by region), so no blanket renumber repairs it.

| row | cites | frozen line there | now at | current line there |
|---|---|---|---|---|
| AuthAndDead.401-authentication-error-envelope | 459 | `401) C_VERDICT=UNAUTHORIZED_SERVICE…` | 495 | same 401 branch |
| AuthAndDead.401-plain-text-body | 459 | same | 495 | same |
| AuthAndDead.403-authentication-error-envelope | 460 | `403) …http-403` | 496 | same 403 branch |
| AuthAndDead.closed-port-connection-refused | 426-430 | `6\|7) …connection-refused` | 462-466 | same rc branch |
| AuthAndDead.raw-accept-then-close | 436-440 | `52) …empty-reply` | 472-474 | same rc branch |
| ForeignControls.html-index | 506-511 | html sniff → `html-non-model` | 549-554 | same branch |
| ForeignControls.openmetrics-text | 514-519 | 2xx CT → `non-model-2xx`/`schema-unrecognized` | 557-562 | same branch |
| ForeignControls.json-no-model-array | 392-411 | `body_has_model_array()` whole | 399-418 | function shifted |
| ForeignControls.json-data-object-not-array | 403-405 | `for key in ("data","models")` | 410-412 | same loop |
| ForeignControls.not-found-json | 520-522 | `else …non-2xx-non-model-http` | 563-565 | same branch |

Concrete proof of mis-citation: `sed -n '459p' tools/kama-probe.sh` returns an **empty
line** and `460p` returns `case "$F_RC" in`; the frozen file at 459 is the 401 branch.
Worst case is `AuthAndDead.closed-port-connection-refused`, whose committed
`why` (`run-after.json`) says *"No listener on the port: curl rc=7 maps to DEAD
connection-refused (kama-probe.sh:426-430)."* — current 426-430 is instead the new
loading-matcher preamble, *"a grep approximation cannot prove the exact envelope…"* and
`body_is_llamacpp_loading()`. The rationale now points at the round's own new code.
No fixture carries `authored_against`/probe digest (the matrix is a bare JSON array and
`check.py` rejects non-array documents), so a reader cannot tell which bytes the anchors
address. Note the receipts do pin the probe (above), so this is rationale rot, not
measurement rot; [INFERENCE] it would mislead the next author who re-derives an oracle
from the cited lines.

### G2 — frozen witness records integrity but not prior exposure (QUALITY 12)

`frozen/manifest.json` has exactly `snapshot, sha256, source_commit, source_path,
source_blob, capture, bytes` — no prior-exposure field. `QUALITY.md:39-42`: *"A frozen
witness declaration records prior exposure and checks integrity before replay…"*.
`grep -rniE "prior.exposure|10:17|previously run|already run"` over `LOG.md`,
`corpus/lessons/round-16.md`, `SKILL.md`, `PROVINCE.md`, `README.md`, `SCORECARD.md`
returns nothing (exit 1), so the disclosure exists in no in-repo artifact the replay can
cite. The build wave was told: `.ufo/waves/round-16/build/advice/ConnectTameshi.md:67`
*"Frozen manifest lacks prior exposure; the claim is stronger than the record"* — it was
not landed and is recorded as debt nowhere (QUALITY 7-adjacent). Integrity-before-replay
itself is satisfied (G-range above), so only the declaration half is missing.

### G3 — the matrix gate's self-test is helper-only and retains no forged-line fixture (QUALITY 17, 18)

`check.py:383-395` `run_selftest()` calls `validate_test()` in-process; it never launches
the public CLI, never asserts a literal exit, and its coverage is schema shape only.
Its own advertised count is stale: docstring line 29 says *"feeds 3 embedded malformed
tests"* and `--selftest` help says *"reject 3 embedded malformed tests"*, while
`SELFTEST_MALFORMED` holds 4 and the run prints `selftest: 4/4`. `QUALITY.md:77-82`
(17): *"Its public isolated self-invocation asserts literal exits… helper-only controls
are not a standalone selftest."*

The attribution behaviour is in fact correct — my probes (table above) show the harness
refuses a decoy human line (`unparseable probe output`, exit 1), accepts pure JSON
(exit 0), and rejects a JSON row whose process exit lies (exit 1); `--json` documents
`emit JSON on stdout (diagnostics stay on stderr)`, so purity is contractual. But those
bytes exist only in scratch: `grep -rniE "forged|decoy|inject|canary" tests/` has no hit,
and there is no fixture that would fail if someone "fixed" `grade()` to scrape text.
`QUALITY.md:88-95` (18) explicitly demands *"including a forged-line fixture"*, and
`QUALITY.md:24-26` (9) forbids resting on scratch. The sibling receipt gate does this
correctly (16 child-CLI mutations, literal exits), so the matrix gate is the outlier
against both tameshi and kama's own `SKILL.md:414` vocabulary.

## Secondary (below the top 3)

- A4: one sample per row per snapshot (`measure.py` has no repeat flag; receipts hold one
  record each). The single `port_mode: closed` row (`AuthAndDead.closed-port-connection-refused`)
  depends on `bind_closed_port()`, which binds, listens, **closes**, then lets the probe
  connect (`check.py:264-271`) — a TOCTOU window; a collision would produce a flaky
  failure (fail-safe, not false-pass). The live harness admits the same class of race in
  `receipt.port_pick_note` (*"a sub-second collision race is possible"*); the matrix
  documents it nowhere. QUALITY 11 would require a named finite sample if any clean
  verdict were presented as repeated; none is claimed, so this is debt, not overclaim.
- `run-*.json` pins the probe digest but not the grader: its keys are `name, command,
  cwd, exit, stdout_sha256, parsed, stderr_tail` — no `check.py` sha (QUALITY 20 says
  *"every receipt names the instrument sha it ran"*; the probe is named, the harness is not).
- `stderr_tail` is truncated in the receipt; raw stdout survives only as
  `stdout_sha256` + the parsed doc, so byte-level replay is by digest, not by bytes.

## Proposed move (one, bounded)

Make `check.py --selftest` a **child-CLI gate selftest over two committed synthetic
probes**, reusing the existing closed-port row so no matrix expectation changes:

1. add `tests/probe-verdicts/selftest/forged-line.sh` (prints an expected-verdict human
   line, then contradicting JSON, exit 2) and `selftest/clean.sh` (pure JSON row, exit 2),
   plus `selftest/expectations.json` pinning `{exit, error_contains}` for each — the bytes
   I exercised in scratch, retained in-repo;
2. `run_selftest()` keeps the 4 schema cases, then runs the public CLI three times:
   forged-line → exit **1** with `unparseable probe output`; clean → **0**; `--bogus` →
   **2** (and/or a missing probe → 2), asserting each literal code;
3. in the same patch correct `3` → `4` in the docstring and `--selftest` help.

This closes G3's two named criterion requirements (17 child-CLI literal exits, 18
forged-line fixture) with no change to `tools/kama-probe.sh`, to any expectation, or to
the 72/72 result. G1 and G2 are independent, also-cheap patches (re-anchor the 10
`why` refs to function names + add a `prior_exposure`/expected-red-set block to
`frozen/manifest.json`); I keep them separate rather than bundling.

## Risks

- `--selftest` gains ~2-3 s (two single-row child runs; ephemeral port only, no stubs).
- Coupling the selftest to `AuthAndDead.closed-port-connection-refused` means a rename
  breaks it loudly (fail-closed); if L1 prefers decoupling, give `selftest/` its own
  mini-matrix and a `--matrix-dir` flag instead.
- QUALITY 20: `check.py` is an instrument this falsify wave's seats execute. Stage the
  patch outside `tests/probe-verdicts/` and install after the last reader; receipts should
  then name `check.py`'s sha (currently absent, secondary above).

## Verification

After install: `python3 tests/probe-verdicts/check.py --selftest` → exit 0 with
`selftest: 4/4 malformed rejected; forged-line rejected; clean accepted; argv 2`;
sabotage control: point `--probe` at a probe that emits matching JSON *and* a decoy line
and confirm the selftest path exits 1; full matrix remains exit 0, 72/72; frozen run
remains exit 1, 55/72; `git diff --stat` touches only `check.py` + `selftest/` + docs.

## Limitations

- `QUALITY.md` read as the convention source (20 criteria); tameshi's `SKILL.md` was
  consulted only through `ConnectTameshi.md`'s citations, not re-read here.
- The `why`-anchor comparison assumes the rationale targets the current probe. Evidence
  for that: the 17 expectations only pass on current, fixtures and edit landed in the same
  commit, and no fixture names a target digest; [INFERENCE] anchored at authoring time.
- Mutant-killing (single-change matchers) is the `MutateMatcher` seat's item; I did not
  duplicate it. My "mutation evidence" review covers the before/after flip receipts and
  the receipt gate's 16-mutation selftest.
- No live server, no `measure.py`, no 8080/34113 contact; frozen re-run only via
  `check.py`, output in /tmp.

## Installs

None. No tool installed or upgraded; no pacman transaction attempted.
