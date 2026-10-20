VERDICT: partial — "named survivors -> 0" is honest only if stated as a bounded survivor-set kill with a declared denominator; as specified the count is closed, author-chosen, and silently repeats round 17's "10 of 10" trap.

# Axes named

- **calibration** — does the count mean what the lesson will claim it means.
- **coverage / stated universe** — which mutants the denominator spans.
- **independence** — who authored the mutants and when (author-blind vs tailored).
- **comparability / no-harm** — did kills for named survivors trade away prior kills.

# The attack

## A. The set is closed and self-referential

`survivors.py` is specified to run *only* the named survivors: "Each named survivor is a single-site edit located by exact source-string match" (`build/spec.json:39`, item `C2Survivors`). The named set is exactly what round-17 attacker seats published: H1–H3, H5–H7 (`round-17/falsify/advice/MutC1Preregistered.md:17-19`, `MutC1Preregistered2.md:15-17`), the fault-controls weakenings (`MutFaultControlsSelf.md:22-25`), the append-only weakenings (`MutAppendOnlyGuard.md:54-55`), plus provenance/crash/timeout findings. A count over exactly these can reach 0 by construction once each gets a dedicated fault — the detector work item literally maps one new fault per named survivor: "Add one fault per surviving check.py mutant so that the mutant is killed while the current check.py detects the fault" (`build/spec.json:29`, item `C2FaultControls`). That is tailoring faults to the published survivor list; it cannot detect a *fresh* weakening, because a fresh mutant is by definition absent from the counting command's registry. The command is closed-world: there is no slot for a wave-2 mutant to enter the denominator.

Precedent that this exact failure mode recurs: round 17 measured "current/full **10 of 10**" over its registered author set (`corpus/lessons/round-17.md:161-164`), while three seat-authored mutants survived the same detectors the same round (`MutC1Preregistered.md:1` "H1–H3 survive both bounded detectors"; `MutC1Preregistered2.md:1` "H5–H7 survive fault-controls and the pair"). The lesson itself already scoped the honest shape of the claim: "The C1 claim is therefore 'the documented gradings plus served_model and route now each have a killing fault', not 'check.py cannot be weakened'" (`corpus/lessons/round-17.md:285-286`). Round 18's "named survivors -> 0" needs the same scoping, or it reads as "the detectors cannot be weakened."

## B. Kills for named survivors may trade against prior kills

The spec's kill predicate is per-mutant against frozen-vs-current detectors; nothing in the round-18 items requires rerunning the previously-killed set (round-17 grid mutants M1–M8, faults F1–F8, selftest cases) on the new detectors. Adding F9+ faults could weaken an existing conjunct in a way that *kills an H mutant while un-killing a prior registered mutant* — e.g. the H6 fix touches the no-request acceptance branch that M5's `timeout-pass` mutant also reaches via the early return (`TimeoutPath.md:66-72` shows M5 inserts `record["passed"] = True` in the timeout branch; H6 inserts it before the no-stub-requests return, `MutC1Preregistered2.md:40-46`). [INFERENCE] A fix scoped only to the six named survivors could plausibly regress an un-retested adjacent kill; only a retained prior-kill arm proves it did not.

## C. Equivalent-mutant declarations exist only for the H family

The wave-1 reviewer covers equivalence for exactly six mutants: "an equivalent mutant must be declared, not 'killed'" (`build/spec.json:234`, item `RevHKillability`). No equivalent/n-a disposition is specified for the other families (detector-self, append-only, provenance, crash, timeout), and `survivors.py` as specified has outcome killed/survived/`site_missing` only. The lane's own registry vocabulary already needs a third bucket: S045 admits killed/survived/no-coverage with "killed over applicable per mutant and detector" (`corpus/SOURCES.md:57`), and round 17 established the n-a precedent — H8 "is excluded from the mutation denominator; it is not a fourth survivor or a killed mutant" (`MutC1Preregistered.md:22`). If any named "survivor" turns out equivalent on the repaired tool, silently folding it into killed inflates the count; silently dropping it shrinks the denominator. Both must be declared.

Also note `RevHKillability`'s equivalence test is *input-bounded*: "whether a probe-output fault exists that the CURRENT check.py rejects but the mutant accepts" (`build/spec.json:234`). A mutant for which no tested input distinguishes it is **equivalent-under-the-detector's-input-set**, not equivalent — declare it as such, because a future matrix row could resurrect it.

# What the round must add so the count is not cherry-picked

1. **Stated universe, in the lesson, before counting.** Name the denominator: "the N mutants registered in `survivors.py`'s registry — the round-17 seat-published survivors plus K previously-killed regression mutants" (or a generated grammar: every single-site drop/weaken of each comparison conjunct and each selftest row in the three tools). Anything outside that universe is not counted; the lesson must say so in the same sentence as the 0. A generated grammar is cheap and far more damning than another hand-picked list — it converts "survivors -> 0" into "mutation score k/N over grammar G," which is falsifiable.
2. **Fresh non-author mutants in wave 2, preregistered before they see the new detectors.** Round 17's own method — seat-authored mutants the C1 authors never saw — produced all six H survivors. Dispatch falsify seats to (a) write fresh single-site mutants in the *registry format* `survivors.py` already consumes (exact old->new string, detector, expectation), and (b) append them to the registry so the post-fix count includes kills *and* survivors of mutants nobody tailored a fault to. Report `fresh: killed X of Y`, separately from `named: killed N of N`. If wave 2 produces zero fresh mutants (rate limits killed seven seats last round, `round-17-verifier-spotcheck.md` R7 list), the lesson must state that the fresh arm is empty — an absent arm, not a zero-survivor arm.
3. **Explicit outcome set: killed / survived / equivalent / not-applicable / site_missing.** Every declared equivalent mutant carries the bounded-equivalence reason (per C) and is excluded from the denominator *visibly*, per the H8 precedent (`MutC1Preregistered.md:20-22`) and S045's applicable-only denominator (`corpus/SOURCES.md:57`).
4. **Retained prior-kill arm.** Rerun the still-applicable round-17 registered mutants and F1–F8 faults against the new detectors; a killed->survived transition is a regression finding, not a wash. Per B, adjacency of H6/M5 sites makes this non-ceremonial.
5. **Survivor count stays signed.** "0" means: every *named* survivor is now killed *and* the fresh arm found none *and* no prior kill regressed — three conjuncts, each printed, not one integer.

# The honest claim (drop-in phrasing for the lesson)

> "Of the N mutants named by round-17 non-author seats (H1–H3, H5–H7, three detector-self weakenings, two append-only weakenings, the refused-count and crash/timeout paths), all applicable are killed by the current detectors, with E declared equivalent (bounded: no probe-output fault distinguishes them) and S surviving. Wave-2 fresh non-author mutants: killed X of Y. Prior kills retained: K of K. This bounds detector strength to the stated universe; it does not show the detectors cannot be weakened."

If the fresh arm is empty: replace sentence three with "No wave-2 fresh mutants were produced; the fresh arm is absent, not zero-survivors."

# Limitations

- I read the spec items, the round-17 advice files, lesson debt list, and spot-check routed defects; I ran no detector and mutated no bytes (read-only seat).
- `survivors.py`, the new `fault-controls.py`, and new `check.py` do not yet exist; statements about them are statements about `build/spec.json` items as written [INFERENCE on landed behavior].
- Whether wave 2 exists / dispatches fresh mutation seats is L1's call; item 2 is conditional on it.
- Installs: none. Python 3.14.8, git, grep only; no ports bound.
