# Sc1Exe — S499 source reopen

**Verdict: S499 quote is verbatim and correctly anchored to §DESCRIPTION; its stated man-pages version/date and text-copy colophon agree. S498 is defective by omitting two literal fence characters without marking the omission; proposed erratum below.**

Axes: source fidelity; citation/version reproducibility; operability of the executable-identity claim.

## Evidence

- Reopened live source `https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html` on 2026-10-27. Under DESCRIPTION, it says: “This symbolic link can be dereferenced normally; attempting to open it will open the executable.” This exactly matches S499's quoted sentence (SOURCES.md:252); quote remains verbatim, including punctuation, and its §DESCRIPTION anchor is correct.
- S499 scope's neighboring clauses are supported by the same DESCRIPTION: actual pathname (Linux 2.2+), `' (deleted)'` suffix after unlink, and the `PTRACE_MODE_READ_FSCREDS` dereference/read check. The source limits the claim to Linux 2.2 and later. S499 accurately captures these boundaries.
- Live page colophon identifies Linux man-pages 6.19, page date 2026-02-08, obtained from man-pages-6.19.tar.gz; rendering created 2026-09-09. The committed copy `.ufo/waves/round-51/c1/proc_pid_exe.5.txt`:113-123 records the same tarball, fetch date, version, and page date; copy DESCRIPTION lines 73-87 contains the same wording and permission qualification. No version/colophon discrepancy observed.
- Reopened S496 live page: `proc_pid_maps(5)`, man-pages 6.19, dated 2026-02-08. Its DESCRIPTION states dev is major:minor, inode is on that device, 0 means no inode associated, and pathname will usually be the file backing the mapping. S496's excerpt is verbatim and correctly grounded in those DESCRIPTION paragraphs. Important qualification in source: pathname “usually” names backing file; mappings can be anonymous, and deleted backing files are marked ` (deleted)`.
- Reopened S497 live page: `PR_SET_PDEATHSIG(2const)`, man-pages 6.19, dated 2026-02-08. S497's excerpt matches DESCRIPTION verbatim. Source also says no signal is sent if parent thread and all ancestor subreapers have already terminated by call time, setting is cleared for a fork child, and signal is process-directed; those caveats bound any operational interpretation.
- Reopened CommonMark URL. Page identifies **Version 0.31.2 (2024-01-28)**. Section 4.5 opening sentence is “A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).” S498 teaches only “A code fence is a sequence of at least three consecutive backtick characters or tildes.” This silently removes the inline literal characters `(``)` and `(~)` (specifically the parenthesized backtick and tilde glyphs) from the quoted sentence. The omission is material for exact quotation and must be marked rather than presented as continuous verbatim quote. Committed section text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`:5-7 contains both glyphs.

## Proposed appended erratum text

Append this to the round-50 closure/errata record (do not edit the SOURCES row outside status/recheck/used-by):

> **S498 quote correction (Round 51 source reopen, 2026-10-27).** The S498 `teaches` quotation elides the source's parenthesized literal fence characters without marking the omission. CommonMark 0.31.2 §4.5 reads: “A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).” Corrected short quotation: “A code fence is a sequence of at least three consecutive backtick characters … or tildes …” (elisions shown explicitly); alternatively quote the full source sentence. The surrounding claim about the scanner remains supported. Source: https://spec.commonmark.org/0.31.2/#fenced-code-blocks; version 0.31.2 dated 2024-01-28; committed text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`, lines 5–7.

## Commands / outputs / exits

- `read https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html` — live page returned; DESCRIPTION and COLOPHON read; success.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:249-252:raw` — S496–S499 rows read; success.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/c1/proc_pid_exe.5.txt` — committed S499 source copy read; success.
- `read https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html` — live DESCRIPTION and COLOPHON returned; success.
- `read https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html` — live DESCRIPTION and COLOPHON returned; success.
- `read https://spec.commonmark.org/0.31.2/#fenced-code-blocks` — live page version and §4.5 returned; success.
- `read /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/closure.md` attempt — path not found. Round-50 closure document location therefore remains unresolved; erratum is drafted here for appending by integration.

No tools installed. No runtime or campaign counter run.
