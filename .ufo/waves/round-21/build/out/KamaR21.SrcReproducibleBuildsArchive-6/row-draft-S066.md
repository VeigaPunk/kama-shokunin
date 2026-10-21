# S066 - contract-v1 row draft (KamaR21.SrcReproducibleBuildsArchive-6, round 21)

Not written to corpus/SOURCES.md; the L1 appends it. Registry last row is S065 (65 rows, checked
2026-10-21), so S066 is the next unused id; renumber if another round-21 draft takes it first.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S066 | Reproducible Builds — Stable order for inputs — https://reproducible-builds.org/docs/stable-inputs/ | docs | A | directory-listing order and locale-independent sorting of build inputs, including archive member order; not a digest format, not symlink identity, not any kama code | §Stable order for inputs (page title and intro paragraphs) and §Example: tar of that page; also §File ordering of https://reproducible-builds.org/docs/archives/ (same fetch). Live pages fetched 2026-10-21, no version printed, Last-Modified 2026-10-19 17:18:03 GMT on all three pages. Live HTML sha256: stable-inputs bb90eb799c4fef244b0badfae7d588c13156b2bb3eeb9f3bd0bd76b470cc2568; archives 72ca2de401821e717ec7843f4b865d5ed14503518080871412800e031ef7fd9b. Rendering source (Salsa reproducible-builds/reproducible-website, master): _docs/stable_inputs.md blob 97d60745b113a977b3b3e2d742fe9ce85043564e, last commit 3eb4b174 (2026-04-20); _docs/archives.md blob 81587c1c4308b6c30655c8da9208869d690fd963, last commit 50909f64 (2026-04-16) | Most filesystems do not guarantee a stable directory listing order, so a step that depends on input order must sort explicitly with a fixed locale (the page's example is LC_ALL=C sort). | queued | 2026-10-21 | 180d | — |

Flip: queued -> mined, with used-by set to the knowledge or lesson path that cites S066, logged old->new in the round lesson.

## Gate line (lessons/round-21.md, CORPUS rule 1)

| Candidate | Decision | URL, access date, location and quote |
|---|---|---|
| S066 | admit as queued | https://reproducible-builds.org/docs/stable-inputs/ opened 2026-10-21; §Stable order for inputs, intro under the page title, 18 words: "When sorting inputs, one must ensure that the sorting order is not affected by the system locale settings." Second: https://reproducible-builds.org/docs/archives/ opened 2026-10-21; §File ordering, 14 words: "most archive formats will read their content in the order returned by the filesystem". Both quotes verified verbatim in the live HTML and the source blob (verify_source_quotes.py, exit 0). |

## Search-log note (CORPUS rule 5)

2026-10-21 - round-21 directory-order source (S066). Question: does an official reproducible-builds source ground an explicit, locale-independent sort of directory entries for kama's C2 install digest? Where: https://reproducible-builds.org/docs/stable-inputs/ and https://reproducible-builds.org/docs/archives/ (live HTML pinned by sha256; Salsa source blobs id-verified with git hash-object), and https://reproducible-builds.org/docs/stable-outputs/ (located, not cited). Identified 3 pages, screened 3, included 1 row (S066, anchor cites two pages), excluded 1 (stable-outputs §General locale note: same concept, corroboration only). The guessed URL https://reproducible-builds.org/docs/ordering/ returned HTTP 404 and is not a source. Stop: locale dependence and the C-locale sort recipe located in both pages; the pages are silent on digests, symlinks and Python sort semantics.

## Leads (unopened; a lead is never a row)

- Python stdtypes, string comparison by code point: would source "sorted() on str ignores locale" in the docs instead of by observation.
- GNU coreutils sort manual, LC_ALL=C byte order: would source the shell-side claim.
