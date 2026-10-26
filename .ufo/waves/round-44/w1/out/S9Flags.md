# S9Flags — round 44 C1 flag placement (prep, not a verdict)

**Verdict: PREP COMPLETE — 50 (id, entry) flag positions mapped for the 38 of 91
population ids that have a `corpus/knowledge/*.md` used-by; the drafted sentence and
its placement score `flags_missing=0` against the frozen counter on 31 simulated
drifted rows, but 53 population ids have no `corpus/knowledge` used-by at all and one
used-by entry never states one of its own rows (S186), so the flag surface C1's
counter checks covers only part of the population's used-by set.**

Seat: leaf (S9Flags), no subagent dispatch. Lane and fleet untouched; every write is
under `.ufo/waves/round-44/w1/out/S9Flags/` plus this report.

## 1. What was produced

| file | content |
|---|---|
| `w1/out/S9Flags/flag-map.tsv` | `id  entry  line_of_claim`, 50 rows = every (population id × existing `corpus/knowledge/*.md` used-by) pair |
| `w1/out/S9Flags/placement-notes.tsv` | same rows + block kind, enclosing block span, whether the id already sits on the claim line |
| `w1/out/S9Flags/flag-placement-check.tsv` | the above + the line each drafted flag actually lands on after insertion + the draft ledger's verdict and release lines for that id |
| `w1/out/S9Flags/claim-lines.txt` | the claim line text at freeze `77d1bbf5`, per pair (what the flag sentence refers to as "the statement above") |
| `w1/out/S9Flags/build-flag-map.py` | builder (reads the preregistration, SOURCES.md and entries through `git show 77d1bbf5:`, never the working tree) |
| `w1/out/S9Flags/run-flagtest.py` | throwaway-clone exerciser for the drafted flags |
| `w1/out/S9Flags/flagtest-c1.out` | frozen counter run, one flag line per id: `flags_missing=0` |
| `w1/out/S9Flags/flagtest-c1-combined.out` | frozen counter run, one combined line for S180–S191: `flags_missing=0` |
| `w1/out/S9Flags/flagtest-knowledge.diff` | the 11 entries with the drafted flags inserted (insertion points) |
| `w1/out/S9Flags/flag-leg-predicate.out` | per-pair re-derivation of the counter's flag predicate: 50/50 satisfied |

## 2. The template

Exactly as specified, `<what changed>` left open:

```
Release recheck (round 44, b11889): S### <what changed, release lines> - the statement above holds at b11755 (704366d76), not at b11889.
```

Two variants the L1 needs (both exercised only for the placement leg, not for wording):

- **S186 (and any row whose used-by entry states no such claim):** "the statement above"
  is false for S186 — the entry has no S186 statement (§5). Use
  `Release recheck (round 44, b11889): S186 <what changed, release lines> - this entry states no S186 line; the frame holds at b11755 (704366d76), not at b11889.`
- **several ids in one block:** one line may carry several ids;
  `Release recheck (round 44, b11889): S180 <…> S181 <…> … S191 <…> - the statements above hold at b11755 (704366d76), not at b11889.`
  satisfies the counter for each id (`flagtest-c1-combined.out`: `flags_missing=0`).
  Use it where a block carries ≥4 ids (`chat-adapter-outcomes.md` 12, `context-capacity.md`
  errata 5); otherwise one line per id.

`<what changed, release lines>`: the draft ledger already gives the release-side line
numbers per id (`registry/…b11889` draft column `release_lines`); `flag-placement-check.tsv`
column `draft_release_lines` reproduces them beside each anchor, e.g. S190 → `49`, S186 → `1535`.

## 3. Coverage of the frozen population (91 ids)

Command: `build-flag-map.py` (exit 0, `pairs=50 rows=50 files=11`).

- 91 ids in `claims[0].population`.
- **38 ids** have ≥1 used-by that is a `corpus/knowledge/*.md` file existing at the tip → **50 pairs** over 11 entries: `context-capacity.md` (14 rows), `served-identity-crosswalk.md` (4), `runtime-health-surface-matrix.md` (4), `llamacpp-loading-lifecycle.md` (8), `endpoint-identity.md` (3), `chat-adapter-outcomes.md` (12), `gguf-runtime-compatibility-boundary.md` (1), `gguf-declared-identity.md` (1), `echo-discriminating-counters.md` (1), `serving-metrics-crosswalk.md` (1), `context-capacity-engine-sides.md` (1).
- **53 ids have no such used-by** — the flag surface the frozen counter reads
  (`tools/round44-release-recheck-audit.py:322-330`) is empty for them:
  - `S059`: used-by is `—` (no used-by at all) → no knowledge-entry and no other home;
  - 51 ids cite `SKILL.md` (17 of them also `registry/error-signatures-r26.json`, 34 also
    `registry/request-field-outcomes-r28.json` + `corpus/lessons/round-28.md`); `S138`
    cites `corpus/lessons/round-27.md` only. None of those paths matches
    `corpus/knowledge/[\w.\-]+\.md`, so the counter never checks them and the drafted
    templates were not placed there. 51 ∪ {S138} ∪ {S059} = the 53 missing ids (verified
    set relation: r26-set ⊂ SKILL-set, r28-set ⊂ SKILL-set).

