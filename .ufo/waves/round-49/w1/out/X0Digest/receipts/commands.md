# X0Digest — commands as run (2026-10-26)

Scratch is gone after the seat; every path below was inside
`S=/fast/scratch/hyaku/kama-r49/X0Digest` (`TMPDIR=$S`). The lane itself was read
only through `git -C` on a `git clone --shared` of it.

```
S=/fast/scratch/hyaku/kama-r49/X0Digest
L=/home/vgpnk/Projects/shokunin/kama-shokunin          # lane, read-only
git clone --shared $L $S/lane
TIP=74558c71c38ceaeace15fd4cf8aa9d84977584b1
```

## 1. Baseline at the build tip (fresh clone, read-only)

```
python3 $L/tools/digest-ledger.py  scan --repo $S/lane --rev $TIP --details   # exit 0
python3 $L/tools/hexrun-census.py  scan --repo $S/lane --rev $TIP --details   # exit 1
```

## 2. Fixtures with the draft paragraph, lane history kept

Plumbing only: index = the build tree, two modified blobs, one commit whose parent
is `TIP`; no worktree checkout and no `git commit` outside the fixture dir. Each
fixture printed `TOPLEVEL_OK <dir>` from `git -C <dir> rev-parse --show-toplevel`
before the first object was written.

```
D=$S/fx-full
git clone -q --shared --no-checkout $S/lane $D
test "$(git -C $D rev-parse --show-toplevel)" = "$D"
git -C $D read-tree $TIP
git -C $S/lane show $TIP:SCORECARD.md > $S/fx-full.sc.md; cat draft-scorecard-full.md  >> $S/fx-full.sc.md
git -C $S/lane show $TIP:LOG.md      > $S/fx-full.log.md; cat draft-log-full.md       >> $S/fx-full.log.md
b1=$(git -C $D hash-object -w $S/fx-full.sc.md)
b2=$(git -C $D hash-object -w $S/fx-full.log.md)
git -C $D update-index --add --cacheinfo 100644,$b1,SCORECARD.md
git -C $D update-index --add --cacheinfo 100644,$b2,LOG.md
tree=$(git -C $D write-tree)
c=$(GIT_AUTHOR_NAME=X0Digest GIT_AUTHOR_EMAIL=x0digest@fixture.invalid \
    GIT_COMMITTER_NAME=X0Digest GIT_COMMITTER_EMAIL=x0digest@fixture.invalid \
    git -C $D commit-tree $tree -p $TIP -m 'round-49 draft paragraph (seat X0Digest fixture identity)')
git -C $D update-ref refs/heads/r49draft $c
```

Revisions produced (scratch only, they do not exist in the lane):

| fixture | rev | contents |
|---|---|---|
| `fx-full` | `4798904300fe911363015ae323d630a293d966c6` | full-length paragraph (SCORECARD ends line 2811, LOG 2333) |
| `fx-abbrev` | `567fbe1ae441f0858c1a562bcaaaafc344b954b5` | house-style paragraph (8-char ids) |
| `fx-rows` | `788c2b35a371d1920a6fdf5384d18abea86207cf` | full-length paragraph + 3 draft hexrun rows + 3 evidence files + the digest row replacement |

`fx-rows` differs from `fx-full` by four more blobs and three evidence blobs:
`registry/hexrun-ledger.tsv` (3 rows appended, 110 lines), `registry/digest-ledger.tsv`
(the `35ac50fb…` row replaced), and
`.ufo/waves/round-49/w1/out/X0Digest/hexrun-evidence/{36d5ed26…,74558c71…,438127bc…}.txt`.

## 3. Fixtures with lane history absent (a rewritten or squashed integration tip)

A root commit whose tree is the build tree; no lane commit object exists in the repo,
so `lane_oid` cannot fire.

```
D=$S/fx-root-base
mkdir -p $D; git -C $D init -q
test "$(git -C $D rev-parse --show-toplevel)" = "$D"
git -C $S/lane archive $TIP | tar -x -C $D
git -C $D add -A -f
GIT_AUTHOR_NAME=X0Digest GIT_AUTHOR_EMAIL=x0digest@fixture.invalid \
GIT_COMMITTER_NAME=X0Digest GIT_COMMITTER_EMAIL=x0digest@fixture.invalid \
  git -C $D commit -q -m 'round-49 build tree, root commit, no draft paragraph'
```

| fixture | rev | contents |
|---|---|---|
| `fx-root-base` | `1dfcde156b286449a1002db14d353183128c8c75` | build tree, no paragraph (control) |
| `fx-root` | `68cbf00e7f7614ab6c228b32d75b42faf8589d1f` | + full-length paragraph |
| `fx-root` (2nd commit) | `9bbeb3764b198893743f02fdb7bf523795eef65a` | + draft rows, evidence files, digest row replacement |

