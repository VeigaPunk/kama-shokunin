# REV01Semantics — the two interpretation readings and the five C2 mutant classes, derived from committed bytes

Round 75, wave 1, lane `kama-shokunin`. Read-only derivation: **no production file was edited**, no
byte-frozen tool touched, no other seat's file read for writing. Every claim below is tied to a line of the
freeze-commit bytes or to a run whose receipt is in `receipts/`.

**Provenance.** Lane base `dc58e51315e79d36df5fc530c95fbd3aecbf7593` == freeze commit
`0908bab5cbf0ab6b435144fc525a3e18443dc08f` for the two target modules: both files hash identically at base and
freeze (`receipts/hashes.txt`):

```
c2c7b08e...1709ba05  tools/round74-selfdesc-canon.py
5c6174c4...e1e022    tools/round74-receipt-claim-binding.py
```

**Disclosure — the working tree drifted while I worked.** `tools/round74-receipt-claim-binding.py` is
`M` in the lane worktree (581 lines) because the C2 seat is adding its two arms; the worktree copy is *not*
the freeze bytes (539 lines). Every line citation here is to the bytes obtained with
`git show 0908bab5:tools/...`, extracted once into scratch and sha256-checked against the table above. The
drifting worktree copy was never executed or cited. `git status --porcelain` at derivation start is in
`receipts/hashes.txt` (seven tracked files modified, including the C2 module, plus untracked additions by
concurrent seats).

**Method.** (1) Read the code path, not the docstring. (2) Build minimal fixtures and run the *committed*
modules over them; run the exact frozen mutants from
`.ufo/waves/round-75/controls/mutation-control.py` (C1_MUTANTS / C2_MUTANTS) over copies in scratch.
(3) Compare the observed values to the plan's sentences. No tool install was needed (python3 + read-only git).

Scratch `/fast/scratch/hyaku/kama-r75/REV01Semantics/` held the clone, the freeze-byte copies, the mutants
and the fixtures; it was deleted after the receipts were copied into `receipts/` (see §8).

---

## 1. `tools/round74-selfdesc-canon.py` — what the code computes

### 1.1 Three table populations, one dedupe

`capability_tables()` (`tools/round74-selfdesc-canon.py:184-220`) classifies each line of `SCORECARD.md`:

| kind | test | line |
|---|---|---|
| `bold-canon` | `BOLD_CANON_RE` (L104: `canonical list as of round\s+(\d+)\*\*`) matches **anywhere on the line** (search at L193; branch L196-198) | 193, 196-198 |
| `canon` | `CANON_HEADING_RE` matches **and** `_HEADING_RE` (`^\s*#|\*\*`) matches | 199-201 |
| `demo` | `DEMO_HEADING_RE` matches **and** `line.lstrip().startswith("#")` | 202-204 |

Per-round resolution is `per_round` (L191, L207-218), first table wins unless a higher-priority kind
appears:

- entry absent → store (L209-210);
- an existing `demo` blocks every later table at that round (L211-212);
- a new `demo` replaces a `canon`/`bold-canon` (L213-214) — demo wins at equal round in either order;
- an existing `canon` blocks a later `bold-canon` (L215-216) — bold wins over canon;
- a later `canon` replaces an earlier `canon` (L217-218).

`tables` is then sorted by round (L219).

The canon side is **not** this table: `resolve()` calls the byte-frozen r42 `canon()`
(`tools/round42-selfdesc-reconcile.py:141-148`), whose regex (L145) requires the literal `**` immediately
after the digits and which reads the first `|` block below the heading (`table_rows`, L131-138; drops the
first two rows, returns `[]` for fewer than two). So `canon_round`/`canon_rows` are the **newest bold**
heading's resolution regardless of the markup-agnostic table list (L226).

### 1.2 Which names enter `total`

`total` is a **set of names**: `total = set(canon_names) | demonstrated` (L244).

- `canon_names` = first column of the r42 bold canon rows (L227; `_names_below` L180-181 =
  `[row[0] for row in table_rows(...)]`).
- `demonstrated` = union of first-column names over every deduped table whose round is **strictly greater**
  than `canon_round` (L236-239), of any kind (`bold-canon`, `canon`, `demo`).

Consequences:
- `total` is deduplicated by name; `canon_rows` is a **row count** (L248). They are equal only when the
  canon's names are distinct — fixture `p1h` (canon rows `alpha, alpha, beta`) prints
  `canon_rows=3 total=2`, exit 0 (`receipts/canon-probes.txt`).
