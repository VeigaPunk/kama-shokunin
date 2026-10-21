VERDICT: confirm - Go's h1 cannot see symlink identity (executed: a same-bytes retarget and a link-for-copy swap hash equal); supports C2's premise, refutes nothing, no C1 bearing.

# SrcGoDirhash — round 21 (KamaR21.SrcGoDirhash-6), opened 2026-10-21

Probe labels A1–A9, B1–B4, C1–C3, D1–D3 are lines of `out/SrcGoDirhash/probe-output.txt`, not claims. "C2" below always means the claim.

## Answer: does the module tree hash include symlinks?
- Module hash (go.sum h1 = HashZip over the module zip): links are not in it as links. golang.org/x/mod v0.42.0 zip: 137 entries, 0 symlink, 0 non-regular, 0 directory (python3 S_ISLNK sweep, exit 0). Go's producers omit links (zip.go:323–326; probe B1, B2). HashZip ignores mode bits: a symlink-mode entry hashes equal to a regular entry with the same text (probe C2 equal=true). CheckZip accepts the symlink entry (probe C1); Unzip writes it as a read-only regular file holding the link text (probe C3).
- Directory hash (HashDir/DirFiles): a link is listed by name (A1) and its target bytes are read via os.Open (hash.go:76). Link text never enters the hash. Same-bytes retarget (A2, D1), link-for-regular-copy (D3) and same-resolution chain shortcut (A9) are unchanged; different bytes change it (A3, D2). Dangling link (A6), link-to-directory (A7) and symlinked root (A8) are errors, not hashes. Walk does not traverse links (A7; Go 1.27.3 src/path/filepath/path.go:419, "Walk does not follow symbolic links.").

