# MutC2Key — C2 correction-key collapse probe (round 31, wave 2)

```text
RESULTS

[exit 0] $ git cat-file -t 382d11b2107d335705875da1a4d889b074bd6fa6
         commit

[exit 0] $ git clone --quiet --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin lane \
            && git -C lane checkout --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 \
            && git -C lane rev-parse HEAD
         382d11b2107d335705875da1a4d889b074bd6fa6

[exit 0] $ sha256sum lane/.ufo/waves/round-31/count-c2.py
         2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  lane/.ufo/waves/round-31/count-c2.py

[exit 0] $ /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane \
            --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --list --out receipts/pristine.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
       |   C1: p1 line 266 p1:no-revision
       |   C1: p1 line 320 p1:no-revision
       |   C1: p1 line 379 p1:no-revision
         (three failing rows are SCORECARD.md rounds 11/12/13, Claim cell `C1`, class p1, identical observed string)

[exit 0] $ /usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
            --tip 382d11b2… --list --out receipts/frozen-lane.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
         (identical to the clone run: no clone artifact)

[tool: edit] inserted `| CR31:11:C1:p1 | C1 | p1 | p1:no-revision |` into the corrections table
[exit 0] $ git -c user.name=mut -c user.email=mut@local commit -qam "scratch: one C1/p1 correction (collapse probe)"
         de77715b2545b4ad35420dd88076db8c1d36462f
[exit 0] $ /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-one --tip HEAD --list --out receipts/frozen-one.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True tip de77715b2545
       |   corr CR31:11:C1:p1 row=C1 class=p1 ok=True
         ONE correction row naming row cell `C1` marks all three round-distinct rows resolved; unresolved 0; met False -> True.
         `--list` still prints the three `C1: p1` problem lines (the listing has no per-row resolution column).

[tool: edit] inserted `| CR31:11:C1:p1 | C1 | p1 | p1:no-revision |`, `| CR31:12:C1:p1 | C1 | p1 | p1:no-revision |`,
            `| CR31:13:C1:p1 | C1 | p1 | p1:no-revision |`
[exit 0] $ git -c user.name=mut -c user.email=mut@local commit -qam "scratch: three round-distinct C1/p1 corrections"
         69a4fd451e69fab15225e3bdcc99afc3081530ac
[exit 0] $ /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-three --tip HEAD --list --out receipts/frozen-three.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False tip 69a4fd451e69
       |   corr CR31:11:C1:p1 row=C1 class=p1 ok=False
       |   corr CR31:12:C1:p1 row=C1 class=p1 ok=False
       |   corr CR31:13:C1:p1 row=C1 class=p1 ok=False
         The frozen key makes three separate dispositions unexpressible: `len(by_key[key]) == 1` fails for each.

[tool: edit] inserted a byte-copy of the existing round-11 correction as `| CR31:11:C2:p1 (copy) | C2 | p1 | p1:no-revision |`
[exit 0] $ git -c user.name=mut -c user.email=mut@local commit -qam "scratch: literal copy of round-11 C2 correction"
         7a018316f26ebbe9cda8d3aebbfde8915b9a2ccb
[exit 0] $ /usr/bin/python3 lane/.ufo/waves/round-31/count-c2.py --repo lane-literal --tip HEAD --list --out receipts/frozen-literal.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 9 false_corrections 2 unresolved 4 append_only True met False tip 7a018316f26e
       |   corr CR31:11:C2:p1 row=C2 class=p1 ok=False
       |   corr CR31:11:C2:p1 (copy) row=C2 class=p1 ok=False
         Copying the existing round-11 correction literally (row cell `C2`) does not touch the three; it poisons the
         round-11 C2 correction instead. There is no pre-existing `CR31:11:C1` row at the tip to copy, so the M1 row
         was authored with the failing row's actual cell `C1` and class `p1` (the item's intended shape).

[exit 0] $ cp frozen counter -> counter-roundkey.py; rekey corrections on (round, row, class), round from the id prefix `CR31:<N>:`
[exit 0] $ sha256sum counter-roundkey.py lane/.ufo/waves/round-31/count-c2.py
         730f2844bab5940ef0354ad2bb56e75df9e723257daecb4c20839eb89384ea54  counter-roundkey.py
         2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  lane/.ufo/waves/round-31/count-c2.py
[exit 0] $ diff -u lane/.ufo/waves/round-31/count-c2.py counter-roundkey.py  (3 hunks)
       | +RE_CID = re.compile(r"^CR31:(\d+):")   # MUTATION: round carried by the correction id prefix
       | +    def corr_round(c): ...            # id prefix; else infer only when one population row matches
       | -        key = (c["row"].strip(), c["class"])
       | +        key = (corr_round(c), c["row"].strip(), c["class"])
       | -    problem_by_key = {(p["row"], p["class"]): p for p in problems}
       | +    problem_by_key = {(p["round"], p["row"], p["class"]): p for p in problems}
       | -    unresolved = [p for p in problems if (p["row"], p["class"]) not in valid_map]
       | +    unresolved = [p for p in problems if (p["round"], p["row"], p["class"]) not in valid_map]
         All other bytes identical (row/path/digest logic, append_only, predicate, thresholds untouched).

[exit 0] $ /usr/bin/python3 counter-roundkey.py --repo lane --tip 382d11b2 --list --out receipts/roundkey-pristine.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
         (mutation is behavior-identical on the pristine tree: 10 valid corrections stay valid)

[exit 0] $ /usr/bin/python3 counter-roundkey.py --repo lane-one --tip HEAD --list --out receipts/roundkey-one.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 2 append_only True met False tip de77715b2545
       |   corr CR31:11:C1:p1 row=C1 class=p1 ok=True
         (the collapsed correction now resolves only round 11; rounds 12 and 13 stay unresolved; met stays False)

[exit 0] $ /usr/bin/python3 counter-roundkey.py --repo lane-three --tip HEAD --list --out receipts/roundkey-three.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 13 false_corrections 0 unresolved 0 append_only True met True tip 69a4fd451e69
       |   corr CR31:11:C1:p1 row=C1 class=p1 ok=True
       |   corr CR31:12:C1:p1 row=C1 class=p1 ok=True
       |   corr CR31:13:C1:p1 row=C1 class=p1 ok=True
         (three separate correction rows resolve 3/3; 10 pre-existing corrections unchanged)

[exit 0] $ /usr/bin/python3 counter-roundkey.py --repo lane-literal --tip HEAD --list --out receipts/roundkey-literal.json
       | rows 30 base_mismatched 13 exempt 1 valid_corrections 9 false_corrections 2 unresolved 4 append_only True met False tip 7a018316f26e
         (duplicate-detection behaviour preserved by the mutation)

[exit 0] $ cd /home/vgpnk/Projects/shokunin/kama-shokunin && git rev-parse HEAD; sha256sum .ufo/waves/round-31/count-c2.py;
            git diff --quiet -- SCORECARD.md; git status --porcelain
       | HEAD addeb57c5d717785a94105a2e36cc8a76940fb6c   (was bda324bb at probe start; a concurrent wave seat landed addeb57c)
       | counter 2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  .ufo/waves/round-31/count-c2.py
       | SCORECARD worktree-vs-HEAD: identical
       | ?? .ufo/waves/round-31/c1/…  ?? .ufo/waves/round-31/c2/…  ?? .ufo/waves/round-31/c3/…  ?? .ufo/waves/round-31/w2/…  (untracked receipts only; no tracked file modified)

[exit 0] $ git merge-base --is-ancestor 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD && echo "382d still ancestor of HEAD"
         382d still ancestor of HEAD
[exit 0] $ git diff --stat 382d11b2..HEAD -- SCORECARD.md .ufo/waves/round-31/count-c2.py
         (empty — SCORECARD.md and the frozen counter are byte-identical at addeb57c, so the probe readings hold at the current tip)
```

