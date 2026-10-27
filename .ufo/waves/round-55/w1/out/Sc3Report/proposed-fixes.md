# Proposed fixes for round-55 defects found while drafting the L1 report

Nothing here was applied. The lane is read-only for this seat; every item is a proposal
for the L1 / a later round. Frozen artifacts (preregistration, counters, controls) are
not proposed for edit — where a defect lives in a frozen artifact it is reported, not
patched.

## F1 — battery receipts carry no exit code

Defect: `.ufo/waves/round-55/c1/battery/*.out` (7 files, each 24 or 48 lines) contain
`tip=`, the aggregate leg line and `detail:` lines only. The preregistration's target and
kill rule talk about exits (`preregistration.json:19-20`), and `build_spec.py:25-26`
asserts them, but no committed artifact records the exit of any battery run. The harness
computes it and prints it to stdout only (`run-battery.py:111-112,146`).

Shows it: `grep -c '^exit=' .ufo/waves/round-55/c1/battery/*.out` → `0` for every file;
`grep -n 'exit=' .ufo/waves/round-55/c1/battery/run-battery.py` → line 146 (stdout print).

Proposed fix (harness change, next freeze): append the observed exit to each receipt.
Patch against `.ufo/waves/round-55/c1/battery/run-battery.py:111-112`:

```diff
--- a/.ufo/waves/round-55/c1/battery/run-battery.py
+++ b/.ufo/waves/round-55/c1/battery/run-battery.py
@@ -109,6 +109,8 @@
         p = run([sys.executable, COUNTER, "--repo", clone, "--tip", tip,
                  "--scratch", os.path.join(SCRATCH, f"run-{name}"), "--out", outp], env=env)
         text = open(outp).read() if os.path.isfile(outp) else p.stdout
         met = "met=True" in text.splitlines()[1] if len(text.splitlines()) > 1 else False
+        if os.path.isfile(outp):
+            with open(outp, "a") as fh:
+                fh.write(f"exit={p.returncode}\n")
         return p.returncode, met, text
```

(Line 2 stays the leg line, so the `met=` parse at line 111 is unaffected.)

## F2 — two battery receipts are not attributable to the committed harness

Defect: `run-battery.py:23-85` defines exactly four `MUTANTS` keys —
`m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`, `m-member-flip`. The battery directory
also holds `m-extra-in-tree.out` (`tip=312530a9…`) and `m-ldaudit-writable.out`
(`tip=23dc15da…`), which no committed harness revision produces. The preregistration
names `m-ldaudit-writable` as a mutant (`preregistration.json:44`), so its receipt is
load-bearing evidence that cannot be regenerated from the frozen harness.

Shows it (run from the lane root):
```sh
python3 -c "import re;s=open('.ufo/waves/round-55/c1/battery/run-battery.py').read();print(sorted(re.findall(r'\"(m-[a-z-]+)\": \(', s)))"
# -> ['m-ldaudit-foreign', 'm-ldpreload', 'm-member-flip', 'm-text-flip']
ls .ufo/waves/round-55/c1/battery/ | grep '^m-'
# -> six receipts: the four above plus m-extra-in-tree.out and m-ldaudit-writable.out
```

Proposed fix (documentation, this round): list both orphan receipts in the report's
battery table as *not produced by the frozen harness*, with their `tip=` values, and
either (a) re-derive them at the next freeze from a committed harness revision, or (b)
delete them from the evidence set and keep only the four harness-produced receipts +
`control.out`:

```sh
git rm .ufo/waves/round-55/c1/battery/m-extra-in-tree.out \
       .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
```

## F3 — SKILL.md registry rows describe the round-54 counter state

Defect: `SKILL.md:1598` pins the C1 counter "base `0b75a84c`" but the round-55 freeze
re-bases C1 to `3a600d2f` (`preregistration.json:7`). `SKILL.md:1599` says
`scenarios=N/14` and "fourteen constructed scenarios" while the frozen counter prints
`scenarios=15/15` (`measured/c2-build.out:2`). The C2 row's own base `0b75a84c` is
correct and must NOT change.

