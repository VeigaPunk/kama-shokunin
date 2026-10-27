# W01LessonGateDraft — draft `## Gate` for corpus/lessons/round-58.md

Output file only; no production file edited, no commit, no judge seat. Scratch `S=/fast/scratch/hyaku/kama-r58/W01LessonGateDraft` (receipts copied to `W01LessonGateDraft/checks.txt`, scratch removed).

## Draft — `## Gate`

- **S517 — ADMIT, tier A, mined.** Python documentation, `sys.setprofile`, https://docs.python.org/3/library/sys.html#sys.setprofile, accessed live 2026-10-27 (live title “Python 3.15.2 documentation”; footer “Last updated on Oct 27, 2026 (16:42 UTC)”). Located quote at §sys.setprofile, event `'call'`: “A function is called (or some other code block entered). The profile function is called; arg is None.” (18 words). Scope: the hook fires on `'call'`/`'return'` and on C-level `'c_call'`/`'c_return'`/`'c_exception'`, not per executed line, and reports a return even when an exception is set; it is thread-specific (“The function is thread-specific, but there is no way for the profiler to know about context switches between threads”, 19 words) and self-uninstalls on error (“Error in the profile function will cause itself unset.”, 9 words). A profile receipt therefore proves a frame was entered or returned, never what the frame did: C1 must pair each watched call event with the battery's own stubbed side-effect records, and an empty receipt is ambiguous between “no call” and “hook error”. The source grounds the mechanism only; C1's accept/reject predicate is judged by `tools/round58-c1-counter.py`. S517 is free at build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` (highest id S516; 0 rows S517/S518).

- **S513 — REJECT retained, rationale narrowed, tier A.** `ld.so(8)`, https://man7.org/linux/man-pages/man8/ld.so.8.html, re-opened live 2026-10-27 (fetch sha256 `d9b7737e…`, byte-identical to `.ufo/waves/round-56/sources/ld.so.8.html`; Linux man-pages 6.19, page dated 2026-08-03). Located quote at §ENVIRONMENT → LD_AUDIT: “A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace” (18 words); the same entry has “LD_AUDIT is ignored in secure-execution mode.” (6 words), `$ORIGIN`/`$LIB`/`$PLATFORM` expansion in the audit list, and “For details, see rtld-audit(7).” Disposition from this read: the round-56 reason — overlap with the dedicated rtld-audit(7) source “for the claim's only need” — is true only for the name-presence use and false as general overlap: the committed rtld-audit(7) snapshot has 0 occurrences of `secure-execution` and 0 of `$ORIGIN`. Retain the REJECT for the narrow use and score the flip as fired: the secure-execution rule needs its own narrow anchor (S518 is drafted this wave for that), not S513's broad scope. No existing row cell rewritten; S513 status stays `rejected`.

- **Spot-check set (non-author):** ADMIT S517 and REJECT S513 — one of each, both re-derived in this seat from live page text, not from a sibling report; all seven quotes verified verbatim after tag/whitespace normalization of the fetched HTML.

## Findings for L1 / canonical judge

1. **S517 version token.** Working-tree Gate `corpus/lessons/round-58.md:14` says “Python 3.14”; the live URL served “Python 3.15.2 documentation” on 2026-10-27. Working-tree `corpus/SOURCES.md:270` repeats “Python 3.14”. Attack: S517 registry anchor cell and Gate line 14.
2. **S513 disposition conflict (verbatim).** Working-tree Gate line 16 reads “**S518 — ADMIT, tier A, mined; supersedes S513 (a REJECT overturned).**” and line 20 reads “reject carried forward: none new this round, the overturned reject is S513 (the closure may re-open it).” My live read retains S513 rejected for the narrow name-presence use, flip fired but not claimed. Reported for the canonical judge, not reconciled.
3. **S517 scope truncation.** Gate line 14's “a profile hook sees frame entry, not line execution” omits the C-level events and the self-unset/thread-specific limits; an empty profile receipt is ambiguous. Attack: S517 `teaches` cell.

## Checks (exact command → output; exit)

- `curl -sSL -o $S/sys.html https://docs.python.org/3/library/sys.html` → 280,618 bytes, exit 0; `curl -sSL -o $S/ldso.html https://man7.org/linux/man-pages/man8/ld.so.8.html` → 41,398 bytes, exit 0.
- `python3` quote check over tag-stripped, whitespace-normalized HTML → 7/7 FOUND (S517 18w/18w/9w/19w; S513 18w/6w/4w), exit 0 (`W01LessonGateDraft/checks.txt`).
- `sha256sum .ufo/waves/round-56/sources/ld.so.8.html $S/ldso.html` → both `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`, exit 0.
- `grep -c secure-execution .ufo/waves/round-56/sources/rtld-audit.7.html` → 0, exit 1; `grep -c '\$ORIGIN' .ufo/waves/round-56/sources/rtld-audit.7.html` → 0, exit 1.
- `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 259; same over `git show e4891d8:corpus/SOURCES.md` → 257; `… | grep -cE '^\| S51[78] '` → 0, exit 1; highest id at build tip → S516.
- `awk -F'|' '/^\| S513 /{print $9}' corpus/SOURCES.md` → `rejected`, exit 0.
- `git status --porcelain` → ` M corpus/SOURCES.md`, `?? corpus/lessons/round-58.md` (tree moved during the seat; observed read-only).

## Limits

- Live pages read 2026-10-27 ~16:56; later edits are outside this seat's evidence.
- No independent closure available to this seat; lane authors are not independent. I did not run the frozen C1/C2 counters (outside a draft-only seat).
