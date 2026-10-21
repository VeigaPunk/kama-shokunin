VERDICT: **reopened, already-used source** — the URL is already registered and mined by S033 and S083 (S071 superseded). The assigned “batch missing” angle is S083's scope, and the only defect found there is its “absence” gloss. “Partial clone behavior” and “wrong type” are not in this manual at all: both are documented absences, not new positive scope. No registry edit was made.

# SrcCatFile — git-cat-file manual, batch missing / wrong type / partial clone (round 24)

## 1. Source identity and access

| item | observation |
|---|---|
| URL opened | https://git-scm.com/docs/git-cat-file |
| Versioned reopen | https://git-scm.com/docs/git-cat-file/2.56.0 |
| Page version label | “git-cat-file last updated in 2.56.0”; version menu entry 2.56.0 dated **2026-09-28** |
| Access date | **2026-10-21** |
| Installed git | `git version 2.56.0` |
| Installed man page | `/usr/share/man/man1/git-cat-file.1.gz`, footer “Git 2.56.0 … 2026-09-27”; its missing and `<type>` paragraphs match the web text |
| Live vs versioned rendering | extracted visible text **equal** (`True`, 14,847 chars each); the two HTML byte streams differ (live `sha256 53983042…`, versioned `sha256 447057e9…`), but their manual text is identical |

Anchor ids confirmed on both live and 2.56.0 pages: `#_options`, `#_output`,
`#_batch_output`, `#Documentation/git-cat-file.txt---batch-check`,
`#Documentation/git-cat-file.txt-lttypegt`, `#Documentation/git-cat-file.txt--e`.
Rendered-line numbers below are from `out/SrcCatFile/catfile-2.56.0.txt`
(`sha256 01415f1d…`), which begins at `NAME`; anchors are the stable citation.

## 2. Exact quotes (all ≤25 words)

| # | Anchor | Rendered lines | Words | Quote |
|---|---|---|---|---|
| Q1 | `#_batch_output`, missing paragraph | 267-269 | 17 | “If a name is specified on stdin that cannot be resolved to an object in the repository” |
| Q2 | `#Documentation/git-cat-file.txt-lttypegt` | 38-44 | 16 | “asking for a type that can trivially be dereferenced from the given `<object>` is also permitted.” |
| Q3 | `#Documentation/git-cat-file.txt---batch-check` | 94-98 | 9 | “Print object information for each object provided on stdin.” |
| Q4 | `#_batch_output`, intro | 213-217 | 15 | “the whole line is considered as an object, as if it were fed to git-rev-parse[1].” |
| Q5 | `--batch-command`, `remote-object-info` | 223-224 | 10 | “prints object info from the remote without downloading the objects.” |
| Q6 | `#Documentation/git-cat-file.txt--e` | 32-35 | 17 | “If `<object>` is of an invalid format, exit with non-zero status and emit an error on stderr.” |
| Q7 | `#_batch_output`, ambiguous paragraph | 273-274 | 17 | “If a name is specified that might refer to more than one object (an ambiguous short sha)” |
| Q8 | gitrevisions `^{<type>}` | gitrevisions lines 583-589 | 4 | “in which case, barf” (cross-page; not a cat-file claim) |

Q1's record is literally `<object> SP missing LF` (line 269). A **second** `missing LF`
occurs at line 289 under `--follow-symlinks` (“the initial symlink requested does not
exist”); it is not the stdin batch record and must not be used as its anchor.

## 3. Claim-vs-source matrix for the round-24 C1 questions

| Claim the lane might make | Source status | Basis / limit |
|---|---|---|
| `--batch-check` prints `missing` when a stdin name cannot be resolved | **Supported** | Q1. This is all S083 needed and all it may say. |
| `missing` proves the object is absent from the repository | **Not supported** | Q1 says “cannot be resolved … in the repository” at that invocation. The page never states absence, completeness, or that resolution excludes promisor remotes. S099 (`partial-clone` §Handling Missing Objects) supplies the fetch mechanism; S089 supplies `--no-lazy-fetch`. |
| `missing` distinguishes absence from a *wrong-type* citation | **Not documented** | The page has one missing paragraph (BATCH OUTPUT) and one follow-symlinks missing record; no type-mismatch record. `<type>` (Q2) is the non-batch type argument and only permits “trivially dereferenced” types. Peel failure is described only by gitrevisions (Q8), and no page maps it to batch `missing`. |
| A wrong-type object yields a documented exit status | **Not documented** | The only documented non-zero exit is Q6, and it is for an invalid-format object under `-e`, not a type mismatch. Batch mode documents records, not statuses. |
| Batch input may carry `^{commit}` | **Supported** | Q4: the whole line is fed to rev-parse semantics. Whether a failed peel becomes `missing` is behavior, not a quote. |
| In a promisor repo cat-file lazy-fetches a missing object | **Absent from this page** | Rendered text contains **zero** occurrences of `promisor`, `partial clone`, `lazy` or `fetch` (counts run on both the live and 2.56.0 renderings). Positive authority is S099; the only remote text here is Q5. |
| `remote-object-info` queries a remote without downloading | **Supported** | Q5, an explicit command, not implicit lazy fetch. |
| `--batch-all-objects` covers alternate object stores | **Supported, no promisor statement** | Lines 140-147: “all objects in the repository and any alternate object stores (not just reachable objects)”. |
| `--batch-check` exit status separates git failure from `missing` | **Policy, not this page** | The page documents no batch exit status. S083 itself already labels the status distinction own-work; keep that label. |
| `%(objecttype)` exposes the resolved object's type | **Supported** | `#_batch_output` atom list, lines 231-232. This gives the caller a documented way to see a wrong-type resolution without a peel. |

