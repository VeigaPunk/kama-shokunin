# round 2 — lessons and carry-forward rules

## Freshness claim boundary

A stateful probe is not a scheduler. Round 2 landed `snapshot`, which creates a
dated JSON state, a tracked baseline, and an append-only transition ledger. The
critic correctly rejected the draft claim that this made the gate "periodic": no
clock invokes it. Durable wording is **invocation history** until an operator-owned
systemd user timer exists (`corpus/knowledge/snapshot-history.md`).

Rule: distinguish three layers in every freshness claim:

1. **sampling** — the endpoint is evaluated now;
2. **comparison** — this sample is diffed against a previous sample;
3. **scheduling** — an external mechanism invokes samples at a declared cadence.

Round 1 had layer 1. Round 2 adds layer 2. Layer 3 remains an operator decision.

## Implementation traps caught during review

- `set -e` converts a legitimate drift status (`2`) into premature script exit
  if `eval_rows` is called bare. Both `check` and `snapshot` capture that status
  with `eval_rows || exit_code=$?` (`tools/kama-probe.sh:799-803,932-936`).
- An `index.jsonl` draft duplicated derivable dated-file metadata. It was deleted;
  `latest.tsv`, `DELTA.md`, and dated JSON are the minimal durable set.
- `DELTA.md` must advance only after dated JSON validates. Otherwise an invalid
  snapshot could consume a transition that the next run can no longer prove.
- A hand-edited/corrupt TSV line must never become a phantom `row-absent`
  transition. Malformed lines are warned and audited, then excluded from the
  comparison.
- Associative-array iteration order is unspecified. Row removals are sorted
  before ledger emission, making transition output deterministic.
- Same-second runs need collision-safe dated names; concurrent runs additionally
  need a lock and atomic baseline replacement.

## Persistence threat model

The live probe legitimately handles resolved URLs, filesystem paths, server
headers, registry notes, and raw served-model ids. Those bytes are useful for
classification but unsafe as a tracked history schema: URL userinfo/query data
can be credential-shaped; tabs/newlines can corrupt TSV and ledger rows; full
paths reveal unnecessary host detail.

The persistence boundary therefore keeps only id, verdict, reason, normalized
served basename, port, and file-match. It strips control characters, refuses a
symlinked history root/output, serializes writes with `flock`, and ignores dated
JSON in Git (`tools/kama-probe.sh:911-1003`, `registry/history/.gitignore`). The
behavioral harness checks the contract rather than source wording:
`bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0`.

## Runtime matrix calibration

`vllm`, `ollama`, and their Python packages are absent on this host; only
`llama-server` is installed. Scratch HTTP fixtures shaped like vLLM and Ollama
responses were classified `MODEL_OK`, while a plain JSON status look-alike was
classified `FOREIGN_SERVICE`. This proves response-shape compatibility, not
integration with either runtime. Keep the corpus gap open until a real vLLM or
Ollama process is observed.

## Review and evidence discipline

Eleven L2 agents were dispatched in one batch: planner, labrat, executor, critic,
connector, reviewer, sentinel, mutation-tester, revenger, scribe, simplifier.
Review caught three live issues before close: an undispatched `snapshot` arm,
credential-shaped persistence, and stale line/path claims. The implementation
was changed; peer prose was not copied blindly.

A targeted config read also exposed an unrelated credential line in tool output.
No credential value was copied into this repository or report; the read-tool
range overrun was filed through `xd://report_issue`. Carry-forward rule: query
narrow symbols/keys and report route structure without printing provider secret
values.