- Names already in the canon also count into `demonstrated` when a **newer** table repeats them
  (fixture `p1e`: `demonstrated=5` while only `invisible=2`).
- `invisible = sorted(demonstrated - set(canon_names))` (L240); exit is `0 if not invisible else 1`
  (L593) — findings are printed before the summary line (L289-293).

### 1.3 Names carried only by tables **older** than the canonical round

They enter **none** of the three counters:
`round < canon_round` fails the `>` test at L238, so they are not in `demonstrated`; `total` is
`canon ∪ demonstrated` (L244), so they are not in `total`; `invisible` is a subset of `demonstrated`
(L240), so they are not findings. A record can therefore demonstrate a capability it never lists and still
exit 0.

Verified (`receipts/p1.txt`), bold canon round 71 with `alpha,beta,gamma`, plus a round-60 table carrying
those three **and** `delta,epsilon`:

```
p1a_older_canon (round-60 table is an unbolded canonical list)
  SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0   exit=0
p1b_older_demo  (round-60 table is "### Capabilities demonstrated in round 60")
  SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0   exit=0
```

The result does not depend on the older table's kind, only on its round.

### 1.4 Canonical round **newer** than every other table

`demonstrated` is empty, `total = |canon names|`, `invisible=0`, exit 0. Anything the record demonstrates
in an older table disappears from every emitted number. `p1c` — bold canon round 74 with three rows, a
round-73 demonstrated table with a fourth name `legacy-audit`:

```
SELFDESC_CANON_V2 canon_round=74 canon_rows=3 demonstrated=0 total=3 invisible=0   exit=0
```

`legacy-audit` is nowhere in the output. This is the F1b reading applied to the opposite boundary; the plan
pins it for older tables (§C1 P1) and the same code path gives it for "newer than everything".

Two adjacent boundaries, both derived and run (`receipts/canon-probes.txt`):

- a canonical heading with **no parsable rows** prints `canon_round=71 canon_rows=0 ... total=0`, exit 0 —
  the exit-2 arm `no capability table can be parsed` (L229-230) does not fire because a heading exists;
- a record with no recognised heading at all exits 2 with that message.

### 1.5 Dead and inert code that the route depends on

- `newest_names` (L232-235) is computed and **never read** (absent from the returned dict, L245-255).
- `emit()` (L263-269) reads `document["findings"]`, which `resolve()` never sets; only `run()` sets it
  (L288). `emit` has no caller in the module; the CLI path is `run()` (L271-295).
- The demo-wins tie-break (L211-214) is **inert for every printed counter**: a same-round demo entry is
  never read by `demonstrated` (strict `>`), and `newest_names` — the only consumer that would read it — is
  dead. This contradicts the docstring's L186-188 promise ("a demonstrated table wins over a canonical table
  at the same round, so the demonstrated additions are never hidden by a same-round canonical list"):
  fixture `p1f` (bold canon 71 + demonstrated 71 with `same-round-extra`) prints
  `total=3 invisible=0`, exit 0 — the name is hidden from `total`, from `invisible` and from the finding
  list (`receipts/p1.txt`). Same result with the two table orders swapped (L207-218), verified by calling
  `capability_tables()` directly (`receipts/canon-dedupe.txt`):

```
canon_then_demo_same_round -> capability_tables = [(71, 6, 'demo')]
demo_then_bold_same_round  -> capability_tables = [(71, 0, 'demo')]
both: canon_round=71 canon_rows=1 demonstrated=0 total=1 invisible=[] newest_round=71
```

### 1.6 A structural invariant worth stating

`has_token` is evaluated on the `"\n"`-joined paragraph, and `_claim_kind` re-evaluates the same three
substring tests per line. Because every tip token contains a space, a token can never straddle a line
break, so `token_idx` is non-empty whenever `has_token` is true and the `min()` at
`round74-receipt-claim-binding.py:152` cannot see an empty generator. (Inference from the two tests; I did
not find a fixture that can violate it.)

---

## 2. `tools/round74-receipt-claim-binding.py` — what the code computes

### 2.1 Receipt header parse — `_header_rev_v2()` (L105-116)

- window = first `HEADER_WINDOW = 5` lines (L79, L107), decoded `utf-8` with `replace`.
- `HEADER_RE_V2` (L82): `(?:^|[^\w-])(?:#\s*)?(?:tip|rev)=([0-9a-fA-F]{40})(?![0-9a-fA-F])` with `re.I` —
  case-insensitive key **and** hex; optional `#` prefix; exactly 40 hex digits, not preceded by a word
  character/hyphen, not followed by a hex digit.
