# Proposed amendment (V3Freeze, round 55 w1) — reconcile the C1 battery with the frozen preregistration

The frozen preregistration (`.ufo/waves/round-55/preregistration.json:19,20,44`) names four
mutants (`m-ldpreload` envnames, `m-ldaudit-writable` code, `m-ldaudit-foreign` hostlibs,
`m-member-flip` rehash), each expected `met=False`; the committed battery
(`.ufo/waves/round-55/c1/battery/`) delivers a re-scoped roster (`m-text-flip` instead of
`m-ldaudit-writable` for the code leg; `m-ldaudit-foreign` as a vector analysis expecting
`met=True`) plus two stale `met=True` receipts from an earlier run. The preregistration is
frozen and must NOT be edited. Proposed non-destructive reconciliation, for the lane owner
to apply:

## 1. Archive the stale receipts (git mv)

```
git mv .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out \
       .ufo/waves/round-55/c1/battery/first-run/m-ldaudit-writable.out
git mv .ufo/waves/round-55/c1/battery/m-extra-in-tree.out \
       .ufo/waves/round-55/c1/battery/first-run/m-extra-in-tree.out
```

Add `.ufo/waves/round-55/c1/battery/first-run/README.md`:

```markdown
# first-run artifacts (round 55 C1 battery)

Receipts from the first battery iteration, superseded by the committed roster in
run-battery.py. They are NOT battery mutants of the final run: m-ldaudit-writable was an
LD_AUDIT env-injection probe (not a code-leg mutation) and m-extra-in-tree fed the
m-text-flip design (backend scan dlcloses an unmapped-in-init DSO). Both print met=True by
design of those probes; the kill rule's "any battery mutant prints met=True" refers to the
run-battery.py roster (control, m-ldpreload, m-text-flip, m-member-flip, m-ldaudit-foreign
as vector), not to these files.
```

## 2. Battery MANIFEST (new file, kills the ambiguity in the kill rule)

Add `.ufo/waves/round-55/c1/battery/MANIFEST.txt`:

```
control            kind=control leg=-            expect met=True  receipt=control.out
m-ldpreload        kind=kill     leg=envnames    expect met=False receipt=m-ldpreload.out
m-text-flip        kind=kill     leg=code        expect met=False receipt=m-text-flip.out
m-member-flip      kind=kill     leg=rehash      expect met=False receipt=m-member-flip.out
m-ldaudit-foreign  kind=vector   leg=hostlibs    expect met=True  receipt=m-ldaudit-foreign.out
```

(and, if adopted, have `run-battery.py` assert its output against this manifest so the
roster and the receipts cannot drift again silently.)

## 3. Amendment note appended to `corpus/lessons/round-55.md` (after the battery paragraph, line 76)

```markdown
  Amendment (recorded post-freeze, before round-55 closure): the battery as committed
  re-scopes the frozen mutant list. The frozen `m-ldaudit-writable (code leg)` was not
  reproducible as a same-uid code mutation; the delivered code-leg kill is `m-text-flip`
  (byte flip in libggml-rpc's late text). The frozen `m-ldaudit-foreign (hostlibs leg)` is
  delivered as a vector analysis (`run-battery.py` kind=vector, expected met=True): the
  LD_AUDIT vector is void on this glibc for a same-uid process, so the receipt evidences
  that the hostlibs kill is root-gated rather than demonstrating a kill. Two first-run
  receipts (`m-ldaudit-writable.out`, `m-extra-in-tree.out`, both met=True) predate the
  final roster and are archived under `first-run/`. The kill rule's "any battery mutant"
  refers to the run-battery.py roster recorded in `MANIFEST.txt`.
```

Rationale: the divergence is between two committed/frozen documents, not a counter defect;
these edits make the delivered battery self-describing so the frozen kill rule has an
unambiguous referent. Written by seat V3Freeze (read-only for the lane); not applied.
