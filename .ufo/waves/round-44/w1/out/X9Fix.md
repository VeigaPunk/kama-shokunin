# X9Fix — round-44 D1 and D5 closure proposals (proposals only; no lane byte edited)

**Verdict: both round-43 closure defects reproduce exactly as filed; `d1.diff` and `d5.diff` are
apply-clean (`git apply --check rc=0`), change nothing but the named bytes, and the head's nine
`§` pointers all resolve to existing headings after the diff (`unresolved=0`, exit 0) — with one
landing-order constraint: `d1.diff` must land together with the round-44 `## Round 44` append,
never standalone (see §D1 risk).**

Measured tree: lane working tree at HEAD `098df344d977a9047ea346a01a93c307887570b0`
(`git -C kama-shokunin rev-parse HEAD`). All three target files are clean against that HEAD
(`git status --porcelain` lists only the pre-existing untracked `.ufo/waves/round-44/*` drafts),
so the diffs' preimages are the committed bytes.

Axis this seat moves: **calibration** (a closure defect is either real at the cited line or it is
not; every claim below is a command with an exit code, not a reading).

---

## D1 — the round-43 measured block sits inside the `## Planned` pointer sentence

### Defect (exact lines)

| file:line | text (truncated at 76 chars) |
|---|---|
| `SCORECARD.md:51` | `## Planned` |
| `SCORECARD.md:53` | `Superseded in round 42. The live plan is `##### Round-43 measured results` ← sentence ends mid-phrase |
| `SCORECARD.md:55-65` | the whole round-43 measured-results block (measured commit, claim table, capability census, scores held) |
| `SCORECARD.md:67` | `### Planned (round 44)` at the end of this file; … §Historical head sections.` ← the sentence's tail, 14 lines after its head |

Reproduce:

```
$ awk 'NR>=51&&NR<=55||NR==67{printf "%d|%s\n",NR,substr($0,1,76)}' SCORECARD.md
51|## Planned
52|
53|Superseded in round 42. The live plan is `### Round-43 measured results
54|
55|Measured commit: `25df591a4e50f315b920ec0d0acba6145989e267`, the integration comm
67|### Planned (round 44)` at the end of this file; the round-5 plan this section
```

Two consequences are observable, not stylistic:
1. Line 67 begins with `### `, so a naive heading scan *counts it as a heading*: 127 heading-like
   lines before and after the fix, not 126+1 (`python3` count in §Verification).
2. `tools/round42-selfdesc-reconcile.py:192` takes `section(Planned)` as everything between
   `## Planned` and the next `## ` line — i.e. the entire round-43 measured block. The `planned`
   fact is therefore satisfied only because line 67 happens to contain the literal
   `### Planned (round 44)` inside prose.

### Proposed fix — `d1.diff` (2 hunks, +15/−15 lines on one file)

1. Restore line 53 to the full pointer sentence, now naming the plan round 44 will append:
   `` Superseded in round 42. The live plan is `### Planned (round 45)` at the end of this file;
   the round-5 plan this section carried is kept verbatim under §Historical head sections. ``
2. Move lines 54-66 byte-for-byte under a new heading `### Round-43 measured results` placed
   immediately before `### Planned (round 44)` (after the round-43 canonical capability table).
3. Nothing else. The file stays 2337 lines; `### Planned (round 44)` stays at line 2334;
   `## Retired` moves 69 → 55; the new heading is line 2320, the block 2321-2332.

### Verification (all run in the throwaway clone, then removed)

```
$ git -C "$S/lane" apply --check --verbose d1.diff ; echo rc=$?
Checking patch SCORECARD.md...
rc=0
$ git -C "$S/lane" apply d1.diff && cmp SCORECARD.md d1/SCORECARD.proposed.md ; echo rc=$?
SCORECARD_IDENTICAL            # cmp exit 0: applied text == proposed text
$ wc -l SCORECARD.md           # 2337 before and after
```

**No other change** — multiset diff of the old and new line lists (`collections.Counter`):

```
ADDED:   +1  Superseded in round 42. The live plan is `### Planned (round 45)` at the end of this file; …
         +1  ### Round-43 measured results
REMOVED: -1  Superseded in round 42. The live plan is `### Round-43 measured results
         -1  ### Planned (round 44)` at the end of this file; … §Historical head sections.
MOVED block byte-identical: 11 lines, 3382 chars   (old 54:65 == new block, list equality)
heading-like lines: 127 before, 127 after           (pseudo-heading removed, real heading added)
tail heading order: [..., '## Round 43 — …', '### Round-43 measured results', '### Planned (round 44)']
```

**Required `§`-pointer check** (head = everything before `## Historical head sections`; a pointer
resolves if it names a heading, a round-qualified heading, or an external `.md` named earlier on
the same line):