All 11 entries are byte-identical at `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40` and in the
working tree (`git show <freeze>:<entry>` vs file, 11/11 SAME), so every line number is
valid at the tip the counter reads.

## 4. Placement rule (what the L1 must do, and why)

The claim anchor is almost never a whole block: of the 50 anchors, 4 are table rows
(`runtime-health…:14`, `serving-metrics…:14`, `served-identity…:27`,
`gguf-runtime…:19`), 9 are list items, 37 are paragraph interiors. Inserting the flag line at the anchor splits the table/list. The
rule that was exercised: **insert the flag as its own paragraph after the enclosing
block (the next blank line), before the following heading**, i.e.
`flag-placement-check.tsv` column `flag_line_after_insert`. Examples from
`flagtest-knowledge.diff`: `runtime-health-surface-matrix.md` flag lands at 20 (after the
table, before `## What this does not establish`); `served-identity-crosswalk.md:27`
(table, block 27-29) lands at 31; `chat-adapter-outcomes.md` block 23-50 → flags 52-74;
`context-capacity.md` errata block 258-262 → flags 282-290.

Where the id is **not** on the claim line (`id_on_claim_line=0`, 16 pairs) the flag is
necessarily a new line naming the id — that is fine for the counter (`\bS###\b` + `b11889`
on one line) but the sentence must then say which entry line it refers to.

## 5. Findings (defects found while mapping; nothing edited in place)

**F1 — `corpus/knowledge/chat-adapter-outcomes.md` states 11 of its 12 rows. S186 is missing.**
S186's row (`corpus/SOURCES.md:198`) teaches the frame
`throw std::invalid_argument("logprobs is not supported with tools + stream")` at
`server-common.cpp:1517`. The entry cites `:1519` and `:1521` only
(`corpus/knowledge/chat-adapter-outcomes.md:29-32`).
Show: `grep -n '1517' corpus/knowledge/chat-adapter-outcomes.md` → no output (exit 1);
`grep -n '1519\|1521' …` → `31`, `32`.
Effect: if S186 is judged drifted or removed, the flag required by
`round44-release-recheck-audit.py:326-330` can only be a line the L1 invents; the
"statement above" in the template has no referent. Proposed fix (full text, to be
inserted after line 32, inside the `logprobs` bullet):

```
  The tools-plus-stream combination is refused by its own frame
  `logprobs is not supported with tools + stream` (`server-common.cpp:1517`, S186);
  [INFERENCE] the trigger the message names is read from the message, not from a
  condition this entry read.
```

**F2 — the population's flag surface is 38/91 ids.** 53 ids (F3 below for the exact
split) have no `corpus/knowledge` used-by, so C1's statement "drifted or removed
statements are flagged in their used-by entries" is only checkable for 38 ids; the
counter's predicate (`flags_missing`) is silent for the rest. `S059` has no used-by at
all. Not fixed (preregistration and counter are frozen); reported so the drift notes do
not over-claim. The SOURCES round-44 section is the only home those rows have, and it
is L1-authored.

**F3 — split of the 53:** 1 id (`S059`) used-by `—`; 51 ids used-by `SKILL.md`
(+`registry/error-signatures-r26.json`); 34 ids used-by `registry/request-field-outcomes-r28.json`
+ `corpus/lessons/round-28.md`; `S138` used-by `corpus/lessons/round-27.md`.
(Overlapping sets — several ids cite both a registry file and a lesson.)

**F4 — anchors that are the only id-bearing line are headers, not claims.**
`endpoint-identity.md` carries S035 only on its section source line 184 (claim paragraph
200-216); `context-capacity-engine-sides.md` carries S479 only on its `source:` header
line 1 (claim sentence at 21). Flag placement recorded at 184 and 21 respectively; both
need a *new* line, and the sentence should name the claim line, not "above".