## 4. Existing SOURCES rows: reopened vs new scope

| Row | URL/anchor | Status | Relation to this assignment |
|---|---|---|---|
| **S033** | same URL, §OUTPUT raw `<type>` clause, OPTIONS `<type>`/`--textconv`/`--filters` | mined (used by `corpus/lessons/round-13.md`) | Unaffected. Reopening confirms Q raw-output line 211-212 and Q2 text are unchanged. |
| **S071** | same URL, batch missing/ambiguous | mined, **superseded by S083** | Do not resurrect. |
| **S083** | same URL, BATCH OUTPUT missing/ambiguous | mined (used by `corpus/lessons/round-22.md`) | Same anchor and quote are accurate; its teaches-cell phrase “so absence, ambiguity and a git failure are separable” is the overreach: the page says unresolved, not absent. |
| **S099** | `partial-clone` §Handling Missing Objects | mined (used by `corpus/lessons/round-23.md`) | The authority for promisor lazy fetch; the cat-file page must not be cited for it. |
| **S089 / S090** | git(1) global options / git-replace | mined | `--no-lazy-fetch` / `--no-replace-objects` isolation; untouched. |

**Conclusion:** this is a reopened used source, not new scope. The batch-missing claim is
already registered. The two assigned negatives (page is silent on promisor/partial clone;
page is silent on type-mismatch outcomes) are *limits*, not positive claims; no row is
needed merely to record silence.

One row would be justified only if L1 wants S083's “absence” gloss corrected under the
lane's append-only supersession pattern. Candidate (not applied) at
`out/SrcCatFile/SOURCES-candidate-row.md`, provisional **S103** because SrcPromisorCode
already drafts S102: same URL, exact Q1 quote, scope narrowed to “unresolved at this
invocation”, noting the promisor and type-mismatch silences and the follow-symlinks
second `missing` record. Status `queued`; flip to `mined` only when a committed lesson
cites it. If L1 prefers prose correction, keep S083 and put the limit in the lesson.

## 5. What this licenses for C1 (advisory only, no production edit)

- **Complete promisor-marked clone with all required objects local:** `cat-file
  --batch-check` resolves them and prints oid/type/size; Q1 never fires. This page gives
  no basis to refuse the repository. Metadata alone is not an unresolved object.
- **Genuine omitted required commit:** with `--no-lazy-fetch` (S089, not this page),
  the name prints `missing` (Q1). That is “unresolved here”, not “never existed”; when
  promisor metadata is present, the only defensible classification is
  could-not-evaluate (exit 2), never a clean/failed or landed-omitted guess.
- **Unknown citation in a promisor-backed repository:** `missing` in the lane and fleet is
  per-invocation unresolved, so it cannot establish global absence. The page supports only
  that weaker reading; the exit-2 rule and the cross-repo `found` fallback are audit
  policy, not source claims.
- **Wrong-type citation:** the bare lookup can legitimately print `found` with
  `%(objecttype)` = blob/tree; the `^{commit}` peel can instead print `missing`. Neither
  output means “absent”. This page documents no type-mismatch error, so any exit-2
  classification for wrong type is policy plus observed exit status, not a source claim.
  If the audit wants type evidence, the `%(objecttype)` atom (line 231-232) is the
  documented field; whether to use it is L1's call.

## 6. Evidence, commands, limits

- Opened live and versioned pages; extracted visible text with Python `html.parser`;
  compared live vs 2.56.0 (`equal: True`, 14,847 chars).
- Keyword count over rendered text: `promisor` 0, `partial` 0, `lazy` 0, `fetch` 0;
  `alternate` 1 (line 143), `missing LF` 2 (lines 269, 289), `ambiguous LF` 1
  (line 274), `invalid format` 1 (line 34).
- Local corroboration: `git --version` → 2.56.0; `git cat-file -h` shows the same batch
  option family and **no** missing-policy option; `man git-cat-file` footer
  “Git 2.56.0 2026-09-27” and matching Q1/Q2 paragraphs.
- Cross-page check only: gitrevisions `^{<type>}` says “in which case, barf” (Q8); no
  cat-file mapping from peel failure to `missing`.
- Prior local observations cited, not rerun: round-21 `SrcGitCatFile.md` probe F2
  (`cat-file -e tree^{commit}` rc 128, `blob^{commit}` rc 128; bare `-e tree` rc 0) and
  its F1 (`-e` on missing full 40-hex rc 1, silent). Those are behavior, not this page.
- **Unrun:** no fixture, grid, selftest, build, lint or formatter. No git transport, no
  network beyond plain HTTPS fetches of official git-scm documentation. No installs or
  upgrades. No registry, tool or lesson edit; only this report and
  `out/SrcCatFile/{catfile-live.html,catfile-2.56.0.html,catfile-2.56.0.txt,git-cat-file.man.txt,SOURCES-candidate-row.md}`.
- Evidence digests: live HTML `53983042…8c8c73`; versioned HTML `447057e9…bf7572`;
  rendered text `01415f1d…58a458a1`; man text `0a45c68b…f7d8a2`.
