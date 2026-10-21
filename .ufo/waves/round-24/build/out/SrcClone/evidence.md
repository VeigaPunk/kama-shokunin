# SrcClone — evidence transcript (2026-10-21, local −03 / UTC 17:59Z)

All commands run on the host; page fetches are official HTTPS, fixtures are
local `file://` only. Scratch: `/fast/scratch/hyaku/kama-r24/SrcClone/`.

## 1. Corpus scope check

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ git rev-parse HEAD
0df800e896f6bce285a81e794ad4ae1d1e6c3a71          # at seat start (14:53)
$ grep -rn "git-clone" . | grep -v '^./.ufo/' | grep -v Binary
(no output)
$ grep -c '^| S' corpus/SOURCES.md
101
$ grep -n '^| S089 \|^| S092 \|^| S094 \|^| S099 \|^| S101 ' corpus/SOURCES.md
101:| S089 | git(1) global options — https://git-scm.com/docs/git
104:| S092 | partial-clone design note — https://git-scm.com/docs/partial-clone
106:| S094 | gitrepository-layout(5) — https://git-scm.com/docs/gitrepository-layout
111:| S099 | partial-clone design note, missing-object handling — ...partial-clone#_handling_missing_objects
113:| S101 | git v2.56.0 `commit.c` `read_graft_line` — .../git/git/v2.56.0/commit.c
```

Only wave mention, `.ufo/waves/round-23/falsify/advice/SrcS094.md:121`:

```
- I did not open git-replace(1) or git-clone(1) to test the "similar to
  info/grafts" analogy beyond the quoted page sentence.
```

Existing practice without a row:

```
tests/report-audit/repo-state-grid.py:203:    g(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
tests/report-audit/repo-state-grid.py:204:      "--filter=blob:none", "--no-local", f"file://{lane}", str(clone))
tests/report-audit/repo-state-grid.py:491:                 ("remote.origin.partialclonefilter", "blob:none"),
tests/report-audit/repo-state-grid.py:601:      "--filter=blob:none", "--no-local", f"file://{lane}", str(clone))
```

## 2. Page fetch and version

```
$ curl -sS -L --max-time 60 https://git-scm.com/docs/git-clone -o git-clone.html
$ ls -l git-clone.html
-rw-r--r-- 107886 Oct 21 14:53 git-clone.html
$ sha256sum git-clone.html
d6e7b5e8b4e5d65401f4f002f94ccdac2faa27f914261b0db0916aef85b66dc9
$ grep -o 'git-clone last updated in [0-9.]*'
git-clone last updated in 2.54.0
$ grep -n '2\.55\.0\|2\.56\.0' git-clone.txt
1275:        2.55.0 → 2.56.0 no changes
```

Version-pinned renders:

```
$ curl ... https://git-scm.com/docs/git-clone/2.54.0  -> http=200
  grep -c "Do not checkout" -> 1 ; grep -c "will filter out all blobs" -> 1
  "git-clone last updated in 2.54.0"
  sha256 efe89007422070dde3837e2389d297d97d1bfcc79354fe90ebbab263978bdce3
$ curl ... https://git-scm.com/docs/git-clone/2.56.0  -> http=200
  599 bytes, <title>Redirecting&hellip;</title>, meta url=https://git-scm.com/docs/git-clone/2.54.0
```

Local interpreter: `git --version` → `git version 2.56.0`.

## 3. Anchors and quotes

`id` attributes (each present exactly once; page's own `href="#…"` links each
present exactly once):

```
Documentation/git-clone.txt---filterfilter-spec      (OPTIONS --filter=<filter-spec>)
Documentation/git-clone.txt---no-checkout            (OPTIONS -n, --no-checkout)
```

Raw HTML for the quotes:

```
...<span class='synopsis'><code>--no-checkout</code></span> </dt>
<dd>
<p>Do not checkout <span class='synopsis'><code>HEAD</code></span> after the clone is complete.</p>
...
For example, <span class='synopsis'><code>--filter=blob:none</code></span> will filter out all blobs (file
contents) until needed by Git.
```

Normalized-whitespace counts on both renders (`git-clone.html`,
`git-clone-2.54.0.html`):

```
1 | Do not checkout HEAD after the clone is complete.
1 | will filter out all blobs (file contents) until needed by Git
```

Word counts:

```
9  | Do not checkout HEAD after the clone is complete.
11 | will filter out all blobs (file contents) until needed by Git
14 | For example, --filter=blob:none will filter out all blobs (file contents) until needed by Git.
22 | Use the partial clone feature and request that the server sends a subset of reachable objects according to a given object filter.
```

`promisor` occurrences on git-clone (only in `--filter=auto`):
lines 2749, 2751, 2752, 2754 — "promisor-remote protocol",
"promisor remotes", "promisor.acceptFromServer".

Delegation sentence:

```
For details on all other available filter specifications, see the
--filter=<filter-spec> option in git-rev-list[1].
```

## 4. Cross-referenced pages (fetched, not registered)

```
$ curl ... https://git-scm.com/docs/git-rev-list  -> http=200
  "git-rev-list last updated in 2.56.0"
  "The form --filter=blob:none omits all blobs."
