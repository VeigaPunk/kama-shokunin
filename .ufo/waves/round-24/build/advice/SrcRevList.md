# SrcRevList — Git `git-rev-list` missing/object reporting (round 24)

Seat: KamaR23-2.SrcRevList-2 (leaf; no dispatch). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Accessed 2026-10-21. No production file, registry row, fixture or test was edited or run.
No tools installed or updated.

## Verdict

**NEW SCOPE on an already-used official source family — claim SUPPORTED with hard limits.**
`https://git-scm.com/docs/git-rev-list` at 2.56.0 documents that `--missing=print` continues the
traversal and prints encountered missing objects prefixed `?`, that `--missing=allow-any` omits
missing objects **silently**, and that `--objects` adds object IDs referenced by the listed commits
while `--no-object-names` suppresses names only. It does **not** document any numeric exit status,
does **not** promise a complete required-object closure, and does **not** define promisor
expectedness or lazy-fetch behaviour. Therefore r24's "missing required object evidence → exit 2"
and "promisor unknown citation → exit 2 unless locally found" remain **lane policy**, not this
page's claims. `corpus/SOURCES.md` was not edited; a candidate row is under `out/SrcRevList/`.

Axes (godspeed): A1 source identity/version exactness; A2 claim admissibility (what the page can and
cannot ground); A3 registry distinction (new scope vs reopened used row); A4 parse contract the
repair may rely on. Every observation below moves one of these without harming another.

## Observations (path:line / command)

| # | Observation | Evidence |
|---|---|---|
| 1 | Latest page fetched: HTTP 200, 254770 bytes, final URL unchanged | `curl -sS -D headers.txt -o rev-list.html https://git-scm.com/docs/git-rev-list`; server `Date: Wed, 21 Oct 2026 17:53:42 GMT` |
| 2 | Page is the rolling "latest" manual, currently 2.56.0 | `rev-list-2.56.0.html:1322` → `git-rev-list last updated in 2.56.0` |
| 3 | Version-pinned page exists and is text-identical | `https://git-scm.com/docs/git-rev-list/2.56.0` → 200, 254641 bytes; tag-stripped text: 3538 vs 3538 lines, `difflib` diff 0 lines |
| 4 | Local git matches the page | `git --version` → `git version 2.56.0`; `man git-rev-list \| col -b` lines 949–988 carry the same `--missing` text |
| 5 | All three options are under §Object Traversal | heading `#_object_traversal` at `rev-list-2.56.0.html:4516`; `--objects` dt `:4522`; `--no-object-names` dt `:4570`; `--missing=<missing-action>` dt `:4654` |
| 6 | Missing handling is declared a debug option | `rev-list-2.56.0.html:4656-4657`: `A debug option to help with future "partial clone" development.` |
| 7 | `-z` replaces the `?` marker with a `missing=yes` token | `rev-list-2.56.0.html:3825-3828`; `--missing-only` says the `?` prefix is "used by the non--z forms" (`:4712-4722`) |
| 8 | `--quiet` is the only documented exit-status consumer | `rev-list-2.56.0.html:3670-3676`: caller may "test the exit status to see if a range of objects is fully connected"; no numeric value stated |
| 9 | No prior rev-list row exists at base | `git show 0df800e8:corpus/SOURCES.md \| grep -c rev-list` → `0`; current file sha256 `274d50916eb04b158f4f2b2fbc0ffdfaec56270aeb54282d4f2d95d193744993` equals base |
| 10 | Host is already used, page is not | existing rows S032, S033, S070/S082, S071/S083, S073/S085, S089, S090, S093, S099, S100 cite `git-scm.com/docs`; none cites `git-rev-list` |
| 11 | Current audit tool does not call `rev-list` at all; it refuses promisor metadata outright | `tools/report-landing-audit.py:441-467` (`check_history_repo`: promisor pack, `remote.*.promisor`, `extensions.partialclone`); `grep -n 'rev-list\|--missing\|--objects' tools/report-landing-audit.py` → no match |

