# F1 — frozen preregistration battery contract vs committed battery outcome

## The frozen text (immutable, committed in 9c60eae6)

`.ufo/waves/round-55/preregistration.json`:

- `:44` `"mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`
- `:19` C1 target: "kill battery: each named mutant receipt prints met=False (exit 1) with its named leg failing; the unmutated positive control prints met=True."
- `:20` C1 kill_rule: "the claim is falsified if ... any battery mutant prints met=True ..."

## What the committed battery actually is (8abadfed; unchanged at bf336baa)

`.ufo/waves/round-55/c1/battery/run-battery.py` `MUTANTS` has 4 keys:

| frozen name | committed runner | outcome | frozen expectation met? |
|---|---|---|---|
| m-ldpreload (envnames) | m-ldpreload kind=kill | met=False exit 1, envnames=0/3 | yes |
| m-ldaudit-writable (code) | — absent; replaced by m-text-flip kind=kill (code) | m-text-flip.out met=False exit 1, code=0/3 | code leg killed by an unfrozen mutant name |
| m-ldaudit-foreign (hostlibs) | m-ldaudit-foreign kind="vector" (run-battery.py:57-62) | met=True exit 0, hostlibs=3/3 | NO — named mutant prints met=True; runner's own ok-rule for it is `rc==0 and met` (:137-138) |
| m-member-flip (rehash) | m-member-flip kind=kill | met=False exit 1, rehash=3 | yes |

## Verdict as frozen

Read literally, the frozen kill rule is tripped by a committed receipt:
`m-ldaudit-foreign.out` is a preregistration-named battery mutant that prints
`met=True` (exit 0). The frozen target sentence ("each named mutant receipt prints
met=False (exit 1) with its named leg failing") is also unmet for it — the hostlibs
leg has no live kill anywhere in the battery (the LD_AUDIT vector is void on this
glibc, run-battery.py:54-56). The lesson now records this verbatim
(`corpus/lessons/round-55.md:95-104`: "not repaired in the frozen preregistration"),
so the defect is a disclosed freeze-contract inconsistency, not a hidden one.

## Proposed fix (full text — for a follow-up freeze; the frozen file must not be amended)

1. Follow-up preregistration (next attempt/round) states the battery contract as
   delivered, e.g.:
   `"mutants": ["m-ldpreload (envnames leg, kill)", "m-text-flip (code leg, kill)", "m-member-flip (rehash leg, kill)", "m-ldaudit-foreign (hostlibs leg, vector analysis — expected met=True; the LD_AUDIT injection is void on this host's glibc, evidence that the live hostlibs kill is root-gated)"]`
   and
   `kill_rule: "... falsified if any kill mutant prints met=True, if the vector receipt prints met=False or trips a leg other than its named analysis, ..."`
2. If the hostlibs leg is to keep a live kill, implement it as a root-side
   scenario (a same-uid LD_AUDIT injection cannot reach it — proven by the
   vector receipt); otherwise restate the leg's coverage as "root-actor plants,
   evidenced by vector analysis" in both predicate and target.
3. When a mutant cannot be made to trip before data, withdraw or re-class it in
   the freeze text itself — do not substitute an unfrozen mutant name (m-text-flip
   for m-ldaudit-writable) after freeze; the substitution's only committed record
   is currently in code comments and the w1 commit message.
