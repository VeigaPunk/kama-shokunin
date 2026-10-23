# VerifyRow05 — hand-verification of correction row 5 (sid `SA29:SCORECARD.md:P:312b3e69b1:0`)

Seat: kama-r29-w2-VerifyRow05 · 2026-10-23 · Counter run on the lane tree: **none** (all checks hand-derived per item).
Scratch: `/tmp/vr05-VerifyRow05/` (base blob, data-commit diff). No tools installed; no pacman. No lane file mutated.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:P:312b3e69b1:0", "verdict": "confirmed-false", "observed_hand_derived": "p:absent", "row_last_cell": "p:absent", "row_valid": true}
```

## Evidence

**Frozen counter integrity.** `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — matches the declared frozen hash.

**(1) Base statement located.** Base commit `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, `SCORECARD.md` line 740 (the line the correction row names, cell 2 `SCORECARD.md:740`):

```
	improved** (`round-17-verifier-spotcheck.md:217–221`), superseding the pending
```

(repr: `'improved** (`round-17-verifier-spotcheck.md:217–221`), superseding the pending'`; en dash U+2013.)

**(2) Writing revision W.** `git blame 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d -L 740,740 --line-porcelain -- SCORECARD.md` →
`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` ("round-18: classify missing observations and bind detector survivor claims").

*Format note (no defect):* the sid's third field is **not** W's prefix. The frozen counter (count-c1.py:178-182,225-226) computes it as `lsha = hashlib.sha256(line.encode()).hexdigest()[:10]`, a line-content hash. Hand recomputation of that hash over line 740's UTF-8 bytes gives exactly `312b3e69b1` — the sid identifies this line ✓ (k=0 ✓: exactly one `RE_P` match on the line). W's prefix appears separately in the row's cell 5, `c6dc46fa`, and matches blame W ✓ (also matches the frozen receipt `.ufo/waves/round-29/before/c1-base.json` record for this sid: `"W": "c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d"`).

**(3) P rule applied by hand at W** (rule, count-c1.py docstring: "the blob `W:path` exists and has at least max(L, M) lines (fail: p:absent, p:beyond-eof)"). Token `round-17-verifier-spotcheck.md:217–221` → path `round-17-verifier-spotcheck.md` (bare name, passes `in_lane`), required end = max(217,221) = 221.

- `git cat-file -e c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d:round-17-verifier-spotcheck.md` → `fatal: path 'round-17-verifier-spotcheck.md' does not exist in 'c6dc46fab…'` (exit 128). Blob absent ⇒ per code (`if data is None: return False, "p:absent"`) observed = **`p:absent`** — not `p:beyond-eof`, since the blob itself is missing.
- Context confirming the row's rationale: the real file at W is `corpus/lessons/round-17-verifier-spotcheck.md` (`cat-file -e` exit 0), 276 lines ≥ 221 — the statement fails only because the pointer omits the `corpus/lessons/` prefix. The pointer rule is path-literal, so the statement is **false at W**.

**(4) Correction row vs hand-derived value.** Data commit `513eba3ba51a142c9936553e3a85918345eb5c4c` appends the correction table under heading `## Round 29 — self-assessment corrections` (tip `SCORECARD.md` line 1443). Our row is the 5th of the 11 appended rows (tip line 1458), exactly one row for this sid:

```
| SA29:SCORECARD.md:P:312b3e69b1:0 | SCORECARD.md:740 | P | `round-17-verifier-spotcheck.md:217–221` | c6dc46fa | bare file name; the lane file is corpus/lessons/round-17-verifier-spotcheck.md | p:absent |
```

Last cell = `p:absent` = my hand-derived observed value, exact string ✓. Row cells 2/3/4/5 (line 740, class P, token with en dash, W prefix `c6dc46fa`) all independently verified above ✓.

Sanity cross-checks (counter-wide claims, not re-run, only touched incidentally): `append_only` — tip `SCORECARD.md` starts with the base bytes: True (computed directly from the two blobs).

## Residual risk / gaps

- I did not re-run the counter (per item), so row-to-row properties (all 11 rows, `valid_corrections 11 false_corrections 0`) rest on the frozen receipts; this seat only certifies row 5.
- The sid-format item phrasing ("confirm W's prefix matches the sid") does not match the actual sid derivation (line-content hash, not commit prefix); both identifications were verified independently, so no impact on the verdict.
