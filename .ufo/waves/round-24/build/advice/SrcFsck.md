# SrcFsck — git-fsck docs vs absent promised objects

Scope: the page https://git-scm.com/docs/git-fsck as a source for (a) whether fsck regards absent
promised objects as valid and (b) whether fsck can serve as a local completeness oracle.
Read-only: no production file, registry, tool, test or config edited. No installs. No fixture run.

## Verdict

**The page cannot be cited for promisor validity.** It never mentions promisor remotes, promised
objects, partial clones, lazy fetching, or exit statuses — zero occurrences in the live HTML, in the
installed git 2.56.0 manual, and in `Documentation/git-fsck.adoc` at tag v2.56.0. It therefore
neither says fsck treats absent promised objects as valid nor that it reports them missing.

What the page *does* support is a narrower, defensible statement: the documented `missing`
diagnostic has no promisor exemption, fsck's default heads are index + refs + reflogs, and
`--connectivity-only` checks only that referenced objects exist (never blob contents). That is
enough for "the manual does not define fsck as a completeness certificate", but not for the
promisor-specific behavior.

The actual v2.56.0 behavior — fsck skips missing objects that `is_promisor_object()` reports and
disables lazy fetch — is **implementation only** (`builtin/fsck.c:884-885` plus the
`is_promisor_object` guards). If L1 needs that claim, it requires a code row (new scope), not this
docs row. Citing git-fsck docs for it would be a mis-citation.

For C1: do not let a clean `git fsck` upgrade missing evidence to present. Docs supply no promisor
contract; code exempts precisely the promised absences. "Missing required object evidence is exit 2"
remains lane policy — the page documents no exit-code mapping at all.

## Source identity

| field | value |
|---|---|
| URL | https://git-scm.com/docs/git-fsck |
| Title | "Git - git-fsck Documentation" |
| Version banner | "git-fsck last updated in 2.53.0"; version list "2.54.0 → 2.56.0 no changes"; 2.53.0 dated 2026-02-02 |
| Versioned URL | https://git-scm.com/docs/git-fsck/2.56.0 serves an HTML redirect with canonical https://git-scm.com/docs/git-fsck/2.53.0 (no separate 2.56.0 rendering) |
| Host manual | `git version 2.56.0`, `/usr/share/man/man1/git-fsck.1.gz` — matches every quoted sentence |
| Opened | 2026-10-21 |
| Retrieval | `curl -sS -o git-fsck-2560.html https://git-scm.com/docs/git-fsck` → HTTP 200, 95083 bytes, sha256 `ba958ce198bb3ee15550c138fe9b55183b004d1b1246b40b9eaadfd76e59ffd8` |

## Exact quotes (all ≤25 words)

Primary — §EXTRACTED DIAGNOSTICS, `missing <type> <object>`
anchor `#Documentation/git-fsck.txt-missinglttypegtltobjectgt` (section `#_extracted_diagnostics`);
man lines 255–257; adoc lines 150–152:

> "The <type> object <object>, is referred to but isn't present in the database." — 13 words

The rendered HTML inserts a space before the comma because of the `<object>` markup; the man/adoc
form above is the one to quote.

Secondary, same page:

- §OPTIONS `--connectivity-only` (man line 98; adoc lines 66–68): "Check only the connectivity of reachable objects, making sure that any objects referenced by a reachable tag, commit, or tree are present." — 22 words.
- §OPTIONS `--connectivity-only` next sentence (man line 98; adoc line 71): "Corruption in blob objects will not be detected at all." — 10 words.
- §OPTIONS `<object>` default heads (man lines 52–53; adoc lines 26–27): "defaults to using the index file, all SHA-1 references in the refs namespace, and all reflogs" — 16 words.
- §DISCUSSION (man line 243; adoc lines 126–127): "It prints out any corruption it finds (missing or bad objects)" — 11 words.
- §DESCRIPTION (man line 43; adoc line 19): "Verifies the connectivity and validity of the objects in the database." — 11 words.

## Claim-vs-source limits

