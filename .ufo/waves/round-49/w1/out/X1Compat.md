# X1Compat — backward compatibility at 74558c71c38ceaeace15fd4cf8aa9d84977584b1

**Verdict: no backward-compatibility break.** At the round-49 build tip, the round-47 C2 counter
(`met=True`) and the round-48 v5 C2 counter (`met=True`, `replayed=3/3`) both still pass, the
receipt schema is unchanged (`kama-llamacpp-live/v4`/`v5`, `tools/kama-llamacpp-live.py:84-85`),
and every receipt consumer I ran — `tests/llamacpp-live/check-receipt.py`, `tools/gguf-identity.py`,
`kama-live-replay.py --compare` — accepts a rerun receipt that now carries a `witness` block.
The witness is additive and, as documented (`tools/kama-live-replay.py:45`), not compared.
One low-severity robustness risk found (R-1: a witness dir that already holds `release` yields a
zero-length hold window); no defect that changes any counter or predicate outcome.

Both axes are untouched by this seat: operability (C1) and calibration (C2) evidence recorded below
is *re-execution of the pre-existing contracts*, not new claim evidence.

Environment: clone `git clone --shared` of the lane → `/fast/scratch/hyaku/kama-r49/X1Compat/lane`
(HEAD `122c4ee9`; `git diff 74558c71 122c4ee9 --stat` = 4 wave-spec files only, 2008 insertions,
zero tool/corpus changes; both counters at HEAD hash-identical to the tip blobs:
`round48-live-replay-v5-audit.py` = `6bc16e25…fb0c09`, `round47-live-replay-audit.py` = `15408dce…b0f`).
Tool runs used a full `git archive 74558c71 | tar -x` tree at `$S/tip`. All replays ran with
`HOME`, `XDG_CACHE_HOME`, `TMPDIR` inside scratch; downloads observed: archive 22,475,032 B,
model 1,185,376 B. No pacman, no installs, no services started by me; every llama-server I started
was torn down by the tools (`teardown.returncode 0`, `port_refuses true`); `pgrep -af llama-server`
afterwards shows only other seats' processes (`X1Kill`, `X1Offline` paths), none from my scratch.

## 1. Frozen counters at the tip

| # | command | result | exit |
|---|---------|--------|------|
| 1 | `tools/round47-live-replay-audit.py --repo $S/lane --tip 74558c71… --scratch $S/c47` | `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (5.1 s) | **0** |
| 2 | `tools/round48-live-replay-v5-audit.py --repo $S/lane --tip 74558c71… --scratch $S/c48` | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` (12.6 s) | **0** |

Evidence: `r47-c2-counter.json`, `r48-v5-counter.json` (both `--out` transcripts; no `detail:` lines
were emitted, i.e. every leg passed with no problems recorded).

What this covers that matters for compatibility: round-47's counter drives a **v4** receipt through the
**round-49** `kama-live-replay.py`/`kama-llamacpp-live.py` and requires a v4 rerun (`schema v4`, same
evaluated checks) — it passed; round-48's counter requires **v5** receipts, a v5 rerun, record-time
provenance refusal (`recordcheck`), the stable projection, `--compare` instance/stable separation,
`tamper` and `urlswap` refusals — all passed. The new bounded `verify_archive_member()`
(`tools/kama-llamacpp-live.py:212-274`) did not refuse the real 22 MB b11909 asset at record time.

## 2. `check-receipt.py`

| # | command | result | exit |
|---|---------|--------|------|
| 3 | `python3 tests/llamacpp-live/check-receipt.py --selftest` | `16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` | **0** |
| 4 | `check-receipt.py <rerun v4 + witness>` | `VALID …` | **0** |
| 5 | `check-receipt.py <rerun v5 + witness>` | `VALID …` | **0** |
| 6 | `check-receipt.py <rerun v4 + witness released=false>` | `VALID …` | **0** |

The validator has no `witness` reference at all (`grep -n witness tests/llamacpp-live/check-receipt.py`
→ no hits) and tolerates the extra top-level key; it validates the v4/v5 provenance, checks, and
teardown of a witnessed run unchanged. Both witnessed rerun receipts are in this directory
(`rerun-v4-witnessed-receipt.json`, `rerun-v5-witnessed-receipt.json`).

