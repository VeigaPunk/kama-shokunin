VERDICT: confirm - man7 ld.so(8) (man-pages 6.19) DESCRIPTION item (3) supports "only direct dependencies are searched via RUNPATH" in substance, scoped to the carrying object's DT_NEEDED entries. The paraphrase is not verbatim and must not be quoted. Gate quote G (23 words, below) reproduces in the man7 page and in both cross-check renders.

# S057 item (3): DT_RUNPATH search scope (LdsoSearchOrder)

## Exact sentence and section
- Section: DESCRIPTION (`<h2 id="DESCRIPTION">`, fetched line 80). Search-order list item (3) sits at lines 113-119. It follows the verbatim lead-in "If a shared object dependency does not contain a slash, then it is searched for in the following order:". No subsection heading sits between DESCRIPTION and item (3).
- Exact sentence (verbatim): "Such directories are searched only to find those objects required by DT_NEEDED (direct dependencies) entries and do not apply to those objects' children, which must themselves have their own DT_RUNPATH entries."
- Antecedent, item (3) sentence 1 (verbatim): "Using the directories specified in the DT_RUNPATH dynamic section attribute of the binary if present."

## Support for the claim
- Supported in substance. The page says RUNPATH directories are searched "only to find those objects required by DT_NEEDED (direct dependencies) entries" and "do not apply to those objects' children". The page's own word "children" means the dependency tree below the carrying object (verbatim item (3) sentence 3: "This is unlike DT_RPATH, which is applied to searches for all children in the dependency tree.").
- Scope is required. "Direct" means direct DT_NEEDED entries of the object that carries the RUNPATH. Each child must carry its own RUNPATH.
- Using this to ground an install-tree identity claim is [INFERENCE] beyond the page text. glibc loader code was not examined here.

## S057 Gate quote (23 words; verbatim fragment, sentence continues)
> Such directories are searched only to find those objects required by DT_NEEDED (direct dependencies) entries and do not apply to those objects' children

Locator: DESCRIPTION, search-order item (3) (DT_RUNPATH), after "Using the directories specified in the DT_RUNPATH dynamic section attribute of the binary if present."

## Rejected (not reproduced or over limit; 0 hits in man7 6.19, local 6.19-1 and upstream master)
- "only direct dependencies are searched via RUNPATH": paraphrase, not verbatim.
- Same clause with "(direct dependencies)" dropped: 0 hits.
- Same clause with "object's" typo: 0 hits.
- Same clause with curly apostrophe: 0 hits. The page uses straight '.
- Item (3) with DT_RPATH in place of DT_RUNPATH: 0 hits. Item (1) reads "DT_RPATH ... present and DT_RUNPATH attribute does not exist."
- Whole item (3), 62 words: verbatim, but over the 25-word limit.

## Lane-text and sibling notes (read-only; nothing edited)
- corpus/SOURCES.md:69 gives "are searched only to find those objects required by DT_NEEDED" as "(11 words)". It is 10 words (`reproduce.sh` word-count step prints `10 23`). The clause is verbatim, as a prefix of G.
- The same list fixes the order: (2) LD_LIBRARY_PATH (line 109) precedes (3) DT_RUNPATH (line 113). This settles the claim tagged [INFERENCE] at .ufo/waves/round-16/build/advice/SentinelLiveSafety.md:41.
- Upstream master troff is not the cited revision. It renders the list as bullets, and it differs elsewhere (e.g. "-z nodeflib" vs 6.19 "-z nodefaultlib"). Cite the 6.19 man7 page.

## Receipts (/tmp/kama-r19-LdsoSearchOrder/out)
- `bash out/reproduce.sh out > out/receipt.log`: exit 0. Re-run in a visible shell also exit 0. The man7 sha256 matched the pinned value on both runs.
- `python3 out/verify_s057.py out`: exit 0, `all_expectations_met=True gate_pass=True`.
- Per-step exits: cp -a 0; curl man7 0 (41398 B); curl upstream `main` path 22 (404) and git.kernel.org path 22 (404); `git ls-remote --symref` 0 (HEAD = master); curl upstream `master` path 0; zcat 0; `man -P cat -l` 0 (both renders); `pacman -Q man-pages` 0 (6.19-1).
- Files: `S057-gate-draft.md`, `quote-check.json`, `verify_s057.py`, `reproduce.sh`, `receipt.log`, `sha256sums.txt`, `item3-normalized.txt`, plus the raw HTML, troff and render files.

## Install record
None. No tools installed or updated. Used curl, git, man-db, zcat, python3 3.14.8, and `pacman -Q` (query only).
