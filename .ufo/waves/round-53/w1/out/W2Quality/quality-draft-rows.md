> **Status at filing:** superseded by the rows already in the lane's working tree. The lane's
> uncommitted `corpus/QUALITY.md` (sha256 `ed46d4b4…7eb94`) carries a round-53 section with
> `KQ94`-`KQ96` for the same three criteria; this file keeps the seat's independently drafted
> text and its checks for comparison and for renumbering if those rows are re-landed. See
> `quality.md` for the review of the in-tree rows and the proposed corrections.

# QUALITY.md rows — round 53, seat W2Quality (draft, not landed)

Status: draft for the kama L1 to append to `corpus/QUALITY.md`. The file is A-corr (corrections
are appended rows; `registry/append-only-contract.tsv`), so nothing below rewrites or moves an
existing line. Proposed append point: end of file, after the landed round-52 table
(`corpus/QUALITY.md:456-466`; the last row is `KQ93`) — the same point round 52 used.

Numbering: the next free id at drafting time is `KQ94`, so the three rows read `KQ94`-`KQ96`.
Round 52's W2Quality drafted `KQ94`-`KQ103` and none of them landed
(`.ufo/waves/round-52/w1/out/W2Quality/rows.md:28`: "next free id … If integration lands other
rows first, renumber in landing order"). If the L1 lands a sibling seat's rows first, renumber in
landing order: the row text, not the number, is the criterion.

Provenance: every `Check:` below was run by **this seat** at the build
`c22602bd8d83ab26349d1087e916ca537ee4f9d1`, on a `git clone --shared` of the lane. Receipts in
this directory: `c1-build.out` (my run of the C1 counter), `c2-build.out` (my run of the C2
counter), `anchor-round53.out` and `anchor-controls.out` (my runs of `sources-anchor-check.py`), and
the L1's own `measured-c1-build.out` / `measured-c2-build.out` copied beside them. Line pointers
into `tools/` name the **build commit** — read them as `git show c22602bd:<path>`; the lane's
working tree carries uncommitted round-53 edits, so a pointer read from the working tree is not
this criterion's evidence.

---

## Proposed append (exact text, from the blank line above the heading)

```markdown

## Criteria added — round 53 (each cites `corpus/lessons/round-53.md`)

Same columns as the tables above; appended after the round-52 rows so no existing line moves.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ94 | A replay's server runs the release archive's own code only when **every** executable file mapping of the running server — the `/proc/<pid>/maps` rows with `x` in the permission field and a pathname that is not `/memfd:` — is either an archive member under the replay's unpacked tree whose mapped range, read from `/proc/<pid>/mem` at the maps address and compared with the member's bytes at the mapping's file offset (S506; `tools/round53-replay-code-audit.py:405`, `:424-433`), is byte-equal to the counter's **own** download of the release, or a host file that is root-owned, carries the mapped inode and is not writable by the counter (`:447`), with `libllama-server-impl.so`, `libggml-base.so*`, `libggml.so*` and `libggml-cpu-*.so` among the compared members (`:103`, `:456-459`), and with the receipt's `code_mappings` — path, dev, inode and the sha256 of the file opened at that path only while `fstat()` shows the mapped inode, a `(deleted)` pathname never opened (`tools/kama-llamacpp-live.py:774-838`, written at `:2309`) — and the replay's `own_code` (member digests hashed from the archive stream, `tools/kama-live-replay.py:290-303`, `:305-338`, `:521-522`) naming the same members with the same digests; `code=1` requires all three runs, and the counter must be the server's ancestor (S507) | a launcher-image digest or a library's bytes at a path accepted as the code that runs (round-52 closure R2: `libllama-server-impl.so` and `libggml*` load by path — the base control fails all 8 members per run with `own_code 'None'` and no `code_mappings` entry); a mapping hashed without the inode/dev check, a `(deleted)` pathname opened, a member claim without a digest (`code-mapping:digest`, `:329`), a non-root mapping outside the tree (`:333`), a server mapping no archive library (`:337`), or a mapping of one path from two files. Limits: bytes are compared, not provenance, so a replay fed the host's byte-identical install still meets; host libraries (libc, libstdc++, libssl) are only classed root-owned and unwritable, their bytes compared with nothing; read-only and writable data mappings and the model mapping are not byte-compared; memory is read once while the server is held, so a library rewritten after that read is unseen; the bytes of a mapping past the member's end are expected to be zeros (`:425`), so the page padding of a short segment is compared as zero fill; a host at Yama `ptrace_scope` 2 or 3 offers no ancestor exception, so this leg cannot run there (S507) | `corpus/lessons/round-53.md` Claims C1 and Gate S506-S508; `corpus/lessons/round-52-verifier-spotcheck.md` R2; SCORECARD §Planned (round 53) item 1 |
| KQ95 | A self-assessment citation counts as evidence only when the path it names resolves in the tree its surface names, or its miss is disclosed by a row of `registry/cited-path-corrections.tsv` whose class the counter **re-derives** from git history — `deleted <commit>` (present at `<commit>^`, absent at it), `never` (never a path in any commit), `moved <path>` (blob equal to the token's at the last commit holding it), `eof <commit>` (the file was at least that long), `untracked` (on disk under the fleet root), `upstream <pinned raw URL>` (answers 200), `fixed <replacement>` (still cited and resolving) — for a citation set and parser frozen before the data: backtick spans outside ``` fences, a trailing `:N`/`:N-M`/`:N,M` anchor cut and checked against the line count only, `{a,b}` expanded, globs and directories matched, lane roots then fleet roots (`tools/round53-cited-path-check.py:28-37`, `:41-58`, `:107`); with `undisclosed=0`, `bad=0`, `stale=0` and no SCORECARD.md citation dropped since the base (`:59-73`) | a ledger row the counter cannot re-derive (`bad`: a forged `deleted` or `never`); a row whose token resolves at the tip (`stale`); a fenced restored block read as a standing citation; a dropped SCORECARD.md citation called a correction; a correction made in place in an append-only surface. Limits: resolution is **existence, not content** — the counter does not check that the cited file says what the citing sentence claims, nor that `:N` points at the right line, only that the file is at least that long (`:35-38`), so a citation whose path resolves and whose sentence is false still passes; LOG.md, lessons, `corpus/README.md` and knowledge entries are out of scope | `corpus/lessons/round-53.md` Claims C2; `corpus/lessons/round-52.md` Mistakes #4; seat W3Mistakes' prototype `.ufo/waves/round-52/w1/out/W3Mistakes/cited-path-exists.py`; SCORECARD §Planned (round 53) item 2 |
| KQ96 | A `corpus/SOURCES.md` row's line-number anchor is admitted only after the quote or symbol it names is **located at those lines in the copy fetched now**: `` `SYM` from line N `` → the first line of the fetched copy containing SYM is N; `` `SYM` lines A–B `` → the first line containing SYM lies in [A, B] (a body span, not a token on every line); `line N` in a cell that says quote/quoted → the row's quote (the first double-quoted span of `teaches`, at least 8 characters) occurs on line N — and a committed text copy the round relies on is byte-equal by sha256 to that fetch; a row whose anchor names no line number (`§SECTION`) or uses a form outside this grammar reads `n/a` with its reason, never a pass | an anchor copied from another row or an earlier lesson and never located (S505 `` `ggml_backend_load_best`, lines 422–439 ``: the symbol first occurs at 480 and the quote at 491; the round-52 lesson's `line 431`; the quote's "21 words" when it has 7 — round-52 closure R1); a committed copy accepted as the fetch without comparing digests; a range re-written in place instead of a correction row (S509 supersedes S505). Limits: the check locates text, not meaning; three anchor forms only; a row whose source is a lane-local file at a commit has no fetchable URL and reads `n/a` | `corpus/lessons/round-52-verifier-spotcheck.md` R1; `corpus/lessons/round-53.md` Gate S509 |

Drafted by wave-1 scribe W2Quality (`.ufo/waves/round-53/w1/out/W2Quality/`), round 53. KQ94
carries round-52 closure R2's library-by-path gap into a byte comparison with the archive, and
supplements KQ85/KQ91 (which bind the launcher image, not the libraries); KQ95 gives round-52
Mistakes #4 and seat W3Mistakes' 51 unexamined `.ufo/` misses a counter and a re-derived ledger;
KQ96 carries the round-52 outside closure's R1 into SOURCES admission (S505/S509).
```

---

## Checks (run by this seat at `c22602bd8d83ab26349d1087e916ca537ee4f9d1`)

Scratch clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; every
counter reads git objects at `--tip`, never the working tree.

**KQ94 — the memory comparison is real and the base control fails it.**
`python3 tools/round53-replay-code-audit.py --repo $S/lane --tip c22602bd… --scratch $S/c1` →
exit 0, `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`;
each of b1-b3: `code b? : 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to
the counter's own archive, 13 root-owned host files; recorded in code_mappings and own_code:
['libggml-base.so.0.27.0', 'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0',
'llama-common.so.0.7.0', 'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']`
(`c1-build.out`; the L1's `measured-c1-build.out` reads the same numbers).
Base control `.ufo/waves/round-53/controls/base.c1.out`: `code=0 coderuns=0/3`, with per run
`code: replay own_code 'None' is not verified with members` and eight
`code: rerun code_mappings has no entry <tree>/llama-b11909/<lib> …` — i.e. the rule fails exactly
the population the claim adds.

**KQ95 — the ledger classes are re-derived, and the base leaves 16 undisclosed.**
`python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd… --scratch $S/c2` →
exit 0, `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0
stale=0 dropped=0 met=True` (`c2-build.out`; the L1's `measured-c2-build.out` matches it leg for
leg and detail line for detail line, differing only in the echoed command line, its `fleet=` rev
(`ee9f7341` vs my `d2a6c59a` — the fleet repo moved, the verdict did not) and the trailer `exit=`).
Base control `.ufo/waves/round-53/controls/base.c2.out`: `lane=0 cited=679 unresolved=16
disclosed=0 undisclosed=16`, each named (`SKILL.md` 6, `SCORECARD.md` 10).
The build's `registry/cited-path-corrections.tsv` has 15 rows: 7 `never`, 1 `deleted`, 1
`untracked`, 5 `upstream`, 1 `fixed` (`SCORECARD.md` 10, `SKILL.md` 5); the 14 rows whose class
is not `fixed` cover the 14 unresolved citations (the round-40 `{base,after}` row covers two
tokens), every one re-derived by the counter, `bad=0 stale=0`, and `SKILL.md:113`'s
`scripts/local-helper.mjs` was corrected in place with no row (an absolute path is not a lane
citation).

**KQ96 — the anchor rule admits S509 and rejects S505.**
`sources-anchor-check.py --sources <SOURCES.md at c22602bd> --row S506 --row S507 --row S508
--row S509 --copy S509=.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` → exit 0,
`rows=4 anchors=4 ok=4 fail=0 na=3 covered_copy=1 copy_mismatch=0 met=True`
(`anchor-round53.out`): S509's four anchors located at 401 / 480 / 488-489 / 491 in the fetched
copy (sha256 `1436b46b…7fe`, equal to the committed copy), S506-S508 `n/a` (no line number).
Controls (`anchor-controls.out`, exit 1): S505 `lines 422–439` → `fail`, `got=[480, 578, 579]`;
S101 (`read_graft_line`, `lines 249-260`) → `ok`, first occurrence 249 — a row this seat did not
write, admitted by the same rule; S106/S140 → `n/a reason=form-not-in-grammar` (their anchors use
`path line N (declaration X)` and a lane-local file, forms the check does not read and therefore
never passes).

## Integration notes for the L1

- Append after `corpus/QUALITY.md:466` (`KQ93`); no existing line moves, so `tools/append-only-audit.py`
  sees an addition only.
- `corpus/QUALITY.md` is A-corr: if a row here is later narrowed, narrow it by an appended
  `(narrows KQnn)` row, not in place (KQ92's rule).
- The three rows name only tools and lessons that exist at `c22602bd`; the round-53 instrument
  registry entry in `SKILL.md` should name `tools/round53-replay-code-audit.py` and
  `tools/round53-cited-path-check.py` if KQ94/KQ95 land, and `sources-anchor-check.py` is a draft
  instrument in this directory only if KQ96 lands with it — it is not a lane tool.
