# AttackSource — S033 critic (round 13)

I opened the sources myself and did not edit them. I opened `https://git-scm.com/docs/git-cat-file` (latest) and `https://git-scm.com/docs/git-cat-file/2.55.0` on 2026-10-20. I also read `corpus/SOURCES.md:45,61,74`, `corpus/lessons/round-13.md:36-51`, `.ufo/waves/round-12/fidelity.py` and `corpus/lessons/round-12-verifier-spotcheck.md:147-149`. I ran no gate, test, census, validator or fidelity run. The read-only commands were `git --version`, `git diff --numstat`, `cmp`, `git grep` and `ls`. Tools installed or updated: none.

## Verdict

S033 mostly does what it should: it cites the manual for the method only, not for any result. No finding blocks it. I reported F1–F3 to `KamaR13.Sources`, which revised the row; I re-read the revised state (`SOURCES.md:45,61,74`). F2 and F3 are closed. F1 is mostly closed. F4 is still open: it is in the L1-owned lesson, and `KamaR13.MistakeScribe` agreed but cannot edit that file.

## Evidence

| Check | Observed |
|---|---|
| Row state | `SOURCES.md:45` S033 added; `git diff --numstat` = `4 0`, so additions only. The row sits at line 45, the old blank line after S032. Later lines shift by 1. `git grep 'SOURCES\.md:(4[5-9]\|[5-7][0-9])' HEAD -- corpus SKILL.md PROVINCE.md` returned 0 hits, so no line citations break. |
| OUTPUT quote | Live page §OUTPUT reads: “If *<type>* is specified, the raw (though uncompressed) contents of the *<object>* will be returned.” (rendered line 500 of the latest page). That is 15 words, and it matches `SOURCES.md:74` and `round-13.md:38-39` word for word. |
| `--textconv` / `--filters` quotes | The page says “Show the content as transformed by a textconv filter” and “…as converted by the filters configured in the current working tree”. Both match `SOURCES.md:74`. |
| Version | Page header: “git-cat-file last updated in 2.56.0”, with 2.56.0 dated *2026-09-28*. The row matches. The host binary is `git version 2.55.0`, and round-12 `ReviewSelftest.md:9` also records 2.55.0. The 2.55.0 page has the same OUTPUT sentence (rendered line 493). |
| Method vs result | I searched the page for `independent\|compar\|verif\|replace`. Outside navigation and mailmap text, the only hit is the batch note at :405-406, which says `--batch-all-objects` output ignores replace refs. The page says nothing about comparison, independence or verification. |
| Result limits present | Revised row: “The page documents command mechanics only; it is not evidence that any comparison ran and not endpoint truth.” Search log `:61`: “does not establish that any kama run performed the comparison”. `:74`: “supports only direct object-content comparison mechanics”. Lesson `:39-40`: “method support only”. **PASS**: the documentation is not credited with any result. |
| Self-endorsement | The row cites no round-12 receipt, spotcheck “agree”, or 1→0/2→0 count. `used-by` = `corpus/lessons/round-13.md`, which exists and cites S033 at `:36`. **PASS**. |

## Findings

**F1 (low–medium): the OPTIONS `<type>` anchor does not support the claim attached to it.**
- The anchor cites “OPTIONS `<type>`” and the scope says “explicit-type raw output”.
- The page's `<type>` text is a permission, not a type check: “asking for a type that can trivially be dereferenced from the given *<object>* is also permitted… ask for a ‘blob’ with *<object>* being a tag object that points at it.”
- So `git cat-file blob X` does not show that X is a blob. Counterexample: a tag pointing at the blob passes as `blob`.
- In kama the identity of the bytes comes from code, not from the doc: `source_oid == SOURCE_BLOB_OID` plus the sha256 and byte-count pins (`fidelity.py:283-285`, constants `:47-49`).
- **Smallest fix:** append one clause stating that OPTIONS `<type>` allows trivial dereference, and that byte identity rests on the code-pinned OID, sha256 and length, not on the type word. Alternatively, drop OPTIONS `<type>` from the anchor while the row is still uncommitted.
- **Status after the re-read: mostly closed.** `:74` now says OPTIONS `<type>` “is not raw-output support”, and the anchor names OUTPUT as the authority. Residual: no text says that the type word `blob` does not prove the object is a blob, or that identity comes from the code pins. This is low severity, and the fidelity code already guards it.

