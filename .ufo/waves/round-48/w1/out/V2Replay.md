# V2Replay — round 48, lane kama — code review of `tools/kama-live-replay.py`

Verdict: **the diff is sound on every named axis** (v4/v5 acceptance, v5 provenance rules, `--server-archive` argv insertion, `compare()` schema rule, projection on real receipts, `--compare` exit codes, selftest 21/21) — **3 defects** (one crash class on malformed receipts, `https`-only not enforced at replay, `--compare` skipping provenance validation) **+ 4 informational observations**, each reproduced on a minimal fixture; a validated proposed patch is attached.

Reviewed: `git diff 33e005827742b29772b153cda036ec9f27f653be 380bcdff9c8af06997c482f6eb03db926a794a2b -- tools/kama-live-replay.py` (149+/15−). All line numbers below are `tools/kama-live-replay.py` at 380bcdf (430 lines). Method: `git clone --shared` of the lane into my scratch, checked out at 380bcdf (`git -C $S/lane rev-parse HEAD` = 380bcdff9c8af06997c482f6eb03db926a794a2b); every run used that clone; scratch was removed after evidence was copied out.

## Verified correct (no defect)

- **Selftest: 21/21 pass, exit 0** at the build commit:
  `python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S/st` → `KLR_SELFTEST pass=21 fail=0`, exit 0. Case count matches the item: 13 v4-era + 6 v5 + 2 `compare()` cases (:316-380). Note: `--scratch` must already exist (`tempfile.mkdtemp(dir=root)` at :270 raises FileNotFoundError otherwise — usability nit, not a defect; the counter passes an existing dir).
- **v4/v5 acceptance** (:96-99): `provenance()` accepts both schemas; real receipts accepted — r48 receipt-1 (v5) and r47 receipt-1 (v4, `resolve/main` URL) both pass `provenance()` (fixture run, no Refused).
- **v5 provenance rules** (:114-123): commit must be 40-lowercase-hex (`HEX40.fullmatch`), the URL must contain `/resolve/<commit>/`, `verified.at == "record"`; refusal order commit → URL → verified. Selftest cases v5-bad-commit / v5-url-not-at-commit / v5-not-verified all refuse with exit 2.
- **argv insertion** (:240-241): `argv[-2:-2] = ["--server-archive", archive]` verified empirically (F5, fake live dumping `sys.argv`): `--server-archive` lands between the `--model-url` value and `--out`; the live tool receives all five flags. Correct position; no defect.
- **compare() schema rule** (:180-181): rerun schema must equal the original's AND be v4/v5 — no vacuous path (two schemaless receipts still mismatch via the `not in LIVE_SCHEMAS` disjunct). Both flip directions caught: v5→v4 (selftest v5-rerun-schema-differs, exit 1) and v4→v5 (F7: v4 original + always-v5 live → `mismatches=['schema:kama-llamacpp-live/v4->kama-llamacpp-live/v5']`, exit 1).
- **projection() is non-vacuous on real data**: every projected key reads a real value from receipt-1 (`props.fields`, `slots.element_count=4`+digest, `health.status=200`+digest, `metrics.status=501`, models body parses to a dict with `data[].id|owned_by` and `models[].name`, `loading=[True,digest]`, `teardown=[0,True,False,True]`, `ownership=child`). Pairwise `--compare` of the three real receipts: **all exit 0** (receipt-1/2/3 cross-run stability holds).
- **--compare exit codes** (:404-419): equal→0, differ→1, missing file→2, JSON-list→2 (`compare could-not-read: ...`) — as documented (F6).
- **Digest ordering**: downloads verified before extraction/execution; member digest before execution; v5 adds the live tool's record-time re-verification via `--server-archive`. Unchanged from v4 and correct.

## Findings

