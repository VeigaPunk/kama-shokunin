VERDICT: partial - S066 supports only the explicit, locale-independent sort inside C2's install_links_sha256; silent on symlink identity; no bearing on C1.

Scope: S066 draft (reproducible-builds.org ordering pages) mapped to C1/C2. Lane not edited; draft commit a29bb84 read from a scratch clone, removed afterwards. Out dir: .ufo/waves/round-21/build/out/KamaR21.SrcReproducibleBuildsArchive-6/ (row-draft-S066.md, fetched/, four stdlib scripts).

## 1. Draft row (L1 appends after S065; I did not write corpus/SOURCES.md)

```
| S066 | Reproducible Builds — Stable order for inputs — https://reproducible-builds.org/docs/stable-inputs/ | docs | A | directory-listing order and locale-independent sorting of build inputs, including archive member order; not a digest format, not symlink identity, not any kama code | §Stable order for inputs (page title and intro paragraphs) and §Example: tar of that page; also §File ordering of https://reproducible-builds.org/docs/archives/ (same fetch). Live pages fetched 2026-10-21, no version printed, Last-Modified 2026-10-19 17:18:03 GMT on all three pages. Live HTML sha256: stable-inputs bb90eb799c4fef244b0badfae7d588c13156b2bb3eeb9f3bd0bd76b470cc2568; archives 72ca2de401821e717ec7843f4b865d5ed14503518080871412800e031ef7fd9b. Rendering source (Salsa reproducible-builds/reproducible-website, master): _docs/stable_inputs.md blob 97d60745b113a977b3b3e2d742fe9ce85043564e, last commit 3eb4b174 (2026-04-20); _docs/archives.md blob 81587c1c4308b6c30655c8da9208869d690fd963, last commit 50909f64 (2026-04-16) | Most filesystems do not guarantee a stable directory listing order, so a step that depends on input order must sort explicitly with a fixed locale (the page's example is LC_ALL=C sort). | queued | 2026-10-21 | 180d | — |
```

- Tier A: official project documentation, scoped to directory-listing order and locale-dependent sorting; it is guidance, not a spec.
- Status queued (opened; no used-by path yet). Flip to mined only when a knowledge or lesson path cites it, and set used-by in that same commit (census requires an existing path).
- id S066 is the next unused id (registry S001–S065, 65 rows). If another draft takes it first, renumber.
- Gate line and search-log note (CORPUS rules 1 and 5): out dir row-draft-S066.md.

## 2. Quotes (verify_source_quotes.py exit 0, RESULT PASS; each verbatim in the live HTML and the Salsa source blob, under the heading named)

- Q1, 18 words, https://reproducible-builds.org/docs/stable-inputs/, §Stable order for inputs (intro under page title): "When sorting inputs, one must ensure that the sorting order is not affected by the system locale settings."
- Q2, 14 words, https://reproducible-builds.org/docs/archives/, §File ordering: "most archive formats will read their content in the order returned by the filesystem"
- Q3, 25 words, same page, §File ordering (backticks around sort dropped as rendering): "Care must be taken to ensure that sort is called in the context of the C locale to avoid any surprises related to collation order."

## 3. Revision pins (every command exit 0)

- curl -sS -D … -w → HTTP 200: stable-inputs 40521 B, archives 52751 B, stable-outputs 40580 B. Each sends Last-Modified Mon, 19 Oct 2026 17:18:03 GMT. No version is printed.
- sha256sum of the saved live HTML: stable-inputs bb90eb799c4fef244b0badfae7d588c13156b2bb3eeb9f3bd0bd76b470cc2568; archives 72ca2de401821e717ec7843f4b865d5ed14503518080871412800e031ef7fd9b.
- git hash-object on the saved sources equals the Salsa tree ids: _docs/stable_inputs.md 97d60745b113a977b3b3e2d742fe9ce85043564e; _docs/archives.md 81587c1c4308b6c30655c8da9208869d690fd963; _docs/stable_outputs.md a8f345b1241b3c92c785d60496c3da7adeb1b15c.
- Salsa path-scoped last commits: stable_inputs.md 3eb4b174 (2026-04-20); archives.md 50909f64 (2026-04-16). Project last_activity_at 2026-10-19T17:17:29Z.
- [INFERENCE] the live pages are built from master; every quote matches both the live bytes and the source blob.
- Miss: https://reproducible-builds.org/docs/ordering/ returns HTTP 404. The ordering material is at /docs/stable-inputs/ and /docs/stable-outputs/.

## 4. C1 / C2 mapping

- C2, supports in part. The page says "Most filesystems do not guarantee…" and that sorting "must ensure that the sorting order is not affected by the system locale settings". The draft sorts explicitly: install_links() uses sorted(os.listdir(...)) (tools/kama-llamacpp-live.py:214) and digests over sorted(links) (:224-225); tests/llamacpp-live/check-receipt.py:173-178 recomputes with sorted(links).
- Observed (locale_order_check.py exit 0) on the real 61-entry tree: Python sorted() output is identical under LC_ALL=C, C.utf8 and en_US.utf8, and equals the C-locale sort. Shell sort under en_US.utf8 differs from C at 40 of 61 positions (position 0: LICENSE vs ggml-rpc-server). The draft uses no shell sort, so the hazard the page names does not reach it; this holds for this tree only.
- [INFERENCE] Python str order is code-point order in general; it stays unsourced until the lead in §7 is opened.
- C2 is silent on symlink identity, readlink text semantics, the name -> text encoding, chain checks and the gate. No source here refutes it.
- C1, no bearing. tools/report-landing-audit.py at a29bb84 enumerates no directories (search for glob, listdir, iterdir, rglob, scandir, os.walk: no hits); its sets are already sorted (:116, :127, :202). The source neither supports nor refutes a C1 statement.

## 5. Finding outside the row (symlink_encoding_probe.py exit 0)

- control, ASCII soname target: install_links() returns {'libllama.so.0': 'libllama.so.0.7.0'} and a digest.
- probe, link target containing byte 0xff: install_links() raises UnicodeEncodeError ('\udcff' surrogates not allowed) at the .encode() on :224-225; nothing catches it there.
- [INFERENCE, not run through the launcher] This fails loud rather than yielding a wrong digest, and real names are ASCII. install_tree() :201 has the same encode for non-UTF-8 filenames (not probed). The fix is left to L1.

## 6. Checks for the main agent (run once after landing; all exit 0 here)

python3 verify_source_quotes.py · python3 locale_order_check.py · python3 row_census_check.py · python3 symlink_encoding_probe.py <a29bb84 checkout>/tools/kama-llamacpp-live.py

## 7. Leads (unopened; never rows)

Python stdtypes §Comparisons (string ordering by code point); GNU coreutils sort manual (LC_ALL=C byte order).

## 8. Tooling and cleanup

Installed or updated: nothing. Tools used, all already present: curl, sha256sum, git, python3 3.14.8, sort, locale. No processes started. Scratch /tmp/kama-r21-SrcReproducibleBuildsArchive-6 removed (rm -rf chained; path confirmed absent).