- every match in the window is collected and lower-cased (L109-111).
- none → `(None, "no tip=/rev= header among the first 5 lines")` (L112-113);
- distinct values > 1 → `(None, "conflicting header revisions: ...")` (L114-115) — a conflict is a
  *finding source*, never a crash;
- otherwise `(first rev in the window, "")` (L116).

### 2.2 The paragraph pass — `_claim_pass_v2()` (L156-212)

Records: the `## Round <N>` section of `SCORECARD.md` at the tip plus `corpus/lessons/round-<N>.md` at the
tip (loaded through the frozen r73 `_read_records`). Paragraphs are blank-line separated with a 1-based start
line (`_paragraphs`, L119-135). For each paragraph:

1. `text = "\n".join(plines)`, `low = text.lower()` (L165-166).
2. `has_token` — one of `("at the report tip", "at the tip", "report tip")` (L75) appears in `low` (L167).
3. `cited` — every backtick token (`base.TOKEN_RE`, r72 L119) resolved by `_resolve_citation` (r72 L347-...);
   unresolvable/out-of-scope tokens are dropped, duplicates collapsed in order (L168-175).
4. **No cited path → the paragraph is skipped entirely** (L176-177), before revision mentions are even
   computed. A revision mention in a citation-free paragraph is ungraded.
5. headers are computed for **every** cited path before the branch (L179-182); a path absent at the tip is
   `(None, "absent at tip")`.

### 2.3 The tip-claim branch (L183-199)

- `claims += 1` (L184) for every cited paragraph carrying a token, bound or not.
- `bad` = cited paths whose header rev is `None` **or** differs from `tip_sha` (L185-189). A revision
  mention never reaches this branch's decision.
- `kind = _claim_kind(...)`; `"same-line"` is remapped to `"stale-claim"` (L191-193); `unbound_claims += 1`;
  one finding per bad path (L195-199).

### 2.4 The exact binding condition — the `elif rev_mentions` branch (L200-210)

Reached only when **all** of these hold:

1. the paragraph cites at least one resolvable receipt path (L176);
2. it carries **no** tip token (L183 `if has_token:` is exclusive — this is an `elif`);
3. `REVISION_RE` matches the paragraph text.

`REVISION_RE` (L83): `\brev(?:ision)?\s+([0-9a-fA-F]{40})\b`, `re.I` — the literal word `rev` or
`revision`, at least one whitespace character, exactly 40 hex digits, a word boundary after. Matches are
lower-cased (L178).

Binding is **per (mention × cited path) pair** (L201-210):

```
for want in rev_mentions:
    for path in cited:
        rev, _problem = headers[path]
        if rev is not None and rev == want:
            bound_revisions += 1
        else:
            findings.append({"kind": "stale-revision", ...})
```

So a 40-hex token binds a cited receipt iff the receipt's header revision (parsed as in §2.1) is present,
non-conflicting, and **exactly equal** (full 40 chars, both lower-cased) to the mentioned revision. There is
no prefix match, no case difference, and **no requirement that the mention equal the tip** — a mention of an
older ancestor binds, and the r72 base leg separately grades that ancestor's path history. A
conflicting-header receipt (`rev is None`) always yields `stale-revision`, never a bind. Multiplicity is
real: two mentions of the same revision over one path → `bound_revisions=2`; one right + one wrong mention →
one bind and one finding (`receipts/mention-bounds.txt`):

```
two_mentions_same_hex exit=0 bound_revisions=2 findings=[]
two_mentions_diff_hex exit=1 bound_revisions=1 findings=['stale-revision']
mention_39_hex        exit=0 bound_revisions=0 findings=[]   (not a mention)
mention_41_hex        exit=0 bound_revisions=0 findings=[]   (not a mention)
mention_no_space      exit=0 bound_revisions=0 findings=[]   ("revision:<hex>" is not a mention)
```

### 2.5 What a `recorded at <hex>` paragraph does

`recorded at <hex>` is not a revision mention: the word before the hex is `at`, so `REVISION_RE` does not
match. With no tip token and no mention, the paragraph produces no claim, no finding, `bound_revisions=0`,
and the module exits 0 iff the base leg is green. Verified end-to-end on the `nc2_recorded_at_hex` shape
(§3.2) — full CLI, exit 0:

