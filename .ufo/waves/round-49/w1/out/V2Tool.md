# V2Tool — code review of the round-49 change to tools/append-only-audit.py

Verdict: **no defect found in the diff** — `origins()`, the graded condition, `binds()`, the
`definition` key and both new selftests are correct against the tool docstring and the frozen
C2 contract (tools/round49-append-audit-v4-check.py); the two new selftests both bite on the
v3 base; the frozen C2 counter reproduces `fixture=1 lane=1 scenarios=8/8 met=True` and the
frozen lane claim (ungraded 72→65 on 0718b6ab SCORECARD.md, event stays restored, exit 0).
Three residual notes, none in the diff itself (one latent counter-lane-leg strictness, one
frozen-definition semantics note, one cost note).

## Scope and method

Diff reviewed: `git -C kama-shokunin diff 438127bc01ff3b99f98468549d58046f932490ef 74558c71c38ceaeace15fd4cf8aa9d84977584b1 -- tools/append-only-audit.py`
(+94/−7; full diff read). All runs on my own `git clone --shared` at 74558c71 in scratch;
every finding exercised on a minimal fixture; base v3 tool extracted with
`git show 438127bc:tools/append-only-audit.py` for delta runs. LSP not used: no language
server answers for this lane (text/AST review of a single-file Python diff; grep used only
for line numbers).

## Findings

### High / Medium
None.

