source: S175 — Git git-merge-base, https://git-scm.com/docs/git-merge-base §OPTIONS `--is-ancestor` (docs, tier A; the round's live re-open of 2026-11-03, retained bytes sha256 `46d106b77…`, recorded in `corpus/lessons/round-72.md` §Gate): "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not."; the following sentence separates errors (a nonzero status that is not 1) from a false verdict. The round's new **S543** (`corpus/SOURCES.md:295`, `git-check-ignore`, docs, tier A, status `mined`, used-by this entry; §EXIT STATUS: "0 One or more of the provided paths is ignored. 1 None of the provided paths are ignored.", page "last updated in 2.52.0", fetched bytes sha256 `bdee84a9…`) grounds C1's ignored-path case only — this binding reads committed git objects (`cat-file`, `merge-base --is-ancestor`, `rev-list`/`diff-tree`), never ignore rules. Contract: `plans/round-72-claims.md` §C2 (frozen predicate, counter, kill rule, exit map). Instrument: `tools/round72-receipt-tip-binding.py`.
verified-at: the round-72 instrument commit (pre-commit tip `a3cc39f0` plus this round's uncommitted instrument and record edits). Instrument bytes graded by the round's receipts: `tools/round72-receipt-tip-binding.py` sha256 `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd`; the frozen contract `plans/round-72-claims.md` sha256 `c656e66b2bc3b97164366babb125ffa1cc4ce7c409c8a2943235d92f1be889a1` (the committed `a3cc39f0` text plus the pre-score amendment 2 that makes `cited=0` exit 2). The entry cites two receipts that were green before this line was written: `.ufo/waves/round-72/measured/before/receipt-tip-control-old.out` (`BINDING_CONTROL cited=3 accepted=3 rejected=0`, exit 1 — the shortcut the claim removes) and `.ufo/waves/round-72/w1/CRT01ReceiptAttack/live-r71-min.out` (`RECEIPT_TIP_BINDING round=71 cited=1 bound=1 unbound=0 shifted=0 stale=0`, exit 0 — the round-71 record re-graded by these bytes). The C1 arm's own bytes are `tools/round72-round-scope.py` sha256 `45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4`.
recheck: `python3 tools/round72-receipt-tip-binding.py --repo . --round 72 --tip master` → one `RECEIPT_TIP_BINDING round=72 cited=<c> bound=<c> unbound=0 shifted=0 stale=0` line, exit 0 (exit 2 names the could-not-evaluate reason and is not a pass); `python3 tools/round72-receipt-tip-binding.py --selftest`; S175 on-release.

# Receipt-to-revision binding (receipt-tip binding)

A round cites receipts. The binding question is not whether a receipt is true; it is whether the
revision the receipt names was still the code base when the record citing it was written. The
frozen sentence:

> `python3 tools/round72-receipt-tip-binding.py --repo <lane> --round <N> --tip <rev>` prints one
> `RECEIPT_TIP_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t>` line and
> exits 0 only when every receipt path cited by the round's self-record (`SCORECARD.md`'s
> round-`<N>` section and `corpus/lessons/round-<N>.md`) exists at `<rev>`, carries a
> `# tip=<40-hex>` or `# rev=<40-hex>` header, names a revision that is an ancestor of `<rev>`,
> and every commit in `<rev>..<tip>` touches only declared record paths; it exits 1 naming each
> `RECEIPT_TIP_FINDING <unbound|shifted|stale> <path>`.

## What it establishes

Four conjuncts, and only these:

1. **Existence** — the cited path is a blob at the tip (`git cat-file -e <tip>:<path>` exits 0).
   Citations are expanded from the self-record's notation (full, section-relative, brace, glob);
   a citation resolving to no receipt is `stale`, a non-receipt path is exit 2, and a root-relative
   `tools/`/`corpus/` citation is out of scope (tool docstring §Population sources).
2. **Declaration** — the receipt carries a 40-hex revision header. The header forms are two
   (`grep -o '# tip=<40-hex>\|# rev=<40-hex>' plans/round-72-claims.md | sort -u | wc -l` → `2`).
3. **Ancestry** — `git merge-base --is-ancestor <header-rev> <tip>` exits 0. S175: status 0 means
   the first is an ancestor of the second. A commit is its own ancestor, so a receipt naming the
   tip itself binds; this check is not a strict-ancestor check.
4. **Record-only delta** — every commit in `<header-rev>..<tip>` changes only declared record
   paths. No instrument input moves between the revision the receipt names and the record that
   cites it.

Together they say: the named revision is inside the tip's history, and no graded-input byte moved
after it. This is the machine form of the round-71 hand argument ("the only commits after it add
receipts") — the counter replaces the argument, it does not strengthen it.

## What it does not establish

- **Not the receipt's content.** The frozen non-goal is exact: "the binding does not prove a
  receipt's *content* is honest (C1's module and the existing instruments grade that); it binds a
  receipt to the revision whose bytes it graded."
