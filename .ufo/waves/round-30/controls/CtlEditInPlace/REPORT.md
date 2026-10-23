# CtlEditInPlace — round-30 C1 control arm (calibration)

Advisory evidence for the frozen predicate
`mismatched_at_base == 13 and unresolved == 0 and oracle_items == 72 and oracle_unbound == 0 and append_only`.
This is a pre-freeze control, not a verdict on C1. A green or red measurement here never makes the claim.

## Policy applied

Item text (`controls/items/CtlEditInPlace.md`): "instead of appending a section, rewrite the two false base
lines in place (line 41 and line 901 of SCORECARD.md) so they no longer read as false."

The arm deliberately skips C1.claimed_work: it appends **no** correction section and **no** correction rows.
It edits the two false base lines where they stand.

The two false base lines are exactly the two oracle statements that carry no correction row in
`.ufo/waves/round-30/preregistration.json` → C1.claimed_work:

- `SCORECARD.md:41` — the carried-debt line asserting the pins verify `file=yes`.
  Oracle item `SCORECARD.md:Q:4a6f7c911e:o0`, class Q, span `file=yes`, W `ea72c3ea`.
- `SCORECARD.md:901` — the round-20 C2 table cell asserting `declared2048 = captured training2048`.
  Oracle item `SCORECARD.md:Q:422b431349:o0`, class Q, span `declared2048 = captured training2048`, W `92b14625`.

## The rewrite

Both rewrites keep every factual component of the original line and drop only the unquoted, unretained
literal that the oracle flagged. Evidence used, read from committed objects only:

- For line 41: `registry/history/latest.tsv` at W `ea72c3ea` carries
  `ufo-fsd-thetick  DEAD  connection-refused  -  34113  yes` and
  `ufo-fsd-local-helper  DEAD  connection-refused  -  34113  yes` (columns: id, verdict, reason,
  served_model, port, file_match). The file check **did** match; the string `file=yes` was simply never
  committed in that spelling (`tools/kama-probe.sh:858` at W writes `file=${EV_FMATCH[i]}`, and the probe
  contains the bytes `file=missing`, not `file=yes`). New wording:
  "the pins' file check matched at the relocated tree but nothing listens on 34113" — same fact, no
  unquoted literal.
- For line 901: `.ufo/waves/round-20/c2/measure-reference.json` at W `92b14625` (and the retained
  `.ufo/waves/round-20/runs/0957ce61/gguf-measure.stdout`) record `"gguf_declared_context_length": 2048`,
  `"models_meta_n_ctx_train": 2048`, `"training_context_comparison": "equal"`. New cell wording names those
  three retained fields instead of the bare `declared2048 = captured training2048` literal.

## Clone, commit, diff

Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlEditInPlace` (from `/home/vgpnk/Projects/shokunin/kama-shokunin`),
checked out at the lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c`.

Mutant commit: `98544b06ee203f46d7165f356c2c3e53991274da`, retained as `refs/heads/ctl` in the clone.
Author identity: `kama-r30-control CtlEditInPlace <control@kama-shokunin.local>` (local to the clone; no
lane or fleet git write was performed).
Parent: `52ac3af8614b5040ba5e17f17a2c7af029706e6c`.

Full diff: `policy.diff` in this directory. Two lines of `SCORECARD.md`, one file, no appended section:

```
@@ -38,7 +38,7 @@
-`ufo-fsd-local-helper`) read `DEAD` — the pins verify `file=yes` at the relocated
+`ufo-fsd-local-helper`) read `DEAD` — the pins' file check matched at the relocated
@@ -898,7 +898,7 @@
-... model version3, tensors48, KV19, declared2048 = captured training2048; props256 informational |
+... model version3, tensors48, KV19, declared context 2048 = captured training context 2048 (`gguf_declared_context_length` 2048, `models_meta_n_ctx_train` 2048, `training_context_comparison` equal); props256 informational |
```

SHA-256 of `SCORECARD.md`: base `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`,
mutant `6ecb3bd1e09f644969aeaa0ea9d7337f213fcdbeb5dc7fd85971d07aebfc9a8b`.

## Counter invocations

The LANE counter was used unmodified, from the lane path, against the clone. Its bytes are unchanged:
`sha256 c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`, matching the frozen digest and
the digest recorded inside both receipts.

Mutant:

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlEditInPlace \
  --tip 98544b06ee203f46d7165f356c2c3e53991274da \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlEditInPlace/counter.json
```

Same-clone baseline at the untouched lane tip (for attribution of the delta):

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlEditInPlace \
  --tip 52ac3af8614b5040ba5e17f17a2c7af029706e6c \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlEditInPlace/baseline-tip.counter.json
```

