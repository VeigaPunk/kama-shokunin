# RV01RenderedAttack — C1 rendered-cell selector attack (kama r86 wave w2, falsify)

Seat: reviewer (attack C1 calibration, rendered-cell identity). Leaf, no delegation.
Measured revision: **67eddac89f44e768b670301ea0feff06e766f32d** (fleet `git rev-parse HEAD`
identical at measurement; working-copy bytes of `tools/round86-rendered-cells.py` and
`.ufo/waves/round-86/count.py` hash-identical to committed: `370de91021694c99fe70f5230d2d356b64d6f8f5`,
`4c1461ce4232ed6d66334df6ee0ee23b29234a41`). Renderer arbiter: **cmark 0.31.2** (the exact
CommonMark version the claims cite). Fixtures: 19 commits on an `attack` branch of one scratch
clone of 67eddac; every commit preceded by `git -C "$D" rev-parse --show-toplevel` == `$D`;
scratch removed after receipts landed in out/. Receipts:
`.ufo/waves/round-86/w2/out/RV01RenderedAttack/` (`VERDICTS.json`, `VERDICTS_V2.json`,
`VERDICTS_V3.json`, `tree-facts.json`, `00-counter-rederive.out`, `01-selftest.out`,
`<case>/{scorecard.md,instr.out,cmark.html}`).