## 3. `gguf-identity.py`

| # | command | result | exit |
|---|---------|--------|------|
| 7 | `python3 tools/gguf-identity.py --help` | usage printed (v3/v4/v5 reconciler) | **0** |
| 8 | `python3 tools/gguf-identity.py --selftest` | `"status": "passed"` | **0** |
| 9 | `gguf-identity.py <model.gguf> --receipt <rerun v4 + witness> --json` | `status engine-agreement`, comparisons `agree/agree/agree`, `file_sha256` = receipt `model.sha256` = `270cba1b…256d`, `props_n_ctx 256` vs `context_length 2048` (`training_context_comparison: equal`) | **0** |
| 10 | `gguf-identity.py <model.gguf> --receipt <rerun v5 + witness>` | same agreement, exit 0 | **0** |

`RECEIPT_SCHEMAS` (`tools/gguf-identity.py:47`) is unchanged and the reconciler reads only fields the
build did not touch; the extra `witness` block is inert. Evidence: `gguf-identity-v4-witness.json`,
`gguf-identity-v5-witness.json`.

## 4. Round-47 v4 receipt, with and without `--witness-dir`

Receipt replayed: `.ufo/waves/round-47/c2/live/receipt-1.json` (v4, `kama-r47-live`, ctx 256, 11 checks).

| # | command | result | exit |
|---|---------|--------|------|
| 11 | `kama-live-replay.py --receipt receipt-1.json --work w-nw --out …` | `replay match=True refused=None mismatches=0` (2.1 s) | **0** |
| 12 | `… --witness-dir $S/wd-v4 --witness-timeout 60` + observer | `match=True mismatches=0`; observer read `ready.json {schema kama-live-witness/v1, port 35147, pid 335130}` and `exe=/…/w-wit/server/llama-b11909/llama-server`, `cmdline` starts `llama-server -m …/stories260K.gguf --alias`; rerun receipt `outcome pass`, `witness {released true, waited_ms 50, port 35147, pid 335130, dir …}` | **0** |
| 13 | same, `--witness-timeout 3`, no observer | `match=True`; rerun `outcome pass`, `witness {released false, waited_ms 3008}` | **0** (unreleased witness does not fail the replay) |
| 14 | `kama-live-replay.py --witness-dir $S/does-not-exist …` | `error: --witness-dir must be an existing directory` | **2** |
| 15 | `kama-llamacpp-live.py <valid> --witness-dir $S/does-not-exist` | `error: --witness-dir must be an existing directory` (`:1581-1582`) | **2** |
| 16 | `kama-llamacpp-live.py <valid> --witness-dir … --witness-timeout 0` | `error: --witness-timeout must be > 0` (`:1583-1584`) | **2** |
| 17 | same, `--witness-dir $S/wd-v4` **already holding** `ready.json`+`release` from run 12, `--witness-timeout 30` | `match=True`; rerun `outcome pass`, `witness {released true, waited_ms 0}` — no hold window (R-1) | **0** |

The v4 path is preserved exactly: with no `--witness-dir`, `argv` is unchanged and no `witness` key is
written; with it, `tools/kama-live-replay.py:275-281` inserts the two flags before `--out` and grows the
subprocess bound by the witness timeout (observed: 5.3 s total for a 3 s hold after a ~2 s
download+run). A witnessed v5 replay of `.ufo/waves/round-48/c2/live/receipt-1.json` also passes
(`match=True`, exit **0**, `provenance.verified` intact, `witness released true`) — `replay-v5-witness.json`.

## 5. Comparison and selftests

| # | command | result | exit |
|---|---------|--------|------|
| 17 | `--compare <v4 original> <v4 witnessed rerun>` | `compare match=True mismatches=0` | **0** |
| 18 | `--compare <v5 original> <v5 witnessed rerun>` | `compare match=True mismatches=0` | **0** |
| 19 | `--compare <v4 witnessed rerun> <v4 unreleased-witness rerun>` | `compare match=True mismatches=0` | **0** |
| 20 | `kama-live-replay.py --selftest --scratch $S/tmp-selftest` | `KLR_SELFTEST pass=22 fail=0` | **0** |
| 21 | `kama-llamacpp-live.py --selftest` | `selftest: ok; closed tcp6 listeners …` | **0** |

