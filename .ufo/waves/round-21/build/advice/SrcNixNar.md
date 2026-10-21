VERDICT: partial - NAR at Nix tag 2.34.1 supports C2's premise that a directory identity must carry symlink nodes with their raw target text; it does not verify install_links() or its digest encoding, and bears on no C1 statement.

# SrcNixNar — Nix NAR symlink prior art (kama round 21, BUILD)
Access date 2026-10-21 (`date -I`, exit 0). Lane registry unchanged: corpus/SOURCES.md sha256 98df6390… before and after.

## Source and revision
- URL: https://nix.dev/manual/nix/2.34/protocols/nix-archive/ (the `stable` alias resolved to this 2.34 path on access). Kind spec, tier A.
- Pinned copy: https://github.com/NixOS/nix/blob/2.34.1/doc/manual/source/protocols/nix-archive/index.md = tag 2.34.1, commit 26842787496f2293c676fb36db38dacfd63497e0, blob sha256 11d16341595cdc287935e00bdb8062618ecb43a26c643c5f4cdd709d3b0713f1. Byte-identical at tag 2.34.9 (commit 5fb7eb7d64ba7b78819aa3ac6a7fdd21354910fc; cmp exit 0).
- Implementation at 2.34.1 (fetched; sha256 prefixes): src/libutil/archive.cc [1c1bcf95…], src/libutil/posix-source-accessor.cc [b529a6fa…], src/libutil/file-system.cc [d129033a…], doc/manual/source/store/file-system-object/content-address.md [6ceb1865…], doc/manual/source/protocols/nix-archive/nar.ksy [9ffdcbbd…].

## Quotes (verbatim; for the round lesson Gate)
- index.md line 29, §"# Nix Archive (NAR) format": `symlink = str("target"), str(target);`
- content-address.md line 14, §"Serialising File System Objects": "serialise the entire file system object tree into a single binary string, and then hash that binary string" (lines 46–49 name NAR as the directory format).
- archive.cc line 95 (code): `sink << "type" << "symlink" << "target" << this_.readLink(path);`

## Findings (observed in fetched files unless tagged)
1. A symlink node is `(` `type` `symlink` `target` <link text> `)`; there is no `contents` field (index.md lines 21–29).
2. The link text is recorded raw: archive.cc:95 → PosixSourceAccessor::readLink (posix-source-accessor.cc:181–185) → nix::readLink → file-system.cc:258 `return std::filesystem::read_symlink(path);`. [INFERENCE: read_symlink returns the link contents, not a resolved path; standard semantics, not fetched.]
3. Entries must be name-sorted (index.md line 31); the reader throws "NAR directory is not sorted" on `name <= prevName` (archive.cc:225–226).
4. The reader passes the parsed target straight to createSymlink (archive.cc:256–257); the grammar constrains the target only as a string. C2's gate rules (no '/' targets, no loops, chain must end at a pinned regular member) are kama policy, not NAR prior art.
5. Store-path tie: content-address.md line 14 hashes the serialized tree; lines 46–49 make NAR that serialization for directories. [INFERENCE: directory store-path digests are sha256 over NAR; the store-path derivation page was not opened.]
6. Flat and Git addressing error on a bare symlink (content-address.md line 78); NAR is the form that carries symlinks inside a tree.
7. useCaseHack is true only under __APPLE__ (archive.cc:20–26), so the rename paths (archive.cc:72–75, 228–232) are inactive on this Linux host.

## C1 / C2
- C2 (symlink-aware install identity): SUPPORTS the premise. The prior-art tree serialization carries symlink nodes with raw target text, so a regular-file-only digest (install_tree-like) cannot see a retarget; NAR does (probe below). Both sort names. Does NOT verify install_links_sha256: its `name -> text` lines are not NAR, so do not describe it as a NAR digest. Does not test install_tree() or the grid.
- C1 (report landing audit): no bearing; refutes nothing.

