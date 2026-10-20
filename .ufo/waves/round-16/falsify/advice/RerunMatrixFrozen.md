VERDICT: confirm — the frozen pre-round probe fails exactly the 17 `MODEL_LOADING` rows of the 72-row matrix (16 as `FOREIGN_SERVICE/non-2xx-non-model-http`, 1 as `FOREIGN_SERVICE/html-non-model`, all exit 2), and my fresh rerun matches the committed `run-before.json` record-for-record on every claim-bearing field.

## Attack

Independent rerun of C1's red arm, twice, plus provenance and contrast checks:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py \
  --probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/frozen/kama-probe-before.sh \
  --json > /tmp/kama-r16-RerunMatrixFrozen/before.json
```
exit `1` (expected: failures present), 37.8 s, `tests=72 passes=55 failures=17`.
Second identical run → `/tmp/kama-r16-RerunMatrixFrozen/before2.json`, exit `1`, same 55/17, 37.8 s.

## Evidence

1. **Counts match L1 receipts exactly.** Fresh run 72 / 55 pass / 17 fail. Committed `run-before.json` at `b8e485c` (`git show b8e485c:.ufo/waves/round-16/run-before.json`): 72 / 55 / 17, `probe_sha256=93ee4302…a2cd64` — identical to the fresh run's `probe_sha256`.
2. **Exact failing-name set matches, including order.** 17/17 names equal, `new-only=[]`, `old-only=[]`, `order equal: True`.
3. **Record-level equality, not just counts.** Comparing all 72 records on `(verdict, reason, probe_exit, passed, drift, expected.verdict)` against the committed receipt: **0 diffs** (`names equal: True`, `probe_sha == True`). Only `port` and port-bearing `evidence` strings differ run to run.
4. **Every failure is an expected loading row observed as foreign.** Programmatic assertions over the 17 fails: `all expected MODEL_LOADING/llamacpp-loading/2: True`; `all observed FOREIGN_SERVICE: True`; reasons `{'non-2xx-non-model-http': 16, 'html-non-model': 1}`; `all exit 2: True`; `all drift True: True`; `all error None: True`; `all evidence mentions 503: True`. The html row is `NearMissTriple.exact-envelope-labelled-html` → evidence `GET /v1/models -> 503 text/html (Server: kama-stub)`.
5. **Converse holds — no overbroad red-arm failure or false positive.** Matrix contains exactly 17 rows with `expected.verdict == MODEL_LOADING`; `passed: 0`. The other 55 rows all pass under the frozen probe; zero failing rows have any other expectation; zero rows observe `MODEL_LOADING`. Observed verdict histogram: DEAD 1, FOREIGN_SERVICE 54, MODEL_MISMATCH 3, MODEL_OK 8, NOT_HTTP 1, UNAUTHORIZED_SERVICE 5 (no `MODEL_LOADING`). Expect variants among the 17 fails: `*`, `-`, `stories260K` — all still FOREIGN_SERVICE (frozen never reaches expect matching for a 503).
6. **Mechanism proven, not inferred from behavior.** Frozen snapshot has **0** occurrences of `MODEL_LOADING` and **0** of `503` (`grep -c`, exit 1); its generic branches produce the observed reasons at `.ufo/waves/round-16/frozen/kama-probe-before.sh:508` (`html-non-model`), `:517` (`non-model-2xx`), `:521` (`non-2xx-non-model-http`). Current `tools/kama-probe.sh` carries `body_is_llamacpp_loading` (lines ~422–447, exact envelope incl. bool/float/string `code` rejection) and `C_VERDICT=MODEL_LOADING` at `:504-505`.
7. **Frozen snapshot is truly the pre-round probe.** `sha256(frozen)=93ee4302…a2cd64` = `frozen/manifest.json.sha256`; `git rev-parse 20e392e:tools/kama-probe.sh` = `447e29b3…2763` = manifest `source_blob`; `git show 20e392e:tools/kama-probe.sh | sha256sum` = same digest; byte count 47443 = manifest `bytes`.
8. **Contrast run (causation, not just correlation).** Current probe on exactly those 17 names (`--only …`): `tests 17 passes 17 failures 0`, exit `0`, every record `('MODEL_LOADING','llamacpp-loading',2)` (9.0 s). And fresh frozen run vs committed `run-after.json` (`probe_sha256=6edd3c4c…7a50` = `sha256(tools/kama-probe.sh)`, 72/72): changed set is **exactly 17**, all with `expected.verdict == MODEL_LOADING`.
9. **Determinism.** Two runs identical after normalizing ephemeral ports: 0 records differ in `(verdict, reason, probe_exit)` or normalized `evidence`; 0 probe timeouts / non-null `error` across all 144 record-gradings.
10. **Cleanliness.** `pgrep -x llama-server` → exit 1 (empty); nothing listening on 8080/34113 (`ss` grep exit 1); I never invoked `measure.py`; tracked tree clean (`git status --porcelain -uno` empty); `check.py` unmodified since `b8e485c`; matrix JSONs unmodified; no lane/fleet file written except this Report.

## Findings by severity

- **No blocking finding.** C1's red arm is exactly what the lane claims: 55/17, same 17 names, same observed verdict/reason/exit, reproducible twice, and structurally attributable to the absent verdict branch rather than to a bad expectation (items 6 and 8).
- **Low — `stdout_sha256` is irreproducible by construction.** `measure.py:163` hashes raw probe-harness stdout, which embeds OS-assigned stub ports (e.g. record `port: 39685` → `33971`). My two runs produce different digests (`8c3893d0…`, `85442bd0…`) and neither can equal the receipt's `68a15ac3…`. The `parsed` block is the reproducible artifact; the digest cannot serve as a rerun-integrity check. Advisory only — no claim depends on it.
- **Info — transient receipt churn during the wave.** At 10:54:12/10:54:50 `run-before.json`/`run-after.json` were dirty (ports/`stdout_sha256` only; parsed claim fields 55/17 and the same failing-name set) and by 10:55:04 both were byte-identical to `b8e485c` again. [INFERENCE] a concurrent process ran `measure.py` and then reverted the receipts. Both versions agree on every claim-bearing field, so the claim is unaffected; flagged so L1 knows the on-disk receipts need not be the committed bytes mid-wave.

## Limitations

- Stub-level attack only: this proves the pre-change probe's verdict on the matrix, not behavior against a real llama.cpp process (the live capa is a separate seat).
- Two reruns on one host, one `python3`, sequential; the harness spawns 72 ephemeral stub servers per run, so ports (and `stdout_sha256`) cannot be stable.
- Provenance is checked against the local git object store; I did not re-fetch upstream.

## Installs

None (no tool installed or upgraded).

Scratch `/tmp/kama-r16-RerunMatrixFrozen/` (run outputs, receipts copies, comparison stdout) was used and removed after comparison; digests and excerpts above are the retained evidence.