Shows it:
`sed -n 1598,1599p SKILL.md | grep -o 'base `[^`]*`\|scenarios=N/[0-9]*\|fourteen constructed scenarios'`
→ `base `0b75a84c`` (row 1598), `scenarios=N/14` and `fourteen constructed scenarios`
(row 1599).

Proposed fix (integration, after the wave; exact substrings, unique anchors):

1. Line 1598: replace `13-name frozen host set, base `0b75a84c`;` with
   `13-name frozen host set, base `3a600d2f`;` (the longer anchor leaves the C2 row's
   base untouched).
2. Line 1599: replace `scenarios=N/14` with `scenarios=N/15`.
3. Line 1599: replace `fourteen constructed scenarios` with
   `fifteen constructed scenarios`.

Then re-run `python3 tools/gate-registry-check.py` and
`python3 tools/round42-selfdesc-reconcile.py` (registry cell count is unchanged; the
self-description counter is the one that watches these rows).

## F4 — the round-55 lesson pre-claims a census receipt that does not exist

Defect: `corpus/lessons/round-55.md:98-101` states the round ends with the sources census
at exit 0 and receipt `.ufo/waves/round-55/census/end.out`. At `8abadfed` the wave tree
holds only `census/start.out`, whose last line is `census_start_exit=1` (line 102, the
E11 S510 dangling used-by at round start).

Shows it:
`ls .ufo/waves/round-55/census/` → `start.out` only;
`tail -1 .ufo/waves/round-55/census/start.out` → `census_start_exit=1`.

Proposed fix (round end, L1):
```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
  --root /home/vgpnk/Projects/shokunin kama > /dev/null  # expect exit 0
# commit the receipt as .ufo/waves/round-55/census/end.out
```
If exit is not 0, fix the row (S510's used-by now points at the existing
`corpus/lessons/round-55.md`, so the E11 should be closed) and, if it still cannot close,
correct the lesson text instead of leaving the receipt named but absent.

## F5 — no LOG.md round-55 entry and no SCORECARD round-55 section

Defect: `LOG.md`'s last round heading is `## Round 53` (`LOG.md:2435`); `SCORECARD.md`'s
live plan pointer is `### Planned (round 54)` (`SCORECARD.md:3048`) and there is no
`round 55` occurrence anywhere in `SCORECARD.md` or `SKILL.md` (case-insensitive grep).

Shows it:
`grep -n '^## Round ' LOG.md | tail -1` → `2435:## Round 53 …`;
`grep -ni 'round.55' SCORECARD.md | wc -l` → `0`.

Proposed fix (integration): land the round-55 LOG paragraph naming the round-54
wrap-up it answers, and a SCORECARD `## Round 55` section carrying both claims with the
leg lines/exits and receipt paths, then move the live plan pointer to
`### Planned (round 55)`. `round41-scorecard-reconcile.py` and
`round42-selfdesc-reconcile.py` are the gates that will notice if the pointer and the
counts disagree.

## F6 — the kill rule's "any mutant `met=True`" clause and the vector receipts

Defect (conflict, not a mechanical fix): `preregistration.json:20` falsifies C1 "if any
battery mutant prints `met=True`"; `preregistration.json:44` lists
`m-ldaudit-writable` and `m-ldaudit-foreign` as mutants; both receipts print `met=True`
(`m-ldaudit-writable.out:2`, `m-ldaudit-foreign.out:2`), and the harness deliberately
labels `m-ldaudit-foreign` a `vector` whose pass is "the finding"
(`run-battery.py:52-59,137-139`).

Shows it:
```sh
head -2 .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
head -2 .ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out
sed -n 20p .ufo/waves/round-55/preregistration.json
```

Proposed disposition (report prose, not a patch to the frozen file): state in the report
that the battery comprises three live kills (`m-ldpreload`/envnames,
`m-text-flip`/code+bind, `m-member-flip`/rehash), one positive control, one void vector
(`m-ldaudit-foreign`, root-gated hostlibs) and two receipts not produced by the frozen
harness (`m-ldaudit-writable`, `m-extra-in-tree`); then let the judge rule whether the
kill rule as written is met. Do not rewrite `preregistration.json`.
