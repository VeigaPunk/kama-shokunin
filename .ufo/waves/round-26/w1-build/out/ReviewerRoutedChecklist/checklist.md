# Round-26 routed-defect acceptance checklist

Scope: round-25 spot-check routed defects 1-8
(`corpus/lessons/round-25-verifier-spotcheck.md:203-232`) and the round-24
routed items 1-5 (`corpus/lessons/round-24-verifier-spotcheck.md:147-160`).
Checked revision: `a23c0e042114016a909eb15173aa6df74b5b7eb0`. Base:
`1560e4d83f42b04f40336357de6f9637eafa0f4b`.

Re-run at the landed tip: `bash .ufo/waves/round-26/w1-build/out/ReviewerRoutedChecklist/checks.sh <landed-tip>`.
The script reads committed bytes through `git show REV:path`. D1 and D7 read
live state: the working tree and the hyaku wave-slots file. D5 runs the
round-25 C2 counter in a `git archive` extract under
`/fast/scratch/hyaku/kama-r26/ReviewerRoutedChecklist/checks/`. The script
starts no server. The full output at a23c0e04 is in `checks-a23c0e04.out`
(script exit 0).

Grep counts print `0` with exit 1 when nothing matches; that is the expected
"absent" result, not a failure of the script.

## Summary

| Item | State at a23c0e04 | Who acts |
|---|---|---|
| D1 uncommitted round-25 paths | **open**: 1 path still untracked | L1 |
| D2 KQ36 "landed tip" and lesson erratum | **open** | L1 |
| D3 supersedes rows for S106, S109, S113 | **open** | L1 |
| D4 entry wording, lines 55-56 and 137 | **open** | L1 |
| D5 count-c2 raw-hash binding | **open**: reproduced on a mutant | L1 |
| D6 SCORECARD round-25 trend-line correction | **open** | L1 |
| D7 wave-slot reservation held until every seat returns | **in progress**: row held, 7 of 36 advice reports present | L1 holds it; there is no release record (see D7) |
| D8 lowest-axis claim | **met at preregistration**: C1 is on depth (7) | closure judges fit |
| R24-1 original clauses untouched | **holds** | none |
| R24-2 PM08 manual and uncredited | **holds**; stale semantics are debt that needs separate authorization | operator or closure authorization |
| R24-3 locator correction; append lineage | locator **done** (round-25 lesson); lineage **unresolved** | closure or operator |
| R24-4 qualifications kept | checkable only on the round-26 report | L1 |
| R24-5 H2 (Git ≥ 2.45 floor) | **operator-owned, open** | operator |

## D1 — 42 uncommitted `a2-falsify/` paths

