# REV01Semantics — the frozen receipt-binding semantics C1 must preserve (kama round 76, w1)

Read-only seat. No lane path was written except this report and the receipts under
`.ufo/waves/round-76/w1/REV01Semantics/`. Every clone, fixture and temp tree lived in
`/fast/scratch/hyaku/kama-r76/REV01Semantics/` and was deleted before yielding.

Measured lane revision: `1a85a991fce5b76b60f88a5cab3df98d253b1a4a` (freeze), round-76 base
`b06cc612711560c53eef3ec21484c6963601262f`. Receipts:

| receipt | what it is |
|---|---|
| `fence-spans.out` | CommonMark 0.31.2 §4.5 spans of both record blobs, computed with `tools/append-only-audit.py`'s own byte primitives |
| `population.out` | every backtick token in the round-75 record, its fence state, the frozen resolver's answer, and the class at the freeze tip and at the round-76 base |
| `token-census.out` | all 30 wave-ish tokens and their resolution |
| `delta-commits.out` | per cited receipt: every commit in `<rev>..<tip>` with every touched path classified |
| `delta-union.out` | distinct out-of-scope paths per delta window |
| `tip-sweep.out` | the 11 live paths classified at all 17 tips of `dc58e513..1a85a991` |
| `clone-runs.out` | the frozen tools run in a scratch clone: before (exit 2), fence-stripped default scope, fence-stripped r76 scope, freeze tip |
| `scope-line.out` | the attainability search for the frozen after-line |

Commands actually run (all read-only against the lane; the clone is
`git clone --no-hardlinks` of the committed tree, then `git checkout --detach` + fixture commits
inside it, `git rev-parse --show-toplevel` asserted before every mutation). The seat's scratch
tree was deleted before yielding, as the bounds require; each receipt's header records the
command and the frozen module it imports, and the load-bearing measurement is re-runnable in one
snippet (this is exactly what produced `population.out`, `delta-commits.out` and `sweep.py`):

```python
import importlib.util, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("r72", "tools/round72-receipt-tip-binding.py")
r72 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r72)
specs = r72.default_record_paths(75) + ["PROVINCE.md", "SKILL.md", "corpus/**"]
print(r72._resolve_citation(".", "1a85a991", 75, "controls/build-spec.py", "lesson:126"))
for p in sorted(live_paths):  # the 11 paths of population.out
    print(p, r72._evaluate(".", "1a85a991", p, specs))
```

The clone leg (`clone-runs.out`) is `git clone --no-hardlinks <lane> <scratch>/clone`, detach at
`b06cc612` / `1a85a991`, strip CommonMark fences with the freeze control's own rule
(`.ufo/waves/round-76/controls/fence-dryrun.py`), commit in the clone, then run the frozen tool
with `--record-path` repeated for the five default specs plus the three ruled paths.

No tool was installed or upgraded; nothing needed it.

---

## 0. The reconstructed contract (what the three frozen layers actually do)

C1 composes three frozen tools. Their roles are **not** interchangeable:

| layer | file | what it decides | what it hands to the next layer |
|---|---|---|---|
| L1 resolver | `tools/round72-receipt-tip-binding.py` | token → receipt paths; then one class per receipt path (`stale`/`unbound`/`shifted`/`bound`) | a text line plus a `--json` verdict (`cited/bound/unbound/shifted/stale/findings/exit`) |
| L2 claim pass | `tools/round73-receipt-claim-binding.py` | imports L1 (`_load_base`, `tools/round73-receipt-claim-binding.py:102`) and reuses its resolver and record readers; adds a *line-scoped* tip-claim pass | r74 supersedes this pass |
| L3 claim pass v2 | `tools/round74-receipt-claim-binding.py` | imports L2, which imports L1 (`:86-91`); runs L1 as a subprocess (`:247`), re-reads the record, paragraph-scoped claims | `RECEIPT_CLAIM_V2 …` |

The invariant all three share: **a citation is a file claim about a receipt, and a receipt is
only evidence if the revision it names is still a faithful description of the tree at the tip.**
Nothing in the chain skips anything it cannot resolve; unresolvable means could-not-evaluate
(exit 2), never a silent pass (L1, `:24`, `:461-520`).

---

## 1. How a citation token is extracted, and what is excluded

