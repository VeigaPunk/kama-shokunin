# F07C1CounterReDerivation — C1 counter re-derivation (round 60, wave 2)

Axis: operability (C1). Attack only; no lane file altered (sha256 of `tools/kama-ollama-live.py`,
`tools/kama-ollama-evidence.py`, `tools/round60-c1-counter.py`, `registry/ollama-live-pin.tsv`
identical before/after all probes — `summary.json:lane_unchanged=true`).

## 1. Frozen claim re-derived at the current tip — NOT already false

- Tip measured: `8f5f4e334fbecc2251c331f7301a0e8c01805391` (lane HEAD; base per freeze `ec3b0d58…`;
  all three TOOL_FILES + pin present at tip via `git ls-tree`).
- Command: `TMPDIR=<scratch>/evidence/tmp python3 tools/round60-c1-counter.py --repo …/kama-shokunin
  --tip 8f5f4e334fbecc2251c331f7301a0e8c01805391 --work <scratch>/counter-work` → exit 0.
- Output (exact): `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3
  log_rejected=1/1 errors=0 met=True predicate='C1-r60 …'` (`counter-tip.out`). Fresh nonce, fresh
  live run, 7/7 controls rejected. **C1-r60 stands at the tip; the claim is not already false.**
- Independent corroboration: my own fresh-nonce baseline run (nonce `f07ac59acfa`, unmodified tip
  tree, pinned binary b0a4becf…, fixture GGUF) produced a MODEL_OK receipt that the *unmodified*
  frozen verifier accepts: `verify_bad=[]` (`receipt_B.json`, run dir work artifacts in scratch).

## 2. The minimal falsifiable control: causal classifier-invocation differential

Question: did `tools/kama-ollama-evidence.py` (the evidence classifier) actually run inside the C1
live pipeline, or are the `evidence-before-load`/`evidence-after-load` check flags decorative (the
A10/W1 stub direction)? Frozen test untouched; the probe replaces a *tool* file only inside my
scratch copy of the tip tree.

- Baseline B: `git archive 8f5f4e33…` → treeB (byte-identical tool set); live run, fresh nonce
  `f07ac59acfa` → exit 0, verdict MODEL_OK, evidence details `available_not_loaded exit 1` (before)
  and `loaded_same_digest exit 0` (after), both passed; frozen verifier accepts.
- Treatment T: identical treeT except `tools/kama-ollama-evidence.py` replaced by a 4-line stub
  printing `{"finding_id":"f07_stub_marker","verdict_exit":4,…}` and exiting 4
  (`stub-classifier.py`); live run, fresh nonce `f075c57a314` → exit 1, verdict FAIL;
  evidence details record `f07_stub_marker exit 4` in both checks.
- Result: the receipts differ *exactly* in the two evidence checks plus verdict; frozen verifier
  rejects T with precisely `["verdict","check:evidence-before-load","check:evidence-after-load"]`.
- Proof of execution: the marker `f07_stub_marker exit 4` can only enter the receipt through
  `run_evidence()`'s subprocess call — the child's stdout/returncode flowed into the check detail
  and gated the verdict. Falsifiability: if the unmodified tool did not invoke the classifier,
  T would equal B; it does not. The pair isolates one file, so the delta is the classifier itself.
- Content dependence (offline, on B's own captures, original classifier): tags+ps-before →
  `available_not_loaded`/1; tags+ps-after → `loaded_same_digest`/0; one hex char flipped in the
  ps-after digest → `identity_conflict`/1; ps-after models emptied → `available_not_loaded`/1.
  Classifier output is a strict function of capture bytes, so what the pipeline executed is not a
  constant.

## 3. Committed receipt (live/receipt.json, W1) status

Unmodified frozen `verify()` over the committed receipt with its committed directory rejects only on
the four clauses that need ephemeral work-dir artifacts never committed: `["log-listening",
"log-generate","manifest","blob-missing"]`. Every clause evaluable from committed bytes passes:
schema, nonce `b61c98ad5747`, verdict MODEL_OK, binary sha b0a4becf…, port 58921 unregistered, all
16 checks passed/evaluated, **all capture sha256 intact**, tags/ps/version parses, teardown. This is
expected (C1's verification is a fresh run, not the commit) and corroborates C2's "capture hashes
intact" clause.

## 4. Residual risks / gaps (attack perspective)

- Open (A10/W1, still true at this tip): the frozen verifier binds the evidence checks only as
  booleans; a stubbed classifier producing the expected finding/exit pair would be accepted
  downstream. My control proves execution happened in the re-derivation run; it does not repair
  that binding. A closing clause would have the counter re-run the classifier over
  `captures.tags.body` × `captures.ps-before/ps-after.body` and require finding+exit equality.
- The counter takes `--tip` only for archiving tool files; binary/model digests come from constants
  frozen in the counter and `REAL_BIN`/fixture from the host — verified consistent with the freeze
  (b0a4becf…, 270cba1b…).
- `corpus/SOURCES.md` is dirty in the lane worktree (mtime 18:56, before my first write at 19:02) —
  a concurrent seat's edit, not mine; recorded, not touched.

## 5. Bounds

Lane READ-ONLY (read/git archive only; 4-file sha256 stable). Scratch
`/fast/scratch/hyaku/kama-r60/F07C1CounterReDerivation` with explicit `TMPDIR`, removed at exit;
receipts/logs/stub copied to this out dir first. Servers were started only by the lane tool itself
(fresh nonce, free unregistered port, tool-internal killpg + teardown proof in each receipt);
residue scan of `/proc/*/environ` post-run: none. Disk guard pre-run: `/fast/scratch/hyaku` 592.8G
free (exit 0). No tool installs (stdlib python3/git/tar sufficed). No commits/push/jj.
