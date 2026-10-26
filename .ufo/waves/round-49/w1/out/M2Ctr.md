# M2Ctr — C2 counter mutation test (round 49, lane kama)

VERDICT: 49 single-site mutants of `tools/round49-append-audit-v4-check.py` (sha256 `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945`): **28 killed** by the golden pair, **16 survived with proposed killing cases** (one of them first-order and tool-anchored: M03), **5 equivalent-in-scope**. The lane counter was mutated only in my scratch copy; lane bytes are identical before/after (same sha256, `git status --porcelain` clean). No counter defect found; the survivors are coverage findings, not contract changes.

## Setup

- Scratch `S=/fast/scratch/hyaku/kama-r49/M2Ctr`; `TMPDIR=$S`; one live clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (clone HEAD `122c4ee95701587cef7f4342c3d175622ec2f4ad`, which carries a byte-identical `tools/append-only-audit.py` to the tip — `git diff --stat tip..HEAD -- tools/append-only-audit.py` is empty).
- Golden inputs (frozen): TIP `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, BASE `438127bc01ff3b99f98468549d58046f932490ef` (round-48 closure control).
- Pristine detector runs (exit, full stdout):
  - tip: `tip=74558c71…` `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0 (~4 s)
  - base: `tip=438127bc…` `fixture=0 lane=0 scenarios=4/8 met=False`, exit 1 — byte-comparable to the frozen control `.ufo/waves/round-49/controls/base.c2.out` (lane events 5, `dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23`, `0718b6abbda6 … 72 > 65`).
- Detector: a mutant is **killed** iff its (exit, stdout) on tip or base differs from pristine's; survived = identical on both; crashed runs (traceback) count as killed.
- Runner: `python3 run_one.py mut/<name> tip|base` per mutant (98 runs, `xargs -P 6`, ~80 s wall). Every receipt cited is copied under `out/M2Ctr/runs/`.

## Result table

`K(tip)`/`K(base)` = divergence side. Full table also in `out/M2Ctr/detect.txt`.

