# X2V4Compat - round 48, lane kama: backward compatibility of the replaced instruments

**Verdict:** C2 is backward compatible at the build tip - the frozen round-47 C2 counter
(`met=True`, exit 0) and a standalone replay of a v4 receipt with the build-tip (v5-era) tools
(`match=True`, 11/11 checks) both succeed; C1 is backward-**incompatible by construction** - the
round-47 v2 counter fails `contract`, `fixture` and (gated, never executed) `lane`, `stable` at
`380bcdff`, and fails for format/version reasons only: the identical counter passes 5/5 on its
own round-47 measurement tip. `kama-live-replay.py --compare` over 36 receipt pairs shows the
round-48 stable projection agrees across v3/v4/v5 on every surface except alias and
`build_info`, and exposes one message defect (two *equal* unsupported schemas are printed as a
schema transition).

Measured: lane clone `git clone --shared` of `/home/vgpnk/Projects/shokunin/kama-shokunin`,
tip `380bcdff9c8af06997c482f6eb03db926a794a2b` (build), base `33e005827742b29772b153cda036ec9f27f653be`;
trees for runs extracted with `git archive 380bcdff… | tar -x` (the tools at the tip, not the
working tree of the clone, were the ones executed). Round-47 reference tip: `3442d707fdf926ec5ea3f34363cf2f0899cc79b5`
(the `c1-fix`/`c2-fix` measurement in `.ufo/waves/round-47/measured/`).

## 1. C2 (operability): v4 receipts under v5-era tools - compatible

### 1.1 The frozen round-47 C2 counter at the build tip

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-live-replay-audit.py \
  --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/r47c2 \
  --out $S/r47c2-receipt.json
-> receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True
   tip=380bcdff9c8af06997c482f6eb03db926a794a2b   EXIT=0   (wall 5.6 s)
```

All four legs hold with the tool set that round 48 replaced: `receipts` (v4 contract fields still
accepted), `replay` (the build-tip `tools/kama-live-replay.py` re-acquired the archive and model
into scratch, re-ran the lifecycle, and the rerun started after the counter, with the receipt's
digests and all 11 evaluated checks equal), `tamper` (both digest flips refused), `newrow`
(the b11909 SOURCES row is still present). Evidence: `r47-c2-counter-at-build.txt`.

### 1.2 Standalone v4 replay with the build-tip tools (artifact kept)

```
HOME=$S/home TMPDIR=$S/tmp python3 $S/tree/tools/kama-live-replay.py \
  --receipt $S/tree/.ufo/waves/round-47/c2/live/receipt-1.json \
  --work $S/replay-work-v4 --out $S/replay-v4-on-v5.json
-> replay match=True refused=None mismatches=0 exit=0   (wall 2.4 s)
```

The rerun receipt (`rerun-receipt-v4-from-v5-era-tool.json`) is schema `kama-llamacpp-live/v4`,
outcome `pass`, `build_info b11909-caa8191df`, `port 38621`, `teardown.log_path null`,
`server.sha256 35ac50fb…`, `model.sha256 270cba1b…`, 11 evaluated checks - i.e. the v5-era live
tool still *records* v4 when `--server-archive` is absent, and the replay tool does not pass that
flag for a v4 original. Two consequences worth stating:

- a v4 rerun gains **no** record-time provenance: its `provenance` has keys `model, server` and no
  `verified` block, even though the v5-era replay tool hashed the archive against the receipt
  before extracting it (the v5 record-time check is not retro-fitted into v4 output);
- the v4 model URL is **not commit-pinned**: `.ufo/waves/round-47/c2/live/receipt-1.json`
  `provenance.model.url` is `…/models-moved/resolve/main/tinyllamas/stories260K.gguf`. v4 replay is
  therefore digest-bound, not immutability-bound. It cannot pass silently on upstream drift - a
  moved `main` makes `acquire` refuse (exit 2, `digest-mismatch`) - but the receipt names a mutable
  ref. This is exactly the gap v5 closes (`provenance.model.commit 499bc882…`, `verified.at=record`).

### 1.3 The supported boundary is explicit and enforced

```
python3 $S/tree/tools/kama-live-replay.py --receipt .ufo/waves/round-46/c1/live/receipt-1.json …
-> replay match=False refused=not-a-v4-or-v5-receipt:kama-llamacpp-live/v3 mismatches=0 exit=2
```

v3 (round-46) receipts are refused *before* any network access with a named reason
(`tools/kama-live-replay.py:98-99`), so the v5-era tool is v4/v5-only by design; it does not
mis-classify a v3 receipt as a failed replay. Evidence: `v3-receipt-refused.json`.
The build-tip replay tool's own `--selftest` is `KLR_SELFTEST pass=21 fail=0`, exit 0
(`replay-selftest-at-build.out`).

## 2. C1 (calibration): the round-47 v2 counter at the build tip - fails, structurally

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py \
  --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/r47c1 \
  --out $S/r47c1-receipt.json
-> selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0
   lane_mismatch=-1 fixture_mismatch=-1 met=False
   detail: contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note
   detail: fixture: tool exit=2, stdout is not one JSON object
   EXIT=1
```

