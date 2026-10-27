# S7Pointers — round-55 evidence-pointer sweep (seat S7Pointers)

Verdict: every path cited in `corpus/lessons/round-55.md` and `.ufo/waves/round-55/preregistration.json` resolves at landed tip `9c60eae6f7ed84f7da93d219a406aadc30958c6c` except two wave-artifact pointers — `.ufo/waves/round-55/c1/battery/` (on disk, committed later at `8abadfed`, reconstructable via its committed `run-battery.py`) and `.ufo/waves/round-55/census/end.out` (still pending; reconstruction command documented below) — plus one by-design non-existent path (`corpus/lessons/round-54.md`, the recorded E11 dangling used-by); the battery receipts cited for C1 show one real defect: the frozen preregistration's named-mutant list diverges from the landed battery (code-leg kill renamed m-ldaudit-writable → m-text-flip, undisclosed) and two stale `met=True` receipts sit in the committed evidence dir under a kill rule reading "any battery mutant prints met=True".

## Method

- Read-only shared clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` ($S=/fast/scratch/hyaku/kama-r55/w1/S7Pointers); every git check names `-C $S/lane`. No mutation of the lane; no fixture commit needed (no counter runs — pure pointer sweep).
- For each cited path: `git -C $S/lane cat-file -e TIP:<path>` (TIP=9c60eae6f7ed84f7da93d219a406aadc30958c6c) plus an on-disk `[ -e ]` check against the live lane.
- Receipts cited were copied to `.ufo/waves/round-55/w1/out/S7Pointers/receipts/` per the scratch directive; scratch was removed after the sweep.

## Citation sweep (28 pointers)

Full table with per-row commands: `out/S7Pointers/citations.tsv`. Summary:

**Exists in the TIP tree (25):** `corpus/lessons/round-54-verifier-spotcheck.md` (lesson:4); `tools/round54-replay-code-audit.py` (lesson:14) — sha256 at TIP = `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`, matches `preregistration.json` claims.C1.counter_sha256; `.ufo/waves/round-55/preregistration.json` (lesson:17); `tools/round54-cited-path-check.py` (lesson:20) — sha256 at TIP = `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`, matches claims.C2.counter_sha256; `.ufo/waves/round-55/sources/git-docs-git-config.html` (lesson:34) — 830,605 bytes at TIP, lesson's located quote verified at HTML lines 5850–5852; `corpus/lessons/round-55.md` (self); `.ufo/waves/round-53` (lesson:62 — J12Hide receipts under `.ufo/waves/round-53/w1/out/J12Hide/`); `corpus/lessons/round-53-verifier-spotcheck.md` (lesson:63 — its line 17 C2 row names J12Hide `met=True`, matching the lesson's quote); `.ufo/waves/round-55/census/start.out` (lesson:100 — its line 101 `kama E11 S510 missing used-by corpus/lessons/round-54.md`, plus W01×1 and W04 rows, matching lesson text); host-absolute `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (lesson:100); `considerthese/2026-10-26.md` (lesson:105 — proposal 2 at its line 31); `corpus/QUALITY.md` (lesson:106 — KQ97 at line 477, citing the same proposal); `tools/pin-watch.py` (lesson:112); `SCORECARD.md` (lesson:65, prereg:9,30); `corpus/SOURCES.md` (prereg:9 — S510 row 263 and S511 row 264, both with used-by cell = `corpus/lessons/round-55.md`, matching the "S510 used-by re-pointed old→new" claim); `registry/cited-path-corrections.tsv` (prereg:9 — superseded row at line 46: `SCORECARD.md → corpus/lessons/round-52-verifier-spotcheck.md superseded → corpus/lessons/round-53-verifier-spotcheck.md`); `SHONEN.md`, `SKILL.md` (prereg:30); `.ufo/waves/round-55/controls/base.c1.out` (prereg:40 — content `newrow=0 … met=False`, matching expected "C1: exit 1, newrow=0, met=False"); `.ufo/waves/round-55/controls/base.c2.out` (prereg:40 — content `fixture=1 lane=0 scenarios=15/15 … dropped=1 met=False`, matching "C2: exit 1, dropped=1, met=False"); `.ufo/waves/round-48/c2/live/receipt-1.json`, `receipt-2.json`, `receipt-3.json` (prereg:9 "three committed round-48 v5 receipts"); cited commits `3a600d2f729828419aaea34cc402c8b0d20fb720` (prereg:7,38 base), `0b75a84c56e024cac1662e8ff81802f249acb410` (prereg:28 C2 counter_base), `9a3104c771509df2dad6b6fe13c023bd3c472c35` (prereg:10 round-54 draft) — all `git cat-file -t` = commit; fleet-root `shokunin.conf` (prereg:8 — line 52 `kama|kama-shokunin|operability + calibration`, matching the authority claim); fleet-root `MANIFEST.json` (prereg:8 cites "MANIFEST rounds[812]" — exists; name cited loosely without `.json`, the only manifest at fleet root — minor looseness, not a defect).

**Missing by design (1):** `corpus/lessons/round-54.md` (lesson:53,90,100) — `git log --all -- corpus/lessons/round-54.md` is empty: never existed in any commit. The citation records the OLD dangling S510 used-by value (the E11 defect the round fixes); census start.out names exactly this path. Not a scratch path — a deliberate non-existence record.