```
$ python3 -c "…"  | tee scorecard-pointer-check.out
head_lines=136 head_section_pointers=9 unresolved=0
  RESOLVED line 3   [external-file]           SCORECARD.md contract -> line names a .md before the pointer
  RESOLVED line 6   [heading]                 Planned -> Planned
  RESOLVED line 6   [heading]                 Retired -> Retired
  RESOLVED line 6   [heading]                 Saturation and -> Saturation
  RESOLVED line 6   [heading]                 Capabilities below are re-derived from the tree by -> Capabilities
  RESOLVED line 6   [heading]                 Historical head sections. Completed rounds … -> Historical head sections (superseded in round 42)
  RESOLVED line 53  [heading]                 Historical head sections -> Historical head sections (superseded in round 42)
  RESOLVED line 117 [heading]                 Round 43 carries -> Round 43 — instrument registry reconciled (calibration), …
  RESOLVED line 131 [heading]                 Capabilities -> Capabilities
heading Round-43 measured results present: True
POINTER_CHECK_EXIT=0
```

Line 53 is the pointer this diff rewrites; it is the only head pointer that the move touches, and
it resolves. `git diff --check` exits 0 (no whitespace damage); all three files keep their final
newline (`tail -c 1 | xxd` → `0a`).

### D1 risk — landing order (do not drop this)

`tools/round42-selfdesc-reconcile.py:192-202` derives `ph = "### Planned (round <maxN+1>)"` from
the highest `## Round N` heading and requires `ph` to appear inside `section(Planned)`. Simulated
on the proposed text (`planned-landing-order.out`, replicating those lines exactly):

```
as-diff-alone:   maxn=43 expected_heading=### Planned (round 44) named_in_section_Planned=False … planned_mismatches=1
after-r44-append: maxn=44 expected_heading=### Planned (round 45) named_in_section_Planned=True  … planned_mismatches=0
```

So: **land `d1.diff` inside the round-44 SCORECARD append** (the commit that adds `## Round 44`
and its `### Planned (round 45)`). Applied alone at the current HEAD it fixes the prose but
regresses the `planned` fact by 1, because `### Planned (round 45)` exists only after the append.
The `### Planned (round 45)` target is not an `§` pointer, so it is outside the pointer check's
scope by construction; it is named here so the L1 does not read `unresolved=0` as covering it.

---

## D5a — the two round-41 rows carry a stray backtick

### Defect (exact bytes)

`grep -n 'sha256 `[0-9a-f]*``' SKILL.md` → lines 1395 and 1396 (section
`## Round-43 registry completion (counters of rounds 35-43)`, `SKILL.md:1378`):

```
$ python3 -c "…print(repr(line[line.index('sha256')-4:][:30]))"
1395 ' | `sha256 `4ca5ddee1b42`` of the '
1396 ' | `sha256 `eff934a27b3e`` of the '
```

