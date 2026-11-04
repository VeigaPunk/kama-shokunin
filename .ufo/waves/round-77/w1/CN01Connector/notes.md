# CN01Connector notes — kama round 77, wave 1 (read-only seat)

Seat: connector. Read-only over sibling repos and `/home/vgpnk/Projects/shokuknow`; writes confined to
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/CN01Connector/` (this dir) and the seat report
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/CN01Connector.md`. No tools installed or upgraded
(named-items seat; nothing needed — recorded per the tooling-authorization rule as "no installs"). Scratch
`/fast/scratch/hyaku/kama-r77/CN01Connector/` was created per §7, never used (no clones, no fixtures), and deleted
before yield. No git/jj mutation was run anywhere; only read-only git (`rev-parse`, `merge-base --is-ancestor`,
`ls-tree`, `log`) inside the lane.

Context anchors (commands + verbatim output):

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master
7d60e2ab58866a0366937d61c9712483be57b36e
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin merge-base --is-ancestor cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 master && echo rc0
rc0
```

Frozen plan `plans/round-77-claims.md` read in full before any item. The **base revision**
`cc6e1d3c…` was observed ancestral to master; this check did not identify the separate freeze commit.

---

## 1. Sibling-overlap scan

Method classes scanned over all 21 `*-shokunin` repos (read-only):

- baseline-receipt class: `measured/before`, `diff-filter=A`, `merge-base --is-ancestor`
- register-cutoff/rotation accounting: `append-only`, `cutoff`, and the distinctive machine tokens
  `rotation_safe|append-only-(accepted|exempt)|accepted_cutoff|exempt_cutoff` and
  `APPEND_REGISTERS|APPEND_EXEMPT|append-registers|append-exempt`

Per-repo file counts (bash aggregation pipeline; loop body:
`n=$(grep -rl --binary-files=without-match -e PATTERN "$d" 2>/dev/null | wc -l)`), verbatim:

```
audio-shokunin measured/before=0 diff-filterA=1 is-ancestor=9 register-classes=0
chousa-shokunin measured/before=6 diff-filterA=49 is-ancestor=149 register-classes=0
game-dev-2d-shokunin measured/before=0 diff-filterA=2 is-ancestor=10 register-classes=0
game-dev-3d-shokunin measured/before=0 diff-filterA=4 is-ancestor=20 register-classes=0
kagi-shokunin measured/before=0 diff-filterA=11 is-ancestor=53 register-classes=0
kaidoku-shokunin measured/before=0 diff-filterA=367 is-ancestor=383 register-classes=0
kake-shokunin measured/before=0 diff-filterA=149 is-ancestor=522 register-classes=0
kama-shokunin measured/before=210 diff-filterA=433 is-ancestor=393 register-classes=61
kasegi-shokunin measured/before=0 diff-filterA=12 is-ancestor=331 register-classes=0
kengaku-shokunin measured/before=0 diff-filterA=78 is-ancestor=366 register-classes=0
kotoba-shokunin measured/before=0 diff-filterA=88 is-ancestor=322 register-classes=0
kotodama-shokunin measured/before=0 diff-filterA=74 is-ancestor=160 register-classes=1
kumitate-shokunin measured/before=0 diff-filterA=50 is-ancestor=758 register-classes=0
lore-shokunin measured/before=0 diff-filterA=7 is-ancestor=39 register-classes=0
mado-shokunin measured/before=0 diff-filterA=70 is-ancestor=270 register-classes=0
mori-shokunin measured/before=0 diff-filterA=122 is-ancestor=457 register-classes=0
revenger-shokunin measured/before=0 diff-filterA=6 is-ancestor=46 register-classes=0
souji-shokunin measured/before=0 diff-filterA=1718 is-ancestor=1335 register-classes=0
tabi-shokunin measured/before=2 diff-filterA=102 is-ancestor=428 register-classes=0
tameshi-shokunin measured/before=0 diff-filterA=189 is-ancestor=665 register-classes=0
tsukuroi-shokunin measured/before=0 diff-filterA=39 is-ancestor=346 register-classes=0
```

(`merge-base --is-ancestor` and `--diff-filter=A` alone are fleet-wide git idioms — 10–1700 files per lane — so the
class-A judgment rests on the *combination* introduction-commit + ancestry + byte-stability binding, not the idiom.)

### Class A findings (baseline-receipt method)

- **mori round 24 — prior use of the introduction-commit + ancestry recipe** (verified verbatim):
  `/home/vgpnk/Projects/shokunin/mori-shokunin/.ufo/waves/round-24/w1/ReviewDeclarationSizing.md:72-73`:

  > Minimal fix: state the ordering as a labelled precondition with its own command:
  > `git merge-base --is-ancestor <commit adding cases.json> <commit adding tools/mori-pressure.py>`
  > exits 0, with both commits found by `git log --diff-filter=A --format=%H -1 -- <path>`.

  Same recipe applied in `/home/vgpnk/Projects/shokunin/mori-shokunin/.ufo/waves/round-25/w1/CriticLearningRules.md:131-135`
  (F/B introduction commits via `--diff-filter=A`, `merge-base --is-ancestor`, `diff --quiet "$F" "$R" -- "$C"`
  `cases_unchanged`, blob count at the freeze commit).

- **mori rounds 26–27 — the machinery plus its own rename refutation**
  `/home/vgpnk/Projects/shokunin/mori-shokunin/.ufo/waves/round-26/count-c2.sh:5-10` (verbatim):

  ```bash
  F=$(git -C "$L" log --format=%H --diff-filter=A "$R" -- "$C" | tail -1); B=$(git -C "$L" log --format=%H --diff-filter=A "$R" -- "$T" | tail -1)
  [ -n "$F" ] && [ -n "$B" ] || { echo "absent cases_commit=${F:-none} tool_commit=${B:-none}"; exit 2; }
  git -C "$L" merge-base --is-ancestor "$F" "$B" && [ "$F" != "$B" ] && echo freeze_order=ok || echo freeze_order=bad
  echo "cases_changed_since_freeze=$(git -C "$L" diff --name-only "$F" "$R" -- "$C" | wc -l)"
  echo "N=$(git -C "$L" show "$F:$C" | jq '.cases|length')"
  ```

  and `/home/vgpnk/Projects/shokunin/mori-shokunin/.ufo/waves/round-27/w1/CriticC2Counter.md:120-124` (finding F6):

  > **F6. The freeze commit is wrong under a rename.** Line 42 runs `git log --diff-filter=A` without `--follow`.
  > Path limiting turns a rename into an add.

- **tabi — adjacent measurement binding**
  `/home/vgpnk/Projects/shokunin/tabi-shokunin/scripts/selftest-measurement-binding.mjs:91-105`: claim objects carry
  `before: {revision, count}` / `after: {revision, count}` ("measured/before/after default to rev1") — binding
  measurements to revisions in a harness, not a receipt-introduction class.

- **chousa — witness copies, no claim**
  `/home/vgpnk/Projects/shokunin/chousa-shokunin/.ufo/waves/round-73/w1/R73S03/.ufo__reports__round-{65,66,71,72}__kama.md.txt`
  are byte extracts of kama's own fleet reports (header lines `fleet_revision=…`, `source=.ufo/reports/round-65/kama.md`,
  `git_show_rc=0`). Chousa holds kama's receipts as recon evidence; it claims nothing on the method.

- **kama (210 files)** — the lane's own lineage: `measured/before` receipts since r65, r72 receipt-tip-binding,
  r76 receipt-scope, r77 C1. Home lane, not a competitor.

**Verdict (C1 overlap):** kama's C1 *primitives* (introduction commit via `--diff-filter=A`, ancestry via
`merge-base --is-ancestor`, byte-stability across revisions) have prior sibling use in mori r24–r27 — as a
freeze-order precondition for fixture-vs-tool commits, a different subject. No sibling holds a claim on the
baseline-receipt class itself (a receipt under `measured/before/` bound by its own introduction and byte-stability).
Distinct on the claim, overlapping on the idiom.

### Class B findings (register-cutoff/rotation accounting)

- The distinctive token scan over all 20 siblings returns exactly one non-kama file:
  `/home/vgpnk/Projects/shokunin/kotodama-shokunin/.ufo/waves/round-76/w1/ScoutReadmeIndex.md:49` — prose in a SOURCES
  recon: "changed pre-existing-row lines are append-only-exempt only inside `used-by`/`status`/`recheck`, per r75
  accept-ca APPENDONLY leg text". That is a SOURCES cell-edit exemption rule, not audit-event register accounting with
  introduction cutoffs or rotation checks.
- `APPEND_REGISTERS|APPEND_EXEMPT|append-registers|append-exempt` over all 20 siblings: **no matches**.

**Verdict (C2 overlap):** kama's C2 register-cutoff/rotation accounting is **distinct** — no sibling lane holds a
competing or prior claim on it. Kotodama's single mention is adjacent (permitted-cell exemption) and names no
cutoff, register or rotation semantics.

---

## 2. considerthese sweep (newest file: `considerthese/2026-10-26.md`)

Directory listing (newest first): `2026-10-26.md, 2026-10-25.md, 2026-10-24.md, 2026-10-23.md, 2026-10-22.md,
2026-10-21.md, 2026-10-20.md, 2026-10-19.md`. The newest file was read in full. Its four proposals are all
"proposals only; I am not acting on any of them", and all four are **already dispositioned** by the lane
(verified in the lane, not from the prose):

| proposal (2026-10-26.md) | lane disposition (evidence) | state |
|---|---|---|
| 1 — flag deletions in append-only files | `tools/append-only-audit.py` (round-46 capability; `corpus/QUALITY.md` KQ86→KQ89 supersession chain, each row citing `considerthese/2026-10-26.md` proposal 1) | implemented |
| 2 — track what happens to my own proposals | `corpus/QUALITY.md` KQ97 ("Each daily `considerthese/YYYY-MM-DD.md` reflection … records, for each proposal in the preceding reflection window, the eventual disposition …"); `corpus/README.md` "Frontier disposition — round 55": "considerthese proposal 2 is represented by `corpus/QUALITY.md` KQ97 (proposal disposition tracking)" | implemented as a QUALITY criterion |
| 3 — running count of counters a shortcut can satisfy | `tools/shortcut-tally.py` (promoted from `.ufo/waves/round-47/w1/out/X9Tally/`, round 48; round-49 measured run "exit 0 over rounds 40–47"; round-64 `--rounds 56-63` run) + `corpus/QUALITY.md` KQ118 ("carries `considerthese/2026-10-26.md` proposal 3 into the bar") | implemented |
| 4 — report the pin gap every morning | `tools/pin-watch.py` (round 41) + the consumer criterion citing "considerthese/2026-10-26.md proposal 4 (still unimplemented at round 72)" and the round-73 live run `pins=3 current=0 behind=3 missing=0 error=0` (receipt `.ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out`); `corpus/README.md` round-10 note: "proposal 4 (daily pin-gap line) remains pending" | substance implemented; the "one line in each daily file" half unimplemented |

**Grounded note — the one candidate examined (proposal 4's residue):**

- **Proposal:** add one line per pinned engine (newest tag, releases above the pin) to each daily reflection.
- **Current state:** the data side exists (`tools/pin-watch.py`, round-73 live run) and a QUALITY criterion binds the
  consumer side; the only unbuilt part is the morning-report integration into `considerthese/YYYY-MM-DD.md` files.
- **Why unimplemented:** `considerthese/` is operator-authored input — §10 and the seat bounds say "mine it, never
  edit it". A lane cannot write the daily files, so this half is out of lane province by construction.
- **Should it land?** No — not as a lesson, QUALITY criterion, or SOURCES row. It is already represented by a
  QUALITY criterion plus a live receipt; a second row would duplicate it, and the remaining half demands an edit to a
  file the lane must never touch.
- **Sweep conclusion:** the newest considerthese file holds **no still-unimplemented proposal that is in lane
  province**. The round's frontier duty is satisfiable by the sweep-found-none record citing this note (the plan's
  Frontier bullet allows "or the sweep that found none").

---

## 3. Assimilation guard (read-only against shokuknow; adopt nothing this round)

Commands exactly as round prompt §10 prescribes, with one declared divergence: §10's canonical output dir is
`.ufo/waves/round-77/assimilation`, but this seat's bounds confine writes to
`.ufo/waves/round-77/w1/CN01Connector/`, so `A` points at `<seat>/assimilation/`. Patterns, inputs and pipeline are
byte-identical to §10; nothing was written into shokuknow; nothing was adopted.

```
S=/home/vgpnk/Projects/shokuknow
A=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/CN01Connector/assimilation; mkdir -p "$A"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md \
  | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$S/merge/kama/SOURCES.append.md" \
  | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"   # nonempty -> renumber in scratch