Leg by leg (all line numbers in `tools/round47-append-audit-v2-check.py` unless stated):

| leg | result | exact reason |
|---|---|---|
| `selftest` | **1** | the v3 tool's `--selftest` still prints `AOA_SELFTEST pass=27 fail=0` (the leg only wants `fail=0`, n>=10). The instrument's self-test survived the version bump. |
| `contract` | 0 | `read_contract` (:249) requires the header to be *exactly* `path\trule\tdeclared_at\tnote`, and its row loop (:255) requires 4 cells. `registry/append-only-contract.tsv:1` at the tip is `path\trule\tdeclared_at\tregion\tnote` and every row has 5 cells (the `region` cell is the round-48 work). `rows` is `None`, so `files=[]`. |
| `lane` | 0 (not executed) | `main` gates the leg on `files` (:619 `if have_tool and files else (False, 0, -1, None)`), and `files` is empty. Even if it ran it would fail twice over: :381 asserts `schema == "append-only-audit/v2"` and the tip tool reports `append-only-audit/v3`; and the v3 event values are deliberately different - at the tip the two SCORECARD events are `deleted 31 graded 14 ungraded 17 restored_max 14 status restored` and `deleted 2421 graded 2349 ungraded 72 restored_max 2349 status restored`, whereas v2's recomputation wants `deleted 31 restored_max 24 partial` / `deleted 2421 restored_max 2420 partial`, and the tool's exit is 0 where v2's `expected_exit` is 1. |
| `fixture` | 0 | the counter writes its own 4-cell contract (`:437` `contract = [HEADER.encode(), b"LOG.md\tA-corr\t…", …]`); the v3 tool parses it at `tools/append-only-audit.py:163` and raises `contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`, exit 2 with no JSON on stdout (`AuditError` -> `could-not-evaluate:`), so the counter reports `tool exit=2, stdout is not one JSON object` (:535). |
| `stable` | 0 (not executed) | same `files` gate (:625). |

Reproduction of the fixture failure with a minimal repo (`$S/probe`, built under the scratch tree,
never in the lane):

```
# 4-cell contract (what the frozen round-47 counter emits)
python3 append-only-audit.py --repo $S/probe --to HEAD --contract registry/contract.tsv --json
-> could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note   EXIT=2
# same repo, 5-cell v3 contract
python3 append-only-audit.py --repo $S/probe --to HEAD --contract registry/contract5.tsv --json
-> {"schema": "append-only-audit/v3", … "declarations":[{"path":"LOG.md","ok":true}]}            EXIT=0
```

### 2.1 The counter itself is intact - the break is the version bump, not drift

```
python3 tools/round47-append-audit-v2-check.py --repo $S/lane \
  --tip 3442d707fdf926ec5ea3f34363cf2f0899cc79b5 --scratch $S/r47c1-atr47
-> selftest=1 contract=1 lane=1 fixture=1 stable=1 files=86 lane_events=5
   lane_mismatch=0 fixture_mismatch=0 met=True    EXIT=0
```

At its own round-47 measurement tip the same frozen counter is 5/5, reproducing round 47's
`measured/c1-fix.out` line for line. So the round-48 C1 build did not damage history or the
counter; it replaced the contract format (4 -> 5 cells, `region`) and the tool schema
(`v2` -> `v3`), and the frozen v2 counter's own parsers/assertions were correctly frozen against
the old shape. A counter is only re-runnable against the tool version it froze; the runnable
regression check for C1's *history* is the round-48 counter applied at the build tip.

For reference, the v3 tool at the build tip reports `schema append-only-audit/v3 files 89 events 5
summary {commits 311, restored 5, partial 0, unrestored 0, ungraded_lines 89, regressed 0,
bad_declarations 0}` exit 0 (`v3-tool-at-build.json`).

## 3. `--compare` across rounds 46, 47, 48 (36 pairs, no network)

```
python3 <build-tip>/tools/kama-live-replay.py --compare A B
```

Required set (6 receipts from rounds 47 and 46, 15 pairs) - full output in
`compare-all-36pairs.txt`, machine table in `compare-matrix.tsv`:

| pair class | pairs | exit | mismatches | diff |
|---|---|---|---|---|
| r47 x r47 (v4) | 3 | 0 | 0 | none |
| r47 x r46 (v4 x v3) | 9 | 1 | 4 | `schema`, `server.sha256`, `projection:props` (`build_info` b11909-caa8191df vs b11906-4d71b42fd, `model_alias`), `projection:models` (alias ids) |
| r46 x r46 (v3) | 3 | 1 | 1 | `schema:v3->v3` only (**defect**, section 4) |