These are the only two cells of that shape (`grep -c '`sha256 `' SKILL.md` → 2); the fourteen
sibling rows all use plain `sha256` + a backticked prefix, e.g.
`SKILL.md:1394` = ``ter sha256 `c227aedb3857` at `8957``, and the counter's own docstring states
the cell form as `sha256 `<hex>`` (`tools/round43-registry-audit.py:25`).

### Proposed fix — `d5.diff` (hunk 1 of 2)

Delete the backtick before `sha256` and the duplicate backtick after the hash (2 characters per
row, no word changed):

```
- | `sha256 `4ca5ddee1b42`` of the blob at 895793e0; …
+ | sha256 `4ca5ddee1b42` of the blob at 895793e0; …
```

Backtick-run analysis (`python3 -c`, receipt inline above): old rows contain a run of **2**
backticks; new rows have max run **1** and an even run count (38 and 26), i.e. every run pairs
into a well-formed code span.

Counter impact: **none, verified.** `tools/round43-registry-audit.py:78` parses pins with
`SHA_RE = re.compile(r"sha256 `([0-9a-f]{8,64})")` and only needs `want.startswith(prefix)`
(`:151-170`); the fixed cell still matches, and the prefixes are the real blob prefixes:

```
$ git show 895793e0:tools/round41-pinwatch-audit.py | sha256sum
4ca5ddee1b42cb2f9611942ed8bb20957d69add21415be46af052440ddcc7e97
$ git show 895793e0:tools/round41-scorecard-reconcile.py | sha256sum
eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6
```

## D5b — the malformed commit time in the hexrun ledger

`registry/hexrun-ledger.tsv:62`, note field (col 7 of 7):

```
…  2026-10-25  commit 2026-10-25:T08:05:18Z - fleet commit "round-37: kama report" (adds …
```

There is a stray `:` between the date and the `T` of the ISO timestamp. The clock value itself is
correct — `git -C /home/vgpnk/Projects/shokunin show -s --format='%ci|%cI' a7361db0…` →
`2026-10-25 05:05:18 -0300|2026-10-25T05:05:18-03:00`, i.e. `08:05:18Z`. The round-43 seat
receipt `.ufo/waves/round-43/w1/out/W1X10.md:63` already renders the same commit as
`2026-10-25T08:05:18Z`, so the ledger is the outlier.

### Proposed fix — `d5.diff` (hunk 2 of 2)

One character deleted, nothing else:

```
- a7361db0…  commit 2026-10-25:T08:05:18Z - fleet commit "round-37: kama report" …
+ a7361db0…  commit 2026-10-25T08:05:18Z - fleet commit "round-37: kama report" …
```

Field integrity after the fix (`python3` diff of the two byte strings): 79 lines → 79 lines; the
single differing line is 62; 7 tab-separated fields; every field except the note is byte-equal;
note length 173 → 172. `tools/hexrun-census.py:274` reads the note only through
`len(row.note) >= NOTE_MIN` (10) — still satisfied, so the row's `unprovable`/`ledger_bad`
classification and `tools/round43-hexrun-audit.py`'s `ledger_bad=0` leg are unaffected.

### Defect class (reported, deliberately not fixed beyond the named instance)

The same malformation occurs on **eight** ledger rows, 59-66, not one:

```
$ python3 -c "…scan notes…"
line 59 19b66dd47215 note=2026-10-25:T00:33:06Z real=2026-10-24 21:33:06 -0300   (= 2026-10-25T00:33:06Z)
line 60 428a0560daa8 note=2026-10-25:T02:14:02Z real=2026-10-24 23:14:02 -0300   (= 2026-10-25T02:14:02Z)
line 61 296981080328 note=2026-10-25:T02:14:45Z real=2026-10-24 23:14:45 -0300   (= 2026-10-25T02:14:45Z)
line 62 a7361db0097b note=2026-10-25:T08:05:18Z real=2026-10-25 05:05:18 -0300   (= 2026-10-25T08:05:18Z)
line 63 f8116dcd6411 note=2026-10-25:T09:30:09Z real=2026-10-25 06:30:09 -0300   (= 2026-10-25T09:30:09Z)
line 64 58fde7e12a95 note=2026-10-25:T19:33:22Z real=2026-10-25 16:33:22 -0300   (= 2026-10-25T19:33:22Z)
line 65 48199b98dc97 note=2026-10-25:T20:42:32Z real=2026-10-25 17:42:32 -0300   (= 2026-10-25T20:42:32Z)
line 66 af737dd1ba64 note=2026-10-25:T22:54:41Z real=2026-10-25 19:54:41 -0300   (= 2026-10-25T22:54:41Z)
```

The closure named only the `a7361db0…` instance (`corpus/lessons/round-43-verifier-spotcheck.md:109`),
so `d5.diff` stays exactly that scope. `d5-class-optional.diff` is the same two SKILL hunks plus the
one-character deletion on all eight rows; it also passes `git apply --check` (rc=0). Applying it is
the L1's call, not this seat's.

---

## Non-findings (checked, nothing done)

- `SCORECARD.md:65` ends with a real sentence ("…the closure judges relevance and sufficiency."),
  not a truncated ellipsis: an earlier read display cut it; byte check says otherwise. No change
  proposed.
- No counter reads `SCORECARD.md` for `Measured commit`/`Round-43 measured` (`grep -rn` over
  `tools/*.py` → no hits), and the only consumer of `## Planned` is
  `tools/round42-selfdesc-reconcile.py:192`; `round43-hexrun-audit.py:379` reads only the highest
  `canonical list as of round N` table, which the move leaves in place and unchanged.
- No lane file was edited: all writes went to
  `.ufo/waves/round-44/w1/out/X9Fix/`. No commit, checkout, reset or add in the lane; the scratch
  clone was `git clone --shared` under `/fast/scratch/hyaku/kama-r44/X9Fix/` and is deleted.

## Tooling

None installed or upgraded this seat (no `pacman`, no `uv`, no network fetch); `git`, `python3`,
`diff`, `cmp` and coreutils only.

## Blocker / handoff for the L1

Not blocked. Handoff: apply `d1.diff` inside the round-44 SCORECARD append (§D1 risk), apply
`d5.diff` (or `d5-class-optional.diff` if the class fix is wanted) in the same round, then run the
post-integration gates `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip <commit>`
and `python3 tools/round43-registry-audit.py --repo <clone> --tip <commit> --out <receipt>`.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/d1.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/d5.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/d5-class-optional.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/SCORECARD.proposed.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/SKILL.proposed.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/hexrun-ledger.proposed.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/hexrun-ledger.class-proposed.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/scorecard-pointer-check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/planned-landing-order.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Fix/apply-check.out`