Method: the tip is already green (`mismatches=0`, below), so every attack tree makes the live
cells deliberately **stale** (round-84 banner/row) and places **fully-coupled fresh copies**
(the exact green banner and green `| calibration |` row lifted from the tip's own line 6/18)
in a hidden position. A working selector must then exit 1 naming all three mismatches; exit 0
on any of these trees is a false green by construction (the fresh copies couple: token
`PRE_REPORT round=85 …` exists at ancestor revisions in `.ufo/waves/round-85/measured/after/gate.out`,
so `gate_fact` accepts them when they are seen — proven by the b3/p3b greens).

## 1. Counter re-derivation (item-mandated)

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py c1 \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev 67eddac89f44e768b670301ea0feff06e766f32d \
  --work /fast/scratch/hyaku/kama-r86/RV01RenderedAttack/w
→ exit 0
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
```

The plan's red before-control (`mismatches=3`) was measured at frozen base `3ff23da…`; at the
dispatch tip the live cells are already repaired. Receipt: `00-counter-rederive.out`.

## 2. Delivered instrument `--selftest` at committed bytes

```
python3 <clone>/tools/round86-rendered-cells.py --selftest   (TMPDIR=scratch/w)
→ exit 0, RENDERED_CELLS_SELFTEST pass=11 fail=0
```

All 11 frozen arms green — while defects D1–D4 below exist. The control set does not cover
capital-R correction headings, HTML blocks, unbalanced close lines, or backtick-info fences.

## 3. The five assigned cases (each: instrument exit + verdict + arbiter truth + class)

| case | commit | exit | verdict line (instrument) | cmark truth | class |
|---|---|---|---|---|---|
| (a1) fresh cells inside a fence nested in a **blockquote** | `d35be45ebdd0` | 1 | `mismatches=3 gate=0 closure=0 disposition=0` | shadow in `<pre>`, stale live cells rendered | **CORRECT-REJECT** (finding, not fail-closed) |
| (a2) fence nested in a **list item** | `5893cddb6657` | 2 | `could-not-evaluate: no rendered top-level calibration row inside ## Axes` | shadow hidden, stale live row rendered | **DEFECT D3** (spurious fail-closed) |
| (a3) col-0 cell between `> ```markdown` / `> ``` ` (lazy arbiter) | `bb9a4fe1e8b2` | 0 | `mismatches=0` (all facts true) | **fresh cells RENDERED** — cmark ends the blockquote at the col-0 line (no lazy continuation into fences) | **CORRECT-ACCEPT** — instrument agrees with the renderer; not a defect |
| (b) cell in `### round-86 correction` section (lowercase) | `cec9f5bf8ac1` | 1 | `mismatches=3` | cmark renders correction bodies (plain markdown); arbiter for this case is the **frozen claims sentence** ("a `round-<N> correction` block is not a rendered cell") | **CORRECT-REJECT** per frozen letter |
| (b2/b3) same under **`### Round-86 correction`** (capital R — the form SCORECARD history itself uses: `### Round-26 correction`, `### Round-20 correction`) | `f5123ec4cbde` / `826e657f2b14` | 1 (closure=1 disposition=1 — row accepted!) / **0** | `mismatches=1 gate=0 closure=1 disposition=1` / `mismatches=0 gate=1 closure=1 disposition=1` | (convention arbiter, see b) | **DEFECT D1** — false green at b3 |
| (c1b) fresh cells in a true **4-space indented code block** (blank line before block) | `10e0e3667858` | 1 | `mismatches=4 gate=0 closure=0 disposition=0` | shadow hidden (`<pre>`), stale live cells rendered | **CORRECT-REJECT** (finding) |
| (c2) col-0 cell adjacent to 4-indent fence-looking lines | `11c2615f8989` | 0 | `mismatches=0` | **fresh cells RENDERED** — col-0 ends indented code | **CORRECT-ACCEPT** — indent cannot hide col-0; instrument agrees |
| (d) fresh cells inside **multi-line HTML comments** | `0dd3baa0c47a` | 1 | `mismatches=3` | shadow hidden, stale live cells rendered | **CORRECT-REJECT** (finding) |
| (e) **round-85 false green**: fresh fenced cell + stale live cells | `6186063f309d` | 1 | `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85` + all three `RENDERED_CELLS_FINDING` lines | shadow in `<pre>`, stale live cells rendered | **CORRECT-REJECT** — the R85 false green is rejected as findings, not fail-closed |

Every rejection in the assigned set that should be a finding **is** an exit-1 finding naming all
three mismatches (a1, b, c1b, d, e); the only assigned case that fails is (a2), fail-closed (D3).

## 4. DEFECTS

### D1 — HIGH — false green via capital-R `Round-N correction` heading (case b3, commit `826e657f2b14`)

Selector regex `CORRECTION = re.compile(r"^ {0,3}(#{1,6})\s+round-[0-9]+ correction(?:\s|$)")`
is case-sensitive lowercase. Adversarial bytes (complete file at
`out/b3-capital-correction-full/scorecard.md`): both live cells replaced by stale round-84
analogues, and the exact green banner + green row placed under:

```
### Round-86 correction
**Current authority (round 86):** … `python3 tools/pre-report-gate.py --repo . --round 85 --tip master` …
### end round-86 correction
…
### Round-86 correction
| calibration | **7** | … latest outside closure `corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-honest-stop) …
### end round-86 correction
```

Instrument: `exit 0`, `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1
newest_gate=85 newest_closure=85` — a false green on a tree whose only fresh cells sit inside a
correction block. b2 (`f5123ec4cbde`) shows the row-level half even under a stale banner:
`mismatches=1 gate=0 closure=1 disposition=1` — the correction-wrapped row was accepted and
satisfied closure+disposition. The lane's own SCORECARD history uses capital-R correction
headings (`### Round-26 correction — …`, `### Round-20 correction — …`), so this is not an
exotic spelling. Caveat for admission: the frozen plan and PREDICATE spell `round-<N>
correction` lowercase, and the round-85 raw counter had the same case-sensitivity
(`.ufo/waves/round-85/count.py:16`); whether the convention's letter is lowercase-only is the
L1's call. The 11 frozen selftest arms contain no correction arm at all, so nothing pins this.

### D2 — MEDIUM — false green inside a raw-HTML `<script>` block (case p3b, commit `bf37a7430f8c`)

`<script>` … fresh cells … `</script>` placed where the banner/row live, on a stale-live base.
cmark 0.31.2 renders the block as raw HTML (§4.6 HTML block type 1) — the cells are invisible;
instrument: `exit 0`, `mismatches=0 gate=1 closure=1 disposition=1`. The selector models
fences, comments and corrections but no HTML-block rule, so any type-1/6 raw-HTML block
(`<script>`, `<pre>`, `<style>`, `<textarea>`) is a false-green surface. Scope caveat: the
frozen hidden-set letter is "fence- and comment-free, column-0" — §4.6 is outside the letter,
inside the renderer truth. (p3 on a green base, commit `303de102ede9`, was inconclusive by
construction and is kept only as the receipt trail.)

### D3 — MEDIUM — spurious fail-closed from a fence-looking *close* line whose opener was missed (case a2, commit `5893cddb6657`; same root in p2 `c0e70db3b9eb`, p4 `babec2dd3c77`, p6 `1061e035eea2`)