Supplementary (adding the round-48 v5 receipts, 21 pairs): r48 x r48 3 pairs -> 0 mismatches;
r47 x r48 9 pairs -> 3 each (`schema`, `props.model_alias`, `models` ids) with `build_info` and
`server.sha256` **equal**; r46 x r48 9 pairs -> 4 each (as r46 x r47).

Reading:

- **The round-48 stable projection is stable across three rounds and two schema versions.**
  In all 36 pairs the differing components are only `props` and `models`; `slots`, `health`,
  `metrics`, `loading`, `teardown` and `ownership` are byte-identical in every pair. That is a
  calibration datum for the round-48 D4 projection: it is not tuned to v5 receipts, and the
  v4 -> v5 transition changes no captured surface.
- What does differ across rounds is exactly what a per-round alias implies: `props.model_alias`
  and the `models` id list (`kama-r46-live` / `kama-r47-live` / `kama-r48-live`), plus
  `build_info` when the llama.cpp build changed (b11906 -> b11909) and `server.sha256`
  (`c949950e…` -> `35ac50fb…`). Model digest `270cba1b…` is equal in all 9 receipts.
- Because `model_alias` is a graded `props` field, **every** cross-round compare reports at least
  one real mismatch; `--compare` is a within-round replay check, not a cross-round equality
  oracle. Stated as a limit, not a defect: a replay must reproduce the receipt's own alias.

## 4. Defect: `--compare` prints a schema *transition* for two equal unsupported schemas

`tools/kama-live-replay.py:181-182`:

```python
if rerun.get("schema") != orig.get("schema") or rerun.get("schema") not in LIVE_SCHEMAS:
    out.append(f"schema:{orig.get('schema')}->{rerun.get('schema')}")
```

The second disjunct fires for any out-of-contract schema, but the message template always prints
`orig->rerun`, so two *identical* unsupported schemas read as a version difference:

```
$ python3 <build-tip>/tools/kama-live-replay.py --compare \
    .ufo/waves/round-46/c1/live/receipt-1.json .ufo/waves/round-46/c1/live/receipt-2.json
compare match=False mismatches=1
mismatch: schema:kama-llamacpp-live/v3->kama-llamacpp-live/v3
$ echo $?   # 1
```

The two round-46 receipts are structurally identical (matrix row 1: `server_sha_equal True`,
`model_sha_equal True`, no projection component differs); the only reason the comparison fails is
that v3 is outside the tool's supported set. A reader cannot distinguish "not comparable" from
"versions differ", which is precisely the distinction a back-compat audit needs.

Proposed fix (message only, no exit-code change; both consumers are string-agnostic -
`round48-live-replay-v5-audit.py:493-500` checks exit codes only and
`kama-live-replay.py:379` counts mismatches):

```diff
-    if rerun.get("schema") != orig.get("schema") or rerun.get("schema") not in LIVE_SCHEMAS:
-        out.append(f"schema:{orig.get('schema')}->{rerun.get('schema')}")
+    if orig.get("schema") not in LIVE_SCHEMAS or rerun.get("schema") not in LIVE_SCHEMAS:
+        out.append(f"schema-unsupported:{orig.get('schema')}->{rerun.get('schema')}")
+    elif rerun.get("schema") != orig.get("schema"):
+        out.append(f"schema:{orig.get('schema')}->{rerun.get('schema')}")
```

plus one selftest case next to `compare-stable-differs` (`kama-live-replay.py:379`):
`cases.append(("compare-both-unsupported", compare({"schema": "kama-llamacpp-live/v3"}, {"schema":
"kama-llamacpp-live/v3"}) == ["schema-unsupported:kama-llamacpp-live/v3->kama-llamacpp-live/v3"], …))`.
(An alternative - exit 2 for a non-comparable pair - would change the documented `--compare`
contract at `kama-live-replay.py:40-41` and is left to the lane as a next-round decision.)

## 5. Optional compat ergonomics (not required, does not rescue the old counter)

`tools/append-only-audit.py:163` could accept a legacy 4-cell header by defaulting `region` to `*`
(the v2 semantics are exactly "every line graded"), e.g. treat a 4-cell row as
`(path, rule, declared_at, "*", note)`. Two caveats make this low value: it does **not** let the
frozen round-47 counter pass - that counter fails on its own header check (:249) and on the schema
string (:381) before any tool behaviour matters; and no leg of the round-48 C1 counter depends on
4-cell rejection (its `contract` leg parses the lane contract itself). Propose only if an external
caller needs to keep emitting 4-cell contracts.

## 6. Risks and limits

