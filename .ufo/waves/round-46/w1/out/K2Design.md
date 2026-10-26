# Round 46 — K2Design, C2 design critic (calibration)

**Verdict: C2 acquires a real history-audit instrument, but it is not yet a calibration capability in the `AXES.md:15` sense — 3 of its 5 declared files are declared append-only nowhere in the lane (SCORECARD.md is instead rewritten in place in 13 commits), its `restored` verdict counts same-commit relocations and blank-line artefacts (24/24 of the lines it calls restored at `dd9f5dc6` are re-added by that same commit; 494 deleted blank lines at `0718b6ab` are counted restored by an empty-string element), and its exit 1 today is composed entirely of two SCORECARD head-table rewrites while the incident it was built for would exit 0 after a complete repair. Land it, but the SCORECARD capability row must not claim that "the lane treats five files as append-only".**

Round-46 base for this critique: `0163fea2dab3f282ebd70c71da9ab5de4cedf733`; tool as landed at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` (blob `768f078e`, sha256 `793dab9f…`, identical at `96d3291`). Nothing frozen was edited; no lane file was modified.

## 1. What the frozen pair actually measures

- `tools/append-only-audit.py:4-8` asserts the population ("The lane treats five files as append-only"), `:43` fixes it in `FILES`, `:73-78` reduces each blob to a **set** of line texts, `:101-117` scores a deletion against that set, `:135-137` exits 1 only when a mass deletion is `partial`/`unrestored`.
- `tools/round46-append-audit-check.py:23-31` restates the same definitions. The `fixture` and `lane` legs therefore test an **independently implemented computation, not an independent specification**: both sides encode the same set-of-lines model, so the defects D2–D4 below pass both legs undetected (`fixture=1 lane=1` cannot catch them).
- `AXES.md:15` defines calibration by the proxy "SHONEN.md/SCORECARD entries match observed repo state". This tool compares file history against a *list*, never an entry's content against a *tree*. It becomes calibration exactly when the list is itself a declared SCORECARD/README entry — which is true for LOG.md and false for the other three files (D1).

## 2. Findings

### D1 — The five-file set is unsourced; 3/5 are not append-only by any declaration (calibration-critical)

`git -C <clone> grep -n -i append-only 0163fea2 -- README.md PROVINCE.md SKILL.md AGENTS.md MINT.md SHONEN.md SCORECARD.md corpus/QUALITY.md corpus/README.md corpus/SOURCES.md` (`e06-declarations.txt`) returns exactly two file-level declarations:

- `README.md:16` — "`LOG.md` — append-only round log" (fleet `PROTOCOL.md:431,463` agree).
- `corpus/SOURCES.md` — append-only per the CORPUS.md contract (`PROTOCOL.md:435`), and the lane's own guard permits in-place edits of three cells (`SKILL.md:578`; `corpus/QUALITY.md:123`, KQ22), i.e. the file the tool calls append-only is under an explicit in-place-edit rule.

There is **no** declaration for `SCORECARD.md`, `corpus/QUALITY.md` or `corpus/README.md`. The opposite holds for SCORECARD.md: its head axis rows are replaced in place in **13 commits** (`e04-analysis.txt` §5: `0718b6ab 21945c61 2793eb51 44fa5627 4fe239a4 83bee7fa 8bc8e375 c8c92db4 dabc6eee dd9f5dc6 ea72c3ea ef76777e f1a4ad2a`), and `LOG.md:523` records that as a sanctioned exception ("`SCORECARD.md` capability and saturation rows replaced 1:1").

Consequence: the "self-description" being audited is coined by the tool and the preregistration in the same round it is measured. If the landed SCORECARD row repeats "five files the lane treats as append-only", C2 adds a *false* self-description on the very axis it works — a calibration regression, not a gain. The proposal text it comes from (`considerthese/2026-10-26.md:29`) is an operator suggestion, not a lane contract, and the counter's `table` leg (`round46-append-audit-check.py:246-252`) checks only tool name + round `46`, so it cannot catch that wording.

### D2 — `restored_at_tip` counts text presence, not restoration: relocation and blank lines both read "restored"

`append-only-audit.py:77` stores `split("\n")`, whose trailing `""` element is always a "line at tip"; `:106` tests membership only, ignoring multiplicity (`:18` says so).

- Live blank-line artefact (`e04-analysis.txt` §2): of the lines counted restored at `0718b6ab`, **494/2416 are blank lines** in SCORECARD.md, 280/2290 in LOG.md, 102/375 in QUALITY.md, 138/663 in README.md. A deleted blank line is "restored" by the empty-string element even when the file has no blank line left.
- Live relocation (`e04-analysis.txt` §3): at `dd9f5dc6` **all 24** "restored" lines are also `+` lines of that same commit — the old head block moved verbatim into §Historical head sections. Nothing was restored; the file was reorganised.
- Fixtures (`e05-fixtures.txt`): F1 deletes 25 blank lines with no blank left at tip → `restored_at_tip=25 status=restored`, exit 0. F2 deletes 20 of 25 identical `|---|---|` lines → `restored_at_tip=20 status=restored`, exit 0, because one surviving copy "restores" every deleted copy.

This is the item's stated attack, confirmed live and by construction: a line restored *elsewhere* in the file counts, and a same-commit move counts as restoration.

### D3 — `restored_by` is not ancestry-scoped and can contradict `status`

`:108-115` scans every later commit in rev-list order, whether or not it descends from the event commit.

F3 (`e05-fixtures.txt`): event `475fd3a8` deletes 30 of 40 lines on mainline; side commit `c2b322c6` forked *before* the event and never lost a line; the merge keeps mainline. Output: `status=unrestored restored_by=c2b322c6` — a commit that never restored anything is named as the restorer, and the row reads as a contradiction. The selftest builds precisely this shape (`append-only-audit.py:257-273`) but asserts only `e[0]["commit"] != m`, so the field is never checked. The lane has 2 merges (`e04-analysis.txt` §6), so first-parent semantics has live instances; the sibling case is untested there.

### D4 — The threshold and the missing window make exit 0 mean "no news", not "append-only held"

`-U0` deletions are counted per (commit,file) with `>= 20` (`:101-104`).

- Live (`e04-analysis.txt` §4): **61 commits** delete 1–19 lines from the declared files; **171 of those lines are absent at the tip** (SCORECARD.md 81, corpus/SOURCES.md 46, LOG.md 22, corpus/README.md 20, corpus/QUALITY.md 2). The tool reports 0 events and exits 0 for all of it.
- F4: 15 lines deleted from each of two declared files → no event, exit 0.
- A *repaired* mass deletion also exits 0: had `82b5e9d3` restored all 2417 lines, `0718b6ab`'s four-file truncation would not have changed the exit code at all.
- There is no `--since`/window: `dd9f5dc6` (round 42) still pins exit 1 four rounds later, so the exit code cannot express the proposal's intent ("flag deletions … the morning after").

### D5 — Is exit 1 on the lane's own history signal or noise? Both partials are head-table maintenance; the incident that motivated the tool is invisible to the exit code

Audit at the base (`e02-audit-base-0163fea2.txt`, exit 1) is 5 events / 3 restored / 2 partial:

| event | missing lines | what they are |
|---|---|---|
| `dd9f5dc6` SCORECARD 24/31 | 7 | the six §Axes head rows + the round-41 reconcile sentence, superseded **in the same commit** by same-score rows (`e08-repair.txt`; tip scores 8/8/7/9/7/7). This is the round-42 C1 head reconcile, the lane's declared practice. |
| `0718b6ab` SCORECARD 2416/2417 | 1 | the head depth row with `SKILL.md` sha `91440eb8` (1420 lines); `82b5e9d3` re-anchored it to `3046955b` (1432 lines) — commit subject "depth re-anchor", `e08-repair.txt`. |

So exit 1 today means "SCORECARD.md is not append-only in its head" — true, but it denies the tool's own population statement (D1) and it is *not* unrepaired loss. Conversely the case the tool exists for (`0718b6ab` truncating four file bodies) is reported as `restored` and contributes 0 to the exit code once repaired. Neither the red nor the green state maps onto "an append-only file lost text".

## 3. Is it calibration? (the assigned question)

- As a **capability acquisition** under the frozen predicate (`selftest=1 fixture=1 lane=1 table=1`) the claim is unaffected by D1–D5: the tool runs, passes 10 selftest cases, and agrees with an independent re-implementation. Those legs are legitimate for implementation equality and insufficient for specification validity.
- As a **calibration move** it is honest only for the two files the lane actually declares (LOG.md; SOURCES.md with the KQ22 cell exception): there it converts a real event (`0718b6ab` truncating LOG.md by 2290 lines) into a timestamped, restorer-named record — the SCORECARD entry "LOG.md is append-only" was false for one commit and this is the evidence. That is a genuine, if narrow, calibration fact.
- For SCORECARD.md / QUALITY.md / corpus/README.md the tool measures a claim the lane never made, so the SCORECARD row must be worded as what it is: *an audit of a declared list*, or the declaration must be landed first (D1 fix) — otherwise the row itself becomes the round's overclaim, on the axis whose definition is "overreach caught".

## 4. Smallest safe correction (finding only — tool, counter and preregistration stay frozen)

**Primary (one line, no code):** land the declaration the tool assumes, before/with the capability row — in `README.md` beside line 16:

```
- `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `SCORECARD.md` —
  append-only *as scoped here*: SOURCES row text except the `status`/`recheck`/`used-by`
  cells (`SKILL.md:578`, KQ22); SCORECARD except the §Axes head rows, replaced 1:1 when a
  round reconciles them (`LOG.md:523`).
```