## 4. Scans (all results in `receipts/scan-matrix.tsv`)

```
python3 $L/tools/digest-ledger.py scan --repo $S/fx-full  --rev 4798904300fe911363015ae323d630a293d966c6 --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-full  --rev 4798904300fe911363015ae323d630a293d966c6 --details
python3 $L/tools/digest-ledger.py scan --repo $S/fx-abbrev --rev 567fbe1ae441f0858c1a562bcaaaafc344b954b5 --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-abbrev --rev 567fbe1ae441f0858c1a562bcaaaafc344b954b5 --details
python3 $L/tools/digest-ledger.py scan --repo $S/fx-root  --rev 68cbf00e7f7614ab6c228b32d75b42faf8589d1f --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-root  --rev 68cbf00e7f7614ab6c228b32d75b42faf8589d1f --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-root-base --rev 1dfcde156b286449a1002db14d353183128c8c75 --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-rows  --rev 788c2b35a371d1920a6fdf5384d18abea86207cf --details
python3 $L/tools/digest-ledger.py scan --repo $S/fx-rows  --rev 788c2b35a371d1920a6fdf5384d18abea86207cf --details
python3 $L/tools/hexrun-census.py scan --repo $S/fx-root  --rev 9bbeb3764b198893743f02fdb7bf523795eef65a --details
python3 $L/tools/digest-ledger.py scan --repo $S/fx-root  --rev 9bbeb3764b198893743f02fdb7bf523795eef65a --details
```

## 5. Does an abbreviated citation reach either census?

```
mkdir -p $S/mini-abbr/registry $S/mini-full/registry
git -C $S/lane show $TIP:registry/digest-ledger.tsv > $S/mini-abbr/registry/digest-ledger.tsv
cp $S/mini-abbr/registry/digest-ledger.tsv $S/mini-full/registry/digest-ledger.tsv
printf 'witness pin recorded in house style: b11909 llama-server `35ac50fb`.\n' > $S/mini-abbr/doc.md
printf 'witness pin recorded in full: b11909 llama-server `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`.\n' > $S/mini-full/doc.md
python3 $L/tools/digest-ledger.py scan --dir $S/mini-abbr --details   # tokens=0, exit 0
python3 $L/tools/digest-ledger.py scan --dir $S/mini-full --details   # tokens=1 external_ok=1, exit 0
```

## 6. The pinned server digest, re-hashed

```
sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server
git -C $S/lane show $TIP:tools/round49-replay-witness-audit.py | grep -n '^SERVER_SHA'
stat -c '%s bytes, mode %A' /home/vgpnk/.local/opt/llama-b11909/llama-server
```

Output is `x0-digest-rehash-r49.txt`.

## 7. Remote identity of the freeze, build and base commits

```
gh api repos/VeigaPunk/kama-shokunin/commits/36d5ed2681111b68c180f8ab1646d8dc9beaedee --jq '{sha, date: .commit.committer.date, message: (.commit.message|split("\n")[0]), parents: [.parents[].sha]}'
gh api repos/VeigaPunk/kama-shokunin/commits/74558c71c38ceaeace15fd4cf8aa9d84977584b1 --jq …
gh api repos/VeigaPunk/kama-shokunin/commits/438127bc01ff3b99f98468549d58046f932490ef --jq …
gh api rate_limit --jq '.rate | {remaining, limit}'      # 4982 / 5000 after these three
```

Each returned 200 with the same sha; the outputs are in the three evidence files.

## 8. How many abbreviations the censuses cannot see

Backticked runs of `[0-9a-f]{7,31}` in the integrative documents, resolved with
`git rev-parse --verify --quiet <id>^{commit}` at the build tip:

```
SCORECARD.md 137   LOG.md 111   corpus/SOURCES.md 5   corpus/QUALITY.md 21   SKILL.md 28   total 302
```

and the in-tree truncated forms of the round-49 witness pin:

```
git -C $S/lane show $TIP:corpus/README.md | grep -o '.\{0,30\}35ac50fb.\{0,60\}'
  -> … `llama-b11909/llama-server` sha256 `35ac50fb…d7ff0`), and `provenance.verified.at` is     (line 1009)
git -C $S/lane show $TIP:corpus/knowledge/llamacpp-loading-lifecycle.md | grep -o …
  -> `35ac50fb…7ff0`                                                                            (line 440)
git -C $S/lane show $TIP:corpus/lessons/round-47.md | grep -o …
  -> `llama-b11909/llama-server` sha256 `35ac50fb…7ff0`                                         (line 20)
```

## 9. Leftovers

No llama-server was started by this seat (the two live ones in `pgrep -af llama-server`
belong to peers X1Offline and U0Consumers). `rm -rf /fast/scratch/hyaku/kama-r49/X0Digest`
ran at the end of the seat; the lane, the fleet repo and `~/.local` were not written.
