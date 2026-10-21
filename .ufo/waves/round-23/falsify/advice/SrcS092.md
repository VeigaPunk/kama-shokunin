# SrcS092 — git partial-clone design note (S092) re-open

Seat: CloseKama22.SrcS092-2. Base: lane checkout HEAD
`245a37f69628c2c6bb29bbf17897d8fb5946c857` (`git rev-parse HEAD`, exit 0).
No code edits; report only. No clone was needed because this seat only reads
tracked files and writes this untracked report.

## Verdict: ADMIT the row (holds), with one Gate over-attribution

S092's URL, version label, quote and scope hold at fetch time. The registered
sentence is verbatim, occurs once, and the row's `teaches` first clause is its
literal consequence. Two defects are named below and neither is a false source
claim in the row itself: (a) the lesson Gate says the quote "Supports F06/F23
refusals", but F23's refusal is supported by different, unquoted sentences on
the same page; (b) the anchor cell names the wrong section title. Fixes belong
in the append-only lesson/Gate channel and, for the anchor, would require a
`supersedes S092` row under KQ31 — this seat opens neither.

## Evidence

### 1. URL, version claimed, effective fetch

```
curl -sS -o /dev/null -w 'final=%{url_effective} code=%{http_code} type=%{content_type}\n' \
  -L --max-time 60 https://git-scm.com/docs/partial-clone
final=https://git-scm.com/docs/partial-clone code=200 type=text/html; charset=utf-8
```

No redirect. The header carries exactly one instance of:

`<span class="light d-flex">partial-clone last updated in 2.56.0</span>`

so the row's `page "last updated in 2.56.0"` (`corpus/SOURCES.md:104`) is the
page's own label, not an inferred date. The dropdown labels this "Latest
version". I also fetched `https://git-scm.com/docs/partial-clone/2.56.0`
(code=200); it carries the same marker and the same quote once.

### 2. Quote located verbatim

The row's Gate sentence (`corpus/lessons/round-23.md:38-40`) appears once in
the rendered page, in the § **Handling Missing Objects** body:

> "For efficiency reasons, no check as to whether the missing object is
> actually a promisor object is performed." (15 words)

Its immediate predecessor on the page is the mechanism the row's scope names:

> "When the normal object lookup fails to find an object, Git invokes
> promisor_remote_get_direct() to try to get the object from a promisor
> remote and then retry the object lookup. This allows objects to be
> 'faulted in' without complicated prediction algorithms."

Checks run on the stripped text: `quote_count=1` on both the live and the
`/2.56.0` pages; HTML line wrap between "is" and "actually" only.

### 3. Scope and teaches vs the quote

- Scope `promisor lazy fetch on missing objects` matches §Handling Missing
  Objects narrowly. It does **not** claim promisor-pack detection, promisor
  config keys, or object-store corruption generally.
- Teaches clause 1 — "A missing-object lookup in a promisor repository fetches
  on demand without first checking that the object is a promisor object" — is
  the two sentences above restated. Holds, including the condition: fetching
  is attempted via a *configured promisor remote*, and the page elsewhere says
  "Use of partial clone requires that the user be online and the origin remote
  or other promisor remotes available".
- Teaches clause 2 — "absence there is not evidence" — is **[INFERENCE]**, not
  page prose. It follows from "faulted in": a failed local lookup may mean
  "not fetched", not "absent upstream". The row does not mark the inference
  (S033 does mark an equivalent one). True as a scoped consequence, not a
  quotation; a wording nit, not a source error.

### 4. Anchor cell points at the wrong section title