Summary lines verbatim:

    statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only False valid_corrections 11 false_corrections 0 unresolved 141 met False tip 98544b06ee20
    exit=0

    statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
    exit=0

`met` from the mutant receipt (`counter.json`): **false**. Exit status of both runs: 0.

## What the measurement shows

The mutant reproduces the item's expected outcome exactly: `append_only False`, `unresolved 141`, `met False`.

| receipt field | baseline @ tip | mutant |
|---|---|---|
| statements / extracted / oracle_items / oracle_unbound | 141 / 69 / 72 / 0 | 141 / 69 / 72 / 0 |
| mismatched_at_base | 13 | 13 |
| append_only | True | **False** |
| correction_rows / valid_corrections / false_corrections | 11 / 11 / 0 | 11 / 11 / 0 |
| unresolved | 2 | **141** |
| met | false | false |

Two mechanisms, both visible in the frozen counter's source:

1. **Append-only violation.** `append_only` is `tip_sc.startswith(base_sc)` (count-c1.py:530). Rewriting
   bytes in the middle of `SCORECARD.md` means the tip blob no longer starts with the base blob, so
   `append_only` flips to False. The counter's response to a non-append-only tip is not "ignore the edit" but
   "treat every statement as unresolved": `unresolved_ids = sorted(sids)` when `append_only` is False
   (count-c1.py:542-546). 141 statements, all unresolved.
2. **The rewrite does not reach the statements being judged.** `extract()` reads `repo.blob(BASE, fname)`
   (count-c1.py:192) and the oracle binding reads `repo.blob(BASE, fname)` for the line text
   (count-c1.py:456). The counter's population is the **base** text, and the two oracle Q items are bound to
   base lines 41 and 901 with the base spans `file=yes` and `declared2048 = captured training2048`. Editing
   those lines in the tip leaves the judged statements untouched: both oracle mismatches survive the rewrite
   verbatim in the mutant receipt — `SCORECARD.md:Q:4a6f7c911e:o0` (line 41) and
   `SCORECARD.md:Q:422b431349:o0` (line 901), both still `q:no-artifact`. So the rewrite changes nothing that
   the counter measures as fixed, and it costs the append-only property.

The 11 pre-existing round-29 `SA29:` rows are inherited from the lane tip and remain valid
(`valid_corrections 11`, `false_corrections 0`); the 2 baseline-unresolved ids are exactly the two oracle
Q items the arm edited.

**Is this arm a genuine shortcut?** No — it is a genuine *failure mode*, not a shortcut. The counter rejects
it, and rejects it twice over: the two statements it claims to repair still fail, and the whole file stops
being append-only. A shortcut would be a policy that turns the predicate green by gaming the counter
(for example by pasting the `holds` values, or by keying observed cells off the statement token). This arm
attempts to make the false lines stop reading as false and instead makes the measurement strictly worse
(unresolved 2 → 141). It is the correct negative control for the "rewrite history instead of disclosing"
shortcut: it demonstrates that the frozen counter's append-only rule catches an in-place repair of base
lines, and that such a repair does not reach the base-anchored population it is judged against.

## Bounds observed

- The lane is read-only for this seat: `git status` in `/home/vgpnk/Projects/shokunin/kama-shokunin` shows no
  modified tracked file; the lane's own `SCORECARD.md` still carries the original `file=yes` line (SHA-256
  `73a3270dc89b529300f73f380a658c42938d58e5dbb44e46ef885162eb000083`). The only lane writes are the new
  untracked files in this control directory.
- The frozen counter was never edited; its digest was re-verified after both runs.
- No correction rows, no correction section, and no `SA30:` rows were appended by this arm — that is the
  policy, and it is why `correction_rows` stays at the lane tip's inherited 11.
- Tools: no installs were needed. The arm used only `/usr/bin/python3` (3.14.8) and `/usr/bin/git`
  (2.56.0), both pre-installed system binaries — no pacman, no `uv tool`, no `npx`, no new downloads.
- All evidence was read from committed objects; no live server was started and no model was called.

## Artifacts in this directory

- `counter.json` — mutant receipt (tip `98544b06ee20`).
- `counter.out` — mutant summary line and exit status.
- `baseline-tip.counter.json` — same-clone baseline receipt (tip `52ac3af8614b`).
- `baseline-tip.counter.out` — baseline summary line and exit status.
- `policy.diff` — the full diff of the mutant commit against the lane tip.
- `REPORT.md` — this file.

Report: .ufo/waves/round-30/controls/CtlEditInPlace/REPORT.md
