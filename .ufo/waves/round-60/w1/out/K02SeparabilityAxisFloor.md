# K02SeparabilityAxisFloor — claim-structure falsification

## Counterexample and evidence

C1 and C2 are mechanically separable but share provenance: C2 reads the committed receipt and its own registry/amendment, not the C1 tool or counter (`tools/round60-c2-counter.py:285-305`); C1 archives only its declared tool files and does not read the C2 registry (`tools/round60-c1-counter.py:35,161-170`). Thus each counter can be invoked independently at a tip if its required artifacts exist. But C2's oracle is explicitly the receipt produced by C1's live lifecycle (`freeze.txt:34-35`), a data dependency not expressly acknowledged as a causal dependency in the freeze. `AXES.md:27-33` requires every claim be verifiable without the others having landed. Clarify whether frozen, shared evidence counts as allowed dependency; do not call C2 independent confirmation of C1 evidence.

C2 does not authenticate the receipt: `receipt_caps()` checks only schema and self-consistent hashes (`round60-c2-counter.py:163-177`). A fabricated capture set with valid hashes is acceptable to this layer. `falsifiable()` only requires that mutation of a referenced capture changes the predicate (`:141-160`); it cannot establish that the predicate semantics match its quoted sentence. Controls cover tautology, flips, corrupted quotes, dropped lines, and capture-hash tamper (`:243-282`), not fabricated-but-consistent capture data or quote/predicate semantic mismatch.

C1's independent verifier is materially stronger: it checks nonce, digest, captures, required checks, serve log, manifest and model blob (`round60-c1-counter.py:62-132`). But these are not cryptographic proof that a live server produced the ordinary files; the receipt's check fields are asserted by the tool, and no outside witness observes the server. This is an attack surface, not an observed passing exploit. Frozen C1 controls test fake binary inputs, stale nonce, receipt tampers and missing log; they do not test a replacement driver or handcrafted matching artifacts. Prior precedent: fleet `.ufo/l0-questions.md:193` records a do-nothing wrapper forging a fresh-nonce receipt without launching the runtime.

The committed receipt reports `teardown.log_path=/fast/scratch/hyaku/kama-r60/live1/serve.log`; that directory is gone (`ls` returned “No such file or directory”). C1 verifier expects run-dir log/model artifacts; C2 only validates captures. Hence the committed receipt is not independently re-verifiable by C1 from its recorded path. This is a durability limitation, not proof that the fresh C1 counter run failed.

## Axes and lowest-axis floor

Exact fleet definitions: `AXES.md:13` operability is “Runnable artifacts: checklists that are executable, commands that exist, scripts that run”; `:15` calibration is “Self-assessment quality: gaps named honestly, confidence graded, overreach caught.” A live lifecycle capability plausibly belongs to operability as a capability acquisition, but does not improve the registered endpoint probe. C2's mapping and correction of inference claims plausibly exercises calibration, and calibration 7 is the lowest assigned axis (`freeze.txt:28`). Its counter, however, proves coverage and mutation-sensitivity, not semantic calibration; claim no calibration improvement absent adequate independent judgment. Freeze admits no score increase (`:48-50`).

## Do-nothing reachability

The explicitly frozen controls fail to reach target: `controls/c1-base.out`: `tool_present=0 ... met=False`, exit 1; `controls/c2-base.out`: `rows=0 covered=0/14 ... met=False`, exit 1. No observed result says otherwise.

Stronger controls remain uncovered: C1 replacement-driver/fabricated-artifact control; C2 fabricated-but-self-consistent capture control. Do not state these have passed. Small correction: add them, bind C2 to retained independently verifiable C1 run identity, or explicitly limit C2 to grading the immutable committed capture corpus without independent provenance claims. Also add outside quote/predicate semantic review or control; sensitivity alone is insufficient.

## Existing statements and admission-floor risks

* `SCORECARD.md:14` says registered endpoints are DEAD and no model-readiness verdict is evidenced. `:32-35` says the gate is verified against real llama.cpp only and vLLM/Ollama are fixture-shaped parser tests. This round does not change registered consumer rows or `kama-probe.sh`, so those scoped statements remain true. Broad implication that kama has no live Ollama integration is now stale; qualify it as applying to the probe/offline replay.
* `SCORECARD.md:122` says offline replay readiness is always unknown; `SKILL.md:455-463` says inputs need not be from Ollama and readiness remains unknown. Those statements remain true about the offline replay tool, even though C1 feeds real captures through it. Distinguish offline replay from lifecycle.
* `SCORECARD.md:119-133` says capabilities enter only through a round demonstrating them. C1 demonstrates a distinct candidate capability; this advisory review makes no admission decision.
* `PROVINCE.md:47-51` hard boundary: “kama never writes to `~/.config`, `~/.omp`, or systemd units.” Tool docstring says isolated HOME/models/log (`kama-ollama-live.py:14-15`); child env sets HOME and OLLAMA_MODELS within work dir, cloud off (`:180-187`). No boundary violation evidenced; preserve it.
* **L0 required:** `PROVINCE.md:57-71` says the lane-owned llama.cpp fixture's narrowing of the rule is pending L0 ratification, applies only to its own child, and leaves other unregistered endpoints requiring L0. The existing question `.ufo/l0-questions.md:58` asks ratify/reject and disposition of install/link/cache; no answer found. Ollama is a second engine and its docstring itself says its exception is pending ratification (`kama-ollama-live.py:14-20`). L0 must explicitly address Ollama's unregistered child and persistent install/cache; do not treat the llama.cpp question as covering it.
* `SCORECARD.md:6` and `.ufo/l0-questions.md:145` document unresolved axis authority: `MISSION.md:29` says operability+freshness while config/prompt say operability+calibration. Freeze follows established current authority and works calibration 7; this review does not resolve it. Existing L0 question is the correct route.
* Round-16 precedent is a policy exception specific to llama.cpp, not general permission for all unregistered engines (`PROVINCE.md:63-68`).

## Exact observed commands/results

* `python3 tools/round60-c1-counter.py --repo <repo> --tip <freeze-tip>` → `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True`, exit 0 (`controls/c1-freeze-tip.out`). Base: tool absent, `met=False`, exit 1.
* `python3 tools/round60-c2-counter.py --repo <repo> --tip <freeze-tip>` → `population=14 rows=0 covered=0/14 ... receipt_ok=0 controls_rejected=0/0 errors=0 met=False`, exit 1 (`controls/c2-freeze-tip.out`). Base also `covered=0/14 ... met=False`, exit 1. No C2 registry has landed at this measured tip.
* `ls /fast/scratch/hyaku/kama-r60/live1` → `No such file or directory`; receipt teardown path points there.
* `/home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status` → root free not reported; `/tmp 5%, 122.5G free; /var/tmp 35%, 584.6G free; /fast/scratch/hyaku 27%, 591.2G free`. No ENOSPC observed.

## Smallest safe correction

No lane edits from this seat. At closure: identify the explicit C1-receipt-C2 dependency; add the two do-nothing/fabrication controls or narrow provenance claims; qualify historical SCORECARD/SKILL Ollama parser language to the offline replay/probe gate; and file a separate L0 question for the Ollama unregistered child and persistent artifacts. No verdict or score change is offered.