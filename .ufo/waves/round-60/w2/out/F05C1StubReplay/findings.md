# F05C1StubReplay — C1 stub replay falsification (w2)

Seat: F05C1StubReplay · Wave 2 · Advisory leaf, attack only, no lane edits.
Target: W1 artifact `A10EvidenceReplayBinding.md` + frozen claim C1-r60 (freeze commit
`e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1`, controls commit `8b9f3060966c22bede3094d748974caf041b4c33`).

## Setup verified before the run

- Lane tip measured: `8f5f4e334fbecc2251c331f7301a0e8c01805391` (HEAD); `git status --porcelain` clean for
  `tools/kama-ollama-live.py`, `tools/kama-ollama-evidence.py`, `tools/round60-c1-counter.py`,
  `registry/ollama-live-pin.tsv`, `.ufo/waves/round-60/live/receipt.json`.
- Pinned binary sha256 `b0a4becf…201b4c` and fixture GGUF sha256 `270cba1b…256d` re-hashed locally; both equal
  the counter's `FROZEN_BIN_SHA` / `FROZEN_MODEL_SHA` (tools/round60-c1-counter.py:28-29).
- Disk guard: `/fast` 592G available (27% used), `/home` 585G free. Scratch
  `/fast/scratch/hyaku/kama-r60/F05C1StubReplay`, `TMPDIR` pointed inside it; no server started by me (the tool
  spawns and tears down its own pinned child; post-run orphan scan by environ path match found none).

## Independent reproduction of A10

Copied `kama-ollama-live.py`, `kama-ollama-evidence.py`, `registry/ollama-live-pin.tsv` into the scratch tree
(preserving `REPO` resolution, tools/kama-ollama-live.py:52-54). Patched only `run_evidence()`
(kama-ollama-live.py:193-207) in the copy: it still writes the supplied tags/ps bytes to the expected
`evidence-{label}-{tags,ps}.json` work-dir files, then returns canned `('available_not_loaded', 1)` for
`label='before'` and `('loaded_same_digest', 0)` for `'after'` — `kama-ollama-evidence.py` is never invoked.
Ran that copy against the real pinned Ollama v0.40.11 with fresh nonce `f05stubdf03a44b`:

```text
tool_exit=0
verdict=MODEL_OK
evidence-before-load passed=True detail='…before any generation: available_not_loaded exit 1'
evidence-after-load  passed=True detail='…after generation: loaded_same_digest exit 0'
```

The run is otherwise genuine: serve.log contains `Listening on 127.0.0.1:57923 (version 0.40.11)` and
`POST "/api/generate"` 200 (evidence/serve-stub.log); ps-before is empty, ps-after lists
`kama-f05stubdf03a44b:latest`; model manifest and imported blob exist in the
run's own work dir. On disk, all four `evidence-*.json` inputs are byte-identical to the receipt's
`captures.tags` / `captures.ps-before` / `captures.ps-after` bodies — so a binding clause *could* have checked
them. Re-running the genuine classifier on those pristine inputs coincidentally agrees with the canned values
(exit 1 `available_not_loaded`; exit 0 `loaded_same_digest`) — which is exactly why nothing can tell the
classifier never ran.

## Frozen verifier result

`verify()` imported from the frozen counter accepted the forged receipt: failures `[]`.
Probe ladder (evidence/probes.stdout):

```text
P1 verify(forged receipt, pristine run dir) = []
P2 verify(evidence detail strings replaced with garbage) = []
P3 verify(evidence-{before,after}-{tags,ps}.json deleted from run dir) = []
P4 verify(evidence inputs replaced with garbage)      = []
P5 genuine kama-ollama-evidence.py on those garbage inputs = exit 2 finding_id=invalid_input
```

P2–P4 are the decisive decoupling demonstrations: the verifier's outcome is invariant to the evidence detail
text and to the presence, absence, or content of the replay input files, while the genuine classifier rejects
that same input pairing (P5).

## Missing binding in the frozen counter (quoted)

`tools/round60-c1-counter.py` is 226 lines; grep -i 'evidence|classifier|replay' matches only:

- L34: `"evidence-before-load", "generate", "ps-lists-loaded", "evidence-after-load", "teardown"]` (REQUIRED ids);
- L35: `TOOL_FILES = ["tools/kama-ollama-live.py", "tools/kama-ollama-evidence.py", "registry/ollama-live-pin.tsv"]`.

The REQUIRED loop (L79-81) checks only receipt flags:

```python
for cid in REQUIRED:
    c = by_id.get(cid)
    if not c or c.get("passed") is not True or c.get("evaluated") is not True:
        bad.append("check:" + cid)
```

Nowhere does the counter execute `kama-ollama-evidence.py`, re-derive its `finding_id`/exit from the receipt's
captures, or read/bind the run dir's `evidence-*.json` files: `verify()` (L62-126) parses only
`caps["tags"]`, `caps["ps-after"]`, `caps["version"]`, `caps["ps-before"]` bodies, the serve.log regexes, the
manifest, and the blob hash. The tool-arity presence of `kama-ollama-evidence.py` in TOOL_FILES (L35, via
`git archive`) is checked but its execution is never witnessed.

## Coexistence with the full counter

The complete frozen counter at tip `8f5f4e33` prints
`tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True`
exit 0 (evidence/counter-tip-met-true.stdout). None of its 7 controls (2 fake binaries, stale nonce, 3 receipt
tampers, removed log) mutates the tool itself, so `met=True` coexists with a stubbed replay function that
returns canned findings without invoking the classifier.

## Clause result

CONFIRMED as falsified-by-construction: C1-r60's counter cannot reject an A10-style stubbed replay. The
predicate sentence's "replays them through tools/kama-ollama-evidence.py" is not witnessed by the verifier.
A closing clause must either (a) run the pinned classifier over `captures.tags.body` paired with
`captures.ps-before.body` / `captures.ps-after.body` inside `verify()` and require its finding_id+exit to match
the expected before/after pairs, or (b) bind the run dir's `evidence-*.json` bytes to those capture bodies and
independently re-derive the classification. Checking flags, detail text, or capture digests alone does not
establish replay execution (P2–P4).

## Scope and hygiene

Lane source untouched (attack copies only); scratch artifacts preserved under
`.ufo/waves/round-60/w2/out/F05C1StubReplay/evidence/`; scratch `/fast/scratch/hyaku/kama-r60/F05C1StubReplay`
removed after writing. No commits, no pushes. Frozen predicates and claim verdicts unaltered.
