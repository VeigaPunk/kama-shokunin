# SrcS094 — source-row falsification (S094 gitrepository-layout)

Seat: CloseKama22.SrcS094-2 (leaf, no dispatch). Lane base verified
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` →
`245a37f69628c2c6bb29bbf17897d8fb5946c857`.

## Verdict

**ADMIT (holds).** The row at `corpus/SOURCES.md:106` is factually backed by the
fetched page: both Gate quotes are verbatim (one after whitespace normalization
of the page's own line wrap), the claimed version table is exact, the scope
names exactly the four sections the page carries, and the single used-by path
really cites and relies on the row. Three precision defects in the Gate
citation are recorded below; none states a falsehood and none backs a graded
claim that the page does not support.

## Evidence

### Quotes (fetched 2026-10-21, exit 0)

`curl -fsS https://git-scm.com/docs/gitrepository-layout -o /tmp/r23-s094-page.html`
→ `curl_exit=0`; grep -c for quote 1 = 1, quote 2 = 1.

- https://git-scm.com/docs/gitrepository-layout §info/grafts — "Note that the
  grafts mechanism is outdated and can lead to problems transferring objects
  between repositories" (16 words). Gate quote is the same text truncated at
  "outdated".
- https://git-scm.com/docs/gitrepository-layout §refs/replace/\*<obj-sha1>\* —
  "Such refs can be exchanged between repositories while grafts are not."
  (13 words). Exact under whitespace normalization; the page and the lesson
  both wrap the sentence across a line break.
- Supporting text not quoted by the Gate: §shallow — "This is similar to
  `info/grafts` but is internally used and maintained by shallow clone
  mechanism." (16 words); §objects item 2 / §objects/info/alternates — "borrow
  objects from other object stores".
- Same page, §objects item 1, explicitly calls a shallow clone "an incomplete
  but locally usable repository".

### Version claimed

Row says "page version table 2.49.1→2.56.0 no changes". Page carries
"Latest version … gitrepository-layout last updated in 2.49.0" and the first
changes-table entry "2.49.1 → 2.56.0 no changes" (both matched with `grep -o`,
exit 0). Local interpreter for the claim: `git --version` → `git version 2.56.0`.
No 2.57 entry exists on the page. **Accurate.**

### Teaches vs source

Row teaches at `corpus/SOURCES.md:106`: "Grafts and shallow rewrite visible
history outside refs/replace; alternates make another store's objects resolve
as local."

- grafts "pretend the set of parents a commit has is different from how the
  commit was actually created" (§info/grafts) → visible-ancestry override: yes.
- shallow is "similar to `info/grafts`" (§shallow) → the "shallow" clause rests
  on that page sentence; see caveat C2.
- "outside refs/replace" matches the page's own contrast ("This is similar to
  info/grafts … Such refs can be exchanged … while grafts are not") and the
  file-vs-ref placement.
- alternates "borrow objects from other object stores" (§objects item 2) →
  "resolve as local" is a behavioral paraphrase; see caveat C3.

Scope ("on-disk history rewriting and borrowing: info/grafts, shallow,
refs/replace, objects/info/alternates") does not extend to clone policy,
replacement safety, lazy fetch or `.git` gitfiles. **No overreach in scope.**

### Used-by

Row lists `corpus/lessons/round-23.md`. At base 245a37f6,
`corpus/lessons/round-23.md:45-48` names the URL, the version and both quotes
and maps them to "F10/F11 and the O01 alternates limit". Those are the rows
`tests/report-audit/repo-state-grid.py:551` (`F10-shallow-lane`),
`:552` (`F11-grafts-lane`) and `:570` (`O01-alternates-foreign-object`); pinned
reasons at `:582-583` are "shallow repository" / "rewrites history", matching
the audit's raises at `tools/report-landing-audit.py:436-441`. The tool
docstring at `tools/report-landing-audit.py:44,51-54` states the same semantics
("shallow, grafted … refused"; alternates "still resolve as local"). So the
listed path genuinely cites and relies on the row.

`git show HEAD:corpus/SOURCES.md | grep -n S094` → line 106; no duplicate row
carries the page (`grep -n 'gitrepository-layout\|info/grafts\|objects/info/alternates'
corpus/SOURCES.md` → only S094, plus S089's "Neither covers info/grafts or
shallow" in-tier remark). Status `mined` is consistent with the lesson citation
under the registry's own rule (queued → mined when a lesson/knowledge entry
cites it).

## Caveats (precision, not rejection)

- **C1 — truncated quote without ellipsis.** Gate quote 1 stops at "outdated";
  the page sentence continues "and can lead to problems transferring objects
  between repositories". The fragment is a verbatim substring, but a reader
  cannot see the sentence boundary. Add `…` or the full clause.
- **C2 — F10 (shallow) is not quote-backed in the Gate.** The two Gate quotes
  cover grafts and the refs/replace contrast (F11 + the replace distinction).
  The shallow half of the row's teaches, and the F10 mapping, rest on §shallow's
  "This is similar to `info/grafts` …" — named in the row's anchor, present on
  the page, but absent from the Gate quote list. If the wave requires one
  located quote per mapped fault, add that sentence; as written, "Supports
  F10/F11" is one-half shown by the quotes.
- **C3 — "rewrite" and "resolve as local" are the row's compression.** The page
  says shallow is "similar to" grafts (a truncation, not a parent substitution)
  and says alternates "borrow" objects; it never says "resolve as local"
  (that phrase is the tool's, `tools/report-landing-audit.py:53`). O01 is
  declared open/reported-not-graded at `corpus/lessons/round-23.md:86-88`, so no
  graded claim depends on the stronger wording. Keep, but do not later cite the
  row for a graded "alternates are transparent" claim without the page's
  "borrow" language.
- **C4 — used-by under-lists.** `tools/report-landing-audit.py` and
  `tests/report-audit/repo-state-grid.py` rely on these semantics, and S089's
  row already lists the tool as used-by, so registry convention would add both.
  Under-listing, not a false citation; the listed path is real.

## Not verified

- I did not diff the 2.49.0/2.49.1 page body against the 2.56.0 claim; I relied
  on the page's own changes table ("2.49.1 → 2.56.0 no changes") plus local
  git 2.56.0, and did not open a version-pinned `/docs/gitrepository-layout/2.56.0`
  URL.
- I did not re-run the repo-state grid or selftest (source-row seat; no
  execution claim made here).
- I did not open git-replace(1) or git-clone(1) to test the "similar to
  info/grafts" analogy beyond the quoted page sentence.
- Build advice `SrcGitRepoLayout.md`'s local man-page cross-check was read,
  not re-executed.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/SrcS094.md`
  (this report).
- Transient outside the lane: `/tmp/r23-s094-page.html` (fetched page copy).
- No lane checkout files, tracked files, Git index, or jj state were modified.
  No tools installed or upgraded.