## Exact source identity

- URL (latest): `https://git-scm.com/docs/git-rev-list`
- URL (pinned): `https://git-scm.com/docs/git-rev-list/2.56.0`
- Version: **2.56.0** — page label `git-rev-list last updated in 2.56.0`
  (`rev-list-2.56.0.html:1322`); local `git --version` = `2.56.0`.
- Access date: **2026-10-21** (HTTP `Date: Wed, 21 Oct 2026 17:53:42 GMT`).
- sha256 latest `6eca09d9ef21dd4270ff2c73cac7ee26964aebc470f4dfc52705eb27749ce65f` (254770 B);
  pinned `2c9b7ed2177a70b69fa1c801f026ce2a2e6ece0a842f2055c98f44b7c405c7d4` (254641 B);
  tag-stripped text identical.

Anchors (in-page ids exactly as rendered):

| Option | Anchor id | Raw line (pinned copy) |
|---|---|---|
| `--objects` | `#Documentation/git-rev-list.txt---objects` | 4522 |
| `--no-object-names` | `#Documentation/git-rev-list.txt---no-object-names` | 4570 |
| `--missing=<missing-action>` | `#Documentation/git-rev-list.txt---missingmissing-action` | 4654 |

Quotes (whitespace-normalized, ≤25 words, pinned page lines in parentheses):

1. `--objects` (4524–4525, 12 words):
   > Print the object IDs of any object referenced by the listed commits.
2. `--no-object-names` (4572–4573, 16 words):
   > Only useful with --objects; does not print the names of the object IDs that are found.
3. `--missing=print` (4673–4674, 16 words):
   > The form --missing=print is like allow-any, but will also print a list of the missing objects.
4. Prefix (4674, 8 words):
   > Object IDs are prefixed with a “?” character.
5. `--missing=allow-any` (4664–4665, 9 words):
   > Missing objects will silently be omitted from the results.
6. Default (4659–4660, 16 words):
   > The form --missing=error requests that rev-list stop with an error if a missing object is encountered.
7. Missing tips (4705–4707, 22 words):
   > If some tips passed to the traversal are missing, they will be considered as missing too, and the traversal will ignore them.
8. Missing tip without an OID (4707, 14 words):
   > In case we cannot get their Object ID though, an error will be raised.
9. `-z` record (3828, syntax): `<OID> NUL missing=yes NUL [<token>=<value> NUL]...`
10. `--quiet` (3673–3675, 22 words):
    > is primarily meant to allow the caller to test the exit status to see if a range of objects is fully connected

## Which missing objects are reported, and what is silent

- **`--missing=print`** is "like allow-any" (traversal continues) **and** prints a list of the
  missing objects; in non-`-z` output the IDs carry a `?` prefix (Q3, Q4). The records go to the
  same output stream: `--missing-only` says it suppresses "all output for present objects and
  print[s] only the missing ones" (pinned 4712–4722).
- **`--missing=allow-any`** is the silent path (Q5): missing objects are omitted from results with
  no record. **`--missing=error`** is the default and stops with an error (Q6).
  **`--missing=allow-promisor`** continues only for "EXPECTED promisor missing objects"; unexpected
  ones raise an error.
- **Object coverage** is whatever the traversal encounters. With `--objects`, the printed set is
  "object IDs of any object referenced by the listed commits" (Q1) — a pack-negotiation framing
  ("all object IDs which I need to download"), not a repository census. Without `--objects`,
  rev-list prints commits, not trees/blobs.
- **`--no-object-names`** only removes the accompanying names ("This inverts `--object-names`");
  presentation only, and "Only useful with `--objects`" (Q2).
- **Missing tips** are a second, action-independent skip: they "will be considered as missing too,
  and the traversal will ignore them" (Q7), and only an OID that cannot be obtained raises an error
  (Q8). This applies even under `--missing=print`; the page does not say whether such a tip appears
  as a `?` record.
