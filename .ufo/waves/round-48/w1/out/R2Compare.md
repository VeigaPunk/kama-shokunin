# R2Compare — two definitions of the stable projection

**Verdict:** the tool's `projection()` (`tools/kama-live-replay.py`) and the frozen counter's `projection()` (`tools/round48-live-replay-v5-audit.py`) are *not* the same projection — they disagree on constructible receipt pairs in **both** directions — and the dangerous direction is real: a replay can **pass the tool and fail the counter** (demonstrated end-to-end through the frozen counter, fixture tip `ff719e0f…` → `replay 2: projection models: None -> unparseable` with the tool at exit 0). The reverse direction (tool fails, counter's projection would say equal) exists but is masked by the counter's exit-0 gate.

---

## 0. Versions pinned

The lane's working tree changed **during** this session: `tools/kama-live-replay.py` is now dirty (` M` in `git status`; +69/−26 vs 380bcdff) — an uncommitted mid-wave patch citing seat findings (V2Replay F2 file:// gating, K2Selftest v5-rerun provenance, F11 digest fallback). All analysis below is pinned to explicit copies (sha256):

| file | version | lines | sha256 |
|---|---|---|---|
| `tools/kama-live-replay.py` | **as-built, tip 380bcdff** (what the frozen counter measures at `--tip`) | 430 | `69837013ec64b78a…` |
| `tools/kama-live-replay.py` | **worktree (F11 patch, uncommitted)** | 473 | `7be002a14f0d0292…` |
| `tools/round48-live-replay-v5-audit.py` | **frozen** (identical at 12284ba and 380bcdff; worktree clean) | 566 | `6bc16e2532469f16…` |

Copies of all three are in this directory (tool-at-tip.py, tool-worktree.py, counter-frozen.py).

---

## 1. Field-by-field diff

Both projections return the same eight keys: `props, slots, health, models, metrics, loading, teardown, ownership`.

| field | tool (as-built 154-175 / patched 166-190) | counter (206-224) | treatment of absent captures |
|---|---|---|---|
| props | `captures.props.fields` (`_get`/`dig` → None if any level non-dict) | same | identical (None) |
| slots | `[element_count, body_sha256]` **list** | `(element_count, body_sha256)` **tuple** | identical (None, None) |
| health | `[status, body_sha256]` list | tuple | identical |
| metrics | `captures.metrics.status` | same | identical |
| loading | `[loading_envelope_exact, loading_503.body_sha256]` list | tuple | identical |
| teardown | `[returncode, sigterm_sent, sigkill_sent, port_refuses]` list | tuple | identical (None×4) |
| ownership | `port_listener_ownership` | same | identical |
| **models** | **see below — the only semantic divergence** | | |

**Absent captures** (verified per-field, harness A2): `captures` missing / non-dict, `models` without `body`, `teardown` absent — both definitions produce identical None-valued projections. No disagreement.

**List vs tuple**: structural only; each definition compares itself consistently, so it never causes an equality disagreement. It does make the two projections unequal as objects on every receipt (harness A1: `tool projection == counter projection as objects: False`) — a latent hazard if anyone ever compares them directly or serializes one into the other's format (tuple→JSON array is fine, but a raw `==` is always False).

**models body handling** (the divergence):

| body shape | tool as-built | tool patched (F11) | counter (frozen) |
|---|---|---|---|
| parses to dict | `{"data": sorted(id\|owned_by), "models": sorted(names)}` | same (data/models list-guarded) | `(sorted(id\|owned_by), sorted(names))` tuple |
| parses to non-dict (5, [1,2], "abc", false, "0") | keeps the parsed value | keeps the parsed value | **collapses to None** |
| parses to null / missing | None | **fallback**: `body_sha256` field or `"unparseable"` | None |
| unparseable string (`{bad`) | `"unparseable"` (sentinel) | fallback `body_sha256` or `"unparseable"` | `"unparseable"` |
| non-string body (JSON object) | **crash** (TypeError in `json.loads`) | fallback (no crash) | **crash** (TypeError in `json.loads`) |
| dict body with non-list `data` (e.g. `{"data": 5}`) | **crash** (TypeError in `for m in ... or []`) | guarded → empty list | **crash** (TypeError) |

## 2. Constructed receipt pairs on which they disagree

Grid over 20 models-body shapes (harness v2 A3, 400 pairs, counter projection executed directly; verdict = EQ vs FAIL where FAIL includes mismatches and crashes):

| tool version | tool=EQ/counter=EQ | tool=FAIL/counter=EQ (counter lenient) | tool=EQ/counter=FAIL (dangerous) | both FAIL |
|---|---|---|---|---|
| as-built 380bcdff | 46 | **110** | **6** | 238 |
| patched F11 | 32 | **124** | **18** | 226 |

**Disagreeing pairs (real tool `--compare`):**

| pair | shapes (A vs B) | tool as-built | tool patched | counter projection |
|---|---|---|---|---|
| P1 “sentinel collision” | `'"unparseable"'` vs `"{bad"` (no body_sha256) | **exit 0 / match** | **exit 0 / match** | None vs "unparseable" → DIFF |
| P2 “digest collision” | `'"unparseable"'` vs unparseable with `body_sha256` | exit 0 / match (digest ignored) | exit 1 (fixed by F11) | None vs digest → DIFF |
| P3 “two garbage bodies” | `"{bad"`+sha1 vs `"{bad2"`+sha2 | exit 0 / match | exit 1 (fixed) | "unparseable" vs "unparseable" → EQ |
| P4 “digest-string collision” | body parses to a 64-hex string vs unparseable with that digest | exit 1 | **exit 0 / match** | None vs "unparseable" → DIFF |
| P5 “non-string body” | body as JSON object vs `"{bad"` | exit 1 (traceback) | **exit 0 / match** | crash vs "unparseable" → FAIL |
| P6 “lenient” | `"null"` vs `"5"` | exit 1 | exit 1 | None vs None → EQ (silent) |

(scripts: `harness_v2.py`, run with `KLR_TOOL=tool-at-tip.py` / `tool-worktree.py`; pair files `pair-at-tip-*` / `pair-worktree-*` in this directory; the digest-string collision pair is `pair-worktree-digeststr-*`.)

## 3. End-to-end: the frozen counter's own verdict on a disagreeing pair

Fixture repo (my scratch, `git init` + assert toplevel; receipt-2/3 = real lane receipt-1 byte-copies mutated **only** in `captures.models.body` / `alias`; tool at the as-built tip; fake live tool implementing the record-time contract offline). Full frozen-counter run (`round48-live-replay-v5-audit.py --repo <fixture> --tip ff719e0f…`):

```
receipts=1 recordcheck=1 replay=0 compare=1 tamper=1 urlswap=1 newrow=1 replayed=1/3 met=False
detail: replay 2: projection models: None -> unparseable
detail: replay 3: exit 1 match False: replay match=False refused=None mismatches=1 exit=1
```

- **receipt-2** (orig `'"unparseable"'`, rerun `'{bad json'`): the tool replayed it **exit 0 / match=true** — *no* `exit` detail line — and the counter's own projection check fired `projection models: None -> unparseable` → replay leg failed → `met=False`. **This is a replay that passes the tool and fails the counter** (counter lines 428-435: projection difference → `replayed` not incremented → `rep` False → `met` False at 550).
- **receipt-3** (orig `"null"`, rerun `"5"`): the tool itself failed (exit 1) and the counter's projection stayed silent (None == None) — the counter's leniency on non-dict parses is **masked by the exit-0 gate** (counter lines 404-405 gate before 428-431): it can never flip a verdict today.
- receipt-1 (control, real dict body both sides): clean, replayed.

## 4. Which disagreement can let a replay pass the tool and fail the counter — and vice versa

- **Pass tool / fail counter (real, demonstrated):** the counter's projection is *stricter* than the tool's on the sentinel/digest/non-string corners (P1, P4, P5; also the counter's crash paths). Because the counter's replay leg runs its own projection *after* the tool's exit-0 gate, a pair the tool accepts can still fail the leg. P1 is demonstrated end-to-end (section 3); P4/P5 are demonstrated at `--compare` level under the patched tool (exit 0 / match) and by direct counter-projection execution.
- **Fail tool / counter projection would pass (exists, masked):** P6 and the 110/124 lenient pairs. This can never change the counter's verdict because the leg already fails on the tool's exit code. It is a latent hole only if the counter's projection check is ever reused without the tool's exit gate.

**What actually matters for round 48:** all three lane receipts carry parseable dict bodies (receipt-1's `captures.models.body` is a JSON object string; the live tool's `models_alias_id`/`models_owned_by_llamacpp` checks require a parsed dict with ids, kama-llamacpp-live.py:1694-1711), so healthy runs agree and the L1 dry-run verdict (replayed=3/3) stands. The divergence lives entirely in malformed/degenerate bodies; the dangerous direction is reachable only with hand-built receipts (or a server returning a degenerate body while still passing the tool's models checks — not possible today). The counter's stricter corner is nonetheless what exposed the tool's sentinel defect, so harmonizing naively (counter → tool semantics) without P1 would lose that protection.

## 5. Findings

- **F1 (tool as-built, defect):** `projection()` sentinel `"unparseable"` collides with a legal parsed body value; also ignores `body_sha256` (P2/P3 exit 0). The F11 worktree patch fixes P2/P3 but keeps P1 and introduces P4. Proposed fix P1: tuple sentinel `("unparseable", body_sha256)` — a value no `json.loads` can produce (`proposed-tool-tuple-fallback.diff`).
- **F2 (frozen counter, divergence — the item's subject):** counter collapses non-dict parses to None and unparseable bodies to `"unparseable"` (209-217), disagreeing with the tool in both directions. Its "own stable projection" is not the same projection. Proposed fix P2 (future round only — counter is frozen): mirror the tool's models semantics, which also removes the counter's TypeError crash on non-string bodies and non-list `data` (`proposed-counter-mirror.diff`).
- **F3 (both, robustness):** non-string body / non-iterable `data` crash both as-built tool and counter with an unhandled TypeError (not the graceful refused/unparseable path); the patched tool fixes its side, the counter still crashes. Symmetric verdicts (both fail), so no disagreement, but the counter should not traceback.
- **F4 (frozen counter, gating):** the counter's projection check (428-431) is gated behind the tool's exit-0 (404-405); combined with F2's leniency it can only add failures, never remove them — its docstring claim (“this counter's own stable projection of the rerun equals the receipt's”) is only partially an independent check.
- **F5 (observation):** the lane's `tools/kama-live-replay.py` was modified (uncommitted) during this session; all runs here are version-pinned (section 0).

## 6. Residual risk / verification gaps

- P4/P5 (patched tool) demonstrated at `--compare` + projection level, not end-to-end through the counter (would require a fixture rerun with a malformed body that still passes rerun checks).
- The F11 worktree patch is uncommitted; if it is reverted or amended before the L1 lands it, P2/P3 regress (as-built behavior).
- Not tested: `--receipt` end-to-end under the patched tool (the fixture runs pinned the as-built tool); the patched tool's new v5-rerun provenance compare is outside this seat's scope.

## 7. Evidence files (this directory)

- `counter-fixture-output.txt` — frozen counter run, fixture with the F11-patched tool (receipt-2: tool exit 1 + counter projection line).
- `counter-fixture-tip-tool.txt` — **the artifact**: frozen counter run, fixture with the as-built tool (receipt-2: tool exit 0, only the counter projection line).
- `harness_v2.py`, `build_fixture.py`, `tool-at-tip.py`, `tool-worktree.py`, `counter-frozen.py`, pair-*.json, `receipts/` (fixture receipt-1/2/3 + lane receipt-1 base), `fixture-tip.txt`, `proposed-tool-tuple-fallback.diff`, `proposed-counter-mirror.diff`.
