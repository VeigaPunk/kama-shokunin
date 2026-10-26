# K1Cheat — shortcut attack on C1 (round 44)

**Verdict: C1's counter is cheatable. Eight scored variants, spanning six distinct defects, make
`tools/round44-release-recheck-audit.py` print `met=True` without re-verifying any row's `teaches`
statement; the cheapest is a 91-row ledger plus one appended heading line, with zero anchor-text
comparisons and zero flag lines.** The frozen counter was not modified (sha256 still
`87503e18e47dae6fa0414cf24d988f2a44ffa61d422db62c82cad3c24d8218d2`, matching the preregistration).

All work happened in `git clone --shared` fixture clones under
`/fast/scratch/hyaku/kama-r44/K1Cheat/` at `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40`; every
clone's toplevel was verified before the first commit, and commits used inline
`-c user.name=K1Cheat -c user.email=k1cheat@localhost`. The lane, fleet repo and upstream clone
were only read.

Invocation used throughout (`$C` = fixture clone, `$U` = shared llama.cpp clone):

```
python3 tools/round44-release-recheck-audit.py --repo "$C" --tip "$(git -C "$C" rev-parse HEAD)" --upstream "$U"
```

Builder: `K1Cheat/build_cheat.py` (modes `drift`, `reword`, `scatter`). It reads only the frozen
population (`population`/`cited` from the counter itself), `git rev-parse` blob ids and line
counts. No `teaches` cell is read; no anchor statement is judged.

---

## F1 — `drifted` carries no evidence at all (85/91 rows, met=True)

Counterexample: every one of the 85 changed rows labelled `drifted`, `release_lines` = `1-1`
repeated to match the pair count, note = a self-incriminating filler string, and the ledger still
passes.

```
$ python3 .../round44-release-recheck-audit.py --repo "$C" --tip f3d6387f... --upstream "$U"
pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=0 reworded=0 drifted=85 removed=0 flags_missing=0 section=1 met=True
EXIT=0
```
(`K1Cheat/receipt-v1-drift.out`.)

The ledger row is literally:

```
S001  tools/server/README.md  c0fd78626...  b11889  ec82db00... 8e27e37b... 1  1-1  1-1  drifted  K1Cheat: mechanically flagged drifted at b11889, no anchor text compared
```
(`K1Cheat/ledger-v1-drift.tsv`.)

Counter cause — `tools/round44-release-recheck-audit.py:239-242`:

```python
    if v == "drifted":
        if len(note) < 20:
            return False, "note too short"
        return not all(r is None for r in rr), "drifted rule"
```

There is no text comparison, no relation between `release_lines` and `pin_lines`, and the note is
never read against anything. `drifted` is the cheapest verdict to fabricate and it *inverts* C1:
the preregistration's C1 statement is "81 `holds` = the cited text relocated verbatim"; a
100 %-drifted ledger satisfies the same predicate (`unverified=0`) while asserting the opposite.

**Impacted axis:** freshness (C1). **Skips:** the entire re-verification; the drift claim itself.

