VERDICT: confirm — L1's C1 numbers reconstruct exactly from `run-before.json`, `run-after.json` and `measure-stdout.txt`: 72 rows, frozen 55 pass / 17 fail (exit 1), current 72/72 (exit 0), changed set = exactly the 17 `MODEL_LOADING` rows in the stdout's own order; both `stdout_sha256` fields verify against a canonical reconstruction whose method I validated on live `check.py` output. No numeric inconsistency found. Six scoping observations are reported below, one of them a timestamp anomaly mid-session; none changes a number.

# What was attacked

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, commit `b8e485cc6b201c8e4604a20808e58babbfe08e34`. The C1 claim: "frozen 55 pass / 17 fail, current 72/72, changed set == the 17 loading rows", plus the `stdout_sha256` fields in the two receipts and every number printed in `measure-stdout.txt`. I reconstructed from the three named files first, then corroborated by execution.

# What I ran (exact commands, exit codes)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh tools/kama-probe.sh` | 0 | `93ee4302…cd64` (47443 B), `6edd3c4c…fa50` (49637 B) |
| 2 | `git cat-file blob 20e392e…:tools/kama-probe.sh \| sha256sum` | 0 | `93ee4302…cd64` — frozen == round-15 blob |
| 3 | same blob `\| git hash-object --stdin` | 0 | `447e29b3…2763` == `manifest.source_blob` |
| 4 | `python3 /tmp/kama-r16-RevengerRunReceipts/recount.py` (receipt-only recount) | 0 | all consistency predicates `True` |
| 5 | `python3 tests/probe-verdicts/check.py --probe .ufo/…/frozen/kama-probe-before.sh --json > /tmp/…/rerun-before.json` | **1** | 37.8 s; stderr tail `tests=72 passes=55 failures=17`; stdout 76341 B |
| 6 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/…/rerun-after.json` | **0** | 38.0 s; `tests=72 passes=72 failures=0`; stdout 76386 B |
| 7 | `python3 /tmp/…/final2.py` (scrubbed receipt↔rerun diff, serializer validation) | 0 | receipt==rerun `before True`, `after True`; reconstruction-method check `True`, `True` |
| 8 | `python3 /tmp/…/deep.py` (stdout-claim recomputation) | 0 | every claim in `measure-stdout.txt` matches the receipts |
| 9 | `pgrep -x llama-server`; `ss -ltn \| grep -E ':(8080\|34113)\b'` | 1 / 1 | no llama-server; nothing on 8080/34113 |

I did **not** run `measure.py` (lane rule: it rewrites L1 receipts). `check.py` binds only loopback stub servers on ephemeral ports; no `llama-server` was started and post-run `pgrep -x llama-server` is empty.

# Receipt-only recount

Both receipts have exactly the seven keys `{name, command, cwd, exit, stdout_sha256, parsed, stderr_tail}`; `parsed` is the full `check.py` machine document.

| Arm | declared tests/passes/failures | recounted from `parsed.records` | `exit` | exit rule (`0 iff failures==0`) |
|---|---|---|---|---|
| before | 72 / 55 / 17 | 72 / 55 / 17 | 1 | holds |
| after | 72 / 72 / 0 | 72 / 72 / 0 | 0 | holds |

`passes + failures == tests` in both; 72 unique names; 9 `matrix_sources`; zero non-null `error` fields; zero rows where the stored `passed` flag disagrees with a fresh recomputation of `verdict==expected.verdict ∧ reason==expected.reason ∧ probe_exit==expected.exit ∧ drift==(verdict!="MODEL_OK")`; zero `drift` inconsistencies.

Per-family pass counts (recomputed) equal the stdout's lines character-for-character:

- before: `AuthAndDead 7/7, EnvelopeShapes 7/9, ForeignControls 8/8, LoadingEnvelope 0/8, LoadingRace 4/9, NearMissTriple 6/8, NonLoadingStatuses 7/7, Overbroad503 8/8, ReadyControls 8/8`
- after: `AuthAndDead 7/7, EnvelopeShapes 9/9, ForeignControls 8/8, LoadingEnvelope 8/8, LoadingRace 9/9, NearMissTriple 8/8, NonLoadingStatuses 7/7, Overbroad503 8/8, ReadyControls 8/8`

Expected-verdict census (from the receipts, corroborated against the 9 matrix files directly): `UNAUTHORIZED_SERVICE 5, DEAD 1, NOT_HTTP 1, FOREIGN_SERVICE 37, MODEL_LOADING 17, MODEL_OK 8, MODEL_MISMATCH 3` = 72. Observed: before `FOREIGN_SERVICE 54`, after `FOREIGN_SERVICE 37` + `MODEL_LOADING 17` — i.e. exactly 17 rows move, 54 = 37 + 17, and no expected-`FOREIGN_SERVICE` row moves.

Before-arm failure reasons: `non-2xx-non-model-http` ×16, `html-non-model` ×1. After-arm loading rows: verdict `{MODEL_LOADING}`, reason `{llamacpp-loading}`, `probe_exit` `{2}`, all `passed`.

# Changed set

Verdict diff (17, sorted) — literal equality with the stdout's list, same names, same order, same before/after/expected triples:

```
EnvelopeShapes.ExtraFieldsAllowed            FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
EnvelopeShapes.Padding64KiB                  FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.canonical-alias              FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.dash-expect                  FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.every-non-frontend-path      FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.key-order-permuted           FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.no-server-header             FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.plain-json-content-type      FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.pretty-printed-body          FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingEnvelope.wildcard-expect              FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingRace.HealthAlreadyOk                  FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingRace.HealthAlsoLoading                FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingRace.HealthConnClosed                 FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingRace.HealthExplicit404                FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
LoadingRace.HealthUnlisted                   FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
NearMissTriple.exact-envelope-labelled-html  FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
NearMissTriple.readme-key-order-positive     FOREIGN_SERVICE -> MODEL_LOADING (expected MODEL_LOADING)
```

Directional predicate from the receipts: `loading expectations 17 == before failures 17 == changed 17`, all three the same name set, before and after name sets identical, non-loading changed = ∅. `measure.py:351-363` computes exactly these sets and its PASS requires `before_failures>=1 ∧ after_failures==0 ∧ all_changed_loading ∧ directional`; all four hold, so the stdout's `result: PASS` is entailed, not merely asserted.

Fields that did **not** change across the two runs (checked row by row): `expect`, `probe_exit`, `drift`, `source`, `why`, `requests`, `expected`, `served_model`. Only `verdict`, `reason`, `evidence`, `passed` move, and only on the 17.

# stdout_sha256 verification

`measure.py:154-166` takes one `stdout` byte string and both hashes and parses it: `receipt["stdout_sha256"] = hashlib.sha256(stdout).hexdigest()` (:163), `receipt["parsed"] = json.loads(stdout.decode("utf-8","replace"))` (:166). `check.py:502-503` puts the human summary on stderr and prints the machine document with `print(json.dumps(doc, indent=2))` — i.e. `json.dumps(doc, indent=2) + "\n"`, default separators, `ensure_ascii=True`. Therefore the only byte string that can hash to the field and parse to the field is canonical:

```
K = sha256( json.dumps(parsed, indent=2).encode() + b"\n" )
```

| Receipt | recorded `stdout_sha256` | re-derived `K` | match |
|---|---|---|---|
| before | `68a15ac3ec5e152e9004193e288276fbf955b30660bb1ab013a1b1488bbe9200` | same | yes |
| after | `64fe78afa27797b987baedd69bf177d8e679f10cdf75eabc0340eb4ef79b22ab` | same | yes |

Method validation: applied to the **actual captured bytes** of my two live `check.py` runs, the reconstruction reproduces the file byte-for-byte (`True`, `True`). The live stdout is pure ASCII (0 bytes > 0x7F; 6 `\u` escapes), because `why` strings contain U+2014 which `ensure_ascii` escapes — so the `errors="replace"` decode at :166 can never fire and the round trip is lossless. The two hashes differ from each other and from my reruns (`8fb690f0…`, `1a4e3a34…`), as they must: each of the 72 rows carries a fresh ephemeral `port` and one row embeds its port in `evidence`.

# External corroboration (why "confirm" is not just internal arithmetic)

- **Replay identity.** Both reruns (rows 5–6) equal the receipts record-for-record after removing the only three nondeterministic strings: the per-row `port` field, the port echoed inside `AuthAndDead.closed-port-connection-refused`'s `evidence` (`rc=7 Failed to connect to 127.0.0.1:50499 after 0 ms…`), and the `probe` path I passed relatively. Every verdict, reason, served_model, evidence, request list, probe_exit, expected block and passed flag reproduced; 72/72 distinct ports per arm (the two runs happen to share one port value by coincidence).
- **Live-input census.** Direct read of `tests/probe-verdicts/*.json`: 9 files, 72 rows, 9 families, 17 `MODEL_LOADING`, unique names — matching the Context's "72 rows, 9 families, 17 MODEL_LOADING".
- **Committed bytes.** On-disk sha256 == `git cat-file blob b8e485c:<path>` for all three named files (`run-before.json` `9d3168c936a79f10…`, `run-after.json` `ad3a7460d87b38b8…`, `measure-stdout.txt` `aeec7fdfc5efa92b…`); `git status --porcelain` clean for them; `tools/kama-probe.sh` unchanged at HEAD.
- **Probe identities.** `run-before.parsed.probe_sha256 = 93ee4302…cd64` = frozen file = git blob at `20e392e`; `run-after.parsed.probe_sha256 = 6edd3c4c…fa50` = current `tools/kama-probe.sh`. Both receipts' `command`/`parsed.probe` name the matching absolute paths.
- **Stdout claims.** The frozen-verification line, the `name/exit/passes/failures` table (`before\t1\t55\t17`, `after\t0\t72\t0`), both per-family lines, the 17-line changed list (order included), the `directional:` line (`loading_expectations=17 before_failed=17 changed=17 equal=True`) and the `result: PASS …` line were each recomputed from the receipts and are exactly true.

# Inconsistencies / observations

1. **The C1 delta is invisible to exit-code-only consumers (real scope limit, not a contradiction).** `probe_exit` is identical on both arms for all 72 rows: 8×0 (`MODEL_OK`) and 64×2; all 17 loading rows exit 2 before *and* after and `drift` is `True` both times. The entire 17-row change exists only in the `--json` `verdict`/`reason` fields (`FOREIGN_SERVICE/non-2xx-non-model-http|html-non-model` → `MODEL_LOADING/llamacpp-loading`). [INFERENCE] Any consumer keying on exit status or `drift` cannot distinguish loading from dead/foreign; the stdout's wording ("verdict change(s)") is accurate, but downstream prose must not claim an exit-status-visible change.
2. **Whole-record diffs overcount by one.** 18 rows differ in `evidence` between the receipts while 17 differ in verdict: `AuthAndDead.closed-port-connection-refused`'s evidence embeds its ephemeral port (`…127.0.0.1:50499…` vs `…127.0.0.1:51349…`), and that difference is harness nondeterminism. `measure.py` diffs verdicts only, so its 17 is right; a future recount that diffs full records without port normalization would report 18 changed rows.
3. **`stdout_sha256` is a self-consistency digest, not an attestation and not replay-stable.** It proves the stored `parsed` *is* the document whose serialization was hashed; it cannot be reproduced across runs (ports), is unsigned, and the receipts retain no raw stdout. It also binds nothing else: `check.py` and the 9 matrix files are not digested by the receipt (`probe_sha256` is the only file identity). My replay against today's `check.py` + matrices reproduces all records, so drift *now* is excluded; drift *between* 10:50 and my replay cannot be excluded from the receipts alone [INFERENCE].
4. **The two receipt files were rewritten (identical bytes) at 10:55:04, mid-session.** `measure-stdout.txt` and the rest of the build-wave tree carry `2026-10-20 10:50:49.145…` (== commit instant; only the untracked `build/completion-summary.json` at 10:53:33 differs); `run-before.json` and `run-after.json` carry the *same* nanosecond `10:55:04.201442395`, and `.git/index` is `10:55:07`. Their content is byte-identical to HEAD before and after: `run-before`'s first record still carries `port: 39685` as it did before the rewrite, and both files hash to the committed blobs. [INFERENCE] a path-scoped `git restore`/`checkout --` of exactly those two paths by concurrent wave activity, not a re-measurement. Consequence: the mtime ordering cannot be used to argue `measure-stdout.txt` and the receipts are from one invocation; the numbers do not depend on that because all stdout claims recompute from the receipts. (This also corrects the blanket claim in sibling advice `RevengerFrozenProvenance.md` that "all wave artifacts … share mtime 10:50:49" — false for these two files; that seat's provenance conclusion does not rest on it.)
5. **`measure-stdout.txt` has no recorded digest.** No manifest or receipt binds it (grep over the wave dir finds no digest of it). I treated every line as a claim to recompute rather than evidence; all of them held, so no trust anchor is needed.
6. **Wrong-attribution guard.** `tools/__pycache__/kama-llamacpp-live.cpython-314.pyc` (10:54:44) and the untracked `build/completion-summary.json` / `falsify/` tree are other seats' artifacts — not created by me, and I did not remove them.

# Limitations and scope

- My recount verifies arithmetic, classification deltas and receipt integrity — **not** that the 17 matrix rows are semantically "loading". Several of them deliberately pin `MODEL_LOADING` where `/health` is 404/closed/unlisted or the loading envelope is labelled `text/html`; those expectations are declared by the build wave's matrices, so the *numbers* are consistent with the declared contract, while the semantic call is the `FamilyLoadingRace` / `FamilyLoadingEnvelope` / `FamilyNearMissTriple` / `FamilyEnvelopeShapes` seats' item.
- "Receipts only" cannot establish authenticity: without a signature, the strongest available check is reproducibility against the current, committed inputs, which passes exactly.
- The receipts record `check.py`'s exit (1/0), not `measure.py`'s; `measure-stdout.txt`'s trailing `exit=0` is the caller's echo of `measure.py`'s `EXIT_PASS`, consistent with `main()`'s return.

# Installs

None — no package installed or upgraded; only `git`, `python3`, `sha256sum`, `cmp`/`grep` were used. No `llama-server` started, no port 8080/34113 contacted. Scratch `/tmp/kama-r16-RevengerRunReceipts/` removed after writing this report. I wrote no lane file except this report.
