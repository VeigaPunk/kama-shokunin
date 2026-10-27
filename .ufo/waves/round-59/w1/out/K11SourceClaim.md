# K11SourceClaim — round-59 source-claim falsification

**Axes:** operability, calibration (lowest assigned). **Attacked claim/clause:** the proposed single claim that cites S517 as opened this round and says its quote supports only profile call/return semantics, not line execution/result use. This is source/provenance and scope falsification, not a verdict on the frozen C1/C2 counters.

## Finding

The round context explicitly says the external S517/S518 spot-check is **not yet recorded** and forbids claiming discernment progress. Therefore a claim asserting S517 was opened this round is unsupported by the available recorded evidence and must not be presented as an observed event. Further, call/return semantics alone do not establish execution of a particular line, nor consumption/validation of a returned result. The strongest local counterexample is round-58 `R02ProfileHookSemantics`: its reported X01-ghost-thread fixture records subprocess argv while watched main-thread frames are on the stack, even though those watched `run`/assert bodies issue no subprocess; a background thread issues them. Its X02 fixture also demonstrates genuinely issuing from worker-thread frames can be invisible to the thread-local profile hook. Thus observed profile events / call-return boundaries are not proof of line execution provenance or result use.

Evidence: `.ufo/waves/round-58/w1/out/R02ProfileHookSemantics.md`, especially lines 12–23 (ghost-thread accepted no-op), 28–40 (time-slice attribution and threaded false negative). This is a prior seat report, not a fresh reproduction in this assignment.

## Verdict and correction

- S517-opened-this-round clause: **unsubstantiated / do not claim**; the round input explicitly says the spot-check is not recorded. No S517 artifact was found in the round-59 wave directory listing (only w1 setup, controls, and census artifacts were listed).
- Quote-scope clause: **needs narrow wording**. A quote showing profile call/return semantics may support only that narrow instrumentation behavior; it cannot support line-level execution or returned-result-use claims. Do not infer broader semantics from the quote.
- Axes impacted: **calibration** (provenance and evidentiary scope overclaim); **operability** (a reader cannot verify the claimed source opening or reproduce the claimed stronger inference from the stated quote).
- Smallest safe correction: remove “S517 opened this round” unless a dated/opening receipt is actually recorded; attribute the quote only to profile call/return semantics and explicitly state it does not establish line execution or result use. Keep frozen claims, counters, controls, and predicates unchanged.

## Commands / outputs / exit status

No campaign counter or source-opening command was run: this seat is limited to claim falsification and the available source-opening receipt is absent. This is **not a pass** for S517 provenance or either frozen counter. Read-only evidence inspected: `freeze.txt` (contains the explicit not-yet-recorded guard) and the round-58 report cited above. No tools installed or updated.