1. **Promisor silence is total.** Case-insensitive counts in the fetched HTML: `promisor` 0,
   `promise` 0, `partial clone` 0, `partialclone` 0, `exit status` 0, `network` 0. The 9 `fetch`
   hits are `fsck.<msg-id>` / `fetch.fsck.<msg-id>` configuration prose and site navigation; the 2
   `remote` hits are navigation. Installed 2.56.0 man page: 0 promisor/promise/partial-clone hits.
   `Documentation/git-fsck.adoc` at v2.56.0: no match. So:
   - docs cannot prove "promised absence is valid";
   - docs cannot prove "fsck would report a promised-absent object as `missing`" as runtime fact;
   - docs cannot prove fsck avoids or performs any network access.
2. **The documented `missing` rule is unconditional on its face.** The manual defines `missing` as
   "referred to but isn't present in the database" and states no exemption. Runtime diverges: the
   v2.56.0 code skips `is_promisor_object()` OIDs before printing the diagnostic
   (`builtin/fsck.c:143-149, 253-258, 469-472, 534-540`; `fsck.c:1337-1340`). Quote the manual only
   about what the manual says; do not present it as observed behavior.
3. **Documented scope is not general completeness.** Default heads are the index, all refs and all
   reflogs (quote above); objects reachable only from an arbitrary cited commit are not traced
   unless that commit is passed as a `<object>` argument. `--connectivity-only` avoids reading
   blobs, so blob corruption is invisible in that mode.
4. **No exit-status contract on the page.** `exit status` has 0 occurrences; there is no
   EXIT STATUS section. Any mapping from fsck results to exit codes is policy or probe measurement,
   not this source. (Round-23 probes observed rc=1/3 — own-work, not re-run here.)
5. **Configurable suppression exists but is narrow.** `fsck.skipList` ignores listed
   known-broken (non-fatal) objects; `fsck.<msg-id>` can switch error/warn/ignore. Do not stretch
   this to "missing promised objects can be ignored" — that mechanism is the code exemption in (2),
   not `skipList`.

## Implementation context (code, not this row; static reading only)

At tag v2.56.0 (host version), unexecuted:

- `builtin/fsck.c:884-885` — `/* fsck knows how to handle missing promisor objects */` then
  `repo->fetch_if_missing = 0;` (no lazy fetch during fsck).
- `builtin/fsck.c:143-149` — reachability walk returns without recursing for promisor objects.
- `builtin/fsck.c:253-258` — `check_reachable_object` returns before the `missing` printf for promisor objects.
- `builtin/fsck.c:469-472`, `534-540` — promisor-absent reflog/ref entries are not errors.
- `fsck.c:1337-1340` — unreadable blobs are skipped when `is_promisor_object()`.
- `packfile.c:2061-2078` — `is_promisor_object` seeds its set only when
  `repo_has_promisor_remote(r)`, via `ODB_FOR_EACH_OBJECT_PROMISOR_ONLY`; `packfile.c:748-750`
  sets `pack_promisor` from the `<pack>.promisor` marker; `add_promisor_object` (2006-2030) also
  adds objects referenced from promisor trees/commits/tags.
  [INFERENCE: a promised missing blob is therefore exempt; the walk was read, not executed.]

Consequence for C1: fsck's silence on an object inside a promisor pack is not evidence of local
presence. That conclusion is code-anchored; a docs row cannot carry it.

## Existing SOURCES check — new scope, not a reopened used source

- `corpus/SOURCES.md`: 101 rows (S001–S101); `grep -c 'fsck'` → **0**. No row cites
  https://git-scm.com/docs/git-fsck, and no row's `teaches` text mentions fsck.
- `registry/` (all files): `grep -rn 'fsck'` → no match.
- `tools/report-landing-audit.py` and `tests/report-audit/*.py`: `grep -n 'fsck'` → no match, so the
  page was never a tool source.
- Round-23 used `git fsck` only as a probe command, not as a citation:
  `.ufo/waves/round-23/falsify/advice/RowF26HugeAuthor.md:105`,
  `RowF04ReplaceFabricated.md:142`, `RevSourcesBlob.md:53`. No `used-by` or `status` cell changes.
- Therefore: **new scope**. No recheck date or supersession applies; nothing depends on this page
  today. Provisional id: **S103** (S102 is proposed by SrcPromisorCode for `promisor-remote.c`);
  the integrator assigns the final id.