```
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

The parenthetical `(content id, not a run revision)` contributes nothing: `revision` there is not followed
by a hex token.

### 2.6 `_claim_kind()` boundaries (L137-153)

- `same-line` iff any token line index equals any citation line index (L145-151) — the caller turns it into
  `stale-claim`.
- otherwise `distance = min |token_line − citation_line|` over **all** pairs in the paragraph (L152);
  `distance == 1` → `offset-claim`; `distance >= 2` → `wrapped-claim` (L153).

The paragraph is the unit: blank lines split paragraphs, so a token and a citation separated by a blank line
are two paragraphs, each of which is skipped (one has no citation, the other no token). Verified
(`receipts/p2.txt`, header deliberately different from the tip so the claim is unbound):

```
kind_same_line   exit=1 kinds=['stale-claim']
kind_offset      exit=1 kinds=['offset-claim']     (token line 2, citation line 1)
kind_wrapped2    exit=1 kinds=['wrapped-claim']    (distance 2)
kind_wrapped3    exit=1 kinds=['wrapped-claim']    (distance 3)
```

### 2.7 Exit composition

`clean = (base_exit == 0 and unbound_claims == 0 and not claim_findings)` (L259-260); exit is 0/1 from that
(L261). A `stale-revision` finding forces exit 1 even with all counts at 0. The base leg (frozen r72) is
green only when each cited receipt's header revision is a commit, is an ancestor of the tip, and the commits
in `rev..tip` touch only record paths (`default_record_paths`, r72 L217-224: `.ufo/waves/round-<N>/`,
`corpus/lessons/`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`; `_evaluate`, r72 L430-445). That is why a
P2 fixture needs `seed commit → receipt commit → record commit`, with the receipt header naming the seed.

---

## 3. Re-derivation of the two readings against the plan

Both readings were reproduced on fixtures built in scratch with the **freeze** module and the exact frozen
mutants. Raw output: `receipts/p1.txt`, `receipts/p2.txt`, `receipts/fixture-p2.txt`.

### 3.1 P1 — older-demonstrated `total` (plan §C1 P1)

Fixture as the plan specifies: bold canon round 71 with three rows, a round-60 table with those three plus
two (`alpha…epsilon`). Declared vs the `c1_f1b_older_union` patch (mutation-control L26-35: union
`_names_below` over tables with `_r < canon_round` into `total`):

| fixture | declared | older-union mutant |
|---|---|---|
| round-60 **canonical** table | `canon_rows=3 total=3`, exit 0 | `canon_rows=3 total=5`, exit 0 |
| round-60 **demonstrated** table | `canon_rows=3 total=3`, exit 0 | `canon_rows=3 total=5`, exit 0 |
| no bold canon (canon_round=-1) | `canon_round=-1 canon_rows=0 demonstrated=4 total=4 invisible=4`, exit 1 | identical — mutant **escapes** on this fixture |
| bold canon 71 + demonstrated **71** | `total=3 invisible=0`, exit 0 | identical — mutant **escapes** on this fixture |

The plan's declared value `total=3` and mutant value `total=5` are reproduced exactly, and the plan's
motivating control is reproduced too: the mutant leaves the canon selftest green
`SELFDESC_CANON_V2_SELFTEST pass=11 fail=0`, exit 0 (`receipts/c2.txt`).

**Pin-implication (derived, for EX01).** The pin must compare `total` on a fixture with a **bold canon at
round 71**; the last two rows show that a fixture without a bold canon, or with the older table at the
*equal* round, leaves mutant == declared and the pin would score `escaped`.

### 3.2 P2 — revision-mention context (plan §C1 P2)

Fixture rebuilt from the round-74 critic's `nc2_recorded_at_hex` shape (`attack.md:242-247`): receipt header
names `c0` (the seed commit); the record paragraph is
``probe recorded at <c1> naming `.ufo/waves/round-74/measured/r.out` (content id, not a run revision)``.
Git chain: `base` (c0) → `receipt` (header `# rev=c0`) → `record` (tip); the base leg is green
(`cited=1 bound=1`). Full CLI (`receipts/fixture-p2.txt`):

```
declared : RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0
           exit=0
any-hex  : RECEIPT_CLAIM_V2_FINDING stale-revision .ufo/waves/round-74/measured/r.out :: 5: C2: probe recorded at bbbb… naming `.ufo/waves/round-74/measured/r.out` (content id, not a run revision).
           RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 ... claims=0 unbound_claims=0 bound_revisions=0
           exit=1
```

The any-hex patch (mutation-control L36-41) is exactly the literal reading and its selftest stays green
`RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0` (`receipts/c2.txt`), i.e. the debt is real at the freeze.

Related boundaries run in the same harness (`receipts/p2.txt`):

