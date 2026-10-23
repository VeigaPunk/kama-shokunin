# CtlBaseTree — control report (kama lane, round 30, claim C1 calibration)

Seat: `kama-r30-ctl-CtlBaseTree` · control call for C1 (pre-data control, committed before any correction row)
Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only; no lane git write performed)
Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlBaseTree` (fresh clone of the lane remote, checked out at lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c`)
Counter (FROZEN, bytes untouched): `.ufo/waves/round-30/count-c1.py`, sha256 `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` (re-verified before and after the run; unchanged)

## 1. Policy

A counter **variant** copied into the clone as `count-c1-basecheck.py` (the LANE bytes stay unchanged) that
**sets every oracle item's writing revision `W` to the BASE commit before binding**, so every oracle class
check runs against the base tree (`2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`) instead of the tree at the
revision where the statement was actually written.

The only functional change is one line in `oracle_statements()` plus a receipt marker:

```
             for cls in ORACLE_LINE_READ:
                 if cls in item:
                     item.pop(cls)  # never read by the check; dropped to prove it
+            # CtlBaseTree variant: every oracle item's writing revision W is replaced by
+            # the BASE commit, so the class check runs against the base tree instead of
+            # the tree at the revision where the statement was written.
+            item["W"] = BASE
```

Full diff (clone commit `d94409edda9fc40ebe8fdbf1d9c16c172cc26d96`, parent `52ac3af8614b5040ba5e17f17a2c7af029706e6c`,
`1 file changed, 604 insertions(+)` — the whole counter is a new file in the clone): `policy.diff`
(the same diff minus the copied body is the 7-line hunk above).

Commit identity (local, clone only): `UFO-FSD CtlBaseTree <ctlbasetree@ufo-fsd.invalid>`.

## 2. Commands and receipts

Both counters were run on the **same candidate tree** (`--repo` = the clone, `--tip` = the clone commit
`d94409edda9fc40ebe8fdbf1d9c16c172cc26d96`, whose tree is the lane tip tree plus the variant file):

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
    --repo /fast/scratch/hyaku/kama-r30/ctl/CtlBaseTree --tip d94409edda9fc40ebe8fdbf1d9c16c172cc26d96 \
    --out .../controls/kama-r30-ctl-CtlBaseTree/counter.json          # LANE bytes

/usr/bin/python3 /fast/scratch/hyaku/kama-r30/ctl/CtlBaseTree/count-c1-basecheck.py \
    --repo /fast/scratch/hyaku/kama-r30/ctl/CtlBaseTree --tip d94409edda9fc40ebe8fdbf1d9c16c172cc26d96 \
    --out .../controls/kama-r30-ctl-CtlBaseTree/variant.json           # my copy
```

Summary lines, verbatim:

* LANE copy — `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip d94409edda9f` — **exit 0**
* My copy (variant) — `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 12 append_only True valid_corrections 11 false_corrections 0 unresolved 1 met False tip d94409edda9f` — **exit 0**

`met` from the LANE receipt (`counter.json`): **False**. `met` from the variant receipt (`variant.json`): **False**.

Receipt files: `counter.json` (lane), `counter.out` (lane summary + `LANE_EXIT=0`), `variant.json` / `variant.out`
(variant summary + `VARIANT_EXIT=0`), `variant-at-base.json` / `.out` (variant at `--tip` = base commit:
`statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 12 append_only True valid_corrections 0 false_corrections 0 unresolved 12 met False tip 2aa46e2481d2`),
`variant-list.json` (per-statement `--list` dump), `policy.diff`.

Field-by-field, lane vs variant on the same tree:

| field | lane | variant |
|---|---|---|
| statements | 141 | 141 |
| extracted | 69 | 69 |
| oracle_items / bound / unbound | 72 / 72 / 0 | 72 / 72 / 0 |
| mismatched_at_base | **13** | **12** |
| append_only | True | True |
| valid_corrections / false_corrections | 11 / 0 | 11 / 0 |
| unresolved | **2** | **1** |
| met | False | False |

The 11 valid corrections are the round-29 rows already present at the lane tip; the candidate tree carries no
round-30 row, so the residual unresolved set is the two oracle Q items in both receipts.

## 3. The misclassified statement

**`SCORECARD.md:Q:4a6f7c911e:o0`** — oracle item for `SCORECARD.md:41`, class **Q**, text `` `file=yes` ``.

* Lane counter (W = the item's writing revision `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`, 2026-10-14 09:46:23 -0300):
  `git grep -F -e 'file=yes' <W> -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'`
  → **no hit** → observed `q:no-artifact`, statement **does not hold** (counted as a mismatch).
