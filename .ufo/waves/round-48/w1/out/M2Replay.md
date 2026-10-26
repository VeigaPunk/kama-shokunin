# M2Replay — replay tool mutation test (round 48, lane kama)

**Verdict: 32 mutants of `tools/kama-live-replay.py` (base 380bcdff9c8af06997c482f6eb03db926a794a2b) → 15 killed by `--selftest`, 3 killed by the frozen C2 counter, 13 survived (coverage findings F1–F13), 1 equivalent; fresh baseline passes (selftest 21/21, counter met=True).**

## Method

- Mutation base = **committed** bytes at the measured tip: `git show 380bcdff:tools/kama-live-replay.py` (sha256 `69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f`, 430 lines). One live `git clone --shared` fixture at 380bcdff; each mutant committed on top with a fixture identity; the frozen counter `tools/round48-live-replay-v5-audit.py` run against that tip (the counter archives the tip tree, so the mutant is what it executes).
- Each mutant is a single exact text replacement at one behavior-bearing point; the generator asserted each old string occurs exactly once and that the mutant compiles (32/32).
- Detectors: (1) `kama-live-replay.py --selftest` (21 offline cases, baseline pass=21 fail=0 exit=0); (2) frozen C2 counter (baseline: `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0).

## Results

| mutant | category | @380bcdf line | selftest | counter | verdict |
|---|---|---|---|---|---|
| baseline (pristine) | — | — | pass 21/21 | met=True exit 0 | healthy |
| 01-verified-at-dropped | v5 provenance | 121 | FAIL v5-not-verified | — | killed-by-selftest |
| 02-commit-hex-dropped | v5 provenance | 116 | FAIL v5-bad-commit | — | killed-by-selftest |
| 03-url-pin-dropped | v5 provenance | 118 | FAIL v5-url-not-at-commit | — | killed-by-selftest |
| 04-url-pin-noslash | v5 provenance | 118 | pass 21/21 | met=True exit 0 | **survived (F1)** |
| 05-schema-allowlist-dropped | v5 provenance | 98 | FAIL v3-receipt | — | killed-by-selftest |
| 26-prov-hex64-dropped | v5 provenance | 107 | pass 21/21 | met=True exit 0 | **survived (F13)** |
| 27-model-bind-dropped | v5 provenance | 109 | FAIL model-digest-differs-from-receipt | — | killed-by-selftest |
| 06-argv-archive-dropped | archive argv | 240 | FAIL v5-match | — | killed-by-selftest |
| 07-cmp-schema-dropped | schema equality | 181 | FAIL v5-rerun-schema-differs | — | killed-by-selftest |
| 08-proj-props-const | projection | 167 | FAIL compare-stable-differs | compare=0 (props-n_ctx) exit 1 | killed-by-selftest |
| 09-proj-metrics-const | projection | 171 | pass 21/21 | met=True exit 0 | **survived (F2)** |
| 10-proj-loading-const | projection | 172 | pass 21/21 | met=True exit 0 | **survived (F3)** |
| 11-proj-ownership-const | projection | 174 | pass 21/21 | met=True exit 0 | **survived (F4)** |
| 12-proj-slots-body-dropped | projection | 168 | pass 21/21 | met=True exit 0 | **survived (F5)** |
| 13-proj-model-names-dropped | projection | 163 | pass 21/21 | met=True exit 0 | **survived (F6)** |
| 14-proj-port-refuses-dropped | projection | 173 | pass 21/21 | met=True exit 0 | **survived (F7)** |
| 15-check-loop-void | compare loop | 192 | FAIL check-differs | — | killed-by-selftest |
| 16-missing-check-ignored | compare loop | 193 | pass 21/21 | met=True exit 0 | **survived (F8)** |
| 17-evaluated-gate-void | compare loop | 142 | pass 21/21 | met=True exit 0 | **survived (F9)** |
| 18-compare-exit-inverted | --compare exit | 419 | pass 21/21 | compare=0 (instance-only, 5 stable) exit 1 | killed-by-counter |
| 19-compare-exit-zero | --compare exit | 419 | pass 21/21 | compare=0 (5 stable) exit 1 | killed-by-counter |
| 20-extract-before-verify | digest order | 218 | pass 21/21 | met=True exit 0 | **survived (F10)** |
| 21-member-verify-after-exec | digest order | 227/240 | pass 21/21 | met=True exit 0 | **survived (F11)** |
| 22-member-containment-dropped | member checks | 223 | pass 21/21 | met=True exit 0 | **survived (F12)** |
| 23-member-dotdot-dropped | member checks | 112 | FAIL unsafe-member | — | killed-by-selftest |
| 24-member-isfile-dropped | member checks | 223 | FAIL absent-member | — | killed-by-selftest |
| 25-acquire-digest-skipped | digests | 129 | FAIL model/asset-digest-wrong | — | killed-by-selftest |
| 28-fetch-scheme-void | fetch scheme | 83 | FAIL http-refused | — | killed-by-selftest |
| 29-live-exit-ignored | plumbing | 250 | FAIL live-exit-nonzero | — | killed-by-selftest |
| 30-match-constant-true | plumbing | 256 | FAIL 5 cases (check-differs, no-evaluated-check, live-exit-nonzero, v5-rerun-schema-differs, projection-differs) | — | killed-by-selftest |
| 31-main-exit-zero | plumbing | 426 | pass 21/21 | tamper=0 urlswap=0 exit 1 | killed-by-counter |
| 32-acquire-order-swapped | equivalent | 218 | pass 21/21 | met=True exit 0 | equivalent (pure statement reorder; no behavior change) |

Kill evidence (counter detail lines): `08` → `compare props-n_ctx: exit 0 want 1`; `18/19` → `compare <variant>: exit 0/1 want 1/0` (all six variants); `31` → `tamper-model/tamper-asset: exit 0: not refused`, `urlswap-asset/urlswap-model: exit 0` (want 2). Full outputs in `counter/`.

## Findings (survived mutants) — each with a proposed selftest case

- **F1 (04-url-pin-noslash, line 118)** — pin check `f"/resolve/{commit}/" not in url` dropped its trailing slash: `/resolve/<commit>` still matches `/resolve/<commit>anything` and any sibling revision path. Proposed case: v5 receipt whose URL has `<commit>x` after `/resolve/` must exit 2 `provenance-url-revision-differs-from-commit`.
- **F2 (09-proj-metrics-const, line 171)** — projection `metrics` (status) is compared by neither the selftest nor the counter's compare leg. Proposed case: rerun with `captures.metrics.status` changed → exit 1 `projection:metrics` (counter: add a `metrics-status` compare variant).
- **F3 (10-proj-loading-const, line 172)** — `loading_envelope_exact` and `loading_503.body_sha256` unguarded. Proposed case: rerun with `loading_envelope_exact=False` → exit 1.
- **F4 (11-proj-ownership-const, line 174)** — `port_listener_ownership` unguarded. Proposed case: ownership `child`→`host` → exit 1.
- **F5 (12-proj-slots-body-dropped, line 168)** — slots `body_sha256` unguarded (`element_count` is covered by `compare-stable-differs` and the counter's `slots-count`). Proposed case: change slots `body_sha256` only → exit 1.
- **F6 (13-proj-model-names-dropped, line 163)** — `models[].name` list unguarded (`data[].id|owned_by` covered). Proposed case: change the models name list → exit 1.
- **F7 (14-proj-port-refuses-dropped, line 173)** — teardown `port_refuses` unguarded (`sigkill_sent` covered). Proposed case: flip `teardown.port_refuses` → exit 1.
- **F8 (16-missing-check-ignored, line 193)** — `compare()` no longer flags an evaluated check absent from the rerun. The counter independently re-checks evaluated sets in its replay leg, so C2 is robust today; the tool's own `--compare`/replay contract is not. Proposed case: rerun omitting an evaluated check → exit 1 with `check:<id>:not-evaluated`.
- **F9 (17-evaluated-gate-void, line 142)** — `evaluated()` includes non-evaluated checks; today's receipts are all `evaluated=True`, so no detector triggers. Proposed case: receipt with an `evaluated=False` check absent from the rerun must still match (exit 0).
- **F10 (20-extract-before-verify, line 218)** — the archive is extracted before its sha256 is verified. The contract requires verification *before* extraction; the urlswap leg only inspects exit/refused/rerun, so the extraction order is unobservable to every detector. Proposed case: after a digest refusal, assert no extracted tree exists under `--work` (or use a marker file).
- **F11 (21-member-verify-after-exec, lines 227/240)** — the archive member (server binary) is executed before its digest is verified. Proposed case: member digest wrong + a live tool that writes a marker → exit 2 **and** marker absent.
- **F12 (22-member-containment-dropped, line 223)** — realpath containment of the member inside the extraction tree is unguarded; symlink/hardlink escape is untested. Proposed case: archive member that is a symlink pointing outside the tree → refusal before execution.
- **F13 (26-prov-hex64-dropped, line 107)** — 64-hex format validation of provenance digests is unguarded; malformed-digit strings reach acquire (only a later byte mismatch is caught). Proposed case: `provenance.server.asset_sha256="zz"*32` → exit 2 `provenance-bad-digest`.

## Restoration evidence

- Fixture: before every mutant install the file was reset and its sha256 re-verified `== 69837013…`; after the last run the fixture is reset to 380bcdff, `tools/kama-live-replay.py` sha256 `69837013…`, `git status --porcelain` empty (see `counter/fixture-commits.txt`, `counter/counter-*.txt`).
- Lane: never written by this seat (read-only git only); per-mutant fixture commits exist only in the scratch clone under fixture identity.

## Environment observation (not a C2 finding)

The lane **working tree** `tools/kama-live-replay.py` changed during this session: at t0 `wc -l`=430 / sha256 `69837013…` (= the committed 380bcdff blob); later 473 lines / sha256 `7be002a14f0d0292f881b82b09cf7d82807a73d014ddbb4c52adb84e49077db5`, `git status --porcelain` shows ` M` vs HEAD `b85783e` (wave-spec dispatch). The frozen counter measures `git archive --tip`, so this drift does not affect C2; mutants were generated from the committed bytes to avoid testing a moving target.

## Evidence files

- `manifest.json` — mutant names/categories/line numbers/sha256 (line numbers reference the 430-line committed file).
- `counter/selftest-baseline.txt`, `counter/selftest-<name>.txt`, `counter/selftest-summary.txt` — selftest outputs per mutant.
- `counter/counter-baseline.txt`, `counter/counter-<name>.txt`, `counter/fixture-commits.txt` — counter outputs, exit codes, fixture commit hashes, restoration hashes.
- `mutants/*.py` — all 32 mutant sources.
- `report-data.json` — structured verdict table.
