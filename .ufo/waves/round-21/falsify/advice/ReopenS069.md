VERDICT: partial - anchor, revision, quote, tier, kind, opened, status and used-by agree; teaches overstates (zip "forbid" not enforced, error cases omitted, TreeCap clause is another mechanism); anchor omits DirFiles lines and the commit.
Attacked: row S069 (corpus/SOURCES.md:81), its Gate row (corpus/lessons/round-21.md:45), CORPUS.md contract v1 (lines 64-163). Read-only. Evidence: falsify/out/ReopenS069/ (checks.txt, main.go, go.mod, go.sum, probe-output.txt).

## Source re-open (access 2026-10-21; checks.txt 1-5, 9)
- hash.go and zip.go at tag v0.42.0: HTTP 200; decoded sha256 24de6a73... and b749c43c...
- Tag v0.42.0 = commit b5136e5ba156da612a1efc6e49b55988a134a5e0 (git ls-remote, exit 0; lightweight tag).
- Proxy module v0.42.0 copies of both files are byte-identical to the tag sources (cmp exit 0 twice).
- Lane corpus/SOURCES.md is byte-identical to committed b76727f (cmp exit 0).

## Field by field
- id S069: AGREE. Unique; awk NF=13.
- source: AGREE, note. Row cites hash.go only; the zip.go URL used by the Gate is absent.
- kind code, tier A: AGREE. Pinned source code, scoped to h1 symlink behaviour.
- scope: AGREE. Hash1 44-65, HashDir 70-79, DirFiles 84-109.
- anchor: PARTIAL. Verified: hash.go:76 `return os.Open(...)` and zip.go:42. Missing: DirFiles 84-109 (filepath.Walk at 87, info.IsDir at 91; this is why links are listed) and the commit b5136e5b.
- teaches: DISAGREE in part (see below).
- opened 2026-10-21: AGREE (matches today's date and the Gate header).
- recheck on-release: AGREE (pinned tag).
- status mined: AGREE. Contract requires one used-by path that exists and cites the row; corpus/lessons/round-21.md exists and cites S069 at :27 and :45.
- used-by corpus/lessons/round-21.md: AGREE. Corpus grep finds S069 only in SOURCES.md:81,105 and this lesson; no knowledge entry cites it, so the list is complete.

## Gate quote (round-21.md:45)
- "Symbolic links and other irregular files are not allowed." is zip.go:42 verbatim (grep: 1 match); 9 words (<=25); URL matches the fetched file. AGREE.
- The h1 half, "h1 opens each file by content, hash.go line 76", is a location with no quote; the contract requires a quote grounding teaches. PARTIAL. Verbatim candidate at hash.go:76: `return os.Open(filepath.Join(dir, strings.TrimPrefix(name, prefix)))`.

## Teaches vs executed behaviour (x/mod v0.42.0, go1.27.3 linux/amd64; probe-output.txt, go run exit 0)
- "h1 follows link targets by content": AGREE for file targets (B1 link->a.txt equals B2 regular copy, equal=true). INCOMPLETE: dangling link gives an error (D); link to directory gives "is a directory" (E); symlinked root gives "is not a directory" (F).
- "so h1 cannot express symlink identity": AGREE. A1 (link->a.txt) equals A2 (link->b.txt) with identical bytes, equal=true. Hash1 (hash.go:56-62) hashes per-file content digests and names only. C: retarget to different bytes gives equal=false, so the blind spot is link text, not target bytes.
- "module zips forbid links": AGREE as the doc sentence (zip.go:42). DISAGREE as enforcement. G: producers omit links (CheckDir "not a regular file"; CreateFromDir writes no link entry). H: CheckZip accepts a symlink-mode entry (err=nil); HashZip equals the regular entry with the same text (equal=true); Unzip writes a regular read-only file.
- "a content-only digest is the R19 TreeCap shape": DISAGREE. Kama-internal framing, not a source statement [INFERENCE from the wording]. TreeCap skips links (round-19.md:53-57: "pins regular files only"); h1 lists and follows them and does change on different-byte retargets (C). Shared blind spot: link identity. Drop or restate.
- Page-internal, not in the row: hash.go:34-36 says h1 is "as if by ... sha256sum $(find . -type f | sort)". Executed: find -type f lists a.txt only; link.txt is type l; DirFiles lists it. The code, not the comment, defines link behaviour.

## Proposed row changes (L1 applies; nothing edited here)
- teaches (one benefit): "h1 hashes the bytes a link resolves to, never its target text: a same-bytes retarget leaves it unchanged; a dangling or directory link makes HashDir fail."
- anchor: add "Hash1 56-62; DirFiles 84-109 (Walk 87, IsDir 91); zip.go listFilesInDir 997-1001; commit b5136e5b...".
- Gate: add the hash.go URL and the line-76 quote.
- scope "not a defect report": the page does not decide this, and CheckZip does not enforce its own doc line 42 (H). [INFERENCE] whether that is a defect: open.

## Contract v1 and census
- CORPUS.md section vs .ufo/waves/kaika/SOURCES-CONTRACT-v1.md: identical except three heading depths (### vs ## for Shape, Rules, Census). diff exit 1, 79 lines each. No content drift.
- Census at b76727f (contract commands, cwd scratch lane, all exit 0): rows 74; malformed 0; A70 B1 C3; mined60 queued7 rejected7; dup none; enum none; mined used-by missing none. Matches the lesson's stated counts.

## Limits and tooling
- Linux amd64, Go 1.27.3, x/mod v0.42.0 only. Link following relies on filepath.Walk using Lstat (path.go:419 doc, :424 os.Lstat); other Go versions [INFERENCE].
- Probe is my own code; I did not reuse SrcGoDirhash's probe output.
- Installs: none. Used the go1.27.3 already present (installed by sibling SrcGoDirhash-6 per its advice; I ran only `go version`).
- Scratch /tmp/kama-r21-ReopenS069 removed (rm exit 0).