## Candidate row (registry NOT edited)

| S103 | Git git-fsck manual — https://git-scm.com/docs/git-fsck | docs | A | what `git fsck` documents about referenced-but-absent objects, default heads and `--connectivity-only` presence checking; not promisor-remote behavior, exit statuses or audit policy | §EXTRACTED DIAGNOSTICS `missing <type> <object>` (rendered anchor `#Documentation/git-fsck.txt-missinglttypegtltobjectgt`) and OPTIONS `--connectivity-only`, `<object>`; page "Git - git-fsck Documentation", "git-fsck last updated in 2.53.0", 2.54.0→2.56.0 "no changes" (2.53.0 dated 2026-02-02), installed git 2.56.0 man page matches; opened 2026-10-21 | A referenced-but-absent object is `missing` with no stated promisor exemption; with `--connectivity-only` referenced objects must exist but blob contents are never read. | queued | 2026-10-21 | on-release | — |

Gate:
- URL https://git-scm.com/docs/git-fsck; access date 2026-10-21; version/title as above.
- Quote (13 words, §EXTRACTED DIAGNOSTICS; man 255–257): "The <type> object <object>, is referred to but isn't present in the database."
- Second quote (22 words, §OPTIONS `--connectivity-only`; man 98): "Check only the connectivity of reachable objects, making sure that any objects referenced by a reachable tag, commit, or tree are present."
- Scope limit: page has 0 promisor/promise/partial-clone mentions. Do **not** attach the
  promisor-exemption claim to this row.
- Status `queued` (no path or knowledge entry cites it yet). If admitted, `used-by` stays `—`;
  it becomes `mined` only when a lesson/knowledge/tool path cites it.

## Recommendation to L1

- If the round needs a docs anchor for "the manual defines a referenced-but-absent object as
  `missing` and states no promisor exemption; `--connectivity-only` is presence-only", admit the
  row above.
- If the round needs "fsck regards absent promised objects as valid / is not a local completeness
  oracle in promisor repositories", **do not cite this page** — open a code row at
  `git.git v2.56.0 builtin/fsck.c:884` with the guard lines, or leave the claim as [INFERENCE].
- Either way, keep required-object availability checks on `cat-file` batch records (S083) and keep
  missing evidence at exit 2; fsck must not be promoted to a completeness oracle.

Adjacent lead, not drafted here (owned by SrcRevList): https://git-scm.com/docs/git-rev-list
exposes `--missing=allow-promisor` and `--exclude-promisor-objects` option names in its OPTIONS
section; no quote or row is claimed in this report.

## Files

- `.ufo/waves/round-24/build/out/SrcFsck/git-fsck-2560.html` — fetched page, sha256 `ba958ce198bb3ee15550c138fe9b55183b004d1b1246b40b9eaadfd76e59ffd8`
- `.ufo/waves/round-24/build/out/SrcFsck/git-fsck.adoc` — v2.56.0 manual source, sha256 `5c700052d0f87d879c655cce7e0769af1ded831c37368e86aa71e71f6e470ad8`
- `.ufo/waves/round-24/build/out/SrcFsck/git-fsck-2.56.0.man.txt` — installed 2.56.0 man text, sha256 `05fffabbc3087fae8e937f6bb720175e736342adbe0b19960509baa8240b514c`
- `.ufo/waves/round-24/build/out/SrcFsck/fsck-builtin.c` (sha256 `d25f3b1a…cae5a9ca35`), `fsck.c` (`c871ede1…b7bc51d9`), `packfile.c` (`021b1b9b…8b94032`) — code context
- `.ufo/waves/round-24/build/out/SrcFsck/quotes.txt`, `evidence.md`

## Unrun / unverified

- No fixture, no `git fsck` invocation, no exit code measured in this lane; the code behavior in
  §Implementation context is static reading only.
- No build, tests or formatter runs (not assigned).
- `is_promisor_object` internals beyond the cited lines (e.g. exact `ODB_FOR_EACH_OBJECT_PROMISOR_ONLY`
  filter implementation) were not read; the pack-marker reading is [INFERENCE] from
  `packfile.c:748-750`.
