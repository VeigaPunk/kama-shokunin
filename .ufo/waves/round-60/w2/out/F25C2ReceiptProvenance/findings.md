# F25C2ReceiptProvenance — C2 receipt provenance falsification (round-60 w2)

## Claim attacked (frozen, unchanged)

C2-r60 clause: "the committed receipt's capture hashes are intact" (verbatim in
`tools/round60-c2-counter.py` docstring and `.ufo/waves/round-60/controls/freeze.txt`).
Assignment question: can arbitrary receipt capture bodies with recomputed sha256 satisfy C2?
Can a synthetic receipt, never emitted by `tools/kama-ollama-live.py`, be accepted?

## Attack thesis

`receipt_caps()` (tools/round60-c2-counter.py:159-173) is the counter's ONLY receipt
consumer. It checks exactly two things: `rec.get("schema") == "kama-ollama-live/v1"` and
per capture `sha256(cap["body"]) == cap["sha256"]`. Both are internal-consistency checks an
attacker satisfies by construction: author any body, recompute the hash. Grep of the counter
source shows it NEVER reads `nonce`, `binary_sha256`, `pin`, `checks`, `port`, `argv_child`,
`elapsed_s`, or the receipt's own `verdict` (the only `verdict` tokens are registry-row
columns). No signature, HMAC, nonce echo, digest pin check, or tool-identity binding exists.
Predicates evaluate over `c` = the parsed capture bodies, so attacker-chosen bodies directly
drive every `confirmed`/`contradicted` decision.

## Method (scratch fixture only; lane read-only)

Fixture: `git clone` of the lane into scratch (top-level asserted), carrying the REAL
committed receipt (`.ufo/waves/round-60/live/receipt.json`, committed at 8b9f3060). To isolate
ONE variable (the receipt) I first built, in the fixture only, a minimal registry +
amendment that makes C2 green against the REAL receipt — the freeze's sanctioned
"counter can pass" fixture pattern. Frozen base population reproduced exactly 14 lines.
Registry: 14 rows (one per base line), 5 evaluated predicates over ≥4 lines (tags surface,
empty inventory, tags→ps digest join, expires_at presence, size_vram), 1 contradicted row
(`bool(c['ps-after']['models'][0]['size_vram'])`, observed `size_vram=0 (ps-after empty-VRAM
residency)`), 9 not-observable rows. All five control families rejected: 35/35.

- Phase 1 (baseline, REAL receipt): `python3 tools/round60-c2-counter.py --repo <fixture>
  --tip 91b54dfb...` → exit 0, `population=14 rows=14 covered=14/14 evaluated=5 eval_lines=5
  sensitive=5/5 bound=5 contradicted=1 amended=1/1 receipt_ok=1 controls_rejected=35/35
  errors=0 met=True`.
- Phase 2 (fully synthetic receipt): nonce `f00dface0001` (fresh), `binary_sha256` 64×"0"
  (impossible; real pin is b0a4becf...), `argv_child` ["/usr/bin/true"], port 1, server
  version `0.0.0-never-shipped`, `checks: []`, all 11 capture bodies hand-authored
  (model `kama-f00dface0001:latest`, digest f×64). Per-capture sha256 recomputed. Committed
  as fixture tip 73a955ac... → exit 0, stdout BYTE-IDENTICAL to phase 1 (`diff` empty):
  `met=True`, `receipt_ok=1`, `controls_rejected=35/35`.
  Receipt blob sha256: real `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6`
  → forged `76a75436875c3df10560a50e4a731c2153523560508443c2259f15ab8d29e935`. Verdict unchanged.
- Phase 3 (attacker bodies inside the REAL receipt): starting from the committed receipt
  blob, overwrote `captures.root.body` with arbitrary text and `captures.show.body` with a
  fabricated runner, recomputing only those two sha256 fields → exit 0, `met=True`,
  `receipt_ok=1`. The counter's own tamper control (family 5) appends a space WITHOUT
  rehashing — it detects only tampering that forgets to recompute, which a real attacker
  never does.

No Ollama server was started (not needed; the attack is offline forgery). No installs.

## Result

MUTANT KILLED — the provenance clause is falsified. C2 cannot distinguish a receipt emitted
by `tools/kama-ollama-live.py` from a fabricated one; "its recorded verdict equals its
evaluation on the committed receipt's captures" evaluates over attacker-chosen bodies, so a
C2 met=True is compatible with no server ever having run. This is a coverage finding on the
instrument, per bounds: predicates, registry, receipt, and counters untouched.

## Lane-state observations (context, not repaired)

- `registry/ollama-live-claims-r60.tsv` and `corpus/knowledge/ollama-live-amendment-r60.md`
  exist in NO commit (`git log --all` over the path is empty) and not in the working tree, so
  at lane HEAD 8f5f4e33 the counter is red (`reg=None` → rows=0) regardless of receipt
  provenance; `.ufo/waves/round-60/controls/c2-freeze-tip.out` (rows=0 receipt_ok=0 met=False)
  is consistent with that pre-data state. The provenance hole lands the moment the registry
  is committed.
- W1 record (`.ufo/waves/round-60/w1/w1-results.json`, seat F14C1CaptureTamper entry)
  had already suspected "C2 validates capture hashes but not provenance"; this seat turns
  that advisory into a demonstrated false green. [INFERENCE] closing C2 on the current
  counter would certify lane statements about a server that need not exist.

## Restoration evidence

Scratch `/fast/scratch/hyaku/kama-r60/F25C2ReceiptProvenance` removed (verified absent).
Lane pre/post identical: `git status --porcelain` shows only 14 pre-existing sibling/orchestrator
wave entries (none mine); `receipt.json` sha256 `49d06600...90c2a6` and counter sha256
`d2e9a722...6a8fe5` unchanged; HEAD `8f5f4e334fbecc2251c331f7301a0e8c01805391` unchanged.
TMPDIR was scratch-local and removed with the tree. No git/jj mutation in the lane; no commits.