Resolved when:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- .ufo/waves/round-25
# expected: no output, exit 0
git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-files .ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw | wc -l
# expected: 70
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <tip>:.ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw/L3.server.log | sha256sum
# expected: c6723b145db5673dc3579309b6e42303f855f71281e6062783378c7b3ef1d06b
```

Now (D1a, D1b):

```
?? .ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw/L3.server.log
exit=0
69
exit=0
```

Commit a4a159c3 (220 adds, 2 modifications, 1 deletion under
`.ufo/waves/round-25`) left one file out:
`replication-run3/raw/L3.server.log`, 1446775 bytes, mtime
2026-10-22 07:31:37 -0300, sha256 `c6723b14…d06b`. The committed
`replication-run3/receipt.json` binds it as cell L3 `server_log`. Without
it, the committed replication evidence has 69 of its 70 raw files. The file
is not ignored (`git check-ignore -v` exit 1). It is also not too large to
commit: the 1446303-byte `final/raw/L3.server.log` is tracked. Fix: commit
the file. Reverting it would leave a receipt hash with no file.

## D2 — KQ36 "landed tip" qualification and lesson row-2 erratum

Resolved when:

```sh
git -C $L diff --numstat 1560e4d8 <tip> -- corpus/QUALITY.md
# expected: "<N>\t0\tcorpus/QUALITY.md", N > 0 (append-only)
git -C $L diff 1560e4d8 <tip> -- corpus/QUALITY.md | grep '^+' | grep -v '^+++' | grep -c -i 'landed tip'
# expected: >= 1; read the hit: it must define landed tip as "measured source and
# instrument bytes identical to the landing commit, later changes disclosed"
git -C $L diff --numstat 1560e4d8 <tip> -- corpus/lessons/round-25.md SKILL.md
# expected: additions only (second column 0)
git -C $L diff 1560e4d8 <tip> -- corpus/lessons/round-25.md SKILL.md | grep '^+' | grep -v '^+++' | grep -c M17
# expected: >= 1 (the erratum, or a SKILL row line that says M17 survives)
```

Now (D2a to D2e): QUALITY.md numstat is empty, so it is unchanged since base.
The `landed tip` added-line count is `0` (exit 1). The lesson and SKILL numstat
is empty. The added-line M17 count is `0` (exit 1).
`git show a23c0e04:SKILL.md | grep -n -i -E 'M17[^|]*surviv'` finds nothing
(exit 1). M17 appears only at `SKILL.md:883` and `:889`, and neither line says
it survives. Lesson `corpus/lessons/round-25.md:49` still says "the
instrument docstring and SKILL registry row now say M17 survives and why".
KQ36 is at `corpus/QUALITY.md:203`, with its heading at `:199`.

## D3 — `supersedes` rows (KQ31) for S106, S109, S113

Resolved when:

```sh
git -C $L show <tip>:corpus/SOURCES.md | grep -oE '\| supersedes S1(06|09|13) —' | sort | uniq -c
# expected: one line each for S106, S109, S113 (count >= 1)
git -C $L diff 1560e4d8 <tip> -- corpus/SOURCES.md | grep -cE '^-\|[[:space:]]*S[0-9]{3}[[:space:]]*\|'
# expected: 0 (old rows byte-identical, KQ31)
cd /home/vgpnk/Projects/shokunin && bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama | tail -1
# expected: "kama	ok	…/corpus/SOURCES.md", exit 0
```

Now (D3a to D3c): no `supersedes S106/S109/S113` rows (empty output). No old
row is removed (`0`, exit 1). The census prints `kama ok`, exit 0, with
W04-only warnings for S108, S109, S110 and S112. The content each row must
carry is in spot-check lines 213-217: fit.cpp measurement at line 264 comes
before resolution at 270-276; reduction needs `global_surplus < 0` at line
384; the floor path is at 414 and 441-444; S109 needs the idle-slot purge
precondition; S113 needs "per layer". The S107 and S112 corrections are
unverified by the closure.

## D4 — `corpus/knowledge/context-capacity.md` wording

Resolved when:

```sh
git -C $L show <tip>:corpus/knowledge/context-capacity.md | grep -n 'the only trace'
# expected: no match, or a match qualified so it names both K5 log lines
git -C $L show <tip>:corpus/knowledge/context-capacity.md | grep -c 'exceeds the training context'
# expected: >= 1 (cites K5.server.log:1083)
git -C $L show <tip>:corpus/knowledge/context-capacity.md | grep -n -E '1024 cells|held 1024'
# expected: >= 1 match near the L1 release text (old line 137)
```

Now (D4a to D4d): line 55 reads "the only trace" (exit 0). `exceeds the
training context` count is `0` (exit 1). `1024 cells|held 1024` finds nothing
(exit 1). The evidence line does exist:
`final/raw/K5.server.log:1083` =
`0.00.008.336 W srv    load_model: the slot context (4096) exceeds the training context of the model (2048) - capping`.
Line 137 still reads `n_tokens = 1025` … `2 × 1025`. The same 1025 framing
recurs at lines 143-144, 156 and 161. Those lines are not routed, but they
should be checked for the same off-by-one reading.

## D5 — `count-c2.py` accepts receipts without checking raw hashes

Resolved when either of these holds:

- the counter (or a successor registered by a dated amendment) rejects a
  receipt whose `cells[].raw` sha256 values do not match files in
  `final/raw/`. On the mutant built by `checks.sh` (append `TAMPERED\n` to
  `final/raw/K1.server.log`, delete `final/raw/L3.server.log`), it prints
  `observed` < 14, or `bound False`, or exits non-zero. The pristine extract
  still prints `registered 14 observed 14 bound True missing []`; or
- the limit is registered: the counter docstring or round-25 preregistration
  states that raw hashes are not checked, and `grep -n -i -E 'hashlib|raw hash|not check'`
  on `count-c2.py` (or on the amendment) matches.

Now (D5a to D5c):

```
tip: registered 14 observed 14 bound True missing []   exit=0
mut: registered 14 observed 14 bound True missing []   exit=0
count-c2.py grep hashlib|raw hash|not check: no match   exit=1
```

An independent hash join on the same trees gave tip 70 of 70 matched, and
mutant 68 matched with 2 unmatched. The counter's output does not change. The
defect reproduces at a23c0e04. Editing the round-25 frozen file in place
changes a registered instrument's bytes. A new, dated amendment file keeps
the old bytes [INFERENCE: the lane's amendment convention, from round-25
amendments 1-4].

## D6 — SCORECARD round-25 trend line contradicts the report

Resolved when:

```sh
git -C $L diff --numstat 1560e4d8 <tip> -- SCORECARD.md
# expected: "<N>\t0\tSCORECARD.md" (append-only)
git -C $L show <tip>:SCORECARD.md | sed -n '1306,1310p'
# expected: byte-identical to now (the historical line stays)
git -C $L diff 1560e4d8 <tip> -- SCORECARD.md | grep '^+' | grep -v '^+++' | grep -i -E 'discernment|quality' | grep -i unchanged
# expected: >= 1 line, under a round-26 heading, correcting 1306-1310 to
# quality unchanged and discernment unchanged (report and closure agree)
```

Now (D6a to D6c): numstat is empty (unchanged since base; the file is 1310
lines). Lines 1306-1310 read "quality unchanged-to-improved … discernment
improved". There is no added correction line (exit 1).

## D7 — wave-slot reservation released while seats still ran

Resolved when the round-26 reservation row stays in
`~/.local/state/shokunin-hyaku/wave-slots` until every dispatched seat has
returned. Checkable observables:

```sh
grep -n 'kama kama-r26' ~/.local/state/shokunin-hyaku/wave-slots
# while any seat runs: the row is present
python3 -c "import json;print(len(json.load(open('.ufo/waves/round-26/w1-build/spec.json'))['items']))"
ls .ufo/waves/round-26/w1-build/advice | grep -c '\.md$'
# at release: advice report count == dispatched seat count (or each missing seat named dead)
```

Now (D7a to D7c): `23:1792726390 36 kama kama-r26-w1-build` (epoch 1792726390
is 2026-10-23T03:33:10Z). The spec has 36 items. There are 7 `.md` advice
reports, so the reservation is correctly held. Gap: `events.log` records no
slot-release events for kama (the last kama line is 729, `inline launch lane=kama round=26`).
After release, nothing shows when the row was removed. To make this
checkable, the L1 should record in the wave record the release time and
the number of seats that had returned at that time. Any later wave
(falsify) needs the same check.

## D8 — next round works a lowest axis

Resolved when the round-26 claim is on a lowest axis and the closure accepts
the fit:

```sh
git -C $L show <tip>:.ufo/waves/round-26/preregistration.json | python3 -c "import json,sys;print(json.load(sys.stdin)['claims']['C1']['axis'])"
# expected: depth (or calibration/adjacency)
```

Now (D8a, D8b): `depth`. `SCORECARD.md:1304` reads `Other scores held: operability 8, freshness 8, depth 7, adjacency 7`
(calibration 7 in the C1 row at 1260; coverage 9). Depth is a lowest axis.
The prereg `repairs` field reads "defect 8 is honoured by C1 working a lowest
axis (depth)". The axis fit of a signature table to depth is the closure's
call (AXES.md:33-34).

## Round-24 routed items

- **R24-1** (original clauses and seven unmet cells untouched):
  `git diff --stat 5cb46efc a23c0e04 -- .ufo/waves/round-24 corpus/lessons/round-24.md`
  prints nothing, exit 0. **Holds.** Expected at the landed tip: still empty.
- **R24-2** (stale PM08 and mutation semantics): `SKILL.md:888` contains
  `PM08 is a manual review-only note, unexecuted, uncredited`. `SKILL.md:994`
  reads "not settled evidence; corrected in round 25". **Holds** as wording.
  The underlying semantics change is routed "only through separately
  authorized future work". That needs authorization from the operator or a
  closure; it is not a lane action this round. Expected at tip: line 888's phrase is
  still present.
- **R24-3** (locator corrections, append lineage): `corpus/lessons/round-25.md:66-74`
  gives the exact locators (`fixes/docs/ScribeLesson/`,
  `falsify/out/ConnSources/verify.txt`). Line 74 reads "prepared-versus-landed
  append lineage stays unresolved, as routed". The locators are **done**. The
  lineage is **open**: it can be resolved only from original-hash evidence
  that the round-24 closure found missing, so it needs a closure or operator
  ruling.
- **R24-4** (no no-effects, backend-identity, continuous-floor or
  full-isolation claim): this applies to the round-26 report text, which does
  not exist yet. Expected at the landed tip: any matches of
  `grep -n -i -E 'no-effects|backend identity|full isolation|continuous floor'`
  in the round-26 report are only negations or qualifications.
- **R24-5** (H2, the Git ≥ 2.45 prerequisite): **operator-owned, open.** The
  host `git version 2.56.0` satisfies the prerequisite. The routed issue is
  the unapproved floor and the lost support for older Git, which is not a
  host fact.

## Operator action needed

- R24-5: H2 floor approval or rejection.
- R24-2: authorization to change PM08 or the registered mutation semantics,
  if wanted.
- R24-3: a ruling on the unresolved prepared-versus-landed append lineage.
- SHONEN promotion (spot-check line 234: "Promotion is operator-owned").

D1 to D6 are lane (L1) edits. D7 is L1 seat accounting; making the release
time auditable may need a hyaku-side release event, which is outside the
lane's write scope [INFERENCE]. D8 needs a closure judgment.
