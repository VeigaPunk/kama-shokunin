# SrcS089 — git(1) global options (S089) re-open

Seat: CloseKama22.SrcS089-2. Base: lane checkout HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(`git rev-parse HEAD`, exit 0). No code edits; report only.

## Verdict: ADMIT (holds)

S089's URL, version label, both quoted sentences, scope and teaches all hold at
fetch time, and both used-by paths exist and are load-bearing. Two sentences in
`teaches` are page-derived inferences, not quotations; both are true and one is
already disclosed in the lesson. No row rewrite required.

## Evidence

### 1. URL and version claimed

`curl -sS https://git-scm.com/docs/git -o /tmp/gitdoc.html` exit 0 (2026-10-21).
Page header (selector + body): `git last updated in 2.56.0`; selector entry
`2.56.0 ... 2026-09-28`. Host binary: `git --version` → `git version 2.56.0`
(exit 0). The SOURCES anchor's phrase `page "git last updated in 2.56.0"` is
exact.

Caveat (not a defect): the registered URL is the unversioned `/docs/git`
alias, so "2.56.0" is the opening-time label, not a pin. The row records it as
a label and sets `recheck = on-release`, which matches the S087/S088
series-vs-micro distinction class; unlike those rows it never claims a micro
pin.

### 2. Quote located verbatim

Page OPTIONS section, immediately after `--no-replace-objects` and
`--no-lazy-fetch` headings:

- "Do not use replacement refs to replace Git objects." (10 words)
- "Do not fetch missing objects from the promisor remote on demand." (11
  words; HTML wraps after "on")

Both strings also occur exactly once on the versioned page
`https://git-scm.com/docs/git/2.56.0` (`grep -c` → 1 each). The lesson Gate at
`corpus/lessons/round-23.md:27-29` reproduces both sentences with the URL and
"(2.56.0)", byte-equal after line unwrapping.

### 3. Scope / teaches do not overreach

- Scope "git global options that disable replacement refs and promisor lazy
  fetch for one invocation": both are SYNOPSIS-level global options
  (`[-p | --paginate | -P | --no-pager] [--no-replace-objects]
  [--no-lazy-fetch] ... <command> [<args>]`), and the page gives each an
  env-var equivalent, so the CLI form is per-invocation. Holds.
- Teaches sentence 1 and 2 restate the two quotes. Holds.
- "Both are global options placed before the subcommand" — supported by the
  SYNOPSIS ordering and by behavior: in a fresh `/tmp` repo (global/system
  config nulled, explicit identity), `git --no-replace-objects --no-lazy-fetch
  rev-parse --short HEAD` → `09e142d`, rc 0; the same token after a subcommand
  is passed through by `rev-parse` rather than parsed as a global option. This
  clause is [INFERENCE] from the page layout, not prose on the page.
- "Neither covers info/grafts or shallow" — page-silence inference
  [INFERENCE]: `grep -i 'graft'` over the fetched page returns 0 matches; the
  only `shallow` text is the unrelated `GIT_TRACE_SHALLOW` trace variable
  ("Enables trace messages that can help debugging fetching / cloning of
  shallow repositories."). The statement is true of the two options and is
  used as a limit, not as a positive mechanism claim; consistent with the
  tool's separate F10/F11 refusals.

### 4. Used-by paths cite or rely on it

- `corpus/lessons/round-23.md:27-29` — Gate row cites S089 and the two
  sentences verbatim.
- `tools/report-landing-audit.py:93` — `GIT_ISOLATION =
  ("--no-replace-objects", "--no-lazy-fetch", ...)`; `:114` —
  `subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args], ...)`, so
  both flags precede `-C` and the subcommand. `:49-51` docstring states the
  replacement/lazy-fetch channels are neutralized.
- "Supports F03–F05 and F06" is accurate: `tests/report-audit/repo-state-grid.py:541-547`
  maps F03/F04/F05 to replacement fixtures (`f_replace_omission` sets
  `git replace` at `:238`; `f_replace_fabricated` sets `refs/replace/<40-hex>`
  at `:248`) and F06 to `f_lazy_fetch`, whose premise sets
  `remote.origin.promisor=true` and `core.sshCommand` (`:277-282`), expected
  refusal exit 2 with reason "partial clone" (`:581`).
- Reliance nuance, already disclosed: `isolation-mutants.py:29-30` shows M01
  (replace flag) killed and M02 (lazy-fetch flag) surviving; lesson `:79-81`
  declares `--no-lazy-fetch` defensive-only because the promisor refusal runs
  first. So S089's replace sentence is verdict-relevant; its lazy-fetch
  sentence is code-relied but not grid-decisive — consistent with the row and
  lesson, no hidden overclaim.
- `grep -rn S089` over the checkout finds only `corpus/SOURCES.md:101`,
  `corpus/lessons/round-23.md:27`, and wave-local artifacts. `SKILL.md:781`
  documents the same command line but names no source row; its omission from
  the used-by cell is convention, not a missing citation.

## Not verified

- Did not run `repo-state-grid.py` or `isolation-mutants.py` (source-row seat;
  L1's numbers taken as reported, not re-measured).
- Did not audit whether any git call in `report-landing-audit.py` bypasses the
  shared `git()` wrapper; only `:114` was checked.
- Did not test behavior on git < 2.45 (lesson's floor claim) or on releases
  other than the live 2.56.0 page.
- Did not verify git-scm.com page stability over time; findings are the
  2026-10-21 fetch only.

## Files written

- `.ufo/waves/round-23/falsify/advice/SrcS089.md` (this report)

No installs or upgrades performed; no tool records to report.

## Addendum — negative/placement claims under KQ9 and KQ22

Full-set read for the "neither covers info/grafts or shallow" clause at the
fetched page (count first, then read): `grep -o -i 'graft'` → 0 matches;
`grep -o -i 'shallow'` → 5 raw matches, all the single rendered
`GIT_TRACE_SHALLOW` entry ("Enables trace messages that can help debugging
fetching / cloning of shallow repositories."), so the page has no
option-semantics statement tying either global option to shallow or grafts.
The clause is therefore a page-scope limit [INFERENCE], in the same class as
the accepted S067 wording ("the page is silent on symlinks"), not a
mechanism claim. Placement's only page basis is the SYNOPSIS; there is no
prose "before the subcommand" sentence.

KQ6 fit: the anchor names the engine (git), revision label ("git last updated
in 2.56.0"), section (OPTIONS) and both options; quotes are byte-exact. KQ22
consequence: no cell rewrite is needed; any future wording change to the
teaches cell would have to be a `supersedes S089` row, which this seat does
not open. ADMIT stands.