Row anchor (`corpus/SOURCES.md:104`): `section on fetching missing objects`.
The quote is **not** in §Fetching Missing Objects; that h2 begins later with
`Fetching of objects is done by invoking a "git fetch" subprocess.` The quote
is in §Handling Missing Objects. The build-wave advice had this right
(`.ufo/waves/round-23/build/advice/SrcPartialClone.md`: "§Handling Missing
Objects, bullets 3–4"), so the integration loosened a correct anchor. A
reader following the anchor lands in the adjacent section and finds the
promisor-remote config-key list, not the quoted sentence. Under KQ22 only
`supersedes S092 —` can repair the cell.

### 5. Used-by actually cites it

The row's only used-by path, `corpus/lessons/round-23.md`, cites S092 at
`:38-40` with URL, `(2.56.0)` and the exact sentence. The path exists at HEAD
(`git cat-file -e HEAD:corpus/lessons/round-23.md` exit 0). Status `mined`
therefore has its cited path, per contract.

### 6. Gate reliance over-attributes F23

The Gate adds "Supports F06/F23 refusals" (`round-23.md:40`). Against the
committed grid and audit:

- F06 (`tests/report-audit/repo-state-grid.py:547`, reason "partial clone"
  `:581`, fixture `:271-286`) configures `extensions.partialClone`,
  `remote.origin.promisor=true` and a `core.sshCommand` marker; the fixture's
  premise is a `cat-file -e` on a fabricated 40-hex object that runs the
  configured command. That premise is exactly the quoted "no check … is
  performed". But the audit's exit 2 comes from
  `tools/report-landing-audit.py:446-448` (`extensions.partialclone` /
  `remote\..+\.promisor`), not from a lazy-fetch lookup; `--no-lazy-fetch`
  (`:93`) is the defensive-only flag M02 survives
  (`tests/report-audit/isolation-mutants.py:30`). So the quote supports F06's
  *premise*, not its refusal branch.
- F23 (`repo-state-grid.py:566`, reason "promisor pack" `:588`, fixture
  `:194-212`) removes `extensions.partialClone`,
  `remote.origin.promisor` and `remote.origin.partialclonefilter` from a
  blobless clone, then requires a surviving `*.promisor` pack and a missing
  blob. With no promisor remote configured, no lazy fetch is attempted, so the
  quoted sentence is inert for this case. The audit refuses from the
  `*.promisor` file check (`tools/report-landing-audit.py:443-444`), which the
  page supports by a *different* sentence — "These promisor packfiles consist
  of a `<name>.promisor` file with arbitrary contents" — and by the promisor
  object definition, both in §Handling Missing Objects, neither registered in
  S092's anchor or quote.

Conclusion: S092 is a valid source for the lazy-fetch mechanism (F06 premise,
defensive flag); the Gate's claim that this quote supports the F23 refusal is
not supported by the registered quote. The page does support both refusal
detectors, but through the promisor config list (§Using many promisor
remotes: `extensions.partialClone`, `remote.<name>.promisor = true`,
`remote.<name>.partialCloneFilter`) and the promisor-packfile definition, all
outside S092's scope and anchor. The correction is an appended Gate line, not
a row rewrite.

### 7. Used-by under-lists one relier (informational)

`tools/report-landing-audit.py:429` carries the row's conclusion in its own
words ("absence is not evidence there") and `:443-448` implements the promisor
refusal, yet the audit is absent from S092's used-by. S089, S091 and S095 list
`tools/report-landing-audit.py`; S090 does not, so lane convention is
inconsistent. `used-by` is an editable cell under KQ22, so this is a
completeness gap, not an append-only violation. It does not make the current
cell false.

## Not verified

- Did not run `repo-state-grid.py` or `isolation-mutants.py`, or re-measure
  F06/F23; the L1 counts are taken as reported.
- Did not audit whether git's `fetch_if_missing` can be disabled by repository
  state other than the CLI/env switches; only the page text was read.
- Did not test the page's behavior offline, on another git release, or
  against a future docs update; findings are the 2026-10-21 fetch, checked on
  both the live and `/2.56.0` URLs.
- Did not verify the page's claim by executing a lazy fetch against
  `example.invalid` (behavior is taken from the page and the grid fixture's
  premise as committed, not re-run).

## Files written

- `.ufo/waves/round-23/falsify/advice/SrcS092.md` (this report)

No installs or upgrades performed; no tool records to report.