Extraction is line-scoped and backtick-only:

```python
TOKEN_RE = re.compile(r"`([^`\n]+)`")          # tools/round72-receipt-tip-binding.py:119
```

`_citations()` (`:407-413`) walks **every line** of the two record blobs and yields each
single-line inline code span. Consequences that matter for C1:

- A code span may not cross a newline; a multi-line span yields two bogus tokens (the text before
  and after the newline), never one citation.
- Fence lines themselves are scanned: a line ` ``````text ` yields the token `text` (the outer
  first backtick cannot open the span, so the match starts at the second backtick). It is dropped
  later, but it is *seen* — L1 has no notion of a fenced block.
- Nothing else is a citation: HTML code, indented code blocks and bare prose are invisible.

Then `_resolve_citation()` (`:347-386`) normalises (`strip`, drop leading `./`, drop trailing
`,;:`) and expands under the declared notation list:

| notation | code | behaviour |
|---|---|---|
| fully-qualified wave path | `:353-357` | `.ufo/waves/round-<N>/…`; **never filtered** — classified strictly |
| section-relative | `:358-366`, `:367-374` | the token is resolved against `.ufo/waves/round-<N>/` when its first component is not a repo-root entry |
| brace alternatives | `BRACE_RE :120`, `_brace_expand :280-297` | each `{a,b}` alternative is a separate cited path; up to 8 expansion rounds; nested braces are not expanded |
| glob | `GLOB_CHARS :121`, `_glob_re :235`, `_glob_hits :299-305` | `*`/`?`/`[...]` matched by name against the tip tree; `**` crosses `/`; **no match → the literal pattern is the cited path** (so it reads `stale`) |
| directory | `_expand_one :313-321` | a trailing `/`, or a tree at the tip, denotes the receipt files beneath it; a directory with none is exit 2 |

Excluded (out of scope, never a finding — L1 docstring `:56-71` and code `:349-352`, `:358-372`):

- tokens carrying whitespace, `<`, `>`, `$`, `"`, `'`, `\`, `|`, a backtick, or `...`;
- `.ufo/` paths naming another round or a non-wave path (`:361-362`);
- repo-relative paths whose first component is a repo-root entry — `tools/`, `corpus/`, `plans/`,
  `registry/` … (`:363-365`);
- a section-relative token that neither carries a receipt extension nor exists at the tip — bare
  revisions (`b43e71a8`) and prose tokens (`_in_scope :332-344`).

Two asymmetries a re-implementation will get wrong (`token-census.out` measures both):

1. `_in_scope` is applied to the **expanded wave path**, not to the token, so
   `controls/build-spec.py` (section-relative) is in scope and *raises* when the wave path exists,
   while a section-relative **glob** without a receipt extension is dropped before expansion
   (`_in_scope:343` returns `is_receipt(pattern)`), which is why the live token `controls/*.py`
   (`corpus/lessons/round-75.md:161`) is silently out of scope. A *fully-qualified* glob over the
   same files is not filtered and raises instead.
2. A receipt extension claims a path even when the path is absent (`stale`); a non-receipt
   extension claims it only when the blob/tree exists.

---

## 2. The declared record-path set, where it lives, and what it misses

Defined at `tools/round72-receipt-tip-binding.py:217-225`:

```python
def default_record_paths(round_no):
    return [".ufo/waves/round-{}/".format(round_no), "corpus/lessons/",
            "LOG.md", "SCORECARD.md", "corpus/README.md"]
```

`--record-path` **replaces** the list (`:920-960`); matching is prefix for a trailing `/`, exact
apart from that (`_record_match :267-276`). The docstring declares the complement explicitly
(`:88-92`): "Instrument inputs (`tools/`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`,
`corpus/knowledge/`, `registry/`, `plans/`) are never record paths."

Measured — every distinct path in each delta that the declared set (r72 default **plus** the r76
extension `PROVINCE.md`, `SKILL.md`, `corpus/**`) does **not** cover (`delta-union.out`):

| delta | out-of-scope paths | introduced by |
|---|---|---|
| `dc58e513..1a85a991` (what the 3 base-rev receipts see) | **20** — `plans/round-75-claims.md`, `plans/round-76-claims.md`, `registry/append-only-accepted.tsv`, `registry/append-only-contract.tsv`, `registry/append-only-declarations.md`, `tools/pre-report-gate.py`, `tools/round74-receipt-claim-binding.py`, `tools/round75-append-accepted.py`, `tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py`, and the 10 `.ufo/waves/round-76/{controls,measured/before}/*` files | `0908bab5`, `10f37171`, `b8ed2568`, `1a85a991` |
| `c9ab73d8..1a85a991` (what the 6 work-tip receipts see) | **11** — `plans/round-76-claims.md` + the same 10 `.ufo/waves/round-76/**` files | `1a85a991` |

So the set misses, in this lane's own history: the round's frozen **plan** (`plans/`), the
instrument **data** (`registry/`), the instrument **sources** (`tools/`) and **the next round's
wave** (`.ufo/waves/round-76/`). Those four classes are exactly the ones the claim's ruling (b)
refuses to widen, and they are the reason §6 shows the frozen after-line is arithmetically
unreachable.

The extension buys exactly one thing, measured: the `PROVINCE.md` capability-row commit
`c9ab73d8` stops shifting the three base-rev receipts. It does **not** bind them, because the
next-oldest offender is `registry/append-only-contract.tsv` @ `b8ed2568` (`clone-runs.out` §D).

---

## 3. What `shifted` means, and what `bound` requires

`_evaluate()` (`tools/round72-receipt-tip-binding.py:430-445`) is one ordered classifier, first
match wins:

| # | test | class | detail line |
|---|---|---|---|
| 1 | `git cat-file -e <tip>:<path>` fails (`:431-433`) | `stale` | `absent at <tip>` |
| 2 | no `tip=`/`rev=` 40-hex value among the **first five lines** (`HEADER_WINDOW = 5` `:115`; `_header_rev :416-428`) | `unbound` | `no tip=/rev= header among the first 5 lines` |
| 2b | two *different* revisions in that window (`:426-427`) | `unbound` | `conflicting header revisions: …` |
| 3 | header rev is not a commit in this repository (`:437-438`) | `shifted` | `header rev <rev> is not a commit in this repository` |
| 4 | header rev is not an ancestor of the tip (`_is_ancestor :184-185`, `merge-base --is-ancestor`) | `shifted` | `header rev <a> is not an ancestor of <b>` |
| 5 | some commit in `rev..<tip>` touches a path outside the record set (`:441-444`) | `shifted` | `<path> touched by <commit12>` |
| 6 | otherwise | `bound` | `rev=<rev>` |

Header parse details that a duplicate implementation gets wrong:

- `HEADER_RE = (?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])` (`:116`):
  the **key** is lower-case only (r74's v2 pass re-reads it case-insensitively,
  `tools/round74-receipt-claim-binding.py:80-83` — a different layer, do not mix them); the
  **hex** is any case; exactly 40 hex, so a 64-hex sha256 never matches; `base_rev <hex>` does not
  match (no `=`, and `rev` is preceded by a word character), which is why
  `.ufo/waves/round-75/controls/freeze.txt` is `unbound`;
- a short revision is not a header;
- `rev == tip` passes tests 3-5 with an empty delta → `bound`.

`shifted` therefore means, precisely: **the receipt names a revision whose tree-to-tip history is
not confined to record paths** — either the named rev is not in this graph, or it is not an
ancestor, or some commit between it and the tip changed a path the round did not declare as its
own record. It is a statement about the *delta*, never about the receipt's content, and the detail
names **one** offending (commit, path) pair — the one found **first in `git rev-list rev..tip`
order, i.e. the newest** (`:441-443`). That first-match rule is load-bearing for §6.

---

## 4. Why a fully-qualified non-receipt citation is UNREADABLE, not a finding

Because L1 has no class for it, and its exit map has no slot: the three classes are
`unbound|shifted|stale` (`:15-16`), and a token that resolves to a non-receipt cannot be any of
them. Resolution happens *before* classification, in `_expand_one` (`:322-326`):

```python
if not is_receipt(cand):
    raise CouldNotEvaluate("cited path is not a receipt file ({}): {} ({})" …)
```

and `_resolve_citation` calls `_expand_one` for every brace alternative without catching (`:375`).
`audit()` does not catch it; `main()` catches `CouldNotEvaluate`, prints
`RECEIPT_TIP_BINDING_UNREADABLE <msg>` to **stderr** and returns **2** (`:948-951`).

The three layers then compose, and each adds exactly one wrapper:

| layer | mechanism | emitted text |
|---|---|---|
| L1 `round72` | raise → exit 2 | `RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-75/controls/build-spec.py (corpus/lessons/round-75.md:125)` |
| L2 `round73` | `_run_base` sees rc==2 → `raise CouldNotEvaluate("base tool could not evaluate: " + stderr)` (`tools/round73-receipt-claim-binding.py:133-134`) | would print `RECEIPT_CLAIM_BINDING_UNREADABLE …` (`:743`) |
| L3 `round74` | `audit()` calls `r73._run_base` (`tools/round74-receipt-claim-binding.py:239`); `main()` catches both classes (`:559-566`) | `RECEIPT_CLAIM_V2 CouldNotEvaluate: base tool could not evaluate: RECEIPT_TIP_BINDING_UNREADABLE …` |

**The decision is L1's.** L2 and L3 only propagate and relabel; neither re-examines the token —
by the time they run, the base gate has already refused to produce a verdict. Reproduced byte-for-
byte in the scratch clone at `b06cc612` (`clone-runs.out` §A) and equal to the committed before
receipt `.ufo/waves/round-76/measured/before/c1-receipt-claim.out`.

Why fail-closed rather than a finding is also a deliberate contract, not an accident: L1's
docstring `:24` and `:56-71` say a qualified token "is never filtered: it is classified strictly,
so an absent or non-receipt qualified citation is exit 2, never a silent skip", and the exit map
`:27-30` reserves exit 2 for "a cited path that is not a receipt file". The consequence for a
round is total: **one fenced `.py` token poisons every other citation in the record** — 11
receipts and 2 legacy findings are never classified.

---

## 5. What a fence-aware reading changes, citation by citation

### 5.1 Fence spans (audit primitives, file-global)

`fence-spans.out`, computed with `tools/append-only-audit.py:323-346` (`fence_open`/`fence_close`)
— the same definition ruling (a) binds the counter to:

| file (at `1a85a991`) | length | span (file lines) | content lines |
|---|---|---|---|
| `SCORECARD.md` | 4132 | 4106-4112 (6 backticks) | the five held §Round 75 rows |
| `SCORECARD.md` | | 4122-4131 (6 backticks) | the held authority/axes head lines |
| `corpus/lessons/round-75.md` | 163 | 124-133 (6 backticks) | §Superseded bytes (the `.py` pointers) |
| `corpus/lessons/round-75.md` | | 140-143 (3 backticks) | §Restored paragraph (one `.py` pointer) |

Both files end outside a fence. Fence state must be computed **file-globally** before the round
section is cut: L1's `_round_section` (`:388-405`) is fence-blind and would truncate the section at
a `## ` line inside a fence. Measured: the only `## ` line inside the round-75 section is the
heading itself (file line 4053), so this record is not affected — the `fence-unclosed` and
`fence-quoted-skip` fixtures are.

### 5.2 Every wave-ish token, and the fence's effect (`token-census.out`)

30 backticked tokens mention the wave dir or a section-relative receipt root. Classified:

- **11 live receipt paths** (the plan's `live_citations=11`) — unchanged by fencing:
  `assimilation/summary.out` (lesson:71, via the directory token `assimilation/`),
  `controls/freeze.txt` (lesson:149, via `controls/`), the 3 `measured/before/*` and the
  6 `measured/after/*` receipts (SCORECARD:4059-4065, repeated in the lesson at 15, 29, 40).
- **4 fenced non-receipt instances → 1 distinct path** (`fenced_quoted=1`):
  `.ufo/waves/round-75/controls/build-spec.py` at lesson:125 and :141, plus the section-relative
  `controls/build-spec.py` at :126 and :130 which resolve to the same wave path.
- **9 fenced receipt instances** (SCORECARD:4108-4111, the held rows) — exact duplicates of live
  paths; on a set-valued population they change nothing.
- **4 dropped tokens** (`measured/…` SCORECARD:4084, `controls/*` :4116, `controls/*.py`
  lesson:161, and the `text` info-string residue of every fence line) — out of scope under §1.

So the fence scope is load-bearing for exactly one thing on real bytes: it removes the fatal
`.py` **path**, not any receipt. That is why `live_citations` is fence-invariant here and why
`fenced_quoted` must count *distinct resolved paths* (1), not tokens (4).

### 5.3 Expected classification, citation by citation, under the plan's scope rulings

Population and headers measured at the freeze tip (`population.out`; classes by the r76 declared
scope = r72 default + `PROVINCE.md`, `SKILL.md`, `corpus/**`):

| # | live path | header at tip | class at `b06cc612` | class at `1a85a991` (freeze) | frozen target says |
|---|---|---|---|---|---|
| 1 | `.ufo/waves/round-75/assimilation/summary.out` | none | `unbound` (no header) | `unbound` | `unbound` ✓ |
| 2 | `.ufo/waves/round-75/controls/freeze.txt` | none (`base_rev <hex>`) | `unbound` (no header) | `unbound` | `unbound` ✓ |
| 3 | `.ufo/waves/round-75/measured/before/c1-mutants.out` | `dc58e513` | **`shifted`** (registry @ b8ed2568) | **`shifted`** (round-76 wave @ 1a85a991) | `bound` ✗ |
| 4 | `.ufo/waves/round-75/measured/before/c2-mutants.out` | `dc58e513` | **`shifted`** | **`shifted`** | `bound` ✗ |
| 5 | `.ufo/waves/round-75/measured/before/c3-audit.out` | `dc58e513` | **`shifted`** | **`shifted`** | `bound` ✗ |
| 6 | `.ufo/waves/round-75/measured/after/append-only-audit.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |
| 7 | `.ufo/waves/round-75/measured/after/c1-pins.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |
| 8 | `.ufo/waves/round-75/measured/after/c2-survivors.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |
| 9 | `.ufo/waves/round-75/measured/after/c3-append-accepted.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |
| 10 | `.ufo/waves/round-75/measured/after/population.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |
| 11 | `.ufo/waves/round-75/measured/after/selftests.out` | `c9ab73d8` | `bound` | **`shifted`** | `bound` ✗ at freeze |

Fenced entries (quoted history, never classified):

| where | token | resolved path | class |
|---|---|---|---|
| lesson:125 | `.ufo/waves/round-75/controls/build-spec.py` | same | **fenced-quoted** (`fenced_quoted=1`) |
| lesson:126, :130 | `controls/build-spec.py` | same path | fenced-quoted (same distinct path) |
| lesson:141 | `.ufo/waves/round-75/controls/build-spec.py` | same | fenced-quoted (same distinct path) |
| SCORECARD:4108-4111 | the 9 held-row receipt citations | the 9 live receipt paths | not counted; already live |

---

## 6. The measured disagreement: the frozen after-line is unreachable

**Frozen:** `RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
nonreceipt=0 unclassified=0`, exit 0.

**Measured with the frozen tools and the declared scope** (`clone-runs.out`, `tip-sweep.out`,
`population.out`):

| tip | bound | unbound | shifted | first offender for the shifted class |
|---|---|---|---|---|
| `b06cc612` (round-76 base) | 6 | 2 | 3 | `registry/append-only-contract.tsv touched by b8ed25682958` |
| `c9ab73d8` (round-75 work tip) | 6 | 2 | 3 | same |
| every tip in `ba9f7248..b06cc612` (13 tips) | 6 | 2 | 3 | same |
| `1a85a991` (freeze) | **0** | 2 | **9** | `.ufo/waves/round-76/controls/fence-dryrun.py touched by 1a85a991fce5` |
| `max bound` over the whole range `dc58e513..1a85a991` (17 tips) | **6** | | | |

`bound=9` occurs at **no tip**. The reason is structural, not a matter of choosing a tip:

- receipts 6-11 need a tip that contains their current bytes (`rev=c9ab73d8`), i.e. a tip that is
  a descendant of `c9ab73d8`;
- every such tip has `0908bab5` (which adds `plans/round-75-claims.md`) and `b8ed2568` (which
  touches `registry/append-only-contract.tsv`) in `dc58e513..tip`;
- `plans/` and `registry/` are out of scope under the r72 default set **and** under ruling (b);
- therefore receipts 3-5 are `shifted` at every such tip, so the maximum is 6.

**Root cause of the plan's arithmetic (6 → 9).** `_evaluate` reports the *newest* offending
commit only (`:441-443`). At the base revision the newest offender for the three base-rev receipts
was `PROVINCE.md @ c9ab73d8`, so the dry run's finding lines read
`… shifted … :: PROVINCE.md touched by c9ab73d84205` (`.ufo/waves/round-76/measured/before/
c1-fence-dryrun.out`). Adding `PROVINCE.md`/`SKILL.md`/`corpus/**` to the record set does not bind
those receipts — it merely *reveals the next offender*, and that one is a `registry/` delta ruling
(b) keeps shifting. Measured both ways in the same clone:

```
## C. stripped, round-72 default record paths
RECEIPT_TIP_FINDING shifted …/c1-mutants.out :: PROVINCE.md touched by c9ab73d84205      (×3)
RECEIPT_TIP_BINDING round=75 cited=11 bound=6 unbound=2 shifted=3 stale=0                 exit=1

## D. stripped, round-76 declared record paths
RECEIPT_TIP_FINDING shifted …/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958  (×3)
RECEIPT_TIP_BINDING round=75 cited=11 bound=6 unbound=2 shifted=3 stale=0                 exit=1
```

C is byte-identical to the plan's dry run; D is the same claim's scope with the ruling applied —
the class does not move. **C1's fence ruling (a) is load-bearing** (it converts exit 2 into a
graduated classification of 11 paths); **its record-path ruling (b) is not sufficient** for the
frozen target.

Three candidate readings and what each yields on these bytes (only one is consistent with the
claim's own kill rule):

| reading | "the tip" | yields | consistent with `shift-tools`? |
|---|---|---|---|
| **R1** literal: the repository tip | `master` | bound 0..6, never 9 | yes |
| R2 self-binding: the revision the citing sentence claims | the receipt's own rev | bound 9, unbound 2, shifted 0 — the frozen line | **no**: the empty delta makes the `shift-tools` fixture arm unfireable, because there the sentence and the tip are the same commit |
| R3 the round's recorded work tip | `c9ab73d8` | bound 6, shifted 3 | yes |

R2 is rejected by the claim's own kill rule, so R1 is the only reading that keeps the arms
meaningful — and under R1 the after-line cannot be printed by any faithful counter. This is a
freeze defect in the counter's expected line, not in the modules. **Do not edit the plan**
(freeze discipline). The honest routes are: (i) report C1 red with the measured line and the
proof, and land the fence scope as the round's real operability gain; or (ii) declare a new claim
next round with a record-path set that admits the round's own instruments — which would gut the
`shift-tools` arm and needs its own freeze, not a post-hoc edit here.

Two smaller spec gaps in the same frozen sentence (report, do not silently choose):

- **`stale` has no counter.** The exit-1 clause names "a stale receipt" but the summary line has
  no `stale=` field. Recommendation: print `RECEIPT_SCOPE_FINDING stale <path> :: absent at
  <tip>`, exit 1, and let `bound+unbound+shifted+nonreceipt+unclassified < live_citations` by the
  number of stale findings, so the gap is attributable. Add a `stale-at-tip` arm.
- **`unclassified` is undefined.** It can only sensibly mean "a live path that landed in no
  class" (a module bug guard). Recommendation: any nonzero value is exit 1 with
  `RECEIPT_SCOPE_FINDING unclassified <path> :: <where>`, never a silent 0.

---

## 7. Behavioural spec for EX01 (`tools/round76-receipt-scope.py`)

**Inputs.** `--repo` (default `.`), `--round` (default 75 for this claim), `--tip` (default
`master`). Read every blob at the **tip commit**, never the worktree, never the index — same as
L1 (`_blob :162-168`).

**Population.** Import `tools/round72-receipt-tip-binding.py` and `tools/append-only-audit.py` by
path (`importlib.util.spec_from_file_location`, `sys.dont_write_bytecode = True`); never copy
their bytes. Population sources: `SCORECARD.md`'s `## Round 75` section and all of
`corpus/lessons/round-75.md`.

**Fence.** Compute the whole-file fence map with the audit's `fence_open`/`fence_close`
(`tools/append-only-audit.py:323-346`) **before** cutting the section. A line inside a fence is
*quoted history*: it contributes no citation and cannot raise. A file (or the record region, if
you scope it) that ends inside an open fence is `CouldNotEvaluate` → exit 2 (the audit itself does
not fail on an unclosed fence; the counter adds that rule).

**Classes.** For each **live** (unfenced) citation path, exactly one, in this order, reusing
L1's `_header_rev`, `_commit_sha`, `_is_ancestor`, `_rev_list`, `_diff_paths`, `_record_match`:

1. blob absent at tip → `stale`;
2. header window (first 5 lines) empty or conflicting → `unbound` (named, non-failing);
3. header rev not a commit / not an ancestor → `shifted`;
4. some commit in `rev..tip` touches a path outside `default_record_paths(75) +
   ["PROVINCE.md", "SKILL.md", "corpus/**"]` → `shifted`;
5. otherwise → `bound`.
6. a live citation that resolves to a **non-receipt** path → `nonreceipt` (exit 1) — the class L1
   lacks; it must be computed from the resolver, not by re-parsing tokens.

Paths that resolve to a non-receipt **only** inside fences → `fenced_quoted`, counted as distinct
resolved paths.

**Output grammar** (stdout, in this order; each finding line first, then the one summary line):

```
RECEIPT_SCOPE_FINDING shifted <path> :: <path> touched by <commit12>
RECEIPT_SCOPE_FINDING stale <path> :: absent at <tip>
RECEIPT_SCOPE_FINDING nonreceipt <path> :: not a receipt file (<ext>) cited at <where>
RECEIPT_SCOPE_FINDING unclassified <path> :: <where>
RECEIPT_SCOPE_QUOTED <path> :: <first where it is quoted>      # informational, never fails
RECEIPT_SCOPE_UNBOUND <path> :: <reason>                        # informational, never fails
RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=N unbound=2 shifted=M nonreceipt=0 unclassified=0
```

The summary line is one line, field order frozen, and on a clean run
`bound+unbound+shifted+nonreceipt+unclassified == live_citations`. Exit 0 iff
`shifted==0 and nonreceipt==0 and unclassified==0` and the live population is non-empty and no
fence is unclosed; exit 1 on any `RECEIPT_SCOPE_FINDING`; exit 2 on could-not-evaluate (missing
self-record, unclosed fence, empty live population, unreadable receipt at the tip, CLI misuse).

**Worked examples** (each is the exact output the classifier must produce; all four are
reproducible from real bytes except #4, which is the record's own line 125 with the fence removed):

1. **bound** — `.ufo/waves/round-75/measured/after/c1-pins.out` at tip `b06cc612`: header
   `# rev=c9ab73d8…` (line 1 of 5), rev is a commit and an ancestor, and
   `c9ab73d8..b06cc612` touches only `SCORECARD.md`, `corpus/lessons/round-75-verifier-
   spotcheck.md`, `.ufo/waves/round-75/measured/after/pre-report-gate.out` (all record). Emits no
   finding; increments `bound`.
2. **shifted** — `.ufo/waves/round-75/measured/before/c1-mutants.out` at tip `b06cc612`:
   ```
   RECEIPT_SCOPE_FINDING shifted .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
   ```
   (under the r76 scope; the r72 default scope says `PROVINCE.md touched by c9ab73d84205`).
   Exit 1.
3. **unbound** — `.ufo/waves/round-75/assimilation/summary.out`:
   ```
   RECEIPT_SCOPE_UNBOUND .ufo/waves/round-75/assimilation/summary.out :: no tip=/rev= header among the first 5 lines
   ```
   Printed, counted in `unbound`, **does not fail**. `controls/freeze.txt` is the second: its
   `base_rev dc58e513…` is not a `tip=`/`rev=` header.
4. **nonreceipt** — the lesson's line 125 token, live instead of fenced:
   ```
   RECEIPT_SCOPE_FINDING nonreceipt .ufo/waves/round-75/controls/build-spec.py :: not a receipt file (.py) cited at corpus/lessons/round-75.md:125
   ```
   Exit 1. (L1's own behaviour on the same bytes is exit 2 — that is the defect C1 removes.)
5. **fenced-quoted** — the same token inside the §Superseded-bytes fence (lesson:124-133) or the
   §Restored-paragraph fence (lesson:140-143):
   ```
   RECEIPT_SCOPE_QUOTED .ufo/waves/round-75/controls/build-spec.py :: corpus/lessons/round-75.md:125
   ```
   Counted once in `fenced_quoted` (distinct resolved path), never a finding, never in the live
   population.

**Arms** (module `--selftest`, fixture repos under `--work`, print
`RECEIPT_SCOPE_SELFTEST pass=N fail=0`): `fence-quoted-skip`, `fence-live-nonreceipt`,
`fence-none-live` (only receipt citation fenced → exit 2), `fence-unclosed` (exit 2),
`shift-selfdesc` (`PROVINCE.md` delta does not shift), `shift-tools` (`tools/` delta does),
`unbound-named` (header-less printed, exit 0), plus `stale-at-tip` and `unclassified-guard` for
the two gaps above. The `shift-tools` fixture must keep a *non-empty* delta between the receipt's
header and the tip, otherwise the arm is vacuous (that is exactly why reading R2 is unusable).

**Do not tune.** On the real round-75 record the counter must print the line the bytes give — at
`master` today: `RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=6 unbound=2
shifted=3 nonreceipt=0 unclassified=0` **iff** the tip is `b06cc612`-era, and `bound=0 … shifted=9`
at the freeze tip `1a85a991`. Neither equals the frozen target; the difference is §6, and it is
reported, not fixed in the counter.

---

## 8. Disagreements with the frozen plan (reported, not edited)

1. **§C1 predicate's expected line.** `bound=9 … shifted=0` is unattainable: max `bound=6` over all
   17 tips of the round-75..freeze history, because the three base-rev receipts are shifted by the
   round's own `plans/`, `registry/` and `tools/` deltas, which ruling (b) keeps out of scope
   (§6). Consequence: C1 cannot exit 0 as frozen, even with a perfect fence-aware counter.
2. **§C1 motivating sentence, "three before receipts shifted by the self-description commit
   c9ab73d8".** Half true: `PROVINCE.md @ c9ab73d8` is the *newest* offender the fence-blind dry
   run happens to print; the *binding* offenders are `registry/append-only-contract.tsv` and
   `registry/append-only-declarations.md` @ `b8ed2568`, plus `tools/*` and `plans/*` @ `10f37171`
   and `0908bab5`. The distinction matters: widening the record path set for `PROVINCE.md` cannot
   bind these receipts.
3. **§C1 exit map vs summary line: `stale`.** Exit 1 is required for "a stale receipt", but the
   frozen summary line carries no `stale=` field (§6).
4. **§C1 `unclassified` field undefined** in the predicate; recommended meaning is a module-bug
   guard that fails when nonzero (§6).
5. **Minor:** the plan's C1 text calls the citation population "the round-75 self-record's"; the
   population includes a *directory* citation (`assimilation/`) and a `controls/` directory
   citation, so `live_citations=11` is 11 **paths**, not 11 tokens (30 wave-ish tokens exist;
   `token-census.out`).

---

## 9. Confidence and limits

- **High** (byte-verified, from the frozen modules and the lane's history): §§1-5, 7 and
  disagreements 1-3. Every class in §5.3 and every delta in §2 was produced by importing the
  frozen modules, not by re-implementing them; the clone runs reproduce the plan's own dry run
  byte-for-byte before extending it.
- **High**: the §6 unattainability result — the sweep covers every tip on `master` in
  `dc58e513..1a85a991`, and the ancestry argument covers tips outside it (before receipts are
  shifted at every tip ≥ `0908bab5`; receipts 6-11 require a tip ≥ `c9ab73d8`).
- **Inference, flagged:** reading R2 (self-binding) is the only reading I can construct that
  yields the frozen line; I reject it because it makes the claim's own `shift-tools` arm
  unfireable. If the plan's author intended a fourth reading, it is not recoverable from the
  frozen text or from the controls committed at the freeze.
- **Not checked:** whether the in-flight `tools/round76-receipt-scope.py` (untracked at the time I
  looked, sibling seat EX01ReceiptScope) lands the frozen target or reports the divergence — its
  receipts and review belong to EX01/RV01, not to this seat.
