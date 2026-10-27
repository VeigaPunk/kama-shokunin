# X2C2Rerun — round-55 C2 independent re-measurement (lane kama)

**VERDICT: the frozen C2 counter reproduces the recorded receipts byte-for-byte and is
verdict-stable across 9 repeats, BUT the landed `superseded` class is unanchored and
unsound: three hand-built mutants of the real lane tree PASS the frozen counter with
met=True (bad=0 stale=0 dropped=0) while violating the preregistered predicate's own
"live base citation re-pointed" wording. Proposed fix + 2 new fixture scenarios are in
this seat's out dir; the fix keeps the honest landed tip green (17/17) and the base
control red, and kills all three mutants.**

Seat: X2C2Rerun (leaf). Lane: `kama`. Round: 55, wave 1, attempt 1.
Lane commit under test: `9c60eae6f7ed84f7da93d219a406aadc30958c6c`.
Base control tip: `3a600d2f729828419aaea34cc402c8b0d20fb720`.
Counter's own frozen `BASE` constant: `0b75a84c56e024cac1662e8ff81802f249acb410`
(round-53 tip, as preregistered).

---

## 1. Independent measurement — field-by-field against the frozen receipts

### 1.1 Commands

Clone (the seat's own; the lane repo was never written to):

```
S=/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun ; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel     # -> /fast/scratch/hyaku/kama-r55/w1/X2C2Rerun/lane
git -C "$S/lane" cat-file -t 9c60eae6f7ed84f7da93d219a406aadc30958c6c   # commit
git -C "$S/lane" cat-file -t 3a600d2f729828419aaea34cc402c8b0d20fb720   # commit
git -C "$S/lane" cat-file -t 0b75a84c56e024cac1662e8ff81802f249acb410   # commit
```

Counter (FROZEN; bytes never edited):

```
T=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py
sha256sum $T
# d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c
git -C "$S/lane" show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-cited-path-check.py | sha256sum
# d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c   <- matches prereg claims.C2.counter_sha256
```

Runs (each with `--out <receipt>`):

```
python3 $T --repo "$S/lane" --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
  --fleet /home/vgpnk/Projects/shokunin --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b \
  --scratch "$S" --out "$OUT/A-tip9c60eae-fleet6c4aba34.out"      # exit 0
python3 $T --repo "$S/lane" --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 \
  --fleet /home/vgpnk/Projects/shokunin --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b \
  --scratch "$S" --out "$OUT/C-tip3a600d2f-fleet6c4aba34.out"      # exit 1
```

`6c4aba34c2a22519152d8c6f32e1039eecb1381b` is the fleet rev recorded in both frozen
receipts (`fleet=` field), so the run is byte-comparable with them. The fleet repo's
`HEAD` moved during the wave (`47a18cd6` -> `4dd6935e`); §1.3 shows the fleet rev does
not change any counted field.

### 1.2 Field-by-field result

| source | tip | fleet | fixture | lane | scenarios | cited | unresolved | disclosed | undisclosed | bad | stale | dropped | met | exit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `measured/c2-build.out` (frozen) | 9c60eae6 | 6c4aba34 | 1 | 1 | 15/15 | 693 | 14 | 14 | 0 | 0 | 0 | 0 | True | 0 |
| **seat run A** (landed tip) | 9c60eae6 | 6c4aba34 | 1 | 1 | 15/15 | 693 | 14 | 14 | 0 | 0 | 0 | 0 | True | 0 |
| `controls/base.c2.out` (frozen) | 3a600d2f | 6c4aba34 | 1 | 0 | 15/15 | 693 | 14 | 14 | 0 | 0 | 0 | **1** | False | 1 |
| **seat run C** (base tip) | 3a600d2f | 6c4aba34 | 1 | 0 | 15/15 | 693 | 14 | 14 | 0 | 0 | 0 | **1** | False | 1 |

`cited`, `unresolved`, `disclosed`, `dropped` agree on **every** field, in both the
landed and the base direction. The only difference is `fleet`, and only when the fleet
rev is changed on purpose (§1.3).

Whole-file diffs:

```
diff "$OUT/A-tip9c60eae-fleet6c4aba34.out" .ufo/waves/round-55/measured/c2-build.out   -> IDENTICAL
diff "$OUT/C-tip3a600d2f-fleet6c4aba34.out" .ufo/waves/round-55/controls/base.c2.out    -> IDENTICAL
```

So the frozen build measurement and the frozen base control are exactly reproduced —
including all 15 fixture detail lines, all 4 advisory lines, and the base control's
single drop line:

```
detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)
```

### 1.3 Fleet-rev sensitivity (the "fleet rev may differ" allowance)

Three extra runs with different fleet revs; every counted field is unchanged, only the
`fleet=` field moves:

| run | tip | fleet rev | fixture | lane | scenarios | cited | unresolved | disclosed | dropped | met | exit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D | 9c60eae6 | 4dd6935e (HEAD at run time) | 1 | 1 | 15/15 | 693 | 14 | 14 | 0 | True | 0 |
| F | 9c60eae6 | 47a18cd6 | 1 | 1 | 15/15 | 693 | 14 | 14 | 0 | True | 0 |
| E | 3a600d2f | 4dd6935e (HEAD at run time) | 1 | 0 | 15/15 | 693 | 14 | 14 | 1 | False | 1 |

**Conclusion:** the fleet rev is irrelevant to the C2 verdict; the recorded receipts'
`fleet=6c4aba34` is not a hidden dependency of the measurement.

### 1.4 Verdict stability and wall time (3+ runs at the landed tip)

Nine runs at `9c60eae6` (run A plus `rep1`..`rep9`), all with `--fleet-rev 6c4aba34`:

```
rep1 exit=0 wall=1.49s   rep2 exit=0 wall=1.44s   rep3 exit=0 wall=1.46s
rep4 exit=0 wall=1.40s   rep5 exit=0 wall=1.35s   rep6 exit=0 wall=1.31s
rep7 exit=0 wall=1.43s   rep8 exit=0 wall=1.54s   rep9 exit=0 wall=1.48s
(A)   exit=0 wall=2.54s   <- first run, cold page cache / first upstream fetch
```

```
for i in 1 2 3 4 5 6 7 8 9; do diff -q A-....out rep$i-....out; done   -> ALL_IDENTICAL
```

**Verdict stability: perfect.** 9/9 runs exit 0, and all nine receipts are byte-identical
(same `tip`, `fleet`, all counts, all 15 fixture detail lines, all 4 advisory lines).
Wall time: 1.31–1.54 s warm (median ~1.45 s), 2.54 s on the first (cold) run. The
preregistered "~2 s" estimate is right.

### 1.5 Independent cross-check (not via the counter's own CLI)

`xcheck_c2.py` in this out dir imports the frozen counter read-only and re-derives the
four fields from the counter's own `survey()`/`citation_lines()` primitives, so the
numbers are not just the counter's own printout:

* landed tip `9c60eae6`: `cited=693 unresolved=14`, 17 ledger rows, and the 14
  unresolved tokens are exactly the 14 that the ledger discloses (9 `never`,
  1 `deleted`, 1 `untracked`, 5 `upstream`) — 0 undisclosed. Raw drop set
  (before exemption) = `{SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md}`,
  and that token IS exempt via the `superseded` row, so `dropped=0`.
* base tip `3a600d2f`: ledger has 16 rows (no `superseded` row), raw drop set is the
  same single token, nothing exempts it -> `dropped=1`.
  Receipts: `xcheck-tip9c60eae.txt`, `xcheck-tip3a600d2f.txt`.

### 1.6 Environment note (non-defect, disclosed for completeness)

With the network blocked (`http_proxy=http://127.0.0.1:9`), the counter exits **2**
with `could-not-evaluate: upstream evidence https://raw.githubusercontent.com/... unfetchable`
rather than a false verdict. That is the documented `Unevaluable` path (counter
docstring: "Exit 0 met, 1 not met, 2 could not evaluate"), i.e. correct behaviour, not a
defect. Receipt: `G-offline-stdout.txt`. It does mean the counter is network-dependent
for its `upstream` rows; the prereg `limits` already records that `upstream` rows fetch
`raw.githubusercontent.com`.

---

## 2. DEFECT — the landed `superseded` class is unanchored (C2 counter)

### 2.1 The defect, precisely

**File:** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py`
**Lines:** 461–479 (`check_row`, the `superseded` branch); the anchor that is missing
sits at **line 478** (last check before `return None`).

The preregistered predicate (`.ufo/waves/round-55/preregistration.json`,
`claims.C2.predicate`) requires:

> "`superseded` rows disclosing a **live base citation re-pointed** to a cited, resolving
> replacement, with no bad or stale row and **no citation dropped** on any of the three
> surfaces since the base"

The counter's own class comment (lines 462–468) says the same:

> "The token is no longer cited at tip, it WAS cited at base (unlike `fixed`, whose token
> was unresolved at base), and the replacement token is cited in that surface at tip and
> resolves."

But the implementation only checks three things:

```python
461    if cls == "superseded":
...
470        if tok in cited_tip.get(surf, {}):
471            return "superseded token is still cited at tip"
472        rep = cited_tip.get(surf, {}).get(ev)
473        if rep is None:
474            return f"replacement {ev!r} is not cited in {surf} at tip"
475        if any(v != "ok" for _e, v in rep):
476            return f"replacement {ev!r} does not resolve at tip"
477        if base_citelines is not None and tok not in (base_citelines.get(surf) or {}):
478            return "superseded token was not cited in this surface at the base"
479        return None
```

Two properties the predicate and the class comment assert are **not** enforced:

* **(A) "live" at base.** Line 477 only proves the token was *CITED* at base
  (`base_citelines` is `{token: set(line_no)}` of everything cited). It never proves the
  token *resolved* at base. The counter's own docstring distinguishes `superseded`
  ("token was **live** at base") from `fixed` ("token was **unresolved** at base"), and
  `fixed` enforces that distinction at line 429 (`"fixed token was not an unresolved
  citation of this surface at base"`). `superseded` enforces neither side: it accepts
  base-dead citations too, so the two classes overlap.
* **(B) "re-pointed" — anchored at the base citation line.** `fixed` binds the
  replacement to the base citation line (lines 431–442; the M15 fixture case
  `"fixed replacement cited away from the base line is bad"`). `superseded` binds the
  replacement to *the surface* only — "cited somewhere in `SCORECARD.md` at tip and
  resolves" — so any cited+resolving token in the surface can be named as the
  "replacement". There is no requirement that the replacement occupy the base citation's
  place, and no requirement that anything be re-pointed at all.

Compounding (B): at **line 646–647** a `superseded` row's token is placed in `exempt`,
which removes it from the `dropped` computation entirely:

```python
646    exempt = {(row["surface"], row["token"]) for row in rows
647              if row["class"] in ("fixed", "externalized", "superseded")}
```

So a `superseded` row simultaneously (i) declares the base citation disposed of, and
(ii) suppresses the very drop check that would otherwise notice it was disposed of.
Nothing ties the declaration to a re-point that actually happened.

### 2.2 Reproduction on the REAL lane tree (three mutants, all PASS the frozen counter)

All three mutants are commits in the seat's own clone
(`$S/lane`, branches `mutant/*`), created with the fixture identity
`git -c user.name=fx -c user.email=fx@invalid commit`. **The lane repo was never
written to** — verified: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin
cat-file -t <mutant-tip>` exits 128 (object absent) for every mutant, and the lane
`HEAD` is still `8abadfedf89f35372645b1e5d6ce4a2109186f90`.

**M-C — the pointer is DELETED, not re-pointed, and the row names an unrelated file.**
Script: `mutant_CD_superseded_anchor.sh`. Mutation: `SCORECARD.md`'s calibration row
"latest outside closure `corpus/lessons/round-53-verifier-spotcheck.md` (rejected;
re-anchored round 54)" is replaced by "latest outside closure (pointer deleted by mutant
M-C)", and the ledger's `superseded` row's evidence is re-pointed at
`.ufo/round-10/audit/stale-anchors.tsv` (cited at `SCORECARD.md:249`, resolves).

```
M-C tip 9655704080a74c6b18d66bbc76dc4a6095d28077
frozen counter exit=0 :: fixture=1 lane=1 scenarios=15/15 cited=692 unresolved=14
                         disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```

The calibration row's outside-closure pointer is gone, the live base citation
`corpus/lessons/round-52-verifier-spotcheck.md` is not re-pointed anywhere, and the
counter still says `dropped=0 met=True`. Receipt: `MC-frozen.out`.

**M-D — the row names a replacement that is cited AWAY from the base line (the M15
shape for `superseded`).** `SCORECARD.md` is untouched (the honest re-point to
round-53 stays at line 18); only the ledger row's evidence is re-pointed at
`.ufo/round-10/audit/stale-anchors.tsv` (cited at line 249, not at the base citation
line 18).

```
M-D tip aade32411d663ce57d91e80dd12c7833c8f03246
frozen counter exit=0 :: fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14
                         disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```

This is exactly the shape the `fixed` class rejects as M15. Receipt: `MD-frozen.out`.

**M-E — a `superseded` row on a base-DEAD citation.** The token
`.ufo/waves/round-999/count-c999.py` was cited at the frozen base `0b75a84c`
(`SCORECARD.md:1844`) but did **not resolve** there (it is the base's `never` row 17).
The mutant re-classifies that row `never` -> `superseded` and re-points the surface to
a resolving file.

```
M-E tip 34d7c36a4a375945a597e130efeefa4acbe3b9b9
frozen counter exit=0 :: fixture=1 lane=1 scenarios=15/15 cited=692 unresolved=13
                         disclosed=13 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```

The counter accepts a `superseded` row for a citation that was never live — a case
`fixed` explicitly refuses ("fixed token was not an unresolved citation of this surface
at base", line 429). Receipt: `ME-frozen.out`.

Supporting probes (pure function-level, no tree):
`probe_superseded_anchor.py` (three synthetic scenarios: honest re-point, unanchored
re-point, dead base citation — all three print `met=True` under the frozen
`check_row`) and `probe_superseded_live.py` (direct `check_row` call showing
`None` == accepted for a base-dead token). Receipts: `probe-superseded-anchor.txt`,
`probe-superseded-live.txt`.

### 2.3 Why this is a C2 (calibration) defect and not a style nit

The C2 predicate has two halves that the landed `superseded` class does not deliver:

1. **"a live base citation re-pointed to a cited, resolving replacement"** — neither
   "live" (A) nor "re-pointed" (B) is checked. The class currently accepts a row for a
   base-dead citation (M-E) and a row whose replacement is cited in a completely
   different place (M-D).
2. **"no citation dropped on any of the three surfaces since the base"** — a
   `superseded` row exempts its token from the drop computation (lines 646–647), so
   under M-C the live base citation `corpus/lessons/round-52-verifier-spotcheck.md` is
   *deleted outright* from the surface and the counter reports `dropped=0`.

That is exactly the failure mode the class was added to *prevent*: the prereg
`disclosure` records that the class exists because "the round-54 class vocabulary had no
row for [the round-54 re-anchor] - the base control's dropped=1 demonstrated the gap".
The class closes the gap on the *honest* tree but opens a new one: the same base
control's `dropped=1` can now be silenced by a row that names any cited+resolving file.

Note the *honest* landed row is genuinely correct — `SCORECARD.md:18` cites
`corpus/lessons/round-53-verifier-spotcheck.md` at the base citation line 18 where
`corpus/lessons/round-52-verifier-spotcheck.md` was cited at base
(`base_citelines -> {18}`), and the replacement resolves
(`git cat-file -t 9c60eae6:corpus/lessons/round-53-verifier-spotcheck.md` -> `blob`).
So the defect does not invalidate the landed measurement; it weakens the counter's
guarantee going forward.

### 2.4 Proposed fix

Full unified diff (100 lines): **`proposed-fix-round54-cited-path-check.py.diff`** in this
out dir. It is NOT applied to the lane — the counter is FROZEN and this is a finding,
per the round-55 constraints. Two parts:

**(i) `check_row`, `superseded` branch** (after line 478) — add the two missing
checks, mirroring `fixed`:

```python
        # LIVE at base: the token must have RESOLVED at the frozen base, not merely
        # been cited there. `fixed` owns the unresolved-at-base case ("fixed token
        # was not an unresolved citation of this surface at base"); a superseded row
        # that covers a base-dead citation overlaps it, so either class could be
        # used to cover the other's case.
        if base_unres is not None and tok in base_unres.get(surf, set()):
            return "superseded token was an unresolved (not live) citation of this surface at base"
        # ANCHORED at the base citation line: the re-point must have happened where
        # the base cited the token, exactly as `fixed` requires (M15: "fixed
        # replacement cited away from the base line is bad"). Without this, any
        # cited+resolving token in the surface can be named as the "replacement",
        # and a live base citation can be DELETED (not re-pointed) while the row
        # still discloses it - and a `superseded` row exempts its token from the
        # dropped computation, so the deletion stays invisible (dropped=0).
        inherited = base_rows is not None and (surf, tok) in base_rows
        if not inherited:
            lines = (base_citelines or {}).get(surf, {}).get(tok, set())
            if len(lines) != 1:
                return "superseded token needs exactly one base citation line"
            ln = next(iter(lines))
            tip_text = show(lane.path, lane.rev, surf) or ""
            tip_lines = tip_text.split("\n")
            cited = False
            if ln <= len(tip_lines):
                for _n2, t2, _c2, _l2, _h2 in citations_line(tip_lines[ln - 1]):
                    if t2 == ev or ev in t2 or t2 in ev:
                        cited = True
            if not cited:
                return f"replacement {ev!r} is not cited at the base citation line {ln}"
```

`base_unres` and `base_rows` are already parameters of `check_row` and are already
passed by `evaluate()` (lines 605–628), so the change is local to the branch.

**(ii) two new fixture scenarios** (`SCENARIOS = 15` -> `17`), so the new checks are
themselves killed:

* `M16 "superseded replacement cited away from the base line is bad"` — base cites
  `tools/live.py` at line 2, tip re-points line 2 to `tools/new.py` but the ledger names
  `tools/other.py` (cited at line 5) -> expect `not ok and bad == 1`.
* `M17 "superseded row on a base-dead citation is bad"` — base cites a path that does
  not exist at base -> expect `not ok and bad == 1`.

### 2.5 The proposed fix validated

Patched copy: `$S/fix/tools/round54-cited-path-check.py` (scratch only).

| tree | frozen counter | proposed-fix counter |
|---|---|---|
| landed `9c60eae6` | exit 0, `scenarios=15/15 met=True` | exit 0, `scenarios=17/17 cited=693 unresolved=14 disclosed=14 dropped=0 met=True` — **still green** |
| base `3a600d2f` | exit 1, `dropped=1 met=False` | exit 1, `dropped=1 met=False` — **still red, same reason** |
| M-C `96557040` | exit 0, `met=True` (defect) | exit 1, `bad=1 met=False`: `bad ledger line 46 (SCORECARD.md 'corpus/lessons/round-52-verifier-spotcheck.md' superseded): replacement '.ufo/round-10/audit/stale-anchors.tsv' is not cited at the base citation line 18` |
| M-D `aade3241` | exit 0, `met=True` (defect) | exit 1, `bad=1 met=False`: same message |
| M-E `34d7c36a` | exit 0, `met=True` (defect) | exit 1, `bad=1 met=False`: `bad ledger line 17 (...): superseded token was an unresolved (not live) citation of this surface at base` |

Receipts: `fix3-landed.out`, `fix3-base.out`, `fix3-MC.out`, `fix3-MD.out`,
`ME-fixed.out`.

So the fix is a strict improvement: it preserves the honest landed tip and the base
control exactly, and kills all three mutants.

---

## 3. Claim assessment

### C2 (`claims.C2`): calibration 7 -> 7

**The measurement is confirmed.** The frozen counter at the landed tip reproduces the
frozen build measurement byte-for-byte (cited=693, unresolved=14, disclosed=14,
undisclosed=0, bad=0, stale=0, dropped=0, met=True, exit 0), the frozen base control
reproduces byte-for-byte (dropped=1, met=False, exit 1), the verdict is stable across
9/9 repeats, and the fleet rev does not affect any counted field. The kill rule
("base control prints met=True, or the build prints met=False, or any fixture scenario
fails, or the counter bytes differ from `counter_sha256`") is **not** tripped:
`counter_sha256 d70a1729…` matches the counter at `9c60eae6` exactly, the base control
is red for the right reason (`dropped=1`, the round-52 re-anchor), and all 15 fixture
scenarios get their fixed verdicts.

**But the counter's `superseded` class is under-specified relative to the predicate it
is meant to certify** (§2). The landed row is honest, so this does not falsify C2 as
measured; it does mean the C2 instrument would not have caught the three mutants
above, and the fix + M16/M17 scenarios should land before the class is relied on again.

### C1 (`claims.C1`): operability 8 -> 8

**Out of scope for this seat** — the seat spec is "Independent C2 measurement". C1's
counter (`tools/round54-replay-code-audit.py`) was not run. No C1 claim is made or
refuted here. The two claims' separability is asserted in the prereg
(`claims`/`separability`: "C2 touches no C1 path") and nothing in this seat's work
touches a C1 path.

### Score recommendation

**calibration stays 7** (the prereg target `7 -> 7` is met for the measurement itself).
No capability enters. The `superseded`-class defect is a counter finding for the next
round, not a score movement in round 55.

---

## 4. Scope, hygiene, and negative results

* **Read-only respected.** The lane repo was never mutated: `git -C
  /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` is still
  `8abadfedf89f35372645b1e5d6ce4a2109186f90`, `git status --porcelain -- tools registry
  SCORECARD.md SHONEN.md SKILL.md` is empty, and no mutant commit object exists in the
  lane repo (`cat-file -t` -> exit 128 for all five mutant tips). No `jj` command was
  run. The fleet repo `/home/vgpnk/Projects/shokunin` and `/home/vgpnk/Projects/shokuknow`
  were read only; no campaign tool was run in `shokuknow`.
* **All outputs** are in this seat's out dir
  `.ufo/waves/round-55/w1/out/X2C2Rerun/`; nothing was written to
  `.ufo/waves/round-55/measured/`, `.ufo/waves/round-55/c1/battery/`, or any other lane
  directory. `measured/`, `controls/` and `preregistration.json` were copied into
  `receipts/` for citation and left untouched at their original paths.
* **No services started.** The C2 counter starts no server and touches no
  `llama-server`; the seat ran no server at any point. (The C1 counter does start/stop
  loopback servers; it was not run.) `pgrep -af llama-server` was checked at the start
  and the end of the seat's run: at the start it returned nothing, and at the end it
  shows two processes owned by the **peer seat `J5EnvNames`** (PIDs 3521908 / 3523374,
  under `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/`). Those are not this seat's and
  were deliberately left alone — this seat never started, stopped or restarted a
  service.
* **No tracer** wrapped any counter (`strace`/`ltrace` never used).
* **Counter never edited in place.** `sha256sum` of
  `tools/round54-cited-path-check.py` is still
  `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`; the proposed fix
  exists only as a diff and as a scratch copy.
* **No tools installed or upgraded** (no pacman, no uv tool, no npm). The environment
  already had `git`, `python3` and `patch`; nothing was needed, so the
  2026-10-19 tooling directive's recording requirement is not triggered.
* **Scratch** `/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun` removed at the end of the
  session (see §6). No `/tmp` path is used as evidence.
* **Negative results worth recording.** (i) M-A (first attempt at the delete-the-pointer
  mutant) and M-B used `tools/round41-scorecard-reconcile.py` as the wrong replacement
  and were **not** defects: that token happens to be cited at `SCORECARD.md:18`, the
  base citation line, so even a correctly anchored check accepts it. The mutants were
  rebuilt (M-C/M-D) with a replacement cited away from line 18. (ii) The first attempt
  to widen the fixture `shape` dispatch collided with the existing `superseded` branch
  and made M16/M17 self-fail (`scenarios=15/17`); the dispatch was narrowed back and
  the fixture now reports `17/17`. Both are recorded so the receipts are not mistaken
  for clean first attempts.

## 5. Reproduce

```bash
S=/fast/scratch/hyaku/kama-r55/w1/X2C2Rerun ; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
T=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-cited-path-check.py
python3 $T --repo "$S/lane" --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
  --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S"   # exit 0
python3 $T --repo "$S/lane" --tip 3a600d2f729828419aaea34cc402c8b0d20fb720 \
  --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch "$S"   # exit 1
bash mutant_CD_superseded_anchor.sh     # M-C and M-D, frozen vs fixed
bash mutant_E_superseded_deadbase.sh    # M-E, frozen vs fixed
```

## 6. Deliverables written by this seat

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X2C2Rerun.md`

Out dir `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X2C2Rerun/`:

* `proposed-fix-round54-cited-path-check.py.diff` — the proposed fix (check_row
  `superseded` anchoring + liveness, plus fixture M16/M17 and `SCENARIOS 15 -> 17`).
* `receipts/cited-measured-c2-build.out`, `receipts/cited-controls-base.c2.out`,
  `receipts/cited-preregistration.json` — copies of the receipts cited above.
* `A-*.out`, `C-*.out`, `D-*.out`, `E-*.out`, `F-*.out` — the independent measurement
  runs (landed tip, base tip, and the three fleet-rev variants).
* `rep1..rep9-tip9c60eae.out` — the nine stability repeats.
* `G-offline-stdout.txt` — the offline (could-not-evaluate, exit 2) probe.
* `xcheck_c2.py`, `xcheck-tip9c60eae.txt`, `xcheck-tip3a600d2f.txt`,
  `xcheck-base-unresolved.txt`, `xcheck-raw-drops.txt` — the independent cross-check
  driver and its outputs.
* `probe_superseded_live.py`, `probe_superseded_anchor.py`,
  `probe-superseded-live.txt`, `probe-superseded-anchor.txt` — the function-level
  probes of the `superseded` branch.
* `mutant_CD_superseded_anchor.sh`, `mutant_E_superseded_deadbase.sh`,
  `mutant-A/B/C/D/E-run.log`, `MC-frozen.out`, `MC-fixed.out`, `MD-frozen.out`,
  `MD-fixed.out`, `ME-frozen.out`, `ME-fixed.out`,
  `mutant-A-superseded-unanchored.out`, `mutant-B-superseded-wrong-replacement.out` —
  the mutant scripts and their receipts.
* `mutant_A_superseded_unanchored.sh`, `mutant_B_superseded_wrong_replacement.sh` —
  the two first-attempt mutant scripts (negative results, see §4).
* `fix3-landed.out`, `fix3-base.out`, `fix3-MC.out`, `fix3-MD.out`,
  `fix-landed.out`, `fix-base.out`, `fix-mutantA.out`, `fix-mutantB.out`,
  `fix2-*.out`, `fixcheck-*.out` — the proposed-fix validation receipts.