- **v4 evidence replay is digest-bound, not immutability-bound.** Round-47 receipts name
  `…/resolve/main/…`; today's replay matched because `main` still hashes to `270cba1b…`. On drift
  the path is refusal (exit 2), never a false pass - verified indirectly by the r47 counter's
  `tamper` leg and directly by the v3 refusal probe. Do not read a v4 rerun as a pin.
- **No record-time provenance is added by a v4 rerun** (no `verified` block), so a v4 receipt
  replayed with v5-era tools does not retro-actively become v5 evidence.
- **Cross-round `--compare` always mismatches on `model_alias`**; the matrix's "3 mismatches" for
  r47 x r48 is expected, not drift.
- The round-47 C1 counter's failure at the build tip is *expected backward incompatibility*, not a
  lane defect; the honest per-round check is: counter at its own tip (5/5) and the new counter at
  the new tip. Both were exercised here.
- The lane working tree showed sibling edits (`SCORECARD.md`, `SKILL.md`, `hexrun-evidence/`) while
  this seat measured; every number above comes from `git archive 380bcdff…` of a `--shared` clone,
  so in-flight sibling writes cannot have influenced them.
- Scratch was `/fast/scratch/hyaku/kama-r48/X2V4Compat/` only; the lane was read through a
  `--shared` clone (clean `git status`), one fixture repo under scratch with its toplevel asserted
  before committing. No pacman, no tool installs, no service started outside the lane tool's own
  loopback server (torn down by the replay), no writes at the fleet root.

## Files written

Out directory `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X2V4Compat/`:

- `r47-c2-counter-at-build.txt` - `met=True` receipt of the frozen round-47 C2 counter at `380bcdff`
- `r47-c1-counter-at-build.txt` - `met=False` receipt of the frozen round-47 C1 counter at `380bcdff`
- `r47-c1-counter-at-r47-measure-tip.txt` - same counter, 5/5 at `3442d707` (baseline that it is intact)
- `replay-v4-receipt1-at-build.json` - standalone v4 replay JSON (build-tip tools), `match=True`
- `rerun-receipt-v4-from-v5-era-tool.json` - the v4 receipt that replay produced
- `replay-selftest-at-build.out` - `KLR_SELFTEST pass=21 fail=0`
- `v3-receipt-refused.json` - v3 receipt -> `not-a-v4-or-v5-receipt:kama-llamacpp-live/v3`, exit 2
- `v3-tool-at-build.json` / `.err` - v3 tool lane run at `380bcdff` (schema v3, 89 files, 5 events, regressed 0, exit 0)
- `probe-contract-header.txt` - the 4-cell vs 5-cell contract probe transcript (exit 2 / exit 0)
- `compare-all-36pairs.txt` - full `--compare` transcript for all 36 pairs
- `compare-matrix.tsv` - the same as a table (schemas, digest equality, differing projection components)
- `X2V4Compat.md` (this report, one level up)

## Appendix: all 36 `--compare` pairs

| A | B | A schema | B schema | server sha equal | model sha equal | differing projection components | differing props fields | mismatches | exit |
|---|---|---|---|---|---|---|---|---|---|
| r46-1 | r46-2 | v3 | v3 | True | True | - | - | 1 | 1 |
| r46-1 | r46-3 | v3 | v3 | True | True | - | - | 1 | 1 |
| r46-1 | r47-1 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-1 | r47-2 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-1 | r47-3 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-1 | r48-1 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-1 | r48-2 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-1 | r48-3 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r46-3 | v3 | v3 | True | True | - | - | 1 | 1 |
| r46-2 | r47-1 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r47-2 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r47-3 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r48-1 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r48-2 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-2 | r48-3 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r47-1 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r47-2 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r47-3 | v3 | v4 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r48-1 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r48-2 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r46-3 | r48-3 | v3 | v5 | False | True | props,models | build_info,model_alias | 4 | 1 |
| r47-1 | r47-2 | v4 | v4 | True | True | - | - | 0 | 0 |
| r47-1 | r47-3 | v4 | v4 | True | True | - | - | 0 | 0 |
| r47-1 | r48-1 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-1 | r48-2 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-1 | r48-3 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-2 | r47-3 | v4 | v4 | True | True | - | - | 0 | 0 |
| r47-2 | r48-1 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-2 | r48-2 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-2 | r48-3 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-3 | r48-1 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-3 | r48-2 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r47-3 | r48-3 | v4 | v5 | True | True | props,models | model_alias | 3 | 1 |
| r48-1 | r48-2 | v5 | v5 | True | True | - | - | 0 | 0 |
| r48-1 | r48-3 | v5 | v5 | True | True | - | - | 0 | 0 |
| r48-2 | r48-3 | v5 | v5 | True | True | - | - | 0 | 0 |
