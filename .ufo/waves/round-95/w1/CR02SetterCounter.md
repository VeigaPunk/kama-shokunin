# CR02SetterCounter — attack on frozen C2 counter (round 95, depth)

## Scope
Frozen counter `tools/round95-setter-sweep.py`, bytes identical at F=`c798e831` and M2=`beef8922`
(sha256 `753f8ff62a5e690c9cce2d528b9b0bc591f10352eea8a8a43302d2bb57a618cd` at both revs,
`counter-provenance.txt`). SKILL.md and corpus/SOURCES.md extracted at M2 into the out dir; every forgery is
one SKILL.md variant in the out dir, run against `--rev beef8922` with the pinned b12177 archive
(sha256 `f50a52f4…ea13`, verified on download, rc=0). Lane read-only; no commits; scratch removed before yield.

## Commands and outputs (exit codes)
- Baseline, predicate mode: `python3 tools/round95-setter-sweep.py --repo . --rev beef8922 --work <scratch>
  --archive <scratch>/b12177.tar.gz` → **rc=0**, line below; `SETTER_DIGEST f50a52f4…ea13`.
- Every forgery: same command with `--skill-file <out>/<V>.md` (S7 adds `--sources-file`) → **rc=1 for all**,
  survivors included: line 418 returns 1 whenever `--skill-file/--sources-file` is set. The discriminator is
  `met=`, not the exit code. (Receipts `run-*.out`.)
- `grep -cF '<plan C2 line>' base.out` → **0**: the plan's quoted line is not a literal substring of stdout;
  `derived_checked=47` is interposed between `fabricated=0` and `derived_disagree=0`.

Baseline: `SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 entries=7 decisions=9 decisions_bound=9 met=True`

Required forgeries (decisive `SETTER_*` line; all rc=1):
- V1 round-94 SKILL verbatim (`V1-round94-verbatim.md`): `SETTER_SWEEP95 population=106 rows=0 bound=0 unbound=0 missing=106 duplicates=0 fabricated=0 derived_checked=0 derived_disagree=0 entries=0 decisions=0 decisions_bound=0 met=False`; 106 `SETTER_MISSING`.
- V1b round-94 body retitled to the round-95 head: `SETTER_SWEEP95 population=106 rows=92 bound=92 unbound=0 missing=14 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 entries=7 decisions=0 decisions_bound=0 met=False`; 14 `SETTER_MISSING` (P93–P106) and 8 `SETTER_DECISION_MISSING` — round-94 classified P16 `n_parallel|other`, so its model had 8 pairs, not 9.
- V2 drop new row P96: `SETTER_SWEEP95 population=106 rows=105 bound=105 unbound=0 missing=1 … entries=7 decisions=9 decisions_bound=9 met=False`; `SETTER_MISSING common/preset.cpp:292`. (No decision set changes: all 14 new rows carry `-` or `realises`.)
- V2b drop setter row P87: `…missing=1 … decisions_bound=8 met=False`; `SETTER_MISSING tools/server/server-models.h:80`, `SETTER_DECISION R20 unbound setter-set want=1 got=2`.
- V3 fabricated line (P107 at `common/preset.cpp:99999`): `SETTER_ROW P107 unbound fabricated`; `…rows=107 … fabricated=1 … met=False`.
- V4 wrong Entry on new row P100 (`cli`→`server`): `SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 entries=7 decisions=9 decisions_bound=9 met=True` → **SURVIVOR**.
- V5 R20-cli id set +P51: `SETTER_DECISION R20 unbound setter-set want=2 got=3`; `…decisions_bound=8 met=False`.
- V6 P91 `default`→`realises` (value made `-`, id set untouched): `SETTER_DECISION R21 unbound setter-set want=5 got=6`; `…decisions_bound=8 met=False`. V6b (D-row Parameter=`realises`): `SETTER_DECISION R21 unbound header`; `…decisions_bound=8 met=False`.
- V6c V6 + R21 id set edited to match (coherent reclassification): `…decisions_bound=9 met=True` → **SURVIVOR**.
- V7 P102 `realises` with Parameter `-`: `SETTER_ROW P102 unbound dash-param-realises`; `…bound=105 unbound=1 missing=1 … met=False`; `SETTER_MISSING tools/server/server-context.cpp:1489`.
- V8 `[default]` removed from R20-shared decision text: `SETTER_DECISION R20 unbound decision-precedence`; `…decisions_bound=8 met=False`.
- V9 R20-shared row deleted: `SETTER_DECISION_MISSING port shared setters=P38`; `…decisions=8 decisions_bound=8 met=False`. V9b (R21-shared): `SETTER_DECISION_MISSING n_parallel shared setters=P37`; same shape.

## Findings
**BLOCKER — the counter prints `entries=` but `met` does not read it** (`tools/round95-setter-sweep.py:410-412`
met tuple; `:412` computes `entries` afterwards; `:418` exits on `met`). S8 relabels P85 `router`→`other` (a
`copies` row) and the counter prints `… entries=6 decisions=9 decisions_bound=9 met=True` (`run-S8-entries-metric.out`).
Committed, that table exits 0 while printing a line that contradicts the frozen predicate (`entries=7`), so
C2's exit condition is narrower than its own quoted predicate (round-94 K1 class, repeated). One-line fix.