- **`-z`** changes the record shape: missing entries become `<OID> NUL missing=yes NUL ...` (Q9),
  and the `?` prefix is described as belonging to the non-`-z` forms (4712–4722).

## Claim-vs-source limits for the r24 repair

1. **No numeric exit status is documented anywhere on this page.** "Stop with an error" (Q6) and
   "an error will be raised" (Q8) name an outcome, not a code. `--quiet` (Q10) is the only place
   exit status is mentioned, and it still gives no value. **"Missing required object evidence is
   exit 2" is kama policy; it cannot be cited to this row.**
2. **No completeness guarantee.** "A list of the missing objects" is traversal-encountered only.
   The page never promises that every object in a required closure is enumerated, and a missing
   tree cannot be descended to discover its children. [INFERENCE, not page text.]
3. **`--objects` is not an audit closure contract.** It prints objects "referenced by the listed
   commits" (Q1) and is explicitly motivated by pack negotiation ("need to download"). Repository-
   wide or audit-required closure is own-work.
4. **`--missing=print` is not a failure signal by itself.** Because it is "like allow-any", the
   audit must treat every `?` record as its own exit-2 condition; the page supplies no
   process-status mapping for that case.
5. **Promisor policy is out of scope here.** "EXPECTED promisor missing objects" is undefined on
   this page, and lazy fetch is not discussed. S089 (`--no-lazy-fetch`) and S099 (partial-clone
   missing-object handling) own those claims; this row cannot alone justify either accepting or
   refusing a promisor repository.
6. **`--no-object-names` is presentation-only** and only useful with `--objects`; it does not alter
   which objects are walked or reported.
7. **`-z` parsing differs.** A parser keyed only on the `?` prefix will mis-read `-z` output, where
   the marker is `missing=yes` (Q9). Use one mode and test for it; do not mix.
8. **Unspecified details:** ordering and de-duplication of missing records, whether missing lines
   carry names when `--object-names` is active, and how `--missing=print` interacts with `--quiet`
   (which suppresses stdout). Do not encode these as documented facts.
9. **The option is explicitly a debug aid** for future partial-clone development (pinned
   4656–4657); stability beyond 2.56.0 is not promised.

## Registry distinction (reopened vs new)

- **Not a reopened row.** Base `corpus/SOURCES.md` contains zero `rev-list` occurrences
  (observation 9), so there is no row to reopen.
- **New scope inside an already-used family.** The publisher/host `git-scm.com/docs` is already
  used by S089 (git(1)), S090 (git-replace), S093 (git-log), S099 (partial-clone), S100
  (git-config), and the older manual rows S032/S033/S070/S071/S073/S082/S083/S085. This page adds
  the `rev-list` option semantics only and supersedes nothing.
- **Complementary rows:** S089 covers `--no-lazy-fetch` (invocation-level fetch suppression), S099
  covers promisor lazy fetch on missing-object lookup. Neither states what rev-list prints.

## Deliverable

- Candidate row: `out/SrcRevList/SOURCES-row-candidate.md` — provisional `S103` (S101 highest at
  base; S102 already drafted by peer `SrcPromisorCode`), status `queued`, not applied.
- Exact extract with anchors/lines/quotes: `out/SrcRevList/extract.txt`.
- Fetched pages and headers: `out/SrcRevList/rev-list.html`,
  `out/SrcRevList/rev-list-2.56.0.html`, `out/SrcRevList/headers.txt`.
- No production edit, no unified patch (registry must not be edited in this lane).

## Unrun / unresolved

No fixture or command was executed against a synthetic repository (lane bounds: no bounded fixture
measurement assigned). Therefore **unverified by observation**: whether missing blobs/trees under
`--objects` are enumerated, the process exit statuses for each `--missing` action, and whether a
missing tip is emitted as a `?` record. The page text does not settle these; if L1 needs behavioural
proof for the repair, assign a bounded local synthetic fixture measurement.