A=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/CN01Connector/assimilation; mkdir -p "$A"
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
  {print $4, $5}' "$R" > "$A/quarantine-slice"    # every line must carry an S-id
```

Verbatim output (counts + lists):

```
== reg-ids ==
reg-ids count: 289
== staged-ids ==
staged-ids count: 142
== collisions ==
collision count: 9
S330
S333
S334
S335
S346
S347
S352
S353
S363
== quarantine slice ==
slice rows: 7
 S200   `payload-absent`
 S202   `payload-absent`
 S206   `payload-absent`
 S210   `payload-absent`
 S211   `payload-absent`
 S224   `payload-absent`
 S230   `payload-absent`
```

Interpretation and verdict plan (mechanical, per §10; this seat adopts nothing):

- **Id collision: 9 collisions (nonempty).** Per §10, any future adoption renumbers in scratch before any append;
  adopted ids continue the lane's registry and every adopted entry's citation is re-pointed by document (URL/anchor
  is the evidence, the id follows it), never arithmetic. The renumber map is the L1's adoption-time duty.
- **Quarantine: 7 rows, every class cell the specific `` `payload-absent` `` family** (a specific absent-defect
  class, not a prose cell), so none of the rows is in the register's "unchecked family". Verdict plan per row
  (S200, S202, S206, S210, S211, S224, S230 — identical mechanical plan): quarantined, not appendable; before any
  append the cited source is fetched and the register's quote located — absent → refuse the row (fabrication class,
  reason in the round lesson's Gate block); present → adopt with the anchor actually located; unreachable → mark
  unverifiable (`unreachable` is not fabrication) and adoption stays closed. This round: all 7 rows stay out of any
  registry append; adoption is closed.
- Artifact files (absolute paths, all inside this seat dir):
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/CN01Connector/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice}`
  — commands as above, exit 0 (supervised run `assimguard`, exit code 0).

