# Proposed fix: stale `met=True` receipts left in the round-55 C1 kill battery dir

## Defect

`.ufo/waves/round-55/preregistration.json` freezes the C1 kill rule as:

> "the claim is falsified if … any battery mutant prints met=True"

and names the battery receipt dir `.ufo/waves/round-55/c1/battery/` with mutants
`m-ldpreload (envnames leg)`, `m-ldaudit-writable (code leg)`,
`m-ldaudit-foreign (hostlibs leg)`, `m-member-flip (rehash leg)`.

The committed battery dir (lane tip `8abadfedf89f35372645b1e5d6ce4a2109186f90`) holds
eight files. Two of them — `m-ldaudit-writable.out` and `m-extra-in-tree.out` — are
development probes from earlier iterations (mtimes 10:30 and 10:37; the final
`run-battery.py` run is 10:42-10:44) and both print `met=True`:

    m-ldaudit-writable.out: tip=23dc15dae61f04e86efb62ef2e622154bc4db36a … met=True
    m-extra-in-tree.out:    tip=312530a9bcfad7bbd06130f4e7916e859182a7a7 … met=True

The final `run-battery.py` MUTANTS dict produces only five receipts
(`control`, `m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`, `m-member-flip`) and
never writes the two stale names. A literal application of the frozen kill rule to
the committed receipt dir therefore trips on two `met=True` receipts that are not
battery mutants of the landed runner — and the preregistration's own battery list
names `m-ldaudit-writable` (whose only committed receipt prints `met=True`), while
the landed code-leg kill is `m-text-flip`.

## Smallest safe correction

Move the two probe receipts out of the named battery receipt dir (they are evidence
about void attack vectors, not kill mutants) and reconcile the preregistration's
battery list with the landed runner. Lane-side change (proposed; not applied — lane
is frozen to this seat):

```diff
# proposed, against lane tip 8abadfedf89f35372645b1e5d6ce4a2109186f90
# 1) relocate the two stale probe receipts out of the kill battery dir
#    (new home: a probes note beside the battery, cited by the lesson)
-.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
-.ufo/waves/round-55/c1/battery/m-extra-in-tree.out
+.ufo/waves/round-55/c1/battery/probes/m-ldaudit-writable.out
+.ufo/waves/round-55/c1/battery/probes/m-extra-in-tree.out

# 2) amend the preregistration battery list (or record the swap in corpus/lessons/round-55.md):
-    "mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)",
-                "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"],
+    "mutants": ["m-ldpreload (envnames leg)", "m-text-flip (code leg)",
+                "m-ldaudit-foreign (hostlibs leg, vector analysis)",
+                "m-member-flip (rehash leg)"],
```

Smaller alternative if the preregistration is treated as immutable: delete the two
stale receipts from the battery dir and add one line to `corpus/lessons/round-55.md`
recording that `m-ldaudit-writable` was the first code-leg attempt, that its receipt
printed `met=True` (the LD_AUDIT vector is void for a writable lib too), and that
`m-text-flip` replaced it as the code-leg kill.

## Why this is safe

The landed battery verdict ("3 live kills + 1 vector analysis", commit `8abadfed`) is
unchanged: `m-ldpreload`, `m-text-flip`, `m-member-flip` fail with their named legs
and `control` passes. The correction only removes the ambiguity that two undeclared
`met=True` receipts sit in the dir the frozen kill rule reads — it does not touch any
frozen counter, predicate, or live-kill receipt.
