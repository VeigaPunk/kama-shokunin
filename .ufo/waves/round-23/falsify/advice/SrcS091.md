# SrcS091 — git-config row and Gate re-open (round 23, falsify wave)

Seat: `CloseKama22.SrcS091-2` (leaf, no dispatch). Lane base verified:
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` →
`245a37f69628c2c6bb29bbf17897d8fb5946c857`. All lane paths below are at that
commit. No tracked file was written; no fixture, audit run or mutation was
executed for this report.

## Verdict

**Admit — the source and the row's `teaches` hold.** Every key and every
sentence the row relies on exists verbatim on the fetched page, and the claimed
page version is correct.

**One Gate statement is falsified, and three row fields need correction.**
The Gate labels the quoted showSignature sentence as covering `log.follow`/
`log.showSignature` jointly; the sentence is `log.showSignature`'s only, and
`log.follow` has a different sentence on the same page. Separately, the row's
`scope` no longer covers the `core.sshCommand` transport key it anchors, the
F09 program-execution half is anchored nowhere (`gpg.program`), and `used-by`
omits the fault grid that actually exercises all six keys.

If the integrator's rule is "admit only when Gate attribution and scope match
the row", this row is not admissible as written; the defects are in the
presentation fields, not in the source claim.

## 1. Fetch and version

```
$ curl -sSIL --max-time 60 https://git-scm.com/docs/git-config
HTTP/2 200
content-type: text/html; charset=utf-8
last-modified: Wed, 21 Oct 2026 04:42:24 GMT
```

- `<title>`: `Git - git-config Documentation`
- Version marker, exactly one occurrence:
  `<span class="light d-flex">git-config last updated in 2.56.0</span>`
- Version dropdown: `Latest version`; 2.56.0 shown dated `2026-09-28`.

Row `corpus/SOURCES.md:103` claims `page "last updated in 2.56.0"`, opened
2026-10-21. **Matches.** The URL is the floating latest-version page, not a
2.56.0 hard pin; the row's `on-release` recheck is the right setting for that.

## 2. Quote-by-quote verification

Page text was extracted from the fetched HTML (tags stripped, whitespace
normalized) and tested with exact substring matching.

| Row / Gate claim | Page text | Result |
|---|---|---|
| `log.showSignature` | "If true, makes git-log[1], git-show[1], and git-whatchanged[1] assume --show-signature." | verbatim, exact `dd` block |
| `i18n.logOutputEncoding` | "Character encoding the commit messages are converted to when running git log and friends." | verbatim, exact `dd` block |
| `log.follow` | "If true, git log will act as if the --follow option was used when a single <path> is given. This has the same limitations as --follow, i.e. it cannot be used to follow multiple files." | verbatim; **different sentence** from the one the Gate prints |
| `log.showRoot` | "If true, the initial commit will be shown as a big creation event. ... Tools like git-log[1] or git-whatchanged[1], which normally hide the root commit will now show it. True by default." | verbatim |
| `log.mailmap` | "If true, makes git-log[1], git-show[1], and git-whatchanged[1] assume --use-mailmap, otherwise assume --no-use-mailmap. True by default." | verbatim |
| `core.sshCommand` | "If this variable is set, git fetch and git push will use the specified command instead of ssh when they need to connect to a remote system." | verbatim |

Raw HTML proof that the Gate's quoted sentence belongs to
`log.showSignature`, not `log.follow` (fetched copy, raw indices 563234 and
565572):

```
<dt ...>log.follow</dt>
<dd><p>If <code>true</code>, <code>git log</code> will act as if the ...
a single &lt;path&gt; is given. ...

<dt ...>log.showSignature</dt>
<dd><p>If true, makes <a href='/docs/git-log'>git-log[1]</a>, ...
assume <code>--show-signature</code>.</p></dd>
```

The `-c`-over-files claim in the row's `teaches` is supported on the same page,
though the Gate does not quote it:

- SCOPES order ends `local` → `worktree` → `command` → `the -c option`.
- ENVIRONMENT, GIT_CONFIG_COUNT: "These environment variables will override
  values in configuration files, but will be overridden by any explicit options
  passed via git -c." (21 words)

## 3. The Gate line (`corpus/lessons/round-23.md:33-37`)

Printed line:

```
- S091 https://git-scm.com/docs/git-config (2.56.0) — `log.follow`/
  `log.showSignature`: "If true, makes git-log[1], git-show[1], and
  git-whatchanged[1] assume --show-signature."; `i18n.logOutputEncoding`:
  "Character encoding the commit messages are converted to when running git
  log and friends." Supports F01, F07–F09, F14, F22.