and make the SCORECARD capability cell cite that line instead of asserting "five files the lane treats as append-only". Then exit 1 stops being a contradiction: a partial inside a declared exception is a contract question, a partial outside it is a finding.

**Secondary, for a later round (code sketch; helper names are mine, the changed tests are the point):**

```diff
--- a/tools/append-only-audit.py
+++ b/tools/append-only-audit.py
@@
-    def lines(self, blob):
-        ...
-            self._blob_lines[blob] = frozenset(_git(self.path, "cat-file", "blob", blob).split("\n"))
+    def lines(self, blob):
+        ...
+        if blob not in self._blob_lines:
+            text = _git(self.path, "cat-file", "blob", blob)
+            parts = text.split("\n")
+            if text.endswith("\n"):
+                parts.pop()                      # no phantom "" line; blanks keep multiplicity
+            self._blob_lines[blob] = collections.Counter(parts)
@@
-            k = sum(1 for x in dele if x in tip_lines)
-            status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")
+            dc = collections.Counter(dele)
+            k = sum(min(n, tip_lines[x]) for x, n in dc.items())
+            moved = sum(1 for x in set(dele) if x in add_lines_of_same_commit)
+            status = ("moved" if moved == len(dc) else
+                      "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial"))
@@
-            for c2 in later:
-                if need <= r.lines(later_blobs[f"{c2}:{f}"]):
+            for c2 in later:
+                if _is_ancestor(repo_path, c, c2) and need <= set(r.lines(later_blobs[f"{c2}:{f}"])):
                     rb = c2
                     break
```

