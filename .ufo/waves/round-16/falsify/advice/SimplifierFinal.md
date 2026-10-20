VERDICT: confirm — dead code and duplicated authority exist in all four round-16 files, and one duplicate authority is already measurably wrong (the receipt gate accepts a `port_listener_ownership` value the producer cannot emit and rejects the one it can). Twelve deletion candidates below; none require a new abstraction, and the four cross-file duplications that look like DRY bait must be kept.

# SimplifierFinal — dead code / duplicated logic in the four landed files

Item attacked: dead code or duplicated logic that adds failure surface in
`tools/kama-llamacpp-live.py` (989 ln), `tests/llamacpp-live/check-receipt.py` (1014 ln),
`tests/probe-verdicts/check.py` (510 ln), `.ufo/waves/round-16/measure.py` (395 ln).
Advice only; no lane file was modified. No llama-server was started. `measure.py` was
not executed (not even read-only), per the lane contract.

Axes used to keep/drop moves: **A1 fewer authorities** for one fact, **A2 failure surface**
(silent tolerance, dead fields, unreachable vocabulary), **A3 preserved contract** (receipt
schema, 72/72 matrix, frozen bytes), **A4 edit cost**. A move is kept only if A1/A2 improve
and A3 is untouched.

## What I ran (all output written under /tmp/kama-r16-SimplifierFinal)

