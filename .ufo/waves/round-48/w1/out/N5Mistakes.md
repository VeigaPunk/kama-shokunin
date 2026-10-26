# N5Mistakes — round 48 frontier step-3 sweep

Verdict: **4 routed items from closures 44–47 are lost or were closed without capture (F1 dropped after deferral, F2 closed-without-capture and recurred, F4 never addressed, F5 never tracked); 2 named sub-items of r46-D3 never became a row (F3); 2 more closed-without-capture (F6, F7). No spot-check disagreement went uncaptured — closures 44–47 agree with the Gate on every sampled admit/reject. All r47-D1..D9 items are dispositioned in the r48 preregistration `routed` block (not lost).**

Full analysis with per-item routing ledger and proposed rows: `.ufo/waves/round-48/w1/out/N5Mistakes/sweep.md`.

## Evidence (commands, outputs, file:line)

Method: compared each routed item in `corpus/lessons/round-{44..47}-verifier-spotcheck.md` §Routed defects against `## Mistakes` rows in `round-{44..47}.md` (and the r48 lesson draft) and KQ rows in `corpus/QUALITY.md` (KQ58–KQ71). Lane tip `380bcdff9c8af06997c482f6eb03db926a794a2b`; reads via a scratch clone.

- **F1 r45-D1 dropped.** Source `round-45-verifier-spotcheck.md:146`; deferral `round-46.md:12` ("No reader was written or run"); absent from r46 closure routed list (`round-46-verifier-spotcheck.md:137-142`), r47 lesson (`round-47.md:14`), r47 closure (`round-47-verifier-spotcheck.md:97-106`), r48 preregistration `routed` keys (`['r47-D1'…'r47-D9']`). `git grep -n 'r45-D1' 380bcdff -- corpus/lessons/` → 0 matches. KQ65 does not encode the known-data/pre-score constraint.
- **F2 r44-D2 recurred.** Source `round-44-verifier-spotcheck.md:109`; fixed r45 (tip receipts @ `82b5e9d3`, r45 closure §2 lines 96–102) with no Mistakes row; class recurred as r47-D9 (`round-47-verifier-spotcheck.md:105`), now captured in r48 draft row 2 (`round-48.md:29`).
- **F3 r46-D3 sub-items.** Source `round-46-verifier-spotcheck.md:139` (row-or-drop demanded). r47 row 1 (`round-47.md:45`) covers the family/tally, names neither "reworded witnesses" nor V1Code F1–F4; `git grep -l 'V1Code' 380bcdff -- corpus/lessons/` → only round-44/46 docs.
- **F4 base-unresolved producer.** `round-43-verifier-spotcheck.md:110`, `round-44-verifier-spotcheck.md:112`, `round-44.md:56` ("producer not addressed"). At tip: `git grep -l base-unresolved 380bcdff -- tools/ scripts/` → none; file exists only as round-43 wave artifacts.
- **F5 frontier rows.** `round-45-verifier-spotcheck.md:149`, `round-44-verifier-spotcheck.md:112`, `round-44.md:37`; `git grep -n 'floating-series' 380bcdff -- corpus/lessons/` → only the r45 closure; r45/r46 C1 populations did not include them.
- **F6 r44-D3 / F7 r46-D4**: closed with verified fixes (`round-45.md:19`; `round-47.md:14` + closure `unknown=0`), no row/criterion.
- **F8 operator/L0**: open since rounds 35–43 (`round-44-verifier-spotcheck.md:113`, `round-45-verifier-spotcheck.md:150`, `round-46-verifier-spotcheck.md:143`, `round-47-verifier-spotcheck.md:106`); operator-owned.
- **r47-D1..D9**: dispositioned in r48 preregistration `routed`; r48 lesson draft rows 2/3 carry D9/D1 (draft is untracked in the lane workspace — `git status --porcelain` shows `?? corpus/lessons/round-48.md`).

Proposed rows (class, evidence, captured-by, fix able to fail) for F1–F7 are in sweep.md. No tools were installed (read-only analysis; no tooling authorization used).

Absolute paths written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/N5Mistakes/sweep.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/N5Mistakes.md