`--compare` ignores the `witness` block, and `port_listener_ownership` stays `"child"` in every
witnessed receipt (`w-v4`, `w-v5`, unreleased), so the round-48 stable projection is unaffected —
independently confirmed by counter #2 passing its `compare`/`replay` legs.

## 6. Findings

**R-1 (risk, low; no counter impact) — a witness dir that already contains `release` gives the observer
no window.** `hold_for_witness()` (`tools/kama-llamacpp-live.py:280-302`) neither clears nor refuses a
pre-existing `ready.json`/`release`; its loop condition is `not os.path.exists(release)`
(`:295`). Reproduction (run 17 above, `commands.log` item 13):

```
python3 $S/tip/tools/kama-live-replay.py --receipt .ufo/waves/round-47/c2/live/receipt-1.json \
  --work $S/w-stale --out … --witness-dir $S/wd-v4 --witness-timeout 30
→ replay match=True exit=0 ; rerun witness {"released": true, "waited_ms": 0}
```
with `$S/wd-v4` still holding `ready.json` (pid 335130, port 35147) and `release` from run 12. The
server is released microseconds after `ready.json` is written, and until the atomic
`os.replace` (`:292`) an observer can read the *previous* run's pid/port. It fails safe rather than
falsely passing — the C1 counter creates a fresh dir per receipt via `os.makedirs(wd)`
(`tools/round49-replay-witness-audit.py:293-294`) and would see a dead pid — but the failure mode is a
confusing one for any future caller that reuses a directory.
Proposed fix (proposed text only; lane file untouched): in `hold_for_witness`, before writing
`ready.json`, remove `release` and a stale `ready.json`, or refuse with a new token —
```python
for leftover in ('release', 'ready.json'):
    path = os.path.join(wdir, leftover)
    if os.path.exists(path):
        raise SetupError('witness-dir-not-empty')
```
wired as `raise SetupError(...)` at the top of `hold_for_witness` (`:280`), which the existing
`except SetupError` at `:1868` already renders as `setup_error`.

**R-2 (observation, not a break) — the replay tool needs more than `tools/`.** Extracting only
`tools/*.py` from the tip and running it yields `setup_error probe-not-found:<path>/tools/kama-probe.sh`
(the live tool derives the probe path beside itself), and adding `tools/` still yields
`registry-unreadable:<path>/registry/endpoint-consumers.tsv`; only a full `git archive` tree passes.
Both frozen counters extract the whole tree, so no counter is affected; the "replay tool at --tip from
`git archive`" idiom in the docstrings must stay whole-tree.

**R-3 (cosmetic asymmetry) — `witness_dir` is present in the replay result JSON only when witnessing**
(`tools/kama-live-replay.py:279`), matching the receipt-side rule that `witness` appears only when
witnessing (`tools/kama-llamacpp-live.py:1860-1866`). Consumers must use `.get`; the C1 counter
(`:324-326`) and `check-receipt.py` do.

**Not in scope here (other seats):** C2's `append-only-audit.py` v4 definition compatibility
(v3 schema string retained — `X1Concurrent`), and the C1 counter's own execution (`X1Witness`/`X1Kill`).

## 7. Artifacts (this directory)

`r47-c2-counter.json`, `r48-v5-counter.json`, `replay-v4-nowitness.json`, `replay-v4-witness.json`,
`replay-v4-witness-unreleased.json`, `replay-v4-witness-staledir.json`, `replay-v5-witness.json`,
`observer-v4.json`, `observer-v5.json`, `rerun-v4-witnessed-receipt.json`,
`rerun-v5-witnessed-receipt.json`, `gguf-identity-v4-witness.json`, `gguf-identity-v5-witness.json`,
`neg-replay.log`, `neg-live.log`, `neg-live2.log`, `commands.log` (exact commands + exit codes).
Scratch `/fast/scratch/hyaku/kama-r49/X1Compat` removed after these copies.