* Variant (W forced to BASE `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`): the same grep at BASE **does** hit —
  `.ufo/round-5/acceptance.json:24` and `.ufo/round-10/gates/check.json:9` both contain the bytes `file=yes`.
  → observed `ok`, statement **holds** → the variant silently drops it from the mismatch set.

Provenance: both artifact files were committed **after** the statement's writing revision and **before** BASE —
`.ufo/round-5/acceptance.json` in `e246c40` (2026-10-15) and `.ufo/round-10/gates/check.json` in `1e41928`
(2026-10-19); `ea72c3ea` (2026-10-14) is an ancestor of BASE, and 150 commits separate them. The statement was
therefore written *before* any committed artifact carried the span, and only later acquisitions make it look
true.

That single flip is the whole difference: `mismatched_at_base` 13 → 12 and `unresolved` 2 → 1. No other statement
changes verdict — the 11 base-extracted mismatches are byte-identical in both receipts (extractor output is
untouched), the second oracle item `SCORECARD.md:Q:422b431349:o0` (line 901, `declared2048 = captured training2048`)
still fails at BASE because the span occurs only inside `SCORECARD.md` (an excluded path), and the C / H / T / P
oracle items keep their verdicts at BASE (their referenced commits and blobs are ancestors of BASE; the base tree
carries the same blob digests).

## 4. Is this arm a genuine shortcut?

**No — it is a mis-scoping of the evidence, and it cannot turn the claim green.** It is not even a counter
shortcut in the sense of "make the predicate true": the frozen predicate demands `mismatched_at_base == 13`, and
the variant reports `12`, so it fails the predicate on its own terms (`met False` in both receipts). What it
demonstrates is the converse and more useful thing: **the counter's "check at the writing revision" clause is
load-bearing for calibration, and evidence-at-base is a different, weaker question.**

Concretely, the hazard it exposes for the real claim:

* An author who verifies the disclosed statements against the **base tree** concludes that `SCORECARD.md:41`
  `` `file=yes` `` is true (the span is present in `.ufo/round-5/acceptance.json` and
  `.ufo/round-10/gates/check.json` at base), and therefore appends **no** correction row for it. Under the
  **lane** counter that row is required: the LANE receipt on this very tree lists
  `SCORECARD.md:Q:4a6f7c911e:o0` as a mismatch with observed `q:no-artifact`, and it is one of the two ids in
  `unresolved_ids`. Such a submission would land `unresolved 2`, `met False`.
* Conversely, an author who trusted the variant's `12` would also mis-state the population ("one statement does
  not hold"), which is exactly the calibration claim C1 is about.

So the arm shows the wrong-direction error mode is a **silent under-count of false statements** (13 → 12), not a
spurious green, and it confirms that the round-30 predicate's `mismatched_at_base == 13` term is sensitive to
where the evidence is looked up. It also names the concrete reason the two disclosed false statements differ
from the eleven: for line 41 the "evidence" that would clear it exists in the lane but only *after* the
statement's writing revision, whereas for line 901 no committed artifact ever carried the span.

## 5. Risks / blockers

* None blocking. The lane counter bytes were not modified (sha256 re-verified `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`
  before and after). No lane git write was performed; the only lane-side writes are the receipt/report files
  under `.ufo/waves/round-30/controls/` (this directory and `controls/CtlBaseTree/`).
* The candidate tree is the lane tip tree plus the added variant file (`count-c1-basecheck.py`). The lane
  counter reads only committed objects at the pinned revisions (`BASE`, `ORACLE_REV`, the per-line blame
  revisions, and the tip), and the variant file lives at the tip only, so it does not perturb any
  extractor-derived verdict — confirmed by the lane receipt matching the lane's own committed base receipt shape
  (141 / 69 / 72 / 13) and by the 11 round-29 rows still validating.
* Note for the parent: the `unresolved 2` / `valid_corrections 11` seen here is the *pre-data* state of the
  candidate tree (lane tip, no round-30 rows). It is not a claim about the claimed work.
* Tooling: no installs or updates were required or performed for this seat (system `git` 2.56.0 and
  `/usr/bin/python3` 3.14.8 were already present; `uv`/`npx` not needed). The generic tooling directive is
  therefore vacuous for this seat — nothing was installed, updated, or upgraded.