```

Confirmed defect: the one quote is `log.showSignature`'s. Slash-labeling it with
`log.follow` is false as written. The lesson's preamble claims quotes were
"located by exact string match"; the string is located, but it is attached to a
key that has its own, different sentence. `log.follow`'s own sentence is on the
same page and is already quoted by S093 (`corpus/lessons/round-23.md:44`).

Consequence for support mapping: F07 (`tests/report-audit/repo-state-grid.py:548`)
is supported by the git-config page only through the unprinted `log.follow`
sentence, and F09 (`:550`) only through the showSignature sentence. The line as
written still points at true page facts, but its quote-to-key attribution is
wrong.

## 4. `teaches` and `scope` versus the page

`teaches` at `corpus/SOURCES.md:103`: "Each key alters log/show output or the
fetch transport for every reader of that repository; command-line `-c` values
override configuration files."

- Log/show half: true for the five `log.*`/`i18n.*` keys; each is described as
  changing log/show behavior (encoding conversion, follow, root display,
  signature display, mailmap).
- Transport half: true for `core.sshCommand` — the page scopes it to `git fetch`
  and `git push`.
- `-c` precedence: true (SCOPES ordering plus the quoted ENVIRONMENT sentence).

`scope` at the same line: "repository-local keys that change git log output the
audit parses."

- This covers five of the six anchored keys. `core.sshCommand` does **not**
  change log output; it changes fetch/push transport. The row's own `teaches`
  and the grid's F06 (`repo-state-grid.py:280`) depend on that transport role,
  which the `scope` cell no longer grants. **Scope is narrower than anchor and
  teaches — the teaches overreaches its own declared trust boundary.**
- The build-wave draft had the transport in scope
  (`.ufo/waves/round-23/build/advice/SrcGitEnv.md:37`: "keys that change the
  fetch or push transport command and the decoding of git log output ... not a
  claim about lazy fetch"). Integration dropped both the transport phrase and
  the "not a claim about lazy fetch" boundary. The boundary matters: the page
  does not say lazy fetch runs `core.sshCommand`; `SrcGitConfig.md` §6 flag 1
  says the same, and grid F06 only establishes the link empirically through its
  own `require()`.
- "repository-local" is consistent with the page's SCOPES section
  (`local $GIT_DIR/config`); none of these keys is restricted to protected
  configuration.

## 5. `used-by` audit (`corpus/SOURCES.md:103`)

Claimed: `corpus/lessons/round-23.md, tools/report-landing-audit.py`.

- `corpus/lessons/round-23.md:33-37` cites S091. **Yes.**
- `tools/report-landing-audit.py` **relies** on five of the six keys but never
  cites the row: `grep -c S091 tools/report-landing-audit.py` → `0`; the keys
  appear at `:93-96` (`i18n.logOutputEncoding=UTF-8`, `log.follow=false`,
  `log.showRoot=true`, `log.showSignature=false`, `log.mailmap=false`).
  Reliance is real, so the used-by cell is not false — but it is reliance, not
  citation. `core.sshCommand` is not neutralized by the tool; isolation there
  rests on `--no-lazy-fetch` and the promisor refusal.
- **The strongest consumer is missing.** `tests/report-audit/repo-state-grid.py`
  uses every anchored key: F01 `:539`, F06 `core.sshCommand` `:280`/`:547`,
  F07 `:548`, F08 `:549`, F09 `:550` with `gpg.program` `:331`/`:334`,
  F14 `:555`, F22 `:565`. The grid's `require()` premises encode the page's
  claims, so it relies on S091 just as much as the tool does. `used-by` omits
  it.

## 6. F09 is only half-anchored (`gpg.program`)

The showSignature sentence establishes that log/show "assume --show-signature";
it does not establish that a repository-configured program is executed. That
half is documented on the same page under `gpg.program` ("Pathname of the
program to use instead of \"gpg\" when making or verifying a PGP signature ..."),
but:

- `gpg.program` is not in S091's anchor;
- `grep -n gpg.program corpus/SOURCES.md` → no match (no other row anchors it);
- the only registry consumer is the grid at `:331`/`:334`.

So the Gate's "Supports ... F09" is supported only if `gpg.program` is added to
the anchor (with its quote or a cross-reference), or the F09 support claim is
narrowed to "sets `log.showSignature`" and the program-execution premise is
declared grid-observed.

## 7. Duplicate registration (cross-reference)

`i18n.logOutputEncoding` and `log.follow` are named in S091's anchor
(`corpus/SOURCES.md:103`) and again in S093 (`:105`, `--encoding` paragraph and
CONFIGURATION `log.follow`). The lesson's rejection note at `:54-55` says the
separate `log.follow` row was "kept once"; the final registry registers the key
twice and maps F07 to both rows. This is the same finding as
`falsify/advice/SrcS093.md` §item 2; recorded here because it touches S091's
anchor. It is an integration ownership issue, not a false source claim.

## 8. Corrections required

1. **Gate line `round-23.md:33-34`:** drop `log.follow` from the label of the
   showSignature quote (or quote `log.follow`'s own sentence). Current label is
   falsified by the page.
2. **Scope `SOURCES.md:103`:** restore the transport half, e.g. "repository-local
   keys that change git log output or the fetch/push transport", and restore the
   "page does not document lazy-fetch execution" boundary.
3. **Anchor `SOURCES.md:103`:** add `gpg.program` (F09 program execution) or
   narrow the F09 support claim in the Gate.
4. **used-by `SOURCES.md:103`:** add `tests/report-audit/repo-state-grid.py`
   (all six keys, F01/F06/F07/F08/F09/F14/F22).

## 9. Did NOT verify

- Did not run the audit, the grid, the mutants, or any git fixture; no exit
  codes beyond the fetch/grep/rev-parse commands shown.
- Did not verify git 2.56.0 binary behavior for any key on this host; all claims
  are page text plus code reads.
- Did not check the localized git-scm.com pages, a `git help config` render, or
  a version-pinned `Documentation/config.txt` at the 2.56.0 tag.
- Did not verify the historical page state at the row's opening time; the fetch
  is the 2026-10-21 render (`last-modified` same day).
- Did not test whether `-c` overrides a *worktree*-scope value specifically;
  only the page's SCOPES ordering and its GIT_CONFIG_COUNT sentence.
- No tools installed or updated.

## 10. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/SrcS091.md`
  (this file). No other file written; lane tracked files untouched.