- **Not that the command ran.** The header is self-declared text inside the receipt. A fabricated
  header naming a real, ancestor commit with a record-only delta binds.
- **Not "measured at the tip".** A receipt naming an earlier ancestor still binds when the delta
  is record-only. Round 71's `4b284653` receipt against tip `7fb6cb4e` is that shape; the
  spot-check's defect 4 was the report's wording ("at the report tip"), which the binding does
  not grade. The counter separates *named revision* from *content*.
- **Not worktree bytes.** It reads objects at the tip. An uncommitted receipt, or an uncommitted
  self-record that cites one, is outside the grade (C1's arm 6 covers uncommitted bytes).

## Failure classes (frozen kill rule, quoted)

> a receipt with no header (`unbound`), a header naming a non-ancestor or a revision whose delta
> touches `tools/` (`shifted`), and a cited receipt absent at the tip (`stale`) each exit 1 and
> name their class; the clean fixture exits 0.

| Class | Frozen condition | What it denies |
|---|---|---|
| `unbound` | no `# tip=`/`# rev=` header | which revision the receipt measured |
| `shifted` | header names a non-ancestor, or the delta touches an instrument input | that the receipt's basis is the code the tip ships |
| `stale` | cited path absent at the tip | that the cited receipt exists at the measured revision |

Exit map: `0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, unreadable self-record, a
cited path that is not a receipt path, or `cited=0` — an empty population is never a pass). A `2`
is a refusal to grade, not a green.

## Record path vs instrument input

Two lists with two jobs:

- **record paths** (5; `--record-path` replaces the default list): `.ufo/waves/round-<N>/**`,
  `corpus/lessons/**`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`.
- **instrument inputs** (7; never record paths): `tools/**`, `SKILL.md`, `PROVINCE.md`,
  `corpus/SOURCES.md`, `corpus/knowledge/**`, `registry/**`, `plans/**`.

Counts: `python3 -c "import re;t=open('plans/round-72-claims.md').read();t=t[t.index('## C2'):];a=t[t.index('- record paths'):t.index('- exit map')];print([len([x for x in re.findall(r'\`([^\`]+)\`',s) if not x.startswith('--') and x!='shifted']) for s in a.split('- instrument inputs')])"` → `[5, 7]`.

The operative rule is the **allow-list**, not the instrument-input list: every changed path in the
delta must match a record path, so a commit touching `corpus/QUALITY.md` or `tests/**` also makes
the binding fail even though neither is named as an instrument input. The seven instrument inputs
are the named subset whose change is always `shifted`; they are the surfaces where the *measuring
apparatus* lives, as against the record paths where a round's *evidence about itself* lives.
Editing either end changes what a receipt is evidence for; editing the apparatus is the case the
binding refuses by name.

## Operational consequence: commit order

[INFERENCE] Because `plans/**`, `tools/**`, `corpus/knowledge/**`, `registry/**`, `SKILL.md`,
`PROVINCE.md` and `corpus/SOURCES.md` are instrument inputs, a receipt that names the freeze base
is `shifted` at any tip that also lands this entry, the round's tools or a plan amendment. The
order that can bind: land every instrument input first (revision R), take the receipts naming R,
then commit only record paths (wave receipts, lesson, `SCORECARD.md`, `LOG.md`, `corpus/README.md`).
Confirming fixture: a clean delta that is record-only binds, while one committing a
`corpus/knowledge/` line is `shifted`.

C1's arm 6 is a different list with a different question: it grades `git status --porcelain -uall`
over the whole repository and its gate invocation passes no `--allow` (`tools/round72-round-scope.py`
docstring, worktree read at `a3cc39f0`; `tools/pre-report-gate.py` `ARM_SPECS`), so it wants a
clean worktree rather than a record-only delta. Both hold at one tip only when the worktree is
fully committed and the receipts name the commit that last changed an instrument input — the same
order, one condition stricter.

## Limits

- The binding ties a receipt to the revision whose bytes it graded, never to the receipt's content
  (frozen non-goal). It is necessary evidence for a cited measurement, not sufficient evidence.
- The frozen sentence reuses `<rev>` for the `--tip` argument ("exists at `<rev>`") and for the
  receipt's header ("every commit in `<rev>..<tip>`"); read the delta clause as
  header-revision..tip, the only reading the kill rule ("a revision whose delta touches `tools/`")
  supports. Reported as a wording limit, not edited here.
- The frozen sentence fixes the two header spellings, not the line window; the built tool reads a
  40-hex `tip=`/`rev=` match among the first five lines (`#` optional, short revisions rejected,
  two different revisions in the window `unbound`, a non-ancestor header `shifted` —
  `HEADER_WINDOW`/`HEADER_RE`/`_evaluate`, worktree bytes sha256 `789c0559…`).
- `--selftest` and fixture arms grade the tool; they do not upgrade a lane run that exits 2.
- Ignored paths are C1's question: this binding never consults ignore rules, so an ignored receipt
  is visible to it exactly like any other committed blob.