**F2 (low): an inference is written as if the page said it.**
- “deliberately transform them, so exact byte comparison must avoid both” is a normative conclusion. The page only says “as transformed” and “as converted”; “deliberately” and “must avoid” are not on the page.
- The page also never says in plain words that `<type>` mode skips textconv or filters. That follows from “raw” plus the separate SYNOPSIS forms [INFERENCE].
- **Smallest fix:** mark it as inference in the appended prose, or change “deliberately transform” to “transform”.
- **Status after the re-read: closed.** “deliberately” is gone. The teaches cell now says “`--textconv` and `--filters` transform content, so byte comparison must avoid both”. That is a mild normative inference that no longer misstates the page.

**F3 (low): the version pin does not match the git binary, and the URL is not versioned.**
- The URL `/docs/git-cat-file` follows the latest release. 2.56.0 is the version of the manual, but the receipts and comparisons were produced by git 2.55.0.
- No semantic drift: I observed the same OUTPUT sentence in the 2.55.0 manual.
- **Smallest fix:** in the lesson Gate or search log, cite `https://git-scm.com/docs/git-cat-file/2.56.0`. Add: “identical OUTPUT sentence in 2.55.0, the host binary”.
- **Status after the re-read: closed in substance.** The anchor says “same sentence in 2.55.0”, and `:74` records the host `git --version` 2.55.0 as “a version fact, not a comparison result”. The row URL is still unversioned. That is optional, because the `on-release` recheck covers drift.

**F4 (low): the lesson's unqualified “independent” promotes a method into a guarantee.**
- `round-13.md:51` says “the independent comparison uses `git cat-file blob`”.
- `git show` and `cat-file` resolve `<rev>:<path>` against the same object database. A replace ref would redirect both by default. It is neutralised only by `--no-replace-objects` (`fidelity.py:95`), which is documented in git(1), not in S033.
- In spotcheck D1 (`:147`), “independent” means independent of the snapshot manifest.
- **Smallest fix:** write “manifest-independent comparison”. **Status: open.** It is now at `round-13.md:54` (the line shifted). `KamaR13.MistakeScribe` agrees: the code constants are at `fidelity.py:45-49`, `--no-replace-objects` is at `:95`, and `GIT_NO_REPLACE_OBJECTS` is set at `:84`. MistakeScribe's write set excludes the lesson, so **the L1 lesson owner must apply the fix**. The rest of the lesson is already correct: `:39-46` says the quote is not evidence “that its source is independent of the repository being checked”, and that the two commands “share the same object store, not independent external authority”. So only the Mistakes row at `:54` is still unqualified.

**Nit:** the quote's markup differs between places. The anchor uses backticks (`` `<type>` ``), `:74` uses plain `<type>`, and the page renders it in italics. The words are identical, so this does not affect fidelity.

## Axes affected
- **calibration:** F1, F2 and F4 are precision debt and do not move the score. The row correctly claims no result (score stays 7 → 7).
- **quality:** none. S033 is a method source. Under spotcheck `:149`, quality credit belongs to round-12 D4, not to S033 or the gate machinery.
- **operability, freshness, coverage, expansion:** unchanged. The row makes no runtime or endpoint claim.

## Routed
- `KamaR13.Sources`: F1, F3 (and F2) for the row, search log and appended prose.
- `KamaR13.Criterion`: if KQ16 cites S033, cite it for the comparison read method only, not for independence.
- `KamaR13.MistakeScribe`: F4.

## Limits
- The page was read through a markdown reader, so line numbers refer to rendered output (`artifact://4375`, `artifact://4446`), not to the HTML source.
- I did not check that git's actual behaviour matches the manual.
- I did not check `fidelity.py` behaviour beyond reading it statically.
- L1 should run, once after integration: `grep -c '^| S033 ' corpus/SOURCES.md` (expect 1), and `git diff --numstat -- corpus/SOURCES.md`, expecting 0 deletions.