| command | exit | result excerpt |
|---|---|---|
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted` |
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` | 0 | `VALID` |
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt-frozen-probe.json` | 0 | `VALID` |
| `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --selftest > /tmp/...` | 0 | `tests 72 passes 72 failures 0 selftest 4 / 4` |
| AST scan of the four files (Name load/store counts, unused params) | 0 | no unreferenced module-level names; only protocol params unused (`_frame`, `message/explain`) |
| regex hit count of `refused_ports` patterns over `registry/endpoint-consumers.tsv` | 0 | IPv4 pattern 3 hits (`8080,34113,34113`); other five patterns **0 hits each** |
| import module, compare `refused_ports()` vs pattern-subset computation | 0 | both `[8080, 34113]`, `same set: True` |
| `git rev-parse 20e392e:tools/kama-probe.sh` | 0 | `447e29b397405a3ee9813ca2e44aedf88abe2763` = `manifest.source_blob` |
| sha1 git-blob-id formula over frozen bytes | 0 | equals `447e29b…` (`True`) |
| gate on live receipt with `port_listener_ownership` mutated to `unproven` | **1** | `'unproven' not in child\|foreign\|unknown` |
| gate on same receipt with `port_listener_ownership` mutated to `unknown` | **0** | `VALID` |
| `_decode_body(len=65536, cap=65536)` via module import | 0 | `truncated=False`; `HTTP_BODY_CAP<=CAPTURE_BODY_CAP: True` |

Baseline facts used below: the matrix record shape is fixed and verified from a real run —
keys are `drift, error, evidence, expect, expected, family, name, passed, port, port_mode,
probe_exit, reason, requests, served_model, source, verdict, why`, with **no** `observed`,
`observed_verdict`, or `expected_verdict`; top-level doc has integer `passes`/`failures`;
`passed` is `bool`. Live receipt shows `pdeathsig = {"prctl_ok": true, "requested": true}` and
`port_listener_ownership = "child"`.

## Deletion candidates, ranked by failure surface removed

### P1 — gate vocabulary: delete `"unknown"`, add the producer's `"unproven"` (check-receipt.py:363-365)
Producer maps ownership `None` → `'unproven'` (kama-llamacpp-live.py:851) and `verify_live` returns
`'foreign'|'unproven'` (:461). The gate's enum is `("child","foreign","unknown")`. Measured: a valid
receipt relabelled `unproven` is **INVALID** (exit 1) while one relabelled `unknown` is **VALID** (exit 0).
So the validator (a) green-lights a token no producer can emit and (b) red-flags the producer's real
token with a wrong message. Duplicate authority, already divergent. Change both the tuple and its
message string. Gate-only; both stored receipts still pass (measured). Size: 1 line.

### P2 — producer `body_truncated` is a constant-False duplicate of `body_read_truncated` (kama-llamacpp-live.py:476-478, const :65)
`http_get` returns at most `HTTP_BODY_CAP` (65536) bytes; `_decode_body(body, CAPTURE_BODY_CAP)` tests
`len(body) > 65536`, which is unreachable. Measured `_decode_body(65536,65536) -> False`. The receipt
therefore always says `body_truncated: false`, even when `body_read_truncated: true` records that a
bigger response was capped — two flags for one fact, one of them lying. Delete `body_truncated` from
`_capture` (plain `decode` remains; `body_read_truncated` at :473 already records truncation) and its two
literal occurrences in the gate selftest (check-receipt.py:818,824 — the gate never reads the field).
Stored receipts keep the key; the gate only requires `captures.<name>` to be an object, so extra keys
remain tolerated. Size: 3 lines. *Alternative if the key must stay: one line
`cap['body_truncated'] = result['body_truncated']` and drop the `_decode_body` call here.*

### P3 — producer double-assigns `child_env_keys` (kama-llamacpp-live.py:758 vs :785)
The initializer `sorted(CHILD_ENV_KEYS)` is dead: only list construction sits between it and the
unconditional `sorted(child_env)` overwrite. If it ever escaped it would claim the whole allowlist
instead of the subset actually passed to the child — a second, wrong authority for one key. Delete :758.
Size: 1 line. Zero receipt-byte change.

### P4 — producer recomputes the exit code twice (kama-llamacpp-live.py:934 vs :976)
The in-`try` `exit_code = 0 if all(c['passed'] for c in checks) else 1` is unconditionally recomputed in
`finally` (:976) whenever `setup_error is None`, over a strict superset of checks (teardown + model
rehash are appended in between). No path reaches `:976` with a different answer. Delete :934; keep the
`exit_code = 2` initializer. Size: 1 line. Zero behavior change.

### P5 — producer owns two copies of the ownership→error-code mapping (kama-llamacpp-live.py:437-440, :456-461)
`readiness_loop` and `verify_live` both spell the pair `port-listener-not-our-child` /
`port-listener-ownership-unproven` and both carry their own `False/None` split. One fact, two sites, and
`verify_live` already folds the same mapping again for the `'foreign'|'unproven'` label. Extract one
`_ownership_code(owned)` helper used by both. Size: ~6 lines removed; no receipt change.

### P6 — redundant exception subclasses (kama-llamacpp-live.py:582, :591)
`except (ProcessLookupError, PermissionError, OSError)` is exactly `except OSError`:
`ProcessLookupError` and `PermissionError` are both `OSError` subclasses. The tuple implies distinct
handling that does not exist. Same edit in both teardown kill sites. Size: 0 net lines; removes a false
reading of the control flow.

### P7 — measure.py re-parses a schema it owns the producer of (5 dead branches, ~20 lines)
Inputs to measure.py are only ever fresh `check.py --json` documents (`run_check` invokes it), and the
shape is fixed and verified above. Dead today, and each dead branch converts a *schema drift* into a
silent `None`/`False` instead of a loud failure:
- `_verdict` (:208-218): `rec.get("observed")` (no such key), `f"{side}_verdict"` for both sides, and
  the `''` guard are all dead; only `rec["expected"]["verdict"]` and `rec["verdict"]` are live. Replace
  with two direct reads.
- `record_family` (:196-206): the name-derived and `"?"` fallbacks are unreachable; `check.py`
  `validate_test` requires a non-empty `family` and every record copies it (check.py:120-126).
- `count_field` (:182): the `"passed"` / `"failed"` alternates never exist; doc has integer
  `passes`/`failures`. Delete the variadic tail.
- `record_passed` (:227): the `isinstance(flag, int)` branch is unreachable (`passed` is `bool`).
- `expected is None` fallback (:326-328): every after-record carries `expected`; the fallback to the
  before-record can never fire.
Size: ~20 lines. Measure output for the current receipts is unchanged (same 55/17, 72/0).

### P8 — check.py advertises the wrong selftest count (check.py:29, :448-449)
Docstring and `--selftest` help say "3 embedded malformed tests"; `SELFTEST_MALFORMED` has four and the
run reports `4 / 4` (measured). Delete the numeral, do not touch the list. Size: 2 words.

### P9 — check.py splices a constant to build the probe argv (check.py:61, :274-276)
`*PROBE_ARGV_TAIL[:1]` / `*PROBE_ARGV_TAIL[1:]` exists only to insert `--port/--expect` in the middle.
A wrong index silently drops the `check` subcommand and every row then fails as "unparseable probe
output" rather than as a harness error. Write the argv literally and delete `PROBE_ARGV_TAIL` (the
producer already writes the same 10-token invocation literally at kama-llamacpp-live.py:538-540).
Size: 1 constant + 2 slices.

### P10 — gate selftest literal carries a stale `pdeathsig` (check-receipt.py:812)
The literal (documented as "the producer's exact shape") has `"pdeathsig": "SIGKILL (PR_SET_PDEATHSIG,
Linux best-effort)"`; the producer emits `{"requested": True, "prctl_ok": true|false|"unknown"}`
(:846; confirmed in the live receipt). The gate never reads the field (only the docstring key list at
:14 mentions it), so the stale literal asserts nothing and misleads the next reader. Either delete the
key from the literal or mirror the object and add the two-line validation. One authority either way.

