# X9Separation — round-55 causal-separability measurement (lane kama)

**Verdict: the two round-55 claims are causally separable at the two named surfaces — reverting only the superseded ledger row leaves C1 green and turns C2 red (dropped=1); removing only the S511 source row turns C1 red (newrow=0) and leaves C2 green. All four expected receipts confirmed. One secondary finding (F1) below: the separability is *row-level*, not *file-level* — the shared file `corpus/SOURCES.md` is a coupling channel, so the preregistration's separability paragraph is true as stated for the two named rows but over-general if read as "the claims share no file".**

---

## 1. Setup (read-only lane, private clone)

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` was never written to (git status shows only untracked files produced by other seats; `git log --oneline -1` = `8abadfed`, unchanged by me). All measurements ran against a private clone:

```
S=/fast/scratch/hyaku/kama-r55/w1/X9Separation
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane rev-parse --show-toplevel   # -> /fast/scratch/hyaku/kama-r55/w1/X9Separation/lane
```

Branches, all forked from the landed tip `9c60eae6f7ed84f7da93d219a406aadc30958c6c`, each with a single scoped commit (fixture identity `fx <fx@invalid>`, `--show-toplevel` asserted before each commit):

| branch | commit | single change | diff |
|---|---|---|---|
| `mutA` | `2bf9d344caa6d0575ce0e114ebcef1f770896b9b` | revert ONLY the round-55 `superseded` ledger row (+ its 5 comment lines) | `mutA.diff` (14 lines) |
| `mutB` | `567451d4730fd6a7196449e73b8d3a63dce34d9d` | remove ONLY the `\| S511 \|` row from `corpus/SOURCES.md` | `mutB.diff` (12 lines) |
| `mutC` | `b84da95b8c97b5e2407beed32eb47e13cbf69d3d` | *probe*: insert one synthetic row above the `corpus/SOURCES.md:225` anchor | `mutC.diff` |
| `mutD` | `3577a8f80e8650947e0bb1ef2276f96dc56be4c3` | *probe*: truncate `corpus/SOURCES.md` to 224 lines (below the anchor) | `mutD.diff` |
| `mutE` | `e1cc72cba1deded163e2fe5bbf03d932582514c4` | *probe*: swap S511 for a *different* new row quoting the same URL | `mutE.diff` |

`mutA` was produced by exactly the operation the seat spec names (`git show <base>:registry/cited-path-corrections.tsv > …`), with one correction to the spec's literal path: the spec's absolute path form
`git show 3a600d2f…:/home/vgpnk/Projects/shokunin/kama-shokunin/registry/cited-path-corrections.tsv` is **not a valid git pathspec** and exits 128 (`fatal: path '…' does not exist in '…'`). The repo-relative form `git show 3a600d2f…:registry/cited-path-corrections.tsv` was used instead; it yields the same file (41 lines vs 46 at tip) and is the form that works in any clone.

Counter bytes at measurement (kill rule for both claims) — unchanged, and identical in the clone at every branch:

```
$ sha256sum tools/round54-replay-code-audit.py tools/round54-cited-path-check.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  tools/round54-replay-code-audit.py
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  tools/round54-cited-path-check.py
```
These match `counter_sha256` in `.ufo/waves/round-55/preregistration.json` (C1 `c81fe971…`, C2 `d70a1729…`). The same blobs are what the clone holds at `mutA`/`mutB` (`git show <branch>:tools/…| sha256sum` → identical), so no counter was edited between the freeze and the measurement.

Fleet revision: the fleet repo moved after the frozen receipts were taken (frozen receipts record `fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b`; fleet HEAD at my run time is `666bc1efcddd4b711173f23def3278cfe54a418f`). I therefore re-ran **both** mutant C2 measurements with `--fleet-rev 6c4aba34…` pinned: the verdicts are unchanged (`mutA-c2-fleetpinned.out` exit 1 / dropped=1; `mutB-c2-fleetpinned.out` exit 0 / dropped=0), so the fleet move does not drive any result below.

---

## 2. The four required receipts

Commands (from `$S/lane`, `TMPDIR=$S`):

```
python3 …/tools/round54-cited-path-check.py  --repo $S/lane --tip <tip> --scratch $S/c2-<tag> --out <out>
python3 …/tools/round54-replay-code-audit.py --repo $S/lane --tip <tip> --scratch $S/c1-<tag> --out <out>
```

### (a) mutA — revert ONLY the superseded ledger row (`2bf9d344`)

| counter | exit | summary line | receipt |
|---|---|---|---|
| C1 `round54-replay-code-audit.py` | **0** (green) | `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 … rehash=0 met=True` | `out/X9Separation/a-c1.out` |
| C2 `round54-cited-path-check.py` | **1** (red) | `fixture=1 lane=0 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=1 met=False` | `out/X9Separation/a-c2.out` |

C1's newrow leg still fires — `detail: newrow: 2 rows new since base; 1 name the git environment doc: ['| S511 |']` (`a-c1.out:24`) — i.e. the ledger revert is invisible to C1, as the preregistration's separability paragraph predicts.

C2's red is exactly the predicted drop, and names the same token as the base control:

```
a-c2.out:22  detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)
```
(byte-identical to the corresponding line of the frozen base control `lane-base.c2.out:22`.) Mechanism, in the counter: `registry/cited-path-corrections.tsv` line 46 is the only row of class `superseded`; the counter's drop leg exempts a base citation only when a ledger row of class `fixed`/`externalized`/`superseded` covers it (`tools/round54-cited-path-check.py:646-647`), so removing the row puts `corpus/lessons/round-52-verifier-spotcheck.md` back into `bset - tset` (`:653-656`). The row is *not* reported as `bad` — C2's `superseded` branch (`:461-479`) is never entered, so the row's absence is a **drop**, exactly as in the base control, not a malformed-row failure.

### (b) mutB — remove ONLY the S511 source row (`567451d4`)

| counter | exit | summary line | receipt |
|---|---|---|---|
| C2 `round54-cited-path-check.py` | **0** (green) | `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` | `out/X9Separation/b-c2.out` |
| C1 `round54-replay-code-audit.py` | **1** (red) | `bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 … rehash=0 met=False` | `out/X9Separation/b-c1.out` |

C1's only failing leg is `newrow`:

```
b-c1.out:2   bind=1 sealed=1 code=1 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False
b-c1.out:24  detail: newrow: 1 rows new since base; 0 name the git environment doc: []
```
The one remaining "new since base" row is S510 (re-pointed old→new in this round, hence textually new relative to the round-54 tip) — it does not name the git-config doc, so the leg is false. Mechanism: `tools/round54-replay-code-audit.py:863-873` — `rows(tip) - rows(BASE)` then `hit = [ln for ln in new if GITDOC_URL in ln]` with `GITDOC_URL = "git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT"` (`:129`), `BASE = 3a600d2f…` (`:130`).

C2 stays fully green under mutB: `corpus/SOURCES.md` is not a C2 surface (`grep -n "SOURCES" tools/round54-cited-path-check.py` → no match), so removing a SOURCES row cannot move any C2 leg. Its `unresolved=14 disclosed=14` counts are identical to the landed measurement.

### Positive controls (same clone, same counters)

| tip | C1 | C2 |
|---|---|---|
| `9c60eae6` (landed tip) | exit 0, `met=True`, `newrow=1` (`pc-c1.out`) | exit 0, `met=True`, `dropped=0` (`pc-c2.out`) |
| `3a600d2f` (base tip) | — | exit 1, `dropped=1`, `met=False` (`lane-base.c2.out` from the lane; reproduced in-clone as `base-c2.out`) |

The in-clone positive control reproduces the lane's frozen build measurement `measured/c1-build.out` / `measured/c2-build.out` byte-for-byte on the summary line, so the four receipts below are attributable to the two commits and not to the clone or the environment.

### Summary matrix

| tip | C1 | C2 |
|---|---|---|
| base `3a600d2f` | exit 1, `newrow=0`, red | exit 1, `dropped=1`, red |
| landed `9c60eae6` | exit 0, `newrow=1`, green | exit 0, `dropped=0`, green |
| **mutA** `2bf9d344` (ledger row reverted) | **exit 0, green** ← C1 blind to ledger | **exit 1, `dropped=1`, red** |
| **mutB** `567451d4` (S511 row removed) | **exit 1, `newrow=0`, red** | **exit 0, green** ← C2 blind to SOURCES |

All four predictions in the seat spec and in the preregistration's separability paragraph ("Either claim can be measured with the other reverted") hold exactly. No kill rule is triggered by any of these measurements: the base controls are red, the build measurements are green, the counter bytes are unchanged, and none of these mutants is a battery member.

---

## 3. Supplementary probes (beyond the assigned four) — a narrower finding

The preregistration's separability paragraph asserts: *"C1 touches tools/round54-replay-code-audit.py and corpus/SOURCES.md (S511, required by its newrow leg) … C2 touches tools/round54-cited-path-check.py and registry/cited-path-corrections.tsv (the superseded row) … C1's SOURCES row is not a C2 surface; C2 touches no C1 path."*

Read strictly ("C2 touches no C1 path"), that is **not** true, and I can show the counterfactual:

* **mutC** (`b84da95b`, one synthetic row inserted *above* the `corpus/SOURCES.md:225` anchor): C2 exit 0, `met=True`. Inserting a row shifts the anchor's target content — at tip line 225 is the `S472` row, at mutC line 225 is `S353` and `S472` moves to 226 — yet C2 is green. C2 resolves the `corpus/SOURCES.md:225` anchor only by *line count* (`tools/round54-cited-path-check.py:378-380`, `nlines >= max(lo,hi)`), never by the anchor's content, so a shifted anchor is invisible to it. C1 is unaffected (`newrow=1`, exit 0).
* **mutD** (`3577a8f8`, `corpus/SOURCES.md` truncated to 224 lines): C2 exit 1, `undisclosed=1`, `met=False`, with
  `detail: undisclosed SCORECARD.md \`corpus/SOURCES.md:225\`: [('corpus/SOURCES.md', 'beyond-eof')]` (`mutD-c2.out:22`).
  So C2 **does** read `corpus/SOURCES.md` — through the *cited path* `corpus/SOURCES.md:225` that SCORECARD.md:2173 cites — and it fails when that file shrinks below the cited line. C1 is also red here (`newrow=0`), but for its own independent reason (S511 is inside the truncated region).

