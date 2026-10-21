## Round 21 — report landing audit and symlink-aware install identity

Assigned axes remain operability 8 + calibration 7 (lowest non-retired assigned
axis). Calibration below saturation 8 means no stagnation waiver. Last capability
entry round 20; with no row entering this round the stagnation window reads 1 of 4
at round end.

**C1 calibration, 7 → 7 (improved-bounded; 7 → 8 only if the non-author closure admits it):**
mechanical report-landing audit. `tools/report-landing-audit.py` (stdlib) checks fleet
reports `.ufo/reports/round-N/kama.md` for four defect kinds: unresolved-full-hash,
landed-unresolved, landed-omitted, landed-section-missing. Append-only
`registry/report-landing-errata.tsv` records corrections; the reports themselves are
not edited. The audit binds tokens and the `## Landed changes` commit set; it does not
bind prose. Scope bound per R19 erratum (SCORECARD.md:844-848).

**C2 operability, 8 → 8 (delta 0), capability-shaped:** symlink-aware install identity.
`install_links()` and `install_links_sha256` in `tools/kama-llamacpp-live.py`;
`install_tree()` untouched. Gate `tests/llamacpp-live/check-receipt.py` validates
install_links (optional for legacy receipts), recomputes the digest, requires each chain
to end at a pinned regular member, and accepts `--expect-install-links-sha256`.
Closes the R19 TreeCap debt: retargeting a soname symlink left `install_tree_sha256`
unchanged. Grid `tests/llamacpp-live/install-links-grid.py` mirrors the real tree
`~/.local/opt/llama-b11755` in copies only.

### Round-21 measured results — committed tree `<L1 measured commit>`

Work commit `a29bb84abbb8b4d328f5970a89e448330a3a42ac`. Official measurement run by the
L1 only; the scout measurements below are advisory and are **not** official.

| Claim | Axis/score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 report landing | calibration 7 → 7 (delta 0), improved-bounded | raw defects **9** (unresolved-full-hash r20 ×1; landed-omitted r10 ×1, r18 ×3, r20 ×4), uncorrected **9 → 0**, errata unmatched 0, invalid 0; selftest **15/15** | `python3 tools/report-landing-audit.py --no-errata` (exit 1, uncorrected 9); `python3 tools/report-landing-audit.py` (exit 0, corrected 9, uncorrected 0, status clean); `python3 tools/report-landing-audit.py --selftest` (exit 0, cases 15 failed 0) | `runs/<L1 tree>/landing-*.stdout` `<placeholder>` |
| C2 install-links identity | operability 8 → 8 (delta 0) | frozen arm (install_tree at 7a6bc911) link **0/9**; current arm link **9/9**; regular 2/2 and type 1/1 both arms; null 0/1 both arms; back-compat `install_tree_sha256` equal (true) | `python3 tests/llamacpp-live/install-links-grid.py --arm current` (exit 0, `summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass`); `--arm frozen` (exit 1, expected: `link=0/9 … status=fail`); `--selftest` (exit 0, cases 12 failed 0); `python3 tests/llamacpp-live/check-receipt.py --selftest` (exit 0, `9 VALID and 1 NOT-EVALUATED … 90 mutations + unreadable case rejected`) | `runs/<L1 tree>/links-*.stdout` `<placeholder>` |

Round-21 report gate, run by the L1 on the committed report:
`python3 tools/report-landing-audit.py --report 21=<path-to-round-21-kama.md>`.
Round 21 `required=1`: the report's `## Landed changes` must cite `a29bb84…` (probe on a
draft lacking it: exit 1, `UNCORRECTED landed-omitted a29bb84…`).

Other axes held: freshness 8, coverage 9, depth 7, adjacency 7.

Sources (scouts' new rows, opened this round): `<placeholder: S066–S0NN with verbatim
quote <=25 words, section/line, URL, access date 2026-10-21, revision>`. Census before:
rows 65 (tier A 62, C 3; mined 52, queued 6, rejected 7), `validate` exit 0. L1 writes
`corpus/SOURCES.md`.

### capabilities: no append this round (install-links-identity not admitted as a row)

Recommendation: no row. The R19 install-tree pin (sixth pin, SCORECARD.md:828-835) added
none; install-links is the same pin family, and its demonstration runs only on a mirrored
copy of the tree, not a live receipt. [INFERENCE: judgment under AXES.md §Capabilities.]
If the closure rules it a repertoire capability, append:

| Name | What it can do | Demonstration | First-working round |
|---|---|---|---|
| install-links-identity | pin soname symlink chains of a llama.cpp install tree (basename → readlink text) so a retargeted, dangling, looping or outside-pointing link changes the receipt identity or fails the gate; regular-file pin unchanged | `python3 tests/llamacpp-live/install-links-grid.py --arm current` exit 0 (`link=9/9 … status=pass`) with `--arm frozen` exit 1 as counter-control | 21 |

### Round-21 trend verdicts (placeholder)

| Trend axis | Verdict | Evidence |
|---|---|---|
| quality (depth, freshness, operability) | `<L1 verdict>` | §Round-21 measured results |
| discernment (calibration) | `<L1 verdict>`; no non-author reviewer on record unless the closure supplies one | closure record `<placeholder>` |

### Planned (next round, 1–3 claims)

`<L1 chooses>`. Named R20 frontier still open: historical crash-as-kill outside the
15-cell set, broader receipt-header minimization, K05/other-engine serving evidence.
Symlinked soname identity is now C2 above. No next round is started here.
