VERDICT: partial - S066's URL, man-pages 6.19 revision, Gate quote (verbatim, 12 words, ¶3) and mined status/used-by hold; teaches asserts a kama-digest claim the page never makes, the chain example is ¶4 not ¶3, and the scope's "linker name → real name" labels are not on the page.

Target: registry row S066 (corpus/SOURCES.md:78) and its round-21 Gate (lessons/round-21.md:42) at lane a6617149; man7 page re-fetched 2026-10-21. Lane not edited.

## Executed evidence (exit in brackets)
- Fetch [0]: man7 ldconfig.8.html, HTTP 200, 11926 B, sha256 6a81540a…, 11:18:29Z; same hash as the seat's pin. Footer "Linux man-pages 6.19 2026-08-03".
- Upstream [0]: man-pages-6.19.tar.xz (mirror, 25-Aug-2026), sha256 88a7c42a…, `sha256sum -c` OK [0]. PGP signature not checked.
- Upstream troff `.TH` reads "Linux man-pages (unreleased)"; host man-pages 6.19-1 [`pacman -Q`, 0] installs "6.19"; `diff` [1]: only line 6 differs.
- DESCRIPTION word tokens: man7 == upstream troff in 6 of 6 paragraphs (blank lines = troff `.P`).
- CORPUS.md census on a6617149 [all 0]: 74 rows, 0 malformed, A70 B1 C3, mined60 queued7 rejected7; no duplicate ids, enum violations or missing used-by paths. Round start (7a6bc911): A62 C3, mined52 queued6 rejected7.
- Fleet `scripts/sources-census.sh validate` on the a6617149 SOURCES.md [0]: "file ok", W04 only, none on S066 (matches the lesson's "validate exit 0").
- `tools/sources-append-only.py --from 7a6bc911 --to a6617149` [0]: added S066–S074 only, no violations.
- `ldconfig-n-experiment.sh` [0], glibc 2.44: `ldconfig -n` creates only `libfoo.so.1 -> libfoo.so.1.12`, never `libfoo.so`; a copied real libz gives only `libz.so.1`.
- `check-s066.py` [1]: 31 checks, 30 pass; the one FAIL is the anchor's "¶3 holds the chain example" (it is ¶4).

## Field verdicts (registry row at a6617149)
| Field | Verdict | Basis |
|---|---|---|
| id, kind docs, opened 2026-10-21, recheck on-release | AGREE | validator; fetch date |
| source title + URL | AGREE | HTTP 200; page title matches |
| tier A | AGREE (judgment) | maintainers' man page; S057 precedent |
| scope "on glibc systems" | AGREE | OPTIONS "Since glibc 2.2/2.7/2.32" (4 hits) |
| scope "not the DT_SONAME tag" | AGREE | 0 "DT_" on the page |
| scope "(linker name → SONAME → real name)" | PARTIAL | page shows the 3-file chain and calls the middle file the SONAME; names neither outer role |
| anchor "¶1 and ¶3 (SONAME chain example)" | PARTIAL | ¶1 and the SONAME sentence (¶3) correct; the example is ¶4 |
| revision "man-pages 6.19, page dated 2026-08-03" | AGREE + caveat | footer, tarball sha, `.TH` date agree; upstream `.TH` says "(unreleased)" |
| teaches 1 "symlink in the middle of a chain" | AGREE | ¶3 "the middle file … is the SONAME"; example arrows; "symbolic links" |
| teaches 2 "that ldconfig creates" | PARTIAL | ¶1 "creates the necessary links" (generic); ¶3 says "expects"; true for the SONAME link (experiment) |
| teaches 3 "install state" | PARTIAL [INFERENCE] | ¶5 "compatibility issues after an upgrade" supports it; not stated |
| teaches 4 "a regular-file digest cannot see" | DISAGREE as a source benefit | 0 "digest" on the page; a lane design claim that this round changed (C2) |
| status mined; used-by (2 paths) | AGREE | both paths exist; knowledge l.330/335 and lesson l.27/42 cite S066 |
| Gate quote, location, ≤25 words | AGREE | verbatim after whitespace normalisation; 12 words; ¶3; also in upstream troff |
| Gate coverage of teaches | PARTIAL | one quote; teaches 2–4 unquoted |

## Drift from the seat's draft
The seat's draft (build/advice/SrcLdconfig.md:36; `draft-vs-registry.out`) had page-grounded teaches: the chain, "compatibility issues after an upgrade", and "page never names DT_SONAME". The registry row replaced that with teaches 4, dropped the compatibility sentence, dropped "which link it calls the SONAME", and dropped the `(unreleased)` caveat and both sha256 pins. The status and used-by flips are consistent with the knowledge cite.

## Recommendations (L1 decides; nothing edited)
1. teaches → "Documents the soname as the middle file of a three-link chain (libfoo.so -> libfoo.so.1 -> libfoo.so.1.12) and warns that a changed layout may cause compatibility issues after an upgrade; does not name DT_SONAME." The digest argument already sits in knowledge/llamacpp-loading-lifecycle.md:335–338. A post-commit change needs a `supersedes S066 —` row (rule 2); amending in-round is the L1's call.
2. anchor → "§DESCRIPTION ¶1, ¶3 (SONAME sentence), ¶4 (example), ¶5 (upgrade warning); man-pages 6.19 (tarball `.TH` says unreleased)".
3. Gate → add verified quotes: ¶1 "ldconfig creates the necessary links and cache to the most recent shared libraries" (13 w); ¶5 "Failure to follow this pattern may result in compatibility issues after an upgrade." (13 w).
4. scope → drop the "linker name → SONAME → real name" labels, or cite S074 for them (S074 is queued, tier B).
5. knowledge l.330 cites S066 by id and anchor but not the URL that CORPUS.md:163–166 asks for.
Outside S066: S067 and S071 newly carry W04 warnings (URLs shared with S057 and S033); warnings only.

## Hygiene
- Tools: none installed or upgraded (curl, python3, gcc, readelf, ldd, pacman -Q, diff, tar, zcat were already present).
- Lane: scratch clone at a6617149 (clone reads only). One read-only `git status` ran in the lane earlier and may refresh the index stat cache. No lane file edited; created only falsify/advice and falsify/out/ReopenS066.
- Outputs: falsify/out/ReopenS066/ (check-s066.py/.out, draft-vs-registry.py/.out, ldconfig-n-experiment.sh/.out, validate and census outputs, five fixtures). Scratch /tmp/kama-r21-ReopenS066 removed after this report.

## Limits
- glibc source and the PGP signature were not checked. The man7 wrap joins one sentence across a newline (whitespace-normalised match).
- The experiment covers one glibc (2.44), one synthetic library and one libz copy.