### P11 — measure.py's `DEFAULT_COMMIT`/`DEFAULT_SOURCE_PATH` are a second authority for the manifest (measure.py:49-50, :111-112, :288-289)
`frozen/manifest.json` already carries `source_commit`/`source_path` (verified), so all four fallback
expressions are dead for the frozen artifact — and if the manifest ever omitted them, measure would
verify against a *hard-coded* commit while printing the default as if it were the manifest's. Make
`load_manifest` require both fields (exit 3) and delete the two constants plus the four `or`/`.get`
fallbacks. Size: ~8 lines.

### P12 — measure.py never validates the manifest's third declaration, `source_blob` (measure.py:verify_frozen; manifest.json:6)
The blob is already compared byte-for-byte against `commit:path`, so `source_blob` adds nothing unless
checked. It is derivable for free from bytes already in hand:
`hashlib.sha1(b"blob %d\0" % len(blob.stdout) + blob.stdout).hexdigest()`; verified to equal
`447e29b397405a3ee9813ca2e44aedf88abe2763`. Add the compare (or drop the field from the manifest —
do not do both halves differently). One line, no extra process.

### P13 (optional) — gate parses the models body through `dig` twice (check-receipt.py:377-379)
`parse_body(dig(...) if dig(...) is not MISSING else None)` calls `dig` twice for one value. Bind it to a
local. Noise, not failure surface.

Estimated total: ~45–50 lines removed, one duplicated vocabulary fixed, five silent-tolerance branches
converted to loud failures, zero new abstractions.

## Keep — duplicated on purpose (deleting these would harm A3)
These look like the same fact in two files. They are an independent validator re-deriving the producer's
claims; collapsing them makes the gate trust the producer and destroys the point of the gate:
- `loading_envelope_exact` (producer) vs `loading_envelope_ok` (gate) — the gate must not import the
  producer's envelope rule; it re-derives `loading_envelope_exact` from the stored body.
- `HARD_REFUSED_PORTS` vs `HARD_PINS`, `MISMATCH_EXPECT` vs `MISMATCH_EXPECT`,
  `CHILD_ENV_KEYS` vs `CHILD_ENV_ALLOWLIST`, `probe_row` vs `probe_row0`, and the gate's per-check
  re-derivation of every `observed` block from captures/teardown/probes.
- `check.py`'s probe invocation vs the producer's: two harnesses each own their invocation of the
  probe CLI; P9 only deletes the slicing, not the second literal.
- The frozen probe bytes and `manifest.json` (sha256 `93ee4302…`). No finding above requires
  regenerating them; P11/P12 only tighten how measure reads the manifest.

## Considered, no action
- Unifying `_transition_row` and `_capture` row builders: they deliberately keep different header sets
  (`Server`/`Content-Type` vs all headers) and different body caps; merging would change receipt bytes.
- The backward `next(i ...)` fold in `readiness_loop` (:417-419): O(n) over the *transition* list, which
  stays tiny by construction; no measured cost.
- Unused params `_frame`, `send_error(message, explain)`: protocol signatures, not dead code.
- No unreferenced module-level functions/constants exist (AST scan), so this is line/branch weight, not
  symbol removal.

## Limitations
- Nothing here was executed through `measure.py`; its behavior claims are read from the landed code and
  from the stored `run-before.json` (`exit 1`, 72 records, 55 passes) and `measure-stdout.txt`
  (`frozen snapshot verified: sha256 93ee…`).
- P2, P9, P10, P11, P12 touch evidence-literal or manifest-verification behavior; they are build-round
  edits with a receipt re-capture, not falsify-wave edits. Only P1 changes verdicts today, and it makes
  the gate strictly stricter on a value no producer emits.
- Runtime proofs are limited to the gate selftest, the 72-row matrix, module-level helpers
  (`refused_ports`, `_decode_body`), mutated receipts, and git object identity. No server lifecycle was
  exercised. [INFERENCE] P4's "no other path" and P9's "wrong index drops `check`" are read from control
  flow, not executed.
- Scratch `/tmp/kama-r16-SimplifierFinal` removed after writing this report.

## Installs
None. Nothing installed or updated; no pacman transaction attempted (host pause respected).
