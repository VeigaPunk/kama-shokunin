# RV01WordingC1 — adversarial review of C1's STATED WORDING vs tools/round100-record-audit.py

- **Lane:** kama-shokunin, base `6776c667372a0da8635ebfbda6cbc92d8fb17304`, freeze M `2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6` (receipts commit 3626e06c; counter behaviors below reproduced at M on scratch clones, never by editing tracked lane files).
- **Wording under attack:** `plans/round-100-claims.md` §C1 (lines 32–73) and `.ufo/waves/round-100/claims.json` C1 `name` (line 8).
- **Counter under attack:** `tools/round100-record-audit.py` (194 lines; docstring lines 1–48, code lines 50–194) with `HEADING` at line 57, `POLICY_ATTACK`/`LEDGER_ATTACK` at 58–60, `BOUND_RE`/`ANY_PTR_RE`/`PCT_RE` at 63–66, `block()` at 113–127, checks at 132–178.
- **Receipts attacked:** `.ufo/waves/round-100/measured/c1.out`, `controls/c1-base.out`, `controls/c1-forgeries.out` (+ `controls/c1_forgeries.py`). Read-only gate source: `/home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py` lines 58–61 (`ATTACK_ROLES`), 81–88 (`attack_seats`), 216–220.
- **Method:** (1) read the plan, the counter, the receipts, `r99-measured.json`, and the round-99 `w1-spec.json`/`w1-results.json` at `6776c667`; (2) reproduced the counter green at M on a scratch clone; (3) ran 44 fixture forgeries (each: shared clone checked out at `6776c667`, lane files copied in, one uncommitted edit, commit on a scratch bench, counter run via its public `--repo/--rev` path with `GIT_AUTHOR_NAME/GIT_COMMITTER_NAME=fixture`). Out dir that I left the 44 rows under: `.ufo/waves/round-100/w1/out/RV01WordingC1/` (6 receipt files, see §6). Commands are absolute-path; every finding names the file:line and the repr-comparable command output that shows it.
- **Verdict vocabulary:** `falsifies-wording` = the counter goes green on a property narrower than the claim's stated wording (Amendment-59 class). `falsifies-number` = a wrong number. Otherwise `neutral`.

---

## 1. Enforcement matrix — property the code enforces vs property the wording asserts