### F1 (Low-Medium, robustness/contract) — malformed receipt fields crash the tool instead of refusing or mismatching
- `tools/kama-live-replay.py:157` — `json.loads(_get(rec, "captures", "models", "body") or "null")` catches only `ValueError` (:158); a **non-string** body (JSON object/array/number) raises `TypeError`.
- `tools/kama-live-replay.py:161-163` — the projection comprehensions iterate `body.get("data") or []` / `body.get("models") or []` unguarded; a parsed body with non-iterable `"data"` (e.g. `5`) raises `TypeError: 'int' object is not iterable`.
- `tools/kama-live-replay.py:186` and `:253-255` — `(orig.get(side) or {}).get("sha256")` / same for `tool`/`probe`: a truthy non-dict field (e.g. `"server": "x"`) raises `AttributeError`.
- None of these are in the except tuple at :261-262, so: in `--compare` mode the tool dies with a traceback, **exit 1** (indistinguishable from "different"), no `compare match=` line; in replay mode it dies **before writing J**, violating the docstring's "Writes J" (:31-32).
- Fixture (F1/F2, `out/fixture-F1-F4.txt`, `out/fixture-F2-F10.txt`):
  - `--compare` body-as-object → `TypeError: the JSON object must be str, bytes or bytearray, not dict`, exit 1
  - `--compare` `{"data": 5}` → `TypeError: 'int' object is not iterable`, exit 1
  - `--compare` server-as-string → `AttributeError: 'str' object has no attribute 'get'`, exit 1
  - `--receipt ... --live fake` with `{"data": 5}` in the original → exit 1, **J_exists=False**, traceback
- Why it matters: the D1 threat model is a fabricated rerun receipt; a crafted one crashes the verifier instead of being flagged. It fails closed (no false pass), but the documented output contract breaks.
- Fix (in `out/proposed-fix.patch`): treat non-string/unparseable bodies uniformly, guard the two comprehension iterables with `isinstance(..., list)`, use `_get()` for the sha accesses, and add `TypeError, AttributeError` to the :261 except tuple as belt-and-braces. Validated: fixed version passes selftest 21/21 and all three triggers now produce clean output.

### F2 (Low-Medium, provenance) — `https`-only is documented but not enforced at replay time
- `tools/kama-live-replay.py:81-83` — `fetch()` accepts `file://` for any caller; the docstrings say "Network: https only, for the two recorded URLs" (:37) and "file:// only for the selftest" (:82), but nothing enforces it outside `_selftest`.
- Fixture (F3, `out/fixture-F2-F10.txt`): a v5 receipt whose URLs are `file://…/resolve/<40-hex>/…` (local paths, digests matching local files) replays to **exit 0, `match=True`, zero network**.
- Why it matters: the paired live tool refuses non-https at record time (`tools/kama-llamacpp-live.py:1470-1472`), so a `file://` receipt is not one the live tool could have recorded — replaying it "successfully" proves nothing about re-acquisition (the D1 class). The lane gate is not weakened (the C2 receipts leg pins the frozen https URLs), so this is a tool-level gap.
- Fix (in patch): `fetch(..., allow_file=False)` default; `replay(..., allow_file=False)` threads it; only `_selftest` passes `allow_file=True`. Verified compatible: both real r47-v4 and r48-v5 receipts use https URLs; fixed version refuses the fixture with `url-scheme:file://…`, exit 2, selftest still 21/21.

### F3 (Low, contract asymmetry) — `--compare` skips provenance validation entirely
- `tools/kama-live-replay.py:404-419` — the `--compare` branch never calls `provenance()`; `compare()` (:177-201) does not validate provenance either.
- Fixture (F8): a v5 receipt with **no `provenance.model.commit` and no `verified` block**: `--compare X X` → exit 0 `match=True`, while `--receipt X` → exit 2 `refused=provenance-bad-commit`. The docstring says `--compare` "compares two receipts with the replay rules" (:29) — provenance acceptance is one of those rules.
- Related: `compare()` ignores the provenance blocks altogether, so a rerun carrying a different model URL/commit (same digests) would still match; the C2 counter's replay leg covers the rerun's commit, so this is layered, but the tool alone does not check it.
- Fix (in patch): run `provenance()` on both receipts in the `--compare` branch; `Refused` → print and exit 2. Validated: fixed version exits 2 `compare refused: provenance-bad-commit`; the counter's compare-leg copies (valid v5) are unaffected; real receipts still compare equal.