### N1 (Low, frozen instrument, latent) — C2 lane leg can false-kill a correct tool on `only=` files
tools/round49-append-audit-v4-check.py:346-348: for any reported event with `ungraded > 0`
on a file with no `exempt=` row it sets `ok = False` ("ungrades lines in a file with no
exempt row"). But the tool's `ungraded` is `|D| − |G|` (append-only-audit.py:469-480), which
counts deletions skipped by an `only=` prefix (allowed edits per that row's own declaration)
and non-exempt-origin lines. The lane has two `only=` rows (registry/append-only-contract.tsv:
corpus/knowledge/consumer-registry.md `only=## Errata`, error-is-not-a-verdict.md
`only=## Round24`). A future ≥20-line deletion outside those regions — permitted by the row —
yields an event with `ungraded > 0`, `ex = ∅` → `lane=0 met=False` on a conforming tool.
Latent (no such events today; counter reproduced met=True at the measured commit). FROZEN —
reported as a finding, not fixed in place. Proposed direction for a future round: bound only
the exempt-row files, or have the tool report prefix-skipped lines separately from `ungraded`.

### N2 (Informational, frozen definition, no divergence) — negation window is one-sided
NEG_WINDOW (append-only-audit.py:212-213) unbinds only when a negator precedes
`append[- ]only` within three words; "log is append-only but not really" binds (probe,
with token present). Identical regex in the frozen counter (round49-append-audit-v4-check.py:60-61)
and identical wording in both docstrings and the preregistration — tool and contract agree;
recorded as a residual semantics limit, not a defect.

### N3 (Informational) — origins() cost on the lane is negligible but subprocess-per-blob
origins() (append-only-audit.py:423-441) runs one `cat-file --batch-check` over all commits
and one `git cat-file blob` per distinct blob. Lane at 74558c71: 319 commits, 96 distinct
SCORECARD.md blobs; wall 0.74 s (v3 base) → 0.87 s (v4), same 5 events, exit 0 both
(lane.v3.json / lane.v4.json in this directory). Fine at lane scale; a 10k-commit history
with many blobs would degrade linearly in subprocess count. No change needed now.

## Review-area evidence

1. **origins()** — `commits` is `rev-list --topo-order --reverse --parents <to>`
   (append-only-audit.py:447-451), parents before children, so every deleted line's text has
   an origin (the parent blob is always scanned first); org is total over deleted texts, the
   `frozenset()` default at :475 is unreachable belt-and-braces. Blob dedup (`b in seen`)
   and per-first-blob title union match the frozen definition. **Non-ancestor/side-branch
   lines are covered**: fixture 3 (driver.py §3) births 24 lines under `## Round 9` on a side
   branch, a real merge moves them under exempt `## Plan`, a later first-parent commit
   deletes them there → v4 grades 24 (origin = side-branch birth under a dated title) while a
   first-parent-only origin would have ungraded them; v3 base ungraded 24. Matches
   "first commit of `git rev-list --topo-order --reverse <to>`" exactly (docstring :8-10,
   counter docstring origin(l)). First-appearance **union within the first holding blob** is
   the registered limit ("identical text born in both places counts as exempt-born",
   preregistration limits): fixture 5 — text born under `## Axes` and `## Round 1` in the same
   commit, Axes copy deleted → ungraded 24 on v3 and v4 alike (limit held, tool == counter).
   Preamble birth (None title) → graded: fixture 4 v4 graded 24 / v3 ungraded 24.
2. **Graded condition** `if s in eligible and org.get(text, frozenset()) & titles:` (:475) —
   `titles` is `set[str]` from `file_regions` (:404-413), origin values are `set[str | None]`;
   `set & set` is None-safe and correct; the v3 gates (`prefixes` skip, `s in eligible`,
   window/eligible regrowth) are unchanged. Counter's bound (`ungraded ≤ native`,
   counter:353-358) holds structurally since `eligible ⊆ titles = ex`; reproduced live:
   `ungraded 17 <= natively exempt 23`, `ungraded 65 <= natively exempt 65` (c2.receipt.out).
3. **binds()** (:216-232) — wildcard detection `any(ch in pattern for ch in "*?[")` and
   `re.escape(tok)` with `(?<![a-z0-9_])…(?![a-z0-9_])` are byte-identical to the frozen
   counter's `token()`/`binds()` (counter:100-137); 21-case edge probe (probe.py) confirms
   catalog/blog/logging refused, log.txt/log-2 bound, `_log` refused, "not strictly"/
   "no longer"/hyphenated/standalone-`non` negations unbind, wildcard self-declaration
   refused, wildcard named via directory token bound, no-directory wildcard row (`*.md`,
   token "") can never bind (same in counter). **Backtracking**: separator class `[\s\-]` and
   word class `[\w'’]` are disjoint and the repeat is bounded `{0,3}?`, so parses are unique;
   measured ≤ 9.1 ms on 400 KB adversarial inputs (`no ` + `a`×400000 + ` append-only`,
   20k negators, hyphen runs) — no catastrophic backtracking.
4. **`definition` key** (:504) — emitted: `--json` returns `"schema": "append-only-audit/v3"`
   plus `"definition": "v4"`; `render()`, exit codes and all other keys unchanged; grep over
   tools/ finds no consumer doing exact-key comparison (round46/47/48 counters read named
   keys of `events`/`summary` only).
5. **Docstring vs code** — every v4 bullet verified: origin definition (fixture 3/4/5),
   ungraded v3∧v4 condition (native-head fixture 6 keeps ungraded 24; counter native-head
   scenario ok), word-bounded token (probe), negator list not/never/no/nor/neither/non/
   isn't/aren't/`no longer` == regex alternation (:212-213), wildcard self-declaration rule
   (probe + counter scenario), JSON shape claim (:6). v3 text is explicitly versioned
   ("v3 (round 48) text, kept", :26).
6. **Two new selftests** (:910-931) — pass at tip (30/30, `AOA_SELFTEST pass=30 fail=0`,
   exit 0) and **both bite on v3**: t_launder_through_head on base → `deleted=25 graded=0
   ungraded=25 status=ungraded` (test wants graded 25 → FAIL on v3); t_binding_v4 on base →
   `oks=[True, True, True, True]` (wants [F,F,F,T] → FAIL on v3). Counter's 8 scenarios all
   ok at the tip (c2.receipt.out).

## Commands and results (all in my scratch clone at 74558c71)

- `python3 <tip>/tools/append-only-audit.py --selftest` → `pass=30 fail=0`, exit 0
- `python3 driver.py` (v3-vs-v4 on 6 fixtures: two new selftests + merge-origin,
  preamble-launder, dual-birth limit, native-head) → deltas as cited above, exit 0
- `python3 probe.py` (NEG_WINDOW timings + 21 binds edges; 3 initial "FAIL"s were my probe
  expectation errors — those lines name no token, and `doc[s]/a.md`'s frozen token is base
  `a`; re-checked with token present → frozen semantics confirmed) → exit 0
- lane v3 vs v4 `--repo <clone> --to 74558c71… --json` → both exit 0, 5 events all restored;
  0718b6ab SCORECARD.md ungraded 72→65, graded 2349→2356, status restored — exactly the
  frozen claim sentence; dd9f5dc6 unchanged (17)
- `python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip 74558c71… --scratch <S>`
  → `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0; counter sha256
  `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` == preregistration
  counter_sha256
- space-in-path declared file with an event + exempt row → no crash, native carve-out intact
  (cat-file batch resolves `rev:path with space`; pre-existing v3 concern, disproven at tip)
- mid-history file birth (file absent at root) → origins handles absent blobs (`b is None`)

## Residual risk and verification gaps

- N1 is latent and untested against a live only=-file event (would need a lane-sized fixture;
  counter is frozen, so it stays a routed risk for the C2 instrument).
- Origins semantics on pathological merges (evil merge, replace-style rewrites) was sampled
  with one real-merge fixture, not exhaustively.
- The tool's lane exit is 0 at the measured commit; the two round-49 counters are not yet in
  SKILL.md's registry and round-49 scribe entries are pending — known integration items,
  not re-reported.
- No tool was installed or upgraded for this seat.

## Artifacts (this directory)

- `c2.receipt.out` — frozen C2 counter receipt at the measured commit
- `lane.v3.json`, `lane.v4.json` — lane runs at 74558c71 by base and tip tool
- `driver.py` — the six v3-vs-v4 fixtures (incl. the two new selftests verbatim)
- `probe.py` — NEG_WINDOW timings and binds() edge cases