| # | Code actually enforces (`tools/round100-record-audit.py`) | Wording asserts (`plans/round-100-claims.md` §C1; `claims.json` C1 `name`) | Gap? |
|---|---|---|---|
| 1 | `checks[1] = sc is not None` (line 132). `block()` (113–127): text after the **one** line starting with `## Round 100 correction — round-99 records` (em dash U+2014, see `HEADING`, line 57) up to the next line starting with `## `, or EOF; `len(heads) != 1` → `None` (118–120). | "one `## Round 100 correction — round-99 records` block in `SCORECARD.md`" (plan line 38). | **No substantive gap.** The em dash is the kind of thing that could bite a reader copying a hyphen (D1 probe below), but the heading text is given exactly and the "exactly-one-occurs" rule is the natural reading of "one block". |
| 2 | `checks[2] = lg is not None`, same procedure on `LOG.md` (133). | "one … block in `LOG.md`" (38). | No gap, same remark. |
| 3 | `led_s in sc and pol_s in sc` (134), where `led_s`/`pol_s` are the rendered strings `f"{n} of {total} ({round(100*n/total)}%)"` (101–102) — **substring presence per block, with no label binding**. `n` counts roles in the spec items (95–100) against hardcoded frozensets (58–60). | "each block contains the policy attack fraction `4 of 12 (33%)` and the ledger attack fraction `6 of 12 (50%)`" (38–40). | **YES — two gaps.** (a) The wording can be read as attributing those strings to the policy/ledger roles. The counter cannot tell policy from ledger: a block that puts `6 of 12 (50%)` under the *policy* label and `4 of 12 (33%)` under the *ledger* label while also naming the right role sets in some other position passes (F1 probe, §5). (b) Substring presence is strictly weaker than the natural-language "states the derived fraction": `14 of 12 (33%)` contains the substring `4 of 12 (33%)` and `16 of 12 (50%)` contains `6 of 12 (50%)`, so those pass (G1a/G1b probes, §5). The *rendered* value must of course be right, but the *numerator as a standalone claim* is not bound — the substring is over an unbounded left context. |
| 4 | Same as (3) for the LOG block (135). | Same. | Same two gaps (each independently falsifiable; the check requires both blocks). |
| 5 | For each block (`len(blocks)==2` else `pct_ok=False`, 137), strip `BOUND_RE` (139) and fail on any `PCT_RE` (`\d+(?:\.\d+)?\s?%`, 66) whose space-stripped text is not in `{round(100*pol/total)%, round(100*led/total)%}` (136–143). | "neither block, its quoted pointer phrases removed, contains a digit percentage other than those two" (41–42). | **YES — one gap.** "Counts percentages written in words" is **not** enforced and not disclosed: `58 percent` contains no `\d+%` and slips through (F3 probe). Disclosed limit (a) (plan lines 64–66) already says word-level contradictions escape; the gap is that it is not mentioned against **this specific sentence**, and the claims.json wording "carry no other digit percentage" is read as "digit", so a reader can still conclude "correct" while the block contradicts itself in words. G2 (112 seats) is a related substring-bypass for the *seats* sentence; for check 5 itself, a stated "50.0%" fails check 3&5 doubly (W10 probe) because the *rendered* form is `50%` and decimal reprs are not admitted — that is a **number**-ward narrowing, not a wording one (see §7). |
| 6 | `seat_s = f"{seats} seats, {dead} dead" in b for both blocks` (145–146). `dead` = results rows with empty `output` or `status` in `DEAD_STATUS` (93–94); the round-99 file carries no `status` (docstring 22–23), so this is purely "non-empty output". | "both state `12 seats, 0 dead`" (42–43). | **YES — disclosed (e), but repeated here as the wording-gap:** "state" is again substring presence. `112 seats, 0 dead` contains `12 seats, 0 dead` and passes (G2 probe, §5). The disclosed limits say dead = empty output or failure status (plan line 70); they do not say the sentence is a substring scan. |
| 7 | `bound` (via `BOUND_RE`, 63–64) and `unbound` (via `ANY_PTR_RE`, 65) after removing bound tokens (147–154). Requires `len(blocks)==2`, `unbound==0`, `len(bound)>=3`. `BOUND_RE` requires: backticks, one of `SCORECARD.md`/`LOG.md`/`corpus/lessons/<[\w.-]+>.md`, literal `@`, **lowercase** hex `[0-9a-f]{7,40}`, `:`, digits, closing backtick, `\s*`, then `("…")` with a non-empty, quote-free phrase (`[^\"]+`). `ANY_PTR_RE` is non-enforcing of the backtick/`@"`/quote parts — see §2. | "every `SCORECARD.md`/`LOG.md`/`corpus/lessons/*.md` line pointer in the blocks is revision-bound and quoted" (43–45, and claims.json "bind every SCORECARD/LOG/lessons line pointer… (>=3)"). | **YES — two gaps.** (a) Pointer *forms* that a reasonable reader calls a line pointer are not pointers to the regex (words form `SCORECARD.md line 6431`, `LOG.md#L4040`, `corpus/lessons/sub/x.md:10` nested path, uppercase hex, `@123456` short hash). The committed blocks themselves use the words form (§2), so the counter's green does not mean "no unbound pointer anywhere" — it means "no *grammar-recognised* pointer is unbound". (b) "is revision-bound and quoted" includes backticks and a parenthesised phrase in the counter but the wording supplies no such exact punctuation; W18 (lessons pointer unbound) shows the same pointer in slash-only form *does* fail (1 mismatch check7), while the words/`#L` forms do not — the binding is *syntactically exact*, which is narrower than the English. |
| 8 | Each bound token resolves: `git show <hex>:<path>` (157), line in range, `phrase.strip() != ""`, `phrase in lines[n-1]` (162), and `resolved == len(bound)` with `len(bound)>=3` (167). **Substring containment on that one line**, not line equality. `"10 reported, 2 dead"` inside a longer line resolves. | "every bound pointer's phrase is on that line at that revision" (45). | No material gap: "on that line" is substring-equivalent (same content). Disclosure is fine. |
| 9 | `m_ok` (168–178): `r99-measured.json` parses as a dict, key set exactly `{C1,C2,C3}`, each value non-None and **byte-equal** to the first line of the corresponding `c{k}.out` starting with the predicate prefix (`PRED_PREFIX`, line 62), and that file's last `exit=` line is exactly `exit=0`. The `exit=` tail is read off **any** file at `<rev>` — not necessarily `c{k}.out`'s own. | "`r99-measured.json` maps exactly C1/C2/C3 to the round-99 measured predicate lines, byte-equal to `.ufo/waves/round-99/measured/c{1,2,3}.out`, each of which ends `exit=0`" (46–47). | **No material gap.** Two small un-disclosed caveat forms: the layout of the JSON (pretty-print, key order) is not bound — the values are (Q4e probe: reformatting alone passes). That's a *widening* of the property (byte-equal *values*, not byte-equal file), not a narrowing, so it is not a falsification. The `exit=0` tail check reads the *last* `exit=` line in the file, including an appended one (Q4c in §4 fails exactly as expected); that is byte-faithful. History caveat: at `00394f3b` the measured files do not exist yet (§6), so "each of which ends `exit=0`" is only intelligible read at the *base* revision's tree (files were committed by `6776c667`). |

