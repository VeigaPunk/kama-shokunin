# VerifyBaseMapping — kama round-29 w2 (seat report)

**Verdict: PASS.** The preregistration base is the true round base; the frozen counter's extractor
maps the 11 correction rows verbatim to base `SCORECARD.md` lines. No defect found in the mapped slice.

## 1. Base identity

| Check | Command / evidence | Result |
|---|---|---|
| Freeze commit parent | `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %P' -1 827d136546b85059a984b34970f5b493d9a71290` → `827d1365…71290 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` (sole parent) | PASS |
| Prereg `base` field | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json` → `"base": "2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d"` | PASS |
| Base on master | `git merge-base --is-ancestor 2aa46e24… master` → exit 0 (`ANCESTOR_OK`) | PASS |
| Freeze carries prereg | `git log --format='%H %s' -- .ufo/waves/round-29/preregistration.json` → single commit `827d136… round-29: C1 freeze (calibration): counter, preregistration, base receipt, census start; before any seat` | PASS |
| Round chain | parents: `35b90184 → 827d136`, `513eba3 → 35b90184`; so `2aa46e24 → 827d136 (freeze) → 35b90184 (controls) → 513eba3 (data)` | PASS |
| Counter frozen bytes | `sha256sum .ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, equals prereg `counter_sha256` | PASS |

## 2. The 11 statement lines at base exist verbatim

The data commit `513eba3ba51a142c9936553e3a85918345eb5c4c` appends exactly 11 correction rows under
`## Round 29 — self-assessment corrections` (SCORECARD.md diff, `@@ -1441,0 +1442,23 @@` — first content
line after base EOF at 1441, append-only placement). All 11 rows name `SCORECARD.md` lines. Full set of
"line at base" values (completes the item's "20, 211, 740, 824, 834, 1349, 1375 etc."):

| sid | base line | class | W |
|---|---|---|---|
| SCORECARD.md:Q:f4c42debcc:0 | 20 | Q | ea72c3ea |
| SCORECARD.md:Q:f4c42debcc:2 | 20 | Q | ea72c3ea |
| SCORECARD.md:P:980355388a:0 | 192 | P | 1e41928a |
| SCORECARD.md:Q:4f8083e30a:0 | 211 | Q | 40660352 |
| SCORECARD.md:P:312b3e69b1:0 | 740 | P | c6dc46fa |
| SCORECARD.md:Q:0ccd533544:0 | 823 | Q | 7229fa95 |
| SCORECARD.md:Q:4c5d902830:0 | 824 | Q | 7229fa95 |
| SCORECARD.md:Q:f1021c03db:0 | 833 | Q | 7229fa95 |
| SCORECARD.md:Q:a7e98b1030:0 | 834 | Q | 7229fa95 |
| SCORECARD.md:P:1c6c1f3e4c:0 | 1349 | P | 7f84cd0e |
| SCORECARD.md:P:17a7db7c81:0 | 1375 | P | d183ec57 |

Two independent verifications, both 11/11 PASS (script: `/tmp/verifybasemap-r29-w2/check_base_mapping.py`,
importing the frozen `count-c1.py` module so the sid/line derivation is the extractor's own code):

1. **Frozen-extractor derivation** — `extract(repo, f)` over `FILES = ("SCORECARD.md", "SHONEN.md")` at
   `BASE` yields **69 unique statements**; every row sid is a member with matching `line`, `class`,
   `token`, and `W` (W taken from the extractor's `git blame --line-porcelain BASE` call).
2. **Raw blob check** — `git show 2aa46e24:SCORECARD.md` (via `repo.blob`, 1441 lines): each named line
   exists; `sha256(line)[:10]` equals the sid's embedded line hash (`f4c42debcc`, `980355388a`,
   `4f8083e30a`, `312b3e69b1`, `0ccd533544`, `4c5d902830`, `f1021c03db`, `a7e98b1030`, `1c6c1f3e4c`,
   `17a7db7c81`); each row's statement token is a verbatim substring of its line (lines 20, 192, 211,
   740, 823, 824, 833, 834, 1349, 1375 printed verbatim in the run log).

Cross-checks with the prereg/receipt record:
- My extraction's class mix `{C: 27, H: 2, N: 2, P: 10, Q: 25, T: 3}` (sum 69) equals the prereg
  `before.by_class` and the base receipt's `statements 69`.
- Frozen module's own `corrections()` on the `513eba3` blob: exactly 11 rows, 11 unique sids, all 11 are
  base-statement sids, no duplicates, heading byte-exact, observed values `q:no-artifact` × 7 /
  `p:absent` × 4 — mapping-level agreement with `valid_corrections 11 false_corrections 0`.
- SHONEN.md at base exists (12 lines) and contributes 0 statements (checklist prose without
  lane-path:line pointers or quoted measurement spans) — consistent with all 69 coming from
  SCORECARD.md; not a mapping defect.

## Method and bounds

All git access read-only (`log`, `show`, `merge-base --is-ancestor`, `cat-file`, `blame` via the frozen
module at `BASE`). No lane file, index, jj state, or fleet repo touched. Scratch confined to
`/tmp/verifybasemap-r29-w2/`. No tools installed (none needed) — pacman guard respected.

## Residual risk / gaps

- I verified the **mapping** (sid → base line verbatim), not the **observed values**: whether
  `q:no-artifact`/`p:absent` are what `check()` truly prints at each W is the counter-rerun slice
  (RerunCounter seats / L1 C1 re-verification). The 11 statements may still hold while being falsely
  "false" — that risk is intentionally out of this seat's scope.
- W attributions come from the frozen extractor's own blame call; I did not run `blame` independently
  outside it. Raw line bytes were independently hash-verified, but the W→line binding is taken from the
  extractor under test.
- The `f4c42debcc` line-20 pair relies on the extractor's k-index (Q matches k=0 and k=2 on one line);
  membership + token match in the frozen extractor's output confirms the indexes, but only via the same
  code under test.

Copies: this file also at `.ufo/waves/round-29/w2/out/VerifyBaseMapping/report.md` (seat copy, identical).