| Mutant | Site (line refs = pristine.py) | Verdict | Evidence |
|---|---|---|---|
| M01-neg3-empty | `NEG3 = ()` (L81) | survived | binder never sees these texts on tip/base rows; divergence: `binds("LOG.md does no longer append; it is append-only",…) False→True` (funccheck) |
| M02-negw-window2 | NEGW `{0,3}?`→`{0,2}?` (L83) | survived | tool-anchored masking (see F-1); divergence at 3-word gap |
| M03-negw-window6 | NEGW `{0,3}?`→`{0,6}?` (L83) | **survived — first-order** | tool binds 4-word gap (`anchors.txt`: `negation-gap-4 … exit 0`), pristine binder binds, mutant unbinds → would fail a compliant lane |
| M04-negw-drop-nor | drops `nor\|` (L82) | survived | masked (tool unbinds `nor`, anchored); killing case F-2 |
| M05-negw-drop-non | drops `non\|` (L82) | survived | masked (tool unbinds `non`, anchored); killing case F-2 |
| M06-negw-hyphen-only | `append[- ]only`→`append-only` (L83) | survived | masked (tool unbinds spaced `never append only`, anchored); killing case F-2 |
| M07-says-drop-negw | `says()` drops `NEGW.search` (L88-89) | survived | masked on goldens; killing case F-2 (v3-regressed tool) |
| M08-token-wild-base | `parts[-2]`→`parts[-1]` (L94) | **killed (tip+base)** | `corpus/lessons/*.md` row: token `*.md` absent from `corpus/QUALITY.md:143` → `lane: contract row … does not bind under v4`, exit 0→1 |
| M09-token-keep-ext | drop `rsplit(".",1)[0]` (L96) | **killed (tip+base)** | `corpus/SOURCES.md` row: `SKILL.md:578` has `SOURCES` but no `sources.md` → unbound, exit 0→1 |
| M10-word-lookahead | `(?![a-z0-9_])`→`(?![a-z])` (L103) | survived | masked (tool word regex strict); killing case F-2 |
| M11-self-wild-bind | drop `not wild` guard (L101) | survived | masked; killing case F-3 |
| M12-wild-const-false | `wild = False` (L100) | survived | masked; killing case F-3 |
| M13-wild-star-only | `"*?["`→`"*"` (L100) | survived | masked; killing case F-3 (?/[ patterns) |
| M14-sections-hash1 | `b"## "`→`b"# "` (L255) | **killed (tip+base)** | exempt titles never match → native 0 → `ungraded 17 > natively exempt 0` |
| M15-origin-all | `& ex`→`ex <= org[...]` (L352) | **killed (tip+base)** | tip native 65→<65 → `ungraded 65 > natively exempt …` |
| M16-native-ge | `>`→`>=` (L353) | **killed (tip)** | tip event `0718b6abbda6` sits exactly at the bound: `ungraded 65 >= natively exempt 65` → exit 0→1 |
| M17-events-ge6 | `>= 5`→`>= 6` (L289) | **killed (tip)** | tip has exactly 5 events |
| M18-events-gt5 | `>= 5`→`> 5` (L289) | **killed (tip)** | same |
| M19-lane-exit-le0 | `== 0`→`<= 0` (L289) | survived (equiv.) | `subprocess` returncode is never <0 unless signal-killed after emitting full JSON — unreachable in practice |
| M20-drop-baddecl | drop `bad_declarations == 0` clause (L289) | survived | killing case F-4 |
| M21-scenarios-7 | `len(res) == 8`→`== 7` (L392) | **killed (tip)** | fl False on a passing tip |
| M22-met-or | `fl and ll`→`fl or ll` (L393) | survived | goldens flip both legs together; killing case F-5 |
| M23-launder-exit0 | launder want_exit 1→0 (L212) | **killed (tip+base)** | `scenario launder: FAIL exit 1 (want 0)` |
| M24-launder-graded | want graded 25→24 (L212) | **killed (tip)** | `event {'graded': 25…} want {'graded': 24…}` |
| M25-nativehead-ungraded | want ungraded 25→24 (L219) | **killed (tip+base)** | FAIL on tip |
| M26-datedloss-exit | want_exit 1→0 (L226) | **killed (tip+base)** | FAIL on tip |
| M27-substring-exit | want_exit 1→0 (L230) | **killed (tip+base)** | FAIL on tip |
| M28-wordtoken-exit | want_exit 0→1 (L231) | **killed (tip+base)** | FAIL on tip |
| M29-negated-exit | want_exit 1→0 (L232) | **killed (tip+base)** | FAIL on tip |
| M30-wildself-exit | want_exit 1→0 (L233) | **killed (tip+base)** | FAIL on tip |
| M31-wildnamed-exit | want_exit 0→1 (L234) | **killed (tip+base)** | FAIL on tip |
| M32-wildself-bad | want bad 1→0 (L233) | **killed (tip)** | `bad_declarations 1 want 0` |
| M33-runtool-path | `{name}.contract.tsv`→`"contract.tsv"` (L165) | survived (equiv.) | scenarios run sequentially; no collision possible in the current call graph |
| M34-runtool-flag | `--contract`→`--contract-typo` (L168) | **killed (tip+base)** | tool errors → JSON unreadable → all scenarios FAIL |
| M35-exit-always-0 | `return 0 if met else 1`→`return 0` (L402) | **killed (base only)** | base exit 1→0 — only the base control sees it |
| M36-exit-invert | inverted (L402) | **killed (tip+base)** | both goldens |
| M37-archive-head | archive `tip`→`"HEAD"` (L381) | **killed (base only)** | base fixtures re-run against HEAD's v4 tool → `fixture=1`, exit 1→0; tip blind because tool@HEAD==tool@tip |
| M38-revlist-noreverse | drop `--reverse` (L316) | **killed (tip+base)** | origins become last-appearance → native 65→<65 → tip fails |
| M39-region-relax | `[^@:]+:\d+`→`[^@:]*:\d*` (L313) | survived | killing case F-6 (region grammar never exercised) |
| M40-region-never | regex→never-match (L313) | **killed (tip+base)** | titles {} → `ungraded 17 > natively exempt 0` |
| M41-titles-split | `split("\|")`→`split()` (L314) | **killed (tip+base)** | SCORECARD's 5-title row collapses → native 0 |
| M42-ex-fnmatch-eq | `fnmatchcase(f,pat)`→`f == pat` (L325) | survived | all ungraded tip events are `SCORECARD.md` (exact row name); killing case F-7 |
| M43-diff-U3 | `-U0`→`-U3` (L271) | **killed (tip+base)** | position parser over-runs context: native 23→15, 65→60 → `ungraded 17 > natively exempt 15` |
| M44-header-row | `[1:]`→`[0:]` in parse_contract (L298) | **killed (crash)** | header parsed as row → `int("declared_at")` ValueError traceback, exit 1 |
| M45-fx-no-trailing-nl | drop trailing `\n` in Fx.write (L152) | survived (equiv.) | fixtures never delete a file-final line and the tool is newline-robust (`split_lines`); no counter input distinguishes |
| M46-ident-name | fixture commit identity renamed (L78) | survived (equiv.) | identity never asserted |
| M47-toplevel-guard | guard→`if False:` (L148) | survived (equiv.) | guard cannot fire for Fx-created dirs under --scratch |
| M48-origins-lastwins | first→last appearance (L338-343) | **killed (tip+base)** | native 65→<65 on tip |
| M49-negw-apos | `[\w'’]+`→`[\w]+` (L83) | survived | masked (tool unbinds apostrophe middle word, anchored); killing case F-2 |

Counts: 49 mutants = 28 killed (25 by tip, 3 of those also/only by base; M35 and M37 killed **only** by the base control) + 16 survivors-with-killing-case + 5 equivalent-in-scope. Requirement ">= 25 mutants" met.

## Findings (coverage; survivors with proposed killing cases)

**F-1 (M03, first-order, anchored).** The counter's negation window `{0,3}` must not widen: the v4 tool binds a declaration with a 4-word negation gap (`SCORE.md is not in the least bit append-only` → tool exit 0, bad 0 — `out/M2Ctr/anchors.txt`), pristine's binder binds it, and M03 (`{0,6}`) unbinds it → `lane: contract row … does not bind under v4` on a lane the tool itself calls clean. Killing case: any lane whose contract row is declared by that line — pristine exit 0/met=True, M03 exit 1/met=False. Command shown in `anchors.txt`; run `python3 tool-tip.py --repo anchor/negation-gap-4 --to HEAD --contract anchor-negation-gap-4.contract.tsv --json` (exit 0).

**F-2 (M02, M04-M07, M10, M49 — masked second-line-of-defense).** The golden pair exercises the counter's own binder (`says`/`binds`, L84-103) only through the lane's 10 contract rows, none of which carries a negation, a digit/underscore word boundary, or an apostrophe middle word. Each of these mutants relaxes the binder and still passes both goldens, while the tool (correctly) rejects the underlying declarations (anchored exits 1 in `anchors.txt`), so the counter's exit-0/bad-0 check masks the binder. Killing case per mutant: a tip whose `tools/append-only-audit.py` regresses exactly that one v4 rule (e.g. M07: tool reverts to v3's four fixed strings — `SCORE.md is not strictly append-only` binds → tool exit 0 — pristine binder then fails the lane, mutant passes). Proposed closure (lane-side, not mine to implement): a junk-style control pair like C1's — run the counter against a scratch repo whose tip tool regresses one v4 rule and require met=False.