### How checks 3 and 9 treat the three round-99 measured lines — the "first line" is not unique outside the receipts
At `2e27e6f1`, each of `c{1,2,3}.out` has exactly one line starting with its predicate prefix, and those three lines are byte-equal to `r99-measured.json` (verified below with the counter's own prefixes). But the section-9 wording "the three round-99 measured predicate lines" has no uniqueness claim for arbitrary trees: if a file contained several predicate-prefixed lines, the counter takes the **first** (line 106), while the ledger phrase "the measured predicate lines" suggests a canonically unique thing. On a contaminated tree with a fake earlier `CONTROL_POP99 ` line and a real later one, the counter grades the fake. This is not a wording falsification because the receipts carry exactly one such line each, but it is a *second* instance of the same class: the instrument grades a projection (first matching prefix line) and the wording asserts identity ("the predicate lines").

---

## 2. Is "every SCORECARD/LOG/lessons line pointer in the blocks is bound" true of the committed blocks as written?

`git show 2e27e6f1:SCORECARD.md | awk 'NR>=6538 && NR<=6559'` and the LOG twin at lines 4100–4121 (plus `git show 2e27e6f1:SCORECARD.md | tail -40` / `git show 2e27e6f1:LOG.md | tail -40` taken at the start of this seat) show the committed blocks are:

- `SCORECARD.md:6538-6559` (block) and `LOG.md:4100-4121` (block), each with the single heading `## Round 100 correction — round-99 records` (SCORECARD.md:6538; LOG.md:4100; each file has exactly one such heading at M — `grep -n` above).
- **Bound tokens (10, 5 per block, all resolving — counter's `RECORD_AUDIT100_DERIVED … bound=10 resolved=10 unbound=0` at M):**
  `` `SCORECARD.md@6776c667:6500` ("58% attack") `` (SCORECARD.md:6549; LOG.md:4111),
  `` `LOG.md@6776c667:4065` ("CN01Overlap (attack)") `` (SCORECARD.md:6550; LOG.md:4112),
  `` `SCORECARD.md@00394f3b:6431` ("10 reported, 2 dead") `` (SCORECARD.md:6552; LOG.md:4114),
  `` `SCORECARD.md@6776c667:6446` ("10 reported, 2 dead") `` (SCORECARD.md:6553; LOG.md:4115),
  `` `LOG.md@6776c667:4040` ("10 reported, 2 dead") `` (SCORECARD.md:6555; LOG.md:4117).
- **And one grammar-invisible pointer form in each block:** the words-form citation at SCORECARD.md:6551–6552 / LOG.md:4113–4114:

  > "The round-99 correction blocks cite the round-98 wave sentence as an unbound `SCORECARD.md` line 6431."

This is a *description* of the defect being corrected, not itself an unbound pointer to live corpus text, but under the stated wording "every SCORECARD/LOG/lessons line pointer in the blocks is bound" it is still a line pointer in the blocks written without a revision, a quote, or digits-in-colon form. The counter (receipt `measured/c1.out`: `checks=9 mismatches=0 met=True`) is green *because* `ANY_PTR_RE` requires `:` + digits — `SCORECARD.md line 6431` has neither. Semantically the sentence is not `SCORECARD.md:6431` (a pointer *to* a line) but a words-description of a future pointer; a reader who read "every SCORECARD/LOG/lessons line pointer in the blocks is bound" would still reasonably want this form to count. Recorded as the canonical example of the gap; see §5 W1.

**Pointer forms the regex misses (each tested against the frozen regexes by direct `re.compile` probe, and W1–W4 by scratch-clone forgeries):**

| Form | Example | `BOUND_RE` | `ANY_PTR_RE` after strip | Verdict when placed in block |
|---|---|---|---|---|
| Words | `` `SCORECARD.md` line 6431 `` | 0 | `[]` | passes (W1 rc=0) |
| Hash form | `LOG.md#L4040` | 0 | `[]` | passes (G3b rc=0) |
| Slash | `SCORECARD.md:311/5840/5944` | 0 | `['SCORECARD.md:311']` | **fails** (check7 counts it; W5 rc=1) |
| Bare `LOG.md:4040` | plain text | 0 | `['LOG.md:4040']` | **fails** (F2-analogue, rc=1 check7) |
| Backticked, no `@rev` | `` `SCORECARD.md:6446` ("10") `` | 0 | `['SCORECARD.md:6446']` | **fails** (W17/W18-adjacent) |
| Uppercase hex | `` `SCORECARD.md@6776C67:1` ("x") `` | 0 | `['SCORECARD.md@6776C67:1']` | **fails** (0 bound → check7 counts it) |
| Nested lessons | `` `corpus/lessons/sub/x.md@6776c667:10` ("x") `` | 0 | `[]` | passes (W4 rc=0) |
| 41-char hex | `` `SCORECARD.md@<41 hex>:1` ("x") `` | **1** (regex is `{7,40}` but `finditer` on a 41-char run matches the first 40) | `[]` | would be counted **bound** (41-char reads as bound; then check8 fails on `git show`) |
| Empty phrase | `` `SCORECARD.md@6776c67:1` ("") `` | 0 | `['SCORECARD.md@6776c67:1']` | **fails** (check7), though check8 also rejects |

So: are there pointer forms the regex misses? **Yes — words, `#L`, and nested-lessons forms.** Three of the findings are reachable by renaming the current committed sentences; the fourth (`corpus/lessons/sub/x.md`) is reachable against *any* lesson pointer because `[\w.-]+` excludes `/`. The disclosed limit (b) (plan lines 66–67) already covers `tools/x.py:12`-style pointers, but no disclosed limit mentions `log.md#L4040`-style pointers or nested lesson paths. The honest fence is in §7 (N4/N5).

---

## 3. Is "6 of 12 (50%) ledger" really the prefile gate's attack set?

**Yes, the number is right — and the *provenance chain* is correct.**

- The frozen prefile gate at `/home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py` defines `ATTACK_ROLES = {reviewer, security-reviewer, critic, mutation-tester, sentinel, connector, revenger, labrat}` (lines 58–61) and computes attack seats from the **results** file's `agent` field: `attack_seats(results)` (lines 81–88). For the round-99 results file (at `6776c667`), the rows carry `agent ∈ {scout, executor, scribe, reviewer, critic, mutation-tester, sentinel, connector}` and the extraction is exactly `['CN01Overlap', 'CR01Records', 'MT01Mutants', 'RV01Wording', 'RV02Counter', 'SN01Bounds']` — 6 seats. Replayed with the gate's own code:
  `attack_seats` on that file = 6; on the spec items (by `role`) = the same 6 names. So ledger = 6 of 12 (50%) is the gate's attack set, and the correction's gloss — "the prefile ledger's attack roles (adding sentinel and connector)" — names exactly the two extras the gate adds over the policy set (policy `4` = reviewer/critic/mutation-tester/labrat; gate extras over policy = sentinel and connector; revenger/security-reviewer happen to be absent from round 99 — they are in the gate's frozenset but no seat carries them).
- **Against the round-99 spec roles:** the round-99 `w1-spec.json` items (12, all enumerated in §6) carry `role`-fields reviewer×2, critic×1, mutation-tester×1, sentinel×1, connector×1, executor×3, scout×2, scribe×1. Policy attack (reviewer/critic/mutation-tester/labrat) = 4 seats; ledger attack (gate's eight, of which six occur + two absent) = 6 seats. `wave_role_mix` in the round-99 `claims.json` (at `6776c667`) independently says `"attack": "6 of 12 (50%)"` — consistent.
- **The counter's derivation is *different*, but extensionally equal on this wave:** `tools/round100-record-audit.py` reads roles from `w1-spec.json` items (`role`, lines 95–100) against its own `LEDGER_ATTACK`/`POLICY_ATTACK` (58–60), not from `w1-results.json`'s `agent` field. The gate reads from `w1-results.json`'s `agent`. For round 99 the two files agree seat-for-seat (spec names ≡ results names, each role ≡ agent), so 6 and 4 agree. The counter's rendering uses Python's banker's `round()` (line 101): `round(33.333…)=33`, `round(50.0)=50` — correct here. (Banker's rounding itself would matter for a wave whose rate lands on .5, but this wave's fractions are integral after the third decimal.)
- Numbers in the receipt (`measured/c1.out`: `policy_attack='4 of 12 (33%)' ledger_attack='6 of 12 (50%)`) are the *right* numbers for this wave. Q3's answer is therefore **not** `falsifies-number` for the ledger figure.

**The one true semantic reservation:** the counter's `LEDGER_ATTACK` is a hardcoded copy of the gate's `ATTACK_ROLES`, not an import of `/home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py`. If the gate's frozenset is extended (or a role is dropped) for a future wave, the counter silently grades the old set. That is not a falsification of *this* claim on *this* wave (the sets agree today), but it is the correct remedy to record: source `LEDGER_ATTACK` from the gate or import `ATTACK_ROLES`. If the wording is later reused for a wave where the gate has changed, the "6 of 12 (50%)" *value* is still derived from the spec (never hardcoded), but the *role membership* would still be wrong. Narrowing sentence N7 (§7) fences exactly this.

---

## 4. Does check 9 really bind the three round-99 measured lines? (byte-edit probes)

Yes — check 9 binds the lines, demonstrated on a scratch clone at `6776c667` with each forged commit then graded by the frozen counter at scratch HEAD (`records = COMMITTED baseline + fixture forgeries`):

| Probe | Edit on scratch clone | Exit | Mismatch |
|---|---|---|---|
| P0-positive | none (the lane's correction itself) | 0 | reported `taken` |
| Q4a C2 12→13 | `.ufo/waves/round-100/r99-measured.json`: `checks=12` → `checks=13` in the C2 value | 1 | reported `check9` |
| Q4b swap C1/C2 | exchanged C1 and C2 JSON values (each still "looks like" a predicate line) | 1 | reported `check9` |
| Q4c trailing `exit=1` | appended `exit=1\n` to `.ufo/waves/round-99/measured/c1.out` (counter reads the *last* `exit=` line) | 1 | reported `check9` |
| Q4d C1=C3 | set C1 value to the C3 line string (a plausible-looking decoy) | 1 | reported `check9` |
| Q4e reformat only | repretty-printed `r99-measured.json` (`sort_keys, indent=4`) — values unchanged | 0 | reported `taken` (as expected: binding is on values) |
| Q4f extra key C4 | added `"C4": "AUTOLOAD_STATES99 extra"` | 1 | reported `check9` |
| Q4g trailing space | appended ` ` to the C2 value | 1 | reported `check9` |

So a one-byte edit of a measured line, a swap, an appended `exit=1`, a decoy line from another claim, an extra key, or a stray whitespace byte all exit 1 with `check9` (and nothing else). The forgery F4 in the frozen `controls/c1-forgeries.out` (`mismatches=0  met=True` one-byte edit) is independently green in the frozen receipt. Check 9 **does bind** — including versus the three more creative forgeries above (swap, decoy-same-claim string, extra key) that were not in the freeze controls.

---

## 5. The false-green forgeries (Amendment-59 class) and the remaining W/E probes

Each row is one scratch-clone commit graded by the frozen counter at scratch HEAD (same harness as §4). **G = green (rc=0) on a falsifying edit; F = red (rc=1) as it should be.**

### Words-form and pointer-shape probes (Q2)

| Probe | Edit | Outcome |
|---|---|---|
| W1 words-form unbound — `` `SCORECARD.md@00394f3b:6431` `` → `` `SCORECARD.md` line 6431 `` (per the committed sentence) | bound token → words description | **GREEN** (rc=0, 0 mismatches) |
| W2 `LOG.md#L` form — `` `LOG.md@6776c667:4040` `` → `LOG.md#L4040` | bound token → hash form | **GREEN** (rc=0) |
| W3 tools pointer — inject `tools/x.py:12` beside the unbound-`file:line` sentence | disclosed limit (b) | GREEN (expected; disclosed) |
| W4 lessons nested subdir — `` `SCORECARD.md@…:6431` `` → `` `corpus/lessons/sub/x.md@6776c667:10` `` | `[\w.-]+` excludes `/` so neither regex fires | **GREEN** (rc=0) |
| W5 bare `SCORECARD.md:9999` injection | grammar-detected | RED, `check7` (correct) |
| W6 words-only percentage — `were 4 of 12 (33%)` → `were four of twelve` | removes the fraction string | RED, `check3` |
| W7 extra `%` inside quoted phrase — `("58% attack")` → `("58% attack, 42% noise")` | changes quoted phrase; STILL resolves against a different line? No → | RED, `check8` — because the phrase is no longer on the target line (check8 is the binding one) |
| E1 in-quote percent swap — `("58% attack")` → `("42% attack")` | quoted phrase altered | RED, `check8` |
| E4 file absent at rev — point a lesson pointer at the line of a file that does not exist there | `git show` fails | RED, `check8` |

### Number-shape probes (Q3, corrected anchors)

| Probe | Edit | Outcome |
|---|---|---|
| W8 wrong n in words (`seven of 12 (50%)`) | keeps the right rendered pct | RED, `check3` — correct: the counter requires the rendered fraction |
| W9 `49.9%` / W10 `50.0%` / W11 `50.5%` | decimal percentages in place of `50%` | RED, `check3,check5` — correct: decimal pct not admitted |
| W12 seats wrong (`19 seats, 0 dead`) | keeps shares | RED, `check6` |
| W13 contradiction in words — append "seven seats, more than half" | no digit pct contradicted | **GREEN** (rc=0) — the disclosed limit (a) case |
| W14 heading em-dash → hyphen | `## Round 100 correction - round-99 records` | RED, `check1,3,5,6,7` |
| W15/W16 heading early truncation | `## ` early inside the block | **GREEN** (extra `## ` ends the block; content simply isn't graded; F2-style detection still works) |
| W17 bare `SCORECARD.md:6431` injection | plain text | RED, `check7` (correct) |
| W18 lessons pointer unbound bare (`corpus/lessons/…md:3`) | slash-only pointer | RED, `check7` — correct: this one *is* in the grammar |
| W19 bound line moved (6446→6447) | off-by-one | RED, `check8` |
| W20 bound≥3 diluted with a duplicate valid pointer | duplicates the `?` | RED, `check7,check8` |

### Substring-presence probes (the actual falsifications)

| Probe | Edit | Outcome | Why |
|---|---|---|---|
| G1a `14 of 12 (33%)` | `were 4 of 12 (33%)` → `were 14 of 12 (33%)` | **GREEN** (rc=0 mismatches=?) | `14 of 12 (33%)` *contains* the substring `4 of 12 (33%)` (checks 3/4, lines 134–135) |
| G1b `16 of 12 (50%)` | ledger fraction → `16 of 12 (50%)` | **GREEN**, same | |
| G2 `112 seats, 0 dead` | `12 seats, 0 dead` → `112 seats, 0 dead` | **GREEN**, same | `112 seats, 0 dead` contains the substring `12 seats, 0 dead` (check 6, line 146) |
| G4 (first attempt, labels only) | policy sentence `were 6 of 12 (50%)` replacing `were 4 of 12 (33%)` | RED, `check3` — expected: still drops the policy fraction string entirely |
| **F1 label swap, both fractions present** | swap *labels and fractions together*: policy sentence now `were 6 of 12 (50%)` AND ledger sentence now `were 4 of 12 (33%)` | **GREEN** (rc=0, met=True) | The counter cannot read labels at all — only the presence of the two rendered strings (lines 134–135). The tabling now asserts the opposite assignment ("the policy attack were 6 of 12", "the ledger attack were 4 of 12"), which is exactly the round-99 58% mistake in reverse, and the counter is green. |
| F3 stray word-percent | insert `58 percent with the scribe` | **GREEN** (rc=0) | `PCT_RE` (line 66) requires `\d+%`; word-percent escapes. Disclosed limit (a) (plan lines 64–66) names word-level contradiction as uncovered — but check 5's sentence *in the claim* says "contains a digit percentage other than those two", so the reader-facing claim is silently narrower than "the block's percentages agree". |

G1a, G1b, G2, F1, F3 are the Amendment-59 counterexamples: every one is a committed change to a frozen file that flips the *statement* while leaving the frozen predicate green. The three most damning for the claim are **F1** (a full policy/ledger inversion the counter cannot even see), **F3** (a stray contradictory percentage in words, past check 5's digit-only grammar), and **G2** (substring semantics: the counter turns a claimed headcount of 112 into a passing "12 seats" without reading the `1`). G1a/G1b are the same substring defect in both fraction checks.

---

## 6. Evidence — commands and line-level receipts

### 6.1 Green at M, red at base (reproduced on scratch clones, not in the lane)

```
$ git -C /fast/scratch/hyaku/kama-r100/RV01WordingC1/fx.HDkcgD rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r100/RV01WordingC1/fx.HDkcgD
$ python3 tools/round100-record-audit.py --repo /fast/scratch/hyaku/kama-r100/RV01WordingC1/fx.HDkcgD --rev HEAD
RECORD_AUDIT100_DERIVED seats=12 dead=0 roles=12 policy_attack='4 of 12 (33%)' ledger_attack='6 of 12 (50%)' bound=10 resolved=10 unbound=0
RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6
rc=0
$ python3 /fast/scratch/hyaku/kama-r100/RV01WordingC1/q4.out (Q4 table §4: P0-positive rc=0, Q4a–d/f/g rc=1 check9, Q4e rc=0 taken)
$ python3 /fast/scratch/hyaku/kama-r100/RV01WordingC1/q3probe.py invocation output is in q3.out (W8–W20 table §5)
$ python3 /fast/scratch/hyaku/kama-r100/RV01WordingC1/finalprobe.py invocation output is in final.out (G1a–G4/D1/G3b table §5)
$ python3 /fast/scratch/hyaku/kama-r100/RV01WordingC1/followup.py invocation output is in followup.out (F1/F2/F3 table §5)
$ python3 /fast/scratch/hyaku/kama-r100/RV01WordingC1/closeout.py invocation output is in closeout.out (E1–E5 table §5)
```

The frozen receipts agree with what the scratch-clone runs show:

```
$ cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-100/measured/c1.out
RECORD_AUDIT100_DERIVED seats=12 dead=0 roles=12 policy_attack='4 of 12 (33%)' ledger_attack='6 of 12 (50%)' bound=10 resolved=10 unbound=0
RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6
exit=0

$ cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-100/controls/c1-base.out
RECORD_AUDIT100_MISMATCH check1 … check9 (all nine)
RECORD_AUDIT100 checks=9 mismatches=9 met=False rev=6776c667372a0da8635ebfbda6cbc92d8fb17304
exit=1

$ cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-100/controls/c1-forgeries.out
C1_FORGERY P0-positive rc=0 want=0 ok=1 mismatched=- …
C1_FORGERY F1-stray-58pct rc=1 want=1 ok=1 mismatched=check5 …
C1_FORGERY F4-measured-edit rc=1 want=1 ok=1 mismatched=check9 …
C1_FORGERIES cases=8 wrong=0 met=True
exit=0
```

### 6.2 Block contents at M

```
$ git show 2e27e6f1:SCORECARD.md | awk 'NR>=6538 && NR<=6559'
6538: ## Round 100 correction — round-99 records (appended 2026-11-08; the round-99 entries above are not rewritten)
6540: Routed by `corpus/lessons/round-99-verifier-spotcheck.md` defects 1, 2 and 4. …
6544: - **Wave share.** Round-99 wave 1 had 12 seats, 0 dead (`.ufo/waves/round-99/w1-results.json`: 12
6545:   results, every output non-empty). By `.ufo/waves/round-99/w1-spec.json` roles, the policy attack
6546:   roles (reviewer, critic, mutation-tester, labrat) were 4 of 12 (33%): RW01Wording, RV02Counter,
6547:   CR01Records, MT01Mutants. The prefile ledger's attack roles (adding sentinel and connector) were
6548:   6 of 12 (50%): the four above plus SN01Bounds and CN01Overlap. The round-99 sentence
6549:   `SCORECARD.md@6776c667:6500` ("58% attack") is arithmetic-wrong under either set; the LOG's list
6550:   `LOG.md@6776c667:4065` ("CN01Overlap (attack)") is the ledger set and stays correct.
6551: - **Stale pointer.** The round-99 correction blocks cite the round-98 wave sentence as an unbound
6552:   `SCORECARD.md` line 6431. It was there at the measured commit, `SCORECARD.md@00394f3b:6431`
6553:   ("10 reported, 2 dead"), and had moved by the round-99 tip, `SCORECARD.md@6776c667:6446`
6554:   ("10 reported, 2 dead"), when the round-100 plan block was inserted above it. The LOG twin did not
6555:   move: `LOG.md@6776c667:4040` ("10 reported, 2 dead").
6556: - **Measured values.** `.ufo/waves/round-99/claims.json` still carries `"measured": "pending"` for
6557:   C1, C2 and C3 (frozen bytes, not rewritten). The measured predicate lines, byte-equal to the first
6558:   predicate line of `.ufo/waves/round-99/measured/c1.out`, `c2.out` and `c3.out` (each `exit=0`),
6559:   are recorded in `.ufo/waves/round-100/r99-measured.json`.
(The LOG twin is at LOG.md:4100–4121, with the identical words-form at LOG.md:4113–4114.)
```

### 6.3 Counter source lines cited

- `HEADING`/`POLICY_ATTACK`/`LEDGER_ATTACK` — `tools/round100-record-audit.py:57-60`
- `BOUND_RE`/`ANY_PTR_RE`/`PCT_RE` — `tools/round100-record-audit.py:63-66`
- `block()` — `tools/round100-record-audit.py:113-127`
- checks 3/4 presence — lines 134–135; check 5 — 136–144; check 6 — 145–146; check 7 — 147–154; check 8 — 155–167; check 9 — 168–178.

### 6.4 Round-99 derivation detail (supports §3)

`w1-results.json` at `6776c667` rows (name, agent): SC01Recon/scout, SC02Sources/scout, EX01Counter/executor, EX02Records/executor, EX03Autoload/executor, SB01Entry/scribe, RV01Wording/reviewer, RV02Counter/reviewer, CR01Records/critic, MT01Mutants/mutation-tester, SN01Bounds/sentinel, CN01Overlap/connector. `w1-spec.json` items: the same 12 names with `role` mirroring `agent`. `attack_seats(results)` under the gate (prefile-falsification.py:81–88) = the 6 ledger seats; policy (4) = RV01Wording, RV02Counter, CR01Records, MT01Mutants. `wave_role_mix` in the round-99 `claims.json` (at `6776c667`): `{'attack': '6 of 12 (50%)', 'connectors': '1', 'total': '12'}`. `min len(str(r.get('output')))` over the results rows is 4210 — no row is empty, so `dead=0` by the empty-output rule (counter lines 93–94), with the no-`status`-field caveat in the counter's own docstring (lines 20–23) and in the plan's disclosed limit (e).

### 6.5 Scratch harness (46 fixture commits, one per probe)

- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/q4.out` — Q4a–g + P0 (8 rows)
- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/q2.out` — W1–W7 (7 rows; W8–W10 anchors redone in q3)
- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/q3.out` — W8–W20 (14 rows, corrected anchors)
- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/final.out` — G1a, G1b, G2, G4, D1, G3b (6 rows)
- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/followup.out` — F1, F2, F3 (3 rows)
- `/fast/scratch/hyaku/kama-r100/RV01WordingC1/closeout.out` — E1–E5 (5 rows)
- Driver scripts: `q3probe.py`, `finalprobe.py`, `followup.py`, `closeout.py` (and the inline Q4/Q2 drivers), all under `/fast/scratch/hyaku/kama-r100/RV01WordingC1/`; copied to the out dir as `control-runs.md` equivalents below.

---

## 7. Required narrowing sentences (if the claim is kept, the claim must be re-stated as these)

> **N1 (checks 3/4 — label blindness).** "Checks 3 and 4 grade the *presence* of the derived fraction strings `4 of 12 (33%)` and `6 of 12 (50%)` somewhere in each block; they do not bind either string to the policy or the ledger label, and they do not bind the role lists named in the blocks. A block that swaps the two assignments while keeping both strings is green." (F1 falsifier: `tools/round100-record-audit.py:134-135`.)

> **N2 (checks 3/4/6 — substring left-context).** "Checks 3, 4 and 6 match by substring with no left-boundary anchor, so `14 of 12 (33%)`, `16 of 12 (50%)`, and `112 seats, 0 dead` satisfy the respective checks. The fractions and the seat count are not graded as standalone numbers with an explicit digit boundary." (Falsifiers: G1a/G1b/G2.)

> **N3 (check 5 — digit-only grammar, extend disclosed limit (a)).** "Check 5 rejects only percentages written as digits (`\d+%`). Percentages written in words (`58 percent`) and any other contradicting statement without a digit percentage — including a policy/ledger count stated in words — are not caught." (Falsifier: F3.)

> **N4 (check 7 — pointer grammar).** "Check 7's pointer grammar is `SCORECARD.md`, `LOG.md`, or `corpus/lessons/[\w.-]+.md` followed by `:<digits>`, with bound form requiring backticks, lowercase `#gh-`shorthands, a lowercase 7–40-char hex after `@`, and a `("…")` phrase with no quotes. A pointer written without a colon-and-digits (the words form `SCORECARD.md line 6431`, or the hash form `LOG.md#L4040`) is neither required to bind nor graded, and a pointer into a nested `corpus/lessons/sub/…` path is not in the grammar at all. The committed blocks themselves contain the words form (SCORECARD.md:6551–6552; LOG.md:4113–4114), which the counter does not see." (Falsifiers: W1, G3b, W4.)

> **N5 (check 7 — quoted punctuation).** "The counted notion of a bound pointer includes the counter's exact punctuation; a pointer that scans as a pointer to a human reader but omits backticks or the `@"` part is graded as unbound." (Disclosed limit (b) covers `tools/x.py:12`; extend it to the bound punctuation itself.)

> **N6 (check 9 — values, not file identity; first-line provenance).** "Check 9 binds the *values* of C1/C2/C3 in `r99-measured.json` byte-equal to the first predicate-prefixed line of each round-99 receipt and to that receipt's last `exit=` line being `exit=0`. The JSON layout (order, indentation) is not graded, and the derivation takes the first matching line when a receipt contains several." (Q4e: layout change is green by design.)

> **N7 (ledger provenance).** "The ledger set graded by the counter is a hardcoded copy of the gate's `ATTACK_ROLES` frozenset, not the gate itself. If the gate's set changes, the 6-of-12 value will be derived against the old set; the remedy is to import `ATTACK_ROLES` from the gate (currently `prefile-falsification.py:58-61`)."

If the claim is not re-stated, at least the verdict for the round is **falsified-wording**: the counter goes green on G1a, G1b, G2, F1, and F3, each of which contradicts the stated wording ("both state the derived … fractions", "12 seats, 0 dead", "contains no other digit percentage") without changing a graded number.

### Verdicts

- **VERDICT C1 falsifies-wording** — G1a/G1b/G2/F1/F3 are false greens under the Amendment-59 class; the narrowings N1–N7 are the required corrections.

### Outputs (out dir)

- `.ufo/waves/round-100/w1/out/RV01WordingC1/q4.out` — Q4a–g + P0 rows
- `.ufo/waves/round-100/w1/out/RV01WordingC1/q2.out` — W1–W7 rows
- `.ufo/waves/round-100/w1/out/RV01WordingC1/q3.out` — W8–W20 (corrected anchors) rows
- `.ufo/waves/round-100/w1/out/RV01WordingC1/final.out` — G1a/G1b/G2/G4/D1/G3b rows
- `.ufo/waves/round-100/w1/out/RV01WordingC1/followup.out` — F1/F2/F3 rows
- `.ufo/waves/round-100/w1/out/RV01WordingC1/closeout.out` — E1–E5 rows

### Tooling note

No tool installation or upgrade was required or performed. `python3` (3.14), `git`, and the lane's own counter/controls were used as they stand. No `pacman` invoked.
