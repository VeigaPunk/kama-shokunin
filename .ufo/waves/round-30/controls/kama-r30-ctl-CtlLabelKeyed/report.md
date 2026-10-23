# Round-30 C1 pre-freeze control — CtlLabelKeyed

Seat: kama-r30-ctl-CtlLabelKeyed. Clone: `/fast/scratch/hyaku/kama-r30/ctl/kama-r30-ctl-CtlLabelKeyed`,
checked out at lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c`.
Counter (lane, untouched): `.ufo/waves/round-30/count-c1.py`, sha256
`c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` (matches freeze).

## Policy

Append one correction row per false base statement (the 13 statements with
`mismatched_at_base`) whose **observed** cell echoes that statement's own token text —
i.e. rows keyed by the label `SA29:<sid>` but carrying the statement text instead of the
value the counter prints. Rows generated from the committed base receipt
`.ufo/waves/round-30/c1/before/c1-base.json` (13 entries), appended under a new
`## Round 29 — self-assessment corrections` heading at the end of SCORECARD.md.

## Forecast

All 13 rows have wrong observed values (`token != "q:no-artifact"|"p:absent"`), so
`false_corrections == 13` and `met False`. Anticipated additionally: 11 of the sids already
carry valid round-29 rows in the lane-tip SCORECARD, so those 11 rows are flagged `duplicate`
rather than `wrong-observed`.

## Diff

`policy.diff` (21 insertions, SCORECARD.md only, append-only); block sha256
`a32e41b83de8cdb9e4fbeeb9d9237e9f1352956e7ca4e2505e4326e59aff5055`.

```
+## Round 29 — self-assessment corrections
+
+Control arm CtlLabelKeyed: one row per base statement that does not hold, observed cell
+echoing the statement's own token text (label-keyed, not value-correct).
+
+| Statement | Arm | Observed |
+|---|---|---|
+| `SA29:SCORECARD.md:Q:f4c42debcc:0` | token-echo | snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2 |
+| `SA29:SCORECARD.md:Q:f4c42debcc:2` | token-echo | RESULT pass=24 fail=0 |
+| `SA29:SCORECARD.md:P:980355388a:0` | token-echo | MISSION.md:29 |
+| `SA29:SCORECARD.md:Q:4f8083e30a:0` | token-echo | rows=50 resolved=48 terminal=2 unresolved=0 |
+| `SA29:SCORECARD.md:P:312b3e69b1:0` | token-echo | round-17-verifier-spotcheck.md:217–221 |
+| `SA29:SCORECARD.md:Q:0ccd533544:0` | token-echo | required=3 found=0 verified=0 missing=3 |
+| `SA29:SCORECARD.md:Q:4c5d902830:0` | token-echo | required=3 found=3 verified=3 missing=0 mismatch=0 |
+| `SA29:SCORECARD.md:Q:f1021c03db:0` | token-echo | baseline=VALID members=3 rejected=0/3 |
+| `SA29:SCORECARD.md:Q:a7e98b1030:0` | token-echo | baseline=VALID rejected=3/3 |
+| `SA29:SCORECARD.md:P:1c6c1f3e4c:0` | token-echo | .ufo/reports/round-25/kama.md:120-129 |
+| `SA29:SCORECARD.md:P:17a7db7c81:0` | token-echo | count-c1.py:384 |
+| `SA29:SCORECARD.md:Q:4a6f7c911e:o0` | token-echo | `file=yes` |
+| `SA29:SCORECARD.md:Q:422b431349:o0` | token-echo | declared2048 = captured training2048 |
```

Candidate commit: `61cad7677e44732a300e98e69962012128eadd76` (local identity
`CtlLabelKeyed <ctl@local.invalid>`).

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/kama-r30-ctl-CtlLabelKeyed \
  --tip 61cad7677e44732a300e98e69962012128eadd76 \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/kama-r30-ctl-CtlLabelKeyed/counter.json
```

## Measurement

Pristine (clone at lane tip `52ac3af8`, before mutation), exit 0:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```

Mutated (candidate `61cad767`), `counter.out`, exit 0:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 0 false_corrections 13 unresolved 26 met False tip 61cad7677e44
```

Restored (clone returned to `52ac3af8`), `restored.out`, exit 0:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b
```

`met` from `counter.json`: **False**. `false_corrections` detail: 11 `duplicate`, 2
`wrong-observed` (the two genuinely uncorrected statements, `SCORECARD.md:Q:4a6f7c911e:o0`
and `SCORECARD.md:Q:422b431349:o0`).

## Restoration evidence

- SCORECARD.md sha256 (pristine → mutant → restored):
  `b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd` →
  `4e5e054ccfd39b30be08eabfc0945e45fd86545b66ad6b3e13172c0aa3dade99` →
  `b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd`
- Clone HEAD restored to `52ac3af8614b5040ba5e17f17a2c7af029706e6c`; `git status --porcelain` empty.
- Restored counter output is byte-identical to the pristine summary line.

## Verdict

Arm refused (mutant killed): `met False`, `unresolved 26 ≠ 0`. Not a genuine shortcut.
Echoing a statement's own token text never equals the printed observed value, so exact-string
matching rejects every row; worse, 11 of the 13 sids already carry valid round-29 rows and the
counter's duplicate rule also strips those sids from `valid`, so the arm turns a state with
`valid_corrections 11 / unresolved 2` into `valid_corrections 0 / unresolved 26`. Label-keyed
row placement is insufficient: the observed cell must equal the value the counter prints, and
rows for already-corrected sids are self-harming.

No tools installed or updated.