| fixture paragraph | declared | any-hex mutant |
|---|---|---|
| `recorded at <c1> … (content id, not a run revision)` | exit 0, no finding | exit 1 `stale-revision` |
| `re-run at revision <c0>` (right) | exit 0, `bound_revisions=1` | identical — **cannot distinguish** |
| `re-run at revision <c1>` (wrong) | exit 1 `stale-revision` | identical — **cannot distinguish** |
| `revision: <c1>` | exit 0, no finding | exit 1 `stale-revision` |
| `revision id <c1>` | exit 0, no finding | exit 1 `stale-revision` |
| `revision=<c1>` | exit 0, no finding | exit 1 `stale-revision` |
| `<receipt> measured at the tip; re-run at revision <c1>` | exit 1 `stale-claim`, `bound_revisions=0` | identical |

The second and third rows are the critic's point (the frozen fixture set cannot adjudicate); the fourth to
sixth are new and are §4(c) below.

### 3.3 Agree/disagree table

| plan sentence (round-75-claims.md) | observed at freeze | verdict |
|---|---|---|
| C1-P1: an older table that carries a name the canon lacks contributes no name to `total` | p1a/p1b: `total=3` with 5 names in the older table | **agree** |
| C1-P1: "an older table with two extra names leaves `total` at the canonical row count" | `total=3`, `canon_rows=3` | **agree on the fixture**; imprecise in general — `total` counts distinct names, `canon_rows` rows; duplicate rows give `total=2 canon_rows=3` (p1h) |
| C1-P1: "the all-tables-union mutant scores above it" | mutant `total=5` > 3 | **agree on the value**, **disagree on the description**: the frozen patch (mutation-control L26-35) unions only tables with `round < canon_round`; a table at the *same* round is not unioned (p1f: mutant `total=3` == declared) |
| C1-P1: declared `total=3`, older-union mutant `total=5` | exact | **agree** |
| C1: the canon mutant leaves selftest `pass=11 fail=0` | `pass=11 fail=0`, exit 0 | **agree** |
| C1-P2: the `nc2_recorded_at_hex` paragraph grades clean, exit 0 | CLI exit 0, `claims=0` | **agree** |
| C1-P2: the any-hex mutant reports `stale-revision` | exit 1, one `stale-revision` finding | **agree** |
| C1-P2: "not introduced by `rev`/`revision` names no revision" | the code tests *immediate adjacency* (`\brev(?:ision)?\s+<hex>`), not "introduction"; `revision: <hex>`, `revision id <hex>`, `revision=<hex>` name no revision either | **partial disagree** — the pin as specified passes (its fixture is `recorded at`), but the declared reading is **narrower** than the plan's sentence |
| C1: with the older-union and any-hex mutants applied both selftests stay green (`killed=0 escaped=2`) | canon `pass=11`, receipt `pass=9` | **agree** |
| C2: five named mutants; three killed, two escape at base | killed `case_hex`, `kind_boundary`, `paragraph_scope`; escaped `conflict_off`, `header_window` | **agree** (see §4) |
| C2 docstring: "conflicting headers inside the first five lines stay a finding source (`unbound`), never a crash" | true for the frozen r72 leg; in the **v2 claim pass** the conflict makes the header `None`, so a rev-mention paragraph yields `stale-revision` — and the `conflict_off` mutant turns that same paragraph into a **bind** | **agree on the sentence, with a precision the arm must encode** (§4.4) |

---

## 4. The five C2 mutant classes — smallest edit, broken path, base arm

All five patches are imported verbatim from `mutation-control.py` (`C2_MUTANTS`, L43-75) in the runs below;
the "smallest edit" column is the minimal source change I verified flips the same behaviour. Raw output:
`receipts/c2.txt`, `receipts/minimal-edits.txt`, `receipts/c2-extra.txt`. Pristine module at freeze:
`RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0`, exit 0.