So `corpus/SOURCES.md` is a **shared file** between the two counters: C1 reaches it by *row* (the newrow leg), C2 reaches it by *line-count anchor* (the SCORECARD.md:2173 citation). The preregistration's row-level claim is exact; its file-level phrasing is not. This does not falsify either claim today (S511 sits at `corpus/SOURCES.md:264`, well below the `:225` anchor, and the anchor's content is not checked), but it is a real coupling channel for any future change to that file's length above line 225.

**Proposed wording fix** (to the preregistration's `separability` field; not applied — preregistration is frozen):

```diff
- C1's SOURCES row is not a C2 surface; C2 touches no C1 path. Either claim can be measured with the other reverted.
+ C1's SOURCES row is not a C2 surface. C2 reads no C1 *row*, but it does read the
+ C1 file corpus/SOURCES.md by line count: SCORECARD.md:2173 cites corpus/SOURCES.md:225
+ and C2 resolves that anchor by requiring the file to have at least 225 lines
+ (tools/round54-cited-path-check.py:378-380), not by checking the cited line's content.
+ So the two claims are separable at the level of the two named rows - either claim can
+ be measured with the other row reverted - but a change to corpus/SOURCES.md that drops
+ it below line 225 moves both counters (C2 as undisclosed/beyond-eof, C1 through its own
+ newrow leg).
```

**mutE** (`e1cc72cb`): replacing the S511 row with a *different* new row (`S512`) that merely quotes the same git-config URL keeps C1 green (`newrow=1`, `detail: newrow: 2 rows new since base; 1 name the git environment doc: ['| S512 |']`) and keeps C2 green. The newrow leg is therefore a **URL-presence** test, not an S511-identity test — it checks that *some* row new since the base names `GITDOC_URL`, not that the row is S511. This is consistent with the preregistration's predicate wording ("the newrow source row re-pointed at S511") but it is a weaker check than the S511-specific phrasing implies: a round could satisfy the leg with a copy row and drop the real source row, and C1 would stay green. Worth stating explicitly in the C1 predicate/limits text, not a defect in the round-55 measurement (S511 does exist and is what the landed tree carries).

---

## 4. Findings

**F1 — preregistration separability paragraph overstates file-level independence (minor, non-falsifying).**
Exact text: `.ufo/waves/round-55/preregistration.json`, field `separability`, last sentence: *"C1's SOURCES row is not a C2 surface; C2 touches no C1 path."*
Counter-source that shows the coupling: `tools/round54-cited-path-check.py:378-380` (anchor resolution by `nlines`), reached from `SCORECARD.md:2173` (`corpus/SOURCES.md:225`).
Command that shows it:
```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
# truncating corpus/SOURCES.md to 224 lines and re-running the frozen C2 counter:
python3 tools/round54-cited-path-check.py --repo $S/lane --tip 3577a8f8… --scratch $S/c2d
# -> exit 1, undisclosed=1, met=False
#    detail: undisclosed SCORECARD.md `corpus/SOURCES.md:225`: [('corpus/SOURCES.md', 'beyond-eof')]
```
Receipt `out/X9Separation/mutD-c2.out`. Fix: the wording patch in §3. No change to either frozen counter is warranted — the counter is behaving as an existence/disposition instrument by design, as the preregistration's own `limits` field states ("the counter is an existence/disposition instrument, not a truth or reachability checker").

**F2 — C1's newrow leg is a URL-presence test, not an S511-identity test (disclosure gap, non-falsifying).**
`tools/round54-replay-code-audit.py:871` — `hit = [ln for ln in new if GITDOC_URL in ln]`; no row-id check. Shown by `mutE` (`out/X9Separation/mutE-c1.out`, exit 0, `newrow=1` with `['| S512 |']`). Fix: add the row id to the predicate, or state the weaker check in the preregistration's C1 `predicate`/`limits`. Not applied (frozen).

**F3 — the seat spec's literal `git show` path form is invalid (spec defect, worked around).**
`git show 3a600d2f…:/home/vgpnk/Projects/shokunin/kama-shokunin/registry/cited-path-corrections.tsv` → exit 128, `fatal: path '/home/vgpnk/Projects/shokunin/kama-shokunin/registry/cited-path-corrections.tsv' does not exist in '3a600d2f…'`. Git pathspecs are relative to the repo root; the repo-relative form was used. No lane file involved; a spec-text fix only.

**No falsification.** Neither kill rule is tripped: base/do-nothing controls red (C1 `newrow=0`, C2 `dropped=1`), build measurements green at the landed tip, no battery mutant green, all 15 C2 fixture scenarios pass in every measurement, and both counters' bytes match `counter_sha256`.

---

## 5. Artifacts and hygiene

Receipts, diffs and mutant log (all under `…/kama-shokunin/.ufo/waves/round-55/w1/out/X9Separation/`):

`a-c1.out` `a-c2.out` `b-c1.out` `b-c2.out` `pc-c1.out` `pc-c2.out` `base-c2.out` `mutC-c1.out` `mutC-c2.out` `mutD-c1.out` `mutD-c2.out` `mutE-c1.out` `mutE-c2.out` `mutA-c2-fleetpinned.out` `mutB-c2-fleetpinned.out` `mutA.diff` `mutB.diff` `mutC.diff` `mutD.diff` `mutE.diff` `mutants.txt` `lane-base.c1.out` `lane-base.c2.out` `lane-c1-build.out` `lane-c2-build.out` (+ `.stdout`/`.stderr` twins for each run; all stderr files are 0 bytes).

Scratch `$S` was removed after the measurement; the lane and the fleet repo were never written to. No `llama-server` process from my scratch survives (`pgrep -af llama-server | grep X9Separation` → none; the only live llama-server at teardown belonged to another seat's scratch, `w1/J5EnvNames`, and was left alone). No tool was installed or upgraded for this seat, so nothing to record under the tooling directive.
