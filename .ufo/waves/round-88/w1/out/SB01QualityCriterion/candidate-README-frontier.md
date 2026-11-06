## Frontier — round 88 disposition (appended)

Appended after the round-85 disposition; no earlier bytes move. Round 88 moves
llama.cpp **router-mode readiness** from frontier to held: `tools/kama-probe.sh`
grades a matching `GET /v1/models` entry by that entry's own `status.value`
(S581, b11755) and the frozen counter `tools/round88-router-cells.py` printed
`ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=rev`, exit 0, at
`138a75437bcd11b72446087e970f5dfc5abf9ccd`
(`.ufo/waves/round-88/measured/c1.out`); the same counter at base printed
`mismatches=11` (`.ufo/waves/round-88/controls/c1-base.out`). The new knowledge
entry is `knowledge/router-mode-readiness.md`. That closes only the single-host
llama.cpp case; the following remain frontier.

- **Other engines' multi-model readiness.** The lane's vLLM and SGLang holds are
  documentary `/health` and capacity statements (S480, S481, S483, S567, S568,
  S574; S478, S569, S570, S575), and no lane-owned vLLM or SGLang child appears
  in the registry or this round's receipts (the line-60 gap names vLLM and
  Ollama; the SGLang hold is documentary, S574). No registry row states a
  per-entry readiness object for their model listings, so whether vLLM multi-LoRA
  or SGLang multi-model mode reports load state in a listing is unread; the
  round-88 verdict rule does not transfer without such a source, and no fixture
  is called runtime integration.
- **Per-request `?autoload`.** S581 line 1993 documents `?autoload=true|false`,
  but the probe sends no completions by design, so it cannot grade "loadable at a
  load cost" against "ready", and the first-request latency under autoload on and
  off is unmeasured.
- **`sleeping` and cold-start cost.** `sleeping` is graded not-ready by choice
  (README places it beside `unloaded`); the wake latency and whether a sleeping
  model refuses or serves on the first request are unobserved. `downloading`,
  `incomplete` and `failed: true` are exercised only by canned cells C04/C06/C07,
  not by a live router state.
- **Operator router 127.0.0.1:1234.** Only GETs were sent (a completion would load
  a model on the operator's GPU). The only 1234 receipt is the pre-fix pilot
  (`MODEL_OK` against four `unloaded` entries,
  `.ufo/waves/round-88/controls/pilot-live-1234.out`); the post-fix verdict there
  is a derivation from the same GET body, not a receipt, and an authorized window
  with the completion oracle is outstanding.
- **Load/unload as an action.** `POST /models/load` and `POST /models/unload` are
  documented (S581 lines 2137, 2159) and were used on the lane's own child, but a
  probe that mutates router state stays a separate move: the probe's read-only
  promise and the operator's GPU are not crossed by a readiness check.
- **Residency routes other than a listing status.** Ollama reports loaded
  residency on `/api/ps` (round-11/14 entries), not as a listing-entry object;
  the round-88 rule grades only llama.cpp's `status`, so an engine that answers
  residency elsewhere is ungraded by `MODEL_UNLOADED`.
- **Verdict-set consumers outside this lane.** The probe gained a vocabulary
  member (`MODEL_UNLOADED`, drift, `check`/`snapshot` exit 2); the lane updated
  its own baseline parser and `tools/round79-unregistered-census.py`, but no
  census enumerates external parsers that hardcoded the pre-r88 set.
- Retained from earlier rounds: K05 declared-versus-served context capacity,
  registered-consumer reconciliation (rows remain `DEAD`), and round 85's
  rendered-cell identity, coupled measurement provenance, ownership-aware mutant
  transcript grading and independently corroborated source origin.
- Index note: if the round-88 knowledge entry lands without a coverage-map row,
  that is an index gap, not absence of the entry (round-76 D1 precedent).