**Not in the TIP tree — wave artifacts (2):**
- `.ufo/waves/round-55/c1/battery/` (lesson:73, prereg:45) — `cat-file -e TIP:<dir>` fails; on disk it exists and it is committed at `8abadfed` (the w1 follow-up commit). Label: wave artifact, reconstruction-documented — `python3 .ufo/waves/round-55/c1/battery/run-battery.py` (its committed docstring: "Run: python3 .ufo/waves/round-55/c1/battery/run-battery.py; receipts land beside this file; scratch /fast/scratch/hyaku/kama-r55/c1/battery removed on exit").
- `.ufo/waves/round-55/census/end.out` (lesson:95,101) — absent from the TIP tree, from `8abadfed`, and from disk. The lesson cites it as the required round-end receipt ("ends with census exit 0"). Still pending at sweep time. Reconstruction: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/census/end.out 2>&1` (round must not close without it; flagged so the gap is not lost).

## Battery receipts vs citations

`out/S7Pointers/battery-map.txt` has the per-file map. The lesson cites the battery directory only (lesson:73); the preregistration names four mutants (line 44: `m-ldpreload (envnames leg)`, `m-ldaudit-writable (code leg)`, `m-ldaudit-foreign (hostlibs leg)`, `m-member-flip (rehash leg)`) and a blanket target sentence (claims.C1.target): "each named mutant receipt prints met=False (exit 1) with its named leg failing". Actual committed dir (8 files, verified `git ls-tree -r 8abadfed`):

| file | named in prereg | committed run-battery.py MUTANTS | verdict |
|---|---|---|---|
| control.out | target sentence | positive control | met=True at tip=9c60eae6 — OK |
| m-ldpreload.out | yes (envnames) | kill | met=False, envnames=0/3 — named leg fails, OK |
| m-member-flip.out | yes (rehash) | kill | met=False, rehash=3 — named leg fails, OK |
| m-ldaudit-foreign.out | yes (hostlibs) | vector ("expect met=True … void on this glibc") | met=True — consistent with the assignment's "vector analysis" and run-battery.py lines 57–60; in tension with the prereg's blanket "each named mutant prints met=False" |
| m-ldaudit-writable.out | yes (code leg) | NO — stale (fixture tip 23dc15da, mtime 10:30, first composition) | **met=True** |
| m-text-flip.out | NO | kill (code leg) | met=False, code=0/3 — landed code-leg kill, unnamed in lesson and prereg |
| m-extra-in-tree.out | NO | NO — stale (fixture tip 312530a9, mtime 10:37) | **met=True** |
| run-battery.py | — | driver | MUTANTS = {m-ldpreload, m-text-flip, m-ldaudit-foreign(vector), m-member-flip} |

## Defect

Exact location: `.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out:2` (`met=True` at a prereg-named kill mutant) and `.ufo/waves/round-55/c1/battery/m-extra-in-tree.out:2` (`met=True`, named nowhere); root cause at the freeze boundary: `preregistration.json:44` (named-mutant list) vs the landed `run-battery.py` MUTANTS dict — the code-leg mutant was swapped m-ldaudit-writable → m-text-flip between freeze and landing with no disclosure (contrast the C2 BASE revert, which the lesson and preregistration disclose).

Command that shows it: `grep -m1 '^bind=' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/c1/battery/*.out` — prints `met=True` for `m-ldaudit-writable.out` and `m-extra-in-tree.out` beside the dir's kill receipts; and `python3 -c "import json; d=json.load(open('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/preregistration.json')); print(d['controls']['c1_kill_battery']['mutants'])"` — prints the four frozen names including `m-ldaudit-writable (code leg)`.

Why it matters: the frozen kill rule (`preregistration.json` claims.C1.kill_rule) says "the claim is falsified if … any battery mutant prints met=True". Two receipts in the committed evidence dir print met=True; one is a frozen-named mutant. A literal scorer falsifies C1 on the lane's own evidence. The w1 commit message ("kill battery green (3 live kills + 1 vector analysis)") and the assignment text show the landed intent (3 kills + 1 vector), so this is a documentation/disclosure and evidence-hygiene defect, not an indication the counter mis-measures — but as frozen, the preregistration and the evidence dir contradict each other.

Proposed fix: `out/S7Pointers/proposed-fix.patch` — (1) a Mistakes disclosure row in `corpus/lessons/round-55.md` naming the m-ldaudit-writable → m-text-flip swap (per KQ26, named not erased) and reconciling the vector receipt with the kill-rule sentence; (2) move the two first-composition receipts to `.ufo/waves/round-55/c1/battery/first-composition/` with a README (shell sketch included). Not applied — counters, preregistration and controls are frozen; lane files were not edited.

## Secondary observations (not defects)

- `census/end.out` dangles until the round closes (reconstruction above); the round must produce it or the lesson's "After" row stays unevidenced.
- `MANIFEST` cited without `.json` — resolves uniquely to fleet-root `MANIFEST.json`; cosmetic.
- `__pycache__/` exists on disk inside the battery dir (uncommitted, gitignored) — not a citation target; noted for hygiene only.

## Written paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/S7Pointers.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/S7Pointers/citations.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/S7Pointers/battery-map.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/S7Pointers/proposed-fix.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/S7Pointers/receipts/` (copies of the 7 battery receipts + run-battery.py + census-start.out cited above)