---

## 4. Rename-check on the C1 baseline population (grounding for the proposed move)

mori r27 F6 says an introduction-commit rule built on `git log --diff-filter=A` without `--follow` is wrong under a
rename. Checked read-only against the frozen base `cc6e1d3c…` for every round-75 `measured/before/` receipt
(the C1 shifted/baseline population's files):

```
$ for f in $(git ls-tree -r --name-only cc6e1d3c… -- .ufo/waves/round-75/measured/before/); do
    plain=$(git log --format=%H --diff-filter=A cc6e1d3c… -- "$f" | wc -l)
    follow=$(git log --follow --format=%H --diff-filter=A cc6e1d3c… -- "$f" | wc -l)
    echo "$f plain_adds=$plain follow_adds=$follow"; done
.ufo/waves/round-75/measured/before/c1-mutants.out plain_adds=1 follow_adds=1
.ufo/waves/round-75/measured/before/c2-mutants.out plain_adds=1 follow_adds=1
.ufo/waves/round-75/measured/before/c3-audit.out plain_adds=1 follow_adds=1
.ufo/waves/round-75/measured/before/control.out plain_adds=1 follow_adds=1
.ufo/waves/round-75/measured/before/source-gitattributes.receipt plain_adds=1 follow_adds=1
```

Each history query returned one addition. **Counts alone do not prove the two queries select the same commit,
nor rule out renames.** No live C1 defect is established by this check.

---

## 5. Contradictions named (not smoothed)

- Mori's older fixture-freeze rule treats rename provenance as material; kama's frozen rule explicitly binds a
  receipt at its declared path. These are different contracts. Mori's rename finding motivates a future boundary
  probe, not a demonstrated contradiction or defect in C1. Do not change the frozen counter on this evidence.
- The register's stale-summary caveat (§10) and this slice agree: 7 data rows derived fresh; the file's own header
  and `## By lane` totals were not trusted.