| mutant | smallest source edit | code path it breaks | base selftest arm | result at base |
|---|---|---|---|---|
| `case-hex` | delete `, re.I` from L82 (the frozen patch also narrows `A-F` out of the hex class) | `_header_rev_v2` L105-116: a `REV=<HEX>` header is no longer seen → `rev=None` → every receipt is "unbound" in the claim path | **`blob-reader-seam`** (registration L389) — injects an upper-case header; the arm asserts `pristine claims=1 unbound=0` and `mutant_case_sensitive_rev is None` | **killed** `pass=8 fail=1` |
| `kind-boundary` | change L192 `if kind == "same-line":` to `if False:` | L191-193: the same-line remap is skipped, so findings carry the undocumented kind `same-line` instead of the inherited `stale-claim` | **`same-line-stale-claim`** (L429) asserts the kind | **killed** `pass=8 fail=1`, `kinds=['same-line']` |
| `paragraph-scope` | replace L164 `for start, plines in _paragraphs(lines):` with per-line iteration | L164-199: the paragraph becomes a line; a multi-line claim has a token line and a citation line but no line with both → `claims=0`, no finding, exit 0 | **`committed-fixtures`** (L361): both `c2_wrapped` (citation 1, token 3) and `c2_offset` grade `rc=0 kinds=[]` | **killed** `pass=8 fail=1` |
| `conflict-off` | change L114 `if len(set(revs)) > 1:` to `if False:` | `_header_rev_v2` L114-115: a conflicting header returns its **first** revision instead of `(None, …)`; a rev-mention paragraph then **binds** that revision (L204-205) instead of raising `stale-revision` | **none at base** — no committed fixture carries two headers in the window | **escaped** `pass=9 fail=0` |
| `header-window` | change L79 `HEADER_WINDOW = 5` to `3` | L107 `splitlines()[:HEADER_WINDOW]`: a header on line 5 is outside the window → `rev=None` → unbound / `stale-revision` | **none at base** — every base fixture receipt names its revision on line 1 | **escaped** `pass=9 fail=0` |

The nine base arms (freeze): `predicate` L321, `predicate-at-tip` L329, `committed-fixtures` L361,
`blob-reader-seam` L389, `stale-revision` L410, `same-line-stale-claim` L429, `base-absent` L439,
`record-missing` L450, `cli-misuse` L458.

### 4.1 What each escape changes observably (the assertion a new arm must make)

Both escaping mutants are observable, but *not* through the module's exit code alone — the r72 base leg
independently reports conflicting headers as `unbound`, so the full module stays exit 1 either way. The
discriminating surface is the claim pass's `bound_revisions` / finding kind
(`receipts/c2-extra.txt`):

```
== conflicting headers (rev=c0 and rev=a*40), paragraph "re-run at revision c0"
  declared     exit=1 kinds=['stale-revision'] bound_revisions=0
  conflict_off exit=1 kinds=[]                 bound_revisions=1     <-- binds where declared finds
== header on the fifth line, paragraph "re-run at revision c0"
  declared     exit=0 kinds=[]                 bound_revisions=1
  header_window exit=1 kinds=['stale-revision'] bound_revisions=0
== header on the fourth line (control: inside 5, outside 3)
  declared     exit=0 ... bound_revisions=1;  header_window exit=1 stale-revision
```

So a committed `conflicting-headers` arm must assert the **kind** (or `bound_revisions == 0`), and a
committed `header-window-fifth-line` arm must put the header on exactly line 5 of a receipt whose revision
the record names. The plan's §C2 wording ("graded `unbound`, never a crash") is satisfied by asserting the
claim-pass finding; asserting only the exit code would remain green under `conflict-off`.

### 4.2 Probe arithmetic

The plan's probe target is `mutants=5 killed=5 escaped=0` with the pristine selftest green. My runs give the
per-mutant failing arm names the probe must print:

- `case-hex` → `blob-reader-seam`
- `kind-boundary` → `same-line-stale-claim`
- `paragraph-scope` → `committed-fixtures`
- `conflict-off` → (must become non-empty once the conflicting-headers arm lands)
- `header-window` → (must become non-empty once the fifth-line arm lands)

After EX02 adds the two arms the pristine count becomes 11, not 9; the probe must require "green", not a
frozen `pass=9`.

---

## 5. Third readings the code leaves free

These are cases where **neither the plan nor the module docstring pins the answer**, and a second
minimally-faithful implementation can differ. Each has a fixture and an observed value.

### (a) Canon — a demonstrated table at the **same** round as the bold canon

The plan speaks of tables "older" (§C1 P1) and newer (docstring L48-52); the equal-round case is named
nowhere in a counter rule. The docstring's tie-break sentence (L186-188) promises these names are "never
hidden", but they are hidden from every output.

Fixture `p1f`: bold canon 71 (`alpha,beta,gamma`) + `### Capabilities demonstrated in round 71`
(those three + `same-round-extra`).

```
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0   exit=0
```

Alternative readings: `total=4` and/or `invisible=1`. The frozen older-union mutant also prints `total=3`,
so a pin over this fixture would score `escaped`.