**F5 — rows that cannot need a flag this release.** `S015`, `S106`, `S131` (and
`S128`, `S129`, outside the knowledge map) have `changed=0` at b11889
(`.ufo/waves/round-44/c1/draft-ledger.tsv`). The counter's verdict table admits
`drifted` only for `changed 1` and `removed` only when every release element is `-`
(absent path), so neither verdict can apply to a byte-identical file; their placements
are documented but inert. Derived from the frozen docstring
(`tools/round44-release-recheck-audit.py:36-42`) and from the code path at `:316-317`;
not executed.

**F6 — priorities for the L1.** Rows that are `changed=1` **and** still `TODO` in the
draft — the ones whose verdict the L1 must read and which will trigger flags — are
`S001` (3 entries), `S037` (4 entries), `S043` (1), `S108` (1). `<= 9 flag lines`.
`S001`/`S037`/`S043`/`S108` release-side ranges are `-` in the draft, i.e. their pinned
text did not relocate verbatim.

## 6. Checks actually run (all in scratch, `S=/fast/scratch/hyaku/kama-r44/S9Flags`)

1. `python3 .ufo/waves/round-44/w1/out/S9Flags/build-flag-map.py` → `pairs=50 rows=50 files=11`, exit 0.
2. Freeze-vs-worktree equality of the 11 entries: 11/11 `SAME`.
3. `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/clone`;
   `git -C $S/clone rev-parse --show-toplevel` → `$S/clone` (asserted inside
   `run-flagtest.py` before the first commit); `git -C $S/clone checkout --detach 77d1bbf5…`
   → HEAD `77d1bbf5…`; `git cat-file -t` on `77d1bbf5…` and `9d9cc93e…` → `commit`.
4. `python3 run-flagtest.py $S/clone <out>` → 31 draft rows whose verdict was `holds`
   flipped to `drifted` (note: "S9Flags flag-placement test: treated as drifted so the
   frozen counter exercises this row's used-by flag"), all 50 drafted flags inserted,
   `corpus/SOURCES.md` given the `## Round-44 release re-verification (b11889 = d854d98b)`
   section, committed **inside the clone** (`-c user.name=S9Flags -c user.email=s9flags@fixture.invalid`),
   then the frozen counter at tip `f39c2e0654ff548bc1274bb494549607a28340bf`:
   `pop=91 rows=91 valid=85 unverified=6 unchanged=4 holds=50 reworded=0 drifted=31 removed=0 flags_missing=0 section=1 met=False`, exit 1.
   `unverified=6` = exactly the 6 `TODO` rows the draft never resolved (S001, S015, S037,
   S043, S059, S108) — untouched by this seat; **no** `not flagged in <entry>` detail.
5. Combined-line variant of F-§2 for S180–S191, tip `715519fdaba22760cc99828b1b3c8121e8bcbc04`:
   same summary line, `flags_missing=0` (`flagtest-c1-combined.out`).
6. Per-pair re-derivation of the counter's flag predicate over the modified clone:
   `pairs=50 satisfied=50 missing=0` (`flag-leg-predicate.out`).
7. `git diff` of the exercised clone: 11 entries + `corpus/SOURCES.md` +
   `registry/release-recheck-b11889.tsv`, 228 insertions, no other path
   (`flagtest-knowledge.diff` holds the entry half).

Not run (and not claimed): any verdict for any row; the SOURCES.md round-44 section
(content, wording); C2; the lane's own gates. No pacman/uv/npx installs or upgrades were
needed, nothing was installed.

## 7. Limits

- `line_of_claim` is a reading of each entry against the row's SOURCES `teaches`; four
  anchors are judgement calls, recorded here so a reviewer can overrule them without
  re-reading everything: `context-capacity.md:65` (S110's `-kvu` default; its `-c 0`
  claim is at 115), `context-capacity.md:54` (S060's cap; also 50 and 177),
  `serving-metrics-crosswalk.md:14` (S001's `--metrics` gate; the name table is 15-21 and
  the prose restatement at 27/40), `chat-adapter-outcomes.md:38` (S180's 500; the
  paragraph is 37-41).
- The flag test proves the *placement and predicate* leg, not that any row drifted: the
  31 `drifted` verdicts were synthetic and are labelled as such in the clone's ledger.
- The clone lived only in scratch and was removed; every receipt cited is in
  `w1/out/S9Flags/`.
- `S015`'s placement (`gguf-runtime-compatibility-boundary.md:19`) is the only pair whose
  entry could not be exercised as drifted (`changed=0`), so it is predicate-verified
  only.