## Executed probe — out/SrcNixNar/nar_symlink_probe.py (+ nar_symlink_probe.out)
Stdlib encoder written from the grammar, not Nix's dumper; no Nix binary on this host (`command -v nix nix-store nix-hash nix-instantiate`, exit 1).
- Run 1: exit 1. Check 1 failed on my hand-computed length 144; the emitted hex decodes to 128 bytes (24+16+16+16+16+24+16). Constant corrected to 128.
- Run 2: exit 0, 4/4 PASS. A 128-byte root symlink `../lib/foo` parses back raw; retargeting changes NAR a1c35d43… → 48361569…; regular-only digest 69b59998… unchanged; mtime-only change leaves NAR a1c35d43… unchanged.

## Draft row (full text and Gate fields: out/SrcNixNar/S066-draft.md; id S066 = next unused, max S065 at round start)
```
| S066 | Nix Archive (NAR) format — https://nix.dev/manual/nix/2.34/protocols/nix-archive/ (repo copy: https://github.com/NixOS/nix/blob/2.34.1/doc/manual/source/protocols/nix-archive/index.md) | spec | A | how a NAR, the tree serialization Nix hashes for directory store paths, records one symlink: node type plus raw target text | §Nix Archive (NAR) format, EBNF lines 21–29 (`symlink = str("target"), str(target);` at line 29) of doc/manual/source/protocols/nix-archive/index.md @ nix tag 2.34.1 = commit 26842787496f2293c676fb36db38dacfd63497e0 (file sha256 11d16341…; identical at tag 2.34.9 = commit 5fb7eb7d64ba7b78819aa3ac6a7fdd21354910fc); §Kaitai `type_symlink` in nar.ksy (same directory) lines 159–169 (sha256 9ffdcbbd…) | NAR gives a symlink its own node type and stores its raw target string unresolved, so retargeting a link changes the serialized tree | queued | 2026-10-21 | on-release | — |
```
- Status queued: opened, worth mining, no admitted entry cites it. Flip to mined when a knowledge entry cites S066 (used-by then names it).
- Census dry run (scratch copy plus row; commands from CORPUS.md lines 133–147): rows 66; malformed 0; tier A=63 C=3; status mined=52 queued=7 rejected=7; duplicate ids none; enum violations none; missing used-by none. The first draft lacked the trailing `|` (malformed 1); fixed, rerun clean.

## Search log (rule 5)
- web_search "Nix manual Nix archive (NAR) format protocols symlink target": identified 15, screened 15, included 1 primary (nix.dev manual, 2.34 path) plus its repo copy; excluded 14: other manual versions (2.22, 2.29, 2.33, 2.35.2), the nix CLI page, an Ubuntu man page, Hackage and third-party write-ups. Stop: spec and implementation read at one tag; the search summary's wording was not quoted.

## Commands and exit codes
- `date -I` 0 · `command -v nix nix-store nix-hash nix-instantiate` 1 (absent)
- `curl -fsSL` raw index.md @2.34.1 0 · @2.34.9 0 · `cmp` 0 · `git ls-remote --tags https://github.com/NixOS/nix 'refs/tags/2.34*'` 0
- `curl -fsSL` nar.ksy, archive.cc, posix-source-accessor.cc, file-system.cc, content-address.md 0 each; src/libutil/archive.hh 22 (404); src/libutil/include/nix/util/archive.hh 0
- `python3 nar_symlink_probe.py`: run 1 exit 1, run 2 exit 0; census commands 0 (duplicate, enum and missing checks printed nothing)
- `cp` of lane corpus/SOURCES.md to scratch: 0 (read-only copy)

## Installs
None. Used curl, git, python3 3.14.8 (stdlib) and system grep/awk.

## Unknowns
- Not run against a Nix binary: the bytes follow the grammar; that Nix's dumper emits identical bytes is [INFERENCE].
- std::filesystem::read_symlink semantics taken from the standard name [INFERENCE].
- Store-path name derivation not read.
- install_links(), its gate and the grid were not examined; that belongs to the C2 reviewers.

## Cleanup
/tmp/kama-r21-SrcNixNar removed after this report (exit in transcript).
