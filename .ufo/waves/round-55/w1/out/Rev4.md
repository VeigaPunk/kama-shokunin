# Rev4 — the limits arc, rounds 53 → 55 (kama, round 55 w1)

**Verdict:** of the 20 disclosed limit clauses (round-53 paragraph: 12; round-55 preregistration: 8) 5 are closed by a leg that a round-55 receipt exercises, 2 are narrowed, 10 are still open and 3 are consciously permanent — but **one round-53 limit silently vanished from the round-55 limits field with no closing leg and is still open (D1: the `untracked` row's present-disk-state/no-history class and its never-read `note`), and the frozen C1 battery contradicts its own preregistration: three receipts in `.ufo/waves/round-55/c1/battery/` print `met=True`, two of them the prereg's named mutants, so the hostlibs closure is unexercised and the frozen kill rule "if any battery mutant prints met=True" fires on committed bytes (D2).**

Audited commit: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (freeze). Battery and the `w1` build commit `8abadfedf89f35372645b1e5d6ce4a2109186f90` were read for receipts. Lane working tree was never written; all runs used my own `git clone --shared` at `/fast/scratch/hyaku/kama-r55/w1/Rev4/lane`.

---

## 0. Method (commands, outputs, exit codes)

```console
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin && git rev-parse HEAD
8abadfedf89f35372645b1e5d6ce4a2109186f90
$ git show 9c60eae6:tools/round54-replay-code-audit.py > .../Rev4/tip-counter-c1.py   # sha256 c81fe971…
$ git show 9c60eae6:tools/round54-cited-path-check.py > .../Rev4/tip-counter-c2.py   # sha256 d70a1729…
$ sha256sum .../Rev4/tip-counter-c*.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  tip-counter-c1.py   # == preregistration.json:16
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  tip-counter-c2.py   # == preregistration.json:28
```

Independent C2 rerun at the freeze (my clone, my scratch), exit 0 — reproduces `measured/c2-build.out:2`:

```console
$ python3 tools/round54-cited-path-check.py --repo $S/lane --tip 9c60eae6… --scratch $S/c2base --out Rev4/rev4-c2-baseline.out
tip=9c60eae6f7ed84f7da93d219a406aadc30958c6c fleet=666bc1efcddd4b711173f23def3278cfe54a418f
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
$ echo $?   -> 0
```

Two probes on my clone (fixture identity `fx <fx@invalid>`, `git -C $S/lane rev-parse --show-toplevel` == `$S/lane` before each commit):

| probe | change (in my clone only) | result | receipt |
|---|---|---|---|
| A | the `untracked` row's note replaced by a plainly false claim (`registry/cited-path-corrections.tsv:21`) | `dropped=0 … met=True`, **exit 0** | `Rev4/rev4-probeA-false-note.out:2`, diff `Rev4/rev4-probeA.diff` |
| B | the round-53 J12Hide shape: one SKILL.md citation (`corpus/knowledge/endpoint-identity.md`) de-backticked into prose, no ledger row | `lane=0 … dropped=1 met=False`, **exit 1**, `detail: dropped citation `SKILL.md: corpus/knowledge/endpoint-identity.md`` | `Rev4/rev4-probeB-skill-hide.out:2,19`, diff `Rev4/rev4-probeB.diff` |

I did **not** run the C1 counter (it starts `llama-server`); C1 evidence is the committed receipts. No tool was installed or upgraded; no service was started or stopped.

---

## 1. Premise: SCORECARD has no round-54 text at the freeze

The assignment names "the 'What met=True does not show' paragraphs of SCORECARD rounds 53 and 54". There is exactly one such paragraph, for round 53; round 54 never filed a section, because it froze zero claims (its outside closure is `rejected-honest-stop`).

```console
$ git show 9c60eae6:SCORECARD.md | grep -n "Round 54"
16:| depth | … | evidence re-anchored round 54 |
18:| calibration | … | latest outside closure … (rejected; re-anchored round 54) …
53:Superseded in round 42. The live plan is `### Planned (round 54)` at the end of this file; …
3048:### Planned (round 54)
$ git show 9c60eae6:SCORECARD.md | grep -n "does not show" | tail -2
3013:### What `met=True` does not show (round-52 wave attacks)
3044:### What `met=True` does not show (round 53)
$ git show 9c60eae6:SCORECARD.md | wc -l        -> 3053   (file ends with round 53's §Planned (round 54))
$ find .ufo/waves/round-54 -type f | wc -l      -> 1      (.ufo/waves/round-54/sources/git-docs-git.html only)
```

So the round-54 disclosure set is the outside closure's routed-defect list, classified in §6 below. Nothing is "missing" in the sense of a deleted paragraph: round 54 owed no `met=True` paragraph.

---

## 2. Round-53 ¶ C1 — `SCORECARD.md:3046` (six clauses)

| # | clause | verdict at 9c60eae6 | leg / receipt |
|---|---|---|---|
| C1-1 | 13 root-owned host libs not byte-compared; J5Preload: arbitrary root-owned non-writable code outside the archive was accepted | **PARTIAL** — the arbitrary-basename half is closed, the byte-reference half is not; closure is code-only | `hostlibs` leg `tools/round54-replay-code-audit.py:552-565` with `HOST_LIBS` `:138`; positive receipt `measured/c1-build.out:2` (`hostlibs=3/3`); the only negative attempt is void: `c1/battery/m-ldaudit-foreign.out:2` `met=True` |
| C1-2 | a byte-identical host install is indistinguishable from an archive-derived one | **OPEN** | restated `preregistration.json:49`; counter docstring `:91-93` ("bytes, not provenance") |
| C1-3 | data/RELRO segments and the model's mapped bytes are not compared | **OPEN** | restated `preregistration.json:49`; `mapped_model` hashes a *file* (`:362-392`); only `x` maps rows are read (`:467-520`) |
| C1-4 | the download is not witnessed | **OPEN** | restated in its equivalent form (`preregistration.json:49` "byte-identical host install"); no leg observes the replay's own download — the counter downloads its own archive (`:444-460`) |
| C1-5 | a mutation after the counter's single memory read is not observed | **NARROWED** — "rewritten and left rewritten" is closed, "rewritten and restored between instants" is open | `twopass` `:708-714` + `rehash` `:780-790`; receipts `measured/c1-build.out:2` (`twopass=3/3 rehash=0`) and `c1/battery/m-member-flip.out:2` (`rehash=3 met=False`); residual restated `preregistration.json:49` |
| C1-6 | the frozen counter itself skips `/memfd:` mappings | **CLOSED** (positive receipt only) | `:508-514` admits a `/memfd:` row only when its dev/inode equal the sealed image (`own=got`, `:711`); receipt `measured/c1-build.out:2` (`code=1 sealed=1`). No receipt injects a *foreign* executable memfd, so the negative arm is unexercised |

**Why C1-1 is only partial, with a receipt:** the battery's own `m-ldpreload` plants a *root-owned library whose basename is inside the frozen set* (`/usr/lib/libzstd.so.1.5.7`, `run-battery.py:27-31`). Its receipt shows the counter does **not** object to the mapping — `c1/battery/m-ldpreload.out:2` reads `code=1 … envnames=0/3 hostlibs=3/3`: the kill comes from the environment *name*, not from the hostlibs leg. A root-owned in-set library loaded by a route that leaves no environment trace (`/etc/ld.so.preload`, a `dlopen` by the server) is therefore admitted, which is exactly the round-53 J5Preload residue.

```console
$ sed -n '2p' .ufo/waves/round-55/c1/battery/m-ldpreload.out
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=0/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False
```

---

## 3. Round-53 ¶ C2 — `SCORECARD.md:3047` (six clauses)

| # | clause | verdict | leg / receipt |
|---|---|---|---|
| C2-1 | existence/disposition instrument, not truth/reachability | **PERMANENT** | restated `preregistration.json:49`; no code path reads a claim's semantics |
| C2-2 | J12Hide changed SKILL.md citations to non-citation forms and removed their rows; all variants met | **CLOSED** | per-surface drop leg `tools/round54-cited-path-check.py:648-666`; `controls/base.c2.out` last line (a real SCORECARD drop → `dropped=1 met=False`), and my probe B re-runs the J12Hide shape on **SKILL.md** → `dropped=1 met=False` exit 1 (`Rev4/rev4-probeB-skill-hide.out`) |
| C2-3 | the `dropped` leg protected SCORECARD.md tokens only | **CLOSED** | `:651-656` loops `SURFACES = ("SCORECARD.md","SHONEN.md","SKILL.md")` (`:159`); probe B is the SKILL.md arm |
| C2-4 | J11BadFixed: upstream row can name different bytes or a mutable ref and still pass on HTTP 200 | **CLOSED** | upstream leg `:529-573` (full 40-hex ref, frozen owner/repo/revision `:543-548`, digest vs surface-stated/pinned `:553-572`); receipts `measured/c2-build.out` fixtures M10, M11, M12, M13 |
| C2-5 | the `untracked` row checks present disk/tree state, not a history-derived explanation; its original note was false and a correction comment was appended | **OPEN and UNDECLARED in round 55 → D1** | code unchanged `:574-583`; the `note` column is never read (only the fixture header `:721`); ledger row `registry/cited-path-corrections.tsv:21` still carries the false note with the erratum below it `:29-31`; probe A: false note → `met=True` exit 0 |
| C2-6 | Sen4Fixture: inherited `GIT_*` can redirect fixture git calls | **CLOSED** | `clean_env` `:198-208` used by `run_git` `:208` and by the fixture's own `git` `:678-684`; C1 gained the same helper `tools/round54-replay-code-audit.py:163-176`; sourced S510/S511. No poisoned-environment receipt is committed — the closure rests on the code and the base/build measurements having run clean |

The `externalized` class (round 54, ledger `:40`) is the lane-side escape hatch J12Hide used for its *in-place* correction: it exempts a de-backticked token from `dropped` only when the replacement text appears verbatim in the surface and the token was unresolved at base — i.e. hiding is permitted only with a row, which is disclosure, not the round-53 defect.

---

## 4. Round-55 preregistration limits — `preregistration.json:49` (eight clauses)

| # | clause | verdict | note |
|---|---|---|---|
| P-C1-a | host libraries bound by basename to the frozen 13-name set, not byte-compared | **OPEN** | same fact as C1-1's residual; correct disclosure |
| P-C1-b | a byte-identical host install remains indistinguishable | **OPEN** | same fact as C1-2 |
| P-C1-c | the model's mapped bytes and data segments are not compared | **OPEN** | same fact as C1-3 |
| P-C1-d | sampling: a library rewritten and restored between the two passes and the post-exit re-hash is not observed | **OPEN** | same fact as C1-5's residual; correctly narrowed wording |
| P-C1-e | the anon leg's non-root isolation is covered by design and receipts, not by a same-uid mutant | **OPEN** | correct, and stronger than stated: **no committed round-55 receipt carries `anon>0`** — `git grep -n "anon=[1-9]" 8abadfed -- .ufo/waves/round-55/` → rc 1 (no match), and the battery's mutant list (`run-battery.py:26,38,57,69`) has no anon arm, so the leg has no receipt at all |
| P-C2-a | not a truth or reachability checker | **PERMANENT** | by construction |
| P-C2-b | upstream rows validate bytes at the frozen commit, not the semantic content of the citing claim | **PERMANENT** | no path-resolution instrument can decide whether a claim is true |
| P-C2-c | prose-shaped root tokens are advisory only | **OPEN, consciously accepted** | advisory detail only (`:236-238`, `:587-600`); receipts `measured/c2-build.out` last four `detail: advisory:` lines |

---

## 5. Defects

### D1 (medium) — the round-53 `untracked`/note limit silently disappeared from the round-55 disclosure and is still open

* Where it was stated: `SCORECARD.md:3047` — *"The `untracked` row checks present disk/tree state, not a history-derived explanation; its original note was false and a correction comment was appended."*
* Where it is absent: `preregistration.json:49` (the round-55 `limits` string names none of it), and the frozen counter's docstring has no limits section at all.
* Why it is still open: `tools/round54-cited-path-check.py:574-583` accepts `evidence = "-"` plus "the path exists on disk under `--fleet`"; nothing re-derives history, and `note` is never read.
* Showing command + output (exit 0 = the defect):

```console
$ python3 tools/round54-cited-path-check.py --repo $S/lane --tip 5e179b18… --scratch $S/c2probeA --out Rev4/rev4-probeA-false-note.out
tip=5e179b186ee2e50e70b204efaf1d77a45e369176 …
fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True     # exit 0
```

  (probe A replaced the watchdog row's note with a plainly false sentence; `git -C /home/vgpnk/Projects/shokunin log --oneline -3 -- .ufo/watchdog.log` → `7930399e hyaku: … untrack driver runtime (… watchdog.log) …`, i.e. the note "never committed" is false.)
* Proposed fix: `Rev4/proposed-fixes.diff` — make `untracked` evidence the full fleet commit that last held the path (`git log --all -- <path>`), treat `-` as false when history holds the path (the watchdog row would become `7930399e`), and add the sentence to the round-56 `limits` string (the diff's header carries the exact wording).

### D2 (high) — the frozen C1 battery contradicts the frozen target and kill rule

* The frozen text:
  - `preregistration.json:19` target: *"kill battery: each named mutant receipt prints met=False (exit 1) with its named leg failing"*;
  - `preregistration.json:20` kill rule: *"the claim is falsified if … if any battery mutant prints met=True"*;
  - `preregistration.json:44` mutants: `m-ldpreload (envnames leg)`, `m-ldaudit-writable (code leg)`, `m-ldaudit-foreign (hostlibs leg)`, `m-member-flip (rehash leg)`.
* What the committed battery prints (`sed -n '2p'` of each receipt):

| receipt | line 2 (excerpt) | met |
|---|---|---|
| `c1/battery/control.out` | `bind=1 sealed=1 code=1 … newrow=1 … met=True` | True (positive control, expected) |
| `c1/battery/m-ldpreload.out` | `… envnames=0/3 hostlibs=3/3 … met=False` | False (kill, envnames) |
| `c1/battery/m-text-flip.out` | `bind=0 … code=0 … rehash=3 met=False` | False (kill, code) |
| `c1/battery/m-member-flip.out` | `… rehash=3 met=False` | False (kill, rehash) |
| `c1/battery/m-ldaudit-writable.out` | `… hostlibs=3/3 … met=True` | **True** — the prereg's named **code-leg** mutant |
| `c1/battery/m-ldaudit-foreign.out` | `… hostlibs=3/3 anon=0 … met=True` | **True** — the prereg's named **hostlibs** mutant |
| `c1/battery/m-extra-in-tree.out` | `… met=True` | **True** (probe, not in the prereg) |

* The driver reclassifies only after the freeze: `run-battery.py:57-63` gives `m-ldaudit-foreign` `kind = "vector"` with the comment *"not reproducible as a non-root mutant … Recorded as a vector analysis, not a live kill"*, and `main()` scores a vector as ok when it prints `met=True`. The preregistration was never amended (`git log --oneline -- .ufo/waves/round-55/preregistration.json` → the single freeze commit `9c60eae6`; no `*amend*` file under the wave dir). The redefinition exists only in the driver's `vector` kind and in the w1 commit message ("kill battery green (3 live kills + 1 vector analysis)", `8abadfed`), neither of which the frozen kill rule reads.
* Consequence for this seat's question: the **hostlibs closure has no negative receipt**, so C1-1's J5Preload half is code-only; and on the frozen wording the kill rule fires. A non-root seat cannot do better: planting a root-owned foreign library requires root (the driver says so), and the LD_AUDIT route is void on this glibc (`m-ldaudit-foreign.out` envnames b1..b3 record 6 names — `LD_AUDIT` present — while every code leg passes).
* Proposed fix: (i) record the disposition in the round-55 measured paragraph / lesson (three green receipts named, the vector's root-gating stated, `m-extra-in-tree` and `m-ldaudit-writable` named as probes), and (ii) the round-56 controls wording in `Rev4/proposed-fixes.diff` header, which separates `kill` from `vector`. A reachable hostlibs arm would need a unit-level fixture (feed a synthetic maps row to `code_observe`) rather than a live root plant.

### D3 (medium) — two battery receipts cannot be regenerated by the committed driver

`run-battery.py` defines exactly four mutants (`:26` `m-ldpreload`, `:38` `m-text-flip`, `:57` `m-ldaudit-foreign`, `:69` `m-member-flip`). `m-ldaudit-writable.out` and `m-extra-in-tree.out` are therefore orphan receipts: their `tip=` commits (`23dc15da…`, `312530a9…`) are fixture commits in a scratch clone that the committed driver does not build. Exact fix: commit the driver variant that produced them, or drop the receipts and cite the vector analysis in prose.

### D4 (low) — the ledger header's class list is stale

`registry/cited-path-corrections.tsv:4-6` still names `tools/round53-cited-path-check.py` and lists seven classes; `externalized` (round 54) and `superseded` (round 55, row at `:45-46`) appear only in dated comments. The counter itself accepts nine (`CLASSES`, `tools/round54-cited-path-check.py:167`). Fix: `Rev4/proposed-fixes.diff` first hunk.

### D5 (low, checklist) — round-54 routed defects 1 and 5 had not landed at either audited commit

```console
$ git ls-tree 9c60eae6 .ufo/waves/round-55/census/     -> only start.out (no end.out)
$ git show 9c60eae6:LOG.md | grep -c "round 55\|round-55"  -> 0
```

Routed defect 1's other half landed (lesson `corpus/lessons/round-55.md` exists; S510 re-pointed), so this is the census receipt and the LOG entry, not a limits question.

### O1 (observation, unfiled limit) — the C2 surface includes the fleet tree at a *moving* HEAD

`tools/round54-cited-path-check.py:823` defaults `--fleet-rev` to `HEAD`, and the counting command in the prereg passes no `--fleet-rev`. `measured/c2-build.out:1` records `fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b`; my rerun records `fleet=666bc1efcddd4b711173f23def3278cfe54a418f` — the fleet moved and both meet. A fleet commit can thus change the verdict without any lane change. This limit was never disclosed in rounds 53–55.

---

## 6. Round-54's disclosures that do exist (outside closure routed defects)

Source: `corpus/lessons/round-54-verifier-spotcheck.md` §"Routed defects / next-round items".

| routed item | status at `9c60eae6` / `8abadfed` |
|---|---|
| 1 write the round-54 lesson (or successor), re-point S510's used-by so the census exits 0 | lesson + re-point **landed**; census **end** receipt absent (D5) |
| 2 commit receipts for the X5 sabotage re-verification and the C2 14/14 smoke | **not committed** (`git ls-files .ufo/waves/round-55/w1/out/X5ReplaySelftest` → 0); the C2 half is superseded by `measured/c2-build.out` (15/15) |
| 3 freeze C1/C2 before data with base/do-nothing controls | **landed** — `preregistration.json`, `controls/base.c{1,2}.out` (C1 `newrow=0 met=False`, C2 `dropped=1 met=False`) |
| 4 run the C1 end-to-end measurement and build the kill battery | **landed** — `measured/c1-build.out`, `c1/battery/` (with D2/D3 caveats) |
| 5 LOG.md round-55 entry | **absent** at both audited commits |
| 6 operator ruling `ed135b3c` | operator-owned, untouched |

---

## 7. Direct answer: what silently disappeared

* **Silently dropped, no closing leg:** the round-53 `untracked`/note limit (C2-5, `SCORECARD.md:3047`) — absent from `preregistration.json:49`, unchanged in code, and demonstrably still live (probe A). **D1.**
* **Dropped as a wording, kept as a requirement:** the round-53 §Planned (round 54) promise to keep the *ptrace-scope* limit explicit — `preregistration.json:49` does not mention it; it survives only as a requirement line in the counter docstring (`tools/round54-replay-code-audit.py:99-101`) and fails closed (unreadable `/proc` → `code=0` → `met=False`). Low severity, but it is a third silent omission.
* **Not a disappearance:** the absent round-54 SCORECARD paragraph (§1) — round 54 froze no claim, so none was owed; its disclosures live in the outside closure.
* **All other round-53 clauses** are either closed with a leg + receipt, narrowed with the residue restated, or restated verbatim in the round-55 `limits` field.

---

## 8. Files written (all absolute)

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/limits-classification.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/proposed-fixes.diff`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/rev4-c2-baseline.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/rev4-probeA-false-note.out`, `rev4-probeA.diff`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/rev4-probeB-skill-hide.out`, `rev4-probeB.diff`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev4/tip-counter-c1.py`, `tip-counter-c2.py` (byte copies of the frozen counters; sha256 in §0)