## Gate (all opened 2026-10-21)
- URL https://go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go (`?format=TEXT`, base64-decoded sha256 24de6a735c1605e39b6381e6962787faa5c59adab896fb66dbc1ac8b6afcb297 = module zip member; exit 0). zip.go at .../v0.42.0/zip/zip.go decodes to b749c43c2ded96ed19307cedb2c8a70d1375cc2ef46977b225ad441c67be76aa = zip member (exit 0).
- Revision: commit b5136e5ba156da612a1efc6e49b55988a134a5e0, tag refs/tags/v0.42.0, time 2026-10-09T20:24:17Z (https://proxy.golang.org/golang.org/x/mod/@v/v0.42.0.info, read OK; @latest = v0.42.0).
- Module zip https://proxy.golang.org/golang.org/x/mod/@v/v0.42.0.zip, sha256 2770e372e42c30dd498d63bb094fe257edfad6882c611f8e0d82925feac159f3 (curl exit 0). https://sum.golang.org/lookup/golang.org/x/mod@v0.42.0 records h1:ICeL3t2L30ljSPHHxDnR4fqVcBt/zR2zJAb9juavmQg= (exit 0); my Hash1 recomputation over the 137 entries matches it.
- Quote Q1 (9 words, verbatim): "Symbolic links and other irregular files are not allowed." — zip.go, package doc, module-zip restriction list, line 42.
- Quote Q2 (code, verbatim): `return os.Open(filepath.Join(dir, strings.TrimPrefix(name, prefix)))` — hash.go, HashDir, osOpen closure, line 76.
- Quote Q3 (6 words, verbatim): "Skip symbolic links (golang.org/issue/27093)." — zip.go, checkFiles comment, line 324.
- Not already a row: tool grep over corpus/SOURCES.md for `dirhash|sumdb|go\.sum|hash1|symlink|golang|x/mod` → "No matches found". corpus/ hits are unrelated symlink refusals and TreeCap prose (knowledge/llamacpp-loading-lifecycle.md:318–322; lessons/round-19.md:53–57).

## Draft row (contract v1, 11 cells; file `out/SrcGoDirhash/draft-row-S066.md`; L1 renumbers in write order, several siblings also drafted S066)
| S066 | golang.org/x/mod v0.42.0 sumdb/dirhash and zip packages — https://go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go (zip: https://go.googlesource.com/mod/+/refs/tags/v0.42.0/zip/zip.go) | code | A | how Go's h1 hashes treat symbolic links: a directory hash follows link targets by content and never records link text; x/mod builds module zips without links, and a symlink-mode zip entry hashes as its target text; not other Go versions, not kama's install tree | hash.go §HashDir lines 75–77 (os.Open at 76) and §DirFiles lines 84–93 (filepath.Walk at 87, info.IsDir at 91); zip.go package doc line 42, §checkFiles lines 323–326 and §CheckZip loop lines 449–501 (no file-mode check); all at golang.org/x/mod v0.42.0 commit b5136e5ba156da612a1efc6e49b55988a134a5e0 (tag refs/tags/v0.42.0); module zip sha256 2770e372e42c30dd498d63bb094fe257edfad6882c611f8e0d82925feac159f3, h1:ICeL3t2L30ljSPHHxDnR4fqVcBt/zR2zJAb9juavmQg= | a directory digest that follows links hashes their target bytes under the link name and never their text, so a same-bytes retarget or a link-for-copy swap is invisible; a link-aware pin must record readlink text (hash.go:76, :87) | queued | 2026-10-21 | on-release | — |

## Census (CORPUS.md lines 133–147; every command exit 0)
- before (lane file, read-only counts): rows 65; A=62 C=3; mined=52 queued=6 rejected=7.
- after (scratch clone, row at line 78): rows 66; malformed 0; A=63 C=3; mined=52 queued=7 rejected=7; duplicate ids none; enum violations none; missing mined paths none. Saved: `out/SrcGoDirhash/census-after.txt`.

## Proposed status and flip
- queued; used-by —; recheck on-release. Flip to mined when corpus/knowledge/llamacpp-loading-lifecycle.md (TreeCap, lines 318–322) cites S066 by path.

## Which statement it bears on
- C2 (install_tree pins regular files only; a soname retarget leaves install_tree_sha256 unchanged): SUPPORTS the premise. Executed: a link-following digest also misses same-bytes retargets (A2, D1), so the blind spot is not an artifact of skipping links.
- [INFERENCE, not run on the grid] C2's grid cells `link-same-resolution-shortcut` (tests/llamacpp-live/install-links-grid.py:133–136) and `type-link-to-regular-copy` (:144–146) are the classes A9 and D3 show a Go-style digest cannot see, so install_links (readlink text) is the needed element, not an optional one. Refutes no C2 statement. Refutes one alternative: a HashDir-style digest catches different-byte retargets (A3) but not same-bytes retargets, shortcuts or link-for-copy swaps, so it does not fully close the TreeCap debt.
- C1 (report landing audit): no bearing.
- Format: install_tree (tools/kama-llamacpp-live.py:178–202) and install_links (:205–226) digest flat `name sha` / `name -> text` lines in hex sha256. Not Hash1-compatible (Hash1: `h1:` base64 over `<hex>  <path>` lines). Same construction family; do not claim equality.

## Discrepancies (executed; for L1/critic)
- zip.go:42 says symlinks "are not allowed", but CheckZip (zip.go:405; loop 449–501 has no mode check) accepts a symlink-mode entry (C1). The validator does not enforce the documented rule.
- The web_search summary said symlinked directories are traversed and that links are not in the hash. A7 and A1/A4 contradict both. Not used as a source.
- pkg.go.dev reader for sumdb/dirhash at v0.42.0 says "This package is not in the latest version of its module" with an empty Documentation section, yet the zip contains hash.go and hash_test.go. Not used.

## Search log (rule 5), proposed line
- 2026-10-21 — round-21 Go dirhash symlinks. Question: does Go's tree/module hash include symlinks? Where: x/mod v0.42.0 via googlesource, proxy zip, sum.golang.org; pkg.go.dev (inconsistent, unused); one web_search (15 results: identified 15, screened 15, included 0). Stop: executed probe on Go 1.27.3 covers each claim; other Go versions and non-POSIX filesystems not probed.

## Commands and exits (all run this session)
- curl proxy x/mod zip 0; sha256sum 0; curl sum.golang.org lookup 0; `go get golang.org/x/mod@v0.42.0` 0; `go vet .` 0; `go run . <work>` 0 (final clean run, logged); `go version` 0 (go1.27.3 linux/amd64); python3 urllib download of the go1.27.3 tarball (70588678 bytes, matches go.dev JSON), sha256 65efbc80fdc1fa2cd2631cad5b481777a68e8725f34e89f50fc6ac714e379b40 matched go.dev/dl JSON; census commands 0; `sha256sum -c SHA256SUMS` 0.
- Read-only lane checks: cmp (0), ls (0), grep (ok); lane git state untouched (clone to scratch only).

## Tooling record (tooling directive)
- Installed Go go1.27.3 linux/amd64 from the official go.dev release (dl.google.com; sha256 verified against go.dev/dl JSON). Extracted to ~/.local/opt/go1.27.3/go; added ~/.local/bin/go and gofmt symlinks. Reason: execute dirhash/zip behaviour; no Go existed on the host. Kept (persistent tool).
- golang.org/x/mod v0.42.0 fetched into scratch GOPATH only. No pacman, no upgrades.

## Files and hygiene
- `out/SrcGoDirhash/`: main.go, go.mod, go.sum, probe-output.txt, draft-row-S066.md, census-after.txt, SHA256SUMS.
- Lane: no tracked file edited; new files only under build/advice/SrcGoDirhash.md and build/out/SrcGoDirhash/. Scratch `/tmp/kama-r21-SrcGoDirhash` removed after the copies were verified (chmod u+w on the read-only Go module cache, then rm -rf; exit 0).
- Limits: Linux amd64, Go 1.27.3, x/mod v0.42.0 only. [INFERENCE] other OSes and filesystems untested.