**F-3 (M11-M13).** Wild detection and the `not wild` self-declaration guard are only exercised by the `corpus/lessons/*.md` row (declared outside its own pattern). Killing cases: (a) M11/M12 — a lane row `notes/*.md` declared at `notes/a.md:1` `this file is append-only` with a tip tool that binds wildcard self-declarations (v3 behavior): pristine exit 1, mutant exit 0; (b) M13 — a pattern using `?`/`[` (e.g. `LOG[0-9].md` declared at `LOG5.md:1`): pristine token is `""` → unbinds, mutant self-binds.

**F-4 (M20).** The `bad_declarations == 0` lane clause is enforced only jointly with `exit == 0`. Killing case: a tool that exits 0 with `bad_declarations > 0` — pristine lane leg fails, mutant passes.

**F-5 (M22).** `met = fl and ll` is never differentiated by the goldens because both legs flip together on them. Killing case: any input where exactly one leg fails — e.g. F-1's 4-word-gap declaration on a lane row (tool exit 0, fixtures pass, binder rejects): pristine met=False, M22 met=True.

**F-6 (M39).** The strict region grammar `exempt=(.+)@[^@:]+:\d+` is never exercised by a malformed region. Killing case: a contract row with region `exempt=## Axes@NOTES.md` (no `:N`) — pristine drops the row from `titles` (and fails the lane on any ungraded event in that file), mutant parses it.

**F-7 (M42).** `fnmatch.fnmatchcase(f, pat)` is only hit with exact-name rows: the only ungraded events at tip are `SCORECARD.md`. Killing case: an ungraded event on a wildcard-covered file (e.g. `corpus/lessons/round-9.md` under `corpus/lessons/*.md`) — pristine computes `ex` from the row, mutant reports `ungrades lines in a file with no exempt row`.

**F-8 (robustness, killed-class).** `-U0` in `deleted_with_pos` (L271) is load-bearing: under `-U3` the hunk walker consumes context into the deleted-line census (native 23→15, 65→60) and the lane leg fails. M35/M37 show the base control is the only detector for exit-code and archive-target drift — keep `controls/base.c2.out` in every future run.

## Restoration evidence

- Before: `sha256sum tools/round49-append-audit-v4-check.py` → `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945`.
- After: same hash; scratch copy `pristine.py` identical; `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- tools/round49-append-audit-v4-check.py` → empty. All mutations lived in `/fast/scratch/hyaku/kama-r49/M2Ctr/mut/` (disposable, now removed).
- No services started: no llama-server was launched by this seat (the 5 `pgrep -f llama-server` hits at finish belong to other seats; none were started or stopped here).

## Commands

```
S=/fast/scratch/hyaku/kama-r49/M2Ctr
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 $S/mutgen.py                                   # 49 mutants, each asserted single-site
python3 $S/run_one.py pristine tip; python3 $S/run_one.py pristine base
for f in $S/mut/*.py; do echo "mut/$(basename $f .py) tip"; echo "mut/$(basename $f .py) base"; done \
  | xargs -P 6 -L 1 python3 $S/run_one.py
python3 $S/detect.py > out/M2Ctr/detect.txt
python3 $S/funccheck.py … > out/M2Ctr/funccheck.txt    # binder divergences for survivors
```
No tool installs were needed (python3 + git only).