plus two summary fields that keep exit 0 honest — `below_threshold_commits=N below_threshold_missing=M` (this lane: 61 and 171) — and `--since REV`, whose exit code covers only events at or after it (D4). With those, the signal is: *a declared append-only file lost text inside its declared scope and either was or was not put back, as of a window* — which is what "flag deletions the morning after" asked for.

## 5. Impacted axes

- **calibration** — the exposure. Unchanged-score direction depends on the row's wording: with D1's declaration the row is true and the incident evidence (`0718b6ab`/`82b5e9d3`) supports it; without it the row is an unchecked self-description added by the round that measures it.
- **operability** — none: the tool exists, runs, selftest 10/10; D2–D4 are semantic, not availability.
- **freshness / depth / coverage / adjacency** — untouched; nothing here bears on upstream bytes or domain surface.

## 6. Evidence index (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Design/`)

| file | content |
|---|---|
| `e01-tool-identity.txt` | blob `768f078e` at `4a2a4d55` and `96d3291`, sha256, commit history |
| `e02-audit-base-0163fea2.txt` | full `--json` audit at the base, exit 1, 5 events |
| `e03-audit-landing-96d3291.txt`, `e03b-audit-at-4a2a4d55.txt` | same 5 events at both landing tips, exit 1 |
| `e04-analysis.txt` | `analysis.py` re-derivation: missing lines, blank accounting, relocation, below-threshold 61 commits / 171 lines, 13 head-row replacement commits, 2 merges |
| `e05-fixtures.txt` | F1 blank-line, F2 duplicate-text, F3 non-descendant `restored_by`, F4 per-file threshold |
| `e06-declarations.txt` | the grep of declarations at `0163fea2`, lane `README.md:16`, `SKILL.md:578`, fleet `PROTOCOL.md:431,435,463` |
| `e07-tool-lines.txt` | the exact tool lines cited above |
| `e08-repair.txt` | the `82b5e9d3` depth re-anchor and the unchanged tip scores |
| `analysis.py`, `fixtures.py`, `README.md` | re-runnable drivers and how to reproduce |

All commands ran on a `git clone --shared` of the lane under `/fast/scratch/hyaku/kama-r46/K2Design/lane` (read-only use, removed after the run); no receipt came from `/tmp`. The lane, its index and its jj state were never written.