**Smallest safe correction:** require a machine witness for `drifted` — at least one pin-range
first line must be absent from the release file's line set, the paired release range must stay
within `MOVE` lines of its pin range, and the note must quote ≥16 characters of the missing pin
line. (Tested below; refuses F1 entirely, keeps the honest draft's `holds` untouched.)

## F2 — cheapest cheat: `holds-reworded` + one heading line, zero flags, met=True

```
$ python3 .../round44-release-recheck-audit.py --repo "$C" --tip bc3cbaeb... --upstream "$U"
pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=0 reworded=85 drifted=0 removed=0 flags_missing=0 section=1 met=True
EXIT=0
```
(`K1Cheat/receipt-v9-heading-only.out`; the whole change set is
`corpus/SOURCES.md | 2 +` and `registry/release-recheck-b11889.tsv | 92 +++`, see
`K1Cheat/diff-v9-heading-only.stat`.)

The two moves:

1. `holds-reworded` is forced by **one** differing pair. `check_row` computes
   `eq = [excerpt(pin) == excerpt(release)]` per pair and accepts when `not all(eq)`
   (`:238`). The paired release range is unconstrained by anything else. So for a row whose cited
   block is byte-identical at b11889, the builder pairs the last pin block with an unrelated
   release line and the verdict flips to `holds-reworded`:
   `S001 … pin_lines 1-1, release_lines 2523-2523, holds-reworded` (`K1Cheat/ledger-v5-reworded.tsv`).
   Measured on the full ledger: **66 of 85** `holds-reworded` rows have *every other pair
   text-equal* — the label is manufactured by the injected pair alone.
2. `section=1` needs only `any(SECTION in x and x.startswith("#"))` (`:314`); nothing has to be
   under the heading, because no video row needs a flag when no row is `drifted`/`removed`
   (`:319-322`). One appended line is enough:

```
$ printf '\n## Round-44 release re-verification\n' >> corpus/SOURCES.md
```

**Impacted axes:** freshness. **Skips:** the rewording judgement entirely (`limits` in the
preregistration already admits "drift notes are read by attack seats, not by the counter" — here
even the *verdict* is manufactured, not just the note).

**Smallest safe correction:** for `holds-reworded`, require each pair to be near its pin range
(`|r0-p0| <= MOVE`) and require the note to quote ≥12 characters of the *release* excerpt of a
differing pair. Filler text cannot quote release bytes; a cheater must then read the site.

## F3 — `holds` is a bag of lines: order, contiguity and locality are unchecked

```
pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=65 reworded=0 drifted=0 removed=0 flags_missing=0 section=1 met=True
```
(`K1Cheat/receipt-v6-scatter.out`, `K1Cheat/ledger-v6-scatter.tsv`.)

`holds` is `return all(eq)` (`:233-234`): each pin range must textually equal *its* release range,
but the release ranges need not be ordered, contiguous or even near. The builder splits the cited
coverage into minimal ≥20-non-whitespace windows and matches each window *anywhere* in the release
file. Concrete row:

```
S141  tools/server/server-schema.cpp  …  pin_lines 44-44,45-45   release_lines 46-46,43-43   holds
```
— the release side runs **backwards** (46 then 43) and the counter accepts it as "cited text
relocated verbatim". Measured over the 65 `holds` rows: 20 non-contiguous release block sets, 64
with a release offset different from the pin offset, and **15 with strictly descending ranges**
(S110, S141, S143, S144, S149, S151, S154, S157, S158, S166, S167, S168, S169, S171, S173).

**Impacted axis:** freshness. **Skips:** relocation-contiguity — the property that makes
"verbatim relocation" mean anything.

**Smallest safe correction:** require release ranges to be strictly increasing
(`r[i+1][0] > r[i][1]`) and each pair within `MOVE` of its pin range. Do **not** require
contiguity or equal widths: measured false positives on the honest draft are S035 (two distant
anchors `479-490,1258 → 479-490,1346`) and S112 (`919-934 → 1007-1021`, a 15→16-line window).

## F4 — `removed` never checks that the path was removed

```
$ python3 .../round44-release-recheck-audit.py --repo "$C" --tip 3e9c0865... --upstream "$U"
pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=0 reworded=0 drifted=84 removed=1 flags_missing=0 section=1 met=True
EXIT=0
```
(`K1Cheat/receipt-v7-removed.out`.)

```
S108  tools/server/server.cpp  …  pin_lines 159-186  release_lines -  removed  K1Cheat: anchor text absent from b11889, labelled removed
$ git -C /fast/scratch/hyaku/kama-r44/shared/llama.cpp cat-file -e d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server.cpp && echo EXISTS
EXISTS
```

The rule (`:243-251`) checks `note`, `all(r is None for r in rr)` and that the pin's first line is
absent from the release text — it never compares `release_blob` with `-`. A live file whose anchor
text was rewritten can therefore be declared `removed`, and `removed` is the strongest claim in the
vocabulary.

**Smallest safe correction:** `if rb != "-": return False, "removed but path present at release"`.

## F5 — flag scoping is heading-bounded: pre-existing text counts as a round-44 flag

Two variants both reach `flags_missing=0`:

* **V1** (honest position, real bullets): 85 bullet lines `- Sxxx drifted at b11889` plus, per
  knowledge file, **one** single line listing every id —

  ```
  b11889 re-verification flags (round 44): S180 S181 S182 S183 S184 S185 S186 S187 …
  ```

  one line satisfies every row that names that file (`:329` only needs `sid in line and RELEASE in
  line`). The bullet text itself may be reduced to a bare id: 85 lines of just `- Sxxx` (no
  release string, no verdict word) plus knowledge lines of just `b11889 S180 S181 …` also give
  `pop=91 … drifted=85 flags_missing=0 section=1 met=True` (`K1Cheat/receipt-v10-bare-bullets.out`).
* **V2** (heading harvest, zero *SOURCES* flag lines — the knowledge lines from V1 stay): move
the section heading above the registry table and demote `## Registry` to prose; every registry row is then a `sec_lines` entry (`:306-313`), so
  every id is "listed in SOURCES section" without writing a single round-44 line.
  `pop=91 … drifted=85 flags_missing=0 section=1 met=True`
  (`K1Cheat/receipt-v2-heading.out`; `K1Cheat/diff-v2-heading-flags.diff` is cumulative from the
freeze, so it also shows V1's knowledge flag lines).

V2 has a side cost (deleting `## Registry` would trip `scripts/sources-census.sh validate` E12, per
`corpus/lessons/round-31.md` §Mistakes row 4); the bare-bullet variant above has none, because the
flag rule never asks the flag line to carry the release or the verdict.

**Smallest safe correction:** a flag line must contain `RELEASE` and exactly one id:
`RELEASE in x and re.findall(r"\bS\d{3,}\b", x) == [sid]`. That refuses the table harvest (registry
rows do not name b11889) and the all-ids line.

## F6 — deleting a used-by entry *removes* the flag requirement

`corpus/knowledge/chat-adapter-outcomes.md` was the sole flag carrier for 12 drifted ids. Deleting
it (67 lines) left the counter unchanged at `met=True`:

```
$ python3 .../round44-release-recheck-audit.py --repo "$C" --tip 8d1a6686...
pop=91 rows=91 valid=91 unverified=0 unchanged=6 holds=0 reworded=0 drifted=85 removed=0 flags_missing=0 section=1 met=True
 corpus/knowledge/chat-adapter-outcomes.md | 67 -------------------------------
```
(`K1Cheat/receipt-v3-delete.out`, `K1Cheat/diff-v3-knowledge-delete.stat`.)

Cause, `:327-329`: `body = show(...); if body is None: continue`. The counter rewards removing the
evidence it is supposed to check.

**Smallest safe correction:** treat a missing used-by path as a failure
(`missing += 1`), not a skip.

## F7 — the seat-level fragment gate accepts the same thing

`tools/check-fragment.py` reports `VALID` for **all 91 rows** of the zero-evidence
`holds-reworded` ledger (`K1Cheat/fragment-check-v5.out`, `K1Cheat/fragment-v5.tsv`):
`pop=91 … valid=91 … met=False` followed by 91 `VALID Sxxx` lines. The gate only prints `VALID`
when the counter emits no detail for the key, and the counter's only row-level details are
range/blob/verdict checks — so a fabricated verdict is invisible at seat level. A merge built from
such fragments would be indistinguishable per row.

## Latent — three population rows have no cited-line constraint at all

`S001`, `S015`, `S059` carry no line numbers in `source`/`anchor`, so `cited()` yields empty
`strong`/`weak` and `check_row` applies **no coverage rule** (`:216-223`). Their `pin_lines` may be
any range with ≥20 non-whitespace characters (`1-1` in every receipt above). They are 3 of the 6
`TODO` rows in the frozen draft, i.e. the cheapest rows to fake. Second latent hole at the same
place (`:217`): `strong = {n for n in strong if n <= len(ptext)}` silently drops citations that
point past the pin file's EOF, so a row citing a line number beyond the file loses its coverage
constraint altogether. No frozen population row exploits this today (I verified all 91 cite in-file
lines), but a future SOURCES row can neutralise its own anchor this way without touching the
counter.

---

## Proposed counter amendment (tested, never applied to the frozen file)

`K1Cheat/PROPOSED-counter-amendment.diff` + the full proposed text
`K1Cheat/counter-amended-PROPOSAL.py`. Rules added: `drifted` witness (missing pin line, quoted in
the note, near pairing), `holds-reworded` near pairing + a ≥12-char verbatim quote of the release
side, `holds` strictly-increasing + near pairing, `removed` requires `release_blob == "-"`, flag
lines must carry `RELEASE` and exactly one id, and a missing used-by entry is a failure.

Two-direction result (all in `K1Cheat/amended-on-*.out`):

| tree | frozen counter | amended counter |
|---|---|---|
| honest draft (81 holds, 4 unchanged, 6 TODO) | valid=85 holds=81 unverified=6 | **valid=85 holds=81 unverified=6** (only the same 6 TODO rows invalid — first 6 details identical) |
| V1 mass drift | met=True | valid=6 (unchanged rows only), met=False |
| V5/V9 reworded + heading | met=True | valid=6, met=False |
| V6 scatter holds | met=True | valid=56, holds=50 (the 50 are genuinely ordered/near/equal) |
| V7 false `removed` | met=True | valid=6, met=False |
| V10 bare-id bullets | met=True | valid=6, met=False |

`MOVE = 2000` is not arbitrary: the honest draft's largest accepted relocation is 1049 lines
(`S121`, `5803 → 6852`), so 400 would have produced 5 false positives. The equal-width rule was
dropped after S112 failed it; the contiguity rule was dropped after S035 failed it. Every rule that
survived was validated in both directions before being proposed.

## Environment / cleanup

No tool installs, no `pacman`, no service changes, no subagents. All fixture clones, the amended
counter and the measurement dumps lived in `/fast/scratch/hyaku/kama-r44/K1Cheat/` and were removed
(`rm -rf`) after the receipts were copied; `/tmp` was never used for evidence.

## Files written

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Cheat.md`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/K1Cheat/` —
`build_cheat.py`, `counter-amended-PROPOSAL.py`, `PROPOSED-counter-amendment.diff`,
`receipt-v1-drift.out`, `receipt-v2-heading.out`, `receipt-v3-delete.out`,
`receipt-v5-reworded.out`, `receipt-v6-scatter.out`, `receipt-v7-removed.out`,
`receipt-v9-heading-only.out`, `receipt-v10-bare-bullets.out`, `amended-on-honest-draft.out`,
`amended-on-v1.out`, `amended-on-v5.out`, `amended-on-v6.out`, `amended-on-v7.out`,
`amended-on-v10.out`, `ledger-v1-drift.tsv`,
`ledger-v5-reworded.tsv`, `ledger-v6-scatter.tsv`, `ledger-v7-removed.tsv`, `fragment-v1.tsv`,
`fragment-v5.tsv`, `fragment-check-v1.out`, `fragment-check-v5.out`, `diff-v2-heading-flags.diff`,
`diff-v3-knowledge-delete.stat`, `diff-v9-heading-only.stat`, `v{1,5,6,7}-clone-log.txt`.