$ curl ... https://git-scm.com/docs/partial-clone  -> http=200
  "partial-clone last updated in 2.56.0"
  id="_handling_missing_objects" present
```

partial-clone §Handling Missing Objects body (whitespace-collapsed):

```
An object may be missing due to a partial clone or fetch, or missing due to
repository corruption. To differentiate these cases, the local repository
specially indicates such filtered packfiles obtained from promisor remotes as
"promisor packfiles". These promisor packfiles consist of a "<name>.promisor"
file with arbitrary contents ... 
...
no check as to whether the missing object is actually a promisor object is performed.
Dynamic object fetching tends to be slow as objects are fetched one at a time.
checkout (and any other command using unpack-trees) has been taught to bulk
pre-fetch all required missing blobs in a single batch.
```

## 5. Bounded local fixture (offline, scratch only)

Source for each fixture: `git init src; printf 'hello\n' > f; git add f;
git commit -qm c1; git config uploadpack.allowFilter true`. Blob is always
`ce013625030ba8dba906f756967f9e9ca394464a`, tree `10731d0b170b98481a00bdca161e874e0ab93377`.

### fx2 — `--no-checkout --filter=blob:none`, no-lazy probes

```
$ git -c protocol.file.allow=always clone -q --no-checkout --filter=blob:none --no-local "file://$PWD/src" dst
C=962076740fd7911b101b907c2ba117f08aed46cf
T=10731d0b170b98481a00bdca161e874e0ab93377
B=ce013625030ba8dba906f756967f9e9ca394464a
--- pack contents (idx only, no object lookup) ---
962076740fd7911b101b907c2ba117f08aed46cf commit 117
10731d0b170b98481a00bdca161e874e0ab93377 tree 29
--- no-lazy-fetch presence probes ---
96207674 -> present
10731d0b -> present
ce013625 -> MISSING
$
```

Pack size 168 bytes; worktree empty except `.git`. Only one pack; no blob.

### fx3 — `--filter=blob:none` with checkout

```
packs after clone: 2
pack-dac7d2ee...  ece0b913... commit 117
pack-dac7d2ee...  10731d0b... tree 29
pack-de041240...  ce013625... blob 6
worktree: .git f
GIT_NO_LAZY_FETCH=1 git cat-file -e <blob> -> exit=0
cat dst/f -> hello
```

The second pack exists because checkout needed the filtered blob (bulk prefetch).

### fx4 — `--no-checkout`, then a plain missing-object lookup

```
packs before: 1
git -C dst cat-file -e ce013625...  -> exit 0 (present)
packs after: 2
```

i.e. the lookup fetched the blob from the still-present `file://` remote; under
`GIT_NO_LAZY_FETCH=1` (fx2) the same probe reports MISSING. First ad-hoc attempt
(fx1) showed the same hydration, which is why fx2 added the no-lazy control.

## 6. Repo advance during the seat

```
$ git log --oneline -3
d1b9d95 round-24: preregister promisor completeness repair and correct r23 closure interpretation
0df800e round-23: sources S096-S101 ...
e876b95 round-23: falsify-wave integration ...
$ git diff --stat 0df800e..HEAD
 .ufo/waves/round-24/preregistration.json | 18 +
 LOG.md                                   | 21 +
$ git diff --name-only 0df800e..HEAD -- corpus/SOURCES.md
(no output)
```

`corpus/SOURCES.md` line numbers re-checked at d1b9d95: unchanged (101/104/106/111/113).

## 7. Environment

```
local=2026-10-21T14:59:01-0300   utc=2026-10-21T17:59:01Z
Python 3.14.8
curl 8.23.0 (x86_64-pc-linux-gnu) libcurl/8.23.0 OpenSSL/3.6.5 ...
git version 2.56.0
```

No installs or updates were performed.