In a2 the fresh cells sit in a list-nested fence: opener `- ```markdown` (list marker prefix —
correctly not a column-0-3 fence for the instrument) and closer `  ``` `. The instrument never
opens the first fence, then treats the closer `  ``` ` (col 2 ≤ 3) as a **new opener** and
swallows the real live calibration row behind it: `exit 2 — could-not-evaluate: no rendered
top-level calibration row inside ## Axes`, on a document cmark grades evaluable-red (shadow
hidden, stale live row plainly rendered). Fail-closed direction — it can never produce a false
green — but it silently stops grading a renderer-evaluable tree, the same shape as the
kill-rule's "any control that stops discriminating". No selftest arm covers an unbalanced
close-looking line.

### D4 — MEDIUM — state machine enters hidden states from non-block constructs (false reds, fail-closed; commits `7d9e4d14ca8e`, `5efba3fb46e6`, `5c91a364be0a`, `1061e035eea2`, `8fec8f7acd1a`, `babec2dd3c77`)

Each trigger below is placed on an otherwise **green** tree (live cells untouched; cmark keeps
them rendered); each flips the instrument to `exit 2`:

- **p1a/p1b** — a line ```` ```md `info` with backtick ````: per CommonMark §4.4 a backtick
  fence whose info string contains a backtick is **not a fence**; cmark renders it as paragraph
  text. The instrument's `FENCE` regex accepts any info string and opens fence state, swallowing
  the live cells → `exit 2`.
- **p5/p6** — a literal backticked `` `<!--` `` in a rendered paragraph: code span, not a
  comment start; the substring-based comment state swallows everything to the next `-->` →
  `exit 2` ("no rendered top-level Current authority cell" / "…calibration row…").
- **p7** — `    <!--` at 4-space indent: indented code (§4.5), not a comment; instrument opens
  comment state → `exit 2`.
- **p4** — a fence opened **inside** a correction section stays open past the section's end
  (fence check precedes the depth check), swallowing `## Axes` and the live row; the stale
  `depth` also suppresses the row after the fence closes → `exit 2`.

Root cause shared with D3: the selector is a textual state machine without CommonMark
block-context checks (no indented-code tracking, no HTML-block line-initiality, no
backtick-info rule, no lazy-continuation model). All D4 instances fail **closed** (false reds),
so the green gate is not threatened; the cost is spurious could-not-evaluate on valid
documents and wrong "no live cell" readings. Not covered by any selftest arm.

## 5. What the delivered instrument demonstrably rejects (the C1 capability delta)

The round-85 counter (`.ufo/waves/round-85/count.py:19-21`) regex-searches **raw bytes** with
no fence/comment/indent handling (only lowercase correction headings skipped), so it accepts
every shadow in a1, a2, c1b, d, e. The delivered instrument rejects all five as exit-1
findings on real tree bytes with fully-coupled cells — the coupling is proven live by b3/p3b,
where the same bytes in an accepted position produce `gate=1 closure=1 disposition=1`. The
round-85 false green (e) is dead: `mismatches=3`, all three findings printed.

Two probe results deserve explicit note because they are **correct** behaviors that look
suspicious: a3 and c2 show the column-0 rule refusing to hide cells that a renderer actually
renders (blockquote fences and indented code physically cannot hide a column-0 line — the
blockquote/code block ends at that line). The instrument's greens there match cmark exactly;
any "fix" that stripped those would over-strip into false reds.

## 6. Residual risk and verification gaps

- Single renderer arbiter (cmark 0.31.2). No second engine cross-checked; markdown-it is
  installed locally but was not used as a second opinion.
- The correction-convention arbiter is the frozen claims sentence, not cmark (cmark renders
  correction bodies as ordinary markdown; VERDICTS_V2 labels several b-family truths
  "FRESH-CELLS-RENDERED" on that renderer basis — read them through the convention lens).
- D1 admission hinges on whether the lane's correction convention is case-sensitive lowercase
  (frozen letter) or casing-independent (lane practice). I report the bytes; the L1 rules.
- The exit-2-vs-exit-1 boundary in D3/D4 is judged against cmark's "renderer-evaluable"
  reading; the predicate letter permits exit 2 when no rendered cell exists, and in these
  trees a rendered cell does exist under cmark.
- 19 fixture commits measured; scratch clone removed after receipts were written. No
  production files touched; no commits outside the scratch fixture; no mutating git anywhere
  but the fixture (toplevel asserted before every commit).

Report: .ufo/waves/round-86/w2/RV01RenderedAttack.md
Receipts: .ufo/waves/round-86/w2/out/RV01RenderedAttack/