### F4 (Low, false-match path) — two *differently* unparseable models bodies compare equal
- `tools/kama-live-replay.py:156-159` — an unparseable models body maps to the sentinel `"unparseable"`; two different unparseable bodies (e.g. two differently-truncated captures — `captures.models.body_read_truncated` exists in real receipts) both map to it → equal.
- Fixture (F11): receipts differing only in models body (`"qqq{truncated"` vs `"www{also-bad"`, distinct `body_sha256`s) → `--compare` **exit 0, match=True** — a false match the semantic projection cannot see.
- Note the asymmetry: `slots`/`health` are compared via `body_sha256`, but `models` — the one surface that must be semantic because its body carries per-request `created` — has no digest fallback exactly where parsing fails.
- Fix (in patch): when the body is unparseable/non-string, project `captures.models.body_sha256` (byte-level) instead of the sentinel. Validated: fixed version exits 1 with `projection:models:"444a…->e28f…"`; parseable real bodies unaffected (real receipts still compare equal).

### F5 (Informational) — None vs absent conflate in projection()
- `:145-168` — `_get()` returns `None` for absent and null alike: `captures.slots.element_count=null` vs no captures → `--compare` exit 0 (F4a); models body `"null"`/`""`/absent all → `None` (F4b); `body.get("data") or []` conflates missing `data` with empty `data`. No false-pass on real receipts (real captures are populated; real-value-vs-absent correctly differs, F4e). Observation only; a fix would need a distinct "absent" marker for marginal benefit.

### F6 (Informational) — URL containment is substring-based, shared with the live tool
- `:118-119` — `f"/resolve/{commit}/" not in need["model.url"]` accepts a query-injected segment: `https://…/resolve/main/…gguf?pin=/resolve/<40-hex>/x` passes `provenance()` **and** the live tool's record-time regex `PINNED_MODEL_URL` (`kama-llamacpp-live.py:71`) matches the same shape by backtracking (F9), so record and replay agree and the sha256 digest is the actual byte pin (the urlswap leg relies on it). A coordinated fix in both tools would anchor to `urllib.parse.urlsplit(url).path`; not safe to change in the replay tool alone (it would refuse receipts the live tool accepted).

### F7 (Informational) — `provenance.verified` digests not cross-checked
- `:120-123` — only `verified.at == "record"` is checked; a v5 receipt whose `verified.archive_sha256/member_sha256/model_sha256` contradict the receipt's own digests is accepted (F10). The C2 receipts leg checks these and the replay re-verifies every byte itself, so this is defense-in-depth only. Cross-check added in the patch (validated: `refused: provenance-verified-archive_sha256-differs`).

## Selftest gap notes (21 cases)
Not covered by the selftest, each verified manually here: the v4→v5 schema-flip direction (F7: caught); models-body edge cases (F1/F4/F11: two crash, one false-match); CLI-level `--compare` (exit 2 unreadable untested anywhere, F6: correct); missing-vs-null captures (F5). Suggested additions if the counter is ever revised — the counters are frozen, so these are notes for a later round, not fixes in place.

## Residual risk & verification gaps
- I did not run the C2 counter end-to-end (L1's integration; the pre-wave dry run is recorded as `replayed=3/3 met=True`); my review is the tool source + offline fixtures + real-receipt `--compare`/`provenance()` controls.
- The crash class (F1) was exercised only via `--compare` and one replay-mode fixture with a fake live tool; a real-network replay crash path is the same code path (`compare()` inside `replay()`'s try).
- `compare()` ignoring provenance (F3, related note) is layered by the counter's replay leg; I did not attempt to defeat that layering end-to-end.

## Tooling
No tools installed or upgraded (none needed; pacman guard respected).

## Evidence files (this directory)
`fixture-F1-F4.txt`, `fixture-F2-F10.txt`, `fixture-F11-and-fix-validation.txt`, `fixtures.py`, `fixtures2.py`, `replay-fixed.py` (full proposed text), `proposed-fix.patch` (unified diff vs 380bcdf), `receipt-1.json`, `receipt-2.json`, `receipt-3.json` (copies of the cited lane receipts).
