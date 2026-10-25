# ReviewC2Ground — admission-503 was not already held

Verdict: at base `719655f12517a9ce6b1a5ca44316897fed8420b0` the lane did not hold the vLLM admission-503 distinction. The C2 entry is new coverage-map ground for that distinction. Do not reject it as a restatement of llama.cpp loading-503 or of S004. This seat did not create the entry.

Search method: ripgrep over `corpus/`, a Python byte count, then `git grep` at the base and at `d419b99df20d1f0b34caf65807e913784e69baf5`. Literal search is not semantic proof. The "holds" judgment is from reading the knowledge files next to those hits.

HEAD moved during this review, from `719655f` to `d419b99` (`round-35: calibration corrections, probe-convention entry, frozen counters`, 2026-10-24 21:28:08 -0300). Counts below are re-derived after that commit. This seat did not commit.

## Findings

### None — the kill condition does not fire

The assigned rule was: if the lane already holds the vLLM admission-503 distinction, the C2 entry would not be new ground. "Already" means before the entry. That antecedent is false at the base.

Held at `719655f`, and a different 503:

- `corpus/knowledge/runtime-health-surface-matrix.md:15` and S004: vLLM `GET /health` returns 503 only on `EngineDeadError`. Engine-dead, not an admission valve. No `engine_args` row. No S327.
- `corpus/knowledge/llamacpp-loading-lifecycle.md` and KQ19: the llama.cpp loading envelope (`Loading model` / `unavailable_error` / integer code 503) is `MODEL_LOADING`. Different engine, different condition. Round 16 already refused to resell the `/health` 503 body as new (`corpus/README.md:209-211` at the base).

Named at the base, and explicitly not held:

- `corpus/knowledge/served-model-id-resolution.md:37-46`, heading "A related gap this round could not close." It says a "wave-1 vLLM engine-arguments row" records that `/v1/chat/completions` returns 503 as a deliberate admission rejection, then says no new row was opened and points at `CANNOT-ANSWER.md`. That file is not in the lane. The paragraph's own "holds" sentence is only for the S004 handler. An unopened gap note is not admitted knowledge.

The three assigned phrases are absent from the base corpus (`git grep` at `719655f` prints nothing). They are not prior ground.

After `d419b99` the lane holds the distinction because the entry was admitted, not because it was already there. That commit is the new ground. It is not evidence the entry was duplicate.

### None — landed counter meets; the earlier unmet reading is withdrawn

Re-run after the commit:

```
python3 tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
named 0 file_exists 0 cited_row 0 met False
exit 1

python3 tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip d419b99df20d1f0b34caf65807e913784e69baf5
named 1 file_exists 1 cited_row 1 met True
exit 0
```

Working tree matches that tip for the entry, `corpus/README.md`, and `corpus/SOURCES.md` (porcelain empty on those paths). An earlier pass in this same review saw the file untracked and the counter at `named 0 file_exists 1 cited_row 0`. That reading is stale. Do not use it.

The landed saturation sentence matches the live page, opened 2026-10-24: https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/ §EngineArgs → SchedulerConfig → `--max-num-queued-reqs`. The page says "When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance." The same heading's `--max-num-queued-tokens` says "When the limit is reached, new requests are rejected with HTTP 503." That matches `endpoint-health-probe-conventions.md:10-14` and the S327 anchor. It is not a local runtime observation, and the entry does not claim one.

### Low — do not sell the bare idea as never named

`served-model-id-resolution.md:41` already uses the words "deliberate admission rejection," as an unclosed gap. A sentence that says the lane had never named a deliberate-rejection 503 would overclaim. The new ground is the sourced `engine_args` statement, distinct from S004 and from llama.cpp loading-503. `service_healthy` and `probe_success` are still not held conventions: their only tip hit is the entry's refusal ("were not re-opened into this file").

## Hits

| Phrase | Base `719655f` | Tip `d419b99` |
|---|---|---|
| `rejected with HTTP 503` | 0 | 3 — `corpus/SOURCES.md:213` (S327 anchor), `corpus/knowledge/endpoint-health-probe-conventions.md:11`, `corpus/lessons/round-35.md:28` |
| `service_healthy` | 0 | 1 — `corpus/knowledge/endpoint-health-probe-conventions.md:22`, exclusion only |
| `probe_success` | 0 | 1 — same line, exclusion only |

Near miss, not one of the three phrases: the entry's line 12 has `rejects with HTTP 503`. `deliberate admission` also occurs in the pre-existing gap at `served-model-id-resolution.md:41`.

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -F \
  -e 'rejected with HTTP 503' -e 'service_healthy' -e 'probe_success' \
  719655f12517a9ce6b1a5ca44316897fed8420b0 -- corpus
# no output; printed BASE_HITS_NONE
```

## Residual risk

- A reader can still treat `served-model-id-resolution.md:37-46` as if it had admitted the distinction. It did not. The sourced statement starts at S327 / the new entry.
- `service_healthy` and `probe_success` remain exclusions. Admitting Docker HEALTHCHECK or blackbox `probe_success` would be further ground; this entry does not take it.
- The gap paragraph still points at a missing `CANNOT-ANSWER.md`. The new entry does not edit that paragraph.

## Verification gaps

- Live-page check covered the two HTTP 503 sentences under SchedulerConfig only. It did not re-audit the rest of the engine_args page or staged rows other than the landed S327 quote.
- No corpus mutation by this seat. The entry, the coverage block, and S327 were already committed at `d419b99` when this report was corrected.