### (b) Receipt — precedence when a paragraph carries **both** a tip claim and a revision mention

The code makes the branches exclusive (`if has_token:` … `elif rev_mentions:`, L183/L200). The docstring's
`stale-revision` definition (L40-41) is unconditional: "the paragraph names an explicit 40-hex revision and
a cited receipt's header differs". Nothing in the plan says the tip-claim branch wins.

Fixture `f2c_token_plus_rev`: ``<receipt> measured at the tip; re-run at revision <wrong hex>``, header =
c0 ≠ tip.

```
declared exit=1 kinds=['stale-claim'] bound_revisions=0
```

The alternative reading would report `stale-revision` (the named revision differs from the header) — or both
kinds. A second implementation is free to choose; the frozen fixture set contains no such paragraph.

### (c) Receipt — the mention grammar is adjacency, not "introduction"

The plan's P2 sentence ("not introduced by `rev`/`revision`") reads as a context test; the code requires the
word immediately before the hex (`\brev(?:ision)?\s+`). Natural prose that *names* a revision therefore
grades clean:

| fixture | paragraph | declared | any-hex |
|---|---|---|---|
| `f2c_rev_colon` | `re-run, revision: <wrong hex>, naming <receipt>` | exit 0 | exit 1 `stale-revision` |
| `f2c_rev_id` | `re-run at revision id <wrong hex> …` | exit 0 | exit 1 `stale-revision` |
| `f2c_rev_eq` | `re-run at revision=<wrong hex> …` | exit 0 | exit 1 `stale-revision` |

This is the same F2c ambiguity re-entering through a different door: the module is context-sensitive only
for the exact `rev <hex>` surface form. A record can name a wrong revision in `revision:` form and the
committed module calls it clean. (Same family: 39- and 41-digit tokens are not mentions at all; verified.)

### (d) Canon — a bold canonical phrase in prose, not a heading

`BOLD_CANON_RE` is searched on every line with no heading requirement (L195-198), and r42 `canon()` uses the
same free-text regex (r42 L145). A sentence that quotes the phrase sets `canon_round`.

Fixture `p1g`: `The reconciler quotes **canonical list as of round 90** here.` followed by a one-row table,
plus a demonstrated table at round 91.

```
SELFDESC_CANON_V2_FINDING invisible 91 beta
SELFDESC_CANON_V2 canon_round=90 canon_rows=1 demonstrated=1 total=2 invisible=1   exit=1
```

The plan says "heading markup … forms all count"; the code counts a non-heading mention. The alternative
(heading-only) reading would leave `canon_round=-1` and flag both names.

### (e) Canon — a canonical heading whose table has no parsable rows

Fixture `p1i`: `**Capabilities — canonical list as of round 71**` with nothing below it.

```
SELFDESC_CANON_V2 canon_round=71 canon_rows=0 demonstrated=0 total=0 invisible=0   exit=0
```

The docstring's exit-2 clause says "no capability table can be parsed"; a heading with zero rows arguably
did not parse, yet the module exits 0 with an empty repertoire. The alternative reading is exit 2.

**Priority for a future pin:** (a) and (b) are decisions a pin must make explicitly; (c) is a live hole a
wrong-revision prose can exploit; (d)/(e) are detection-surface divergences with lower blast radius.

---

## 6. Disagreements and imprecisions in the frozen plan (report-only, no edit made)

1. **"all-tables-union"** (§C1 P1) names a mutant that is older-tables-only. The frozen patch unions
   `round < canon_round`. Same-round tables are not unioned; a probe author who re-implements "all tables"
   literally would build a different mutant and could disagree with the frozen control.
2. **P2's "not introduced by `rev`/`revision`"** is broader than the code's `\brev(?:ision)?\s+<hex>`
   grammar (§3.3, §5(c)). The pin as specified still passes, but the *declared reading* the pin freezes is
   "40-hex immediately after `rev`/`revision` + whitespace", not "introduced by".
3. **"leaves `total` at the canonical row count"** holds only for unique canon names; `total` is a name set
   and `canon_rows` a row count (§1.2, p1h).
4. **The same-round case is unpinned** and the docstring's "never hidden" claim is contradicted by the
   counters (§5(a)).
5. **The conflicting-header sentence** is true of the frozen r72 leg; in the v2 claim pass a conflict makes
   `rev=None`, so the observable is a `stale-revision` finding (or, under `conflict-off`, a bind). An arm
   that asserts only the exit code cannot kill `conflict-off` (§4.1).

---

## 7. What this means for the two round-75 counters (derived, not prescriptive)