**DEFECT — the 14 new carrier rows sit outside every decision id set.** `want` is built only from
`default|overrides` rows (`:366-370`), so P93–P100 (`-`) and P101–P106 (`realises`) enter no set; their Entry
cells are enum-checked only (`:269`). V4 mislabels P100 — the whole-struct carrier the section exists to admit —
`cli`→`server` and scores `met=True`. Round-94's G05 instance *is* now caught (S15: P50 `cli`→`server` →
`SETTER_DECISION R20 unbound setter-set want=16 got=15` and `want=1 got=2`), but K02's declares-row relabel is
not (S16: P18 `server`→`other`, `met=True`).

**DEFECT — row ids are free, and the decision model trusts id strings.** No uniqueness check: `seen` is keyed
by (file,line) only (`:255,:356`), so S6 (P38 renamed P93, an existing id) and S6b (P38 renamed P37, the live
`n_parallel|shared` id) both score `met=True`, with the R20-shared and R21-shared rows each citing "P37" for a
different physical row (`run-S6*.out`). K3's "id set equals the setter rows" is string equality, not row identity.

**NOTE — round-94 survivor classes retested on the round-95 document** (all `met=True`, receipts in out dir):
value cell when RHS is not an integer literal (S1, P50 free-port value → `8080`; `INT_RHS` only, `:281-286`);
`default`↔`overrides` swap (S2, P38); condition garbage on a config-route row (S3, P93; `derived_checked` is
still 47 with 14 new rows, so the new rows contribute no derived cell; `:295` grades only `common/arg.cpp`
add_opt blocks); scope garbage on a non-arg.cpp row (S4, P101); decision text negated while still carrying the
tokens (S5, R20-shared; `:392-396` is substring presence, no polarity); fabricated SOURCES row (S7: S999 citing
the right file URL → `met=True`; citing another file is caught — first S7 attempt gave `SETTER_ROW P93 unbound source`);
hidden rows are still caught by `missing` (S11 comment → missing=1, S12 fence → missing=106; `section_rows` is
unchanged from round 94 except a comment).
- **Caught, verified:** integer literal (S13 `P11 value-literal` + dependent `R21 setter-set`), text (S14 `P93 text`), fabricated key (V3), id-set off-by-one (V5), deleted decision (V9/V9b), missing precedence token (V8), `realises`+`-` (V7), D-row header (V6b), dropped carrier (V2 `missing`), dropped setter (V2b).
- **New hole besides the BLOCKER:** a decision row's Sources cell is never read (S9 → `met=True`); P-row sources are graded only as "some cell contains `/b12177/<file>`" with no S-row status/sha check (`:175-184`).

**NOTE — `--skill-file/--sources-file` force rc=1** (`:418`), so any harness reading exit codes alone scores
every survivor as caught; the receipt must quote `met=`. Consistent with round 94, restated because this round's
V1–V9 exit codes are all 1.

**NOTE (calibration, for the C3 owner, not judged here)** — the plan's C2 line is not printed contiguously
(`derived_checked=47` interposed; `grep -cF`=0) and its numeric tokens (`population=106`, `entries=7`, …) do not
occur in the counter bytes (docstring uses placeholders). Under `round95-freeze-audit.py`'s `TOKEN_RE` (`:47`,
numerics matched) those would read as token-missing.

## Which round-94 classes (CR02's 20/38) this counter now catches
Newly caught: entry relabel of a `default|overrides` row (S15); effect moved out of the setter class when the id
set keeps the row (V6); missing decision row (V9/V9b); missing precedence token (V8); `realises`+`-` (V7, newly
reachable). Still not caught: non-literal value, entry on `copies`/`declares` rows, `default`↔`overrides`,
condition, scope, decision negation, row-id rename/duplication, fake SOURCES row; plus new: the printed `entries`
metric and decision-row Sources. Net: 1 of 8 round-94 survivor classes fully closed, 1 partially (setter rows
only); the other 7 bind, and 2 new holes join them. The section's per-entry claim is real for setter rows
(8→9 pairs, V1b), but the carriers it adds are graded by line text only.

## Smallest safe correction (advisory; next freeze, no frozen predicate changed here)
1. Add `entries == 7` and `ndec == 9` (module constants) to `met`. 2. Reject a second P-row using an existing
id (`duplicates`). 3. Check `copies` rows' Entry against a frozen map (P50/P51/P74/P82/P100) or admit them into
the fed entry's id set. 4. Bind a D-row's Sources cell to the S-rows it names. 5. Print the predicate line
exactly as the plan quotes it (or freeze `derived_checked` in the plan).

## Deliverables
`.ufo/waves/round-95/w1/out/CR02SetterCounter/`: `V1-round94-verbatim.md`, `V1b-round94-retitled.md`,
`V2-drop-newrow.md`, `V2b-drop-setter-row.md`, `V3-fabricated-line.md`, `V4-entry-newrow.md`,
`V5-id-off-by-one.md`, `V6-default-to-realises.md`, `V6b-decision-param-realises.md`,
`V6c-realises-coherent.md`, `V7-realises-dash-param.md`, `V8-shared-default-token.md`,
`V9-shared-decision-deleted.md`, `V9b-shared-np-decision-deleted.md`, `S1..S16` variants (17 files, incl. `S6b`),
`S7-fake-source-SOURCES.md`, M2 `skill-M2.md`/`SOURCES-M2.md`, `build.py`, `base.out`, `skillM2.out`,
`run-*.out` (32 receipts), `counter-provenance.txt`, `r94-counter.py`.

VERDICT: partial — C2's frozen predicate reproduces at M2 (rc=0, met=True, counter bytes identical at F and M2), and per-entry decisions are enforced for setter rows, but `met` ignores the `entries` field it prints, the 14 new carrier rows enter no decision set, and 7 of 8 round-94 semantic survivor classes still bind.
