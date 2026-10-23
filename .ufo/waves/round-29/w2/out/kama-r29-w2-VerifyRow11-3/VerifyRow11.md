# VerifyRow11 — correction row 11, sid `SA29:SCORECARD.md:P:17a7db7c81:0`

Seat: kama-r29-w2-VerifyRow11-3 · 2026-10-23 · All commands read-only git plumbing on
/home/vgpnk/Projects/shokunin/kama-shokunin; the counter was NEVER executed (item constraint honored).
Frozen-counter integrity: `sha256sum .ufo/waves/round-29/count-c1.py` →
`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — matches the frozen hash.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:P:17a7db7c81:0", "verdict": "confirmed-false",
 "observed_value": "p:absent", "W": "d183ec572a5eed5bedeb4bce0da02707d51df3dd",
 "row": "SCORECARD.md@513eba3ba51a142c9936553e3a85918345eb5c4c:1464",
 "last_cell_matches_observed": true}
```

## (1) Base statement located

`git --no-replace-objects show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md`, line 1375:

```
request text (round-26 `count-c1.py:384`), a base-tree shortcut met it 12/12,
```

- sha256 of the exact line bytes (no trailing newline; `sed -n 'l'` confirms no hidden
  whitespace/control chars): `17a7db7c8138a083a8a3d03be047f69fc53117e685131ec1c5186c92e36861d1`
  → prefix **`17a7db7c81`** = the sid's third field exactly.
- The line content occurs exactly once in base SCORECARD.md and 0 times in base SHONEN.md,
  so the plain (non-`#`-suffixed) sid unambiguously names base SCORECARD.md:1375.
- Note on sid semantics: per the frozen extractor (`lsha = hashlib.sha256(line.encode()).hexdigest()[:10]`),
  the sid's third field is the **line-content hash**, not W. The correction row's W cell
  (column 5, `d183ec57`) is the blame revision — verified next.

## (2) Writing revision W via blame — matches the row's W cell

`git --no-replace-objects blame --line-porcelain 2aa46e2… -L 1375,1375 -- SCORECARD.md`:

```
d183ec572a5eed5bedeb4bce0da02707d51df3dd 1375 1375 1
author kama-shokunin <kama@shokunin.local>  author-time 1792740053 (-0300)
summary round-27: w1a3 wave evidence (34 seats); … SCORECARD, README, LOG round-27 entries
```

W = `d183ec572a5eed5bedeb4bce0da02707d51df3dd`, prefix `d183ec57` — equals the row's W cell.

Token/rule hand-application (RE_P on the line): exactly one P-class match, `count-c1.py:384`,
first match ⇒ index `:0` ✓. Char before the match is a backtick (passes the negative
lookbehind `(?<![\w./~:-])`), char after `384` is a backtick (passes `(?![\w])`); path
`count-c1.py` is extension-eligible and lane-relative (`in_lane` true). `end = max(384) = 384`.

## (3) P-class rule applied by hand at W — statement is FALSE

Rule (counter docstring + `check()`): the blob `W:count-c1.py` must exist AND have
≥ 384 lines; holds iff both conjuncts pass.

- `git --no-replace-objects cat-file -e d183ec57…:count-c1.py` →
  `fatal: path 'count-c1.py' does not exist in 'd183ec57…'` (rc 128);
  `git ls-tree --name-only d183ec57 | grep -i count-c1` → no entries. **First conjunct fails
  ⇒ `check()` returns `(False, "p:absent")`. Statement is false at W.**
- Row's supporting explanation verified: `W:.ufo/waves/round-26/count-c1.py` exists at W with
  423 newline-terminated lines; its line 384 exists (`c["e_not_echoed"] = sig not in req_bytes`).
  So the pointer's mistake is exactly the bare file name (lane file lives under
  `.ufo/waves/round-26/`); with the correct path the pointer would hold. The counter's P rule
  is path-literal (root-relative blob lookup), so the statement as written is false at W.

Hand-derived observed value: **`p:absent`** (from `return False, f"{cls.lower()}:absent"`).

## (4) Correction row's last cell equals the observed value exactly

Tip `513eba3ba51a142c9936553e3a85918345eb5c4c` SCORECARD.md:1464 — the 11th and final row
under `## Round 29 — self-assessment corrections` (heading at :1443, the last `## ` heading,
so the row sits inside the counter's collection window):

```
| SA29:SCORECARD.md:P:17a7db7c81:0 | SCORECARD.md:1375 | P | `count-c1.py:384` | d183ec57 | bare file name; the lane file is .ufo/waves/round-26/count-c1.py (line 384 exists there) | p:absent |
```

- Last cell `p:absent` == hand-derived observed value `p:absent` (exact; `corrections()`
  strips backticks, none present). ✓
- sid occurs exactly once at tip (grep count 1 — no duplicate). ✓
- Auxiliary context (outside the per-row validity rule): tip SCORECARD.md begins with the
  base SCORECARD.md bytes (byte-exact prefix compare, N = base blob size) ⇒ append-only True,
  so this valid correction actually cancels the statement's unresolved status.

## Residual risk / gaps

- I did not run the counter (per item constraint); the receipt's global numbers (statements 69,
  mismatches 11, valid 11) are out of my slice and re-verified by the L1.
- No other caller/diagnostic surface exists for this row beyond the counter's parsing, which I
  hand-replicated from the frozen source. No defects found in this slice.
- Tooling: no tools installed (git + coreutils sufficed); no pacman use.

## Report-path deviation

The item's `Report:` trailer names `.ufo/waves/round-29/w2/VerifyRow11.md` (lane-root relative),
but the hard write bounds allow writes ONLY inside
`.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyRow11-3/`. Both `report.md` and this
`VerifyRow11.md` (identical content) are written inside the bounded directory; the L1 may move
a copy to the trailer path if it wants that layout. Nothing outside my output directory or
/tmp scratch was written; the lane Git index and all lane files are untouched.
