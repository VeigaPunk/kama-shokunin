# Evidence — git-fsck page, promisor-remote silence

Access date 2026-10-21. No installs, no package updates, no repository mutation.
Fetches were plain official HTTPS GETs (git-scm.com docs, raw.githubusercontent.com git.git tag v2.56.0).
Scratch: /fast/scratch/hyaku/kama-r24/SrcFsck/.

## Retrieval provenance

    curl -sS -o git-fsck-2560.html -w '%{http_code} %{url_effective}\n' https://git-scm.com/docs/git-fsck
      -> 200 https://git-scm.com/docs/git-fsck ; 95083 bytes
      sha256 ba958ce198bb3ee15550c138fe9b55183b004d1b1246b40b9eaadfd76e59ffd8

    curl -sS -o git-fsck.adoc -w '%{http_code}\n' \
      https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-fsck.adoc
      -> 200 ; 6134 bytes ; 189 lines
      sha256 5c700052d0f87d879c655cce7e0769af1ded831c37368e86aa71e71f6e470ad8

    zcat /usr/share/man/man1/git-fsck.1.gz | col -b > git-fsck-2.56.0.man.txt
      host: git version 2.56.0 ; man file /usr/share/man/man1/git-fsck.1.gz
      sha256 05fffabbc3087fae8e937f6bb720175e736342adbe0b19960509baa8240b514c

    curl -sS https://git-scm.com/docs/git-fsck/2.56.0
      -> HTML redirect page: <meta name="canonical" content="https://git-scm.com/docs/git-fsck/2.53.0">
         ("Redirecting…"), i.e. no separate 2.56.0 rendering.

    Code context (static reading only, not executed):
    curl -sS -o fsck-builtin.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c  -> 200
      sha256 d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35
    curl -sS -o fsck.c https://raw.githubusercontent.com/git/git/v2.56.0/fsck.c  -> 200
      sha256 c871ede138dd7f7942627c1750cf1ed3f53857c644bf073a6a4bc291b7bc51d9
    curl -sS -o packfile.c https://raw.githubusercontent.com/git/git/v2.56.0/packfile.c  -> 200
      sha256 021b1b9b25551070a3a1f986d1972ef93ef9695c3ff4f60eeb0a9a0798b94032

## Version identity

- Page title "Git - git-fsck Documentation"; banner "git-fsck last updated in 2.53.0";
  version list: "2.54.0 → 2.56.0 no changes", "2.52.0 ... 2025-11-17", "2.53.0 ... 2026-02-02".
- Installed manual is git 2.56.0 and matches the 2.53.0 rendering at every quoted sentence below
  (man lines 43, 52-53, 98, 243, 255-257).

## Promisor-silence checks

    python3: len(re.findall('promisor', html, re.I)) == 0
             len(re.findall('promise', html, re.I)) == 0
             len(re.findall('partial clone', html, re.I)) == 0
             len(re.findall('exit status', html, re.I)) == 0
    zcat ... | grep -icE 'promisor|promise[ds]?|partial clone' git-fsck-2.56.0.man.txt  -> 0
    grep -niE 'promisor|promise|partial' git-fsck.adoc  -> no match (exit 1)

So the manual (web rendering, installed 2.56.0 man page, and v2.56.0 adoc source) contains no statement
about promisor remotes, promised objects, partial clones, lazy fetching, or exit statuses.

## Implementation context at tag v2.56.0 (static reading, not executed)

- builtin/fsck.c:143-149 — in the reachability walk, `if (is_promisor_object(...)) return 0;`
  with comment "Further recursion does not need to be performed on this object since it is a
  promisor object (so it does not need to be added to "pending")".
- builtin/fsck.c:253-258 — `check_reachable_object`: `if (is_promisor_object(...)) return;`
  before the `printf_ln(_("missing %s %s"), ...)` diagnostic.
- builtin/fsck.c:469-472 — a reflog entry whose object is absent is an error only
  `else if (!is_promisor_object(repo, oid))`.
- builtin/fsck.c:534-540 — a ref whose object does not parse is counted as a valid ref and
  returns 0 when `is_promisor_object(...)`, instead of "invalid sha1 pointer".
- builtin/fsck.c:884-885 — `/* fsck knows how to handle missing promisor objects */`
  `repo->fetch_if_missing = 0;`
- fsck.c:1337-1340 — in the blob pass, an unreadable object is skipped when
  `is_promisor_object(options->repo, oid)` instead of reporting msg_missing.
- packfile.c:2061-2078 — `is_promisor_object` builds a static oidset only when
  `repo_has_promisor_remote(r)`, using `odb_for_each_object(... ODB_FOR_EACH_OBJECT_PROMISOR_ONLY ...)`;
  returns set membership.
- packfile.c:2006-2030 — `add_promisor_object` inserts the enumerated OID and walks trees/commits/tags,
  so objects referenced by promisor objects are also in the set. [INFERENCE: this is how a missing
  promised blob becomes exempt; the walk itself was read, not run.]
- packfile.c:748-750 — `p->pack_promisor = 1` when `<pack>.promisor` exists.

This is code behavior, not documented behavior. It is unexecuted in this lane (no fixture run assigned).

## Registry scope check

    grep -c 'fsck' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md   -> 0
    grep -rn 'fsck' /home/vgpnk/Projects/shokunin/kama-shokunin/registry         -> no match
    grep -n 'fsck' tools/report-landing-audit.py tests/report-audit/*.py          -> no match
    grep -c '^| S[0-9]' corpus/SOURCES.md                                        -> 101 rows, S001-S101

No row cites https://git-scm.com/docs/git-fsck, so this is new scope, not a reopened used source.
Prior use of `git fsck` in round 23 is probe measurement only:
.ufo/waves/round-23/falsify/advice/RowF26HugeAuthor.md:105, RowF04ReplaceFabricated.md:142,
RevSourcesBlob.md:53. Those are not SOURCES citations and imply no used-by cell.

## Unrun

- No local fixture constructed; no `git fsck` invoked; no exit code measured here.
- No full test suite, no build, no formatter.