CONTEXT: seat `KamaR31.MutC2Key` (mutation tester, leaf). Claim served: **C2 (calibration)** —
"the correction key's collapse is the counter's defect, not a population artifact." Measured tip
`382d11b2107d335705875da1a4d889b074bd6fa6` (dispatch tip; still an ancestor of lane HEAD `addeb57c`
at the end of this run). Frozen counter `.ufo/waves/round-31/count-c2.py`, sha256
`2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe` (re-hashed at start and end:
unchanged). No tracked lane file was edited; all mutants are copies. No tool was installed or upgraded.

FINDING: collapse reproduced yes; round-qualified key resolves 3/3 yes — one correction row with row cell `C1` / class `p1` silently resolves the three round-distinct failing rows (valid 11, unresolved 0, met False→True) under the frozen `(row, class)` key, three separate rows with that same key are all marked false, and a `(round, row, class)` key derived from the `CR31:<N>:` id prefix accepts the three separately (valid 13, unresolved 0) while keeping the pristine 10 corrections valid and duplicate-detection intact.

LIMITS:
- Population is the 30 `Claim`-table rows of SCORECARD.md at `382d11b2` (re-checked byte-identical at `addeb57c`); the probe does not re-derive other files' tables, other rounds, or the frontmatter/section structure.
- The mutant counter is an instrument probe in my scratch dir, not a proposed lane patch. The round for each correction is derived from the `CR31:<round>:` id prefix by my choice; a correction id without that prefix is resolved only when exactly one population row matches its row cell, else counted false. A different round-derivation rule would move the counts.
- Neither counter reads the prose of a correction, only the `row`, `class` and `observed` cells (and, in the mutant, the id prefix); "met True" under any key is still a counter reading, not proof that the underlying evidence exists.
- The M3 literal copy shows only that copying the existing `C2` row poisons; the item's phrase "existing round-11 C1 correction" has no literal referent at the tip (the table holds `CR31:11:C2:p1`, no `CR31:11:C1`), so M1's row was authored rather than copied.
- No live server, model, or fixture was involved; all reads are committed git objects. Nothing here judges whether C2 is met, which fix the lane should adopt, or whether the collapse harm outweighs the frozen predicate's stability.

RESTORATION: nothing to restore — the lane's `count-c2.py` was never opened for write (sha256 `2d06f38d…` before and after), SCORECARD.md is worktree-identical to HEAD, and the three scratch commits live only in `/tmp/kama-r31w2/MutC2Key/{lane-one,lane-three,lane-literal}`. Mutated counter preserved at `.ufo/waves/round-31/w2/out/MutC2Key/counter-roundkey.py` (sha256 `730f2844…`) and `/tmp/kama-r31w2/MutC2Key/counter-roundkey.py`.

ARTIFACTS (all under `.ufo/waves/round-31/w2/out/MutC2Key/`): `counter-roundkey.py`,
`count-c2-frozen-copy.py`, `HASHES.txt`, `run-transcript.sh`, `receipts/transcript.txt`,
`receipts/{pristine,frozen-lane,frozen-one,frozen-three,frozen-literal,roundkey-pristine,roundkey-one,roundkey-three,roundkey-literal}.json`,
matching `.out` files, `receipts/rows-verbatim.txt`, `receipts/lane-untouched.txt`,
`receipts/exits.txt`.
