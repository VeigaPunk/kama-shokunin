# ConfirmM11 — verdict report

**Item:** C1 (calibration) first falsifier — base statement
`SCORECARD.md:P:17a7db7c81:0` (SCORECARD.md line 1375 at base 2aa46e24).

**Verdict: `confirmed-false`**

## Evidence

1. **Writing revision.** `git blame -L 1375,1375 --line-porcelain
   2aa46e24 -- SCORECARD.md` names W = `d183ec572a5eed5bedeb4bce0da02707d51df3dd`
   (committer-time 1792740053, summary "round-27: w1a3 wave evidence …"). Matches
   the receipt's W.
2. **Statement text (line 1375):** `request text (round-26
   \`count-c1.py:384\`), a base-tree shortcut met it 12/12,` — class P token
   `count-c1.py:384`.
3. **P rule applied by hand (counter docstring):** path as written, not starting
   `../`/`/`/`~`/URL; `blob W:path` must exist. `git cat-file -e
   d183ec57:count-c1.py` → `fatal: path 'count-c1.py' does not exist …`, exit 128.
   **The path as written does not exist at W → `p:absent` is the correct observed
   value → the statement was false at the revision that wrote it.**
4. **Intended referent.** `git ls-tree -r W` shows the only `count-c1.py`
   at W is `.ufo/waves/round-26/count-c1.py` (plus round-27 counter copies).
   At W that blob has 423 lines (≥ 384), and line 384 is exactly
   `c["e_not_echoed"] = sig not in req_bytes` — the raw-bytes echo check the
   sentence describes. So the pointer is real but omitted the
   `.ufo/waves/round-26/` directory prefix. The same shorthand
   `count-c1.py:384` is used consistently in corpus/lessons/round-26-verifier-spotcheck.md
   (lines 109, 234) and round-27 evidence; in corpus lessons the lane
   convention is a bare filename (the lane repo root), which is wrong when the
   file lives under `.ufo/waves/round-26/`.
   The round-26 counter was introduced at commit `a4a159c` (round-26 freeze).

**Cause (≤ 25 words):** SCORECARD line 1375 omits the `.ufo/waves/round-26/`
prefix of the referenced counter path, so the path as written does not exist at W.

## Severity and findings

No counter defect found: the counter emitted `p:absent`, which hand-applying the
frozen P rule reproduces. The statement is genuinely false at W (overreach:
pointer missing its directory prefix). This is a first falsifier of the base
receipt (pre-data), not a correction row.

- High: none.
- Medium: the SHONEN/SCORECARD convention of referencing
  `.ufo/waves/round-<n>/…` files by bare filename (`count-c1.py:384`) is
  systematically ambiguous; round-29 correction rows should use the full path
  to avoid re-introducing this failure class (cf. lessons/round-26-verifier-spotcheck.md
  lines 220-247).

## Commands run (all read-only, under timeout, in the lane repo)

See `verdict.json` → `commands` (each with exact output, trimmed to 40 lines).

## Residual risk / verification gaps

- The Q-class alternative referent (quoted output artifact) does not apply: the
  statement is class P and refers to a code location, not a quoted measurement.
  The echo-measurement claim itself ("met it 12/12") is a separate C-class
  statement elsewhere, not this sid.
- I verified only line 1375's statement; other base statements were not touched.
- No tools installed; no writes outside the item's output dir; no git writes.