- **C1 P1 pin**: compare `total` on a fixture with a **bold** canon at round 71 and an older table (either
  kind) carrying three shared + two extra names; asserted values `3` (declared) and `5` (mutant). A fixture
  without a bold canon or with the table at the equal round produces mutant == declared → `escaped`.
- **C1 P2 pin**: the fixture needs a base-green chain (`seed → receipt(header=seed) → record`) or the
  declared run is exit 1 for base reasons, not for the reading. The paragraph must not contain a tip token
  (otherwise the tip-claim branch masks the difference) and must not contain any other 40-hex token (the
  literal mutant would match it). Asserted values `exit 0` vs `exit 1 stale-revision`.
- **C2 probe**: the pristine module at freeze prints `pass=9 fail=0`; after the two arms it is `11`. The two
  former escapes are only killable with *behavioural* assertions: `conflict-off` on
  `bound_revisions`/finding kind, `header-window` on a fifth-line header (the fourth line is already outside
  a three-line window).
- The C1 pin must not be built on the module's selftest alone: both mutants leave it green at base, which is
  the debt the round is closing.

---

## 8. Reproduction

All commands ran with an explicit scratch dir; no fixture inherited `TMPDIR`. The lane worktree file was
never executed (only freeze bytes from `git show`). Fixture repos were created under
`/fast/scratch/hyaku/kama-r75/REV01Semantics/` and each asserted its own `rev-parse --show-toplevel`
(the `_Fixture` constructor does this, r72 L546-554).

| receipt | command (script in scratch, now deleted) | exit |
|---|---|---|
| `receipts/p1.txt` | `python3 drive_p1.py` — 6 SCORECARD fixtures × {declared, older-union} | 0 |
| `receipts/p2.txt` | `python3 drive_p2.py` — 12 receipt fixtures × {declared, any-hex} | 0 |
| `receipts/c2.txt` | `python3 drive_c2.py` — pristine + five C2 mutants + canon mutant in the shared clone | 0 |
| `receipts/c2-extra.txt` | `python3 drive_c2_extra.py` — conflict/window discriminating fixtures | 0 |
| `receipts/minimal-edits.txt` | five single-token edits, each selftest run, clone file restored byte-exact (`sha256 5c6174c4…`) | 0 |
| `receipts/mention-bounds.txt` | multiplicity, 39/41-hex and `revision:` boundaries | 0 |
| `receipts/canon-probes.txt` | prose-bold, duplicate rows, empty canon, no-table | 0 |
| `receipts/canon-dedupe.txt` | `capability_tables()`/`resolve()` on same-round permutations | 0 |
| `receipts/fixture-p2.txt` | P2 fixture git log, blobs, full CLI both modules, `ls-files` | 0 |
| `receipts/hashes.txt` | freeze sha256 manifest, worktree drift, base-vs-freeze check | 0 |

Key output lines are quoted inline above; the receipts contain the untruncated runs. Exit codes relied on:
declared P1 fixtures `0`/`1` as shown, declared P2 CLI `0`, any-hex P2 CLI `1`, pristine receipt selftest
`0` with `pass=9`, each `case-hex`/`kind-boundary`/`paragraph-scope` selftest `1` with `pass=8`, each
`conflict-off`/`header-window` selftest `0` with `pass=9`, canon pristine `0` with `pass=11`, canon
older-union `0` with `pass=11`.

**Cleanup.** The scratch tree `/fast/scratch/hyaku/kama-r75/REV01Semantics/` (clone, freeze copies, mutants,
fixtures, work dirs) was removed after these receipts were copied into this directory; no scratch tree is
left on disk.

---

## 9. Confidence

- **High** — every mechanics claim in §1, §2 and §4 is a direct reading of the freeze bytes with a line
  cite, and every value in §3 and §5 is an executed run with its receipt in this directory.
- **Medium** — the *intent* labels ("which reading the lane rejected", "a pin must…") are inferences from the
  plan's sentences and the mutation-control patches; they are marked as such where they appear.
- **Not claimed** — that any round-75 counter is correct (none existed at freeze): EX01's
  `round75-interpretation-pins.py` and EX02's arms must be graded by their own runs. The assertion I derive
  for the `conflicting-headers` arm (§4.1) is a design claim from observed mutant behaviour, not a run of a
  committed arm.
- The one thing I could not test is the cross-line token invariant in §1.6: I could not construct a fixture
  where `has_token` is true while `token_idx` is empty, and the string tests make it seem impossible; it is
  labelled inference.
